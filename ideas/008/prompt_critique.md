You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/008
Preserve existing files unless the task explicitly requires an update.
Do not claim novelty without verified primary sources.
Do not write code unless this is the probe_code stage and human approval exists.

===== CHARTER.md =====
# Research charter

## The driver

Medical imaging models sometimes outperform physicians, or predict things
physicians cannot predict at all. When that happens the model is using signal
that is present in the image and that human readers do not knowingly use.
Sometimes that signal is a real biological or physical fact nobody had
articulated. Sometimes it is an artifact of how the data was made.

**The program: decode what medical imaging models have found, and determine
which kind of thing it is.**

Concepts enter here as the *readout language* — a way to say what the model
found — rather than as a supervision constraint imposed in advance. That is
the inverse of standard concept-bottleneck work and it is the more interesting
direction.

### The deliverable

**Every candidate must end in a sentence a radiologist could read and either
agree or disagree with.**

Of the form: *the model is using X*, where X is a named anatomical,
physiological, or physical thing. Not "the model is not using the scanner."
Not "performance drops when we ablate region R." A positive statement, in
words a physician already has.

That sentence is the point. Everything else is what makes it credible.

### The three rungs

State which rung the candidate reaches and what would move it up.

1. **The model uses signal X.** Ablation, probing, perturbation, occlusion
   with proper controls. Comparatively easy.
2. **X is not an artifact.** Not scanner, site, protocol, reconstruction,
   position, dose, habitus, referral pattern, or label leakage. This is the
   validity gate — necessary, and where most projects quietly fail.
3. **X is a named, human-legible thing.** The deliverable sentence.

Rung 2 is a **gate, not a destination.** A study that only eliminates
confounds tells a physician what the model is *not* doing, which does not help
them understand a decision. Confound elimination earns the right to make the
rung-3 claim; it is not the claim.

A candidate that can reach only rung 2 is allowed, but must say so and must
name what would be needed to reach rung 3. A candidate that reaches rung 1 and
asserts rung 3 is the standard failure of this literature.

### The hard constraint on X

**X must be independently measurable without a human annotator.**

This is the constraint that makes the program feasible for you, and it is not
optional. Six prior candidates died because they required knowing what a human
saw when they assigned a label, and that was undocumented, unavailable, or
contaminated. Do not walk back into that.

X qualifies if it can be computed from the image by an existing, citable tool
or a well-defined measurement. Examples of the right shape:

- parenchymal texture statistics, emphysema percentage, density histograms
- vessel blood volume by calibre, airway wall thickness, luminal area
- muscle or fat attenuation in Hounsfield units, sarcopenia indices
- cardiac chamber size, aortic diameter, coronary calcium
- bone mineral density, vertebral morphometry
- organ volumes from an off-the-shelf segmentation tool

X does **not** qualify if establishing it requires a radiologist to look at
images and agree, or if it exists only as a rating in a dataset whose
annotation conditions are undocumented.

The test: *could you compute X on a scan the model has never seen, today,
without asking anyone?* If not, pick a different X.

This constraint is what separates a concept the model found from a concept you
asserted.

### The two precedents to hold in mind

- Retinal fundus photographs predict patient sex at near-ceiling accuracy while
  ophthalmologists are at chance (Poplin et al. 2018). Real signal, previously
  unarticulated, and it opened a line of work. Related: histopathology slides
  predicting driver mutations, ECG predicting ventricular dysfunction.
- Chest radiographs predict self-reported race across modalities and
  preprocessing, robustly, and after years of investigation nobody can say what
  the signal is (Gichoya et al. 2022). Real, reproducible, and not a discovery.

Both are true. The difference between them is rung 2.

## Two entry points, both allowed

### Entry point 1 — a known gap

Start from a documented case where a model beats human readers, or predicts
something readers cannot. The gap is the evidence that signal exists; the
question is what it is. More grounded, easier to verify, less likely to be
vapor.

### Entry point 2 — looking for the unexpected

Start from a model that merely performs well and ask what it is using that
nobody expected. No documented gap to anchor on. This is where genuinely novel
findings would come from, and also where unfalsifiable speculation comes from.

Entry point 2 candidates carry a higher burden: name the specific measurement
that would detect the unexpected signal, and the specific artifact it would be
confused with. "Probe the representation and see what's there" is not a design.

## Search modes

Each candidate declares `search_mode`.

- **Mode A — the unfinished story.** A paper stops one experiment short.
  Citation-anchored: strong evidence, limited imagination. It can only surface
  questions the literature already framed, and it selects for gaps authors
  chose to leave — sometimes because the data to close them does not exist.
- **Mode B — the unasked question.** Nobody framed it. Found in the space
  between two things that should connect and do not. What would you check if
  you did not trust this result, and why has nobody published that check?
- **Mode C — speculative.** Explicitly permitted to be unlikely. Lower bar on
  feasibility and prior work; **higher** bar on mechanism. A Mode C candidate
  must name the physical or biological quantity it thinks the model is using,
  and the measurement that would show it. Cross-domain borrowing belongs here.

Per cycle: **1 Mode A, 2 Mode B, 2 Mode C.** Five candidates.

Mode C candidates are scored on interest, novelty, and mechanism clarity rather
than feasibility. Do not demote a Mode C candidate for being hard. Do demote it
for being untestable.

## Guard against fluent nonsense

The characteristic failure of speculative generation is a connection that reads
beautifully and implies no measurement. Free energy and diagnostic uncertainty.
Sparse coding and concept bottlenecks. Predictive processing and radiologist
priors. These produce excellent sentences and no experiment.

Every cross-domain or speculative candidate must answer:

**What would be different if the analogy were dropped?**

If the answer is "nothing" — if you would run the same code either way — the
analogy is decoration. Rewrite without it or discard.

## Learn from the record

`evidence/decisions.md` is injected into your context. It is the accumulated
record of what has been proposed, critiqued, and killed, with reasons.

**Read it before proposing, and state explicitly for each candidate whether it
dies the same way as a prior candidate.**

The dominant failure so far, five of six kills, is **annotation provenance**:
the study depended on knowing who assigned the labels and what they could see,
and that was undocumented, unavailable, or contaminated by peer exposure.
Specifically:

