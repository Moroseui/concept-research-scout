"""Real worker, package and receipt consumers; fake paid SDK and HTTP only."""
from pathlib import Path
from types import SimpleNamespace as NS
import json
import hashlib
import pytest
from test_modal_ctp_download import planned,image_plan
from test_modal_direct_budget import billing
from test_modal_direct_budget import NOW
from orchestrator import modal_download_package as package, modal_download_provider as route
from orchestrator import modal_ctp_download as worker, modal_direct_budget as budget, private_records
from orchestrator.modal_ctp_download import encoded
from orchestrator.modal_executor import canonical
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_budget import ComputeAccounts


class Missing(Exception):pass

class Volume:
    def __init__(self,root,name):
        self.root=root;self.object_id='vo-'+name;private_records.mkdir(root)
        self.reads=[]
    def hydrate(self,**kw):return self
    def listdir(self,*a,**kw):
        return [NS(path='/'+str(p.relative_to(self.root)),size=p.stat().st_size,
                   type=NS(name='FILE' if p.is_file() else 'DIRECTORY')) for p in self.root.rglob('*')]
    def read_file(self,name):
        assert '/train/' not in name,'controller attempted imaging read'
        self.reads.append(name);yield (self.root/name.lstrip('/')).read_bytes()
    def remove_file(self,name,recursive):
        assert recursive is False and '/train/' in name
        (self.root/name.lstrip('/')).unlink()
    def with_mount_options(self,**kw):return NS(volume=self,options=kw)
    def batch_upload(self,**kw):
        assert kw=={'force':False};return self
    def __enter__(self):return self
    def __exit__(self,*a):pass
    def put_file(self,source,target,mode):
        assert mode==0o440
        p=self.root/target.lstrip('/');private_records.mkdir(p.parent,parents=True,exist_ok=True)
        private_records.copyfile(source,p)


