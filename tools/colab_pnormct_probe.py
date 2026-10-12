"""Package-only Colab host for one reviewed, unchanged synthetic fixture.

No scientific transformations, patient inputs, Drive login or provider API.
The caller runs this in a fresh default A100 runtime. Preserve the temporary
evidence folder after any failure; the second notebook cell archives it to Drive
only once the child has stopped.
"""
from pathlib import Path
import base64, hashlib, importlib.util, json, os, shutil, signal
import subprocess, sys, time, traceback

MODULE_SHA = "33153177657c1f2a3383bcd50fffb393a571514c3363f7ef2c24f131d48251f2"
PLANS_SHA = "532aa8160bf0db6c83ceeb0c1456d3bf6f2f7b528cdb0a9586866ac724de92d0"
ROOT = Path("/content/13B_A1_pnormct_real_trainer_check")
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

def evidence(root):
    result = root / "result"
    gate = json.loads((result / "gate.json").read_bytes())
    native = json.loads((result / "evidence.json").read_bytes())
    require(gate["status"] == "PASS" and gate["returncode"] == 0
            and gate["patient_data"] is False and gate["module_sha256"] == MODULE_SHA,
            "GATE")
    require(native["status"] == "PASS" and native["synthetic_only"] is True
            and type(native["iterations"]) is int and native["iterations"] >= 1
            and native["module_sha256"] == MODULE_SHA
            and native["plans_sha256"] == PLANS_SHA
            and native["max_parameter_change"] > 0
            and native["checkpoint_load_exercised"] is False,
            "NATIVE_EVIDENCE")
    for name in ("native.pth", "evidence.json", "plans.json", "console.log"):
        pin = gate["files"][name]
        p = result / name
        require(p.is_file() and not p.is_symlink()
                and p.stat().st_size == pin["bytes"], "RESULT_FILE")
        h = hashlib.sha256()
        with p.open("rb") as inp:
            for block in iter(lambda: inp.read(4 * 1024**2), b""):
                h.update(block)
        require(h.hexdigest() == pin["sha256"], "RESULT_HASH")
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
        print("Synthetic A1_pnormct check only. No Drive mount or patient inputs.")
        print("Allow about 10-25 minutes including installation; roughly 1.13-2.82 CU at 6.77 CU/hour. Informational, no balance or spending gate.")
        source_hashes(root)
        install = ("import importlib.util,sys;"
                   "p=sys.argv[1];s=importlib.util.spec_from_file_location('reviewed_pnormct',p);"
                   "m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;"
                   "s.loader.exec_module(m);m.install_dependencies()")
        run_child([sys.executable, "-I", "-B", "-c", install,
                   str(root / "execution.py")], root, timeout=600,
                  name="installation-console.log")
        for name in ("install-report.json", "pnormct-preinstalled-constraints.txt"):
            report = Path("/content") / name
            if report.is_file():
                shutil.copyfile(report, root / name)
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
    print("This is not the five-fold training notebook and does not establish checkpoint reload or scientific efficacy.")
    return record

def evidence_files(root):
    # The reviewed fixture declares root-level result files in gate.json.
    # Compilation and temporary work live in subdirectories; they are not
    # evidence and can contain thousands of cache entries.
    names = ('execution.py', 'plans.json', 'PACKAGE_RESULT.json',
             'installation-console.log', 'launcher-console.log',
             'install-report.json', 'pnormct-preinstalled-constraints.txt')
    files = []
    for name in names:
        p = root / name
        require(not p.is_symlink(), 'EVIDENCE_ALIAS')
        if p.exists():
            require(p.is_file(), 'EVIDENCE_FILE')
            files.append(p)
    result = root / 'result'
    require(not result.is_symlink(), 'EVIDENCE_ALIAS')
    if result.exists():
        require(result.is_dir(), 'EVIDENCE_DIRECTORY')
        for p in result.iterdir():
            require(not p.is_symlink(), 'EVIDENCE_ALIAS')
            if p.is_file():
                files.append(p)
        gate = result / 'gate.json'
        if gate.is_file():
            for name in json.loads(gate.read_bytes()).get('files', {}):
                require(Path(name).name == name, 'EVIDENCE_MEMBER')
                require(result / name in files, 'EVIDENCE_MEMBER')
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
    dest = Path("/content/drive/MyDrive/isles-pilot/private-integration/A1_pnormct") / stamp
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
