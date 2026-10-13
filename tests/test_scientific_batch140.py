import copy,json,sqlite3
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import scientific_batch140 as b
ROOT=Path(__file__).resolve().parents[1]
REVIEW="a"*64
MEETING="meeting-775e80719952cfe222a61dcd"
L="colab-arm-47e6a72d9a2c821a4938fcae"
COLAB="colab-arm-b9d64a3c09b799bc10b0eba7"

def freeze(db):
    scope=copy.deepcopy(b.document(ROOT))
    scope["frozen_calls"]=[{"id":r["id"],"sha256":b.sha(b.canonical(dict(r)))}
                         for r in db.execute("SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY id")]
    return scope
@pytest.fixture
def ledger():
    db=sqlite3.connect(":memory:",isolation_level=None);db.row_factory=sqlite3.Row
    db.execute("CREATE TABLE autonomy_calls(id TEXT PRIMARY KEY,kind TEXT,change_id TEXT,round INTEGER,day TEXT,status TEXT,binding TEXT,receipt TEXT)")
    for i in range(128):
        db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",(str(i),"scientific","prior",1,"2026-10-12","COMPLETE","{}","{}"))
    a=SimpleNamespace(db=db)
    yield a,freeze(db)
    db.close()
def add(a,ident,run,status="COMPLETE",kind="scientific"):
    a.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",(ident,kind,run,1,"2026-10-13",status,"{}","{}"))

def test_exact_verbatim_money_authority():
    s=b.document(ROOT)
    assert s["batch_limit"]==140 and sum(s["allocations"].values())==12
    assert (ROOT/"docs/SCIENTIFIC_BATCH140_OPERATOR_APPROVAL.txt").read_text()=="Approve12 calls: Colab and meeting"

def test_twelve_call_boundary_and_no_cross_purpose_borrowing(ledger):
    a,s=ledger
    for run in [COLAB,L,MEETING]:
        for i in range(4):
            v=b.allowance(a,run,s,REVIEW)
            assert v["purpose_used"]==i and v["limit"]==140
            add(a,run+str(i),run)
        with pytest.raises(ValueError,match="PURPOSE_EXHAUSTED|BATCH_EXHAUSTED"):
            b.allowance(a,run,s,REVIEW)
    assert a.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==140
    for run in [COLAB,L,MEETING]:
        with pytest.raises(ValueError,match="BATCH_EXHAUSTED"):b.allowance(a,run,s,REVIEW)

@pytest.mark.parametrize("status",["FAILED","UNCERTAIN","RUNNING","COMPLETE"])
def test_every_attempt_status_counts(ledger,status):
    a,s=ledger
    for i in range(4):add(a,"new-"+str(i),MEETING,status)
    with pytest.raises(ValueError,match="PURPOSE_EXHAUSTED"):b.allowance(a,MEETING,s,REVIEW)
    assert b.allowance(a,L,s,REVIEW)["purpose_used"]==0

@pytest.mark.parametrize("change",["delete","receipt","relabel"])
def test_original_rows_cannot_be_rewritten(ledger,change):
    a,s=ledger
    if change=="delete":a.db.execute("DELETE FROM autonomy_calls WHERE id='0'")
    if change=="receipt":a.db.execute("UPDATE autonomy_calls SET receipt='changed' WHERE id='0'")
    if change=="relabel":a.db.execute("UPDATE autonomy_calls SET kind='administrative' WHERE id='0'")
    with pytest.raises(ValueError,match="ORIGINAL_CALL_CHANGED"):b.allowance(a,MEETING,s,REVIEW)

def test_unknown_future_call_and_unknown_run_refuse(ledger):
    a,s=ledger
    with pytest.raises(ValueError,match="FIXED_SCOPE"):b.allowance(a,"unapproved",s,REVIEW)
    add(a,"unknown","not-approved")
    with pytest.raises(ValueError,match="UNCLASSIFIED_NEW_CALL"):b.allowance(a,MEETING,s,REVIEW)

def test_administrative_calls_do_not_consume_scientific_allocation(ledger):
    a,s=ledger;add(a,"admin","review",kind="implementation_review")
    assert b.allowance(a,MEETING,s,REVIEW)["actual_scientific_calls"]==128

@pytest.mark.parametrize("key,value",[("batch_limit",141),("baseline_count",127),("allocations",{"meeting":12})])
def test_no_caller_selected_increase(ledger,key,value):
    a,s=ledger;s[key]=value
    with pytest.raises(ValueError,match="FIXED_SCOPE"):b.allowance(a,MEETING,s,REVIEW)


