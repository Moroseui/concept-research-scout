"""Actual SQLite recovery and admission; no patient data or model clients."""
import copy,json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from test_idea2_interpretation import lane
from orchestrator import idea2_interpretation as f,idea2_serialization_recovery as r
from orchestrator import private_records as pr
@pytest.fixture
def failed(lane):
    x=lane;f.activate(x.store,f.RUN)
    state={"phase":"BLOCKED","reason":r.REASON,"blocked_stage":r.STAGE,"blocker_categories":[],
      "rounds":copy.deepcopy(x.scope["offsets"]),"interventions":[],"artifacts":[{"id":"saved","sha256":"a"*64}]}
    x.store.db.execute("UPDATE manual_state SET payload=?WHERE id=1",(json.dumps(state),))
    work=Path(x.config["workspace_root"])/(r.STAGE+"-3");pr.mkdir(work.parent);pr.mkdir(work)
    pr.write_text(work/"input.json",'{"synthetic":true}')
    d=NS(store=x.store,state=x.new,config=x.config,
      current=lambda:json.loads(x.store.db.execute("SELECT payload FROM manual_state WHERE id=1").fetchone()[0]))
    b={"config":copy.deepcopy(x.config),"config_sha256":r.sha((x.new/"lane.json").read_bytes()),
       "lane":str(x.new),"workspace":str(work),"workspace_files":{"input.json":{"sha256":r.sha((work/"input.json").read_bytes()),"bytes":18}},
       "next_call_id":r.sha((r.RUN+":"+r.STAGE+":3").encode()),
       "local_calls":[dict(z)for z in x.store.db.execute("SELECT *FROM manual_calls ORDER BY id")],
       "global_calls":[dict(z)for z in x.db.execute("SELECT *FROM autonomy_calls WHERE change_id=?ORDER BY id",(r.RUN,))],
       "state_row":dict(x.store.db.execute("SELECT *FROM manual_state WHERE id=1").fetchone()),
       "account_row":dict(x.store.db.execute("SELECT *FROM manual_account WHERE id=1").fetchone()),
       "owner":dict(x.db.execute("SELECT *FROM autonomy_runs WHERE id=?",(r.RUN,)).fetchone()),
       "grant":dict(x.db.execute("SELECT *FROM events WHERE id=?",(f.EVENT,)).fetchone())}
    return NS(x=x,d=d,b=b,work=work,approval="a"*64)
def test_recovery_preserves_rows_account_scope_and_original_workspace(failed):
    q=failed;before=q.work.read_bytes()if q.work.is_file()else(q.work/"input.json").read_bytes()
    result=r.recover(q.d,q.b,q.approval)
    assert result=={"status":"READY_SAME_UNRESERVED_AUTHOR3","model_calls":0,"prior_calls":15,"new_allowance":0}
    assert q.d.current()["rounds"]==json.loads(q.b["state_row"]["payload"])["rounds"]
    assert q.d.current()["artifacts"]==json.loads(q.b["state_row"]["payload"])["artifacts"]
    assert not q.work.exists()
    assert(q.d.state/r.EVENT/"original-workspace/input.json").read_bytes()==before
    assert dict(q.x.store.db.execute("SELECT *FROM manual_account WHERE id=1").fetchone())==q.b["account_row"]
    r.originals(q.d,q.b)
    with pytest.raises(ValueError):r.recover(q.d,q.b,q.approval)
