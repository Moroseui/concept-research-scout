# P001 authorized input preflight — preparation

The operator approved the exact readiness packet at `a94d886`, recorded in
`prediction_selection.json`. This preflight uses the existing CPU Colab archive;
no patient transfer to Linux or patient launch is authorized.

`scripts/p001_input_preflight.py` binds the exact approval and frozen runner hash,
requires numpy 2.3.3/nibabel 5.3.2, and first checks existing execution paths and
process metadata. Existing or incompletely visible execution holds the operation
for reconciliation. Absence in that checked runtime is not a global nonexecution
claim. The adapter never calls P001's run/predict/metrics functions.

The frozen selection routine verifies the 99-case cohort and member-manifest
identities. The preflight samples **one lexical first eligible admission Tmax**,
without outcome-based selection, to avoid duplicating full cohort staging merely
for unit/decoder readiness. It checks current full archive size and MD5, extracts
only that explicitly selected admission member, verifies its size/CRC through the
unchanged runner, and reads its NIfTI header/proxy scaling without materializing
voxels. No lesion label or reserved member is opened. The patient runner will
still perform all of its original 99-case input checks after a separate launch.

The fresh private attempt retains archive identity, input/header hashes, original
extraction console and failure evidence. The receipt exports aggregate metadata
only. A 90-minute overall preflight bound and pre-extraction disk check limit the
operation; this is staging/readiness time, not an expansion of the frozen 60-minute
scientific analysis cap. Existing attempts refuse instead of overwriting. No
automatic retries, new GPU or paid provisioning are involved.

A valid header or plausible scaling is **not** release-specific proof of seconds.
Combine the observed header with the pinned official starter's decoded-seconds
convention and applicable release documentation, and record residual assumptions
before the exact launch decision. Contradictory evidence stops and invokes the
existing amendment/review route, without changing the strict >6.0 threshold.

Synthetic tests verify admission-only selection, header access without voxel
materialization, and holds for existing/active execution. Fresh affected-surface
Claude review and a generated human-usable, private-console transport wrapper are
required before using this on the authorized input. No temporary browser or Drive
connection has been requested for it yet.
