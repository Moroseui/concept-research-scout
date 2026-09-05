# P001 — awaiting review and real Colab execution

Question: How well does admission Tmax > 6 s predict follow-up infarct?
Baseline: fixed threshold without fitting. Change: none; this is the baseline.
Data/input timing: frozen eligible 99 development cases; admission Tmax only.
Measured result and uncertainty: **not available — no real run has occurred**.
Synthetic tests validate software behavior, not predictive performance.
Limitations: exploratory reused development cohort, treatment dependence,
registration and units. No generalization or clinical claim.
Artifacts: SPEC.md, investigator_decision.json, run.py, requirements.txt.
Next decision: opposing-family review of spec/code, then operator Run All in
Colab. At most two follow-ups may be registered after returned evidence is read.
