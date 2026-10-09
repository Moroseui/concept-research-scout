"""Real existing SQLite accounting, synthetic billing and no paid operations."""
from datetime import datetime,timezone
import hashlib,json
import pytest
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_budget import ComputeAccounts
from orchestrator import modal_item4_budget as item4
from orchestrator.modal_billing import canonical

NOW=datetime(2026,10,6,2,30,tzinfo=timezone.utc)
RATES={'cpu_hour_cost_sandbox':'.1419','mem_gib_hour_cost_sandbox':'.024',
       'gpu_hour_cost_a100_80gb':'2.5','gpu_hour_cost_h100':'3.95','gpu_hour_cost_b200':'6.25'}


def snapshot(spent='0'):
    body={'schema':'modal-billing-snapshot/v1','workspace':'moroseui','observed_at':NOW.isoformat(),
          'rates':RATES,'rows':[],'summary':{'metered_cost':spent,'billed_cost':spent,'adjustments':{}}}
    return {**body,'sha256':hashlib.sha256(canonical(body)).hexdigest()}


def bound(fit='one',stage='SMOKE',**resources):
    limits={'gpu':'A100-80GB','cpu':4,'memory_mib':8192,'timeout_seconds':60,**resources}
    return {'run_id':'item4','spec_sha256':'a'*64,'resources':limits,'overhead_micro_usd':0,
        'cost':item4.quote(limits,RATES,0),
        'experiment':{'backlog_item':4,'authority_sha256':item4.AUTHORITY,'team_authority_sha256':item4.TEAM_AUTHORITY,
           'fit_id':fit,'stage':stage,'segment':1,'billing_object_id':'ap-'+fit}}


def reserve(accounts,binding,**kw):
    ident=hashlib.sha256(json.dumps(binding,sort_keys=True).encode()).hexdigest()
    return accounts.reserve_item4(ident,'item4',binding,billing_snapshot=kw.pop('billing_snapshot',snapshot()),now=NOW,**kw)


@pytest.fixture
def ledger(tmp_path):
    batch=BatchAccounts(tmp_path/'ledger')
    batch.register_run('item4',{'backlog_item':4,'experiment_authority_sha256':item4.AUTHORITY})
    return batch,ComputeAccounts(batch)


def test_same_request_once_independent_fits_share_existing_ledger(ledger):
    batch,accounts=ledger
    assert reserve(accounts,bound()) is True
    rows=[tuple(row) for row in batch.db.execute('SELECT * FROM autonomy_compute')]
    assert reserve(accounts,bound()) is False
    assert [tuple(row) for row in batch.db.execute('SELECT * FROM autonomy_compute')]==rows
    assert reserve(accounts,bound('two')) is True
    assert batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==2
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    receipt=json.loads(batch.db.execute('SELECT payload FROM events WHERE id LIKE ?',('%:gpu-reserved',)).fetchone()[0])
    assert receipt['billing_snapshot']==snapshot() and receipt['caps']['smoke']==75_000_000


def test_no_second_realization_or_unreviewed_resume(ledger):
    _,accounts=ledger;reserve(accounts,bound())
    altered=bound();altered['spec_sha256']='f'*64
    with pytest.raises(ValueError,match='ITEM4_FIT_ALREADY_EXISTS_NO_RESTART'):reserve(accounts,altered)
    altered['experiment']['segment']=2
    with pytest.raises(ValueError,match='ITEM4_RESUME_TERMINAL_PROOF_REQUIRED'):reserve(accounts,altered)


def test_concurrency_and_cumulative_smoke_cap(ledger):
    _,accounts=ledger
    for i in range(50):assert reserve(accounts,bound('fit'+str(i)))
    with pytest.raises(ValueError,match='ITEM4_GPU_CONCURRENCY_LIMIT'):reserve(accounts,bound('extra'))


def test_hard_smoke_cap_includes_assets_and_refuses_atomically(ledger):
    batch,accounts=ledger
    batch.db.execute("INSERT INTO autonomy_assets VALUES('data','item4','{}','READY',74000000,'{}')")
    b=bound(timeout_seconds=3600)
    with pytest.raises(ValueError,match='ITEM4_HARD_COST_CAP'):reserve(accounts,b)
    assert batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==0


def test_full_requires_bound_originals_not_generic_acceptance(ledger):
    batch,accounts=ledger;b=bound(stage='FULL')
    with pytest.raises(ValueError,match='ITEM4_ACCEPTED_SMOKE_PROJECTION_REQUIRED'):reserve(accounts,b)
    proof={'status':'ACCEPTED','run_id':'item4','spec_sha256':'a'*64,'full_projection_micro_usd':1200000001}
    batch.db.execute('INSERT INTO events VALUES(?,?,?)',('item4:full-projection-approved','item4',json.dumps(proof)))
    with pytest.raises(ValueError,match='ITEM4_FULL_BOUND_PROJECTION_REQUIRED'):reserve(accounts,b)


