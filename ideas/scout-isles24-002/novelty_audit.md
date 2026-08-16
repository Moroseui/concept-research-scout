# Novelty audit — scout-isles24-002

Search date: 2026-08-16. “No duplicate found” below means only that the documented search did not retrieve one; it is not proof of novelty.

## C1 — The water already in the tissue: does the model read the edema clock? (baseline)

1. **Neighbors.** (i) *Deep learning biomarker of chronometric and biological ischemic stroke lesion age from unenhanced CT* (Nature Communications, 2024; PMCID PMC11624201) trained an NCCT model for lesion age and explicitly compared it with a relative-intensity measure equivalent to NWU. (ii) *Automated Measurement of Net Water Uptake From Baseline and Follow-Up CTs in Patients With Large Vessel Occlusion Stroke* (Stroke: Vascular and Interventional Neurology, 2022; PMCID PMC9271791) automated mirrored-ROI NWU using CTP-defined baseline core and follow-up lesion masks. (iii) *Feasibility of net water uptake for CTP predicting true infarct core and long-term outcome in acute ischemic stroke* (Journal of Radiation Research and Applied Sciences, 2026; DOI 10.1016/j.jrras.2026.102324) used NWU to stratify CTP thresholds for final-core and outcome prediction in 390 patients. These make the physiological and prediction connection substantially less open than the card suggests.
2. **Delta.** The candidate does not introduce NWU into outcome prediction; its narrower delta is a controlled, graded intervention asking whether a separately trained multimodal final-infarct model *uses* admission-NCCT NWU while perfusion inputs are held fixed.
3. **Why not done.** `NEW_CAPABILITY` — ISLES’24 newly combines public co-registered admission NCCT/perfusion inputs with follow-up infarct masks, making an input-specific use audit reproducible; the underlying NWU–prediction link is already established.
4. **Verdict.** `INCREMENTAL` — the intervention-grade interpretability test is distinct, but the headline “edema clock inside prediction” is now crowded by a lesion-age DL model and direct NWU-stratified infarct prediction.

## C2 — The healthy hemisphere is the ruler (baseline)

1. **Neighbors.** (i) *PerfU-Net: Baseline infarct estimation from CT perfusion source data for acute ischemic stroke* (Medical Image Analysis, 2023; DOI 10.1016/j.media.2023.102749) explicitly built a symmetry-aware network that processes affected and healthy hemispheres together. (ii) *Identification of infarct core and ischemic penumbra using computed tomography perfusion and deep learning* (J Med Radiat Sci, 2023; PMCID PMC9826796) compared a DL segmentation method with clinical contralateral-relative thresholding. (iii) Campbell et al., *Cerebral blood flow is the optimal CT perfusion parameter for assessing infarct core* (Stroke, 2011; DOI 10.1161/STROKEAHA.111.618355; PMID 21980202) established the contralateral-normalized rCBF reference used clinically.
2. **Delta.** Unlike symmetry-aware architecture or performance comparisons, this candidate perturbs only the contralateral hemisphere and reads the ipsilateral output to identify whether a frozen model actually computes a patient-specific cross-hemisphere reference.
3. **Why not done.** `BLIND_SPOT` — prior work encoded symmetry as an architectural prior or treated relative thresholds as a comparator, but did not frame the healthy hemisphere as an experimentally manipulable internal reference.
4. **Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — a close architecture-level neighbor exists, but searches spanning symmetry-aware CTP networks, contralateral normalization, and final-infarct prediction found no remote-perturbation audit.

## C3 — Two tissues, two death thresholds (baseline)

1. **Neighbors.** (i) Chen et al., *Thresholds for infarction vary between gray matter and white matter in acute ischemic stroke: A CT perfusion study* (J Cereb Blood Flow Metab, 2019; DOI 10.1177/0271678X17744453; PMCID PMC6421247) measured distinct GM/WM CBF thresholds. (ii) *Toward Patient-Tailored Perfusion Thresholds for Prediction of Stroke Outcome* (AJNR, 2014; PMCID PMC7964729) improved tissue-fate prediction using patient-specific transformations and separately modeled GM and WM. (iii) *Deep Learning-Based Prediction of Final Infarct Core from CT Perfusion Data: A Comparison to the Clinical Standard* (J Am Heart Assoc, 2024; PMCID PMC11864740) combined CBF, delay time, CBV, and baseline CT in an Attention U-Net but did not audit tissue-class use.
2. **Delta.** The candidate tests whether a learned predictor applies tissue-class-dependent fate rules at matched perfusion, then removes NCCT gray–white visibility while preserving spatial position; the neighbors estimate thresholds or train predictors without this use test.
3. **Why not done.** `BLIND_SPOT` — tissue-specific physiology remained a threshold-design question, while learned outcome models were evaluated by aggregate accuracy rather than whether they recovered that interaction.
4. **Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — primary threshold studies and modern DL outcome studies were found and distinguished; no model-use audit of the GM/WM threshold interaction was retrieved.

