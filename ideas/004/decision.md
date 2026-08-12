# Probe decision — idea 004 load probe (contract v1)

**Date:** 2026-08-12  
**Decision:** **ADVANCE** — the exploratory load probe satisfied its contract. This
authorizes drafting and seeking separate human approval for the 425-pair floor-study
contract; it does not authorize that bulk run.

## Strict contract result

`probes/004/results/summary.json` reports `contract_satisfied: true`. All three
authorized variants ran, in the preregistered order and with one seed:

| Execution | Input | Result | Time | Peak GPU memory |
|---|---|---|---:|---:|
| `exec1_A` | Br40f `valid_1004_a_1.nii.gz` | 18 finite named scores | 5.21 s | 4.10 GB |
| `exec2_B` | Br60f `valid_1004_a_2.nii.gz` | 18 finite named scores | 4.96 s | 4.10 GB |
| `exec3_A_repeat` | repeated Br40f A | 18 finite named scores, bit-identical to `exec1_A` | 4.81 s | 4.10 GB |

Total recorded GPU time was 0.250 minutes, below the 45-minute cap. Batch size was
one, patch size was unchanged, and no additional pair or seed was run.

## Demonstrates

- The frozen official artifact `CT_LiPro_v2.pt` (SHA-256
  `9246d9c8a7e2cedaa115719699229fe0acb02f19488e8bd1ad1eff5f47ff1d7d`)
  is obtainable and loads with official CT-CLIP code commit
  `a2a155c601987820433c01db69b64d701d3d229d` and CT-RATE revision
  `deeca4d89e9f978d4d1bccd88a55071ddbb146bb`.
- Loading is strict modulo exactly the r6-authorized, provenance-recorded removal of
  `trained_model.text_transformer.embeddings.position_ids`. No other missing or
  unexpected state-dict key was tolerated.
- The released pipeline emits exactly 18 finite scores with a stable recorded
  head-name/order mapping for both members of the selected pair.
- The identical-file A rerun is bit-deterministic in the recorded one-seed
  environment.
- The current pipeline fits the tested A100 compute envelope easily at batch size
  one. These are hard feasibility outcomes and do not depend on estimating an
  effect size, so `DEMONSTRATES` is appropriate despite the single seed.
- The repaired selection logic reproduces all 237 frozen qualifying Br40f|Br60f
  pairs, and the selected pair passes the Stage-0 matching rules.

## Suggests

- The resource cost of model inference itself is unlikely to be the limiting factor
  for the proposed floor study on comparable hardware: each execution took about
  five seconds and used 4.10 GB peak GPU memory. This remains a one-pair observation;
  it does not measure bulk download, preprocessing, session-recovery, or storage
  costs.
- The two reconstructions produce numerically different outputs for all 18 heads in
  this pair (14 lower and 4 higher for B; maximum absolute diagnostic difference
  0.0070026815). Because there is only one pair and one seed, and because the
  contract explicitly classifies A-versus-B differences as diagnostics, this does
  not support a scientific or head-specific conclusion.

## Does not establish

- It does not establish that ClassFine uses reconstruction-dependent
  spatial-frequency content, that any head is reconstruction-sensitive, or that the
  observed differences are systematic. One pair cannot estimate the prespecified
  paired-difference distributions, and the single seed cannot separate a metric
  movement from seed-specific behavior.
- It does not establish equivalence, robustness, accuracy, concept validity,
  localization, clinical reliability, or cross-vendor/site generalization.
- It does not validate the correspondence between these v2 weights and any specific
  published paper table. Attribution remains limited to the “released v2 ClassFine
  checkpoint.”
- Bit-identical A reruns establish software determinism only; they do not rule out
  deterministic preprocessing effects between distinct inputs.
- It does not authorize the 425-pair study, margin selection, threshold fitting,
  AUROC analysis, or confirmatory interpretation.

## Findings

**Positive findings:** Every positive-pattern clause passed: frozen provenance,
strict-compatible load under the enumerated r6 exception, 18 finite named outputs,
bit-identical A repeat, unchanged batch/patch configuration, three completed
executions, and completion far inside the GPU budget.

**Negative findings:** No contract-negative pattern occurred. In particular, there
was no access, hashing, pair-validity, load, output-shape, finiteness, determinism,
memory, crash, or time-cap failure. “Negative” here does not mean scientific
evidence of no reconstruction effect; the probe was incapable of producing such a
result by design.

## Validity failures

None. The `position_ids` removal is not treated as a validity failure because the
2026-08-12 r6 ledger explicitly authorized that single non-learnable framework-era
buffer exception, required it to be exact and provenance-logged, and preserved
strict loading for all other keys. The artifacts show exactly that behavior.

## Next decision

**ADVANCE** to preparation and human review of a new, separate contract for the
425-pair label-free floor study. Before any bulk score is inspected, that contract
must freeze the per-head/per-stratum readout, the three confirmatory contrast strata
(with Br40f|Br44f exploratory), patient-level resampling, score scales, precision
gates, and any externally justified margin. The bulk run requires fresh explicit
human approval. If a later scientific comparison uses stochastic seeds, repeat with
at least three seeds; this load probe itself needs no seed replication because its
passing outcomes are hard pipeline and determinism checks.

