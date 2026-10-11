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
    approval={'verdict':'APPROVE','findings':[],'change_id':m.REVIEW_CHANGE,'runtime_sha256':m.sha(runtime.read_bytes())}
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
    monkeypatch.setattr(m,'network_predecessor',lambda *a:{'transition':'a'*64})
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


@pytest.mark.parametrize('damage',[None,'prior-source','prior-review','document','sequence-path','predecessor-refusal'])
def test_reviewed_recovery_composes_existing_checks_and_exact_new_components(tmp_path,monkeypatch,damage):
    import orchestrator
    from orchestrator import analysis_driver,manual_driver
    root=tmp_path/'root';root.mkdir();doc=root/'synthetic.json';raw=b'{"synthetic":true}';doc.write_bytes(raw)
    monkeypatch.setattr(m,'ROOT',root);monkeypatch.setattr(m,'trusted',Path)
    seen=[];events=[];context=NS();approval={'report_sha256':'a'*64}
    monkeypatch.setattr(m,'authority',lambda held=True:(events.append(('authority',held)) or approval))
    approved={'source_sha':'c4280f2723e0adcf3c7cee51a435fc775528b393','report_sha256':'f5118bf6ae3c80cee8bf719adb4059b1f12637208c5a601a6a3fa6b6fab1d0b5'}
    if damage=='prior-source':approved['source_sha']='wrong'
    if damage=='prior-review':approved['report_sha256']='wrong'
    branch=NS(load=lambda name,path:(seen.append(('branch-load',name,path)) or context))
    prior=NS()
    previous=NS(authority=lambda:approved,original=lambda:branch)
    def prior_connect():
        events.append('prior-connect')
        if damage=='predecessor-refusal':raise ValueError('original search guard')
        route=previous.original()
        assert route.load('orchestrator.preparation_interleaving',(m.BRANCH if damage!='sequence-path' else tmp_path)/'orchestrator/preparation_interleaving.py') is context
        route.load('unchanged',tmp_path/'original.py')
        return prior
    previous.connect=prior_connect
    repair=NS(TURN_DOCUMENT=doc.name,TURN_DOCUMENT_SHA=m.sha(raw),install_hook=lambda *args:events.append(('hook',args)))
    monkeypatch.setattr(m,'colab_recovery_review',lambda:'original-recovery-review')
    if damage=='document':doc.write_bytes(b'changed')
    def load(name,path):
        seen.append((name,path))
        if name=='_colab_reader_previous_runtime':return previous
        if name=='orchestrator.manual_context':return context
        if name=='orchestrator.colab_reader_recovery':return repair
        if name=='orchestrator.colab_author_terminal':return NS(connect_sequence=lambda pi:events.append('terminal-sequence'))
        raise AssertionError(name)
    monkeypatch.setattr(m,'load',load)
    # Restore the shared module attributes after the composition test.
    for module in [orchestrator,analysis_driver,manual_driver]:monkeypatch.setattr(module,'manual_context',module.manual_context)
    if damage:
        with pytest.raises(ValueError):m.connect('verify')
        assert not any(isinstance(e,tuple) and e[0]=='hook' for e in events)
    else:
        assert m.connect('verify') is prior
        assert seen[0]==('_colab_reader_previous_runtime',m.READER_PREVIOUS/m.ENTRY)
        assert ('branch-load','orchestrator.preparation_interleaving',root/'orchestrator/preparation_interleaving.py') in seen
        assert ('branch-load','unchanged',tmp_path/'original.py') in seen
        assert all(module.manual_context is context for module in [orchestrator,analysis_driver,manual_driver])
        assert events[-1]=='terminal-sequence'
        assert events[-2]==('hook',(analysis_driver,{'synthetic':True},'original-recovery-review','verify'))
        assert events.count(('authority',False))==2 and 'prior-connect' in events


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
    monkeypatch.setattr(m,'network_predecessor',lambda raw:events.append('network-predecessor-verified'))
    (branch_record/'installed.json').write_text(json.dumps({'units':{str(old_unit):m.sha(old_unit.read_bytes())}}))
    def put(path,raw):
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as out:out.write(raw)
    def relative(name):
        p=RealPath(name);assert not p.is_absolute() and '..' not in p.parts;return p
    helper=NS(relative=relative,OWNER_CHECK='readonly owner check',mkdir=lambda p:p.mkdir(),put=put)
    prior=NS(standalone_git=lambda p:events.append('standalone-verified'),verify_units=lambda u:events.append('units-verified'))
    native_unit='research-preserved-native-review.service'
    (unit_dir/native_unit).write_bytes(('User=partho\nProtectSystem=strict\nExecStart=/usr/bin/python3 -s -B '+str(m.NATIVE_PREVIOUS/'tools/item4_diagnostic_review_runtime.py')+' run\n').encode())
    retained=NS(authority=lambda:{'source_sha':'1f2243448ca452abcad92ca355bead042cc731d2',
        'report_sha256':'c27eaa20e857449d1d054621848fd63084dc811a092f98128e63c9a99797ba93'},
        REVIEW_UNIT=native_unit,CPU_UNIT='research-preserved-native-cpu.service')
    monkeypatch.setattr(m,'preserved_native',lambda:(retained,retained.authority()))
    monkeypatch.setattr(m,'colab_recovery_review',lambda:m.COLAB_RECOVERY_REVIEW)
    monkeypatch.setattr(m,'load',lambda name,path:helper if 'existing_installer' in name else prior)
    controls={'source':'a'*40,'branch':'astra/manual-fixture','dirty':'','unit':'MainPID=0\nActiveState=inactive\nExecMainStatus=0\n','running':False,'verify_exit':0,'native_verify_exit':0}
    def output(args,**kwargs):
        if args[:2]==['git','rev-parse']:return controls['source']+'\n'
        if args[:2]==['git','branch']:return controls['branch']+'\n'
        if args[:2]==['git','status']:return controls['dirty']
        if args[:2]==['systemctl','show']:return controls['unit']
        if args[0]=='runuser':return json.dumps({'status':'RUNNING' if controls['running'] else 'NO_RUNNING_CALL'})
        raise AssertionError(args)
    def run(args,**kwargs):
        events.append(args)
        if args[0]=='runuser':return NS(returncode=controls['native_verify_exit'] if 'item4_diagnostic_review_runtime.py' in args[-2] else controls['verify_exit'],stdout=b'VERIFIED_HELD',stderr=b'')
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
    assert set(installed['units'])=={str(f.units/m.UNIT),str(f.units/m.NATIVE_UNIT)}
    assert (f.record/'NATIVE_VERIFY.stdout').exists()
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


