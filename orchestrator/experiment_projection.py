"""Measured item4 hardware/cost calculation from authenticated aggregate originals.

The author/reviewer freeze the benchmark protocol, timing applicability, epochs,
validation checks and assumptions. This module applies the operator's hardware
and dollar rules only. It creates no ACCEPTED event or spending reservation.
"""
from decimal import Decimal, ROUND_CEILING
from datetime import datetime, timezone
from pathlib import Path
from orchestrator import experiment_collection as collection, experiment_result as results
from orchestrator import private_records as pr
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from orchestrator.manual_driver import write_once
from orchestrator.modal_item4_policy import GPU_KEYS, PROJECTION_LIMIT, quote
from orchestrator.modal_billing import decimal, headroom
from orchestrator.experiment_plan_validation import number, contract






def timing_view(timing, resources):
    """Validate the author's richer native record; preserve the original object.

    The seven-field legacy form is unchanged. The native form adds evidence,
    not a different timing definition: calculation still uses all measured time
    divided by completed epochs. No warm-up filtering or scientific choice here.
    """
    import math
    base={'schema','fit_id','completed_epochs','elapsed_training_seconds',
          'real_epoch','loader_not_bottleneck','comparability_id'}
    extra={'epoch_records','gpu','measured_loader_wait_seconds','memory_gib',
           'physical_cpus','segment','total_native_epochs'}
    if not isinstance(timing,dict) or set(timing)==base:return timing
    def require(ok):
        if not ok:raise ValueError('EXPERIMENT_PROJECTION_NATIVE_TIMING')
    def finite(value):
        try:return type(value) in (int,float) and math.isfinite(value)
        except (OverflowError,ValueError):return False
    require(set(timing)==base|extra and isinstance(resources,dict))
    count=timing['completed_epochs'];records=timing['epoch_records']
    require(type(count) is int and count>0 and isinstance(records,list) and len(records)==count)
    require(type(timing['total_native_epochs']) is int and timing['total_native_epochs']==count
            and type(timing['segment']) is int and timing['segment']>0)
    fields={'epoch','elapsed','loader_wait','training_iterations','validation_iterations'}
    for index,row in enumerate(records):
        require(isinstance(row,dict) and set(row)==fields)
        require(type(row['epoch']) is int and row['epoch']==index
            and type(row['training_iterations']) is int and row['training_iterations']==250
            and type(row['validation_iterations']) is int and row['validation_iterations']==50)
        require(finite(row['elapsed']) and row['elapsed']>0 and finite(row['loader_wait'])
            and 0<=row['loader_wait']<=row['elapsed'])
    elapsed=sum(r['elapsed'] for r in records);wait=sum(r['loader_wait'] for r in records)
    require(finite(elapsed) and finite(wait) and wait/elapsed<=.10
        and finite(timing['elapsed_training_seconds']) and timing['elapsed_training_seconds']==elapsed
        and finite(timing['measured_loader_wait_seconds']) and timing['measured_loader_wait_seconds']==wait)
    require(type(timing['physical_cpus']) is int and timing['physical_cpus']==resources.get('cpu')
        and isinstance(timing['gpu'],str) and timing['gpu']==resources.get('gpu')
        and type(resources.get('memory_mib')) is int and finite(timing['memory_gib'])
        and timing['memory_gib']==resources['memory_mib']/1024)
    return {key:timing[key] for key in base}


