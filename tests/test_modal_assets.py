"""Private asset transfer/accounting contracts with no provider authentication."""
import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import modal_assets,private_records,connectivity
from orchestrator.modal_executor import canonical
from orchestrator.modal_budget import ComputeAccounts,MICRO,WORKSPACE_CAP
from orchestrator.manual_executor import digest,inventory,read
from test_modal_executor import setup
from test_modal_provider import Volume,ModalProvider


class UploadVolume(Volume):
    def __init__(self):super().__init__({});self.uploads=0;self.fail=False
    def batch_upload(self,force=False):
        assert not force;self.uploads+=1;return self
    def __enter__(self):return self
    def __exit__(self,*args):
        if self.fail:raise TimeoutError('Synthetic lost upload acknowledgement')
    def put_file(self,path,remote,mode):
        assert mode==0o440;self.files[remote.lstrip('/')]=Path(path).read_bytes()


def adapter(volume):
    provider=object.__new__(ModalProvider);provider._volume=lambda ident:volume
    return provider


def test_upload_verifies_both_ends_and_forbids_overwrite(tmp_path):
    source=tmp_path/'source';private_records.mkdir(source);private_records.write_bytes(source/'one',b'abc')
    expected={'one':{'bytes':3,'sha256':digest(b'abc')}};volume=UploadVolume();p=adapter(volume)
    modal_assets.upload(p,'vo-test',source,expected)
    assert volume.files=={'one':b'abc'} and volume.uploads==1
    with pytest.raises(ValueError,match='NOT_EMPTY'):modal_assets.upload(p,'vo-test',source,expected)
    assert volume.uploads==1


def test_local_asset_damage_prevents_any_upload(tmp_path):
    source=tmp_path/'source';private_records.mkdir(source);private_records.write_bytes(source/'one',b'bad')
    volume=UploadVolume()
    with pytest.raises(ValueError,match='MEMBERS_OR_HASH'):
        modal_assets.upload(adapter(volume),'vo-test',source,{'one':{'bytes':3,'sha256':digest(b'abc')}})
    assert volume.uploads==0


def test_unsafe_local_asset_is_refused_without_changing_it(tmp_path):
    source=tmp_path/'source';private_records.mkdir(source);file=source/'one';private_records.write_bytes(file,b'abc');file.chmod(0o644)
    volume=UploadVolume();before=digest(file.read_bytes())
    with pytest.raises(ValueError):modal_assets.upload(adapter(volume),'vo-test',source,{'one':{'bytes':3,'sha256':before}})
    assert file.stat().st_mode&0o777==0o644 and digest(file.read_bytes())==before and volume.uploads==0


def test_package_upload_reconciliation_is_read_only(setup,monkeypatch,tmp_path):
    e,p,b,run,binding,package,dest=setup;binding['package_volume_id']='vo-test'
    manifest=read(package/'manifest.json');manifest['binding']=binding;private_records.write_bytes(package/'manifest.json',canonical(manifest))
    monkeypatch.setattr(connectivity,'require',lambda *a:{'synthetic':True})
    volume=UploadVolume();provider=adapter(volume);record=tmp_path/'transfer'
    result=modal_assets.prepare_package(provider,binding,package,record)
    assert result['status']=='READY' and volume.uploads==1
    assert modal_assets.prepare_package(provider,binding,package,record)==result and volume.uploads==1
    private_records.check_tree(record)


def test_uncertain_package_upload_is_never_repeated(setup,monkeypatch,tmp_path):
    e,p,b,run,binding,package,dest=setup;binding['package_volume_id']='vo-test'
    manifest=read(package/'manifest.json');manifest['binding']=binding;private_records.write_bytes(package/'manifest.json',canonical(manifest))
    monkeypatch.setattr(connectivity,'require',lambda *a:{'synthetic':True})
    volume=UploadVolume();volume.fail=True;provider=adapter(volume);record=tmp_path/'transfer'
    with pytest.raises(TimeoutError):modal_assets.prepare_package(provider,binding,package,record)
    assert (record/'intent.json').exists() and not (record/'READY.json').exists()
    volume.fail=False
    with pytest.raises(ValueError,match='UNCERTAIN_RECONCILE'):modal_assets.prepare_package(provider,binding,package,record)
    assert volume.uploads==1


