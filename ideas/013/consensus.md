# Debate summary — idea 013

## Agreed

- The original cross-sectional regressions can establish, at most, convergent calibration between CT-CLIP scores and automated calcium measurements; association alone does not show that CT-CLIP uses or localises coronary calcium (round 1).
- Geometry-matched reconstruction pairs control patient anatomy, site, referral pathway, and true calcium burden, but vary the rendering rather than the amount or location of calcium. Their defensible role is a reconstruction-sensitivity audit, not a localisation experiment (round 1).
- A 2×2 head-by-measurement interaction is stronger than a single within-pair correlation and cancels purely volume-common effects, but it remains vulnerable to a head×measurement-tool artifact response and therefore cannot establish anatomical localisation (round 1).
- A causal localisation claim would require reciprocal anatomy-specific interventions, sham controls, and a prespecified head-by-location interaction; observational regressions cannot substitute for that intervention (round 1).
- Checking only sham edits against a natural reconstruction-variability band does not validate targeted calcium edits. Global embedding similarity also cannot certify that a small, semantically important local edit is realistic (round 2).
- Edit validation would need local patch-statistic checks, held-out real-versus-edited discrimination with an equivalence margin, and agreement across independently specified edit generators. Even then, a discriminator near chance is a falsification screen rather than proof that CT-CLIP cannot detect editing artifacts (round 2).
- The proposed insertion arm lacks a verified coronary-wall target in calcium-free recipients: AI-CAC locates present coronary calcium, not an absent coronary vessel target, and the cited TotalSegmentator asset does not supply coronary-wall segmentation (round 3).
- Appearance validation cannot detect semantic misplacement. If coronary and aortic target accuracy or placement mechanics differ, that difference loads directly onto the head-by-location estimand (round 3).
- The load-bearing prerequisite for a future localisation study is comparable, independently validated coronary and aortic target localisation on nongated noncontrast CT without human annotation. This prerequisite is `NOT_INSPECTED` (round 3).
- The current candidate must retreat to rung 1: cross-sectional calibration descriptives plus the geometry-matched reconstruction-sensitivity audit may support only the sentence that CT-CLIP uses displayed vascular-calcium signal. They do not earn the original claim that its coronary head specifically localises coronary calcium (round 3).
- The submitted card's rung-3 status and `INSPECTED_TRUE` keystone are no longer accepted. The localisation claim, the main point of the original candidate, is lost (round 3).

## Unresolved

### Is the reduced rung-1 audit worth running?

- **Question:** Does the modest calibration and reconstruction-sensitivity audit have enough standalone scientific value to justify the roughly two-week inference effort?
- **Proposer's position:** It is worth running only because it is relatively cheap and produces score dynamic-range, AI-CAC compatibility, and reconstruction-variability assets needed by a possible later intervention study.
- **Critic's position:** The critic accepted the reconstruction analysis as a valuable robustness audit but did not explicitly endorse its standalone priority after the localisation claim was removed.
- **What evidence would settle it:** A Stage 0 feasibility result showing that AI-CAC operates validly on the released CT-RATE volumes, that both CT-CLIP heads have adequate dynamic range, that the calcium measurements have usable prevalence and reliability, and that the 425 reconstruction pairs yield sufficient measurement variation for a prespecified minimum detectable effect. Scientific priority after those gates remains partly a human value judgment.

### Can the localisation question be revived as a separate intervention study?

- **Question:** Can coronary and aortic intervention targets be located with comparable, independently validated anatomical accuracy on nongated noncontrast CT without a new annotation campaign?
- **Proposer's position:** A spin-off could use either within-volume relocation between observable native coronary and aortic calcifications or donor insertion gated by a validated coronary localiser, while retaining the round-2 edit-realism controls.
- **Critic's position:** Localisation remains uninterpretable until a named off-the-shelf coronary segmentation or centreline method is directly verified on the released format and passes a held-out target-validity gate, or a native-lesion relocation design supplies observable source and target anatomy with identical placement mechanics.
- **What evidence would settle it:** Direct inspection of a named localiser's primary validation on nongated noncontrast chest CT, a successful run on CT-RATE's released volume format, and a prespecified held-out comparison demonstrating coronary and aortic placement accuracy against an independent anatomical reference. Alternatively, a validated within-volume native-lesion relocation protocol with identical bidirectional mechanics and a no-op reconstruction control would settle the targeting objection.

