"""Packaging checks only: these do not replace the real scientific fixture."""
import base64
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

import pytest
from tools import colab_multiwin_probe as p
from tools import package_multiwin_probe as package


def inputs(monkeypatch):
    bodies = {"execution.py": b"# exact synthetic test stub\n", "plans.json": b"{}\n"}
    monkeypatch.setattr(p, "MODULE_SHA", p.sha(bodies["execution.py"]))
    monkeypatch.setattr(p, "PLANS_SHA", p.sha(bodies["plans.json"]))
    return {name: base64.b64encode(raw).decode() for name, raw in bodies.items()}


def test_materialization_is_exact_and_never_overwrites(tmp_path, monkeypatch):
    payload = inputs(monkeypatch)
    root = tmp_path / "attempt"
    p.materialize(payload, root)
    p.source_hashes(root)
    assert {x.name for x in root.iterdir()} == set(payload)
    assert all(x.stat().st_mode & 0o777 == 0o400 for x in root.iterdir())
    with pytest.raises(RuntimeError, match="EXISTING_ATTEMPT"):
        p.materialize(payload, root)


@pytest.mark.parametrize("damage", ["extra", "module", "plans"])
def test_bad_input_refused_before_any_write(tmp_path, monkeypatch, damage):
    payload = inputs(monkeypatch)
    payload[{"extra": "../escape", "module": "execution.py", "plans": "plans.json"}[damage]] = base64.b64encode(b"changed").decode()
    with pytest.raises(RuntimeError):
        p.materialize(payload, tmp_path / "attempt")
    assert not (tmp_path / "attempt").exists()


def test_changed_source_refused(tmp_path, monkeypatch):
    p.materialize(inputs(monkeypatch), tmp_path / "attempt")
    file = tmp_path / "attempt" / "execution.py"
    file.chmod(0o600)
    file.write_text("changed")
    with pytest.raises(RuntimeError, match="SOURCE_CHANGED"):
        p.source_hashes(tmp_path / "attempt")


def test_child_failure_is_printed_and_full_log_preserved(tmp_path, capsys):
    with pytest.raises(RuntimeError, match="CHILD_EXIT_7"):
        p.run_child([sys.executable, "-c", "import sys;print('failure detail',file=sys.stderr);sys.exit(7)"], tmp_path)
    assert "failure detail" in capsys.readouterr().out
    assert "failure detail" in (tmp_path / "launcher-console.log").read_text()


def test_timeout_kills_and_reaps_the_same_process_group(tmp_path, monkeypatch):
    calls = []
    class Child:
        pid = 43210
        ended = False
        def wait(self, timeout=None):
            calls.append(("wait", timeout))
            if timeout is not None:
                raise subprocess.TimeoutExpired("synthetic", timeout)
            self.ended = True
            return -9
        def poll(self):
            return -9 if self.ended else None
    monkeypatch.setattr(p.subprocess, "Popen", lambda *a, **kw: Child())
    monkeypatch.setattr(p.os, "killpg", lambda pid, sig: calls.append(("kill", pid, sig)))
    with pytest.raises(RuntimeError, match="OUTER_TIMEOUT"):
        p.run_child(["unused"], tmp_path, timeout=1)
    assert calls == [("wait", 1), ("kill", 43210, signal.SIGKILL), ("wait", None)]


