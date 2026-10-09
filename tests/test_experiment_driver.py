"""Real initialization and ledger integration; synthetic evidence/native verifier only."""
import copy
import json
import subprocess
from pathlib import Path
import pytest
from orchestrator import experiment_driver as ed, experiment_context as ec
from orchestrator import diagnostics_policy as dp, analysis_revisions as ar
from orchestrator import private_records as pr
from orchestrator.manual_executor import atomic, digest, read
from orchestrator.autonomy_accounting import BatchAccounts
from test_analysis_driver import initialization, analysis_lane
from test_manual_lane import lane, root, ROOT
from test_scientific_intake import save_registry
from test_item4_notebook_controller import configured

@pytest.fixture
def prepared(initialization, monkeypatch):
    d, review, approval = initialization
    for path in (ROOT/"orchestrator").glob("*.py"):
        pr.write_bytes(d.root/"orchestrator"/path.name, path.read_bytes())
    from orchestrator import autonomy_limits
    for name in [autonomy_limits.DOCUMENT, dp.DOCUMENT,
            "docs/SPRINT13B_EXECUTION_OPERATOR_DECISION.txt", "docs/SPRINT13B_TEAM_OPERATOR_DECISION.txt"]:
        pr.write_bytes(d.root/name, (ROOT/name).read_bytes())
    old = read(d.state/"preparation-plan.json")
    reg = read(d.context/old["private_intake"]["path"])
    reg.update(task=dp.TASK, idea_ids=[dp.TASK]); ref=save_registry(d.context,reg)
    rawplan=b'{"synthetic_fixture":true,"purpose":"interface verification only"}'
    pr.write_bytes(d.context/"execution-plan.json",rawplan)
    body=(ROOT/"docs/DIAGNOSTICS_BACKLOG_ITEM.txt").read_bytes()
    assert digest(body)==dp.ITEM_SHA256
    authority=(ROOT/dp.DOCUMENT).read_bytes()
    binding={"schema":"operator-backlog/v1","backlog_sha256":digest(body),"operator_sha256":digest(authority),
        "items":[{"number":6,"sha256":dp.ITEM_SHA256,"mode":"cpu","state":"AUTHORIZED","prerequisites":[]}]}
    refs={}
    for key,name,raw in [("backlog","BACKLOG.md",body),("operator","operator.txt",authority),
        ("backlog_binding","backlog-binding.json",json.dumps(binding).encode())]:
        pr.write_bytes(d.context/name,raw);refs[key]={"path":name,"sha256":digest(raw)}
    plan={"schema":"experiment-lane/v1","context":str(d.context),"context_files":{},**refs,
        "item_number":6,"item_sha256":dp.ITEM_SHA256,"private_intake":ref,"idea_ids":[dp.TASK],
        "artifacts":[],"batch_ledger":str(d.store.batch.folder),"prerequisites":[],
        "execution_scope":scope(6),"execution_plan":{"path":"execution-plan.json","sha256":digest(rawplan)},
        "revision_policy":copy.deepcopy(ar.POLICY),"diagnostics":dp.policy(),
        "synthetic_environment":{"environment_root":"/synthetic-tools","environment_sha256":"a"*64},
        "execution_provisioning":str(d.state/"future-cpu-runtime")}
    plan["execution_scope"]["plan_sha256"]=digest(rawplan)
    monkeypatch.setattr("orchestrator.cpu_isolation.verify_environment",lambda cfg:Path(cfg["environment_root"]))
    plan["context_files"]={str(p.relative_to(d.context)):digest(p.read_bytes()) for p in d.context.rglob("*") if p.is_file()}
    atomic(d.state/"preparation-plan.json",plan)
    atomic(review.parent/"packet-manifest.json",{"files":{"evidence/experiment-plan.json":digest((d.state/"preparation-plan.json").read_bytes())}})
    d.store.batch.complete_run(d.config["run_id"],{"synthetic":True})
    with pr.umask():
        subprocess.run(["git","add","."],cwd=d.root,check=True,capture_output=True)
        subprocess.run(["git","commit","-qm","Exact source; synthetic experiment fixture"],cwd=d.root,check=True)
    approval["source_sha"]=ed.git(d.root,"rev-parse","HEAD")
    return d,review,approval,plan


def init(p,name="new-experiment"):
    d,review,_,_=p
    return ed.initialize(d.root,d.state/name,review,d.state/"preparation-plan.json")


