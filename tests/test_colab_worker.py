import json
import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from orchestrator.colab_worker import invoke_handoff_worker, task_packet, verify_synthetic_protocol
from orchestrator.colab_worker import capture_cell, digest, private_dir, verify_handoff


class WorkerTests(unittest.TestCase):
    def test_committed_remote_receipt(self):
        self.assertEqual(verify_handoff()['status'], 'HANDOFF_RECEIPT_VERIFIED')

    def exercise(self, source):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d)/'original.console.log'
            wrapper = capture_cell(source, log)
            run = subprocess.run([sys.executable, '-c', wrapper], capture_output=True, text=True)
            return run, log.read_text()

    def worker_fixture(self, result, subtype="success", models=None, raw=None):
        def run(command, **kwargs):
            event = {"type": "result", "subtype": subtype, "is_error": False,
                     "structured_output": result, "modelUsage": {"claude-fable-5": {}} if models is None else models}
            kwargs["stdout"].write((json.dumps(event if raw is None else raw)+"\n").encode())
            return subprocess.CompletedProcess(command, 0)
        packet = task_packet()
        with tempfile.TemporaryDirectory() as d, patch("orchestrator.colab_worker.task_packet", return_value=packet), patch("orchestrator.colab_worker.subprocess.run", side_effect=run):
            return invoke_handoff_worker(Path(d)/"attempt")

    def test_successful_worker_receipt_requires_exact_fields(self):
        packet = task_packet()
        result = {"status": "HANDOFF_CHECKED", "task": packet["task"],
                  "receipt_sha256": packet["expected_receipt_sha256"],
                  "notebook_sha256": packet["expected_notebook_sha256"],
                  "returned_sha256": verify_handoff()["returned_sha256"]}
        self.assertEqual(self.worker_fixture(result)["status"], "WORKER_HANDOFF_VALIDATED")
        self.assertEqual(self.worker_fixture(result, models={"unexpected-model": {}})["status"], "WORKER_FAILED")
        result["returned_sha256"] = "bad"
        self.assertEqual(self.worker_fixture(result)["status"], "WORKER_FAILED")

    def test_incomplete_and_unexpected_worker_outputs_rejected(self):
        self.assertEqual(self.worker_fixture({"unreviewed": "SYNTHETIC_PRIVATE"})["status"], "WORKER_FAILED")
        status = self.worker_fixture({}, "error_max_turns")
        self.assertEqual(status["status"], "WORKER_FAILED")
        self.assertNotIn("SYNTHETIC_PRIVATE", json.dumps(status))
        self.assertEqual(self.worker_fixture([], raw=[])["status"], "WORKER_FAILED")
        self.assertEqual(self.worker_fixture([])["status"], "WORKER_FAILED")

    def test_actual_synthetic_protocol_and_tampering(self):
        fixture = json.loads((Path(__file__).parent/'fixtures/colab_synthetic_protocol.json').read_text())
        self.assertEqual(verify_synthetic_protocol(fixture)["pinned_execution_calls"], 3)
        bad = copy.deepcopy(fixture)
        runs = [b for e in bad for b in e["message"]["content"] if b["type"] == "tool_use" and b["name"].endswith("__run_code_cell")]
        runs[1]["input"]["cellId"] = runs[2]["input"]["cellId"]
        with self.assertRaises(ValueError): verify_synthetic_protocol(bad)
        with self.assertRaises((ValueError, KeyError)): verify_synthetic_protocol(fixture[:-1])

    def test_python_and_fd_console_stay_private(self):
        source = "import subprocess, sys\nprint('SYNTHETIC_PRIVATE_PYTHON')\nsubprocess.run([sys.executable, '-c', \"print('SYNTHETIC_PRIVATE_CHILD')\"], check=True)"
        run, console = self.exercise(source)
        self.assertEqual(run.returncode, 0)
        self.assertIn('SYNTHETIC_PRIVATE_PYTHON', console)
        self.assertIn('SYNTHETIC_PRIVATE_CHILD', console)
        self.assertNotIn('SYNTHETIC_PRIVATE', run.stdout+run.stderr)
        self.assertIn(digest(source.encode()), run.stdout)

    def test_failure_is_not_success_and_evidence_retained(self):
        run, console = self.exercise("raise RuntimeError('SYNTHETIC_PRIVATE_FAILURE')")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('SYNTHETIC_PRIVATE_FAILURE', console)
        self.assertNotIn('SYNTHETIC_PRIVATE_FAILURE', run.stdout+run.stderr)
        self.assertIn('FAILED', run.stdout)

    def test_rerun_appends_console(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'console'
            for text in ['first', 'second']:
                subprocess.run([sys.executable, '-c', capture_cell('print('+repr(text)+')', p)], check=True, capture_output=True)
            self.assertEqual(p.read_text(), 'first\nsecond\n')

    def test_reject_existing_or_repository_evidence_dir(self):
        with self.assertRaises(ValueError): private_dir(Path(__file__).resolve().parent/'worker-private')
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileExistsError): private_dir(d)


if __name__ == '__main__': unittest.main()