def timings(plan, observations, rates, needed):
    """Typed measurements; actual file/ledger authentication is separate."""
    selected,smoke,byid=contract(plan)
    if not isinstance(observations,dict) or set(observations)!=needed:
        raise ValueError('EXPERIMENT_PROJECTION_OBSERVATIONS')
    epochs={};resources={}
    for fit_id,observed in observations.items():
        if not isinstance(observed,dict) or set(observed)!={'timing','resources'}:
            raise ValueError('EXPERIMENT_PROJECTION_OBSERVATION')
        resource=observed['resources'];timing=timing_view(observed['timing'],resource)
        if (not isinstance(timing,dict) or set(timing)!={'schema','fit_id','completed_epochs',
                'elapsed_training_seconds','real_epoch','loader_not_bottleneck','comparability_id'}
                or timing['schema']!='experiment-epoch-timing/v1' or timing['fit_id']!=fit_id
                or type(timing['completed_epochs']) is not int or timing['completed_epochs']<1
                or timing['real_epoch'] is not True or timing['loader_not_bottleneck'] is not True
                or not isinstance(timing['comparability_id'],str) or not timing['comparability_id']):
            raise ValueError('EXPERIMENT_PROJECTION_REAL_EPOCH_REQUIRED')
        quote(resource,rates,0) # same real billing/resource validator as admission
        if resource['gpu'] not in GPU_KEYS:raise ValueError('EXPERIMENT_PROJECTION_GPU')
        epochs[fit_id]=number(timing['elapsed_training_seconds'],positive=True)/timing['completed_epochs']
        resources[fit_id]=resource
    return selected,byid,epochs,resources


def hardware(plan,observations,rates):
    """Choose from the three authenticated real-epoch observations first."""
    selected,_,_=contract(plan)
    selected,byid,epochs,resources=timings(plan,observations,rates,set(selected['benchmark_fit_ids']))
    benchmarks=selected['benchmark_fit_ids']
    if ({resources[x]['gpu'] for x in benchmarks}!=set(GPU_KEYS)
            or len({(resources[x]['cpu'],resources[x]['memory_mib']) for x in benchmarks})!=1
            or len({(byid[x]['arm'],byid[x]['fold']) for x in benchmarks})!=1
            or any(observations[x]['timing']['comparability_id']!=selected['benchmark_comparability_id'] for x in benchmarks)):
        raise ValueError('EXPERIMENT_PROJECTION_BENCHMARK_COMPARABILITY')
    ordered=sorted(benchmarks,key=lambda x:(number(rates[GPU_KEYS[resources[x]['gpu']]],positive=True),resources[x]['gpu']))
    candidates=[];comparisons=[]
    for index,fit_id in enumerate(ordered):
        previous=ordered[index-1] if index else None
        qualifies=previous is None or epochs[fit_id]<=epochs[previous]*Decimal('0.8')
        comparisons.append({'fit_id':fit_id,'gpu':resources[fit_id]['gpu'],
            'epoch_seconds':str(epochs[fit_id]),'next_cheaper_fit_id':previous,
            'qualifies':qualifies})
        if qualifies:candidates.append(fit_id)
    chosen=min(candidates,key=lambda x:(epochs[x],number(rates[GPU_KEYS[resources[x]['gpu']]],positive=True)))
    return {'selected_gpu':resources[chosen]['gpu'],'benchmarks':comparisons}


