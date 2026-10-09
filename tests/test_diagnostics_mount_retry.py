"""Synthetic exact-parent retry: real ledger, package verifier and native worker."""
import copy,json,os,shutil,subprocess
from pathlib import Path
import pytest
from orchestrator import diagnostics_mount_retry as retry,diagnostics_execution as de
from orchestrator import diagnostics_budget as budget,diagnostics_contract as dc,private_records as pr
from orchestrator.modal_budget import ComputeAccounts
from orchestrator.modal_item4_policy import quote
from orchestrator.modal_executor import ModalExecutor,verify_package
from test_diagnostics_connection import prepared,CPUProvider,ITEM4_RATES,private_test_environment
from test_modal_item4_budget import snapshot,NOW

@pytest.fixture
def retry_ready(prepared,monkeypatch):
    folder,old,config,batch=prepared
    old['overhead_micro_usd']=1951600-old['cost']['reserved_micro_usd']
    old['cost']=quote(old['resources'],ITEM4_RATES,old['overhead_micro_usd'])
    code=(folder/'code/analysis.py').read_text()
    code=code.replace("output_root=Path(output_root);runtime=contract['runtime']", "output_root=Path(output_root);runtime=contract['runtime'];assert contract['requirements']==runtime['program_contract']['requirements'];assert {k:contract[k] for k in runtime['program_contract']}==runtime['program_contract']")
    pr.write_text(folder/'code/analysis.py',code)
    program=json.loads((folder/'code/analysis.program.json').read_bytes());program['files']['analysis.py']=code
    pr.write_bytes(folder/'code/analysis.program.json',dc.encoded(program))
    old['code_sha256']=dc.sha(code.encode());old['program_sha256']=dc.sha(dc.encoded(program))
    manifest=json.loads((folder/'manifest.json').read_bytes());manifest['binding']=old
    manifest['files'].update({'code/analysis.py':old['code_sha256'],'code/analysis.program.json':old['program_sha256']})
    pr.write_bytes(folder/'manifest.json',dc.encoded(manifest))
    original=dc.sha(dc.encoded(old));monkeypatch.setattr(retry,'ORIGINAL',original)
    mounts={'data':{'volume_id':'vo-data','sub_path':'/selected'},'package':{'volume_id':'vo-code','sub_path':'/'}}
    monkeypatch.setattr(retry,'MOUNTS',mounts)
    # Clearly synthetic history: first failed launch admitted normally; prior
    # approved mount retry is a fixed historical row. New admission stays real.
    accounts=ComputeAccounts(batch)
    assert budget.reserve(accounts,original,old['run_id'],old,billing_snapshot=snapshot(),now=NOW)
    batch.db.execute("UPDATE autonomy_compute SET status='RUNNING',provider_id=? WHERE id=?",(retry.ORIGINAL_PROVIDER,original))
    prior_descriptor={'synthetic_previous_mount_retry':True,'parent':original}
    previous={**old,'mechanical_retry':prior_descriptor};parent=dc.sha(dc.encoded(previous))
    monkeypatch.setattr(retry,'PARENT',parent);monkeypatch.setattr(retry,'prior_permit',lambda:{'descriptor':prior_descriptor})
    batch.db.execute("INSERT INTO autonomy_compute(id,run,binding,status,reserved_micro_usd,actual_micro_usd,provider_id,month) VALUES(?,?,?,'RUNNING',1951600,NULL,?,?)",(parent,old['run_id'],dc.encoded(previous).decode(),retry.PROVIDER_ID,NOW.strftime('%Y-%m')))
    descriptor=retry.descriptor('a'*64)
    monkeypatch.setattr(retry,'permit',lambda:{'descriptor':descriptor})
    binding={**old,'mechanical_retry':descriptor}
    return folder,binding,config,batch,accounts


def rows(batch):return [tuple(r) for r in batch.db.execute('SELECT * FROM autonomy_compute ORDER BY id')]


