import json
import os
from pathlib import Path
import subprocess
from concurrent.futures import ThreadPoolExecutor

import pytest

from orchestrator import change_requests as changes
from orchestrator.operations_report import finalize

AGENT = {'kind': 'agent', 'family': 'codex', 'model': 'fixture-model', 'session_id': 'synthetic-only'}
HUMAN = {'kind': 'human', 'identity': 'fixture-operator'}
REVIEWER = {'kind': 'agent', 'family': 'claude', 'model': 'fixture-reviewer', 'session_id': 'synthetic-review'}


@pytest.fixture
def case(tmp_path):
    repo = tmp_path/'repo'
    repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    subprocess.run(['git', 'config', 'user.email', 'fixture@example.invalid'], cwd=repo, check=True)
    subprocess.run(['git', 'config', 'user.name', 'Fixture'], cwd=repo, check=True)
    (repo/'code.py').write_text('original = True\n')
    subprocess.run(['git', 'add', 'code.py'], cwd=repo, check=True)
    subprocess.run(['git', 'commit', '-qm', 'Original fixture'], cwd=repo, check=True)
    store = tmp_path/'changes'
    request = changes.submit(store, repo, 'campaign:isles24-pilot:P001',
                             'Preserve original bytes and make the saved record owner-only.', AGENT,
                             files=['code.py'], key='fixture', risk='LOW_IMPACT',
                             scope_limits=['No scientific scope change'])
    folder = store/request['identity']
    return repo, store, folder, request


def authority(folder):
    return changes.record(folder, 'AUTHORIZED', AGENT,
                          {'rationale': 'Synthetic existing authority record, not real permission.',
                           'authority_reference': 'fixture-direction', 'review_policy': 'DEFERRED_LOW_IMPACT'})


def application(folder, tmp_path, name='first', *, source=None):
    evidence = tmp_path/(name+'.txt')
    evidence.write_text('Synthetic actual modification and successful focused check.\n')
    ref = changes.preserve(folder, evidence)
    return changes.record(folder, 'APPLIED', AGENT,
                          {'modification': ref, 'checks': [ref], 'result_binding': {'source_after': name,
                               **({'source': source} if source is not None else {})},
                           'review_status': 'PENDING'})


def review(folder, applied, tmp_path, verdict='APPROVE'):
    evidence = tmp_path/'review.txt'
    evidence.write_text('Synthetic review of the exact recorded application.\n')
    ref = changes.preserve(folder, evidence)
    return changes.record(folder, 'REVIEW', REVIEWER,
                          {'applied_event': applied['identity'], 'verdict': verdict,
                           'rationale': 'Synthetic opposing review; not a real model result.',
                           'review_evidence': ref, 'affected_results': ['fixture-result']})


def test_plain_submission_preserves_version_and_is_not_authority(case):
    repo, store, folder, request = case
    original = (folder/'request.json').read_bytes()
    same = changes.submit(store, repo, 'campaign:isles24-pilot:P001', request['requested_change'], AGENT,
                          files=['code.py'], key='fixture', risk='LOW_IMPACT', scope_limits=request['scope_limits'])
    assert same == request
    assert (folder/'request.json').read_bytes() == original
    assert os.stat(folder/'request.json').st_mode & 0o777 == 0o600
    assert request['request']['control'] == 'actioner'
    assert request['target']['files']['code.py'] == changes.digest((repo/'code.py').read_bytes())
    assert changes.context(store)['requests'][0]['state'] == 'SUBMITTED'
    assert changes.load(folder)['events'] == []
    (repo/'code.py').write_text('changed = True\n')
    with pytest.raises(ValueError, match='TARGET_VERSION_MISMATCH'):
        changes.submit(store, repo, 'notebook:fixture', 'Record a repair', HUMAN,
                       files=['code.py'], scope_limits=['No changed science'])


