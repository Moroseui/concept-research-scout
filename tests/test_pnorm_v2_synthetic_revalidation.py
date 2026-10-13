"""Bounded recovery control tests; synthetic data only."""
import copy,json,sqlite3,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from tools import revalidate_pnorm_v2_synthetic as r

class RevalidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.state=self.root/'lane';self.state.mkdir(mode=0o700)
        self.ctx=self.root/'context';self.ctx.mkdir(mode=0o700)
        self.work=self.root/'workspace';self.work.mkdir(mode=0o700)
        self.folder=self.state/'notebook-revisions/author-1';self.folder.mkdir(parents=True,mode=0o700)
        self.nb=b'{"synthetic_fixture":true}';(self.folder/'revised.ipynb').write_bytes(self.nb)
        (self.folder/'original-failed-test.json').write_text('{"status":"FAIL"}')
        review=b'{"verdict":"APPROVE","findings":[]}';(self.work/'review.json').write_bytes(review)
        (self.ctx/'tests-original.json').write_text('{"status":"FAIL"}')
        config={'run_id':r.RUN,'context':str(self.ctx),'notebook_revision':{'environment':{'synthetic_fixture':True}}}
        (self.state/'lane.json').write_bytes(r.canonical(config))
        self.value={'phase':'BLOCKED','reason':r.REASON,'pending':{'id':r.CALL,'stage':'run_spec_review','round':2,'workspace':str(self.work)},
          'artifacts':[{'id':'synthetic_tests','type':'synthetic_tests','path':'tests-original.json','sha256':r.sha((self.ctx/'tests-original.json').read_bytes())}],
          'notebook_revision_result':{'folder':str(self.folder),'notebook_sha256':r.sha(self.nb),'tests_sha256':'a'*64,'synthetic_status':'FAIL'},'interventions':[]}
        db=sqlite3.connect(self.state/'jobs.sqlite',isolation_level=None);db.row_factory=sqlite3.Row;self.addCleanup(db.close)
        batch=sqlite3.connect(self.root/'batch.sqlite',isolation_level=None);batch.row_factory=sqlite3.Row;self.addCleanup(batch.close)
        db.executescript("CREATE TABLE manual_calls(id TEXT,stage TEXT,attempt INTEGER,status TEXT,receipt TEXT);CREATE TABLE manual_account(id INTEGER,calls INTEGER);CREATE TABLE manual_state(id INTEGER,payload TEXT);")
        batch.executescript("CREATE TABLE autonomy_calls(id TEXT,kind TEXT,change_id TEXT,status TEXT);CREATE TABLE autonomy_runs(id TEXT,status TEXT);")
        for ident,stage,attempt,status in [('author','run_spec_author',1,'COMPLETE'),('failed','run_spec_review',1,'FAILED'),(r.CALL,'run_spec_review',2,'COMPLETE')]:
            db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(ident,stage,attempt,status,'preserved'))
            batch.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?)',(ident,'scientific',r.RUN,status))
        db.execute('INSERT INTO manual_account VALUES(1,3)');db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps(self.value),))
        batch.execute('INSERT INTO autonomy_runs VALUES(?,?)',(r.RUN,'ACTIVE'))
        self.d=SimpleNamespace(state=self.state,context=self.ctx,config=config,store=SimpleNamespace(db=db,path=self.state/'jobs.sqlite',batch=SimpleNamespace(db=batch,folder=self.root)))
        self.d.guard=lambda:None
        self.d.current=lambda:json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
        self.accepted=[]
        def artifact(value,kind,name,raw,version):
            (self.ctx/name).write_bytes(raw);value['artifacts']=[{'id':kind,'type':kind,'path':name,'sha256':r.sha(raw),'version':version}]
        self.d.artifact=artifact
        def accept(value):
            self.assertEqual(value['notebook_revision_result']['synthetic_status'],'PASS')
            self.accepted.append(copy.deepcopy(value));value.pop('pending');value.update(phase='COMMIT_SPEC',spec_review=str(self.work/'review.json'))
            db.execute('UPDATE manual_state SET payload=?WHERE id=1',(json.dumps(value),));return {'phase':'COMMIT_SPEC'}
        self.d.accept_completed=accept
        self.b={'config':config,'configuration_sha256':r.sha((self.state/'lane.json').read_bytes()),'lane':str(self.state),
           'local_rows':[dict(x)for x in db.execute('SELECT * FROM manual_calls')],
           'global_rows':[dict(x)for x in batch.execute('SELECT * FROM autonomy_calls')],
           'account_row':dict(db.execute('SELECT * FROM manual_account').fetchone()),
           'owner':dict(batch.execute('SELECT * FROM autonomy_runs').fetchone()),
           'state_row':dict(db.execute('SELECT * FROM manual_state').fetchone()),'failed_workspace':str(self.work),
           'files':{'review.json':{'sha256':r.sha(review)}},
           'synthetic_original_files':{p.name:{'bytes':p.stat().st_size,'sha256':r.sha(p.read_bytes())}for p in self.folder.iterdir()}}
        self.approval={'source_sha':'b'*40,'report_sha256':'c'*64}
        self.result={'status':'PASS','binding':{'files':{'revised.ipynb':r.sha(self.nb)}},'isolation':{'status':'ISOLATED','patient_mounts':False,'network':'UNSHARED','credentials':False}}
    def run_retest(self,result=None):
        result=self.result if result is None else result
        return r.retest_and_accept(self.d,self.b,self.approval,lambda *a,**k:result)
    def test_originals_require_exact_state_calls_and_bytes(self):
        self.assertEqual(r.originals(self.d,self.b)[1],self.nb)
        for target,value in [('reason','other'),('phase','run_spec_review')]:
            old=self.b['state_row']['payload'];v=json.loads(old);v[target]=value;self.b['state_row']['payload']=json.dumps(v)
            with self.subTest(target=target),self.assertRaises(ValueError):r.originals(self.d,self.b)
            self.b['state_row']['payload']=old
    def test_pass_preserves_accounting_and_original_failure(self):
        before=self.d.store.batch.db.iterdump();before='\n'.join(before)
        result=self.run_retest()
        self.assertEqual(result['status'],'SYNTHETIC_PASS_NORMAL_SPEC_ACCEPTANCE')
        self.assertEqual(before,'\n'.join(self.d.store.batch.db.iterdump()))
        self.assertEqual((self.ctx/'tests-original.json').read_text(),'{"status":"FAIL"}')
        self.assertEqual(len(self.accepted),1);self.assertEqual(self.d.current()['phase'],'COMMIT_SPEC')
        r.originals(self.d,self.b,state=False)
    def test_failed_test_never_accepts_or_mutates_state(self):
        result=copy.deepcopy(self.result);result['status']='FAIL'
        with self.assertRaisesRegex(ValueError,'SYNTHETIC_PASS'):self.run_retest(result)
        self.assertFalse(self.accepted);r.originals(self.d,self.b)
    def test_invalid_isolation_never_accepts(self):
        self.result['isolation']['credentials']=True
        with self.assertRaisesRegex(ValueError,'SYNTHETIC_PASS'):self.run_retest()
        self.assertFalse(self.accepted);r.originals(self.d,self.b)
    def test_wrong_notebook_binding_refuses(self):
        self.result['binding']['files']['revised.ipynb']='d'*64
        with self.assertRaisesRegex(ValueError,'SYNTHETIC_PASS'):self.run_retest()
        self.assertFalse(self.accepted)
    def test_no_second_retest_after_failed_result(self):
        self.result['status']='FAIL'
        with self.assertRaises(ValueError):self.run_retest()
        with self.assertRaisesRegex(ValueError,'ALREADY_ATTEMPTED'):self.run_retest()
    def test_live_model_refuses_before_intent(self):
        self.d.store.batch.db.execute("INSERT INTO autonomy_calls VALUES('live','scientific','other','RUNNING')")
        with self.assertRaisesRegex(ValueError,'LIVE_MODEL'):self.run_retest()
        self.assertFalse((self.state/r.CHANGE).exists())
    def test_changed_notebook_refuses_before_intent(self):
        (self.folder/'revised.ipynb').write_text('changed')
        with self.assertRaisesRegex(ValueError,'ORIGINAL_BYTES'):self.run_retest()
        self.assertFalse((self.state/r.CHANGE).exists())
    def test_changed_original_charge_refuses(self):
        self.d.store.db.execute("UPDATE manual_calls SET receipt='changed' WHERE id='failed'")
        with self.assertRaisesRegex(ValueError,'CALLS'):self.run_retest()
    def test_scope_pin_matches_frozen_file(self):
        raw=(Path(__file__).parents[1]/r.DOCUMENT).read_bytes()
        self.assertEqual(r.sha(raw),r.PIN)
if __name__=='__main__':unittest.main()
