"""Pure author-plan validators shared with execution consumers.

No provider, dispatch, collection or ledger is imported here. These functions
are moved unchanged; the runtime modules retain their public callable names.
"""
from pathlib import Path
from orchestrator.modal_billing import decimal

# Author-facing spelling list; the original validator remains byte-identical.
FULL_TRAINING_FIELDS = ('schema', 'timing_file', 'benchmark_fit_ids',
    'benchmark_comparability_id', 'resume_fit_id', 'full_fits')
FULL_FIT_FIELDS = ('fit_id', 'timing_fit_id', 'epochs', 'fixed_seconds',
    'overhead_micro_usd', 'assumption')


def author_schema():
    return {
        'full_training': {'required_exact_fields': list(FULL_TRAINING_FIELDS),
            'schema': 'measured-full-training/v1',
            'benchmark_fit_ids': 'exactly three distinct SMOKE fit IDs',
            'full_fits': 'one row per FULL fit, in the frozen FULL-fit order'},
        'full_training.full_fits[]': {'required_exact_fields': list(FULL_FIT_FIELDS),
            'fit_id': 'the corresponding frozen FULL fit ID',
            'timing_fit_id': 'a SMOKE fit ID for the same arm',
            'epochs': 'positive integer; boolean is invalid',
            'fixed_seconds': 'finite nonnegative number or numeric string',
            'overhead_micro_usd': 'nonnegative integer; boolean is invalid',
            'assumption': 'nonempty scientific applicability explanation; exact key is assumption'},
        'validation': 'No additional fields. The existing contract() validator also checks cross-field bindings.'}


def validate_fits(plan, *, incremental=False):
    """Pure shared schema check for author output and runtime selection."""
    fits = plan.get('fits')
    if not isinstance(fits, list) or not fits:
        raise ValueError('EXPERIMENT_FROZEN_FITS_REQUIRED')
    for fit in fits:
        if (not isinstance(fit, dict) or set(fit) != {'fit_id','stage','arm','fold','realization','outputs','validation_checks'} | ({'preprocessing_id'} if incremental and plan.get('preprocessing') else set())
                or type(fit['fold']) is not int or fit['fold'] < 0
                or fit['stage'] not in {'SMOKE','FULL'}
                or any(not isinstance(fit[k], str) or not fit[k] for k in ('fit_id','arm','realization'))
                or not isinstance(fit['outputs'], list) or not fit['outputs']
                or any(not isinstance(name, str) or not name for name in fit['outputs'])):
            raise ValueError('EXPERIMENT_FROZEN_FIT_FIELDS')
    return fits

def number(value, *, positive=False):
    if type(value) not in (str,int,float):raise ValueError('EXPERIMENT_PROJECTION_NUMBER')
    try: result=decimal(value)
    except (ValueError,ArithmeticError):raise ValueError('EXPERIMENT_PROJECTION_NUMBER') from None
    if result<0 or (positive and result<=0):raise ValueError('EXPERIMENT_PROJECTION_NUMBER')
    return result

def contract(plan):
    value=plan.get('full_training')
    if (not isinstance(value,dict) or set(value)!={'schema','timing_file','benchmark_fit_ids',
            'benchmark_comparability_id','resume_fit_id','full_fits'}
            or value['schema']!='measured-full-training/v1'):
        raise ValueError('EXPERIMENT_PROJECTION_CONTRACT')
    name=value['timing_file']
    if (not isinstance(name,str) or Path(name).name!=name or not name.endswith('.json')
            or name=='validation.json'):
        raise ValueError('EXPERIMENT_PROJECTION_TIMING_FILE')
    fits=plan.get('fits',[])
    if (not isinstance(fits,list) or not fits or any(not isinstance(f,dict) or
            not isinstance(f.get('fit_id'),str) for f in fits)
            or len({f['fit_id'] for f in fits})!=len(fits)):
        raise ValueError('EXPERIMENT_PROJECTION_FITS')
    byid={f['fit_id']:f for f in fits}
    smoke=[f['fit_id'] for f in fits if f.get('stage')=='SMOKE']
    full=[f['fit_id'] for f in fits if f.get('stage')=='FULL']
    benchmark=value['benchmark_fit_ids'];rows=value['full_fits']
    if (not isinstance(benchmark,list) or len(benchmark)!=3
            or any(not isinstance(x,str) or x not in smoke for x in benchmark)
            or len(set(benchmark))!=3 or value['resume_fit_id'] not in smoke
            or not isinstance(value['benchmark_comparability_id'],str)
            or not value['benchmark_comparability_id'].strip()
            or not isinstance(rows,list) or not full or len(rows)!=len(full)):
        raise ValueError('EXPERIMENT_PROJECTION_FROZEN_SELECTION')
    required=set(benchmark)
    for fit_id,row in zip(full,rows):
        if (not isinstance(row,dict) or set(row)!={'fit_id','timing_fit_id','epochs',
                'fixed_seconds','overhead_micro_usd','assumption'}
                or row['fit_id']!=fit_id or not isinstance(row['timing_fit_id'],str)
                or row['timing_fit_id'] not in smoke or type(row['epochs']) is not int
                or row['epochs']<1 or type(row['overhead_micro_usd']) is not int
                or row['overhead_micro_usd']<0 or not isinstance(row['assumption'],str)
                or not row['assumption'].strip()):
            raise ValueError('EXPERIMENT_PROJECTION_FULL_FIT')
        number(row['fixed_seconds'])
        if byid[fit_id]['arm']!=byid[row['timing_fit_id']]['arm']:
            raise ValueError('EXPERIMENT_PROJECTION_ARM_TIMING')
        required.add(row['timing_fit_id'])
    if any(name not in byid[x].get('outputs',[]) for x in required):
        raise ValueError('EXPERIMENT_PROJECTION_UNDECLARED_TIMING')
    return value,smoke,byid