def test_applied_requires_attribution_authority_actual_evidence(case, tmp_path):
    _, _, folder, _ = case
    with pytest.raises(ValueError, match='AUTHORIZATION_RECORD_REQUIRED'):
        application(folder, tmp_path)
    with pytest.raises(ValueError, match='AGENT_PROVENANCE_REQUIRED'):
        changes.record(folder, 'AUTHORIZED', {'kind': 'agent'}, {})
    authority(folder)
    with pytest.raises(ValueError, match='MODIFICATION_CHECKS_BINDING_REQUIRED'):
        changes.record(folder, 'APPLIED', AGENT, {'review_status': 'PENDING'})
    applied = application(folder, tmp_path)
    assert applied['payload']['review_status'] == 'PENDING'


def test_later_review_does_not_approve_new_executed_version(case, tmp_path):
    _, store, folder, _ = case
    original = (folder/'request.json').read_bytes()
    authority(folder)
    first = application(folder, tmp_path)
    reviewed = review(folder, first, tmp_path)
    assert changes.context(store)['requests'][0]['review_status'] == 'APPROVE'
    second = application(folder, tmp_path, 'second')
    projection = changes.context(store)['requests'][0]
    assert projection['review_status'] == 'PENDING'
    assert projection['pending_applied_events'] == [second['identity']]
    assert reviewed['payload']['applied_event'] == first['identity']
    assert (folder/'request.json').read_bytes() == original
    assert len(changes.load(folder)['events']) == 4


def test_criticism_names_affected_results_and_reaches_roles_and_report(case, tmp_path):
    _, store, folder, _ = case
    authority(folder)
    applied = application(folder, tmp_path)
    review(folder, applied, tmp_path, 'REQUEST_CHANGES')
    state = changes.context(store)
    for role in ('driver', 'reviewer'):
        received = changes.context_text(store)
        assert 'REQUEST_CHANGES' in received and 'fixture-result' in received
    report = finalize(tmp_path/'reports', 'a'*40, '2026-09-09', [],
                      task_state={'change_requests': state, 'change_review': 'REQUEST_CHANGES for fixture-result'})
    body = (tmp_path/'reports'/(report['id']+'.md')).read_text()
    assert 'REQUEST_CHANGES for fixture-result' in body
    saved = list((tmp_path/'reports').glob('*.context.json'))
    assert json.loads(saved[0].read_text())['change_requests'] == state


def test_tampered_evidence_and_private_modes_fail_closed(case, tmp_path):
    _, _, folder, _ = case
    authority(folder)
    applied = application(folder, tmp_path)
    evidence = folder/applied['payload']['modification']['artifact']
    original = evidence.read_bytes()
    evidence.write_text('Replaced evidence')
    with pytest.raises(ValueError, match='EVIDENCE_CHANGED'):
        changes.load(folder)
    evidence.write_bytes(original)
    evidence.chmod(0o644)
    with pytest.raises(ValueError, match='PRIVATE_FILE_REQUIRED'):
        changes.load(folder)


def test_missing_event_or_cross_application_review_refused(case, tmp_path):
    _, _, folder, _ = case
    authorization = authority(folder)
    applied = application(folder, tmp_path)
    with pytest.raises(ValueError, match='REVIEW_APPLIED_EVENT_REQUIRED'):
        review(folder, {'identity': 'b'*64}, tmp_path)
    event = next((folder/'events').glob('0001-*'))
    event.rename(folder/'retained-first-event.json')
    with pytest.raises(ValueError, match='EVENT_CHAIN_INVALID'):
        changes.load(folder)


def test_concurrent_duplicate_recording_reuses_original(case):
    _, _, folder, _ = case
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(lambda _: authority(folder), range(8)))
    assert len({r['identity'] for r in records}) == 1
    assert len(changes.load(folder)['events']) == 1


def test_human_and_generic_notebook_use_same_saved_operations(case, tmp_path, monkeypatch, capsys):
    repo, store, _, _ = case
    monkeypatch.setattr('sys.argv', ['change-requests', 'submit', '--store', str(store), '--root', str(repo),
                                   '--target', 'notebook:fixture', '--request', 'Explain and repair the saved output.',
                                   '--human', 'fixture-operator', '--scope-limit', 'No execution by submission'])
    changes.main()
    record = json.loads(capsys.readouterr().out)
    assert record['submitter']['kind'] == 'human'
    assert record['request']['authority'] == 'request_only'
    assert changes.context(store, 'notebook:fixture')['requests'][0]['state'] == 'SUBMITTED'


