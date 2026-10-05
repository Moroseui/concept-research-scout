"""Native CLI/tick dispatch boundaries; all provider/admin effects are replaced."""
import json
import sqlite3
import sys
from types import SimpleNamespace
import pytest
from orchestrator import handover_runtime as hr, disposition_successors as ds

TASK='a'*64
SOURCE='b'*40
REF={'request_id':'c'*64,'applied_event':'d'*64}
BY={'kind':'agent','family':'codex','model':'gpt-6-astra','session_id':'synthetic-routing-check'}


def arguments(operation,extra=()):
    return ['runtime','--config','/synthetic/controller.json',operation,*extra]


def request_arguments(*extra):
    return arguments('disposition-request',[TASK,'--reason','Preserve original discussion.',
        '--expected-source',SOURCE,'--change-request',REF['request_id'],'--applied-event',REF['applied_event'],*extra])


@pytest.fixture
def cli(monkeypatch):
    config={'source':SOURCE,'controller_uid':997,'state':'/synthetic/state'}
    monkeypatch.setattr(hr,'configuration',lambda path:config)
    def fail(*args,**kwargs):raise AssertionError('Unexpected provider or inline workflow')
    monkeypatch.setattr(hr,'request_broker',fail)
    return config


def test_root_human_request_uses_fixed_attribution_without_inline_runtime(cli,monkeypatch,capsys):
    monkeypatch.setattr(hr.os,'getuid',lambda:0)
    monkeypatch.setattr(hr,'Runtime',lambda config:pytest.fail('Root request must use controller transport'))
    seen=[]
    def transport(*args,**kwargs):seen.append((args,kwargs));return {'status':'QUEUED','models':0}
    monkeypatch.setattr(hr,'controller_command',transport)
    monkeypatch.setattr(sys,'argv',request_arguments('--human'))
    hr.main()
    assert json.loads(capsys.readouterr().out)['status']=='QUEUED'
    args,kwargs=seen[0]
    assert args[1:4]==('disposition-request','/synthetic/controller.json',TASK)
    assert args[4]=={'kind':'human','identity':'ssh-uid:0','identity_source':'authenticated_root_transport_declared_human'}
    assert kwargs['replacement']=={'reason':'Preserve original discussion.','expected_source':SOURCE,'change_request':REF}


def test_nonroot_request_reaches_saved_request_api_with_explicit_actor(cli,monkeypatch,capsys):
    monkeypatch.setattr(hr.os,'getuid',lambda:997)
    runtime=SimpleNamespace(config=cli)
    monkeypatch.setattr(hr,'Runtime',lambda config:runtime)
    seen=[]
    def request(*args,**kwargs):seen.append((args,kwargs));return {'status':'QUEUED','models':0}
    monkeypatch.setattr(ds,'request',request)
    monkeypatch.setattr(sys,'argv',request_arguments('--submitter',json.dumps(BY)))
    hr.main()
    assert json.loads(capsys.readouterr().out)['models']==0
    assert seen==[((runtime,TASK),{'by':BY,'reason':'Preserve original discussion.','expected_source':SOURCE,'change_request':REF})]


@pytest.mark.parametrize('extra',[[],['--human'],['--submitter',json.dumps(BY),'--previous-request','e'*64]])
def test_nonroot_missing_attribution_or_retry_argument_refuses(cli,monkeypatch,extra):
    monkeypatch.setattr(hr.os,'getuid',lambda:997)
    monkeypatch.setattr(hr,'Runtime',lambda config:pytest.fail('Must refuse before runtime'))
    monkeypatch.setattr(sys,'argv',request_arguments(*extra))
    with pytest.raises(ValueError):hr.main()


@pytest.mark.parametrize('operation',['disposition-status','disposition-recover'])
def test_root_read_and_original_recovery_use_controller_transport(cli,monkeypatch,operation,capsys):
    monkeypatch.setattr(hr.os,'getuid',lambda:0)
    seen=[]
    monkeypatch.setattr(hr,'controller_command',lambda *args,**kw:seen.append(args) or {'status':'ORIGINAL_READ','models':0})
    monkeypatch.setattr(hr,'Runtime',lambda config:pytest.fail('Root must use controller transport'))
    monkeypatch.setattr(sys,'argv',arguments(operation,[TASK] if operation.endswith('recover') else []))
    hr.main()
    assert seen[0][1]==operation
    assert json.loads(capsys.readouterr().out)['models']==0


