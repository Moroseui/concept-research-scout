# Research status

- Item 6 and synthesis are accepted; 352 rounded Sprint 14 values match the same saved fits/cohort, not independent retraining.
- Review 3 approved the Colab notebook. The exact file is in Partho's Downloads; private execution bindings are still being packaged.
- Partho reports 6.77 units/hour: 1,001 units buy 147.9 A100 hours, versus the provisional 130?140 hours for all 40 fits.
- No scientific or GPU job is running. Timing is parked after a repeated admission-reader failure; idea 2 authoring has not started yet.
- Compute actual is $24.40; stage-1 exposure is $115.52/$150. Reported Claude charges are $105.71; author dollars are unavailable.
- Next: runnable A1_repeat fold-0 smoke package, then saved-output 3?3 analysis. Server access is intermittent, so no reliable completion estimate yet.
- Action needed: none yet. Today 28/50 calls. C: about 19.1 GiB free. No swap point. See the [execution plan](13B_EXECUTION_PLAN.md).

## Current state

The operator explicitly removed the timed-out final interpretation as a prerequisite for the first Colab smoke. Review 3 is a genuine preparation APPROVE, with the full isolated synthetic gate passed. Exact notebook SHA-256: `be4c49bcadd07c3cc9626dd6035c11974268df6331208eeaf4aad4e57d4ae371`. A byte-identical copy is delivered locally. Its private contract, input/membership and accounting bindings remain required; do not run with missing bindings. First fit is A1_repeat, fold 0, five smoke epochs, seed 101, workers 2, deliberate interruption/resume, then pause. Final interpretation and the preserved draft assessment follow returned smoke evidence. Full training remains held.

Idea 2 is now explicitly requested: the accepted synthesis's fixed 3?3 comparison of each saved model ranking against each saved predicted amount, on server CPU, no training. The scientific author must specify and implement it, followed by independent review. Existing item 6 execution is provider-specific and already completed; reuse its frozen evidence and shared accounting without relabeling or resetting the old run. No new analysis call or patient execution has occurred yet.

The author-only timeout patch is prepared at `7d9ed0c`: 1,800 seconds for both scientific author stages, plus the existing 60-second watchdog margin. Reviewer and default bounds are unchanged. Tests: 101 passed; four fixture setup errors reproduce on the unchanged baseline. The dedicated 28-test subset passes. Independent review is prepared but not started; the registration transport failed to connect and is awaiting server reconciliation before any retry. The patch is not installed.

The prior direction call is confirmed terminal FAILED, with no accepted submission and $1.4199795 counted. It returned a request timeout, not advice or approval. Fold the necessary direction questions into the timeout implementation review; do not repeat a standalone direction check. The previously installed timing-reader repair remains preserved; its subsequent scientific admission failed at a second reader before any reservation. No automatic timing retry, host pulse or GPU launch.

## Verification

Current candidate:386 regression tests pass. The strict read-only server test reproduced the original SQLite failure, passed the snapshot read, refused a genuine uncheckpointed journal, preserved original bytes/membership, and removed the private snapshot. The reviewed packet has922 files, including619 source files. Its current diff and test guide were checked against the exact Git source and transcript. Earlier test/setup failures are preserved; no full-suite pass is claimed. The previous complete admission/cap-refusal rehearsal still documents unchanged live ledgers, but it did not reproduce the confinement problem now covered by the server test.

## Money and calls

Today 28/50 model calls: 3 scientific authors (Colab correction, timing author 24, and the timed-out final Colab interpretation); 3 scientific reviewers (two failed Colab reviews and one approved preparation review); 18 administrative implementation reviews; and 4 direction calls/discussions. Administrative purposes: combined continuations; intake/disk; alignment; transport recovery; connection repair; entry-point/network continuation; preservation/admission; inspection recovery; installed combined bundle; reader/history bundle; native-review/Colab-turn continuation; import-context repair; bounded manifest-read recovery; the terminal/native-intent bundle; the native admission repair; its mechanical packet correction; a native-manifest-read qualification correction; and the terminal-ledger reader repair. Direction calls: one failed zero-cost check, two completed discussions and the timed-out repeated-failure direction check. Direction and accounting opinions were folded into these implementation reviews. All past usage stays counted; today's limit is 50.

