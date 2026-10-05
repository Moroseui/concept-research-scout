"""SDK adapter tests with API-shaped fakes. No authentication or paid operation."""
from decimal import Decimal
import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import private_records
from orchestrator.manual_executor import inventory,digest
from orchestrator.modal_executor import canonical
from orchestrator.modal_budget import estimate
from orchestrator.modal_provider import ModalProvider,member_map,safe_name


class NotFound(Exception):pass

class Volume:
    def __init__(self,files):self.files=files;self.read_only=None
    def listdir(self,*a,**kw):return [NS(path=k,size=len(v),type=NS(name='FILE')) for k,v in self.files.items()]
    def read_file(self,path):yield self.files[path.lstrip('/')]
    def with_mount_options(self,**kwargs):self.read_only=kwargs;return self

class Filesystem:
    def __init__(self):self.files={};self.aliases=set()
    def stat(self,path):
        if path in self.aliases:return NS(type=NS(value='symlink'),size=0)
        if path=='/tmp/outputs' or any(k.startswith(path+'/') for k in self.files):return NS(type=NS(value='directory'),size=0)
        if path not in self.files:raise NotFound(path)
        return NS(type=NS(value='file'),size=len(self.files[path]))
    def read_bytes(self,path):return self.files[path]

class Sandbox:
    def __init__(self):self.object_id='sb-test';self.filesystem=Filesystem();self.execs=[];self.exit_code=None
    def exec(self,*args,**kwargs):self.execs.append((args,kwargs))
    def poll(self):return self.exit_code
    def terminate(self,wait=False):assert wait;self.exit_code=137

@pytest.fixture
def provider(tmp_path):
    package=tmp_path/'package';private_records.mkdir(package)
    private_records.write_text(package/'run.py','# Synthetic only.\n')
    cfg={'asset_expires_utc':'2099-01-01T00:00:00+00:00','workspace':'moroseui','image_id':'im-test','data_volume_id':'vo-data','package_volume_id':'vo-package','wheel_volume_id':'vo-wheels','wheel_files':{'fixture.whl':{'bytes':3,'sha256':digest(b'whl')}},'app_name':'reviewed-test',
        'input_contract':{'scope':'DEVELOPMENT_99_ONLY','count':99,'cohort_sha256':'a'*64,'split_sha256':'b'*64,'cache_map_sha256':'c'*64},
        'data_files':{'one.npz':{'bytes':3,'sha256':digest(b'abc')}}}
    resources={'gpu':'A100-80GB','cpu':4,'memory_mib':32768,'timeout_seconds':1800}
    binding={'runtime_sha256':digest(canonical(cfg)),'resources':resources,'overhead_micro_usd':500000,'cost':estimate(resources,500000),
        'input_contract':cfg['input_contract'],'input_contract_sha256':digest(canonical(cfg['input_contract'])),'image_id':'im-test','data_volume_id':'vo-data','package_volume_id':'vo-package','wheel_volume_id':'vo-wheels','outputs':['result.csv']}
    volume={'vo-wheels':Volume({'fixture.whl':b'whl'}),'vo-data':Volume({'one.npz':b'abc'}),'vo-package':Volume({k:(package/k).read_bytes() for k in inventory(package)})}
    rates={'gpu_hour_cost_a100_80gb':Decimal('2.50'),'cpu_hour_cost_sandbox':Decimal('.1419'),'mem_gib_hour_cost_sandbox':Decimal('.024')}
    ws=NS(name='moroseui',hydrate=lambda **kw:None,billing=NS(rates=lambda:rates,summary=lambda **kw:NS(metered_cost=Decimal('.1234561'),billed_cost=Decimal('0'))))
    sb=Sandbox();created=[]
    def create(*args,**kwargs):created.append((args,kwargs));return sb
    adapter=object.__new__(ModalProvider);adapter.config=cfg;adapter.client=NS(hello=lambda:None)
    adapter.modal=NS(Workspace=NS(from_context=lambda **kw:ws),Volume=NS(from_id=lambda ident,**kw:volume[ident]),
        Sandbox=NS(from_id=lambda ident,**kw:sb,create=create),Image=NS(from_id=lambda ident,**kw:NS(object_id=ident,build=lambda app:None)),
        App=NS(lookup=lambda *args,**kw:'existing-app'),stream_type=NS(StreamType=NS(DEVNULL='DEVNULL')),exception=NS(SandboxFilesystemNotFoundError=NotFound))
    return adapter,cfg,binding,package,volume,sb,created,rates,ws


