# Debate summary — idea 023

## Agreed

- The original card named an executability fact as its keystone when the load-bearing interpretability fact is whether final-infarct labels contain a compensation-state signal at matched CBF. In round 2 the critic explicitly accepted the proposer's round-1 repair: K2 becomes the real, `NOT_INSPECTED` keystone; a frozen, patient-clustered outcome census precedes model work; feasibility is capped at 3; and both salvageability wording and a decisive toggle null are conditional on that census passing.
- The model-free census must assess adequate within-patient joint support, precision and directional consistency across matched-rCBF strata, and account for released reperfusion or treatment variables where available. Cases used to estimate the label relationship must be separated from the later toggle-evaluation cases. Both sides accepted this in rounds 1–2.
- A compensated-to-collapsed joint CBV/MTT edit cannot distinguish an autoregulatory-reserve reader from a generic monotone low-CBV reader: both predict the same sign. It can distinguish either from a model that ignores the state, and it gives the opposite prediction from a monotone long-MTT severity reader. The proposer conceded this in round 2, and the critic accepted that concession in round 3.
- When the released maps obey the central-volume identity, CBV and MTT at fixed CBF are one degree of freedom. The study therefore cannot attribute an effect to the CBV channel rather than the MTT channel. Both sides accepted an explicit prohibited conclusion to that effect in rounds 2–3.
- An above-mirror arm needs native empirical support, separate in-distribution checks, physiologic-range bounds, and a prespecified response-shape analysis. If that support gate fails, the current candidate must pause rather than silently narrow to a joint-channel-state claim; that weaker deliverable would be a successor. This was proposed in round 2 and accepted by the critic in round 3.
- Mirror-normal CBV is a reference, not an established physiological ceiling. A kink fixed at `rCBV_mirror = 1` cannot identify reserve use. The proposer conceded this in round 3 and replaced the assumed boundary with a proposed outcome-estimated change point.
- The claim is about a joint compensation state, not whether autoregulatory dilation or collateral inflow produced it. Scanner, site, protocol, positioning, and global injection or cardiac-output scaling are addressed principally by within-case edits and mirror ratios; label provenance is not the dominant failure mode here.
- The queueing/control-engineering analogy is not necessary to the experiment. The measurable mechanism survives in classical autoregulatory and central-volume terminology; the revision should remove decorative Little's-law language rather than treat it as evidence.

## Unresolved

### Does an outcome-derived change point identify autoregulatory reserve rather than a learned nonlinear map pattern?

- **Question:** If a change point in final-infarct risk versus `rCBV_mirror` is estimated in matched-rCBF strata and the model's edited response changes near the same point, is that sufficient to call the model-used signal “autoregulatory blood-volume reserve”?
- **Proposer's position:** Yes, conditionally. Round 3 replaces the assumed kink at 1 with a frozen, patient-clustered G-shape analysis comparing a change-point model with flexible monotone alternatives. The model probe would then test agreement in response shape and change-point location on held-out cases. A construct reader should break near the outcome-derived point, a density/calibration artifact near the support boundary, and a monotone reader nowhere. If the outcome change point and support boundary are inseparable, the study exits as indeterminate.
- **Critic's position:** The last stated critic position, before this amendment, is that neither flattening nor continuation uniquely identifies reserve without independent evidence for the physiological response shape. The critic allowed an outcome-derived shape as one possible repair, but did not respond to the proposer's implementation. It therefore remains unresolved whether same-cohort outcome anchoring satisfies the critic or merely shows that the model learned a nonlinear relationship present in its training target.
- **Evidence that would settle it:** First, a frozen Stage 0 result showing a precise, patient-clustered outcome change point at matched CBF, adequate support on both sides, separation from the empirical support edge, and robustness to available reperfusion/treatment variables. Second, critic or human review must decide whether that cohort-outcome landmark is an independently justified physiological endpoint or only a label-distribution feature. Stronger settlement would come from primary-source or independent-cohort replication of the same shape, or from a separately measured autoregulatory endpoint. If the program requires physiology independent of the training labels, no same-cohort analysis alone can settle it.

### Is the revised deliverable still the same claim?

- **Question:** Does redefining “reserve” as a cohort-specific, outcome-supported ceiling preserve the original deliverable sentence, or cross the claim-identity boundary?
- **Proposer's position:** It preserves identity because the question and sentence remain about blood-volume reserve read against CBF; only an assumed boundary has been replaced by a measured one. The proposer nevertheless acknowledges that the claim is now cohort-anchored rather than universal.
- **Critic's position:** In round 3 the critic said an externally or independently supported outcome/autoregulatory shape could preserve the original question, but did not assess the final same-cohort amendment. Earlier rounds agreed that adding the label gate and a valid saturation discriminator did not itself change identity.
- **Evidence that would settle it:** This is principally a governance judgment, not an empirical fact. The human must decide whether “autoregulatory reserve” may be operationalized by the training cohort's outcome curve. Independent physiological validation would reduce the judgment call but cannot eliminate the need to apply the claim-identity rule.

### Are the necessary Stage 0 conditions present in ISLES'24?