### Would validated synthetic edits identify calcium location rather than edit artifacts?

- **Question:** If targeting becomes feasible, can synthetic insertion and erasure support the claimed anatomical mechanism rather than a generator-specific artifact response?
- **Proposer's position:** Matched-mechanics shams, local patch-statistic gates, a held-out discriminator, and agreement in sign and magnitude across independent transplantation and erasure generators would provide evidence for calcium location as their shared cause.
- **Critic's position:** Those controls are necessary but were insufficient in the proposed design because they do not validate semantic placement; a near-chance discriminator is not an in-distribution certificate for CT-CLIP.
- **What evidence would settle it:** First satisfy the independent target-validity gate; then require targeted edits to pass prespecified local realism tests and require the head-by-location interaction to replicate within a prespecified margin across two structurally different generators. Failure of either gate would leave localisation unsupported.

## Positions that moved

- **Proposer, round 1:** Conceded the critic's deeper claim that reconstruction sensitivity cannot establish localisation. This followed the argument that true calcium and its location are fixed within reconstruction pairs and that shared rendering/tool responses remain plausible. The proposer retained the narrower point that a 2×2 interaction rules out purely common-mode effects.
- **Proposer, round 2:** Conceded that the round-1 validity gate checked the sham rather than the targeted edit, and that a global embedding band cannot validate a local semantic edit. This directly answered the critic's new treatment-versus-control and global-versus-local objections.
- **Proposer, round 3:** Conceded that insertion into calcium-free recipients had no verified coronary target and that appearance gates or generator agreement cannot correct semantic misplacement. This directly answered the critic's newly identified targeting asymmetry. The concession was earned, not unearned.
- No concession occurred without a new argument; none should be flagged `UNEARNED`.

## Amendments made

- **Round zero claim:** Cross-sectional monotone and partial regressions of CT-CLIP's coronary score against AI-CAC and thresholded aortic calcium would establish that the model uses localised coronary calcium and reach rung 3.
- **Round 1 amendment:** The regressions were demoted to descriptive convergent validity. A reciprocal coronary/aortic attenuation intervention with matched shams and a head-by-location interaction became confirmatory; reconstruction pairs became a robustness and edit-validity reference. Feasibility fell from 4 to 3 and the keystone became uninspected.
- **Round 2 amendment:** Transplantation into calcium-free recipients replaced erasure as the primary intervention; erasure became an independent secondary generator. Local patch statistics, a held-out real-versus-edited discriminator, and cross-generator agreement were added. The project expanded from an approximately two-week inference audit to a five-to-six-week editing-and-validation methods study.
- **Round 3 retreat:** The intervention amendments were not adopted into the current candidate because their coronary-target prerequisite was unsupported and a third structural repair would violate the proposer's prespecified stopping rule. The candidate now claims only rung-1 use of displayed vascular-calcium signal through calibration descriptives and a reconstruction-sensitivity audit. The anatomy-specific localisation question is separated as a gated spin-off.
- **Lost:** The original deliverable sentence that CT-CLIP's coronary label specifically tracks coronary calcium, the rung-3 status, the `INSPECTED_TRUE` keystone, and the claim that observational association demonstrates use “by definition.”

## Recommendation

**REVISE.** Rewrite the idea card around the reduced rung-1 calibration and reconstruction-sensitivity audit, with localisation explicitly excluded and the keystone set to `NOT_INSPECTED`. The single most important thing for the human to inspect before deciding is whether a validated, annotation-free coronary target localiser for nongated noncontrast CT actually exists and runs on CT-RATE; that fact determines whether the high-value localisation question has a credible spin-off or whether idea 013 should remain only a modest robustness audit.