def test_retry_retains_original_charge_owner_and_bytes(retry_ready):
    folder,b,_,batch,accounts=retry_ready
    before=rows(batch);original=(folder/'manifest.json').read_bytes();ident=dc.sha(dc.encoded(b))
    assert verify_package(folder,b)['binding']==retry.parent_binding(b)
    assert retry.job(b)==b['run_id']+'-contract-retry1'
    assert budget.reserve(accounts,ident,b['run_id'],b,billing_snapshot=snapshot(),now=NOW)
    assert all(row in rows(batch) for row in before) and len(rows(batch))==3
    assert batch.db.execute('SELECT sum(reserved_micro_usd) FROM autonomy_compute').fetchone()[0]==5854800
    assert (folder/'manifest.json').read_bytes()==original
    saved=rows(batch)
    assert budget.reserve(accounts,ident,b['run_id'],b,billing_snapshot=snapshot(),now=NOW) is False
    assert rows(batch)==saved


@pytest.mark.parametrize('damage',['cap','actual-cost-cap','uncertain-parent','wrong-provider','wrong-charge','unrelated-uncertain','second-retry','changed-parent','changed-authority'])
def test_retry_refusals_preserve_ledger(retry_ready,damage):
    _,b,_,batch,accounts=retry_ready;b=copy.deepcopy(b)
    if damage=='cap':
        # Fits if the first reservation is incorrectly forgotten; exceeds with it.
        batch.db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,'READY',?,?)",('prep',b['run_id'],'{}',95000000,'{}'))
    if damage=='actual-cost-cap':
        batch.db.execute('UPDATE autonomy_compute SET actual_micro_usd=99000000')
    if damage=='uncertain-parent':batch.db.execute("UPDATE autonomy_compute SET status='UNCERTAIN'")
    if damage=='wrong-provider':batch.db.execute("UPDATE autonomy_compute SET provider_id='sb-other'")
    if damage=='wrong-charge':batch.db.execute('UPDATE autonomy_compute SET reserved_micro_usd=1')
    if damage=='unrelated-uncertain':
        batch.db.execute("INSERT INTO autonomy_compute(id,run,binding,status,reserved_micro_usd,actual_micro_usd,provider_id,month) SELECT 'unresolved',run,binding,'UNCERTAIN',reserved_micro_usd,actual_micro_usd,provider_id,month FROM autonomy_compute LIMIT 1")
    if damage=='second-retry':
        ident=dc.sha(dc.encoded(b));assert budget.reserve(accounts,ident,b['run_id'],b,billing_snapshot=snapshot(),now=NOW)
        b['mechanical_retry']['attempt']=4
    if damage=='changed-parent':b['provisioning_sha256']='e'*64
    if damage=='changed-authority':b['mechanical_retry']['authority_sha256']='e'*64
    before=rows(batch)
    with pytest.raises(ValueError,match='DIAGNOSTICS_HARD_COST_CAP' if damage in {'cap','actual-cost-cap'} else None):budget.reserve(accounts,dc.sha(dc.encoded(b)),b['run_id'],b,billing_snapshot=snapshot(),now=NOW)
    assert rows(batch)==before


def test_retry_executor_does_not_repeat_uncertain_create(retry_ready,tmp_path):
    folder,b,config,batch,_=retry_ready;p=CPUProvider();p.failure='create'
    e=ModalExecutor(tmp_path/'lane/jobs.sqlite',config,p,batch);job=retry.job(b)
    with pytest.raises(ValueError,match='UNCERTAIN_SUBMISSION'):e.submit(job,b,folder,tmp_path/'emitted')
    count=p.calls.count('create');p.failure=None
    e.submit(job,b,folder,tmp_path/'emitted')
    assert p.calls.count('create')==count==1
    assert len(rows(batch))==3 and len(set(rows(batch)))==3


def mount_proof(b):
    inputs={k:{f:v[f] for f in ('sha256','bytes')} for k,v in b['input_contract']['files'].items()}
    evidence={'data':{'files':len(inputs),'inventory_sha256':dc.sha(dc.encoded(inputs))},
        'package':{'files':30,'inventory_sha256':'788e55ab77f0bf03be72b99d9e47418722d003e2d1fb9edfc241db738c161976'}}
    for role,v in evidence.items():v.update(retry.MOUNTS[role],write_refusal_probes=2)
    return {'schema':'diagnostics-mount-verification/v1','status':'PASS','binding_sha256':dc.sha(dc.encoded(b)),
        'worker_sha256':b['mechanical_retry']['worker_sha256'],'before':evidence,'after':copy.deepcopy(evidence),'full_rehash_before_and_after':True}


