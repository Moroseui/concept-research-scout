import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from orchestrator.publication_subset import verify

class SubsetTests(unittest.TestCase):
    def test_exhaustive_source_and_original_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo=root/'repo'; repo.mkdir()
            def git(*a): return subprocess.check_output(['git',*a],cwd=repo)
            git('init','-q'); git('config','user.name','fixture'); git('config','user.email','fixture@local')
            source=repo/'probes/001/results_v2'; (source/'staged').mkdir(parents=True)
            (source/'summary.json').write_text('{}'); (source/'audit.txt').write_text('audit')
            (source/'staged/raw.csv').write_text('synthetic only')
            git('add','.'); git('commit','-qm','synthetic source'); commit=git('rev-parse','HEAD').decode().strip()
            bundle=root/'bundle'; bundle.mkdir()
            for name in ['summary.json','audit.txt']: (bundle/name).write_bytes((source/name).read_bytes())
            sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
            doc={'schema_version':1,'source_commit':commit,'source_dir':'probes/001/results_v2','contract_blob':'b'*40,
                 'retained':{n:sha(bundle/n) for n in ['summary.json','audit.txt']},
                 'excluded':{'staged/raw.csv':{'sha256':sha(source/'staged/raw.csv'),'reason':'input staging outside publication','decision_ref':'fixture-policy-v1','disposition':'private-original-preserved','private_evidence_path':str(source/'staged/raw.csv')}}}
            declaration=root/'subset.json'
            def check():
                declaration.write_text(json.dumps(doc)); return verify(repo,bundle,declaration,commit,'b'*40,['summary.json','audit.txt'],'probes/001/results_v2')
            self.assertEqual(check()['source_file_count'],3)
            original=doc['excluded'].pop('staged/raw.csv')
            with self.assertRaisesRegex(ValueError,'every source'): check()
            doc['excluded']['staged/raw.csv']=original
            (source/'staged/raw.csv').write_text('changed evidence')
            with self.assertRaisesRegex(ValueError,'evidence'): check()
            (source/'staged/raw.csv').write_text('synthetic only')
            doc['retained'].pop('audit.txt')
            doc['excluded']['audit.txt']={'sha256':sha(source/'audit.txt')}
            with self.assertRaisesRegex(ValueError,'required'): check()
