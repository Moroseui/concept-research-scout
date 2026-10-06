# Generated artifacts belong to a run

Copied analysis context preserves predecessor artifacts. A generic stage/round name
therefore is not globally unique. New artifacts use current/runs/<SHA256(run_id)>/
plus their existing stage/round filename. Current artifact IDs and versions remain
unchanged; all callers select the same content through the recorded path and hash.

An existing same-run path with different bytes still refuses. No predecessor file,
model output, ledger call or charge is changed. The directions author completed;
recording failed afterward. Reuse its hash-bound output through ordinary completed
output validation, after reviewed installation and a held same-run continuation.
Do not start another author call or initialize another allowance.

Focused tests cover every downstream analysis stage with copied predecessor files,
distinct-run separation, same-run immutable refusal, and requalification of a
completed synthetic author with identical call/charge rows and no model launch.
The live continuation still requires private-copy rehearsal and source-bound review.


The held continuation is bound to ITEM5_ARTIFACT_CHECKPOINT.json. It verifies the
original config, preparation, context, owner, pending output, local rows and the
original global call/owner. It permits only the exact one completed author, copies
with SQLite backup as the owner, appends one continuation event, and does not
change the original lane or any call/charge row. The saved author is passed through
normal output validation. Unknown or active calls, changed bindings, duplicate
continuation and a different runtime refuse. Completion later releases only the
proved frozen predecessor, while preserving its historical BLOCKED state.

Unit fixtures explicitly simulate qualification and service state; their SQLite
copy/ledger transaction and frozen-row checks are real. Private copies of genuine
server state and installed promotion checks remain required release evidence.
