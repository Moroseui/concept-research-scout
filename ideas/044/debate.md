# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed intervention cannot answer the original question because a response to removing a contralateral cavity does not identify reduced brain reserve as the model's interpretation of that cue.

**Argument:** The card asks whether chronic infarct cavities are used "as a marker of reduced brain reserve," yet its own identifiability score and confound list concede that the same paired response could arise because the cavity is an age proxy, a generic marker of prior vascular disease, or simply a learned NCCT morphology associated with final-infarct labels. Holding the acute lesion and perfusion inputs fixed isolates sensitivity to the edited NCCT appearance; the CSF and parenchyma shams can rule out generic filling or boundary effects. Neither operation distinguishes reserve from those other patient-level meanings. ISLES'24 supplies admission imaging and follow-up-infarct ground truth, but no independent reserve measurement or perturbation, so even a clean positive result supports only use of contralateral chronic-cavity-like appearance. The proposed critique repair that drops "brain reserve" remains the same operational estimand and is a defensible narrowing, but until the actual question, deliverable, suspected-signal claim, and pitch are narrowed together, the live study overclaims what it tests.

**What would change my mind:** Either revise the card consistently so its claim is limited to NCCT-channel use of contralateral chronic-cavity-like tissue loss, with reserve explicitly left unestablished, or add an independently validated reserve measurement or intervention and a prespecified contrast that separates reserve-mediated responses from age and prior-vascular-disease proxy responses.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The design measures whether the model's affected-hemisphere forecast responds to editing out contralateral cavity-like tissue loss in the NCCT channel — nothing more. It cannot distinguish a reserve interpretation from an age proxy, a prior-vascular-disease proxy, or a bare learned morphology-label association, and ISLES'24 contains no independent reserve measurement that could supply that discrimination. Yet the live card carries "brain reserve" in the question, the deliverable sentence, the suspected-signal claim, and the pitch, so the study as registered overclaims what its own intervention tests.

**Response:** AMEND

**Argument:** The objection is correct on the substance and I will not defend the reserve wording; the card's own identifiability rationale ("cavity use but not whether the model interprets it as reserve or age") already concedes it, and the critique reached the same verdict independently. The second branch of the critic's resolution — adding an independently validated reserve measurement — is not available inside ISLES'24 and would be a different study; per the idea-023 precedent (decisions.md, 2026-08-17), physiological naming on top of an operational estimand requires challenge- or validation-based grounding in a successor, not a rider on this card. So I take the first branch, in full and jointly across every surface the critic listed:

1. **Question** becomes: "Is the frozen final-infarct model using contralateral chronic-cavity-like tissue loss in the admission-NCCT channel when forecasting new infarction?"
2. **Deliverable sentence** becomes: "The final-infarct model is using remote chronic-cavity-like tissue loss on admission NCCT when forecasting new infarction." No reserve clause.
3. **Suspected signal** retains the reserve physiology only as motivation for why such a cue could exist, with an explicit sentence that reserve, age-proxy, and prior-vascular-disease readings are observationally equivalent under this design and none is established by any outcome.
4. **Prohibited conclusions** gain an entry: a positive result may not be described as evidence that the model measures brain reserve, patient age, or vascular-disease burden; it demonstrates NCCT-channel use of contralateral cavity-like appearance only.
5. **Plain pitch** drops "treats the patient as more vulnerable" in favor of "asks whether that old-looking damage changes the forecast," and "that old damage" becomes "that old-looking damage" so the etiology hedge survives translation.

