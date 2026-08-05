FATAL OBJECTION: The proposed observational partial associations cannot establish that Sybil uses vascular pruning, and the Murray-exponent arm has neither a validated LDCT measurement nor a disease-specific directional prediction.
EVIDENCE: Sobieski et al., arXiv:2602.02560; Altieri Correa et al., DOI 10.1115/1.4068886; idea_card.json `smallest_decisive_experiment` and `suspected_signal`.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial review

## Bottom line

There is a worthwhile descriptive analysis hiding here, but not the claimed model-decoding study. Stage 1 asks whether two quantities computed from the same CT covary: Sybil's risk score and BV5/TBV. Stage 2 adds another correlated CT phenotype, LAA%-950, to a regression. Neither varies vascular pruning independently of the rest of the image, probes the representation, occludes vessels with a valid control, or otherwise tests model reliance. A positive result is therefore compatible with Sybil completely ignoring vessels and reading any correlated smoking, airway, parenchymal, nodule, acquisition, or habitus signal. This fails rung 1 before the study reaches the rung-2 confound gate.

The card's own source makes the problem worse rather than solving it: San Jose Estepar et al. report that emphysema and vascular ratios are related (PMID 23656466; DOI 10.1164/rccm.201301-0162OC). Conditioning one noisy, reconstruction-sensitive image biomarker on another does not create independent variation. It can instead produce unstable coefficients, attenuation from differential measurement error, or collider/overadjustment effects among co-manifestations of smoking-related disease. The larger surviving coefficient cannot identify which feature the model uses.

This is the same estimand failure already established in the Idea 008 debate: association between a model output and a computable phenotype is not evidence of model use. It is not an annotation-provenance failure, but it does die like that prior candidate's unrepaired rung-1 objection. Calling the analysis a comparison of “competing mediators” is also incorrect without an exposure, an outcome-mediated causal estimand, and defensible mediator assumptions; these are correlated candidate readouts, not identified mediators.

## The Murray claim is not yet a hypothesis

The physical story is more specific than the evidence permits.

- Altieri Correa et al. analyzed seven healthy human pulmonary arterial geometries and reported a mean exponent of 2.31 ± 0.60; the human comparison with 3 was not significant (p=0.3721) (DOI 10.1115/1.4068886; PMID 40489106). Their data establish neither a normal individual-level reference nor a COPD, pruning, or cancer-risk shift.
- Dong et al. reported 2.92 ± 1.07 in 16 healthy subjects (PMID 32618514; DOI 10.1152/ajpheart.00127.2020). The disagreement and dispersion are large relative to the proposed effect, and both studies concern visible preacinar/angiographic anatomy rather than small vessels on NLST LDCT.
- “Remodeling changes the maintenance-to-dissipation cost ratio and therefore shifts the exponent” is speculation. The card gives no predicted direction, minimum effect, affected branch orders, or expected relationship between the fitted exponent and BV5/TBV. Without those, almost any exponent result can be narrated after the fact.
- Scale invariance under uniform multiplication of every radius does not imply invariance to breath hold. Inspiration changes vascular recruitment, distension, regional geometry, and which peripheral branches cross the visibility threshold. A segmentation-derived exponent can change even if the underlying branching law does not. The proposed C3 check is therefore a repeatability test, not proof of physiological invariance.

Dropping the analogy would indeed change the code, so the Murray framing is not merely verbal decoration. But extra code is not enough: it currently generates an unstable exploratory statistic without a validated biological interpretation. The compound deliverable is especially unsafe because a BV5-only positive cannot support the exponent clause, while an exponent-only positive is expressly declared unbelievable by the card.

## Measurement and data feasibility

The keystone is correctly marked `NOT_INSPECTED`, but Stage 0 as written cannot turn it true. “Consistent recovery depth” on 50 NLST and 50 diagnostic scans has no reference segmentation and therefore measures self-consistency or visual plausibility, not fidelity. Comparing low-dose with unmatched diagnostic cases additionally confounds dose with anatomy, disease, protocol, contrast, and reconstruction. No annotator-free statistic can reveal missed peripheral vessels when the reference tree is unknown.

There is closer prior work than the card acknowledges. Park et al. developed a noncontrast pulmonary-vessel segmentation model using matched virtual-noncontrast and contrast-enhanced vessel maps, tested it externally, and evaluated PVV5/%PVV5 on heterogeneous COPD LDCT with thin sections under 1.5 mm (Radiology: Cardiothoracic Imaging 2021; PMID 34036222; DOI 10.1148/ryct.2021200315). This shows that LDCT BV5 is not an untouched feasibility question. It does **not** rescue this study: that dedicated model and validation do not validate TotalSegmentator on NLST's 1–2.5 mm scans, and the reported implementation/weights are not established here as openly runnable.

The TotalSegmentator repository proves availability, not fitness for this endpoint. Its `lung_vessels` task now emits artery, vein, airway, and airway-wall classes, but the repository entry supplies no inspected NLST external validation, small-calibre recall curve, BV5 agreement, or bifurcation-radius accuracy. Moreover, separate artery/vein classification is not required for the original combined-vessel BV5 definition, so taking on A/V classification risk buys little for the primary endpoint. The 5 mm² boundary corresponds to about 2.52 mm diameter for a circular cross-section—precisely where slice thickness, partial volume, reconstruction kernel, denoising, and centerline/radius conventions can dominate.

