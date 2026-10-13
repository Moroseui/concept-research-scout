"""Front-load trainer-check Drive login, preserving exact scientific payloads."""
from pathlib import Path
import base64
import copy
import hashlib
import json

CHANGE = "colab-trainer-upfront-20261013"
COMPONENT = ("tools/colab_mounted_drive_worker.py",
             "tools/package_colab_trainer_upfront.py",
             "tests/test_colab_mounted_drive_worker.py",
             "tests/test_package_colab_trainer_upfront.py")
ORIGINALS = {
    "A1_multiwin": "71daab2445b23d98167d7edc53e0bca058967c7060b881af2fd8a51abe4641ec",
    "A1_pnorm_v2": "b28ca24032ad0cd4f511fd05cb5b7d94069d606062f5092edda53700698f62ac",
}
def sha(raw):
    return hashlib.sha256(raw).hexdigest()

LOGIN = """# FIRST CELL: all Drive authorization (about two minutes)
from google.colab import drive
import signal
print("Complete Drive authorization now; no later login is requested.", flush=True)
def _login_timeout(signum, frame):
    raise TimeoutError("Drive login did not finish within two minutes. No installation or GPU test started.")
if signal.getitimer(signal.ITIMER_REAL) != (0.0, 0.0):
    raise RuntimeError("Unexpected existing login timer")
_login_old_handler = signal.signal(signal.SIGALRM, _login_timeout)
signal.setitimer(signal.ITIMER_REAL, 120)
try:
    drive.mount('/content/drive', timeout_ms=60000)
finally:
    signal.setitimer(signal.ITIMER_REAL, 0)
    signal.signal(signal.SIGALRM, _login_old_handler)
print("All logins done, you can leave now", flush=True)
"""
WRAPPER = """
from colab_mounted_drive_worker import isolated_argv, prepare_boundary
_original_run_child = run_child
def run_child(args, root, timeout=720, name="launcher-console.log"):
    if name != "installation-console.log":
        args = isolated_argv(args, root)
    return _original_run_child(args, root, timeout=timeout, name=name)
"""

def code_cell(code):
    return {"cell_type":"code", "metadata":{}, "source":[code],
            "execution_count":None, "outputs":[]}