- **Question:** Do the 149 cases provide adequate within-patient matched-rCBF support, an estimable outcome shape, native above-mirror coverage away from the support boundary, usable mirror geometry, compatible grids, and clinical covariates sufficient for the intended interpretation?
- **Proposer's position:** These are measurable CPU-first gates, not assumptions. Failure of G-label, G-hyper, or G-shape pauses this candidate; coincidence of the outcome change point with the support boundary yields an indeterminate exit.
- **Critic's position:** These facts must be directly established before model training or a decisive-negative interpretation. The critic has not accepted any of them as presently true.
- **Evidence that would settle it:** A version- and hash-pinned header/schema census followed by the preregistered patient-clustered Stage 0 analyses, with minimum-support and precision criteria fixed before inspecting outcomes. This evidence does not yet exist in the debate record.

### Whose model can support the eventual wording?

- **Question:** Can the study speak about benchmark models if it probes only a self-trained map-input nnU-Net?
- **Proposer's position:** The proposed machinery assumes a self-trained model, with a Stage 0 inventory for any released challenge weights and maps-only plus multimodal configurations.
- **Critic's position:** Claims and negatives must be scoped to the actual trained model family and recipe unless a released submission is found; multimodal dominance can make a weak toggle response ambiguous.
- **Evidence that would settle it:** An inspected inventory of participant repositories and weights, a frozen input-channel specification, and successful reproduction of the intended model family. Without released challenge weights, only model-family-scoped language is supportable.

## Positions that moved

- **Proposer, round 1:** Conceded that the stated co-registration keystone was adjacent rather than load-bearing. This moved in response to the critic's argument that label-outcome structure gates both salvageability interpretation and negative-result decisiveness. The proposer adopted K2, G-label, split separation, conditional negative interpretation, and the feasibility cap. Earned concession.
- **Critic, round 2:** Accepted the round-1 keystone repair and the claim-identity rationale. This moved because the proposer supplied concrete gates, scoring changes, and failure consequences. Earned concession.
- **Proposer, round 2:** Conceded that the bidirectional basic toggle does not distinguish reserve from monotone CBV use and that CBV-versus-MTT channel attribution is impossible under the identity. This moved in response to the critic's explicit sign analysis. The proposer added G-hyper, a confirmatory above-mirror arm, prohibited conclusions, and reduced identifiability to 3 pending the gate. Earned concession.
- **Critic, round 3:** Accepted the channel-degeneracy limit, confirmatory status of the above-mirror arm, and pause/successor consequence if G-hyper fails. This moved because the proposer made those constraints explicit. Earned concession.
- **Proposer, round 3:** Conceded that a kink at mirror-normal had been assumed rather than measured. This moved in response to the critic's demonstration that true reserve use may continue above 1 and generic nonlinear channel use may flatten there. The proposer replaced it with G-shape and a shape/location comparison. Earned concession.
- No concession in the transcript is UNEARNED. The final round-3 amendment remains unaccepted because the critic had no subsequent turn; it must not be recorded as consensus.

## Amendments made

At round zero, the card claimed that a two-sided, mirror-referenced, manifold-preserving CBV/MTT toggle at fixed CBF could identify use of autoregulatory reserve; treated map co-registration as the inspected keystone; fixed compensation at mirror-normal; described a gated null as decisive; attributed the finding broadly to benchmark models; and presented the experiment as cheap and near-ready.

The debated version instead proposes:

- K2, not map coexistence, as the load-bearing `NOT_INSPECTED` keystone: outcome must encode a compensation-state relationship at matched CBF.
- A frozen CPU-first G-label/G-shape census with patient clustering, joint-support and precision requirements, treatment/reperfusion handling where possible, and separation from held-out toggle cases.
- A continuous outcome-response model that estimates any change point rather than assuming one at `rCBV_mirror = 1`.
- G-hyper and separate in-distribution validity for above-mirror edits, plus an explicit indeterminacy exit when the outcome landmark and support boundary cannot be separated.
- A confirmatory model response-shape/location comparison, with the slope contrast secondary, rather than treating the sign of the basic toggle as construct-specific.
- Explicit prohibition of CBV-versus-MTT channel attribution and model-family-scoped wording unless released challenge weights are found.
- Removal of the Little's-law/control analogy from the evidentiary logic.

What was lost is substantial: feasibility and identifiability fall to 3 pending unrun gates; decisive-negative value is conditional; the simple two-sided toggle no longer identifies the construct; the claim becomes cohort-anchored; at least three Stage 0 death paths and one indeterminacy exit now precede the full probe; the cheapest-candidate claim no longer holds; and a failure may require a separately registered weaker successor. The current `idea_card.json` contains none of these amendments and is materially stale.

## Recommendation

**REVISE.** Rewrite the card to the fully gated, cohort-anchored design before any feasibility memo or model work. The single most important thing for the human to examine is whether matching a model's edit-response change point to a change point estimated from its own training cohort's outcomes is sufficient evidence for the physician-legible phrase “autoregulatory blood-volume reserve,” or whether independent physiological validation is required. That decision controls both claim identity and whether G-shape can ever reach rung 3.

```json
{"verdict": "REVISE", "unblock": "Rewrite the card with K2, G-label/G-shape, G-hyper, support-boundary indeterminacy, channel-attribution limits, and model-family scope, then obtain human agreement that the outcome-derived shape can validly operationalize autoregulatory reserve before Stage 0."}
```
