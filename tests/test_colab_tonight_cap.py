"""Real synthetic admission boundaries; no provider or live ledger."""
import json
from pathlib import Path
import pytest
from orchestrator import autonomy_limits as limits
from test_temporary_daily_cap import queue as base_queue,reserve,Clock
from orchestrator import autonomy_review_runner as reviewer
from tools import temporary_daily_cap as adapter
ROOT=Path(__file__).resolve().parents[1]
def queue(tmp_path,monkeypatch,day,kind,count):
    # Test the deployed legacy reviewer with its already-reviewed dated method,
    # not the unrelated, uninstalled opposite-family development route.
    dated=adapter.module('_test_tonight_admin',ROOT/'docs/COLAB_TONIGHT_ADMIN_ADMISSION_PRIVATE.py')
    monkeypatch.setattr(dated,'datetime',Clock)
    monkeypatch.setattr(reviewer.ReviewQueue,'reserve',dated.ReviewQueue.reserve)
    return base_queue(tmp_path,monkeypatch,day,kind,count)
@pytest.mark.parametrize('kind',['scientific','administrative'])
@pytest.mark.parametrize('day,count,ok',[('2026-10-12',50,True),('2026-10-12',99,True),
 ('2026-10-12',100,False),('2026-10-13',49,True),('2026-10-13',50,False),
 ('2026-10-11',50,False),('2027-10-12',50,False)])
def test_tonight_real_admission_preserves_old_rows(tmp_path,monkeypatch,kind,day,count,ok):
    q=queue(tmp_path,monkeypatch,day,kind,count)
    before=[tuple(r)for r in q.db.execute('SELECT * FROM autonomy_calls ORDER BY id')]
    if ok:
        result=reserve(q,kind)
        row=q.db.execute('SELECT binding FROM autonomy_calls WHERE id=?',(result['id'],)).fetchone()
        body=json.loads(row[0]);cap=body['caps']if kind=='scientific'else body
        assert cap['daily_limit_authority_sha256']==limits.daily_allowance(day)['authority_sha256']
    else:
        with pytest.raises(ValueError,match='AUTONOMY_DAILY_CALL_LIMIT'):reserve(q,kind)
    assert [tuple(r)for r in q.db.execute("SELECT * FROM autonomy_calls WHERE id LIKE 'original-%' OR id='prior-day' ORDER BY id")]==before
@pytest.mark.parametrize('kind',['scientific','administrative'])
def test_midnight_reverts_in_same_process(tmp_path,monkeypatch,kind):
    q=queue(tmp_path,monkeypatch,'2026-10-12',kind,99);reserve(q,kind)
    q.db.execute("UPDATE autonomy_calls SET status='COMPLETE'WHERE status='RUNNING'")
    for i in range(50):
        q.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
          ('tomorrow-'+str(i),'implementation_review','past',1,'2026-10-13','COMPLETE','{}','{}'))
    Clock.day='2026-10-13'
    with pytest.raises(ValueError,match='AUTONOMY_DAILY_CALL_LIMIT'):reserve(q,kind,'tomorrow')
@pytest.mark.parametrize('mode',['missing','changed','symlink'])
def test_authority_exact(tmp_path,mode):
    root=Path(limits.__file__).resolve().parents[1];(tmp_path/'docs').mkdir()
    for name in (limits.DOCUMENT,limits.DAILY_DOCUMENT):
        (tmp_path/name).write_bytes((root/name).read_bytes())
    p=tmp_path/limits.TONIGHT_DOCUMENT
    if mode=='changed':p.write_text('unapproved')
    if mode=='symlink':p.symlink_to(root/limits.TONIGHT_DOCUMENT)
    with pytest.raises((ValueError,FileNotFoundError)):limits.daily_allowance('2026-10-12',tmp_path)
    assert limits.daily_allowance('2026-10-13',tmp_path)['limit']==50
def test_cache_copy_keeps_evidence_excludes_subtrees(tmp_path):
    from tools.colab_pnormct_probe import evidence_files
    root=tmp_path/'probe';root.mkdir();(root/'execution.py').write_text('source')
    (root/'PACKAGE_RESULT.json').write_text('{"status":"PASS"}')
    result=root/'result';result.mkdir()
    (result/'native.pth').write_bytes(b'checkpoint')
    (result/'gate.json').write_text(json.dumps({'files':{'native.pth':{'bytes':10}}}))
    cache=result/'torchinductor_synthetic';cache.mkdir()
    for i in range(1100):(cache/str(i)).write_text('synthetic cache')
    names={p.relative_to(root).as_posix()for p in evidence_files(root)}
    assert names=={'execution.py','PACKAGE_RESULT.json','result/native.pth','result/gate.json'}
def test_declared_evidence_never_omitted(tmp_path):
    from tools.colab_pnormct_probe import evidence_files
    result=tmp_path/'result';result.mkdir()
    (result/'gate.json').write_text('{"files":{"missing.pth":{}}}')
    with pytest.raises(RuntimeError,match='EVIDENCE_MEMBER'):evidence_files(tmp_path)
