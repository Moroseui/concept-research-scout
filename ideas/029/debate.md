# Debate transcript

## Round 1 — CRITIC

**Position:** The released artifacts cannot recover the historical pre-correction draft, so the proposed surrogate-rerun experiment does not identify the original claim that an acute-CT model inherited DeepISLES conventions through the ISLES'24 labels.

**Argument:** The official paper establishes only that the masks were derived using the ISLES'22 ensemble and corrected when needed; it does not release the historical draft masks or specify the exact weights, commit, input channels, native-space preprocessing, thresholding, postprocessing, or registration path. The available rerun necessarily uses a later released implementation/weights and already resampled `space-ncct` DWI/ADC, without the possibly used FLAIR. Thus its output D is a related contemporary surrogate, not the historical draft, and D xor G cannot be called a correction field or used to estimate an "uncorrected fraction." More decisively, at voxels where D and released ground truth G disagree, an ISLES'24-trained model was supervised toward G, not D; prediction agreement with D there can arise from shared segmentation priors, acute-CT predictability, calibration, or thresholding, but cannot demonstrate inheritance of D through the labels. An external model trained on another cohort does not isolate label exposure because label protocol, cohort, treatment, preprocessing, and inductive bias all change together. Narrowing the study to version-pinned D-versus-G agreement would be feasible, but it answers a different descriptive reproducibility question and therefore fails the required identity check; it should be a separate candidate, not a repair of this claim.

**What would change my mind:** Release of the exact archived pre-correction masks and generation provenance, followed by a frozen held-out design that compares models differing in exposure to draft-derived versus independently produced labels while holding architecture, acute inputs, cohort, preprocessing, and operating point fixed; absent that, the original inheritance claim is not identifiable.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The released artifacts cannot reconstruct the historical pre-correction draft, so the surrogate rerun D neither measures an "uncorrected fraction" nor defines the set of expert-overridden voxels; and even at genuine disagreement voxels, no available comparison isolates inheritance-through-labels from shared segmentation priors, so the original claim is not identifiable with obtainable data.

**Response:** CONCEDE

**Argument:** The critic is correct, and I concede in round one rather than defend across rounds.

One clarification for the record, offered as context and not as a rebuttal: the card's stage-2 mechanism was never "the model fits D at D-G voxels." It was inheritance by generalization — conventions absorbed from the bulk of uncorrected labels bleeding into the corrected regions, where siding with D against the supervised target G would be the observable trace. That mechanism is coherent. But conceding it is coherent does not make it identifiable here, and the critic's argument kills the design at an earlier joint than the causal one:

1. **The conditioning set itself is unidentified.** The entire stage-2 analysis is defined on "expert-overridden voxels," operationalized as D xor G. Without the historical draft, that set irreducibly mixes true corrections with version drift, resampling into `space-ncct`, the FLAIR-path uncertainty, and thresholding differences. My own keystone screen (§4) documented the drift sources and called the statistic a "lower bound"; the critic is right that this concession is fatal rather than conservative, because the *asymmetric interpretation* defense only protects the stage-1 agreement number — it cannot protect an analysis that must *condition on* correction status voxelwise. An analysis restricted to a contaminated set does not degrade gracefully; it changes estimand.

2. **Even on a clean disagreement set, no obtainable control isolates label exposure.** The external never-trained-on-ISLES'24 model was the card's discriminator for shared inductive bias, and the critic is right that it confounds label protocol, cohort, treatment mix, preprocessing, and architecture simultaneously. I have no candidate model that differs from the subject model in label exposure alone, and I cannot construct one without the historical draft (which would itself enable the better study directly).

3. **The identity check forbids the salvage.** The surviving computable study — version-pinned DeepISLES-versus-G agreement, stratified and honestly labeled as surrogate reproducibility — is worth something as a data note, but it does not answer "is a trained model using inherited draft conventions?" Under the claim-identity rule (decision ledger, 2026-08-15), that is a different deliverable sentence, so it must not be filed as an amendment of this card.

