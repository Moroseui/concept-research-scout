import copy,json,sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import multiwin_returned as f
from test_colab_arm_preparation import database,snapshot
ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture
def lane(tmp_path,monkeypatch):
    state=tmp_path/'work/lane';state.mkdir(parents=True,mode=0o700)
    db=database(state/'jobs.sqlite');glob=database(tmp_path/'batch/jobs.sqlite')
    config={'run_id':f.RUN,'source':'a'*40,'workspace_root':str(state.parent/'lane-scientific-workspaces'),'batch_ledger':str(tmp_path/'batch'),'context':str(state/'context')}
    value={'phase':'BLOCKED','reason':'OUTPUT_VALIDATION_REFUSED: ANALYSIS_REVISION_ROUND',
        'pending':{'id':f.sha((f.RUN+":run_spec_review:11").encode()),'stage':'run_spec_review','round':11},
        'rounds':{'run_spec_author':12,'run_spec_review':11,'result_interpretation_author':1},
        'interventions':[],'artifacts':[]}
    db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps(value),))
    db.execute("INSERT INTO manual_account VALUES(1,'all charges retained')")
    stages=[('run_spec_author',n)for n in range(1,13)]+[('run_spec_review',n)for n in range(1,12)]+[('result_interpretation_author',1)]
    for i,(stage,n)in enumerate(stages):
        ident=f.sha((f.RUN+':'+stage+':'+str(n)).encode())
        status='COMPLETE'
        db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(ident,stage,n,status,'{"charge":1}'))
        glob.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',(ident,'scientific',f.RUN,i+1,'2026-10-13',status,'{}','{"charge":1}'))
    glob.execute('INSERT INTO autonomy_runs VALUES(?,?,?)',(f.RUN,'{}','ACTIVE'))
    work=state.parent/'lane-scientific-workspaces/run_spec_review-11';work.mkdir(parents=True,mode=0o700)
    from orchestrator import review_submission as rs
    review={'verdict':'REVISE','findings':[{'id':'trainer'},{'id':'authority'}]}
    console=work/'review.json';console.write_text(json.dumps(review))
    submission=work/rs.RECORD;submission.write_text(json.dumps({'submission':{**review,'bindings':{'call_id':f.sha((f.RUN+':run_spec_review:11').encode())}}}))
    b={'config':config,'files':{str(console):f.sha(console.read_bytes()),str(submission):f.sha(submission.read_bytes())},'prior_review_call':f.sha((f.RUN+':run_spec_review:11').encode()),
       'state_row':dict(db.execute('SELECT * FROM manual_state').fetchone()),
       'account_row':dict(db.execute('SELECT * FROM manual_account').fetchone()),
       'owner':dict(glob.execute('SELECT * FROM autonomy_runs').fetchone()),
       'allowed_calls':[{'stage':s,'attempt':n}for s,n in [('run_spec_author',13),('run_spec_review',12)]]}
    for key,con,table in [('local_calls_pins',db,'manual_calls'),('global_calls_pins',glob,'autonomy_calls'),('scientific_calls_pins',glob,'autonomy_calls')]:
        b[key]={r['id']:f.sha(f.canonical(dict(r)))for r in con.execute('SELECT * FROM '+table)}
    store=NS(db=db,path=state/'jobs.sqlite',batch=NS(db=glob,folder=tmp_path/'batch'))
    driver=NS(config=config,state=state,store=store,current=lambda:json.loads(db.execute('SELECT payload FROM manual_state').fetchone()[0]))
    yield NS(driver=driver,b=b,db=db,glob=glob,work=work,console=console)
    db.close();glob.close()
def test_resume_preserves_history_and_genuine_review_round(lane):
    x=lane;old=[snapshot(db,t)for db,t in [(x.db,'manual_calls'),(x.db,'manual_account'),(x.glob,'autonomy_calls'),(x.glob,'autonomy_runs')]]
    out=f.resume(x.driver,x.b,'a'*64)
    assert out['maximum_new_calls']==2 and out['preserved_calls']==24
    assert x.driver.current()['rounds']=={'run_spec_author':12,'run_spec_review':11,'result_interpretation_author':1}
    assert x.driver.current()['pending']is None
    assert old==[snapshot(db,t)for db,t in [(x.db,'manual_calls'),(x.db,'manual_account'),(x.glob,'autonomy_calls'),(x.glob,'autonomy_runs')]]
    assert f.grant(x.driver,x.b,'a'*64)['run_limit']==26
    with pytest.raises(ValueError):f.resume(x.driver,x.b,'a'*64)
