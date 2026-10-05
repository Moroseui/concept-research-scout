"""Prospective input/revision fixtures; no provider, real ledger or installed use."""
from contextlib import nullcontext
from copy import deepcopy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from types import SimpleNamespace

import pytest
from orchestrator import disposition_successors as d, disposition_context as dc
from orchestrator import hosted_context as h, hosted_cycle as cycle, protected_disposition as pd
from orchestrator import dispatch_limiter as limiter
from test_disposition_context import chain
from test_selected_scientific_history import append
from test_disposition_successors import original
from test_dispatch_limiter import config as policy_config

SOURCE = 'a'*40
OLD_SOURCE = 'b'*40
TASK = 'a'*64
sha = lambda raw: hashlib.sha256(raw).hexdigest()
REAL_MEASUREMENT = d._measurement


def history_pair():
    _, before = chain()
    after = deepcopy(before)
    active = after['events'][1]['identity']
    new = append(after,'APPLIED',{'modification':'Current source input repair','checks':['synthetic'],
        'result_binding':{'source':SOURCE},'review_status':'PENDING',
        'supersedes_applied_events':[active]})
    append(after,'REVIEW',{'verdict':'APPROVE','applied_event':new['identity'],
        'rationale':'Synthetic approval does not erase prior criticism.','affected_results':['fixture'],
        'review_evidence':'Synthetic original approval fixture'})
    return before,after,new['identity']