# Actual L reservation transaction. Only external approval/terminal proof is
# stubbed here; its read-only integrity controls have separate mutation tests.
from test_colab_arm_question import scenario, install_owner
from orchestrator import colab_arm_question as q

@pytest.fixture
def l_admission(scenario,monkeypatch):
    x=scenario
    install_owner(x)
    for i in range(4):
        x.accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
            ("original-L-"+str(i),"scientific",L,i+1,"2026-10-12","COMPLETE","{}","{}"))
    for i in range(18):
        x.accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
            ("other-original-"+str(i),"scientific","history",i+1,"2026-10-12","COMPLETE","{}","{}"))
    s=freeze(x.accounts.db)
    monkeypatch.setattr(q,"configuration",lambda a,run:x.scope if run==L else None)
    monkeypatch.setattr(q,"terminal_ids",lambda a,scope:[])
    monkeypatch.setattr(q,"batch_allowance",lambda a,scope:b.allowance(a,L,s,REVIEW))
    def reserve(ident):
        return x.accounts.reserve_scientific(ident,L,"run_spec_author","a"*40,
                                            {"stage":"run_spec_author"})
    return x,s,reserve

def test_L_admission_four_calls_then_refuses_and_preserves_all128(l_admission):
    x,s,reserve=l_admission
    for i in range(4):
        r=reserve("L-new-"+str(i))
        assert (r["batch_limit"],r["run_limit"],r["daily_limit"])==(140,20,50)
        x.accounts.db.execute("UPDATE autonomy_calls SET status='COMPLETE' WHERE id=?",("L-new-"+str(i),))
        x.accounts.db.execute("UPDATE jobs SET status='COMPLETE' WHERE id=?",("L-new-"+str(i),))
    with pytest.raises(ValueError,match="PURPOSE_EXHAUSTED"):reserve("fifth")
    assert not x.accounts.db.execute("SELECT 1 FROM jobs WHERE id='fifth'").fetchone()
    for old in s["frozen_calls"]:
        row=x.accounts.db.execute("SELECT * FROM autonomy_calls WHERE id=?",(old["id"],)).fetchone()
        assert b.sha(b.canonical(dict(row)))==old["sha256"]

@pytest.mark.parametrize("boundary",["daily","halt","uncertain","running","run20","batch140"])
def test_L_actual_admission_retains_all_refusals(l_admission,boundary):
    from datetime import datetime,timezone
    x,s,reserve=l_admission
    if boundary=="daily":
        day=datetime.now(timezone.utc).date().isoformat()
        used=x.accounts.db.execute("SELECT count(*) FROM autonomy_calls WHERE day=?",(day,)).fetchone()[0]
        for i in range(50-used):
            x.accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                ("admin-"+str(i),"implementation_review","review",i,day,"COMPLETE","{}","{}"))
    elif boundary=="halt":
        (x.accounts.folder/"HALT").touch()
    elif boundary in {"uncertain","running"}:
        add(x.accounts,"foreign","foreign",boundary.upper(),"implementation_review")
    elif boundary=="run20":
        ids=[r["id"] for r in x.accounts.db.execute(
            "SELECT id FROM autonomy_calls WHERE id LIKE 'other-original-%' LIMIT 16")]
        for ident in ids:x.accounts.db.execute("UPDATE autonomy_calls SET change_id=? WHERE id=?",(L,ident))
        s.clear();s.update(freeze(x.accounts.db))
    else:
        for run in (L,COLAB,MEETING):
            for i in range(4):add(x.accounts,run+str(i),run)
    before=list(x.accounts.db.iterdump())
    with pytest.raises(ValueError,match="DAILY_CALL_LIMIT|BATCH_HALTED|BATCH_UNCERTAIN_OR_RUNNING_CALL|RUN_CALL_LIMIT|BATCH_EXHAUSTED"):
        reserve("refused")
    assert list(x.accounts.db.iterdump())==before

@pytest.mark.parametrize("file",["SCIENTIFIC_BATCH140_OPERATOR_APPROVAL.txt","SCIENTIFIC_BATCH140_OPERATOR_QUESTION.txt","SCIENTIFIC_BATCH140_OPERATOR_RECORD_PRIVATE.json","SCIENTIFIC_BATCH140_PRIVATE.json"])
def test_changed_authority_refused(tmp_path,file):
    import shutil
    (tmp_path/"docs").mkdir()
    for path in (ROOT/"docs").glob("SCIENTIFIC_BATCH140*"):
        shutil.copyfile(path,tmp_path/"docs"/path.name)
    (tmp_path/"docs"/file).write_text("changed")
    with pytest.raises(ValueError,match="SCOPE_CHANGED|OPERATOR_AUTHORITY_CHANGED"):b.document(tmp_path)
