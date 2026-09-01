# Feasibility memo — idea 045

**Question under test:** Does per-patient Q1-minus-Q4 NCCT median-attenuation
imbalance account for idea-023's opposite-signed mean final-infarct contrasts
in flow bands 2 and 3?

Stage run 2026-09-01. This retries the 2026-09-01 attempt that failed on
agent authentication before producing any content (`log_feasibility.txt`;
no partial memo existed). All inspections below were performed fresh.

**Conduct rule adopted for this memo:** the probe contract
(`ideas/045/probe_contract.yaml`, v1, unapproved) is an *outcome-blind*
design audit with frozen thresholds. To keep the approval decision clean,
this memo verified **input structure only**. No value of the outcome column
`d` was read (header presence only), and none of the probe's own gated
quantities — HU-imbalance distribution, design-matrix rank, condition
number, leverage — was computed. Those are the probe's certified
deliverables; computing them before human approval would let the approver
see the outcomes of the gates being approved.

## 1. Keystone inputs: directly inspected, all pass

Everything in this section is **verified fact**, inspected today at
`probes/023/results/results_v2/` (import commit `1c0acdb`, "idea 023:
validated results bundle results_v2 (phase C)").

File identities (SHA-256, recorded for the probe's input manifest):

| file | sha256 |
|---|---|
| bin_tissue_audit.csv | `35e896dfe2a5275a9fa8077e990dff96e72ce1ec0e5048079653556e1c7e2cd2` |
| per_patient.csv | `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c` |
| summary.json | `71418b78caa5a853917b131777ad6fa37f1c1f9c2242d5f1e4fc586fcc8ebfbb` |

Structure, against the contract's row gate:

- `bin_tissue_audit.csv`: header
  `case_id,stratum,style_group,member_voxels,finite_hu_voxels,nonfinite_hu_voxels,median_hu,q25_hu,q75_hu,iqr_hu`;
  594 data rows; **99 distinct cases**; **exactly 99 rows in every one of
  the six (stratum 1/2/3 × Q1_low_CBV/Q4_high_CBV) cells**; zero duplicate
  `(case, stratum, style_group)` keys.
- `per_patient.csv`: header `case_id,stratum,q1_voxels,q4_voxels,d`;
  297 data rows; 99 per stratum; zero duplicate `(case, stratum)` keys.
  The `d` column the contract expects is present in the header; **no `d`
  value was read**.
- **Case sets are identical across the two files** (union of distinct case
  IDs across both = 99), so the join the card's keystone requires is
  bijective on `(case, stratum)` by construction.
- `median_hu` values: 594/594 numeric (no letters, no empty fields, clean
  numeric sort), range **3.0 to 59.0 HU**. The contract's finiteness
  requirement is satisfiable on the real data.
- Exposure variation exists: distinct raw `median_hu` values per
  primary-band cell are 30 (band 2, Q1), 31 (band 2, Q4), 28 (band 3, Q1),
  32 (band 3, Q4) across 99 cases. This does not certify the contract's
  "≥20 distinct HU-imbalance values per band" gate — the imbalance is a
  derived difference and was deliberately not computed — but it makes a
  degenerate-exposure failure unlikely.
- `sub-stroke0043` is absent from both tables and named in
  `exclusions.csv` with reason `source_corrupt_member`, exactly as the
  parent contract's exclusion policy required.
- `summary.json` matches the card's `keystone_evidence`
  transcription-exactly: 99 analyzed of 100 census cases, 49 reserved
  untouched, band-2 mean d −0.0320 CI [−0.0559, −0.0080], band-3 +0.0231
  [+0.0050, +0.0436], band-1 null [−0.0268, +0.0384]. Note the per-band
  **medians are ≈0**, which is why the card's deliverable is correctly
  scoped to equal-patient-weight means.
- Bundle identity: `resolved_config.json` and `summary.json` both carry
  contract/approval blob `03d4545fe293…`; provenance pins Zenodo record
  16813698, archive md5 `36ae28b9…`, seed 20260824.

**Verdict on the card's keystone (`INSPECTED_TRUE`): confirmed.** Joinable,
unique, complete patient-by-band rows exist for both sides of the analysis.

## 2. Closest work and exact gap

- **Closest work is the parent itself.** Idea-023's take-13 census produced
  both input tables under one frozen contract, and its ratified
  interpretation never analyzed their relationship — the label-blind HU
  audit was mandated (2026-08-28 activation directive) precisely so a
  successor could ask this question. The gap is exactly the prespecified
  bands-2/3 imbalance-versus-d attribution analysis. No one else can have
  done it: the audit table's structure (case × CBF-band × CBV-quartile-cell
  median HU) exists only in this bundle.
- **Closest external family: net water uptake (NWU) densitometry.**
  Verified today: Lu et al., AJNR Am J Neuroradiol 2023
  (DOI 10.3174/ajnr.A7741) defines NWU = [1 − (HU_ischemic/HU_normal)] ×
  100 from NCCT and reports elevated NWU associated with malignant edema
  and poor outcome; it cites the foundational Minnerup et al. 2016 study
  (Ann Neurol 80:924–34, DOI 10.1002/ana.24818 — **secondary transcription
  from Lu's reference list, primary not fetched**). This establishes that
  NCCT attenuation is a quantitative, outcome-relevant tissue signal —
  supporting the confound premise — but NWU work measures lesion-versus-
  contralateral attenuation as a prognostic biomarker. Nobody uses
  within-cell HU imbalance to audit a hemodynamic census's sign reversal.
  The delta is clear and the card claims no novelty beyond completing the
  parent's audit (novelty_confidence 2 stands).
- **Alzahrani et al. 2023 (PMCID PMC9855746)** re-verified live today; the
  uncertainty sentence quoted in `keystone_screen.md` is confirmed
  verbatim. **Correction of record:** the PMC page gives the journal as
  *Stroke*, not "Journal of the Belgian Society of Radiology" as the
  keystone screen stated. PMCID, year, and quote are unchanged;
  non-load-bearing.

## 3. Dataset access and license

No new data. Both inputs are in-repo, imported under the record-result gate
(commit `1c0acdb`, operator-executed import of 2026-08-30). The parent
dataset license (ISLES'24, CC-BY-NC-SA-4.0) was verified 2026-08-18 and is
recorded in `evidence/datasets.csv` (idea-023 row); it was **not
re-verified today** — the tables analyzed here are derived aggregates
already committed, so no new license action arises. No DUA, no download,
no gated access, no annotation campaign.

## 4. Labels and concept validity

- **X is annotator-free**, per the charter's hard constraint: Q1−Q4 median
  HU per case-band, computable from the released label-blind audit by
  subtraction.
- **The outcome side is frozen**: per-case d from the parent census
  (final-infarct masks via DeepISLES with neuroradiologist-supervised
  correction, documented provenance — prior verification on the idea-023
  datasets row).
- **Concept validity limit stands as the card states it**: median HU is a
  composition *proxy* (mixture of normal brain, early ischemic
  hypodensity, partial-volume CSF); Alzahrani 2023 bounds any temptation
  to read it as viability. The card's `keystone_residual_assumption`
  (median-HU sensitivity) is honest and remains **unverifiable in
  advance** — it is what the analysis measures.

## 5. Sample structure and split unit

99 patients × 2 primary bands = 198 analysis rows; patient is the cluster
unit (bootstrap and leverage accounting). There is deliberately no
train/test split: this is exploratory successor-design evidence on
outcomes opened by the parent, with the model form, primary bands, and
interpretation rule frozen in the card before any new aggregate is
computed. The 49 reserved cases are physically absent from both input
tables, so the probe cannot touch them even in error.

## 6. Existing code, checkpoints, compute

No model, no checkpoint, no GPU (`maximum_gpu_minutes: 0`). The probe is a
deterministic CPU join-and-diagnostics pass over two small CSVs (37 KB and
14 KB); the later scientific analysis is one OLS fit with a patient
bootstrap. Compute estimate: **minutes of laptop CPU end to end**. The 023
probe-harness conventions (input manifests, resolved config, run logs)
carry over directly.

## 7. Baselines and metrics

The probe's baseline is algebraic: a full-rank (rank-4) design. Its frozen
feasibility thresholds (condition number ≤30 after diagnostic scaling, max
leverage ≤0.20, ≥20 distinct imbalance values per band, leave-one-patient-
out stability) are conservative conventions, declared as such in the
contract, not medical claims. For the eventual scientific stage the
estimator (equal-patient-weight band contrasts, patient-cluster bootstrap)
mirrors the parent's accepted conventions, so no new metric machinery is
needed.

## 8. Critical leakage and confounds

1. **Opened-outcome reuse** — the live one. Band-level directions, means,
   CIs, and four individual per-case d values (quoted in `critique.md`)
   are on the record and in designers' context. The card handles this
   honestly: exploratory classification, frozen decision rule, no
   confirmatory census claim. This memo added no exposure: no d value read,
   no new aggregate formed.
2. **Severity as common cause** — stroke severity could drive both HU
   imbalance and d. Not ruled out by design; the card prohibits causal
   claims and the deliverable says "associated / consistent with
   contributing," which is the correct strength.
3. **CSF partial volume vs early ischemic hypodensity** — median HU cannot
   separate them; both directions of contamination were observed
   qualitatively in the critique's row-level reading. The card's
   composition-proxy wording absorbs this.
4. **Mean-vs-median fragility** — parent band medians ≈0, so any
   association found is a property of the mean contrast, potentially
   driven by a patient minority. The probe's leverage gates and the
   card's equal-patient-weight scoping are the right guards.
5. **Design-freeze integrity** — the remaining leak channel is this stage
   itself; handled by the conduct rule in the preamble.

Standing acquisition confounds (scanner, protocol, reconstruction, site,
positioning) are moot within-case as the card states; they bound
transportability, not validity, and the card's scope already says so.

This idea involves **no data manipulation, editing, perturbation, or
synthesis** — it is a conditional-observational join of two frozen tables —
so the prior-art-for-interventions subsection required for such designs
does not apply.

## 9. Smallest probe of the riskiest assumption

The riskiest still-unverified assumption is that the **actual exposure
geometry supports the frozen interaction model**: rank-4 design, acceptable
conditioning, no domination by a few patients, real within-band imbalance
variation. File joinability (verified) does not establish this.
`probe_contract.yaml` v1 is precisely and only this check — outcome-blind,
single variant, deterministic, zero GPU. Feasibility endorses it
**unchanged** and recommends it proceed to human approval.

## 10. Marked unverified

- Minnerup 2016 bibliographic details (secondary, via Lu 2023).
- ISLES'24 license status as of today (prior verification 2026-08-18).
- HU-imbalance distribution, design conditioning, leverage — deliberately
  unmeasured; the probe's job.
- Median-HU sensitivity as a composition proxy — residual assumption,
  answerable only by the analysis itself.
- Minor observation, out of 045's scope: bundle `provenance.json` records
  `archive_member_count: 2981` while the 2026-08-25 ledger entry cited
  2983 archive members; the parent bundle passed validation and
  ratification, and 045 consumes only the two tables, so this is noted
  for the record, not raised as a blocker.

## Verdict

**GO.** Every input the probe contract names exists, is identity-pinned,
and passed structural inspection today; the analysis costs minutes on a
CPU; the honest epistemic limits (exploratory status, proxy validity,
sensitivity-limited nulls) are already written into the card and contract.
The next act is the human approval gate on `probe_contract.yaml` v1.

## In plain terms

This study can definitely be run: both data tables it needs are already in
the repository, they line up row-for-row exactly as required, and the whole
analysis is a small statistical computation that takes minutes on an
ordinary computer — no downloads, no GPU, no permissions. The biggest
practical risk is not access or cost but interpretability: the patients'
outcome data was already examined in the parent study, so this analysis
can suggest but never prove that tissue composition explains the earlier
contradictory result, and a null answer may simply mean the chosen
measurement was too blunt. A small pre-check (already drafted, awaiting
human approval) will confirm the numbers have enough spread to support the
planned model before any outcome value is looked at.
