"""Real synthetic ledger transitions, frozen authors and unchanged global holds."""
import copy,json
import pytest
from orchestrator import item4_smoke_response as post,item4_scoped_calls as scoped
from orchestrator import item4_review4_continuation as x,author_revision_accounting as a
from orchestrator import autonomy_limits as limits,manual_recovery,experiment_collection
from orchestrator.manual_executor import ManualExecutor,Accounts
from orchestrator.autonomy_accounting import BatchAccounts
from test_item4_diagnostic_entrypoint_recovery import (recovery_ready,diagnostic_ready,baseline,
    diagnostic_plan,response_ready,accepted_author,smoke_ready,extended,fifth,accepted,mechanical,
    fourth,third,setup,second,continuation,base_setup)
from test_author_revision_accounting import review
from test_manual_lane import policy

@pytest.fixture
def scoped_ready(request,monkeypatch):
    connect=scoped.connect
    originals=[(o,k,getattr(o,k)) for o,k in [(limits,k) for k in
        ('local_limit','global_limit','allowance','cap_authority','scientific_batch_allowance')]+
        [(ManualExecutor,'reserve_call'),(BatchAccounts,'reserve_scientific')]]
    f,recovery,_=request.getfixturevalue('recovery_ready');store,batch,c,d,*_=f
    ident,n,r=store.reserve_call(x.RUN,'run_spec_author',c['source'],'astra/manual-test',policy(),{})
    work=d.state.parent/(d.state.name+'-scientific-workspaces')/'run_spec_author-17';work.mkdir()
    files={'SPEC.proposed.md':b'exact author spec','notebook.patch.json':b'exact patch','execution.plan.json':b'exact plan'}
    for name,raw in files.items():(work/name).write_bytes(raw)
    r.update(workspace=str(work),output_sha256={k:x.sha(v) for k,v in files.items()})
    store.finish_call(ident,r,'COMPLETE');a.accepted(d,{'id':ident,'stage':'run_spec_author','round':17})
    value=x.state(store);value.update(phase='run_spec_review',rounds={'run_spec_author':17,'run_spec_review':12},artifacts=[]);d.save(value)
    # Candidate extraction has its separate structural/real-source tests. Ledger tests never execute scientific code.
    monkeypatch.setattr(post,'executable_candidate',lambda *args:post.validate_diagnostic_delta(x.canonical(diagnostic_plan()),b'changed',recovery))
    value=x.state(store);review_work,_=review(store,c,13,category='budget')
    value.update(phase='MODEL_RUNNING',pending={'id':post.call(recovery,'review'),'stage':'run_spec_review','round':13,'workspace':str(review_work)})
    post.finish_review(d,value,recovery,'7'*64)
    raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    value=json.loads(raw);assessment=value['cpu_diagnostic_recovery']
    monkeypatch.setattr(post,'SCOPED_REVIEW13_REPORT',assessment['report_sha256'])
    pins=lambda db,sql:{r['id']:x.sha(x.canonical(dict(r))) for r in db.execute(sql)}
    p=copy.deepcopy(recovery);p.update(schema=post.SCOPED_SCHEMA,review_attempt=14,run_limit=33,batch_limit=71,
        original_state=raw,state_sha256=x.sha(raw.encode()),assessment=assessment,assessment_sha256=x.sha(x.canonical(assessment)),
        accepted_author_event=json.loads(store.db.execute('SELECT payload FROM events WHERE id=?',('author-accepted:'+ident,)).fetchone()[0]),
        author_outputs=r['output_sha256'],local_calls=pins(store.db,'SELECT * FROM manual_calls ORDER BY rowid'),
        global_calls=pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' AND change_id='"+x.RUN+"' ORDER BY rowid"),
        batch_calls=pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid"))
    for o,k,fn in originals:monkeypatch.setattr(o,k,fn)
    monkeypatch.setattr(scoped,'_validate',None)
    _,smoke,post_p,_=request.getfixturevalue('response_ready');_,diagnostic=request.getfixturevalue('diagnostic_ready')
    _,saved=request.getfixturevalue('extended')
    connect(request.getfixturevalue('fourth')[4],'b'*64,mechanical=request.getfixturevalue('mechanical')[4],mechanical_approval='a'*64,
        response=f[4],response_approval='9'*64,batch_extension=saved['extension'],batch_approval='e'*64,
        smoke=smoke,smoke_approval='d'*64,post_smoke=post_p,post_smoke_approval='c'*64,
        diagnostic=diagnostic,diagnostic_approval='8'*64,diagnostic_recovery=recovery,diagnostic_recovery_approval='7'*64,
        diagnostic_scoped=p,diagnostic_scoped_approval='6'*64)
    assert limits.local_limit(store,x.RUN,policy())==32
    before=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    assert post.activate(d,p,'6'*64,d.state/'cpu-diagnostic-scoped-review')['status']=='READY_DIAGNOSTIC_REVIEW14'
    assert before==[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    return f,p,work

@pytest.mark.parametrize('verdict',['APPROVE','REVISE','REJECT'])
def test_only_review14_is_charged_and_all_verdicts_keep_global_holds(scoped_ready,verdict):
    f,p,work=scoped_ready;store,batch,c,d,*_=f
    before=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    value=x.state(store);old=copy.deepcopy(value)
    assert manual_recovery.role_limit(store,x.RUN,'run_spec_review')==14
    review_work,_=review(store,c,14,verdict=verdict)
    value.update(phase='MODEL_RUNNING',pending={'id':post.call(p,'review'),'stage':'run_spec_review','round':14,'workspace':str(review_work)})
    result=post.finish_review(d,value,p,'6'*64);record=result['cpu_diagnostic_scoped_review']
    assert result['phase']=='BLOCKED' and record['verdict']==verdict
    assert record['scientific_scope']=='two-cpu-diagnostic-fits-only'
    assert record['carried_review_sha256']==p['assessment']['report_sha256']
    assert all(record[k] is False for k in ['global_findings_closed','execution_authorized','full_training_admitted','coverage_released'])
    assert result['cpu_diagnostic_recovery']==old['cpu_diagnostic_recovery'] and result['cpu_diagnostic_recovery']['verdict']=='REVISE'
    for key in post.protected_keys(p):assert result.get(key)==old.get(key)
    after=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    assert after[:30]==before and len(after)==31
    receipt=json.loads(after[-1]['receipt'])
    assert receipt['batch_accounting']['run_limit']==33 and receipt['batch_accounting']['batch_limit']==71
    assert Accounts(store).read()[1]['count']==31
    assert batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]==69
    value=x.state(store);value.update(phase='result_interpretation_author');d.save(value)
    prior=Accounts(store).read()
    with pytest.raises((ValueError,KeyError,FileNotFoundError)):
        store.reserve_call(x.RUN,'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
    assert Accounts(store).read()==prior
    post.originals(store,p,'6'*64)

@pytest.mark.parametrize('fault',['author-bytes','accepted-event','old-call','global-call','carried-review','global-hold','superseding-author','wrong-stage','daily','uncertain','duplicate'])
def test_refusal_never_charges_or_rewrites_originals(scoped_ready,fault):
    f,p,work=scoped_ready;store,batch,c,d,*_=f
    if fault=='author-bytes':(work/'notebook.patch.json').write_bytes(b'changed')
    elif fault=='accepted-event':store.db.execute('DELETE FROM events WHERE id=?',('author-accepted:'+post.call(p,'author'),))
    elif fault=='old-call':store.db.execute("UPDATE manual_calls SET receipt='{}' WHERE id=?",(post.call(p,'author'),))
    elif fault=='global-call':batch.db.execute("UPDATE autonomy_calls SET receipt='{}' WHERE id=?",(post.call(p,'author'),))
    elif fault in {'carried-review','global-hold','superseding-author','wrong-stage'}:
        value=x.state(store)
        if fault=='carried-review':value['cpu_diagnostic_recovery']['verdict']='APPROVE'
        elif fault=='global-hold':value['reviewed_execution']={'forged':True}
        elif fault=='superseding-author':value['artifacts'].append({'id':'authored-execution-plan','type':'configuration','version':18})
        else:value['phase']='run_spec_author'
        d.save(value)
    elif fault=='daily':
        from datetime import datetime,timezone
        from test_scoped_revisions_limits import seed
        day=datetime.now(timezone.utc).date().isoformat();n=batch.db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(day,)).fetchone()[0]
        seed(batch,50-n,kind='implementation_review',day=day)
    elif fault=='uncertain':batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('new-uncertain','review','other',1,'2000-01-01','UNCERTAIN','{}','{}'))
    before=Accounts(store).read();rows=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    with pytest.raises(ValueError):
        if fault=='duplicate':post.activate(d,p,'6'*64,d.state/'duplicate-scoped-review')
        else:store.reserve_call(x.RUN,'run_spec_author' if fault=='wrong-stage' else 'run_spec_review',c['source'],'astra/manual-test',policy(),{})
    assert Accounts(store).read()==before and rows==[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
