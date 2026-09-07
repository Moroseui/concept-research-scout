import os
import hashlib,json
import subprocess
import pytest
from orchestrator.protected_handover import Broker,REPOSITORY,BRANCH
from orchestrator.dispatch_limiter import GitLedger,initial
from test_dispatch_limiter import config
from test_server_admission import server


def broker(tmp_path):
    ledger=tmp_path/'ledger';ledger.mkdir()
    subprocess.run(['git','init','-q',str(ledger)],check=True)
    GitLedger(ledger).cas(None,initial())
    return Broker({'mode':'SYNTHETIC_FIXTURE','repository':REPOSITORY,'branch':BRANCH,
                  'controller_uid':10001,'operator_uids':[os.getuid()],'sources':['b'*40],
                  'ledger_repo':str(ledger),'publication_root':str(tmp_path/'publication'),'writer_config':None,'model_mode':'DISABLED','turn_root':str(tmp_path/'turns'),'max_model_turns':0,
                  'policy':{**config(2),'server_semantics':'OPERATOR_AUTHORIZED_V1','reset_operators':['ssh-uid:'+str(os.getuid())]}})


def test_peer_bound_admission_no_socket_reset_or_publication(tmp_path):
    b=broker(tmp_path);request={'operation':'admit_server','body':server(1)}
    with pytest.raises(ValueError,match='PEER'):b.handle(request,10002)
    assert b.handle(request,10001)['count']==1
    assert b.handle(request,10001)['duplicate_admission']
    with pytest.raises(ValueError,match='OPERATION'):b.handle({'operation':'reset','body':{}},10001)
    with pytest.raises(ValueError,match='NOT_AUTHORIZED'):b.handle({'operation':'publish','body':{}},10001)
    with pytest.raises(ValueError,match='SOURCE'):b.handle({'operation':'admit_server','body':{**server(2),'source':'c'*40}},10001)


def test_publication_status_has_fixed_peer_and_no_fixture_network(tmp_path,monkeypatch):
    b=broker(tmp_path)
    def forbidden(*args):raise AssertionError('No fixture network')
    monkeypatch.setattr('orchestrator.publication_candidate.git',forbidden)
    request={'operation':'publication_status','body':{}}
    with pytest.raises(ValueError,match='PEER'):b.handle(request,10002)
    assert b.handle(request,10001)=={'status':'PUBLICATION_NOT_AUTHORIZED'}
    with pytest.raises(ValueError,match='STATUS_BODY'):
        b.handle({'operation':'publication_status','body':{'branch':'main'}},10001)
    assert b.handle({'operation':'flush_notifications','body':{}},10001)=={'status':'NOTIFICATIONS_DISABLED'}
    with pytest.raises(ValueError,match='BLOCK_NOTIFICATION_SCHEMA'):
        b.handle({'operation':'notify_task_block','body':{'source':'b'*40,'task':'a'*64,'reason':'run arbitrary shell'}},10001)


def test_operator_reset_sequence_and_action_provenance(tmp_path,monkeypatch):
    b=broker(tmp_path)
    b.handle({'operation':'admit_server','body':server(1)},10001)
    with pytest.raises(ValueError,match='PROVENANCE'):b.actions_admission({}, {})
    request={'expected_sequence':1,'decision_ref':'fixture-only','policy_sha256':hashlib.sha256(json.dumps(b.config['policy'],sort_keys=True).encode()).hexdigest()}
    assert b.operator('reset',request)['sequence']==2
    with pytest.raises(ValueError,match='STATE_MOVED'):b.operator('reset',request)
    monkeypatch.setattr('os.getuid',lambda:10001)
    with pytest.raises(ValueError,match='OS_IDENTITY'):b.operator('reset',request)


