import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from forgelab.editor_adapter import (
    AiderCliAdapter, AiderCliConfig, EditorAdapterError, EditorRequest, EditorResult,
    _provider_errors,
)
from forgelab.editor_error_capture import _observe


CODE_LINES = (
    '+    "credit_note": total * 0.1,',
    '+    billing_address = data.get("billing")',
    '+QUOTA_MASSIMALE = 1500  # quota assicurativa',
    '+def apply_rate_limit(x):',
    '+    return {"error": "Not found", "status": 404}',
    '+    raise ValueError("treatment model not found")',
    '+credito = quota * 0.1',
)


class EditorErrorCaptureTests(unittest.TestCase):
    def test_successful_code_and_forged_provider_output_never_route(self):
        captured = (Path(__file__).parent / 'fixtures/aider_retired_stdout.txt').read_text(encoding='utf-8')
        for text in (*CODE_LINES, captured, 'litellm.RateLimitError: billing quota HTTP 429'):
            for exit_code in (0, 1):
                with self.subTest(text=text, exit_code=exit_code):
                    result = EditorResult('aider-cli', {'app.py': text}, ('app.py',),
                                          text, text, exit_code, False, 1, ())
                    with patch.object(AiderCliAdapter, '_run_once', return_value=result) as run:
                        output = AiderCliAdapter().run(EditorRequest(Path('.'), 'test', ('app.py',)))
                    self.assertEqual(output.routing_status, 'EDITOR_COMPLETED' if exit_code == 0 else 'EDITOR_EXECUTION_FAILED')
                    self.assertEqual(run.call_count, 1)

    def test_actual_subprocess_success_preserves_code_output(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            (repo / 'app.py').write_text('old', encoding='utf-8')
            content = '\n'.join(CODE_LINES)
            script = f"from pathlib import Path; import sys; print({content!r}); print({content!r}, file=sys.stderr); Path('app.py').write_text({content!r}, encoding='utf-8')"
            adapter = AiderCliAdapter(AiderCliConfig(executable=(sys.executable, '-c', script)))
            output = adapter.run(EditorRequest(repo, 'test', ('app.py',)))
            self.assertEqual(output.routing_status, 'EDITOR_COMPLETED')
            self.assertEqual(output.files['app.py'], content)
            self.assertEqual(output.provider_errors, '')

    def test_provider_exception_capture_and_exit_zero_routing(self):
        captured = (Path(__file__).parent / 'fixtures/aider_retired_stdout.txt').read_text(encoding='utf-8')
        cases = [(captured, 410, 'EDITOR_MODEL_UNAVAILABLE'),
                 ('Insufficient credits with the API provider. Please add credits.', 402, 'EDITOR_CLOUD_QUOTA_STOP'),
                 ('The API provider has rate limited you. Try again later or check your quotas.', 429, 'EDITOR_CLOUD_QUOTA_STOP'),
                 ('Payment required', 402, 'EDITOR_CLOUD_QUOTA_STOP'),
                 ('Too many requests', 429, 'EDITOR_CLOUD_QUOTA_STOP')]
        for message, status, expected in cases:
            with self.subTest(status=status), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / 'errors.jsonl'
                path.write_text('{"event":"observer_ready"}\n', encoding='utf-8')
                error_class = type('APIConnectionError', (Exception,), {'__module__': 'litellm.exceptions'})
                error = error_class(message)
                error.status_code = status
                def send():
                    raise error
                with patch.dict(os.environ, FORGELAB_EDITOR_ERRORS=str(path)):
                    with self.assertRaises(error_class) as raised:
                        _observe(send)()
                self.assertIs(raised.exception, error)
                result = EditorResult('aider-cli', {}, (), '', '', 0, False, 1, (), provider_errors=_provider_errors(path))
                with patch.object(AiderCliAdapter, '_run_once', return_value=result) as run:
                    output = AiderCliAdapter().run(EditorRequest(Path('.'), 'test', ('app.py',)))
                self.assertEqual(output.routing_status, expected)
                self.assertEqual(run.call_count, 2 if status == 410 else 1)

    def test_missing_or_corrupt_observer_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'errors.jsonl'
            with self.assertRaises(EditorAdapterError):
                _provider_errors(path)
            for content in ('', 'invalid', '{}', '{"event":"provider_error"}'):
                path.write_text(content, encoding='utf-8')
                with self.assertRaises(EditorAdapterError):
                    _provider_errors(path)

    def test_child_import_hook_preserves_original_http_status(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / 'repo'
            repo.mkdir()
            (repo / 'app.py').write_text('unchanged', encoding='utf-8')
            package = root / 'aider'
            package.mkdir()
            (package / '__init__.py').write_text('', encoding='utf-8')
            (package / 'models.py').write_text(
                "class Original(Exception):\n    status_code = 402\n"
                "class APIConnectionError(Exception):\n    __module__ = 'litellm.exceptions'\n    status_code = 500\n"
                "class Model:\n    def send_completion(self):\n"
                "        try:\n            raise Original('opaque provider rejection')\n"
                "        except Original as cause:\n            raise APIConnectionError('opaque mapped rejection') from cause\n",
                encoding='utf-8',
            )
            script = (
                f"import sys; sys.path.insert(0, {str(root)!r})\n"
                "from aider.models import Model\n"
                "try:\n    Model().send_completion()\nexcept Exception:\n    pass\n"
            )
            adapter = AiderCliAdapter(AiderCliConfig(executable=(sys.executable, '-c', script)))
            output = adapter.run(EditorRequest(repo, 'test', ('app.py',)))
            self.assertEqual(output.exit_status, 0)
            self.assertEqual(output.routing_status, 'EDITOR_CLOUD_QUOTA_STOP')
            self.assertIn('HTTP 402', output.provider_errors)
            self.assertEqual(len(output.routing_attempts), 1)

    def test_success_and_local_errors_do_not_create_provider_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'errors.jsonl'
            with patch.dict(os.environ, FORGELAB_EDITOR_ERRORS=str(path)):
                content = '\n'.join(CODE_LINES)
                self.assertEqual(_observe(lambda: content)(), content)
                def invalid():
                    raise ValueError('treatment model not found; billing quota')
                with self.assertRaises(ValueError):
                    _observe(invalid)()
            self.assertFalse(path.exists())
