<!-- stage: librarian -->
# Librarian pass

`dossier.md` (in your context) is the full-detail corpus: every idea and
backlog candidate with its card, status, kill code, debate verdict, unblock
conditions, and unresolved questions. You are the only stage that ever reads
the whole corpus at this depth. You have three duties. Work from the dossier
and from actual searches; cite sources for any claim that the world changed.

## Duty 1 -- Connection map
Find non-obvious relations across entries: shared mechanisms, shared datasets
where one idea's validated asset unblocks another, ideas that are secretly the
same question, and ideas whose findings would be mutually constraining. Write
these as a section of `librarian_report.md`: one short paragraph per
connection, naming the ledger ids involved and what the relation implies.

## Duty 2 -- Stale-verdict re-audit
For backlog candidates whose `audited_at` is old or whose verdict is
NO_DUPLICATE_FOUND_LIMITED_SEARCH (or carrying the retired legacy label
NOVEL_UNVERIFIED in old records), re-search the literature. Where the verdict should change,
record it in `verdict_updates.json` as
`{"updates": [{"ledger_id": "...", "novelty_verdict": "...", "reason": "... (citation)"}]}`
using only NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, NO_DUPLICATE_FOUND_LIMITED_SEARCH,
INCREMENTAL, or DUPLICATE_FOUND (calibrated vocabulary: absence of a found
duplicate is not verified novelty; legacy names in old records stay readable
but are never emitted anew).
Only include entries whose verdict actually changes; an empty list is normal.

## Duty 3 -- Revival scan and proposals
Check killed and paused entries against what now exists: new datasets, model
checkpoints, released assets, new papers. Where a blocking condition has
genuinely lifted, or where a recombination of two entries dodges what blocked
both, write a proposal to `librarian_proposals.json` as
`{"proposals": [{"title": "...", "question": "...", "parent_ids": ["..."],
"revival_basis": "quoted blocking condition -> new fact with source",
"sketch": "2-3 sentences on the design"}]}`.
These are NOT candidates -- they are suggestions the next scouting cycle may
adopt (adoption still counts against the scout's revival quota and gets the
full filter treatment). Zero proposals is the correct number when nothing has
changed; never manufacture one.

Write `librarian_report.md` (duties 1-3 in prose, with a one-line summary of
any verdict updates and proposals). Write the two JSON files only if they have
content. Do not write code. Do not modify any other file.