@pytest.mark.parametrize('target',['local','global','owner','state','account','file','config','running'])
def test_drift_refused_before_transition(lane,target):
    x=lane
    if target=='local':x.db.execute("UPDATE manual_calls SET receipt='changed'")
    if target=='global':x.glob.execute("UPDATE autonomy_calls SET receipt='changed'")
    if target=='owner':x.glob.execute("UPDATE autonomy_runs SET status='COMPLETE'")
    if target=='state':x.db.execute("UPDATE manual_state SET payload='{}'")
    if target=='account':x.db.execute("UPDATE manual_account SET payload='changed'")
    if target=='file':x.console.write_text('{}')
    if target=='config':x.driver.config={**x.driver.config,'extra':True}
    if target=='running':x.glob.execute("INSERT INTO autonomy_calls VALUES('live','scientific','other',1,'2026-10-13','RUNNING','{}','{}')")
    with pytest.raises(ValueError):f.resume(x.driver,x.b,'a'*64)
    assert not(x.driver.state/f.EVENT).exists()
@pytest.mark.parametrize('verdict',['REJECT','APPROVE'])
def test_other_verdict_cannot_be_called_revise(lane,verdict):
    from orchestrator import review_submission as rs
    x=lane
    v=json.loads(x.console.read_text());v['verdict']=verdict;x.console.write_text(json.dumps(v))
    x.b['files'][str(x.console)]=f.sha(x.console.read_bytes())
    with pytest.raises(ValueError):f.resume(x.driver,x.b,'a'*64)
    assert not(x.driver.state/f.EVENT).exists()
def add(x,stage,n):
    ident=f.sha((f.RUN+':'+stage+':'+str(n)).encode())
    x.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(ident,stage,n,'COMPLETE','{}'))
    x.glob.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',(ident,'scientific',f.RUN,x.glob.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]+1,'2026-10-13','COMPLETE','{}','{}'))
def test_two_exact_calls_then_third_refused(lane):
    x=lane;f.resume(x.driver,x.b,'a'*64)
    for s,n in [('run_spec_author',13),('run_spec_review',12)]:
        add(x,s,n);f.grant(x.driver,x.b,'a'*64)
    assert x.glob.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==26
    add(x,'run_spec_author',14)
    with pytest.raises(ValueError,match='TWO_CALL_SCOPE'):f.grant(x.driver,x.b,'a'*64)
@pytest.mark.parametrize('stage,n',[('run_spec_author',14),('run_spec_review',13),('result_interpretation_author',2)])
def test_unrelated_calls_refused(lane,stage,n):
    x=lane;f.resume(x.driver,x.b,'a'*64);add(x,stage,n)
    with pytest.raises(ValueError,match='TWO_CALL_SCOPE'):f.grant(x.driver,x.b,'a'*64)
def test_pinned_scope_unchanged_money_and_original_counts():
    b=f.frozen(ROOT)
    assert b['run_limit']==26 and b['batch_limit']==140 and b['maximum_new_calls']==2
    assert len(b['local_calls_pins'])==len(b['global_calls_pins'])==24 and len(b['scientific_calls_pins'])==128
    assert b['execution_authorized']is False
def test_native_unit_preserves_all_protections():
    rt=f.load('_test_multiwin_runtime',ROOT/'tools/multiwin_returned_runtime.py')
    source=("\n".join(["[Service]","User=partho","Group=partho","ProtectSystem=strict","NoNewPrivileges=yes","PrivateTmp=yes","Restart=no","ExecStart=/usr/bin/python3 -s -B "+str(rt.BASE)+"/tools/colab_simple_runtime.py run",""])).encode()
    parent=NS(metadata=lambda:({},{}),unit_bytes=lambda scope:source)
    old=('/usr/bin/python3 -s -B '+str(rt.BASE)+'/tools/colab_simple_runtime.py run').encode()
    new=('/usr/bin/python3 -s -B '+str(rt.ROOT/rt.ENTRY)+' run').encode()
    assert rt.unit_bytes(parent)==source.replace(old,new)

