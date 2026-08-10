FATAL OBJECTION: The proposed partial association cannot establish that Sybil uses coronary calcium, and the exact published “no visible future-cancer-site nodule” cohort is not reconstructible from the cited release.
EVIDENCE: Sybil JCO 2023 Data Supplement/PMC10419602; public Sybil repository `files/*.csv`, `scripts/data/parse_mdai_annotations.py`, and `sybil/loaders/image_loaders.py` (inspected 2026-08-10).
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: PAUSE

# Detailed adversarial review

## 1. The central inference is association, not use

The card asks whether Sybil's score is “a function of” CAC and promises the sentence “Sybil is using coronary artery calcium.” Its primary identifying analysis is a partial regression of Sybil score on AI-CAC after adjustment for emphysema and BV5. That does not establish use.

A positive coefficient is also expected if Sybil reads any omitted correlate of CAC: chronological age, smoking duration or intensity, aortic calcium, vertebral degeneration, airway disease, cardiac size, image noise/body habitus, or an unmeasured centre/protocol mixture. Adding two selected rivals does not make CAC the causal image feature. Pack-years in particular is not an image-level intervention and is measured with error; residual confounding is almost guaranteed. “Unique variance” is unique only relative to the variables and measurement models in that regression.

The proposed kernel arm does not repair this. As the card correctly admits, changing reconstruction changes calcium blooming, emphysema thresholds, edges, noise, and essentially every texture seen by Sybil. Correlated changes in AI-CAC and Sybil therefore establish reconstruction sensitivity or, at best, generic high-density-channel sensitivity—not CAC-specific use. The design can reach a source-supported statement such as “Sybil score contains information correlated with automated CAC,” but not the charter's rung-3 deliverable.

This objection is repairable only by making a controlled CAC intervention the primary analysis: use the AI-CAC lesion mask to remove or plausibly inpaint calcified coronary lesions while holding all other voxels fixed, with matched interventions in (i) noncoronary high-attenuation lesions and (ii) equally sized coronary regions without calcium. The estimand is the within-scan Sybil-score change attributable specifically to coronary calcium. Counterfactual validity remains a gate: constant-HU deletion would repeat idea 006's OOD failure, so realistic local inpainting, mask-size matching, boundary checks, and negative controls are mandatory.

## 2. The “nodule-free” cohort keystone was not inspected true

Mikhael et al. did not study scans with no nodules in the ordinary sense. Their exploratory analysis excluded cases annotated by their radiologists as having a visible nodule **in the exact location of the subsequently proven cancer**. The paper reports the resulting AUC (2-year 0.81, 95% CI 0.74–0.86), but a published aggregate AUC is not a released case-membership list.

Direct inspection of the public Sybil repository found:

- `files/lung_cancer_dataset.csv` and `files/lung_cancer_metadata.csv` contain headers plus empty placeholder rows, not the NLST split or cohort membership.
- `scripts/data/create_nlst_metadata_json.py` expects an external Ardila split spreadsheet at an internal mount path.
- `scripts/data/parse_mdai_annotations.py` expects an unreleased MD.ai JSON export and an internal `annotation_comments_12062020.csv`.
- the repository README says annotations and splits are available, but the inspected release does not contain the artifacts needed to reproduce the future-cancer-site exclusion.

Thus the card's keystone status must be downgraded from `INSPECTED_TRUE`. The nearest checkable fact was that the paper performed the analysis; the still-assumed load-bearing fact was that outsiders can identify the same scans. They currently cannot from the cited release. This resembles idea 001's `DATA_INSUFFICIENT` failure: a published analysis exists, but the linkable subset needed for the proposed inference is unavailable. It also resembles the recurring wrong-keystone error more strongly than the card acknowledges.

There is an additional endpoint ambiguity. “Nodule-free” implies absence of visible nodules, whereas the published exclusion concerns a visible precursor at the later cancer site and was based on joint expert annotation informed by NLST clinical localization. Incidental nodules elsewhere can remain. The title, question, cohort definition, and deliverable must use the narrower wording.

