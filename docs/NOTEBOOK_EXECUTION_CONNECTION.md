# Execute the reviewed notebook module

Item4 authors revise the preserved notebook, including its existing writefile
module. The controller exports the source bodies of one `%%writefile
/content/sprint13_pipeline.py` cell followed by its `-a` cells. It never runs the
notebook's other cells to build the package and refuses another overwrite or an
append without the initial cell.

The scientific author supplies `main(input_root, output_root, contract)` and
`synthetic_tests()` returning a nonempty unittest.TestSuite in that module. The
controller supplies no scientific algorithm. The actual exported module is
imported and its tests run inside the existing no-network synthetic sandbox,
alongside the unchanged fold, verdict, coverage and original-unit checks.
Skipped/expected-failure tests do not pass. Top-level real I/O is not supported:
only synthetic inputs are available during this stage.

The independent reviewer receives the notebook source/diff and bound test
receipts. Approval verification recomputes the exact export and checks that the
same bytes passed the execution test. The immutable experiment package includes
that tested execution.py. This is preparation, not provider admission or a
successful experiment. The paid-job adapter, preprocessing and collection gates
remain required; no fallback to a legacy notebook is allowed.

Item2's original synthetic-only route remains unchanged. Native sandbox proof
is `SyntheticHarnessTests.test_actual_exported_module_and_author_tests_in_native_sandbox`;
unit tests do not stand in for that server check.
