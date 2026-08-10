<!-- stage: actioner -->
# Actioner pass

`action_state.md` (in your context) is a mechanically collected snapshot of
everything currently awaiting a human or drifting without one: pending
decisions extracted from consensus files, paused ideas with unblock
conditions, queue state, recent librarian findings, and workflow health
notes. Your job is synthesis and prioritization, not collection -- the facts
are already gathered; do not re-derive or contradict them.

Write `actions.md` with exactly these sections:

## Decisions waiting on the human
Each pending decision as one item: the idea id, the exact question quoted or
tightly paraphrased, what each option implies, and your recommendation with a
one-line reason. Order by consequence, not recency. If a decision has been
waiting across multiple briefs, say so.

## Worth a check soon
Unblock conditions and stale items where a cheap look could change something:
what to check, where, and what a positive finding would unlock. Only items
where the check is genuinely cheap (a search, a release page, one file).

## System observations
At most five short items on the pipeline itself: queue health, imbalances
(e.g. verdicts aging, tracks unrun, near-misses unadopted), and anything the
latest librarian report surfaced that has not yet reached the stage that
needs it. No flattery, no padding; if the system is healthy, say so in one
line.

## Proposed improvement (only if instructed)
If and only if the task input enables improvement mode, pick the SINGLE
highest-value change and describe it: what file(s), what change, why now,
what could break, and how the tests cover it. Otherwise omit this section
entirely.

Keep the whole brief under 150 lines. It is read on a phone.
Write `actions.md` in the assigned output directory. Do not write code.
Do not modify any other file.
