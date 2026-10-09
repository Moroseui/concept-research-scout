"""Actual driver transitions/Git/package verification; synthetic science only."""
import json
import subprocess
from pathlib import Path
import pytest
from orchestrator import experiment_package as package, private_records as pr
from orchestrator import experiment_approval as approval, review_submission as rs
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import digest, inventory
from test_experiment_approval import reviewed
from test_experiment_context import experiment, root


def test_package_keeps_exact_reviewed_bytes_and_is_idempotent(reviewed):
    d,value,work=reviewed
    Driver._accept_completed(d,value)
    calls=[tuple(r) for r in d.store.db.execute("SELECT * FROM manual_calls")]
    original={p:p.read_bytes() for p in work.iterdir() if p.is_file()}
    manifest=package.emit(d,value)
    folder=d.state/"experiment-package"
    assert package.verify(d,value,folder)==manifest==package.emit(d,value)
    assert manifest["execution_admitted"] is False and manifest["real_data_execution"] is False
    sealed=approval.verify(d,value)
    for name,ref in sealed["code_files"].items():
        assert (folder/"code"/name).read_bytes()==Path(ref["path"]).read_bytes()
    assert (folder/"review.json").read_bytes()==(work/"review.json").read_bytes()
    assert (folder/"SPEC.md").read_bytes()==Path(value["spec"]).read_bytes()
    assert (folder/"execution-plan.json").read_bytes()==(d.context/"execution-plan.json").read_bytes()
    assert not any(p.name in {"console.log","prompt.md",rs.RECORD} for p in folder.rglob("*"))
    assert all(p.read_bytes()==raw for p,raw in original.items())
    assert [tuple(r) for r in d.store.db.execute("SELECT * FROM manual_calls")]==calls
    pr.check_tree(folder)


@pytest.mark.parametrize("damage",["code","manifest","extra","missing","unsafe","changed-original"])
def test_existing_package_is_never_rebuilt_after_damage(reviewed,damage):
    d,value,work=reviewed;Driver._accept_completed(d,value);package.emit(d,value)
    folder=d.state/"experiment-package";code=next((folder/"code").iterdir())
    if damage=="code":pr.write_text(code,"changed")
    if damage=="manifest":pr.write_text(folder/"manifest.json",'{}')
    if damage=="extra":pr.write_text(folder/"unreviewed.py","# extra")
    if damage=="missing":code.unlink() # Disposable fixture only.
    if damage=="unsafe":code.chmod(0o644) # Planted negative fixture.
    if damage=="changed-original":pr.write_text(Path(value["spec"]),"changed")
    before={str(p):p.read_bytes() for p in folder.rglob("*") if p.is_file()}
    with pytest.raises((ValueError,FileNotFoundError)):package.emit(d,value)
    assert {str(p):p.read_bytes() for p in folder.rglob("*") if p.is_file()}==before


def test_partial_package_refuses_without_overwrite(reviewed):
    d,value,work=reviewed;Driver._accept_completed(d,value)
    folder=d.state/"experiment-package";pr.mkdir(folder);pr.write_text(folder/"SPEC.md","partial")
    with pytest.raises(ValueError,match="^EXPERIMENT_PACKAGE_PARTIAL_INSPECT_NO_REBUILD$"):
        package.emit(d,value)
    assert (folder/"SPEC.md").read_text()=="partial"


def connect_driver(d,value,tmp_path):
    # Only outer source/host setup is a fixture; the actual _advance, Git commit,
    # ledger, approval verifier, assembler and package producer run normally.
    repo=tmp_path/"test-repo";pr.mkdir(repo)
    subprocess.run(["git","init","-b","astra/manual-experiment-test",str(repo)],check=True,capture_output=True)
    for k,v in (("user.name","Synthetic Test"),("user.email","synthetic@example.invalid")):
        subprocess.run(["git","config","--local",k,v],cwd=repo,check=True)
    pr.write_text(repo/"README.md","Synthetic test repository, not scientific evidence.\n")
    subprocess.run(["git","add","README.md"],cwd=repo,check=True)
    subprocess.run(["git","commit","-m","Synthetic seed"],cwd=repo,check=True,capture_output=True)
    d.root=repo;d.current=lambda:value
    guards=[];d.guard=lambda:guards.append("outer-fixture-guard")
    return guards


def test_actual_driver_commits_then_packages_without_legacy_execution(reviewed,tmp_path):
    d,value,work=reviewed;Driver._accept_completed(d,value)
    guards=connect_driver(d,value,tmp_path)
    before=[tuple(r) for r in d.store.db.execute("SELECT * FROM manual_calls")]
    Driver._advance(d)
    assert value["phase"]=="EMIT_EXPERIMENT_PACKAGE" and guards
    commit=value["spec_commit"]
    target=d.root/"projects/isles24/experiments"/d.config["run_id"]/"spec"
    assert (target/"SPEC.md").read_bytes()==Path(value["spec"]).read_bytes()
    # Simulate interruption after exact Git commit and before saved phase.
    value["phase"]="COMMIT_SPEC";Driver._advance(d)
    assert value["spec_commit"]==commit
    Driver._advance(d)
    assert value["phase"]=="EXECUTE_EXPERIMENT"
    manifest=package.verify(d,value,Path(value["execution_package"]["path"]))
    assert digest(rs.canonical(manifest))==value["execution_package"]["sha256"]
    if d.config["item_number"] == 4:
        result=Driver._advance(d)
        assert result["next_action"]=="WAIT_EXECUTION_PREPARATION" and result["provider_called"] is False
    else:
        with pytest.raises(ValueError,match="^DIAGNOSTICS_EXECUTABLE_CONTRACT_REQUIRED$"):Driver._advance(d)
    assert not (d.state/"validation.json").exists()
    assert [tuple(r) for r in d.store.db.execute("SELECT * FROM manual_calls")]==before


def test_unrelated_edits_not_swept_into_commit(reviewed,tmp_path):
    d,value,work=reviewed;Driver._accept_completed(d,value);connect_driver(d,value,tmp_path)
    pr.write_text(d.root/"unrelated.txt","must not commit")
    before=subprocess.check_output(["git","rev-parse","HEAD"],cwd=d.root)
    with pytest.raises(ValueError,match="^UNRELATED_EDITS_BEFORE_EXPERIMENT_COMMIT$"):Driver._advance(d)
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=d.root)==before


def test_halt_or_guard_failure_precedes_package_writes(reviewed,tmp_path):
    d,value,work=reviewed;Driver._accept_completed(d,value);connect_driver(d,value,tmp_path)
    def stopped():raise ValueError("OPERATOR_HALT")
    d.guard=stopped
    with pytest.raises(ValueError,match="^OPERATOR_HALT$"):Driver._advance(d)
    assert not (d.state/"experiment-package").exists()
    assert not (d.root/"projects").exists()


def test_manual_return_arguments_do_not_enter_experiment_lane(reviewed,tmp_path):
    d,value,work=reviewed;Driver._accept_completed(d,value);connect_driver(d,value,tmp_path)
    with pytest.raises(ValueError,match="^EXPERIMENT_LEGACY_COLLECTION_REFUSED$"):
        Driver._advance(d,collect_folder="synthetic-return")


def test_no_approval_cannot_build_package_or_commit(reviewed,tmp_path):
    d,value,work=reviewed;Driver._accept_completed(d,value);connect_driver(d,value,tmp_path)
    value.pop("reviewed_execution")
    with pytest.raises(KeyError):Driver._advance(d)
    assert not (d.root/"projects").exists()
    with pytest.raises(KeyError):package.emit(d,value)
    assert not (d.state/"experiment-package").exists()
