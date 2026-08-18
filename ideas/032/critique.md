FATAL OBJECTION: The graph-edge intervention cannot identify use of proximal collateral reserve because it changes putative arterial patency while freezing the downstream CTA enhancement and perfusion consequences that make patency physiologically meaningful.
EVIDENCE: Frölich et al., Stroke 2012, DOI 10.1161/STROKEAHA.112.668889; idea card `use_vs_association`; TopCoW arXiv:2312.17670v4 §2.4.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial critique

## 1. The claimed mechanism is not identified

The card asks whether a model uses Circle-of-Willis (CoW) redundancy **as a reserve for maintaining flow**. Its intervention adds or removes a communicating-artery-like structure in CTA while explicitly preserving distal CTA enhancement and every perfusion map. This separates the drawn vessel from the very evidence that it carries blood.

That is not a clean isolation of topology. It is a cross-modal contradiction. In real anatomy, whether an alternate route supplies a threatened territory depends on flow direction, pressure gradients, inlet and outlet conditions, distal resistance, autoregulation, occlusion completeness, and bolus timing. Patient-specific CoW flow models therefore use measured velocity or flow information and boundary conditions, not topology alone (Moorhead et al., DOI 10.1109/IEMBS.2004.1403261; Lassila et al., PMID 32974727; Brindise et al., PMID 36173034). Frölich et al. directly showed why a static bright lumen is insufficient in acute occlusion: time-resolved 4D CTA distinguished antegrade from retrograde collateral filling with 100% sensitivity and 97.9% specificity against angiography, whereas single-phase CTA had 40% sensitivity and 87.2% specificity (DOI 10.1161/STROKEAHA.112.668889).

Consequently:

- A positive response establishes sensitivity to an anatomically placed CTA intensity structure, not use of a patent alternate route or collateral reserve.
- A null does not establish that the model ignores a visible proximal route. A multimodal model could reasonably defer to unchanged CTP and distal CTA evidence, or the synthetic route could be recognized as incompatible with those channels.
- A monotone response with the proposed graph score does not rescue the interpretation, because the renderer itself changes vessel extent, local contrast, junction geometry, and distance to the skull base monotonically with the nominal caliber.

The topology-neutral shams address only generic bright-voxel amount and perhaps caliber. They cannot match anatomical location, junction structure, route length, relation to named parent vessels, or cross-modal consistency while differing only in connectivity. Thus the score of 4 for identifiability is unsupported.

Repair would require either (a) a validated, physiologically conditioned counterfactual generator that jointly changes CTA dynamics and perfusion, in which case topology is no longer the isolated cause, or (b) natural anatomically varying cases with measured flow, which supports association rather than the proposed within-case use claim. Either changes the decisive question.

## 2. The graph quantity is not the medical construct

The proposed caliber-weighted max flow is a graph surrogate, not a verified measurement of hydraulic reserve. The card does not define edge capacity as a physical function, source pressures, sinks/territories, directionality, collateral recruitment, or how an LVO mask intersects a multiclass CoW graph. A minimum centerline radius measured after resampling into NCCT space is especially unstable: resistance in an idealized cylindrical vessel scales approximately with the fourth power of radius, while even simplified CoW simulations require flow equations, wall and boundary assumptions, and calibration. Primary modeling work reports that simplified Poiseuille and 3D models can allocate materially different flow through communicating arteries (Moorhead et al., PMID 17271780), and calibrated CoW models use in-vivo velocity data and modeled outlet conditions (Passerini et al., PMID 19043621).

Therefore edge-disjoint path count and an unspecified max-flow capacity may rank graph morphology, but calling their signed change “proximal collateral reserve” outruns validation. The rung-1 deliverable itself embeds this physiological gloss; external agreement only at rung 2 cannot retroactively validate the confirmatory rung-1 variable.

## 3. The keystone screen leaves the needed cases and labels unverified

Verified facts from the existing screen are useful but adverse:

- The Zenodo release (record 16813698) states that `cow-msk.nii.gz` is an automatically generated multilabel CoW mask. It gives no case-level manual QC or branch-fidelity claim.
- The cited TopCoW taxonomy separates Acom and bilateral Pcom, but an actual released ISLES mask has not been inspected to establish that its values implement that taxonomy.
- TopCoW's external ISLES evaluation selected only 26 CTA cases “whose CoW were not occluded within the ROI” (arXiv:2312.17670v4, §2.4). That excludes the most relevant stratum.
- Even expert annotations have lower agreement for Acom/Pcom than for many larger components (TopCoW supplementary §S6), and the released masks are resampled into NCCT space, undermining subvoxel caliber claims.

The proposed visual review of 30 masks is described as “tool QA” rather than annotation, but visual raw-CTA/mask agreement is still an annotator-dependent validity judgment. If those judgments determine eligibility or whether a branch is real, they are new labeling burden under the charter regardless of the name given to them. If they do not determine anything, they cannot establish fidelity. Automatic graph validity can detect disconnected or impossible masks; it cannot tell whether a plausible labeled Pcom exists in the image.

The threshold of at least 20 cases in each of two editable families is also asserted without a power calculation. With only 149 released training cases and an unknown number of occlusion-adjacent usable CoWs, the proposed 40 held-out cases may overlap the entire eligible pool. There is no frozen training/development/test allocation or patient-level power target.

