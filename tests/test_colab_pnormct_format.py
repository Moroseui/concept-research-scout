import copy,json,sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import colab_pnormct_format as f,colab_arm_question as q
from test_colab_static_feedback import feedback,call

@pytest.fixture
def lane(tmp_path,monkeypatch):
    state=tmp_path/'lane';state.mkdir(mode=0o700)
    config={'run_id':q.RUN};(state/'lane.json').write_text(json.dumps(config))
    work=tmp_path/'author1';work.mkdir(mode=0o700)
    (work/'SPEC.proposed.md').write_text('preserved specification')
    (work/'notebook.patch.json').write_text(json.dumps({'edits':[{'replacement':['scientific bytes\n']}]}))
    for p in [state/'lane.json',*work.iterdir()]:p.chmod(0o600)
    db=sqlite3.connect(':memory:',isolation_level=None);db.row_factory=sqlite3.Row
    db.executescript('CREATE TABLE manual_calls(id TEXT PRIMARY KEY,status TEXT,receipt TEXT);'
        'CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT);'
        'CREATE TABLE manual_account(id INTEGER PRIMARY KEY,payload TEXT);'
        'CREATE TABLE events(id TEXT PRIMARY KEY,job TEXT,payload TEXT);')
    g=sqlite3.connect(':memory:',isolation_level=None);g.row_factory=sqlite3.Row
    g.execute('CREATE TABLE autonomy_calls(id TEXT PRIMARY KEY,status TEXT,receipt TEXT)')
    row={'id':f.CALL,'status':'COMPLETE','receipt':'preserved charge and outputs'}
    for store,table in [(db,'manual_calls'),(g,'autonomy_calls')]:store.execute('INSERT INTO '+table+' VALUES(:id,:status,:receipt)',row)
    value={'phase':'BLOCKED','reason':f.REASON,'rounds':{},'interventions':[],
           'pending':{'id':f.CALL,'stage':'run_spec_author','round':1},'artifacts':[]}
    db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps(value),))
    db.execute("INSERT INTO manual_account VALUES(1,'unchanged allowance usage')")
    driver=NS(state=state,config=config,store=NS(db=db,batch=NS(db=g,folder=tmp_path/'batch')),
              current=lambda:json.loads(db.execute('SELECT payload FROM manual_state').fetchone()[0]))
    frozen={'run_id':q.RUN,'lane':str(state),'config_sha256':q.sha((state/'lane.json').read_bytes()),
            'local_calls':[dict(db.execute('SELECT * FROM manual_calls').fetchone())],
            'global_row':dict(g.execute('SELECT * FROM autonomy_calls').fetchone()),
            'state_row':dict(db.execute('SELECT * FROM manual_state').fetchone()),
            'account_row':dict(db.execute('SELECT * FROM manual_account').fetchone()),
            'workspace':str(work),'files':{p.name:{'sha256':q.sha(p.read_bytes()),'bytes':p.stat().st_size}for p in work.iterdir()}}
    monkeypatch.setattr(q,'validate',lambda *args: {'run_id':q.RUN})
    yield NS(driver=driver,frozen=frozen,db=db,g=g,work=work)
    db.close();g.close()

def test_same_call_checker_catches_list_then_accepts_string_on_synthetic_code(tmp_path):
    patch,folder=feedback(tmp_path)
    text=patch['edits'][0]['replacement']
    patch['edits'][0]['replacement']=text.splitlines(keepends=True)
    (tmp_path/'notebook.patch.json').write_text(json.dumps(patch))
    first=call(tmp_path,folder)
    assert first.returncode==1 and 'AUTHOR_PATCH_EDIT_SCHEMA' in first.stdout
    patch['edits'][0]['replacement']=text
    (tmp_path/'notebook.patch.json').write_text(json.dumps(patch))
    second=call(tmp_path,folder)
    assert second.returncode==0 and 'FORMAT_PASS_NOT_SCIENTIFIC_APPROVAL' in second.stdout

def test_recovery_preserves_outputs_receipts_account_and_one_failed_attempt(lane):
    x=lane;before={p.name:p.read_bytes()for p in x.work.iterdir()}
    result=f.recover(x.driver,x.frozen,'a'*64)
    assert result['new_allowance']==result['model_calls']==0 and result['calls_preserved']==1
    assert [dict(r)for r in x.db.execute('SELECT * FROM manual_calls')]==x.frozen['local_calls']
    assert dict(x.db.execute('SELECT * FROM manual_account').fetchone())==x.frozen['account_row']
    assert dict(x.g.execute('SELECT * FROM autonomy_calls').fetchone())==x.frozen['global_row']
    assert before=={p.name:p.read_bytes()for p in x.work.iterdir()}
    assert x.driver.current()['phase']=='run_spec_author' and 'pending'not in x.driver.current()
    assert x.driver.current()['rounds']=={}
    with pytest.raises(ValueError):f.recover(x.driver,x.frozen,'a'*64)

