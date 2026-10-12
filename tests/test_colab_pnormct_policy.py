import copy,json,sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import colab_pnormct_policy as p, colab_arm_question as q
from orchestrator import analysis_revisions as revisions, manual_recovery

@pytest.fixture
def lane(tmp_path,monkeypatch):
    root=Path(__file__).resolve().parents[1]
    config={'run_id':q.RUN,'backend':'analysis','item_number':4,'root':str(root),
            'review_contract':'bound-review/v1','revision_policy':revisions.POLICY}
    (tmp_path/'lane.json').write_text(json.dumps(config))
    db=sqlite3.connect(tmp_path/'jobs.sqlite',isolation_level=None);db.row_factory=sqlite3.Row
    db.executescript('CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT);'
                    'CREATE TABLE manual_calls(id TEXT PRIMARY KEY,stage TEXT,attempt INTEGER,status TEXT,receipt TEXT);'
                    'CREATE TABLE events(id TEXT PRIMARY KEY,run_id TEXT,payload TEXT);')
    state={'phase':'BLOCKED','reason':'ValueError: ANALYSIS_REVISION_POLICY_SCOPE',
           'rounds':{},'interventions':[],'artifacts':[]}
    db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps(state),))
    batch=sqlite3.connect(':memory:');batch.execute('CREATE TABLE autonomy_calls(id TEXT,status TEXT)')
    store=NS(path=tmp_path/'jobs.sqlite',db=db,batch=NS(db=batch,folder=tmp_path/'batch'))
    driver=NS(state=tmp_path,config=config,store=store,
              current=lambda:json.loads(db.execute('SELECT payload FROM manual_state').fetchone()[0]))
    frozen={'run_id':q.RUN,'lane':str(tmp_path),'config_sha256':q.sha((tmp_path/'lane.json').read_bytes()),
            'state_row':dict(db.execute('SELECT * FROM manual_state').fetchone()),'calls':[]}
    calls=[]
    def validate(store,run):
        assert run==q.RUN;calls.append(run);return {'run_id':run}
    monkeypatch.setattr(q,'validate',validate)
    # Restore installed hooks automatically after every synthetic test.
    monkeypatch.setattr(revisions,'enabled',revisions.enabled)
    monkeypatch.setattr(revisions,'instructions',revisions.instructions)
    yield NS(driver=driver,frozen=frozen,store=store,config=config,root=tmp_path,checks=calls)
    db.close();batch.close()

def connect(x):
    p.connect()
    return manual_recovery.role_limit(x.store,q.RUN,'run_spec_author')

def test_real_role_limit_author_and_reviewer_chain(lane):
    x=lane
    with pytest.raises(ValueError,match='ANALYSIS_REVISION_POLICY_SCOPE'):
        manual_recovery.role_limit(x.store,q.RUN,'run_spec_author')
    assert connect(x)==1
    assert manual_recovery.role_limit(x.store,q.RUN,'run_spec_review')==4
    assert x.checks
    assert 'Approved UTC-day policy, run20' in revisions.instructions(x.store,q.RUN)

@pytest.mark.parametrize('field,value',[('run_id','wrong'),('backend','wrong'),('item_number',2),
    ('review_contract','wrong'),('revision_policy',{})])
def test_wrong_policy_scope_refused(lane,field,value):
    x=lane;x.config[field]=value
    (x.root/'lane.json').write_text(json.dumps(x.config));p.connect()
    with pytest.raises(ValueError,match='POLICY_CONFIGURATION'):revisions.enabled(x.store,q.RUN)

def test_unrelated_run_keeps_legacy_refusal(lane):
    x=lane;p.connect()
    with pytest.raises(ValueError,match='ANALYSIS_REVISION_POLICY_SCOPE'):
        revisions.enabled(x.store,'another-run')

