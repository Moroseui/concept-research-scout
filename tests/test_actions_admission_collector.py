"""No model/writer launch; failed and duplicate transport reuse shared CAS."""
from contextlib import nullcontext
import pytest
from orchestrator.actions_admission_collector import reconcile


class FixtureBroker:
    def __init__(self):self.events={};self.calls=0
    def authentication(self):return nullcontext()
    def actions_admission(self,record,verified):
        assert record==verified
        self.calls+=1
        key=record['run_id']
        duplicate=key in self.events
        self.events[key]=record
        return {'status':'ADMITTED','duplicate_admission':duplicate,'count':len(self.events)}


def test_failed_request_yields_to_independent_and_repeated_success_is_not_recharged(tmp_path):
    broker=FixtureBroker();seen=[]
    def fetch(expected,token):
        seen.append(expected['run_id'])
        if expected['run_id']=='1':raise ValueError('fixture API unavailable')
        return expected
    requests=[{'run_id':'1'},{'run_id':'2'}]
    first=reconcile(broker,requests,tmp_path/'state',fetch=fetch)
    assert [r['outcome']['status'] for r in first]==['BLOCKED','ADMITTED']
    second=reconcile(broker,requests,tmp_path/'state',fetch=fetch)
    assert first==second and broker.calls==1
    assert seen==['1','2','1']


def test_lost_local_receipt_recovers_via_shared_admission_identity(tmp_path,monkeypatch):
    import orchestrator.actions_admission_collector as module
    broker=FixtureBroker();original=module.immutable
    def fail_once(path,raw):
        if len(path.stem)==64:raise OSError('fixture local failure')
        original(path,raw)
    monkeypatch.setattr(module,'immutable',fail_once)
    requests=[{'run_id':'1'}];fetch=lambda expected,token:expected
    assert reconcile(broker,requests,tmp_path/'state',fetch=fetch)[0]['outcome']['status']=='BLOCKED'
    monkeypatch.setattr(module,'immutable',original)
    recovered=reconcile(broker,requests,tmp_path/'state',fetch=fetch)[0]['outcome']
    assert recovered['status']=='ADMITTED' and recovered['duplicate_admission']
    assert recovered['count']==1


def test_bounded_manifest_refuses_before_access(tmp_path):
    with pytest.raises(ValueError,match='BOUNDED_PROTECTED'):
        reconcile(None,[{}]*17,tmp_path/'state')


def test_failed_network_reads_have_persistent_retry_cap(tmp_path):
    calls=[]
    def unavailable(*args):
        calls.append(1);raise OSError('fixture network unavailable')
    broker=FixtureBroker()
    for _ in range(6):
        outcome=reconcile(broker,[{'run_id':'1'}],tmp_path/'state',fetch=unavailable)
    assert len(calls)==3 and broker.calls==0
    assert outcome[0]['outcome']['reason']=='ACTIONS_ADMISSION_READ_RETRY_LIMIT'