## C4 — The barrier is already leaking (baseline)

1. **Neighbors.** (i) Lin et al., *Measuring elevated microvascular permeability and predicting hemorrhagic transformation in acute ischemic stroke using first-pass dynamic perfusion CT imaging* (AJNR, 2007; DOI 10.3174/ajnr.A0539; PMID 17698530) generated Patlak PS maps from first-pass CTP and associated elevation with hemorrhagic transformation. (ii) *CT perfusion analysis by nonlinear regression for predicting hemorrhagic transformation in ischemic stroke* (J Cereb Blood Flow Metab, 2016; PMID 26233188) found nonlinear-regression relative PS more discriminative than standard Patlak estimates. (iii) Amador et al., *Predicting treatment-specific lesion outcomes in acute ischemic stroke from 4D CT perfusion imaging using spatio-temporal convolutional neural networks* (Medical Image Analysis, 2022; DOI 10.1016/j.media.2022.102610) trained a raw-4D-CTP tissue-outcome model and showed an advantage over map inputs, without assigning that advantage to permeability.
2. **Delta.** It links these strands by measuring permeability from the same raw series and testing whether a raw-CTP outcome model specifically uses the late leakage signal rather than merely showing that permeability predicts hemorrhage or that raw series improve Dice.
3. **Why not done.** `NEW_CAPABILITY` — ISLES’24 provides a rare public combination of raw motion-corrected 4D CTP, registered map controls, and follow-up infarct masks suitable for a reproducible use audit.
4. **Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH` — no duplicate was retrieved, but the permeability literature is method-diverse and the keystone acquisition duration remains uninspected; confidence should stay limited.

## C5 — The clot that lets contrast through (baseline)

1. **Neighbors.** (i) Santos et al., *Thrombus Permeability Is Associated With Improved Functional Outcome and Recanalization in Patients With Ischemic Stroke* (Stroke, 2016; DOI 10.1161/STROKEAHA.115.011187; PMID 26846859) introduced CTA attenuation increase/void fraction and linked perviousness to smaller final infarcts and recanalization. (ii) *Introduction of CTA-index as Simplified Measuring Method for Thrombus Perviousness* (Clin Neuroradiol, 2021; PMCID PMC8463362) proposed a simpler admission CTA measure with outcome-prediction capacity. (iii) *Endovascular Treatment Effect Diminishes With Increasing Thrombus Perviousness* (Stroke, 2021; PMID 34281377) pooled seven trials and related increasing perviousness to outcome, infarct volume, and treatment-effect heterogeneity.
2. **Delta.** The candidate’s distinct step is not outcome association but a clot-confined intervention asking whether a final-infarct model reads clot attenuation beyond the downstream perfusion field held fixed.
3. **Why not done.** `NEW_CAPABILITY` — the ISLES’24 release newly supplies co-registered multimodal inputs plus public LVO masks and follow-up infarct labels in one benchmark, although file-level mask extent is still unverified.
4. **Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH` — the model-use delta survived targeted searches, but thrombus-imaging ML is broad and the archive-level mask assumption prevents high confidence.

## C6 — The scan is also an actigraph: the model may be reading how much the patient moved (wide)

