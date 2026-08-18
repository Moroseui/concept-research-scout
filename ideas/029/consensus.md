# Debate summary — idea 029

## Agreed

- In round 1, both sides agreed that the available DeepISLES rerun is a contemporary surrogate, not the recoverable historical pre-correction draft. Its disagreement with the released ground truth mixes possible human edits with model-version, input-channel, resampling, thresholding, postprocessing, and registration-path differences.
- In round 1, both sides agreed that `D xor G` therefore cannot identify the expert-overridden voxels or measure an “uncorrected fraction.” The stage-2 analysis would condition on the wrong estimand rather than merely suffer reduced power.
- In round 1, both sides agreed that the proposed external-model control does not isolate exposure to ISLES'24 labels because it also changes label protocol, cohort, treatment mix, preprocessing, architecture, and inductive bias.
- In round 1, both sides agreed that the inheritance-by-generalization mechanism is coherent in principle but is not identifiable with the obtainable artifacts and controls.
- In round 1, both sides agreed that a version-pinned surrogate-versus-ground-truth agreement census is a different descriptive question. It cannot repair the original claim under the claim-identity rule and is, at most, a data note.
- By round 2, both sides agreed that the original candidate should be rejected for `IDENTIFIABILITY_FAILURE`. A direct audit using archived pre-correction masks would be a separate, data-access-gated candidate with no inherited queue position.

## Unresolved

There is no live disagreement between proposer and critic about the present candidate.

One factual condition remains unresolved outside the debate: whether the exact archived pre-correction masks and their generation provenance can be obtained. The proposer and critic both hold that these artifacts are necessary to identify actual supervised edits. Evidence that would settle this is release or verified access from the dataset organizers to the archived masks and exact provenance, followed—if the inheritance claim is revived—by a frozen comparison that varies training-label exposure while holding acute inputs, cases, architecture, preprocessing, and operating point fixed.

## Positions that moved

- The proposer conceded in round 1 in response to the critic's two-part argument: the surrogate rerun does not recover the historical draft or correction set, and the external-model comparison cannot isolate inheritance through label exposure. This was an earned concession because the proposer restated and extended the causal and estimand consequences rather than merely capitulating.
- In round 2, the proposer reaffirmed the existing concession after the critic confirmed the shared diagnosis and disposition. No new position moved, so this is not recorded as a separate concession and is not flagged `UNEARNED`.

## Amendments made

No amendment preserves the candidate's identity. At round zero, the idea claimed that a rerun of released DeepISLES could recover a correction field, estimate surviving machine-drafted content, and test whether an acute-CT model inherited draft conventions through ISLES'24 labels. After debate, those claims are withdrawn because neither the historical draft nor the overridden-voxel set is observable from released artifacts, and no proposed control isolates label exposure.

What survives is a separate possible question: using exact archived pre-correction masks, characterize supervised edits and measure their effects on official model scores and rankings. The model-inheritance claim is lost unless an additional controlled label-exposure design becomes possible. A present-day surrogate agreement census is demoted to a possible data note, not a replacement candidate.

## Recommendation

**REJECT.** The single most important thing for the human to inspect before deciding is whether the exact archived pre-correction masks and generation provenance are actually obtainable. Their availability could justify a separate benchmark-audit candidate or a formally justified revival, but it does not rescue this card as written.

## In plain terms

This idea asks whether stroke models learn quirks from the algorithm that first drafted the benchmark's lesion masks. It proposes recreating those drafts and checking whether trained models repeat their boundary habits.

The debate concluded that the released software cannot recreate the exact historical drafts: differences from the official masks could come from software versions, missing inputs, resampling, or human edits. The proposed comparison model also changes too many things at once to show that label exposure caused any shared behavior, so the current experiment cannot answer the question.

The human is being asked to check whether the organizers can provide the exact original draft masks and how they were generated; if so, that supports a separate, better-controlled study.

```json
{"verdict": "KILL", "kill_code": "IDENTIFIABILITY_FAILURE", "unblock": "Obtain the exact archived pre-correction masks and generation provenance, then use a frozen design that isolates training-label exposure while holding acute inputs, cases, architecture, preprocessing, and operating point fixed."}
```