@pytest.mark.parametrize('damage',[None,'missing-post','changed-post','missing-member','wrong-volume','no-probe','wrong-worker','no-controls'])
def test_collection_requires_complete_pinned_pre_and_post_evidence(retry_ready,damage):
    _,b,_,_,_=retry_ready;p=mount_proof(b)
    if damage=='missing-post':p.pop('after')
    if damage=='changed-post':p['after']['data']['inventory_sha256']='f'*64
    if damage=='missing-member':p['before']['data']['files']=p['after']['data']['files']=0
    if damage=='wrong-volume':p['before']['package']['volume_id']=p['after']['package']['volume_id']='vo-other'
    if damage=='no-probe':p['before']['data']['write_refusal_probes']=p['after']['data']['write_refusal_probes']=0
    if damage=='wrong-worker':p['worker_sha256']='f'*64
    if damage is None:assert retry.validate_mount_proof(p,b)==p
    elif damage=='no-controls':
        with pytest.raises(ValueError):retry.validate_collected_proof({'mount_verification':p},b)
    else:
        with pytest.raises(ValueError):retry.validate_mount_proof(p,b)


@pytest.mark.skipif(not shutil.which('bwrap'),reason='Native bubblewrap unavailable')
@pytest.mark.parametrize('damage',[None,'writable-data','writable-package','extra-input','changed-package','missing-contract'])
def test_native_worker_preserves_package_and_checks_modal_style_mounts(retry_ready,tmp_path,damage):
    folder,b,_,_,_=retry_ready
    data=tmp_path/'data';out=tmp_path/'native';pr.mkdir(data);pr.mkdir(out);pr.write_bytes(data/'synthetic.bin',b'synthetic')
    if damage=='extra-input':pr.write_bytes(data/'unselected',b'not selected')
    if damage=='changed-package':pr.write_bytes(folder/'SPEC.md',b'changed')
    before={str(p.relative_to(folder)):p.read_bytes() for p in folder.rglob('*') if p.is_file()}
    links=[]
    for name in ('/bin','/lib','/lib64'):
        p=Path(name)
        if p.exists():
            assert p.is_symlink() and p.resolve().is_relative_to('/usr')
            links+=['--symlink',os.readlink(p),name]
    source=retry.program()
    if damage=='missing-contract':source=source.replace("{**binding['program_contract'],'execution_plan':","{'execution_plan':")
    cmd=['bwrap','--unshare-all','--die-with-parent','--new-session','--clearenv','--ro-bind','/usr','/usr',*links,
        '--dev','/dev','--proc','/proc','--bind',str(out),'/tmp',
        '--bind' if damage=='writable-data' else '--ro-bind',str(data),'/__modal/volumes/vo-data',
        '--bind' if damage=='writable-package' else '--ro-bind',str(folder),'/__modal/volumes/vo-code',
        '--symlink','/__modal/volumes/vo-data','/data','--symlink','/__modal/volumes/vo-code','/reviewed',
        '--chdir','/tmp','/usr/bin/python3','-s','-B','-c',source,'--binding',dc.sha(dc.encoded(b)),
        '--retry',dc.encoded(b['mechanical_retry']).decode()]
    done=subprocess.run(cmd,capture_output=True,timeout=30)
    result=json.loads((out/'research-result.json').read_bytes())
    if damage is None:
        assert done.returncode==0,done.stderr.decode()
        assert result['status']=='COMPLETE'
        evidence=json.loads((out/'mount-verification.json').read_bytes())
        assert evidence['before']==evidence['after'] and evidence['full_rehash_before_and_after']
        assert evidence['before']['package']['files']==len(before)
        assert dc.validate_outputs(out/'outputs',b)['status']=='VALIDATED'
    elif damage=='missing-contract':
        assert result['status']=='FAILED' and done.returncode!=0
        assert not any((out/'outputs').iterdir()) and (out/'mount-guard-after.json').exists()
        assert json.loads((out/'worker-failure.json').read_bytes())=={'schema':'diagnostics-worker-failure/v1','phase':'analysis','exception_type':'KeyError','missing_contract_key':'requirements'}
    else:
        assert result['status']=='FAILED' and done.returncode!=0
        assert not (out/'outputs').exists() and not (out/'mount-verification.json').exists()
    assert all((folder/n).read_bytes()==raw for n,raw in before.items())


