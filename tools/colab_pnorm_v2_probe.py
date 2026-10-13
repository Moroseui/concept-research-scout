"""Package-only Colab host for one reviewed, unchanged synthetic fixture.

No scientific transformations, patient inputs, Drive login or provider API.
The caller runs this in a fresh default A100 runtime. Preserve the temporary
evidence folder after any failure; the second notebook cell archives it to Drive
only once the child has stopped.
"""
from pathlib import Path
import base64, hashlib, importlib.util, json, math, os, shutil, signal
import subprocess, sys, time, traceback

MODULE_SHA = "59363a58e9bda0a6d4a8b401a9f4d979c7d5c6305c3d7c757d17f0fe7d9cd5a7"
PLANS_SHA = "532aa8160bf0db6c83ceeb0c1456d3bf6f2f7b528cdb0a9586866ac724de92d0"
ROOT = Path("/content/13B_A1_pnorm_v2_real_trainer_check")
MAX_CONSOLE = 2 * 1024**2

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def require(ok, why):
    if not ok:
        raise RuntimeError("INTEGRATION_PACKAGE_" + why)

def materialize(payload, root):
    require(set(payload) == {"execution.py", "plans.json"}, "EXACT_INPUTS")
    for name, pin in [("execution.py", MODULE_SHA), ("plans.json", PLANS_SHA)]:
        raw = base64.b64decode(payload[name], validate=True)
        require(sha(raw) == pin, "INPUT_HASH")
    require(not root.exists() and not root.is_symlink(), "EXISTING_ATTEMPT_KEEP_EVIDENCE")
    root.mkdir(mode=0o700)
    for name, encoded in payload.items():
        with (root / name).open("xb") as out:
            out.write(base64.b64decode(encoded, validate=True))
        (root / name).chmod(0o400)

def source_hashes(root):
    for name, pin in [("execution.py", MODULE_SHA), ("plans.json", PLANS_SHA)]:
        p = root / name
        require(p.is_file() and not p.is_symlink() and sha(p.read_bytes()) == pin,
                "SOURCE_CHANGED")

def run_child(args, root, timeout=720, name="launcher-console.log"):
    # The reviewed scientific entrypoint applies its own 600s bound and worker
    # network audit hook. This outer bound also covers import/setup hangs.
    log = root / name
    proc = None
    with log.open("xb") as stream:
        try:
            proc = subprocess.Popen(args, stdout=stream, stderr=subprocess.STDOUT,
                                    start_new_session=True)
            try:
                returncode = proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
                raise RuntimeError("INTEGRATION_PACKAGE_OUTER_TIMEOUT")
            require(returncode == 0, "CHILD_EXIT_" + str(returncode))
        finally:
            if proc is not None and proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            stream.flush()
            if log.exists():
                with log.open("rb") as inp:
                    inp.seek(max(0, log.stat().st_size - MAX_CONSOLE))
                    print(inp.read(MAX_CONSOLE).decode("utf-8", errors="replace"), flush=True)

def checked_file(path, pin):
    require(path.is_file() and not path.is_symlink()
            and path.stat().st_size == pin["bytes"], "RESULT_FILE")
    h = hashlib.sha256()
    with path.open("rb") as inp:
        for block in iter(lambda: inp.read(4 * 1024**2), b""):
            h.update(block)
    require(h.hexdigest() == pin["sha256"], "RESULT_HASH")

