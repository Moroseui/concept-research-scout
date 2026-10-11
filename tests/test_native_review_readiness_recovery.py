"""Actual ready function and preserved failed-activation transaction."""
import copy,json
from types import SimpleNamespace as NS
import pytest
from orchestrator import item4_smoke_response as helper,modal_executor
from tools import item4_diagnostic_review_runtime as review
from test_timing_author24_native_binding import held

@pytest.fixture
def ready_scope(monkeypatch,tmp_path):
    # Dependency proofs are generated fixtures; the readiness function itself is real.
    seen=[];p={'schema':helper.SNAPSHOT_SCHEMA,'delivery_recovery':True}
    driver=NS(store=NS(batch=object()),state=tmp_path,config={'run_id':'fixture'})
    value={'phase':'run_spec_review','rounds':{'run_spec_author':24,'run_spec_review':15},
        'proof':{'retained':True},'protected':'unchanged','diagnostic_native_evidence':{'receipt':'pass'}}
    monkeypatch.setattr(helper,'granted',lambda *a:seen.append('granted'))
    monkeypatch.setattr(helper,'profile',lambda p:{'field':'proof','author':24,'reviewer':16,'previous_review':15})
    monkeypatch.setattr(helper,'proof',lambda *a:{'retained':True})
    monkeypatch.setattr(helper,'fixture_audit',lambda p:True)
    monkeypatch.setattr(helper,'native_harness',lambda p:True)
    monkeypatch.setattr(helper,'fixture_correction',lambda p:True)
    monkeypatch.setattr(helper,'scoped_review',lambda p:False)
    monkeypatch.setattr(helper,'delivery_recovery',lambda p:True)
    monkeypatch.setattr(helper,'protected_keys',lambda p:['protected'])
    monkeypatch.setattr(helper,'scope',lambda *a:{'protected':'unchanged'})
    monkeypatch.setattr(helper,'review_binding',lambda *a:seen.append('review_binding'))
    monkeypatch.setattr(helper,'diagnostic',lambda p:True)
    monkeypatch.setattr(helper,'executable_candidate',lambda *a:seen.append('executable_candidate'))
    monkeypatch.setattr(helper,'_native_review_ready',None)
    monkeypatch.setattr(review,'marker',lambda accounts:{'receipt':'pass'})
    return NS(driver=driver,p=p,value=value,seen=seen)


def test_real_ready_preserves_default_refusal_then_all_other_checks(ready_scope):
    x=ready_scope
    with pytest.raises(ValueError,match='AUDIT_AUTHOR_ONLY'):helper.ready(x.driver,x.value,x.p,'a'*64)
    restore=review.attach(x.driver,helper,x.p,'a'*64)
    try:
        helper.ready(x.driver,x.value,x.p,'a'*64)
        assert x.seen[-3:]==['granted','review_binding','executable_candidate']
    finally:restore()
    with pytest.raises(ValueError,match='AUDIT_AUTHOR_ONLY'):helper.ready(x.driver,x.value,x.p,'a'*64)

@pytest.mark.parametrize('fault',['receipt','proof','pending','round','protected','stage','approval','owner','scope','verifier'])
def test_equivalent_gate_cannot_mask_other_ready_refusals(ready_scope,monkeypatch,fault):
    x=ready_scope;v=copy.deepcopy(x.value);driver=x.driver;p=x.p;approval='a'*64
    restore=review.attach(driver,helper,p,approval)
    if fault=='receipt':v['diagnostic_native_evidence']={'receipt':'changed'}
    elif fault=='proof':v['proof']={}
    elif fault=='pending':v['pending']={'id':'already-admitted'}
    elif fault=='round':v['rounds']['run_spec_review']=16
    elif fault=='protected':v['protected']='changed'
    elif fault=='stage':v['phase']='result_interpretation_author'
    elif fault=='approval':approval='b'*64
    elif fault=='owner':driver=NS(store=object(),state=x.driver.state,config=x.driver.config)
    elif fault=='scope':p={'other':True}
    else:
        def refusal(*args):raise ValueError('actual native receipt refused')
        monkeypatch.setattr(review,'marker',refusal)
    try:
        with pytest.raises(ValueError):helper.ready(driver,v,p,approval)
    finally:restore()


def original_intent(h):return modal_executor.canonical({'original_state':h.driver.store.db.execute('SELECT payload FROM manual_state').fetchone()[0],'native':h.mark})

def recovery(h):
    raw=original_intent(h)
    return {'schema':'native-review-activation-recovery/v1','state_sha256':review.sha(h.driver.store.db.execute('SELECT payload FROM manual_state').fetchone()[0].encode()),'intent_sha256':review.sha(raw),'native':h.mark}

def test_failed_activation_is_preserved_and_resumed_once(held):
    h=held;raw=original_intent(h);p=h.driver.state/'diagnostic-native24-activation.json';p.write_bytes(raw)
    result=review.activate_review(h.driver,h.helper,h.scope,h.approval,recovery=recovery(h),recovery_approval='b'*64)
    assert result['model_calls']==result['provider_calls']==0 and p.read_bytes()==raw
    assert (h.driver.state/'diagnostic-native24-recovery-intent.json').is_file()
    assert h.driver.current()['phase']=='run_spec_review'
    assert h.driver.store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==0
    with pytest.raises(ValueError):review.activate_review(h.driver,h.helper,h.scope,h.approval,recovery=recovery(h),recovery_approval='b'*64)

@pytest.mark.parametrize('fault',['intent','state-pin','native-pin','approval','existing-recovery','ready'])
def test_recovery_refusal_never_changes_original_or_ledger(held,fault):
    h=held;raw=original_intent(h);p=h.driver.state/'diagnostic-native24-activation.json';p.write_bytes(raw);f=recovery(h);approval='b'*64
    if fault=='intent':p.write_bytes(raw+b' ')
    elif fault=='state-pin':f['state_sha256']='0'*64
    elif fault=='native-pin':f['native']={}
    elif fault=='approval':approval='invalid'
    elif fault=='existing-recovery':(h.driver.state/'diagnostic-native24-recovery-intent.json').write_text('preserved')
    else:
        def refusal(*args):raise ValueError('other readiness check')
        h.helper.ready=refusal
    before=p.read_bytes();state=h.driver.current()
    with pytest.raises((ValueError,FileExistsError)):
        review.activate_review(h.driver,h.helper,h.scope,h.approval,recovery=f,recovery_approval=approval)
    assert p.read_bytes()==before and h.driver.current()==state
    assert h.driver.store.db.execute('SELECT count(*) FROM events').fetchone()[0]==0


def test_completion_connection_keeps_actual_native_and_pending_scope(ready_scope):
    x=ready_scope;restore=review.attach(x.driver,helper,x.p,'a'*64)
    value={**x.value,'phase':'MODEL_RUNNING','pending':{'stage':'run_spec_review','round':16,'id':helper.call(x.p,'review')}}
    try:
        assert helper._native_review_complete(x.driver,value,x.p,'a'*64)
        for changed in [dict(value,diagnostic_native_evidence={}),dict(value,pending={}),dict(value,phase='BLOCKED')]:
            with pytest.raises(ValueError):helper._native_review_complete(x.driver,changed,x.p,'a'*64)
    finally:restore()
    assert helper._native_review_complete is None
