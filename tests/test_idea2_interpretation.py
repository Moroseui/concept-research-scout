import base64,copy,json,sqlite3
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import idea2_interpretation as f
from orchestrator import item6_idea2_followup as old
from test_item6_idea2_followup import db_at

@pytest.fixture
def lane(tmp_path,monkeypatch):
    scope=f.document()
    partial=f._path(tmp_path,scope["failed_prepare"]["lane"])
    partial.mkdir(parents=True,mode=0o700)
    (partial/"original.bin").write_bytes(b"preserved partial preparation")
    (partial/"original.bin").chmod(0o600)
    scope["failed_prepare"]["files"]={"original.bin":{"sha256":f.sha(b"preserved partial preparation"),"bytes":len(b"preserved partial preparation")}}
    parent=f._path(tmp_path,scope["prior"]["parent_lane"])
    new=f._path(tmp_path,scope["new_lane"])
    parent.mkdir(parents=True,mode=0o700);new.mkdir(parents=True,mode=0o700)
    previous=db_at(parent/"jobs.sqlite");local=db_at(new/"jobs.sqlite")
    previous.execute("CREATE TABLE manual_account(id INTEGER,payload TEXT,version INTEGER)")
    local.execute("CREATE TABLE manual_account(id INTEGER,payload TEXT,version INTEGER)")
    for db in (previous,local):
        for row in scope["prior"]["local"]["manual_calls"]:
            db.execute("INSERT INTO manual_calls VALUES(?,?,?,?,?)",tuple(row[k]for k in ("id","stage","attempt","status","receipt")))
        sr=scope["prior"]["local"]["manual_state"][0]
        db.execute("INSERT INTO manual_state VALUES(?,?)",(sr["id"],sr["payload"]))
        ar=scope["prior"]["local"]["manual_account"][0]
        db.execute("INSERT INTO manual_account VALUES(?,?,?)",(ar["id"],ar["payload"],ar["version"]))
    (parent/"lane.json").write_bytes(base64.b64decode(scope["prior"]["config_raw_base64"]))
    (parent/"lane.json").chmod(0o600)
    for path in (parent/"jobs.sqlite",new/"jobs.sqlite"):path.chmod(0o600)
    config={**scope["prior"]["config"],"root":str(Path(f.__file__).parents[1]),"source":"1"*40,
        "branch":f.BRANCH,"context":str(new/"context"),"workspace_root":str(new.with_name("lane-scientific-workspaces")),
        "engine_review":{},"engine_files":{},
        f.FIELD:{"schema":"idea2-interpretation/v1","scope_sha256":f.DOCUMENT_SHA}}
    (new/"lane.json").write_bytes(f.encoded(config));(new/"lane.json").chmod(0o600)
    value=json.loads(sr["payload"]);value["phase"]="result_interpretation_author"
    local.execute("UPDATE manual_state SET payload=?",(f.encoded(value).decode(),))
    global_db=db_at(tmp_path/"global/jobs.sqlite")
    for row in scope["prior"]["global"]["calls"]:
        global_db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",tuple(row[k]for k in (
            "id","kind","change_id","round","day","status","binding","receipt")))
    owner=scope["prior"]["global"]["owner"][0]
    global_db.execute("INSERT INTO autonomy_runs VALUES(?,?,?)",tuple(owner[k]for k in ("id","binding","status")))
    for event in scope["prior"]["global"]["preserved_events"]:
        global_db.execute("INSERT INTO events VALUES(?,?,?)",tuple(event[k]for k in ("id","job","payload")))
    # Ninety-six unrelated synthetic calls plus the original thirteen reproduce
    # the 109-row pre-allocation baseline; two current specification calls remain.
    for i in range(96):
        global_db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
            ("synthetic-baseline-"+str(i),"scientific","other",i,"2026-10-01","COMPLETE","{}","{}"))
    original=set(scope["allocation_original_call_ids"])
    rows=[dict(r)for r in global_db.execute("SELECT * FROM autonomy_calls")]
    initial=[r for r in rows if r["id"] in original or r["id"].startswith("synthetic-baseline-")]
    scope["allocation_initial_calls"]=[{"id":r["id"],"sha256":f.sha(f.encoded(r))}for r in initial]
    batch=SimpleNamespace(db=global_db,filesystem_root=tmp_path,folder=tmp_path/"global",
        status=lambda ident:{"status":"NOT_RESERVED"})
    store=SimpleNamespace(db=local,path=new/"jobs.sqlite",batch=batch)
    # Independent approval verification and actual output verification have
    # separate negative-control tests; this fixture exercises real frozen history.
    monkeypatch.setattr(f,"_approval",lambda *args:"2"*64)
    monkeypatch.setattr(f,"verified_by_store",lambda *args:{"status":"VALIDATED"})
    monkeypatch.setattr(f,"native_results",lambda *args:{"receipt":{"execution_receipt_sha256":"e"*64}})
    scope["uncertain_rows"]=[]
    monkeypatch.setattr(f,"document",lambda:copy.deepcopy(scope))
    monkeypatch.setattr(f,"_TERMINAL_QUALIFIER",lambda *args:pytest.fail("no uncertain fixture rows"))
    yield SimpleNamespace(store=store,scope=scope,config=config,parent=parent,new=new,
                          previous=previous,db=global_db)
    previous.close();local.close();global_db.close()

