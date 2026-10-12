import copy
import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import colab_arm_preparation as f

def database(path):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    db=sqlite3.connect(path,isolation_level=None);db.row_factory=sqlite3.Row
    db.executescript("""
      CREATE TABLE manual_calls(id TEXT PRIMARY KEY,stage TEXT,attempt INTEGER,status TEXT,receipt TEXT);
      CREATE TABLE autonomy_calls(id TEXT PRIMARY KEY,kind TEXT,change_id TEXT,round INTEGER,day TEXT,status TEXT,binding TEXT,receipt TEXT);
      CREATE TABLE autonomy_runs(id TEXT PRIMARY KEY,binding TEXT,status TEXT);
      CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT);
      CREATE TABLE manual_account(id INTEGER PRIMARY KEY,payload TEXT);
      CREATE TABLE events(id TEXT PRIMARY KEY,job TEXT,payload TEXT);
    """)
    return db

@pytest.fixture
def lane(tmp_path,monkeypatch):
    state=tmp_path/'work/lane';state.mkdir(parents=True,mode=0o700)
    db=database(state/'jobs.sqlite');glob=database(tmp_path/'batch/jobs.sqlite')
    config={'run_id':f.RUN,'batch_ledger':str(tmp_path/'batch'),'context':str(state/'context')}
    value={'phase':'COMMIT_SPEC','rounds':{'run_spec_author':9,'run_spec_review':8,
        'result_interpretation_author':1},'interventions':[],'artifacts':[],
        'review':str(state.parent/'lane-scientific-workspaces/run_spec_review-8/review.json')}
    db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps(value),))
    db.execute('INSERT INTO manual_account VALUES(1,?)',('unchanged allowance',))
    local=[];global_rows=[]
    stages=[('run_spec_author',i) for i in range(1,10)]+[('run_spec_review',i) for i in range(1,9)]+[('result_interpretation_author',1)]
    for index,(stage,attempt) in enumerate(stages):
        ident=f.CALL if (stage,attempt)==('run_spec_review',8) else 'prior-'+str(index)
        row=dict(id=ident,stage=stage,attempt=attempt,status='COMPLETE',receipt='{}')
        db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',tuple(row.values()));local.append(row)
        grow=dict(id=ident,kind='scientific',change_id=f.RUN,round=index+1,day='2026-10-12',status='COMPLETE',binding='{}',receipt='{}')
        glob.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',tuple(grow.values()));global_rows.append(grow)
    owner=dict(id=f.RUN,binding='original owner',status='ACTIVE')
    glob.execute('INSERT INTO autonomy_runs VALUES(?,?,?)',tuple(owner.values()))
    review=state.parent/'lane-scientific-workspaces/run_spec_review-8/review.json'
    review.parent.mkdir(parents=True,mode=0o700);review.write_text(json.dumps({'verdict':'APPROVE','findings':[]}))
    b={'config':config,'files':{str(review.relative_to(state.parent)):f.sha(review.read_bytes())},
       'local_rows':local,'global_rows':global_rows,'owner':owner,
       'account_row':dict(db.execute('SELECT * FROM manual_account').fetchone()),
       'state_row':dict(db.execute('SELECT * FROM manual_state').fetchone()),
       'operator_sha256':'o'*64}
    store=SimpleNamespace(db=db,path=state/'jobs.sqlite',batch=SimpleNamespace(db=glob))
    driver=SimpleNamespace(config=config,state=state,store=store,
        current=lambda:json.loads(db.execute('SELECT payload FROM manual_state').fetchone()[0]),
        model_round_number=lambda value:db.execute('SELECT count(*) FROM manual_calls WHERE stage=?',(value['phase'],)).fetchone()[0]+1)
    from orchestrator import experiment_approval
    monkeypatch.setattr(experiment_approval,'verified_review_delivery',lambda *args:(None,None,review.read_bytes(),None,None,None))
    yield SimpleNamespace(driver=driver,b=b,db=db,glob=glob,review=review,value=value)
    db.close();glob.close()

def snapshot(db,table):
    return [dict(row) for row in db.execute('SELECT * FROM '+table+' ORDER BY rowid')]

