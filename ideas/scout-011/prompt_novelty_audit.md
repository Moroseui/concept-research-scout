You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-011
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


## 2026-08-12 - Probe 004 r5 environment dead end; r6 pivot to enumerated-key-tolerant load

The r5 pin (transformers 4.30.1 / tokenizers 0.13.3) is uninstallable on
Colab Python 3.12: tokenizers <0.14 ships no cp312 wheels and the Rust
source build fails (pip error captured 2026-08-12). Pinning backward to the
authors 2023 environment is not viable on current runtimes. Revision r6,
and ONLY this: (1) revert requirements.txt to the r4 closure that installed
cleanly twice (transformers 4.38.2 / tokenizers 0.15.2). (2) In run.py,
before load_state_dict, remove state-dict keys matching
*.embeddings.position_ids - the non-learnable arange buffer that
transformers 4.31 made non-persistent; this replicates from_pretrained
documented cross-era behavior. Strictness otherwise preserved: assert the
removed set is exactly one key matching that pattern, log the removed
key(s) to provenance.json and the run log, and any OTHER unexpected or
missing key still exits 5. (3) Startup logs the installed transformers
version. Exit-5 semantics update: a load is "unchanged" modulo enumerated,
provenance-logged framework-era buffer keys only.


## 2026-08-12 — Probe 004 contract v1 ADVANCE (load probe passed)

The authorized real A/B/A run satisfied every load-probe contract gate. The frozen
`CT_LiPro_v2.pt` artifact (SHA-256
`9246d9c8a7e2cedaa115719699229fe0acb02f19488e8bd1ad1eff5f47ff1d7d`)
loaded strictly under CT-CLIP commit `a2a155c601987820433c01db69b64d701d3d229d`,
modulo exactly the single r6-authorized and provenance-recorded
`trained_model.text_transformer.embeddings.position_ids` buffer key. The selected
Stage-0-valid Br40f|Br60f pair produced 18 finite named scores for A, B, and repeated
A; the A repeat was bit-identical. All three executions completed at batch size one
without patch-size changes in 0.250 GPU minutes with 4.10 GB peak memory, under the
45-minute cap. All authorized variants are reported in `ideas/004/decision.md`.

Scope: this demonstrates checkpoint/pipeline compatibility, output shape,
determinism, and bounded single-pair inference only. The one-pair A-versus-B score
differences are diagnostic and scientifically uninterpretable; they establish
nothing about reconstruction sensitivity, equivalence, accuracy, or concept
validity. No validity failure occurred. ADVANCE means only that a separate 425-pair
floor-study contract may now be drafted and submitted for fresh human approval; no
bulk inference is authorized by this decision.


===== evidence/ledger_digest.md =====
# Ledger digest (auto-generated -- do not edit; run `python scout.py ledger digest`)

61 tracked ideas. Latest state per idea; full history in ledger.jsonl.

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
- ... and 19 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- counterfactual-synthesis: 5
- regional-substitution: 5
- conditional-observational: 4
- representation-erasure: 3
- longitudinal-within-subject: 3
- natural-paired: 2
- model-output-perturbation: 2

## Ideas

