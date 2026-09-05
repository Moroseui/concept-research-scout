# P001 worker execution handoff

The operator authorized locating the existing archive by filename/path metadata,
Drive mounting with operator consent, a reviewed P001 dispatch, and the existing
validation/import/interpretation lifecycle. This does not authorize results-branch
cleanup, reserved-case extraction, new scientific comparisons, or new billing.

`python -m orchestrator.colab_patient mount --private-dir NEW_PRIVATE_DIRECTORY`
prepares a plain, unexecuted drive.mount cell and runs only a CPU/Colab check.
The operator runs the mount cell in the browser and grants Google consent there.
Authorization output is not captured or read by the worker. An earlier wrapped
mount was refused by the worker because it would hide and persist consent output;
that attempt did not mount Drive or scan metadata. This is not an approval bypass.

`locate --private-dir NEW_PRIVATE_DIRECTORY` then runs only the CPU check and
filename/path metadata search in the mounted runtime. The search walks MyDrive
and shared-drive metadata for train.7z and stats matching files; it never opens
archive contents or patient images. It also checks the versioned notebook's
/content/train.7z candidate. It reports matching paths, sizes and scan completeness,
never other filenames. An incomplete scan is not proof of absence. Multiple
plausible candidates require operator selection. The old 047 phenotype staging
directory is not an imaging DATA_ROOT substitute.

`prepare` and `dispatch` additionally require `--archive ACTUAL_COLAB_PATH`.
They verify the original P001 scientific approval and a completed fresh patient
adapter review at reviews/p001-dispatch-approved.{execution,response}.json,
bound to the exact current adapter, capture dependency, tests, documentation and
scientific reference files. The required scope is p001-patient-dispatch and the
required reviewer is Fable. A request for Fable with a different reported model
is not silently relabeled as a Fable approval. Worker sessions can use Claude
fallback models; requested and actual model IDs are recorded separately.
No approval is created by preparing a packet or by a worker saying COMPLETE.

The scientific source stays d6a1184b4378e849213fd887a6f7b103fb1a64d5 and the
original notebook stays 1a81c037343598f4e4585153b11d761b87a9ae3a. Packet parameters
record the actual ARCHIVE separately. DATA_ROOT is None; the original runner
can reuse its own verified private staging. Original notebook bytes are retained
privately. The already-mounted Drive replaces notebook cell 2's interactive mount
and placeholder parameters; original dependency, analysis and publication cells
3/4/5 execute unchanged in a separate Python process. The acquisition cell is
also unchanged, executed inside the private transport wrapper. No broad clone.

Output remains /content/drive/MyDrive/isles-pilot/P001-v1. Launcher and transport
records are sibling P001-v1.worker and P001-v1.launch.console.log; scientific
outputs, original P001-v1.console.log and P001-v1.private stay under the original
runner's control. A pre-existing worker directory causes a nondestructive refusal,
not a second launch. Failed launcher-owned attempts receive FAILED status. Reruns
need investigator inspection and a deliberate separate handoff; never delete
checkpoints or evidence to make a rerun pass. CPU, Drive and existing 7z are checked
before dispatch. No GPU or paid provisioning is requested.

The worker launches a detached child, so a long archive verification is not killed
by the MCP cell timeout. DISPATCHED is not successful analysis. The original runner
enforces archive size/MD5, exactly 198 selected members, frozen 99 eligible cases,
checkpoint identity and the 60-minute analysis cap. Archive verification/staging
is timed separately under the existing specification. `poll` executes only a CPU
check and fixed status lookup. It cannot relaunch, mount Drive or read logs. A
not-visible job requires restoring access to the same private Drive location.

All scientific stdout, subprocess fd output and exceptions remain private. The
child calls the original semantic return validator after the pinned cells, then
captures only its byte-verified five aggregate files into validated_return.json.
The cell that prints the result card still executes, but its output is private
until semantic validation. The private P001-private-return.zip contains aggregate
files, original console, binding/index, predictions/checkpoints and prior private
failure records; it excludes staged input images. The full source artifacts and
consoles remain on Drive. Zip bytes and private audit contents must never be printed
or base64-encoded into model tools. Operator browser download/private transfer is
required before local record-result can validate the original audit evidence.

The committed original scientific review is preserved, not broadened by the new
adapter review. Once the private return is locally accessible, use the existing
pinned dependencies and built-in validate-bundle, record-result, interpret-build
commands with --campaign isles24-pilot --experiment P001. No scientific result or
interpretation is claimed before those gates pass. A FAILED run is a failed
experiment attempt, not evidence of poor predictive performance.
