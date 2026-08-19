# Debate summary — idea 039

## Agreed

- In round 1, both sides agreed that projection onto the central-volume-consistent manifold versus equal-energy tangent shams identifies directional dependence on the off-manifold component, not use of that component as a confidence map for perfusion evidence. Monotone dose response and energy matching do not remove the raw-value, spatial-placement, or gradient-alignment alternatives.
- In round 1, both sides agreed that the confidence-map claim requires an interaction test: the response to a perfusion-evidence edit must differ as a function of the residual. The projection/tangent experiment was therefore demoted to supporting evidence of residual dependence.
- In round 2, both sides agreed that comparing naturally high- and low-residual sites remains observational in the residual. Matching measured severity and anatomy cannot hold the complete receptive-field state fixed or exclude ordinary nonlinear conditioning on CBV and MTT.
- In round 2, both sides agreed that the residual must be manipulated at the same site and crossed with the perfusion-evidence edit. They also agreed that such a factorial establishes functional behavior on the tested support, not that the network explicitly computes an internal residual.
- In round 3, both sides agreed that the proposed single-channel CBF evidence edit changes the signed central-volume residual and therefore does not form an independent factor. The evidence edit must preserve the preregistered residual set-point if the interaction is to be interpretable.
- Across the debate, neither side argued that the original scientific question changed. The dispute concerned whether successive instruments identified that question.

## Unresolved

### Does the round-three compensated factorial identify functional use of the residual as a confidence signal?

- **Proposer's position:** Yes, conditionally. Jointly lowering CBF while exactly compensating through CBV or MTT preserves signed residual, and assigning the residual carrier and evidence compensator to different channels permits a within-site difference-in-differences. Replication across the two role-disjoint constructions, residual-sign strata, and compensator shams would support the functional confidence-map claim on the tested support.
- **Critic's position:** The critic requested an r-preserving joint construction, coordinate-matched compensator shams, replication across CBV- and MTT-carried constructions, no crossing of r = 0, and a frozen realism gate. The proposer adopted these requirements, but the transcript ends before the critic assesses whether the resulting role-disjoint design is sufficient. Acceptance therefore cannot be inferred.
- **What evidence would settle it:** A further independent design review should algebraically inspect all four cells in both role assignments and test whether any residual-blind multichannel response mechanism can still satisfy the complete conjunction. The review must explicitly accept or reject the proposed set-point verification, compensator-sham adjustment, carrier replication, and sign test as identifying the functional claim.

### Can the released maps support a nontrivial residual and the full edited-cell inventory?

- **Proposer's position:** This is an empirical Stage 0 question. The study proceeds only if stored MTT is not merely an algebraic or quantized copy of CBV/CBF, the residual survives artifact exclusions, and enough sites in every required carrier-by-sign cell have three-channel dose headroom.
- **Critic's position:** The critique identified a serious possibility that MTT is computed directly as CBV/CBF, making the residual zero or quantization-dominated. The debate did not dispute that risk or establish that the necessary inventory exists.
- **What evidence would settle it:** Direct inspection of released voxel arrays, including a preregistered algebraic-dependence and quantization audit, common-support and clipping checks, residual-sign counts, and eligible-site counts under the final joint-edit constraints.

### Are the jointly edited cells realistic enough for causal interpretation?

- **Proposer's position:** Use within-case observed residual set-points, prohibit range or clipping violations, and apply a frozen nearest-neighbor feature-distance gate to each complete multichannel cell.
- **Critic's position:** Round 3 explicitly required the jointly constructed cells—not merely individual channel edits—to pass a frozen realism gate. No empirical evidence was presented.
- **What evidence would settle it:** A feasibility memo must freeze the realism metric and acceptance rule before inference, then report the full-cell distributions and gate results for both role assignments and sign strata.

### Is a usable surrogate obtainable and demonstrably reliant on the linked channels?

- **Proposer's position:** A representative multichannel surrogate can carry the rung-1 test if it passes frozen predictive-performance and channel-reliance gates.
- **Critic's position:** A weak self-trained surrogate that ignores CBV or MTT cannot test the mechanism, and evidence from one such model cannot be generalized to “the final-infarct model.”
- **What evidence would settle it:** Train or obtain the frozen surrogate, evaluate it on an untouched split, and preregister a manipulation check requiring reliance on at least two identity-linked maps. Replication across model families remains necessary for broader claims.

