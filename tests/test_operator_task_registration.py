import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

class TaskRegistrationTests(unittest.TestCase):
    def test_three_tasks_persist_and_replay_without_execution_or_duplicate_review(self):
        root=Path(__file__).resolve().parents[1]
        spec=importlib.util.spec_from_file_location('operator_tasks',root/'deploy/research-system/register_operator_tasks.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)/'source';repo.mkdir();state=Path(tmp)/'state';state.mkdir(mode=0o700)
            doc=repo/'docs/operations/QUEUED_SCIENTIFIC_TASKS_20260906.json';doc.parent.mkdir(parents=True)
            shutil.copyfile(root/doc.relative_to(repo),doc)
            def git(*a):return subprocess.check_output(['git',*a],cwd=repo,text=True).strip()
            git('init','-q');git('config','user.name','Synthetic');git('config','user.email','fixture@local.invalid');git('add','.');git('commit','-qm','tasks')
            source=git('rev-parse','HEAD')
            first=module.register(state,repo,source,'2026-09-06');second=module.register(state,repo,source,'2026-09-06')
            self.assertEqual(first['report']['id'],second['report']['id']);self.assertEqual(first['task_count'],3)
            self.assertFalse(first['execution_dispatched'])
            queue=module.Queue(state/'reports')
            self.assertEqual(queue.db.execute('SELECT count(*) FROM reviews').fetchone()[0],1)
            store=module.Store(state/'operator-tasks.sqlite')
            self.assertEqual(store.db.execute('SELECT count(*) FROM jobs').fetchone()[0],3)
            self.assertTrue(all(r['status']=='OPEN' for r in store.inbox()))
            report=(state/'reports'/(first['report']['id']+'.md')).read_text()
            for task in json.loads(doc.read_text())['tasks']:self.assertIn(task['id'],report)

            # An operations-only source update preserves every original task binding.
            (repo/'note.txt').write_text('new operations revision')
            git('add','.');git('commit','-qm','operations')
            newer=git('rev-parse','HEAD')
            third=module.register(state,repo,newer,'2026-09-06')
            self.assertEqual({r['source'] for r in third['tasks']},{source})
