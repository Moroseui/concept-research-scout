# Debate transcript

## Round 1 — CRITIC

**Position:** The experiment cannot answer the original oxygen-carrying-capacity question; its strongest identifiable result is only sensitivity to edited dural-sinus intensity, which is a different claim and therefore a separate candidate.

**Argument:** Black et al. (DOI 10.3174/ajnr.A2504; PMID 21566009) support an association between unenhanced venous-sinus HU and contemporaneous hematocrit/hemoglobin, but that population-level measurement association does not identify what a final-infarct model means by sinus HU. A monotone output response to texture-preserving sinus edits would still be compatible with use of scanner calibration, reconstruction or site signatures, skull-adjacent boundary structure, or a remote brightness shortcut; within-case edits and anatomical shams can narrow these alternatives but cannot turn the response into evidence that the model uses HU *as a proxy for oxygen-carrying capacity*. The card exposes the contradiction itself: its rung-1 limit says “use of sinus attenuation, not a claim of measured anemia,” while its question and deliverable sentence assert proxy semantics and oxygen carrying capacity. Amending the deliverable to regional-intensity sensitivity would cross the repository's claim-identity boundary. Moreover, the released winning system cannot rescue the interpretation: Ren et al. (arXiv:2505.18424v2, Table 1 and Methods 3.2–3.3) excludes NCCT from the final input set, and the official implementation at commit `bb6c00c8a58cb57a5a33c133c02885776673d230` constructs inference inputs from CBF, CBV, MTT, and Tmax. Training a new NCCT-inclusive model may make an intensity-sensitivity study executable, but it does not repair this semantic non-identifiability.

**What would change my mind:** Show, in a frozen NCCT-inclusive final-infarct model evaluated on an untouched treatment-characterized cohort, that measured admission hemoglobin and oxygen saturation predict the model's sinus-HU response conditional on acquisition/site, perfusion, reperfusion, and time, and that replacing sinus HU with the subject's laboratory-implied value mediates the model response while matched nonhematologic intensity edits do not; also show that this cohort is concretely linked to ISLES'24 so the dataset remains load-bearing. Without that evidence, the oxygen-proxy claim must be rejected and any sinus-intensity-use audit registered separately.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The strongest result this design can produce — a monotone, sham-surviving output response to within-case sinus-intensity edits — identifies only sensitivity to the edited region, never that the model treats sinus HU *as a proxy for oxygen-carrying capacity*. The deliverable sentence asserts the proxy semantics anyway; narrowing it to intensity sensitivity would change the claim's identity; and the released winning pipeline cannot even see the sinus (NCCT excluded from its inputs, SynthStrip-masked away), so no existing checkpoint carries the question.

**Response:** CONCEDE

**Argument:** The objection is correct, and it is correct in a way the card itself pre-registered. Three points, none of which I can answer with new evidence:

1. **The semantic gap is intrinsic to the design, not a repairable gate.** Every arm of the proposed intervention — dose response, skull and extracranial-vein shams, site stratification, noise normalization — discriminates *where* and *how strongly* the model responds, never *what the scalar means to it*. The card's own rung ladder admits this: rung 1 is "use of sinus attenuation, not a claim of measured anemia," and rung 2 requires measured hematocrit in an external cohort. The keystone screen (2026-08-18) confirmed the release documents no hematocrit or hemoglobin field, so rung 2 is unreachable inside ISLES'24 by construction; and once an external laboratory cohort becomes the evidential engine, ISLES'24 is no longer load-bearing, which fails the charter's second criterion for the very claim that makes the candidate interesting. The question cannot be answered with the dataset, and the question that can be answered with the dataset is not this question.

2. **The card contains its own kill condition, and the critic has triggered it.** Under `cross_domain.what_changes_if_dropped` the card states: "Without the hematology link, the experiment becomes an uninteresting remote-intensity shortcut audit and should be killed." Round 1 establishes that the hematology link cannot be carried by any evidence obtainable within this design. The identity check on AMEND forbids the only available dodge: rewriting the deliverable sentence from "image proxy for oxygen-carrying capacity" to "sensitive to dural-sinus intensity" is a change of claim identity under the 2026-08-10 rule (idea-015 precedent), so it must be a successor registration, not an amendment. I decline to submit that amendment and concede instead.

3. **The model-asset facts are verified and undisputed.** Ren et al. (arXiv:2505.18424v2, Table 1) list CTA, CBF, CBV, MTT, and Tmax as the final inputs — no NCCT — and the official `inference.py` (commit `bb6c00c8a58cb57a5a33c133c02885776673d230`, lines 121–124) builds four inference channels from perfusion maps only; Methods 3.2 applies SynthStrip brain masking that removes the dural sinuses from the field entirely. Mode C tolerates the resulting feasibility cost (training a new NCCT-inclusive model), but feasibility was never the fatal axis; even a purpose-trained model inherits point 1 unchanged.

