# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed NPS-residual transplant does not isolate an acquisition-site noise fingerprint, so even a positive model response cannot support the original deliverable sentence.

**Argument:** In CT, the measured residual and noise-power spectrum jointly vary with reconstruction kernel, dose, interpolation, object size and position, reconstruction method, and denoiser error; residual fine anatomy and preprocessing correlations can also survive. Mackin et al. directly measured strong reconstruction-kernel effects on NPS and texture (DOI 10.1002/mp.14208), while the cited scanner-forensics precedent used only eight 3D images from different scanners, leaving patient, protocol, and scanner bundled (Kharboutly et al., DOI 10.1109/EUVIP.2014.7018385). ISLES'24 supplies neither paired acquisitions that hold anatomy and protocol fixed across devices nor a validated noise-transfer generator. Therefore, a classifier flip, matched total energy, monotone blend response, and spectrally neutral sham would show sensitivity to this particular synthetic operator, not use of a physical site fingerprint. Recasting the result as “the model responds to NPS remapping” fails the mandatory identity check: it no longer answers whether the model uses scanner-specific noise as a site prior and must be a separate candidate. The proposed site-stratified out-of-fold performance audit is likewise a defensible successor, not a repair, because it tests cross-center performance rather than the claimed mechanism.

**What would change my mind:** Show primary validation on repeated phantom, traveling-subject, or paired-reconstruction acquisitions demonstrating that the exact transfer operator changes independently recoverable device/site noise identity while preserving anatomy, resolution, dose/kernel information, and all other model-readable evidence, then apply that frozen operator to a competent, frozen ISLES'24 final-infarct model with a prespecified spatial output endpoint.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card's key inference — classifier-flipping, energy-matched spectral reshaping plus a neutral sham implies that only the site noise fingerprint changed, so any model response demonstrates use of that fingerprint — has an unestablished middle term. Within ISLES'24 there is no paired acquisition, phantom, or traveling-subject data that could validate the transfer operator, so a positive response shows sensitivity to this synthetic operator, not use of a physical site fingerprint; and the honest recast ("the model responds to NPS remapping") is a different deliverable sentence under the claim-identity rule.

**Response:** CONCEDE

**Argument:** The objection is correct, and no amendment available inside this dataset repairs it.

I checked the only two defenses the card could mount, and both fail:

1. *"The claim is about the site-labeled noise channel, not physical scanner identity, so operator physicality doesn't matter."* This fails twice over. The deliverable sentence itself commits to "scanner-specific noise texture," so the weaker channel reading is already an identity change. And even the weaker claim still requires that the edit changes nothing else model-readable — directional correlations, local stationarity, resolution-noise coupling, surviving fine anatomy in the residual — which is precisely what is unvalidated. The equal-energy sham gates one artifact family (generic spectral perturbation), not that enumeration; a larger response to the target than the sham is compatible with sensitivity to any of those co-varying properties.

2. *"The classifier-flip manipulation check ties the dose axis to site identity."* The critic's instrument-circularity point stands: the same classifier family defines what counts as site-like and certifies that the edit became more site-like. Passing both establishes agreement with that classifier's decision boundary, not substitution of the underlying construct. A second classifier family would reduce overfitting, not confounding, because every classifier is trained on the same two-center data in which noise statistics, kernel, dose, geometry, and preprocessing are perfectly bundled.

The critic's discharge condition — primary validation of the frozen operator on repeated-phantom, traveling-subject, or paired-reconstruction acquisitions — is the correct and only route to the original question, and that data is outside ISLES'24 by construction. This makes the failure an IDENTIFIABILITY_FAILURE of the same family as idea-020: the card's `dies_like_prior` entry claimed the within-case transplant was "precisely such an intervention" that separates the mechanism from co-varying factors, but an intervention whose own validity cannot be established in any obtainable cohort does not discharge that kill pattern; it relocates it from the cohort to the operator.

What is lost: the mechanism-isolating use test, which was the entire point of the candidate. The Stage-0 decodability census survives as a fact-finding exercise but is, as the critique says, routine detectability — prior art territory (Zech et al., arXiv 2008.08525) — and not worth a standalone candidate. The keystone screen's verified facts (per-case center labels released, raw plus derivative arms present, five scanner models across two vendors) remain of record and transfer to any successor.

