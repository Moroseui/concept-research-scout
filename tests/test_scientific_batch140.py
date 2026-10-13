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

# Durable reservation boundaries are exercised in test_multiwin_returned.py.
@pytest.mark.parametrize("file",["SCIENTIFIC_BATCH140_OPERATOR_APPROVAL.txt","SCIENTIFIC_BATCH140_OPERATOR_QUESTION.txt","SCIENTIFIC_BATCH140_OPERATOR_RECORD_PRIVATE.json","SCIENTIFIC_BATCH140_PRIVATE.json"])
def test_changed_authority_refused(tmp_path,file):
    import shutil
    (tmp_path/"docs").mkdir()
    for path in (ROOT/"docs").glob("SCIENTIFIC_BATCH140*"):
        shutil.copyfile(path,tmp_path/"docs"/path.name)
    (tmp_path/"docs"/file).write_text("changed")
    with pytest.raises(ValueError,match="SCOPE_CHANGED|OPERATOR_AUTHORITY_CHANGED"):b.document(tmp_path)
