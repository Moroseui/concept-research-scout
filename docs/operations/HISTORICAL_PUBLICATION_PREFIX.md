# Existing public decision evidence: narrow prefix preservation

The expanded case-identifier scan rejected an append to `evidence/decisions.md`
because that already-public file contains ten historical identifier occurrences.
The new operating decision added zero occurrences. No publication occurred during
that refusal; the local commit was preserved.

The history auditor now recognizes only the exact SHA-256-bound bytes of this
one file at public baseline `2cb97cec43a07b3ab908329d38c509215237081f`, and requires
that baseline in the audited public ancestor history. The outgoing file must
begin with those bytes unchanged. New appended bytes receive the full scan;
existing bytes still receive all non-identifier checks. Copying this content to
another path, changing the prefix, adding identifiers or credentials all refuse.
Direct artifact/summary scans have no grandfathering exception. This preserves
historical scientific evidence without authorizing new case-level publication.

This is a deliberate, narrow remaining public exposure, not anonymization or a
universal privacy guarantee. The separate 047 cleanup and case-linked metadata
decisions remain unchanged. Publication credentials can still bypass client-side
checks; the remote driver and worker receive none pending the protected writer
design. Tests exercise both permitted preservation and forbidden additions.

The first focused exception review requested a boundary guard: the preserved
prefix must end with a newline, so appends cannot extend its final identifier.
The actual pinned public prefix already has that boundary; the explicit guard and
a rejecting synthetic fixture now enforce it. Unexpected Git ancestry errors
also fail closed. The original rejected review remains private and attributed.

The next review identified a pre-existing path-pattern hole in the history auditor.
Changed names are now matched byte-for-byte against the complete NUL-delimited
Git tree, and bytes are read by the matched blob object identity. Pattern-shaped
filenames cannot hide a blob or borrow another entry's mode. Tests reject unsafe
content under unusual names and a pattern-shaped symlink. Actual tree absence
is the only deletion case. No original commit or review was rewritten.

The subsequent review rejected the broad Python scanner exception. It is removed.
All formats and filenames now receive identifier/credential checks. One additional
historical allowance is limited to `tests/test_git_publication.py`: exactly one
unchanged newline-terminated fixture line from the SHA-256-pinned public baseline
file. Duplicate or altered lines, extra identifiers and other paths refuse. This
allows old local commits to preserve an inherited public synthetic fixture; the
final test source splits that literal and needs no exception. The decision-prefix
and public test-line allowances preserve historical identifiers. A third, separately
SHA-bound allowance covers exactly `tests/test_operations_report.py` as supplied in
the approved review at `1900522275c7f8b74836432cef5a8ebd605c1840` (SHA-256
`46aa7a14b8390cc16562f21863fb1c80499c73441209f3b727b50b8e00424b3d`).
That new test file contains a deliberately synthetic identifier-rejection fixture,
not patient input. It is not claimed to be an already-public baseline. Any byte
change or other path loses that allowance. These are the complete explicit
identifier exceptions in the history scanner; there is no format-wide exemption.
Direct artifact and summary scans retain neither exception.

The delegated pilot auditor also now reads modes and blobs from byte-exact tree
entries. It no longer allows a pattern-shaped symlink to borrow a regular file's
mode. Its branch/path/history quarantines remain in force; this does not broaden
pilot publication authority or relax a refusal caused by historical content.
