"""One diagnosed unaccepted author; no general relaxation or execution grant."""
import copy,json
import pytest
from orchestrator import item4_smoke_response as post,item4_scoped_calls as scoped
from orchestrator import item4_review4_continuation as x,author_revision_accounting as a
from orchestrator import autonomy_limits as limits,manual_recovery,experiment_collection
from orchestrator.manual_executor import ManualExecutor,Accounts
from orchestrator.autonomy_accounting import BatchAccounts
from test_item4_cpu_diagnostic_authoring import (diagnostic_ready,baseline,diagnostic_plan,
    response_ready,accepted_author,smoke_ready,extended,fifth,accepted,mechanical,fourth,third,
    setup,second,continuation,base_setup)
from test_author_revision_accounting import review
from test_manual_lane import policy

@pytest.fixture
def recovery_ready(request,monkeypatch):
    connect=scoped.connect
    originals=[(o,k,getattr(o,k)) for o,k in [(limits,k) for k in
        ('local_limit','global_limit','allowance','cap_authority','scientific_batch_allowance')]+
        [(ManualExecutor,'reserve_call'),(BatchAccounts,'reserve_scientific')]]
    f,diagnostic=request.getfixturevalue('diagnostic_ready');store,batch,c,d,*_=f
    ident,n,receipt=store.reserve_call(x.RUN,'run_spec_author',c['source'],'astra/manual-test',policy(),{})
    assert n==16
    work=d.state.parent/(d.state.name+'-scientific-workspaces')/'run_spec_author-16';work.mkdir(parents=True)
    files={'SPEC.proposed.md':b'spec','notebook.patch.json':b'patch','execution.plan.json':b'plan'}
    for name,raw in files.items():(work/name).write_bytes(raw)
    (work/'console.log').write_bytes(b'preserved-native-stream')
    receipt.update(workspace=str(work),output_sha256={k:x.sha(v) for k,v in files.items()},
        native={'transport_returncode':0,'console_sha256':x.sha(b'preserved-native-stream')})
    store.finish_call(ident,receipt,'COMPLETE')
    value=x.state(store);value.update(phase='BLOCKED',reason=post.FAILED_REASON,
        rounds={'run_spec_author':16,'run_spec_review':12},pending={'id':ident,'stage':'run_spec_author','round':16,'workspace':str(work)})
    d.save(value);raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    pins=lambda db,sql:{r['id']:x.sha(x.canonical(dict(r))) for r in db.execute(sql)}
    p=copy.deepcopy(diagnostic);p.update(schema=post.RECOVERY_SCHEMA,author_attempt=17,run_limit=32,batch_limit=70,
        original_state=raw,state_sha256=x.sha(raw.encode()),direction_sha256=post.RECOVERY_DIRECTION,
        failed_call_id=ident,failed_outputs=receipt['output_sha256'],
        local_calls=pins(store.db,'SELECT * FROM manual_calls ORDER BY rowid'),
        global_calls=pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' AND change_id='"+x.RUN+"' ORDER BY rowid"),
        batch_calls=pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid"))
    for o,k,fn in originals:monkeypatch.setattr(o,k,fn)
    monkeypatch.setattr(scoped,'_validate',None)
    _,smoke,post_p,_=request.getfixturevalue('response_ready')
    _,saved=request.getfixturevalue('extended')
    connect(request.getfixturevalue('fourth')[4],'b'*64,
        mechanical=request.getfixturevalue('mechanical')[4],mechanical_approval='a'*64,
        response=f[4],response_approval='9'*64,batch_extension=saved['extension'],batch_approval='e'*64,
        smoke=smoke,smoke_approval='d'*64,post_smoke=post_p,post_smoke_approval='c'*64,
        diagnostic=diagnostic,diagnostic_approval='8'*64,diagnostic_recovery=p,diagnostic_recovery_approval='7'*64)
    assert limits.local_limit(store,x.RUN,policy())==31
    before=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    result=post.activate(d,p,'7'*64,d.state/'cpu-diagnostic-recovery')
    assert result['status']=='READY_DIAGNOSTIC_AUTHOR17' and not x.state(store).get('pending')
    assert before==[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    return f,p,work


def test_recovery_counts_failed_author_and_keeps_scientific_review_and_final_hold(recovery_ready,monkeypatch):
    f,p,work=recovery_ready;store,batch,c,d,*_=f
    before=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    ident,n,r=store.reserve_call(x.RUN,'run_spec_author',c['source'],'astra/manual-test',policy(),{})
    assert n==17 and ident==post.call(p,'author')
    assert (r['batch_accounting']['run_limit'],r['batch_accounting']['batch_limit'])==(32,70)
    r['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,r,'COMPLETE')
    a.accepted(d,{'id':ident,'stage':'run_spec_author','round':17})
    value=x.state(store);value.update(phase='run_spec_review',rounds={'run_spec_author':17,'run_spec_review':12});d.save(value)
    monkeypatch.setattr(post,'executable_candidate',lambda *args:post.validate_diagnostic_delta(x.canonical(diagnostic_plan()),b'changed',p))
    assert manual_recovery.role_limit(store,x.RUN,'run_spec_review')==13
    value=x.state(store);review_work,_=review(store,c,13,verdict='APPROVE')
    value.update(phase='MODEL_RUNNING',pending={'id':post.call(p,'review'),'stage':'run_spec_review','round':13,'workspace':str(review_work)})
    result=post.finish_review(d,value,p,'7'*64)
    assert result['reason']=='CPU_DIAGNOSTIC_AUTHORING_APPROVE_EXECUTION_HELD'
    assert result['cpu_diagnostic_recovery']['execution_authorized'] is False
    assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')][:28]==before
    assert Accounts(store).read()[1]['count']==30
    assert batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]==68
    value=x.state(store);value.update(phase='result_interpretation_author');d.save(value)
    prior=Accounts(store).read()
    with pytest.raises((ValueError,KeyError,FileNotFoundError)):
        store.reserve_call(x.RUN,'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
    assert Accounts(store).read()==prior
    post.originals(store,p,'7'*64)


@pytest.mark.parametrize('fault',['accepted','output','stream','prior-call','wrong-direction','duplicate','daily','uncertain','execution'])
def test_failed_author_exception_refuses_drift_and_keeps_charges(recovery_ready,fault):
    f,p,work=recovery_ready;store,batch,c,d,*_=f
    if fault=='accepted':a.accepted(d,{'id':post.FAILED_AUTHOR,'stage':'run_spec_author','round':16})
    elif fault=='output':(work/'notebook.patch.json').write_bytes(b'changed')
    elif fault=='stream':(work/'console.log').write_bytes(b'changed')
    elif fault=='prior-call':store.db.execute("UPDATE manual_calls SET receipt='{}' WHERE id=?",(post.FAILED_AUTHOR,))
    elif fault=='wrong-direction':p['direction_sha256']='f'*64
    elif fault=='daily':
        from datetime import datetime,timezone
        from test_scoped_revisions_limits import seed
        day=datetime.now(timezone.utc).date().isoformat();n=batch.db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(day,)).fetchone()[0]
        seed(batch,50-n,kind='implementation_review',day=day)
    elif fault=='uncertain':batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('new-uncertain','review','other',1,'2000-01-01','UNCERTAIN','{}','{}'))
    elif fault=='execution':
        value=x.state(store);value['execution_package']={'changed':True};d.save(value)
    before=Accounts(store).read()
    with pytest.raises(ValueError):
        if fault=='duplicate':post.activate(d,p,'7'*64,d.state/'duplicate-recovery')
        else:store.reserve_call(x.RUN,'run_spec_author',c['source'],'astra/manual-test',policy(),{})
    assert Accounts(store).read()==before
