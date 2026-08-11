# Critique — Idea 018: The brain-tumor prognosticator may be weighing the chewing muscle

```
FATAL OBJECTION: Both assets the design requires — a runnable frozen whole-head
GBM survival model, and an obtainable tumor-stable serial cohort that retains
the temporalis — fail direct inspection: GRASP released no weights or inference
code and its data is by-request, and every public longitudinal GBM MRI resource
is either skull-stripped (LUMIERE) or anti-selected against tumor stability
(UPenn-GBM follow-ups are re-resections for progression).
EVIDENCE: keystone_screen.md (GRASP repo commit ba0a1ca, Data Availability of
PMC11145448); LUMIERE Sci Data 2022 (10.1038/s41597-022-01881-7, skull-stripped
for anonymization); UPenn-GBM Sci Data 2022 (PMC9338035, 60 follow-ups, all at
second resection for progressive changes).
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT
```

REJECT is under the claim-identity rule (ledger 2026-08-10, idea 015): the only
viable repair replaces the audited object (GRASP → a self-trained model) and
deletes the longitudinal-within-subject arm, which changes the deliverable's
identity. A specific, well-evidenced successor exists and should enter as a new
candidate with `parent_ids: ["idea-018"]` — see the constructive section.

---

## 1. The audited model does not exist as an obtainable artifact

This is not a prediction; it was inspected. The keystone screen cloned the
publication-linked GRASP repository (commit `ba0a1ca0`) and found training code
only: no checkpoint, no pretrained weights, no inference entry point, and
configuration paths pointing at local files (`pretrained_weights/t1_weights.pt`,
`data/input_data/training_data.npz`) that were never released. The paper's data
availability is "available from the corresponding author by request"
(PMC11145448, Data Availability). The charter forbids dependence on unconfirmed
gated data, so the GRASP route fails twice over: the model cannot be run, and
the recipe cannot be retrained without by-request data.

This is the idea-014 failure mode realized, not merely risked. Idea 014 was
PAUSED because "the rate-limiting model asset has not been reproduced." Here
the asset is not merely unreproduced — the ingredients to reproduce it are
confirmed absent. The card's `dies_like_prior` field claimed only that no
annotation-provenance failure applies (true) and missed this resemblance
entirely. The keystone screen's verdict of UNVERIFIABLE was, if anything,
generous: for the specific GRASP route the conjunctive keystone is now
INSPECTED_FALSE in its second and third conjuncts (obtainable weights;
obtainable serial cohort).

## 2. The longitudinal arm is unexecutable on any public cohort — verified

The card's design leans on "serial scans with stable automated tumor volume"
to decorrelate muscle loss from tumor change. I checked the candidate cohorts:

- **LUMIERE** (91 GBM patients, 638 study dates, OS for a subset; Sci Data
  2022, DOI 10.1038/s41597-022-01881-7) is the one public longitudinal GBM MRI
  dataset — and every study was skull-stripped, with skull-stripping visually
  verified "to ensure patient anonymization." The temporalis is removed by
  construction. Dead.
- **UPenn-GBM** (PMC9338035) includes 60 follow-up scans, but all are from
  patients "who have undergone a second resection due to progressive
  radiographic changes" — the follow-up subset is selected *for* progression,
  i.e., anti-selected against the tumor-stable pairs the design needs. Dead
  for this arm (though decisive for the successor; see below).
- **BraTS-family data** (including UCSF-PDGM) is skull-stripped as a matter of
  pipeline definition. Dead.

So even if GRASP weights materialized tomorrow, the within-patient
tumor-stable tracking arm has no data to run on. Half the "smallest decisive
experiment" cannot be purchased at any effort level with public data.

## 3. A confound the card missed: age (and sex)

The card's alternative-explanations list covers tumor progression, steroids,
and edit seams. It omits the strongest one. Age is the dominant clinical
predictor of GBM survival — in the BraTS survival-prediction task era, simple
age-based models were competitive with imaging pipelines — and temporalis
cross-sectional area declines with age and differs by sex. A whole-head model
that has learned cortical atrophy, ventricular size, or any other age
correlate will co-vary with temporalis without using it; conversely, a model
that *does* use temporalis pixels may be using them as an age/sex readout, not
a frailty readout. Substitution can establish that the pixels are used (rung
1); it cannot arbitrate "frailty" versus "age proxy" as the meaning.