- LIDC diagnosis file: patient-level, numbering inconsistent with the XML, only
  18 nodules reliably linkable.
- Derm7pt: whether checklist annotators saw the clinical photograph is
  undocumented, making cross-modality results ambiguous.
- BUS-BRA: releases BI-RADS assessment categories, not lexicon descriptors —
  there were no concepts to intervene on.
- LIDC semantic ratings: released reads are from the unblinded phase after
  readers saw each other's marks, and reader IDs are not stable across scans,
  so they are not independent measurement methods.

The one candidate that survived did so by **not requiring labels at all** in
its primary readout — comparing a model to itself across two reconstructions of
identical anatomy. That structural move is available more often than it is
used. Look for it.

Required per candidate: `dies_like_prior` — either the prior candidate it
resembles and why this one is different, or an explicit "no prior failure mode
applies, because…"

## The keystone prerequisite

Name the single fact which, if false, makes the study impossible or
uninterpretable. State whether it has been **directly inspected** — the actual
file, table, schema, or methods section — or merely inferred from a collection
page, abstract, or search summary.

`feasibility` and `novelty_confidence` are capped at 3 unless
`keystone_status` is `INSPECTED_TRUE`. Mode C candidates may honestly report
`NOT_INSPECTED` and accept the cap; that is expected and not a defect.

**The wrong-keystone error has now occurred three times.** It is the dominant
failure of this loop, ahead of annotation provenance. In each case the easy
adjacent fact was verified and the load-bearing one assumed:

- idea 005: verified that multiple opinions exist per lesion (true); needed
  that they are independent measurement methods (false).
- idea 006: verified that exterior voxels survive preprocessing (true); needed
  that a body-excluded volume is in-distribution (unverified, and probably
  false).

Procedure, mandatory: write the keystone, then write the sentence *"if I have
only verified the nearest checkable thing, what am I still assuming?"* and
answer it. If the answer is load-bearing, that is the real keystone.

Watch for the same error: "Multiple opinions exist
per lesion" was inspected true. "Those opinions constitute independent
measurement methods" was the real keystone, and it was false. State the keystone
as the thing your inference needs, not the thing that is easy to check.

## Claim identifiability

Can the design distinguish the claimed explanation from the plausible
alternatives? A compelling headline is not identifiability. List the two or
three most plausible alternative explanations for a positive result and say
which ones the design rules out.

For this program specifically, the standing alternatives are: scanner or
vendor, acquisition protocol, reconstruction, site, patient positioning, body
habitus, disease prevalence in the sampled population, referral pathway, and
label leakage from the report. Address them by name.

## Negative results

Classify the anticipated negative:

1. **Decisive** — meaningfully weakens the hypothesis.
2. **Sensitivity-limited** — may reflect power, modelling, or metric choice;
   needs an equivalence margin or minimum-detectable-effect.
3. **Uninterpretable** — several explanations survive.

Only type 1 counts toward negative-result value. Non-rejection is not evidence
of independence.

## Domain focus

**Radiology, with emphasis on CT and 3D volumetric imaging.** Vascular and
tubular anatomy, chest CT, and CT-report paired corpora are especially
relevant. Retinal, ECG, and pathology precedents may be cited as motivation but
the experiment should land in radiology where possible.

Per cycle: at least three of five candidates in radiology or CT. At most one
dermatology candidate. No more than two on any single dataset.

## Constraints

- Compute: Colab Pro+ or equivalent single-GPU sessions.
- No dependence on unconfirmed DUA-gated data.
- No large-scale radiologist annotation campaign.
- Literature claims require primary-source verification.
- Keep confirmatory and exploratory work separate.
- Never tune on the untouched test set.
- Prefer designs whose primary readout does not depend on label quality.

## What counts as success

- A clear positive result.
- A decisive negative — including "the signal was an artifact."
- Evidence that a popular assumption is unsupported.
- Identification of a decisive confound.
- A feasibility result that prevents wasted effort.


===== docs/COLLABORATOR_RULES.md =====
# Collaborator rules

## Role

Act as a critical research collaborator. Generate ideas, but spend at least as much effort trying to disprove or simplify them.

## Required distinctions

Always distinguish:

- verified fact;
- source-supported interpretation;
- inference;
- speculation;
- exploratory result;
- confirmatory result.

## Literature

- Use primary sources for medical, dataset, and method claims.
- Record DOI, PMID, arXiv ID, or official repository URL.
- Never claim novelty from memory alone.
- “I did not find it” is not proof that it does not exist.
- Identify the closest work and explain the exact delta.

## Idea generation

Prefer “one experiment away from a stronger story” over unconstrained novelty brainstorming.

For every idea, identify:

- the scientific uncertainty;
- the existing legwork already completed by others;
- the missing final step;
- why that step matters;
- the smallest decisive experiment;
- the most dangerous confound;
- why a negative result remains useful.

## Coding gate

Do not generate probe code until all are present:

- a reviewed idea card;
- a feasibility memo;
- a probe contract;
- explicit human approval.

## Experimental integrity

- Freeze splits before model comparison.
- Save configurations, seeds, environment, and per-case outputs.
- Use validation for development and preserve an untouched test set.
- Do not reinterpret an invalid run as a negative result.
- Report every authorized variant, not only the best one.
- Stop when the preregistered question is answered or the budget is exhausted.


===== docs/SCORING_RUBRIC.md =====
# Idea scoring rubric

Score each dimension 1-5. Explain every score.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Clarity | vague | testable with refinement | one-sentence precise question |
| **Identifiability** | a positive result has many explanations | design rules out the main alternative | design isolates the claimed mechanism |
| Medical relevance | cosmetic | plausible utility | clear meaningful consequence |
| Interest | routine | useful niche result | surprising or broadly compelling |
| Prior legwork | little exists | some reusable assets | data/code/labels/checkpoints ready |
| Feasibility | major barriers | manageable | first result in days |
| Data readiness | uncertain/restricted | accessible with work | public and directly usable |
| Evaluation readiness | unclear | custom metrics needed | accepted metrics and baselines exist |
| Negative-result value | uninterpretable null | sensitivity-limited null | decisive negative |
| Novelty confidence | likely covered | uncertain | precise verified gap |
| Regret | little concern | worth considering | obvious-in-hindsight opportunity |

