Generate **4** candidate research ideas that fit the charter, then rank them.

Four, not six. Depth of verification matters more than breadth this cycle.

## Before you write anything

Read `evidence/decisions.md` and `ledger/`-equivalent records of prior cycles.
Do not re-propose a killed idea or a thin variant of one.

## Mode and quota requirements

- Each candidate declares `search_mode: A` or `search_mode: B` (see charter).
- **At least two candidates must be Mode B** — questions nobody framed, not
  gaps somebody left.
- **At least three of four must be radiology or CT.**
- At most one dermatology candidate.
- No more than two on the same dataset.
- No more than two whose method is a concept bottleneck model.

If you cannot meet a quota with a candidate you believe in, say so explicitly
in a `quota_note` field rather than padding with a weak idea. An honest short
list beats a padded one.

## The keystone check comes first

For each candidate, before scoring anything:

1. Name the `keystone_prerequisite` — the single fact which, if false, makes
   the study impossible or uninterpretable.
2. **Actually go and check it.** Open the file listing, the data dictionary,
   the methods section, the repository contents. Not the collection homepage,
   not the abstract, not a search-engine summary.
3. Record `keystone_status` as one of:
   - `INSPECTED_TRUE` — you looked at the primary artifact and it holds
   - `INSPECTED_FALSE` — you looked and it does not hold (discard the candidate
     or reformulate around what you found)
   - `NOT_INSPECTED` — you could not verify it, and say why

`feasibility` and `novelty_confidence` are capped at 3 unless
`keystone_status` is `INSPECTED_TRUE`. This cap is not negotiable.

"The dataset exists" is not the keystone. The keystone is the specific linkage,
label, protocol, or artifact the experiment depends on.

## Per candidate, write

1. `search_mode` and `title`
2. `question` — one sentence, ending in a question mark
3. `why_unasked` (Mode B) or `what_was_left_undone` (Mode A)
4. `concept_definition` — exactly what counts as a concept here
5. `keystone_prerequisite`, `keystone_status`, `keystone_evidence` (what you
   opened and what it said)
6. `closest_prior_work` — with identifiers, and what it did *not* do
7. `existing_assets` — data, labels, code, checkpoints already available
8. `smallest_decisive_experiment` — the cheapest thing that answers it
9. `alternative_explanations` — two or three other things that could produce a
   positive result, and which ones the design rules out
10. `anticipated_negative` — classified as decisive / sensitivity-limited /
    uninterpretable, per the charter
11. `remaining_legwork` — not just what exists, but what still has to be built:
    data cleaning, linkage risk, provenance risk, author correspondence,
    statistical development, expected time to first decision
12. `cross_domain` — if applicable: borrowed construct, the measurement it
    implies, and what would change if the analogy were dropped
13. `scores` per `docs/SCORING_RUBRIC.md`, including `identifiability`
14. `unverified_claims` — everything you did not check directly

## Style

Prefer the small check over the large study. A question answerable in an
afternoon that changes how a literature is read is worth more here than a
well-scoped three-month replication.

Be suspicious of your own good sentences. If a candidate's appeal is mostly in
how it sounds, say so in `alternative_explanations` and score
`identifiability` accordingly.

Write `scout_candidates.json` in the assigned scouting folder. Do not write
code.