def calculate(plan,observations,rates):
    """Project all full fits after their selected-hardware smoke timings exist."""
    selected,_,_=contract(plan)
    needed=set(selected['benchmark_fit_ids'])|{r['timing_fit_id'] for r in selected['full_fits']}
    selected,byid,epochs,resources=timings(plan,observations,rates,needed)
    chosen=hardware(plan,{x:observations[x] for x in selected['benchmark_fit_ids']},rates)
    gpu=chosen['selected_gpu'];comparisons=chosen['benchmarks'];projected=[]
    for row in selected['full_fits']:
        timing_id=row['timing_fit_id'];resource=resources[timing_id]
        if resource['gpu']!=gpu:raise ValueError('EXPERIMENT_PROJECTION_SELECTED_GPU_TIMING_REQUIRED')
        seconds=epochs[timing_id]*row['epochs']+number(row['fixed_seconds'])
        seconds=int(seconds.to_integral_value(rounding=ROUND_CEILING))
        # A realization may span bounded continuation segments. Project all of
        # it without requesting a provider lifetime above 24 hours. Charges for
        # actual interruptions remain additional ordinary reservations.
        estimated_resources={**resource,'timeout_seconds':min(seconds,86400)}
        unit=quote(estimated_resources,rates,0)
        whole,remainder=divmod(seconds,86400)
        compute=whole*quote({**resource,'timeout_seconds':86400},rates,0)['compute_micro_usd']
        if remainder:compute+=quote({**resource,'timeout_seconds':remainder},rates,0)['compute_micro_usd']
        cost={'compute_micro_usd':compute,'overhead_micro_usd':row['overhead_micro_usd'],
            'projected_micro_usd':compute+row['overhead_micro_usd'],'rates':unit['rates'],
            'basis':'Measured duration, rounded upward per bounded lifetime segment, plus reviewed overhead'}
        projected.append({**row,'gpu':gpu,'epoch_seconds':str(epochs[timing_id]),
            'projected_seconds':seconds,'minimum_lifetime_segments':(seconds+86399)//86400,
            'cost':cost,'resources':estimated_resources})
    total=sum(x['cost']['projected_micro_usd'] for x in projected)
    return {'selected_gpu':gpu,'benchmarks':comparisons,'fits':projected,
        'full_projection_micro_usd':total,'within_projection_limit':total<=PROJECTION_LIMIT,
        'projection_limit_micro_usd':PROJECTION_LIMIT,
        'meaning':'Measured estimate with reviewed assumptions; not a reservation or scientific approval.'}


def evidence(driver,value,selected,*,kind="full"):
    """Read originals and real owner ledgers; no remote request or model call."""
    if kind not in {"hardware","full"}:raise ValueError("EXPERIMENT_PROJECTION_KIND")
    plan_raw=pr.check(driver.state/'experiment-package/execution-plan.json').read_bytes()
    plan=results.strict(plan_raw)
    config,smoke,byid=contract(plan)
    required=[f["fit_id"] for f in plan["fits"] if f["fit_id"] in config["benchmark_fit_ids"]] if kind=="hardware" else smoke
    records=collection.verified_subset(driver,value,selected,required)
    jobs={j['binding']['experiment']['fit_id']:j for j in selected['jobs']}
    needed=set(config['benchmark_fit_ids'])
    if kind=='full':needed|={r['timing_fit_id'] for r in config['full_fits']}
    observations={};pins={}
    for fit_id in sorted(needed):
        job=jobs[fit_id];folder=driver.state/'fit-packages'/job['job']/'prepared'
        manifest=results.strict(pr.check(folder/'manifest.json').read_bytes())
        if manifest['binding']['experiment']['stage']!='SMOKE':
            raise ValueError('EXPERIMENT_PROJECTION_SMOKE_BINDING')
        path=driver.state/'fit-results'/job['job']/config['timing_file']
        raw=pr.check(path).read_bytes()
        pinned=next(r for r in records if r['fit_id']==fit_id)['files'][config['timing_file']]
        if pinned!={'sha256':digest(raw),'bytes':len(raw)}:
            raise ValueError('EXPERIMENT_PROJECTION_TIMING_CHANGED')
        observations[fit_id]={'timing':results.strict(raw),'resources':manifest['binding']['resources']}
        pins[fit_id]={'job':job['job'],'file':config['timing_file'],'sha256':digest(raw),
            'binding_sha256':digest(canonical(manifest['binding']))}
    if kind=='hardware':
        return plan,observations,{'collections':records,'timings':pins,'execution_plan_sha256':digest(plan_raw)}
    resumes=resume_evidence(driver,value,jobs[config['resume_fit_id']])
    return plan,observations,{'collections':records,'timings':pins,
        'deliberate_resumes':resumes,'execution_plan_sha256':digest(plan_raw)}


