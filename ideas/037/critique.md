FATAL OBJECTION: The proposed spectral edit cannot identify use of an acquisition-site noise fingerprint because its “noise residual” and NPS jointly encode reconstruction, dose, interpolation, object-dependent noise, and denoiser error, while no paired acquisition or validated generator shows that anatomy and all other model-readable evidence remain fixed.
EVIDENCE: Kharboutly et al., DOI 10.1109/EUVIP.2014.7018385 (eight 3D images from different scanners); Mackin et al., DOI 10.1002/mp.14208; ideas/037/idea_card.json.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Detailed critique

## 1. The intervention does not manipulate the claimed construct

The card's key inference is invalid:

> classifier-flipping, matched-energy spectral reshaping + a spectrally neutral sham -> only the site fingerprint changed -> any model response demonstrates use of that fingerprint.

The middle term is not established. In reconstructed CT, the noise power spectrum is a property of an acquisition-and-reconstruction chain, not a unique sensor identifier. It varies with reconstruction kernel, dose, pitch, reconstruction method, object size and position, and spatial location. Mackin et al. experimentally found that reconstruction kernel strongly shifts NPS peak frequency and CT texture features (PMCID PMC5729963; DOI 10.1002/mp.14208). Li et al. further showed that local NPS estimates depend on ROI size/location, background removal, windowing, and reconstruction method (PMCID PMC5690921; PMID 27167257). These are primary measurements, not a semantic objection.

A wavelet-Wiener residual is also not guaranteed to be anatomy-free. It is the difference between an image and an imperfect denoised estimate; edges, fine anatomy, partial volume, beam-hardening structure, and interpolation correlations can remain. “Homogeneous” ventricular CSF and white-matter patches reduce this problem but do not prove its absence, and extracranial air is especially vulnerable to defacing and padding signatures. A site classifier can exploit any of those residual differences. A successful classifier-flip manipulation check establishes that the edit crosses that classifier's decision boundary, not that it substitutes a physical scanner fingerprint.

The sham does not rescue identification. An equal-energy phase or spectrum permutation is merely a different artificial perturbation. If the target edit changes directional correlations, local stationarity, resolution/noise coupling, or residual anatomical structure while the sham does not, a larger response to the target remains compatible with generic sensitivity to those properties. Likewise, a monotone response along a constructed blend axis shows sensitivity to the construction, not to site identity as a causal variable.

The card therefore cannot deliver its rung-1 sentence. At best it can say that a particular model responds to a particular NPS-remapping operator. Replacing “uses the acquisition-site noise fingerprint” with that sentence changes the deliverable's identity under the repository's claim-identity rule.

## 2. The cited forensics instrument is not validation for this use

