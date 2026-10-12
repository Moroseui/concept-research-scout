"""Actual ManualExecutor -> BatchAccounts -> CAS admission; no model clients."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import multiwin_local_allowance as repair
from orchestrator import autonomy_limits as limits, private_records as pr
from orchestrator import dispatch_limiter, manual_recovery, preparation_followup
from orchestrator import autonomy_accounting, item4_scoped_calls
from orchestrator.manual_executor import ManualExecutor, Accounts, digest
from orchestrator.autonomy_accounting import BatchAccounts
from test_temporary_daily_cap import Clock


@pytest.fixture
def live(tmp_path, monkeypatch):
    lane = tmp_path / "lane"
    pr.mkdir(lane)
    policy = {"status":"RATIFIED", "operator_approval":"synthetic",
              "state_write_permission":"OPERATOR_AUTHORIZED", "n":3,
              "window":"UTC_CALENDAR_DAY", "state_ref":dispatch_limiter.REF,
              "manual_semantics":"OPERATOR_SERVER_SPRINT10_MAX_SIX"}
    config = {"run_id":repair.RUN, "source":"a"*40, "branch":"astra/manual-synthetic",
              "policy":policy, "workspace_root":str(tmp_path/"workspaces"),
              "item_number":4, "backend":"modal"}
    pr.atomic(lane/"lane.json",config)
    batch = BatchAccounts(tmp_path/"batch",filesystem_root=tmp_path)
    batch.register_run(repair.RUN,{"state":"/lane"})
    store = ManualExecutor(lane/"jobs.sqlite",batch=batch)
    store.initialize_allowance(policy)
    stages = ([("run_spec_author",n)for n in range(1,11)]
              +[("run_spec_review",n)for n in range(1,10)]
              +[("result_interpretation_author",1),("run_spec_author",11)])
    for i,(stage,n)in enumerate(stages):
        ident=digest((repair.RUN+":"+stage+":"+str(n)).encode())
        local_status="BLOCKED_BEFORE_MODEL" if n==11 and stage=="run_spec_author" else "COMPLETE"
        store.db.execute("INSERT INTO manual_calls VALUES(?,?,?,?,?)",
                         (ident,stage,n,local_status,'{"preserved":true}'))
        batch.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                         (ident,"scientific",repair.RUN,i+1,"2026-10-12",
                          "FAILED" if local_status=="BLOCKED_BEFORE_MODEL" else "COMPLETE","{}",'{"preserved":true}'))
    version,account=Accounts(store).read()
    account.update(count=11,sequence=19,day="2026-10-12",halted=False)
    for i in range(11):
        key="manual:"+digest(("old-event-"+str(i)).encode())+":1"
        account["events"][key]={"source":config["source"],"branch":config["branch"],
            "day":"2026-10-12","count":i+1,"notification":None,"halted":False}
    assert Accounts(store).cas(version,account)
    originals=[dict(r)for r in store.db.execute("SELECT * FROM manual_calls ORDER BY rowid")]
    global_originals=[dict(r)for r in batch.db.execute("SELECT * FROM autonomy_calls ORDER BY rowid")]
    def verify(store_):
        assert store_ is store
        assert [dict(r)for r in store.db.execute("SELECT * FROM manual_calls ORDER BY rowid LIMIT 21")]==originals
        assert [dict(r)for r in batch.db.execute("SELECT * FROM autonomy_calls ORDER BY rowid LIMIT 21")]==global_originals
    old_local,old_global,old_role=limits.local_limit,limits.global_limit,manual_recovery.role_limit
    monkeypatch.setattr(limits,"local_limit",lambda s,r,p:24 if r==repair.RUN else old_local(s,r,p))
    monkeypatch.setattr(limits,"global_limit",lambda b,r:24 if r==repair.RUN else old_global(b,r))
    monkeypatch.setattr(limits,"scientific_batch_allowance",lambda *args:{"limit":128})
    monkeypatch.setattr(limits,"cap_authority",lambda c:repair.AUTHORITY if c==24 else limits.AUTHORITY)
    monkeypatch.setattr(manual_recovery,"role_limit",lambda s,r,stage:(12 if stage.endswith("author") else 11) if r==repair.RUN else old_role(s,r,stage))
    monkeypatch.setattr(preparation_followup,"guard_admission",lambda *args:None)
    monkeypatch.setattr("orchestrator.connectivity.require",lambda *args,**kw:{"synthetic":True})
    Clock.day="2026-10-12"
    monkeypatch.setattr(autonomy_accounting,"datetime",Clock)
    monkeypatch.setattr(dispatch_limiter,"datetime",Clock)
    x=NS(store=store,batch=batch,config=config,policy=policy,verify=verify,
         originals=originals,global_originals=global_originals,account=copy.deepcopy(account))
    yield x
    store.db.close();batch.db.close()


def reserve(x,stage="run_spec_author",source=None,workspace=None):
    n=x.store.db.execute("SELECT count(*) FROM manual_calls WHERE stage=?",(stage,)).fetchone()[0]+1
    receipt={"workspace":workspace or str(Path(x.config["workspace_root"])/(stage+"-"+str(n)))}
    return x.store.reserve_call(repair.RUN,stage,source or x.config["source"],
                                x.config["branch"],x.policy,receipt)


def test_unpatched_full_path_reproduces_actual_partial_reservation(live):
    x=live
    assert limits.local_limit(x.store,repair.RUN,x.policy)==24
    assert limits.allowance(x.store,repair.RUN,x.policy) is None
    with pytest.raises(ValueError,match="LIMITER_STATE_INCONSISTENT"):
        reserve(x)
    assert x.store.db.execute("SELECT status FROM manual_calls ORDER BY rowid DESC LIMIT 1").fetchone()[0]=="BLOCKED_BEFORE_MODEL"
    assert x.batch.db.execute("SELECT status FROM autonomy_calls ORDER BY rowid DESC LIMIT 1").fetchone()[0]=="RUNNING"
    assert Accounts(x.store).read()[1]==x.account
    x.verify(x.store)


def test_full_reservation_counts_both_ledgers_and_preserves_all_history(live):
    x=live
    restore=repair.bind(x.config,"b"*64,"c"*64,x.verify)
    try:
        ident,n,receipt=reserve(x)
        assert n==12
        assert receipt["batch_accounting"]["run_limit"]==24
        assert receipt["batch_accounting"]["batch_limit"]==128
        assert receipt["accounting"]["status"]=="ADMITTED"
        assert receipt["accounting"]["count"]==12
        assert receipt["accounting"]["limit_amendment"]=={
            "authority_sha256":repair.AUTHORITY,"run_limit":24,"scoped_run_id":repair.RUN,
            "call_id":ident,"review_sha256":"c"*64,"checkpoint_sha256":"b"*64}
        account=Accounts(x.store).read()[1]
        assert account["sequence"]==20 and account["resets"]==[]
        assert all(account["events"][k]==v for k,v in x.account["events"].items())
        assert account["policy_sha256"]==x.account["policy_sha256"]
        assert x.store.db.execute("SELECT count(*)FROM manual_calls").fetchone()[0]==22
        assert x.batch.db.execute("SELECT count(*)FROM autonomy_calls").fetchone()[0]==22
        x.verify(x.store)
    finally:restore()


@pytest.mark.parametrize("which",["local_run","global_run","batch","day","uncertain"])
def test_whole_reservation_retains_existing_cap_and_uncertainty_refusals(live,which):
    x=live
    if which=="local_run":
        for i in range(3):
            x.store.db.execute("INSERT INTO manual_calls VALUES(?,?,?,?,?)",
                             ("extra-local-"+str(i),"result_interpretation_review",i+1,"COMPLETE","{}"))
        expected="STEP_D_MODEL_CALL_LIMIT"
    elif which=="global_run":
        for i in range(3):
            x.batch.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                             ("extra-global-"+str(i),"scientific",repair.RUN,22+i,"2020-01-01","COMPLETE","{}","{}"))
        expected="AUTONOMY_RUN_CALL_LIMIT"
    elif which=="batch":
        for i in range(107):
            x.batch.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                             ("extra-batch-"+str(i),"scientific","other",i,"2020-01-01","COMPLETE","{}","{}"))
        expected="AUTONOMY_BATCH_CALL_LIMIT"
    elif which=="day":
        for i in range(79):
            x.batch.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                             ("extra-day-"+str(i),"implementation_review","other",i,"2026-10-12","COMPLETE","{}","{}"))
        expected="AUTONOMY_DAILY_CALL_LIMIT"
    else:
        x.batch.db.execute("INSERT INTO autonomy_calls VALUES('uncertain','scientific','other',1,'2020-01-01','UNCERTAIN','{}','{}')")
        expected="UNCERTAIN"
    before=[tuple(r)for r in x.store.db.execute("SELECT * FROM manual_calls")]
    glob=[tuple(r)for r in x.batch.db.execute("SELECT * FROM autonomy_calls")]
    restore=repair.bind(x.config,"b"*64,"c"*64,x.verify)
    try:
        with pytest.raises(ValueError,match=expected):reserve(x)
        assert [tuple(r)for r in x.store.db.execute("SELECT * FROM manual_calls")]==before
        assert [tuple(r)for r in x.batch.db.execute("SELECT * FROM autonomy_calls")]==glob
        assert Accounts(x.store).read()[1]==x.account
    finally:restore()


@pytest.mark.parametrize("bad",["source","workspace","stage","config"])
def test_wrong_binding_refused_before_global_reservation(live,bad):
    x=live
    restore=repair.bind(x.config,"b"*64,"c"*64,x.verify)
    try:
        if bad=="config":pr.atomic(Path(x.store.path).parent/"lane.json",{**x.config,"extra":True})
        with pytest.raises(ValueError,match="MULTIWIN_LOCAL_ALLOWANCE_"):
            reserve(x,source="d"*40 if bad=="source" else None,
                    workspace="/wrong" if bad=="workspace" else None,
                    stage="result_interpretation_author" if bad=="stage" else "run_spec_author")
        assert x.batch.db.execute("SELECT count(*)FROM autonomy_calls").fetchone()[0]==21
        assert Accounts(x.store).read()[1]==x.account
    finally:restore()


def test_cannot_invoke_validator_without_the_real_reservation(live):
    x=live;restore=repair.bind(x.config,"b"*64,"c"*64,x.verify)
    try:
        with pytest.raises(ValueError,match="ACCOUNT_CONNECTION"):
            item4_scoped_calls.validate_allowance(Accounts(x.store),{},
                                                  {"scoped_run_id":repair.RUN,"run_limit":24})
        with pytest.raises(ValueError,match="LOCAL_OWNER"):
            limits.allowance(x.store,repair.RUN,x.policy)
    finally:restore()


def test_ordinary_owner_and_scoped_validator_remain_delegated(live,monkeypatch):
    x=live;seen=[]
    monkeypatch.setattr(limits,"allowance",lambda *args:{"unchanged":True})
    monkeypatch.setattr(item4_scoped_calls,"validate_allowance",lambda *args:seen.append(args))
    restore=repair.bind(x.config,"b"*64,"c"*64,x.verify)
    try:
        assert limits.allowance(x.store,"other",{})=={"unchanged":True}
        item4_scoped_calls.validate_allowance("account","event",{"scoped_run_id":"other"})
        assert seen==[("account","event",{"scoped_run_id":"other"})]
    finally:restore()


def test_latched_local_halt_is_never_cleared(live):
    x=live;version,state=Accounts(x.store).read();state["halted"]=True
    assert Accounts(x.store).cas(version,state)
    restore=repair.bind(x.config,"b"*64,"c"*64,x.verify)
    try:
        with pytest.raises(ValueError,match="LOCAL_ALLOWANCE_HALTED"):reserve(x)
        assert Accounts(x.store).read()[1]==state
        assert x.store.db.execute("SELECT status FROM manual_calls ORDER BY rowid DESC LIMIT 1").fetchone()[0]=="BLOCKED_BEFORE_MODEL"
    finally:restore()
