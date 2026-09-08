# 047b saved console recovered; scientific acceptance remains gated

The `incoming-notebook-evidence` stage ran read-only on the operator-supplied
saved notebook. [Its receipt](047B_NOTEBOOK_INTAKE_20260907.json) binds the
implementation hash, original notebook, extracted stream, contract and both result
commits. Original bytes, all saved streams and provenance are retained privately;
no notebook cells were executed. Original failure evidence remains separate.

Cell index 7 (execution count 7, eighth notebook cell) contains one saved stdout
stream of 9,466 bytes. It includes the Phase B contract and STUDY_COMPLETE. Its
embedded summary equals the parsed Phase B summary at both `940293b6` and
`c8124212`; the two committed summary files are byte-identical. Embedded JSON
formatting differs from the file, so this is semantic equality of the embedded
summary, not a claim of identical formatting. Notebook SHA-256:
`0f38603e579633e017bd1ba5be11f15d7bff373762e5729778edcd29195cf7ce`.
Stream SHA-256:
`00a247582691bdec7fff74633443cc0cfe9391ac7ea4bdd393274d6699a95bca`.

This resolves the absence of genuine saved successful-session output. It does not
prove that the notebook retained every process-output byte or that its stream is
identical to the original Drive sibling log. No exit status was saved: the old
launcher piped Python through tee without capturing the Python exit code. The
receipt therefore records null, not zero. The notebook pins launcher checkout
`6280d76a16c5e4739c8f32739e11a89e9b8177e3`; `940293b6` identifies the results
commit, not the notebook's executable checkout.

Read-only source inspection confirms the omission: the launcher writes beside
OUTPUT_DIR with append-mode tee; the uploader copies only OUTPUT_DIR. The saved
notebook must remain unchanged. Current generated launchers already preserve the
console beside their export. The added collection stage copies it to a private
handoff directory, verifies the bytes, and binds a private receipt to the export
inventory and source/contract before announcing handoff readiness. This is not a
public-artifact allowlist expansion.

The existing connected Colab worker has exhausted its bounded connection session;
its termination does not establish the status of any remote job. The original
Drive sibling has not been checked in this intake. A targeted read-only check of
that log can supplement these saved outputs when the existing mounted runtime is
accessible; do not rerun the notebook or reconnect blindly.

Next lifecycle work is review of this evidence disposition, historical registry
attestation, exclusions/audit publication semantics, and the separately reserved
scientific landing decision. The cleanup approval accepts three retained metadata
files for that first cleanup only; it does not authorize a new scientific import.
The 17-required-artifact policy still blocks the 16-file cleanup projection.
No analysis, interpretation, result import or scientific acceptance ran in this
stage. The prior missing-console searches remain valid historical bounded searches.

## Reproduce the intake privately

Use `python -m orchestrator.notebook_evidence --help`. Supply exact source and
replacement commits, contract, the Phase B summary path, the preserved private
Git repository, the original notebook path and a fresh private destination.
The command never executes cells. It emits only a correspondence receipt; raw
outputs and local source paths remain in the private evidence directory.

## Review and validation

The author-operated Claude review approved source and the permitted intake receipt
at `7ed2605505a0a3b3beda3dd1443baa8cb136ab2c`. It did not receive the raw
notebook/console, run tests, or grant scientific acceptance. See the attributed
[review receipt](047B_NOTEBOOK_REVIEW_20260907.json). It agreed that the evidence
resolves saved-output availability to the limited extent stated here.

Eight focused tests passed, including real generated export, repeated collection,
missing/conflicting/partial evidence refusal, and saved-output versus cell-source
separation. The initial generated-cell test failed on an undefined CONSOLE name;
the generator was corrected to derive the sibling path and embed its source pin,
then passed. No frozen scientific code was changed.

The public intake receipt's supplemental `intake_implementation_sha256` was added
by Astra's recorder using Python hashlib over orchestrator/notebook_evidence.py
at the reviewed commit. It is not a field emitted by the original intake function;
the private stage receipt remains unchanged. Console collection binds the caller's
supplied metadata; the generated caller obtains its inventory from export_session.
Collection does not independently authenticate caller claims or replace scientific
validation. These limits address the review's documentation suggestions.
