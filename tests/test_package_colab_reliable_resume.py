import ast
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest
from tools import package_colab_reliable_resume as p
from tools import colab_reliable_resume as bootstrap

@pytest.fixture(params=["A1_pnormct","A1_pnorm_v2"])
def candidate(request,tmp_path):
    arm=request.param
    originals=Path(os.environ["COLAB_RESUME_BASES"])
    raw=(originals/(arm+".ipynb")).read_bytes()
    out=p.render(raw,arm,Path(__file__).parents[1]/"tools")
    before,after=json.loads(raw),json.loads(out)
    return arm,before,after,tmp_path

def materialize(n,root):
    for c in n["cells"]:
        s="".join(c["source"])
        if "operational_files = " not in s:continue
        for node in ast.parse(s).body:
            if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=="operational_files"for t in node.targets):
                files=ast.literal_eval(node.value)
                for name,row in files.items():
                    body=base64.b64decode(row["base64"],validate=True)
                    assert hashlib.sha256(body).hexdigest()==row["sha256"]
                    (root/name).write_bytes(body)
                return files
    raise AssertionError("No helper block")

def test_exact_science_logins_and_settings_unchanged(candidate):
    arm,before,after,_=candidate
    changed=[]
    for i,(a,b)in enumerate(zip(before["cells"],after["cells"])):
        if a!=b:changed.append(i)
        source="".join(a["source"])
        if a["cell_type"]=="code" and (source.startswith("%%writefile") or "All logins done" in source or "DELIVERY_FOLDS =" in source):
            assert a==b
    assert len(changed)==3 and changed[0]==0
    assert after["metadata"]["storage_repair_candidate"]["release_status"]=="UNRELEASED_REVIEW_REQUIRED"

def test_exact_legacy_binding_and_parent_dispatch(candidate,monkeypatch):
    arm,before,after,root=candidate
    files=materialize(after,root)
    monkeypatch.syspath_prepend(str(root))
    for name in ("colab_operational_resume","colab_epoch_watchdog","colab_private_output"):
        monkeypatch.delitem(sys.modules,name,raising=False)
    monkeypatch.setattr(bootstrap,"__file__",str(root/"colab_reliable_resume.py"))
    original=bootstrap.checked(arm)
    assert original.policy_identity()==bootstrap.PINNED[arm]["identity"]
    import colab_epoch_watchdog as watch
    import colab_private_output as folder
    calls=[]
    monkeypatch.setattr(folder,"install",lambda m:calls.append("folder"))
    def supervise(argv,token,**kwargs):
        calls.append(argv);return "child-result"
    monkeypatch.setattr(watch,"supervise",supervise)
    m=SimpleNamespace(__file__="/exact/science.py")
    def run(m,a,folds):
        assert a==arm and folds==(0,1,2,3,4)
        return watch.supervise([sys.executable,"-u",original.__file__,"--child",m.__file__,arm],"token")
    monkeypatch.setattr(original,"run_notebook",run)
    assert bootstrap.run_notebook(m,arm,(0,1,2,3,4))=="child-result"
    assert calls==["folder",[sys.executable,"-u",str(root/"colab_reliable_resume.py"),"--child",m.__file__,arm]]
    assert watch.supervise is supervise

def test_tampered_legacy_refused(candidate,monkeypatch):
    arm,_,after,root=candidate
    materialize(after,root)
    monkeypatch.setattr(bootstrap,"__file__",str(root/"colab_reliable_resume.py"))
    with (root/"colab_operational_resume.py").open("a")as s:s.write("\n# changed\n")
    with pytest.raises(RuntimeError,match="SOURCE_CHANGED"):bootstrap.checked(arm)

def test_wrong_base_refused():
    with pytest.raises(ValueError,match="EXACT_PRIOR"):p.render(b"{}", "A1_pnormct",Path("."))

def test_child_installs_all_hooks_and_restores(monkeypatch):
    calls=[];m=SimpleNamespace()
    def adapter(m):calls.append("original");return "old-binding"
    orig=SimpleNamespace(install_adapter=adapter)
    def child(path,arm):
        assert orig.install_adapter(m)=="old-binding"
        calls.append("child")
    orig.child=child
    monkeypatch.setattr(bootstrap,"checked",lambda arm:orig)
    monkeypatch.setitem(sys.modules,"colab_private_output",SimpleNamespace(install=lambda m:calls.append("folder")))
    monkeypatch.setitem(sys.modules,"colab_storage_reliability",SimpleNamespace(install=lambda m:(calls.append("storage")or {"repair":True})))
    bootstrap.child("source","A1_pnormct")
    assert calls==["original","folder","storage","child"]
    assert orig.install_adapter is adapter
