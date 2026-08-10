<!-- stage: wide_scout -->
# Wide-mode scouting: raise the ceiling, keep the floor

This track exists because the baseline track selects for ideas that are safe by
sentence two. Here the *hypothesis space* is opened up while the *evidence
standards* stay exactly where the charter puts them. Ambitious in what is
claimed, conservative in how it would be shown.

## What is different from the baseline track

- Multi-step causal stories are allowed: "the model uses X, which it can only
  see because of Y, which implies Z about its failure mode" is eligible if each
  link is separately checkable.
- Cross-field transplants are mandatory, not optional: every candidate must
  borrow a construct, instrument, or law from a field outside medical imaging
  (physiology, physics, forensics, ecology, economics, materials, anything) and
  name the measurement the borrowed construct implies.
- Mechanistic surprise is the selection criterion. Ask: would a radiologist
  raise an eyebrow at the claim, and would they *change something* if it were
  true?

## What is NOT different

- The charter's hard constraint holds: X must be computable from an image
  today, by an existing tool or well-defined formula, with no human annotator.
- The deliverable sentence still has the form "the model is using X." Absence
  of a confound is still not X.
- The use-vs-association test still applies at generation time: for each
  candidate, state in one line how the design distinguishes "the model uses X"
  from "X is merely correlated with the label." If you cannot, the candidate is
  ineligible -- this single pattern killed nine of eleven ideas in cycle one.
- One compute envelope: the smallest decisive experiment must fit one Colab
  GPU session on public data. State the envelope explicitly per candidate.
- Read `evidence/ledger_digest.md` (in your context) before writing anything.
  Fill `dies_like_prior` against the kill-code table, per candidate.

## Keystone evidence rule

Any `keystone_status: INSPECTED_TRUE` claim MUST include a
`keystone_evidence` field quoting the artifact that proves it (URL,
file path, table row, or verbatim excerpt). A bare INSPECTED_TRUE
without evidence is mechanically demoted to NOT_INSPECTED at merge.

## Procedure

1. Write **eight** one-line questions. At least five must connect medical
   imaging to a distinct outside field (name the field in brackets). At least
   two should feel one step past what you believe defensible.
2. Develop **three**. For the five dropped, one line each on why.
3. For each developed candidate, produce the same fields as the baseline scout
   (deliverable_sentence, X_measurement, keystone_prerequisite / status /
   evidence, dies_like_prior, closest_prior_work, smallest_decisive_experiment,
   standing_confounds_addressed, scores, unverified_claims), **plus** a novelty
   triplet:
   - `novelty_neighbors`: the three closest prior works with identifiers,
     found by actually searching, not recalled;
   - `novelty_delta`: the precise difference in one sentence;
   - `why_not_done`: one of `NEW_CAPABILITY` (name the capability or dataset
     that only recently exists), `BLIND_SPOT` (state the reason the field
     missed it), or `TRIED_AND_FAILED` (cite it -- and treat this as a red
     flag, not a disqualifier).
   If you cannot find neighbors, write `NO_NEIGHBORS_FOUND` -- that is a flag
   for human verification, never proof of novelty.
4. Set `"track": "wide"` on every candidate.

Write `wide_candidates.json` with the shape
`{"candidates": [...], "dropped": [{"question": "...", "why": "..."}]}`.
The `candidates` array contains ONLY the three fully developed candidates;
the one-line notes on dropped questions go under `dropped`, never as stub
entries in `candidates` (stubs are filtered out at merge and waste the slot).
Do not write code. Do not modify any other file.
