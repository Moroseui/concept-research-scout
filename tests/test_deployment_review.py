"""Offline synthetic provider fixtures only; never actual deployment approvals."""
import io
import json
import os
from pathlib import Path
import tarfile

import pytest
from orchestrator import change_requests as c, deployment_review as d, remote_supervisor, review_input_codec as presentation

SOURCE = 'a'*40
PREVIOUS = 'b'*40
ACTOR = {'kind': 'agent', 'family': 'codex', 'model': 'synthetic author', 'session_id': 'synthetic-author'}


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw); path.chmod(0o600)
    return raw


def fixture(tmp_path, monkeypatch, *, selected=False, mutate_selection=None, framed=False, omit_source=False):
    # UID fixtures emulate a protected installation; separate tests refuse actual
    # unprotected paths. No provider, network, services, Git writes or model calls.
    bundle = tmp_path/'bundle'; bundle.mkdir(mode=0o700)
    root = tmp_path/'source'; previous = tmp_path/'previous'; previous.mkdir()
    target = tmp_path/'controller.json'; old = b'{"source":"old"}\n'; new = b'{"source":"new"}\n'
    write(target, old)
    direction = b'Synthetic shared policy.\n'
    authority = d.encoded({'direction_path': 'docs/direction.md', 'direction_sha256': d.digest(direction)})
    operating = d.encoded({'authority_policy': {'path': 'configs/authority.json', 'sha256': d.digest(authority)},
                           'documents': {'docs/direction.md': d.digest(direction)}})
    files = {'orchestrator/example.py': b'# Synthetic fixture\n', 'scripts/pilot_review.py': b'# Synthetic courier fixture\n',
             'configs/scientific-operating-context.json': operating, 'configs/authority.json': authority,
             'docs/direction.md': direction}
    for name, raw in files.items(): write(root/name, raw)
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w:gz') as archive:
        for name, raw in files.items():
            item = tarfile.TarInfo('snapshot/'+name); item.size = len(raw)
            archive.addfile(item, io.BytesIO(raw))
    archive = write(bundle/'source.tar.gz', buffer.getvalue())
    request = c.submit(bundle/'changes', Path(__file__).resolve().parents[1], 'implementation:deployment',
                       'Synthetic pre-use review fixture only.', ACTOR, source=SOURCE, key='fixture',
                       scope_limits=['Offline synthetic fixture only.'])
    change = bundle/'changes'/request['identity']
    c.record(change, 'AUTHORIZED', ACTOR, {'rationale': 'Synthetic fixture', 'authority_reference': 'synthetic', 'review_policy': 'review first'})
    applied = c.record(change, 'APPLIED', ACTOR, {'modification': 'Synthetic implementation', 'checks': 'Fixture only',
                                                 'result_binding': SOURCE, 'review_status': 'PENDING'})
    if selected:
        for n in range(12):
            c.record(change, 'DISPOSITION', ACTOR, {'rationale': str(n)+' Synthetic preserved history. '*100,
                     'affected_results': 'No actual research result.'})
        applied = c.record(change, 'APPLIED', ACTOR, {'modification': 'Final source integration fixture',
            'checks': 'Synthetic checks only', 'result_binding': {'source': SOURCE},
            'supersedes_applied_events': [applied['identity']], 'review_status': 'PENDING'})
    selections = [{'request': request['identity'], 'applied': applied['identity']}]
    projection = c.review_context(bundle/'changes', selections, source=SOURCE) if selected else c.context(bundle/'changes')
    supplied_changes = [{'store': 'synthetic', 'projection': projection}]
    metadata = lambda raw: {'sha256': d.digest(raw), 'uid': 0, 'gid': os.getgid(), 'mode': 0o600}
    recovery = d.encoded({'status': 'PRESERVE_PREVIOUS_AND_PARTIAL', 'synthetic_fixture': True})
    proposal = {'schema': d.SCHEMA, 'profile': d.PROFILE, 'source': SOURCE, 'source_root': str(root),
                'previous_source': PREVIOUS, 'previous_source_root': str(previous),
                'archive_sha256': d.digest(archive), 'source_files': {name: d.digest(raw) for name, raw in files.items()},
                'targets': {str(target): metadata(new)}, 'previous_files': {str(target): metadata(old)},
                'dependencies': {'synthetic-launcher': {'sha256': 'e'*64}},
                'recovery_sha256': d.digest(recovery), 'changes': [{'request': request['identity'], 'applied': applied['identity']}]}
    proposal_raw = write(bundle/'proposal.json', d.encoded(proposal))
    private = [proposal_raw, old, new, recovery]
    selection_sha = None
    if selected:
        sidecar = c.review_bindings(SOURCE, d.digest(proposal_raw), selections)
        if mutate_selection:
            mutate_selection(sidecar, projection)
        sidecar_raw = d.encoded(sidecar); private.append(sidecar_raw)
        selection_sha = d.digest(sidecar_raw)
    for raw in [old, new, recovery]: write(bundle/'literals'/d.digest(raw), raw)
    supplements = {str(i): {'sha256': d.digest(raw), 'content': raw.decode()} for i, raw in enumerate(private)}
    prompt = (d.CHANGES+json.dumps(supplied_changes)+'\nFresh author-operated Fable implementation review, '
              'not execution worker or independent merge desk. Scope human-controls at '+SOURCE+'. Source:\n'
              +json.dumps({name: raw.decode() for name, raw in files.items()})+d.SUPPLEMENT+json.dumps(supplements))
    review_request = {'scope': 'human-controls', 'reviewed_commit': SOURCE, 'prompt': prompt,
                      'input_file_sha256': {name: d.digest(raw) for name, raw in files.items()},
                      'private_evidence_sha256': {name: value['sha256'] for name, value in supplements.items()},
                      'runner_sha256': d.digest(files['scripts/pilot_review.py']),
                      'change_context_sha256': d.digest(json.dumps(supplied_changes, sort_keys=True).encode()),
                      'change_bindings_sha256': selection_sha}
    if framed:
        source_text = {name: raw.decode() for name, raw in files.items()}
        if omit_source:
            source_text.pop('orchestrator/example.py')
            review_request['input_file_sha256'].pop('orchestrator/example.py')
        prompt = presentation.encode('human-controls', SOURCE, source_text, supplements, supplied_changes)
        review_request.update(prompt=prompt, input_presentation=presentation.FORMAT, shared_context_sha256=None)
    response = {'type': 'result', 'subtype': 'success', 'is_error': False, 'session_id': 'synthetic-claude-session',
                'structured_output': {'scope': 'human-controls', 'reviewed_commit': SOURCE, 'verdict': 'APPROVE',
                                      'findings': ['Synthetic fixture only.']}}
    events = [{'type': 'system', 'subtype': 'init', 'tools': ['StructuredOutput'], 'mcp_servers': [], 'permissionMode': 'dontAsk',
               'session_id': response['session_id']},
              {'type': 'assistant', 'session_id': response['session_id'], 'message': {'model': d.MODEL}}, response]
    raw = {'request.json': d.encoded(review_request), 'response.json': d.encoded(response),
           'protocol.jsonl': b''.join(d.encoded(e).replace(b'\n', b'')+b'\n' for e in events)}
    execution = {'reviewed_commit': SOURCE, 'returncode': 0, 'requested_model': d.MODEL,
                 'assistant_message_models': [d.MODEL], 'request_sha256': d.digest(raw['request.json']),
                 'response_sha256': d.digest(raw['response.json']), 'protocol_sha256': d.digest(raw['protocol.jsonl']),
                 'prompt_sha256': d.digest(prompt.encode()), 'input_file_sha256': review_request['input_file_sha256']}
    raw.update({'execution.json': d.encoded(execution), 'intent.json': d.encoded({'reviewed_commit': SOURCE,
                'request_sha256': execution['request_sha256'], 'maximum_invocations': 1, 'automatic_retry': False}),
                'returned.json': d.encoded({'returncode': 0})})
    for name, value in raw.items(): write(bundle/name, value)
    review_actor = {'kind': 'agent', 'family': 'claude', 'model': d.MODEL, 'session_id': response['session_id']}
    original = {key: execution[key] for key in ('request_sha256', 'response_sha256', 'protocol_sha256')}
    payload = {'applied_event': applied['identity'], 'verdict': 'APPROVE', 'rationale': 'Synthetic reviewed fixture only.',
               'review_evidence': 'Synthetic original protocol fixture', 'original_review': original}
    c.record(change, 'REVIEW', review_actor, payload)
    monkeypatch.setattr(d, 'DEPENDENCY_PATHS', {'synthetic-launcher': '/synthetic/launcher'})
    monkeypatch.setattr(d, 'dependency_metadata', lambda name: {'sha256': 'e'*64})
    monkeypatch.setattr(d, 'running_broker', lambda root: {'main_pid': 123, 'cwd': str(root)})
    monkeypatch.setattr(d, 'REQUIRED_TARGETS', {str(target)})
    monkeypatch.setattr(d, 'protected', lambda path, directory=False: Path(path).lstat())
    monkeypatch.setattr(d, 'access', lambda path: (0, os.getgid(), Path(path).stat().st_mode & 0o777))
    monkeypatch.setattr(remote_supervisor, 'checked_source', lambda path, source: Path(path))
    return dict(bundle=bundle, root=root, target=target, new=new, raw=raw, change=change, payload=payload, actor=review_actor)