What was lost: the genuinely valuable question — how much machine-drafted content survives in a hybrid-annotated public benchmark, and whether it propagates into trained models — is real and, to my knowledge after bounded search, unanswered for ISLES'24. It is paused by data access, not answered in the negative.

**Spin-off** (already identified in critique §8, registered as a separate candidate, not a repair): if the organizers release the archived pre-correction masks and exact generation provenance, quantify which voxels and lesions supervised review changed, characterize edit types, and measure how official metrics and method rankings shift when the reference is draft versus corrected mask. That study needs no acute-CT model, no surrogate rerun, and no unidentifiable conditioning set. Its gate is a data-access request to the organizers, which costs one email and should be made.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The proposer has accepted the fatal identifiability failure and correctly determined that the feasible surrogate-agreement study fails the identity check, so the original candidate should be rejected rather than amended.

**Argument:** The proposer's response resolves the objection through substantive argument: it recognizes that `D xor G` cannot identify expert-overridden voxels because the available `D` mixes historical correction with model-version, input-channel, resampling, thresholding, and postprocessing differences; it also recognizes that the proposed external-model comparison changes label protocol, cohort, treatment mix, preprocessing, and architecture rather than isolating exposure to ISLES'24 labels. Most importantly, the proposer applies the claim-identity rule correctly: a version-pinned census of agreement between a contemporary DeepISLES rerun and the released mask is a descriptive reproducibility study, not a test of whether an acute-CT model inherited draft conventions through the labels. No amendment preserving the obtainable data repairs the original deliverable sentence. The proposed archived-draft benchmark audit is therefore a separate, data-access-gated candidate and cannot rescue this card.

**What would change my mind:** The exact archived pre-correction masks and generation provenance, plus a design that holds acute inputs, cases, architecture, preprocessing, and operating point fixed while varying training-label exposure between draft-derived and independently produced labels; that evidence is not currently available and would support reconsideration through a new candidate or a formally justified revival.

**Status:** CONVERGED

## Round 2 — PROPOSER

**Responding to:** The critic's confirmation that the round-1 concession is complete and correctly applied — the surrogate-agreement study fails the identity check, no amendment on obtainable data repairs the deliverable sentence, and the candidate should be rejected rather than amended, with the archived-draft audit registered separately.

**Response:** CONCEDE

**Argument:** The concession stands as given; I have no new argument and will not manufacture one. The debate is closed on the shared position: idea 029 is rejected for identifiability failure — the conditioning set (expert-overridden voxels) is not recoverable from released artifacts, and no obtainable control isolates label exposure. Nothing in the critic's round 2 requires further response; we agree on both the diagnosis and the disposition.

Two disposition items for the record, so the close is actionable and not merely terminal:

1. **Kill classification.** This should enter the ledger as IDENTIFIABILITY_FAILURE, the third such kill in this charter (after ideas 020 and 028). The pattern worth flagging for future scouting cycles: all three died because a construct named in the deliverable sentence (spreading front, oxygen gauge, correction field) was not observable from the released data — the keystone screen verified that *something* was computable without verifying it was *the thing the claim needed*. That is the same wrong-keystone failure mode recorded three times in the other charter (ideas 005, 006, 007). Keystone screens should ask not only "can X be computed?" but "is the computed X the estimand the deliverable sentence names?"

2. **Spin-off handling, per the claim-identity rule (decision ledger, 2026-08-15) and the S2 precedent (2026-08-10).** The archived-draft benchmark audit — which edits did supervised review make, and how do official metrics and rankings shift under draft-versus-corrected reference — enters, if at all, through a normal scouting cycle or librarian proposal with `parent_ids: ["isles24-scout-004-c01"]`, not by manual registration, and takes no inherited queue position. Its gate is data access: the organizers hold the archived pre-correction masks and exact generation provenance, and the request costs one email. That request is worth making regardless of whether the spin-off is ever scouted, because both this debate's reopening condition and the critic's stated change-of-mind condition depend on it. The stage-1 surrogate census is not worth registering as a standalone candidate: high agreement is expected and unsurprising, low agreement is confounded by documented execution-path drift — at most a data note.

**Status:** CONVERGED
