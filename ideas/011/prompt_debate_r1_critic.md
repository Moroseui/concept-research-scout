You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/011
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


===== ideas/011/README.md =====
# Idea 011: Forensic anthropologists age a skeleton by its rib cartilage - ask whether an unguided CT model found the same clock

Selected from scouting cycle 004, candidate 4.


===== ideas/011/critique.md =====
FATAL OBJECTION: Conditioning an age prediction on a second age-correlated variable cannot show that the model used that variable; the proposed primary endpoint is non-identifying.
EVIDENCE: The Stage 2 mediation specification in `idea_card.json`, combined with Shabani et al. (PMID 34966360, DOI 10.3389/fendo.2021.785957), which establishes that cartilage calcification itself rises with age.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: PAUSE

# Adversarial review

## 1. The present experiment cannot earn the deliverable sentence

The question is causal—does the model **use** calcified costal cartilage?—but the proposed test is associational. Let chronological age be `Y`, model prediction be `P`, cartilage volume be `C`, and any other visible age marker be `Z`. A model can construct `P` entirely from `Z`; because both `C` and `Z` track `Y`, adding `C` to a regression of `P` will often attenuate an age coefficient or explain variance in `P` even when no cartilage voxel influenced the model. Sex stratification and a competing-mediator panel do not close this path. They only change which correlated proxies enter the regression.

This is concept–label circularity in measurement form: the model is optimized/probed for age, and the proposed concept is selected because it predicts age. Correlation between two age estimators is not evidence that one is inside the other. “More attenuation than aorta, vertebrae, or emphysema” is also not a causal criterion; its ranking depends on measurement error, scale, nonlinear specification, collinearity, and age-range restriction. The card supplies no preregisterable effect or equivalence margin.

Therefore a positive Stage 2 result supports only: **calcified cartilage volume predicts the output of an age predictor**. It does not support: **the model is using calcified cartilage volume**, and especially not the stronger “rather than” clause. This candidate is currently at rung 0 for the model-use claim, not conditional rung 3. X is human-legible, but X has not been linked to the model causally.

## 2. The claimed negative is not decisive

The assertion that “one of [the competing mediators] will be the answer” is false. The model may distribute signal across many weak markers, use an omitted feature (airway geometry, muscle composition, breast tissue, skin, acquisition), or encode interactions that no scalar mediator captures. A null cartilage coefficient can also result from TotalSegmentator error, restricted age range, sex interaction, protocol-dependent thresholding, collinearity, or a weak age probe. This is a **sensitivity-limited** negative, not a decisive negative. Negative-result value should be at most 2 under the rubric, not 4.

A decisive negative requires a validated intervention with a prespecified minimum detectable change: changing cartilage while holding other anatomy fixed fails to change model output beyond an equivalence margin. Even that conclusion must be scoped to the intervention's fidelity and the tested model.

## 3. Stage 0 does not validate the extractor

Recovering the MESA age slope would not establish accurate cartilage segmentation. An age-dependent segmentation error can reproduce an age slope precisely because calcified cartilage is easier to see than uncalcified cartilage. Conversely, failure to reproduce MESA's slope need not indict the extractor: MESA used semi-automated ROIs on cardiac CT in a selected cohort, whereas CT-RATE comprises routine non-contrast diagnostic chest CT. Population, sex mix, slice thickness, kernel, reconstruction count, and referral pathway can change the slope.

The proposed “landmark box” is not segmentation-independent measurement of X. A >180 HU voxel count in a broad rib–sternum box includes rib, sternum, vascular calcium, devices, and potentially contrast or noise. Agreement between two biased measurements would not prove cartilage specificity. The keystone needs direct accuracy assessment against a reference that distinguishes cartilage from adjacent bone across age and calcification severity. That likely requires a small annotation/quality-control set, which is allowed if it is not a large annotation campaign, but contradicts the claim that the current measurement is ready today without asking anyone.

TotalSegmentator's primary paper evaluated 104 structures across heterogeneous CT and reported strong aggregate performance (Wasserthal et al., DOI 10.1148/ryai.230024), but aggregate performance does not inspect costal-cartilage accuracy or age-dependent error. The emergence of a dedicated costal-cartilage segmentation benchmark explicitly motivated by low contrast further weakens the assumption that presence in a class map equals validated measurement (Zhang et al., arXiv:2408.07444; later Expert Systems with Applications, 2026).

## 4. Data and model readiness are overstated

