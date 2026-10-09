"""Real controller + persistent ledger, synthetic host proof/provider boundary.

No model, network, paid SDK, credentials or patient data are used by this file.
Provider-specific command/output validation is covered in its connected tests.
"""
from types import SimpleNamespace as NS
import json
import pytest
from test_modal_direct_budget import billing, NOW
from orchestrator import modal_environment_inventory as inventory
from orchestrator import modal_environment_budget as budget
from orchestrator import private_records as pr
from orchestrator.modal_assets import BASE_IMAGE
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_budget import ComputeAccounts
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import read, digest
from orchestrator.manual_driver import write_once


@pytest.fixture
def controlled(tmp_path,monkeypatch):
    state=tmp_path/'state';pr.mkdir(state)
    batch=BatchAccounts(tmp_path/'ledger');accounts=ComputeAccounts(batch)
    config={'schema':inventory.SCHEMA,'source':'a'*40,'release':'/opt/synthetic-release',
        'installation_record':'/var/lib/synthetic-install','installation_sha256':'b'*64,
        'state':str(state),'batch_ledger':str(batch.folder),'provider':{},
        'operation_id':budget.OPERATION,'image_id':'im-synthetic',
        'base_image':BASE_IMAGE,'worker_sha256':inventory.native.WORKER_SHA256,'units':{}}
    proof={'status':'PASS','source':config['source'],'installation_sha256':config['installation_sha256'],
           'config_sha256':'c'*64}
    f=NS(state=state,batch=batch,accounts=accounts,config=config,proof=proof,calls=[],outcome='RUNNING')
    f.provider=NS(billing_snapshot=billing)
    def launch(provider,accounts,binding,root):
        inventory.native.require_reserved(accounts,binding)
        pr.mkdir(root);write_once(root/'intent.json',canonical(binding))
        f.calls.append('create')
        if f.outcome=='LOST':raise TimeoutError('synthetic lost reply')
        handle={'binding_sha256':digest(canonical(binding)),'provider_id':'sb-synthetic','app_id':'ap-synthetic',
                'image_id':binding['image_id']}
        write_once(root/'sandbox.json',canonical(handle));return handle
    def observe(provider,binding,handle,root):
        return {'status':f.outcome,'provider_id':handle['provider_id'],'no_automatic_retry':True}
    monkeypatch.setattr(inventory.native,'launch',launch)
    monkeypatch.setattr(inventory.native,'observe',observe)
    yield f
    batch.db.close()


def tick(f):return inventory.tick(f.config,f.provider,f.accounts,host_proof=f.proof,now=NOW)


def test_controller_completes_exactly_once_without_scientific_allowance(controlled):
    f=controlled
    assert tick(f)['status']=='RUNNING'
    assert tick(f)['status']=='RUNNING'
    with pytest.raises(ValueError,match='^ADMINISTRATIVE_INPUT_OWNER_CANNOT_ADMIT_SCIENCE$'):
        f.batch.reserve_scientific('forbidden',budget.RUN,'run_spec_author','a'*40,{})
    f.outcome='VERIFIED';result=tick(f)
    before=[tuple(x) for x in f.batch.db.execute('select * from autonomy_assets')]
    assert tick(f)==result
    assert [tuple(x) for x in f.batch.db.execute('select * from autonomy_assets')]==before
    assert f.batch.db.execute('select count(*) from autonomy_calls').fetchone()[0]==0
    assert f.batch.db.execute('select status from autonomy_runs').fetchone()[0]=='COMPLETE'
    assert f.calls==['create'];pr.check_tree(f.state)


def test_lost_create_retains_reservation_and_never_creates_again(controlled):
    f=controlled;f.outcome='LOST'
    with pytest.raises(TimeoutError):tick(f)
    assert tick(f)['status']=='BLOCKED_CREATE_UNCERTAIN'
    assert tick(f)['status']=='BLOCKED_CREATE_UNCERTAIN'
    assert f.calls==['create']
    assert f.batch.db.execute('select status from autonomy_assets').fetchone()[0]=='RESERVED'


def test_terminal_failure_is_preserved_with_full_charge_and_no_retry(controlled):
    f=controlled;f.outcome='UNCERTAIN'
    assert tick(f)['status']=='UNCERTAIN'
    row=f.batch.db.execute('select * from autonomy_assets').fetchone()
    assert row['status']=='UNCERTAIN' and row['reserved_micro_usd']>0
    assert tick(f)['status']=='BLOCKED_PRESERVED_FAILURE' and f.calls==['create']
    assert read(f.state/'FAILED.json')['status']=='UNCERTAIN'


@pytest.mark.parametrize('field,value', [('source','d'*40),('image_id','im-changed'),
    ('worker_sha256','d'*64),('operation_id','another'),('base_image','unselected')])
def test_selection_change_never_creates_another_attempt(controlled,field,value):
    f=controlled;tick(f);f.config[field]=value
    with pytest.raises(ValueError,match='^ENVIRONMENT_INVENTORY_'):tick(f)
    assert f.calls==['create']


