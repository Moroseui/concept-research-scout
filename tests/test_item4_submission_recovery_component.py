import copy
import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace
import pytest
from tools import item4_submission_recovery_component as h
from tools import install_item4_submission_recovery as installer
from orchestrator import author_submission_recovery as rec


def dump(path):
    with sqlite3.connect(path) as db:return list(db.iterdump())

@pytest.fixture
def saved(tmp_path,monkeypatch):
    from orchestrator import experiment_driver,experiment_context
    lane=tmp_path/'lane';lane.mkdir();work=tmp_path/'work';work.mkdir();dest=tmp_path/'recovery'
    monkeypatch.setattr(h,'LANE',lane);monkeypatch.setattr(h,'WORK',work);monkeypatch.setattr(h,'DEST',dest)
    config={'run_id':h.RUN};(lane/'lane.json').write_text(json.dumps(config))
    value={'phase':'BLOCKED','reason':'MODEL_FAILED_OR_UNCERTAIN_NO_RETRY','rounds':{'run_spec_author':4},
        'pending':{'id':rec.CALL,'stage':'run_spec_author','round':5,'workspace':str(work)},'interventions':[]}
    raw=json.dumps(value)
    db=sqlite3.connect(lane/'jobs.sqlite',isolation_level=None);db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE manual_state(id INTEGER,payload TEXT)');db.execute('INSERT INTO manual_state VALUES(1,?)',(raw,))
    db.execute('CREATE TABLE manual_calls(id TEXT,stage TEXT,attempt INTEGER,status TEXT,receipt TEXT)')
    for i in range(1,6):db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',
        (rec.CALL if i==5 else 'original-'+str(i),'run_spec_author',i,'UNCERTAIN' if i in (1,5) else 'COMPLETE','preserved charge'))
    db.execute('CREATE TABLE manual_account(used INTEGER)');db.execute('INSERT INTO manual_account VALUES(5)')
    globaldb=sqlite3.connect(tmp_path/'global.sqlite',isolation_level=None);globaldb.row_factory=sqlite3.Row
    globaldb.execute('CREATE TABLE autonomy_calls(id TEXT,status TEXT,receipt TEXT)');globaldb.execute('INSERT INTO autonomy_calls VALUES(?,?,?)',(rec.CALL,'UNCERTAIN','preserved charge'))
    b={'state_sha256':h.sha(raw.encode())}
    evidence={'call':rec.CALL,'native_submission':'REFUSED_NO_RECEIPT'}
    recovery=SimpleNamespace(CALL=rec.CALL,binding=lambda:b)
    monkeypatch.setattr(h,'load',lambda:({'source':'b'*40,'review_sha256':'c'*64},recovery))
    monkeypatch.setattr(h,'check',lambda *args:evidence)
    class Driver:
        def __init__(self,*a):self.store=SimpleNamespace(db=db,batch=SimpleNamespace(db=globaldb));self.state=lane;self.config=config
        def guard(self):
            if (lane/'HALT').exists():raise ValueError('OPERATOR_HALT')
    monkeypatch.setattr(experiment_driver,'ExperimentDriver',Driver)
    def accept(driver,state,pending):
        assert state['rounds']['run_spec_author']==5 and pending==value['pending']
        # Represents the unchanged host validators/synthetic runner boundary.
        if (lane/'synthetic-failure').exists():raise ValueError('ORIGINAL_HOST_VALIDATOR_REFUSED')
        state.update(phase='run_spec_review',spec=str(work/'SPEC.proposed.md'))
    monkeypatch.setattr(experiment_context,'accept_author',accept)
    return lane,tmp_path/'global.sqlite',dest,work


def test_recovery_transitions_only_state_without_native_receipt_or_refunds(saved):
    lane,globalpath,dest,work=saved
    before=dump(globalpath)
    with sqlite3.connect(lane/'jobs.sqlite') as db:calls=db.execute('SELECT * FROM manual_calls').fetchall()
    assert h.apply()['status']=='READY_FOR_NORMAL_SCIENTIFIC_REVIEW'
    assert dump(globalpath)==before
    with sqlite3.connect(lane/'jobs.sqlite') as db:
        assert db.execute('SELECT * FROM manual_calls').fetchall()==calls
        assert db.execute('SELECT used FROM manual_account').fetchone()[0]==5
        state=json.loads(db.execute('SELECT payload FROM manual_state').fetchone()[0])
    assert state['phase']=='run_spec_review' and state['rounds']=={'run_spec_author':5} and 'pending' not in state
    assert not (work/'.author-submission.json').exists()
    assert json.loads((dest/'qualification.json').read_bytes())['native_submission']=='REFUSED_NO_RECEIPT'
    assert (dest/'before.sqlite').is_file()

@pytest.mark.parametrize('damage',['halt','state','already','host-validator'])
def test_block_or_partial_application_stays_closed(saved,damage):
    lane,globalpath,dest,work=saved
    before=dump(globalpath)
    if damage=='halt':(lane/'HALT').touch()
    elif damage=='state':
        with sqlite3.connect(lane/'jobs.sqlite') as db:db.execute("UPDATE manual_state SET payload='{}'")
    elif damage=='already':dest.mkdir()
    else:(lane/'synthetic-failure').touch()
    local_before=dump(lane/'jobs.sqlite')
    with pytest.raises(ValueError):h.apply()
    assert dump(lane/'jobs.sqlite')==local_before and dump(globalpath)==before
    assert not (dest/'applied.json').exists() and not (work/'.author-submission.json').exists()


