"""Bounded response after genuine review9; real accounting, synthetic reviews."""
import json
import pytest
from orchestrator import item4_review4_continuation as x,item4_scoped_calls as scoped
from orchestrator import author_revision_accounting as a,manual_recovery as recovery
from orchestrator import autonomy_limits as limits,analysis_revisions as ar
from orchestrator.manual_executor import ManualExecutor,Accounts
from orchestrator.autonomy_accounting import BatchAccounts
from test_item4_review8_recovery import mechanical,apply,fourth,third,setup,second,continuation,activate,base_setup
from test_author_revision_accounting import review,reserve
from test_manual_lane import policy

@pytest.fixture
def fifth(request,monkeypatch):
    saved=[(obj,key,getattr(obj,key)) for obj,key in [(limits,k) for k in ('local_limit','global_limit','allowance','cap_authority')]+[(ManualExecutor,'reserve_call'),(BatchAccounts,'reserve_scientific'),(recovery,'role_limit')]]
    fixture=request.getfixturevalue('mechanical');store,batch,c,d,mechanic,*_=fixture
    fourth_grant=request.getfixturevalue('fourth')[4]
    apply(fixture);work,value=review(store,c,9)
    value.update(phase='BLOCKED',reason='UNRESOLVED_AFTER_THREE_REVISIONS',rounds={'run_spec_author':13,'run_spec_review':9})
    raw=json.dumps(value);store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(raw,))
    local=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    globalrows=[dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid')]
    assert len(local)==len(globalrows)==22
    frozen={**fourth_grant,'author_attempt':14,'review_attempt':10,'state_sha256':x.sha(raw.encode()),
        'local_calls':{r['id']:x.sha(x.canonical(r)) for r in local},
        'global_calls':{r['id']:x.sha(x.canonical(r)) for r in globalrows},
        'review_call_id':local[-1]['id'],'review_sha256':x.sha((work/'review.json').read_bytes())}
    for obj,key,original in saved:monkeypatch.setattr(obj,key,original)
    monkeypatch.setattr(scoped,'_validate',None)
    x.connect(a,recovery,frozen,'9'*64)
    scoped.connect(fourth_grant,'b'*64,mechanical=mechanic,mechanical_approval='a'*64,response=frozen,response_approval='9'*64)
    assert limits.local_limit(store,c['run_id'],policy())==24
    x.activate(d,frozen,'9'*64,d.state/'fifth')
    return store,batch,c,d,frozen,local,globalrows

def accepted(v):
    store,batch,c,d,f,*_=v
    ident,n,receipt=reserve(store,c);assert n==14
    assert receipt['batch_accounting']['run_limit']==26
    assert receipt['accounting']['limit_amendment']['review_sha256']=='9'*64
    assert receipt[a.FIELD]['review_round']==9
    assert receipt[a.FIELD]['review_call_id']==f['review_call_id']
    receipt['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,receipt,'COMPLETE')
    a.accepted(d,{'id':ident,'stage':'run_spec_author','round':14})
    value=x.state(store);value.update(phase='run_spec_review',rounds={'run_spec_author':14,'run_spec_review':9},reason=None)
    store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
    return receipt

def test_fixed_pair_preserves_all22_and_genuine_revise_stops(fifth):
    store,batch,c,d,f,local,globalrows=fifth
    accepted(fifth);review(store,c,10)
    assert Accounts(store).read()[1]['count']==24
    decision={'verdict':'REVISE','findings':[{'category':'code/spec mismatch'}]}
    assert x.terminal_transition(ar.review_transition,d,decision,'run_spec_review',10,f,'9'*64)==('BLOCKED','UNRESOLVED_AFTER_THREE_REVISIONS')
    assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid LIMIT 22')]==local
    assert [dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid LIMIT 22')]==globalrows
    with pytest.raises(ValueError):reserve(store,c)

def test_exact26_never27_and_interpretation_uses_real_collection_gate(fifth,monkeypatch):
    from orchestrator import experiment_collection
    store,batch,c,d,f,local,globalrows=fifth
    accepted(fifth);review(store,c,10,verdict='APPROVE')
    checked=[];monkeypatch.setattr(experiment_collection,'verified',lambda driver,value:checked.append(value['phase']))
    rounds={'run_spec_author':14,'run_spec_review':10}
    for stage in ('result_interpretation_author','result_interpretation_review'):
        value=x.state(store);value.update(phase=stage,reason=None,rounds=dict(rounds))
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
        ident,n,receipt=store.reserve_call(c['run_id'],stage,c['source'],'astra/manual-test',policy(),{})
        assert n==1;receipt['output_sha256']={'interpretation.md':'f'*64};store.finish_call(ident,receipt,'COMPLETE');rounds[stage]=1
        if stage.endswith('author'):a.accepted(d,{'id':ident,'stage':stage,'round':1})
    account=Accounts(store).read()[1]
    assert account['count']==26 and account['halted'] and account['resets']==[]
    assert len(checked)==4
    for stage in ('run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review'):
        with pytest.raises(ValueError):store.reserve_call(c['run_id'],stage,c['source'],'astra/manual-test',policy(),{})
    assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid LIMIT 22')]==local
    assert [dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid LIMIT 22')]==globalrows

def test_no_early_interpretation_or_unvalidated_execution(fifth):
    store,batch,c,d,f,*_=fifth
    with pytest.raises(ValueError):store.reserve_call(c['run_id'],'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
    accepted(fifth);review(store,c,10,verdict='APPROVE')
    value=x.state(store);value.update(phase='result_interpretation_author',rounds={'run_spec_author':14,'run_spec_review':10})
    store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
    with pytest.raises((ValueError,KeyError,FileNotFoundError)):
        store.reserve_call(c['run_id'],'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
    assert Accounts(store).read()[1]['count']==24

@pytest.mark.parametrize('fault',['local','global','grant','state','round','failed','uncertain','duplicate','direct-global'])
def test_mutation_or_unresolved_attempt_never_adds_charge(fifth,fault):
    store,batch,c,d,f,*_=fifth;expected=22
    if fault=='local':store.db.execute("UPDATE manual_calls SET receipt='{}' WHERE id=?",(f['review_call_id'],))
    elif fault=='global':batch.db.execute("UPDATE autonomy_calls SET receipt='{}' WHERE id=?",(f['review_call_id'],))
    elif fault=='grant':store.db.execute('DELETE FROM events WHERE id=?',(x.reason(f),))
    elif fault in ('state','round'):
        value=x.state(store)
        if fault=='state':value['phase']='BLOCKED'
        else:value['rounds']['run_spec_review']=8
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
    elif fault=='direct-global':
        with pytest.raises(ValueError):batch.reserve_scientific('f'*64,c['run_id'],'run_spec_author',c['source'],{})
        return
    else:
        ident,n,receipt=reserve(store,c);expected=23
        if fault!='duplicate':store.finish_call(ident,receipt,'FAILED' if fault=='failed' else 'UNCERTAIN')
    with pytest.raises(ValueError):reserve(store,c)
    assert Accounts(store).read()[1]['count']==expected

@pytest.mark.parametrize('kind',['day','batch','account-halt','batch-halt'])
def test_existing_caps_and_stops_unchanged(fifth,kind):
    from datetime import datetime,timezone
    from test_scoped_revisions_limits import seed
    store,batch,c,d,f,*_=fifth
    if kind=='day':seed(batch,28,kind='implementation_review',day=datetime.now(timezone.utc).date().isoformat())
    elif kind=='batch':seed(batch,38)
    elif kind=='batch-halt':(batch.folder/'HALT').write_text('synthetic stop')
    else:
        version,value=Accounts(store).read();value['halted']=True;assert Accounts(store).cas(version,value)
    with pytest.raises(ValueError):reserve(store,c)
    assert Accounts(store).read()[1]['count']==22
