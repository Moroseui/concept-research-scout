# Codex Linux sandbox compatibility

Actual non-root preflight failed first with `bwrap: loopback: Failed RTM_NEWADDR:
Operation not permitted`; the existing network-enabled workspace configuration
then failed with `bwrap: setting up uid map: Permission denied`. No model was
called. Kernel records identify the `unprivileged_userns` AppArmor profile, and
`kernel.apparmor_restrict_unprivileged_userns` is 1. Original logs remain private.

The prepared repair follows Ubuntu's application-specific user-namespace profile
route. It keeps the global restriction enabled, binds the installed Codex 0.153.4
native binary and bundled helper by SHA-256, and restricts binary execution to the
driver/reviewer model-client group. It gives those programs the user namespaces
needed to construct their own sandbox; it does not grant sudo, host root, model
credentials or publication authority. The profile's `unconfined` flag is Ubuntu's
per-application compatibility mechanism, not a global AppArmor disable. This does
increase those model clients' access to user-namespace kernel interfaces.

Before claiming success, the installer must run an actual non-model command,
allow a workspace write, deny a write outside the workspace where the user would
otherwise have OS write access, and deny scientific-worker invocation of Codex.
It refuses altered/unprotected binaries, unknown existing profiles or unexpected
group membership. No API call or authentication is part of this test. Existing
synthetic systemd workers do not use Codex and remain independent.

Source: [Ubuntu 24.04 release notes, user namespace restrictions](https://discourse.ubuntu.com/t/ubuntu-24-04-lts-noble-numbat-release-notes/39890),
[Ubuntu AppArmor security documentation](https://documentation.ubuntu.com/security/security-features/privilege-restriction/apparmor/).
This document records a prepared repair; only a later actual host receipt proves application and validation.
