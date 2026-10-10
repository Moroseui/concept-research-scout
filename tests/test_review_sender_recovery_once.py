"""Exact terminal classification only; originals and accounting stay unchanged."""
import json,sqlite3
from pathlib import Path
import pytest
from tools import review_sender_recovery_once as boot

@pytest.fixture
def case(tmp_path,monkeypatch):
    work=tmp_path/'work';work.mkdir();(work/'.author-runtime').mkdir()
    files={'console.log':b'exact-preserved-trace','transport.log':b'transport','stage_provenance.jsonl':b'provenance'}
    for n,raw in files.items():(work/n).write_bytes(raw)
    (work/'.author-runtime/config.json').write_bytes(b'bound-config')
    src=tmp_path/'source.py';src.write_bytes(b'bound-source')
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE autonomy_calls(id TEXT,kind TEXT,change_id TEXT,status TEXT)')
    db.execute("INSERT INTO autonomy_calls VALUES('exact','scientific','original-run','UNCERTAIN')")
    row=dict(db.execute('SELECT * FROM autonomy_calls').fetchone())
    binding={'call_id':'exact','row_sha256':boot.sha(json.dumps(row,sort_keys=True).encode()),'workspace':str(work),'files':{n:boot.sha(v) for n,v in files.items()},'config_sha256':boot.sha(b'bound-config'),'source_path':str(src),'source_sha256':boot.sha(b'bound-source'),'unit':'exact.service','invocation':'exact-invocation'}
    monkeypatch.setattr(boot,'trusted',Path)
    state={'LoadState':'loaded','ActiveState':'failed','MainPID':'0','ControlGroup':'','ExecMainStatus':'1','InvocationID':'exact-invocation'}
    monkeypatch.setattr(boot.subprocess,'check_output',lambda *a,**k:'\n'.join(k+'='+v for k,v in state.items()))
    def original(*args):raise ValueError('UNKNOWN_CALL_REFUSED')
    return db,binding,original,state,work,src

def invoke(case):
    db,binding,original,*_=case
    return boot.exceptions(db,None,binding,original,lambda p:p.read_bytes())

def test_exact_terminal_qualifies_once_without_edits(case):
    db,*_=case;before=list(db.iterdump());v=invoke(case)
    assert v[0]['classification']=='EXACT_TERMINAL_PRE_SDK_AUTHOR22_ADMIN_ONLY'
    assert list(db.iterdump())==before

@pytest.mark.parametrize('fault',['running','changed-row','missing','unknown','prior-call','live-pid','active','changed-invocation','controlgroup','exit','native','config','source','submission','sent-input','output'])
def test_refuses_changed_uncertain_or_second_request(case,fault):
    db,binding,original,state,work,src=case
    if fault=='running':db.execute("UPDATE autonomy_calls SET status='RUNNING'")
    elif fault=='changed-row':db.execute("UPDATE autonomy_calls SET change_id='other'")
    elif fault=='missing':db.execute('DELETE FROM autonomy_calls')
    elif fault=='unknown':db.execute("INSERT INTO autonomy_calls VALUES('unknown','scientific','other','UNCERTAIN')")
    elif fault=='prior-call':db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?)',('review','implementation_review',boot.CHANGE,'FAILED'))
    elif fault=='live-pid':state['MainPID']='99'
    elif fault=='active':state['ActiveState']='active'
    elif fault=='changed-invocation':state['InvocationID']='different'
    elif fault=='controlgroup':state['ControlGroup']='not-empty'
    elif fault=='exit':state['ExecMainStatus']='0'
    elif fault=='native':(work/'console.log').write_bytes(b'changed')
    elif fault=='config':(work/'.author-runtime/config.json').write_bytes(b'changed')
    elif fault=='source':src.write_bytes(b'changed')
    else:(work/{'submission':'.author-submission.json','sent-input':'sent-input.json','output':'SPEC.proposed.md'}[fault]).write_bytes(b'new')
    before=list(db.iterdump())
    with pytest.raises(ValueError):invoke(case)
    assert list(db.iterdump())==before