def fixture(root):
    out = root / "result/evidence"
    out.mkdir(parents=True)
    scratch = root / "result/scratch"
    scratch.mkdir()
    checkpoint = b"synthetic checkpoint bytes"
    (scratch / "roundtrip.pth").write_bytes(checkpoint)
    native = {"status": "PASS", "synthetic_only": True, "iterations": 1,
              "epochs_completed": 0, "lr_horizon": 250,
              "module_sha256": p.MODULE_SHA, "plans_sha256": p.PLANS_SHA,
              "max_parameter_change": 0.01, "checkpoint_roundtrip": True,
              "checkpoint": {"bytes": len(checkpoint), "sha256": p.sha(checkpoint)}}
    gate = {"status": "PASS", "returncode": 0, "patient_data": False,
            "module_sha256": p.MODULE_SHA}
    bodies = {"plans.json": b"{}", "console.log": b"synthetic log",
              "evidence.json": json.dumps(native).encode(),
              "gate.json": json.dumps(gate).encode()}
    for name, raw in bodies.items():
        (out / name).write_bytes(raw)
    manifest = {"missing": [], "files": {
        n: {"bytes": len(raw), "sha256": p.sha(raw)} for n, raw in bodies.items()}}
    (out / "manifest.json").write_text(json.dumps(manifest))
    return native

def test_requires_real_evidence_and_matching_checkpoint(tmp_path):
    native = fixture(tmp_path)
    assert p.evidence(tmp_path) == native
    (tmp_path / "result/scratch/roundtrip.pth").write_bytes(b"changed")
    with pytest.raises(RuntimeError):
        p.evidence(tmp_path)


@pytest.mark.parametrize("field,value", [
    ("iterations", 0), ("iterations", True), ("status", "FAIL"),
    ("synthetic_only", False), ("module_sha256", "x"),
    ("plans_sha256", "x"), ("max_parameter_change", 0), ("max_parameter_change", float("inf")),
    ("max_parameter_change", float("nan")),
    ("checkpoint_roundtrip", False),
])
def test_rejects_missing_or_overclaimed_evidence(tmp_path, field, value):
    native = fixture(tmp_path)
    native[field] = value
    (tmp_path / "result/evidence/evidence.json").write_text(json.dumps(native))
    with pytest.raises(RuntimeError):
        p.evidence(tmp_path)


def test_package_carries_exact_scientific_bytes_and_separates_drive(monkeypatch):
    monkeypatch.setattr(package, "approved_package", lambda folder: {"report_sha256": "a"*64})
    payload = inputs(monkeypatch)
    review = json.dumps({"schema": "accepted-review-submission/v1", "submission": {
        "bindings": {"call_id": package.REVIEW_CALL, "run_id": package.RUN},
        "verdict": "REVISE", "findings": [{"id": "MULTIWIN-REAL-TRAINER-CHECK-NOT-EXECUTED"}, {"id": "EXECUTION-AUTHORITY-HELD-OPPOSING-EVIDENCE-PENDING"}]}}).encode()
    monkeypatch.setattr(package, "REVIEW_SUBMISSION_SHA", p.sha(review))
    notebook = json.loads(package.build(
        base64.b64decode(payload["execution.py"]), base64.b64decode(payload["plans.json"]), review, "qualified"))
    assert len(notebook["cells"]) == 3
    execution = "".join(notebook["cells"][1]["source"])
    archive = "".join(notebook["cells"][2]["source"])
    assert execution.endswith("RESULT = run(" + repr(payload) + ")\n")
    assert archive == "PRIVATE_EVIDENCE_FOLDER = preserve_to_drive()\n"
    assert notebook["metadata"]["private_only"] is True
    assert all(c.get("outputs", []) == [] for c in notebook["cells"])
    compile(execution, "probe", "exec")
    compile(archive, "archive", "exec")
    with pytest.raises(RuntimeError, match="REVIEW_SUBMISSION"):
        package.build(b"bad", b"bad", review + b" ", "qualified")


def test_packaging_never_runs_child_or_download(monkeypatch):
    monkeypatch.setattr(p.subprocess, "Popen", lambda *a, **k: pytest.fail("no execution during packaging"))
    with pytest.raises((RuntimeError, KeyError, ValueError, FileNotFoundError)):
        package.build(b"", b"", b"{}", "/nonexistent-qualified-review")


