# Debate transcript

## Round 1 — CRITIC

**Position:** The factorial CTA/tensor edits do not intervene on intracranial compliance or mechanically valid swelling, so their interaction cannot identify the original claim that the model uses CSF reserve to expand final-infarct geometry.

**Argument:** The released winner consumes CBF, CBV, MTT, Tmax, and CTA—not NCCT—and the proposed repair injects edits after global histogram equalization and with frozen normalization constants. That can isolate sensitivity to chosen tensor patterns, but it cannot create two physically possible brains that differ only in compliance: changing ventricular or sulcal reserve necessarily displaces adjacent anatomy, while keeping parenchymal inputs bit-identical necessarily creates or deletes synthetic image content without implementing pressure–volume mechanics. Likewise, net water uptake is an admission-NCCT attenuation measurement within ischemic tissue (Broocks et al., DOI `10.1161/STROKEAHA.118.020507`), not a validated swelling dose transferable to CTA or perfusion tensors. ISLES'24 supplies follow-up infarct masks but no edema, mass-effect, deformation, or intracranial-pressure target (dataset DOI `10.1148/ryai.250603`). Therefore even a gated reserve-by-“edema” interaction remains compatible with ordinary nonlinear coupling between two artificial patterns, receptive-field effects, or age/anatomy-conditioned prediction. It does not establish pressure-vessel mechanics or expansion beyond acute tissue injury. The easier reserve-stratified error audit would be feasible, but it changes the deliverable from model use of compliance to an observational reliability association and must be a separate candidate under the claim-identity rule.

**What would change my mind:** Show a source-validated intervention or natural paired design in which the model inputs encode independently measured differences in intracranial compliance and mechanically observed swelling/deformation while acute injury burden is held fixed, with an external edema, displacement, or pressure measurement demonstrating that the manipulated dose has the claimed physical meaning; alternatively, narrow the deliverable to tensor-pattern sensitivity and register it as a new candidate.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The two factorial factors cannot carry the constructs the question names. The "reserve" edit cannot instantiate a physically possible brain that differs only in compliance, because real reserve differences necessarily displace adjacent anatomy while the design demands bit-identical parenchyma; and the "edema" factor has no validated physical meaning once moved off NCCT into equalized CTA/perfusion tensor space, because net water uptake is defined and validated only as an admission-NCCT attenuation measurement within ischemic tissue. Therefore even a clean, gated, signed interaction remains an interaction between two synthetic patterns and cannot identify model use of compliance or expansion "beyond acute tissue injury."

**Response:** CONCEDE

**Argument:** The objection is correct, and it is fatal to the question as posed rather than to a repairable part of the design.

Two independent failures, either sufficient alone:

1. **The edema factor has no dose validity in the space where the edit must live.** The keystone screen's own findings force the edit downstream of global histogram equalization on a model that never sees NCCT (`inference.py:121-125`, commit `bb6c00c8`). Broocks et al. (DOI `10.1161/STROKEAHA.118.020507`) validate net water uptake as an admission-NCCT attenuation measurement inside an early ischemic lesion — nothing licenses transplanting that scalar onto equalized CTA and perfusion tensors and calling it a swelling dose. Without a valid dose, the compliance construct's signature prediction ("same swelling, different geometric response by reserve") is unmeasurable in principle within this design, not merely unpowered or ungated.

2. **The compliance counterfactual is anatomically impossible by construction, and the target phrase is unobservable.** A brain with different CSF reserve is a brain with different adjacent tissue geometry; requiring parenchymal bit-identity guarantees the edited input depicts no physically possible alternative anatomy. And "beyond acute tissue injury" cannot be identified because acute irreversible injury is never independently observed, and ISLES'24 carries no edema, mass-effect, deformation, or pressure target (DOI `10.1148/ryai.250603`) against which label-borne expansion could be validated.

One point of partial disagreement, recorded because it does not change the verdict: the critic's phrase "ordinary nonlinear coupling" understates what the prespecified signed interaction conjunction would discriminate — it does rule out purely additive age/atrophy main effects, which is more than nothing. But that statistical discrimination operates downstream of the construct failure. It can establish that the model couples the two edited patterns nonlinearly; it cannot give that coupling the meaning "reserve absorbing swelling," because neither edited pattern validly instantiates its construct. Identifiability fails at measurement validity, before the statistics start.

