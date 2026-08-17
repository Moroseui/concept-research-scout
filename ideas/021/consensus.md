# Debate summary — idea 021

## Agreed

- The round-zero edit/readout-disjointness argument is invalid under per-case normalization computed from an edited tensor: contralateral scaling would alter affected-side network inputs arithmetically before inference. The proposer conceded this in round 1, and the critic accepted the repair in round 2.
- The frozen pipeline must compute perfusion normalization constants independently of each edited tensor, either from the unedited case or from frozen cohort-level statistics. A numerical gate must verify that contralateral-only editing leaves affected-side network-input voxels bit-identical (rounds 1–2).
- The experiment should include global, contralateral-only, and partial-contralateral scaling arms so that whole-image gain behavior can be compared with hemisphere-specific behavior (round 1; accepted by the critic in round 2).
- A gated null cannot establish that the model uses absolute perfusion values, nor can it support the original claim about fragility to cardiac output or injection variation. At most it establishes no detected mirror-specific use beyond the pinned standardization, subject to adequate sensitivity (round 1).
- The original deliverable overclaimed identity with the clinical mean-contralateral-CBF ratio. The proposed intervention does not distinguish ratio, difference, or another learned signed comparator. Campbell-style rCBF is therefore motivation, not a mechanism that this study may claim to have recovered (round 2, retained in round 3).
- Direct affected-side editing would sacrifice the spatial disjointness that motivates this candidate and would introduce a harder pathology-edit realism problem. The proposer declined that factorial design for this candidate; the critic had explicitly allowed a narrowed claim if such edits were uninterpretable (round 2).
- Laterality competition, bilateral-lesion detection, unsigned anomaly response, generic contralateral context, and edit-induced cross-channel inconsistency must be treated as alternative explanations rather than ignored (rounds 2–3).
- The study needs frozen margins, an edit-realism/cross-channel discriminator gate, and a pre-run minimum-detectable-effect analysis. If the planned sample cannot detect the frozen slope margin, the study must increase its sample or report itself unpowered rather than interpret a null (round 3; this also answers the power defect raised in the critique).
- If the stricter reference-setting test cannot be executed validly, the weaker result is only that the model uses contralateral perfusion information; it does not resolve whether that information acts as a patient-specific baseline (round 3 proposer, adopting the critic's fallback).

## Unresolved

### Does the round-three conjunction identify reference-setting rather than generic cross-hemispheric use?

- **Question:** Is a signed monotone response in both directions—especially increased affected-side predicted deficit when the healthy hemisphere is up-scaled—combined with no emergent contralateral lesion and a contralateral-over-global response margin, uniquely adequate evidence that the healthy hemisphere sets a personal perfusion baseline?
- **Proposer's position:** Yes, at the declared functional level. A signed left-right comparator that helps judge the affected-side deficit is an implementation of “baseline,” not an alternative. The up-scaling direction, emergence gate, and mirror-specificity margin jointly exclude laterality competition, bilateral-lesion detection, unsigned anomaly detection, and nonspecific context. Ratio versus difference versus another learned comparator remains out of scope.
- **Critic's position:** Before the conjunction was proposed, the critic held that “personal baseline” remained stronger than the three-arm evidence and demanded a preregistered, powered test whose prediction was not shared by hemispheric mismatch, laterality competition, bilateral-lesion detection, or generic context. The critic did not respond after the proposer supplied the round-three conjunction, so acceptance or rejection of its identifying logic is unknown.
- **What evidence would settle it:** A fresh critic or methods review must write down the predicted response, including its sign, for each named alternative under every arm and determine whether any non-reference mechanism survives all gates. Simulation or controlled models implementing those alternatives could test whether the conjunction has false positives. If “signed hemispheric mismatch used to judge deficit” and “personal baseline” are treated as definitionally identical, the remaining disagreement is semantic and must be resolved by a human claim-definition decision, not empirical evidence.

### Can the discriminating up-scaling arm remain physiologically and cross-modally in distribution?

- **Question:** Is there a nontrivial up-scaling range in which edited CBF/CBV remains plausible relative to NCCT, CTA, Tmax, and the cohort distribution while retaining enough effect to test the frozen slope?
- **Proposer's position:** This is a hard preregistered gate. If the arm fails the discriminator/realism gate, the reference question is unresolved and only the weaker contralateral-information result may be reported.
- **Critic's position:** Unilateral perfusion scaling can resemble contralateral vascular disease or create cross-channel inconsistency; a generic real-versus-edited discriminator alone does not establish the intended mechanism. The critic has not assessed whether the proposed up-scaling and emergence gates are sufficient.
- **What evidence would settle it:** Inspect the actual ISLES'24 tensors and freeze an empirical, cross-channel up-scaling envelope before confirmatory scoring; then test every dose with a held-out real-versus-edited discriminator and explicit CBF/CBV–Tmax–CTA consistency checks. Failure to find an adequately powered passing range settles this against the current design.

### Is the weaker fallback a revision of idea 021 or a successor?

- **Question:** If only “the model uses contralateral perfusion information” survives, may that finding remain under idea 021?
- **Proposer's position:** It is a preregistered failure-path report that explicitly leaves the original baseline question unresolved; the human should adjudicate successor registration at that point.
- **Critic's position:** Removing the reference-setting predicate changes the deliverable claim's identity, so the weaker experiment/result must be a successor under the portfolio's claim-identity rule.
- **What evidence would settle it:** No scientific evidence can settle this governance question. The human must apply the 2026-08-10 claim-identity rule to decide whether deleting “as a patient-specific reference” changes the deliverable sentence. Existing precedent favors successor registration when the predicate changes.

### Is the study adequately powered within the available cohort and compute envelope?

- **Question:** Can the available held-out cases detect the frozen paired trend and mirror-specificity margins after exclusions and invalidated doses?
- **Proposer's position:** Validation-fold variability must support an MDE calculation before confirmatory scoring; otherwise increase the case count or stop as unpowered.
- **Critic's position:** The original 40-case plan was unsupported given weak and variable ISLES'24 predictions; no evidence in the debate establishes adequate power.
- **What evidence would settle it:** A blinded Stage 0 power memo using validation-fold prediction variability, anticipated exclusions, within-case covariance, and the prespecified margins. If the required sample exceeds the obtainable clean cases, the claimed negative is sensitivity-limited and the design must pause or narrow.

## Positions that moved

- **Proposer, round 1:** Conceded that per-case normalization destroys raw-space edit/readout disjointness, that co-registration was the nearest checkable fact rather than the true identifiability keystone, and that the original null could not imply absolute-value reliance. This was earned by the critic's explicit normalization mechanism.
- **Critic, round 2:** Accepted that normalization pinned to the unedited case plus a bit-identity gate repairs the deterministic preprocessing pathway and preserves the original question. This was earned by the round-1 design amendment.
- **Proposer, round 2:** Conceded that the original deliverable asserted the clinical rCBF-ratio mechanism beyond rung-1 evidence. The ratio claim was demoted to motivation, with within-family mechanism identity moved to a possible successor. This was earned by the critic's mismatch/laterality alternatives.
- **Proposer, round 3:** Accepted that the tier-1 positive needed more than an arbitrary cross-hemispheric response and added a signed bidirectional dose-response, a contralateral-emergence gate, a mirror-specificity margin, and a power gate. This was earned by the critic's objection that “personal baseline” remained a functional claim.
- **Proposer, round 3:** Did not concede that signed hemispheric mismatch is an alternative to the baseline claim; instead, the proposer classified signed comparison used in affected-side judgment as an implementation of that claim. This remains a substantive definitional disagreement.
- **No unearned concession was identified.** However, the proposer's round-3 declaration of `CONVERGED` is not itself consensus: the critic never evaluated the new conjunction.

## Amendments made

At round zero, the idea claimed that raw spatial separation alone made any affected-side response proof of a learned healthy-hemisphere reference, identified that reference with clinical rCBF normalization, and interpreted a null as absolute-value reliance. It proposed contralateral CBF/CBV scaling, partial-area edits, an affected-side positive control, and a sham in 40 cases.

The amended idea instead:

- pins normalization constants to the unedited case or a frozen cohort reference and requires affected-side input bit-identity;
- adds global and bidirectional contralateral scaling;
- makes a positive reference claim conditional on a signed monotone response, an especially discriminating up-scaling response, no emergent contralateral lesion, and a frozen contralateral-over-global margin;
- requires cross-channel edit-realism gates and an MDE/power gate before confirmatory scoring;
- treats ratio, difference, and learned comparator identity as outside the confirmatory claim;
- interprets a valid null only as no detected mirror-specific reference beyond pinned standardization; and
- reports failure of the conjunction only as contralateral-information use, leaving the baseline question unresolved and triggering a human successor-identity decision.

What was lost is substantial: the study can no longer claim that the model rediscovered the clinical rCBF convention, cannot infer absolute-value reliance from a null, cannot infer fragility to global hemodynamic variation, is no longer a simple one-week/40-case experiment, and may be unable to answer its central question if the up-scaling arm fails realism or power gates. It characterizes one self-trained, deliberately normalized model rather than unreleased challenge-winning pipelines.

## Recommendation

**REVISE.** The round-three design may repair the remaining mechanism-family objection, but that repair was never tested by the critic and is not yet in the idea card. Before deciding, the human should look most closely at a prediction table for the signed up-scaling conjunction: can any plausible non-reference mechanism produce increased affected-side deficit under healthy-side up-scaling while passing the contralateral-emergence, global-arm, realism, and power gates? The card should not advance until an independent review answers that question and the actual card is rewritten to the agreed normalization pins, reduced claims, gates, power requirement, and fallback governance.

```json
{"verdict": "REVISE", "unblock": "Independently validate that the signed up-scaling conjunction excludes the named non-reference mechanisms, then rewrite the card with frozen normalization, realism, emergence, margin, and power gates plus successor handling for the weaker fallback."}
```
