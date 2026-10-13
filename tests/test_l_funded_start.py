import json,os,stat
from pathlib import Path
from types import SimpleNamespace
import pytest
from tools import l_funded_start as r
from tools import l_funded_runtime as installed

@pytest.fixture
def receipt(tmp_path,monkeypatch):
    from orchestrator import manual_host_guard
    work=tmp_path/"work";folder=work/"lane"/"l-funded-continuation-20261013"
    folder.mkdir(parents=True)
    for p in [work,work/"lane",folder]:p.chmod(0o700)
    target=folder/"COMPLETE.json";target.write_text('{"ok":true}');target.chmod(0o600)
    monkeypatch.setattr(manual_host_guard,"trusted",lambda p:Path(p))
    original=os.fstat
    def owned(fd):
        s=original(fd)
        return SimpleNamespace(st_uid=1003,st_gid=1003,st_mode=s.st_mode,st_nlink=s.st_nlink,st_size=s.st_size)
    monkeypatch.setattr(r.os,"fstat",owned)
    return work,target,owned
def test_real_file_descriptor_reads_private_receipt(receipt):
    work,path,_=receipt
    assert r.service_receipt(path,work)=={"ok":True}
@pytest.mark.parametrize("component",["work","lane","amendment","file"])
def test_wrong_modes_refuse(receipt,component):
    work,path,_=receipt
    p={"work":work,"lane":work/"lane","amendment":path.parent,"file":path}[component]
    p.chmod(0o644 if component=="file" else 0o755)
    with pytest.raises(ValueError,match="PRIVATE_"):r.service_receipt(path,work)
@pytest.mark.parametrize("field,value",[("st_uid",0),("st_uid",999),("st_gid",0)])
def test_wrong_owner_refuses(receipt,monkeypatch,field,value):
    work,path,owned=receipt
    def changed(fd):
        s=owned(fd);setattr(s,field,value);return s
    monkeypatch.setattr(r.os,"fstat",changed)
    with pytest.raises(ValueError,match="PRIVATE_"):r.service_receipt(path,work)
@pytest.mark.parametrize("component",["work","lane","amendment","file"])
def test_symlink_refuses(receipt,component):
    work,path,_=receipt
    p={"work":work,"lane":work/"lane","amendment":path.parent,"file":path}[component]
    real=p.with_name(p.name+"-real");p.rename(real);p.symlink_to(real,target_is_directory=component!="file")
    with pytest.raises(OSError):r.service_receipt(path,work)
def test_hardlink_refuses(receipt):
    work,path,_=receipt;os.link(path,path.with_name("alias"))
    with pytest.raises(ValueError,match="PRIVATE_RECEIPT"):r.service_receipt(path,work)
def test_wrong_path_refuses(receipt):
    work,path,_=receipt
    with pytest.raises(ValueError,match="EXACT_RECEIPT_PATH"):r.service_receipt(path.with_name("other"),work)
def test_large_file_refuses(receipt):
    work,path,_=receipt;path.write_bytes(b"x"*65537)
    with pytest.raises(ValueError,match="PRIVATE_RECEIPT"):r.service_receipt(path,work)
def test_fifo_refuses_without_blocking(receipt):
    work,path,_=receipt;path.unlink();os.mkfifo(path,0o600)
    with pytest.raises(ValueError,match="PRIVATE_RECEIPT"):r.service_receipt(path,work)
def test_bad_json_refuses(receipt):
    work,path,_=receipt;path.write_text("bad")
    with pytest.raises(json.JSONDecodeError):r.service_receipt(path,work)

