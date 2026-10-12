"""Exact terminal proof, counted reconciliation, then real full admission."""
import copy,json,importlib.util
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import multiwin_local_recovery as q, multiwin_local_allowance as bridge
from orchestrator.manual_executor import Accounts
from test_multiwin_local_allowance import live,reserve
ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture
def failure(live,monkeypatch):
    x=live
    x.batch.db.execute("UPDATE autonomy_calls SET status='RUNNING',receipt=NULL WHERE id=?",(q.CALL,))
    state={"phase":"BLOCKED","reason":"ValueError: LIMITER_STATE_INCONSISTENT","pending":None,
           "rounds":{"run_spec_author":10,"run_spec_review":9},"interventions":[]}
    x.store.db.execute("INSERT INTO manual_state VALUES(1,?)",(json.dumps(state),))
    rows=lambda db,table:[dict(r)for r in db.execute("SELECT * FROM "+table+" ORDER BY rowid")]
    row=lambda db,table:dict(db.execute("SELECT * FROM "+table+" WHERE id=1").fetchone())
    local=rows(x.store.db,"manual_calls");glob=rows(x.batch.db,"autonomy_calls")
    binding={"stage":"run_spec_author","source":x.config["source"],
             "input":{"workspace":str(Path(x.config["workspace_root"])/"run_spec_author-11")}}
    x.batch.db.execute("UPDATE autonomy_calls SET binding=?WHERE id=?",(json.dumps(binding),q.CALL))
    glob=rows(x.batch.db,"autonomy_calls")
    unit={"MainPID":"0","ActiveState":"failed","SubState":"failed","ControlGroup":"",
          "ExecMainStatus":"1","InvocationID":"synthetic-positive-terminal",
          "ExecMainStartTimestampMonotonic":"100","ExecMainExitTimestampMonotonic":"200"}
    owner=dict(x.batch.db.execute("SELECT * FROM autonomy_runs WHERE id=?",(q.RUN,)).fetchone())
    b={"config":x.config,"local_calls_pins":{r["id"]:q.sha(q.canonical(r))for r in local},
       "global_calls_pins":{r["id"]:q.sha(q.canonical(r))for r in glob},
       "local_failed":local[-1],"global_failed":glob[-1],
       "state_row":row(x.store.db,"manual_state"),"account_row":row(x.store.db,"manual_account"),
       "owner":owner,"unit":unit,"workspace_files":{"prompt.md":{"bytes":5,"sha256":"a"*64}},
       "workspace_dirs":["context"]}
    driver=NS(store=x.store,state=Path(x.store.path).parent,config=x.config,
              current=lambda:json.loads(x.store.db.execute("SELECT payload FROM manual_state WHERE id=1").fetchone()[0]))
    def args():
        return [b,dict(x.batch.db.execute("SELECT * FROM autonomy_calls WHERE id=?",(q.CALL,)).fetchone()),
                rows(x.store.db,"manual_calls"),rows(x.batch.db,"autonomy_calls"),
                row(x.store.db,"manual_state"),row(x.store.db,"manual_account"),owner,
                x.config,copy.deepcopy(unit),copy.deepcopy(b["workspace_files"]),list(b["workspace_dirs"])]
    def qualify(db,scope,prior):
        assert db is x.batch.db and scope is b
        return q.validate(*args())
    monkeypatch.setattr(q,"qualify",qualify)
    return NS(x=x,b=b,driver=driver,args=args,approval={"source_sha":"d"*40,"report_sha256":"e"*64},
              old_local=local,old_global=glob)
def test_exact_positive_terminal_proof(failure):
    f=failure;v=q.validate(*f.args())
    assert v["model_client_launched"]is False and v["scientific_successor"]is False
@pytest.mark.parametrize("bad",["global_row","local","global_history","state","account","owner","config",
                                "pid","status","invocation","clock","files","dirs","console"])
def test_any_drift_or_possible_client_launch_refused(failure,bad):
    f=failure;a=[copy.deepcopy(v)for v in f.args()]
    if bad=="global_row":a[1]["receipt"]="unexplained"
    elif bad=="local":a[2][0]["receipt"]="changed"
    elif bad=="global_history":a[3][0]["receipt"]="changed"
    elif bad=="state":a[4]["payload"]="{}"
    elif bad=="account":a[5]["payload"]="reset"
    elif bad=="owner":a[6]["status"]="changed"
    elif bad=="config":a[7]["source"]="f"*40
    elif bad=="pid":a[8]["MainPID"]="42"
    elif bad=="status":a[8]["ActiveState"]="active"
    elif bad=="invocation":a[8]["InvocationID"]=""
    elif bad=="clock":a[8]["ExecMainExitTimestampMonotonic"]="50"
    elif bad=="files":a[9]["prompt.md"]["sha256"]="b"*64
    elif bad=="dirs":a[10].append(".git")
    else:a[9]["console.log"]={"bytes":3,"sha256":"c"*64}
    with pytest.raises(ValueError,match="MULTIWIN_PREMODEL_"):q.validate(*a)
