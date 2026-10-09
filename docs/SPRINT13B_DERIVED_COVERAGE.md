# Sprint13B coverage survey and revised method

Status: surveyed before deriving any patient mask. The earlier map-based draft
was never installed or used on patient arrays. It is superseded by the operator's
CTP decision (SHA256 27738b1204a929e37dc6a65a2318dfbb39018575e476cdb73a4815ad99980e4c),
recorded verbatim in SPRINT13B_CTP_COVERAGE_OPERATOR_DECISION.txt. The old draft
remains in Git history (ad5bcc80); it is removed from active source so it cannot
be mistaken for the selected method. The unfinished loader is preserved privately.

## What the release provides

The official Zenodo release lists raw admission 4D CTP and an NCCT-registered
CTP derivative, alongside the four derived perfusion maps. Its documented file
tree lists no acquisition/FOV mask or registration-transform file. That is a
statement about the published description, not proof that every possible
supplement lacks a mask. The authors' code repository documents the same CTP
paths. Sources:

- https://zenodo.org/records/16813698 (v3, the locally preserved source version)
- https://zenodo.org/records/17652035 (v7, current public release)
- https://github.com/ezequieldlrosa/isles24/blob/main/README.md

The official descriptions do not specify the registered CTP padding value or a
validated recipe for recovering FOV from time-series intensities. These details
must be checked label-blind, not invented or inferred from perfusion-map zeros.
The v3 archive checksum is MD5 36ae28b9a17f7340b8bbef62b595cb57; v7 is a different
archive. Do not silently mix release versions.

## Our local copy: observed metadata

A fresh allowlisted survey of all 99 development cases in source-extract-v1
found 0 raw CTP files and 0 registered CTP files, and no coverage/FOV-named
members in those admission directories. No patient image bytes were read.
The existing extracted copy is therefore insufficient for CTP-derived coverage.

The previously verified v3 source archive still exists on the existing private
Drive. It is 99,014,629,647 bytes, matching its preservation receipt. Reading
only the signature and encoded metadata (40,336 bytes, CRC-validated) found:

- 99 raw CTP and 99 registered CTP members for the frozen development cohort;
- 47,772,428,991 bytes of compressed NIfTI registered CTP members in that cohort;
- no coverage-, FOV-, validity- or transform-named member for those cases;
- 92 of those registered CTP members share solid-compression blocks with
  non-development cases.

The archive header survey consumed no patient payloads. The historical full
archive verification is preserved, not represented as a fresh full-file hash.
Never decompress a mixed block to recover selected files: doing so would decode
other patients even if their output files were discarded. The archive is not
absent; safe selective extraction is the remaining delivery problem.

A public per-file mirror has been checked at fixed revision
7bead709cd9f60ed6bea866b7a994a8ecc83db16: all 99 selected registered CTP files
have sizes matching the official archive and have LFS SHA256 identities.
No image payload was fetched by the survey. The mirror cites v2 and our archive
is v3; a subsequent check of the official Zenodo metadata resolves that version
concern: v2 and v3 publish the same 99,014,629,647-byte train.7z with MD5
36ae28b9a17f7340b8bbef62b595cb57. V7 has a different checksum and is not being
silently substituted. The exact metadata and their hashes are preserved in
CTP_RELEASE_VERSION_RECONCILIATION.json. This establishes the published archive
identity, not independent authentication of third-party mirror file bytes.
Before use, download only frozen-cohort registered CTP paths from that fixed
revision, verify each complete file against its LFS SHA256 and the official
archive member's size and CRC32, and preserve a separate retrieval receipt.
CRC32 is an integrity check, not a cryptographic source-authenticity proof;
this limitation belongs in normal review with the method and loader. Do not use the mirror's rendered
previews or combined data shards, which include patients outside our cohort.
Prefer an official per-file source if available. Existing locked exclusions apply
to requests, downloaded bytes, decompression and output files.

## Proposed fixed rule for normal review

Use only the registered 4D admission CTP and the registered brain mask. Verify
source identities, the frozen99 membership, full spatial affine/shape against
NCCT, time dimension and finite-value behavior before deriving support.