def test_real_initialization_and_context_without_legacy_executor(prepared):
    d,_,_,_=prepared; result=init(prepared)
    assert result=={"status":"READY","run_id":dp.RUN_ID,"next":"run_spec_author","calls_used":0,"call_limit":30}
    driver=ed.ExperimentDriver(d.state/"new-experiment",runner=lambda *a:pytest.fail("No model call"))
    driver.guard(); assert driver.status()["call_limit"]==30
    assert type(driver.store).__name__=="ManualExecutor" and driver.store.batch is not None
    text,measurement=driver.prepare_input(driver.current(),"run_spec_author",driver.state/"assembly-proof")
    assert "interface verification only" in text and "Sprint10 known-case" not in text and len(text)<200000
    assert measurement["execution_mode"]==dp.TASK
    assert not driver.store.db.execute("SELECT 1 FROM manual_calls").fetchone()
    with pytest.raises(ValueError,match="^EXISTING_EXPERIMENT_OWNER_NO_NEW_ALLOWANCE$"):init(prepared,"duplicate")
    assert not (d.state/"duplicate").exists()


@pytest.mark.parametrize("key,value",[("verdict","REJECT"),("source_sha","0"*40),("runtime_sha256","0"*64),("report_sha256","0"*64)])
def test_wrong_approval_prevents_owner(prepared,key,value):
    prepared[2][key]=value
    with pytest.raises(ValueError,match="^QUALIFIED_EXACT_ENGINE_APPROVAL_REQUIRED$"):init(prepared)
    assert not (prepared[0].state/"new-experiment").exists()


def test_unreviewed_plan_refused(prepared):
    atomic(prepared[1].parent/"packet-manifest.json",{"files":{}})
    with pytest.raises(ValueError,match="^REVIEWED_EXPERIMENT_PLAN_REQUIRED$"):init(prepared)
    assert not list((prepared[0].root/".git").glob("experiment-owner-*"))


@pytest.mark.parametrize("file",["execution-plan.json","view.txt","BACKLOG.md"])
def test_changed_original_blocks(prepared,file):
    pr.write_text(prepared[0].context/file,"changed")
    with pytest.raises(ValueError,match="^EXPERIMENT_CONTEXT_INVENTORY_CHANGED$"):init(prepared)
    assert not (prepared[0].state/"new-experiment").exists()


@pytest.mark.parametrize("field,value",[("item_number",4),("batch_ledger","/other-ledger"),("execution_plan",{})])
def test_changed_configuration_blocks_without_call(prepared,field,value):
    init(prepared);driver=ed.ExperimentDriver(prepared[0].state/"new-experiment")
    driver.config[field]=value
    with pytest.raises((ValueError,KeyError)):driver.guard()
    assert not driver.store.db.execute("SELECT 1 FROM manual_calls").fetchone()


def test_other_active_owner_refuses_before_new_state(prepared):
    prepared[0].store.batch.register_run("unrelated",{"synthetic":True})
    with pytest.raises(ValueError,match="^ONE_ACTIVE_RESEARCH_RUN$"):init(prepared)
    assert not (prepared[0].state/"new-experiment").exists()


def test_halt_refuses_before_owner(prepared):
    d=prepared[0];pr.write_text(d.store.batch.folder/"HALT","Synthetic stop")
    with pytest.raises(ValueError,match="^AUTONOMY_BATCH_HALTED$"):init(prepared)
    assert not (d.state/"new-experiment").exists()


def scope(item):
    from orchestrator.modal_item4_policy import AUTHORITY
    return {"schema":"scientific-execution/v1","item_number":item,
        "run_id":ec.ITEM4_RUN if item==4 else dp.RUN_ID,"authority_sha256":AUTHORITY if item==4 else dp.AUTHORITY,
        "plan_sha256":"a"*64}


def owner(batch,tmp_path,item):
    s=scope(item);state=tmp_path/("lane"+str(item));pr.mkdir(state)
    raw=json.dumps({"execution_scope":s,"synthetic":True}).encode();pr.write_bytes(state/"preparation-plan.json",raw)
    b={"state":str(state),"run_id":s["run_id"],"source":"a"*40,"plan_sha256":digest(raw),
        "review_sha256":"b"*64,"execution_scope":s}
    batch.register_experiment_run(s["run_id"],b)
    atomic(state/"lane.json",{"run_id":s["run_id"],"item_number":item,"backend":"modal" if item==4 else "cpu",
        "diagnostics":dp.policy(),"owner_binding":b,"execution_scope":s,"plan_sha256":digest(raw)})
    return b


