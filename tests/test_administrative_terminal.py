"""Synthetic root provenance only in unit tests; real-copy rehearsal is separate."""
import copy,hashlib,json,sqlite3
from pathlib import Path
import pytest
from orchestrator import administrative_terminal as terminal,private_records
from orchestrator.autonomy_review_runner import ReviewQueue
from orchestrator.autonomy_accounting import BatchAccounts

ID='a'*64
PIN='b'*64

def fixture():
    row={'id':ID,'kind':'scientific','change_id':'run','round':1,'day':'2026-01-01','status':'UNCERTAIN',
      'binding':json.dumps({'stage':'result_interpretation_review','input':{'input_sha256':PIN}}),'receipt':'{}'}
    events=[{'type':'system','subtype':'init','session_id':'synthetic'},
      {'type':'result','subtype':'error_max_turns','session_id':'synthetic','num_turns':30}]
    prov={'stage':'result_interpretation_review','family_effective':'claude','exit_class':'ok','attempts':[{'returncode':0}],'prompt_sha256':PIN}
    bodies={'console.log':('\n'.join(map(json.dumps,events))+'\n').encode(),'stage_provenance.jsonl':(json.dumps(prov)+'\n').encode(),'sent-input.json':json.dumps({'input_sha256':PIN}).encode()}
    return row,bodies

@pytest.mark.parametrize('damage',['running','implementation','missing','duplicate','conflict','verdict','session','input','exit','trailing','unknown'])
def test_unproven_or_conflicting_outcomes_refuse(damage):
    row,b=fixture()
    if damage=='running':row['status']='RUNNING'
    elif damage=='implementation':row['kind']='implementation_review'
    elif damage=='missing':b.pop('console.log')
    elif damage=='input':b['sent-input.json']=b'{}'
    elif damage=='exit':p=json.loads(b['stage_provenance.jsonl']);p['attempts'][0]['returncode']=1;b['stage_provenance.jsonl']=json.dumps(p).encode()
    else:
        e=[json.loads(x) for x in b['console.log'].splitlines()]
        if damage=='duplicate':e.append(e[-1])
        elif damage=='conflict':e[-1]['subtype']='success'
        elif damage=='verdict':e[-1]['result']='APPROVE'
        elif damage=='session':e[-1]['session_id']='different'
        elif damage=='trailing':e.append({'type':'assistant'})
        elif damage=='unknown':e[-1]['subtype']='unknown'
        b['console.log']=('\n'.join(map(json.dumps,e))+'\n').encode()
    with pytest.raises((ValueError,KeyError)):terminal.proof_kind(row,b)

def test_terminal_is_not_approval():
    row,b=fixture();assert terminal.proof_kind(row,b)=='PROVEN_TERMINAL_NATIVE_NO_VERDICT'
    assert row['status']=='UNCERTAIN'

@pytest.fixture
def preserved(tmp_path,monkeypatch):
    root=tmp_path/'terminal';root.mkdir(mode=0o700);folder=root/ID;folder.mkdir(mode=0o700)
    row,b=fixture();unit={'unit':'research-manual-sprint10-synthetic.service','invocation':'synthetic','boot_id':'synthetic'}
    for n,raw in b.items():(folder/n).write_bytes(raw);(folder/n).chmod(0o600)
    p={'schema':'administrative-only-terminal/v1','id':ID,'row_sha256':terminal.row_hash(row),'authority_sha256':terminal.APPROVAL,
       'classification':terminal.proof_kind(row,b),'unit':unit,'files':{n:terminal.digest(raw) for n,raw in b.items()}}
    (folder/'proof.json').write_text(json.dumps(p));(folder/'proof.json').chmod(0o600)
    monkeypatch.setattr(terminal,'ROOT',root)
    monkeypatch.setattr(terminal,'trusted',lambda p:private_records.check(p)) # synthetic root provenance ONLY
    monkeypatch.setattr(terminal,'unit_state',lambda u:unit) # synthetic stopped unit ONLY
    return row,folder

@pytest.mark.parametrize('damage',['row','file','proof','public','unit'])
def test_preserved_binding_and_private_modes_fail_closed(preserved,monkeypatch,damage):
    row,folder=preserved
    if damage=='row':row['receipt']='changed'
    elif damage=='file':(folder/'console.log').write_text('changed')
    elif damage=='proof':(folder/'proof.json').write_text('{}')
    elif damage=='public':(folder/'console.log').chmod(0o644)
    else:monkeypatch.setattr(terminal,'unit_state',lambda u:{'unit':u,'boot_id':'changed'})
    with pytest.raises((ValueError,KeyError)):terminal.verify(row)

def test_administrative_reconciliation_is_readonly_and_scientific_guard_stays(preserved,tmp_path,monkeypatch):
    row,folder=preserved;q=BatchAccounts(tmp_path/'ledger');q.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',tuple(row.values()))
    before=[tuple(x) for x in q.db.execute('select * from autonomy_calls')]
    a=terminal.administrative_exceptions(q.db);assert len(a)==1
    assert terminal.administrative_exceptions(q.db)==a
    q.db.execute("INSERT INTO autonomy_runs VALUES('run','{}','ACTIVE')")
    with pytest.raises(ValueError,match='BATCH_UNCERTAIN_OR_RUNNING_CALL'):q.reserve_scientific('new','run','run_spec_author','c'*40,{})
    assert [tuple(x) for x in q.db.execute('select * from autonomy_calls')]==before
    q.db.execute("UPDATE autonomy_calls SET status='RUNNING'")
    with pytest.raises(ValueError,match='UNCERTAIN_OR_RUNNING_REVIEW_NO_NEW_CALL'):terminal.administrative_exceptions(q.db)


def test_unknown_preclient_claim_is_not_positive_proof():
    row,b=fixture();row['id']=terminal.PRECLIENT_ID
    with pytest.raises(ValueError,match='ADMIN_PRECLIENT_BINDING'):terminal.proof_kind(row,b)
