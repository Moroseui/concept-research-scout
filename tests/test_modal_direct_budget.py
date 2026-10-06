"""Existing SQLite budget rows and authenticated-shaped synthetic billing only."""
import json
import pytest
from datetime import datetime,timezone
NOW=datetime(2026,10,6,2,30,tzinfo=timezone.utc)
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_budget import ComputeAccounts
from orchestrator import modal_direct_budget as direct, modal_item4_policy as item4
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest


def billing():
    value={'schema':'modal-billing-snapshot/v1','workspace':'moroseui','observed_at':NOW.isoformat(),
           'rates':{'cpu_hour_cost_sandbox':'.1419','mem_gib_hour_cost_sandbox':'.024',
                    'volume_storage_gib_month_cost':'.09','egress_gib_cost':'.04',
                    'gpu_hour_cost_a100_80gb':'2.5','gpu_hour_cost_h100':'3.95','gpu_hour_cost_b200':'6.25'},
           'rows':[],'summary':{'metered_cost':'0','billed_cost':'0','adjustments':{}},'sha256':'pending'}
    from orchestrator.modal_billing import canonical as compact
    body=dict(value);body.pop('sha256');value['sha256']=digest(compact(body));return value


@pytest.fixture
def prepared(tmp_path):
    batch=BatchAccounts(tmp_path/'ledger');accounts=ComputeAccounts(batch)
    owner={'purpose':direct.PURPOSE,'authority_sha256':item4.AUTHORITY}
    batch.register_run('item4-inputs',owner)
    view=billing();value={'purpose':direct.PURPOSE,'authority_sha256':item4.AUTHORITY,
      'download_authority_sha256':direct.DOWNLOAD_AUTHORITY,'team_authority_sha256':item4.TEAM_AUTHORITY,
      'run_id':'item4-inputs','download_bytes':54323796401,'envelope':direct.envelope(54323796401,view['rates']),
      'package_manifest_sha256':'a'*64}
    return batch,accounts,value,view


def reserve(f):
    _,a,b,v=f;return direct.reserve(a,digest(canonical(b)),b['run_id'],b,billing_snapshot=v,now=NOW)


def test_direct_cpu_preparation_is_once_and_consumes_no_model_allowance(prepared):
    batch,a,b,v=prepared
    assert reserve(prepared) is True
    amount=b['envelope']['cost']['reserved_micro_usd'];assert 1_000_000<amount<10_000_000
    old=[tuple(x) for x in batch.db.execute('SELECT * FROM autonomy_assets')]
    assert reserve(prepared) is False
    assert [tuple(x) for x in batch.db.execute('SELECT * FROM autonomy_assets')]==old
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    assert batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==0
    assert b['envelope']['resources']['gpu'] is None



@pytest.mark.parametrize('change',['cost','authority','download-authority','owner','running','unknown','asset','headroom'])
def test_no_reservation_on_guard_failure(prepared,change):
    batch,a,b,v=prepared
    if change=='cost':b['envelope']['cost']['reserved_micro_usd']=1
    elif change=='authority':b['authority_sha256']='f'*64
    elif change=='download-authority':b['download_authority_sha256']='f'*64
    elif change=='owner':batch.db.execute("UPDATE autonomy_runs SET binding='{}'")
    elif change in ('running','unknown'):
        status='RUNNING' if change=='running' else 'UNCERTAIN'
        batch.db.execute("INSERT INTO autonomy_calls VALUES('old','scientific','old',1,'2026-10-06',?,'{}',NULL)",(status,))
    elif change=='asset':batch.db.execute("INSERT INTO autonomy_assets VALUES('old','other','{}','UNCERTAIN',100,NULL)")
    else:
        v['summary']['metered_cost']='1000';from orchestrator.modal_billing import canonical as compact
        body=dict(v);body.pop('sha256');v['sha256']=digest(compact(body))
    with pytest.raises(ValueError):reserve(prepared)
    assert batch.db.execute("SELECT count(*) FROM autonomy_assets WHERE run='item4-inputs'").fetchone()[0]==0


def test_no_fresh_preparation_owner_can_duplicate_completed_download(prepared):
    batch,a,b,v=prepared;reserve(prepared);a.finish_assets(digest(canonical(b)),'READY',{'status':'VERIFIED'})
    batch.complete_run('item4-inputs',{'administrative_only':True})
    batch.register_run('another',{'purpose':direct.PURPOSE,'authority_sha256':item4.AUTHORITY})
    b['run_id']='another'
    with pytest.raises(ValueError,match='^DIRECT_ASSET_ALREADY_PREPARED_NO_NEW_RESERVATION$'):reserve(prepared)
    assert batch.db.execute('SELECT count(*) FROM autonomy_assets').fetchone()[0]==1
