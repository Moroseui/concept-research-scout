"""Package an independently approved operational adapter around exact scientific notebooks."""
from pathlib import Path
import base64
import copy
import hashlib
import json
import sys

CHANGE = "colab-operational-logins-20261013"
FILES = ("tools/colab_epoch_watchdog.py", "tools/colab_operational_resume.py",
         "tools/package_colab_operational_resume.py",
         "tests/test_colab_epoch_watchdog.py", "tests/test_colab_operational_resume.py",
         "tests/test_package_colab_operational_resume.py",
         "tools/colab_upfront_logins.py", "tests/test_colab_upfront_logins.py")
ORIGINALS = {
    "A1_pnormct": "30bb6ba0d2904cff6f7725c40693dd5b7ef196989f23455e46d6814b12c986f6",
    "A1_pnorm_v2": "ea7d113255d3fa2ff53f156c2d7afc61e47278770e493ab311454b491f847a3b",
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def render(raw, arm, root, approval):
    if arm not in ORIGINALS or sha(raw) != ORIGINALS[arm]:
        raise ValueError("Exact original notebook required")
    original = json.loads(raw)
    notebook = copy.deepcopy(original)
    for cell in original["cells"]:
        if cell.get("outputs") or cell.get("execution_count") is not None:
            raise ValueError("Original must be unexecuted")
    setup = "".join(original["cells"][20]["source"])
    prefix = "pipeline.stream_command("
    if setup.count(prefix) != 1:
        raise ValueError("Exact original transport required")
    start = setup.index(prefix)
    if arm == "A1_pnormct":
        expected = "pipeline.stream_command([sys.executable, '/content/sprint13_pipeline.py', DELIVERY_ARM,\n                  ','.join(str(k) for k in DELIVERY_FOLDS)])\n"
    else:
        expected = "pipeline.stream_command([sys.executable, '/content/sprint13_pipeline.py', DELIVERY_ARM, ','.join(map(str, DELIVERY_FOLDS))])\n"
    if setup[start:] != expected:
        raise ValueError("Original setup suffix changed")
    helpers = {}
    for name in ("colab_epoch_watchdog.py", "colab_operational_resume.py"):
        body = (Path(root) / "tools" / name).read_bytes()
        helpers[name] = {"sha256": sha(body), "base64": base64.b64encode(body).decode()}
    materialize = (
        "import base64, hashlib, json\nfrom pathlib import Path\n"
        "operational_files = " + repr(helpers) + "\n"
        "for name, descriptor in operational_files.items():\n"
        "    content = base64.b64decode(descriptor['base64'], validate=True)\n"
        "    assert hashlib.sha256(content).hexdigest() == descriptor['sha256']\n"
        "    Path('/content', name).write_bytes(content)\n"
    )
    notebook["cells"][20]["source"] = [
        setup[:start] + "from colab_operational_resume import run_notebook\n"
        + "run_notebook(pipeline, DELIVERY_ARM, DELIVERY_FOLDS)\n"
    ]
    notebook["cells"].insert(20, {"cell_type": "code", "metadata": {}, "source": [materialize],
                                 "execution_count": None, "outputs": []})
    note = (
        "# " + arm + ": resume with CPU workers and stall protection\n\n"
        "Fresh default Colab A100, high-RAM runtime: Run all, unedited. Complete all prompts in the first code cell and wait for All logins done, you can leave now before leaving. No later browser interaction is requested. "
        "Do not start while the old session for this arm is running. "
        "Stop and delete that old runtime first, then allow its lease to expire (up to five minutes). "
        "Checkpoints and preprocessing stay in the same private Drive folder. "
        "Completed folds are verified and skipped; an unfinished fold resumes its latest verified checkpoint. "
        "For the reported pnormct checkpoint the next epoch is85; this file verifies the actual record and payload.\n\n"
        "Workers are chosen from available CPU and RAM (12 training/6 validation workers on the recorded runtime). "
        "Scientific source, inputs, normalization, plans, folds, seed,250epochs and scoring are unchanged. "
        "Resume is not a bitwise replay of augmentation workers. Original bindings and checkpoint bytes are retained.\n\n"
        "The historical14-hour estimate is obsolete. At the measured old rate, a five-fold arm takes about 67-68 hours "
        "(roughly 454-460 CU at 6.77 CU/hour). New speed is unmeasured. Use the first completed epochs to assess it.\n\n"
        "During training, the watchdog uses about 3 times the recent median completed-epoch time, bounded to 2-30 minutes. "
        "The first resumed/compiled epoch has a15-minute grace; preparation, validation and scoring are bounded to30minutes. "
        "A stall kills the training process group, prints the last log lines, attempts to save a private error report, "
        "and requests Colab runtime unassignment. If Colab refuses or remains connected, Disconnect and delete runtime manually. "
        "No automatic retry; an interrupted or mismatched migration fails closed. Keep the executed notebook private.\n\n"
        "Independent operational review: " + approval["report_sha256"] + ". "
        "This is an operational repair, not new scientific acceptance or new A100 performance evidence.\n"
    )
    from tools.colab_upfront_logins import frontload
    notebook = frontload(notebook, 21, arm)
    notebook["cells"].insert(0, {"cell_type": "markdown", "metadata": {}, "source": [note]})
    notebook.setdefault("metadata", {})["operational_repair"] = {
        "schema": "colab-workers-watchdog-resume/v1", "arm": arm,
        "original_notebook_sha256": ORIGINALS[arm],
        "implementation_source": approval["source_sha"],
        "implementation_review_sha256": approval["report_sha256"],
        "scientific_source_unchanged": True,
        "new_hardware_performance_qualified": False,
        "helpers": {name: row["sha256"] for name, row in helpers.items()},
    }
    return (json.dumps(notebook, ensure_ascii=True, indent=1) + "\n").encode()

def build(original, arm, root, review, destination):
    from orchestrator.autonomy_review import verify_result
    root, review, destination = Path(root), Path(review), Path(destination)
    approval = verify_result(review)
    report = json.loads((review / "report.md").read_bytes())
    manifest = json.loads((review / "packet-manifest.json").read_bytes())
    if (approval["verdict"] != "APPROVE" or approval["change_id"] != CHANGE
        or report["findings"] != []):
        raise ValueError("Genuine independent implementation APPROVE required")
    for name in FILES:
        if sha((root / name).read_bytes()) != manifest["source_files"].get(name):
            raise ValueError("Reviewed component changed: " + name)
    if arm == "A1_L":
        raw = Path(original).read_bytes()
        if sha(raw) != "b5e1ef2ffcde451c88f4e62d04dcf681a91dccf78c30a4bb6ce53e6922281319":
            raise ValueError("Exact approved L preparation notebook required")
        from tools.colab_upfront_logins import frontload
        before = json.loads(raw)
        result = frontload(before, len(before["cells"])-1, arm)
        result["cells"][0]["source"].append("\nAll prompts are in the first code cell. Wait for All logins done, you can leave now before leaving.\n")
        result["metadata"]["login_packaging_source"] = approval["source_sha"]
        result["metadata"]["login_packaging_review_sha256"] = approval["report_sha256"]
        output = (json.dumps(result, ensure_ascii=True, indent=1) + "\n").encode()
    else:
        output = render(Path(original).read_bytes(), arm, root, approval)
    if destination.exists() or destination.is_symlink():
        raise ValueError("Existing delivery must be reconciled")
    with destination.open("xb") as stream:
        stream.write(output)
    return {"name": destination.name, "sha256": sha(output), "bytes": len(output),
            "arm": arm, "original_notebook_sha256": sha(Path(original).read_bytes()),
            "source": approval["source_sha"], "review": approval["report_sha256"]}