The card correctly admits that the released per-volume age column in CT-RATE has not been inspected. The official CT-RATE paper verifies only that the corpus contains 25,692 non-contrast scans, paired reports, and metadata; it does not establish from the accessible article text that age is released per scan (Hamamci et al., *Nature Biomedical Engineering* 2026, DOI 10.1038/s41551-025-01599-y). Until the actual metadata schema is inspected, the proposed CT-RATE experiment is unavailable, not merely inconvenient.

The model is also hypothetical. CT-CLIP is a report–image foundation model, not an age model. Its official repository now advertises pretrained checkpoints and says inference is possible on smaller GPUs, but the age linear probe has neither a demonstrated accuracy nor a frozen split. Calling it “a linear probe rather than a training run” understates that a new target model must be created and validated. Patient-level splits are mandatory because CT-RATE contains multiple reconstructions per scan and potentially multiple scans per patient.

Text pairing is not direct inference-time leakage—the image encoder receives pixels—but it can make report-correlated visual shortcuts salient. More mundane leakage is worse: age can be encoded in burned-in text, scan fields, reconstruction/protocol choices, or the age-dependent referral population. Those must be audited. A same-institution random patient split does not exclude them.

Compute is manageable only after narrowing. Full TotalSegmentator inference over tens of thousands of reconstructions is unnecessary and wasteful; duplicate reconstructions must not be treated as independent observations. CT-CLIP's repository states that training needs an 80 GB A100 at batch size 8, although inference can use smaller GPUs. The proposed frozen-encoder route is plausible on Colab, but only after checkpoint loading and embedding extraction are demonstrated on a small set.

## 5. Prior-work overlap and relevance

The biological finding is occupied. Shabani et al. quantified >180 HU bilateral costal-cartilage calcium in 2,305 MESA participants and measured sex-specific age gradients (PMID 34966360). Zhang et al. already used clinical multislice CT costal cartilage to estimate adult age (PMID 28717963, DOI 10.1007/s00414-017-1646-y). Lu et al. trained deep models directly on costal-cartilage CT representations in 2,700 subjects (PMID 37231070, DOI 10.1007/s00330-023-09761-3). The novel delta is therefore only whether a whole-chest model independently relies on this known marker.

The card also understates whole-chest CT age precedent. Azarfar et al. trained an unguided chest-CT age model on 13,824 NLST scans, externally tested it on 1,849 local scans, and reported lung-region activation and association of CT-age acceleration with lung-cancer risk (PMID 37418109, DOI 10.1007/s11548-023-02989-w). That is closer than the radiograph precedent and removes the need to borrow the existence of an age-prediction gap from another modality. No public checkpoint or official code was located in this review, so it is prior work, not yet a reusable asset.

Medical relevance is modest but real only if tied to biological-age interpretation: if a clinically prognostic “CT age” is mostly chronological cartilage mineralization, its apparent biological-aging meaning changes. As written, however, CT-RATE chronological-age prediction has no demonstrated clinical endpoint. The forensic story is engaging but does not itself create a radiology consequence.

## 6. Confounds the proposed design does not identify

- **Scanner/vendor, acquisition, reconstruction, site:** all can affect thresholded calcium and model embeddings. Stratification cannot isolate them when age and protocol are imbalanced. Multiple reconstructions must be collapsed or used as a robustness analysis, never counted as independent cases.
- **Position and habitus:** mask-based volume is not automatically invariant. Truncation, field of view, inspiratory level, body size, and anterior chest coverage affect both the denominator and available cartilage.
- **Disease prevalence and referral pathway:** “not applicable because age has no prevalence” is incorrect. Diseases and indications have age-dependent prevalence and can supply easier age signals; routine CT referral creates the correlation structure the model learns.
- **Label leakage:** DICOM/burned-in annotations, protocol choices, and report-aligned pretraining need explicit audits. Report-text pretraining alone is not proof of leakage, but it makes a report-age audit necessary.
- **General calcium burden:** regression adjustment for aortic calcium does not distinguish local cartilage use from a distributed calcium detector.

The design rules out none of these sufficiently for rung 2. A multicohort external test can address site/referral dependence; within-volume interventions are needed for local use; paired reconstructions can test reconstruction robustness.

## 7. Easier formulations and available assets

### Low-hanging fruit, conditional on one schema check

The smallest version preserving the question is a **localized intervention study on a frozen CT-CLIP age probe**, using one reconstruction per patient from CT-RATE validation rather than segmenting the full corpus. Assets now verified from official sources are: CT-RATE volumes/reports and patient-grouped naming, public CT-CLIP code and advertised pretrained checkpoints, and a free TotalSegmentator costal-cartilage class. The missing load-bearing asset remains the released per-scan age field. If it exists, a few hundred age-stratified, sex-stratified cases can first establish probe signal and intervention sensitivity.

