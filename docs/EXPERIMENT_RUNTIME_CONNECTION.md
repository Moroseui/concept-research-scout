# Pinned scientific runtime connection

Item4 previously verified a wheel Volume but launched plain Python without loading those dependencies. The existing M3 offline installation mechanism is now connected to the item4 guard. It is infrastructure only: no preprocessing rule, trainer configuration, metric or scientific conclusion is implemented here.

Before reservation, an actual reviewed-module preflight requires scientific_environment in the immutable runtime and binding. The record contains the selected interpreter path, exact Python/CUDA/package versions and every wheel's size/hash. Its expected-environment hash must match the fit and preprocessing contract. The actual fit requires the pinned nnU-Net 2.8.1 and Torch/CUDA environment. No default interpreter or unpinned package fallback is permitted for that route. Root provisioning must supply this record from verified environment evidence; this code does not invent the expected values.

Inside the existing network-disabled container, the guard binds the already-mounted read-only wheel role to its exact Volume identity. Other aliases and overlapping roles refuse. It verifies wheel bytes and creates a fresh segment-specific temporary dependency target. Installation uses only binary wheels, no index, no dependency resolution, no cache, and hash-required requirements derived from the selected wheel records. It never installs into the host or image's existing Python tree. Missing or incompatible dependencies fail before scientific code imports.

The guard checks the actual interpreter and installed package metadata, including Torch's CUDA version, against the selected environment. It preserves a private per-segment installation log and exact observation receipt. Input verification can report VERIFIED only after that check. Collection verifies the original environment receipt and passes the actual observation with its hash in the existing native execution receipt. Missing, changed, duplicate-key or ambiguous records refuse. Repeated invocation still refuses at the original exclusive input-verification record; no install or execution retry is inferred.

The generic lower-level guard tests also exercise legacy three-role transport without an environment. Those are not a reviewed-module production admission: the real item4 preflight and launch both require the selected environment. M3 is unchanged.

Tests include an actual native bubblewrap run with networking unshared, a locally built synthetic wheel, real offline pip installation and a scientific fixture that imports the installed dependency. Wrong wheel bytes, Python and package versions, role overlap and repeated execution refuse. Provider-boundary tests use synthetic SDK/storage and synthetic environment metadata, explicitly labelled. These do not establish that a GPU image has been provisioned or that the real nnU-Net dependency closure works. That still requires the actual pinned image/lock provisioning and the authorized smoke.

Remaining critical connections are the scientific author's preprocessing module/executor and the root runtime producer. No paid fit or scientific result is claimed by this engineering change. It requires integrated tests and independent implementation review before installation.

## Preprocessing-to-dispatch handoff

The lane now has an actual `prepare-execution` command. As the lane's owning
account, run `python -m orchestrator.experiment_driver prepare-execution --state
LANE --jobs ROOT_SELECTED_JOBS_JSON --destination FRESH_PRIVATE_PREPARATION`.
The job list has the same `runtime` reference and base `binding` records that
`experiment_dispatch` consumes; it is not another scientific plan. This command
holds the existing driver lock, checks the actual lane guard and genuine
scientific approval, and emits the real provider packages. It never reserves a
call, starts a provider client, uploads, or submits a fit.

Preparation uses the same fit-selection checks as the live dispatcher. It
checks each actual package against its frozen fit and original approval; the
root-selected preprocessing/cohort records; the scientific module's identity;
and the original preprocessing validator receipt. The runtime selects that
receipt as `item4_preprocessing_validation: {path, sha256}`. Its validator and
preprocessing code hashes must equal the reviewed execution module hash.
`modal_preprocessing_receipt.check_validation` is shared with the original
receipt sealer: run/spec/cohort/input-contract/environment/output identities,
PASS and empty errors must all match. The selected module will own both
preprocessing and validation. Merely possessing outputs is insufficient.

The same read-only checks also validate the selected offline environment,
four distinct Volume roles, and the actual serialized input-guard payload and
its transport limit. No image bytes leave the private Volume. This is an
identity/contract preflight; the admitted worker still hashes actual data bytes
before scientific import, and the provider still performs its live inventory,
package/wheel, environment and billing checks before spending.

