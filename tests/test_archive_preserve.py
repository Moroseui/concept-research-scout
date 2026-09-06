import hashlib
from pathlib import Path
import tempfile
import unittest
from scripts.colab_archive_preserve import inspect, copy_verified

class ArchivePreserveTests(unittest.TestCase):
    def test_current_hash_corruption_and_missing(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'train.7z';p.write_bytes(b'opaque synthetic bytes')
            md5=hashlib.md5(p.read_bytes()).hexdigest();size=p.stat().st_size
            self.assertTrue(inspect(p,size,md5)['matches'])
            p.write_bytes(b'x'*size)
            self.assertFalse(inspect(p,size,md5)['matches'])
            self.assertFalse(inspect(Path(d)/'missing',size,md5)['exists'])
    def test_exclusive_verified_copy_preserves_original(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'source';q=Path(d)/'destination';p.write_bytes(b'fixture')
            h=hashlib.md5(b'fixture').hexdigest()
            self.assertTrue(copy_verified(p,q,7,h)['matches'])
            with self.assertRaises(FileExistsError):copy_verified(p,q,7,h)
            self.assertEqual(p.read_bytes(),b'fixture');self.assertEqual(q.read_bytes(),b'fixture')
    def test_bad_destination_retained_and_symlink_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'source';q=Path(d)/'destination';p.write_bytes(b'fixture')
            with self.assertRaises(ValueError):copy_verified(p,q,7,'0'*32)
            self.assertTrue(q.exists())
            link=Path(d)/'link';link.symlink_to(p)
            self.assertFalse(inspect(link,7,hashlib.md5(b'fixture').hexdigest())['matches'])

    def test_synthetic_complete_preservation_and_existing_copy(self):
        from unittest.mock import patch
        import scripts.colab_archive_preserve as m
        import os, json
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);drive=root/'drive';project=drive/'MyDrive/isles-pilot';project.mkdir(parents=True)
            local=root/'train.7z';local.write_bytes(b'fixture')
            identity=project/'identity.json';identity.write_text(json.dumps({'size_bytes':7,'md5':hashlib.md5(b'fixture').hexdigest()}))
            job=project/'job1';job.mkdir()
            settings={'SIZE':7,'MD5':hashlib.md5(b'fixture').hexdigest(),'LOCAL':local,'DRIVE':drive,'PROJECT':project,'IDENTITY':identity,'OUTPUT':project/'P001-v1'}
            # inspect/copy defaults are production pins; bind fixture versions explicitly.
            real_inspect=m.inspect;real_copy=m.copy_verified
            with patch.multiple(m,**settings),patch.dict(os.environ,{'COLAB_RELEASE_TAG':'synthetic'}),patch.object(m.os.path,'ismount',return_value=True),patch.object(m.shutil,'which',return_value=None),patch.object(m,'inspect',side_effect=lambda p,*args:real_inspect(p,7,settings['MD5'])),patch.object(m,'copy_verified',side_effect=lambda p,q:real_copy(p,q,7,settings['MD5'])):
                m.run(job);r=json.loads((job/'receipt.json').read_text())
                self.assertEqual(r['status'],'VERIFIED');self.assertEqual(r['persistence_status'],'FRESH_DRIVE_COPY_VERIFIED')
                self.assertEqual(local.read_bytes(),b'fixture')
                second=project/'job2';second.mkdir();m.run(second)
                r=json.loads((second/'receipt.json').read_text());self.assertEqual(r['persistence_status'],'EXISTING_DRIVE_COPY_VERIFIED')
                self.assertFalse((second/'train.7z').exists())

    def test_poll_handoff_includes_source_without_launch_cell(self):
        from unittest.mock import patch
        import orchestrator.archive_preserve as a
        captured=[]
        def fake(*args,**kwargs):
            captured.append(kwargs['input'])
            raise RuntimeError('synthetic stop before any remote execution')
        with tempfile.TemporaryDirectory() as d,patch.object(a,'reviewed',return_value='a'*40),patch.object(a.subprocess,'run',side_effect=fake):
            a.run('poll',Path(d)/'private','/content/drive/MyDrive/isles-pilot/archive-preservation-'+'a'*32)
        self.assertIn('READ-ONLY SCRIPT CONTEXT',captured[0])
        self.assertIn((a.ROOT/a.FILES[0]).read_text(),captured[0])
        cells=a.cells_for('poll','/content/drive/MyDrive/isles-pilot/archive-preservation-'+'a'*32)
        self.assertFalse(any('Popen' in c for c in cells))
        self.assertIn('does not launch, enable, certify or approve',captured[0])

    def test_supplementary_poll_accepts_only_terminal_lf_and_known_blank(self):
        from unittest.mock import patch
        from orchestrator.archive_preserve import verify_poll
        calls=[{'id':'g0','name':'mcp__colab-worker__get_cells','input':{'includeOutputs':False}},
               {'id':'a','name':'mcp__colab-worker__add_code_cell','input':{'code':'print(1)'}},
               {'id':'d','name':'mcp__colab-worker__delete_cell','input':{'cellId':'blank'}},
               {'id':'g1','name':'mcp__colab-worker__get_cells','input':{'includeOutputs':False}},
               {'id':'r','name':'mcp__colab-worker__run_code_cell','input':{'cellId':'new'}}]
        results={'g0':{'cells':[{'id':'blank','source':['\n']}]},'a':{'newCellId':'new'},'d':{},'g1':{'cells':[{'id':'new','source':['print(1)']}]},'r':{'outputs':[]}}
        with patch('orchestrator.archive_preserve.tool_exchanges',return_value=(calls,results)):
            self.assertEqual(verify_poll([],['print(1)\n'])['known_initial_blanks_removed'],1)
            with self.assertRaises(ValueError):verify_poll([],['print(2)\n'])
            results['g0']['cells'][0]['source']=['not empty']
            with self.assertRaises(ValueError):verify_poll([],['print(1)\n'])
            results['g0']['cells'][0]['source']=['']
            calls[0]['input']['includeOutputs']=True
            with self.assertRaises(ValueError):verify_poll([],['print(1)\n'])

    def test_observation_is_bound_to_exact_job_and_returns_only_metadata(self):
        from orchestrator.archive_preserve import observe
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);job=root/'job';job.mkdir();(job/'train.7z').write_bytes(b'fixture')
            proc=root/'proc';entry=proc/'42';entry.mkdir(parents=True)
            (entry/'cmdline').write_bytes(b'python\0'+str(job/'verify.py').encode()+b'\0'+str(job).encode()+b'\0')
            fields=['S']+['0']*20;fields[11]='10';fields[12]='20'
            (entry/'stat').write_text('42 (python) '+' '.join(fields))
            (entry/'io').write_text('rchar: 123\nwchar: 456\n')
            result=observe(job,proc)
            self.assertEqual(result['destination_size_bytes'],7)
            self.assertEqual(result['matching_verification_processes'],[{'pid':42,'state':'S','cpu_ticks':30,'rchar':123,'wchar':456}])
            self.assertEqual(observe(root/'other',proc)['matching_verification_processes'],[])
            (entry/'io').write_text('rchar: invalid')
            self.assertFalse(observe(job,proc)['process_scan_complete'])

    def test_generated_observation_definition_is_executable(self):
        from orchestrator.archive_preserve import cells_for
        source=cells_for('poll','/content/drive/MyDrive/isles-pilot/archive-preservation-'+'a'*32)[1]
        namespace={}
        exec(source.split('import os, json, hashlib')[0],namespace)
        self.assertTrue(callable(namespace['observe']))