def test_preflight_verifies_actual_remote_bytes_without_starting(provider):
    p,c,b,package,vol,sb,created,rates,ws=provider
    assert p.preflight(c,b,package)['workspace_spent_micro']==123457
    assert not created and not sb.execs
    vol['vo-data'].files['one.npz']=b'bad'
    with pytest.raises(ValueError,match='VOLUME_HASH'):p.preflight(c,b,package)
    assert not created

@pytest.mark.parametrize('damage',['workspace','rate','member','contract','image'])
def test_preflight_refuses_authority_and_asset_changes(provider,damage):
    p,c,b,package,vol,sb,created,rates,ws=provider
    if damage=='workspace':ws.name='other'
    if damage=='rate':rates['cpu_hour_cost_sandbox']=Decimal('.20')
    if damage=='member':vol['vo-data'].files['extra']=b''
    if damage=='contract':b['input_contract_sha256']='f'*64
    if damage=='image':b['image_id']='im-other'
    with pytest.raises(ValueError):p.preflight(c,b,package)
    assert not created and not sb.execs


def test_create_is_idle_confined_and_launch_is_separate(provider):
    p,c,b,package,vol,sb,created,rates,ws=provider
    assert p.create(c,b,package)['provider_id']=='sb-test'
    args,kw=created[0]
    assert args==('/bin/sleep','1800') and not sb.execs
    assert kw['block_network'] and not kw['include_oidc_identity_token'] and kw['secrets']==[]
    assert kw['cpu']==(4,4) and kw['memory']==(32768,32768) and kw['timeout']==1800
    assert all(v.read_only=={'read_only':True} for v in vol.values())
    assert not kw['encrypted_ports'] and not kw['unencrypted_ports'] and not kw['h2_ports']
    p.launch('sb-test',b)
    assert len(sb.execs)==1 and sb.execs[0][0][-1]==digest(canonical(b))
    for _ in range(3):assert p.status('sb-test',b)['status']=='RUNNING'
    assert len(sb.execs)==1 and len(created)==1
    sb.exit_code=1
    assert p.status('sb-test',b)['status']=='UNKNOWN'


def completed(p,b,sb):
    data=b'metric,value\ndice,0.1\n';files={'result.csv':{'bytes':len(data),'sha256':digest(data)}}
    sb.filesystem.files={'/tmp/outputs/result.csv':data,'/tmp/research-result.json':canonical({'schema':'modal-result/v1','binding_sha256':digest(canonical(b)),'status':'COMPLETE','files':files})}
    return data


def test_collect_hashes_and_preserves_then_terminates(provider,tmp_path):
    p,c,b,package,vol,sb,created,rates,ws=provider;data=completed(p,b,sb)
    assert p.status('sb-test',b)['status']=='COMPLETE'
    dest=tmp_path/'collected';private_records.mkdir(dest)
    result=p.collect('sb-test',b,dest)
    assert result['file_sha256']==inventory(dest) and (dest/'result.csv').read_bytes()==data
    private_records.check_tree(dest)
    assert p.terminate('sb-test')['terminated']
    assert not sb.execs and not created

@pytest.mark.parametrize('damage',['body','binding','extra','alias'])
def test_collection_refuses_hash_binding_member_or_alias(provider,tmp_path,damage):
    p,c,b,package,vol,sb,created,rates,ws=provider;completed(p,b,sb)
    key='/tmp/research-result.json';result=json.loads(sb.filesystem.files[key])
    if damage=='body':sb.filesystem.files['/tmp/outputs/result.csv']=b'changed'
    if damage=='binding':result['binding_sha256']='f'*64
    if damage=='extra':result['files']['extra.txt']={'bytes':0,'sha256':digest(b'')}
    if damage=='alias':sb.filesystem.aliases.add('/tmp/outputs')
    sb.filesystem.files[key]=canonical(result)
    dest=tmp_path/'collected';private_records.mkdir(dest)
    with pytest.raises(ValueError):p.collect('sb-test',b,dest)
    assert not sb.execs and not created

