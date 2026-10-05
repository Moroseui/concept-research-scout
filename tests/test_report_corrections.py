"""Report corrections retain the ordinary coordinator and original review bindings."""
import json
from pathlib import Path

import pytest

from orchestrator.operations_report import Queue, finalize


def task_state():
    return {
        'coordinator_summary': '0 queued, 0 running, 2 complete, 1 blocked',
        'coordinator_tasks_total': 3,
        'coordinator_tasks_omitted': 0,
        'coordinator_tasks': [
            {'id': 'b'*64, 'status': 'BLOCKED', 'reason': 'HISTORICAL_STAGES_INCOMPLETE_NO_RETRY'},
            {'id': 'c'*64, 'status': 'COMPLETE', 'reason': None},
            {'id': 'd'*64, 'status': 'COMPLETE', 'reason': None},
        ],
        'research_schedule': {'status': 'BLOCKED', 'requests': [
            {'task_id': 'retained-readiness', 'status': 'BLOCKED',
             'reason': 'CURRENT_INSTALLED_RESEARCH_AUTHORITY_SOURCE_REQUIRED'}]},
        'scientific_position': 'No P001 baseline result is supplied.',
    }


def test_empty_receipts_do_not_hide_coordinator_and_schedule_blocks(tmp_path):
    root = tmp_path/'reports'
    report = finalize(root, 'a'*40, '2026-09-12', [], task_state=task_state())
    body = (root/(report['id']+'.md')).read_text()
    assert 'Supplied execution receipts (0): 0 completed; 0 failed; 0 blocked' in body
    assert 'coordinator summary: 0 queued, 0 running, 2 complete, 1 blocked' in body
    assert 'research schedule: BLOCKED' in body
    assert 'scheduled request retained-readiness: BLOCKED; reason: CURRENT_INSTALLED_RESEARCH_AUTHORITY_SOURCE_REQUIRED' in body
    assert 'coordinator task '+'b'*64+': BLOCKED; reason: HISTORICAL_STAGES_INCOMPLETE_NO_RETRY' in body
    assert 'coordinator tasks total: 3' in body
    assert 'coordinator tasks omitted: 0' in body
    assert 'No named dependency was supplied;' not in body
    assert 'No P001 baseline result is supplied.' in body
    assert json.loads(next(root.glob('*.receipts.json')).read_bytes()) == []
    assert json.loads(next(root.glob('*.context.json')).read_bytes()) == task_state()


def test_missing_task_state_does_not_imply_no_other_dependencies(tmp_path):
    root = tmp_path/'reports'
    report = finalize(root, 'a'*40, '2026-09-12', [])
    body = (root/(report['id']+'.md')).read_text()
    assert 'No named dependency was supplied in the execution receipts' in body
    assert 'does not establish that other queues are unblocked' in body
    assert 'coordinator summary' not in body


def test_nested_context_is_bounded_and_discloses_omitted_rows(tmp_path):
    state = task_state()
    state['coordinator_tasks'] = [{'id': str(i), 'status': 'BLOCKED', 'reason': 'SAVED_REASON'} for i in range(25)]
    root = tmp_path/'reports'
    report = finalize(root, 'a'*40, '2026-09-12', [], task_state=state)
    body = (root/(report['id']+'.md')).read_text()
    assert body.count('- coordinator task ') == 24
    assert '1 additional coordinator task rows remain in the complete linked context' in body
    assert len(json.loads(next(root.glob('*.context.json')).read_bytes())['coordinator_tasks']) == 25


