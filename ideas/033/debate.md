# Debate transcript

## Round 1 — CRITIC

**Position:** The experiment cannot identify the card’s original claim that the model treats gray–white attenuation loss as a map of already injured tissue, because every proposed response is equally compatible with use of a prognostic baseline severity cue for later infarction.

**Argument:** ISLES’24 supplies acute NCCT but trains and evaluates against follow-up MRI-derived lesion masks after treatment and disease evolution (arXiv:2408.10966); it does not supply an acute irreversible-tissue reference. Selective latent erasure, input-space contrast restoration, preserved perfusion decodability, random-direction controls, center replication, and even a positive NCCT-versus-perfusion ablation could establish sensitivity to the named attenuation measurement, but none separates two mechanisms that make the same prediction under this target: the model reads already irreversibly injured tissue, or it reads a continuous early-ischemic-severity feature associated with eventual fate. The adjacent evidence does not bridge that gap: Takahashi et al. relate contralateral densitometry to ASPECTS, baseline severity, and outcomes (PMID 26158082), while Reidler et al. compare relative HU with a CTP-threshold-defined core surrogate (DOI 10.1148/radiol.2019182041). The card’s own caveat forbidding an irreversible-core claim conflicts with its question and deliverable sentence, which explicitly say “already injured” and “acute-tissue-injury signal.” Recasting the endpoint as measurement-level model use would be scientifically defensible, but it changes the deliverable claim’s identity and therefore requires a separate successor under the repository rule.

**What would change my mind:** Show an obtainable, acquisition-time tissue-viability reference independent of the follow-up infarct mask—for example, validated acute tissue fate under a design that separates baseline irreversible injury from salvageable tissue—and prespecify a contrast-response test that discriminates those states; otherwise register the narrower attenuation-measurement use study as a new candidate.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** ISLES'24 contains no acquisition-time tissue-viability reference — its only supervision is the follow-up-MRI-derived lesion mask after treatment and evolution — so every intervention the card proposes (selective erasure, contrast restoration, decodability preservation, random-direction controls, center replication, NCCT-vs-perfusion ablation) is equally consistent with two mechanisms: the model reads tissue that is already injured, or the model reads a continuous baseline severity cue prognostic of eventual infarction. Since the card's question and deliverable sentence commit to "already injured" / "acute-tissue-injury signal," the defensible measurement-level study is a successor under the claim-identity rule, not a repair.

**Response:** CONCEDE

**Argument:** The objection is correct, and I concede in round one rather than defend it across rounds. Before conceding I tested the two strongest available defenses; both fail, and stating why they fail is the useful content of this round.

*Defense 1 (semantic): "already injured" need not mean "irreversibly infarcted."* Cytotoxic edema — the accepted cause of gray–white differentiation loss — is by definition a state of presently injured tissue, and that pathophysiology is established by prior literature, not something this experiment must prove. The defense fails anyway, because the deliverable sentence attributes the injury reading to the *model*, and the model's dependence on the contrast measurement can only have been learned through its association with the follow-up outcome label. What the sign means in patients is an external fact; what the model uses it *as* is the claim, and the "injury" content of that claim is precisely the part no ISLES'24-internal test can reach. Prior literature cannot close the gap either: as the critic notes, Takahashi et al. (PMID 26158082) validates against ASPECTS/severity/outcome, and Reidler et al. (DOI 10.1148/radiol.2019182041) against a CTP-thresholded surrogate — neither supplies acquisition-time tissue fate.

*Defense 2 (spatial coupling): the region-specific endpoint distinguishes map-like use from a scalar severity cue.* True but insufficient: a spatially resolved severity feature predicts exactly the same region-specific response to a regional contrast edit as an injury map does. Spatial coupling separates "map" from "global scalar"; it cannot separate "map of present injury" from "map of predicted fate." The residual difference between the two mechanisms is temporal (tissue state at acquisition versus tissue destiny), and the dataset contains no acquisition-time reference to test it — the keystone screen's verified facts (arXiv:2408.10966: lesion masks derived from follow-up MRI via DeepISLES) confirm this rather than soften it.

I also note convergence: the independent critique on file reached the same fatal objection ("repairable without changing the question? NO") before this debate opened. Two independent analyses agreeing on the identical identifiability gap is itself evidence the gap is structural, not presentational.

*Identity check:* any amendment that deletes "already injured" and "acute-tissue-injury signal" changes the deliverable sentence, and under the 2026-08-10 claim-identity rule that is REJECT (superseded) plus a new registration, not an amendment. So no AMEND is submitted. What is lost is real: the card's medically compelling framing — that the model reads the radiologist's early-injury sign *as* injury — was the claim; the surviving question is narrower and must re-earn its queue position on its own merit.

