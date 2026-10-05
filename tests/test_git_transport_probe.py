"""Refusal before mutation for the bounded hosted acceptance probe."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('transport_probe', Path(__file__).resolve().parents[1] / 'deploy/research-system/verify_git_transport.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class TransportProbeBoundaryTests(unittest.TestCase):
    def test_existing_attempt_is_preserved_not_replayed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / 'original'
            evidence.write_bytes(b'preserve exact original')
            with patch.object(probe, 'git_run') as execute:
                with self.assertRaisesRegex(ValueError, 'FRESH_ABSOLUTE_ATTEMPT_REQUIRED'):
                    probe.verify(root, 'a' * 40)
                execute.assert_not_called()
            self.assertEqual(evidence.read_bytes(), b'preserve exact original')

    def test_capacity_refuses_before_creating_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'attempt'
            with patch.object(probe.shutil, 'disk_usage') as usage:
                usage.return_value.free = 1
                with self.assertRaisesRegex(ValueError, 'DIAGNOSTIC_CAPACITY_REQUIRED'):
                    probe.verify(root, 'a' * 40)
            self.assertFalse(root.exists())
