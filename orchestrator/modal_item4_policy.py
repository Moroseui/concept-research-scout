"""Operator-selected item4 caps and actual-rate pricing shared by preparation and fits."""
from decimal import Decimal, ROUND_CEILING
from orchestrator.modal_billing import decimal

AUTHORITY = 'a74959ac4546a982af4ae13719108f93d50bc91e264200c48afeb660fae51b59'
TEAM_AUTHORITY = 'a9bb4359c8218f263ee04591211820db7886b779894b73170b4ac9495fe10fc6'
SMOKE_CAP = 75_000_000
PROJECTION_LIMIT = 1_200_000_000
TOTAL_CAP = 1_275_000_000
CONCURRENCY = 50
USAGE_CEILING = 1_000_000_000
SPEND_CEILING = 900_000_000
GPU_KEYS = {'A100-80GB': 'gpu_hour_cost_a100_80gb', 'H100': 'gpu_hour_cost_h100',
            'B200': 'gpu_hour_cost_b200'}


def quote(resources, rates, overhead_micro):
    if not isinstance(resources, dict) or set(resources) != {'gpu', 'cpu', 'memory_mib', 'timeout_seconds'}:
        raise ValueError('ITEM4_RESOURCE_FIELDS')
    gpu, cpu, memory, seconds = (resources[k] for k in ('gpu','cpu','memory_mib','timeout_seconds'))
    if (gpu is not None and gpu not in GPU_KEYS) or any(type(v) is not int for v in (cpu,memory,seconds,overhead_micro)):
        raise ValueError('ITEM4_RESOURCE_TYPES')
    if not (1 <= cpu <= 64 and 1024 <= memory <= 524288 and 1 <= seconds <= 86400 and 0 <= overhead_micro <= SMOKE_CAP):
        raise ValueError('ITEM4_RESOURCE_BOUNDS')
    keys = ['cpu_hour_cost_sandbox','mem_gib_hour_cost_sandbox'] + ([GPU_KEYS[gpu]] if gpu else [])
    if any(k not in rates or decimal(rates[k]) <= 0 for k in keys):
        raise ValueError('ITEM4_ACTUAL_RATES_REQUIRED')
    hourly = cpu*decimal(rates[keys[0]]) + Decimal(memory)/1024*decimal(rates[keys[1]])
    if gpu: hourly += decimal(rates[GPU_KEYS[gpu]])
    compute = int((hourly * seconds / 3600 * 1_000_000).to_integral_value(rounding=ROUND_CEILING))
    return {'compute_micro_usd':compute,'overhead_micro_usd':overhead_micro,
            'reserved_micro_usd':compute+overhead_micro,
            'rates':{k:str(decimal(rates[k])) for k in keys},
            'basis':'hard Sandbox CPU/RAM maxima and lifetime, plus storage/transfer/probe overhead'}

