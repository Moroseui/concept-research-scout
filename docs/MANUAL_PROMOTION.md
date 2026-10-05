# Held versioned promotion and host safeguards

Scope: RC4 successor only; independent approval of this new source/configuration
and promotion remains required. RC4 866171cca4b118b4ba435835561057645409fcd1,
its report, installed RC3, old scientific outcomes and six-call lane remain
unchanged. No model calls, logins or live installation during preparation.

## Release and recovery

`tools/deploy_manual_lane.py promote` uses `tools/manual_promotion.py`.
It verifies a clean annotated tag, full commit, exact approval report hash,
APPROVE heading and `runtime_sha256: <full hash>` in that report. This is the
existing operator-managed review trust boundary, not cryptographic proof of
reviewer identity. Original independent review/session evidence stays private.

Every release has a distinct source, runtime config, writable repository/state,
service/timer pair, install receipt, hash list and generated rollback. Source
files are immutable. Selection is recorded atomically. Promotion is always
held: predecessor and successor services must be disabled/inactive; no model
may be running or uncertain. No lane initialization, migration or automatic
enablement is performed. The successor CLI refuses historical RC3 live install
and rollback subcommands; they remain scratch-testable for original receipts.
The original installed RC3 files are not modified. The service account is checked before any write.
Partial operations retain an intent and refuse blind retry.
Configuration lives in `/etc/research-system-manual-sprint10/releases/<tag>`,
a new root-owned namespace: the RC3 config parent is partho-owned and unchanged.
The root hook refuses any runtime/lane other than the root-selected release.
Promotion refuses once any retained server lane is initialized, including after
rollback. Migrating an initialized lane needs a separately reviewed change;
this tool must not mint another six-call allowance by creating a new repository.

Rollback validates predecessor and successor bindings, refuses an active service
or pending call, stops/disables only its own units, archives/removes only its
own installed unit files and restores the previous selection. Source, runtime,
new scientific state and receipts remain preserved. Both releases remain held;
rollback does not enable any of the 18 old units, or restart research. Run
`systemctl daemon-reload` after promotion/rollback, then verify disabled state.

Host policy is a separate reviewed operation, not a side effect of rollback.
Keeping the scoped host protection and needrestart exclusion during a source
rollback prevents renewed interruptions. Explicit policy revert restores the
vendor enforcing bwrap policy; it will intentionally make the current nested
sandbox refuse until a suitable reviewed policy is installed again.

## Host controls and accepted risk

`tools/manual_policy.py` migrates the currently approved scoped policy from the
package-owned file to `/etc/apparmor.d/research-manual-bwrap`. It atomically
restores the original package file and creates its exact disable link. It
reloads only the specified policy file. Original `unpriv_bwrap` definition is
preserved. Revert uses atomic replace, fsync and a mandatory loaded
`bwrap (enforce)` readback. Global user namespace restriction must remain 1.

Accepted risk: **any process can create user namespaces through /usr/bin/bwrap**.
The scoped AppArmor exception increases kernel attack surface. It does not grant
models host files, service control or privileges; the outer filesystem jail,
dropped capabilities and native Codex inner sandbox remain mandatory.

A root-owned needrestart configuration excludes only services whose names begin
`research-manual-sprint10-` (or that exact base service). The root preflight verifies
that exclusion, the scoped AppArmor profile and loaded mode, vendor disable link,
original vendor hash and global user-namespace restriction. It uses Python `-s`,
refuses user-site loading, and emits the same invocation/runtime-bound proof.
There is no timer acquire, release, mask, unmask or start operation and no post-hook.
The preflight runs before every transition, including idle WAIT_OUTPUTS; it no
longer reads task phase/SQLite because that inspection served only the removed
hold. The separate promotion/rollback no-call reader still drops privileges.

Operator decision after the observed native timer failure: **remove upgrade holds**.
There is no reviewed timer-only configuration switch. Omitting `host_guard` would
also disable required host checks, so it is not an acceptable alternative. Runtime
configuration remains byte-identical; the removal is an independently reviewed
source successor, never an edit of an installed release.

