# Private Git transport diagnostics

This repair captures original stderr for GitLedger, the controlled Git publisher
(including branch creation), and bounded exact-object provenance retrieval. It
changes neither retries nor admission/publication permissions. Checked failures
raise with exit status and an opaque receipt ID; unchecked CAS failures retain
private stderr too. Timeouts preserve bytes written before termination. No
command arguments, input, stdout or stderr are copied into the public exception.

For supervised local use, receipts use a current-user-owned 0700 directory under
`/tmp`. Before hosted verification configure `RESEARCH_GIT_DIAGNOSTICS` to a
pre-created private 0700 directory owned by that runtime identity, outside any
checkout. Files are 0600. Preserve the directory through the existing private
evidence route before ephemeral runners terminate or reboot. Never upload it as
a public Actions artifact or place its stderr in model context. Per-process
stderr files are original evidence; the small receipt records exit/timeout and
byte identity. Failed diagnostic setup refuses before Git execution.

This is source implementation, not installed hosted evidence. It cannot recover
the original PR failure's missing stderr. The OPEN exit-128 transport finding is
not assigned a root cause by this repair. Actual droplet contention/recovery with
isolated state remains required. No live credentials, limiter state or timer is
activated. Retention/backup and private retrieval on the deployed host must be
verified before claiming durable hosted diagnostics.
