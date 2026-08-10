# Revision of idea 013

## Outcome

The idea is now one conditional rung-1 question: across geometry-matched reconstructions of the same CT-RATE acquisition, do reconstruction-induced changes in an automated coronary-calcium measurement covary with changes in CT-CLIP's coronary-calcification score?

The revision removes the original localisation claim. No code was written. The next action is Stage 0 validation of the model asset, measurement path, and within-pair support—not inference or image editing.

## Material changes

1. **Narrowed the study to one question, one head, and one measurement.** The coronary-calcification head and automated coronary-calcium measurement are the sole confirmatory variables. Cross-sectional calibration, the arterial head, thresholded aortic calcium, and the 2×2 “double dissociation” were removed.

2. **Made the geometry-matched reconstruction contrast the entire experiment.** The card now uses the 425 same-acquisition pairs already inspected under idea 004. Pairing holds anatomy, true calcium burden, habitus, positioning, referral pathway, disease prevalence, site, and report content fixed while reconstruction changes.

3. **Removed the observational localisation claim.** A score-versus-biomarker regression does not show model use “by definition,” and partial regression does not establish anatomical localisation. The original deliverable sentence claiming that the coronary label specifically localises coronary calcium was deleted.

4. **Demoted the candidate to rung 1.** The revised deliverable is limited to use of *displayed coronary-calcium signal under the tested reconstruction contrasts*. The card explicitly states that shared sensitivity of CT-CLIP and AI-CAC to kernel, noise, blooming, slice thickness, or partial volume remains an alternative. The study cannot pass the rung-2 artifact gate or reach rung 3.

5. **Removed all synthetic-intervention architecture.** Coronary insertion, erasure, transplantation, donor/recipient matching, patch discriminators, sham edits, and generator agreement were deleted. Debate showed that these repairs require an unverified coronary target in calcium-free recipients and would constitute a separate methods study.

6. **Recorded localisation only as a gated spin-off.** A successor intervention study may enter separately only after direct inspection shows comparable, independently validated coronary and aortic target localisation on nongated noncontrast CT without human annotation. Its keystone remains `NOT_INSPECTED`; it inherits no queue position or conclusion from idea 013.

7. **Replaced the false keystone.** The old card marked `INSPECTED_TRUE` because two labels, software packages, and data existed. The real prerequisite is that a coronary-calcium tool validly consumes the released CT-RATE representation and yields reliable, above-noise within-pair measurement variation. This is `NOT_INSPECTED`, so feasibility and novelty confidence are capped at 3.

8. **Made file compatibility and measurement validity prospective stop gates.** AI-CAC's released path is DICOM-oriented, whereas CT-RATE is distributed as processed volumes. Stage 0 must document a defensible conversion or choose a validated replacement, quantify reliability, exclude unsupported thickness/FOV strata, and establish adequate within-pair support before CT-CLIP scores are inspected.

9. **Separated what pairing rules out from what it does not.** Pairing rules out patient, acquisition, positioning, habitus, prevalence, referral, and report-label explanations within a pair. It does not rule out a shared head×measurement-tool reconstruction response, a generic hyperdensity response, or vendor/site effect modification. These limitations now bound the claim rather than appearing as covariates that supposedly solve identification.

10. **Strengthened test integrity.** The revised card requires a patient-level development/test split, frozen checkpoint and preprocessing, prespecified contrast orientation, measurement reliability and support gates, minimum detectable coupling, equivalence margin, outlier rule, and multiplicity rule before the untouched test scores are examined.

11. **Preserved a meaningful negative outcome.** After measurement validity, dynamic range, and power gates pass, a confidence interval wholly inside a preregistered equivalence margin is a decisive negative for material within-pair coupling in the tested contrasts. Failure to reject zero remains sensitivity-limited. Stage 0 failure is a feasibility finding, not evidence that CT-CLIP ignores calcium.

12. **Corrected novelty language.** No novelty is claimed. The exact delta was not found in the already inspected primary sources, but the card requires a targeted 2025–2026 primary-source audit before describing it as previously unreported.

13. **Updated scores and priority.** Clarity remains 5. Identifiability falls from 4 to 2 because the central shared reconstruction/tool response survives. Medical relevance is 3, interest is 3, prior legwork is 4, feasibility is capped at 3, data readiness is 3, evaluation readiness is 3, negative-result value is 4 conditional on the gates, and novelty confidence is capped at 3. The recalculated priority score is 3.25.

## What did not change

- X remains independently computable without a human annotator, conditional on Stage 0 measurement validation.
- The primary readout remains label-free and does not depend on report quality or annotation provenance.
- The candidate still reuses real, same-acquisition images rather than an extreme deletion or an unvalidated synthetic counterfactual.
- The CT-RATE validation-pair asset remains promising, but its existence does not resolve the measurement or checkpoint keystones.

## Next decision

Advance only to Stage 0. A feasibility memo and probe contract may follow only if the exact checkpoint is provenance-verified, the calcium measurement is valid on the released files, and enough eligible pairs exceed the frozen measurement-noise and precision thresholds. Explicit human approval remains required before any probe code is written.
