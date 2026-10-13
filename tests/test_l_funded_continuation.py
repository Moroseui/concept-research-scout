import copy,json,sqlite3,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from orchestrator import l_funded_continuation as r
from orchestrator.manual_driver import Driver
class ContinuationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  root=Path(self.tmp.name);self.root=root;state=root/"lane";state.mkdir(mode=0o700);ctx=root/"context";ctx.mkdir(mode=0o700)
  db=sqlite3.connect(state/"jobs.sqlite",isolation_level=None);db.row_factory=sqlite3.Row;self.addCleanup(db.close)
  batch=sqlite3.connect(root/"batch.sqlite",isolation_level=None);batch.row_factory=sqlite3.Row;self.addCleanup(batch.close)
  db.executescript("CREATE TABLE manual_calls(id TEXT,status TEXT);CREATE TABLE manual_state(id INTEGER,payload TEXT);CREATE TABLE manual_account(id INTEGER,calls INTEGER);")
  batch.executescript("CREATE TABLE autonomy_calls(id TEXT,change_id TEXT,status TEXT);CREATE TABLE autonomy_runs(id TEXT,status TEXT);")
  for name in ["author1","review1","author2","review2"]:
   db.execute("INSERT INTO manual_calls VALUES(?,'COMPLETE')",(name,))
   batch.execute("INSERT INTO autonomy_calls VALUES(?,?,'COMPLETE')",(name,r.RUN))
  db.execute("INSERT INTO manual_account VALUES(1,4)");batch.execute("INSERT INTO autonomy_runs VALUES(?,'ACTIVE')",(r.RUN,))
  config={"run_id":r.RUN};(state/"lane.json").write_bytes(r.encoded(config))
  notebook_sha="a"*64;harness=b"synthetic original harness"
  isolation={"credentials":False,"denied_paths":15,"network":"UNSHARED","package_read_only":True,"patient_mounts":False,"status":"ISOLATED","workspace_writable":True}
  bodies={"review":r.encoded({"verdict":"REVISE","findings":[{"id":str(i)}for i in range(4)]}),
          "harness":harness,"synthetic":r.encoded({"status":"FAIL","binding":{"files":{"run.py":r.sha(harness),"revised.ipynb":notebook_sha}},"isolation":isolation}),
          "accepted_source":b"accepted scientific source","accepted_provenance":b"original provenance"}
  refs={}
  for name,raw in bodies.items():
   p=root/(name+".txt");p.write_bytes(raw);refs[name]={"path":str(p),"sha256":r.sha(raw),"bytes":len(raw)}
  (ctx/"original.txt").write_bytes(b"original scientific artifact")
  value={"phase":"run_spec_author","reason":"REVISION_REQUIRED","rounds":{"run_spec_author":2,"run_spec_review":2},
   "artifacts":[{"id":"existing","type":"notebook_source","path":"original.txt","sha256":r.sha(b"original scientific artifact"),"version":1}],
   "interventions":[],"notebook_revision_result":{"notebook_sha256":notebook_sha,"synthetic_status":"FAIL"}}
  db.execute("INSERT INTO manual_state VALUES(1,?)",(json.dumps(value),))
  d=SimpleNamespace(state=state,context=ctx,config=config,store=SimpleNamespace(path=state/"jobs.sqlite",db=db,batch=SimpleNamespace(db=batch,folder=root)))
  d.guard=lambda:None;d.current=lambda:json.loads(db.execute("SELECT payload FROM manual_state").fetchone()[0])
  d.artifact=lambda *args:Driver.artifact(d,*args)
  d.prepare_input=lambda value,stage,work:(" ".join(x["sha256"]for x in value["artifacts"]),{"stage":stage,"model_calls":0})
  self.d=d;self.b={"run_id":r.RUN,"lane":str(state),"config":config,"config_sha256":r.sha((state/"lane.json").read_bytes()),
   "state_row":dict(db.execute("SELECT * FROM manual_state").fetchone()),"account_row":dict(db.execute("SELECT * FROM manual_account").fetchone()),
   "local_rows":[dict(x)for x in db.execute("SELECT * FROM manual_calls")],"global_rows":[dict(x)for x in batch.execute("SELECT * FROM autonomy_calls")],
   "owner":dict(batch.execute("SELECT * FROM autonomy_runs").fetchone()),"files":refs}
  self.approval={"source_sha":"b"*40,"report_sha256":"c"*64}
  self.question=b"Respond to genuine scientific revision; no changed science from operator"
  self.baseline=b'{"reference":"authenticated synthetic baseline descriptor"}'
  self.pins={"question_sha256":r.sha(self.question),"baseline_sha256":r.sha(self.baseline)}
 def apply(self):
  return r.apply(self.d,{"lanes":{"L":self.b}},self.approval,self.question,self.baseline,self.pins)

 def test_additive_context_keeps_phase_verdict_calls_and_original_artifacts(self):
  before=self.d.current();batch="\n".join(self.d.store.batch.db.iterdump())
  result=self.apply();after=self.d.current()
  self.assertEqual(result["model_calls"],0)
  for key in before:
   if key not in {"artifacts","interventions"}:self.assertEqual(before[key],after[key])
  self.assertEqual(after["artifacts"][:len(before["artifacts"])],before["artifacts"])
  self.assertEqual(batch,"\n".join(self.d.store.batch.db.iterdump()))
  r.original_lane(self.d,self.b,state=False)
 def test_replay_refuses(self):
  self.apply()
  with self.assertRaises(ValueError):self.apply()
 def test_uncertain_intent_refuses(self):
  (self.d.state/r.CHANGE).mkdir()
  with self.assertRaisesRegex(ValueError,"ALREADY_ATTEMPTED"):self.apply()
 def test_running_model_refuses_before_intent(self):
  self.d.store.batch.db.execute("INSERT INTO autonomy_calls VALUES('live','other','RUNNING')")
  with self.assertRaisesRegex(ValueError,"LIVE_MODEL"):self.apply()
  self.assertFalse((self.d.state/r.CHANGE).exists())
 def test_changed_original_charge_refuses(self):
  self.d.store.batch.db.execute("UPDATE autonomy_calls SET status='FAILED' WHERE id='review2'")
  with self.assertRaisesRegex(ValueError,"GLOBAL_CALLS"):self.apply()
 def test_changed_local_count_refuses(self):
  self.d.store.db.execute("UPDATE manual_account SET calls=0")
  with self.assertRaisesRegex(ValueError,"ACCOUNT"):self.apply()
 def test_artifact_mutation_refuses(self):
  (self.d.context/"original.txt").write_text("changed")
  with self.assertRaisesRegex(ValueError,"ARTIFACT_CHANGED"):self.apply()
 def test_question_and_baseline_hashes_required(self):
  for key in ("question_sha256","baseline_sha256"):
   pins=copy.deepcopy(self.pins);self.pins[key]="0"*64
   with self.assertRaisesRegex(ValueError,"CONTEXT_BINDINGS"):self.apply()
   self.pins=pins
 def test_input_failure_preserves_original_state_and_durable_intent(self):
  def fail(*args):raise ValueError("input delivery failed")
  self.d.prepare_input=fail
  with self.assertRaisesRegex(ValueError,"input delivery failed"):self.apply()
  r.original_lane(self.d,self.b)
  self.assertTrue((self.d.state/r.CHANGE/"INTENT.json").is_file())
 def test_halt_refuses(self):
  (self.d.state/"HALT").touch()
  with self.assertRaisesRegex(ValueError,"HALT"):self.apply()
if __name__=="__main__":unittest.main()
