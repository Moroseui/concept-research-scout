"""Synthetic state fixtures, real SQLite copying and binding checks; no model calls."""
import json
from pathlib import Path
import sqlite3
import subprocess
import pytest
from orchestrator import artifact_recording_transition as t, private_records
from orchestrator.manual_executor import atomic, digest, inventory, read
from orchestrator.stocktake_recovery import ledger_folder, connect


def test_exact_frozen_checkpoint_and_scratch_ledger(tmp_path):
    p=t.checkpoint()
    assert len(p['call_rows'])==1 and set(p['call_rows'])==set(p['global_rows'])
    assert p['reason']=='OUTPUT_VALIDATION_REFUSED: IMMUTABLE_ARTIFACT_CONFLICT'
    assert p['output_sha256']['SPEC.proposed.md']=='018821e74757a1547aee355368abda80f48ad11210dec450616d4c10fc5a3adf'
    assert ledger_folder({'artifact_continuation':t.KEY,'artifact_filesystem_root':str(tmp_path),'batch_ledger':'/ledger'})==tmp_path/'ledger'
    with pytest.raises(KeyError):ledger_folder({'artifact_continuation':t.KEY,'batch_ledger':'/ledger'})


@pytest.fixture
def frozen(tmp_path,monkeypatch):
    old=tmp_path/'old/lane';private_records.mkdir(old/'context',parents=True)
    private_records.write_text(old/'context/old.md','Synthetic prior artifact.')
    private_records.mkdir(tmp_path/'old/work');raw=b'Synthetic completed author output.'
    private_records.write_bytes(tmp_path/'old/work/SPEC.proposed.md',raw)
    atomic(tmp_path/'owner.json',{'run':'synthetic'})
    c={'source':'a'*40,'run_id':'synthetic','item_number':5,'backend':'analysis','batch_ledger':'/ledger',
       'owner_path':'/owner.json','owner_binding':{'run':'synthetic'},'profile_files':{},'revision_policy':t.analysis_revisions.POLICY}
    atomic(old/'lane.json',c);atomic(old/'preparation-plan.json',{'synthetic':True})
    v={'phase':'BLOCKED','reason':'OUTPUT_VALIDATION_REFUSED: IMMUTABLE_ARTIFACT_CONFLICT',
       'pending':{'id':'one','stage':'run_spec_author','round':1,'workspace':'/old/work'}}
    with sqlite3.connect(old/'jobs.sqlite') as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT)')
        db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps(v),))
        db.execute('CREATE TABLE manual_calls(id TEXT PRIMARY KEY,status TEXT,receipt TEXT)')
        db.execute('INSERT INTO manual_calls VALUES(?,?,?)',('one','COMPLETE',json.dumps({'output_sha256':{'SPEC.proposed.md':digest(raw)}})))
        for table in ['manual_account','manual_recoveries']:
            db.execute('CREATE TABLE '+table+'(id TEXT PRIMARY KEY,payload TEXT)')
        db.execute('INSERT INTO manual_account VALUES(?,?)',('one',json.dumps({'count':1,'resets':[]})))
    private_records.mkdir(tmp_path/'ledger')
    with sqlite3.connect(tmp_path/'ledger/jobs.sqlite') as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('CREATE TABLE autonomy_calls(id TEXT PRIMARY KEY,status TEXT,receipt TEXT)')
        db.execute('INSERT INTO autonomy_calls VALUES(?,?,?)',('one','COMPLETE','{"charge":1}'))
        db.execute('CREATE TABLE autonomy_runs(id TEXT PRIMARY KEY,status TEXT)')
        db.execute('INSERT INTO autonomy_runs VALUES(?,?)',('synthetic','ACTIVE'))
        db.execute('CREATE TABLE events(id TEXT PRIMARY KEY,run_id TEXT,payload TEXT)')
    with connect(old/'jobs.sqlite') as db:
        tables={name:t.sha(t.rows(db,name)) for name in ('manual_state','manual_calls','manual_account','manual_recoveries')}
    with connect(tmp_path/'ledger/jobs.sqlite') as db:
        call=t.sha(dict(db.execute('SELECT * FROM autonomy_calls').fetchone()))
        owner=t.sha(dict(db.execute('SELECT * FROM autonomy_runs').fetchone()))
    p={'run_id':'synthetic','old_state':'/old/lane','old_source':'a'*40,'call_rows':['one'],'workspace':'/old/work',
       'config_sha256':digest((old/'lane.json').read_bytes()),'plan_sha256':digest((old/'preparation-plan.json').read_bytes()),
       'owner_sha256':digest((tmp_path/'owner.json').read_bytes()),'context_sha256':t.sha(inventory(old/'context')),
       'tables':tables,'global_rows':{'one':call},'global_owner_sha256':owner,
       'output_sha256':{'SPEC.proposed.md':digest(raw)},'units':['old.service','old.timer']}
    # Synthetic checkpoint substitution only. Actual installed checkpoint is exercised on server.
    monkeypatch.setattr(t,'checkpoint',lambda:p)
    return tmp_path,old,c,v,p