def test_halt_and_host_proof_refuse_before_register_or_reserve(controlled):
    f=controlled;f.proof['status']='FAIL'
    with pytest.raises(ValueError,match='^ENVIRONMENT_INVENTORY_HOST_PROOF$'):tick(f)
    f.proof['status']='PASS';pr.write_bytes(f.batch.folder/'HALT',b'halt')
    with pytest.raises(ValueError,match='^AUTONOMY_BATCH_HALTED$'):tick(f)
    assert f.calls==[]
    assert f.batch.db.execute('select count(*) from autonomy_assets').fetchone()[0]==0
    assert f.batch.db.execute('select count(*) from autonomy_runs').fetchone()[0]==0


def test_changed_saved_outcome_refuses_without_recharging(controlled):
    f=controlled;f.outcome='VERIFIED';tick(f)
    original=(f.state/'VERIFIED.json').read_bytes()
    changed=json.loads(original);changed['source']='d'*40
    pr.write_bytes(f.state/'VERIFIED.json',canonical(changed))
    with pytest.raises(ValueError):tick(f)
    assert f.calls==['create']


def test_any_no_science_owner_cannot_reserve_scientific_call(tmp_path):
    batch=BatchAccounts(tmp_path/'ledger')
    try:
        batch.register_run('administrative-only',{'no_scientific_allowance':True})
        with pytest.raises(ValueError,match='^ADMINISTRATIVE_INPUT_OWNER_CANNOT_ADMIT_SCIENCE$'):
            batch.reserve_scientific('forbidden','administrative-only','run_spec_author','a'*40,{})
        assert batch.db.execute('select count(*) from autonomy_calls').fetchone()[0]==0
    finally:batch.db.close()


# Full producer/consumer chain below uses the actual controller, budget,
# provider and capture validation. Only the paid SDK endpoint is synthetic.
from test_modal_environment_provider import fixture as provider_fixture, Stream


def test_real_controller_provider_receipt_accounting_chain(provider_fixture,tmp_path):
    f=provider_fixture
    for table in ('events','autonomy_assets','autonomy_runs'):
        f.accounts.db.execute('DELETE FROM '+table)
    state=tmp_path/'controller';pr.mkdir(state)
    config={'schema':inventory.SCHEMA,'source':'a'*40,'release':'/opt/synthetic-release',
        'installation_record':'/var/lib/synthetic-install','installation_sha256':'c'*64,
        'state':str(state),'batch_ledger':str(f.accounts.batch.folder),'provider':{},
        'operation_id':budget.OPERATION,'image_id':f.binding['image_id'],
        'base_image':BASE_IMAGE,'worker_sha256':inventory.native.WORKER_SHA256,'units':{}}
    proof={'status':'PASS','source':config['source'],'installation_sha256':config['installation_sha256'],
           'config_sha256':'b'*64}
    f.provider.billing_snapshot=billing
    # Actual subprocess executes only the fixed stdlib inventory on this host;
    # this proves code/format compatibility, not the remote image's environment.
    import subprocess
    worker=subprocess.run(['/usr/bin/python3','-I','-B','-c',inventory.native.WORKER,
                           inventory.native.WORKER_SHA256,f.binding['image_id']],
                          capture_output=True,timeout=30)
    assert worker.returncode==0 and not worker.stderr
    f.sb.stdout=Stream([worker.stdout])
    result=inventory.tick(config,f.provider,f.accounts,host_proof=proof,now=NOW)
    assert result['status']=='VERIFIED'
    before=[tuple(row) for row in f.accounts.db.execute('SELECT * FROM autonomy_assets')]
    calls=list(f.calls)
    assert inventory.tick(config,f.provider,f.accounts,host_proof=proof,now=NOW)==result
    assert f.calls==calls and f.sb.stdout.reads==1
    assert sum(row[0]=='create' for row in f.calls)==1
    assert [tuple(row) for row in f.accounts.db.execute('SELECT * FROM autonomy_assets')]==before
    assert f.accounts.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    pr.write_bytes(state/'provider/stdout.bin',b'changed retained output')
    with pytest.raises(ValueError,match='^ENVIRONMENT_PRESERVED_OUTPUT_CHANGED$'):
        inventory.tick(config,f.provider,f.accounts,host_proof=proof,now=NOW)
    assert f.calls==calls


@pytest.mark.parametrize('completed',[False,True])
@pytest.mark.parametrize('drift,code',[('amount','ENVIRONMENT_INVENTORY_ASSET_COST'),
    ('owner','ENVIRONMENT_INVENTORY_OWNER_CHANGED'),('owner-status','ENVIRONMENT_INVENTORY_OWNER_CHANGED')])
def test_charge_and_owner_drift_refuses_every_reentry(controlled,completed,drift,code):
    f=controlled
    if completed:f.outcome='VERIFIED'
    tick(f)
    if drift=='amount':f.batch.db.execute('UPDATE autonomy_assets SET reserved_micro_usd=0')
    elif drift=='owner':f.batch.db.execute("UPDATE autonomy_runs SET binding='{}'")
    else:f.batch.db.execute("UPDATE autonomy_runs SET status='UNKNOWN'")
    events=[tuple(r) for r in f.batch.db.execute('SELECT * FROM events')]
    with pytest.raises(ValueError,match='^'+code+'$'):tick(f)
    assert f.calls==['create'] and [tuple(r) for r in f.batch.db.execute('SELECT * FROM events')]==events


