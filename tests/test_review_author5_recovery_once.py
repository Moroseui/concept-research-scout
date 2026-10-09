import sqlite3
from types import SimpleNamespace
import pytest
from tools import review_author5_recovery_once as boot

@pytest.fixture
def ledger(monkeypatch):
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE autonomy_calls(id TEXT,change_id TEXT,status TEXT)')
    db.execute("INSERT INTO autonomy_calls VALUES('known','scientific-run','UNCERTAIN')")
    monkeypatch.setattr(boot,'stopped',lambda unit:None)
    recovery=SimpleNamespace(CALL='known',UNIT='exact',binding=lambda:{},terminal=lambda row,bodies:{'original_status':row['status'],'files':bodies})
    def verify(row,path):raise ValueError('UNKNOWN_REFUSED')
    return db,recovery,verify


def test_only_exact_failed_call_exempted_no_row_edits(ledger):
    db,rec,verify=ledger;before=list(db.iterdump())
    result=boot.exceptions(db,None,rec,verify,lambda b:{'native':'pin'})
    assert result[0]['classification']=='OPERATOR_STANDING_ONE_ADMIN_AUTHOR5_REPAIR'
    assert list(db.iterdump())==before

@pytest.mark.parametrize('block',['running','unknown','prior-admin','nonterminal','changed-native','missing'])
def test_bootstrap_does_not_exempt_other_calls_or_allow_second_review(ledger,monkeypatch,block):
    db,rec,verify=ledger
    if block=='running':db.execute("UPDATE autonomy_calls SET status='RUNNING'")
    elif block=='unknown':db.execute("INSERT INTO autonomy_calls VALUES('unknown','other','UNCERTAIN')")
    elif block=='prior-admin':db.execute('INSERT INTO autonomy_calls VALUES(?,?,?)',('review',boot.CHANGE,'FAILED'))
    elif block=='missing':db.execute('DELETE FROM autonomy_calls')
    elif block=='nonterminal':monkeypatch.setattr(boot,'stopped',lambda unit:(_ for _ in ()).throw(ValueError('NOT_TERMINAL')))
    else:rec.terminal=lambda *args:(_ for _ in ()).throw(ValueError('NATIVE_CHANGED'))
    before=list(db.iterdump())
    with pytest.raises(ValueError):boot.exceptions(db,None,rec,verify,lambda b:{'native':'pin'})
    assert list(db.iterdump())==before