@pytest.mark.parametrize("change",["config","local","global","owner","grant","state","account","file","extra","live","reserved","halt"])
def test_drift_refuses_without_state_change(failed,change):
    q=failed;x=q.x
    if change=="config":pr.atomic(q.d.state/"lane.json",{**x.config,"changed":True})
    elif change=="local":x.store.db.execute("UPDATE manual_calls SET receipt='changed'WHERE id=?",(q.b["local_calls"][0]["id"],))
    elif change=="global":x.db.execute("UPDATE autonomy_calls SET receipt='changed'WHERE id=?",(q.b["global_calls"][0]["id"],))
    elif change=="owner":x.db.execute("UPDATE autonomy_runs SET status='STOPPED'")
    elif change=="grant":x.db.execute("UPDATE events SET payload='{}'WHERE id=?",(f.EVENT,))
    elif change=="state":x.store.db.execute("UPDATE manual_state SET payload='{}'")
    elif change=="account":x.store.db.execute("UPDATE manual_account SET version=version+1")
    elif change=="file":pr.write_text(q.work/"input.json","changed")
    elif change=="extra":pr.write_text(q.work/"console.log","client output")
    elif change=="live":x.db.execute("INSERT INTO autonomy_calls VALUES('live','scientific','other',1,'2026-10-12','RUNNING','{}',NULL)")
    elif change=="reserved":x.db.execute("INSERT INTO autonomy_calls VALUES(?,'scientific',?,16,'2026-10-12','FAILED','{}','{}')",(q.b["next_call_id"],r.RUN))
    else:pr.write_text(q.d.state/"HALT","halt")
    state=list(x.store.db.execute("SELECT *FROM manual_state"))
    with pytest.raises(ValueError):r.recover(q.d,q.b,q.approval)
    assert list(x.store.db.execute("SELECT *FROM manual_state"))==state
    assert q.work.exists()and not(q.d.state/r.EVENT).exists()
def test_recovery_binds_corrected_function_and_actual_counted_admission(failed,monkeypatch):
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator import autonomy_limits as limits
    q=failed;x=q.x;r.recover(q.d,q.b,q.approval)
    implementation=NS(RUN=f.RUN,DOCUMENT_SHA=f.DOCUMENT_SHA,EVENT=f.EVENT,batch_allowance=f.batch_allowance)
    undo=r.bind(q.d,q.b,q.approval,implementation,f)
    monkeypatch.setattr(limits,"global_limit",lambda *args:30)
    monkeypatch.setattr(limits,"daily_allowance",lambda *args:{"limit":50,"authority_sha256":"d"*64})
    try:
        allowance=f.batch_allowance(x.store.batch,x.scope)
        assert allowance["analysis_allocation_used"]==2
        out=BatchAccounts.reserve_scientific(x.store.batch,q.b["next_call_id"],f.RUN,r.STAGE,"1"*40,
            {"workspace":str(q.work)})
        assert out["accounting_units"]==1 and out["run_limit"]==30 and out["batch_limit"]==128
        assert x.db.execute("SELECT count(*)FROM autonomy_calls WHERE change_id=?",(r.RUN,)).fetchone()[0]==16
        r.originals(q.d,q.b)
        with pytest.raises(ValueError):BatchAccounts.reserve_scientific(x.store.batch,q.b["next_call_id"],f.RUN,r.STAGE,"1"*40,{"workspace":str(q.work)})
    finally:undo()
def test_binding_never_changes_other_function_or_encoding(failed):
    q=failed;r.recover(q.d,q.b,q.approval);original=f.batch_allowance;encoder=f.encoded
    implementation=NS(RUN=f.RUN,DOCUMENT_SHA=f.DOCUMENT_SHA,EVENT=f.EVENT,batch_allowance=original)
    undo=r.bind(q.d,q.b,q.approval,implementation,f)
    try:
        assert f.encoded is encoder
        assert f.batch_allowance(q.x.store.batch,q.x.scope)["analysis_allocation_limit"]==4
        with pytest.raises(ValueError):f.batch_allowance(NS(),q.x.scope)
        with pytest.raises(ValueError):f.batch_allowance(q.x.store.batch,{**q.x.scope,"allocation_limit":5})
    finally:undo()
    assert f.batch_allowance is original
def test_unit_changes_only_entrypoint(monkeypatch,tmp_path):
    from tools import idea2_serialization_runtime as rt
    from orchestrator import manual_host_guard
    raw=(chr(10).join(["[Service]","User=partho","ProtectSystem=strict","NoNewPrivileges=true",
        "ExecStart=/usr/bin/python3 -s -B "+str(rt.BASE/"tools/idea2_interpretation_runtime.py")+" run",""])).encode()
    unit=tmp_path/"unit";unit.write_bytes(raw)
    monkeypatch.setattr(manual_host_guard,"trusted",lambda path:unit)
    parent=NS(ENTRY="tools/idea2_interpretation_runtime.py",metadata=lambda:({},{"unit":"prior.service"}),authority=lambda:None)
    changed=rt.unit_bytes(parent)
    assert changed.replace(str(rt.ROOT/rt.ENTRY).encode(),str(rt.BASE/parent.ENTRY).encode())==raw