def test_failed_install_leaves_terminal_record_and_does_not_run_fixture(tmp_path, monkeypatch):
    payload = inputs(monkeypatch)
    monkeypatch.setattr(p.sys, "version_info", (3, 13, 0))
    monkeypatch.setattr(p.shutil, "disk_usage", lambda x: type("Disk", (), {"free": 30 * 1024**3})())
    calls = []
    def failed(args, root, **kwargs):
        calls.append(args)
        raise RuntimeError("synthetic installer failure")
    monkeypatch.setattr(p, "run_child", failed)
    result = p.run(payload, tmp_path / "attempt")
    assert result["status"] == "FAIL" and len(calls) == 1
    assert "synthetic installer failure" in result["error"]
    assert (tmp_path / "attempt/PACKAGE_RESULT.json").is_file()
    assert not (tmp_path / "attempt/result").exists()


def test_success_requires_both_stages_and_exact_fixture_evidence(tmp_path, monkeypatch):
    payload = inputs(monkeypatch)
    monkeypatch.setattr(p.sys, "version_info", (3, 13, 0))
    monkeypatch.setattr(p.shutil, "disk_usage", lambda x: type("Disk", (), {"free": 30 * 1024**3})())
    calls = []
    def fake(args, root, **kwargs):
        calls.append((args, kwargs))
        if "--synthetic-integration" in args:
            fixture(root)
    monkeypatch.setattr(p, "run_child", fake)
    result = p.run(payload, tmp_path / "attempt")
    assert result["status"] == "PASS" and len(calls) == 3
    assert calls[0][1]["timeout"] == 600
    assert calls[1][1]["timeout"] == 120
    assert calls[1][1]["name"] == "synthetic-tests-console.log"
    assert "m.synthetic_tests()" in calls[1][0][-2]
    assert calls[2][0][1:3] == ["-I", "-B"]
    assert "--synthetic-integration" in calls[2][0]
    assert result["scientific_result_acceptance"] is False


def test_drive_cannot_mount_before_terminal_record(tmp_path):
    with pytest.raises(RuntimeError, match="NO_TERMINAL_RECORD"):
        p.preserve_to_drive(tmp_path)


def test_runtime_disk_stop_precedes_materialization(tmp_path, monkeypatch):
    monkeypatch.setattr(p.sys, "version_info", (3, 13, 0))
    monkeypatch.setattr(p.shutil, "disk_usage", lambda x: type("Disk", (), {"free": 1024**3})())
    with pytest.raises(RuntimeError, match="RUNTIME_DISK"):
        p.run({}, tmp_path / "attempt")
    assert not (tmp_path / "attempt").exists()


def test_cache_files_are_not_enumerated_or_copied(tmp_path):
    fixture(tmp_path)
    cache = tmp_path / "result/scratch/inductor"
    cache.mkdir()
    for i in range(1001):
        (cache / str(i)).write_bytes(b"cache")
    (tmp_path / "result/scratch/unrelated").write_bytes(b"not evidence")
    selected = {str(x.relative_to(tmp_path)) for x in p.evidence_files(tmp_path)}
    assert selected == {"result/evidence/" + n for n in
        ("plans.json", "console.log", "gate.json", "evidence.json", "manifest.json")} | {"result/scratch/roundtrip.pth"}


@pytest.mark.parametrize("damage", ["missing", "extra", "checkpoint", "alias"])
def test_native_evidence_membership_and_alias_refusal(tmp_path, damage):
    fixture(tmp_path)
    ev = tmp_path / "result/evidence"
    if damage in {"missing", "extra"}:
        f = ev / "manifest.json"; v = json.loads(f.read_bytes())
        if damage == "missing": v["missing"] = ["evidence.json"]
        else: v["files"]["../scratch/cache"] = {"bytes": 0, "sha256": p.sha(b"")}
        f.write_text(json.dumps(v))
    elif damage == "checkpoint":
        (tmp_path / "result/scratch/roundtrip.pth").unlink()
    else:
        out = tmp_path / "moved"; ev.rename(out); ev.symlink_to(out, target_is_directory=True)
        with pytest.raises(RuntimeError, match="EVIDENCE_ALIAS"): p.evidence_files(tmp_path)
    with pytest.raises(RuntimeError):
        p.evidence(tmp_path)