def test_real_scope_pins_only_interpretation_and_unchanged_money():
    s=f.document()
    assert s["admitted_stages"]==sorted(f.STAGES)
    assert len(s["allocation_initial_calls"])==109 and s["allocation_limit"]==4
    assert len(s["prior"]["local"]["manual_calls"])==15
    assert s["call_limit"]==30 and s["batch_limit"]==128
    assert s["item_cap_micro_usd"]==100000000
    assert not s["new_execution_authorized"] and s["new_provider_commitment_micro_usd"]==0

def test_activation_preserves_actual_prior_owner_acceptance_and_calls(lane):
    x=lane
    before={t:[dict(r)for r in x.db.execute("SELECT * FROM "+t)]for t in ("autonomy_runs","autonomy_calls")}
    result=f.activate(x.store,f.RUN)
    assert result["prior_calls"]==15 and result["new_allowance"]==0
    assert before=={t:[dict(r)for r in x.db.execute("SELECT * FROM "+t)]for t in before}
    assert dict(x.db.execute("SELECT * FROM events WHERE id=?",(f.RUN+":accepted",)).fetchone())==x.scope["prior"]["global"]["accepted"][0]
    assert old.validate(x.store,f.RUN)["schema"]=="idea2-interpretation-scope/v1"
    with pytest.raises(ValueError,match="ALREADY_ACTIVATED"):f.activate(x.store,f.RUN)

@pytest.mark.parametrize("change",["prior-account","prior-state","local-call","global-call","original-acceptance","owner"])
def test_changed_history_refuses_activation(lane,change):
    x=lane
    if change=="prior-account":x.previous.execute("UPDATE manual_account SET payload='{}'")
    elif change=="prior-state":x.previous.execute("UPDATE manual_state SET payload='{}'")
    elif change=="local-call":x.store.db.execute("UPDATE manual_calls SET receipt='{}'")
    elif change=="global-call":x.db.execute("UPDATE autonomy_calls SET receipt='{}'")
    elif change=="original-acceptance":x.db.execute("UPDATE events SET payload='{}'")
    else:x.db.execute("UPDATE autonomy_runs SET binding='{}'")
    with pytest.raises((ValueError,KeyError)):f.activate(x.store,f.RUN)
    assert not x.db.execute("SELECT 1 FROM events WHERE id=?",(f.EVENT,)).fetchone()

def test_exact_admission_uses_old_router_and_refuses_other_stages(lane):
    x=lane;f.activate(x.store,f.RUN)
    work=x.new.with_name("lane-scientific-workspaces")
    receipt={"workspace":str(work/"result_interpretation_author-3")}
    assert old.guard_admission(x.store.batch,f.RUN,"result_interpretation_author","1"*40,receipt)["batch_limit"]==128
    for stage,number,source in [("run_spec_author",6,"1"*40),("result_interpretation_author",1,"1"*40),
                              ("result_interpretation_author",7,"1"*40),("result_interpretation_author",3,"0"*40)]:
        with pytest.raises(ValueError):
            old.guard_admission(x.store.batch,f.RUN,stage,source,{"workspace":str(work/(stage+"-"+str(number)))})

def test_config_tamper_is_rechecked_at_admission(lane):
    x=lane;f.activate(x.store,f.RUN);x.config["author_timeout_seconds"]=9999
    (x.new/"lane.json").write_bytes(f.encoded(x.config))
    with pytest.raises(ValueError,match="CONFIG_CHANGED"):
        old.guard_admission(x.store.batch,f.RUN,"result_interpretation_author","1"*40,
            {"workspace":str(x.new.with_name("lane-scientific-workspaces")/"result_interpretation_author-3")})

