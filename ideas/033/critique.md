FATAL OBJECTION: The proposed interventions can show sensitivity to regional attenuation contrast, but cannot identify that the model uses it as a map of *already injured tissue* rather than as a correlated predictor of eventual post-treatment infarction.
EVIDENCE: ISLES'24 challenge paper arXiv:2408.10966; Takahashi et al., PMID 26158082; Reidler et al., DOI 10.1148/radiol.2019182041.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial critique

## 1. The biological interpretation is not identified

The narrow computational question—whether predictions respond to a prespecified affected-versus-mirrored gray–white attenuation-contrast measurement—is testable. The card, however, asks and promises more: that the model uses the measurement “as a map of already injured tissue” and calls the response an “acute-tissue-injury signal.” ISLES'24 cannot adjudicate that interpretation.

The input is acute NCCT, while the target is a lesion mask derived from follow-up MRI after the intervening clinical course. The challenge paper describes final-infarct prediction, not acute irreversible-core labeling (arXiv:2408.10966). Acute attenuation loss is an early ischemic change associated with severity and outcome, but association does not establish irreversibility at acquisition. Takahashi et al. validated automated contralateral densitometry against manual ASPECTS, baseline NIHSS, and later outcomes, not histologic tissue death (PMID 26158082). Reidler et al. evaluated relative HU against **CTP-defined** ischemic core (DOI 10.1148/radiol.2019182041), itself a thresholded imaging surrogate. Thus neither the ISLES target nor the cited measurement literature supplies the missing acute tissue-state ground truth.

A positive erasure/restoration response is compatible with at least three materially different readings: use of established injury; use of a continuous severity cue that predicts later fate; or use of scanner/reconstruction-dependent local contrast correlated with cohort outcome. The proposed controls may narrow the third explanation. They cannot distinguish the first two because both produce the same intervention response and the same follow-up label relation. Calling the cue “already injured” is therefore concept-label circularity in the interpretive sense: final infarction is being used to retrospectively confer acute irreversibility on a baseline sign.

This is not repaired by center replication or a second model family. Those establish reproducibility of model sensitivity, not construct validity. Repair requires deleting the acute-injury interpretation and changing the deliverable to a measurement-level use claim; under the repository's claim-identity rule, that is a successor.

## 2. “Selective representation erasure” is not operationally selective

The card says to learn a gray–white-contrast direction and remove it while preserving decodability of Tmax burden, lesion side, anatomy, and global HU. It does not define:

- the representation layer, learner, training partition, or intervention operator;
- how the direction is learned without using held-out cases or leaking follow-up lesion labels;
- an erasure-success criterion showing that the target measurement, rather than merely a linear probe, is removed;
- preservation margins fixed before model outputs are inspected; or
- the primary output statistic and its expected sign.

Preserving four probes is not evidence that all relevant perfusion severity and anatomy remain intact. Information can remain decodable while the downstream segmentation path is substantially damaged, and a distributed nonlinear signal need not correspond to one removable direction. Conversely, a learned direction can encode acute lesion burden, laterality, tissue class, site, and preprocessing jointly. Norm-matched random directions do not match those correlations. A fall in predicted infarct probability would therefore not isolate gray–white contrast.

The input-space arm is more interpretable but still underspecified. “Contrast restoration” must say which voxels change, toward what patient-specific target, how partial-volume voxels are handled, whether gray matter is raised, white matter lowered, or both, and how local mean HU, noise power, edges, and histogram are matched. Each choice creates a different image. A discriminator cannot validate biological realism or exclude exploitation of edit traces. Agreement between two interventions is not independent corroboration if both are built from the same atlas, mirror mapping, and contrast estimate.

## 3. Leakage and circular region construction remain live

The phrase “learn ... from held-out-free training cases” is ambiguous. If affected regions or direction labels use the follow-up infarct mask, the intervention is learned from the same biological endpoint later used to interpret model response. That is permissible for training a predictor, but not for claiming that the latent direction uniquely represents an acute NCCT sign. If affected side is obtained from the model prediction, the test becomes prediction-conditioned. If it comes from released LVO or lesion-derived annotations, availability and provenance must be stated.

The ASPECTS formulation also restricts the study primarily to MCA-territory early change. ISLES'24 includes a broader real-world cohort; the card gives no eligibility rule for posterior circulation, bilateral, old infarct, leukoaraiosis, hemorrhage, severe artifact, or cases with no reliable homologous region. Within-case mirroring does not control asymmetric chronic disease, beam hardening, head rotation, or reconstruction-dependent gray–white contrast. “Stratify by site/region” is not a remedy with roughly 150 public cases and only 40 proposed held-out cases.

## 4. The target model, sample, endpoint, and power are not ready

The keystone screen correctly found no released winning checkpoint and no published modality ablation establishing that the winner used NCCT. The actual experiment is therefore not an audit of “the winner”; it is an audit of a newly trained model inspired by the winning recipe. The title and motivation overstate that connection.