def resume_evidence(driver,value,resume):
    """Authenticate every original segment, including its derived package seal."""
    from orchestrator import experiment_continuation as continuation, experiment_modal_package as bridge
    from orchestrator.modal_executor import item4_job
    folder=driver.state/'fit-packages'/resume['job']/'prepared'
    binding=results.strict(pr.check(folder/'manifest.json').read_bytes())['binding']
    bridge.replay(driver,value,folder,binding)
    current=binding;deliberate=[];seen=set()
    while current['experiment']['segment']>1:
        previous=current.get('resume',{}).get('previous_segment_id')
        if not isinstance(previous,str) or previous in seen:
            raise ValueError('EXPERIMENT_PROJECTION_LIVE_RESUME_BINDING')
        seen.add(previous)
        row=driver.store.batch.db.execute('SELECT binding FROM autonomy_compute WHERE id=?',(previous,)).fetchone()
        if row is None:raise ValueError('EXPERIMENT_PROJECTION_LIVE_RESUME_REQUIRED')
        old=results.strict(row['binding'])
        if digest(canonical(old))!=previous:raise ValueError('EXPERIMENT_PROJECTION_LIVE_RESUME_BINDING')
        old_job={'job':item4_job(old),'binding':bridge.base_binding(old),'runtime':resume['runtime']}
        bridge.replay(driver,value,driver.state/'fit-packages'/old_job['job']/'prepared',old)
        proof=continuation.terminal(driver,value,old_job)
        if continuation.successor(old_job,proof)['binding']!=bridge.base_binding(current):
            raise ValueError('EXPERIMENT_PROJECTION_LIVE_RESUME_BINDING')
        if proof['record']['resume_reason']=='DELIBERATE_SMOKE_INTERRUPTION':
            epoch=proof['record']['proof']['checkpoint_record'].get('metadata',{}).get('next_epoch')
            if type(epoch) is not int or epoch<1:
                raise ValueError('EXPERIMENT_PROJECTION_COMPLETED_CHECKPOINT_EPOCH_REQUIRED')
            deliberate.append({'event_sha256':proof['event_sha256'],'epoch_resumed_from':epoch,
                'checkpoint_record_sha256':proof['record']['proof']['checkpoint_record_sha256']})
        current=old
    if not deliberate:raise ValueError('EXPERIMENT_PROJECTION_LIVE_RESUME_REQUIRED')
    return deliberate



@pr.private_umask
def prepare(driver,value,selected,billing_snapshot,*,now=None,kind="full"):
    """Preserve a reproducible, unaccepted calculation for scientific review."""
    now=now or datetime.now(timezone.utc)
    plan,observations,proof=evidence(driver,value,selected,kind=kind)
    # Same bounded freshness/hash validation as admission, not a cached price.
    from orchestrator.modal_item4_policy import USAGE_CEILING,SPEND_CEILING
    headroom(billing_snapshot,now=now,usage_limit_micro=USAGE_CEILING,
        spend_limit_micro=SPEND_CEILING,commitments={})
    calculated=(hardware if kind=='hardware' else calculate)(plan,observations,billing_snapshot['rates'])
    record={'schema':'experiment-measured-projection/v1','calculation_kind':kind,'run_id':driver.config['run_id'],
        'source':driver.config['source'],'evidence':proof,'observations':observations,
        'billing_snapshot':billing_snapshot,'calculation':calculated,
        'scientifically_accepted':False,'execution_admitted':False}
    raw=canonical(record);path=driver.state/'measured-projections'/(digest(raw)+'.json')
    write_once(path,raw)
    return {'path':str(path),'sha256':digest(raw),'record':record}


