"""Exercise the actual V2 courier with synthetic Git/provider boundaries only."""
import copy
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from types import SimpleNamespace

import pytest

from orchestrator import deployment_review as gate
from orchestrator import inspection_bootstrap as baseline
from orchestrator import review_input_codec as codec
from orchestrator.inspection_source import write_once
from test_inspection_bootstrap import SOURCE, inputs, originals
from test_review_policy_baseline import synthetic_proof


CANDIDATE = 'b' * 40
PILOT = Path(gate.__file__).resolve().parents[1] / 'scripts/pilot_review.py'


@pytest.fixture
def courier(tmp_path, monkeypatch):
    proof, files, context = synthetic_proof()
    approved = baseline.validate_policy_baseline(proof)
    root = tmp_path / 'candidate'
    root.mkdir()
    candidate = dict(files)
    candidate['scripts/pilot_review.py'] = PILOT.read_bytes()
    candidate['orchestrator/change_requests.py'] = b'# Synthetic V2 mandatory validator literal.\n'
    # The candidate may propose a different policy, without becoming its own anchor.
    operating = codec.parsed(candidate['configs/scientific-operating-context.json'])
    operating['roles']['claude'] = 'Synthetic candidate role, not approved instructions'
    candidate['configs/scientific-operating-context.json'] = codec.encoded(operating)
    for name, raw in candidate.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    proof_path = tmp_path / 'approved-proof'
    for name, raw in proof.items():
        write_once(proof_path / name, raw)
    # Fixture parents must satisfy the real private-tree reader under any test umask.
    for path in [proof_path, *proof_path.rglob('*')]:
        if path.is_dir():
            path.chmod(0o700)
    output = tmp_path / 'review'
    calls = []

    def git_read(argv, **kwargs):
        assert argv[0] == 'git', 'No non-Git subprocess check is permitted'
        assert Path(kwargs['cwd']) == root
        if argv[1:] == ['rev-parse', 'HEAD']:
            return CANDIDATE + '\n'
        if argv[1:] == ['status', '--porcelain']:
            return b''
        assert argv[1] == 'show' and argv[2].startswith(CANDIDATE + ':')
        return (root / argv[2].split(':', 1)[1]).read_bytes()

    class Provider:
        def __init__(self, argv, **kwargs):
            calls.append({'argv': argv, 'kwargs': kwargs})
            self.stdout = kwargs['stdout']
            self.pid = os.getpid()  # Existing harmless proc metadata; no child is launched.
            self.returncode = 0

        def communicate(self, prompt, timeout):
            assert timeout == 600
            calls[-1]['prompt'] = prompt
            result = {'type': 'result', 'subtype': 'success', 'is_error': False,
                      'session_id': 'synthetic-v2-courier-session',
                      'modelUsage': {gate.MODEL: {}}, 'structured_output': {
                          'scope': baseline.SCOPE, 'reviewed_commit': CANDIDATE,
                          'verdict': 'APPROVE',
                          'findings': ['Synthetic offline result; not actual approval.']}}
            events = [{'type': 'system', 'subtype': 'init',
                       'session_id': result['session_id'], 'tools': ['StructuredOutput'],
                       'mcp_servers': [], 'permissionMode': 'dontAsk'},
                      {'type': 'assistant', 'session_id': result['session_id'],
                       'message': {'model': gate.MODEL}}, result]
            self.stdout.write(b''.join(codec.encoded(row) + b'\n' for row in events))

    monkeypatch.setattr(subprocess, 'check_output', git_read)
    monkeypatch.setattr(subprocess, 'Popen', Provider)
    monkeypatch.chdir(root)

    def run(*, prepared=False, omit_baseline=False, expected_source=SOURCE):
        argv = [str(PILOT), '--scope', baseline.SCOPE, '--files', *sorted(candidate),
                '--private-dir', str(output), '--expected-source', CANDIDATE,
                '--shared-context', '--claude-bin', 'synthetic-no-provider']
        if not omit_baseline:
            argv += ['--policy-baseline', str(proof_path),
                     '--approved-policy-source', expected_source]
        if prepared:
            argv += ['--run-prepared', '--request-sha256',
                     codec.digest((output / 'request.json').read_bytes())]
        else:
            argv += ['--prepare-only']
        monkeypatch.setattr(sys, 'argv', argv)
        old_path = list(sys.path)
        old_umask = os.umask(0o077)
        try:
            if prepared:
                runpy.run_path(str(PILOT), run_name='__main__')
            else:
                with pytest.raises(SystemExit) as stopped:
                    runpy.run_path(str(PILOT), run_name='__main__')
                assert stopped.value.code == 0
        finally:
            sys.path[:] = old_path
            os.umask(old_umask)

    return SimpleNamespace(run=run, root=root, output=output, proof=proof,
                           proof_path=proof_path, candidate=candidate,
                           approved=approved, context=context, calls=calls)