**Identity check on amendment:** attempted and failed. The only amendment that survives the objection — narrowing the deliverable to "the frozen winner's output is sensitive to a prespecified interaction between CSF-region and lesion-region tensor patterns" — abandons compliance, swelling, and "beyond acute tissue injury," which are the question's identity. Under the 2026-08-10 claim-identity rule that is a successor, not a repair. I therefore do not amend.

**Spin-off (not defended here, to register as a new candidate through the normal pipeline):** the critique's reserve-stratified benchmark error audit — does the released winner's held-out final-infarct error vary with baseline NCCT CSF/ICV after prespecified adjustment for age, site, acute lesion burden, perfusion deficit, and reperfusion covariates? Observational, no use/compliance/edema claim, all assets in hand (public NCCT, follow-up masks, frozen public checkpoint), one load gate plus inference from an answer. It retains the medically real motivation — delayed ground truth may make benchmark error subgroup-dependent — while claiming only what the data can show. The tensor-pattern-sensitivity successor is also registrable but is the weaker of the two; it should compete on current merit, not inherit this card's position.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The proposer has accepted the fatal construct-validity failure and correctly determined that the defensible alternatives change the original claim's identity, so no live disagreement remains about rejecting this idea as posed.

**Argument:** The concession is supported by argument rather than repetition: it accepts that net water uptake is validated as an admission-NCCT lesion measurement (Broocks et al., DOI `10.1161/STROKEAHA.118.020507`) and therefore cannot serve as a mechanically meaningful swelling dose in the winner's post-equalization CTA/perfusion tensor space; it also accepts that changing CSF reserve while holding adjacent parenchyma bit-identical cannot instantiate a physically possible compliance counterfactual. Because ISLES'24 provides neither an independent acute irreversible-injury measurement nor edema, mass-effect, deformation, or pressure ground truth (dataset DOI `10.1148/ryai.250603`), the original deliverable remains unidentifiable. The identity check is also correctly resolved: narrowing to interaction sensitivity between synthetic tensor patterns removes compliance and swelling from the conclusion, while the proposed reserve-stratified error audit asks an observational subgroup-reliability question. Either would be a separate candidate under the 2026-08-10 claim-identity rule, not an amendment to this one. The proposer's clarification that the signed interaction can exclude a purely additive age/atrophy main effect is valid, but does not repair the upstream measurement failure and therefore does not alter the rejection.

**What would change my mind:** Nothing within the present ISLES'24 assets and released winner can repair this card without changing its identity; revival would require the natural paired or source-validated compliance-and-swelling design specified in round 1, including independent mechanical or edema/deformation validation and control of acute injury burden.

**Status:** CONVERGED

## Round 2 — PROPOSER

**Responding to:** The critic states that convergence is reached: my round-1 concession is accepted as argued rather than pro forma, the identity check on both alternatives is judged correctly resolved, and the only recorded disagreement — whether the signed interaction discriminates more than "ordinary nonlinear coupling" — is acknowledged as valid but immaterial to the verdict.

**Response:** CONCEDE

**Argument:** Nothing remains to argue; I confirm convergence rather than restate it. Three closing items of record, none of which reopens the question:

1. **Final disposition.** The idea as posed — does the model use baseline intracranial compliance to expand predicted final-infarct geometry beyond acute tissue injury — is REJECTED for identifiability failure at the measurement-validity level: neither factorial factor can instantiate its construct within the released winner's input space (post-equalization CBF/CBV/MTT/Tmax/CTA, no NCCT; `inference.py:121-125`, commit `bb6c00c8`), and ISLES'24 carries no edema, mass-effect, deformation, or pressure target (DOI `10.1148/ryai.250603`) against which the claim could be validated. This matches the portfolio's IDENTIFIABILITY_FAILURE pattern; what distinguished this card long enough to reach debate was a genuinely novel interaction-based discrimination design, which failed one level upstream of where that design operates.

2. **Revival condition, co-signed.** I adopt the critic's round-1 bar as the ledger's reopen condition: a natural paired or source-validated design in which model inputs encode independently measured compliance differences and mechanically observed swelling or deformation, with acute injury burden held fixed and an external edema, displacement, or pressure measurement giving the manipulated or observed dose its claimed physical meaning. No asset currently in ISLES'24 meets this.

3. **Spin-offs, restated once for the register and not defended here.** (a) The reserve-stratified benchmark error audit (observational; no use, compliance, or edema claim; all assets in hand) — the stronger successor. (b) The tensor-pattern interaction-sensitivity study — registrable but weaker, to compete on current merit. Both enter through the normal scouting pipeline with parent_id idea-035 under the 2026-08-10 claim-identity rule.

**Status:** CONVERGED
