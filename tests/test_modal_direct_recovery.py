"""Real controller/ledger and scratch installed bindings; fake HTTP/paid SDK only.

Root ownership/systemd is simulated in scratch as in the installed-continuation
tests. No model, patient computation, actual provider call or charge occurs.
"""
from pathlib import Path
from types import SimpleNamespace as NS
import copy,json
import pytest
from orchestrator import modal_direct_recovery as recovery, modal_direct_storage as storage
from orchestrator import modal_direct_budget as budget, private_records as pr
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest,read
from orchestrator.modal_budget import ComputeAccounts
from test_modal_direct_storage import controlled,fixture,finish
from test_modal_ctp_download import planned
from test_modal_direct_budget import NOW,billing
from test_direct_storage_continuation import prepared,installed,snapshot
from tools import direct_storage_service as deploy


@pytest.fixture
def linked(controlled,monkeypatch):
    f=controlled
    storage.tick(f.config,f.provider,f.accounts,host_proof=f.proof,now=NOW)
    f.sandbox.poll=lambda:2
    storage.tick(f.config,f.provider,f.accounts,host_proof=f.proof,now=NOW)
    old_binding=read(f.state/'binding.json');parent=digest(canonical(old_binding));monkeypatch.setattr(recovery,'PARENT',parent)
    original_state=f.state;original_config=copy.deepcopy(f.config)
    handle=read(f.state/'provider/sandbox.json');failed=read(f.state/'FAILED.json')
    old_sb=f.sandbox
    old_sb.log_entries=[NS(object_id=handle['provider_id'],source='stderr',message=recovery.ERROR,
        timestamp=recovery.datetime(2026,10,6,11,tzinfo=recovery.timezone.utc))]
    old_sb.logs=NS(fetch=lambda **kw:iter(old_sb.log_entries))
    f.sandbox=NS(object_id='sb-second',poll=lambda:None)
    original_create=f.provider.modal.Sandbox.create
    def create(*a,**kw):original_create(*a,**kw);return f.sandbox
    f.provider.modal.Sandbox.create=create
    f.provider._sandbox=lambda ident:old_sb if ident==handle['provider_id'] else f.sandbox
    ref={'config':{'path':'/etc/synthetic/config.json','sha256':'d'*64},
         'terminal_proof':{'path':'/var/lib/synthetic/proof.json','sha256':'e'*64},'binding_sha256':parent}
    result={'old':original_config,'binding':old_binding,'handle':handle,'failure':failed,'reference':ref}
    # Root/source verification separately exercised below with real scratch files.
    # The controller test preserves actual parent/child SQLite and provider flow.
    def selected(config,**kw):
        assert config['recovery_from']==ref
        return result
    monkeypatch.setattr(recovery,'selection',selected)
    f.state=original_state.parent/'recovery';pr.mkdir(f.state)
    f.config={**f.config,'state':str(f.state),'source':'f'*40,'recovery_from':ref}
    f.proof={**f.proof,'source':f.config['source'],'config_sha256':'e'*64}
    f.old_state=original_state;f.parent_id=parent;f.old_sb=old_sb;f.parent_result=result
    f.original_rows=[tuple(x) for x in f.batch.db.execute('SELECT * FROM autonomy_assets')]
    f.original_files=snapshot(original_state)
    return f


def tick(f):return storage.tick(f.config,f.provider,f.accounts,host_proof=f.proof,now=NOW)


def test_actual_linked_launch_completion_keeps_original_charge_and_refuses_duplicate(linked):
    f=linked
    assert tick(f)['status']=='RUNNING'
    assert tick(f)['status']=='RUNNING'
    child=read(f.state/'binding.json');assert child['run_id']==f.parent_result['binding']['run_id']
    assert child['asset_expires_utc']==f.parent_result['binding']['asset_expires_utc']
    assert f.batch.db.execute('SELECT count(*) FROM autonomy_assets').fetchone()[0]==2
    assert f.batch.db.execute('SELECT sum(reserved_micro_usd) FROM autonomy_assets').fetchone()[0]==2*child['envelope']['cost']['reserved_micro_usd']
    assert recovery.resolved_failure_ids(f.accounts)==set()
    outcome=finish(f);assert outcome['status']=='VERIFIED' and outcome['recovery_of']==f.parent_id
    assert recovery.resolved_failure_ids(f.accounts)=={f.parent_id}
    assert tick(f)==outcome
    assert snapshot(f.old_state)==f.original_files
    assert [tuple(x) for x in f.batch.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(f.parent_id,))]==f.original_rows
    assert f.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    assert sum(x[0]=='sandbox' for x in f.calls)==2
    # A fresh state/config cannot manufacture a third attempt.
    with pytest.raises(ValueError,match='^BATCH_ACTIVE_RUN_REQUIRED$'):
        other=dict(child,source='1'*40)
        budget.reserve(f.accounts,digest(canonical(other)),other['run_id'],other,
            billing_snapshot=billing(),now=NOW,recovery=f.config)


