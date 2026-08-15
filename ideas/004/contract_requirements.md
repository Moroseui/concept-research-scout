# Contract requirements — idea 004, contract v2 (425-pair study)

**Status:** human-authored requirements, reviewed and committed by the
operator. Authorized by: the 2026-08-11 pins as amended 2026-08-14
(pin 2), the 2026-08-12 ADVANCE, and the A1 ratification of the
CT-Scroll context memo (blob 6668a313ae83779ef2a74d1982dd287d504a7e0d).
The contract drafted from these requirements is `probe_contract.yaml`
with `contract_version: 2`, superseding the executed v1 load-probe
contract (preserved in git history and in the PROBED ledger record).
Every requirement below is binding; the reviewer checks conformance
line by line.

## R1. Scope and manifest

- Exactly the frozen Stage-0 pair list: 425 geometry-matched pairs
  (Br40f|Br60f 237, Bl56f|Br40f 126, Bl57d|Br36d 58, Br40f|Br44f 4).
  No additions, no substitutions.
- The contract materializes the pair list as `pair_manifest.csv`
  (pair id, patient id, both VolumeNames, stratum, normalized kernels)
  and records its SHA-256 in the contract. The analysis population is
  the manifest byte-for-byte, not the counts.
- The unique-volume count is computed from the manifest and recorded in
  the contract; 425 x 2 is not assumed.
- The Br40f|Br44f stratum (4 pairs) is exploratory only and excluded
  from every confirmatory statement.
- Vendor scope (462/464 Siemens) stated as a limitation in the
  contract's claim language.

## R2. Canonical sign direction

- One canonical direction per stratum, defined explicitly in the
  contract BEFORE any score is seen, with the rule stated (e.g.
  sharper-minus-softer with the ordering justified from kernel naming,
  or a stated lexicographic convention). Pair ordering in the data may
  never determine sign.

## R3. Tier 1 (primary, label-free)

- Per-head (18) x per-stratum signed paired score differences on BOTH
  probability and logit scales.
- Empirical absolute-difference quantiles per head per stratum.
- Patient-cluster bootstrap confidence intervals: the patient is the
  resampling unit (patients contribute multiple scans).
- NO cross-head averaging anywhere in any tier-1 statistic.
- The term "repeatability coefficient" and its machinery are not used:
  these are intentionally different conditions, not repeated identical
  measurements.

## R4. Tier 2 (secondary, descriptive; amended pin 2)

- Per-head paired delta-AUROC against CT-RATE's released
  RadBERT-derived validation labels, with patient-cluster bootstrap
  intervals.
- ZERO threshold language: no margin, cutoff, "meaningful", "material",
  or pass/fail semantics anywhere in tier 2. Context for magnitude is
  the ratified memo's arXiv-v6-pinned values (spread 2.61, adjacent
  gaps 0.18-1.53), cited by memo blob hash, with these inherited
  caveats stated in the contract: 18-label-average vs per-head
  aggregation mismatch; 0-100 vs [0,1] scale conversion; the memo's
  seed-variance-vs-sampling-variance non-comparability; the v6 ViViT
  Table-1/Table-2 inconsistency for ViViT-involved gaps; framing as
  benchmark discrimination against report-derived labels, never
  clinical accuracy.
- Preregistered sparse-label rule: minimum positive AND negative counts
  per head per stratum for AUROC computation, and how excluded
  head-stratum cells are reported, fixed in the contract before any
  score is seen.
- Tier 2 runs only if tier 1 completes.

## R5. Environment (r6 closure)

- transformers 4.38.2 / tokenizers 0.15.2 pinned; exactly the single
  enumerated `*.embeddings.position_ids` buffer key removed and
  provenance-logged; any other unexpected or missing key is a hard
  failure. Startup logs all installed versions.
- Checkpoint identity: CT_LiPro_v2.pt by recorded SHA-256 under the
  pinned CT-CLIP commit; attribution language per pin 4 (released v2
  ClassFine checkpoint).

## R6. Selection (r5 closure)

- Kernel-field normalization: parse list-literal, take element 0, else
  stripped raw string.
- On any shortfall vs the frozen manifest: diagnostic audit (top-10
  kernel values with counts, example VolumeNames, per-filter drops) to
  the run log AND selection_audit.json; shortfall without a matching
  audit is invalidating.
- Normalized kernel recorded per volume in input_manifest.csv.

## R7. Execution model

- Chunked download -> preprocess -> infer -> delete, chunk size stated
  and sized to Colab Pro+ disk.
- Per-chunk manifest with input-file SHA-256 hashes, committed before
  the next chunk begins; an interrupted chunk is redone in full.
- Both members of every pair run in the SAME session/environment.
- Per-chunk environment record: GPU model, CUDA and PyTorch versions,
  package versions, session identifier.
- Anchor pair: the v1 load-probe pair (scores already exposed and
  declared uninterpretable) re-run at every session start as a drift
  detector, excluded from all scientific counting. Within-session
  repeat: bit-identical. Cross-session anchor: a numerical tolerance on
  logits/probabilities, its value fixed in the contract before bulk
  execution, with the rationale (hardware may differ across sessions;
  same-session pairing is the load-bearing protection).
- The launcher notebook is a thin driver: it clones, installs pinned
  requirements, and runs run.py as a subprocess; it never imports the
  model stack into its own kernel (no restart may exist in the
  workflow).

## R8. Budgets

- Caps expressed in volumes processed and sessions, not GPU minutes.
- Three separate frozen numbers: pair count (425), unique-volume count
  (from the manifest), and a QA/retry download allowance covering
  redone chunks and anchor re-runs. A single total-download cap is
  incoherent under resumability and is not used.

## R9. Determinism and stopping

- Preregistered within-session spot-check subset (stated in the
  contract, e.g. first pair of each stratum), re-run bit-identical.
- Invalidating failures, enumerated v1-style and each distinct from a
  negative outcome: provenance mismatch, selection shortfall without
  audit, spot-check non-determinism, environment drift, anchor drift
  beyond the preregistered tolerance.

## R10. Outputs

- The v1 output set, plus: pair_manifest.csv (hash-recorded), per-chunk
  manifests, per-chunk environment records, input_manifest.csv,
  selection_audit.json when triggered, and a results-bundle layout
  (documented in the contract) that the interpret stage and a
  deterministic validator can both consume.
- The contract cites: this requirements file, the pin-2 amendment, the
  A1 ratification entry, and the context memo blob hash.

## R11. Claim discipline

- The result is a reconstruction-sensitivity baseline for this
  checkpoint on these contrasts, vendor-scoped; not a universal
  measurement floor, and no artifact may state the universal-threshold
  interpretation.
- The one-pair diagnostic exposure and its non-compromise argument
  (memo section 4) are restated in the contract's assumptions.
