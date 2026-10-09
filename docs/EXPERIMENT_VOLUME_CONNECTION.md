# Existing fit mounts and worker launch

The provider already mounts three selected Volumes for preprocessed inputs,
reviewed code and durable progress. The actual Modal layout uses aliases into
`/__modal/volumes/<Volume ID>`. The experiment launcher must bind those aliases
before the unchanged child-file checks can operate on canonical paths.

`modal_volume_path.bound_fit_roots` accepts only those three roles, with distinct
controller-selected Volume IDs. It checks the exact target, real directory
ancestors and stable identity. The downloader retains its separate single-alias
contract. No arbitrary alias, another Volume, external directory or child alias
is accepted. Mount exposure and read-only flags are unchanged.

The provider sends one program composed from the exact release's Volume binder
and input guard. Its hash covers both sources. There is no import through an
unverified mount alias. The guard verifies all input hashes before the worker
starts and records the three Volume IDs in its original proof. The provider
requires the same IDs when reading that proof. The worker receives canonical
paths and independently checks them against its manifest's role IDs before
loading the scientific module. Duplicate guard entry refuses without executing
scientific code again.

Native tests construct the actual three-alias namespace with bubblewrap and
exercise the composed program, exec handoff, actual experiment worker,
scientific validator envelope and checkpoint/result publication. Scientific
code and payloads are explicitly synthetic. Wrong roles, shared IDs, redirected
aliases, changed bytes, child aliases and unsafe permissions refuse. These are
not GPU execution, patient computation or scientific acceptance evidence.

This does not change the requirement that progress roots and every written
child be private. A readable root or child still refuses; the launcher never
repairs its modes. The real provisioning preflight must establish those
prerequisites before a paid fit. Input preparation, per-fit runtime production,
checkpoint continuation and the final integrated release remain separate gates.
