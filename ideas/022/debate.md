# Debate transcript

## Round 1 — CRITIC

**Position:** The original model-use question is presently untestable because no obtainable, performant frozen ISLES'24 final-infarct model consumes raw 4D CTP with documented training-supported prefix semantics.

**Argument:** The published ISLES'24 winner cannot be the study object: Ren et al. (arXiv:2505.18424v2, Table 1) report CTA, CBF, CBV, MTT, and Tmax inputs to the final nnU-Net, not raw CTP. The closest public raw-CTP system, Amador et al. (DOI 10.1007/978-3-031-81101-2_9; `kimberly-amador/ISLES24-PrediCTP`), releases code but no frozen checkpoint and reports Dice 0.20 and lesion-wise F1 0.02. Retraining that recipe is not a repair: it changes the original audit of a model that has already learned useful benchmark signal into a study of a model whose response to prefixes is partly installed by the experimenter's own padding, masking, or temporal-dropout choices. That is a different deliverable sentence under the claim-identity rule and would require a successor candidate. Without the frozen artifact, the nested-prefix design cannot distinguish learned use of terminal incompleteness from an out-of-distribution tensor convention, the same unresolved intervention-validity failure that paused idea 006.

**What would change my mind:** Produce an obtainable frozen raw-4D-CTP final-infarct checkpoint with non-trivial held-out performance, plus its actual training loader or methods showing that the proposed shorter-prefix mask/padding representation occurred during training; then the existing nested-prefix experiment could test the original claim without retraining or changing its identity.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The study object does not exist as an obtainable artifact — no frozen, performant ISLES'24 final-infarct model consumes raw 4D CTP with training-supported prefix semantics, and every substitute (audit the derived-map winner, retrain PrediCTP, train my own) either collapses the novelty delta into known truncation-propagation results or installs the very prefix semantics the experiment is supposed to measure, changing the deliverable sentence.

**Response:** CONCEDE

**Argument:** The objection is correct, and I verified it independently rather than taking it on trust before conceding. (1) The `kimberly-amador/ISLES24-PrediCTP` repository, inspected 2026-08-17, has an empty Releases section, no pretrained weights or download link anywhere in the README, and no mention of temporal padding, masking, or variable-length input handling — so even the weak candidate model fails both the frozen-artifact clause and the documented-prefix-semantics clause. (2) A sweep for any other obtainable raw-4D-CTP infarct checkpoint (Hugging Face, Zenodo, challenge releases) found none. The nearest lineage — Robben et al., Med Image Anal 2020 (native-CTP final-infarct prediction, arXiv:1812.02496) and the Amador spatio-temporal CNN line (DOI 10.1016/j.media.2022.102610) — trained on MR CLEAN and single-center cohorts with no released weights, and using a non-ISLES model would in any case change the deliverable sentence, which names an ISLES'24 benchmark model. (3) The retraining path fails the identity check exactly as the critic argues: whether short prefixes are in-distribution would be decided by my own augmentation choices, so the experiment would measure a property I installed. That is the idea-006 intervention-validity failure with the additional defect that here I would be the one who created the distribution. I have no amendment that preserves the question: the design's identifying power comes from auditing a model that already learned benchmark signal, and no such model is obtainable. PAUSE is the right disposition, with the critique's unblock condition standing (a released performant raw-CTP checkpoint with documented temporal-input semantics, via future challenge release or author correspondence with the PrediCTP group). The nested-prefix design itself is sound and should be reused verbatim on unpause, not redrafted.

**Spin-off (already recorded in critique.md, endorsed here, no new idea introduced):** the dataset-side censoring–severity audit — does terminal completeness correlate with infarct volume and center across the 149 released cases — is model-free, resolves keystone clause (a) as a by-product, and if positive gives a concrete reason to pursue the checkpoint through correspondence. It should register as a separate candidate with parent_ids [idea-022] under the claim-identity rule.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The proposer’s evidence resolves the dispute: idea 022 should remain paused because its original model-use question has no obtainable study object, and the proposed dataset audit is correctly separated as a successor rather than treated as a repair.

**Argument:** The independent repository inspection and artifact sweep substantiate, rather than merely restate, the round-1 objection: the only public ISLES’24 raw-4D-CTP implementation has no frozen checkpoint or documented training-supported prefix representation, while the published winning model consumes derived CTA/perfusion maps instead of the raw temporal series. The proposer also passes the identity check by rejecting retraining and by recognizing that the model-free censoring–severity audit has a different estimand. No amendment to idea 022 remains to assess, and raising the duration census or weak-model issue as a new objection would not change the already-agreed disposition.

**What would change my mind:** The agreed unblock evidence: an obtainable frozen raw-4D-CTP final-infarct checkpoint with non-trivial held-out performance and inspectable training-time temporal masking or padding semantics that support the nested-prefix intervention.

**Status:** CONVERGED

## Round 2 — PROPOSER

**Responding to:** The critic's closing position that the round-1 concession is substantiated, no amendment remains to assess, and the dataset-side audit is correctly a successor rather than a repair.

**Response:** CONCEDE

**Argument:** The round-1 concession stands unchanged and I have nothing new to add — no fresh evidence has surfaced that would alter it, and per the debate rules restating settled agreement is not a contribution. Three closing precisions for the record rather than for dispute. (1) Disposition: PAUSE with the kill-pattern named as DATA_ACCESS (the idea-003/idea-018 shape), per the critique's correction of the card's own `dies_like_prior`. (2) The unblock condition is exactly the critic's round-1 "what would change my mind" clause: an obtainable frozen raw-4D-CTP final-infarct checkpoint with non-trivial held-out performance *and* inspectable training-time temporal masking or padding semantics — both clauses required, since a checkpoint without documented prefix semantics reproduces the idea-006 intervention-validity failure on unpause. (3) On unpause the nested-prefix design (censor–extrapolate rescue, equal-count interior-frame masking, positive-control temporal shift) is reused verbatim, not redrafted; only the keystone re-inspection and the duration census (which the endorsed spin-off resolves as a by-product if it runs first) precede execution. The censoring–severity audit registers separately with parent_ids [idea-022] through the normal scouting path, not by manual insertion — consistent with the 2026-08-10 claim-identity and revival-machinery decisions.

**Status:** CONVERGED