def test_assets_reserve_once_and_uncertainty_stops_compute(setup):
    e,p,b,run,binding,package,dest=setup;cost=ComputeAccounts(b);asset={'scope':'synthetic'}
    assert cost.reserve_assets('prep',run,asset,workspace_spent_micro=0)
    assert not cost.reserve_assets('prep',run,asset,workspace_spent_micro=0)
    with pytest.raises(ValueError,match='UNCERTAIN_ASSET'):
        cost.reserve('compute',run,binding,workspace_spent_micro=0,smoke=True)
    cost.finish_assets('prep','UNCERTAIN',{'original':'preserved'})
    with pytest.raises(ValueError,match='OUTCOME_CHANGED'):cost.finish_assets('prep','READY',{'invented':'receipt'})
    assert b.db.execute('SELECT reserved_micro_usd FROM autonomy_assets').fetchone()[0]==MICRO


def test_preparation_and_compute_share_conservative_dollar_caps(setup):
    e,p,b,run,binding,package,dest=setup;cost=ComputeAccounts(b)
    with pytest.raises(ValueError,match='COST_CAP'):cost.reserve_assets('prep',run,{},workspace_spent_micro=WORKSPACE_CAP)
    assert cost.reserve_assets('prep',run,{},workspace_spent_micro=0)
    receipt={'status':'READY','synthetic':True};cost.finish_assets('prep','READY',receipt)
    cost.finish_assets('prep','READY',receipt)
    assert cost.reserve('compute',run,binding,workspace_spent_micro=0,smoke=True)
    total=b.db.execute('SELECT reserved_micro_usd FROM autonomy_assets').fetchone()[0]+b.db.execute('SELECT reserved_micro_usd FROM autonomy_compute').fetchone()[0]
    assert total==MICRO+binding['cost']['reserved_micro_usd']
    assert b.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0


