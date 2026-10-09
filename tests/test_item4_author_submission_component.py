"""Synthetic recovery and actual original admission tests; no native/model calls."""
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace
import pytest
from tools import item4_author_submission_component as h
from tools import install_item4_author_submission as installer
from orchestrator import author_format_submission as sub
from test_author_format_submission import fixture as format_fixture, author_correction


@pytest.fixture
def saved(tmp_path, monkeypatch):
    state=tmp_path/'state';lane=state/'item4/lane';lane.mkdir(parents=True)
    work=state/'item4/work/run_spec_author-5';prior=work.with_name('run_spec_author-4');prior.mkdir(parents=True)
    context=lane/'context';context.mkdir();globalroot=tmp_path/'global';globalroot.mkdir()
    dest=state/'item4/recovery'
    for name,value in [('STATE',state),('LANE',lane),('WORK',work),('DEST',dest),('GLOBAL',globalroot)]:monkeypatch.setattr(h,name,value)
    owner={'run_id':'synthetic-item4'};op=lane/'owner.json';op.write_text(json.dumps(owner))
    config={'run_id':'synthetic-item4','source':'a'*40,'context':str(context),'owner_path':str(op),'owner_binding':owner}
    cr=json.dumps(config).encode();(lane/'lane.json').write_bytes(cr);(lane/'DECISION_REQUEST.md').write_text('Original failure')
    state_value={'phase':'BLOCKED','reason':'OUTPUT_VALIDATION_REFUSED: EXPERIMENT_PROJECTION_FULL_FIT',
        'rounds':{'run_spec_author':4},'pending':{'id':'call4'},'blocked_stage':'run_spec_author',
        'artifacts':[],'interventions':[]}
    sr=json.dumps(state_value)
    db=sqlite3.connect(lane/'jobs.sqlite');db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE manual_state(id INTEGER,payload TEXT)');db.execute('INSERT INTO manual_state VALUES(1,?)',(sr,))
    db.execute('CREATE TABLE manual_calls(id TEXT,stage TEXT,attempt INTEGER,status TEXT,receipt TEXT)')
    for i in range(1,5):db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',('call'+str(i),'run_spec_author',i,'UNCERTAIN' if i==1 else 'COMPLETE','original charge'+str(i)))
    db.execute('CREATE TABLE manual_account(id INTEGER,used INTEGER)');db.execute('INSERT INTO manual_account VALUES(1,4)');db.commit()
    calls=h.call_rows(db)
    account={n:h.sha(h.canonical([dict(r) for r in db.execute('SELECT * FROM '+n+' ORDER BY rowid')])) for n in ['manual_calls','manual_account']}
    db.close()
    g=sqlite3.connect(globalroot/'jobs.sqlite');g.row_factory=sqlite3.Row
    g.execute('CREATE TABLE autonomy_calls(id TEXT,status TEXT,receipt TEXT)')
    for c in calls:g.execute('INSERT INTO autonomy_calls VALUES(?,?,?)',(c['id'],c['status'],c['receipt']))
    g.execute('CREATE TABLE autonomy_runs(id TEXT,binding TEXT,status TEXT)');g.execute('INSERT INTO autonomy_runs VALUES(?,?,?)',(config['run_id'],json.dumps(owner),'ACTIVE'));g.commit()
    gp={r['id']:h.sha(h.canonical(dict(r))) for r in g.execute('SELECT * FROM autonomy_calls')};g.close()
    bodies={'SPEC.proposed.md':b'Synthetic spec','execution.plan.json':b'{"synthetic":true}','notebook.patch.json':b'{"synthetic":true}'}
    for name,raw in bodies.items():(prior/name).write_bytes(raw)
    b={'config_sha256':h.sha(cr),'state_sha256':h.sha(sr.encode()),'source':config['source'],'run_id':config['run_id'],
        'call4':'call4','call5':'call5','calls_sha256':h.sha(h.canonical(calls)), 'global_calls':gp,'accounting':account,
        'outputs':{n:h.sha(raw) for n,raw in bodies.items()}}
    monkeypatch.setattr(h,'load',lambda:({'review_sha256':'b'*64},b))
    for root in [state, globalroot]:
        for path in [root, *root.rglob('*')]:path.chmod(0o700 if path.is_dir() else 0o600)
    return lane,globalroot,b,calls,bodies


def dump(path):
    with sqlite3.connect(path) as db:return list(db.iterdump())


