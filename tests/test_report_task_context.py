"""A human report shows its bound pending work without inventing execution."""
from orchestrator.operations_report import finalize


def test_empty_execution_period_keeps_pending_task_visible(tmp_path):
    state={'next_task':'Recover the original disposition without model replay',
           'research_queue':'Prediction charter; result reconciliation; evidence propagation'}
    result=finalize(tmp_path,'a'*40,'2026-09-07',[],task_state=state)
    body=(tmp_path/(result['id']+'.md')).read_text()
    assert 'No execution receipts were supplied' in body
    assert 'does not establish an empty task queue' in body
    assert state['next_task'] in body and state['research_queue'] in body
    assert 'Execution receipt sources: .' not in body
    assert '| Job |' not in body
    assert len(list(tmp_path.glob('*.context.json')))==1
    assert finalize(tmp_path,'a'*40,'2026-09-07',[],task_state=state)['id']==result['id']


def test_steering_changes_report_binding_without_mutating_original(tmp_path):
    first=finalize(tmp_path,'a'*40,'2026-09-07',[],task_state={'next_task':'first'})
    path=tmp_path/(first['id']+'.md');before=path.read_bytes()
    second=finalize(tmp_path,'a'*40,'2026-09-07',[],task_state={'next_task':'second'},amendment_of=first['id'])
    assert first['id']!=second['id'] and path.read_bytes()==before
