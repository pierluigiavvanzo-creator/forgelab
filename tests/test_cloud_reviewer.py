import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from forgelab.model_router import (
    ModelRouter, ProviderPermanentError, ProviderResponse, ProviderTransientError,
    CloudRoleModelConfig, CloudRoleRoutingError, RouterError, TaskClass, UsageLedger, load_routes,
)
from forgelab.orchestrator import run_multi_agent
from test_orchestrator import ai_plan, make_demo, request, semantic_review_pass


def response(text='review'):
    return ProviderResponse(text, 11, 7, actual_cost=Decimal('0'))


class FakeProvider:
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.calls = []

    def invoke(self, *args):
        self.calls.append(args)
        outcome = next(self.outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class CloudReviewerTests(unittest.TestCase):
    def router(self, outcomes):
        provider = FakeProvider(outcomes)
        router = ModelRouter(load_routes(Path('.forgelab/routing.yaml')),
                             {'ollama': provider}, UsageLedger(Decimal('0')))
        return router, provider

    def test_primary_cloud_records_tokens_route_and_preserves_contract(self):
        router, provider = self.router([response()])
        schema = {'type': 'object'}
        router.execute_reviewer('prompt', 'review-0', 60, schema)
        self.assertEqual(provider.calls, [('gemma4:31b-cloud', 'prompt', 60, schema)])
        record = router.ledger.records[0]
        self.assertEqual((record.policy_route, record.model_id, record.input_tokens),
                         ('REVIEWER', 'gemma4:31b-cloud', 11))
        self.assertIn('independent model family', record.routing_reason)

    def test_generic_s1_entry_cannot_route_reviewer_locally(self):
        router, provider = self.router([response()])
        router.execute(TaskClass.S1, 'prompt', 'review-0', 'REVIEWER', 'legacy caller')
        self.assertEqual(provider.calls[0][0], 'gemma4:31b-cloud')
        self.assertEqual(router.ledger.records[0].policy_route, 'REVIEWER')

    def test_s0_still_forbids_inference_even_for_reviewer(self):
        router, provider = self.router([])
        with self.assertRaisesRegex(RouterError, 'S0 deterministic'):
            router.execute(TaskClass.S0, 'prompt', 'r', 'REVIEWER', 'test')
        self.assertEqual(provider.calls, [])

    def test_planner_stays_local_and_support_uses_cloud(self):
        router, provider = self.router([response(), response()])
        for task, role in ((TaskClass.S1, 'PROJECT_MANAGER'), (TaskClass.S2, 'SUPPORT')):
            router.execute(task, 'prompt', role, role, 'test')
        self.assertEqual([c[0] for c in provider.calls], ['qwen2.5-coder:7b', 'gemma4:31b-cloud'])
        self.assertEqual([r.policy_route for r in router.ledger.records], ['S1', 'SUPPORT'])

    def test_unavailable_switches_once_with_reduced_independence(self):
        for message in ('Ollama HTTP 404: missing', 'Ollama HTTP 410: retired',
                        'model retired', 'model not found'):
            with self.subTest(message=message):
                router, provider = self.router([ProviderPermanentError(message), response()])
                router.execute_reviewer('prompt', 'review-0')
                self.assertEqual([c[0] for c in provider.calls], ['gemma4:31b-cloud', 'gpt-oss:120b-cloud'])
                self.assertEqual([r.attempt for r in router.ledger.records], [1, 2])
                self.assertIn('PRIMARY_UNAVAILABLE; reduced independence', router.ledger.records[-1].routing_reason)
                self.assertEqual(router.ledger.records[0].outcome, 'REVIEWER_MODEL_UNAVAILABLE')

    def test_quota_stops_without_switch_even_when_unavailability_also_present(self):
        for message in ('Ollama HTTP 402', 'Ollama HTTP 429', 'quota exhausted',
                        'no credits', 'billing required', 'HTTP 410: quota exhausted'):
            with self.subTest(message=message):
                router, provider = self.router([ProviderPermanentError(message)])
                with self.assertRaisesRegex(CloudRoleRoutingError, 'REVIEWER_CLOUD_QUOTA_STOP'):
                    router.execute_reviewer('prompt', 'review-0')
                self.assertEqual(len(provider.calls), 1)
                self.assertEqual(router.ledger.records[0].outcome, 'REVIEWER_CLOUD_QUOTA_STOP')

    def test_both_unavailable_stop_never_local(self):
        router, provider = self.router([ProviderPermanentError('HTTP 404'), ProviderPermanentError('HTTP 410')])
        with self.assertRaisesRegex(CloudRoleRoutingError, 'REVIEWER_MODEL_UNAVAILABLE'):
            router.execute_reviewer('prompt', 'review-0')
        self.assertEqual([c[0] for c in provider.calls], ['gemma4:31b-cloud', 'gpt-oss:120b-cloud'])

    def test_transient_failure_does_not_retry_reset_or_switch(self):
        router, provider = self.router([ProviderTransientError('timeout')])
        with self.assertRaisesRegex(CloudRoleRoutingError, 'REVIEWER_PROVIDER_ERROR'):
            router.execute_reviewer('prompt', 'review-0')
        self.assertEqual(len(provider.calls), 1)

    def test_success_content_is_not_scanned_for_provider_errors(self):
        router, provider = self.router([response('quota credito billing model not found HTTP 404')])
        router.execute_reviewer('prompt', 'review-0')
        self.assertEqual(len(provider.calls), 1)
        self.assertEqual(router.ledger.records[0].outcome, 'SUCCESS')

    def test_configuration_rejects_local_and_unapproved_models(self):
        for model in ('qwen2.5-coder:7b', 'another-cloud', ''):
            with self.subTest(model=model), self.assertRaises(RouterError):
                CloudRoleModelConfig(primary=model)

    def test_quota_on_alternative_stops(self):
        router, provider = self.router([ProviderPermanentError('HTTP 410'), ProviderPermanentError('HTTP 429')])
        with self.assertRaisesRegex(CloudRoleRoutingError, 'REVIEWER_CLOUD_QUOTA_STOP'):
            router.execute_reviewer('prompt', 'review-0')
        self.assertEqual(len(provider.calls), 2)

    def test_unexpected_cost_fails_closed(self):
        router, _ = self.router([ProviderResponse('x', 1, 1, actual_cost=Decimal('0.01'))])
        with self.assertRaisesRegex(CloudRoleRoutingError, 'REVIEWER_CLOUD_COST_STOP'):
            router.execute_reviewer('prompt', 'review-0')

    def test_production_orchestrator_records_reviewer_stops_and_usage(self):
        patch_text = json.dumps({'schema_version': '1.0', 'path': 'calculator.py',
                                 'old_text': 'return a - b', 'new_text': 'return a + b', 'summary': 'Fix addition'})
        for outcome, expected in ((ProviderPermanentError('HTTP 429: quota'), 'REVIEWER_CLOUD_QUOTA_STOP'),
                                  (response('{"status":"PASS"}'), 'REVIEWER_CONTRACT_INVALID')):
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); repo = make_demo(root)
                with patch('forgelab.orchestrator.OllamaProvider.invoke', side_effect=[response(ai_plan()), response(patch_text), outcome]) as invoke:
                    run = run_multi_agent(request(repo, objective='Fix addition', operation='ai_generate',
                                                  old_text='', new_text='', max_repair_attempts=0), root/'runs')
                self.assertEqual(invoke.call_args_list[-1].args[0], 'gemma4:31b-cloud')
                self.assertEqual(json.loads((run/'RunSummary.json').read_text())['status'], 'CLOSED')
                self.assertEqual(json.loads((run/'ReviewerFailure.json').read_text())['reason'], expected)
                records = json.loads((run/'UsageReport.json').read_text())['records']
                self.assertEqual(records[-1]['policy_route'], 'REVIEWER')
                self.assertNotEqual(json.loads((run/'GateDecision.json').read_text())['decision'], 'APPROVE')


    def test_support_error_policy_switch_stop_and_never_local(self):
        cases = [
            ([ProviderPermanentError(message), response()], None, 2)
            for message in ('HTTP 404', 'HTTP 410', 'model retired', 'model not found')
        ] + [
            ([ProviderPermanentError(message)], 'SUPPORT_CLOUD_QUOTA_STOP', 1)
            for message in ('HTTP 402', 'HTTP 429', 'quota exhausted', 'no credits',
                            'billing required', 'HTTP 410: quota exhausted')
        ] + [
            ([ProviderPermanentError('HTTP 404'), ProviderPermanentError('HTTP 410')],
             'SUPPORT_MODEL_UNAVAILABLE', 2),
            ([ProviderPermanentError('HTTP 410'), ProviderPermanentError('HTTP 429')],
             'SUPPORT_CLOUD_QUOTA_STOP', 2),
            ([ProviderTransientError('timeout')], 'SUPPORT_PROVIDER_ERROR', 1),
        ]
        for outcomes, expected, count in cases:
            with self.subTest(outcomes=str(outcomes)):
                router, provider = self.router(outcomes)
                def execute():
                    return router.execute(TaskClass.S2, 'prompt', 'support-1', 'SUPPORT', 'diagnose')
                if expected:
                    with self.assertRaises(CloudRoleRoutingError) as error:
                        execute()
                    self.assertEqual(error.exception.reason, expected)
                    self.assertEqual(error.exception.role, 'SUPPORT')
                else:
                    execute()
                    self.assertIn('reduced independence', router.ledger.records[-1].routing_reason)
                self.assertEqual([c[0] for c in provider.calls],
                                 ['gemma4:31b-cloud', 'gpt-oss:120b-cloud'][:count])
                self.assertTrue(all(r.policy_route == r.agent_role == 'SUPPORT'
                                    for r in router.ledger.records))

    def test_production_support_quota_stops_before_repair_and_records_evidence(self):
        wrong_patch = json.dumps({'schema_version': '1.0', 'path': 'calculator.py',
                                  'old_text': 'return a - b', 'new_text': 'return a * b',
                                  'summary': 'Wrong candidate'})
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); repo = make_demo(root)
            with patch('forgelab.orchestrator.OllamaProvider.invoke', side_effect=[
                response(ai_plan()), response(wrong_patch), ProviderPermanentError('HTTP 429: quota')
            ]) as invoke:
                run = run_multi_agent(request(repo, operation='ai_generate', old_text='', new_text='',
                                              max_repair_attempts=1), root/'runs')
            self.assertEqual(len(invoke.call_args_list), 3)
            self.assertEqual(invoke.call_args_list[-1].args[0], 'gemma4:31b-cloud')
            failure = json.loads((run/'SupportFailure.json').read_text())
            self.assertEqual(failure['reason'], 'SUPPORT_CLOUD_QUOTA_STOP')
            self.assertEqual(failure['attempts'][0]['agent_role'], 'SUPPORT')
            self.assertEqual(json.loads((run/'RunSummary.json').read_text())['status'], 'CLOSED')
            self.assertNotEqual(json.loads((run/'GateDecision.json').read_text())['decision'], 'APPROVE')

    def test_all_support_and_correction_prompt_builders_include_oracle_rule(self):
        import ast
        from forgelab import orchestrator
        tree = ast.parse(Path(orchestrator.__file__).read_text(encoding='utf-8'))
        expected = {'diagnostic_prompt', 'prewrite_repair_prompt', 'correction_prompt',
                    'repair_prompt', 'repair_prewrite_prompt', 'semantic_review_correction_prompt',
                    'semantic_repair_prompt', 'semantic_prewrite_prompt', 'semantic_test_correction_prompt'}
        checked = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                names = {t.id for t in node.targets if isinstance(t, ast.Name)} & expected
                if names:
                    self.assertTrue(any(isinstance(n, ast.Name) and n.id == 'GENERATED_TEST_REPAIR_RULE'
                                        for n in ast.walk(node.value)), names)
                    checked |= names
        self.assertEqual(checked, expected)
        rule = orchestrator.GENERATED_TEST_REPAIR_RULE
        for required in ('NOT an oracle', 'recompute', 'objective and the test inputs', 'fix the TEST',
                         'rounding or bucketing not required by the objective'):
            self.assertIn(required, rule)


if __name__ == '__main__':
    unittest.main()
