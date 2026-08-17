# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed experiment cannot identify the original capillary-transit-time-heterogeneity claim because large-vessel and collateral-path bolus dispersion produces the same tissue-curve broadening.

**Argument:** In this LVO stroke cohort, the arterial input function is measured upstream of tissue reached through patient-specific collateral routes. Willats, Connelly, and Calamante (MRM 2006) showed that the effective residue-function shape reflects bolus distortion as well as tissue hemodynamics, and Calamante et al. (MRM 2000) showed that correcting dispersion requires a vascular model; delay-insensitive deconvolution removes arrival-time sensitivity, not dispersion. The card's moment-matched edits and recomputed CBF/CBV/MTT/Tmax controls therefore isolate, at best, transit-time dispersion in observed tissue curves. They do not distinguish capillary passage heterogeneity from macrovascular dispersion, which is especially plausible inside the Tmax>6 s territory in collateral-dependent LVO. Renaming the result to “the model uses tissue-curve dispersion” would be a defensible rung-1 successor, but it changes the physician-facing X and deliverable sentence; under the claim-identity rule it does not repair Idea 024 in place.

**What would change my mind:** A primary-source-validated, independently computable CTP measurement or paired acquisition in this population that separates upstream macrovascular dispersion from capillary transit-time variance, followed by an intervention that changes the latter while holding the former fixed through the model's final input tensor.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The design's moment-matched edits and recomputed conventional-map controls can at best isolate dispersion of the observed tissue curves; they cannot attribute that dispersion to capillary passage rather than upstream macrovascular and collateral-path bolus distortion, which in this LVO cohort is maximal precisely inside the Tmax>6 s territory the card aggregates over. Any repair that renames X to generic tissue-curve dispersion changes the deliverable sentence and therefore cannot rescue Idea 024 in place.

**Response:** CONCEDE

**Argument:** The objection is correct, and I have no new evidence against it. The critic's condition for changing their mind — an ISLES'24-computable measurement that separates upstream macrovascular dispersion from capillary transit-time variance — cannot be met on this data: the release contains one global AIF site per case, no local arterial sampling, no vascular model inputs, and Calamante et al. (MRM 2000) establishes that dispersion correction requires exactly the vascular model that is absent. Delay-insensitive deconvolution addresses arrival time only. So the micro-versus-macro attribution the deliverable sentence requires ("capillary transit-time heterogeneity, a dispersion property of microvascular passage") is unavailable in principle on this cohort, not merely unverified. The identity check on the only available amendment fails: "the model uses transit-time dispersion in the tissue curves" is a different physician-facing X and a different deliverable sentence, which under the 2026-08-10 claim-identity rule is REJECT (superseded), not revision-in-place.

I concede the wider position as well, because the critique record for this idea (`critique.md`, this folder, 2026-08-17) independently establishes two facts that would kill the idea even if the attribution problem were solved: (1) no ISLES'24 team that consumed raw 4D CTP released trained weights, so the "already trained raw-CTP model" the smallest decisive experiment freezes does not exist, and training one from scratch is outside the card's stated compute envelope while the challenge's own aggregate result (maps ≥ raw CTP; PrediCTP Dice 0.20) says the subject would be too weak for an interpretable null; and (2) the nonparametric residue-variance estimator of CTH was explicitly rejected for CT by the construct's originators (Mouridsen et al. 2014, JCBFM, DOI 10.1038/jcbfm.2014.111) because regularizer-imposed smoothness makes the recovered shape stable-but-invalid — which means the card's Stage-0 cross-regularizer stability gate could pass while measuring nothing microvascular. No subject, no instrument, no attribution: three independent kills.

**Spin-off:** None registered. The nearest defensible successor territory — whether a released map-based ISLES'24 winner uses a named, map-computable hemodynamic quantity — is already occupied by shortlisted ideas 021 and 023, per the critique's easier-version search; a CTH-flavored duplicate would add homogenization (counterfactual-synthesis already at x12), not coverage.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** I concede the debate because the proposer accepts that the original capillary-transit-time-heterogeneity claim is unidentifiable on ISLES'24 and that every feasible amendment changes the question.

**Argument:** The proposer answered the decisive objection with the specific missing information and mechanism: one global AIF, no local arterial sampling or vascular-model inputs, and no way for delay-insensitive deconvolution to separate collateral-path macrovascular dispersion from microvascular transit-time variance. That establishes that the proposed intervention cannot support the original physician-facing sentence. The identity check also resolves the disposition: replacing capillary transit-time heterogeneity with tissue-curve dispersion would change X and the deliverable sentence, so it must not be treated as a repair to Idea 024. The additional inspected failures—no released raw-CTP checkpoint suitable for the frozen-model experiment and rejection of nonparametric residue-variance estimation for CT by Mouridsen et al. 2014—independently reinforce rejection, but no further objection is needed once the original claim is conceded as unidentifiable.

**What would change my mind:** Only the evidence specified in round 1: a validated, independently computable CTP measurement or paired acquisition that separates upstream macrovascular dispersion from capillary transit-time variance in this population, plus an obtainable performant raw-CTP model and a selective intervention that changes the latter while holding the former fixed through the final model input.

**Status:** CONCEDED

## Round 2 — PROPOSER

**Responding to:** The critic's round-2 concession, which closes the debate: the original capillary-transit-time-heterogeneity claim is unidentifiable on ISLES'24, no feasible amendment preserves the deliverable sentence, and no further objection is needed.

**Response:** CONCEDE

**Argument:** Nothing remains in dispute; my round-1 concession stands unmodified. What is new in this round is only the disposition record for the ledger. Recommended entry: **Idea 024 REJECT**, with a composite kill classification — primary DATA_ACCESS (no ISLES'24 team that consumed raw 4D CTP released trained weights, so the frozen audit subject does not exist and cannot be created inside the stated compute envelope), compounded by IDENTIFIABILITY_FAILURE (with one global AIF and no vascular model, macrovascular/collateral bolus dispersion is inseparable in principle from capillary transit-time variance; Calamante et al. MRM 2000, Willats et al. MRM 2006), and by an instrument-invalidity mode the kill-code list does not yet name: X could not be computed by any released, citable, construct-valid tool, because the nonparametric residue-variance estimator was rejected for CT by the CTH construct's own originators (Mouridsen et al. 2014, JCBFM, DOI 10.1038/jcbfm.2014.111) — a violation of the charter's hard constraint on X, and a mode worth adding to the ledger's failure taxonomy so future cards check it. The critique's keystone audit should also enter the record as the fourth occurrence of the wrong-keystone error: temporal adequacy was the nearest checkable thing, while the load-bearing assumptions — an obtainable subject model and a valid instrument — were checkable from public sources on the day the card was written, and both were adverse. Reopen conditions are exactly the critic's evidence bar, all three prongs jointly: a validated CTP measurement or paired acquisition separating upstream macrovascular dispersion from capillary transit-time variance in an LVO population, an obtainable performant raw-CTP model, and a selective intervention that changes the latter while holding the former fixed through the final input tensor.

**Spin-off:** None, reaffirmed from round 1: the adjacent map-based model-use territory is already held by shortlisted ideas 021 and 023, and a CTH-flavored duplicate would add homogenization, not coverage.

**Status:** CONVERGED
