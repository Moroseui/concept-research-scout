"""Format feedback cannot launch an unadmitted author; synthetic records only."""
import json,sqlite3
from pathlib import Path
import pytest
from tools import item4_smoke_response_runtime as route
from orchestrator import item4_smoke_response as helper

@pytest.fixture
def sender(tmp_path,monkeypatch):
    lane=tmp_path/'lane';lane.mkdir();work=tmp_path/'lane-scientific-workspaces/run_spec_author-18';work.mkdir(parents=True)
    monkeypatch.setattr(route,'author_work',lambda:work)
    ident=helper.call({'schema':helper.NATIVE_SCHEMA},'author');expected='a'*64
    config={'bindings':{'call_id':ident,'round':18,'stage':'run_spec_author','run_id':helper.RUN,'input_sha256':expected}}
    pending={'id':ident,'stage':'run_spec_author','round':18,'workspace':str(work)}
    local=sqlite3.connect(lane/'jobs.sqlite');local.execute('CREATE TABLE manual_calls(id TEXT,status TEXT,stage TEXT,attempt INTEGER,receipt TEXT)')
    local.execute('CREATE TABLE manual_state(id INTEGER,payload TEXT)')
    local.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(ident,'RUNNING','run_spec_author',18,json.dumps({'input_sha256':expected,'workspace':str(work)})))
    local.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps({'phase':'MODEL_RUNNING','pending':pending}),));local.commit()
    other=sqlite3.connect(tmp_path/'global.sqlite');other.execute('CREATE TABLE autonomy_calls(id TEXT,status TEXT)');other.execute('INSERT INTO autonomy_calls VALUES(?,?)',(ident,'RUNNING'));other.commit()
    (lane/'jobs.sqlite').chmod(0o600);(tmp_path/'global.sqlite').chmod(0o600)
    original=sqlite3.connect
    def connect(database,*args,**kwargs):
        if database=='file:/var/lib/research-system-autonomy/reviews/jobs.sqlite?mode=ro':database=(tmp_path/'global.sqlite').as_uri()+'?mode=ro'
        return original(database,*args,**kwargs)
    monkeypatch.setattr(sqlite3,'connect',connect)
    yield config,expected,local,other,pending
    local.close();other.close()


def test_sender_requires_matching_dual_admission(sender):
    config,expected,*_=sender
    route.author_sender_admitted(config,expected)


@pytest.mark.parametrize('fault',['local-missing','global-missing','local-complete','global-uncertain','pending','input','wrong-call'])
def test_sender_refuses_without_mutating_admissions(sender,fault):
    config,expected,local,other,pending=sender
    if fault=='local-missing':local.execute('DELETE FROM manual_calls')
    elif fault=='global-missing':other.execute('DELETE FROM autonomy_calls')
    elif fault=='local-complete':local.execute("UPDATE manual_calls SET status='COMPLETE'")
    elif fault=='global-uncertain':other.execute("UPDATE autonomy_calls SET status='UNCERTAIN'")
    elif fault=='pending':local.execute('UPDATE manual_state SET payload=?',(json.dumps({'phase':'run_spec_author','pending':pending}),))
    elif fault=='input':expected='f'*64
    else:config['bindings']['call_id']='f'*64
    local.commit();other.commit()
    before=(list(local.iterdump()),list(other.iterdump()))
    with pytest.raises(ValueError):route.author_sender_admitted(config,expected)
    assert (list(local.iterdump()),list(other.iterdump()))==before