The estimand is scoped to the NCCT channel explicitly (the critic's own phrase "NCCT-channel use" is adopted), which also aligns the claim with the critique's separate cross-channel finding: the cavity persists in the perfusion maps, so a null licenses "does not use the NCCT-channel appearance," never "does not use the cavity."

**Identity check:** the revised design answers the revised question with the identical intervention, shams, endpoint, gates, and paired analysis; nothing operational changes. Under the claim-identity rule (2026-08-10) this is a narrowing that deletes an interpretive rider while the measured contrast and the prohibited-conclusions direction are preserved and strengthened — revision-in-place, not a successor. The rule's REJECT trigger is a change of deliverable identity; here the deliverable sentence loses an adjective phrase the design never had the right to assert.

**What is lost:** real value, and it should be priced. The reserve interpretation was the bridge from this experiment to a physician-legible vulnerability story, and it carried part of `medical_relevance: 4` and `interest: 4`; both scores should be re-argued at revision (interest also owes a debit to the critique's low-prior finding). What survives is the load-bearing part: whether a final-infarct model consults remote old-looking damage at all is a citable fact about model behavior — for transportability across cohorts with differing chronic-lesion prevalence and for auditing what these models actually read — whichever interpretation later wins. Reserve-as-mechanism is recorded as a potential successor requiring independent physiological grounding (e.g., a cohort with a validated reserve construct), not as a spin-off registered now.

This is amendment 1 of this debate; it converges with, and does not substitute for, the critique's other required revisions (frozen-model pin, NCCT-sensitivity ablation gate, donor-exclusion rule, power-derived census gate), which stand for the revision stage.

**Status:** CONVERGED

## Round 3 — CRITIC

**Position:** The amendment changes the claim's identity: NCCT-channel sensitivity to cavity-like appearance does not answer the original question of whether the model uses chronic infarct cavities as a reduced-brain-reserve signal.

**Argument:** The proposer's operational concession is scientifically correct but its governance conclusion is not. The 2026-08-10 claim-identity rule in `evidence/decisions.md` states that revision-in-place is allowed only when the deliverable claim remains the same, and that changing the deliverable sentence or the prohibited-conclusions set requires rejecting the original idea as superseded and registering a new candidate. This amendment does both: it removes the causal/physiological predicate "as a brain-reserve signal" from the deliverable and newly prohibits precisely that conclusion. That phrase is not an expendable adjective; it distinguishes the original mechanism claim from the replacement's morphology-sensitivity claim. The unchanged intervention cannot rescue identity, because the critic's first round established that this intervention never identified reserve in the first place. The replacement is worth considering, but approving it in place would make idea 044 appear to have survived debate after abandoning the question that defined it.

**What would change my mind:** Either show an independently validated reserve measurement or intervention that makes the paired contrast distinguish reserve use from age, vascular-disease burden, and bare morphology-label association while retaining idea 044, or reject idea 044 as superseded and register the NCCT-channel cavity-appearance study as a new candidate with `parent_ids` linking it to idea 044.

**Status:** OPEN

## Round 4 — PROPOSER

**Responding to:** My round-2 amendment changed both the deliverable sentence and the prohibited-conclusions set — exactly the two triggers the 2026-08-10 claim-identity rule names for REJECTED (superseded) plus registration of a new candidate with `parent_ids`. Calling that a revision-in-place would let idea 044 appear to survive debate while abandoning the reserve question that defined its registration.

**Response:** CONCEDE

**Argument:** The critic is right, and my round-2 identity check was wrong. Two points settle it against me:

1. **The letter of the rule, and its founding case.** The 2026-08-10 rule triggers on "when the deliverable sentence or the prohibited-conclusions set changes." Round 2 did both and itemized the changes. My defense was that the deleted phrase is "an adjective phrase the design never had the right to assert" — but that is an argument the rule's founding case already heard and rejected. Idea 015 lost precisely an interpretive physiological rider (the vascular-age reading) sitting on top of an operational contrast (the BAC-response experiment) that survived unchanged, and the ruling was REJECTED (superseded), with the successor re-entering through a normal scouting cycle, receiving its own novelty audit, and holding no inherited queue position. Reserve-on-top-of-cavity-edit is structurally identical to vascular-age-on-top-of-BAC-response. Relitigating the rule's founding case from inside a debate is not a rebuttal.

2. **The precedent I leaned on does not carry the weight I put on it.** Idea 023's claim-language reduction (decisions.md, 2026-08-17) happened at a human-inspection stage: the operator answered the debate's question, fixed the claim language, and ratified the binding disclaimer. Whatever tension exists between that disposition and the 2026-08-10 rule is the operator's to resolve, not a proposer's to exploit; the debate cannot self-award a dispensation the operator granted case-specifically elsewhere. For its own disposition the debate has only the written rule, and the written rule says supersede. I flag the tension explicitly for the decision stage: if the operator regards 023-style language reduction as legitimate revision-in-place, they may overrule this concession; the default disposition follows the rule.

**Recommended disposition:** idea 044 REJECTED (superseded). This is not a defect of the experiment — no fatal objection was found; the intervention, shams, endpoint, gates, and census-first economics all stand — but of the claim the card was registered to deliver, which round 1 established the design never could deliver.

**Spin-off (recorded, not registered):** the NCCT-channel cavity-appearance study, exactly as specified in round 2 items 1–5 (narrowed question and deliverable, reserve demoted to suspected-signal motivation with the observational-equivalence sentence, expanded prohibited conclusions, corrected plain pitch), carrying the critique's five revision pins (frozen-model path with a numeric performance gate; NCCT-sensitivity ablation gate preceding any paired run; donor-exclusion rule for mirrored sampling; power-derived editable-case census over all 149 public cases replacing the 15-of-30 prevalence fraction; CSF sham designated as the cross-channel mismatch control), with `parent_ids: ["isles24-scout-005-c02"]`. Per the 2026-08-10 rule and the S2 note of the same date, it re-enters through a normal scout cycle or librarian proposal — not manual registration here — and is re-ranked on current merit. The reserve-mechanism question itself remains a further, distinct successor requiring a cohort with an independently validated reserve construct.

**What is lost:** the shortlist slot and queue position. The successor competes fresh against a backlog in which the critique's low-prior finding will rightly count against it. That is the rule working as intended, and conceding now — one round after the governance objection — costs less than defending a disposition the ledger already forecloses.

**Status:** CONCEDED

## Round 5 — CRITIC

**Position:** The proposer has resolved my objection by conceding that idea 044 must be rejected as superseded rather than revised in place.

**Argument:** The concession is supported by a governance argument, not mere agreement: it applies the explicit 2026-08-10 claim-identity triggers to the amendment's changed deliverable sentence and prohibited-conclusions set, and it identifies the founding idea-015 disposition as structurally analogous. The proposer also correctly withdraws the attempted reliance on idea 023 because that was a case-specific human ruling, not authority for this debate to waive the standing rule. The resulting disposition preserves the scientific distinction established in round 1: ISLES'24 has no independent reserve measurement, so the registered brain-reserve claim remains untestable by the proposed NCCT edit, while the narrower cavity-appearance experiment is a different candidate that may re-enter with lineage and fresh review. I have no remaining objection to that disposition; the successor's frozen-model, sensitivity, donor, census, and mismatch-control requirements are appropriately recorded for its own pipeline rather than used to rehabilitate idea 044.

**What would change my mind:** Only an independently validated reserve measurement or intervention that distinguishes reserve-mediated model behavior from age, vascular-disease burden, and bare cavity-morphology association would justify retaining the original idea 044 claim.

**Status:** CONCEDED

## Round 6 — PROPOSER

**Responding to:** The critic has no remaining objection: my round-4 concession — idea 044 REJECTED (superseded) under the 2026-08-10 claim-identity rule, with the narrowed NCCT-channel cavity-appearance study recorded as a lineage-linked successor rather than a rehabilitation of this card — is accepted as the disposition.

**Response:** CONCEDE

**Argument:** The concession stands; I have no new argument and none is needed. This round only fixes the closed state of the debate so the decision stage inherits it cleanly:

1. **Disposition:** idea 044 REJECTED (superseded). The registered claim — cavity use *as a brain-reserve signal* — was established in round 1 as untestable by the proposed intervention within ISLES'24, and the round-2 amendment that repaired the overclaim changed both the deliverable sentence and the prohibited-conclusions set, which are exactly the supersession triggers of the 2026-08-10 rule and its founding idea-015 case.
2. **Successor path:** the NCCT-channel cavity-appearance study as specified in round 2 items 1–5, carrying the critique's five revision pins (frozen-model path with numeric performance gate; NCCT-sensitivity ablation gate before any paired run; donor-exclusion rule; power-derived editable-case census over all 149 public cases; CSF sham as the cross-channel mismatch control), with `parent_ids: ["isles24-scout-005-c02"]`. It re-enters through a normal scout cycle or librarian proposal, not manual registration, and is re-ranked on current merit — including the critique's low-prior finding counting against it.
3. **Flag preserved for the operator:** the recorded tension between this disposition and the idea-023 claim-language reduction (decisions.md, 2026-08-17) remains for the decision stage; the default follows the written rule, and only the operator may rule otherwise.
4. **For the record:** no fatal objection to the experiment itself was found at any point — the intervention, shams, endpoint, gates, and census-first economics survived critique and debate intact. What died was the claim the card was registered to deliver.

**Status:** CONVERGED
