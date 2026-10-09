"""Exact fixed retry on synthetic ledgers; all original charges retained."""
import copy
import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import item4_private_staging_retry as retry, item4_preprocessing_fresh_start as first
from orchestrator.modal_executor import item4_job
from test_item4_preprocessing_fresh_start import setup as first_setup


@pytest.fixture
def setup(first_setup,monkeypatch):
    original,db=first_setup
    monkeypatch.setattr(retry,'ROOT',Path(__file__).resolve().parents[1])
    monkeypatch.setattr(retry,'authority',lambda:{'report_sha256':'b'*64})
    monkeypatch.setattr(retry,'previous',lambda:first)
    p=retry.contract();row={**p['old_row'],'status':'ACCOUNTED'}
    db.execute('INSERT INTO autonomy_compute VALUES(?,?,?,?,?,?,?,?)',tuple(row[k] for k in ['id','run','binding','status','reserved_micro_usd','provider_id','actual_micro_usd','month']))
    db.execute('INSERT INTO events VALUES(?,?,?)',(row['id']+':pre-science-stop',row['run'],retry.encoded(p['event']).decode()));db.commit()
    return p,db


def rows(db):return [(r,json.loads(r['binding'])) for r in db.execute('SELECT * FROM autonomy_compute')]


def test_exact_second_recovery_preserves_both_charges(setup):
    p,db=setup;before=db.total_changes
    retry.validate_reservation(NS(db=db),rows(db),p['new_binding'])
    assert db.total_changes==before
    assert sum(r['reserved_micro_usd'] for r,_ in rows(db))==20_684_800
    assert item4_job(p['new_binding'])==p['new_job']!=p['old_job']
    assert retry.terminal_contract(NS(db=db),p['old_row']['id'])==p


@pytest.mark.parametrize('fault',['first-live','second-live','first-charge','second-charge','first-event','second-event','missing-predecessor','extra-predecessor','changed-input','changed-science','changed-image','changed-cpu','full','foreign-cost'])
def test_unknown_or_changed_attempts_fail_closed(setup,fault):
    p,db=setup;b=copy.deepcopy(p['new_binding']);selected=rows(db)
    ids=[first.contract()['old_row']['id'],p['old_row']['id']]
    if fault.endswith('-live'):db.execute("UPDATE autonomy_compute SET status='RUNNING' WHERE id=?",(ids[fault.startswith('second')],))
    if fault.endswith('-charge'):db.execute('UPDATE autonomy_compute SET reserved_micro_usd=1 WHERE id=?',(ids[fault.startswith('second')],))
    if fault.endswith('-event'):db.execute('DELETE FROM events WHERE id=?',(ids[fault.startswith('second')]+':pre-science-stop',))
    if fault=='missing-predecessor':selected=selected[:1]
    if fault=='extra-predecessor':selected=selected+selected[:1]
    if fault=='changed-input':b['source_volume_id']='vo-wrong'
    if fault=='changed-science':b['execution']['module_sha256']='0'*64
    if fault=='changed-image':b['image_id']='im-wrong'
    if fault=='changed-cpu':b['resources']['cpu']=1
    if fault=='full':b['experiment']['stage']='FULL'
    with pytest.raises(ValueError):
        if fault=='foreign-cost':retry.terminal_contract(NS(db=db),'0'*64)
        else:retry.validate_reservation(NS(db=db),selected,b)


