# Novelty audit — cycle isles24-003

Audited 2026-08-18 against `candidates_all.json` (8 candidates, tracks baseline + wide).
Method: live web searches (Google-mediated WebSearch), with PubMed metadata verified
through NCBI E-utilities (PubMed article pages are cookie-walled), and arXiv/PMC/Europe
PMC/Frontiers pages fetched directly where accessible. Full query log and establishing
passages in `novelty_manifest.json`. Calibration note: no verdict below is evidence of
novelty; "no duplicate found" is a statement about the search performed.

Shared search limits (apply to every section): 2025–2026 MICCAI/ISLES post-challenge
workshop papers are sparsely indexed and were not enumerated individually; no
Scopus/Embase/OpenReview sweep; several establishing passages come from abstracts or
search summaries rather than full text (flagged per neighbor in the manifest).

---

## C1 — Did preprocessing teach the winner to read the disappearing insular ribbon? (baseline)

**Neighbors.**
1. arXiv:2505.18424 — "How We Won the ISLES'24 Challenge by Preprocessing" (Ren et al.). The audit target itself: winning pipeline attributing performance to skull stripping and custom intensity windowing; its abstract contains no interpretability or feature-use analysis.
2. PMID 35357053 (Cao Z et al., Hum Brain Mapp 2022) with sibling PMID 30498017 (Kuang H et al., AJNR 2019) — deep-learning/ML automated ASPECTS scoring on NCCT; detection of early ischemic change, not a use audit of a downstream final-infarct model.
3. arXiv:2312.12865 — RadEdit (ECCV 2024): diffusion-based counterfactual editing to stress-test biomedical vision models; the closest methodological precedent, but chest X-ray only, no stroke or gray-white-contrast concept.

**Delta.** Prior work detects early ischemic change or stress-tests models generically; no found work audits whether a final-infarct model uses regional gray-white contrast via selective erasure plus contrast restoration. Caveat recorded: symmetry/contrast priors are already built into some NCCT stroke models (e.g. SEAN, arXiv:2110.05039), so the novelty rests entirely on the audit framing, not on the clinical feature.

**Why not done.** NEW_CAPABILITY — ISLES'24 (2024) plus the published winning recipe with its preprocessing ablation (2025) only recently created a public, reproducible final-infarct model family whose reported windowing gain makes this specific audit askable.

**Verdict.** NO_DUPLICATE_FOUND_HIGH_CONFIDENCE. The card's three cited IDs all check out (verified via E-utilities and arXiv).

---

## C2 — How much artery did the clot occupy? (baseline)

**Neighbors.**
1. PMID 18811738 — Puetz V et al., Int J Stroke 2008: the canonical clot burden score paper; CTA thrombus extent predicts final infarct size, outcome, and hemorrhage — association, no model audit.
2. Tan IYL et al., "CT Angiography Clot Burden Score and Collateral Score...", AJNR 2009;30:525 — multivariate regression showing CBS independently predicts final infarct size alongside ASPECTS/CBV/collaterals.
3. "Thrombus Imaging Features for Anterior Circulation Stroke: Their Impact on CTP Parameters and Natural Evolution of Infarct Progression", J Pers Med 2025 (PMC12565474, full text read) — relates thrombus length/CBS to CTP parameters and infarct progression by regression; already probes the clot-versus-perfusion pathway statistically, with no ML and no counterfactuals.

**Delta.** No found work performs a within-case counterfactual clot-extent edit with perfusion held fixed inside a deep final-infarct model; but the clinical half of the question (clot burden information beyond/through the perfusion deficit) is already addressed by regression in the 2025 J Pers Med paper, so the deliverable must be pitched strictly as the model-use half.

**Why not done.** NEW_CAPABILITY — ISLES'24's released vessel-occlusion masks co-registered with perfusion maps and post-treatment infarct ground truth are the recent asset; before that coupling, a public within-case clot-edit audit had no target.

**Verdict.** NO_DUPLICATE_FOUND_HIGH_CONFIDENCE. **Citation correction required:** the card's cited PMIDs exist but are off-target for "CTA clot burden outcome studies" — PMID 25804568 is Topcuoglu et al. 2015 (clot characteristics vs thrombolysis response) and PMID 27576312 is Pikija et al. 2016 (fibrinogen/clot-burden biochemistry). The card should cite PMID 18811738 and Tan AJNR 2009 instead.