Root then runs `python -m orchestrator.experiment_provisioning --preparation
PREPARATION_JSON --sha256 RECORDED_HASH`. This opens no service database, calls
no SDK and imports no scientific module. It repeats the full file/binding
checks, locks the destination parent directory, writes only fresh root:1003
0440 records under a 0550 directory, and publishes READY last by rename after
its bytes are complete and fsynced. Lane initialization's preallocated empty
0550 root:1003 directory is supported without changing its metadata. Unsafe,
changed or partial existing records refuse. An identical completed publication
is verified and returned unchanged. No old state, permission or ownership is
modified. Root cannot use the service-account preparation command.

The next ordinary driver tick consumes this exact READY record through the
shared validator and rechecks the genuine scientific approval. READY grants
neither scientific acceptance nor a spending reservation; the existing
executor remains responsible for admission, costs, duplicates and live checks.
Tests exercise the real approval/ledger, package, preprocessing/environment
validators and next driver transition on explicitly synthetic scientific
fixtures. Separate native root tests exercise actual ownership and file modes;
they do not claim live preprocessing, Modal provisioning or paid execution.

Still required before a fit: the scientific author/reviewer must provide the
preprocessing and validation implementation; its executor must produce the
authenticated original receipts on the private Volume; and actual pinned
assets/dependencies must be provisioned. This handoff does not fabricate those
prerequisites or make the current draft operational. Integrated server suites
and independent implementation review remain mandatory before deployment.

## Reviewed preprocessing worker

The item4 notebook extraction now requires four exported entry points:
`main(input_root, output_root, contract)`, `preprocess(input_root, output_root,
contract)`, `validate_preprocessing(output_root, contract)` and
`synthetic_tests()`. Earlier non-execution notebook routes keep their existing
contract. Author and reviewer receive the same explicit interface. Infrastructure
does not supply preprocessing algorithms or a scientific PASS.

A preprocessing package adds a hash-bound cohort manifest and source-file
inventory. The real package verifier and reconstructed launch manifest check
them against the exact preprocessing selection in the frozen execution plan.
This avoids embedding a large source inventory in each command-line argument.
The worker verifies its complete package, code, source bytes and original
observed environment proof before importing the author's module. Preprocessing
is restricted to a CPU smoke job. It has no training completion path.

The author calls `contract['checkpoint'](step_id, files)` for each completed
step. Each map names new relative output paths with byte counts and hashes.
The wrapper checks their bytes and private modes, fsyncs files, preserves an
exclusive step record, and uses the existing bounded Volume-v2 commit helper.
Duplicate steps and overlapping paths refuse. On failure, completed steps and
the failed attempt remain; repeating the invocation cannot execute again.
Resumption requires an explicit, normally admitted recovery connection, which
is not implemented by this adapter.

The validator returns exactly `{proposed, validation}`. Both original objects
are preserved before qualification. The shared preprocessing contract checks
all 99 case identities and three case-file roles plus dataset, plans and splits,
source/code/environment/split bindings, PASS with empty errors and exact output
members, sizes and hashes. Every validated file must belong to a committed
step. Preprocessing observes the resulting plans-file hash; subsequent fit
consumers still require that exact hash. The worker never substitutes a native
training checkpoint, interprets results or grants scientific acceptance.

Tests run the actual package verifier, a fresh-process worker, the shared fit
consumer and original-receipt sealer. Cohorts, files, reviews and environment
observations are explicitly synthetic fixtures. Altered output, failed or
ambiguous validation, unsafe modes, changed environment, uncommitted outputs,
repeated execution and incomplete processing refuse with originals preserved.
No native nnU-Net preprocessing or scientific conclusion is established by them.

## CPU preprocessing provider and original-result collection

The actual Modal provider now dispatches a selected preprocessing binding through
the existing item4 executor and compute accounting. It requires CPU-only SMOKE,
segment one, no inferred retry, the fixed operator authorities, four distinct
Volume roles, the selected offline environment and the genuine reviewed package.
Input members derive from the existing authenticated development reader, with
an optional pinned-v3 CTP plan from the existing CTP reader. A free-form inventory
cannot substitute. SDK preflight checks member sets and sizes without reading
patient payloads into the controller; the native input guard hashes actual bytes
inside the confined worker before science imports.

The source inventory travels as a hash-checked package file. The launch sends a
small descriptor bound to the same package manifest and input contract, avoiding
the Linux per-argument limit. Existing no-alias, duplicate invocation, source-hash,
network-disabled and dependency controls remain. Only the output Volume is
writable. The existing executor reserves costs before creation and records a
single launch; HALT, caps and prior uncertain work still refuse normally.

