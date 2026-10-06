"""Actual-response-shaped billing tests; no provider calls or spending."""
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from types import SimpleNamespace as NS
import copy
import hashlib
import pytest
from orchestrator.modal_billing import capture, headroom, canonical, micros

NOW = datetime(2026,10,6,2,30,tzinfo=timezone.utc)


def workspace():
    summary=NS(start=NOW.replace(day=1,hour=0,minute=0),end=NOW.replace(month=11,day=1,hour=0,minute=0),
      metered_cost=Decimal('0.28000000'),billed_cost=Decimal('209.67741935'),
      metered_cost_breakdown={'Deployed Apps':Decimal('.27959643'),'Volumes':Decimal('0')},
      adjustments={'Plan Cost':Decimal('209.67741935'),'Credits':Decimal('-.28')})
    row=NS(object_id='ap-fit',interval_start=NOW.replace(hour=1,minute=0),cost=Decimal('.20'),
           cost_by_resource={'cpu':Decimal('.05'),'gpu':Decimal('.15')})
    calls=[]
    def report(**kw):calls.append(('report',kw));return [row]
    def result(**kw):calls.append(('summary',kw));return summary
    ws=NS(name='moroseui',billing=NS(rates=lambda:{'gpu_hour_cost_b200':Decimal('6.25')},report=report,summary=result))
    return ws,summary,row,calls


def remaining(snap,**kw):
    return headroom(snap,now=NOW,usage_limit_micro=1000_000_000,spend_limit_micro=900_000_000,
                    commitments=kw.pop('commitments',{}),**kw)


def test_actual_snapshot_plan_fee_and_commitments_without_double_counting():
    ws,summary,row,calls=workspace();snap=capture(ws,'moroseui',now=NOW)
    assert [c[0] for c in calls]==['report','summary']
    assert calls[0][1]['end']==NOW.replace(minute=0)
    assert calls[0][1]['resolution']=='h'
    view=remaining(snap,commitments={'ap-fit':1_000_000,'pending-fit':2_000_000})
    assert view['workspace_metered_micro']==280000
    assert view['operator_plan_fee_micro']==209677420
    assert view['workspace_workload_billed_micro']==0
    assert view['unreported_commitment_micro']==2_800_000
    assert view['usage_headroom_micro']==996_920_000
    assert view['spend_headroom_micro']==897_200_000
    assert snap['summary']['billed_cost']=='209.67741935'
    assert remaining(snap,commitments={'ap-fit':100000})['unreported_commitment_micro']==0


def test_unrelated_usage_and_plan_fee_are_not_attributed_to_experiment():
    ws,summary,row,_=workspace();summary.metered_cost=Decimal('100');summary.billed_cost=Decimal('221.67741935')
    summary.adjustments['Credits']=Decimal('-88')
    snap=capture(ws,'moroseui',now=NOW);view=remaining(snap)
    assert view['workspace_workload_billed_micro']==12_000_000
    assert view['usage_headroom_micro']==900_000_000
    assert view['spend_headroom_micro']==888_000_000
    assert 'experiment_cost' not in view # Workspace usage is never called fit cost.


@pytest.mark.parametrize('damage', ['workspace','negative','nan','duplicate','outside','summary','ahead'])
def test_bad_provider_observations_refuse(damage):
    ws,summary,row,_=workspace()
    if damage=='workspace':ws.name='different'
    if damage=='negative':summary.metered_cost=Decimal('-1')
    if damage=='nan':row.cost=Decimal('NaN')
    if damage=='duplicate':ws.billing.report=lambda **kw:[row,row]
    if damage=='outside':row.interval_start=NOW.replace(hour=2,minute=0)
    if damage=='summary':summary.billed_cost=Decimal('999')
    if damage=='ahead':row.cost=Decimal('100')
    with pytest.raises(ValueError,match='MODAL_'):capture(ws,'moroseui',now=NOW)


def test_stale_tampered_or_wrong_cycle_snapshot_is_not_spending_authority():
    ws,*_=workspace();snap=capture(ws,'moroseui',now=NOW)
    for now in [NOW+timedelta(seconds=301),NOW-timedelta(seconds=1),NOW.replace(month=11)]:
        with pytest.raises(ValueError,match='MODAL_BILLING_SNAPSHOT_STALE'):
            headroom(snap,now=now,usage_limit_micro=100,spend_limit_micro=100,commitments={})
    snap['summary']['metered_cost']='0'
    with pytest.raises(ValueError,match='MODAL_BILLING_SNAPSHOT_HASH'):remaining(snap)


def test_month_open_has_summary_but_no_fabricated_report_rows():
    ws,summary,_,calls=workspace();now=NOW.replace(day=1,hour=0,minute=1)
    snap=capture(ws,'moroseui',now=now)
    assert snap['rows']==[] and [c[0] for c in calls]==['summary']


def test_provider_entrypoint_authenticates_without_launch_or_upload():
    from orchestrator.modal_provider import ModalProvider
    ws,*_=workspace();events=[]
    ws.hydrate=lambda **kw:events.append('hydrate')
    p=object.__new__(ModalProvider);p.config={'workspace':'moroseui'}
    p.client=NS(hello=lambda:events.append('hello'))
    p.modal=NS(Workspace=NS(from_context=lambda **kw:ws))
    # Use a current-cycle response, as the provider wrapper supplies real now().
    current=datetime.now(timezone.utc);base=current.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
    summary=ws.billing.summary();summary.start=base
    summary.end=(base.replace(day=28)+timedelta(days=4)).replace(day=1)
    ws.billing.report=lambda **kw:[]
    out=p.billing_snapshot()
    assert out['workspace']=='moroseui' and events==['hello','hydrate']


@pytest.mark.parametrize('value',[True,-1,'20',1.5])
def test_commitment_requires_nonnegative_integer_microdollars(value):
    ws,*_=workspace();snap=capture(ws,'moroseui',now=NOW)
    with pytest.raises(ValueError,match='MODAL_BILLING_LIMIT_OR_COMMITMENT'):
        remaining(snap,commitments={'ap-fit':value})
