"""Actual reserve/submit/collect/account/next-wave connection; synthetic provider.

Only connectivity, provider facts and clock values are synthetic. No mocked
accounting, validator, job lifecycle, original receipt reader or admission gate.
"""
from datetime import datetime,timezone
from copy import deepcopy
import json
import pytest
from orchestrator import modal_terminal_cost as cost,private_records as pr
from orchestrator.modal_item4_policy import quote
from orchestrator.modal_executor import canonical,item4_job
from orchestrator.manual_executor import digest,inventory
from orchestrator.modal_billing import canonical as billing_canonical
from test_modal_executor import setup,item4_dispatch,private_test_environment,make_item4_package,ITEM4_RATES

BOOT='11111111-1111-4111-8111-111111111111'
NOW=datetime(2026,10,6,23,30,tzinfo=timezone.utc)


def stamp(seconds,boot=BOOT):
    return {'boot_id':boot,'boottime_ns':seconds*1_000_000_000,'observed_at':NOW.isoformat()}


def prepared(fixture,fit,seconds=20_000,overhead=100_000):
    args=list(make_item4_package(fixture,fit));binding=args[1]
    binding['resources']['timeout_seconds']=seconds
    binding['overhead_micro_usd']=overhead
    binding['cost']=quote(binding['resources'],ITEM4_RATES,overhead)
    files=inventory(args[2]);files.pop('manifest.json')
    pr.write_bytes(args[2]/'manifest.json',canonical({'schema':'modal-run/v1','binding':binding,'files':files}))
    return args


def complete(fixture,args,monkeypatch,seconds=90,boot=BOOT):
    executor,provider,_,_=fixture
    monkeypatch.setattr(cost,'clock',lambda:stamp(1000))
    assert executor.submit(*args)['status']=='SUBMITTED'
    provider.state='COMPLETE'
    monkeypatch.setattr(cost,'clock',lambda:stamp(1000+seconds,boot))
    destination=executor.path.parent/('return-'+args[0])
    validate=lambda path:json.loads((path/'result.json').read_text())
    assert executor.collect_remote(args[0],args[3],destination,validate)['status']=='VALID'
    return destination,validate


def test_real_collection_bounds_exposure_and_unblocks_next_wave_once(item4_dispatch,monkeypatch):
    executor,provider,batch,run=item4_dispatch
    first=prepared(item4_dispatch,'first');second=prepared(item4_dispatch,'second')
    monkeypatch.setattr(cost,'clock',lambda:stamp(1000))
    assert executor.submit(*first)['status']=='SUBMITTED'
    with pytest.raises(ValueError,match='^ITEM4_HARD_COST_CAP$'):executor.submit(*second)
    assert provider.calls.count('create')==1
    original=dict(batch.db.execute('SELECT * FROM autonomy_compute').fetchone())
    provider.state='COMPLETE';monkeypatch.setattr(cost,'clock',lambda:stamp(1090))
    dest=executor.path.parent/'results';validate=lambda p:json.loads((p/'result.json').read_text())
    executor.collect_remote(first[0],first[3],dest,validate)
    row=batch.db.execute('SELECT * FROM autonomy_compute').fetchone()
    assert row['reserved_micro_usd']==original['reserved_micro_usd'] and row['actual_micro_usd'] is None
    bound=quote({**first[1]['resources'],'timeout_seconds':90},ITEM4_RATES,100_000)['reserved_micro_usd']
    assert cost.effective(batch.db,row,ITEM4_RATES)==bound
    events=[tuple(r) for r in batch.db.execute('SELECT * FROM events')];calls=list(provider.calls)
    executor.collect_remote(first[0],first[3],dest,validate)
    assert events==[tuple(r) for r in batch.db.execute('SELECT * FROM events')] and provider.calls==calls
    provider.state='RUNNING';assert executor.submit(*second)['status']=='SUBMITTED'
    assert provider.calls.count('create')==2 and batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    receipt=json.loads(batch.db.execute('SELECT payload FROM events WHERE id=?',(digest(canonical(second[1]))+':gpu-reserved',)).fetchone()[0])
    assert receipt['terminal_exposure']['terminal_bounds_micro_usd'][row['id']]==bound