def test_evidence_symlink_refused(tmp_path):
    from tools.colab_pnormct_probe import evidence_files
    (tmp_path/'execution.py').symlink_to('/nonexistent')
    with pytest.raises(RuntimeError,match='EVIDENCE_ALIAS'):evidence_files(tmp_path)

def test_installed_binding_uses_exact_original_and_preserves_other_selectors(monkeypatch):
    from tools import colab_tonight_cap as c
    original=adapter.module('_tonight_legacy',ROOT/'tests/fixtures/daily_cap/autonomy_review_runner.py')
    monkeypatch.setattr(reviewer.ReviewQueue,'reserve',original.ReviewQueue.reserve)
    monkeypatch.setattr(limits,'daily_allowance',limits.daily_allowance)
    monkeypatch.setattr(c,'verified',lambda: {})
    monkeypatch.setattr(c,'ROOT',ROOT)
    monkeypatch.setattr(c,'trusted',lambda p:p)
    selected={k:getattr(limits,k)for k in ('global_limit','local_limit','scientific_batch_allowance','cap_authority')}
    result=c.bind_administrative()
    assert reviewer.ReviewQueue.reserve is result
    assert all(getattr(limits,k)is v for k,v in selected.items())
    assert limits.daily_allowance('2026-10-12')['limit']==100
    assert limits.daily_allowance('2026-10-13')['limit']==50
def test_binding_rejects_unknown_existing_method(monkeypatch):
    from tools import colab_tonight_cap as c
    def unrecognized(*args):pass
    monkeypatch.setattr(reviewer.ReviewQueue,'reserve',unrecognized)
    monkeypatch.setattr(c,'verified',lambda:{})
    monkeypatch.setattr(c,'ROOT',ROOT)
    monkeypatch.setattr(c,'trusted',lambda p:p)
    with pytest.raises(ValueError,match='ORIGINAL_ADMISSION_METHOD'):c.bind_administrative()
    assert reviewer.ReviewQueue.reserve is unrecognized

@pytest.mark.parametrize('count,day,running,used,ok',[
 (50,'2026-10-12',False,False,True),(49,'2026-10-12',False,False,False),
 (51,'2026-10-12',False,False,False),(50,'2026-10-13',False,False,False),
 (50,'2026-10-12',True,False,False),(50,'2026-10-12',False,True,False)])
def test_bootstrap_exact_single_review(tmp_path,count,day,running,used,ok):
    import sqlite3,hashlib,types
    from tools import colab_tonight_bootstrap as b
    db=sqlite3.connect(':memory:')
    db.execute('CREATE TABLE autonomy_calls(id,change_id,day,status)')
    for i in range(count):
        db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?)',
          (str(i),b.CHANGE if used and i==0 else 'old','2026-10-12','RUNNING'if running and i==0 else'COMPLETE'))
    manifest={'change_id':b.CHANGE,'round':1,'predecessor':None,'source_sha':'a'*40}
    packet=hashlib.sha256(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    before=db.execute('SELECT * FROM autonomy_calls').fetchall();limit=types.SimpleNamespace(DAILY=50,daily_allowance=lambda day:{'limit':50,'authority_sha256':'old'})
    operator=ROOT/'docs/COLAB_TONIGHT_OPERATOR_20261012.txt'
    if ok:
        assert b.allow_once(db,limit,manifest,packet,'a'*40,operator,day)==50 and limit.DAILY==50
        assert limit.daily_allowance(day)=={'limit':100,'authority_sha256':b.AUTHORITY}
        with pytest.raises(ValueError,match='ONE_DATED_ADMISSION'):limit.daily_allowance(day)
    else:
        with pytest.raises(ValueError):b.allow_once(db,limit,manifest,packet,'a'*40,operator,day)
        assert limit.DAILY==50
    assert db.execute('SELECT * FROM autonomy_calls').fetchall()==before

def test_bootstrap_through_deployed_dated_queue(tmp_path,monkeypatch):
    from tools import colab_tonight_bootstrap as b
    from orchestrator import administrative_terminal as terminal,autonomy_review as review
    q=queue(tmp_path,monkeypatch,b.DAY,'administrative',50)
    manifest={'change_id':b.CHANGE,'round':1,'predecessor':None,'source_sha':'a'*40}
    ident=review.sha(review.canonical(manifest))
    before=[tuple(r)for r in q.db.execute('SELECT * FROM autonomy_calls ORDER BY id')]
    monkeypatch.setattr(limits,'daily_allowance',lambda day:{'limit':50,'authority_sha256':'old'})
    def admit(db,root):
        b.allow_once(db,limits,manifest,ident,'a'*40,ROOT/'docs/COLAB_TONIGHT_OPERATOR_20261012.txt',b.DAY)
        return []
    monkeypatch.setattr(terminal,'administrative_exceptions',admit)
    row,new=q.reserve(manifest,{})
    assert new
    binding=json.loads(row['binding'])
    assert binding['daily_limit']==100 and binding['daily_limit_authority_sha256']==b.AUTHORITY
    assert limits.DAILY==50
    assert [tuple(r)for r in q.db.execute("SELECT * FROM autonomy_calls WHERE id!=? ORDER BY id",(ident,))]==before
