import copy,json,sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import colab_reader_recovery as m,private_records as pr,review_submission as rs
APPROVAL='a'*64

@pytest.fixture
def fixture(tmp_path):
    tmp_path=tmp_path/'recovery-fixture';pr.mkdir(tmp_path)
    lane=tmp_path/'lane';batch=tmp_path/'batch';work=tmp_path/'lane-scientific-workspaces/run_spec_review-1'
    for folder in (lane,batch,work):pr.mkdir(folder,parents=True)
    pr.write_text(lane/'lane.json','{"run_id":"'+m.RUN+'","max_calls":8}')
    final={'type':'result','session_id':'synthetic-session','is_error':True,'subtype':'error_max_turns','num_turns':30}
    pr.write_text(work/'console.log',json.dumps(final)+'\n');pr.write_text(work/rs.CONFIG,'{}')
    local=sqlite3.connect(lane/'jobs.sqlite',isolation_level=None);local.row_factory=sqlite3.Row
    global_db=sqlite3.connect(batch/'jobs.sqlite',isolation_level=None);global_db.row_factory=sqlite3.Row
    local.executescript('CREATE TABLE manual_calls(id TEXT,stage TEXT,attempt INTEGER,status TEXT,receipt TEXT); CREATE TABLE manual_state(id INTEGER,payload TEXT); CREATE TABLE events(id TEXT PRIMARY KEY,job TEXT,payload TEXT);')
    global_db.execute('CREATE TABLE autonomy_calls(id TEXT,status TEXT,receipt TEXT,kind TEXT,change_id TEXT,binding TEXT,round INTEGER)')
    for n,(stage,attempt,status,ident) in enumerate([('run_spec_author',1,'COMPLETE','author1'),('run_spec_author',2,'COMPLETE','author2'),(m.STAGE,1,'FAILED',m.FAILED)],1):
        receipt=json.dumps({'error_type':'TerminalSubmissionFailure','reason':'ACCEPTED_SUBMISSION_REQUIRED','cost':4.476676} if status=='FAILED' else {'outcome':'COMPLETE','cost':1})
        binding=json.dumps({'source':'b'*40,'run_id':m.RUN,'stage':stage})
        local.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(ident,stage,attempt,status,receipt))
        global_db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?)',(ident,status,receipt,'scientific',m.RUN,binding,n))
    value={'phase':'BLOCKED','reason':m.REASON,'rounds':{'run_spec_author':2},'pending':{'id':m.FAILED,'stage':m.STAGE,'round':1},'artifacts':[{'sha256':'c'*64}],'spec':'unchanged','notebook_revision_result':{'unchanged':True},'interventions':[]}
    raw=json.dumps(value,sort_keys=True);local.execute('INSERT INTO manual_state VALUES(1,?)',(raw,))
    f={'schema':'colab-review-reader-recovery/v1','run_id':m.RUN,'failed_call':m.FAILED,'next_review':2,'max_turns':30,'run_limit':8,'no_new_allowance':True,'lane':str(lane),'failed_workspace':str(work),'configuration_sha256':m.sha((lane/'lane.json').read_bytes()),'state_sha256':m.sha(raw.encode()),'original_state':value,'local_rows':[dict(r) for r in local.execute('SELECT * FROM manual_calls')],'global_rows':[dict(r) for r in global_db.execute('SELECT * FROM autonomy_calls')],'files':{x.name:{'bytes':len(x.read_bytes()),'sha256':m.sha(x.read_bytes())} for x in work.iterdir()}}
    store=NS(db=local,path=lane/'jobs.sqlite',batch=NS(db=global_db,path=batch/'jobs.sqlite',folder=batch))
    driver=NS(store=store,state=lane,config={'run_id':m.RUN},current=lambda:json.loads(local.execute('SELECT payload FROM manual_state').fetchone()[0]))
    yield NS(f=f,driver=driver,store=store,work=work,lane=lane,batch=batch)
    local.close();global_db.close()


def test_exact_restore_keeps_calls_charges_science_and_rounds(fixture):
    x=fixture;assert m.originals(x.store,x.f)
    assert m.activate(x.driver,x.f,APPROVAL)['model_calls']==0
    after=x.driver.current();assert after['phase']==m.STAGE and 'pending' not in after
    for key in ['artifacts','spec','notebook_revision_result','rounds']:assert after[key]==x.f['original_state'][key]
    assert [dict(r) for r in x.store.db.execute('SELECT * FROM manual_calls')]==x.f['local_rows']
    assert [dict(r) for r in x.store.batch.db.execute('SELECT * FROM autonomy_calls')]==x.f['global_rows']
    assert m.next_round(x.driver,after,x.f,APPROVAL,lambda v:99)==2
    assert (x.lane/m.EVENT/'original-state.json').read_text()==json.dumps(x.f['original_state'],sort_keys=True)
    assert (x.lane/m.EVENT/'COMPLETE.json').exists()
    with pytest.raises(ValueError):m.activate(x.driver,x.f,APPROVAL)

