You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/012
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
- **idea-012** [SHORTLISTED/CRITIQUED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **idea-013** [SHORTLISTED/SCOUTED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **scout-006-c01** [SHORTLISTED/SCOUTED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **scout-006-c02** [SHORTLISTED/SCOUTED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **scout-006-c03** [SCOUT_ONLY/SCOUTED/baseline] -- An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver
- **scout-006-c04** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-006-c05** [SCOUT_ONLY/SCOUTED/baseline] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two


===== ideas/012/README.md =====
# Idea 012: Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan

Selected from scouting cycle 006, candidate 1.


===== ideas/012/critique.md =====
FATAL OBJECTION: The proposed partial association cannot establish that Sybil uses coronary calcium, and the exact published “no visible future-cancer-site nodule” cohort is not reconstructible from the cited release.
EVIDENCE: Sybil JCO 2023 Data Supplement/PMC10419602; public Sybil repository `files/*.csv`, `scripts/data/parse_mdai_annotations.py`, and `sybil/loaders/image_loaders.py` (inspected 2026-08-10).
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: PAUSE

# Detailed adversarial review

## 1. The central inference is association, not use

The card asks whether Sybil's score is “a function of” CAC and promises the sentence “Sybil is using coronary artery calcium.” Its primary identifying analysis is a partial regression of Sybil score on AI-CAC after adjustment for emphysema and BV5. That does not establish use.

A positive coefficient is also expected if Sybil reads any omitted correlate of CAC: chronological age, smoking duration or intensity, aortic calcium, vertebral degeneration, airway disease, cardiac size, image noise/body habitus, or an unmeasured centre/protocol mixture. Adding two selected rivals does not make CAC the causal image feature. Pack-years in particular is not an image-level intervention and is measured with error; residual confounding is almost guaranteed. “Unique variance” is unique only relative to the variables and measurement models in that regression.

The proposed kernel arm does not repair this. As the card correctly admits, changing reconstruction changes calcium blooming, emphysema thresholds, edges, noise, and essentially every texture seen by Sybil. Correlated changes in AI-CAC and Sybil therefore establish reconstruction sensitivity or, at best, generic high-density-channel sensitivity—not CAC-specific use. The design can reach a source-supported statement such as “Sybil score contains information correlated with automated CAC,” but not the charter's rung-3 deliverable.

This objection is repairable only by making a controlled CAC intervention the primary analysis: use the AI-CAC lesion mask to remove or plausibly inpaint calcified coronary lesions while holding all other voxels fixed, with matched interventions in (i) noncoronary high-attenuation lesions and (ii) equally sized coronary regions without calcium. The estimand is the within-scan Sybil-score change attributable specifically to coronary calcium. Counterfactual validity remains a gate: constant-HU deletion would repeat idea 006's OOD failure, so realistic local inpainting, mask-size matching, boundary checks, and negative controls are mandatory.

## 2. The “nodule-free” cohort keystone was not inspected true

Mikhael et al. did not study scans with no nodules in the ordinary sense. Their exploratory analysis excluded cases annotated by their radiologists as having a visible nodule **in the exact location of the subsequently proven cancer**. The paper reports the resulting AUC (2-year 0.81, 95% CI 0.74–0.86), but a published aggregate AUC is not a released case-membership list.

Direct inspection of the public Sybil repository found:

- `files/lung_cancer_dataset.csv` and `files/lung_cancer_metadata.csv` contain headers plus empty placeholder rows, not the NLST split or cohort membership.
- `scripts/data/create_nlst_metadata_json.py` expects an external Ardila split spreadsheet at an internal mount path.
- `scripts/data/parse_mdai_annotations.py` expects an unreleased MD.ai JSON export and an internal `annotation_comments_12062020.csv`.
- the repository README says annotations and splits are available, but the inspected release does not contain the artifacts needed to reproduce the future-cancer-site exclusion.

Thus the card's keystone status must be downgraded from `INSPECTED_TRUE`. The nearest checkable fact was that the paper performed the analysis; the still-assumed load-bearing fact was that outsiders can identify the same scans. They currently cannot from the cited release. This resembles idea 001's `DATA_INSUFFICIENT` failure: a published analysis exists, but the linkable subset needed for the proposed inference is unavailable. It also resembles the recurring wrong-keystone error more strongly than the card acknowledges.

There is an additional endpoint ambiguity. “Nodule-free” implies absence of visible nodules, whereas the published exclusion concerns a visible precursor at the later cancer site and was based on joint expert annotation informed by NLST clinical localization. Incidental nodules elsewhere can remain. The title, question, cohort definition, and deliverable must use the narrower wording.

## 3. Annotation provenance is not absent

CAC itself satisfies the charter: AI-CAC is an independently computable measurement. However, human annotation enters the primary cohort restriction. The Sybil repository states that two thoracic radiologists jointly annotated lesions and were informed by the series/image number and anatomical location of biopsy-confirmed cancers. That is suitable for the authors' stated retrospective sensitivity analysis, but it is neither an independent blinded measurement nor an available machine-computable selection rule.

This is not concept-label circularity—CAC was not Sybil's target label—but the card's statement that “no human rating enters any readout” evades the selection problem. Conditioning on an outcome-informed lesion assessment can also create a selected population whose score–CAC relation does not generalize to screening scans prospectively called nodule-free.

## 4. CAC measurement is feasible, but Stage 0 is underspecified

AI-CAC is genuine reusable prior legwork. Hagopian et al. released code and weights and evaluated non-gated chest CT against paired gated radiology-report Agatston scores (NEJM AI 2025, DOI 10.1056/AIoa2400937; PMID 40746702). TCIA's current NLST collection page lists CT images and a public clinical subset under CC BY 4.0 (DOI 10.7937/TCIA.HMQ8-J677). These parts are verified and materially lower implementation risk.

But the proposed “~40 NLST scans that also have a visually-read ordinal CAC” is not tied to a released per-scan reference table. Watts et al. (PMID 25370000) validates visual CAC prognostically in an NLST sample; citing that paper does not establish that its scan-linked scores are public or joinable to TCIA identifiers. Unless the actual table/schema is inspected, Stage 0 requires new manual reads or author-shared data and violates the advertised no-annotation simplicity.

Transfer is not merely absolute calibration. Scanner era, slice thickness, kernel, motion, and noise can alter false positives and ranks. A rank-only association does not survive arbitrary differential error correlated with reconstruction or Sybil score. Validate AI-CAC on an explicitly obtainable reference set, or limit the claim to AI-CAC's operational output rather than biological CAC.

## 5. Sybil's input transform weakens the Agatston framing

The public inference loader applies a lung window centred at −600 HU with width 1500 HU, clipping all values above approximately +150 HU, converts to 8-bit, resizes in-plane to 256×256, and samples/resamples to 200 slices. Consequently Sybil cannot read the density weighting that defines an Agatston score above the conventional calcium threshold in the same way AI-CAC does. It can still read the presence, area, shape, and location of saturated bright calcium, but “automated Agatston-equivalent score” is not the most faithful mechanistic X.

The revised concept should therefore be coronary calcium **burden visible after Sybil preprocessing**—for example lesion presence and mask area/volume after mapping the AI-CAC mask through the exact transform—with Agatston as a secondary clinical coarsening. This makes a negative more interpretable and aligns the intervention with what the model actually receives.

## 6. Confounds and claim identifiability

Most plausible positive-result alternatives remain:

1. **Shared biological burden:** age, smoking, aortic atherosclerosis, emphysema, vascular pruning, and other degenerative changes cause CAC to mark a diffuse phenotype. The partial regression rules out only the measured linear components of LAA-950 and BV5; it does not rule out the phenotype.
2. **Acquisition/reconstruction/site:** these affect both AI-CAC and Sybil. Metadata adjustment cannot eliminate unobserved site, and site is masked. The kernel arm actively induces this alternative rather than excluding it.
3. **Body habitus/noise:** auto-exposure and attenuation alter calcium detection and the entire Sybil input. Effective mAs is incomplete control.
4. **Outcome/referral/label leakage:** report leakage is not relevant because Sybil sees pixels and Stages 1–2 do not use reports. Trial referral pathway and prevalence are largely fixed by NLST enrollment. These are genuine strengths, but they do not rescue feature identifiability.

A targeted within-scan CAC intervention with anatomical and high-density controls would rule out much of (1)–(3) because the rest of each scan remains fixed. It would not alone establish that the signal is biologically causal for lung cancer; the honest claim is about model use, not disease mechanism.

## 7. Prior-work overlap and relevance

No inspected primary source here directly pre-empts the Sybil-score-versus-CAC question. Mikhael et al. establish Sybil and the exact-site-nodule exclusion (JCO 2023, DOI 10.1200/JCO.22.01345; PMID 36634294). The 2026 “Auditing Sybil” preprint (arXiv:2602.02560) supplies adjacent generative-intervention machinery but, based on its inspected text as recorded in the card, does not quantify CAC. The 2026 HeartLung/MESA cardiac-versus-lung-CT article is adjacent, but the card has only a search-summary-level inspection; novelty confidence cannot rest on an unread abstract/full text. The novelty claim should remain `NOT FOUND in inspected sources`, not “untouched.”

Medical relevance is real but overstated. Finding CAC dependence would change interpretation of Sybil as a lung-cancer risk score and could expose poor transport across populations with different cardiovascular risk. It would not imply that CAC should be “read alongside” Sybil or alter management without showing incremental calibration, transport, or decision impact. The strongest medical consequence is model validity and subgroup transportability, not opportunistic cardiac care.

## 8. Compute and data burden

Inference itself is compatible with a single GPU. The burden is data engineering: NLST contains 11.3 TB in full, cohort reconciliation is unresolved, AI-CAC needs original DICOM while Sybil applies its own transform, and BV5 is described as though it were as turnkey as lungmask without a directly named released implementation or validation plan. Running all three competing ideas jointly is scientifically sensible but not a three-week “one command” study.

The current data-readiness score of 5 and feasibility score of 4 are unjustified while exact cohort membership, the reference CAC table, the test-split join, and the BV5 implementation are uninspected. Under the charter, feasibility and novelty confidence should be capped at 3 until the real keystone is inspected true.

## 9. Negative-result value

The anticipated null from partial regression is **sensitivity-limited**, not decisive. A null can arise from AI-CAC transfer error, Sybil's clipping/downsampling of calcium, collinearity and measurement error in smoking/LAA/BV5, nonlinear or thresholded use, inadequate variation, or subset-selection error. An equivalence margin on Sybil-score SD does not solve errors-in-variables or define a clinically meaningful minimum feature dependence. `negative_result_value` should be at most 2 for the current design.

A well-powered controlled CAC intervention can produce a more decisive negative, conditional on demonstrated intervention fidelity and a positive-control model known to respond to CAC. Without that positive control, even the interventional null remains sensitivity-limited.

## 10. Low-hanging-fruit repair

The easiest useful formulation drops the unreleased exact-site-nodule subset and the cancer endpoint initially. Use an obtainable frozen NLST/Ardila test subset, run the released Sybil ensemble and AI-CAC, map AI-CAC masks through Sybil's exact preprocessing, and compare original scores with realistically CAC-inpainted scores plus matched controls. No clinical labels, pack-years, BV5, mediation, or full 11.3-TB download are required for the primary readout. Public checkpoints and code exist for both models; TCIA permits targeted series download. This directly tests the interesting feature-use question on ordinary screening scans.

This simpler experiment does **not** reproduce the published nodule-excluded residual. It should be treated as a general Sybil mechanism study, with the special residual cohort added only if the authors release case membership or a reproducible public rule is found. An initial association/attention-overlap benchmark is acceptable as a feasibility check, but it is not worth publishing alone and must not be promoted to a rung-3 claim.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: On a frozen public NLST test subset, does realistic removal of AI-CAC-segmented coronary calcium change Sybil's risk score more than size-matched coronary and noncoronary high-density control edits?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes—if counterfactual fidelity and positive controls pass, it directly identifies a named feature used by an open lung-cancer model; a score–CAC correlation alone is not worth doing.


===== ideas/012/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed partial regression and paired-kernel analysis cannot support the deliverable sentence that Sybil is using coronary artery calcium; they identify correlation with CAC and generic reconstruction-sensitive image signal, respectively.

**Argument:** CAC is a marker of a diffuse age/smoking/vascular phenotype that also includes aortic calcium, vertebral degeneration, airway disease, cardiac morphology, body-habitus-dependent noise, and acquisition differences. Conditioning on pack-years, LAA-950, and BV5 only removes the measured components of three selected covariates; it does not turn the remaining AI-CAC coefficient into evidence that Sybil reads coronary lesions. The paired-kernel arm is no stronger: changing kernel jointly changes calcium blooming, emphysema thresholds, edges, and texture throughout the volume, so correlated changes in AI-CAC and Sybil score demonstrate reconstruction sensitivity, not CAC-specific use. This is fatal under the charter because the candidate asserts rung 3 from associative evidence. A targeted within-scan intervention on AI-CAC lesion masks could preserve the core question, but only if realistic inpainting holds all non-CAC content fixed and is compared with size- and attenuation-matched edits in noncalcified coronary regions and noncoronary high-density lesions; simple deletion would repeat idea 006's out-of-distribution failure. Moving that experiment to an ordinary NLST subset would test a general Sybil mechanism, not the original claim about the published future-cancer-site-nodule-excluded residual, so that amendment would fail the identity check unless the title, question, and claim are explicitly narrowed or the replacement becomes a separate candidate.

**What would change my mind:** Show a preregistered, fidelity-validated within-scan CAC inpainting experiment on a reproducibly obtainable version of the stated future-cancer-site-nodule-excluded cohort, with the two matched control edits above and a positive-control model demonstrably sensitive to CAC; the Sybil score change must be specifically larger for coronary-calcium removal than for both controls.

**Status:** OPEN


===== ideas/012/idea_card.json =====
{
  "id": "C1",
  "search_mode": "A",
  "entry_point": 1,
  "title": "Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan",
  "question": "On low-dose CT scans with no visible nodule at the site of the subsequent cancer, where Sybil still reaches a 2-year AUC of 0.81, is its risk score a function of coronary artery calcium - the automated Agatston score computed by AI-CAC on the same scan - after adjustment for the emphysema and vascular measures that are its two rival explanations?",
  "deliverable_sentence": "Sybil is using coronary artery calcium: on nodule-free screening scans its risk score rises with the automated Agatston score, and it does so over and above quantitative emphysema and small-vessel blood volume.",
  "rung": {
    "current": 3,
    "why": "Coronary calcification is a named finding a radiologist reports by name, quantified in calibrated units by a released tool. It is not a region and not an absence.",
    "what_would_move_it_up": "Nothing sits above rung 3. What strengthens the rung-3 claim: the partial-association survives adjustment for pack-years and for the two rival cues, and it holds within the paired-kernel perturbation arm."
  },
  "X_measurement": {
    "X": "Coronary artery calcium, as an automated Agatston-equivalent score, with a zero/non-zero and an ordinal (<100 / 100-400 / >400) coarsening as pre-registered co-primaries because absolute Agatston on ungated LDCT is noisier than on gated scans.",
    "how": "Run AI-CAC (github.com/Raffi-Hagopian/AI-CAC, MIT, weights va_non_gated_ai_cac_model.pth at release v1.0.0) on the same DICOM series; it segments and scores coronary calcium on non-gated non-contrast chest CT. No annotation, no license key, no application.",
    "citations": "Hagopian et al., 'AI Opportunistic Coronary Calcium Screening at Veterans Affairs Hospitals', NEJM AI 2025, DOI 10.1056/AIoa2400937, PMID 40746702 (developed on 446 expert segmentations across 98 VA centres; benchmarked vs paired ECG-gated CAC in 795 patients; non-gated AI-CAC predicted 10-year all-cause mortality). NLST CAC-mortality validity: Watts et al., Coronary Artery Disease 2015;26(2):157-62, PMID 25370000 ('Visual scoring of coronary calcium predicts all-cause and CVD mortality in NLST participants').",
    "could_I_compute_it_today_without_asking_anyone": "Yes. pip-installable/clone, MIT weights, run on a DICOM series. This is the cleanest tool in the portfolio on the charter's test.",
    "known_weakness_of_X_stated_up_front": "AI-CAC was validated on VA low-dose CT, not on NLST; transfer to NLST scanners and the older NLST acquisition era is assumed, not verified (see keystone_residual_assumption). Ungated Agatston is inflated by cardiac motion and by sharp reconstruction kernels (calcium blooming), which is why the perturbation arm uses the kernel deliberately and why a coarsened score is co-primary."
  },
  "suspected_signal": "Calcified coronary plaque is hyperdense (conventionally >130 HU) and spatially fixed to the coronary arteries, so a 3D convolutional encoder can read it directly off calibrated voxels. The link to the endpoint is not assumed: coronary calcium and lung cancer share smoking as a common cause, and in NLST cardiovascular deaths (956) outnumbered lung-cancer deaths (930), so a lung-cancer risk model that has learned a general smoking/vascular-ageing signature would plausibly encode CAC. A positive result says the model found a named cardiovascular substrate on its own inside a lung-cancer task.",
  "keystone_prerequisite": "Sybil's per-scan risk score and a per-scan automated CAC score can be placed side by side on the SAME held-out, nodule-free NLST scans, AND the CAC contribution can be estimated separately from emphysema and small-vessel blood volume - because all three are smoking-driven and mutually correlated, so a design that measures only CAC would attribute shared variance to it.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "Sybil residual is verbatim confirmed - PMC10419602 (JCO 2023;41(12):2191-2200), 'Sybil's performance was hampered by removing visible nodules, obtaining a 2-year AUC of 0.81 (95% CI, 0.74 to 0.86) and a 6-year AUC of 0.69'. Sybil weights and code are MIT with a hardcoded checkpoint URL (established in scout-004 / idea 008). AI-CAC weights are MIT and downloadable (release v1.0.0), its stated input domain is 'routine non-gated, non-contrast chest CT scans' which is exactly NLST. NLST imaging is TCIA CC BY 4.0 with no application; outcomes are public via IDC BigQuery. The three-way separation is buyable: emphysema (LAA-950 by lungmask) and small-vessel blood volume (BV5) are computable on the same scans, so partial associations are estimable.",
  "keystone_residual_assumption": "Having verified that AI-CAC exists, is MIT, and names non-gated non-contrast chest CT as its domain, I am still assuming its calcium scores TRANSFER to NLST-era scanners with acceptable accuracy - it was validated on VA scans, not NLST. This is load-bearing for the magnitude of a positive but not for the study's existence: a rank association between Sybil's score and AI-CAC's score is estimable even if AI-CAC's absolute calibration is off, as long as its per-scan ranking is preserved. The cheap Stage-0 check is to score a few dozen NLST scans that also have a visually-read ordinal CAC (Watts-style) and confirm rank agreement.",
  "rung_reached": {
    "value": 2,
    "conditional_on": "The design as primary is an ASSOCIATION between Sybil's score and CAC; it reaches rung 1 (use) via the partial-association and kernel-perturbation arms, and the rung-3 SENTENCE is earned only if the CAC association survives adjustment for pack-years, emphysema and BV5. If CAC's unique contribution vanishes once emphysema and vessels are partialled out, the honest claim drops to 'Sybil uses a shared smoking/density signature' - rung 1, not the named-calcium sentence."
  },
  "use_vs_association": "Association is separated from use by (a) partialling CAC against emphysema and BV5 so a positive is CAC's UNIQUE variance, and (b) the paired-kernel perturbation - if a within-acquisition kernel change that moves measured CAC also moves Sybil's score, that is use of a density-channel feature, though the kernel moves emphysema too, so this arm proves density-channel use, not CAC-specific use. CAC-specific use rests on the partialling.",
  "dies_like_prior": "No prior kill applies. It resembles ideas 008 (emphysema/Sybil) and 009 (vessels/Sybil), but those are ACTIVE competing explanations, not failures - C1 is the third arm of the same decomposition and its distinct X (calcium) is spatially and physically separable from parenchymal density. It shares nothing with the five annotation-provenance kills (no human rating enters any readout) or with idea 006's intervention-validity failure (no anatomy is deleted or masked; the only manipulation is a real second reconstruction).",
  "closest_prior_work": [
    {
      "citation": "Mikhael et al., Sybil.",
      "identifier": "J Clin Oncol 2023;41(12):2191-2200, PMID 36634294, PMC10419602",
      "verification": "INSPECTED (PMC full text)",
      "what_it_did": "Documented the nodule-free residual: 2-year AUC 0.81 after removing visible nodules at the cancer site.",
      "what_it_did_not_do": "Did not measure any image property of the residual; named no anatomical explanation."
    },
    {
      "citation": "Sobieski et al., Auditing Sybil (S(H)NAP generative interventional attributions).",
      "identifier": "arXiv:2602.02560, ICML 2026 poster 66127",
      "verification": "INSPECTED (full HTML v2)",
      "what_it_did": "Causal attribution of Sybil's risk to pulmonary nodules via 3D diffusion-bridge edits; found a background term and reported only its regression on age.",
      "what_it_did_not_do": "Contains ZERO mentions of calcium, coronary, cardiac, cardiovascular, vessel or vascular - the entire cardiovascular hypothesis for the background term is untouched. It intervenes on nodules only."
    },
    {
      "citation": "Hagopian et al., AI-CAC.",
      "identifier": "NEJM AI 2025, DOI 10.1056/AIoa2400937, PMID 40746702",
      "verification": "INSPECTED (GitHub repo + paper record)",
      "what_it_did": "Released an MIT non-gated CAC scorer, validated against gated CAC and against mortality.",
      "what_it_did_not_do": "Never applied to Sybil or to any lung-cancer risk model."
    },
    {
      "citation": "HeartLung / MESA, 'Sybil AI For Lung Cancer Risk Prediction On Cardiac Versus Lung CT'.",
      "identifier": "J Cardiovasc Comput Tomogr, S1934-5925(26)00145-0 (2026)",
      "verification": "SEARCH_SUMMARY_ONLY (abstract paywalled)",
      "what_it_did": "Ran Sybil ON cardiac CAC-scan field of view versus lung CT to test transfer.",
      "what_it_did_not_do": "The orthogonal/reverse direction - it asks whether Sybil works on CAC scans, NOT whether CAC explains Sybil's signal. Must be cited and distinguished; does not pre-empt C1."
    }
  ],
  "existing_assets": [
    "Sybil weights + inference code (MIT, auto-download).",
    "AI-CAC weights + code (MIT, downloadable).",
    "lungmask (Apache-2.0) for LAA-950; a BV5 pipeline for small-vessel volume.",
    "NLST imaging on TCIA (CC BY 4.0, no application).",
    "NLST outcomes public via IDC BigQuery (nlst_canc).",
    "Published nodule-free benchmark (2-year AUC 0.81) so the residual's size is known.",
    "Ardila test-participant split reused by Sybil (established in idea 008 verification)."
  ],
  "smallest_decisive_experiment": "Stage 0 (2 days, go/no-go): score ~40 NLST scans with AI-CAC and confirm rank agreement against a visual ordinal CAC; confirm the nodule-free held-out subset is reachable. Stage 1 (no labels): on held-out nodule-free NLST scans at a single reconstruction kernel, run Sybil and AI-CAC and estimate the score-vs-CAC association, then the PARTIAL association adjusting for LAA-950 and BV5 - this is the identifying step, because it asks for CAC's unique variance. Stage 2 (perturbation, optional): on paired standard/sharp reconstructions of one acquisition, regress the per-patient change in Sybil's score on the per-patient change in AI-CAC; this proves density-channel use. Stage 3 (confirmatory, optional): mediation of Sybil's score-to-cancer association through CAC using the public candx_days outcome.",
  "standing_confounds_addressed": {
    "scanner_and_vendor": "PARTLY - retained in the public DICOM and used as strata; Stage 2 pairs are within-scanner by construction.",
    "acquisition_protocol": "PARTLY - NLST is protocolised; kVp/effective-mAs recoverable.",
    "reconstruction": "The dominant threat to any density-based X: kernel moves Agatston (blooming) and LAA-950 together. Handled by fixing the kernel in Stage 1 and by making it the manipulated variable in Stage 2.",
    "site": "NOT ADDRESSABLE - NLST screening centre is masked even in the gated release (established scout-004). Permanent limitation for Stages 1/3.",
    "positioning": "Weakly relevant; CAC is anatomically localised inside the coronary mask.",
    "habitus": "Body size drives auto-exposure noise which affects both CAC and LAA; mitigated by effective-mAs covariate and the within-patient Stage 2.",
    "prevalence": "ADDRESSED by construction - single screening cohort, uniform eligibility.",
    "referral_pathway": "ADDRESSED by construction - trial enrolment, not clinical referral.",
    "label_leakage": "N/A to Stages 1-2 (no labels). Stage 3 uses a registry cancer date, which cannot leak from a report into an image."
  },
  "alternative_explanations": [
    "Smoking dose. Pack-years cause CAC, emphysema and cancer. The whole design is built to attack this by partialling; if CAC's unique variance disappears, the honest claim is a smoking signature, not calcium.",
    "Emphysema (idea 008). LAA-950 and vascular measures co-vary with CAC. EXCLUDED as the CAC-specific claim only by partialling; run all three jointly.",
    "Vascular pruning (idea 009). BV5 is inversely related to emphysema and correlated with vascular calcium load. Same resolution: partial associations, reported together.",
    "The appealing sentence 'a lung model secretly reads the heart' is exactly what a shared-smoking-signature model would also produce; the partialling is the only thing that separates them and must gate the write-up."
  ],
  "anticipated_negative": {
    "classification": "decisive",
    "reasoning": "If Sybil's score shows no unique association with CAC after partialling (within a prespecified equivalence margin sized to the score's SD ~0.07), it eliminates coronary calcium as the named residual and concentrates the remaining probability on emphysema/vessels - a decisive narrowing of a three-way question, not a failure to find something."
  },
  "cross_domain": null,
  "remaining_legwork": [
    "Stage 0 rank-agreement check: 2 days.",
    "Assemble held-out nodule-free single-kernel cohort and size against a minimum detectable partial association: 3 days.",
    "Download the NLST subset (real cost - large collection): ~1 week.",
    "Validate AI-CAC and lungmask on NLST-era LDCT noise: half a week.",
    "Time to first decision: Stage 0 in 2 days; Stage 1 answers the substantive question in ~3 weeks."
  ],
  "scores": {
    "clarity": {
      "value": 5,
      "why": "One sentence names the model, the cohort, the biomarker, the tool, and the two rivals it must beat."
    },
    "identifiability": {
      "value": 3,
      "why": "CAC is spatially separable and partialling gives its unique variance, but CAC, emphysema and vessels are all smoking-driven and correlated, so a positive never fully excludes a shared signature; the kernel perturbation proves density-channel use, not CAC-specific use. Site is permanently unaddressable in NLST."
    },
    "medical_relevance": {
      "value": 4,
      "why": "Tells a radiologist a lung-cancer screening score is partly reading heart calcium - changing how the number is interpreted and suggesting CAC be read alongside it. Held below 5 as it does not by itself change management."
    },
    "interest": {
      "value": 5,
      "why": "A deployed lung-cancer model whose residual signal turns out to be cardiovascular, in a trial where CV death outnumbers cancer death, with the audit paper never having looked."
    },
    "prior_legwork": {
      "value": 5,
      "why": "Open weights (both tools MIT), open images, public outcomes, published residual benchmark, reusable split."
    },
    "feasibility": {
      "value": 4,
      "why": "Cap lifted (INSPECTED_TRUE). Inference-only, single GPU. Held to 4 by the NLST transfer and the AI-CAC-to-NLST transfer check."
    },
    "data_readiness": {
      "value": 5,
      "why": "CC BY 4.0 imaging, public outcomes, MIT weights - nothing behind a door."
    },
    "evaluation_readiness": {
      "value": 4,
      "why": "Rank correlation, partial regression, paired-change regression, mediation - all standard, with published CAC reference values. Only the equivalence margin needs specifying."
    },
    "negative_result_value": {
      "value": 4,
      "why": "A tight null eliminates one of three named explanations for a documented gap. Held below 5 by the equivalence-margin dependence and the noise of ungated Agatston."
    },
    "novelty_confidence": {
      "value": 4,
      "why": "Cap lifted. The Sybil-vs-CAC link was NOT_FOUND directly; the audit paper never mentions cardiovascular structures. Held at 4 because the general method (model score vs imaging biomarker) is named prior art (Regression Concept Vectors, scout-004 record) and the MESA HeartLung paper is an adjacent Sybil-plus-CAC study that must be distinguished."
    }
  },
  "priority_score": 4.2,
  "priority_arithmetic": "0.20*4 + 0.15*3 + 0.15*4 + 0.10*5 + 0.10*5 + 0.10*5 + 0.10*4 + 0.05*5 + 0.05*4 = 0.80+0.45+0.60+0.50+0.50+0.50+0.40+0.25+0.20 = 4.20",
  "regret": {
    "value": 5,
    "why": "Both tools download free, the biomarker is one command, and a 2026 audit paper isolated the exact residual term and never looked at the heart in the same image."
  },
  "unverified_claims": [
    "AI-CAC's per-scan ranking transfers to NLST-era LDCT (Stage 0 check).",
    "Exact IDC nlst_canc table/column names (minutes to confirm).",
    "The Ardila split reconciliation carried over from idea 008 is still open.",
    "MESA HeartLung abstract text (paywalled - read from snippets)."
  ],
  "track": "baseline"
}


===== STAGE TASK =====
Defend or amend the idea. Append one round to `debate.md` in the idea folder.

Format your append exactly as:

```
## Round N — PROPOSER

**Responding to:** [the critic's objection, restated in your own words]

**Response:** REBUT | AMEND | CONCEDE

**Argument:** [if rebutting: why the objection does not hold, with specifics.
If amending: exactly what changes in the idea, and whether that weakens the
contribution. If conceding: say plainly that the objection is correct.]

**Status:** OPEN | CONCEDED | IRREDUCIBLE DISAGREEMENT | CONVERGED
```

Rules:

- Restating your claim more confidently is not a rebuttal. If you have no new
  argument or evidence, CONCEDE.
- **Identity check on every AMEND.** Before submitting an amendment, answer:
  does the revised design still answer the original one-sentence question?
  If NO, do not submit the amendment. Concede, reject the current idea, and
  record the replacement under `spin-off` as a new candidate. An amendment
  that achieves feasibility by abandoning the motivating question is not a
  repair; it is a different study wearing the old title.

- AMEND is not free. Every amendment that dodges an objection by narrowing
  the claim must say what was lost. Three amendments usually means the
  original idea was wrong.
- If the critic is right, say so in round one. Speed of concession is a
  feature. Defending a dead idea across three rounds wastes the loop.
- Do not introduce a new idea mid-debate. If the discussion reveals a better
  question, note it under "spin-off" and keep defending the original.
- Append only. Never edit earlier rounds.



===== DEBATE STATE =====
You are claude. Your interlocutor is codex.
This is round 1. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed partial regression and paired-kernel analysis cannot support the deliverable sentence that Sybil is using coronary artery calcium; they identify correlation with CAC and generic reconstruction-sensitive image signal, respectively.

**Argument:** CAC is a marker of a diffuse age/smoking/vascular phenotype that also includes aortic calcium, vertebral degeneration, airway disease, cardiac morphology, body-habitus-dependent noise, and acquisition differences. Conditioning on pack-years, LAA-950, and BV5 only removes the measured components of three selected covariates; it does not turn the remaining AI-CAC coefficient into evidence that Sybil reads coronary lesions. The paired-kernel arm is no stronger: changing kernel jointly changes calcium blooming, emphysema thresholds, edges, and texture throughout the volume, so correlated changes in AI-CAC and Sybil score demonstrate reconstruction sensitivity, not CAC-specific use. This is fatal under the charter because the candidate asserts rung 3 from associative evidence. A targeted within-scan intervention on AI-CAC lesion masks could preserve the core question, but only if realistic inpainting holds all non-CAC content fixed and is compared with size- and attenuation-matched edits in noncalcified coronary regions and noncoronary high-density lesions; simple deletion would repeat idea 006's out-of-distribution failure. Moving that experiment to an ordinary NLST subset would test a general Sybil mechanism, not the original claim about the published future-cancer-site-nodule-excluded residual, so that amendment would fail the identity check unless the title, question, and claim are explicitly narrowed or the replacement becomes a separate candidate.

**What would change my mind:** Show a preregistered, fidelity-validated within-scan CAC inpainting experiment on a reproducibly obtainable version of the stated future-cancer-site-nodule-excluded cohort, with the two matched control edits above and a positive-control model demonstrably sensitive to CAC; the Sybil score change must be specifically larger for coronary-calcium removal than for both controls.

**Status:** OPEN

