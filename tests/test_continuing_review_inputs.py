"""Actual source selection and courier preparation; never invoke a model."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from orchestrator import actions_runner, review_input_codec as presentation
from scripts.prepare_handover_snapshot import SERVICE_TEMPLATES, scientific_support_files


def git(root, *arguments):
    return subprocess.check_output(['git', *arguments], cwd=root, stderr=subprocess.PIPE).decode().strip()


def test_installed_module_and_materialization_support_cannot_use_stale_review(tmp_path):
    root = tmp_path/'reviewed'; root.mkdir()
    names = actions_runner.reviewed_files()
    assert set(SERVICE_TEMPLATES) <= set(names)
    assert scientific_support_files(actions_runner.ROOT) <= set(names)
    for name in names:
        target = root/name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(actions_runner.ROOT/name, target)
    new = root/'orchestrator/fixture_new_installed_adapter.py'
    new.write_text('"""Synthetic future installed source dependency."""\n')
    names = actions_runner.reviewed_files(root)
    assert new.relative_to(root).as_posix() in names
    prefix = root/'docs/isles-pilot/reviews/human-controls-handover'
    prefix.parent.mkdir(parents=True, exist_ok=True)
    # Explicit test fixture, not an actual reviewer receipt or scientific result.
    response = {'subtype': 'success', 'structured_output': {
        'verdict': 'APPROVE', 'scope': 'human-controls', 'reviewed_commit': 'a'*40}}
    raw = json.dumps(response).encode()
    Path(str(prefix)+'.response.json').write_bytes(raw)
    evidence = {'returncode': 0, 'reviewed_commit': 'a'*40,
        'assistant_message_models': ['claude-fable-5'], 'response_sha256': hashlib.sha256(raw).hexdigest(),
        'input_file_sha256': {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in names}}
    Path(str(prefix)+'.execution.json').write_text(json.dumps(evidence))
    assert actions_runner.reviewed(root) == 'a'*40
    for name in ('orchestrator/fixture_new_installed_adapter.py', 'scripts/package_pilot.py',
                 'orchestrator/scientific_job_results.py', SERVICE_TEMPLATES[0]):
        path = root/name; original = path.read_bytes(); path.write_bytes(original+b'\n')
        try:
            with pytest.raises(ValueError, match='REVIEW_BINDING_CHANGED'):
                actions_runner.reviewed(root)
        finally:
            path.write_bytes(original)
    missing = evidence['input_file_sha256'].pop('orchestrator/deployment_review.py')
    Path(str(prefix)+'.execution.json').write_text(json.dumps(evidence))
    with pytest.raises(ValueError, match='REVIEW_BINDING_CHANGED'):
        actions_runner.reviewed(root)
    assert missing


def fixture_policy(tmp_path):
    """Real baseline parser over explicit offline synthetic originals, no model."""
    from test_review_policy_baseline import synthetic_proof
    from test_inspection_bootstrap import SOURCE
    from orchestrator.inspection_source import write_once
    from orchestrator.inspection_bootstrap import validate_policy_baseline
    proof, _, _ = synthetic_proof()
    validate_policy_baseline(proof)
    directory = tmp_path/'synthetic-approved-policy'
    for name, raw in proof.items(): write_once(directory/name, raw)
    for path in [directory, *directory.rglob('*')]:
        if path.is_dir(): path.chmod(0o700)
    return ['--shared-context', '--policy-baseline', str(directory), '--approved-policy-source', SOURCE]


@pytest.mark.parametrize('name,accepted', [(name, True) for name in SERVICE_TEMPLATES] + [
    ('deploy/research-system/unreviewed.service.in', False),
    ('other/research-system-scientific-job@.service.in', False)])
def test_courier_prepares_only_exact_service_template_inputs(tmp_path, name, accepted):
    root = tmp_path/'source'; root.mkdir()
    git(root, 'init', '-q')
    git(root, 'config', 'user.name', 'Synthetic source fixture')
    git(root, 'config', 'user.email', 'fixture@example.invalid')
    path = root/name; path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('[Service]\nExecStart=/usr/bin/true\n')
    git(root, 'add', '.'); git(root, 'commit', '-qm', 'Synthetic template only')
    output = tmp_path/'prepared'
    command = [sys.executable, str(actions_runner.ROOT/'scripts/pilot_review.py'),
        '--scope', 'human-controls', '--files', name, '--private-dir', str(output),
        '--expected-source', git(root, 'rev-parse', 'HEAD'), '--prepare-only',
        '--claude-bin', '/must-not-run-fixture-model']
    command += fixture_policy(tmp_path)
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=20)
    if accepted:
        assert result.returncode == 0, result.stderr
        prepared = json.loads((output/'request.json').read_text())
        assert prepared['input_file_sha256'][name] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert not (output/'intent.json').exists()
    else:
        assert result.returncode != 0 and 'unsupported review input' in result.stderr
        assert not output.exists()


@pytest.mark.parametrize('defect', [None, 'proposal', 'source', 'application_source'])
def test_courier_delivers_exact_selected_originals_without_model_call(tmp_path, defect):
    from orchestrator import change_requests as changes, deployment_review as gate
    root = tmp_path/'source'; root.mkdir()
    for name in actions_runner.reviewed_files():
        target = root/name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(actions_runner.ROOT/name, target)
    git(root, 'init', '-q'); git(root, 'config', 'user.name', 'Synthetic courier fixture')
    git(root, 'config', 'user.email', 'fixture@example.invalid')
    git(root, 'add', '.'); git(root, 'commit', '-qm', 'Synthetic source copy for offline preparation')
    source = git(root, 'rev-parse', 'HEAD')
    prepared = tmp_path/'bundle'; prepared.mkdir(mode=0o700)
    store = prepared/'change-inputs'
    actor = {'kind': 'agent', 'family': 'codex', 'model': 'synthetic-only', 'session_id': 'synthetic-only'}
    request = changes.submit(store, root, 'implementation:deployment', 'Review exact original application.',
        actor, source=source, key='synthetic', scope_limits=['No model or host operation.'])
    folder = store/request['identity']
    changes.record(folder, 'AUTHORIZED', actor, {'authority_reference': 'Synthetic only',
        'rationale': 'Offline fixture', 'review_policy': 'Pending actual review'})
    applied = changes.record(folder, 'APPLIED', actor, {'modification': 'Synthetic exact application',
        'checks': 'Offline fixture', 'result_binding': {'source': 'f'*40 if defect=='application_source' else source},
        'review_status': 'PENDING'})
    for n in range(12):
        changes.record(folder, 'DISPOSITION', actor, {'rationale': str(n)+' Preserved original history. '*100,
            'affected_results': 'No actual research.'})
    selection = [{'request': request['identity'], 'applied': applied['identity']}]
    proposal_raw = gate.encoded({'source': source, 'changes': selection})
    (prepared/'proposal.json').write_bytes(proposal_raw)
    sidecar = changes.review_bindings(source, gate.digest(proposal_raw), selection)
    if defect == 'proposal': sidecar['proposal_sha256'] = 'e'*64
    if defect == 'source': sidecar['source'] = 'e'*40
    sidecar_raw = gate.encoded(sidecar)
    (prepared/'change-bindings.json').write_bytes(sidecar_raw)
    output = tmp_path/'review'
    result = subprocess.run([sys.executable, '-B', str(root/'scripts/pilot_review.py'),
        '--scope', 'material-deployment', '--files', 'scripts/pilot_review.py', '--private-dir', str(output),
        '--expected-source', source, '--shared-context', '--change-bindings', str(prepared/'change-bindings.json'),
        '--prepare-only', '--claude-bin', '/must-not-run-fixture-model'] + fixture_policy(tmp_path),
        cwd=root, capture_output=True, text=True, timeout=30)
    assert not (output/'intent.json').exists()
    if defect:
        assert result.returncode != 0, result.stdout
        assert 'exact prepared change selections required' in result.stderr or 'SELECTED_APPLICATION_SOURCE_CHANGED' in result.stderr
        assert not (output/'request.json').exists()
    else:
        assert result.returncode == 0, result.stderr
        actual = json.loads((output/'request.json').read_bytes())
        assert actual['change_bindings_sha256'] == gate.digest(sidecar_raw)
        assert set(actual['private_evidence_sha256'].values()) == {gate.digest(sidecar_raw), gate.digest(proposal_raw)}
        _, _, delivered = presentation.decode_v2(actual['prompt'], actual['scope'], source, actual['shared_context_sha256'], actual['policy_baseline'])
        assert actual['input_presentation'] == presentation.FORMAT_V2
        projection = delivered[0]['projection']
        assert projection['projection']['kind'] == 'BOUNDED_SUMMARY'
        assert projection['requests'][0]['review_status'] == 'PENDING'
        assert projection['selected_applications'][0]['event'] == applied
        assert 'Source:' in actual['prompt'] and actual['shared_context_sha256']

@pytest.fixture
def bounded_courier(tmp_path):
    # A local executable emits synthetic protocol fixtures; no hosted client runs.
    root = tmp_path/'source'; root.mkdir()
    git(root, 'init', '-q')
    git(root, 'config', 'user.name', 'Synthetic courier fixture')
    git(root, 'config', 'user.email', 'fixture@example.invalid')
    (root/'example.py').write_text('# Offline source fixture.\n')
    (root/'scripts').mkdir()
    shutil.copyfile(actions_runner.ROOT/'scripts/pilot_review.py', root/'scripts/pilot_review.py')
    git(root, 'add', '.'); git(root, 'commit', '-qm', 'Synthetic source')
    fake = tmp_path/'synthetic-review-executable'
    fake.write_text('#!'+sys.executable+'\n'+'''import hashlib,json,sys
from pathlib import Path
schema=json.loads(sys.argv[sys.argv.index('--json-schema')+1])
prompt=sys.stdin.buffer.read()
Path('synthetic-invocation.json').write_text(json.dumps({'prompt_sha256':hashlib.sha256(prompt).hexdigest()}))
print(json.dumps({'type':'system','subtype':'init','tools':['StructuredOutput'],'mcp_servers':[],'permissionMode':'dontAsk'}))
print(json.dumps({'type':'assistant','message':{'model':'claude-fable-5'}}))
print(json.dumps({'type':'result','subtype':'success','is_error':False,'session_id':'synthetic-offline-only',
    'structured_output':{'scope':schema['properties']['scope']['const'],'reviewed_commit':schema['properties']['reviewed_commit']['const'],
    'verdict':'APPROVE','findings':['Synthetic protocol fixture only; no actual review.']}}))
''')
    fake.chmod(0o700)
    output = tmp_path/'review'
    command = [sys.executable, '-B', str(actions_runner.ROOT/'scripts/pilot_review.py'),
        '--scope', 'material-deployment', '--files', 'example.py', 'scripts/pilot_review.py', '--private-dir', str(output),
        '--expected-source', git(root, 'rev-parse', 'HEAD'), '--claude-bin', str(fake)]
    command += fixture_policy(tmp_path)
    def invoke(*options):
        return subprocess.run(command+list(options), cwd=root, capture_output=True, text=True, timeout=20)
    def supplement(name, size):
        path = tmp_path/name; path.write_text(name[0]*size); path.chmod(0o600)
        return str(path)
    return output, invoke, supplement


def test_complete_request_over_supplement_limit_prepares_and_replays_once(bounded_courier):
    out, invoke, supplement = bounded_courier
    first = supplement('alpha.txt', 1100000); second = supplement('beta.txt', 1100000)
    prepared = invoke('--prepare-only', '--private-evidence', first, '--private-evidence', second)
    assert prepared.returncode == 0, prepared.stderr
    raw = (out/'request.json').read_bytes()
    assert 2000000 < len(raw) < 4000000
    assert not (out/'intent.json').exists()
    request = json.loads(raw); sha = hashlib.sha256(raw).hexdigest()
    assert request['private_evidence_sha256'] == {
        p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (first, second)}
    assert all(Path(p).read_text() in request['prompt'] for p in (first, second))
    completed = invoke('--run-prepared', '--request-sha256', sha)
    assert completed.returncode == 0, completed.stderr
    assert (out/'request.json').read_bytes() == raw
    invoked = (out/'synthetic-invocation.json').read_bytes()
    assert json.loads(invoked)['prompt_sha256'] == hashlib.sha256(request['prompt'].encode()).hexdigest()
    assert json.loads((out/'execution.json').read_bytes())['request_sha256'] == sha
    assert json.loads((out/'response.json').read_bytes())['session_id'] == 'synthetic-offline-only'
    from orchestrator import deployment_review as gate
    # The real local courier lifecycle is checked by the production original gate;
    # its synthetic executable protocol is not an actual provider review.
    originals = {name: (out/name).read_bytes() for name in
        ('request.json', 'response.json', 'execution.json', 'protocol.jsonl', 'intent.json', 'returned.json')}
    from orchestrator.inspection_bootstrap import read_policy_baseline
    reviewed = gate.review_originals(originals, request['reviewed_commit'],
        policy_baseline=read_policy_baseline(out/'policy-baseline'))
    assert reviewed['source_text']['example.py'] == '# Offline source fixture.\n'
    assert len(reviewed['source_text']) == 2
    again = invoke('--run-prepared', '--request-sha256', sha)
    assert again.returncode != 0 and 'original review intent exists' in again.stderr
    assert (out/'synthetic-invocation.json').read_bytes() == invoked


def test_prepare_rejects_complete_request_above_installed_gate_limit(bounded_courier):
    out, invoke, supplement = bounded_courier
    options = ['--prepare-only']
    for name in ('alpha.txt', 'beta.txt', 'gamma.txt'):
        options += ['--private-evidence', supplement(name, 1400000)]
    result = invoke(*options)
    assert result.returncode != 0 and 'bounded complete prepared request required' in result.stderr
    assert not any((out/name).exists() for name in ('request.json', 'intent.json', 'protocol.jsonl', 'synthetic-invocation.json'))


@pytest.mark.parametrize('defect', ['oversized', 'symlink'])
def test_prepared_request_size_and_regular_file_guards_precede_invocation(bounded_courier, defect):
    out, invoke, supplement = bounded_courier
    assert invoke('--prepare-only').returncode == 0
    request = out/'request.json'
    if defect == 'oversized':
        request.write_bytes(b' ' * 4000001)
    else:
        original = out/'request-original.json'
        request.rename(original); request.symlink_to(original)
    sha = hashlib.sha256(request.read_bytes()).hexdigest()
    result = invoke('--run-prepared', '--request-sha256', sha)
    assert result.returncode != 0 and 'bounded regular' in result.stderr
    assert not any((out/name).exists() for name in ('intent.json', 'protocol.jsonl', 'synthetic-invocation.json'))


def test_complete_request_limit_does_not_expand_supplement_limit(bounded_courier):
    out, invoke, supplement = bounded_courier
    result = invoke('--prepare-only', '--private-evidence', supplement('oversized.txt', 2000001))
    assert result.returncode != 0 and 'bounded regular supplemental evidence required' in result.stderr
    assert not any((out/name).exists() for name in ('request.json', 'intent.json', 'synthetic-invocation.json'))