def test_same_application_cannot_erase_criticism_with_later_approval(case, tmp_path):
    _, store, folder, _ = case
    authority(folder)
    first = application(folder, tmp_path)
    review(folder, first, tmp_path, 'REQUEST_CHANGES')
    review(folder, first, tmp_path, 'APPROVE')
    assert changes.context(store)['requests'][0]['review_status'] == 'REQUEST_CHANGES'
    second = application(folder, tmp_path, 'second')
    review(folder, second, tmp_path)
    assert changes.context(store)['requests'][0]['review_status'] == 'REQUEST_CHANGES'
    revised = changes.record(folder, 'APPLIED', AGENT, {
        **second['payload'], 'supersedes_applied_events': [first['identity'], second['identity']]})
    row = changes.context(store)['requests'][0]
    assert row['review_status'] == 'PENDING'
    assert row['pending_applied_events'] == [revised['identity']]
    review(folder, revised, tmp_path)
    row = changes.context(store)['requests'][0]
    assert row['review_status'] == 'APPROVE'
    assert any(e['payload'].get('verdict') == 'REQUEST_CHANGES' for e in row['events'])
    with pytest.raises(ValueError, match='SUPERSEDED_APPLICATION_REQUIRED'):
        changes.record(folder, 'APPLIED', AGENT, {
            **second['payload'], 'supersedes_applied_events': ['0'*64]})


def test_growing_history_keeps_criticism_and_full_private_inspection(case, tmp_path, monkeypatch, capsys):
    _, store, folder, request = case
    authority(folder)
    applied = application(folder, tmp_path)
    review(folder, applied, tmp_path, 'REQUEST_CHANGES')
    for n in range(12):
        changes.record(folder, 'DISPOSITION', AGENT, {
            'rationale': str(n)+' '+('A readable explanation. '*100),
            'affected_results': ['fixture-result']})
    original = changes.load(folder)
    projected = changes.context(store)
    assert len(changes.encoded(projected)) < 20000
    assert projected['projection']['kind'] == 'BOUNDED_SUMMARY'
    row = projected['requests'][0]
    assert row['review_status'] == 'REQUEST_CHANGES'
    assert 'fixture-result' in row['latest_criticism']['affected_results_preview']
    assert row['record_head_sha256'] == original['head_sha256']
    monkeypatch.setattr('sys.argv', ['change-requests', 'inspect', '--store', str(store),
                                   '--request-id', request['identity']])
    changes.main()
    assert json.loads(capsys.readouterr().out) == original
    assert changes.request_index(store) == [{'identity': request['identity'],
                                             'target': request['target']['task']}]


def test_large_store_reports_omitted_review_states_without_approval(case):
    _, store, _, _ = case
    row = changes.context(store)['requests'][0]
    rows = [{**row, 'identity': f'{n:064x}',
             'review_status': 'REQUEST_CHANGES' if n % 2 else 'PENDING'} for n in range(120)]
    summary = changes._bounded_context(rows)
    assert len(changes.encoded(summary)) < 20000
    meta = summary['projection']
    assert meta['omitted_requests'] > 0
    assert sum(meta['omitted_review_status_counts'].values()) == meta['omitted_requests']
    assert meta['total_requests'] == len(summary['requests']) + meta['omitted_requests']
    assert summary['requests'][0]['review_status'] == 'REQUEST_CHANGES'


def selected_application(folder, source):
    return changes.record(folder, 'APPLIED', AGENT, {
        'modification': 'Synthetic final source changes.', 'checks': 'Offline fixture.',
        'result_binding': {'source': source}, 'review_status': 'PENDING'})


