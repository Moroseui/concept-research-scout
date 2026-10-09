import hashlib
import subprocess
import sys
from types import SimpleNamespace
import pytest
from orchestrator import modal_fit_stdin as transport


def test_exact_large_unicode_payload_roundtrip():
    payload=('frozen metadata '+chr(945))*6000
    raw=payload.encode()
    source="from __future__ import annotations\nimport sys,hashlib\nprint(hashlib.sha256(sys.argv[1].encode()).hexdigest())"
    args=transport.arguments(sys.executable,source,raw)
    assert sum(map(len,args))<65536 and len(raw)>65536
    done=subprocess.run(args,input=raw,capture_output=True)
    assert done.returncode==0 and done.stdout.decode().strip()==hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize('sent',[b'',b'wrong',b'exact!'])
def test_corrupt_or_incomplete_stdin_never_executes_guard(sent):
    args=transport.arguments(sys.executable,"print('GUARD_EXECUTED')",b'exact')
    done=subprocess.run(args,input=sent,capture_output=True)
    assert done.returncode!=0 and b'GUARD_EXECUTED' not in done.stdout


def test_same_length_corruption_fails_hash_before_guard():
    args=transport.arguments(sys.executable,"print('GUARD_EXECUTED')",b'exact')
    done=subprocess.run(args,input=b'EXACT',capture_output=True)
    assert done.returncode!=0 and b'FIT_STDIN_HASH' in done.stderr and not done.stdout


def test_limits_are_not_relaxed():
    with pytest.raises(ValueError,match='PAYLOAD_BOUND'):
        transport.arguments(sys.executable,'pass',b'x'*120001)
    with pytest.raises(ValueError,match='SDK_ARGUMENT_BOUND'):
        transport.arguments(sys.executable,'#'+'x'*66000,b'x')
    with pytest.raises(SyntaxError):transport.arguments(sys.executable,'invalid !',b'x')


def test_send_is_single_exec_then_write_eof_drain():
    payload=b'exact';args=transport.arguments(sys.executable,'pass',payload);calls=[]
    stream=SimpleNamespace(write=lambda value:calls.append(('write',value)),
        write_eof=lambda:calls.append(('eof',)),drain=lambda:calls.append(('drain',)))
    def execute(*actual,**kw):
        calls.append(('exec',actual,kw));return SimpleNamespace(stdin=stream)
    receipt=transport.send(SimpleNamespace(exec=execute),args,payload,timeout=3600,
                           workdir='/tmp',stdout='same-out',stderr='same-err')
    assert calls[0]==('exec',args,{'timeout':3600,'workdir':'/tmp','stdout':'same-out','stderr':'same-err'})
    assert calls[1:]==[('write',payload),('eof',),('drain',)]
    assert receipt=={'schema':'fit-stdin-transport/v1','bytes':5,'sha256':hashlib.sha256(payload).hexdigest(),'eof':True}


@pytest.mark.parametrize('failure',['write','write_eof','drain'])
def test_send_failure_propagates_without_retry(failure):
    calls=[];payload=b'exact';args=transport.arguments(sys.executable,'pass',payload)
    def action(name):
        def call(*unused):
            calls.append(name)
            if name==failure:raise OSError('synthetic transport failure')
        return call
    stream=SimpleNamespace(**{name:action(name) for name in ('write','write_eof','drain')})
    def execute(*unused,**kw):calls.append('exec');return SimpleNamespace(stdin=stream)
    with pytest.raises(OSError):transport.send(SimpleNamespace(exec=execute),args,payload,
        timeout=3600,workdir='/tmp',stdout=None,stderr=None)
    assert calls==['exec','write','write_eof','drain'][:['write','write_eof','drain'].index(failure)+2]


def test_wrong_payload_binding_refuses_before_exec():
    args=transport.arguments(sys.executable,'pass',b'exact')
    def forbidden(*args,**kwargs):raise AssertionError('must not exec')
    with pytest.raises(ValueError,match='PAYLOAD_BINDING'):
        transport.send(SimpleNamespace(exec=forbidden),args,b'wrong',timeout=3600,
                       workdir='/tmp',stdout=None,stderr=None)
