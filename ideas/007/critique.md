FATAL OBJECTION: The proposed volume slope cannot identify lung inflation as the model's cue because density, anatomy motion, field-of-view/resampling, and 4DCT reconstruction artifacts all change with measured lung volume.
EVIDENCE: TCIA collection DOI 10.7937/3ppx-7s22; CT-CLIP official preprocessing/inference repository; Yamamoto et al., DOI 10.1118/1.3488984.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION

# Adversarial review

## Bottom line

The paired breath-hold data are real, public, small, and unusually useful. The experiment is worth doing. The interpretation in the card is not yet earned.

The clean estimand is: **how much do CT-CLIP finding scores change between a real inspiratory and expiratory acquisition of the same patient in one session?** That is a clinically relevant robustness question. The present card instead claims the model is specifically using total lung volume and the attenuation it sets, and treats the ten 4DCT phases as a mechanism-identifying dose response. Neither move is valid. A score-volume association cannot separate volume from the many image properties that deterministically accompany breathing, and phase-binned 4DCT adds reconstruction artifacts rather than resolving that ambiguity.

This is a revision, not a rejection, because the paired breath-hold comparison remains unusually well controlled and needs no labels or invented counterfactuals. The claim must drop from “specific cue decoded” to “respiratory-state sensitivity measured,” unless an additional intervention separates the candidate cues.

## What is verified