def test_explicit_original_review_selection_preserves_bounded_criticism(case, tmp_path):
    repo, store, folder, request = case
    authority(folder); source = request['target']['source']
    applied = selected_application(folder, source)
    review(folder, applied, tmp_path, 'REQUEST_CHANGES')
    for n in range(12):
        changes.record(folder, 'DISPOSITION', AGENT, {'rationale': str(n)+' Original explanation. '*100,
            'affected_results': 'Synthetic affected result.'})
    before = {str(p): p.read_bytes() for p in folder.rglob('*.json')}
    generic = changes.context(store)
    selected = changes.review_context(store, [{'request': request['identity'], 'applied': applied['identity']}], source=source)
    assert generic['projection']['kind'] == 'BOUNDED_SUMMARY'
    assert len(changes.encoded(generic)) < 20000
    assert {k: selected[k] for k in generic} == generic
    assert selected['requests'][0]['review_status'] == 'REQUEST_CHANGES'
    assert selected['selected_applications'][0]['event'] == applied
    assert selected['selected_applications'][0]['event']['payload']['review_status'] == 'PENDING'
    assert {str(p): p.read_bytes() for p in folder.rglob('*.json')} == before
    # Selection presents criticism for review; it does not authorize use.
    review(folder, applied, tmp_path, 'APPROVE')
    assert changes.review_context(store, [{'request': request['identity'], 'applied': applied['identity']}],
                                  source=source)['requests'][0]['review_status'] == 'REQUEST_CHANGES'


def test_selected_application_rejects_wrong_source_supersession_and_chain_tamper(case):
    _, store, folder, request = case; authority(folder)
    source = request['target']['source']; applied = selected_application(folder, source)
    selection = [{'request': request['identity'], 'applied': applied['identity']}]
    with pytest.raises(ValueError, match='SOURCE_CHANGED'):
        changes.review_context(store, selection, source='f'*40)
    with pytest.raises(ValueError, match='ORIGINAL_SELECTED_APPLICATION_REQUIRED'):
        changes.review_context(store, [{'request': request['identity'], 'applied': 'f'*64}], source=source)
    with pytest.raises(ValueError, match='UNIQUE_REVIEW_SELECTION'):
        changes.review_context(store, selection*2, source=source)
    next_applied = changes.record(folder, 'APPLIED', AGENT, {**applied['payload'],
        'modification': 'Revised source', 'supersedes_applied_events': [applied['identity']]})
    with pytest.raises(ValueError, match='SELECTED_APPLICATION_SUPERSEDED'):
        changes.review_context(store, selection, source=source)
    path = next((folder/'events').glob('*'+next_applied['identity']+'.json'))
    path.write_bytes(path.read_bytes().replace(b'Revised source', b'Tampered source'))
    with pytest.raises(ValueError, match='EVENT_CHAIN_INVALID'):
        changes.review_context(store, [{'request': request['identity'], 'applied': next_applied['identity']}], source=source)


def test_explicit_review_selection_remains_finite(case, monkeypatch):
    _, store, folder, request = case; authority(folder)
    source = request['target']['source']; applied = selected_application(folder, source)
    selection = [{'request': request['identity'], 'applied': applied['identity']}]
    assert changes.MAX_REVIEW_SELECTIONS == 32 and changes.MAX_SELECTED_REVIEW_BYTES == 250000
    rows = [{'request': f'{n:064x}', 'applied': 'a'*64} for n in range(32)]
    assert changes.review_bindings(source, 'b'*64, rows)['changes'] == rows
    with pytest.raises(ValueError, match='BOUNDED_EXPLICIT_REVIEW_SELECTION_REQUIRED'):
        changes.review_bindings(source, 'b'*64, rows+[{'request': 'f'*64, 'applied': 'a'*64}])
    exact = changes.review_context(store, selection, source=source)
    monkeypatch.setattr(changes, 'MAX_SELECTED_REVIEW_BYTES', len(changes.encoded(exact['selected_applications']))-1)
    with pytest.raises(ValueError, match='APPLICATION_BYTES_EXCEEDED'):
        changes.review_context(store, selection, source=source)
