<!-- stage: fiction_refine -->
# Formalize a collaborator's pitch

A collaborator has sent you a rough technical pitch: `fiction_pitch.md`, in
your context. They believe there is something in it. Your job is to determine
whether a testable kernel exists inside this program's charter, and if so, to
formalize it into candidate idea cards.

Treat the pitch the way you would treat an excited hallway conversation with a
smart colleague: take the underlying observation seriously; take none of the
claims on faith. The pitch's *strength of claim* is not your problem -- your
output claims only what a real experiment on real public data could show.

## The honorable exit comes first

"No testable kernel exists" is a first-class, fully successful outcome of this
stage. It is not a failure, and you are not being scored on rescuing the
pitch. If the pitch's central quantity cannot be computed from an image today
without a human annotator, or the claim cannot be cast as "the model is using
X" with a design that distinguishes use from mere association, or the smallest
decisive experiment cannot fit one Colab GPU session on public data -- say so
and stop. In that case write:

```json
{"candidates": [], "no_testable_kernel": "<one paragraph naming precisely which requirement fails and why>", "adjacent_question": "<OPTIONAL: if your exit reasoning surfaced a well-formed nearby question that WOULD be testable on other public assets, state it in one or two sentences. This is a banked note for future scouts, not a candidate, and including it does not weaken the exit. Omit the field if nothing genuine surfaced.>"}
```

Do NOT rationalize. The characteristic failure of this stage is building an
elaborate justification around a premise with no measurable core. If you
notice yourself supplying the mechanism the pitch lacks, that is the signal to
take the exit, not to keep building.

## If a kernel exists

Extract it -- the kernel, not the pitch. It is fine (expected) for the
formalized question to be far more modest than the claimed finding. Produce
one or at most two candidates in the same JSON shape as scout candidates, each
with: `title`, `question`, `deliverable_sentence` (form: "the model is using
X"), `X_measurement` (tool or formula, computable today, no annotator),
`suspected_signal`, `keystone_prerequisite` + `keystone_status` (checking is
encouraged but `NOT_INSPECTED` is honest and acceptable here; INSPECTED_TRUE
requires a `keystone_evidence` quote or it is demoted at merge),
`use_vs_association_design` (one line: how the design separates use from
correlation), `dataset` (public, named), `smallest_decisive_experiment` (must
fit one Colab GPU session), `closest_prior_work` (search; if none found, write
`NO_NEIGHBORS_FOUND` for human check), `critical_confound`,
`anticipated_negative`, `scores` per the rubric, and `"track": "fiction"`.

Also record `kernel_provenance`: one sentence on what, in the pitch, the
kernel came from -- so a later post-mortem can tell whether a dead fiction
idea failed in the source or in the translation.

Write `fiction_candidates.json` with the shape
`{"candidates": [...]}` (plus `no_testable_kernel` when taking the exit).
Do not write code. Do not modify any other file.

## Design template (required field)

Set `design_template` to the experimental GRAMMAR of the candidate, one of:
natural-paired, cross-reconstruction, regional-removal,
regional-substitution, representation-erasure, counterfactual-synthesis,
conditional-observational, longitudinal-within-subject,
cross-model-disagreement, model-output-perturbation.
The digest counts these: homogenization is measured by repeated grammar,
not repeated nouns. Pick the closest; if truly none fits, use
`other:<short-name>` and justify it in the card.

## Scoring (Mode C)

Fiction candidates are Mode-C by nature (mechanism-first). Score with the
Mode-C rubric -- mechanism_clarity (30%), identifiability (25%), interest
(20%), medical_relevance (15%), clarity (10%) -- each as {value, why},
and include `search_mode: "C"`, `mode_c_priority_score`, and its
arithmetic. The orchestrator recomputes and never trusts a self-score it
cannot verify, so honest arithmetic costs nothing and disagreement is
auto-corrected.
