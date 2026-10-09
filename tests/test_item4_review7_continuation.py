"""Fourth continuation: real reservation engines, synthetic receipts, no providers."""
import json
import pytest
from orchestrator import item4_review4_continuation as x, item4_scoped_calls as scoped
from orchestrator import author_revision_accounting as a, manual_recovery as recovery
from orchestrator import autonomy_limits as limits, dispatch_limiter, analysis_revisions as ar
from orchestrator.manual_executor import ManualExecutor, Accounts
from orchestrator.autonomy_accounting import BatchAccounts
from test_author_revision_accounting import review, reserve, setup as base_setup
from test_item4_review4_continuation import continuation, activate
from test_item4_review5_continuation import setup, second
from test_item4_review6_continuation import third
from test_manual_lane import policy

@pytest.fixture
def fourth(third,monkeypatch):
    store,batch,c,d,old,*_=third
    x.activate(d,old,'c'*64,d.state/'third')
    ident,n,r=reserve(store,c);assert n==12
    r['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,r,'COMPLETE')
    a.accepted(d,{'id':ident,'stage':'run_spec_author','round':12})
    v=x.state(store);v.update(phase='run_spec_review',rounds={'run_spec_author':12,'run_spec_review':6})
    store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(v),))
    work,v=review(store,c,7)
    v.update(phase='BLOCKED',reason='UNRESOLVED_AFTER_THREE_REVISIONS',rounds={'run_spec_author':12,'run_spec_review':7})
    raw=json.dumps(v);store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(raw,))
    local=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    glob=[dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid')]
    frozen={**old,'author_attempt':13,'review_attempt':8,'state_sha256':x.sha(raw.encode()),
        'local_calls':{r['id']:x.sha(x.canonical(r)) for r in local},
        'global_calls':{r['id']:x.sha(x.canonical(r)) for r in glob},
        'review_call_id':local[-1]['id'],'review_sha256':x.sha((work/'review.json').read_bytes())}
    # Disk checkpoint keys may be sorted; row order is independently checked.
    frozen=json.loads(json.dumps(frozen,sort_keys=True))
    for obj,key in [(limits,k) for k in ('local_limit','global_limit','allowance','cap_authority')]+[
        (ManualExecutor,'reserve_call'),(BatchAccounts,'reserve_scientific'),(scoped,'_validate')]:
        monkeypatch.setattr(obj,key,getattr(obj,key))
    x.connect(a,recovery,frozen,'b'*64);scoped.connect(frozen,'b'*64)
    x.activate(d,frozen,'b'*64,d.state/'fourth')
    return store,batch,c,d,frozen,local,glob

def accept_author(v):
    store,batch,c,d,f,*_=v
    ident,n,r=reserve(store,c);assert n==13
    r['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,r,'COMPLETE')
    a.accepted(d,{'id':ident,'stage':'run_spec_author','round':13})
    state=x.state(store);state.update(phase='run_spec_review',rounds={'run_spec_author':13,'run_spec_review':7})
    store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(state),))
    return r

