"""Actual aggregate returns plus synthetic damage, never paid execution."""
from copy import deepcopy
from pathlib import Path
import hashlib,json
import pytest
from orchestrator import experiment_projection as p
from test_experiment_projection import example,RATES


def fixture(gpu='h100'):
    path=Path(__file__).with_name('fixtures')/('item4_'+gpu+'_epoch_timing.json')
    raw=path.read_bytes();expected={'a100':'a22e05605564513e8f87ca5c8fb5ba04d169513772af7f70506090e9f5dc3c46',
        'h100':'d457c2ddc178495bfa787b88abf88b7e19812df2fde746cba43e322c72a3a677'}
    assert hashlib.sha256(raw).hexdigest()==expected[gpu]
    timing=json.loads(raw)
    return timing,{'gpu':timing['gpu'],'cpu':16,'memory_mib':131072,'timeout_seconds':3600}


@pytest.mark.parametrize('gpu',['a100','h100'])
def test_genuine_records_keep_originals_and_exact_duration(gpu):
    timing,resources=fixture(gpu);before=deepcopy(timing)
    view=p.timing_view(timing,resources)
    assert timing==before and len(view)==7 and view['elapsed_training_seconds']==timing['epoch_records'][0]['elapsed']
    assert view['completed_epochs']==1


@pytest.mark.parametrize('damage',['extra','missing','epochs_bool','epochs_count','native_count','native_bool',
    'segment_zero','segment_bool','record_extra','record_missing','epoch_bool','epoch_offset','duplicate',
    'train_count','train_bool','val_count','val_bool','negative_time','nan_time','infinite_time',
    'negative_wait','wait_over_time','bottleneck','total_time','total_wait','total_bool','gpu','cpu','memory'])
def test_damaged_native_evidence_refuses(damage):
    t,r=fixture();v=t['epoch_records'][0]
    if damage=='extra':t['unknown']=1
    elif damage=='missing':t.pop('segment')
    elif damage=='epochs_bool':t['completed_epochs']=True
    elif damage=='epochs_count':t['completed_epochs']=2
    elif damage=='native_count':t['total_native_epochs']=2
    elif damage=='native_bool':t['total_native_epochs']=True
    elif damage=='segment_zero':t['segment']=0
    elif damage=='segment_bool':t['segment']=True
    elif damage=='record_extra':v['unknown']=1
    elif damage=='record_missing':v.pop('loader_wait')
    elif damage=='epoch_bool':v['epoch']=False
    elif damage=='epoch_offset':v['epoch']=1
    elif damage=='duplicate':t['epoch_records']*=2;t['completed_epochs']=t['total_native_epochs']=2
    elif damage=='train_count':v['training_iterations']=249
    elif damage=='train_bool':v['training_iterations']=True
    elif damage=='val_count':v['validation_iterations']=49
    elif damage=='val_bool':v['validation_iterations']=True
    elif damage=='negative_time':v['elapsed']=-1
    elif damage=='nan_time':v['elapsed']=float('nan')
    elif damage=='infinite_time':v['elapsed']=float('inf')
    elif damage=='negative_wait':v['loader_wait']=-1
    elif damage=='wait_over_time':v['loader_wait']=v['elapsed']+1
    elif damage=='bottleneck':v['loader_wait']=v['elapsed']*.11;t['measured_loader_wait_seconds']=v['loader_wait']
    elif damage=='total_time':t['elapsed_training_seconds']+=1
    elif damage=='total_wait':t['measured_loader_wait_seconds']+=1
    elif damage=='total_bool':t['elapsed_training_seconds']=True
    elif damage=='gpu':t['gpu']='B200'
    elif damage=='cpu':t['physical_cpus']=32
    elif damage=='memory':t['memory_gib']=64
    with pytest.raises(ValueError,match='EXPERIMENT_PROJECTION_NATIVE_TIMING'):p.timing_view(t,r)


def rich(observed):
    result=deepcopy(observed)
    for v in result.values():
        t=v['timing'];r=v['resources'];duration=float(t['elapsed_training_seconds'])
        t.update(elapsed_training_seconds=duration,epoch_records=[{'epoch':0,'elapsed':duration,'loader_wait':0.,
            'training_iterations':250,'validation_iterations':50}],measured_loader_wait_seconds=0.,
            total_native_epochs=1,segment=1,gpu=r['gpu'],physical_cpus=r['cpu'],memory_gib=r['memory_mib']/1024)
    return result


def test_hardware_and_full_cost_are_unchanged_for_equivalent_records():
    plan,observed=example()
    for value in observed.values():value['timing']['elapsed_training_seconds']=float(value['timing']['elapsed_training_seconds'])
    native=rich(observed)
    assert p.calculate(plan,native,RATES)==p.calculate(plan,observed,RATES)
    native['a100']['timing']['real_epoch']=False
    with pytest.raises(ValueError,match='REAL_EPOCH_REQUIRED'):p.calculate(plan,native,RATES)


def test_resumed_all_epoch_totals_are_preserved_without_warmup_filtering():
    t,r=fixture();t['segment']=2;t['completed_epochs']=t['total_native_epochs']=5
    times=[228.13786939,36.2,125.5,36.7,36.4]
    t['epoch_records']=[{'epoch':i,'elapsed':seconds,'loader_wait':.1,'training_iterations':250,'validation_iterations':50} for i,seconds in enumerate(times)]
    t['elapsed_training_seconds']=sum(times);t['measured_loader_wait_seconds']=.5
    result=p.timing_view(t,r)
    assert result['elapsed_training_seconds']==sum(times) and result['completed_epochs']==5