def test_exact_question_validation_not_skipped(lane,monkeypatch):
    def refuse(*args):raise ValueError('bound-question-refused')
    monkeypatch.setattr(q,'validate',refuse)
    p.connect()
    with pytest.raises(ValueError,match='bound-question-refused'):revisions.enabled(lane.store,q.RUN)

def test_failed_attempt_limit_and_no_offset_reset(lane):
    x=lane;connect(x)
    for i in range(4):
        x.store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',
            ('failed'+str(i),'run_spec_author',i+1,'FAILED','{}'))
    assert manual_recovery.role_limit(x.store,q.RUN,'run_spec_author')==4
    assert x.store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==4

def test_recovery_preserves_original_once_and_zero_calls(lane):
    x=lane;before=x.frozen['state_row']['payload'];p.connect()
    result=p.recover(x.driver,x.frozen,'a'*64)
    assert result['model_calls']==result['new_allowance']==0
    assert (x.root/p.EVENT/'original-state.json').read_text()==before
    after=x.driver.current()
    assert after['phase']=='run_spec_author' and after['artifacts']==[]
    assert after['rounds']=={} and len(after['interventions'])==1
    assert not x.store.db.execute('SELECT * FROM manual_calls').fetchall()
    with pytest.raises(ValueError):p.recover(x.driver,x.frozen,'a'*64)

@pytest.mark.parametrize('damage',['pending','reason','call','global_running','config','halt','intent'])
def test_recovery_refuses_changed_or_active_state(lane,damage):
    x=lane
    if damage in {'pending','reason'}:
        value=x.driver.current();value[damage]={'id':'uncertain'} if damage=='pending' else 'genuine scientific rejection'
        x.store.db.execute('UPDATE manual_state SET payload=?',(json.dumps(value),))
    elif damage=='call':x.store.db.execute("INSERT INTO manual_calls VALUES('x','run_spec_author',1,'RUNNING','{}')")
    elif damage=='global_running':x.store.batch.db.execute("INSERT INTO autonomy_calls VALUES('x','RUNNING')")
    elif damage=='config':(x.root/'lane.json').write_text('{}')
    elif damage=='halt':(x.root/'HALT').write_text('hold')
    else:(x.root/p.EVENT).mkdir()
    before=list(x.store.db.iterdump())
    with pytest.raises(ValueError):p.recover(x.driver,x.frozen,'a'*64)
    assert list(x.store.db.iterdump())==before

def test_native_unit_retains_all_confinement_except_reviewed_entry(monkeypatch):
    from tools import colab_pnormct_policy_runtime as runtime,colab_pnormct_runtime as parent
    native=json.loads((Path(__file__).resolve().parents[1]/'docs/COLAB_PNORMCT_NATIVE_PRIVATE.json').read_text())
    scope={'new_lane':native['work']+'/lane'}
    monkeypatch.setattr(parent,'metadata',lambda:(scope,native))
    raw=parent.unit_bytes(scope)
    fake=NS(metadata=lambda:(scope,native),unit_bytes=lambda s:raw)
    changed=runtime.unit_bytes(fake)
    old=b'/usr/bin/python3 -s -B '+str(runtime.BASE).encode()+b'/tools/colab_pnormct_runtime.py run'
    new=b'/usr/bin/python3 -s -B '+str(runtime.ROOT/runtime.ENTRY).encode()+b' run'
    assert changed==raw.replace(b'ExecStart='+old+b'\n',b'ExecStart='+new+b'\n')
    assert b'Restart=no' in changed and b'ProtectSystem=strict' in changed

def test_old_pnormct_recovery_checkpoint_cannot_apply_to_new_arm():
    root=Path(__file__).resolve().parents[1]
    raw=(root/p.DOCUMENT).read_bytes()
    assert q.sha(raw)==p.DOCUMENT_SHA
    original=json.loads(raw)
    assert original['run_id']!=q.RUN and original['calls']==[]
    with pytest.raises(ValueError,match='POLICY_CHECKPOINT_SCOPE'):
        p.document(root)
