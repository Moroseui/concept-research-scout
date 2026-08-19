# Debate summary — idea 040

## Agreed

- In round 1, both sides agreed that the observational association between patent-vessel tortuosity and prediction error cannot establish that the model uses tortuosity. The age/hypertension association and signed-volume-error analyses can serve only as cheap kill gates, with no positive evidential weight toward the use claim.
- In round 1, both sides accepted the critique-stage repairs: measure only verifiably patent vessels; determine eligible segments from the released occlusion masks; report affected-side exclusions; name thrombectomy difficulty as the leading alternative; adjust for available procedural covariates; replace infeasible narrow strata with prespecified regression and overlap diagnostics; and prohibit vascular-age interpretation without procedural adjustment.
- In round 1, both sides agreed that ISLES'24 alone cannot establish the stronger “long-term pressure-load gauge” interpretation. That requires external validation against age or pressure-related measurements and alternatives such as ancestry, anatomy, and disease subtype.
- In round 2, both sides agreed that the proposed tube-confined CTA straightening edit is invalid. Moving the parent vessel while holding its surroundings fixed necessarily creates broken or distorted branch junctions, altered vessel-to-territory registration, and old-path/new-path tissue artifacts that can explain a model response without tortuosity use.
- In round 2, both sides agreed that a topology-preserving diffeomorphic warp improves on the tube edit by moving connected CTA anatomy together and avoiding copy-and-fill seams. They also agreed that differential attribution would require TI-neutral shams, bidirectional dose controls, quantitative anatomical and image-quality audits, and an honest new resource estimate.
- In round 3, both sides agreed that the CTA-only diffeomorphic edit with chord-axis-rotation shams remains invalid for a multimodal model. TI-changing and sham warps create systematically different CTA-to-NCCT/perfusion registration changes, so an edit-minus-sham response could reflect cross-modal displacement rather than tortuosity.
- In round 3, both sides agreed that no valid rung-1 intervention remains in the current card. The cheap observational screens survive only as kill-only gates, and failure of an intervention must not be reinterpreted as positive observational evidence.
- Across all rounds, both sides agreed that the scientific question and deliverable sentence can remain the same if a valid intervention is later found; the dispute concerned whether the proposed instruments identify that claim.

## Unresolved

### Can a common-warp equivariance design isolate tortuosity use?

- **Proposer's position:** Applying one volume-preserving diffeomorphism to every spatial input, inverse-warping the output, and comparing TI-changing common warps against tissue-deformation-matched TI-neutral common-warp shams is coherent and removes the identified cross-modal registration channel by construction. The proposer did not adopt it because it would be a third intervention redesign and lacks demonstrated precedent and audits.
- **Critic's position:** The critic offered this as a possible route, conditional on quantitative evidence that TI is the only systematic model-visible geometric difference between the edit and sham families. The critic did not claim that such a construction is already feasible or sufficient.
- **What evidence would settle it:** A fresh feasibility review must identify workable precedent or demonstrate the construction directly; specify volume-preserving common warps and inverse-warped output comparison; build TI-neutral shams matched on tissue deformation; and independently test whether caliber, contrast, topology, lesion volume, interpolation burden, and all cross-modal registrations are controlled. A counterexample showing another systematic model-visible difference would reject this route.

### Is there an obtainable natural paired design that changes tortuosity selectively?

- **Proposer's position:** A natural paired acquisition could unblock the rung-1 claim without synthetic-edit confounds, but none was identified in the debate.
- **Critic's position:** A natural pair or validated vascular phantom would settle the selectivity objection if tortuosity varied while the named rival cues were controlled. A phantom may weaken the requirement that ISLES'24 be load-bearing.
- **What evidence would settle it:** Verify an obtainable paired cohort or acquisition in which intracranial tortuosity differs while lumen caliber, contrast filling, occlusion, perfusion, collateral topology, and other visible vascular-age cues are sufficiently controlled, and show how ISLES'24 remains essential to the test. No such evidence is currently in hand.

### Should the two kill-only observational screens be run while the causal arm is paused?

- **Proposer's position:** Yes, if the verdict stage wants them. Patent-vessel TI versus released age and hypertension, followed by signed-volume-error regression, are cheap and can terminate the idea before intervention development.
- **Critic's position:** The critic accepted their limited feasibility and falsification value but maintained that neither a positive nor a null observational result establishes model use or long-term pressure load; TICI-based range restriction also weakens the null.
- **What evidence would settle it:** This is mainly a resource-allocation judgment. Stage 0 measurements of patent-vessel recovery, TI reliability and variance, procedural-covariate availability, and the exact compute needed for leakage-free out-of-fold predictions would quantify cost and kill power, but the human must decide whether a kill-only screen merits effort while the positive test has no validated design.