@pytest.mark.parametrize("order",[(4,6),(6,4)])
def test_canonical_parallel_pair_and_legacy_registration_unchanged(tmp_path,order):
    b=BatchAccounts(tmp_path/"ledger")
    for item in order:owner(b,tmp_path,item)
    assert b.db.execute("SELECT count(*) FROM autonomy_runs WHERE status='ACTIVE'").fetchone()[0]==2
    with pytest.raises(ValueError,match="^ONE_ACTIVE_RESEARCH_RUN$"):b.register_run("third",{})
    with pytest.raises(ValueError,match="^EXISTING_EXPERIMENT_OWNER_NO_NEW_ALLOWANCE$"):
        b.preflight_experiment_run(dp.RUN_ID,scope(6))
    assert not b.db.execute("SELECT 1 FROM autonomy_calls").fetchone()


@pytest.mark.parametrize("key,value",[("run_id","other"),("item_number",True),("authority_sha256","0"*64),("plan_sha256","g"*64)])
def test_parallel_scope_cannot_expand(tmp_path,key,value):
    b=BatchAccounts(tmp_path/"ledger");binding={"run_id":dp.RUN_ID,"execution_scope":scope(6)}
    binding["execution_scope"][key]=value
    with pytest.raises(ValueError,match="^EXPERIMENT_PARALLEL_SCOPE_REQUIRED$"):b.preflight_experiment_run(dp.RUN_ID,binding["execution_scope"])
    assert not b.db.execute("SELECT 1 FROM autonomy_runs").fetchone()


@pytest.mark.parametrize("status",["RUNNING","UNCERTAIN"])
def test_parallel_owners_do_not_bypass_uncertain_call(tmp_path,status):
    b=BatchAccounts(tmp_path/"ledger");owner(b,tmp_path,4);owner(b,tmp_path,6)
    b.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",("pending","scientific",ec.ITEM4_RUN,1,"2020-01-01",status,"{}","{}"))
    with pytest.raises(ValueError,match="^BATCH_UNCERTAIN_OR_RUNNING_CALL$"):
        b.reserve_scientific("new",dp.RUN_ID,"run_spec_author","a"*40,{})
    assert b.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==1


def add_prerequisite(prepared):
    d,review,_,plan=prepared
    body=b"1. Synthetic previously reviewed analysis.\n"+(ROOT/"docs/DIAGNOSTICS_BACKLOG_ITEM.txt").read_bytes()
    from orchestrator.autonomy_backlog import numbered_items
    parts=numbered_items(body)
    binding=read(d.context/"backlog-binding.json");binding["backlog_sha256"]=digest(body)
    binding["items"].insert(0,{"number":1,"sha256":parts[1][1],"mode":"analysis","state":"AUTHORIZED","prerequisites":[]})
    binding["items"][1]["prerequisites"]=[1]
    for key,name,raw in [("backlog","BACKLOG.md",body),("backlog_binding","backlog-binding.json",json.dumps(binding).encode())]:
        pr.write_bytes(d.context/name,raw);plan[key]={"path":name,"sha256":digest(raw)}
    report=b"Synthetic prerequisite report; no scientific result."
    pr.write_bytes(d.context/"accepted-prior.md",report)
    prior_run="synthetic-completed-analysis";state=d.state/"prior-accepted";pr.mkdir(state)
    prior_owner={"state":str(state),"source":"b"*40}
    atomic(state/"lane.json",{"item_number":1,"run_id":prior_run,"owner_binding":prior_owner})
    d.store.batch.register_run(prior_run,prior_owner)
    d.store.batch.complete_run(prior_run,{"report_sha256":digest(report)})
    plan["prerequisites"]=[{"item_number":1,"run_id":prior_run,"report":{"path":"accepted-prior.md","sha256":digest(report)}}]
    plan["context_files"]={str(p.relative_to(d.context)):digest(p.read_bytes()) for p in d.context.rglob("*") if p.is_file()}
    atomic(d.state/"preparation-plan.json",plan)
    atomic(review.parent/"packet-manifest.json",{"files":{"evidence/experiment-plan.json":digest((d.state/"preparation-plan.json").read_bytes())}})
    return prior_run,state


def test_real_prerequisite_rows_and_hashes_are_consumed(prepared):
    run,_=add_prerequisite(prepared)
    before=[tuple(r) for r in prepared[0].store.batch.db.execute("SELECT * FROM events WHERE job=?",(run,))]
    assert init(prepared)["status"]=="READY"
    assert before==[tuple(r) for r in prepared[0].store.batch.db.execute("SELECT * FROM events WHERE job=?",(run,))]


