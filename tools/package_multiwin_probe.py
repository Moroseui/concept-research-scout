"""Private packaging of exact already-reviewed multiwin scientific bytes."""
from pathlib import Path
import base64, hashlib, json
from tools import colab_multiwin_probe as probe

REVIEW_CALL = "01a477307a7309b31baa04983b107a560835e052c803b29d661c20c28b28041e"
RUN = "colab-1ad5fafc220b3d65f576ce08"
REVIEW_SUBMISSION_SHA = 'bb3d25f29f35788140be9b23783819e3496f45dae7513a4483c3458bd209ff43'

CHANGE = "multiwin-trainer-package-20261012"
COMPONENT = ("tools/colab_multiwin_probe.py", "tools/package_multiwin_probe.py",
             "tests/test_colab_multiwin_probe.py", "docs/MULTIWIN_TRAINER_PACKAGE_SCOPE.md")

def approved_package(folder):
    # Administrative authority only for this synthetic evidence acquisition.
    # A scientific REVISE is preserved and never upgraded to APPROVE.
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

def build(module, plans, submission, approval_folder):
    approval = approved_package(approval_folder)
    probe.require(probe.sha(submission) == REVIEW_SUBMISSION_SHA, "REVIEW_SUBMISSION")
    record = json.loads(submission)
    verdict = record["submission"]
    probe.require(record["schema"] == "accepted-review-submission/v1"
                  and verdict["verdict"] == "REVISE"
                  and {f["id"] for f in verdict["findings"]} == {
                      "MULTIWIN-REAL-TRAINER-CHECK-NOT-EXECUTED",
                      "EXECUTION-AUTHORITY-HELD-OPPOSING-EVIDENCE-PENDING"}
                  and verdict["bindings"]["call_id"] == REVIEW_CALL
                  and verdict["bindings"]["run_id"] == RUN,
                  "SCIENTIFIC_REVIEW")
    probe.require(probe.sha(module) == probe.MODULE_SHA
                  and probe.sha(plans) == probe.PLANS_SHA, "REVIEWED_BYTES")
    payload = {name: base64.b64encode(raw).decode() for name, raw in
               [("execution.py", module), ("plans.json", plans)]}
    runtime = Path(probe.__file__).read_text()
    cell1 = runtime + "\n\nRESULT = run(" + repr(payload) + ")\n"
    cell2 = "PRIVATE_EVIDENCE_FOLDER = preserve_to_drive()\n"
    intro = """# A1_multiwin: real trainer integration check
Use a **fresh default Colab A100** runtime and click **Run all**. No settings to edit.
The scientific review remains REVISE pending this evidence. This independently approved package runs only that synthetic check; it does not authorize the full training notebook.
This is a synthetic check of the exact scientifically reviewed code, not the five-fold training notebook.
It constructs the actual trainer, runs one real forward/backward/optimizer iteration and verifies checkpoint save/reload.
It does not test the production data loader or establish scientific efficacy.
No Drive mount or real input is used during execution. After the child stops, the final cell asks for your existing Drive login and preserves the declared evidence and checkpoint privately, excluding caches.
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
                       "scientific_review_verdict": "REVISE",
                       "full_training_authorized": False,
                       "packaging_approval_sha256": approval["report_sha256"],
                       "module_sha256": probe.MODULE_SHA, "plans_sha256": probe.PLANS_SHA,
                       "review_submission_sha256": probe.sha(submission),
                       "runtime_sha256": probe.sha(runtime.encode()),
                       "purpose": "synthetic real trainer check; no patient run or efficacy claim"}}
    return (json.dumps(nb, indent=1, ensure_ascii=True) + "\n").encode()
