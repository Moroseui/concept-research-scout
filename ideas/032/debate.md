# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed CTA-only graph edit cannot identify whether the model uses Circle-of-Willis redundancy as collateral reserve because it creates a physiologically contradictory case by changing the putative route while freezing distal CTA enhancement and perfusion.

**Argument:** The original question is about a functional reserve for maintaining flow, not merely sensitivity to communicating-artery-shaped bright voxels. Yet the intervention adds or removes an Acom/Pcom-like route while holding fixed the downstream evidence through which a patent route has meaning. In acute occlusion, static single-phase CTA cannot reliably establish flow direction or functional collateral filling: Frölich et al. found markedly greater sensitivity for time-resolved 4D CTA than single-phase CTA for distinguishing antegrade from retrograde collateral filling (DOI 10.1161/STROKEAHA.112.668889). A positive response would therefore show sensitivity to the rendered CTA structure, while a null could mean either non-use or rational deference to the unchanged CTP/distal CTA channels. Volume-matched shams do not repair this because they cannot match anatomical junctions, route length, location, and cross-modal consistency while differing only in connectivity. This is an identity-level problem for any proposed repair: a branch-fidelity audit or observational graph-outcome analysis could be valuable, but neither answers the original within-case model-use question and must be a separate candidate.

**What would change my mind:** Show a validated patient-conditioned counterfactual method that jointly produces mutually consistent proximal CTA topology, time-resolved or otherwise flow-informative distal vascular evidence, and perfusion consequences, plus an intervention analysis that isolates the incremental effect of alternate-path redundancy from the jointly changed hemodynamic variables; alternatively, narrow the claim to model sensitivity to a prespecified CTA graph feature and register that changed deliverable as a new candidate.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The graph edit cannot identify use of collateral reserve because the design's central move — changing the putative alternate route while freezing distal CTA enhancement and every perfusion map — manufactures a cross-modally contradictory input. A positive response therefore demonstrates only sensitivity to a rendered communicating-artery-shaped structure; a null is ambiguous between non-use and rational deference to the unchanged downstream channels; and shams cannot match anatomy while differing only in connectivity.

**Response:** CONCEDE

**Argument:** The objection is correct, and I have no new evidence or argument against it. Three points make this unrepairable within the original question rather than merely difficult.

First, the contradiction is constitutive, not incidental. The card's own `use_vs_association` field defines the intervention as preserving "the occlusion, distal CTA enhancement, brain images, and perfusion maps" — that freeze IS the isolation strategy. But for a multimodal model consuming CTA alongside perfusion maps, the downstream channels already encode the hemodynamic consequences a patent route would have. Editing the route while pinning its consequences creates an input off the joint data manifold in exactly the dimension under test. Isolation and physiological coherence are mutually exclusive here by construction; I cannot amend one without surrendering the other. The critic's two escape routes confirm this: a jointly consistent hemodynamic counterfactual no longer isolates topology (the incremental effect of redundancy is confounded with everything co-generated), and the sensitivity-only narrowing changes the deliverable sentence.

Second, the premise fails upstream of the intervention. The Frölich result (DOI 10.1161/STROKEAHA.112.668889: single-phase CTA 40% sensitivity vs 4D CTA 100% for antegrade-vs-retrograde collateral filling) means a static bright lumen does not carry functional-patency information even in unedited images. So "patent alternate path" as read from single-phase CTA is not a valid marker of hydraulic reserve observationally, before any synthetic edit is layered on. The deliverable sentence — "using Circle-of-Willis alternate-path redundancy as an image marker of proximal collateral reserve" — embeds a physiological gloss the source modality cannot support. The keystone screen independently narrowed the same wound: the only published mask-fidelity evidence on this cohort excluded occluded-CoW cases, so the edit substrate is weakest exactly where the question lives.

Third, the identity check forbids the surviving repair. The only defensible residue is "the model is sensitive to a prespecified CTA graph feature," which drops collateral reserve from the claim. Under the claim-identity rule of record (2026-08-10, idea 015): when the deliverable sentence changes, the idea is REJECTED (superseded) and the successor registers as a new candidate with `parent_ids` — it does not proceed as an amendment. And that residue is scientifically thin on its own; it should compete on current merit, not inherit this idea's queue position.

Spin-offs (noted, not defended here; both must enter as new candidates through normal scouting):
1. **Mask branch-fidelity and stability audit** (from the critique's §8 and the keystone screen's residual): are the released automatic CoW masks branch-faithful and resampling-stable, stratified by CoW-involving versus distal occlusion? No checkpoint or GPU needed; gates every downstream graph idea; requires a small, honestly declared expert-reference set.
2. **CTA graph-feature sensitivity claim** (the critic's narrowing): registerable with `parent_ids: ["isles24-scout-003-c03"]` only if a proposer can articulate why sensitivity-without-physiology is worth having; I do not assert that it is.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The proposer has established that the original collateral-reserve question is not identifiable with the proposed ISLES'24 inputs and that every defensible narrowing changes the claim's identity.

**Argument:** I concede because the response does more than accept the objection: it identifies the exact incompatibility between physiological coherence and the proposed isolation strategy. Holding perfusion and distal CTA evidence fixed makes the topology edit cross-modally contradictory, while jointly changing those consequences would no longer isolate alternate-path redundancy. The additional modality argument is decisive: the cited single-phase CTA evidence does not support treating a visible communicating-artery lumen as functional patency or hydraulic reserve, so the original deliverable fails even before synthetic editing. Finally, the proposer correctly applies the repository's claim-identity rule: a branch-fidelity audit or a CTA graph-feature sensitivity study would answer a different question and must enter as a separate candidate rather than repair idea 032. No remaining amendment preserves the original question, and the proposed spin-offs are explicitly not being smuggled in as revisions.

**What would change my mind:** A new primary-source-validated measurement available for the same ISLES'24 cases that establishes patient-specific functional flow through the communicating arteries, together with an intervention or natural design that separates alternate-route redundancy from its downstream hemodynamic consequences; absent that changed evidence condition, the original candidate should remain rejected.

**Status:** CONVERGED

## Round 2 — PROPOSER

**Responding to:** The critic accepts the round-1 concession in full and states the terminal position: the collateral-reserve question is not identifiable with ISLES'24 inputs, every defensible narrowing changes the claim's identity, and the candidate should remain rejected absent a specific changed evidence condition.

**Response:** CONCEDE

**Argument:** My round-1 concession stands; the critic's round 2 introduces no new point requiring argument, and I do not restate the agreement already reached. Two closing records only. (1) Outcome for the ledger: idea 032 (isles24-scout-003-c03) is REJECTED, kill code IDENTIFIABILITY_FAILURE — the freeze that constitutes the isolation strategy is also what makes the edited input cross-modally contradictory, and single-phase CTA cannot carry the functional-patency semantics the deliverable sentence requires. (2) Revisit trigger of record, adopted verbatim from the critic's round 2: a primary-source-validated, per-case measurement of functional communicating-artery flow for the same ISLES'24 cases, together with an intervention or natural design that separates alternate-route redundancy from its downstream hemodynamic consequences. The two round-1 spin-offs (the mask branch-fidelity/stability audit; the CTA graph-feature sensitivity claim) remain unregistered here and enter, if at all, through normal scouting with `parent_ids: ["isles24-scout-003-c03"]`, with no inherited queue position; I continue not to assert that the second is worth registering.

**Status:** CONVERGED
