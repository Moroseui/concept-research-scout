# First 047 cleanup — historical decision request

**Executed 7 September under the operator’s exact approval.** See
[verified execution receipt](047_CLEANUP_EXECUTED_20260907.json). The original
request below is retained as historical scope; its pending/current language
describes preparation, not the present state. Scientific landing and longer-term
metadata disposition remain separate.


**Approve or decline the complete operation below, including its temporary
branch-specific protection exception and the residual public metadata.** No
cleanup or protection change has occurred. [Current read-only recheck](047_CLEANUP_POSTMERGE_RECHECK_20260906.json)
confirms the original target and protection. The reviewed projection is unchanged;
reuse [the successful rehearsal](CLEANUP_RECONCILIATION_20260906.json) and existing
cleanup reviews, without repeating generation or claiming a new review.

Only `refs/heads/results/probe-047-dc586665d0be` changes:

- Before: `940293b6d562f2d3dd6bfd9d8d8281ccf01e4783`.
- After: `c812421207b6ddcba6516444897c777d8440275a`.
- Parent stays `b652005fbcf6a87765a85e81b381a8596b4384ce`.

This removes 198 staged phenotype CSVs and quarantines the exact original
`probe_exclusions.csv` privately. Sixteen top-level scientific/audit files retain
their bytes. **Three case-linked metadata files remain public:**
`per_case_staging.csv`, `split_manifest.csv`, and `staging_audit.json`, including
identity-linked usability/anomaly/stratum metadata. This is not anonymization.
The original bundle, exclusions and failure console remain private; failure
history stays intact and the identical console is added in its sibling location.
No successful console is reconstructed. Earlier Phase-A evidence is untouched.

## Exact permission exception and restoration

Ruleset **20885616**, `protect-results-branches`, is active for `refs/heads/results/**`
with deletion and non-fast-forward restrictions, no exclusions and no bypass
actors (`current_user_can_bypass=never`). It currently prevents the proposed push.
Approval must include this temporary configuration sequence, not a broad admin
bypass, global ruleset disablement, or deletion permission:

1. Snapshot and compare the current ruleset/effective rules and target pin. Add
   an active temporary **deletion-only** ruleset targeting exactly
   `refs/heads/results/probe-047-dc586665d0be`, no bypass actors. Verify it applies.
2. Add only that exact ref to ruleset 20885616's `ref_name.exclude`, preserving
   every other setting. Verify the target retains deletion protection, its
   non-fast-forward restriction is temporarily absent, and other results refs
   retain both restrictions. This exception is branch-scoped, not actor-scoped;
   avoid concurrent writers during the short window.
3. Recheck the exact before pin, private original evidence and affected refs;
   execute the single leased update below from the existing rehearsal repository.
4. **Whether the push succeeds or fails**, remove that exact exclusion to restore
   the saved ruleset configuration. Verify both restrictions apply to the target
   and other results refs. Only then remove the temporary deletion-only ruleset.
   Never overwrite concurrent ruleset changes blindly. If restoration fails, stop
   further mutations, retain deletion protection and report an urgent operator
   dependency; do not claim cleanup complete or repeat the push automatically.

```bash
git push --force-with-lease=refs/heads/results/probe-047-dc586665d0be:940293b6d562f2d3dd6bfd9d8d8281ccf01e4783 https://github.com/Moroseui/concept-research-scout.git c812421207b6ddcba6516444897c777d8440275a:refs/heads/results/probe-047-dc586665d0be
```

Run only after approval from the preserved private `rehearsal-047-v2/rehearsal.git`.
Verify after pin, tree, retained bytes, failure evidence, restored protections and
unchanged unrelated refs. Target/projection changes invalidate this request;
re-audit before proceeding. A new broader metadata projection requires new review
and rehearsal. The current recheck is not a new full cached/hidden-ref audit.

This addresses a confirmed project publication-policy violation; an independent
licensing violation has not been established. It grants no 047 scientific landing
or acceptance: missing successful-console evidence, required exclusions disposition
and import/registry gates remain. Future provenance must bind the new source hash;
old citations remain historical. Clones, forks, copied data, caches and hidden
service refs cannot be erased by this ref update; host-side handling is separate.
