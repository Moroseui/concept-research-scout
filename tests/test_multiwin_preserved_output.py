import copy,json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import multiwin_preserved_output as f
from test_multiwin_returned import lane as original_lane
from test_colab_arm_preparation import snapshot

@pytest.fixture
def lane(original_lane,monkeypatch):
    x=original_lane;d=x.driver;state=d.current()
    work=d.state.parent/'lane-scientific-workspaces/run_spec_author-13';work.mkdir(mode=0o700)
    d.config['private_intake']={'path':'intake.json','sha256':'d'*64}
    (d.state/'lane.json').write_bytes(f.encoded(d.config))
    state.update(phase='BLOCKED',reason='MODEL_FAILED_OR_UNCERTAIN_NO_RETRY',
        pending={'id':f.CALL,'stage':'run_spec_author','round':13,'workspace':str(work)})
    x.db.execute('UPDATE manual_state SET payload=?',(json.dumps(state),))
    x.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(f.CALL,'run_spec_author',13,'UNCERTAIN','{"error":"MODEL_OUTPUT_TOO_LARGE","charge":1}'))
    prompt=b'bound prompt';inputfile=b'original input';(work/'original.txt').write_bytes(inputfile)
    spec=('run_id: '+f.RUN+'\nanalysis_registry_sha256: '+'d'*64+'\n').encode()
    patch=b' '*84502
    body={'SPEC.proposed.md':spec,'notebook.patch.json':patch,'prompt.md':prompt,
      'input-measurement.json':f.encoded({'workspace_files':[{'path':'original.txt','sha256':f.sha(inputfile)}]}),
      'sent-input.json':f.encoded({'input_sha256':f.sha(prompt)}),
      'isolation-live.json':f.encoded({'status':'ISOLATED'}),
      'stage_provenance.jsonl':f.encoded({'stage':'run_spec_author','family_effective':'codex','exit_class':'ok','fallback':False,
          'prompt_sha256':f.sha(prompt),'attempts':[{'model':'gpt-6-astra','returncode':0}]})}
    events=[{'type':'item.completed','item':{'id':'item_18','type':'command_execution','status':'completed','exit_code':0,
        'aggregated_output':'\n'.join(n+' characters '+str(len(body[n].decode()))+' sha256 '+f.sha(body[n])for n in ('SPEC.proposed.md','notebook.patch.json'))}},
        {'type':'turn.completed'}]
    body['console.log']=b'\n'.join(f.encoded(e)for e in events)
    for n,raw in body.items():(work/n).write_bytes(raw)
    x.glob.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',(f.CALL,'scientific',f.RUN,25,'2026-10-13','UNCERTAIN',
        json.dumps({'input':{'input_sha256':f.sha(prompt)}}),'{"charge":1}'))
    b={'run':f.RUN,'call':f.CALL,'unit':'exact-author.service','workspace':str(work),'lane':str(d.state),
      'files':{n:{'bytes':len(raw),'sha256':f.sha(raw)}for n,raw in body.items()},
      'config_sha256':f.sha((d.state/'lane.json').read_bytes()),'local_rows':snapshot(x.db,'manual_calls'),
      'global_row':dict(x.glob.execute('SELECT * FROM autonomy_calls WHERE id=?',(f.CALL,)).fetchone()),
      'owner':dict(x.glob.execute('SELECT * FROM autonomy_runs').fetchone()),
      'state_row':dict(x.db.execute('SELECT * FROM manual_state').fetchone()),
      'account_row':dict(x.db.execute('SELECT * FROM manual_account').fetchone()),
      'prior_model_limit':80000,'output_limit':96000,'exact_output_bytes':84502,'new_author_calls':0,'next_review_attempt':12,'scientific_acceptance':False}
    x.b=b;x.work=work;x.state=state;d.context=d.state/'context';d.context.mkdir(mode=0o700)
    (d.context/'cohort').write_bytes(b'fixture')
    x.artifacts=[]
    d.artifact=lambda value,*args:x.artifacts.append(args)
    return x

def test_native_exact_outputs_and_original_rows(lane):
    x=lane;before=snapshot(x.db,'manual_calls'),snapshot(x.glob,'autonomy_calls')
    proof=f.check(x.driver,x.b,True)
    assert proof['new_calls']==0 and proof['original_status']=='UNCERTAIN'and not proof['scientific_acceptance']
    assert before==(snapshot(x.db,'manual_calls'),snapshot(x.glob,'autonomy_calls'))