def test_question_transition_retains_every_row_and_allowance(lane):
    x=lane;before={name:snapshot(db,name) for db,name in [(x.db,'manual_calls'),(x.db,'manual_account'),(x.glob,'autonomy_calls'),(x.glob,'autonomy_runs')]}
    result=f.resume(x.driver,x.b,'a'*64)
    assert result=={'status':'READY_MULTIWIN_AUTHOR10','calls_preserved':18,'new_calls':0,'new_allowance':0}
    after=x.driver.current();assert after['phase']=='run_spec_author' and after['reason']=='NEW_OPERATOR_ARM_QUESTION'
    assert after['rounds']==x.value['rounds']
    assert after['interventions'][-1]['reviewer_revise'] is False
    for db,name in [(x.db,'manual_calls'),(x.db,'manual_account'),(x.glob,'autonomy_calls'),(x.glob,'autonomy_runs')]:
        assert snapshot(db,name)==before[name]
    assert f.grant(x.driver,x.b,'a'*64)['maximum_new_calls']==2
    with pytest.raises(ValueError):f.resume(x.driver,x.b,'a'*64)

@pytest.mark.parametrize('change',['local-call','global-call','owner','account','state','file','config','live'])
def test_original_drift_refuses_before_any_transition(lane,change):
    x=lane
    if change=='local-call':x.db.execute("UPDATE manual_calls SET receipt='changed' WHERE id='prior-0'")
    elif change=='global-call':x.glob.execute("UPDATE autonomy_calls SET receipt='changed' WHERE id='prior-0'")
    elif change=='owner':x.glob.execute("UPDATE autonomy_runs SET status='COMPLETE'")
    elif change=='account':x.db.execute("UPDATE manual_account SET payload='changed'")
    elif change=='state':x.db.execute("UPDATE manual_state SET payload='{}'")
    elif change=='file':x.review.write_text('{}')
    elif change=='config':x.driver.config={**x.driver.config,'unexpected':True}
    elif change=='live':x.glob.execute("INSERT INTO autonomy_calls VALUES('live','scientific','other',1,'2026-10-12','RUNNING','{}','{}')")
    with pytest.raises(ValueError):f.resume(x.driver,x.b,'a'*64)
    assert not (x.driver.state/f.EVENT).exists()

def test_native_review_authenticity_is_required(lane,monkeypatch):
    from orchestrator import experiment_approval
    def refuse(*args):raise ValueError('INVALID_NATIVE_REVIEW')
    monkeypatch.setattr(experiment_approval,'verified_review_delivery',refuse)
    with pytest.raises(ValueError,match='INVALID_NATIVE_REVIEW'):f.resume(lane.driver,lane.b,'a'*64)
    assert not (lane.driver.state/f.EVENT).exists()

@pytest.mark.parametrize('bad',[None,'','x'*64,'a'*63])
def test_no_unbound_implementation_reference(lane,bad):
    with pytest.raises(ValueError,match='APPROVAL'):f.resume(lane.driver,lane.b,bad)

@pytest.mark.parametrize('stage,number',[('run_spec_author',11),('run_spec_review',10),('result_interpretation_author',2)])
def test_other_scientific_call_cannot_borrow_question(lane,stage,number):
    x=lane;f.resume(x.driver,x.b,'a'*64)
    x.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',('new',stage,number,'COMPLETE','{}'))
    with pytest.raises(ValueError,match='QUESTION_TWO_CALL_BOUND'):f.grant(x.driver,x.b,'a'*64)

def test_only_author10_review9_are_the_remaining_question_calls(lane):
    x=lane;f.resume(x.driver,x.b,'a'*64)
    for stage,number in [('run_spec_author',10),('run_spec_review',9)]:
        x.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(f.sha((f.RUN+':'+stage+':'+str(number)).encode()),stage,number,'COMPLETE','{}'))
        f.grant(x.driver,x.b,'a'*64)
    x.db.execute("INSERT INTO manual_calls VALUES('extra','run_spec_author',9,'COMPLETE','{}')")
    with pytest.raises(ValueError,match='QUESTION_TWO_CALL_BOUND'):f.grant(x.driver,x.b,'a'*64)

def test_real_round_probe_is_rolled_back(lane,monkeypatch):
    from orchestrator import manual_recovery
    x=lane;seen=[]
    monkeypatch.setattr(f,'frozen',lambda root:x.b)
    def role(store,run,stage):
        seen.append((run,stage))
        return 10 if stage=='run_spec_author' else 9
    monkeypatch.setattr(manual_recovery,'role_limit',role)
    before=snapshot(x.db,'manual_state')
    result=f.probe_admission(x.driver,Path('/unused'),'a'*64)
    assert result['status']=='PASS' and result['reservations']==0
    assert len(seen)==2 and snapshot(x.db,'manual_state')==before
    assert not x.db.in_transaction and not (x.driver.state/f.EVENT).exists()

