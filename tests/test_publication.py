import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from orchestrator.publication import copy_verified, inventory, validate


class PublicationTests(unittest.TestCase):
    def test_rejected_tree_never_copied_and_rerun_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); src=root/'source'; src.mkdir(); dst=root/'dest'
            policy={'allowed':['summary.json'], 'required':['summary.json']}
            (src/'summary.json').write_text('{}')
            (src/'staged').mkdir(); (src/'staged'/'patient.csv').write_text('private')
            with self.assertRaises(ValueError): copy_verified(src,dst,policy)
            self.assertFalse(dst.exists())
            (src/'staged'/'patient.csv').unlink(); (src/'staged').rmdir()
            copy_verified(src,dst,policy); before=inventory(dst)
            copy_verified(src,dst,policy); self.assertEqual(before,inventory(dst))
            (src/'summary.json').write_text('{"changed":true}')
            with self.assertRaises(ValueError): copy_verified(src,dst,policy)
            self.assertEqual(before,inventory(dst))

    def test_symlink_and_required_exclusion_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'summary.json').symlink_to('/etc/hostname')
            with self.assertRaises(ValueError): validate(root,{'allowed':['summary.json'],'required':['summary.json']})
            (root/'summary.json').unlink()
            with self.assertRaises(ValueError): validate(root,{'allowed':[],'required':['audit.json']})

    def test_real_logged_child_preserves_checkpoint_and_failure(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'out'; out.mkdir(); (out/'checkpoint').write_text('retain')
            script='from orchestrator.publication import run_logged; import sys; sys.exit(run_logged([sys.executable,"-c", "print(123); raise SystemExit(7)"],sys.argv[1]))'
            for _ in range(2):
                r=subprocess.run([sys.executable,'-c',script,str(out)],capture_output=True)
                self.assertEqual(r.returncode,7,r.stderr)
            self.assertEqual((out/'checkpoint').read_text(),'retain')
            self.assertEqual(Path(str(out)+'.console.log').read_text(),'123\n123\n')

    def test_047_smoke_stages_outside_output_and_refuses_rerun(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'out'
            cmd=[sys.executable,'probes/047/run.py','--smoke','--output-dir',str(out)]
            r=subprocess.run(cmd,capture_output=True)
            self.assertEqual(r.returncode,0,r.stderr.decode())
            before=inventory(out)
            self.assertTrue(out.with_name('out.private-staged').is_dir())
            self.assertNotIn('staged', {p.parts[0] for p in map(Path,before)})
            r=subprocess.run(cmd,capture_output=True)
            self.assertEqual(r.returncode,7)
            self.assertEqual(inventory(out),before)

    def test_generated_export_runs_and_refuses_contamination(self):
        import argparse
        import scout
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'probes/001').mkdir(parents=True); (root/'ideas/001').mkdir(parents=True)
            (root/'ideas/001/probe_contract.yaml').write_text('idea_id: idea-001\n')
            subprocess.run(['git','init','-q',str(root)],check=True)
            old=scout.ROOT
            try:
                scout.ROOT=root
                scout.package_colab(argparse.Namespace(idea=1,phase='B'))
            finally:
                scout.ROOT=old
            nb=json.loads((root/'probes/001/colab_probe_001.ipynb').read_text())
            cell=next(''.join(c['source']) for c in nb['cells'] if 'policy_path =' in ''.join(c['source']))
            blob=subprocess.check_output(['git','hash-object',str(root/'ideas/001/probe_contract.yaml')]).decode().strip()
            (root/'probes/001/publication.json').write_text(json.dumps({'contract_blob':blob,'allowed':['summary.json'],'required':['summary.json']}))
            out=root/'output'; out.mkdir(); (out/'summary.json').write_text('{}')
            Path(str(out)+'.console.log').write_text('actual console\n')
            import os
            cwd=os.getcwd()
            try:
                os.chdir(root)
                env={'OUTPUT_DIR':str(out)}
                exec(cell,env); exec(cell,env)
                self.assertEqual(Path(str(out)+'.publication.console.log').read_text(),'actual console\n')
                (out/'raw.csv').write_text('private')
                with self.assertRaises(ValueError): exec(cell,env)
            finally:
                os.chdir(cwd)
