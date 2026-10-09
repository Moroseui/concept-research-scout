"""Real lifecycle/SQLite/native transport; paid Modal endpoint is synthetic only."""
import copy
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace as NS
import pytest
from orchestrator import modal_environment_closure_route as route
from orchestrator import modal_environment_budget as budget, modal_environment_inventory as inventory
from orchestrator import modal_environment_provider as provider, private_records as pr
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest,read
from orchestrator.modal_assets import BASE_IMAGE
from test_modal_environment_provider import fixture as provider_fixture,Stream
from test_modal_environment_closure import fixture as wheel_fixture
from test_modal_direct_budget import billing,NOW


@pytest.fixture(autouse=True)
def private_mode():
    previous=os.umask(0o077)
    try:yield
    finally:os.umask(previous)


@pytest.fixture
def closure_case(provider_fixture,tmp_path):
    f=provider_fixture
    for table in ('events','autonomy_assets','autonomy_runs'):f.accounts.db.execute('DELETE FROM '+table)
    selected=wheel_fixture(tmp_path/'synthetic-wheels')
    f.closure={'selection':selected,'wheel_root':str(tmp_path/'synthetic-wheels/wheels')}
    f.binding={'purpose':route.PURPOSE,'operation_id':route.OPERATION,'run_id':route.RUN,
        'authority_sha256':budget.AUTHORITY,'team_authority_sha256':budget.TEAM_AUTHORITY,
        'source':'a'*40,'installed_config_sha256':'b'*64,'image_id':'im-Pinned','base_image':BASE_IMAGE,
        'worker_sha256':route.worker_sha256(),'envelope':route.envelope(billing()['rates'],f.closure['selection']['wheels']),
        'closure':f.closure}
    f.state=tmp_path/'controller';pr.mkdir(f.state)
    f.config={'schema':route.SCHEMA,'source':'a'*40,'release':'/opt/synthetic-reviewed-release',
        'installation_record':'/var/lib/synthetic-install','installation_sha256':'c'*64,
        'state':str(f.state),'batch_ledger':str(f.accounts.batch.folder),'provider':{},
        'operation_id':route.OPERATION,'image_id':'im-Pinned','base_image':BASE_IMAGE,
        'worker_sha256':route.worker_sha256(),'closure':f.closure,'units':{}}
    f.proof={'status':'PASS','source':'a'*40,'installation_sha256':'c'*64,'config_sha256':'b'*64}
    f.provider.billing_snapshot=billing
    from contextlib import contextmanager
    from types import MethodType
    from orchestrator.modal_provider import ModalProvider
    f.volumes={};f.volume_files={}
    class Volume:
        object_id='vo-SyntheticWheels'
        def hydrate(self,**kw):return self
        def listdir(self,path,recursive=False):
            assert path=='/' and recursive
            return [NS(path='/'+n,size=len(v),type=NS(name='FILE')) for n,v in f.volume_files.items()]
        def read_file(self,name):yield f.volume_files[name.lstrip('/')]
        @contextmanager
        def batch_upload(self,force=False):
            assert force is False;f.calls.append(('upload-begin',))
            def put_file(path,name,mode):
                assert mode==0o440 and name.lstrip('/') not in f.volume_files
                f.volume_files[name.lstrip('/')]=Path(path).read_bytes();f.calls.append(('upload',name))
            yield NS(put_file=put_file)
        def with_mount_options(self,**kw):
            f.calls.append(('mount',self.object_id,kw));return ('read-only-wheel-volume',self.object_id)
        def remove_file(self,name,recursive):
            assert recursive is False;del f.volume_files[name.lstrip('/')];f.calls.append(('remove',name))
    f.volume=Volume()
    def from_name(name,create_if_missing):
        f.calls.append(('volume-name',name,create_if_missing))
        if name not in f.volumes:
            if not create_if_missing:raise f.provider.modal.exception.NotFoundError()
            f.volumes[name]=f.volume
        return f.volumes[name]
    f.provider.modal.Volume=NS(from_name=from_name)
    f.provider._volume=lambda ident:f.volume if ident==f.volume.object_id else (_ for _ in ()).throw(AssertionError('unrelated volume'))
    f.provider._verify_volume=MethodType(ModalProvider._verify_volume,f.provider)
    f.provider._verify_volume_members=MethodType(ModalProvider._verify_volume_members,f.provider)
    return f


