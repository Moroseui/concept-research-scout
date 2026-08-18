FATAL OBJECTION: The destination-swap response cannot identify use of arterial-border distance because changing destination necessarily changes global coordinates, surrounding anatomy, and patch-context compatibility together with the purported vascular “last mile.”
EVIDENCE: `ideas/038/idea_card.json` (`use_vs_association`); Liu et al., Sci Data 2023, DOI 10.1038/s41597-022-01923-0; Volders et al., Sci Rep 2020, PMID 32501132.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial critique

## 1. The intervention does not isolate the claimed variable

The card says that transporting the same joint NCCT/perfusion patch between an interior and a border-zone destination makes a destination-dependent prediction a test of a learned border-distance prior. That conclusion does not follow.

**Verified fact:** the public arterial atlas defines territories in template space from lesion distributions, and vascular territories vary between patients (Liu et al., DOI 10.1038/s41597-022-01923-0, PMID 36739282). A separate digital-border-zone study was motivated specifically by uncertainty in the traditional border location (Phan et al., DOI 10.1159/000214215, PMID 19390177).

**Verified fact:** surrounding perfusion context itself improves voxel-level infarction prediction. Volders et al. compared local perfusion values with cuboid receptive-field information in 144 patients and reported materially higher prediction performance with surrounding context (PMID 32501132).

**Inference:** after a swap, the model can respond to at least four inseparable changes: absolute anatomical coordinate, neighboring tissue/perfusion context, mismatch between transplanted anatomy and its surroundings, and atlas-border distance. Matching cortical depth, tissue class, local vessel density, and four perfusion summaries does not equalize sulcal geometry, white-matter tract layout, multiscale perfusion gradients, receptive-field content, or the learned coordinate implied by skull/ventricle geometry. The parallel-boundary sham controls displacement and interpolation, but it does not control the fact that the border-directed destination is a different anatomical and contextual location.

An edit discriminator and seam checks cannot repair this. Passing them would show only that the chosen detector did not distinguish the edits; it would not establish equality of all features used by the infarct model. Conversely, requiring the transplanted patch and its entire effective receptive field to be identical would leave no independent way to change its anatomical border distance. This is the same structural pattern as the portfolio's repeated `IDENTIFIABILITY_FAILURE`: the claimed mechanism covaries with location and context by construction.

The endpoint is also underspecified. “Continuous probability-mass readout” does not say whether mass is measured inside the transplanted patch, a fixed destination ROI, the whole lesion, or a change relative to an unedited image. Those estimands behave differently when a segmentation model changes boundary probabilities or produces spatial spillover. This is repairable drafting, but it is downstream of the fatal construct problem.

## 2. “Subject-specific competing supply fronts” are not actually measured

**Verified fact:** the ISLES'24 release provides an automatically generated multi-label Circle-of-Willis mask and linearly co-registered acute modalities (Zenodo DOI 10.5281/zenodo.16731717). **Verified fact:** the Liu atlas provides population arterial territories, not patient-specific distal perfusion boundaries.

The card proposes to “refine major-territory seeds” with the CoW mask, but it gives no validated transformation from proximal Circle-of-Willis anatomy to an individual's distal ACA/MCA/PCA competition fronts. Agreement between an atlas-only estimate and a CTA-refined estimate is not validation when both inherit the same atlas boundary. One-voxel registration perturbations quantify numerical stability, not biological validity. Calling the resulting quantity “subject-specific” would therefore be unsupported.

The “last-mile” analogy also slips between two different measurements. Distance to the nearest territory *boundary* is smallest at a border, whereas economic last-mile cost is naturally distance from a supply hub or network path length. The card mentions both boundary distance and CTA centerline distance but never defines a signed direction that makes these equivalent. Near-boundary tissue is not necessarily farthest along a patient-specific vascular route. Thus even a clean border-coordinate effect would not establish that the model prices distal delivery cost or limited redundancy.

## 3. The medical interpretation outruns the experiment

Mangla et al. review heterogeneous border-zone mechanisms (DOI 10.1148/rg.315105014, PMID 21918038); that literature supports border-zone relevance, not a universal scalar reserve determined by atlas distance. The card itself cites Carpenter et al. as a counterexample to selective chronic border-zone hemodynamic impairment (DOI 10.1212/WNL.40.10.1587, PMID 2215951). More proximal clot location also changes perfusion-defect size and salvage (Sillanpää et al., DOI 10.3174/ajnr.A3149, PMID 22723067), illustrating how occlusion topology and treatment response can generate spatial fate differences not captured by four local maps.