Administrative reviews still consume most calls. Continue batching adjacent required repairs and direction opinions into one whole-component review; defer unrelated sandbox and rotation infrastructure until the next scientific result. No standalone direction call is planned before the next agreed trigger.

Administrative and direction model cost is $82.3648565; failed scientific-review cost $10.19855925; approved scientific-review cost $13.15064175; combined reported Claude cost $105.7140575. The terminal-ledger review cost $2.30716925. Author dollar totals are unavailable. Confirmed compute actual remains $24.39800404. Estimated stage-1 exposure is $115.516623/$150 and timing diagnostic exposure $5.405445/$25. The $1.118950 synthetic CPU reservation remains counted pending provider-confirmed actual billing. Item 6 cap $100, item4 total $1,275 and full-training projection gate $1,200 remain unchanged. No GPU retry or full training was started.

## Direction and judgments

2026-10-11 | direction call 28 | request timeout, no verdict | Preserve $1.4199795 and fold the next necessary direction question into the required implementation review.
2026-10-11 | operator update | Package the genuinely approved Colab preparation now; assess final draft after returned smoke. No new scientific conclusion or guard bypass.
2026-10-11 | timeout patch | Explicit author-only 1,800-second instruction, tested; normal independent review pending. No accounting or reviewer-limit change.
2026-10-11 | A100 capacity | Use operator-reported 6.77 CU/hour; record actual balance/time during smoke and retain coverage holds.

2026-10-11 17:24 UTC | 1 qualified round after the mechanical native-read correction | APPROVE / PROCEED | Independently review the actual patch; do not rely on stale earlier rationale. Install the narrow repair and proceed to reviewer16; keep Colab held for scientific assessment and defer unrelated infrastructure. Final review cost $5.03697425.

Judgments: preserve the zero-call allocation refusal; verify full admission on copies; refuse installation on stale review guidance; preserve the disqualified supplemental review and fix mandatory reading instructions without changing the qualifier; bind the actual same-source independent approval to installation. Original attempts, caps, reservations and refusals remain intact. No operator money decision is needed.

## Cleanup and backup

Cleanup is complete; never replay migration or deletion. The server verified 1,917,698 historical files /75,608,503,402bytes by hash before laptop removal. Disposable caches totaled18,317,762,560bytes; Codex logs were retained. C: now about 19.3 GiB free and WSL about 906 GiB. Server free space was160.6 GiB before the move,123.7 GiB afterward, and120.0 GiB now. Warn below 15 GiB; stop below 8 GiB or unknown capacity. No setup commands or disk purchase are needed.

Withheld: evidence folders, ledgers, review packets, native streams, private authority/provenance, all *_PRIVATE* files, patient rows/identifiers/images/masks/caches, and raw private Git ancestry. New private bindings include docs/NATIVE_REVIEW_ACTIVATION_PRIVATE.json and docs/COLAB_FINAL_AUTHOR_TERMINAL_PRIVATE.json. The scanned source projection is merged into remote-server after genuine APPROVE and both real service checks. The safe working branch is also retained for history. Installed releases remain on remote-server. Never merge main or edit BACKLOG.

Last verified remote-server before this update:`dc75186341cbf4278163fd9ffc2bdd4985d7ad2f`. Installed source projection was pushed. The installed ledger-read source projection is merged here; the separately scanned working branch is retained for history.

2026-10-11 18:21 UTC | The actual service exposed a read-only SQLite bookkeeping failure before any reservation. Preserve the run; replace only the read mechanism with an exact private snapshot and fail-closed journal/hash checks. No writable paths added.386 tests and synthetic confined controls pass. Claude accounting/confinement and overhead judgment were folded into the review; genuine APPROVE and both installation checks are complete.

2026-10-11 18:21 UTC | 1 administrative round | APPROVE; reviewer judged this narrow repair the shortest safe path | Installed source76e56df after386 tests and both real verification checks. The first installation transport timeout had zero effects and no running request, positively reconciled before one bounded transport retry. All original records retained; no model or compute retry occurred. No explicit categorical direction label was returned.

2026-10-11 18:38 UTC | Repeated same-cause failure at a second ledger reader: park timing, preserve the attempt and zero-call outcome, consult Claude before another repair/retry. No scientific code changed. Direction outcome pending.
