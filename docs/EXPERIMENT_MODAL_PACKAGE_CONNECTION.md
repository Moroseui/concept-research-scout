# Reviewed code to provider package

The existing experiment approval seal verifies the genuine scientific MCP
submission, exact input delivery and synthetic-test evidence. The provider
package is built only after revalidating that seal and the frozen package.

The approved SPEC.md and review.json are copied byte for byte. The current
execution_plan_sha256 binding is preserved rather than inserting the legacy
notebook_code_sha256 line after review. The exact exported execution.py and a
release-bound generic run.py receive a separate code identity. The existing
Modal verifier handles this explicit item4 selection; the old M3 contract and
its checks are unchanged. Item6 cannot enter this GPU package path.

The generic worker checks the complete package before importing execution.py,
then calls the author's main(input_root, output_root, contract). The contract
contains the unchanged frozen execution plan and admitted runtime binding.
The input guard has already verified the preprocessed Volume. Outputs are
private per-segment directories; existing directories refuse another execution.
The worker records EXECUTED or FAILED, never scientific validity or acceptance.
No methods, metrics, patient selection or training code are written here.

The package producer/verifier tests use the real scientific seal and original
package path, with explicitly synthetic native/model evidence. Worker tests run
only trivial synthetic modules. The old Modal executor regression also passes.
This is not proof of a paid launch: the actual driver dispatch, provisioning of
preprocessing/package assets, result collection and scientific validation are
still required. The execution branch needs its normal final suites and review
before installation; the installed retrieval release is unchanged.


Durable return connection: the package now includes the exact small worker-side
support files (private record I/O, file limits, fit identity, progress writer,
native checkpoint adapter and result publisher). The publisher's existing checks
were factored unchanged; controller imports remain compatible. No client, billing
or credential module is shipped to the worker. The same helper hashes are in the
synthetic notebook package and required again when scientific approval is sealed.

The generic worker holds the bound fit writer, passes it as contract['progress'],
and gives main a fresh artifacts directory. main must produce exactly the declared
returns and a complete native final checkpoint. The existing publisher commits
outputs and the final result pointer, and the existing provider status/collection
reads those durable objects even after the container ends. Program failure is
recorded and published as failed. No return from main, receipt or synthetic fixture
is treated as scientific validation or acceptance.

Actual ExperimentDriver paid dispatch and preprocessing provisioning remain
unconnected. This change does not claim that item4 ran. Scientific implementation,
training settings and conclusions still belong to the author and reviewer.


Native verification found that the CPU sandbox does not expose `/usr/bin/sync`.
The worker now performs the same mountpoint `fsync` through its pinned Python
in an isolated child with the existing 120-second timeout. No added host mount,
SDK, credential, or network access. GNU coreutils `src/sync.c` (MODE_FILE) confirms
`sync MOUNT` uses `fsync`; Modal documents `sync MOUNT` as Volume-v2 commit; the syscall equivalence is
inferred from the coreutils implementation.
Sources: https://raw.githubusercontent.com/coreutils/coreutils/master/src/sync.c
and https://modal.com/docs/guide/volumes . The server synthetic test proves the
real syscall runs within the existing sandbox; it does not prove a live Modal
Volume commit or interrupted GPU fit, which remain smoke-stage requirements.

The same pre-program input guard had the same external-utility assumption;
its commit is corrected in the same candidate. The native positive test now
runs the actual input hash guard, exec handoff, package verifier, module and
result publisher in one sandbox. It checks the genuine guard receipt as well
as the result. No verifier or filesystem operation is mocked on this path.