- **Verified fact:** TCIA states that all 20 subjects have inhale/exhale breath-hold CT and a free-breathing 4DCT acquired in one session on one Siemens Biograph mCT.S/64. It also states that the breath holds targeted approximately 80% of maximum inhalation and exhalation. The collection is 14.93 GB and complete. Primary dataset record: [TCIA CT-vs-PET-Ventilation-Imaging](https://www.cancerimagingarchive.net/collection/ct-vs-pet-ventilation-imaging/), DOI 10.7937/3ppx-7s22.
- **Verified fact:** The collection record says 20 inhale/exhale BHCT scans were successfully acquired for 20 patients. This resolves the card's listed uncertainty about whether the pair exists for every subject at the collection level, although series-level usability still requires direct DICOM inspection.
- **Verified fact:** CT-CLIP's official repository provides inference code and links a ClassFine checkpoint; it reports inference on 18 abnormalities and says inference can run on smaller GPUs. [Official CT-CLIP repository](https://github.com/ibrahimethemhamamci/CT-CLIP); Hamamci et al., arXiv:2403.17834, DOI 10.1038/s41551-025-01599-y.
- **Verified fact:** The released 18-label vocabulary includes emphysema, atelectasis, lung opacity, and consolidation. It does **not** include mosaic attenuation. “Mosaic attenuation score” must be removed from the question and deliverable unless a different, explicitly validated model is introduced.
- **Verified fact:** The checkpoint is not literally ungated. It is linked inside the gated CT-RATE Hugging Face dataset repository and requires the click-through/contact-sharing access already noted elsewhere in this repository. The imaging corpus is ungated; the proposed model weights are not. This is a modest access dependency, not a fatal data barrier.
- **Source-supported interpretation:** The published Eslick study used these acquisitions for CT ventilation rather than diagnostic-model robustness. Eslick et al., *Radiotherapy and Oncology* 2018;127:267-273, PMID 29290405. I found no verified primary study that already reports CT-CLIP finding-score changes across this paired BHCT corpus.
- **Not established:** Novelty remains “not found,” not proven. The search did not exhaust conference proceedings, benchmark supplements, or analyses published after the CT-CLIP paper.

## Decisive identifiability problem

The card says that a monotone score relationship across ten phases would distinguish inflation from “something else that moved.” It would not.

Measured lung volume is jointly accompanied by:

- mean parenchymal HU and the entire density histogram;
- diaphragm position, mediastinal geometry, cardiac silhouette, vessel crowding, and dependent opacity;
- tumor and atelectasis position and apparent shape;
- the amount of anatomy admitted to or discarded by CT-CLIP's fixed input preprocessing;
- interpolation, duplication, discontinuity, and phase-sorting artifacts in 4DCT.

Most of those quantities move systematically with respiratory phase and can therefore produce the same monotone score-volume relationship. Tumor position in particular can be monotone with lung volume; the card's statement that it would not be is unsupported and physiologically implausible. A continuous covariate improves precision but does not identify which correlated visual variable the model uses.

The 4DCT series is also not a ten-level controlled-inflation experiment. Respiratory phase is a location in time within a cycle, not a calibrated percentage of vital capacity. Equal phase bins need not have equal amplitude increments, and the same amplitude may occur on inspiratory and expiratory limbs with different anatomy. Conventional respiratory-correlated CT is reconstructed from projections acquired across breathing cycles and is vulnerable to phase-sorting artifacts under irregular breathing. These are established properties of 4DCT, not theoretical edge cases: Yamamoto et al. directly studied spatial 4DCT artifacts (Medical Physics 2010, DOI [10.1118/1.3488984](https://doi.org/10.1118/1.3488984), PMID 20964215), and Abdelnour et al. compared phase and amplitude binning because phase binning produced respiration-related misalignments (Physics in Medicine & Biology 2007, DOI [10.1088/0031-9155/52/12/012](https://doi.org/10.1088/0031-9155/52/12/012)).

Consequently:

- The breath-hold pair identifies sensitivity to **respiratory acquisition state**, conditional on the protocol actually matching in the DICOM headers.
- The 4DCT phases can be an exploratory consistency analysis after image-quality control.
- Neither analysis alone identifies total lung volume rather than attenuation, motion, resampling, or reconstruction artifact as the cue.

The card currently scores identifiability as 5 and rung 3 as reached. Both are overstated. Before repair, identifiability is at most 3 and the result reaches rung 1: the model uses something that changes with respiratory state. A named rung-3 statement could be “the model's emphysema score is sensitive to inspiratory versus expiratory acquisition state,” but not “the model uses total lung volume and mean attenuation” as two independently isolated cues.

## The preprocessing confound is central, not a technical footnote

CT-CLIP consumes a fixed-size preprocessed volume. When the lungs expand and the diaphragm moves, converting both scans to that fixed representation can alter anatomical scale, superior-inferior coverage, padding, and crop boundaries. A score can therefore track measured litres even if the encoder is responding to scale or crop occupancy rather than parenchymal physiology.

This is the nearest-checkable-thing error to avoid here:

> If I have only verified that paired breath-hold scans and a fixed preprocessing pipeline exist, what am I still assuming?

The remaining load-bearing assumption is that the two respiratory states enter the model with comparable coverage and physical scale, such that the score difference reflects the acquired anatomy rather than preprocessing-induced framing. That assumption is not inspected. It must become a Stage 0 gate based on actual preprocessed volumes, not a post hoc caveat.

At minimum, the revision must report, by respiratory state, retained superior/inferior landmarks, crop loss, padding fraction, post-resampling lung-voxel count, physical voxel spacing before preprocessing, and whether either lung touches an input boundary. If these differ systematically, the experiment remains a valuable pipeline robustness test but cannot decode a physiological cue.

## Negative controls do not rescue the mechanism

Calcification findings are useful **process controls**, but they do not exclude general acquisition sensitivity:

- Different heads have different prevalences, calibration, and score variances. A flat calcification head is not evidence that an emphysema-head change arose specifically from inflation rather than head-specific sensitivity to resampling or motion.
- Arterial-wall and coronary calcification are not necessarily geometrically invariant in the fixed tensor: cardiac and mediastinal positions change with respiration, and partial-volume effects can change after resampling.
- Failure of the negative controls would be informative—the pipeline is globally unstable—but success does not identify the positive mechanism.

Better controls include every released output, standardized by each head's test-retest variability, rather than selecting a few “should be flat” heads. The primary contrast should test whether the prespecified parenchymal heads move more than the empirical background distribution across non-parenchymal heads. This is still a specificity analysis, not proof of the cue.

## Endpoint and medical-claim problems

The card mixes three distinct endpoints:

1. paired inhale-exhale score difference;
2. within-patient score-versus-volume slope across 4DCT phases;
3. comparison with a published LAA%-950 change per litre.

Only the first is presently clean enough to be primary. The second is confounded by phase reconstruction and pseudo-replication: ten phases do not create 200 independent patients. The third is dimensionally awkward. A neural-network probability/logit change per litre cannot be called “more or less robust” than a percentage-point change in LAA%-950 per litre without a clinically justified normalization or decision threshold. Those outputs have different units and purposes.

The sentence “a patient who cannot hold a full breath receives a different diagnosis” is not supported by a continuous score shift. It requires a validated clinical threshold, evidence that cases cross it, and evidence that the output is actually used as a diagnosis. CT-CLIP ClassFine is an abnormality classifier trained from report-derived labels, not a deployed diagnostic decision rule. The defensible consequence is narrower: breath-hold quality may alter model finding scores and therefore threatens score comparability.

There is no concept-label circularity in the primary analysis because it uses no reference labels. There is, however, **output-semantic dependence**: ClassFine heads inherit report-derived categories. A movement in an “emphysema” head does not prove the visual feature used is emphysema. That is exactly why the physical cue claim needs stronger identification.

## Statistical weakness and the null

The anticipated null is correctly classified as sensitivity-limited. The proposed comparison to 1.44 LAA percentage points per litre does not supply an equivalence margin for a model logit or probability. A revision needs a model-scale margin tied to a consequence, for example:

- a prespecified fraction of the score separation between positive and negative CT-RATE validation cases; or
- a prespecified probability/logit change based on ClassFine calibration and threshold-crossing behavior; or
- a standardized paired change relative to same-state repeatability on RIDER, treated cautiously because RIDER respiratory state is uncontrolled.

With 20 patients, confidence intervals and patient-level bootstrap or randomization inference matter more than nominal phase-level sample size. Phase volumes must remain clustered within patient. Multiplicity across 18 heads must be handled with a small confirmatory set and all others explicitly exploratory.

A null without a justified equivalence margin remains type 2. It cannot establish inflation invariance. A large paired effect, by contrast, would be a clear and useful robustness failure even before cue identification.

## Prior-work overlap

The closest verified overlap does not kill the project:

- Eslick et al. validate CT-derived ventilation against Galligas PET; they do not evaluate diagnostic-model scores.
- The RIDER foundation-model study tests embedding repeatability in 26 scan-rescan patients but does not control or measure respiratory state and does not report ClassFine head changes. The manuscript is “Foundation model embeddings for quantitative tumor imaging biomarkers,” Research Square rs-6630446; its methods state two scans within 15 minutes and embedding cosine similarity. This is meaningful overlap in **robustness framing**, not the same experiment.
- Quantitative emphysema studies already establish that inspiration changes density-based emphysema measures. This supports the medical premise but also means the biological direction is not novel. The novel delta, if retained cautiously, is the magnitude and head specificity of a released model's response.

The project should not claim discovery of the inflation-density relationship. It can claim a previously unreported model audit only after a final, documented search and direct inspection of the closest papers.

## Feasibility and compute

Compute is not a serious objection. The official repository reports sub-second ClassFine inference per volume under its setup and permits smaller-GPU inference. Even 20 pairs plus 200 phase volumes are modest. The real feasibility risks are:

- gated access to the 1.77 GB checkpoint;
- compatibility of radiotherapy CT coverage with CT-CLIP preprocessing;
- direct DICOM confirmation of slice thickness, reconstruction kernel, contrast status, pixel spacing, dose fields, series completeness, and breath-hold pair matching;
- lung segmentation reliability on expiratory and artifact-affected 4DCT volumes.

These are Stage 0 checks. No score should be interpreted before they pass.

## Easier version with existing assets

The low-hanging-fruit formulation is a paired **respiratory-state repeatability audit** using only the 40 breath-hold volumes. It uses the already released TCIA images, CT-CLIP code and ClassFine checkpoint, and a standard automatic lung mask. It needs no labels, no 4D registration, no 4DCT artifact adjudication, and no bespoke training.

Freeze emphysema as the sole confirmatory head because it has the clearest quantitative link to inflation. Treat atelectasis, lung opacity, and consolidation as ordered secondary hypotheses; remove mosaic attenuation because the head does not exist. Report the paired change from expiration to inspiration, its confidence interval, the fraction of cases crossing any **pre-existing author-defined** classification threshold if one exists, and descriptive associations with measured volume and mean HU. Call those associations explanatory evidence, not mechanism identification. Report all 18 heads as an exploratory specificity panel.

This preserves the clinically important question—whether breath-hold quality changes a model's output—while avoiding the false promise that ten correlated phase reconstructions reveal which pixels or physical quantity the model uses. If the paired effect is large, a later, separate mechanism study can use registered, tissue-mass-preserving transformations or a controlled-inflation acquisition with independently set volumes. Such interventions require their own in-distribution validation and should not be smuggled into this first audit.

## Required revision before a probe contract

1. Change the primary question to respiratory-state sensitivity of the emphysema score on the matched BHCT pair.
2. Downgrade the 4DCT analysis to exploratory and remove the claim that it identifies inflation or supplies ten calibrated dose levels.
3. Remove mosaic attenuation and verify the complete output vocabulary and score semantics directly from the pinned code revision.
4. Make preprocessing comparability an explicit Stage 0 go/no-go gate.
5. Separate score shift, measured-volume association, and diagnostic threshold crossing; do not translate the first into “different diagnosis.”
6. Define a model-scale equivalence margin before inference; otherwise preserve the null as sensitivity-limited.
7. Freeze one confirmatory head, a small ordered secondary set, and multiplicity handling. Keep all-head analysis exploratory.
8. Correct “no distribution shift” to the narrower fact that both images are real acquisitions. Relative to CT-RATE training, radiotherapy-planning patients, respiratory phase, coverage, and preprocessing may still be out of distribution.

## Decision rationale

Advance to revision because the data contrast is rare, real, and clinically interpretable, and the smallest experiment is cheap. Do not advance the present rung-3 mechanism claim. The study earns a strong robustness statement first; decoding total lung volume or mean attenuation requires a second design that breaks their collinearity with motion and preprocessing.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: In the same patient and session, how much does CT-CLIP's emphysema score change between real inspiratory and expiratory breath-hold CT after verifying matched acquisition and preprocessing coverage?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes—the paired public acquisition can reveal a clinically meaningful breath-hold robustness failure with almost no annotation or compute burden, even though it cannot by itself identify the exact visual cue.
