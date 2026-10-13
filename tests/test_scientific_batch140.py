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

# Exercise the actual durable admission method, leaving its real daily/run/
# global/uncertainty/duplicate checks intact. Only external lane qualification
# is replaced by the already tested synthetic original-lane fixture.
from test_meeting_preparation import accounts,owner
from orchestrator import meeting_preparation as m,autonomy_limits,preparation_followup
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.autonomy_review_runner import ReviewQueue
from tools.deploy_manual_lane import bound

def admission_fixture(accounts,monkeypatch):
    accounts.db.execute("CREATE TABLE jobs(id TEXT PRIMARY KEY,binding TEXT,phase TEXT,status TEXT,receipt TEXT)")
    accounts.status=lambda ident:ReviewQueue.status(accounts,ident)
    m.register(accounts,owner(accounts),accounts.scope)
    config={"run_id":m.RUN,m.FIELD:{"scope_sha256":m.DOCUMENT_SHA},
            "backend":"meeting-preparation","item_number":6,"author_timeout_seconds":1800,
            "review_contract":"bound-review/v1"}
    lane=bound(accounts.filesystem_root,accounts.scope["new_lane"])
    lane.mkdir(parents=True);(lane/"lane.json").write_text(json.dumps(config))
    for i in range(4):add(accounts,"original-meeting-"+str(i),m.RUN)
    s=freeze(accounts.db)
    monkeypatch.setattr(m,"configuration",lambda a,run:accounts.scope if run==m.RUN else None)
    def funded(a,original):
        assert original==accounts.scope
        m.preserved(a,original)
        return b.allowance(a,m.RUN,s,REVIEW)
    monkeypatch.setattr(m,"batch_allowance",funded)
    workspace=Path(accounts.scope["new_lane"]).with_name("lane-scientific-workspaces")/"run_spec_author-1"
    bound(accounts.filesystem_root,str(workspace)).mkdir(parents=True)
    def reserve(ident):
        return BatchAccounts.reserve_scientific(accounts,ident,m.RUN,"run_spec_author","a"*40,
                     {"stage":"run_spec_author","workspace":str(workspace)})
    return s,reserve

def test_actual_reservation_refuses_fifth_and_retains_originals(accounts,monkeypatch):
    s,reserve=admission_fixture(accounts,monkeypatch)
    # The synthetic original rows have no binding.stage, so the fixture's exact
    # workspace suffix advances after each newly admitted call.
    for i in range(4):
        workspace=Path(accounts.scope["new_lane"]).with_name("lane-scientific-workspaces")/("run_spec_author-"+str(i+1))
        bound(accounts.filesystem_root,str(workspace)).mkdir(parents=True,exist_ok=True)
        r=BatchAccounts.reserve_scientific(accounts,"funded-"+str(i),m.RUN,"run_spec_author","a"*40,
                    {"stage":"run_spec_author","workspace":str(workspace)})
        assert r["batch_limit"]==140 and r["run_limit"]==20 and r["daily_limit"]==50
        accounts.db.execute("UPDATE autonomy_calls SET status='COMPLETE' WHERE id=?",("funded-"+str(i),))
        accounts.db.execute("UPDATE jobs SET status='COMPLETE' WHERE id=?",("funded-"+str(i),))
    workspace=Path(accounts.scope["new_lane"]).with_name("lane-scientific-workspaces")/"run_spec_author-5"
    bound(accounts.filesystem_root,str(workspace)).mkdir()
    with pytest.raises(ValueError,match="PURPOSE_EXHAUSTED"):
        BatchAccounts.reserve_scientific(accounts,"fifth",m.RUN,"run_spec_author","a"*40,
              {"stage":"run_spec_author","workspace":str(workspace)})
    assert not accounts.db.execute("SELECT 1 FROM jobs WHERE id='fifth'").fetchone()
    assert accounts.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]==132
    assert all(b.sha(b.canonical(dict(accounts.db.execute("SELECT * FROM autonomy_calls WHERE id=?",(r["id"],)).fetchone())))==r["sha256"] for r in s["frozen_calls"])

@pytest.mark.parametrize("boundary",["daily","halt","uncertain","running"])
def test_existing_admission_refusals_still_apply(accounts,monkeypatch,boundary):
    s,reserve=admission_fixture(accounts,monkeypatch)
    if boundary=="daily":
        from datetime import datetime,timezone
        day=datetime.now(timezone.utc).date().isoformat()
        used=accounts.db.execute("SELECT count(*) FROM autonomy_calls WHERE day=?",(day,)).fetchone()[0]
        for i in range(50-used):
            accounts.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
                ("admin-"+str(i),"implementation_review","review",i,day,"COMPLETE","{}","{}"))
    if boundary=="halt":(accounts.folder/"HALT").touch()
    if boundary in {"uncertain","running"}:add(accounts,"open","foreign",boundary.upper(),kind="implementation_review")
    count=accounts.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]
    with pytest.raises(ValueError,match="DAILY_CALL_LIMIT|BATCH_HALTED|UNCLASSIFIED_OR_RUNNING_CALL"):
        reserve("refused")
    assert accounts.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==count
    assert not accounts.db.execute("SELECT 1 FROM jobs WHERE id='refused'").fetchone()

def test_actual_global_ceiling_refused_without_a_new_row(accounts,monkeypatch):
    s,reserve=admission_fixture(accounts,monkeypatch)
    for run in [L,COLAB,MEETING]:
        for i in range(4):
            add(accounts,run+str(i),run)
    with pytest.raises(ValueError,match="BATCH_EXHAUSTED"):reserve("over140")
    assert not accounts.db.execute("SELECT 1 FROM jobs WHERE id='over140'").fetchone()
    assert accounts.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]==140

def test_actual_run20_refusal_unchanged(accounts,monkeypatch):
    scope,reserve=admission_fixture(accounts,monkeypatch)
    ids=[r["id"]for r in accounts.db.execute("SELECT id FROM autonomy_calls WHERE id LIKE 'prior-%' ORDER BY id LIMIT 16")]
    for ident in ids:accounts.db.execute("UPDATE autonomy_calls SET change_id=? WHERE id=?",(MEETING,ident))
    accounts.scope["frozen_calls"]=[{"id":r["id"],"sha256":m.sha(m.encoded(dict(r)))}for r in accounts.db.execute("SELECT * FROM autonomy_calls WHERE id LIKE 'prior-%' ORDER BY id")]
    scope.clear();scope.update(freeze(accounts.db))
    with pytest.raises(ValueError,match="AUTONOMY_RUN_CALL_LIMIT"):reserve("over20")
    assert not accounts.db.execute("SELECT 1 FROM jobs WHERE id='over20'").fetchone()

@pytest.mark.parametrize("file",["SCIENTIFIC_BATCH140_OPERATOR_APPROVAL.txt","SCIENTIFIC_BATCH140_OPERATOR_QUESTION.txt","SCIENTIFIC_BATCH140_OPERATOR_RECORD_PRIVATE.json","SCIENTIFIC_BATCH140_PRIVATE.json"])
def test_changed_authority_refused(tmp_path,file):
    import shutil
    (tmp_path/"docs").mkdir()
    for path in (ROOT/"docs").glob("SCIENTIFIC_BATCH140*"):
        shutil.copyfile(path,tmp_path/"docs"/path.name)
    (tmp_path/"docs"/file).write_text("changed")
    with pytest.raises(ValueError,match="SCOPE_CHANGED|OPERATOR_AUTHORITY_CHANGED"):b.document(tmp_path)
