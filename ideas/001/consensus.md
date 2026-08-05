# Debate summary — idea 001

## Agreed

- The released LIDC-IDRI diagnosis records cannot be assumed to identify the specific XML nodule carrying the eight semantic ratings. Assigning a patient-level diagnosis to every nodule would be label misattribution, not ordinary label noise (Round 1).
- Zinovev et al. (DOI 10.1007/s10278-011-9445-3) is the governing verified feasibility evidence: its conservative single-nodule rule yielded only 18 reliably linked nodules—8 malignant, 9 benign, and 1 indeterminate—which is inadequate for the proposed eight-predictor nested-CV paired-AUC analysis at useful precision (Round 1).
- The endpoint should be called “confirmed clinical diagnosis,” not “pathology-confirmed malignancy,” with confirmation mechanism reported and tissue-confirmed cases treated as a sensitivity stratum (Round 1).
- Any linkage must be frozen without access to semantic attributes or malignancy ratings, and model fitting must depend on a prespecified precision criterion rather than merely on whether a classifier can be fit (Round 1).
- Applying one conservative linkage rule estimates that rule's yield, not a true “linkage ceiling.” The nodule-count spreadsheet may separate single- from multi-nodule patients, but it does not itself identify the diagnosed XML nodule in ambiguous patients (Round 2).
- Manual image matching is not a defensible rescue under the stated constraints because no independent reference standard, diagnostic location evidence, or second adjudicator was established (Round 2).
- Reproducing the earlier linkage limitation would describe dataset usability, not answer whether the semantic concepts predict disease. A linkage audit can serve only as a private reopening gate, not as the publishable concept-validity result (Rounds 2–3).
- The card as written should be rejected rather than paused. The underlying medical question remains interesting and unanswered; the failed element is the released LIDC-IDRI diagnosis file as an instrument for answering it (Round 3).
- Reopening requires a publicly released or independently validated mapping from confirmed diagnoses to specific XML nodules, retention of all eight semantic ratings, and enough verified benign and malignant cases to meet a prespecified precision target before model fitting (Round 3).
- The endpoint-practice audit remains a logged spin-off only; promoting it would be a new idea rather than a revision of this card (Rounds 1–3).

## Unresolved

### Does a suitable diagnosis-to-XML-nodule mapping already exist?

- **Proposer's position:** No suitable mapping was verified in the search performed, but failure to find one is not evidence that none exists.
- **Critic's position:** Claims of larger strongly labelled cohorts do not resolve feasibility unless they supply an auditable nodule-level mapping that retains all eight XML ratings.
- **Evidence that would settle it:** A publicly released or independently validated mapping, accompanied by an auditable linkage method and independently verified benign and malignant counts. Its counts must satisfy a prespecified confidence-interval-width target before modeling.

There is no remaining disagreement about the present disposition. The empirical question—whether the eight LIDC semantic attributes predict independently confirmed disease as well as radiologist malignancy suspicion—remains unanswered because both sides agree that the currently verified linkage cannot test it.

## Positions that moved

- **Proposer, Round 1 — earned amendment.** In response to the critic's primary-source linkage evidence and sample-size objection, the proposer withdrew the immediately feasible nested-CV paired-AUC design, renamed and stratified the endpoint, required blinded linkage and a pre-modeling precision stop, and initially promoted linkage auditing to the main deliverable.
- **Critic, Round 2 — earned concession.** In response to those safeguards, the critic accepted that the original feasibility objection had been handled procedurally, then raised a distinct contribution-validity objection: the proposed audit was neither a true ceiling nor an answer to concept validity.
- **Proposer, Round 2 — earned concession.** In response, the proposer withdrew the “linkage ceiling” claim, abandoned unverified manual matching, conceded that reproducing the 18-nodule limitation lacks a publishable concept-validity inference, and demoted the audit to an internal gate.
- **Critic, Round 3 — earned acceptance.** The critic accepted those withdrawals because they directly addressed the mechanism of the objection and stated that no defensible study remained under the original card.
- **Proposer, Round 3 — earned concession.** In response to that consequence, the proposer moved from leaving an internal gate attached to the idea to recommending outright rejection and adopted the critic's concrete reopening condition.

No concession was unearned: each movement followed a new objection, safeguard, or consequence stated by the other side. The debate did not converge in one round; the critic raised a substantive second objection after accepting the first-round safeguards.

## Amendments made

At round zero, the idea claimed that a public LIDC pathology endpoint could be linked to the same nodules carrying eight semantic ratings, enabling a quick paired comparison between prediction of radiologist suspicion and prediction of disease. It described the endpoint as pathology-confirmed malignancy, proposed nested cross-validation and paired AUCs, treated a small gap as evidence licensing endpoint substitution, assigned a 4.45/5 priority score, and recommended `SHORTLIST`.

The final position withdraws that study. The endpoint is more accurately “confirmed clinical diagnosis,” but the released records have no verified, sufficiently large, auditable mapping to specific XML nodules. A recount under one rule is not a linkage ceiling, manual matching lacks adequate validation, and an imprecise null cannot validate endpoint substitution. The linkage check survives only as an internal reopening gate, not as the scientific deliverable.

Lost from the original idea are the one-experiment concept-validity story, the claimed high value of either outcome, the strong novelty framing, and the expectation of an immediately feasible CPU-only study. The agreed card updates are `recommendation: REJECT`, priority score 2.85/5, reduced negative-result value and novelty confidence, and an unverified-claims entry recording Zinovev et al.'s 18-nodule result as the governing prior evidence. The underlying medical question and the unpromoted endpoint-practice spin-off remain, but neither is an active revision of this idea.

## Recommendation

**REJECT** — before deciding whether to reopen, the human should look for a publicly released or independently validated diagnosis-to-XML-nodule mapping that retains all eight semantic ratings, then verify *before model fitting* that its independently confirmed benign and malignant counts meet a prespecified CI-width target. Without that artifact, the proposed experiment cannot support its intended inference.