Accepted residual risk: unattended or administrator-initiated upgrades can change
packages after preflight or disrupt an in-flight invocation. The needrestart
exclusion prevents its matching automatic service restarts, not every possible
package disruption. Whole-package and AppArmor/nested checks detect pre-existing
changes before a call is reserved/charged. Disruption after reservation may still
consume a call and leave it uncertain; the existing uncertain-call and duplicate
protections block further work for reconciliation. No refund, retry, extra
allowance or relaxed sandbox is authorized by accepting this risk.

The preflight uses systemd's `+` executable prefix, trusted immutable source and
fixed policy paths. The driver remains partho under the reviewed service
restrictions. No sudo grant, credential access or model tool is added.

Before reservation the driver checks a fresh root-owned proof bound to the same
systemd invocation, boot and runtime bytes, verifies the whole immutable Codex
and Claude packages, runs credential-free native Codex `sandbox` inside the
outer jail, then the role's existing denial probe. Any failure prevents
reservation/charge. Package bytes, additions/removals, modes and internal alias
layout are covered. Live root ownership/non-writability is also required.
A pinned launcher alone no longer suffices. No tool is silently upgraded.

## Post-approval sequence (no new general authorization needed)

1. Reconcile old-state snapshot, all 18 holds, new lane jobs and current profile.
2. Verify approved tag/report/runtime, source clean and tool inventories unchanged.
3. Run held `promote` with the preserved predecessor record and old inventory.
4. Save installation receipt/hash list off-server; verify all installed files.
5. Verify and reuse the completed bound host-policy migration and needrestart
   exclusion. Do not rerun installation into existing policy destinations.
6. Retain the scratch promotion/rollback receipt and completed RC3 live rollback
   rehearsal. The current request does not require repeating that live rehearsal.
7. daemon-reload, confirm both new units disabled, verify root preflight and package/
   nested/denial probes as the service user; no credential is needed for probes.
8. Stop at the operator's dedicated Codex and Claude setup-token logins.
9. Only after logins and six-call owner/budget checks: initialize/enable the lane,
   stop at WAIT_OUTPUTS for Colab CPU execution, collect by SCP, then finish.

No source promotion creates sustained scientific autonomy or a new call budget.
The previous manual known-case success and all earlier failed attempts remain
unchanged. AppArmor policy/revert and service runtime evidence on Ubuntu remain
post-approval live checks; scratch evidence must not be described as live.

References: Ubuntu's [profile disabling instructions](https://documentation.ubuntu.com/server/how-to/security/apparmor/index.html)
and the installed `systemd.service(5)` executable-prefix documentation. Exact
current server observations and prior RC4 receipts accompany the review folder.


## Current preflight and recovery boundary

The single privileged preflight uses `/usr/bin/python3 -s -B` and refuses unless
`sys.flags.no_user_site` is true. Root never parses the lane database: the separate
promotion/rollback no-call reader uses isolated Python after dropping UID/GID.

No collection-hold proof or `--collecting` pre-hook override remains. Collection
uses the ordinary driver `advance --collect-folder <exact extracted return>` with
the same service restrictions and ordinary preflight. Existing return validation,
identity, preservation and duplicate/uncertain collection checks are unchanged.

Status/report preserve host-policy refusals and explicitly state that timer control
was removed by operator decision. Any matching old `upgrade-hold.json` is labelled
**historical**, not used as evidence that a timer is currently held. Original
failed INTENT/refusal records must not be erased or converted into successful holds.
The exact approved restoration recovered active/enabled scheduling, but its final
cross-filesystem `os.replace` failed. That original script and failure remain
preserved in the private deployment record; do not rerun it. Metadata finalization
is a separate recorded recovery step, not a reason to change source or timer state.

**Rollback followed by manual init is operator-only.** Rollback preserves all
new state and restores no old research routes. Initializing a lane after rollback
creates a new model-call allowance, even when the previous release is empty.
It requires a new explicit operator decision identifying that allowance. Neither
rollback authority, the existing six-call grant, nor successful source review
authorizes this manual init. No automatic rollback/init sequence is supported.
