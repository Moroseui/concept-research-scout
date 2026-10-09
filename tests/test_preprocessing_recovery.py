"""Real worker, terminal reader and SQLite continuation; synthetic science/SDK only."""
import copy
import json
import subprocess
import sys
from pathlib import Path
import pytest
from orchestrator import private_records as pr, preprocessing_recovery as recovery
from orchestrator import preprocessing_checkpoints as checkpoints, experiment_worker as worker
from orchestrator import modal_preprocessing_provider as pp
from orchestrator.modal_executor import canonical,item4_job,ModalExecutor
from orchestrator.manual_executor import digest,inventory
from orchestrator.modal_scientific_environment import environment_bytes
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_item4_budget import AUTHORITY
from test_modal_preprocessing_provider import connection,candidate
from test_experiment_preprocessing import prepared
from test_modal_development_inputs import inventory as input_inventory,synthetic_provider
# fixture requested by synthetic_provider is named inventory in its module.
from test_modal_development_inputs import inventory


def hard_stop(package,inputs,progress,binding,*,before_publish=False):
    ident=digest(canonical(binding));b=binding
    code="""import sys,os
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from orchestrator import experiment_preprocessing as prep
import run as worker # Actual packaged worker filename, not its source-tree import path.
prep.COHORT=sys.argv[5];prep.SOURCE=sys.argv[6]
def external_stop(path):
 if len(list((Path(path)/'preprocessing'/sys.argv[7]/'steps').glob('*.json')))>=2:os._exit(137)
if sys.argv[8]=='publish':
 original=os.rename
 def interrupted_rename(source,target):
  if len(list((Path(target).parent).glob('*.json')))>=2:os._exit(137)
  return original(source,target)
 prep.os.rename=interrupted_rename # Synthetic interruption at atomic publication boundary.
 prep.commit=lambda path:None
else:prep.commit=external_stop # Synthetic external hard stop instead of a live Volume commit.
worker.execute(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[7])
"""
    child=subprocess.run([sys.executable,'-I','-B','-c',code,str(package),str(inputs),str(progress),
        'synthetic-stop',b['preprocessing']['cohort_sha256'],b['preprocessing']['source_capture_sha256'],ident,'publish' if before_publish else 'commit'],
        capture_output=True,text=True,timeout=30)
    assert child.returncode==137,child.stderr
    return ident


def killed(connection):
    p,c,b,package,inputs,progress,created,calls,volume,proofs=connection
    ident=proofs()
    hard_stop(package,inputs,progress,b)
    attempt=progress/'preprocessing'/ident
    assert not (attempt/'failed.json').exists() and not (attempt/'result.json').exists()
    assert len(list((attempt/'steps').glob('*.json')))==2
    p._sandbox('sb-preprocessing').poll=lambda:137
    return ident,attempt


def linked(b,proof):
    new=copy.deepcopy(b);new['experiment']['segment']+=1
    new['resume']={'previous_segment_id':digest(canonical(b)),'terminal_receipt_sha256':'e'*64,
                  'steps_record_sha256':proof['steps_record_sha256']}
    return new


def next_package(connection,new,tmp_path):
    p,c,b,package,inputs,progress,*_=connection
    target=tmp_path/'resumed-package';pr.copytree(package,target)
    manifest=json.loads((target/'manifest.json').read_bytes());manifest['binding']=new
    pr.write_bytes(target/'manifest.json',canonical(manifest))
    ident=digest(canonical(new));env=new['scientific_environment']
    proof={'schema':'scientific-environment-proof/v1','binding_sha256':ident,
        'expected_sha256':digest(environment_bytes(env['expected'])),'actual':env['expected'],'offline':True}
    pr.write_bytes(progress/'environment-verification'/ident/'environment.json',environment_bytes(proof))
    guard=pp.payload(p,new);files=pp.input_files(c,new)
    observed={'schema':'modal-input-verification/v1',**{k:guard[k] for k in ('binding_sha256','guard_sha256','preprocessing_sha256')},
        'inventory_sha256':digest(canonical(files)),'file_count':len(files),'total_bytes':sum(v['bytes'] for v in files.values()),
        'volume_ids':guard['volume_ids'],'scientific_environment_sha256':digest(canonical(env)),'status':'VERIFIED','reason':None}
    pr.write_bytes(progress/'input-verification'/(ident+'.json'),canonical(observed))
    return target,ident


