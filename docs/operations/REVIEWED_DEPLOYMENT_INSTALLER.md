# Reviewed continuing upgrade

The root-only orchestrator.install_reviewed_deployment module installs one exact reviewed deployment and restarts only its idle broker/socket. It does not start a controller, model, scientific worker, completion poller or intake poller; it never enables a timer. GOVERNED bridge configuration and scientific worker activation are separate facts. Bounded deployed acceptance still needs its recorded authority. Standing timers remain held until the actual deployment, role, scientific lifecycle and intake conditions have passed.

Run the reviewed module from /etc/research-system/deployment-review/staging/<proposal SHA>/snapshot with Python -B. The fixed installation bundle is /etc/research-system/deployment-review/bundles/<proposal SHA>. The target release is /opt/research-system/releases/<source>-research-handover/snapshot. The executing staging source must be root protected, match every reviewed archive file and have the exact clean Git identity. Do not run an older installer over the existing live system.

```bash
cd /etc/research-system/deployment-review/staging/PROPOSAL_SHA/snapshot
/usr/bin/python3 -B -m orchestrator.install_reviewed_deployment apply \
  --bundle-sha256 PROPOSAL_SHA --source EXACT_SOURCE
```

The continuing profile has15 fixed targets, including the versioned live-research/report-evidence.json needed by current-source reports. The Issue6 unit and guide use /etc/research-system/issue-intake.json. Snapshot, material configuration/unit literals, prior originals, launcher identities, original independent Claude request/protocol/result/execution and actual change REVIEW chains must satisfy deployment_review first. No locally invented approval string or original install intent is sufficient authority.

The recovery literal is JSON with exactly schema, instructions, directories, units_before, previous_active, preserved_state_sha256 and preserved_blocked_tasks. Schema is reviewed-deployment-recovery/v1. Instructions is human-readable text. units_before is the unchanged result of units_observation(); inapplicable service properties on timer/socket interfaces are empty, with MainPID0. previous_active is {state:ABSENT} or {state:EXISTING,sha256,raw}, where raw contains the exact original UTF-8 pointer bytes. preserved_state_sha256 is state_fingerprint(original_broker_configuration).sha256. These read-only observations must be collected from actual installed state and included in the original review, not inferred from package filenames.

preserved_blocked_tasks maps exact terminal task IDs to {reason,binding_sha256}, using the stored reason and SHA256 of exact tasks.binding UTF-8 bytes. Only that reviewed unchanged BLOCKED set may remain alongside completed tasks. QUEUED/RUNNING work, other pending states, active scientific units or model children refuse. This permits repair while preserving the original timed-out P001 task; it never retries it or rewrites its status. All evidence, stage receipts and ledger files remain covered by the state fingerprint.

The nine directory entries use exact uid/gid/mode/before objects. before is ABSENT or EXISTING:

| Directory | UID:GID and mode |
| --- | --- |
| /var/lib/research-system/scientific-jobs | 0:9870750 |
| Its requests, outputs, snapshots and inputs children | 0:9870750 |
| /var/lib/research-system/handover-live-controller/scientific-versions | 997:9870700 |
| /var/lib/research-system/handover-live-controller/scientific-observation | 0:9870750 |
| /var/lib/research-system/issue-intake | 0:0 0700 |
| /etc/research-system/live-research/controls/issue-intake-attestations | 0:9870750 |

Use integer JSON modes. Existing directories must already match; only reviewed absent directories are created, with explicit chmod/chown after mkdir. Existing controller parent remains997:9870700. The fixed jobs configuration uses UID995/GID987, proposals at scientific-versions and only the empty scientific-jobs/inputs root. Empty inputs establishes no data connector or scientific data authority. Database files and original evidence are not initialized, cleared, migrated or restored by this installer.

The installer holds existing branch/admission and private upgrade locks. It verifies the actual reviewed previous state before begin_install, then records a separate operational intent. It stops the socket before the idle broker, installs exact reviewed source/target bytes, checks preserved logical SQLite state and regular evidence, records installation, selects the active pointer and starts only socket/broker. Effective unit fragments, drop-ins, side commands, ExecStart, User/Group, working directory and actual broker source are checked. Completed duplicate application returns its original receipt without another restart or admission. Original enabled states are recorded; no enable/disable command is issued.

The source/config install receipt precedes broker restart by design. The separate upgrade receipt establishes actual broker readback and says REVIEWED_UPGRADE_INSTALLED_WORKERS_HELD. Neither receipt says unattended activation occurred. A failure preserves the pre-install proof, operational intent, original reviewed literals, installed subset and named failure; it does not create a whole-upgrade success receipt. Repeating apply after a partial intent refuses.

Explicit restoration is available only after reconciling the preserved original attempt:

```bash
/usr/bin/python3 -B -m orchestrator.install_reviewed_deployment restore \
  --bundle-sha256 PROPOSAL_SHA --source EXACT_SOURCE
```

Restoration verifies the full actual original Claude proof without requiring an all-old or all-new current filesystem, then independently requires each current target to be exactly an approved old or new byte/access identity. Unknown changes, missing old targets, unknown active selection, changed research state or live work refuse before effects. It preserves recognized temporary writes, restores exact original target bytes and active selection, leaves the new release and evidence intact, and restarts only the prior broker/socket. New target files are retained inside the private bundle. It never rewinds a database, deletes results, resumes research or converts the partial upgrade into success. An interrupted restoration itself requires reconciliation, not automatic retry.

The original-review-only verifier mode is explicit check_current=False and returns current_state_checked:false. It is used only for restoration evidence checking. begin_install, record_install and verify_installed always perform current-state checks; tests observe those defaults. A malicious root administrator replacing the reviewed code remains outside this protection boundary.
