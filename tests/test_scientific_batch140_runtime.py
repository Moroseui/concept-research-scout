import copy
from pathlib import Path
import pytest
from tools import scientific_batch140_runtime as r

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
            "orchestrator/scientific_program.py","orchestrator/author_revision_accounting.py"} <= r.REQUIRED
    assert len(r.ADDED)==14

def test_patched_meeting_receipt_satisfies_unused_new_allocation_gate():
    from orchestrator.meeting_batch140 import meeting_receipt
    from orchestrator.meeting_preparation import require
    allowance=meeting_receipt({"purpose":"meeting","purpose_limit":4,"purpose_used":0,"limit":140})
    require(allowance["meeting_allocation_used"]==0,"EXACT_UNUSED_MEETING_ALLOCATION")
    assert allowance["meeting_allocation_limit"]==4 and allowance["meeting_calls_preserved"]==4
    allowance=meeting_receipt({"purpose":"meeting","purpose_limit":4,"purpose_used":1,"limit":140})
    with pytest.raises(ValueError,match="EXACT_UNUSED_MEETING_ALLOCATION"):
        require(allowance["meeting_allocation_used"]==0,"EXACT_UNUSED_MEETING_ALLOCATION")


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
