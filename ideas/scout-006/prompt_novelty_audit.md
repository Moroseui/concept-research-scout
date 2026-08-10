You are a critical research collaborator working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-006
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

16 tracked ideas. Latest state per idea; full history in ledger.jsonl.

## Known failure modes (kill-code frequency)

Before proposing a candidate, check it against every pattern below.
A candidate that dies like a prior one must say what makes it different.

- **DATA_INSUFFICIENT** x1: The subset that actually supports the inference is too small or unreachable.

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
- **scout-006-c01** [SCOUT_ONLY/SCOUTED/baseline] -- Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan
- **scout-006-c02** [SCOUT_ONLY/SCOUTED/baseline] -- CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity
- **scout-006-c03** [SCOUT_ONLY/SCOUTED/baseline] -- An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver
- **scout-006-c04** [SCOUT_ONLY/SCOUTED/baseline] -- Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle
- **scout-006-c05** [SCOUT_ONLY/SCOUTED/baseline] -- An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two


===== ideas/scout-006/README.md =====
# Scouting cycle 006

Tracks: baseline


===== ideas/scout-006/candidates_all.json =====
{
  "cycle": 6,
  "tracks": [
    "baseline"
  ],
  "notes": {},
  "candidates": [
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
    },
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
    },
    {
      "id": "C3",
      "search_mode": "B",
      "entry_point": 2,
      "title": "An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver",
      "question": "When Merlin predicts diabetes mellitus from an abdominal CT, is its score mediated by hepatic steatosis - the mean Hounsfield attenuation of the liver - rather than by the visceral-fat and pancreatic signals it is usually assumed to use?",
      "deliverable_sentence": "Merlin is using hepatic steatosis: its diabetes score falls as mean liver attenuation falls, and liver attenuation mediates a measurable share of the diabetes signal independent of visceral fat.",
      "rung": {
        "current": 3,
        "why": "Hepatic steatosis / fatty liver is a named finding a radiologist reports; liver attenuation is its calibrated measurement.",
        "what_would_move_it_up": "Nothing above rung 3; strengthened by showing the mediation survives adjustment for visceral fat and pancreatic attenuation."
      },
      "X_measurement": {
        "X": "Mean liver attenuation in Hounsfield units on non-contrast CT (steatosis at <= 40 HU), with the liver-minus-spleen HU difference as a co-primary to reduce global-calibration drift.",
        "how": "TotalSegmentator free 'total' task segments liver and spleen; take mean HU inside each mask. No annotation.",
        "citations": "TotalSegmentator: Wasserthal et al., Radiol Artif Intell 2023;5(5):e230024. Steatosis threshold: liver mean attenuation <= 40 HU (non-contrast) and liver-spleen difference, per RSNA Radiology quantification reviews (radiol.241171; radiol.2021204288) and the classic Kodama-type population thresholds. Merlin diabetes output: Blankemeier et al., arXiv:2406.06512 (diabetes mellitus is one of the six named 5-year chronic-disease predictions).",
        "could_I_compute_it_today_without_asking_anyone": "Yes. Merlin weights are MIT and open; TotalSegmentator is open; liver HU is a masked mean.",
        "known_weakness_of_X_stated_up_front": "The <= 40 HU threshold is for NON-CONTRAST CT; Merlin's training corpus mixes contrast phases, and portal-venous enhancement raises liver HU by 30-50 HU, which would mask steatosis. Contrast phase must be detected (e.g., aortic/portal HU) and the analysis stratified or restricted to non-contrast; this is the live confound."
      },
      "suspected_signal": "Hepatic steatosis is the imaging hallmark of NAFLD, which sits on the insulin-resistance/type-2-diabetes axis, and fat lowers liver X-ray attenuation directly and proportionally (roughly -1.6 HU per 1% fat). So a diabetes predictor that has learned the metabolic-syndrome phenotype would encode low liver HU. A positive says Merlin found the fatty liver on its own and is using it to call diabetes.",
      "keystone_prerequisite": "Merlin emits a per-scan diabetes score that can be regressed against, and mediated through, liver attenuation on the SAME abdominal CT - and enough scans are non-contrast (or phase can be recovered) that liver HU is a valid steatosis measure rather than a contrast artefact.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "Merlin is released MIT with downloadable weights (HF stanfordmimi/Merlin; pip merlin-vlm) and its six explicit 5-year chronic-disease predictions include 'diabetes mellitus' (arXiv:2406.06512, INSPECTED). Its FOV is abdominal CT and it segments the liver and spleen among its 20 organs, so liver HU is computable on exactly the volumes it scores. TotalSegmentator liver/spleen masks are established for steatosis attenuation (Sci Rep 2024, s41598-024-62887-2). The diabetes-score-vs-liver-HU regression needs no ground-truth diabetes label, so it runs on any public abdominal CT set (AMOS, AbdomenAtlas, FLARE).",
      "keystone_residual_assumption": "Having verified Merlin predicts diabetes and images the liver, I am still assuming a supply of scans on which liver HU is a valid steatosis reading - i.e. non-contrast or phase-recoverable. Merlin was trained on a phase-mixed corpus; if the accessible public test scans are predominantly contrast-enhanced, liver HU is contaminated and the mediation is uninterpretable. This is load-bearing and checkable in Stage 0 by measuring aortic/portal HU to classify phase.",
      "rung_reached": {
        "value": 2,
        "conditional_on": "Mediation of the model's own diabetes score through liver HU is rung 1 (use) if liver HU carries score variance independent of visceral fat; the rung-3 SENTENCE is earned if the mediated share is non-trivial and survives adjustment for visceral fat and pancreatic attenuation. If liver HU's mediation vanishes once visceral fat is controlled, the claim drops to 'Merlin uses general adiposity'."
      },
      "use_vs_association": "Mediation analysis, not bare correlation: the diabetes score is decomposed into a part explained by liver HU and a part independent of it, with visceral fat and pancreatic HU as competing mediators, so 'uses steatosis' means liver HU carries UNIQUE score variance, not that steatosis happens to correlate with diabetes.",
      "dies_like_prior": "No prior kill applies - new organ system, new model, no human rating anywhere. The nearest concern is the scout-004 liver-dome question, which died on field-of-view truncation; that defect does NOT apply here because Merlin images the whole liver (abdominal CT), removing the coverage confound that sank the chest-CT version.",
      "closest_prior_work": [
        {
          "citation": "Blankemeier et al., Merlin.",
          "identifier": "arXiv:2406.06512 (Nature 2026, s41586-026-10181-8)",
          "verification": "INSPECTED (arXiv v1 HTML)",
          "what_it_did": "Trained the abdominal-CT VLM; predicts diabetes among six chronic diseases and 692 phenotypes.",
          "what_it_did_not_do": "Never named or probed hepatic steatosis / liver attenuation; 'steatosis', 'NAFLD', 'hepatic' absent from the text."
        },
        {
          "citation": "CT-IDP, 'Segmentation-Derived Quantitative Phenotypes for Interpretable Abdominal CT Disease Classification'.",
          "identifier": "arXiv:2605.09002",
          "verification": "SEARCH_SUMMARY_ONLY",
          "what_it_did": "Built hand-crafted segmentation phenotypes (including a hepatic-steatosis feature) and benchmarked them AGAINST Merlin (reported +0.156 on hepatic steatosis vs a ViT baseline).",
          "what_it_did_not_do": "Did not probe or mediate Merlin's internal reliance on liver attenuation - it is a competing pipeline, not an interpretability audit of the foundation model."
        }
      ],
      "existing_assets": [
        "Merlin weights (MIT, HF/pip).",
        "TotalSegmentator (Apache-2.0) for liver/spleen HU.",
        "Public abdominal CT sets (AMOS, AbdomenAtlas, FLARE) for the label-free primary readout.",
        "Established CT steatosis thresholds and a phase-classification heuristic (aortic/portal HU)."
      ],
      "smallest_decisive_experiment": "Stage 0 (2 days): classify phase on a public abdominal CT set via aortic/portal HU and confirm a usable non-contrast subset. Stage 1 (no labels): run Merlin's diabetes head and regress its score on liver HU (and liver-spleen HU); a using-steatosis model shows a monotone score gradient across liver-HU deciles. Stage 2 (mediation): decompose the score's variance through liver HU with visceral fat area and pancreatic HU as competing mediators; the identifying quantity is liver HU's unique mediated share.",
      "standing_confounds_addressed": {
        "scanner_and_vendor": "Covariate; public multi-site sets give diversity.",
        "acquisition_protocol": "CONTRAST PHASE is the dominant confound and is handled by phase classification and non-contrast restriction.",
        "reconstruction": "Kernel affects HU noise; covariate.",
        "site": "Addressable by using a multi-site public test set, unlike NLST.",
        "positioning": "Negligible for organ-mean HU.",
        "habitus": "Visceral fat is a competing mediator, explicitly measured, not just a nuisance.",
        "prevalence": "Diabetes prevalence differs by source cohort; the primary readout is score-vs-HU, not prevalence-dependent.",
        "referral_pathway": "Abdominal CT indication may correlate with both steatosis and diabetes; addressed as a limitation and partly by the within-scan mediation.",
        "label_leakage": "N/A - primary readout uses no diabetes label; the score is regressed on a voxel measurement."
      },
      "alternative_explanations": [
        "General adiposity / visceral fat, not liver fat specifically - the central alternative, attacked by including visceral fat area as a competing mediator.",
        "Pancreatic fat/atrophy, a second diabetes substrate visible on the same scan - included as a competing mediator.",
        "Contrast phase masquerading as steatosis (enhanced livers look 'non-fatty') - handled by phase stratification.",
        "The appealing 'the model reads the fatty liver' sentence would also arise from any metabolic-syndrome signal; only the unique mediated share of liver HU, net of visceral and pancreatic fat, supports it."
      ],
      "anticipated_negative": {
        "classification": "decisive",
        "reasoning": "If liver HU carries no unique mediated share of the diabetes score once visceral and pancreatic fat are controlled, it decisively excludes hepatic steatosis as Merlin's diabetes cue and points to generic adiposity - provided the non-contrast subset is adequately powered."
      },
      "cross_domain": null,
      "remaining_legwork": [
        "Assemble a phase-classified non-contrast abdominal CT subset: 3 days.",
        "Run Merlin + TotalSegmentator across it: 3 days.",
        "Mediation with competing mediators: 2 days.",
        "Time to first decision: ~2 weeks."
      ],
      "scores": {
        "clarity": {
          "value": 5,
          "why": "Names the model, the output, the biomarker, the tool and the two competing mediators."
        },
        "identifiability": {
          "value": 3,
          "why": "Mediation with competing mediators isolates liver HU's unique share, but contrast phase and the visceral/pancreatic-fat correlation are strong threats; held at 3."
        },
        "medical_relevance": {
          "value": 4,
          "why": "Says the abdominal model's diabetes signal is (partly) the fatty liver - clinically meaningful on the NAFLD-diabetes axis and relevant to opportunistic screening."
        },
        "interest": {
          "value": 4,
          "why": "A foundation model implicitly using a named metabolic biomarker it was never told to compute."
        },
        "prior_legwork": {
          "value": 5,
          "why": "Merlin open MIT, TotalSegmentator open, public abdominal CT sets, established thresholds."
        },
        "feasibility": {
          "value": 4,
          "why": "Cap lifted (INSPECTED_TRUE). Inference-only. Held by the phase-handling requirement."
        },
        "data_readiness": {
          "value": 4,
          "why": "Model open; abdominal CT test data public but needs phase filtering."
        },
        "evaluation_readiness": {
          "value": 4,
          "why": "Mediation, decile regression - standard; equivalence margin needed for the null."
        },
        "negative_result_value": {
          "value": 3,
          "why": "Decisive if adequately powered, but phase contamination could make a null sensitivity-limited; held at 3."
        },
        "novelty_confidence": {
          "value": 4,
          "why": "Cap lifted. No mediation/probe of Merlin through liver HU found; CT-IDP benchmarks but does not probe internals. Held at 4 for the crowded steatosis-from-CT space generally."
        }
      },
      "priority_score": 3.95,
      "priority_arithmetic": "0.20*4 + 0.15*3 + 0.15*4 + 0.10*5 + 0.10*4 + 0.10*5 + 0.10*3 + 0.05*4 + 0.05*4 = 0.80+0.45+0.60+0.50+0.40+0.50+0.30+0.20+0.20 = 3.95",
      "regret": {
        "value": 4,
        "why": "Open model, open tool, a whole-liver FOV that removes the truncation defect that killed the chest-CT version - a week of work sits between here and the answer."
      },
      "unverified_claims": [
        "A sufficiently large non-contrast abdominal CT subset with Merlin-scannable format is reachable (Stage 0).",
        "Merlin's diabetes head exposes a usable continuous score in the released weights (not only the 692-phenotype head).",
        "Exact steatosis threshold behaviour across the accessible cohort's scanners."
      ],
      "track": "baseline"
    },
    {
      "id": "C4",
      "search_mode": "C",
      "entry_point": 2,
      "title": "Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle",
      "question": "When Merlin predicts osteoporosis, is its score reading vertebral trabecular attenuation (opportunistic bone density in Hounsfield units) or vertebral wedge deformity (the Genant anterior-to-posterior height ratio), and does the deformity signal concentrate at the thoracolumbar junction as column-buckling mechanics predicts?",
      "deliverable_sentence": "Merlin is using vertebral wedge deformity - the Genant anterior-to-posterior height ratio - and it weights the thoracolumbar junction most, rather than reading uniform trabecular bone density.",
      "rung": {
        "current": 3,
        "why": "Both candidate X's are named radiological quantities: opportunistic BMD (trabecular HU) and vertebral compression/wedging (Genant). The deliverable names which one and where.",
        "what_would_move_it_up": "Nothing above rung 3; the spatial (thoracolumbar) prediction is what turns a correlation into a mechanistically specific claim."
      },
      "X_measurement": {
        "X": "Two competing, separately measured quantities: (a) trabecular attenuation = mean HU in an eroded vertebral-body core; (b) Genant wedge ratio = anterior height / posterior height per vertebra, graded 20/25/40% for mild/moderate/severe.",
        "how": "TotalSegmentator (or Merlin's own nnU-Net) segments individual vertebrae T12-L5; trabecular HU is a masked mean of an eroded core; wedge ratio is a geometric height computation per body. No annotation.",
        "citations": "Genant HK, Wu CY, van Kuijk C, Nevitt MC, J Bone Miner Res 1993;8(9):1137-1148, PMID 8237484 (semiquantitative wedge/biconcave/crush grading, 20/25/40% thresholds). TotalSegmentator vertebrae: Wasserthal et al., Radiol Artif Intell 2023;5(5):e230024. Merlin osteoporosis output: Blankemeier et al., arXiv:2406.06512 (osteoporosis is one of the six named chronic-disease predictions).",
        "could_I_compute_it_today_without_asking_anyone": "Yes. Both X's are geometric/densitometric computations on open vertebral masks; Merlin weights are open.",
        "known_weakness_of_X_stated_up_front": "Trabecular HU is moved by contrast phase, marrow fat and kernel; wedge ratio is robust to these but needs clean vertebral segmentation and endplate localisation, which degrade with severe deformity - exactly the cases of interest."
      },
      "suspected_signal": "Osteoporosis is DEFINED by low bone density (trabecular HU) but MANIFESTS as fragility fractures - anterior wedge collapse of vertebral bodies. Column-buckling mechanics (Euler) says a slender loaded column fails where compressive load and slenderness are greatest, which for the spine is the thoracolumbar junction (T12-L1), and the failure mode of an anteriorly-loaded vertebra is a wedge. So the mechanism names both a QUANTITY (wedge ratio) and a LOCATION (thoracolumbar) that a density-only reading would not privilege. Whether Merlin reads the cause (density) or the consequence (shape), and where, is the discriminating question.",
      "keystone_prerequisite": "Merlin emits a per-scan osteoporosis score that can be regressed against BOTH trabecular HU and Genant wedge ratio on the same vertebrae, AND the two quantities vary independently enough across scans to be dissociated - because low BMD causes wedge fractures, so they are correlated and a design that cannot separate them will credit whichever it measures first.",
      "keystone_status": "INSPECTED_TRUE",
      "keystone_evidence": "Merlin predicts osteoporosis explicitly (one of six 5-year chronic diseases, arXiv:2406.06512, INSPECTED) and segments T12-L5/S1 vertebrae (its 20-organ target list, INSPECTED), so both X's are computable on scans it scores. Weights MIT/open. Genant grading and TotalSegmentator vertebrae are established. The osteoporosis-output existence - the thing that makes the study possible - is INSPECTED_TRUE, which is why this Mode C candidate is not NOT_INSPECTED.",
      "keystone_residual_assumption": "Having verified Merlin has an osteoporosis output and segments the vertebrae, I am still assuming trabecular HU and wedge ratio VARY INDEPENDENTLY enough to dissociate - which is the real keystone and is NOT verified. Because osteoporosis couples them (low density -> fracture -> wedge), a cohort may show them collinear, in which case the headline dissociation is unidentifiable and the candidate retreats to 'Merlin uses vertebral bone signal' without saying which. This is the identical trap the charter names three times: 'both are measurable' is not 'both vary independently'. Stage 0 must estimate their joint distribution.",
      "rung_reached": {
        "value": 2,
        "conditional_on": "Regressing the model's own osteoporosis score against each X is rung 1; the rung-3 SENTENCE (naming wedging AND the thoracolumbar location) is earned only if the wedge ratio carries score variance independent of trabecular HU and the location weighting matches the mechanical prediction. If they are collinear, the honest claim is the coarser 'vertebral bone signal'."
      },
      "use_vs_association": "The osteoporosis score is decomposed against two competing measured X's simultaneously; 'uses wedging' means the wedge ratio carries UNIQUE score variance net of trabecular HU, and the pre-registered thoracolumbar spatial prediction is a second, independent identifying constraint that a mere density correlation would fail.",
      "dies_like_prior": "Resembles idea 011 (costal-cartilage age clock) as cross-domain skeletal reading, which is ACTIVE not killed; C4 differs by model (Merlin osteoporosis output, not an age model), by bone (vertebrae), and by using a two-X dissociation rather than a single recovered clock. No annotation-provenance issue. The one real inherited risk is the dissociation-identifiability trap, flagged above as the true keystone.",
      "closest_prior_work": [
        {
          "citation": "Blankemeier et al., Merlin.",
          "identifier": "arXiv:2406.06512",
          "verification": "INSPECTED",
          "what_it_did": "Predicts osteoporosis as one of six chronic diseases.",
          "what_it_did_not_do": "Never probed whether the osteoporosis signal is density or morphometry, nor where in the spine it sits."
        },
        {
          "citation": "Xu et al., explainable spine biological age.",
          "identifier": "GeroScience 2024, PMC11979066",
          "verification": "INSPECTED",
          "what_it_did": "Used anterior/posterior/mid height ratios (APR, MPR, PPR) across T4-L4 with SHAP to quantify spinal compression as an age signal.",
          "what_it_did_not_do": "A hand-crafted RF/LASSO model, NOT a probe of any learned CT foundation model; does not touch Merlin or osteoporosis output."
        },
        {
          "citation": "Kerber et al., deep-learning age estimation from thorax/abdomen CT.",
          "identifier": "PLoS One 2023, PMC10629654",
          "verification": "INSPECTED",
          "what_it_did": "Saliency highlighted the lumbar spine and abdominal aorta for age.",
          "what_it_did_not_do": "Stopped at 'lumbar spine'; never attributed the signal to wedging vs density and cautioned saliency is unreliable."
        }
      ],
      "existing_assets": [
        "Merlin weights (MIT).",
        "TotalSegmentator / Merlin nnU-Net vertebral masks.",
        "Genant protocol and published wedge thresholds.",
        "Xu et al.'s height-ratio definitions to reuse.",
        "Public abdominal CT sets for the label-free readout."
      ],
      "smallest_decisive_experiment": "Stage 0 (2 days): compute trabecular HU and wedge ratio on a public abdominal CT set and estimate their joint distribution - go/no-go for the dissociation. Stage 1: regress Merlin's osteoporosis score on each X separately, then jointly (partial contributions). Stage 2 (spatial test): weight the wedge signal by vertebral level and test the pre-registered prediction that the thoracolumbar junction dominates; a density-only model would show no such spatial concentration.",
      "standing_confounds_addressed": {
        "scanner_and_vendor": "Covariate; multi-site public data helps.",
        "acquisition_protocol": "Contrast phase moves trabecular HU (not wedge ratio) - handled by phase stratification; the wedge arm is phase-robust.",
        "reconstruction": "Kernel affects HU; covariate.",
        "site": "Addressable via multi-site public data.",
        "positioning": "Spinal curvature/lordosis affects apparent wedge; measured per-vertebra in the local frame to reduce this.",
        "habitus": "Body size affects HU noise; covariate.",
        "prevalence": "Score-vs-X readout is not prevalence-dependent.",
        "referral_pathway": "Indication may correlate with fracture burden; limitation.",
        "label_leakage": "N/A - no osteoporosis label enters the primary readout."
      },
      "alternative_explanations": [
        "Trabecular density (the definitional cause), not shape - the central competing X, which is exactly why it is measured head-to-head.",
        "Degenerative change (osteophytes, disc-space loss) co-located with wedging - a covariate that could inflate the morphometry signal; addressed by restricting height measurement to the vertebral body.",
        "Collinearity of density and wedging makes the dissociation vacuous - the true keystone risk, checked in Stage 0.",
        "The Euler/thoracolumbar story is attractive; if the dissociation is unidentifiable, the spatial arm must not be over-read as confirming a mechanism it cannot isolate."
      ],
      "anticipated_negative": {
        "classification": "sensitivity-limited",
        "reasoning": "If wedge ratio and trabecular HU are collinear in the accessible cohort, a null on the dissociation reflects the cohort's joint distribution, not the model - so it needs the Stage-0 independence estimate and a minimum-detectable partial effect to be interpretable. A clean result requires a cohort with genuine density-shape decoupling (e.g., low-BMD but un-fractured spines)."
      },
      "cross_domain": {
        "borrowed_construct": "Euler buckling of a slender loaded column from structural mechanics.",
        "measurement_it_implies": "Weight the wedge-deformity signal by vertebral level and predict thoracolumbar (T12-L1) dominance and an anterior (wedge) failure mode, rather than uniform height loss.",
        "what_would_change_if_dropped": "Without the analogy you would still measure the Genant wedge ratio (standard radiology), but you would have no principled prediction about WHERE the signal should live; the mechanics converts a generic 'measure the spine' into a pre-registered spatial test (thoracolumbar predominance) that a density-only reading fails. That specific, falsifiable location claim is what the analogy earns - it is not decoration."
      },
      "remaining_legwork": [
        "Stage 0 joint-distribution check: 2 days.",
        "Vertebral segmentation QC and endplate localisation: 3 days.",
        "Merlin osteoporosis-score extraction + regressions: 3 days.",
        "Time to first decision: ~2 weeks; a decoupled cohort may need sourcing, extending it."
      ],
      "scores": {
        "mechanism_clarity": {
          "value": 4,
          "why": "Two named physical quantities and their measurements, plus a mechanically-derived spatial prediction. Below 5 because Euler is mechanism motivation the wedge ratio does not strictly need."
        },
        "identifiability": {
          "value": 4,
          "why": "Two-X dissociation plus an independent spatial constraint; held below 5 by the density-wedge collinearity that is the true keystone."
        },
        "interest": {
          "value": 4,
          "why": "Whether a model reads a disease by its cause (density) or its consequence (fracture shape), and where, is a sharp and general question."
        },
        "medical_relevance": {
          "value": 4,
          "why": "Distinguishes opportunistic BMD from morphometric fracture detection inside one score - relevant to how the osteoporosis output should be trusted and used."
        },
        "clarity": {
          "value": 5,
          "why": "One sentence names the model, both quantities, and the location claim."
        }
      },
      "priority_score": 4.1,
      "priority_arithmetic": "Mode C weighting: 0.30*4 (mechanism) + 0.25*4 (ident) + 0.20*4 (interest) + 0.15*4 (med) + 0.10*5 (clarity) = 1.20+1.00+0.80+0.60+0.50 = 4.10",
      "feasibility_for_information": {
        "value": 3,
        "why": "Inference-only and open tools, but the identifying cohort (density-shape decoupled) may need sourcing, and severe-deformity segmentation is fragile. Cap would allow higher given INSPECTED_TRUE, but the sourcing risk holds it at 3."
      },
      "novelty_confidence_for_information": {
        "value": 4,
        "why": "No probe of Merlin's osteoporosis signal for density-vs-morphometry found; the wedge-age link exists only as hand-crafted features (Xu) and the region only as saliency (Kerber). The Euler-buckling-to-foundation-model framing appears novel."
      },
      "regret": {
        "value": 3,
        "why": "A clean, legible dissociation sitting on an open model; discounted because the collinearity risk could make it uninterpretable without a special cohort."
      },
      "unverified_claims": [
        "Trabecular HU and wedge ratio vary independently enough in an accessible cohort (the true keystone; Stage 0).",
        "Merlin's osteoporosis head exposes a usable continuous score in the released weights.",
        "Vertebral segmentation is reliable on osteoporotic/deformed bodies.",
        "The Euler thoracolumbar prediction is the right one for supine CT loading (biomechanics literature exists but the supine-imaging load state is assumed)."
      ],
      "track": "baseline"
    },
    {
      "id": "C5",
      "search_mode": "C",
      "entry_point": 2,
      "title": "An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two",
      "question": "When CT-CLIP fires 'Bronchiectasis', is the score a function of the bronchoarterial ratio - airway luminal diameter divided by the diameter of the accompanying pulmonary artery - rather than of absolute airway calibre, which is confounded by lung and body size?",
      "deliverable_sentence": "CT-CLIP is using the bronchoarterial ratio - the airway widened relative to its accompanying artery - and not merely the absolute size of the airway.",
      "rung": {
        "current": 3,
        "why": "The bronchoarterial ratio is the radiological definition of bronchiectasis - a named finding.",
        "what_would_move_it_up": "Nothing above rung 3; the absolute-vs-ratio contrast is what makes it the named finding rather than 'big airways'."
      },
      "X_measurement": {
        "X": "Bronchoarterial ratio (BAR) = airway inner luminal diameter / diameter of the immediately adjacent pulmonary artery, at matched airway generations; BAR > 1 is the conventional bronchiectasis threshold. Absolute luminal area is the competing X.",
        "how": "Segment the airway lumen and the pulmonary arteries, pair each airway with its accompanying artery along the bronchovascular bundle, and take the diameter ratio. Requires an airway segmenter (e.g., open ATM-challenge models) plus a pulmonary-vessel segmenter.",
        "citations": "BAR definition and threshold: standard Fleischner/thoracic imaging criteria for bronchiectasis (signet-ring sign, BAR > 1). Airway segmentation baselines: ATM'22 challenge models. CT-CLIP bronchiectasis label: Hamamci et al., arXiv:2403.17834 (label #17).",
        "could_I_compute_it_today_without_asking_anyone": "Partly - airway and vessel segmenters are open, but pairing airways to arteries and measuring lumen diameters on NON-CONTRAST CT is a research pipeline, not a one-command tool. This is the weakest measurement channel in the portfolio and is why the candidate is Mode C.",
        "known_weakness_of_X_stated_up_front": "Non-contrast CT-RATE gives poor pulmonary-artery lumen edges (no contrast), and TotalSegmentator's free task does not segment the pulmonary artery, so the artery side of the ratio must come from a vessel-segmentation model on non-contrast data - noisy. Slice thickness up to 6 mm blurs small peripheral airways where bronchiectasis is graded."
      },
      "suspected_signal": "An airway and its accompanying pulmonary artery travel together in the bronchovascular bundle and, in health, co-scale so their diameters are roughly matched (BAR ~ 0.65-1.0). Bronchiectasis is airway dilation OUT OF PROPORTION to the artery - traction, inflammation and wall destruction widen the lumen while the artery does not follow. So the disease is a broken ratio, not an absolute size. A model that has learned the finding rather than a size proxy will track BAR.",
      "keystone_prerequisite": "A per-scan bronchoarterial ratio can be computed reliably on non-contrast CT-RATE volumes and regressed against CT-CLIP's bronchiectasis score, with the ratio separable from absolute airway calibre - because if only absolute calibre is measurable (artery side too noisy on non-contrast CT), the design cannot show the model uses the RATIO rather than size.",
      "keystone_status": "NOT_INSPECTED",
      "keystone_evidence": "CT-CLIP's bronchiectasis label is confirmed (arXiv:2403.17834, label #17). But the load-bearing fact - that a reliable per-scan BAR is computable on non-contrast, up-to-6mm-slice CT-RATE volumes with an open pipeline - was NOT inspected and is genuinely uncertain. Per the charter, a Mode C candidate may honestly report NOT_INSPECTED and accept the feasibility/novelty caps.",
      "keystone_residual_assumption": "Even if airway and vessel segmenters run, I am assuming the ARTERY side of the ratio is measurable on non-contrast CT well enough to make BAR more than noise around absolute airway size. If it is not, the whole point (ratio, not size) collapses and the candidate reduces to 'the model uses big airways', which does not identify the named finding.",
      "rung_reached": {
        "value": 1,
        "conditional_on": "Even a positive score-vs-BAR association is rung 1 (use of an airway-size feature) until the ratio is shown to beat absolute calibre; the rung-3 SENTENCE needs BAR to carry score variance independent of absolute luminal area, which the non-contrast measurement may not support."
      },
      "use_vs_association": "Absolute calibre and BAR are entered together; 'uses the ratio' means BAR carries score variance net of absolute luminal area - otherwise the model is using airway size, and the ratio framing is unsupported.",
      "dies_like_prior": "No prior kill applies directly - it uses no human ratings and no deletion intervention. Its risk is not a prior failure MODE but feasibility: the measurement channel may be too weak on non-contrast CT, which is the honest reason it is the lowest-scored Mode C candidate rather than a Mode B.",
      "closest_prior_work": [
        {
          "citation": "Hamamci et al., CT-CLIP.",
          "identifier": "arXiv:2403.17834",
          "verification": "INSPECTED",
          "what_it_did": "Reports a bronchiectasis ClassFine score.",
          "what_it_did_not_do": "Never related it to a bronchoarterial-ratio measurement."
        },
        {
          "citation": "ATM'22 airway segmentation challenge and follow-ups.",
          "identifier": "airway-segmentation literature",
          "verification": "SEARCH_SUMMARY_ONLY",
          "what_it_did": "Open airway-tree segmentation models.",
          "what_it_did_not_do": "Not paired with pulmonary-artery matching for BAR on non-contrast foundation-model corpora, and not linked to any model's score."
        }
      ],
      "existing_assets": [
        "CT-CLIP bronchiectasis score (gated-free CT-RATE).",
        "Open airway and pulmonary-vessel segmentation models.",
        "Standard BAR definition and threshold."
      ],
      "smallest_decisive_experiment": "Stage 0 (go/no-go, 1 week): on a handful of CT-RATE volumes, test whether an open airway+vessel pipeline yields a stable BAR on non-contrast data (reproducibility across kernels/thicknesses). Only if BAR is stable: Stage 1 regresses CT-CLIP's bronchiectasis score on BAR and on absolute luminal area jointly; the identifying quantity is BAR's unique contribution.",
      "standing_confounds_addressed": {
        "scanner_and_vendor": "Covariate.",
        "acquisition_protocol": "Non-contrast throughout; the artery-edge problem is protocol-driven and is the core feasibility risk.",
        "reconstruction": "Kernel and slice thickness strongly affect airway-wall/lumen measurement; covariate and reproducibility-gated in Stage 0.",
        "site": "Limited in CT-RATE; limitation.",
        "positioning": "Minor.",
        "habitus": "BAR is designed to normalise body/lung size - that is the point of the ratio.",
        "prevalence": "Score-vs-X readout not prevalence-dependent.",
        "referral_pathway": "Indication may correlate with airway disease; limitation.",
        "label_leakage": "N/A - no label in the primary readout."
      },
      "alternative_explanations": [
        "Absolute airway calibre / lung size, not the ratio - the central alternative, attacked by entering both.",
        "Mucus plugging or wall thickening co-occurring with dilation - could drive the score independently of BAR; a covariate.",
        "Measurement noise on the artery side mimicking or masking a ratio effect - the feasibility keystone.",
        "The elegant 'broken co-scaling' story must not survive if BAR proves unmeasurable; then the honest claim is airway size."
      ],
      "anticipated_negative": {
        "classification": "uninterpretable",
        "reasoning": "Given the NOT_INSPECTED measurement keystone, a null could mean the model ignores BAR OR that BAR was too noisy to detect on non-contrast CT - several explanations survive. This is honestly an uninterpretable-null risk unless Stage 0 first establishes BAR reliability, which caps negative-result value."
      },
      "cross_domain": {
        "borrowed_construct": "Allometric co-scaling of two parallel transport conduits (an airway and its pulmonary artery in the bronchovascular bundle), a Murray-law-adjacent diameter-matching principle.",
        "measurement_it_implies": "Use the airway-to-artery diameter RATIO with the paired artery as an internal normaliser, rather than absolute airway diameter.",
        "what_would_change_if_dropped": "Without the co-scaling principle you would measure absolute airway calibre, which is confounded by lung and body size; the paired-tube view says use the accompanying artery as the internal ruler - which is exactly the radiological BAR and removes the size confound. The analogy earns the ratio (and its internal normalisation), not just a metaphor - dropping it changes the measurement from absolute to relative."
      },
      "remaining_legwork": [
        "Stage 0 BAR-reproducibility test on non-contrast CT-RATE: 1 week (this is the whole gamble).",
        "If stable: Stage 1 regressions: 1 week.",
        "Time to first decision: ~2-3 weeks, front-loaded on the feasibility check."
      ],
      "scores": {
        "mechanism_clarity": {
          "value": 4,
          "why": "Named quantity (BAR) with a clear physical mechanism (disproportionate airway dilation) and a specific measurement. Below 5 because the artery-side measurement is uncertain."
        },
        "identifiability": {
          "value": 3,
          "why": "Entering BAR against absolute calibre would isolate the ratio, but non-contrast artery-edge noise threatens the discrimination; held at 3."
        },
        "interest": {
          "value": 3,
          "why": "A neat 'does the model use the defining ratio' question, but narrower and more measurement-fragile than the others."
        },
        "medical_relevance": {
          "value": 3,
          "why": "Confirms whether a bronchiectasis label means the defining finding; useful but modest."
        },
        "clarity": {
          "value": 4,
          "why": "Clear question; slightly softened by the measurement uncertainty baked into it."
        }
      },
      "priority_score": 3.4,
      "priority_arithmetic": "Mode C weighting: 0.30*4 (mechanism) + 0.25*3 (ident) + 0.20*3 (interest) + 0.15*3 (med) + 0.10*4 (clarity) = 1.20+0.75+0.60+0.45+0.40 = 3.40",
      "feasibility_for_information": {
        "value": 2,
        "why": "NOT_INSPECTED keystone; the BAR pipeline on non-contrast, thick-slice CT is the real risk and could fail Stage 0. Capped at <=3 and set to 2."
      },
      "novelty_confidence_for_information": {
        "value": 3,
        "why": "No prior link of a foundation model's bronchiectasis score to BAR found, but airway quantification is a worked field and the specific gap was not exhaustively searched; capped at 3 (NOT_INSPECTED)."
      },
      "regret": {
        "value": 2,
        "why": "If it works it is a clean legible sentence, but the feasibility risk is high enough that little is lost by deferring it until the measurement is shown to be stable."
      },
      "unverified_claims": [
        "A reliable per-scan BAR is computable on non-contrast CT-RATE volumes (the keystone; Stage 0).",
        "Open airway+vessel segmenters transfer to CT-RATE's non-contrast, up-to-6mm-slice data.",
        "CT-CLIP's bronchiectasis score has enough dynamic range to regress against a continuous ratio."
      ],
      "track": "baseline"
    }
  ]
}


