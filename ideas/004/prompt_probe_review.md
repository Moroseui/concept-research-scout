You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/004
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

## 2026-08-10 — Idea 015 REJECTED (superseded) + claim-identity governance rule

The narrowed BAC-response experiment survives on its merits, but removing the
vascular-age interpretation changed the deliverable claim's identity. Rule
going forward: revision-in-place is for narrowing scope or fixing design
within the same deliverable sentence; when the deliverable sentence or the
prohibited-conclusions set changes, the idea is REJECTED (superseded) and the
successor registers as a NEW candidate with parent_ids for lineage. The
successor re-enters through a normal scouting cycle, receives its own novelty
audit, and is re-ranked in the backlog on current merit — no inherited queue
position. For idea 015 specifically: the successor keeps the agreed
BAC-specific design and prohibited conclusions, and remains conditional on
Stage 0 confirming an obtainable Mirai-compatible cohort and spatial
registration between the BAC mask and Mirai's exact input tensor.


## 2026-08-10 — Idea 005 spin-off S2 (reader-slot exchangeability): deliberate wait

S2 is a legitimate successor under the claim-identity rule (different
estimand; parent idea-005) and should re-enter, if at all, through a normal
scout revival or librarian proposal with parent_ids — not manual
registration. This is also a live test of the revival machinery. If S2 has
not resurfaced within a few cycles despite this note, that is a finding
about the revival path, not about S2.


## 2026-08-10 — Idea 006 unblock check: FAILED (evidence-quoted)

Released CT-CLIP training uses deterministic preprocessing only (CTReportDataset,
scripts/data.py): rescale, resample, HU clip [-1000,1000], /1000, center
crop/pad (fill -1, data.py:156). No masking/cutout/erasing augmentation
exists; visual SSL is present in the library but disabled (use_visual_ssl
default False; not enabled in run_train.py). Body-excluded volumes are out-
of-distribution for this checkpoint; the deletion intervention is
indefensible per the debate's condition. Idea 006 stays PAUSED, hardened;
the exterior-swap spin-off (idea 004 pairs) is the only live path.
Side finding for idea 013 Stage 0: CT-CLIP clips at +1000 HU, so calcium
density saturates — compute the automated calcium measure on the same
clipped range.


## 2026-08-11 — Idea 004 Stage 0: feasibility memo accepted with four contract pins

GO per feasibility.md, with the probe contract required to encode: (1) primary
readout is per-head (18) x per-stratum paired-difference distributions; no
cross-head averaging; the 4-pair Br40f|Br44f stratum is exploratory only.
(2) Two-tier readout: tier 1 label-free per-head deltas (the floor, primary,
no margin needed); tier 2 label-dependent AUROC shift judged against the
CT-Scroll between-method spread, margin fixed from the PDF tables BEFORE any
paired score is seen. (3) Probes are phased: contract v1 is exactly the
section-9 load probe (gate, checkpoint hash, 18-output load, one-pair
inference, bit-determinism); the bulk 425-pair floor study is a separate
later contract requiring fresh human approval. (4) Freeze HF commit hash and
checkpoint SHA-256 at download time; attribution limited to 'released v2
ClassFine checkpoint' until paper-number correspondence is checked.


## 2026-08-12 - Probe 004 exit-7 root cause (evidence-quoted) and revision spec

Diagnostic on the frozen revision (deeca4d8) of validation_metadata.csv:
ConvolutionKernel values are stringified lists - value_counts shows
"['Br40f', '3']": 425 and "['Br60f', '3']": 239 - while run.py matches
row['ConvolutionKernel'].strip() == 'Br40f', which matches zero rows. World
matches Stage 0 (239 Br60f volumes ~ frozen 237 pairs); only the predicate
drifted. Revision requirements, and ONLY these: (1) normalize the kernel
field before comparison - if it parses as a Python list literal take element
0, else use the stripped raw string - then compare to Br40f/Br60f; robust to
both formats. (2) Diagnosability: on any selection shortfall vs the frozen
count, dump top-10 distinct kernel values with counts, example VolumeNames,
and per-filter drop counts to the run log AND selection_audit.json in the
output dir. (3) Record the normalized kernel per selected volume in
input_manifest.csv. Geometry list-string columns compare same-format
row-vs-row and need no change. No other scope.


## 2026-08-12 - Probe 004 exit-5 root cause (evidence-quoted): transformers pin, not the checkpoint

Load failed on exactly one unexpected key, "trained_model.text_transformer.
embeddings.position_ids". Transformers 4.31.0 changed BERT position_ids
from a persistent to a non-persistent buffer, so checkpoints saved under
<=4.30.x carry the key and models instantiated under >=4.31 do not expect
it. The released repo own transformer_maskgit/setup.py line 17 contains
the commented pin "#transformers==4.30.1" - the authors environment.
Verdict: environment-alignment failure, not a checkpoint/code
incompatibility; exit 5 is provisionally reclassified as environment-class
pending a run under the released pin. Revision, and ONLY this: in
probes/004/requirements.txt set transformers==4.30.1 and cascade
tokenizers to a compatible 0.13.x (4.30.1 requires tokenizers<0.14);
no run.py changes. Process note for the floor-study contract: an exit-5
load classification is only final after the released environment pin has
been tested - version-semantics mismatches must not masquerade as
checkpoint facts.



===== evidence/ledger_digest.md =====
# Ledger digest (auto-generated -- do not edit; run `python scout.py ledger digest`)

56 tracked ideas. Latest state per idea; full history in ledger.jsonl.

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **DATA_ACCESS** x2: Required data, checkpoints, or mappings are not obtainable in practice.
- **IDENTIFIABILITY_FAILURE** x2: The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.
- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.
- **ANNOTATION_PROVENANCE** x1: Inference depends on who assigned labels / what they could see, and that is undocumented or contaminated.
- **CIRCULARITY** x1: The endpoint is a re-encoding of the input or of the thing being tested.

## Candidate backlog (scouted, not yet shortlisted; ranked)

- **scout-010-c01** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.9, audited 2026-08-12] -- CXR-Age put back together from parts a radiologist can measure
- **scout-010-c03** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.5, audited 2026-08-12] -- Merlin's cirrhosis signal may be the spleen
- **scout-010-c02** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.2, audited 2026-08-12] -- Atelectasis vs consolidation: has CT-CLIP learned the radiologist's volume-loss rule?
- **scout-006-c04** [NOVEL_UNVERIFIED, score 4.1, audited 2026-08-10] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-009-c08** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.1, audited 2026-08-11] -- The glioblastoma prognosticator may be reading the invasion front's roughness
- **scout-010-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.0, audited 2026-08-12] -- The inferior vena cava as a manometer: does the chest model read venous pressure?
- **scout-009-c06** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.0, audited 2026-08-11] -- The CT spirometer may be reading the diaphragm as a pressure-loaded membrane
- **scout-007-c06** [NOVEL_UNVERIFIED, score 3.9, audited 2026-08-10] -- The effusion model may be reading whether pleural fluid still obeys gravity
- **scout-008-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.9, audited 2026-08-11] -- The emphysema call may read the shape of the holes, not just how many
- **scout-008-c05** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 3.9, audited 2026-08-11] -- The lung-cancer model may read the aorta as an ageing clock
- ... and 14 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- conditional-observational: 4
- counterfactual-synthesis: 3
- representation-erasure: 3
- regional-substitution: 3
- natural-paired: 2
- longitudinal-within-subject: 2
- model-output-perturbation: 2

## Ideas