@pytest.mark.parametrize('damage',[None,'source','report','change','active','pid'])
def test_preserved_recovery_keeps_original_approval_and_refuses_live_writer(monkeypatch,damage):
    approved={'source_sha':m.PREVIOUS_SOURCE,'report_sha256':m.PREVIOUS_REVIEW,
              'change_id':'colab-intake-identity-20261011'}
    if damage in {'source','report','change'}:
        approved[{'source':'source_sha','report':'report_sha256','change':'change_id'}[damage]]='wrong'
    recovery=object();seen=[]
    previous=NS(authority=lambda:approved,recovery=lambda:recovery)
    monkeypatch.setattr(m,'load',lambda name,path:(seen.append(path) or previous))
    unit='MainPID='+('123' if damage=='pid' else '0')+'\nActiveState='+('active' if damage=='active' else 'failed')+'\n'
    monkeypatch.setattr(m,'subprocess',NS(check_output=lambda *a,**k:unit))
    if damage is None:
        assert m.recovery() is recovery
        assert seen==[m.PREVIOUS_ROOT/m.ENTRY]
    else:
        with pytest.raises(ValueError,match='PREVIOUS_'):m.recovery()


@pytest.mark.parametrize('result',[{'status':'VERIFIED_HELD','model_calls':0,'provider_calls':0},{'status':'wrong'},{'status':'VERIFIED_HELD','model_calls':1,'provider_calls':0}])
def test_verify_exercises_real_connection_before_held_install_complete(monkeypatch,result):
    events=[]
    monkeypatch.setattr(m,'os',NS(getuid=lambda:1003,getgid=lambda:1003))
    monkeypatch.setattr(m,'sys',NS(path=[]))
    prior=NS(RECORD=Path('/synthetic'),main=lambda argv:(events.append(argv) or result))
    monkeypatch.setattr(m,'connect',lambda action:(events.append(action) or prior))
    if result=={'status':'VERIFIED_HELD','model_calls':0,'provider_calls':0}:
        assert m.main(['verify'])=={'status':'VERIFIED_HELD','scientific_calls':0,'provider_calls':0}
    else:
        with pytest.raises(ValueError,match='ACTUAL_VERIFY_REQUIRED'):m.main(['verify'])
    assert events==['verify',['advance','--scope','/synthetic/preparation-interleaving.json','--review-report','/synthetic/review/report.md','--lane','colab_preparation']]


def test_successor_cannot_replay_completed_preservation():
    with pytest.raises(SystemExit):m.main(['resume'])


@pytest.mark.parametrize('damage',[None,'old-change','missing-scope'])
def test_transport_recovery_requires_explicit_scope_and_exact_approval(tmp_path,monkeypatch,damage):
    from orchestrator import autonomy_review
    runtime=tmp_path/'runtime.json';runtime.write_bytes(b'unchanged')
    manifest={'source_files':dict.fromkeys(m.REQUIRED,'b'*64)}
    approval={'verdict':'APPROVE','findings':[],'change_id':m.REVIEW_CHANGE,
              'runtime_sha256':m.sha(runtime.read_bytes())}
    if damage=='old-change':approval['change_id']=m.CHANGE
    if damage=='missing-scope':manifest['source_files'].pop(m.REVIEW_SCOPE)
    (tmp_path/'packet-manifest.json').write_text(json.dumps(manifest))
    monkeypatch.setattr(m,'RUNTIME',runtime);monkeypatch.setattr(m,'trusted',Path)
    monkeypatch.setattr(autonomy_review,'verify_result',lambda folder:approval)
    if damage is None:assert m.reviewed(tmp_path)==(approval,manifest)
    else:
        with pytest.raises(ValueError):m.reviewed(tmp_path)


