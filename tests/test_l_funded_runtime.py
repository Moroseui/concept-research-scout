import copy
from pathlib import Path
import pytest
from tools import l_funded_runtime as r

def props():
    return {"DropInPaths":"","ExecStart":"old","FragmentPath":"same","ExecStartPre":"host guard",
            "ExecStopPost":"","User":"service","Group":"service","Environment":"unchanged",
            "WorkingDirectory":"unchanged","TimeoutStartUSec":"3700s","TimeoutStopUSec":"90s",
            "KillMode":"control-group","Restart":"no","UMask":"0077","NoNewPrivileges":"yes",
            "ProtectSystem":"strict","ReadWritePaths":"fixed","PrivateTmp":"yes","Type":"oneshot"}
def changed(before):
    return {**before,"DropInPaths":str(r.DROP),
            "ExecStart":"{ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 -s -B "+str(r.ROOT/r.ENTRY)+" run ; }"}
def test_only_fixed_entrypoint_changes():
    before=props();r.verify_delta(before,changed(before))
    assert r.drop_bytes().decode().splitlines()==["[Service]","ExecStart=",
          "ExecStart=/usr/bin/python3 -s -B "+str(r.ROOT/r.ENTRY)+" run"]
@pytest.mark.parametrize("field",["ExecStartPre","ExecStopPost","User","Group","Environment","WorkingDirectory",
    "TimeoutStartUSec","KillMode","Restart","UMask","NoNewPrivileges","ProtectSystem","ReadWritePaths","PrivateTmp","Type"])
def test_confinement_delta_refuses(field):
    before=props();after=changed(before);after[field]="changed"
    with pytest.raises(ValueError,match="CONFINEMENT_CHANGED"):r.verify_delta(before,after)
def test_other_dropins_or_commands_refused():
    before=props();after=changed(before)
    with pytest.raises(ValueError,match="ONLY_FIXED_DROPIN"):r.verify_delta({**before,"DropInPaths":"other"},after)
    with pytest.raises(ValueError,match="ONLY_FIXED_DROPIN"):r.verify_delta(before,{**after,"DropInPaths":str(r.DROP)+" other"})
    with pytest.raises(ValueError,match="FIXED_COMMAND"):r.verify_delta(before,{**after,"ExecStart":"unreviewed"})
def test_uninstalled_entry_cannot_claim_authority():
    with pytest.raises(ValueError,match="INSTALLED_ENTRY"):r.authority()
def test_review_requires_entire_component():
    assert {"orchestrator/autonomy_accounting.py","orchestrator/manual_executor.py",
            "orchestrator/colab_arm_question.py","orchestrator/author_revision_accounting.py"} <= r.REQUIRED
    assert len(r.ADDED)==16


def queried(monkeypatch,rows=None,omit=("ExecStopPost",),extra=None):
    import json
    hooks=rows if rows is not None else {"ExecStartPre":[["/guard",["/guard","before"],False,0,0,0,0,0,0,0]],"ExecStopPost":[]}
    def output(cmd,text):
        if cmd[0]=="systemctl":
            assert cmd[:4]==["systemctl","show","--all",r.UNIT]
            fields={k:v for k,v in props().items() if k not in omit}
            if extra:fields.update(extra)
            return "\n".join(k+"="+v for k,v in fields.items())
        if cmd[1]=="call":
            assert cmd[-3:]==["LoadUnit","s",r.UNIT]
            return 'o "/org/freedesktop/systemd1/unit/test"'
        assert cmd[1:3]==["--json=short","get-property"]
        return json.dumps({"type":"a(sasbttttuii)","data":hooks[cmd[-1]]})
    monkeypatch.setattr(r.subprocess,"check_output",output)
    return r.properties()

def test_typed_hooks_and_empty_array_are_explicit(monkeypatch):
    p=queried(monkeypatch)
    assert p["ExecStartPre"]=='[["/guard",["/guard","before"],false]]'
    assert p["ExecStopPost"]=="[]"
    assert set(p)==set(props())

def test_runtime_hook_telemetry_does_not_change_configuration(monkeypatch):
    before=queried(monkeypatch)
    running={"ExecStartPre":[["/guard",["/guard","before"],False,123,456,789,1000,231,1,0]],"ExecStopPost":[]}
    after=queried(monkeypatch,running)
    r.verify_delta(before,changed(after))

@pytest.mark.parametrize("index,value",[(0,"/other"),(1,["/guard","skip"]),(2,True)])
def test_all_command_configuration_fields_remain_compared(monkeypatch,index,value):
    before=queried(monkeypatch)
    row=["/guard",["/guard","before"],False,0,0,0,0,0,0,0];row[index]=value
    after=queried(monkeypatch,{"ExecStartPre":[row],"ExecStopPost":[]})
    with pytest.raises(ValueError,match="CONFINEMENT_CHANGED"):r.verify_delta(before,changed(after))

@pytest.mark.parametrize("hook",["ExecStartPre","ExecStopPost"])
def test_added_or_removed_hooks_refuse(monkeypatch,hook):
    before=queried(monkeypatch)
    rows={"ExecStartPre":[["/guard",["/guard","before"],False,0,0,0,0,0,0,0]],"ExecStopPost":[]}
    rows[hook].append(["/new",["/new"],False,0,0,0,0,0,0,0])
    after=queried(monkeypatch,rows)
    with pytest.raises(ValueError,match="CONFINEMENT_CHANGED"):r.verify_delta(before,changed(after))

@pytest.mark.parametrize("omit,extra",[(("User",),None),((),{"Unknown":"x"})])
def test_nonhook_missing_or_extra_property_refuses(monkeypatch,omit,extra):
    with pytest.raises(ValueError,match="UNIT_PROPERTIES"):queried(monkeypatch,omit=omit,extra=extra)