def test_original_review_and_complete_bundle(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch)
    result = d.verify_bundle(f['bundle'], f['root'], SOURCE)
    assert result['review_model'] == d.MODEL
    assert result['unattended_activation_authority'] is False


@pytest.mark.parametrize('mutation,reason', [
    ('missing_protocol', 'DEPLOYMENT_ORIGINAL_CLAUDE_PROTOCOL_REQUIRED'),
    ('wrong_model', 'DEPLOYMENT_ORIGINAL_CLAUDE_PROTOCOL_REQUIRED'),
    ('negative', 'DEPLOYMENT_EXACT_APPROVING_REVIEW_REQUIRED'),
    ('stale_source', 'DEPLOYMENT_EXACT_APPROVING_REVIEW_REQUIRED'),
    ('metadata_only', 'DEPLOYMENT_REVIEWED_SOURCE_TEXT_CHANGED'),
    ('private_text', 'DEPLOYMENT_REVIEWED_PRIVATE_TEXT_CHANGED'),
    ('request_hash', 'DEPLOYMENT_ORIGINAL_REVIEW_BINDING_CHANGED'),
])
def test_review_refusals(tmp_path, monkeypatch, mutation, reason):
    f = fixture(tmp_path, monkeypatch); raw = dict(f['raw'])
    events = [json.loads(line) for line in raw['protocol.jsonl'].splitlines()]
    response = json.loads(raw['response.json']); request = json.loads(raw['request.json'])
    execution = json.loads(raw['execution.json']); intent = json.loads(raw['intent.json'])
    if mutation == 'missing_protocol': events = [events[-1]]
    if mutation == 'wrong_model': events[1]['message']['model'] = 'wrong-model'
    if mutation == 'negative': response['structured_output']['verdict'] = 'REQUEST_CHANGES'
    if mutation == 'stale_source': response['structured_output']['reviewed_commit'] = PREVIOUS
    if mutation == 'metadata_only': request['input_file_sha256']['orchestrator/example.py'] = 'f'*64
    if mutation == 'private_text': request['prompt'] = request['prompt'].replace('PRESERVE_PREVIOUS_AND_PARTIAL', 'UNREVIEWED_RECOVERY')
    events[-1] = response
    raw['response.json'] = d.encoded(response); raw['request.json'] = d.encoded(request)
    raw['protocol.jsonl'] = b''.join(json.dumps(e).encode()+b'\n' for e in events)
    execution.update(response_sha256=d.digest(raw['response.json']), protocol_sha256=d.digest(raw['protocol.jsonl']),
                     request_sha256=d.digest(raw['request.json']), prompt_sha256=d.digest(request['prompt'].encode()),
                     input_file_sha256=request['input_file_sha256'])
    intent['request_sha256'] = execution['request_sha256']
    if mutation == 'request_hash': execution['request_sha256'] = '0'*64
    raw['execution.json'] = d.encoded(execution); raw['intent.json'] = d.encoded(intent)
    with pytest.raises(ValueError, match=reason): d.review_originals(raw, SOURCE)


