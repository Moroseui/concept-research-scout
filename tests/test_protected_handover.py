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
                  'ledger_repo':str(tmp_path),'publication_root':str(tmp_path),'writer_config':None,
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
