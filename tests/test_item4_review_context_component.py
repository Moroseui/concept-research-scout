import json
import sqlite3
from types import SimpleNamespace
import pytest
from tools import item4_review_context_component as component
from tools import install_item4_review_context as installer
from tools import item4_submission_recovery_component as prior
from test_item4_submission_recovery_component import dump

@pytest.fixture
def saved(tmp_path,monkeypatch):
    from orchestrator import experiment_driver
    lane=tmp_path/'lane';lane.mkdir();state=tmp_path/'state';(state/'item4').mkdir(parents=True)
    (lane/'lane.json').write_text('{"unchanged":"configuration"}')
    value={'phase':'BLOCKED','blocked_stage':'run_spec_review','reason':'ValueError: SEARCH_DUPLICATE_BINDING','rounds':{'run_spec_author':5},'interventions':[]}
    raw=json.dumps(value)
    db=sqlite3.connect(lane/'jobs.sqlite',isolation_level=None);db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE manual_state(id INTEGER,payload TEXT)');db.execute('INSERT INTO manual_state VALUES(1,?)',(raw,))
    db.execute('CREATE TABLE manual_calls(id TEXT,status TEXT,receipt TEXT,stage TEXT)')
    globalpath=tmp_path/'global.sqlite';g=sqlite3.connect(globalpath,isolation_level=None);g.row_factory=sqlite3.Row
    g.execute('CREATE TABLE autonomy_calls(id TEXT,change_id TEXT,status TEXT,receipt TEXT)')
    for i in range(5):
        status='UNCERTAIN' if i in (0,4) else 'COMPLETE'
        db.execute('INSERT INTO manual_calls VALUES(?,?,?,?)',(str(i),status,'original charge','run_spec_author'))
        g.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?)',(str(i),prior.RUN,status,'original charge'))
    calls=[dict(x) for x in db.execute('SELECT * FROM manual_calls')];globals=[dict(x) for x in g.execute('SELECT * FROM autonomy_calls')]
    binding={'state_sha256':prior.sha(raw.encode()),'original_failure':value['reason'],'configuration_sha256':prior.sha((lane/'lane.json').read_bytes()),'calls_sha256':prior.sha(prior.canonical(calls)),'globals_sha256':prior.sha(prior.canonical(globals))}
    work=state/'item4/lane-scientific-workspaces/run_spec_review-1';work.mkdir(parents=True);(work/'prompt.md').write_text('preserved pre-admission original')
    binding['workspace_files']={'prompt.md':prior.sha((work/'prompt.md').read_bytes())}
    helper=SimpleNamespace(LANE=lane,STATE=state,RUN=prior.RUN,sha=prior.sha,canonical=prior.canonical,require=prior.require,grant=lambda *a:None)
    monkeypatch.setattr(component,'load',lambda:({'review_sha256':'c'*64},binding,helper,{},None))
    class Driver:
        def __init__(self,*a):self.store=SimpleNamespace(db=db,batch=SimpleNamespace(db=g))
        def guard(self):
            if (lane/'HALT').exists():raise ValueError('OPERATOR_HALT')
    monkeypatch.setattr(experiment_driver,'ExperimentDriver',Driver)
    return lane,globalpath,state/'item4'/component.CHANGE


def test_exact_context_continuation_preserves_every_charge(saved):
    lane,globalpath,dest=saved
    before=dump(globalpath)
    with sqlite3.connect(lane/'jobs.sqlite') as db:calls=db.execute('SELECT * FROM manual_calls').fetchall()
    assert component.apply()=={'status':'READY_NO_MODEL_CALL','model_calls':0,'limit_unchanged':200000}
    assert dump(globalpath)==before
    with sqlite3.connect(lane/'jobs.sqlite') as db:
        assert db.execute('SELECT * FROM manual_calls').fetchall()==calls
        state=json.loads(db.execute('SELECT payload FROM manual_state').fetchone()[0])
    assert state['phase']=='run_spec_review' and state['rounds']=={'run_spec_author':5}
    assert 'blocked_stage' not in state and state['reason'] is None
    assert (dest/'failed-pre-admission-workspace/prompt.md').read_text()=='preserved pre-admission original'
    assert not (dest.parent/'lane-scientific-workspaces/run_spec_review-1').exists()
    with sqlite3.connect(dest/'before.sqlite') as db:assert json.loads(db.execute('SELECT payload FROM manual_state').fetchone()[0])['phase']=='BLOCKED'

@pytest.mark.parametrize('damage',['halt','state','configuration','local-charge','global-charge','running','already','workspace-changed','workspace-symlink','review-exists'])
def test_other_blocks_and_uncertainty_refused_without_changes(saved,damage):
    lane,globalpath,dest=saved
    if damage=='halt':(lane/'HALT').touch()
    elif damage=='state':
        with sqlite3.connect(lane/'jobs.sqlite') as db:db.execute("UPDATE manual_state SET payload='{}'")
    elif damage=='configuration':(lane/'lane.json').write_text('{}')
    elif damage=='local-charge':
        with sqlite3.connect(lane/'jobs.sqlite') as db:db.execute("UPDATE manual_calls SET status='COMPLETE' WHERE id='4'")
    elif damage=='global-charge':
        with sqlite3.connect(globalpath) as db:db.execute("UPDATE autonomy_calls SET receipt='changed' WHERE id='4'")
    elif damage=='running':
        with sqlite3.connect(globalpath) as db:db.execute("INSERT INTO autonomy_calls VALUES('elsewhere','other','RUNNING','preserved')")
    elif damage=='workspace-changed':(dest.parent/'lane-scientific-workspaces/run_spec_review-1/prompt.md').write_text('changed')
    elif damage=='workspace-symlink':
        p=dest.parent/'lane-scientific-workspaces/run_spec_review-1/link';p.symlink_to('/etc/hosts')
    elif damage=='review-exists':
        with sqlite3.connect(lane/'jobs.sqlite') as db:db.execute("INSERT INTO manual_calls VALUES('review','RUNNING','charge','run_spec_review')")
    else:dest.mkdir()
    before,globalbefore=dump(lane/'jobs.sqlite'),dump(globalpath)
    with pytest.raises((ValueError,KeyError)):component.apply()
    assert dump(lane/'jobs.sqlite')==before and dump(globalpath)==globalbefore
    assert not (dest/'applied.json').exists()


def test_held_unit_retains_every_protection():
    original='User=partho\nGroup=partho\nExecStartPre=+/unchanged\nNoNewPrivileges=true\nProtectSystem=strict\nExecStart=/usr/bin/python3 -s -B /opt/research-system/manual-repair-helpers/item4-review-context-delivery-20261008/tools/item4_review_context_component.py run\n'
    actual=installer.unit_bytes(original).decode()
    assert [x for x in original.splitlines() if not x.startswith('ExecStart=')]==[x for x in actual.splitlines() if not x.startswith('ExecStart=')]
    assert 'item4_review_context_component.py run' in actual
    assert set(installer.FILES)==set(component.FILES)
    with pytest.raises(ValueError):installer.unit_bytes(original+original)