@pytest.mark.parametrize("change",["status","receipt","wrong-item","owner"])
def test_prerequisite_claim_is_not_acceptance(prepared,change):
    run,state=add_prerequisite(prepared);d=prepared[0]
    if change=="status":d.store.batch.db.execute("UPDATE autonomy_runs SET status='ACTIVE' WHERE id=?",(run,));code="EXPERIMENT_PREREQUISITE_NOT_ACCEPTED"
    elif change=="receipt":
        d.store.batch.db.execute("UPDATE events SET payload='{}' WHERE id=?",(run+":accepted",));code="EXPERIMENT_PREREQUISITE_BINDING"
    else:
        config=read(state/"lane.json");config["item_number" if change=="wrong-item" else "owner_binding"]=2 if change=="wrong-item" else {}
        atomic(state/"lane.json",config);code="EXPERIMENT_PREREQUISITE_BINDING"
    with pytest.raises(ValueError,match="^"+code+"$"):init(prepared)
    assert not (d.state/"new-experiment").exists()


@pytest.mark.parametrize("limit",["daily","batch"])
def test_parallel_pair_keeps_shared_caps(tmp_path,limit):
    from datetime import datetime,timezone
    b=BatchAccounts(tmp_path/"ledger");owner(b,tmp_path,4);owner(b,tmp_path,6)
    count=30 if limit=="daily" else 60
    kind="implementation_review" if limit=="daily" else "scientific"
    day=datetime.now(timezone.utc).date().isoformat() if limit=="daily" else "2020-01-01"
    for i in range(count):b.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",(str(i),kind,"other",i+1,day,"FAILED","{}","{}"))
    code="AUTONOMY_DAILY_CALL_LIMIT" if limit=="daily" else "AUTONOMY_BATCH_CALL_LIMIT"
    with pytest.raises(ValueError,match="^"+code+"$"):b.reserve_scientific("new",dp.RUN_ID,"run_spec_author","a"*40,{})
    assert b.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==count


def test_other_owner_changed_plan_refuses_parallel_init(tmp_path):
    b=BatchAccounts(tmp_path/"ledger");first=owner(b,tmp_path,4)
    pr.write_text(Path(first["state"])/"preparation-plan.json","{}")
    with pytest.raises(ValueError,match="^EXPERIMENT_PARALLEL_OWNER_CHANGED$"):
        b.preflight_experiment_run(dp.RUN_ID,scope(6))
    assert b.db.execute("SELECT count(*) FROM autonomy_runs").fetchone()[0]==1


def test_initialized_lane_reserves_through_actual_local_and_global_accounting(prepared):
    from orchestrator.manual_executor import Accounts
    init(prepared);d=ed.ExperimentDriver(prepared[0].state/"new-experiment")
    d.guard()
    ident,attempt,receipt=d.store.reserve_call(d.config['run_id'],'run_spec_author',d.config['source'],
        d.config['branch'],d.config['policy'],{'synthetic_transport':True})
    assert attempt==1 and receipt['accounting']['status']=='ADMITTED'
    assert receipt['accounting']['limit_amendment']['run_limit']==30
    assert receipt['batch_accounting']['run_limit']==30
    assert Accounts(d.store).read()[1]['count']==1
    assert d.store.batch.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==1
    with pytest.raises(ValueError,match='^UNCERTAIN_MODEL_CALL_NO_RETRY$'):
        d.store.reserve_call(d.config['run_id'],'run_spec_author',d.config['source'],d.config['branch'],d.config['policy'],{})
    d.store.finish_call(ident,{'synthetic_transport':True},'COMPLETE')
    assert d.store.batch.status(ident)['status']=='COMPLETE'


def test_incompatible_accounting_branch_refuses_before_allowance(prepared):
    d=prepared[0]
    with pr.umask():subprocess.run(['git','checkout','-b','astra/unbound-branch'],cwd=d.root,check=True,capture_output=True)
    with pytest.raises(ValueError,match='^EXPERIMENT_ACCOUNTED_BRANCH_REQUIRED$'):init(prepared)
    assert not (d.state/'new-experiment').exists()