def test_fourth_pair_charged_and_genuine_revise_still_stops(fourth):
    store,batch,c,d,f,local,glob=fourth
    r=accept_author(fourth)
    assert r[a.FIELD]['continuation_review_sha256']=='b'*64
    for review_no,author,pin in [(4,10,'e'),(5,11,'d'),(6,12,'c')]:
        assert a.review_binding(d,'run_spec_author',review_no,author)['continuation_review_sha256']==pin*64
    review(store,c,8)
    assert Accounts(store).read()[1]['count']==21 and not Accounts(store).read()[1]['halted']
    assert x.terminal_transition(ar.review_transition,d,{'verdict':'REVISE','findings':[{'category':'metric/statistic'}]},'run_spec_review',8,f,'b'*64)==('BLOCKED','UNRESOLVED_AFTER_THREE_REVISIONS')
    assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid LIMIT 19')]==local
    assert [dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid LIMIT 19')]==glob
    with pytest.raises(ValueError):reserve(store,c)


def test_exact_twenty_three_and_never_twenty_four(fourth,monkeypatch):
    from orchestrator import experiment_collection
    store,batch,c,d,f,local,glob=fourth
    accept_author(fourth);review(store,c,8,verdict='APPROVE')
    checks=[]
    def verified(driver,value):
        assert driver.context==d.state.parent and str(driver.root)==c['root']
        checks.append(value['phase'])
    monkeypatch.setattr(experiment_collection,'verified',verified)
    rounds={'run_spec_author':13,'run_spec_review':8}
    for stage in ('result_interpretation_author','result_interpretation_review'):
        value=x.state(store);value.update(phase=stage,reason=None,rounds=dict(rounds))
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
        ident,n,r=store.reserve_call(c['run_id'],stage,c['source'],'astra/manual-test',policy(),{})
        assert n==1;r['output_sha256']={'interpretation.md':'f'*64};store.finish_call(ident,r,'COMPLETE');rounds[stage]=1
        if stage.endswith('author'):a.accepted(d,{'id':ident,'stage':stage,'round':1})
        if stage.endswith('author'):assert Accounts(store).read()[1]['count']==22 and not Accounts(store).read()[1]['halted']
    state=Accounts(store).read()[1]
    assert state['count']==23 and state['halted'] and state['resets']==[]
    assert r['accounting']['notification']=='CAP'
    assert len(checks)==4 # Each interpretation rechecked at local and global reservation.
    for stage in ('run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review'):
        with pytest.raises(ValueError):store.reserve_call(c['run_id'],stage,c['source'],'astra/manual-test',policy(),{})
    assert store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==23
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==23
    assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid LIMIT 19')]==local
    assert [dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid LIMIT 19')]==glob


def test_interpretation_requires_actual_complete_collection(fourth):
    store,batch,c,d,*_=fourth
    accept_author(fourth);review(store,c,8,verdict='APPROVE')
    value=x.state(store);value.update(phase='result_interpretation_author',reason=None,rounds={'run_spec_author':13,'run_spec_review':8})
    store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
    with pytest.raises((ValueError,KeyError,FileNotFoundError)):
        store.reserve_call(c['run_id'],'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
    assert Accounts(store).read()[1]['count']==21

@pytest.mark.parametrize('fault',['grant','local','global','state','round','extra-stage','direct-global','forged-amendment','failed','uncertain','duplicate'])
def test_changed_or_unbound_request_fails_without_new_charge(fourth,fault):
    store,batch,c,d,f,*_=fourth
    expected=19
    if fault=='grant':store.db.execute('DELETE FROM events WHERE id=?',(x.reason(f),))
    elif fault=='local':store.db.execute("UPDATE manual_calls SET receipt='{}' WHERE id=?",(next(iter(f['local_calls'])),))
    elif fault=='global':batch.db.execute("UPDATE autonomy_calls SET receipt='{}' WHERE id=?",(next(iter(f['global_calls'])),))
    elif fault in ('state','round'):
        value=x.state(store)
        if fault=='state':value['phase']='BLOCKED'
        else:value['rounds']['run_spec_author']=13
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
    elif fault=='extra-stage':
        with pytest.raises(ValueError):store.reserve_call(c['run_id'],'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
        return
    elif fault=='direct-global':
        with pytest.raises(ValueError):batch.reserve_scientific('f'*64,c['run_id'],'run_spec_author',c['source'],{})
        return
    elif fault=='forged-amendment':
        with pytest.raises(ValueError):dispatch_limiter.admit_manual(Accounts(store),policy(),
            {'run_id':'f'*64,'attempt':'1','source':c['source'],'branch':'astra/manual-test'},
            allowance={'run_limit':23})
        return
    elif fault in ('failed','uncertain','duplicate'):
        ident,n,r=reserve(store,c);expected=20
        if fault!='duplicate':store.finish_call(ident,r,'FAILED' if fault=='failed' else 'UNCERTAIN')
    with pytest.raises(ValueError):reserve(store,c)
    assert Accounts(store).read()[1]['count']==expected

@pytest.mark.parametrize('kind',['day','batch','account-halt','batch-halt'])
def test_other_limits_unchanged(fourth,kind):
    from datetime import datetime,timezone
    from test_scoped_revisions_limits import seed
    store,batch,c,d,f,*_=fourth
    if kind=='day':seed(batch,31,kind='implementation_review',day=datetime.now(timezone.utc).date().isoformat());expected='AUTONOMY_DAILY_CALL_LIMIT'
    elif kind=='batch':seed(batch,41);expected='AUTONOMY_BATCH_CALL_LIMIT'
    elif kind=='batch-halt':(batch.folder/'HALT').write_text('synthetic stop');expected='AUTONOMY_BATCH_HALTED'
    else:
        version,value=Accounts(store).read();value['halted']=True;assert Accounts(store).cas(version,value);expected='LOCAL_ALLOWANCE_HALTED'
    with pytest.raises(ValueError,match=expected):reserve(store,c)
    assert Accounts(store).read()[1]['count']==19


def test_unrelated_run_retains_twenty_and_wrong_source_is_refused(fourth,tmp_path):
    from test_scoped_revisions_limits import configured
    store,batch,c,d,*_=fourth
    (tmp_path/'unrelated').mkdir(mode=0o700)
    other,other_batch,config=configured(tmp_path/'unrelated',item=4,backend='modal')
    try:
        assert limits.local_limit(other,'synthetic',policy())==20
        assert limits.global_limit(other_batch,'synthetic')==20
        with pytest.raises(ValueError,match='ITEM4_SCOPED_CALL_SOURCE'):
            store.reserve_call(c['run_id'],'run_spec_author','b'*40,'astra/manual-test',policy(),{})
        assert Accounts(store).read()[1]['count']==19
    finally:other.db.close();other_batch.db.close()
