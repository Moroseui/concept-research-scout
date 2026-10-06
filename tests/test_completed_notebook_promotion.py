"""Synthetic SQLite connections; frozen-prior checks stubbed only in unit fixture.

Live read-only preflight separately exercises both real checkpoint verifiers.
"""
import json
import sqlite3
from pathlib import Path
import pytest
from orchestrator import notebook_revision_transition as n, analysis_revision_transition as a
from tools.deploy_manual_lane import bound


def put(root, name, value):
    p=bound(root,name);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value));return p


@pytest.fixture
def completed(tmp_path,monkeypatch):
    root=tmp_path;run='synthetic-run'
    old='/var/lib/research-system-manual-sprint10/releases/four/lane'
    first='/var/lib/research-system-manual-sprint10/releases/two/lane'
    latest='/var/lib/research-system-manual-sprint10/releases/final/lane'
    checkpoint={'run_id':run,'old_state':old,'call_rows':['one','two']}
    monkeypatch.setattr(n,'checkpoint',lambda:checkpoint)
    monkeypatch.setattr(a,'checkpoint',lambda:{'run_id':run,'old_state':first})
    verified=[]
    monkeypatch.setattr(n,'prior',lambda host,completed=False:(verified.append(('four',completed)) or ({'revision_continuation':a.KEY},{})))
    monkeypatch.setattr(a,'prior',lambda host,completed=False:verified.append(('two',completed)))
    import tools.deploy_manual_lane as deploy
    monkeypatch.setattr(deploy,'system',lambda *args:{'enabled':False,'active':False})
    cfg={'source':'a'*40,'run_id':run,'item_number':2,'notebook_revision_continuation':n.KEY}
    put(root,latest+'/lane.json',cfg)
    binding={'kind':n.KEY,'run_id':run,'source':cfg['source'],'state':latest,'filesystem_root':'/',
       'config_sha256':n.sha(cfg),'checkpoint_sha256':n.CHECKPOINT,'operator_decision_sha256':n.AUTHORITY,
       'preserved_call_ids':checkpoint['call_rows'],'allowance_reset':False}
    put(root,latest+'/notebook-continuation.json',binding)
    prior={'kind':a.KEY,'synthetic':True};put(root,old+'/revision-continuation.json',prior)
    put(root,latest+'/REPORT.md',{'synthetic':'accepted report'})
    report=n.digest(bound(root,latest+'/REPORT.md').read_bytes())
    ledger=bound(root,'/var/lib/research-system-autonomy/reviews/jobs.sqlite');ledger.parent.mkdir(parents=True)
    with sqlite3.connect(ledger) as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('CREATE TABLE events(id TEXT PRIMARY KEY,job TEXT,payload TEXT)')
        db.execute('CREATE TABLE autonomy_runs(id TEXT PRIMARY KEY,status TEXT)')
        db.execute('INSERT INTO autonomy_runs VALUES(?,?)',(run,'COMPLETE'))
        for key,payload in [(n.KEY,binding),(a.KEY,prior),(run+':accepted',{'report_sha256':report})]:
            db.execute('INSERT INTO events VALUES(?,?,?)',(key,run,json.dumps(payload)))
        db.execute('CREATE TABLE autonomy_calls(id TEXT,kind TEXT,change_id TEXT,status TEXT)')
        db.executemany('INSERT INTO autonomy_calls VALUES(?,?,?,?)',[(x,'scientific',run,'COMPLETE') for x in ['one','two','three']])
    for path,ids in [(old,['one','two']),(latest,['one','two','three'])]:
        target=bound(root,path);target.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(target/'jobs.sqlite') as db:
            db.execute('CREATE TABLE manual_calls(id TEXT PRIMARY KEY,status TEXT,receipt TEXT)')
            db.executemany('INSERT INTO manual_calls VALUES(?,?,?)',[(x,'COMPLETE','original-'+x) for x in ids])
            db.execute('CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT)')
            db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps({'phase':'COMPLETE'}),))
    return root,ledger,old,first,latest,verified


