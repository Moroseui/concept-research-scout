# RC4 portability-only candidate

RC3 baseline bcf64853c9e9f84539899180888d1561266fd0b9 is preserved. No driver stage, admission, accounting, scientific method, credential rule, old service or deployment control changes.

1. `manual_isolation.command`: keep the existing empty site-packages mask when the directory exists. When Ubuntu has no such stdlib child, leave it absent. No host directory, added host mount, writable stdlib or relaxed systemd property.
2. `runtime.rc4-review.json`: use a separate exact-byte copy of the installed Codex0.153.4 package. Its original bundled codex/bwrap executables are mode0750 root:GID983, inaccessible to partho. The copy is root:partho with directories/executables0550 and data0440. It exposes the same package at /tools/codex; no existing package or service-user group changes. Exact source inventory SHA256: 058cac31fb919981af3f85849d196c5118a4921e6a61fa1632f588d6948bdccf. The copied package, config and hash receipts are in the external review evidence folder.
3. Python3.12 test packages already exist in the separate new-lane environment. The previous inventory query quoting error is corrected read-only; it was not a package absence. Configured Claude2.0.37 is the exact separate laptop-tested package; newer system Claude remains unchanged and unsupported by this adapter.

Runtime identity remains configuration-bound. The installed RC3 source, original runtime config, old units and original rollback inventory are unchanged. RC4 is only a pre-review test checkout; no login or model call is allowed before the operator-managed independent review approves.

4. Test-only login fixture: explicitly bind synthetic logins to its temporary home, even with a server runtime configuration. A regression keeps a configured host-login sentinel unchanged. Production credential handling is unchanged.

## Observed verification limit

The first RC4 server attempt (fc99f0ed, preserved separately) passed both outer live denial probes (21 checks each) and44 focused tests, but failed Codex's nested sandbox check and errored in5 tests due to the fixture above. Kernel audit at2026-09-26 06:25:34 UTC records AppArmor unpriv_bwrap denying sys_admin to bwrap. The installed profile intentionally denies capabilities to children. Static namespace sysctls and supported flags were insufficient to establish nested compatibility.

No AppArmor, capabilities, systemd property, mount set, native sandbox or test expectation was weakened. This host security-policy incompatibility remains BLOCKED. The full server suites did not start after the focused failure. The final fixture correction receives deterministic local checks only; it is not falsely credited with a successful server run. No login/model call or deployment is permitted on this evidence. Resolving nested execution under unchanged confinement is the next required technical decision, outside this portability patch's demonstrated result.

## Later authorized host verification and fixture corrections

The operator subsequently authorized the scoped /usr/bin/bwrap AppArmor userns exception. Actual before/after profile and host evidence are in the external manual-review/apparmor folder; the global restriction, outer filesystem boundary and inner sandbox are retained. Both live outer probes and51 focused checks then passed. This supersedes the runtime-blocked checkpoint above without removing its original evidence.

The full server suite exposed two additional fixture portability assumptions: next(events.iterdir()) removed .lock on ext4 rather than a JSON event; the synthetic legacy-installer fixture left its existing-installation lookup on a real protected /etc path. Tests now select a sorted JSON event and redirect that one path to synthetic private state while retaining the real guard. Two negative guard tests assert existing synthetic controller/broker files still refuse before commands or writes. No production installer, reader, authority, privacy or isolation gate changed.
