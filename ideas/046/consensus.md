# Debate summary — idea 046

## Agreed

- In round 1, both sides agreed that the original smallest-removal-set rule measures proximity to loss of statistical significance, not contribution concentration; band 2's confidence interval makes this especially acute.
- In round 1, both sides also agreed that permuting patient labels cannot calibrate permutation-invariant statistics such as Gini or top-k share, and that comparison with randomly chosen subsets does not by itself correct the selection advantage of choosing the most influential subset.
- In round 2, both sides agreed that voxel counts in `per_patient.csv` cannot identify patient-specific uncertainty. The proposed inverse-count variance model assumes independence and equal variance despite spatial autocorrelation, and fitting nuisance parameters cannot recover the missing effective sample sizes.
- In round 3, both sides agreed that access to voxel arrays does not create the replication unit needed for a stable patient-carrier claim. Block or parcel resampling of one realized lesion field measures sensitivity to an invented spatial perturbation, not stability across repeat measurements.
- By round 3, both sides accepted a narrower finite-population study: signed contribution and Lorenz curves may describe which observed case contributions dominate this realized 99-case estimator, without classifying the pattern as diffuse versus carrier-concentrated and without claiming that dominance is a stable patient property.
- Both sides consistently agreed that the question's subject remains the same, even though the proposed instrument and attainable epistemic ceiling changed substantially.

## Unresolved

### Does the narrowed descriptive study preserve idea 046's claim identity?

- **Question:** May idea 046 be revised in place after relinquishing its promised binary diffuse-versus-subset-concentrated verdict, or must the descriptive finite-population study be registered as a successor?
- **Proposer's position:** Revision in place is appropriate because the question still asks who carries the reversal, and the idea-045 precedent treated a lower epistemic ceiling as identity-preserving when the question remained unchanged.
- **Critic's position:** The critic did not oppose that reading, but the final concession explicitly routes it to the operator because the round-zero deliverable promised to resolve a binary question that the surviving design no longer resolves.
- **What evidence would settle it:** No empirical evidence can settle this. It is a governance judgment about the repository's claim-identity rule and should be decided by the human, with the idea-045 precedent and the before/after deliverable sentences in view.

### Could a future dataset support a stable carrier classification?

- **Question:** Can patient-level carrier status ever be distinguished from dominance in one realized estimator?
- **Proposer's position:** Yes, but only in a different candidate using data with an actual replication unit, such as test-retest perfusion imaging, multiple independently generated lesion measurements, or an independently calibrated measurement-uncertainty model.
- **Critic's position:** Such repeated or independently perturbed admissible measurements are necessary before contribution-rank or membership stability can be claimed.
- **What evidence would settle it:** Inspectable repeated measurements or independently calibrated alternative measurements showing stable contribution ranks or membership. The pinned ISLES'24 record does not contain them, so this cannot be settled within idea 046's present dataset.

## Positions that moved

- In round 1, the proposer conceded that the original CI-flip removal rule and the permutation/random-subset calibration were invalid, in response to the critic's demonstration that they measure statistical margin or use a degenerate reference. The proposer replaced them with a hierarchical-null proposal.
- In round 2, the proposer conceded that the hierarchical null's inverse-count uncertainty law was unidentified, in response to the critic's spatial-autocorrelation and effective-sample-size argument. The proposer replaced it with a conditional voxel-level spatial-resampling tier and made descriptive curves the unconditional deliverable.
- In round 3, the proposer conceded that spatial resampling still lacked a replication unit matched to stable carrier status, in response to the critic's distinction between perturbing one realized lesion field and repeating the patient-level measurement. The binary Tier B was withdrawn entirely.
- None of these concessions was unearned: each answered a new, load-bearing objection. The sequence nevertheless shows that the original card underpriced the inferential instrument three times.

## Amendments made

At round zero, the idea claimed that a frozen, minutes-long analysis of `per_patient.csv` could decisively classify the reversal as cohort-diffuse or subset-concentrated, then compare the resulting strata on clinical variables.

The converged design claims only a finite-population description of the already-realized estimator: signed patient contributions and Lorenz curves for the 99 cases, plus descriptive comparisons of contribution-rank strata on a fully enumerated variable list. Clinical comparisons must report deficit size jointly and cannot present outcome differences already accounted for by deficit burden as an independent signature. Phenotype reads must be restricted to the 99 analyzed identifiers; acquiring those files requires re-staging the full pinned archive, not a small standalone download.

Lost in revision are the binary diffuse-versus-carrier verdict, stable patient-carrier language, a decisive negative for concentration, and the claim that the smallest decisive experiment takes only minutes on the imported aggregate table. Any future stability claim requires a separately registered candidate with genuine repeated or independently calibrated measurements.

## Recommendation

**REVISE.** The surviving descriptive census is coherent, inexpensive at its first rung, and faithful to the already-open 99 cases, but the card must be rewritten throughout: deliverable, question wording where necessary, measurement, identifiability, anticipated negative, smallest experiment, rungs, acquisition cost, multiplicity plan, mode, and scores must all relinquish the binary and stable-carrier claims. The single most important thing for the human to inspect is whether that reduced deliverable preserves the candidate's identity under the claim-identity rule; if not, it must enter as a successor rather than a revision in place.

## In plain terms

This idea asks which of the 99 observed cases contribute most to the opposite patterns seen in two blood-flow bands. It also asks whether cases with larger observed contributions differ on a short, pre-specified list of imaging and clinical variables.

The debate concluded that the data can describe contribution dominance in this one census, but cannot reliably label patients as stable “carriers” or decide that the pattern is truly diffuse versus subset-driven. Every proposed binary classifier required uncertainty or repeat-measurement information that this dataset does not provide, so the study must be narrowed to descriptive curves and comparisons.

The human is being asked whether that more modest descriptive claim is still the same idea or must be registered as a new successor.

```json
{"verdict":"REVISE","unblock":"The human must rule whether replacing the binary diffuse-versus-carrier verdict with a finite-population descriptive contribution census preserves idea 046's claim identity."}
```
