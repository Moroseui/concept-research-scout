# Research status

- Item 6 and synthesis remain accepted; 352 rounded Sprint14 values match the same saved fits/cohort, not independent retraining.
- Colab preparation is approved; its final author timed out and the draft still needs scientific assessment.
- The read-only ledger repair is independently approved and installed; 386 tests and both installation checks passed.
- One scientific timing-review start is being reconciled. No GPU job has started.
- Confirmed compute actual: $24.40; stage1 exposure: $115.52/$150. Reported Claude charges: $104.29; author dollars unavailable.
- Next expected result: scientific judgment of the saved CPU evidence, about 15-30 minutes if admission succeeds. See the [plan](13B_EXECUTION_PLAN.md).
- Action needed: none. Today 27/50 calls before scientific admission. C: about 19.3 GiB free. No swap point.

## Current state ? October11,18:21UTC

The installed native-review admission repair at source `9e2816b` passed both connection checks. Its actual scientific service then stopped before model admission: SQLite could not create bookkeeping files for the separate, read-only Colab ledger. The run is terminal, with no reviewer16 reservation or charge. Do not restart or pulse it. The original ledger and scientific state are unchanged.

A narrow repair at source `76e56df232da49da8e4f73163b24312235b2ad8d` reads a private snapshot of the exact frozen ledger, checks original hashes and absence of journals before and after, and removes the snapshot. It adds no writable path. The original failure and the fixed behavior were reproduced under strict read-only server confinement on synthetic data; genuine uncheckpointed journals are refused. All386 regression tests pass, including retained predecessor-service checks. Claude independently approved source76e56df as call27, with no findings; report b57065d4d57e08768c94ba0d2b24a31999cd362a7c4f87f906396f4055cd073c. Installation completed and both actual verification checks passed. A single normal host start for scientific reviewer16 has been requested; reconcile it before any further launch. No GPU job has started.

The approved repair is installed. One normal host start for scientific reviewer16 is being reconciled; reuse the existing native CPU PASS and activation, never repeat them. That reviewer must accept the evidence before the capped CPU-starvation GPU diagnostic. Colab's separate final-author draft remains unaccepted and held for scientific assessment. Full training and coverage-dependent arms remain held.

The first same-source administrative report was qualified but followed stale packet guides, so it was insufficient alone. The next review assessed the actual patch but failed native qualification because it omitted the manifest read. Both originals and charges remain counted. The final review `dce9fd714538ec6482813bada594dc827e95a9997f02b28f3c8d8873daf64efe` is genuinely qualified APPROVE, report `001ea72281ccb25b0eaf0d5d0881966d2b46ae68c036f661fb7f621d53a6b48c`. It independently covers the current patch. Installation binds that substantive approval alongside the preserved original installer binding; the stale rationale supplies no current-patch coverage.

Colab preparation review 3 approved the specification and notebook preparation. The final interpretation author then reached its 900-second timeout; its draft raises limitations and remains unaccepted. Original UNCERTAIN rows and charges are preserved, with positive evidence that its process is terminal. Colab stays BLOCKED. Do not restart that author or invent a receipt. Its scientific assessment and the first operator instructions remain pending. Full training and coverage-dependent arms remain held.

## Verification

Current candidate:386 regression tests pass. The strict read-only server test reproduced the original SQLite failure, passed the snapshot read, refused a genuine uncheckpointed journal, preserved original bytes/membership, and removed the private snapshot. The reviewed packet has922 files, including619 source files. Its current diff and test guide were checked against the exact Git source and transcript. Earlier test/setup failures are preserved; no full-suite pass is claimed. The previous complete admission/cap-refusal rehearsal still documents unchanged live ledgers, but it did not reproduce the confinement problem now covered by the server test.

## Money and calls