def test_hard_interruption_resume_reuses_verified_steps_preserves_originals_and_validates(connection,tmp_path):
    p,c,b,package,inputs,progress,created,calls,volume,proofs=connection
    ident,old=killed(connection);before={str(x.relative_to(old)):digest(x.read_bytes()) for x in old.rglob('*') if x.is_file()}
    proof=p.terminal_preprocessing_steps('sb-preprocessing',b)
    assert len(proof['snapshot']['steps'])==2 and proof['may_launch'] is False
    assert not any('/artifacts/' in path for path in volume.reads)
    new=linked(b,proof);target,pin=next_package(connection,new,tmp_path)
    result=worker.execute(target,inputs,progress,pin)
    assert result['status']=='VALIDATED' and result['steps']==100 and result['files']==300
    inherited=json.loads((progress/'preprocessing'/pin/'inherited.json').read_bytes())
    assert inherited['snapshot']==proof['snapshot']
    assert before=={str(x.relative_to(old)):digest(x.read_bytes()) for x in old.rglob('*') if x.is_file()}
    for step in proof['snapshot']['steps'].values():
        for name in step['files']:
            assert (old/'artifacts'/name).stat().st_ino!=(progress/'preprocessing'/pin/'artifacts'/name).stat().st_ino
    assert p.status('sb-preprocessing',new)['status']=='COMPLETE'
    with pytest.raises(FileExistsError):worker.execute(target,inputs,progress,pin)
    assert not created and not calls


@pytest.mark.parametrize('damage,code',[
    ('active','PREPROCESSING_NOT_PROVEN_INTERRUPTED'),('zero','PREPROCESSING_NOT_PROVEN_INTERRUPTED'),
    ('wrong-provider','MODAL_FIT_SANDBOX_ID_CHANGED'),('failed','PREPROCESSING_PREDECESSOR_NOT_INTERRUPTED'),
    ('validated','PREPROCESSING_PREDECESSOR_NOT_INTERRUPTED'),('binding','PREPROCESSING_PREDECESSOR_CHANGED'),
    ('step','PREPROCESSING_STEP_BINDING'),('missing-file','PREPROCESSING_COMMITTED_BYTES_CHANGED')])
def test_terminal_refusals_never_create_resume_authority(connection,damage,code):
    p,c,b,package,inputs,progress,created,calls,volume,proofs=connection;ident,old=killed(connection)
    if damage in {'active','zero'}:p._sandbox('sb-preprocessing').poll=lambda:None if damage=='active' else 0
    if damage=='wrong-provider':p._sandbox('sb-preprocessing').object_id='sb-other'
    if damage=='failed':pr.write_bytes(old/'failed.json',b'{}')
    if damage=='validated':pr.write_bytes(old/'author-validation.json',b'{}')
    if damage=='binding':pr.write_bytes(old/'binding.json',b'{}')
    if damage=='step':
        path=next((old/'steps').glob('*.json'));value=json.loads(path.read_bytes());value['binding_sha256']='f'*64;pr.write_bytes(path,canonical(value))
    if damage=='missing-file':next(x for x in (old/'artifacts').rglob('*') if x.is_file()).unlink()
    with pytest.raises(ValueError,match='^'+code+'$'):p.terminal_preprocessing_steps('sb-preprocessing',b)
    assert not created and not calls


