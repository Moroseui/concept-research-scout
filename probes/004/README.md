# Probe — idea 004 (load probe, contract v1)

This directory implements the exploratory load probe defined in
[`ideas/004/probe_contract.yaml`](../../ideas/004/probe_contract.yaml). Human
approval exists as the committed marker `ideas/004/HUMAN_APPROVED_PROBE`
(2026-08-11), and the contract's `human_approved` field is synchronized to
`true`. `run.py` gates on the marker file, which is the human's approval act.

## How to run

```bash
# Harness self-test: synthetic data, stdlib only, no network/GPU, seconds.
# Cannot satisfy the contract; verifies gate, split guards, pair selection,
# per-sample outputs, bit-identity and budget checks.
python3 run.py --smoke

# Install the pinned environment before starting the probe. The driver then
# imports the two released packages directly from its provenance-frozen clone.
python3 -m pip install -r requirements.txt

# Real probe: write artifacts to persistent storage (for example mounted Drive).
# Requires the accepted CT-RATE gate, a logged-in HF token, and a CUDA GPU.
python3 run.py --output-dir /path/on/drive/idea004
```

Exit codes distinguish contract failures from environment failures (see the
`run.py` docstring): 0 pass, 2 gate, 3 access, 4 provenance, 5 checkpoint
load, 6 output shape, 7 pair validity, 8 determinism, 9 budget, 11 missing
dependency/GPU, 10 model/tokenizer access, 12 internal error (never to be reinterpreted as a negative
result). Outputs land in `--output-dir` when supplied, otherwise `outputs/`
(real) or `outputs_smoke/` (smoke):
`resolved_config.json`, `per_sample.csv`, `summary.json`, `environment.txt`,
`provenance.json`, `input_manifest.csv`, `selection_audit.json`,
`run_log.txt`.

The one probe pair is not hardcoded: it is derived deterministically from the
released `validation_metadata.csv` by re-applying the frozen Stage-0 rules
(exact string equality on RescaleSlope, RescaleIntercept, XYSpacing, ZSpacing,
NumberofSlices, plus position/acquisition columns where present), restricting
to the Br40f|Br60f contrast, sorting by the Br40f member's volume name, and
taking the first — selected before any score is inspected. The run stops if
the qualifying count differs from Stage 0's frozen count of 237.

Revision 2026-08-12 (exit-7 root cause, decision ledger): the released
metadata stores `ConvolutionKernel` as a stringified Python list
(`"['Br40f', '3']"`), which the original raw-string predicate matched zero
times. The kernel field is now normalized before comparison (a parsable list
literal takes element 0; anything else uses the stripped raw string — robust
to both formats). Pair selection always writes `selection_audit.json`
(kernel-value tally with counts and example VolumeNames, per-filter drop
counts), and any shortfall against the frozen 237 count also dumps those
diagnostics to `run_log.txt` before the exit-7 stop. `input_manifest.csv`
records each selected volume's normalized and raw kernel from its own
metadata row. Geometry list-string columns compare same-format row-vs-row
and are unchanged.

If the released code's constructor or call signatures differ from the
transcription in `run.py` (taken from `scripts/ct_lipro_inference.py` on
2026-08-11), the probe fails with exit 5/7/9; fix the driver to match the
released code, never the released code to match the driver.

`verification.json` records the local checks done at implementation time; the
sandbox used for implementation could not execute python, so the smoke run is
the human's first step.

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

The authorized run preserves `resolved_config.json`, `per_sample.csv`,
`summary.json`, `environment.txt`, `provenance.json`, `input_manifest.csv`,
and `run_log.txt`, written by `run.py` into `outputs/` (or `outputs_smoke/`
for the harness self-test). They exist only after a run.
