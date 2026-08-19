# Debate summary — idea 041

## Agreed

- In round 1, both sides agreed that deleting a linear encoder direction cannot by itself identify use of Higuchi fractal dimension (FD). It can establish only dependence on an FD-associated bundle unless an input-space intervention independently moves measured FD while controlling rival curve properties.
- In round 1, both sides agreed that the card mixed input-space and representation-space claims. Input curve area, peak timing, and related properties cannot literally be preserved by an encoder-space projection; their cross-validated decodability must instead be checked after erasure.
- In round 1, both sides agreed that FD must be nontrivially decodable within CBF strata before erasure is interpreted, because the inspected phantom result reports FD–CBF correlation above 0.9. A failed anti-vacuity gate is sensitivity-limited, not a negative result.
- In round 1, both sides accepted a two-arm structure in principle: graded, in-distribution input resynthesis that demonstrably moves FD while preserving named curve quantities, plus representation erasure that removes FD decodability while preserving decodability of named controls. Both also accepted that the strongest descriptor claim remains qualified by roughness functionals inseparable from FD under those interventions.
- In round 2, both sides agreed that those two arms identify the quantity the model depends on, not the physiological source of that quantity. Because released ISLES'24 CTP was co-registered and resampled to 1 frame/sec, FD-equivalent roughness could arise from flow, motion correction, interpolation, sampling, or noise.
- In round 2, both sides agreed that the phrase “tissue-flow signal” requires a source-selectivity experiment: flow-generated and technique-generated perturbations must produce matched FD changes, and the model must respond preferentially to the flow-generated dose.
- In round 3, both sides agreed that fitting a textbook forward model to already-processed patient curves cannot supply valid flow-versus-technique source labels. Low residual error, dose matching, and an in-distribution score do not validate the fitted decomposition.
- In round 3, both sides agreed on the required form of the repair: prospective source-ground-truth validation using a primary-source-supported digital CTP phantom, under an analog of the ISLES'24 temporal sampling and preprocessing regime, before a frozen generator is transported to patient-support perturbations.
- Across all rounds, both sides agreed that failure of a prerequisite gate is a sensitivity-limited stop. It must not be narrated as evidence that the model does not use FD or flow-derived roughness.

## Unresolved

### Does the proposed phantom validation make Arm C a valid physiological source-selectivity test?

- **Proposer's position:** Yes, conditionally. Stage C0 would use the Kudo digital perfusion phantom or the Manniesing 4D CT brain phantom, where flow and acquisition parameters are known by construction. It would generate independently labeled flow-side and technique-side matched-ΔFD families under an analog of the ISLES'24 release regime, require blinded recovery of source class and parameter changes, freeze the validated generator, and only then apply it at plausible patient operating points.
- **Critic's position:** The critic required exactly this kind of prospective source-ground-truth validation, but the transcript ends before the critic evaluates the specific Kudo/Manniesing implementation. Its sufficiency therefore cannot be inferred from silence.
- **What evidence would settle it:** An independent review must inspect the cited phantom sources and the proposed C0 protocol, then determine whether the simulated co-registration/resampling chain and technique-side perturbations cover the relevant source alternatives well enough that preferential response identifies flow source selectivity within an explicitly bounded regime. A concrete unmodeled artifact that systematically enters only one family would defeat the claim.

### Can a phantom-validated generator be transported to processed ISLES'24 patient curves?

- **Proposer's position:** Phantom validation supports a deliberately qualified claim only within the validated perturbation regime. Per-patient fitting would select plausible operating points but would have no authority to assign source labels. Artifact modes absent from the phantom remain a stated residual limitation.
- **Critic's position:** The critic established that patient curves contain potentially inseparable effects from motion correction, interpolation, partial volume, scanner physics, AIF error, and model misspecification. The critic did not assess whether the final regime qualifier adequately contains the phantom-to-patient transport problem.
- **What evidence would settle it:** Compare phantom and patient curve support after the frozen ISLES-like processing chain; report parameter-range coverage, feature-distribution overlap, and sensitivity to omitted artifact families. This can bound transport, but no finite phantom establishes source validity for artifact modes it does not simulate. The human must decide whether a regime-scoped result remains scientifically worthwhile under that residual limitation.

### Are the required phantom assets and uses obtainable?

- **Proposer's position:** The Kudo CTP DICOM phantom is downloadable for research use with no redistribution, and the Manniesing phantom supplies an anatomically realistic alternative with arbitrary sampling and known tissue parameters. Derived data can be regenerated rather than redistributed. The feature-paper simulation code can also be requested as a secondary path.
- **Critic's position:** The critic requested an obtainable, primary-source-supported phantom or the feature paper's inspected simulation code. The final-round asset claims were introduced by the proposer and were not checked by the critic in the transcript.
- **What evidence would settle it:** Inspect the official downloads, licenses, supplemental files, and full methods; verify local acquisition, allowed derived use, parameter ranges, and the ability to generate both matched-FD source families. Author correspondence would settle availability of the feature-paper code but is not required if a verified public phantom suffices.

### Can the full gate stack be passed within an honest resource envelope?