- **idea-001** [REJECTED/DEBATED/baseline] -- Have lung nodule concept models been validated against radiologist opinion rather than against disease? -- killed: DATA_INSUFFICIENT -- data: {"primary": "LIDC-IDRI via The Cancer Imaging Archive", "license": "CC BY 3.0", 
- **idea-002** [PAUSED/DEBATED/baseline] -- Dermoscopic concepts predicted from non-dermoscopic photographs: genuine visibility or shortcut? -- data: {"primary": "Derm7pt paired clinical/dermoscopic images", "source": "github.com/
- **idea-003** [REJECTED/DEBATED/baseline] -- Does BI-RADS concept intervention survive realistic clinician behaviour, and does it beat simply reading the BI-RADS category? -- killed: DATA_ACCESS -- data: {"primary": "BUS-BRA (Zenodo 8231412, CC BY 4.0) for the external and baseline a
- **idea-004** [ACTIVE/PROBED/baseline] -- The free test-retest experiment already inside CT-RATE: duplicate reconstructions of the same acquisition
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
- **scout-011-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Name the bone phenotype hidden in a near-perfect hand-radiograph sex classifier
- **scout-011-c02** [SCOUT_ONLY/SCOUTED/baseline] -- Does Merlin read renal atrophy when it predicts future CKD?
- **scout-011-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Cephalization in 3D: decode CT-CLIP's pulmonary-edema score
- **scout-011-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The air bronchogram as a topological cue
- **scout-011-c05** [SCOUT_ONLY/SCOUTED/baseline] -- A pancreatic fat gauge inside Merlin's diabetes forecast


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


===== ideas/scout-011/README.md =====
# Scouting cycle 011

Tracks: baseline


===== ideas/scout-011/candidates_all.json =====
{
  "cycle": 11,
  "tracks": [
    "baseline"
  ],
  "notes": {
    "mode_c_score_missing": 2
  },
  "candidates": [
    {
      "id": "scout-011-c01",
      "parent_ids": [],
      "search_mode": "A",
      "entry_point": 1,
      "title": "Name the bone phenotype hidden in a near-perfect hand-radiograph sex classifier",
      "question": "Is the hand-radiograph sex classifier using second- and third-metacarpal cortical proportion and trabecular anisotropy, the measurable bone phenotype its heat maps left unnamed?",
      "rung": "Targets rung 1; a successful controlled regional perturbation plus acquisition checks reaches rung 2, while external biological validation of the measurements would support rung 3.",
      "deliverable_sentence": "The hand-radiograph sex classifier is using metacarpal cortical proportion and trabecular anisotropy.",
      "X_measurement": "Segment metacarpals 2 and 3 with a public hand-bone segmentation model; cortical proportion is cortical area divided by total cross-sectional bone area along a prespecified shaft interval, and trabecular anisotropy is the dominant-orientation coherence of the local structure tensor in the metacarpal base. Both are deterministic image measurements. Could I compute X on a new radiograph today without asking anyone? Yes in principle from a bone mask and pixels, but the exact segmentation model must pass Stage 0 on the target images.",
      "suspected_signal": "Sex hormones and sex-linked loading patterns alter cortical apposition and trabecular organization; these micro-geometric differences remain visible in projection even when radiologists cannot verbalize them.",
      "keystone_prerequisite": "The exact published sex classifier, or a faithfully reproducible classifier evaluated on an untouched cohort, must be obtainable; otherwise there is no fixed discovered signal to decode.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "The primary full text was inspected: Yune et al., Journal of Digital Imaging 2019, PMCID PMC6646498, PMID 30478479, DOI 10.1007/s10278-018-0148-x, reports 95.9% model accuracy versus 58% and 46% for two radiologists and localizes CAMs to metacarpal bases and wrist structures. I did not inspect a released checkpoint or a complete reproducible training-data manifest; therefore the load-bearing asset remains unverified.",
      "keystone_residual_assumption": "The nearest verified fact is the published performance and localization. I am still assuming the model can be obtained or faithfully reproduced without hidden institutional data and that a reproduced model recovers the same gap and attention pattern. That is load-bearing and is the real keystone.",
      "rung_reached": "Rung 1 only if X-selective perturbations alter the fixed model score beyond matched shams. Rung 2 requires cross-site, detector, age, and positioning replication; rung 3 requires showing that the two named measurements, rather than an edit signature, mediate the response.",
      "dies_like_prior": "Resembles idea-018 (DATA_ACCESS): a compelling model cannot be decoded if its asset is unobtainable. It is different only in having a reproducible architecture and a public pediatric hand-radiograph alternative; unless Stage 0 produces the same gap on a frozen external split, it should die the same way. Annotation provenance does not apply to X; sex labels are EHR phenotypes, not reader concepts.",
      "closest_prior_work": "Yune et al., Journal of Digital Imaging 2019, PMCID PMC6646498, PMID 30478479, DOI 10.1007/s10278-018-0148-x, is the unfinished story: it established the model-human gap and CAM locations but radiologists could not name the features. It did not quantify cortical proportion or trabecular anisotropy and did not intervene on them. No novelty is claimed beyond this exact delta pending a formal audit.",
      "existing_assets": "Primary paper with architecture, performance, human comparison, and localized regions; RSNA pediatric bone-age images are public under registration and include sex; deterministic cortical and structure-tensor measurements.",
      "smallest_decisive_experiment": "Stage 0 reproduces the sex AUC and metacarpal localization on a frozen split. On held-out images, make paired, measurement-targeted frequency/geometry edits confined to metacarpals 2-3 that change cortical proportion or trabecular orientation while preserving bone outline and global exposure; compare score deltas with equal-energy within-bone shams and irrelevant-metacarpal edits. A monotone, sham-exceeding response in both measurements supports rung 1.",
      "design_template": "counterfactual-synthesis",
      "use_vs_association": "Use is distinguished from association by changing X within the same radiograph while holding patient, label, acquisition, outline, and surrounding anatomy fixed, with equal-energy sham edits; observational correlation alone is not counted.",
      "standing_confounds_addressed": "Within-image edits fix site, detector, protocol, position, habitus, prevalence, referral, and label leakage. Cross-site replication addresses scanner/vendor. The unresolved confound is edit detectability or bone-age texture changed along with X; sham edits and age-stratified analysis reduce but do not eliminate it.",
      "alternative_explanations": [
        {
          "explanation": "The model detects edit artifacts",
          "excluded_by": "equal-energy within-bone shams and an image-realism discriminator; failure invalidates the experiment"
        },
        {
          "explanation": "Bone age, not sex-linked structure, drives both X and score",
          "excluded_by": "within-age strata and X edits that preserve global maturation landmarks"
        },
        {
          "explanation": "The model uses a different localized feature such as sesamoid presence",
          "excluded_by": "sesamoids are held fixed; a null remains decisive only for the two named Xs"
        }
      ],
      "anticipated_negative": "Decisive against these two Xs only if the fixed model reproduces the gap and the edit sensitivity/realism gates pass; otherwise sensitivity-limited.",
      "cross_domain": null,
      "remaining_legwork": "Two to four days for asset/reproduction audit; roughly one week for segmentation and edit-validity gates; first scientific decision in two weeks if Stage 0 passes.",
      "scores": {
        "clarity": {
          "value": 5,
          "reason": "Two precisely computed Xs and a fixed target model."
        },
        "identifiability": {
          "value": 4,
          "reason": "Paired selective edits plus shams isolate use, but edit realism remains a serious gate."
        },
        "medical_relevance": {
          "value": 3,
          "reason": "The result is more biological and fairness-relevant than directly clinical."
        },
        "interest": {
          "value": 5,
          "reason": "It could name a signal radiologists explicitly failed to see."
        },
        "prior_legwork": {
          "value": 4,
          "reason": "The gap and anatomical localization are already published."
        },
        "feasibility": {
          "value": 2,
          "reason": "Checkpoint/data reproducibility keystone is not inspected; score is capped."
        },
        "data_readiness": {
          "value": 2,
          "reason": "A substitute public cohort exists, but correspondence to the published model is unverified."
        },
        "evaluation_readiness": {
          "value": 3,
          "reason": "Paired deltas are clear; realistic selective bone edits require validation."
        },
        "negative_result_value": {
          "value": 4,
          "reason": "After validity gates, a null rules out the paper's most localized plausible measurements."
        },
        "novelty_confidence": {
          "value": 3,
          "reason": "Exact gap not found in the inspected paper; capped because systematic search is incomplete."
        },
        "regret": {
          "value": 5,
          "reason": "The source paper stopped almost exactly one measurement short."
        }
      },
      "priority_score": 3.5,
      "unverified_claims": [
        "Availability of the original checkpoint",
        "A public segmentation model reliable on the exact radiographs",
        "Novelty beyond the inspected primary paper"
      ],
      "track": "baseline"
    },
    {
      "id": "scout-011-c02",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "Does Merlin read renal atrophy when it predicts future CKD?",
      "question": "Is Merlin's five-year chronic-kidney-disease output using bilateral renal volume and surface irregularity as CT measures of renal atrophy?",
      "rung": "Targets rung 1. Within-patient change and cross-protocol replication can open rung 2; clinical calibration against kidney function would be required for rung 3 biology.",
      "deliverable_sentence": "Merlin is using renal atrophy—small, irregular kidneys—in its five-year chronic-kidney-disease output.",
      "X_measurement": "From TotalSegmentator kidney_left and kidney_right masks: bilateral volume normalized by body-surface proxy; surface-area-to-volume ratio; and boundary curvature dispersion after resampling to physical space. The official class table lists both kidneys, and the tool is citable (DOI 10.1148/ryai.230024). Could I compute X on a new scan today without asking anyone? Yes.",
      "suspected_signal": "Chronic nephron loss produces renal volume loss and cortical scarring, yielding smaller and more irregular kidneys. A report/EHR-supervised abdominal model may turn that established morphology into a future-CKD cue.",
      "keystone_prerequisite": "The released Merlin five-year head must expose an identifiable CKD logit and accept obtainable abdominal CTs with preprocessing faithful to the paper.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "Primary full text: Blankemeier et al., Nature 2026, PMID 41781626, PMCID PMC13082451, DOI 10.1038/s41586-026-10181-8, states that adapted tasks include six five-year diseases. The official StanfordMIMI/Merlin model release inspected in the prior cycle lists 'Five Year Disease Prediction' weights; the paper names chronic kidney disease among the six targets. This proves the head/release exists, not that it loads locally.",
      "keystone_residual_assumption": "Having verified the released task and CKD target, I am still assuming output ordering and preprocessing are sufficiently documented and the weights load. That is a practical Stage 0 gate but not a new inferential keystone. The remaining inferential assumption is that TotalSegmentator kidney boundaries remain stable across contrast phases; test-retest across same-patient phases is required before interpreting surface irregularity.",
      "rung_reached": "Rung 1 if score changes follow X within patients and survive organ-preserving dissociation analyses. Rung 2 needs phase/kernel/site replication. Rung 3 needs external renal-function linkage; the scout claim remains morphology-level.",
      "dies_like_prior": "Closest is idea-010 (CIRCULARITY), where cardiomegaly labels and measured heart size risked restating the same report concept. Different: the output is future CKD and X is automatically measured present morphology, not a report label re-encoding. USE_VS_ASSOCIATION remains live and is handled with longitudinal within-subject deltas; no human concepts are used.",
      "closest_prior_work": "Merlin (DOI 10.1038/s41586-026-10181-8) reports five-year CKD performance but not which renal morphology drives it. TotalSegmentator (DOI 10.1148/ryai.230024) supplies kidney masks but does not decode Merlin. Clinical renal-volume work establishes association, not model use; exact primary citations remain to be pinned.",
      "existing_assets": "Released Merlin weights/code; TotalSegmentator kidney masks; public TotalSegmentator and AMOS CT; deterministic shape metrics. A longitudinal cohort with dates and adequate repeated scans remains to be identified without relying on unconfirmed DUA data.",
      "smallest_decisive_experiment": "Stage 0 loads the CKD head and quantifies kidney-mask repeatability across phase/reconstruction duplicates. Main screen: compute within-patient changes in CKD score and renal volume/irregularity on repeated clinical CTs, conditioning on scan interval, phase, hydronephrosis proxy, cyst burden, and body size. Require directionally consistent deltas beyond the duplicate-scan noise floor. Follow with kidney-region substitution only if natural-change evidence passes.",
      "design_template": "longitudinal-within-subject",
      "use_vs_association": "Stable patient risk factors are fixed by within-patient changes; reconstruction/phase duplicates establish both model and X noise floors. This is stronger than cross-sectional correlation, though it establishes sensitivity to changing renal morphology rather than exclusive mediation.",
      "standing_confounds_addressed": "Within-patient analysis fixes site, sex, stable habitus, referral pathway, and most prevalence effects. Phase, protocol, reconstruction, positioning, and interval disease are measured/matched. Label leakage is absent from the primary readout. Unresolved: treatment and systemic illness may change both kidneys and model score.",
      "alternative_explanations": [
        {
          "explanation": "Contrast phase changes masks and model score",
          "excluded_by": "same-phase restriction and phase/reconstruction noise floors"
        },
        {
          "explanation": "Hydronephrosis or cysts alter volume without nephron mass",
          "excluded_by": "cyst masks, collecting-system dilation proxy, and separate smooth-volume analysis"
        },
        {
          "explanation": "The model reads vascular calcification or muscle loss as systemic disease",
          "excluded_by": "not fully; regional substitution is the rung-1 upgrade if observational screen passes"
        }
      ],
      "anticipated_negative": "Sensitivity-limited because true renal atrophy may change slowly relative to scan interval; equivalence margins must come from the duplicate noise floor and observed longitudinal range.",
      "cross_domain": null,
      "remaining_legwork": "One day to load/output-map; two days for mask repeatability; up to a week to verify an obtainable longitudinal cohort. First decision in one to two weeks.",
      "scores": {
        "clarity": {
          "value": 4,
          "reason": "Named morphology and metrics; two correlated components slightly broaden the claim."
        },
        "identifiability": {
          "value": 3,
          "reason": "Within-patient changes remove stable confounds, but systemic disease changes remain."
        },
        "medical_relevance": {
          "value": 4,
          "reason": "Explaining a five-year CKD signal affects biomarker credibility and incidental CT use."
        },
        "interest": {
          "value": 4,
          "reason": "A model deriving renal prognosis from visible atrophy is plausible and clinically legible."
        },
        "prior_legwork": {
          "value": 4,
          "reason": "Model and measurement tool are released."
        },
        "feasibility": {
          "value": 3,
          "reason": "Keystone inspected, but the longitudinal cohort is not yet verified."
        },
        "data_readiness": {
          "value": 2,
          "reason": "Cross-sectional data are public; repeat-scan data readiness is uncertain."
        },
        "evaluation_readiness": {
          "value": 4,
          "reason": "Shape metrics and paired deltas are standard."
        },
        "negative_result_value": {
          "value": 2,
          "reason": "A null is sensitivity-limited by slow morphology change."
        },
        "novelty_confidence": {
          "value": 3,
          "reason": "No exact decode found, but only limited primary-source search was completed."
        },
        "regret": {
          "value": 4,
          "reason": "A simple organ measurement may explain a high-profile prognostic head."
        }
      },
      "priority_score": 3.3,
      "unverified_claims": [
        "Obtainable repeated-scan cohort",
        "Local load/output ordering",
        "Kidney-mask stability across contrast phases",
        "Systematic novelty"
      ],
      "track": "baseline"
    },
    {
      "id": "scout-011-c03",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "Cephalization in 3D: decode CT-CLIP's pulmonary-edema score",
      "question": "Is CT-CLIP's pulmonary-edema score using cranial redistribution of pulmonary vessel volume, the CT analogue of cephalization?",
      "rung": "Targets rung 1; matched reconstruction and body-position checks address rung 2; clinical hemodynamic validation would move the already named concept to rung 3.",
      "deliverable_sentence": "CT-CLIP is using cranial redistribution of pulmonary vessel volume—cephalization—in its pulmonary-edema score.",
      "X_measurement": "Segment lung vasculature with TotalSegmentator's lung_vessels task or an open PARSE-derived model; compute vessel volume by caliber in upper versus lower thirds after registering to lung height. X is (upper-lung vessel volume / upper-lung volume) divided by the corresponding lower-lung value, stratified by caliber. PARSE challenge primary identifier arXiv:2304.03708; public release page states training and validation data were freely released in 2025. Could I compute X today without asking anyone? Yes with an existing model, conditional on noncontrast-domain validation.",
      "suspected_signal": "Elevated pulmonary venous pressure redistributes and recruits upper-lung vessels before or alongside interstitial/alveolar fluid. A 3D model may quantify this classical radiographic sign more consistently than readers do on CT.",
      "keystone_prerequisite": "The released CT-CLIP ClassFine checkpoint must have a distinct pulmonary-edema output and the vessel extractor must be usable on CT-RATE noncontrast CT.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "The released ClassFine 18-output checkpoint is proven runnable in decisions.md (2026-08-12), but I have not directly inspected the canonical 18-name artifact in this turn to confirm a pulmonary-edema head, nor tested lung_vessels on CT-RATE. PARSE's official page was inspected and describes automatic pulmonary-artery segmentation plus the 2025 free release. Because both exact-head identity and domain transfer are load-bearing, status remains NOT_INSPECTED.",
      "keystone_residual_assumption": "The nearest verified fact is that CT-CLIP has 18 named outputs and pulmonary vessel tools exist. I am still assuming the exact edema head exists and that a tool trained on contrast-enhanced pulmonary arteries measures total vessel-volume redistribution on noncontrast CT. That second assumption is not cosmetic; it is the real measurement keystone and must be tested against reconstruction pairs and an independent noncontrast method.",
      "rung_reached": "Rung 1 only after a within-scan regional substitution changes upper/lower vessel distribution while preserving total vessel volume and parenchyma, with realism gates. Rung 2 requires position/inspiration/reconstruction controls. Rung 3 uses the clinical name cephalization but still needs pressure validation.",
      "dies_like_prior": "Resembles idea-016 (IDENTIFIABILITY_FAILURE): a pressure-gauge cue could be entangled with acquisition. Different: no contrast reflux or injection timing is required, and the intervention preserves total vascular volume while redistributing it regionally. It also risks idea-006's OOD edit failure; this is addressed as a mandatory realism gate, not assumed away. Annotation provenance does not apply.",
      "closest_prior_work": "PARSE challenge, arXiv:2304.03708, establishes automatic pulmonary-artery segmentation, not model interpretation. CT-CLIP's primary work establishes the model outputs but does not test vessel redistribution. Classical cephalization literature motivates X; exact primary CT quantification citations remain unpinned. No novelty claim is made pending audit.",
      "existing_assets": "Verified CT-CLIP load pipeline and reconstruction pairs from idea-004; lung/lobe masks; TotalSegmentator lung_vessels task; PARSE public benchmark and labels.",
      "smallest_decisive_experiment": "Stage 0 confirms the head and establishes vessel-X repeatability on idea-004 reconstruction pairs. Screen score-X association within CT-RATE while conditioning on lung volume, effusion volume, heart size, position, and kernel. Only if it passes, perform paired regional vessel-preserving substitution between upper and lower thirds, holding total vessel voxels and parenchyma fixed; compare edema-score change against left-right and within-third shams.",
      "design_template": "regional-substitution",
      "use_vs_association": "The confirmatory estimand is the same scan before/after an X-selective upper-lower redistribution with total vascular burden fixed; association is only a screen and cannot establish use.",
      "standing_confounds_addressed": "Within-image intervention fixes scanner, vendor, protocol, reconstruction, site, positioning, habitus, prevalence, referral, and labels. Stage 0 separately quantifies kernel sensitivity. Not ruled out: synthetic junction artifacts and gravity-related parenchymal gradients; shams and parenchyma preservation address them incompletely.",
      "alternative_explanations": [
        {
          "explanation": "The model reads edema fluid, not vessels",
          "excluded_by": "parenchymal voxels are held fixed"
        },
        {
          "explanation": "It reads total vascular congestion",
          "excluded_by": "total vessel volume and caliber histogram are fixed"
        },
        {
          "explanation": "It responds to synthetic vascular discontinuities",
          "excluded_by": "junction-realism gate and position-matched sham substitutions; failure invalidates the result"
        }
      ],
      "anticipated_negative": "Decisive against cephalization use only if measurement repeatability, edit realism, and positive-control sensitivity pass; otherwise uninterpretable. Negative-result score is therefore conservative.",
      "cross_domain": null,
      "remaining_legwork": "Head-name and vessel-domain screen: two to three days; association screen: two days; valid substitution construction: one to two weeks. First kill/go decision within a week.",
      "scores": {
        "clarity": {
          "value": 5,
          "reason": "One named sign, one ratio, one model head."
        },
        "identifiability": {
          "value": 4,
          "reason": "Burden-preserving regional substitution isolates distribution if realism passes."
        },
        "medical_relevance": {
          "value": 4,
          "reason": "It would explain edema errors and expose a hemodynamic sign."
        },
        "interest": {
          "value": 5,
          "reason": "A classical 2D sign rediscovered quantitatively in 3D is compelling."
        },
        "prior_legwork": {
          "value": 4,
          "reason": "Inference and measurement assets exist."
        },
        "feasibility": {
          "value": 3,
          "reason": "Capped by uninspected dual keystone and demanding edit validity."
        },
        "data_readiness": {
          "value": 4,
          "reason": "CT-RATE and idea-004 infrastructure are available."
        },
        "evaluation_readiness": {
          "value": 3,
          "reason": "Paired score deltas are ready; vessel-edit realism needs custom gates."
        },
        "negative_result_value": {
          "value": 3,
          "reason": "Potentially decisive after stringent gates, otherwise invalid rather than negative."
        },
        "novelty_confidence": {
          "value": 3,
          "reason": "Capped; exact literature audit incomplete."
        },
        "regret": {
          "value": 5,
          "reason": "The named sign is obvious in hindsight once a vessel mask is available."
        }
      },
      "priority_score": 3.85,
      "unverified_claims": [
        "Exact pulmonary-edema head",
        "Noncontrast validity of lung-vessel segmentation",
        "Feasibility of realistic burden-preserving redistribution",
        "Systematic novelty"
      ],
      "track": "baseline"
    },
    {
      "id": "scout-011-c04",
      "parent_ids": [],
      "search_mode": "C",
      "entry_point": 2,
      "title": "The air bronchogram as a topological cue",
      "question": "Is CT-CLIP's consolidation score using the fraction of dense opacity traversed by patent airways—an automatically measured air-bronchogram burden?",
      "rung": "Targets rung 1; rung 2 requires protocol/kernel and edit-realism gates; rung 3 would require distinguishing consolidation etiologies rather than merely naming the sign.",
      "deliverable_sentence": "CT-CLIP is using air bronchograms—patent airways traversing dense lung opacity—in its consolidation score.",
      "X_measurement": "Automatic airway tree from an open 3D U-Net (Garcia-Uceda et al., Scientific Reports 2021, PMCID PMC8346579) intersected with an opacity mask defined within lung as locally connected voxels above a prespecified HU threshold. Air-bronchogram burden is patent airway centerline length inside opacity divided by opacity volume, with caliber strata. Could I compute X on a new CT today without asking anyone? Yes, using released airway segmentation plus a deterministic HU mask; validation on thick-slice CT-RATE is still required.",
      "suspected_signal": "Alveolar filling raises surrounding attenuation while conducting bronchi remain air-filled, producing a dark branching tree embedded in opacity. The model could learn this topology rather than generic whiteness.",
      "keystone_prerequisite": "The airway segmentation and opacity measurement must retain enough peripheral airway signal after CT-CLIP's resampling/cropping that X is measurable in the same tensor the model sees.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Primary airway-method full text inspected: Garcia-Uceda et al., Scientific Reports 2021, PMCID PMC8346579, describes fully automatic end-to-end 3D airway segmentation. The CT-CLIP pipeline is locally verified by idea-004. I did not inspect performance after CT-CLIP's exact resampling or on CT-RATE slice thicknesses; that same-tensor fact is the keystone.",
      "keystone_residual_assumption": "The easy fact is that high-resolution airway segmentation works. I am still assuming distal bronchi survive the model's lower-resolution input and that HU-defined opacity is meaningful after clipping/resampling. This is load-bearing; X must be computed both before and after preprocessing and meet a prespecified rank-stability threshold.",
      "rung_reached": "Rung 1 after airway-selective, opacity-preserving counterfactuals change the consolidation score beyond matched sham edits. Rung 2 needs robustness across kernels and slice thickness. Rung 3 needs an independently validated clinical sign definition.",
      "dies_like_prior": "Closest is idea-019's unresolved edit-validity problem and idea-006's OOD perturbation. Difference: the edit is sparse, intraparenchymal, intensity-matched to neighboring airway lumen, and has an explicit same-tensor positive control. It still dies like those ideas if the discriminator or sham gate fails. No annotation provenance is used.",
      "closest_prior_work": "Garcia-Uceda et al., PMCID PMC8346579, supplies automatic airway segmentation but does not measure air bronchograms or decode a VLM. Zheng et al., Medical Physics 2007, DOI 10.1118/1.2742777, quantified airways and documented reconstruction dependence, not model use. CT-CLIP has separate clinical heads but no published topology test found in this limited search.",
      "existing_assets": "CT-CLIP pipeline/checkpoint; CT-RATE; open airway models; deterministic HU opacity masks; reconstruction pairs for a measurement and score noise floor.",
      "smallest_decisive_experiment": "Stage 0 computes X on native and final tensors and requires rank correlation plus reconstruction repeatability. Select scans with equal opacity burden but divergent X. Confirmatory paired edit fills only airway-lumen voxels inside opacity with locally matched opacity texture, preserving total opacity boundary; converse positive control inserts anatomically connected air columns along an existing airway centerline. Equal-volume disconnected-air and boundary edits are shams.",
      "design_template": "counterfactual-synthesis",
      "use_vs_association": "Use is identified by changing connected patent-airway topology inside a fixed opacity while holding opacity burden, boundary, patient, and acquisition fixed; cross-sectional score-X association is exploratory only.",
      "standing_confounds_addressed": "Paired edits fix scanner/vendor/site/protocol/reconstruction/position/habitus/prevalence/referral/labels. Reconstruction sensitivity is measured on idea-004 pairs. Unresolved: edit texture and the possibility that connected air changes generic local contrast rather than the clinical topology.",
      "alternative_explanations": [
        {
          "explanation": "Generic black-white contrast drives the score",
          "excluded_by": "equal-volume disconnected-air shams"
        },
        {
          "explanation": "Opacity boundary shape drives it",
          "excluded_by": "boundary is fixed"
        },
        {
          "explanation": "The intervention is OOD",
          "excluded_by": "realism discriminator, reverse edit, and native-example retrieval; failure makes the result uninterpretable"
        }
      ],
      "anticipated_negative": "Sensitivity-limited if airway survival after preprocessing is marginal; decisive only after the positive-control insertion moves a known airway-sensitive auxiliary measurement while shams do not.",
      "cross_domain": "Borrowed construct: graph topology—connected paths through a dense domain rather than pixel count. It implies centerline length, branch count, and connectivity inside opacity, plus disconnected-air shams. If the analogy were dropped, one would measure only dark-voxel fraction and miss the decisive connectivity control; the experiment changes materially.",
      "remaining_legwork": "Same-tensor keystone and repeatability: three days; cohort screen: two days; edit validity: one to two weeks.",
      "scores": {
        "mechanism_clarity": {
          "value": 5,
          "reason": "Specific physical sign and explicit topology measurement."
        },
        "identifiability": {
          "value": 4,
          "reason": "Connected-versus-disconnected, burden-matched edits isolate topology if valid."
        },
        "interest": {
          "value": 4,
          "reason": "It asks whether a model learned a textbook sign in quantitative form."
        },
        "medical_relevance": {
          "value": 4,
          "reason": "Air bronchograms shape consolidation interpretation and differential diagnosis."
        },
        "clarity": {
          "value": 5,
          "reason": "Precise X, head, and counterfactual."
        },
        "feasibility_info_only": {
          "value": 3,
          "reason": "Same-tensor airway survival is uninspected and edit construction is nontrivial."
        },
        "novelty_confidence_info_only": {
          "value": 3,
          "reason": "Limited search only; no novelty claim."
        }
      },
      "priority_score": 4.4,
      "unverified_claims": [
        "Airway model weights/licence and CT-RATE performance",
        "Distal-airway survival after exact preprocessing",
        "Edit realism",
        "Exact novelty"
      ],
      "track": "baseline"
    },
    {
      "id": "scout-011-c05",
      "parent_ids": [],
      "search_mode": "C",
      "entry_point": 2,
      "title": "A pancreatic fat gauge inside Merlin's diabetes forecast",
      "question": "Is Merlin's five-year diabetes output using low pancreatic attenuation, an image-defined measure of fatty pancreatic replacement?",
      "rung": "Targets rung 1; rung 2 requires phase-matched and site-replicated attenuation calibration; rung 3 requires a validated fat measurement rather than attenuation alone.",
      "deliverable_sentence": "Merlin is using fatty replacement of the pancreas in its five-year diabetes output.",
      "X_measurement": "Use TotalSegmentator's pancreas mask (official class 7; DOI 10.1148/ryai.230024). X is median pancreatic HU normalized to splenic HU on matched slices, plus the fraction below a prespecified fat-like threshold, excluding ducts/vessels by erosion. Could I compute X on a new CT today without asking anyone? Yes; it is deterministic after automatic organ masks, but contrast phase limits biological interpretation.",
      "suspected_signal": "Adipocyte infiltration lowers pancreatic attenuation and may accompany beta-cell dysfunction and systemic ectopic-fat deposition. A model trained with longitudinal EHR outcomes could exploit this organ-specific depot before diabetes is coded.",
      "keystone_prerequisite": "There must be enough noncontrast or single-phase, pancreas-complete scans in an obtainable Merlin-compatible cohort to separate tissue attenuation from contrast timing.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Inspected adjacent facts: Merlin's primary paper (PMID 41781626; DOI 10.1038/s41586-026-10181-8) names diabetes among five-year prediction tasks, and TotalSegmentator's official class table includes pancreas and spleen. I did not inspect phase distribution or pancreas coverage in an obtainable compatible cohort; that is the real keystone.",
      "keystone_residual_assumption": "The easy verified fact is that both organs can be segmented. I am still assuming spleen normalization adequately removes phase and scanner effects and that enough scans share a phase. It may not: differential enhancement between pancreas and spleen is timing-dependent. Therefore the keystone is explicitly a single-phase cohort, not mere mask availability.",
      "rung_reached": "Rung 1 if pancreas-selective, phase-matched tissue substitution moves the diabetes score beyond liver-fat and generic attenuation controls. Rung 2 requires external site/scanner replication. Rung 3 requires chemical-shift MRI or validated CT fat calibration in a separate cohort.",
      "dies_like_prior": "Resembles idea-009 and idea-016 (IDENTIFIABILITY_FAILURE) because a quantitative cue can co-vary with protocol. Different only if the single-phase keystone passes and pancreas-specific effects survive liver and muscle controls. It also resembles scout-006-c03 (diabetes/liver fat) but is not a revival: the organ, measurement, and hypothesis differ; both should not advance together without a direct organ-dissociation design. Annotation provenance does not apply.",
      "closest_prior_work": "Merlin, DOI 10.1038/s41586-026-10181-8, predicts future diabetes but does not report a pancreatic-fat mechanism. TotalSegmentator supplies masks. Clinical studies link low pancreatic attenuation to diabetes, but primary identifiers and whether any decoded Merlin are not yet systematically audited; novelty remains unverified.",
      "existing_assets": "Merlin five-year weights; TotalSegmentator pancreas, spleen, liver, and muscle masks; public abdominal CT datasets; deterministic attenuation ratios.",
      "smallest_decisive_experiment": "Stage 0 inventories contrast phase and requires a sufficiently large single-phase subset plus pancreas/spleen mask stability. Screen partial association of diabetes score with pancreas:spleen attenuation conditional on BMI proxy, liver attenuation, muscle attenuation, age, and scanner. Confirmatory regional substitution swaps pancreas texture between tightly matched scans while preserving pancreas shape and global abdominal fat; liver-region and intensity-histogram shams are controls.",
      "design_template": "regional-substitution",
      "use_vs_association": "The confirmatory paired substitution changes pancreas texture while preserving patient-level/body-fat context and organ shape; conditioning alone is only exploratory. Liver-fat substitution tests whether the response is pancreas-specific or generic ectopic fat.",
      "standing_confounds_addressed": "Single-phase restriction and spleen ratio address protocol/contrast; within-site analyses address scanner/vendor; substitution fixes positioning, habitus, prevalence, referral, and labels. External site replication remains necessary. Label leakage is absent from the primary readout. Residual: texture transplantation artifacts and systemic fat correlation.",
      "alternative_explanations": [
        {
          "explanation": "Contrast timing lowers the ratio",
          "excluded_by": "single-phase restriction; if unavailable, candidate is killed"
        },
        {
          "explanation": "The model reads generic visceral or hepatic fat",
          "excluded_by": "matched body-fat context and liver-fat substitution control"
        },
        {
          "explanation": "The model responds to transplanted texture",
          "excluded_by": "histogram-matched liver/muscle shams and realism gate; failure invalidates inference"
        }
      ],
      "anticipated_negative": "Decisive against pancreas-specific use only after phase support and positive-control sensitivity pass; otherwise uninterpretable, so negative-result value is capped at 2.",
      "cross_domain": "Borrowed construct: ectopic-fat partitioning from metabolic physiology. It implies a pancreas-specific attenuation ratio and direct dissociation from hepatic, visceral, and muscle fat. Without the analogy the experiment would be a generic HU correlation; the organ-control matrix and prediction of pancreas specificity would disappear.",
      "remaining_legwork": "Phase inventory and model load: two days; masks and observational screen: three to five days; credible substitutions: one to two weeks. Candidate dies immediately if no single-phase cohort.",
      "scores": {
        "mechanism_clarity": {
          "value": 5,
          "reason": "Named tissue change, HU measurement, and organ-specific controls."
        },
        "identifiability": {
          "value": 3,
          "reason": "Organ substitution can isolate use, but phase and systemic adiposity are formidable."
        },
        "interest": {
          "value": 4,
          "reason": "A routine CT containing a latent metabolic forecast is compelling."
        },
        "medical_relevance": {
          "value": 4,
          "reason": "It could make an incidental pancreatic biomarker interpretable."
        },
        "clarity": {
          "value": 5,
          "reason": "One organ, one physical measurement, one output."
        },
        "feasibility_info_only": {
          "value": 2,
          "reason": "Single-phase data and valid transplantation are unverified."
        },
        "novelty_confidence_info_only": {
          "value": 2,
          "reason": "Pancreatic-fat/diabetes literature is active and formal audit is absent."
        }
      },
      "priority_score": 4.15,
      "unverified_claims": [
        "Single-phase obtainable Merlin-compatible cohort",
        "Pancreas-fat CT threshold validity",
        "Region-substitution realism",
        "Exact closest clinical primary papers",
        "Novelty"
      ],
      "track": "baseline"
    }
  ]
}


===== ideas/scout-011/run_provenance.json =====
{
  "timestamp": "2026-08-13T07:13:04+00:00",
  "git_commit": "ffef85fb85a98ccc5ef5d6183cf447d3c648b4dd",
  "claude_cli": "2.1.197 (Claude Code)",
  "codex_cli": "codex-cli 0.147.0",
  "tracks": [
    "baseline"
  ],
  "seed_concepts": null,
  "prompt_hashes": {
    "actioner.md": "263f5cce53cb0cee",
    "critique.md": "5c8ed5c43071eaeb",
    "debate_critic.md": "74f1e299e3c6db50",
    "debate_proposer.md": "6a41797dbc73796a",
    "debate_summary.md": "7243fe771e1f612d",
    "feasibility.md": "48f4f111abfcd1eb",
    "fiction_extract.md": "8ada1a395c25072e",
    "fiction_refine.md": "ab92bb6c46fe0fbb",
    "fiction_scout.md": "63b11687055c8624",
    "interpret.md": "ea213b1be9c3d178",
    "keystone_screen.md": "f6f206ca8577b47b",
    "librarian.md": "3c5c129fe98b1717",
    "novelty_audit.md": "eb2b70b4159ab881",
    "probe_code.md": "bc0c52c94d1af371",
    "probe_plan.md": "a10441cab1b3d8e0",
    "probe_review.md": "0b420d600b32812f",
    "revise.md": "db7fab4a10c7c32b",
    "scout.md": "c5ae0f349d7a6d67",
    "wide_scout.md": "b21b441dba189d08"
  },
  "agents_toml_hash": "7e80bd12c967c003"
}


===== ideas/scout-011/scout_candidates.json =====
{
  "cycle": "scout-011",
  "track": "baseline",
  "date": "2026-08-13",
  "all_questions": [
    "Q1: Is the hand-radiograph sex classifier using second- and third-metacarpal cortical proportion and trabecular anisotropy, the measurable bone phenotype its heat maps left unnamed?",
    "Q2: Is Merlin's five-year chronic-kidney-disease output using bilateral renal volume and surface irregularity as a CT measure of renal atrophy?",
    "Q3: Is CT-CLIP's pulmonary-edema score using cranial redistribution of pulmonary vessel volume, the CT analogue of cephalization?",
    "Q4: Is CT-CLIP's consolidation score using the fraction of opacity traversed by patent airways, an automatically measured air-bronchogram burden?",
    "Q5: Is Merlin's five-year diabetes output using low pancreatic attenuation, an image-defined measure of fatty pancreatic replacement?",
    "Q6: Is a head-CT age model using diploic-space expansion and skull-table thinning, the forensic-anthropology clock in the calvarium?",
    "Q7: Is a pulmonary-embolism model using the pulmonary-artery-to-aorta diameter ratio as a chronic right-heart-strain cue rather than embolus burden?",
    "Q8: Is a mammographic risk model using the orientation entropy of Cooper ligaments, like a material-failure map of breast stroma?",
    "Q9: Is a chest-radiograph sex classifier using clavicular curvature and rib-cage aspect ratio rather than breast shadow?",
    "Q10: Is an abdominal CT model using bowel-gas topology as a microbiome surrogate?"
  ],
  "dropped_questions": [
    {"question": "Q6 (calvarial forensic clock)", "reason": "Interesting and cross-domain, but I did not verify a runnable public head-CT age checkpoint; developing it would be model-free speculation."},
    {"question": "Q7 (PA:aorta ratio for PE)", "reason": "The ratio is a chronic-pressure correlate, but without natural embolus changes the design cannot separate use of it from severity association and risks repeating idea-016's identifiability failure."},
    {"question": "Q8 (Cooper-ligament orientation entropy)", "reason": "No independently validated automatic ligament extractor was found; X therefore fails the compute-it-today constraint."},
    {"question": "Q9 (CXR sex from thoracic geometry)", "reason": "Dropped to avoid developing two sex-decoding questions; Q1 has the stronger documented model-human gap and anatomically localized unfinished story."},
    {"question": "Q10 (bowel-gas topology as microbiome surrogate)", "reason": "The deliberately wrong-sounding question survives logical refutation but not measurement validity: CT gas topology is strongly preparation- and transit-dependent and is not an independently established microbiome measure."}
  ],
  "quota_note": "Exactly 1 Mode A, 2 Mode B, and 2 Mode C. All five are radiology and four are CT; no dataset is used more than twice. Zero revivals: no portfolio-brief unblock condition has a newly verified fact, so manufacturing a revival would violate the charter. Each developed design states how it distinguishes use from association. Mode C feasibility and novelty are reported outside their priority score.",
  "revivals": [],
  "candidates": [
    {
      "id": "scout-011-c01",
      "parent_ids": [],
      "search_mode": "A",
      "entry_point": 1,
      "title": "Name the bone phenotype hidden in a near-perfect hand-radiograph sex classifier",
      "question": "Is the hand-radiograph sex classifier using second- and third-metacarpal cortical proportion and trabecular anisotropy, the measurable bone phenotype its heat maps left unnamed?",
      "rung": "Targets rung 1; a successful controlled regional perturbation plus acquisition checks reaches rung 2, while external biological validation of the measurements would support rung 3.",
      "deliverable_sentence": "The hand-radiograph sex classifier is using metacarpal cortical proportion and trabecular anisotropy.",
      "X_measurement": "Segment metacarpals 2 and 3 with a public hand-bone segmentation model; cortical proportion is cortical area divided by total cross-sectional bone area along a prespecified shaft interval, and trabecular anisotropy is the dominant-orientation coherence of the local structure tensor in the metacarpal base. Both are deterministic image measurements. Could I compute X on a new radiograph today without asking anyone? Yes in principle from a bone mask and pixels, but the exact segmentation model must pass Stage 0 on the target images.",
      "suspected_signal": "Sex hormones and sex-linked loading patterns alter cortical apposition and trabecular organization; these micro-geometric differences remain visible in projection even when radiologists cannot verbalize them.",
      "keystone_prerequisite": "The exact published sex classifier, or a faithfully reproducible classifier evaluated on an untouched cohort, must be obtainable; otherwise there is no fixed discovered signal to decode.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "The primary full text was inspected: Yune et al., Journal of Digital Imaging 2019, PMCID PMC6646498, PMID 30478479, DOI 10.1007/s10278-018-0148-x, reports 95.9% model accuracy versus 58% and 46% for two radiologists and localizes CAMs to metacarpal bases and wrist structures. I did not inspect a released checkpoint or a complete reproducible training-data manifest; therefore the load-bearing asset remains unverified.",
      "keystone_residual_assumption": "The nearest verified fact is the published performance and localization. I am still assuming the model can be obtained or faithfully reproduced without hidden institutional data and that a reproduced model recovers the same gap and attention pattern. That is load-bearing and is the real keystone.",
      "rung_reached": "Rung 1 only if X-selective perturbations alter the fixed model score beyond matched shams. Rung 2 requires cross-site, detector, age, and positioning replication; rung 3 requires showing that the two named measurements, rather than an edit signature, mediate the response.",
      "dies_like_prior": "Resembles idea-018 (DATA_ACCESS): a compelling model cannot be decoded if its asset is unobtainable. It is different only in having a reproducible architecture and a public pediatric hand-radiograph alternative; unless Stage 0 produces the same gap on a frozen external split, it should die the same way. Annotation provenance does not apply to X; sex labels are EHR phenotypes, not reader concepts.",
      "closest_prior_work": "Yune et al., Journal of Digital Imaging 2019, PMCID PMC6646498, PMID 30478479, DOI 10.1007/s10278-018-0148-x, is the unfinished story: it established the model-human gap and CAM locations but radiologists could not name the features. It did not quantify cortical proportion or trabecular anisotropy and did not intervene on them. No novelty is claimed beyond this exact delta pending a formal audit.",
      "existing_assets": "Primary paper with architecture, performance, human comparison, and localized regions; RSNA pediatric bone-age images are public under registration and include sex; deterministic cortical and structure-tensor measurements.",
      "smallest_decisive_experiment": "Stage 0 reproduces the sex AUC and metacarpal localization on a frozen split. On held-out images, make paired, measurement-targeted frequency/geometry edits confined to metacarpals 2-3 that change cortical proportion or trabecular orientation while preserving bone outline and global exposure; compare score deltas with equal-energy within-bone shams and irrelevant-metacarpal edits. A monotone, sham-exceeding response in both measurements supports rung 1.",
      "design_template": "counterfactual-synthesis",
      "use_vs_association": "Use is distinguished from association by changing X within the same radiograph while holding patient, label, acquisition, outline, and surrounding anatomy fixed, with equal-energy sham edits; observational correlation alone is not counted.",
      "standing_confounds_addressed": "Within-image edits fix site, detector, protocol, position, habitus, prevalence, referral, and label leakage. Cross-site replication addresses scanner/vendor. The unresolved confound is edit detectability or bone-age texture changed along with X; sham edits and age-stratified analysis reduce but do not eliminate it.",
      "alternative_explanations": [
        {"explanation": "The model detects edit artifacts", "excluded_by": "equal-energy within-bone shams and an image-realism discriminator; failure invalidates the experiment"},
        {"explanation": "Bone age, not sex-linked structure, drives both X and score", "excluded_by": "within-age strata and X edits that preserve global maturation landmarks"},
        {"explanation": "The model uses a different localized feature such as sesamoid presence", "excluded_by": "sesamoids are held fixed; a null remains decisive only for the two named Xs"}
      ],
      "anticipated_negative": "Decisive against these two Xs only if the fixed model reproduces the gap and the edit sensitivity/realism gates pass; otherwise sensitivity-limited.",
      "cross_domain": null,
      "remaining_legwork": "Two to four days for asset/reproduction audit; roughly one week for segmentation and edit-validity gates; first scientific decision in two weeks if Stage 0 passes.",
      "scores": {
        "clarity": {"value": 5, "reason": "Two precisely computed Xs and a fixed target model."},
        "identifiability": {"value": 4, "reason": "Paired selective edits plus shams isolate use, but edit realism remains a serious gate."},
        "medical_relevance": {"value": 3, "reason": "The result is more biological and fairness-relevant than directly clinical."},
        "interest": {"value": 5, "reason": "It could name a signal radiologists explicitly failed to see."},
        "prior_legwork": {"value": 4, "reason": "The gap and anatomical localization are already published."},
        "feasibility": {"value": 2, "reason": "Checkpoint/data reproducibility keystone is not inspected; score is capped."},
        "data_readiness": {"value": 2, "reason": "A substitute public cohort exists, but correspondence to the published model is unverified."},
        "evaluation_readiness": {"value": 3, "reason": "Paired deltas are clear; realistic selective bone edits require validation."},
        "negative_result_value": {"value": 4, "reason": "After validity gates, a null rules out the paper's most localized plausible measurements."},
        "novelty_confidence": {"value": 3, "reason": "Exact gap not found in the inspected paper; capped because systematic search is incomplete."},
        "regret": {"value": 5, "reason": "The source paper stopped almost exactly one measurement short."}
      },
      "priority_score": 3.5,
      "unverified_claims": ["Availability of the original checkpoint", "A public segmentation model reliable on the exact radiographs", "Novelty beyond the inspected primary paper"]
    },
    {
      "id": "scout-011-c02",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "Does Merlin read renal atrophy when it predicts future CKD?",
      "question": "Is Merlin's five-year chronic-kidney-disease output using bilateral renal volume and surface irregularity as CT measures of renal atrophy?",
      "rung": "Targets rung 1. Within-patient change and cross-protocol replication can open rung 2; clinical calibration against kidney function would be required for rung 3 biology.",
      "deliverable_sentence": "Merlin is using renal atrophy—small, irregular kidneys—in its five-year chronic-kidney-disease output.",
      "X_measurement": "From TotalSegmentator kidney_left and kidney_right masks: bilateral volume normalized by body-surface proxy; surface-area-to-volume ratio; and boundary curvature dispersion after resampling to physical space. The official class table lists both kidneys, and the tool is citable (DOI 10.1148/ryai.230024). Could I compute X on a new scan today without asking anyone? Yes.",
      "suspected_signal": "Chronic nephron loss produces renal volume loss and cortical scarring, yielding smaller and more irregular kidneys. A report/EHR-supervised abdominal model may turn that established morphology into a future-CKD cue.",
      "keystone_prerequisite": "The released Merlin five-year head must expose an identifiable CKD logit and accept obtainable abdominal CTs with preprocessing faithful to the paper.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "Primary full text: Blankemeier et al., Nature 2026, PMID 41781626, PMCID PMC13082451, DOI 10.1038/s41586-026-10181-8, states that adapted tasks include six five-year diseases. The official StanfordMIMI/Merlin model release inspected in the prior cycle lists 'Five Year Disease Prediction' weights; the paper names chronic kidney disease among the six targets. This proves the head/release exists, not that it loads locally.",
      "keystone_residual_assumption": "Having verified the released task and CKD target, I am still assuming output ordering and preprocessing are sufficiently documented and the weights load. That is a practical Stage 0 gate but not a new inferential keystone. The remaining inferential assumption is that TotalSegmentator kidney boundaries remain stable across contrast phases; test-retest across same-patient phases is required before interpreting surface irregularity.",
      "rung_reached": "Rung 1 if score changes follow X within patients and survive organ-preserving dissociation analyses. Rung 2 needs phase/kernel/site replication. Rung 3 needs external renal-function linkage; the scout claim remains morphology-level.",
      "dies_like_prior": "Closest is idea-010 (CIRCULARITY), where cardiomegaly labels and measured heart size risked restating the same report concept. Different: the output is future CKD and X is automatically measured present morphology, not a report label re-encoding. USE_VS_ASSOCIATION remains live and is handled with longitudinal within-subject deltas; no human concepts are used.",
      "closest_prior_work": "Merlin (DOI 10.1038/s41586-026-10181-8) reports five-year CKD performance but not which renal morphology drives it. TotalSegmentator (DOI 10.1148/ryai.230024) supplies kidney masks but does not decode Merlin. Clinical renal-volume work establishes association, not model use; exact primary citations remain to be pinned.",
      "existing_assets": "Released Merlin weights/code; TotalSegmentator kidney masks; public TotalSegmentator and AMOS CT; deterministic shape metrics. A longitudinal cohort with dates and adequate repeated scans remains to be identified without relying on unconfirmed DUA data.",
      "smallest_decisive_experiment": "Stage 0 loads the CKD head and quantifies kidney-mask repeatability across phase/reconstruction duplicates. Main screen: compute within-patient changes in CKD score and renal volume/irregularity on repeated clinical CTs, conditioning on scan interval, phase, hydronephrosis proxy, cyst burden, and body size. Require directionally consistent deltas beyond the duplicate-scan noise floor. Follow with kidney-region substitution only if natural-change evidence passes.",
      "design_template": "longitudinal-within-subject",
      "use_vs_association": "Stable patient risk factors are fixed by within-patient changes; reconstruction/phase duplicates establish both model and X noise floors. This is stronger than cross-sectional correlation, though it establishes sensitivity to changing renal morphology rather than exclusive mediation.",
      "standing_confounds_addressed": "Within-patient analysis fixes site, sex, stable habitus, referral pathway, and most prevalence effects. Phase, protocol, reconstruction, positioning, and interval disease are measured/matched. Label leakage is absent from the primary readout. Unresolved: treatment and systemic illness may change both kidneys and model score.",
      "alternative_explanations": [
        {"explanation": "Contrast phase changes masks and model score", "excluded_by": "same-phase restriction and phase/reconstruction noise floors"},
        {"explanation": "Hydronephrosis or cysts alter volume without nephron mass", "excluded_by": "cyst masks, collecting-system dilation proxy, and separate smooth-volume analysis"},
        {"explanation": "The model reads vascular calcification or muscle loss as systemic disease", "excluded_by": "not fully; regional substitution is the rung-1 upgrade if observational screen passes"}
      ],
      "anticipated_negative": "Sensitivity-limited because true renal atrophy may change slowly relative to scan interval; equivalence margins must come from the duplicate noise floor and observed longitudinal range.",
      "cross_domain": null,
      "remaining_legwork": "One day to load/output-map; two days for mask repeatability; up to a week to verify an obtainable longitudinal cohort. First decision in one to two weeks.",
      "scores": {
        "clarity": {"value": 4, "reason": "Named morphology and metrics; two correlated components slightly broaden the claim."},
        "identifiability": {"value": 3, "reason": "Within-patient changes remove stable confounds, but systemic disease changes remain."},
        "medical_relevance": {"value": 4, "reason": "Explaining a five-year CKD signal affects biomarker credibility and incidental CT use."},
        "interest": {"value": 4, "reason": "A model deriving renal prognosis from visible atrophy is plausible and clinically legible."},
        "prior_legwork": {"value": 4, "reason": "Model and measurement tool are released."},
        "feasibility": {"value": 3, "reason": "Keystone inspected, but the longitudinal cohort is not yet verified."},
        "data_readiness": {"value": 2, "reason": "Cross-sectional data are public; repeat-scan data readiness is uncertain."},
        "evaluation_readiness": {"value": 4, "reason": "Shape metrics and paired deltas are standard."},
        "negative_result_value": {"value": 2, "reason": "A null is sensitivity-limited by slow morphology change."},
        "novelty_confidence": {"value": 3, "reason": "No exact decode found, but only limited primary-source search was completed."},
        "regret": {"value": 4, "reason": "A simple organ measurement may explain a high-profile prognostic head."}
      },
      "priority_score": 3.3,
      "unverified_claims": ["Obtainable repeated-scan cohort", "Local load/output ordering", "Kidney-mask stability across contrast phases", "Systematic novelty"]
    },
    {
      "id": "scout-011-c03",
      "parent_ids": [],
      "search_mode": "B",
      "entry_point": 2,
      "title": "Cephalization in 3D: decode CT-CLIP's pulmonary-edema score",
      "question": "Is CT-CLIP's pulmonary-edema score using cranial redistribution of pulmonary vessel volume, the CT analogue of cephalization?",
      "rung": "Targets rung 1; matched reconstruction and body-position checks address rung 2; clinical hemodynamic validation would move the already named concept to rung 3.",
      "deliverable_sentence": "CT-CLIP is using cranial redistribution of pulmonary vessel volume—cephalization—in its pulmonary-edema score.",
      "X_measurement": "Segment lung vasculature with TotalSegmentator's lung_vessels task or an open PARSE-derived model; compute vessel volume by caliber in upper versus lower thirds after registering to lung height. X is (upper-lung vessel volume / upper-lung volume) divided by the corresponding lower-lung value, stratified by caliber. PARSE challenge primary identifier arXiv:2304.03708; public release page states training and validation data were freely released in 2025. Could I compute X today without asking anyone? Yes with an existing model, conditional on noncontrast-domain validation.",
      "suspected_signal": "Elevated pulmonary venous pressure redistributes and recruits upper-lung vessels before or alongside interstitial/alveolar fluid. A 3D model may quantify this classical radiographic sign more consistently than readers do on CT.",
      "keystone_prerequisite": "The released CT-CLIP ClassFine checkpoint must have a distinct pulmonary-edema output and the vessel extractor must be usable on CT-RATE noncontrast CT.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "The released ClassFine 18-output checkpoint is proven runnable in decisions.md (2026-08-12), but I have not directly inspected the canonical 18-name artifact in this turn to confirm a pulmonary-edema head, nor tested lung_vessels on CT-RATE. PARSE's official page was inspected and describes automatic pulmonary-artery segmentation plus the 2025 free release. Because both exact-head identity and domain transfer are load-bearing, status remains NOT_INSPECTED.",
      "keystone_residual_assumption": "The nearest verified fact is that CT-CLIP has 18 named outputs and pulmonary vessel tools exist. I am still assuming the exact edema head exists and that a tool trained on contrast-enhanced pulmonary arteries measures total vessel-volume redistribution on noncontrast CT. That second assumption is not cosmetic; it is the real measurement keystone and must be tested against reconstruction pairs and an independent noncontrast method.",
      "rung_reached": "Rung 1 only after a within-scan regional substitution changes upper/lower vessel distribution while preserving total vessel volume and parenchyma, with realism gates. Rung 2 requires position/inspiration/reconstruction controls. Rung 3 uses the clinical name cephalization but still needs pressure validation.",
      "dies_like_prior": "Resembles idea-016 (IDENTIFIABILITY_FAILURE): a pressure-gauge cue could be entangled with acquisition. Different: no contrast reflux or injection timing is required, and the intervention preserves total vascular volume while redistributing it regionally. It also risks idea-006's OOD edit failure; this is addressed as a mandatory realism gate, not assumed away. Annotation provenance does not apply.",
      "closest_prior_work": "PARSE challenge, arXiv:2304.03708, establishes automatic pulmonary-artery segmentation, not model interpretation. CT-CLIP's primary work establishes the model outputs but does not test vessel redistribution. Classical cephalization literature motivates X; exact primary CT quantification citations remain unpinned. No novelty claim is made pending audit.",
      "existing_assets": "Verified CT-CLIP load pipeline and reconstruction pairs from idea-004; lung/lobe masks; TotalSegmentator lung_vessels task; PARSE public benchmark and labels.",
      "smallest_decisive_experiment": "Stage 0 confirms the head and establishes vessel-X repeatability on idea-004 reconstruction pairs. Screen score-X association within CT-RATE while conditioning on lung volume, effusion volume, heart size, position, and kernel. Only if it passes, perform paired regional vessel-preserving substitution between upper and lower thirds, holding total vessel voxels and parenchyma fixed; compare edema-score change against left-right and within-third shams.",
      "design_template": "regional-substitution",
      "use_vs_association": "The confirmatory estimand is the same scan before/after an X-selective upper-lower redistribution with total vascular burden fixed; association is only a screen and cannot establish use.",
      "standing_confounds_addressed": "Within-image intervention fixes scanner, vendor, protocol, reconstruction, site, positioning, habitus, prevalence, referral, and labels. Stage 0 separately quantifies kernel sensitivity. Not ruled out: synthetic junction artifacts and gravity-related parenchymal gradients; shams and parenchyma preservation address them incompletely.",
      "alternative_explanations": [
        {"explanation": "The model reads edema fluid, not vessels", "excluded_by": "parenchymal voxels are held fixed"},
        {"explanation": "It reads total vascular congestion", "excluded_by": "total vessel volume and caliber histogram are fixed"},
        {"explanation": "It responds to synthetic vascular discontinuities", "excluded_by": "junction-realism gate and position-matched sham substitutions; failure invalidates the result"}
      ],
      "anticipated_negative": "Decisive against cephalization use only if measurement repeatability, edit realism, and positive-control sensitivity pass; otherwise uninterpretable. Negative-result score is therefore conservative.",
      "cross_domain": null,
      "remaining_legwork": "Head-name and vessel-domain screen: two to three days; association screen: two days; valid substitution construction: one to two weeks. First kill/go decision within a week.",
      "scores": {
        "clarity": {"value": 5, "reason": "One named sign, one ratio, one model head."},
        "identifiability": {"value": 4, "reason": "Burden-preserving regional substitution isolates distribution if realism passes."},
        "medical_relevance": {"value": 4, "reason": "It would explain edema errors and expose a hemodynamic sign."},
        "interest": {"value": 5, "reason": "A classical 2D sign rediscovered quantitatively in 3D is compelling."},
        "prior_legwork": {"value": 4, "reason": "Inference and measurement assets exist."},
        "feasibility": {"value": 3, "reason": "Capped by uninspected dual keystone and demanding edit validity."},
        "data_readiness": {"value": 4, "reason": "CT-RATE and idea-004 infrastructure are available."},
        "evaluation_readiness": {"value": 3, "reason": "Paired score deltas are ready; vessel-edit realism needs custom gates."},
        "negative_result_value": {"value": 3, "reason": "Potentially decisive after stringent gates, otherwise invalid rather than negative."},
        "novelty_confidence": {"value": 3, "reason": "Capped; exact literature audit incomplete."},
        "regret": {"value": 5, "reason": "The named sign is obvious in hindsight once a vessel mask is available."}
      },
      "priority_score": 3.85,
      "unverified_claims": ["Exact pulmonary-edema head", "Noncontrast validity of lung-vessel segmentation", "Feasibility of realistic burden-preserving redistribution", "Systematic novelty"]
    },
    {
      "id": "scout-011-c04",
      "parent_ids": [],
      "search_mode": "C",
      "entry_point": 2,
      "title": "The air bronchogram as a topological cue",
      "question": "Is CT-CLIP's consolidation score using the fraction of dense opacity traversed by patent airways—an automatically measured air-bronchogram burden?",
      "rung": "Targets rung 1; rung 2 requires protocol/kernel and edit-realism gates; rung 3 would require distinguishing consolidation etiologies rather than merely naming the sign.",
      "deliverable_sentence": "CT-CLIP is using air bronchograms—patent airways traversing dense lung opacity—in its consolidation score.",
      "X_measurement": "Automatic airway tree from an open 3D U-Net (Garcia-Uceda et al., Scientific Reports 2021, PMCID PMC8346579) intersected with an opacity mask defined within lung as locally connected voxels above a prespecified HU threshold. Air-bronchogram burden is patent airway centerline length inside opacity divided by opacity volume, with caliber strata. Could I compute X on a new CT today without asking anyone? Yes, using released airway segmentation plus a deterministic HU mask; validation on thick-slice CT-RATE is still required.",
      "suspected_signal": "Alveolar filling raises surrounding attenuation while conducting bronchi remain air-filled, producing a dark branching tree embedded in opacity. The model could learn this topology rather than generic whiteness.",
      "keystone_prerequisite": "The airway segmentation and opacity measurement must retain enough peripheral airway signal after CT-CLIP's resampling/cropping that X is measurable in the same tensor the model sees.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Primary airway-method full text inspected: Garcia-Uceda et al., Scientific Reports 2021, PMCID PMC8346579, describes fully automatic end-to-end 3D airway segmentation. The CT-CLIP pipeline is locally verified by idea-004. I did not inspect performance after CT-CLIP's exact resampling or on CT-RATE slice thicknesses; that same-tensor fact is the keystone.",
      "keystone_residual_assumption": "The easy fact is that high-resolution airway segmentation works. I am still assuming distal bronchi survive the model's lower-resolution input and that HU-defined opacity is meaningful after clipping/resampling. This is load-bearing; X must be computed both before and after preprocessing and meet a prespecified rank-stability threshold.",
      "rung_reached": "Rung 1 after airway-selective, opacity-preserving counterfactuals change the consolidation score beyond matched sham edits. Rung 2 needs robustness across kernels and slice thickness. Rung 3 needs an independently validated clinical sign definition.",
      "dies_like_prior": "Closest is idea-019's unresolved edit-validity problem and idea-006's OOD perturbation. Difference: the edit is sparse, intraparenchymal, intensity-matched to neighboring airway lumen, and has an explicit same-tensor positive control. It still dies like those ideas if the discriminator or sham gate fails. No annotation provenance is used.",
      "closest_prior_work": "Garcia-Uceda et al., PMCID PMC8346579, supplies automatic airway segmentation but does not measure air bronchograms or decode a VLM. Zheng et al., Medical Physics 2007, DOI 10.1118/1.2742777, quantified airways and documented reconstruction dependence, not model use. CT-CLIP has separate clinical heads but no published topology test found in this limited search.",
      "existing_assets": "CT-CLIP pipeline/checkpoint; CT-RATE; open airway models; deterministic HU opacity masks; reconstruction pairs for a measurement and score noise floor.",
      "smallest_decisive_experiment": "Stage 0 computes X on native and final tensors and requires rank correlation plus reconstruction repeatability. Select scans with equal opacity burden but divergent X. Confirmatory paired edit fills only airway-lumen voxels inside opacity with locally matched opacity texture, preserving total opacity boundary; converse positive control inserts anatomically connected air columns along an existing airway centerline. Equal-volume disconnected-air and boundary edits are shams.",
      "design_template": "counterfactual-synthesis",
      "use_vs_association": "Use is identified by changing connected patent-airway topology inside a fixed opacity while holding opacity burden, boundary, patient, and acquisition fixed; cross-sectional score-X association is exploratory only.",
      "standing_confounds_addressed": "Paired edits fix scanner/vendor/site/protocol/reconstruction/position/habitus/prevalence/referral/labels. Reconstruction sensitivity is measured on idea-004 pairs. Unresolved: edit texture and the possibility that connected air changes generic local contrast rather than the clinical topology.",
      "alternative_explanations": [
        {"explanation": "Generic black-white contrast drives the score", "excluded_by": "equal-volume disconnected-air shams"},
        {"explanation": "Opacity boundary shape drives it", "excluded_by": "boundary is fixed"},
        {"explanation": "The intervention is OOD", "excluded_by": "realism discriminator, reverse edit, and native-example retrieval; failure makes the result uninterpretable"}
      ],
      "anticipated_negative": "Sensitivity-limited if airway survival after preprocessing is marginal; decisive only after the positive-control insertion moves a known airway-sensitive auxiliary measurement while shams do not.",
      "cross_domain": "Borrowed construct: graph topology—connected paths through a dense domain rather than pixel count. It implies centerline length, branch count, and connectivity inside opacity, plus disconnected-air shams. If the analogy were dropped, one would measure only dark-voxel fraction and miss the decisive connectivity control; the experiment changes materially.",
      "remaining_legwork": "Same-tensor keystone and repeatability: three days; cohort screen: two days; edit validity: one to two weeks.",
      "scores": {
        "mechanism_clarity": {"value": 5, "reason": "Specific physical sign and explicit topology measurement."},
        "identifiability": {"value": 4, "reason": "Connected-versus-disconnected, burden-matched edits isolate topology if valid."},
        "interest": {"value": 4, "reason": "It asks whether a model learned a textbook sign in quantitative form."},
        "medical_relevance": {"value": 4, "reason": "Air bronchograms shape consolidation interpretation and differential diagnosis."},
        "clarity": {"value": 5, "reason": "Precise X, head, and counterfactual."},
        "feasibility_info_only": {"value": 3, "reason": "Same-tensor airway survival is uninspected and edit construction is nontrivial."},
        "novelty_confidence_info_only": {"value": 3, "reason": "Limited search only; no novelty claim."}
      },
      "priority_score": 4.4,
      "unverified_claims": ["Airway model weights/licence and CT-RATE performance", "Distal-airway survival after exact preprocessing", "Edit realism", "Exact novelty"]
    },
    {
      "id": "scout-011-c05",
      "parent_ids": [],
      "search_mode": "C",
      "entry_point": 2,
      "title": "A pancreatic fat gauge inside Merlin's diabetes forecast",
      "question": "Is Merlin's five-year diabetes output using low pancreatic attenuation, an image-defined measure of fatty pancreatic replacement?",
      "rung": "Targets rung 1; rung 2 requires phase-matched and site-replicated attenuation calibration; rung 3 requires a validated fat measurement rather than attenuation alone.",
      "deliverable_sentence": "Merlin is using fatty replacement of the pancreas in its five-year diabetes output.",
      "X_measurement": "Use TotalSegmentator's pancreas mask (official class 7; DOI 10.1148/ryai.230024). X is median pancreatic HU normalized to splenic HU on matched slices, plus the fraction below a prespecified fat-like threshold, excluding ducts/vessels by erosion. Could I compute X on a new CT today without asking anyone? Yes; it is deterministic after automatic organ masks, but contrast phase limits biological interpretation.",
      "suspected_signal": "Adipocyte infiltration lowers pancreatic attenuation and may accompany beta-cell dysfunction and systemic ectopic-fat deposition. A model trained with longitudinal EHR outcomes could exploit this organ-specific depot before diabetes is coded.",
      "keystone_prerequisite": "There must be enough noncontrast or single-phase, pancreas-complete scans in an obtainable Merlin-compatible cohort to separate tissue attenuation from contrast timing.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "Inspected adjacent facts: Merlin's primary paper (PMID 41781626; DOI 10.1038/s41586-026-10181-8) names diabetes among five-year prediction tasks, and TotalSegmentator's official class table includes pancreas and spleen. I did not inspect phase distribution or pancreas coverage in an obtainable compatible cohort; that is the real keystone.",
      "keystone_residual_assumption": "The easy verified fact is that both organs can be segmented. I am still assuming spleen normalization adequately removes phase and scanner effects and that enough scans share a phase. It may not: differential enhancement between pancreas and spleen is timing-dependent. Therefore the keystone is explicitly a single-phase cohort, not mere mask availability.",
      "rung_reached": "Rung 1 if pancreas-selective, phase-matched tissue substitution moves the diabetes score beyond liver-fat and generic attenuation controls. Rung 2 requires external site/scanner replication. Rung 3 requires chemical-shift MRI or validated CT fat calibration in a separate cohort.",
      "dies_like_prior": "Resembles idea-009 and idea-016 (IDENTIFIABILITY_FAILURE) because a quantitative cue can co-vary with protocol. Different only if the single-phase keystone passes and pancreas-specific effects survive liver and muscle controls. It also resembles scout-006-c03 (diabetes/liver fat) but is not a revival: the organ, measurement, and hypothesis differ; both should not advance together without a direct organ-dissociation design. Annotation provenance does not apply.",
      "closest_prior_work": "Merlin, DOI 10.1038/s41586-026-10181-8, predicts future diabetes but does not report a pancreatic-fat mechanism. TotalSegmentator supplies masks. Clinical studies link low pancreatic attenuation to diabetes, but primary identifiers and whether any decoded Merlin are not yet systematically audited; novelty remains unverified.",
      "existing_assets": "Merlin five-year weights; TotalSegmentator pancreas, spleen, liver, and muscle masks; public abdominal CT datasets; deterministic attenuation ratios.",
      "smallest_decisive_experiment": "Stage 0 inventories contrast phase and requires a sufficiently large single-phase subset plus pancreas/spleen mask stability. Screen partial association of diabetes score with pancreas:spleen attenuation conditional on BMI proxy, liver attenuation, muscle attenuation, age, and scanner. Confirmatory regional substitution swaps pancreas texture between tightly matched scans while preserving pancreas shape and global abdominal fat; liver-region and intensity-histogram shams are controls.",
      "design_template": "regional-substitution",
      "use_vs_association": "The confirmatory paired substitution changes pancreas texture while preserving patient-level/body-fat context and organ shape; conditioning alone is only exploratory. Liver-fat substitution tests whether the response is pancreas-specific or generic ectopic fat.",
      "standing_confounds_addressed": "Single-phase restriction and spleen ratio address protocol/contrast; within-site analyses address scanner/vendor; substitution fixes positioning, habitus, prevalence, referral, and labels. External site replication remains necessary. Label leakage is absent from the primary readout. Residual: texture transplantation artifacts and systemic fat correlation.",
      "alternative_explanations": [
        {"explanation": "Contrast timing lowers the ratio", "excluded_by": "single-phase restriction; if unavailable, candidate is killed"},
        {"explanation": "The model reads generic visceral or hepatic fat", "excluded_by": "matched body-fat context and liver-fat substitution control"},
        {"explanation": "The model responds to transplanted texture", "excluded_by": "histogram-matched liver/muscle shams and realism gate; failure invalidates inference"}
      ],
      "anticipated_negative": "Decisive against pancreas-specific use only after phase support and positive-control sensitivity pass; otherwise uninterpretable, so negative-result value is capped at 2.",
      "cross_domain": "Borrowed construct: ectopic-fat partitioning from metabolic physiology. It implies a pancreas-specific attenuation ratio and direct dissociation from hepatic, visceral, and muscle fat. Without the analogy the experiment would be a generic HU correlation; the organ-control matrix and prediction of pancreas specificity would disappear.",
      "remaining_legwork": "Phase inventory and model load: two days; masks and observational screen: three to five days; credible substitutions: one to two weeks. Candidate dies immediately if no single-phase cohort.",
      "scores": {
        "mechanism_clarity": {"value": 5, "reason": "Named tissue change, HU measurement, and organ-specific controls."},
        "identifiability": {"value": 3, "reason": "Organ substitution can isolate use, but phase and systemic adiposity are formidable."},
        "interest": {"value": 4, "reason": "A routine CT containing a latent metabolic forecast is compelling."},
        "medical_relevance": {"value": 4, "reason": "It could make an incidental pancreatic biomarker interpretable."},
        "clarity": {"value": 5, "reason": "One organ, one physical measurement, one output."},
        "feasibility_info_only": {"value": 2, "reason": "Single-phase data and valid transplantation are unverified."},
        "novelty_confidence_info_only": {"value": 2, "reason": "Pancreatic-fat/diabetes literature is active and formal audit is absent."}
      },
      "priority_score": 4.15,
      "unverified_claims": ["Single-phase obtainable Merlin-compatible cohort", "Pancreas-fat CT threshold validity", "Region-substitution realism", "Exact closest clinical primary papers", "Novelty"]
    }
  ]
}


===== STAGE TASK =====
<!-- stage: novelty_audit -->
# Novelty audit

`candidates_all.json` (in your context) is this cycle's merged candidate pool
across all tracks. Audit every candidate's novelty claim by *searching*, not
recalling. A model asserting "this is novel" is worthless; the audit is the
verification path.

For each candidate, in order:

1. **Neighbors.** Search for the three closest prior works. Cite each with an
   identifier (DOI, arXiv ID, or exact title + venue + year) and one line on
   what it did. If after a genuine search you find fewer than three, list what
   you found and mark the candidate `NO_NEIGHBORS_FOUND` -- this is a flag for
   human verification, never evidence of novelty.
2. **Delta.** One sentence: precisely what this candidate does that the
   closest neighbor did not. "More data" or "a different dataset" is a weak
   delta; say so if it is one.
3. **Why not done.** Exactly one of:
   - `NEW_CAPABILITY` -- name the tool, dataset, or model that only recently
     made this testable;
   - `BLIND_SPOT` -- state the concrete reason the field missed it (framing,
     incentive, disciplinary boundary);
   - `TRIED_AND_FAILED` -- cite the attempt. Red flag: explain what would be
     different this time or recommend the kill.
4. **Verdict.** Calibrated vocabulary -- absence of a found duplicate is NOT
   verified novelty: `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` (thorough
   multi-source search, neighbors found and distinguished),
   `NO_DUPLICATE_FOUND_LIMITED_SEARCH` (search bounded or access-limited),
   `INCREMENTAL`, or `DUPLICATE_FOUND` (recommend kill with the citation).

Also write `novelty_manifest.json` -- the reproducibility record:
`{"searched_at": "...", "queries": [{"query": "...", "source": "..."}],
"neighbors": [{"candidate": "C1", "identifier": "...", "access":
"full_text|abstract|search_summary", "establishing_passage": "..."}]}`.

Write `novelty_audit.md` in the assigned output directory: one section per
candidate, headed by the candidate's title and track, containing exactly the
four items above. Close the file with a summary table: candidate / verdict /
why-not-done code. Number candidates by their position in
`candidates_all.json` as C1..Cn across ALL tracks -- do not renumber per
track (no W1/F1); the orchestrator maps the summary table back to the ledger
by these merged indices.

Do not write code. Do not modify any other file.

