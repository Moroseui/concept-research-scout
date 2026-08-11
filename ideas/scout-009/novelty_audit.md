# Novelty audit — cycle 009

Audited 2026-08-11. Nine candidates from `candidates_all.json`, numbered C1–C9 by
merged position (C1–C5 baseline, C6 = wide W1, C7 = wide W2, C8 = wide W3,
C9 = fiction F1). Every verdict is based on searches run this cycle (queries and
retrieved passages in `novelty_manifest.json`), not on recall. Absence of a found
duplicate is not verified novelty.

---

## C1 — The CT spirometer may be measuring remodeled airway walls (baseline, Mode A)

**Neighbors.**
1. Park et al., *Deep Learning-based Approach to Predict Pulmonary Function at Chest CT*, Radiology 2023 — PMID 36786699; DOI 10.1148/radiol.221488. The target model itself; predicts FEV1/FVC from LDCT and reports only associational Grad-CAM/saliency (central lung fields weighted; airway/diaphragm/thoracic-cage contributions examined visually), no causal concept test. (abstract verified; full text paywalled)
2. *Efficient adversarial debiasing with concept activation vector — Medical image case-studies*, J Biomed Inform 2024 — PMID 38043883. Closest concept-direction-intervention work in medical imaging: locates and removes a concept (race) from a trained chest-X-ray/mammography model — debiasing, not a physiological USE audit, and not Pi10 or regression. (search_summary)
3. *Deep Learning Estimation of Small Airways Disease from Inspiratory Chest CT is Associated with FEV1 Decline in COPD*, medRxiv 2024 — PMID 39314974; DOI 10.1101/2024.09.10.24313079. DL-derived airway measure associated with FEV1/FEV1 decline in SPIROMICS — associational, no model decoding. (search_summary)

**Delta.** No prior work fits a Pi10 probe to a frozen CT-to-FEV1 model's representation and selectively erases that direction to measure a paired output change; the concept-erasure machinery and the airway-FEV1 association each exist, but their combination as a causal model-use audit does not.

**Why not done.** `NEW_CAPABILITY` — concept-direction identify-and-remove interventions were first validated on medical-imaging models only in 2024 (PMID 38043883), and only for fairness concepts; applying them to a physiological quantity in a regression model became a natural next step only after that.

**Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH` — multi-source search with verified identifiers, but the Park full text (which contains the model's own saliency analysis, possibly including airway commentary) was paywalled (HTTP 403) and could not be inspected; two of three neighbors are search_summary access.

---

## C2 — The kidney model may be reading fat packed into the renal sinus (baseline, Mode B)

**Neighbors.**
1. Blankemeier et al., *Merlin: a computed tomography vision-language foundation model and dataset* — arXiv:2406.06512; Nature 2026 DOI 10.1038/s41586-026-10181-8 (DOI seen in search results only). The audit target; 752 tasks including 5-year chronic-disease prediction; no renal-sinus-fat attribution reported in the abstract. (abstract)
2. Cohen, Blankemeier, Chaudhari, *Explaining 3D Computed Tomography Classifiers with Counterfactuals* — arXiv:2502.07156. The Merlin group's own 3D counterfactual audit method (Latent Shift extended to CT) — demonstrated only on lung size and pleural effusion; no kidney, CKD, or renal sinus fat anywhere in the full text. (full_text)
3. Bialek et al., *Opportunistic Detection of Chronic Kidney Disease Using CT-Based Measurements of Kidney Volume and Perirenal Fat*, J Clin Med 2025 — DOI 10.3390/jcm14165888; PMID 40869714. Correlational: CT kidney volume and perirenal/hilar fat independently predict CKD via HU-threshold segmentation; no model audit. (full_text)

**Delta.** The counterfactual-audit tooling exists in the Merlin group itself but has never been pointed at the CKD output or at any renal compartment; the candidate's compartment-selective sinus-fat substitution with visceral-fat-matched controls is the missing application, which makes the delta real but exposed to being scooped by the model's own authors.

**Why not done.** `NEW_CAPABILITY` — Merlin (2024–2026) and its group's 3D CT counterfactual method (2025) are both new; the audit only became posable this year.

**Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH` — Merlin was inspected only at arXiv-abstract level; the Nature version's supplementary interpretability analyses (if any) could not be checked and are exactly where a pre-emption would hide.