---

## C3 — The arterial network's spare route (baseline)

**Neighbors.**
1. PMID 39788631 — AJNR 2025: Circle-of-Willis variant classes (complete / non-isolating / isolating incomplete) associate with 90-day mRS and mortality after successful revascularization — association, no model audit (abstract via Europe PMC).
2. arXiv:2312.17670 / PMID 38235066 — TopCoW challenge: 13-class CoW segmentation with variant classification via a four-edge variant graph derived from the mask; the closest existing mask-to-graph machinery, purely a segmentation/classification benchmark.
3. DOI 10.1002/cnm.70121 — Mut et al., Int J Numer Methods Biomed Eng 2025: mechanistic CFD framework rendering CoW anatomical variants and stenoses to assess collateral capacity — the nearest thing to graph-edge intervention, but in a physics model, not an audit of a learned predictor (search summary only; Wiley 403).

**Delta.** No found work audits whether a deep final-infarct model uses CoW topology, and none intervenes on the vascular graph of a model input; all ingredients (variant-outcome association, mask-to-graph extraction, mechanistic variant rendering, counterfactual-audit recipes) exist separately, so the novelty is the combination plus the audit target.

**Why not done.** NEW_CAPABILITY — ISLES'24's released multilabel CoW masks coupled to final-infarct ground truth, plus TopCoW-era mask-to-graph tooling (2023–2024), only recently made a public graph-edit audit constructible.

**Verdict.** NO_DUPLICATE_FOUND_HIGH_CONFIDENCE (caveat: sparsely indexed recent workshop papers). Both card citations verified (10.1016/j.wneu.2017.07.084 = Zaninovich 2017, PMID 28736349; PMID 39788631 as claimed).

---

## C4 — The blood's grayscale oxygen gauge (baseline)

**Neighbors.**
1. PMID 21566009 / DOI 10.3174/ajnr.A2504 — Black DF et al., AJNR 2011 (full text via PMC): dural-sinus HU on NCCT correlates with hematocrit and hemoglobin in 166 patients; exactly the claimed proxy relation.
2. PMID 34507404 — Neurology India 2021: sinus attenuation on plain CT detects anemia (35.5 HU cutoff, 100% specificity) — a human/threshold pipeline, not a stroke-outcome model.
3. arXiv:2509.08640 — RoentMod (2025): synthetic within-image counterfactual modification to test whether trained medical-imaging models use a specific feature — closest methodological precedent, different organ/modality/feature.

**Delta.** No found work tests whether any stroke-outcome or final-infarct network reads venous sinus attenuation (an explicit-null query confirmed the gap); the proxy relation, the anemia-outcome association (which uses lab hemoglobin, not image HU), and substitution-style auditing each exist separately.

**Why not done.** BLIND_SPOT — the sinus-HU literature is diagnostic (CVST, incidental anemia) and stroke-model interpretability looks at lesional/perfusion features; remote non-lesional systemic physiology in the same volume falls between the two communities.

**Verdict.** NO_DUPLICATE_FOUND_HIGH_CONFIDENCE. The card's key citation (PMID 21566009) verified against full text.

---

## C5 — When vanished sulci mean rescue, not death (baseline)

**Neighbors.**
1. PMID 25931460 / DOI 10.1161/STROKEAHA.115.009304 — Haussen DC et al., Stroke 2015: the primary series; isolated sulcal effacement in 8/108 LVO patients (7.4%), attributed to engorged leptomeningeal vessels, with no infarct in the effaced area on follow-up in all cases (abstract via E-utilities).
2. PMID 32912520 — J Stroke Cerebrovasc Dis 2020: second clinical series; ISE in 12/195 tPA-treated patients (6.2%), 100% specificity for proximal anterior-circulation occlusion (search-summary access only).
3. DOI 10.1007/978-3-031-79103-1_19 — Taba Chabi et al., Springer 2025: GLCM+SVM segmentation of sulcal effacement on CT as a stroke-detection sign — the only ML touchpoint found, and it treats effacement as an injury marker, the opposite semantic direction.