@pytest.mark.parametrize('fault',['row-status','row-binding','charge','receipt','owner','provider-live','logs','volume'])
def test_predecessor_drift_never_reserves_or_creates(linked,fault):
    f=linked
    if fault=='row-status':f.batch.db.execute("UPDATE autonomy_assets SET status='RESERVED'")
    elif fault=='row-binding':f.batch.db.execute("UPDATE autonomy_assets SET binding='{}'")
    elif fault=='charge':f.batch.db.execute("UPDATE autonomy_assets SET reserved_micro_usd=1")
    elif fault=='receipt':f.batch.db.execute("UPDATE autonomy_assets SET receipt='{}'")
    elif fault=='owner':f.batch.db.execute("UPDATE autonomy_runs SET binding='{}'")
    elif fault=='provider-live':f.old_sb.poll=lambda:None
    elif fault=='logs':f.old_sb.log_entries[0].message='different failure'
    else:
        v=f.volumes[f.parent_result['handle']['data_volume_id']];pr.write_bytes(v.root/'unexpected',b'x')
    before=[tuple(x) for x in f.batch.db.execute('SELECT * FROM autonomy_assets')]
    with pytest.raises(ValueError):tick(f)
    assert before==[tuple(x) for x in f.batch.db.execute('SELECT * FROM autonomy_assets')]
    assert sum(x[0]=='sandbox' for x in f.calls)==1


def test_failed_replacement_blocks_without_another_reservation(linked):
    f=linked;tick(f);f.sandbox.poll=lambda:2
    assert tick(f)['status']=='FAILED'
    assert tick(f)=={'status':'BLOCKED_PRESERVED_FAILURE','no_automatic_retry':True}
    assert recovery.resolved_failure_ids(f.accounts)==set()
    assert f.batch.db.execute('SELECT count(*) FROM autonomy_assets').fetchone()[0]==2
    assert sum(x[0]=='sandbox' for x in f.calls)==2


def test_child_scope_and_other_uncertain_rows_still_refuse(linked):
    f=linked;tick(f);child=read(f.state/'binding.json')
    with pytest.raises(ValueError,match='^DIRECT_RECOVERY_CHILD_SCOPE:download_bytes$'):
        recovery.check_child(dict(child,download_bytes=1),f.parent_result)
    f.batch.db.execute("INSERT INTO autonomy_assets VALUES('other','else','{}','UNCERTAIN',1,NULL)")
    candidate=dict(child,source='3'*40)
    with pytest.raises(ValueError,match='^MODAL_UNCERTAIN_ASSET_PREPARATION$'):
        budget.reserve(f.accounts,digest(canonical(candidate)),candidate['run_id'],candidate,
            billing_snapshot=billing(),now=NOW,recovery=f.config)


def test_pending_child_cannot_be_reserved_again(linked):
    f=linked;tick(f);child=read(f.state/'binding.json');candidate=dict(child,source='3'*40)
    with pytest.raises(ValueError,match='^MODAL_UNCERTAIN_ASSET_PREPARATION$'):
        budget.reserve(f.accounts,digest(canonical(candidate)),candidate['run_id'],candidate,
            billing_snapshot=billing(),now=NOW,recovery=f.config)
    assert f.batch.db.execute('SELECT count(*) FROM autonomy_assets').fetchone()[0]==2