@pytest.mark.parametrize("which",["daily","run","batch"])
def test_normal_caps_still_refuse_without_new_reservation(lane,monkeypatch,which):
    from datetime import datetime,timezone
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator import autonomy_limits as limits
    x=lane;f.activate(x.store,f.RUN)
    monkeypatch.setattr(limits,"global_limit",lambda *args:30)
    monkeypatch.setattr(limits,"daily_allowance",lambda *args:{"limit":50,"authority_sha256":"d"*64})
    day=datetime.now(timezone.utc).date().isoformat()
    if which=="run": count,kind,run,when=19,"scientific",f.RUN,"2026-10-01"
    elif which=="batch":count,kind,run,when=17,"scientific","other","2026-10-01"
    else:count,kind,run,when=50,"implementation_review","other",day
    for i in range(count):
        x.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
            ("extra-"+str(i),kind,run,100+i,when,"COMPLETE","{}","{}"))
    before=x.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]
    with pytest.raises(ValueError,match="ANALYSIS_ALLOCATION_EXHAUSTED" if which=="run" else "AUTONOMY_"+which.upper()+"_CALL_LIMIT"):
        BatchAccounts.reserve_scientific(x.store.batch,"new",f.RUN,"result_interpretation_author","1"*40,
            {"workspace":str(x.new.with_name("lane-scientific-workspaces")/"result_interpretation_author-3")})
    assert x.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==before
    assert not x.db.execute("SELECT 1 FROM jobs WHERE id='new'").fetchone()

def test_legacy_completion_stays_refused(lane):
    x=lane
    f.activate(x.store,f.RUN)
    with pytest.raises(ValueError,match="DISTINCT_ACCEPTANCE_REQUIRED"):
        old.refuse_legacy_completion(x.store.batch,f.RUN)

def test_new_execution_cannot_pass_preparation_hold(lane):
    x=lane;f.activate(x.store,f.RUN)
    driver=SimpleNamespace(store=x.store,config=x.config)
    for phase in ("COMMIT_SPEC","EXECUTE_CPU","WAIT_OUTPUTS","EMIT_PACKAGE"):
        with pytest.raises(ValueError,match="INTERPRETATION_ONLY"):
            old.preparation_hold(driver,{"phase":phase},None,None)
    with pytest.raises(ValueError,match="NO_EXECUTION"):
        old.preparation_hold(driver,{"phase":"result_interpretation_author"},"/arbitrary",None)

def test_live_or_unknown_uncertain_call_cannot_be_qualified(lane):
    x=lane;f.activate(x.store,f.RUN)
    x.db.execute("INSERT INTO autonomy_calls VALUES('live','scientific','other',1,'2026-10-12','RUNNING','{}',NULL)")
    with pytest.raises(ValueError,match="UNCLASSIFIED_OR_RUNNING"):
        old.terminal_ids(x.store.batch,x.scope)

@pytest.mark.parametrize("verdict,findings,source",[("REVISE",[],"1"*40),("REJECT",[],"1"*40),
        ("APPROVE",[{"finding":"unresolved"}],"1"*40),("APPROVE",[],"0"*40)])
def test_real_approval_gate_refuses_invalid_review(tmp_path,monkeypatch,verdict,findings,source):
    from orchestrator import autonomy_review
    folder=tmp_path/"review";folder.mkdir(mode=0o700)
    (folder/"packet-manifest.json").write_text("{}")
    (folder/"report.md").write_text(json.dumps({"findings":findings}))
    monkeypatch.setattr(autonomy_review,"verify_result",lambda *args:{"verdict":verdict,
        "source_sha":source,"change_id":f.CHANGE,"report_sha256":"2"*64})
    with pytest.raises(ValueError,match="INDEPENDENT_APPROVE"):
        f._approval({"source":"1"*40},{"review_directory":"/review"},tmp_path)

