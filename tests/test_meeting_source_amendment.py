"""Synthetic controls for a source amendment preserving approval and accounting."""
import copy,json,sqlite3,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from tools import amend_meeting_source as r
from orchestrator.manual_driver import Driver

class SupplementTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  root=Path(self.tmp.name);self.root=root;state=root/"lane";state.mkdir(mode=0o700);ctx=root/"context";ctx.mkdir(mode=0o700)
  db=sqlite3.connect(state/"jobs.sqlite",isolation_level=None);db.row_factory=sqlite3.Row;self.addCleanup(db.close)
  batch=sqlite3.connect(root/"batch.sqlite",isolation_level=None);batch.row_factory=sqlite3.Row;self.addCleanup(batch.close)
  db.executescript("CREATE TABLE manual_calls(id TEXT,status TEXT);CREATE TABLE manual_state(id INTEGER,payload TEXT);CREATE TABLE manual_account(id INTEGER,calls INTEGER);")
  batch.executescript("CREATE TABLE autonomy_calls(id TEXT,change_id TEXT,status TEXT);CREATE TABLE autonomy_runs(id TEXT,status TEXT);")
  for name in ["author","review"]:
   db.execute("INSERT INTO manual_calls VALUES(?,'COMPLETE')",(name,))
   batch.execute("INSERT INTO autonomy_calls VALUES(?,?,'COMPLETE')",(name,r.RUN))
  db.execute("INSERT INTO manual_account VALUES(1,2)");batch.execute("INSERT INTO autonomy_runs VALUES(?,'ACTIVE')",(r.RUN,))
  config={"run_id":r.RUN};(state/"lane.json").write_bytes(r.canonical(config))
  source=b"accepted scientific source";tests=b"accepted scientific tests"
  isolation={"credentials":False,"denied_paths":15,"network":"UNSHARED","package_read_only":True,"patient_mounts":False,"status":"ISOLATED","workspace_writable":True}
  bodies={"review":r.canonical({"verdict":"APPROVE","findings":[]}),
          "accepted_source":source,"accepted_tests":tests,
          "synthetic":r.canonical({"status":"PASS","binding":{"files":{"analysis.py":r.sha(source),"test_analysis.py":r.sha(tests)}},"isolation":isolation}),
          "accepted_spec":b"accepted preparation spec"}
  refs={}
  for name,raw in bodies.items():
   p=root/(name+".txt");p.write_bytes(raw);refs[name]={"path":str(p),"sha256":r.sha(raw),"bytes":len(raw)}
  (ctx/"original.txt").write_bytes(b"original scientific artifact")
  value={"phase":"COMMIT_SPEC","reason":None,"rounds":{"run_spec_author":1,"run_spec_review":1},
   "artifacts":[{"id":"existing","type":"notebook_source","path":"original.txt","sha256":r.sha(b"original scientific artifact"),"version":1}],
   "interventions":[],"program_result":{"synthetic_status":"PASS","synthetic_receipt_sha256":r.sha(bodies["synthetic"])}}
  db.execute("INSERT INTO manual_state VALUES(1,?)",(json.dumps(value),))
  d=SimpleNamespace(state=state,context=ctx,config=config,store=SimpleNamespace(path=state/"jobs.sqlite",db=db,batch=SimpleNamespace(db=batch,folder=root)))
  d.guard=lambda:None;d.current=lambda:json.loads(db.execute("SELECT payload FROM manual_state").fetchone()[0])
  d.artifact=lambda *args:Driver.artifact(d,*args)
  d.prepare_input=lambda value,stage,work:(" ".join(x["sha256"]for x in value["artifacts"]),{"stage":stage,"model_calls":0})
  self.d=d;self.b={"run_id":r.RUN,"lane":str(state),"config":config,"configuration_sha256":r.sha((state/"lane.json").read_bytes()),
   "state_row":dict(db.execute("SELECT * FROM manual_state").fetchone()),"account_row":dict(db.execute("SELECT * FROM manual_account").fetchone()),
   "local_rows":[dict(x)for x in db.execute("SELECT * FROM manual_calls")],"global_rows":[dict(x)for x in batch.execute("SELECT * FROM autonomy_calls")],
   "owner":dict(batch.execute("SELECT * FROM autonomy_runs").fetchone()),"files":refs,"evidence_sha256":r.sha(b"source inventory")}
  self.approval={"source_sha":"b"*40,"report_sha256":"c"*64}
 def apply(self):return r.apply(self.d,self.b,self.approval,b"source amendment; original approval retained",b"source inventory")
 def test_amendment_preserves_approval_calls_and_all_unrelated_state(self):
  before=self.d.current();batch_before="\n".join(self.d.store.batch.db.iterdump());result=self.apply();after=self.d.current()
  self.assertEqual(result["model_calls"],0);self.assertEqual(result["new_allowance"],0)
  self.assertEqual(after["artifacts"][:len(before["artifacts"])],before["artifacts"])
  for key in before:
   if key not in {"artifacts","interventions","phase","reason"}:self.assertEqual(before[key],after[key],key)
  self.assertEqual(batch_before,"\n".join(self.d.store.batch.db.iterdump()))
  self.assertEqual(after["phase"],"run_spec_author");self.assertEqual(after["reason"],"SOURCE_AMENDMENT_REQUIRED")
  self.assertEqual(after["rounds"],before["rounds"])
  r.originals(self.d,self.b,state=False)
  self.assertTrue((self.d.state/r.CHANGE/"INPUT_PREFLIGHT.json").is_file())
 def test_consumed_intent_cannot_replay(self):
  self.apply()
  with self.assertRaises(ValueError):self.apply()
 def test_uncertain_intent_refuses(self):
  (self.d.state/r.CHANGE).mkdir()
  with self.assertRaisesRegex(ValueError,"ALREADY_ATTEMPTED"):self.apply()
 def test_live_call_refuses_before_intent(self):
  self.d.store.batch.db.execute("INSERT INTO autonomy_calls VALUES('live','other','RUNNING')")
  with self.assertRaisesRegex(ValueError,"LIVE_MODEL"):self.apply()
  self.assertFalse((self.d.state/r.CHANGE).exists())
 def test_changed_local_call_refuses(self):
  self.d.store.db.execute("UPDATE manual_calls SET status='FAILED' WHERE id='review'")
  with self.assertRaisesRegex(ValueError,"LOCAL_CALLS"):self.apply()
 def test_changed_global_charge_refuses(self):
  self.d.store.batch.db.execute("UPDATE autonomy_calls SET status='FAILED' WHERE id='review'")
  with self.assertRaisesRegex(ValueError,"GLOBAL_CALLS"):self.apply()
 def test_changed_account_refuses(self):
  self.d.store.db.execute("UPDATE manual_account SET calls=0")
  with self.assertRaisesRegex(ValueError,"ACCOUNT"):self.apply()
 def test_changed_owner_refuses(self):
  self.d.store.batch.db.execute("UPDATE autonomy_runs SET status='COMPLETE'")
  with self.assertRaisesRegex(ValueError,"OWNER"):self.apply()
 def test_changed_config_bytes_refuses(self):
  (self.d.state/"lane.json").write_text("{}")
  with self.assertRaisesRegex(ValueError,"CONFIG_BYTES"):self.apply()
 def test_changed_evidence_refuses(self):
  Path(self.b["files"]["accepted_source"]["path"]).write_text("older permissive harness")
  with self.assertRaisesRegex(ValueError,"EVIDENCE_BYTES"):self.apply()
 def test_original_artifact_mutation_refuses(self):
  (self.d.context/"original.txt").write_text("changed")
  with self.assertRaisesRegex(ValueError,"ARTIFACT_BYTES"):self.apply()
 def test_live_pending_or_other_phase_refuses(self):
  value=self.d.current();value["pending"]={"id":"uncertain"}
  raw=json.dumps(value);self.b["state_row"]["payload"]=raw;self.d.store.db.execute("UPDATE manual_state SET payload=?",(raw,))
  with self.assertRaisesRegex(ValueError,"REVISION"):self.apply()
 def test_halt_refuses(self):
  (self.d.state/"HALT").touch()
  with self.assertRaisesRegex(ValueError,"HALT"):self.apply()
 def test_colliding_id_never_replaces_original(self):
  value=self.d.current();value["artifacts"][0]["id"]="question";raw=json.dumps(value)
  self.b["state_row"]["payload"]=raw;self.d.store.db.execute("UPDATE manual_state SET payload=?",(raw,))
  with self.assertRaisesRegex(ValueError,"ARTIFACT_COLLISION"):self.apply()
  self.assertFalse((self.d.state/r.CHANGE).exists())
 def test_input_failure_leaves_state_intact_intent_preserved(self):
  def fail(*a):raise ValueError("delivery failed")
  self.d.prepare_input=fail
  with self.assertRaisesRegex(ValueError,"delivery failed"):self.apply()
  r.originals(self.d,self.b);self.assertTrue((self.d.state/r.CHANGE/"INTENT.json").is_file())
 def test_missing_binding_leaves_state_intact(self):
  self.d.prepare_input=lambda *a:("no supplement binding",{})
  with self.assertRaisesRegex(ValueError,"INPUT_BINDINGS"):self.apply()
  r.originals(self.d,self.b)
 def test_frozen_pins(self):
  root=Path(__file__).parents[1]
  self.assertEqual(r.sha((root/r.DOCUMENT).read_bytes()),r.PIN)
  self.assertEqual(r.sha((root/r.QUESTION).read_bytes()),r.QUESTION_PIN)

 def test_source_evidence_mismatch_refuses_without_intent(self):
  with self.assertRaisesRegex(ValueError,"SOURCE_EVIDENCE"):
   r.apply(self.d,self.b,self.approval,b"question",b"changed evidence")
  self.assertFalse((self.d.state/r.CHANGE).exists());r.originals(self.d,self.b)
 def test_original_revise_or_reject_is_not_relabelled_as_approved(self):
  for verdict in ["REVISE","REJECT"]:
   p=Path(self.b["files"]["review"]["path"]);raw=r.canonical({"verdict":verdict,"findings":[]})
   p.write_bytes(raw);self.b["files"]["review"].update(sha256=r.sha(raw),bytes=len(raw))
   with self.assertRaisesRegex(ValueError,"PRESERVED_APPROVAL"):self.apply()
   self.assertFalse((self.d.state/r.CHANGE).exists())
 def test_synthetic_failure_refuses_without_intent(self):
  p=Path(self.b["files"]["synthetic"]["path"]);v=json.loads(p.read_bytes());v["status"]="FAIL"
  raw=r.canonical(v);p.write_bytes(raw);self.b["files"]["synthetic"].update(sha256=r.sha(raw),bytes=len(raw))
  with self.assertRaisesRegex(ValueError,"TEST_BINDING"):self.apply()
  self.assertFalse((self.d.state/r.CHANGE).exists())
 def test_no_call_allowance_or_limits_are_modified(self):
  before=self.d.config.copy();account=dict(self.d.store.db.execute("SELECT * FROM manual_account").fetchone())
  self.apply()
  self.assertEqual(self.d.config,before)
  self.assertEqual(dict(self.d.store.db.execute("SELECT * FROM manual_account").fetchone()),account)
  self.assertEqual(self.d.store.db.execute("SELECT COUNT(*) FROM manual_calls").fetchone()[0],2)

if __name__=="__main__":unittest.main()