@pytest.fixture
def preserved(prepared,monkeypatch):
    root,old,new,binding,batch=prepared
    result=deploy.install(root,new);previous=read(root/result['config'].lstrip('/'))
    state=root/old['state'].lstrip('/');ident=digest(canonical(binding));monkeypatch.setattr(recovery,'PARENT',ident)
    failure={'status':'FAILED','exit_code':2,'provider_id':'sb-original','no_automatic_retry':True}
    handle={'provider_id':'sb-original','binding_sha256':ident,'data_volume_id':'vo-original'}
    pr.mkdir(state/'provider');pr.write_bytes(state/'provider/sandbox.json',canonical(handle));pr.write_bytes(state/'FAILED.json',canonical(failure))
    batch.db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,'UNCERTAIN',?,?)",(ident,binding['run_id'],canonical(binding).decode(),binding['envelope']['cost']['reserved_micro_usd'],canonical(failure).decode()))
    proof={'provider_id':'sb-original','exit_code':2,'stdout':'','stderr':recovery.ERROR,
        'data_volume_file_count':0,'data_volume_bytes':0,'provider_mutations':0}
    path='/var/lib/research-system-manual-sprint10-deployment/proof.json'
    pr.write_bytes(root/path.lstrip('/'),canonical(proof))
    config={**{k:v for k,v in previous.items() if k not in ('prepared_from','units')},'source':'d'*40,
        'state':'/var/lib/research-system-manual-sprint10/direct-inputs/'+'d'*40,
        'recovery_from':{'config':{'path':result['config'],'sha256':digest((root/result['config'].lstrip('/')).read_bytes())},
            'terminal_proof':{'path':path,'sha256':digest(canonical(proof))},'binding_sha256':ident}}
    return root,config,batch,state,proof


def test_real_scratch_parent_record_validation_is_read_only(preserved):
    root,cfg,batch,state,_=preserved;before=snapshot(root);rows=list(batch.db.iterdump())
    result=recovery.parent(ComputeAccounts(batch),cfg,root=root)
    assert result['binding']['run_id']=='synthetic-same-owner'
    assert snapshot(root)==before and list(batch.db.iterdump())==rows


@pytest.mark.parametrize('fault',['positive-exit','stderr','stdout','files','bytes','proof-hash','binding-hash','mode','old-file'])
def test_real_scratch_proofs_do_not_accept_other_failure(preserved,fault):
    root,cfg,batch,state,proof=preserved
    ref=cfg['recovery_from']['terminal_proof'];p=root/ref['path'].lstrip('/')
    if fault=='proof-hash':ref['sha256']='f'*64
    elif fault=='binding-hash':cfg['recovery_from']['binding_sha256']='f'*64
    elif fault=='mode':p.chmod(0o644)
    elif fault=='old-file':pr.write_bytes(state/'FAILED.json',b'{}')
    else:
        key={'positive-exit':'exit_code','stderr':'stderr','stdout':'stdout','files':'data_volume_file_count','bytes':'data_volume_bytes'}[fault]
        proof[key]=1 if key in ('exit_code','data_volume_file_count','data_volume_bytes') else 'different'
        pr.write_bytes(p,canonical(proof));ref['sha256']=digest(p.read_bytes())
    before=snapshot(root);rows=list(batch.db.iterdump())
    with pytest.raises(ValueError):recovery.parent(ComputeAccounts(batch),cfg,root=root)
    assert snapshot(root)==before and list(batch.db.iterdump())==rows


def recovery_installation(preserved):
    root,cfg,batch,state,proof=preserved
    cfg.update(release='/opt/research-system/manual-sprint10/synthetic-recovery',
        installation_record='/var/lib/research-system-manual-sprint10-deployment/synthetic-recovery')
    release=root/cfg['release'].lstrip('/');pr.mkdir(release/'orchestrator',parents=True)
    module=release/'orchestrator/modal_direct_storage.py';pr.write_bytes(module,b'# synthetic recovery approval provenance')
    record=root/cfg['installation_record'].lstrip('/');pr.mkdir(record)
    inventory={cfg['release']+'/orchestrator/modal_direct_storage.py':{'sha256':digest(module.read_bytes()),'mode':0o600}}
    pr.write_bytes(record/'FILES.json',canonical(inventory))
    pr.write_bytes(record/'installed.json',canonical({'source':cfg['source'],'files_sha256':digest((record/'FILES.json').read_bytes()),'layout':{'release':cfg['release']}}))
    cfg['installation_sha256']=digest((record/'installed.json').read_bytes())
    return root,cfg,batch,state,proof


def test_complete_recovery_provisioner_keeps_prior_files_and_rows(preserved):
    root,cfg,batch,state,_=recovery_installation(preserved)
    before=snapshot(root);rows=list(batch.db.iterdump())
    result=deploy.install(root,cfg)
    assert result['installed_disabled'] and result['systemctl_operations']==0
    assert result['state']!=str(state.relative_to(root))
    newstate=root/result['state'].lstrip('/');assert newstate.is_dir() and not list(newstate.iterdir())
    assert all(snapshot(root)[k]==v for k,v in before.items())
    assert list(batch.db.iterdump())==rows
    installed_cfg=read(root/result['config'].lstrip('/'))
    assert recovery.parent(ComputeAccounts(batch),installed_cfg,root=root)['binding']['run_id']=='synthetic-same-owner'
    after=snapshot(root)
    with pytest.raises(ValueError,match='^DIRECT_INSTALL_DESTINATION_EXISTS$'):deploy.install(root,cfg)
    assert snapshot(root)==after
    pr.check_tree(root)