@pytest.mark.parametrize('damage',['configuration','local-charge','global-status','console','verdict','receipt','wrong-run','wrong-reason','extra-call','running-call','halt','batch-halt','intent','next-workspace','state','cap','turns','approval'])
def test_damage_refuses_without_state_or_accounting_mutation(fixture,damage):
    x=fixture;approval=APPROVAL
    if damage=='configuration':pr.write_text(x.lane/'lane.json','changed')
    elif damage=='local-charge':x.store.db.execute("UPDATE manual_calls SET receipt='{}' WHERE id=?",(m.FAILED,))
    elif damage=='global-status':x.store.batch.db.execute("UPDATE autonomy_calls SET status='COMPLETE' WHERE id=?",(m.FAILED,))
    elif damage=='console':pr.write_text(x.work/'console.log','changed')
    elif damage=='verdict':pr.write_text(x.work/'review.json','{"verdict":"REJECT"}')
    elif damage=='receipt':pr.write_text(x.work/rs.RECORD,'{}')
    elif damage=='wrong-run':x.driver.config['run_id']='other'
    elif damage=='wrong-reason':x.f['original_state']['reason']='REJECT'
    elif damage=='extra-call':x.store.db.execute("INSERT INTO manual_calls VALUES('other','run_spec_author',3,'COMPLETE','{}')")
    elif damage=='running-call':x.store.batch.db.execute("INSERT INTO autonomy_calls(id,status) VALUES('other','RUNNING')")
    elif damage=='halt':pr.write_text(x.lane/'HALT','halt')
    elif damage=='batch-halt':pr.write_text(x.batch/'HALT','halt')
    elif damage=='intent':pr.mkdir(x.lane/m.EVENT)
    elif damage=='next-workspace':pr.mkdir(x.work.with_name('run_spec_review-2'))
    elif damage=='state':x.store.db.execute("UPDATE manual_state SET payload='{}'")
    elif damage=='cap':x.f['run_limit']=9
    elif damage=='turns':x.f['max_turns']=31
    else:approval='not-approved'
    before=x.store.db.execute('SELECT payload FROM manual_state').fetchone()[0]
    calls=[tuple(r) for r in x.store.db.execute('SELECT * FROM manual_calls')]
    with pytest.raises((ValueError,KeyError)):m.activate(x.driver,x.f,approval)
    assert x.store.db.execute('SELECT payload FROM manual_state').fetchone()[0]==before
    assert calls==[tuple(r) for r in x.store.db.execute('SELECT * FROM manual_calls')]
    assert not (x.lane/m.EVENT/'COMPLETE.json').exists()

@pytest.mark.parametrize('kind',['submission','success','missing-session','multiple','not-final'])
def test_native_failure_must_be_unsubmitted_and_terminal(fixture,kind):
    x=fixture;event=json.loads((x.work/'console.log').read_text());events=[event]
    if kind=='submission':events.insert(0,{'type':'assistant','message':{'content':[{'type':'tool_use','name':'mcp__review__submit_review'}]}})
    elif kind=='success':event['subtype']='success'
    elif kind=='missing-session':event.pop('session_id')
    elif kind=='multiple':events.append(event)
    else:events.append({'type':'assistant'})
    raw=''.join(json.dumps(e)+'\n' for e in events).encode();pr.write_bytes(x.work/'console.log',raw)
    x.f['files']['console.log']={'bytes':len(raw),'sha256':m.sha(raw)}
    with pytest.raises(ValueError):m.originals(x.store,x.f)


def test_next_review_requires_grant_and_unchanged_science(fixture):
    x=fixture
    with pytest.raises(ValueError,match='GRANT_REQUIRED'):m.next_round(x.driver,dict(x.driver.current(),phase=m.STAGE),x.f,APPROVAL,lambda v:99)
    m.activate(x.driver,x.f,APPROVAL)
    value=x.driver.current();value['spec']='changed'
    x.store.db.execute('UPDATE manual_state SET payload=?',(json.dumps(value),))
    with pytest.raises(ValueError,match='SCIENTIFIC_STATE_CHANGED'):m.next_round(x.driver,value,x.f,APPROVAL,lambda v:99)
    assert m.next_round(x.driver,dict(value,phase='other'),x.f,APPROVAL,lambda v:99)==99


