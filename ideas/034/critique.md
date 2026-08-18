FATAL OBJECTION: The proposed observational stage 2 cannot distinguish use of the slab boundary itself from use of the perfusion evidence that necessarily disappears at that boundary, so it cannot support the deliverable sentence.
EVIDENCE: Official ISLES'24 repository task definition; `ideas/034/idea_card.json` (`use_vs_association`, `standing_confounds_addressed`); ISLES 2018 analysis, PMCID PMC8240494.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial review

## 1. What is verified, and what is not

Verified fact: ISLES'24 asks algorithms to predict follow-up infarct lesions from acute NCCT, CTA, CTP/perfusion maps, and clinical tabular data. The official repository lists Dice, absolute volume difference, absolute lesion-count difference, and lesion-wise F1 as ranking metrics (official repository: https://github.com/ezequieldlrosa/isles24; challenge paper: arXiv:2408.10966).

Source-supported fact, with the provenance limitation already recorded in `keystone_screen.md`: the official challenge forum contains a report that case 0019 has 1,685 labeled lesion voxels outside the CTP extent, and the organizer says such voxels are not masked from evaluation. This verifies existence in kind, not the card's population threshold of overflow greater than 5% in at least 10% of cases.

Verified prior legwork: limited CTP coverage is not a hidden problem newly imported from remote sensing. The retrospective ISLES 2018 analysis states that CTP coverage ranged from 2.4 to 16 cm and that lesion prediction was performed only within the acquired image volume; it explicitly discusses the effect of limited coverage on absolute volumetric error (PMCID PMC8240494; PMID 33957774; DOI 10.1161/STROKEAHA.120.030696). A prior benchmarking tool likewise evaluated CTP against DWI with 4.4–16 cm coverage (PMCID PMC5076783; DOI 10.1177/0271678X15610586). The exact ISLES'24 whole-cohort census may still be unreported, but the card's claim that the challenge community has not asked what the sensor saw is too broad and its `why_not_done` story is speculation.

## 2. Fatal identifiability failure in the model claim

The deliverable says the model uses the *support boundary* as a determinant, “rather than the ischemia.” The proposed comparison is across patients at atlas locations that happen to be inside versus outside their CTP slabs. That exposure changes at least three things together:

- availability of every perfusion value;
- acquisition protocol/scanner and cranio-caudal positioning;
- anatomical and stroke-population mix near each slab edge.

Matching on NCCT appearance, CTA appearance, atlas location, and lesion volume cannot make the missing perfusion evidence equal. Indeed, the card concedes that “out-of-slab voxels genuinely have less evidence.” A prediction discontinuity can therefore be caused by ordinary use of local CBF/Tmax evidence; it does not show that the network treats the padding/support indicator as a spatial stopping rule. Conditioning on lesion volume also uses the follow-up outcome and does not restore exchangeability.

Calling the estimand merely “how models behave” does not repair the mismatch. The title, question, rung, deliverable sentence, and plain pitch all make a use claim contrasting the sensor edge with the injury edge. The observational estimator identifies an association between prediction and evidence availability, not use of the boundary cue. A within-case crop intervention would still remove true perfusion evidence while moving the boundary and would introduce a training-distribution shift; it has the same mechanistic ambiguity in a different form. No specified obtainable contrast moves the boundary while preserving the perfusion evidence whose disappearance defines that boundary.

This dies by the portfolio's recurrent `IDENTIFIABILITY_FAILURE`: the claimed mechanism cannot be separated from a co-varying acquisition property. Removing stage 2 changes the deliverable from a model-use claim to a dataset/evaluation audit, which is a different question and therefore a successor under the claim-identity rule in `evidence/decisions.md`.

## 3. The “sensor-respecting performance ceiling” is mislabeled

For a prediction constrained to support \(S\), the label clipped to \(S\) gives an oracle maximum Dice of \(2|Y \cap S|/(|Y|+|Y \cap S|)\). That is a valid *CTP-support-constrained oracle score*. It is not a ceiling for an ISLES'24 algorithm, because an eligible algorithm can use NCCT, CTA, anatomy, and clinical variables rather than confining predictions to the CTP slab. The official task is not CTP-only.