**Spin-off** (for normal scout-cycle registration with `parent_ids: ["isles24-scout-004-c06"]`, not mid-debate adoption): the critique's site-stratified out-of-fold benchmark audit — does final-infarct performance, calibration, or volume bias differ by center on strictly out-of-fold predictions, and does train-on-one-center transfer degrade beyond a size-matched within-center baseline? It keeps the medical motivation (multicenter deployment risk), uses only released labels, center assignments, and official metrics, and is honest that it measures the consequence without identifying the noise mechanism. A second, conditional successor — the original use test gated on externally validated noise-transfer operators from phantom or paired-reconstruction data — should only be registered if such a validation dataset is actually located; it dies on DATA_ACCESS otherwise.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The proposer has substantively conceded the fatal identifiability objection, so the original candidate should be rejected and neither proposed spin-off should be treated as an amendment.

**Argument:** The concession is supported by argument rather than repetition: it accepts that the classifier-flip check is instrument-circular, that the matched-energy sham excludes only one artifact family, and that ISLES'24 contains no paired or phantom acquisition capable of validating the residual-transfer operator while holding the other model-readable acquisition properties fixed. It also passes the identity check correctly. A site-stratified out-of-fold performance audit asks whether performance or calibration differs by center, not whether the model uses scanner-specific noise texture; the conditional externally validated transfer study preserves the original question but depends on evidence outside the current dataset that has not been located. Thus neither is a repair to this card, and the verified ISLES'24 facts about center labels, raw and derivative images, and scanner heterogeneity do not rescue the causal use claim. There is no remaining factual dispute within the present design: the candidate dies by IDENTIFIABILITY_FAILURE, while any successor must enter separately under the stated parent ID and undergo its own novelty and feasibility review.

**What would change my mind:** Locate the previously specified repeated-phantom, traveling-subject, or paired-reconstruction primary evidence validating the exact frozen transfer operator, together with an obtainable competent final-infarct model; that would justify registering and evaluating the conditional successor, not reversing this candidate's rejection in place.

**Status:** CONCEDED

## Round 2 — PROPOSER

**Responding to:** The critic accepts the round-1 concession as substantive, rules that neither spin-off is an amendment to this card, and closes the candidate as an IDENTIFIABILITY_FAILURE, with any successor entering separately under `parent_ids: ["isles24-scout-004-c06"]` and subject to its own novelty and feasibility review.

**Response:** CONCEDE

**Argument:** The concession stands and nothing in the critic's round 2 is contested; I will not re-argue what both sides already accept. Two closing points of record, neither reopening the dispute:

1. **The critic's reversal condition and my registration gate for the conditional successor are the same condition.** Round 1 said that successor "should only be registered if such a validation dataset is actually located; it dies on DATA_ACCESS otherwise"; the critic's what-would-change-my-mind names the same evidence (validated frozen transfer operator plus an obtainable competent final-infarct model) and the same consequence (register and evaluate the successor, never reverse this rejection in place). The condition can be carried into the ledger entry verbatim with no interpretive gap.

2. **Proposed ledger disposition, for the human gate:** REJECT, kill code IDENTIFIABILITY_FAILURE, with the specific signature recorded so future candidates can be checked against it: the intervention's own construct validity — that the transfer operator changes site-noise identity while leaving everything else model-readable fixed — cannot be established in any obtainable cohort; the idea-020 kill pattern relocated from cohort to operator. Facts of record that transfer to successors: per-case center labels are released (arXiv 2408.11142v2, keystone screen), raw and derivative arms exist per case, five scanner models across two manufacturers with no device-to-center mapping, and the public train set is 149 cases (99 + 50), correcting the card's 100 + 50. The site-stratified out-of-fold benchmark audit enters through a normal scout cycle on its own merits, with no inherited queue position, per the 2026-08-10 claim-identity rule.

No factual dispute remains and no amendment is on the table.

**Status:** CONVERGED
