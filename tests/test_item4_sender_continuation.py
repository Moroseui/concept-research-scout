"""Frozen author23 scope, actual sender boundary and actual host predicate."""
import ast,copy,json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import item4_smoke_response as helper,manual_recovery
from tools import item4_smoke_response_runtime as route
from test_item4_author17_feedback_runtime import sender
from test_item4_full_author_sender import full_sender
from test_item4_snapshot_host_admission import state,predicate
ROOT=Path(__file__).parents[1]

def frozen():return json.loads((ROOT/helper.SNAPSHOT_DOCUMENT).read_bytes())

def test_exact_scope_preserves_original_and_authority():
    p=frozen();old=helper.scope(p,'a'*64);q=helper.profile(p)
    assert (q['author'],q['count'],q['batch'],q['limit'],q['batch_limit'])==(23,37,75,41,79)
    assert old['rounds']=={'run_spec_author':21,'run_spec_review':15}
    assert old['pending']['round']==22 and old['pending']['id']==helper.SENDER_FAILED_CALL
    before=p['sender_recovery']['previous_scope']
    assert helper.profile(before)['author']==22
    assert p['native_failure']==before['native_failure'] and p['fixture_reference']==before['fixture_reference']
    assert set(p['local_calls'])-set(before['local_calls'])=={helper.SENDER_FAILED_CALL}

@pytest.mark.parametrize('key,value',[('author_attempt',22),('run_limit',42),('batch_limit',80),('automatic_retry',True),('execution_authorized',True),('diagnostic_micro_usd',25000001),('stage1_micro_usd',150000001)])
def test_other_scope_or_cap_refused(key,value):
    p=frozen();p[key]=value
    with pytest.raises(ValueError):helper.scope(p,'a'*64)

@pytest.mark.parametrize('fault',['changed-approval','missing-pending','changed-pending','accepted-round','missing-old-call'])
def test_original_failure_or_provenance_cannot_be_relabelled(fault):
    p=frozen()
    if fault=='changed-approval':p['sender_recovery']['previous_approval']='b'*64
    elif fault=='missing-old-call':p['local_calls'].pop(next(iter(p['sender_recovery']['previous_scope']['local_calls'])))
    else:
        value=json.loads(p['original_state'])
        if fault=='missing-pending':value.pop('pending')
        elif fault=='changed-pending':value['pending']['id']='c'*64
        else:value['rounds']['run_spec_author']=22
        p['original_state']=json.dumps(value);p['state_sha256']=helper.sha(p['original_state'].encode())
    with pytest.raises(ValueError):helper.scope(p,'a'*64)

@pytest.mark.parametrize('sender',[23],indirect=True)
def test_actual_sender23_uses_one_profile(full_sender):
    expected,command,calls,local,other,*_=full_sender
    before=(list(local.iterdump()),list(other.iterdump()))
    assert route.send(expected,'codex',command)=={'boundary':'COUNTED_NATIVE_SEND_READY'}
    assert len(calls)==1 and before==(list(local.iterdump()),list(other.iterdump()))

@pytest.mark.parametrize('sender',[23],indirect=True)
@pytest.mark.parametrize('number',[21,22,24])
def test_sender23_refuses_other_attempts(full_sender,number):
    expected,command,calls,local,other,*_=full_sender
    local.execute('UPDATE manual_calls SET attempt=?',(number,));local.commit()
    with pytest.raises(ValueError):route.send(expected,'codex',command)
    assert not calls

def test_actual_host23_and_same_profile(state,monkeypatch):
    state['frozen']=frozen();state['db'].execute("INSERT INTO manual_calls VALUES('extra')")
    monkeypatch.setattr(manual_recovery,'role_limit',lambda *args:23)
    exec(predicate((ROOT/'tools/item4_response_host_operation.py').read_bytes()),state)
    assert state['count']==37 and state['ident']==helper.call(frozen(),'author')

@pytest.mark.parametrize('number',[22,24])
def test_host23_refuses_other_profile_roles(state,monkeypatch,number):
    state['frozen']=frozen();state['db'].execute("INSERT INTO manual_calls VALUES('extra')")
    monkeypatch.setattr(manual_recovery,'role_limit',lambda *args:number)
    with pytest.raises(AssertionError):exec(predicate((ROOT/'tools/item4_response_host_operation.py').read_bytes()),state)

def test_runtime_profile_drives_workspace_pins_and_round(monkeypatch):
    monkeypatch.setattr(route,'ROOT',ROOT);monkeypatch.setattr(route,'trusted',Path)
    assert route.author_round()==23 and route.author_work().name=='run_spec_author-23'
    assert route.pins_path().name=='runtime-pins-23.json'
    assert route.active_profile()['folder']==helper.profile(frozen())['folder']
    tree=ast.parse((ROOT/'tools/item4_smoke_response_runtime.py').read_bytes())
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    # All six independent scope callers use the same function rather than literals.
    names={n.func.id for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)}
    assert 'author_round' in names
    assert not any(isinstance(n,ast.Constant) and type(n.value) is int and n.value in (21,22,23) for n in ast.walk(fn))

def test_host_and_installer_target_the_same_release(monkeypatch):
    from tools import item4_response_host_operation as host,install_item4_smoke_response as installer
    assert host.CHANGE==installer.CHANGE==route.CHANGE=='item4-driver-round-repair-20261010'
    assert host.UNIT==installer.UNIT.name=='research-'+route.CHANGE+'.service'
    assert host.ENTRY==route.ROOT/route.FILES[0]
    captured=[]
    def command(argv):
        captured.append(argv)
        child=argv[argv.index('-c')+1]
        compile(child,'actual-host-authority-child','exec')
        assert 'p=Path(entry)' in child and 'source,report,entry=sys.argv[1:]' in child
        assert argv[-1]==str(host.ENTRY) and argv[-2]=='a'*64 and argv[-3]=='b'*40
        return '{"status":"CAPTURED_ONLY"}'
    monkeypatch.setattr(host,'command',command)
    assert host.starting_state({}, {'source_sha':'b'*40,'report_sha256':'a'*64})=={'status':'CAPTURED_ONLY'}
    assert len(captured)==1