def test_controller_transport_preserves_exact_repair_and_agent_fields(cli,monkeypatch):
    import pwd
    monkeypatch.setattr(hr.os,'getuid',lambda:0)
    monkeypatch.setattr(pwd,'getpwuid',lambda uid:SimpleNamespace(pw_name='research-controller'))
    monkeypatch.setattr(hr,'checked_source',lambda *args:None)
    cli.update(source_root='/synthetic/source',controller_gid=987)
    seen=[]
    monkeypatch.setattr(hr.subprocess,'run',lambda cmd,**kw:seen.append((cmd,kw)) or SimpleNamespace(stdout=b'{"status":"QUEUED"}'))
    spec={'reason':'Preserve original discussion.','expected_source':SOURCE,'change_request':REF}
    assert hr.controller_command(cli,'disposition-request',task_id=TASK,submitted_by=BY,replacement=spec)['status']=='QUEUED'
    cmd,kwargs=seen[0]
    assert cmd[cmd.index('--reason')+1]==spec['reason']
    assert json.loads(cmd[cmd.index('--submitter')+1])==BY
    assert cmd[cmd.index('--applied-event')+1]==REF['applied_event']
    assert '--previous-request' not in cmd
    assert kwargs['timeout']==60 and kwargs['check'] is True


def tick_fixture(monkeypatch,queue_result,successor):
    db=sqlite3.connect(':memory:')
    db.execute('CREATE TABLE runtime_blocks(phase TEXT PRIMARY KEY, reason TEXT)')
    calls=[]
    empty=lambda:None
    runtime=SimpleNamespace(q=SimpleNamespace(db=db,tick=lambda:queue_result),controls=empty,
        recover=empty,completions=None,scheduled_research=empty,scheduled_report=lambda now:None,
        bookkeeping=empty,deliver_reports=empty,notifications=empty,
        continuing_step=lambda:calls.append('continuing') or {'status':'EXISTING_WORK_ADVANCED'})
    monkeypatch.setattr('orchestrator.continuing_operations.discover',lambda runtime:None)
    monkeypatch.setattr('orchestrator.investigator_wakes.discover',lambda runtime:None)
    def advance(runtime):
        calls.append('disposition')
        if isinstance(successor,Exception):raise successor
        return successor
    monkeypatch.setattr(ds,'advance',advance)
    return runtime,calls,db


@pytest.mark.parametrize('queue_status',['STAGE_COMPLETE','PAUSED','RUNNING'])
def test_tick_never_adds_successor_to_existing_work_or_pause(monkeypatch,queue_status):
    runtime,calls,db=tick_fixture(monkeypatch,{'status':queue_status},{'status':'COMPLETE'})
    try:assert hr.Runtime.tick(runtime)=={'status':queue_status};assert calls==[]
    finally:db.close()


@pytest.mark.parametrize('successor_status',['COMPLETE','PAUSED','RECONCILIATION_REQUIRED'])
def test_successor_nonidle_result_prevents_second_model_work(monkeypatch,successor_status):
    runtime,calls,db=tick_fixture(monkeypatch,{'status':'WAITING_FOR_ELIGIBLE_WORK'},{'status':successor_status})
    try:assert hr.Runtime.tick(runtime)=={'status':successor_status};assert calls==['disposition']
    finally:db.close()


def test_only_exact_successor_idle_allows_normal_existing_work(monkeypatch):
    runtime,calls,db=tick_fixture(monkeypatch,{'status':'WAITING_FOR_ELIGIBLE_WORK'},{'status':'NO_QUEUED_DISPOSITION_SUCCESSOR'})
    try:assert hr.Runtime.tick(runtime)=={'status':'EXISTING_WORK_ADVANCED'};assert calls==['disposition','continuing']
    finally:db.close()


def test_successor_refusal_records_runtime_block_without_fallthrough(monkeypatch):
    runtime,calls,db=tick_fixture(monkeypatch,{'status':'WAITING_FOR_ELIGIBLE_WORK'},ValueError('PRESERVED_REFUSAL'))
    try:
        assert hr.Runtime.tick(runtime)['status']=='SAVED_DISPOSITION_REQUIRES_RECONCILIATION'
        assert calls==['disposition']
        assert db.execute('SELECT phase FROM runtime_blocks').fetchall()==[('disposition-successors',)]
    finally:db.close()
