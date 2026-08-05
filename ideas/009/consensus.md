# Debate summary — idea 009

## Agreed

- The original partial-association design does not test whether Sybil uses pulmonary vascular pruning. A residual association between Sybil score and BV5/TBV after conditioning on LAA%-950 remains compatible with the model ignoring vessels and using correlated smoking, airway, parenchymal, nodule, habitus, or acquisition signals. The proposer accepted this in round 1 and withdrew the regression as the primary experiment.
- A null partial BV5/TBV association is sensitivity-limited, not decisive. Measurement error, multicollinearity, disease-dependent segmentation failure, nonlinearity, and range restriction would remain viable explanations. The proposer accepted this in round 1.
- Same-acquisition reconstruction pairs can support an acquisition-sensitivity audit, but cannot establish biological reliance on pruning. Both sides agreed in round 1 that this belongs as a bounded arm of the reconstruction work, not as a rescue of Idea 009.
- The proposed calibre-band ablation is a potentially valid rung-1 test of sensitivity to synthetic removal of sub-5 mm² vessel-like structures, subject to intervention-validity controls. It is not a test of reliance on naturally occurring vascular pruning. The proposer accepted this construct distinction in round 2.
- The synthetic ablation can diverge from the natural-pruning claim in either direction: a positive edit response need not mean natural BV5 variation drives intact scores, while a null edit response need not exclude pruning biology if Sybil reads associated parenchymal changes rather than vessel voxels. This became common ground in rounds 2 and 3.
- Dropping the branching-exponent limb abandons the named Murray-law mechanism rather than repairing it. Neither the observational design nor the ablation tests that limb. Both sides agreed in rounds 2 and 3 that the narrower ablation should be a separate candidate if pursued.
- No presently named dataset supports independently measured natural within-patient variation in both BV5 and the branching exponent while holding acquisition and parenchymal change sufficiently fixed and tying that variation to a model-reliance test. The proposer reviewed NLST longitudinal scans, paired breath-hold data, and reconstruction pairs in round 2; the critic accepted the account in round 3.
- The candidate's keystone was mis-specified because the estimand was not first shown to be a reliance test. This differs subtly from prior wrong-keystone cases involving a valid estimand resting on a false factual premise. The proposer clarified this in round 3, without disagreement from the critic.
- Idea 009 as titled should be rejected rather than paused: the surviving barriers are failures of estimand and construct, not missing access or an inspectable fact likely to unblock the proposed study. Both sides converged on this disposition in round 3.

## Unresolved

There is no unresolved disagreement about the disposition of Idea 009 as titled.

Two empirical questions remain for possible future candidates, but neither was disputed as a basis for rescuing this one:

- **Could a narrower calibre-band ablation yield an interpretable rung-1 result?** The proposer considers the controlled ablation potentially valid if artifact exchangeability across calibre bands is supported by a non-vessel artifact floor and a preregistered calibre dose-response. The critic considers it a separate candidate whose claim must be limited to sensitivity to synthetic removal. Evidence that would settle intervention validity includes matched sham results showing that score changes are specific to vessel-like structures rather than patch scale or inpainting artifacts. Even favorable evidence would not settle the natural-pruning claim.
- **Could the Murray-exponent question ever be reopened on CT?** Both sides require a newly identified dataset with natural within-patient BV5 and exponent variation, sufficiently fixed acquisition and parenchymal state, and a model-reliance test tied to those changes. The proposer additionally requires a same-session repeatability study establishing that within-patient exponent changes exceed the measurement precision floor. Those data would determine whether reopening is technically defensible; they are not currently identified.

## Positions that moved

- **Proposer, round 1:** Conceded that score–phenotype partial associations do not establish model use, in response to the critic's argument that correlated, reconstruction-sensitive quantities from the same image leave many alternative explanations. The proposer withdrew Stages 1–2 as the primary experiment and corrected the anticipated negative from decisive to sensitivity-limited. This concession was earned by a substantive estimand objection.
- **Proposer, round 1:** Agreed that the reconstruction-pair audit answers a different acquisition-sensitivity question and cannot rescue the biological-use claim. This was earned by the critic's identity-check argument.
- **Proposer, round 2:** Conceded that the calibre-band ablation does not repair Idea 009 because it abandons the Murray-exponent mechanism and tests synthetic deletion rather than naturally occurring pruning. This followed the critic's new construct-validity argument and was earned.
- **Proposer, round 2:** Abandoned the attempted partial identity pass after recognizing that synthetic ablation can disagree with natural-pruning reliance in both positive and negative directions. The second direction—Sybil could read parenchymal correlates while ignoring vessel voxels—strengthened the reason for concession rather than merely repeating the critic.
- **Proposer, round 3:** Accepted the critic's summary and the REJECT disposition. This did not introduce a new concession; it formally closed the already-earned round-2 agreement. It is not an unearned capitulation.
- No critic position materially moved. No concession in the transcript should be flagged **UNEARNED**.

## Amendments made

At round zero, the idea claimed that Sybil uses natural pulmonary vascular pruning—both reduced BV5/TBV and a departure of the arterial branching exponent from Murray's cube law—rather than parenchymal destruction. It proposed observational partial associations as the decisive test and classified the anticipated null as decisive.

In round 1, the proposer replaced the primary analysis with within-patient, volume-matched calibre-band ablation and shams, retained regression only as descriptive, changed the negative classification to sensitivity-limited, dropped the Murray-exponent clause, and proposed a symmetric LAA%-950 intervention for the comparison with parenchymal destruction. This amendment lost the title's defining physical mechanism, reduced the claim to rung-1 edit sensitivity, added an artifact-exchangeability keystone, and increased compute and feasibility burdens.

In round 2, that amendment was withdrawn as a repair. The narrower ablation was retained only as a possible separate candidate with the deliverable: *Sybil's score responds to removal of sub-5 mm² vessel-like structures beyond a volume- and geometry-matched sham.* It must not be described as evidence that Sybil uses natural pruning. Idea 009 itself has no surviving amended claim or experiment.

## Recommendation

**REJECT.** Before deciding, the human should look most closely at the estimand mismatch: neither association with a computable vascular phenotype nor sensitivity to synthetic vessel deletion identifies reliance on naturally occurring pruning and Murray-exponent departure. Revisit only if a dataset and validated design can isolate natural within-patient BV5 and exponent variation from acquisition and parenchymal change, with adequate exponent repeatability and a model-reliance test tied to that variation.
