# Debate transcript

## Round 1 — CRITIC

**Position:** The original study is not executable with obtainable assets, and the proposed feasible repair changes the audited model and estimand enough that it must be a separate successor rather than an amendment to Idea 018.

**Argument:** Idea 018 asks whether the published whole-head GRASP glioblastoma survival model uses temporalis thickness, with tumor-stable longitudinal tracking as convergent evidence. Direct inspection defeats both load-bearing assets: the publication-linked GRASP repository at commit `ba0a1ca0` contains training code but no checkpoint, pretrained weights, inference entry point, or released training cohort, while the paper makes its data available only by request; this violates the charter's prohibition on dependence on unconfirmed gated data. The longitudinal arm also has no suitable public cohort: LUMIERE is skull-stripped and therefore removes temporalis (DOI 10.1038/s41597-022-01881-7), whereas all 60 UPenn-GBM follow-ups were obtained at second resection for progressive radiographic change (PMCID PMC9338035), making that subset anti-selected against the required tumor-stable pairs. Training a new model on UPenn-GBM unstripped baseline scans and using cross-patient temporalis substitution could be feasible, but it would answer whether a newly trained model family uses temporalis, not whether GRASP does, and it drops the original longitudinal estimand. Under the ledger's claim-identity rule, that is a new candidate with `parent_ids: ["idea-018"]`, not a repair. This is the realized form of idea 014's missing-model-asset failure, which the card's `dies_like_prior` assessment omitted.

**What would change my mind:** Show an openly obtainable, runnable frozen GRASP checkpoint together with its exact preprocessing and an obtainable survival-linked serial cohort retaining bilateral temporalis that contains a prespecified adequate number of same-patient, tumor-stable pairs; otherwise reject Idea 018 and register the UPenn-GBM self-trained design as a separate successor.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The study as carded cannot be executed — the audited model (GRASP) has no obtainable weights, inference path, or training data, and no public longitudinal GBM cohort both retains the temporalis and contains tumor-stable pairs — and the only feasible repair (self-trained UPenn-GBM model, cross-patient substitution, longitudinal arm dropped) changes the claim's identity and must therefore enter as a new candidate, not an amendment.

**Response:** CONCEDE

**Argument:** The objection is correct, and I have no new evidence against any part of it. The card's keystone was conjunctive, and both load-bearing conjuncts fail on direct inspection, not on prediction: the publication-linked GRASP repository at commit `ba0a1ca0` contains training scripts referencing unreleased local files (`pretrained_weights/t1_weights.pt`, `data/input_data/training_data.npz`) and no checkpoint or inference entry point, with the paper's data available only "by request" — which the charter prohibits depending on. The longitudinal arm is independently dead: LUMIERE deletes the temporalis by construction (skull-stripped, DOI 10.1038/s41597-022-01881-7), and the UPenn-GBM follow-ups are all second-resection cases selected *for* progression (PMC9338035), the opposite of the tumor-stable pairs the design requires. The two halves of the "smallest decisive experiment" therefore fail separately; no ordering of effort rescues either.

I also accept the identity check as the critic frames it. I considered defending an amendment — keep the question "does a whole-head GBM survival model use temporalis bulk?" and swap in a self-trained model — but that reading fails the ledger's rule. The carded deliverable names a published prognosticator and leans on within-patient, tumor-stable tracking as convergent evidence; the feasible study audits a model I would train myself and replaces the longitudinal estimand with cross-patient substitution. The deliverable sentence changes from "the GRASP model is using temporalis" to "whole-head survival training on UPenn-GBM discovers temporalis," and the critique additionally showed the "as a marker of systemic frailty" gloss must be cut, since an age/sex-proxy reading is an unarbitrated alternative meaning of the same substitution result. Two identity-changing edits make a successor, not a repair — the idea-015 precedent exactly.

Two corrections for the record. First, my `dies_like_prior` field was wrong by omission: it cleared annotation provenance but missed that this is idea-014's missing-model-asset failure realized; the keystone screen's UNVERIFIABLE verdict should be read as INSPECTED_FALSE for the GRASP-route conjuncts. Second, this concession is not a claim that the question is worthless — the medical motivation (frailty contamination of imaging prognosticators) and the measurement asset (public temporalis segmentation tool, Dice 0.893, validated on public TCIA GBM collections) both survive intact and transfer to the successor.