def control_proof(b):
    raw=b'synthetic non-patient mount-control fixture\n'
    pin=dc.sha(dc.encoded({'nested/source.bin':{'sha256':dc.sha(raw),'bytes':len(raw)}}))
    cases={}
    for n,name in enumerate(('read_only','writable_data','writable_package')):
        mounts={'data':{'volume_id':'vo-syntheticdata'+str(n),'sub_path':'/inputs'},
                'package':{'volume_id':'vo-syntheticpackage'+str(n),'sub_path':'/'}}
        result={'schema':'diagnostics-mount-control/v1','case':name,'status':'REJECTED_WRITABLE','reason':'DIAGNOSTICS_WRITE_WAS_ALLOWED'}
        if name=='read_only':result.update(status='PASS',reason=None,proof={r:{**mounts[r],'files':1,'inventory_sha256':pin,'write_refusal_probes':2} for r in mounts})
        cases[name]={'provider_id':'sb-synthetic'+str(n),'terminated':True,'mounts':mounts,'result':result}
    return {'schema':'diagnostics-native-controls/v1','status':'PASS','controls_sha256':b['mechanical_retry']['controls_sha256'],'cases':cases}


@pytest.mark.parametrize('damage',[None,'missing-case','not-stopped','same-sandbox','patient-volume','wrong-subpath','bad-fixture','insufficient-probes','writable-passed','wrong-control-source'])
def test_native_control_evidence_refuses_missing_or_wrong_protection(retry_ready,damage):
    _,b,_,_,_=retry_ready;v=control_proof(b);cases=v['cases']
    if damage=='missing-case':cases.pop('writable_package')
    if damage=='not-stopped':cases['read_only']['terminated']=False
    if damage=='same-sandbox':cases['writable_data']['provider_id']=cases['read_only']['provider_id']
    if damage=='patient-volume':cases['writable_data']['mounts']['data']['volume_id']=retry.MOUNTS['data']['volume_id']
    if damage=='wrong-subpath':cases['writable_package']['mounts']['data']['sub_path']='/'
    if damage=='bad-fixture':cases['read_only']['result']['proof']['data']['inventory_sha256']='f'*64
    if damage=='insufficient-probes':cases['read_only']['result']['proof']['package']['write_refusal_probes']=1
    if damage=='writable-passed':cases['writable_package']['result']['status']='PASS'
    if damage=='wrong-control-source':v['controls_sha256']='f'*64
    if damage is None:
        assert retry.validate_controls(v,b)==v
        retry.validate_collected_proof({'mount_verification':mount_proof(b),'native_mount_controls':v},b)
    else:
        with pytest.raises(ValueError):retry.validate_controls(v,b)


def test_component_modules_load_in_fresh_process_without_early_import():
    # Synthetic path/trust boundary only. Real dependency loading order executes.
    code="""from pathlib import Path
from tools import item6_native_mount_service as service
root=Path.cwd();service.ROOT=root;service.SPENDING=str(root)
service.checked=lambda:None
original=service.file_module
def load(name,path):
 m=original(name,path)
 if name=='orchestrator.diagnostics_mount_retry':m.permit=lambda:{'synthetic_fixture':True}
 return m
service.file_module=load
assert service.load('verify-execute')=={'synthetic_fixture':True}
print('PASS')
"""
    import sys
    r=subprocess.run([sys.executable,'-s','-B','-c',code],capture_output=True,text=True)
    assert r.returncode==0,r.stderr
    assert r.stdout.strip()=='PASS'


