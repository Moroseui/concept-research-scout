import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from tools import preparation_host_operation as host

class TransitionTests(unittest.TestCase):
    def test_changed_state_or_history_cannot_reuse_transition(self):
        payload=json.dumps({'phase':'run_spec_author'})
        original=host.transition_identity('run',payload,[])
        changes=[('another',payload,[]),('run',json.dumps({'phase':'MODEL_RUNNING'}),[]),
                 ('run',payload,[['id','run_spec_author',1,'COMPLETE']])]
        self.assertEqual(original,host.transition_identity('run',payload,[]))
        self.assertEqual(len(original),64)
        for args in changes:self.assertNotEqual(original,host.transition_identity(*args))

    def test_invalid_transition_refuses_before_source_or_service_access(self):
        with patch.object(host.os,'getuid',return_value=0),patch.object(host.sys,'flags',type('Flags',(),{'no_user_site':1})()):
            for key,value in [('unknown','a'*64),('aggregate_analysis','../escape'),('colab_preparation','A'*64),('colab_preparation',None)]:
                with patch.object(host,'trusted',side_effect=AssertionError('must not touch files')):
                    with self.assertRaisesRegex(ValueError,'ACTION_BINDING'):host.connect(key,value)

    def test_model_and_host_controls_cannot_run_as_service_account(self):
        with patch.object(host.os,'getuid',return_value=1003):
            with self.assertRaisesRegex(ValueError,'ROOT_ISOLATED'):host.connect('aggregate_analysis','a'*64)
            with self.assertRaisesRegex(ValueError,'STATUS_OWNER'):host.status('aggregate_analysis')

    def test_state_reader_uses_readonly_databases_and_never_root(self):
        # This executable test uses isolated temporary databases and the real
        # sqlite reader; only filesystem locations and explicit UID assertion
        # are adapted to make the test portable without privilege escalation.
        import tempfile,sqlite3,hashlib
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);lane=root/'lane';lane.mkdir();global_db=root/'global.sqlite'
            config={'run_id':'aggregate-fixture','source':'a'*40,'engine_review':{'sha256':'b'*64}}
            (lane/'lane.json').write_text(json.dumps(config))
            with sqlite3.connect(lane/'jobs.sqlite') as db:
                db.execute('CREATE TABLE manual_state(id INTEGER,payload TEXT)');db.execute('CREATE TABLE manual_calls(id TEXT,stage TEXT,attempt INTEGER,status TEXT)')
                db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps({'phase':'run_spec_author'}),))
            with sqlite3.connect(global_db) as db:db.execute('CREATE TABLE autonomy_calls(status TEXT)')
            raw=host.STATE_READER.replace('assert os.getuid()==os.getgid()==1003','assert os.getuid()=='+str(__import__('os').getuid())).replace('file:/var/lib/research-system-autonomy/reviews/jobs.sqlite?mode=ro',global_db.as_uri()+'?mode=ro')
            before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (lane/'jobs.sqlite',global_db)}
            result=subprocess.run([sys.executable,'-s','-B','-c',raw,str(lane)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            value=json.loads(result.stdout);self.assertEqual(value['phase'],'run_spec_author');self.assertEqual(value['local_calls'],0)
            self.assertEqual(before,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in before})
            with sqlite3.connect(global_db) as db:db.execute("INSERT INTO autonomy_calls VALUES('RUNNING')")
            self.assertNotEqual(subprocess.run([sys.executable,'-s','-B','-c',raw,str(lane)],capture_output=True).returncode,0)
            with sqlite3.connect(global_db) as db:db.execute('DELETE FROM autonomy_calls')
            with sqlite3.connect(lane/'jobs.sqlite') as db:db.execute("UPDATE manual_state SET payload=?",(json.dumps({'phase':'COMPLETE'}),))
            self.assertNotEqual(subprocess.run([sys.executable,'-s','-B','-c',raw,str(lane)],capture_output=True).returncode,0)

if __name__=='__main__':unittest.main()
