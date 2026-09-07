# P001: concrete next decision, launch still held

The system readiness proposal was approved by a fresh Claude reviewer at working
source `039c4f327ea0e9c5655aa030ae244e3457d29a0f`:
[candidate](../../campaigns/isles24-pilot/pipeline/p001-readiness-20260907-v3/round-1/readiness.md),
[exact proposed bindings](../../campaigns/isles24-pilot/pipeline/p001-readiness-20260907-v3/round-1/launch_decision.proposed.json),
[review](../../campaigns/isles24-pilot/pipeline/p001-readiness-20260907-v3/round-1/review.json).
This is a reviewed proposal, not adoption or launch authority.

## Recommendation

Prospectively ratify the reviewed prediction charter and conditionally adopt the
externally seeded P001 as the unchanged minimal reference. Preserve the old
charter, scores, source and approvals. It predicts follow-up infarct after observed
treatment from admission Tmax, using the exposed 99-case development cohort;
results will be exploratory. Baseline plus at most two subsequent comparisons
remains the envelope. No follow-up is selected and no patient result exists.

For the first baseline, prefer the preserved **CPU Colab manual notebook route**
if current archive access and execution state can be verified. Its source is
`d6a1184b4378e849213fd887a6f7b103fb1a64d5`, notebook
`1a81c037343598f4e4585153b11d761b87a9ae3a`, preserved execution checkout
`0770c7dcabe781cbfb87de505755e7aafa758f2e`. Do not regenerate from the moving
working branch or use Run All before the gates below. This preserves the reviewed
one-CPU-Colab-run contract. Historical approval is not current launch permission.

The Linux server avoids repeated browser consent for computation, but is not yet
a P001-compatible approved backend: prepare a thin launcher/amendment preserving
scientific code, pinned dependencies, member selection and private evidence;
review affected transport/resource gates, then obtain separate input-transfer and
launch approval. No GPU or new spending is needed for that proposal. Synthetic
Linux execution is not P001 execution. Colab's shorter review path is a recommendation,
not a measured speed or completion guarantee; the one-shot worker handoff is a
real operational limitation, so manual notebook operation remains supported.

## Unit and input evidence

The official pinned starter supports decoded Tmax seconds. It does not recommend
changing P001's threshold to the starter's nine-second illustration. A versioned
synthetic decoder check, using numpy 2.3.3 and nibabel 5.3.2, confirms proxy
slope/intercept handling agrees with get_fdata at P001's frozen float32 precision.
One deliberately near-threshold value differs from float64; this is recorded,
not used to change precision or the strict >6.0 rule. These checks establish no
patient-map or v3-specific unit identity.

Historical Drive archive read-back remains verified in its original receipt.
The new worker actually executed CPU and metadata checks: Drive was absent then.
The operator subsequently mounted it. That later mount is operator-reported;
the one-shot worker had closed its MCP connection, so current archive presence
has not been independently retrieved. Preserve the tab/runtime. Do not ask for
another fresh connection until its continuation/retrieval path is ready.

## Exact proposed authorization and stopping points

The immediate scientific decision is **prospective charter ratification and
conditional external-seed adoption**, together with permission for a narrowly
bounded eligible-admission input preflight if desired. Such a preflight would
reconcile existing P001 process/output/checkpoint state; check the single preserved
archive path and disk capacity; apply the approved archive/member integrity checks;
and inspect only permitted admission Tmax header/scaling metadata to resolve
v3 applicability. No reserved case, outcome-based tuning or whole-archive
extraction is permitted. Do not treat absence of a visible job as proof it never
started. A failed check preserves evidence and holds execution.

The final launch decision remains separate and must bind the selected backend,
unchanged specification/source/dependencies, verified input receipt, private output
path and reconciled attempt identity. One CPU run, 60 analysis minutes, exactly 99
eligible completions, no scientific amendment, no new spend. This document grants
none of those permissions; no launch occurs automatically on charter adoption.

After an authorized return, use the existing campaign validate-bundle,
record-result and interpret-build commands documented in
[CAMPAIGN_COMMANDS.md](../isles-pilot/CAMPAIGN_COMMANDS.md), supplying the private
checkpoint directory and actual sibling console to validation. Publish only the
five permitted aggregate files after validation. Interpret and independently
cross-family review the actual measured result before selecting a follow-up.
P001 does not wait for 047 acceptance or unattended deployment activation.