## Positions that moved

- **Proposer, round 1:** Accepted that the original observational arm had no positive evidential force toward model use and reclassified both observational analyses as kill-only gates. This was earned by the critic's use-versus-association argument and explicit rival explanations.
- **Critic, round 2:** Accepted that the round-1 amendments preserved claim identity in form and that a selective intervention could still answer the original question. This movement was earned by retaining the deliverable sentence while making the observational arms explicitly nonconfirmatory.
- **Proposer, round 2:** Conceded that the tube-confined straightening edit was invalid. This was earned by the critic's demonstration that branch continuity, unchanged surroundings, and seam-free tissue handling cannot all hold when the vessel path moves.
- **Critic, round 3:** Accepted that the compactly supported diffeomorphism better addressed within-CTA topology and seam defects than the tube edit. This movement was earned by moving the parent vessel, branches, and adjacent CTA anatomy under one invertible field.
- **Proposer, round 3:** Conceded that the CTA-only diffeomorphic edit and chord-axis sham fail to isolate tortuosity in the multimodal input. This was earned by the critic's new demonstration that straightening and bend rotation create different vessel-displacement fields relative to fixed perfusion and NCCT anatomy.
- **Proposer, round 3:** Declined a third in-debate redesign and accepted PAUSE. This followed the exact failure condition the proposer had stated in round 2, so it was not unearned capitulation.
- No concession was UNEARNED.

## Amendments made

At round zero, the card proposed bilateral MCA-plus-basilar TI, narrow-stratum observational residual analysis, and an unspecified later geometry-preserving counterfactual. It suggested that the observational result could justify building the intervention, while leaving the model, signed error quantity, procedural pathway, and intervention mechanics insufficiently specified.

The agreed revision measures TI only on vessels verifiably patent at CTA, uses released occlusion masks to define per-case segment eligibility, reports exclusion rates, and treats thrombectomy difficulty as the leading alternative mechanism. Its observational endpoint is prespecified signed volume error with regression adjustment and overlap diagnostics; available mTICI grade, pass count, and procedure-time variables must be checked and used where present. The age/hypertension association runs first and the residual regression second, but both are kill-only and cannot support a use claim. No vascular-age interpretation is allowed without procedural adjustment, and long-term pressure-load interpretation remains prohibited without external validation.

Both proposed positive instruments were lost. The tube edit was abandoned because it creates topology and tissue artifacts. The CTA-only diffeomorphic warp with displacement-matched chord-axis shams was abandoned because it creates unmatched cross-modal registration changes. The intervention cost is no longer credibly 2–3 weeks, the original under-10-GPU-hour model-analysis estimate remains unreconciled until a model and fold plan are named, and the current card has no valid path to rung 1. A common-warp equivariance experiment remains a possible unblock within the same claim, but it requires a fresh feasibility review rather than another debate amendment.

## Recommendation

**PAUSE.** The single most important thing the human should inspect is whether a volume-preserving common-warp equivariance protocol can be made genuinely selective: after every spatial channel is warped together and the output is inverse-warped, can TI-changing and TI-neutral deformation families be matched closely enough that tortuosity is the only systematic model-visible difference? If not, this idea has no positive test inside the available design and the observational screens should not be allowed to substitute for one.

## In plain terms

This idea asks whether a stroke model reads how winding the brain's arteries are as a clue to vascular aging and years of pressure stress. It would need to change artery winding while keeping every other clue the model sees effectively unchanged.

The debate concluded that simple statistical associations cannot show model use, and that both proposed image edits introduce other changes the model could detect. The idea is therefore paused, although cheap statistical screens could still kill it early and a carefully validated whole-image warping method might eventually reopen it. The human is being asked to judge whether that whole-image method is realistic enough to deserve a fresh feasibility review.

```json
{"verdict": "PAUSE", "unblock": "Validate, through fresh feasibility and independent counterexample review, a volume-preserving common-warp equivariance protocol with TI-neutral deformation-matched shams that leaves tortuosity as the only systematic model-visible between-family difference, or obtain a selective natural paired design."}
```