Training one NCCT-plus-perfusion model and one perfusion-only “twin” is insufficient. A single seed cannot separate modality contribution from optimization variance, and matched architectures do not ensure matched effective capacity. The card provides no non-trivial-performance threshold, minimum NCCT improvement, equivalence rule for perfusion-only performance, seed count, or power calculation. Its 30–50 GPU-hour estimate omits architecture selection, failed training, atlas registration QA, intervention development, and replicated twins. Seven to ten days is possible for an exploratory result, not for the claimed gated conclusion.

The endpoint is also unclear. “Region-specific fall in predicted infarct probability” does not specify mean probability over which fixed voxels, predicted volume, paired affected-minus-unaffected change, or behavior conditional on the eventual lesion. Selecting voxels using the follow-up mask would answer response *inside eventual infarct*, not whether the model generally uses the sign; selecting with the baseline contrast measurement risks regression to the mean. Official Dice and absolute-volume-difference metrics do not solve this intervention endpoint.

## 5. Prior work leaves a narrower delta than the card suggests

There is extensive primary work on automated ASPECTS and contralateral attenuation measurements. Takahashi et al. implemented atlas-to-patient registration and hemispheric density-distribution comparisons (PMID 26158082). Qiu et al. trained automated regional ASPECTS detection using acute NCCT with near-contemporaneous DWI reference (PMID 30498017; DOI 10.3174/ajnr.A5889). Reidler et al. tested regional relative HU against CTP-defined core in 200 patients (DOI 10.1148/radiol.2019182041). These do not appear to perform the proposed final-infarct-model intervention, so no exact duplicate is established. But the legwork means the medically interesting association and computable measurement are already known; the remaining delta is a model-behavior audit, not discovery that fading gray–white contrast predicts injured tissue.

The card appropriately avoids a verified novelty claim. Its novelty-confidence cap of 3 is defensible, but “one experiment apart” understates the missing model, construct-validity problem, intervention validation, and power work.

## 6. Negative-result value is overstated

A null after the current gates remains ambiguous among absent model use, an insensitive or nonselective latent intervention, an unrealistic input edit, inadequate NCCT contribution, training variance, and low prevalence of measurable early change. The NCCT incremental-performance gate removes only one ambiguity: NCCT can help through many cues besides gray–white contrast. The proposed negative-result score of 3 should be at most 2 until a positive-control model is shown to use the exact synthetic measurement and the intervention recovers that known dependence.

## 7. Plain-pitch fidelity fails

The first sentence is faithful background. The second says the study asks whether the model uses the sign “rather than merely benefiting from better-looking scans.” The technical card does not offer a clean binary test between biological use and better-looking/preprocessing-dependent contrast: it explicitly leaves windowing as a model-mechanism explanation and cannot identify irreversible tissue. The final sentence says removing “that contrast signal” would leave perfusion information intact, whereas the card proposes this as an unverified selectivity gate, not an assured property. The pitch drops the single-model, no-checkpoint, 40-case, edit-validity, and rung-1 measurement limitations and sounds more conclusive than the card.

## 8. Easier versions and low-hanging fruit

The lowest-hanging defensible study is model-free and uses released data and labels: measure affected-to-mirrored regional attenuation contrast on NCCT and test whether it adds center-held-out prediction of follow-up infarct involvement beyond prespecified released CBF/CBV/MTT/Tmax summaries. Use region-level outcomes to keep the sample size honest, freeze Munich-to-Zurich and Zurich-to-Munich analyses, and report calibration and uncertainty rather than a segmentation headline. The released NCCT, registered perfusion maps, and follow-up masks already exist; atlas/densitometry methods are published; no checkpoint or new annotation is necessary. A simple preregistered regression is sufficient, so this is CPU-scale after registration.

That study is genuinely worth doing only as a benchmark-specific incremental-information test: does subtle NCCT attenuation contain fate information not captured by the supplied commercial perfusion maps across centers? A negative result is useful if confidence intervals exclude a prespecified increment. It does **not** establish model use or acute irreversible injury, and adjacent attenuation-versus-core literature makes its novelty uncertain. A targeted novelty audit must compare the exact center-held-out, follow-up-region endpoint before promotion.

The nearest model-use successor would first train replicated NCCT-plus-perfusion models and establish NCCT increment, then use a completely specified input-space attenuation intervention with a synthetic positive-control task. That is closer to the original computational question, but it is not low-hanging fruit and should not start with latent erasure.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does affected-to-mirrored ASPECTS-region attenuation contrast add center-held-out information about follow-up regional infarct involvement beyond released perfusion-map summaries in ISLES'24?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes, conditionally: a two-center incremental-information test is cheap and clinically legible, but it merits promotion only if a targeted primary-source audit verifies that this exact follow-up, cross-center delta is not already covered.