@pytest.mark.parametrize('damage',['cross-boot','no-clock'])
def test_missing_or_cross_boot_window_never_releases_maximum(item4_dispatch,monkeypatch,damage):
    executor,provider,batch,run=item4_dispatch;args=prepared(item4_dispatch,'legacy')
    if damage=='cross-boot':complete(item4_dispatch,args,monkeypatch,boot='22222222-2222-4222-8222-222222222222')
    else:
        monkeypatch.setattr(cost,'clock',lambda:stamp(1000));executor.submit(*args)
        path=executor._paths(args[0])/'create-intent.json';value=json.loads(path.read_text());value.pop('cost_clock')
        pr.write_bytes(path,canonical(value)) # explicitly synthetic legacy receipt, never a preserved live original
        provider.state='COMPLETE';executor.collect_remote(args[0],args[3],executor.path.parent/'legacy-return',lambda p:{'status':'VALID'})
    row=batch.db.execute('SELECT * FROM autonomy_compute').fetchone()
    assert cost.effective(batch.db,row,ITEM4_RATES)==row['reserved_micro_usd']
    with pytest.raises(ValueError,match='^ITEM4_HARD_COST_CAP$'):executor.submit(*prepared(item4_dispatch,'later'))


@pytest.mark.parametrize('damage',['intent','created','terminal','collection','row','event'])
def test_original_drift_refuses_before_any_second_creation(item4_dispatch,monkeypatch,damage):
    executor,provider,batch,run=item4_dispatch;args=prepared(item4_dispatch,'first');complete(item4_dispatch,args,monkeypatch)
    ident=digest(canonical(args[1]));work=executor._paths(args[0])
    if damage=='row':batch.db.execute('UPDATE autonomy_compute SET reserved_micro_usd=reserved_micro_usd+1 WHERE id=?',(ident,))
    elif damage=='event':batch.db.execute("UPDATE events SET payload='{}' WHERE id=?",(ident+':gpu-collected',))
    else:
        name={'intent':'create-intent.json','created':'created.json','terminal':'terminated.json','collection':'collection-receipt.json'}[damage]
        value=json.loads((work/name).read_text());value['synthetic_tamper']=True
        pr.write_bytes(work/name,canonical(value))
    before=provider.calls.count('create')
    with pytest.raises(ValueError):executor.submit(*prepared(item4_dispatch,'later'))
    assert provider.calls.count('create')==before


def test_unknown_terminal_and_future_clock_never_qualify(item4_dispatch,monkeypatch):
    executor,provider,batch,run=item4_dispatch;args=prepared(item4_dispatch,'first')
    monkeypatch.setattr(cost,'clock',lambda:stamp(1000));executor.submit(*args)
    row=batch.db.execute('SELECT * FROM autonomy_compute').fetchone()
    with pytest.raises(ValueError,match='^ITEM4_EXPOSURE_TERMINAL_BINDING$'):cost.record(executor.costs,row['id'],executor._paths(args[0]))
    assert cost.effective(batch.db,row,ITEM4_RATES)==row['reserved_micro_usd']
    provider.state='COMPLETE';monkeypatch.setattr(cost,'clock',lambda:stamp(999))
    with pytest.raises(ValueError,match='^ITEM4_EXPOSURE_CLOCK_REVERSED$'):
        executor.collect_remote(args[0],args[3],executor.path.parent/'bad-clock',lambda p:{'status':'VALID'})
    assert not batch.db.execute('SELECT 1 FROM events WHERE id=?',(row['id']+':terminal-exposure',)).fetchone()


def snapshot(object_id,amount,now=NOW):
    body={'schema':'modal-billing-snapshot/v1','workspace':'moroseui','observed_at':now.isoformat(),
          'rates':ITEM4_RATES,'rows':[{'object_id':object_id,'cost':amount}],
          'summary':{'metered_cost':amount,'billed_cost':amount,'adjustments':{}}}
    return {**body,'sha256':digest(billing_canonical(body))}


def test_billed_excess_survives_lag_month_rollover_and_reservation_refusal(item4_dispatch,monkeypatch):
    executor,provider,batch,run=item4_dispatch;args=prepared(item4_dispatch,'first');complete(item4_dispatch,args,monkeypatch)
    app=args[1]['experiment']['billing_object_id'];observed=snapshot(app,'80')
    second=prepared(item4_dispatch,'second');binding=second[1]
    with pytest.raises(ValueError,match='^ITEM4_HARD_COST_CAP$'):
        executor.costs.reserve_item4(digest(canonical(binding)),run,binding,billing_snapshot=observed,now=NOW)
    assert cost.highwater(batch.db)[(app,'2026-10')]==80_000_000
    lower=snapshot(app,'1');cost.observe_billing(executor.costs,lower,NOW)
    november=NOW.replace(month=11);new=snapshot(app,'2',november);cost.observe_billing(executor.costs,new,november)
    rows=batch.db.execute('SELECT * FROM autonomy_compute').fetchall()
    assert cost.exposure(batch.db,rows,new)['smoke_cost'][run]==82_000_000
    assert cost.exposure(batch.db,rows,new)['commitments'][app]==2_000_000
    before=batch.db.execute('SELECT count(*) FROM events').fetchone()[0]
    cost.observe_billing(executor.costs,new,november)
    assert batch.db.execute('SELECT count(*) FROM events').fetchone()[0]==before
    assert rows[0]['actual_micro_usd'] is None


