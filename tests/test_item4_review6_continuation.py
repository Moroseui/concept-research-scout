"""Third exact continuation retains both historical grants and all admission limits."""
import json
from pathlib import Path
import pytest
from orchestrator import item4_review4_continuation as x, author_revision_accounting as a
from orchestrator import manual_recovery as recovery, analysis_revisions as ar
from orchestrator.manual_executor import Accounts
from test_author_revision_accounting import review,reserve,setup as base_setup
from test_item4_review4_continuation import continuation,activate
from test_item4_review5_continuation import setup,second
from tools import item4_scientific_revision_component as component

@pytest.fixture
def third(second):
    store,batch,c,d,old,first,local,glob=second
    x.activate(d,old,'d'*64,d.state/'second')
    ident,n,r=reserve(store,c);assert n==11
    r['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,r,'COMPLETE')
    a.accepted(d,{'id':ident,'stage':'run_spec_author','round':11})
    v=x.state(store);v.update(phase='run_spec_review',rounds={'run_spec_author':11,'run_spec_review':5})
    store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(v),))
    work,v=review(store,c,6)
    v.update(phase='BLOCKED',reason='UNRESOLVED_AFTER_THREE_REVISIONS',rounds={'run_spec_author':11,'run_spec_review':6})
    raw=json.dumps(v);store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(raw,))
    local=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    glob=[dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid')]
    frozen={**old,'author_attempt':12,'review_attempt':7,'state_sha256':x.sha(raw.encode()),
        'local_calls':{r['id']:x.sha(x.canonical(r)) for r in local},
        'global_calls':{r['id']:x.sha(x.canonical(r)) for r in glob},
        'review_call_id':local[-1]['id'],'review_sha256':x.sha((work/'review.json').read_bytes())}
    x.connect(a,recovery,frozen,'c'*64)
    return store,batch,c,d,frozen,old,local,glob

def test_third_pair_charged_and_both_historical_approvals_preserved(third):
    store,batch,c,d,f,old,local,glob=third
    assert x.activate(d,f,'c'*64,d.state/'third')['status']=='READY_AUTHOR12_NO_MODEL_CALL'
    assert a.inspect(store,c['run_id'],'run_spec_author')['binding']['continuation_review_sha256']=='c'*64
    assert a.review_binding(d,'run_spec_author',4,10)['continuation_review_sha256']=='e'*64
    assert a.review_binding(d,'run_spec_author',5,11)['continuation_review_sha256']=='d'*64
    ident,n,r=reserve(store,c);assert n==12 and r[a.FIELD]['review_round']==6
    r['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,r,'COMPLETE')
    a.accepted(d,{'id':ident,'stage':'run_spec_author','round':12})
    v=x.state(store);v.update(phase='run_spec_review',rounds={'run_spec_author':12,'run_spec_review':6})
    store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(v),))
    assert recovery.role_limit(store,c['run_id'],'run_spec_review')==7
    work,v=review(store,c,7)
    assert Accounts(store).read()[1]['count']==19
    for verdict,category,expected in [('REVISE','metric/statistic',('BLOCKED','UNRESOLVED_AFTER_THREE_REVISIONS')),
        ('REJECT','metric/statistic',('BLOCKED','REVIEW_REJECTED')),
        ('REVISE','budget',('BLOCKED','REVIEW_REQUIRES_OPERATOR_DECISION'))]:
        assert x.terminal_transition(ar.review_transition,d,{'verdict':verdict,'findings':[{'category':category}]},'run_spec_review',7,f,'c'*64)==expected
    assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid LIMIT 17')]==local
    assert [dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid LIMIT 17')]==glob
    with pytest.raises(ValueError):x.activate(d,f,'c'*64,d.state/'duplicate')


@pytest.mark.parametrize('fault',['old-grant','new-grant','old-receipt','new-approval','state','extra-pair'])
def test_third_continuation_cannot_replace_old_proof_or_extend_scope(third,fault):
    store,batch,c,d,f,old,local,glob=third
    if fault=='state':
        store.db.execute("UPDATE manual_state SET payload=payload || ' '")
        with pytest.raises(ValueError):x.activate(d,f,'c'*64,d.state/'third')
        return
    if fault=='extra-pair':
        f.update(author_attempt=14,review_attempt=9)
        with pytest.raises(ValueError,match='FIXED_ATTEMPTS'):x.activate(d,f,'c'*64,d.state/'third')
        return
    x.activate(d,f,'c'*64,d.state/'third')
    if fault=='old-grant':store.db.execute('DELETE FROM events WHERE id=?',(x.reason(old),))
    elif fault=='new-grant':store.db.execute('DELETE FROM events WHERE id=?',(x.reason(f),))
    elif fault=='old-receipt':store.db.execute("UPDATE manual_calls SET receipt='{}' WHERE stage='run_spec_author' AND attempt=11")
    elif fault=='new-approval':
        x.connect(a,recovery,f,'b'*64)
    with pytest.raises(ValueError):reserve(store,c)
    assert Accounts(store).read()[1]['count']==17


@pytest.mark.parametrize('field',['verdict','change_id','source_sha','report_sha256',None])
def test_historical_approval_is_authenticated_separately(tmp_path,monkeypatch,field):
    from orchestrator import autonomy_review as ar,manual_host_guard as hg
    approval={'verdict':'APPROVE','change_id':'item4-review5-continuation-20261008',
        'source_sha':component.SECOND_SOURCE,'report_sha256':component.SECOND_REVIEW}
    paths=[]
    def verify(path):paths.append(path);return approval
    monkeypatch.setattr(component,'RECORD',tmp_path);monkeypatch.setattr(hg,'trusted',lambda p:p)
    monkeypatch.setattr(ar,'verify_result',verify)
    if field:
        approval[field]='wrong'
        with pytest.raises(ValueError,match='HELD_SECOND_CONTINUATION_APPROVAL'):component.held_second_continuation_approval()
    else:assert component.held_second_continuation_approval()==component.SECOND_REVIEW
    assert paths==[tmp_path/'history'/component.SECOND_SOURCE/'original-review-directory']


@pytest.mark.parametrize('kind',['day','batch','run','uncertain','account-halt'])
def test_third_pair_keeps_all_normal_limits(third,kind):
    from datetime import datetime,timezone
    from test_scoped_revisions_limits import seed
    store,batch,c,d,f,*_=third;x.activate(d,f,'c'*64,d.state/'third')
    if kind=='day':seed(batch,33,kind='implementation_review',day=datetime.now(timezone.utc).date().isoformat());expected='AUTONOMY_DAILY_CALL_LIMIT'
    elif kind=='batch':seed(batch,43);expected='AUTONOMY_BATCH_CALL_LIMIT'
    elif kind=='run':
        for n in range(3):store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',('extra'+str(n),'result_interpretation_author',n+1,'FAILED','{}'))
        expected='STEP_D_MODEL_CALL_LIMIT'
    elif kind=='uncertain':
        store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',('unknown','result_interpretation_author',1,'UNCERTAIN','{}'));expected='UNCERTAIN_MODEL_CALL_NO_RETRY'
    else:
        version,value=Accounts(store).read();value['halted']=True;assert Accounts(store).cas(version,value);expected='LOCAL_ALLOWANCE_HALTED'
    with pytest.raises(ValueError,match=expected):reserve(store,c)
    assert Accounts(store).read()[1]['count']==17