def bind_test_scope(x,monkeypatch,base=object):
    from orchestrator import autonomy_limits as limits,manual_recovery, colab_simple_full as full
    from orchestrator import colab_notebook_delivery as delivery,manual_context
    monkeypatch.setattr(f,'frozen',lambda root:x.b)
    old=NS(frozen=lambda root:{},legacy=lambda root:NS(activate_correction_modules=lambda root:None),
           authorized_batch=lambda accounts,b,approval,prior:{'limit':128,'scoped_run_id':f.RUN})
    original_load=f.load
    def loader(name,path):
        if name=='_retained_multiwin_question':return old
        if name=='_returned_batch140':return NS(document=lambda root:{},allowance=lambda *a:{'limit':140,'purpose':'returned_colab','purpose_limit':4,'scoped_run_id':f.RUN})
        return original_load(name,path)
    monkeypatch.setattr(f,'load',loader)
    monkeypatch.setattr(limits,'global_limit',lambda batch,run:20 if run==f.RUN else 8)
    monkeypatch.setattr(limits,'local_limit',lambda store,run,policy:20 if run==f.RUN else 8)
    monkeypatch.setattr(limits,'daily_allowance',limits.daily_allowance)
    monkeypatch.setattr(limits,'cap_authority',limits.cap_authority)
    monkeypatch.setattr(manual_recovery,'role_limit',lambda store,run,stage:10 if run==f.RUN else 3)
    monkeypatch.setattr(full,'batch_allowance',lambda accounts,scope:{'limit':104,'scoped_run_id':f.RUN})
    monkeypatch.setattr(delivery,'prepare_variants',delivery.prepare_variants)
    monkeypatch.setattr(manual_context,'_notebook_patch_reading_copy',manual_context._notebook_patch_reading_copy)
    from orchestrator.autonomy_accounting import BatchAccounts
    monkeypatch.setattr(BatchAccounts,'reserve_scientific',BatchAccounts.reserve_scientific)
    x.correction=f.install_hook(base,ROOT,'a'*64)
    return limits,manual_recovery,full
def test_bound_selectors_require_grant_and_keep_other_owners(lane,monkeypatch):
    x=lane;limits,recovery,full=bind_test_scope(x,monkeypatch)
    with pytest.raises(ValueError,match='MISSING_APPROVED_GRANT'):limits.global_limit(x.driver.store.batch,f.RUN)
    f.resume(x.driver,x.b,'a'*64)
    assert limits.global_limit(x.driver.store.batch,f.RUN)==26
    assert limits.local_limit(x.driver.store,f.RUN,{})==26
    assert recovery.role_limit(x.driver.store,f.RUN,'run_spec_author')==13
    assert recovery.role_limit(x.driver.store,f.RUN,'run_spec_review')==12
    assert limits.global_limit(x.driver.store.batch,'other')==8
    assert limits.local_limit(x.driver.store,'other',{})==8
    assert recovery.role_limit(x.driver.store,'other','run_spec_author')==3
    with pytest.raises(ValueError,match='PREPARATION_ONLY'):recovery.role_limit(x.driver.store,f.RUN,'result_interpretation_author')
    assert full.batch_allowance(x.driver.store.batch,{'run_id':f.RUN})['process_continuation']['preserved_calls']==24
@pytest.mark.parametrize('stop',['run','batch','daily'])
def test_actual_reservation_still_refuses_caps(lane,monkeypatch,stop):
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator import preparation_followup
    x=lane;limits,recovery,full=bind_test_scope(x,monkeypatch);f.resume(x.driver,x.b,'a'*64)
    if stop=='run':
        for s,n in [('run_spec_author',13),('run_spec_review',12)]:add(x,s,n)
    # Unrelated past scientific calls fill batch, while same-day admin calls fill daily.
    if stop=='batch':
        for i in range(116):x.glob.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('other-'+str(i),'scientific','other',i,'2026-10-11','COMPLETE','{}','{}'))
    if stop=='daily':
        for i in range(26):x.glob.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('other-'+str(i),'implementation_review','other',i,'2026-10-13','COMPLETE','{}','{}'))
    monkeypatch.setattr(preparation_followup,'guard_admission',lambda *a:None)
    monkeypatch.setattr(limits,'scientific_batch_allowance',lambda *a:{'limit':140})
    from test_temporary_daily_cap import Clock
    from orchestrator import autonomy_accounting
    Clock.day='2026-10-13';monkeypatch.setattr(autonomy_accounting,'datetime',Clock)
    q=BatchAccounts(x.driver.store.batch.folder)
    before=snapshot(q.db,'autonomy_calls')
    try:
        with pytest.raises(ValueError,match='AUTONOMY_'+stop.upper()+'_CALL_LIMIT'):
            method=q.reserve_scientific
            if stop=='run':
                import inspect
                method=inspect.getclosurevars(type(q).reserve_scientific).nonlocals['previous_reserve'].__get__(q,type(q))
            method('fresh-cap-probe'if stop=='run'else f.sha((f.RUN+':run_spec_author:13').encode()),f.RUN,'run_spec_author','a'*40,{'workspace':str(x.driver.state.parent/'lane-scientific-workspaces/run_spec_author-13')})
        assert snapshot(q.db,'autonomy_calls')==before
    finally:q.db.close()

