"""Controller harness: load author tests only inside the existing CPU sandbox.

Tests and scientific code are reviewed together. Passing author tests establishes
only those tests' results, never their scientific adequacy or real-data success.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest


def run_tests(package, workspace):
    package, workspace = Path(package), Path(workspace)
    files = {name: hashlib.sha256((package/name).read_bytes()).hexdigest()
             for name in ("analysis.py", "test_analysis.py", "run.py")}
    # -I intentionally excludes the working directory and user packages.
    # Only this read-only package is added for the author's test imports.
    sys.path.insert(0, str(package))
    spec = importlib.util.spec_from_file_location("test_analysis", package/"test_analysis.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    success = (result.testsRun > 0 and result.wasSuccessful() and not result.skipped
               and not result.expectedFailures and not result.unexpectedSuccesses)
    record = {"schema":"scientific-program-tests/v1", "files":files,
        "status":"PASS" if success else "FAIL", "tests_run":result.testsRun,
        "failures":len(result.failures), "errors":len(result.errors), "skipped":len(result.skipped),
        "expected_failures":len(result.expectedFailures), "unexpected_successes":len(result.unexpectedSuccesses),
        "patient_data":False, "network":False,
        "scope":"Author-written synthetic tests of the actual analysis source; adequacy requires independent review."}
    (workspace/"result.json").write_text(json.dumps(record, sort_keys=True)+"\n")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(run_tests("/package", "/workspace"))
