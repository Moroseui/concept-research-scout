FATAL OBJECTION: NONE
EVIDENCE: `ideas/046/idea_card.json` freezes NIHSS at 24 hours and deficit-region voxel count, while idea 047 substitutes admission NIHSS and leaves its burden extraction and endpoint undefined.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION

# Adversarial critique — idea 047

## Bottom line

The clinical join is worth doing, but the current card is not contract-ready. Its strongest defensible product is a small exploratory descriptive table for a subgroup frozen by earlier work. The card instead adds an inadequately defined “keystone” residual, implies that a small-sample null can distinguish clinical signal from imaging geometry, and prices only the extracted CSV bytes rather than the archive restage and image-derived burden calculation. None of those defects requires changing the central question, but all require narrowing the interpretation and freezing the actual variables and estimands.

## The decisive defects

### D1 — The clinical endpoint has drifted from the ratified lineage

`ideas/046/idea_card.json` freezes the optional clinical comparison to deficit-region voxel count, vessel-cap statistic, exclusion flags, **NIHSS at 24 hours**, and mRS at 3 months. Idea 047 asks for **admission NIHSS**, age, sex, and conditionally treatment fields. The official challenge design lists NIHSS at admission, NIHSS at discharge, 90-day mRS, time since onset, and reperfusion fields (ISLES'24 challenge design, official repository URL: https://zenodo.org/records/10991145/files/Ischemic%20Stroke%20Lesion%20Segmentation%20Challenge%202024.pdf), while the current Zenodo record promises admission NIHSS and 3-month mRS more generally (official record: https://zenodo.org/records/16813698). These sources do not establish that “NIHSS at 24 hours” and “admission NIHSS” are interchangeable.

This is not merely wording. Baseline neurological severity and post-treatment neurological status answer different questions and sit at different causal positions. Revision must first read only `clinical_data-description.xlsx`, freeze exact field names, time points, coding, missing-value rules, and the hierarchy of primary versus contextual variables, and then preserve the D3 restriction when case rows are staged. If the release lacks the previously frozen 24-hour field, state the forward correction and use admission NIHSS as a newly specified contextual variable; do not describe it as execution of the old frozen list.

### D2 — “Keystone-like” is not yet a reproducible endpoint

The top-ten group is reproducible: it is the already frozen signed ranks 1–10. The second proposed group is not. “Residual of |c_i| on burden” leaves open the burden definition, scale, functional form, nonlinear terms, treatment of zero contributions, leverage handling, and whether the residual is signed, absolute, studentized, or rank-based. Turning the ten largest residuals into another group after choosing among these options creates an analyst-defined result, not a frozen ecological measurement.

There is also a construct mismatch. The borrowed ecological analogy concerns impact disproportionate to abundance, but here `c_i` is algebraically a patient-specific band contrast divided by the fixed cohort size. “Abundance” has no unique analogue. Deficit volume is a plausible nuisance/exposure measure, not a validated translation of ecological abundance. The study may call the result “contribution disproportionate to measured deficit support”; it should not make “keystone” the scientific endpoint.

Repair: make the frozen top-ten-versus-rest comparison primary and treat contribution-versus-burden as a continuous descriptive plot. Predefine one burden measure and one simple model before phenotype access. Do not dichotomize fitted residuals unless a separate sensitivity analysis demonstrates that the conclusion is stable across reasonable burden definitions and functional forms.

### D3 — The proposed burden measure is not already available, and cost is understated

The low-hanging-fruit input table does **not** contain total deficit burden. `probes/023/results/results_v2/per_patient.csv` contains only `case_id,stratum,q1_voxels,q4_voxels,d`; `probes/046/results/results_v3/per_case_contributions.csv` contains contribution quantities only. The card proposes recomputing eroded Tmax>6 s voxel counts from maps, yet says the experiment uses “two 99-file CSV families totaling ~50 kB” and takes under five minutes. Those statements describe final extracted bytes, not acquisition and preprocessing.

The lineage feasibility memo already gives the honest cost: the phenotype members are inside `train.7z`, so the clinical rung requires selective extraction from/restaging of the checksum-pinned approximately 99 GB archive (`ideas/046/feasibility.md`, sections 3 and 5). Recomputing exact burden also requires the map payload and the frozen take-13 region implementation, its contract identity, and a reproducibility comparison against cached case counts. This remains feasible and GPU-free, but “minutes on 50 kB” is not an honest end-to-end envelope.

An easier option already exists: use a clearly labeled **eligible-extreme-quartile support proxy** derived from the existing q1/q4 counts, after verifying its relationship to total eligible support from the frozen take-13 definitions. It must not silently be renamed “deficit burden.” If exact eroded deficit volume is scientifically necessary, pay and state the archive/map restage cost.

### D4 — A null cannot support “clinically silent” or favor imaging geometry

Ten versus 89 is a weak design for detecting anything but large distributional separation, especially for ordinal mRS, incompletely observed clinical variables, and multiple predeclared fields. Permutation tests do not cure low power. No smallest effect of interest, precision target, or missingness floor is specified. Therefore a failure to detect a difference is sensitivity-limited; it cannot show the dominant cases are clinically silent, and it cannot push explanation toward “imaging geometry.”

This defect appears in the title, `audience_relevance`, the negative-result rationale, and the plain pitch (“whether the dominant patients look clinically different ... or ... only for imaging-arithmetic reasons”). The technical card partly concedes sensitivity limitation, but then restores the stronger dichotomy elsewhere. Revision should replace “clinically silent” with “no large clinical separation detected at the achieved precision” and require confidence intervals or randomization intervals for effect sizes. The useful negative result is bounded: it excludes only effects larger than the reported uncertainty.

### D5 — A positive comparison remains confounded and selection-specific

The group was selected for a realized final-infarct-derived contribution. mRS and later NIHSS are downstream of infarct burden and treatment; admission NIHSS reflects baseline severity, occlusion territory, collaterals, and time. Deficit volume is only one common cause or mediator. Even after displaying volume, a positive association cannot establish a clinical subtype or explain why these cases dominate. Treatment/reperfusion, onset-to-imaging time, occlusion site, and missingness could all structure the comparison.

The card's association register prevents this from becoming fatal, provided it remains strict: report joint distributions and standardized contrasts; do not say clinical variables “explain” dominance; do not fit a multivariable model with ten exposed cases and a growing covariate list. Conditional “treatment fields if present” is not a frozen analysis plan. Inventory first, then predeclare a very short contextual set.

### D6 — Endpoint and multiplicity are still unclear

The card names standardized mean differences, rank tests, and permutation nulls across mixed continuous, binary, and ordinal variables but defines no primary endpoint, test statistic, sidedness, permutation unit, missing-data rule, or interpretation threshold. “Does / does not differ” invites a binary conclusion that the proposed all-variable table cannot honestly deliver. The most defensible endpoint is not a global discovery test. It is an estimation display: for each frozen variable, give both groups' distributions, an appropriate standardized effect with uncertainty, effective sample size, and the same display stratified or accompanied by the frozen burden measure. Label all inferential p-values exploratory and do not select a headline by significance.

## Prior work, relevance, circularity, and leakage

I found no verified exact duplicate of the proposed ISLES'24 contribution-census/phenotype join. The organizers' paper uses multimodal imaging and clinical data for final-infarct prediction (arXiv:2408.10966; DOI 10.48550/arXiv.2408.10966), which overlaps in variables but not in estimand. Maier-Hein et al. show that biomedical challenge conclusions can be sensitive to the sampled test cases and aggregation choices (DOI 10.1038/s41467-018-07619-7), supporting the general benchmark-audit motivation but not establishing novelty. Broocks et al. is a thematic neighbor for clinically characterizing perfusion-threshold error (DOI 10.1148/radiol.231750; PMID 39078297), not a duplicate. The card's “appears unpublished” language is appropriately hedged; it must not be upgraded to a novelty claim, especially while the cited 2026 near-miss remains unread.

There is no concept-label circularity in the narrow descriptive join: group membership is frozen from imaging/final-infarct quantities, not defined from mRS, NIHSS, age, or sex. There is nevertheless outcome coupling: both contribution and 3-month disability are consequences of the same stroke and treatment course. That is confounding/shared-outcome structure, not prohibited leakage, as long as the analysis is explicitly exploratory and does not claim independent validation.

Medical relevance is moderate, not high. The result could tell researchers whether a program-central estimator anomaly visibly coincides with broad clinical severity. It cannot validate a perfusion biomarker, alter treatment, or characterize a population from 99 selected training cases. Its strongest audience is benchmark methodologists and researchers interpreting this exact lineage.

## Plain-pitch fidelity

**Named defect: PLAIN-PITCH OVERCLAIM.** The pitch accurately preserves the 99-case scope, aggregate-only rule, exploratory status, and absence of individual claims. It does not preserve the technical card's sensitivity-limited-null caveat. “Whether the dominant patients look clinically different ... or whether they stand out only for imaging-arithmetic reasons” presents exhaustive alternatives that this observational, underpowered comparison cannot distinguish. “Either answer changes how researchers should read” similarly overstates an imprecise null. Replace this with: the analysis can reveal a large clinical separation if present; otherwise it reports how much separation the small frozen subgroup comparison can exclude.

## Low-hanging fruit and simplest defensible execution

The easiest useful version requires no new image calculation and no model or checkpoint:

1. Freeze the schema from the already public 12.1 kB `clinical_data-description.xlsx` before opening case rows.
2. Select the already frozen signed-rank top ten from `per_case_contributions.csv`; do not create a fitted-residual subgroup.
3. Selectively extract only the 99 permitted baseline/outcome CSV pairs from the already held, checksum-verified archive under D3.
4. Produce a single aggregate table for exact available versions of mRS, NIHSS, age, and sex, with completeness, group distributions, effect sizes, uncertainty, and the existing q1/q4 support counts shown as a labeled imaging-support proxy.
5. Report all rows jointly and stop. No significance-based headline, clinical subtype language, causal adjustment, or per-patient output.

Data and labels already exist; the case group is frozen; code logic for the census and archive integrity already exists; no checkpoint, GPU, or new annotation is needed. The operational low-hanging fruit is real, although the archive extraction is not equivalent to a 50 kB download.

## Required revision

- Reconcile admission versus 24-hour/discharge NIHSS using the data dictionary and explicitly document any departure from idea 046's frozen optional rung.
- Replace “clinically silent” and the clinical-versus-imaging dichotomy throughout, including title, negative-result value, audience relevance, and plain pitch.
- Choose one exact burden/support variable, show where it comes from, and price its extraction honestly.
- Drop the residual top-decile confirmatory contrast or fully prespecify and demote it to sensitivity analysis.
- Make the primary deliverable an estimation table with uncertainty and missingness, not a binary “differs / does not differ” verdict.
- Freeze a short variable list after dictionary-only inspection; remove conditional analyst discretion such as “treatment fields if present.”
- Bind D3 to exact permitted identifiers and D4 to an exact joint display. Preserve aggregate-only outputs and suppress small cells if any categorical cross-tab risks case re-identification.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Among the frozen ten largest signed contributors and the other 89 analyzed cases, what are the aggregate differences and uncertainty in the release-defined mRS, NIHSS, age, and sex distributions when displayed jointly with one predeclared imaging-support measure?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes — it cheaply closes a specifically preregistered, still-open clinical-description rung, provided its value is an honest bounded description rather than a clinical-subtype or explanatory claim.