- **Proposer's position:** The project is now a multi-stage program with feasibility about 2, roughly three GPU sessions, about 30 GPU-hours, days of CPU fitting and phantom validation, and a modal risk of sensitivity-limited termination. This is the cost of retaining the tissue-flow provenance claim.
- **Critic's position:** The critic did not evaluate the final resource estimate. Earlier objections imply that performance, FD movement, support, within-CBF decodability, control-decoding preservation, source recovery, and matched-dose gates are all necessary rather than optional.
- **What evidence would settle it:** A feasibility memo must price data acquisition, FD reproduction, phantom construction, CPU fitting, model training, and every gate with concrete counts and stopping rules. Because the stated GPU requirement exceeds one 12-hour session, the human must also decide whether the enlarged program fits the governing compute envelope or should be paused before implementation.

### Does the three-repair history warrant one more pipeline stage?

- **Proposer's position:** Round 3 corrected an under-implementation of round 2’s already-stated “validated phantom” requirement rather than adding a fourth scientific instrument. The proposer made a binding commitment that any further structural defect, or failure of C0, kills this card without another repair; the weaker roughness-only claim would be a successor.
- **Critic's position:** The critic had not accepted the final implementation when the transcript ended. The earlier rounds show that the original compact experiment grew into a substantially different and much larger evidentiary program.
- **What evidence would settle it:** This is principally a governance and portfolio-value judgment, not a fact that further literature can decide. Independent review of the final design and a concrete feasibility estimate can inform the judgment, but the human must decide whether a third-amendment exception is warranted.

## Positions that moved

- **Proposer, round 1:** Conceded that single-direction representation erasure cannot support descriptor-specific use and that the original preservation language confused input and representation spaces. This was earned by the critic's correlated-feature counterexample and space mismatch.
- **Proposer, round 1:** Added the input-resynthesis arm, within-CBF anti-vacuity gate, representation decodability-preservation gates, and a two-arm conjunction. This directly answered the critic's stated discharge criterion.
- **Critic, round 2:** Accepted that the two-arm amendment could identify dependence on Higuchi FD or its intervention-equivalent roughness class. This movement was earned by the added FD-moving input intervention and selective representation test.
- **Proposer, round 2:** Conceded that the two-arm design did not establish physiological provenance and added a source-selectivity arm. This was earned by the critic's distinction between quantity dependence and flow origin in processed CTP.
- **Proposer, round 3:** Conceded that the proposed fitted patient forward model was circular as a source-labeling instrument. This was earned by the critic's explanation that fit adequacy cannot recover the true decomposition of already-processed curves.
- **Proposer, round 3:** Rebuilt Arm C around prospective phantom validation and demoted patient fitting to operating-point selection. This follows the critic's existing round-2 and round-3 criterion; however, the critic never reviewed the concrete implementation, so it is not recorded as accepted consensus.
- No concession was UNEARNED. Silence after the final amendment is not agreement.

## Amendments made

At round zero, the card proposed training a small raw-temporal final-infarct model on 30 ISLES'24 cases and erasing one linear FD-predictive encoder direction. It claimed that a selective output change would show that the model uses temporal FD as a deconvolution-free tissue-flow signal, within one GPU session and about 12 GPU-hours.

The current proposed study is a gated triple conjunction for a self-trained probe model. Arm A must move measured FD by graded input-space curve resynthesis while preserving named curve properties and remaining on support. Arm B must erase within-CBF-stratum FD decodability while preserving cross-validated decodability of CBF, curve moments, sampling, and noise controls. Arm C must show preferential response to flow-generated rather than technique-generated matched FD changes using a generator first validated, blind, on a source-ground-truth digital perfusion phantom under an ISLES-like processing regime. A positive conclusion is limited to FD or an intervention-inseparable roughness functional, to the self-trained architecture, and to the phantom-validated perturbation regime.

What was lost is substantial: the original one-arm causal interpretation, definite reference to “the” final-infarct model, unconditional descriptor specificity, unqualified physiological provenance, the one-session envelope, and the expectation of a quick decisive result. The revised program has numerous sensitivity gates, makes an uninformative stop the likely outcome, carries a named phantom-to-patient transport assumption, and requires a successor rather than claim demotion if source validation fails. The idea card has not yet been rewritten to reflect any of these amendments or the corrected author attributions and score reductions identified in critique.

## Recommendation

**REVISE.** The final amendment is responsive to the critic's source-ground-truth requirement, but it arrived after three rounds, was not reviewed by the critic, is absent from the card, and changes the project from a small erasure probe into a multi-stage phantom-validation program. The single most important thing the human should inspect is whether source recovery in the proposed Kudo/Manniesing C0 design, followed by explicitly regime-limited transport to patient support, is enough to justify the words “tissue-flow signal”; if not, this card should stop and any roughness-dependence study must enter as a successor.

## In plain terms

This idea asks whether a small stroke model trained on ISLES'24 uses the jaggedness of each voxel's contrast-over-time curve, and whether it treats that jaggedness as information about blood flow. The debate agreed that simply deleting a model feature cannot show this, and that even controlled curve edits cannot tell whether the jaggedness came from blood flow or from scanning and preprocessing. The latest design adds a digital-phantom test where the true source is known, but the critic did not review that final design and its transfer to real patient curves remains limited. The human is being asked whether that phantom-validated, explicitly limited result is strong enough to retain the tissue-flow claim and justify the much larger study.

```json
{"verdict": "REVISE", "unblock": "Independently review the Kudo/Manniesing source-ground-truth C0 protocol and phantom-to-patient regime limit, then rewrite the card with the accepted triple-conjunction design, corrected citations, successor governance, concrete feasibility gates, and honest resource estimates."}
```
