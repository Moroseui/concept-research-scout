"""Second exact continuation composes with the first without rewriting authority."""
import json
from pathlib import Path
import pytest
from orchestrator import item4_review4_continuation as x,author_revision_accounting as a
from orchestrator import manual_recovery as recovery,analysis_revisions as ar
from orchestrator.manual_executor import Accounts
from test_author_revision_accounting import review,reserve,setup as base_setup
from test_item4_review4_continuation import continuation,activate
from tools import item4_scientific_revision_component as component

@pytest.fixture
def setup(base_setup):
    from orchestrator.manual_executor import atomic,digest
    from orchestrator import experiment_context as ec,private_records as pr
    store,batch,c=base_setup
    state=Path(store.path).parent;context=state.parent
    raw=b'{"synthetic_accounting_fixture":true}'
    pr.write_bytes(context/'execution-plan.json',raw)
    scope={'schema':'scientific-execution/v1','item_number':4,'run_id':ec.ITEM4_RUN,
        'authority_sha256':ec.ITEM4_AUTHORITY,'plan_sha256':digest(raw)}
    c.update(item_number=4,backend='modal',run_id=ec.ITEM4_RUN,context=str(context),
        execution_scope=scope,idea_ids=['sprint13b-execution'],notebook_revision={'mode':'item4-execution-revision'})
    plan={k:c[k] for k in ('execution_scope','idea_ids','item_number','revision_policy','notebook_revision')}
    plan['execution_plan']={'path':'execution-plan.json','sha256':digest(raw)}
    pr.write_text(state/'preparation-plan.json',json.dumps(plan))
    c['plan_sha256']=digest((state/'preparation-plan.json').read_bytes())
    atomic(state/'lane.json',c)
    batch.complete_run('synthetic',{'status':'EMPTY_FIXTURE_ONLY_NO_CALLS'})
    batch.register_run(c['run_id'],{'state':'/lane'})
    return store,batch,c

