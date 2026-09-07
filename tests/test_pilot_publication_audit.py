import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
P=Path(__file__).resolve().parents[1]/'scripts/check_pilot_publication.py'
s=importlib.util.spec_from_file_location('pilot_audit',P); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)

class OutgoingAuditTests(unittest.TestCase):
    def test_entire_history_rejects_raw_file_even_after_deletion(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            def git(*a): return subprocess.check_output(['git',*a],cwd=root)
            git('init','-q','-b',m.BRANCH); git('config','user.name','fixture'); git('config','user.email','fixture@local')
            (root/'README.md').write_text('base'); git('add','.'); git('commit','-qm','base'); base=git('rev-parse','HEAD').decode().strip()
            git('checkout','-qb','contaminated'); (root/'raw.csv').write_text('synthetic'); git('add','.'); git('commit','-qm','contaminated'); contaminated=git('rev-parse','HEAD').decode().strip()
            git('checkout','-q',m.BRANCH); (root/'README.md').write_text('safe'); git('add','.'); git('commit','-qm','safe')
            with patch.object(m,'ROOT',root),patch.object(m,'BASE',base),patch.object(m,'CONTAMINATED',contaminated):
                self.assertEqual(m.audit('HEAD')['artifact_versions_checked'],1)
                (root/'raw.csv').write_text('synthetic'); git('add','.'); git('commit','-qm','raw accident')
                (root/'raw.csv').unlink(); git('add','-u'); git('commit','-qm','delete raw')
                with self.assertRaisesRegex(ValueError,'unpermitted'): m.audit('HEAD')

    def test_pattern_shaped_symlink_cannot_borrow_regular_file_mode(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            def git(*a):return subprocess.check_output(['git',*a],cwd=root).decode().strip()
            git('init','-q','-b',m.BRANCH);git('config','user.name','fixture');git('config','user.email','fixture@local')
            (root/'README.md').write_text('base');git('add','.');git('commit','-qm','base');base=git('rev-parse','HEAD')
            git('checkout','-qb','contaminated');(root/'raw.csv').write_text('synthetic');git('add','.');git('commit','-qm','unrelated');bad=git('rev-parse','HEAD')
            git('checkout','-q',m.BRANCH);(root/'tests').mkdir()
            (root/'tests/1.md').write_text('safe');(root/'tests/[1].md').symlink_to('1.md')
            git('add','.');git('commit','-qm','pattern shaped symlink')
            with patch.object(m,'ROOT',root),patch.object(m,'BASE',base),patch.object(m,'CONTAMINATED',bad):
                with self.assertRaisesRegex(ValueError,'non-regular'):m.audit('HEAD')
