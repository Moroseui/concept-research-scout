"""Native synthetic review receipts and real local/global admission; no paid calls."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import item4_review4_continuation as x, author_revision_accounting as a
from orchestrator import manual_recovery as recovery, private_records as pr, analysis_revisions as ar
from orchestrator.manual_executor import Accounts
from test_author_revision_accounting import review, reserve, setup
from test_scoped_revisions_limits import seed

@pytest.fixture
def continuation(setup,monkeypatch):
    store,batch,c=setup
    monkeypatch.setattr(x,'RUN',c['run_id'])
    driver=SimpleNamespace(store=store,config=c,state=Path(store.path).parent)
    for _ in range(9):
        ident,n,r=reserve(store,c);r['output_sha256']={'SPEC.proposed.md':'f'*64}
        store.finish_call(ident,r,'COMPLETE')
        a.accepted(driver,{'id':ident,'stage':'run_spec_author','round':n})
    for n in range(1,5):work,value=review(store,c,n)
    value.update(phase='BLOCKED',reason='UNRESOLVED_AFTER_THREE_REVISIONS',
        rounds={'run_spec_author':9,'run_spec_review':4},interventions=[])
    raw=json.dumps(value);store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(raw,))
    local=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    glob=[dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid')]
    frozen={'run_id':c['run_id'],'authority_sha256':x.AUTHORITY,'author_attempt':10,'review_attempt':5,
        'state_sha256':x.sha(raw.encode()),'configuration_sha256':x.sha((driver.state/'lane.json').read_bytes()),
        'local_calls':{r['id']:x.sha(x.canonical(r)) for r in local},
        'global_calls':{r['id']:x.sha(x.canonical(r)) for r in glob},
        'review_call_id':local[-1]['id'],'review_sha256':x.sha((work/'review.json').read_bytes())}
    # Restore each process-local wrapper at fixture teardown.
    for obj,key in [(a,'inspect'),(a,'review_binding'),(recovery,'role_limit')]:monkeypatch.setattr(obj,key,getattr(obj,key))
    x.connect(a,recovery,frozen,'e'*64)
    return store,batch,c,driver,frozen,local,glob


def activate(v):
    store,batch,c,d,f,*_=v
    return x.activate(d,f,'e'*64,d.state/'continuation')


def test_one_author_and_one_review_are_normally_charged_without_rewriting_history(continuation):
    store,batch,c,d,f,local,glob=continuation
    assert activate(continuation)['model_calls']==0
    assert Accounts(store).read()[1]['count']==13
    ident,n,r=reserve(store,c)
    assert n==10 and r[a.FIELD]['review_round']==4 and r[a.FIELD]['continuation_review_sha256']=='e'*64
    r['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,r,'COMPLETE')
    a.accepted(d,{'id':ident,'stage':'run_spec_author','round':10})
    value=x.state(store);value.update(phase='run_spec_review',rounds={'run_spec_author':10,'run_spec_review':4})
    store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
    assert recovery.role_limit(store,c['run_id'],'run_spec_review')==5
    work,_=review(store,c,5)
    assert Accounts(store).read()[1]['count']==15
    assert x.terminal_transition(ar.review_transition,d,{'verdict':'REVISE','findings':[{'category':'metric/statistic'}]},'run_spec_review',5,f,'e'*64)==('BLOCKED','UNRESOLVED_AFTER_THREE_REVISIONS')
    assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid LIMIT 13')]==local
    assert [dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid LIMIT 13')]==glob
    assert recovery.role_limit(store,c['run_id'],'run_spec_review')==4
    with pytest.raises(ValueError):activate(continuation)


@pytest.mark.parametrize('fault',['state','config','local-charge','global-charge','native-review','native-console','running','authority'])
def test_changed_checkpoint_native_proof_or_authority_refuses_without_admission(continuation,fault):
    store,batch,c,d,f,local,glob=continuation
    if fault=='state':store.db.execute("UPDATE manual_state SET payload=payload || ' '")
    elif fault=='config':(d.state/'lane.json').write_bytes((d.state/'lane.json').read_bytes()+b' ')
    elif fault=='local-charge':store.db.execute("UPDATE manual_calls SET receipt='{}' WHERE id=?",(local[0]['id'],))
    elif fault=='global-charge':batch.db.execute("UPDATE autonomy_calls SET receipt='{}' WHERE id=?",(glob[0]['id'],))
    elif fault.startswith('native-'):
        p=Path(json.loads(local[-1]['receipt'])['workspace'])/('review.json' if fault=='native-review' else 'console.log')
        p.chmod(0o600);p.write_bytes(p.read_bytes()+b' ')
    elif fault=='running':seed(batch,1);batch.db.execute("UPDATE autonomy_calls SET status='RUNNING' WHERE id='seed-0'")
    else:f['authority_sha256']='f'*64
    with pytest.raises(ValueError):activate(continuation)
    assert Accounts(store).read()[1]['count']==13
    assert not store.db.execute('SELECT 1 FROM events WHERE id=?',(x.REASON,)).fetchone()


@pytest.mark.parametrize('fault',['missing-grant','changed-grant','original-after-activation','second-author','unaccepted-author','wrong-author-receipt'])
def test_grant_is_bound_and_cannot_be_reused_or_skip_author_validation(continuation,fault):
    store,batch,c,d,f,*_=continuation;activate(continuation)
    if fault=='missing-grant':store.db.execute('DELETE FROM events WHERE id=?',(x.REASON,))
    elif fault=='changed-grant':store.db.execute("UPDATE events SET payload='{}' WHERE id=?",(x.REASON,))
    elif fault=='original-after-activation':store.db.execute("UPDATE manual_calls SET receipt='{}' WHERE id=?",(next(iter(f['local_calls'])),))
    else:
        ident,n,r=reserve(store,c);r['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,r,'COMPLETE')
        if fault=='wrong-author-receipt':
            a.accepted(d,{'id':ident,'stage':'run_spec_author','round':10})
            r[a.FIELD]['continuation_review_sha256']='a'*64;store.db.execute('UPDATE manual_calls SET receipt=? WHERE id=?',(json.dumps(r),ident))
        if fault in ('unaccepted-author','wrong-author-receipt'):
            value=x.state(store);value.update(phase='run_spec_review',rounds={'run_spec_author':10,'run_spec_review':4})
            store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
            with pytest.raises(ValueError):recovery.role_limit(store,c['run_id'],'run_spec_review')
            return
    with pytest.raises(ValueError):reserve(store,c)


@pytest.mark.parametrize('kind',['day','batch','run','uncertain','account-halt'])
def test_ordinary_admission_limits_survive_exception(continuation,kind):
    from datetime import datetime,timezone
    store,batch,c,d,f,*_=continuation;activate(continuation)
    if kind=='day':seed(batch,37,kind='implementation_review',day=datetime.now(timezone.utc).date().isoformat());expected='AUTONOMY_DAILY_CALL_LIMIT'
    elif kind=='batch':seed(batch,47);expected='AUTONOMY_BATCH_CALL_LIMIT'
    elif kind=='run':
        for n in range(3):store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',('extra'+str(n),'result_interpretation_author',n+1,'FAILED','{}'))
        expected='STEP_D_MODEL_CALL_LIMIT'
    elif kind=='uncertain':
        store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',('unknown','result_interpretation_author',1,'UNCERTAIN','{}'));expected='UNCERTAIN_MODEL_CALL_NO_RETRY'
    else:
        version,value=Accounts(store).read();value['halted']=True;assert Accounts(store).cas(version,value);expected='LOCAL_ALLOWANCE_HALTED'
    with pytest.raises(ValueError,match=expected):reserve(store,c)
    assert Accounts(store).read()[1]['count']==13


def test_unrelated_scope_and_terminal_rejections_keep_default_policy(continuation):
    store,batch,c,d,f,*_=continuation
    for verdict,category,expected in [('REJECT','metric/statistic','REVIEW_REJECTED'),('REVISE','budget','REVIEW_REQUIRES_OPERATOR_DECISION')]:
        decision={'verdict':verdict,'findings':[{'category':category}]}
        assert x.terminal_transition(ar.review_transition,None,decision,'run_spec_review',4,f,'e'*64)[1]==expected
    with pytest.raises(ValueError):x.terminal_transition(ar.review_transition,None,{'verdict':'REVISE','findings':[]},'run_spec_review',5,f,'e'*64)
    assert ar.review_transition({'verdict':'REVISE','findings':[{'category':'metric/statistic'}]},'run_spec_review',4)[0]=='BLOCKED'
