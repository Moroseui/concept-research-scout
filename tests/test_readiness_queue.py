import json
from pathlib import Path
import subprocess
from unittest.mock import patch
from orchestrator.readiness_queue import ReadinessQueue,run


def binding(handler='context_inventory',thread='adjacent',dependencies=None,gates=None):
    return dict(source='a'*40,thread=thread,handler=handler,dependencies=dependencies or [],gates=gates or [],seconds=1,parent='prediction-charter')


def test_overlap_restart_and_duplicate(tmp_path):
    root=tmp_path/'root';root.mkdir();state=tmp_path/'state';state.mkdir()
    q=ReadinessQueue(state/'readiness.sqlite')
    q.add('a-slow',binding('slow_synthetic','primary'))
    q.add('b-context',binding())
    q.add('c-baseline',binding('baseline_inventory',dependencies=['b-context']))
    q.add('d-patient-gated',binding(gates=['patient_launch']))
    q.db.close()
    with patch('orchestrator.readiness_queue.checked_source',return_value=root):
        r=run(root,'a'*40,state)
        repeat=run(root,'a'*40,state)
    assert r==repeat and r['processed_events']==3
    slow=json.loads((state/'a-slow/result.json').read_text())
    useful=json.loads((state/'c-baseline/result.json').read_text())
    assert slow['started'] < useful['finished'] < slow['finished']
    assert [x['job'] for x in r['inbox'] if x['status']=='OPEN']==['d-patient-gated']


def test_uncertain_attempt_is_not_retried(tmp_path):
    q=ReadinessQueue(tmp_path/'readiness.sqlite');q.add('uncertain',binding());q.claim('uncertain');q.db.close()
    with patch('orchestrator.readiness_queue.checked_source',return_value=tmp_path):r=run(tmp_path,'a'*40,tmp_path)
    assert r['processed_events']==0 and r['jobs'][0]['status']=='BLOCKED'
    assert not (tmp_path/'uncertain').exists()


def test_binding_and_handler_rejected(tmp_path):
    import pytest
    q=ReadinessQueue(tmp_path/'state.sqlite');q.add('same',binding())
    with pytest.raises(ValueError):q.add('same',binding('baseline_inventory'))
    with pytest.raises(ValueError):q.add('shell',binding('arbitrary_shell'))


def test_crash_before_claim_yields_to_independent_work(tmp_path):
    q=ReadinessQueue(tmp_path/'readiness.sqlite');q.add('crashed',binding());q.add('independent',binding());q.db.close()
    (tmp_path/'crashed').mkdir(mode=0o700)
    with patch('orchestrator.readiness_queue.checked_source',return_value=tmp_path):r=run(tmp_path,'a'*40,tmp_path)
    assert dict((x['id'],x['status']) for x in r['jobs'])=={'crashed':'BLOCKED','independent':'COMPLETE'}
