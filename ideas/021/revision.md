# Revision — Idea 021

## Outcome

The idea is now one conditional question: under normalization frozen from the unedited case, does one frozen ISLES'24 final-infarct model use the healthy hemisphere as a **signed patient-specific perfusion reference**, rather than merely responding to global gain, an anomalous opposite hemisphere, or an invalid edit?

The card remains at rung 0. It authorizes no code or inference. An independent mechanism review, an in-distribution bidirectional scaling envelope, and a prospective power calculation must all pass before a probe contract can be drafted.

## Material changes

1. **Repaired the preprocessing pathway.** The original claim that raw spatial separation made edit and readout disjoint was deleted. Every variant must reuse perfusion normalization constants computed from its unedited case, and contralateral-only editing must leave affected-side final network-input voxels bit-identical. This directly addresses the critique's fatal nnU-Net z-score objection.

2. **Replaced the easy registration keystone with the real conjunction.** NCCT-space registration remains a verified enabling fact, not the keystone. The load-bearing prerequisite is now an adequately powered up-scaling range that is realistic across channels, preserves affected-side inputs, and supports a response conjunction that named non-reference mechanisms cannot reproduce. Its status is `NOT_INSPECTED`, so feasibility and novelty confidence are capped at 3.

3. **Narrowed the deliverable away from the exact clinical rCBF mechanism.** The revised sentence claims a signed patient-specific contralateral reference only. It does not claim division by mean contralateral CBF, Campbell's threshold, or identity with the precise convention clinicians use. Campbell et al. remain motivation and an independent measurement anchor.

4. **Removed the absolute-values branch.** A null can no longer be interpreted as evidence that the model reads absolute perfusion, nor as evidence of fragility to cardiac output or injection variation. The pinned preprocessing itself controls scale, and ipsilateral texture or topology remains another possible information source.

5. **Made the positive result a conjunction, not any cross-hemispheric response.** The confirmatory result requires a signed monotone dose response in both directions, including increased affected-side predicted deficit when the healthy hemisphere is up-scaled; no emergent contralateral lesion; and a contralateral-only response exceeding the global response by a frozen margin.

6. **Added global and partial-area arms but kept one scientific question.** Global scaling tests whole-image gain behavior. Partial-area scaling diagnoses area-dependent response. These are controls within one reference-setting experiment, not separate hypotheses or tiers.

7. **Promoted non-reference mechanisms to explicit competitors.** Laterality competition, bilateral-lesion detection, unsigned anomaly response, generic contralateral context, and whole-image gain control are no longer dismissed by spatial separation. The card states which part of the conjunction targets each one.

8. **Required independent review of the unresolved identifying logic.** Before any confirmatory score is seen, a fresh methods review must write the predicted sign for every mechanism under contralateral down-scaling, contralateral up-scaling, and global scaling. If any plausible non-reference mechanism satisfies the full conjunction, Idea 021 pauses. This implements the consensus recommendation rather than treating the proposer's unreviewed round-three amendment as accepted.

9. **Strengthened edit-validity gates.** A generic real-versus-edited discriminator is insufficient by itself. Every dose must also pass final-tensor distribution checks and explicit CBF/CBV consistency checks against frozen Tmax, CTA, and NCCT. A contralateral predicted-lesion emergence threshold is frozen prospectively; breach invalidates the case-dose.

10. **Corrected the physiological rationale.** Unilateral scaling is no longer described as natural cardiac-output variation, which is global. The card instead treats unilateral scaling as a controlled mechanism test that may resemble vascular disease or create cross-channel inconsistency and therefore must earn validity empirically.

11. **Added a mandatory power gate.** The unsupported 40-case plan was removed. Development-fold variability must support a prospective minimum-detectable-effect calculation for both the signed slope and mirror-over-global margin. If the clean obtainable cohort is too small, the study stops as unpowered.

12. **Preserved a meaningful negative with strict conditions.** After all gates pass, confidence bounds excluding the preregistered minimum signed slope or mirror-over-global margin decisively weaken material use of the reference by this frozen model. Non-significance, inadequate power, invalid edits, emergent contralateral lesions, or loss of bit identity are not negative evidence about model use.

13. **Removed unsupported assets and scope.** The nonexistent “official baseline recipe” is gone. The model is explicitly self-trained and frozen, and no claim is made about the unreleased winning system or other challenge submissions. The card no longer calls the work a simple one-week experiment.

14. **Specified automatic cohort QC without pretending the outcome mask solves it.** The revised card requires array-level orientation and geometry inspection, automatic midsagittal-plane QC, and automatic detection or exclusion of bilaterally abnormal mirrors. The released follow-up lesion mask is used for cohort construction, not as proof that chronic contralateral disease is absent.

15. **Addressed every standing confound at the supported level.** Within-case pairing fixes scanner, vendor, site, protocol, reconstruction, positioning, habitus, prevalence, referral pathway, and report-label leakage for the intervention contrast, but does not establish transportability. Cross-channel inconsistency is treated as edit validity, not waved away as a fixed confound.

16. **Made the prior-failure comparison honest.** The proposal can still die like idea 006 if unilateral scaling is out of distribution. It also repeats the program's wrong-keystone pattern unless preprocessing disjointness, mechanism uniqueness, realism, and power are directly inspected. Annotation provenance does not apply because X and the primary readout are automatic.

17. **Removed the weaker fallback from this candidate.** “The model uses contralateral perfusion information” changes the reference-setting predicate and is not silently retained as an alternate deliverable. If that is all the machinery can test, the work stops for a human claim-identity ruling and likely successor registration.

18. **Updated scoring.** Identifiability is 3 because the proposed controls are strong but their uniqueness remains disputed. Feasibility is 3 because the true keystone is uninspected. Prior legwork is 3 because no official recipe or winner checkpoint exists. Negative-result value remains 4 only for the powered, fully gated negative. The recalculated priority score is 3.50.

## Claim retention

The revision keeps the original model, anatomical source, and central predicate that the healthy hemisphere acts as the patient's reference. It removes two stronger clauses the experiment could not identify: equivalence to the exact clinical relative-CBF computation and the contrast with absolute-value reliance. That is a substantial narrowing of the original deliverable, but it does not replace the reference-setting claim with mere contralateral-information use.

```json
{"claim_retention": "narrowed"}
```