Collection returns exactly five original metadata files: result, preprocessing,
validation, environment and input-verification records. A shared validator checks
these at observation and again on saved local collection replay. Processed
images, labels and properties stay on the private Volume. Exact validated output
member/size checks run before collection; each fit subsequently verifies bytes.
Repeated collection uses the existing saved manifest and transaction, so it
makes no second call, charge or termination. Positive failures preserve the
existing failed-execution record, full reservation and no-resubmission block.

Fits can select the original preprocessing job's artifacts subdirectory via the
pinned SDK's read-only sub_path mount. Preflight verifies the exact subdirectory
members before creation (the SDK would otherwise create a missing subdirectory).
Sibling records and other attempts are not mounted. Both runtime and fit binding
pin the preprocessing job hash. Root provisioning requires the original
item4_preprocessing_execution reference (path and hash), matching result,
validation and output identities, and preserves that reference in its handoff.
The legacy flat-volume contract remains supported unchanged.

Tests use real worker, executor, package, ledger and validators with synthetic
SDK/data/environment fixtures. Native input-guard tests exercise the large-map
file transport in the existing confined subprocess. No paid container, real
preprocessing or live sub_path alias behavior is claimed. Remaining prerequisites
are driver-owned preprocessing dispatch and publication, the actual source view
and dependencies, interrupted-preprocessing continuation, integrated server
suites and independent review before installation. The existing fit path remains
separately guarded. This draft is not an operational paid launch.

## Driver-owned preprocessing transitions

`experiment_driver prepare-preprocessing` uses the same owner-only command,
lock, scientific seal, package producer and root publication as
`prepare-execution`. It selects all preprocessing entries of the reviewed plan
in their declared order and verifies the pinned source readers and environment.
The root selection is published to a separate sibling of the fit-selection
directory, with the same private creation, immutable records, duplicate and
changed-record checks. It cannot change the existing fit selection or create
another scientific or compute allowance.

The ordinary `EXECUTE_EXPERIMENT` driver ticks now perform preprocessing package
preparation, upload, submission, observation and collection. Every paid operation
uses the existing executor and canonical experiment-owner verifier. A missing
runtime selection is a visible wait. RUNNING, UNKNOWN and unavailable observation
remain the same attempt; none is permission to resubmit. A terminal failure stops
with its existing evidence and reservation preserved. Preprocessing never uses
the training checkpoint monitor or counts as a fit or scientific acceptance.

After collection, each tick verifies the saved originals, their native schemas,
the immutable admitted package and the actual collection ledger row. Fit
preparation and dispatch require matching original result/validation hashes and
the selected private output Volume from one of these completed preprocessing
jobs. A root-selected unrelated receipt cannot substitute. The normal root fit
handoff and next fit package follow only after these checks. Repeated ticks leave
completed originals, model rows and compute reservations unchanged.

Connected tests drive the actual scientific qualifier on explicitly synthetic
review evidence, the ordinary driver, real uploader, package and worker, actual
canonical owner/admission and collection transactions, and the next fit package.
Only external SDK/storage/environment and the outer installation fixture are
synthetic; the production checks are not patched. A separate root scratch test
runs both publications with real ownership and modes. This is engineering
verification, not scientific execution or live service-user verification.

Remaining before paid use: actual source-view/dependency provisioning and live
mount proof, an interruption-safe preprocessing continuation, full integrated
server suites and independent review/deployment. The runtime selection must also
be exercised against the real smoke/benchmark-to-full-run sequence; this change
does not claim that future-wave provisioning or GPU selection has been proven.


## Interrupted preprocessing continuation

Preprocessing now preserves its exact binding and atomically publishes each
completed step record after verifying and syncing its files. Unfinished record
writes stay outside the committed-step index. A positively interrupted attempt
with committed steps can be reconciled by the lane owner with the existing
classified cause receipt (`PROVIDER_LIMIT`, `LIFETIME_TIMEOUT`, or the deliberate
smoke interruption). `experiment_driver reconcile-preprocessing --state LANE
--job JOB --reason RECEIPT` holds the normal lock and guard. Root cannot open the
owner's ledger through this command.

