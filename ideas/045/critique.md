# Critique — idea 045 (Tissue-normalized joint CBV/MTT compensation at matched flow)

```
FATAL OBJECTION: NONE
EVIDENCE: Leading repairable defect: the card's own motivating rows (bin_tissue_audit.csv
joined against per_patient.csv) do not show the simple tissue-inflation story, and the card
prespecifies no Rung-0a -> Rung-0b decision rule, so the census could run on a premise 0a refutes.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

---

## 1. What was verified before writing this critique

All claims below were checked against the imported take-13 bundle at
`probes/023/results/results_v2/` (import commit `1c0acdbf5dcc…`), the ratified
interpretation `ideas/023/interpretation.md`, and `ideas/023/confer/q0002.md`.

- **Verified fact:** the 594-row `bin_tissue_audit.csv` exists with the stated
  case × band × cell structure; `summary.json` records
  `bin_tissue_audit_rows: 594`, `analyzed_census_case_count: 99`,
  `status: NEGATIVE_PATTERN`, split manifest sha256 `da79e94b…`, reserved
  count 49.
- **Verified fact:** the band statistics quoted in the card's
  `keystone_evidence` are transcription-exact against
  `per_stratum_summary.csv` (band 1 mean d +0.0064 CI [−0.0268, +0.0384];
  band 2 −0.0320 [−0.0559, −0.0080]; band 3 +0.0231 [+0.0050, +0.0436]) and
  `identity_residual_summary.csv` (MAD 0.0078/0.0036/0.0078).
- **Verified fact:** the cited hypodense-Q1 examples are real rows
  (sub-stroke0092 band 1: Q1 median 3.0 HU vs Q4 23.0; sub-stroke0057: 5.0 vs
  24.0; sub-stroke0189: 6.0 vs 25.0).
- **Verified fact:** confer q0002 `SUGGESTED UPDATES` item 4 contains the
  question sketch the card adopts, and `q0002_review.md` records
  `{"verdict":"CONCUR","findings":[]}`. The kernel-provenance claim is
  accurate.
- **Verified fact:** registration as a NEW candidate with `parent_ids:
  ["idea-023"]` complies with the 2026-08-10 claim-identity rule; the
  deliverable sentence differs from the parent's, so revision-in-place would
  have been wrong and was correctly not attempted.
- **Verified fact:** the keystone screen honestly returns `UNVERIFIABLE`; the
  feasibility/novelty caps therefore stand. As a Mode C card this is
  charter-expected, not a defect.

No fatal objection was found in data access, compute, leakage of new labels,
or prior-work overlap. The objections below are ordered by severity; all are
repairable inside the card's existing question.

## 2. Objection 1 (leading): the tissue-confound premise is attributed to the wrong band, and nothing forces Rung 0a to adjudicate it

The parent's decisive negative was the **band-2/band-3 opposite-signed
reversal** (both CIs excluding zero). Band 1 — where the card's three
motivating hypodense-Q1 examples live — was the null band (CI includes zero).
The card's `revival_basis` builds its case almost entirely on band-1 rows and
then proposes to fix the reversal that happened elsewhere.

Row-level inspection (no aggregate computed; that remains Rung 0a's governed
deliverable) makes this worse for the simple story:

- The three cited hypodense-Q1 band-1 cases have per-case band-1 d of
  **−0.0089** (sub-stroke0092), **−0.0051** (sub-stroke0057), and **−0.1404**
  (sub-stroke0189) in `per_patient.csv`. If frank hypodensity in Q1 meant
  "established injury inflating Q1 infarct membership," these d values should
  be strongly positive. They are near zero or **negative** — more consistent
  with the hypodense voxels being partial-volume CSF that *dilutes* Q1
  membership than with injury that inflates it.
- sub-stroke0183 shows the reverse imbalance (band 2: Q1 23.0 HU vs Q4 5.0 HU)
  with band-2 d = **+0.2405** — against the band-2 negative mean, again
  consistent with hypodense-cell dilution, in the opposite cell.

So the audit rows do support "tissue mixing corrupts the contrast in
case-dependent directions" (which also fits the parent's mean-vs-median
divergence), but they do **not** support a single-direction contamination
mechanism, and whether tissue imbalance *accounts for* the band-2/3 reversal
is at present pure inference. The card's honesty about not computing
prevalence is commendable, but honesty is not a design: as written, Rung 0a
measures only **prevalence and magnitude** of imbalance, and no decision rule
connects its outcome to whether the expensive Rung-0b census runs. A Rung 0a
showing low prevalence — or showing imbalance uncorrelated with d in bands 2
and 3 — would refute the successor's premise, yet the card would still
authorize proceeding.

**Repair (stays within the question):**

1. Extend Rung 0a beyond prevalence to a prespecified **imbalance-versus-d
   attribution analysis**: per case and band, join Q1−Q4 median-HU imbalance
   (`bin_tissue_audit.csv`) against per-case d (`per_patient.csv`), bands 2
   and 3 primary. Declare it label-touching (per_patient d is
   outcome-derived) — defensible because these labels were already opened for
   exactly these cases under the parent contract, but it must be walled off
   as exploratory successor-design evidence, never confirmatory.
2. Prespecify the 0a→0b rule now: if imbalance neither reaches material
   prevalence nor associates with d in the reversal bands, the tissue
   explanation is refuted and Rung 0b does **not** run — the lineage goes
   terminal under the card's own "taste is not grounds for a third
   operationalization" rule. Write the thresholds before the aggregate is
   seen.

## 3. Objection 2: the confirmatory census reuses a split whose outcome structure is already known

Rung 0b runs "on the released 100-case census split only." Those are the same
99 analyzed cases whose band-level outcome structure, per-case d values, and
per-case HU audit rows are now on the record and in every designer's context.
The parent could claim a genuine label freeze; this successor cannot. The
card's phrase "both label-blind at design time" overstates what is available:
the *window* can be frozen before new label access, but the designers already
know which direction each band leaned.

This is not fatal — the analysis form is inherited frozen, patient-level
voxel-outcome structure was never exposed, and burning the 49 reserved cases
on a Stage-0 association question would likely be underpowered and spend the
lineage's only pristine holdout. But it must be handled, not elided:

**Repair:** (a) the card must acknowledge the reuse explicitly and state why
the confirmatory reading survives (single new degree of freedom, externally
pinned); (b) the NCCT viability window must be pinned to a **citable external
source** (published HU threshold for brain tissue / early ischemic
hypodensity), not chosen by the team, and frozen **before** the
label-touching Rung-0a join is run — the sequence must be: freeze window →
Rung 0a → decision rule → Phase-S → census; (c) the reserved 49 cases stay
untouched, as the card already states.

## 4. Objection 3: the gate can manufacture its own "decisive" negative by removing the outcome

Admission-NCCT frank hypodensity is a strong predictor of final-infarct
membership (it is the substrate of early-ischemic-change scoring). Excluding
frankly hypodense voxels therefore preferentially removes voxels that would
have carried the outcome label. If post-gate cells retain little final-infarct
membership at all, d collapses toward zero with narrow bootstrap CIs — and the
preregistered conjunction would report a "decisive negative" that actually
means "the gate deleted the outcome variance." Phase-S cannot catch this: it
is outcome-blind by design and sizes voxel support and CI width, not retained
outcome prevalence.

**Repair:** preregister a non-gating per-band, per-cell **post-gate
final-infarct prevalence descriptor** in the census output, plus a frozen
floor (set before the census, justifiable from the parent's already-opened
label aggregates) below which the negative is downgraded from "decisive,
conditional" to **sensitivity-limited**. This classification fork must be
written into the contract now; deciding it at interpretation time would be
exactly the implicit-margin failure the 2026-08-14 amendment exists to
prevent.

## 5. Lesser findings

- **`design_template` mislabel.** "counterfactual-synthesis" is wrong:
  nothing is synthesized or edited; this is a conditional-observational
  census with a voxel-admission filter. The homogenization watch counts these
  strings; mislabeling corrupts that telemetry. Relabel.
- **Mode C designation is strained but acceptable.** This is really a
  confirmatory Stage-0 association study inheriting proven machinery, not a
  speculative mechanism hunt; but the parent was registered the same way and
  the mode's honest NOT_INSPECTED reporting is being used as intended.
- **"Directionally stable association" wording.** The gate is mean-based
  while the parent's median patient showed ≈0 contrast in every band. A
  passed conjunction driven by a patient minority would still be announced as
  a "directionally stable… association." The card's non-gating median
  descriptor is the right instrument; the deliverable sentence should scope
  itself to equal-patient-weight means so the positive cannot be read as
  cohort-typical.
- **Prior work.** HU-window brain-tissue masking is standard CTP
  preprocessing (vendor pipelines routinely exclude CSF/bone by HU), and the
  card already disclaims novelty of the gate concept. The citable object here
  is the governed, preregistered attribution analysis of a label-blind tissue
  audit — modest but real. No overlap kill. The Alzahrani et al. (2023)
  uncertainty about NECT viability discrimination, quoted in the keystone
  screen, bounds interpretation of the gate (it separates *attenuation
  classes*, not certified viability) and the card should say "viable-
  attenuation" everywhere it currently says "viable tissue" — the deliverable
  sentence already does this correctly.
- **plain_pitch.** The card carries none, so the plain-pitch fidelity check
  is N/A. No defect; noting for the record that the deliverable sentence is
  dense enough that a pitch will eventually be needed, and translating
  "establishing, or decisively refusing, the Stage-0 prerequisite" without
  overclaiming will take care.
- **Confound checklist (charter-standing alternatives).** Scanner, vendor,
  protocol, reconstruction, site: moot within-patient and single-pipeline
  (icobrain cva), scope-limited as the card states. Positioning/habitus:
  absorbed by within-patient design. Referral/prevalence: treated-cohort
  scope stands. Label leakage: no new labels are read before the frozen
  census; the real leakage risk is the reused split (Objection 2) and the
  gate-outcome coupling (Objection 3), both named above.
- **Duplicate-work guard.** The separately pre-registered patient-level
  clinical-outcome join (2026-08-28 ledger entry) is adjacent, already
  authorized, and not this card's job; the revision should state it neither
  depends on nor duplicates it.

## 6. Scores check (Mode C weighting)

Scores were operator-withheld in this view; only structural checks are
possible. The keystone screen's `UNVERIFIABLE` verdict caps feasibility and
novelty_confidence at 3 — the card must respect that at merge.
`negative_result_value` as claimed ("decisive, conditional") is only
defensible **after** the Objection-4/§4 prevalence fork is added; without it,
the honest classification of a post-gate null is sensitivity-limited, which
caps that score at 2 under the rubric.

---

## Constructive close

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does per-case Q1-vs-Q4 NCCT attenuation
imbalance statistically account for the parent census's opposite-signed band-2/band-3
final-infarct contrasts — i.e., was idea-023's negative a tissue-composition artifact?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it is Rung 0a of this card, properly
specified with a prespecified 0a->0b decision rule.
IS IT ACTUALLY WORTH DOING? Yes — minutes of CPU on two already-imported CSVs decides
whether the recalibrated census is justified at all, and either answer is
decision-grade for the lineage.
```

The genuinely valuable object in this card is small and already paid for: the
594-row audit and the per-case d table sit in the same imported bundle, and
joining them answers whether the successor's premise is true before any new
staging, Phase-S run, or census take is bought. The revision should promote
that join into Rung 0a's core, freeze the externally-sourced HU window before
running it, write the 0a→0b and negative-classification forks now, fix the
template label, and proceed. If Rung 0a refutes the tissue explanation, the
card's own terminality rule should be allowed to execute — that outcome would
itself be a clean, citable close to the 023 lineage, not a failure of this
candidate.
