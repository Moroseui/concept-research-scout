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
{"candidates": [], "no_testable_kernel": "<one paragraph naming precisely which requirement fails and why>"}
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
encouraged but `NOT_INSPECTED` is honest and acceptable here),
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