def change(dbpath,sql,args=()):
    with sqlite3.connect(dbpath) as db:db.execute(sql,args)


def test_completed_chain_closes_exact_predecessors_without_writes(completed):
    root,ledger,old,first,latest,verified=completed
    def snapshot():
        files={str(p):p.read_bytes() for p in root.rglob('*') if p.is_file() and 'jobs.sqlite' not in p.name}
        logical={}
        for p in root.rglob('jobs.sqlite'):
            with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as db:logical[str(p)]=list(db.iterdump())
        return files,logical
    before=snapshot()
    assert n.completed_predecessors(root)=={bound(root,old),bound(root,first)}
    assert verified==[('four',True),('two',True)]
    assert snapshot()==before


@pytest.mark.parametrize('damage,code',[
 ('acceptance','ACCEPTANCE_REQUIRED'),('report','REPORT_CHANGED'),('event-run','EVENT_RUN'),
 ('config','CONTINUATION_CHANGED'),('binding','CONTINUATION_CHANGED'),('reset','CONTINUATION_CHANGED'),
 ('prior-event','PREDECESSOR_EVENT_CHANGED'),('unfinished','NOT_TERMINAL'),
 ('uncertain','CALL_SET_CHANGED'),('missing-call','CALL_SET_CHANGED'),('receipt','COPIED_CALL_CHANGED')])
def test_closure_damage_refuses(completed,damage,code):
    root,ledger,old,first,latest,_=completed
    lane=bound(root,latest)
    if damage=='acceptance':change(ledger,"DELETE FROM events WHERE id LIKE '%:accepted'")
    elif damage=='report':(lane/'REPORT.md').write_text('changed')
    elif damage=='event-run':change(ledger,'UPDATE events SET job=? WHERE id=?',('unrelated',n.KEY))
    elif damage=='config':
        v=json.loads((lane/'lane.json').read_text());v['source']='b'*40;put(root,latest+'/lane.json',v)
    elif damage in ('binding','reset'):
        v=json.loads((lane/'notebook-continuation.json').read_text());v['allowance_reset']=True
        put(root,latest+'/notebook-continuation.json',v)
        if damage=='reset':change(ledger,'UPDATE events SET payload=? WHERE id=?',(json.dumps(v),n.KEY))
    elif damage=='prior-event':change(ledger,'UPDATE events SET payload=? WHERE id=?',('{}',a.KEY))
    elif damage=='unfinished':change(lane/'jobs.sqlite','UPDATE manual_state SET payload=?',(json.dumps({'phase':'BLOCKED'}),))
    elif damage=='uncertain':change(ledger,"UPDATE autonomy_calls SET status='UNCERTAIN' WHERE id='three'")
    elif damage=='missing-call':change(lane/'jobs.sqlite',"DELETE FROM manual_calls WHERE id='three'")
    elif damage=='receipt':change(lane/'jobs.sqlite',"UPDATE manual_calls SET receipt='changed' WHERE id='one'")
    with pytest.raises(ValueError,match='^NOTEBOOK_CLOSURE_'+code+'$'):n.completed_predecessors(root)


def test_incomplete_run_never_closes_predecessors(completed):
    root,ledger,*_=completed
    change(ledger,"UPDATE autonomy_runs SET status='ACTIVE'")
    assert n.completed_predecessors(root)==set()


def test_real_checkpoint_failure_propagates(completed,monkeypatch):
    def fail(*args,**kwargs):raise ValueError('NOTEBOOK_OLD_ROWS_CHANGED:manual_calls')
    monkeypatch.setattr(n,'prior',fail)
    with pytest.raises(ValueError,match='^NOTEBOOK_OLD_ROWS_CHANGED:manual_calls$'):n.completed_predecessors(completed[0])


def test_active_predecessor_service_refuses(completed,monkeypatch):
    import tools.deploy_manual_lane as deploy
    monkeypatch.setattr(deploy,'system',lambda *args:{'enabled':False,'active':True})
    with pytest.raises(ValueError,match='^NOTEBOOK_CLOSURE_UNITS_NOT_HELD$'):n.completed_predecessors(completed[0])