**Spin-off** (recorded, not defended here):

1. *Measurement-level use audit* (successor, parent idea-033): does a reproduced NCCT+perfusion final-infarct model respond region-specifically to the prespecified mirrored ASPECTS-region gray–white HU-contrast measurement, with no tissue-state interpretation attached? Any registration should inherit the critique's repairs: fully specified input-space edit operator first, latent erasure demoted or dropped, synthetic positive control, replicated twins, prespecified NCCT-increment gate.
2. *Model-free incremental-information test* (already proposed as a separate candidate in critique.md): does the attenuation-contrast measurement add center-held-out information about regional follow-up infarct involvement beyond the released perfusion-map summaries?
3. *Path back to injury language, for the record:* the critic's "what would change my mind" is an acquisition-time viability reference, which ISLES'24 does not contain. One partial alternative worth one line: if the ISLES'24 clinical table includes reperfusion success (e.g., mTICI — to be verified against the data descriptor, not assumed), tissue that shows the sign and infarcts *despite* documented complete reperfusion behaves like baseline injury, while sign-positive tissue that infarcts only under failed reperfusion behaves like an at-risk marker. That is an observational, confounded design (time-to-treatment, severity) and a different experiment from this card — an ingredient for a successor's design debate, not a rescue.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The proposer’s concession resolves the debate: idea 033’s original injury-state claim is not identifiable with ISLES’24 and must be rejected rather than amended.

**Argument:** The argument that moved me is the proposer’s explicit separation of spatial form from temporal meaning: a region-specific response can distinguish a map-like cue from a global scalar, but it cannot distinguish a map of tissue state at acquisition from a map of later tissue fate. That directly accepts the load-bearing objection and is consistent with the verified target provenance—follow-up-MRI-derived lesion masks, not an acquisition-time viability reference (arXiv:2408.10966). The identity check also passes cleanly: no amendment was offered, and the proposer correctly recognizes that deleting “already injured” and “acute-tissue-injury signal” changes the original question and deliverable sentence. The two narrower studies are therefore potential successors with `parent_ids` pointing to idea 033, not repairs to this card. There is no remaining objection worth debating within the original claim because both sides now agree that its decisive missing evidence is absent from the dataset.

**What would change my mind:** An obtainable acquisition-time viability reference, independent of the follow-up infarct mask, together with a prespecified test that separates already-injured from salvageable sign-positive tissue could justify registering a new injury-state candidate; it would not retroactively turn the proposed measurement-level successors into amendments of idea 033.

**Status:** CONVERGED

## Round 2 — PROPOSER

**Responding to:** The critic accepts the round-1 concession, finds the identity check clean, and declares the debate resolved: idea 033 is to be rejected, with the narrower studies entering only as successors carrying `parent_ids`.

**Response:** CONCEDE

**Argument:** The concession stands; nothing in the critic's closing round is contested, and I will not re-argue agreement. Three closure facts for the record, none of which reopens the debate:

1. *Recommended kill code:* IDENTIFIABILITY_FAILURE. The design cannot separate "map of tissue state at acquisition" from "map of predicted tissue fate" because the discriminating reference (acquisition-time viability, independent of the follow-up mask) is absent from ISLES'24 — the same structural class as ideas 028, 029, 030, and 032, and the ledger's most frequent failure mode under this charter. What distinguishes 033's death from those is only that the missing evidence is temporal rather than acquisitional; the pattern match should be recorded so future scouts proposing NCCT-sign "use" claims against follow-up-supervised targets are checked against it at generation time, not after three stages.

2. *Successor scope, restated once precisely so registration does not drift:* spin-offs 1 and 2 from my round-1 entry inherit the critique's repairs verbatim (input-space edit operator fully specified before any latent method, synthetic positive control, replicated twins, prespecified NCCT-increment gate; and for spin-off 2, the targeted novelty audit of the exact center-held-out follow-up-region endpoint that the critique made a promotion condition). Neither successor may reuse the words "injured," "injury," or "tissue state" in its deliverable sentence; that is the boundary this debate established.

3. *Revisit trigger, matching the critic's:* a validated acquisition-time viability reference obtainable for an NCCT cohort — or the mTICI-stratified partial design from my round-1 note, if the ISLES'24 clinical table is verified to contain reperfusion grades — would justify a **new** injury-state candidate, not a reopening of this card.

Both sides now agree on verdict, mechanism of failure, and successor handling. The debate is closed.

**Status:** CONVERGED
