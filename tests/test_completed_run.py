"""Synthetic private-copy closures; real SQLite, no mocked ledger operations."""
import copy
import json
import sqlite3
from pathlib import Path
import pytest
from orchestrator import completed_run as c
from orchestrator.autonomy_accounting import BatchAccounts
from tools.deploy_manual_lane import bound


def put(root,name,raw):
    p=bound(root,name);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(raw);return p


@pytest.fixture
def closed(tmp_path):
    root=tmp_path/'host';root.mkdir()
    batch=BatchAccounts(bound(root,c.LEDGER).parent,filesystem_root=root)
    # The copied owner is complete and explicitly operator-accepted.
    batch.db.execute('INSERT INTO autonomy_runs VALUES(?,?,?)',(c.RUN,'{}','COMPLETE'))
    calls=[]
    for n,status in enumerate(('UNCERTAIN','FAILED','COMPLETE')):
        ident='old'+str(n)
        batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',(ident,'scientific',c.RUN,n+1,'2000-01-01',status,'{}','{}'))
        calls.append((ident,status))
    report=put(root,'/private/accepted.md',b'Synthetic accepted report')
    receipt={'acceptance_type':'operator-accepted','report_sha256':c.sha(report.read_bytes())}
    batch.db.execute('INSERT INTO events VALUES(?,?,?)',(c.RUN+':accepted',c.RUN,json.dumps(receipt)))
    lane='/var/lib/research-system-manual-sprint10/releases/complete/lane'
    put(root,lane+'/lane.json',json.dumps({'run_id':c.RUN}).encode())
    with sqlite3.connect(bound(root,lane+'/jobs.sqlite')) as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('CREATE TABLE manual_calls(id TEXT,status TEXT)');db.executemany('INSERT INTO manual_calls VALUES(?,?)',calls)
        for name in ('manual_state','manual_account','manual_recoveries'):
            db.execute('CREATE TABLE '+name+'(id INTEGER,payload TEXT)')
        db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps({'phase':'COMPLETE'}),))
    put(root,lane+'/REPORT.md',report.read_bytes())
    authority=Path(__file__).resolve().parents[1]/'docs/CONNECTIONS_OPERATOR_APPROVAL.txt'
    put(root,'/private/authority.txt',authority.read_bytes())
    review={'status':'REVIEWED_BY_OPERATOR','stocktake_run':c.RUN,'accepted_report_sha256':c.sha(report.read_bytes())}
    put(root,'/private/review.json',json.dumps(review).encode())
    c.seal(root,'/private/authority.txt','/private/review.json',lane)
    return root,batch,lane


def test_exact_closed_run_admits_new_run_without_rewriting_or_reset(closed):
    root,batch,lane=closed
    before=c.rows(batch.db,'autonomy_calls',c.RUN)
    assert c.closed_ids(batch,'new',root=root)=={'old0','old1'}
    assert c.closed_lanes(root)=={bound(root,lane).resolve()}
    batch.register_run('new',{'synthetic':True})
    batch.reserve_scientific('newcall','new','run_spec_author','a'*40,{})
    assert c.rows(batch.db,'autonomy_calls',c.RUN)==before
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==4
    with pytest.raises(ValueError,match='DUPLICATE'):batch.reserve_scientific('newcall','new','run_spec_author','a'*40,{})
    with pytest.raises(ValueError,match='CANNOT_REOPEN'):c.closed_ids(batch,c.RUN,root=root)


@pytest.mark.parametrize('damage',['global-row','active','acceptance','report','review','local-row','new-uncertain'])
def test_changed_unaccepted_or_unrelated_calls_still_refuse(closed,damage):
    root,batch,lane=closed
    if damage=='global-row':batch.db.execute("UPDATE autonomy_calls SET binding='changed' WHERE id='old0'")
    elif damage=='active':batch.db.execute("UPDATE autonomy_runs SET status='ACTIVE' WHERE id=?",(c.RUN,))
    elif damage=='acceptance':batch.db.execute("UPDATE events SET payload='{}' WHERE id=?",(c.RUN+':accepted',))
    elif damage=='report':bound(root,lane+'/REPORT.md').write_text('changed')
    elif damage=='review':bound(root,'/private/review.json').write_text('{}')
    elif damage=='local-row':
        with sqlite3.connect(bound(root,lane+'/jobs.sqlite')) as db:db.execute("UPDATE manual_calls SET status='RUNNING' WHERE id='old0'")
    else:
        batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('unrelated','scientific','another',1,'2000-01-01','UNCERTAIN','{}','{}'))
    if damage=='active':
        with pytest.raises(ValueError):c.validate(root,batch.db)
    else:
        batch.register_run('new',{})
        with pytest.raises(ValueError):batch.reserve_scientific('newcall','new','run_spec_author','a'*40,{})
    assert not batch.db.execute("SELECT 1 FROM autonomy_calls WHERE id='newcall'").fetchone()


def test_missing_closure_never_closes_generic_uncertainty(tmp_path):
    batch=BatchAccounts(tmp_path/'ledger')
    batch.register_run('new',{})
    batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('other','scientific','old',1,'2000-01-01','UNCERTAIN','{}','{}'))
    with pytest.raises(ValueError,match='UNCERTAIN'):batch.reserve_scientific('newcall','new','run_spec_author','a'*40,{})
