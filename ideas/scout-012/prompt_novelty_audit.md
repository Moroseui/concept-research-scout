You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/scout-012
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

**Canonical shape (mandatory):** emit each score in the `scores` object as
`{"value": N, "why": "..."}` — the key is `value`, never `score`. Omit
`keystone_evidence` entirely when there is none; never emit `null` for it.
Cards violating the shape are rejected at merge.

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

66 tracked ideas. Latest state per idea; full history in ledger.jsonl.

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
- **scout-011-c02** [NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, score 3.3, audited 2026-08-13] -- Does Merlin read renal atrophy when it predicts future CKD?
- **scout-011-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.4, audited 2026-08-13] -- The air bronchogram as a topological cue
- **scout-010-c02** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.2, audited 2026-08-12] -- Atelectasis vs consolidation: has CT-CLIP learned the radiologist's volume-loss rule?
- **scout-006-c04** [NOVEL_UNVERIFIED, score 4.1, audited 2026-08-10] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-009-c08** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.1, audited 2026-08-11] -- The glioblastoma prognosticator may be reading the invasion front's roughness
- **scout-010-c04** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.0, audited 2026-08-12] -- The inferior vena cava as a manometer: does the chest model read venous pressure?
- **scout-009-c06** [NO_DUPLICATE_FOUND_LIMITED_SEARCH, score 4.0, audited 2026-08-11] -- The CT spirometer may be reading the diaphragm as a pressure-loaded membrane
- **scout-007-c06** [NOVEL_UNVERIFIED, score 3.9, audited 2026-08-10] -- The effusion model may be reading whether pleural fluid still obeys gravity
- ... and 24 more (python scout.py backlog)

## Design-template concentration (homogenization watch)

The research GRAMMAR, not the nouns. High concentration means the
portfolio explores one scientific move with rotating vocabulary.

- regional-substitution: 7
- conditional-observational: 6
- counterfactual-synthesis: 5
- representation-erasure: 3
- longitudinal-within-subject: 3
- natural-paired: 2
- model-output-perturbation: 2
- regional-removal: 1

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
- **scout-012-c01** [SCOUT_ONLY/SCOUTED/baseline] -- The race signal in chest CT: measure the bone density everyone names and nobody measured -- data: NLST (CDAS; same cohort the anchor paper trained on)
- **scout-012-c02** [SCOUT_ONLY/SCOUTED/baseline] -- The dilated esophagus inside the fibrosis score -- data: CT-RATE (validation split; local inference pipeline already frozen and probe-verified)
- **scout-012-c03** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin's COPD call may come from the lungs it wasn't asked to look at -- data: Public abdominal CT (AMOS 2022 / TotalSegmentator public dataset) + released Merlin checkpoint
- **scout-012-c04** [SCOUT_ONLY/SCOUTED/baseline] -- The non-gated chest CT contains an ECG: heart rate written in motion banding -- data: CT-RATE (second and final CT-RATE candidate this cycle); TCIA gated collections only for validating the X-measurement
- **scout-012-c05** [SCOUT_ONLY/SCOUTED/baseline] -- The prognosis model as a manometer: midline shift is pressure the skull wrote down -- data: Anchor model's cohort (single-institution + TRACK-TBI) - access is the declared rate-limiter; CQ500 (public, has MLS/mass-effect reads but no outcomes) for X-measurement development only


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


===== ideas/scout-012/README.md =====
# Scouting cycle 012

Tracks: baseline


