import json
import os
from pathlib import Path
from types import SimpleNamespace
import pytest
from tools import preparation_branch_repair_runtime as runtime
from tools import preparation_branch_repair_host as host
from tools import install_preparation_branch_repair as installer


def old_unit(lane):
    return ("[Unit]\nDescription=Original preparation\n[Service]\n"
        "User=partho\nGroup=partho\nTimeoutStartSec=3600\nRestart=no\nKillMode=control-group\n"
        "ProtectSystem=strict\nNoNewPrivileges=yes\nPrivateTmp=yes\n"
        "ExecStartPre=/unchanged/host before\nExecStopPost=/unchanged/host after\n"
        "Environment=PYTHONPATH="+str(installer.ORIGINAL_ROOT)+":/original/base\n"
        "ReadWritePaths=/original/state /existing/lane\n"
        "ExecStart=/usr/bin/python3 -s -B "+str(installer.ORIGINAL_ROOT/'tools/preparation_scientific_runtime.py')+
        " advance --scope "+str(installer.ORIGINAL_RECORD/'preparation-interleaving.json')+
        " --review-report "+str(installer.ORIGINAL_RECORD/'review/report.md')+" --lane "+lane+"\n").encode()

@pytest.mark.parametrize('lane',installer.LANES)
def test_unit_only_entry_changes(lane):
    raw=old_unit(lane);new=installer.unit_bytes(raw,lane)
    before=raw.splitlines();after=new.splitlines()
    changes=[(a,b) for a,b in zip(before,after) if a!=b]
    assert len(before)==len(after) and len(changes)==1
    assert changes[0][0].startswith(b'ExecStart=') and b'preparation_branch_repair_runtime.py' in changes[0][1]
    assert b'PYTHONPATH='+str(installer.ORIGINAL_ROOT).encode() in new

@pytest.mark.parametrize('mutation',[lambda x:x.replace(b'--lane aggregate_analysis',b'--lane other'),lambda x:x+b'ExecStart=/wrong\n',lambda x:x.replace(b' -s -B ',b' -B ')])
def test_unit_rejects_wrong_or_duplicate_entry(mutation):
    with pytest.raises(ValueError,match='EXACT_PRIOR_ENTRY'):
        installer.unit_bytes(mutation(old_unit('aggregate_analysis')),'aggregate_analysis')

def test_unit_rejects_unknown_lane():
    with pytest.raises(ValueError,match='NAMED_LANE'):installer.unit_bytes(old_unit('aggregate_analysis'),'other')

@pytest.mark.parametrize('name',['/absolute','../escape','x/../escape','a//b',''])
def test_installer_refuses_unsafe_relative_paths(name):
    with pytest.raises(ValueError,match='RELATIVE_PATH'):installer.relative(name)

@pytest.mark.parametrize('action,lane',[('verify',None),('init','colab_preparation'),('advance','aggregate_analysis')])
def test_delegate_retains_original_scope_report(action,lane,monkeypatch):
    calls=[];monkeypatch.setattr(runtime.os,'getuid',lambda:1003);monkeypatch.setattr(runtime.os,'getgid',lambda:1003)
    monkeypatch.setattr(runtime,'connect',lambda:SimpleNamespace(main=lambda args:calls.append(args) or {'ok':True}))
    args=[action]+(['--lane',lane] if lane else [])
    assert runtime.main(args)=={'ok':True}
    expected=[action,'--scope',str(runtime.ORIGINAL_RECORD/'preparation-interleaving.json'),'--review-report',str(runtime.ORIGINAL_RECORD/'review/report.md')]
    if lane:expected+=['--lane',lane]
    assert calls==[expected]

@pytest.mark.parametrize('uid,gid',[(0,0),(1003,0),(0,1003)])
def test_runtime_refuses_wrong_identity(uid,gid,monkeypatch):
    monkeypatch.setattr(runtime.os,'getuid',lambda:uid);monkeypatch.setattr(runtime.os,'getgid',lambda:gid)
    monkeypatch.setattr(runtime,'connect',lambda:pytest.fail('must not connect'))
    with pytest.raises(ValueError,match='SERVICE_ACCOUNT'):runtime.main(['verify'])

@pytest.mark.parametrize('args',[['verify','--lane','aggregate_analysis'],['advance'],['init']])
def test_runtime_refuses_invalid_action_lane(args,monkeypatch):
    monkeypatch.setattr(runtime.os,'getuid',lambda:1003);monkeypatch.setattr(runtime.os,'getgid',lambda:1003)
    monkeypatch.setattr(runtime,'connect',lambda:pytest.fail('must not connect'))
    with pytest.raises(ValueError,match='ACTION_LANE'):runtime.main(args)

