# Experiment results connection (private draft, not installed)

The system author supplies the scientific checks and implementation. Each frozen
fit declares aggregate return filenames and validation check IDs. The reviewed
module writes `validation.json` binding the run, fit, spec, code, execution plan,
all other file hashes/sizes, and each check's PASS result with evidence filenames.
Missing, failed, ambiguous or unbound checks refuse. No infrastructure-written
scientific calculation or result interpretation is introduced.

The actual worker applies the existing private intake scanner before any return
payload is published on the Volume. The scanner implementation and secret
pattern are extracted unchanged into stdlib modules shared with the original
intake/publication callers; public scanner behavior is unchanged. Return files
must be aggregate UTF-8 JSON/CSV/Markdown/text, with every identifier refused.
Per-patient predictions, native checkpoints and masks remain on the approved
private Volume; they are not part of this server collection. Content classification
also depends on review: a text scanner is not proof that arbitrary anonymized rows
are aggregate. No wider data-transfer authority is implied.

The controller uses the existing ModalExecutor collection, ledger and cost
finalization. It repeats exact-file validation, preserves authentic collection
receipt hashes and scans, and performs one collection per tick. Repeated delivery
or collection cannot launch or charge another job. Changed files or receipts
refuse. Both interpretation roles receive original aggregate files by hash-checked
workspace reference, with validation, execution and package identities. There is
no concatenation of growing tables into each initial prompt. The result advances
to the existing interpretation author/reviewer pipeline; validation is not
independent scientific acceptance.

Verification uses synthetic provider and root-selection fixtures, with the real
worker, publisher, collection/ledger, validator and context assembly connections.
The scanner function AST is identical to source98b68. Native sandbox and both
full server suites, independent implementation review and installation remain
required. Preprocessing/provisioning, interruption recovery, concrete scientific
plans, item6 executor and final experiment acceptance/report connections remain
open; this draft does not establish M4 completion.