===== ideas/scout-012/candidates_all.json =====
{
  "cycle": 12,
  "tracks": [
    "baseline"
  ],
  "notes": {
    "normalized": [
      "baseline: The race signal in chest CT: measure the bone dens -- scores.clarity: score->value, scores.identifiability: score->value, scores.medical_relevance: score->value, scores.interest: score->value, scores.prior_legwork: score->value, scores.feasibility: score->value, scores.data_readiness: score->value, scores.evaluation_readiness: score->value, scores.negative_result_value: score->value, scores.novelty_confidence: score->value, scores.regret: score->value",
      "baseline: The dilated esophagus inside the fibrosis score -- scores.clarity: score->value, scores.identifiability: score->value, scores.medical_relevance: score->value, scores.interest: score->value, scores.prior_legwork: score->value, scores.feasibility: score->value, scores.data_readiness: score->value, scores.evaluation_readiness: score->value, scores.negative_result_value: score->value, scores.novelty_confidence: score->value, scores.regret: score->value",
      "baseline: Merlin's COPD call may come from the lungs it wasn -- scores.clarity: score->value, scores.identifiability: score->value, scores.medical_relevance: score->value, scores.interest: score->value, scores.prior_legwork: score->value, scores.feasibility: score->value, scores.data_readiness: score->value, scores.evaluation_readiness: score->value, scores.negative_result_value: score->value, scores.novelty_confidence: score->value, scores.regret: score->value",
      "baseline: The non-gated chest CT contains an ECG: heart rate -- scores.mechanism_clarity: score->value, scores.identifiability: score->value, scores.interest: score->value, scores.medical_relevance: score->value, scores.clarity: score->value, scores.feasibility_informational: score->value, scores.novelty_confidence_informational: score->value, scores.negative_result_value_informational: score->value, keystone_evidence: null->absent",
      "baseline: The prognosis model as a manometer: midline shift  -- scores.mechanism_clarity: score->value, scores.identifiability: score->value, scores.interest: score->value, scores.medical_relevance: score->value, scores.clarity: score->value, scores.feasibility_informational: score->value, scores.novelty_confidence_informational: score->value, scores.negative_result_value_informational: score->value, keystone_evidence: null->absent"
    ],
    "mode_c_score_missing": 2
  },
  "candidates": [
    {
      "id": "scout-012-c01",
      "search_mode": "A",
      "entry_point": 1,
      "title": "The race signal in chest CT: measure the bone density everyone names and nobody measured",
      "question": "Does the chest-CT race classifier of Gichoya et al., trained on NLST, use vertebral trabecular attenuation - the opportunistic bone-density measure already validated in screening CT?",
      "design_template": "regional-substitution",
      "dataset": "NLST (CDAS; same cohort the anchor paper trained on)",
      "rung": "Targets rung 2 with a rung-3 sentence conditional on the substitution arm. Rung 1 is delivered by the substitution readout; rung 2 by site/scanner/habitus stratification available in NLST metadata; rung 3 (the sentence below) requires both plus a mediated-fraction estimate.",
      "deliverable_sentence": "The race classifier is using the trabecular bone mineral attenuation of the visible vertebrae.",
      "X_measurement": "Mean trabecular attenuation (HU) inside eroded vertebral-body masks from TotalSegmentator (Wasserthal et al. 2023, Radiology: AI, DOI 10.1148/ryai.230024; vertebrae are named classes), the standard opportunistic-osteoporosis measurement (Pickhardt et al. 2013, Ann Intern Med, DOI 10.7326/0003-4819-158-9-201305070-00003, L1 trabecular HU; thoracic-level variants validated in lung-screening LDCT). Computable today on a scan the model has never seen, with no human annotator: YES.",
      "suspected_signal": "Population-level BMD differences by self-reported race are among the largest documented imaging-visible anthropometric differences (NHANES DXA: higher mean femoral/lumbar BMD in Black adults). Trabecular attenuation is directly rendered in calibrated CT HU, is spatially diffuse (consistent with the signal surviving patch ablation in prior work), and survives resolution degradation (consistent with the low-frequency robustness the anchor paper reported).",
      "use_vs_association": "Association arm is explicitly labeled association; USE is carried by sham-controlled substitution: swap the trabecular interior between geometry-matched patients of discordant self-reported race, with same-race swaps as the sham floor - score movement above sham distinguishes use from correlation.",
      "keystone_prerequisite": "What the inference needs: (a) the demonstrated NLST chest-CT race signal is reproducible with slice-level models at single-GPU compute on scans where (b) vertebral trabecular HU is measurable, and (c) the anchor study genuinely left quantitative BMD unmeasured (the Mode A gap exists).",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "Component (c) and the CT anchor inspected in the full text (PMC9650160, 'AI recognition of patient race in medical imaging: a modelling study'): chest CT experiments used NLST with race-prediction AUC 0.92 (slice) / 0.96 (study), external validation on EM-CT and RSPECT; the only bone-related test was removal of brightest pixels on radiographs ('deep learning models effectively predicted patient race even when the bone density information was removed', AUC 0.960/0.945 on MIMIC-CXR/CheXpert) - bone mineral density was never quantitatively measured, and never tested on CT at all. Component (b): TotalSegmentator vertebral classes are documented in the cited paper/tool. Component (a) is NOT inspectable in advance and is listed as the residual assumption.",
      "keystone_residual_assumption": "Load-bearing residuals, stated per the three-strikes rule: (1) the NLST CDAS delivery links self-reported race to the imaging at the scan level (race was collected in NLST; the linkage in the delivered tables is inferred, not inspected); (2) a slice-level classifier at AUC >= 0.85 is reproducible within Colab-class compute (the anchor used slice-level training, which argues yes, but this is assumed until run); (3) within age-sex-site strata there remains enough trabecular-HU variance to test mediation. If (1) or (2) fails, the candidate is dead, not merely weakened.",
      "rung_reached": "1 by design (use of X via substitution); moves to 2 with site/scanner stratification and habitus conditioning; the mediated fraction determines whether the rung-3 sentence is 'is using' or 'is partly using'.",
      "dies_like_prior": "No annotation-provenance failure applies: self-reported race is subject-reported demographic data, independent of any image reader. Closest prior kill is idea-009 (IDENTIFIABILITY_FAILURE: index inseparable from covariates in any obtainable cohort); the difference is that identifiability here is not carried observationally but by within-pair trabecular substitution with a same-race sham floor, and NLST's uniform screening eligibility plus 33-site metadata gives real stratification support that idea-009 never had.",
      "closest_prior_work": "Gichoya et al. 2022, Lancet Digit Health 4:e406-14 (DOI 10.1016/S2589-7500(22)00063-2; preprint arXiv:2107.10356). They established the phenomenon across modalities including NLST chest CT and tested many candidate explanations - but their bone test was brightness clipping on uncalibrated radiographs, which removes cortical extremes, not the trabecular mean, and no bone test was performed on CT. Follow-up literature (e.g., frequency-domain and anatomical-region ablations) remains confound-elimination; I found no study regressing or intervening on quantitative CT BMD. That absence is a search result, not proof.",
      "existing_assets": "Anchor paper's public training code (Emory-HITI 'AI-vengers' repo - existence recalled, unverified); NLST already the working cohort of ideas 008/012/017 in this portfolio; TotalSegmentator off-the-shelf; opportunistic-BMD literature supplies validated thresholds and expected effect sizes.",
      "smallest_decisive_experiment": "On an NLST subset: (i) reproduce the slice-level race classifier (their recipe); (ii) compute trabecular HU per scan with TotalSegmentator; (iii) report fraction of race-score variance explained by trabecular HU within age-sex-site strata; (iv) in ~100 geometry-matched cross-race pairs, substitute vertebral trabecular interiors (same-race substitution as sham) and read the score shift. (iii) is association, labeled as such; (iv) is the use readout.",
      "standing_confounds_addressed": "Scanner/site: NLST race composition varies by site, so all observational readouts stratify by site and scanner model (metadata available); the paired substitution arm is within-pair immune. Protocol/reconstruction: stratify by kernel as in the anchor cohort. Habitus: condition on body cross-sectional area computed from the same scan. Prevalence/referral: screening trial with uniform eligibility - the strongest referral-pathway control available anywhere. Label leakage: no reports involved. NOT ruled out observationally: body-composition axes correlated with BMD (muscle attenuation, marrow fat) - measured and co-modeled, but only the substitution arm separates them.",
      "alternative_explanations": "(1) BMD is a marker, not the signal - the model reads correlated soft-tissue composition; substitution arm with trabecular-only edits addresses this, observational arm cannot. (2) Substitution edits are out-of-distribution and the score shift measures edit artifact - addressed by the same-race sham floor and a prespecified sham-effect tolerance (idea-008's lesson). (3) The anchor's own CXR bright-pixel result suggests bone is not the signal - acknowledged honestly; that experiment removed clipped cortical brightness on uncalibrated radiographs and is weak evidence about calibrated trabecular HU on CT, which is exactly why the direct measurement is the missing experiment.",
      "anticipated_negative": "Decisive, with an equivalence margin: if trabecular HU explains less than a prespecified fraction of stratified score variance AND substitution moves the score by less than the sham-derived margin, the most-cited candidate explanation for the field's most famous unexplained signal is dead on the modality where it is most measurable. That is a publishable type-1 negative.",
      "cross_domain": null,
      "remaining_legwork": "CDAS project scope/approval for race+images subset (weeks, administrative); classifier reproduction (~days of Colab); TotalSegmentator batch run (~days); substitution tooling reusing portfolio edit-validity machinery. First decision (observational arm): ~2-3 weeks after data in hand.",
      "scores": {
        "clarity": {
          "why": "One named X, one named model, one sentence; loses a point because 'the race signal' is a family of models, not one checkpoint.",
          "value": 4
        },
        "identifiability": {
          "why": "Observational arm is confounded by correlated body composition; the sham-controlled substitution arm carries identification but inherits edit-validity risk.",
          "value": 3
        },
        "medical_relevance": {
          "why": "Mechanism of the most-discussed algorithmic-bias vector in radiology; a positive names the shortcut vector deployed models carry.",
          "value": 4
        },
        "interest": {
          "why": "Four years of literature says 'nobody knows what the signal is'; this is the named-X experiment that literature keeps gesturing at.",
          "value": 5
        },
        "prior_legwork": {
          "why": "Anchor code public, cohort known, X-measurement tools validated; nothing needs inventing.",
          "value": 4
        },
        "feasibility": {
          "why": "Cap lifted by INSPECTED_TRUE but honestly 3: NLST delivery, classifier training, and edit machinery are each real work.",
          "value": 3
        },
        "data_readiness": {
          "why": "NLST via CDAS: obtainable with administrative latency, precedented in this portfolio, not in hand.",
          "value": 3
        },
        "evaluation_readiness": {
          "why": "AUC for reproduction, variance-explained and paired score-shift with sham floor are all standard.",
          "value": 4
        },
        "negative_result_value": {
          "why": "Type-1 decisive against the field's most-cited hypothesis, with margins.",
          "value": 5
        },
        "novelty_confidence": {
          "why": "The gap is verified inside the anchor paper, but the follow-up literature is large and my search for a quantitative-BMD test was not exhaustive.",
          "value": 3
        },
        "regret": {
          "why": "If someone else runs this first it will look obvious in hindsight.",
          "value": 5
        }
      },
      "priority_score": 3.8,
      "unverified_claims": [
        "NHANES-scale BMD differences by self-reported race (direction and rough magnitude from memory; needs primary citation).",
        "Public availability and completeness of the Emory-HITI training code (from memory).",
        "NLST CDAS delivery links self-reported race to scans (inferred from trial design; data dictionary not inspected).",
        "Thoracic-level opportunistic BMD validation in LDCT (literature recalled, specific citation needed)."
      ],
      "track": "baseline"
    },
    {
      "id": "scout-012-c02",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The dilated esophagus inside the fibrosis score",
      "question": "Does CT-CLIP's pulmonary-fibrotic-sequela score use the air-filled dilated esophagus - the connective-tissue-disease clue radiologists read alongside the lungs?",
      "design_template": "regional-substitution",
      "dataset": "CT-RATE (validation split; local inference pipeline already frozen and probe-verified)",
      "entry_point_2_requirements": "Measurement that would detect the unexpected signal: partial association of the fibrosis score with esophageal air volume conditional on a lung-only quantitative fibrosis surrogate, then digital esophageal collapse with sham. Artifact it would be confused with: contrastive label binding from reports that co-mention esophageal dilation (a training-provenance fact that does not change the image-use claim, but changes its interpretation), and positioning/aerophagia correlates.",
      "rung": "Targets rung 1 (use), with rung 2 within reach because the decisive readout is within-scan paired and label-free; rung 3 sentence below is the honest endpoint if the substitution arm is positive and sham-clean.",
      "deliverable_sentence": "The model's fibrosis score is using the air-filled, dilated esophagus.",
      "X_measurement": "Esophageal air volume and maximal luminal diameter: TotalSegmentator 'esophagus' class (Wasserthal et al. 2023, DOI 10.1148/ryai.230024), air = voxels < -500 HU within the (slightly dilated) mask; diameter from per-slice mask geometry. Computable today without an annotator: YES.",
      "suspected_signal": "Esophageal dysmotility in systemic sclerosis and other CTD-ILD produces a patulous, air-filled esophagus; a visibly dilated esophagus on chest CT is a standard clue toward CTD-ILD in fibrosis workup. A contrastive model trained on image-report pairs would be rewarded for binding this extra-pulmonary cue to fibrosis language.",
      "use_vs_association": "Primary conditional association is labeled association; USE is carried by a within-scan intervention - digitally collapsing the esophagus (replace luminal air with adjacent mediastinal soft-tissue HU) against a sham edit of matched voxel count elsewhere, reading the paired fibrosis-score change.",
      "keystone_prerequisite": "What the inference needs: a locally computable per-volume 'Pulmonary fibrotic sequela' score from the released CT-CLIP checkpoint on CT-RATE volumes.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "probes/004/run.py:150 lists \"Pulmonary fibrotic sequela\" in EXPECTED_PATHOLOGIES (18 heads), and the 2026-08-12 ledger decision records the load probe producing '18 finite named scores' bit-deterministically from the frozen CT_LiPro_v2.pt checkpoint (SHA-256 9246d9c8...) under the pinned pipeline. The scoring machinery for this exact head is verified working on this machine's lineage.",
      "keystone_residual_assumption": "Still assumed, load-bearing for power rather than possibility: (1) CT-RATE fibrosis-positive volumes contain enough variance in esophageal air (prevalence of visible dilation is unknown until counted - Stage 0 gate with a prespecified minimum); (2) TotalSegmentator's esophagus class performs adequately on CT-RATE's resampled geometry (spot-check gate); (3) the collapse edit can pass a sham-effect tolerance (idea-008's edit-validity lesson, prespecified before any score is read).",
      "rung_reached": "1 if substitution is positive and sham-clean; 2 requires the confound work below (much of it comes free from the paired design); 3 is the deliverable sentence itself, which is already stated in words a chest radiologist uses.",
      "dies_like_prior": "Not annotation-provenance: the primary readout is the model against its own edited input - no label enters the primary measurement (the structural move the charter says has saved the one surviving candidate). Not idea-010 circularity: the esophagus is not part of the fibrosis label's definition. The live inherited risk is idea-008's edit-validity objection - addressed by prespecified sham tolerance, not assumed away.",
      "closest_prior_work": "CT-CLIP/CT-RATE (Hamamci et al., arXiv:2403.17834) provides model and labels but no per-concept decoding of the fibrosis head. Radiology literature documents esophageal dilation as a CTD-ILD marker (primary citation to be pinned in feasibility; currently from memory). I found no work probing any chest-CT foundation model for extra-pulmonary reliance of a fibrosis output; not exhaustively searched.",
      "existing_assets": "Frozen CT-CLIP checkpoint + pinned environment + validated metadata/selection machinery from probe 004 (the portfolio's most de-risked pipeline); TotalSegmentator; CT-RATE validation volumes enumerable locally.",
      "smallest_decisive_experiment": "Stage 0: count fibrosis-positive validation volumes with measurable esophageal air (gate). Then: (i) fibrosis score vs esophageal air conditional on %high-attenuation-area of the lungs (an automated lung-only fibrosis surrogate) and lung volume; (ii) in the top-decile dilated-esophagus volumes, collapse the esophagus digitally, sham edit control, read paired score change on ~100 volumes (~0.25 GPU-min/volume per probe 004 timing).",
      "standing_confounds_addressed": "Scanner/protocol/reconstruction/site: within-scan paired edits are immune; observational arm stratifies by kernel using the frozen metadata pipeline. Positioning/habitus: unchanged within pair; conditioned in the observational arm. Prevalence/referral: single-center CT-RATE limits external generalization, not internal validity - stated as scope limit. Label leakage: labels never enter the primary readout; report co-mention explains mechanism of acquisition, not the image-use claim.",
      "alternative_explanations": "(1) Score shift measures edit artifact, not esophagus use - sham floor with prespecified tolerance addresses; if sham fails tolerance the candidate stops rather than reinterprets. (2) The model reads adjacent mediastinal changes the edit disturbs (hiatal hernia head shares anatomy) - check cross-head specificity: the esophageal collapse should move the fibrosis head more than unrelated heads. (3) Esophageal air proxies supine dwell time/aerophagia correlated with sicker patients - the conditional arm cannot fully exclude this; the substitution arm can, because the claim is about the image cue, whatever its upstream cause.",
      "anticipated_negative": "Decisive for the named X given gates pass: no conditional association AND no paired score response beyond sham tolerance in adequately dilated cases kills the hypothesis. If the Stage 0 prevalence gate fails, the result is 'not testable in this cohort', declared as such, not a negative.",
      "cross_domain": null,
      "remaining_legwork": "Stage 0 prevalence count + esophagus segmentation spot-check (~2-3 days); edit implementation with sham calibration (~1 week); scoring runs are cheap on the existing pipeline. First decision: ~2 weeks.",
      "scores": {
        "clarity": {
          "why": "One head, one named organ, one intervention, one sentence.",
          "value": 5
        },
        "identifiability": {
          "why": "Within-scan paired edit with sham floor and cross-head specificity check; residual edit-validity risk keeps it from 5.",
          "value": 4
        },
        "medical_relevance": {
          "why": "If fibrosis scores lean on the esophagus they inherit CTD-ILD case-mix bias and mislead in non-CTD fibrosis - directly deployment-relevant.",
          "value": 4
        },
        "interest": {
          "why": "An extra-pulmonary organ inside a pulmonary score is the kind of finding a radiologist immediately understands and did not expect a probe to establish.",
          "value": 4
        },
        "prior_legwork": {
          "why": "Rides the only probe-verified pipeline in the portfolio; every tool named is in hand or off-the-shelf.",
          "value": 5
        },
        "feasibility": {
          "why": "INSPECTED_TRUE; scoring machinery verified; the only real work is the edit and the gates.",
          "value": 4
        },
        "data_readiness": {
          "why": "CT-RATE validation split enumerated and frozen locally.",
          "value": 5
        },
        "evaluation_readiness": {
          "why": "Paired score deltas with sham margins follow the accepted idea-004 readout pattern.",
          "value": 4
        },
        "negative_result_value": {
          "why": "Decisive against the named X conditional on the prevalence and sham gates.",
          "value": 4
        },
        "novelty_confidence": {
          "why": "No probe of CT-CLIP extra-pulmonary reliance found, but search was limited; capped by honesty, not by rule.",
          "value": 3
        },
        "regret": {
          "why": "Cheap, fast, and the positive is a memorable sentence.",
          "value": 4
        }
      },
      "priority_score": 4.1,
      "unverified_claims": [
        "Esophageal dilation as a CTD-ILD clue: standard radiology teaching, but the primary citation is from memory and must be pinned.",
        "Prevalence of visible esophageal air/dilation in CT-RATE fibrosis positives: unknown until Stage 0.",
        "TotalSegmentator esophagus-class accuracy on CT-RATE resampled volumes: assumed pending spot-check."
      ],
      "track": "baseline"
    },
    {
      "id": "scout-012-c03",
      "search_mode": "B",
      "entry_point": 2,
      "title": "Merlin's COPD call may come from the lungs it wasn't asked to look at",
      "question": "Does Merlin use the emphysema visible in the lung bases captured at the top of an abdominal CT when it scores the chronic-airway-obstruction phenotype?",
      "design_template": "regional-removal",
      "dataset": "Public abdominal CT (AMOS 2022 / TotalSegmentator public dataset) + released Merlin checkpoint",
      "entry_point_2_requirements": "Measurement that would detect the unexpected signal: %LAA-950 within the imaged basal lung, and the dose-response of the phenotype score to natural-range superior truncation. Artifact it would be confused with: scan superior extent itself covaries with protocol and habitus (longer coverage on some indications), so score-versus-extent must be separated from score-versus-removed-emphysema; the paired within-scan design plus regressing score change on removed-slab content does that separation explicitly.",
      "rung": "Targets rung 1-2 in one design: the primary readout is label-free and within-scan (rung 1 use), and the natural-variation framing plus content regression does most rung-2 work structurally.",
      "deliverable_sentence": "The model is using emphysematous destruction of the lung bases imaged at the top of the scan.",
      "X_measurement": "%LAA-950: percentage of imaged lung voxels below -950 HU within TotalSegmentator lung masks restricted to the field of view - the standard quantitative emphysema index (Gevenois et al. 1996, Am J Respir Crit Care Med, DOI 10.1164/ajrccm.154.1.8680679). Computable today without an annotator: YES.",
      "suspected_signal": "Emphysema is visible at the lung bases; standard abdominal protocols begin above the diaphragm, so several centimeters of lung enter every abdominal CT; Merlin's phecode supervision (496, chronic airway obstruction) pairs those voxels with COPD outcomes at training time. The model has both the cue and the incentive.",
      "use_vs_association": "USE is read directly: progressively truncate the superior slab within the naturally occurring range of scan starts and regress the paired score change on the emphysema content of the removed slab (vs its total volume, cardiac volume, and atelectasis content) - an input intervention, not a correlation.",
      "keystone_prerequisite": "What the inference needs: the released Merlin checkpoint exposes a per-scan phenotype head that includes a COPD-family phenotype.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "GitHub StanfordMIMI/Merlin README documents initialization modes including Merlin(PhenotypeCls=True) (phenotype classification head released, MIT license, pip 'merlin-vlm', HF stanfordmimi/Merlin); documentation/phenotypes.csv in the same repo contains rows '496,Chronic airway obstruction' and '496.1,Emphysema' (also 496.2 chronic bronchitis, 496.3 bronchiectasis). Both fetched and read 2026-08-14.",
      "keystone_residual_assumption": "Still assumed, and stated as the real remaining keystones: (1) the phenotype head's output index mapping to phenotypes.csv rows is documented or recoverable from the released code (inferred from repo structure, not yet traced); (2) Merlin's preprocessing handles variable superior extent through the same deterministic path, so truncated volumes are in-distribution - this is exactly the idea-006 lesson, and Stage 0 must inspect Merlin's released dataloader the way the idea-006 unblock check inspected CT-CLIP's, plus quantify the empirical distribution of scan starts in the public cohort and stay inside it; (3) AMOS/TotalSegmentator-dataset scans actually include lung bases at useful frequency (anatomically near-certain for standard protocols, uncounted).",
      "rung_reached": "1 on a positive dose-response attributable to removed emphysema; 2 largely structural (within-scan pairing kills scanner/site/positioning; content regression separates emphysema from generic slab removal); 3 is the deliverable sentence, already in physician vocabulary.",
      "dies_like_prior": "Closest prior kill is idea-006 (PAUSED: patient-deletion was an extreme OOD intervention). The difference is explicit and testable: superior truncation reproduces a natural axis of acquisition variation present in Merlin's training distribution (scan coverage varies patient to patient), the truncation range is confined to the empirically observed range of scan starts, and the in-distribution claim is gated on dataloader inspection BEFORE any inference - the exact procedure that idea-006 learned the hard way. No annotation-provenance dependence: primary readout is label-free.",
      "closest_prior_work": "Merlin (Blankemeier et al., arXiv:2406.06512): reports phenotype AUROCs, including respiratory phecodes, but no attribution of any phenotype to specific anatomy. The opportunistic-screening literature runs the reverse direction (measure lung bases, predict COPD) and never asks what a trained foundation model actually uses. Backlog Merlin candidates (spleen, renal atrophy, pancreatic fat, osteoporosis) target abdominal organs; none touches the imaged thorax spillover.",
      "existing_assets": "Merlin: MIT-licensed weights, pip package, demo inference scripts (all public); AMOS 2022 and TotalSegmentator dataset public; TotalSegmentator for lung masks and %LAA; no labels required for the primary readout.",
      "smallest_decisive_experiment": "Stage 0: inspect Merlin loader for z-extent handling; measure the natural distribution of superior scan starts and basal-lung inclusion in the public cohort. Then on ~200 public abdominal CTs spanning basal %LAA: score each scan at 3-4 nested natural-range superior extents; regress paired chronic-airway-obstruction score change on removed-slab %LAA vs removed-slab lung volume, cardiac volume, and atelectasis content.",
      "standing_confounds_addressed": "Scanner/vendor/protocol/site/positioning: within-scan paired truncation is immune to all of them. Habitus: unchanged within scan; conditioned across scans. Prevalence/referral: no outcome labels in the primary readout, so case-mix cannot leak into it; cross-sectional secondary analyses inherit case-mix caveats and say so. Label leakage: none (label-free primary). Reconstruction: fixed within scan. The design does NOT rule out: the possibility that the score responds to any removed thoracic content - handled by the content regression, which is the identifiability core and must be adequately powered.",
      "alternative_explanations": "(1) Score drop reflects removed lung volume generically, not emphysema - separated by the regression contrast (low-%LAA truncations as controls). (2) Truncated volumes are subtly OOD despite loader compatibility - bounded by staying inside the empirical scan-start distribution and by a negative-control head (a purely abdominal phenotype, e.g. a renal code, should not respond to thoracic truncation). (3) The COPD head has near-zero signal on this external cohort and there is nothing to decode - bounded by a Stage 0 sanity check that the score distribution has variance and tracks basal %LAA cross-sectionally at all.",
      "anticipated_negative": "Decisive for the named X if gates pass: a flat dose-response against removed emphysema, inside the natural range, with the negative-control head behaving, means Merlin's COPD phenotype does not read the imaged lung bases - itself a striking, publishable statement given the cue is sitting in the scan. Gate failures are declared 'not testable', not negatives.",
      "cross_domain": null,
      "remaining_legwork": "Stage 0 loader inspection + scan-start census (~2-3 days); index-mapping trace (~1 day); inference over ~800 scan-variants on a single GPU (Merlin trains on one GPU; inference is light) (~2-3 days). First decision: ~1.5 weeks.",
      "scores": {
        "clarity": {
          "why": "One phenotype, one named cue, one intervention; slightly diffuse because 'COPD-family' spans four phecodes.",
          "value": 4
        },
        "identifiability": {
          "why": "Within-scan pairing plus content regression plus negative-control head; residual OOD risk is gated, not assumed away.",
          "value": 4
        },
        "medical_relevance": {
          "why": "Opportunistic COPD signal on abdominal CT is clinically actionable, and knowing the model reads real emphysema (vs abdominal correlates) determines whether to trust it.",
          "value": 4
        },
        "interest": {
          "why": "'The abdominal model is reading the chest' is surprising to exactly the audience the program serves.",
          "value": 4
        },
        "prior_legwork": {
          "why": "Everything public and documented; nothing yet run locally (unlike CT-CLIP).",
          "value": 4
        },
        "feasibility": {
          "why": "INSPECTED_TRUE; single-GPU by the model's own design; public data.",
          "value": 4
        },
        "data_readiness": {
          "why": "All public, immediate; basal-lung inclusion rate uncounted.",
          "value": 4
        },
        "evaluation_readiness": {
          "why": "Paired deltas and regression contrasts; no custom metrics.",
          "value": 4
        },
        "negative_result_value": {
          "why": "Decisive conditional on gates; the flat result is itself informative.",
          "value": 4
        },
        "novelty_confidence": {
          "why": "No FOV-spillover probe of Merlin found; search limited.",
          "value": 3
        },
        "regret": {
          "why": "Cheap, novel grammar for the portfolio, obvious in hindsight.",
          "value": 4
        }
      },
      "priority_score": 3.95,
      "unverified_claims": [
        "Phenotype-head output indexing corresponds to phenotypes.csv row order (inferred; to be traced in released code).",
        "Merlin loader tolerance of variable z-extent (uninspected; Stage 0 gate, idea-006 procedure).",
        "Basal lung inclusion frequency in AMOS/TotalSegmentator scans (anatomically expected, uncounted).",
        "Merlin phenotype AUROC for phecode 496 specifically (paper reports macro averages; per-phenotype value not checked)."
      ],
      "track": "baseline"
    },
    {
      "id": "scout-012-c04",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The non-gated chest CT contains an ECG: heart rate written in motion banding",
      "question": "Do CT-CLIP's cardiac heads use the patient's heart rate, read from the periodic motion banding a beating heart writes into a non-gated helical acquisition?",
      "design_template": "conditional-observational",
      "dataset": "CT-RATE (second and final CT-RATE candidate this cycle); TCIA gated collections only for validating the X-measurement",
      "entry_point_2_requirements": "Measurement: banding-wavelength-derived heart rate at the left cardiac border (construction below). Artifact it would be confused with: rotation time and pitch (protocol) set the sampling geometry - they are recorded in metadata and enter the formula rather than confounding it; respiratory motion and aortic pulsation are the confusable periodicities and must be separated by frequency band and location.",
      "rung": "Targets rung 1 only, and says so: establishing that a cardiac score covaries with banding-derived HR conditional on measured anatomy. Moving up requires an intervention (banding-smoothing edit) whose validity is a separate, harder project.",
      "deliverable_sentence": "The model is using the patient's heart rate, recorded in the scan as periodic cardiac motion banding.",
      "X_measurement": "A well-defined construction rather than an off-the-shelf tool (permitted by the charter): segment the heart (TotalSegmentator), track the left-heart border position slice-by-slice along z, take the spatial FFT of border displacement; the dominant banding frequency f_band, with table speed and gantry rotation period from acquisition metadata, yields an aliased candidate set of heart rates via beat-frequency arithmetic (stroboscopic sampling). Validate the construction once on gated cardiac CT collections where DICOM records HeartRate (0018,1088). Computable on an unseen scan without an annotator: YES, given acquisition metadata; the aliasing means HR is recovered as a small candidate set, honestly reported.",
      "suspected_signal": "Physiology, not electronics: tachycardia accompanies acute illness, heart failure, pericardial effusion. A model trained on image-report pairs has an incentive to use any image-visible correlate of clinical acuity; banding periodicity is exactly such a correlate, present in every non-gated chest CT and invisible-as-information to human readers, who file it under 'artifact'.",
      "use_vs_association": "This candidate honestly reaches association-with-named-competitors only: cardiac-head scores vs banding-HR conditional on measured chamber size, pericardial fluid, and effusion presence from the same scan. The one-line distinction: competitors are named, measured quantities from the same image, so a surviving partial association localizes the signal to the banding periodicity rather than to the anatomy the heads nominally measure. A banding-smoothing intervention is named as the upgrade path, not claimed.",
      "keystone_prerequisite": "What the inference needs: banding periodicity survives CT-RATE's released preprocessing (resampling to fixed spacing may low-pass it away), and acquisition metadata (rotation time, pitch/table speed) is present per volume to invert the formula.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The keystone above is already stated as the load-bearing fact (survival of banding through resampling), not the easy adjacent fact (that motion artifacts exist in chest CT, which is textbook). Additionally assumed: rotation time is in CT-RATE metadata (the Stage 0 record confirms rich acquisition metadata exists but I have not looked for RevolutionTime specifically); and that banding-HR has enough between-patient variance in a resting outpatient population.",
      "rung_reached": "1 at best this cycle, declared. Up: validated banding-smoothing edit (counterfactual with sham), or a cohort with recorded HR for direct anchoring.",
      "dies_like_prior": "Most resembles idea-007 (respiratory state), which survived by demoting its claim from mechanism-identification to state-sensitivity - this card starts at the demoted rung deliberately. No annotation-provenance dependence (no labels in the readout). The idea-006 OOD trap is avoided by not intervening at all this cycle.",
      "closest_prior_work": "Cardiac motion artifacts in non-gated CT are extensively documented as nuisance (coronary calcium scoring literature); I found no work extracting heart rate from banding periodicity as a signal, and no work asking whether any model uses it. Sanity check ('is it even recoverable?') has no published answer I could find - which is why the X-validation on gated data with recorded HR comes first. Absence of prior work is asserted from limited search.",
      "cross_domain": {
        "borrowed_construct": "Stroboscopic/aliased sampling (signal processing; rolling-shutter imaging): a rotating gantry samples a periodic motion, so the artifact pattern's spatial frequency encodes the beat frequency between heart rate and rotation rate.",
        "implied_measurement": "The FFT-of-border-displacement construction above, with the aliasing arithmetic that maps banding wavelength to an HR candidate set given rotation period and table speed.",
        "what_changes_if_dropped": "Everything: without the sampling-theory construct, banding is 'motion artifact', a nuisance with no formula, and there is no measurement to run. The analogy is not decoration; it is the instrument."
      },
      "existing_assets": "CT-RATE volumes + frozen metadata pipeline + working CT-CLIP scoring (probe 004); TotalSegmentator heart class; TCIA gated cardiac collections for X-validation (specific collection to be chosen; DICOM HR tag standard).",
      "smallest_decisive_experiment": "Phase 1 (X-validation, no model): on a gated collection with recorded HR, run the banding extractor on the non-gated-equivalent series and test recovery of HR within the aliased candidate set. Phase 2 (only if Phase 1 passes): on CT-RATE validation volumes, cardiomegaly/pericardial-effusion score vs banding-HR conditional on segmented cardiac volume and effusion measures.",
      "standing_confounds_addressed": "Protocol (rotation time/pitch): enters the formula from metadata, converted from confound to parameter; stratify by rotation time as a check. Scanner/vendor: 462/464 Siemens in the frozen subset - near-constant, stated as scope limit. Respiratory motion and aortic pulsation: separated by anatomical location (cardiac vs aortic border) and frequency band; imperfect, named. Habitus: noise floor of border tracking scales with image noise - conditioned. Prevalence/referral/label leakage: no labels in readout. NOT ruled out: HR correlates with true cardiac pathology the heads read directly from anatomy - the conditional design attenuates but cannot eliminate this; scored accordingly.",
      "alternative_explanations": "(1) Any surviving association reflects residual anatomical pathology imperfectly captured by the conditioning segmentations - the main threat, named, and the reason this is rung 1. (2) Banding amplitude (motion severity), not periodicity (rate), drives the score - distinguishable because amplitude and wavelength are separately measurable; test both. (3) The extractor measures noise - killed or confirmed by Phase 1 before the model is ever consulted.",
      "anticipated_negative": "Sensitivity-limited, declared: a Phase-1 failure (banding unrecoverable post-resampling) says nothing about the model; a Phase-2 null under a passing Phase 1 is evidence against use but bounded by conditioning quality. negative_result_value scored 2 accordingly.",
      "remaining_legwork": "Choose and download a gated collection with HR tags (~days); build the border-tracking extractor (~1 week); Phase 2 rides existing pipeline (~days). First decision (Phase 1): ~2 weeks.",
      "scores": {
        "mechanism_clarity": {
          "why": "A specific physiological quantity (heart rate), a specific physical encoding (beat-frequency banding), and an explicit formula with a validation dataset named.",
          "value": 5
        },
        "identifiability": {
          "why": "HR covaries with exactly the pathology the cardiac heads measure; conditioning on segmented anatomy attenuates but cannot sever this. Honest ceiling without an intervention.",
          "value": 2
        },
        "interest": {
          "why": "'The artifact is an instrument' - the strongest sounds-wrong-but-maybe-isn't question this cycle, and physicians would genuinely not expect it.",
          "value": 5
        },
        "medical_relevance": {
          "why": "If models read physiological state through artifacts, anatomical scores drift with acuity - a real deployment concern, one step removed from decisions.",
          "value": 3
        },
        "clarity": {
          "why": "Precise question; the aliasing candidate-set complication costs a point.",
          "value": 4
        },
        "feasibility_informational": {
          "why": "Capped by NOT_INSPECTED anyway; Phase 1 is genuinely uncertain.",
          "value": 2
        },
        "novelty_confidence_informational": {
          "why": "Nothing found on banding-as-signal; limited search; capped.",
          "value": 3
        },
        "negative_result_value_informational": {
          "why": "Sensitivity-limited as classified.",
          "value": 2
        }
      },
      "priority_score": 3.85,
      "priority_note": "Mode C weighting: 0.30*5 + 0.25*2 + 0.20*5 + 0.15*3 + 0.10*4 = 3.85; feasibility and novelty reported outside the score per rubric.",
      "unverified_claims": [
        "Banding periodicity survives CT-RATE resampling (the keystone; unknown).",
        "RevolutionTime/pitch present per-volume in CT-RATE metadata (acquisition metadata exists per Stage 0 record; these tags not specifically confirmed).",
        "A TCIA gated collection retains DICOM HeartRate tags after de-identification (standard tag, but de-id profiles vary).",
        "The beat-frequency formula as sketched (derived here; not yet checked against the CT physics literature on banding artifacts)."
      ],
      "track": "baseline"
    },
    {
      "id": "scout-012-c05",
      "search_mode": "C",
      "entry_point": 1,
      "title": "The prognosis model as a manometer: midline shift is pressure the skull wrote down",
      "question": "Does the head-CT TBI outcome model of Pease et al. use midline shift out of proportion to lesion volume - the Monro-Kellie signature of exhausted intracranial compliance - beyond the hemorrhage it can see directly?",
      "design_template": "conditional-observational",
      "dataset": "Anchor model's cohort (single-institution + TRACK-TBI) - access is the declared rate-limiter; CQ500 (public, has MLS/mass-effect reads but no outcomes) for X-measurement development only",
      "rung": "Targets rung 1 (the model uses shift-beyond-volume), honestly conditional on model access; rung 2 would need acquisition stratification within the anchor cohort; the rung-3 sentence is below and is already radiologist vocabulary.",
      "deliverable_sentence": "The model is using midline shift out of proportion to lesion volume - the image signature of exhausted intracranial compliance.",
      "X_measurement": "Midline shift in millimeters: automated as the deviation of the septum pellucidum / third ventricle from the ideal midline plane (skull-symmetry registration + ventricle segmentation; automated MLS algorithms are published and validated, e.g. the CQ500 line of work - specific tool to be pinned in feasibility). Lesion+edema volume: public intracranial hemorrhage segmentation models. The compliance construct is the residual of MLS regressed on lesion+edema volume - a formula, not a judgment. Computable on an unseen head CT today without an annotator: YES.",
      "suspected_signal": "Monro-Kellie: the cranium is a closed, fixed-volume vessel; CSF and venous buffering absorb early mass effect, so once shift grows disproportionate to lesion volume, compliance is exhausted and intracranial pressure is rising. Shift-conditional-on-volume is therefore a pressure state written in geometry - precisely the kind of physiological quantity an outcome-trained CNN would find, since ICP, not hemorrhage volume, is what kills.",
      "use_vs_association": "Association with named competitors, declared as such: model risk score vs automated MLS conditional on lesion+edema volume (and vs the interaction - shift per unit volume). A surviving conditional dependence localizes the signal to displacement rather than lesion burden; upgrading to use requires access to run the model on counterfactually warped inputs, named as future work, not claimed.",
      "keystone_prerequisite": "What the inference needs: the trained Pease et al. model (weights or scored outputs on a shareable cohort) is obtainable, since the claim is about what THAT documented-gap model uses; a re-trained substitute would change the claim's identity.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_residual_assumption": "The keystone is already the load-bearing fact: model availability. Not inspected; probably not publicly released; the honest path is author correspondence or a hosted-inference arrangement, and this card accepts the caps that follow. Also assumed: automated MLS tools transfer to the anchor cohort's acquisition profile, and MLS variance conditional on volume is adequate in severe TBI (clinically expected - the shift-out-of-proportion patient is a recognized archetype - but unmeasured here).",
      "rung_reached": "1 conditional on access; without access, 0 - stated plainly. Up: counterfactual midline-restoring warps with sham-warp controls, if edit validity can be established in brain CT (a hard, separate problem).",
      "dies_like_prior": "Most resembles idea-018 (DATA_ACCESS kill: required model/data not obtainable) and says so upfront - the difference is only that this card declares access as its keystone from the start, requests correspondence as Stage 0, and stops if it fails rather than substituting a retrained model (which would repeat the idea-015 claim-identity error). No annotation-provenance issue: MLS and volumes are computed, not read; outcome labels (GOS) are trial-adjudicated, not image-derived.",
      "closest_prior_work": "Pease et al., Radiology 2022;304(2):385-394 (DOI 10.1148/radiol.212181, PMID 35471108): DL on admission head CT + clinical variables predicted 6-month outcome in severe TBI, evaluated against the IMPACT model and neurosurgeon predictions, with external TRACK-TBI validation - the documented gap. Their interpretability stopped at saliency-style inspection; no quantitative decomposition of the image signal into named radiological quantities. IMPACT itself uses human-read CT class (Marshall) - the model beating it while reading CT directly is exactly an undecoded signal.",
      "existing_assets": "Anchor paper with external validation; automated MLS literature; public ICH segmentation models; CQ500 (public) for building and sanity-checking the X pipeline against its expert MLS reads before any anchor-cohort contact.",
      "smallest_decisive_experiment": "Stage 0a: build the MLS+volume pipeline on CQ500 and check automated MLS against CQ500's released reads (tool validation, no model involved). Stage 0b: author correspondence for scored outputs or hosted inference. Then: variance decomposition of the model's image-derived risk into lesion volume, MLS, and MLS-conditional-on-volume.",
      "standing_confounds_addressed": "Scanner/protocol/site: anchor cohort is one institution + 18-site TRACK-TBI; stratify by site in the external set if access includes it. Positioning: head tilt corrupts naive MLS - the registration-based ideal-midline method addresses this and is why the tool must be validated first. Habitus/prevalence/referral: outcome model, single defined population (severe TBI admissions); referral homogeneous by definition. Label leakage: outcomes are 6-month GOS, not report-derived. NOT ruled out observationally: MLS correlates with everything severe (multiple lesions, cisternal effacement) - hence rung 1 and the named-competitor framing.",
      "alternative_explanations": "(1) The model reads cisternal effacement or other severity correlates and MLS merely tags along - partially separable by adding automated cistern volume to the competitor set; acknowledged residual. (2) The clinical-fusion pathway (GCS, pupils) carries the compliance information and the image contributes little - separable if the released design allows image-only scoring (the paper reports an image-only variant). (3) A null could reflect the model genuinely compressing everything into lesion burden - that is the decisive negative, and it is interesting: the celebrated model would be shown to ignore the quantity neurosurgeons act on.",
      "anticipated_negative": "Decisive for the named X given access and tool validation: if the image-derived score has no MLS-conditional-on-volume component, the model does not read the pressure signature - a clinically pointed finding. Without access, no experiment exists; that outcome is a feasibility result (idea-018 pattern), recorded and closed cheaply.",
      "cross_domain": {
        "borrowed_construct": "Closed-vessel mechanics / Monro-Kellie doctrine: in a rigid container, displacement out of proportion to added volume signals exhausted compliance and rising pressure.",
        "implied_measurement": "Not MLS alone but the residual of MLS on lesion+edema volume - shift per unit mass - as the pressure-state variable the model is tested against.",
        "what_changes_if_dropped": "Without the construct you would test 'model uses lesion size' or 'model uses MLS' marginally; the construct specifically predicts the conditional/residual term carries the outcome signal, which is a different regression and a different claim."
      },
      "remaining_legwork": "CQ500 pipeline build + validation (~1-2 weeks, fully public, zero model risk); correspondence (unbounded latency, cheap to initiate); analysis itself is days once scores exist. First decision point (Stage 0a tool validation) is independent of access and useful to two future candidates.",
      "scores": {
        "mechanism_clarity": {
          "why": "A named physiological quantity (intracranial pressure state via compliance), a physical law that predicts its geometric signature, and an explicit residual-regression measurement.",
          "value": 5
        },
        "identifiability": {
          "why": "MLS-vs-volume are separable in principle and clinically distinct in practice, but severity correlates (cisterns, multiplicity) remain partially entangled without intervention.",
          "value": 3
        },
        "interest": {
          "why": "A prognosis model shown to read the quantity surgeons actually act on would be the program's cleanest rung-3 story; the access risk is what keeps this from 5.",
          "value": 4
        },
        "medical_relevance": {
          "why": "ICP management is THE decision in severe TBI; a model that reads compliance is a model a neurosurgeon can reason with.",
          "value": 5
        },
        "clarity": {
          "why": "Precise conditional claim; loses a point for depending on which model variant (fusion vs image-only) access provides.",
          "value": 4
        },
        "feasibility_informational": {
          "why": "Model access unestablished and probably hard; capped and honestly low regardless.",
          "value": 1
        },
        "novelty_confidence_informational": {
          "why": "No decoding of TBI outcome models into named CT quantities found; limited search; capped.",
          "value": 3
        },
        "negative_result_value_informational": {
          "why": "Decisive if access exists; the access-failure outcome is only a feasibility note.",
          "value": 3
        }
      },
      "priority_score": 4.2,
      "priority_note": "Mode C weighting: 0.30*5 + 0.25*3 + 0.20*4 + 0.15*5 + 0.10*4 = 4.20; feasibility and novelty reported outside the score per rubric - the rubric explicitly forbids demoting Mode C for being hard, and the untestability escape hatch (Stage 0a is runnable today on public data) is what keeps this eligible.",
      "unverified_claims": [
        "Pease et al. model weights are not publicly released (presumed; not yet checked against the paper's data-availability statement).",
        "The paper reports an image-only model variant (recalled from search summary; must be verified in the full text).",
        "Automated MLS tool accuracy at CQ500-scale (published claims not yet read in primary form).",
        "CQ500 licensing permits this derivative use (public research release; terms not re-read this cycle)."
      ],
      "track": "baseline"
    }
  ]
}


