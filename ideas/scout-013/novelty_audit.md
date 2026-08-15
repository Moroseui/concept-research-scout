# Novelty audit — cycle 013

Audited 2026-08-15 against `candidates_all.json` (5 candidates, baseline track).
All searches were run live (WebSearch, with WebFetch confirmation where
possible); the full query and neighbor record is in `novelty_manifest.json`.
Access levels are stated per neighbor. Absence of a found duplicate is not
verified novelty.

---

## C1 — The vessel map inside the mosaic-attenuation score (baseline, Mode A)

### 1. Neighbors

1. **arXiv:2607.20993** — *Sparse Concept Channels in Frozen 3D CT Vision
   Encoders* (Nooralahzadeh et al., 2026). Training-free "concept channel
   probe" on frozen 3D CT vision-language models (Pillar-0, Merlin): finds
   ~10 embedding channels per radiological finding and validates causally by
   channel ablation. Does not probe CT-CLIP and does not touch mosaic
   attenuation or vessel caliber. [access: abstract]
2. **DOI 10.1007/978-3-032-05479-1_10** — *Interpreting CT-Scans with CLIP: An
   Explorative Study of Attribution Methods for 3D Vision-Language Models*
   (Injarabian et al., CLIP workshop @ MICCAI 2025, LNCS 16126). Applies
   spatial attribution methods to a CT-CLIP-style 3D contrastive model to ask
   whether it attends to spatially meaningful regions; no concept-level
   intervention, no specific head decoded. [access: search_summary]
3. **DOI 10.1148/radiology.205.2.9356630** — Worthy, Müller et al., *Radiology*
   1997. Establishes the clinical rule the candidate wants to test in the
   model: in airway/vascular causes of mosaic attenuation, vessels in lucent
   lung are smaller than in opaque lung, while in infiltrative disease vessel
   caliber is uniform. Human-reader rule; no model. Supporting quantitative
   work: %CSA<5 / small-vessel volume measures (PMC8601304; PubMed 37661531).
   [access: search_summary]

### 2. Delta

No prior work performs input-space, factorial vessel-caliber-versus-attenuation
edits against any named head of a chest-CT foundation model; the nearest
interpretability neighbors intervene in embedding space (channel ablation, on
other models) or stop at spatial attribution, and the vessel-caliber
discriminator itself exists only as a human-reader rule and a static
quantitative-CT measurement. This is a genuine mechanism delta, not a
dataset delta.

### 3. Why not done

`NEW_CAPABILITY` — a public, runnable 3D chest-CT model exposing a named
per-volume "Mosaic attenuation pattern" score only exists since the CT-CLIP /
CT-RATE release (arXiv:2403.17834, 2024), and this repository's verified local
inference lineage (frozen checkpoint, bit-deterministic load probe) is what
makes the factorial-edit readout practical. The clinical rule has been sitting
unused as a model-decoding target since 1997.

### 4. Verdict

`NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — nine distinct searches across
interpretability, quantitative-CT, and counterfactual-editing angles;
neighbors found on every axis and distinguished. Note for the critique stage:
arXiv:2607.20993 shows concept-level causal probing of frozen 3D CT encoders
is now an active area — the input-space design should cite it and state the
delta explicitly.

---

## C2 — The open fissure inside lung-cancer risk (baseline, Mode B)

### 1. Neighbors

1. **arXiv:2602.02560** — *Auditing Sybil: Explaining Deep Lung Cancer Risk
   Prediction Through Generative Interventional Attributions* (ICML 2026).
   First interventional attribution audit of Sybil using a 3D diffusion-bridge
   framework; finds Sybil behaves approximately as a linear model with
   pairwise interactions over nodule presence, ties the baseline term to age
   via global cues "like bone density", and exposes fixation on ECG electrodes
   and gown snaps. Does not examine fissures or emphysema conditioning.
   [access: full_text]
2. **PMC11826273** — Yang et al., *Transl Lung Cancer Res*. Deep lung-cancer
   risk model trained on NLST parenchyma with nodules ≥8 mm excluded (AUC
   0.68–0.82), arguing background parenchyma carries risk signal beyond
   nodules; calls for feature-ablation follow-up but names no specific
   anatomy. [access: search_summary]
3. **DOI 10.1038/s41598-023-41322-y** (PMC10465516) — *IntegrityNet*, Sci Rep
   2023. Attention U-Net computing automated per-fissure completeness
   (89.8–96.1% accuracy) for endobronchial-valve / collateral-ventilation
   screening — the measurement tool half of the candidate, never applied to
   cancer risk. Related: fissure integrity vs emphysema distribution
   (PMID 28987683); fissure completeness vs surgical outcomes (ICVTS 2018).
   [access: search_summary]

### 2. Delta

The closest neighbor audits exactly this model with a stronger (generative
interventional) toolkit but never tests fissure completeness, so the
candidate's specific hypothesis is untested; however, that audit's finding —
Sybil's non-nodule signal largely reduces to an age/bone-density baseline plus
artifacts — directly lowers the prior on an independent fissure signal and
must be engaged, making this a moderate delta on a freshly audited model
rather than a first look.

### 3. Why not done

`BLIND_SPOT` — fissure-completeness measurement lives in the interventional
pulmonology / lung-volume-reduction community (collateral-ventilation
planning), while lung-cancer risk modeling lives in the screening community;
no incentive existed to cross them, and the Sybil audit that could have
tested it chose nodule- and artifact-centric interventions. Partially
consumed: the interventional machinery for auditing Sybil now exists
(arXiv:2602.02560), so the remaining gap is the hypothesis, not the method.

### 4. Verdict

`NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` on the specific fissure question, with a
material flag: the candidate card's `closest_prior_work` is now stale —
arXiv:2602.02560 supersedes "nobody has decoded Sybil beyond nodules" and its
nodule-linearity finding should be treated as adverse prior evidence in any
revision. If the candidate advances, the smallest decisive experiment should
consider reusing that audit's intervention framework rather than the proposed
conditional-observational design.

---

## C3 — Name the skeletal frailty inside mortality prediction (baseline, Mode B)

### 1. Neighbors

1. **DOI 10.1007/s10916-023-02030-2** — Lin et al., *J Med Syst* 2024.
   CNN trained on ~48k chest radiographs against DXA T-scores detects
   osteoporosis and independently stratifies all-cause mortality (HR 1.67;
   HR 2.59 in the DXA subgroup). Builds a new skeletal classifier as a
   mortality predictor; does not audit an existing mortality model.
   [access: search_summary]
2. **PMID 31322692** (PMC6646994) — Lu et al., *JAMA Netw Open* 2019
   (CXR-Risk), with companion CXR-Age (PMID 33744131). The anchor mortality
   models; interpretability stops at qualitative class-activation maps
   naming heart, aortic knob, sternal wires, breast, waist — no vertebral or
   morphometric feature measured. [access: search_summary]
3. **PMID 39549901** (*Bone* 2024) + **arXiv:2001.01277** — automated
   opportunistic VCF detection on frontal chest radiographs (AUC 0.930) and
   deep-learning vertebral segmentation on lateral CXR with Genant-style
   height ratios; plus Kado et al., *Arch Intern Med* 1999, establishing the
   VCF→mortality epidemiologic link a model could exploit.
   [access: search_summary]

### 2. Delta

All three threads exist separately — CXR-derived skeletal frailty predicts
mortality, the anchor mortality models exist with only qualitative saliency,
and automated CXR vertebral morphometry exists — but no work treats a
published CXR mortality model as the object of study and tests, by
morphometry-normalizing intervention, whether its score is driven by
vertebral compression burden; the delta is the causal-audit combination, and
Lin 2024 strengthens rather than preempts the hypothesis.

### 3. Why not done

`BLIND_SPOT` — the bone/DXA community builds its own predictors rather than
auditing prognosis models, and the CXR-prognosis community's interpretability
practice stopped at class-activation maps, which cannot name a morphometric
feature; the disciplinary boundary left the audit unattempted. The candidate's
real risk remains what the card already states: DATA_ACCESS to the exact
anchor model, which the searches did not resolve.

### 4. Verdict

`NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — eight distinct searches across
interpretability, opportunistic-screening, and epidemiology angles; neighbors
found and distinguished on each. Lin 2024 should enter the card as supporting
prior legwork (a skeletal mortality signal on CXR is now demonstrated, not
hypothesized).

---

## C4 — The renal artery as a buckled pressure line (baseline, Mode C)

### 1. Neighbors

1. **arXiv:2605.09002** — *CT-IDP: Segmentation-Derived Quantitative
   Phenotypes for Interpretable Abdominal CT Disease Classification* (Dahal &
   Lo). Builds >900 organ/compartment descriptors on the Merlin abdominal-CT
   benchmark and fits sparse interpretable classifiers per disease; treats
   Merlin as a benchmark rather than probing the released model's logits, and
   its descriptor set contains no vessel-centerline geometry.
   [access: abstract]
2. **PMID 35003315** (PMC8731270) — renal-artery CT anatomy vs hypertension in
   3,000 patients: accessory renal arteries and early branching independently
   associate with hypertension. Branching anatomy, not tortuosity, and no
   model. [access: search_summary]
3. **PMC11157772** — arterial tortuosity index in non-atherosclerotic vascular
   disease is associated with age, aneurysms, and hypertension; supported by
   carotid tortuosity vs hypertension duration (PMC10961416). Establishes the
   clinical premise in other vascular beds; no renal-artery-specific claim,
   no ML model. Methodological analog: Grad-CAM attribution of a retinal
   hypertension model to vessel bifurcations (PMC7058325). [access:
   search_summary]

### 2. Delta

