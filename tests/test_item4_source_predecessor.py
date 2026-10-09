"""Exact failure continuation; real ledger and synthetic frozen payloads."""
import copy,json,subprocess
from pathlib import Path
import pytest
from orchestrator import modal_source_budget as q,modal_source_composition as m,private_records as pr
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from test_item4_source_budget import prepared,unreserved,unreserved_fixture,inventory_fixture,experiment,root
from test_item4_source_composition import synthetic_contract
REAL_PREDECESSOR=q.source_predecessor

@pytest.fixture
def predecessor(prepared,synthetic_contract,tmp_path,monkeypatch):
    f=prepared;metadata,_=synthetic_contract;files,membership=m.contract(metadata)
    f.source_binding['inventory_sha256']=m.INVENTORY
    old=copy.deepcopy(f.source_binding);old['operation_id']='item4-frozen-base-source-v1'
    ident=digest(canonical(old));failure={'status':'UNCERTAIN','binding_sha256':ident,'error_type':'AttributeError','no_automatic_retry':True,'reservation_retained':True}
    db=f.accounts.db;db.execute('DELETE FROM autonomy_assets WHERE id=?',(q.SOURCE_PREDECESSOR_ID,))
    db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,'UNCERTAIN',3321330,?)",(ident,q.RUN,canonical(old).decode(),canonical(failure).decode()))
    monkeypatch.setattr(q,'SOURCE_PREDECESSOR_ID',ident)
    state=tmp_path/'old';pr.mkdir(state);pr.mkdir(state/'data');pr.mkdir(state/'incoming')
    _,brain,cache,baseline=m.partitions(files)
    for n,r in {**brain,**baseline}.items():m.write_verified(state/'incoming',n,r,[b'x'])
    for n,r in {**brain,**cache,**baseline}.items():m.write_verified(state/'data',n,r,[b'x'])
    for name,value in [('binding.json',old),('FAILED.json',failure),('prepare-intent.json',{'binding_sha256':ident})]:pr.write_bytes(state/name,canonical(value))
    row=dict(db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone())
    unit={'MainPID':'0','ExecMainStatus':'1','ActiveState':'failed','InvocationID':'synthetic-terminal'}
    proof={'asset':row,'asset_sha256':digest(canonical(row)),'unit':unit,'membership':membership,
           'records':{p.name:{'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())} for p in state.iterdir() if p.is_file()}}
    monkeypatch.setattr(q,'SOURCE_PREDECESSOR_STATE',state);monkeypatch.setattr(q,'source_failure_proof',lambda:proof)
    monkeypatch.setattr(q,'source_predecessor',REAL_PREDECESSOR)
    monkeypatch.setattr(m,'contract',lambda root:(files,membership))
    monkeypatch.setattr(subprocess,'check_output',lambda *a,**kw:'\n'.join(k+'='+v for k,v in unit.items()))
    f.predecessor_state=state;f.predecessor_proof=proof;f.predecessor_id=ident;f.observed_unit=unit
    return f

def test_only_exact_terminal_precreate_failure_qualifies_without_mutation(predecessor):
    f=predecessor;before=[tuple(r) for r in f.accounts.db.execute('SELECT * FROM autonomy_assets')]
    assert q.source_predecessor(f.accounts,f.source_binding)==f.predecessor_id
    assert before==[tuple(r) for r in f.accounts.db.execute('SELECT * FROM autonomy_assets')]

@pytest.mark.parametrize('damage',['row-cost','row-status','missing-row','record','directory','payload','new-create','active-unit','different-invocation','scope','operation'])
def test_changed_unknown_or_active_source_failure_refuses(predecessor,damage):
    f=predecessor;s=f.predecessor_state;db=f.accounts.db
    if damage=='row-cost':db.execute('UPDATE autonomy_assets SET reserved_micro_usd=0 WHERE id=?',(f.predecessor_id,))
    elif damage=='row-status':db.execute("UPDATE autonomy_assets SET status='READY' WHERE id=?",(f.predecessor_id,))
    elif damage=='missing-row':db.execute('DELETE FROM autonomy_assets WHERE id=?',(f.predecessor_id,))
    elif damage=='record':pr.write_bytes(s/'unexpected.json',b'{}')
    elif damage=='directory':pr.mkdir(s/'unexpected')
    elif damage=='payload':
        p=next(p for p in (s/'data').rglob('*') if p.is_file());p.chmod(0o600);p.write_bytes(b'y')
    elif damage=='new-create':pr.write_bytes(s/'volume-create-intent.json',b'{}')
    elif damage in {'active-unit','different-invocation'}:
        # The captured terminal proof remains unchanged; only observation differs.
        changed=dict(f.observed_unit);changed['MainPID' if damage=='active-unit' else 'InvocationID']='other'
        import unittest.mock
        with unittest.mock.patch.object(subprocess,'check_output',return_value='\n'.join(k+'='+v for k,v in changed.items())):
            with pytest.raises(ValueError):q.source_predecessor(f.accounts,f.source_binding)
        return
    elif damage=='scope':f.source_binding['inventory_sha256']='e'*64
    else:f.source_binding['operation_id']='unbounded-other'
    with pytest.raises(ValueError):q.source_predecessor(f.accounts,f.source_binding)

def test_changed_pinned_predecessor_document_refuses(tmp_path,monkeypatch):
    p=tmp_path/'proof.json';pr.write_bytes(p,b'{}');monkeypatch.setattr(q,'SOURCE_PREDECESSOR_PROOF',p)
    with pytest.raises(ValueError,match='PREDECESSOR_PROOF_CHANGED'):q.source_failure_proof()