def test_reconcile_preserves_charge_and_is_idempotent(failure):
    f=failure;x=f.x
    assert q.reconcile(x.batch,f.b,None)["accounting_units_preserved"]==1
    assert x.batch.db.execute("SELECT count(*)FROM autonomy_calls").fetchone()[0]==21
    assert [dict(r)for r in x.store.db.execute("SELECT * FROM manual_calls ORDER BY rowid")]==f.old_local
    assert dict(x.store.db.execute("SELECT *FROM manual_account WHERE id=1").fetchone())==f.b["account_row"]
    got=dict(x.batch.db.execute("SELECT *FROM autonomy_calls WHERE id=?",(q.CALL,)).fetchone())
    assert got=={**f.b["global_failed"],"status":"FAILED","receipt":json.dumps(q.terminal_receipt(f.b),sort_keys=True)}
    assert q.reconcile(x.batch,f.b,None)["status"]=="ALREADY_RECONCILED_NO_NEW_CALL"
def test_recovery_then_actual_next_reservation_preserves_all_twenty_one(failure):
    f=failure;x=f.x
    result=q.recover(f.driver,f.b,f.approval,None)
    assert result["preserved_local_calls"]==21 and result["maximum_remaining_calls"]==3
    assert f.driver.current()["rounds"]["run_spec_author"]==11
    assert Accounts(x.store).read()[1]==x.account
    assert q.recover(f.driver,f.b,f.approval,None)["status"]=="ALREADY_RECOVERED_NO_NEW_CALL"
    restore=bridge.bind(x.config,q.PIN,f.approval["report_sha256"],lambda store:q.guard(f.driver,f.b,f.approval))
    try:
        ident,n,receipt=reserve(x)
        assert n==12 and receipt["accounting"]["status"]=="ADMITTED"
        assert x.store.db.execute("SELECT count(*)FROM manual_calls").fetchone()[0]==22
        assert x.batch.db.execute("SELECT count(*)FROM autonomy_calls").fetchone()[0]==22
        q.guard(f.driver,f.b,f.approval)
        assert Accounts(x.store).read()[1]["resets"]==[]
    finally:restore()
def test_incomplete_recovery_is_not_replayed(failure):
    f=failure
    (f.driver.state/q.EVENT).mkdir(mode=0o700)
    with pytest.raises(ValueError,match="INCOMPLETE_RECOVERY_RECONCILE"):
        q.recover(f.driver,f.b,f.approval,None)
    assert f.x.batch.db.execute("SELECT status FROM autonomy_calls WHERE id=?",(q.CALL,)).fetchone()[0]=="RUNNING"
def test_halt_prevents_recovery(failure):
    f=failure;(f.driver.state/"HALT").write_text("hold")
    with pytest.raises(ValueError,match="HALT"):q.recover(f.driver,f.b,f.approval,None)
    assert not(f.driver.state/q.EVENT).exists()
def test_runtime_unit_changes_only_entrypoint():
    p=ROOT/"tools/multiwin_local_runtime.py"
    spec=importlib.util.spec_from_file_location("_local_runtime_unit_test",p)
    rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
    old="/usr/bin/python3 -s -B "+str(rt.PRIOR/"tools/multiwin_tonight_runtime.py")+" run"
    raw=("\n".join(["[Service]","User=partho","Group=partho","ProtectSystem=strict",
                    "NoNewPrivileges=yes","PrivateTmp=yes","Restart=no","ExecStart="+old,""])).encode()
    prior=NS(ENTRY="tools/multiwin_tonight_runtime.py",authority=lambda:({},object(),None),unit_bytes=lambda parent:raw)
    new="/usr/bin/python3 -s -B "+str(rt.ROOT/rt.ENTRY)+" run"
    assert rt.unit_bytes(prior)==raw.replace(old.encode(),new.encode())
def test_scope_keeps_existing_limits_and_three_remaining_slots():
    raw=(ROOT/q.DOCUMENT).read_bytes()
    assert q.sha(raw)==q.PIN
    b=json.loads(raw)
    assert b["run_limit"]==24 and b["batch_limit"]==128 and b["max_remaining_calls"]==3
    assert b["original_calls"]==20 and b["failed_extra_reservation"]==1
    assert b["execution_authorized"]is False
    assert set(map(tuple,b["allowed_next"]))==bridge.ALLOWED