This bears directly on the deliverable sentence. "…as an image marker of
systemic frailty" is interpretive gloss of exactly the kind the ledger already
ruled against when idea 015 lost "vascular age." The defensible rung-3
sentence is "the model is using temporalis muscle bulk" — temporalis
thickness/CSA is the named, tool-measurable X, and it qualifies on its own.
The frailty mechanism is a discussion-section hypothesis, not part of the
claim. Any successor card must make this cut up front, and must carry an
age-adjusted analysis (does temporalis substitution move the score *beyond*
what the model's age estimate explains) if it wants to gesture at frailty.

## 4. Prior-work overlap: real but survivable

- The GRASP authors already knew extracranial tissue carries signal — they
  kept whole-brain inputs partly because "extracranial information is linked
  with overall survival" (PMC11145448, Discussion). The *motivation* is
  pre-articulated in the primary source; the use-audit is not performed there.
  The delta claimed by the card (association exists, use untested) survives,
  but a successor's novelty audit should specifically check whether GRASP or
  its citing literature published saliency/occlusion maps highlighting the
  temporal region — that would narrow the delta from "unasked" to
  "informally observed, never measured."
- The temporalis prognostic literature (Furtner et al.; An et al., BJC 2021,
  DOI 10.1038/s41416-021-01590-9) is association-with-outcome, not
  model-use. No overlap with the audit question.
- No concept-label circularity: X is geometry from an automated tool, the
  model consumes raw images, and no report text enters. The
  annotation-provenance failure family genuinely does not apply.

## 5. What inspection *supports* — the assets for an easier version

The adversarial search turned up genuinely good news, all primary-source:

1. **The temporalis measurement tool is public and proven on public data.**
   The BJC 2021 pipeline (PMC8770629) releases code at
   `gitlab.com/computational.oncology/temporalissegmentation`, and was
   trained/validated on TCGA-GBM (n=31), IVY-GAP (n=23), and REMBRANDT (n=38)
   — public TCIA collections — plus one in-house set. Dice 0.893. This
   *proves* the temporalis survives in standard public GBM T1c imaging and is
   segmentable there without asking anyone. X passes the charter's hard
   constraint cleanly.
2. **A large, open, survival-linked, non-skull-stripped GBM cohort exists.**
   UPenn-GBM (TCIA, CC BY 4.0; Sci Data PMC9338035): 630 patients, 611
   preoperative mpMRI studies, overall survival in a released CSV, and —
   decisively — the release includes "unstripped-structural" scans: defaced
   but with skull and extracranial tissue intact, in original DICOM and
   NIfTI. Defacing removes facial-surface features, and skull-stripping (the
   step that would delete the temporalis) is a *separate* released derivative,
   not the only form.
3. **Compute fits the charter.** A GRASP-style 130³ single-sequence 3D model
   on ~600 patients trains in single-GPU sessions; the temporalis tool is a
   2D segmentation at defined slice levels.

The one load-bearing unknown for this route: whether the CaPTk defacing mask
spares the temporalis at the standardized measurement levels (superior orbital
roof / Sylvian fissure). That is directly inspectable by downloading a handful
of UPenn-GBM unstripped cases and running the GitLab tool — an afternoon of
Stage 0, with a binary answer. That is what a keystone should look like.

## 6. Remaining weaknesses of the successor, stated honestly

- **It audits a model you trained, not a model the field deployed.** The
  program's driver is decoding what models found; a self-trained
  standard-recipe model is a legitimate object (the race-detection literature
  did exactly this), but the finding becomes "whole-head survival training
  discovers sarcopenia" rather than "GRASP uses sarcopenia." Weaker headline,
  same scientific content, and honest.
- **The model must be worth decoding.** If the self-trained model cannot beat
  an age+sex-only baseline on a frozen split, there is no interesting signal
  to decode and the study should stop. This must be a preregistered gate
  (idea-014's lesson applied prospectively). The gate is cheap — days, not
  weeks — which is what makes the successor runnable where idea 014 stalled.
- **Single site.** UPenn-GBM is one health system; scanner/protocol confounds
  are largely neutralized by the within-cohort substitution design, but any
  positive finding is a single-site finding and must say so.
- **Cross-patient substitution replaces within-patient substitution.** With
  no serial arm, the edit source is a sequence- and intensity-matched other
  patient. Seam and bias-field validity checks (scalp/fat shams, left-right
  shams, distribution checks) carry more weight than in the card's
  within-patient version. This is the successor's main identifiability risk.
- **Negative-result value stays capped.** A null remains sensitivity-limited
  until visibility (temporalis in tensor post-defacing) and a positive
  control (tumor-region substitution moves the score) are confirmed; after
  both, a null is a reasonably decisive "this model family does not use it."

## 7. Scoring corrections implied (for the record)

The card's feasibility 3 and novelty 3 caps were correct. Data readiness 2 was
correct for the card as written; the successor on UPenn-GBM would honestly be
a 4 (public, CC BY, direct download) — one of the few cases where the easier
version scores *higher* on data. Identifiability 4 was too generous for the
card given the omitted age confound; the successor should re-score after the
age-adjusted arm is specified.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Train a whole-head 3D survival model on
UPenn-GBM's unstripped defaced scans, gate on beating an age+sex-only baseline
on a frozen split, and test by temporalis-only cross-patient substitution
(with scalp/fat and left-right shams) whether it uses temporalis muscle bulk.
RETAINS ORIGINAL MEDICAL MOTIVATION? YES — frailty contamination of imaging
prognosticators is still the stake; only the audited object changes.
SHOULD IT BECOME A SEPARATE CANDIDATE? YES — claim identity changes (GRASP →
self-trained model; longitudinal arm dropped), so per the 2026-08-10 rule it
re-enters scouting with parent_ids: ["idea-018"], not revision-in-place.
IS IT ACTUALLY WORTH DOING? Yes, conditionally: the age-baseline gate and the
defacing-spares-temporalis check together cost under a week and are decisive
either way — if both pass, this is the rare candidate where the model, the
cohort, the survival labels, and the X-measurement tool are all public today;
if either fails, stop having spent days, not weeks.
```