1. **Neighbors.** (i) Fahmi et al., *Head movement during CT brain perfusion acquisition of patients with suspected acute ischemic stroke* (Eur J Radiol, 2013; DOI 10.1016/j.ejrad.2013.08.039; PMID 24041432) quantified CTP motion and found moderate/severe movement in about one quarter of patients. (ii) Moghari et al., *Head movement during cerebral CT perfusion imaging of acute ischaemic stroke: Characterisation and correlation with patient baseline features* (Eur J Radiol, 2021; DOI 10.1016/j.ejrad.2021.109979; PMID 34678666) found NIHSS, age, and onset time predictive of motion. (iii) Potreck et al., *What is the impact of head movement on automated CT perfusion mismatch evaluation in acute ischemic stroke?* (J Neurointerv Surg, 2022; DOI 10.1136/neurintsurg-2021-017510; PMID 34301804) injected motion into a perfusion phantom and measured bias in RAPID core/penumbra estimates.
2. **Delta.** It treats residual motion as a learned prognostic shortcut and tests a raw-CTP outcome model with calibrated within-case injection; prior work measured motion, its clinical correlates, or its effect on classical mismatch software.
3. **Why not done.** `BLIND_SPOT` — CTP research frames motion exclusively as corruption to quantify or correct, not as behavior that a learned model might exploit.
4. **Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — three very close primary neighbors delimit the gap cleanly, and multi-query searches found no learned final-infarct model audit of motion as a shortcut.

## C7 — Little's law in the penumbra: the model may be reading the vasodilatory counterattack (wide)

1. **Neighbors.** (i) Wintermark et al., *Perfusion-CT assessment of infarct core and penumbra* (Stroke, 2006; DOI 10.1161/01.STR.0000209238.61459.39) advanced CBV/CTP definitions of core and penumbra. (ii) Campbell et al., *Cerebral blood flow is the optimal CT perfusion parameter for assessing infarct core* (Stroke, 2011; DOI 10.1161/STROKEAHA.111.618355; PMID 21980202) found contralateral-relative CBF superior for core definition. (iii) Robben et al., *Prediction of final infarct volume from native CT perfusion and treatment parameters using deep learning* (Medical Image Analysis, 2020; DOI 10.1016/j.media.2019.101589; arXiv:1812.02496) predicted final infarct from native CTP and performed input/metadata ablations, not physiological-state interventions.
2. **Delta.** The candidate toggles mirror-referenced CBV state at matched CBF while co-editing MTT to preserve the empirical inter-map manifold, asking about the CBV×CBF reserve interaction rather than whole-channel importance.
3. **Why not done.** `BLIND_SPOT` — the clinical literature framed CBV and CBF as competing scalar thresholds, and DL work inherited channel-level ablations rather than testing their joint physiological state.
4. **Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — the threshold debate and raw-CTP DL literature were searched directly; no construct-preserving reserve toggle was found.

## C8 — Has the deficit percolated? Volume is what the metric sees; connectivity may be what the model uses (wide)

1. **Neighbors.** (i) *Acute Ischemic Stroke Infarct Topology: Association with Lesion Volume and Severity of Symptoms at Admission and Discharge* (AJNR, 2017; PMID 27758775; PMCID PMC7963653) studied infarct topology/location against volume and clinical severity on acute MRI. (ii) Amador et al., *Predicting treatment-specific lesion outcomes in acute ischemic stroke from 4D CT perfusion imaging using spatio-temporal convolutional neural networks* (Medical Image Analysis, 2022; DOI 10.1016/j.media.2022.102610) showed spatial-temporal raw CTP improves tissue-outcome prediction without isolating connectivity. (iii) *Deep generative computed perfusion-deficit mapping of ischaemic stroke* (Nature Communications, 2026; arXiv:2502.01334; PMCID PMC12894690) modeled the topology of disrupted perfusion to localize NIHSS substrates, but did not use a percolation order parameter or predict final infarct.
2. **Delta.** It defines connectedness of the input Tmax field as an order parameter and proposes volume/histogram-conserving bridge-versus-cut interventions on a final-infarct model; the neighbors study output topology, exploit spatial context, or map perfusion patterns to deficits.
3. **Why not done.** `BLIND_SPOT` — stroke selection and challenge evaluation privilege deficit volume and severity, leaving connectivity of the *input* perfusion field unnamed as a candidate variable.
4. **Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH` — the precise percolation test was not found, but terminology spans topology, fragmentation, connected components, and lesion-pattern literatures, and the candidate’s edit remains speculative.

## Summary

| Candidate | Verdict | Why-not-done code |
|---|---|---|
| C1 | INCREMENTAL | NEW_CAPABILITY |
| C2 | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C3 | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C4 | NO_DUPLICATE_FOUND_LIMITED_SEARCH | NEW_CAPABILITY |
| C5 | NO_DUPLICATE_FOUND_LIMITED_SEARCH | NEW_CAPABILITY |
| C6 | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C7 | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C8 | NO_DUPLICATE_FOUND_LIMITED_SEARCH | BLIND_SPOT |