@pytest.mark.parametrize('boundary',['before-accounting','after-accounting','before-owner'])
def test_terminal_crash_windows_resume_without_new_call_or_charge(controlled,monkeypatch,boundary):
    f=controlled;f.outcome='VERIFIED';once=[True]
    if boundary=='before-owner':
        original=f.batch.complete_run
        def fail(*a,**kw):
            if once[0]:once[0]=False;raise RuntimeError('injected crash before owner completion')
            return original(*a,**kw)
        monkeypatch.setattr(f.batch,'complete_run',fail)
    else:
        original=f.accounts.finish_assets
        def fail(*a,**kw):
            if once[0]:
                once[0]=False
                if boundary=='after-accounting':original(*a,**kw)
                raise RuntimeError('injected accounting crash')
            return original(*a,**kw)
        monkeypatch.setattr(f.accounts,'finish_assets',fail)
    with pytest.raises(RuntimeError,match='injected'):tick(f)
    amount=f.batch.db.execute('SELECT reserved_micro_usd FROM autonomy_assets').fetchone()[0]
    assert tick(f)['status']=='VERIFIED'
    assert tick(f)['status']=='VERIFIED'
    assert f.calls==['create']
    rows=f.batch.db.execute('SELECT * FROM autonomy_assets').fetchall()
    assert len(rows)==1 and rows[0]['status']=='READY' and rows[0]['reserved_micro_usd']==amount
    assert f.batch.db.execute("SELECT count(*) FROM events WHERE id LIKE '%:assets-reserved'").fetchone()[0]==1


def test_halt_appearing_after_reservation_prevents_create(controlled,monkeypatch):
    f=controlled;original=inventory.budget.reserve
    def halt(*a,**kw):
        result=original(*a,**kw)
        pr.write_bytes(f.batch.folder/'HALT',b'halt after reservation')
        return result
    monkeypatch.setattr(inventory.budget,'reserve',halt)
    assert tick(f)['status']=='HALTED' and f.calls==[]
    assert f.batch.db.execute('SELECT status FROM autonomy_assets').fetchone()[0]=='RESERVED'


def test_host_proof_hashes_trusted_config_separately_from_unit_files(tmp_path,monkeypatch):
    from pathlib import Path
    # Root ownership, systemd properties and installed source receipt are host
    # fixture boundaries. Actual trusted file bytes/hash checks run unchanged.
    root=tmp_path/'host';pr.mkdir(root)
    config={'schema':inventory.SCHEMA,'source':'a'*40,'release':str(Path(inventory.__file__).resolve().parents[1]),
        'installation_record':str(root/'installation'),'installation_sha256':'pending',
        'state':str(root/'state'),'batch_ledger':str(root/'ledger'),'provider':{},
        'operation_id':budget.OPERATION,'image_id':'im-synthetic','base_image':BASE_IMAGE,
        'worker_sha256':inventory.native.WORKER_SHA256,'units':{}}
    installed=root/'installation/installed.json';pr.write_bytes(installed,b'{"synthetic_host_receipt":true}')
    config['installation_sha256']=digest(installed.read_bytes())
    name=inventory.unit_name(config);unit=root/name;pr.write_bytes(unit,b'[Service]\nUser=partho\n')
    config['units']={name:{'sha256':digest(unit.read_bytes())}}
    path=root/'config.json';pr.write_bytes(path,canonical(config))
    def trusted(p):
        p=Path(p)
        if p==Path('/etc/systemd/system')/name:p=unit
        return pr.check(p)
    monkeypatch.setattr('orchestrator.manual_host_guard.trusted',trusted)
    monkeypatch.setattr('tools.manual_promotion.manifest_check',lambda *a:{'source':config['source'],'layout':{'release':config['release']}})
    monkeypatch.setattr(inventory,'os',NS(getuid=lambda:1003))
    monkeypatch.setattr(inventory,'sys',NS(flags=NS(no_user_site=1)))
    props={'User':'partho','Group':'partho','UMask':'0077','NoNewPrivileges':'yes','ProtectSystem':'strict',
        'PrivateTmp':'yes','ProtectHome':'read-only','RestrictSUIDSGID':'yes','LockPersonality':'yes'}
    monkeypatch.setattr(inventory,'subprocess',NS(check_output=lambda *a,**k:'\n'.join(k+'='+v for k,v in props.items())))
    selected,proof=inventory.host_check(path)
    assert selected==config
    assert proof['config_sha256']==digest(path.read_bytes())
    assert proof['config_sha256']!=config['units'][name]['sha256']
    # Unit files retain their independent config-bound hash checks.
    pr.write_bytes(unit,b'[Service]\nUser=changed\n')
    with pytest.raises(ValueError,match='ENVIRONMENT_INVENTORY_UNIT_CHANGED'):inventory.host_check(path)