@pytest.fixture
def preparation(tmp_path,monkeypatch):
    """Full preparation control flow, synthetic local assets and provider only."""
    from orchestrator.autonomy_accounting import BatchAccounts
    source='a'*40;root=tmp_path/'root';private_records.mkdir(root)
    science=root/'experiments/sprint9_modal';private_records.mkdir(science,parents=True)
    data=tmp_path/'data';wheels=tmp_path/'wheels'
    for p in [data,wheels]:private_records.mkdir(p)
    private_records.write_bytes(data/'synthetic.npz',b'cache')
    private_records.write_bytes(wheels/'synthetic.whl',b'wheel')
    private_records.write_bytes(science/'wheels.json',canonical({'files':{'synthetic.whl':{'bytes':5,'sha256':digest(b'wheel')}}}))
    smoke=tmp_path/'smoke.json';private_records.write_bytes(smoke,canonical({'cache_file_hashes':{'synthetic':digest(b'cache')}}))
    report=tmp_path/'review.md';private_records.write_text(report,'Synthetic approval, not genuine evidence. '+source+'\n## Verdict: APPROVE\n')
    settings={'smoke_path':str(smoke),'data_root':str(data),'wheel_root':str(wheels),'sdk_package':'synthetic','sdk_sha256':'b'*64,
      'credential_file':'not-read','workspace':'moroseui','batch_ledger':str(tmp_path/'ledger'),
      'resources':{'gpu':'A100-80GB','cpu':4,'memory_mib':32768,'timeout_seconds':1800},'overhead_micro_usd':500000}
    monkeypatch.setattr(modal_assets,'git',lambda root,*args:source if args==('rev-parse','HEAD') else '')
    monkeypatch.setattr(modal_assets,'validate_config',lambda *a:None) # Real cohort guard tested in test_sprint9_modal.
    monkeypatch.setattr(connectivity,'require',lambda *a:{'synthetic':True})
    monkeypatch.setattr(modal_assets,'workspace_spend',lambda p:0)
    monkeypatch.setattr(modal_assets,'require_supervisor',lambda *a:{'synthetic':True})
    class Missing(Exception):pass
    class NativeVolume(UploadVolume):
        def __init__(self,ident):super().__init__();self.object_id=ident
        def hydrate(self,**kwargs):return self
    class Remote:
        def __init__(self):self.apps={};self.volumes={};self.creates=[]
        def app(self,name,create_if_missing,**kwargs):
            if name not in self.apps:
                if not create_if_missing:raise Missing()
                self.apps[name]=NS(app_id='ap-synthetic');self.creates.append('app')
            return self.apps[name]
        def volume(self,name,create_if_missing):
            if name not in self.volumes:
                if not create_if_missing:raise Missing()
                self.volumes[name]=NativeVolume('vo-'+str(len(self.volumes)));self.creates.append(name)
            return self.volumes[name]
        def registry(self,name):
            assert name==modal_assets.BASE_IMAGE
            def build(app):self.creates.append('image');return NS(object_id='im-synthetic')
            return NS(build=build)
    remote=Remote();p=object.__new__(ModalProvider);p.client=object();p.config=settings
    p.modal=NS(App=NS(lookup=remote.app),Volume=NS(from_name=remote.volume),Image=NS(from_registry=remote.registry),exception=NS(NotFoundError=Missing))
    p._volume=lambda ident:next(v for v in remote.volumes.values() if v.object_id==ident)
    p.build_registry_image=lambda app,registry:remote.registry(registry).build(app)
    args=(root,tmp_path/'state',report,settings,tmp_path/'records/preparation')
    return args,p,remote,BatchAccounts(settings['batch_ledger'])


def test_full_preparation_reserves_before_remote_writes_and_finishes_last(preparation,monkeypatch):
    args,p,remote,batch=preparation
    original=remote.app
    def checked(*a,**kw):
        row=batch.db.execute('SELECT status FROM autonomy_assets').fetchone()
        assert row and row[0]=='RESERVED'
        return original(*a,**kw)
    p.modal.App.lookup=checked
    plan=modal_assets.prepare(*args,provider_factory=lambda config:p)
    assert read(args[-1]/'READY.json')['status']=='READY'
    row=batch.db.execute('SELECT * FROM autonomy_assets').fetchone()
    assert row['status']=='READY' and row['reserved_micro_usd']==MICRO
    assert plan==read(args[-1]/'lane-plan.json')
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    before=list(remote.creates)
    with pytest.raises(ValueError,match='EXISTING_MODAL_PREPARATION'):
        modal_assets.prepare(*args,provider_factory=lambda config:p)
    assert remote.creates==before
    private_records.check_tree(args[-1])


def test_partial_local_completion_cannot_publish_ready_accounting(preparation,monkeypatch):
    args,p,remote,batch=preparation;original=modal_assets.write_once
    def fail_plan(path,raw):
        if Path(path).name=='lane-plan.json':raise OSError('Synthetic disk failure')
        original(path,raw)
    monkeypatch.setattr(modal_assets,'write_once',fail_plan)
    with pytest.raises(ValueError,match='ASSET_PREPARATION_UNCERTAIN'):
        modal_assets.prepare(*args,provider_factory=lambda config:p)
    assert (args[-1]/'READY.json').exists() # File alone never qualifies approval.
    assert batch.db.execute('SELECT status FROM autonomy_assets').fetchone()[0]=='UNCERTAIN'
    assert not (args[-1]/'lane-plan.json').exists()
    before=list(remote.creates)
    with pytest.raises(ValueError,match='EXISTING_MODAL_PREPARATION'):
        modal_assets.prepare(*args,provider_factory=lambda config:p)
    assert remote.creates==before