def tick(f):return inventory.tick(f.config,f.provider,f.accounts,host_proof=f.proof,now=NOW)


def native_transport(f):
    """Execute actual provider argv in a no-network native sandbox, fixture wheels."""
    args=route.arguments(f.binding);root=Path(f.closure['wheel_root']).parent
    cmd=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--ro-bind','/usr','/usr']
    for name in ('/lib','/lib64','/bin'):
        q=Path(name)
        if q.is_symlink():cmd+=['--symlink',os.readlink(q),name]
        elif q.exists():cmd+=['--ro-bind',name,name]
    executable=args[0]
    if executable.startswith('/opt/'):
        base=str(Path(executable).parent.parent);cmd+=['--ro-bind',base,base]
    cmd+=['--proc','/proc','--dev','/dev','--tmpfs','/tmp','--bind',str(root),'/work',
          '--ro-bind',str(root/'wheels'),'/wheels','--chdir','/work','--setenv','HOME','/tmp',
          '--setenv','PATH','/usr/bin:/bin','--unsetenv','PYTHONHOME','--unsetenv','PYTHONPATH',*args]
    result=subprocess.run(cmd,capture_output=True,timeout=300)
    assert result.returncode==0,(result.stdout,result.stderr)
    assert not result.stderr
    route.validate_result(result.stdout,f.binding)
    return result.stdout


def test_actual_transport_controller_ledger_and_consumer_roundtrip(closure_case):
    f=closure_case;raw=native_transport(f);f.sb.stdout=Stream([raw]);f.sb.stderr=Stream([])
    result=tick(f)
    assert result['status']=='VERIFIED' and result['dependency_closure']['gpu_verified'] is False
    assert result['dependency_closure']['patient_computation'] is False
    assert result['dependency_closure']['scientific_environment']['expected']['cuda']=='12.8'
    args,kw=next(row[1:] for row in f.calls if row[0]=='create')
    assert args==route.arguments(f.binding)
    assert kw['gpu'] is None and kw['cpu']==(2,2) and kw['memory']==(8192,8192) and kw['timeout']==1800
    assert kw['volumes']=={'/wheels':('read-only-wheel-volume','vo-SyntheticWheels')}
    assert ('mount','vo-SyntheticWheels',{'read_only':True}) in f.calls
    assert kw['block_network'] is True and kw['include_oidc_identity_token'] is False
    assert kw['secrets']==[] and kw['env']=={} and kw['outbound_cidr_allowlist']==[] and kw['outbound_domain_allowlist']==[]
    old=[tuple(row) for row in f.accounts.db.execute('SELECT * FROM autonomy_assets')];calls=list(f.calls)
    assert tick(f)==result and f.calls==calls and f.sb.stdout.reads==1
    assert [tuple(row) for row in f.accounts.db.execute('SELECT * FROM autonomy_assets')]==old
    assert f.accounts.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    assert f.accounts.db.execute('SELECT status FROM autonomy_runs WHERE id=?',(route.RUN,)).fetchone()[0]=='COMPLETE'
    row=f.accounts.db.execute('SELECT * FROM autonomy_assets WHERE run=?',(route.RUN,)).fetchone()
    assert budget.selected_asset(row) and row['reserved_micro_usd']==f.binding['envelope']['cost']['reserved_micro_usd']
    from orchestrator import modal_scientific_environment as normal
    normal.environment_validate(result['dependency_closure']['scientific_environment'])
    pr.check_tree(f.state)


