"""Benchmark setup respects ledger caps and never repeats uncertain creation."""
from copy import deepcopy
from types import SimpleNamespace as NS
from pathlib import Path
import json
import pytest
from orchestrator import item4_benchmark_handoff as h, private_records as pr
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from test_modal_item4_budget import ledger, bound, snapshot, NOW, RATES


def policy():
    b=bound(gpu=None,cpu=16,memory_mib=131072,timeout_seconds=3600)
    b.update(source='synthetic',purpose='M4_ITEM4',overhead_micro_usd=5000000,
             preprocessing={'plans_name':'synthetic-plans','split_sha256':'a'*64},
             execution={'module_sha256':'b'*64},fresh_start={'synthetic':True},resume={'synthetic':True})
    runtime={'asset_expires_utc':'2026-11-05T00:00:00+00:00','image_id':'im-synthetic',
             'item4_preprocessing_assets':{'output_volume_id':'vo-syntheticInput',
              'source_records':{'cohort':'/synthetic/cohort.json'}}}
    return {'run_id':'item4','source':'synthetic','package_manifest':{'path':'/synthetic/lane/experiment-package/manifest.json','sha256':'a'*64},
            'preprocessing_binding':b,'preprocessing_runtime':runtime,
            'fits':[{'fit_id':'benchmark-'+gpu,'stage':'SMOKE','arm':'A1_repeat','fold':0,
                     'realization':'benchmark-'+gpu,'preprocessing_id':'prep-A1_repeat',
                     'outputs':['metrics.json','epoch-timing.json','validation.json']} for gpu in h.GPUS],
            'preprocessing_records':{k:{'sha256':'a'*64} for k in ['preprocessing.json','validation.json','result.json']},
            'spec_sha256':'a'*64,'code_hashes':{'run.py':'b'*64,'execution.py':'c'*64},
            'preprocessing_identity':{k:'d'*64 for k in ['input_contract_sha256','environment_sha256','plans_sha256']}}


def billing():
    v=snapshot();v['rates']={**v['rates'],'volume_storage_gib_month_cost':'.09','egress_gib_cost':'.04'}
    body={k:x for k,x in v.items() if k!='sha256'}
    from orchestrator.modal_billing import canonical as bc
    v['sha256']=digest(bc(body));return v


def test_asset_reservation_counts_with_ordinary_fit_admission_and_cannot_repeat(ledger):
    batch,accounts=ledger;p=policy()
    ident=h.reserve(accounts,p,billing(),NOW)
    row=dict(batch.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone())
    assert row['reserved_micro_usd']==1000000 and row['status']=='RESERVED'
    accounts.finish_assets(ident,'READY',{'status':'READY','synthetic':True})
    with pytest.raises(ValueError,match='EXISTING_PREPARATION'):h.reserve(accounts,p,billing(),NOW)
    # Setup plus the ordinary run is still subject to the original smoke cap.
    batch.db.execute("INSERT INTO autonomy_assets VALUES('old','item4','{}','READY',73000000,'{}')")
    from test_modal_item4_budget import reserve
    with pytest.raises(ValueError,match='ITEM4_HARD_COST_CAP'):
        reserve(accounts,bound(timeout_seconds=3600))
    assert batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==0


@pytest.mark.parametrize('cause',['cap','active','uncertain','foreign-asset','rate','stale'])
def test_preparation_admission_refuses_without_a_new_reservation(ledger,cause):
    batch,accounts=ledger;p=policy();v=billing()
    if cause=='cap':batch.db.execute("INSERT INTO autonomy_assets VALUES('old','item4','{}','READY',75000000,'{}')")
    elif cause in {'active','uncertain'}:
        batch.db.execute("INSERT INTO autonomy_compute VALUES('old','item4',?,?,100,NULL,NULL,'2026-10')",
                         (canonical(bound()).decode(),'RUNNING' if cause=='active' else 'UNCERTAIN'))
    elif cause=='foreign-asset':batch.db.execute("INSERT INTO autonomy_assets VALUES('old','other','{}','UNCERTAIN',1,'{}')")
    elif cause=='rate':v['rates']['volume_storage_gib_month_cost']='.10'
    else:v['observed_at']='2026-10-01T00:00:00+00:00'
    before=[dict(x) for x in batch.db.execute('SELECT * FROM autonomy_assets')]
    with pytest.raises(ValueError):h.reserve(accounts,p,v,NOW)
    assert before==[dict(x) for x in batch.db.execute('SELECT * FROM autonomy_assets')]


