import json
import sqlite3
from types import SimpleNamespace as NS
from pathlib import Path
import pytest
from tools import item4_image_runtime as adapter
from orchestrator import modal_environment_budget as budget
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from test_modal_pinned_image import unreserved_fixture,inventory_fixture,experiment,root,view
from test_modal_direct_budget import NOW
from test_modal_environment_budget import asset


def stored(db,ident,status='RUNNING',amount=1951600):
    body={'purpose':'M4_ITEM6_CPU','run_id':'diagnostics-b203ee1ce27e909d9d78d44a'}
    db.execute('INSERT INTO autonomy_compute VALUES(?,?,?,?,?,?,NULL,?)',
        (ident,body['run_id'],canonical(body).decode(),status,amount,'sb-stopped','2026-10'))


@pytest.mark.parametrize('failure',[None,'unknown_running','unknown_uncertain','over_cap','no_proof'])
def test_real_budget_keeps_old_rows_and_charges_and_other_refusals(unreserved_fixture,monkeypatch,failure):
    f=unreserved_fixture;db=f.accounts.db
    for ident in adapter.CPU_PARENTS:stored(db,ident)
    if failure=='unknown_running':stored(db,'unknown')
    if failure=='unknown_uncertain':stored(db,'unknown','UNCERTAIN')
    if failure=='over_cap':asset(f.accounts.batch,budget.SMOKE_CAP)
    if failure!='no_proof':monkeypatch.setattr(budget,'terminal_failed_compute',lambda a:set(adapter.CPU_PARENTS))
    before=[tuple(x) for x in db.execute('SELECT * FROM autonomy_compute')]
    prior=[tuple(x) for x in db.execute('SELECT * FROM autonomy_assets')]
    def reserve():return budget.reserve(f.accounts,digest(canonical(f.binding)),adapter.RUN,f.binding,billing_snapshot=view(),now=NOW)
    if failure:
        with pytest.raises(ValueError,match='ITEM4_HARD_COST_CAP' if failure=='over_cap' else 'MODAL_ACTIVE_OR_UNCERTAIN_COMPUTE'):reserve()
        assert [tuple(x) for x in db.execute('SELECT * FROM autonomy_assets')]==prior
    else:
        assert reserve()
        assert db.execute('SELECT reserved_micro_usd FROM autonomy_assets').fetchone()[0]==f.binding['envelope']['cost']['reserved_micro_usd']
    assert [tuple(x) for x in db.execute('SELECT * FROM autonomy_compute')]==before
    assert db.execute('SELECT sum(reserved_micro_usd) FROM autonomy_compute WHERE id IN (?,?)',tuple(adapter.CPU_PARENTS)).fetchone()[0]==3903200


@pytest.mark.parametrize('damage',[None,'helper','missing','status','run','provider','binding','proof','first_stop','first_terminal'])
def test_proof_connection_restores_modules_and_refuses_changed_success(tmp_path,monkeypatch,damage):
    import orchestrator
    from orchestrator import manual_host_guard
    first_stop=tmp_path/'first-stop.json'
    monkeypatch.setattr(manual_host_guard,'trusted',lambda p:first_stop if Path(p).name=='parent-failed-stop.json' else Path(p))
    proof={'result':{'binding_sha256':'d9bd52cf0b27045e1e23ba018ac44d9ed25cb2ab8ccf81f8c22cf33b4fb264e3','files':{},'schema':'modal-result/v1','status':'FAILED'},'stop':{'provider_id':'sb-01M4CJFPRC3SJ1ZXPXG6APJA5H','terminated':True},'reservation_retained':True}
    if damage=='first_terminal':proof['stop']['terminated']=False
    first_stop.write_bytes(canonical(proof));monkeypatch.setattr(adapter,'FIRST_STOP_SHA',digest(first_stop.read_bytes()))
    if damage=='first_stop':first_stop.write_bytes(b'changed')
    helper=tmp_path/'tools/item6_native_mount_service.py';helper.parent.mkdir();helper.write_bytes(b'original-helper')
    monkeypatch.setattr(adapter,'CPU_ROOT',tmp_path);monkeypatch.setattr(adapter,'CPU_HELPER_SHA',digest(helper.read_bytes()))
    binding=canonical({'synthetic':'binding'}).decode();ident=digest(binding.encode());monkeypatch.setattr(adapter,'CPU_SUCCESS',ident)
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE autonomy_compute(id,run,status,provider_id,binding)')
    db.execute('INSERT INTO autonomy_compute VALUES(?,?,?,?,?)',(ident,'diagnostics-b203ee1ce27e909d9d78d44a','COLLECTED','sb-01M4CTVGT1CC1CSPY149KG94BK',binding))
    if damage=='helper':helper.write_bytes(b'changed')
    elif damage=='missing':db.execute('DELETE FROM autonomy_compute')
    elif damage in {'status','run','binding'}:db.execute('UPDATE autonomy_compute SET '+damage+'=?',('changed',))
    elif damage=='provider':db.execute("UPDATE autonomy_compute SET provider_id='sb-wrong'")
    before=[tuple(x) for x in db.execute('SELECT * FROM autonomy_compute')]
    checked=[]
    def load(name,path):
        if name=='_image_cpu_original':return NS(checked=lambda:checked.append('verified installed sources'))
        if name=='_image_cpu_guard':return object()
        assert name=='_image_cpu_retry'
        def proof(accounts,value):
            assert accounts.db is db and value==json.loads(binding)
            return {'unexpected'} if damage=='proof' else set(adapter.CPU_PARENTS)
        return NS(retained_parent=proof)
    monkeypatch.setattr(adapter,'load_source',load)
    prior=getattr(orchestrator,'diagnostics_native_guard',None)
    try:
        if damage:
            with pytest.raises(ValueError):adapter.stopped_item6(NS(db=db))
        else:assert adapter.stopped_item6(NS(db=db))==adapter.CPU_PARENTS
        assert getattr(orchestrator,'diagnostics_native_guard',None) is prior
        assert [tuple(x) for x in db.execute('SELECT * FROM autonomy_compute')]==before
    finally:db.close()
