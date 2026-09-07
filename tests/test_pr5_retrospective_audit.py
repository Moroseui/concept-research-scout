"""Synthetic regressions for complete historical coverage and independent trust."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from scripts.pr5_retrospective_audit import scan_commits


class RecordingPolicy:
    def __init__(self):
        self.trusts = []

    def scan_commit(self, data):
        if b'bad-message' in data:
            raise ValueError('COMMIT_METADATA_REJECTED')

    def scan_history_blob(self, root, trust, name, data):
        self.trusts.append(trust)
        if b'unsafe-fixture' in data:
            raise ValueError('PUBLICATION_CONTENT_REJECTED')


class RetrospectiveTests(unittest.TestCase):
    def test_deleted_intermediate_and_metadata_are_scanned_and_trust_is_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def git(*args):
                return subprocess.check_output(['git', '-c', 'user.name=Synthetic',
                    '-c', 'user.email=synthetic@example.invalid', *args], cwd=root,
                    stderr=subprocess.PIPE).decode().strip()
            git('init')
            (root / 'fixture.txt').write_text('unsafe-fixture')
            git('add', '.')
            git('commit', '-m', 'bad-message')
            first = git('rev-parse', 'HEAD')
            (root / 'fixture.txt').unlink()
            (root / 'safe.txt').write_text('safe')
            git('add', '-A')
            git('commit', '-m', 'safe final tree')
            second = git('rev-parse', 'HEAD')
            policy = RecordingPolicy()
            metadata, blobs, findings = scan_commits(root, [first, second], policy, 'separate-trust')
            self.assertEqual(len(metadata), 2)
            self.assertEqual(len(blobs), 2)
            self.assertEqual(len(findings), 2)
            self.assertEqual({f['reason'] for f in findings},
                {'COMMIT_METADATA_REJECTED', 'PUBLICATION_CONTENT_REJECTED'})
            self.assertEqual(policy.trusts, ['separate-trust', 'separate-trust'])
            self.assertNotIn('unsafe-fixture', str(findings))


if __name__ == '__main__':
    unittest.main()
