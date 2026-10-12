"""Private packaging of exact already-reviewed pnormct scientific bytes."""
from pathlib import Path
import base64, hashlib, json
from tools import colab_pnormct_probe as probe

REVIEW_CALL = "35b8c89569791e3c11791b026bac1a0500bf3f08d4b5708068f0dbe6b1daacae"
RUN = "colab-arm-22cf228b71bc3d1441ef2031"
REVIEW_SUBMISSION_SHA = '1a4871fec98f47fa2b0f08e754f34ec8c6cb38a48ff2d72043167bf17ca77b12'

def build(module, plans, submission):
    probe.require(probe.sha(submission) == REVIEW_SUBMISSION_SHA, "REVIEW_SUBMISSION")
    record = json.loads(submission)
    verdict = record["submission"]
    probe.require(record["schema"] == "accepted-review-submission/v1"
                  and verdict["verdict"] == "APPROVE" and verdict["findings"] == []
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
    intro = """# A1_pnormct: real trainer integration check
Use a **fresh default Colab A100** runtime and click **Run all**. No settings to edit.
This is a synthetic check of the exact scientifically reviewed code, not the five-fold training notebook.
It constructs the actual trainer, runs one real forward/backward/optimizer iteration and saves a checkpoint.
It does not test the production data loader or checkpoint reload.
No Drive mount or real input is used during execution. After the child stops, the final cell asks for your existing Drive login and preserves all evidence privately.
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
                       "module_sha256": probe.MODULE_SHA, "plans_sha256": probe.PLANS_SHA,
                       "review_submission_sha256": probe.sha(submission),
                       "runtime_sha256": probe.sha(runtime.encode()),
                       "purpose": "synthetic real trainer check; no patient run or efficacy claim"}}
    return (json.dumps(nb, indent=1, ensure_ascii=True) + "\n").encode()
