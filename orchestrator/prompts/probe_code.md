<!-- stage: probe_code -->
Human approval has been granted. Implement only the approved `probe_contract.yaml` in probes/IDEA_ID/.

Requirements:
- minimal dependencies;
- one command to run;
- fixed seed;
- deterministic split manifest;
- assertions against split overlap;
- synthetic or tiny smoke mode;
- per-sample outputs;
- resolved configuration and environment capture;
- no test-set access;
- no unapproved variants;
- clear failure exit codes.

Run local non-expensive checks and write `verification.json`. Do not launch expensive compute.