**Spin-off (to register as a new candidate with `parent_ids: ["idea-018"]`, via normal scouting):** Train a whole-head 3D survival model on UPenn-GBM unstripped defaced scans (630 patients, released overall survival, CC BY 4.0); preregistered gate: beat an age+sex-only baseline on a frozen split, else stop; test use by temporalis-only cross-patient substitution with scalp/fat and left–right shams; deliverable sentence limited to "the model is using temporalis muscle bulk," with frailty relegated to discussion and an age-adjusted arm specified. Stage 0 is the binary check that CaPTk defacing spares the temporalis at the standardized measurement levels.

**Status:** CONVERGED

## Round 2 — CRITIC

**Position:** The proposer’s evidence-based concession resolves the dispute: Idea 018 should be rejected, and the UPenn-GBM self-trained design should proceed only as a separate successor candidate.

**Argument:** The proposer did more than repeat agreement: it accepted the directly inspected failure of both conjuncts of the original keystone, corrected the GRASP route from unresolved to effectively `INSPECTED_FALSE`, and applied the claim-identity rule to the model swap and removal of the longitudinal estimand. That reasoning answers the sole open objection. The proposed spin-off does not amend Idea 018 because it changes the audited object from GRASP to a newly trained model and narrows the deliverable from systemic frailty to measurable temporalis muscle bulk; registering it with `parent_ids: ["idea-018"]` through normal scouting is therefore the correct disposition. No remaining technical objection can rescue the original question without the unavailable GRASP artifact and suitable serial cohort.

**What would change my mind:** Nothing in the present record; reopening Idea 018 would require the concrete assets specified in Round 1—an openly runnable frozen GRASP checkpoint with exact preprocessing and an obtainable survival-linked serial cohort retaining temporalis with enough tumor-stable within-patient pairs.

**Status:** CONVERGED

## Round 2 — PROPOSER

**Responding to:** The critic's closing position that the concession resolves the dispute, Idea 018 is rejected, and the UPenn-GBM design proceeds only as a separate successor through normal scouting.

**Response:** CONCEDE

**Argument:** Nothing remains in dispute and I will not relitigate the agreement. This round exists only to fix the disposition precisely, so the ledger entry and the successor's intake are unambiguous:

1. **Disposition:** Idea 018 is REJECTED (superseded), kill code the idea-014 family — the audited model asset is unobtainable, here confirmed by direct inspection rather than left unreproduced. The keystone record should carry `INSPECTED_FALSE` for the two GRASP-route conjuncts (obtainable runnable weights; obtainable tumor-stable serial cohort retaining temporalis), superseding the screen's UNVERIFIABLE verdict. The reopening condition is the critic's Round 1 formulation verbatim: an openly runnable frozen GRASP checkpoint with exact preprocessing, plus an obtainable survival-linked serial cohort retaining bilateral temporalis with a prespecified adequate count of same-patient, tumor-stable pairs. Both are required; neither alone reopens.

2. **Successor intake, so nothing is lost at the handoff:** the successor enters scouting with `parent_ids: ["idea-018"]` and carries four constraints fixed by this debate, which its card may not silently drop: (a) deliverable sentence limited to "the model is using temporalis muscle bulk" — the frailty gloss is prohibited as a claim, discussion only; (b) an age-adjusted arm is mandatory, since age/sex-proxy is the standing unarbitrated alternative meaning of a positive substitution result; (c) preregistered stop gate: the self-trained model must beat an age+sex-only baseline on a frozen split before any decoding work; (d) Stage 0 is the binary check that CaPTk defacing spares the temporalis at the standardized measurement levels in UPenn-GBM unstripped scans. Per the 2026-08-10 rule it inherits no queue position and gets its own novelty audit — which should specifically check whether GRASP or its citing literature published saliency or occlusion maps over the temporal region, the one delta-narrowing risk the critique identified.

3. **What was lost, stated for the record:** the ability to say anything about GRASP itself, the within-patient tumor-stable estimand, and the frailty interpretation. The surviving assets are the medical motivation, the public temporalis segmentation tool validated on public TCIA GBM collections, and UPenn-GBM as cohort.

**Status:** CONVERGED