@pytest.mark.parametrize('mode',['execute','science','state'])
def test_new_units_keep_every_existing_confinement_line(mode):
    from tools.install_item6_native_mount import unit_text
    from tools import item6_native_mount_service as s
    command=('ExecStart=/usr/bin/python3 -s -B '+str(s.INPUT_ROOT)+'/tools/item6_input_service.py advance' if mode=='execute'
        else 'ExecStart=/usr/bin/python3 -s -B '+str(s.DAILY)+'/tools/daily_limit_component.py 6')
    original='[Service]\nUser=partho\nGroup=partho\nNoNewPrivileges=true\nProtectSystem=strict\nPrivateTmp=true\nExecStartPre=synthetic-existing-check\n'+command+'\nRestart=no\n'
    result=unit_text(original,mode)
    assert [x for x in result.splitlines() if not x.startswith('ExecStart=')]==[x for x in original.splitlines() if not x.startswith('ExecStart=')]
    with pytest.raises(ValueError):unit_text(original.replace(command,'ExecStart=unrecognized'),mode)


@pytest.mark.skipif(not shutil.which('bwrap'),reason='Native bubblewrap unavailable')
@pytest.mark.parametrize('damage',[None,'readonly-actually-writable','writable-actually-readonly'])
def test_control_harness_executes_native_synthetic_cases_and_stops(retry_ready,tmp_path,damage):
    from contextlib import contextmanager
    from types import SimpleNamespace
    folder,b,config,_,_=retry_ready;created=[];stopped=[];volumes=[]
    work=folder.parent/'modal-executions'/retry.job(b);pr.mkdir(work,parents=True)
    pr.write_bytes(work/'create-intent.json',dc.encoded({'binding_sha256':dc.sha(dc.encoded(b)),
        'preflight':{'billing_snapshot':snapshot()}}))
    class Volume:
        def __init__(self):
            self.object_id='vo-nativefixture'+str(len(volumes));self.path=tmp_path/self.object_id
            pr.mkdir(self.path);volumes.append(self)
        @classmethod
        @contextmanager
        def ephemeral(cls,**kwargs):
            assert kwargs=={'client':'synthetic','version':2};yield cls()
        @contextmanager
        def batch_upload(self):yield self
        def put_file(self,stream,path):pr.write_bytes(self.path/path.lstrip('/'),stream.read())
        def with_mount_options(self,**kwargs):return self,kwargs
    class Sandbox:
        @classmethod
        def create(cls,*args,**kw):
            assert args==('/bin/sleep','120')
            assert kw['block_network'] and not kw['include_oidc_identity_token']
            assert kw['secrets']==kw['encrypted_ports']==kw['h2_ports']==kw['unencrypted_ports']==[]
            assert kw['cpu']==(1,1) and kw['memory']==(1024,1024) and kw['timeout']==120 and 'gpu' not in kw
            self=cls();self.kw=kw;self.object_id='sb-nativefixture'+str(len(created));created.append(self)
            self.output=tmp_path/self.object_id;pr.mkdir(self.output);return self
        def exec(self,*args,**kwargs):
            assert kwargs['timeout']==90 and kwargs['workdir']=='/tmp'
            links=[]
            for name in ('/bin','/lib','/lib64'):
                p=Path(name)
                if p.exists():links+=['--symlink',os.readlink(p),name]
            cmd=['bwrap','--unshare-all','--die-with-parent','--new-session','--clearenv','--ro-bind','/usr','/usr',*links,
                '--dev','/dev','--proc','/proc','--bind',str(self.output),'/tmp']
            for alias,(volume,options) in self.kw['volumes'].items():
                selected=volume.path/options.get('sub_path','/').lstrip('/')
                readonly=options['read_only']
                if damage=='readonly-actually-writable':readonly=False
                if damage=='writable-actually-readonly':readonly=True
                target='/__modal/volumes/'+volume.object_id
                cmd+=['--ro-bind' if readonly else '--bind',str(selected),target,'--symlink',target,alias]
            r=subprocess.run([*cmd,'--chdir','/tmp',*args],capture_output=True,timeout=30)
            assert r.returncode==0,r.stderr.decode()
            return SimpleNamespace(wait=lambda:None,returncode=r.returncode)
    modal=SimpleNamespace(Volume=Volume,Sandbox=Sandbox,
        App=SimpleNamespace(lookup=lambda *a,**k:'synthetic-app'),Image=SimpleNamespace(from_id=lambda *a,**k:'synthetic-image'),
        stream_type=SimpleNamespace(StreamType=SimpleNamespace(DEVNULL='synthetic-devnull')))
    def terminate(ident):stopped.append(ident);return {'provider_id':ident,'terminated':True}
    provider=SimpleNamespace(config=config,modal=modal,client='synthetic',terminate=terminate,
        _read=lambda sb,path,limit:(sb.output/Path(path).name).read_bytes())
    if damage is None:
        v=retry.controls(provider,b,folder)
        assert retry.validate_controls(v,b)==v and len(created)==3 and len(volumes)==6
        assert (work/'native-mount-controls.json').exists()
    else:
        with pytest.raises(ValueError,match='CONTROL_FAILED'):retry.controls(provider,b,folder)
        assert not (work/'native-mount-controls.json').exists()
        assert len(created)==(1 if damage=='readonly-actually-writable' else 2)
    assert stopped==[s.object_id for s in created]
    assert all(not v.path.is_relative_to(Path('/data')) for v in volumes)