def prepare_item4(prepared,monkeypatch):
    d,review,_,plan=prepared
    # Keep the composed notebook fixture inside the ignored private test lane,
    # not as untracked files in the exact-source checkout being initialized.
    fixture_root=d.state/'item4-fixture';pr.mkdir(fixture_root)
    fixture,cfg,_,_=configured.__wrapped__(fixture_root,monkeypatch)
    cfg=copy.deepcopy(cfg)
    for key in ['authority','scientific_ownership','selection','safe_view','backlog','backlog_binding','carried_conditions']:
        ref=cfg[key];name='notebook/'+ref['path']
        pr.mkdir((d.context/name).parent,parents=True,exist_ok=True)
        pr.write_bytes(d.context/name,(fixture/ref['path']).read_bytes());cfg[key]['path']=name
    body=b'4. Approved synthetic item4 execution interface.\n'
    binding=read(d.context/'backlog-binding.json');binding['backlog_sha256']=digest(body)
    binding['items']=[{'number':4,'sha256':digest(body),'mode':'gpu','state':'AUTHORIZED','prerequisites':[]}]
    pr.write_bytes(d.context/'BACKLOG.md',body);pr.write_text(d.context/'backlog-binding.json',json.dumps(binding))
    reg=read(d.context/plan['private_intake']['path']);reg.update(task=ec.TASKS[4],idea_ids=[ec.TASKS[4]])
    provisioning=d.state/'synthetic-root-provisioning';pr.mkdir(provisioning)
    monkeypatch.setattr('orchestrator.manual_host_guard.trusted',lambda path:Path(path)) # Root provenance simulated only.
    plan.update(item_number=4,item_sha256=digest(body),idea_ids=[ec.TASKS[4]],notebook_revision=cfg,
        execution_provisioning=str(provisioning),
        private_intake=save_registry(d.context,reg),execution_scope={**scope(4),'plan_sha256':plan['execution_plan']['sha256']})
    plan.pop('synthetic_environment');plan.pop('diagnostics')
    for key in ['backlog','backlog_binding']:plan[key]['sha256']=digest((d.context/plan[key]['path']).read_bytes())
    plan['context_files']={str(p.relative_to(d.context)):digest(p.read_bytes()) for p in d.context.rglob('*') if p.is_file()}
    atomic(d.state/'preparation-plan.json',plan)
    atomic(review.parent/'packet-manifest.json',{'files':{'evidence/experiment-plan.json':digest((d.state/'preparation-plan.json').read_bytes())}})


def test_item4_initializer_uses_actual_notebook_validator_and_twenty_call_account(prepared,monkeypatch):
    prepare_item4(prepared,monkeypatch)
    d=prepared[0]
    result=init(prepared);assert result['call_limit']==20 and result['run_id']==ec.ITEM4_RUN
    driver=ed.ExperimentDriver(d.state/'new-experiment');driver.guard()
    text,measured=driver.prepare_input(driver.current(),'run_spec_author',driver.state/'assembly-proof')
    assert measured['execution_mode']==ec.TASKS[4] and 'notebook.patch.json' in measured['outputs']
    assert 'Sprint10 known-case' not in text
    ident,_,receipt=driver.store.reserve_call(ec.ITEM4_RUN,'run_spec_author',driver.config['source'],
        driver.config['branch'],driver.config['policy'],{'synthetic_transport':True})
    assert receipt['accounting']['limit_amendment']['run_limit']==20
    assert receipt['batch_accounting']['run_limit']==20
    driver.store.finish_call(ident,{'synthetic_transport':True},'COMPLETE')


def test_completed_owner_allows_only_hash_bound_report_finalization(prepared):
    init(prepared);d=ed.ExperimentDriver(prepared[0].state/'new-experiment')
    value=d.current();value['phase']='REPORT';d.save(value)
    raw=b'Synthetic completed report; no scientific result.\n'
    pr.write_bytes(d.state/'REPORT.md',raw)
    d.store.batch.complete_run(d.config['run_id'],{'report_sha256':digest(raw)})
    rows=list(d.store.batch.db.iterdump())
    d.guard()
    value['phase']='COMPLETE';d.save(value);d.guard()
    assert list(d.store.batch.db.iterdump())==rows
    value['phase']='run_spec_author';d.save(value)
    with pytest.raises(ValueError,match='^EXPERIMENT_GLOBAL_OWNER_CHANGED$'):d.guard()
    value['phase']='REPORT';d.save(value);pr.write_bytes(d.state/'REPORT.md',b'changed')
    with pytest.raises(ValueError,match='^EXPERIMENT_GLOBAL_OWNER_CHANGED$'):d.guard()
    pr.write_bytes(d.state/'REPORT.md',raw)
    d.store.batch.db.execute('DELETE FROM events WHERE id=?',(d.config['run_id']+':accepted',))
    with pytest.raises(ValueError,match='^EXPERIMENT_GLOBAL_OWNER_CHANGED$'):d.guard()
    assert not d.store.db.execute('SELECT 1 FROM manual_calls').fetchone()