@pytest.mark.parametrize('defect',['hash','member','missing','alias'])
def test_exact_local_wheel_inputs_required_before_reservation(closure_case,defect):
    f=closure_case;root=Path(f.closure['wheel_root']);name=next(iter(f.closure['selection']['wheels']))
    if defect=='hash':pr.write_bytes(root/name,b'changed synthetic wheel')
    elif defect=='member':pr.write_bytes(root/'unexpected.whl',b'extra')
    elif defect=='missing':(root/name).unlink()
    else:
        original=root/name;copy=root.parent/'outside.whl';original.rename(copy);original.symlink_to(copy)
    with pytest.raises(ValueError):tick(f)
    assert not any(x[0] in ('create','volume-name','lookup') for x in f.calls)
    assert f.accounts.db.execute('SELECT count(*) FROM autonomy_assets').fetchone()[0]==0
    assert not (f.state/'binding.json').exists()


def test_lost_create_preserves_intent_and_full_reservation_no_second_create(closure_case):
    f=closure_case
    def lost(*args,**kwargs):f.calls.append(('create-lost',));raise TimeoutError('fixture lost response')
    f.provider.modal.Sandbox.create=lost
    with pytest.raises(TimeoutError):tick(f)
    row=f.accounts.db.execute('SELECT * FROM autonomy_assets WHERE run=?',(route.RUN,)).fetchone()
    assert row['status']=='RESERVED' and row['reserved_micro_usd']>0
    assert tick(f)['status']=='BLOCKED_CREATE_UNCERTAIN'
    assert tick(f)['status']=='BLOCKED_CREATE_UNCERTAIN'
    assert sum(x[0]=='create-lost' for x in f.calls)==1
    assert (f.state/'provider/sandbox-intent.json').exists()


def test_terminal_failure_cannot_be_relaunched_or_admit_science(closure_case):
    f=closure_case;f.sb.poll=lambda:2;f.sb.stdout=Stream([]);f.sb.stderr=Stream([b'synthetic dependency failure'])
    assert tick(f)['status']=='UNCERTAIN'
    assert tick(f)['status']=='BLOCKED_PRESERVED_FAILURE'
    with pytest.raises(ValueError,match='^ADMINISTRATIVE_INPUT_OWNER_CANNOT_ADMIT_SCIENCE$'):
        f.accounts.batch.reserve_scientific('forbidden',route.RUN,'run_spec_author','a'*40,{})
    assert sum(x[0]=='create' for x in f.calls)==1


def test_selected_operation_cannot_change_source_for_another_reservation(closure_case):
    f=closure_case;f.sb.poll=lambda:None;assert tick(f)['status']=='RUNNING'
    original=[tuple(row) for row in f.accounts.db.execute('SELECT * FROM autonomy_assets')]
    f.config['source']='d'*40;f.proof['source']='d'*40
    with pytest.raises(ValueError,match='^ENVIRONMENT_INVENTORY_EXISTING_BINDING_CHANGED$'):tick(f)
    assert [tuple(row) for row in f.accounts.db.execute('SELECT * FROM autonomy_assets')]==original


@pytest.mark.parametrize('defect,code',[('halt','AUTONOMY_BATCH_HALTED'),('smoke','ITEM4_HARD_COST_CAP'),
 ('headroom','ITEM4_PROVIDER_HEADROOM_WAIT'),('stale','MODAL_BILLING_SNAPSHOT_STALE')])
def test_existing_caps_halt_and_fresh_billing_still_apply(closure_case,defect,code):
    from test_modal_environment_budget import asset,seal
    from datetime import timedelta
    f=closure_case;view=billing()
    if defect=='halt':pr.write_bytes(f.accounts.batch.folder/'HALT',b'fixture hold')
    elif defect=='smoke':asset(f.accounts.batch,budget.SMOKE_CAP-f.binding['envelope']['cost']['reserved_micro_usd']+1)
    elif defect=='headroom':view['summary']['metered_cost']='1000';seal(view)
    else:view['observed_at']=(NOW-timedelta(minutes=6)).isoformat();seal(view)
    f.provider.billing_snapshot=lambda:view
    with pytest.raises(ValueError,match='^'+code+'$'):tick(f)
    assert not any(x[0]=='create' for x in f.calls)
    assert f.accounts.db.execute('SELECT count(*) FROM autonomy_assets WHERE run=?',(route.RUN,)).fetchone()[0]==0


