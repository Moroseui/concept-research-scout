You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/013
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


===== evidence/ledger_digest.md =====
# Ledger digest (auto-generated -- do not edit; run `python scout.py ledger digest`)

18 tracked ideas. Latest state per idea; full history in ledger.jsonl.

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **scout-006-c04** [NOVEL_UNVERIFIED, audited 2026-08-10] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-006-c05** [NOVEL_UNVERIFIED, audited 2026-08-10] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two
- **scout-006-c03** [INCREMENTAL, audited 2026-08-10] -- An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver

## Ideas

- **idea-001** [REJECTED/DEBATED/baseline] -- Have lung nodule concept models been validated against radiologist opinion rather than against disease? -- killed: DATA_INSUFFICIENT -- data: {"primary": "LIDC-IDRI via The Cancer Imaging Archive", "license": "CC BY 3.0", 
- **idea-002** [PAUSED/DEBATED/baseline] -- Dermoscopic concepts predicted from non-dermoscopic photographs: genuine visibility or shortcut? -- data: {"primary": "Derm7pt paired clinical/dermoscopic images", "source": "github.com/
- **idea-003** [ACTIVE/DEBATED/baseline] -- Does BI-RADS concept intervention survive realistic clinician behaviour, and does it beat simply reading the BI-RADS category? -- data: {"primary": "BUS-BRA (Zenodo 8231412, CC BY 4.0) for the external and baseline a
- **idea-004** [ACTIVE/DEBATED/baseline] -- The free test-retest experiment already inside CT-RATE: duplicate reconstructions of the same acquisition
- **idea-005** [PAUSED/DEBATED/baseline] -- Eight named characteristics, or three latent ones? Discriminant validity of the LIDC concept vocabulary
- **idea-006** [PAUSED/DEBATED/baseline] -- Ask the chest-CT foundation model to diagnose a volume with no patient in it
- **idea-007** [ACTIVE/DEBATED/baseline] -- The same patient, twice, ten minutes apart, differing only in how much air is in the lungs
- **idea-008** [ACTIVE/DEBATED/baseline] -- Two papers say Sybil's residual signal is the background, one of them names emphysema, and neither measured it
- **idea-009** [ACTIVE/DEBATED/baseline] -- Murray's cube law says how a branching tree should be built - ask whether the risk model is reading the lung's departure from it
- **idea-010** [ACTIVE/DEBATED/baseline] -- Cardiomegaly on a CT report is admitted gestalt - ask whether the model has quietly turned it into millilitres
- **idea-011** [ACTIVE/DEBATED/baseline] -- Forensic anthropologists age a skeleton by its rib cartilage - ask whether an unguided CT model found the same clock
- **idea-012** [SHORTLISTED/DEBATED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **idea-013** [SHORTLISTED/SCOUTED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **scout-006-c01** [SHORTLISTED/SCOUTED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **scout-006-c02** [SHORTLISTED/SCOUTED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **scout-006-c03** [SCOUT_ONLY/SCOUTED/baseline] -- An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver
- **scout-006-c04** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-006-c05** [SCOUT_ONLY/SCOUTED/baseline] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two


===== ideas/013/README.md =====
# Idea 013: CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity

Selected from scouting cycle 006, candidate 2.


===== ideas/013/idea_card.json =====
{
  "id": "C2",
  "search_mode": "B",
  "entry_point": 2,
  "title": "CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity",
  "question": "When CT-CLIP fires its 'Coronary artery wall calcification' label, is the score a monotone function of automated coronary Agatston, and does it dissociate from aortic-wall calcium measured in the same volume - so that the coronary label tracks coronary calcium specifically rather than total vascular calcium?",
  "deliverable_sentence": "CT-CLIP is using coronary artery calcium as a localised quantity: its coronary-calcification score rises with automated coronary Agatston and is not merely a readout of total calcium load, because it separates from aortic-wall calcium in the same scan.",
  "rung": {
    "current": 3,
    "why": "Coronary calcification is a named radiological finding; the design also tests whether the model's OWN label means what it says.",
    "what_would_move_it_up": "Nothing above rung 3; the localisation dissociation is what makes the rung-3 claim strong rather than a bare correlation."
  },
  "X_measurement": {
    "X": "Coronary Agatston (AI-CAC) as the primary; aortic-wall calcium (volume of voxels >130 HU inside the TotalSegmentator 'aorta' mask) as the dissociating comparison.",
    "how": "AI-CAC for coronary calcium; TotalSegmentator free 'total' task (Apache-2.0) segments the aorta, then threshold-count calcium inside it. Both are threshold/segmentation operations, no annotation.",
    "citations": "AI-CAC: Hagopian et al., NEJM AI 2025, DOI 10.1056/AIoa2400937. TotalSegmentator: Wasserthal et al., Radiol Artif Intell 2023;5(5):e230024, DOI 10.1148/ryai.230024 (aorta in the free task). CT-CLIP labels: Hamamci et al., arXiv:2403.17834 ('our dataset distinguishes between Arterial wall calcification and Coronary artery wall calcification').",
    "could_I_compute_it_today_without_asking_anyone": "Yes for both measures. CT-CLIP checkpoints require a CC-BY-NC-SA click-through gate but no application.",
    "known_weakness_of_X_stated_up_front": "CT-RATE is non-contrast (good for calcium HU) but slice thickness ranges up to 6 mm, which coarsens small coronary calcifications; AI-CAC expects full-FOV chest CT, which CT-RATE mostly is, but truncated fields would bias coronary coverage."
  },
  "suspected_signal": "Both labels were trained from RadBERT-parsed reports, so the model has a supervised target for calcium. The question is whether it learned calcium as a LOCATION-BOUND finding (coronary vs aortic) or as a texture detector for any dense vascular fleck. Calcified plaque is hyperdense and anatomically placed; a model that truly localises will track coronary Agatston with partial independence from aortic calcium.",
  "keystone_prerequisite": "CT-CLIP's coronary-calcification score can be regressed against a per-scan automated coronary Agatston on CT-RATE volumes (primary), AND coronary and aortic calcium vary independently ENOUGH in the CT-RATE population for the localisation dissociation to be identifiable (secondary) - because if the two calcium loads are nearly collinear, the dissociation cannot be estimated regardless of how well each is measured.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "The two labels exist verbatim in the paper ('Arterial wall calcification' and 'Coronary artery wall calcification'). ClassFine/CT-LiPro outputs exactly the 18-label set. Checkpoints (CT_LiPro_v2.pt etc.) are in models/CT-CLIP-Related/ inside the CC-BY-NC-SA CT-RATE HF repo (click-through gate). AI-CAC's stated domain is non-gated non-contrast chest CT = CT-RATE. TotalSegmentator's free task segments the aorta. All primary-readout ingredients are confirmed runnable.",
  "keystone_residual_assumption": "The primary (score vs coronary Agatston, monotone) is fully supported by INSPECTED facts. The SECONDARY dissociation carries the real residual: I verified that coronary and aortic calcium are each measurable, but I did NOT verify that they vary independently in CT-RATE. Coronary and aortic calcium share atherosclerosis and are positively correlated (population r commonly ~0.4-0.6), which is enough to identify a dissociation but not guaranteed in this specific cohort. This is the same shape as the scout-004 lesson (LAA and BV5 co-vary): 'both are measurable' is not 'both vary independently'. Stage 0 must estimate the joint distribution before the dissociation is trusted; if collinear, the candidate honestly retreats to the fidelity-only claim.",
  "rung_reached": {
    "value": 2,
    "conditional_on": "The fidelity regression is rung 1 (the score IS the model's calcium output, so a monotone dependence on measured calcium is use, not correlation with an external label). The rung-3 localisation SENTENCE is earned only if coronary calcium predicts the coronary score with aortic calcium partialled out; if the two are collinear or the coronary label tracks total calcium, the claim is 'the model uses vascular calcium' (still rung 3, but a coarser X)."
  },
  "use_vs_association": "Use is not in doubt for the primary, because the score being regressed IS the model's own calcification output - a monotone dependence on measured Agatston is the model using calcium by definition. The association-vs-use worry lives entirely in WHICH calcium (coronary vs total), which the localisation dissociation resolves.",
  "dies_like_prior": "Resembles idea 010 (cardiomegaly -> heart volume, CT-CLIP score vs machine measurement), which is ACTIVE, not killed; C2's distinct move is the two-label localisation dissociation that idea 010's single label cannot support. No annotation-provenance issue: the primary readout regresses the model's own score against a voxel Agatston, and the RadBERT report label never enters the primary.",
  "closest_prior_work": [
    {
      "citation": "Hamamci et al., CT-CLIP / CT-RATE foundation model.",
      "identifier": "arXiv:2403.17834",
      "verification": "INSPECTED (v3 HTML)",
      "what_it_did": "Trained the model and reported the 18-label ClassFine performance, including both calcification labels.",
      "what_it_did_not_do": "Never tested whether the calcification scores track a measured calcium score, nor whether the two labels dissociate by anatomy."
    },
    {
      "citation": "Kenia, McNamara, Lotter, 'Anatomy Contextualized Adaption of CT Foundation Models'.",
      "identifier": "arXiv:2607.27154 (2026)",
      "verification": "SEARCH_SUMMARY_ONLY",
      "what_it_did": "Combined CT-CLIP and Merlin with TotalSegmentator anatomy for zero-shot binary finding classification.",
      "what_it_did_not_do": "No correlation of model scores against any continuous geometric or densitometric biomarker; no calcium quantification."
    },
    {
      "citation": "Hagopian et al., AI-CAC.",
      "identifier": "NEJM AI 2025, DOI 10.1056/AIoa2400937",
      "verification": "INSPECTED",
      "what_it_did": "Released the calcium scorer.",
      "what_it_did_not_do": "Never applied to a foundation model's calcification label."
    }
  ],
  "existing_assets": [
    "CT-CLIP ClassFine checkpoints (CC-BY-NC-SA, click-through).",
    "CT-RATE non-contrast chest CT volumes (same gate).",
    "AI-CAC (MIT).",
    "TotalSegmentator free task (Apache-2.0) for the aorta mask.",
    "The paper's own ClassFine AUROC for the two calcification labels as reference."
  ],
  "smallest_decisive_experiment": "Stage 0 (2 days): on a CT-RATE validation slice, run AI-CAC and aortic-calcium counting and estimate their joint distribution - go/no-go for the dissociation. Stage 1 (fidelity, no labels): regress CT-CLIP's coronary-calcification score on coronary Agatston across deciles; a model using calcium shows a monotone gradient. Stage 2 (localisation): partial the coronary score on coronary Agatston with aortic calcium held, and cross-check the 'Arterial wall calcification' score against aortic calcium - a localising model shows a double dissociation.",
  "standing_confounds_addressed": {
    "scanner_and_vendor": "CT-RATE is largely single-institution; vendor retained as a covariate.",
    "acquisition_protocol": "Non-contrast throughout; slice thickness varies and is a covariate (thick slices blur small coronary calcium).",
    "reconstruction": "Kernel affects calcium blooming; recorded per volume where available and used as a covariate.",
    "site": "Limited institutional diversity in CT-RATE; stated as a scope limitation.",
    "positioning": "Weak effect; calcium measured inside anatomical masks.",
    "habitus": "Noise via body size; covariate.",
    "prevalence": "Single-cohort; no between-population contrast.",
    "referral_pathway": "CT-RATE is clinically-referred chest CT - a genuine caveat, since indication may correlate with calcium burden; addressed only as a limitation.",
    "label_leakage": "N/A to primary (score vs voxel Agatston). The training label came from reports, but the readout is the score against an independent measurement, not against the report."
  },
  "alternative_explanations": [
    "The coronary score tracks TOTAL vascular calcium, not coronary specifically - the central alternative, resolved by the aortic-calcium dissociation.",
    "The score is effectively binary/saturated (present/absent), so a 'monotone' relationship is really a step - handled by the ordinal coarsening and by inspecting the score distribution.",
    "Slice-thickness confound: thick-slice scans blur coronary calcium and may drop the score for measurement reasons - covariate-adjusted and stratified.",
    "The appealing 'the model localises calcium' sentence would also arise if aortic and coronary calcium simply differ in average magnitude; only the partialled dissociation, not the marginal correlations, supports it."
  ],
  "anticipated_negative": {
    "classification": "sensitivity-limited",
    "reasoning": "If the coronary score does not track Agatston, it may be because the ClassFine head is near-binary and saturates, not because the model ignores calcium - so a null needs the score-distribution diagnostic and a minimum-detectable-slope to be interpretable. A clean null on the DISSOCIATION (coronary score tracks total calcium equally) is more decisive and would say the label does not localise."
  },
  "cross_domain": null,
  "remaining_legwork": [
    "Accept the CT-RATE gate and pull the validation split + checkpoints: 1 day.",
    "Stage 0 joint-distribution check: 2 days.",
    "Run AI-CAC + aortic counting across the split: 3 days.",
    "Time to first decision: ~2 weeks."
  ],
  "scores": {
    "clarity": {
      "value": 5,
      "why": "Names the model, both labels, both measurements, and the dissociation that identifies the claim."
    },
    "identifiability": {
      "value": 4,
      "why": "The score is the model's own output so use is not in question; the two-label dissociation isolates coronary calcium from total calcium. Held below 5 by the residual (coronary/aortic calcium co-vary) and by CT-RATE's clinical-referral confound."
    },
    "medical_relevance": {
      "value": 3,
      "why": "A fidelity/localisation audit of a model's label - useful for trusting the model's calcium reporting, but less directly consequential than a discovery."
    },
    "interest": {
      "value": 4,
      "why": "Whether a foundation model's finding label is anatomically meaningful or just a hyperdensity detector is a sharp, generalisable question."
    },
    "prior_legwork": {
      "value": 5,
      "why": "Open model, open images (gated but free), two open measurement tools, published reference AUROCs."
    },
    "feasibility": {
      "value": 4,
      "why": "Cap lifted (INSPECTED_TRUE). Inference-only; both tools run. Held by the CT-RATE gate and thick-slice coronary blurring."
    },
    "data_readiness": {
      "value": 4,
      "why": "CT-RATE is a free click-through, non-commercial gate; not fully open."
    },
    "evaluation_readiness": {
      "value": 5,
      "why": "Agatston, ordinal agreement, partial regression, double dissociation - all standard with reference values."
    },
    "negative_result_value": {
      "value": 3,
      "why": "A fidelity null is sensitivity-limited (label may saturate); a dissociation null is more decisive. Averaged to 3."
    },
    "novelty_confidence": {
      "value": 4,
      "why": "Cap lifted. No prior test of CT-CLIP calcification-score fidelity or localisation was found. Held at 4 because the score-vs-biomarker method is established prior art and a very recent preprint could exist."
    }
  },
  "priority_score": 3.95,
  "priority_arithmetic": "0.20*4 + 0.15*4 + 0.15*3 + 0.10*5 + 0.10*4 + 0.10*5 + 0.10*3 + 0.05*4 + 0.05*4 = 0.80+0.60+0.45+0.50+0.40+0.50+0.30+0.20+0.20 = 3.95",
  "regret": {
    "value": 4,
    "why": "The two-label natural experiment is sitting in the released model and nobody has run it; the tools are free."
  },
  "unverified_claims": [
    "Coronary and aortic calcium vary independently enough in CT-RATE (Stage 0).",
    "AI-CAC runs acceptably on 6 mm-slice CT-RATE volumes.",
    "The exact ClassFine score scale/saturation behaviour for the calcification heads.",
    "CT-RATE FOV consistently includes full coronary coverage (inferred from 'chest CT', not verbatim)."
  ],
  "track": "baseline"
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