@pytest.mark.parametrize('kind',['compute','call','asset'])
def test_uncertainty_blocks_without_another_reservation(ledger,kind):
    batch,accounts=ledger
    if kind=='compute':batch.db.execute("INSERT INTO autonomy_compute VALUES('old','old','{}','UNCERTAIN',100,NULL,NULL,'2026-10')")
    if kind=='call':batch.db.execute("INSERT INTO autonomy_calls VALUES('old','scientific','old',1,'2026-10-06','UNCERTAIN','{}',NULL)")
    if kind=='asset':batch.db.execute("INSERT INTO autonomy_assets VALUES('old','old','{}','UNCERTAIN',100,'{}')")
    with pytest.raises(ValueError,match='UNCERTAIN'):reserve(accounts,bound())
    assert batch.db.execute("SELECT count(*) FROM autonomy_compute WHERE run='item4'").fetchone()[0]==0


def test_provider_headroom_and_stale_observation_refuse(ledger):
    _,accounts=ledger
    with pytest.raises(ValueError,match='ITEM4_PROVIDER_HEADROOM_WAIT'):reserve(accounts,bound(),billing_snapshot=snapshot('1000'))
    old=snapshot();old['observed_at']='2026-10-06T01:00:00+00:00';body=dict(old);body.pop('sha256');old['sha256']=hashlib.sha256(canonical(body)).hexdigest()
    with pytest.raises(ValueError,match='MODAL_BILLING_SNAPSHOT_STALE'):reserve(accounts,bound(),billing_snapshot=old)


def test_binding_rates_and_owner_scope_are_required(ledger):
    batch,accounts=ledger;b=bound();b['cost']['reserved_micro_usd']=1
    with pytest.raises(ValueError,match='ITEM4_COST_OR_RUN_BINDING'):reserve(accounts,b)
    batch.db.execute("UPDATE autonomy_runs SET binding='{}' WHERE id='item4'")
    with pytest.raises(ValueError,match='ITEM4_SELECTED_RUN_REQUIRED'):reserve(accounts,bound())


def test_fixed_hardware_choices_use_actual_sandbox_prices():
    for gpu in ('A100-80GB','H100','B200',None):
        q=item4.quote({'gpu':gpu,'cpu':16,'memory_mib':65536,'timeout_seconds':3600},RATES,0)
        assert q['compute_micro_usd']>=3806400 # CPU and RAM alone, not Function prices.
    with pytest.raises(ValueError,match='ITEM4_RESOURCE_TYPES'):item4.quote({'gpu':'H200','cpu':16,'memory_mib':65536,'timeout_seconds':60},RATES,0)
    with pytest.raises(ValueError,match='ITEM4_ACTUAL_RATES_REQUIRED'):item4.quote(bound()['resources'],{},0)


def test_operator_authority_files_match_selected_constants():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    assert hashlib.sha256((root/'docs/SPRINT13B_EXECUTION_OPERATOR_DECISION.txt').read_bytes()).hexdigest()==item4.AUTHORITY
    assert hashlib.sha256((root/'docs/SPRINT13B_TEAM_OPERATOR_DECISION.txt').read_bytes()).hexdigest()==item4.TEAM_AUTHORITY


# The input owner has no scientific calls; its spending still follows item4.
from test_modal_direct_budget import prepared
from orchestrator.modal_executor import canonical as asset_canonical
from orchestrator.manual_executor import digest
from orchestrator import modal_direct_budget as direct

def test_preparation_cost_carries_to_different_scientific_owner(prepared):
    batch,a,b,v=prepared;direct.reserve(a,digest(asset_canonical(b)),b["run_id"],b,billing_snapshot=v,now=NOW)
    ident=digest(asset_canonical(b));a.finish_assets(ident,'READY',{'status':'VERIFIED'})
    batch.complete_run('item4-inputs',{'administrative_input_preparation_only':True})
    batch.register_run('item4',{'backlog_item':4,'experiment_authority_sha256':item4.AUTHORITY})
    scientific=bound();scientific['cost']=item4.quote(scientific['resources'],v['rates'],0)
    cost=scientific['cost']['reserved_micro_usd']
    # Preserved earlier scientific costs leave room only if preparation is wrongly ignored.
    old=bound('old');old['purpose']='M4_ITEM4'
    batch.db.execute("INSERT INTO autonomy_compute (id,run,binding,status,reserved_micro_usd,provider_id,actual_micro_usd,month) VALUES('old','item4',?,'ACCOUNTED',?,'sb-old',NULL,'2026-10')",
      (asset_canonical(old).decode(),item4.SMOKE_CAP-cost))
    with pytest.raises(ValueError,match='^ITEM4_HARD_COST_CAP$'):
        a.reserve_item4(digest(asset_canonical(scientific)),'item4',scientific,billing_snapshot=v,now=NOW)
    assert batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==1