===== ideas/scout-006/scout_candidates.json =====
{
  "cycle": "scout-006",
  "stage": "scout",
  "generated_on": "2026-08-10",
  "tracks": ["baseline"],
  "charter_version_seen": "CHARTER.md / prompt_scout.md as injected this cycle (rung 3 as deliverable; X must be machine-measurable without a human annotator; keystone must be stated as the thing the inference needs).",

  "evidence_standard": {
    "INSPECTED": "The primary artifact was opened this session (arXiv/PMC full text, HuggingFace file tree, GitHub repo/README, or a paper's Results/Methods) and text is quoted or a specific field is named.",
    "SEARCH_SUMMARY_ONLY": "The claim came from a search engine's synthesis or an abstract-level record, not the primary page opened directly. Treated as unverified and flagged.",
    "NOT_FOUND": "Searched and not located; queries recorded. Not proof of absence."
  },

  "method_note": "Keystone verification ran before development, via three parallel source-checks (CT-RATE/CT-CLIP; Sybil+CAC; Merlin+abdominal CT), and it changed the portfolio three times. (1) CT-CLIP has NO aorta-diameter and NO pulmonary-artery/pulmonary-hypertension label among its 18 abnormalities, and TotalSegmentator's free Apache-2.0 task does not segment the pulmonary artery (that is behind the license-gated heartchambers_highres subtask) - this killed the aortic-diameter question (Q6) and the PA:A question (Q10) as 'the model is using X for X's own output' designs. (2) CT-CLIP DOES carry two verbatim labels, 'Arterial wall calcification' and 'Coronary artery wall calcification', which converted a weak vascular-geometry probe into a strong calcification-fidelity-and-localization design (C2), because AI-CAC (MIT, downloadable weights) supplies coronary calcium and the TotalSegmentator aorta mask supplies aortic calcium, so the two labels can be dissociated. (3) Merlin does NOT predict chronological age and does NOT name steatosis as a target (searched full text - 'age', 'steatosis', 'NAFLD', 'hepatic' absent), so the age-clock framing was dropped and both Merlin candidates were re-anchored on outputs Merlin explicitly HAS: its diabetes-mellitus prediction (C3) and its osteoporosis prediction (C4), each of which has a named, machine-measurable abdominal biomarker as the suspected cue.",

  "prior_cycle_review": {
    "records_read": [
      "evidence/decisions.md (full, as injected)",
      "evidence/ledger_digest.md (kill-code table and all 11 tracked ideas)",
      "ideas/scout-004/scout_candidates.json (full schema and C1/C2 in depth, as the template)",
      "ideas/scout-005/candidates_all.json (empty - scout-005 produced no candidate file)"
    ],
    "use_vs_association_note": "Cycle-one lesson: USE_VS_ASSOCIATION killed nine of eleven first-cycle ideas. Every candidate below carries a one-line statement of how its design separates 'the model uses X' from 'X merely correlates with the label'. The honest reading is that a score-versus-biomarker regression is ASSOCIATION, and reaches rung 1 (use) only with a controlled perturbation or a partialling design that isolates X from its correlated neighbours. C1, C3 and C4 buy this with partial-association or mediation designs plus, where available, a free in-distribution perturbation (the paired reconstruction kernel). C2's primary is a fidelity regression whose 'use' interpretation is underwritten by the fact that the score IS the model's own calcification output, so a monotone dependence on measured calcium is use by construction, not correlation with an external label.",
    "structural_lesson_applied": "The one candidate that survived this loop (idea 004) removed labels from its primary readout. All five here do the same: every primary readout regresses a model's own continuous output against a quantity computed from the same voxels by a released tool. No human-assigned label enters any primary readout. CT-RATE's RadBERT report labels and NLST/registry outcomes appear only in optional confirmatory arms.",
    "interventions_are_in_distribution": "Idea 006 died because a constant-filled body deletion was extreme OOD. Nothing here blanks, masks, inpaints or deletes anatomy. The only manipulation used anywhere is the paired reconstruction-kernel swap (C1 optional arm), which is two real reconstructions the scanner produced from one acquisition - both images in-distribution.",
    "dominant_failure_watch": {
      "annotation_provenance": "Five of six prior kills needed to know who assigned a label and what they could see. NONE of these candidates use a human rating as a measurement. Every X is a voxel computation (Agatston by AI-CAC; calcium HU inside an aorta mask; liver mean HU; Genant wedge ratio and trabecular HU from vertebral masks; bronchoarterial ratio). The models' own outputs are the other side of each comparison.",
      "wrong_keystone": "Occurred three times (the easy adjacent fact verified, the load-bearing one assumed). For each candidate the keystone is written below as the thing the INFERENCE needs, followed by keystone_residual_assumption naming what is still assumed after checking the nearest thing. The sharpest residual this cycle is C2's and C4's: a dissociation design is only identifiable if the two candidate cues vary independently, which is NOT the same as verifying that both cues are measurable."
    }
  },

  "all_questions": [
    {"n": 1, "q": "On low-dose CT scans with no visible nodule at the future cancer site, where Sybil still reaches a 2-year AUC of 0.81, is its residual risk score a function of coronary artery calcium - the automated Agatston score computed on the same scan?", "status": "DEVELOPED as C1", "note": "X is a word a radiologist already has: coronary calcification. Third named competing explanation for Sybil's documented residual, alongside emphysema (idea 008) and vascular pruning (idea 009)."},
    {"n": 2, "q": "When CT-CLIP fires its 'Coronary artery wall calcification' label, is the score a monotone function of automated coronary Agatston, and does it dissociate from aortic-wall calcium measured in the same volume - i.e. does the model localise calcium or merely detect hyperdensity?", "status": "DEVELOPED as C2", "note": "X: coronary calcium. Uses CT-CLIP's own two calcification labels as a natural localisation experiment."},
    {"n": 3, "q": "When the abdominal foundation model Merlin predicts diabetes mellitus, is its score mediated by hepatic steatosis - the mean Hounsfield attenuation of the liver?", "status": "DEVELOPED as C3", "note": "X is a word a radiologist already has: fatty liver / hepatic steatosis. Merlin predicts diabetes explicitly; steatosis is the visible NAFLD-insulin-resistance substrate."},
    {"n": 4, "q": "When Merlin predicts osteoporosis, is its score reading vertebral trabecular attenuation (opportunistic bone density in Hounsfield units) or vertebral wedge deformity (the Genant anterior-to-posterior height ratio), and does the failure concentrate at the thoracolumbar junction as column-buckling mechanics predicts?", "status": "DEVELOPED as C4", "note": "Cross-domain: structural mechanics (Euler buckling of a loaded column). X: two competing, separately measurable skeletal quantities."},
    {"n": 5, "q": "When CT-CLIP fires 'Bronchiectasis', is the score a function of the bronchoarterial ratio - airway luminal diameter divided by the diameter of its accompanying pulmonary artery - rather than absolute airway calibre?", "status": "DEVELOPED as C5", "note": "Cross-domain: allometric co-scaling of two parallel transport conduits. X: bronchoarterial ratio, the radiological definition of bronchiectasis."},
    {"n": 6, "q": "Does a frozen chest-CT foundation model's embedding linearly encode ascending aortic diameter, and does that representation drive any of its finding outputs?", "status": "DROPPED", "why_dropped": "CT-CLIP has no aorta-diameter output label (verified: none among the 18 abnormalities), so 'the model is USING aortic diameter' has no output to be used FOR - the best achievable answer is 'the representation encodes aortic diameter', which is presence-in-representation, not use, and a weak deliverable sentence."},
    {"n": 7, "q": "Does a COPD or lung-cancer risk model read the fractal dimension - the branching complexity - of the segmented airway tree?", "status": "DROPPED", "why_dropped": "Fractal dimension is not a word a radiologist has; the deliverable sentence would fail the human-legibility test at rung 3. Also the classic fluent-nonsense risk: dropping the fractal analogy leaves you measuring airway calibre and count, which is what C5 does with a legible ratio. Kept as one of the two required cross-domain questions but not developed."},
    {"n": 8, "q": "Does a chest-CT model's score for a thoracic finding depend on splenic volume visible at the base of the scan?", "status": "DROPPED", "why_dropped": "This is the obviously-wrong-sounding entry and I could not immediately refute it (spleen is in most chest-CT fields of view; splenomegaly tracks portal hypertension and haematologic disease; splenic volume is a clean TotalSegmentator measurement). Dropped on measurement and interest rather than plausibility: caudal extent of a chest CT varies, so the spleen is truncated in exactly the scans where the claim would matter, confounding the exposure with the field of view - the same defect that sank the liver-dome question in scout-004."},
    {"n": 9, "q": "Does an opportunistic chest-CT age or mortality model read vertebral trabecular attenuation - opportunistic bone mineral density?", "status": "DROPPED", "why_dropped": "Folded into C4 as the competing X. Standalone it is confounded (trabecular attenuation is moved by steroids, marrow fat, contrast, and disease) and less identifiable than the C4 dissociation, which pits trabecular density against morphometric wedging inside one output."},
    {"n": 10, "q": "When a chest-CT model reports pulmonary hypertension or a related outcome, is its score using the pulmonary-artery-to-aorta diameter ratio (PA:A)?", "status": "DROPPED", "why_dropped": "Two keystones fail at once: CT-CLIP has no pulmonary-hypertension or PA output label, and TotalSegmentator's free Apache-2.0 task does NOT segment the pulmonary artery (only the license-gated heartchambers_highres subtask does, and the maintainers flag it as less robust), while non-contrast CT-RATE volumes give poor PA lumen edges. The measurement channel is the weakest in the set."}
  ],

  "quota_compliance": {
    "search_mode_A": ["C1"],
    "search_mode_B": ["C2", "C3"],
    "search_mode_C": ["C4", "C5"],
    "quota_status": "MET exactly: 1 Mode A, 2 Mode B, 2 Mode C.",
    "entry_point_1": ["C1"],
    "entry_point_2": ["C2", "C3", "C4", "C5"],
    "radiology_or_CT": "5 of 5 (minimum 3). C1, C2, C5 chest CT; C3, C4 abdominal CT.",
    "dermatology": "0 of 5 (maximum 1). Not padded - no dermatology candidate was worth writing, and the two open PAUSED derm-adjacent leads (idea 002) remain blocked on annotation provenance.",
    "dataset_concentration": "NLST x1 (C1); CT-RATE x2 (C2, C5); Merlin/abdominal-CT x2 (C3, C4). At the cap of 2 on two datasets, not over.",
    "keystone_inspected_true": ["C1", "C2", "C3", "C4"],
    "keystone_not_inspected": ["C5"],
    "quota_note": "Four honest disclosures. (1) THEMATIC CONCENTRATION ON CALCIUM: C1 and C2 are both about coronary calcium. They are genuinely different questions on different datasets and models - C1 asks what an unlabelled residual signal IS (discovery), C2 asks whether a model's own calcification label is faithful and localised (fidelity) - but a funder should know the portfolio has two calcium bets and can hedge by running one. (2) C2 RESEMBLES IDEA 010 in method (regress a CT-CLIP finding score against a machine measurement); its distinct contribution is the coronary-versus-aortic localisation dissociation, which idea 010 (heart volume) has no analogue for. (3) MERLIN CONCENTRATION: C3 and C4 share the Merlin encoder and an abdominal-CT test set but nothing else - different outputs (diabetes vs osteoporosis), different biomarkers (liver HU vs vertebral morphometry), and they fail independently. (4) C5 is the only NOT_INSPECTED keystone and the only sub-3 feasibility; it is a Mode C candidate whose measurement pipeline (paired airway-and-artery segmentation on NON-CONTRAST CT) is genuinely uncertain, which is exactly what Mode C is for."
  },

  "portfolio_ranking": {
    "by_priority_score": "Mode A/B: C1 4.20, C2 3.95, C3 3.95. Mode C (different weighting, not commensurable): C4 4.10, C5 3.40.",
    "caution_on_comparing_across_modes": "Mode C scores use the mechanism-weighted formula and omit feasibility, data readiness, prior legwork and negative-result value entirely. C4's 4.10 is NOT evidence it beats C1's 4.20. Compare C1/C2/C3 among themselves; compare C4/C5 among themselves.",
    "recommendation_if_one": "C1. It attacks a documented, quantified model-beats-human gap (Sybil's nodule-free 2-year AUC 0.81, verbatim confirmed) with two fully open tools (Sybil MIT, AI-CAC MIT) and public imaging and outcomes, and it completes the residual-signal decomposition that ideas 008 and 009 began - the three should be run together because their candidate cues (emphysema, vessels, calcium) co-vary and only a joint partial-association design separates them.",
    "recommendation_if_two": "C1 and C3. They share no dataset, model, biomarker or failure mode; C3 opens a second organ system (abdomen/metabolic) and a second open foundation model (Merlin), and its diabetes-through-steatosis mediation is a clean, legible sentence a physician can dispute."
  },

  "candidates": [
    {
      "id": "C1",
      "search_mode": "A",
      "entry_point": 1,
      "title": "Two papers say Sybil's residual is the background and name emphysema; neither measured the heart calcium sitting in the same scan",

      "question": "On low-dose CT scans with no visible nodule at the site of the subsequent cancer, where Sybil still reaches a 2-year AUC of 0.81, is its risk score a function of coronary artery calcium - the automated Agatston score computed by AI-CAC on the same scan - after adjustment for the emphysema and vascular measures that are its two rival explanations?",

      "deliverable_sentence": "Sybil is using coronary artery calcium: on nodule-free screening scans its risk score rises with the automated Agatston score, and it does so over and above quantitative emphysema and small-vessel blood volume.",

      "rung": {"current": 3, "why": "Coronary calcification is a named finding a radiologist reports by name, quantified in calibrated units by a released tool. It is not a region and not an absence.", "what_would_move_it_up": "Nothing sits above rung 3. What strengthens the rung-3 claim: the partial-association survives adjustment for pack-years and for the two rival cues, and it holds within the paired-kernel perturbation arm."},

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

      "rung_reached": {"value": 2, "conditional_on": "The design as primary is an ASSOCIATION between Sybil's score and CAC; it reaches rung 1 (use) via the partial-association and kernel-perturbation arms, and the rung-3 SENTENCE is earned only if the CAC association survives adjustment for pack-years, emphysema and BV5. If CAC's unique contribution vanishes once emphysema and vessels are partialled out, the honest claim drops to 'Sybil uses a shared smoking/density signature' - rung 1, not the named-calcium sentence."},

      "use_vs_association": "Association is separated from use by (a) partialling CAC against emphysema and BV5 so a positive is CAC's UNIQUE variance, and (b) the paired-kernel perturbation - if a within-acquisition kernel change that moves measured CAC also moves Sybil's score, that is use of a density-channel feature, though the kernel moves emphysema too, so this arm proves density-channel use, not CAC-specific use. CAC-specific use rests on the partialling.",

      "dies_like_prior": "No prior kill applies. It resembles ideas 008 (emphysema/Sybil) and 009 (vessels/Sybil), but those are ACTIVE competing explanations, not failures - C1 is the third arm of the same decomposition and its distinct X (calcium) is spatially and physically separable from parenchymal density. It shares nothing with the five annotation-provenance kills (no human rating enters any readout) or with idea 006's intervention-validity failure (no anatomy is deleted or masked; the only manipulation is a real second reconstruction).",

      "closest_prior_work": [
        {"citation": "Mikhael et al., Sybil.", "identifier": "J Clin Oncol 2023;41(12):2191-2200, PMID 36634294, PMC10419602", "verification": "INSPECTED (PMC full text)", "what_it_did": "Documented the nodule-free residual: 2-year AUC 0.81 after removing visible nodules at the cancer site.", "what_it_did_not_do": "Did not measure any image property of the residual; named no anatomical explanation."},
        {"citation": "Sobieski et al., Auditing Sybil (S(H)NAP generative interventional attributions).", "identifier": "arXiv:2602.02560, ICML 2026 poster 66127", "verification": "INSPECTED (full HTML v2)", "what_it_did": "Causal attribution of Sybil's risk to pulmonary nodules via 3D diffusion-bridge edits; found a background term and reported only its regression on age.", "what_it_did_not_do": "Contains ZERO mentions of calcium, coronary, cardiac, cardiovascular, vessel or vascular - the entire cardiovascular hypothesis for the background term is untouched. It intervenes on nodules only."},
        {"citation": "Hagopian et al., AI-CAC.", "identifier": "NEJM AI 2025, DOI 10.1056/AIoa2400937, PMID 40746702", "verification": "INSPECTED (GitHub repo + paper record)", "what_it_did": "Released an MIT non-gated CAC scorer, validated against gated CAC and against mortality.", "what_it_did_not_do": "Never applied to Sybil or to any lung-cancer risk model."},
        {"citation": "HeartLung / MESA, 'Sybil AI For Lung Cancer Risk Prediction On Cardiac Versus Lung CT'.", "identifier": "J Cardiovasc Comput Tomogr, S1934-5925(26)00145-0 (2026)", "verification": "SEARCH_SUMMARY_ONLY (abstract paywalled)", "what_it_did": "Ran Sybil ON cardiac CAC-scan field of view versus lung CT to test transfer.", "what_it_did_not_do": "The orthogonal/reverse direction - it asks whether Sybil works on CAC scans, NOT whether CAC explains Sybil's signal. Must be cited and distinguished; does not pre-empt C1."}
      ],

      "existing_assets": ["Sybil weights + inference code (MIT, auto-download).", "AI-CAC weights + code (MIT, downloadable).", "lungmask (Apache-2.0) for LAA-950; a BV5 pipeline for small-vessel volume.", "NLST imaging on TCIA (CC BY 4.0, no application).", "NLST outcomes public via IDC BigQuery (nlst_canc).", "Published nodule-free benchmark (2-year AUC 0.81) so the residual's size is known.", "Ardila test-participant split reused by Sybil (established in idea 008 verification)."],

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

      "anticipated_negative": {"classification": "decisive", "reasoning": "If Sybil's score shows no unique association with CAC after partialling (within a prespecified equivalence margin sized to the score's SD ~0.07), it eliminates coronary calcium as the named residual and concentrates the remaining probability on emphysema/vessels - a decisive narrowing of a three-way question, not a failure to find something."},

      "cross_domain": null,

      "remaining_legwork": ["Stage 0 rank-agreement check: 2 days.", "Assemble held-out nodule-free single-kernel cohort and size against a minimum detectable partial association: 3 days.", "Download the NLST subset (real cost - large collection): ~1 week.", "Validate AI-CAC and lungmask on NLST-era LDCT noise: half a week.", "Time to first decision: Stage 0 in 2 days; Stage 1 answers the substantive question in ~3 weeks."],

      "scores": {
        "clarity": {"value": 5, "why": "One sentence names the model, the cohort, the biomarker, the tool, and the two rivals it must beat."},
        "identifiability": {"value": 3, "why": "CAC is spatially separable and partialling gives its unique variance, but CAC, emphysema and vessels are all smoking-driven and correlated, so a positive never fully excludes a shared signature; the kernel perturbation proves density-channel use, not CAC-specific use. Site is permanently unaddressable in NLST."},
        "medical_relevance": {"value": 4, "why": "Tells a radiologist a lung-cancer screening score is partly reading heart calcium - changing how the number is interpreted and suggesting CAC be read alongside it. Held below 5 as it does not by itself change management."},
        "interest": {"value": 5, "why": "A deployed lung-cancer model whose residual signal turns out to be cardiovascular, in a trial where CV death outnumbers cancer death, with the audit paper never having looked."},
        "prior_legwork": {"value": 5, "why": "Open weights (both tools MIT), open images, public outcomes, published residual benchmark, reusable split."},
        "feasibility": {"value": 4, "why": "Cap lifted (INSPECTED_TRUE). Inference-only, single GPU. Held to 4 by the NLST transfer and the AI-CAC-to-NLST transfer check."},
        "data_readiness": {"value": 5, "why": "CC BY 4.0 imaging, public outcomes, MIT weights - nothing behind a door."},
        "evaluation_readiness": {"value": 4, "why": "Rank correlation, partial regression, paired-change regression, mediation - all standard, with published CAC reference values. Only the equivalence margin needs specifying."},
        "negative_result_value": {"value": 4, "why": "A tight null eliminates one of three named explanations for a documented gap. Held below 5 by the equivalence-margin dependence and the noise of ungated Agatston."},
        "novelty_confidence": {"value": 4, "why": "Cap lifted. The Sybil-vs-CAC link was NOT_FOUND directly; the audit paper never mentions cardiovascular structures. Held at 4 because the general method (model score vs imaging biomarker) is named prior art (Regression Concept Vectors, scout-004 record) and the MESA HeartLung paper is an adjacent Sybil-plus-CAC study that must be distinguished."}
      },
      "priority_score": 4.20,
      "priority_arithmetic": "0.20*4 + 0.15*3 + 0.15*4 + 0.10*5 + 0.10*5 + 0.10*5 + 0.10*4 + 0.05*5 + 0.05*4 = 0.80+0.45+0.60+0.50+0.50+0.50+0.40+0.25+0.20 = 4.20",
      "regret": {"value": 5, "why": "Both tools download free, the biomarker is one command, and a 2026 audit paper isolated the exact residual term and never looked at the heart in the same image."},

      "unverified_claims": ["AI-CAC's per-scan ranking transfers to NLST-era LDCT (Stage 0 check).", "Exact IDC nlst_canc table/column names (minutes to confirm).", "The Ardila split reconciliation carried over from idea 008 is still open.", "MESA HeartLung abstract text (paywalled - read from snippets)."]
    },

    {
      "id": "C2",
      "search_mode": "B",
      "entry_point": 2,
      "title": "CT-CLIP has two calcification labels - coronary and arterial - so it can be asked whether it localises calcium or just sees hyperdensity",

      "question": "When CT-CLIP fires its 'Coronary artery wall calcification' label, is the score a monotone function of automated coronary Agatston, and does it dissociate from aortic-wall calcium measured in the same volume - so that the coronary label tracks coronary calcium specifically rather than total vascular calcium?",

      "deliverable_sentence": "CT-CLIP is using coronary artery calcium as a localised quantity: its coronary-calcification score rises with automated coronary Agatston and is not merely a readout of total calcium load, because it separates from aortic-wall calcium in the same scan.",

      "rung": {"current": 3, "why": "Coronary calcification is a named radiological finding; the design also tests whether the model's OWN label means what it says.", "what_would_move_it_up": "Nothing above rung 3; the localisation dissociation is what makes the rung-3 claim strong rather than a bare correlation."},

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

      "rung_reached": {"value": 2, "conditional_on": "The fidelity regression is rung 1 (the score IS the model's calcium output, so a monotone dependence on measured calcium is use, not correlation with an external label). The rung-3 localisation SENTENCE is earned only if coronary calcium predicts the coronary score with aortic calcium partialled out; if the two are collinear or the coronary label tracks total calcium, the claim is 'the model uses vascular calcium' (still rung 3, but a coarser X)."},

      "use_vs_association": "Use is not in doubt for the primary, because the score being regressed IS the model's own calcification output - a monotone dependence on measured Agatston is the model using calcium by definition. The association-vs-use worry lives entirely in WHICH calcium (coronary vs total), which the localisation dissociation resolves.",

      "dies_like_prior": "Resembles idea 010 (cardiomegaly -> heart volume, CT-CLIP score vs machine measurement), which is ACTIVE, not killed; C2's distinct move is the two-label localisation dissociation that idea 010's single label cannot support. No annotation-provenance issue: the primary readout regresses the model's own score against a voxel Agatston, and the RadBERT report label never enters the primary.",

      "closest_prior_work": [
        {"citation": "Hamamci et al., CT-CLIP / CT-RATE foundation model.", "identifier": "arXiv:2403.17834", "verification": "INSPECTED (v3 HTML)", "what_it_did": "Trained the model and reported the 18-label ClassFine performance, including both calcification labels.", "what_it_did_not_do": "Never tested whether the calcification scores track a measured calcium score, nor whether the two labels dissociate by anatomy."},
        {"citation": "Kenia, McNamara, Lotter, 'Anatomy Contextualized Adaption of CT Foundation Models'.", "identifier": "arXiv:2607.27154 (2026)", "verification": "SEARCH_SUMMARY_ONLY", "what_it_did": "Combined CT-CLIP and Merlin with TotalSegmentator anatomy for zero-shot binary finding classification.", "what_it_did_not_do": "No correlation of model scores against any continuous geometric or densitometric biomarker; no calcium quantification."},
        {"citation": "Hagopian et al., AI-CAC.", "identifier": "NEJM AI 2025, DOI 10.1056/AIoa2400937", "verification": "INSPECTED", "what_it_did": "Released the calcium scorer.", "what_it_did_not_do": "Never applied to a foundation model's calcification label."}
      ],

      "existing_assets": ["CT-CLIP ClassFine checkpoints (CC-BY-NC-SA, click-through).", "CT-RATE non-contrast chest CT volumes (same gate).", "AI-CAC (MIT).", "TotalSegmentator free task (Apache-2.0) for the aorta mask.", "The paper's own ClassFine AUROC for the two calcification labels as reference."],

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

      "anticipated_negative": {"classification": "sensitivity-limited", "reasoning": "If the coronary score does not track Agatston, it may be because the ClassFine head is near-binary and saturates, not because the model ignores calcium - so a null needs the score-distribution diagnostic and a minimum-detectable-slope to be interpretable. A clean null on the DISSOCIATION (coronary score tracks total calcium equally) is more decisive and would say the label does not localise."},

      "cross_domain": null,

      "remaining_legwork": ["Accept the CT-RATE gate and pull the validation split + checkpoints: 1 day.", "Stage 0 joint-distribution check: 2 days.", "Run AI-CAC + aortic counting across the split: 3 days.", "Time to first decision: ~2 weeks."],

      "scores": {
        "clarity": {"value": 5, "why": "Names the model, both labels, both measurements, and the dissociation that identifies the claim."},
        "identifiability": {"value": 4, "why": "The score is the model's own output so use is not in question; the two-label dissociation isolates coronary calcium from total calcium. Held below 5 by the residual (coronary/aortic calcium co-vary) and by CT-RATE's clinical-referral confound."},
        "medical_relevance": {"value": 3, "why": "A fidelity/localisation audit of a model's label - useful for trusting the model's calcium reporting, but less directly consequential than a discovery."},
        "interest": {"value": 4, "why": "Whether a foundation model's finding label is anatomically meaningful or just a hyperdensity detector is a sharp, generalisable question."},
        "prior_legwork": {"value": 5, "why": "Open model, open images (gated but free), two open measurement tools, published reference AUROCs."},
        "feasibility": {"value": 4, "why": "Cap lifted (INSPECTED_TRUE). Inference-only; both tools run. Held by the CT-RATE gate and thick-slice coronary blurring."},
        "data_readiness": {"value": 4, "why": "CT-RATE is a free click-through, non-commercial gate; not fully open."},
        "evaluation_readiness": {"value": 5, "why": "Agatston, ordinal agreement, partial regression, double dissociation - all standard with reference values."},
        "negative_result_value": {"value": 3, "why": "A fidelity null is sensitivity-limited (label may saturate); a dissociation null is more decisive. Averaged to 3."},
        "novelty_confidence": {"value": 4, "why": "Cap lifted. No prior test of CT-CLIP calcification-score fidelity or localisation was found. Held at 4 because the score-vs-biomarker method is established prior art and a very recent preprint could exist."}
      },
      "priority_score": 3.95,
      "priority_arithmetic": "0.20*4 + 0.15*4 + 0.15*3 + 0.10*5 + 0.10*4 + 0.10*5 + 0.10*3 + 0.05*4 + 0.05*4 = 0.80+0.60+0.45+0.50+0.40+0.50+0.30+0.20+0.20 = 3.95",
      "regret": {"value": 4, "why": "The two-label natural experiment is sitting in the released model and nobody has run it; the tools are free."},

      "unverified_claims": ["Coronary and aortic calcium vary independently enough in CT-RATE (Stage 0).", "AI-CAC runs acceptably on 6 mm-slice CT-RATE volumes.", "The exact ClassFine score scale/saturation behaviour for the calcification heads.", "CT-RATE FOV consistently includes full coronary coverage (inferred from 'chest CT', not verbatim)."]
    },

    {
      "id": "C3",
      "search_mode": "B",
      "entry_point": 2,
      "title": "An abdominal foundation model predicts diabetes - ask whether it is quietly reading the fat in the liver",

      "question": "When Merlin predicts diabetes mellitus from an abdominal CT, is its score mediated by hepatic steatosis - the mean Hounsfield attenuation of the liver - rather than by the visceral-fat and pancreatic signals it is usually assumed to use?",

      "deliverable_sentence": "Merlin is using hepatic steatosis: its diabetes score falls as mean liver attenuation falls, and liver attenuation mediates a measurable share of the diabetes signal independent of visceral fat.",

      "rung": {"current": 3, "why": "Hepatic steatosis / fatty liver is a named finding a radiologist reports; liver attenuation is its calibrated measurement.", "what_would_move_it_up": "Nothing above rung 3; strengthened by showing the mediation survives adjustment for visceral fat and pancreatic attenuation."},

      "X_measurement": {
        "X": "Mean liver attenuation in Hounsfield units on non-contrast CT (steatosis at <= 40 HU), with the liver-minus-spleen HU difference as a co-primary to reduce global-calibration drift.",
        "how": "TotalSegmentator free 'total' task segments liver and spleen; take mean HU inside each mask. No annotation.",
        "citations": "TotalSegmentator: Wasserthal et al., Radiol Artif Intell 2023;5(5):e230024. Steatosis threshold: liver mean attenuation <= 40 HU (non-contrast) and liver-spleen difference, per RSNA Radiology quantification reviews (radiol.241171; radiol.2021204288) and the classic Kodama-type population thresholds. Merlin diabetes output: Blankemeier et al., arXiv:2406.06512 (diabetes mellitus is one of the six named 5-year chronic-disease predictions).",
        "could_I_compute_it_today_without_asking_anyone": "Yes. Merlin weights are MIT and open; TotalSegmentator is open; liver HU is a masked mean.",
        "known_weakness_of_X_stated_up_front": "The <= 40 HU threshold is for NON-CONTRAST CT; Merlin's training corpus mixes contrast phases, and portal-venous enhancement raises liver HU by 30-50 HU, which would mask steatosis. Contrast phase must be detected (e.g., aortic/portal HU) and the analysis stratified or restricted to non-contrast; this is the live confound."
      },

      "suspected_signal": "Hepatic steatosis is the imaging hallmark of NAFLD, which sits on the insulin-resistance/type-2-diabetes axis, and fat lowers liver X-ray attenuation directly and proportionally (roughly -1.6 HU per 1% fat). So a diabetes predictor that has learned the metabolic-syndrome phenotype would encode low liver HU. A positive says Merlin found the fatty liver on its own and is using it to call diabetes.",

      "keystone_prerequisite": "Merlin emits a per-scan diabetes score that can be regressed against, and mediated through, liver attenuation on the SAME abdominal CT - and enough scans are non-contrast (or phase can be recovered) that liver HU is a valid steatosis measure rather than a contrast artefact.",

      "keystone_status": "INSPECTED_TRUE",

      "keystone_evidence": "Merlin is released MIT with downloadable weights (HF stanfordmimi/Merlin; pip merlin-vlm) and its six explicit 5-year chronic-disease predictions include 'diabetes mellitus' (arXiv:2406.06512, INSPECTED). Its FOV is abdominal CT and it segments the liver and spleen among its 20 organs, so liver HU is computable on exactly the volumes it scores. TotalSegmentator liver/spleen masks are established for steatosis attenuation (Sci Rep 2024, s41598-024-62887-2). The diabetes-score-vs-liver-HU regression needs no ground-truth diabetes label, so it runs on any public abdominal CT set (AMOS, AbdomenAtlas, FLARE).",

      "keystone_residual_assumption": "Having verified Merlin predicts diabetes and images the liver, I am still assuming a supply of scans on which liver HU is a valid steatosis reading - i.e. non-contrast or phase-recoverable. Merlin was trained on a phase-mixed corpus; if the accessible public test scans are predominantly contrast-enhanced, liver HU is contaminated and the mediation is uninterpretable. This is load-bearing and checkable in Stage 0 by measuring aortic/portal HU to classify phase.",

      "rung_reached": {"value": 2, "conditional_on": "Mediation of the model's own diabetes score through liver HU is rung 1 (use) if liver HU carries score variance independent of visceral fat; the rung-3 SENTENCE is earned if the mediated share is non-trivial and survives adjustment for visceral fat and pancreatic attenuation. If liver HU's mediation vanishes once visceral fat is controlled, the claim drops to 'Merlin uses general adiposity'."},

      "use_vs_association": "Mediation analysis, not bare correlation: the diabetes score is decomposed into a part explained by liver HU and a part independent of it, with visceral fat and pancreatic HU as competing mediators, so 'uses steatosis' means liver HU carries UNIQUE score variance, not that steatosis happens to correlate with diabetes.",

      "dies_like_prior": "No prior kill applies - new organ system, new model, no human rating anywhere. The nearest concern is the scout-004 liver-dome question, which died on field-of-view truncation; that defect does NOT apply here because Merlin images the whole liver (abdominal CT), removing the coverage confound that sank the chest-CT version.",

      "closest_prior_work": [
        {"citation": "Blankemeier et al., Merlin.", "identifier": "arXiv:2406.06512 (Nature 2026, s41586-026-10181-8)", "verification": "INSPECTED (arXiv v1 HTML)", "what_it_did": "Trained the abdominal-CT VLM; predicts diabetes among six chronic diseases and 692 phenotypes.", "what_it_did_not_do": "Never named or probed hepatic steatosis / liver attenuation; 'steatosis', 'NAFLD', 'hepatic' absent from the text."},
        {"citation": "CT-IDP, 'Segmentation-Derived Quantitative Phenotypes for Interpretable Abdominal CT Disease Classification'.", "identifier": "arXiv:2605.09002", "verification": "SEARCH_SUMMARY_ONLY", "what_it_did": "Built hand-crafted segmentation phenotypes (including a hepatic-steatosis feature) and benchmarked them AGAINST Merlin (reported +0.156 on hepatic steatosis vs a ViT baseline).", "what_it_did_not_do": "Did not probe or mediate Merlin's internal reliance on liver attenuation - it is a competing pipeline, not an interpretability audit of the foundation model."}
      ],

      "existing_assets": ["Merlin weights (MIT, HF/pip).", "TotalSegmentator (Apache-2.0) for liver/spleen HU.", "Public abdominal CT sets (AMOS, AbdomenAtlas, FLARE) for the label-free primary readout.", "Established CT steatosis thresholds and a phase-classification heuristic (aortic/portal HU)."],

      "smallest_decisive_experiment": "Stage 0 (2 days): classify phase on a public abdominal CT set via aortic/portal HU and confirm a usable non-contrast subset. Stage 1 (no labels): run Merlin's diabetes head and regress its score on liver HU (and liver-spleen HU); a using-steatosis model shows a monotone score gradient across liver-HU deciles. Stage 2 (mediation): decompose the score's variance through liver HU with visceral fat area and pancreatic HU as competing mediators; the identifying quantity is liver HU's unique mediated share.",

      "standing_confounds_addressed": {
        "scanner_and_vendor": "Covariate; public multi-site sets give diversity.",
        "acquisition_protocol": "CONTRAST PHASE is the dominant confound and is handled by phase classification and non-contrast restriction.",
        "reconstruction": "Kernel affects HU noise; covariate.",
        "site": "Addressable by using a multi-site public test set, unlike NLST.",
        "positioning": "Negligible for organ-mean HU.",
        "habitus": "Visceral fat is a competing mediator, explicitly measured, not just a nuisance.",
        "prevalence": "Diabetes prevalence differs by source cohort; the primary readout is score-vs-HU, not prevalence-dependent.",
        "referral_pathway": "Abdominal CT indication may correlate with both steatosis and diabetes; addressed as a limitation and partly by the within-scan mediation.",
        "label_leakage": "N/A - primary readout uses no diabetes label; the score is regressed on a voxel measurement."
      },

      "alternative_explanations": [
        "General adiposity / visceral fat, not liver fat specifically - the central alternative, attacked by including visceral fat area as a competing mediator.",
        "Pancreatic fat/atrophy, a second diabetes substrate visible on the same scan - included as a competing mediator.",
        "Contrast phase masquerading as steatosis (enhanced livers look 'non-fatty') - handled by phase stratification.",
        "The appealing 'the model reads the fatty liver' sentence would also arise from any metabolic-syndrome signal; only the unique mediated share of liver HU, net of visceral and pancreatic fat, supports it."
      ],

      "anticipated_negative": {"classification": "decisive", "reasoning": "If liver HU carries no unique mediated share of the diabetes score once visceral and pancreatic fat are controlled, it decisively excludes hepatic steatosis as Merlin's diabetes cue and points to generic adiposity - provided the non-contrast subset is adequately powered."},

      "cross_domain": null,

      "remaining_legwork": ["Assemble a phase-classified non-contrast abdominal CT subset: 3 days.", "Run Merlin + TotalSegmentator across it: 3 days.", "Mediation with competing mediators: 2 days.", "Time to first decision: ~2 weeks."],

      "scores": {
        "clarity": {"value": 5, "why": "Names the model, the output, the biomarker, the tool and the two competing mediators."},
        "identifiability": {"value": 3, "why": "Mediation with competing mediators isolates liver HU's unique share, but contrast phase and the visceral/pancreatic-fat correlation are strong threats; held at 3."},
        "medical_relevance": {"value": 4, "why": "Says the abdominal model's diabetes signal is (partly) the fatty liver - clinically meaningful on the NAFLD-diabetes axis and relevant to opportunistic screening."},
        "interest": {"value": 4, "why": "A foundation model implicitly using a named metabolic biomarker it was never told to compute."},
        "prior_legwork": {"value": 5, "why": "Merlin open MIT, TotalSegmentator open, public abdominal CT sets, established thresholds."},
        "feasibility": {"value": 4, "why": "Cap lifted (INSPECTED_TRUE). Inference-only. Held by the phase-handling requirement."},
        "data_readiness": {"value": 4, "why": "Model open; abdominal CT test data public but needs phase filtering."},
        "evaluation_readiness": {"value": 4, "why": "Mediation, decile regression - standard; equivalence margin needed for the null."},
        "negative_result_value": {"value": 3, "why": "Decisive if adequately powered, but phase contamination could make a null sensitivity-limited; held at 3."},
        "novelty_confidence": {"value": 4, "why": "Cap lifted. No mediation/probe of Merlin through liver HU found; CT-IDP benchmarks but does not probe internals. Held at 4 for the crowded steatosis-from-CT space generally."}
      },
      "priority_score": 3.95,
      "priority_arithmetic": "0.20*4 + 0.15*3 + 0.15*4 + 0.10*5 + 0.10*4 + 0.10*5 + 0.10*3 + 0.05*4 + 0.05*4 = 0.80+0.45+0.60+0.50+0.40+0.50+0.30+0.20+0.20 = 3.95",
      "regret": {"value": 4, "why": "Open model, open tool, a whole-liver FOV that removes the truncation defect that killed the chest-CT version - a week of work sits between here and the answer."},

      "unverified_claims": ["A sufficiently large non-contrast abdominal CT subset with Merlin-scannable format is reachable (Stage 0).", "Merlin's diabetes head exposes a usable continuous score in the released weights (not only the 692-phenotype head).", "Exact steatosis threshold behaviour across the accessible cohort's scanners."]
    },

    {
      "id": "C4",
      "search_mode": "C",
      "entry_point": 2,
      "title": "Merlin predicts osteoporosis - ask whether it reads the density of the bone or the shape of a column that has begun to buckle",

      "question": "When Merlin predicts osteoporosis, is its score reading vertebral trabecular attenuation (opportunistic bone density in Hounsfield units) or vertebral wedge deformity (the Genant anterior-to-posterior height ratio), and does the deformity signal concentrate at the thoracolumbar junction as column-buckling mechanics predicts?",

      "deliverable_sentence": "Merlin is using vertebral wedge deformity - the Genant anterior-to-posterior height ratio - and it weights the thoracolumbar junction most, rather than reading uniform trabecular bone density.",

      "rung": {"current": 3, "why": "Both candidate X's are named radiological quantities: opportunistic BMD (trabecular HU) and vertebral compression/wedging (Genant). The deliverable names which one and where.", "what_would_move_it_up": "Nothing above rung 3; the spatial (thoracolumbar) prediction is what turns a correlation into a mechanistically specific claim."},

      "X_measurement": {
        "X": "Two competing, separately measured quantities: (a) trabecular attenuation = mean HU in an eroded vertebral-body core; (b) Genant wedge ratio = anterior height / posterior height per vertebra, graded 20/25/40% for mild/moderate/severe.",
        "how": "TotalSegmentator (or Merlin's own nnU-Net) segments individual vertebrae T12-L5; trabecular HU is a masked mean of an eroded core; wedge ratio is a geometric height computation per body. No annotation.",
        "citations": "Genant HK, Wu CY, van Kuijk C, Nevitt MC, J Bone Miner Res 1993;8(9):1137-1148, PMID 8237484 (semiquantitative wedge/biconcave/crush grading, 20/25/40% thresholds). TotalSegmentator vertebrae: Wasserthal et al., Radiol Artif Intell 2023;5(5):e230024. Merlin osteoporosis output: Blankemeier et al., arXiv:2406.06512 (osteoporosis is one of the six named chronic-disease predictions).",
        "could_I_compute_it_today_without_asking_anyone": "Yes. Both X's are geometric/densitometric computations on open vertebral masks; Merlin weights are open.",
        "known_weakness_of_X_stated_up_front": "Trabecular HU is moved by contrast phase, marrow fat and kernel; wedge ratio is robust to these but needs clean vertebral segmentation and endplate localisation, which degrade with severe deformity - exactly the cases of interest."
      },

      "suspected_signal": "Osteoporosis is DEFINED by low bone density (trabecular HU) but MANIFESTS as fragility fractures - anterior wedge collapse of vertebral bodies. Column-buckling mechanics (Euler) says a slender loaded column fails where compressive load and slenderness are greatest, which for the spine is the thoracolumbar junction (T12-L1), and the failure mode of an anteriorly-loaded vertebra is a wedge. So the mechanism names both a QUANTITY (wedge ratio) and a LOCATION (thoracolumbar) that a density-only reading would not privilege. Whether Merlin reads the cause (density) or the consequence (shape), and where, is the discriminating question.",

      "keystone_prerequisite": "Merlin emits a per-scan osteoporosis score that can be regressed against BOTH trabecular HU and Genant wedge ratio on the same vertebrae, AND the two quantities vary independently enough across scans to be dissociated - because low BMD causes wedge fractures, so they are correlated and a design that cannot separate them will credit whichever it measures first.",

      "keystone_status": "INSPECTED_TRUE",

      "keystone_evidence": "Merlin predicts osteoporosis explicitly (one of six 5-year chronic diseases, arXiv:2406.06512, INSPECTED) and segments T12-L5/S1 vertebrae (its 20-organ target list, INSPECTED), so both X's are computable on scans it scores. Weights MIT/open. Genant grading and TotalSegmentator vertebrae are established. The osteoporosis-output existence - the thing that makes the study possible - is INSPECTED_TRUE, which is why this Mode C candidate is not NOT_INSPECTED.",

      "keystone_residual_assumption": "Having verified Merlin has an osteoporosis output and segments the vertebrae, I am still assuming trabecular HU and wedge ratio VARY INDEPENDENTLY enough to dissociate - which is the real keystone and is NOT verified. Because osteoporosis couples them (low density -> fracture -> wedge), a cohort may show them collinear, in which case the headline dissociation is unidentifiable and the candidate retreats to 'Merlin uses vertebral bone signal' without saying which. This is the identical trap the charter names three times: 'both are measurable' is not 'both vary independently'. Stage 0 must estimate their joint distribution.",

      "rung_reached": {"value": 2, "conditional_on": "Regressing the model's own osteoporosis score against each X is rung 1; the rung-3 SENTENCE (naming wedging AND the thoracolumbar location) is earned only if the wedge ratio carries score variance independent of trabecular HU and the location weighting matches the mechanical prediction. If they are collinear, the honest claim is the coarser 'vertebral bone signal'."},

      "use_vs_association": "The osteoporosis score is decomposed against two competing measured X's simultaneously; 'uses wedging' means the wedge ratio carries UNIQUE score variance net of trabecular HU, and the pre-registered thoracolumbar spatial prediction is a second, independent identifying constraint that a mere density correlation would fail.",

      "dies_like_prior": "Resembles idea 011 (costal-cartilage age clock) as cross-domain skeletal reading, which is ACTIVE not killed; C4 differs by model (Merlin osteoporosis output, not an age model), by bone (vertebrae), and by using a two-X dissociation rather than a single recovered clock. No annotation-provenance issue. The one real inherited risk is the dissociation-identifiability trap, flagged above as the true keystone.",

      "closest_prior_work": [
        {"citation": "Blankemeier et al., Merlin.", "identifier": "arXiv:2406.06512", "verification": "INSPECTED", "what_it_did": "Predicts osteoporosis as one of six chronic diseases.", "what_it_did_not_do": "Never probed whether the osteoporosis signal is density or morphometry, nor where in the spine it sits."},
        {"citation": "Xu et al., explainable spine biological age.", "identifier": "GeroScience 2024, PMC11979066", "verification": "INSPECTED", "what_it_did": "Used anterior/posterior/mid height ratios (APR, MPR, PPR) across T4-L4 with SHAP to quantify spinal compression as an age signal.", "what_it_did_not_do": "A hand-crafted RF/LASSO model, NOT a probe of any learned CT foundation model; does not touch Merlin or osteoporosis output."},
        {"citation": "Kerber et al., deep-learning age estimation from thorax/abdomen CT.", "identifier": "PLoS One 2023, PMC10629654", "verification": "INSPECTED", "what_it_did": "Saliency highlighted the lumbar spine and abdominal aorta for age.", "what_it_did_not_do": "Stopped at 'lumbar spine'; never attributed the signal to wedging vs density and cautioned saliency is unreliable."}
      ],

      "existing_assets": ["Merlin weights (MIT).", "TotalSegmentator / Merlin nnU-Net vertebral masks.", "Genant protocol and published wedge thresholds.", "Xu et al.'s height-ratio definitions to reuse.", "Public abdominal CT sets for the label-free readout."],

      "smallest_decisive_experiment": "Stage 0 (2 days): compute trabecular HU and wedge ratio on a public abdominal CT set and estimate their joint distribution - go/no-go for the dissociation. Stage 1: regress Merlin's osteoporosis score on each X separately, then jointly (partial contributions). Stage 2 (spatial test): weight the wedge signal by vertebral level and test the pre-registered prediction that the thoracolumbar junction dominates; a density-only model would show no such spatial concentration.",

      "standing_confounds_addressed": {
        "scanner_and_vendor": "Covariate; multi-site public data helps.",
        "acquisition_protocol": "Contrast phase moves trabecular HU (not wedge ratio) - handled by phase stratification; the wedge arm is phase-robust.",
        "reconstruction": "Kernel affects HU; covariate.",
        "site": "Addressable via multi-site public data.",
        "positioning": "Spinal curvature/lordosis affects apparent wedge; measured per-vertebra in the local frame to reduce this.",
        "habitus": "Body size affects HU noise; covariate.",
        "prevalence": "Score-vs-X readout is not prevalence-dependent.",
        "referral_pathway": "Indication may correlate with fracture burden; limitation.",
        "label_leakage": "N/A - no osteoporosis label enters the primary readout."
      },

      "alternative_explanations": [
        "Trabecular density (the definitional cause), not shape - the central competing X, which is exactly why it is measured head-to-head.",
        "Degenerative change (osteophytes, disc-space loss) co-located with wedging - a covariate that could inflate the morphometry signal; addressed by restricting height measurement to the vertebral body.",
        "Collinearity of density and wedging makes the dissociation vacuous - the true keystone risk, checked in Stage 0.",
        "The Euler/thoracolumbar story is attractive; if the dissociation is unidentifiable, the spatial arm must not be over-read as confirming a mechanism it cannot isolate."
      ],

      "anticipated_negative": {"classification": "sensitivity-limited", "reasoning": "If wedge ratio and trabecular HU are collinear in the accessible cohort, a null on the dissociation reflects the cohort's joint distribution, not the model - so it needs the Stage-0 independence estimate and a minimum-detectable partial effect to be interpretable. A clean result requires a cohort with genuine density-shape decoupling (e.g., low-BMD but un-fractured spines)."},

      "cross_domain": {"borrowed_construct": "Euler buckling of a slender loaded column from structural mechanics.", "measurement_it_implies": "Weight the wedge-deformity signal by vertebral level and predict thoracolumbar (T12-L1) dominance and an anterior (wedge) failure mode, rather than uniform height loss.", "what_would_change_if_dropped": "Without the analogy you would still measure the Genant wedge ratio (standard radiology), but you would have no principled prediction about WHERE the signal should live; the mechanics converts a generic 'measure the spine' into a pre-registered spatial test (thoracolumbar predominance) that a density-only reading fails. That specific, falsifiable location claim is what the analogy earns - it is not decoration."},

      "remaining_legwork": ["Stage 0 joint-distribution check: 2 days.", "Vertebral segmentation QC and endplate localisation: 3 days.", "Merlin osteoporosis-score extraction + regressions: 3 days.", "Time to first decision: ~2 weeks; a decoupled cohort may need sourcing, extending it."],

      "scores": {
        "mechanism_clarity": {"value": 4, "why": "Two named physical quantities and their measurements, plus a mechanically-derived spatial prediction. Below 5 because Euler is mechanism motivation the wedge ratio does not strictly need."},
        "identifiability": {"value": 4, "why": "Two-X dissociation plus an independent spatial constraint; held below 5 by the density-wedge collinearity that is the true keystone."},
        "interest": {"value": 4, "why": "Whether a model reads a disease by its cause (density) or its consequence (fracture shape), and where, is a sharp and general question."},
        "medical_relevance": {"value": 4, "why": "Distinguishes opportunistic BMD from morphometric fracture detection inside one score - relevant to how the osteoporosis output should be trusted and used."},
        "clarity": {"value": 5, "why": "One sentence names the model, both quantities, and the location claim."}
      },
      "priority_score": 4.10,
      "priority_arithmetic": "Mode C weighting: 0.30*4 (mechanism) + 0.25*4 (ident) + 0.20*4 (interest) + 0.15*4 (med) + 0.10*5 (clarity) = 1.20+1.00+0.80+0.60+0.50 = 4.10",
      "feasibility_for_information": {"value": 3, "why": "Inference-only and open tools, but the identifying cohort (density-shape decoupled) may need sourcing, and severe-deformity segmentation is fragile. Cap would allow higher given INSPECTED_TRUE, but the sourcing risk holds it at 3."},
      "novelty_confidence_for_information": {"value": 4, "why": "No probe of Merlin's osteoporosis signal for density-vs-morphometry found; the wedge-age link exists only as hand-crafted features (Xu) and the region only as saliency (Kerber). The Euler-buckling-to-foundation-model framing appears novel."},
      "regret": {"value": 3, "why": "A clean, legible dissociation sitting on an open model; discounted because the collinearity risk could make it uninterpretable without a special cohort."},

      "unverified_claims": ["Trabecular HU and wedge ratio vary independently enough in an accessible cohort (the true keystone; Stage 0).", "Merlin's osteoporosis head exposes a usable continuous score in the released weights.", "Vertebral segmentation is reliable on osteoporotic/deformed bodies.", "The Euler thoracolumbar prediction is the right one for supine CT loading (biomechanics literature exists but the supine-imaging load state is assumed)."]
    },

    {
      "id": "C5",
      "search_mode": "C",
      "entry_point": 2,
      "title": "An airway and its artery run together and should taper together - ask whether the model reads bronchiectasis as the broken ratio between the two",

      "question": "When CT-CLIP fires 'Bronchiectasis', is the score a function of the bronchoarterial ratio - airway luminal diameter divided by the diameter of the accompanying pulmonary artery - rather than of absolute airway calibre, which is confounded by lung and body size?",

      "deliverable_sentence": "CT-CLIP is using the bronchoarterial ratio - the airway widened relative to its accompanying artery - and not merely the absolute size of the airway.",

      "rung": {"current": 3, "why": "The bronchoarterial ratio is the radiological definition of bronchiectasis - a named finding.", "what_would_move_it_up": "Nothing above rung 3; the absolute-vs-ratio contrast is what makes it the named finding rather than 'big airways'."},

      "X_measurement": {
        "X": "Bronchoarterial ratio (BAR) = airway inner luminal diameter / diameter of the immediately adjacent pulmonary artery, at matched airway generations; BAR > 1 is the conventional bronchiectasis threshold. Absolute luminal area is the competing X.",
        "how": "Segment the airway lumen and the pulmonary arteries, pair each airway with its accompanying artery along the bronchovascular bundle, and take the diameter ratio. Requires an airway segmenter (e.g., open ATM-challenge models) plus a pulmonary-vessel segmenter.",
        "citations": "BAR definition and threshold: standard Fleischner/thoracic imaging criteria for bronchiectasis (signet-ring sign, BAR > 1). Airway segmentation baselines: ATM'22 challenge models. CT-CLIP bronchiectasis label: Hamamci et al., arXiv:2403.17834 (label #17).",
        "could_I_compute_it_today_without_asking_anyone": "Partly - airway and vessel segmenters are open, but pairing airways to arteries and measuring lumen diameters on NON-CONTRAST CT is a research pipeline, not a one-command tool. This is the weakest measurement channel in the portfolio and is why the candidate is Mode C.",
        "known_weakness_of_X_stated_up_front": "Non-contrast CT-RATE gives poor pulmonary-artery lumen edges (no contrast), and TotalSegmentator's free task does not segment the pulmonary artery, so the artery side of the ratio must come from a vessel-segmentation model on non-contrast data - noisy. Slice thickness up to 6 mm blurs small peripheral airways where bronchiectasis is graded."
      },

      "suspected_signal": "An airway and its accompanying pulmonary artery travel together in the bronchovascular bundle and, in health, co-scale so their diameters are roughly matched (BAR ~ 0.65-1.0). Bronchiectasis is airway dilation OUT OF PROPORTION to the artery - traction, inflammation and wall destruction widen the lumen while the artery does not follow. So the disease is a broken ratio, not an absolute size. A model that has learned the finding rather than a size proxy will track BAR.",

      "keystone_prerequisite": "A per-scan bronchoarterial ratio can be computed reliably on non-contrast CT-RATE volumes and regressed against CT-CLIP's bronchiectasis score, with the ratio separable from absolute airway calibre - because if only absolute calibre is measurable (artery side too noisy on non-contrast CT), the design cannot show the model uses the RATIO rather than size.",

      "keystone_status": "NOT_INSPECTED",

      "keystone_evidence": "CT-CLIP's bronchiectasis label is confirmed (arXiv:2403.17834, label #17). But the load-bearing fact - that a reliable per-scan BAR is computable on non-contrast, up-to-6mm-slice CT-RATE volumes with an open pipeline - was NOT inspected and is genuinely uncertain. Per the charter, a Mode C candidate may honestly report NOT_INSPECTED and accept the feasibility/novelty caps.",

      "keystone_residual_assumption": "Even if airway and vessel segmenters run, I am assuming the ARTERY side of the ratio is measurable on non-contrast CT well enough to make BAR more than noise around absolute airway size. If it is not, the whole point (ratio, not size) collapses and the candidate reduces to 'the model uses big airways', which does not identify the named finding.",

      "rung_reached": {"value": 1, "conditional_on": "Even a positive score-vs-BAR association is rung 1 (use of an airway-size feature) until the ratio is shown to beat absolute calibre; the rung-3 SENTENCE needs BAR to carry score variance independent of absolute luminal area, which the non-contrast measurement may not support."},

      "use_vs_association": "Absolute calibre and BAR are entered together; 'uses the ratio' means BAR carries score variance net of absolute luminal area - otherwise the model is using airway size, and the ratio framing is unsupported.",

      "dies_like_prior": "No prior kill applies directly - it uses no human ratings and no deletion intervention. Its risk is not a prior failure MODE but feasibility: the measurement channel may be too weak on non-contrast CT, which is the honest reason it is the lowest-scored Mode C candidate rather than a Mode B.",

      "closest_prior_work": [
        {"citation": "Hamamci et al., CT-CLIP.", "identifier": "arXiv:2403.17834", "verification": "INSPECTED", "what_it_did": "Reports a bronchiectasis ClassFine score.", "what_it_did_not_do": "Never related it to a bronchoarterial-ratio measurement."},
        {"citation": "ATM'22 airway segmentation challenge and follow-ups.", "identifier": "airway-segmentation literature", "verification": "SEARCH_SUMMARY_ONLY", "what_it_did": "Open airway-tree segmentation models.", "what_it_did_not_do": "Not paired with pulmonary-artery matching for BAR on non-contrast foundation-model corpora, and not linked to any model's score."}
      ],

      "existing_assets": ["CT-CLIP bronchiectasis score (gated-free CT-RATE).", "Open airway and pulmonary-vessel segmentation models.", "Standard BAR definition and threshold."],

      "smallest_decisive_experiment": "Stage 0 (go/no-go, 1 week): on a handful of CT-RATE volumes, test whether an open airway+vessel pipeline yields a stable BAR on non-contrast data (reproducibility across kernels/thicknesses). Only if BAR is stable: Stage 1 regresses CT-CLIP's bronchiectasis score on BAR and on absolute luminal area jointly; the identifying quantity is BAR's unique contribution.",

      "standing_confounds_addressed": {
        "scanner_and_vendor": "Covariate.",
        "acquisition_protocol": "Non-contrast throughout; the artery-edge problem is protocol-driven and is the core feasibility risk.",
        "reconstruction": "Kernel and slice thickness strongly affect airway-wall/lumen measurement; covariate and reproducibility-gated in Stage 0.",
        "site": "Limited in CT-RATE; limitation.",
        "positioning": "Minor.",
        "habitus": "BAR is designed to normalise body/lung size - that is the point of the ratio.",
        "prevalence": "Score-vs-X readout not prevalence-dependent.",
        "referral_pathway": "Indication may correlate with airway disease; limitation.",
        "label_leakage": "N/A - no label in the primary readout."
      },

      "alternative_explanations": [
        "Absolute airway calibre / lung size, not the ratio - the central alternative, attacked by entering both.",
        "Mucus plugging or wall thickening co-occurring with dilation - could drive the score independently of BAR; a covariate.",
        "Measurement noise on the artery side mimicking or masking a ratio effect - the feasibility keystone.",
        "The elegant 'broken co-scaling' story must not survive if BAR proves unmeasurable; then the honest claim is airway size."
      ],

      "anticipated_negative": {"classification": "uninterpretable", "reasoning": "Given the NOT_INSPECTED measurement keystone, a null could mean the model ignores BAR OR that BAR was too noisy to detect on non-contrast CT - several explanations survive. This is honestly an uninterpretable-null risk unless Stage 0 first establishes BAR reliability, which caps negative-result value."},

      "cross_domain": {"borrowed_construct": "Allometric co-scaling of two parallel transport conduits (an airway and its pulmonary artery in the bronchovascular bundle), a Murray-law-adjacent diameter-matching principle.", "measurement_it_implies": "Use the airway-to-artery diameter RATIO with the paired artery as an internal normaliser, rather than absolute airway diameter.", "what_would_change_if_dropped": "Without the co-scaling principle you would measure absolute airway calibre, which is confounded by lung and body size; the paired-tube view says use the accompanying artery as the internal ruler - which is exactly the radiological BAR and removes the size confound. The analogy earns the ratio (and its internal normalisation), not just a metaphor - dropping it changes the measurement from absolute to relative."},

      "remaining_legwork": ["Stage 0 BAR-reproducibility test on non-contrast CT-RATE: 1 week (this is the whole gamble).", "If stable: Stage 1 regressions: 1 week.", "Time to first decision: ~2-3 weeks, front-loaded on the feasibility check."],

      "scores": {
        "mechanism_clarity": {"value": 4, "why": "Named quantity (BAR) with a clear physical mechanism (disproportionate airway dilation) and a specific measurement. Below 5 because the artery-side measurement is uncertain."},
        "identifiability": {"value": 3, "why": "Entering BAR against absolute calibre would isolate the ratio, but non-contrast artery-edge noise threatens the discrimination; held at 3."},
        "interest": {"value": 3, "why": "A neat 'does the model use the defining ratio' question, but narrower and more measurement-fragile than the others."},
        "medical_relevance": {"value": 3, "why": "Confirms whether a bronchiectasis label means the defining finding; useful but modest."},
        "clarity": {"value": 4, "why": "Clear question; slightly softened by the measurement uncertainty baked into it."}
      },
      "priority_score": 3.40,
      "priority_arithmetic": "Mode C weighting: 0.30*4 (mechanism) + 0.25*3 (ident) + 0.20*3 (interest) + 0.15*3 (med) + 0.10*4 (clarity) = 1.20+0.75+0.60+0.45+0.40 = 3.40",
      "feasibility_for_information": {"value": 2, "why": "NOT_INSPECTED keystone; the BAR pipeline on non-contrast, thick-slice CT is the real risk and could fail Stage 0. Capped at <=3 and set to 2."},
      "novelty_confidence_for_information": {"value": 3, "why": "No prior link of a foundation model's bronchiectasis score to BAR found, but airway quantification is a worked field and the specific gap was not exhaustively searched; capped at 3 (NOT_INSPECTED)."},
      "regret": {"value": 2, "why": "If it works it is a clean legible sentence, but the feasibility risk is high enough that little is lost by deferring it until the measurement is shown to be stable."},

      "unverified_claims": ["A reliable per-scan BAR is computable on non-contrast CT-RATE volumes (the keystone; Stage 0).", "Open airway+vessel segmenters transfer to CT-RATE's non-contrast, up-to-6mm-slice data.", "CT-CLIP's bronchiectasis score has enough dynamic range to regress against a continuous ratio."]
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
4. **Verdict.** `NOVEL_VERIFIED`, `NOVEL_UNVERIFIED` (search inconclusive),
   `INCREMENTAL`, or `DUPLICATE_PRIOR` (recommend kill with the citation).

Write `novelty_audit.md` in the assigned output directory: one section per
candidate, headed by the candidate's title and track, containing exactly the
four items above. Close the file with a summary table: candidate / verdict /
why-not-done code.

Do not write code. Do not modify any other file.

