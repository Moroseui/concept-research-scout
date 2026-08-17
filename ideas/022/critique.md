# Critique: Does the model mistake the end of the scan for the end of the bolus? (idea 022)

```
FATAL OBJECTION: The study object — a frozen, performant ISLES'24 final-infarct model that consumes raw 4D CTP — does not exist as an obtainable artifact, and every substitute changes the question or breaks the card's own envelope.
EVIDENCE: arXiv:2505.18424v2 Table 1 (winner's inputs: CTA, CBF, CBV, MTT, Tmax — derived maps, not raw CTP); github.com/kimberly-amador/ISLES24-PrediCTP (only public raw-4D-CTP entry: training code, no released checkpoint, Dice 0.20, lesion-wise F1 0.02).
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: PAUSE
```

Unblock condition: an obtainable frozen raw-CTP final-infarct model with documented temporal-input semantics (padding/masking seen in training) and non-trivial performance — via a future challenge release, another team's checkpoint, or author correspondence with the PrediCTP group (the idea-002 unblock pattern). The nested-prefix design itself survives intact and should not be redrafted on unpause.

---

## 1. The fatal objection in full: there is no model to audit

The deliverable sentence is "The **raw-CTP final-infarct model** is using terminal-curve incompleteness…". The card never names the model, and the keystone screen (correctly returned `UNVERIFIABLE`) already showed the published winner cannot be it: Ren et al. (arXiv:2505.18424v2, Table 1) feed the final nnU-Net **CTA, CBF, CBV, MTT, and Tmax** — derived 3D maps, no raw time series.

New legwork for this critique found the closest thing to the required artifact: Amador et al., *Spatio-Temporal Deep Learning for Final Infarct Prediction using Acute Stroke CT Perfusion Data* (Springer, DOI 10.1007/978-3-031-81101-2_9; official repo `kimberly-amador/ISLES24-PrediCTP`). It genuinely consumes 4D CTP (CNN encoder + temporal Transformer + CNN decoder). But:

- **No released checkpoint.** The repository provides training and inference code only. The frozen artifact the card's estimand requires does not exist publicly.
- **Dice 0.20, absolute volume difference 17 ml, lesion-wise F1 0.02** on the 143-patient multicenter evaluation.
- Temporal padding/masking semantics are undocumented in the README, so the card's second keystone clause (prefixes in-distribution) cannot be inspected even for this architecture.

Every path around this damages the claim:

1. **Audit the winner instead.** Then the question becomes "does truncation propagate through deconvolution into the derived maps" — which Kasasbeh (PMID 25789631) and Copen (PMID 25500309) already established, with phantoms. The novelty delta collapses to prior work.
2. **Train a raw-CTP model yourself.** This violates the card's own compute envelope ("one frozen model, no retraining"), and — worse — it is quietly circular: whether short prefixes are in-distribution is decided by the *experimenter's* training-time augmentation choices. Train with temporal dropout and the model plausibly shrugs off censoring; train without and padding is OOD by construction. The experiment would measure a property you installed. The card's claim would degrade from "an ISLES'24 benchmark model has this failure mode" to "a model I trained can be given or denied this failure mode," which is a different and much less interesting sentence. Under the claim-identity rule (decisions.md, 2026-08-10), that is a successor, not a revision.
3. **Retrain PrediCTP from its released recipe.** Same circularity as (2), plus the weak-model problem below.

None of these preserve the question. Hence PAUSE, not ADVANCE TO REVISION.

## 2. The weak-model problem: entry point 2 requires a model that performs well

The charter's entry point 2 starts "from a model that merely performs well." Dice 0.20 with lesion-wise F1 0.02 is not that. There is no evidence this model family found *any* signal worth decoding; auditing what a barely-functioning model attends to has little medical consequence either way. Two card scores fail on this alone:

- **medical_relevance 4** is unsupportable for the only concretely available raw-CTP architecture. A duration shortcut in a Dice-0.20 model threatens nobody's deployment.
- **negative_result_value 4 / "decisive"** inverts. On a weak model, a null ("predictions stable under censoring") has a dominant boring explanation — the model uses little of the temporal signal, or little of anything. That is a type-3 uninterpretable null, which caps negative_result_value at 2 under the rubric.

The card's positive-control gate (a temporal shift must move predictions) partially defends against this, and deserves credit — but if the positive control fails on the only available model, the study returns "not runnable," which is a feasibility note, not science.

## 3. The OOD-intervention residual (the idea-006 pattern), confirmed unresolvable today

The card honestly names its own kill condition: if padding/masking cannot be shown in-distribution, the use claim is invalid — precisely the pattern that paused idea 006 (patient-deletion OOD). The card gates on "an explicit mask if supported and concordance across three padding conventions." But concordance across padding conventions is a weak substitute for training-time support: three padding styles can agree because all three are equally OOD in the same direction (all shrink late-time information mass). The idea-006 resolution required inspecting the training loader; here there is no training loader to inspect because there is no released model. The keystone screen's `UNVERIFIABLE` verdict is right, and clause (b) — model semantics — is indeed the load-bearing one.

