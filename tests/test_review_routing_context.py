"""Synthetic privacy/provenance tests; no account or provider calls."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from orchestrator import review_routing_context as routing

class RoutingContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.binary = self.root / 'claude'
        self.binary.write_bytes(b'synthetic executable, never run')
        self.request = self.root / 'request.json'
        self.request.write_bytes(routing.encoded({'command': [str(self.binary), '--model', 'claude-fable-5', '--setting-sources', ''], 'scope': 'synthetic-review', 'reviewed_commit': 'a' * 40}))
        self.kw = dict(request_path=self.request, executable=self.binary,
                       executable_sha256=hashlib.sha256(self.binary.read_bytes()).hexdigest(),
                       environment={}, cwd=self.root, mode='PRE_LAUNCH')
    def test_uses_supplied_environment_not_test_process(self):
        with patch.dict(os.environ, {'ANTHROPIC_MODEL': 'claude-opus-5'}):
            value = routing.capture(**self.kw, managed_settings=[])
        self.assertEqual(value['named_environment']['ANTHROPIC_MODEL'], {'status':'ABSENT'})
        self.assertFalse(value['effective_cli_policy_exported'])
        self.assertFalse(value['qualification_authority'])
    def test_request_and_executable_bytes_bound(self):
        value = routing.capture(**self.kw)
        self.assertEqual(value['request']['sha256'], routing.digest(self.request.read_bytes()))
        self.assertEqual(value['executable']['sha256'], self.kw['executable_sha256'])
        self.assertEqual(value['child_cwd'], str(self.root))
        self.binary.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'ROUTING_EXECUTABLE_CHANGED'):
            routing.capture(**self.kw)
    def test_modes_do_not_claim_historical_or_authenticated_account(self):
        for mode in routing.MODES:
            value = routing.capture(**(self.kw | {'mode': mode}))
            self.assertEqual(value['mode'], mode)
            self.assertFalse(value['historical_environment_reconstructed'])
            self.assertEqual(value['authenticated_claude_account'], 'NOT_OBSERVED')
        with self.assertRaises(ValueError):
            routing.capture(**(self.kw | {'mode':'HISTORICAL_RECONSTRUCTION'}))
    def test_environment_secrets_and_url_components_excluded(self):
        environment={'ANTHROPIC_API_KEY':'secret-key-A', 'ANTHROPIC_AUTH_TOKEN':'secret-token-B',
                     'UNRELATED':'secret-unrelated-C', 'ANTHROPIC_MODEL':'secret-model-D',
                     'ANTHROPIC_BASE_URL':'https://secret-user-E:secret-pass-F@api.anthropic.com/private?token=secret-query-G#secret-fragment-H',
                     'ANTHROPIC_DEFAULT_OPUS_MODEL':'claude-opus-5'}
        raw=routing.encoded(routing.capture(**(self.kw | {'environment':environment}))).decode()
        for value in ('secret-key-A','secret-token-B','secret-unrelated-C','secret-model-D','secret-user-E','secret-pass-F','secret-query-G','secret-fragment-H'):
            self.assertNotIn(value, raw)
        self.assertIn('api.anthropic.com',raw)
        self.assertIn('claude-opus-5',raw)
    def test_named_settings_only_and_nested_env_filtered(self):
        settings=self.root/'managed-settings.json'
        settings.write_text(json.dumps({'switchModelsOnFlag':True,'model':'claude-fable-5',
            'apiKeyHelper':'secret-helper-command','unknown':{'token':'secret-nested'},
            'env':{'ANTHROPIC_DEFAULT_OPUS_MODEL':'claude-opus-4-8','ANTHROPIC_AUTH_TOKEN':'secret-env'},
            'modelOverrides':{'secret-map-key':'secret-map-value'}}))
        raw=routing.encoded(routing.capture(**self.kw,managed_settings=[settings])).decode()
        for value in ('secret-helper-command','secret-nested','secret-env','secret-map-key','secret-map-value'):
            self.assertNotIn(value,raw)
        self.assertIn('claude-opus-4-8',raw)
    def test_missing_malformed_and_duplicate_settings_are_not_defaults(self):
        for raw in (b'{broken', b'{"model":"claude-fable-5","model":"claude-opus-5"}',b'{"model":NaN}'):
            p=self.root/'managed-settings.json';p.write_bytes(raw)
            value=routing.capture(**self.kw,managed_settings=[p])
            self.assertEqual(value['managed_settings'][0]['status'],'UNOBSERVED_READ_OR_PARSE_REFUSED')
            self.assertNotIn('projection',value['managed_settings'][0])
        value=routing.capture(**self.kw,managed_settings=[self.root/'absent.json'])
        self.assertEqual(value['managed_settings'][0]['status'],'ABSENT')
    def test_symlink_settings_refused_but_executable_resolution_explicit(self):
        p=self.root/'managed-settings.json';p.write_text('{"model":"claude-opus-5"}')
        link=self.root/'link.json';link.symlink_to(p)
        value=routing.capture(**self.kw,managed_settings=[link])
        self.assertEqual(value['managed_settings'][0]['status'],'UNOBSERVED_READ_OR_PARSE_REFUSED')
        executable=self.root/'cli-link';executable.symlink_to(self.binary)
        value=routing.capture(**(self.kw | {'executable':executable}))
        self.assertEqual(value['executable']['resolved_path'],str(self.binary))
    def test_credential_or_global_config_not_a_managed_settings_input(self):
        for name in ('.credentials.json','auth.json','token.json','.claude.json','.config.json'):
            with self.assertRaisesRegex(ValueError,'ROUTING_MANAGED_SETTINGS_ONLY'):
                routing.capture(**self.kw,managed_settings=[self.root/name])
    def test_no_launch_or_file_write(self):
        before={p.name:p.read_bytes() for p in self.root.iterdir()}
        with patch('subprocess.Popen',side_effect=AssertionError('no process expected')):
            routing.capture(**self.kw)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.root.iterdir()})
    def test_bound_settings_and_sidecar(self):
        with self.assertRaisesRegex(ValueError,'ROUTING_SETTINGS_COUNT'):
            routing.capture(**self.kw,managed_settings=[self.root/'a.json']*17)
        p=self.root/'oversize.json';p.write_bytes(b' ' * 2000001)
        value=routing.capture(**self.kw,managed_settings=[p])
        self.assertEqual(value['managed_settings'][0]['status'],'UNOBSERVED_READ_OR_PARSE_REFUSED')
        self.assertLess(len(routing.encoded(value)),100000)

    def test_different_selected_executable_refused(self):
        other=self.root/'other';other.write_bytes(self.binary.read_bytes())
        with self.assertRaisesRegex(ValueError,'ROUTING_COMMAND_EXECUTABLE_MISMATCH'):
            routing.capture(**(self.kw | {'executable':other}))
    def test_global_cache_is_whitelisted_and_not_live_state(self):
        cache=self.root/'.config.json'
        cache.write_text(json.dumps({'oauthAccount':{'emailAddress':'secret-account'},
            'cachedGrowthBookFeatures':{'tengu_dash_flame':True,'secret-feature':'secret-feature-value'},
            'clientDataCache':{'convolute_arcades':False,'token':'secret-client-token'},
            'clientDataCacheSlots':{'secret-slot-key':{'data':{'convolute_arcades':True,'secret':'secret-slot-value'}}},
            'modelAccessCache':[{'apiName':'claude-opus-5','entitled':True,'secret':'secret-access'}]}))
        value=routing.capture(**self.kw,config_cache=cache)
        raw=routing.encoded(value).decode()
        for secret in ('secret-account','secret-feature-value','secret-client-token','secret-slot-key','secret-slot-value','secret-access'):
            self.assertNotIn(secret,raw)
        self.assertTrue(value['config_cache']['projection']['features']['tengu_dash_flame'])
        self.assertFalse(value['config_cache']['projection']['active_slot_or_live_payload_observed'])
    def test_plan_bound_and_output_exclusive(self):
        plan=dict(self.kw);plan.pop('environment')
        for key in ('request_path','executable','cwd'):plan[key]=str(plan[key])
        plan.update(schema='review-routing-capture-plan/v1',managed_settings=[],config_cache=None,launcher_sha256='b'*64)
        raw=routing.encoded(plan);value=routing.capture_plan(raw,environment={})
        self.assertEqual(value['plan_sha256'],routing.digest(raw))
        output=self.root/'routing-context.json'
        pin=routing.write_sidecar(output,value)
        self.assertEqual(pin['sha256'],routing.digest(output.read_bytes()))
        self.assertEqual(output.stat().st_mode & 0o777,0o600)
        with self.assertRaises(FileExistsError):routing.write_sidecar(output,value)
        self.assertEqual(pin['sha256'],routing.digest(output.read_bytes()))

if __name__ == '__main__':
    unittest.main()
