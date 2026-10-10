"""Bounded native-harness author response with genuine synthetic review protocol."""
import copy,json
import pytest
from orchestrator import item4_smoke_response as post,item4_scoped_calls as scoped
from orchestrator import item4_review4_continuation as x,author_revision_accounting as a
from orchestrator import autonomy_limits as limits,manual_recovery,review_submission as rs
from orchestrator.manual_executor import ManualExecutor,Accounts
from orchestrator.autonomy_accounting import BatchAccounts
from test_item4_diagnostic_scoped_review import (scoped_ready,recovery_ready,diagnostic_ready,
    baseline,diagnostic_plan,response_ready,accepted_author,smoke_ready,extended,fifth,accepted,
    mechanical,fourth,third,setup,second,continuation,base_setup)
from test_author_revision_accounting import review
from test_manual_lane import policy

@pytest.fixture
def native_ready(request,monkeypatch):
    connect=scoped.connect
    originals=[(o,k,getattr(o,k)) for o,k in [(limits,k) for k in
        ('local_limit','global_limit','allowance','cap_authority','scientific_batch_allowance')]+
        [(ManualExecutor,'reserve_call'),(BatchAccounts,'reserve_scientific')]]
    f,scoped_p,work17=request.getfixturevalue('scoped_ready');store,batch,c,d,*_=f
    submit=rs.submit
    def finding(work,pin,decision):
        if work.name=='run_spec_review-14':
            decision['findings'][0]['id']='DIAG-U2-changed-module-native-integration-unverified'
        return submit(work,pin,decision)
    monkeypatch.setattr(rs,'submit',finding)
    value=x.state(store);work,_=review(store,c,14,category='execution authority/provenance')
    value.update(phase='MODEL_RUNNING',pending={'id':post.call(scoped_p,'review'),
        'stage':'run_spec_review','round':14,'workspace':str(work)})
    post.finish_review(d,value,scoped_p,'6'*64)
    raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    assessment=json.loads(raw)['cpu_diagnostic_scoped_review']
    monkeypatch.setattr(post,'NATIVE_REVIEW14_REPORT',assessment['report_sha256'])
    pins=lambda db,sql:{r['id']:x.sha(x.canonical(dict(r))) for r in db.execute(sql)}
    p=copy.deepcopy(scoped_p);p.update(schema=post.NATIVE_SCHEMA,author_attempt=18,review_attempt=15,
        run_limit=35,batch_limit=73,original_state=raw,state_sha256=x.sha(raw.encode()),assessment=assessment,
        assessment_sha256=x.sha(x.canonical(assessment)),reference_author_call_id=post.call(scoped_p,'author'),
        diagnostic_plan_sha256=p['author_outputs']['execution.plan.json'],reference_native_harness_sha256=x.sha(b'reference'),
        local_calls=pins(store.db,'SELECT * FROM manual_calls ORDER BY rowid'),
        global_calls=pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' AND change_id='"+x.RUN+"' ORDER BY rowid"),
        batch_calls=pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid"))
    for o,k,fn in originals:monkeypatch.setattr(o,k,fn)
    monkeypatch.setattr(scoped,'_validate',None)
    _,recovery,_=request.getfixturevalue('recovery_ready');_,diagnostic=request.getfixturevalue('diagnostic_ready')
    _,smoke,post_p,_=request.getfixturevalue('response_ready');_,saved=request.getfixturevalue('extended')
    connect(request.getfixturevalue('fourth')[4],'b'*64,mechanical=request.getfixturevalue('mechanical')[4],mechanical_approval='a'*64,
        response=f[4],response_approval='9'*64,batch_extension=saved['extension'],batch_approval='e'*64,
        smoke=smoke,smoke_approval='d'*64,post_smoke=post_p,post_smoke_approval='c'*64,
        diagnostic=diagnostic,diagnostic_approval='8'*64,diagnostic_recovery=recovery,diagnostic_recovery_approval='7'*64,
        diagnostic_scoped=scoped_p,diagnostic_scoped_approval='6'*64,diagnostic_native=p,diagnostic_native_approval='5'*64)
    assert limits.local_limit(store,x.RUN,policy())==33
    before=[dict(row) for row in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    assert post.activate(d,p,'5'*64,d.state/'cpu-diagnostic-native-harness')['status']=='READY_DIAGNOSTIC_AUTHOR18'
    assert before==[dict(row) for row in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    return f,p,work17


def test_author18_counted_with_genuine_revise_and_all_later_calls_held(native_ready):
    f,p,work=native_ready;store,batch,c,d,*_=f
    before=[dict(row) for row in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    for row in before:
        binding=json.loads(row['receipt']).get(a.FIELD)
        if binding is not None:
            assert binding==a.review_binding(d,row['stage'],binding['review_round'],row['attempt']), row['attempt']
    old=copy.deepcopy(x.state(store));assert manual_recovery.role_limit(store,x.RUN,'run_spec_author')==18
    ident,n,receipt=store.reserve_call(x.RUN,'run_spec_author',c['source'],'astra/manual-test',policy(),{})
    assert ident==post.call(p,'author') and n==18
    assert receipt['batch_accounting']['run_limit']==35 and receipt['batch_accounting']['batch_limit']==73
    assert receipt[a.FIELD]['review_round']==14 and receipt[a.FIELD]['review_sha256']==p['assessment']['report_sha256']
    assert receipt['accounting']['limit_amendment']['review_sha256']=='5'*64
    receipt['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,receipt,'COMPLETE')
    a.accepted(d,{'id':ident,'stage':'run_spec_author','round':18})
    assert [dict(row) for row in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')][:31]==before
    assert Accounts(store).read()[1]['count']==32
    assert batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]==70
    for stage in ['run_spec_review','result_interpretation_author','run_spec_author']:
        value=copy.deepcopy(old);value.update(phase=stage,rounds={'run_spec_author':18,'run_spec_review':14});d.save(value)
        charged=Accounts(store).read()
        with pytest.raises(ValueError):store.reserve_call(x.RUN,stage,c['source'],'astra/manual-test',policy(),{})
        assert Accounts(store).read()==charged
        for key in post.protected_keys(p):assert x.state(store).get(key)==old.get(key)
    post.originals(store,p,'5'*64)

@pytest.mark.parametrize('fault',['reference-bytes','old-local','old-global','global-hold','wrong-stage','daily','uncertain','failed-author-accepted','reference-unaccepted','grant'])
def test_failed_scope_never_consumes_a_call(native_ready,fault):
    f,p,work=native_ready;store,batch,c,d,*_=f
    if fault=='reference-bytes':(work/'notebook.patch.json').write_bytes(b'changed')
    elif fault in {'old-local','old-global'}:
        db,table,pins=(store.db,'manual_calls',p['local_calls']) if fault=='old-local' else (batch.db,'autonomy_calls',p['global_calls'])
        db.execute('UPDATE '+table+" SET receipt='changed' WHERE id=?",(next(iter(pins)),))
    elif fault in {'global-hold','wrong-stage'}:
        value=x.state(store)
        if fault=='global-hold':value['cpu_diagnostic_scoped_review']['verdict']='APPROVE'
        else:value['phase']='run_spec_review'
        d.save(value)
    elif fault=='failed-author-accepted':a.accepted(d,{'id':post.FAILED_AUTHOR,'stage':'run_spec_author','round':16})
    elif fault=='reference-unaccepted':store.db.execute('DELETE FROM events WHERE id=?',('author-accepted:'+p['reference_author_call_id'],))
    elif fault=='grant':store.db.execute("UPDATE events SET payload='{}' WHERE id=?",(post.profile(p)['event'],))
    elif fault=='daily':
        from datetime import datetime,timezone
        from test_scoped_revisions_limits import seed
        day=datetime.now(timezone.utc).date().isoformat();n=batch.db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(day,)).fetchone()[0]
        seed(batch,50-n,kind='implementation_review',day=day)
    else:batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('new-uncertain','review','other',1,'2000-01-01','UNCERTAIN','{}','{}'))
    before=Accounts(store).read();rows=[dict(row) for row in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    with pytest.raises(ValueError):store.reserve_call(x.RUN,'run_spec_review' if fault=='wrong-stage' else 'run_spec_author',c['source'],'astra/manual-test',policy(),{})
    assert Accounts(store).read()==before and rows==[dict(row) for row in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]

@pytest.mark.parametrize('module',[b'pass',b'def native_synthetic_integration(): pass',
    b'def native_synthetic_integration(progress_factory=None): pass',
    b'def native_synthetic_integration(progress_factory): pass\ndef native_synthetic_integration(progress_factory): pass'])
def test_native_worker_entrypoint_refused_before_acceptance(module):
    plan=x.canonical(diagnostic_plan());p={'schema':post.NATIVE_SCHEMA,'baseline_plan':x.canonical(baseline()).decode(),
        'baseline_module_sha256':x.sha(b'old'),'diagnostic_plan_sha256':x.sha(plan)}
    with pytest.raises(ValueError,match='NATIVE_ENTRYPOINT_REQUIRED'):post.validate_diagnostic_delta(plan,module,p)


def test_native_entrypoint_does_not_allow_plan_drift():
    plan=x.canonical(diagnostic_plan());p={'schema':post.NATIVE_SCHEMA,'baseline_plan':x.canonical(baseline()).decode(),
        'baseline_module_sha256':x.sha(b'old'),'diagnostic_plan_sha256':x.sha(plan)}
    module=b'def native_synthetic_integration(progress_factory): pass'
    assert post.validate_diagnostic_delta(plan,module,p)['execution_authorized'] is False
    with pytest.raises(ValueError,match='DIAGNOSTIC_PLAN_CHANGED'):post.validate_diagnostic_delta(plan+b' ',module,p)