**Delta.** No found work tests whether any model recognizes or uses the coherent ISE-with-preserved-gray-white pattern as a survival (rather than injury) signal; the only ML neighbor detects effacement as a stroke sign, and generic counterfactual-audit machinery is not stroke- or sign-specific.

**Why not done.** BLIND_SPOT — the sign is rare, described in two small clinical series framed around thrombolysis/thrombectomy eligibility, and ML work has coded effacement with the standard injury polarity; the survival-direction reading has no computational uptake.

**Verdict.** NO_DUPLICATE_FOUND_HIGH_CONFIDENCE for the duplicate question specifically (multi-angle searches returned explicit nulls), with the standing caveat that a niche clinical sign invites missed literature — the card's own novelty_confidence of 2 remains appropriate. Primary citation PMID 25931460 verified and supports every quantitative claim in the card.

---

## C6 — The bolus spreads like dye in a river (wide)

**Neighbors.**
1. DOI 10.1109/ISBI56570.2024.10635756 — Amador K et al., ISBI 2024, "Unveiling the Temporal Patterns of a 4D CTP Stroke Lesion Outcome Prediction Model Through Attention Analysis" — the closest prior work, and closer than anything cited on the card: an interpretability probe of which temporal patterns a raw-4D-CTP transformer outcome model relies on. Correlational attention analysis, not causal perturbation, and it does not isolate dispersion/kernel width from delay or area (abstract-level access only).
2. PMID 29500248 — Lin L et al., Stroke 2018: delay/dispersion correction changes classical CTP core measurement — dispersion in quantification, not in a learned model.
3. PMID 40194529 / DOI 10.1088/2057-1976/adc9b6 — Zeng W et al., Biomed Phys Eng Express 2025: transformer estimating local AIF/perfusion parameters, trained robust to delay/dispersion/bolus-shape degradation — dispersion simulation machinery exists as training augmentation, not as an audit.
(Background: Robben et al., Med Image Anal 2020, PMID 31683091 — native-CTP deep learning final-infarct prediction, the model class to be audited, with no dispersion analysis.)

**Delta.** No found work applies delay- and area-preserving curve narrowing/broadening to a raw-CTP final-infarct model to test transport-kernel-width use; but Amador ISBI 2024 already asks the coarser form of this question (what temporal features does a raw-4D-CTP outcome model use) with attention analysis, so the delta is the upgrade from correlational attention to a causal, dispersion-specific perturbation with maps held in tolerance.