The analogous minimum absolute volume difference is also not generally determined by overflow. A support-confined mask may match the total lesion volume by adding false-positive voxels inside the slab, producing zero absolute volume difference whenever enough support volume exists. Thus “minimum absolute volume difference attainable by ANY prediction confined to the support” may be zero even when much of the lesion lies outside support. If the intended oracle forbids false positives or fixes the in-support prediction to the in-support label, that is a different, explicitly constrained quantity—not the metric's mathematical minimum.

Nor does either oracle say “how much [overflow] could move the leaderboard.” Actual rank sensitivity requires team predictions (or at least controlled synthetic prediction families), all four metrics, per-case rank aggregation, and the hidden test cohort. Training-set oracle penalties do not determine a leaderboard displacement. This is repairable within the dataset-audit successor by reporting descriptive overflow, a clearly named CTP-confinement Dice penalty, and metric sensitivity under explicit counterfactual scoring rules; it does not rescue the current model-use question.

## 4. Relevance, circularity, leakage, access, and cost

There is no concept-label circularity: the label is appropriately the object being audited. There is also no training leakage in the model-free census. But stage 2's proposal to compare a model on the same 149 labeled cases used to characterize the phenomenon is underspecified: it names no frozen checkpoint, training cohort, held-out split, or independently preserved evaluation set. The card itself says the “shared audit model” may not exist. Therefore the stated under-five-GPU-hour estimate omits model acquisition/training and cannot be credited as concrete feasibility.

The stage-1 data are available and the compute is genuinely low. The 99 GB archive noted in the keystone screen is manageable, and derivative maps plus masks may be obtainable more cheaply from the mirror. No new annotation is needed. These strengths favor the narrower audit; they do not compensate for the invalid mechanistic endpoint.

The negative-result claim is only partly sound. Near-zero overflow would be useful reassurance about the *149 released training cases under the chosen support definition*. It would not establish that “ISLES'24's sensor coverage matches its scoring target” on the hidden test cohort unless the test geometry and overflow distribution are released or organizer-verified. A stage-2 null would be sensitivity-limited because an observational discontinuity test can miss diffuse, learned handling of missing perfusion or be underpowered in the small joint-support strata.

## 5. Plain-pitch fidelity failure

The pitch does not preserve the card's limitations:

- “their main sensor never saw” collapses a multimodal task into CTP; NCCT and CTA still image those locations.
- “each model must invent its own policy there” overstates the dilemma: a model may infer from NCCT, CTA, anatomy, clinical variables, and learned spatial priors rather than merely truncate or hallucinate.
- “how much that could move the leaderboard” promises an analysis not specified or supported by the proposed oracle calculation.
- “checks whether models draw their predicted damage boundary at the sensor's edge rather than the injury's” states the causal contrast more strongly than the admitted evidence-availability confounding permits.
- “Either outcome changes how results on this benchmark should be read” generalizes a training-cohort finding to the unreleased test cohort.

These are material overclaims, not harmless simplifications.

## 6. Easier formulation and existing low-hanging fruit

The low-hanging-fruit experiment is a model-free, training-set coverage audit. All required inputs already exist: 149 released labels, raw perfusion maps, NCCT-space derivative maps, official evaluation code, and a named positive case from the challenge forum. It should preregister at least two support definitions (raw 4D spatial extent and nondegenerate-map support), require agreement or adjudicate discrepancies, report per-case lesion fraction and lesion-component count outside support, stratify by scanner/protocol where metadata allow, and show sensitivity to registration/erosion-dilation of the support edge.

The primary endpoint should simply be the empirical proportion of released cases with more than 5% of labeled lesion volume outside CTP support, with a binomial interval and the full distribution. Secondary outputs can include a precisely named CTP-confinement oracle Dice and rescoring of public predictions if such predictions are actually available. Do not call anything a leaderboard effect without prediction submissions and the official aggregation. Confirm the forum posts directly through registered access before publication.

This is worth doing because it cheaply quantifies a documented but currently unmeasured evaluation condition in the released ISLES'24 cohort and can motivate an observed/unobserved-region metric breakdown. Its claim is narrower: it says what fraction of the reference target lacks CTP coverage, not what a multimodal model uses.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: In the 149 released ISLES'24 training cases, what fraction of follow-up lesion volume and lesion components lies outside acute CTP support, and what Dice constraint does that impose specifically on predictions confined to that support?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—because the data, labels, and metric code already exist, and a one-session census would replace an organizer-acknowledged anecdote with a cohort-level benchmark-integrity result, provided claims remain training-cohort and CTP-coverage specific.