@pytest.mark.parametrize('damage,code',[
    ('bytes','PREPROCESSING_COMMITTED_BYTES_CHANGED'),('snapshot','PREPROCESSING_STEPS_CHANGED'),
    ('selection','PREPROCESSING_RESUME_IDENTITY_CHANGED'),('skip-segment','PREPROCESSING_RESUME_SEGMENT')])
def test_worker_refuses_changed_predecessor_before_science(connection,tmp_path,damage,code):
    p,c,b,package,inputs,progress,*_=connection;_,old=killed(connection)
    proof=p.terminal_preprocessing_steps('sb-preprocessing',b);new=linked(b,proof)
    if damage=='bytes':
        path=next(x for x in (old/'artifacts').rglob('*') if x.is_file());pr.write_bytes(path,b'x'*path.stat().st_size)
    if damage=='snapshot':new['resume']['steps_record_sha256']='f'*64
    if damage=='selection':new['resources']['cpu']+=1
    if damage=='skip-segment':new['experiment']['segment']+=1
    target,pin=next_package(connection,new,tmp_path)
    with pytest.raises(ValueError,match='^'+code+'$'):worker.execute(target,inputs,progress,pin)
    assert not (progress/'preprocessing'/pin/'result.json').exists()


def test_real_ledger_preserves_charge_and_admits_one_linked_segment(connection,tmp_path,monkeypatch):
    from orchestrator import connectivity
    p,c,b,package,inputs,progress,created,calls,volume,proofs=connection
    monkeypatch.setattr(connectivity,'require',lambda *a,**k:None) # No network in fixture.
    batch=BatchAccounts(tmp_path/'batch');batch.register_run(b['run_id'],{'backlog_item':4,'experiment_authority_sha256':AUTHORITY})
    e=ModalExecutor(tmp_path/'lane/jobs.sqlite',c,p,batch);job=item4_job(b)
    p._sandbox('sb-preprocessing').object_id='sb-synthetic'
    assert e.submit(job,b,package,tmp_path/'submitted')['status']=='SUBMITTED'
    ident,old=killed(connection)
    reason=tmp_path/'reason.json';pr.write_bytes(reason,canonical({'schema':'modal-interruption-cause/v1',
        'segment_id':ident,'provider_id':'sb-synthetic','reason':'DELIBERATE_SMOKE_INTERRUPTION',
        'evidence':{'synthetic_hard_stop_exit':137,'fixture_not_live_provider':True}}))
    before=dict(batch.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone())
    saved=recovery.record(e.costs,ident,p,reason_record=reason)
    assert recovery.record(e.costs,ident,p,reason_record=reason)==saved
    after=dict(batch.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone())
    assert after=={**before,'status':'ACCOUNTED'}
    raw=batch.db.execute('SELECT payload FROM events WHERE id=?',(ident+':preprocessing-interruption',)).fetchone()[0]
    new=linked(b,saved['proof']);new['resume']['terminal_receipt_sha256']=digest(raw.encode())
    target,pin=next_package(connection,new,tmp_path)
    assert e.costs.reserve_item4(pin,b['run_id'],new,billing_snapshot=p.billing_snapshot())
    assert not e.costs.reserve_item4(pin,b['run_id'],new,billing_snapshot=p.billing_snapshot())
    assert batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==2
    assert dict(batch.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone())==after
    assert len(created)==len(calls)==1
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0


def test_interrupted_step_publication_keeps_last_committed_steps_usable(connection,tmp_path):
    p,c,b,package,inputs,progress,*_=connection;ident=connection[-1]()
    hard_stop(package,inputs,progress,b,before_publish=True)
    old=progress/'preprocessing'/ident
    assert len(list((old/'steps').glob('*.json')))==2
    assert len(list((old/'step-records-pending').glob('*.json')))==1
    originals={str(x.relative_to(old)):digest(x.read_bytes()) for x in old.rglob('*') if x.is_file()}
    p._sandbox('sb-preprocessing').poll=lambda:137
    proof=p.terminal_preprocessing_steps('sb-preprocessing',b)
    new=linked(b,proof);target,pin=next_package(connection,new,tmp_path)
    assert worker.execute(target,inputs,progress,pin)['status']=='VALIDATED'
    assert originals=={str(x.relative_to(old)):digest(x.read_bytes()) for x in old.rglob('*') if x.is_file()}