## 3. Annotation provenance is not absent

CAC itself satisfies the charter: AI-CAC is an independently computable measurement. However, human annotation enters the primary cohort restriction. The Sybil repository states that two thoracic radiologists jointly annotated lesions and were informed by the series/image number and anatomical location of biopsy-confirmed cancers. That is suitable for the authors' stated retrospective sensitivity analysis, but it is neither an independent blinded measurement nor an available machine-computable selection rule.

This is not concept-label circularity—CAC was not Sybil's target label—but the card's statement that “no human rating enters any readout” evades the selection problem. Conditioning on an outcome-informed lesion assessment can also create a selected population whose score–CAC relation does not generalize to screening scans prospectively called nodule-free.

## 4. CAC measurement is feasible, but Stage 0 is underspecified

AI-CAC is genuine reusable prior legwork. Hagopian et al. released code and weights and evaluated non-gated chest CT against paired gated radiology-report Agatston scores (NEJM AI 2025, DOI 10.1056/AIoa2400937; PMID 40746702). TCIA's current NLST collection page lists CT images and a public clinical subset under CC BY 4.0 (DOI 10.7937/TCIA.HMQ8-J677). These parts are verified and materially lower implementation risk.

But the proposed “~40 NLST scans that also have a visually-read ordinal CAC” is not tied to a released per-scan reference table. Watts et al. (PMID 25370000) validates visual CAC prognostically in an NLST sample; citing that paper does not establish that its scan-linked scores are public or joinable to TCIA identifiers. Unless the actual table/schema is inspected, Stage 0 requires new manual reads or author-shared data and violates the advertised no-annotation simplicity.

Transfer is not merely absolute calibration. Scanner era, slice thickness, kernel, motion, and noise can alter false positives and ranks. A rank-only association does not survive arbitrary differential error correlated with reconstruction or Sybil score. Validate AI-CAC on an explicitly obtainable reference set, or limit the claim to AI-CAC's operational output rather than biological CAC.

## 5. Sybil's input transform weakens the Agatston framing

The public inference loader applies a lung window centred at −600 HU with width 1500 HU, clipping all values above approximately +150 HU, converts to 8-bit, resizes in-plane to 256×256, and samples/resamples to 200 slices. Consequently Sybil cannot read the density weighting that defines an Agatston score above the conventional calcium threshold in the same way AI-CAC does. It can still read the presence, area, shape, and location of saturated bright calcium, but “automated Agatston-equivalent score” is not the most faithful mechanistic X.

The revised concept should therefore be coronary calcium **burden visible after Sybil preprocessing**—for example lesion presence and mask area/volume after mapping the AI-CAC mask through the exact transform—with Agatston as a secondary clinical coarsening. This makes a negative more interpretable and aligns the intervention with what the model actually receives.

## 6. Confounds and claim identifiability

Most plausible positive-result alternatives remain:

1. **Shared biological burden:** age, smoking, aortic atherosclerosis, emphysema, vascular pruning, and other degenerative changes cause CAC to mark a diffuse phenotype. The partial regression rules out only the measured linear components of LAA-950 and BV5; it does not rule out the phenotype.
2. **Acquisition/reconstruction/site:** these affect both AI-CAC and Sybil. Metadata adjustment cannot eliminate unobserved site, and site is masked. The kernel arm actively induces this alternative rather than excluding it.
3. **Body habitus/noise:** auto-exposure and attenuation alter calcium detection and the entire Sybil input. Effective mAs is incomplete control.
4. **Outcome/referral/label leakage:** report leakage is not relevant because Sybil sees pixels and Stages 1–2 do not use reports. Trial referral pathway and prevalence are largely fixed by NLST enrollment. These are genuine strengths, but they do not rescue feature identifiability.

