You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/006
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

### The three rungs

Every candidate must state which rung it is on and what would move it up.

1. **The model uses signal X.** A measurement. Comparatively easy: ablation,
   masking, probing, perturbation, saliency with proper controls.
2. **X is not an artifact.** Not scanner, site, protocol, reconstruction,
   position, dose, body habitus, referral pattern, or label leakage. This is
   where most projects quietly fail, and it is where most of the real work is.
3. **X is biologically meaningful and not already known.** The actual
   discovery. Rare, and it usually requires evidence from outside the imaging
   dataset.

A project that does rung 1 and asserts rung 3 is the standard failure of this
literature. A project that does rung 2 honestly is a contribution **even when
the answer is "it was the scanner."** Negative results at rung 2 are among the
most valuable outputs available here.

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

Watch for the C3 error: verifying the *wrong* fact. "Multiple opinions exist
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


===== ideas/006/README.md =====
# Idea 006: Ask the chest-CT foundation model to diagnose a volume with no patient in it

Selected from scouting cycle 003, candidate 2.


===== ideas/006/idea_card.json =====
{
  "id": "C2",
  "search_mode": "B",
  "entry_point": 2,
  "title": "Ask the chest-CT foundation model to diagnose a volume with no patient in it",
  "question": "When every voxel inside the body contour is replaced with a constant and only the air, table, positioning aids and reconstruction field-of-view boundary are left, how much of the released chest-CT foundation model's abnormality AUROC survives?",
  "why_unasked": "The question is unasked because it is embarrassing to ask and cheap to answer, which is an unstable combination. Two habits keep it invisible. First, in 3D CT the analysis unit is the volume and the body fills most of it, so 'the background' is not a category anyone names - unlike histopathology, where whitespace is an explicit preprocessing concern and where background and site signatures are known to survive stain normalisation. Second, CT is trusted because it is calibrated: air is minus one thousand Hounsfield units everywhere, so it feels definitionally information-free. But air is not information-free. It carries the quantum noise magnitude set by the tube current, the noise correlation structure set by the reconstruction kernel, the reconstruction field-of-view boundary, truncation and beam-hardening streaks radiating from the body, the table and mattress, positioning aids, arm position, and the extent of the scan - and every one of those is a function of the scanner, the protocol, the technologist and the patient's size. Nobody asked because everyone assumes the answer, and the assumption has never been priced.",
  "rung": {
    "current": 2,
    "why": "This is a pure rung 2 instrument. It does not ask what biological thing the model found; it asks whether what the model found is present in a region that contains no biology at all. A positive result is a direct artifact demonstration.",
    "what_would_move_it_up": "Nothing here moves to rung 3, and that is deliberate. This candidate's job is to place a floor under every rung-3 claim made on this corpus: any concept whose body-excluded AUROC is materially above chance has that much of its apparent performance unattributable to anatomy until proven otherwise."
  },
  "suspected_signal": "Quantum noise magnitude (voxel standard deviation in air, which scales inversely with the square root of the tube-current-time product and therefore encodes the automatic-exposure-control response to the patient's attenuation, i.e. body habitus), the noise correlation structure imposed by the reconstruction kernel, the reconstruction field-of-view diameter and the resulting circular boundary, truncation and beam-hardening streaks whose amplitude scales with body size and arm position, and the presence and shape of the table, mattress and positioning aids. All of these are scanner-and-protocol properties, and all are visible to a convolutional or transformer encoder that sees the whole 480 by 480 by 240 grid.",
  "keystone_prerequisite": "The released CT-RATE volumes retain the region outside the patient's body, AND the released checkpoint's own preprocessing pipeline neither masks nor crops that region away - so that a body-excluded input is both constructible and in-distribution for the model rather than an out-of-distribution image whose score means nothing. The second clause is what my inference needs: if the pipeline already discarded the exterior, a body-excluded input would be a novel image type and any score on it would be uninterpretable.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "I fetched and read the official preprocessing script at raw.githubusercontent.com/ibrahimethemhamamci/CT-CLIP/main/scripts/data_inference_nii.py. It applies the per-volume rescale slope and intercept ('img_data = slope * img_data + intercept'), clips to 'hu_min, hu_max = -1000, 1000', resamples to 'target_x_spacing = 0.75, target_y_spacing = 0.75, target_z_spacing = 1.5' by trilinear interpolation, crops or pads to 'target_shape = (480,480,240)', and normalises by dividing by one thousand. There is no body mask, no lung mask, no thresholding to tissue, and no anatomical cropping anywhere in the pipeline; the full volume is processed. The lower clip bound of exactly minus one thousand Hounsfield units is the attenuation of air, which confirms the exterior is retained at full dynamic range rather than being floored away. The transverse extent kept is 480 voxels at 0.75 mm, i.e. 360 mm, which for a typical chest reconstruction field of view retains the peripheral air, the boundary and generally the table. RESIDUAL, stated plainly: I inferred the field-of-view arithmetic rather than measuring the actual body-to-frame ratio on a real CT-RATE volume, and a centred 360 mm crop could clip the table in large-field reconstructions. Measuring the distribution of body-fraction-of-frame over a sample of volumes is the first step of the experiment, not an assumption of it.",
  "dies_like_prior": "No prior failure mode applies, because no label enters the primary comparison. The readout is the drop in the model's own score between the full volume and the body-excluded volume of the same patient - the model measured against itself, which is the structural move that let idea 004 survive. Label quality enters only in the secondary AUROC arm, and it enters in the safe direction: CT-RATE's labels are RadBERT-extracted from reports and therefore noisy, but label noise attenuates a measured association toward chance. A body-excluded AUROC that is substantially above chance despite noisy labels is therefore a lower bound on the artifact, not an artifact of the labels. That asymmetry is the reason this candidate cannot die the way ideas 001, 002, 003 and 005 died.",
  "closest_prior_work": [
    {
      "citation": "Hamamci I.E. et al. Developing Generalist Foundation Models from a Multimodal Dataset for 3D Computed Tomography (CT-RATE, CT-CLIP, CT-CHAT).",
      "identifier": "arXiv:2403.17834",
      "verification": "INSPECTED (arXiv abstract record) plus INSPECTED preprocessing script in the official repository.",
      "what_it_did": "Released the corpus, the 18-abnormality labels and the CT-CLIP, VocabFine, ClassFine and RadBertClassifier checkpoints.",
      "what_it_did_not_do": "Reports zero-shot and supervised AUROC. Performs no region ablation of any kind and offers no evidence that the reported performance comes from within the body."
    },
    {
      "citation": "Shortcut Learning in Medical Image Segmentation.",
      "identifier": "arXiv:2403.06748",
      "verification": "SEARCH_SUMMARY_ONLY",
      "what_it_did": "Catalogues shortcut cues in medical imaging - annotations, ink markings, rulers, calipers, text burned into ultrasound.",
      "what_it_did_not_do": "The catalogued shortcuts are all marks a human placed on the image. The hypothesis here is different in kind: the shortcut is the physics of the acquisition recorded in empty space, which no human placed and no annotation removal would catch."
    },
    {
      "citation": "Histopathology shortcut and site-signature literature (e.g. Shortcut Learning in Glomerular AI, arXiv:2604.07936, and the general finding that residual site-specific signatures survive stain normalisation and bias predictions).",
      "identifier": "arXiv:2604.07936 and related",
      "verification": "SEARCH_SUMMARY_ONLY",
      "what_it_did": "Established in pathology that site and processing signatures survive normalisation and drive predictions, and that non-tissue background is a real channel.",
      "what_it_did_not_do": "This is the precedent that makes the question askable rather than absurd, and it is the honest source of the hypothesis. It has not been transferred to 3D CT, where the exterior region is far larger in absolute voxel count and where the 'background' is a calibrated physical measurement of scanner behaviour rather than a slide artifact."
    },
    {
      "citation": "Moreno-Aguado R., Magallon A., Moreno V., Fang Y., Yang G. Learning Robust Visual Features in Computed Tomography Enables Efficient Transfer Learning for Clinical Tasks.",
      "identifier": "arXiv:2604.04133",
      "verification": "SEARCH_SUMMARY_ONLY (the retrieved quotation is from a search synthesis of the PDF; my direct PDF fetch did not surface the relevant section).",
      "what_it_did": "Reports all evaluated CT foundation models performing near chance on an instance retrieval benchmark, and states that scanner manufacturer, acquisition protocol, reconstruction kernel, patient demographics and imaged extent 'can dominate the similarity structure of the embedding space, such that the most similar scans by cosine distance share acquisition characteristics rather than clinical findings.'",
      "what_it_did_not_do": "Establishes that acquisition dominates the embedding's similarity geometry. It does not localise that dominance to a spatial region, does not ablate anything, and does not convert the observation into a bound on benchmark AUROC. It is the strongest existing reason to expect this candidate to come back positive, and it is also the reason a merely qualitative result here would not be news - the contribution has to be the number, and the region."
    }
  ],
  "existing_assets": [
    "CT-RATE volumes, labels, metadata and reports in one repository, with a released supervised 18-abnormality classifier (ClassFine) so the whole study is inference-only.",
    "The official preprocessing script, read and confirmed, so the ablation can be inserted at exactly the right point in the pipeline.",
    "CT-RATE ships TotalSegmentator outputs (ts_seg) and anatomy_segmentation_labels, which give a body mask essentially for free; a simple minus-500 HU threshold plus largest-connected-component and hole-filling is an independent fallback that needs no learning.",
    "Idea 004 is already scoped to download 850 CT-RATE validation volumes. If those are on disk, this candidate's marginal data cost is zero.",
    "Published AUROC on the same validation split to compare the ablated number against."
  ],
  "smallest_decisive_experiment": "One afternoon of GPU time on volumes that are already being downloaded. Build the body mask two independent ways - the shipped segmentation and a threshold-plus-morphology rule - and report both, so the finding does not depend on one segmenter. Construct four inputs per volume: (A) unmodified; (B) body-excluded, every voxel inside the body contour set to a constant, exterior untouched; (C) exterior-excluded, the complement of B, every voxel outside the body set to minus one thousand HU with the table removed; (D) a scrambled control in which the exterior is replaced with the exterior of a randomly chosen different volume, which breaks the pairing while preserving the marginal statistics of exterior content. Run the released ClassFine checkpoint on all four. PRIMARY READOUT, no labels: per concept, the distribution of score change from A to B and from A to C, and the rank correlation between the A scores and the B scores across volumes - if the model's ranking of patients is preserved when the patients are removed, that is the whole result and it needs no ground truth. SECONDARY: AUROC of the B inputs against the released labels, per concept, with scan-clustered bootstrap intervals, reported against both chance and the published full-volume number. The D control is what distinguishes 'the exterior carries information about this specific patient' from 'the ablation produced a degenerate input that the model maps to a fixed prevalence-like prior' - if B and D behave identically, the effect is a prior, not a signal, and that is a different and much less interesting finding.",
  "standing_confounds_addressed": {
    "scanner_and_vendor": "NOT RULED OUT - IT IS THE HYPOTHESIS. A positive result is a demonstration that scanner and protocol signal is present outside the body and is being used. The design's job is to establish that, not to remove it. Reporting the body-excluded AUROC stratified by manufacturer says how much of it is vendor-level.",
    "acquisition_protocol": "Same - this is the suspected mechanism, not a nuisance.",
    "reconstruction": "Same, and partially separable: because CT-RATE contains multiple reconstructions of one acquisition (verified in idea 004's Stage 0 - 425 strictly clean geometry-matched kernel pairs), the exterior-only score can be compared across kernels on identical anatomy, which isolates the kernel's contribution to the exterior signal.",
    "site": "NOT ADDRESSED. CT-RATE is single-institution as far as I know, so site variation is limited, but this also means the result may understate what a multi-site corpus would show. State as a limitation, not a control.",
    "positioning": "PARTIALLY MEASURED. Arm position and table height are literally part of the exterior region and are therefore candidate carriers. The design can describe them by measuring the table position and body centroid, but it does not remove them - nor should it.",
    "habitus": "PARTIALLY ADDRESSED. Body size determines the body mask itself and therefore the size of the excluded region, so mask geometry leaks habitus even after the interior is blanked. MITIGATION, and it is essential: report a variant in which the body region is replaced with a smooth soft-tissue-valued ellipse of matched area rather than a constant, so the silhouette is destroyed while the exterior is preserved. Without this variant, a positive result is confounded by silhouette and the study is much weaker.",
    "prevalence": "ADDRESSED by the D control, which detects a degenerate collapse to a prevalence-like prior.",
    "referral_pathway": "NOT ADDRESSED, and it is a live alternative: if sicker patients get different protocols, exterior signal could encode the indication. The design cannot separate this and it must be stated.",
    "label_leakage": "NOT APPLICABLE to the primary readout, which uses no labels. In the secondary arm CT-RATE labels are RadBERT-extracted from reports, and that noise attenuates toward chance, so it cannot manufacture a positive."
  },
  "alternative_explanations": [
    "The ablated input is out of distribution and the model emits a near-constant per-concept prior that happens to beat chance because prevalence is skewed. EXCLUDED by the D control and by reporting the across-volume variance of the B scores - a prior has near-zero variance, a signal does not.",
    "The body mask is imperfect and leaks a rim of lung or chest wall. EXCLUDED by dilating the mask by increasing margins (5, 10, 20 mm) and showing the effect persists as the margin grows; if it decays to chance by 10 mm, it was leakage and the finding dies. This must be prespecified.",
    "The silhouette of the blanked body region carries the signal, so 'the exterior' is really 'the patient's outline.' ADDRESSED by the matched-ellipse variant. This is the most plausible innocent explanation and the design must run that variant to claim anything.",
    "Honest self-assessment: 'the model diagnoses a scan with no patient in it' is a headline, and the headline is doing work the measurement may not support. A body-excluded AUROC of 0.60 against a full-volume 0.75 is a genuinely important number; a body-excluded AUROC of 0.53 is a footnote dressed as a scandal. The result must be reported as a fraction of the full-volume performance with intervals, and the write-up should be drafted so that it reads honestly at 0.53."
  ],
  "anticipated_negative": {
    "classification": "decisive",
    "reasoning": "If body-excluded inputs give AUROC indistinguishable from chance across all 18 concepts with tight intervals, and the A-to-B rank correlation collapses, that is a clean, quotable robustness result for the corpus the field is standardising on: the reported performance comes from inside the patient. It meaningfully weakens a live and well-motivated worry rather than merely failing to confirm it. Because the intervals are computed on thousands of volumes with an inference-only pipeline, a null here will be tight rather than underpowered - but an equivalence margin must be prespecified so the null is reported as equivalence and not as non-rejection."
  },
  "sibling_disclosure": "C2 and C3 are two halves of one rung-2 audit of the same corpus: C2 asks whether non-anatomical signal is present in image space, C3 asks whether it is present in metadata space. They share a dataset and, if idea 004 proceeds, a download. They do not share a failure mode - C2 can be defeated by mask leakage or by an out-of-distribution collapse, C3 by neither - and a reviewer merging them would be trading two independent checks for one. C2 additionally overlaps idea 004 in infrastructure only, not in question.",
  "remaining_legwork": [
    "HuggingFace gated-access acceptance for CT-RATE, shared with idea 004 and already on that critical path.",
    "Measure the body-fraction-of-frame distribution over a sample of volumes and confirm the 360 mm crop retains the table and boundary - this closes the keystone's stated residual. Hours.",
    "Validate the body mask by visual inspection on 30 volumes and by agreement between the two independent mask methods. One day.",
    "Prespecify the mask-dilation series, the equivalence margin, and the multiple-comparison handling across 18 concepts before running anything.",
    "Time to first decision: two to three days after the volumes are on disk, and if idea 004 has already downloaded them, essentially immediately."
  ],
  "cross_domain": {
    "borrowed_construct": "The background-patch and site-signature test from computational pathology, where models are probed on tissue-free whitespace and residual site signatures are shown to survive stain normalisation.",
    "measurement_it_implies": "Ablate to the complement of the object of interest and re-run the frozen model, reporting performance on the object-free input as a fraction of full performance, with a scrambled-pairing control to distinguish signal from prior.",
    "what_changes_if_the_analogy_is_dropped": "Without it you would run gradient saliency on the full volume, observe that attention sits on the lungs, and conclude the model looks at the anatomy - which is exactly the standard failure the charter names, because saliency is not a controlled ablation and a model can be highly sensitive to a region it barely attends to. The borrowed construct changes the code: it says build the complement image and evaluate on it, which is a different experiment producing a number with an interpretation, not a picture. It also supplies the scrambled-pairing control, which I would not have thought to include from a saliency mindset. This is not decoration."
  },
  "scores": {
    "clarity": {
      "value": 5,
      "why": "One ablation, one frozen model, one number per concept, and the null is stated in the question. There is nothing to interpret about what was asked."
    },
    "identifiability": {
      "value": 4,
      "why": "The D control separates signal from prior, the dilation series separates signal from mask leakage, the matched-ellipse variant separates exterior content from silhouette, and the kernel-pair comparison isolates reconstruction. Held below 5 because a positive result names a region, not a cause: it would show non-anatomical signal exists without saying whether it is noise magnitude, table, or protocol, and because referral pathway remains unseparated."
    },
    "medical_relevance": {
      "value": 4,
      "why": "A model whose performance partly comes from outside the patient will fail on transfer in ways its benchmark cannot predict, and this is the corpus a growing number of chest-CT foundation models are evaluated on. Held below 5 because the study audits a benchmark rather than changing a clinical pathway."
    },
    "interest": {
      "value": 5,
      "why": "'We deleted the patient and it still worked' is intelligible to anyone and consequential if true. It is also genuinely uncertain - the pathology precedent says yes, calibrated CT intuition says no."
    },
    "prior_legwork": {
      "value": 4,
      "why": "Released checkpoint, released segmentations, verified preprocessing, published baseline numbers, and a download already scoped by idea 004. Short of 5 only because no CT precedent exists to inherit an analysis protocol from."
    },
    "feasibility": {
      "value": 4,
      "why": "Cap lifted, keystone INSPECTED_TRUE. Inference-only, no training, four forward passes per volume, mask construction is a threshold and a morphological operation. Held to 4 by CT-RATE's gated access and the size of 3D downloads, both shared with idea 004."
    },
    "data_readiness": {
      "value": 3,
      "why": "Public but behind a click-through research-use agreement (CC BY-NC-SA 4.0, no redistribution) whose approval mechanism remains unverified. Accessible with work."
    },
    "evaluation_readiness": {
      "value": 4,
      "why": "AUROC, clustered bootstrap and rank correlation are standard; the ablation-fraction metric and the equivalence margin need specification but not invention."
    },
    "negative_result_value": {
      "value": 4,
      "why": "A tight null is a genuine reassurance about a corpus the field is standardising on and is publishable as such. Held below 5 because a null is somewhat expected by the calibrated-CT intuition, so it moves less belief than the positive would."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Cap lifted by the keystone, held at 3 on the evidence. I found no CT background-ablation study, but 'I did not find it' is not proof, my searches did not cover MICCAI, SPIE or Medical Physics, and arXiv:2604.04133 shows the field is actively circling this territory. If someone has run a background ablation on CT-RATE, it would most likely appear in exactly the venues I did not search."
    }
  },
  "priority_score": 4.1,
  "priority_arithmetic": "0.20*4 (feas) + 0.15*4 (ident) + 0.15*4 (med) + 0.10*4 (legwork) + 0.10*5 (interest) + 0.10*5 (clarity) + 0.10*4 (neg) + 0.05*3 (data) + 0.05*3 (novelty) = 0.80+0.60+0.60+0.40+0.50+0.50+0.40+0.15+0.15 = 4.10",
  "regret": {
    "value": 5,
    "why": "Four forward passes per volume on a checkpoint that is already downloaded, answering a question that bounds every claim made on the corpus. If it comes back positive and nobody checked, that is the worst kind of hindsight."
  },
  "recommendation": "SHORTLIST",
  "unverified_claims": [
    "The actual body-fraction-of-frame in CT-RATE volumes, and whether the centred 360 mm crop retains the table. Inferred from the crop arithmetic; measurable in hours.",
    "Whether ClassFine inference is deterministic. Needed so that score changes are attributable to the ablation rather than to sampling. Shared with idea 004's noise-floor control.",
    "Whether CT-RATE's ts_seg outputs include a usable body or torso mask, or only organ classes. The threshold fallback removes the dependency but has not been validated on these volumes.",
    "Whether CT-RATE is genuinely single-institution. Assumed, not verified, and it materially affects how the site limitation is stated.",
    "That no background-region ablation of a CT foundation model has been published. Not established; MICCAI, SPIE, Medical Physics and Radiology: Artificial Intelligence were not searched.",
    "The exact content of arXiv:2604.04133's instance-retrieval section. The key quotation reached me through a search synthesis, not a direct read of the PDF, and it must be verified before being cited."
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

