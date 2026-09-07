import os
import hashlib,json
import subprocess
import pytest
from orchestrator.protected_handover import Broker,REPOSITORY,BRANCH
from orchestrator.dispatch_limiter import GitLedger,initial
from test_dispatch_limiter import config
from test_server_admission import server


def broker(tmp_path):
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    GitLedger(tmp_path).cas(None,initial())
    return Broker({'mode':'SYNTHETIC_FIXTURE','repository':REPOSITORY,'branch':BRANCH,
                  'controller_uid':10001,'operator_uids':[os.getuid()],'sources':['b'*40],
                  'ledger_repo':str(tmp_path),'publication_root':str(tmp_path),'writer_config':None,'model_mode':'DISABLED','turn_root':str(tmp_path/'turns'),'max_model_turns':0,
                  'policy':{**config(2),'server_semantics':'OPERATOR_AUTHORIZED_V1','reset_operators':['ssh-uid:'+str(os.getuid())]}})


def test_peer_bound_admission_no_socket_reset_or_publication(tmp_path):
    b=broker(tmp_path);request={'operation':'admit_server','body':server(1)}
    with pytest.raises(ValueError,match='PEER'):b.handle(request,10002)
    assert b.handle(request,10001)['count']==1
    assert b.handle(request,10001)['duplicate_admission']
    with pytest.raises(ValueError,match='OPERATION'):b.handle({'operation':'reset','body':{}},10001)
    with pytest.raises(ValueError,match='NOT_AUTHORIZED'):b.handle({'operation':'publish','body':{}},10001)
    with pytest.raises(ValueError,match='SOURCE'):b.handle({'operation':'admit_server','body':{**server(2),'source':'c'*40}},10001)


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
    (folder/'binding.json').write_text(json.dumps({'event':event}))
    assert b.handle(request,10001)['status']=='NOT_STARTED_RECONCILIATION_REQUIRED'
    (folder/'review.started.json').write_text('{}')
    assert b.handle(request,10001)['status']=='UNCERTAIN_MODEL_RECONCILE_NO_RETRY'
    receipt={}
    for suffix,key in [('.stdout','stdout_sha256'),('.stderr','stderr_sha256'),('.input.md','input_sha256'),('.md','answer_sha256'),('.operating-context.json','operating_context_sha256')]:
        raw=b'synthetic evidence';(folder/('review'+suffix)).write_bytes(raw)
        receipt[key]=hashlib.sha256(raw).hexdigest()
    (folder/'review.receipt.json').write_text(json.dumps(receipt))
    assert b.handle(request,10001)['status']=='COMPLETE'
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
