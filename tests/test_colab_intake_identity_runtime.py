import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import colab_intake_identity_runtime as m


def test_unit_preserves_every_control_and_only_changes_entry():
    before=('ExecStart=/usr/bin/python3 -s -B '+str(m.BRANCH/'tools/preparation_branch_repair_runtime.py')+' advance --lane colab_preparation\n')
    safeguards='[Service]\nUser=partho\nGroup=partho\nNoNewPrivileges=true\nProtectSystem=strict\nPrivateTmp=true\nUMask=0077\nTimeoutStartSec=3700\n'
    raw=(safeguards+before).encode();changed=m.unit_bytes(raw)
    assert changed.decode().startswith(safeguards)
    assert str(m.ROOT/m.ENTRY).encode() in changed
    assert changed.replace(('ExecStart=/usr/bin/python3 -s -B '+str(m.ROOT/m.ENTRY)+' advance\n').encode(),before.encode())==raw
    with pytest.raises(ValueError):m.unit_bytes(raw+before.encode())
    with pytest.raises(ValueError):m.unit_bytes(raw.replace(b'colab_preparation',b'aggregate_analysis'))


@pytest.mark.parametrize('damage',['verdict','findings','scope','runtime','missing-source'])
def test_review_must_genuinely_approve_exact_scope_and_runtime(tmp_path,monkeypatch,damage):
    from orchestrator import autonomy_review
    runtime=tmp_path/'runtime.json';runtime.write_bytes(b'unchanged-config')
    manifest={'source_files':dict.fromkeys(m.REQUIRED,'b'*64)}
    approval={'verdict':'APPROVE','findings':[],'change_id':m.CHANGE,'runtime_sha256':m.sha(runtime.read_bytes())}
    if damage=='verdict':approval['verdict']='REVISE'
    elif damage=='findings':approval['findings']=[{'id':'unresolved'}]
    elif damage=='scope':approval['change_id']='other'
    elif damage=='runtime':approval['runtime_sha256']='0'*64
    else:manifest['source_files'].pop(m.RECOVERY)
    (tmp_path/'packet-manifest.json').write_text(json.dumps(manifest))
    monkeypatch.setattr(m,'RUNTIME',runtime);monkeypatch.setattr(m,'trusted',Path)
    monkeypatch.setattr(autonomy_review,'verify_result',lambda folder:approval)
    with pytest.raises(ValueError):m.reviewed(tmp_path)


def test_fixed_host_reuses_prior_start_state_checks_pulses_and_bounds(tmp_path,monkeypatch):
    root=tmp_path/'root';record=tmp_path/'record';record.mkdir();root.mkdir()
    monkeypatch.setattr(m,'ROOT',root);monkeypatch.setattr(m,'RECORD',record)
    monkeypatch.setattr(m,'os',NS(getuid=lambda:0));monkeypatch.setattr(m,'sys',NS(flags=NS(no_user_site=1),argv=['before']))
    monkeypatch.setattr(m,'trusted',Path);monkeypatch.setattr(m,'authority',lambda:{'report_sha256':'a'*64})
    monkeypatch.setattr(m,'original',lambda:None)
    installed={'units':{'/etc/systemd/system/'+m.UNIT:'u'},'files':{'one.py':'f'}}
    (record/'installed.json').write_text(json.dumps(installed))
    original_checks=object();events=[]
    h=NS(authority=lambda review:({'hashes':{'prior':'p'}},{}),hashes=lambda v:events.append(v),
         starting_state=original_checks,MAX_REFRESHES=62,MAX_SECONDS=3700)
    def run():
        assert h.starting_state is original_checks and (h.MAX_REFRESHES,h.MAX_SECONDS)==(62,3700)
        assert h.UNIT==m.UNIT and h.ENTRY==root/m.ENTRY
        assert h.OPERATION_ROOT==record/'operations'/('a'*64)
        assert m.sys.argv[1:] == ['pulse','--stage','author','--review',str(record/'review')]
        return {'status':'UNCHANGED_HOST_PULSE'}
    h.main=run
    old=NS(connect=lambda lane,transition:h)
    monkeypatch.setattr(m,'load',lambda name,path:old)
    assert m.host('pulse','a'*64)=={'status':'UNCHANGED_HOST_PULSE'}
    assert events[0]['hashes']=={'prior':'p',**installed['units'],str(root/'one.py'):'f'}
    assert m.sys.argv==['before']


