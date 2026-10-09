"""Two-fit setup uses real reservations and retains all package-consumer guards."""
from copy import deepcopy
from types import SimpleNamespace as NS
from datetime import timedelta
import pytest
from orchestrator import item4_smoke_handoff as h
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from test_modal_item4_budget import ledger, bound, NOW, RATES
from test_item4_benchmark_handoff import policy, billing

@pytest.fixture
def scoped(monkeypatch):
    original=policy();original['preprocessing_runtime']['image_id']='im-synthetic'
    monkeypatch.setattr(h.base,'contract',lambda:deepcopy(original))
    monkeypatch.setattr(h.cap,'RUN','item4')
    monkeypatch.setattr(h.cap,'PINS',{'source':'synthetic','image_id':'im-synthetic'})
    p=deepcopy(original)
    p.update(fits=deepcopy(h.FITS),selected_gpu='H100',measured_hardware={
        'path':'/synthetic/lane/measured-projections/'+'e'*64+'.json','sha256':'e'*64})
    return p

@pytest.mark.parametrize('field',['source','run_id','fits','selected_gpu','measured_hardware','code_hashes'])
def test_modified_scope_refused(scoped,field):
    p=deepcopy(scoped);p[field]='changed'
    with pytest.raises(ValueError):h.policy_sha(p)


def test_scoped_reservation_uses150_preserves_old_rows_and_originals(ledger,scoped):
    batch,accounts=ledger
    batch.db.execute("INSERT INTO autonomy_assets VALUES('old','item4','{}','READY',148000000,'{}')")
    ident=h.reserve(accounts,scoped,billing(),NOW)
    assert batch.db.execute("SELECT reserved_micro_usd FROM autonomy_assets WHERE id='old'").fetchone()[0]==148000000
    row=batch.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
    assert row['reserved_micro_usd']==1000000 and row['status']=='RESERVED'
    with pytest.raises(ValueError,match='EXISTING_PREPARATION'):h.reserve(accounts,scoped,billing(),NOW)

@pytest.mark.parametrize('cause',['cap','running','uncertain','foreign-asset','rate','stale'])
def test_refusals_create_no_reservation(ledger,scoped,cause):
    batch,accounts=ledger;v=billing()
    if cause=='cap':batch.db.execute("INSERT INTO autonomy_assets VALUES('old','item4','{}','READY',149000001,'{}')")
    elif cause in {'running','uncertain'}:
        batch.db.execute("INSERT INTO autonomy_compute VALUES('old','item4',?,?,100,NULL,NULL,'2026-10')",
            (canonical(bound()).decode(),cause.upper()))
    elif cause=='foreign-asset':batch.db.execute("INSERT INTO autonomy_assets VALUES('old','other','{}','UNCERTAIN',1,'{}')")
    elif cause=='rate':v['rates']['volume_storage_gib_month_cost']='.10'
    else:v['observed_at']='2026-10-01T00:00:00+00:00'
    before=[dict(x) for x in batch.db.execute('SELECT * FROM autonomy_assets')]
    with pytest.raises(ValueError):h.reserve(accounts,scoped,v,NOW)
    assert before==[dict(x) for x in batch.db.execute('SELECT * FROM autonomy_assets')]


def test_two_distinct_apps_and_progress_reuse_exact_package(scoped):
    ready={'status':'READY','contract_sha256':h.policy_sha(scoped),
        'reservation_id':digest(canonical(h.asset_binding(scoped))),
        'package':{'id':'vo-originalPackage'},'fits':{}}
    for i,f in enumerate(h.FITS):
        ready['fits'][f['fit_id']]={'app_name':'smoke-'+str(i),'app_id':'ap-new'+str(i),
            'progress':{'id':'vo-new'+str(i),'name':'progress-'+str(i)}}
    rows=h.runtime_rows(scoped,ready,RATES)
    assert [r['fit'] for r in rows]==['smoke-A1_repeat','smoke-A1_repeat2']
    assert {r['binding']['resources']['gpu'] for r in rows}=={'H100'}
    assert {r['binding']['package_volume_id'] for r in rows}=={'vo-originalPackage'}
    assert len({r['binding']['experiment']['billing_object_id'] for r in rows})==2
    assert len({r['binding']['progress']['volume_id'] for r in rows})==2
    assert all(r['binding']['experiment']['segment']==1 for r in rows)
    ready['contract_sha256']='f'*64
    with pytest.raises(ValueError,match='ASSET_RECEIPT'):h.runtime_rows(scoped,ready,RATES)