@pytest.mark.parametrize('bad',['file','input','local','global','owner','state','account','config','running','extra'])
def test_drift_refuses_without_mutation(lane,bad):
    x=lane
    if bad=='file':(x.work/'notebook.patch.json').write_bytes(b'changed')
    if bad=='input':(x.work/'original.txt').write_bytes(b'changed')
    if bad=='local':x.db.execute("UPDATE manual_calls SET receipt='changed'WHERE id=?",(f.CALL,))
    if bad=='global':x.glob.execute("UPDATE autonomy_calls SET receipt='changed'WHERE id=?",(f.CALL,))
    if bad=='owner':x.glob.execute("UPDATE autonomy_runs SET status='COMPLETE'")
    if bad=='state':x.db.execute("UPDATE manual_state SET payload='{}'")
    if bad=='account':x.db.execute("UPDATE manual_account SET payload='changed'")
    if bad=='config':(x.driver.state/'lane.json').write_bytes(b'{}')
    if bad=='running':x.glob.execute("INSERT INTO autonomy_calls VALUES('live','scientific','other',1,'2026-10-13','RUNNING','{}','{}')")
    if bad=='extra':x.db.execute("INSERT INTO manual_calls VALUES('extra','run_spec_author',14,'FAILED','{}')")
    before=snapshot(x.db,'manual_state')
    with pytest.raises(ValueError):f.check(x.driver,x.b,True)
    assert snapshot(x.db,'manual_state')==before

@pytest.mark.parametrize('bad',['exit','fallback','family','input','isolation','terminal','twoturns','hash_event','chars'])
def test_native_semantic_failures_refused_even_with_matching_file_hash(lane,bad):
    x=lane;b=copy.deepcopy(x.b)
    name='stage_provenance.jsonl'
    value=json.loads((x.work/name).read_bytes())
    if bad=='exit':value['exit_class']='timeout'
    if bad=='fallback':value['fallback']=True
    if bad=='family':value['family_effective']='claude'
    if bad=='input':value['prompt_sha256']='e'*64
    raw=f.encoded(value)
    if bad=='isolation':name='isolation-live.json';raw=f.encoded({'status':'NOT_ISOLATED'})
    if bad in {'terminal','twoturns','hash_event','chars'}:
        name='console.log';events=[json.loads(l)for l in (x.work/name).read_bytes().splitlines()]
        if bad=='terminal':events[-1]={'type':'turn.failed'}
        if bad=='twoturns':events.append({'type':'turn.completed'})
        if bad=='hash_event':events[0]['item']['exit_code']=1
        if bad=='chars':events[0]['item']['aggregated_output']=events[0]['item']['aggregated_output'].replace('84502','84501')
        raw=b'\n'.join(f.encoded(e)for e in events)
    (x.work/name).write_bytes(raw);b['files'][name]={'bytes':len(raw),'sha256':f.sha(raw)}
    with pytest.raises(ValueError):f.native(b,lambda p:p.read_bytes())

def synthetic_stubs(x,monkeypatch,fail=False):
    from orchestrator import notebook_revision as nr,scientific_intake as intake,colab_preparation_scope as scope,colab_notebook_delivery as delivery
    monkeypatch.setattr(nr,'bound',lambda *a:f.encoded({'cohort':'cohort'}))
    monkeypatch.setattr(intake,'cohort',lambda *a:[])
    monkeypatch.setattr(nr,'scan',lambda *a:None)
    calls=[]
    def underlying(original,selection,raw,cases,**kw):
        assert kw=={'patch_limit':96000}and raw==(x.work/'notebook.patch.json').read_bytes()
        calls.append('real-parser-called');return None
    monkeypatch.setattr(nr,'apply',underlying)
    def prepare(driver,value,pending,cases):
        nr.apply(None,None,(x.work/'notebook.patch.json').read_bytes(),cases)
        value['notebook_revision_result']={'synthetic_status':'FAIL'if fail else'PASS'}
    monkeypatch.setattr(scope,'prepare_notebook_artifacts',prepare)
    monkeypatch.setattr(delivery,'prepare_variants',lambda *a:calls.append('normal-delivery'))
    return nr,underlying,calls

def test_recovery_preserves_all_charges_no_fabricated_call_receipt(lane,monkeypatch):
    x=lane;nr,original,calls=synthetic_stubs(x,monkeypatch)
    before=snapshot(x.db,'manual_calls'),snapshot(x.db,'manual_account'),snapshot(x.glob,'autonomy_calls')
    result=f.apply(x.driver,x.b,'a'*64)
    assert result['model_calls']==0 and result['original_calls_preserved']==25
    assert nr.apply is original and calls==['real-parser-called','normal-delivery']
    assert before==(snapshot(x.db,'manual_calls'),snapshot(x.db,'manual_account'),snapshot(x.glob,'autonomy_calls'))
    assert x.driver.current()['phase']=='run_spec_review'and x.driver.current()['rounds']['run_spec_author']==13
    assert len(x.artifacts)==2 and all(a[2]==(x.work/'SPEC.proposed.md').read_bytes()for a in x.artifacts)
    f.grant(x.driver,x.b,'a'*64)
    with pytest.raises(ValueError):f.apply(x.driver,x.b,'a'*64)
    assert not(x.work/'.author-submission.json').exists()

def test_failed_synthetic_validation_keeps_block_and_restores_parser(lane,monkeypatch):
    x=lane;nr,original,calls=synthetic_stubs(x,monkeypatch,True);before=x.driver.current()
    with pytest.raises(ValueError,match='SYNTHETIC_PASS_REQUIRED'):f.apply(x.driver,x.b,'a'*64)
    assert nr.apply is original and x.driver.current()==before
    assert not(x.driver.state/f.EVENT/'COMPLETE.json').exists()