def test_only_reviewed_intake_is_loaded_search_and_old_runtime_retained(tmp_path,monkeypatch):
    original=tmp_path/'original';root=tmp_path/'root'
    for p in [original/'orchestrator',root/'orchestrator']:p.mkdir(parents=True)
    (original/'orchestrator/scientific_intake.py').write_bytes(b'old intake')
    for p in [original,root]:(p/'orchestrator/scientific_search.py').write_bytes(b'same strict search')
    b={'original_intake_sha256':m.sha(b'old intake'),'original_search_sha256':m.sha(b'same strict search')}
    monkeypatch.setattr(m,'ORIGINAL',original);monkeypatch.setattr(m,'ROOT',root);monkeypatch.setattr(m,'trusted',Path)
    monkeypatch.setattr(m,'authority',lambda:None);prior=object()
    monkeypatch.setattr(m,'original',lambda:NS(connect=lambda:prior))
    monkeypatch.setattr(m,'recovery',lambda:NS(binding=lambda:b))
    seen=[];patched=NS()
    monkeypatch.setattr(m,'load',lambda name,path:(seen.append((name,path)) or patched))
    import orchestrator
    from orchestrator import scientific_intake
    monkeypatch.setattr(orchestrator,'scientific_intake',scientific_intake)
    assert m.connect() is prior
    assert seen==[('orchestrator.scientific_intake',root/'orchestrator/scientific_intake.py')]
    (root/'orchestrator/scientific_search.py').write_bytes(b'weakened')
    with pytest.raises(ValueError,match='SEARCH_GUARD_UNCHANGED'):m.connect()


@pytest.fixture
def install_fixture(tmp_path, monkeypatch):
    import hashlib
    source=tmp_path/'source';review=tmp_path/'review';review.mkdir();root=tmp_path/'installed';record=tmp_path/'record'
    branch_record=tmp_path/'branch-record';branch_record.mkdir()
    unit_dir=tmp_path/'units';unit_dir.mkdir();old_unit=unit_dir/m.OLD_UNIT
    before=('ExecStart=/usr/bin/python3 -s -B '+str(m.BRANCH/'tools/preparation_branch_repair_runtime.py')+' advance --lane colab_preparation\n').encode()
    old_unit.write_bytes(b'[Service]\nUser=partho\nProtectSystem=strict\n'+before)
    bodies={n:b'synthetic source' for n in m.REQUIRED};bodies[m.ENTRY]=Path(m.__file__).read_bytes()
    for n,raw in bodies.items():
        (source/n).parent.mkdir(parents=True,exist_ok=True);(source/n).write_bytes(raw)
    manifest={'source_files':{n:m.sha(raw) for n,raw in bodies.items()}}
    (review/'packet-manifest.json').write_text(json.dumps(manifest));(review/'report.md').write_text('synthetic independently approved report')
    # Only redirect the fixed system unit directory, never a caller-supplied root.
    RealPath=Path
    def path(value):return unit_dir if str(value)=='/etc/systemd/system' else RealPath(value)
    monkeypatch.setattr(m,'Path',path);monkeypatch.setattr(m,'ROOT',root);monkeypatch.setattr(m,'RECORD',record)
    monkeypatch.setattr(m,'BRANCH_RECORD',branch_record);monkeypatch.setattr(m,'trusted',lambda value:RealPath(value))
    monkeypatch.setattr(m,'os',NS(getuid=lambda:0));monkeypatch.setattr(m,'sys',NS(flags=NS(no_user_site=1)))
    approval={'source_sha':'a'*40,'report_sha256':'b'*64};monkeypatch.setattr(m,'reviewed',lambda folder:(approval,manifest))
    events=[];monkeypatch.setattr(m,'original',lambda:events.append('original-verified'))
    (branch_record/'installed.json').write_text(json.dumps({'units':{str(old_unit):m.sha(old_unit.read_bytes())}}))
    def put(path,raw):
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as out:out.write(raw)
    def relative(name):
        p=RealPath(name);assert not p.is_absolute() and '..' not in p.parts;return p
    helper=NS(relative=relative,OWNER_CHECK='readonly owner check',mkdir=lambda p:p.mkdir(),put=put)
    prior=NS(standalone_git=lambda p:events.append('standalone-verified'),verify_units=lambda u:events.append('units-verified'))
    monkeypatch.setattr(m,'load',lambda name,path:helper if 'existing_installer' in name else prior)
    controls={'source':'a'*40,'branch':'astra/manual-fixture','dirty':'','unit':'MainPID=0\nActiveState=inactive\nExecMainStatus=0\n','running':False,'verify_exit':0}
    def output(args,**kwargs):
        if args[:2]==['git','rev-parse']:return controls['source']+'\n'
        if args[:2]==['git','branch']:return controls['branch']+'\n'
        if args[:2]==['git','status']:return controls['dirty']
        if args[:2]==['systemctl','show']:return controls['unit']
        if args[0]=='runuser':return json.dumps({'status':'RUNNING' if controls['running'] else 'NO_RUNNING_CALL'})
        raise AssertionError(args)
    def run(args,**kwargs):
        events.append(args)
        if args[0]=='runuser':return NS(returncode=controls['verify_exit'],stdout=b'VERIFIED_HELD',stderr=b'')
        assert args==['systemctl','daemon-reload'];return NS(returncode=0)
    monkeypatch.setattr(m,'subprocess',NS(check_output=output,run=run))
    return NS(source=source,review=review,root=root,record=record,unit=old_unit,units=unit_dir,
              controls=controls,events=events,manifest=manifest)


