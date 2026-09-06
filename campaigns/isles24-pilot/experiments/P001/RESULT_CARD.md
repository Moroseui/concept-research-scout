# P001 — ready for the first Colab execution

Question: How well does admission Tmax > 6 seconds predict the released
follow-up infarct mask in the frozen eligible 99 development patients?
Baseline: fixed threshold, no fitting. Change: none; this is the campaign baseline.
Data/input timing: admission CT completion; follow-up labels are evaluation only.

Measured result and uncertainty: unavailable — no patient prediction run has
occurred. The registered primary metric is mean patient Dice with a 2,000-resample
patient-bootstrap interval. Synthetic test numbers are not scientific findings.

Independent review: Claude Fable APPROVE at
469d29df002ea78f64146731244769d7c82330d6 (actual response and bound review.json).
SPEC v1.1 explicitly stops on any nonfinite Tmax voxel. Such a failed attempt
would require preserved evidence and a reviewed amendment, not silent imputation.

Limitations: reused development cohort, selection, registration, inherited Tmax
units and unmodeled treatment. Findings will be exploratory, not external or
clinical validation. Private predictions/checkpoints and original console must
be retained; only validated aggregate outputs may enter Git.

Artifacts: SPEC.md, investigator_decision.json, review.json, run.py,
validate_return.py, publication.json and colab_P001.ipynb; execution receipts
will identify the exact verified source pin. No follow-up has been selected.

Next decision: connect a CPU Colab runtime and run the pinned notebook. Validate
the returned bundle and private audit evidence before interpretation and before
selecting one of at most two follow-up comparisons.
