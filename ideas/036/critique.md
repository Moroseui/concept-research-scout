FATAL OBJECTION: A prediction jump at a population-atlas border cannot identify model use of an internal vascular map because the border is not a cutoff-assigned treatment and is itself a locus of real, incompletely measured vascular physiology.
EVIDENCE: Liu et al., Scientific Data 2023, DOI 10.1038/s41597-022-01923-0 (watershed cases excluded; territory assignment not angiographic); ideas/036/keystone_screen.md; Momjian-Mayor & Baron, Brain 2005, DOI 10.1093/brain/awh366.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial critique

## 1. The proposed regression discontinuity does not identify the stated use claim

**Verified fact:** classical and geographic regression-discontinuity designs require a treatment or exposure that changes at a cutoff, plus continuity/local exchangeability of untreated potential outcomes around that cutoff. Territory membership is not an input supplied to the proposed nnU-Net and crossing the registered atlas line does not assign a treatment. The observable contrast is therefore a spatial discontinuity in model output, not an effect of territory membership.

**Verified medical fact:** arterial border zones are not exchangeable tissue separated only by a cartographic label. They are distal junctions of arterial supply and are specifically susceptible to hemodynamic failure and impaired embolus washout. Momjian-Mayor and Baron review this physiology in *Brain* (2005; DOI `10.1093/brain/awh366`). Matching CBF, CBV, MTT, Tmax, NCCT HU, and distance to core cannot establish that collateral routes, arterial arrival curves, bolus truncation, occlusion geometry, tissue history, or nonlocal context are continuous across the border.

**Verified atlas fact:** Liu et al. built the atlas from infarct distributions in 1,298 MRI cases, explicitly excluding infarcts “exclusively within watershed areas,” and acknowledge that territory classification used expert description rather than angiography (only 59% had MRA confirming a single relevant large-artery lesion). The deterministic 30-label map is thus not a patient-specific supply map and was not validated for the very border-zone estimand proposed here (Scientific Data 10:74, DOI `10.1038/s41597-022-01923-0`).

Placebo borders answer only whether arbitrary shifted curves also show jumps. They do not make physiology smooth at the true border, distinguish a learned atlas from a learned spatial/location prior, or distinguish either from use of nonlocal image evidence within the model's receptive field. Contralateral borders have different lesion and occlusion context and do not supply the missing counterfactual. Registration perturbations measure sensitivity to atlas placement, not construct validity.

Consequently, even a clean positive result supports only: **predictions are associated with a registered population-atlas boundary after adjustment for selected released channels.** It does not support the card's deliverable that the model “is using arterial-territory membership ... as a spatial prior.” The card itself admits the residual physiology but scores identifiability as if it were only a ceiling; it is fatal to rung 1.

## 2. Patient-specific anatomy is not an optional rung-2 enhancement

The card postpones anatomically variant cases to rung 2. That is backwards. Dissociation between the population atlas and patient-specific vascular supply is the observation that could discriminate a memorized textbook map from image-derived case evidence. On standard anatomy, atlas location, true supply, lesion prevalence, training-label geometry, and stereotyped spatial coordinates all align.

ISLES'24 releases single-phase CTA, but the inspected materials do not provide patient-specific perfusion-territory labels or selective arterial perfusion imaging. Inferring territories from the same CTA/perfusion inputs used by the model would introduce another model and another construct-validation problem. Without an independently measured patient-specific map or a valid intervention on the alleged internal variable, the original use question is not identified.

## 3. Leakage and model choice are unresolved

**Verified asset fact:** a frozen winning checkpoint and probability-export path exist, but its public weights were trained on the public challenge training cohort; the hidden 98-case test set is unavailable. Auditing that checkpoint on the same 150 public cases risks measuring memorized training-mask geography. It cannot establish held-out behavior.

Training a new model with 30 held-out cases avoids that leakage but changes the object from “the winning model” to a lab-trained model, leaves roughly 120 training cases on a task whose winner achieved only Dice 0.285 ± 0.213, and requires the performance threshold to be frozen before training. Cross-fitted out-of-fold predictions are possible, but every fold then represents a different fitted model. None of these repairs the causal interpretation above.

The claim of “about 10^4” usable matched pairs is not a sample-size argument. Voxels share patients, borders, receptive fields, and preprocessing; effective sample size is governed principally by patients and boundary segments. A patient-cluster bootstrap alone does not show power for a narrow discontinuity after overlap, registration-QA, and bandwidth gates. The proposed decisive null is therefore overstated: registration blur, low model skill, limited common support, and atlas misplacement can all erase a true effect.

## 4. Prior work and novelty

The atlas and deliberate anatomical-prior segmentation methods establish substantial nearby legwork. Robben et al. (Medical Image Analysis 2020; DOI `10.1016/j.media.2019.101589`) establish final-infarct prediction from CTP, but do not establish this audit. I did not locate a primary study with this exact atlas-border analysis; that is **not proof of novelty**. More importantly, absence of an exact duplicate cannot rescue a non-identifying estimand. The candidate should not claim an econometric inferential guarantee.

## 5. Medical relevance and endpoint

The motivation—failure under variant anatomy—is medically intelligible, but the proposed endpoint never measures performance in variant anatomy or even prediction error. Labels are deliberately excluded from the primary readout. A discontinuity could be anatomically helpful, harmful, or irrelevant; it does not show that the prior “overrides case evidence.” The clinical-safety language outruns the endpoint.

The endpoint is also underspecified: territory hierarchy, border classes, signed orientation, probability scale, bandwidth, matching algorithm, caliper, overlap criterion, aggregation across boundary surfaces, and multiplicity across borders are not frozen. Different choices can reverse or average away heterogeneous effects. These are repairable analytic defects, but they are secondary to the identification failure.

## 6. Plain-pitch fidelity

The pitch fails fidelity in two places. “Two neighboring tissue spots look hemodynamically identical” translates observed matching into physiological identity, despite the card's explicit unreleased-physiology residual. “The model imposes anatomy textbook knowledge on individual patients” states the desired use conclusion as what a positive test establishes, although the design can show only a conditional spatial association. The statement about risk to “the many people” with variant vessels is unquantified and the study contains no variant-anatomy cohort. Hedges and the rung-1 limitation did not survive translation.

## 7. Easier version and existing low-hanging fruit

The low-hanging-fruit formulation is an **out-of-fold error audit by atlas border distance**, not a use test. ISLES'24 already supplies the 150 public multimodal cases, follow-up-MRI-derived masks, NCCT-space perfusion maps, and official evaluation machinery; the atlas and nnU-Net code also exist. Train prespecified cross-validation models, retain out-of-fold probabilities only, register the atlas without viewing model outputs, and ask whether calibration error, false-negative burden, or soft Dice contribution worsens in prespecified border-zone bands versus territory-interior tissue after stratifying by lesion status and perfusion severity. Registration QA and patient-level uncertainty remain mandatory. This uses labels rather than avoiding them, because error—not an unexplained output jump—is the medically relevant endpoint.

That study would reveal a benchmark failure mode and could motivate a later patient-specific-territory study. It must not be narrated as proof that the model carries or uses a vascular map. Because the deliverable changes from internal use to spatial error concentration, the claim-identity rule requires a separate candidate.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: On strictly out-of-fold ISLES'24 predictions, are calibration and segmentation errors systematically worse in registered arterial border-zone bands than in perfusion- and lesion-status-matched territory interiors?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—if registration and effective patient support pass prespecified gates, it directly tests a clinically recognizable spatial failure mode using existing images, labels, atlas, and training code, with either direction informative for benchmark design.