def test_install_is_held_exact_source_and_verification_before_complete(install_fixture):
    f=install_fixture;before=f.unit.read_bytes();result=m.install(f.source,f.review)
    assert result['status']=='INSTALLED_HELD' and result['scientific_calls']==result['provider_calls']==0
    assert f.unit.read_bytes()==before
    installed=json.loads((f.record/'installed.json').read_bytes())
    assert installed['files']==f.manifest['source_files']
    for name,pin in installed['files'].items():assert m.sha((f.root/name).read_bytes())==pin
    assert 'original-verified' in f.events and 'standalone-verified' in f.events and 'units-verified' in f.events
    assert all(not isinstance(e,list) or e[:2] not in [['systemctl','start'],['systemctl','enable']] for e in f.events)
    with pytest.raises(ValueError,match='EXISTING_INSTALL_PRESERVED'):m.install(f.source,f.review)


@pytest.mark.parametrize('damage',['source','branch','dirty','source-bytes','unit-bytes','live-unit','running-call','existing-root','existing-record','existing-unit'])
def test_installer_refuses_before_writes(install_fixture,damage):
    f=install_fixture
    if damage in {'source','branch','dirty'}:f.controls[damage]='wrong'
    elif damage=='source-bytes':(f.source/m.RECOVERY).write_bytes(b'changed')
    elif damage=='unit-bytes':f.unit.write_bytes(f.unit.read_bytes()+b'changed')
    elif damage=='live-unit':f.controls['unit']='MainPID=123\nActiveState=active\nExecMainStatus=0\n'
    elif damage=='running-call':f.controls['running']=True
    elif damage=='existing-root':f.root.mkdir()
    elif damage=='existing-record':f.record.mkdir()
    else:(f.units/m.UNIT).write_bytes(b'earlier attempt')
    before={str(p):p.read_bytes() for folder in [f.root,f.record,f.units] if folder.exists() for p in folder.rglob('*') if p.is_file()}
    with pytest.raises(ValueError):m.install(f.source,f.review)
    after={str(p):p.read_bytes() for folder in [f.root,f.record,f.units] if folder.exists() for p in folder.rglob('*') if p.is_file()}
    assert before==after and not (f.record/'COMPLETE.json').exists()


def test_postinstall_failure_remains_partial_and_refuses_retry(install_fixture):
    f=install_fixture;f.controls['verify_exit']=1
    with pytest.raises(ValueError,match='SERVICE_VERIFY_FAILED'):m.install(f.source,f.review)
    assert (f.record/'INSTALL_INTENT.json').exists() and (f.record/'VERIFY.stdout').exists()
    assert not (f.record/'COMPLETE.json').exists()
    with pytest.raises(ValueError,match='EXISTING_INSTALL_PRESERVED'):m.install(f.source,f.review)