def test_native_unit_retains_client_protections_and_replaces_writable_state():
    from tools.idea2_interpretation_runtime import unit_bytes
    s=f.document();unit=unit_bytes(s).decode();oldunit=s["native"]["template_bytes"]
    for key in ("User=partho","Group=partho","Restart=no","UMask=0077","NoNewPrivileges=true","ProtectSystem=strict"):
        assert unit.splitlines().count(key)==1
    assert [x for x in unit.splitlines()if x.startswith("ExecStartPre=")]==[x for x in oldunit.splitlines()if x.startswith("ExecStartPre=")]
    rw=[x for x in unit.splitlines()if x.startswith("ReadWritePaths=")]
    assert len(rw)==1 and s["native"]["work"]in rw[0]
    assert str(Path(s["prior"]["parent_lane"]).parent)not in rw[0]

def test_normal_reservation_counts_next_call_and_preserves_originals(lane,monkeypatch):
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator import autonomy_limits as limits
    x=lane;f.activate(x.store,f.RUN)
    monkeypatch.setattr(limits,"global_limit",lambda *args:30)
    monkeypatch.setattr(limits,"daily_allowance",lambda *args:{"limit":50,"authority_sha256":"d"*64})
    before=[dict(r)for r in x.db.execute("SELECT * FROM autonomy_calls ORDER BY id")]
    out=BatchAccounts.reserve_scientific(x.store.batch,"new-counted-call",f.RUN,"result_interpretation_author","1"*40,
        {"workspace":str(x.new.with_name("lane-scientific-workspaces")/"result_interpretation_author-3")})
    assert out["accounting_units"]==1 and out["run_limit"]==30 and out["batch_limit"]==128
    assert x.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==112
    for row in before:assert dict(x.db.execute("SELECT * FROM autonomy_calls WHERE id=?",(row["id"],)).fetchone())==row
    assert json.loads(x.db.execute("SELECT binding FROM autonomy_calls WHERE id='new-counted-call'").fetchone()[0])["caps"]["daily_all_roles"]==50

def test_distinct_acceptance_preserves_original_and_is_idempotent(lane,monkeypatch):
    from orchestrator import experiment_acceptance
    x=lane;f.activate(x.store,f.RUN)
    (x.new/"interpretation.md").write_text("Synthetic reviewed interpretation.")
    (x.new/"decision.json").write_text('{"proposed_action_type":"stop"}')
    for name in ("interpretation.md","decision.json"):(x.new/name).chmod(0o600)
    value={"phase":"UPDATE_STATE","interpretation":str(x.new/"interpretation.md"),
           "next_decision":str(x.new/"decision.json"),"reviewed_results":{"sha256":"a"*64}}
    driver=SimpleNamespace(store=x.store,state=x.new,config=x.config,
        save=lambda v:None,status=lambda:{"phase":value["phase"]})
    monkeypatch.setattr(experiment_acceptance,"verify",lambda *args:{"scientifically_reviewed":True})
    original=dict(x.db.execute("SELECT * FROM events WHERE id=?",(f.RUN+":accepted",)).fetchone())
    assert f.finish(driver,value)["phase"]=="COMPLETE"
    assert f.finish(driver,value)["phase"]=="COMPLETE"
    assert dict(x.db.execute("SELECT * FROM events WHERE id=?",(f.RUN+":accepted",)).fetchone())==original
    assert x.db.execute("SELECT count(*) FROM events WHERE id=?",(f.ACCEPTED,)).fetchone()[0]==1
    assert x.db.execute("SELECT status FROM autonomy_runs").fetchone()[0]=="COMPLETE"
    assert f.validate(x.store,f.RUN)["run_id"]==f.RUN

def test_no_completion_with_unresolved_scientific_call(lane,monkeypatch):
    from orchestrator import experiment_acceptance
    x=lane;f.activate(x.store,f.RUN)
    (x.new/"interpretation.md").write_text("Synthetic reviewed interpretation.")
    (x.new/"decision.json").write_text('{"proposed_action_type":"stop"}')
    for name in ("interpretation.md","decision.json"):(x.new/name).chmod(0o600)
    x.db.execute("INSERT INTO autonomy_calls VALUES('uncertain-new','scientific',?,12,'2026-10-12','UNCERTAIN','{}',NULL)",(f.RUN,))
    value={"phase":"UPDATE_STATE","interpretation":str(x.new/"interpretation.md"),
           "next_decision":str(x.new/"decision.json"),"reviewed_results":{"sha256":"a"*64}}
    driver=SimpleNamespace(store=x.store,state=x.new,config=x.config,save=lambda v:None,status=lambda:{})
    monkeypatch.setattr(experiment_acceptance,"verify",lambda *args:{"scientifically_reviewed":True})
    with pytest.raises(ValueError,match="UNRESOLVED_CALL"):f.finish(driver,value)
    assert x.db.execute("SELECT status FROM autonomy_runs").fetchone()[0]=="ACTIVE"
    assert not x.db.execute("SELECT 1 FROM events WHERE id=?",(f.ACCEPTED,)).fetchone()

