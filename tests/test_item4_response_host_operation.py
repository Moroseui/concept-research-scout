import importlib.util
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import pytest

@pytest.fixture
def op(monkeypatch,tmp_path):
    p=Path(__file__).parents[1]/'tools/item4_response_host_operation.py'
    spec=importlib.util.spec_from_file_location('_host_operation_test',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    root=tmp_path/'operation';root.mkdir();monkeypatch.setattr(m,'RECORD',root);monkeypatch.setattr(m,'STAGE','reviewer')
    receipt=tmp_path/'proof.json';receipt.write_text('{}');monkeypatch.setattr(m,'RECEIPT',receipt)
    # Disposable filesystem boundary only; no root/systemd/policy command runs.
    monkeypatch.setattr(m,'trusted',lambda p:Path(p));monkeypatch.setattr(m,'boot',lambda:'test-boot')
    monkeypatch.setattr(m.os,'kill',lambda pid,sig:None);monkeypatch.setattr(m.time,'monotonic',lambda:1000.)
    monkeypatch.setattr(m.time,'time',lambda:2000.)
    run={'stage':'reviewer','invocation':'a'*32,'started_monotonic_us':900000000,'boot_id':'test-boot','review_sha256':'b'*64,'source_sha':'c'*40}
    approval={'report_sha256':'b'*64,'source_sha':'c'*40};frozen={'hashes':{str(m.RUNTIME):'d'*64}}
    value={'ActiveState':'activating','MainPID':'123','InvocationID':run['invocation'],'ControlGroup':'/system.slice/'+m.UNIT,'ExecMainStatus':'0','ExecMainStartTimestampMonotonic':'900000000'}
    calls=[]
    def cmd(args,**kwargs):
        calls.append((args,kwargs))
        if str(m.HOOK) in args:
            assert kwargs['env']=={'PATH':'/usr/bin:/bin','PYTHONPATH':str(m.BASE),'INVOCATION_ID':run['invocation']}
            m.RECEIPT.write_text(json.dumps({'status':'PASS','invocation':run['invocation'],'runtime_sha256':'d'*64,'lane':str(m.LANE),'boot_id':'test-boot','time':2000.}))
        return ''
    monkeypatch.setattr(m,'command',cmd);monkeypatch.setattr(m,'unit',lambda:dict(value));monkeypatch.setattr(m,'hashes',lambda f:None)
    m.put(root/'RUN.json',run)
    return SimpleNamespace(m=m,run=run,approval=approval,frozen=frozen,value=value,calls=calls,monkeypatch=monkeypatch)


def test_pulse_uses_actual_bound_invocation_and_minimal_environment(op):
    assert op.m.pulse(op.frozen,op.approval)=={'status':'REFRESHED','number':1}
    assert len(op.calls)==1 and str(op.m.HOOK) in op.calls[0][0]
    record=op.m.RECORD/'refresh-001'
    assert json.loads((record/'previous-proof.json').read_bytes())=={}
    assert json.loads((record/'COMPLETE.json').read_bytes())['status']=='GENUINE_POLICY_RECHECK'
    assert (record/'fresh-proof.json').stat().st_mode&0o777==0o600

@pytest.mark.parametrize('field,replacement',[('InvocationID','e'*32),('MainPID','0'),('ControlGroup','/other.slice/x'),('ExecMainStartTimestampMonotonic','800000000'),('ActiveState','active')])
def test_wrong_identity_never_refreshes(op,field,replacement):
    op.value[field]=replacement
    with pytest.raises(ValueError):op.m.pulse(op.frozen,op.approval)
    assert not any(str(op.m.HOOK) in a for a,k in op.calls)
    if field=='InvocationID':assert not op.calls  # Never stop a replacement invocation.

@pytest.mark.parametrize('kind',['age','boot','pid'])
def test_stale_boot_and_dead_process_refused(op,kind):
    if kind=='age':op.monkeypatch.setattr(op.m.time,'monotonic',lambda:4600.)
    if kind=='boot':op.monkeypatch.setattr(op.m,'boot',lambda:'other-boot')
    if kind=='pid':op.monkeypatch.setattr(op.m.os,'kill',lambda *args:(_ for _ in ()).throw(ProcessLookupError()))
    with pytest.raises((ValueError,ProcessLookupError)):op.m.pulse(op.frozen,op.approval)
    assert not any(str(op.m.HOOK) in a for a,k in op.calls)
    assert op.calls[-1][0]==['systemctl','stop',op.m.UNIT]


def test_policy_refusal_preserved_and_exact_invocation_stopped(op):
    ordinary=op.m.command
    def cmd(args,**kwargs):
        if str(op.m.HOOK) in args:raise subprocess.CalledProcessError(1,args,output='',stderr='HOST_POLICY_DRIFT')
        return ordinary(args,**kwargs)
    op.monkeypatch.setattr(op.m,'command',cmd)
    with pytest.raises(subprocess.CalledProcessError):op.m.pulse(op.frozen,op.approval)
    assert 'HOST_POLICY_DRIFT' in (op.m.RECORD/'refresh-001/REFUSAL.json').read_text()
    assert not (op.m.RECORD/'refresh-001/COMPLETE.json').exists()
    assert op.calls==[(['systemctl','stop',op.m.UNIT],{})]


def test_wrong_proof_refused_and_stopped(op):
    ordinary=op.m.command
    def cmd(args,**kwargs):
        result=ordinary(args,**kwargs)
        if str(op.m.HOOK) in args:
            v=json.loads(op.m.RECEIPT.read_bytes());v['invocation']='f'*32;op.m.RECEIPT.write_text(json.dumps(v))
        return result
    op.monkeypatch.setattr(op.m,'command',cmd)
    with pytest.raises(ValueError,match='FRESH_PROOF_BINDING'):op.m.pulse(op.frozen,op.approval)
    assert op.calls[-1][0]==['systemctl','stop',op.m.UNIT]

@pytest.mark.parametrize('complete,count',[(False,1),(True,62)])
def test_uncertain_refresh_or_count_limit_stops_without_refresh(op,complete,count):
    for i in range(count):
        p=op.m.RECORD/('refresh-%03d'%(i+1));p.mkdir()
        if complete:(p/'COMPLETE.json').write_text('{}')
    with pytest.raises(ValueError,match='REFRESH_BOUND_OR_UNCERTAIN'):op.m.pulse(op.frozen,op.approval)
    assert op.calls==[(['systemctl','stop',op.m.UNIT],{})]


def test_source_drift_fails_closed(op,tmp_path):
    p=tmp_path/'source';p.write_text('changed')
    # Restore real source hash verification, with only synthetic path trust.
    def check(f):
        for name,pin in f['hashes'].items():op.m.require(op.m.sha(op.m.trusted(name).read_bytes())==pin,'HOST_SOURCE_CHANGED')
    op.monkeypatch.setattr(op.m,'hashes',check)
    with pytest.raises(ValueError,match='HOST_SOURCE_CHANGED'):op.m.pulse({'hashes':{str(p):'0'*64}},op.approval)
    assert op.calls==[(['systemctl','stop',op.m.UNIT],{})]


def test_terminal_invocation_receives_no_refresh(op):
    op.value.update(ActiveState='inactive',MainPID='0',ControlGroup='',InvocationID='')
    assert op.m.pulse(op.frozen,op.approval)['status']=='TERMINAL_NO_REFRESH'
    assert not op.calls


def test_start_captures_actual_identity_and_duplicate_is_refused(op):
    (op.m.RECORD/'RUN.json').unlink()
    failed={**op.value,'ActiveState':'inactive','MainPID':'0','ControlGroup':'','InvocationID':'','ExecMainStatus':'0'}
    states=[failed,op.value]
    op.monkeypatch.setattr(op.m,'unit',lambda:states.pop(0) if states else failed)
    op.monkeypatch.setattr(op.m,'starting_state',lambda f,a:{'local_calls':25})
    assert op.m.start(op.frozen,op.approval)['run']['invocation']=='a'*32
    assert op.calls==[(['systemctl','start','--no-block',op.m.UNIT],{})]
    with pytest.raises(FileExistsError):op.m.start(op.frozen,op.approval)
    assert len(op.calls)==1

@pytest.mark.parametrize('bad',['verdict','change','source','document'])
def test_authority_refuses_unapproved_or_changed_bytes(op,tmp_path,bad):
    m=op.m;op.monkeypatch.setattr(m.os,'getuid',lambda:0)
    engine=tmp_path/'engine.json';engine.write_text('{"files":{}}');op.monkeypatch.setattr(m,'ENGINE_RECEIPT',engine);op.monkeypatch.setattr(m,'ENGINE_PIN',m.sha(engine.read_bytes()))
    from orchestrator import autonomy_review
    approval={'verdict':'APPROVE','change_id':m.REVIEW_CHANGE,'source_sha':'c'*40}
    if bad=='verdict':approval['verdict']='REVISE'
    if bad=='change':approval['change_id']='unrelated'
    op.monkeypatch.setattr(autonomy_review,'verify_result',lambda p:approval)
    root=Path(m.__file__).resolve().parents[1]
    pins={m.FILE:m.sha(Path(m.__file__).read_bytes()),m.DOCUMENT:m.sha((root/m.DOCUMENT).read_bytes())}
    if bad=='source':pins[m.FILE]='0'*64
    if bad=='document':pins[m.DOCUMENT]='0'*64
    review=tmp_path/'review';review.mkdir();(review/'packet-manifest.json').write_text(json.dumps({'source_sha':'c'*40,'source_files':pins}))
    with pytest.raises(ValueError):m.authority(review)
    assert not op.calls


def test_new_completed_invocation_is_not_misattributed(op):
    op.value.update(ActiveState='inactive',MainPID='0',ControlGroup='',InvocationID='',ExecMainStartTimestampMonotonic='950000000')
    with pytest.raises(ValueError,match='INVOCATION_CHANGED'):op.m.pulse(op.frozen,op.approval)
    assert not op.calls


def test_wrong_bound_approval_stops_original_without_refresh(op):
    with pytest.raises(ValueError,match='RUN_AUTHORITY'):op.m.pulse(op.frozen,{'source_sha':'c'*40,'report_sha256':'f'*64})
    assert op.calls==[(['systemctl','stop',op.m.UNIT],{})]


def test_author_record_cannot_refresh_reviewer_stage(op):
    op.monkeypatch.setattr(op.m,'STAGE','author')
    with pytest.raises(ValueError,match='RUN_AUTHORITY'):op.m.pulse(op.frozen,op.approval)
    assert not any(str(op.m.HOOK) in a for a,k in op.calls)

@pytest.mark.parametrize('state,pid,code',[('activating','0','0'),('failed','0','1'),('inactive','42','0')])
def test_start_requires_successfully_terminal_prior(op,state,pid,code):
    op.value.update(ActiveState=state,MainPID=pid,ExecMainStatus=code)
    with pytest.raises(ValueError,match='PRIOR_NOT_SUCCESSFULLY_TERMINAL'):op.m.start(op.frozen,op.approval)
    assert not op.calls