---

## C3 — The brain-tumor prognosticator may be weighing the chewing muscle (baseline, Mode B)

**Neighbors.**
1. Chelliah et al., GRASP study, Neuro-Oncology 2024 — PMID 38285679; DOI 10.1093/neuonc/noae017; PMC11145448. The target model; full text inspected: input is whole-head T1c/T2 resampled to 1 mm³ and cropped/padded to 130³ **with extracranial tissue retained**; interpretability is guided-backpropagation saliency noting non-tumor regions are informative; no extracranial substitution or occlusion experiment. (full_text)
2. Mi et al., *Deep learning-based quantification of temporalis muscle has prognostic value in patients with glioblastoma*, Br J Cancer 2022 — PMID 34848854; DOI 10.1038/s41416-021-01590-9. Temporalis cross-sectional area is an independent survival predictor in GBM — associational prognostic marker, not a model-reliance test. (abstract)
3. Tinauer et al., *Skull-stripping induces shortcut learning in MRI-based Alzheimer's disease classification*, Insights into Imaging 2025 — DOI 10.1186/s13244-025-02158-4. Closest methodological neighbor: audits a brain-MRI model's reliance on preprocessing-induced contours via configuration comparison + LRP — different disease, no region substitution, no temporalis. (abstract)

**Delta.** The prognostic association (Mi) and the shortcut-audit method family (Tinauer) exist separately; no work tests whether a whole-head tumor-survival model causally uses extracranial temporalis signal via tumor-stable within-patient substitution. Side finding: the GRASP full-text inspection directly supports this candidate's keystone (the model demonstrably retains extracranial tissue in its input tensor).

**Why not done.** `BLIND_SPOT` — the sarcopenia-prognosis literature and the model-interpretability literature run on disjoint tracks; whole-head model builders treat extracranial tissue as framing, and marker researchers do not audit other people's models.

**Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — multi-source search including full-text inspection of the load-bearing target-model paper; neighbors found and distinguished.

---

## C4 — The risk model may be reading the breast's lines of force (baseline, Mode C)

**Neighbors.**
1. *Using Explainable AI to Characterize Features in the Mirai Mammographic Breast Cancer Risk Prediction Model*, Radiology: AI 2025 — DOI 10.1148/ryai.240417; PMID 40899990. Verified real: correlates Mirai's 512 internal features with mammographic observations on EMBED; concludes Mirai implicitly relies on lesion features, especially calcifications (CalcMirai ≈ Mirai in screen-negatives). Feature-correlational; no texture perturbation. (abstract; full text 403)
2. Gastounioti et al., *Incorporating Breast Anatomy in Computational Phenotyping of Mammographic Parenchymal Patterns*, Sci Rep 2018 — DOI 10.1038/s41598-018-35929-9; PMID 30504841. Nipple-centered polar/radial grid aligned to ductal orientation for handcrafted texture risk features — the prior art for nipple-relative orientation coordinates. (full_text)
3. Rangayyan & Ayres, *Gabor filters and phase portraits for the detection of architectural distortion in mammograms*, Med Biol Eng Comput 2006 — DOI 10.1007/s11517-006-0088-3; PMID 16991010. Orientation-field analysis of fibroglandular strands for architectural-distortion CAD. (search_summary)

**Delta.** Orientation-field measurement of parenchyma and Mirai explainability both exist, but no study defines an orientation order parameter and causally perturbs it (spectrum- and density-preserving) to test a deep risk model's use; note the XAI paper's calcification finding is mild evidence *against* this candidate's mechanism carrying much of Mirai's signal.

**Why not done.** `BLIND_SPOT` — orientation analysis lives in pre-deep-learning CAD, and modern Mirai XAI has been feature-correlational and lesion-centric; nobody has crossed the two with a controlled perturbation.

**Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH` — the most relevant XAI full text was 403-blocked, and one neighbor is search_summary access.

---

## C5 — The lung-cancer model may be reading the marrow as a smoking dosimeter (baseline, Mode C)

**Neighbors.**
1. Sobieski et al., *Auditing Sybil: Explaining Deep Lung Cancer Risk Prediction Through Generative Interventional Attributions* — arXiv:2602.02560 (v2 2026-05-13; accepted ICML 2026). Verified real, full text read: S(H)NAP, a causal generative-edit (3D diffusion-bridge) audit of Sybil isolating object-specific score contributions — nodules, lobes, artifacts (electrodes, gown snaps, mandible). It states Sybil "likely infers age from global cues like bone density." Vertebrae/marrow/trabecular structures are **not** among the intervened objects. (full_text)
2. Mikhael et al., *Sybil*, J Clin Oncol 2023 — PMID 36634294; DOI 10.1200/JCO.22.01345. The target model; whole-LDCT risk without clinical inputs; no interpretability analysis at source. (abstract)
3. Cai et al., *Regional variations and spatial heterogeneity of lumbar CT attenuation are associated with osteoporotic vertebral fracture*, Front Endocrinol 2025 — DOI 10.3389/fendo.2025.1630371. Establishes intra-vertebral attenuation heterogeneity (CV, IQR) as an image signature — for fracture on standard CT, not smoking/LDCT/Sybil. (full_text)

**Delta.** Relative to Auditing Sybil the delta is only the intervention object (vertebral trabecular marrow, transplanted between matched vertebrae) and the specific X (attenuation heterogeneity); the audit framework, the model, and even the qualitative "Sybil reads bone" motivation are already published, and the paper's bone-density remark pre-empts part of the candidate's headline.

**Why not done.** `NEW_CAPABILITY` — the generative interventional machinery for Sybil appeared in January 2026; the flip side is that the group that built it is best positioned to run the marrow object next.

**Verdict.** `INCREMENTAL` — no duplicate of the specific marrow experiment, but the candidate is methodologically dominated by arXiv:2602.02560 and must be reframed as an object-level extension of it (and cite it as such), with the novelty claim narrowed to marrow-specific heterogeneity vs. the already-asserted bone-density/age cue.

---

## C6 — The CT spirometer may be reading the diaphragm as a pressure-loaded membrane (wide W1, Mode B)

**Neighbors.**
1. Chang et al., *Three-dimensional quadratic modeling and quantitative evaluation of the diaphragm on volumetric CT in COPD*, Med Phys 2016 — PMID 27370142 (verified by fetch). Principal curvatures, shape index, height, surface area of the dome, correlated with PFTs. (abstract)
2. Bakker et al., *Automated evaluation of diaphragm configuration based on chest CT in COPD patients*, Eur Radiol Exp 2024 — PMID 39090324; PMC11294507 (verified by fetch). Diaphragm index (surface/projected area) from the lung-diaphragm intersection in >8,400 scans; correlates with GOLD stage, FEV1%pred, emphysema. Citation correction: the candidate card says "Bak et al."; the verified first author is **Bakker**. (abstract)
3. Li et al., *Deep learning based CT images for lung function prediction in COPD*, BMC Pulm Med 2025 — PMID 41120976; DOI 10.1186/s12890-025-03957-7 (verified by fetch). DL CT-to-PFT model with Grad-CAM interpretability — no diaphragm localization. (abstract)

**Delta.** Diaphragm-configuration quantification and CT-FEV1 model saliency exist separately; no work warps the caudal lung-diaphragm boundary band with lung-volume compensation to causally test whether a frozen pulmonary-function model reads dome curvature. Caveat: Park et al.'s own (unreadable, paywalled) saliency analysis reportedly examined diaphragm-region contributions associationally — the causal question remains open but the region is not unnoticed.

**Why not done.** `BLIND_SPOT` — pulmonary-function interpretability centers on parenchyma and airways; the diaphragm sits at the input boundary and is treated as framing rather than signal.

**Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH` — key identifiers verified by fetch, but the Park full text (the target model's own regional-attribution analysis) was paywalled and uninspected.

---

## C7 — Mirai may be detecting broken bilateral symmetry before a lesion exists (wide W2, Mode B)

**Neighbors.**
1. Donnelly et al., *AsymMirai: Interpretable Mammography-based Deep Learning Model for 1-5-year Breast Cancer Risk Prediction*, Radiology 2024;311(1):e232780 — PMID 38501952; DOI 10.1148/radiol.232780 (verified by PubMed fetch). Built a local bilateral-dissimilarity model on Mirai's encoder that reproduces Mirai's risk scores (1-year r = 0.68; 4–5-year r = 0.70) and reports that **mirroring the unilateral breast makes Mirai predict uniformly low risk** — concluding bilateral dissimilarity "was a key to Mirai's reasoning." (abstract)
2. *Using Explainable AI to Characterize Features in the Mirai Model*, Radiology: AI 2025 — DOI 10.1148/ryai.240417. Feature-correlational Mirai explainability (calcification-dominant). (search_summary)
3. Tan, Zheng et al., *Prediction of Near-term Breast Cancer Risk based on Bilateral Mammographic Feature Asymmetry*, Acad Radiol 2013 — PMID 24200481; DOI 10.1016/j.acra.2013.08.020. Classic handcrafted bilateral-asymmetry near-term risk prediction. (abstract)

**Delta.** Only the perturbation refinement remains: AsymMirai already established the deliverable claim (Mirai uses bilateral asymmetry) by surrogate reconstruction *and* by a mirroring perturbation that collapses Mirai's scores; the candidate's registered, density/spectrum-preserving graded equalization is a finer dose-response version of an experiment whose qualitative answer is published. The search also surfaced active follow-on contention (selective-mirroring results suggesting unilateral signal suffices; STA-Risk arXiv:2505.21699, VMRA-MaR arXiv:2506.17412), meaning the question is being worked, not unasked.

**Why not done.** `TRIED_AND_FAILED` (red-flag category; here it was tried and **succeeded**): Donnelly et al. 2024 performed the core test and published the positive answer. Nothing material would be different this time beyond dose-response resolution — recommend the kill.

**Verdict.** `DUPLICATE_FOUND` — AsymMirai (Radiology 2024, PMID 38501952, DOI 10.1148/radiol.232780). Recommend killing C7 as scoped; the candidate's own novelty_neighbors missed this paper entirely. Any successor (e.g., "which component of asymmetry, beyond what mirroring shows, carries the signal — with density/spectrum controls") changes the deliverable sentence and must re-enter as a new candidate under the claim-identity rule.

---

## C8 — The glioblastoma prognosticator may be reading the invasion front's roughness (wide W3, Mode C)

**Neighbors.**
1. Chelliah et al., GRASP study, Neuro-Oncology 2024 — PMID 38285679; DOI 10.1093/neuonc/noae017 (verified by fetch). The target whole-brain survival model; saliency-only interpretability. (abstract; full text separately inspected under C3)
2. Curtin et al., *Shape matters: morphological metrics of glioblastoma imaging abnormalities as biomarkers of prognosis*, Sci Rep 2021 — PMID 34853344; DOI 10.1038/s41598-021-02495-6 (verified by fetch). Fractal dimension and lacunarity of GBM abnormalities in 402 patients; T2/FLAIR shape most strongly related to survival. Citation correction: the candidate card attributes this PMID to "Tate et al."; the verified first author is **Curtin** (Swanson lab). (abstract)
3. Smitha et al., *Fractal analysis: fractal dimension and lacunarity from MR images for differentiating the grades of glioma*, Phys Med Biol 2015 — PMID 26305773; DOI 10.1088/0031-9155/60/17/6937 (verified by fetch). The box-counting + lacunarity toolchain on glioma MR. (abstract)

**Delta.** Fractal boundary complexity is established as a prognostic *association*; no retrieved work performs invariant-matched (volume, surface area, centroid, intensity histogram) signed-distance-field roughness edits and measures a frozen survival model's response — the causal audit is the missing piece, not the biomarker.

**Why not done.** `BLIND_SPOT` — radiomics-prognosis and model-interpretability communities are disjoint; interpretation work localizes attention rather than constructing geometry-matched counterfactuals.

**Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH` — identifiers verified by fetch and neighbors distinguished, but coverage of MICCAI/arXiv counterfactual-interpretability venues was bounded and neighbor access was abstract-level.

---

## C9 — The arterial-calcification score may be reading inspiratory depth (fiction F1, Mode C)

**Neighbors.**
1. Hamamci et al., CT-CLIP / CT-RATE — arXiv:2403.17834; published in Nature Biomedical Engineering 2025 (s41551-025-01599-y). The target model and its arterial-wall-calcification output; no shortcut or interpretability audit of any abnormality head in the paper. (abstract)
2. Brown et al., *Detecting shortcut learning for fair medical AI using shortcut testing*, Nat Commun 2023 — arXiv:2207.10384 (verified by fetch); published DOI 10.1038/s41467-023-39902-7, PMID 37463884 (search_summary — PubMed CAPTCHA-blocked). Closest methodological neighbor: systematic test of whether a clinical model exploits a suspected confound, via multitask probing on radiology/dermatology — no pixel-preserving edits, no CT-CLIP. (full_text for arXiv version)
3. van Velzen et al., *Deep Learning for Automatic Calcium Scoring in CT*, Radiology 2020 — PMID 32043947; DOI 10.1148/radiol.2020191621 (verified by fetch). Reference location-aware automated CAC/TAC scoring across six CT protocols; no confound analysis. (abstract)

**Delta.** No retrieved work audits CT-CLIP (or any CT-RATE-trained model) for shortcut reliance, and no work frames inspiratory depth as a spurious cue for a calcification classifier; the plaque-preserving (>130 HU voxels copied bit-for-bit) diaphragm-displacement design has no found precedent, though lesion-preserving counterfactual audits exist in other modalities (RoentMod arXiv:2509.08640, chest X-ray; MedEdit arXiv:2407.15270, brain MRI).

**Why not done.** `NEW_CAPABILITY` — the released CT-CLIP checkpoint (2024) plus public NLST imaging make a checkpoint-specific, label-free shortcut audit possible; before the weights release the question was untestable.

**Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH` — multiple sub-checks with verified identifiers, but CT-CLIP itself was inspected at abstract level and the published Nature BME version was not fetched. Consistent with the candidate's own "NO NOVELTY CLAIM" stance; human verification still required before any novelty language hardens.

---

## Summary

| Candidate | Title (short) | Track | Verdict | Why-not-done |
|---|---|---|---|---|
| C1 | CT spirometer / Pi10 airway walls | baseline | NO_DUPLICATE_FOUND_LIMITED_SEARCH | NEW_CAPABILITY |
| C2 | Merlin / renal sinus fat | baseline | NO_DUPLICATE_FOUND_LIMITED_SEARCH | NEW_CAPABILITY |
| C3 | GBM prognosticator / temporalis muscle | baseline | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C4 | Mirai / radial stromal alignment | baseline | NO_DUPLICATE_FOUND_LIMITED_SEARCH | BLIND_SPOT |
| C5 | Sybil / vertebral marrow dosimeter | baseline | INCREMENTAL | NEW_CAPABILITY |
| C6 | CT spirometer / diaphragm curvature | wide | NO_DUPLICATE_FOUND_LIMITED_SEARCH | BLIND_SPOT |
| C7 | Mirai / bilateral asymmetry | wide | DUPLICATE_FOUND (AsymMirai, PMID 38501952) | TRIED_AND_FAILED |
| C8 | GBM prognosticator / fractal boundary | wide | NO_DUPLICATE_FOUND_LIMITED_SEARCH | BLIND_SPOT |
| C9 | CT-CLIP calcification / inspiratory depth | fiction | NO_DUPLICATE_FOUND_LIMITED_SEARCH | NEW_CAPABILITY |