def test_native_postcheck_failure_keeps_originals_and_never_marks_complete(install_fixture):
    f=install_fixture;before=f.unit.read_bytes();f.controls['native_verify_exit']=1
    with pytest.raises(ValueError,match='NATIVE_SERVICE_VERIFY_FAILED'):m.install(f.source,f.review)
    assert f.unit.read_bytes()==before and (f.record/'VERIFY.stdout').exists()
    assert (f.record/'NATIVE_VERIFY.stdout').exists() and not (f.record/'COMPLETE.json').exists()
    with pytest.raises(ValueError,match='EXISTING_INSTALL_PRESERVED'):m.install(f.source,f.review)


@pytest.mark.parametrize('uid',[0,1003])
@pytest.mark.parametrize('fault',[None,'source','result','process','uid','gid'])
def test_native_config_check_uses_preserved_bootstrap_in_isolated_service_context(tmp_path,monkeypatch,uid,fault):
    approved={'source_sha':'1f2243448ca452abcad92ca355bead042cc731d2','report_sha256':'c27eaa20e857449d1d054621848fd63084dc811a092f98128e63c9a99797ba93'}
    if fault=='source':approved['source_sha']='changed'
    prior=NS(reviewed_source=lambda:(approved,{'files':{'tools/item4_diagnostic_native_runtime.py':'a'*64}}))
    monkeypatch.setattr(m,'load',lambda name,path:prior)
    monkeypatch.setattr(m,'os',NS(getuid=lambda:1004 if fault=='uid' else uid,getgid=lambda:1004 if fault=='gid' else 1003))
    monkeypatch.setattr(m,'sys',NS(flags=NS(no_user_site=1)))
    seen=[]
    def output(argv,**kwargs):
        seen.append(argv)
        assert kwargs=={'text':True,'timeout':120}
        assert ('runuser' in argv)==(uid==0)
        assert 'RESEARCH_MANUAL_RUNTIME_CONFIG='+str(m.RUNTIME) in argv
        assert argv[-2:]==[str(m.NATIVE_PREVIOUS/'tools/item4_diagnostic_native_runtime.py'),'a'*64]
        assert 'm.bootstrap();print(json.dumps(m.authority()))' in argv[argv.index('-c')+1]
        assert '-s' in argv and '-B' in argv
        if fault=='process':raise ValueError('original native check refused')
        return json.dumps({**approved,'source_sha':'wrong'} if fault=='result' else approved)
    monkeypatch.setattr(m,'subprocess',NS(check_output=output))
    if fault and not (fault=='gid' and uid==0):
        with pytest.raises(ValueError):m.preserved_native()
    else:assert m.preserved_native()==(prior,approved)
    if fault in {'source','uid'} or fault=='gid' and uid!=0:assert not seen


@pytest.mark.parametrize('fault',[None,'source','report','change','original-refusal'])
def test_continuation_keeps_exact_predecessor_grant_approval(monkeypatch,fault):
    approval={'source_sha':m.COLAB_RECOVERY_SOURCE,'report_sha256':m.COLAB_RECOVERY_REVIEW,
              'change_id':'native-authority-reader-recovery-20261011'}
    if fault in {'source','report','change'}:
        approval[{'source':'source_sha','report':'report_sha256','change':'change_id'}[fault]]='changed'
    def original():
        if fault=='original-refusal':raise ValueError('original installed authority refused')
        return approval
    def load(name,path):
        assert path==m.CONTINUATION_PREVIOUS/m.ENTRY
        return NS(authority=original)
    monkeypatch.setattr(m,'load',load)
    if fault:
        with pytest.raises(ValueError):m.colab_recovery_review()
    else:assert m.colab_recovery_review()==m.COLAB_RECOVERY_REVIEW


@pytest.mark.parametrize('unit',['research-review-continuation-20261011.service','research-review-continuation-20261011-native-review.service'])
def test_new_install_refuses_either_previous_continuation_writer(install_fixture,monkeypatch,unit):
    f=install_fixture;original=m.subprocess.check_output
    def output(args,**kwargs):
        if args[:3]==['systemctl','show',unit]:return 'MainPID=7\nActiveState=activating\n'
        return original(args,**kwargs)
    monkeypatch.setattr(m.subprocess,'check_output',output)
    with pytest.raises(ValueError):m.install(f.source,f.review)
    assert not f.root.exists() and not f.record.exists()
