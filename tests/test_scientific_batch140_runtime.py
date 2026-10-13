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