@pytest.mark.parametrize("row",[[],["/x"],["/x",["/x"],"false",0,0,0,0,0,0,0],["/x",["/x"],False,0,0,0,0,"pid",0,0]])
def test_malformed_typed_hook_refuses(monkeypatch,row):
    with pytest.raises(ValueError,match="TYPED_HOOK_FIELDS"):queried(monkeypatch,{"ExecStartPre":[row],"ExecStopPost":[]})

def test_frozen_context_pins_are_complete(monkeypatch):
    monkeypatch.setattr(r,"ROOT",Path(__file__).resolve().parents[1])
    from orchestrator import manual_host_guard
    monkeypatch.setattr(manual_host_guard,"trusted",lambda p:Path(p))
    checkpoint,question,baseline,pins=r.context()
    assert checkpoint["lanes"]["L"]["run"]=="colab-arm-47e6a72d9a2c821a4938fcae"
    assert r.sha(question)==pins["question_sha256"] and r.sha(baseline)==pins["baseline_sha256"]

def test_no_missing_candidate_component_files():
    root=Path(__file__).resolve().parents[1]
    assert all((root/name).is_file() for name in r.REQUIRED)

@pytest.fixture
def start_context(tmp_path,monkeypatch):
    import json
    from types import SimpleNamespace
    from orchestrator import manual_host_guard
    from tools import install_preparation_branch_repair as installer
    record=tmp_path/"record";record.mkdir()
    (record/"operations").mkdir()
    lane=tmp_path/"lane";lane.mkdir()
    amendment=lane/r.CHANGE;amendment.mkdir()
    approval={"source_sha":"a"*40,"report_sha256":"b"*64}
    old={"source_sha":"c"*40,"report_sha256":"d"*64}
    transition="e"*64
    (amendment/"COMPLETE.json").write_text(json.dumps({
        **{"source":approval["source_sha"],"review_sha256":approval["report_sha256"]},
        "status":"L_BASELINE_CONTEXT_READY_NO_CALL"}))
    parent=SimpleNamespace(metadata=lambda:({"new_lane":str(lane)},
        {"record":str(record),"runtime":"existing-runtime","unit":r.UNIT}),authority=lambda:old)
    monkeypatch.setattr(r,"authority",lambda:(approval,parent))
    monkeypatch.setattr(r,"quiet",lambda p:None)
    monkeypatch.setattr(r.os,"getuid",lambda:0)
    monkeypatch.setattr(r,"sys",SimpleNamespace(flags=SimpleNamespace(no_user_site=True)))
    monkeypatch.setattr(manual_host_guard,"trusted",lambda p:Path(p))
    def put(path,raw):
        with Path(path).open("xb")as out:out.write(raw)
    monkeypatch.setattr(installer,"put",put)
    state={"transition":transition,"phase":"run_spec_author"}
    def output(cmd,text):
        if cmd[-1]=="status":return json.dumps(state)
        assert cmd[-1]==installer.OWNER_CHECK
        return '{"status":"NO_RUNNING_CALL"}'
    monkeypatch.setattr(r.subprocess,"check_output",output)
    starts=[]
    monkeypatch.setattr(r.subprocess,"run",lambda cmd,check:starts.append(cmd))
    return SimpleNamespace(record=record,lane=lane,state=state,transition=transition,
                           approval=approval,old=old,starts=starts)

def test_L_start_keeps_original_native_operation_and_one_durable_intent(start_context):
    import json
    x=start_context
    result=r.start(x.transition)
    assert len(x.starts)==1 and result["new_owner"]is False
    operation=json.loads((x.record/"OPERATION.json").read_text())
    assert operation=={"mode":"advance","transition":x.transition,
                      "source":x.old["source_sha"],"review_sha256":x.old["report_sha256"],"unit":r.UNIT}
    intent=x.record/"operations"/("advance-"+x.transition+".json")
    before=intent.read_bytes()
    with pytest.raises(ValueError,match="START_ALREADY_ATTEMPTED"):r.start(x.transition)
    assert intent.read_bytes()==before and len(x.starts)==1

@pytest.mark.parametrize("field,value",[("transition","f"*64),("phase","BLOCKED"),("phase","MODEL_RUNNING")])
def test_L_changed_or_pending_transition_refuses_before_intent(start_context,field,value):
    x=start_context;x.state[field]=value
    with pytest.raises(ValueError,match="STATE_CHANGED_OR_HELD"):r.start(x.transition)
    assert not x.starts and list((x.record/"operations").iterdir())==[]

def test_L_start_requires_reviewed_context_amendment(start_context):
    import json
    x=start_context
    p=x.lane/r.CHANGE/"COMPLETE.json";v=json.loads(p.read_text());v["source"]="0"*40;p.write_text(json.dumps(v))
    with pytest.raises(ValueError,match="AMENDMENT_REQUIRED"):r.start(x.transition)
    assert not x.starts and list((x.record/"operations").iterdir())==[]

def test_L_start_transport_failure_preserves_consumed_intent(start_context,monkeypatch):
    import subprocess
    x=start_context
    def fail(*args,**kw):raise subprocess.CalledProcessError(1,"systemctl")
    monkeypatch.setattr(r.subprocess,"run",fail)
    with pytest.raises(subprocess.CalledProcessError):r.start(x.transition)
    assert (x.record/"operations"/("advance-"+x.transition+".json")).exists()
    with pytest.raises(ValueError,match="START_ALREADY_ATTEMPTED"):r.start(x.transition)