def test_unreviewed_configuration_bytes_refused(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch)
    write(f['bundle']/'literals'/d.digest(f['new']), b'{"unreviewed":true}\n')
    with pytest.raises(ValueError, match='CONFIGURATION_NOT_ACTUALLY_REVIEWED'):
        d.verify_bundle(f['bundle'], f['root'], SOURCE)


def test_later_negative_change_review_blocks(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch)
    c.record(f['change'], 'REVIEW', f['actor'], {**f['payload'], 'verdict': 'REQUEST_CHANGES',
             'rationale': 'Synthetic later criticism.', 'affected_results': 'Do not deploy.'})
    with pytest.raises(ValueError, match='ACTIVE_CHANGE_PENDING_OR_NEGATIVE'):
        d.verify_bundle(f['bundle'], f['root'], SOURCE)


def test_changed_previous_configuration_blocks_before_install(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch); write(f['target'], b'changed old configuration')
    with pytest.raises(ValueError, match='INSTALLED_CONFIGURATION_CHANGED'):
        d.verify_bundle(f['bundle'], f['root'], SOURCE)


def test_installed_exact_bytes_and_unknown_source_refused(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch); write(f['target'], f['new'])
    assert d.verify_bundle(f['bundle'], f['root'], SOURCE, installed=True)['source'] == SOURCE
    write(f['root']/'orchestrator/unreviewed.py', b'# new executable')
    with pytest.raises(ValueError, match='INSTALLED_SOURCE_INVENTORY_CHANGED'):
        d.verify_bundle(f['bundle'], f['root'], SOURCE, installed=True)


def test_actual_unprotected_path_refused(tmp_path):
    path = tmp_path/'input'; path.write_text('synthetic')
    with pytest.raises(ValueError, match='ROOT_PROTECTED_INPUT_REQUIRED'): d.protected(path)


def test_archive_rejects_link_without_extraction():
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode='w:gz') as archive:
        item = tarfile.TarInfo('snapshot/alias'); item.type = tarfile.SYMTYPE; item.linkname = '/tmp'
        archive.addfile(item)
    with pytest.raises(ValueError, match='ARCHIVE_MEMBER_REFUSED'): d.archive_inventory(data.getvalue())


def test_historical_install_receipt_recovery_and_fixed_selection(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch)
    base = tmp_path/'deployment'; bundle = base/'bundles'/d.digest((f['bundle']/'proposal.json').read_bytes())
    bundle.parent.mkdir(parents=True); f['bundle'].rename(bundle)
    monkeypatch.setattr(d, 'BASE', base); monkeypatch.setattr(d, 'ACTIVE', base/'active.json')
    monkeypatch.setattr(d.os, 'getuid', lambda: 0)
    def save_once(folder, name, value):
        path = folder/name; raw = d.encoded(value)
        if path.exists(): assert path.read_bytes() == raw
        else: write(path, raw)
        return value
    monkeypatch.setattr(d, '_save_once', save_once)
    original_verify=d.verify_bundle; current_modes=[]
    def observed_verify(*args,**kwargs):
        current_modes.append(kwargs.get('check_current',True))
        return original_verify(*args,**kwargs)
    monkeypatch.setattr(d,'verify_bundle',observed_verify)
    # Reconstruct an existing historical pre-install original, without invoking
    # the fresh-install entrypoint that now requires V2.
    intent = save_once(bundle, 'install-intent.json', {'status': 'PREPARED_REVIEW_VERIFIED',
        **original_verify(bundle, f['root'], SOURCE, installed=False)})
    assert intent['status'] == 'PREPARED_REVIEW_VERIFIED'
    write(f['target'], f['new'])
    receipt = d.record_install(bundle, f['root'], SOURCE)
    assert d.record_install(bundle, f['root'], SOURCE) == receipt
    write(d.ACTIVE, d.encoded({'schema': d.SCHEMA, 'source': SOURCE,
          'proposal_sha256': bundle.name, 'install_receipt_sha256': d.digest((bundle/'install-receipt.json').read_bytes())}))
    assert d.verify_installed(f['root'], SOURCE, config_path=f['target'], config=json.loads(f['new']))['source'] == SOURCE
    assert current_modes and all(current_modes)
    with pytest.raises(ValueError, match='IN_MEMORY_CONFIGURATION_CHANGED'):
        d.verify_installed(f['root'], SOURCE, config_path=f['target'], config={'source': 'forged'})
    write(bundle/'install-receipt.json', d.encoded({**receipt, 'previous_source': 'c'*40}))
    with pytest.raises(ValueError, match='COMPLETED_INSTALL_RECEIPT_REQUIRED'):
        d.verify_installed(f['root'], SOURCE)


def test_missing_original_preinstall_intent_cannot_be_promoted(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch); write(f['target'], f['new'])
    monkeypatch.setattr(d.os, 'getuid', lambda: 0)
    with pytest.raises(FileNotFoundError): d.record_install(f['bundle'], f['root'], SOURCE)
    assert not (f['bundle']/'install-receipt.json').exists()


def test_recorded_approval_without_actual_provider_link_refused(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch)
    original = d.review_originals(f['raw'], SOURCE)
    original['response'] = {**original['response'], 'session_id': 'other-session'}
    proposal = json.loads((f['bundle']/'proposal.json').read_bytes())
    with pytest.raises(ValueError, match='CHANGE_ORIGINAL_CLAUDE_REVIEW_REQUIRED'):
        d.change_review(f['bundle'], proposal['changes'][0], original)


def test_application_missing_from_original_review_context_refused(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch)
    original = d.review_originals(f['raw'], SOURCE); original['changes'] = []
    proposal = json.loads((f['bundle']/'proposal.json').read_bytes())
    with pytest.raises(ValueError, match='APPLICATION_NOT_IN_ACTUAL_REVIEW'):
        d.change_review(f['bundle'], proposal['changes'][0], original)


