# Debate summary — idea 037

## Agreed

- By proposer round 1, both sides accepted that the proposed noise-residual/NPS transplant does not isolate a physical acquisition-site noise fingerprint. Reconstruction kernel, dose, interpolation, spatially varying noise, residual anatomy, and denoiser error can change with the edit, and ISLES'24 has no paired acquisition, phantom, or traveling-subject data with which to validate the operator while holding those alternatives fixed.
- By proposer round 1, both sides accepted that the classifier-flip manipulation check is instrument-circular: it shows that the edit crosses the site classifier's boundary, not that it substitutes the underlying physical construct. A second classifier family would reduce classifier-specific overfitting but would not remove the acquisition and preprocessing confounding.
- By proposer round 1, both sides accepted that the equal-energy sham rules out only a limited generic-perturbation explanation. It does not establish invariance of directional correlations, local stationarity, resolution–noise coupling, or residual fine anatomy.
- By proposer round 1, both sides accepted that the honest weaker conclusion—“the model responds to this NPS-remapping operator”—would change the deliverable sentence and therefore cannot repair idea 037 in place under the repository's claim-identity rule.
- By critic round 2, both sides accepted that the site-stratified out-of-fold performance audit is a separate successor: it tests the consequence of center shift, not use of scanner-specific noise. They also accepted that a renewed noise-use study would be a separate conditional successor requiring external construct-validation data and a competent frozen final-infarct model.
- By proposer round 2, both sides accepted rejection of the present candidate under `IDENTIFIABILITY_FAILURE`. The failure is specifically that the intervention's construct validity cannot be established in an obtainable cohort, rather than that center labels or ISLES'24 images are unavailable.
- By proposer round 2, both sides accepted that verified dataset facts may transfer as facts, but not as inherited merit or queue position: ISLES'24 releases per-case center assignments, raw and derivative imaging, and includes multiple scanner models and vendors, while the public training cohort contains 149 cases (99 from Center 1 and 50 from Center 2).

## Unresolved

There is no remaining dispute about the disposition of idea 037 or the inference supported by its proposed experiment.

One empirical condition remains open only as a possible trigger for a future candidate:

- **Question:** Can the exact frozen noise-transfer operator be validated on obtainable repeated-phantom, traveling-subject, or paired-reconstruction data as changing independently recoverable device/site noise identity while preserving anatomy and every other model-readable acquisition property, and can it then be applied to a competent frozen final-infarct model?
  - **Proposer's position:** This is the only route back to the original noise-use question, but no such dataset/operator validation or suitable model has been located; a successor should not be registered until it is.
  - **Critic's position:** The same evidence would justify registering and evaluating a new conditional successor, but would not reverse the rejection of idea 037 in place.
  - **Evidence that would settle it:** Primary validation of the exact operator on repeated-phantom, traveling-subject, or paired-reconstruction acquisitions, demonstrating preservation of anatomy, resolution, dose/kernel information, and other model-readable evidence, plus an obtainable competent frozen ISLES'24 final-infarct model with a prespecified spatial output endpoint.

## Positions that moved

- **Proposer, round 1:** Conceded the fatal identifiability objection in response to the critic's argument that NPS/residual edits co-manipulate acquisition, reconstruction, preprocessing, and residual-anatomy properties; that the classifier check is circular; and that ISLES'24 provides no independent validation design for the operator. This concession was earned: it directly addressed the critic's construct-validity argument and tested the two available defenses before rejecting both.
- **Proposer, round 1:** Conceded that weakening the claim to sensitivity to an NPS-remapping operator would change the idea's identity, in response to the critic's application of the claim-identity rule. This was earned and explicitly stated what would be lost.
- **Critic, round 2:** Moved from an open objection to accepting convergence after the proposer substantively conceded every load-bearing point. This was not a concession on the scientific issue; it was recognition that no factual dispute remained.
- **Proposer, round 2:** Reaffirmed the rejection and successor boundary without a new scientific argument. This is not flagged as UNEARNED because it did not introduce a new concession; it recorded closure on the already-supported round-1 agreement.

## Amendments made

No amendment to idea 037 was adopted. At round zero, the idea claimed that a within-case, matched-energy spectral transplant could isolate scanner-specific noise texture and show that a final-infarct model uses the acquisition-site fingerprint. That claim was withdrawn as unsupported because the operator cannot be shown to manipulate only that construct.

The following alternatives were identified but explicitly kept outside this candidate:

- a site-stratified, strictly out-of-fold performance, calibration, and volume-bias audit, including cross-center transfer against a size-matched within-center baseline; and
- a conditional noise-use successor, but only after external primary evidence validates the exact transfer operator and a competent frozen final-infarct model is obtainable.

What was lost is the candidate's central mechanism claim: ISLES'24 alone cannot support an experiment identifying use of scanner-specific stochastic noise. The cheaper center-decodability census survives only as diagnostic context and was agreed not to be sufficient as a standalone candidate.

## Recommendation

**REJECT.** The single most important thing for the human to inspect is whether the record correctly applies the claim-identity rule: neither a center-stratified performance audit nor mere sensitivity to an NPS-remapping operator answers the original question about model use of scanner-specific noise, so neither can preserve this candidate in place.

## In plain terms

This idea asks whether a stroke model can recognize the hospital or scanner from faint image noise and then use that clue when predicting the final damaged brain tissue. It proposed changing that noise within the same patient's scan and observing whether the prediction moved.

The debate concluded that this edit would also change other properties created by scanning, reconstruction, and preprocessing, so a model response could not be attributed specifically to a scanner-noise fingerprint. Because ISLES'24 has no paired or phantom data that could validate the edit while keeping those other properties fixed, both sides agreed that the present idea should be rejected; a direct audit of performance differences between centers would be a separate idea.

The human is being asked to judge whether that separate performance audit changes the original claim enough that it must enter the pipeline as a new candidate.

```json
{"verdict": "KILL", "kill_code": "IDENTIFIABILITY_FAILURE", "unblock": "Register a new successor only after primary evidence validates the exact frozen noise-transfer operator on obtainable paired or phantom acquisitions and a competent frozen final-infarct model is obtainable."}
```