@pytest.mark.parametrize('status',['RESERVED','SUBMITTED','RUNNING','UNCERTAIN','FAILED'])
def test_shared_cleanup_refuses_every_nonterminal_consumer(ledger,scoped,monkeypatch,tmp_path,status):
    batch,accounts=ledger;calls=[]
    monkeypatch.setattr(h.base,'state',lambda p:tmp_path)
    monkeypatch.setattr(h,'shared_package',lambda a:{'id':'vo-shared'})
    monkeypatch.setattr(h.base,'cleanup_package',lambda *a:calls.append(a))
    b=bound();b['package_volume_id']='vo-shared';b['experiment']['billing_object_id']='ap-unlistedConsumer'
    batch.db.execute("INSERT INTO autonomy_compute VALUES('old','item4',?,?,100,NULL,NULL,'2026-10')",
        (canonical(b).decode(),status))
    with pytest.raises(ValueError,match='ACTIVE_OR_UNCERTAIN_SHARED_PACKAGE_CONSUMER'):
        h.cleanup_shared(accounts,NS(),NOW+timedelta(days=50))
    assert calls==[]


def test_terminal_cleanup_delegates_all_original_checks(ledger,scoped,monkeypatch,tmp_path):
    batch,accounts=ledger;calls=[]
    monkeypatch.setattr(h.base,'state',lambda p:tmp_path)
    monkeypatch.setattr(h,'shared_package',lambda a:{'id':'vo-shared'})
    monkeypatch.setattr(h.base,'cleanup_package',lambda *a:calls.append(a) or {'status':'ORIGINAL_CHECKS'})
    for status in ['COLLECTED','ACCOUNTED']:
        b=bound();b['package_volume_id']='vo-shared'
        batch.db.execute("INSERT INTO autonomy_compute VALUES(?, 'item4',?,?,100,NULL,NULL,'2026-10')",
            (status,canonical(b).decode(),status))
    assert h.cleanup_shared(accounts,NS(),NOW+timedelta(days=50))=={'status':'ORIGINAL_CHECKS'}
    assert len(calls)==1


def test_creation_after_reservation_and_uncertainty_never_repeated(scoped,monkeypatch,tmp_path):
    events=[];outcomes=[]
    monkeypatch.setattr(h,'context',lambda *a:scoped)
    monkeypatch.setattr(h,'state',lambda p:tmp_path/'new')
    monkeypatch.setattr(h,'retention_ready',lambda:None)
    monkeypatch.setattr(h,'shared_package',lambda a:{'id':'vo-originalPackage'})
    monkeypatch.setattr(h,'reserve',lambda *a:events.append('reserve') or 'a'*64)
    class Missing(Exception):pass
    def lookup(name,*,create_if_missing,client):
        events.append('create' if create_if_missing else 'lookup')
        if not create_if_missing:raise Missing()
        raise RuntimeError('uncertain create')
    provider=NS(config=scoped['preprocessing_runtime'],billing_snapshot=lambda:billing(),client=object(),
        modal=NS(App=NS(lookup=lookup),exception=NS(NotFoundError=Missing)))
    accounts=NS(finish_assets=lambda *a:outcomes.append(a))
    with pytest.raises(RuntimeError):h.prepare_assets(NS(),{},accounts,provider)
    assert events==['reserve','lookup','create'] and outcomes[0][1]=='UNCERTAIN'
    with pytest.raises(ValueError,match='EXISTING_PREPARATION'):
        h.prepare_assets(NS(),{},accounts,provider)
    assert events==['reserve','lookup','create']
