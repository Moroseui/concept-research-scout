# Probe — idea 004

This directory holds the probe artifacts for idea 004. Two contracts exist:

- **Contract v1** (load probe): executed and **PASSED 2026-08-12**. Its code
  (`run.py`, `requirements.txt`, `colab_probe_004.ipynb`) and outputs
  (`results/`, `outputs_smoke/`) remain in this directory as the frozen v1
  record.
- **Contract v2** (the 425-pair floor study):
  [`ideas/004/probe_contract.yaml`](../../ideas/004/probe_contract.yaml)
  with `contract_version: 2`, drafted 2026-08-14 from the human-authored
  requirements file
  [`ideas/004/contract_requirements.md`](../../ideas/004/contract_requirements.md).
  **No v2 code exists yet.** The v1 `run.py` implements contract v1 only and
  must not be used for the floor study.

## Contract v2 status and approval flow

The v2 contract supersedes v1 in `ideas/004/probe_contract.yaml` (v1 is
preserved in git history and in the PROBED ledger record). Approval is
hash-bound: `HUMAN_APPROVED_PROBE` records the contract's git blob hash, and
the probe-code gate blocks on any mismatch. The marker currently in
`ideas/004/` is bound to the superseded v1 blob, so it correctly authorizes
nothing for v2.

The v2 execution is phased, and the phasing is part of the contract:

1. **Approval #1** (`python scout.py approve-probe 4` against the drafted
   contract) authorizes **Phase M only**: a metadata-only manifest freeze
   that re-derives the 425 frozen Stage-0 pairs from the pinned
   `validation_metadata.csv`, hard-gates on the exact stratum counts
   (237/126/58/4), and writes `pair_manifest.csv` plus a selection audit.
   No image download, no inference, no scores.
2. The operator records the manifest SHA-256 and the manifest-derived
   unique-volume count in the contract (replacing the
   `TO_BE_RECORDED_AT_MANIFEST_FREEZE` placeholders). This amendment changes
   the contract blob, so the Phase-M approval goes stale by construction.
3. **Approval #2** (re-run `approve-probe`) binds to the amended blob and
   authorizes **Phase B**: chunked bulk inference over the manifest
   (17 chunks × 25 pairs, download → hash-verify → preprocess → infer →
   delete), followed by the frozen two-tier analysis.

Any Phase B activity while a placeholder remains, or without a marker bound
to the amended blob, is an invalidating failure under the contract.

## What contract v2 measures

- **Tier 1 (primary, label-free, confirmatory):** per-head (18) ×
  per-stratum signed paired score differences on probability and logit
  scales, with |Δ| quantiles and patient-cluster bootstrap intervals. No
  cross-head averaging anywhere. The Br40f|Br44f stratum (4 pairs) is
  exploratory only.
- **Tier 2 (secondary, descriptive, runs only if tier 1 completes):**
  per-head per-stratum paired ΔAUROC against the released report-derived
  validation labels, with a preregistered sparse-label eligibility rule
  (≥10 positive and ≥10 negative pairs per cell) and a mandatory
  excluded-cell table. Zero threshold language, per the 2026-08-14
  amendment to pin 2: benchmark numbers from the ratified CT-Scroll context
  memo (git blob `6668a313ae83779ef2a74d1982dd287d504a7e0d`) are context
  only and carry no pass/fail semantics.

Execution safeguards: the v1 pair (`valid_1004_a_1|a_2`) runs as a
session-start anchor with within-session bit-identity and a preregistered
cross-session tolerance (≤1.0e-4 max per-head probability deviation against
the v1 reference scores, `results/per_sample.csv` @ git blob
`ea1cdd3fb463cafa9c1f7bc7ec048d2c7c320cc1`); its deltas are excluded from
all confirmatory statistics. Both members of every pair run in the same
session; interrupted chunks are redone in full. Budgets are capped in
volumes and sessions, not GPU minutes (425 pairs; unique-volume cap fixed at
manifest freeze; QA/retry allowance of 20% of unique volumes; 30 sessions).

The result, whatever its magnitude, is a reconstruction-sensitivity
baseline for the released v2 ClassFine checkpoint on these contrasts, in a
predominantly Siemens cohort. It is not a universal measurement floor, not
an equivalence claim, and not evidence about concept validity, accuracy, or
clinical reliability.

## Contract v1 record (executed, PASSED 2026-08-12)

The v1 load probe tested only the load-bearing feasibility assumption:
whether the officially released `CT_LiPro_v2.pt` checkpoint could be frozen
by hash, loaded unchanged with the released CT-CLIP inference path (modulo
exactly one provenance-logged `*.embeddings.position_ids` framework-era
buffer key, per the r6 ledger decision), and made to emit 18 finite,
bit-deterministic ClassFine scores for one Stage-0-valid Br40f|Br60f pair
at batch size 1. All contract gates passed in 0.250 GPU minutes at 4.10 GB
peak; see `results/summary.json` and `ideas/004/decision.md`. The one-pair
A-versus-B differences are diagnostics, declared scientifically
uninterpretable by the v1 contract.

v1 operational notes retained for the v2 implementation (full history in
git and the decision ledger):

- **Kernel normalization (r5):** the released metadata stores
  `ConvolutionKernel` as a stringified Python list (`"['Br40f', '3']"`); a
  parsable list literal takes element 0, anything else uses the stripped
  raw string. Selection always writes `selection_audit.json`; any shortfall
  against frozen counts also dumps diagnostics to the run log before
  stopping.
- **Environment (r6):** `transformers==4.38.2` / `tokenizers==0.15.2` (the
  authors' 2023 pin is uninstallable on Colab Python 3.12). Exactly one
  state-dict key matching `*.embeddings.position_ids` is removed before
  strict loading and logged to `provenance.json`; any other unexpected or
  missing key is a hard failure.
- **Harness:** `python3 run.py --smoke` self-tests the v1 harness with
  synthetic data (stdlib only, no network/GPU); it cannot satisfy any
  contract. The launcher notebook is a thin driver that runs `run.py` as a
  subprocess and never imports the model stack into its own kernel.
- If released-code signatures differ from the driver's transcription, fix
  the driver to match the released code, never the reverse.

## Next steps

1. Operator reviews the v2 contract draft, including its two flagged open
   questions (the two-approval reading of R1, and the anchor-pair exclusion
   from confirmatory counting).
2. `approve-probe` (approval #1) → probe-code stage implements the v2
   driver → Phase M manifest freeze.
3. Contract amendment with the manifest hash and unique-volume count →
   `approve-probe` (approval #2) → Phase B bulk run → interpret stage
   consumes `probes/004/results_v2/`.
