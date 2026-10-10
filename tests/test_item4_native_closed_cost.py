"""Fixed positively closed native costs, original rows and refusal boundaries."""
import copy,json,sqlite3
from types import SimpleNamespace as NS
from pathlib import Path
import pytest
from orchestrator import item4_diagnostic_native as d
from test_modal_item4_budget import snapshot
from orchestrator.modal_billing import canonical as billing_bytes

def seal(view):
    view.pop('sha256',None);view['sha256']=d.sha(billing_bytes(view));return view

@pytest.fixture
def closed():
    db=sqlite3.connect(':memory:',isolation_level=None);db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE autonomy_assets(id TEXT,run TEXT,binding TEXT,status TEXT,reserved_micro_usd INTEGER,receipt TEXT)')
    db.execute('CREATE TABLE autonomy_compute(id TEXT,run TEXT,binding TEXT,status TEXT,reserved_micro_usd INTEGER,provider_id TEXT,actual_micro_usd INTEGER,month TEXT)')
    db.execute('CREATE TABLE events(id TEXT,job TEXT,payload TEXT)')
    p=d.document(d.CORRECTED,d.CORRECTED_SHA)
    rows=[p['original_failed_asset'],p['second_failed_asset']]
    for row in rows:db.execute('INSERT INTO autonomy_assets VALUES(?,?,?,?,?,?)',tuple(row[k] for k in ('id','run','binding','status','reserved_micro_usd','receipt')))
    view=snapshot()
    # Real binding identities, synthetic billing data; no provider or live ledger.
    view.update(resolution='h',partial_hour_excluded=True,observed_at='2026-10-10T13:30:00+00:00',report_start='2026-10-10T00:00:00+00:00',report_end_exclusive='2026-10-10T13:00:00+00:00')
    view['rows']=[{'object_id':json.loads(row['receipt'])['app_id'],'interval_start':'2026-10-10T12:00:00+00:00','cost':cost,'cost_by_resource':{'cpu':cost}} for row,cost in zip(rows,['0.02512208','0.02347152'])]
    seal(view)
    yield NS(db=db),{r['id'] for r in rows},view,{r['id']:r['reserved_micro_usd'] for r in rows}
    db.close()

def test_closed_compute_release_preserves_rows_and_retains_overhead(closed):
    a,ids,view,amounts=closed;before=[tuple(r) for r in a.db.execute('SELECT * FROM autonomy_assets')]
    result=d.closed_native_amounts(a,ids,view,amounts)
    assert result=={d.FAILED_ASSET:1025123,d.SECOND_FAILED_ASSET:1023472}
    assert sum(amounts.values())-sum(result.values())==189305
    assert before==[tuple(r) for r in a.db.execute('SELECT * FROM autonomy_assets')]
    assert a.db.execute('SELECT count(*) FROM events').fetchone()[0]==2
    assert d.closed_native_amounts(a,ids,view,amounts)==result
    assert a.db.execute('SELECT count(*) FROM events').fetchone()[0]==2

@pytest.mark.parametrize('fault',['unqualified','changed-row','missing-billing','partial-hour','workspace','shared-app','corrupt-highwater'])
def test_uncertain_or_corrupt_cost_evidence_refuses(closed,fault):
    a,ids,view,amounts=closed
    if fault=='unqualified':ids.remove(d.SECOND_FAILED_ASSET)
    elif fault=='changed-row':a.db.execute('UPDATE autonomy_assets SET reserved_micro_usd=1 WHERE id=?',(d.FAILED_ASSET,))
    elif fault=='missing-billing':view['rows']=[]
    elif fault=='partial-hour':view['report_end_exclusive']='2026-10-10T12:00:00+00:00'
    elif fault=='workspace':view['workspace']='different'
    elif fault=='shared-app':a.db.execute('INSERT INTO autonomy_compute VALUES(?,?,?,?,?,?,?,?)',('other','other',json.dumps({'experiment':{'billing_object_id':view['rows'][0]['object_id']}}),'COLLECTED',1,None,1,'2026-10'))
    else:a.db.execute('INSERT INTO events VALUES(?,?,?)',('item4-billing:bad','run','{}'))
    seal(view)
    a.db.execute('BEGIN')
    try:
        with pytest.raises((ValueError,KeyError)):d.closed_native_amounts(a,ids,view,amounts)
    finally:a.db.execute('ROLLBACK')
    assert a.db.execute('SELECT count(*) FROM events WHERE id LIKE ?',('%:closed-native-cost:%',)).fetchone()[0]==0