@pytest.fixture
def start_context(tmp_path,monkeypatch):
    from tools import install_preparation_branch_repair as installer
    record=tmp_path/"record";(record/"operations").mkdir(parents=True)
    lane=tmp_path/"work/lane";lane.mkdir(parents=True)
    approval={"source_sha":r.OLD_SOURCE,"report_sha256":r.OLD_REVIEW}
    old={"source_sha":"c"*40,"report_sha256":"d"*64}
    parent=SimpleNamespace(metadata=lambda:({"new_lane":str(lane)},{"record":str(record),"runtime":"existing","unit":installed.UNIT}),authority=lambda:old)
    parent_runtime=SimpleNamespace(quiet=lambda p:None,CHANGE=installed.CHANGE,encoded=installed.encoded)
    monkeypatch.setattr(r,"authority",lambda:(parent_runtime,approval,parent,{"report_sha256":"a"*64}))
    monkeypatch.setattr(r.os,"getuid",lambda:0)
    monkeypatch.setattr(r,"sys",SimpleNamespace(flags=SimpleNamespace(no_user_site=True)))
    amended={"source":r.OLD_SOURCE,"review_sha256":r.OLD_REVIEW,"status":"L_BASELINE_CONTEXT_READY_NO_CALL"}
    monkeypatch.setattr(r,"service_receipt",lambda path,work:amended)
    transition="e"*64;state={"transition":transition,"phase":"run_spec_author"}
    def output(cmd,text):
        if cmd[-1]=="status":return json.dumps(state)
        assert cmd[-1]==installer.OWNER_CHECK
        return '{"status":"NO_RUNNING_CALL"}'
    monkeypatch.setattr(r.subprocess,"check_output",output)
    def put(path,raw):
        with Path(path).open("xb")as f:f.write(raw)
    monkeypatch.setattr(installer,"put",put)
    starts=[];monkeypatch.setattr(r.subprocess,"run",lambda cmd,check:starts.append(cmd))
    return SimpleNamespace(record=record,state=state,amended=amended,starts=starts,transition=transition,old=old)
@pytest.mark.parametrize("phase",["run_spec_author","run_spec_review"])
def test_same_unit_original_operation_and_replay_refusal(start_context,phase):
    x=start_context;x.state["phase"]=phase
    out=r.start(x.transition)
    assert out["new_owner"]is False and len(x.starts)==1
    operation=json.loads((x.record/"OPERATION.json").read_bytes())
    assert operation=={"mode":"advance","transition":x.transition,"source":x.old["source_sha"],"review_sha256":x.old["report_sha256"],"unit":installed.UNIT}
    with pytest.raises(ValueError,match="START_ALREADY_ATTEMPTED"):r.start(x.transition)
    assert len(x.starts)==1
@pytest.mark.parametrize("field,value",[("source","0"*40),("review_sha256","0"*64),("status","other")])
def test_altered_amendment_refuses_before_intent(start_context,field,value):
    x=start_context;x.amended[field]=value
    with pytest.raises(ValueError,match="AMENDMENT_REQUIRED"):r.start(x.transition)
    assert not x.starts and not list((x.record/"operations").iterdir())
@pytest.mark.parametrize("field,value",[("transition","f"*64),("phase","MODEL_RUNNING"),("phase","BLOCKED")])
def test_changed_pending_state_refuses(start_context,field,value):
    x=start_context;x.state[field]=value
    with pytest.raises(ValueError,match="STATE_CHANGED_OR_HELD"):r.start(x.transition)
    assert not x.starts and not list((x.record/"operations").iterdir())
def test_transport_failure_never_replays(start_context,monkeypatch):
    x=start_context
    def fail(*args,**kw):raise OSError("transport")
    monkeypatch.setattr(r.subprocess,"run",fail)
    with pytest.raises(OSError):r.start(x.transition)
    with pytest.raises(ValueError,match="START_ALREADY_ATTEMPTED"):r.start(x.transition)
def test_uninstalled_start_helper_has_no_authority():
    with pytest.raises(ValueError,match="INSTALLED_ENTRY"):r.authority()

@pytest.mark.parametrize("verdict,change,findings",[("REVISE","l-funded-receipt-start-20261013",[]),("REJECT","l-funded-receipt-start-20261013",[]),("APPROVE","wrong",[]),("APPROVE","l-funded-receipt-start-20261013",[{"open":True}])])
def test_installer_refuses_unapproved_before_any_mutation(tmp_path,monkeypatch,verdict,change,findings):
    from tools import install_l_funded_start as install
    review=tmp_path/"review";review.mkdir()
    (review/"packet-manifest.json").write_text('{}')
    (review/"report.md").write_text(json.dumps({"findings":findings}))
    monkeypatch.setattr(install.os,"getuid",lambda:0)
    monkeypatch.setattr(install,"sys",SimpleNamespace(flags=SimpleNamespace(no_user_site=True)))
    monkeypatch.setattr(install,"trusted",lambda p:Path(p))
    monkeypatch.setattr(install,"standalone_git",lambda p:None)
    monkeypatch.setattr(install,"verify_result",lambda p:{"verdict":verdict,"change_id":change})
    def forbidden(*a,**k):raise AssertionError("mutation before approval")
    monkeypatch.setattr(install.files,"mkdir",forbidden);monkeypatch.setattr(install.files,"put",forbidden)
    with pytest.raises(ValueError,match="APPROVE"):install.install(tmp_path,review)
