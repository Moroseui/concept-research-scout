# Novelty audit — cycle isles24-001

Audit of all 8 candidates in `candidates_all.json`, numbered C1–C8 by merged
position. Every verdict below rests on searches executed 2026-08-16 (eight
parallel multi-source web searches; full query and access log in
`novelty_manifest.json`). Absence of a found duplicate is not verified
novelty; access limits are stated per candidate.

---

## C1 — Does the winning model rediscover the collateral clock? (baseline, isles24-scout-001-c01)

**1. Neighbors.**
- de la Rosa et al., "ISLES'24: Final Infarct Prediction with Multimodal Imaging and Clinical Data. Where Do We Stand?" — arXiv:2408.10966 (abstract fetched). Defines the exact benchmark and reports submitted models' performance (top multimodal nnU-Net, Dice 0.285); no interpretability, probing, or HIR analysis.
- Guenego et al., "Hypoperfusion intensity ratio correlates with angiographic collaterals in acute ischaemic stroke with M1 occlusion," Eur J Neurol 2020 — DOI 10.1111/ene.14181 (search_summary; Wiley full text returned 403). Clinical study establishing HIR (Tmax>10/Tmax>6) as a surrogate of angiographic collateral status.
- Amador et al., "Spatio-Temporal Deep Learning for Final Infarct Prediction Using Acute Stroke CT Perfusion Data" (ISLES'24/PrediCTP), Springer 10.1007/978-3-031-81101-2_9 (search_summary). Trains a CNN-Transformer on raw 4D CTP for ISLES'24 final-infarct prediction; performance only, no representation analysis.

**2. Delta.** No prior work probes or erases a named physiological scalar (HIR) inside a frozen deep stroke final-infarct model; the neighbors supply, respectively, the benchmark, the clinical construct, and the model class — none asks the model-use question, and concept-erasure/amnesic-probing literature found remains confined to NLP and diffusion models.

**3. Why not done.** `NEW_CAPABILITY` — ISLES'24 is the first public co-release of acute perfusion maps with post-treatment DWI final-infarct ground truth plus a reproducible trained-model family (challenge submissions such as PrediCTP), which is what makes a probing/erasure audit runnable without private data.

**4. Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH`. Multi-source search from several angles (HIR+ML, XAI-on-infarct-models, concept erasure in medical imaging) found no duplicate, but the Guenego anchor was confirmed only at snippet level (paywall), Scholar was reachable only indirectly, and very recent workshop literature may be missed.

---

## C2 — The vascular detour the segmentation model can see (baseline, isles24-scout-001-c02)

**1. Neighbors.**
- de la Rosa et al., ISLES'24 challenge paper — arXiv:2408.10966 (abstract). Benchmarks final-infarct prediction on the exact dataset; no collateral-vessel analysis and no intervention experiments.
- "Deep learning for prediction of post-thrombectomy outcomes based on admission CT angiography in large vessel occlusion stroke," Front Artif Intell 2024;7:1369702 — DOI 10.3389/frai.2024.1369702 (full text). End-to-end CNNs on admission CTA predicting 90-day mRS; interpretability limited to M3d-CAM attention maps; paper states no ablation studies were conducted.
- "Automatic collateral quantification in acute ischemic stroke using U2-Net" (2025) — PMC12104720 (full text). Deep segmentation of CTA collateral vessels and an explicit affected/contralateral vessel-volume ratio (qCS) validated against visual collateral scoring; no perturbation of any predictive model.

**2. Delta.** The 2025 U2-Net work engineers essentially the same interhemispheric distal-vessel quantity as an explicit biomarker, but no prior work tests whether a trained infarct-prediction network implicitly *uses* it — the within-scan downstream-vessel substitution with upstream and nonvascular shams has no located precedent; existing CTA-model interpretability stops at correlational saliency maps.

**3. Why not done.** `NEW_CAPABILITY` — ISLES'24 co-releases registered CTA, machine-generated Circle-of-Willis vessel masks (`cow-msk.nii.gz` confirmed on the Zenodo record, TopCoW-derived), and final-infarct outcome masks per case; that vessel-plus-outcome pairing in one public benchmark did not previously exist. (Anchors verified: TopCoW arXiv:2312.17670; Riedel et al. DOI 10.1148/ryai.250603 confirmed via Zenodo/RSNA listing, full text 403-blocked.)

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE`. Nine varied queries across PubMed/arXiv/journal indexes; both closest neighbors read in full text and distinguished; adjacent shortcut-audit methodology literature checked and found not applied to stroke vessels. Residual gap: gray literature (theses, unindexed workshop papers).

---

## C3 — Read the stroke from the blood leaving, not only entering (baseline, isles24-scout-001-c03)

**1. Neighbors.**
- Winkelmeier, Faizy et al., "Venous Outflow Profiles Are Linked to Clinical Outcomes in Ischemic Stroke Patients with Extensive Baseline Infarct," J Stroke 2022 — PMC9561220 (full text). COVES (manual cortical-vein opacification score on single-phase CTA) associated with 90-day mRS by logistic regression; no model, no time-resolved curves.
- Singh et al., "Time-resolved assessment of cortical venous drainage on multiphase CT angiography in patients with acute ischemic stroke," Neuroradiology 2022;64:897-903 — PMID 34704112 / DOI 10.1007/s00234-021-02837-1 (abstract; anchor CONFIRMED). Manual per-phase venous opacification grading (TVS) associated with outcome.
- ISLES'24 raw-CTP deep models (challenge paper arXiv:2408.10966; Amador PrediCTP) (search_summary). Supply the model class and dataset; no venous-feature analysis.

**2. Delta.** All located venous-outflow work uses hand-graded static or phase-discrete scores with classical statistics; no prior work extracts automated venous-phase time-curves from raw 4D CTP and audits a deep final-infarct model's reliance on them via curve substitution. **Anchor flag:** the card's second anchor, Wang et al., Eur J Radiol 2026, DOI 10.1016/j.ejrad.2026.112671, could NOT be independently verified — the DOI resolves only to an Elsevier PII stub, ScienceDirect returned 403, and no index hit surfaced for author/title; treat that citation as unverified pending human check.

**3. Why not done.** `NEW_CAPABILITY` — public raw motion-corrected 1-frame/s 4D CTP with venous-phase coverage co-released with tissue-fate labels did not exist before ISLES'24; prior venous scoring was tied to manual mCTA grading.

**4. Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH`. Nine queries, no duplicate found; but one card anchor is unverified, two of three neighbors were confirmed only at abstract/snippet level, and the venous-outflow literature (Faizy/Heit groups) is prolific enough that a recent automated-venous-ML paper could be missed.

---

## C4 — The frail brain around the threatened territory (baseline, isles24-scout-001-c04)

**1. Neighbors.**
- "Deep learning-based white matter lesion volume on CT is associated with outcome after acute ischemic stroke," Eur Radiol 2024 — DOI 10.1007/s00330-024-10584-z / PMID 38285103 (search_summary; medRxiv/Springer full text 403-blocked). DL-segmented WML volume on NCCT tested as risk factor and IVT-effect modifier for sICH and 90-day mRS vs the Fazekas scale (MR CLEAN No-IV post hoc).
- He et al., "Impact of leukoaraiosis on the infarct growth rate and clinical outcome in acute large vessel occlusion stroke after endovascular thrombectomy," Eur Stroke J 2024;9(2):338 — DOI 10.1177/23969873241226771 / PMC11318440 (full text). Visual Fazekas LA independently predicted faster infarct growth (aOR 1.53), with collateral impairment mediating ~33% — regression/mediation only.
- de la Rosa et al., ISLES'24 challenge paper — arXiv:2408.10966 (full PDF fetched). The substrate benchmark; no mention of leukoaraiosis, brain frailty, or any interpretability audit.

**2. Delta.** The clinical premise (LA → faster infarct growth) and an automated NCCT WML measure both exist separately, but no work measures LA automatically on a final-infarct benchmark and erases its representation inside a frozen voxelwise infarct model at matched HIR/volume/age/NIHSS — the closest works predict clinical outcomes by regression from a hand- or DL-computed burden.

**3. Why not done.** `BLIND_SPOT` — a disciplinary boundary: small-vessel-disease epidemiology quantifies LA for outcome regressions, while the stroke-AI community treats NCCT as a context channel and reports only segmentation accuracy; model-use interpretability for infarct prediction is nascent, so nobody connected the two despite both halves being available.

**4. Verdict.** `NO_DUPLICATE_FOUND_LIMITED_SEARCH`. Eight multi-source queries and a specific sweep for concept-erasure/TCAV applied to stroke imaging found nothing; but the closest neighbor's full text was inaccessible and the automated CT-WML tooling literature is broad enough that a near-duplicate measurement paper could be missed.

---

## C5 — A spreading front inside the perfusion deficit (baseline, isles24-scout-001-c05)

**1. Neighbors.**
- de la Rosa et al., ISLES'24 challenge paper — arXiv:2408.10966 (abstract). The benchmark; no shape/topology analysis, no counterfactual experiments.
- Lucas et al., "Learning to Predict Ischemic Stroke Growth on Acute CT Perfusion Data by Interpolating Low-Dimensional Shape Representations," Front Neurol 2018;9:989 — DOI 10.3389/fneur.2018.00989 / PMC6275324 (full text). Injects core/penumbra lesion shape as a learned modeling constraint (shape-embedding interpolation) for growth prediction.
- Olivot et al., "Hypoperfusion Intensity Ratio Predicts Infarct Progression and Functional Outcome in the DEFUSE 2 Cohort," Stroke 2014;45:1018-1023 — DOI 10.1161/STROKEAHA.113.003857 / PMC4047639 (full text). Establishes severe-delay burden as a growth predictor, operationalized purely as a volume ratio; no spatial topology.

**2. Delta.** Prior work either compresses the perfusion deficit to threshold volumes/ratios (Olivot/HIR) or uses shape as a generative modeling constraint (Lucas); no located work diagnostically tests whether a trained infarct model uses deficit topology at exactly fixed value histogram, threshold volumes, and smoothness — the candidate's inverse, counterfactual question.

**3. Why not done.** `BLIND_SPOT` — a framing gap: the perfusion tradition summarizes deficits as volumes at fixed Tmax thresholds, so spatial organization was never treated as a candidate model input to be audited; shape entered the field only as a constraint to improve prediction, not as an estimand.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE`. Twelve varied queries including topology/TDA, radiomics-shape, and counterfactual-XAI angles; three load-bearing sources fetched (two full text); nearest methodological non-duplicates (clinical-variable counterfactuals arXiv:2504.06299, DWI-lesion sphericity radiomics) located and distinguished. Residual gap: an unindexed supplement analysis inside the challenge paper cannot be fully excluded.

---

## C6 — The capillary traffic jam hidden behind the same mean transit time (wide, isles24-scout-001-w01)

**1. Neighbors.**
- Winder et al., "Predicting the tissue outcome of acute ischemic stroke from acute 4D CT perfusion imaging using temporal features and deep learning," Front Neurosci 2022 — DOI 10.3389/fnins.2022.1009654 / PMC9672821 (full text). Directly compared perfusion maps vs deconvolved residue curves vs raw source curves as deep-model inputs (145 patients); accuracy comparison only, no manipulation of transit-time dispersion.
- Robben et al., "Prediction of final infarct volume from native CT perfusion and treatment parameters using deep learning," Med Image Anal 2020 — DOI 10.1016/j.media.2019.101589 / arXiv:1812.02496 / PMID 31683091 (abstract). DeepMedic-based prediction from native 4D CTP; ablation showed native inputs beat deconvolved inputs — deconvolution treated as an all-or-nothing input choice.
- Potreck et al., "Increased volumes of mildly elevated capillary transit time heterogeneity..." Eur Radiol 2019 — DOI 10.1007/s00330-019-06064-4 / PMID 30887195 (search_summary; anchor CONFIRMED via NCBI E-utilities). CTH maps in 131 thrombectomy patients associated with outcome/ICH by logistic regression; no deep model.

**2. Delta.** Winder and Robben establish that deep models can consume residue/source curves and that representation choice matters, but treat the temporal representation wholesale; no prior work isolates the residue-function transit-time *dispersion* and manipulates it at fixed integral, first moment, peak time, and Tmax threshold volumes inside a frozen model — CTH itself has only ever been a regression covariate. (Second card anchor Bathla DOI 10.1161/STROKEAHA.121.034266 / PMID 34670412 confirmed to exist; see C7 for a characterization caveat.)

**3. Why not done.** `NEW_CAPABILITY` — CTH estimation needs raw concentration-time curves, and public stroke benchmarks released only derived maps until ISLES'24 co-released motion-corrected raw 4D CTP with tissue-fate labels; prior raw-CTP deep models (Robben, Winder) ran on private cohorts.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE`. Ten query passes including quoted-phrase CTH+DL searches; anchors bibliographically verified via NCBI E-utilities; closest deep-model neighbor read in full text and distinguished. Residual gap: 2025–2026 MICCAI/ISLES workshop proceedings not fully web-indexed.

---

## C7 — Does the model mistake the end of the scan for the end of the bolus? (wide, isles24-scout-001-w02)

**1. Neighbors.**
- Copen et al., "Exposing Hidden Truncation-Related Errors in Acute Stroke Perfusion Imaging," AJNR 2015;36(4):638-45 — PMID 25500309 (search_summary; anchor CONFIRMED). Progressive deletion of trailing frames from 110-s perfusion acquisitions in 57 patients quantified truncation-induced distortion of deconvolution-derived maps.
- Kasasbeh et al., "Optimal Computed Tomographic Perfusion Scan Duration for Assessment of Acute Stroke Lesion Volumes," Stroke 2016;47:2966-2971 — DOI 10.1161/STROKEAHA.116.014177 (search_summary). Gradual truncation across 70 CTP scans to find minimum duration for stable classical lesion volumes.
- de la Rosa et al., "Detecting CTP truncation artifacts in acute stroke imaging from the arterial input and the vascular output functions," PLOS ONE 2023;18(3):e0283610 — DOI 10.1371/journal.pone.0283610 / PMC10062663 (full text). Nested end-frame censoring to generate labels, then ML classifiers that *detect* truncated/unreliable scans from AIF/VOF features.

**2. Delta.** All located nested-truncation work is analytic (Copen, Kasasbeh, Borst) or treats truncation as a nuisance to detect (de la Rosa 2023); no work tests whether a neural *outcome* model has learned terminal-curve incompleteness as a severity cue, with tail-extrapolation rescue and interior-frame-masking controls to attribute the effect to the censoring boundary specifically. **Anchor corrections for the card:** (a) PMID 25789631 is Borst et al., PLOS ONE 2015 ("Effect of Extended CT Perfusion Acquisition Time on Ischemic Core and Penumbra Volume Estimation"), not Kasasbeh — the card's title/PMID are right but the author attribution is wrong; the true Kasasbeh paper is the Stroke 2016 optimal-duration study cited above. (b) DOI 10.1161/STROKEAHA.121.034266 (card: "Bathla et al.") resolves to a Stroke *editorial/commentary* of that title, not an original study — the card's claim that it "trained AIF-independent neural networks" appears to describe the study the editorial discusses, not the cited item itself. Both corrections should propagate to the card before any feasibility work.

**3. Why not done.** `BLIND_SPOT` — the field frames truncation as an error source to be corrected or flagged (quality control), while raw-CTP AI papers optimize accuracy or dose; the scan boundary was never treated as a candidate *learned feature* of an outcome model, so the shortcut question fell between the QC and AI literatures.

**4. Verdict.** `NO_DUPLICATE_FOUND_HIGH_CONFIDENCE`. Nine queries across PubMed/arXiv/journal indexes; the closest methodological neighbor read in full text; anchor cross-checks were deep enough to surface two citation errors. Residual gap: non-English and 2026 conference abstracts.

---

## C8 — The deconvolution algorithm may have signed the image (wide, isles24-scout-001-w03)

**1. Neighbors.**
- "Deep Learning for Ischemic Penumbra Segmentation from MR Perfusion Maps: Robustness to the Deconvolution Algorithm," MICCAI 2024 Brainlesion workshop, Springer LNCS — DOI 10.1007/978-3-031-76160-7_10 (abstract; full text paywalled). Trained a DL penumbra segmenter on Tmax maps from one deconvolution algorithm, then evaluated on 268 patients with Tmax re-derived by three different deconvolution algorithms, measuring output change.
- Kudo et al., "Differences in CT Perfusion Maps Generated by Different Commercial Software," Radiology 2010;254:200-209 — DOI 10.1148/radiol.254082000 / PMID 20032153 (abstract; DOI verified valid via Crossref — the card's uncertainty flag on this DOI is resolved). Identical raw source data through five commercial packages produced significantly different maps, grouped by tracer-delay sensitivity.
- "CT perfusion stroke lesion threshold calibration between deconvolution algorithms," Sci Rep 2023 — DOI 10.1038/s41598-023-48700-6 (search_summary). Digital-phantom calibration of equivalent core/penumbra thresholds across delay-sensitive vs delay-insensitive algorithm families; no deep model.

**2. Delta.** The MICCAI 2024 workshop paper already performs the core manipulation — swap the deconvolution algorithm under a trained DL model and measure output change — so the phenomenon "DL stroke-lesion output depends on perfusion software" is demonstrated, on MR perfusion, as a robustness finding. C8's residual delta is real but layered: CT/ISLES'24, the four-map bundle with raw CTP co-input held fixed, histogram/threshold-volume matching, and within-family shams that upgrade a robustness observation to a causal fingerprint-use claim. That is a sharper estimand on the same axis, not a new axis. **Anchor correction:** PMCID PMC10853359 is Peerlings, Bennink, Dankbaar et al., Eur Radiol 2023 (the harmonization paper) — the card's "Koopman et al." attribution is wrong and should be fixed.

**3. Why not done.** `NEW_CAPABILITY` — ISLES'24's per-case co-release of raw CTP and derived maps newly enables the source-fixed CT version — but note the field has already begun probing this axis (the 2024 MR-perfusion robustness study), which is why the verdict below is not a no-duplicate finding.

**4. Verdict.** `INCREMENTAL` — relative to DOI 10.1007/978-3-031-76160-7_10. Not a duplicate (different modality, endpoint, and causal-matching design; no kill recommended), but the candidate's headline can no longer read as "nobody has tested whether a stroke DL model depends on the perfusion software." Any card revision must cite that work as the primary neighbor and position the contribution as the causal-attribution and CT-benchmark layer. Assessment is based on the workshop paper's indexed abstract (design quoted verbatim there); a full-text read is the first item of remaining legwork.

---

## Summary

| # | Candidate | Verdict | Why-not-done |
|---|-----------|---------|--------------|
| C1 | isles24-scout-001-c01 — collateral clock (HIR) | NO_DUPLICATE_FOUND_LIMITED_SEARCH | NEW_CAPABILITY |
| C2 | isles24-scout-001-c02 — vascular detour (collateral reach) | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C3 | isles24-scout-001-c03 — venous drainage | NO_DUPLICATE_FOUND_LIMITED_SEARCH | NEW_CAPABILITY |
| C4 | isles24-scout-001-c04 — leukoaraiosis frailty | NO_DUPLICATE_FOUND_LIMITED_SEARCH | BLIND_SPOT |
| C5 | isles24-scout-001-c05 — perfusion-front topology | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C6 | isles24-scout-001-w01 — capillary transit-time heterogeneity | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C7 | isles24-scout-001-w02 — scan-end censoring cue | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C8 | isles24-scout-001-w03 — deconvolution software fingerprint | INCREMENTAL | NEW_CAPABILITY |

Cross-cutting citation corrections surfaced by this audit (for the revise stage):
C3's Wang Eur J Radiol 2026 anchor unverified; C7's Kasasbeh attribution belongs
to Borst et al. and its Bathla anchor is an editorial, not a study; C8's
"Koopman" PMCID is Peerlings et al.; C8's Kudo DOI is confirmed valid.