def test_preparation_requires_ready_installed_retention_route_before_any_provider(preparation,monkeypatch):
    args,p,remote,batch=preparation
    def refuse(*args):raise ValueError('MODAL_RETENTION_TIMER_NOT_READY')
    monkeypatch.setattr(modal_assets,'require_supervisor',refuse)
    with pytest.raises(ValueError,match='RETENTION_TIMER'):
        modal_assets.prepare(*args,provider_factory=lambda cfg:pytest.fail('no authentication or provider write'))
    assert not remote.creates and not args[-1].exists()
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0


@pytest.mark.parametrize('active',['active','inactive'])
def test_native_supervisor_check_binds_release_sdk_and_timer(tmp_path,monkeypatch,active):
    from tools import manual_promotion
    from orchestrator import manual_host_guard
    state=tmp_path/'release/lane';record=state.parent/'modal-preparation';source='a'*40
    runtime_path=tmp_path/'runtime.json';runtime={'lane_backend':'modal','modal_sdk':{'package':'/opt/sdk','sha256':'b'*64}}
    private_records.write_bytes(runtime_path,canonical(runtime))
    selected={'source':source,'state':str(state.parent),'runtime':str(runtime_path),'runtime_sha256':digest(runtime_path.read_bytes()),'hash_list':str(tmp_path/'FILES.json'),'units':['research-modal.service','research-modal.timer']}
    pointer=tmp_path/'selected.json';private_records.write_bytes(pointer,canonical(selected))
    monkeypatch.setattr(manual_promotion,'POINTER',str(pointer));monkeypatch.setattr(manual_host_guard,'trusted',lambda p:Path(p))
    monkeypatch.setattr(manual_promotion,'manifest_check',lambda *a:{'source':source,'layout':{'units':selected['units']}})
    def observe(cmd,**kw):
        assert cmd==['/usr/bin/systemctl','show','research-modal.timer','--property=LoadState,UnitFileState,ActiveState']
        return 'LoadState=loaded\nUnitFileState=enabled\nActiveState='+active+'\n'
    monkeypatch.setattr(modal_assets.subprocess,'check_output',observe)
    settings={'sdk_package':'/opt/sdk','sdk_sha256':'b'*64}
    if active=='active':assert modal_assets.require_supervisor(settings,state,record,source)['timer']=='research-modal.timer'
    else:
        with pytest.raises(ValueError,match='TIMER_NOT_READY'):modal_assets.require_supervisor(settings,state,record,source)


def test_prepared_runtime_drives_real_cleanup_without_plural_alias(preparation,monkeypatch):
    # Native preparation -> native cleanup. Provider alone is synthetic.
    from orchestrator import modal_cleanup
    from test_modal_cleanup import Removable
    args,p,remote,batch=preparation
    modal_assets.prepare(*args,provider_factory=lambda config:p)
    runtime=read(args[-1]/'runtime.json')
    assert 'wheel_volume_id' in runtime and 'wheels_volume_id' not in runtime
    volumes={v.object_id:Removable(dict(v.files)) for v in remote.volumes.values()}
    p._volume=lambda ident:volumes[ident]
    before={kind:inventory(path) for kind,path in runtime['local_assets'].items() if Path(path).exists()}
    creations=list(remote.creates)
    result=modal_cleanup.clear_copies(p,runtime,args[-1]/'cleanup',collected=True)
    assert result['status']=='CLEARED'
    assert all(not v.files for v in volumes.values())
    assert before=={kind:inventory(path) for kind,path in runtime['local_assets'].items() if Path(path).exists()}
    assert remote.creates==creations
    assert modal_cleanup.clear_copies(p,runtime,args[-1]/'cleanup',collected=True)==result
    assert batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==0