def test_apply_preserves_all_calls_charges_originals_and_never_touches_item6(saved):
    lane,glob,b,calls,bodies=saved
    before=dump(glob/'jobs.sqlite')
    result=h.apply();assert result=={'status':'APPLIED_HELD','model_calls':0,'item6_untouched':True}
    assert before==dump(glob/'jobs.sqlite')
    assert dump(h.DEST/'before.sqlite')
    with sqlite3.connect(lane/'jobs.sqlite') as db:
        db.row_factory=sqlite3.Row;assert h.call_rows(db)==calls
        state=json.loads(db.execute('SELECT payload FROM manual_state').fetchone()[0])
        assert state['phase']=='run_spec_author' and state['rounds']=={'run_spec_author':4} and 'pending' not in state
        assert db.execute('SELECT used FROM manual_account').fetchone()[0]==4
    for name,raw in bodies.items():assert (h.WORK.with_name('run_spec_author-4')/name).read_bytes()==raw
    with pytest.raises(ValueError,match='AUTHOR_RECOVERY_EXISTS_INSPECT'):h.apply()


@pytest.mark.parametrize('damage', ['local-charge','global-charge','config','state','output','halt'])
def test_drift_stops_before_recovery_writes(saved, damage):
    lane,glob,b,_,_=saved
    if damage in {'local-charge','global-charge'}:
        path=(lane if damage=='local-charge' else glob)/'jobs.sqlite'
        table='manual_calls' if damage=='local-charge' else 'autonomy_calls'
        with sqlite3.connect(path) as db:db.execute('UPDATE '+table+" SET receipt='changed'")
    elif damage=='config':(lane/'lane.json').write_text('{}')
    elif damage=='state':
        with sqlite3.connect(lane/'jobs.sqlite') as db:db.execute("UPDATE manual_state SET payload='{}'")
    elif damage=='output':(h.WORK.with_name('run_spec_author-4')/'SPEC.proposed.md').write_bytes(b'Changed')
    else:(lane/'HALT').touch()
    with pytest.raises(ValueError):h.apply()
    assert not h.DEST.exists()


def test_role_scope_does_not_grant_a_sixth_or_any_other_run(saved):
    lane,glob,b,calls,_=saved
    db=sqlite3.connect(lane/'jobs.sqlite');db.row_factory=sqlite3.Row
    store=SimpleNamespace(path=lane/'jobs.sqlite',db=db)
    original=lambda *a:4
    assert h.fifth_limit(original,store,b['run_id'],'run_spec_author',b)==5
    assert h.fifth_limit(original,store,'another','run_spec_author',b)==4
    assert h.fifth_limit(original,store,b['run_id'],'run_spec_review',b)==4
    db.execute("INSERT INTO manual_calls VALUES('call5','run_spec_author',5,'COMPLETE','new charge')")
    assert h.fifth_limit(original,store,b['run_id'],'run_spec_author',b)==5  # n=6 still exceeds returned cap
    db.execute("INSERT INTO manual_calls VALUES('call6','run_spec_author',6,'COMPLETE','forbidden')")
    with pytest.raises(ValueError,match='AUTHOR_FIFTH_ONLY'):h.fifth_limit(original,store,b['run_id'],'run_spec_author',b)
    db.close()


def accepted_event(root,pin,answer):
    return json.dumps({'type':'item.completed','item':{'id':'item_42','type':'mcp_tool_call',
        'server':'author_format','tool':'submit_author','arguments':{},'status':'completed','error':None,
        'result':{'content':[{'type':'text','text':json.dumps(answer)}],'structured_content':None}}})


def test_native_ack_required_and_final_prose_cannot_substitute(tmp_path):
    pin,originals=format_fixture(tmp_path);author_correction(tmp_path,originals);answer=sub.submit(tmp_path,pin,{})
    event=accepted_event(tmp_path,pin,answer)
    assert sub.verify_native(tmp_path,pin,event)['native_item_id']=='item_42'
    for console in [json.dumps(answer),json.dumps({'type':'item.completed','item':{'type':'agent_message','text':event}}),
        event.replace('mcp_tool_call','command_execution'),event.replace('author_format','other_server'),
        event.replace('completed", "error"','failed", "error"'),event+'\n'+event]:
        with pytest.raises(ValueError,match='AUTHOR_NATIVE_ACCEPTED_SUBMISSION_REQUIRED'):sub.verify_native(tmp_path,pin,console)


def test_unit_changes_only_execstart_preserving_all_sandbox_and_owner_options():
    old='User=partho\nGroup=partho\nExecStartPre=+/original/host-control\nExecStart=/usr/bin/python3 -s -B /opt/research-system/manual-repair-helpers/daily-limit-and-image-probe-20261007/tools/daily_limit_component.py 4\nRestart=no\nNoNewPrivileges=true\nProtectSystem=strict\nPrivateTmp=true\n'
    new=installer.unit_bytes(old).decode()
    assert [x for x in old.splitlines() if not x.startswith('ExecStart=')]==[x for x in new.splitlines() if not x.startswith('ExecStart=')]
    with pytest.raises(ValueError,match='AUTHOR_INSTALL_UNIT_SHAPE'):installer.unit_bytes(old.replace(' 4',' 6'))


