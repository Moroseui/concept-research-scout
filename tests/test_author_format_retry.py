"""The exact once-only exception never becomes a general author allowance."""
import json
import sqlite3
from types import SimpleNamespace as NS
import pytest
from orchestrator import author_format_retry as retry


def fixture(count=7,phase='run_spec_author',reason=retry.REASON):
    db=sqlite3.connect(':memory:')
    db.execute('CREATE TABLE manual_calls(id TEXT,stage TEXT)')
    for n in range(count):db.execute('INSERT INTO manual_calls VALUES(?,?)',(str(n),'run_spec_author'))
    db.execute('CREATE TABLE manual_state(id INTEGER,payload TEXT)')
    db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps({'phase':phase,'reason':reason}),))
    return NS(db=db),{'run_id':'exact-approved-run'}


def test_only_next_call_gets_qualified_exception_without_scientific_slot(monkeypatch):
    store,b=fixture();seen=[]
    monkeypatch.setattr(retry,'qualify',lambda *a:seen.append(a))
    original=lambda *a:{'limit':7,'binding':None,'failed_attempts':5}
    before=store.db.total_changes
    result=retry.inspect(original,store,b['run_id'],'run_spec_author',b)
    assert result=={'limit':8,'binding':None,'failed_attempts':5}
    assert len(seen)==1 and store.db.total_changes==before
    store.db.execute('INSERT INTO manual_calls VALUES(?,?)',('8','run_spec_author'))
    assert retry.inspect(original,store,b['run_id'],'run_spec_author',b)==original()
    assert len(seen)==1


@pytest.mark.parametrize('change',['run','role','phase','reason','past','future'])
def test_other_work_keeps_original_guard(monkeypatch,change):
    store,b=fixture(count=6 if change=='past' else 8 if change=='future' else 7,
        phase='BLOCKED' if change=='phase' else 'run_spec_author',reason='REVISION_REQUIRED' if change=='reason' else retry.REASON)
    def forbidden(*a):raise AssertionError('unrelated state must not qualify')
    monkeypatch.setattr(retry,'qualify',forbidden)
    expected={'limit':4,'binding':None,'failed_attempts':5}
    assert retry.inspect(lambda *a:expected,store,'another' if change=='run' else b['run_id'],
        'run_spec_review' if change=='role' else 'run_spec_author',b) is expected


def test_failed_original_qualification_cannot_grant(monkeypatch):
    store,b=fixture()
    def refused(*a):raise ValueError('AUTHOR7_RECOVERY_CHANGED')
    monkeypatch.setattr(retry,'qualify',refused)
    with pytest.raises(ValueError,match='AUTHOR7_RECOVERY_CHANGED'):
        retry.inspect(lambda *a:{'limit':7,'binding':None},store,b['run_id'],'run_spec_author',b)