def test_missing_continuing_component_refused(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(d, 'REQUIRED_TARGETS', {str(f['target']), '/etc/systemd/system/research-system-scientific-completion.timer'})
    with pytest.raises(ValueError, match='CONTINUING_COMPONENT_MISSING'):
        d.verify_bundle(f['bundle'], f['root'], SOURCE)


def test_changed_fixed_model_launcher_refused(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(d, 'dependency_metadata', lambda name: {'sha256': 'f'*64})
    with pytest.raises(ValueError, match='LAUNCHER_IDENTITY_CHANGED'):
        d.verify_bundle(f['bundle'], f['root'], SOURCE)


def test_running_broker_requires_actual_matching_process_cwd(tmp_path, monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setattr(d.subprocess, 'run', lambda *a, **k: SimpleNamespace(returncode=0, stdout=str(os.getpid())+'\n'))
    assert d.running_broker(Path.cwd())['main_pid'] == os.getpid()
    root = tmp_path/'different-release'; (root/'orchestrator').mkdir(parents=True)
    monkeypatch.setattr(d, '__file__', str(root/'orchestrator/deployment_review.py'))
    with pytest.raises(ValueError, match='RUNNING_BROKER_SOURCE_CHANGED'): d.running_broker(root)


def test_nonroot_cannot_claim_full_installed_verification(monkeypatch):
    monkeypatch.setattr(d.os, 'getuid', lambda: 997)
    with pytest.raises(ValueError, match='PROTECTED_BROKER_VERIFIER_REQUIRED'):
        d.verify_installed('/synthetic/source', SOURCE)


@pytest.mark.parametrize('later_verdict', [None, 'REQUEST_CHANGES'])
def test_other_active_application_cannot_remain_unapproved(tmp_path, monkeypatch, later_verdict):
    f = fixture(tmp_path, monkeypatch)
    other = c.record(f['change'], 'APPLIED', ACTOR, {'modification': 'Another active material change',
                     'checks': 'Synthetic fixture', 'result_binding': SOURCE, 'review_status': 'PENDING'})
    if later_verdict:
        c.record(f['change'], 'REVIEW', f['actor'], {**f['payload'], 'applied_event': other['identity'],
                 'verdict': later_verdict, 'affected_results': 'Do not deploy the other active change.'})
    with pytest.raises(ValueError, match='SINGLE_ACTIVE_APPLICATION_REQUIRED'):
        d.verify_bundle(f['bundle'], f['root'], SOURCE)


def test_read_allows_access_time_updates_but_keeps_modification_identity(tmp_path, monkeypatch):
    from types import SimpleNamespace
    path=tmp_path/'review';path.write_bytes(b'synthetic original')
    observed=os.fstat; count=[0]
    def atime_changes(fd):
        info=observed(fd);count[0]+=1
        values={key:getattr(info,key) for key in ('st_dev','st_ino','st_uid','st_gid','st_mode','st_size','st_mtime_ns','st_ctime_ns')}
        return SimpleNamespace(**values,st_atime_ns=info.st_atime_ns+count[0])
    monkeypatch.setattr(d,'protected',lambda p:Path(p).stat())
    monkeypatch.setattr(d.os,'fstat',atime_changes)
    assert d.read(path)==b'synthetic original'


def test_review_only_restoration_mode_still_requires_original_provider_proof(tmp_path,monkeypatch):
    f=fixture(tmp_path,monkeypatch)
    write(f['target'],b'unknown partial target; restore must reject this separately')
    with pytest.raises(ValueError,match='INSTALLED_CONFIGURATION_CHANGED'):
        d.verify_bundle(f['bundle'],f['root'],SOURCE)
    result=d.verify_bundle(f['bundle'],f['root'],SOURCE,check_current=False)
    assert result['current_state_checked'] is False
    write(f['bundle']/'protocol.jsonl',b'{}\n')
    with pytest.raises(ValueError,match='ORIGINAL_CLAUDE_PROTOCOL_REQUIRED'):
        d.verify_bundle(f['bundle'],f['root'],SOURCE,check_current=False)


def test_large_original_selected_application_receives_complete_review(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch, selected=True)
    original = d.review_originals(f['raw'], SOURCE)
    projection = original['changes'][0]['projection']
    assert projection['projection']['kind'] == 'BOUNDED_SUMMARY'
    assert projection['requests'][0]['review_status'] == 'PENDING'
    assert 'events' not in projection['requests'][0]
    assert projection['selected_applications'][0]['event']['payload']['review_status'] == 'PENDING'
    assert d.verify_bundle(f['bundle'], f['root'], SOURCE)['review_model'] == d.MODEL
    # Later criticism is never masked by the selected section or an old approval.
    c.record(f['change'], 'REVIEW', f['actor'], {**f['payload'], 'verdict': 'REQUEST_CHANGES',
             'rationale': 'Synthetic later criticism', 'affected_results': 'Hold deployment.'})
    with pytest.raises(ValueError, match='ACTIVE_CHANGE_PENDING_OR_NEGATIVE'):
        d.verify_bundle(f['bundle'], f['root'], SOURCE)


@pytest.mark.parametrize('defect', ['proposal_hash', 'selected_identity', 'payload', 'actor',
    'request_metadata', 'head', 'early_head', 'wrong_source', 'missing', 'duplicate'])
@pytest.mark.parametrize('framed', [False, True])
def test_selected_proof_tamper_refused_even_with_self_consistent_provider_fixture(tmp_path, monkeypatch, defect, framed):
    def mutate(sidecar, projection):
        row = projection['selected_applications'][0]
        if defect == 'proposal_hash': sidecar['proposal_sha256'] = 'f'*64
        elif defect == 'selected_identity': row['event']['identity'] = 'f'*64
        elif defect == 'payload': row['event']['payload']['modification'] = 'Changed actual application'
        elif defect == 'actor': row['event']['actor']['model'] = 'Changed attribution'
        elif defect == 'request_metadata': row['requested_change'] = 'Changed requested scope'
        elif defect == 'head': row['record_head_sha256'] = 'f'*64
        elif defect == 'early_head': row['record_head_sha256'] = row['request_sha256']
        elif defect == 'wrong_source': row['event']['payload']['result_binding']['source'] = PREVIOUS
        elif defect == 'missing': projection['selected_applications'] = []
        else: projection['selected_applications'].append(row)
    f = fixture(tmp_path, monkeypatch, selected=True, mutate_selection=mutate, framed=framed)
    with pytest.raises(ValueError): d.verify_bundle(f['bundle'], f['root'], SOURCE)


def test_selected_proof_cannot_hide_another_pending_application(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch, selected=True)
    c.record(f['change'], 'APPLIED', ACTOR, {'modification': 'A separate active material change',
             'checks': 'Synthetic fixture', 'result_binding': {'source': SOURCE}, 'review_status': 'PENDING'})
    with pytest.raises(ValueError, match='SINGLE_ACTIVE_APPLICATION_REQUIRED'):
        d.verify_bundle(f['bundle'], f['root'], SOURCE)


@pytest.mark.parametrize('defect', ['missing_literal', 'missing_identity'])
def test_explicit_selection_requires_actual_sidecar_literal(tmp_path, monkeypatch, defect):
    f = fixture(tmp_path, monkeypatch, selected=True)
    original = d.review_originals(f['raw'], SOURCE)
    if defect == 'missing_literal': original['private_text'].pop(original['request']['change_bindings_sha256'])
    else: original['request'].pop('change_bindings_sha256')
    with pytest.raises(ValueError):
        d.selected_review_applications(original, (f['bundle']/'proposal.json').read_bytes(), SOURCE)


@pytest.mark.parametrize('defect', [None, 'source_omission', 'literal', 'pending', 'later_negative'])
def test_framed_review_keeps_complete_bundle_gates(tmp_path, monkeypatch, defect):
    f = fixture(tmp_path, monkeypatch, selected=True, framed=True, omit_source=defect=='source_omission')
    if defect == 'literal':
        write(f['bundle']/'literals'/d.digest(f['new']), b'changed')
    elif defect == 'pending':
        c.record(f['change'], 'APPLIED', ACTOR, {'modification': 'Unreviewed follow-up',
            'checks': 'Fixture only', 'result_binding': {'source': SOURCE}, 'review_status': 'PENDING'})
    elif defect == 'later_negative':
        c.record(f['change'], 'REVIEW', f['actor'], {**f['payload'], 'verdict': 'REQUEST_CHANGES',
            'rationale': 'Synthetic later criticism', 'affected_results': 'Hold deployment.'})
    if defect:
        with pytest.raises(ValueError):
            d.verify_bundle(f['bundle'], f['root'], SOURCE)
    else:
        assert d.verify_bundle(f['bundle'], f['root'], SOURCE)['review_model'] == d.MODEL


@pytest.mark.parametrize('defect', ['absent_version', 'both_versions', 'legacy_body', 'swapped_names', 'duplicate_version'])
def test_framed_originals_reject_format_claims_and_cross_name_swaps(tmp_path, monkeypatch, defect):
    f = fixture(tmp_path, monkeypatch, framed=True)
    raw = dict(f['raw']); request = json.loads(raw['request.json'])
    if defect == 'duplicate_version':
        pass  # Inject a duplicate claim into the final serialized request below.
    elif defect == 'absent_version':
        request.pop('input_presentation')
    elif defect == 'both_versions':
        request['input_presentation'] = [presentation.FORMAT, 'legacy-json']
    elif defect == 'legacy_body':
        request['prompt'] = 'Source:\n{}'+d.SUPPLEMENT+'{}'
    else:
        sources, supplements, changes = presentation.decode(request['prompt'], request['scope'], SOURCE, None)
        first, second = 'orchestrator/example.py', 'scripts/pilot_review.py'
        sources[first], sources[second] = sources[second], sources[first]
        request['prompt'] = presentation.encode(request['scope'], SOURCE, sources, supplements, changes)
    raw['request.json'] = d.encoded(request)
    if defect == 'duplicate_version':
        raw['request.json'] = raw['request.json'].replace(b'{', b'{"input_presentation":"legacy-json",', 1)
    execution = json.loads(raw['execution.json'])
    execution.update(request_sha256=d.digest(raw['request.json']), prompt_sha256=d.digest(request['prompt'].encode()))
    raw['execution.json'] = d.encoded(execution)
    intent = json.loads(raw['intent.json']); intent['request_sha256'] = execution['request_sha256']
    raw['intent.json'] = d.encoded(intent)
    with pytest.raises(ValueError):
        d.review_originals(raw, SOURCE)


@pytest.mark.parametrize('framed', [False, True])
def test_extra_active_codex_approval_cannot_bypass_selected_claude_gate(tmp_path, monkeypatch, framed):
    f = fixture(tmp_path, monkeypatch, selected=True, framed=framed)
    other = c.record(f['change'], 'APPLIED', ACTOR, {
        'modification': 'Separate active synthetic application', 'checks': 'Offline fixture only',
        'result_binding': {'source': SOURCE}, 'review_status': 'PENDING'})
    c.record(f['change'], 'REVIEW', ACTOR, {
        'applied_event': other['identity'], 'verdict': 'APPROVE',
        'rationale': 'Synthetic same-family review, not independent provider approval.',
        'review_evidence': 'Offline fixture only'})
    with pytest.raises(ValueError, match='DEPLOYMENT_SINGLE_ACTIVE_APPLICATION_REQUIRED'):
        d.verify_bundle(f['bundle'], f['root'], SOURCE)


def component_protocol(scope, sources, context, private, changes, selection_sha, session):
    """Original-shaped synthetic fixture, explicitly not a real model receipt."""
    supplements = {str(i): {'sha256': d.digest(raw), 'content': raw.decode()} for i, raw in enumerate(private)}
    prompt = presentation.encode(scope, SOURCE, sources, supplements, changes, context)
    request = {'scope': scope, 'reviewed_commit': SOURCE, 'prompt': prompt,
        'input_presentation': presentation.FORMAT, 'shared_context_sha256': d.digest(context),
        'input_file_sha256': {name: d.digest(text.encode()) for name, text in sources.items()},
        'private_evidence_sha256': {name: value['sha256'] for name, value in supplements.items()},
        'runner_sha256': d.digest(sources['scripts/pilot_review.py'].encode()),
        'change_context_sha256': d.digest(json.dumps(changes, sort_keys=True).encode()),
        'change_bindings_sha256': selection_sha}
    response = {'type': 'result', 'subtype': 'success', 'is_error': False, 'session_id': session,
        'structured_output': {'scope': scope, 'reviewed_commit': SOURCE, 'verdict': 'APPROVE',
                              'findings': ['Synthetic complete criticism, retained verbatim.']}}
    raw = {'request.json': d.encoded(request), 'response.json': d.encoded(response)}
    return bind_component_protocol(raw)


def bind_component_protocol(raw):
    request = json.loads(raw['request.json']); response = json.loads(raw['response.json'])
    session = response['session_id']
    events = [{'type': 'system', 'subtype': 'init', 'tools': ['StructuredOutput'], 'mcp_servers': [],
               'permissionMode': 'dontAsk', 'session_id': session},
              {'type': 'assistant', 'session_id': session, 'message': {'model': d.MODEL}}, response]
    raw['protocol.jsonl'] = b''.join(d.encoded(event).replace(b'\n', b'')+b'\n' for event in events)
    execution = {'reviewed_commit': SOURCE, 'returncode': 0, 'requested_model': d.MODEL,
        'assistant_message_models': [d.MODEL], 'request_sha256': d.digest(raw['request.json']),
        'response_sha256': d.digest(raw['response.json']), 'protocol_sha256': d.digest(raw['protocol.jsonl']),
        'prompt_sha256': d.digest(request['prompt'].encode()), 'input_file_sha256': request['input_file_sha256']}
    raw.update({'execution.json': d.encoded(execution), 'intent.json': d.encoded({
        'reviewed_commit': SOURCE, 'request_sha256': execution['request_sha256'],
        'maximum_invocations': 1, 'automatic_retry': False}), 'returned.json': d.encoded({'returncode': 0})})
    return raw


def composition_fixture(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch, selected=True, framed=True)
    proposal = json.loads((f['bundle']/'proposal.json').read_bytes())
    files = d.archive_inventory((f['bundle']/'source.tar.gz').read_bytes())
    # Small synthetic bodies exercise the actual fixed profile names, without
    # copying the large implementation or weakening constants in the tests.
    for name in (d.INTEGRATION_FILES | d.PART_COMMON_FILES | d.REQUIRED_TEMPLATES) - d.REFERENCE_ONLY_FILES:
        files.setdefault(name, ('# Synthetic complete '+name+'\n').encode())
    manifest = json.loads(files['configs/scientific-operating-context.json'])
    manifest['roles'] = {'claude': 'independent reviewer'}
    files['configs/scientific-operating-context.json'] = d.encoded(manifest)
    policy = json.loads(files['configs/authority.json'])
    context = presentation.context_original({'family': 'claude', 'role': 'independent reviewer',
        'recorded_changes': {'status': 'synthetic frozen context'},
        'shared_policy': {'binding': manifest['authority_policy'], 'policy': policy,
            'direction': files['docs/direction.md'].decode(),
            'operating_context': {'manifest': manifest,
                'manifest_sha256': d.digest(files['configs/scientific-operating-context.json']),
                'documents': {'docs/direction.md': {'sha256': d.digest(files['docs/direction.md']),
                                                    'text': files['docs/direction.md'].decode()}}}}})
    refs = {name: ('# Synthetic reference only '+name+'\n').encode() for name in d.REFERENCE_ONLY_FILES}
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w:gz') as archive:
        for name, raw in files.items():
            item = tarfile.TarInfo('snapshot/'+name); item.size = len(raw)
            archive.addfile(item, io.BytesIO(raw))
    archive = write(f['bundle']/'source.tar.gz', buffer.getvalue())
    proposal.update(archive_sha256=d.digest(archive),
                    source_files={name: d.digest(raw) for name, raw in files.items()})
    required, policy_names = d.coverage_requirements(files)
    known = {**proposal['source_files'], **{name: d.digest(raw) for name, raw in refs.items()}}
    criticism = b'Synthetic preserved original criticism.\n'
    plan = {'schema': d.COVERAGE_SCHEMA, 'source': SOURCE, 'archive_sha256': d.digest(archive),
        'shared_context_sha256': d.digest(context), 'required_files': required,
        'reference_files': {name: known[name] for name in refs},
        'parts': {'a': {name: sha for name, sha in known.items() if name != 'orchestrator/example.py'},
                  'b': {name: known[name] for name in d.PART_COMMON_FILES | policy_names | {'orchestrator/example.py'}}},
        'integration': {name: known[name] for name in d.INTEGRATION_FILES | policy_names},
        'shared_evidence_sha256': [d.digest(criticism)]}
    plan_raw = write(f['bundle']/'review-plan.json', d.encoded(plan))
    proposal['review_plan_sha256'] = d.digest(plan_raw)
    proposal_raw = write(f['bundle']/'proposal.json', d.encoded(proposal))
    selection = d.encoded(c.review_bindings(SOURCE, d.digest(proposal_raw), proposal['changes']))
    changes = d.review_originals(f['raw'], SOURCE)['changes']
    private = [proposal_raw, plan_raw, selection, criticism,
               *[path.read_bytes() for path in (f['bundle']/'literals').iterdir()]]
    texts = {name: raw.decode() for name, raw in {**files, **refs}.items()}
    def make(part, *, changed_sources=None, changed_context=None, changed_changes=None, changed_private=None):
        assignment = plan['integration'] if part == 'integration' else plan['parts'][part]
        return component_protocol('material-deployment' if part == 'integration' else d.PART_SCOPES[part],
            {name: texts[name] for name in assignment} if changed_sources is None else changed_sources,
            context if changed_context is None else changed_context,
            private if changed_private is None else changed_private,
            changes if changed_changes is None else changed_changes, d.digest(selection), 'synthetic-part-'+part)
    components = {part: make(part) for part in d.PART_SCOPES}
    manifest, _, _ = d.checked_components(plan, plan_raw, proposal_raw, components)
    receipt_raw = write(f['bundle']/'component-receipts.json', d.encoded(manifest))
    private.extend([receipt_raw, *[raw['response.json'] for raw in components.values()]])
    final = make('integration')
    for part, raw in components.items():
        for name, value in raw.items(): write(f['bundle']/'component-reviews'/part/name, value)
    for name, value in final.items(): write(f['bundle']/name, value)
    execution = json.loads(final['execution.json'])
    c.record(f['change'], 'REVIEW', {**f['actor'], 'session_id': 'synthetic-part-integration'},
        {**f['payload'], 'original_review': {key: execution[key] for key in
            ('request_sha256', 'response_sha256', 'protocol_sha256')}})
    f.update(plan=plan, plan_raw=plan_raw, proposal=proposal, proposal_raw=proposal_raw, files=files,
        components=components, final=final, receipt_raw=receipt_raw, context=context, make=make,
        private=private, changes=changes, texts=texts)
    return f


def test_composed_review_requires_complete_named_source_and_final_application_outcome(tmp_path, monkeypatch):
    f = composition_fixture(tmp_path, monkeypatch)
    proof = d.verify_bundle(f['bundle'], f['root'], SOURCE)
    assert proof['component_original_sha256']['b']['request.json'] == d.digest(f['components']['b']['request.json'])
    assert proof['review_session'] == 'synthetic-part-integration'
    assert proof['unattended_activation_authority'] is False
    assert 'orchestrator/example.py' not in f['plan']['integration']
    for part in d.PART_SCOPES:
        with pytest.raises(ValueError, match='EXACT_APPROVING_REVIEW_REQUIRED'):
            d.review_originals(f['components'][part], SOURCE)


@pytest.mark.parametrize('defect', ['missing_part', 'replayed_a', 'negative', 'different_source',
    'different_context', 'different_changes', 'renamed_same_bytes', 'changed_overlap', 'missing_original'])
def test_component_original_proof_refusals(tmp_path, monkeypatch, defect):
    f = composition_fixture(tmp_path, monkeypatch)
    originals = {part: dict(raw) for part, raw in f['components'].items()}
    if defect == 'missing_part': originals.pop('b')
    elif defect == 'replayed_a': originals['b'] = originals['a']
    elif defect == 'missing_original': originals['b'].pop('intent.json')
    elif defect == 'negative':
        response = json.loads(originals['b']['response.json'])
        response['structured_output']['verdict'] = 'REQUEST_CHANGES'
        originals['b']['response.json'] = d.encoded(response)
        originals['b'] = bind_component_protocol(originals['b'])
    elif defect == 'different_source':
        response = json.loads(originals['b']['response.json'])
        response['structured_output']['reviewed_commit'] = PREVIOUS
        originals['b']['response.json'] = d.encoded(response)
        originals['b'] = bind_component_protocol(originals['b'])
    elif defect == 'different_context':
        context = json.loads(f['context']); context['recorded_changes'] = {'different': True}
        originals['b'] = f['make']('b', changed_context=presentation.context_original(context))
    elif defect == 'different_changes':
        originals['b'] = f['make']('b', changed_changes=[*f['changes'], {'newer': 'unreviewed head'}])
    else:
        sources = {name: f['texts'][name] for name in f['plan']['parts']['b']}
        if defect == 'renamed_same_bytes':
            sources['orchestrator/renamed.py'] = sources.pop('orchestrator/example.py')
        else: sources['scout.py'] += '# changed overlapping source\n'
        originals['b'] = f['make']('b', changed_sources=sources)
    with pytest.raises(ValueError):
        d.checked_components(f['plan'], f['plan_raw'], f['proposal_raw'], originals)


@pytest.mark.parametrize('defect', ['template', 'required_inventory', 'union', 'reference_profile',
    'integration_scout', 'integration_gate', 'part_scout', 'receipt_cycle'])
def test_frozen_plan_cannot_reduce_profile(tmp_path, monkeypatch, defect):
    f = composition_fixture(tmp_path, monkeypatch); plan = json.loads(f['plan_raw'])
    files = dict(f['files'])
    if defect == 'template': files.pop(sorted(d.REQUIRED_TEMPLATES)[0])
    elif defect == 'required_inventory': plan['required_files'].pop('orchestrator/example.py')
    elif defect == 'union': plan['parts']['b'].pop('orchestrator/example.py')
    elif defect == 'reference_profile': plan['reference_files'].pop(sorted(d.REFERENCE_ONLY_FILES)[0])
    elif defect == 'integration_scout': plan['integration'].pop('scout.py')
    elif defect == 'integration_gate': plan['integration'].pop('orchestrator/deployment_review.py')
    elif defect == 'part_scout': plan['parts']['b'].pop('scout.py')
    else: plan['part_request_sha256'] = 'a'*64
    with pytest.raises(ValueError):
        d.coverage_plan(d.encoded(plan), SOURCE, f['proposal']['archive_sha256'], files)


@pytest.mark.parametrize('defect', ['part_digest', 'paraphrased_findings', 'missing_manifest',
    'missing_criticism', 'different_changes', 'missing_final_scout', 'component_scope_final'])
def test_final_integration_cannot_skip_originals_or_cross_cutting_inputs(tmp_path, monkeypatch, defect):
    f = composition_fixture(tmp_path, monkeypatch)
    final = f['final']; receipt = f['receipt_raw']
    if defect == 'part_digest':
        value = json.loads(receipt); value['parts']['a']['original_sha256']['intent.json'] = 'f'*64
        receipt = d.encoded(value)
    elif defect in {'paraphrased_findings', 'missing_manifest', 'missing_criticism'}:
        omitted = {'paraphrased_findings': f['components']['a']['response.json'],
                   'missing_manifest': receipt,
                   'missing_criticism': b'Synthetic preserved original criticism.\n'}[defect]
        private = [raw for raw in f['private'] if raw != omitted]
        private.append(b'Driver paraphrase does not replace original evidence.')
        final = f['make']('integration', changed_private=private)
    elif defect == 'different_changes':
        final = f['make']('integration', changed_changes=[*f['changes'], {'changed': True}])
    elif defect == 'missing_final_scout':
        sources = {name: f['texts'][name] for name in f['plan']['integration'] if name != 'scout.py'}
        final = f['make']('integration', changed_sources=sources)
    else: final = f['components']['a']
    review = d._review_originals(final, SOURCE, {'material-deployment', d.PART_SCOPES['a']})
    with pytest.raises(ValueError):
        d.composed_review_bytes(f['proposal'], f['proposal_raw'], f['files'], review,
                                f['plan_raw'], f['components'], receipt)


@pytest.mark.parametrize('defect', ['current_negative', 'missing_target_literal'])
def test_composition_keeps_existing_live_change_and_configuration_gates(tmp_path, monkeypatch, defect):
    f = composition_fixture(tmp_path, monkeypatch)
    if defect == 'current_negative':
        c.record(f['change'], 'REVIEW', f['actor'], {**f['payload'], 'verdict': 'REQUEST_CHANGES',
            'rationale': 'Synthetic later applicable criticism.', 'affected_results': 'Do not deploy.'})
        reason = 'ACTIVE_CHANGE_PENDING_OR_NEGATIVE'
    else:
        final = f['make']('integration', changed_private=[raw for raw in f['private'] if raw != f['new']])
        for name, raw in final.items(): write(f['bundle']/name, raw)
        reason = 'CONFIGURATION_NOT_ACTUALLY_REVIEWED'
    with pytest.raises(ValueError, match=reason):
        d.verify_bundle(f['bundle'], f['root'], SOURCE)

def test_new_authority_module_cannot_be_omitted_from_archive_or_final_integration(tmp_path,monkeypatch):
    import copy
    f=composition_fixture(tmp_path,monkeypatch)
    files=dict(f['files'])
    entry='orchestrator/handover_runtime.py'
    module='orchestrator/authority_replacements.py'
    files[entry]=b'from orchestrator import authority_replacements\n'
    with pytest.raises(ValueError,match='REPLACEMENT_AUTHORITY_SOURCE_MISSING'):
        d.coverage_requirements(files)
    files[module]=b'# Complete synthetic authority replacement module.\n'
    required,policy=d.coverage_requirements(files)
    assert required[module]==d.digest(files[module])
    plan=copy.deepcopy(f['plan']);plan['required_files']=required
    for assignment in [*plan['parts'].values(),plan['integration']]:
        if entry in assignment:assignment[entry]=d.digest(files[entry])
    plan['parts']['a'][module]=d.digest(files[module])
    with pytest.raises(ValueError,match='INTEGRATION_SOURCE_REQUIRED'):
        d.coverage_plan(d.encoded(plan),SOURCE,plan['archive_sha256'],files)
    plan['integration'][module]=d.digest(files[module])
    assert d.coverage_plan(d.encoded(plan),SOURCE,plan['archive_sha256'],files)==plan
    del plan['parts']['a'][module]
    with pytest.raises(ValueError,match='COMPLETE_NAMED_COVERAGE_REQUIRED'):
        d.coverage_plan(d.encoded(plan),SOURCE,plan['archive_sha256'],files)


def test_legacy_archive_does_not_gain_a_nonexistent_replacement_requirement():
    assert d.replacement_review_files({'orchestrator/handover_runtime.py':b'# Old complete source.\n'})==set()


@pytest.mark.parametrize('framed', [False, True])
def test_new_install_rejects_valid_legacy_review_before_intent(tmp_path, monkeypatch, framed):
    f = fixture(tmp_path, monkeypatch, framed=framed)
    monkeypatch.setattr(d.os, 'getuid', lambda: 0)
    assert d.verify_bundle(f['bundle'], f['root'], SOURCE)['source'] == SOURCE
    originals = {name: (f['bundle']/name).read_bytes() for name in d.ORIGINAL_NAMES}
    with pytest.raises(ValueError, match='REVIEW_PROSPECTIVE_V2_REQUIRED'):
        d.begin_install(f['bundle'], f['root'], SOURCE)
    assert not (f['bundle']/'install-intent.json').exists()
    assert all((f['bundle']/name).read_bytes() == raw for name, raw in originals.items())
    assert d.verify_bundle(f['bundle'], f['root'], SOURCE)['source'] == SOURCE


def test_new_v2_install_validates_external_baseline_and_preserves_receipt_readback(tmp_path, monkeypatch):
    from orchestrator import inspection_bootstrap as baseline
    from test_review_policy_baseline import synthetic_proof
    f = fixture(tmp_path, monkeypatch)
    raw = dict(f['raw'])
    historical = d.review_originals(raw, SOURCE)
    proof, _, _ = synthetic_proof()
    approved = baseline.validate_policy_baseline(proof)
    request = json.loads(raw['request.json'])
    supplements = {name: {'sha256': pin, 'content': historical['private_text'][pin].decode()}
                   for name, pin in request['private_evidence_sha256'].items()}
    request.update(input_presentation=presentation.FORMAT_V2,
        policy_baseline=approved['descriptor'],
        shared_context_sha256=d.digest(approved['context_raw']))
    request['prompt'] = presentation.encode_v2(request['scope'], SOURCE,
        historical['source_text'], supplements, historical['changes'],
        approved['context_raw'], approved['descriptor'])
    raw['request.json'] = d.encoded(request)
    execution = json.loads(raw['execution.json'])
    execution.update(request_sha256=d.digest(raw['request.json']),
                     prompt_sha256=d.digest(request['prompt'].encode()),
                     policy_baseline=approved['descriptor'])
    raw['execution.json'] = d.encoded(execution)
    intent = json.loads(raw['intent.json'])
    intent['request_sha256'] = d.digest(raw['request.json'])
    raw['intent.json'] = d.encoded(intent)
    for name, body in raw.items(): write(f['bundle']/name, body)
    for name, body in proof.items(): write(f['bundle']/'policy-baseline'/name, body)
    for path in (f['bundle']/'policy-baseline').rglob('*'):
        path.chmod(0o700 if path.is_dir() else 0o600)
    (f['bundle']/'policy-baseline').chmod(0o700)
    payload = {**f['payload'], 'original_review': {key: execution[key] for key in
               ('request_sha256', 'response_sha256', 'protocol_sha256')}}
    c.record(f['change'], 'REVIEW', f['actor'], payload)
    # Emulate only the installer UID; the real baseline reader still checks
    # ownership and private modes against the actual test user's identity.
    from types import SimpleNamespace
    monkeypatch.setattr(d, 'os', SimpleNamespace(**{**vars(os), 'getuid': lambda: 0}))
    def save_once(folder, name, value):
        path = folder/name
        if path.exists(): assert path.read_bytes() == d.encoded(value)
        else: write(path, d.encoded(value))
        return value
    monkeypatch.setattr(d, '_save_once', save_once)
    intent = d.begin_install(f['bundle'], f['root'], SOURCE)
    assert intent['status'] == 'PREPARED_REVIEW_VERIFIED'
    write(f['target'], f['new'])
    receipt = d.record_install(f['bundle'], f['root'], SOURCE)
    assert receipt['status'] == 'INSTALLED_REVIEW_VERIFIED'
    # A current V2 label without its complete proof cannot start a new install.
    (f['bundle']/'policy-baseline/baseline.json').write_bytes(b'{}\n')
    with pytest.raises(ValueError):
        d.verify_bundle(f['bundle'], f['root'], SOURCE, prospective=True, check_current=False)
