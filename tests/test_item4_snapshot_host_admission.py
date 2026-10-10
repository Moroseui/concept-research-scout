"""Execute the actual embedded host-start predicate against real SQLite fixtures."""
import ast,json,sqlite3,subprocess
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import item4_smoke_response as helper,manual_recovery

ROOT=Path(__file__).parents[1]

def predicate(raw):
    outer=ast.parse(raw)
    fn=next(n for n in outer.body if isinstance(n,ast.FunctionDef) and n.name=='starting_state')
    child=next(n.value.value for n in fn.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='child' for t in n.targets))
    tree=ast.parse(child)
    block=next(n for n in tree.body if isinstance(n,ast.With))
    start=next(i for i,n in enumerate(block.body) if isinstance(n,ast.Assert) and ast.unparse(n.test)=="stage == 'author'")
    return compile(ast.Module(body=block.body[start:],type_ignores=[]),'actual-host-start-predicate','exec')

@pytest.fixture
def state(monkeypatch):
    local=sqlite3.connect(':memory:');batch=sqlite3.connect(':memory:')
    local.execute('CREATE TABLE manual_calls(id TEXT)');batch.execute('CREATE TABLE autonomy_calls(id TEXT,status TEXT)')
    local.executemany('INSERT INTO manual_calls VALUES(?)',[(str(n),) for n in range(36)])
    p=json.loads((ROOT/helper.SNAPSHOT_DOCUMENT).read_bytes())
    data=dict(stage='author',value={'phase':'run_spec_author'},helper=helper,frozen=p,db=local,
        global_db=batch,store=NS(db=local,batch=NS(db=batch)),source='test-source',report='test-review',json=json)
    monkeypatch.setattr(manual_recovery,'role_limit',lambda *args:22)
    yield data
    local.close();batch.close()

def test_actual_host_gate_accepts_new_count_and_role(state):
    exec(predicate((ROOT/'tools/item4_response_host_operation.py').read_bytes()),state)
    assert state['count']==36 and state['ident']==helper.call(state['frozen'],'author')

def test_original_approved_host_gate_reproduces_prelaunch_refusal(state):
    raw=subprocess.check_output(['git','show','0a19e3e3b3b7679f991ebc07710250c64099a2aa:tools/item4_response_host_operation.py'],cwd=ROOT)
    with pytest.raises(AssertionError):exec(predicate(raw),state)

@pytest.mark.parametrize('fault',['count35','count37','role21','role23','stage','phase','local-duplicate','global-duplicate','other-live-call'])
def test_all_other_host_admissions_still_refused(state,monkeypatch,fault):
    if fault=='count35':state['db'].execute("DELETE FROM manual_calls WHERE id='35'")
    elif fault=='count37':state['db'].execute("INSERT INTO manual_calls VALUES('extra')")
    elif fault.startswith('role'):monkeypatch.setattr(manual_recovery,'role_limit',lambda *args:int(fault[4:]))
    elif fault=='stage':state['stage']='reviewer'
    elif fault=='phase':state['value']['phase']='run_spec_review'
    elif fault=='local-duplicate':state['db'].execute("UPDATE manual_calls SET id=? WHERE id='0'",(helper.call(state['frozen'],'author'),))
    elif fault=='global-duplicate':state['global_db'].execute('INSERT INTO autonomy_calls VALUES(?,?)',(helper.call(state['frozen'],'author'),'COMPLETE'))
    else:state['global_db'].execute("INSERT INTO autonomy_calls VALUES('uncertain-other','RUNNING')")
    before=(list(state['db'].iterdump()),list(state['global_db'].iterdump()))
    with pytest.raises(AssertionError):exec(predicate((ROOT/'tools/item4_response_host_operation.py').read_bytes()),state)
    assert (list(state['db'].iterdump()),list(state['global_db'].iterdump()))==before
