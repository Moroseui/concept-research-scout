"""Real synthetic SQLite admissions; no provider, credentials or patient inputs."""
import hashlib,json
from pathlib import Path
import pytest
from orchestrator import item4_stage1_cap as cap
from orchestrator import modal_item4_budget as budget
from test_modal_item4_budget import ledger,bound,reserve,snapshot,NOW


def selected():
    b=bound('benchmark-H100',gpu='H100',cpu=16,memory_mib=131072,timeout_seconds=3600)
    b['experiment']['billing_object_id']='ap-SyntheticH100'
    b.update(cap.PINS)
    b['execution']={'module_sha256':'3925313395199992195412e5db908e764e8215df52f59c408ba27619653993d8'}
    return b


@pytest.mark.parametrize('delta,allowed',[(-1,True),(0,True),(1,False)])
def test_cap_boundary_preserves_existing_rows_and_reserves_atomically(ledger,monkeypatch,delta,allowed):
    batch,accounts=ledger
    # Use the existing synthetic owner, not a fabricated production seal.
    monkeypatch.setattr(cap,'RUN','item4')
    b=selected();amount=b['cost']['reserved_micro_usd']
    batch.db.execute("INSERT INTO autonomy_assets VALUES('earlier','item4','{}','READY',?,'{}')",(cap.CAP-amount+delta,))
    before=tuple(batch.db.execute("SELECT * FROM autonomy_assets WHERE id='earlier'").fetchone())
    if allowed:
        assert reserve(accounts,b)
        assert not reserve(accounts,b)
        row=batch.db.execute('SELECT * FROM autonomy_compute').fetchone()
        assert row['reserved_micro_usd']==amount
        event=json.loads(batch.db.execute("SELECT payload FROM events WHERE id LIKE '%:gpu-reserved'").fetchone()[0])
        assert event['caps']=={'smoke':150000000,'projection':1200000000,'total':1275000000}
        assert event['stage1_operator_sha256']==cap.OPERATOR_SHA
    else:
        with pytest.raises(ValueError,match='ITEM4_HARD_COST_CAP'):reserve(accounts,b)
        assert batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==0
    assert tuple(batch.db.execute("SELECT * FROM autonomy_assets WHERE id='earlier'").fetchone())==before


@pytest.mark.parametrize('field',['source','image_id','spec_sha256','execution_plan_sha256','review_sha256','module','fit'])
def test_exact_scientific_milestone_required(field):
    b=selected();b['run_id']=cap.RUN
    assert cap.limit(b)==150000000
    if field=='module':b['execution']['module_sha256']='0'*64
    elif field=='fit':b['experiment']['fit_id']='smoke-coverage'
    else:b[field]='changed'
    with pytest.raises(ValueError,match='MILESTONE_SCOPE'):cap.limit(b)


def test_other_runs_full_and_quote_bound_unchanged():
    assert cap.limit(bound())==75000000
    b=selected();b['run_id']=cap.RUN;b['experiment']['stage']='FULL'
    assert cap.limit(b)==75000000
    assert (budget.PROJECTION_LIMIT,budget.TOTAL_CAP)==(1200000000,1275000000)
    with pytest.raises(ValueError,match='RESOURCE_BOUNDS'):
        budget.quote(b['resources'],snapshot()['rates'],75000001)


def test_verbatim_authority_required(tmp_path,monkeypatch):
    b=selected();b['run_id']=cap.RUN
    doc=Path(cap.__file__).resolve().parents[1]/cap.DOCUMENT
    assert hashlib.sha256(doc.read_bytes()).hexdigest()==cap.OPERATOR_SHA
    fake=tmp_path/'orchestrator/helper.py';fake.parent.mkdir();fake.write_text('synthetic')
    target=tmp_path/cap.DOCUMENT;target.parent.mkdir();target.write_bytes(doc.read_bytes()+b' ')
    monkeypatch.setattr(cap,'__file__',str(fake))
    with pytest.raises(ValueError,match='OPERATOR_CHANGED'):cap.limit(b)

@pytest.mark.parametrize('fit',sorted(cap.FITS))
def test_all_milestone_fits_and_resumed_segments_share_same_total(fit):
    b=selected();b['run_id']=cap.RUN;b['experiment']['fit_id']=fit
    for segment in [1,2,3]:
        b['experiment']['segment']=segment
        assert cap.limit(b)==150000000