@pytest.mark.parametrize('bad',['identity','stage','attempt','source','workspace'])
def test_normal_reservation_wrapper_refuses_wrong_scope_before_charge(lane,monkeypatch,bad):
    from orchestrator.autonomy_accounting import BatchAccounts
    x=lane;bind_test_scope(x,monkeypatch);f.resume(x.driver,x.b,'a'*64)
    stage='run_spec_author';number=13;source='a'*40
    if bad=='stage':stage='result_interpretation_author'
    if bad=='attempt':number=14
    if bad=='source':source='b'*40
    ident=f.sha((f.RUN+':'+stage+':'+str(number)).encode())
    if bad=='identity':ident='wrong'
    work=x.driver.state.parent/'lane-scientific-workspaces'/(stage+'-'+str(number))
    if bad=='workspace':work=work.parent.parent/work.name
    q=BatchAccounts(x.driver.store.batch.folder);before=snapshot(q.db,'autonomy_calls')
    try:
        with pytest.raises(ValueError,match='MULTIWIN_RETURNED_'):
            q.reserve_scientific(ident,f.RUN,stage,source,{'workspace':str(work)})
        assert snapshot(q.db,'autonomy_calls')==before
    finally:q.db.close()

def test_actual_normal_call25_records_dated_and_process_authority(lane,monkeypatch):
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator import preparation_followup,autonomy_accounting
    from test_temporary_daily_cap import Clock
    x=lane;limits,recovery,full=bind_test_scope(x,monkeypatch);f.resume(x.driver,x.b,'a'*64)
    monkeypatch.setattr(preparation_followup,'guard_admission',lambda *a:None)
    monkeypatch.setattr(limits,'scientific_batch_allowance',lambda accounts,*a:full.batch_allowance(accounts,{'run_id':f.RUN}))
    Clock.day='2026-10-13';monkeypatch.setattr(autonomy_accounting,'datetime',Clock)
    q=BatchAccounts(x.driver.store.batch.folder);before=snapshot(q.db,'autonomy_calls')
    ident=f.sha((f.RUN+':run_spec_author:13').encode())
    try:
        result=q.reserve_scientific(ident,f.RUN,'run_spec_author','a'*40,
            {'workspace':str(x.driver.state.parent/'lane-scientific-workspaces/run_spec_author-13')})
        assert result['run_limit']==26 and result['batch_limit']==140 and result['daily_limit']==50
        row=q.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(ident,)).fetchone()
        binding=json.loads(row['binding'])
        assert row['round']==25 and binding['batch_continuation']['process_continuation']['scope_sha256']==f.DOCUMENT_SHA
        assert binding['batch_continuation']['process_continuation']['review_sha256']=='a'*64
        assert [dict(r)for r in q.db.execute('SELECT * FROM autonomy_calls WHERE id!=? ORDER BY rowid',(ident,))]==before
    finally:q.db.close()


@pytest.mark.parametrize("verdict,expected",[("REJECT",("BLOCKED","REVIEW_REJECTED")),("REVISE",("BLOCKED","BOUNDED_PROVENANCE_REVIEW_REVISE")),("APPROVE",("COMMIT_SPEC",None))])
def test_final_review_preserves_verdict_and_parks_unresolved(lane,monkeypatch,verdict,expected):
    from orchestrator import analysis_revisions as revisions
    previous=revisions.review_transition
    class Base:
        def _accept_completed(self,value):
            if verdict=="APPROVE":return "COMMIT_SPEC",None
            return revisions.review_transition({"verdict":verdict,"findings":[{"id":"genuine"}]},
                        "run_spec_review",12,offset=4)
    x=lane;bind_test_scope(x,monkeypatch,Base)
    assert x.correction()._accept_completed({"pending":{"stage":"run_spec_review","round":12}})==expected
    assert revisions.review_transition is previous

def test_returned_four_purpose_slots_cannot_be_borrowed(lane,monkeypatch):
    from orchestrator import scientific_batch140 as budget
    from orchestrator import colab_simple_full as full
    x=lane;bind_test_scope(x,monkeypatch);f.resume(x.driver,x.b,'a'*64)
    for i in range(104):
        x.glob.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                       ("baseline-"+str(i),"scientific","prior",1,"2026-10-12","COMPLETE","{}","{}"))
    scope=copy.deepcopy(budget.document(ROOT))
    scope["frozen_calls"]=[{"id":r["id"],"sha256":budget.sha(budget.canonical(dict(r)))}
                          for r in x.glob.execute("SELECT * FROM autonomy_calls ORDER BY id")]
    assert budget.allowance(x.driver.store.batch,f.RUN,scope,'a'*64)["purpose_used"]==0
    for i in range(4):
        x.glob.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
            ("returned-"+str(i),"scientific","colab-arm-b9d64a3c09b799bc10b0eba7",1,"2026-10-13","COMPLETE","{}","{}"))
    with pytest.raises(ValueError,match="PURPOSE_EXHAUSTED"):
        budget.allowance(x.driver.store.batch,f.RUN,scope,'a'*64)
    assert x.glob.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==132
