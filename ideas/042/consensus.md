# Debate summary — idea 042

## Agreed

- The round-zero edit is internally contradictory over its full proposed dose range: at fixed curve area and peak height, width contraction is bounded by the boxcar limit, and approaching that limit produces shapes that conflict with the intended physiological-realism gate (round 1).
- Letting peak height rise in an area-preserving dispersion edit creates a peak-amplitude alternative explanation; the original matched delay arm does not remove it (round 1).
- Replacing the original question with sensitivity to an undifferentiated width–peak bundle would change the claim's identity and should be handled as a successor, not as a revision in place (rounds 1–2).
- The round-1 subtraction between the physiologic dispersion and peak-only arms is not identifying: the peak-only arm changes area, and interpreting the subtraction requires an untested additivity assumption for a nonlinear network (round 2).
- A low-dose, peak-preserving dispersion edit can only be asserted on a prespecified common-support subset where it is constructible and all arms pass the same realism gates. Making that subset and edit confirmatory removes the specific peak/area confound from round 2 while preserving the original question (rounds 2–3).
- The common-support subset must be determined before model inference and must have a prespecified minimum-size kill gate. It selects relatively dispersed tissue and therefore narrows the population to which any result applies (round 2).
- Confirmatory claims must be restricted to retained low doses. The 50% and 75% physiologic edits are exploratory (round 2).
- Moment constraints do not uniquely determine a concentration-time curve. A variance contraction at fixed arrival time, area, and peak will also change some combination of skewness, tail fraction, kurtosis, slopes, or temporal-frequency content (round 3).
- The edit operator should be completely preregistered; its full descriptor changes should be computed before inference and published; and its realism gate should include the temporal descriptors named in round 3 (round 3).
- A positive experiment cannot establish collateral-route physiology without independent collateral measurements. The live rung-1 claim is limited to model use of delay-independent post-alignment curve shape distinct from delay and amplitude (implicit throughout and made explicit by the proposer's round-3 formulation).

## Unresolved

### Does the common-support edit identify physiological dispersion or only sensitivity to one reshaping operator?

**Question:** After arrival time, area, and peak are held fixed, are the remaining co-movements in variance, tail fraction, kurtosis, slopes, and spectral energy measurements of one physiological dispersion degree of freedom, or are they distinct model-usable alternatives that prevent a selective-dispersion claim?

**Proposer's position:** Within the same-case physiological curve family, these descriptors are functionally coupled manifestations of transport-kernel spreading. Delay and delivered amplitude are separate physical cue classes and are controlled; requiring all other shape descriptors to remain invariant would demand a nonphysiological edit. A fully pinned interpolation operator plus a full-descriptor same-case gate therefore supports the broader rung-1 construct, “delay-independent bolus dispersion (post-alignment curve shape),” while the exact mediating descriptor belongs to a successor study.

**Critic's position:** Fixed arrival, area, peak, and a target second moment still underdetermine the curve. Realism and nearest-neighbor support do not demonstrate that the network response is caused by dispersion rather than tail, slope, kurtosis, or spectral changes introduced by the chosen operator. Without bounding those alternatives below repeatability limits, the result supports sensitivity to that operator's shape bundle, not selective use of dispersion.

**What evidence would settle it:** Before inference, apply a completely specified operator to released ISLES'24 curves and empirically map the admissible same-case curve manifold. Test whether, conditional on fixed arrival, area, and peak, the named descriptors lie on an effectively one-dimensional, monotonic dispersion trajectory across cases, scanners, and affected-tissue regions, with residual orthogonal variation below prespecified repeatability limits. Then test alternative admissible operators that reach matched dispersion-coordinate changes: concordant model responses would support the proposer's construct; materially different responses would support the critic's operator-specific objection. If the parties disagree about whether even such operator invariance is sufficient to call the construct “dispersion,” the remaining disagreement is terminological and cannot be settled by this dataset alone.

### Is the common-support subset large and stable enough for a confirmatory experiment?

**Question:** Do released ISLES'24 curves contain enough affected-tissue voxels and cases with sufficient headroom above the boxcar bound for realistic low-dose peak-preserving edits?

**Proposer's position:** Define membership deterministically from unedited data and edit constructions, freeze it before inference, and kill the design if a prespecified fraction of affected-tissue voxels and minimum number of cases do not pass every arm's gate.

**Critic's position:** The common-support design is an acceptable logical repair to the round-2 peak/area confound, but it has not been demonstrated on released data.

**What evidence would settle it:** A model-blind Stage 0 construction study on the 20 inspection cases, with headroom, full-descriptor realism, per-case voxel-fraction, and contributing-case thresholds frozen before examining model outputs. This is an empirical feasibility question.

### Can the required physical-family constraint be justified rather than assumed?

**Question:** Does interpolation through observed same-case curves genuinely restrict edits to a transport-consistent family, and does fixing arrival, area, and peak leave “essentially one” shape parameter?

**Proposer's position:** Smooth tissue curves generated by an arterial input convolved with transport and residue kernels form a gamma-like family in which the named shape descriptors move together; same-case interpolation and the expanded descriptor gate pin the edit to that family.

**Critic's position:** Same-case proximity establishes plausibility, not the claimed dimensionality or causal meaning of the trajectory. The cited transport literature does not by itself prove that the proposed second-moment manipulation uniquely follows physiological dispersion.

**What evidence would settle it:** Fit and compare prespecified one- versus multi-dimensional transport-family models to the unedited curves, assess held-out reconstruction and descriptor residuals, and verify that the proposed interpolation paths correspond to changes in an explicit transport-kernel dispersion parameter rather than arbitrary mixtures of tissue residue and preprocessing effects. Direct validation against an independent dispersion or collateral measurement would be stronger, but ISLES'24 may not contain it.

## Positions that moved

- **Proposer, round 1:** Conceded the critic's boxcar-bound argument, the incompatibility between the original invariances and physiological realism, and the fact that allowing peak to rise leaves a peak-amplitude explanation. This was earned by the critic's explicit fixed-area/fixed-peak construction argument.
- **Proposer, round 1:** Replaced the single dispersion edit with physiologic dispersion, peak-only, low-dose peak-preserving dispersion, and delay arms, plus a construction-before-inference gate. This was an earned response to the critic's requested control family.
- **Critic, round 2:** Accepted that the round-1 amendment preserved claim identity and added the appropriate control family, while rejecting its primary subtraction. This movement was earned by the concrete amended design.
- **Proposer, round 2:** Conceded that dispersion-minus-peak subtraction was invalid because area was unmatched, additivity was assumed, and no conservative direction was justified. This was earned by the critic's explicit decomposition of the two arms.
- **Proposer, round 2:** Made the low-dose peak-preserving edit confirmatory on a frozen common-support subset, added a subset-size kill gate and required physiologic-arm concordance, and demoted large doses. This directly adopted the critic's first proposed repair.
- **Critic, round 3:** Accepted that the common-support amendment fixed the peak/area confound and preserved the original question. This was earned by the round-2 invariance-based redesign.
- **Proposer, round 3:** Accepted the mathematical premise that moment constraints underdetermine curves and adopted complete operator specification, a full-descriptor realism gate, and publication of descriptor deltas. The specification changes were earned by the critic's identification of co-edited temporal features. The proposer did not concede the critic's inference that these are separate confounds.
- No concession was UNEARNED. The final exchange is a rebuttal and partial procedural amendment, not consensus on construct validity.

## Amendments made

At round zero, the idea claimed that one dispersion-only edit could contract width while preserving arrival time, area, peak, and noise across 25%, 50%, and 75% doses, and that a stronger response than to a matched delay edit demonstrated selective use of dispersion. It also described dispersion as a collateral-route signal.

The debated version instead makes a low-dose, peak-preserving edit confirmatory only within a frozen common-support subset of sufficiently dispersed tissue. Subset membership requires the peak-preserving, physiologic dispersion, peak-only, and matched-delay arms to pass identical support and expanded full-descriptor realism gates before inference. The primary response must exceed the matched-cost delay response and be dose-ordered; the physiologic arm must be sign- and dose-concordant on the same subset. The peak-only arm is descriptive context, not an algebraic subtraction. Larger physiologic doses are exploratory.

The operator must be fully specified as movement along interpolation paths through real same-case curves of lower measured dispersion. Gates now include skewness, tail-area fraction, kurtosis, maximum upslope and downslope, and temporal spectral energy, and all descriptor deltas must be published.

What was lost: the claim that a single edit “narrows only the spread”; generalization to all affected tissue; confirmatory claims at 50% and 75% doses; the round-1 dispersion-minus-peak contrast; and any direct attribution to collateral routes. The surviving proposed claim is narrower: in tissue where a realistic low-dose invariant edit is constructible, the model uses delay-independent post-alignment curve shape, interpreted as dispersion, distinctly from delay and amplitude. Whether that last interpretation is identified remains unresolved.

The idea card itself has not yet been rewritten to encode these amendments and still contains the superseded round-zero design and collateral wording.

## Recommendation

**REVISE.** The debate repaired two concrete identifiability failures, but the final rebuttal introduced an unverified load-bearing assertion: that the admissible same-case curve family is effectively one-dimensional after arrival, area, and peak are fixed, so all remaining descriptor changes are manifestations of dispersion rather than operator-specific alternatives. Before deciding, the human should look most closely at whether an empirical, model-blind manifold and alternative-operator test is sufficient to operationalize “dispersion”; that decision determines whether this remains idea 042 or must become a narrower operator-specific successor.

## In plain terms

This idea asks whether a stroke model reacts to how spread out the contrast bolus is after separating that shape from simple late arrival and overall brightness. It would make small, realistic curve edits and compare the model's response with matched timing and amplitude controls.

The debate found that the original edit could not do what it promised and that the first repair still mixed in total contrast. A narrower low-dose design fixes those problems only in suitable tissue, but the sides still disagree over whether the other curve-shape changes are all part of physical dispersion or are separate cues created by the edit. The human is being asked to judge whether a model-blind curve-manifold and alternative-operator test would make “dispersion” a defensible name for the tested signal.

```json
{"verdict": "REVISE", "unblock": "Rewrite the card to the low-dose common-support design and, before model inference, show with released ISLES'24 curves and matched alternative operators that the admissible fixed-arrival/fixed-area/fixed-peak trajectory supports a defensible dispersion construct rather than operator-specific shape sensitivity."}
```
