import ast
import copy
import json
import os
from pathlib import Path
import sys
import types
import pytest
from tools import package_colab_trainer_upfront as p
from tools import colab_mounted_drive_worker as w

NAMES={"A1_multiwin":"13B_A1_multiwin_real_trainer_check_review12_PRIVATE.ipynb",
       "A1_pnorm_v2":"13B_A1_pnorm_v2_real_trainer_check_PRIVATE.ipynb"}
@pytest.fixture(params=list(NAMES))
def rendered(request):
    arm=request.param;root=Path(__file__).parents[1]
    raw=(Path(os.environ["COLAB_EXACT_MODULE_FIXTURES"])/NAMES[arm]).read_bytes()
    old=json.loads(raw)
    new=json.loads(p.render(raw,arm,root,{"source_sha":"a"*40,"report_sha256":"b"*64}))
    return arm,raw,old,new

def test_exact_scientific_payload_and_no_late_prompts(rendered):
    arm,raw,old,new=rendered
    assert len(new["cells"])==len(old["cells"])+2
    oldcode="".join(old["cells"][1]["source"])
    newcode="".join(new["cells"][3]["source"])
    marker="\n\nRESULT = run("
    assert oldcode.split(marker)[1]==newcode.split(marker)[1]
    assert old["metadata"]["module_sha256"]==new["metadata"]["module_sha256"]
    assert old["metadata"]["plans_sha256"]==new["metadata"]["plans_sha256"]
    assert old["metadata"]["scientific_review_verdict"]==new["metadata"]["scientific_review_verdict"]
    assert new["metadata"]["full_training_authorized"] is False
    for index,cell in enumerate(new["cells"]):
        if cell["cell_type"]=="code":
            tree=ast.parse("".join(cell["source"]))
            for node in ast.walk(tree):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):
                    if node.func.attr in ("mount","authenticate_user","blocking_request"):
                        assert index==1
    assert "All logins done, you can leave now" in "".join(new["cells"][1]["source"])
    with pytest.raises(ValueError,match="Exact previously reviewed"):
        p.render(raw+b" ",arm,Path(__file__).parents[1],{})

@pytest.mark.parametrize("boundary_fails",[False,True])
def test_parent_gate_before_install_and_worker_commands_are_confined(rendered,tmp_path,monkeypatch,boundary_fails):
    _,_,_,new=rendered
    monkeypatch.setitem(sys.modules,"colab_mounted_drive_worker",w)
    text="".join(new["cells"][3]["source"]).split("\n\nRESULT = run(")[0]
    ns={};exec(text,ns)
    original_is_dir=Path.is_dir
    monkeypatch.setattr(Path,"is_dir",lambda path:True if str(path)=="/content/drive/MyDrive" else original_is_dir(path))
    monkeypatch.setattr(ns["shutil"], "disk_usage", lambda path: types.SimpleNamespace(free=100*2**30))
    events=[]
    def materialize(payload,root):
        root.mkdir()
    def gate(root):
        events.append("gate")
        if boundary_fails:raise RuntimeError("namespace unavailable")
    def command(args,root,timeout=720,name="launcher-console.log"):
        events.append((name,args))
    ns.update(materialize=materialize,source_hashes=lambda root:None,
              prepare_boundary=gate,_original_run_child=command,
              isolated_argv=lambda args,root:["BWRAP",*args],
              evidence=lambda root:{"status":"PASS"})
    root=tmp_path/"package"
    result=ns["run"]({},root=root)
    assert events[0]=="gate"
    assert result["status"]==("FAIL" if boundary_fails else "PASS")
    commands=[x for x in events if isinstance(x,tuple)]
    if boundary_fails:assert not commands
    else:
        assert len(commands)==3
        for name,args in commands:
            assert (args[0]=="BWRAP")== (name!="installation-console.log")
    assert (root/"PACKAGE_RESULT.json").is_file()

def test_gate_checks_qualified_review_before_delivery(tmp_path,monkeypatch):
    from orchestrator import autonomy_review
    monkeypatch.setattr(autonomy_review,"verify_result",lambda path:
                        {"change_id":p.CHANGE,"verdict":"REVISE"})
    (tmp_path/"report.md").write_text('{"findings":[{}]}')
    (tmp_path/"packet-manifest.json").write_text('{"source_files":{}}')
    with pytest.raises(ValueError,match="qualified APPROVE"):
        p.build(tmp_path/"absent","A1_multiwin",tmp_path,tmp_path,tmp_path/"out.ipynb")
    assert not (tmp_path/"out.ipynb").exists()