def test_private_wal_copy_preserves_rows_and_duplicate_refuses(frozen,monkeypatch):
    host,old,c,v,p=frozen
    from orchestrator import analysis_driver,autonomy_review
    from tools import manual_promotion,deploy_manual_lane
    repo=host/'new/repository';private_records.mkdir(repo,parents=True)
    private_records.write_text(repo/'source.txt','Synthetic source')
    for args in [('init','-q'),('config','user.name','Fixture'),('config','user.email','fixture@invalid'),
                 ('add','.'),('commit','-qm','Synthetic release'),('switch','-qc','astra/manual-server-fixture')]:
        subprocess.run(['git','-C',str(repo),*args],check=True)
    head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    runtime=host/'runtime.json';atomic(runtime,{'synthetic':True});monkeypatch.setenv('RESEARCH_MANUAL_RUNTIME_CONFIG',str(runtime))
    report=host/'review/report.json';private_records.write_text(report,'Synthetic review, never genuine approval.')
    selected={'source':head,'state':'/new','runtime_sha256':digest(runtime.read_bytes()),'units':['new.service','new.timer']}
    atomic(host/manual_promotion.POINTER.lstrip('/'),selected)
    # Qualification, authority and host service simulation are explicitly synthetic.
    # Prior-state verification, WAL-backed SQLite copy and ledger transaction are real.
    monkeypatch.setattr(autonomy_review,'verify_result',lambda folder:{'verdict':'APPROVE','source_sha':head,
        'report_sha256':digest(report.read_bytes()),'runtime_sha256':selected['runtime_sha256']})
    monkeypatch.setattr(t.autonomy_limits,'authority',lambda root:None)
    monkeypatch.setattr(analysis_driver,'release_identities',lambda root:({}, {'source.txt':digest((root/'source.txt').read_bytes())}))
    monkeypatch.setattr(deploy_manual_lane,'system',lambda *args:{'enabled':False,'active':False})
    with connect(old/'jobs.sqlite') as db:before=list(db.iterdump())
    with connect(host/'ledger/jobs.sqlite') as db:charges=[tuple(x) for x in db.execute('SELECT * FROM autonomy_calls')]
    result=t.prepare(host/'new/lane',repo,report,filesystem_root=host)
    assert result['calls_used']==1 and result['call_limit']==16
    with connect(old/'jobs.sqlite') as db:assert list(db.iterdump())==before
    with connect(host/'new/lane/jobs.sqlite') as db:assert list(db.iterdump())==before
    with connect(host/'ledger/jobs.sqlite') as db:
        assert [tuple(x) for x in db.execute('SELECT * FROM autonomy_calls')]==charges
        assert db.execute('SELECT count(*) FROM events').fetchone()[0]==1
    assert read(host/'new/lane/lane.json')['owner_binding']==c['owner_binding']
    with pytest.raises(ValueError,match='^ARTIFACT_EXISTING_DESTINATION$'):
        t.prepare(host/'new/lane',repo,report,filesystem_root=host)
    # A completed successor is checked independently; never infer completion from the event.
    assert t.completed_predecessors(host)==[]
    with sqlite3.connect(host/'ledger/jobs.sqlite') as db:db.execute("UPDATE autonomy_runs SET status='COMPLETE'")
    with pytest.raises(ValueError,match='^ARTIFACT_SUCCESSOR_NOT_COMPLETE$'):t.completed_predecessors(host)
    with sqlite3.connect(host/'new/lane/jobs.sqlite') as db:
        db.execute('UPDATE manual_state SET payload=?',(json.dumps({'phase':'COMPLETE'}),))
    assert t.completed_predecessors(host)==[old]
    with sqlite3.connect(host/'new/lane/jobs.sqlite') as db:db.execute("UPDATE manual_calls SET receipt='changed'")
    with pytest.raises(ValueError,match='^ARTIFACT_PRESERVED_CALL_CHANGED$'):t.completed_predecessors(host)


@pytest.mark.parametrize('kind,code',[
 ('output','ARTIFACT_SAVED_OUTPUT_CHANGED'),('context','ARTIFACT_CONTEXT_CHANGED'),
 ('owner','ARTIFACT_OWNER_CHANGED'),('call','ARTIFACT_OLD_ROWS_CHANGED:manual_calls'),
 ('charge','ARTIFACT_GLOBAL_CALL_CHANGED'),('active','ARTIFACT_ACTIVE_CALL')])
def test_frozen_evidence_changes_refuse(frozen,kind,code):
    host,old,c,v,p=frozen
    if kind=='output':private_records.write_text(host/'old/work/SPEC.proposed.md','changed')
    elif kind=='context':private_records.write_text(old/'context/old.md','changed')
    elif kind=='owner':atomic(host/'owner.json',{'changed':True})
    elif kind=='call':
        with sqlite3.connect(old/'jobs.sqlite') as db:db.execute("UPDATE manual_calls SET status='UNCERTAIN'")
    else:
        with sqlite3.connect(host/'ledger/jobs.sqlite') as db:
            if kind=='charge':db.execute("UPDATE autonomy_calls SET receipt='changed'")
            else:db.execute("INSERT INTO autonomy_calls VALUES('other','RUNNING','{}')")
    with pytest.raises(ValueError,match='^'+code+'$'):t.prior(host)