def test_linked_amendment_receives_fresh_review_delivery_and_notification(tmp_path, monkeypatch):
    import orchestrator.handover_runtime as module
    import orchestrator.report_delivery as delivery

    monkeypatch.setattr(module, 'checked_source', lambda root, pin: Path(root))
    config = {'source_root': str(tmp_path), 'source': 'a'*40,
              'controller_uid': module.os.getuid(), 'state': str(tmp_path/'state'),
              'broker_socket': str(tmp_path/'socket'), 'purpose': 'LIVE_APPROVED_HANDOVER',
              'publication': {'checkout': 'fixture-only', 'permission_sha256': 'd'*64},
              'notifications': True}
    runtime = module.Runtime(config)
    calls = []; publications = []; notifications = []; admissions = []

    def broker(socket, operation, body):
        if operation == 'admit_server':
            admissions.append(body)
            return {'status': 'ADMITTED'}
        if operation == 'flush_notifications':
            return {'status': 'EMPTY'}
        assert operation == 'notify_report'
        notifications.append(body)
        return {'status': 'SENT', 'issue': len(notifications)}

    def stage(binding, position):
        calls.append((binding['id'], position))
        return {'status': 'COMPLETE', 'answer': 'Synthetic correction route fixture '+binding['id']+' '+str(position),
                'receipt': {'actual_model': 'claude-fable-5', 'session_id': 'synthetic-'+binding['id']}}

    def publish(reports, report, *args, phase='reviewed', **kwargs):
        content = delivery.assets(reports, report, phase)
        publications.append((report, phase, set(content)))
        return {'status': 'PUBLISHED', 'source': 'e'*40}

    monkeypatch.setattr(module, 'request_broker', broker)
    monkeypatch.setattr(delivery, 'deliver', publish)
    runtime.q.handlers = {name: stage for name in ('continuation', 'review', 'disposition')}
    original = runtime.enqueue_report('2026-09-11', [], {'recorded_state': 'Original report fixture.'})
    runtime.q.submit(original)
    assert runtime.q.tick()['status'] == 'COMPLETE'
    runtime.bookkeeping(); runtime.deliver_reports(); runtime.notifications()
    original_report = json.loads((runtime.state/'tasks'/original['id']/'report.json').read_bytes())['id']
    before = {p.name: p.read_bytes() for p in (runtime.state/'reports').glob(original_report+'.*')}

    amendment = runtime.enqueue_report('2026-09-12', [], task_state(), amendment_of=original_report)
    assert amendment['id'] != original['id']
    assert amendment['kind'] == 'nightly_review'
    assert amendment['stages'] == ['continuation', 'review', 'disposition']
    folder = runtime.state/'tasks'/amendment['id']
    packet = json.loads((folder/'packet.json').read_bytes())
    assert packet['amendment_of'] == original_report
    report = json.loads((folder/'report.json').read_bytes())['id']
    assert report != original_report
    assert '('+original_report+'.md)' in (runtime.state/'reports'/(report+'.md')).read_text()
    queue = Queue(runtime.state/'reports')
    claim = queue.claim(report)
    old_receipt = json.loads(before[original_report+'.claude-review.json'])
    with pytest.raises(ValueError, match='REVIEW_BINDING_MISMATCH'):
        queue.attach(report, claim['attempt_id'], before[original_report+'.claude-review.md'].decode(), old_receipt)
    assert not (runtime.state/'reports'/(report+'.claude-review.md')).exists()

    runtime.q.submit(amendment); runtime.q.submit(amendment)
    assert runtime.q.tick()['status'] == 'COMPLETE'
    runtime.bookkeeping(); runtime.bookkeeping()
    runtime.deliver_reports(); runtime.deliver_reports()
    runtime.notifications(); runtime.notifications()
    assert calls == [(original['id'], i) for i in range(3)]+[(amendment['id'], i) for i in range(3)]
    assert len(admissions) == 2
    assert [(r, phase) for r, phase, _ in publications] == [
        (original_report, 'finalized'), (original_report, 'reviewed'), (report, 'finalized'), (report, 'reviewed')]
    assert report+'.claude-review.md' in publications[-1][2]
    assert report+'.astra-disposition.md' in publications[-1][2]
    assert [n['report'] for n in notifications] == [original_report, report]
    assert all(n['phase'] == 'reviewed' for n in notifications)
    assert queue.status(report)['status'] == 'REVIEWED'
    assert before == {p.name: p.read_bytes() for p in (runtime.state/'reports').glob(original_report+'.*')}
    assert runtime.q.tick()['status'] == 'WAITING_FOR_ELIGIBLE_WORK'
    assert len(runtime.q.status()['tasks']) == 2
    assert queue.db.execute('SELECT count(*) FROM reviews').fetchone()[0] == 2


@pytest.mark.parametrize('extra', [
    {'trigger': 'installed-research-request'},
    {'trigger': 'verified-completion'},
    {'execution_proposal': {'fixture': 'not permitted for an amendment'}},
    {'research_task_id': 'not-permitted-for-an-amendment'},
])
def test_amendment_cannot_rebind_scientific_or_execution_work(tmp_path, monkeypatch, extra):
    import orchestrator.handover_runtime as module
    monkeypatch.setattr(module, 'checked_source', lambda root, pin: Path(root))
    runtime = module.Runtime({'source_root':str(tmp_path), 'source':'a'*40,
        'controller_uid':module.os.getuid(), 'state':str(tmp_path/'state'), 'broker_socket':str(tmp_path/'socket')})
    with pytest.raises(ValueError, match='REPORT_AMENDMENT_TRIGGER_REQUIRED'):
        runtime.enqueue_report('2026-09-12', [], {}, amendment_of='b'*64, **extra)
    assert not (runtime.state/'reports').exists()