@pytest.mark.parametrize("damage", ["none", "verdict", "change", "findings", "source", "missing"])
def test_independent_package_approval_and_exact_component_required(tmp_path, monkeypatch, damage):
    from orchestrator import autonomy_review
    source = tmp_path / "source"
    for name in package.COMPONENT:
        f = source / name; f.parent.mkdir(parents=True, exist_ok=True); f.write_bytes(name.encode())
    monkeypatch.setattr(package, "__file__", str(source / "tools/package_multiwin_probe.py"))
    folder = tmp_path / "approval"; folder.mkdir()
    approval = {"verdict": "APPROVE", "change_id": package.CHANGE, "report_sha256": "a"*64}
    report = {"findings": []}
    pins = {n: p.sha((source/n).read_bytes()) for n in package.COMPONENT}
    if damage == "verdict": approval["verdict"] = "REVISE"
    elif damage == "change": approval["change_id"] = "unrelated"
    elif damage == "findings": report["findings"] = [{"id": "unresolved"}]
    elif damage == "source": (source/package.COMPONENT[0]).write_bytes(b"changed")
    elif damage == "missing": pins.pop(package.COMPONENT[-1])
    (folder/"report.md").write_text(json.dumps(report))
    (folder/"packet-manifest.json").write_text(json.dumps({"source_files": pins}))
    monkeypatch.setattr(autonomy_review, "verify_result", lambda folder: approval)
    if damage == "none": assert package.approved_package(folder) == approval
    else:
        with pytest.raises((RuntimeError, KeyError)): package.approved_package(folder)


@pytest.mark.parametrize("damage", ["reject", "approve", "extra_finding", "call", "run"])
def test_staging_does_not_replace_or_generalize_scientific_revise(monkeypatch, damage):
    payload = inputs(monkeypatch)
    v = {"schema": "accepted-review-submission/v1", "submission": {
        "bindings": {"call_id": package.REVIEW_CALL, "run_id": package.RUN},
        "verdict": "REVISE", "findings": [
            {"id": "MULTIWIN-REAL-TRAINER-CHECK-NOT-EXECUTED"},
            {"id": "EXECUTION-AUTHORITY-HELD-OPPOSING-EVIDENCE-PENDING"}]}}
    if damage in {"reject", "approve"}: v["submission"]["verdict"] = damage.upper()
    elif damage == "extra_finding": v["submission"]["findings"].append({"id": "CODE_DEFECT"})
    elif damage == "call": v["submission"]["bindings"]["call_id"] = "different"
    else: v["submission"]["bindings"]["run_id"] = "different"
    raw = json.dumps(v).encode()
    monkeypatch.setattr(package, "REVIEW_SUBMISSION_SHA", p.sha(raw))
    monkeypatch.setattr(package, "approved_package", lambda folder: {"report_sha256": "a"*64})
    with pytest.raises(RuntimeError, match="SCIENTIFIC_REVIEW"):
        package.build(base64.b64decode(payload["execution.py"]),
                      base64.b64decode(payload["plans.json"]), raw, "qualified")


def test_authored_unit_fixture_failure_prevents_gpu_launch(tmp_path, monkeypatch):
    payload = inputs(monkeypatch)
    monkeypatch.setattr(p.sys, "version_info", (3, 13, 0))
    monkeypatch.setattr(p.shutil, "disk_usage", lambda x: type("Disk", (), {"free": 30 * 1024**3})())
    calls = []
    def child(args, root, **kwargs):
        calls.append(args)
        if kwargs.get("name") == "synthetic-tests-console.log":
            raise RuntimeError("authored E034 fixture failure")
    monkeypatch.setattr(p, "run_child", child)
    result = p.run(payload, tmp_path/"attempt")
    assert result["status"] == "FAIL" and len(calls) == 2
    assert all("--synthetic-integration" not in args for args in calls)
