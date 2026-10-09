"""One shared item6 allowance; scope selection never admits or executes work.

All five diagnostics share one canonical owner. A release, plan, grouping or
backlog-document change cannot silently create another 30-call/$100 allowance.
Scientific design and implementation remain the author/reviewer's responsibility.
"""
from pathlib import Path
import json
from orchestrator.manual_executor import digest

DOCUMENT = 'docs/DIAGNOSTICS_OPERATOR_DECISION.txt'
AUTHORITY = 'b203ee1ce27e909d9d78d44a6808e947ed02d4004f699acd70e40c73e0edc537'
ITEM_SHA256 = '7c7630f7f694f2ba7f5d57abc45f8f72c30b3389f4094878d9136e39fba723f6'
RUN_ID = 'diagnostics-' + AUTHORITY[:24]
CALL_LIMIT = 30
TOTAL_MICRO_USD = 100_000_000
TASK = 'directions-diagnostics'
DIAGNOSTICS = ('placement-vs-amount', 'small-lesion-components', 'calibration',
               'centre-coverage', 'admission-availability')


def authority(root=None):
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    path = root / DOCUMENT
    if path.is_symlink() or digest(path.read_bytes()) != AUTHORITY:
        raise ValueError('DIAGNOSTICS_OPERATOR_AUTHORITY_CHANGED')
    return AUTHORITY


def policy():
    return {'operator_sha256': authority(), 'item_sha256': ITEM_SHA256,
            'diagnostics': list(DIAGNOSTICS), 'cpu_only': True, 'training': False,
            'scientific_call_limit': CALL_LIMIT, 'total_micro_usd': TOTAL_MICRO_USD}


def validate_config(config, run):
    """Validate the protected lane selection without creating an allowance.

    The executor must additionally authenticate the reviewed code, data, exact
    backlog selection, native evidence and ordinary budget/admission controls.
    No per-diagnostic owner is permitted, even if execution is split into jobs.
    """
    if (run != RUN_ID or config.get('run_id') != run
            or type(config.get('item_number')) is not int or config['item_number'] != 6
            or config.get('backend') != 'cpu' or json.dumps(config.get('diagnostics'), sort_keys=True, allow_nan=False) != json.dumps(policy(), sort_keys=True, allow_nan=False)):
        raise ValueError('DIAGNOSTICS_SCOPE_OR_ALLOWANCE_BINDING')
    return CALL_LIMIT