@pytest.mark.parametrize('name',['../outside','/absolute','a//b','a/./b','a/../b','a\\b',''])
def test_member_paths_refuse_ambiguous_or_external_names(name):
    with pytest.raises(ValueError):safe_name(name)


def test_expired_asset_binding_refuses_before_submission(provider):
    p,c,b,package,vol,sb,created,rates,ws=provider
    c['asset_expires_utc']='2000-01-01T00:00:00+00:00';b['runtime_sha256']=digest(canonical(c))
    with pytest.raises(ValueError,match='RETENTION_EXPIRED'):p.preflight(c,b,package)
    assert not created and not sb.execs


def test_builder_pin_and_from_only_commands_are_checked(provider,monkeypatch):
    import sys,os,types
    p,*_=provider;calls=[]
    native=types.ModuleType('modal._image');native._Image=NS(_registry_setup_commands=lambda *a:['FROM '+a[0]])
    config=types.ModuleType('modal.config');config.config=NS(get=lambda key:os.environ.get('MODAL_IMAGE_BUILDER_VERSION'))
    monkeypatch.setitem(sys.modules,'modal._image',native);monkeypatch.setitem(sys.modules,'modal.config',config)
    p.modal.Image.from_registry=lambda registry:NS(build=lambda app:calls.append((registry,os.environ['MODAL_IMAGE_BUILDER_VERSION'])) or NS(object_id='im-synthetic'))
    monkeypatch.setenv('MODAL_IMAGE_BUILDER_VERSION','2024.10')
    assert p.build_registry_image('ap','pinned-registry').object_id=='im-synthetic'
    assert calls==[('pinned-registry','2025.06')] and os.environ['MODAL_IMAGE_BUILDER_VERSION']=='2024.10'
    native._Image._registry_setup_commands=lambda *a:['FROM '+a[0],'RUN unwanted']
    with pytest.raises(ValueError,match='BUILD_COMMANDS'):p.build_registry_image('ap','pinned-registry')
    assert len(calls)==1 and os.environ['MODAL_IMAGE_BUILDER_VERSION']=='2024.10'


def test_preflight_resolves_existing_image_not_unsupported_hydrate(provider):
    p,c,b,package,vol,sb,created,rates,ws=provider
    looked=[];resolved=[]
    class Image:
        object_id='im-test'
        def hydrate(self,**kw):raise AssertionError('SDK1.6 refuses Image hydration')
        def build(self,app):resolved.append(app);return self
    def lookup(name,**kw):
        assert name==c['app_name'] and kw=={'create_if_missing':False,'client':p.client}
        looked.append(name);return 'existing-app'
    p.modal.App.lookup=lookup;p.modal.Image.from_id=lambda ident,**kw:Image()
    assert p.preflight(c,b,package)['image_id']=='im-test'
    assert looked==[c['app_name']] and resolved==['existing-app']
    assert not created and not sb.execs


@pytest.mark.parametrize('failure',['image_missing','app_missing','wrong_id'])
def test_image_resolution_refuses_before_create_or_launch(provider,failure):
    p,c,b,package,vol,sb,created,rates,ws=provider
    class Image:
        object_id='im-test'
        def build(self,app):
            if failure=='image_missing':raise NotFound('original image unavailable')
            if failure=='wrong_id':self.object_id='im-wrong'
            return self
    def lookup(*a,**kw):
        assert kw['create_if_missing'] is False
        if failure=='app_missing':raise NotFound('original app unavailable')
        return 'existing-app'
    p.modal.App.lookup=lookup;p.modal.Image.from_id=lambda *a,**kw:Image()
    if failure=='wrong_id':
        with pytest.raises(ValueError,match='^MODAL_IMAGE_ID_CHANGED$'):p.preflight(c,b,package)
    else:
        with pytest.raises(NotFound):p.preflight(c,b,package)
    assert not created and not sb.execs