## Hard caps

`feasibility` and `novelty_confidence` may not exceed **3** unless
`keystone_status` is `INSPECTED_TRUE`. See the charter.

`negative_result_value` may not exceed **2** if the anticipated negative is
classified as uninterpretable.

## Priority score

Transparent weighted sum, not a fake probability:

- 20% feasibility
- **15% identifiability**
- 15% medical relevance
- 10% prior legwork
- 10% interest
- 10% clarity
- 10% negative-result value
- 5% data readiness
- 5% novelty confidence

Evaluation readiness and regret are reported separately and must not override
weak scientific value.

Identifiability enters at 15% because the first cycle produced several
candidates with strong headlines whose designs could not isolate the stated
phenomenon. Interest was compensating for weak measurement validity.

## Mode C scoring

Mode C (speculative) candidates are scored differently. Do **not** demote a
Mode C candidate for low feasibility or thin prior legwork — that is what the
mode is for. Do demote it for being untestable.

For Mode C, replace the priority weighting with:

- 30% mechanism clarity (is the suspected physical/biological signal named?)
- 25% identifiability
- 20% interest
- 15% medical relevance
- 10% clarity

Report feasibility and novelty confidence for information, outside the score.
A Mode C candidate that would take three weeks is fine. One that could not be
falsified in three years is not.

**Mechanism clarity, 1-5:**

| 1 | 3 | 5 |
|---|---|---|
| "probe the representation and see what is there" | a named signal family, unclear how to isolate it | a specific physical or biological quantity, and the measurement that would show the model uses it |


===== evidence/decisions.md =====
# Decision ledger

Record decisions as evidence statements rather than broad permanent bans.

Format:

## YYYY-MM-DD — IDEA-ID — ADVANCE | REVISE | PAUSE | REJECT

**Question:**

**Evidence:**

**Scope of conclusion:**

**What this does not establish:**

**Revisit trigger:**

## 2026-08-04 — Idea 001 REJECTED (LIDC concepts vs diagnosis)
Zinovev et al. 2012, J Digit Imaging 25:423-436 (DOI 10.1007/s10278-011-9445-3)
VERIFIED by reading the paper: diagnosis file is patient-level, numbering
inconsistent with LIDC XML, only 18 nodules reliably linked (8 mal / 9 ben /
1 indet) via single-nodule-patient restriction. Too small for the proposed
paired AUC analysis.
Reopen only with a released, independently validated diagnosis-to-XML-nodule
mapping retaining all eight semantic ratings, meeting a prespecified CI-width
target before model fitting.
Separate unresolved objection, raised in critique but never debated: the eight
characteristics and the malignancy rating come from the same reader in the same
session, so concept-to-suspicion prediction measures rating-form consistency,
not concept validity.

## 2026-08-04 - Idea 004 Stage 0 COMPLETE
3,039 validation volumes / 1,564 scans / 1,304 patients.
1,432 of 1,564 scans multi-reconstruction (92%).
425 strictly clean geometry-matched kernel pairs after excluding slice-count,
position, and acquisition-parameter drift.
Contrasts: Br40f|Br60f 237, Bl56f|Br40f 126, Bl57d|Br36d 58, Br40f|Br44f 4.
462/464 Siemens - findings vendor-specific, state as limitation.
Labels identical across reconstructions: 1.00 (exact duplication).
No released per-volume ClassFine scores: CT-RATE has only RadBERT report
labels; CT-CLIP GitHub v1.0.0 has no release assets; checkpoints are not on
the authors HF account. Inference must be run locally.
Scope: download 850 volumes (425 pairs), not 3,039. Inference code exists at
scripts/data_inference_nii.py and run_forward_data.py.

## 2026-08-04 - Idea 002 PAUSE (Derm7pt clinical photo concepts)
Annotation provenance undocumented: unknown whether checklist annotators saw
the paired clinical photograph. A positive result would have two materially
different explanations. Unblocked only by author correspondence.

## 2026-08-04 - Idea 003 REJECT (BI-RADS intervention realism)
BUS-BRA releases BI-RADS assessment categories, not lexicon descriptors - no
concepts to intervene on. Debate ran six rounds; amendments achieved
feasibility by abandoning the intervention question entirely.

## 2026-08-04 - Idea 005 PAUSE (LIDC concept discriminant validity)
MTMM requires independent measurement methods. LIDC released reads are from the
unblinded phase after readers saw each others marks, and reader IDs are not
stable across scans. Keystone error: verified that multiple opinions exist
(true) rather than that they are independent measurement methods (false).

## 2026-08-05 - Idea 006 PAUSE (CT-CLIP non-tissue voxel prediction)
Patient-deletion is an extreme OOD intervention; neither direction identifies
exterior reliance during intact inference. Wrong-keystone error, third
occurrence: verified that exterior voxels survive preprocessing (true) when the
inference required that a body-excluded volume is in-distribution (unverified).
Reopening condition: inspect CT-CLIP training loader for large-region masking
or cutout with matching fill value.
SPIN-OFF, endorsed by both critique and debate: hold every voxel inside a
dilated patient contour fixed and substitute only the scan exterior between
geometry-matched scans; measure paired ClassFine score change. Separate
estimand, enter as a new candidate.

## 2026-08-05 - Idea 007 ADVANCE TO REVISION (lung inflation, CT-CLIP)
Paired inhale/exhale BHCT + 4DCT confirmed: 20 patients, one session, one
scanner, TCIA DOI 10.7937/3ppx-7s22, ungated, 14.93 GB.
4DCT phases are NOT calibrated inflation levels - phase is time position, not
fraction of vital capacity; same amplitude occurs on both limbs; phase-sorting
artifacts. Dose-response arm demoted to exploratory.
Preprocessing confound is the live keystone residual: fixed-size crop may admit
different anatomy at different diaphragm positions. Stage 0 gate.
CT-CLIP has no mosaic attenuation head - card claimed a nonexistent output.
Claim demoted rung 3 -> rung 1: sensitivity to respiratory state, not
identification of total lung volume as the cue.


