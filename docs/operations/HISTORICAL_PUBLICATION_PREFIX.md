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