- **idea-001** [REJECTED/DEBATED/baseline] -- Have lung nodule concept models been validated against radiologist opinion rather than against disease? -- killed: DATA_INSUFFICIENT -- data: {"primary": "LIDC-IDRI via The Cancer Imaging Archive", "license": "CC BY 3.0", 
- **idea-002** [PAUSED/DEBATED/baseline] -- Dermoscopic concepts predicted from non-dermoscopic photographs: genuine visibility or shortcut? -- data: {"primary": "Derm7pt paired clinical/dermoscopic images", "source": "github.com/
- **idea-003** [REJECTED/DEBATED/baseline] -- Does BI-RADS concept intervention survive realistic clinician behaviour, and does it beat simply reading the BI-RADS category? -- killed: DATA_ACCESS -- data: {"primary": "BUS-BRA (Zenodo 8231412, CC BY 4.0) for the external and baseline a
- **idea-004** [ACTIVE/DEBATED/baseline] -- The free test-retest experiment already inside CT-RATE: duplicate reconstructions of the same acquisition
- **idea-005** [REJECTED/DEBATED/baseline] -- Eight named characteristics, or three latent ones? Discriminant validity of the LIDC concept vocabulary -- killed: ANNOTATION_PROVENANCE
- **idea-006** [PAUSED/DEBATED/baseline] -- Ask the chest-CT foundation model to diagnose a volume with no patient in it
- **idea-007** [ACTIVE/DEBATED/baseline] -- The same patient, twice, ten minutes apart, differing only in how much air is in the lungs
- **idea-008** [ACTIVE/DEBATED/baseline] -- Two papers say Sybil's residual signal is the background, one of them names emphysema, and neither measured it
- **idea-009** [REJECTED/DEBATED/baseline] -- Murray's cube law says how a branching tree should be built - ask whether the risk model is reading the lung's departure from it -- killed: IDENTIFIABILITY_FAILURE
- **idea-010** [REJECTED/DEBATED/baseline] -- Cardiomegaly on a CT report is admitted gestalt - ask whether the model has quietly turned it into millilitres -- killed: CIRCULARITY
- **idea-011** [PAUSED/DEBATED/baseline] -- Forensic anthropologists age a skeleton by its rib cartilage - ask whether an unguided CT model found the same clock
- **idea-012** [PAUSED/DEBATED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **idea-013** [SHORTLISTED/DEBATED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **idea-014** [PAUSED/DEBATED/baseline] -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away
- **idea-015** [REJECTED/DEBATED/baseline] -- A breast-cancer risk model may be reading the arteries as a vascular clock
- **idea-016** [REJECTED/DEBATED/baseline] -- The PE model may read contrast flowing backward as a pressure gauge -- killed: IDENTIFIABILITY_FAILURE
- **idea-017** [SHORTLISTED/DEBATED/baseline] -- A lung-cancer model may be reading a mechanically remodeled trachea
- **idea-018** [REJECTED/DEBATED/baseline] -- The brain-tumor prognosticator may be weighing the chewing muscle -- killed: DATA_ACCESS
- **idea-019** [SHORTLISTED/DEBATED/wide] -- The fibrosis model may be counting holes at the pleural edge
- **scout-006-c01** [SHORTLISTED/SCOUTED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **scout-006-c02** [SHORTLISTED/SCOUTED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **scout-006-c03** [SCOUT_ONLY/SCOUTED/baseline] -- An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver
- **scout-006-c04** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-006-c05** [SCOUT_ONLY/SCOUTED/baseline] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two
- **scout-007-c01** [SHORTLISTED/SCOUTED/baseline] -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away
- **scout-007-c02** [SHORTLISTED/SCOUTED/baseline] -- A breast-cancer risk model may be reading the arteries as a vascular clock
- **scout-007-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin may be reading fatty kidney rather than kidney shape
- **scout-007-c04** [SHORTLISTED/SCOUTED/baseline] -- The PE model may read contrast flowing backward as a pressure gauge
- **scout-007-c05** [SHORTLISTED/SCOUTED/baseline] -- A lung-cancer model may be reading a mechanically remodeled trachea
- **scout-007-c06** [SCOUT_ONLY/SCOUTED/wide] -- The effusion model may be reading whether pleural fluid still obeys gravity
- **scout-007-c07** [SHORTLISTED/SCOUTED/wide] -- The fibrosis model may be counting holes at the pleural edge
- **scout-007-c08** [SCOUT_ONLY/SCOUTED/wide] -- The PE model may be reading how completely blood and contrast have mixed
- **scout-007-c09** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-007-c10** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-007-c11** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-007-c12** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-007-c13** [REJECTED/SCOUTED/wide] -- (untitled)
- **scout-008-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The cirrhosis model may be reading the bumpiness of the liver's edge
- **scout-008-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The chest-CT model may see the heart by watching the airway splay
- **scout-008-c03** [SCOUT_ONLY/SCOUTED/baseline] -- The model that 'predicts a blood count' may just be reading how bright the blood is
- **scout-008-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The emphysema call may read the shape of the holes, not just how many
- **scout-008-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The lung-cancer model may read the aorta as an ageing clock
- **scout-009-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The CT spirometer may be measuring remodeled airway walls
- **scout-009-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The kidney model may be reading fat packed into the renal sinus
- **scout-009-c03** [SHORTLISTED/SCOUTED/baseline] -- The brain-tumor prognosticator may be weighing the chewing muscle
- **scout-009-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The risk model may be reading the breast's lines of force
- **scout-009-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The lung-cancer model may be reading the marrow as a smoking dosimeter
- **scout-009-c06** [SCOUT_ONLY/SCOUTED/wide] -- The CT spirometer may be reading the diaphragm as a pressure-loaded membrane
- **scout-009-c07** [SCOUT_ONLY/SCOUTED/wide] -- Mirai may be detecting broken bilateral symmetry before a lesion exists
- **scout-009-c08** [SCOUT_ONLY/SCOUTED/wide] -- The glioblastoma prognosticator may be reading the invasion front's roughness
- **scout-009-c09** [SCOUT_ONLY/SCOUTED/fiction] -- The arterial-calcification score may be reading inspiratory depth
- **scout-010-c01** [SCOUT_ONLY/SCOUTED/baseline] -- CXR-Age put back together from parts a radiologist can measure -- data: ChestX-ray8 (primary), PadChest (replication); CheXmask for both.
- **scout-010-c02** [SCOUT_ONLY/SCOUTED/baseline] -- Atelectasis vs consolidation: has CT-CLIP learned the radiologist's volume-loss rule? -- data: CT-RATE (validation split; established access and local pipeline).
- **scout-010-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin's cirrhosis signal may be the spleen -- data: Public abdominal CT (AMOS 2022, TotalSegmentator public dataset); Merlin checkpoint from HF.
- **scout-010-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The inferior vena cava as a manometer: does the chest model read venous pressure? -- data: CT-RATE (repeat-session subset; second and final CT-RATE candidate this cycle).
- **scout-010-c05** [SCOUT_ONLY/SCOUTED/baseline] -- Aortic tortuosity as a buckled column: is the hypertension head reading exceeded critical pressure? -- data: Public abdominal CT with age metadata (candidate cohorts: AMOS 2022, TotalSegmentator public dataset - metadata adequacy is Stage 0); Merlin checkpoint from HF. Second and final Merlin/public-abdominal candidate this cycle.


===== evidence/portfolio_brief.md =====
# Portfolio brief (auto-generated; run `python scout.py brief`)

Actionable ideas with debate verdicts. A revival/recombination
candidate MUST cite the specific condition below that has changed.

## idea-019 [SHORTLISTED] -- Does CT-CLIP use a subpleural cyst-network topology index?

**Verdict:** **REVISE.** The debate produced a coherent conditional rung-1 feasibility/use study, but the existing card is materially stale and the program's required physician-legible endpoint remains outside the evidence. Before deciding whether revision-in-place is permissible, the human should look most closely at the claim-identity boundary: whether replacing “the model uses honeycombing” with “the model uses a prespecified subpleural cyst-network topology index” is rung honesty within the same candidate or a new deliverable sentence that must be registered as a successor. ```json {"verdict": "REVISE", "unblock": "Human resolves the claim-identity boundary, then the card is rewritten to the agreed index-level, K1-gated, G2a/G2b-conditional rung-1 design (or registered as a successor if the deliverable sentence is judged changed)."} ```

**Unresolved:** Does narrowing the confirmatory sentence to a topology index preserve the candidate's identity?; Can the topology index be validated as honeycombing and thereby reach rung 3?; Will CT-RATE contain enough suitable cases for the proposed study?; Can the latent intervention pass the agreed validity gates?

## idea-017 [SHORTLISTED] -- Can Sybil's tracheal-deformity question be identified in NLST?

**Verdict:** **REVISE.** Rewrite `idea_card.json` to implement the converged Stage 0-only design before any feasibility memo or probe contract. The single most important thing for the human to inspect is whether the joint-support gate can be given a prespecified, adequately powered minimum-support criterion: if continuous tracheal index cannot be separated from sex, emphysema, lung volume, and reconstruction in a recoverable held-out cohort, idea 017 dies like idea 009 regardless of the attractiveness of its mechanism. ```json {"verdict":"REVISE","unblock":"Rewrite the idea card as a four-gate Stage 0-only study with no erasure or use claim, then prespecify and inspect adequate independent tracheal-index support in a recoverable Sybil-held-out or external cohort."} ```

## idea-014 [PAUSED] -- The knee-pain model may be reading trabecular stress architecture that KL grade throws away

**Verdict:** **PAUSE.** The revised question remains scientifically coherent, but the rate-limiting model asset has not been reproduced, and the final edit-validity amendment has not been tested or answered by the critic. The single most important thing for the human to inspect before deciding is whether the released Pierson pipeline can, with available OAI access and the allowed compute, produce at least two independent models that pass preregistered better-than-KLG and disparity-signature gates on a frozen split. Without that, there is no model family to decode; editor validity is the next gate only after reproduction succeeds. ```json {"verdict": "PAUSE", "unblock": "Demonstrate at least two independently trained Pierson-recipe models that pass preregistered pain-performance and disparity reproduction gates on a frozen OAI split within the available access and compute constraints."} ```

**Unresolved:** Can the published model family be reproduced under the access and compute constraints?; Does the revised image edit identify use of the declared fractal-signature X rather than edit artifacts?; Is directional fractal signature a medically legitimate name for the model-used signal, and how much biological gloss may it carry?; Does discriminator equivalence adequately establish in-distribution editi

## idea-013 [SHORTLISTED] -- Does CT-CLIP's coronary-calcification score follow reconstruction-dependent changes in displayed coronary calcium?

**Verdict:** **REVISE.** Rewrite the idea card around the reduced rung-1 calibration and reconstruction-sensitivity audit, with localisation explicitly excluded and the keystone set to `NOT_INSPECTED`. The single most important thing for the human to inspect before deciding is whether a validated, annotation-free coronary target localiser for nongated noncontrast CT actually exists and runs on CT-RATE; that fact determines whether the high-value localisation question has a credible spin-off or whether idea 013 should remain only a modest robustness audit.

**Unresolved:** Is the reduced rung-1 audit worth running?; Can the localisation question be revived as a separate intervention study?; Would validated synthetic edits identify calcium location rather than edit artifacts?

## idea-012 [PAUSED] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan

**Verdict:** **PAUSE.** Before deciding otherwise, the human should inspect whether the MD.ai-derived scan-level exclusion membership has become available—and is joinable to a frozen obtainable Sybil evaluation split—because without it the study cannot test the specific residual that defines Idea 012.

## idea-011 [PAUSED] -- Forensic anthropologists age a skeleton by its rib cartilage - ask whether an unguided CT model found the same clock

**Verdict:** **PAUSE.** The debate converged after a real, persistent objection; this was not a one-round rubber stamp. Before deciding whether to reopen, the human should look first for the missing identification instrument: a confirmed human chest CT resource with retained spectral base-material or dual-kV raw data and linkable age that can provide a measured, post-preprocessing-matched mineralized-to-soft-tissue contrast. Without that—or another genuinely matched real-tissue control—the current experiment cannot distinguish native use of costal cartilage mineralization from response to the deletion operation, regardless of improvements to masks, models, or supervision audits.

**Unresolved:** Can a measured, properly matched control separate mineralization use from the deletion signature?; Could registered longitudinal CT provide a natural contrast?; Is the editable cartilage mask sufficiently precise in the population where the experiment would run?; Are the other Stage-0 assets actually available and clean?

## idea-008 [ACTIVE] -- Does Sybil use CT-defined emphysema geometry?

**Verdict:** **REVISE.** The debate produced a coherent conditional design, but the current `idea_card.json` still describes the superseded reconstruction arm, rung-3 observational logic, `INSPECTED_TRUE` keystone, and obsolete scores. Before deciding whether to advance, the human should look most closely at whether the proposed tissue-for-tissue edit can be validated as in-distribution with a prespecified sham-effect tolerance; that is now the single fact separating a model-use study from an association-only study.

**Unresolved:** Are the local parenchymal substitutions in-distribution for Sybil?; Does a score response isolate CT-emphysema geometry from remaining visible correlates?; Can the required held-out NLST cohort and covariates actually be recovered?

## idea-007 [ACTIVE] -- The same patient at two degrees of inspiration

**Verdict:** **REVISE.** Update the idea card to the converged state-level claim and corrected scores, then require Stage 0 before a probe contract. The single most important thing for the human to inspect is the prespecified DICOM-to-final-tensor comparability gate: whether enough inhale/exhale pairs truly retain matched reconstruction, coordinates, physical scale, and thoracic coverage through the complete pinned CT-CLIP preprocessing pipeline.

**Unresolved:** Do enough actual pairs pass the reconstruction and framing gate?; Is a common physical box compatible with CT-CLIP preprocessing without state-dependent framing?; Is the optional matched-volume 4DCT jitter floor usable?



===== evidence/librarian_proposals.md =====


===== ideas/004/README.md =====
# Idea 004: The free test-retest experiment already inside CT-RATE: duplicate reconstructions of the same acquisition

Selected from scouting cycle 002, candidate 1.


===== ideas/004/consensus.md =====
# Debate summary — idea 004

## Agreed

- **Stage 0 cannot estimate benchmark-interval inflation from labels and cluster sizes alone (Round 1).** Both sides agree that duplicated label rows describe the release structure but do not identify the sampling variance of AUROC or another score-based performance statistic. The simple `1 + (m-1)rho` design-effect formula is not valid for this use, and label ICC is not a proxy for dependence in model errors or estimator influence values.
- **The metadata-only stage is a linkage and feasibility audit (Round 1).** It may count reconstruction groups, check within-scan duplication of labels and reports, enumerate metadata contrasts, reconcile the reported validation patient counts, and confirm access. Any benchmark-precision analysis requires per-volume ClassFine outputs, either released or regenerated.
- **Reconstruction-, scan-, and patient-weighted analyses are different estimands (Round 1).** A difference between them is not automatically numerical bias. The revised benchmark arm must name each estimand and use a scan- or patient-clustered procedure appropriate to it, with patient-level resampling as the outer unit when patients contribute multiple scans.
- **The identical-file rerun tests software determinism only (Round 2).** It does not rule out deterministic effects of resampling, cropping, padding, or other preprocessing triggered by different source geometries.
- **Causal reconstruction-content language must be restricted (Rounds 2–3).** Geometry-matched pairs may support a reconstruction-content interpretation when the relevant preprocessing inputs and transformations are identical. All other pairs estimate end-to-end pipeline repeatability under composite released reconstruction variants. Kernel-specific attribution is unavailable unless the metadata isolate that contrast.
- **The revised design retains the original paired-score measurement (Rounds 2–3).** Both sides accept that measuring score changes from the frozen released checkpoint and preprocessing across same-acquisition reconstruction variants remains the core study, even though its interpretation and summaries have narrowed.
- **A pooled ICC cannot establish clinically or operationally meaningful repeatability (Round 3).** ICC is demoted to a descriptive statistic because it can be dominated by between-scan heterogeneity, can mislead for rare findings, and does not match the unequal and inconsistently named reconstruction structure well enough to carry an equivalence claim.
- **Primary stability analysis must use paired score changes with prespecification (Round 3).** The revised plan reports paired-difference distributions, a repeatability coefficient or upper quantile of absolute change, reconstruction-contrast strata, score-region strata, and probability- and logit-scale results with the margin's scale declared in advance.
- **Thresholds may not be selected on the audit pairs (Round 3).** Threshold-crossing rates are secondary and require thresholds estimated from sufficiently numerous singleton validation scans or, failing that, the training split. Underpowered outputs must be labelled exploratory using a prespecified independent positive-scan rule.
- **A reassuring result is decisive only against a justified, powered equivalence margin (Round 3).** Without that margin, a null is sensitivity-limited. The unsupported `ICC > 0.95` and “low-single-digit” flip-rate cutoffs are abandoned.
- **The benchmark-dependence and score-stability arms answer different questions (Round 3).** Patient-clustered intervals assess dependence and weighting; paired-difference margins assess reconstruction stability. Neither substitutes for the other.

## Unresolved

There is no remaining proposer–critic disagreement about the revised design. The unresolved items are empirical gates accepted by both sides:

### Do enough geometry-matched same-acquisition pairs exist?

- **Question:** Are there enough pairs sharing slope, intercept, XY spacing, Z spacing, and array shape—and carrying interpretable reconstruction contrasts—to support the primary mechanistic stratum?
- **Proposer's position:** Make this stratum primary for reconstruction-content attribution; if it is empty or too small, retain only the composite end-to-end pipeline analysis.
- **Critic's position:** Accepted in Round 3 as an adequate repair to the preprocessing objection.
- **Evidence that would settle it:** Direct counts and parameter comparisons in `validation_metadata.csv`, followed by a power or precision calculation for the paired endpoints.

### Are audit-independent thresholds estimable?

- **Question:** Are singleton validation scans numerous enough, per output, to estimate stable operating thresholds without using the paired audit cases?
- **Proposer's position:** Use singleton validation scans; fall back to training-split thresholds if the singleton group is inadequate.
- **Critic's position:** Thresholds must be fixed independently of the audit pairs; this repair satisfies that requirement in principle.
- **Evidence that would settle it:** Counts of singleton scans and independent positive/negative cases per output, plus prespecified threshold-estimation precision criteria.

### Are per-output analyses adequately powered?

- **Question:** Do the paired data contain enough independent positive and negative scans for confirmatory per-output repeatability, crossing-rate, and AUROC analyses?
- **Proposer's position:** Apply a prespecified minimum-count rule and mark failures exploratory.
- **Critic's position:** Accepted; rare outputs cannot support confirmatory claims merely because all 18 heads are available.
- **Evidence that would settle it:** Direct label and grouping counts, followed by minimum-detectable-effect or confidence-width calculations for each planned endpoint.

### Can the benchmark-precision arm be run without large-scale inference?

- **Question:** Do released per-volume ClassFine scores or logits exist and correspond exactly to the frozen checkpoint and validation files?
- **Proposer's position:** Search for released artifacts first; if absent, re-cost the study as gated image access plus inference.
- **Critic's position:** Scores are indispensable for the precision claim, whether released or regenerated.
- **Evidence that would settle it:** Direct inspection of official repository artifacts, model outputs, or author-provided files; otherwise successful unchanged-pipeline inference on accessed validation volumes.

### What equivalence margin is scientifically defensible?

- **Question:** What paired-score or reconstruction-swap AUROC change is small enough to count as operationally equivalent?
- **Proposer's position:** Anchor the primary consequence margin to published between-method AUROC gaps on the same validation split, fixed before examining paired differences; use independently derived thresholds for secondary crossing rates.
- **Critic's position:** A margin must be tied to an observable consequence and fixed before the audit; the proposed anchor is compatible with that demand but has not yet been demonstrated or justified numerically.
- **Evidence that would settle it:** Direct inspection of the cited benchmark tables, a written margin rationale fixed before score inspection, and confidence intervals showing whether the paired effect lies inside that margin. The choice of how consequential a benchmark gap must be also contains a value judgment; data can quantify the gap but cannot alone decide its importance.

## Positions that moved

- **Proposer, Round 1 — earned concession.** In response to the critic's estimator-specific argument, the proposer withdrew the claim that labels and cluster sizes alone yield the factor by which per-volume confidence intervals are too narrow. The proposer explicitly acknowledged conflating cluster structure with the variance of AUROC and moved all precision claims behind model outputs.
- **Proposer, Round 2 — earned partial concession and amendment.** In response to the critic's distinction between stochastic rerun noise and deterministic geometry-dependent preprocessing, the proposer withdrew the claim that an identical-file rerun rules out preprocessing and abandoned unqualified “reconstruction-induced,” kernel-specific, and content-specific language for the full corpus. Inspection of the released preprocessing code then supported the geometry-matched primary stratum and composite interpretation elsewhere.
- **Critic, Round 3 — position moved after new evidence and repair.** The critic accepted that the Round 2 amendment adequately narrows the preprocessing claim and preserves the study's identity. This followed the proposer's direct inspection of the released preprocessing implementation and explicit restriction of causal attribution.
- **Proposer, Round 3 — earned concession and amendment.** In response to the critic's variance-ratio and threshold-selection arguments, the proposer demoted ICC to descriptive status, struck the unsupported numerical reassurance criteria, accepted independent thresholds and equivalence margins, and made paired-difference and consequence-based analyses primary.
- **No concessions were unearned.** Each movement answered a specific objection or newly inspected implementation detail; none was mere capitulation.

## Amendments made

- **Stage 0:** Now a metadata, linkage, provenance, access, and feasibility audit. It no longer promises a label-only design effect or a no-model estimate of confidence-interval narrowing.
- **Benchmark arm:** Now requires per-volume scores, explicitly separates reconstruction-, scan-, and patient-weighted estimands, and compares row-level resampling with scan- or patient-clustered inference without prespecifying the direction of change.
- **Repeatability claim:** Now concerns within-acquisition reconstruction or end-to-end pipeline repeatability, not test-retest reliability across repeated acquisitions and not general concept validity.
- **Causal interpretation:** Reconstruction-content attribution is limited to adequately sized geometry-matched strata. Geometry-mismatched pairs retain a composite pipeline estimand; matched-grid transformations are secondary, asymmetrically interpreted mechanistic checks rather than definitive subtraction controls.
- **Primary statistics:** Paired score-difference distributions, repeatability coefficients or upper absolute-difference quantiles, and reconstruction-swap AUROC deltas replace pooled ICC as the main evidence. Analyses are stratified by reconstruction contrast and score region and reported on declared probability/logit scales.
- **Threshold analysis:** Crossing rates are secondary, with thresholds estimated away from audit pairs and outputs failing minimum-count criteria labelled exploratory.
- **Negative result:** No fixed reassuring cutoff is claimed. A negative is decisive only if confidence bounds fall within a prespecified, powered margin; otherwise it is sensitivity-limited.
- **Cross-domain claim:** The psychometric/QIBA borrowing now contributes within-subject variance, repeatability reporting, stratification, and advance margins. The general attenuation ceiling and claims that downstream correlations become “impossible” are lost.
- **Medical scope:** The study audits a released research model and benchmark. It no longer treats stable outputs as validated concepts or unstable outputs as direct proof that clinicians cannot act on the finding.
- **Cost and value lost:** The original one-afternoon headline result disappears unless validation scores are already released. Geometry stratification reduces sample size, the reliability coefficient is no longer the headline, the anticipated result loses its numerical form, and the revised card is materially narrower and potentially more expensive.

## Recommendation

**REVISE.** The debate converged on a defensible design, but the current idea card still contains claims and scores that the debate explicitly withdrew. Before deciding whether to advance to a feasibility memo, the human should look first at the direct Stage 0 metadata counts—especially the number and parameter makeup of geometry-matched same-acquisition pairs—because that single inspection determines whether the stronger reconstruction-content study exists or only the narrower composite pipeline audit remains.


===== ideas/004/critique.md =====
FATAL OBJECTION: NONE; the paired audit is feasible, but the current Stage 0 and clinical interpretation make claims that its data cannot identify.
EVIDENCE: The official CT-RATE card confirms reconstruction-indexed volumes and a gated 21.3-TB repository, but filenames and duplicated labels alone cannot determine an AUROC design effect.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION

# Adversarial critique

## Bottom line

There is a defensible study here: measure how much a *specific released CT-CLIP classifier's scores* change across CT-RATE reconstructions of the same scan, and audit whether treating those reconstructions as independent changes uncertainty or estimands in that model's published validation. The current card goes beyond that evidence in four places: it calls reconstruction repeatability “test-retest,” promises a no-model design-effect result that cannot be computed from labels, treats report-derived abnormalities as validated concepts, and converts agreement into a general ceiling on clinical validity. Those are repairable, but they require a narrower claim and a different primary analysis.

## Facts actually verified

- **Verified fact:** the official CT-CLIP repository states that 25,692 CT volumes expand to 50,188 through “various reconstructions,” defines names as `split_patientID_scanID_reconstructionID`, and gives `valid_53_a_1` as a worked example. This verifies an identifiable reconstruction grouping, not yet that every same-scan group is a clean matched-kernel pair. Official repository: https://github.com/ibrahimethemhamamci/CT-CLIP ; paper identifier: arXiv:2403.17834, subsequently listed by the dataset card as *Nature Biomedical Engineering* (2026).
- **Verified fact:** the current official Hugging Face card requires login and agreement to share contact information; it calls the repository publicly accessible subject to conditions, prohibits redistribution, and reports a total size of 21.3 TB. It does not describe a manual approval step. Official dataset: https://huggingface.co/datasets/ibrahimhamamci/CT-RATE
- **Verified fact:** the official repository reports approximately 0.5 seconds per volume for ClassFine inference and says inference can run on smaller GPUs. It also warns that changing encoder patch size to fit memory can affect small-pathology performance. This supports bounded inference, but not reproducibility on an arbitrary Colab GPU without first reproducing the released preprocessing and logits.
- **Source-supported interpretation:** paired reconstructions are a valuable within-acquisition perturbation because anatomy and acquisition are substantially held fixed.
- **Still unverified:** the validation reconstruction count; whether all members share acquisition UID/time and report; which parameters differ; whether reconstruction IDs have consistent meanings; whether released metadata retain kernel, thickness, method, and series description; and whether accessible files contain raw logits or only binary labels.

The card should correct the patient-count discrepancy before revision: the official repository/card says 1,304 validation patients, whereas the cited later benchmark says 1,314. This is probably a paper/version or filtering difference, but it prevents casually combining their denominators.

## The strongest objection: Stage 0 cannot deliver its promised result

Counting clusters and showing that label vectors repeat is useful bookkeeping. It does **not** yield “the factor by which a naive per-volume confidence interval is too narrow.” The familiar design effect `1 + (m-1)rho` applies to particular clustered estimators under assumptions; `rho` must concern the relevant observations, scores, losses, or influence functions. An ICC of duplicated binary label vectors is either mechanically one or near one and says nothing about covariance of model errors. AUROC is a pairwise rank statistic, so its clustered variance is not recoverable from cluster sizes and labels alone.

Likewise, duplicate volumes do not necessarily inflate an AUROC point estimate. Per-volume AUROC estimates a reconstruction-weighted quantity; one-per-scan AUROC estimates a scan-weighted quantity. A difference can arise because scans with more reconstructions receive more weight, not because the original computation is numerically biased for its own estimand. “Overstate the precision of every number” is especially too broad: point estimates are not precision estimates, some papers may publish no confidence intervals, and metrics react differently to clustering.

**Required repair:** Stage 0 should only establish the cluster structure, label/report duplication, parameter contrasts, and feasibility. The benchmark audit must use model outputs and compare clearly named estimands: reconstruction-weighted, scan-weighted (for example, mean score per scan), and patient-weighted where longitudinal scans exist. Use a patient- or scan-cluster bootstrap appropriate to the chosen estimand. Do not predeclare the direction of interval change.

## This is reconstruction repeatability, not test-retest reliability

The acquisition is not repeated. Consequently the study cannot measure sensitivity to positioning, inspiration, dose realization, patient motion, biological change, or scanner repeat acquisition. Calling it a “free test-retest experiment” overstates what is held and varied. The accurate term is **within-acquisition reconstruction repeatability** or **reconstruction perturbation consistency**.

This distinction matters clinically. A stable score across two reconstructions can still be unstable across acquisitions or wrong in both reconstructions. An unstable score is a valid model-robustness failure, but it does not establish that a radiological finding itself is unreliable.

## The endpoint is not yet identifiable

### “Reconstruction” is a bundle, not a named intervention

Two released NIfTI volumes may differ in kernel, slice thickness, interval, reconstruction algorithm, field of view, orientation, or corrections applied during dataset construction. The dataset card explicitly notes later intensity-normalization and spacing corrections to the NIfTI files. If metadata do not identify the contrast, the experiment can estimate repeatability across the corpus's released reconstruction variants, but cannot attribute changes to kernel choice.

Parsing identical patient and scan IDs is necessary but insufficient. Before GPU work, verify acquisition/series fields and inspect voxel grids and metadata. If the pair differs in slice thickness as well as kernel, describe the composite contrast. “Reconstruction-induced” is acceptable; “kernel-induced” is not.

### The identical-volume rerun is a weak control

Evaluation-mode inference should normally be deterministic. A zero software-noise floor only excludes stochastic execution; it does not separate reconstruction effects from dataset resampling, intensity correction, cropping, padding, or interpolation. Those operations are part of the deployed inference pipeline and can interact with different source grids.

A better decomposition uses three controls: identical file twice; a deterministic re-save/resample of one volume through the pipeline; and the actual paired reconstruction. If only the last changes, the result is still a *pipeline-under-reconstruction* effect unless preprocessing is independently standardized.

### ICC(2,1) is not automatically the right primary statistic

Reconstruction IDs are not human raters sampled from a common population, groups may have unequal sizes, and different scans may receive different reconstruction contrasts. A pooled ICC can be very high merely because between-scan score variance is large while clinically important within-scan changes remain. It is also unstable for rare findings and says little at decision thresholds.

Pre-specify a reference/contrast only where metadata define comparable pairs. Report paired score differences with Bland–Altman-style limits or a repeatability coefficient, absolute difference distributions, and threshold crossing rates over clinically justified thresholds. Stratify by concept prevalence/score region and reconstruction contrast. ICC may be secondary, with its model and variance components stated. An equivalence claim needs an a priori, clinically or operationally justified margin; `ICC > 0.95` and “low single-digit flips” are currently unsupported illustrative cutoffs.

## Concept-label circularity and leakage

The primary paired-score analysis avoids using report-derived labels, so it is not circular in the narrow statistical sense. But it also does not validate a “concept.” The 18 outputs are heads trained/evaluated against RadBERT-derived report labels. Agreement shows only that a model output is stable under a reconstruction perturbation. Both reconstructions can share the same spurious cue, and both predictions can be consistently wrong.

The secondary benchmark is more vulnerable. If each reconstruction inherits the same report and label, repeated labels are mechanically correlated. ClassFine was trained on similarly expanded reconstructions, so the audit describes robustness of a system trained with this augmentation-like duplication; it cannot establish robustness of chest-CT foundation models generally. There is no train/validation patient leakage implied by this fact, but there is **estimand dependence** and possible training-policy leakage: the model may have learned reconstruction invariance precisely because training scans appeared in multiple variants.

Required language: call these “18 abnormality output scores” or “named report-derived finding outputs,” not validated abnormality concepts. Keep validity, accuracy, and faithfulness out of the primary claim.

## The attenuation-bound argument should be removed

The proposed statement that no downstream correlation can exceed the square root of this reliability imports classical test theory assumptions that this design does not establish: a stable latent construct, additive independent error, appropriate sampling, and a reliability coefficient for the same measurement process. Within-acquisition reconstruction agreement isolates only one nuisance source. High agreement across reconstruction variants is not total score reliability; low agreement may combine preprocessing and heterogeneous reconstruction contrasts. It therefore cannot provide a general ceiling on correlations with external outcomes, much less make a published correlation “impossible.”

The cross-domain construct still adds value if used modestly: variance decomposition and limits of agreement force reporting of the within-scan distribution rather than only flips. That is what changes when the analogy is retained.

## Prior-work overlap and novelty

The broad scientific premise is already established. Primary studies use paired chest CT reconstructions to evaluate or enforce model/measurement consistency:

- Zuo et al., “Adaptation to CT Reconstruction Kernels by Enforcing Cross-Domain Feature Maps Consistency,” used public paired LIDC/IDRI reconstructions differing in kernel and documented large baseline prediction/feature inconsistency for a lung-CT segmentation task. PMCID: PMC9503667.
- Hwang et al., “Kernel Conversion for Robust Quantitative Measurements of Archived Chest Computed Tomography Using Deep Learning-Based Image-to-Image Translation,” used paired sharp/soft reconstructions and evaluated emphysema and other quantitative measures. PMID: 35112080; DOI: 10.3389/frai.2021.769557; PMCID: PMC8801695.
- Liard et al., “Impact of reconstruction kernel variability on segmentation consistency in low-dose thoracic CT,” evaluates 9,529 paired scans and 84 thoracic regions. DOI: 10.1117/12.3085743; PMID: 42266434. This is especially close in design vocabulary, although its endpoint is segmentation rather than named abnormality scores.
- A 2025 foundation-model study directly evaluates feature robustness across three kernels and two slice thicknesses in repeated LDCT reconstructions. PMID: 42038169. This materially weakens any broad novelty claim about “foundation-model reliability across reconstruction parameters,” though it does not appear to test CT-CLIP's 18 scan-level outputs.

Thus the defensible delta is narrow: **CT-RATE-specific paired reconstruction consistency of released CT-CLIP abnormality outputs, plus a scan-clustered audit of its validation protocol.** Searches here did not establish that this exact audit is unpublished; proceedings and citing-paper searches remain required. Novelty confidence should remain 3 or fall to 2 until those are checked.

## Medical relevance and negative-result value

The immediate medical relevance is moderate, not high. CT-CLIP/ClassFine is a released research model, and this experiment does not connect a threshold crossing to a clinical decision or a radiologist's interpretation. A large discordance is actionable for model evaluation and dataset design. It is not yet evidence that “a clinician cannot act on” the concept, because no clinical operating point or workflow is evaluated.

The proposed negative is not fully decisive. Near-identical outputs would establish robustness only for multiply reconstructed CT-RATE scans, their observed reconstruction contrasts, this checkpoint, and this preprocessing. It would not reassure against site/scanner shift or ordinary test-retest variation. Meanwhile an unchanged AUROC with wider clustered intervals addresses a different question. Split the outcomes:

- **High within-acquisition agreement:** decisive for the narrow reconstruction-repeatability hypothesis if the contrast and equivalence margin are prespecified; otherwise sensitivity-limited.
- **No AUROC point-estimate change:** weak by itself, because weighting and labels can hide paired score changes.
- **No confidence-interval change:** informative only after selecting the clustered estimator and attaining enough independent positive/negative scans per abnormality.

Rare abnormalities may make per-concept threshold flips and AUROC too imprecise. Prespecify a prevalence/positive-count rule and label the remaining categories exploratory rather than silently presenting 18 underpowered tests.

## Availability and compute

Access is a real pause condition, though not presently fatal. The files are gated and the full corpus is 21.3 TB. The card should not call this “fully public” under a charter that excludes dependence on unconfirmed gated data. Accepting conditions appears user-mediated and cannot be assumed complete. Before a feasibility score of 4 is retained, directly verify access to the two small tables and one paired image group.

Compute is probably manageable: the authors report 0.5 seconds per ClassFine volume and smaller-GPU inference. Storage/download, exact preprocessing, checkpoint loading, and memory are more credible risks than raw inference time. Do not alter patch size to fit the GPU, because the official repository says this can affect small-pathology performance; use batch size one or pause if the released configuration itself does not fit.

## Easier version and low-hanging fruit

The genuine low-hanging fruit is **not** the claimed label-only confidence-interval audit. It is a metadata and release-structure audit that answers whether the substantive experiment is identified:

1. With the small validation labels/metadata tables, count reconstruction groups, longitudinal scans, and patients; test whether labels/reports are exactly duplicated within scan; enumerate the parameter contrasts; and reconcile 1,304 versus 1,314 patients.
2. If the authors have released per-volume ClassFine scores (this remains unverified), analyze those immediately with no image download or GPU. This would be the cheapest faithful version and should be explicitly sought in repository artifacts, evaluation outputs, model cards, or from the authors.
3. If scores are not released, download a small, stratified set of approximately 50–100 clean, same-acquisition pairs spanning the common reconstruction contrasts. Run the unchanged released checkpoint. Use continuous paired score differences across all 18 outputs as the first endpoint; treat rare-label AUROC and flip rates as later analyses.

Existing assets are unusually strong: official grouping keys, small metadata/label tables, released inference code, and released ClassFine weights. What does **not** yet exist in inspected form is the essential per-volume output table. Asking the authors for validation logits is therefore the highest-value shortcut: it could eliminate terabytes of image access and most GPU work while preserving both the repeatability and clustered-benchmark questions.

## Required revision before a feasibility memo

- Rename the study as within-acquisition reconstruction repeatability.
- Make access to small tables and one image pair a hard gate; downgrade data readiness until demonstrated.
- Replace the Stage 0 design-effect promise with a cluster/metadata/label provenance audit.
- Define the unit and estimand separately for scan and patient; handle multiple scans per patient.
- Establish comparable reconstruction contrasts from metadata before causal wording.
- Use paired differences/limits of agreement as primary; justify any ICC model and equivalence margin.
- Separate model-score repeatability from benchmark inference and from concept validity.
- Remove the general attenuation ceiling and clinical-actionability language.
- Search the model repository, authors' artifacts, MICCAI/SPIE/MIDL proceedings, PubMed, and citing literature for both released logits and exact prior audits.
- Freeze one checkpoint, one unmodified preprocessing pipeline, pair inclusion rules, thresholds, primary concepts or multiplicity plan, and the bootstrap unit before inspecting substantive score differences.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Across metadata-confirmed alternative reconstructions of the same CT-RATE acquisition, how much do the released ClassFine abnormality scores change, and do scan- rather than reconstruction-weighted validation estimates materially alter conclusions?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes—if clean reconstruction contrasts and either released logits or a bounded paired download exist, because it audits a widely reused chest-CT resource with no retraining and can change both robustness reporting and benchmark inference.


===== ideas/004/debate.md =====
# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed Stage 0 cannot answer the study's benchmark-precision question, because duplicated labels and reconstruction counts do not identify the sampling variance of AUROC or any other model-performance statistic.

**Argument:** The design claims that `valid_predicted_labels.csv` and cluster sizes alone yield “the factor by which a naive per-volume confidence interval is too narrow.” They do not. Within-scan agreement of report-derived label vectors is mechanical duplication, whereas the relevant dependence is in ClassFine scores, errors, losses, or estimator influence values. AUROC is a pairwise rank statistic whose clustered variance depends on the joint distribution of positive and negative model scores; it cannot be recovered from label ICC and cluster size using the simple `1 + (m-1)rho` design-effect formula. Moreover, per-volume and one-per-scan AUROC target different weighting estimands, so a point-estimate difference is not automatically inflation or bias. The metadata-only audit can establish grouping, duplicated labels, and reconstruction contrasts, but the precision claim requires per-volume model outputs and a prespecified reconstruction-, scan-, or patient-weighted estimand with bootstrap resampling at the corresponding independent unit. The narrowed ClassFine audit still retains the core identity of the original paired-reconstruction question, but Stage 0 as written does not test its second half.

**What would change my mind:** Show either released validation logits or newly generated unchanged-checkpoint logits, then specify the target estimand and demonstrate with a scan- or patient-cluster bootstrap that the per-volume analysis materially changes interval width or conclusions; alternatively, remove the precision result from Stage 0 and describe that stage only as a linkage and feasibility audit.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** Stage 0 advertises a number it cannot compute. Label duplication and cluster sizes give the *structure* of the validation set, not the *sampling variance* of any performance statistic on it. Label ICC is mechanically ~1 and carries no information about model behaviour; AUROC's clustered variance depends on the joint distribution of positive and negative scores; and one-per-scan versus per-volume AUROC are differently weighted estimands rather than a corrected and an inflated version of the same one. So "the factor by which a naive per-volume confidence interval is too narrow" is not obtainable from `valid_predicted_labels.csv` plus filenames.

**Response:** CONCEDE

**Argument:** The objection is correct, and the error is specific enough to name. I conflated the cluster structure of an evaluation set with the variance of a statistic computed on it. `1 + (m-1)rho` is the design effect for the mean of exchangeable observations in equal-sized clusters; here the estimator is not a mean, the units entering it are pairs rather than observations, and the clusters are unequal in size. The `rho` that enters any correct clustered variance is the within-scan correlation of score-dependent quantities — errors, losses, influence contributions — which requires exactly the per-volume model outputs I claimed Stage 0 could do without. An ICC of 1.0 on duplicated label rows is a fact about how the corpus was released, not a fact about an estimator. The sentence in the idea card should be struck, not reworded.

What Stage 0 keeps is still worth doing and still cheap: cluster counts and the reconstructions-per-scan distribution, an exact-duplicate check on labels and reports within scan, the enumeration of reconstruction parameter contrasts from `validation_metadata.csv`, the 1,304-versus-1,314 patient reconciliation, and the go/no-go on paired-image access. What it loses is the headline deliverable — "the benchmark's error bars are N times too narrow," obtainable from a 174 kB CSV with no model and no GPU. That was the cheapest advertised result and a large part of why the candidate read as a one-afternoon measurement. Conceding it makes the study strictly more expensive: every precision claim now sits behind logits, whether released or regenerated.

One point in the objection I want to keep on the table without pretending it rescues Stage 0. When a paper reports "AUROC on the CT-RATE validation set," the estimand a reader infers is per-scan or per-patient diagnostic performance, not reconstruction-weighted performance. On that reading a reconstruction-weighted computation is a reporting defect even where it is not estimator bias in the narrow sense — the number answers a question nobody asked. But that is a claim about the interpretation of a published quantity, it is still only testable with scores in hand, and it changes nothing about the arithmetic. It belongs in Stage 1, not as a defence of Stage 0.

The precision half of the question therefore relocates rather than dies: with logits, prespecify reconstruction-weighted, scan-weighted (mean score per scan, and separately a random-draw-per-scan variant), and patient-weighted estimands; bootstrap at the patient level as the outermost independent unit, since patients contribute multiple scans and scans contribute multiple reconstructions; report interval widths for each without predeclaring a direction of change. The original one-sentence question survives intact — what dies is my claim that its second half could be answered without running the model.

The honest replacement for the lost cheap deliverable is a search task, not a compute task: establish whether per-volume ClassFine validation scores were ever released alongside the checkpoints or in the paper's evaluation artifacts. If they were, the relocated precision analysis costs no image download and no GPU and Stage 0's cost profile is nearly restored. If they were not, the candidate must be re-costed as inference-first, and the feasibility score of 4 should be revisited on that basis rather than on the gated-access risk alone.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The revised design still cannot attribute paired score differences to reconstruction variation, because its identical-file rerun control tests stochastic execution rather than the deterministic preprocessing differences induced by distinct source grids.

**Argument:** The proposer correctly preserves the original question by relocating the benchmark-precision analysis behind logits, so the Round 1 objection is resolved. The strongest remaining problem is the causal interpretation of the repeatability arm. ClassFine does not consume the released reconstruction untouched: CT-CLIP preprocessing resamples, crops or pads, and normalizes each 3D volume, while CT-RATE itself has undergone spacing and intensity corrections. Alternative reconstructions can differ in voxel spacing, slice thickness, field of view, orientation, and matrix as well as kernel. Running one identical file twice in evaluation mode should return the same score and therefore only bounds stochastic software noise; it cannot reveal whether a paired score difference arose from the reconstruction contrast itself or from deterministic interpolation, crop inclusion, padding, or normalization triggered by the two grids. This matters because the card explicitly says that control “rules out” preprocessing instability and then interprets the residual as reconstruction-induced concept variation. The proposed output remains a valid estimate of end-to-end *pipeline consistency across released reconstruction variants*, but that is narrower than identifying a model response to reconstruction content and does not support kernel-specific or image-content-specific language. A deterministic re-save is also insufficient unless it reproduces the relevant grid transformations. The design needs a preprocessing perturbation control matched to each pair: transform one member onto the other's grid (and, where possible, the reverse) while holding its intensities/content source fixed, then compare the score change from grid/preprocessing alone with the actual cross-reconstruction change. If reconstruction metadata show bundled changes that cannot be separately recreated, the estimand must remain explicitly composite.

**What would change my mind:** Prespecify and demonstrate a matched-grid preprocessing control for representative metadata-confirmed pairs, showing that deterministic resampling/cropping of one reconstruction onto the partner's geometry produces materially smaller score changes than the true pair; otherwise revise the claim throughout to end-to-end pipeline repeatability under composite released reconstruction variants and stop saying the identical-file control rules out preprocessing.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The identical-file rerun bounds stochastic execution noise only. Because the released pipeline resamples, crops/pads and normalises each volume before the network sees it, two reconstructions arriving on different voxel grids get deterministically *different* preprocessing, and that difference is not stochastic and is therefore invisible to the rerun control. So the card is wrong to say the control "rules out" preprocessing, and wrong to read the residual as reconstruction-induced concept variation. The honest estimand is composite end-to-end pipeline repeatability unless a matched-grid control separates the two.

**Response:** AMEND

**Argument:** The two language defects are conceded without qualification: "RULED OUT by the identical-volume repeat control" in `alternative_explanations[1]` is false and must be struck, and "reconstruction-induced" must not appear as a causal descriptor for the unstratified corpus. The identical-file rerun establishes determinism of the software, nothing more, and I will label it that way.

What I dispute is the scope of the damage, and I have new evidence rather than a restatement. I read the released preprocessing rather than reasoning about it in the abstract — `scripts/data_inference_nii.py` in the official repository (raw.githubusercontent.com/ibrahimethemhamamci/CT-CLIP/main/scripts/data_inference_nii.py, inspected 4 Aug 2026). The differential surface is smaller and far more legible than the objection assumes:

- HU conversion is `slope`/`intercept` read per volume from the metadata CSV (`row["RescaleSlope"]`, `row["RescaleIntercept"]`).
- Clipping is `hu_min, hu_max = -1000, 1000` — **fixed constants**. Normalisation is `img_data / 1000` — a **fixed scalar**. There is no percentile, mean/std, or otherwise data-dependent intensity step. This removes an entire class of content-driven differential preprocessing that the objection allows for.
- Resampling is `F.interpolate(..., mode='trilinear', align_corners=False)` to a fixed target of 0.75 × 0.75 × 1.5 mm, with the scaling factor computed from `row["XYSpacing"]` and `row["ZSpacing"]`.
- Crop/pad is a centre crop or a symmetric pad with value `-1` to a fixed `target_shape = (480, 480, 240)`.

So `nii_img_to_tensor` is a deterministic function whose *shape* is fully determined by five per-volume scalars: RescaleSlope, RescaleIntercept, XYSpacing, ZSpacing, and the source array dimensions. Everything else is a constant. That yields a sharper repair than the one proposed.

**The amendment: stratify on geometry-matched pairs, and make that stratum the primary analysis.** If two members of a scan group share slope, intercept, XY spacing, Z spacing and array shape, then the resample scaling factors are identical, the crop/pad offsets are identical, and the intensity map is identical — the preprocessing applied to the two volumes is not "approximately matched," it is *the same function*. For that stratum there is no differential preprocessing effect to control for, and the paired score difference is attributable to the reconstruction content itself. Same-geometry sharp/soft kernel pairs from one raw acquisition are the textbook reconstruction variant, so this stratum is plausibly non-empty; whether it is *large* is unknown and becomes a hard Stage 0 gate. Critically, this costs nothing new: `validation_metadata.csv` demonstrably carries those exact columns, since the released loader indexes them by filename. The gate is one metadata query on a file already first on the Stage 0 list.

This is stronger than the proposed matched-grid control, which I adopt but reassign. Resampling A onto B's grid does not reproduce reconstructing at B's parameters: trilinear interpolation is a low-pass operator, native sharp-kernel reconstruction is not, so `resample(A → grid_B)` carries A's frequency content plus an interpolation artefact that neither released volume has. Its correct use is a three-way decomposition, not a two-way subtraction — `d_grid = |s(A) − s(resample(A→grid_B))|`, `d_content = |s(resample(A→grid_B)) − s(B)|`, against `d_total = |s(A) − s(B)|`, symmetrised in both directions and checked for consistency. Its interpretation is asymmetric: a *large* `d_grid` is decisive (the pipeline is grid-fragile and no content attribution is available), while a *small* `d_grid` licenses only a weak content inference, because the interpolation artefact contaminates `d_content`. I will run it on the geometry-*mismatched* pairs as a secondary mechanistic analysis with that asymmetry stated in advance, and not as the identification strategy.

One point I want on the record without pretending it answers the objection. The primary scientific claim — the repeatability coefficient and what it bounds — needs the *composite* quantity, not the decomposed one. The deployed measurement is `released volume → released pipeline → score`. When a technologist's reconstruction choice moves that score, the clinical consequence is identical whether the mediator is trilinear interpolation in the loader or high-frequency kernel content in the image. Decomposition is a mechanistic question and it is downstream of the reliability question. The original one-sentence question asks *how much the score changes*, not *why*; the composite estimand answers it exactly, and the mechanistic arm is an addition to the study rather than a repair of it.

**What is lost.** Kernel-specific and content-specific language disappears for the corpus as a whole, and survives only inside a stratum whose size I cannot yet count — that is a genuine new failure mode, not a rhetorical hedge. If the geometry-matched stratum turns out to be empty or too small to estimate a per-concept ICC, the mechanistic arm collapses to the contaminated three-way decomposition and the study becomes pipeline repeatability under composite variants, exactly as the critic demands. Stratification also shrinks the usable N for the mechanistic arm, so the power calculation must run on the stratum rather than on the full paired set. And a specific bad case is now visible that the card did not anticipate: if CT-RATE's reconstruction variants differ predominantly in slice thickness rather than kernel at fixed thickness, the geometry-matched stratum is empty *by construction* and the interesting version of the experiment is unavailable. That is a real risk and the Stage 0 metadata query resolves it before any download.

**Identity check.** The one-sentence question is "when the same chest CT acquisition is reconstructed twice, how much does a released chest-CT foundation model's predicted abnormality concept change, and does the per-volume unit of analysis overstate precision." Nothing in this amendment touches either clause. The composite estimand answers the first clause on its own terms; the geometry-matched stratum and the decomposition are added mechanistic detail. The amendment restricts an *interpretive* claim I had no right to, not the measurement. Identity holds.

**Tally.** This is one concession and one amendment across two rounds. The concession removed a deliverable; this amendment removes a causal reading. Neither has touched the measurement itself, but a third hit that does would mean the candidate is a different study and should be re-scoped rather than patched again.

**Status:** OPEN

## Round 3 — CRITIC

**Position:** The amendment preserves the original question and adequately narrows the preprocessing claim, but the proposed primary statistic still cannot establish that ClassFine outputs are repeatable in the clinically relevant sense because a high pooled ICC can coexist with large within-scan changes and frequent decision reversals.

**Argument:** The new inspection of `data_inference_nii.py` materially answers Round 2: restricting causal language to geometry-matched pairs and treating all other pairs as an end-to-end composite is an adequate repair, and the revised design still asks how much scores change across reconstructions, so the identity check passes. The strongest remaining defect is now the measurement model. ICC is a ratio of between-scan variance to total variance. For an abnormality head whose scores separate obvious negatives from obvious positives, between-scan variance can be enormous, producing an ICC above 0.95 even if paired reconstructions move scores enough to reverse many borderline decisions. Conversely, a restricted or rare-finding stratum can produce a low ICC despite small absolute paired differences. Pooling heterogeneous reconstruction contrasts worsens the problem, and `ICC(2,1)` presumes a rater-like crossed structure that reconstruction IDs with inconsistent meanings and unequal group sizes do not supply. Therefore the anticipated negative—“ICC above 0.95 with low-single-digit flips”—is not yet decisive: 0.95 is unsupported, “low single digits” is unsupported, and threshold flips are uninterpretable unless the threshold is frozen from the released model or an external validation rule rather than selected after viewing these pairs. The primary analysis should instead estimate the paired score-difference distribution within prespecified reconstruction-contrast strata, including a repeatability coefficient or upper quantile of absolute change and crossing rates at frozen operational thresholds. A reassuring result requires a prespecified equivalence margin tied to an observable consequence, such as the largest score perturbation that does not materially change sensitivity/specificity or classifications on an independent calibration set. ICC can remain descriptive, but it cannot carry the equivalence claim. This matters to the benchmark arm too: patient-clustered intervals answer dependence, while paired-difference margins answer stability; neither substitutes for the other.

**What would change my mind:** Before inspecting paired ClassFine differences, freeze the checkpoint and preprocessing, define comparable reconstruction strata, identify thresholds without using the audit pairs, and justify per-output or grouped equivalence margins in score or decision space; then show confidence intervals for the upper paired-difference bound and threshold-crossing rate lie within those margins, with rare outputs declared exploratory when independent positive/negative scan counts are inadequate.

**Status:** OPEN

## Round 3 — PROPOSER

**Responding to:** ICC cannot carry the equivalence claim. It is a ratio of between-scan to total variance, so a head that cleanly separates obvious negatives from obvious positives can post ICC > 0.95 while paired reconstructions still move borderline scores enough to reverse decisions; a rare-finding stratum can post a low ICC despite trivial absolute differences. `ICC(2,1)` also assumes a crossed rater-like structure that unequal, inconsistently-meaning reconstruction IDs do not supply. Consequently the anticipated negative — "ICC above 0.95 with flip rates in the low single digits" — is unsupported in both of its numbers, and flip rates are uninterpretable unless the threshold comes from somewhere other than the audit pairs. Primary analysis should be the paired-difference distribution within reconstruction-contrast strata, with a repeatability coefficient and an equivalence margin tied to an observable consequence.

**Response:** AMEND

**Argument:** The objection is correct and I concede it without reservation: ICC(2,1) is demoted to descriptive, and both numbers in `anticipated_negative` — the 0.95 and the "low single digits" — are struck as illustrative cutoffs I had no basis for. The embarrassing part is that the fix was already inside the construct I claimed to be borrowing. Raunig et al., the QIBA Technical Performance working-group review (Stat Methods Med Res 2015;24(1):27–67; PMID 24919831; PMC5574197), states explicitly that a high ICC may mainly reflect between-subject heterogeneity in the sampled population and does not guarantee precision of quantification, which is why that tradition reports the repeatability coefficient from the within-subject variance instead. I imported the vocabulary of quantitative imaging biomarkers and then used the one statistic that tradition warns against. That is a self-inflicted wound, not a discovered limitation.

Three things I want to add rather than merely accept, because the critic's replacement needs specification before it is usable, and two of the three come from code I read after the objection.

**(a) The proposed replacement needs the same stratification it demands of ICC.** I checked what ClassFine actually emits: `scripts/zero_shot.py` applies `torch.nn.Softmax(dim=0)` over a two-element [present, absent] vector per pathology and writes `predicted_weights.npz`. The output is therefore a bounded probability, and the paired-difference distribution of a bounded score is structurally heteroscedastic — variance is compressed near 0 and 1 and maximal mid-range. A single pooled repeatability coefficient is misleading for exactly the reason a pooled ICC is: it averages over a variance that is a function of score location. So the RC and the upper quantile of |Δ| get reported within score-region bins as well as within reconstruction-contrast strata, with the bin assigned by the *mean* of the pair rather than by either member, Bland–Altman fashion, to avoid regression-to-the-mean selection. I will also report on the logit scale, where the variance is closer to constant, and state which scale the margin is defined on. This does not rescue ICC; it stops the replacement inheriting the same defect.

**(b) "Freeze the threshold from the released model" is not available, and the released code is why.** `scripts/eval.py` defines `choose_operating_point(fpr, tpr, thresholds)`, which walks the ROC and returns the sensitivity/specificity maximising Youden's J — selected on the evaluation set itself. There is no published fixed operating point to inherit, and the one that exists was chosen on the same reconstruction-duplicated validation data it reports. A flip rate computed at "the released threshold" would therefore be contaminated twice over. The concrete fix costs nothing: validation scans carrying exactly **one** reconstruction are disjoint by construction from the paired audit set, sit in the same distribution, and can supply a per-output Youden threshold that never sees a pair. If that singleton stratum proves too small for stable threshold estimation, the fallback is thresholds derived from the training split. Either is fixable in advance of looking at a single paired difference, which is precisely what the critic asked for. Whether the singleton stratum is large enough becomes a second hard Stage 0 gate alongside the geometry-matched count, and both are answered by the same metadata query.

**(c) A better consequence anchor than threshold crossing, which also links the two arms.** ClassFine is not deployed at an operating point; it is read through AUROC, a rank statistic. The decision-relevant consequence of a score perturbation for the way this model is actually used is rank displacement, not threshold crossing. So the prespecified primary consequence measure becomes the **reconstruction-swap AUROC delta**: recompute each output's AUROC with every multiply-reconstructed scan represented by its alternate reconstruction, over the distribution of swap assignments, with intervals bootstrapped at the patient unit. It needs no threshold, it is denominated in the units the benchmark already reports, and it gives the equivalence margin an anchor that is observable and external: the margin can be set against the published between-method gaps on this same validation split — the CT-Net / Swin3D / CT-ViT / global-local spread tabulated in arXiv:2503.20652 — read off those tables before I compute anything of my own. If a technologist's reconstruction choice moves AUROC as far as the method differences the benchmark is used to adjudicate, the benchmark cannot resolve those differences; that is an observable consequence, not a convention. Threshold-crossing rates at the singleton-derived thresholds drop to secondary, and per-output analyses are declared exploratory below a prespecified independent positive-scan count.

One bounded note on the benchmark arm, which does not reopen Round 1. `eval.py` bootstraps with `resample(idx, replace=True, random_state=i)` over row indices of the prediction array, 1000 replicates, percentile intervals. The published intervals therefore resample volumes and treat duplicate reconstructions of one scan as exchangeable rows. My Round 1 concession stands unchanged — this still cannot be evaluated without logits — but the target is no longer an abstraction: it is a named estimator in released code, and the comparison is that same function resampling scan or patient identifiers instead of rows.

**What is lost.** The reliability coefficient stops being the headline. With the attenuation bound already removed by the critique and ICC now demoted, what survives of the psychometric borrowing is thinner than the card claims: the insistence on a within-subject variance component, a repeatability coefficient reported with its scale and stratum, and a margin fixed before the data are seen. That is methodological hygiene, not a new bound, and the `cross_domain` block must be rewritten to say so — "what changes if the analogy is dropped" now answers *you would report a flip rate with no reference and no margin*, which still clears the charter's decoration test but at reduced value. Second loss: `anticipated_negative` can no longer be stated numerically at all until the margin is fixed from published tables and the singleton stratum is counted. Under the charter's classification the negative is decisive **only** conditional on a prespecified, powered margin; unconditionally it is sensitivity-limited. I recommend `negative_result_value` drop from 5 to 4 pending margin prespecification, and that the reviewer treat 4 as itself conditional on the two Stage 0 gates returning non-empty.

**Identity check.** The question remains "when the same chest CT acquisition is reconstructed twice, how much does a released chest-CT foundation model's predicted abnormality concept change, and does the per-volume unit of analysis overstate precision." This amendment changes how the paired scores are summarised, not which scores are compared or on what. The measurement — released volume pair, unmodified checkpoint, unmodified preprocessing, paired difference — is byte-identical to what Round 2 left. Identity holds. I note that in Round 2 I drew the line at "a third hit that touches the measurement itself," and that this hit lands on the summary statistic instead. That distinction is real but it is thin, and I should not be allowed to invoke it a second time.

**Tally.** One concession and two amendments across three rounds. The concession removed a deliverable, the first amendment removed a causal reading, this one removes a primary statistic and an anticipated result. Nothing has yet touched what is measured, but the card that goes to feasibility is meaningfully poorer than the card that entered this debate, and the revision should present it as such rather than absorbing three hits into unchanged prose.

**Status:** CONVERGED

I accept the whole of the critic's prespecification list — frozen checkpoint and preprocessing, comparable strata, audit-pair-independent thresholds, justified margins, exploratory labelling of underpowered outputs — and (a)–(c) above fill the two places where that list was not yet operational: where the thresholds come from, and what the margin is denominated in. What I cannot supply is the demonstration the list ends with, that the intervals fall inside the margins. That requires gated data and a GPU, so it is the next gate rather than this debate's business. There is no remaining disagreement about the design; there are three empirical gates — geometry-matched pairs exist, singleton scans suffice for thresholds, per-output positive counts support the analysis — any of which can still kill the study before it runs.


===== ideas/004/feasibility.md =====
# Feasibility memo — idea 004

**Question under audit:** Across geometry-matched alternative reconstructions of the
same CT-RATE acquisition, how much do the frozen ClassFine abnormality scores change?

**Date:** 2026-08-11. All web inspections performed today unless attributed to Stage 0
(2026-08-04) or the prior critique.

---

## 1. Keystone resolution: the checkpoint EXISTS (headline finding)

Stage 0 concluded the ClassFine checkpoint was unavailable after inspecting GitHub
v1.0.0 release assets and the authors' Hugging Face *model* account. Both were the
wrong places. Directly inspected today:

- **Verified fact:** The official CT-CLIP GitHub README
  (github.com/ibrahimethemhamamci/CT-CLIP) links model downloads hosted **inside the
  CT-RATE dataset repository**: "CT-CLIP (ClassFine): Download Here →
  `huggingface.co/datasets/ibrahimhamamci/CT-RATE/blob/main/models/CT-CLIP-Related/CT_LiPro_v2.pt`".
- **Verified fact:** The HF file-listing page for
  `datasets/ibrahimhamamci/CT-RATE/tree/main/models/CT-CLIP-Related` displays three
  files — `CT-CLIP_v2.pt`, `CT_VocabFine_v2.pt`, `CT_LiPro_v2.pt` — each **1.77 GB**,
  pickle format. The listing is visible without authentication ("You can list files
  but not access them"); downloads require accepting the gate.
- **Verified fact:** The HF API reports `gated: "auto"` — approval is automatic on
  agreeing to share contact information. No manual review, no DUA committee. This
  satisfies the charter's "no unconfirmed DUA-gated data" constraint once the user
  performs the one-time click-through.

**Naming caution (verified):** the file the README labels "CT-CLIP (ClassFine)" is
named `CT_LiPro_v2.pt` (linear-probing nomenclature). The load probe must confirm the
inference scripts (`run_forward_data.py` / `data_inference_nii.py`, identified in
Stage 0) consume this file for the 18-output ClassFine head.

**Keystone status: INSPECTED_TRUE for existence and obtainability** (official path,
file size, gate mechanics all directly inspected).

*"If I have only verified the nearest checkable thing, what am I still assuming?"*
I verified the file exists at an officially endorsed path. I am still assuming:
(a) the checkpoint **loads unchanged** with the released inference code and emits 18
scores; (b) the **v2** weights are the version corresponding to the current released
preprocessing and the published results (CT-RATE was corrected post-release; the
repo's main branch and the v2 checkpoints are the officially endorsed current
pairing, but paper-number correspondence is inferred, not inspected). Assumption (a)
is load-bearing and cheap to kill: it is the smallest probe (§9). Assumption (b) does
not threaten the primary readout, which compares the model with itself; it only
constrains how the result is attributed ("the released v2 ClassFine checkpoint",
not "the checkpoint behind Table N of the paper") until verified. Freeze the HF
commit hash and the LFS SHA-256 (displayed by HF) at download time.

## 2. Closest work and exact gap

Nearest works, all from the prior critique (primary sources inspected then), none
overturned by today's searches:

- Zuo et al., cross-domain feature-map consistency across paired LIDC kernels
  (PMCID PMC9503667) — segmentation, not CT-RATE, not ClassFine outputs.
- Hwang et al., kernel conversion for quantitative chest CT (PMID 35112080, DOI
  10.3389/frai.2021.769557) — quantitative measures, not abnormality heads.
- Liard et al., kernel variability vs segmentation consistency in low-dose thoracic
  CT (DOI 10.1117/12.3085743) — closest design vocabulary, segmentation endpoint.
- LDCT foundation-model feature robustness across kernels/thickness (PMID 42038169)
  — features, not CT-CLIP's 18 scan-level outputs.

Today's targeted searches (CT-CLIP/CT-RATE reconstruction sensitivity; CT-RATE
duplicate-reconstruction benchmark bias) surfaced **no** paper performing a paired,
within-acquisition, geometry-matched audit of ClassFine scores on CT-RATE, and none
exploiting the reconstruction duplication for evaluation-dependence analysis.
**"I did not find it" is not proof**: MICCAI/SPIE/MIDL proceedings and the full
CT-RATE citation graph remain unsearched at depth. Novelty confidence stays at 3.

**Exact gap:** paired reconstruction sensitivity of a released 3D chest-CT
foundation model's named abnormality outputs, on the corpus that model was trained
and benchmarked on, with preprocessing held byte-identical via geometry matching.

## 3. Dataset access and license

- CT-RATE: gated `auto`, CC-BY-NC-SA-4.0 (verified on dataset card today).
  Non-commercial research use is compliant. No redistribution of images.
- Total corpus 21.3 TB, but the study needs **850 validation volumes** (425 pairs,
  Stage 0 frozen list) plus one 1.77 GB checkpoint. Per-file HTTP download is
  supported, so the gated corpus size is irrelevant.
- Validation patient count on the card: **1,304** — matches Stage 0's count and
  resolves the 1,304-vs-1,314 discrepancy in favor of the official card (the 1,314
  figure belongs to the external benchmark paper's filtering, to be noted, not used).

## 4. Labels and concept validity

The primary readout is **label-free** (model vs itself on paired volumes). CT-RATE's
RadBERT-derived labels are used nowhere in the primary endpoint; the 18 outputs are
named report-derived heads, not validated concepts, and the card's prohibited
conclusions already enforce that language. No annotation-provenance exposure.

## 5. Sample structure and split unit

Stage 0 (directly inspected metadata): 3,039 validation volumes / 1,564 scans /
1,304 patients; 425 strict geometry-matched pairs; contrasts Br40f|Br60f (237),
Bl56f|Br40f (126), Bl57d|Br36d (58), Br40f|Br44f (4, exploratory). Patient is the
outer bootstrap unit (patients contribute multiple scans). The pair list is frozen
before any download. 462/464 audited volumes Siemens — vendor-specific scope stands.

## 6. Code and checkpoints

- Inference code: verified present in the official repo (Stage 0).
- Checkpoint: verified present and obtainable (§1).
- Preprocessing: deterministic, fully characterized in the idea-006 unblock check
  (fixed HU clip, fixed resample target, fixed crop/pad) — supports the
  geometry-matched identical-function argument.

## 7. Compute estimate

- Download: 850 volumes × ~0.42 GB average (21.3 TB / 50,188) ≈ **~360 GB** total,
  processed in chunks (download → preprocess → infer → delete) within Colab Pro+
  disk limits. This is the dominant cost: dozens of hours of transfer, days of
  wall-clock across sessions, not GPU-bound.
- Inference: ~0.5 s/volume (official README) → minutes of GPU. Preprocessing
  (trilinear resample to 0.75×0.75×1.5 mm, crop/pad to 480×480×240) dominates at
  maybe 10–30 s/volume CPU → single-digit hours.
- No patch-size modification permitted (official warning re small-pathology
  performance); released configuration at batch size 1.

## 8. Baselines, metrics, leakage, confounds

- Metrics: paired score differences (probability and logit scales), repeatability
  coefficient / upper |Δ| quantile per contrast stratum, patient-level bootstrap.
  All standard; no custom infrastructure.
- Equivalence margin: to be fixed from the CT-Scroll benchmark's between-method
  AUROC spread on CT-RATE validation (arXiv:2503.20652 — existence and CT-RATE
  evaluation verified today from the abstract; **tables not yet extracted**, PDF
  inspection required at margin-fixing time, before any paired score is seen).
- Leakage/confounds: within-pair design removes patient, anatomy, habitus,
  prevalence, referral, and report-leakage alternatives; strict geometry matching
  removes differential preprocessing; vendor (Siemens) and site remain scope
  limitations, already stated. Interpretive note, not leakage: ClassFine was
  trained on reconstruction-expanded data, so observed invariance is partly a
  learned property of this training policy — the claim is already restricted to
  this checkpoint.

## 9. Smallest probe of the riskiest assumption

Riskiest surviving assumption: **the checkpoint loads and runs unchanged with the
released code** (§1a). Probe, requiring human approval and gate acceptance, before
any bulk download:

1. Accept the CT-RATE gate (one click-through; user action).
2. Download `CT_LiPro_v2.pt` (1.77 GB); record HF commit hash and SHA-256.
3. Load with the released inference scripts; confirm an 18-output head.
4. Download **one** Br40f|Br60f pair (~1 GB); run inference; confirm scores emerge
   and that an identical-file rerun is bit-deterministic.

Total ≈ 3 GB and under an hour of session time. If step 3 or 4 fails, the idea
stops per the card's stop rule before any material cost.

## 10. Verification ledger

| Claim | Status |
|---|---|
| ClassFine checkpoint exists at official path, 1.77 GB | VERIFIED (file listing inspected) |
| Gate is automatic click-through | VERIFIED (API `gated:"auto"`) |
| License CC-BY-NC-SA-4.0 | VERIFIED (dataset card) |
| Checkpoint loads with released code | NOT VERIFIED — probe §9 |
| v2 weights ↔ published paper numbers | NOT VERIFIED — attribution constrained until checked |
| 425 geometry-matched pairs | VERIFIED (Stage 0 direct metadata audit) |
| CT-Scroll margin tables usable | PARTIALLY — paper exists, evaluates CT-RATE; tables not extracted |
| No exact prior audit exists | NOT PROVEN — limited search only; proceedings sweep outstanding |

## 11. Score implications (recommendation only; card not modified)

`keystone_status` should move to `INSPECTED_TRUE`, lifting the cap: feasibility
3 → 4 (bounded download, trivial GPU, frozen pair list; residual is the unprobed
load step), data readiness 3 → 4 (gate confirmed automatic). Novelty confidence
stays 3 pending the proceedings sweep. Priority recomputes to
0.20*4 + 0.15*4 + 0.15*3 + 0.10*4 + 0.10*3 + 0.10*5 + 0.10*4 + 0.05*4 + 0.05*3 = **3.90**.

## Decision

**GO** — conditional on the §9 load probe as the first gated step (needs human gate
acceptance and probe-contract approval), and on fixing the equivalence margin from
the CT-Scroll tables before any paired score is inspected. No blocking unknown
remains; the Stage-0 "checkpoint unavailable" finding is corrected by direct
inspection of the official download path.


===== ideas/004/idea_card.json =====
{
  "id": "idea-004",
  "parent_ids": [],
  "search_mode": "B",
  "title": "Within-acquisition reconstruction sensitivity of ClassFine abnormality scores",
  "question": "Across geometry-matched alternative reconstructions of the same CT-RATE acquisition, how much do the frozen ClassFine abnormality scores change?",
  "one_sentence_claim": "The ClassFine model uses reconstruction-dependent spatial-frequency content when producing named chest-CT abnormality scores.",
  "claim_rung": 1,
  "what_would_move_it_up": "Rung 2 would require showing that the paired effect persists after stratification or adjustment for every remaining measured acquisition and preprocessing difference and across vendors/sites; rung 3 would require a validated, independently computable image measurement that names the responsible content more specifically than reconstruction-dependent spatial frequency.",
  "scientific_uncertainty": "It is unknown whether a frozen chest-CT classifier assigns operationally equivalent scores to two images reconstructed from the same acquisition when anatomy, geometry, and deterministic preprocessing transformations are held fixed.",
  "existing_legwork": "The completed Stage 0 audit inspected 3,039 validation volumes from 1,564 scans and 1,304 patients. It found 1,432 multi-reconstruction scans and 425 strict geometry-matched pairs after excluding slice-count, position, and acquisition-parameter drift. The main contrasts were Br40f|Br60f (237), Bl56f|Br40f (126), and Bl57d|Br36d (58). Labels were exact duplicates within pairs, but labels are not used in the primary readout. The released inference scripts were identified; no official per-volume ClassFine scores or checkpoint release assets were found in the inspected official locations.",
  "missing_final_step": "Obtain and cryptographically freeze the exact ClassFine weights used with the released inference pipeline, then run paired inference on the 425 predeclared geometry-matched pairs and estimate score-change bounds by reconstruction contrast.",
  "concept_definition": "The candidate X is reconstruction-dependent spatial-frequency content: the frequency and noise texture imposed by a named reconstruction-kernel contrast while the acquisition and voxel geometry remain fixed. X is independently measurable without annotation using image-domain noise-power-spectrum or local frequency-energy statistics and the recorded kernel contrast. The study does not claim that any report-derived abnormality label is valid, nor that it has localized the responsible frequency band.",
  "keystone_prerequisite": "The exact frozen ClassFine checkpoint corresponding to the released architecture and preprocessing is obtainable with sufficient provenance to make the resulting scores attributable to the published model.",
  "keystone_status": "NOT_INSPECTED",
  "keystone_evidence": "Direct Stage 0 inspection found no released per-volume ClassFine scores, no GitHub v1.0.0 release assets, and no checkpoint files on the authors' inspected Hugging Face account. The repository contains inference code, but code alone does not establish that the published weights are obtainable. If I have only verified the nearest checkable thing, what am I still assuming? I verified that inference code exists and that 425 clean pairs exist; I am still assuming that the exact published checkpoint can be obtained and loaded unchanged. That assumption is load-bearing and is therefore the keystone.",
  "dies_like_prior": "It risks the DATA_ACCESS failure seen in idea 003: the needed model asset may not be obtainable. Unlike idea 003, the image pairs, metadata, and primary annotation-free readout are already confirmed; however, that does not rescue the study if the exact checkpoint is unavailable. No annotation-provenance failure applies because the primary endpoint compares the model with itself and uses no labels.",
  "closest_prior_work": [
    {
      "citation": "Zuo et al., Adaptation to CT Reconstruction Kernels by Enforcing Cross-Domain Feature Maps Consistency",
      "identifier": "PMCID: PMC9503667",
      "verification": "PRIMARY SOURCE INSPECTED in the prior critique",
      "delta": "Used paired CT reconstructions for lung-CT segmentation and documented kernel inconsistency; it did not audit ClassFine's 18 scan-level abnormality outputs on CT-RATE."
    },
    {
      "citation": "Hwang et al., Kernel Conversion for Robust Quantitative Measurements of Archived Chest Computed Tomography Using Deep Learning-Based Image-to-Image Translation",
      "identifier": "DOI: 10.3389/frai.2021.769557; PMID: 35112080; PMCID: PMC8801695",
      "verification": "PRIMARY SOURCE INSPECTED in the prior critique",
      "delta": "Evaluated quantitative measurements across sharp and soft reconstructions, not the paired stability of the published ClassFine abnormality scores."
    },
    {
      "citation": "Hamamci et al., Developing Generalist Foundation Models from a Multimodal Dataset for 3D Computed Tomography",
      "identifier": "arXiv:2403.17834",
      "verification": "OFFICIAL REPOSITORY AND PRIMARY PAPER INSPECTED in the prior work",
      "delta": "Introduced CT-RATE and ClassFine but did not report the proposed within-acquisition, geometry-matched paired-score audit."
    }
  ],
  "novelty_statement": "No broad novelty is claimed: reconstruction sensitivity of CT models is established. The narrow potential delta is a geometry-matched, within-acquisition audit of the published ClassFine abnormality scores on CT-RATE. Exact novelty remains unverified pending a targeted proceedings and citation search.",
  "smallest_decisive_experiment": {
    "population": "The 425 Stage-0-confirmed geometry-matched same-acquisition pairs; retain the three adequately sized named kernel contrasts as separate strata and leave the four-pair stratum exploratory.",
    "frozen_elements": "Exact checkpoint checksum, released preprocessing, pair inclusion list, score scale, reconstruction strata, multiplicity rule, and equivalence margins are fixed before inspecting paired scores.",
    "primary_readout": "For each abnormality output and reconstruction stratum, paired score differences on the probability and logit scales, summarized by the median, upper quantile of absolute change, and bootstrap confidence interval with patient as the outer resampling unit.",
    "equivalence_rule": "A negative is decisive only where a prespecified, externally justified score-change margin is met by the full confidence interval and the stratum has adequate precision. The margin may not be chosen from these 425 pairs.",
    "secondary_readout": "Descriptive reconstruction-swap rank changes may be reported, but AUROC, threshold flips, and benchmark interval correction are excluded from the clean primary question because they reintroduce labels, calibration choices, and a second estimand.",
    "stop_rule": "Stop before image inference if the exact checkpoint cannot be obtained and provenance-verified. Do not substitute a retrained model under this idea identity."
  },
  "claim_identifiability": {
    "identified": "Within the strict matched pairs, a systematic paired score change identifies sensitivity of the frozen end-to-end model to reconstruction-dependent image content under the observed kernel contrasts.",
    "alternatives": [
      {
        "explanation": "Different anatomy, disease prevalence, body habitus, referral pathway, report leakage, or patient positioning",
        "status": "Ruled out within a pair because both volumes derive from the same acquisition; the primary endpoint does not use reports or labels."
      },
      {
        "explanation": "Different voxel geometry, crop/pad offsets, resampling scale, slope/intercept, or recorded acquisition parameters",
        "status": "Ruled out by the strict Stage 0 matching and exclusions for the primary cohort, subject to a final tensor-level equality audit before scoring."
      },
      {
        "explanation": "Scanner/vendor or site explains the effect",
        "status": "Not ruled out as an effect modifier: 462 of 464 audited volumes were Siemens. The result is vendor-specific and cannot establish cross-vendor behavior. Site may remain entangled if site identifiers are unavailable."
      },
      {
        "explanation": "The effect is caused by a particular frequency/noise property rather than the named kernel itself",
        "status": "Not separated. That is why the rung-1 claim names reconstruction-dependent spatial-frequency content and does not claim a specific anatomical feature or kernel mechanism."
      }
    ]
  },
  "anticipated_positive": "At least one prespecified output and major reconstruction contrast has an absolute-change bound exceeding its external margin, supporting the narrow claim that this model uses reconstruction-dependent spatial-frequency content for that output.",
  "anticipated_negative": {
    "classification": "decisive conditional on margin and precision; otherwise sensitivity-limited",
    "reasoning": "If every adequately powered major contrast has a confidence bound wholly within its prespecified external equivalence margin, the result decisively weakens the hypothesis that the observed CT-RATE reconstruction variation materially changes ClassFine scores. Failure to reject zero, or an interval crossing the margin, is only sensitivity-limited."
  },
  "prohibited_conclusions": [
    "Do not call the pairs test-retest scans; the acquisition was not repeated.",
    "Do not claim kernel invariance, clinical reliability, concept validity, localization, or generalization beyond the observed predominantly Siemens cohort.",
    "Do not infer a general attenuation ceiling for downstream correlations.",
    "Do not describe stable scores as accurate or clinically actionable.",
    "Do not attribute a paired effect to a specific anatomical feature or frequency band without an independent intervention or measurement."
  ],
  "remaining_legwork": [
    "Resolve the checkpoint keystone by inspecting an official weight file, checksum, model configuration, and license; author correspondence is acceptable evidence of access but the actual artifact must be inspected before feasibility can advance.",
    "Perform a targeted primary-source novelty audit of MICCAI, MIDL, SPIE Medical Imaging, Medical Physics, Radiology: Artificial Intelligence, and papers citing CT-RATE/CT-CLIP.",
    "Specify external equivalence margins without examining paired scores and document the clinical or benchmark consequence used to justify them.",
    "Audit equality of every preprocessing-relevant field and final tensor geometry for the frozen pair list before inference.",
    "Calculate confidence-width or minimum-detectable-effect gates per output and contrast before designating analyses confirmatory."
  ],
  "scores": {
    "clarity": {"value": 5, "why": "One frozen model, one set of same-acquisition geometry-matched pairs, and one paired score-change estimand."},
    "identifiability": {"value": 4, "why": "Pairing and strict geometry matching remove the main patient, acquisition, and preprocessing alternatives; vendor/site generalization and the responsible frequency property remain unresolved."},
    "medical_relevance": {"value": 3, "why": "The result determines whether named chest-CT outputs are stable to common reconstruction choices, but the research model is not a clinical device and accuracy is not tested."},
    "interest": {"value": 3, "why": "A within-acquisition self-disagreement is concrete, though reconstruction sensitivity is already an established concern."},
    "prior_legwork": {"value": 4, "why": "Stage 0 already produced 425 clean pairs and dominant contrast counts; the missing checkpoint is a major remaining asset."},
    "feasibility": {"value": 3, "why": "Capped because the true checkpoint keystone is NOT_INSPECTED; conditional on weights, only 850 volumes require inference."},
    "data_readiness": {"value": 3, "why": "Pair membership and metadata are inspected, but image access is gated and the checkpoint is not confirmed."},
    "evaluation_readiness": {"value": 3, "why": "Paired summaries and patient bootstrap are standard, but external equivalence margins still require prespecification."},
    "negative_result_value": {"value": 4, "why": "A powered equivalence result would decisively bound sensitivity for the observed contrasts and checkpoint; without the margin it falls to type 2."},
    "novelty_confidence": {"value": 3, "why": "Capped by the uninspected keystone and held at uncertainty because exact prior-art searching is incomplete."}
  },
  "priority_score": 3.55,
  "priority_arithmetic": "0.20*3 + 0.15*4 + 0.15*3 + 0.10*4 + 0.10*3 + 0.10*5 + 0.10*4 + 0.05*3 + 0.05*3 = 3.55",
  "regret": {"value": 4, "why": "The corpus supplies hundreds of unusually clean paired perturbations, so abandoning the question without first resolving the checkpoint would waste a rare natural control."},
  "recommendation": "REVISE_AND_GATE_ON_CHECKPOINT"
}


===== ideas/004/probe_contract.yaml =====
idea_id: "idea-004"
track: exploratory
question: "Can the officially released v2 ClassFine checkpoint be provenance-frozen, loaded unchanged with the released inference pipeline, and used to emit deterministic 18-head scores for one predeclared CT-RATE validation reconstruction pair?"
risky_assumption_tested: "The officially linked CT_LiPro_v2.pt artifact is compatible with the frozen released code and preprocessing, represents an 18-output ClassFine head, and can run unchanged at batch size 1 within the available compute envelope."
primary_metric: "Successful end-to-end completion: verified checkpoint and code provenance, exactly 18 finite output scores for each inference execution, and bit-identical scores for the repeated execution of reconstruction A."
secondary_metrics:
  - "Peak GPU memory and total GPU minutes for each inference execution."
  - "Wall-clock download, preprocessing, model-load, and inference times."
  - "Per-head scores for reconstruction A and B and their paired differences, retained only as pipeline diagnostics and not as a scientific reconstruction-sensitivity estimate."
baselines:
  - "Identical-file determinism control: run reconstruction A twice from the same frozen input bytes and configuration."
dataset: "Exactly one frozen Stage-0 geometry-matched Br40f|Br60f pair from the CT-RATE validation split (two volumes), selected before score inspection; CT_LiPro_v2.pt from the official CT-RATE dataset repository."
split_policy: "validation split only; this is an exploratory feasibility/load probe, and no model selection, threshold fitting, margin selection, or test-set analysis is permitted"
maximum_variants: 3
maximum_gpu_minutes: 45
maximum_seeds: 1
stopping_rule: "Run only three preregistered executions (A, B, repeated A). Stop immediately on an invalidating failure, after all three executions complete, or when 45 cumulative GPU minutes are exhausted. Do not download or score any additional pair."
positive_pattern: "The pinned artifact loads without architecture or preprocessing changes; each execution produces exactly 18 finite named scores; repeated A is bit-identical; and the three executions finish within 45 GPU minutes at batch size 1 without changing patch size. This authorizes only a later request for human approval of the separate 425-pair floor-study contract."
negative_pattern: "Any magnitude or direction of A-versus-B score differences, including exactly zero difference across all heads, is a scientifically uninterpretable probe observation rather than evidence for or against reconstruction sensitivity. A compatible but slow run that completes correctly within the cap is a feasibility cost finding, not a negative scientific result."
invalidating_failures:
  - "The official gate cannot be accepted or either of the two frozen validation volumes or CT_LiPro_v2.pt cannot be obtained from the recorded official revision."
  - "The checkpoint file, repository revision, or input volumes cannot be cryptographically identified; record the Hugging Face commit hash, checkpoint SHA-256/LFS object identity, code commit, and input-file hashes before inference."
  - "CT_LiPro_v2.pt does not load with the released architecture and inference path without modifying weights, model structure, preprocessing, target shape, or patch size."
  - "The loaded model does not emit exactly 18 finite output scores with a stable head-name/order mapping."
  - "Either member of the selected pair fails the frozen Stage-0 geometry and acquisition matching rules or does not survive the released preprocessing path."
  - "Repeated inference on reconstruction A is not bit-identical under the recorded environment and deterministic evaluation configuration."
  - "Batch-size-1 inference exceeds available memory, crashes, or reaches the 45 GPU-minute cap before the three executions finish."
required_outputs:
  - resolved_config.json
  - per_sample.csv
  - summary.json
  - environment.txt
  - provenance.json
  - input_manifest.csv
  - selection_audit.json
  - run_log.txt
human_approved: true


===== ideas/004/probe_review.md =====
# Probe code review — idea 004 (load probe, contract v1) — ROUND 4

**Reviewed artifacts:** `probes/004/run.py` (revision `759b664`),
`probes/004/requirements.txt`, `probes/004/README.md`,
`probes/004/verification.json`, and `ideas/004/probe_contract.yaml`.
This review is limited to the decision-ledger-authorized exit-7 repair: kernel
normalization, selection diagnostics, and manifest provenance. The previously
approved one-pair, three-execution probe remains unchanged.

**Verdict: APPROVE.** The repair fixes the observed predicate drift without
expanding the experiment. I independently compiled the script and ran
`python probes/004/run.py --smoke --output-dir <temporary-directory>`; it
completed successfully, wrote all required smoke artifacts including the new
`selection_audit.json`, produced 54 per-head rows, and retained the explicit
`contract_satisfied: false` smoke interpretation.

## Contract fidelity

- **No scope or cap drift.** The real path still selects exactly one
  predeclared validation pair and runs A, B, A-repeat only. The 45-minute,
  three-execution, one-seed gates and the diagnostic-only treatment of A-vs-B
  differences are unchanged (`run.py:982-1002`, `run.py:1141-1194`).
- **Kernel repair matches the ledger.** `normalize_kernel` strips a raw string
  and, for a parsable list literal, uses element 0; selection applies that
  function only to Br40f/Br60f membership (`run.py:376-397`,
  `run.py:477-483`). Geometry fields remain exact row-to-row comparisons
  (`run.py:491-502`).
- **Required outputs are covered.** `selection_audit.json` was added to the
  contract and documentation. Real mode writes it before enforcing the frozen
  237-pair count, so an exit-7 mismatch leaves the diagnostic artifact behind
  (`run.py:986-998`). Successful real mode still writes the other required
  artifacts through the previously approved paths.
- **Manifest provenance is faithful.** Each selected volume's raw and
  normalized kernel values come from its own metadata row, rather than from a
  role-based constant (`run.py:557-568`).

## Silent-failure review

No blocking silent-failure surface was introduced. A count differing from 237
still stops before volume inference. Before that stop, the code writes the
top-ten raw kernel values with counts, normalized values and example volume
names, plus per-filter drop counts, to both the JSON audit and run log
(`run.py:437-455`, `run.py:468-507`, `run.py:535-550`, `run.py:986-998`). The
smoke test asserts the exact planted-decoy drop counts and verifies both the
list-form and plain-string paths (`run.py:715-764`).

The independent smoke run confirmed that `"['Br40f', '3']"` and
`"['Br60f', '3']"` select the intended pair, while slice-count and spacing
decoys are rejected. The generated audit reported five validation scans, two
missing-contrast drops, two geometry drops, and the expected per-column
mismatch counts.

## Claim discipline and readability

The summary language remains contract-correct: smoke mode cannot satisfy the
contract, and a real passing run authorizes only a request for a later bulk
contract. The new module and phase comments explain the exit-7 cause and the
normalization provenance. No test split, extra pair, threshold, margin, or
scientific reconstruction-sensitivity analysis was added.

## Non-blocking findings

1. **Reruns still overwrite an existing output directory.** `run_log.txt` is
   truncated and artifacts are rewritten in place (`run.py:1218-1219`). This
   was carried from the prior approved revision; use a fresh persistent output
   directory for each real attempt.
2. **Committed verification text understates current verification.** The
   bundled `verification.json` says the revised smoke run could not be
   executed in the coder's sandbox. This review independently executed it
   successfully, so that historical statement is no longer a project-level
   uncertainty and does not require a code change.

```json
{"verdict": "APPROVE", "blocking": [], "note": "The exit-7 repair faithfully normalizes list-form kernels, emits pre-failure selection diagnostics, records row-derived kernel provenance, and passes an independent smoke run without scope or cap drift."}
```


===== ideas/004/revision.md =====
# Revision of idea 004

## Revised question

Across geometry-matched alternative reconstructions of the same CT-RATE acquisition, how much do the frozen ClassFine abnormality scores change?

This revision implements the converged debate and the completed Stage 0 findings. It retains one experiment: compare a frozen model with itself across 425 strict, same-acquisition, geometry-matched reconstruction pairs. It does not retain the separate benchmark-precision study.

## Material changes

1. **Narrowed the question to paired score sensitivity.** The prior card joined reconstruction repeatability to a clustered benchmark audit. The latter needs labels, a separately defined weighting estimand, and additional inference. It is now excluded from the primary question. Reconstruction-swap rank summaries may be descriptive only.

2. **Renamed the study.** “Free test-retest” was removed because no acquisition was repeated. The study is now a within-acquisition reconstruction-sensitivity audit.

3. **Used the completed Stage 0 evidence.** The card now records 3,039 validation volumes, 1,564 scans, 1,304 patients, 1,432 multi-reconstruction scans, and 425 strict geometry-matched pairs. It also records the dominant contrast counts and the overwhelmingly Siemens composition. These replace the old inferred validation structure.

4. **Replaced the keystone.** Pair existence is no longer the load-bearing unknown; it was directly confirmed. The real keystone is whether the exact published ClassFine checkpoint is obtainable and provenance-verifiable. The inspected official locations contained inference code but no released per-volume scores or checkpoint assets. `keystone_status` is therefore `NOT_INSPECTED`, and feasibility and novelty confidence are capped at 3.

5. **Removed the label-only design-effect claim.** Duplicate labels and cluster sizes cannot determine AUROC variance or confidence-interval inflation. Stage 0 is treated only as the completed linkage and feasibility audit. No primary endpoint uses CT-RATE labels.

6. **Replaced ICC as the primary statistic.** A pooled ICC can conceal large borderline score changes and is ill-suited to heterogeneous reconstruction contrasts. The revised primary endpoints are paired score differences and an upper bound on absolute change, stratified by named reconstruction contrast and reported on probability and logit scales. Patient is the outer bootstrap unit.

7. **Removed unsupported thresholds and numerical reassurance criteria.** The old `ICC > 0.95` and “low-single-digit” flip criteria had no external justification. Threshold flips are no longer primary. A decisive equivalence result now requires an externally justified margin fixed before inspecting the paired scores.

8. **Removed the attenuation-bound argument.** Within-acquisition reconstruction agreement is not total measurement reliability and cannot impose a general ceiling on correlations with external outcomes. The cross-domain architecture built around classical test theory was deleted.

9. **Corrected the causal scope.** The primary cohort is restricted to pairs matched on array shape, spacing, slope/intercept, position, and acquisition parameters so the deterministic preprocessing function is held fixed. The permitted claim is sensitivity to reconstruction-dependent image content under the observed contrasts. The card does not claim that a specific kernel, anatomical feature, or frequency band caused the response.

10. **Made X explicit and independently measurable.** X is reconstruction-dependent spatial-frequency content, measurable from the images through frequency-energy or noise-power-spectrum statistics and the recorded kernel contrast without human annotation. The present experiment reaches rung 1 only; naming a more specific human-legible image property would require an independent measurement or intervention.

11. **Made vendor/site limits explicit.** Because 462 of 464 audited volumes were Siemens, scanner/vendor is not a within-pair explanation but is an unresolved effect modifier. No cross-vendor or broad site-general claim is allowed.

12. **Preserved a meaningful negative.** A powered confidence bound wholly inside a prespecified external margin would decisively weaken material reconstruction sensitivity for the observed contrasts and checkpoint. Mere non-significance remains sensitivity-limited and is not presented as reassurance.

13. **Added explicit stop and identity rules.** If the exact checkpoint cannot be obtained, the idea stops. Retraining or substituting another model would change the claim and must become a new candidate rather than a quiet repair.

14. **Reduced scores and priority.** Medical relevance and interest were moderated, feasibility and novelty were capped at 3, negative-result value was reduced from 5 to 4, and the weighted priority score changed from 4.10 to 3.55.

## What was deliberately removed

- test-retest terminology;
- label ICC and label-only design effects;
- pooled ICC as the headline endpoint;
- audit-pair-derived thresholds and flip-rate targets;
- benchmark confidence-interval correction as a co-primary arm;
- claims of concept validity, clinical actionability, or general reliability;
- the classical-test-theory attenuation ceiling;
- the assertion that an identical-file rerun rules out preprocessing;
- broad novelty claims about reconstruction sensitivity.

## Current gate

Before a feasibility memo or probe contract, inspect the actual checkpoint artifact, configuration, checksum, and license. The existence of code and clean image pairs is not a substitute for that asset.


===== STAGE TASK =====
<!-- stage: probe_review -->
# Probe code review

You are the adversarial reviewer of Stage 0 probe code written by the other
model family. In your context: the idea's `feasibility.md` (the goal), the
filled `probe_contract.yaml` (the preregistration), and the generated
`run.py` + `requirements.txt`. The human has approved the PLAN; your job is
to verify the CODE implements exactly that plan and nothing else.

Review against, in order of severity:
1. **Contract fidelity.** Does run.py measure the contract's primary_metric
   on the contract's dataset, respect maximum_variants / maximum_gpu_minutes
   / maximum_seeds and the stopping_rule, and write every required output
   (resolved_config.json, per_sample.csv, summary.json)?
2. **Silent-failure surfaces.** Missing-file handling, empty dataframes,
   NaN propagation, try/except blocks that swallow the very failure the
   probe exists to detect. A probe that prints a number on broken input is
   worse than one that crashes.
3. **Claim discipline.** No analysis beyond the contract; no test-set
   contact; deterministic seeds; results labeled with the contract's
   positive_pattern / negative_pattern language, never stronger.
4. **Readability.** The human runs this personally: module docstring
   explaining the experiment, narrated phase comments, thresholds annotated
   with provenance, progress printing, plain-English summary at the end.
   Blocking only when the code is genuinely opaque; otherwise list as
   non-blocking findings.
5. **Practicalities.** Will it actually run in Colab: paths, pip pins,
   Drive output dir taken from --output-dir, no interactive prompts.

Write `probe_review.md`: findings by severity with file/line references,
then exactly one fenced json block:

```json
{"verdict": "APPROVE|REVISE", "blocking": ["<finding>", "..."], "note": "<one line>"}
```

REVISE requires at least one blocking finding tied to a rule above. Do not
rewrite the code yourself; do not expand the experiment's scope.