Kharboutly et al. is described too strongly as proving CT-scanner fingerprint readability. The 2014 primary paper reports experiments on only **eight 3D images of 100 slices from different scanners** and constructs reference noise patterns from 3D images before correlating test slices (DOI 10.1109/EUVIP.2014.7018385; author PDF: https://www.lirmm.fr/~subsol/WWW/EUVIP.1214.1.pdf). On the evidence reported, this does not demonstrate patient-independent, protocol-robust scanner identification: slices from one volume are not independent patients, and one volume per scanner leaves anatomy, protocol, and scanner perfectly bundled. It is a method precedent, not construct validation for a 149-patient multicenter clinical dataset.

The card's novelty claim is correspondingly too confident. “None anywhere uses” is universal language unsupported by a targeted search. The defensible statement is only that the recorded search did not locate a stroke-outcome-model use test of this form.

## 3. Site, scanner, protocol, and preprocessing remain inseparable

The keystone screen verified five scanner models across two manufacturers but found no device-to-center mapping. A Munich-versus-Zurich classifier therefore measures center decodability, not scanner identity. Center can be encoded by reconstruction kernel, voxel geometry, field of view, padding, defacing behavior, preprocessing success, or protocol—not necessarily stochastic sensor noise. Calling the result a “site fingerprint” does not solve the measurement problem because the deliverable immediately defines that fingerprint as “scanner-specific noise texture.”

Registration and resampling make the interpretation harder. Their interpolation kernels impose spatial correlations, and those correlations can depend on source voxel geometry and transform. A derivative-input classifier may thus read a preprocessing-by-geometry signature. Raw/derivative comparisons can localize when decodability appears or disappears, but cannot determine which physical source generated it.

There is no concept-label circularity in the ordinary sense—final-infarct labels are not used in the proposed paired response—but there is **instrument circularity**: the same site classifier defines whether the residual is site-like and certifies that the intervention became more site-like. Passing both checks validates agreement with that classifier, not the underlying physical construct. A second classifier family or held-out cases would reduce model overfitting but would not cure construct confounding.

## 4. The audited model and endpoint are not ready

The proposed “shared audit model” does not exist. The endpoint is consequently underspecified: which released or trained model, which input channels, which frozen preprocessing, what constitutes “non-trivial” held-out performance, and whether the model even consumes NCCT/CTA/CTP image channels that retain the proposed residual are all unresolved. This is not a minor feasibility detail because the winning ISLES'24 method used skull stripping and custom intensity windowing before a residual nnU-Net (Ren et al., arXiv:2505.18424). The relevant fingerprint may be removed, transformed, or absent from some input channels.

An easier codebase exists, but it is not a strong substitute model. The released PrediCTP repository provides training and inference code for a raw-4D-CTP model (https://github.com/kimberly-amador/ISLES24-PrediCTP), yet its reported performance is Dice 0.20 and lesion-wise F1 0.02. Auditing a weak model could yield an easy response curve but little medical value. The official ISLES repository provides data-loading and evaluation code, not a frozen high-performing checkpoint (https://github.com/ezequieldlrosa/isles24). Thus the card overstates “prior legwork” and “evaluation readiness.”

The primary response is also unclear. A segmentation has millions of probabilities: plausible summaries include lesion volume, mean probability, voxelwise logit change, soft Dice against the eventual label, or spatially localized change. Those answer different questions. A signed forecast shift cannot be prespecified without defining the sign of the other-center edit and a center-conditioned outcome direction; the card explicitly puts that outcome analysis out of scope. Without it, “signed output change” is not a single endpoint.

## 5. Feasibility and negative-result value are overstated

The public archive is approximately 99 GB according to the keystone screen, not the card's proposed 15–20 GB download. A 60-case subset might be smaller, but the subset bytes and required modalities have not been enumerated. More importantly, automated reliable homogeneous-ROI selection across NCCT and 4D CTP is not “no annotation” merely because no human labels are requested: ventricular CSF, periventricular white matter, and surviving extracranial air require segmentation, erosion, artifact exclusion, and quality control. CTP noise is time-, enhancement-, and motion-dependent, so baseline-frame residuals are not interchangeable with stationary NCCT noise.

The claimed negative is not decisive. Even after center decodability passes, a null edit response can mean that the model ignores site information, that the edit failed to alter the particular site feature the model uses, that preprocessing removed the cue before inference, that the selected summary cancels spatially mixed changes, or that the model is too weak. Decodability by an external shallow classifier does not guarantee alignment with the audited model's representation. The negative-result score should be at most 2 for the proposed intervention.

## 6. Medical relevance is conditional, not demonstrated

Site shortcuts are medically important, but this study does not test the clinically important consequence: performance or calibration failure at a new site. ISLES'24 has only two disclosed training centers, and its hidden test set is not an accessible third-center transfer cohort. A perturbation response on 30 held-out cases cannot support the card's predicted “failure mode at any third center.” That is speculation requiring external validation.

The most direct ISLES'24 question is whether held-out performance differs by center and whether a model trained without one center transfers to it. That does not identify a noise mechanism, but it measures the deployment risk that motivates the card.

## 7. Plain-pitch fidelity: failed

The pitch strengthens four unverified statements:

- “two hospitals with different scanners” is not verified because the dataset paper does not map devices to centers;
- “where you were treated is itself informative about how you will fare” is only a plausible hypothesis; no center-wise outcome analysis is in the card;
- “swaps only the invisible noise signature ... touching nothing about anatomy” presents an unvalidated intervention assumption as fact;
- “would matter anywhere ... at a hospital it never saw” generalizes beyond a two-center, no-third-site design.

These are not harmless simplifications. They remove the exact limitations that determine whether the result has a physical and clinical interpretation.

## 8. Low-hanging fruit and the easier defensible study

The genuine low-hanging fruit is a **site-stratified out-of-fold benchmark audit**. ISLES'24 already provides 149 public training cases, per-case center labels, final-infarct masks, official metrics (Dice, absolute volume difference, absolute lesion-count difference, lesion-wise F1), and official loading/evaluation code. A frozen nnU-Net recipe also exists in the winning-method publication/code ecosystem, although checkpoint availability must be verified before calling it ready.

Use nested patient-level evaluation with two complementary estimates:

1. fixed pooled training with strictly out-of-fold predictions, reporting every official metric and calibration/volume bias separately by center with patient-level uncertainty; and
2. train-on-Munich/test-on-Zurich versus appropriately size-matched within-Munich resampling, repeated with frozen splits, to distinguish ordinary small-training-set degradation from cross-center degradation.

With only 50 Zurich cases and no third site, this remains a two-center benchmark audit, not a general deployment guarantee. It also cannot attribute any gap to scanner noise. But it answers a clinically meaningful question using existing labels and accepted endpoints, and a null is interpretable within stated precision. Metadata-only site decodability from raw/derivative images is even cheaper, but by itself is routine and not worth a separate candidate; it should be diagnostic context inside the performance audit.

The original noise-use question would require a different dataset or new acquisition: repeated phantom/scans across devices and protocols, or traveling-subject/paired reconstruction data that independently validates a noise-transfer operator while holding anatomy fixed, followed by testing a competent final-infarct model. ISLES'24 does not contain that counterfactual support.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: On strictly out-of-fold ISLES'24 predictions, does final-infarct performance, calibration, or volume bias differ by center, and does train-on-one-center transfer degrade beyond a size-matched within-center baseline?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—unlike a site-decoding census, it directly measures the multicenter deployment risk using released center labels, lesion masks, accepted metrics, and reusable training/evaluation machinery, while remaining honest that it cannot identify scanner-noise use.
