# External fit monitoring before item4 paid admission

Operator decision: periodic monitoring belongs to the server job loop. No new
experiment, scientific method, cap, or patient scope is granted. This is an
implementation requirement, not a claim that the connection is live.

Reuse Modal provider status/logs, the native nnU-Net training log, and committed
per-fit checkpoint records on the existing private Volume. Do not add a worker
heartbeat service. Observe independently from the training process and keep the
observations in the existing private execution receipts.

The controller should poll active work about once per minute, collect completed
returns, and admit the next ready wave using the existing actual billing and
budget checks. Observation/network failures are UNKNOWN, never proof of a stall
or permission to duplicate a fit. Logs remain private. Record the provider job
identity, observation time, last complete epoch line and its time, recent epoch
durations, checkpoint epoch/time/hash and current execution phase.

A stall requires positively RUNNING status and repeated valid observations in
which neither native training progress nor committed checkpoints advance. Use
at least five times the slowest recent complete epoch (or the same-environment
smoke timing before enough local epochs exist), with a minimum 15-minute grace
and at least two successful observations beyond the threshold. Account for the
configured checkpoint interval; a missing checkpoint between scheduled saves is
not a stall while the epoch log advances. Ordinary non-epoch log chatter is not
training progress. Initialization, preprocessing and scoring need their own
observed phase progress/time expectations; the epoch rule must not kill them.
These operational defaults must be tested and bound in the execution receipt.

Immediately before stopping, reobserve: any epoch/checkpoint advancement cancels
the stop. Preserve a stop intent and the bound observations; stop only that exact
provider job once. Confirm it is terminal, authenticate the last committed
checkpoint through terminal_fit_checkpoint, then record interruption using the
existing owner transaction and same-fit resume path. No terminal proof means no
resume; no usable checkpoint means no automatic fresh start. Preserve the prior
reservation and charge. A stalled job is an interruption, not a scientific
failure or completed result. A repeated unexplained stall requires diagnosis,
not an unbounded restart loop.

Connection work still required: provider health observation; scheduler's monitor,
collect and next-wave transition; a validated STALL interruption reason in the
existing item4 accounting consumer; server restart recovery of a stop intent;
and a real deliberately interrupted smoke proving checkpoint resume. All go
through focused tests, full suites, submit_review and held promotion. The author
and independent scientific reviewer still own notebook scientific adaptations.

Set the platform timeout generously above the measured expected fit/phase time,
within 86400 seconds. It is a last-resort cap, not the health detector. Bind this
lifetime to the existing conservative cost reservation so longer timeouts cannot
hide spending or exceed the smoke/total caps. Do not use provider automatic retry
or resume from scratch. Work requiring more than one bounded segment must retain
the same fit identity and verified checkpoint continuation.

Acceptance tests must cover advancing log with old checkpoint; advancing
checkpoint with quiet log; slow but normally advancing epochs; warmup and scoring;
missing/malformed signals; transient network errors; a real sustained stall;
progress immediately before stop; repeated observations/stop-intent recovery;
terminal-proof failure; same-fit resume without another realization; and result
collection/next-wave admission while other jobs run. Live smoke must verify the
actual signals and deliberate interruption before the full screen relies on it.

References checked: Modal Sandboxes (https://modal.com/docs/guide/sandboxes)
documents poll/termination and the 24-hour maximum. Modal Volumes
(https://modal.com/docs/guide/volumes) documents explicit v2 sync commits. Use the
installed pinned SDK implementation when connecting the observer.

Draft implementation checkpoint: ModalProvider.fit_health now reads the exact
per-fit native log and authenticates small committed checkpoint records against
the fit/Volume bindings. It deliberately does not download weights on each poll;
terminal_fit_checkpoint still hashes the payload before resume. assess tracks
successful observations using controller time, ignores ordinary log chatter,
requires two overdue observations, and returns a recheck-before-stop candidate.
Missing or changed evidence refuses; no stop/launch/accounting change is made by
these functions. Fifty-six producer/provider/health tests pass with synthetic
Volume data. The scheduler connection, stop-intent recovery, STALL accounting
reason and live interruption proof remain required before paid admission.


The executor now exposes `monitor_fit(job, native_log_path)` as one periodic transition. It preserves observations privately, replays their assessment, and requires two late observations plus an immediate third read before issuing a single recorded stop. Progress on that last read cancels the stop. A network/read failure never becomes a stall. A stop intent left incomplete is reconciliation-only and is not repeated automatically. The existing terminal checkpoint reader verifies the complete checkpoint payload, and the existing compute ledger records OBSERVED_TRAINING_STALL without releasing the previous charge. Ordinary same-fit segment admission remains required; monitoring never launches.

Deterministic connection tests use the actual executor, SQLite accounting, progress writer, provider readers and terminal proof against a synthetic Volume/SDK/clock. They cover retained charges, duplicate observation, an uncertain stop, last-read progress, guard failures, altered history and same-fit resume reservation. This is not live interruption evidence. Remaining connections: the actual worker supplies its exact native log path, the server's executor tick calls this method periodically, and the live smoke demonstrates interruption/resume. Startup and scoring use separate progress observations and the generous platform timeout; they are not classified by the epoch stall rule.