def test_transport_limits_refuse_before_provider_or_accounting(closure_case,monkeypatch):
    f=closure_case;monkeypatch.setattr(route,'MAX_ARGUMENT',1)
    with pytest.raises(ValueError,match='^CLOSURE_TRANSPORT_BOUND$'):tick(f)
    assert not any(x[0]=='create' for x in f.calls)
    assert f.accounts.db.execute('SELECT count(*) FROM autonomy_assets WHERE run=?',(route.RUN,)).fetchone()[0]==0


from test_environment_inventory_service import installed,snapshot


def test_same_installer_pins_and_disables_closure_service(installed,tmp_path):
    from tools import environment_inventory_service as deploy
    from orchestrator import modal_environment_closure as worker,modal_scientific_environment as consumer
    f=installed;selected=wheel_fixture(tmp_path/'wheels')
    f.config.update(schema=route.SCHEMA,operation_id=route.OPERATION,worker_sha256=route.worker_sha256(),
        state=deploy.STATE_ROOT+'/'+route.OPERATION,
        closure={'selection':selected,'wheel_root':str(tmp_path/'wheels/wheels')})
    from orchestrator import modal_cleanup
    for module in (route,worker,consumer,modal_cleanup):f.put(f.release+'/orchestrator/'+Path(module.__file__).name,Path(module.__file__).read_bytes())
    f.seal();before=snapshot(f.root);result=deploy.install(f.root,f.config)
    assert result['operation_id']==route.OPERATION and result['installed_disabled'] is True
    service=(f.root/'etc/systemd/system'/result['units'][0]).read_text()
    assert 'TimeoutStartSec=2100' in service and 'research-manual-sprint10-closure-' in result['units'][0]
    assert 'ReadWritePaths='+f.config['state']+' '+f.config['batch_ledger'] in service
    config=read(f.root/result['config'].lstrip('/'));assert inventory.selection(config)==config
    after=snapshot(f.root);assert all(after[k]==v for k,v in before.items())
    with pytest.raises(ValueError,match='^ENVIRONMENT_INSTALL_DESTINATION_EXISTS$'):deploy.install(f.root,f.config)


@pytest.mark.parametrize('consumer',['fit','direct'])
def test_genuine_closure_charge_counts_in_downstream_smoke_cap(closure_case,consumer):
    from test_modal_environment_budget import compute
    from orchestrator import modal_item4_policy as policy,modal_direct_budget as direct
    from test_modal_item4_budget import bound
    f=closure_case;f.sb.stdout=Stream([native_transport(f)]);f.sb.stderr=Stream([])
    assert tick(f)['status']=='VERIFIED'
    db=f.accounts.db;before_assets=[tuple(x) for x in db.execute('SELECT * FROM autonomy_assets')]
    view=billing();batch=f.accounts.batch
    if consumer=='fit':
        batch.register_run('item4',{'backlog_item':4,'experiment_authority_sha256':policy.AUTHORITY})
        selected=bound('nextfit');selected['cost']=policy.quote(selected['resources'],view['rates'],0)
        compute(batch,policy.SMOKE_CAP-selected['cost']['reserved_micro_usd'],ident='oldfit',run='item4')
        call=lambda:f.accounts.reserve_item4(digest(canonical(selected)),'item4',selected,billing_snapshot=view,now=NOW)
    else:
        run='next-inputs';batch.register_run(run,{'purpose':direct.PURPOSE,'authority_sha256':policy.AUTHORITY})
        selected={'purpose':direct.PURPOSE,'authority_sha256':policy.AUTHORITY,
            'download_authority_sha256':direct.DOWNLOAD_AUTHORITY,'team_authority_sha256':policy.TEAM_AUTHORITY,
            'run_id':run,'download_bytes':54323796401,'envelope':direct.envelope(54323796401,view['rates']),
            'package_manifest_sha256':'d'*64}
        compute(batch,policy.SMOKE_CAP-selected['envelope']['cost']['reserved_micro_usd'],ident='oldfit')
        call=lambda:direct.reserve(f.accounts,digest(canonical(selected)),run,selected,billing_snapshot=view,now=NOW)
    with pytest.raises(ValueError,match='^ITEM4_HARD_COST_CAP$'):call()
    assert [tuple(x) for x in db.execute('SELECT * FROM autonomy_assets')]==before_assets
    assert db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0


