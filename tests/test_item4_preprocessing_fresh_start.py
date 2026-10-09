"""One fixed terminal recovery; no model, provider computation or patient payload."""
import copy
import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import item4_preprocessing_fresh_start as fresh
from orchestrator.modal_executor import item4_job
from orchestrator.modal_preprocessing_provider import exists


@pytest.fixture
def setup(monkeypatch):
    root=Path(__file__).resolve().parents[1]
    monkeypatch.setattr(fresh,'ROOT',root)
    monkeypatch.setattr(fresh,'authority',lambda:{'report_sha256':'a'*64})
    p=fresh.contract()
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE autonomy_compute(id TEXT PRIMARY KEY,run TEXT,binding TEXT,status TEXT,reserved_micro_usd INTEGER,provider_id TEXT,actual_micro_usd INTEGER,month TEXT)')
    db.execute('CREATE TABLE events(id TEXT PRIMARY KEY,job TEXT,payload TEXT)')
    row=dict(p['old_row']);row['status']='ACCOUNTED'
    db.execute('INSERT INTO autonomy_compute VALUES(?,?,?,?,?,?,?,?)',tuple(row[k] for k in ['id','run','binding','status','reserved_micro_usd','provider_id','actual_micro_usd','month']))
    db.execute('INSERT INTO events VALUES(?,?,?)',(row['id']+':pre-science-stop',row['run'],fresh.encoded(p['event']).decode()))
    db.commit()
    yield p,db
    db.close()


def predecessor(p,db):
    row=db.execute('SELECT * FROM autonomy_compute').fetchone()
    return [(row,json.loads(row['binding']))]


def test_exact_successor_retains_full_row_charge_and_does_not_write(setup):
    p,db=setup;before=db.total_changes
    fresh.validate_reservation(SimpleNamespace(db=db),predecessor(p,db),p['new_binding'])
    assert db.total_changes==before
    row=dict(db.execute('SELECT * FROM autonomy_compute').fetchone())
    assert row=={**p['old_row'],'status':'ACCOUNTED'}
    assert item4_job(p['new_binding'])==p['new_job']!=p['old_job']
    changed=copy.deepcopy(p['new_binding']);changed['resources']['cpu']+=1
    assert item4_job(changed)==p['new_job'] # resources cannot mint a new job


@pytest.mark.parametrize('fault',['live','charge','provider','missing-event','changed-event','duplicate','no-predecessor','new-input','new-runtime','new-link','wrong-stage','changed-code'])
def test_unknown_altered_or_duplicate_recovery_refused(setup,fault):
    p,db=setup;b=copy.deepcopy(p['new_binding']);rows=predecessor(p,db)
    if fault=='live':db.execute("UPDATE autonomy_compute SET status='RUNNING'")
    if fault=='charge':db.execute('UPDATE autonomy_compute SET reserved_micro_usd=1')
    if fault=='provider':db.execute("UPDATE autonomy_compute SET provider_id='sb-other'")
    if fault=='missing-event':db.execute('DELETE FROM events')
    if fault=='changed-event':db.execute("UPDATE events SET payload='{}'")
    if fault=='duplicate':rows=rows*2
    if fault=='no-predecessor':rows=[]
    if fault=='new-input':b['source_volume_id']='vo-other'
    if fault=='new-runtime':b['runtime_sha256']='0'*64
    if fault=='new-link':b['fresh_start']['terminal_event_sha256']='0'*64
    if fault=='wrong-stage':b['experiment']['stage']='FULL'
    if fault=='changed-code':b['execution']['module_sha256']='0'*64
    with pytest.raises(ValueError,match='FRESH_PREPROCESSING_'):
        fresh.validate_reservation(SimpleNamespace(db=db),rows,b)


@pytest.mark.parametrize('fault',['fit','segment','resume','bad-link'])
def test_fresh_job_identity_has_no_generic_restart_escape(setup,fault):
    p,_=setup;b=copy.deepcopy(p['new_binding'])
    if fault=='fit':b.pop('preprocessing')
    if fault=='segment':b['experiment']['segment']=2
    if fault=='resume':b['resume']={}
    if fault=='bad-link':b['fresh_start']={'arbitrary':'value'}
    with pytest.raises(ValueError,match='ITEM4_FRESH_START_IDENTITY'):item4_job(b)


class Volume:
    def __init__(self,rows):self.rows=rows
    def listdir(self,path,recursive=False):
        if path not in self.rows:raise RuntimeError('transport or missing unqualified path')
        return [SimpleNamespace(path=name,type=SimpleNamespace(name=kind)) for name,kind in self.rows[path]]


def test_missing_parent_is_absence_not_success_or_terminal():
    v=Volume({'/':[]})
    assert exists(v,'/input-verification/proof.json') is False
    assert exists(v,'/preprocessing/job/result.json') is False
    v=Volume({'/':[('preprocessing','DIRECTORY')],'/preprocessing':[]})
    assert exists(v,'/preprocessing/job/result.json') is False