===== ideas/008/README.md =====
# Idea 008: Two papers say Sybil's residual signal is the background, one of them names emphysema, and neither measured it

Selected from scouting cycle 004, candidate 1.


===== ideas/008/idea_card.json =====
{
  "id": "C1",
  "search_mode": "A",
  "entry_point": 1,
  "title": "Two papers say Sybil's residual signal is the background, one of them names emphysema, and neither measured it",
  "question": "On low-dose CT scans with no visible nodule at the site of the subsequent cancer, where Sybil still reaches a 2-year AUC of 0.81, is its risk score a function of quantitative emphysema - the percentage of lung voxels below minus 950 Hounsfield units - measured on the same scan?",
  "deliverable_sentence": "Sybil is using emphysema, and it reads it in a way that survives a change of reconstruction kernel that moves the standard quantitative emphysema index by about ten percentage points.",
  "rung": {
    "current": 3,
    "why": "The claim is a named parenchymal abnormality that a chest radiologist reports by name in ordinary practice, measured in calibrated units by a released tool. It is not a region and not an absence.",
    "what_would_move_it_up": "Nothing above rung 3 exists. What would strengthen the rung-3 claim rather than raise it: external replication of the score-to-emphysema relationship in the MGH or CGMH validation cohorts used by the original paper, and a demonstration that the relationship holds within strata of pack-years, since emphysema and smoking dose are entangled."
  },
  "X_measurement": {
    "X": "Quantitative emphysema, primarily LAA%-950 - the percentage of lung voxels with attenuation below minus 950 HU - with Perc15, the 15th percentile of the lung attenuation histogram, as the pre-registered co-primary because it is less threshold-brittle.",
    "how": "Segment lung with lungmask (github.com/JoHof/lungmask, Apache-2.0, pip-installable, model R231 or LTRCLobes_R231), then count voxels below the threshold inside the mask. There is no model fitting and no annotation step; it is a threshold and a division.",
    "citations": "Threshold validated against macroscopic morphometry by Gevenois PA, de Maertelaer V, De Vuyst P, Zanen J, Yernault JC, Am J Respir Crit Care Med 1995;152(2):653-7, PMID 7633722, DOI 10.1164/ajrccm.152.2.7633722, which reports that minus 950 HU was 'the only level for which no statistically significant difference was found between the HRCT and the morphometric data'. Segmentation tool: Hofmanninger J et al., Eur Radiol Exp 2020;4:50, DOI 10.1186/s41747-020-00173-2.",
    "could_I_compute_it_today_without_asking_anyone": "Yes. pip install lungmask, run it on a DICOM series, count voxels. No annotator, no license key, no application. This is the cleanest X in the portfolio on the charter's test.",
    "known_weakness_of_X_stated_up_front": "LAA%-950 is a fragile measurement and the charter deserves to hear that before the design rather than in critique. In NLST its association with cancer is real but tiny - Labaki WW et al., Chest 2021;159(5):1812-1820, PMID 33326807, reports 'Every 1% increase in %LAA was independently associated with higher hazards of lung cancer incidence (hazard ratio [HR], 1.02; 95% CI, 1.01-1.03; P = .004)' on a variable whose median is 0.8% - and in a separate NLST case-control it discriminated barely at all, Gierada DS et al., Radiology 2011;261(3):950-959, PMID 21900623, reporting the relationship as 'weak (R2 = 0.015, P < .001, c = 0.57)' with 'no potential practical value for clinical risk stratification'. In PLuSS it was null outright, Wilson DO et al., J Thorac Oncol 2011, PMID 21610523: 'The relationship between visual assessment of emphysema and increased lung cancer risk could not be verified by quantitative analysis of low-dose screening CT scans.' This does NOT sink the candidate, because the study does not ask whether LAA predicts cancer - that is settled and weak. It asks whether SYBIL'S SCORE tracks LAA, which is a different and potentially much larger association. But it does mean a null must be interpreted against a measurement known to be noisy, which is why Perc15 is co-primary and why the kernel is fixed for the primary analysis."
  },
  "suspected_signal": "Emphysematous destruction enlarges distal airspaces and reduces tissue per unit volume, which lowers X-ray attenuation in a spatially textured way that a 3D convolutional encoder can read directly off the calibrated voxel values. The biological link to cancer is independently established and not assumed here: chronic inflammation, impaired mucociliary clearance and altered repair in destroyed parenchyma raise malignant transformation risk, and CT emphysema carries a pooled odds ratio around 2.3 for lung cancer - Yang X et al., Radiology 2022;304(2):322-330, PMID 35503012, DOI 10.1148/radiol.212904, reporting visual 'pooled OR, 2.3; 95% CI: 1.9, 2.6' and quantitative 'pooled OR, 2.2; 95% CI: 1.8, 2.8'. So a positive result would say the model found a real, known, named risk substrate on its own, in a spatial pattern it was never shown.",
  "keystone_prerequisite": "Sybil's risk score and LAA%-950 can be placed side by side, per scan, on NLST series that (a) Sybil did not train on and (b) share a single reconstruction kernel - because the kernel moves LAA%-950 by more than the disease does, so a mixed-kernel sample would measure the kernel and call it emphysema.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "Four separate inspections. (1) WEIGHTS AND CODE: sybil/model.py contains the hardcoded, unauthenticated CHECKPOINT_URL 'https://github.com/reginabarzilaygroup/Sybil/releases/download/v1.5.0/sybil_checkpoints.zip'; LICENSE.txt reads 'MIT License', 'Copyright (c) 2022 Peter Mikhael & Jeremy Wohlwend'; GitHub release assets confirm sybil_checkpoints.zip on v1.5.0, v1.1.0 and v1.0.3. No application, no data transfer agreement. Note the packaging trap: setup.cfg declares name = sybil but pypi.org/project/sybil is an unrelated documentation-testing package, so pip install sybil fetches the wrong software and installation must be from source. (2) HELD-OUT SPLIT: no split file ships - files/lung_cancer_dataset.csv is a header-only template with columns patient_id, exam_id, series_id, exam_date, ever_has_future_cancer, years_to_cancer, years_to_last_negative_followup, file_path, slice_position, split and zero data rows. But scripts/data/create_nlst_metadata_json.py shows exactly how the split was made: test_google_data = pd.read_excel(args.test_google_splits) with default path ending TEST_41591_2019_447_MOESM5_ESM.xlsx, then 'if pid in test_google_pids: split_group = test'. That file is the supplementary material of Ardila et al., Nat Med 2019, DOI 10.1038/s41591-019-0447-x, and it downloads from static-content.springer.com with HTTP 200, 1.1 MB, no login. Sybil's held-out NLST test set is therefore the Ardila test participant IDs. (3) FIXED KERNEL AVAILABLE: TCIA NLST holds 203,099 series across 73,116 studies, 2.78 series per screening exam, and the PUBLIC nlst_screen table carries columns ct_recon_filter3 and ct_recon_filter4, so up to four reconstruction filters are recorded per exam. Kernel names across the three vendors are Siemens B50f and B30f, GE BONE, LUNG and STANDARD, and Philips D and C. (4) THE NON-NODULAR SIGNAL IS REAL: Mikhael et al., J Clin Oncol 2023;41(12):2191-2200, PMID 36634294, PMC10419602, full text inspected: 'Sybil's performance was hampered by removing visible nodules, obtaining a 2-year AUC of 0.81 (95% CI, 0.74 to 0.86) and a 6-year AUC of 0.69 (95% CI, 0.63 to 0.74).'",
  "keystone_residual_assumption": "Having verified that the Ardila supplementary file downloads and that Sybil's own script reads a patient_id column from it, I am still assuming that the identifiers in that column are NLST participant IDs in the form that joins to TCIA's DICOM PatientID. The xlsx was not parsed - the verification environment could not unzip it. There is a specific reason not to wave this through: Simon et al. describe the Sybil internal-validation subset as 'n = 13,326 series of 6883 LDCTs in 2328 participants', while the JCO paper describes 'a heldout set of 6,282 LDCTs from NLST participants', and neither number is obviously the Ardila test set size. Those three numbers need reconciling before the split is trusted. This is load-bearing for contamination control but NOT for the existence of the study - a score-versus-biomarker association is estimable on any scans, and training contamination would have to act through memorization to distort it. A reviewer who judges the contamination control load-bearing should demote this keystone to NOT_INSPECTED and cap feasibility and novelty confidence at 3. The check costs one unzip and one join.",
  "rung_reached": {
    "value": 3,
    "conditional_on": "The rung-3 sentence is earned only if the association survives the fixed-kernel primary analysis AND the nodule-free subset AND adjustment for pack-years. If it survives only in the full sample, the honest claim drops to rung 1 - the model uses something that correlates with the density histogram - because emphysema, smoking dose and nodule burden are entangled in a screening cohort by construction."
  },
  "dies_like_prior": "No prior failure mode applies, and for a structural reason rather than by luck. The five annotation-provenance kills - ideas 001, 002, 003, 005 and the diagnosis-linkage half of 001 - all required knowing which human assigned a label and what that human could see. Here nothing is assigned by a human: X is a voxel count produced by a threshold, and the model's score is a number produced by a released checkpoint. The idea-006 intervention-validity failure also does not apply, because the only manipulation is a swap between two reconstructions that the scanner actually produced from one acquisition, so both arms are real clinical images and neither is off-manifold. The nearest resemblance is to scout-003's C1, which also sat on NLST and also depended on a data-linkage step - but that candidate's decisive variable was the screening centre, which record_corrections now establishes is masked even in the gated release, whereas this candidate's decisive variable is the reconstruction kernel, which is public in nlst_screen and redundantly encoded in the TCIA SeriesDescription.",
  "closest_prior_work": [
    {
      "citation": "Sobieski B, Grzywaczewski A, Dobiczek F, Wojcik P, Bartczak M, Szatkowski F, Bombinski P, Tivnan M, Biecek P. Auditing Sybil: Explaining Deep Lung Cancer Risk Prediction Through Generative Interventional Attributions.",
      "identifier": "arXiv:2602.02560, ICML 2026 poster 66127",
      "verification": "INSPECTED (arXiv HTML v2, full text)",
      "what_it_did": "Built a causal attribution method, S(H)NAP, using 3D diffusion-bridge edits to add and remove pulmonary nodules, and decomposed Sybil's risk into nodule-specific and background terms. Found that Sybil 'functions as a linear model with pairwise interactions over pulmonary nodules', that it has a radial sensitivity bias attributed to 'zero-padding in 3D convolutions', and that it responds to clinically unjustified artifacts including hospital-gown metal snaps and ECG leads, where it 'appears to correlate these leads with critical conditions'.",
      "what_it_did_not_do": "This is the unfinished story, and the gap is stated in the paper's own words. It intervened on PULMONARY NODULES ONLY - no other structure is causally manipulated. It isolates the background term and then sets it aside: 'While not our primary focus, analyzing this baseline offers complementary insights', reporting only a regression of the baseline term on patient age. And it names the very hypothesis this candidate tests, as speculation, without measuring it: 'Intuitively, low nodule contribution aligns with clinical reasoning: absent pathology, risk estimates should rely on background markers like emphysema.' The word emphysema appears as an intuition. No LAA-950, no Perc15, no parenchymal quantification anywhere. Methodological note in this candidate's favour: their diffusion edits required a radiologist realism check to defend, where 'their performance is statistically indistinguishable from random guessing (exact binomial test, point estimate 0.57)'. A kernel swap needs no such defence because both images are real."
    },
    {
      "citation": "Simon J, Mikhael P, Graur A, Chang AEB, Skates SJ, Osarogiagbon RU, Sequist LV, Fintelmann FJ. Significance of Image Reconstruction Parameters for Future Lung Cancer Risk Prediction Using a Deep Learning Model.",
      "identifier": "Invest Radiol 2024, PMID 39437009, PMC12129392, DOI 10.1097/RLI.0000000000001131",
      "verification": "INSPECTED (PMC full text, results section)",
      "what_it_did": "Ran Sybil across matched NLST series differing in exactly one reconstruction parameter - 1,961 standard-versus-lung pairs and 1,049 standard-versus-bone pairs - and found population AUCs indistinguishable: standard versus lung at year 6 was '0.82 [95% CI: 0.77-0.86] standard vs 0.80 [95% CI: 0.76-0.85] lung, P = 0.71'. Concluded that 'Sybil's predictive performance for future lung cancer risk is robust across different reconstruction filters and axial slice thicknesses'.",
      "what_it_did_not_do": "Three omissions, and the candidate lives in all three. First, it measured NO IMAGE PROPERTY AT ALL - matching was on 'Digital Imaging and Communications in Medicine header metadata', so score stability is never linked to any quantity that actually changed in the pixels. Second, it reports only SIGNED mean differences, which cancel to approximately zero by construction - minus 0.0005 with SD 0.07 for standard versus lung - and gives no absolute difference, no ICC, no Bland-Altman limits, and no reclassification analysis, so individual-level agreement is unmeasured on a score whose SD is 0.07 against an event rate of one to two percent. Third, the robustness conclusion rests on DeLong non-rejection with P values from 0.71 to 0.86 and NO PRESPECIFIED EQUIVALENCE MARGIN, and one comparison has a year-1 CI of 0.70 to 0.99. Under this charter's own rule that non-rejection is not evidence of independence, that conclusion is a type-2 result presented as type 1."
    },
    {
      "citation": "Jin H, Heo C, Kim JH. Deep learning-enabled accurate normalization of reconstruction kernel effects on emphysema quantification in low-dose CT.",
      "identifier": "Phys Med Biol 2019;64(13):135010, PMID 31185463, DOI 10.1088/1361-6560/ab28a1",
      "verification": "INSPECTED",
      "what_it_did": "On 353 NLST scans reconstructed both ways across four scanner models: 'The mean of pair-wise differences in RA950 between standard and sharp kernel reconstructions was reduced from 10.75% to -0.07% using kernel normalization. The difference for perc15 decreased from -31.03 HU to -0.30 HU after kernel normalization.'",
      "what_it_did_not_do": "Treated the kernel effect as a nuisance to be removed. This candidate treats it as a free, in-distribution, physically calibrated exposure manipulation of the measurement channel - the same raw data, a known and large shift in X, and a model score to watch. Corroborated independently by Gallardo-Estrella L et al., Eur Radiol 2016, PMID 26002132, with Siemens b31f versus b45f emphysema score differing by '7.7 +/- 2.7' points, and by a virtual imaging trial with known ground truth, Abadi E, Lynch DA, Samei E et al., Chest 2023;163(5):1084-1100, PMID 36462532, where I31 minus I70 is minus 8.6 +/- 5.7 for LAA-950."
    },
    {
      "citation": "Graziani M, Andrearczyk V, Mueller H. Regression Concept Vectors for Bidirectional Explanations in Histopathology.",
      "identifier": "arXiv:1904.04520, DOI 10.1007/978-3-030-02628-8_14",
      "verification": "INSPECTED",
      "what_it_did": "Formalized continuous, segmentation-derived measurements as interpretability concepts and measured network sensitivity along them by directional derivative.",
      "what_it_did_not_do": "This is the methodological prior art that bounds the novelty claim and it must be cited, not discovered in review. It works in the activation space of a chosen layer on histopathology and needs a trained concept regressor per concept. The delta here is narrow and should be stated narrowly: a specific deployed clinical risk model, a specific validated biomarker with a published measurement protocol, an in-distribution physical manipulation of that biomarker, and a mediation decomposition against a registry outcome - the last of which was NOT_FOUND across five queries for radiology generally."
    },
    {
      "citation": "Labaki WW et al. Quantitative Emphysema on Low-Dose CT Imaging and Risk of Lung Cancer and Death.",
      "identifier": "Chest 2021;159(5):1812-1820, PMID 33326807, DOI 10.1016/j.chest.2020.12.004",
      "verification": "INSPECTED",
      "what_it_did": "Established on 7,262 NLST participants that LAA%-950 independently predicts lung cancer incidence, lung cancer mortality and all-cause mortality.",
      "what_it_did_not_do": "Related the biomarker to outcomes, not to any model. It also does not specify the reconstruction kernel used, which given the 10.75-point kernel effect is a material omission and one this candidate must not repeat."
    }
  ],
  "existing_assets": [
    "Sybil weights and inference code under MIT, auto-downloading from a hardcoded URL. No gate of any kind.",
    "NLST imaging on TCIA under CC BY 4.0, 26,254 subjects, no application.",
    "NLST lung cancer outcomes in the PUBLIC subset - nlst_canc with candx_days - queryable as bigquery-public-data.idc_current_clinical.nlst_canc with no credentials, and joinable by dicom_patient_id which IDC documents 'is identical to the PatientID field in the DICOM files'.",
    "Reconstruction filters recorded per exam in the public nlst_screen table (ct_recon_filter1 through 4) and redundantly in TCIA's coded SeriesDescription, field 5.",
    "lungmask, pip-installable, Apache-2.0, for the lung mask; LAA%-950 is then a voxel count.",
    "Published kernel effect sizes on NLST data specifically (10.75 points for RA950, 31.03 HU for Perc15) so the manipulation's expected magnitude is known before running anything.",
    "A published nodule-free performance benchmark (2-year AUC 0.81) so the residual signal's size is known and need not be re-established."
  ],
  "smallest_decisive_experiment": "Stage 0, two days, go/no-go: reconcile the three participant counts named in keystone_residual_assumption, confirm the Ardila supplementary column joins to TCIA PatientID, and tabulate how many held-out participants have at least one series in each of the common kernels. Stage 1 is the whole hypothesis and needs no outcomes and no labels: on held-out NLST scans restricted to ONE kernel, run Sybil and compute LAA%-950 and Perc15 on the identical series, then estimate the association between the risk score and each biomarker, with the nodule-free subset as the pre-registered primary population. A model that is using emphysema will show a monotone score gradient across Perc15 deciles. Stage 2 is the manipulation and is the part no one has run: on the standard-versus-lung and standard-versus-bone pairs, compute the PER-PATIENT change in LAA%-950 and the PER-PATIENT change in Sybil's score, and regress one on the other. This is the analysis Simon et al. could not do because they measured no image property. It separates three outcomes that their signed means conflate - the score tracks the histogram, in which case the per-patient slope is positive and the model is reading a kernel-contaminated measurement; the score is flat while the biomarker moves 10 points, in which case the model has learned a reconstruction-invariant estimate of emphysema that is better than LAA-950 itself; or the score moves but not in proportion to the biomarker shift, which is a constant kernel offset and means the model reads the kernel rather than the emphysema. Stage 3, only if Stage 1 is positive: mediation of the score-to-cancer association through Perc15 using the public candx_days outcome, which is the NOT_FOUND corner of the methodology literature.",
  "standing_confounds_addressed": {
    "scanner_and_vendor": "ADDRESSED in Stage 2 by construction, because the pair is two reconstructions of one acquisition on one scanner. ADDRESSED in Stage 1 by stratification, since manufacturer and model are retained in the public DICOM release.",
    "acquisition_protocol": "PARTLY ADDRESSED. NLST is a protocolised screening trial, and kVp and mAs are recoverable from the coded SeriesDescription. Note that XRayTubeCurrent as a distinct tag was NOT located in the public release - mAs and effective mAs are what is exposed.",
    "reconstruction": "This is the manipulated variable in Stage 2 and a stratification variable in Stage 1. It is the single most dangerous confound for this X - the kernel moves LAA%-950 by 7 to 11 points while the disease effect is HR 1.02 per point - and the design's central discipline is that the primary analysis never pools kernels.",
    "site": "NOT ADDRESSED AND NOT ADDRESSABLE. NLST's screening centre is 'Cen: Screening Center (masked)' in the full release. Stage 2 is immune because the pairing is within-scan, but Stage 1 and Stage 3 cannot exclude site, and this must be stated as a permanent limitation rather than a pending download.",
    "positioning": "ADDRESSED in Stage 2, identical by construction. NOT ADDRESSED in Stage 1, though the biomarker is computed inside an anatomically defined lung mask, which makes it position-invariant to first order.",
    "habitus": "NOT ADDRESSED directly. Body size affects noise via automatic exposure control, which affects LAA%-950. Mitigated by including effective mAs as a covariate and by the Stage 2 within-patient design where habitus is identical.",
    "prevalence": "ADDRESSED by construction - NLST is a single screening cohort with uniform eligibility, so there is no between-population prevalence contrast.",
    "referral_pathway": "ADDRESSED by construction. Participants were trial-enrolled against fixed criteria, not referred for a clinical indication.",
    "label_leakage": "NOT APPLICABLE to Stages 1 and 2, which use no labels at all. In Stage 3 the outcome is a registry-recorded cancer diagnosis date, which cannot leak from a radiology report into an image."
  },
  "alternative_explanations": [
    "Smoking dose. Pack-years cause both emphysema and cancer risk, and the JCO paper notes that 'traditional clinical risk factors such as smoking duration can be predicted directly from the LDCT images'. If Sybil is reading a smoking-dose signature of which emphysema is one component, the association is real but the named X is too narrow. PARTLY EXCLUDED by adjusting for pack-years - conditional on pkyr surviving into the public nlst_prsn cut, which is unverified and is the one query Stage 0 must run.",
    "Vascular pruning rather than parenchymal destruction. Estepar et al. 2013 reports that '%LAA-950 was inversely related to all calculated vascular ratios', so BV5 and LAA-950 move together and a positive for one is weak evidence against the other. NOT EXCLUDED by this design on its own; this is precisely why C5 exists, and the honest resolution is to measure both and report the partial associations.",
    "Residual nodule signal. The nodule-free subset is defined by radiologist annotation of visible nodules at the future cancer site - a human judgment, and the only one anywhere in this candidate. Sub-threshold nodularity would still be present. PARTLY EXCLUDED, and worth noting that the audit paper's diffusion-based nodule removal is a stronger control that this design deliberately declines to use because it reintroduces the distribution-shift problem that killed idea 006.",
    "Honest self-assessment. The appealing sentence here is 'the model learned a better emphysema measurement than the one radiologists use', which would arise from the flat-score-moving-biomarker branch of Stage 2. That branch is also exactly what a model that simply ignores the parenchyma would produce. The two are distinguished ONLY by Stage 1 showing a cross-sectional association at fixed kernel first. If Stage 1 is null, Stage 2's flatness means nothing at all, and the write-up must not be allowed to reach for the better sentence. I would put this in the protocol as a gating rule rather than trusting discipline at analysis time."
  ],
  "anticipated_negative": {
    "classification": "decisive",
    "reasoning": "If Sybil's score on nodule-free, fixed-kernel scans shows no association with Perc15 or LAA%-950 within a prespecified equivalence margin, it falsifies the only positive hypothesis anyone has put in print about this model's residual signal - the audit paper's sentence that risk 'should rely on background markers like emphysema'. That is a named hypothesis from a named paper being eliminated, not a failure to find something. It also sharpens the open question, because the JCO nodule-free AUC of 0.81 does not go away. The margin must be prespecified against the score's own SD of 0.07 from Simon et al., and the sample sized to it, or the null degrades to sensitivity-limited."
  },
  "remaining_legwork": [
    "Reconcile the 6,282 / 6,883 / 2,328 participant counts and parse the Ardila supplementary xlsx. Two days, and it is the keystone residual.",
    "One BigQuery INFORMATION_SCHEMA query on nlst_prsn to confirm pack-years, age and sex survived into the public cut. Minutes, no credentials, but it gates the smoking-dose adjustment.",
    "Select the fixed-kernel cohort and size it against a prespecified minimum detectable association. Three days.",
    "Download the subset. This is the real cost - NLST is an 11 TB collection and even a held-out, single-kernel, nodule-free subset is a substantial transfer.",
    "Validate lungmask on low-dose screening CT, which is noisier than the diagnostic CT these tools are usually shown on. Half a week.",
    "Time to first decision: Stage 0 in two days; Stage 1 answers the substantive question in about three weeks."
  ],
  "scores": {
    "clarity": {
      "value": 5,
      "why": "One sentence naming the model, the population, the biomarker, the threshold and the tool. The null is stated in the question."
    },
    "identifiability": {
      "value": 4,
      "why": "Stage 2 is within-scan, which eliminates scanner, vendor, site, positioning, habitus and prevalence simultaneously, and it distinguishes three named mechanisms rather than two. Stage 1 fixes the kernel, which is the dominant threat to this particular X. Held below 5 because site is permanently unaddressable in NLST, because smoking dose is a genuine competing cause that adjustment only partly handles, and because BV5 and LAA-950 are inversely correlated so a positive does not by itself exclude the vascular explanation."
    },
    "medical_relevance": {
      "value": 4,
      "why": "It would tell a radiologist that a screening risk score is partly reading a finding they already report by name, which changes how the score is interpreted at the point of care and suggests emphysema should be read alongside it. Held below 5 because it does not by itself change management."
    },
    "interest": {
      "value": 5,
      "why": "A deployed, validated, FDA-adjacent risk model whose most-discussed property is that it works without a visible nodule, and two independent papers stop one measurement short of saying what it is using. The answer is interesting in every branch, including the flat-score branch."
    },
    "prior_legwork": {
      "value": 5,
      "why": "Open weights, open images, open outcomes, a pip-installable measurement tool, a published nodule-free benchmark, a published kernel effect size on this exact dataset, and a published paired-series construction to copy."
    },
    "feasibility": {
      "value": 4,
      "why": "Cap lifted, keystone INSPECTED_TRUE. Inference-only, single GPU, no training. Held to 4 by the size of the NLST transfer and by the split-reconciliation step, which is cheap but genuinely unfinished."
    },
    "data_readiness": {
      "value": 5,
      "why": "CC BY 4.0 imaging with no application, public outcome table with no credentials, MIT weights with no gate. Nothing in this candidate is behind any door."
    },
    "evaluation_readiness": {
      "value": 4,
      "why": "AUC, rank correlation, per-patient paired regression and mediation are all standard, and there are published reference values for both the biomarker and the kernel shift. Only the equivalence margin needs specifying."
    },
    "negative_result_value": {
      "value": 4,
      "why": "A tight null eliminates the field's only stated positive hypothesis about this model's background signal. Held below 5 because it requires the equivalence margin to be prespecified and because a null on a measurement as noisy as LAA-950 will always attract a power objection."
    },
    "novelty_confidence": {
      "value": 4,
      "why": "Cap lifted. The specific link - Sybil's score against quantitative emphysema - was NOT_FOUND across seven distinct queries, and both interpretation papers explicitly leave the background term unmeasured, one of them naming emphysema as an untested intuition. Held at 4 rather than 5 because Regression Concept Vectors already occupy the general methodology, because at least six published works already exploit NLST paired-kernel reconstructions for harmonization, and because the searches did not cover RSNA, SPIE, Medical Physics or thoracic-imaging conference abstracts."
    }
  },
  "priority_score": 4.35,
  "priority_arithmetic": "0.20*4 (feas) + 0.15*4 (ident) + 0.15*4 (med) + 0.10*5 (legwork) + 0.10*5 (interest) + 0.10*5 (clarity) + 0.10*4 (neg) + 0.05*5 (data) + 0.05*4 (novelty) = 0.80+0.60+0.60+0.50+0.50+0.50+0.40+0.25+0.20 = 4.35",
  "regret": {
    "value": 5,
    "why": "The weights download from a hardcoded URL, the images are CC BY, the biomarker is a threshold and a voxel count, and a 2026 ICML paper wrote the hypothesis down in a sentence and moved on. If the answer is yes and nobody checked, it was sitting behind about a week of work."
  },
  "recommendation": "SHORTLIST - highest-ranked candidate in the portfolio.",
  "unverified_claims": [
    "That the patient_id column of Ardila et al. supplementary MOESM5 contains NLST participant IDs joinable to TCIA PatientID. Inferred from Sybil's own script reading that column from that filename; the file was downloaded but not parsed.",
    "That the 6,282 LDCT held-out set in JCO, the 2,328 participants in Simon et al., and the Ardila test set are mutually consistent. Three numbers, no reconciliation attempted.",
    "That pack-years, age and sex survived into the public nlst_prsn table. The table is public and is the CDAS Participant dataset, but its column list was not inspected.",
    "That train-versus-dev is irrecoverable. Based on reading np.random.choice with no seed set in create_nlst_metadata_json.py. Only train-union-dev is reconstructible; this does not affect the design, which needs only the test set.",
    "That lungmask performs acceptably on NLST low-dose screening CT. Untested here.",
    "The claim that the ConvolutionKernel DICOM tag may be uninformative in NLST, with identical labels across reconstructions, comes from a single 2026 preprint (arXiv:2606.12824) and was not independently confirmed. If true, kernel identity must be read from the coded SeriesDescription instead. Cheap to check, but it would silently corrupt the Stage 1 stratification if wrong.",
    "That no CT emphysema-versus-Sybil analysis exists in venues not searched: RSNA, SPIE, Medical Physics, Radiology Artificial Intelligence, and thoracic society abstracts."
  ]
}