def evidence(root):
    result = root / "result"
    ev = result / "evidence-package"
    require(not result.is_symlink() and not ev.is_symlink(), "EVIDENCE_ALIAS")
    manifest = json.loads((ev / "manifest.json").read_bytes())
    expected = {"execution.py", "plans.json", "console.log", "gate.json", "evidence.json"}
    require(manifest["schema"] == "synthetic-evidence-allowlist/v1"
            and manifest["arm"] == "A1_pnorm_v2"
            and manifest["scientific_acceptance"] is False
            and set(manifest["files"]) == expected, "EVIDENCE_MEMBERSHIP")
    for name in expected:
        checked_file(ev / name, manifest["files"][name])
    require(sha((ev / "execution.py").read_bytes()) == MODULE_SHA
            and sha((ev / "plans.json").read_bytes()) == PLANS_SHA, "EVIDENCE_SOURCE")
    gate = json.loads((ev / "gate.json").read_bytes())
    native = json.loads((ev / "evidence.json").read_bytes())
    require(gate["status"] == "PASS" and gate["returncode"] == 0
            and gate["patient_data"] is False and gate["module_sha256"] == MODULE_SHA,
            "GATE")
    require(native["status"] == "PASS" and native["synthetic_only"] is True
            and type(native["iterations"]) is int and native["iterations"] >= 1
            and native["epochs_completed"] == 0
            and native["module_sha256"] == MODULE_SHA
            and native["plans_sha256"] == PLANS_SHA
            and native["trainer_sha256"] == "7096efb2040135eb60df3c8bf39cdbcc373e299671fcee365b3aff2f4da4dfbd"
            and math.isfinite(native["loss"])
            and math.isfinite(native["max_parameter_change"])
            and native["max_parameter_change"] > 0
            and native["checkpoint_load_exercised"] is True
            and native["channels"] == ["ncct","cbf","cbv","mtt","tmax","cta"]
            and "A100" in native["environment"]["gpu"]
            and native["environment"]["gpu_bytes"] >= 39 * 1024**3,
            "NATIVE_EVIDENCE")
    # Verify the actual locally reloaded checkpoint but never archive its bytes.
    checked_file(result / "native.pth", gate["files"]["native.pth"])
    return native

def run(payload, root=ROOT):
    require(sys.version_info[:2] == (3, 13), "DEFAULT_PYTHON313_REQUIRED")
    require(not Path("/content/drive/MyDrive").exists(), "FRESH_RUNTIME_NO_DRIVE")
    require(shutil.disk_usage(root.parent).free >= 20 * 1024**3, "RUNTIME_DISK")
    materialize(payload, root)
    record = {"scope": "synthetic trainer only; no patient training",
              "module_sha256": MODULE_SHA, "plans_sha256": PLANS_SHA,
              "status": "FAIL", "started_unix": time.time(),
              "scientific_result_acceptance": False}
    try:
        print("Synthetic A1_pnorm_v2 check only. No Drive mount or patient inputs.")
        print("Allow about 10-25 minutes including installation; roughly 1.13-2.82 CU at 6.77 CU/hour. Informational, no balance or spending gate.")
        source_hashes(root)
        install = ("import importlib.util,sys;"
                   "p=sys.argv[1];s=importlib.util.spec_from_file_location('reviewed_pnorm_v2',p);"
                   "m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;"
                   "s.loader.exec_module(m);m.install_dependencies()")
        run_child([sys.executable, "-I", "-B", "-c", install,
                   str(root / "execution.py")], root, timeout=600,
                  name="installation-console.log")
        for name in ("install-report.json", "preinstalled-torch-constraints.txt"):
            report = Path("/content") / name
            if report.is_file():
                shutil.copyfile(report, root / name)
        tests = ("import importlib.util,sys,unittest;"
                 "s=importlib.util.spec_from_file_location('reviewed_pnorm_v2',sys.argv[1]);"
                 "m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;"
                 "s.loader.exec_module(m);"
                 "r=unittest.TextTestRunner(verbosity=2).run(m.synthetic_tests());"
                 "sys.exit(0 if r.wasSuccessful() and r.testsRun==6 and not r.skipped else 1)")
        run_child([sys.executable, "-I", "-B", "-c", tests,
                   str(root / "execution.py")], root, timeout=120,
                  name="synthetic-tests-console.log")
        run_child([sys.executable, "-I", "-B", str(root / "execution.py"),
                   "--synthetic-integration", str(root / "plans.json"),
                   str(root / "result")], root)
        source_hashes(root)
        record["native"] = evidence(root)
        record["status"] = "PASS"
    except BaseException:
        record["error"] = traceback.format_exc(limit=20)
        print(record["error"], flush=True)
    finally:
        try:
            source_hashes(root)
        except BaseException:
            record["status"] = "FAIL"
            record["source_error"] = traceback.format_exc(limit=5)
        record["finished_unix"] = time.time()
        with (root / "PACKAGE_RESULT.json").open("x") as out:
            json.dump(record, out, indent=2, allow_nan=False)
    print("Trainer check:", record["status"], "- the next cell preserves the evidence.")
    print("This checks one synthetic iteration and checkpoint roundtrip, not production input loading or scientific efficacy.")
    return record

