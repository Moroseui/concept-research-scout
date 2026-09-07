"""Private diagnostics survive checked failures, unchecked CAS errors and timeout."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from orchestrator.git_diagnostics import run


class PrivateGitTests(unittest.TestCase):
    def test_original_stderr_is_private_for_checked_and_unchecked_failures(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'RESEARCH_GIT_DIAGNOSTICS': tmp}):
            secret = 'SYNTHETIC_DIAGNOSTIC_CANARY'
            args = [sys.executable, '-c', "import sys;sys.stderr.write('" + secret + "');sys.exit(128)"]
            with self.assertRaises(subprocess.CalledProcessError) as caught:
                run(args, check=True)
            self.assertNotIn(secret, str(caught.exception))
            self.assertIsNone(caught.exception.stderr)
            result = run(args, check=False, text=True)
            self.assertEqual(result.returncode, 128)
            self.assertEqual(result.stderr, '')
            records = list(Path(tmp).glob('git-*'))
            self.assertEqual(len(records), 2)
            for directory in records:
                self.assertEqual((directory / 'stderr').read_text(), secret)
                self.assertEqual((directory / 'stderr').stat().st_mode & 0o777, 0o600)
                self.assertEqual(json.loads((directory / 'receipt.json').read_text())['returncode'], 128)

    def test_timeout_preserves_stderr_without_retry(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'RESEARCH_GIT_DIAGNOSTICS': tmp}):
            with self.assertRaises(subprocess.TimeoutExpired):
                run([sys.executable, '-c', "import sys,time;sys.stderr.write('before-timeout');sys.stderr.flush();time.sleep(10)"], timeout=.2)
            self.assertEqual(len(list(Path(tmp).glob('git-*'))), 1)
            self.assertEqual(next(Path(tmp).glob('git-*/stderr')).read_text(), 'before-timeout')

    def test_public_permissions_refused_before_execution(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'RESEARCH_GIT_DIAGNOSTICS': tmp}):
            os.chmod(tmp, 0o755)
            with self.assertRaisesRegex(ValueError, 'PERMISSIONS_REJECTED'):
                run(['git', '--version'])
            self.assertEqual(list(Path(tmp).iterdir()), [])
