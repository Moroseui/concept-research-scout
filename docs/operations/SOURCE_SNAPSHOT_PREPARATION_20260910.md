# Prepare the exact reviewed source branch

The existing snapshot builder supports an explicit source branch so an isolated
reviewed handover commit can be packaged without importing unrelated branch
history. This is local source preparation. Branch selection grants no deployment,
publication, scientific execution or unattended activation authority.

Run from the checkout of the reviewed branch, using its full reviewed commit:

```sh
python -m scripts.prepare_handover_snapshot \
  --source FULL_REVIEWED_COMMIT \
  --source-branch astra/linux-research-handover-20260910 \
  --destination /private/fresh-source-snapshot
```

The source must equal the checkout's HEAD and its current branch must exactly
match `--source-branch`. Tracked changes refuse preparation. The historical
default remains `astra/infrastructure-milestone-record` when the new argument is
omitted. Detached HEAD and a different branch refuse with
`SOURCE_BRANCH_MISMATCH`; a changed commit refuses with `SOURCE_HEAD_CHANGED`.
Use the reviewed checkout rather than renaming a branch to satisfy these checks.

Preparation still scans every selected pinned file, shallow-clones only the
selected branch, and verifies that the physical Git blobs are exactly the
inspected inventory. The manifest binds `source`, `source_branch`, selected
files, physical blob count and the archive digest. Existing destinations refuse;
retain failed preparations for inspection instead of replacing their evidence.
Deployment must still receive its separate reviewed source and applicable grant.
