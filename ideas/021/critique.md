# Critique — Idea 021: The healthy hemisphere is the ruler

```
FATAL OBJECTION: The claimed edit/readout disjointness does not survive the pipeline's own
intensity normalization — under nnU-Net's default per-image z-score for non-CT channels, a
contralateral-only scaling deterministically changes the affected side's post-normalization
inputs before the model runs, and simultaneously deletes the "absolute values" null arm.
EVIDENCE: MIC-DKFZ/nnUNet documentation/explanation_normalization.md ("zscore ... separately
for each train case" for everything except CT).
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

---

## 1. The decisive objection: the preprocessing already couples the hemispheres

The card's identifiability argument rests on one sentence: *"no pathway from edit to
readout exists except through a learned cross-hemispheric reference."* That sentence is
false, or at best contingent on an uninspected fact, because a normalization step sits
between the edited NIfTI and the network.

The card's stand-in model is a self-trained nnU-Net ("same recipe family as the winner").
nnU-Net's own documentation states the default normalization is **CT-scheme (fixed,
dataset-level statistics) for channels declared CT, and per-image z-score — "z-scoring
(subtract mean and standard deviation) separately for each train case" — for everything
else** (verified 2026-08-17 at
https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/explanation_normalization.md).
Deconvolved perfusion maps are not CT-attenuation channels; under a default recipe they get
per-image z-score. Both horns of the dilemma damage the design as written:

**Horn A — per-image z-score (the default).** Scaling contralateral CBF/CBV by factor *s*
changes the whole-image mean and standard deviation. Every affected-side voxel's
post-normalization value therefore changes deterministically, with no learning involved.
A positive "affected-side response to contralateral-only edits" is manufactured by the
preprocessing arithmetic; the model could be doing zero cross-hemispheric computation and
the readout would still move. Worse, the artifact has exactly the signature the hypothesis
predicts (affected-side output depends on contralateral values), so no amount of
dose-response rescues it. And the null arm collapses: after per-image z-score the model
*cannot* see absolute perfusion values — the card's advertised two-sided answer ("null ⇒
the model reads absolute values") is unavailable by construction. The card's alternative
explanation #1 ("the model normalizes globally") gestures at this but locates it inside the
model, where partial-area edits could separate it; located in preprocessing it is a
deterministic function the partial-area control does not remove.

**Horn B — fixed dataset-level normalization (CT-scheme or custom).** Then edit/readout
disjointness holds and the design works as stated — but the experimenter *chose* the
normalization, and the choice largely predetermines which answer is available. Since
challenge submissions each froze their own preprocessing (the winning team's paper is
literally titled "How We Won the ISLES'24 Challenge by Preprocessing," arXiv:2505.18424,
and does not disclose its intensity-normalization details; its windowing thresholds are
quoted as relative clinical values such as "CBF < 30%"), the stand-in assumption (card
residual assumption 2) becomes much heavier: the study characterizes one recipe's answer,
and the reference frame may live in *preprocessing* for some submissions and in the
*network* for others.

This is the wrong-keystone pattern the charter warns about, in its fourth costume. The
keystone screen verified co-registration (the nearest checkable thing, and genuinely true).
The load-bearing fact for identifiability is different: **the frozen pipeline's intensity
normalization scheme, which determines whether the edit is disjoint from the readout at the
network's input.** It was never inspected — it could not be, because the "official baseline
recipe" the card lists as an existing asset does not exist (keystone screen already
established the official repo contains only evaluation utilities), and the winner released
no code or checkpoint (search 2026-08-17: none found).

**The repair, which preserves the question.** Because the model is self-trained, the
normalization is under the study's control. Pin it: either (a) use fixed, cohort-level
normalization constants for the perfusion channels, frozen before any edit, so that
per-image statistics cannot transmit the edit; or (b) compute per-image statistics on the
*unedited* image and apply them to the edited one, making preprocessing a fixed function
per case. Either pin restores true disjointness. The question then becomes, stated
honestly: *does the network compute a mirror-specific contralateral reference beyond
whatever global standardization preprocessing already provides?* That is still the
interesting question — per-image z-score is a whole-image reference contaminated by the
lesion itself, whereas the clinical rCBF convention (Campbell 2011, PMID 21980202, verified
2026-08-17: relative CBF < 31% of mean contralateral, AUC 0.79 vs 0.74 for absolute CBV)
is mirror-specific precisely because the healthy hemisphere is uncontaminated. Mirror vs
whole-image is a real, clinically meaningful distinction, and the partial-area and
hemisphere-specific controls in the card are the right instruments for it. A free bonus
contrast falls out: a *global* (both-hemisphere) scaling under pinned normalization tests
whole-image-reference behavior directly and costs nothing extra.

## 2. The null was overstated even before the normalization problem

With the positive control passing, a gated null licenses "the model does not use
contralateral values," not "the model reads absolute perfusion values." Ipsilateral spatial
context (lesion texture, gradients, Tmax topology on the affected side alone) is an
unconsidered third reading that survives any null. After the repair in §1 the null becomes:
no mirror-specific reference beyond global standardization — a type-1 decisive negative for
the *mirror* hypothesis, but the card's advertised consequence ("fragility to cardiac
output and injection variation") no longer follows, because global standardization already
removes global hemodynamic scale. `negative_result_value` 4 → 3; `anticipated_negative`
must be rewritten.

## 3. Prior work: the delta survives, but the framing does not

The card says interpretability work on hemispheric normalization in stroke models "was not
found." Targeted search (2026-08-17) confirms no intervention-grade audit of a trained
model's reference frame — the novelty claim survives narrowly. But an adjacent literature
the card ignores has to be engaged, because it changes the prior: the field extensively
**hand-engineers** the contralateral reference into stroke networks. Symmetric modality
augmentation — feeding the flipped contralateral hemisphere as an extra channel — improved
Dice by 9–13 points in brain lesion segmentation (arXiv:1907.08196); symmetry-sensitive
CNNs for CTA stroke detection and contralateral-feature LVO detectors are established
(e.g., Nature Communications 10.1038/s41467-023-40564-8 and the reviews at
PMC9678444). Two consequences. First, the exact delta must be restated against this
literature: *the field bolts the mirror on because it suspects plain models do not discover
it; nobody has tested the suspicion on a plain model with an intervention.* Second, the
hand-engineering gains are indirect evidence that the expected answer is "no mirror
reference" — which is fine (the null is decisive after §2's rewrite), but the card's
"a well-trained model has every incentive to discover it" prose leans the other way without
acknowledging this evidence.

## 4. Feasibility is overstated; power is unexamined

- **No recipe, no checkpoint.** The "official baseline recipe" asset is already refuted by
  the keystone screen; today's search confirms the winning team released neither code nor
  checkpoint. Training is from scratch, recipe self-assembled. `prior_legwork` 4 → 3.
- **The benchmark's signal is weak.** The winning model's hidden-test Dice is 0.285 ±
  0.213 (arXiv:2408.10966; confirmed in arXiv:2505.18424). Final-infarct prediction on
  ISLES'24 barely works. The paired within-case delta on predicted volume is the right
  readout for a noisy model, but the card contains no minimum-detectable-effect reasoning
  at n = 40 held-out cases against a model whose outputs have this much variance. The
  revision must add an MDE estimate (from validation-fold prediction variability) before
  the 40-case experiment is called decisive.
- **Compute** (2–3 days training shared with c01, ~10 GPU-hours of edits) is plausible on
  the Colab Pro+ constraint with checkpoint-resumable nnU-Net training; not an objection,
  but it is the *whole* budget — the discriminator gate and symmetry-QC tooling are
  additional unbudgeted work.

## 5. Edit realism: the physiologic cover story is wrong, and one alternative is missing

The card defends the edit as mimicking "natural cardiac-output variation." Cardiac output
varies **globally** — it scales both hemispheres. No physiologic process uniformly scales
one hemisphere's CBF with a sharp midsagittal boundary *except unilateral carotid or
proximal vessel disease* — which is common in exactly this cohort. That creates an
unlisted alternative explanation: scaling the contralateral hemisphere *down* into the
low-physiologic range may read to the model as **bilateral or contralateral ischemia**,
changing the affected-side prediction through lesion-detection competition or laterality
reassignment, not through a reference computation. This is diagnosable — up-scaling and
down-scaling arms should behave asymmetrically under this mechanism and symmetrically
under pure normalization — so the fix is to add the up/down asymmetry contrast to the
preregistered analysis and this alternative to the card's list. Relatedly, the edit
touches only perfusion channels while NCCT/CTA channels stay frozen; the resulting
cross-channel inconsistency (hemisphere hypoperfused on CTP, normal on CTA) is part of
what the real-vs-edited discriminator must be shown to pass, and should be named in the
gate's definition rather than left implicit.

## 6. Smaller defects

- **Bilateral-disease exclusion is underspecified.** Follow-up lesion masks cover the acute
  lesion only; chronic contralateral infarcts (which corrupt the mirror) are not in any
  released mask. The symmetry-quality flag needs a concrete, automatic definition (e.g.,
  contralateral CSF/encephalomalacia volume by threshold, or mirror-residual magnitude) or
  the exclusion is a hand-wave.
- **The midline exclusion margin does not address receptive fields.** At the 3D U-Net
  bottleneck the receptive field spans both hemispheres nearly everywhere; a margin around
  the plane removes edge artifacts, not cross-hemisphere information flow. That flow *is*
  the hypothesized mechanism, so this is not fatal — but the card should stop implying the
  margin localizes anything; the dose-by-area control is what does the discriminative work.
- **Dataset concentration.** This is one of two ISLES'24 candidates sharing a trained model
  (with c01) — within the charter's two-per-dataset limit, but the shared-model coupling
  means a training failure kills both; note it in planning.
- **License.** Zenodo release is public noncommercial; no DUA gate — acceptable, record the
  restriction.

## 7. Score adjustments

- `identifiability` 4 → **2 as written** (the §1 pathway is real and unmitigated); restored
  to 4 by the normalization pin, which is why the decision is revision, not rejection.
- `negative_result_value` 4 → 3 (§2).
- `prior_legwork` 4 → 3 (§4; nonexistent baseline recipe already flagged by the keystone
  screen but never propagated to scores).
- `feasibility` 4 → 3 until the MDE analysis exists; the INSPECTED_TRUE keystone
  (co-registration) is genuine, but the identifiability-load-bearing fact (normalization)
  was not part of it — under the charter's intent, the cap-lifting inspection should cover
  the fact the inference actually needs.
- `novelty_confidence` 3 stands (delta survives §3, restated).

## 8. The easier versions

- **Zero-GPU Stage 0 (do this regardless):** freeze the recipe and *state the normalization
  scheme in the card as a design pin*. Half the original question — "is the reference frame
  in the preprocessing?" — is answerable by inspection for any pipeline whose code exists,
  today, at zero cost. For the field's pipelines it is unanswerable only because winners
  did not release code; that fact (verified today) is itself worth one line in any
  write-up.
- **Cheapest decisive contrast:** under pinned normalization, three arms — global scaling
  (both hemispheres), contralateral-only scaling, partial-area contralateral scaling —
  separate "no reference," "whole-image reference," and "mirror reference" with the same
  machinery the card already specifies. This is not a different study; it is the card's
  study with one added (cheap) arm and the confound removed. There is no meaningfully
  smaller version that still answers the question: an observational correlation across
  patients (contralateral CBF vs error) would be confounded by everything the paired design
  exists to remove, and is not worth doing.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Under normalization pinned to the unedited image,
does the network's affected-side final-infarct prediction respond to mirror-specific
contralateral perfusion changes beyond whole-image standardization — i.e., has it learned
the rCBF convention's mirror reference, or only a global gain control?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — same deliverable sentence, sharpened; the
mirror-vs-global distinction was already implicit in the card's alternative #1.
IS IT ACTUALLY WORTH DOING? YES — the field hand-engineers the mirror reference on the
belief that plain models lack it, nobody has run the intervention that tests the belief,
and both answers change how ISLES'24-class models should be preprocessed and trusted.
```

## Sources

- nnU-Net normalization defaults: https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/explanation_normalization.md
- ISLES'24 winner ("How We Won the ISLES'24 Challenge by Preprocessing"): https://arxiv.org/html/2505.18424v1
- ISLES'24 challenge report (winner Dice 0.285 ± 0.213): https://arxiv.org/abs/2408.10966
- Campbell et al. 2011, rCBF < 31% of mean contralateral: https://pubmed.ncbi.nlm.nih.gov/21980202/ / https://www.ahajournals.org/doi/10.1161/strokeaha.111.618355
- Symmetric modality augmentation (+9–13 Dice): https://arxiv.org/pdf/1907.08196
- Contralateral-feature LVO detection: https://www.nature.com/articles/s41467-023-40564-8
- Deep learning stroke imaging review (contralateral-comparison approaches): https://pmc.ncbi.nlm.nih.gov/articles/PMC9678444/
- Official ISLES'24 repository (no training recipe): https://github.com/ezequieldlrosa/isles24
