# Correction: unavailable provenance object, not missing approval

The earlier claim that idea 023 lacked a historical approval marker was incorrect.
Before exact retrieval, `git cat-file -t 5aa8b5a183876a991ea7e307d7a6c8a8d3a34c7a`
failed locally because the referenced commit was unavailable. A depth-one fetch of
that exact SHA from origin succeeded. `ideas/023/HUMAN_APPROVED_PROBE` exists there
and binds `0e223c82f9eb879652a549df9bf857c155ef61db`, as the user stated.

The old validator combined every git-show error with a missing-binding assertion.
The corrected validator distinguishes GIT_OBJECT_UNAVAILABLE from
GIT_PATH_UNAVAILABLE (commit available, path lookup failed), and checks binding
content only after a successful read. A missing object never disproves an approval.

CI now retrieves only explicitly reviewed full-SHA snapshots in
configs/pilot/provenance-objects.json, at depth one with --filter=blob:none and no tag/branch wildcard
fetch, then retrieves only the required marker blob and verifies its SHA-256. A synthetic unrelated snapshot blob remains absent after retrieval. This adds no results branch checkout,
merge, or push. Existing approval and governance bytes remain unchanged. A real
shallow synthetic repository test reproduces unavailable-object failure, retrieves
the exact snapshot, verifies bytes, and confirms HEAD stays unchanged.

After retrieval, local registry validation passes for all four registries.
State verification exposes a separate reproducible stale-view issue in 023/045/046:
only idea_card_sha256 and its derived source_fingerprint_sha256 differ. No node
status or approval differs. Following independent review, the built-in state-materialize command refreshed
only those two derived hash fields in each of the three views. All approval,
registry, scientific status, and scientific artifact bytes remain unchanged;
prior generated views remain in Git history. State verification is now green.
This was not the missing-approval defect previously alleged.

Additional review findings: terminal bundle matching now requires a path boundary;
malformed summary mappings and directory-valued consumed artifacts fail closed.
The derive_status docstring explains that candidate terminal detection delegates
acceptance policy to its bundle_validator. The production scout.validate_bundle
calls terminal_statuses_if_approved (scout.py:2378), enforcing the registry
approval gate; this pre-existing injection interface is not a new approval route.
