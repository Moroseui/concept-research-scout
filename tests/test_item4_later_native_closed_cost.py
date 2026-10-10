"""Only four positively qualified fixed attempts receive compute-only credit."""
import copy,json
from pathlib import Path
import pytest
from orchestrator import item4_diagnostic_native as d
from test_item4_native_closed_cost import closed,seal

@pytest.fixture
def later(closed):
    a,ids,view,amounts=closed
    frozen=json.loads((Path(d.__file__).resolve().parents[1]/'docs/ITEM4_CLOSED_NATIVE_LATER_COST_PRIVATE.json').read_bytes())
    for row in frozen['rows'].values():
        a.db.execute('INSERT INTO autonomy_assets VALUES(?,?,?,?,?,?)',tuple(row[k] for k in ('id','run','binding','status','reserved_micro_usd','receipt')))
        ids.add(row['id']);amounts[row['id']]=row['reserved_micro_usd']
    return a,ids,copy.deepcopy(frozen['billing']),amounts,frozen

def invoke(case):
    a,ids,view,amounts,_=case
    a.db.execute('BEGIN')
    try:
        result=d.closed_native_amounts(a,ids,view,amounts,include_later=True)
        a.db.execute('COMMIT');return result
    except BaseException:a.db.execute('ROLLBACK');raise

def test_four_costs_are_exact_and_originals_and_overhead_stay(later):
    a,ids,view,amounts,frozen=later
    before=[tuple(r) for r in a.db.execute('SELECT * FROM autonomy_assets')]
    result=invoke(later)
    assert sum(result.values())==4107872
    for ident,actual in frozen['actual_floor_micro_usd'].items():assert result[ident]==1000000+actual
    assert sum(amounts.values())-sum(result.values())==367928
    assert before==[tuple(r) for r in a.db.execute('SELECT * FROM autonomy_assets')]
    assert a.db.execute('SELECT count(*) FROM events').fetchone()[0]==4
    assert invoke(later)==result and a.db.execute('SELECT count(*) FROM events').fetchone()[0]==4

@pytest.mark.parametrize('index',[0,1])
@pytest.mark.parametrize('fault',['unqualified','running','changed-reservation','changed-receipt','missing'])
def test_open_uncertain_unqualified_or_changed_attempt_never_released(later,index,fault):
    a,ids,view,amounts,frozen=later;ident=sorted(frozen['rows'])[index]
    if fault=='unqualified':ids.remove(ident)
    elif fault=='running':a.db.execute("UPDATE autonomy_assets SET status='RUNNING' WHERE id=?",(ident,))
    elif fault=='changed-reservation':a.db.execute('UPDATE autonomy_assets SET reserved_micro_usd=0 WHERE id=?',(ident,))
    elif fault=='changed-receipt':a.db.execute("UPDATE autonomy_assets SET receipt='{}' WHERE id=?",(ident,))
    else:a.db.execute('DELETE FROM autonomy_assets WHERE id=?',(ident,))
    before=list(a.db.iterdump())
    with pytest.raises(ValueError):invoke(later)
    assert list(a.db.iterdump())==before

def test_billing_window_must_cover_last_terminal_hour(later):
    a,ids,view,amounts,frozen=later;view['report_end_exclusive']='2026-10-10T15:00:00+00:00';seal(view)
    with pytest.raises(ValueError):invoke(later)
    assert not a.db.execute('SELECT 1 FROM events').fetchone()

def test_later_observed_excess_is_not_capped_at_original_reservation(later):
    a,ids,view,amounts,frozen=later;ident=sorted(frozen['rows'])[0];app=json.loads(frozen['rows'][ident]['receipt'])['app_id']
    row=next(r for r in view['rows'] if r['object_id']==app);row['cost']='0.2';row['cost_by_resource']={'CPU':'0.2'};seal(view)
    assert invoke(later)[ident]>=1200000

def test_unselected_defaults_remain_conservative(later):
    a,ids,view,amounts,frozen=later
    result=d.closed_native_amounts(a,ids,view,amounts)
    assert all(result[ident]==1118950 for ident in frozen['rows'])
    assert not any(a.db.execute('SELECT 1 FROM events WHERE id LIKE ?',(ident+':closed-native-cost:%',)).fetchone() for ident in frozen['rows'])

def test_shared_billing_app_refuses_without_partial_credit(later):
    a,ids,view,amounts,frozen=later;app=json.loads(next(iter(frozen['rows'].values()))['receipt'])['app_id']
    a.db.execute('INSERT INTO autonomy_compute VALUES(?,?,?,?,?,?,?,?)',('other','other',json.dumps({'experiment':{'billing_object_id':app}}),'COLLECTED',1,None,1,'2026-10'))
    before=list(a.db.iterdump())
    with pytest.raises(ValueError):invoke(later)
    assert list(a.db.iterdump())==before
