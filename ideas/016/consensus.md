# Debate summary — idea 016

## Agreed

- The original claim is mechanistic: the model uses IVC/hepatic-vein contrast reflux as a sign of elevated right-sided pressure, not merely that its output responds to reflux-shaped voxels (Round 1, proposer concession; Round 2, critic confirmation).
- RSNA-STR cannot identify that mechanism. Injection rate can independently produce the same reflux appearance, while the dataset provides neither recoverable injection/timing fields nor repeat scans that could hold protocol fixed (Round 1, proposer concession; Round 2, critic confirmation).
- Reflux extent or morphology does not rescue identification because both pathological pressure and injection protocol affect the same observable. The RV/LV label is also not an independent pressure anchor because it is a co-caused chamber-geometry measurement (Round 1, proposer; Round 2, critic).
- A sham-controlled reflux-inpainting experiment could establish only the narrower rung-1 claim that a strain model responds specifically to retrograde venous contrast. It cannot establish that the model treats reflux as a pressure gauge and must therefore be a separate candidate with fresh scores and feasibility gates (Round 1, proposer concession; Round 2, both sides).
- Idea 016 should be rejected on RSNA-STR rather than advanced under the weaker voxel-reliance formulation. The broader pressure-gauge question remains revivable on a different, suitable cohort (Round 2, both sides).

## Unresolved

There is no remaining disagreement between proposer and critic.

The open empirical question is whether a suitable alternative cohort exists. Both sides require a directly inspected CTPA cohort with per-scan injection rate, saline-chaser, and scan-delay metadata; an independent right-sided-pressure or tricuspid-regurgitant-velocity measurement; sufficient reflux variation within a fixed-protocol design; and a runnable frozen strain model. Direct inspection of such a cohort's files, schema, and methods would settle whether the original question can be revived. It would not make RSNA-STR suitable.

## Positions that moved

- The proposer conceded in Round 1 after the critic argued that injection protocol and pathological back-pressure are observationally inseparable in the proposed RSNA-STR design, and that a voxel-inpainting result would answer a different question. This was an earned concession: the proposer tested and rejected three possible rescues—reflux extent, the RV/LV label as an anchor, and within-subject variation—using specific identification arguments.
- The critic conceded in Round 2 that the proposer's revised disposition fully addressed the objection: reject the original claim on RSNA-STR, separate the weaker inpainting experiment, and define evidence-based revival conditions. This was earned by the proposer's explicit analysis rather than by unsupported capitulation.
- The proposer's Round 2 concession merely affirmed the already converged position and clarified its ledger treatment. It introduced no new substantive movement and is not an unearned concession.

## Amendments made

At round zero, Idea 016 claimed that an RSNA-STR pulmonary-embolism model might use IVC/hepatic-vein reflux as a hydraulic gauge of elevated right-sided pressure, with reflux-direction erasure proposed as a path toward that claim.

After debate, that claim is withdrawn for RSNA-STR. The idea is not amended into a weaker rung-1 study because doing so would remove the defining pressure mechanism and materially reduce its interest and mechanism-clarity basis. Two separate future candidates were identified instead:

1. A sham-controlled image-space inpainting study asking only whether a frozen RV/LV-strain output depends on retrograde venous contrast, with no pressure interpretation and with new scores and Stage-0 gates.
2. A resurrection of the original pressure-gauge question only if a different cohort supplies injection-protocol metadata, an independent pressure or TR-velocity readout, fixed-protocol variation, and a runnable frozen model.

What was lost is the central deliverable sentence on the named dataset: RSNA-STR cannot support the claim that the model uses reflux *as a sign of elevated right-sided pressure*.

## Recommendation

REJECT Idea 016 on RSNA-STR. The single most important thing for the human to examine before reconsidering the broader question is whether a directly inspected alternative CTPA cohort jointly contains complete per-scan injection/timing metadata and an independent right-sided-pressure or TR-velocity measurement under enough fixed-protocol variation to identify physiology separately from the power-injector effect.

```json
{"verdict": "KILL", "kill_code": "IDENTIFIABILITY_FAILURE", "unblock": "Locate and directly inspect a CTPA cohort with per-scan injection protocol metadata, an independent pressure or TR-velocity readout, fixed-protocol reflux variation, and a runnable frozen strain model."}
```