def evidence_files(root):
    # Closed file list: no cache traversal. Preserve available evidence on FAIL
    # too, without including checkpoint, dataset or cache payloads.
    names = ("execution.py", "plans.json", "PACKAGE_RESULT.json",
             "installation-console.log", "launcher-console.log", "synthetic-tests-console.log",
             "install-report.json", "preinstalled-torch-constraints.txt",
             "result/evidence-package/execution.py", "result/evidence-package/plans.json",
             "result/evidence-package/console.log", "result/evidence-package/gate.json",
             "result/evidence-package/evidence.json", "result/evidence-package/manifest.json",
             "result/packaging-failure.txt")
    files = []
    for name in names:
        p = root / name
        for part in (p, *p.parents):
            if part == root:
                break
            require(not part.is_symlink(), "EVIDENCE_ALIAS")
        if p.exists():
            require(p.is_file(), "EVIDENCE_FILE")
            files.append(p)
    return sorted(files)

def preserve_to_drive(root=ROOT):
    # run() returns only after run_child has waited/reaped or killed its process.
    require((root / "PACKAGE_RESULT.json").is_file(), "NO_TERMINAL_RECORD")
    # Authentication is the user's normal existing Colab/Drive login. No token is
    # read, copied, printed or recorded. Mount occurs after synthetic execution.
    from google.colab import drive
    drive.mount("/content/drive")
    result = json.loads((root / "PACKAGE_RESULT.json").read_bytes())
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime(result["started_unix"]))
    dest = Path("/content/drive/MyDrive/isles-pilot/private-integration/A1_pnorm_v2") / stamp
    require(not dest.exists() and not dest.is_symlink(), "PRESERVED_ATTEMPT_EXISTS")
    source_hashes(root)
    files = evidence_files(root)
    require(len(files) <= 1000 and sum(p.stat().st_size for p in files) <= 16 * 1024**3,
            "EVIDENCE_SIZE")
    dest.mkdir(parents=True)
    manifest = {}
    for p in files:
        relative = p.relative_to(root)
        out = dest / relative
        out.parent.mkdir(parents=True, exist_ok=True)
        h = hashlib.sha256()
        with p.open("rb") as inp, out.open("xb") as target:
            for block in iter(lambda: inp.read(4 * 1024**2), b""):
                h.update(block)
                target.write(block)
        checked = hashlib.sha256()
        with out.open("rb") as inp:
            for block in iter(lambda: inp.read(4 * 1024**2), b""):
                checked.update(block)
        require(checked.hexdigest() == h.hexdigest(), "DRIVE_COPY_HASH")
        manifest[str(relative)] = {"sha256": h.hexdigest(), "bytes": p.stat().st_size}
    with (dest / "PRESERVED.json").open("x") as out:
        json.dump({"files": manifest, "status": "HASH_VERIFIED",
                   "synthetic_only": True}, out, indent=2)
    print("Evidence preserved privately:", dest)
    print("Report the Trainer check PASS/FAIL and this folder. Keep this runtime open until preservation succeeds.")
    return str(dest)
