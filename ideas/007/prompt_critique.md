You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/007
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


===== ideas/007/README.md =====
# Idea 007: The same patient, twice, ten minutes apart, differing only in how much air is in the lungs

Selected from scouting cycle 004, candidate 3.


===== ideas/007/idea_card.json =====
{
  "id": "C3",
  "search_mode": "B",
  "entry_point": 2,
  "title": "The same patient, twice, ten minutes apart, differing only in how much air is in the lungs",
  "question": "When one patient receives an inhale and an exhale breath-hold CT in a single session on one scanner at matched exposure, how much do a chest-CT foundation model's finding scores move, and do they move as a function of total lung volume in litres?",
  "deliverable_sentence": "The model is using the degree of lung inflation - total lung volume and the mean parenchymal attenuation it sets - as a component of its emphysema, mosaic attenuation, atelectasis and lung opacity scores, so a patient who cannot hold a full breath receives a different diagnosis.",
  "why_unasked": "Radiologists correct for inspiratory effort constantly and without comment; it is one of the first things taught about reading a chest study, and an expiratory scan that looks like ground glass is a standing joke rather than a research question. Because the correction is so automatic in humans, nobody has asked whether the model does it. The benchmark cannot reveal it either: every corpus used to evaluate these models has ONE scan per patient, so inflation state is a fixed property of each case and is silently absorbed into the label. The confound is invisible by construction, and it becomes visible only when you have the same patient twice.",
  "rung": {
    "current": 3,
    "why": "Degree of inspiration is a named physiological state that every chest radiologist assesses on every study, and total lung volume is its calibrated measure in litres.",
    "what_would_move_it_up": "Nothing above rung 3. What would strengthen it: replication in a non-oncological population, since the available corpora are lung cancer and radiotherapy patients, and extension to a second foundation model to show the behaviour is not one checkpoint's quirk."
  },
  "X_measurement": {
    "X": "Total lung volume in litres, with mean lung attenuation in Hounsfield units as the co-primary because it is the channel through which inflation most plausibly acts.",
    "how": "lungmask (Apache-2.0, pip-installable) or TotalSegmentator's free lung lobe classes give the mask; volume is a voxel count times voxel volume and mean attenuation is an average inside it. LAA%-950 is reported alongside as the clinically named quantity that inflation is known to corrupt.",
    "citations": "Effect size anchored in real paired patients: Eur Radiol 2002, PMID 12386770, DOI 10.1007/s00330-002-1514-z, n=155 paired full-inspiration and full-expiration HRCT, reporting mean lung density of minus 813 HU at full inspiration and minus 736 HU at full expiration - a 77 HU shift. Controlled-inflation within-subject support: Madani, Van Muylem, Gevenois, Radiology 2010;257(1):260-268, PMID 20663967, imaging the same subjects at 100, 90, 80, 70 and 50 percent of vital capacity and concluding that 'submaximal inspiration induces underestimation of pulmonary emphysema'.",
    "could_I_compute_it_today_without_asking_anyone": "Yes. Lung segmentation and a voxel count, on a corpus that downloads without any agreement."
  },
  "suspected_signal": "Inflation is a physical dilution. At full inspiration the same tissue mass occupies more volume, so every parenchymal voxel contains proportionally more air and reads lower in Hounsfield units; at expiration the parenchyma is denser, vessels crowd together, dependent regions collapse, and the appearance converges on what ground glass, mosaic attenuation and atelectasis look like. A model trained on single-phase scans has no way to distinguish a patient with genuinely dense lung from a patient who exhaled, unless it has learned an inflation-invariant representation - and nothing in its training objective asked it to.",
  "keystone_prerequisite": "A public corpus, with no application or data transfer agreement, provides at least two breath-hold chest CT acquisitions of the same patient in one session at different inflation states, with matched acquisition parameters and whole-thorax coverage - so that inflation is the only thing that differs and both images are real full-dose reconstructions rather than phase bins.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "TCIA collection CT-vs-PET-Ventilation-Imaging, DOI 10.7937/3ppx-7s22, collection page inspected and quoted: 'For this study, 20 lung cancer patients underwent exhale/inhale breath hold CT (BHCT), free-breathing four-dimensional CT (4DCT) and Galligas PET ventilation scans in a single session on a combined 4DPET/CT scanner.' Breath holds were at 'approximately 80% of maximum inhalation and exhalation' with audiovisual biofeedback, at 120 kVp, 120 mAs, 0.8 pitch, 10 second breath-hold - so exposure is matched between the two arms. Coverage is 'approximately 50 cm from the pharynx to the stomach', which is whole-thorax rather than a radiotherapy crop. Non-contrast, DICOM, 14.93 GB, CC BY 4.0, fully public with no application. Scanner is a single Siemens Biograph mCT.S/64. The same session additionally provides a 10-phase 4DCT, giving a within-patient dose-response with ten points. Source paper Eslick et al., Radiother Oncol 2018;127:267-273, PMID 29290405. Every alternative was checked and gated: DIR-Lab requires a Qualtrics request form and an emailed Dropbox password; COPDGene requires an ancillary study proposal and a DUA with National Jewish Health; LTRC requires BioLINCC committee approval; EMPIRE10 is effectively defunct. Learn2Reg Task 2 is ungated but preprocessed and resampled with unverified HU retention.",
  "keystone_residual_assumption": "Having verified that two matched-exposure breath-hold acquisitions exist per patient, I am still assuming that the score difference between them is attributable to INFLATION rather than to everything else that moves when a patient breathes. Two things move: the tumour and any adjacent atelectasis change position and can change apparent size, and the diaphragm and mediastinum shift. This is load-bearing for the causal claim, and it is why the design does not rest on the paired difference alone. The mitigation is built in rather than bolted on: total lung volume is used as a CONTINUOUS exposure across the 10-phase 4DCT of the same patient in the same session, so the claim becomes a within-patient dose-response slope rather than a two-point difference, and a tumour-position artifact would not produce a monotone relationship with lung volume across ten phases. Also unverified: slice thickness is not stated on the collection page, and n is 20.",
  "rung_reached": {
    "value": 3,
    "conditional_on": "The dose-response holding across the 4DCT phases and not only between the two breath holds. A two-point difference alone would support rung 1 - the model is sensitive to something that changes with breathing - but not the named claim."
  },
  "dies_like_prior": "No prior failure mode applies. No annotation enters anywhere: the primary readout is the same model's score on the same patient under two acquisitions, compared to itself, which is the exact structural move that let idea 004 survive and it is used here in its purest form - there is no ground truth in this study at all. It does not die like idea 006 either, and the contrast is worth stating precisely, because this candidate is what idea 006 should have been: idea 006 tried to create a counterfactual image by deleting the patient, and died because the deleted image was off-manifold. Here the counterfactual was created by the scanner. Both images are real, both are full-dose, both are diagnostic-quality chest CT, and the intervention was performed by the patient's own diaphragm. There is no distribution-shift defence to make because there is no distribution shift.",
  "closest_prior_work": [
    {
      "citation": "Eslick EM et al. CT ventilation imaging derived from breath hold CT exhibits good regional accuracy with Galligas PET.",
      "identifier": "Radiother Oncol 2018;127:267-273, PMID 29290405; TCIA collection DOI 10.7937/3ppx-7s22",
      "verification": "INSPECTED (collection page; abstract-level for the paper)",
      "what_it_did": "Acquired the paired breath-hold CTs to derive regional ventilation maps and validate them against Galligas PET.",
      "what_it_did_not_do": "Used the inflation contrast as a physiological signal to be measured. It never runs a diagnostic model of any kind across the pair. The dataset was built for ventilation imaging and is being repurposed here as a natural experiment, which is the whole reason it is available and unclaimed."
    },
    {
      "citation": "Foundation model embeddings for quantitative tumor imaging biomarkers (test-retest stability on RIDER).",
      "identifier": "PMID 40502795, Research Square rs-6630446",
      "verification": "SEARCH_SUMMARY_ONLY",
      "what_it_did": "Measured embedding stability across two scans of the same patient 15 minutes apart in 26 patients, reporting cosine similarity of 0.97 to 1.00 for most models, with Merlin at 0.81 and CT-CLIP at 0.93.",
      "what_it_did_not_do": "This is the nearest existing measurement and it is a weak proxy. RIDER's repeat scans are free-breathing, so inflation varies uncontrolled and unmeasured - the variation is noise rather than a designed contrast, and the study reports embedding similarity rather than per-finding scores. It cannot say whether the instability it sees IS inflation. That CT-CLIP sits at 0.93 rather than 1.00 is a reason to expect this candidate to find something."
    },
    {
      "citation": "Kavuri et al. Effect of inspiration level on quantitative emphysema (virtual imaging trial).",
      "identifier": "Acad Radiol 2025;32(8):4913-4921, PMID 40348708, DOI 10.1016/j.acra.2025.04.042",
      "verification": "INSPECTED",
      "what_it_did": "Using DukeSim on 20 emphysema models at 70 to 100 percent of full inspiration: 'LAA-950 underestimat[es] the amount of emphysema by 1.44 +/- 0.32% (mean +/- standard error) for every 1-liter deviation from full inspiration.'",
      "what_it_did_not_do": "Quantifies the effect on the BIOMARKER, not on a model. It is simulation rather than patients, so it is cited as a magnitude expectation with the 2002 and 2010 papers as the empirical anchors. It also supplies the per-litre scaling this candidate's dose-response should be compared against - if the model's score moves less per litre than LAA-950 does, the model is more inflation-robust than the standard index."
    },
    {
      "citation": "Cardiothoracic ratio variation with respiration on CT.",
      "identifier": "PMID 26151361",
      "verification": "INSPECTED",
      "what_it_did": "Reports CT-CTR of 44.3 +/- 5.1 inspiratory versus 48.8 +/- 5.5 expiratory - a 4.5 point swing straddling the conventional 0.5 threshold.",
      "what_it_did_not_do": "Concerns humans and the heart rather than models and lungs, but it is the reason this candidate should also score CT-CLIP's Cardiomegaly output on the same pairs. That makes C3 a partial, free, within-patient probe of C2's question, and the overlap should be exploited rather than hidden."
    }
  ],
  "existing_assets": [
    "TCIA CT-vs-PET-Ventilation-Imaging: 20 patients, paired matched-exposure breath-hold CT plus 10-phase 4DCT in one session, CC BY 4.0, 14.93 GB, no gate whatsoever.",
    "TCIA 4D-Lung, DOI 10.7937/K9/TCIA.2016.ELN8YGLE, CC BY 3.0: 20 more patients, 10 phases, 82 4DCT sessions including weekly repeats in 14 subjects - a second, independent, ungated corpus, with the caveat that its phases share one binned acquisition so noise is not matched and coverage is a radiotherapy extent.",
    "The CT-CLIP ClassFine checkpoint, per C2's keystone.",
    "lungmask for the exposure measurement.",
    "Published per-litre and per-phase effect sizes for the biomarker, so the model's sensitivity has something to be compared against rather than being reported in a vacuum."
  ],
  "smallest_decisive_experiment": "One afternoon of inference on a 15 GB ungated download. For each patient compute total lung volume and mean lung attenuation on the inhale and exhale breath-hold scans, run ClassFine on both, and report the paired per-finding score change with the lung volume change as the exposure. The primary readout is entirely label-free: the within-patient slope of score against lung volume in litres, per finding, with the paired difference as a secondary summary. Then use the 10-phase 4DCT from the same session to convert the two-point contrast into a ten-point dose-response inside each patient, which is what separates 'inflation' from 'something else that moved'. Report the model's per-litre sensitivity next to the published per-litre sensitivity of LAA%-950 (1.44 percent per litre), so the result is expressed as whether the model is more or less inflation-robust than the standard quantitative index rather than as an uncalibrated number. Pre-register which findings are expected to move - emphysema, mosaic attenuation, atelectasis, lung opacity, consolidation - and which are not - medical material, arterial wall calcification, coronary artery wall calcification - because the calcification findings are an internal negative control that should be flat, and if they move too, the model is sensitive to the acquisition rather than to inflation specifically. That control costs nothing and it is what turns a suggestive result into an identified one.",
  "standing_confounds_addressed": {
    "scanner_and_vendor": "ELIMINATED BY CONSTRUCTION. One scanner, one patient, one session.",
    "acquisition_protocol": "ELIMINATED BY CONSTRUCTION for the breath-hold pair - 120 kVp, 120 mAs, 0.8 pitch on both arms.",
    "reconstruction": "ELIMINATED for the breath-hold pair. Not eliminated across the 4DCT phases, where each phase is reconstructed from a different subset of projections and therefore has a different noise realization - which is exactly why the breath-hold pair is primary and the phases are the dose-response.",
    "site": "ELIMINATED BY CONSTRUCTION.",
    "positioning": "ELIMINATED BY CONSTRUCTION - the patient does not move off the table between the two breath holds.",
    "habitus": "ELIMINATED BY CONSTRUCTION - the same body.",
    "prevalence": "ELIMINATED BY CONSTRUCTION - within-patient comparison, so there is no population to differ.",
    "referral_pathway": "ELIMINATED BY CONSTRUCTION.",
    "label_leakage": "NOT APPLICABLE - no labels are used anywhere in this study.",
    "what_is_left": "Exactly two things: tumour and atelectasis motion between the breath holds, handled by the ten-point dose-response and the calcification negative controls; and the generalizability of a 20-patient lung cancer and radiotherapy population. This is the shortest residual-confound list in the portfolio and it is the candidate's main argument."
  },
  "alternative_explanations": [
    "The score change reflects tumour and atelectasis displacement, not inflation. PARTLY EXCLUDED by the monotone dose-response across ten phases and by restricting a sensitivity analysis to the lung contralateral to the tumour.",
    "The score change reflects general acquisition sensitivity rather than inflation specifically - the model is simply jittery. EXCLUDED by the calcification negative controls, which have no physiological reason to move with inflation. If they move as much as the parenchymal findings, the finding is jitter and the candidate has produced a different and less interesting result, which the design will detect rather than hide.",
    "Breath-hold at 80 percent of maximum is a smaller contrast than the full-inspiration-to-full-expiration range that the 77 HU literature figure comes from, so the exposure may be weaker than the anchor implies. NOT EXCLUDED - it is a real reason a null could be underpowered, and it must enter the minimum-detectable-effect calculation rather than being discovered afterwards.",
    "Honest self-assessment. The appeal here is genuinely in the design rather than the sentence, which is unusual for this portfolio and is why identifiability is the highest score I have given. The weakness is not identification but SCALE: 20 patients is a small study, and a null would be argued about. The result that would matter most - a large, monotone, per-finding inflation sensitivity - is also the one this design is best powered to detect, which is a fortunate alignment but should be stated as a limitation of what the study can rule out rather than what it can find."
  ],
  "anticipated_negative": {
    "classification": "sensitivity-limited",
    "reasoning": "With 20 patients the paired design is well powered for large within-subject effects and poorly powered for small ones, and the breath-hold contrast is narrower than the full vital-capacity range. A null therefore needs an explicit equivalence margin expressed in the same units as the comparison - the model's score change per litre against LAA-950's published 1.44 percent per litre - and a minimum-detectable-effect computed before any inference is run. It is honestly type 2, not type 1, and I decline to upgrade it on the strength of the design's cleanliness: clean identification does not create statistical power. The 4D-Lung corpus adds 20 more patients and 82 sessions if more is needed, at the cost of matched noise."
  },
  "cross_domain": {
    "applicable": false,
    "note": "No borrowed construct. The design is native to radiology and the analogy budget is spent in C4 and C5."
  },
  "remaining_legwork": [
    "Download 14.93 GB from TCIA via NBIA Data Retriever. No agreement, no form. Hours.",
    "Confirm slice thickness and that both breath-hold series are present for all 20 patients - the collection page does not state thickness. Half a day.",
    "Accept the CT-RATE gate for the ClassFine checkpoint, shared with C2 and idea 004.",
    "Confirm the breath-hold volumes preprocess sanely through the CT-CLIP pipeline - they are 50 cm coverage against a pipeline that crops to 480x480x240 at 0.75 by 0.75 by 1.5 mm, so more of the abdomen and neck will be in frame than in CT-RATE. This is a real risk of exactly the kind this program keeps hitting, and it should be checked before any scores are interpreted. One day.",
    "Pre-register the expected-to-move and expected-not-to-move finding lists and the equivalence margin.",
    "Time to first decision: three to four days after the checkpoint is available, and the data itself is a same-day download."
  ],
  "scores": {
    "clarity": {
      "value": 5,
      "why": "One patient, two scans, one named exposure measured in litres, one score per finding. The comparison is stated completely in the question."
    },
    "identifiability": {
      "value": 5,
      "why": "Scanner, vendor, protocol, site, positioning, habitus, prevalence, referral pathway and label leakage are all eliminated by the acquisition itself rather than by statistical adjustment, and reconstruction is eliminated for the primary pair. The exposure is continuous and measured, the dose-response has ten points within each patient, and there are pre-registered negative-control findings that should not move. This is what isolating a mechanism looks like and I do not think the portfolio contains a cleaner design."
    },
    "medical_relevance": {
      "value": 5,
      "why": "A model whose finding scores move with breath-hold quality will systematically misread frail patients, the elderly, and anyone in pain - precisely the people most likely to be scanned. Radiologists already discount expiratory scans by hand; if the model does not, the failure is silent and clinically consequential."
    },
    "interest": {
      "value": 4,
      "why": "The design is elegant and the question is one every chest radiologist will immediately understand and have an opinion about. Held below 5 because a positive result confirms rather than overturns what an experienced reader would guess, and the surprise is in the magnitude rather than the direction."
    },
    "prior_legwork": {
      "value": 3,
      "why": "The corpus exists and is ungated, the model is released, and there are published biomarker effect sizes to calibrate against - but nothing has been done on this question, so there is no analysis protocol to inherit and the finding-level expectations must be written from scratch."
    },
    "feasibility": {
      "value": 4,
      "why": "Cap lifted, keystone INSPECTED_TRUE. A 15 GB ungated download and inference-only on a released checkpoint. Held to 4 by dependence on the CT-RATE gate for the weights and by the preprocessing-compatibility risk of a 50 cm field of view."
    },
    "data_readiness": {
      "value": 5,
      "why": "CC BY 4.0, no application, no form, no password, DICOM, 14.93 GB. The only genuinely unrestricted dataset in this portfolio."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "Paired within-subject slopes and dose-response regression are standard, but there is no accepted metric for per-finding inflation sensitivity and the comparison against LAA-950's per-litre figure has to be constructed. Custom metrics needed."
    },
    "negative_result_value": {
      "value": 3,
      "why": "Capped by the sensitivity-limited classification. A tight null would be a genuine and useful robustness result for a model the field is building on, but at n=20 with a sub-maximal breath-hold contrast, tightness is the thing in doubt."
    },
    "novelty_confidence": {
      "value": 4,
      "why": "Cap lifted. NOT_FOUND across seven distinct queries for any work applying a chest-CT foundation model across respiratory phases or measuring finding-sensitivity to inflation, and the nearest proxy does not control inflation at all. Held at 4 rather than 5 because robustness evaluations of foundation models are proliferating quickly and this is a natural thing for a benchmark paper to include as one panel."
    }
  },
  "priority_score": 4.25,
  "priority_arithmetic": "0.20*4 (feas) + 0.15*5 (ident) + 0.15*5 (med) + 0.10*3 (legwork) + 0.10*4 (interest) + 0.10*5 (clarity) + 0.10*3 (neg) + 0.05*5 (data) + 0.05*4 (novelty) = 0.80+0.75+0.75+0.30+0.40+0.50+0.30+0.25+0.20 = 4.25",
  "regret": {
    "value": 5,
    "why": "A free 15 GB download and an afternoon of inference, answering a question that bounds every finding score these models produce, on a dataset that has been sitting on TCIA under CC BY since 2022 for a completely different purpose."
  },
  "recommendation": "SHORTLIST - best identifiability in the portfolio, and the only candidate whose data has no gate at all.",
  "unverified_claims": [
    "Slice thickness of the breath-hold CTs. NOT_FOUND on the collection page.",
    "That both inhale and exhale breath-hold series are present and usable for all 20 patients. The collection describes the protocol; per-patient completeness was not checked.",
    "That 50 cm pharynx-to-stomach coverage passes through CT-CLIP's preprocessing without pathological cropping. This is the candidate's main technical risk and it is unverified.",
    "That the 4D-Lung collection has adequate thoracic coverage for a second cohort. NOT_FOUND on its collection page; radiotherapy planning extent is assumed, not verified.",
    "That the 4D-Lung and CT-vs-PET 4DCT phases are retrospectively binned from a single acquisition. Strongly supported by the collection descriptions quoting phase-based binning, but the source paper's methods section could not be opened.",
    "The RIDER test-retest embedding stability figures, including CT-CLIP at 0.93. SEARCH_SUMMARY_ONLY.",
    "The exact per-step effect sizes in Madani et al. 2010. The conclusion sentence is inspected; the per-vital-capacity-step numbers are paywalled."
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