**Spin-off (for separate registration, not defended here):** The critique's constructive alternative is the honest version of the motivating physiology and should enter as a new candidate with `parent_ids: ["isles24-scout-003-c04"]`: in a treatment-characterized acute-stroke cohort with admission hemoglobin and oxygen saturation, test whether measured oxygen-carrying capacity adds held-out predictive information for final infarct conditional on perfusion, reperfusion, and time, and whether quantitative NCCT sinus HU can substitute for the laboratory value without loss of calibration. This requires identifying such a cohort first; ISLES'24 is not it, so the successor either waits on cohort identification or registers outside this charter. I deliberately do **not** register the bare sinus-intensity-sensitivity audit as a spin-off: the card's own kill clause says that study is not worth running without the hematology link, and I agree.

**Fact of record worth preserving:** the keystone screen's verified finding — raw, defaced-only, non-skull-stripped NCCT with intact sinus-region HU for all 149 cases — remains true and reusable by any future NCCT-quantitative candidate under this charter. The concession is about claim identifiability, not data availability.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** I concede the debate because the proposer accepts that ISLES'24 cannot identify the original oxygen-carrying-capacity proxy claim and that narrowing the study to sinus-intensity sensitivity would change the claim's identity.

**Argument:** The proposer answered the decisive objection with an argument rather than insistence: the available intervention arms can identify where and how strongly a model responds, but none can establish what sinus HU means to the model; the release provides no verified hematocrit or hemoglobin measurement with which to bridge that semantic gap; and the obtainable winning system excludes NCCT from its final inputs and brain-masks the sinus region (Ren et al., arXiv:2505.18424v2; official implementation commit `bb6c00c8a58cb57a5a33c133c02885776673d230`). The card's own rung limit and kill condition therefore control. The identity check is also resolved: changing the deliverable from use of venous attenuation *as an oxygen-carrying-capacity proxy* to sensitivity to edited dural-sinus intensity changes the scientific claim, so it cannot repair idea 028 under the 2026-08-10 rule. The proposed laboratory-data study may preserve the medical motivation, but because its evidential engine is a different treatment-characterized cohort rather than ISLES'24, it is a separate candidate and does not rescue this charter-scoped idea.

**What would change my mind:** The evidence specified in round 1: an obtainable frozen NCCT-inclusive final-infarct model and an untouched cohort concretely linked to ISLES'24 containing temporally aligned hemoglobin, oxygen saturation, acquisition/site, perfusion, reperfusion, and time variables, together with a preregistered mediation/substitution experiment showing that laboratory-implied sinus HU explains the model response while matched nonhematologic edits do not.

**Status:** CONCEDED

## Round 2 — PROPOSER

**Responding to:** The critic's round-2 concession, which accepts my round-1 concession and closes the substantive dispute. Nothing remains contested.

**Response:** CONCEDE

**Argument:** The concession stands as given in round 1; I add no new argument and the critic has raised no new objection to answer. For the decision record, the converged outcome is:

1. **Idea 028 is REJECTED.** Recommended kill code: IDENTIFIABILITY_FAILURE — the design can identify regional-intensity sensitivity but not the deliverable's proxy-semantics claim, and the release contains no hematology field that could bridge the gap (keystone screen, 2026-08-18). The card's own kill clause (`cross_domain.what_changes_if_dropped`) controls.
2. **No amendment is submitted.** Narrowing the deliverable to sinus-intensity sensitivity would change claim identity under the 2026-08-10 rule; both parties agree it would be a successor, not a repair, and both parties agree that successor is not worth registering (the card's kill clause covers exactly that study).
3. **One successor is proposed for separate registration** with `parent_ids: ["isles24-scout-003-c04"]`: the laboratory-cohort study of whether measured oxygen-carrying capacity (admission hemoglobin plus oxygen saturation) adds held-out final-infarct information conditional on perfusion, reperfusion, and time, and whether quantitative NCCT sinus HU can substitute for it without calibration loss. It is gated on identifying a treatment-characterized cohort with those variables; ISLES'24 is verified not to be that cohort, so it enters through normal scouting, possibly outside this charter.
4. **Facts of record preserved for reuse:** raw, defaced-only, non-skull-stripped NCCT with intact sinus-region HU for all 149 cases (keystone screen); and the verified negative model-asset facts — the winning pipeline consumes CTA/CBF/CBV/MTT/Tmax only and SynthStrip-masks the sinuses (Ren et al., arXiv:2505.18424v2, Table 1, Methods 3.2; `inference.py` lines 121–124 at commit `bb6c00c8a58cb57a5a33c133c02885776673d230`) — which any future NCCT-consuming candidate under this charter must not re-assume away.

**Status:** CONVERGED