The primary readout should be paired change in predicted age after a local, anatomically constrained cartilage intervention, compared with volume-, location-, and attenuation-matched control interventions. At minimum include: cartilage intervention; adjacent rib/sternum control; aortic-calcium control; and random anterior-soft-tissue control. Preserve an untouched patient-level test split and preregister an equivalence margin. Because deletion is OOD, use several interventions that agree—local intensity replacement sampled from age/sex-matched low-calcification anatomy, calcification-only replacement inside a validated mask, and complementary retention—with artifact detectors and sham transformations. This is harder scientifically than mediation but much smaller computationally.

This remains imperfect: synthetic editing may create OOD signal, and an image-only CT-CLIP probe may be weak. Agreement across matched interventions and external replication would move it to rung 1; protocol/site robustness would be needed for rung 2; only then could the named X support rung 3.

### Existing-data alternative that does not preserve the model-use question

NLST is the obvious age-labelled whole-chest CT corpus: TCIA lists 26,254 subjects and age demographics, and Azarfar et al. already trained on 13,824 scans. But complete clinical linkage requires an approved CDAS project/data-transfer agreement, the image collection is about 11.9 TB, and no reusable checkpoint was found. Thus it is not lower-hanging under this charter. A small automated-cartilage-versus-age benchmark on NLST would merely replicate known biology and is not worth promoting as a separate candidate.

## 8. Required revision gates

1. Inspect the actual CT-RATE metadata schema and one joined image–age row. If age is absent or cannot be linked at patient/scan level, pause until another confirmed corpus is found.
2. Demonstrate a useful frozen-encoder age probe with patient-level splits and one reconstruction per scan; define “useful” before fitting.
3. Replace mediation as the primary endpoint with paired, matched localized interventions and an equivalence margin. Mediation may remain descriptive only.
4. Validate cartilage localization across age and calcification severity on a small reference set; an external cohort slope is not segmentation validation.
5. Audit burned-in text, report age mentions, protocol/vendor imbalance, reconstruction duplication, truncation, and sex. Replicate across at least one site/corpus before any rung-2 claim.
6. Rewrite the deliverable without “rather than” unless interventions show cartilage effects exceed every named matched control. A defensible interim sentence is: “For this model and intervention family, changing calcified costal cartilage changes predicted age more than matched changes to adjacent bone, aortic calcium, or anterior soft tissue.”

## Decision rationale

This does **not** die like the annotation-provenance candidates: chronological age can be an administrative measurement if the released field is verified. It does repeat the wrong-keystone pattern of ideas 005/006: the easy facts—class exists, cartilage predicts age, model predicts age—do not establish the needed fact that a change in cartilage causally changes this model's output under an in-distribution intervention. The current endpoint is fatally non-identifying, but the scientific question survives a change in experimental design. Therefore: pause, do not reject.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: In a frozen whole-chest CT age model, do anatomically constrained changes to calcified costal cartilage cause larger paired age-prediction changes than matched interventions to adjacent bone, aortic calcium, and anterior soft tissue?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes—if a released age field and usable frozen age probe pass cheap gates, the controlled intervention directly tests whether a clinically interpretable CT-age signal is a known developmental clock rather than merely another correlate of age.


===== ideas/011/debate.md =====
# Debate transcript