def verify(driver,value,selected,reference,*,kind="full"):
    if not isinstance(reference,dict) or set(reference)!={'path','sha256'}:
        raise ValueError('EXPERIMENT_PROJECTION_REFERENCE')
    path=Path(reference['path'])
    if path!=driver.state/'measured-projections'/(reference['sha256']+'.json'):
        raise ValueError('EXPERIMENT_PROJECTION_REFERENCE')
    raw=pr.check(path).read_bytes()
    if digest(raw)!=reference['sha256']:raise ValueError('EXPERIMENT_PROJECTION_CHANGED')
    saved=results.strict(raw)
    plan,observations,proof=evidence(driver,value,selected,kind=kind)
    if (saved.get('schema')!='experiment-measured-projection/v1' or saved.get('calculation_kind')!=kind
            or saved.get('run_id')!=driver.config['run_id'] or saved.get('source')!=driver.config['source']
            or saved.get('observations')!=observations or saved.get('evidence')!=proof
            or saved.get('scientifically_accepted') is not False or saved.get('execution_admitted') is not False):
        raise ValueError('EXPERIMENT_PROJECTION_CHANGED')
    # Historical snapshot hash/shape checked at its observation time; this is
    # replay, not a claim that old prices still describe current headroom.
    from datetime import datetime
    from orchestrator.modal_item4_policy import USAGE_CEILING,SPEND_CEILING
    billing=saved['billing_snapshot']
    headroom(billing,now=datetime.fromisoformat(billing['observed_at']),
        usage_limit_micro=USAGE_CEILING,spend_limit_micro=SPEND_CEILING,commitments={})
    if (hardware if kind=='hardware' else calculate)(plan,observations,billing['rates'])!=saved['calculation']:
        raise ValueError('EXPERIMENT_PROJECTION_CALCULATION_CHANGED')
    return saved


@pr.private_umask
def produce(driver,value,*,kind="full"):
    """Owner command: authenticated read-only billing; no model or provider job.

    Idempotent repeats replay existing bytes without another billing request.
    Conditional admission and later scientific interpretation consume this evidence; it is not a verdict.
    """
    from orchestrator import experiment_dispatch as dispatch
    if value.get('phase')!='EXECUTE_EXPERIMENT':raise ValueError('EXPERIMENT_PROJECTION_PHASE')
    selected=dispatch.load(driver,value)
    if selected is None:raise ValueError('EXPERIMENT_PROJECTION_EXECUTION_REQUIRED')
    if kind not in {'hardware','full'}:raise ValueError('EXPERIMENT_PROJECTION_KIND')
    key='measured_hardware' if kind=='hardware' else 'measured_projection'
    if value.get(key):
        saved=verify(driver,value,selected,value[key],kind=kind)
        return {'status':'MEASURED_NOT_ACCEPTED','projection':value[key],
            'calculation':saved['calculation'],'provider_called':False,'execution_admitted':False}
    evidence(driver,value,selected,kind=kind) # refuse missing originals before billing
    first=next(j for j in selected['jobs'] if j['binding']['experiment']['stage']=='SMOKE')
    factory=getattr(driver,'provider_factory',None) or dispatch.ModalProvider
    billing=factory(first['runtime']).billing_snapshot()
    prepared=prepare(driver,value,selected,billing,kind=kind)
    reference={k:prepared[k] for k in ('path','sha256')}
    value[key]=reference
    driver.save(value)
    return {'status':'MEASURED_NOT_ACCEPTED','projection':reference,
        'calculation':prepared['record']['calculation'],'provider_called':True,'execution_admitted':False}


def require_hardware(driver,value,jobs):
    """Before runtime handoff, match subsequent fits to measured hardware."""
    from orchestrator import experiment_dispatch as dispatch
    plan=results.strict(pr.check(driver.state/'experiment-package/execution-plan.json').read_bytes())
    if 'full_training' not in plan:return # historical plans keep their existing admission gates
    frozen,_,_=contract(plan)
    following=[j for j in jobs if j['binding']['experiment']['fit_id'] not in frozen['benchmark_fit_ids']]
    if not following:return
    selected=dispatch.load(driver,value)
    if selected is None or not value.get('measured_hardware'):
        raise ValueError('EXPERIMENT_MEASURED_HARDWARE_REQUIRED')
    measured=verify(driver,value,selected,value['measured_hardware'],kind='hardware')
    if any(j['binding']['resources']['gpu']!=measured['calculation']['selected_gpu'] for j in following):
        raise ValueError('EXPERIMENT_MEASURED_HARDWARE_MISMATCH')