@pytest.mark.parametrize('phase',['volume','upload'])
def test_partial_volume_or_upload_never_repeats(closure_case,phase):
    f=closure_case
    if phase=='volume':
        original=f.provider.modal.Volume.from_name
        def lost(name,create_if_missing):
            value=original(name,create_if_missing)
            if create_if_missing:raise TimeoutError('fixture lost volume response')
            return value
        f.provider.modal.Volume.from_name=lost
    else:
        from contextlib import contextmanager
        @contextmanager
        def partial(force=False):
            def put(path,name,mode):
                f.volume_files[name.lstrip('/')]=Path(path).read_bytes()
                raise TimeoutError('fixture upload interrupted')
            yield NS(put_file=put)
        f.volume.batch_upload=partial
    with pytest.raises(TimeoutError):tick(f)
    calls=list(f.calls);saved=dict(f.volume_files)
    assert tick(f)['status']=='BLOCKED_CREATE_UNCERTAIN' and f.calls==calls and f.volume_files==saved
    assert f.accounts.db.execute('SELECT count(*) FROM autonomy_assets').fetchone()[0]==1


def test_storage_and_receipt_egress_count_in_same_reservation(closure_case):
    f=closure_case;env=f.binding['envelope'];size=sum(x['bytes'] for x in f.closure['selection']['wheels'].values())
    assert env['wheel_bytes']==size and env['retention_days']==30 and env['reserved_storage_days']==35
    assert env['cost']['overhead_micro_usd']>route.OVERHEAD_MICRO
    f.sb.poll=lambda:None;assert tick(f)['status']=='RUNNING'
    assert f.accounts.db.execute('SELECT count(*) FROM autonomy_runs').fetchone()[0]==1
    assert f.accounts.db.execute('SELECT count(*) FROM autonomy_assets').fetchone()[0]==1
    assert f.accounts.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0


def ready(f):
    f.sb.stdout=Stream([native_transport(f)]);f.sb.stderr=Stream([])
    result=tick(f);assert result['status']=='VERIFIED'
    from datetime import datetime,timedelta
    receipt=read(f.state/'provider/wheels-ready.json')
    return result,datetime.fromisoformat(receipt['expires_at'])+timedelta(seconds=1)


def test_terminal_timer_polls_are_local_then_exact_expiry_keeps_originals(closure_case):
    f=closure_case;result,expiry=ready(f)
    before=dict(f.volume_files);calls=list(f.calls)
    assert inventory.tick(f.config,None,f.accounts,host_proof=f.proof,now=NOW)==result
    assert f.calls==calls
    due=inventory.tick(f.config,None,f.accounts,host_proof=f.proof,now=expiry)
    assert due['retention']['status']=='RETENTION_DUE' and f.calls==calls
    finished=inventory.tick(f.config,f.provider,f.accounts,host_proof=f.proof,now=expiry)
    assert finished['retention']['status']=='WHEEL_COPIES_EXPIRED' and f.volume_files=={}
    root=Path(f.closure['wheel_root'])
    assert {p.name:p.read_bytes() for p in root.iterdir()}==before
    row=f.accounts.db.execute('SELECT * FROM autonomy_assets').fetchone()
    assert row['status']=='READY' and row['reserved_micro_usd']==f.binding['envelope']['cost']['reserved_micro_usd']
    calls=list(f.calls)
    # Completed cleanup is local-only too, without repeating the native poll.
    assert inventory.tick(f.config,None,f.accounts,host_proof=f.proof,now=expiry)['retention']==finished['retention']
    assert f.calls==calls
    assert (f.state/'provider/stdout.bin').exists() and (f.state/'VERIFIED.json').exists()