**Why not done.** NEW_CAPABILITY — public raw 4D CTP coupled to treatment-conditioned final-infarct masks (ISLES'24) is recent; note, however, that the Amador group has worked on 4D-CTP outcome models since before ISLES'24, so the capability argument is partial and the blind spot is specifically the dispersion estimand.

**Verdict.** NO_DUPLICATE_FOUND_LIMITED_SEARCH — downgraded from the card's claim not because the search was narrow in breadth but because the load-bearing neighbor (Amador ISBI 2024) could only be read at abstract level; its methods/supplement must be read in full before this card advances, since a curve-shape perturbation there would make C6 INCREMENTAL. All three card-cited IDs verified and support their claims; the card must add Amador ISBI 2024 as closest prior work.

---

## C7 — Does the model price the last mile of blood delivery? (wide)

**Neighbors.**
1. arXiv:2403.06748 — "Shortcut Learning in Medical Image Segmentation" (MICCAI 2024): segmentation networks learn position-derived shortcuts (zero-padding lets a CNN encode distance to image border) — image-frame position, not anatomical territory borders, and not stroke.
2. PMID 41583397 / DOI 10.1161/SVIN.124.001375 — Werdiger F et al., SVIN 2024: attention U-Net predicting final infarct core from CTP, beating the single-threshold clinical standard; no spatial-prior audit. (The suspicious-looking PMID was explicitly verified as real via E-utilities.)
3. DOI 10.3389/fneur.2026.1794563 — Frontiers Neurol 2026 (full text read): territory-stratified ML for arterial-territory infarct prediction using an arterial-territory atlas as an explicit spatial scaffold — uses territories as input structure, does not audit whether a network learned a border-distance prior.
(Runner-up: arXiv:2607.07038, TRACE-Seg3D 2026 — counterfactual context-audit of 3D glioma segmentation; closest audit template, different construct and disease.)

**Delta.** The theme "segmentation networks learn location shortcuts" exists and territory atlases are used as model inputs, but no found work measures a learned arterial-border-distance prior with perfusion/depth-matched real-tissue patch swaps against parallel-boundary shams; the novelty is the anatomical construct plus the matched-substitution design, not "audit a segmentation model" per se.

**Why not done.** BLIND_SPOT — as the card states and the search corroborates: stroke-prediction work encodes location implicitly through convolutional coordinates while perfusion research stratifies named infarct patterns; neither tradition treats learned vascular distance as an auditable quantity.

**Verdict.** NO_DUPLICATE_FOUND_HIGH_CONFIDENCE. All three card citations verified (Carpenter 1990 at title level only; its "counterexample" characterization is plausible but unconfirmed from the abstract).

---

## C8 — The skull is a fixed-volume pressure vessel (wide)

**Neighbors.**
1. PMID 35373655 — Kauw F et al., Int J Stroke 2022/23 (full text via PMC): automated baseline CSF/ICV ratio improves multimodal prediction of malignant edema after EVT — reserve predicts edema outcome, no segmentation model audited.
2. DOI 10.1007/s12028-021-01325-x — Foroushani et al., Neurocrit Care 2021/22 (full text via PMC): explainable LSTM using automated CSF volumes and explicitly an "intracranial reserve" feature with SHAP attribution to predict malignant edema — the closest "does an ML model use reserve" work; SHAP attribution on an edema-outcome model, not within-case factorial edits on a final-infarct segmentation model.
3. DOI 10.1097/RLI.0000000000000475 — Invest Radiol 2018 (Broocks group): subacute follow-up lesion volumes are inflated by ischemic edema and can be densitometrically corrected — the empirical premise that delayed ground-truth masks embed edema-driven geometry (search-summary access).

**Delta.** Both halves of the premise are separately established — reserve predicts edema outcomes even inside explainable ML, and subacute labels are edema-inflated — but no found work audits whether a final-infarct segmentation model exploits a reserve-to-label-geometry shortcut, and the identifying reserve-by-water factorial interaction has no found precedent; reviewers may still read it as a recombination of known ingredients.

**Why not done.** BLIND_SPOT — as the card states and the search corroborates: edema prediction and infarct segmentation are separate literatures, and the ISLES'24 paper itself does not discuss edema/label-geometry issues, so the feedback path from delayed masks into the segmentation model falls between fields.

**Verdict.** NO_DUPLICATE_FOUND_HIGH_CONFIDENCE. All three card citations verified and support their claims. The card should add Foroushani et al. as a named neighbor, since it already attributes an "intracranial reserve" input inside an ML model (by SHAP, on a different endpoint).

---

## Summary

| Candidate | Title (short) | Verdict | Why-not-done |
|---|---|---|---|
| C1 | Disappearing insular ribbon (gray-white use audit) | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C2 | Clot burden beyond perfusion | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE (citation correction required) | NEW_CAPABILITY |
| C3 | Circle-of-Willis graph redundancy | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C4 | Dural-sinus HU as oxygen gauge | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C5 | Isolated sulcal effacement as rescue sign | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C6 | Bolus dispersion in raw CTP | NO_DUPLICATE_FOUND_LIMITED_SEARCH (Amador ISBI 2024 must be read in full) | NEW_CAPABILITY |
| C7 | Arterial border-zone distance prior | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C8 | CSF reserve as geometric prior | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |

Actionable corrections for the merge/ledger: (1) C2's cited PMIDs 25804568 and 27576312 are real but off-target; replace with PMID 18811738 (Puetz 2008) and Tan et al. AJNR 2009. (2) C6 must register DOI 10.1109/ISBI56570.2024.10635756 as closest prior work and its full-text inspection as a gate. (3) C8 should register Foroushani et al. (DOI 10.1007/s12028-021-01325-x) as a named neighbor. (4) C7's PMID 41583397 is verified real despite its unusual number.
