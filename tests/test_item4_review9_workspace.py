"""Regression: execute the real model-step/reservation path, not only context build."""
import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import Accounts
from orchestrator import item4_review8_recovery as repair,item4_review4_continuation as x
from tools import item4_scientific_revision_component as component
from test_item4_review8_recovery import mechanical,apply,fourth,third,second,setup,continuation,base_setup
from test_manual_lane import policy


def runner_driver(v):
    store,batch,c,d,f,*_=v
    invoked=[]
    class Probe(Driver):
        def model_round_number(self,value):
            return repair.model_attempt(self,value,f,'a'*64,super().model_round_number)
        def guard(self):pass
        def prepare_input(self,value,stage,work):return 'replacement9 synthetic prompt',{'workspace_files':[]}
        def save(self,value):store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
        def output_names(self,stage):return ['review.json']
        def accept_completed(self,value):return value
    p=object.__new__(Probe);p.store=store;p.state=d.state
    p.config={'run_id':c['run_id'],'source':c['source'],'branch':'astra/manual-test','policy':policy(),
        'clients':{'runtime_config_sha256':'e'*64},'review_contract':'bound-review/v1',
        'workspace_root':str(Path(f['failed_workspace']).parent)}
    assert 'execution_recovery' not in p.config
    def runner(work,stage,clients,expected):
        invoked.append(work)
        (work/'review.json').write_text('{"synthetic":true}')
        return {'synthetic_transport':True}
    p.runner=runner
    return p,invoked


def test_real_model_step_selects_nine_without_faking_accepted_eight(mechanical):
    store,batch,c,d,f,local,glob=mechanical;apply(mechanical)
    p,invoked=runner_driver(mechanical);value=x.state(store)
    assert Driver.model_round_number(p,value)==8 # exact old config/branch which caused the real refusal
    original=(Path(f['failed_workspace'])/'prompt.md').read_bytes()
    result=p._model_step(value)
    assert [w.name for w in invoked]==['run_spec_review-9']
    assert result['pending']['id']==repair.REPLACEMENT and result['pending']['round']==9
    assert result['rounds']['run_spec_review']==7 # accepted counter never falsified
    assert store.db.execute('SELECT attempt,status FROM manual_calls WHERE id=?',(repair.REPLACEMENT,)).fetchone()[:]==(9,'COMPLETE')
    assert Accounts(store).read()[1]['count']==22
    assert (Path(f['failed_workspace'])/'prompt.md').read_bytes()==original
    assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid LIMIT 21')]==local
    assert [dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid LIMIT 21')]==glob


def test_changed_model_state_refused_before_runner_or_charge(mechanical):
    store,batch,c,d,f,*_=mechanical;apply(mechanical);p,invoked=runner_driver(mechanical)
    value=x.state(store);value['rounds']['run_spec_review']=8
    with pytest.raises(ValueError,match='MODEL_STATE_CHANGED'):p._model_step(value)
    assert invoked==[] and Accounts(store).read()[1]['count']==21
    assert not Path(f['failed_workspace']).with_name('run_spec_review-9').exists()


def failed_preparation(v):
    store,batch,c,d,f,*_=v;apply(v)
    value=x.state(store);value.update(phase='BLOCKED',reason='ValueError: IMMUTABLE_ARTIFACT_CONFLICT')
    raw=json.dumps(value);store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(raw,))
    checkpoint={'schema':'item4-review9-pre-admission/v1','run_id':x.RUN,'state_sha256':x.sha(raw.encode()),
        'reason':value['reason'],'existing_grant':repair.binding(f,'a'*64)}
    return checkpoint


def test_restore_keeps_grant_and_has_no_new_allowance_or_charge(mechanical):
    store,batch,c,d,f,*_=mechanical;checkpoint=failed_preparation(mechanical)
    grant=store.db.execute('SELECT payload FROM events WHERE id=?',(repair.EVENT,)).fetchone()[0]
    result=repair.restore_pre_admission(d,f,'a'*64,'d'*64,checkpoint,d.state/'restore')
    assert result=={'status':'RESTORED_UNADMITTED_REVIEW9','model_calls':0,'new_allowance':0,'preserved_calls':21}
    assert store.db.execute('SELECT payload FROM events WHERE id=?',(repair.EVENT,)).fetchone()[0]==grant
    assert Accounts(store).read()[1]['count']==21 and repair.next_review(store,f,'a'*64)==9
    with pytest.raises(ValueError):repair.restore_pre_admission(d,f,'a'*64,'d'*64,checkpoint,d.state/'restore-again')

@pytest.mark.parametrize('fault',['state','grant','workspace','science'])
def test_restore_refuses_ambiguity_or_changed_science(mechanical,fault):
    store,batch,c,d,f,*_=mechanical;checkpoint=failed_preparation(mechanical)
    raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    if fault=='state':checkpoint['state_sha256']='f'*64
    elif fault=='grant':checkpoint['existing_grant']['review_sha256']='b'*64
    elif fault=='workspace':Path(f['failed_workspace']).with_name('run_spec_review-9').mkdir()
    else:
        v=json.loads(raw);v['spec']='changed';raw=json.dumps(v);store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(raw,));checkpoint['state_sha256']=x.sha(raw.encode())
    with pytest.raises(ValueError):repair.restore_pre_admission(d,f,'a'*64,'d'*64,checkpoint,d.state/'restore')
    assert store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw
    assert Accounts(store).read()[1]['count']==21

@pytest.mark.parametrize('field',[None,'source_sha','report_sha256','verdict','change_id'])
def test_original_grant_approval_separately_authenticated(tmp_path,monkeypatch,field):
    from orchestrator import autonomy_review as ar,manual_host_guard as hg
    v={'source_sha':component.MECHANICAL_SOURCE,'report_sha256':component.MECHANICAL_REVIEW,
       'verdict':'APPROVE','change_id':'item4-review8-turn-recovery-20261009'}
    monkeypatch.setattr(component,'RECORD',tmp_path);monkeypatch.setattr(hg,'trusted',lambda p:p)
    paths=[]
    def verify(p):paths.append(p);return v
    monkeypatch.setattr(ar,'verify_result',verify)
    if field:
        v[field]='wrong'
        with pytest.raises(ValueError):component.held_mechanical_approval()
    else:assert component.held_mechanical_approval()==component.MECHANICAL_REVIEW
    assert paths==[tmp_path/'history'/component.MECHANICAL_SOURCE/'original-review-directory']


def test_unrelated_model_numbering_unchanged():
    p=object.__new__(Driver);p.config={};value={'phase':'run_spec_review','rounds':{'run_spec_review':2}}
    assert p.model_round_number(value)==3
    p.config={'run_id':'unrelated'}
    assert repair.model_attempt(p,value,{},'unused',p.model_round_number)==3