### Does the rebuilt study remain worth its cost and shortlist position?

- **Proposer's position:** The question, invariant, residual construction, dataset audit, and empirical kill gates remain valuable even though the confirmatory instrument was rebuilt during debate.
- **Critic's position:** The transcript contains no final critic position on the round-three design or its value after the third amendment.
- **What evidence would settle it:** This is partly a portfolio-value judgment rather than a factual disagreement. A feasibility memo can inform it with the 99 GB acquisition burden, eligible-site counts, edit budget, expected GPU cost, and the standalone value of the dataset-composition audit, but the human must decide whether that package merits continued pipeline effort.

## Positions that moved

- **Proposer, round 1:** Conceded that the original projection/tangent contrast overclaimed confidence-map use. This was earned by the critic's counterexample of a residual-blind nonlinear model responding anisotropically to edit direction and placement.
- **Proposer, round 2:** Conceded that matched high-X versus low-X sites leave X observational and cannot exclude nonlinear conditioning on unmatched channels or receptive-field context. This was earned by the critic's demonstration that concordance across MTT- and CBV-matched strata can arise without residual use.
- **Critic, round 3:** Accepted that the round-two within-site manipulation repaired the observational-in-X objection and preserved claim identity. This movement was earned by the switch from cross-site comparison to within-site causal setting of X.
- **Proposer, round 3:** Conceded that a single-channel CBF edit necessarily changes r and invalidates the claimed factorial. This was earned by the critic's direct algebraic demonstration.
- **Proposer, round 3:** Rescoped sign symmetry from both factors to the X-setting factor and excluded plain single-channel CBF sensitivity from the study's answer. This followed from the same algebraic coupling argument.
- No concession was UNEARNED. The critic did not respond after the final amendment, so silence is not recorded as agreement.

## Amendments made

At round zero, the card claimed that residual-removal projection versus equal-energy tangent shams could show that a model uses violation of CBV = CBF x MTT as a hidden confidence map. The revised idea retains that scientific question but replaces the confirmatory instrument.

The current proposed design is a within-site 2x2 manipulation of low versus high signed-residual magnitude and absent versus present identity-consistent perfusion worsening. The evidence edit lowers CBF and compensates through another channel so signed r remains fixed. In arm A, CBV carries X and MTT compensates the evidence edit; in arm B, MTT carries X and CBV compensates it. The design adds voxelwise residual set-point verification, no-crossing of r = 0, compensator-only, zero-dose, and off-site shams, replication across carrier assignments and residual-sign strata, and frozen inventory and full-cell realism gates. Projection/tangent testing survives only as a supporting residual-dependence gate.

What was lost is substantial: the original confirmatory design is abandoned; the simpler matched-site amendment is also abandoned; a plain single-channel CBF edit is no longer answerable within the factorial; sign symmetry has narrower scope; evidence concerns one representative surrogate unless replicated; and even a positive result supports functional X-dependent behavior, not an explicit internal residual computation, calibrated uncertainty, or generalization across model families or perfusion software. The final design is more expensive and may fail because the released residual is algebraically trivial, eligible cells are too scarce, joint edits are unrealistic, or the surrogate ignores the linked channels.

## Recommendation

**REVISE.** The final amendment is a plausible repair, but it has not been challenged or accepted by the critic and has not been incorporated into the idea card. Before deciding, the human should look most closely at an independent algebraic counterexample review of the complete role-disjoint, r-preserving factorial: can any residual-blind multichannel surrogate still pass every proposed carrier, sign, sham, and set-point gate?

## In plain terms

This idea asks whether a stroke-prediction model treats disagreement among three related blood-flow maps as a warning that the maps are unreliable. It would test whether the model reacts less to an otherwise comparable, physically consistent worsening of blood flow when that disagreement is deliberately made larger.

The debate found that the original test could not answer this question, and two successive repairs also had causal flaws. A third repair now keeps the disagreement fixed while changing the blood-flow evidence, but the critic never reviewed that final construction and the required dataset and realism checks have not been run. The human is being asked to judge whether this rebuilt experiment is identifiable enough to justify a full revision and feasibility audit.

```json
{"verdict": "REVISE", "unblock": "Independently review the complete role-disjoint, r-preserving factorial for residual-blind counterexamples, then rewrite the card with the accepted design and preregistered Stage 0 algebra, inventory, realism, surrogate-reliance, and resource gates."}
```