Accordingly, “tissue-vulnerability prior,” “fewer pressure and collateral options,” and the proposed clinical generalization to systemic pressure or arterial anatomy are **speculation**, not consequences isolated by this design. A positive swap response would support only destination sensitivity under a synthetic edit. A null would likewise not show that the model “treats fate as local physiology”: the model could use coarse location, occlusion-territory context, or border information at a scale destroyed or obscured by the edit. The stated negative-result value is therefore overstated.

There is no concept-label circularity in the narrow sense—the follow-up infarct mask is not generated from the atlas distance—but there is **measurement circularity** in validating atlas-only and atlas-refined distances that share the same population territory scaffold.

## 4. Executability and cost are not honestly closed

The keystone screen found no public frozen ISLES'24 final-infarct checkpoint in the official repository or winning-solution materials. That is an open access fact, not proof that no checkpoint can be obtained. Still, “after a shared frozen checkpoint” hides the dominant cost. Training and validating a new model on 149 public cases is not part of the claimed two-GPU-hour experiment, and a self-trained model would change “the model” into a newly selected model family whose result may be seed- and recipe-specific.

The card also mixes development and confirmation. “On all public cases” for the support census, followed by “30 untouched cases,” is impossible unless the split is frozen first and the census is restricted to training/development metadata. Eligibility thresholds, atlas variants, discriminator construction, edit parameters, and checkpoint selection all require development cases. With only 149 public cases, the design needs explicit disjoint train, edit-development, and untouched evaluation partitions plus patient-level inference. The proposed 120 forward passes do not represent the preprocessing, matching, atlas-warping, model-training, realism-model training, or sensitivity-analysis burden.

## 5. Prior-work and novelty audit

The exact model-use intervention was not found in the inspected primary neighbors; that is not evidence of novelty. More importantly, the card understates adjacent legwork:

- Volders et al. already tested whether regional CTP context adds voxel-level final-infarct information (PMID 32501132).
- Peerlings et al. used an atlas of downstream regions and CTP spatial layout to infer occlusion location in 596 patients, finding vessel-architecture variation limiting accuracy (PMID 37064186).
- Phan et al. built a probabilistic MCA/PCA border-region atlas expressly because border locations vary (PMID 19390177).
- Liu et al. released the deformable arterial-territory atlas the card would use (PMID 36739282).

These works do not duplicate an audit of a trained ISLES'24 network. They do show that “spatial context matters” and “atlas border zones can be quantified” are established. The precise remaining delta is model reliance on a border-coordinate signal beyond perfusion—not the broader last-mile story. Because the proposed experiment cannot identify that delta, limited novelty confidence is not the reason to proceed.

## 6. Plain-pitch fidelity

The pitch fails fidelity in two places.

First, “Blood supply has a last-mile problem” converts the card's hedged suspected mechanism (“may,” “fewer ... options”) into a fact. Primary sources establish variable border-zone mechanisms, not that distance to a template territory boundary is a patient-level delivery-cost measure.

Second, “moving the same realistic tissue pattern” omits that realism and common support are uninspected gates and that the edit changes destination context. “Even when local blood-flow measurements look the same” is directionally faithful to matching, but it should not imply equivalence of physiology: four derived perfusion maps do not exhaust collateral state, vascular topology, treatment, or tissue context.

## 7. Easier formulation and low-hanging fruit

The genuinely low-hanging-fruit study is model-free: on a frozen patient split, test whether atlas-border distance adds held-out prediction of follow-up infarction beyond acute CBF, CBV, MTT, Tmax, tissue class, cortical depth, hemisphere, and occlusion category. Use patient-clustered evaluation; report incremental log loss/calibration and stratified effects across atlas variants. The released 149-case images, follow-up masks, LVO/CoW products, and public arterial atlas already exist; no new annotation or checkpoint is required.

This would be **association-only**. It cannot establish pressure reserve, subject-specific collateral redundancy, or model use, and treatment/reperfusion variables may leave serious residual confounding. Its value is nevertheless real: it decides whether there is any stable, out-of-sample border-distance signal worth making explicit in later models. A failure to add predictive information is informative and would stop investment in a much harder interpretability experiment. A positive result would justify a separate candidate comparing otherwise identical models trained with and without an explicit, uncertainty-aware border-distance channel. That later comparison would test utility and robustness, not whether an existing implicit model already uses the construct.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does uncertainty-aware arterial-territory border distance add held-out prediction of follow-up infarction beyond acute perfusion maps and prespecified anatomical/occlusion covariates in ISLES'24?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—because it is a checkpoint-free falsification gate for whether a stable border-location signal exists at all, while explicitly stopping short of physiology or model-use claims.