def review_originals(courier):
    return {name: (courier.output / name).read_bytes() for name in gate.ORIGINAL_NAMES}


def rebind_request(raw, request):
    """Keep synthetic receipt hashes consistent so the tested semantic guard decides."""
    raw['request.json'] = codec.encoded(request)
    execution = codec.parsed(raw['execution.json'])
    execution.update(request_sha256=codec.digest(raw['request.json']),
                     prompt_sha256=codec.digest(request['prompt'].encode()))
    raw['execution.json'] = codec.encoded(execution)
    intent = codec.parsed(raw['intent.json'])
    intent['request_sha256'] = codec.digest(raw['request.json'])
    raw['intent.json'] = codec.encoded(intent)


def test_actual_fresh_and_prepared_v2_preserve_distinct_policy_and_candidate(courier):
    courier.run()
    assert not courier.calls and not (courier.output / 'intent.json').exists()
    request_raw = (courier.output / 'request.json').read_bytes()
    request = codec.parsed(request_raw)
    assert request['policy_baseline'] == courier.approved['descriptor']
    assert request['policy_baseline']['source'] == SOURCE != request['reviewed_commit']
    assert (courier.output / 'context_implementation_review.json').read_bytes() == courier.context
    saved = baseline.read_policy_baseline(courier.output / 'policy-baseline')
    assert saved == courier.proof
    reader = codec.Reader(request['prompt'].encode())
    reader.literal(codec.PREFIX_V2.encode())
    reader.line()
    reader.frame('baseline', 'approved-policy-baseline')
    _, shown = reader.frame('context', 'shared-role-context')
    assert codec.parsed(shown) == codec.parsed(courier.context)  # Different closure stays inline.
    assert courier.proof['review/request.json'].decode() not in request['prompt']
    courier.run(prepared=True)
    assert len(courier.calls) == 1
    assert courier.calls[0]['prompt'] == request['prompt'].encode()
    execution = codec.parsed((courier.output / 'execution.json').read_bytes())
    assert execution['policy_baseline'] == courier.approved['descriptor']
    assert execution['request_sha256'] == codec.digest(request_raw)
    result = gate._review_originals(review_originals(courier), CANDIDATE,
                                   {baseline.SCOPE}, policy_baseline=saved)
    assert result['source_text'] == {name: raw.decode() for name, raw in courier.candidate.items()}
    baseline.require_v2_review(review_originals(courier))
    assert baseline.validate_bootstrap(review_originals(courier), CANDIDATE, courier.candidate,
        policy_baseline=saved)['source_text'] == result['source_text']


@pytest.mark.parametrize('defect', ['absent', 'wrong-selected-source', 'mutated-proof'])
def test_fresh_policy_failure_precedes_output_and_provider(courier, defect):
    if defect == 'mutated-proof':
        path = courier.proof_path / 'review/response.json'
        path.chmod(0o600)
        path.write_bytes(path.read_bytes() + b' ')
    with pytest.raises(ValueError):
        courier.run(omit_baseline=defect == 'absent',
                    expected_source='c' * 40 if defect == 'wrong-selected-source' else SOURCE)
    assert not courier.calls
    assert not courier.output.exists()


@pytest.mark.parametrize('defect', ['missing-proof', 'mutated-proof', 'descriptor',
                                  'context-file', 'context-prompt', 'v1-relabel'])