def test_profile_preserves_original_transport_and_binds_fixed_sender(tmp_path,monkeypatch):
    import tomllib
    import sys
    from orchestrator import manual_stage as ms
    pin,originals=format_fixture(tmp_path)
    (tmp_path/sub.SERVER).write_bytes(Path(sub.__file__).read_bytes());(tmp_path/sub.SERVER).chmod(0o600)
    pins={str(p.relative_to(tmp_path)):sub.sha(p.read_bytes()) for p in (tmp_path/sub.RUNTIME).rglob('*') if p.is_file()}
    monkeypatch.setattr(h,'WORK',tmp_path)
    base=['/tools/node','/tools/codex/bin/codex.js','exec','--ignore-user-config','--ignore-rules','--model','gpt-6-astra',
        '-s','workspace-write','-c','approval_policy="never"','-c','sandbox_workspace_write.network_access=false','--json','-']
    commands=[('codex',base),('claude',[])]
    rendered=h.sender_profile(ms.transport_profile,'a'*64,commands,pins,stage='run_spec_author')
    profile=tomllib.loads(rendered)
    assert profile['rotation']['enabled'] is False and profile['limits']['stage_timeout']==900
    cmd=profile['codex']['command']
    assert cmd[:5]==[sys.executable,'-s','-B',str(h.ROOT/'tools/item4_author_submission_component.py'),'send']
    assert cmd[5:8]==['a'*64,'codex','--']
    assert cmd[8:]==sub.client_command(base,tmp_path,pins)
    assert h.sender_profile(ms.transport_profile,'a'*64,commands,None,sink=True,stage='run_spec_author')==ms.transport_profile('a'*64,commands,sink=True,stage='run_spec_author')


@pytest.fixture
def admission(tmp_path,monkeypatch):
    from test_scoped_revisions_limits import configured, policy
    from orchestrator import manual_recovery as rec
    from orchestrator.manual_executor import digest
    store,batch,config=configured(tmp_path,item=4,backend='modal')
    monkeypatch.setattr(h,'LANE',store.path.parent)
    original=lambda *args:4
    # Fixture represents the already-qualified historical four-author grant.
    # Admission, counters and all cap functions remain the actual originals.
    monkeypatch.setattr(rec,'role_limit',original)
    for _ in range(4):
        ident,n,receipt=store.reserve_call('synthetic','run_spec_author','a'*40,'astra/manual-test',policy(),{})
        store.finish_call(ident,receipt,'COMPLETE')
    calls=h.call_rows(store.db)
    binding={'run_id':'synthetic','config_sha256':h.sha((store.path.parent/'lane.json').read_bytes()),
        'calls_sha256':h.sha(h.canonical(calls)),'call5':digest(b'synthetic:run_spec_author:5')}
    monkeypatch.setattr(rec,'role_limit',lambda st,run,stage:h.fifth_limit(original,st,run,stage,binding))
    yield store,batch,calls,policy
    store.db.close();batch.db.close()


def test_actual_fifth_admission_charges_once_and_sixth_refuses(admission):
    from orchestrator.manual_executor import Accounts
    store,batch,originals,policy=admission
    ident,n,receipt=store.reserve_call('synthetic','run_spec_author','a'*40,'astra/manual-test',policy(),{})
    assert n==5 and Accounts(store).read()[1]['count']==5
    store.finish_call(ident,receipt,'COMPLETE')
    before=list(store.db.iterdump());global_before=list(batch.db.iterdump())
    assert h.call_rows(store.db)[:4]==originals
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==5
    with pytest.raises(ValueError,match='STEP_D_MODEL_CALL_LIMIT'):
        store.reserve_call('synthetic','run_spec_author','a'*40,'astra/manual-test',policy(),{})
    assert list(store.db.iterdump())==before and list(batch.db.iterdump())==global_before


@pytest.mark.parametrize('cap', ['day','batch','run'])
def test_actual_original_caps_still_refuse_fifth_before_charging(admission,cap):
    from datetime import datetime,timezone
    from orchestrator import autonomy_limits as limits
    store,batch,originals,policy=admission
    day=datetime.now(timezone.utc).date().isoformat()
    if cap=='run':
        for i in range(16):store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',('other-'+str(i),'run_spec_review',i+1,'COMPLETE','{}'))
        expected='STEP_D_MODEL_CALL_LIMIT'
    else:
        count=limits.DAILY-4 if cap=='day' else limits.SCIENTIFIC_BATCH-4
        for i in range(count):batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
            ('seed-'+str(i),'implementation_review' if cap=='day' else 'scientific','other',1,day if cap=='day' else '2020-01-01','FAILED','{}','{}'))
        expected='AUTONOMY_DAILY_CALL_LIMIT' if cap=='day' else 'AUTONOMY_BATCH_CALL_LIMIT'
    before=list(store.db.iterdump());global_before=list(batch.db.iterdump())
    with pytest.raises(ValueError,match=expected):
        store.reserve_call('synthetic','run_spec_author','a'*40,'astra/manual-test',policy(),{})
    assert list(store.db.iterdump())==before and list(batch.db.iterdump())==global_before