def test_connect_installs_exact_module_and_driver_hook(monkeypatch):
    import orchestrator
    from orchestrator import analysis_driver
    events=[];proof=object();pi=SimpleNamespace(configure_premodel=lambda p:events.append(('proof',p)),install_driver_hook=lambda m,p:events.append(('driver',m,p)))
    original=SimpleNamespace(ROOT=runtime.ORIGINAL_ROOT,RECORD=runtime.ORIGINAL_RECORD)
    def load(name,path):
        events.append(('load',name,str(path)))
        if name=='_reviewed_preparation_premodel_recovery':return SimpleNamespace(load_verified_proof=lambda review:events.append(('review',review)) or proof)
        if name=='orchestrator.preparation_interleaving':return pi
        if name=='_original_preparation_scientific_runtime':return original
        pytest.fail(name)
    monkeypatch.setattr(runtime,'authority',lambda:({}, {}, {}));monkeypatch.setattr(runtime,'load',load)
    monkeypatch.setattr(orchestrator,'__file__',str(runtime.ORIGINAL_ROOT/'orchestrator/__init__.py'))
    previous=getattr(orchestrator,'preparation_interleaving',None)
    try:
        assert runtime.connect() is original
        assert orchestrator.preparation_interleaving is pi
        assert ('review',runtime.RECORD/'review') in events
        assert ('driver',analysis_driver,proof) in events
        assert events.index(('proof',proof))<next(i for i,e in enumerate(events) if e[:2]==('load','_original_preparation_scientific_runtime'))
    finally:orchestrator.preparation_interleaving=previous

def test_connect_refuses_wrong_original_import_root(monkeypatch):
    import orchestrator
    monkeypatch.setattr(runtime,'authority',lambda:({}, {}, {}));monkeypatch.setattr(orchestrator,'__file__','/unexpected/orchestrator/__init__.py')
    monkeypatch.setattr(runtime,'load',lambda *a:pytest.fail('must not load'))
    with pytest.raises(ValueError,match='ORIGINAL_IMPORT_ROOT'):runtime.connect()

def test_readonly_owner_check_does_not_mutate():
    assert 'mode=ro' in installer.OWNER_CHECK and "os.getuid()==os.getgid()==1003" in installer.OWNER_CHECK
    assert 'UPDATE ' not in installer.OWNER_CHECK and 'DELETE ' not in installer.OWNER_CHECK


def test_host_retains_original_state_and_pulse_checks(monkeypatch,tmp_path):
    events=[];key='aggregate_analysis';transition='d'*64
    root=tmp_path/'root';record=tmp_path/'record';record.mkdir()
    approval={'source_sha':'a'*40,'report_sha256':'b'*64}
    complete={'status':'INSTALLED_HELD','source':'a'*40,'scientific_calls':0,'provider_calls':0}
    (record/'COMPLETE.json').write_text(json.dumps(complete))
    unit='research-'+runtime.CHANGE+'-'+key+'.service'
    receipt={'units':{'/etc/systemd/system/'+unit:'f'*64},'files':{'tools/preparation_branch_repair_host.py':'e'*64}}
    original_start=object();original_pulse=object();original_stop=object()
    frozen={'hashes':{'old-unit':'old-pin'}}
    delegated=SimpleNamespace(authority=lambda review:(frozen,{'old':True}),hashes=lambda value:events.append(value.copy()),starting_state=original_start,pulse=original_pulse,safe_stop=original_stop)
    prior=SimpleNamespace(connect=lambda lane,t:events.append((lane,t)) or delegated)
    rt=SimpleNamespace(require=runtime.require,authority=lambda:(approval,{},receipt),trusted=Path,ROOT=root,RECORD=record,ORIGINAL_ROOT=tmp_path/'original',LANES=runtime.LANES,CHANGE=runtime.CHANGE,load=lambda name,path:prior)
    monkeypatch.setattr(host,'runtime',lambda:rt);monkeypatch.setattr(host,'__file__',str(root/'tools/preparation_branch_repair_host.py'))
    monkeypatch.setattr(host.os,'getuid',lambda:0)
    result=host.connect(key,transition)
    assert result is delegated and result.starting_state is original_start and result.pulse is original_pulse and result.safe_stop is original_stop
    assert result.UNIT==unit and result.OPERATION_ROOT==record/'operations'/key/transition
    assert result.authority(None)==(frozen,approval)
    assert frozen['hashes']['old-unit']=='old-pin'
    assert frozen['hashes']['/etc/systemd/system/'+unit]=='f'*64
    assert events[0]==(key,transition)
    # Unit identity must be installed and hash-bound, not a caller-selected unit.
    receipt['units'].clear()
    with pytest.raises(ValueError,match='EXACT_NEW_UNIT'):host.connect(key,transition)

def test_host_refuses_unverified_install_before_original_connect(monkeypatch,tmp_path):
    record=tmp_path/'record';record.mkdir();(record/'COMPLETE.json').write_text('{}')
    root=tmp_path/'root'
    rt=SimpleNamespace(require=runtime.require,authority=lambda:({'source_sha':'a'*40},{},{}),trusted=Path,ROOT=root,RECORD=record,LANES=runtime.LANES,load=lambda *a:pytest.fail('must not connect'))
    monkeypatch.setattr(host,'runtime',lambda:rt);monkeypatch.setattr(host,'__file__',str(root/'tools/preparation_branch_repair_host.py'));monkeypatch.setattr(host.os,'getuid',lambda:0)
    with pytest.raises(ValueError,match='SERVICE_VERIFICATION_REQUIRED'):host.connect('aggregate_analysis','d'*64)


def test_host_loader_refuses_wrong_location_before_import():
    with pytest.raises(ValueError,match='HOST_EXECUTED_PATH'):host.runtime()