Today 27/50 model calls: 3 scientific authors (Colab correction, timing author 24, and the timed-out final Colab interpretation); 3 scientific reviewers (two failed Colab reviews and one approved preparation review); 18 administrative implementation reviews; and 3 direction calls/discussions. Administrative purposes: combined continuations; intake/disk; alignment; transport recovery; connection repair; entry-point/network continuation; preservation/admission; inspection recovery; installed combined bundle; reader/history bundle; native-review/Colab-turn continuation; import-context repair; bounded manifest-read recovery; the terminal/native-intent bundle; the native admission repair; its mechanical packet correction; a native-manifest-read qualification correction; and the current terminal-ledger reader repair. Direction calls: one failed zero-cost check and two completed discussions. Direction and accounting opinions were folded into these implementation reviews. All past usage stays counted; today's limit is 50.

Administrative reviews still consume most calls. Continue batching adjacent required repairs and direction opinions into one whole-component review; defer unrelated sandbox and rotation infrastructure until the next scientific result. No standalone direction call is planned before the next agreed trigger.

Completed administrative model cost is $80.944877; failed scientific-review cost $10.19855925; approved scientific-review cost $13.15064175; combined reported Claude cost $104.294078. The terminal-ledger review cost $2.30716925. Author dollar totals are unavailable. Confirmed compute actual remains $24.39800404. Estimated stage-1 exposure is $115.516623/$150 and timing diagnostic exposure $5.405445/$25. The $1.118950 synthetic CPU reservation remains counted pending provider-confirmed actual billing. Item 6 cap $100, item4 total $1,275 and full-training projection gate $1,200 remain unchanged. No GPU retry or full training was started.

## Direction and judgments

2026-10-11 17:24 UTC | 1 qualified round after the mechanical native-read correction | APPROVE / PROCEED | Independently review the actual patch; do not rely on stale earlier rationale. Install the narrow repair and proceed to reviewer16; keep Colab held for scientific assessment and defer unrelated infrastructure. Final review cost $5.03697425.

Judgments: preserve the zero-call allocation refusal; verify full admission on copies; refuse installation on stale review guidance; preserve the disqualified supplemental review and fix mandatory reading instructions without changing the qualifier; bind the actual same-source independent approval to installation. Original attempts, caps, reservations and refusals remain intact. No operator money decision is needed.

## Cleanup and backup

Cleanup is complete; never replay migration or deletion. The server verified 1,917,698 historical files /75,608,503,402bytes by hash before laptop removal. Disposable caches totaled18,317,762,560bytes; Codex logs were retained. C: now about 19.3 GiB free and WSL about 906 GiB. Server free space was160.6 GiB before the move,123.7 GiB afterward, and120.0 GiB now. Warn below 15 GiB; stop below 8 GiB or unknown capacity. No setup commands or disk purchase are needed.

Withheld: evidence folders, ledgers, review packets, native streams, private authority/provenance, all *_PRIVATE* files, patient rows/identifiers/images/masks/caches, and raw private Git ancestry. New private bindings include docs/NATIVE_REVIEW_ACTIVATION_PRIVATE.json and docs/COLAB_FINAL_AUTHOR_TERMINAL_PRIVATE.json. The scanned source projection is merged into remote-server after genuine APPROVE and both real service checks. The safe working branch is also retained for history. Installed releases remain on remote-server. Never merge main or edit BACKLOG.

Last verified remote-server before this update:`d57c17ed994db2c3a5755068c2f581942969ceeb`. Installed source projection was pushed. The installed ledger-read source projection is merged here; the separately scanned working branch is retained for history.

2026-10-11 18:21 UTC | The actual service exposed a read-only SQLite bookkeeping failure before any reservation. Preserve the run; replace only the read mechanism with an exact private snapshot and fail-closed journal/hash checks. No writable paths added.386 tests and synthetic confined controls pass. Claude accounting/confinement and overhead judgment were folded into the review; genuine APPROVE and both installation checks are complete.

2026-10-11 18:21 UTC | 1 administrative round | APPROVE; reviewer judged this narrow repair the shortest safe path | Installed source76e56df after386 tests and both real verification checks. The first installation transport timeout had zero effects and no running request, positively reconciled before one bounded transport retry. All original records retained; no model or compute retry occurred. No explicit categorical direction label was returned.