The provider must report a nonzero terminal process, verified original input and
environment records, the exact prior binding and committed steps. Unknown or
zero-exit-without-results is not proof. A recorded scientific/code failure or
returned validation is not eligible. The owner transaction preserves the prior
row and its full reservation, appending one terminal receipt and marking only
cost accounting complete. This is neither a scientific result nor new authority.
Duplicate reconciliation returns the same record. Normal caps, HALT, owner,
headroom and all unrelated uncertain-call controls still apply to a successor.

Ordinary ticks derive one linked segment with unchanged source, method, inputs,
environment, resources and runtime. The worker checks original step hashes and
copies only those bytes into a fresh private attempt on the same output Volume;
it never hardlinks writable artifacts or modifies the predecessor. It supplies
`completed_steps` to the unchanged reviewed module, which must reuse them and
compute only missing steps. Every original output is checked again at validation.
Continuation history is delivered with the eventual execution receipt; private
per-case step records are not inserted into scientific model contexts.

The hard-stop tests use an actual fresh worker process on synthetic inputs,
including interruption before atomic step publication, real terminal-reader and
SQLite transactions, and the real driver through resumed collection. The provider
and billing services are synthetic. No live paid interruption or resume is proven
by those tests. Observed provider-limit/lifetime cause collection must still be
connected to the unattended observer; generic UNKNOWN remains a visible wait.
Integrated server tests and independent review precede deployment.


### Incremental runtime provisioning

A reviewed plan can select `dispatch_mode: incremental`. Every scientific fit
stays in its frozen `fits` list. When preprocessing is declared, each fit names
one `preprocessing_id`, and every declared preprocessing step must have at least
one consuming fit. This is a dependency contract for the author and reviewer;
the controller does not invent coverage or preprocessing methods.

The existing owner `prepare-execution` / `prepare-preprocessing` commands accept
an ordered subset of previously unselected identities. The existing root
publisher appends a private `wave-NNNNNN.json`, linked to its predecessor hash.
It never replaces an earlier wave or runtime. Duplicate publication is a verified
no-op; duplicate identities, missing/replaced predecessors, source/runtime drift,
unsafe modes and changed frozen definitions refuse. The service preserves the
observed prefix hashes and verifies every original on later ticks.

Independent fits can use their exact completed preprocessing receipts while
unrelated steps remain unpublished or running. Running fit health is observed
before additional preprocessing. Completed aggregate outputs are collected and
validated as they arrive, with the original collection ledger and hashes, but a
partial selection never enters final interpretation or acceptance. The full
frozen fit set must finish for that transition.

This connects staged runtime provisioning and result availability. It does not
manufacture the benchmark-selected GPU, a smoke acceptance, or the measured
full-run cost projection: those remaining producers must consume genuine returns
before FULL admission can pass the existing gate. No new allowance, retry,
scientific scope, private-data route or confinement change is introduced.


### Benchmark selection and full-run measurements

The service-owner command `experiment_driver measure-benchmark --state ...`
replays the three original benchmark collections and real ledgers, then reads
current authenticated billing. It records the fastest GPU with the operator's
20-percent gain over the next-cheaper choice. Subsequent non-benchmark runtime
preparation must use that verified hardware record. Benchmark provisioning has
no circular dependence on its own result. No provider job or model is launched
by either measurement command.

`measure-projection` separately requires every frozen SMOKE collection, every
FULL fit's same-arm timing on the selected GPU, explicit reviewed extrapolation
assumptions/epochs/overheads, and the original deliberate-interruption ledger
and committed checkpoint followed by collected continuation. Full fits may
span bounded lifetime segments; the projection includes the whole duration,
while no provider lifetime is increased beyond 24 hours. Actual later admission
still reserves each segment and retains old charges.

Both commands preserve hash-bound original references and return
`MEASURED_NOT_ACCEPTED`. Repeated commands re-read original files and ledgers
without another billing request. Hardware comparisons are available before
later smoke fits; full projection remains unavailable until those fits finish.
The new code has no scientific acceptance or FULL-admission event producer.
The remaining connection must deliver these originals and the calculation to
the existing scientific author/reviewer path, preserve that genuine verdict,
and bind both the acceptance producer and FULL-admission consumer to its exact
record. The old generic event must not be manufactured to bridge that gap.
Neither a cost below the threshold nor a runtime validator is scientific
approval. Projections over the threshold remain explicit operator decisions.


### Conditional FULL admission from original smoke evidence