===== STAGE TASK =====
Adversarially review the selected idea. Try to reject it for prior-work overlap, weak relevance, concept-label circularity, leakage, confounding, unavailable data, excessive compute, weak negative-result value, or an unclear endpoint.

Also search for an easier version that preserves the interesting question. Explicitly identify any low-hanging-fruit formulation where data, labels, code, or checkpoints already exist.

Open `critique.md` with a **decision header** of at most six lines, before any
detail:

```
FATAL OBJECTION: [one sentence, or NONE]
EVIDENCE: [the specific source, file, or table]
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES / NO
DECISION: ADVANCE TO REVISION | PAUSE | REJECT
```

Then the detailed analysis below it. Long critiques bury their own best points;
the header exists so the decisive objection cannot be lost in section nine.

Close with a constructive section:

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: [one sentence]
RETAINS ORIGINAL MEDICAL MOTIVATION? YES / PARTLY / NO
SHOULD IT BECOME A SEPARATE CANDIDATE? YES / NO
IS IT ACTUALLY WORTH DOING? [one sentence — "a smaller benchmark exists"
is not the same as "the smaller benchmark is worth doing"]
```

A critic that only demolishes produces a portfolio of corpses. Say plainly when
nothing nearby is worth doing; say plainly when something is.

Do not write code.