def test_absent_prior_timer_is_safe_but_enabled_timer_refuses(monkeypatch):
    from tools import idea2_interpretation_runtime as runtime
    timer={"enabled":False}
    def show(argv,**kwargs):
        if argv[2].endswith(".timer"):
            return "MainPID=0\nActiveState=inactive\nLoadState="+("loaded"if timer["enabled"]else"not-found")+"\n"
        return "MainPID=0\nActiveState=inactive\nLoadState=loaded\n"
    def enabled(argv,**kwargs):
        is_timer=argv[-1].endswith(".timer")
        return SimpleNamespace(returncode=0 if not is_timer or timer["enabled"]else 1,
            stdout=("enabled"if timer["enabled"]else"not-found")if is_timer else"disabled")
    monkeypatch.setattr(runtime.subprocess,"check_output",show)
    monkeypatch.setattr(runtime.subprocess,"run",enabled)
    runtime.held_prior()
    timer["enabled"]=True
    with pytest.raises(ValueError,match="PRIOR_UNIT_ENABLED"):runtime.held_prior()



def test_terminal_reader_uses_approved_frozen_history_not_live_successor_shape(monkeypatch):
    from tools import idea2_interpretation_runtime as runtime
    from orchestrator import colab_premodel_terminal as historical
    marker=object();seen=[]
    reader=lambda db,terminal,continuation:seen.append((db,terminal,continuation)) or ('preserved-row','original-state')
    monkeypatch.setattr(historical,'historical_read',reader)
    proof=SimpleNamespace(CALL='old-uncertain',frozen=lambda:'terminal-proof',
        qualify=lambda row,binding,read_local:read_local(binding))
    history=SimpleNamespace(frozen=lambda:'original-eight-proof',
        terminal_history=lambda *a:pytest.fail('must not revalidate later successor shape'))
    authority=SimpleNamespace(authority=lambda:{'source_sha':'e0394b8b8fd94a2d9feca3ffb88c917aed55936b',
        'report_sha256':'6d5689352510f3dda16edf084da1901c8121deec88af11a0b204685fe5e0d34d'})
    sender=SimpleNamespace(authority=lambda:None)
    def load(name,path):
        return authority if 'authority' in name else history if 'history' in name else proof if 'colab_terminal' in name else sender
    monkeypatch.setattr(runtime,'load',load);monkeypatch.setattr(f,'_TERMINAL_QUALIFIER',None)
    runtime.connect_qualifier()
    assert f._TERMINAL_QUALIFIER(SimpleNamespace(db=marker),{'id':'old-uncertain'})==('preserved-row','original-state')
    assert seen==[(marker,'terminal-proof','original-eight-proof')]


def test_driver_round_and_role_limit_admit_only_validated_interpretation(lane,monkeypatch):
    from orchestrator.manual_driver import Driver
    from orchestrator.manual_recovery import role_limit
    x=lane;f.activate(x.store,f.RUN)
    driver=SimpleNamespace(store=x.store,config=x.config)
    # Context transport validation is covered separately and by the real native probe.
    # Keep the real attempt inspection/offset/history code under this routing test.
    from orchestrator import author_revision_accounting as accounting
    monkeypatch.setattr(accounting,'context',lambda store,run:driver)
    for stage in sorted(f.STAGES):
        value={'phase':stage,'rounds':x.scope['offsets']}
        assert Driver.model_round_number(driver,value)==3
        assert role_limit(x.store,f.RUN,stage)>=3
    for stage in ['run_spec_author','run_spec_review','prepare_execution']:
        with pytest.raises(ValueError,match='PREPARATION_STAGE_ONLY'):
            Driver.model_round_number(driver,{'phase':stage,'rounds':{}})
        with pytest.raises(ValueError,match='PREPARATION_STAGE_ONLY'):
            role_limit(x.store,f.RUN,stage)

