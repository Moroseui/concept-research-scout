# Critique — Idea 040: The pressure history written in a winding artery

```
FATAL OBJECTION: The card measures tortuosity on bilateral MCA (M1) and basilar arteries in a cohort where every patient has an acute large-vessel occlusion at CTA time and inclusion required successful thrombectomy (TICI 2b/3) — so the measured segment is frequently the occluded one, the inclusion gate selects against high tortuosity, and tortuosity's established effect on thrombectomy difficulty supplies a rival mechanism the card never names.
EVIDENCE: arXiv 2408.10966v2 ("inclusion criteria of the ISLES'24 dataset were restricted to patients with favorable recanalization outcomes (i.e., thrombolysis in cerebral infarction -TICI- scores 2B and 3)"); systematic review of tortuosity vs. thrombectomy outcomes (ScienceDirect S0303846725003907); ICATI definition = mean TI of right/left MCA M1 + basilar (PMC5836575).
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

---

## 1. What was verified for this critique (and how it was classified)

**Verified fact (primary-source quote).** The ISLES'24 challenge paper states:
"the inclusion criteria of the ISLES'24 dataset were restricted to patients
with favorable recanalization outcomes (i.e., thrombolysis in cerebral
infarction -TICI- scores 2B and 3)" and that findings "do not capture brain
tissue evolution in patients with poor recanalization outcomes or those who
did not undergo thrombectomy."
Source: [arXiv 2408.10966v2](https://arxiv.org/html/2408.10966v2), *ISLES'24:
Final Infarct Prediction with Multimodal Imaging and Clinical Data. Where Do
We Stand?* Every case in the dataset is therefore a thrombectomy-treated
large-vessel-occlusion (LVO) patient imaged acutely, i.e., with the occlusion
in place at CTA acquisition.

**Verified fact (primary-source-adjacent; formula confirmed).** The
intracranial artery tortuosity index the card borrows (Kim et al. line of
work) is defined as "the mean of the tortuosity indexes
[(actual length/straight length − 1) × 100] of the right and left MCAs and
BA," with the MCA measured on the **M1 portion**, semi-automatically
(TeraRecon). Source:
[PMC5836575](https://pmc.ncbi.nlm.nih.gov/articles/PMC5836575/), *Ethnic
Differences in Intracranial Artery Tortuosity*. Note both the segment (M1)
and the paper's own headline finding (tortuosity differs by ancestry).

**Source-supported interpretation.** Intracranial and access-vessel
tortuosity impairs mechanical thrombectomy: lower first-pass success (34% vs
59% in tortuous vessels), more passes (2.1 vs 1.6), lower final TICI ≥ 2b
rates (63% vs 76%). Sources: systematic review, *Impact of intracranial
vessel tortuosity on mechanical thrombectomy outcomes in acute ischemic
stroke* ([ScienceDirect
S0303846725003907](https://www.sciencedirect.com/science/article/abs/pii/S0303846725003907));
[PubMed 35400203](https://pubmed.ncbi.nlm.nih.gov/35400203/) (ICA
tortuosity and MT); [PubMed
40574353](https://pubmed.ncbi.nlm.nih.gov/40574353/) (prognostic value of
intracranial tortuosity in distal-occlusion thrombectomy).

**Verified fact (repo artifact).** The keystone screen
(`ideas/040/keystone_screen.md`) already established: CTA per case, ensemble
pseudolabel Circle-of-Willis masks ("nonexpert reference standards"),
149-case public cohort, and UNVERIFIABLE status for centerline continuity,
TI repeatability, and tortuosity variance. The keystone log additionally
records that mTICI/treatment-variable availability in the released clinical
data is unverified, and a 149 (Zenodo) vs 150 (paper) case-count
discrepancy.

**I did not find** any published audit of a final-infarct or stroke-outcome
deep model for tortuosity use (searched: shortcut/probing/tortuosity audit
terms). Not proof of absence; consistent with the card's own refusal to
claim novelty (novelty_confidence 2).

## 2. The cohort objection, in three prongs

### 2a. The measurement is broken as specified

The card's X_measurement averages TI over "bilateral MCA and basilar"
arteries. The TI formula it cites is defined on the MCA **M1 segment** — in
an anterior-circulation LVO cohort, M1 is the modal occlusion site. On the
affected side, the segment distal to the clot is unopacified or fills weakly
and late via collaterals on single-phase CTA; its centerline and therefore
its TI do not exist as the formula intends. This is not a Stage-0 sampling
risk (the keystone's framing); it is a structural property of the cohort:
the quantity as defined is uncomputable or systematically corrupted in the
affected hemisphere of most cases. Any basilar-occlusion cases (proportion
unverified; computable from the released occlusion masks) break the BA term
the same way. **Classification: inference from two verified facts (all
cases LVO-at-imaging; TI defined on M1+BA).**

### 2b. Selection on TICI 2b/3 is selection against the exposure

Tortuosity reduces the probability of achieving TICI ≥ 2b (source-supported,
section 1). The dataset conditions inclusion on achieving it. Consequences:
(i) **range restriction** — the most tortuous patients are preferentially
excluded, directly attacking the keystone's "sufficient tortuosity
variation" clause and further weakening the already sensitivity-limited
null (the card's negative_result_value of 2 is, if anything, generous
post-restriction); (ii) **collider-shaped bias** — conditioning on a
downstream consequence of tortuosity can induce spurious associations
between tortuosity and other causes of outcome inside the cohort, which a
residual analysis will read as signal. The card's confound list
(age, hypertension, ancestry, bolus, collaterals) contains nothing about
this because it never registered that the cohort is treatment-selected.

### 2c. The rival mechanism the card never names

In this cohort, tortuosity plausibly affects the *actual* final infarct
through procedural mechanics: harder navigation → more passes, longer time
to reperfusion, 2b-rather-than-3 recanalization → larger infarct. Even
within TICI 2b/3, this pathway survives (2b vs 3, pass count, procedure
duration all vary). So tortuosity in ISLES'24 is not merely a slow
"pressure-history" marker entangled with age; it is a candidate *causal
prognostic factor via the intervention itself*. The card's deliverable
interpretation ("vascular-age and long-term pressure-load gauge") and its
alternative-explanations list (age/ancestry proxy, segmentation quality,
collateral covariance) both miss the strongest alternative available in the
literature. Whether it is adjustable depends on whether mTICI grade, pass
count, or procedure times are in the released clinical table —
availability explicitly unverified per the keystone log. **This is the most
dangerous confound, and it is absent from the card.**

## 3. Endpoint and design defects (independent of the cohort objection)

1. **"The model" is unspecified.** The residual analysis needs per-case
   predictions. Released challenge-winner artifacts, if any, were trained on
   the same 149 public cases — using them yields residuals on training data,
   i.e., **leakage** exactly where the card claims to have avoided it. The
   card's own answer (out-of-fold predictions) implies training in-house,
   which collides with the next defect.
2. **The compute claim is inconsistent with the design.** "Nested
   cross-validated residual analysis on all 149 cases … under 10 GPU-hours"
   requires training a final-infarct model per outer fold. A competitive
   multimodal final-infarct model does not train in ~2 GPU-hours per fold;
   a model that does is a weak baseline, and the finding degrades from "the
   model" (title's implication) to "a small model we trained." Either the
   compute number or the audited-model ambition must change.
3. **"Narrow strata" over six covariates with n=149 is arithmetic fiction.**
   Age × site × occlusion location × deficit volume × HIR × CoW topology
   produces mostly empty cells at n=149. The real analysis will be
   regression adjustment, which reintroduces the model-misspecification
   sensitivity that stratification was advertised to avoid. Say so.
4. **The two-part endpoint conflates "unused" with "correctly used."**
   "Tortuosity explains prediction residuals but *not* ground-truth
   residuals" detects only truth-decoupled reliance. If the model uses
   tortuosity *and* tortuosity genuinely predicts outcome here (which 2c
   makes likely via the procedural pathway), both associations appear and
   the test reads null. The endpoint therefore has a built-in bias toward
   null in precisely the cohort being used, degrading negative-result value
   below the card's own assessment. The cleaner primary readout is the
   association of tortuosity with **signed prediction error**
   (prediction − truth), with the residual scalar defined in advance —
   the card never states whether residuals are of volume, Dice, or a
   voxelwise quantity.
5. **Asymmetric null logic.** The "but not ground-truth residuals" half
   requires accepting a null at n=149; the card treats a low-power
   non-rejection as a positive design element.

## 4. Prior-work overlap

No audit of stroke/infarct models for tortuosity use was found (not proof).
The association literature, however, is denser than the card presents: beyond
age/hypertension (the card's citations), tortuosity is associated with
intracranial atherosclerotic burden
([ResearchGate/380666185](https://www.researchgate.net/publication/380666185_Global_intracranial_arterial_tortuosity_is_associated_with_intracranial_atherosclerotic_burden))
and differs by ancestry — the ancestry finding coming from the *same
measurement lineage the card cites for its formula*. The delta over prior
work (auditing a model rather than the outcome) is real, but the association
leg the card leans on drags in atherosclerosis/calcification as a co-visible
correlate. That collides with portfolio candidate isles24-scout-004-c05
(calcification as the model's age gauge, backlog score 4.3): on this design,
a positive tortuosity residual association and a positive calcification
residual association are mutually indistinguishable — both are "vascular-age
gauge" readings from correlated image features. Not a duplicate, but a
portfolio-level identifiability overlap the debate stage should weigh if
both advance.

## 5. Keystone re-assessment

The keystone screen's UNVERIFIABLE verdict stands and **deepens**: the
continuity risk is not just algorithmic (pseudolabel quality) but
epidemiologic (occluded target segments, section 2a) and statistical
(variance compression from TICI selection, section 2b). The 30-case Stage 0
gate as designed would partially detect 2a (continuity failures on the
affected side) but not 2b (it cannot see the excluded patients). The Stage 0
protocol must separate "centerline fails for algorithmic reasons" from
"centerline is absent because the artery is occluded," or the 80% gate will
be uninterpretable.

## 6. Plain-pitch fidelity (cross-family check)

**PASS, with one noted soft spot.** The pitch preserves the Mode C hedges:
"speculative screen," "would not yet prove that the model actually uses the
shape," and the association-first framing all match the card. Nothing in
the pitch is more certain, general, or clinical than the card. The soft
spot: "a statistical link after matching similar strokes" presents matching
as achievable; the card's narrow-strata design is infeasible at n=149
(section 3.3). The defect is card-level, faithfully mirrored — not a pitch
overclaim. No pitch defect is charged.

## 7. Score consequences (suggested, for the revision)

- **identifiability 3 → 2.** "Design rules out the main alternative" is
  false: the main alternative (procedural-difficulty pathway) is not named,
  let alone ruled out, and the TICI selection adds collider risk.
- **mechanism_clarity 5 → 4.** The physical quantity is named and the
  formula exact — but the measurement as specified is uncomputable on the
  affected side of this cohort, so "the measurement that would show the
  model uses it" is not yet in hand.
- Recomputed Mode C priority: 0.30×4 + 0.25×2 + 0.20×4 + 0.15×3 + 0.10×4
  = **3.35** (from 3.9). Still above the backlog's mid-range; consistent
  with revision rather than rejection.
- negative_result_value stays 2 but the "why" must absorb sections 2b and
  3.4: the null is now doubly compromised (range restriction + endpoint
  biased toward null under the likeliest causal structure).

## 8. Required revisions (all within the existing deliverable sentence)

1. **Patent-vessel measurement.** Redefine TI over vessels verifiably patent
   at CTA: contralateral M1, basilar when not the occluded vessel, and
   supraclinoid ICA up to the clot; use the released occlusion masks to
   determine, per case, which segments enter the average, and report the
   affected-side exclusion rate. No new annotation (charter-compliant).
2. **Name the procedural pathway.** Add tortuosity → thrombectomy difficulty
   → infarct as the leading alternative; state whether mTICI grade/pass
   count/procedure times exist in the released clinical table (checkable
   from `clinical_data-description.xlsx` — flagged unverified in the
   keystone log) and adjust for what exists; add "vascular-age
   interpretation without procedural adjustment" to prohibited conclusions.
3. **Fix the endpoint.** Primary readout: signed volume error (defined
   scalar) regressed on patent-vessel TI with a prespecified covariate set;
   drop the narrow-strata language for regression adjustment with stated
   overlap diagnostics; drop the "but not ground-truth residuals"
   requirement as a pass/fail element (report it descriptively).
4. **Name the model and reconcile compute.** Either an in-house baseline
   with honest GPU-hours (state the number for k outer folds) or a verified
   released artifact with documented training folds; a released artifact
   trained on all 149 public cases is disqualified for this analysis.
5. **Stage 0 amendment.** The 30-case centerline gate must classify
   failures as occlusion-caused vs algorithmic, and must report the TI
   variance actually observed so the range-restriction concern (2b) gets an
   empirical answer.

## 9. Easier version — the low-hanging fruit

There is a genuinely cheap, decisive screen *before any model exists*, using
only released data: **compute patent-vessel TI on the 149 public cases and
test its association with released age and hypertension variables.** All
inputs are public (CTA, CoW pseudolabels, occlusion masks, clinical table);
zero GPU beyond skeletonization; 1–2 days. If TI in this TICI-selected,
two-center European cohort does not track age/hypertension, the
"vascular-age gauge" framing is dead for this dataset regardless of what any
model does — a clean kill that costs almost nothing. If it does track, the
same TI values feed the repaired residual analysis unchanged. This should be
the first Stage 0 arm, ahead of the model audit.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does a final-infarct model's signed prediction error vary with patent-vessel arterial tortuosity after adjustment for measured prognostic and procedural covariates — i.e., is there tortuosity-linked bias in ISLES'24 final-infarct prediction?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — the vascular-age reading survives only as the Mode C interpretive target gated on the cheap age-association screen; the immediate question becomes a bias audit.
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — the deliverable sentence survives as the Mode C target with rung-3 external validation, so this is revision-in-place under the claim-identity rule.
IS IT ACTUALLY WORTH DOING? Qualified yes: the section-9 screen is cheap, public-data-only, and decisive in the negative direction, and it should run first — if tortuosity fails to track age/hypertension in this selected cohort, kill the card there and spend nothing on the model audit.
```