@pytest.fixture
def activation(setup,tmp_path,monkeypatch):
    from orchestrator import private_records as pr,modal_preprocessing_provider as pp
    p,db=setup;p=copy.deepcopy(p);ident=p['old_row']['id']
    proof=b'{"status":"VERIFIED"}';environment=b'{"synthetic_environment":true}'
    p['event']['input_proof_sha256']=retry.sha(proof);p['event']['environment_proof_sha256']=retry.sha(environment)
    evidence=tmp_path/'synthetic-receipt.json';pr.write_bytes(evidence,b'original synthetic receipt')
    p['evidence_files']={str(evidence):retry.sha(evidence.read_bytes())}
    db.execute('DELETE FROM events WHERE id=?',(ident+':pre-science-stop',));db.execute("UPDATE autonomy_compute SET status='RUNNING' WHERE id=?",(ident,));db.commit()
    local=sqlite3.connect(':memory:');local.row_factory=sqlite3.Row
    local.execute('CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT)');local.execute('INSERT INTO manual_state VALUES(1,?)',(p['old_state_raw'],));local.commit()
    driver=NS(state=tmp_path,config={'run_id':p['old_row']['run']},store=NS(db=local,batch=NS(db=db)))
    driver.current=lambda:json.loads(local.execute('SELECT payload FROM manual_state').fetchone()[0])
    def save(value):local.execute('UPDATE manual_state SET payload=?',(retry.encoded(value).decode(),));local.commit()
    driver.save=save
    fake=NS(config={},code=137,proof=proof,environment=environment)
    fake.entries=[NS(path=n,type=NS(name=t)) for n,t in [('input-verification','DIRECTORY'),('environment-verification','DIRECTORY'),('environment-verification/'+ident,'DIRECTORY'),('input-verification/'+ident+'.json','FILE'),('environment-verification/'+ident+'/environment.json','FILE')]]
    fake._sandbox=lambda pid:NS(object_id=pid,poll=lambda:fake.code)
    monkeypatch.setattr(pp,'scope',lambda *args:args[-1])
    monkeypatch.setattr(pp,'output_volume',lambda adapter,b:NS(object_id=b['preprocessing_output_volume_id'],listdir=lambda *a,**k:fake.entries))
    monkeypatch.setattr(pp,'input_proof',lambda *args:fake.proof)
    monkeypatch.setattr(pp,'record',lambda *args:fake.environment)
    monkeypatch.setattr(pp,'environment_proof',lambda *args:None) # labelled synthetic dependency proof only
    monkeypatch.setattr(retry,'contract',lambda:p)
    yield p,db,driver,fake,evidence
    local.close()


def test_terminal_reconcile_is_idempotent_preserves_first_and_has_no_steps(activation):
    p,db,driver,provider,_=activation;original=rows(db)[0][0];prior_marker=driver.current()['preprocessing_fresh_start']
    assert retry.activate(driver,provider)['status']=='FRESH_START_SELECTED'
    retry.retained(db,p)
    assert driver.current()['preprocessing_fresh_start']==prior_marker
    assert driver.current()['preprocessing_dispatch']==json.loads(p['old_state_raw'])['preprocessing_dispatch']
    assert dict(rows(db)[0][0])==dict(original)
    assert sum(r['reserved_micro_usd'] for r,_ in rows(db))==20_684_800
    assert not (driver.state/'steps').exists()
    before=db.total_changes;assert retry.activate(driver,provider)['status']=='ALREADY_ACTIVATED';assert db.total_changes==before


@pytest.mark.parametrize('fault',['live','extra-output','duplicate-output','input-proof','environment-proof','receipt','state'])
def test_terminal_or_proof_mismatch_cannot_change_ledger(activation,fault):
    p,db,driver,provider,evidence=activation;before=[dict(r) for r,_ in rows(db)]
    if fault=='live':provider.code=None
    if fault=='extra-output':provider.entries.append(NS(path='preprocessing/unexpected',type=NS(name='FILE')))
    if fault=='duplicate-output':provider.entries.append(provider.entries[-1])
    if fault=='input-proof':provider.proof=b'{"status":"FAILED"}'
    if fault=='environment-proof':provider.environment=b'changed'
    if fault=='receipt':evidence.write_bytes(b'changed')
    if fault=='state':driver.save({'phase':'EXECUTE_EXPERIMENT'})
    with pytest.raises(ValueError):retry.activate(driver,provider)
    assert [dict(r) for r,_ in rows(db)]==before


def test_global_commit_before_local_crash_replays_without_second_charge(activation):
    p,db,driver,provider,_=activation;save=driver.save
    def crash(value):raise RuntimeError('synthetic crash after global commit')
    driver.save=crash
    with pytest.raises(RuntimeError):retry.activate(driver,provider)
    retry.retained(db,p);driver.save=save
    assert retry.activate(driver,provider)['status']=='FRESH_START_SELECTED'
    assert db.execute("SELECT count(*) FROM events WHERE id LIKE '%:pre-science-stop'").fetchone()[0]==2
    assert sum(r['reserved_micro_usd'] for r,_ in rows(db))==20_684_800
