import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from orchestrator.inspection_source import prepare


class SourceViewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.email', 'fixture@invalid.example')
        self.git('config', 'user.name', 'Synthetic fixture')

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, stderr=subprocess.DEVNULL)

    def commit(self, files):
        for name, raw in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        self.git('add', '.')
        self.git('commit', '-qm', 'Synthetic source version')
        return self.git('rev-parse', 'HEAD').decode().strip()

    def test_originals_history_and_exclusions(self):
        first = self.commit({'code.py': b'first = 1\r\n', '.gitignore': b'ignored\n'})
        private_name = 'private/evidence.txt'
        second = self.commit({'code.py': b'second = 2\n', private_name: b'private original\n',
                              'tests/test_one.py': b'assert True\n',
                              'deploy/research-system/example.service.in': b'[Service]\n'})
        destination = Path(self.temp.name) / 'view'
        result = prepare(self.root, second, destination, history=[first])
        self.assertEqual((destination / ('history/' + first + '/code.py')).read_bytes(), b'first = 1\r\n')
        self.assertEqual((destination / 'source/.gitignore').read_bytes(), b'ignored\n')
        self.assertTrue((destination / 'source/tests/test_one.py').is_file())
        self.assertTrue((destination / 'source/deploy/research-system/example.service.in').is_file())
        self.assertFalse((destination / 'source' / private_name).exists())
        self.assertNotIn(private_name, json.dumps(result))
        self.assertTrue(any(row.get('path_sha256') == hashlib.sha256(private_name.encode()).hexdigest()
                            for row in result['excluded']))
        self.assertEqual(self.git('show', first + ':code.py'), b'first = 1\r\n')
        self.assertFalse((destination / '.git').exists())
        self.assertFalse(result['availability_is_inspection'])

    def test_dirty_checkout_refuses_before_view(self):
        source = self.commit({'code.py': b'original\n'})
        (self.root / 'code.py').write_bytes(b'changed\n')
        destination = Path(self.temp.name) / 'view'
        with self.assertRaisesRegex(ValueError, 'CLEAN_FIXED_SOURCE'):
            prepare(self.root, source, destination)
        self.assertFalse(destination.exists())

    def test_untracked_files_cannot_sneak_into_source(self):
        source = self.commit({'code.py': b'original\n'})
        (self.root / 'untracked.txt').write_bytes(b'not committed\n')
        with self.assertRaisesRegex(ValueError, 'CLEAN_FIXED_SOURCE'):
            prepare(self.root, source, Path(self.temp.name) / 'view')

    def test_evidence_requires_exact_original(self):
        source = self.commit({'code.py': b'original\n'})
        evidence = Path(self.temp.name) / 'evidence.json'
        evidence.write_bytes(b'{"status":"original"}\n')
        with self.assertRaisesRegex(ValueError, 'EVIDENCE_CHANGED'):
            prepare(self.root, source, Path(self.temp.name) / 'view', evidence=[
                {'path': str(evidence), 'sha256': '0' * 64, 'name': 'proof.json'}])
        self.assertEqual(evidence.read_bytes(), b'{"status":"original"}\n')


if __name__ == '__main__':
    unittest.main()
