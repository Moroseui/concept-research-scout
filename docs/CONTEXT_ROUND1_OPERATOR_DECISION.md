Review round 1 of 2 is in manual-review/reviews/001-claude-review.md. Verdict: CHANGES REQUIRED. Fix only the following, then stop:

1. B1, B2, B3 exactly as described in the review.
2. Item 7: I approve the reviewer's resolution. Move the Sprint 10 excluded-case list to a private file beside the split manifest; the config line holds only path, sha256 and count; the notebook verifies hash and count and keeps assert len(CASES) == 99; the hash goes into the run fingerprint. The scanner stays unchanged. Commit the resulting record so the committed code matches the report.
3. Headroom: pass the notebook source and saved outputs to stages as hash-checked workspace files instead of inline text, with the hashes in the input. Remeasure all four inputs with real material (all 9 reviewer artifact types, a real run spec, not placeholders). Each must fit under 200,000 characters with margin.
4. Selection map gaps from item 6: add the research question to interpretation stages, give the interpretation reviewer investigator_next_decision.json, and give spec stages the split/exclusion contract and validator.
5. Make the obligations preflight unavoidable: build() must not return a sendable input unless the preflight passes.
6. Add a test for a stop scoped to a stage (not just adverse findings), and a test for the '*' wildcard.
7. Rerun both full test runners on the final commit and bind the logs to that commit.

Then prepare manual-review/reviews/ROUND2.md listing each fix with file:line and test evidence. Round 2 will verify only these fixes. No model calls or deployment.
