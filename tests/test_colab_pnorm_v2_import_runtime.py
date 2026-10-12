import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import colab_pnorm_v2_import_runtime as r
from orchestrator import manual_host_guard

def test_runtime_accepts_only_the_single_missing_import(tmp_path,monkeypatch):
    monkeypatch.setattr(manual_host_guard,'trusted',lambda p:Path(p))
    base=tmp_path/'base';new=tmp_path/'new'
    for root in (base,new):(root/'orchestrator').mkdir(parents=True)
    old=b'from pathlib import Path'+bytes([10])+b'MARKER=7'+bytes([10])
    (base/'orchestrator/colab_pnorm_v2_feedback.py').write_bytes(old)
    fixed=old.replace(b'from pathlib import Path'+bytes([10]),b'from pathlib import Path'+bytes([10])+b'import json'+bytes([10]))
    (new/'orchestrator/colab_pnorm_v2_feedback.py').write_bytes(fixed)
    assert r.corrected_feedback(new,base).MARKER==7
    (new/'orchestrator/colab_pnorm_v2_feedback.py').write_bytes(fixed.replace(b'MARKER=7',b'MARKER=8'))
    with pytest.raises(ValueError,match='ONLY_MISSING_IMPORT_REPAIR'):
        r.corrected_feedback(new,base)
    (new/'orchestrator/colab_pnorm_v2_feedback.py').write_bytes(old)
    with pytest.raises(ValueError,match='ONLY_MISSING_IMPORT_REPAIR'):
        r.corrected_feedback(new,base)

def test_new_unit_changes_only_entry_original_stays_exact(tmp_path,monkeypatch):
    monkeypatch.setattr(manual_host_guard,'trusted',lambda p:Path(p))
    entry='tools/colab_pnorm_v2_runtime.py'
    old=('User=partho'+chr(10)+'ProtectSystem=strict'+chr(10)+'Restart=no'+chr(10)+
         'ExecStart=/usr/bin/python3 -s -B '+str(r.PRIOR/entry)+' run'+chr(10)+
         'ReadWritePaths=/fixed/work'+chr(10)).encode()
    unit=tmp_path/'original.service';unit.write_bytes(old)
    parent=NS(authority=lambda:None,metadata=lambda:({},{'unit':str(unit)}),ENTRY=entry)
    result=r.unit_bytes(parent)
    assert result.replace(str(r.ROOT/r.ENTRY).encode(),str(r.PRIOR/entry).encode())==old
    assert unit.read_bytes()==old

def test_actual_checkpoint_is_zero_call_and_source_pinned():
    root=Path(__file__).resolve().parents[1]
    raw=(root/'docs/PNORM_V2_FEEDBACK_IMPORT_PRIVATE.json').read_bytes()
    assert r.sha(raw)==r.FROZEN_PIN
    b=json.loads(raw)
    assert b['calls']==b['new_allowance']==0
    assert b['source']=='dd83f3c5c96d5f903aed40c4e56f8f2b27b39a8a'
    state=json.loads(b['state_row']['payload'])
    assert state['phase']=='run_spec_author' and state['rounds']=={}
    assert b['owner']['status']=='ACTIVE'
    assert r.ROOT!=r.BASE and r.UNIT!='research-colab-pnorm-v2-question-20261012.service'

@pytest.mark.parametrize('damage',[None,'config','state','local_call','global_call','owner'])
def test_checkpoint_checks_actual_rows_and_never_mutates(tmp_path,monkeypatch,damage):
    import sqlite3
    monkeypatch.setattr(manual_host_guard,'trusted',lambda p:Path(p))
    monkeypatch.setattr(r,'ROOT',tmp_path)
    (tmp_path/'docs').mkdir()
    lane=tmp_path/'lane';lane.mkdir()
    config={'run_id':'new-arm','source':'a'*40}
    raw=json.dumps(config).encode();(lane/'lane.json').write_bytes(raw)
    d=sqlite3.connect(':memory:');d.row_factory=sqlite3.Row
    d.executescript('CREATE TABLE manual_state(id INTEGER,payload TEXT); CREATE TABLE manual_calls(id TEXT);')
    g=sqlite3.connect(':memory:');g.row_factory=sqlite3.Row
    g.executescript('CREATE TABLE autonomy_calls(id TEXT,change_id TEXT); CREATE TABLE autonomy_runs(id TEXT,binding TEXT,status TEXT);')
    d.execute("INSERT INTO manual_state VALUES(1,'original')")
    g.execute("INSERT INTO autonomy_runs VALUES('new-arm','unchanged','ACTIVE')")
    b={'schema':'pnorm-v2-feedback-import/v1','calls':0,'new_allowance':0,'lane':str(lane),
       'run_id':'new-arm','source':config['source'],'config_sha256':r.sha(raw),
       'state_row':dict(d.execute('SELECT *FROM manual_state').fetchone()),
       'owner':dict(g.execute('SELECT *FROM autonomy_runs').fetchone())}
    frozen=json.dumps(b).encode();monkeypatch.setattr(r,'FROZEN_PIN',r.sha(frozen))
    (tmp_path/'docs/PNORM_V2_FEEDBACK_IMPORT_PRIVATE.json').write_bytes(frozen)
    driver=NS(state=lane,config=config,store=NS(db=d,batch=NS(db=g)))
    if damage=='config':(lane/'lane.json').write_text('{}')
    if damage=='state':d.execute("UPDATE manual_state SET payload='changed'")
    if damage=='local_call':d.execute("INSERT INTO manual_calls VALUES('original-attempt')")
    if damage=='global_call':g.execute("INSERT INTO autonomy_calls VALUES('original-attempt','new-arm')")
    if damage=='owner':g.execute("UPDATE autonomy_runs SET status='COMPLETE'")
    before=(list(d.iterdump()),list(g.iterdump()))
    if damage:
        with pytest.raises(ValueError):r.checkpoint(driver,initial=True)
    else:
        assert r.checkpoint(driver,initial=True)==b
    assert before==(list(d.iterdump()),list(g.iterdump()))
    d.close();g.close()
