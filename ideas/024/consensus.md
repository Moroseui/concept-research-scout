# Debate summary — idea 024

## Agreed

- In round 1, both sides agreed that the proposed controls can isolate, at most, dispersion in observed tissue curves. With one global arterial input function and no local arterial sampling or vascular-model inputs, they cannot distinguish collateral-path or other macrovascular bolus dispersion from capillary transit-time variance.
- In round 1, both sides agreed that delay-insensitive deconvolution addresses arrival delay but does not remove the macrovascular-dispersion alternative. The original physician-facing sentence therefore cannot be supported on ISLES'24.
- In rounds 1–2, both sides agreed that renaming X to “transit-time dispersion in the tissue curves” would change the deliverable sentence and must be treated as a successor rather than an in-place repair.
- In rounds 1–2, both sides accepted two additional independent failures from the inspected critique record: no raw-CTP ISLES'24 team released a trained checkpoint suitable for the frozen-model experiment, and the proposed nonparametric residue-variance instrument is not a construct-valid CT measurement of CTH.
- In rounds 1–2, both sides agreed that cross-AIF and cross-regularizer stability would test reliability, not construct validity; a stable-but-invalid estimate could pass the proposed Stage-0 gate.
- In rounds 1–2, both sides agreed that no spin-off should be registered here because the defensible released-model territory is already represented by ideas 021 and 023.
- In round 2, both sides converged on rejection and on the same three-part reopening condition: a valid way to separate macrovascular dispersion from capillary transit-time variance, an obtainable performant raw-CTP model, and a selective intervention that changes the latter while holding the former fixed through the final input tensor.

## Unresolved

None. The factual and disposition questions raised in the debate were resolved by agreement. The required reopening evidence remains unavailable, but the parties do not disagree about what evidence would be needed.

## Positions that moved

- The proposer conceded in round 1 after the critic showed that macrovascular and collateral-path dispersion produces the same curve broadening as the claimed microvascular CTH signal, and that the available data lack the vascular information needed to separate them. This was an earned concession to a specific identifiability argument.
- The proposer also accepted in round 1 the critique's independently inspected checkpoint-access and measurement-validity failures. These were supported by the cited repository and primary-source findings, not unearned capitulation.
- The critic conceded the debate in round 2 because the proposer had accepted the decisive objection and its claim-identity consequence. This marked convergence, not withdrawal of the critic's objection.
- The proposer's round-2 response introduced no new concession; it reaffirmed the round-1 position and supplied a ledger-oriented classification. It is not an unearned concession.

## Amendments made

No amendment was adopted. Round zero claimed that a raw-CTP final-infarct model uses capillary transit-time heterogeneity in microvascular passage. The only technically defensible narrowing discussed—use of generic tissue-curve dispersion—would lose the capillary and microvascular attribution and therefore change X and the deliverable sentence. Both sides treated that as a different candidate, not a revision of Idea 024.

The debate also corrected the operative keystone: temporal coverage was only the nearest checkable fact. The load-bearing prerequisites were an obtainable performant raw-CTP checkpoint and a construct-valid CTP instrument for CTH; both were inspected and adverse.

## Recommendation

REJECT. The primary ledger classification is `DATA_ACCESS`: the frozen raw-CTP model required by the specified experiment is not obtainable, and producing a suitable model falls outside the stated compute design. This is compounded by `IDENTIFIABILITY_FAILURE` and an instrument-validity failure not separately represented in the current taxonomy.

Before deciding, the human should look most closely at whether all three reopening conditions can jointly be met—not merely whether raw CTP exists: an obtainable performant raw-CTP checkpoint, a validated measurement or paired acquisition that separates upstream macrovascular dispersion from capillary transit-time variance in LVO, and a selective final-input intervention that changes only the latter.

```json
{"verdict": "KILL", "kill_code": "DATA_ACCESS", "unblock": "Reopen only if an obtainable performant raw-CTP model, a validated LVO measurement separating macrovascular dispersion from capillary transit-time variance, and a selective final-input intervention are all available."}
```