After independently confirming the registered series' padding convention:
for voxel x, count frames that are finite and differ from that confirmed padding
value. A conservative proposed support is brain(x), finite in all frames, and
non-padding in at least two frames. Keep the count/fraction as QC alongside the
binary mask. This criterion is a proposed rule for review, not yet frozen for
training. It uses no enhancement threshold, temporal-variance threshold, outcome
label, lesion size, or perfusion-map value. In particular, true zero CBF/CBV/MTT/
Tmax values remain eligible when CTP establishes support. Negative CT values are
not automatically rejected just because they are negative.

If the padding convention is not established, or missing frames/motion/padding
make the rule ambiguous, refuse that case/arm pending label-blind clarification;
never fall back to map nonzero values. No hole filling or intensity optimization
against outcomes. Record boundary interpolation and partial-time support as
limitations: this is a derived registered-CTP acquisition-support estimate, not
a supplied hardware acquisition mask or proof of exact native scanner FOV.

Bind input SHA256s, method version, padding evidence, frame count, spatial grid,
mask SHA256, excluded/partial-support counts and review to preprocessing receipts
and the run fingerprint. The normalization reference rule is separate: coverage
must not silently determine a tissue-reference or contralateral-region rule.

## Sequencing

A1 repeats, multiwindow and whole-L keep baseline preprocessing and may pass their
smoke gates independently of this coverage work. Freeze multiwindows label-blind.
CT normalization proceeds with perfusion handling matched to the fresh pnorm_v2
comparator; resolve only any actual shared comparator/reference dependency.
Z-score/histogram-equalized perfusion requires the reviewed CTP loader and support.
All arms retain frozen split, environment, data-contract, budget, restart and
independent scientific/implementation-review gates. No paid work has started.

## Evidence and next acceptance

Private evidence (not public payloads): REGISTERED_CTP_LOCAL_SURVEY.summary.json,
ARCHIVE_CTP_SURVEY.summary.json, ARCHIVE_CTP_MEMBERS.private.json, archived header
bytes and metadata-only reader extents. The reader refuses any payload-range read.
Official-page captures and mirror metadata are hash-preserved separately.

Next: resolve scoped CTP delivery without touching locked patients, inspect
label-blind padding/grid/time-series metadata, implement the selected rule and
loader in a NEW notebook copy, test true-zero maps/CTP padding/partial frames/
grid mismatch/allowlist enforcement, then normal full suites and independent
review before use. This survey is not a claim of completed coverage or training.

## First allowlisted retrieval and header check

One development registered CTP file was subsequently fetched from the pinned
per-file route, with no requests for excluded patients. Its complete bytes passed
LFS SHA256, official archive member size/CRC32, and an independent disk reread.
The private receipt is CTP_ONE_FILE_RETRIEVAL.private.json. This is integrity
verification of mirror bytes, subject to the source-authenticity limitation above.
The other 98 have not been downloaded by this step.

Its header establishes a four-dimensional series with 44 frames; spatial shape
and affine match the corresponding NCCT exactly. Only that allowlisted NCCT's
header was read for this comparison. The CTP time-spacing field is zero and time
units are unknown: do not infer acquisition seconds from this header. Support/QC
must count frames unless an authenticated timing source is provided. This one
case's agreement is not a substitute for checks on every case.

CTP_FIRST_HEADER.private.json and CTP_FIRST_GRID_CHECK.json bind these checks.
Padding is still unverified; descriptive signal/boundary QC must not silently
turn into an accepted acquisition-mask definition. No coverage mask, normalized
map, label-based tuning or training was produced. The proposed two-frame support
threshold is explicitly provisional and requires the normal scientific review.

### Observed signal and boundary evidence (first development case only)

A complete, frame-by-frame label-blind read of this one registered CTP found all
voxels finite, no voxel zero throughout all 44 frames, and all six outer faces
exactly -1000 in every frame. Thus treating zero as the CTP padding value would
be wrong for this file. These observations are recorded in
CTP_FIRST_SIGNAL_QC.private.json and CTP_FIRST_BOUNDARY_QC.private.json. No brain
mask, lesion label or derived perfusion map was used in these descriptive checks.

-1000 is an observed candidate padding sentinel for this case, not a declaration
for the cohort and not proof of native scanner FOV. The reviewed loader must
check each file, brain-mask/NCCT registration, boundary interpolation and temporal
support; it must not replace this with a hard-coded cohort-wide zero or -1000
assumption. A derived support mask will carry the method, source/QC identities and
limitations. No coverage mask has yet been generated or accepted. Coverage-
independent arms do not depend on completing this mask definition.