@pytest.fixture
def system(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir(mode=0o700)
    for name in ('branch.lock','admission.lock'):
        (state/name).write_bytes(b'');(state/name).chmod(0o600)
    db=sqlite3.connect(state/'coordinator.sqlite')
    db.executescript('CREATE TABLE controls(singleton INTEGER,revision INTEGER,paused INTEGER);'
        'INSERT INTO controls VALUES(1,15,1);CREATE TABLE runtime_blocks(phase TEXT,reason TEXT);')
    db.commit();db.close()
    root=tmp_path/'source';(root/'orchestrator').mkdir(parents=True)
    (root/'orchestrator/hosted_context.py').write_text('LINKED_DISPOSITION_PRESENTATION_VERSION = 1\n')
    config={'state':str(state),'source':OLD_SOURCE,'source_root':str(root),
        'controller_uid':os.getuid(),'controller_gid':os.getgid(),'broker_socket':'synthetic'}
    before,after,newapp=history_pair()
    by={'kind':'agent','family':'codex','model':'synthetic','session_id':'fixture'}
    oldref={'request_id':before['request']['identity'],'applied_event':before['events'][1]['identity']}
    newref={**oldref,'applied_event':newapp}
    _,_,proof=original()
    monkeypatch.setattr(d,'_identity',lambda c:None)
    monkeypatch.setattr(d,'_change',lambda c,ref:deepcopy(before if c['source']==OLD_SOURCE else after))
    monkeypatch.setattr(d,'_proof',lambda *a:deepcopy(proof))
    monkeypatch.setattr(d,'_measurement',lambda *a:({'input_sha256':'c'*64},'d'*64))
    monkeypatch.setattr('orchestrator.remote_supervisor.checked_source',lambda root,source:Path(root))
    monkeypatch.setattr('orchestrator.campaign.require_no_human_stop',lambda *a:None)
    runtime=SimpleNamespace(config=config,deployment_status=lambda:None)
    monkeypatch.setattr(d,'_client',lambda r:lambda *a:pytest.fail('Unexpected registration transport'))
    d.request(runtime,TASK,by=by,reason='Preserve old request.',change_request=oldref,expected_source=OLD_SOURCE)
    base,old,_,_,pred=d._predecessor(config,TASK)
    originals={n:(base/n).read_bytes() for n in d.ORIGINAL_NAMES}
    config['source']=SOURCE

    class Store:
        def __init__(self):self.state=limiter.initial();self.pin='0'*40;self.writes=0
        def read(self):return self.pin,deepcopy(self.state)
        def cas(self,old,value):
            assert old==self.pin
            self.state=deepcopy(value);self.writes+=1;self.pin=sha(cycle.encoded(value))[:40];return True
    store=Store();policy=policy_config(48)
    policy['server_semantics']='OPERATOR_AUTHORIZED_V1'
    limiter.admit_server(store,policy,d._event('f'*64,SOURCE))
    broker=SimpleNamespace(config={'turn_root':str(tmp_path/'turns'),'sources':[OLD_SOURCE,SOURCE],
        'policy':policy},ledger=store,authentication=lambda:nullcontext())
    turns=Path(broker.config['turn_root']);turns.mkdir(mode=0o700)
    (turns/'branch.lock').write_bytes(b'');(turns/'branch.lock').chmod(0o600)
    monkeypatch.setattr(pd,'_require_root',lambda:None)
    monkeypatch.setattr('orchestrator.protected_scientific_jobs.controller_configuration',lambda b:config)
    calls=[]
    def client(socket,op,body):
        calls.append((op,deepcopy(body)))
        assert op=='disposition_unstarted'
        return pd.disposition_unstarted(broker,body)
    monkeypatch.setattr(d,'_client',lambda r:client)
    kwargs=dict(by=by,reason='Explicit new-source input repair.',change_request=newref,expected_source=SOURCE,
        previous_request=old['identity'],predecessor_sha256=pred['original_sha256'],control_revision=15)
    return SimpleNamespace(**locals())


def test_revision_preserves_originals_and_selects_one_new_identity_without_charge(system):
    s=system;writes=s.store.writes
    result=d.revise(s.runtime,TASK,**s.kwargs)
    folder,saved,proof,history=d._load(s.config,TASK)
    assert result['status']=='QUEUED' and saved['schema']==d.REVISION
    assert folder!=s.base and result['revised_unstarted_request']==s.old['identity']
    assert saved['predecessor']==s.pred and history==s.after and proof==s.proof
    assert {n:(s.base/n).read_bytes() for n in d.ORIGINAL_NAMES}==s.originals
    assert s.store.writes==writes and len(s.calls)==2
    rows=d.status(s.config)['successors']
    assert len(rows)==1 and rows[0]['request']==saved['identity']
    with pytest.raises(ValueError,match='ALREADY_PRESENT'):
        d.revise(s.runtime,TASK,**s.kwargs)


def test_retired_never_started_predecessor_uses_saved_bindings_not_an_admission(system):
    s = system
    s.broker.config['sources'] = [SOURCE]
    before = deepcopy(s.store.state);writes = s.store.writes
    result = d.revise(s.runtime,TASK,**s.kwargs)
    _,saved,proof,history = d._load(s.config,TASK)
    assert result['status'] == 'QUEUED'
    assert saved['predecessor']['source'] == OLD_SOURCE
    assert saved['predecessor'] == s.pred and proof == s.proof
    assert history == s.after
    assert s.store.state == before and s.store.writes == writes
    assert {n:(s.base/n).read_bytes() for n in d.ORIGINAL_NAMES} == s.originals


@pytest.mark.parametrize('name',['started.json','failure.json','preflight-failure.json',
    'input-preflight.json','reply.json','result.json','unknown'])
def test_any_predecessor_attempt_or_unknown_file_forbids_revision(system,name):
    s=system;(s.base/name).write_bytes(b'{}')
    with pytest.raises(ValueError,match='NOT_UNSTARTED'):d.revise(s.runtime,TASK,**s.kwargs)
    assert not d._revision_root(s.config,TASK).exists()


@pytest.mark.parametrize('mutation',['request-pin','original-pin','source','history-prefix','history-request',
    'pause','revision','controls-block','already-admitted','partial-turn','dangling-turn','halt','policy'])
def test_revision_refuses_wrong_bindings_or_nonquiescent_state(system,mutation):
    s=system
    if mutation=='request-pin':s.kwargs['previous_request']='9'*64
    elif mutation=='original-pin':s.kwargs['predecessor_sha256']={**s.pred['original_sha256'],'packet.json':'9'*64}
    elif mutation=='source':s.kwargs['expected_source']=OLD_SOURCE
    elif mutation=='history-prefix':s.after['events'][0]['payload']['rationale']='changed'
    elif mutation=='history-request':s.kwargs['change_request']={**s.newref,'request_id':'9'*64}
    elif mutation in ('pause','revision','controls-block'):
        db=sqlite3.connect(s.state/'coordinator.sqlite')
        if mutation=='pause':db.execute('UPDATE controls SET paused=0')
        elif mutation=='revision':db.execute('UPDATE controls SET revision=16')
        else:db.execute("INSERT INTO runtime_blocks VALUES('controls','blocked')")
        db.commit();db.close()
    elif mutation=='already-admitted':limiter.admit_server(s.store,s.policy,d.event(s.old))
    elif mutation in ('partial-turn','dangling-turn'):
        path=s.turns/(d.event(s.old)['turn_id']+'-1')
        path.mkdir() if mutation=='partial-turn' else path.symlink_to(s.turns/'missing')
    elif mutation=='halt':s.store.state['halted']=True
    else:s.store.state['policy_sha256']='f'*64
    with pytest.raises(ValueError):d.revise(s.runtime,TASK,**s.kwargs)
    assert not d._revision_root(s.config,TASK).exists()


def test_busy_existing_controller_writer_is_not_waited_or_bypassed(system):
    s=system
    with (s.state/'branch.lock').open('rb') as f:
        fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with pytest.raises(ValueError,match='WRITER_BUSY'):d.revise(s.runtime,TASK,**s.kwargs)


def test_ledger_movement_before_publication_leaves_partial_revision_ineligible(system,monkeypatch):
    s=system;original=s.client
    def moved(socket,op,body):
        if body['candidate_request'] is not None:limiter.admit_server(s.store,s.policy,d._event('e'*64,SOURCE))
        return original(socket,op,body)
    monkeypatch.setattr(d,'_client',lambda r:moved)
    with pytest.raises(ValueError,match='STATE_MOVED'):d.revise(s.runtime,TASK,**s.kwargs)
    assert not (d._revision_root(s.config,TASK)/'selection.json').exists()
    assert d.status(s.config)['successors'][0]['status']=='RECONCILIATION_REQUIRED'
    assert {n:(s.base/n).read_bytes() for n in d.ORIGINAL_NAMES}==s.originals


def test_late_old_admission_blocks_revised_launch_and_old_packet_cannot_launch(system):
    s=system;oldpacket=d.packet(s.old,s.proof,s.before)
    d.revise(s.runtime,TASK,**s.kwargs)
    with pytest.raises(ValueError):d.verify_launch(s.config,{'event':d.event(s.old),'stage':'disposition',
        'packet':oldpacket,'prompt':d.prompt(oldpacket)},s.client)
    _,saved,proof,history=d._load(s.config,TASK);value=d.packet(saved,proof,history)
    assert d.verify_launch(s.config,{'event':d.event(saved),'stage':'disposition',
        'packet':value,'prompt':d.prompt(value)},s.client)['status']=='VERIFIED_LINKED_DISPOSITION_LAUNCH'
    limiter.admit_server(s.store,s.policy,d.event(s.old))
    with pytest.raises(ValueError,match='ALREADY_ADMITTED'):
        d.verify_launch(s.config,{'event':d.event(saved),'stage':'disposition',
            'packet':value,'prompt':d.prompt(value)},s.client)


def test_current_and_historical_active_apps_and_all_adverse_payloads_remain(system):
    s=system;d.revise(s.runtime,TASK,**s.kwargs)
    _,saved,proof,history=d._load(s.config,TASK);value=d.packet(saved,proof,history)
    view=dc.selected_linked_disposition_view(value,SOURCE)
    selected=view['recorded_changes']
    assert view['reviewer_evidence']==value['reviewer_evidence']
    assert s.oldref['applied_event'] in selected['retained_historical_active_events']
    assert s.newref['applied_event'] in selected['active_applied_events']
    assert [(e['sequence'],e['payload']) for e in selected['events'] if e['event']!='APPLIED']==[
        (e['sequence'],e['payload']) for e in history['events'] if e['event']!='APPLIED']
    changed=deepcopy(value);changed['reviewer_evidence']['unstarted_predecessor']['active_applied_events']=[]
    with pytest.raises(ValueError):dc.selected_linked_disposition_view(changed,SOURCE)


def test_shared_compact_context_is_lossless_and_historical_encoder_is_unchanged(system):
    s=system
    context={'verified_source_commit':SOURCE,'task_state':{'trigger':d.TRIGGER},
             'unicode':'é\n"\\','many':[{'value':'x'*20} for _ in range(25000)]}
    raw=h.context_bytes(s.root,context,SOURCE)
    assert json.loads(raw)==context and cycle.encoded(json.loads(raw))==cycle.encoded(context)
    assert len(raw)<len(cycle.encoded(context))
    (s.root/'orchestrator/hosted_context.py').write_text('"""historical source"""\n')
    assert h.context_bytes(s.root,context,SOURCE)==cycle.encoded(context)
    (s.root/'orchestrator/hosted_context.py').write_text('LINKED_DISPOSITION_PRESENTATION_VERSION = True\n')
    with pytest.raises(ValueError,match='SOURCE_BOUND'):h.context_bytes(s.root,context,SOURCE)


def test_context_size_bound_is_not_raised_or_replaced_with_selected_original(system):
    s=system
    context={'verified_source_commit':SOURCE,'task_state':{'trigger':d.TRIGGER},'full_original':'x'*1500000}
    with pytest.raises(ValueError,match='HOSTED_FULL_CONTEXT_TOO_LARGE'):h.context_bytes(s.root,context,SOURCE)
    assert cycle.encoded(context)==cycle.encoded(deepcopy(context))


def test_composition_and_measurement_use_same_selected_input_and_full_context_bytes(system,monkeypatch):
    s=system
    monkeypatch.setattr(h,'build',lambda root,state:{'task_state':state,'documents':{},
        'policy':'synthetic source policy'})
    _,saved,proof,history=d._base(s.config,TASK)
    saved={**saved,'source':SOURCE}
    value=d.packet(saved,proof,s.after);value['linked_disposition']['change_request']=s.newref
    # Packet metadata is supplied only through this pure synthetic case.
    raw=cycle.encoded(value)
    final,context=h.compose_input(s.root,raw,d.prompt(value),verified_source=SOURCE,family='astra')
    shown=json.JSONDecoder().raw_decode(final.split(':\n',1)[1])[0]
    assert shown['task_state']['reviewer_evidence']==context['task_state']['reviewer_evidence']
    assert shown['task_state']['recorded_changes']['schema']==dc.SELECTED_CHAIN
    assert context['task_state']['recorded_changes']==s.after
    assert shown['selected_linked_disposition_presentation']['original_context_sha256']==sha(h.context_bytes(s.root,context,SOURCE))
    folder=s.root/'turn';folder.mkdir();(folder/'packet.json').write_bytes(raw)
    enveloped,restored=h.envelope(s.root,folder,d.prompt(value),SOURCE,family='codex')
    assert h.format_prefix(enveloped,prepared_prompt=False,output_format='markdown')==final
    assert h.context_bytes(s.root,restored,SOURCE)==h.context_bytes(s.root,context,SOURCE)


def test_native_measurement_and_dispatch_file_receipt_agree(system,monkeypatch):
    s=system
    monkeypatch.setattr(h,'build',lambda root,state:{'task_state':state,'documents':{},'policy':'synthetic'})
    monkeypatch.setattr(d,'checked_source',lambda *a:s.root)
    _,saved,proof,_=d._base(s.config,TASK)
    saved={**saved,'source':SOURCE,'change_request':s.newref}
    value=d.packet(saved,proof,s.after)
    final,context=h.compose_input(s.root,cycle.encoded(value),d.prompt(value),verified_source=SOURCE,family='astra')
    measured,expected_sha=REAL_MEASUREMENT(saved,value)
    assert measured['input_sha256']==sha(final.encode())
    assert expected_sha==sha(h.context_bytes(s.root,context,SOURCE))
    original_path=Path
    # Only the synthetic protected model-work ownership boundary is replaced;
    # context preservation, measurements, process receipts and parsing run unchanged.
    class ModelWorkPath(type(Path())):
        def stat(self, **kwargs):
            info=super().stat(**kwargs)
            if str(self)==str(s.root/'model-work'):
                fields=list(info);fields[4]=0
                return os.stat_result(fields)
            return info
    monkeypatch.setattr(cycle,'Path',lambda path: ModelWorkPath(s.root/'model-work') if str(path)=='/var/lib/research-system/model-work' else original_path(path))
    monkeypatch.setattr(cycle,'checked_source',lambda *a:s.root)
    monkeypatch.setattr(cycle.subprocess,'check_output',lambda *a,**kw:SOURCE)
    monkeypatch.setattr(h,'envelope',lambda *a,**kw:(h.compose_input(s.root,cycle.encoded(value),d.prompt(value),verified_source=SOURCE,family='astra',prepared_prompt=True)[0],context))
    monkeypatch.setattr(cycle.pwd,'getpwnam',lambda user:SimpleNamespace(pw_uid=os.getuid(),pw_gid=os.getgid()))
    monkeypatch.setattr(cycle.os,'chown',lambda *a:None)
    monkeypatch.setattr(cycle.os,'killpg',lambda *a:None)
    commands=[]
    class Process:
        pid=2000000000
        returncode=0
        def __init__(self,argv,**kwargs):
            commands.append(argv);self.output=kwargs['stdout']
        def communicate(self,data,timeout):
            assert data==final.encode()
            for event in [{'type':'thread.started','thread_id':'synthetic-thread'},
                {'type':'item.completed','item':{'type':'agent_message','text':'Defer; scientific acceptance remains absent.'}},
                {'type':'turn.completed','usage':{'input_tokens':1,'output_tokens':1}}]:
                self.output.write((json.dumps(event)+'\n').encode())
            self.output.flush()
        def wait(self,**kwargs):return 0
    monkeypatch.setattr(cycle.subprocess,'Popen',Process)
    folder=s.root/'dispatch';folder.mkdir(mode=0o700)
    answer,receipt=cycle.model_call(folder,'disposition','astra',d.prompt(value))
    raw=(folder/'disposition.operating-context.json').read_bytes()
    assert json.loads(raw)==context and raw==h.context_bytes(s.root,context,SOURCE)
    assert receipt['operating_context_sha256']==expected_sha
    assert receipt['input_sha256']==measured['input_sha256']
    assert '-s' in commands[0] and 'read-only' in commands[0]
    assert 'scientific acceptance remains absent' in answer


def test_current_admitted_threshold_turn_may_finish_without_admitting_predecessor(system):
    s=system
    d.revise(s.runtime,TASK,**s.kwargs)
    _,saved,proof,history=d._load(s.config,TASK)
    for number in range(2,96):
        limiter.admit_server(s.store,s.policy,d._event(f'{number:064x}',SOURCE))
    assert s.store.state['count']==95 and not s.store.state['halted']
    admitted=limiter.admit_server(s.store,s.policy,d.event(saved))
    assert admitted['status']=='ADMITTED' and s.store.state['count']==96 and s.store.state['halted']
    value=d.packet(saved,proof,history)
    result=d.verify_launch(s.config,{'event':d.event(saved),'stage':'disposition','packet':value,'prompt':d.prompt(value)},s.client)
    assert result['status']=='VERIFIED_LINKED_DISPOSITION_LAUNCH'
    assert 'server:'+d.event(s.old)['turn_id']+':1' not in s.store.state['events']


def test_unrelated_threshold_admission_does_not_allow_unadmitted_revision(system):
    s=system
    d.revise(s.runtime,TASK,**s.kwargs)
    for number in range(2,97):
        limiter.admit_server(s.store,s.policy,d._event(f'{number:064x}',SOURCE))
    assert s.store.state['halted']
    _,saved,proof,history=d._load(s.config,TASK);value=d.packet(saved,proof,history)
    with pytest.raises(ValueError,match='LEDGER_HALTED'):
        d.verify_launch(s.config,{'event':d.event(saved),'stage':'disposition','packet':value,'prompt':d.prompt(value)},s.client)


def test_candidate_admission_before_publication_refuses_and_preserves_partial(system):
    s=system
    def racing(socket,op,body):
        if body['candidate_request'] is not None:
            _,candidate,_,_=d._load_folder(d._revision_root(s.config,TASK)/body['candidate_request'],TASK)
            limiter.admit_server(s.store,s.policy,d.event(candidate))
        return s.client(socket,op,body)
    s.monkeypatch.setattr(d,'_client',lambda r:racing)
    with pytest.raises(ValueError,match='ALREADY_ADMITTED'):d.revise(s.runtime,TASK,**s.kwargs)
    assert not (d._revision_root(s.config,TASK)/'selection.json').exists()
    assert d.status(s.config)['successors'][0]['status']=='RECONCILIATION_REQUIRED'
    assert {n:(s.base/n).read_bytes() for n in d.ORIGINAL_NAMES}==s.originals


def test_protected_absence_is_controller_only_and_has_no_generic_lookup(system,monkeypatch):
    from orchestrator.protected_handover import Broker
    broker=Broker.__new__(Broker);broker.config={'controller_uid':12345}
    request={'operation':'disposition_unstarted','body':{}}
    with pytest.raises(ValueError,match='BROKER_PEER_REFUSED'):broker.handle(request,12346)
    with pytest.raises(ValueError,match='UNSTARTED_REQUEST_SCHEMA'):
        pd.disposition_unstarted(system.broker,{'ledger_key':'arbitrary'})


def test_root_transport_preserves_exact_revision_arguments(system,monkeypatch):
    from orchestrator import handover_runtime as hr
    import pwd
    s=system;calls=[]
    monkeypatch.setattr(hr.os,'getuid',lambda:0)
    monkeypatch.setattr(pwd,'getpwuid',lambda uid:SimpleNamespace(pw_name='research-controller'))
    monkeypatch.setattr(hr,'checked_source',lambda *a:s.root)
    monkeypatch.setattr(hr.subprocess,'run',lambda argv,**kw:calls.append((argv,kw)) or SimpleNamespace(stdout=b'{"status":"QUEUED"}'))
    replacement={k:v for k,v in s.kwargs.items() if k!='by'}
    result=hr.controller_command(s.config,'disposition-revise',task_id=TASK,submitted_by=s.by,replacement=replacement)
    assert result['status']=='QUEUED'
    argv,kwargs=calls[0]
    assert argv[argv.index('--previous-request')+1]==s.old['identity']
    assert json.loads(argv[argv.index('--predecessor-sha256')+1])==s.pred['original_sha256']
    assert argv[argv.index('--revision')+1]=='15'
    assert 'disposition-revise' in argv and '-B' in argv
    assert kwargs['timeout']==60 and kwargs['check'] is True
    with pytest.raises(ValueError,match='REVISION_ARGUMENTS_ONLY'):
        hr.controller_command(s.config,'operation-replace',task_id=TASK,submitted_by=s.by,replacement=replacement)
