import ast
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from orchestrator import colab_patient as p


class PatientDispatchTests(unittest.TestCase):
    def test_gate_blocks_patient_packet(self):
        with tempfile.TemporaryDirectory() as d, patch.object(p,'REVIEW_DIR',Path(d)):
            with self.assertRaises(FileNotFoundError):
                p.execution_packet('/content/train.7z')

    def test_archive_path_rejects_phenotype_root_and_traversal(self):
        for path in ['/content/047-staged', '/tmp/train.7z', '/content/../train.7z', '/content/train.7z\n']:
            with self.assertRaises(ValueError): p.archive_path(path)
        self.assertEqual(p.archive_path('/content/drive/MyDrive/ISLES/train.7z'), '/content/drive/MyDrive/ISLES/train.7z')

    def test_packet_preserves_scientific_sources_and_compiles(self):
        with patch.object(p,'require_patient_review',return_value='synthetic-review'):
            packet=p.execution_packet('/content/drive/MyDrive/ISLES/train.7z')
        for source in packet['cells']:compile(source,'transport','exec')
        compile(packet['launch_source'],'launcher','exec')
        script=p.child_script(packet['original_notebook'],packet['parameters'])
        compile(script,'child','exec')
        self.assertIn("DATA_ROOT = None",script)
        tree=ast.parse(script)
        literals=[node.value for node in ast.walk(tree) if isinstance(node,ast.Constant) and isinstance(node.value,str)]
        for i in (3,4,5):self.assertIn(''.join(packet['original_notebook']['cells'][i]['source']),literals)
        self.assertNotIn('047',packet['parameters']['archive'])

    def test_metadata_scan_never_opens_file_payload(self):
        class Stat:st_size=99014629647
        out=io.StringIO()
        with patch('os.path.isfile',return_value=False), patch('os.path.isdir',return_value=True), patch('os.path.ismount',return_value=True), patch('os.path.islink',return_value=False), patch('os.walk',return_value=iter([('/content/drive/MyDrive/data',[],['train.7z','patient.nii.gz'])])), patch('os.stat',return_value=Stat()), patch('builtins.open',side_effect=AssertionError('payload opened')), contextlib.redirect_stdout(out):
            exec(p.FIND_CELL,{})
        result=json.loads(out.getvalue())
        self.assertTrue(result['scan_complete'])
        self.assertEqual(result['archive_candidates'],[{'path':'/content/drive/MyDrive/data/train.7z','size_bytes':99014629647}])
        self.assertNotIn('patient.nii.gz',out.getvalue())

    def test_unmounted_drive_refuses_before_any_output_directory(self):
        with patch.object(p,'require_patient_review',return_value='synthetic-review'):
            packet=p.execution_packet('/content/train.7z')
        with patch('os.path.ismount',return_value=False), patch.object(Path,'mkdir',side_effect=AssertionError('created output before mount')) as mkdir:
            with self.assertRaisesRegex(RuntimeError,'Drive mount unavailable'):
                exec(packet['cells'][1],{})
            mkdir.assert_not_called()

    def test_child_failure_retains_private_console_and_fixed_status(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'P001';job=Path(str(output)+'.worker');job.mkdir()
            cells=[{'source':[]} for _ in range(6)]
            cells[3]['source']=["raise RuntimeError('SYNTHETIC_PRIVATE_DETAIL')"]
            params={'repo':d,'output':str(output),'archive':'/content/train.7z'}
            script=job/'run.py';script.write_text(p.child_script({'cells':cells},params))
            with (job/'console').open('wb') as log:
                run=subprocess.run([sys.executable,str(script)],stdout=log,stderr=subprocess.STDOUT)
            self.assertNotEqual(run.returncode,0)
            self.assertEqual(json.loads((job/'status.json').read_text()),{'status':'FAILED'})
            self.assertIn('SYNTHETIC_PRIVATE_DETAIL',(job/'console').read_text())

    def test_child_success_validates_then_packages_no_staged_inputs(self):
        import zipfile
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);output=root/'P001';output.mkdir();job=Path(str(output)+'.worker');job.mkdir()
            private=Path(str(output)+'.private');private.mkdir()
            for folder in ['predictions','checkpoints','staged']:(private/folder).mkdir()
            (private/'binding.json').write_text('{}');(private/'checkpoint_index.json').write_text('{}')
            (private/'predictions/synthetic.npy').write_bytes(b'synthetic')
            (private/'staged/never-transfer.nii').write_bytes(b'synthetic-staged')
            Path(str(output)+'.console.log').write_text('original synthetic console')
            (output/'summary.json').write_text('{"synthetic":true}')
            (root/'validate_return.py').write_text("import hashlib\ndef verify(bundle,private,console):\n    (private/'validator-called').write_text('yes')\n    return {'file_sha256':{'summary.json':hashlib.sha256((bundle/'summary.json').read_bytes()).hexdigest()}}\n")
            cells=[{'source':[]} for _ in range(6)]
            cells[3]['source']=["EXPERIMENT = REPO"]
            params={'repo':d,'output':str(output),'archive':'/content/train.7z','notebook_pin':'synthetic','source_pin':'synthetic'}
            script=job/'run.py';script.write_text(p.child_script({'cells':cells},params))
            with (job/'console').open('wb') as log:run=subprocess.run([sys.executable,str(script)],stdout=log,stderr=subprocess.STDOUT)
            self.assertEqual(run.returncode,0)
            self.assertTrue((private/'validator-called').is_file())
            self.assertEqual(json.loads((job/'status.json').read_text()),{'status':'VALIDATED'})
            with zipfile.ZipFile(job/'P001-private-return.zip') as z:
                self.assertIn('private/predictions/synthetic.npy',z.namelist())
                self.assertIn('console.log',z.namelist())
                self.assertFalse(any('staged' in n for n in z.namelist()))


if __name__=='__main__':unittest.main()
