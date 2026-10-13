"""Private packaging of exact already-reviewed pnorm_v2 scientific bytes."""
from pathlib import Path
import base64, hashlib, json
from tools import colab_pnorm_v2_probe as probe

REVIEW_CALL = "7d44f07e32ed9343acba871aeb8c0f7232c6da281227c1b9585fa06a6a70572e"
RUN = "colab-arm-b9d64a3c09b799bc10b0eba7"
REVIEW_SUBMISSION_SHA = '603e085d3385c1053f55f73fe40928101d976f05187f5f867543daa9ba787dad'

SYNTHETIC_RECEIPT_SHA = "2c1766349854497336dc00e205245d5d9edf22a0859d83ef6d63369bd6e91830"

CHANGE = "pnorm-v2-trainer-package-20261013"
COMPONENT = ("tools/colab_pnorm_v2_probe.py", "tools/package_pnorm_v2_probe.py",
             "tests/test_colab_pnorm_v2_probe.py", "docs/PNORM_V2_TRAINER_PACKAGE_SCOPE.md")

def approved_package(folder):
    # Administrative authority only for this synthetic evidence acquisition.
    # Scientific code approval is preserved; actual GPU evidence is still pending.
    from orchestrator.autonomy_review import verify_result
    approval = verify_result(Path(folder))
    report = json.loads((Path(folder) / "report.md").read_bytes())
    manifest = json.loads((Path(folder) / "packet-manifest.json").read_bytes())
    probe.require(approval["verdict"] == "APPROVE"
                  and approval["change_id"] == CHANGE
                  and report["findings"] == [], "PACKAGE_APPROVAL")
    root = Path(__file__).resolve().parents[1]
    for name in COMPONENT:
        probe.require(probe.sha((root / name).read_bytes()) == manifest["source_files"][name],
                      "PACKAGE_SOURCE")
    return approval

def build(module, plans, submission, synthetic, approval_folder):
    approval = approved_package(approval_folder)
    probe.require(probe.sha(submission) == REVIEW_SUBMISSION_SHA, "REVIEW_SUBMISSION")
    record = json.loads(submission)
    verdict = record["submission"]
    probe.require(record["schema"] == "accepted-review-submission/v1"
                  and verdict["verdict"] == "APPROVE"
                  and verdict["findings"] == []
                  and verdict["bindings"]["call_id"] == REVIEW_CALL
                  and verdict["bindings"]["run_id"] == RUN,
                  "SCIENTIFIC_REVIEW")
    probe.require(probe.sha(synthetic) == SYNTHETIC_RECEIPT_SHA,
                  "NATIVE_SYNTHETIC_RECEIPT")
    tests = json.loads(synthetic)
    probe.require(tests["status"] == "PASS"
                  and tests["binding"]["files"]["execution.py"] == probe.MODULE_SHA
                  and tests["isolation"]["patient_mounts"] is False
                  and tests["isolation"]["credentials"] is False
                  and tests["isolation"]["network"] == "UNSHARED"
                  and len(tests["tests"]["records"]) == 5
                  and all(r["status"] == "PASS" for r in tests["tests"]["records"]),
                  "NATIVE_SYNTHETIC_PASS")
    probe.require(probe.sha(module) == probe.MODULE_SHA
                  and probe.sha(plans) == probe.PLANS_SHA, "REVIEWED_BYTES")
    payload = {name: base64.b64encode(raw).decode() for name, raw in
               [("execution.py", module), ("plans.json", plans)]}
    runtime = Path(probe.__file__).read_text()
    cell1 = runtime + "\n\nRESULT = run(" + repr(payload) + ")\n"
    cell2 = "PRIVATE_EVIDENCE_FOLDER = preserve_to_drive()\n"
    intro = """# A1_pnorm_v2: real trainer integration check
Use a **fresh default Colab A100** runtime and click **Run all**. No settings to edit.
Scientific code review is APPROVE and all five native synthetic groups passed. This package runs the remaining real A100 check; it does not authorize the full training notebook.
This is a synthetic check of the exact scientifically reviewed code, not the five-fold training notebook.
It constructs the actual trainer, runs one real forward/backward/optimizer iteration and verifies checkpoint save/reload.
It does not test the production data loader or establish scientific efficacy.
No Drive mount or real input is used during execution. After the child stops, the final cell asks for your existing Drive login and preserves compact declared evidence privately, excluding caches, datasets and checkpoints.
Expect about 10-25 minutes including installation, roughly 1.13-2.82 CU at 6.77 CU/hour; this is an estimate, not a spending gate.
Report the printed PASS/FAIL and private evidence folder. Keep the runtime open until preservation succeeds.
Do not rerun or delete a failed attempt; return its evidence for diagnosis.
"""
    cells = [{"cell_type": "markdown", "metadata": {}, "source": intro.splitlines(True)}]
    for text in [cell1, cell2]:
        cells.append({"cell_type": "code", "metadata": {}, "source": text.splitlines(True),
                      "execution_count": None, "outputs": []})
    nb = {"nbformat": 4, "nbformat_minor": 5, "cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3", "name": "python3"},
                       "accelerator": "GPU",
                       "colab": {"provenance": [], "gpuType": "A100"},
                       "private_only": True,
                       "scientific_review_call": REVIEW_CALL,
                       "scientific_review_verdict": "APPROVE",
                       "native_synthetic_receipt_sha256": probe.sha(synthetic),
                       "full_training_authorized": False,
                       "packaging_approval_sha256": approval["report_sha256"],
                       "module_sha256": probe.MODULE_SHA, "plans_sha256": probe.PLANS_SHA,
                       "review_submission_sha256": probe.sha(submission),
                       "runtime_sha256": probe.sha(runtime.encode()),
                       "purpose": "synthetic real trainer check; no patient run or efficacy claim"}}
    return (json.dumps(nb, indent=1, ensure_ascii=True) + "\n").encode()