def render(raw, arm, root, approval):
    if arm not in ORIGINALS or sha(raw) != ORIGINALS[arm]:
        raise ValueError("Exact previously reviewed trainer notebook required")
    old = json.loads(raw)
    if any(c.get("outputs") or c.get("execution_count") is not None for c in old["cells"]):
        raise ValueError("Unexecuted original required")
    result = copy.deepcopy(old)
    text = "".join(old["cells"][1]["source"])
    marker = "\n\nRESULT = run("
    if text.count(marker) != 1:
        raise ValueError("Known exact runtime entry required")
    runtime, invocation = text.split(marker)
    if sha(runtime.encode()) != old["metadata"]["runtime_sha256"]:
        raise ValueError("Original runtime hash")
    replacements = [
        ('require(not Path("/content/drive/MyDrive").exists(), "FRESH_RUNTIME_NO_DRIVE")',
         'require(Path("/content/drive/MyDrive").is_dir(), "FIRST_CELL_DRIVE_REQUIRED")'),
        ('    drive.mount("/content/drive")',
         '    require(Path("/content/drive/MyDrive").is_dir(), "DRIVE_LOGIN_LOST_NO_LATE_PROMPT")'),
        ('    names = ("execution.py", "plans.json", "PACKAGE_RESULT.json",',
         '    names = ("namespace-setup.log", "worker-boundary.json", "execution.py", "plans.json", "PACKAGE_RESULT.json",'),
        ('        source_hashes(root)\n        install =',
         '        source_hashes(root)\n        prepare_boundary(root)\n        install ='),
    ]
    for before, after in replacements:
        if runtime.count(before) != 1:
            raise ValueError("Unrecognized original runtime fragment")
        runtime = runtime.replace(before, after)
    runtime = runtime.replace("No Drive mount or patient inputs.", "Parent Drive mounted; synthetic worker has no Drive access.")
    runtime = runtime.replace("Mount occurs after synthetic execution.", "Drive authorization completed in the first cell.")
    helper = (Path(root)/"tools/colab_mounted_drive_worker.py").read_bytes()
    materialize = (
        "import base64, hashlib\nfrom pathlib import Path\n"
        "raw = base64.b64decode(" + repr(base64.b64encode(helper).decode()) + ", validate=True)\n"
        "assert hashlib.sha256(raw).hexdigest() == " + repr(sha(helper)) + "\n"
        "Path('/content/colab_mounted_drive_worker.py').write_bytes(raw)\n"
    )
    result["cells"][1]["source"] = [runtime + WRAPPER + marker + invocation]
    result["cells"][0]["source"] = [
        "# " + arm + ": synthetic trainer check with all logins first\n\n"
        "Use a fresh default Colab A100, Run all unedited. Complete the first-cell Drive prompt "
        "and wait for **All logins done, you can leave now**. No later login or browser capture.\n\n"
        "The parent keeps Drive mounted to save results automatically. Before dependency installation, "
        "a synthetic OS isolation check must prove that the worker cannot access the parent's Drive or data. "
        "The worker has separate mount, process and network namespaces; existing scientific checks remain unchanged. "
        "If this provider cannot supply the boundary, the check fails before pip or GPU work. No fallback weakens it.\n\n"
        "This remains a synthetic trainer/checkpoint check, not a full training notebook or scientific acceptance. "
        "Scientific code, plans, tests and acceptance criteria are unchanged. Expected 10-25 minutes after login "
        "plus brief isolation setup; no measured new GPU timing is claimed. "
        "Compact evidence is saved automatically to the same private Drive location, excluding caches.\n\n"
        + ("Pnorm_v2 already passed its real trainer check: do not repeat it just for this login update.\n"
           if arm == "A1_pnorm_v2" else "Return the printed PASS/FAIL and private evidence folder. Full multiwin training remains held pending scientific judgment.\n")
    ]
    result["cells"].insert(1,code_cell(LOGIN))
    result["cells"].insert(2,code_cell(materialize))
    result["metadata"].update(
        original_notebook_sha256=ORIGINALS[arm],
        original_runtime_sha256=old["metadata"]["runtime_sha256"],
        runtime_sha256=sha((runtime+WRAPPER).encode()),
        worker_boundary_sha256=sha(helper),
        upfront_packaging_source=approval["source_sha"],
        upfront_packaging_review_sha256=approval["report_sha256"],
        interaction_policy="all prompts first cell; no later auth or browser capture",
        scientific_payload_unchanged=True,
        gpu_boundary_qualification="pending actual provider execution",
    )
    return (json.dumps(result, ensure_ascii=True, indent=1)+"\n").encode()

def build(original, arm, root, review, destination):
    from orchestrator.autonomy_review import verify_result
    root,review,destination=Path(root),Path(review),Path(destination)
    approval=verify_result(review)
    report=json.loads((review/"report.md").read_bytes())
    manifest=json.loads((review/"packet-manifest.json").read_bytes())
    if approval["change_id"]!=CHANGE or approval["verdict"]!="APPROVE" or report["findings"]:
        raise ValueError("Independent qualified APPROVE required")
    for name in COMPONENT:
        if sha((root/name).read_bytes())!=manifest["source_files"].get(name):
            raise ValueError("Reviewed component changed")
    body=render(Path(original).read_bytes(),arm,root,approval)
    with destination.open("xb") as out:
        out.write(body)
    return {"name":destination.name,"sha256":sha(body),"bytes":len(body),
            "source":approval["source_sha"],"review":approval["report_sha256"],"arm":arm}