@pytest.fixture
def fixture(planned,tmp_path):
    f=planned;ctp=f.plan;image_plan(f);plans={'ctp':ctp,'images':f.plan}
    prepared=tmp_path/'package';emitted=package.emit(Path(__file__).resolve().parents[1],prepared,f.cohort,plans,'first')
    batch=BatchAccounts(tmp_path/'ledger');accounts=ComputeAccounts(batch)
    batch.register_run('inputs',{'purpose':budget.PURPOSE,'authority_sha256':budget.AUTHORITY})
    view=billing();binding={'purpose':budget.PURPOSE,'authority_sha256':budget.AUTHORITY,
      'download_authority_sha256':budget.DOWNLOAD_AUTHORITY,'team_authority_sha256':budget.TEAM_AUTHORITY,
      'run_id':'inputs','download_bytes':emitted['planned_download_bytes'],
      'envelope':budget.envelope(emitted['planned_download_bytes'],view['rates']),
      'package_manifest_sha256':emitted['manifest_sha256']}
    budget.reserve(accounts,hashlib.sha256(canonical(binding)).hexdigest(),'inputs',binding,billing_snapshot=view,now=NOW)
    volumes={};calls=[];app=NS(app_id='ap-private');image=NS(object_id='im-pinned');sandbox=NS(object_id='sb-once',poll=lambda:0)
    def lookup(name,create_if_missing,**kw):
        if not create_if_missing:raise Missing()
        calls.append(('app',name));return app
    def from_name(name,create_if_missing,version,**kw):
        assert version==2
        if not create_if_missing:raise Missing()
        v=Volume(tmp_path/name,name);volumes[v.object_id]=v;calls.append(('volume',name));return v
    def create(*args,**kw):
        calls.append(('sandbox',args,kw));return sandbox
    ws=NS(name='moroseui',hydrate=lambda **kw:None)
    provider=NS(config={'workspace':'moroseui'},client=NS(hello=lambda:None),
      modal=NS(App=NS(lookup=lookup),Volume=NS(from_name=from_name),Sandbox=NS(create=create),
               Workspace=NS(from_context=lambda **kw:ws),exception=NS(NotFoundError=Missing)),
      build_registry_image=lambda *a:image,_sandbox=lambda ident:sandbox,
      _volume=lambda ident:volumes[ident])
    def verify(ident,expected):
        v=volumes[ident]
        assert {str(p.relative_to(v.root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in v.root.rglob('*') if p.is_file()}=={k:r['sha256'] for k,r in expected.items()}
    provider._verify_volume=verify
    return NS(f=f,plans=plans,prepared=prepared,binding=binding,accounts=accounts,batch=batch,
              provider=provider,calls=calls,volumes=volumes,sandbox=sandbox,record=tmp_path/'records')


def launch(f):return route.launch(f.provider,f.accounts,f.binding,f.prepared,f.record)


def complete(f,handle):
    volume=f.volumes[handle['data_volume_id']];manifest=package.verify(f.prepared,f.binding['package_manifest_sha256']);results={}
    for kind,plan in f.plans.items():
        root=volume.root/kind;private_records.mkdir(root)
        # Real streaming checks, durable worker records and second read. Only
        # HTTP transport and host-specific sync are synthetic here.
        results[kind]=worker.download(plan,f.f.cohort,root,'first-'+kind,
            plan_sha256=manifest['plans'][kind]['sha256'],opener=f.f.opener,commit=lambda p:None)
    private_records.write_bytes(volume.root/'DOWNLOAD_COMPLETE.json',encoded({
       'schema':'private-development-download-result/v1','manifest_sha256':f.binding['package_manifest_sha256'],
       'results':results,'patient_computation':False}))


def test_provider_is_bound_cpu_only_and_no_credentials(fixture):
    f=fixture;handle=launch(f);args,kw=f.calls[-1][1:]
    assert args==('/usr/bin/python3','-I','-S','-B','/reviewed/run.py',f.binding['package_manifest_sha256'],'all',handle['data_volume_id'])
    assert kw['gpu'] is None and kw['cpu']==(1,1) and kw['memory']==(2048,2048) and kw['timeout']==21600
    assert kw['secrets']==[] and kw['env']=={} and kw['include_oidc_identity_token'] is False
    assert kw['outbound_cidr_allowlist']==[] and kw['outbound_domain_allowlist']==list(route.DOMAINS)
    assert kw['inbound_cidr_allowlist']==[] and kw['encrypted_ports']==[]
    assert set(kw['volumes'])=={'/reviewed','/volume'} and kw['volumes']['/reviewed'].options=={'read_only':True}
    assert (f.record/'sandbox-intent.json').is_file()
    assert f.batch.db.execute('select count(*) from autonomy_calls').fetchone()[0]==0


def test_real_worker_to_provider_receipts_no_payload_returns_and_idempotent_observation(fixture):
    f=fixture;handle=launch(f);complete(f,handle)
    before=len(f.calls);one=route.observe(f.provider,f.binding,f.prepared,handle);two=route.observe(f.provider,f.binding,f.prepared,handle)
    assert one==two and len(f.calls)==before
    assert one['status']=='VERIFIED' and one['controller_image_bytes_read']==0
    assert one['scopes']['ctp']['files']==99 and one['scopes']['images']['files']==693
    assert all('/train/' not in p for p in f.volumes[handle['data_volume_id']].reads)
    with pytest.raises(ValueError,match='^DIRECT_DOWNLOAD_EXISTING_INTENT_RECONCILE$'):launch(f)
    assert len(f.calls)==before


@pytest.mark.parametrize('defect',['missing','hash','extra','summary','record-extra'])
def test_altered_completed_receipts_or_inventory_refuse(fixture,defect):
    f=fixture;handle=launch(f);complete(f,handle);root=f.volumes[handle['data_volume_id']].root
    if defect=='missing':next((root/'ctp/train').rglob('*.nii.gz')).unlink()
    elif defect=='extra':private_records.write_bytes(root/'unselected.bin',b'not allowed')
    elif defect=='record-extra':private_records.write_bytes(root/'ctp/download-records/first-ctp/unselected.bin',b'not allowed')
    elif defect=='summary':
        p=root/'DOWNLOAD_COMPLETE.json';v=json.loads(p.read_bytes());v['manifest_sha256']='0'*64;p.write_bytes(encoded(v))
    else:
        p=root/'ctp/download-records/first-ctp/001-verified.json';v=json.loads(p.read_bytes());v['sha256']='0'*64;p.write_bytes(encoded(v))
    with pytest.raises(ValueError,match='^DIRECT_DOWNLOAD_'):route.observe(f.provider,f.binding,f.prepared,handle)


def test_lost_create_response_never_launches_again(fixture):
    f=fixture
    def lost(*a,**kw):f.calls.append(('lost-create',));raise TimeoutError('synthetic transport')
    f.provider.modal.Sandbox.create=lost
    with pytest.raises(TimeoutError):launch(f)
    assert (f.record/'sandbox-intent.json').exists() and not (f.record/'sandbox.json').exists()
    with pytest.raises(ValueError,match='^DIRECT_DOWNLOAD_EXISTING_INTENT_RECONCILE$'):launch(f)
    assert sum(x[0]=='lost-create' for x in f.calls)==1
    assert f.batch.db.execute('select status from autonomy_assets').fetchone()[0]=='RESERVED'


def test_no_start_without_reservation_or_with_altered_package(fixture):
    f=fixture;f.batch.db.execute("update autonomy_assets set status='UNCERTAIN'")
    with pytest.raises(ValueError,match='^DIRECT_DOWNLOAD_RESERVED_BINDING_REQUIRED$'):launch(f)
    assert f.calls==[] and not f.record.exists()


def test_pending_and_failed_container_do_not_claim_verification_or_read_volume(fixture):
    f=fixture;handle=launch(f)
    for code,status in [(None,'RUNNING'),(1,'FAILED')]:
        f.sandbox.poll=lambda:code
        assert route.observe(f.provider,f.binding,f.prepared,handle)['status']==status
        assert f.volumes[handle['data_volume_id']].reads==[]
