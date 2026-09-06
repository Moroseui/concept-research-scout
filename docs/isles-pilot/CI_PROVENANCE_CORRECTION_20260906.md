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
configs/pilot/provenance-objects.json, at depth one with no tag/branch wildcard
fetch, then verifies the marker's SHA-256. This adds no results branch checkout,
merge, or push. Existing approval and governance bytes remain unchanged. A real
shallow synthetic repository test reproduces unavailable-object failure, retrieves
the exact snapshot, verifies bytes, and confirms HEAD stays unchanged.

After retrieval, local registry validation passes for all four registries.
State verification exposes a separate reproducible stale-view issue in 023/045/046:
only idea_card_sha256 and its derived source_fingerprint_sha256 differ. No node
status or approval differs. Those existing state files are preserved in this fix;
this is not the missing-approval defect previously alleged.