def test_later_higher_billing_increases_effective_cost(closed):
    a,ids,view,amounts=closed
    view['rows'][0]['cost']='0.2';view['rows'][0]['cost_by_resource']={'cpu':'0.2'};seal(view)
    assert d.closed_native_amounts(a,ids,view,amounts)[d.FAILED_ASSET]==1200000
    # A smaller later snapshot cannot undercut a retained hourly high water.
    saved={'schema':'item4-billing-highwater/v1','snapshot':view};raw=d.canonical(saved).decode()
    a.db.execute('INSERT INTO events VALUES(?,?,?)',('item4-billing:'+d.sha(raw.encode()),'run',raw))
    later=copy.deepcopy(view);later['rows'][0]['cost']='0.01';later['rows'][0]['cost_by_resource']={'cpu':'0.01'};seal(later)
    assert d.closed_native_amounts(a,ids,later,amounts)[d.FAILED_ASSET]==1200000


def test_observation_persists_native_highwater_before_admission(closed,monkeypatch):
    from datetime import datetime
    from orchestrator import modal_terminal_cost as terminal,item4_closed_asset_billing as old
    a,ids,view,amounts=closed
    monkeypatch.setattr(old,'billing_objects',lambda accounts:{})
    terminal.observe_billing(a,view,datetime.fromisoformat(view['observed_at']))
    saved=[json.loads(r[0]) for r in a.db.execute("SELECT payload FROM events WHERE id LIKE 'item4-billing:%'")]
    assert len(saved)==2 and {x['object_id'] for x in saved}=={r['object_id'] for r in view['rows']}
    later=copy.deepcopy(view)
    for row in later['rows']:row['cost']='0.001';row['cost_by_resource']={'cpu':'0.001'}
    seal(later)
    assert d.closed_native_amounts(a,ids,later,amounts)=={d.FAILED_ASSET:1025123,d.SECOND_FAILED_ASSET:1023472}


def test_third_failed_attempt_keeps_its_full_reservation(closed):
    a,ids,view,amounts=closed
    row=d.document(d.PROGRESS,d.PROGRESS_SHA)['third_failed_asset']
    a.db.execute('INSERT INTO autonomy_assets VALUES(?,?,?,?,?,?)',tuple(row[k] for k in ('id','run','binding','status','reserved_micro_usd','receipt')))
    before=[tuple(r) for r in a.db.execute('SELECT * FROM autonomy_assets')]
    ids.add(row['id']);amounts[row['id']]=row['reserved_micro_usd']
    result=d.closed_native_amounts(a,ids,view,amounts)
    assert result[row['id']]==1118950
    assert before==[tuple(r) for r in a.db.execute('SELECT * FROM autonomy_assets')]
    assert not a.db.execute('SELECT 1 FROM events WHERE id LIKE ?',(row['id']+':%',)).fetchone()


@pytest.mark.parametrize('field',['binding','status','reserved_micro_usd','receipt','run'])
def test_third_original_failure_row_cannot_change(field):
    row=d.document(d.PROGRESS,d.PROGRESS_SHA)['third_failed_asset']
    assert d.historical_asset(row)
    changed=copy.deepcopy(row);changed[field]=1 if field=='reserved_micro_usd' else 'changed'
    with pytest.raises(ValueError,match='THIRD_FAILED_ROW_CHANGED'):d.historical_asset(changed)


@pytest.mark.parametrize('field',['asset_id','source','status','exit_code','scientific_acceptance'])
def test_third_failure_qualification_cannot_be_substituted(monkeypatch,field):
    frozen=d.document(d.PROGRESS,d.PROGRESS_SHA)
    monkeypatch.setattr(d.subprocess,'check_output',lambda *a,**kw:json.dumps(frozen['qualification']).encode())
    assert d.progress_failure()==frozen
    changed=copy.deepcopy(frozen['qualification']);changed[field]='changed'
    monkeypatch.setattr(d.subprocess,'check_output',lambda *a,**kw:json.dumps(changed).encode())
    with pytest.raises(ValueError,match='THIRD_NATIVE_FAILURE'):d.progress_failure()