===== ideas/011/idea_card.json =====
{
  "id": "C4",
  "search_mode": "C",
  "entry_point": 1,
  "title": "Forensic anthropologists age a skeleton by its rib cartilage - ask whether an unguided CT model found the same clock",
  "question": "Does a chest-CT age model that was never told where to look recover the costal cartilage calcification clock, such that conditioning on calcified cartilage volume attenuates its age prediction more than conditioning on the aging markers a radiologist would name first?",
  "deliverable_sentence": "The chest-CT age model is using calcified costal cartilage volume - the same structure a forensic anthropologist scores to age an unidentified body - rather than aortic calcification, vertebral bone density or emphysema.",
  "rung": {
    "current": 3,
    "why": "Costal cartilage calcification is a structure a radiologist sees on every chest CT and has a name for, and its volume is a threshold measurement in cubic millimetres.",
    "what_would_move_it_up": "Nothing above rung 3. What would strengthen it: showing the model's residual age error carries the sex-specific pattern the forensic literature describes, which is a hard-to-fake prediction - though see the contradiction flagged below, which weakens this test more than I would like."
  },
  "X_measurement": {
    "X": "Calcified costal cartilage volume - the volume of voxels above a fixed Hounsfield threshold inside the costal cartilage mask - reported both absolutely in cubic millimetres and as a fraction of total cartilage volume.",
    "how": "TotalSegmentator's default 'total' task, class 117 costal_cartilages, then threshold. Apache-2.0, no license key.",
    "citations": "Segmentation: Wasserthal J et al., Radiology: Artificial Intelligence 2023, DOI 10.1148/ryai.230024, class map inspected directly in totalsegmentator/map_to_binary.py. Threshold and prior volumetry: Shabani M, Pishgar F, Akhtarkhavari S et al., Front Endocrinol 2021;12:785957, PMID 34966360, DOI 10.3389/fendo.2021.785957, in MESA at n=2,305: 'The volume of bilateral CCC was quantified in high-density pixels (threshold of Hounsfield Unit>180)'.",
    "could_I_compute_it_today_without_asking_anyone": "Yes. Free tool, free class, a threshold, a voxel count.",
    "published_age_gradient_to_calibrate_against": "MESA reports a '2.6% increase per each year [95%CI: 2.0-3.2%]' in females and '1.5% [1.0-2.1%]' in males, with median volume 1158 mm3 in females versus 3054 mm3 in males. Having a published per-year slope means the measurement can be validated before it is used to explain anything."
  },
  "suspected_signal": "Costal cartilage undergoes progressive dystrophic and metaplastic calcification through adult life, converting a structure that is invisible at soft-tissue window in a young adult into a high-attenuation, spatially extensive, bilaterally symmetric structure in an older one. It is a developmental clock rather than a disease marker, which is what distinguishes it from every aging feature a radiologist would name first - aortic calcification, vertebral height loss, emphysema, coronary calcium - all of which are pathological and therefore confounded by comorbidity rather than tracking chronology. It sits in the anterior chest, in the field of view of every chest CT ever acquired, at an attenuation that separates cleanly from surrounding soft tissue.",
  "keystone_prerequisite": "Costal cartilage can be segmented on ordinary ungated chest CT by a free tool, AND a public chest-CT corpus provides per-scan patient age across a range wide enough to fit an age model - so that a model's age prediction and a cartilage calcification volume exist for the same scans.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_evidence": "The first clause is INSPECTED_TRUE and is not the problem. TotalSegmentator's map_to_binary.py was read directly and the 'total' class map contains 116: 'sternum', 117: 'costal_cartilages'; the README confirms 'total: default task containing 117 main classes' and lists it among tasks 'Openly available for any usage (Apache-2.0 license)', unlike tissue_types, heartchambers_highres and coronary_arteries which require a license key. The second clause is NOT inspected and that is why the compound status is NOT_INSPECTED. The CT-CLIP paper reports a per-scan age range of 18 to 102 for CT-RATE, which is the wide span this candidate needs, but the metadata CSV column headers are behind the HuggingFace gate and returned HTTP 401; only VolumeName, RescaleSlope, RescaleIntercept, XYSpacing and ZSpacing are confirmed to exist, from the authors' own inference script. So I have confirmed that ages were RECORDED and not that a per-volume PatientAge column is RELEASED. As a Mode C candidate this cap is accepted rather than argued around, per the charter.",
  "keystone_residual_assumption": "Two, and the second is the one that would actually sink it. First, that TotalSegmentator's costal cartilage class performs acceptably on the corpus in question - it exists in the class map, which says nothing about its accuracy on a structure whose whole point is that it changes attenuation dramatically with age, and a segmenter that under-segments uncalcified cartilage in the young would manufacture the age gradient it is meant to measure. That failure mode is specific, plausible, and would produce a beautiful false positive. It must be checked by segmenting a fixed anatomical volume defined by rib and sternum landmarks INSTEAD OF by the cartilage mask, as a segmentation-independent replication. Second, that a chest CT reconstructed for diagnosis resolves the cartilage adequately at the slice thickness of the corpus. Neither is inspected.",
  "rung_reached": {
    "value": 3,
    "conditional_on": "The segmentation-independent replication agreeing with the mask-based measurement. Without it, the claim is about a segmentation tool rather than about anatomy."
  },
  "dies_like_prior": "It does not die like the annotation-provenance candidates: age is an administrative field recorded at registration, not a judgment anyone made by looking at the image, so there is no reader, no session, and no peer exposure. It does not die like idea 006, since nothing is ablated or edited. The failure mode it genuinely shares with idea 005 is the WRONG-KEYSTONE structure, and I am naming it rather than waiting for critique: the easy checkable fact is that a costal cartilage class exists, and I checked it and it is true; the fact my inference actually needs is that the class measures cartilage calcification rather than measuring the segmenter's own age-dependent behaviour. That is stated as the first residual assumption and it is, on reflection, the real keystone.",
  "closest_prior_work": [
    {
      "citation": "Lu T, Deng ZH et al. Forensic age estimation based on costal cartilage CT using deep learning.",
      "identifier": "Eur Radiol 2023;33(11):7519, PMID 37231070, DOI 10.1007/s00330-023-09761-3",
      "verification": "INSPECTED",
      "what_it_did": "n=2,700, ages 20 to 70, volume-rendered and maximum-intensity-projection multimodal deep learning: 'The best-performing multi-modality model obtained the lowest MAEs of 3.78 in males and 3.40 in females', against a manual visual scoring method at 8.90 and 6.42.",
      "what_it_did_not_do": "This is the most dangerous prior work for the candidate and it must be confronted rather than minimized. It establishes that a model CAN estimate age from costal cartilage - but it TRAINED ON CROPPED COSTAL CARTILAGE RECONSTRUCTIONS, so the model was told exactly where to look. The question here is the inverse and it is the one this program exists to ask: does a model given a whole chest CT and only an age label FIND that structure on its own. Those are different claims, but the delta is narrower than I would like and a reviewer could reasonably say the interesting part - that cartilage carries age - is already known."
    },
    {
      "citation": "Shabani M, Pishgar F, Akhtarkhavari S et al. Costal Cartilage Calcification in MESA.",
      "identifier": "Front Endocrinol 2021;12:785957, PMID 34966360, DOI 10.3389/fendo.2021.785957",
      "verification": "INSPECTED",
      "what_it_did": "Semi-automated HU>180 volumetry in 2,305 MESA participants with sex-stratified per-year age gradients, inter-reader reliability 88.7.",
      "what_it_did_not_do": "Uses the measurement as a cardiovascular risk marker on gated coronary-calcium scans, and the quantification is SEMI-automated with manual ROIs on a gated protocol. The open corner is fully automated volumetry on ordinary UNGATED chest CT - which is a narrow corner, and I would rather say so now than have it discovered in review. An entire MESA line follows this paper (Radiol Cardiothorac Imaging 2025 PMID 41342680; Acad Radiol 2025 PMID 40764198; Eur Radiol 2026 PMID 40782222), so the measurement itself is well occupied."
    },
    {
      "citation": "MacPherson M, Goh V, Montana G et al. Deep learning age estimation from chest radiographs versus radiologists.",
      "identifier": "arXiv:2207.01302, DOI 10.1007/978-3-031-16449-1_25, MICCAI 2022",
      "verification": "INSPECTED",
      "what_it_did": "The documented model-beats-human gap this candidate's entry point rests on: 'the regression model achieves an R2 of 0.94, MAE 3.53 years' against 'the radiologists achieve R2 of 0.27 with MAE 11.84 years'. Independently replicated in Japan by Ieki et al., Commun Med 2022, PMID 36494479, with seven clinicians at 'MAE 10.06 [95% CI, 9.17-10.94] years'.",
      "what_it_did_not_do": "Is on RADIOGRAPHS, not CT, and offers no explanation of the signal. NOT_FOUND, across three queries: any human-versus-model free age estimation on whole chest CT. The one adjacent CT comparison is anatomically narrow and shows essentially no gap once the human has a validated scoring system - Wesp et al., Int J Legal Med 2024, PMID 38286953, clavicle CT, model MAE 1.65 years versus human 1.84 years. So the gap motivating this candidate is borrowed from an adjacent modality, and if a human chest-CT baseline is needed it would have to be collected."
    },
    {
      "citation": "Sipahioglu et al. Age estimation from chest CT with window-specific deep learning.",
      "identifier": "Forensic Sci Int 2026, PMID 42172947, DOI 10.1016/j.forsciint.2026.113014",
      "verification": "INSPECTED",
      "what_it_did": "n=1,278, ages 20 to 80, MAE 4.89 years, and reports that 'The bone-window model achieved the lowest MAE among single-window approaches, emphasizing the role of skeletal features', with Grad-CAM.",
      "what_it_did_not_do": "Points at skeletal features with a saliency method and a window ablation rather than measuring any quantity. It is the closest existing answer to this candidate's question and it stops precisely where measurement would begin - which is the standard failure this charter names."
    },
    {
      "citation": "Rejtarova O et al., Forensic Sci Int 2009, PMID 19646830; Zhang S et al., Sci Rep 2017, PMID 28592818; Middleham et al., Clin Anat 2015, PMID 25534066.",
      "identifier": "as listed",
      "verification": "INSPECTED (all three)",
      "what_it_did": "Rejtarova established the sex-dimorphic ossification pattern - male 'peripheral ossification pattern', female 'central lingual ossification pattern' - and Zhang confirmed it on dual-energy CT in 154 patients: 'An increasing C pattern of cartilage was displayed in females, while P type preferred in males as age increased.'",
      "what_it_did_not_do": "And here is the contradiction I am not going to bury, because it damages the candidate's best identifiability test. Middleham et al. applied Rejtarova's method to 41 Scottish cadavers and sexed ZERO males correctly. Separately, Goh and Anderson, JBMR Plus 2025, PMID 39697522, report by pQCT that 'there was more calcification volume in cartilage of females than males' - the OPPOSITE direction to MESA's 1158 versus 3054 mm3. The sex-specific pattern is therefore not a reliable enough fingerprint to serve as the confirmatory test I originally wanted it to be, and identifiability is scored down accordingly rather than the test being quietly kept."
    }
  ],
  "existing_assets": [
    "TotalSegmentator costal_cartilages in the free default task.",
    "A published per-year age gradient in a 2,305-person cohort, sex-stratified, to validate the extractor against before it is used.",
    "CT-RATE with a reported 18-to-102 age span and the CT-CLIP encoder, so an age model is a linear probe on frozen embeddings rather than a training run.",
    "Competing mediators all measurable with the same free tool - aorta for calcification, vertebrae for trabecular attenuation, lungs for LAA%-950 - so the comparison set costs one extra segmentation pass."
  ],
  "smallest_decisive_experiment": "Three stages, and the first is the go/no-go the keystone demands. Stage 0: confirm a per-volume age column is actually released, then run TotalSegmentator on 200 volumes spanning the age range and check that calcified cartilage volume reproduces the published per-year gradient of about 2.6 percent in females and 1.5 percent in males. If the extractor cannot recover a known, published, sex-stratified age slope, nothing downstream means anything and the candidate stops here. Stage 1: fit an age model as a linear probe on frozen CT-CLIP embeddings, which needs no training run and no architecture choices, and record its predictions on held-out scans. Stage 2, the actual question: mediation of the model's age prediction through calcified cartilage volume, against a pre-registered panel of competing mediators measured by the same tool - aortic calcification volume, vertebral trabecular attenuation, LAA%-950, and total heart volume. The claim is comparative, not absolute: cartilage must attenuate the prediction MORE than the markers a radiologist would name first, or the candidate has not earned its sentence. Stage 3, the segmentation-independent replication named in the residual: repeat the measurement inside a fixed anatomical box defined by rib and sternum landmarks rather than by the cartilage mask, to show the result is about anatomy rather than about the segmenter's age-dependent behaviour.",
  "standing_confounds_addressed": {
    "scanner_and_vendor": "PARTLY ADDRESSED by stratification, conditional on the metadata columns existing. A high-attenuation threshold measurement is less kernel-sensitive than a low-attenuation one, which helps.",
    "acquisition_protocol": "NOT ADDRESSED. Contrast phase in particular could affect the threshold measurement at the cartilage boundary.",
    "reconstruction": "PARTLY ADDRESSED - a 180 HU threshold on a high-contrast structure is far more kernel-robust than the minus 950 HU threshold C1 depends on, which is a real advantage of this X.",
    "site": "NOT ADDRESSED, single-institution corpus.",
    "positioning": "ADDRESSED by construction - the measurement is defined by an anatomical mask, so it is invariant to where the patient sits in the frame.",
    "habitus": "NOT ADDRESSED, and it is live: body size correlates with both cartilage volume and with age-related change. Mitigated by reporting the calcified FRACTION of cartilage as well as the absolute volume, since the fraction is size-normalized by construction.",
    "prevalence": "NOT APPLICABLE - the outcome is chronological age, which has no prevalence.",
    "referral_pathway": "NOT ADDRESSED, and it matters more than usual here: who gets a chest CT is strongly age-dependent and indication-dependent, so the age distribution is not a population age distribution.",
    "label_leakage": "PARTIALLY LIVE and worth naming - if age appears in the radiology report and the corpus's text was used in pretraining the encoder, an embedding-based age probe could be reading a textual association rather than an anatomical one. The linear probe is fit on IMAGE embeddings only, but CT-CLIP's image encoder was trained against report text, so this cannot be fully excluded and should be stated."
  },
  "alternative_explanations": [
    "The segmenter, not the anatomy. Named as the real keystone above; addressed only by the Stage 3 landmark-box replication, and a positive result without that replication should not be believed.",
    "Cartilage calcification is a proxy for general vascular and dystrophic calcification, so the model is reading calcium everywhere and cartilage is merely one convenient readout. PARTLY EXCLUDED by the competing-mediator panel, which includes aortic calcification specifically - but the two are correlated and the comparison is relative rather than clean.",
    "Sex, not age. The measurement is strongly sex-dimorphic - by a factor of about 2.6 in MESA - and models predict sex from chest CT near ceiling, so an apparent age mediation could partly be a sex pathway. EXCLUDED only by fitting everything sex-stratified from the start, which must be pre-registered rather than added later.",
    "Honest self-assessment. 'The model rediscovered the forensic anthropologist's clock' is the most seductive sentence in this portfolio and it is doing more work than the evidence will. Two things puncture it: a 2023 paper already showed deep learning can age costal cartilage, and MESA already showed the volumetry tracks age, so the genuinely new part is only that an UNGUIDED model converges on it. That is a narrower claim than the sentence implies, and I have scored novelty confidence 2 rather than dressing it up."
  ],
  "anticipated_negative": {
    "classification": "decisive",
    "reasoning": "Provided Stage 0 passes - the extractor reproduces the published age gradient - a null in Stage 2 is genuinely informative: it says that an unguided chest-CT age model is NOT using the structure that forensic science validated and that a bone-window ablation study pointed toward, which redirects the search to the competing mediators measured in the same pass. The comparative design is what makes the negative decisive rather than empty, because the competing mediators are measured simultaneously and one of them will be the answer. If Stage 0 fails, the study produces a feasibility result instead, which the charter also counts as success."
  },
  "cross_domain": {
    "borrowed_construct": "Age-at-death estimation from costal cartilage calcification in forensic anthropology and forensic radiology, where the marker has been scored on skeletons and post-mortem CT for decades.",
    "measurement_it_implies": "Segment costal cartilage, threshold at a fixed Hounsfield value, take the volume, stratify by sex, and compare against a published per-year gradient before using it for anything.",
    "what_changes_if_the_analogy_is_dropped": "The candidate becomes a different and worse study. Without forensic anthropology you would ask what a radiologist thinks makes a chest look old, and you would measure aortic calcification, vertebral height and bone density, emphysema, and thymic involution - every one of which is a DISEASE marker whose relationship to chronological age is mediated by comorbidity, so a positive would be uninterpretable between aging and illness. Forensic science's whole problem is estimating age in people about whom nothing else is known, which forced it toward markers that are developmental rather than pathological, and costal cartilage is the one that happens to sit inside a chest CT field of view. Concretely different code: you run TotalSegmentator's costal cartilage class and threshold at 180 HU, which nobody in radiology AI does, and you stratify by sex from the outset because the forensic literature says the pattern differs. It also supplied the sex-dimorphism confirmatory test - which, as recorded above, the same literature then undermined by contradicting itself. That is what a live analogy looks like as opposed to a decorative one: it changed the measurement, and it also cost me a test I wanted."
  },
  "remaining_legwork": [
    "Confirm a per-volume age column exists in the gated CT-RATE metadata. Minutes after the gate, and it is the keystone.",
    "Stage 0 extractor validation against the published MESA gradient on 200 volumes. One week including segmentation time.",
    "Build the landmark-box replication measurement. One week, and it is not optional.",
    "Fit the linear age probe on frozen embeddings and pre-register the mediator panel and sex stratification. One week.",
    "Time to first decision: Stage 0 within two weeks, and it can kill the candidate before any modelling."
  ],
  "scores": {
    "mechanism_clarity": {
      "value": 5,
      "why": "A specific physical quantity - volume of voxels above 180 HU inside the costal cartilage - measured by a named free tool with a named class number, with a published per-year gradient in a 2,305-person cohort to validate against, and a named biological process for why it changes with age. This is the top of the rubric's description and I do not think it is arguable."
    },
    "identifiability": {
      "value": 3,
      "why": "The competing-mediator panel is measured in the same pass with the same tool, which is the design's strength, and the landmark-box replication separates anatomy from segmenter behaviour. But the mediation is observational, cartilage calcification correlates with vascular calcification, sex is a strong parallel pathway, and the sex-dimorphism test I wanted as confirmation is undermined by a direct contradiction in the source literature. Three is honest."
    },
    "interest": {
      "value": 4,
      "why": "A model given nothing but an age label converging on the marker forensic science spent decades validating is a genuinely good result, and the cross-domain route is not one this field would have taken. Held below 5 because a 2023 paper already aged costal cartilage with deep learning, so the surprise is about convergence rather than about the clock."
    },
    "medical_relevance": {
      "value": 3,
      "why": "Plausible utility rather than clear consequence. Understanding what a biological-age model reads matters for whether such scores mean anything clinically, and there is a real forensic application. But no management decision changes, and costal cartilage calcification is not itself actionable."
    },
    "clarity": {
      "value": 4,
      "why": "The question names the structure, the tool, the comparison set and the comparative criterion. Held below 5 because 'recovers the clock' is operationalized as relative mediation strength against a panel, which is a threshold-free comparison that will need a pre-registered decision rule to avoid being argued about afterwards."
    }
  },
  "mode_c_priority_score": 3.9,
  "mode_c_priority_arithmetic": "0.30*5 (mechanism) + 0.25*3 (ident) + 0.20*4 (interest) + 0.15*3 (med) + 0.10*4 (clarity) = 1.50+0.75+0.80+0.45+0.40 = 3.90",
  "reported_outside_the_score": {
    "feasibility": {
      "value": 3,
      "why": "CAPPED at 3, keystone NOT_INSPECTED. The uncapped estimate would be about 3 anyway: TotalSegmentator over thousands of volumes is many GPU-hours, and Stage 0 could fail."
    },
    "novelty_confidence": {
      "value": 2,
      "why": "CAPPED at 3 but scored 2 on the evidence, which is a deliberate mark-down rather than a cap. MESA has semi-automated volumetry at n=2,305 and Eur Radiol has deep-learning age-from-cartilage at n=2,700, both with sex-stratified results. The residual gap is narrow - fully automated volumetry on ungated chest CT, used to explain an unguided model - and 'likely covered in part' is the honest reading."
    },
    "data_readiness": {
      "value": 3,
      "why": "Behind the CT-RATE click-through, with the needed column unverified."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "Mediation analysis is standard; a decision rule for 'recovers the clock' is not, and must be written."
    },
    "negative_result_value": {
      "value": 4,
      "why": "Decisive, conditional on Stage 0 passing, because the competing mediators are measured simultaneously."
    }
  },
  "regret": {
    "value": 3,
    "why": "Worth considering. If it is true it is a lovely result, but nothing downstream is blocked by not knowing."
  },
  "recommendation": "DEVELOP FURTHER, DO NOT SHORTLIST YET - Stage 0 is cheap and the candidate should not be funded past it until the extractor reproduces the published age gradient.",
  "unverified_claims": [
    "That CT-RATE releases a per-volume PatientAge column. The paper reports an 18 to 102 age range, so ages were recorded; the column list is gated and unread. This is the keystone.",
    "That TotalSegmentator's costal cartilage class is accurate on ungated diagnostic chest CT, and specifically that its accuracy does not itself vary with the degree of calcification. This is the real keystone and it is unverified.",
    "That the MESA per-year gradients transfer to an ungated non-cardiac-protocol corpus with different slice thickness.",
    "That the sex-dimorphic ossification pattern is reliable. Two inspected sources contradict each other on the direction of the sex difference in volume, and a third failed to replicate the pattern for sex estimation entirely.",
    "That a linear probe on frozen CT-CLIP embeddings gives a usable age model. Untested; the encoder was trained against report text rather than for age.",
    "That no unguided-model age-attribution study exists. Searches did not cover forensic radiology conference proceedings, where this community publishes heavily."
  ]
}