@pytest.mark.parametrize('fault,code',[
    ('both','DIRECT_INSTALL_ONE_CONTINUATION'),
    ('same-state','DIRECT_INSTALL_STATE_BINDING'),
    ('same-source','DIRECT_RECOVERY_FRESH_STATE_REQUIRED'),
    ('unit-set','DIRECT_RECOVERY_UNIT_SET'),
    ('config-path','DIRECT_RECOVERY_PREDECESSOR_PATH'),
])
def test_recovery_source_unit_and_path_drift_before_writes(preserved,fault,code):
    root,cfg,batch,state,_=recovery_installation(preserved)
    ref=cfg['recovery_from']['config'];path=root/ref['path'].lstrip('/')
    if fault=='both':cfg['prepared_from']={}
    elif fault=='same-state':cfg['state']='/'+str(state.relative_to(root))
    elif fault=='same-source':
        old=read(path);cfg['source']=old['source'];cfg['state']='/var/lib/research-system-manual-sprint10/direct-inputs/'+cfg['source']
    elif fault=='unit-set':
        old=read(path);old['units']={};pr.write_bytes(path,canonical(old));ref['sha256']=digest(path.read_bytes())
    else:
        other=path.with_name('copy.json');pr.copyfile(path,other);ref['path']='/'+str(other.relative_to(root))
    before=snapshot(root);rows=list(batch.db.iterdump())
    with pytest.raises(ValueError,match='^'+code+'$'):
        if fault in ('both','same-state'):deploy.install(root,cfg)
        else:recovery.preflight(cfg,root=root)
    assert snapshot(root)==before and list(batch.db.iterdump())==rows


@pytest.mark.parametrize('kind',['assets','compute'])
def test_downstream_admission_requires_verified_recovery_and_keeps_both_costs(linked,kind):
    from orchestrator.modal_budget import estimate,WORKSPACE_CAP
    f=linked;tick(f)
    resources={'gpu':'T4','cpu':1,'memory_mib':1024,'timeout_seconds':60}
    binding={'resources':resources,'overhead_micro_usd':0,'cost':estimate(resources,0)}
    # Separate downstream owner is synthetic; no scientific allowance/call is created.
    f.batch.db.execute("INSERT INTO autonomy_runs(id,binding,status) VALUES(?,?,'ACTIVE')",('downstream','{}'))
    def reserve(spent=0):
        if kind=='assets':return f.accounts.reserve_assets('downstream-assets','downstream',{'synthetic':True},workspace_spent_micro=spent)
        return f.accounts.reserve('downstream-compute','downstream',binding,workspace_spent_micro=spent)
    with pytest.raises(ValueError,match='^MODAL_UNCERTAIN_ASSET_PREPARATION$'):reserve()
    finish(f)
    cost=sum(x[0] for x in f.batch.db.execute('SELECT reserved_micro_usd FROM autonomy_assets'))
    with pytest.raises(ValueError,match='^MODAL_(ASSET_COST_CAP|WORKSPACE_COST_CAP)$'):reserve(WORKSPACE_CAP-cost)
    before=f.batch.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(f.parent_id,)).fetchone()
    assert reserve()
    assert not reserve()
    assert tuple(f.batch.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(f.parent_id,)).fetchone())==tuple(before)
    assert f.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0


def test_missing_or_altered_completion_cannot_close_original(linked):
    f=linked;tick(f);finish(f)
    child=digest(canonical(read(f.state/'binding.json')))
    saved=f.batch.db.execute('SELECT receipt FROM autonomy_assets WHERE id=?',(child,)).fetchone()[0]
    for change in ({'status':'FAILED'},{'recovery_of':'e'*64},{'binding_sha256':'f'*64}):
        f.batch.db.execute('UPDATE autonomy_assets SET receipt=? WHERE id=?',(json.dumps(dict(json.loads(saved),**change)),child))
        with pytest.raises(ValueError,match='^DIRECT_RECOVERY_COMPLETION_BINDING$'):recovery.resolved_failure_ids(f.accounts)
    f.batch.db.execute('UPDATE autonomy_assets SET receipt=? WHERE id=?',(saved,child))
    assert recovery.resolved_failure_ids(f.accounts)=={f.parent_id}
