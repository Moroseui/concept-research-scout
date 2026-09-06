# Explicit controlled creation of the milestone record branch

This bounded repair implements the operator's authorization to publish
`astra/infrastructure-milestone-record`. It adds no main, results, cleanup or
other production destination grant. Existing update callers retain their exact
before-pin compare-and-swap behavior. Existing credentials are unchanged.

`orchestrator.git_publication.publish` now accepts a distinct `operation=create`
request with exact `source`, `audit_baseline`, `baseline_ref`, `destination`,
`remote`, `expected_destination=absent`, and the full outgoing `inventory`.
The caller's externally established authority must bind every field except the
inventory, whose full equality is separately audited. This mapping records an
operation grant; it does not authenticate or manufacture an operator signature.

For this operation the already-public baseline is main
`d24ffb9003a2291f359afe3acf4bf491f2d7fd9f`, advertised as `refs/heads/main` by
`https://github.com/Moroseui/concept-research-scout.git`. It is not an expected
old destination value. The destination must be absent. If the baseline ref moves,
stop and rebind deliberately; never silently broaden the unaudited baseline.

The route checks clean bound HEAD, configured repository identity, valid exact refs,
and the remotely advertised baseline. Existing full outgoing commit/blob checks
(including intermediate/deleted files, side history, credential/case boundaries,
notebook outputs, modes, ancestry and exact inventory) run unchanged. It then
requires absent destination and uses the bound repository URL directly, avoiding
a separately configured pushurl.

Publication uses one push with `--force-with-lease=refs/heads/DESTINATION:`.
The empty expected-old value enforces absence atomically at the receiving ref.
There is no update fallback or retry that could overwrite a concurrent creator.
A porcelain new-branch result is additionally required: Git may otherwise report
an identical concurrently created ref as up-to-date without checking the lease.
That no-op is refused, not claimed as this operation's successful creation. The
remote source pin is independently read back before returning success. A failed
post-write verification is uncertain and must be reconciled, not blindly retried.

Synthetic tests use real disposable Git remotes. They cover successful creation,
already-existing identical/different refs, a competing creator between preflight
and push (both different and identical source), exact lease use and no overwrite,
unsafe history added then deleted, inventory/authority/baseline/repository/ref
bindings, and a divergent pushurl. The legacy update route remains covered.
No patient, protection, limiter or cleanup operation is exercised.

Changing this publisher invalidates the earlier hosted adapter's whole-file review
binding. No Actions scientific/control dispatch is performed by this repair.
This focused review is for publication creation; it does not silently replace
or expand the hosted adapter's prior source-bound approval. Refresh any affected
adapter review before its next execution if its existing gate requires it.