===== ideas/scout-012/run_provenance.json =====
{
  "timestamp": "2026-08-14T07:10:02+00:00",
  "git_commit": "8a7b2da846306675457aa5a9691883495650d8d3",
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


===== ideas/scout-012/scout_candidates.json =====
{
  "cycle": "scout-012",
  "date": "2026-08-14",
  "track": "baseline",
  "quota_note": "Quotas met without padding: 1 Mode A, 2 Mode B, 2 Mode C; five of five in radiology/CT; zero dermatology; CT-RATE used twice (limit), NLST twice (limit, one as substrate for a reproduced classifier). Zero revivals: nothing in the portfolio brief has a NEW checkable fact that changes a blocking condition, and manufacturing one is forbidden. Homogenization note: candidates 1 and 2 declare regional-substitution, which is already the portfolio's most common grammar (5 uses); candidate 3 introduces regional-removal via NATURAL field-of-view truncation, a grammar the portfolio has not used. The critic should weigh whether both substitution candidates deserve development in the same cycle.",
  "revivals": [],
  "all_questions": [
    {
      "q": "Does the chest-CT race classifier of Gichoya et al. use vertebral trabecular bone attenuation - the bone density everyone names and nobody measured?",
      "status": "DEVELOPED (c01, Mode A)"
    },
    {
      "q": "Does CT-CLIP's pulmonary-fibrotic-sequela score use the air-filled dilated esophagus that radiologists read as a connective-tissue-disease clue?",
      "status": "DEVELOPED (c02, Mode B)"
    },
    {
      "q": "Does Merlin use the emphysema visible in the lung bases captured at the top of an abdominal CT when it scores chronic airway obstruction?",
      "status": "DEVELOPED (c03, Mode B)"
    },
    {
      "q": "Do CT-CLIP's cardiac heads use the patient's heart rate, read from the periodic motion banding a beating heart writes into non-gated helical CT? (sounds obviously wrong; cross-domain: stroboscopic sampling)",
      "status": "DEVELOPED (c04, Mode C)"
    },
    {
      "q": "Does the head-CT TBI outcome model use midline shift out of proportion to lesion volume - the Monro-Kellie pressure readout? (cross-domain: closed-vessel mechanics)",
      "status": "DEVELOPED (c05, Mode C)"
    },
    {
      "q": "Does an age probe on chest-CT embeddings use thymic involution (prevascular fat replacement)?",
      "status": "DROPPED - would be a third CT-RATE candidate this cycle (quota); the alternative substrate NLST is age 55-74, where thymic involution is essentially complete and the mechanism has no variance left. Queue for a cycle with a broad-age chest cohort."
    },
    {
      "q": "Does CT-CLIP's lymphadenopathy head use node short-axis diameter with a sigmoid knee at the radiologist's 10-mm rule?",
      "status": "DROPPED - same 'has the model learned the written rule' grammar as backlog scout-010-c02 (atelectasis volume-loss rule); mediastinal node segmentation tool for non-contrast CT unverified; would also be a third CT-RATE candidate."
    },
    {
      "q": "Does CT-CLIP's mosaic-attenuation head use the vessel-caliber deficit in the lucent lung (the radiologist's mosaic-perfusion rule)?",
      "status": "DROPPED - the head exists (verified this cycle at probes/004/run.py:152, contrary to a plausible misreading of the idea-007 ledger note), but the candidate needs vessel segmentation validated on 1.5 mm resampled volumes and rides an exhausted CT-RATE quota. Good candidate for cycle 013."
    },
    {
      "q": "Does a deterioration/mortality model read splenic contraction as a catecholamine gauge (diving-reflex physiology)?",
      "status": "DROPPED - the spleen already carries backlog candidate scout-010-c03 (homogenization); no in-hand anchor model outputs an acute-deterioration score; no HR/catecholamine ground truth to validate the X-measurement."
    },
    {
      "q": "Do abdominal foundation models use departures from allometric organ-volume scaling (Kleiber-style) as a frailty signal?",
      "status": "DROPPED - fails the fluent-nonsense gate: no single named X a radiologist has a word for, and the allometry analogy currently implies no measurement that a plain organ-volume regression would not already run."
    }
  ],
  "candidates": [
    {
      "id": "scout-012-c01",
      "search_mode": "A",
      "entry_point": 1,
      "title": "The race signal in chest CT: measure the bone density everyone names and nobody measured",
      "question": "Does the chest-CT race classifier of Gichoya et al., trained on NLST, use vertebral trabecular attenuation - the opportunistic bone-density measure already validated in screening CT?",
      "design_template": "regional-substitution",
      "dataset": "NLST (CDAS; same cohort the anchor paper trained on)",
      "rung": "Targets rung 2 with a rung-3 sentence conditional on the substitution arm. Rung 1 is delivered by the substitution readout; rung 2 by site/scanner/habitus stratification available in NLST metadata; rung 3 (the sentence below) requires both plus a mediated-fraction estimate.",
      "deliverable_sentence": "The race classifier is using the trabecular bone mineral attenuation of the visible vertebrae.",
      "X_measurement": "Mean trabecular attenuation (HU) inside eroded vertebral-body masks from TotalSegmentator (Wasserthal et al. 2023, Radiology: AI, DOI 10.1148/ryai.230024; vertebrae are named classes), the standard opportunistic-osteoporosis measurement (Pickhardt et al. 2013, Ann Intern Med, DOI 10.7326/0003-4819-158-9-201305070-00003, L1 trabecular HU; thoracic-level variants validated in lung-screening LDCT). Computable today on a scan the model has never seen, with no human annotator: YES.",
      "suspected_signal": "Population-level BMD differences by self-reported race are among the largest documented imaging-visible anthropometric differences (NHANES DXA: higher mean femoral/lumbar BMD in Black adults). Trabecular attenuation is directly rendered in calibrated CT HU, is spatially diffuse (consistent with the signal surviving patch ablation in prior work), and survives resolution degradation (consistent with the low-frequency robustness the anchor paper reported).",
      "use_vs_association": "Association arm is explicitly labeled association; USE is carried by sham-controlled substitution: swap the trabecular interior between geometry-matched patients of discordant self-reported race, with same-race swaps as the sham floor - score movement above sham distinguishes use from correlation.",
      "keystone_prerequisite": "What the inference needs: (a) the demonstrated NLST chest-CT race signal is reproducible with slice-level models at single-GPU compute on scans where (b) vertebral trabecular HU is measurable, and (c) the anchor study genuinely left quantitative BMD unmeasured (the Mode A gap exists).",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "Component (c) and the CT anchor inspected in the full text (PMC9650160, 'AI recognition of patient race in medical imaging: a modelling study'): chest CT experiments used NLST with race-prediction AUC 0.92 (slice) / 0.96 (study), external validation on EM-CT and RSPECT; the only bone-related test was removal of brightest pixels on radiographs ('deep learning models effectively predicted patient race even when the bone density information was removed', AUC 0.960/0.945 on MIMIC-CXR/CheXpert) - bone mineral density was never quantitatively measured, and never tested on CT at all. Component (b): TotalSegmentator vertebral classes are documented in the cited paper/tool. Component (a) is NOT inspectable in advance and is listed as the residual assumption.",
      "keystone_residual_assumption": "Load-bearing residuals, stated per the three-strikes rule: (1) the NLST CDAS delivery links self-reported race to the imaging at the scan level (race was collected in NLST; the linkage in the delivered tables is inferred, not inspected); (2) a slice-level classifier at AUC >= 0.85 is reproducible within Colab-class compute (the anchor used slice-level training, which argues yes, but this is assumed until run); (3) within age-sex-site strata there remains enough trabecular-HU variance to test mediation. If (1) or (2) fails, the candidate is dead, not merely weakened.",
      "rung_reached": "1 by design (use of X via substitution); moves to 2 with site/scanner stratification and habitus conditioning; the mediated fraction determines whether the rung-3 sentence is 'is using' or 'is partly using'.",
      "dies_like_prior": "No annotation-provenance failure applies: self-reported race is subject-reported demographic data, independent of any image reader. Closest prior kill is idea-009 (IDENTIFIABILITY_FAILURE: index inseparable from covariates in any obtainable cohort); the difference is that identifiability here is not carried observationally but by within-pair trabecular substitution with a same-race sham floor, and NLST's uniform screening eligibility plus 33-site metadata gives real stratification support that idea-009 never had.",
      "closest_prior_work": "Gichoya et al. 2022, Lancet Digit Health 4:e406-14 (DOI 10.1016/S2589-7500(22)00063-2; preprint arXiv:2107.10356). They established the phenomenon across modalities including NLST chest CT and tested many candidate explanations - but their bone test was brightness clipping on uncalibrated radiographs, which removes cortical extremes, not the trabecular mean, and no bone test was performed on CT. Follow-up literature (e.g., frequency-domain and anatomical-region ablations) remains confound-elimination; I found no study regressing or intervening on quantitative CT BMD. That absence is a search result, not proof.",
      "existing_assets": "Anchor paper's public training code (Emory-HITI 'AI-vengers' repo - existence recalled, unverified); NLST already the working cohort of ideas 008/012/017 in this portfolio; TotalSegmentator off-the-shelf; opportunistic-BMD literature supplies validated thresholds and expected effect sizes.",
      "smallest_decisive_experiment": "On an NLST subset: (i) reproduce the slice-level race classifier (their recipe); (ii) compute trabecular HU per scan with TotalSegmentator; (iii) report fraction of race-score variance explained by trabecular HU within age-sex-site strata; (iv) in ~100 geometry-matched cross-race pairs, substitute vertebral trabecular interiors (same-race substitution as sham) and read the score shift. (iii) is association, labeled as such; (iv) is the use readout.",
      "standing_confounds_addressed": "Scanner/site: NLST race composition varies by site, so all observational readouts stratify by site and scanner model (metadata available); the paired substitution arm is within-pair immune. Protocol/reconstruction: stratify by kernel as in the anchor cohort. Habitus: condition on body cross-sectional area computed from the same scan. Prevalence/referral: screening trial with uniform eligibility - the strongest referral-pathway control available anywhere. Label leakage: no reports involved. NOT ruled out observationally: body-composition axes correlated with BMD (muscle attenuation, marrow fat) - measured and co-modeled, but only the substitution arm separates them.",
      "alternative_explanations": "(1) BMD is a marker, not the signal - the model reads correlated soft-tissue composition; substitution arm with trabecular-only edits addresses this, observational arm cannot. (2) Substitution edits are out-of-distribution and the score shift measures edit artifact - addressed by the same-race sham floor and a prespecified sham-effect tolerance (idea-008's lesson). (3) The anchor's own CXR bright-pixel result suggests bone is not the signal - acknowledged honestly; that experiment removed clipped cortical brightness on uncalibrated radiographs and is weak evidence about calibrated trabecular HU on CT, which is exactly why the direct measurement is the missing experiment.",
      "anticipated_negative": "Decisive, with an equivalence margin: if trabecular HU explains less than a prespecified fraction of stratified score variance AND substitution moves the score by less than the sham-derived margin, the most-cited candidate explanation for the field's most famous unexplained signal is dead on the modality where it is most measurable. That is a publishable type-1 negative.",
      "cross_domain": null,
      "remaining_legwork": "CDAS project scope/approval for race+images subset (weeks, administrative); classifier reproduction (~days of Colab); TotalSegmentator batch run (~days); substitution tooling reusing portfolio edit-validity machinery. First decision (observational arm): ~2-3 weeks after data in hand.",
      "scores": {
        "clarity": {"score": 4, "why": "One named X, one named model, one sentence; loses a point because 'the race signal' is a family of models, not one checkpoint."},
        "identifiability": {"score": 3, "why": "Observational arm is confounded by correlated body composition; the sham-controlled substitution arm carries identification but inherits edit-validity risk."},
        "medical_relevance": {"score": 4, "why": "Mechanism of the most-discussed algorithmic-bias vector in radiology; a positive names the shortcut vector deployed models carry."},
        "interest": {"score": 5, "why": "Four years of literature says 'nobody knows what the signal is'; this is the named-X experiment that literature keeps gesturing at."},
        "prior_legwork": {"score": 4, "why": "Anchor code public, cohort known, X-measurement tools validated; nothing needs inventing."},
        "feasibility": {"score": 3, "why": "Cap lifted by INSPECTED_TRUE but honestly 3: NLST delivery, classifier training, and edit machinery are each real work."},
        "data_readiness": {"score": 3, "why": "NLST via CDAS: obtainable with administrative latency, precedented in this portfolio, not in hand."},
        "evaluation_readiness": {"score": 4, "why": "AUC for reproduction, variance-explained and paired score-shift with sham floor are all standard."},
        "negative_result_value": {"score": 5, "why": "Type-1 decisive against the field's most-cited hypothesis, with margins."},
        "novelty_confidence": {"score": 3, "why": "The gap is verified inside the anchor paper, but the follow-up literature is large and my search for a quantitative-BMD test was not exhaustive."},
        "regret": {"score": 5, "why": "If someone else runs this first it will look obvious in hindsight."}
      },
      "priority_score": 3.8,
      "unverified_claims": [
        "NHANES-scale BMD differences by self-reported race (direction and rough magnitude from memory; needs primary citation).",
        "Public availability and completeness of the Emory-HITI training code (from memory).",
        "NLST CDAS delivery links self-reported race to scans (inferred from trial design; data dictionary not inspected).",
        "Thoracic-level opportunistic BMD validation in LDCT (literature recalled, specific citation needed)."
      ]
    },
    {
      "id": "scout-012-c02",
      "search_mode": "B",
      "entry_point": 2,
      "title": "The dilated esophagus inside the fibrosis score",
      "question": "Does CT-CLIP's pulmonary-fibrotic-sequela score use the air-filled dilated esophagus - the connective-tissue-disease clue radiologists read alongside the lungs?",
      "design_template": "regional-substitution",
      "dataset": "CT-RATE (validation split; local inference pipeline already frozen and probe-verified)",
      "entry_point_2_requirements": "Measurement that would detect the unexpected signal: partial association of the fibrosis score with esophageal air volume conditional on a lung-only quantitative fibrosis surrogate, then digital esophageal collapse with sham. Artifact it would be confused with: contrastive label binding from reports that co-mention esophageal dilation (a training-provenance fact that does not change the image-use claim, but changes its interpretation), and positioning/aerophagia correlates.",
      "rung": "Targets rung 1 (use), with rung 2 within reach because the decisive readout is within-scan paired and label-free; rung 3 sentence below is the honest endpoint if the substitution arm is positive and sham-clean.",
      "deliverable_sentence": "The model's fibrosis score is using the air-filled, dilated esophagus.",
      "X_measurement": "Esophageal air volume and maximal luminal diameter: TotalSegmentator 'esophagus' class (Wasserthal et al. 2023, DOI 10.1148/ryai.230024), air = voxels < -500 HU within the (slightly dilated) mask; diameter from per-slice mask geometry. Computable today without an annotator: YES.",
      "suspected_signal": "Esophageal dysmotility in systemic sclerosis and other CTD-ILD produces a patulous, air-filled esophagus; a visibly dilated esophagus on chest CT is a standard clue toward CTD-ILD in fibrosis workup. A contrastive model trained on image-report pairs would be rewarded for binding this extra-pulmonary cue to fibrosis language.",
      "use_vs_association": "Primary conditional association is labeled association; USE is carried by a within-scan intervention - digitally collapsing the esophagus (replace luminal air with adjacent mediastinal soft-tissue HU) against a sham edit of matched voxel count elsewhere, reading the paired fibrosis-score change.",
      "keystone_prerequisite": "What the inference needs: a locally computable per-volume 'Pulmonary fibrotic sequela' score from the released CT-CLIP checkpoint on CT-RATE volumes.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "probes/004/run.py:150 lists \"Pulmonary fibrotic sequela\" in EXPECTED_PATHOLOGIES (18 heads), and the 2026-08-12 ledger decision records the load probe producing '18 finite named scores' bit-deterministically from the frozen CT_LiPro_v2.pt checkpoint (SHA-256 9246d9c8...) under the pinned pipeline. The scoring machinery for this exact head is verified working on this machine's lineage.",
      "keystone_residual_assumption": "Still assumed, load-bearing for power rather than possibility: (1) CT-RATE fibrosis-positive volumes contain enough variance in esophageal air (prevalence of visible dilation is unknown until counted - Stage 0 gate with a prespecified minimum); (2) TotalSegmentator's esophagus class performs adequately on CT-RATE's resampled geometry (spot-check gate); (3) the collapse edit can pass a sham-effect tolerance (idea-008's edit-validity lesson, prespecified before any score is read).",
      "rung_reached": "1 if substitution is positive and sham-clean; 2 requires the confound work below (much of it comes free from the paired design); 3 is the deliverable sentence itself, which is already stated in words a chest radiologist uses.",
      "dies_like_prior": "Not annotation-provenance: the primary readout is the model against its own edited input - no label enters the primary measurement (the structural move the charter says has saved the one surviving candidate). Not idea-010 circularity: the esophagus is not part of the fibrosis label's definition. The live inherited risk is idea-008's edit-validity objection - addressed by prespecified sham tolerance, not assumed away.",
      "closest_prior_work": "CT-CLIP/CT-RATE (Hamamci et al., arXiv:2403.17834) provides model and labels but no per-concept decoding of the fibrosis head. Radiology literature documents esophageal dilation as a CTD-ILD marker (primary citation to be pinned in feasibility; currently from memory). I found no work probing any chest-CT foundation model for extra-pulmonary reliance of a fibrosis output; not exhaustively searched.",
      "existing_assets": "Frozen CT-CLIP checkpoint + pinned environment + validated metadata/selection machinery from probe 004 (the portfolio's most de-risked pipeline); TotalSegmentator; CT-RATE validation volumes enumerable locally.",
      "smallest_decisive_experiment": "Stage 0: count fibrosis-positive validation volumes with measurable esophageal air (gate). Then: (i) fibrosis score vs esophageal air conditional on %high-attenuation-area of the lungs (an automated lung-only fibrosis surrogate) and lung volume; (ii) in the top-decile dilated-esophagus volumes, collapse the esophagus digitally, sham edit control, read paired score change on ~100 volumes (~0.25 GPU-min/volume per probe 004 timing).",
      "standing_confounds_addressed": "Scanner/protocol/reconstruction/site: within-scan paired edits are immune; observational arm stratifies by kernel using the frozen metadata pipeline. Positioning/habitus: unchanged within pair; conditioned in the observational arm. Prevalence/referral: single-center CT-RATE limits external generalization, not internal validity - stated as scope limit. Label leakage: labels never enter the primary readout; report co-mention explains mechanism of acquisition, not the image-use claim.",
      "alternative_explanations": "(1) Score shift measures edit artifact, not esophagus use - sham floor with prespecified tolerance addresses; if sham fails tolerance the candidate stops rather than reinterprets. (2) The model reads adjacent mediastinal changes the edit disturbs (hiatal hernia head shares anatomy) - check cross-head specificity: the esophageal collapse should move the fibrosis head more than unrelated heads. (3) Esophageal air proxies supine dwell time/aerophagia correlated with sicker patients - the conditional arm cannot fully exclude this; the substitution arm can, because the claim is about the image cue, whatever its upstream cause.",
      "anticipated_negative": "Decisive for the named X given gates pass: no conditional association AND no paired score response beyond sham tolerance in adequately dilated cases kills the hypothesis. If the Stage 0 prevalence gate fails, the result is 'not testable in this cohort', declared as such, not a negative.",
      "cross_domain": null,
      "remaining_legwork": "Stage 0 prevalence count + esophagus segmentation spot-check (~2-3 days); edit implementation with sham calibration (~1 week); scoring runs are cheap on the existing pipeline. First decision: ~2 weeks.",
      "scores": {
        "clarity": {"score": 5, "why": "One head, one named organ, one intervention, one sentence."},
        "identifiability": {"score": 4, "why": "Within-scan paired edit with sham floor and cross-head specificity check; residual edit-validity risk keeps it from 5."},
        "medical_relevance": {"score": 4, "why": "If fibrosis scores lean on the esophagus they inherit CTD-ILD case-mix bias and mislead in non-CTD fibrosis - directly deployment-relevant."},
        "interest": {"score": 4, "why": "An extra-pulmonary organ inside a pulmonary score is the kind of finding a radiologist immediately understands and did not expect a probe to establish."},
        "prior_legwork": {"score": 5, "why": "Rides the only probe-verified pipeline in the portfolio; every tool named is in hand or off-the-shelf."},
        "feasibility": {"score": 4, "why": "INSPECTED_TRUE; scoring machinery verified; the only real work is the edit and the gates."},
        "data_readiness": {"score": 5, "why": "CT-RATE validation split enumerated and frozen locally."},
        "evaluation_readiness": {"score": 4, "why": "Paired score deltas with sham margins follow the accepted idea-004 readout pattern."},
        "negative_result_value": {"score": 4, "why": "Decisive against the named X conditional on the prevalence and sham gates."},
        "novelty_confidence": {"score": 3, "why": "No probe of CT-CLIP extra-pulmonary reliance found, but search was limited; capped by honesty, not by rule."},
        "regret": {"score": 4, "why": "Cheap, fast, and the positive is a memorable sentence."}
      },
      "priority_score": 4.1,
      "unverified_claims": [
        "Esophageal dilation as a CTD-ILD clue: standard radiology teaching, but the primary citation is from memory and must be pinned.",
        "Prevalence of visible esophageal air/dilation in CT-RATE fibrosis positives: unknown until Stage 0.",
        "TotalSegmentator esophagus-class accuracy on CT-RATE resampled volumes: assumed pending spot-check."
      ]
    },
    {
      "id": "scout-012-c03",
      "search_mode": "B",
      "entry_point": 2,
      "title": "Merlin's COPD call may come from the lungs it wasn't asked to look at",
      "question": "Does Merlin use the emphysema visible in the lung bases captured at the top of an abdominal CT when it scores the chronic-airway-obstruction phenotype?",
      "design_template": "regional-removal",
      "dataset": "Public abdominal CT (AMOS 2022 / TotalSegmentator public dataset) + released Merlin checkpoint",
      "entry_point_2_requirements": "Measurement that would detect the unexpected signal: %LAA-950 within the imaged basal lung, and the dose-response of the phenotype score to natural-range superior truncation. Artifact it would be confused with: scan superior extent itself covaries with protocol and habitus (longer coverage on some indications), so score-versus-extent must be separated from score-versus-removed-emphysema; the paired within-scan design plus regressing score change on removed-slab content does that separation explicitly.",
      "rung": "Targets rung 1-2 in one design: the primary readout is label-free and within-scan (rung 1 use), and the natural-variation framing plus content regression does most rung-2 work structurally.",
      "deliverable_sentence": "The model is using emphysematous destruction of the lung bases imaged at the top of the scan.",
      "X_measurement": "%LAA-950: percentage of imaged lung voxels below -950 HU within TotalSegmentator lung masks restricted to the field of view - the standard quantitative emphysema index (Gevenois et al. 1996, Am J Respir Crit Care Med, DOI 10.1164/ajrccm.154.1.8680679). Computable today without an annotator: YES.",
      "suspected_signal": "Emphysema is visible at the lung bases; standard abdominal protocols begin above the diaphragm, so several centimeters of lung enter every abdominal CT; Merlin's phecode supervision (496, chronic airway obstruction) pairs those voxels with COPD outcomes at training time. The model has both the cue and the incentive.",
      "use_vs_association": "USE is read directly: progressively truncate the superior slab within the naturally occurring range of scan starts and regress the paired score change on the emphysema content of the removed slab (vs its total volume, cardiac volume, and atelectasis content) - an input intervention, not a correlation.",
      "keystone_prerequisite": "What the inference needs: the released Merlin checkpoint exposes a per-scan phenotype head that includes a COPD-family phenotype.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "GitHub StanfordMIMI/Merlin README documents initialization modes including Merlin(PhenotypeCls=True) (phenotype classification head released, MIT license, pip 'merlin-vlm', HF stanfordmimi/Merlin); documentation/phenotypes.csv in the same repo contains rows '496,Chronic airway obstruction' and '496.1,Emphysema' (also 496.2 chronic bronchitis, 496.3 bronchiectasis). Both fetched and read 2026-08-14.",
      "keystone_residual_assumption": "Still assumed, and stated as the real remaining keystones: (1) the phenotype head's output index mapping to phenotypes.csv rows is documented or recoverable from the released code (inferred from repo structure, not yet traced); (2) Merlin's preprocessing handles variable superior extent through the same deterministic path, so truncated volumes are in-distribution - this is exactly the idea-006 lesson, and Stage 0 must inspect Merlin's released dataloader the way the idea-006 unblock check inspected CT-CLIP's, plus quantify the empirical distribution of scan starts in the public cohort and stay inside it; (3) AMOS/TotalSegmentator-dataset scans actually include lung bases at useful frequency (anatomically near-certain for standard protocols, uncounted).",
      "rung_reached": "1 on a positive dose-response attributable to removed emphysema; 2 largely structural (within-scan pairing kills scanner/site/positioning; content regression separates emphysema from generic slab removal); 3 is the deliverable sentence, already in physician vocabulary.",
      "dies_like_prior": "Closest prior kill is idea-006 (PAUSED: patient-deletion was an extreme OOD intervention). The difference is explicit and testable: superior truncation reproduces a natural axis of acquisition variation present in Merlin's training distribution (scan coverage varies patient to patient), the truncation range is confined to the empirically observed range of scan starts, and the in-distribution claim is gated on dataloader inspection BEFORE any inference - the exact procedure that idea-006 learned the hard way. No annotation-provenance dependence: primary readout is label-free.",
      "closest_prior_work": "Merlin (Blankemeier et al., arXiv:2406.06512): reports phenotype AUROCs, including respiratory phecodes, but no attribution of any phenotype to specific anatomy. The opportunistic-screening literature runs the reverse direction (measure lung bases, predict COPD) and never asks what a trained foundation model actually uses. Backlog Merlin candidates (spleen, renal atrophy, pancreatic fat, osteoporosis) target abdominal organs; none touches the imaged thorax spillover.",
      "existing_assets": "Merlin: MIT-licensed weights, pip package, demo inference scripts (all public); AMOS 2022 and TotalSegmentator dataset public; TotalSegmentator for lung masks and %LAA; no labels required for the primary readout.",
      "smallest_decisive_experiment": "Stage 0: inspect Merlin loader for z-extent handling; measure the natural distribution of superior scan starts and basal-lung inclusion in the public cohort. Then on ~200 public abdominal CTs spanning basal %LAA: score each scan at 3-4 nested natural-range superior extents; regress paired chronic-airway-obstruction score change on removed-slab %LAA vs removed-slab lung volume, cardiac volume, and atelectasis content.",
      "standing_confounds_addressed": "Scanner/vendor/protocol/site/positioning: within-scan paired truncation is immune to all of them. Habitus: unchanged within scan; conditioned across scans. Prevalence/referral: no outcome labels in the primary readout, so case-mix cannot leak into it; cross-sectional secondary analyses inherit case-mix caveats and say so. Label leakage: none (label-free primary). Reconstruction: fixed within scan. The design does NOT rule out: the possibility that the score responds to any removed thoracic content - handled by the content regression, which is the identifiability core and must be adequately powered.",
      "alternative_explanations": "(1) Score drop reflects removed lung volume generically, not emphysema - separated by the regression contrast (low-%LAA truncations as controls). (2) Truncated volumes are subtly OOD despite loader compatibility - bounded by staying inside the empirical scan-start distribution and by a negative-control head (a purely abdominal phenotype, e.g. a renal code, should not respond to thoracic truncation). (3) The COPD head has near-zero signal on this external cohort and there is nothing to decode - bounded by a Stage 0 sanity check that the score distribution has variance and tracks basal %LAA cross-sectionally at all.",
      "anticipated_negative": "Decisive for the named X if gates pass: a flat dose-response against removed emphysema, inside the natural range, with the negative-control head behaving, means Merlin's COPD phenotype does not read the imaged lung bases - itself a striking, publishable statement given the cue is sitting in the scan. Gate failures are declared 'not testable', not negatives.",
      "cross_domain": null,
      "remaining_legwork": "Stage 0 loader inspection + scan-start census (~2-3 days); index-mapping trace (~1 day); inference over ~800 scan-variants on a single GPU (Merlin trains on one GPU; inference is light) (~2-3 days). First decision: ~1.5 weeks.",
      "scores": {
        "clarity": {"score": 4, "why": "One phenotype, one named cue, one intervention; slightly diffuse because 'COPD-family' spans four phecodes."},
        "identifiability": {"score": 4, "why": "Within-scan pairing plus content regression plus negative-control head; residual OOD risk is gated, not assumed away."},
        "medical_relevance": {"score": 4, "why": "Opportunistic COPD signal on abdominal CT is clinically actionable, and knowing the model reads real emphysema (vs abdominal correlates) determines whether to trust it."},
        "interest": {"score": 4, "why": "'The abdominal model is reading the chest' is surprising to exactly the audience the program serves."},
        "prior_legwork": {"score": 4, "why": "Everything public and documented; nothing yet run locally (unlike CT-CLIP)."},
        "feasibility": {"score": 4, "why": "INSPECTED_TRUE; single-GPU by the model's own design; public data."},
        "data_readiness": {"score": 4, "why": "All public, immediate; basal-lung inclusion rate uncounted."},
        "evaluation_readiness": {"score": 4, "why": "Paired deltas and regression contrasts; no custom metrics."},
        "negative_result_value": {"score": 4, "why": "Decisive conditional on gates; the flat result is itself informative."},
        "novelty_confidence": {"score": 3, "why": "No FOV-spillover probe of Merlin found; search limited."},
        "regret": {"score": 4, "why": "Cheap, novel grammar for the portfolio, obvious in hindsight."}
      },
      "priority_score": 3.95,
      "unverified_claims": [
        "Phenotype-head output indexing corresponds to phenotypes.csv row order (inferred; to be traced in released code).",
        "Merlin loader tolerance of variable z-extent (uninspected; Stage 0 gate, idea-006 procedure).",
        "Basal lung inclusion frequency in AMOS/TotalSegmentator scans (anatomically expected, uncounted).",
        "Merlin phenotype AUROC for phecode 496 specifically (paper reports macro averages; per-phenotype value not checked)."
      ]
    },
    {
      "id": "scout-012-c04",
      "search_mode": "C",
      "entry_point": 2,
      "title": "The non-gated chest CT contains an ECG: heart rate written in motion banding",
      "question": "Do CT-CLIP's cardiac heads use the patient's heart rate, read from the periodic motion banding a beating heart writes into a non-gated helical acquisition?",
      "design_template": "conditional-observational",
      "dataset": "CT-RATE (second and final CT-RATE candidate this cycle); TCIA gated collections only for validating the X-measurement",
      "entry_point_2_requirements": "Measurement: banding-wavelength-derived heart rate at the left cardiac border (construction below). Artifact it would be confused with: rotation time and pitch (protocol) set the sampling geometry - they are recorded in metadata and enter the formula rather than confounding it; respiratory motion and aortic pulsation are the confusable periodicities and must be separated by frequency band and location.",
      "rung": "Targets rung 1 only, and says so: establishing that a cardiac score covaries with banding-derived HR conditional on measured anatomy. Moving up requires an intervention (banding-smoothing edit) whose validity is a separate, harder project.",
      "deliverable_sentence": "The model is using the patient's heart rate, recorded in the scan as periodic cardiac motion banding.",
      "X_measurement": "A well-defined construction rather than an off-the-shelf tool (permitted by the charter): segment the heart (TotalSegmentator), track the left-heart border position slice-by-slice along z, take the spatial FFT of border displacement; the dominant banding frequency f_band, with table speed and gantry rotation period from acquisition metadata, yields an aliased candidate set of heart rates via beat-frequency arithmetic (stroboscopic sampling). Validate the construction once on gated cardiac CT collections where DICOM records HeartRate (0018,1088). Computable on an unseen scan without an annotator: YES, given acquisition metadata; the aliasing means HR is recovered as a small candidate set, honestly reported.",
      "suspected_signal": "Physiology, not electronics: tachycardia accompanies acute illness, heart failure, pericardial effusion. A model trained on image-report pairs has an incentive to use any image-visible correlate of clinical acuity; banding periodicity is exactly such a correlate, present in every non-gated chest CT and invisible-as-information to human readers, who file it under 'artifact'.",
      "use_vs_association": "This candidate honestly reaches association-with-named-competitors only: cardiac-head scores vs banding-HR conditional on measured chamber size, pericardial fluid, and effusion presence from the same scan. The one-line distinction: competitors are named, measured quantities from the same image, so a surviving partial association localizes the signal to the banding periodicity rather than to the anatomy the heads nominally measure. A banding-smoothing intervention is named as the upgrade path, not claimed.",
      "keystone_prerequisite": "What the inference needs: banding periodicity survives CT-RATE's released preprocessing (resampling to fixed spacing may low-pass it away), and acquisition metadata (rotation time, pitch/table speed) is present per volume to invert the formula.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": null,
      "keystone_residual_assumption": "The keystone above is already stated as the load-bearing fact (survival of banding through resampling), not the easy adjacent fact (that motion artifacts exist in chest CT, which is textbook). Additionally assumed: rotation time is in CT-RATE metadata (the Stage 0 record confirms rich acquisition metadata exists but I have not looked for RevolutionTime specifically); and that banding-HR has enough between-patient variance in a resting outpatient population.",
      "rung_reached": "1 at best this cycle, declared. Up: validated banding-smoothing edit (counterfactual with sham), or a cohort with recorded HR for direct anchoring.",
      "dies_like_prior": "Most resembles idea-007 (respiratory state), which survived by demoting its claim from mechanism-identification to state-sensitivity - this card starts at the demoted rung deliberately. No annotation-provenance dependence (no labels in the readout). The idea-006 OOD trap is avoided by not intervening at all this cycle.",
      "closest_prior_work": "Cardiac motion artifacts in non-gated CT are extensively documented as nuisance (coronary calcium scoring literature); I found no work extracting heart rate from banding periodicity as a signal, and no work asking whether any model uses it. Sanity check ('is it even recoverable?') has no published answer I could find - which is why the X-validation on gated data with recorded HR comes first. Absence of prior work is asserted from limited search.",
      "cross_domain": {
        "borrowed_construct": "Stroboscopic/aliased sampling (signal processing; rolling-shutter imaging): a rotating gantry samples a periodic motion, so the artifact pattern's spatial frequency encodes the beat frequency between heart rate and rotation rate.",
        "implied_measurement": "The FFT-of-border-displacement construction above, with the aliasing arithmetic that maps banding wavelength to an HR candidate set given rotation period and table speed.",
        "what_changes_if_dropped": "Everything: without the sampling-theory construct, banding is 'motion artifact', a nuisance with no formula, and there is no measurement to run. The analogy is not decoration; it is the instrument."
      },
      "existing_assets": "CT-RATE volumes + frozen metadata pipeline + working CT-CLIP scoring (probe 004); TotalSegmentator heart class; TCIA gated cardiac collections for X-validation (specific collection to be chosen; DICOM HR tag standard).",
      "smallest_decisive_experiment": "Phase 1 (X-validation, no model): on a gated collection with recorded HR, run the banding extractor on the non-gated-equivalent series and test recovery of HR within the aliased candidate set. Phase 2 (only if Phase 1 passes): on CT-RATE validation volumes, cardiomegaly/pericardial-effusion score vs banding-HR conditional on segmented cardiac volume and effusion measures.",
      "standing_confounds_addressed": "Protocol (rotation time/pitch): enters the formula from metadata, converted from confound to parameter; stratify by rotation time as a check. Scanner/vendor: 462/464 Siemens in the frozen subset - near-constant, stated as scope limit. Respiratory motion and aortic pulsation: separated by anatomical location (cardiac vs aortic border) and frequency band; imperfect, named. Habitus: noise floor of border tracking scales with image noise - conditioned. Prevalence/referral/label leakage: no labels in readout. NOT ruled out: HR correlates with true cardiac pathology the heads read directly from anatomy - the conditional design attenuates but cannot eliminate this; scored accordingly.",
      "alternative_explanations": "(1) Any surviving association reflects residual anatomical pathology imperfectly captured by the conditioning segmentations - the main threat, named, and the reason this is rung 1. (2) Banding amplitude (motion severity), not periodicity (rate), drives the score - distinguishable because amplitude and wavelength are separately measurable; test both. (3) The extractor measures noise - killed or confirmed by Phase 1 before the model is ever consulted.",
      "anticipated_negative": "Sensitivity-limited, declared: a Phase-1 failure (banding unrecoverable post-resampling) says nothing about the model; a Phase-2 null under a passing Phase 1 is evidence against use but bounded by conditioning quality. negative_result_value scored 2 accordingly.",
      "remaining_legwork": "Choose and download a gated collection with HR tags (~days); build the border-tracking extractor (~1 week); Phase 2 rides existing pipeline (~days). First decision (Phase 1): ~2 weeks.",
      "scores": {
        "mechanism_clarity": {"score": 5, "why": "A specific physiological quantity (heart rate), a specific physical encoding (beat-frequency banding), and an explicit formula with a validation dataset named."},
        "identifiability": {"score": 2, "why": "HR covaries with exactly the pathology the cardiac heads measure; conditioning on segmented anatomy attenuates but cannot sever this. Honest ceiling without an intervention."},
        "interest": {"score": 5, "why": "'The artifact is an instrument' - the strongest sounds-wrong-but-maybe-isn't question this cycle, and physicians would genuinely not expect it."},
        "medical_relevance": {"score": 3, "why": "If models read physiological state through artifacts, anatomical scores drift with acuity - a real deployment concern, one step removed from decisions."},
        "clarity": {"score": 4, "why": "Precise question; the aliasing candidate-set complication costs a point."},
        "feasibility_informational": {"score": 2, "why": "Capped by NOT_INSPECTED anyway; Phase 1 is genuinely uncertain."},
        "novelty_confidence_informational": {"score": 3, "why": "Nothing found on banding-as-signal; limited search; capped."},
        "negative_result_value_informational": {"score": 2, "why": "Sensitivity-limited as classified."}
      },
      "priority_score": 3.85,
      "priority_note": "Mode C weighting: 0.30*5 + 0.25*2 + 0.20*5 + 0.15*3 + 0.10*4 = 3.85; feasibility and novelty reported outside the score per rubric.",
      "unverified_claims": [
        "Banding periodicity survives CT-RATE resampling (the keystone; unknown).",
        "RevolutionTime/pitch present per-volume in CT-RATE metadata (acquisition metadata exists per Stage 0 record; these tags not specifically confirmed).",
        "A TCIA gated collection retains DICOM HeartRate tags after de-identification (standard tag, but de-id profiles vary).",
        "The beat-frequency formula as sketched (derived here; not yet checked against the CT physics literature on banding artifacts)."
      ]
    },
    {
      "id": "scout-012-c05",
      "search_mode": "C",
      "entry_point": 1,
      "title": "The prognosis model as a manometer: midline shift is pressure the skull wrote down",
      "question": "Does the head-CT TBI outcome model of Pease et al. use midline shift out of proportion to lesion volume - the Monro-Kellie signature of exhausted intracranial compliance - beyond the hemorrhage it can see directly?",
      "design_template": "conditional-observational",
      "dataset": "Anchor model's cohort (single-institution + TRACK-TBI) - access is the declared rate-limiter; CQ500 (public, has MLS/mass-effect reads but no outcomes) for X-measurement development only",
      "rung": "Targets rung 1 (the model uses shift-beyond-volume), honestly conditional on model access; rung 2 would need acquisition stratification within the anchor cohort; the rung-3 sentence is below and is already radiologist vocabulary.",
      "deliverable_sentence": "The model is using midline shift out of proportion to lesion volume - the image signature of exhausted intracranial compliance.",
      "X_measurement": "Midline shift in millimeters: automated as the deviation of the septum pellucidum / third ventricle from the ideal midline plane (skull-symmetry registration + ventricle segmentation; automated MLS algorithms are published and validated, e.g. the CQ500 line of work - specific tool to be pinned in feasibility). Lesion+edema volume: public intracranial hemorrhage segmentation models. The compliance construct is the residual of MLS regressed on lesion+edema volume - a formula, not a judgment. Computable on an unseen head CT today without an annotator: YES.",
      "suspected_signal": "Monro-Kellie: the cranium is a closed, fixed-volume vessel; CSF and venous buffering absorb early mass effect, so once shift grows disproportionate to lesion volume, compliance is exhausted and intracranial pressure is rising. Shift-conditional-on-volume is therefore a pressure state written in geometry - precisely the kind of physiological quantity an outcome-trained CNN would find, since ICP, not hemorrhage volume, is what kills.",
      "use_vs_association": "Association with named competitors, declared as such: model risk score vs automated MLS conditional on lesion+edema volume (and vs the interaction - shift per unit volume). A surviving conditional dependence localizes the signal to displacement rather than lesion burden; upgrading to use requires access to run the model on counterfactually warped inputs, named as future work, not claimed.",
      "keystone_prerequisite": "What the inference needs: the trained Pease et al. model (weights or scored outputs on a shareable cohort) is obtainable, since the claim is about what THAT documented-gap model uses; a re-trained substitute would change the claim's identity.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": null,
      "keystone_residual_assumption": "The keystone is already the load-bearing fact: model availability. Not inspected; probably not publicly released; the honest path is author correspondence or a hosted-inference arrangement, and this card accepts the caps that follow. Also assumed: automated MLS tools transfer to the anchor cohort's acquisition profile, and MLS variance conditional on volume is adequate in severe TBI (clinically expected - the shift-out-of-proportion patient is a recognized archetype - but unmeasured here).",
      "rung_reached": "1 conditional on access; without access, 0 - stated plainly. Up: counterfactual midline-restoring warps with sham-warp controls, if edit validity can be established in brain CT (a hard, separate problem).",
      "dies_like_prior": "Most resembles idea-018 (DATA_ACCESS kill: required model/data not obtainable) and says so upfront - the difference is only that this card declares access as its keystone from the start, requests correspondence as Stage 0, and stops if it fails rather than substituting a retrained model (which would repeat the idea-015 claim-identity error). No annotation-provenance issue: MLS and volumes are computed, not read; outcome labels (GOS) are trial-adjudicated, not image-derived.",
      "closest_prior_work": "Pease et al., Radiology 2022;304(2):385-394 (DOI 10.1148/radiol.212181, PMID 35471108): DL on admission head CT + clinical variables predicted 6-month outcome in severe TBI, evaluated against the IMPACT model and neurosurgeon predictions, with external TRACK-TBI validation - the documented gap. Their interpretability stopped at saliency-style inspection; no quantitative decomposition of the image signal into named radiological quantities. IMPACT itself uses human-read CT class (Marshall) - the model beating it while reading CT directly is exactly an undecoded signal.",
      "existing_assets": "Anchor paper with external validation; automated MLS literature; public ICH segmentation models; CQ500 (public) for building and sanity-checking the X pipeline against its expert MLS reads before any anchor-cohort contact.",
      "smallest_decisive_experiment": "Stage 0a: build the MLS+volume pipeline on CQ500 and check automated MLS against CQ500's released reads (tool validation, no model involved). Stage 0b: author correspondence for scored outputs or hosted inference. Then: variance decomposition of the model's image-derived risk into lesion volume, MLS, and MLS-conditional-on-volume.",
      "standing_confounds_addressed": "Scanner/protocol/site: anchor cohort is one institution + 18-site TRACK-TBI; stratify by site in the external set if access includes it. Positioning: head tilt corrupts naive MLS - the registration-based ideal-midline method addresses this and is why the tool must be validated first. Habitus/prevalence/referral: outcome model, single defined population (severe TBI admissions); referral homogeneous by definition. Label leakage: outcomes are 6-month GOS, not report-derived. NOT ruled out observationally: MLS correlates with everything severe (multiple lesions, cisternal effacement) - hence rung 1 and the named-competitor framing.",
      "alternative_explanations": "(1) The model reads cisternal effacement or other severity correlates and MLS merely tags along - partially separable by adding automated cistern volume to the competitor set; acknowledged residual. (2) The clinical-fusion pathway (GCS, pupils) carries the compliance information and the image contributes little - separable if the released design allows image-only scoring (the paper reports an image-only variant). (3) A null could reflect the model genuinely compressing everything into lesion burden - that is the decisive negative, and it is interesting: the celebrated model would be shown to ignore the quantity neurosurgeons act on.",
      "anticipated_negative": "Decisive for the named X given access and tool validation: if the image-derived score has no MLS-conditional-on-volume component, the model does not read the pressure signature - a clinically pointed finding. Without access, no experiment exists; that outcome is a feasibility result (idea-018 pattern), recorded and closed cheaply.",
      "cross_domain": {
        "borrowed_construct": "Closed-vessel mechanics / Monro-Kellie doctrine: in a rigid container, displacement out of proportion to added volume signals exhausted compliance and rising pressure.",
        "implied_measurement": "Not MLS alone but the residual of MLS on lesion+edema volume - shift per unit mass - as the pressure-state variable the model is tested against.",
        "what_changes_if_dropped": "Without the construct you would test 'model uses lesion size' or 'model uses MLS' marginally; the construct specifically predicts the conditional/residual term carries the outcome signal, which is a different regression and a different claim."
      },
      "remaining_legwork": "CQ500 pipeline build + validation (~1-2 weeks, fully public, zero model risk); correspondence (unbounded latency, cheap to initiate); analysis itself is days once scores exist. First decision point (Stage 0a tool validation) is independent of access and useful to two future candidates.",
      "scores": {
        "mechanism_clarity": {"score": 5, "why": "A named physiological quantity (intracranial pressure state via compliance), a physical law that predicts its geometric signature, and an explicit residual-regression measurement."},
        "identifiability": {"score": 3, "why": "MLS-vs-volume are separable in principle and clinically distinct in practice, but severity correlates (cisterns, multiplicity) remain partially entangled without intervention."},
        "interest": {"score": 4, "why": "A prognosis model shown to read the quantity surgeons actually act on would be the program's cleanest rung-3 story; the access risk is what keeps this from 5."},
        "medical_relevance": {"score": 5, "why": "ICP management is THE decision in severe TBI; a model that reads compliance is a model a neurosurgeon can reason with."},
        "clarity": {"score": 4, "why": "Precise conditional claim; loses a point for depending on which model variant (fusion vs image-only) access provides."},
        "feasibility_informational": {"score": 1, "why": "Model access unestablished and probably hard; capped and honestly low regardless."},
        "novelty_confidence_informational": {"score": 3, "why": "No decoding of TBI outcome models into named CT quantities found; limited search; capped."},
        "negative_result_value_informational": {"score": 3, "why": "Decisive if access exists; the access-failure outcome is only a feasibility note."}
      },
      "priority_score": 4.2,
      "priority_note": "Mode C weighting: 0.30*5 + 0.25*3 + 0.20*4 + 0.15*5 + 0.10*4 = 4.20; feasibility and novelty reported outside the score per rubric - the rubric explicitly forbids demoting Mode C for being hard, and the untestability escape hatch (Stage 0a is runnable today on public data) is what keeps this eligible.",
      "unverified_claims": [
        "Pease et al. model weights are not publicly released (presumed; not yet checked against the paper's data-availability statement).",
        "The paper reports an image-only model variant (recalled from search summary; must be verified in the full text).",
        "Automated MLS tool accuracy at CQ500-scale (published claims not yet read in primary form).",
        "CQ500 licensing permits this derivative use (public research release; terms not re-read this cycle)."
      ]
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

