import copy,json
from pathlib import Path
import pytest
from orchestrator import idea2_cpu_lane as lane
from orchestrator import idea2_cpu_contract as contract

def test_authentic_accepted_lane_binding_and_changed_state_refusal(monkeypatch):
 # Synthetic records exercise the same fixed shape without patient material.
 cfg=json.dumps({'run_id':contract.RUN}).encode()
 monkeypatch.setattr(lane,'CONFIG_SHA',contract.sha(cfg))
 state={'phase':'COMMIT_SPEC','program_result':{'program_sha256':contract.PROGRAM,'synthetic_status':'PASS'},
        'reviewed_execution':{'sha256':contract.APPROVAL}}
 sr={'id':1,'payload':json.dumps(state)};account={'id':1,'payload':'original'}
 calls=[{'id':str(i),'status':'COMPLETE'}for i in range(13)]+[
        {'id':lane.AUTHOR_CALL,'status':'COMPLETE'},{'id':lane.REVIEW_CALL,'status':'COMPLETE'}]
 proof={'config_sha256':contract.sha(cfg),'state_row':sr,'account_row':account,'calls':calls}
 result=lane.verify_snapshot(cfg,sr,account,calls,proof)
 assert result['new_calls']==0 and result['preparation_grant_changed']is False
 for target in ('config','state','account','calls'):
  c,s,a,rows=cfg,copy.deepcopy(sr),copy.deepcopy(account),copy.deepcopy(calls)
  if target=='config':c+=b' '
  if target=='state':s['payload']='{"phase":"MODEL_RUNNING"}'
  if target=='account':a['payload']='reset'
  if target=='calls':rows[-1]['status']='UNCERTAIN'
  with pytest.raises(ValueError):lane.verify_snapshot(c,s,a,rows,proof)

def test_proof_is_pinned():
 root=Path(lane.__file__).parents[1]
 proof=lane.frozen(root)
 assert len(proof['calls'])==15
 assert json.loads(proof['state_row']['payload'])['phase']=='COMMIT_SPEC'


def test_read_accepted_lane_never_creates_a_missing_ledger(tmp_path,monkeypatch):
    from orchestrator import private_records as pr
    monkeypatch.setattr(lane,'frozen',lambda root:{})
    (tmp_path/'lane.json').write_text('{}')
    (tmp_path/'lane.json').chmod(0o600)
    with pytest.raises((ValueError,FileNotFoundError)):
        lane.read_accepted_lane(tmp_path,tmp_path)
    assert not (tmp_path/'jobs.sqlite').exists()


def test_actual_accepted_snapshot_matches_config_calls_and_approval():
    import base64
    proof=lane.frozen(Path(lane.__file__).parents[1])
    raw=base64.b64decode(proof['config_raw_base64'],validate=True)
    result=lane.verify_snapshot(raw,proof['state_row'],proof['account_row'],proof['calls'],proof)
    assert result['scientific_calls_preserved']==15 and result['new_calls']==0
    assert result['review_call']==lane.REVIEW_CALL