@pytest.mark.parametrize('changed',['patch','kwarg'])
def test_parser_extension_is_exact_bytes_only(lane,monkeypatch,changed):
    x=lane;nr,original,_=synthetic_stubs(x,monkeypatch)
    from orchestrator import colab_preparation_scope as scope
    def prepare(*a):
        raw=(x.work/'notebook.patch.json').read_bytes()
        nr.apply(None,None,raw+b' 'if changed=='patch'else raw,[],**({'patch_limit':100000}if changed=='kwarg'else{}))
    monkeypatch.setattr(scope,'prepare_notebook_artifacts',prepare)
    with pytest.raises(ValueError,match='EXACT_PATCH_ONLY'):f.apply(x.driver,x.b,'a'*64)
    assert nr.apply is original and x.driver.current()==x.state

def test_terminal_bridge_proves_exact_row_and_preserves_unknown_refusal(lane,monkeypatch):
    x=lane;synthetic_stubs(x,monkeypatch);f.apply(x.driver,x.b,'a'*64)
    from orchestrator import colab_simple_full as full
    monkeypatch.setattr(full,'_TERMINAL_QUALIFIER',lambda *a:None)
    scope={'run_id':f.RUN,'uncertain_rows':[]}
    monkeypatch.setattr(full,'validate',lambda *a:scope)
    old=full.terminal_ids;restore=f.bind(x.driver,x.b,'a'*64)
    before=snapshot(x.glob,'autonomy_calls')
    try:
        assert full.terminal_ids(x.driver.store.batch,scope)==[f.CALL]
        assert full.local_terminal_ids(x.driver.store,f.RUN)==[f.CALL]
        assert scope['uncertain_rows']==[]and snapshot(x.glob,'autonomy_calls')==before
        x.glob.execute("INSERT INTO autonomy_calls VALUES('unknown','scientific','other',1,'2026-10-13','UNCERTAIN','{}','{}')")
        with pytest.raises(ValueError,match='UNCLASSIFIED_OR_RUNNING_CALL'):full.terminal_ids(x.driver.store.batch,scope)
    finally:restore()
    assert full.terminal_ids is old

def test_installed_parser_default_still_refuses_oversize():
    from orchestrator import notebook_revision as nr
    from test_notebook_revision import fixture
    raw,selection,p=fixture()
    with pytest.raises(ValueError,match='NOTEBOOK_PATCH_LIMIT'):
        nr.apply(raw,selection,b' '*84502,[],original_sha256=p['original_sha256'],view_sha256=p['view_sha256'])

def test_runtime_only_changes_service_entrypoint(tmp_path,monkeypatch):
    from tools import multiwin_preserved_runtime as rt
    from orchestrator import manual_host_guard
    old=NS(UNIT='old.service',ENTRY='tools/multiwin_returned_runtime.py')
    raw=('User=partho\nProtectSystem=strict\nNoNewPrivileges=yes\nExecStart=/usr/bin/python3 -s -B '+str(rt.PRIOR/old.ENTRY)+' run\n').encode()
    p=tmp_path/'unit';p.write_bytes(raw);monkeypatch.setattr(manual_host_guard,'trusted',lambda path:p)
    assert rt.unit_bytes(old).replace(str(rt.ROOT/rt.ENTRY).encode(),str(rt.PRIOR/old.ENTRY).encode())==raw

def test_administrative_bootstrap_one_exact_call_no_scientific_authority(lane):
    x=lane;before=snapshot(x.glob,'autonomy_calls');x.glob.execute('BEGIN')
    try:
        out=f.administrative(x.glob,x.b,lambda p:p.read_bytes(),lambda row:None,lambda unit:True,'multiwin-output-boundary-20261013')
        assert out[0]['id']==f.CALL and out[0]['classification']=='STANDING_ONE_ADMIN_COMPLETED_OUTPUT_REPAIR'
        assert snapshot(x.glob,'autonomy_calls')==before
    finally:x.glob.rollback()

@pytest.mark.parametrize('bad',['prior','live','row','unit','change','transaction'])
def test_administrative_bootstrap_refuses_reuse_and_unknown_live(lane,bad):
    x=lane;x.b['unit']='exact-author.service'
    if bad=='prior':x.glob.execute("INSERT INTO autonomy_calls VALUES('prior-review','implementation_review','multiwin-output-boundary-20261013',1,'2026-10-13','FAILED','{}','{}')")
    if bad=='live':x.glob.execute("INSERT INTO autonomy_calls VALUES('live','scientific','other',1,'2026-10-13','RUNNING','{}','{}')")
    if bad=='row':x.glob.execute("UPDATE autonomy_calls SET receipt='changed'WHERE id=?",(f.CALL,))
    if bad!='transaction':x.glob.execute('BEGIN')
    try:
        with pytest.raises(ValueError):f.administrative(x.glob,x.b,lambda p:p.read_bytes(),lambda row:None,lambda unit:bad!='unit','other'if bad=='change'else'multiwin-output-boundary-20261013')
    finally:x.glob.rollback()
