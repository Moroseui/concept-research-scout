# Probe plan — idea 004

This directory is reserved for the exploratory load probe defined in
[`ideas/004/probe_contract.yaml`](../../ideas/004/probe_contract.yaml). No probe
code has been implemented and no execution is authorized while
`human_approved: false`.

## Purpose

The probe tests only the remaining load-bearing feasibility assumption: whether
the officially released `CT_LiPro_v2.pt` checkpoint can be frozen by hash, loaded
unchanged with the released CT-CLIP inference path, and made to emit 18 finite,
deterministic ClassFine scores for one Stage-0-approved validation pair.

It is not the 425-pair reconstruction-sensitivity study. The A-versus-B score
difference is logged solely to confirm that paired outputs can be produced. It
must not be used to choose heads, margins, thresholds, transformations, or later
analysis variants.

## Authorized shape after human approval

- Data: one predeclared geometry-matched `Br40f|Br60f` validation pair.
- Executions: reconstruction A, reconstruction B, then reconstruction A again.
- Model: the official v2 ClassFine artifact identified by the CT-CLIP README,
  with its Hugging Face revision and SHA-256/LFS identity recorded.
- Pipeline: released preprocessing and architecture, batch size 1, with no patch-
  size, target-shape, weight, or model-structure changes.
- Budget: one seed, at most three executions, at most 45 cumulative GPU minutes.

The identical-file rerun tests software determinism only. It does not establish
that preprocessing is harmless and does not support a reconstruction-content
claim.

## Decision rule

The probe passes only if the artifact and inputs have recorded provenance, the
checkpoint loads unchanged, all three executions return exactly 18 finite scores
with a stable name/order mapping, the repeated-A result is bit-identical, and the
run stays within the compute cap.

Access, provenance, compatibility, output-shape, pair-validity, determinism,
memory, crash, and budget failures are invalidating failures as enumerated in the
contract. Conversely, an A-versus-B difference of any size—including zero—is not
a negative result; one pair cannot answer the scientific question.

Passing this probe does not authorize bulk inference. The 425-pair floor study
requires a separate contract and fresh explicit human approval. Before that later
study, its primary per-head × per-stratum readout must remain unpooled, and any
label-dependent AUROC tier must have its CT-Scroll-derived margin frozen from the
paper tables before paired scores are inspected.

## Expected artifacts

The eventual authorized run must preserve `resolved_config.json`,
`per_sample.csv`, `summary.json`, `environment.txt`, `provenance.json`,
`input_manifest.csv`, and `run_log.txt`. These files do not exist yet because this
stage creates a plan only.
