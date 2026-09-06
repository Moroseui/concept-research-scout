import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/rehearse_047_cleanup.py'
spec=importlib.util.spec_from_file_location('cleanup',SCRIPT); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class CleanupTests(unittest.TestCase):
    def test_exact_projection_and_optimized_refusal(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo=root/'repo'; repo.mkdir()
            def git(*a): return subprocess.check_output(['git',*a],cwd=repo).decode().strip()
            git('init','-q'); git('config','user.name','fixture'); git('config','user.email','fixture@local')
            bundle=repo/'probes/047/results_v2'; bundle.mkdir(parents=True)
            (bundle/'driver_console.log').write_text('original synthetic failure\n')
            git('add','.'); git('commit','-qm','failure'); parent=git('rev-parse','HEAD')
            (bundle/'driver_console.log').unlink(); (bundle/'staged').mkdir()
            for name in ['a.csv','b.csv']: (bundle/'staged'/name).write_text('synthetic input')
            (bundle/'probe_exclusions.csv').write_text('synthetic audit'); (bundle/'summary.json').write_text('{}')
            git('add','-A'); git('commit','-qm','success'); old=git('rev-parse','HEAD')
            r=m.rehearse(repo,root/'replay',old=old,parent=parent,raw_count=2,top_count=2)
            self.assertTrue(r['exact_path_changes_verified']); self.assertEqual(r['retained_result_files'],1)
            code=f"import runpy; m=runpy.run_path({str(SCRIPT)!r}); m['rehearse']({str(repo)!r},{str(root/'bad')!r},old={old!r},parent={parent!r},raw_count=999,top_count=2)"
            run=subprocess.run([sys.executable,'-O','-c',code],capture_output=True,text=True)
            self.assertNotEqual(run.returncode,0); self.assertIn('source inventory mismatch',run.stderr)