A targeted within-scan CAC intervention with anatomical and high-density controls would rule out much of (1)–(3) because the rest of each scan remains fixed. It would not alone establish that the signal is biologically causal for lung cancer; the honest claim is about model use, not disease mechanism.

## 7. Prior-work overlap and relevance

No inspected primary source here directly pre-empts the Sybil-score-versus-CAC question. Mikhael et al. establish Sybil and the exact-site-nodule exclusion (JCO 2023, DOI 10.1200/JCO.22.01345; PMID 36634294). The 2026 “Auditing Sybil” preprint (arXiv:2602.02560) supplies adjacent generative-intervention machinery but, based on its inspected text as recorded in the card, does not quantify CAC. The 2026 HeartLung/MESA cardiac-versus-lung-CT article is adjacent, but the card has only a search-summary-level inspection; novelty confidence cannot rest on an unread abstract/full text. The novelty claim should remain `NOT FOUND in inspected sources`, not “untouched.”

Medical relevance is real but overstated. Finding CAC dependence would change interpretation of Sybil as a lung-cancer risk score and could expose poor transport across populations with different cardiovascular risk. It would not imply that CAC should be “read alongside” Sybil or alter management without showing incremental calibration, transport, or decision impact. The strongest medical consequence is model validity and subgroup transportability, not opportunistic cardiac care.

## 8. Compute and data burden

Inference itself is compatible with a single GPU. The burden is data engineering: NLST contains 11.3 TB in full, cohort reconciliation is unresolved, AI-CAC needs original DICOM while Sybil applies its own transform, and BV5 is described as though it were as turnkey as lungmask without a directly named released implementation or validation plan. Running all three competing ideas jointly is scientifically sensible but not a three-week “one command” study.

The current data-readiness score of 5 and feasibility score of 4 are unjustified while exact cohort membership, the reference CAC table, the test-split join, and the BV5 implementation are uninspected. Under the charter, feasibility and novelty confidence should be capped at 3 until the real keystone is inspected true.

## 9. Negative-result value

The anticipated null from partial regression is **sensitivity-limited**, not decisive. A null can arise from AI-CAC transfer error, Sybil's clipping/downsampling of calcium, collinearity and measurement error in smoking/LAA/BV5, nonlinear or thresholded use, inadequate variation, or subset-selection error. An equivalence margin on Sybil-score SD does not solve errors-in-variables or define a clinically meaningful minimum feature dependence. `negative_result_value` should be at most 2 for the current design.

A well-powered controlled CAC intervention can produce a more decisive negative, conditional on demonstrated intervention fidelity and a positive-control model known to respond to CAC. Without that positive control, even the interventional null remains sensitivity-limited.

## 10. Low-hanging-fruit repair

The easiest useful formulation drops the unreleased exact-site-nodule subset and the cancer endpoint initially. Use an obtainable frozen NLST/Ardila test subset, run the released Sybil ensemble and AI-CAC, map AI-CAC masks through Sybil's exact preprocessing, and compare original scores with realistically CAC-inpainted scores plus matched controls. No clinical labels, pack-years, BV5, mediation, or full 11.3-TB download are required for the primary readout. Public checkpoints and code exist for both models; TCIA permits targeted series download. This directly tests the interesting feature-use question on ordinary screening scans.

This simpler experiment does **not** reproduce the published nodule-excluded residual. It should be treated as a general Sybil mechanism study, with the special residual cohort added only if the authors release case membership or a reproducible public rule is found. An initial association/attention-overlap benchmark is acceptable as a feasibility check, but it is not worth publishing alone and must not be promoted to a rung-3 claim.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: On a frozen public NLST test subset, does realistic removal of AI-CAC-segmented coronary calcium change Sybil's risk score more than size-matched coronary and noncoronary high-density control edits?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes—if counterfactual fidelity and positive controls pass, it directly identifies a named feature used by an open lung-cancer model; a score–CAC correlation alone is not worth doing.
