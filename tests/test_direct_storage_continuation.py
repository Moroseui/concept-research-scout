"""Real scratch promotion records + SQLite; synthetic root/systemd provenance.

No credential, HTTP or provider call. The controller test fakes only installed
root provenance and the paid SDK (as the existing controller fixture does).
"""
import copy
import hashlib
import json
from pathlib import Path
import pytest
from test_direct_storage_service import installed
from test_modal_ctp_download import planned
from test_modal_direct_storage import controlled,fixture,finish
from test_modal_direct_budget import NOW,billing
from orchestrator import private_records,modal_direct_continuation as c,modal_direct_storage as storage
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_budget import ComputeAccounts
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest,read
from orchestrator import modal_direct_budget as budget
from tools import direct_storage_service as deploy


@pytest.fixture
def prepared(installed):
    root,old=installed;first=deploy.install(root,old)
    old=read(root/first['config'].lstrip('/'))
    ref={'config':first['config'],'config_sha256':digest((root/first['config'].lstrip('/')).read_bytes())}
    state=root/old['state'].lstrip('/')
    binding={'purpose':budget.PURPOSE,'authority_sha256':budget.AUTHORITY,
        'download_authority_sha256':budget.DOWNLOAD_AUTHORITY,'team_authority_sha256':budget.TEAM_AUTHORITY,
        'run_id':'synthetic-same-owner','source':old['source'],'download_bytes':123,
        'envelope':budget.envelope(123,billing()['rates']),
        'package_manifest_sha256':old['package_manifest_sha256'],
        'installed_config_sha256':ref['config_sha256'],'asset_expires_utc':'2026-11-05T09:23:30+00:00'}
    for name,raw in [('binding.json',canonical(binding)),('initial-billing.json',canonical(billing())),
                     ('connectivity.json',b'{}'),('tick.lock',b'')]:private_records.write_bytes(state/name,raw)
    ref['binding_sha256']=digest((state/'binding.json').read_bytes())
    batch=BatchAccounts(root/old['batch_ledger'].lstrip('/'));ComputeAccounts(batch)
    batch.register_run(binding['run_id'],c.owner(binding))
    new={k:v for k,v in old.items() if k!='units'}
    new.update(source='c'*40,release='/opt/research-system/manual-sprint10/synthetic-successor',
               installation_record='/var/lib/research-system-manual-sprint10-deployment/synthetic-successor',prepared_from=ref)
    release=root/new['release'].lstrip('/');private_records.mkdir(release/'orchestrator',parents=True)
    module=release/'orchestrator/modal_direct_storage.py';private_records.write_bytes(module,b'# synthetic successor')
    record=root/new['installation_record'].lstrip('/');private_records.mkdir(record)
    inv={new['release']+'/orchestrator/modal_direct_storage.py':{'sha256':digest(module.read_bytes()),'mode':0o600}}
    private_records.write_bytes(record/'FILES.json',canonical(inv))
    private_records.write_bytes(record/'installed.json',canonical({'source':new['source'],
        'files_sha256':digest((record/'FILES.json').read_bytes()),'layout':{'release':new['release']}}))
    new['installation_sha256']=digest((record/'installed.json').read_bytes())
    yield root,old,new,binding,batch
    batch.db.close()


def snapshot(root):
    # SQLite read locks legitimately advance volatile SHM read marks. Compare
    # logical rows separately, DB/WAL and all records bytewise, all modes exactly.
    return {str(p.relative_to(root)):(None if p.name.endswith('-shm') else p.read_bytes(),p.stat().st_mode,p.stat().st_uid,p.stat().st_gid)
            for p in root.rglob('*') if p.is_file()}


def test_real_scratch_continuation_preserves_every_original_and_ledger(prepared):
    root,old,new,binding,batch=prepared;before=snapshot(root);rows=list(batch.db.iterdump())
    result=deploy.install(root,new)
    assert result['preparation_continuation']['run_id']==binding['run_id']
    assert result['preparation_continuation']['writes']==0
    assert result['state']==old['state'] and result['installed_disabled']
    after=snapshot(root)
    assert all(after[k]==v for k,v in before.items())
    assert list(batch.db.iterdump())==rows
    assert batch.db.execute('select count(*) from autonomy_runs').fetchone()[0]==1
    assert batch.db.execute('select count(*) from autonomy_assets').fetchone()[0]==0
    with pytest.raises(ValueError,match='^DIRECT_INSTALL_DESTINATION_EXISTS$'):deploy.install(root,new)
    assert snapshot(root)==after