def test_same_app_segments_are_summed_once_then_billing_floor_applied(item4_dispatch,monkeypatch):
    executor,provider,batch,run=item4_dispatch;args=prepared(item4_dispatch,'first');complete(item4_dispatch,args,monkeypatch)
    row=batch.db.execute('SELECT * FROM autonomy_compute').fetchone();other=deepcopy(args[1]);other['experiment']['segment']=2
    ident=digest(canonical(other))
    # Synthetic prior segment only: unproven cost stays its full reservation.
    batch.db.execute("INSERT INTO autonomy_compute VALUES(?,?,?,'ACCOUNTED',1000000,'sb-synthetic2',NULL,'2026-10')",(ident,run,canonical(other).decode()))
    app=other['experiment']['billing_object_id'];view=snapshot(app,'3')
    cost.observe_billing(executor.costs,view,NOW)
    rows=batch.db.execute('SELECT * FROM autonomy_compute').fetchall();result=cost.exposure(batch.db,rows,view)
    assert result['commitments'][app]==3_000_000 and result['smoke_cost'][run]==3_000_000
    other['experiment']['stage']='FULL'
    batch.db.execute('UPDATE autonomy_compute SET binding=? WHERE id=?',(canonical(other).decode(),ident))
    with pytest.raises(ValueError,match='^ITEM4_BILLING_OBJECT_SHARED$'):cost.exposure(batch.db,batch.db.execute('SELECT * FROM autonomy_compute').fetchall(),view)


def test_accepted_bound_survives_later_reboot_and_keeps_overhead_and_higher_rates(item4_dispatch,monkeypatch):
    executor,provider,batch,run=item4_dispatch;args=prepared(item4_dispatch,'first',overhead=123456);complete(item4_dispatch,args,monkeypatch)
    row=batch.db.execute('SELECT * FROM autonomy_compute').fetchone()
    monkeypatch.setattr(cost,'clock',lambda:stamp(1,'22222222-2222-4222-8222-222222222222'))
    assert cost.record(executor.costs,row['id'],executor._paths(args[0]))
    rates={k:str(float(v)*2) for k,v in ITEM4_RATES.items()}
    assert cost.effective(batch.db,row,rates)==quote({**args[1]['resources'],'timeout_seconds':90},rates,123456)['reserved_micro_usd']


def test_changed_highwater_or_snapshot_refuses(item4_dispatch,monkeypatch):
    executor,provider,batch,run=item4_dispatch;args=prepared(item4_dispatch,'first');complete(item4_dispatch,args,monkeypatch)
    view=snapshot(args[1]['experiment']['billing_object_id'],'3');cost.observe_billing(executor.costs,view,NOW)
    row=batch.db.execute("SELECT id,payload FROM events WHERE id LIKE 'item4-billing:%'").fetchone()
    value=json.loads(row['payload']);value['micro_usd']=0
    batch.db.execute('UPDATE events SET payload=? WHERE id=?',(canonical(value).decode(),row['id']))
    with pytest.raises(ValueError,match='^ITEM4_BILLING_HIGHWATER_CHANGED$'):cost.highwater(batch.db)