def test_existing_nested_proof_and_unexpected_parent_type():
    v=Volume({'/':[('preprocessing','DIRECTORY')],'/preprocessing':[('preprocessing/job','DIRECTORY')],'/preprocessing/job':[('preprocessing/job/result.json','FILE')]})
    assert exists(v,'/preprocessing/job/result.json') is True
    with pytest.raises(ValueError,match='OBSERVATION_PARENT'):
        exists(Volume({'/':[('input-verification','FILE')]}),'/input-verification/proof.json')
    with pytest.raises(RuntimeError):exists(Volume({}),'/input-verification/proof.json')


@pytest.fixture
def activation(setup,tmp_path,monkeypatch):
    from orchestrator import modal_preprocessing_provider as provider,private_records as pr
    p,db=setup;p=copy.deepcopy(p)
    evidence=tmp_path/'receipt.json';pr.write_bytes(evidence,b'original receipt')
    p['evidence_files']={str(evidence):fresh.sha(evidence.read_bytes())}
    db.execute('DELETE FROM events');db.execute("UPDATE autonomy_compute SET status='RUNNING'");db.commit()
    local=sqlite3.connect(':memory:');local.row_factory=sqlite3.Row
    local.execute('CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT)')
    local.execute('INSERT INTO manual_state VALUES(1,?)',(p['old_state_raw'],));local.commit()
    driver=SimpleNamespace(state=tmp_path,config={'run_id':p['old_row']['run']},store=SimpleNamespace(db=local,batch=SimpleNamespace(db=db)))
    driver.current=lambda:json.loads(local.execute('SELECT payload FROM manual_state').fetchone()[0])
    def save(value):local.execute('UPDATE manual_state SET payload=?',(fresh.encoded(value).decode(),));local.commit()
    driver.save=save
    fake=SimpleNamespace(config={},code=137,entries=[])
    fake._sandbox=lambda pid:SimpleNamespace(object_id=pid,poll=lambda:fake.code)
    monkeypatch.setattr(provider,'scope',lambda adapter,config,binding:binding)
    monkeypatch.setattr(provider,'output_volume',lambda adapter,binding:SimpleNamespace(object_id=binding['preprocessing_output_volume_id'],listdir=lambda *a,**k:fake.entries))
    monkeypatch.setattr(fresh,'contract',lambda:p)
    yield p,db,driver,fake,evidence
    local.close()


def test_positive_empty_stop_accounted_without_fabricated_steps_and_idempotent(activation):
    p,db,driver,provider,_=activation
    assert fresh.activate(driver,provider)['status']=='FRESH_START_SELECTED'
    fresh.retained(db,p)
    assert json.loads(db.execute('SELECT payload FROM events').fetchone()[0])==p['event']
    assert driver.current()['preprocessing_dispatch']==json.loads(p['old_state_raw'])['preprocessing_dispatch']
    assert driver.current()['preprocessing_fresh_start']==fresh.marker(p)
    assert (driver.state/'preprocessing-fresh-start/ORIGINAL_STATE.json').read_text()==p['old_state_raw']
    assert not (driver.state/'steps').exists()
    changes=db.total_changes
    assert fresh.activate(driver,provider)['status']=='ALREADY_ACTIVATED'
    assert db.total_changes==changes


@pytest.mark.parametrize('fault',['live','nonempty','receipt','state'])
def test_no_terminal_inference_or_charge_change_on_bad_proof(activation,fault):
    p,db,driver,provider,evidence=activation
    if fault=='live':provider.code=None
    if fault=='nonempty':provider.entries=['unexpected output']
    if fault=='receipt':evidence.write_bytes(b'changed')
    if fault=='state':driver.save({'phase':'EXECUTE_EXPERIMENT'})
    with pytest.raises(ValueError,match='FRESH_PREPROCESSING_'):fresh.activate(driver,provider)
    assert dict(db.execute('SELECT * FROM autonomy_compute').fetchone())==p['old_row']
    assert not db.execute('SELECT 1 FROM events').fetchone()


def test_cross_ledger_interruption_replays_exact_terminal_commit_only(activation):
    p,db,driver,provider,_=activation;save=driver.save
    def crash(value):raise RuntimeError('simulated crash after global terminal commit')
    driver.save=crash
    with pytest.raises(RuntimeError):fresh.activate(driver,provider)
    fresh.retained(db,p)
    assert driver.current()==json.loads(p['old_state_raw'])
    driver.save=save
    assert fresh.activate(driver,provider)['status']=='FRESH_START_SELECTED'
    assert db.execute('SELECT count(*) FROM events').fetchone()[0]==1
    assert db.execute('SELECT reserved_micro_usd FROM autonomy_compute').fetchone()[0]==p['old_row']['reserved_micro_usd']
