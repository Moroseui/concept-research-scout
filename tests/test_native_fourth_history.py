import copy,json,subprocess
import pytest
from orchestrator import item4_diagnostic_native as d,modal_environment_budget as budget
from orchestrator.modal_executor import canonical
from test_item4_diagnostic_native_execution import unreserved,reserve,unreserved_fixture,inventory_fixture,experiment,root,view
from test_modal_environment_budget import asset

@pytest.mark.parametrize('which',['first','second','third','fourth'])
def test_every_exact_historical_native_is_recognized_without_current_selection(which):
    choices={'first':lambda:d.document(d.CORRECTED,d.CORRECTED_SHA)['original_failed_asset'],
      'second':lambda:d.document(d.CORRECTED,d.CORRECTED_SHA)['second_failed_asset'],
      'third':lambda:d.document(d.PROGRESS,d.PROGRESS_SHA)['third_failed_asset'],
      'fourth':lambda:d.document(d.FOURTH,d.FOURTH_SHA)['row']}
    row=choices[which]()
    assert d.historical_asset(row) and budget.selected_asset(row)
    for field in ('binding','status','reserved_micro_usd','receipt','run'):
        changed=copy.deepcopy(row);changed[field]=0 if field=='reserved_micro_usd' else 'changed'
        with pytest.raises(ValueError,match='ROW_CHANGED'):budget.selected_asset(changed)

@pytest.mark.parametrize('damage',[None,'qualification','exception'])
def test_fourth_reuses_original_readonly_terminal_qualifier(monkeypatch,damage):
    frozen=d.document(d.FOURTH,d.FOURTH_SHA);calls=[]
    def checked(argv,timeout):
        calls.append((argv,timeout))
        if damage=='exception':raise subprocess.CalledProcessError(1,argv)
        proof=dict(frozen['qualification'])
        if damage=='qualification':proof['status']='PASS'
        return canonical(proof)
    monkeypatch.setattr(d.subprocess,'check_output',checked)
    if damage:
        with pytest.raises((ValueError,subprocess.CalledProcessError)):d.report_failure()
    else:assert d.report_failure()==frozen
    assert calls[0][0][-1]=='--diagnostic-report-failure' and calls[0][1]==120

@pytest.mark.parametrize('damage',[None,'cap','changed_row','unknown','live'])
def test_real_admission_counts_preserved_fourth_and_refuses_other_history(unreserved,monkeypatch,damage):
    f=unreserved;row=d.document(d.FOURTH,d.FOURTH_SHA)['row'];db=f.accounts.db
    db.execute('INSERT INTO autonomy_assets VALUES(?,?,?,?,?,?)',tuple(row[k] for k in ('id','run','binding','status','reserved_micro_usd','receipt')))
    # The subprocess qualifier is tested separately above. The real transaction,
    # historical row checks, reservations and cap accounting are exercised here.
    def qualify(accounts,binding):
        old=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(d.FOURTH_FAILED_ASSET,)).fetchone()
        assert d.historical_asset(old)
        return {d.FOURTH_FAILED_ASSET},set()
    monkeypatch.setattr(d,'retained_terminal',qualify)
    if damage=='cap':asset(f.accounts.batch,d.STAGE_CAP-row['reserved_micro_usd']-f.binding['envelope']['cost']['reserved_micro_usd']+1)
    elif damage=='changed_row':db.execute('UPDATE autonomy_assets SET reserved_micro_usd=reserved_micro_usd-1')
    elif damage=='live':db.execute("UPDATE autonomy_assets SET status='RESERVED'")
    elif damage=='unknown':
        other=dict(row);other['id']='d'*64
        db.execute('INSERT INTO autonomy_assets VALUES(?,?,?,?,?,?)',tuple(other[k] for k in ('id','run','binding','status','reserved_micro_usd','receipt')))
    before=[dict(r) for r in db.execute('SELECT * FROM autonomy_assets ORDER BY id')]
    if damage:
        with pytest.raises(ValueError):reserve(f)
        assert [dict(r) for r in db.execute('SELECT * FROM autonomy_assets ORDER BY id')]==before
    else:
        assert reserve(f)
        assert dict(db.execute('SELECT * FROM autonomy_assets WHERE id=?',(row['id'],)).fetchone())==row
        event=json.loads(db.execute("SELECT payload FROM events WHERE id LIKE '%:assets-reserved'").fetchone()[0])
        assert event['prior_item4_smoke_micro_usd']>=row['reserved_micro_usd']
        assert event['caps']=={'smoke':150000000,'total':1275000000}
    assert not f.calls