def test_retained_sequence_exact_local_global_and_unrelated_refusal(fixture):
    x=fixture;scope={'source_sha':'b'*40,'lanes':{'colab_preparation':{'run_id':m.RUN,'state':str(x.lane)}},'ledger':str(x.batch)}
    row=x.f['global_rows'][-1];item=x.f['local_rows'][-1]
    assert m.retained_review(scope,row,item,x.f)
    assert not m.retained_review(scope,dict(row,id='other'),item,x.f)
    for changed in [dict(row,status='COMPLETE'),dict(row,receipt='{}')]:
        with pytest.raises(ValueError):m.retained_review(scope,changed,item,x.f)
    with pytest.raises(ValueError):m.retained_review(scope,row,dict(item,status='COMPLETE'),x.f)


def test_hook_preserves_original_guard_and_completion_qualification(fixture,monkeypatch):
    from orchestrator import preparation_interleaving as pi,stocktake_review_recovery as rr
    x=fixture;events=[]
    class Driver:
        def __init__(self):self.__dict__.update(x.driver.__dict__)
        def guard(self):events.append('guard')
        def advance(self):events.append('ordinary');return 'ordinary'
        def model_round_number(self,v):return 99
    module=NS(AnalysisDriver=Driver)
    monkeypatch.setattr(pi,'_REVIEW_TERMINAL',None)
    monkeypatch.setattr(rr,'completion',lambda batch,run:['prior'])
    m.install_hook(module,x.f,APPROVAL,'recover');d=module.AnalysisDriver()
    assert d.advance()['status']=='RESTORED_REVIEW2_NO_CALL' and events==['guard']
    assert rr.completion(x.store.batch,'other')==['prior']
    assert rr.completion(x.store.batch,m.RUN)==['prior',m.FAILED]
    x.store.db.execute('DELETE FROM events')
    with pytest.raises(ValueError,match='GRANT_REQUIRED'):rr.completion(x.store.batch,m.RUN)


def test_failed_transaction_preserves_intent_for_reconciliation(fixture,monkeypatch):
    x=fixture;original=m.originals;calls=[]
    def check(*args):
        calls.append(True)
        if len(calls)>1:raise ValueError('synthetic race')
        return original(*args)
    monkeypatch.setattr(m,'originals',check)
    with pytest.raises(ValueError,match='race'):m.activate(x.driver,x.f,APPROVAL)
    assert x.driver.current()==x.f['original_state']
    assert (x.lane/m.EVENT/'intent.json').exists() and not (x.lane/m.EVENT/'COMPLETE.json').exists()
    assert x.store.db.execute('SELECT count(*) FROM events').fetchone()[0]==0


from test_preparation_interleaving import admitted_history,complete_fixture_call

def test_real_shared_admission_counts_original_failure_and_next_review(admitted_history,fixture,monkeypatch):
    from orchestrator import preparation_interleaving as pi
    scope,history,batch,locals,overlay=admitted_history
    local=locals['colab_preparation'];run=scope['lanes']['colab_preparation']['run_id']
    for stage,attempt in [('run_spec_author',1),('run_spec_author',2),(m.STAGE,1)]:
        _,failed=complete_fixture_call(scope,batch,local,'colab_preparation',stage,attempt)
    receipt=json.dumps({'error_type':'TerminalSubmissionFailure','reason':'ACCEPTED_SUBMISSION_REQUIRED','cost':4.476676})
    for db,table in [(local.db,'manual_calls'),(batch.db,'autonomy_calls')]:db.execute('UPDATE '+table+" SET status='FAILED',receipt=? WHERE id=?",(receipt,failed))
    monkeypatch.setattr(m,'RUN',run);monkeypatch.setattr(m,'FAILED',failed)
    lane=Path(local.path).parent;work=lane.parent/'lane-scientific-workspaces/run_spec_review-1'
    pr.copytree(fixture.work,work)
    f=copy.deepcopy(fixture.f)
    f.update(run_id=run,failed_call=failed,lane=str(lane),failed_workspace=str(work),configuration_sha256=m.sha((lane/'lane.json').read_bytes()),local_rows=[dict(r) for r in local.db.execute('SELECT * FROM manual_calls')],global_rows=[dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls WHERE change_id=?',(run,))])
    # This synthetic fixture has a different directory name; production is lane.
    # Use the actual pinned lane path in the scope, never infer a different ledger.
    monkeypatch.setattr(pi,'_REVIEW_TERMINAL',lambda sc,row,item:m.retained_review(sc,row,item,f))
    before=[dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls')]
    nextid=pi.identity(run,m.STAGE,2)
    admission=batch.reserve_scientific(nextid,run,m.STAGE,scope['source_sha'],{})
    assert admission['run_limit']==8 and admission['batch_limit']==95
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls WHERE change_id=?',(run,)).fetchone()[0]==4
    assert dict(batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(failed,)).fetchone())==f['global_rows'][-1]
    assert [dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls')][:-1]==before