@pytest.mark.parametrize('defect,code',[
    ('config-hash','DIRECT_CONTINUATION_CONFIG_CHANGED'),
    ('binding-hash','DIRECT_CONTINUATION_BINDING_CHANGED'),
    ('package','DIRECT_CONTINUATION_SCOPE_CHANGED:package_manifest_sha256'),
    ('provider','DIRECT_CONTINUATION_SCOPE_CHANGED:provider'),
    ('owner','DIRECT_CONTINUATION_OWNER_CHANGED'),
    ('reservation','DIRECT_CONTINUATION_ALREADY_RESERVED'),
    ('compute','DIRECT_CONTINUATION_ALREADY_RESERVED'),
    ('intent','DIRECT_CONTINUATION_NOT_PRE_RESERVATION'),
    ('missing-binding','DIRECT_CONTINUATION_NOT_PRE_RESERVATION'),
    ('unit','DIRECT_CONTINUATION_UNIT_CHANGED'),
    ('alias','DIRECT_CONTINUATION_ALIAS'),
    ('unsafe','PRIVATE_RECORD_PERMISSIONS'),
])
def test_changed_or_started_preparation_refuses_before_install_writes(prepared,defect,code):
    root,old,new,binding,batch=prepared;state=root/old['state'].lstrip('/')
    if defect=='config-hash':new['prepared_from']['config_sha256']='f'*64
    elif defect=='binding-hash':new['prepared_from']['binding_sha256']='f'*64
    elif defect=='package':new['package_manifest_sha256']='f'*64
    elif defect=='provider':new['provider']=dict(new['provider'],workspace='different')
    elif defect=='owner':batch.db.execute("UPDATE autonomy_runs SET status='COMPLETE'")
    elif defect=='reservation':batch.db.execute("INSERT INTO autonomy_assets VALUES('x',?,?,'RESERVED',1,NULL)",(binding['run_id'],'{}'))
    elif defect=='compute':batch.db.execute("INSERT INTO autonomy_compute VALUES('x',?,?,'RUNNING',1,'sb',NULL,'2026-10')",(binding['run_id'],'{}'))
    elif defect=='intent':private_records.mkdir(state/'provider')
    elif defect=='missing-binding':(state/'binding.json').unlink()
    elif defect=='unit':private_records.write_bytes(root/'etc/systemd/system'/next(iter(old['units'])),b'changed')
    elif defect=='alias':
        target=root/new['prepared_from']['config'].lstrip('/');original=target.with_name('original.json')
        target.rename(original);target.symlink_to(original)
    else:(state/'binding.json').chmod(0o644)
    before=snapshot(root);rows=list(batch.db.iterdump())
    # Scope check directly precedes provisioner package checks where the package
    # pin itself was changed. Both routes must refuse without a write.
    with pytest.raises(ValueError,match='^'+code+'$'):c.preflight(new,root=root)
    assert snapshot(root)==before
    assert list(batch.db.iterdump())==rows


def test_held_rejects_active_enabled_or_unknown_old_unit(monkeypatch):
    for text in ['LoadState=loaded\nActiveState=active\nUnitFileState=disabled\nMainPID=12',
                 'LoadState=loaded\nActiveState=inactive\nUnitFileState=enabled',
                 'LoadState=not-found\nActiveState=inactive\nUnitFileState=disabled']:
        monkeypatch.setattr(c.subprocess,'check_output',lambda *a,**k:text)
        with pytest.raises(ValueError,match='^DIRECT_CONTINUATION_PREDECESSOR_NOT_HELD$'):c.held(['synthetic.service'])
    monkeypatch.setattr(c.subprocess,'check_output',lambda *a,**k:'LoadState=loaded\nActiveState=failed\nUnitFileState=disabled\nMainPID=0')
    c.held(['synthetic.service'])


def test_controller_continues_original_owner_once_without_expiry_or_charge_reset(controlled,monkeypatch):
    f=controlled
    def failed_billing():raise RuntimeError('synthetic response failure before reservation')
    calls=[0]
    def first_then_fail():
        calls[0]+=1
        if calls[0]==1:return billing()
        return failed_billing()
    f.provider.billing_snapshot=first_then_fail
    with pytest.raises(RuntimeError,match='synthetic response failure'):
        storage.tick(f.config,f.provider,f.accounts,host_proof=f.proof,now=NOW)
    original=(f.state/'binding.json').read_bytes();binding=json.loads(original)
    owners=[tuple(x) for x in f.batch.db.execute('SELECT * FROM autonomy_runs')]
    old=copy.deepcopy(f.config);f.config['source']='d'*40
    f.config['prepared_from']={'config':'/etc/synthetic/predecessor.json',
        'config_sha256':f.proof['config_sha256'],'binding_sha256':digest(original)}
    f.proof.update(source=f.config['source'],config_sha256='e'*64)
    # Only root/installed provenance simulated; real check_binding, controller,
    # ledger, accounting, worker receipts, expiry and duplicate guards below.
    monkeypatch.setattr(c,'predecessor',lambda config:old)
    f.provider.billing_snapshot=billing
    assert storage.tick(f.config,f.provider,f.accounts,host_proof=f.proof,now=NOW)['status']=='RUNNING'
    assert [tuple(x) for x in f.batch.db.execute('SELECT * FROM autonomy_runs')]==owners
    assert (f.state/'binding.json').read_bytes()==original
    assert f.batch.db.execute('SELECT count(*) FROM autonomy_assets').fetchone()[0]==1
    assert f.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    outcome=finish(f)
    assert outcome['status']=='VERIFIED' and outcome['asset_expires_utc']==binding['asset_expires_utc']
    assert storage.tick(f.config,f.provider,f.accounts,host_proof=f.proof,now=NOW)==outcome
    assert sum(x[0]=='sandbox' for x in f.calls)==1
    assert (f.state/'binding.json').read_bytes()==original
