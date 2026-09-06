import shutil
import tempfile
from pathlib import Path
import unittest
from scripts.verify_main_integration import workflow_policy, verify


class MainIntegrationTests(unittest.TestCase):
    def test_main_quarantines_and_opt_in_refusal(self):
        result = workflow_policy(Path(__file__).resolve().parents[1])
        self.assertEqual(result['on_main'], 'SKIPPED')
        self.assertEqual(result['pilot_opt_in_guard'], 'REFUSED_EXIT_1')

    def test_new_jobs_and_relaxed_quarantines_rejected(self):
        source = Path(__file__).resolve().parents[1] / '.github/workflows'
        for old, new in [('exit 1', 'exit 0'),
                         ("github.ref == 'refs/heads/astra/autonomous-isles-pilot'", 'true'),
                         ('contents: read', 'contents: write')]:
            with self.subTest(new=new), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                shutil.copytree(source, root / '.github/workflows')
                f = root / '.github/workflows/interpret.yml'
                f.write_text(f.read_text().replace(old, new))
                with self.assertRaises(ValueError): workflow_policy(root)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            shutil.copytree(source, root / '.github/workflows')
            (root / '.github/workflows/new.yml').write_text('jobs: {}')
            with self.assertRaises(ValueError): workflow_policy(root)

    def test_branch_names_are_not_review_pins(self):
        with self.assertRaisesRegex(ValueError, 'full main and pilot pins'):
            verify(Path(__file__).resolve().parents[1], 'main', 'astra/autonomous-isles-pilot')

    def test_duplicate_yaml_and_ci_write_permissions_rejected(self):
        source = Path(__file__).resolve().parents[1] / '.github/workflows'
        for mutation in ('duplicate', 'top_write', 'job_write', 'credentials'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                shutil.copytree(source, root / '.github/workflows')
                f = root / '.github/workflows/check.yml'
                if mutation == 'duplicate':
                    (f.parent / 'interpret.yaml').write_text('jobs: {}')
                elif mutation == 'top_write':
                    f.write_text(f.read_text().replace('contents: read', 'contents: write'))
                elif mutation == 'job_write':
                    f.write_text(f.read_text().replace('  basic:', '  basic:\n    permissions: write-all'))
                else:
                    f.write_text(f.read_text().replace('persist-credentials: false', 'persist-credentials: true'))
                with self.assertRaises(ValueError): workflow_policy(root)