No prior work computes renal-artery centerline tortuosity on abdominal CT and
tests it against a hypertension model's output — the tortuosity-hypertension
association exists only in carotid/systemic beds, the renal-artery CT
literature studied branching variants instead, and the one interpretable-
Merlin effort (CT-IDP) omits vessel geometry entirely; the delta is real but
the candidate correctly self-reports that it shares the tortuosity grammar
with backlog item scout-010-c05, which caps how novel the scientific move (as
opposed to the organ) is.

### 3. Why not done

`NEW_CAPABILITY` — a public abdominal-CT foundation model with a hypertension
phenotype head only exists since the Merlin release (arXiv:2406.06512), and
automated renal-artery segmentation adequate to centerline extraction
(e.g., RenalSegNet-class tools, built for surgical planning) is similarly
recent; before both, the question had no readout on either side.

### 4. Verdict

`NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` on the external literature (eight
searches, neighbors on all three angles), with the standing internal caveat
that the closest analogue is the repository's own backlog (scout-010-c05,
aortic tortuosity), which is a portfolio-homogenization concern, not a
novelty duplicate. The card's own novelty_confidence of 2 remains the honest
scientific reading given the identifiability ceiling it also self-reports.

---

## C5 — Collateral failure written in the cortical veins (baseline, Mode C)

### 1. Neighbors

1. **arXiv:2206.15445** (DOI 10.1007/978-3-031-16452-1_40) — *Asymmetry
   Disentanglement Network*, MICCAI 2022. Interpretable NCCT infarct
   segmentation that disentangles pathological from anatomical hemispheric
   asymmetry into 3D asymmetry maps — the closest interpretability neighbor,
   but its asymmetry is generic parenchymal density, not venous, with no
   collateral link. [access: search_summary]
2. **DOI 10.1161/STROKEAHA.120.032242** — Faizy et al., *Stroke* 2021, plus
   COVES meta-analysis (DOI 10.1007/s00234-025-03701-2). Cortical vein
   opacification / venous-outflow profiles on CTA predict tissue-level
   collaterals and outcome — the venous-to-collateral precedent, entirely a
   contrast-opacification phenomenon. [access: search_summary]
3. **DOI 10.1186/s12883-020-01907-w** (PMC7466490) — asymmetrical prominent
   cortical vein sign on SWI marks penumbra and poor collaterals, correlating
   with MTT/TTP and DSA collateral status. Conceptually the candidate's core
   idea, but the sign exists because SWI is sensitive to deoxyhemoglobin
   susceptibility — a mechanism physically absent on NCCT.
   [access: search_summary]

### 2. Delta

The candidate occupies a genuinely unoccupied intersection — automated
cortical-vein density asymmetry on non-contrast CT, validated against
CTA/CTP collateral status, then tested as a driver of a deep NCCT infarct
model — but the search sharpened why it is unoccupied: every existing venous
asymmetry-collateral result rides on deoxyhemoglobin susceptibility (SWI) or
contrast opacification (COVES), and neither mechanism produces the proposed
NCCT density signal, so the Phase-1 physics gate the card already mandates is
carrying even more weight than the card states.

### 3. Why not done

`BLIND_SPOT`, with an honesty caveat. The venous-collateral literature grew in
modality silos (SWI and CTA), and nobody asked whether any density trace of
the phenomenon survives on non-contrast CT — but the absence may equally
reflect tacit physical implausibility rather than oversight: delayed venous
filling and perfused-blood-volume changes plausibly move NCCT attenuation by
only a few HU. This is exactly what the candidate's model-free Phase 1 would
settle, and a Phase-1 kill would be a decisive, publishable negative for the
proposed mechanism. Not classified `TRIED_AND_FAILED`: no attempt was found.

### 4. Verdict

`NO_DUPLICATE_FOUND_HIGH_CONFIDENCE` — ten distinct searches across
interpretability, venous-sign, and automation angles; neighbors found and
cleanly distinguished by modality and mechanism. The verdict certifies
novelty, not plausibility; the mechanism's physical existence on NCCT is
untested and is the candidate's declared keystone.

---

## Summary

| # | Candidate | Verdict | Why not done |
|---|-----------|---------|--------------|
| C1 | The vessel map inside the mosaic-attenuation score | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C2 | The open fissure inside lung-cancer risk | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C3 | Name the skeletal frailty inside mortality prediction | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |
| C4 | The renal artery as a buckled pressure line | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | NEW_CAPABILITY |
| C5 | Collateral failure written in the cortical veins | NO_DUPLICATE_FOUND_HIGH_CONFIDENCE | BLIND_SPOT |

Cross-cutting notes for the orchestrator: (a) C2's card is stale — the
Auditing Sybil paper (arXiv:2602.02560) both provides reusable intervention
machinery and supplies adverse prior evidence (nodule-linearity, age/bone-
density baseline) that any revision must engage; (b) C3 gains prior legwork
from Lin et al. 2024 (skeletal mortality signal on CXR demonstrated); (c) C5's
novelty is certified but the same search results imply the physical mechanism
may not exist on NCCT, reinforcing the card's Phase-1-first structure; (d)
C4's only near-duplicate is internal (backlog scout-010-c05), a
homogenization concern rather than a novelty kill.