@pytest.fixture
def admission(tmp_path,monkeypatch):
    from test_scoped_revisions_limits import configured,policy
    from orchestrator import manual_recovery as mr,experiment_driver,connectivity,experiment_timeout_continuation as timeout
    store,batch,config=configured(tmp_path,item=4,backend='modal')
    # This legacy fixture stubs its own attempt5 policy, not a genuine
    # execution selection. Do not claim the prospective revision policy here.
    config.pop('revision_policy')
    from orchestrator.private_records import atomic
    atomic(store.path.parent/'lane.json',config)
    monkeypatch.setattr(h,'RUN','synthetic');monkeypatch.setattr(h,'LANE',store.path.parent)
    monkeypatch.setattr(mr,'role_limit',lambda *args:5)
    ids=[]
    for i in range(5):
        ident,n,receipt=store.reserve_call('synthetic','run_spec_author','a'*40,'astra/manual-test',policy(),{})
        store.finish_call(ident,receipt,'COMPLETE');ids.append(ident)
    for ident in (ids[0],ids[-1]):
        store.db.execute("UPDATE manual_calls SET status='UNCERTAIN' WHERE id=?",(ident,))
        batch.db.execute("UPDATE autonomy_calls SET status='UNCERTAIN' WHERE id=?",(ident,))
    prior={'failed_id':ids[0],'stage':'terminal_author_continuation','decision_sha256':'b'*64,'runtime_source':'a'*40}
    monkeypatch.setattr(mr,'permit',lambda *args:prior)
    monkeypatch.setattr(timeout,'global_exception',lambda *args,**kwargs:ids[0])
    recovery=SimpleNamespace(CALL=ids[-1],binding=lambda:{'source':'a'*40})
    monkeypatch.setattr(h,'load',lambda:({'source':'b'*40,'review_sha256':'c'*64},recovery))
    monkeypatch.setattr(h,'grant',lambda *args:{})
    applied=tmp_path/'APPLIED.json';applied.write_text('{"status":"INSTALLED_HELD"}')
    monkeypatch.setattr(h,'trusted',lambda *args:applied)
    requested={'stage':'run_spec_review','source':'a'*40}
    class Driver:
        def __init__(self,*args):self.store=store
        def guard(self):pass
        def current(self):return {'phase':'run_spec_review'}
        def advance(self):
            ident,n,receipt=store.reserve_call('synthetic',requested['stage'],requested['source'],'astra/manual-test',policy(),{})
            return {'id':ident,'round':n,'receipt':receipt}
    monkeypatch.setattr(experiment_driver,'ExperimentDriver',Driver)
    return store,batch,requested,ids


def test_normal_review_admission_counts_once_preserves_five_attempts(admission):
    store,batch,requested,ids=admission;local=store.path;globalpath=batch.folder/'jobs.sqlite'
    before=[dict(x) for x in store.db.execute('SELECT * FROM manual_calls')]
    out=h.run();assert out['round']==1
    with sqlite3.connect(local) as db:
        db.row_factory=sqlite3.Row
        assert [dict(x) for x in db.execute('SELECT * FROM manual_calls ORDER BY rowid')][:5]==before
        assert db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==6
    with sqlite3.connect(globalpath) as db:
        assert db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==6
        assert db.execute('SELECT status FROM autonomy_calls WHERE id=?',(ids[-1],)).fetchone()[0]=='UNCERTAIN'


@pytest.mark.parametrize('block',['day','batch','run','author6','wrong-source','unknown-uncertain'])
def test_normal_admission_refusals_preserved(admission,block):
    from datetime import datetime,timezone
    from orchestrator import autonomy_limits as limits
    store,batch,requested,ids=admission;local=store.path;globalpath=batch.folder/'jobs.sqlite'
    day=datetime.now(timezone.utc).date().isoformat()
    if block in ('day','batch','run'):
        count={'day':limits.DAILY-5,'batch':limits.SCIENTIFIC_BATCH-5,'run':15}[block]
        if block=='run':
            for i in range(count):store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',('extra-'+str(i),'result_interpretation_review',i+1,'COMPLETE','{}'))
        else:
            for i in range(count):batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('extra-'+str(i),'implementation_review' if block=='day' else 'scientific','other',1,day if block=='day' else '2020-01-01','FAILED','{}','{}'))
    elif block=='author6':requested['stage']='run_spec_author'
    elif block=='wrong-source':requested['source']='f'*40
    else:batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('unknown','scientific','other',1,day,'UNCERTAIN','{}','{}'))
    before=dump(local);global_before=dump(globalpath)
    with pytest.raises(ValueError):h.run()
    assert dump(local)==before and dump(globalpath)==global_before


def test_installer_keeps_original_unit_protections_and_fixed_review_action():
    original='User=partho\nGroup=partho\nExecStartPre=+/unchanged\nNoNewPrivileges=true\nProtectSystem=strict\nExecStart=/usr/bin/python3 -s -B /opt/research-system/manual-repair-helpers/daily-limit-and-image-probe-20261007/tools/daily_limit_component.py 4\n'
    actual=installer.unit_bytes(original).decode()
    assert [x for x in original.splitlines() if not x.startswith('ExecStart=')]==[x for x in actual.splitlines() if not x.startswith('ExecStart=')]
    assert 'item4_submission_recovery_component.py run' in actual
    assert set(installer.FILES)==set(h.FILES)
