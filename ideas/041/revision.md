# Revision — idea 041

## Outcome

The card now asks one bounded question: within a source-ground-truth phantom regime transported to ISLES'24 patient support, does one frozen raw-temporal final-infarct surrogate respond selectively to flow-generated rather than technique-generated matched changes in Higuchi fractal dimension?

This preserves the original interest in model use of temporal roughness as a tissue-flow signal, but narrows the model, evidence, and transport scope. No code, data inspection, model training, phantom acquisition, or probe work was performed.

## Material changes

1. **Recorded and narrowed the claim.** `deliverable_original` preserves the original sentence verbatim. The revised deliverable concerns one self-trained, frozen surrogate and only the perturbation regime validated in a source-ground-truth phantom. It makes no claim about “the” challenge model, other architectures, or unmodeled artifacts.

2. **Reduced the project to one confirmatory question.** The endpoint is the paired difference between flow-side and technique-side output dose-response slopes under matched FD change. FD reproduction, input resynthesis, representation erasure, source recovery, support, and model performance are prerequisite gates for interpreting that contrast, not separate headline questions.

3. **Removed unnecessary architecture.** The shallow causal 2D+time U-Net, center-stratified patch recipe, 20/5/5 split, and five-case prediction-volume rule are deleted. Feasibility must choose and freeze one minimally adequate raw-temporal surrogate, split, performance threshold, and power calculation before any output is examined.

4. **Corrected all author attributions.** The exact FD paper is by Ichikawa, Kondo, and Yokoyama, not Lim et al. DOI `10.3389/fnins.2022.1009654` is Winder et al., not Robben et al. PMID `32501132` is Klug et al., not van Os et al. Identifiers and substantive neighbor relations remain.

5. **Separated input and representation spaces.** Input-space resynthesis must move measured FD while preserving named curve quantities and patient support. Representation-space erasure must remove within-CBF-stratum FD decodability while preserving cross-validated decodability of CBF, curve quantities, frame count, and noise controls. The card no longer claims that an encoder projection literally preserves input curves.

6. **Added the anti-vacuity gate.** Because the inspected phantom result reports FD-CBF correlation above 0.9, FD must be nontrivially decodable within CBF strata before erasure has meaning. Failure is sensitivity-limited, not evidence of non-use.

7. **Retained the input-resynthesis necessity arm as a gate-bearing part of the conjunction.** Four graded doses must demonstrably move FD, preserve area, peak height, peak time and the first two moments within frozen tolerances, and pass a common support test. A surrogate that reacts only to representation deletion does not earn a descriptor-use claim.

8. **Added physiological-source identification.** The debate established that curve edits and encoder erasure identify a quantity, not its source. The revised primary contrast therefore compares matched FD changes generated through known flow parameters versus modeled acquisition/preprocessing parameters.

9. **Rejected fitted patient curves as source truth.** A good fit to processed patient data cannot determine whether roughness came from flow, motion correction, interpolation, partial volume, scanner physics, AIF error, or model misspecification. Per-patient fitting may select operating points only; it cannot label sources.

10. **Made prospective phantom validation mandatory.** Candidate instruments are Kudo et al. (DOI `10.1148/radiol.12112618`) and Manniesing et al. (DOI `10.7717/peerj.2683`). Before patient inference, Stage C0 must independently verify acquisition and license, known parameters, controllable technical factors, ISLES-like sampling, range coverage, and blinded recovery of source class and parameter change. The debate's asset claims were not independently reviewed, so the card does not treat them as accepted facts.

11. **Bound phantom-to-patient transport.** A finite phantom cannot exclude artifacts it does not simulate. Feature-support overlap, parameter coverage, and omitted-artifact sensitivity must be reported; even a positive result is valid only within the modeled regime.

12. **Preserved a meaningful negative.** If every performance, measurement, decodability, preservation, source-recovery, dose-matching, support, and power gate passes, an equivalence-bounded equal response rejects selective flow-source use for this surrogate in the validated regime. It remains useful as evidence that the surrogate treats technical roughness as physiological information. Failed gates and ordinary non-significance are not negative results.

13. **Added successor governance.** If source validation fails, the card stops. It does not silently demote itself to the weaker claim that the surrogate uses FD-associated roughness. That weaker study would require a successor under the claim-identity rule.

14. **Corrected prior legwork and readiness.** Prior legwork falls from 5 to 3: the measurement is published, but reusable code, a checkpoint, a source generator, and a transport study are absent. The approximately 99 GB public release is monolithic in the inspected record; the former 25 GB staging assumption and one-day reproduction promise are removed.

15. **Repriced feasibility.** The one-session, 12-GPU-hour claim is deleted. The honest preliminary envelope is roughly 30 GPU-hours across several sessions, several CPU-days, and about 100 GB source storage, subject to a feasibility memo. Feasibility is 2 because a sensitivity-limited stop is likely.

16. **Added the charter-required dataset record.** The card now states the published 149-public/96-hidden realized split, acute NCCT/CTA/CTP and derived maps, co-registration and 1-frame/sec resampling, follow-up-DWI/DeepISLES ground-truth process, public CC BY-NC-SA access, monolithic archive, and four official evaluation measures. These verified facts are distinguished from unverified phantom and model assumptions.

17. **Qualified novelty.** The card identifies the closest association, temporal-model, regional-context, and phantom work by primary identifier. It reports only a targeted-search gap and explicitly says that failure to find a duplicate is not proof of novelty.

18. **Updated scores and arithmetic.** Clarity is 4, identifiability 2, medical relevance 3, interest 4, prior legwork 3, feasibility 2, data readiness 3, evaluation readiness 2, negative-result value 3, and novelty confidence 3. The rubric-weighted priority is 2.85. The score reflects the large identification and transport burden rather than the original compact pitch.

## Prohibited conclusions

A positive result would not show that the surrogate computes the Higuchi algorithm, that FD has a unique biological meaning, that every patient artifact has been excluded, that a challenge winner or other architecture behaves similarly, that segmentation accuracy improves, or that clinical decisions benefit. A failed prerequisite cannot be narrated as model non-use.

## Next gate

Independent review must inspect the candidate phantom sources and decide whether the proposed source-recovery protocol and explicit transport boundary are sufficient to support the words “tissue-flow signal.” A feasibility memo must then price every gate and freeze counts, tolerances, margins, stopping rules, data retrieval, and compute. Until both occur, no probe contract or model work is justified.

```json
{"claim_retention": "narrowed"}
```