def test_driver_stage_routing_requires_active_verified_interpretation(lane):
    from orchestrator.manual_driver import Driver
    from orchestrator.manual_recovery import role_limit
    x=lane;driver=SimpleNamespace(store=x.store,config=x.config)
    for function in [
        lambda:Driver.model_round_number(driver,{'phase':'result_interpretation_author','rounds':{}}),
        lambda:role_limit(x.store,f.RUN,'result_interpretation_author')]:
        with pytest.raises(ValueError,match='ACTIVATION'):function()


def test_legacy_preparation_stage_set_is_not_broadened(lane):
    from orchestrator import preparation_followup
    x=lane
    config=dict(x.config);config.pop(f.FIELD)
    (x.new/'lane.json').write_bytes(f.encoded(config))
    assert preparation_followup.stages(x.store,f.RUN)==old.STAGES
    assert not(f.STAGES & preparation_followup.stages(x.store,f.RUN))

def test_actual_result_missing_cannot_activate_or_create_grant(lane,monkeypatch):
    x=lane
    def missing(*args):raise FileNotFoundError("no completed CPU result")
    monkeypatch.setattr(f,"native_results",missing)
    with pytest.raises(FileNotFoundError):f.activate(x.store,f.RUN)
    assert not x.db.execute("SELECT 1 FROM events WHERE id=?",(f.EVENT,)).fetchone()
    assert x.db.execute("SELECT status FROM autonomy_runs").fetchone()[0]=="ACTIVE"

def test_four_question_calls_including_preparation_refuse_fifth(lane):
    x=lane;f.activate(x.store,f.RUN)
    for i in range(2):
        x.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
            ("interpretation-counted-"+str(i),"scientific",f.RUN,16+i,"2026-10-12","COMPLETE","{}","{}"))
    before=x.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]
    receipt={"workspace":str(x.new.with_name("lane-scientific-workspaces")/"result_interpretation_author-3")}
    with pytest.raises(ValueError,match="ANALYSIS_ALLOCATION_EXHAUSTED"):
        f.guard_admission(x.store.batch,f.RUN,"result_interpretation_author","1"*40,receipt)
    with pytest.raises(ValueError,match="ANALYSIS_ALLOCATION_EXHAUSTED"):
        f.batch_allowance(x.store.batch,x.scope)
    assert x.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==before

def test_prior_smoothing_specification_allocation_is_not_reissued(lane):
    x=lane;f.activate(x.store,f.RUN)
    out=f.batch_allowance(x.store.batch,x.scope)
    assert out["analysis_allocation_used"]==2 and out["analysis_allocation_limit"]==4
    assert out["limit"]==128
    x.db.execute("UPDATE autonomy_calls SET receipt='changed' WHERE id='synthetic-baseline-0'")
    with pytest.raises(ValueError,match="ALLOCATION_HISTORY_CHANGED"):
        f.batch_allowance(x.store.batch,x.scope)

def test_completed_result_binds_exact_original_cpu_approval(tmp_path,monkeypatch):
    from orchestrator import autonomy_review
    scope=f.document();seen=[]
    work=f._path(tmp_path,scope["result_work"]);work.mkdir(parents=True,mode=0o700)
    (work/"receipt.json").write_bytes(b"original");(work/"receipt.json").chmod(0o600)
    scope["result_files"]={"receipt.json":f.sha(b"original")}
    expected={"verdict":"APPROVE","change_id":scope["cpu_change_id"],"source_sha":scope["cpu_source"],"report_sha256":scope["cpu_review_sha256"]}
    monkeypatch.setattr(autonomy_review,"verify_result",lambda *a:expected)
    monkeypatch.setattr(f.results,"verify",lambda work,source,review:seen.append((work,source,review))or{"verified":True})
    assert f.native_results(scope,tmp_path)=={"verified":True}
    assert seen==[(work,scope["cpu_source"],scope["cpu_review_sha256"])]
    for key,value in [("verdict","REVISE"),("source_sha","1"*40),("report_sha256","2"*64),("change_id","other")]:
        wrong={**expected,key:value}
        monkeypatch.setattr(autonomy_review,"verify_result",lambda *a:wrong)
        with pytest.raises(ValueError,match="CPU_APPROVAL"):f.native_results(scope,tmp_path)
    monkeypatch.setattr(autonomy_review,"verify_result",lambda *a:expected)
    (work/"receipt.json").write_bytes(b"changed")
    with pytest.raises(ValueError,match="NATIVE_RESULT_CHANGED"):f.native_results(scope,tmp_path)

