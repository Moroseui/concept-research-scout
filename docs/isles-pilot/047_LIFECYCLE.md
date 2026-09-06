# 047 lifecycle repair — proposed decisions, not ratification

Phase A remains immutable at `probes/047/results/results_v2` under blob
`b4887c05a21bfe870589b5d9982066943df679d5`; its scientific record and
historical human approvals are unchanged. The new two-node registry validates
structurally. Phase A currently derives STALE because historical registry
attestation is missing; Phase B consequently derives BLOCKED. This mechanical
status does not rescind the historical Phase-A result or human ratification.
An investigator must not call `ratify-registry` pretending to be the operator.

The verified intended Phase-B historical import destination is
`probes/047/results/results_v2-dc586665d0be`, matching `record-result`'s
bundle-name + blob-prefix rule. The earlier README's results_v3 prediction was
incorrect. The new registry uses the correct path.

## Proposed decisions for the operator

1. Attest the existing historical Phase-A binding in the two-node registry,
   preserving the original approval/interpretation and their hashes. No new
   scientific claim or Phase-A rerun is proposed.
2. Confirm the publication disposition of the 047 exclusions audit. It has two
   bookkeeping rows and two file-anomaly rows across three identities. Treating
   all of these as analyzed-case exclusions would be wrong. Determine whether
   the identity-linked anomaly is permissible audit metadata or requires an
   aggregate derivative with a preserved private original and an amendment.
   This is not resolved by Fable's recommendation or campaign delegation.
3. Recover the original successful-session `<OUTPUT_DIR>.console.log` from the
   operator's Drive/Colab if available. Local Downloads searches and the pinned
   source tree did not contain it. The prior exit-7 log and run_log.txt are
   preserved; neither is relabeled as the successful console. If unrecoverable,
   decide whether acceptance is impossible or explicitly limited by missing
   evidence. No reconstruction is proposed.

## Provenance-bound subset route

`record-result --publication-subset DECLARATION.json --expected-blob BLOB
--source-commit SHA` verifies a full source-commit/file inventory. Every file
must be retained byte-for-byte or have a hash-bound explicit disposition to
private original evidence that is actually available. Required science and
audit outputs cannot be excluded. This initial implementation supports only
exclusion of `staged/` input files; arbitrary audit exclusion is refused.
The sidecar stores the declaration digest and source/retained/excluded counts,
not private locations. Preserve the original declaration privately for re-audit.
Existing verbatim imports retain their original semantics.

The 047 policy deliberately blocks publication/import while decisions remain
open. Therefore no new Phase-B import, interpretation or ratification is claimed.
New prediction research has its own campaign/specification and does not inherit
any unresolved 047 acceptance decision.

Validation performed: both original Phase-A and the 17-file Phase-B top-level
interface pass the existing historical core validator. The real import was
then exercised and refused by the explicit publication policy. That demonstrates
why core validity alone is insufficient. No unresolved Phase-B interpretation
was launched. The full suite at the M2 checkpoint passed 220 tests.

### Cleanup review r2: scope of the metadata disposition

The proposed exclusions disposition must also explicitly consider retained
`per_case_staging.csv`, `staging_audit.json`, and `split_manifest.csv`. They
retain identity-linked bookkeeping; quarantining `probe_exclusions.csv` alone
is not anonymization. The operator may approve the current raw-payload cleanup
while accepting a possible later metadata rewrite, or rule on all this metadata
first and request one revised, re-rehearsed projection. Neither option ratifies
047 science or supplies its missing successful console.