@pytest.mark.parametrize('kind',['compute','owner'])
def test_retention_refusal_preserves_and_stops_automatic_cleanup(closure_case,kind):
    f=closure_case;result,expiry=ready(f)
    if kind=='compute':
        from test_modal_environment_budget import compute
        compute(f.accounts.batch,100,ident='active',status='RUNNING')
    else:f.accounts.batch.register_run('future-science',{'synthetic_fixture':True})
    before=dict(f.volume_files);calls=list(f.calls)
    stopped=inventory.tick(f.config,None,f.accounts,host_proof=f.proof,now=expiry)
    hold=stopped['retention']
    assert hold['storage_may_continue_accruing'] is True and hold['automatic_cleanup_retry'] is False
    assert f.volume_files==before and f.calls==calls
    assert inventory.tick(f.config,None,f.accounts,host_proof=f.proof,now=expiry)['retention']==hold
    assert f.calls==calls and (f.state/'retention/REFUSAL.json').exists()


def test_tampered_verified_wheel_receipt_blocks_replay_and_downstream_reuse(closure_case):
    f=closure_case;ready(f)
    path=f.state/'provider/wheels-ready.json';raw=read(path);raw['volume_id']='vo-Other';pr.write_bytes(path,canonical(raw))
    with pytest.raises(ValueError,match='^CLOSURE_WHEEL_RECEIPT_BINDING$'):
        inventory.tick(f.config,None,f.accounts,host_proof=f.proof,now=NOW)



def test_actual_consumer_receipt_cites_native_volume_and_exact_environment(closure_case):
    from orchestrator.modal_item4_provider import environment_scope
    f=closure_case;result,expiry=ready(f);calls=list(f.calls)
    proof=route.consumer_proof(f.accounts,f.binding,f.state,now=NOW)
    raw=(f.state/'provider/wheels-ready.json').read_bytes()
    assert proof['wheel_receipt_sha256']==digest(raw)
    assert proof['wheel_volume_id']==read(f.state/'provider/sandbox.json')['wheel_volume_id']
    assert f.calls==calls and proof['scientific_acceptance'] is False
    spec=proof['scientific_environment']
    actual=environment_scope(NS(config={'scientific_environment':spec,'wheel_files':proof['wheel_files']}),
        {'scientific_environment':spec,'progress':{'fit_binding':{'environment_sha256':proof['environment_sha256']}}})
    assert actual==spec
    with pytest.raises(ValueError,match='^CLOSURE_WHEELS_EXPIRED_OR_HELD$'):
        route.consumer_proof(f.accounts,f.binding,f.state,now=expiry)


def test_failed_member_cleanup_is_preserved_without_automatic_retry(closure_case):
    f=closure_case;result,expiry=ready(f);original=f.volume.remove_file;once=[True]
    def interrupted(name,recursive):
        original(name,recursive)
        if once[0]:once[0]=False;raise OSError('fixture deletion response lost')
    f.volume.remove_file=interrupted
    failed=inventory.tick(f.config,f.provider,f.accounts,host_proof=f.proof,now=expiry)
    assert failed['retention']['status']=='EXPIRY_REFUSED_MEMBER_CLEANUP'
    assert failed['retention']['storage_may_continue_accruing'] is True
    partial=dict(f.volume_files);calls=list(f.calls)
    assert inventory.tick(f.config,None,f.accounts,host_proof=f.proof,now=expiry)['retention']==failed['retention']
    assert f.calls==calls and f.volume_files==partial
    assert len(list(Path(f.closure['wheel_root']).iterdir()))==len(f.closure['selection']['wheels'])


@pytest.mark.parametrize('key',['volume_storage_gib_month_cost','egress_gib_cost'])
def test_negative_storage_or_egress_rate_refuses(closure_case,key):
    f=closure_case;rates=dict(billing()['rates']);rates[key]='-1'
    with pytest.raises(ValueError,match='^MODAL_BILLING_NUMBER$'):
        route.envelope(rates,f.closure['selection']['wheels'])
