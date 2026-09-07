# Human control launch-path repair

Actual source update to eb40b9549e2cf94145c5b886a7390f549f2123e4 succeeded:
three retained/consumed model turns, unchanged ledger, no new model, timer or writer.
The new verifier then failed at its first root status invocation, before any
control change. Original logs are preserved in a fresh private server evidence
directory. Current control state remained revision 2, not paused; all tasks and
jobs remained complete. A separate direct non-root status command succeeded.

Root cause: the reviewed verification transport deliberately uses PATH=/usr/bin:/bin;
controller_command selected bare runuser, installed on Ubuntu at /usr/sbin/runuser.
The child never started. The correction uses the absolute fixed executable path;
it does not broaden PATH, select another user, grant sudo, start a job or change
any source/permission checks. A regression verifies the exact fixed executable
and scrubbed child environment. Reuse the reviewed updater and exact hashed source
transport; repeat only the failed human-controls acceptance in a fresh directory.

Fresh review scope is this one-line transport correction and regression. Previous
controls, publication, notification and permission-packet approvals remain valid
for their unchanged source. The subsequent final deployed evidence review will
cover the actual new installed source and human workflow outcomes.