## 4. Prior-work overlap: the delta is real but currently unexercisable

- Kasasbeh et al. (PMID 25789631) and Copen et al. (PMID 25500309): truncation corrupts *derived perfusion estimates*. Verified characterizations in the card.
- Bathla et al. — verified for this critique: *Computed Tomography Perfusion–Based Prediction of Core Infarct and Tissue at Risk: Can Artificial Intelligence Help Reduce Radiation Exposure?*, Stroke, DOI 10.1161/STROKEAHA.121.034266. The card's characterization (feasibility under partial data, radiation-reduction framing) is fair, and its `why_not_done` claim — raw-CTP AI papers emphasize radiation reduction, not the boundary as a learned feature — is corroborated by this title.
- Additional neighbor the card missed: *Detecting CTP truncation artifacts in acute stroke imaging from the arterial input and the vascular output functions* (PLOS ONE 2023, DOI 10.1371/journal.pone.0283610) — machine-learned truncation *detection* from AIF/VOF features. It does not audit an outcome model's use of the boundary, so the delta stands, but it belongs in `novelty_neighbors`, and its feature set is a citable, annotation-free instrument for the card's X. This strengthens the X-measurement clause and the spin-off below.

The model-use-under-nested-censoring question remains genuinely unasked. The overlap objection is *not* fatal; the missing artifact is.

## 5. Secondary objections (would matter if the fatal one fell)

- **Duration census unverified.** Riedel et al. report 1 frame/s resampling but no per-case durations or completeness; the "≥30 cases with both curves within 10% of baseline" gate is pure assumption. If ISLES'24 protocols were uniformly ~50–70 s (typical clinical CTP), severely delayed tissue essentially *never* returns to baseline and the eligible-case count could be near zero — DATA_INSUFFICIENT, the idea-001 death. This is Stage-0-checkable only after registration.
- **Access.** Data is registration-gated, one ~99 GB archive. Lightweight, but the charter requires no dependence on unconfirmed gated data; access is unconfirmed. data_readiness 4 is a notch high; 3 is defensible.
- **Eligibility selection bias.** Cases whose curves fully return to baseline are, by the card's own suspected mechanism, the *less severely delayed* ones. The complete-case subset systematically excludes the severe strata where the censoring cue would matter most, shrinking both the effect and its generalizability. The card's risk-set framing acknowledges conditioning on completeness but not this consequence.
- **What the card does well, for the record:** honest rung 0 and `NOT_INSPECTED`; the interior-frame-masking and tail-extrapolation controls are a genuinely good identification design; and the censoring analogy passes the charter's "what would be different if the analogy were dropped" test on its own terms (nested prefixes, conditioning on complete scans, boundary-vs-missingness separation are all consequences of it). The grammar is sound. The world lacks the artifact.

## 6. dies_like_prior, corrected

The card names IDENTIFIABILITY_FAILURE and DATA_INSUFFICIENT as its risks. The actual death today is **DATA_ACCESS** — "required data, checkpoints, or mappings are not obtainable in practice" — the idea-003/idea-018 pattern: the design is coherent and the decisive asset (here, a frozen performant raw-CTP checkpoint) is not obtainable. The keystone screen half-saw this; this critique confirms it with the PrediCTP repository inspection.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does the ISLES'24 benchmark itself contain a censoring–severity confound — across the 149 released 4D CTP cases, does the terminal completeness index (last-frame residual enhancement, AIF/VOF truncation features) correlate with final-infarct volume and with center?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — same duration-shortcut threat, but it is a dataset property, not a model-use claim; it reaches no rung, landing instead on the charter's "identification of a decisive confound" success mode.
SHOULD IT BECOME A SEPARATE CANDIDATE? YES — different estimand, so the claim-identity rule requires a new registration with parent_ids: [idea-022].
IS IT ACTUALLY WORTH DOING? Yes, conditionally: it is deterministic curve arithmetic on already-released data, needs no model and no labels beyond the released fate masks, has citable instrumentation (PLOS ONE 10.1371/journal.pone.0283610), and a positive result warns every team training on this benchmark — but only if registration-gated access is confirmed and the completeness census is non-degenerate; if nearly all curves are truncated (or none are), it yields a two-line data note, so it should run as a bounded Stage-0-style audit, not a full candidate build-out.
```

Two things follow from that audit for free. First, it *is* the missing duration census: it converts idea-022's unverified completeness assumption into inspected fact, so the paused card's keystone clause (a) resolves as a by-product. Second, if the census shows a real censoring–severity correlation in the training data, the paused model-use question gains urgency (models are demonstrably *exposed* to the shortcut), giving a concrete reason to pursue the checkpoint through author correspondence rather than letting the pause rot.