@pytest.mark.parametrize('damage',[None,'missing-admission','wrong-pin','wrong-source','missing-negative-control'])
def test_reuse_exact_native_controls_requires_admission_and_source(retry_ready,tmp_path,monkeypatch,damage):
    folder,b,config,_,_=retry_ready
    record=tmp_path/'qualified-root-fixture';pr.mkdir(record)
    monkeypatch.setattr(retry,'RECORD',record)
    # Labelled root provenance fixture; genuine control validation remains real.
    monkeypatch.setattr('orchestrator.manual_host_guard.trusted',lambda path:pr.check(path))
    work=folder.parent/'modal-executions'/retry.job(b);pr.mkdir(work,parents=True)
    if damage!='missing-admission':pr.write_bytes(work/'create-intent.json',dc.encoded({'binding_sha256':dc.sha(dc.encoded(b))}))
    value=control_proof(b)
    if damage=='wrong-source':value['controls_sha256']='f'*64
    if damage=='missing-negative-control':value['cases'].pop('writable_package')
    raw=dc.encoded(value);pr.write_bytes(record/'native-mount-controls.json',raw)
    monkeypatch.setattr(retry,'CONTROLS_SHA','0'*64 if damage=='wrong-pin' else dc.sha(raw))
    class Base:
        def create(self,*args):self.called=True;return {'synthetic_create':True}
    provider=retry.provider_factory(Base)();provider.called=False
    if damage is None:
        assert provider.create(config,b,folder)=={'synthetic_create':True}
        assert provider.called and (work/'native-mount-controls.json').read_bytes()==raw
        assert json.loads((work/'reused-native-controls.json').read_bytes())['additional_provider_calls']==0
    else:
        with pytest.raises((ValueError,OSError)):provider.create(config,b,folder)
        assert not provider.called and not (work/'native-mount-controls.json').exists()
    assert (record/'native-mount-controls.json').read_bytes()==raw


def test_installed_component_identity_is_consistent():
    from tools import item6_native_mount_service as service
    from tools import install_item6_native_mount as installer
    from orchestrator import diagnostics_mount_retry as retry
    assert service.CHANGE == retry.CHANGE
    assert service.ROOT == retry.ROOT
    assert service.RECORD == retry.RECORD
    assert installer.UNIT_PREFIX == 'research-' + retry.CHANGE + '-'


def test_installer_refuses_identity_drift_before_any_source_or_file_access(monkeypatch):
    from tools import item6_native_mount_service as service
    from tools import install_item6_native_mount as installer
    monkeypatch.setattr(installer.os, 'getuid', lambda: 0)
    monkeypatch.setattr(installer.os, 'geteuid', lambda: 0)
    monkeypatch.setattr(service, 'CHANGE', 'wrong-component')
    def forbidden(*args, **kwargs):
        raise AssertionError('must refuse before source, ledger or filesystem access')
    monkeypatch.setattr(installer, 'trusted', forbidden)
    with pytest.raises(ValueError, match='^MOUNT_INSTALL_COMPONENT_IDENTITY$'):
        installer.install('/unused/source', '0'*40, '/unused/review')