def test_changed_execution_receipt_cannot_reuse_interpretation_grant(lane,monkeypatch):
    x=lane;f.activate(x.store,f.RUN)
    monkeypatch.setattr(f,"native_results",lambda *a:{"receipt":{"execution_receipt_sha256":"f"*64}})
    with pytest.raises(ValueError,match="ACTIVATION_REQUIRED"):f.validate(x.store,f.RUN)

def test_native_cpu_authority_must_be_same_bundle(monkeypatch):
    from tools import idea2_interpretation_runtime as rt
    own={"source_sha":"a"*40,"report_sha256":"b"*64}
    monkeypatch.setattr(rt,"authority",lambda:own)
    cpu=SimpleNamespace(UNIT="synthetic.service",authority=lambda:({"source_sha":"c"*40,"report_sha256":"b"*64},{}))
    monkeypatch.setattr(rt,"load",lambda *a:cpu)
    with pytest.raises(ValueError,match="CPU_APPROVAL"):rt.cpu_authority()

def test_partial_failed_preparation_cannot_change_or_be_replaced(lane):
    x=lane;folder=f._path(x.store.batch.filesystem_root,x.scope["failed_prepare"]["lane"])
    f.failed_preparation(x.scope,x.store.batch.filesystem_root)
    (folder/"original.bin").write_bytes(b"changed")
    with pytest.raises(ValueError,match="PARTIAL_PREPARATION_CHANGED"):f.activate(x.store,f.RUN)
    assert not x.db.execute("SELECT 1 FROM events WHERE id=?",(f.EVENT,)).fetchone()

def test_collection_keeps_original_namespace_and_immutable_conflict_check(tmp_path,monkeypatch):
    from orchestrator import experiment_collection
    from orchestrator.manual_executor import digest
    state=tmp_path/"state";state.mkdir(mode=0o700)
    context=state/"context";context.mkdir(mode=0o700)
    driver=SimpleNamespace(state=state,context=context,config={"run_id":f.RUN},store=None)
    prefix="current/runs/"+digest(f.RUN.encode())+"/results/"
    original=b'{"prior": true}'
    oldpath=context/(prefix+"idea2/integrity.json");oldpath.parent.mkdir(parents=True,mode=0o700)
    oldpath.write_bytes(original);oldpath.chmod(0o600)
    oldrow={"id":"diagnostics-result-integrity.json","type":"result_tables","version":1,"path":prefix+"idea2/integrity.json","sha256":digest(original)}
    value={"artifacts":[oldrow]}
    # Prove the original refusal still applies; recovery uses a new namespace.
    with pytest.raises(ValueError,match="IMMUTABLE_ARTIFACT_CONFLICT"):
        experiment_collection.artifact(driver,value,"result_tables",oldrow["id"],"idea2/integrity.json",b'{"new": true}')
    outputs={n:(b"Synthetic limitations."if n.endswith(".md")else b'{"new": true}')for n in f.results.OUTPUTS}
    native={"files":outputs,"validation":{"status":"VALIDATED"},"receipt":{"cpu_source":"a"*40,"implementation_review_sha256":"b"*64}}
    monkeypatch.setattr(f,"native_results",lambda *a:native)
    monkeypatch.setattr(f,"verified_by_store",lambda *a:None)
    f.collect(driver,value,{},tmp_path)
    assert oldpath.read_bytes()==original
    assert value["preserved_prior_result_artifacts"]==[oldrow]
    for name,raw in outputs.items():
        assert (context/(prefix+"smoothing/"+name)).read_bytes()==raw
    assert all("/idea2/"not in r["path"]for r in value["artifacts"])
    assert (context/(prefix+"smoothing-execution-receipt.json")).is_file()

def test_native_reader_reuses_completed_cpu_without_new_execution(monkeypatch):
    from tools import idea2_interpretation_runtime as rt
    scope=f.document()
    cpu=SimpleNamespace(UNIT="synthetic.service",authority=lambda:({"source_sha":scope["cpu_source"],"report_sha256":scope["cpu_review_sha256"]},{}))
    monkeypatch.setattr(rt,"authority",lambda:{"source_sha":"f"*40,"report_sha256":"e"*64})
    monkeypatch.setattr(rt,"load",lambda *a:cpu)
    monkeypatch.setattr(rt.subprocess,"check_output",lambda *a,**k:"MainPID=0\nActiveState=inactive\nExecMainStatus=0\n")
    assert rt.cpu_authority()["source_sha"]==scope["cpu_source"]