def test_read_only_completion_recovery_checks_original_bytes(tmp_path):
    b=broker(tmp_path);event=server(1)
    request={'operation':'stage_status','body':{'event':event,'stage':'review'}}
    assert b.handle(request,10001)['status']=='NOT_OBSERVED_NO_RETRY'
    folder=tmp_path/'turns'/(event['turn_id']+'-'+event['attempt']);folder.mkdir(parents=True)
    (folder/'binding.json').write_text(json.dumps({'event':event,'packet_sha256':'a'*64}))
    assert b.handle(request,10001)['status']=='NOT_STARTED_RECONCILIATION_REQUIRED'
    (folder/'review.started.json').write_text('{}')
    assert b.handle(request,10001)['status']=='UNCERTAIN_MODEL_RECONCILE_NO_RETRY'
    receipt={}
    for suffix,key in [('.stdout','stdout_sha256'),('.stderr','stderr_sha256'),('.input.md','input_sha256'),('.md','answer_sha256'),('.operating-context.json','operating_context_sha256')]:
        raw=b'synthetic evidence';(folder/('review'+suffix)).write_bytes(raw)
        receipt[key]=hashlib.sha256(raw).hexdigest()
    (folder/'review.receipt.json').write_text(json.dumps(receipt))
    assert b.handle(request,10001)['status']=='COMPLETE'
    assert b.handle(request,10001)['packet_sha256']=='a'*64
    (folder/'review.stdout').write_text('changed')
    with pytest.raises(ValueError,match='RECEIPT_CHANGED'):b.handle(request,10001)


def test_disconnected_client_does_not_destroy_completed_operation():
    import socket,threading
    from orchestrator.protected_handover import exchange
    completed=[]
    class Fake:
        def handle(self,request,uid):completed.append(True);return {'status':'COMPLETE'}
    left,right=socket.socketpair()
    right.sendall(b'{"operation":"fixture","body":{}}\n');right.close()
    with left:exchange(Fake(),left)
    assert completed==[True]


def test_stage_status_rejects_traversal_via_shared_event_validator(tmp_path):
    b=broker(tmp_path)
    for key,value in [('turn_id','../outside'),('attempt','../../outside')]:
        event={**server(1),key:value}
        with pytest.raises(ValueError,match='SERVER_IDENTITY'):
            b.stage_status({'event':event,'stage':'review'})


def test_publication_cache_cannot_overlap_execution_or_ledger(tmp_path):
    from pathlib import Path
    import orchestrator.protected_handover as module
    b=broker(tmp_path)
    for path in [b.config['ledger_repo'],str(tmp_path),str(Path(module.__file__).resolve().parents[1])]:
        with pytest.raises(ValueError,match='PROTECTED_STATE_ROOTS|EXECUTION_SOURCE'):
            Broker({**b.config,'publication_root':path})


def test_candidate_pin_is_separate_from_installed_execution_pin(tmp_path,monkeypatch):
    from contextlib import nullcontext
    import orchestrator.protected_handover as module
    b=broker(tmp_path)
    # Synthetic fake authentication/publisher: no live credential or Git write.
    b.config['mode']='LIVE_APPROVED'
    monkeypatch.setattr(b,'authentication',lambda:nullcontext())
    calls=[]
    def checked_publish(root,request,authority):
        calls.append((request,authority));return {'status':'fixture-delegated'}
    monkeypatch.setattr(module,'publish',checked_publish)
    request={'source':'c'*40,'before':'d'*40,'destination':BRANCH,'remote':REPOSITORY,'inventory':{}}
    assert request['source'] not in b.config['sources']
    assert b.handle({'operation':'publish','body':request},10001)['status']=='fixture-delegated'
    assert calls[0][1]=={k:v for k,v in request.items() if k!='inventory'}
    with pytest.raises(ValueError,match='DESTINATION_REFUSED'):
        b.handle({'operation':'publish','body':{**request,'destination':'main'}},10001)
    assert len(calls)==1



def test_initialization_permission_is_scoped_even_on_existing_state(tmp_path):
    b=broker(tmp_path)
    assert b.ledger.allow_initialization is False
    with pytest.raises(ValueError,match='ALREADY_EXISTS'):
        b.operator('initialize',{'decision_ref':'synthetic operator request'})
    assert b.ledger.allow_initialization is False


def test_governed_mode_cannot_replace_supervised_fixture_authority(tmp_path):
    b=broker(tmp_path)
    with pytest.raises(ValueError,match='GOVERNED_MODE_REQUIRES_LIVE_PERMISSION'):
        Broker({**b.config,'model_mode':'GOVERNED'})
    proposed={**b.config,'model_mode':'GOVERNED','mode':'LIVE_APPROVED'}
    with pytest.raises(ValueError,match='RATIFICATION_AND_PERMISSION'):
        Broker({**proposed,'policy':{**b.config['policy'],'status':'PROPOSED'}})
    # Construction verifies the protected policy only. No key, state ref, model
    # or live permission is created by this synthetic test.
    with pytest.raises(ValueError,match='SEPARATE_UNATTENDED_ACTIVATION_REQUIRED'):
        Broker(proposed)
    governed=Broker({**proposed,'activation_decision_sha256':'e'*64})
    assert governed.config['max_model_turns']==0
