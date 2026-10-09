"""Synthetic timing arithmetic only; no scientific/paid execution claim."""
from copy import deepcopy
from decimal import Decimal
import pytest
from orchestrator import experiment_projection as projection
from test_modal_item4_budget import RATES


def example():
    fits=[{'fit_id':x,'stage':'SMOKE','arm':'A1','fold':0,
        'outputs':['timing.json','validation.json']} for x in ['a100','h100','b200','arm-smoke']]
    fits.append({'fit_id':'full','stage':'FULL','arm':'A1','fold':1})
    plan={'fits':fits,'full_training':{'schema':'measured-full-training/v1','timing_file':'timing.json',
        'benchmark_fit_ids':['a100','h100','b200'],'benchmark_comparability_id':'frozen-synthetic',
        'resume_fit_id':'arm-smoke','full_fits':[{'fit_id':'full','timing_fit_id':'arm-smoke',
            'epochs':100,'fixed_seconds':'60','overhead_micro_usd':1000,
            'assumption':'Synthetic fixture: apply the same reviewed epoch estimate to fold 1.'}]}}
    observed={}
    for fit_id,gpu,seconds in [('a100','A100-80GB','100'),('h100','H100','80'),
                             ('b200','B200','65'),('arm-smoke','H100','90')]:
        observed[fit_id]={'timing':{'schema':'experiment-epoch-timing/v1','fit_id':fit_id,
            'completed_epochs':1,'elapsed_training_seconds':seconds,'real_epoch':True,
            'loader_not_bottleneck':True,'comparability_id':'frozen-synthetic'},
            'resources':{'gpu':gpu,'cpu':16,'memory_mib':65536,'timeout_seconds':1000}}
    return plan,observed


def test_exact_twenty_percent_and_full_projection_preserves_assumptions():
    plan,observed=example();result=projection.calculate(plan,observed,RATES)
    assert result['selected_gpu']=='H100' # B200 is not 20% faster than H100.
    assert result['fits'][0]['projected_seconds']==9060
    assert result['fits'][0]['assumption']==plan['full_training']['full_fits'][0]['assumption']
    expected=projection.quote({**observed['arm-smoke']['resources'],'timeout_seconds':9060},RATES,1000)
    assert result['full_projection_micro_usd']==expected['reserved_micro_usd']
    assert result['within_projection_limit'] is True
    assert 'scientifically_accepted' not in result


@pytest.mark.parametrize('times,gpu',[(('100','81','70'),'A100-80GB'),
    (('100','80','64'),'B200'),(('100','110','120'),'A100-80GB'),
    (('100','130','100'),'A100-80GB')])
def test_fastest_meaningful_gain_not_merely_most_expensive(times,gpu):
    plan,observed=example()
    for fit_id,seconds in zip(['a100','h100','b200'],times):observed[fit_id]['timing']['elapsed_training_seconds']=seconds
    observed['arm-smoke']['resources']['gpu']=gpu
    assert projection.calculate(plan,observed,RATES)['selected_gpu']==gpu


@pytest.mark.parametrize('value',[True,None,[],{},'-1','NaN','Infinity','0'])
def test_invalid_or_zero_time_refuses(value):
    plan,observed=example();observed['a100']['timing']['elapsed_training_seconds']=value
    with pytest.raises(ValueError,match='^EXPERIMENT_PROJECTION_NUMBER$'):projection.calculate(plan,observed,RATES)


@pytest.mark.parametrize('field,value',[('real_epoch',False),('loader_not_bottleneck',False),
    ('completed_epochs',True),('completed_epochs',0),('fit_id','another')])
def test_actual_epoch_and_loader_checks_required(field,value):
    plan,observed=example();observed['a100']['timing'][field]=value
    with pytest.raises(ValueError,match='^EXPERIMENT_PROJECTION_REAL_EPOCH_REQUIRED$'):
        projection.calculate(plan,observed,RATES)


@pytest.mark.parametrize('kind',['missing_gpu','cpu','memory','arm','fold','comparability'])
def test_benchmark_protocol_must_be_comparable(kind):
    plan,observed=example()
    if kind=='missing_gpu':observed['b200']['resources']['gpu']='H100'
    elif kind=='cpu':observed['b200']['resources']['cpu']=32
    elif kind=='memory':observed['b200']['resources']['memory_mib']=32768
    elif kind in ('arm','fold'):plan['fits'][2][kind]='L' if kind=='arm' else 1
    else:observed['b200']['timing']['comparability_id']='different'
    with pytest.raises(ValueError,match='^EXPERIMENT_PROJECTION_BENCHMARK_COMPARABILITY$'):
        projection.calculate(plan,observed,RATES)


def test_full_arm_needs_its_own_selected_gpu_timing():
    plan,observed=example();observed['arm-smoke']['resources']['gpu']='A100-80GB'
    with pytest.raises(ValueError,match='^EXPERIMENT_PROJECTION_SELECTED_GPU_TIMING_REQUIRED$'):
        projection.calculate(plan,observed,RATES)
    observed['arm-smoke']['resources']['gpu']='H100';plan['fits'][-1]['arm']='L'
    with pytest.raises(ValueError,match='^EXPERIMENT_PROJECTION_ARM_TIMING$'):
        projection.calculate(plan,observed,RATES)


@pytest.mark.parametrize('kind',['missing','extra','duplicate','order','assumption','epochs','output'])
def test_every_frozen_full_fit_and_explicit_assumptions_required(kind):
    plan,observed=example();rows=plan['full_training']['full_fits']
    if kind=='missing':rows.clear()
    elif kind=='extra':rows.append(deepcopy(rows[0]))
    elif kind=='duplicate':plan['fits'].append(deepcopy(plan['fits'][0]))
    elif kind=='order':rows[0]['fit_id']='not-frozen'
    elif kind=='assumption':rows[0]['assumption']=''
    elif kind=='epochs':rows[0]['epochs']=True
    else:plan['fits'][0]['outputs']=['validation.json']
    with pytest.raises(ValueError,match='^EXPERIMENT_PROJECTION_'):projection.calculate(plan,observed,RATES)


def test_large_projection_is_reported_without_admission_or_capping():
    plan,observed=example()
    for i in range(100):
        fit=deepcopy(plan['fits'][-1]);fit['fit_id']='full-'+str(i);plan['fits'].append(fit)
        row=deepcopy(plan['full_training']['full_fits'][0]);row['fit_id']=fit['fit_id']
        plan['full_training']['full_fits'].append(row)
    result=projection.calculate(plan,observed,RATES)
    assert result['full_projection_micro_usd']>1200000000
    assert result['within_projection_limit'] is False and len(result['fits'])==101


def test_seconds_round_up_and_never_override_provider_timeout():
    plan,observed=example();row=plan['full_training']['full_fits'][0]
    row.update(epochs=1,fixed_seconds='0.1')
    assert projection.calculate(plan,observed,RATES)['fits'][0]['projected_seconds']==91
    row['epochs']=1000
    fit=projection.calculate(plan,observed,RATES)['fits'][0]
    assert fit['projected_seconds']==90001 and fit['minimum_lifetime_segments']==2
    assert fit['resources']['timeout_seconds']==86400
    expected=sum(projection.quote({**observed['arm-smoke']['resources'],'timeout_seconds':seconds},RATES,0)['compute_micro_usd'] for seconds in (86400,3601))
    assert fit['cost']['compute_micro_usd']==expected
