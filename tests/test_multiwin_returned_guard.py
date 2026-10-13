"""Original validation at 21 calls, lifecycle checks, and unchanged refusals."""
import copy,json
from types import SimpleNamespace as NS
import pytest
from test_colab_simple_full import lane
from orchestrator import colab_simple_full as f, multiwin_returned_guard as patch,autonomy_limits as limits


@pytest.fixture
def continued(lane,monkeypatch):
    x=lane;f.activate(x.store,f.RUN)
    for i in range(8,21):
        x.global_db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
          ("extra"+str(i),"scientific",f.RUN,i+1,"2026-10-12","COMPLETE","{}","{}"))
    x.driver=NS(store=x.store,config=x.config)
    x.checked=[]
    def grant():x.checked.append(True)
    x.grant=grant
    monkeypatch.setattr(limits,"global_limit",lambda batch,run:26)
    return x


def test_old_lifecycle_guard_rejects_preserved_call21(continued):
    with pytest.raises(ValueError,match="SHARED_CALL_LIMIT"):f.validate(continued.store,f.RUN)


def test_repaired_lifecycle_retains_rows_and_calls_original_checks(continued):
    x=continued;before=list(x.global_db.iterdump())
    restore=patch.bind(x.driver,x.grant)
    try:
        assert f.validate(x.store,f.RUN)==x.scope
        assert x.checked==[True]
        # Actual preparation_hold and offset dynamically call the same validator.
        x.driver.status=lambda:{"phase":"COMMIT_SPEC"}
        assert f.offset(x.store,f.RUN,"run_spec_author")==3
        assert f.preparation_hold(x.driver,{"phase":"COMMIT_SPEC"},None,None)["execution_authorized"] is False
        with pytest.raises(ValueError,match="NO_EXECUTION_OR_COLLECTION"):
            f.preparation_hold(x.driver,{"phase":"COMMIT_SPEC"},"unexpected",None)
        assert list(x.global_db.iterdump())==before
    finally:restore()


@pytest.mark.parametrize("corrupt",["global","local","owner","parent","grant","config","approval","recovery","ceiling","too_many","wrong_store"])
def test_every_original_check_and_exact_continuation_still_refuses(continued,monkeypatch,corrupt):
    x=continued
    if corrupt=="global":x.global_db.execute("UPDATE autonomy_calls SET receipt='changed' WHERE id=?",(x.scope["prior"]["global_calls"][0]["id"],))
    elif corrupt=="local":x.store.db.execute("UPDATE manual_calls SET receipt='changed' WHERE id=?",(x.scope["prior"]["local_calls"][0]["id"],))
    elif corrupt=="owner":x.global_db.execute("UPDATE autonomy_runs SET status='COMPLETE'")
    elif corrupt=="parent":(x.parent/"preparation-plan.json").write_text("changed")
    elif corrupt=="grant":x.global_db.execute("UPDATE events SET payload='{}' WHERE id=?",(f.EVENT,))
    elif corrupt=="config":
        value=copy.deepcopy(x.config);value["author_timeout_seconds"]=1
        (x.new/"lane.json").write_text(json.dumps(value))
    elif corrupt=="approval":monkeypatch.setattr(f,"_approval",lambda *args:(_ for _ in ()).throw(ValueError("APPROVAL_CHANGED")))
    elif corrupt=="recovery":x.grant=lambda:(_ for _ in ()).throw(ValueError("RECOVERY_CHANGED"))
    elif corrupt=="ceiling":monkeypatch.setattr(limits,"global_limit",lambda *args:25)
    elif corrupt=="too_many":
        for i in range(21,27):
            x.global_db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
              ("extra"+str(i),"scientific",f.RUN,i+1,"2026-10-12","FAILED","{}","{}"))
    restore=patch.bind(x.driver,x.grant)
    before=list(x.global_db.iterdump())
    try:
        with pytest.raises(ValueError):f.validate(NS() if corrupt=="wrong_store"else x.store,f.RUN)
        assert list(x.global_db.iterdump())==before
    finally:restore()


def test_other_owner_delegated_and_binding_restores(continued,monkeypatch):
    seen=[];original=lambda *args:seen.append(args)or"legacy"
    monkeypatch.setattr(f,"validate",original)
    restore=patch.bind(continued.driver,continued.grant)
    assert f.validate("other-store","other")=="legacy"
    assert seen==[("other-store","other")]and not continued.checked
    restore();assert f.validate is original


def test_exact_cap26_allows_reconciliation_but_not25(continued):
    x=continued;restore=patch.bind(x.driver,x.grant)
    try:
        for i in range(21,26):
            x.global_db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
              ("extra"+str(i),"scientific",f.RUN,i+1,"2026-10-12","FAILED","{}","{}"))
        assert f.validate(x.store,f.RUN)==x.scope
        x.global_db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
              ("extra26","scientific",f.RUN,25,"2026-10-12","FAILED","{}","{}"))
        with pytest.raises(ValueError,match="SHARED_CALL_LIMIT"):f.validate(x.store,f.RUN)
    finally:restore()


def test_installer_retains_entire_unit_except_entrypoint(monkeypatch,tmp_path):
    from tools import multiwin_shared_runtime as rt
    from orchestrator import manual_host_guard
    unit=(chr(10).join(["[Service]","User=partho","ProtectSystem=strict","NoNewPrivileges=yes",
        "ExecStart=/usr/bin/python3 -s -B "+str(rt.PRIOR/"tools/multiwin_local_runtime.py")+" run",""])).encode()
    fpath=tmp_path/"unit";fpath.write_bytes(unit)
    monkeypatch.setattr(manual_host_guard,"trusted",lambda path:fpath)
    parent=NS(UNIT="previous.service",ENTRY="tools/multiwin_local_runtime.py",authority=lambda:None)
    new=rt.unit_bytes(parent)
    assert new.replace(str(rt.ROOT/rt.ENTRY).encode(),str(rt.PRIOR/parent.ENTRY).encode())==unit
