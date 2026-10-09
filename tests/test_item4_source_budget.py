"""Real SQLite admission, existing caps and originals retained; synthetic fixtures."""
import copy,json
from datetime import timedelta
import pytest
from orchestrator import modal_source_budget as q,modal_source_composition as source,modal_direct_budget as direct,modal_environment_budget as shared
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from test_item4_native_synthetic import unreserved,unreserved_fixture,inventory_fixture,experiment,root
from test_modal_pinned_image import view
from test_modal_direct_budget import NOW
from test_modal_environment_budget import asset,compute

@pytest.fixture
def prepared(unreserved,monkeypatch):
    f=unreserved;v=view();v['rates'].update(volume_storage_gib_month_cost='0.09',egress_gib_cost='0.04')
    from test_modal_environment_budget import seal
    seal(v)
    old={'purpose':direct.PURPOSE,'authority_sha256':q.AUTHORITY,'download_authority_sha256':direct.DOWNLOAD_AUTHORITY,
         'envelope':{'cost':{'reserved_micro_usd':1000000}}}
    ident=digest(canonical(old));monkeypatch.setattr(q,'DIRECT_ID',ident)
    f.accounts.db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,'READY',1000000,NULL)",(ident,'existing-download',canonical(old).decode()))
    monkeypatch.setattr(q,'native_qualification',lambda accounts,binding:set())
    f.source_binding={'purpose':q.PURPOSE,'operation_id':source.OPERATION,'run_id':q.RUN,'authority_sha256':q.AUTHORITY,
        'team_authority_sha256':q.TEAM_AUTHORITY,'source':f.binding['source'],'helper_source':'d'*40,
        'owner_sha256':f.binding['owner_sha256'],'config_sha256':'c'*64,'inventory_sha256':source.INVENTORY,
        'native_asset_id':q.NATIVE_ID,'direct_asset_id':ident,'source_volume_id':q.DIRECT_VOLUME,
        'envelope':q.envelope(v['rates']),'created_at':NOW.isoformat(),'expires_at':(NOW+timedelta(days=30)).isoformat()}
    original={'purpose':q.PURPOSE,'operation_id':'item4-frozen-base-source-v1'}
    f.accounts.db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,'UNCERTAIN',3321330,'{}')",(q.SOURCE_PREDECESSOR_ID,q.RUN,canonical(original).decode()))
    monkeypatch.setattr(q,'source_predecessor',lambda *a:q.SOURCE_PREDECESSOR_ID)
    f.view=v;return f

def reserve(f):return q.reserve(f.accounts,f.source_binding,billing_snapshot=f.view,now=NOW)

def test_normal_admission_once_preserves_originals_and_owner(prepared):
    f=prepared;db=f.accounts.db;before=[tuple(r) for r in db.execute('SELECT * FROM autonomy_assets')];owners=[tuple(r) for r in db.execute('SELECT * FROM autonomy_runs')]
    assert reserve(f) is True and reserve(f) is False
    assert [tuple(r) for r in db.execute('SELECT * FROM autonomy_assets')][:len(before)]==before
    assert [tuple(r) for r in db.execute('SELECT * FROM autonomy_runs')]==owners
    assert db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0 and not f.calls
    assert sum(r['reserved_micro_usd'] for r in db.execute('SELECT * FROM autonomy_assets'))==1000000+3321330+f.source_binding['envelope']['reserved_micro_usd']
    f.source_binding['config_sha256']='e'*64
    with pytest.raises(ValueError,match='ALREADY_PREPARED_NO_RETRY'):reserve(f)

@pytest.mark.parametrize('kind',['download','smoke','full','owned-assets'])
def test_overcap_refused_with_every_previous_liability(prepared,kind):
    f=prepared;amount=f.source_binding['envelope']['reserved_micro_usd'];db=f.accounts.db
    if kind=='download':asset(f.accounts.batch,q.SMOKE_CAP-1000000-3321330-amount+1)
    elif kind=='owned-assets':db.execute("INSERT INTO autonomy_assets VALUES('other',?,'{}','READY',?,NULL)",(q.RUN,q.SMOKE_CAP-1000000-3321330-amount+1))
    else:compute(f.accounts.batch,(q.TOTAL_CAP if kind=='full' else q.SMOKE_CAP)-1000000-3321330-amount+1,stage=kind.upper())
    before=[tuple(r) for r in db.execute('SELECT * FROM autonomy_assets')]
    with pytest.raises(ValueError,match='ITEM4_HARD_COST_CAP'):reserve(f)
    assert before==[tuple(r) for r in db.execute('SELECT * FROM autonomy_assets')] and not f.calls

@pytest.mark.parametrize('damage',['model','uncertain-call','uncertain-asset','active-compute','direct-cost','direct-missing','scope','envelope','expiry','owner-complete'])
def test_refusal_cannot_create_new_charge(prepared,damage):
    f=prepared;db=f.accounts.db;b=f.source_binding
    if damage in {'model','uncertain-call'}:db.execute("INSERT INTO autonomy_calls VALUES('pending','scientific','x',1,'2026-10-09',?,'{}',NULL)",('RUNNING' if damage=='model' else 'UNCERTAIN',))
    elif damage=='uncertain-asset':asset(f.accounts.batch,1,ident='unknown',status='UNCERTAIN')
    elif damage=='active-compute':compute(f.accounts.batch,1,status='RUNNING')
    elif damage=='direct-cost':db.execute('UPDATE autonomy_assets SET reserved_micro_usd=0 WHERE id=?',(q.DIRECT_ID,))
    elif damage=='direct-missing':db.execute('DELETE FROM autonomy_assets WHERE id=?',(q.DIRECT_ID,))
    elif damage=='scope':b['inventory_sha256']='e'*64
    elif damage=='envelope':b['envelope']['reserved_micro_usd']=1
    elif damage=='expiry':b['expires_at']=(NOW+timedelta(days=31)).isoformat()
    else:db.execute("UPDATE autonomy_runs SET status='COMPLETE' WHERE id=?",(q.RUN,))
    before=[tuple(r) for r in db.execute('SELECT * FROM autonomy_assets')]
    with pytest.raises(ValueError):reserve(f)
    assert before==[tuple(r) for r in db.execute('SELECT * FROM autonomy_assets')] and not f.calls

def test_preparation_envelope_cannot_exceed_five_dollars(prepared):
    rates=dict(prepared.view['rates']);rates['egress_gib_cost']='100'
    with pytest.raises(ValueError,match='PREPARATION_BOUND'):q.envelope(rates)

def test_native_proof_is_required_and_failure_does_not_get_waived(prepared,monkeypatch):
    f=prepared
    monkeypatch.setattr(q,'native_qualification',lambda *a:(_ for _ in ()).throw(ValueError('synthetic invalid native proof')))
    before=[tuple(r) for r in f.accounts.db.execute('SELECT * FROM autonomy_assets')]
    with pytest.raises(ValueError,match='invalid native'):reserve(f)
    assert before==[tuple(r) for r in f.accounts.db.execute('SELECT * FROM autonomy_assets')]
