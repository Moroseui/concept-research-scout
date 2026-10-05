# A preserved discussion with a missing disposition

The `disposition-request` command saves one explicit request to record the missing
Astra disposition of an already completed discussion and opposing review. It is
available only for a protected preflight input refusal, after an independently
reviewed correction is installed at a different source. It does not run a model
inline. The original task, its source, both scientific outputs and its blocked
stage remain unchanged.

Inspect the saved state with the existing installed control wrapper:

```text
research-system-live-control status
research-system-live-control research-inspect SCIENTIFIC_TASK_ID
```

The wrapper shows ordinary status and task inspection. Its fixed command list
does not include the specialized disposition commands. Use the installed native
module for those commands, on authenticated administrative SSH. Set the source
directory from the actual inspected installation; this example contains a
placeholder, not a pinned deployment:

```sh
RESEARCH_REVIEWED_SOURCE_ROOT=/opt/research-system/releases/CURRENT_SOURCE_COMMIT-research-handover/snapshot
```

After confirming that source and the exact reviewed repair application, the
following native commands use the same protected non-root controller transport:

```sh
/usr/bin/env -i PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$RESEARCH_REVIEWED_SOURCE_ROOT" /usr/bin/python3 -B -m orchestrator.handover_runtime --config /etc/research-system/live-research/controller.json disposition-status
```

```text
/usr/bin/env -i PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$RESEARCH_REVIEWED_SOURCE_ROOT" /usr/bin/python3 -B -m orchestrator.handover_runtime --config /etc/research-system/live-research/controller.json disposition-request OLD_TASK_ID --human --expected-source CURRENT_SOURCE_COMMIT --change-request REPAIR_REQUEST_ID --applied-event REPAIR_APPLIED_EVENT --reason "Record only the missing disposition from the preserved discussion and review."
```

The uppercase values stand for actual inspected identities, not literal defaults.
An agent must use the existing `--submitter` JSON attribution instead of claiming
`--human`. The command reports the saved request identity, its current source and
the original task/source. Repeating the identical request returns that same
identity; a conflicting request is refused. No hand-edited record is required.

The normal scientific controller service advances one queued successor after its
usual task queue has no eligible work. It checks the installed deployment,
current reviewed repair, protected original replies/refusal, human stop, pause,
input size, writer lock and ordinary admission limit. A single fresh Astra call
records the disposition. It imports the original discussion/review; it does not
repeat them. A negative review remains `NOT_ACCEPTED`. The disposition cannot
grant scientific execution, adopt a proposal or release a stop.

`QUEUED` means no new disposition has started. `RECONCILIATION_REQUIRED` means a
preflight refusal, uncertain start, failure or changed original requires inspection;
it never authorizes an automatic retry. If a provider completed but the controller
lost its receipt, the original-only command is:

```text
/usr/bin/env -i PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$RESEARCH_REVIEWED_SOURCE_ROOT" /usr/bin/python3 -B -m orchestrator.handover_runtime --config /etc/research-system/live-research/controller.json disposition-recover OLD_TASK_ID --human
```

Recovery retrieves and checks an existing completed protected response. If none
exists, it remains blocked and starts no model. The status retains the old task as
blocked even when the new linked disposition is complete.

A verified result becomes a fixed `DISPOSITION` event for the ordinary
investigator. Its evidence contains the original scientific packet and both
outputs, the new disposition, source identities and current repair criticism.
It does not make the blocked task a completed predecessor. The fresh investigator
still needs normal eligibility, independent review and a recorded disposition;
only that later completed investigator can select an ordinary eligible successor.
Old-task artifact references cannot be manufactured from the linked record.

The current linked disposition has an enforced maximum of 30,000 characters
and 30,002 characters in its saved JSON string, including the enclosing quotes.
Escaped newlines, quotes, backslashes and Unicode count toward the second limit.
The existing 80,000-byte limit on the complete serialized broker reply, including
its receipt, remains in force. The prompt and input measurement identify both
answer limits; receipt and future task context still require their actual size
checks before later admission.
An oversized response is preserved as a failed attempt for reconciliation; it is
not shortened, accepted, or automatically retried. This limit does not change
the preserved original discussion and review or their existing limits. Before a new investigator starts,
the system checks the saved evidence size and both eligibility inputs. It also
checks the later campaign disposition against the full allowed prior replies
and a summary bound derived from the registered artifact names and hashes.
These checks are capacity checks, not scientific judgments or permission to run.

The evidence presentation avoids printing certain identical records twice.
Inside the saved investigator evidence, a reference can point from the current
charter evidence to the exact same text already present in the full historical
proof in that file. The original proof stays literal. The reference identifies
its location and digest; reconstruction must reproduce the full original
evidence before it is used. Historical and current source labels stay distinct.

Eligibility may also carry a full current change history that repeats the old
history inside the proof. Only in that same prompt, the old prefix can refer to
the identical current prefix, retaining the old event count, event identities
and distinct head hash. Campaign reports carry a bounded current change view,
so their stored evidence does not depend on such an external prefix. The full
current policy likewise appears once in the trusted operating context; a
checked policy reference points to that literal in the same eligibility input.
Ordinary local decisions without the hosted context keep their policy literal.

Fresh hosted campaign inputs may replace eleven fixed grounding entries with
references to identical literal policy or scientific documents in the same
prompt. The context-disposition entry and unmatched material remain literal.
One identical outer REMOTE operating document may also refer directly to its
literal copy in the full trusted policy. References cannot point to other
references. The source, fixed document name and location, and exact bytes must
match before use.

These views change presentation only. Recovery restores the outer document view
before the earlier eligibility presentation layers; campaign grounding restores
through its own fixed literal targets. The full original operating context and
request grounding remain bound by their original receipt and input hashes.
Before the first campaign admission, both author and reviewer inputs are built
and checked through the same constructors used for dispatch and recovery,
including the permitted prior-answer size. The later disposition check and the
fresh checks against the actual saved result still apply.

These are source-versioned references, not summaries or requests to fetch
missing material. The system verifies each permitted target and reconstructs
the bound originals. Changed, absent, ambiguous or unsupported targets cause a
refusal. All unique scientific text, opposing criticism and qualifications
remain available to each role. Evidence and references remain untrusted content;
matching hashes establish identity, not approval. Historical wakes and receipts
are inspected in their original format, without rewriting their saved bytes.

All outputs and proof remain in the existing private controller state. Source
changes and operation results are distinct from scientific acceptance and from
standing activation. A saved request or completed transport does not release a
pause, reset accounting or authorize a new experiment.