def test_root_reconciliation_command_refuses_before_opening_owner_ledger(tmp_path,monkeypatch):
    from orchestrator import experiment_driver
    monkeypatch.setattr(experiment_driver.os,'geteuid',lambda:0)
    calls=[];monkeypatch.setattr(experiment_driver,'ExperimentDriver',lambda *a:calls.append(a))
    with pytest.raises(ValueError,match='^EXPERIMENT_PREPARATION_OWNER_REQUIRED$'):
        experiment_driver.main(['reconcile-preprocessing','--state',str(tmp_path),'--job','synthetic','--reason','unused'])
    assert calls==[]


@pytest.mark.parametrize('damage,code',[
    ('missing-event','PREPROCESSING_TERMINAL_PROOF_REQUIRED'),('event-pin','PREPROCESSING_RESUME_BINDING'),
    ('reason','PREPROCESSING_RESUME_BINDING'),('identity','PREPROCESSING_RESUME_IDENTITY_CHANGED'),
    ('HALT','AUTONOMY_BATCH_HALTED'),('cap','ITEM4_HARD_COST_CAP')])
def test_no_resume_reservation_on_changed_proof_identity_or_controls(connection,tmp_path,monkeypatch,damage,code):
    from orchestrator import connectivity
    p,c,b,package,inputs,progress,*_=connection
    monkeypatch.setattr(connectivity,'require',lambda *a,**k:None)
    batch=BatchAccounts(tmp_path/'batch');batch.register_run(b['run_id'],{'backlog_item':4,'experiment_authority_sha256':AUTHORITY})
    e=ModalExecutor(tmp_path/'lane/jobs.sqlite',c,p,batch);job=item4_job(b)
    p._sandbox('sb-preprocessing').object_id='sb-synthetic';e.submit(job,b,package,tmp_path/'submitted')
    ident,_=killed(connection);reason=tmp_path/'reason.json'
    pr.write_bytes(reason,canonical({'schema':'modal-interruption-cause/v1','segment_id':ident,
        'provider_id':'sb-synthetic','reason':'DELIBERATE_SMOKE_INTERRUPTION','evidence':{'synthetic':True}}))
    saved=recovery.record(e.costs,ident,p,reason_record=reason)
    raw=batch.db.execute('SELECT payload FROM events WHERE id=?',(ident+':preprocessing-interruption',)).fetchone()[0]
    new=linked(b,saved['proof']);new['resume']['terminal_receipt_sha256']=digest(raw.encode())
    if damage=='missing-event':batch.db.execute('DELETE FROM events WHERE id=?',(ident+':preprocessing-interruption',))
    if damage=='event-pin':new['resume']['terminal_receipt_sha256']='f'*64
    if damage=='reason':
        saved['resume_reason']='UNKNOWN';batch.db.execute('UPDATE events SET payload=? WHERE id=?',(json.dumps(saved),ident+':preprocessing-interruption'))
    if damage=='identity':new['code_sha256']='f'*64
    if damage=='HALT':pr.write_text(batch.folder/'HALT','Synthetic hold')
    if damage=='cap':batch.db.execute("INSERT INTO autonomy_assets VALUES('synthetic-cap',?,'{}','READY',75000000,'{}')",(b['run_id'],))
    before=[tuple(row) for row in batch.db.execute('SELECT * FROM autonomy_compute')]
    with pytest.raises(ValueError,match='^'+code+'$'):
        e.costs.reserve_item4(digest(canonical(new)),b['run_id'],new,billing_snapshot=p.billing_snapshot())
    assert before==[tuple(row) for row in batch.db.execute('SELECT * FROM autonomy_compute')]
