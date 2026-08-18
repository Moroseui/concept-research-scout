# Debate summary — idea 030

## Agreed

- Acute-CSF overlap can be a conservative, high-specificity sentinel for anatomically impossible voxels in the released ISLES'24 labels, but it is not a sensitive or general measure of swelling-related registration displacement (critic round 1; proposer accepted in round 1).
- The proposed observational model comparison cannot identify that a final-infarct model uses a mass-effect displacement halo. Lesion geometry, territory, severity, prediction volume, and smoothing can produce the same association, while DeepISLES is not a matched control because it differs in inputs, time point, task, coordinate frame, training data, and model (critic round 1; proposer conceded in round 1).
- An affine-versus-deformable re-registration comparison cannot determine which tissue-to-tissue geometry is erroneous without independently validated corrected labels. It would show dependence on label-transfer method, not use of a swelling-induced error (proposer round 1; critic confirmed in round 2).
- Training matched models on released labels versus labels with only conservatively verified acute-CSF intersections removed could causally test whether those impossible supervised voxels cause prediction within the same set. It would not establish that the broader label displacement is a mass-effect halo or that the model places infarct according to swelling-displaced geometry rather than acute tissue evidence (critic round 1; proposer accepted in round 1; critic confirmed in round 2).
- That narrower paired-label claim changes the deliverable sentence and therefore must be a successor under the claim-identity rule, not a revision of idea 030. The model-free ventricular-CSF benchmark audit is likewise a separate successor (both sides by round 2).
- Idea 030 should be rejected under its present identity with `IDENTIFIABILITY_FAILURE`. The verified dataset facts about affine MRI-to-NCCT transfer, the 2–9-day follow-up window, and the provenance of the released `space-ncct` masks remain reusable evidence; the inference built from them is what failed (both sides, round 2).

## Unresolved

No substantive disagreement remains between proposer and critic.

One empirical reopening question remains: can independently validated acute-space corrected lesion labels be obtained that isolate local swelling displacement beyond merely clipping CSF voxels?

- **Proposer's position:** Such a reference is not obtainable from the currently identified assets; cross-time, cross-modality deformable registration alone supplies no validated sign convention.
- **Critic's position:** This reference, combined with a matched training contrast holding acute inputs, split, architecture, augmentation, optimization, and evaluation fixed, is the evidence required to identify the original claim.
- **What evidence would settle it:** Obtain and independently validate acute-space corrected lesion labels that specifically undo local swelling displacement beyond CSF clipping, then run the matched training contrast with a prespecified spatially localized endpoint. Without that new asset, the original question cannot be settled with the proposed ISLES'24 design.

Whether successors S1 and S2 merit promotion was not adjudicated in this debate. S1 would require a fresh card and validity gates for the conservative ventricular-CSF sentinel; S2 would additionally require S1 to find non-trivial prevalence and would inherit S1's verified voxel set.

## Positions that moved

- **Proposer, round 1 — earned concession.** In response to the critic's identifiability argument, the proposer withdrew the DeepISLES comparison and accepted that correlations between ground-truth and predicted CSF overlap cannot isolate learned label-geometry error.
- **Proposer, round 1 — earned concession.** After testing the critic's suggested matched-label repair, the proposer accepted that no obtainable reference geometry identifies tissue-to-tissue swelling displacement. The proposer narrowed the only causal experiment available to reproduction of conservatively verified impossible voxels and recognized that this changes claim identity.
- **Critic, round 2 — convergence after the concession.** The critic accepted the proposer's disposition and successor split, while preserving the independently validated corrected-label condition for reopening the original question.
- **Proposer, round 2 — confirmation, not a new concession.** The proposer restated the already converged rejection and ledger treatment without a new substantive argument or further movement. This was not UNEARNED capitulation because no additional consensus claim depends on it; the substantive concessions were already earned in round 1.
- No substantive concession was UNEARNED.

## Amendments made

At round zero, idea 030 claimed that a final-infarct model uses swelling-displaced lesion geometry inherited from affine transfer of 2–9-day follow-up MRI, rather than acute tissue evidence alone. The design proposed to infer this from acute-CSF overlap, correlations with lesion severity and mass effect, an affine-versus-deformable displacement field, and comparison with DeepISLES.

The debate did not produce an amendment that preserves that identity. Instead, it withdrew the model-use claim and separated two possible successors:

1. **S1, model-free benchmark audit:** measure how often released ISLES'24 masks contain conservatively verified acute ventricular-CSF voxels and how removing only those voxels changes all four official evaluation measures. Associations with mass effect may characterize the finding but cannot uniquely attribute its cause.
2. **S2, paired-label causal experiment:** conditional on S1 finding non-trivial prevalence, train matched models on released versus impossible-voxel-clipped labels and compare localized held-out predictions inside the independently defined impossible set and matched controls.

What is lost is the central mechanistic headline: neither successor establishes that the model uses a general swelling-displacement halo, that affine transfer caused every identified impossible voxel, or that predictions rely on displaced geometry rather than acute tissue evidence. The original idea therefore has no surviving executable claim under its current identity.

## Recommendation

**REJECT.** The debate converged after a substantive first-round objection and an explicit attempt to test the proposed repair; this was not a one-round debate with no real criticism. The single most important thing for the human to examine before reconsidering idea 030 is whether independently validated acute-space corrected lesion labels now exist that isolate local swelling displacement beyond CSF clipping. Without that asset, the original mass-effect-halo model-use claim remains unidentifiable; S1 and S2 must re-enter separately with no inherited queue position.

```json
{"verdict": "KILL", "kill_code": "IDENTIFIABILITY_FAILURE", "unblock": "Obtain independently validated acute-space corrected lesion labels that isolate local swelling displacement beyond CSF clipping, then test them in a fully matched training contrast with a localized endpoint."}
```

## In plain terms

This idea asks whether stroke-prediction models learn errors caused when lesion outlines from later, potentially swollen brains are aligned onto earlier CT scans. It specifically proposed checking whether models predict damaged tissue in places that were clearly fluid on the earlier scan.

The debate concluded that the proposed comparisons cannot show that swelling-related alignment error caused the model's behavior, because ordinary lesion geometry, severity, smoothing, and other differences can produce the same pattern. A narrower audit of impossible label voxels and a controlled test of whether training reproduces those voxels may still be worthwhile, but they answer different questions and must be considered as separate ideas.

The human is being asked to reconsider the original idea only if independently validated corrected lesion outlines become available that separate swelling displacement from the competing explanations.
