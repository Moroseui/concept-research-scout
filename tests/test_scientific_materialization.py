"""Mechanical artifact-copy tests, not scientific/model approval evidence."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import orchestrator
from orchestrator import scientific_materialization as material
from orchestrator.hosted_cycle import encoded


class ScientificMaterialization(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name); self.root = self.base/'installed'; self.root.mkdir()
        self.state = self.base/'state'; self.state.mkdir(mode=0o700)
        (self.root/'support.py').write_text('VALUE = 1\n')
        old = self.root/'campaigns/isles24-pilot/experiments/P001/run.py'
        old.parent.mkdir(parents=True); old.write_text('# Preserved baseline fixture\n')
        subprocess.run(['git', 'init', '-q'], cwd=self.root, check=True)
        subprocess.run(['git', 'add', '.'], cwd=self.root, check=True)
        subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@local.invalid',
                        'commit', '-qm', 'Fixture source'], cwd=self.root, check=True)
        self.source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=self.root, text=True).strip()
        self.config = {'source': self.source, 'source_root': str(self.root), 'state': str(self.state),
                       'controller_uid': os.getuid()}
        self.by = {'kind': 'agent', 'family': 'codex', 'model': 'unit-fixture', 'session_id': 'fixture-materializer'}
        self.prefix = 'campaigns/isles24-pilot/experiments/P002/'
        self.blobs = {
            'propose': {'round-1/proposal.md': b'Existing reviewed unit-fixture idea.\n'},
            'specify': {'round-1/SPEC.proposed.md': b'Exact fixture specification.\r\n'},
            'code_bundle': {'round-1/run.proposed.py': b'VALUE = 2\n',
                'round-1/validate_return.proposed.py': b'def verify(*args): return {}\n',
                'round-1/requirements.proposed.txt': b'numpy==1.2.3\n',
                'round-1/publication.proposed.json': b'{"allowed":[],"required":[]}\n',
                'round-1/test.proposed.py': b'assert 2 + 2 == 4\n'},
        }
        self.proposals = []
        for index, (mode, files) in enumerate(self.blobs.items(), 1):
            task = str(index)*64; folder = self.state/'tasks'/task; folder.mkdir(parents=True)
            packet = {'campaign_task': {'mode': mode, 'experiment': 'P002'}}
            if mode in ('specify', 'code_bundle'):
                packet['campaign_task']['protocol'] = {'decision_sha256': 'a'*64}
            (folder/'packet.json').write_bytes(encoded(packet))
            (folder/'scientific-disposition.json').write_text(json.dumps({'task': task,
                'review_verdict': 'APPROVE', 'acceptance_status': 'APPROVED_PROPOSAL_ONLY'}))
            self.proposals.append({'task': task, 'source': self.source, 'mode': mode,
                'packet_sha256': hashlib.sha256(encoded(packet)).hexdigest(), 'artifacts': {name: hashlib.sha256(raw).hexdigest() for name, raw in files.items()}})
        required = {self.prefix+name for name in ('SPEC.md', 'run.py', 'validate_return.py',
                    'requirements.txt', 'publication.json', 'scientific-origin.json')}
        required |= {'tests/test_prediction_p002.py', 'support.py'}
        def origin(core):
            return {'schema': 'prospective-scientific-origin/v1', **{k: core[k] for k in
                ('source', 'experiment', 'version_id', 'parent_version_sha256', 'proposals', 'protocol_decision_sha256')}}
        def validate(root, core):
            if set(core['files']) != required: raise ValueError('fixture required set')
            for name, expected in core['files'].items():
                if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest() != expected:
                    raise ValueError('fixture current version changed')
            return core
        self.version_module = SimpleNamespace(origin=origin, required_files=lambda *args: required,
            validate_core=validate, verify_proposals=lambda core, **kw: kw['original_client'](core))
        self.version_module.PROPOSAL_FILES = {mode: tuple(Path(name).name for name in files) for mode, files in self.blobs.items()}
        self.version_module.artifact_targets = lambda experiment: {'specify': {'SPEC.proposed.md': self.prefix+'SPEC.md'},
            'code_bundle': {'run.proposed.py': self.prefix+'run.py', 'validate_return.proposed.py': self.prefix+'validate_return.py',
                'requirements.proposed.txt': self.prefix+'requirements.txt', 'publication.proposed.json': self.prefix+'publication.json',
                'test.proposed.py': 'tests/test_prediction_p002.py'}}
        def read_ref(config, reference):
            proposal = next(p for p in self.proposals if p['task'] == reference['task'])
            return self.blobs[proposal['mode']][reference['artifact']]
        self.continuing_module = SimpleNamespace(read_reference=read_ref)
        self.patches = [patch.object(orchestrator, 'scientific_versions', self.version_module, create=True),
                       patch.object(orchestrator, 'continuing_research', self.continuing_module, create=True)]
        for item in self.patches: item.start(); self.addCleanup(item.stop)

    def create(self, **overrides):
        request = {'experiment': 'P002', 'version_id': 'fixture-v1', 'proposals': self.proposals,
            'protocol_decision_sha256': 'a'*64, 'original_client': lambda core: [{'fixture_proof': True}],
            'by': self.by, **overrides}
        return material.materialize(self.config, **request)

    def test_exact_copy_pending_review_attributed_and_originals_unchanged(self):
        originals = {str(p): p.read_bytes() for p in (self.state/'tasks').rglob('*') if p.is_file()}
        receipt = self.create(); workspace = Path(receipt['workspace'])
        self.assertEqual(receipt['status'], 'PROSPECTIVE_VERSION_PENDING_FULL_REVIEW')
        self.assertEqual(receipt['scientific_version_sha256'], hashlib.sha256((workspace/'scientific-version.json').read_bytes()).hexdigest())
        self.assertEqual(workspace.parent.name, receipt['scientific_version_sha256'])
        self.assertEqual(receipt['applied_by'], self.by)
        self.assertEqual((workspace/self.prefix/'SPEC.md').read_bytes(), b'Exact fixture specification.\r\n')
        self.assertEqual((workspace/self.prefix/'run.py').read_bytes(), self.blobs['code_bundle']['round-1/run.proposed.py'])
        self.assertFalse((workspace/self.prefix/'investigator_decision.json').exists())
        self.assertFalse((workspace/self.prefix/'review.json').exists())
        self.assertFalse(receipt['scientific_execution']); self.assertEqual(receipt['model_calls'], 0)
        self.assertEqual(originals, {str(p): p.read_bytes() for p in (self.state/'tasks').rglob('*') if p.is_file()})
        self.assertEqual((self.root/'campaigns/isles24-pilot/experiments/P001/run.py').read_text(), '# Preserved baseline fixture\n')

    def test_duplicate_is_original_reuse_and_changed_applied_file_refuses(self):
        first = self.create(); second = self.create()
        self.assertTrue(second['duplicate']); self.assertEqual(first['scientific_version_sha256'], second['scientific_version_sha256'])
        path = Path(first['workspace'])/self.prefix/'run.py'; path.write_text('later unreviewed change')
        with self.assertRaisesRegex(ValueError, 'ORIGINAL_MATERIALIZATION_CHANGED'): self.create()
        self.assertEqual(path.read_text(), 'later unreviewed change')

    def test_frozen_p001_is_never_materialized(self):
        with self.assertRaisesRegex(ValueError, 'PRESERVES_FROZEN_P001'): self.create(experiment='P001')
        self.assertFalse((self.state/'scientific-versions').exists())

    def test_interrupted_materialization_keeps_original_intent_and_refuses_retry(self):
        save = material.immutable
        def interrupted(path, body):
            if Path(path).name == 'SPEC.md': raise OSError('fixture interruption')
            return save(path, body)
        with patch.object(material, 'immutable', side_effect=interrupted), self.assertRaises(OSError): self.create()
        destination = next(p for p in (self.state/'scientific-versions').iterdir() if p.is_dir())
        intent = (destination/'materialization-intent.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'PARTIAL_MATERIALIZATION_RECONCILIATION_REQUIRED'): self.create()
        self.assertEqual((destination/'materialization-intent.json').read_bytes(), intent)
        self.assertFalse((destination/'materialization.json').exists())

    def test_actual_review_and_provider_refusal_precede_workspace_creation(self):
        folder = self.state/'tasks'/self.proposals[0]['task']
        value = json.loads((folder/'scientific-disposition.json').read_text()); value['review_verdict'] = 'REQUEST_CHANGES'
        (folder/'scientific-disposition.json').write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'REVIEWED_ORIGINAL_PROPOSAL_REQUIRED'): self.create()
        self.assertFalse((self.state/'scientific-versions').exists())
        value['review_verdict'] = 'APPROVE'; (folder/'scientific-disposition.json').write_text(json.dumps(value))
        def refuse(core): raise ValueError('actual original proof refused')
        with self.assertRaisesRegex(ValueError, 'actual original proof refused'): self.create(original_client=refuse)
        self.assertFalse((self.state/'scientific-versions').exists())

    def test_bad_packet_or_extra_code_bundle_output_refuses(self):
        bad = copy.deepcopy(self.proposals); bad[0]['packet_sha256'] = 'b'*64
        with self.assertRaisesRegex(ValueError, 'REVIEWED_ORIGINAL_PROPOSAL_REQUIRED'): self.create(proposals=bad)
        bad = copy.deepcopy(self.proposals); bad[2]['artifacts']['round-1/extra.py'] = 'c'*64
        with self.assertRaisesRegex(ValueError, 'EXACT_FORMAL_OUTPUT_SET_REQUIRED'): self.create(proposals=bad)

    def test_historical_proposal_sources_are_preserved_not_silently_rebound(self):
        old = copy.deepcopy(self.proposals); old[0]['source'] = 'd'*40
        receipt = self.create(proposals=old)
        core = json.loads((Path(receipt['workspace'])/'scientific-version.json').read_text())
        self.assertEqual(core['source'], self.source)
        self.assertEqual(next(p for p in core['proposals'] if p['mode'] == 'propose')['source'], 'd'*40)

    def test_missing_installed_review_support_named_refusal_before_new_workspace(self):
        with self.assertRaisesRegex(ValueError, 'SCIENTIFIC_REVIEW_SUPPORT_NOT_INSTALLED:missing.py'):
            material._source_file(self.root, self.source, 'missing.py')
        self.assertFalse((self.state/'scientific-versions').exists())

    def review_fixture(self, receipt):
        path = self.state/'formal-decisions/fixture/round-1/decision.json'
        path.parent.mkdir(parents=True)
        decision = {'decision': 'APPLY'}
        for key in ('judgment', 'review', 'author_provenance', 'reviewer_provenance'):
            raw = encoded({'fixture': key}); name = key+'.json'
            (path.parent/name).write_bytes(raw)
            decision[key] = {'path': name, 'sha256': hashlib.sha256(raw).hexdigest()}
        path.write_bytes(encoded(decision))
        for name in ('scientific_decision.provider-receipt.json', 'scientific_decision_review.provider-receipt.json'):
            (path.parent/name).write_bytes(encoded({'fixture': name}))
        (path.parent.parent/'authority-transport.json').write_bytes(encoded({'fixture': 'original transport'}))
        self.version_module.ACTION = 'approve_scientific_version'
        self.version_module.TRANSITION = {'from': 'REVIEWED_SCIENTIFIC_VERSION_PROPOSAL', 'to': 'SCIENTIFIC_VERSION_ELIGIBLE'}
        self.version_module.bindings = lambda core: {'scientific_version_sha256': hashlib.sha256(encoded(core)).hexdigest()}
        def checked(root, descriptor, **kwargs):
            self.assertEqual((Path(root)/descriptor['decision_path']).read_bytes(), path.read_bytes())
            return {'status': 'SCIENTIFIC_VERSION_ELIGIBLE', 'fixture': True}
        self.version_module.verify_authority = checked
        self.formal_module = SimpleNamespace(verify_original_decision=lambda *a, **kw: decision)
        item = patch.object(orchestrator, 'formal_decisions', self.formal_module, create=True)
        item.start(); self.addCleanup(item.stop)
        return path

    def attach(self, receipt, path):
        return material.attach_review(self.config, scientific_version_sha256=receipt['scientific_version_sha256'],
            decision_path=path, original_client=lambda *a: None, by=self.by)

    def test_attachment_preserves_actual_originals_and_reuses_exact_completed_copy(self):
        receipt = self.create(); path = self.review_fixture(receipt)
        originals = {str(p): p.read_bytes() for p in path.parent.parent.rglob('*') if p.is_file()}
        first = self.attach(receipt, path); duplicate = self.attach(receipt, path)
        self.assertTrue(duplicate['duplicate']); self.assertEqual(first['descriptor'], duplicate['descriptor'])
        self.assertFalse(first['scientific_acceptance']); self.assertEqual(first['model_calls'], 0)
        self.assertEqual(originals, {str(p): p.read_bytes() for p in path.parent.parent.rglob('*') if p.is_file()})
        attached = Path(first['workspace'])/first['descriptor']['decision_path']
        attached.write_text('changed original')
        with self.assertRaisesRegex(ValueError, 'ORIGINAL_REVIEW_ATTACHMENT_CHANGED'): self.attach(receipt, path)

    def test_attachment_refuses_negative_original_before_creating_authority_directory(self):
        receipt = self.create(); path = self.review_fixture(receipt)
        self.formal_module.verify_original_decision = lambda *a, **kw: {'decision': 'DEFER'}
        with self.assertRaisesRegex(ValueError, 'VERSION_NOT_ELIGIBLE'): self.attach(receipt, path)
        self.assertFalse((Path(receipt['workspace'])/'scientific-authority').exists())
        with self.assertRaisesRegex(ValueError, 'ORIGINAL_FORMAL_DECISION_REQUIRED'):
            self.attach(receipt, self.state/'arbitrary/round-1/decision.json')

    def test_attachment_full_input_failure_preserves_partial_and_never_claims_approval(self):
        receipt = self.create(); path = self.review_fixture(receipt)
        def refuse(*args, **kwargs): raise ValueError('FULL_REVIEW_INPUTS_NOT_SUPPLIED')
        self.version_module.verify_authority = refuse
        with self.assertRaisesRegex(ValueError, 'FULL_REVIEW_INPUTS_NOT_SUPPLIED'): self.attach(receipt, path)
        folder = Path(receipt['workspace'])/'scientific-authority/fixture-v1'
        before = {str(p): p.read_bytes() for p in folder.rglob('*') if p.is_file()}
        self.assertTrue((folder/'attachment-intent.json').exists()); self.assertFalse((folder/'attachment.json').exists())
        with self.assertRaisesRegex(ValueError, 'PARTIAL_REVIEW_ATTACHMENT_RECONCILIATION_REQUIRED'):
            self.attach(receipt, path)
        self.assertEqual(before, {str(p): p.read_bytes() for p in folder.rglob('*') if p.is_file()})

    def job_preparation_fixture(self):
        from orchestrator import scientific_job_inputs as inputs, linux_scientific_jobs as jobs
        receipt = self.create(); path = self.review_fixture(receipt); attached = self.attach(receipt, path)
        root = Path(receipt['workspace']); core = json.loads((root/'scientific-version.json').read_text())
        data = self.base/'data'; data.mkdir()
        protocol_files = {key: encoded({'fixture': key}) for key in ('protocol_sha256', 'partition_registry_sha256',
            'exposure_history_sha256', 'literature_review_sha256', 'methodology_review_sha256')}
        protocol_files['input_manifest_sha256'] = encoded({'schema': 'linux-scientific-inputs/v1', 'root': str(data), 'files': {}})
        bindings = {'source': self.source, 'experiment': 'P002', 'prior_protocol_sha256': None,
            **{key: hashlib.sha256(raw).hexdigest() for key, raw in protocol_files.items()}}
        protocol = {'subject': 'fixture-protocol', 'bindings': bindings, 'decision_path': str(path), 'decision_sha256': 'a'*64}
        refs = {key: {'task': 'f'*64, 'artifact': 'round-1/'+key+'.json', 'sha256': bindings[key]} for key in protocol_files}
        settings = encoded({'schema': 'linux-scientific-settings/v1', 'settings': {'fixture': True},
            'limits': {'wall_seconds': 4, 'cpu_seconds': 4, 'memory_bytes': 268435456, 'output_bytes': 100000, 'output_files': 10}})
        settings_ref = {'task': 'e'*64, 'artifact': 'round-1/settings.json', 'sha256': hashlib.sha256(settings).hexdigest()}
        artifacts = {ref['artifact']: protocol_files[key] for key, ref in refs.items()}
        artifacts[settings_ref['artifact']] = settings
        self.continuing_module.read_reference = lambda cfg, ref: artifacts[ref['artifact']]
        self.continuing_module.protocol_descriptor = lambda value: value
        self.formal_module.verify_original_decision = lambda *a, **kw: {'decision': 'APPLY', '_decision_sha256': 'a'*64}
        ops = SimpleNamespace(read_operation_result=lambda cfg, ref, kinds: {'result':
            {'attachment': attached} if kinds == ('APPROVE_VERSION',) else {'protocol': protocol, 'artifacts': refs}})
        env = {'python_version': '3.13.1', 'executable_sha256': 'c'*64, 'packages': {'numpy': '1.2.3'}}
        job_config = {'source': self.source, 'source_root': str(self.root),
            'proposals': str(self.state/'scientific-versions'), 'input_roots': [str(data)]}
        patches = [patch.object(orchestrator, 'continuing_operations', ops, create=True),
            patch.object(jobs, 'configuration', return_value=job_config),
            patch.object(jobs, 'environment', return_value=env), patch.object(jobs, 'protected', side_effect=Path)]
        for item in patches: item.start(); self.addCleanup(item.stop)
        args = {'version_ref': {'operation': '1'*64, 'result_sha256': '2'*64},
            'protocol_ref': {'operation': '3'*64, 'result_sha256': '4'*64}, 'settings_ref': settings_ref,
            'job_id': 'fixture-job', 'original_client': lambda *a: None, 'by': self.by}
        return inputs, args, artifacts, root, protocol

    def test_job_preparation_uses_saved_refs_fixed_environment_and_preserves_version_core(self):
        inputs, args, artifacts, root, protocol = self.job_preparation_fixture()
        original = (root/'scientific-version.json').read_bytes()
        first = inputs.prepare_job(self.config, **args); second = inputs.prepare_job(self.config, **args)
        self.assertTrue(second['duplicate']); self.assertEqual(first['core'], second['core'])
        self.assertEqual(first['core']['limits']['wall_seconds'], 4)
        self.assertEqual((root/first['core']['settings']).read_bytes(), artifacts['round-1/settings.json'])
        self.assertEqual((root/'scientific-version.json').read_bytes(), original)
        self.assertEqual(first['status'], 'PENDING_LAUNCH_JUDGMENT'); self.assertFalse(first['scientific_acceptance'])
        self.assertEqual(first['core']['environment']['python_version'], '3.13.1')

    def test_independently_reviewed_different_protocol_cannot_rebind_original_spec_or_code(self):
        for mode in ('specify', 'code_bundle'):
            proposal = next(row for row in self.proposals if row['mode'] == mode)
            folder = self.state/'tasks'/proposal['task']; packet = json.loads((folder/'packet.json').read_bytes())
            packet['campaign_task']['protocol']['decision_sha256'] = 'b'*64
            (folder/'packet.json').write_bytes(encoded(packet))
            proposal['packet_sha256'] = hashlib.sha256(encoded(packet)).hexdigest()
            with self.assertRaisesRegex(ValueError, 'PROPOSED_PROTOCOL_IDENTITY_CHANGED'): self.create()
            packet['campaign_task']['protocol']['decision_sha256'] = 'a'*64
            (folder/'packet.json').write_bytes(encoded(packet)); proposal['packet_sha256'] = hashlib.sha256(encoded(packet)).hexdigest()
        self.assertFalse((self.state/'scientific-versions').exists())

    def test_job_preparation_rejects_protocol_change_and_resource_expansion_before_copy(self):
        inputs, args, artifacts, root, protocol = self.job_preparation_fixture()
        protocol['decision_sha256'] = 'b'*64
        with self.assertRaisesRegex(ValueError, 'VERSION_PROTOCOL_CHANGED'): inputs.prepare_job(self.config, **args)
        protocol['decision_sha256'] = 'a'*64
        bad = json.loads(artifacts['round-1/settings.json']); bad['limits']['wall_seconds'] = 999999
        artifacts['round-1/settings.json'] = encoded(bad)
        with self.assertRaisesRegex(ValueError, 'REVIEWED_BOUNDED_SETTINGS_REQUIRED'): inputs.prepare_job(self.config, **args)
        self.assertFalse((root/self.prefix/'job-inputs').exists())

    def test_job_preparation_preserves_partial_and_refuses_same_identity_after_settings_change(self):
        inputs, args, artifacts, root, protocol = self.job_preparation_fixture()
        first = inputs.prepare_job(self.config, **args)
        changed = json.loads(artifacts['round-1/settings.json']); changed['settings']['fixture'] = 'different'
        artifacts['round-1/settings.json'] = encoded(changed)
        with self.assertRaisesRegex(ValueError, 'ORIGINAL_INPUT_DESTINATION_CONFLICT'): inputs.prepare_job(self.config, **args)
        self.assertNotEqual((root/first['core']['settings']).read_bytes(), artifacts['round-1/settings.json'])
        args['job_id'] = 'interrupted-job'; folder = self.state/'scientific-job-proposals'/args['job_id']
        folder.mkdir(); (folder/'intent.json').write_text('Retained fixture interrupted proposal')
        with self.assertRaisesRegex(ValueError, 'PARTIAL_PREPARATION_RECONCILIATION_REQUIRED'):
            inputs.prepare_job(self.config, **args)
        self.assertEqual((folder/'intent.json').read_text(), 'Retained fixture interrupted proposal')


if __name__ == '__main__': unittest.main()