def test_bindings_use_actual_preprocessing_and_distinct_gpu_apps(monkeypatch,tmp_path):
    p=policy();monkeypatch.setattr(h,'RECORD',tmp_path/'protected')
    ready={'status':'READY','contract_sha256':h.CONTRACT_SHA,
           'reservation_id':digest(canonical(h.asset_binding(p))),'package':{'id':'vo-package'},'fits':{}}
    for i,f in enumerate(p['fits']):
        ready['fits'][f['fit_id']]={'app_name':'synthetic-'+str(i),'app_id':'ap-synthetic'+str(i),
            'progress':{'id':'vo-progress'+str(i),'name':'synthetic-progress-'+str(i)}}
    rows=h.runtime_rows(p,ready,RATES)
    assert [r['binding']['resources']['gpu'] for r in rows]==list(h.GPUS)
    assert len({r['binding']['experiment']['billing_object_id'] for r in rows})==3
    assert len({r['binding']['progress']['volume_id'] for r in rows})==3
    assert {r['runtime']['package_volume_id'] for r in rows}=={'vo-package'}
    for r in rows:
        b=r['binding'];assert not {'resume','fresh_start','preprocessing','execution','spec_sha256'}&set(b)
        assert b['experiment']['segment']==1 and b['overhead_micro_usd']==5000000
        assert b['preprocessing_job_sha256']==digest(canonical(p['preprocessing_binding']))
        assert b['progress']['fit_binding']['plans_sha256']==p['preprocessing_identity']['plans_sha256']
    ready['reservation_id']='f'*64
    with pytest.raises(ValueError,match='ASSET_RECEIPT'):h.runtime_rows(p,ready,RATES)


def test_first_creation_follows_reservation_and_uncertain_attempt_never_repeats(monkeypatch,tmp_path):
    p=policy();events=[];outcomes=[]
    monkeypatch.setattr(h,'contract',lambda:p);monkeypatch.setattr(h,'state',lambda _:tmp_path/'assets')
    monkeypatch.setattr(h,'checked_driver',lambda *args:None)
    monkeypatch.setattr(h,'retention_ready',lambda:events.append('retention'))
    monkeypatch.setattr(h,'reserve',lambda *args:events.append('reservation') or 'a'*64)
    class Missing(Exception):pass
    def lookup(name,*,create_if_missing,client):
        events.append('create' if create_if_missing else 'lookup')
        if not create_if_missing:raise Missing()
        raise RuntimeError('Synthetic uncertain transport after create request')
    provider=NS(config=p['preprocessing_runtime'],billing_snapshot=lambda:billing(),client=object(),
                modal=NS(App=NS(lookup=lookup),exception=NS(NotFoundError=Missing)))
    accounts=NS(finish_assets=lambda *args:outcomes.append(args))
    with pytest.raises(RuntimeError):h.prepare_assets(NS(),{},accounts,provider)
    assert events==['retention','reservation','lookup','create']
    assert outcomes[0][1]=='UNCERTAIN' and (tmp_path/'assets/INTENT.json').is_file()
    first=list(events)
    with pytest.raises(ValueError,match='EXISTING_PREPARATION_RECONCILE'):
        h.prepare_assets(NS(),{},accounts,provider)
    assert events==first+['retention'] # No second reservation or provider request.


def test_all_generated_names_fit_pinned_sdk_limits_before_reservation():
    p=policy();names,package=h.asset_names(p,'f'*64)
    complete=[package,*names.values(),*(x+'-progress' for x in names.values())]
    assert len(set(complete))==7 and max(map(len,complete))<=64
    p['fits'][0]['fit_id']='x'*100
    with pytest.raises(ValueError,match='PROVIDER_OBJECT_NAME'):h.asset_names(p,'f'*64)
