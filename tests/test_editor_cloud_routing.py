from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from forgelab.artifacts import ArtifactStore
from forgelab.editor_adapter import (
    AiderCliAdapter, EDITOR_MODELS, EditorAdapterError,
    EditorModelConfig, EditorRequest, EditorResult,
)
from forgelab.orchestrator import AIEditorExecutionError, _run_aider_editor


def result(output='', exit_status=0):
    return EditorResult('aider-cli', {'app.py': 'VALUE = 2\n'}, ('app.py',),
                        output, '', exit_status, False, 1, ('aider',), provider_errors=output)


class CloudRoutingTests(unittest.TestCase):
    def test_no_local_developer_call_is_reachable_in_aider_mode(self):
        import ast
        import forgelab.orchestrator as orchestrator
        tree = ast.parse(Path(orchestrator.__file__).read_text(encoding='utf-8'))
        calls = []
        def visit(node, custom_only=False):
            if isinstance(node, ast.If) and ast.unparse(node.test) == "request.editor_engine == 'aider'":
                for child in node.body: visit(child, custom_only)
                for child in node.orelse: visit(child, True)
                return
            if isinstance(node, ast.Call) and ast.unparse(node.func) == 'ai_router.execute' and len(node.args) > 3:
                if ast.unparse(node.args[3]) == 'Role.DEVELOPER.value':
                    calls.append(node.lineno)
                    self.assertTrue(custom_only, f'Local developer call reachable in Aider mode at line {node.lineno}')
            for child in ast.iter_child_nodes(node): visit(child, custom_only)
        visit(tree)
        self.assertTrue(calls)

    def request(self):
        return EditorRequest(Path('.'), 'synthetic', ('app.py',))

    def test_primary_and_no_speculative_alternative(self):
        with patch.object(AiderCliAdapter, '_run_once', return_value=result()) as run:
            output = AiderCliAdapter().run(self.request())
        self.assertEqual(run.call_count, 1)
        self.assertEqual(run.call_args.args[0].model, EDITOR_MODELS.primary)
        self.assertEqual(output.model, EDITOR_MODELS.primary)
        self.assertEqual(output.routing_status, 'EDITOR_COMPLETED')

    def test_unavailable_primary_switches_once_on_same_original_request(self):
        for message in ('HTTP 404', 'HTTP 410', 'model gpt-oss:120b-cloud not found', 'model retired'):
            with self.subTest(message=message), patch.object(
                AiderCliAdapter, '_run_once', side_effect=[result(message), result()]
            ) as run:
                output = AiderCliAdapter().run(self.request())
                requests = [call.args[0] for call in run.call_args_list]
                self.assertEqual([r.model for r in requests], [EDITOR_MODELS.primary, EDITOR_MODELS.alternative])
                self.assertEqual(requests[0].repository, requests[1].repository)
                self.assertEqual(requests[0].objective, requests[1].objective)
                self.assertLessEqual(requests[1].timeout_seconds, requests[0].timeout_seconds)
                self.assertEqual(output.model, EDITOR_MODELS.alternative)
                self.assertEqual(output.routing_attempts[1]['reason'], 'PRIMARY_UNAVAILABLE')

    def test_quota_always_stops_even_exit_zero_or_unavailable_also_present(self):
        for message in ('HTTP 402', 'HTTP 429', 'quota exceeded', 'insufficient credits',
                        'billing error', 'HTTP 404; quota exhausted', 'RateLimitError'):
            with self.subTest(message=message), patch.object(AiderCliAdapter, '_run_once', return_value=result(message)) as run:
                output = AiderCliAdapter().run(self.request())
                self.assertEqual(output.routing_status, 'EDITOR_CLOUD_QUOTA_STOP')
                self.assertEqual(run.call_count, 1)

    def test_both_unavailable_never_reach_local(self):
        with patch.object(AiderCliAdapter, '_run_once', side_effect=[result('HTTP 410'), result('HTTP 404')]) as run:
            output = AiderCliAdapter().run(self.request())
        self.assertEqual(run.call_count, 2)
        self.assertEqual(output.routing_status, 'EDITOR_MODEL_UNAVAILABLE')
        self.assertEqual([a['model'] for a in output.routing_attempts], [EDITOR_MODELS.primary, EDITOR_MODELS.alternative])

    def test_alternative_quota_stops_chain(self):
        with patch.object(AiderCliAdapter, '_run_once', side_effect=[result('HTTP 410'), result('credits exhausted')]) as run:
            output = AiderCliAdapter().run(self.request())
        self.assertEqual(run.call_count, 2)
        self.assertEqual(output.routing_status, 'EDITOR_CLOUD_QUOTA_STOP')

    def test_non_availability_errors_do_not_switch(self):
        for message in ('HTTP 500', 'HTTP 401', 'app.py not found', 'FileNotFoundError: app.py', 'syntax error'):
            with self.subTest(message=message), patch.object(AiderCliAdapter, '_run_once', return_value=result(message, 1)) as run:
                output = AiderCliAdapter().run(self.request())
                self.assertEqual(output.routing_status, 'EDITOR_EXECUTION_FAILED')
                self.assertEqual(run.call_count, 1)

    def test_configuration_and_request_reject_local_other_provider_and_unknown_models(self):
        for model in ('qwen2.5-coder:7b', 'ollama_chat/qwen2.5-coder:7b', 'gpt-oss:120b', '', 'openai/gpt-4'):
            with self.subTest(model=model):
                with self.assertRaises(EditorAdapterError):
                    EditorModelConfig(primary=model)
                with patch.object(AiderCliAdapter, '_run_once') as run:
                    with self.assertRaises(EditorAdapterError):
                        AiderCliAdapter().run(EditorRequest(Path('.'), 'synthetic', ('app.py',), model=model))
                    run.assert_not_called()
        with self.assertRaises(EditorAdapterError):
            EditorModelConfig(alternative=EDITOR_MODELS.primary)
        with self.assertRaises(EditorAdapterError):
            EditorModelConfig(primary=EDITOR_MODELS.alternative, alternative=EDITOR_MODELS.primary)

    def test_total_deadline_does_not_reset_for_alternative(self):
        with patch.object(AiderCliAdapter, '_run_once', return_value=result('HTTP 410')) as run, patch(
            'forgelab.editor_adapter.time.monotonic', side_effect=[0, 300, 300]
        ):
            output = AiderCliAdapter().run(self.request())
        self.assertEqual(run.call_count, 1)
        self.assertEqual(output.routing_status, 'EDITOR_MODEL_UNAVAILABLE')

    def test_every_orchestrator_phase_records_model_and_explicit_stop(self):
        for phase in ('implementation', 'initial_prewrite_correction', 'test_failure_repair',
                      'semantic_review_repair', 'regression_test_correction', 'semantic_test_correction', 'semantic_review_correction'):
            for message, reason in [('HTTP 429', 'EDITOR_CLOUD_QUOTA_STOP'), ('HTTP 410', 'EDITOR_MODEL_UNAVAILABLE')]:
                with self.subTest(phase=phase, reason=reason), tempfile.TemporaryDirectory() as directory:
                    store = ArtifactStore(Path(directory))
                    with patch.object(AiderCliAdapter, '_run_once', return_value=result(message)):
                        with self.assertRaises(AIEditorExecutionError) as raised:
                            _run_aider_editor(repository=Path(directory), objective='synthetic',
                                              allowed_paths=('app.py',), timeout_seconds=300, phase=phase, store=store)
                    self.assertEqual(raised.exception.reason, reason)
                    evidence = json.loads((store.root/'EditorRouting.json').read_text())['calls'][0]
                    self.assertEqual(evidence['phase'], phase)
                    self.assertEqual(evidence['status'], reason)
                    self.assertTrue(evidence['attempts'])

    def test_full_orchestrator_closes_on_quota_without_review_or_write(self):
        from test_orchestrator import make_demo, request, ai_plan
        from forgelab.model_router import ProviderResponse
        from forgelab.orchestrator import run_multi_agent
        from decimal import Decimal
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); repo = make_demo(root)
            original = (repo/'calculator.py').read_bytes()
            with patch('forgelab.orchestrator.OllamaProvider.invoke', return_value=ProviderResponse(ai_plan(), 1, 1, Decimal('0'))) as invoke, patch.object(
                AiderCliAdapter, '_run_once', return_value=result('HTTP 429', 0)
            ):
                run = run_multi_agent(request(repo, operation='ai_generate', editor_engine='aider'), root/'runs')
            failure = json.loads((run/'EditorFailure.json').read_text())
            self.assertEqual(failure['reason'], 'EDITOR_CLOUD_QUOTA_STOP')
            self.assertEqual(json.loads((run/'RunSummary.json').read_text())['status'], 'CLOSED')
            self.assertEqual(invoke.call_count, 1)
            self.assertEqual((repo/'calculator.py').read_bytes(), original)

    def test_secondary_corrections_use_aider_not_local_developer(self):
        from test_orchestrator import make_demo, request, ai_plan, semantic_review_pass, semantic_review_fail
        from forgelab.model_router import ProviderResponse
        from forgelab.orchestrator import run_multi_agent
        from decimal import Decimal
        from dataclasses import replace
        good = 'def add(a, b):\n    return a + b\n'
        bad = 'def add(a, b):\n    return a - b\n'
        tests = 'import unittest\nfrom calculator import add\nclass T(unittest.TestCase):\n    def test_add(self): self.assertEqual(add(2, 3), 5)\n'
        for mode in ('semantic', 'regression', 'rereview'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); repo = make_demo(root)
                if mode == 'semantic':
                    outputs = [({'calculator.py': good}, ('calculator.py',)),
                               ({'calculator.py': good, 'test_calculator.py': tests.replace('5)', '6)')}, ('test_calculator.py',)),
                               ({'calculator.py': good, 'test_calculator.py': tests}, ('test_calculator.py',))]
                    replies = [ai_plan(), semantic_review_fail('More coverage', 'Required coverage absent'), semantic_review_pass()]
                    expected = 'semantic_test_correction'
                elif mode == 'regression':
                    # First candidate preserves one passing case and adds a failing one;
                    # the repair regresses the previously passing case and must be rolled back.
                    initial_tests = tests + '    def test_new(self): self.assertEqual(add(3, 4), 8)\n'
                    outputs = [({'calculator.py': good, 'test_calculator.py': initial_tests}, ('calculator.py', 'test_calculator.py')),
                               ({'calculator.py': 'def add(a, b):\n    return a + b + 1\n', 'test_calculator.py': initial_tests}, ('calculator.py',)),
                               ({'calculator.py': good, 'test_calculator.py': initial_tests.replace('8)', '7)')}, ('test_calculator.py',))]
                    replies = [ai_plan(), 'Correct the new assertion while preserving addition.', semantic_review_pass()]
                    expected = 'regression_test_correction'
                else:
                    outputs = [({'calculator.py': good}, ('calculator.py',)),
                               ({'calculator.py': good + '# intermediate candidate\n'}, ('calculator.py',)),
                               ({'calculator.py': good + '# corrected candidate\n'}, ('calculator.py',))]
                    replies = [ai_plan(), semantic_review_fail('Coverage', 'Missing coverage'),
                               semantic_review_fail('Coverage', 'Still missing coverage'), semantic_review_pass()]
                    expected = 'semantic_review_correction'
                candidates = [replace(result(), files=files, changed_paths=paths) for files, paths in outputs]
                with patch('forgelab.orchestrator.OllamaProvider.invoke', side_effect=[ProviderResponse(text, 1, 1, Decimal('0')) for text in replies]) as invoke, patch.object(
                    AiderCliAdapter, '_run_once', side_effect=candidates
                ) as editor:
                    run = run_multi_agent(request(repo, operation='ai_generate', editor_engine='aider',
                                                  allowed_paths=('calculator.py', 'test_calculator.py'), max_repair_attempts=1), root/'runs')
                routing = json.loads((run/'EditorRouting.json').read_text())['calls']
                self.assertEqual(routing[-1]['phase'], expected)
                self.assertEqual(editor.call_count, 3)
                self.assertEqual(invoke.call_count, len(replies))
                self.assertTrue(all(call['model'] == EDITOR_MODELS.primary for call in routing))
                self.assertEqual(json.loads((run/'RunSummary.json').read_text())['status'], 'READY_FOR_DECISION')


if __name__ == '__main__':
    unittest.main()