def test_real_interruption_record_resumed_segment_and_terminal_cost_are_linked(item4_dispatch,monkeypatch):
    from types import SimpleNamespace
    from orchestrator.modal_item4_budget import record_interruption
    executor,provider,batch,run=item4_dispatch;args=prepared(item4_dispatch,'first')
    monkeypatch.setattr(cost,'clock',lambda:stamp(1000));executor.submit(*args)
    ident=digest(canonical(args[1]));row=batch.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
    reason=executor.path.parent/'cause.json'
    pr.write_bytes(reason,canonical({'schema':'modal-interruption-cause/v1','segment_id':ident,
        'provider_id':row['provider_id'],'reason':'DELIBERATE_SMOKE_INTERRUPTION',
        'evidence':{'synthetic_fixture_only':True}}))
    checkpoint={'synthetic_fixture_only':True,'metadata':{'next_epoch':1}}
    proof={'schema':'modal-fit-terminal-proof/v1','provider_id':row['provider_id'],'binding_sha256':ident,
        'fit_id':'first','terminal_exit_code':137,'may_launch':False,'observed_at':NOW.isoformat(),
        'checkpoint_record':checkpoint,'checkpoint_record_sha256':digest(canonical(checkpoint))}
    record_interruption(executor.costs,ident,SimpleNamespace(terminal_fit_checkpoint=lambda *a:proof),reason_record=reason)
    old=dict(batch.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone())
    # Automatic pre-submit reconciliation reads the actual prior interruption
    # and immutable creation records. It makes no extra provider observation.
    monkeypatch.setattr(cost,'clock',lambda:stamp(1090))
    later=list(make_item4_package(item4_dispatch,'first',segment=2));binding=later[1]
    binding['resources']=deepcopy(args[1]['resources']);binding['cost']=deepcopy(args[1]['cost'])
    binding['overhead_micro_usd']=args[1]['overhead_micro_usd']
    event=batch.db.execute('SELECT payload FROM events WHERE id=?',(ident+':fit-interruption',)).fetchone()[0]
    binding['resume']={'previous_segment_id':ident,'terminal_receipt_sha256':digest(event.encode()),
                       'checkpoint_record_sha256':proof['checkpoint_record_sha256']}
    files=inventory(later[2]);files.pop('manifest.json')
    pr.write_bytes(later[2]/'manifest.json',canonical({'schema':'modal-run/v1','binding':binding,'files':files}))
    assert executor.submit(*later)['status']=='SUBMITTED'
    assert dict(batch.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone())==old
    assert batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==2
    assert batch.db.execute('SELECT 1 FROM events WHERE id=?',(ident+':terminal-exposure',)).fetchone()
    assert provider.calls.count('create')==2


def test_terminal_clock_rounds_up_and_timeout_remains_an_upper_bound(item4_dispatch,monkeypatch):
    executor,provider,batch,run=item4_dispatch;args=prepared(item4_dispatch,'first',seconds=60)
    monkeypatch.setattr(cost,'clock',lambda:stamp(1000));executor.submit(*args)
    stop=stamp(1001);stop['boottime_ns']+=1
    monkeypatch.setattr(cost,'clock',lambda:stop);provider.state='COMPLETE'
    executor.collect_remote(args[0],args[3],executor.path.parent/'rounded',lambda p:{'status':'VALID'})
    row=batch.db.execute('SELECT * FROM autonomy_compute').fetchone()
    assert cost.effective(batch.db,row,ITEM4_RATES)==quote({**args[1]['resources'],'timeout_seconds':2},ITEM4_RATES,100000)['reserved_micro_usd']


def test_halting_still_refuses_a_new_fit_after_terminal_reconciliation(item4_dispatch,monkeypatch):
    executor,provider,batch,run=item4_dispatch;args=prepared(item4_dispatch,'first');complete(item4_dispatch,args,monkeypatch)
    pr.write_bytes(batch.folder/'HALT',b'synthetic operator stop')
    with pytest.raises(ValueError,match='^AUTONOMY_BATCH_HALTED$'):executor.submit(*prepared(item4_dispatch,'later'))
    assert provider.calls.count('create')==1


def test_late_billing_cannot_absorb_active_segment_reservation(item4_dispatch,monkeypatch):
    executor,provider,batch,run=item4_dispatch;args=prepared(item4_dispatch,'first');complete(item4_dispatch,args,monkeypatch)
    old=deepcopy(args[1]);old['experiment']['segment']=2;ident=digest(canonical(old))
    batch.db.execute("INSERT INTO autonomy_compute VALUES(?,?,?,'RUNNING',5000000,'sb-synthetic2',NULL,'2026-10')",(ident,run,canonical(old).decode()))
    app=old['experiment']['billing_object_id'];view=snapshot(app,'6')
    cost.observe_billing(executor.costs,view,NOW)
    result=cost.exposure(batch.db,batch.db.execute('SELECT * FROM autonomy_compute').fetchall(),view)
    assert result['commitments'][app]==11_000_000 and result['smoke_cost'][run]==11_000_000


def test_underestimated_completed_app_stops_admission_without_erasing_bill(item4_dispatch,monkeypatch):
    executor,provider,batch,run=item4_dispatch;args=prepared(item4_dispatch,'first');complete(item4_dispatch,args,monkeypatch)
    app=args[1]['experiment']['billing_object_id'];view=snapshot(app,'6')
    binding=prepared(item4_dispatch,'later')[1]
    with pytest.raises(ValueError,match='^ITEM4_COST_BOUND_BELOW_BILLING$'):
        executor.costs.reserve_item4(digest(canonical(binding)),run,binding,billing_snapshot=view,now=NOW)
    assert cost.highwater(batch.db)[(app,'2026-10')]==6_000_000
    assert batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==1