## 4. The target model and endpoint do not exist yet in operational terms

“An ISLES'24 model” is not a reproducible target. The card names no architecture, preprocessing, training split, checkpoint, checkpoint license, held-out performance gate, or proof that CTA contributes nontrivially. The published winning method used a large residual nnU-Net with CTA and perfusion-map windowing (arXiv:2505.18424v2, Table 1), but its paper and arXiv record provide no checkpoint. The official repository provides data layout and evaluation code, not a trained winning model (official repository: https://github.com/ezequieldlrosa/isles24). “Under 20 GPU-hours after model training” excludes the largest unknown cost and is therefore not an honest compute estimate.

Nor is the response endpoint specified. The model produces a 3D final-lesion mask, but the card does not say whether the primary statistic is total predicted volume, affected-territory volume, voxelwise probability in a preregistered downstream territory, or an official challenge metric. “Output changes predicted by the signed change” is not enough: adding collateral capacity could plausibly shrink predicted infarct only if treatment, time-to-reperfusion, occlusion completeness, and downstream state are held in an interpretable regime. ISLES'24 ground truth is follow-up infarct after treatment, not untreated tissue fate; the winning-method paper states follow-up is 2–9 days and the challenge paper describes final post-treatment prediction (arXiv:2505.18424v2 §2; arXiv:2408.10966). That makes a universal signed endpoint clinically underdetermined.

There is no concept-label circularity in the narrow sense—the final-infarct label was not made from the CoW mask—but the intervention is circular at the measurement level: an automatic mask supplies both the asserted graph concept and the geometry used to render the pixels that are then said to demonstrate use of that concept. Mask errors can therefore manufacture both X and the intervention without independent truth.

## 5. Prior-work and portfolio overlap

The exact model-use experiment was not found in the primary sources inspected; that is not proof of novelty. Adjacent clinical work already studies CoW variant classes and outcome, while fluid-dynamic work models alternate-flow activation. The possible delta is an AI-use audit, but the present design does not validly measure it.

More importantly, the repository already recorded a near-identical proposal during scouting cycle 001: “graph-theoretic betweenness of the Circle of Willis as a network-resilience reserve.” It was dropped because static CTA may not establish communicating-artery patency reliably and because distal collateral reach was considered the more local, identifiable question (`ideas/scout-isles24-001/log_scout.txt`). The current card replaces betweenness with path count/max flow and adds synthetic edits, but does not cure static CTA's inability to establish functional patency. It therefore repeats a known failure mode rather than explaining a changed condition.

## 6. Negative-result value and relevance

The claimed negative-result value is too high. Even after renderer sensitivity controls, a null remains ambiguous among at least four explanations: absent model use, dominant unchanged perfusion evidence, failure of synthetic CTA to represent a patent route, or insufficient CTA contribution by the chosen model. A positive result is interesting as a robustness finding but cannot support the physician-legible reserve claim. The medical motivation is strong; the proposed answer is not medically interpretable enough to justify two weeks plus model training and new expert QA.

## 7. Plain-pitch fidelity

The pitch has a named overclaim. It says connectivity will change “while keeping the total amount of visible vessel ... fixed.” The technical design says topology-neutral shams match volume and intensity; it does not state that each patent-to-hypoplastic intervention redistributes vessel voxels so total visible vessel is fixed. Adding or enlarging a communicating artery ordinarily changes visible vessel amount. The pitch also implies that the “direction expected from the new route” represents functional rerouting, while the card explicitly freezes perfusion and distal enhancement and admits synthetic-artifact and CTA-phase confounds. Those limitations did not survive translation.

## 8. Easier versions and low-hanging fruit

The genuinely low-hanging-fruit analysis is a **measurement/benchmark audit**, not an intervention study: use the already released `cow-msk`, `lvo-msk`, CTA, perfusion maps, clinical tables, and final-infarct masks to quantify (i) how often automatic CoW graphs are anatomically valid, (ii) how often Acom/Pcom labels agree with blinded raw-CTA review, stratified by CoW-involving versus distal occlusion, and (iii) whether graph features are stable to resampling and one-voxel perturbations. TopCoW supplies label definitions and evaluation code; ISLES supplies the masks and outcomes. No model checkpoint or GPU training is needed. It does require a small, honestly acknowledged expert-reference annotation set.

That audit is worth doing because the released pseudolabels are positioned as reusable dataset assets, and the existing primary evidence explicitly excludes occluded CoWs. It could establish whether any downstream graph study is defensible. It does **not** answer whether a final-infarct model uses collateral reserve and should not be sold as a simplified version of that claim.

A second easy analysis—incremental held-out prediction of final infarct from automatic graph features beyond occlusion location and perfusion summaries—uses existing labels and CPU-scale features, but in 149 treatment-heterogeneous cases it would be an exploratory association with substantial measurement error and limited power. It is only worth doing after the mask audit, and it must not be interpreted as model use or hydraulic reserve.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Are the released ISLES'24 automatic CoW masks sufficiently branch-faithful and resampling-stable, especially near CoW-involving occlusions, to support graph-based stroke research?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—a small blinded fidelity and stability audit would validate or invalidate a uniquely reusable public vascular annotation asset and decisively gate several higher-level collateral questions.