def test_prepared_policy_failure_precedes_intent_and_provider(courier, defect):
    courier.run()
    request_path = courier.output / 'request.json'
    request = codec.parsed(request_path.read_bytes())
    if defect == 'missing-proof':
        (courier.output / 'policy-baseline/review/request.json').unlink()
    elif defect == 'mutated-proof':
        path = courier.output / 'policy-baseline/review/response.json'
        path.chmod(0o600)
        path.write_bytes(path.read_bytes() + b' ')
    elif defect == 'descriptor':
        request['policy_baseline']['source'] = 'c' * 40
    elif defect == 'context-file':
        (courier.output / 'context_implementation_review.json').write_bytes(courier.context + b' ')
    elif defect == 'context-prompt':
        altered = codec.parsed(courier.context)
        altered['recorded_changes'] = [{'synthetic': 'Changed original context'}]
        request['prompt'] = codec.encode_v2(baseline.SCOPE, CANDIDATE,
            {name: raw.decode() for name, raw in courier.candidate.items()}, {}, [],
            codec.context_original(altered), courier.approved['descriptor'])
    elif defect == 'v1-relabel':
        request['input_presentation'] = codec.FORMAT
    request_path.write_bytes(codec.encoded(request))
    # Recompute the requested request SHA deliberately: these semantic guards must still reject.
    with pytest.raises(ValueError):
        courier.run(prepared=True)
    assert not courier.calls and not (courier.output / 'intent.json').exists()


@pytest.mark.parametrize('defect', ['absent-proof', 'mutated-proof', 'request-descriptor',
                                  'execution-descriptor', 'unapproved-role',
                                  'unapproved-shared-field', 'v1-relabel'])
def test_v2_terminal_validator_refuses_consistently_rehashed_substitution(courier, defect):
    courier.run()
    courier.run(prepared=True)
    raw = review_originals(courier)
    proof = copy.deepcopy(courier.proof)
    request = codec.parsed(raw['request.json'])
    if defect == 'absent-proof':
        proof = None
    elif defect == 'mutated-proof':
        proof['review/response.json'] += b' '
    elif defect == 'request-descriptor':
        request['policy_baseline']['source'] = 'c' * 40
    elif defect == 'execution-descriptor':
        execution = codec.parsed(raw['execution.json'])
        execution['policy_baseline']['source'] = 'c' * 40
        raw['execution.json'] = codec.encoded(execution)
    elif defect in {'unapproved-role', 'unapproved-shared-field'}:
        altered = codec.parsed(courier.context)
        if defect == 'unapproved-role':
            altered['role'] = 'Synthetic unapproved role'
            altered['shared_policy']['operating_context']['manifest']['roles']['claude'] = altered['role']
        else:
            altered['shared_policy']['unapproved_instruction'] = 'Synthetic unapproved instruction'
        # Build a syntactically valid V2 envelope without changing the actual bound baseline.
        prompt = request['prompt'].encode()
        reader = codec.Reader(prompt)
        reader.literal(codec.PREFIX_V2.encode()); reader.line()
        reader.frame('baseline', 'approved-policy-baseline')
        start = reader.position
        reader.frame('context', 'shared-role-context')
        request['prompt'] = (prompt[:start] + codec.frame('context', 'shared-role-context',
            codec.encoded(altered).decode()) + prompt[reader.position:]).decode()
        request['shared_context_sha256'] = codec.digest(codec.context_original(altered))
    elif defect == 'v1-relabel':
        request['input_presentation'] = codec.FORMAT
    rebind_request(raw, request)
    with pytest.raises(ValueError):
        gate._review_originals(raw, CANDIDATE, {baseline.SCOPE}, policy_baseline=proof)


def test_historical_v1_originals_remain_exact_and_reject_added_v2_proof():
    files, context = inputs()
    raw = originals(files, context)
    before = copy.deepcopy(raw)
    checked = gate._review_originals(raw, SOURCE, {baseline.SCOPE})
    assert checked['source_text'] == {name: value.decode() for name, value in files.items()}
    assert raw == before
    proof, _, _ = synthetic_proof()
    with pytest.raises(ValueError, match='DEPLOYMENT_LEGACY_POLICY_BASELINE_RELABEL'):
        gate._review_originals(raw, SOURCE, {baseline.SCOPE}, policy_baseline=proof)