The operator already authorizes full training after the required smoke and
benchmark stage when the measured full projection is at most $1,200. The owner
command `record-full-admission` binds the genuine specification/code approval,
all original validated smoke collections, the three-GPU benchmark and selected
hardware, deliberate checkpoint/resume evidence and every projected full fit.
Its record says `REVIEWED_SMOKE_CONDITIONS_VERIFIED`, not scientific acceptance.
It creates no spending reservation, model call or new allowance. Final result
interpretation and independent review remain required.

Ordinary FULL admission reopens the actual owning lane read-only, replays those
originals, matches the selected full fit and its complete prepared package, and
recalculates the projection using the current authenticated billing prices. A
loose ACCEPTED amount has no authority. Existing caps, pending-call/uncertain-job
refusals, HALT, private-file checks, owner binding, headroom and duplicate controls
remain in the same transaction. The reservation retains the admission-record and
measurement hashes. Repeating the record or reservation cannot spend again.

Replay recomputes the package's derived code/specification/review fields from the
approved originals before comparing them with the preserved complete binding.
It never creates a missing package. Tests use actual package qualification,
selection, collection validation, local/global ledgers and admission. Synthetic
model/provider evidence is labelled; these are not live GPU or science results.

Remaining engineering before paid full execution includes the conservative
hard-timeout reservation versus actual-duration settlement connection. Original
reservations still count in full; this change does not release or refund them.


### Terminal exposure and successive waves

Item4 reserves the full hard runtime at admission. The executor writes a boot ID
and CLOCK_BOOTTIME stamp into the private creation intent before creating a
Sandbox. After authenticated positive termination, collection (or the next
ordinary submission after a recorded interruption) appends a terminal-exposure
record. Admission rechecks the original files and terminal ledger event. The
elapsed window includes provisioning, idle time and cleanup, rounds up to whole
seconds, and can never exceed the original timeout bound. All overhead remains
reserved. A missing clock, a start/stop spanning boots, an unknown outcome or a
legacy receipt retains the full reservation. A sealed same-boot proof remains
valid after a later reboot. No UTC timestamp is converted into a monotonic proof.

This is a conservative exposure bound, not a provider invoice or a refund.
Original autonomy_compute reservations, statuses and actual-charge values are
not changed by the bound recorder. Ordinary provider transitions are unchanged.
Prices use the greater of reservation and current authenticated rates. Per-app
commitments use the larger of terminal bounds and lifetime app billing, then add
all active reservations. Thus late billing cannot consume a new segment's remaining
reservation. An entirely terminal app whose bill exceeds its bound stops further
admission for diagnosis. Billing
high-water records are append-only per app and UTC cycle; lifetime totals sum
cycles so lagging reports and month rollover cannot erase observed spend. Only
authenticated prior-cycle billing is subtracted for current-cycle headroom;
lifetime run and stage caps still retain it. A
billing observation is preserved even if the subsequent admission is refused.
All existing ownership, uncertainty, HALT, concurrency and dollar gates remain.

The deterministic test uses the real submission, collection, ledger, recorder and
next-wave admission routes with synthetic provider/clock facts. It proves blocked
headroom becomes usable only after qualifying termination, duplicate collection
makes no second call, original charges remain, interrupted segments remain linked,
changed originals refuse, and billed excess survives lag and month rollover. It
is not evidence of a paid experiment or final scientific acceptance.

Provider documentation corroboration (actual installed SDK/live verification still
required): https://modal.com/docs/guide/sandbox-resources,
https://modal.com/docs/sdk/py/latest/Sandbox,
https://modal.com/docs/sdk/py/latest/billing.


### Existing source bytes in a data-only view

Preprocessing may select `/input-views/<frozen input inventory SHA256>` on its
existing source Volume. The same hash is bound in the root-selected runtime,
prepared package and preprocessing contract. The exact member checks and worker
hash/alias checks are unchanged. The view mount is read-only; package, wheel and
progress roles remain separate. Legacy flat source layouts still use the original
path. This reuses the fit consumer's subpath helper and changes no scientific code.

Connected tests carry the selection through actual provisioning preparation,
package emission and provider payload, then exercise real guard checks against
synthetic files. They do not establish that a live view has been published.
Before science: assemble only the verified development members, add the existing
99 frozen brain masks, verify every original size/hash, and prove the actual
Modal SDK's selected subpath and alias behavior. The completed image/CTP download
is preserved and must not be repeated. A real pinned nnU-Net wheel/environment
closure is a separate remaining provisioning prerequisite.
