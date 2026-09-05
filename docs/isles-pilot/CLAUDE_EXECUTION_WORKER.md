# Claude execution worker

The operator authorized Claude Code as a Colab execution worker on 2026-09-05,
in addition to its separate independent-review role. Codex remains investigator
and implementation lead. This does not amend the P001 scientific contract,
ratify a result, authorize the pending cleanup, or permit reserved-cohort access.
Fresh worker sessions and fresh reviewer sessions must remain separate.

The committed remote synthetic receipt at 04385ed is preserved byte-for-byte.
It reports real Colab acquisition, writing, separate retrieval and matching
synthetic text/SHA-256. Claude discovered notebook tools; Codex did not. CPU
support is the absence of a GPU request and nvidia-smi, not hardware attestation.
The receipt reports tool results; it is not an independently replayed transcript.
Its extra read-only transport cell is distinct from the unchanged pinned cells.
Do not reconstruct the subprocess console that MCP failed to return.

`python -m orchestrator.colab_worker verify-handoff` checks the pinned receipt
and notebook bytes. `worker-handoff --private-dir PATH` invokes an actual fresh
Claude subscription worker, supplies a bounded synthetic task, retains its raw
response privately, and accepts only the exact expected result and actual Fable
model identity. This demonstrates request/status/result integration, not another
remote execution. CLI failure, timeout or malformed output stays a failure.
The private directory must be new and outside the checkout. The worker uses
`--mcp-config /home/partho/.local/share/isles-colab-mcp/claude-worker.json`
and `--strict-mcp-config`. No global MCP registration or reviewer command changes.
The private configuration contains the working WSL environment; regenerate its
interoperability value if the WSL session changes. Never publish that file.

`prepare-p001 --private-dir PATH` verifies the existing P001 review, reads the
notebook at 1a81c037343598f4e4585153b11d761b87a9ae3a, and prepares original
cells and separately hashed supplementary transport wrappers. It enables no
patient execution. Wrappers execute the exact scientific source in the kernel
namespace while redirecting Python streams and subprocess file descriptors to
private append-only transport consoles. Failures retain tracebacks privately
and return only FAILED plus a source hash. Successful completion emits only
COMPLETE plus the source hash. Never infer scientific success from transport
completion; the P001 return validator remains mandatory.

Before patient execution: independent review of the adapter, a CPU browser
connection, operator Drive authorization and the exact archive/staged-root path
are required. Preserve the original pinned cells; record parameter overrides
and transport cells separately. Do not let model tools read private notebook
outputs or consoles. Copy transport logs from /content to private Drive storage
before disconnect, retaining the runner's original sibling .console.log and
.private checkpoint/prediction tree. The transport logs supplement, never
replace, the runner console required by the existing validator.

No filename allowlist alone authorizes model disclosure. Validate the five-file
P001 aggregate bundle semantically against the private checkpoints and original
console using the pinned validator in the pinned dependency environment, with
all validation stdout/stderr captured privately. Only validated aggregate values
and typed execution metadata may be returned. Do not display raw failure text.
The local investigator must subsequently run existing `validate-bundle`,
`record-result` and `interpret-build` with `--campaign isles24-pilot
--experiment P001` and private return paths when those artifacts are available.
No return is present yet; no P001 metric or next comparison is claimed.

Manual Run All in the approved notebook remains available. An MCP failure does
not justify modifying scientific code, approvals, eligible cases or stopping rules.
