"""Exercise the real send entry, format pins, dual ledgers and protection assembly.
Only installed identity/bootstrap and final process boundary are substituted.
No native subprocess, network, credentials or live ledger is used.
"""
import ast,json,subprocess
from pathlib import Path
from types import SimpleNamespace
import pytest
from test_item4_author17_feedback_runtime import sender
from tools import item4_smoke_response_runtime as route
from orchestrator import author_format_submission as af,manual_stage as stage

@pytest.fixture
def full_sender(sender,monkeypatch):
    config,expected,local,other,pending=sender
    work=route.author_work();binding={**config['bindings'],'source_sha':'b'*40,'runtime_sha256':'c'*64}
    revision={k:'d'*64 for k in ('review_call_id','review_sha256','operator_scope_sha256','original_sha256','view_sha256')}
    pins=af.prepare_revision(work,binding,revision)
    pinpath=work.parent.parent/'pins.json';pinpath.write_text(json.dumps(pins));pinpath.chmod(0o600)
    monkeypatch.setattr(route,'pins_path',lambda:pinpath)
    monkeypatch.setattr(route,'os',SimpleNamespace(getuid=lambda:1003,getgid=lambda:1003))
    monkeypatch.setattr(route,'ROOT',Path(route.__file__).resolve().parents[1])
    monkeypatch.setattr(route,'connect',lambda:None)
    monkeypatch.chdir(work)
    command=af.client_command(['/tools/node','/tools/codex/bin/codex.js','exec','--ignore-user-config','--ignore-rules','--model','gpt-6-astra','-s','workspace-write','-c','approval_policy="never"','-c','sandbox_workspace_write.network_access=false','--json','-'],work,pins)
    calls=[]
    def no_process(*a,**k):raise AssertionError('NO_NATIVE_PROCESS_ALLOWED')
    monkeypatch.setattr(subprocess,'Popen',no_process)
    outer=['bwrap','--bind',str(work),'/workspace','--chdir','/workspace']
    original=lambda *a,**k:list(outer)
    monkeypatch.setattr(stage.isolation,'command',original)
    def sink(digest,argv,*,family):
        protected=stage.isolation.command(work)
        assert protected==af.protect_command(outer,work,pins)
        assert digest==expected and argv==command and family=='codex'
        calls.append((digest,argv));return {'boundary':'COUNTED_NATIVE_SEND_READY'}
    monkeypatch.setattr(stage,'send_bound',sink)
    return expected,command,calls,local,other,pending,pinpath,original


def test_full_sender_reaches_one_backend_boundary(full_sender):
    expected,command,calls,local,other,_,_,original=full_sender
    before=(list(local.iterdump()),list(other.iterdump()))
    assert route.send(expected,'codex',command)=={'boundary':'COUNTED_NATIVE_SEND_READY'}
    assert len(calls)==1 and stage.isolation.command is original
    assert before==(list(local.iterdump()),list(other.iterdump()))


def test_original_installed_send_reproduces_exact_failure(full_sender):
    expected,command,calls,*_=full_sender
    # Read an exact frozen old function, no git/subprocess inside a test.
    source=(Path(__file__).parents[1]/'docs/ITEM4_AUTHOR22_SEND_ORIGINAL_PRIVATE.py').read_text()
    ns=dict(vars(route));exec(compile(source,'preserved-installed-send','exec'),ns)
    with pytest.raises(ValueError,match='AUTHOR_SENDER_BINDING'):ns['send'](expected,'codex',command)
    assert calls==[]

@pytest.mark.parametrize('fault',['round21','round23','local-missing','global-missing','complete','uncertain','row-attempt','pending','input','config-pin','command','family'])
def test_full_sender_refuses_before_backend(full_sender,fault):
    expected,command,calls,local,other,pending,pinpath,original=full_sender
    family='codex'
    if fault in ('round21','round23'):
        number=int(fault[-2:]);p=route.author_work()/af.CONFIG;v=json.loads(p.read_bytes());v['bindings']['round']=number
        v['bindings']['call_id']=af.sha((v['bindings']['run_id']+':run_spec_author:'+str(number)).encode())
        p.write_bytes(af.canonical(v));pins=json.loads(pinpath.read_bytes());pins[af.CONFIG]=af.sha(p.read_bytes());pinpath.write_text(json.dumps(pins))
    elif fault=='local-missing':local.execute('DELETE FROM manual_calls')
    elif fault=='global-missing':other.execute('DELETE FROM autonomy_calls')
    elif fault=='complete':local.execute("UPDATE manual_calls SET status='COMPLETE'")
    elif fault=='uncertain':other.execute("UPDATE autonomy_calls SET status='UNCERTAIN'")
    elif fault=='row-attempt':local.execute('UPDATE manual_calls SET attempt=21')
    elif fault=='pending':local.execute('UPDATE manual_state SET payload=?',(json.dumps({'phase':'BLOCKED','pending':pending}),))
    elif fault=='input':expected='e'*64
    elif fault=='config-pin':(route.author_work()/af.CONFIG).write_bytes(b'{}')
    elif fault=='command':command=['bad']
    else:family='claude'
    local.commit();other.commit();before=(list(local.iterdump()),list(other.iterdump()))
    with pytest.raises(ValueError):route.send(expected,family,command)
    assert calls==[] and stage.isolation.command is original
    assert before==(list(local.iterdump()),list(other.iterdump()))
