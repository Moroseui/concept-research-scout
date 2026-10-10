"""One bounded administrative call through the real unchanged ReviewQueue."""
import json,sqlite3
from types import SimpleNamespace
import pytest
from tools import review_preparation_branch_repair_once as boot
from orchestrator import autonomy_review_runner as runner,autonomy_review as review,autonomy_limits as limits,administrative_terminal as terminal,connectivity

def proof(db):
    return {'id':boot.PREMODEL_ID,'model_client_launched':False,'proof_sha256':'f'*64}

@pytest.fixture
def queue(tmp_path):
    q=runner.ReviewQueue(tmp_path)
    for n in range(53):
        q.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',(str(n),'implementation_review','old',1,'2026-10-10','UNCERTAIN' if n==0 else 'COMPLETE','{}','{}'))
    q.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,NULL)',(boot.PREMODEL_ID,'scientific','aggregate',1,'2026-10-10','RUNNING','{}'))
    yield q
    q.db.close()

def inputs(q):
    return (q.db,None,{'call_id':'0'},SimpleNamespace(qualify=lambda row,binding,read:{'id':row['id']}),lambda row,path:{'id':row['id']},lambda p:b'',proof)

def test_exact_proof_does_not_rewrite_reservation_or_count(queue):
    before=[tuple(r) for r in queue.db.execute('SELECT * FROM autonomy_calls')]
    assert boot.admission_preflight(queue.db,'new','2026-10-10',proof)['id']==boot.PREMODEL_ID
    assert {p['id'] for p in boot.exceptions(*inputs(queue))}=={'0',boot.PREMODEL_ID}
    assert [tuple(r) for r in queue.db.execute('SELECT * FROM autonomy_calls')]==before

@pytest.mark.parametrize('fault',['other-running','missing-premodel','uncertain-premodel','missing-old-proof','existing-request','count-low','count-high','midnight'])
def test_scope_count_uncertainty_and_midnight_refuse(queue,fault):
    db=queue.db;day='2026-10-10'
    if fault=='other-running':db.execute("UPDATE autonomy_calls SET status='RUNNING' WHERE id='1'")
    elif fault=='missing-premodel':db.execute('UPDATE autonomy_calls SET status=? WHERE id=?',('COMPLETE',boot.PREMODEL_ID))
    elif fault=='uncertain-premodel':db.execute('UPDATE autonomy_calls SET status=? WHERE id=?',('UNCERTAIN',boot.PREMODEL_ID))
    elif fault=='missing-old-proof':db.execute("UPDATE autonomy_calls SET status='COMPLETE' WHERE id='0'")
    elif fault=='existing-request':db.execute('UPDATE autonomy_calls SET change_id=? WHERE id=?',(boot.CHANGE,'1'))
    elif fault=='count-low':db.execute("DELETE FROM autonomy_calls WHERE id='2'")
    elif fault=='count-high':db.execute("INSERT INTO autonomy_calls VALUES('extra','implementation_review','old',1,'2026-10-10','COMPLETE','{}','{}')")
    else:day='2026-10-11'
    before=[tuple(r) for r in db.execute('SELECT * FROM autonomy_calls')]
    with pytest.raises(ValueError):
        boot.admission_preflight(db,'new',day,proof);boot.exceptions(*inputs(queue))
    assert [tuple(r) for r in db.execute('SELECT * FROM autonomy_calls')]==before

@pytest.mark.parametrize('extra',[False,True])
def test_real_queue_transaction_counts_call55_and_refuses_concurrent_growth(queue,monkeypatch,extra):
    from datetime import datetime,timezone
    class Clock:
        @staticmethod
        def now(tz):return datetime(2026,10,10,22,20,tzinfo=timezone.utc)
    monkeypatch.setattr(runner,'datetime',Clock)
    monkeypatch.setattr(limits,'authority',lambda:'a'*64)
    monkeypatch.setattr(review,'round_authority',lambda:'b'*64)
    monkeypatch.setattr(connectivity,'require',lambda *args:{'status':'PASS','synthetic':True})
    original=boot.admission_preflight
    monkeypatch.setattr(boot,'admission_preflight',lambda db,packet,day:original(db,packet,day,proof))
    manifest={'change_id':boot.CHANGE,'round':1};packet=review.sha(review.canonical(manifest))
    original(queue.db,packet,'2026-10-10',proof)
    if extra:queue.db.execute("INSERT INTO autonomy_calls VALUES('extra','implementation_review','old',1,'2026-10-10','COMPLETE','{}','{}')")
    monkeypatch.setattr(limits,'daily_allowance',boot.dated_bootstrap(lambda day:{'limit':100,'authority_sha256':'c'*64},{'db':queue.db},packet))
    monkeypatch.setattr(terminal,'administrative_exceptions',lambda db,root:boot.exceptions(*inputs(queue)))
    if extra:
        with pytest.raises(ValueError,match='EXACT_CALL55'):queue.reserve(manifest,{})
        assert queue.status(packet)['status']=='NOT_RESERVED'
    else:
        value,created=queue.reserve(manifest,{})
        assert created and value['status']=='RUNNING'
        assert queue.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==55
        assert queue.db.execute('SELECT status FROM autonomy_calls WHERE id=?',(boot.PREMODEL_ID,)).fetchone()[0]=='RUNNING'
        with pytest.raises(ValueError,match='ONE_ADMIN_CALL_ONLY'):boot.exceptions(*inputs(queue))

def test_dated_policy_restores50_and_transaction_required(queue):
    boot.verify_dated_policy(lambda day:{'limit':100 if day=='2026-10-10' else 50})
    selected=boot.dated_bootstrap(lambda day:{'limit':100},{'db':queue.db},'packet')
    with pytest.raises(ValueError,match='ADMISSION_TRANSACTION_REQUIRED'):selected('2026-10-10')
    with pytest.raises(ValueError,match='UTC_DAY'):selected('2026-10-11')