The claimed low-hanging data are also less ready than stated. NLST images and Sybil weights are public, but “nodule-free” status depends on the Sybil team's radiologist annotations, and the repository record already notes unresolved held-out-ID reconciliation. Site is masked. Effective mAs adjustment cannot generally repair noise-dependent missed-branch bias, and DICOM dose fields plus body size do not identify the spatially varying noise texture after reconstruction.

Compute is not fatal on a single GPU for a small probe, but thousands of high-resolution vessel segmentations plus skeleton/radius processing are not a cheap add-on. The candidate should not inherit C1's data-readiness score of 5 when its decisive measurement pipeline, validation reference, and reliable branch scale are absent.

## Confounding, leakage, and circularity

There is no conventional concept-label circularity: BV5 is computed rather than assigned by the risk-label annotators, and the primary score-versus-phenotype analysis uses no cancer outcome. Report leakage is likewise irrelevant to Sybil's image-only input.

There is, however, measurement circularity of a different kind. Both BV5/TBV and LAA%-950 are functions of the same noisy reconstructed volume, and emphysema can make vessel boundaries harder for the segmenter. A “pruning” association may therefore be manufactured by disease-dependent segmentation failure. Adding recovery depth as a covariate does not fix this if recovery depth is itself estimated from the same segmentation.

The design does not rule out the standing alternatives:

- Scanner/vendor, kernel, slice thickness, dose/noise, and site can alter both model score and small-vessel recovery. Fixing or stratifying some fields reduces but does not isolate them.
- Inspiration, positioning, body habitus, and gravity-dependent vascular calibre remain plausible common causes or measurement modifiers.
- Smoking dose, airway disease, parenchymal texture, occult nodules, coronary calcium, and other cancer-risk phenotypes remain visible to Sybil and correlated with BV5.
- Disease prevalence and referral pathway are held relatively constant by the screening cohort, but that helps transport consistency, not within-cohort mechanism identification.

Partial regression rules out none of the unmeasured image alternatives. It only asks whether the chosen vascular summary contains residual linear information after chosen covariates, subject to overlap and measurement error.

## Endpoint and negative-result audit

The endpoint is underspecified. Sybil emits six horizon-specific risks, yet the card does not nominate one fixed horizon, a scale for the score, an effect form, an equivalence margin, multiplicity handling, or a minimum detectable partial association. “Estimate its association” invites horizon and model-form selection.

The anticipated negative is misclassified. A null partial BV5 coefficient after conditioning on LAA%-950 is **sensitivity-limited**, not decisive: it may reflect poor small-vessel recovery, multicollinearity, nonlinearity, range restriction in a single-kernel subset, inadequate overlap, or conditioning on a downstream co-phenotype. It does not strengthen the parenchymal hypothesis. The negative-result-value score should be at most 2 unless measurement agreement and an equivalence margin are established first. A Stage 0 failure is useful operational information, but it is not a negative answer about what Sybil uses and is unlikely to be publishable without a reference standard.

## Prior-work overlap and relevance

I did not verify a published BV5-versus-Sybil analysis. That is a search result, not a novelty claim; conference abstracts and active COPD vascular-imaging groups remain incompletely covered. The exact model link may be new, but novelty cannot compensate for an unidentified estimand.

Medical relevance is plausible but overstated. BV5/TBV has outcome and histology anchors in pulmonary disease, including the cited mortality association (PMID 32926788) and histologic comparison (PMID 34881020). Yet showing that a cancer-risk score correlates with it would not establish a causal cancer substrate, chronic hypoxia, immune surveillance, or a management implication. Those mechanistic bridges are speculative and should not motivate interpretation of the primary result.

## Easier formulation and existing assets

The genuinely low-hanging formulation is: on the already identified same-acquisition NLST reconstruction pairs, ask how repeatable **total intrapulmonary vessel volume and a provisional BV5/TBV estimate** are across kernels and slice thicknesses, and whether the corresponding within-pair Sybil score change covaries with the measurement change. The images, pair construction, Sybil code/checkpoint, and reconstruction metadata already exist in the repository's Idea 008/C1 legwork. No outcomes, nodule labels, or new cohort are required. The estimand is an acquisition-sensitivity audit: it can distinguish a shared reconstruction response from score stability while the vessel metric moves. It cannot establish biological pruning use.

Before even that analysis, the smallest honest gate is a method-comparison benchmark on publicly obtainable thin-section noncontrast CT cases with a trustworthy vessel reference or paired contrast-derived reference. Compare TotalSegmentator with the closest validated/released vessel method at branch-level recall, volume agreement, and threshold-crossing stability. If no usable reference labels or runnable comparator can be confirmed, do not manufacture “fidelity” from visual depth. The new TotalSegmentator weights and the published Park et al. validation are existing legwork, but they are not yet a ready labeled benchmark.

This easier audit is worth doing only as a small arm of the emphysema/reconstruction project, because it directly tests whether a proposed readout is a reconstruction artifact and can prevent a false biological story. It is not worth a standalone Sybil-mechanism paper, and it should not include the Murray exponent until branch-radius repeatability is demonstrated against reference geometry.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: On same-acquisition NLST reconstruction pairs, are provisional BV5/TBV measurements and Sybil risk scores coupled in their within-patient response to kernel and slice thickness, after first establishing vessel-measurement agreement at the relevant calibre?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes, as a bounded acquisition-sensitivity arm that can kill a vascular-artifact story cheaply; no, as evidence that Sybil uses biological pruning or Murray-law departure.