def test_refused_native_role_probe_preserves_state(lane,monkeypatch):
    from orchestrator import manual_recovery
    x=lane;monkeypatch.setattr(f,'frozen',lambda root:x.b)
    monkeypatch.setattr(manual_recovery,'role_limit',lambda *args:0)
    before=snapshot(x.db,'manual_state')
    with pytest.raises(ValueError,match='NATIVE_ROLE_LIMIT'):f.probe_admission(x.driver,Path('/unused'),'a'*64)
    assert snapshot(x.db,'manual_state')==before and not x.db.in_transaction

def test_pinned_real_scope_binds_operator_batch_increase_and_unchanged_other_caps():
    root=Path(__file__).resolve().parents[1];b=f.frozen(root)
    assert (b['run_limit'],b['batch_limit'],b['daily_limit'],b['maximum_new_calls'])==(20,128,50,2)
    assert len(b['local_rows'])==len(b['global_rows'])==18 and b['scientific_count']==104
    assert b['execution_authorized'] is False


def runtime_module():
    import importlib.util
    path=Path(__file__).resolve().parents[1]/"tools/colab_arm_preparation_runtime.py"
    spec=importlib.util.spec_from_file_location("_test_arm_runtime",path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result

def test_native_unit_changes_only_fixed_entry_command():
    rt=runtime_module()
    source=("[Service]\nUser=partho\nGroup=partho\nProtectSystem=strict\n"
            "NoNewPrivileges=yes\nPrivateTmp=yes\nRestart=no\n"
            "ExecStart=/usr/bin/python3 -s -B "+str(rt.BASE)+"/tools/colab_simple_runtime.py run\n").encode()
    parent=SimpleNamespace(metadata=lambda:({},{}),unit_bytes=lambda scope:source)
    out=rt.unit_bytes(parent)
    old=("/usr/bin/python3 -s -B "+str(rt.BASE)+"/tools/colab_simple_runtime.py run").encode()
    new=("/usr/bin/python3 -s -B "+str(rt.ROOT/rt.ENTRY)+" run").encode()
    assert out==source.replace(old,new)

@pytest.mark.parametrize('verdict,findings',[('REVISE',[]),('REJECT',[]),('APPROVE',[{'id':'unresolved'}])])
def test_runtime_refuses_unapproved_or_unresolved_implementation(tmp_path,monkeypatch,verdict,findings):
    from orchestrator import autonomy_review,manual_host_guard
    rt=runtime_module()
    monkeypatch.setattr(manual_host_guard,'trusted',lambda p:Path(p))
    monkeypatch.setattr(autonomy_review,'verify_result',lambda p:{'verdict':verdict,'change_id':rt.CHANGE})
    (tmp_path/'report.md').write_text(json.dumps({'findings':findings}))
    (tmp_path/'packet-manifest.json').write_text(json.dumps({'source_files':{}}))
    with pytest.raises(ValueError,match='INDEPENDENT_APPROVE'):rt.reviewed(tmp_path)

def test_runtime_requires_full_component_and_new_inputs(tmp_path,monkeypatch):
    from orchestrator import autonomy_review,manual_host_guard
    rt=runtime_module()
    monkeypatch.setattr(manual_host_guard,'trusted',lambda p:Path(p))
    monkeypatch.setattr(autonomy_review,'verify_result',lambda p:{'verdict':'APPROVE','change_id':rt.CHANGE})
    (tmp_path/'report.md').write_text('{"findings":[]}')
    (tmp_path/'packet-manifest.json').write_text(json.dumps({'source_files':{}}))
    with pytest.raises(ValueError,match='WHOLE_COMPONENT'):rt.reviewed(tmp_path)


def test_exact_successor_review_limit_needs_reviewed_question_record(lane):
    x=lane
    with pytest.raises(FileNotFoundError):
        f.bounded_review_limit(x.driver.store,f.RUN,'run_spec_review',x.b,'a'*64,lambda *args:8)
    f.resume(x.driver,x.b,'a'*64)
    assert f.bounded_review_limit(x.driver.store,f.RUN,'run_spec_review',x.b,'a'*64,lambda *args:8)==9
    assert f.bounded_review_limit(x.driver.store,'other','run_spec_review',x.b,'a'*64,lambda *args:3)==3
    assert f.bounded_review_limit(x.driver.store,f.RUN,'run_spec_author',x.b,'a'*64,lambda *args:10)==10
    with pytest.raises(ValueError,match='PRIOR_REVIEW_LIMIT_CHANGED'):
        f.bounded_review_limit(x.driver.store,f.RUN,'run_spec_review',x.b,'a'*64,lambda *args:0)
    with pytest.raises(ValueError,match='QUESTION_APPROVAL'):
        f.bounded_review_limit(x.driver.store,f.RUN,'run_spec_review',x.b,'b'*64,lambda *args:8)