===== STAGE TASK =====
Attack the idea. Append one round to `debate.md` in the idea folder.

Format your append exactly as:

```
## Round N — CRITIC

**Position:** [one sentence: what you think is wrong]

**Argument:** [the reasoning, with specifics — dataset, metric, prior paper,
mechanism. Not "this may be difficult."]

**What would change my mind:** [a concrete thing the proposer could show]

**Status:** OPEN | CONCEDED | IRREDUCIBLE DISAGREEMENT | CONVERGED
```

Rules:

- Read every prior round. Do not repeat an objection already answered — if
  the proposer's rebuttal was adequate, write CONCEDED and say which argument
  moved you and why.
- Concede only in response to an *argument*, never to insistence or repetition.
  If the proposer restated their claim more confidently without new evidence,
  say so and hold your position.
- **Run the identity check on every amendment you receive.** Ask whether the
  revised design still answers the original question. If it does not, say so
  and make that your objection — it outranks any remaining technical point.
  A feasible study that no longer tests the original claim should be rejected
  and its replacement spawned as a separate candidate, not approved.

- One objection per round, your strongest remaining one. Do not spray.
- If you and the proposer have a real difference of judgement that no
  available evidence can settle, write IRREDUCIBLE DISAGREEMENT and name the
  experiment or fact that *would* settle it. This is a good outcome, not a
  failure.
- Write CONVERGED only if you now think the idea is sound AND you have no
  remaining objection worth stating.
- Append only. Never edit earlier rounds.



===== DEBATE STATE =====
You are codex. Your interlocutor is claude.
This is round 1. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript


