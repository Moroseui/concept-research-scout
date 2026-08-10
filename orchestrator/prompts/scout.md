<!-- stage: scout -->
## Step 0 -- Read the ledger digest

`evidence/ledger_digest.md` is in your context. It is the institutional memory
of every idea this program has tracked: statuses, scrutiny levels, and the
kill-code frequency table. The kill-code table is a generation-time checklist:
before developing any candidate, check it against every listed failure mode.
USE_VS_ASSOCIATION killed nine of eleven ideas in cycle one -- every candidate
must state in one line how its design distinguishes "the model uses X" from
"X is merely correlated with the label."

## Step 0b -- Portfolio revivals (optional, bounded)

`evidence/portfolio_brief.md` (in your context) holds the full verdicts and
unblock conditions for actionable existing ideas. Up to TWO of your developed
candidates may be REVIVALS or RECOMBINATIONS of existing ideas instead of new
questions; at least the remainder must be brand new. Rules:

- A revival/recombination must set `parent_ids` (e.g. ["idea-012"]) and a
  `revival_basis`: quote the specific blocking condition or objection from the
  brief, then state the NEW fact that changes it, with a checkable source
  (a release, a paper, a newly available asset). No new fact, no revival --
  re-proposing an idea against an unchanged objection is forbidden.
- A recombination crosses parts of two entries (e.g. a paused idea's question
  with another idea's validated measurement); it must name both parents and
  say which part of each survives and why the combination dodges what killed
  or blocked the parents.
- ZERO revivals is the correct number when nothing in the brief has genuinely
  changed. Never manufacture a revival to fill the quota; brand-new questions
  are always the default.

## Keystone evidence rule

Any `keystone_status: INSPECTED_TRUE` claim MUST include a
`keystone_evidence` field quoting the artifact that proves it (URL,
file path, table row, or verbatim excerpt). A bare INSPECTED_TRUE
without evidence is mechanically demoted to NOT_INSPECTED at merge.

## Step 1 — Generate ten questions before developing any of them

Write ten one-line research questions. Do not elaborate. Do not score. Do not
check feasibility yet.

The point of this step is to search a wider space than you would if you were
optimizing a complete idea card from the first sentence. Cards written
end-to-end select for ideas that were safe by sentence two.

**Every question must be answerable with a sentence of the form "the model is
using X."** Not "the model is not using the scanner." A question whose best
possible answer is the absence of a confound is not eligible this cycle — write
a different one.

X must be computable from an image today, by an existing tool or a well-defined
measurement, without a human annotator. See the charter's hard constraint.

Include in the ten:
- questions you suspect are too hard
- questions you are not sure are answerable
- at least two that connect medical imaging to a field outside it
- at least one that sounds obviously wrong but that you cannot immediately
  refute
- at least three where X is a quantity a radiologist already has a word for

Then pick **five** to develop. Pick on interest and mechanism clarity, not on
how defensible they will be. The critic exists to handle the rest.

Record all ten in `all_questions`, and for the five you dropped, one line each
on why.

## Step 2 — Mode and entry-point quotas

Of the five developed candidates:

- **1 Mode A** (unfinished story)
- **2 Mode B** (unasked question)
- **2 Mode C** (speculative — lower feasibility bar, higher mechanism bar)

At least three of five in radiology or CT. At most one dermatology.
No more than two on any single dataset.

Each candidate also declares `entry_point`:
- `1` — starts from a documented model-beats-human gap
- `2` — starts from a well-performing model, looking for unexpected signal

Both are allowed. Entry point 2 requires naming the specific measurement that
would detect the unexpected signal and the specific artifact it would be
confused with.

If you cannot fill a quota with something you believe in, say so in
`quota_note`. An honest short list beats a padded one.

## Step 3 — Read the record first

`evidence/decisions.md` is in your context. Read it before developing anything.

For every candidate, fill `dies_like_prior`: name the prior killed candidate it
most resembles and say what makes this one different, or state plainly that no
prior failure mode applies and why.

The dominant prior failure is annotation provenance — the study needed to know
who assigned labels and what they could see, and that was undocumented or
contaminated. If your candidate's keystone depends on annotation conditions,
say so directly rather than discovering it in critique.

## Step 4 — Keystone, checked before scoring

Name `keystone_prerequisite`: the single fact which, if false, makes the study
impossible or uninterpretable.

State it as the thing your *inference* needs, not the thing that is easy to
check. A prior candidate verified "multiple opinions exist per lesion" (true)
when the real keystone was "those opinions are independent measurement
methods" (false). That error cost a full critique and debate cycle.

Then go and check it — the actual file listing, data dictionary, schema, or
methods section. Not the collection homepage. Not an abstract.

`keystone_status`: `INSPECTED_TRUE` / `INSPECTED_FALSE` / `NOT_INSPECTED`.

`feasibility` and `novelty_confidence` cap at 3 unless `INSPECTED_TRUE`.
Mode C candidates may honestly report `NOT_INSPECTED`; that is expected.

## Step 5 — Per candidate, write

1. `search_mode`, `entry_point`, `title`
2. `question` — one sentence, ending in a question mark
3. `rung` — 1, 2, or 3 per the charter, and what would move it up
4. `deliverable_sentence` — the single sentence a radiologist could agree or
   disagree with, of the form "the model is using X." Write it now, before the
   design. If you cannot write it, the candidate is not eligible.
5. `X_measurement` — how X is computed from an image, naming the tool or
   formula, and a citation if one exists. Then answer: *could I compute X on a
   scan the model has never seen, today, without asking anyone?* If no, the
   candidate is ineligible regardless of how interesting it is.
6. `suspected_signal` — the physical or biological mechanism by which X would
   be present in the image. Required for Mode C. "Some feature" is not an
   answer.
7. `keystone_prerequisite`, `keystone_status`, `keystone_evidence`
8. `keystone_residual_assumption` — having verified the nearest checkable
   thing, what are you still assuming? If that assumption is load-bearing, it
   is the real keystone. This error has occurred three times; see the charter.
9. `rung_reached` — 1, 2, or 3, and what would move it up
10. `dies_like_prior`
11. `closest_prior_work` with identifiers, and what it did not do
12. `existing_assets`
13. `smallest_decisive_experiment`
14. `standing_confounds_addressed` — scanner, vendor, protocol, reconstruction,
    site, positioning, habitus, prevalence, referral pathway, label leakage.
    Name which the design rules out and which it does not.
15. `alternative_explanations` and which the design excludes
16. `anticipated_negative` — decisive / sensitivity-limited / uninterpretable
17. `cross_domain` if applicable: borrowed construct, the measurement it
    implies, and **what would change if the analogy were dropped**
18. `remaining_legwork` — time to first decision, not just what exists
19. `scores` per the rubric, including `identifiability`
20. `unverified_claims`

## What went wrong last cycle, and what to do differently

All ten questions last cycle were confound-elimination: does the model read
the dose, the scanner, the table, the motion artifact. Those are good
questions and they are not this program. Their best possible answer is the
*absence* of an explanation, which does not help a physician understand a
decision.

Confound elimination is the validity gate that earns the right to say "the
model is using X." It is not X.

This cycle, lead with X. Ask what a physician would want to hear, then work
backwards to what would make it credible.

## Style

Prefer designs whose primary readout does not need trustworthy labels. The one
candidate that has survived this loop compared a model to itself across two
reconstructions of the same anatomy — no ground truth entered the primary
measurement. That structural move is available more often than it is used.

Be suspicious of your own good sentences. If a candidate's appeal is mostly in
how it sounds, say so in `alternative_explanations` and score identifiability
accordingly.

Write `scout_candidates.json`. Do not write code.

## Design template (required field)

Set `design_template` to the experimental GRAMMAR of the candidate, one of:
natural-paired, cross-reconstruction, regional-removal,
regional-substitution, representation-erasure, counterfactual-synthesis,
conditional-observational, longitudinal-within-subject,
cross-model-disagreement, model-output-perturbation.
The digest counts these: homogenization is measured by repeated grammar,
not repeated nouns. Pick the closest; if truly none fits, use
`other:<short-name>` and justify it in the card.
