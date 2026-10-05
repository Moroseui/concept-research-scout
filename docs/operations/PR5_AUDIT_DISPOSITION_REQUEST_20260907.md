# One additional historical audit disposition

**Proposed, not ratified. Activation remains blocked.** The read-only audit keeps
the original 82-commit range and binds its policy/ruling separately. After closing
Claude's parent-coverage finding it scanned 10 explicitly listed follow-up commits
as well, including merge ancestry and the added decision record: 932 blob versions.
One content refusal remained. No exception was added to make this pass.

- Commit: `cfadeb1b3ef250e981c596b4d36a75fff7e11b3d`.
- File: `evidence/decisions.md`.
- Git blob: `4ddfd8981e5e10c12086535ab8ae788a600221bf`.
- SHA-256: `a6136fdb72224857b1f18948bbc2965d97f2090ee73a4cedc6703e7fb7690b91`.
- Refusal: `CASE_LEVEL_RECORD_REJECTED`.

Direct byte comparison establishes that this entire older file is an exact prefix
of the already pinned decisions baseline at
`2cb97cec43a07b3ab908329d38c509215237081f`. The current exception authorizes that
baseline followed by checked additions; it does not authorize shorter historical
versions. This is an actual policy refusal. The byte relationship explains it,
but does not supply the missing disposition or excuse other findings.

Recommendation for the operator and independent desk: preserve history and allow
this one exact earlier decisions blob in the retrospective audit, with the same
content checks after the already accepted historical identifiers are substituted.
Any implementation would require focused review and a repeated original-range
audit; no general prefix, path, case-data or new-publication exemption is proposed.
Do not repeat the identifiers in the public ruling. An approval here would not
approve 047 cleanup, scientific landing, live publication grants or activation.

Until that decision and reviewed implementation, report the audit as
**BLOCKED_FINDINGS**, not PASS. The original full inventory and rejected review
are preserved separately. This request does not supersede the original range,
metadata coverage or added-decision coverage requirements.