@pytest.fixture
def second(continuation):
    store,batch,c,d,old,local,glob=continuation
    activate(continuation)
    ident,n,r=reserve(store,c);r['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,r,'COMPLETE')
    a.accepted(d,{'id':ident,'stage':'run_spec_author','round':10})
    value=x.state(store);value.update(phase='run_spec_review',rounds={'run_spec_author':10,'run_spec_review':4})
    store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
    work,value=review(store,c,5)
    value.update(phase='BLOCKED',reason='UNRESOLVED_AFTER_THREE_REVISIONS',rounds={'run_spec_author':10,'run_spec_review':5})
    raw=json.dumps(value);store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(raw,))
    local=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    glob=[dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid')]
    frozen={**old,'author_attempt':11,'review_attempt':6,'state_sha256':x.sha(raw.encode()),
        'local_calls':{r['id']:x.sha(x.canonical(r)) for r in local},
        'global_calls':{r['id']:x.sha(x.canonical(r)) for r in glob},
        'review_call_id':local[-1]['id'],'review_sha256':x.sha((work/'review.json').read_bytes())}
    x.connect(a,recovery,frozen,'d'*64)
    return store,batch,c,d,frozen,old,local,glob


def test_second_pair_charged_and_both_historical_approvals_preserved(second):
    store,batch,c,d,f,old,local,glob=second
    assert x.activate(d,f,'d'*64,d.state/'second')['status']=='READY_AUTHOR11_NO_MODEL_CALL'
    assert a.inspect(store,c['run_id'],'run_spec_author')['binding']['continuation_review_sha256']=='d'*64
    assert a.review_binding(d,'run_spec_author',4,10)['continuation_review_sha256']=='e'*64
    ident,n,r=reserve(store,c);assert n==11 and r[a.FIELD]['review_round']==5
    r['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,r,'COMPLETE')
    a.accepted(d,{'id':ident,'stage':'run_spec_author','round':11})
    v=x.state(store);v.update(phase='run_spec_review',rounds={'run_spec_author':11,'run_spec_review':5})
    store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(v),))
    assert recovery.role_limit(store,c['run_id'],'run_spec_review')==6
    work,v=review(store,c,6)
    assert Accounts(store).read()[1]['count']==17
    for verdict,category,expected in [('REVISE','metric/statistic',('BLOCKED','UNRESOLVED_AFTER_THREE_REVISIONS')),
        ('REJECT','metric/statistic',('BLOCKED','REVIEW_REJECTED')),
        ('REVISE','budget',('BLOCKED','REVIEW_REQUIRES_OPERATOR_DECISION'))]:
        assert x.terminal_transition(ar.review_transition,d,{'verdict':verdict,'findings':[{'category':category}]},'run_spec_review',6,f,'d'*64)==expected
    assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid LIMIT 15')]==local
    assert [dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid LIMIT 15')]==glob
    with pytest.raises(ValueError):x.activate(d,f,'d'*64,d.state/'duplicate')


@pytest.mark.parametrize('fault',['old-grant','new-grant','old-receipt','new-approval','state','extra-pair'])
def test_second_continuation_cannot_replace_old_proof_or_extend_scope(second,fault):
    store,batch,c,d,f,old,local,glob=second
    if fault=='state':
        store.db.execute("UPDATE manual_state SET payload=payload || ' '")
        with pytest.raises(ValueError):x.activate(d,f,'d'*64,d.state/'second')
        return
    if fault=='extra-pair':
        f.update(author_attempt=13,review_attempt=8)
        with pytest.raises(ValueError,match='FIXED_ATTEMPTS'):x.activate(d,f,'d'*64,d.state/'second')
        return
    x.activate(d,f,'d'*64,d.state/'second')
    if fault=='old-grant':store.db.execute('DELETE FROM events WHERE id=?',(x.reason(old),))
    elif fault=='new-grant':store.db.execute('DELETE FROM events WHERE id=?',(x.reason(f),))
    elif fault=='old-receipt':store.db.execute("UPDATE manual_calls SET receipt='{}' WHERE stage='run_spec_author' AND attempt=10")
    elif fault=='new-approval':
        x.connect(a,recovery,f,'c'*64)
    with pytest.raises(ValueError):reserve(store,c)
    assert Accounts(store).read()[1]['count']==15


@pytest.mark.parametrize('field',['verdict','change_id','source_sha','report_sha256',None])
def test_historical_approval_is_authenticated_separately(tmp_path,monkeypatch,field):
    from orchestrator import autonomy_review as ar,manual_host_guard as hg
    approval={'verdict':'APPROVE','change_id':'item4-review4-continuation-20261008',
        'source_sha':component.CONTINUATION_SOURCE,'report_sha256':component.CONTINUATION_REVIEW}
    paths=[]
    def verify(path):paths.append(path);return approval
    monkeypatch.setattr(component,'RECORD',tmp_path);monkeypatch.setattr(hg,'trusted',lambda p:p)
    monkeypatch.setattr(ar,'verify_result',verify)
    if field:
        approval[field]='wrong'
        with pytest.raises(ValueError,match='HELD_CONTINUATION_APPROVAL'):component.held_continuation_approval()
    else:assert component.held_continuation_approval()==component.CONTINUATION_REVIEW
    assert paths==[tmp_path/'history'/component.CONTINUATION_SOURCE/'original-review-directory']


@pytest.mark.parametrize('kind',['day','batch','run','uncertain','account-halt'])
def test_second_pair_keeps_all_normal_limits(second,kind):
    from datetime import datetime,timezone
    from test_scoped_revisions_limits import seed
    store,batch,c,d,f,*_=second;x.activate(d,f,'d'*64,d.state/'second')
    if kind=='day':seed(batch,35,kind='implementation_review',day=datetime.now(timezone.utc).date().isoformat());expected='AUTONOMY_DAILY_CALL_LIMIT'
    elif kind=='batch':seed(batch,45);expected='AUTONOMY_BATCH_CALL_LIMIT'
    elif kind=='run':
        for n in range(5):store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',('extra'+str(n),'result_interpretation_author',n+1,'FAILED','{}'))
        expected='STEP_D_MODEL_CALL_LIMIT'
    elif kind=='uncertain':
        store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',('unknown','result_interpretation_author',1,'UNCERTAIN','{}'));expected='UNCERTAIN_MODEL_CALL_NO_RETRY'
    else:
        version,value=Accounts(store).read();value['halted']=True;assert Accounts(store).cas(version,value);expected='LOCAL_ALLOWANCE_HALTED'
    with pytest.raises(ValueError,match=expected):reserve(store,c)
    assert Accounts(store).read()[1]['count']==15


def test_only_exact_large_artifacts_move_to_complete_workspace_delivery():
    from orchestrator.manual_context import workspace_artifact
    assert workspace_artifact('validator',artifact_id='validator')
    assert workspace_artifact('configuration',artifact_id='current-six-item-backlog')
    assert not workspace_artifact('validator',artifact_id='other')
    assert not workspace_artifact('configuration',artifact_id='item4-current-backlog-selection')
    assert not workspace_artifact('configuration',artifact_id='item4-operator-document-1')