@pytest.mark.parametrize('damage',['local','global','new','live','account','state','config','output','accepted','submission','halt','intent'])
def test_recovery_refuses_damage_without_changing_original_records(lane,damage):
    x=lane
    if damage=='local':x.db.execute("UPDATE manual_calls SET status='UNCERTAIN'")
    elif damage=='global':x.g.execute("UPDATE autonomy_calls SET receipt='changed'")
    elif damage=='new':x.db.execute("INSERT INTO manual_calls VALUES('new','COMPLETE','{}')")
    elif damage=='live':x.g.execute("INSERT INTO autonomy_calls VALUES('live','RUNNING','{}')")
    elif damage=='account':x.db.execute("UPDATE manual_account SET payload='changed'")
    elif damage=='state':x.db.execute("UPDATE manual_state SET payload='{}'")
    elif damage=='config':(x.driver.state/'lane.json').write_text('{}')
    elif damage=='output':(x.work/'SPEC.proposed.md').write_text('changed')
    elif damage=='accepted':x.db.execute('INSERT INTO events VALUES(?,?,?)',('author-accepted:'+f.CALL,q.RUN,'{}'))
    elif damage=='submission':(x.work/'.author-submission.json').write_text('{}')
    elif damage=='halt':(x.driver.state/'HALT').touch()
    else:(x.driver.state/f.EVENT).mkdir()
    before=list(x.db.iterdump());global_before=list(x.g.iterdump())
    with pytest.raises(ValueError):f.recover(x.driver,x.frozen,'a'*64)
    assert list(x.db.iterdump())==before and list(x.g.iterdump())==global_before

@pytest.mark.parametrize('field,value',[('reason','REVIEW_REJECTED'),('phase','run_spec_review'),
    ('pending',{'id':'wrong','stage':'run_spec_author','round':1})])
def test_cannot_reclassify_a_scientific_verdict_or_different_failure(lane,field,value):
    v=lane.driver.current();v[field]=value
    with pytest.raises(ValueError):f.restored(v,lane.frozen)

def test_feedback_hook_keeps_exact_inputs_and_provenance(tmp_path,monkeypatch):
    saved={'proof':'test'}
    monkeypatch.setattr(f,'document',lambda root:saved)
    monkeypatch.setattr(f,'check',lambda *args:True)
    inputs={'.colab-feedback/check.py':b'unchanged existing checker'}
    monkeypatch.setattr(f,'feedback_files',lambda *args:inputs)
    class Base:
        config={'run_id':q.RUN}
        def task(self,stage,value):return 'Original scientific task. '
        def prepare_input(self,value,stage,work):return self.task(stage,value),{'workspace_files':[]}
    driver=f.corrected(Base,tmp_path,'a'*64)()
    body,measurement=driver.prepare_input({},'run_spec_author',tmp_path/'work')
    assert 'replacement to be a STRING' in body and 'at most12' in body and 'no submit_author MCP tool' in body
    assert (tmp_path/'work/.colab-feedback/check.py').read_bytes()==inputs['.colab-feedback/check.py']
    assert measurement['workspace_files'][0]['sha256']==q.sha(inputs['.colab-feedback/check.py'])
    assert not hasattr(driver,'_pnormct_feedback')
    with pytest.raises(ValueError,match='FEEDBACK_EXISTS'):driver.prepare_input({},'run_spec_author',tmp_path/'work')

def test_native_unit_keeps_every_other_directive():
    from tools import colab_pnormct_format_runtime as rt
    raw=('User=partho\nGroup=partho\nExecStart=/usr/bin/python3 -s -B '+str(rt.BASE)+'/tools/colab_pnormct_runtime.py run\nRestart=no\nReadWritePaths=/fixed/work\n').encode()
    parent=NS(metadata=lambda:({},{}),unit_bytes=lambda scope:raw)
    assert rt.unit_bytes(parent).replace(str(rt.ROOT/rt.ENTRY).encode(),str(rt.BASE/'tools/colab_pnormct_runtime.py').encode())==raw

def test_actual_frozen_failure_is_counted_and_unaccepted():
    checkpoint=f.document(Path(__file__).resolve().parents[1])
    assert checkpoint['local_calls'][0]['status']=='COMPLETE'
    assert checkpoint['global_row']['id']==f.CALL and checkpoint['next_author']==2
    assert checkpoint['new_allowance']==0
