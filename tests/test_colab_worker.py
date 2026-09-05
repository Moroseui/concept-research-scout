import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
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
