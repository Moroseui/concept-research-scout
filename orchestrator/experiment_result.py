"""Validate author-owned checks and aggregate returns before leaving the Volume.

No scientific thresholds or conclusions are invented here. The frozen plan
names the checks; reviewed scientific code evaluates them and writes evidence.
Passing this envelope is validation, never independent scientific acceptance.
"""
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
from orchestrator import private_records as pr
from orchestrator.scientific_view_scan import scan


def strict(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result: raise ValueError('EXPERIMENT_RESULT_DUPLICATE_FIELD')
            result[key] = value
        return result
    def invalid(value): raise ValueError('EXPERIMENT_RESULT_NONFINITE')
    def number(value):
        result=float(value)
        if not math.isfinite(result): raise ValueError('EXPERIMENT_RESULT_NONFINITE')
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid, parse_float=number)


def pin(raw): return hashlib.sha256(raw).hexdigest()


def selected(plan, binding):
    fits = plan.get('fits')
    if not isinstance(fits, list): raise ValueError('EXPERIMENT_RESULT_PLAN')
    rows = [row for row in fits if isinstance(row, dict)
            and row.get('fit_id') == binding['experiment']['fit_id']]
    if len(rows) != 1: raise ValueError('EXPERIMENT_RESULT_FIT')
    row = rows[0]; checks = row.get('validation_checks')
    if (not isinstance(checks, list) or not checks or any(not isinstance(x, str)
            or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}', x) for x in checks)
            or len(set(checks)) != len(checks)):
        raise ValueError('EXPERIMENT_RESULT_CHECK_SELECTION')
    outputs = row.get('outputs')
    if (outputs != binding.get('outputs') or not isinstance(outputs, list)
            or len(outputs) < 2 or any(not isinstance(x,str) for x in outputs)
            or len(set(outputs)) != len(outputs) or 'validation.json' not in outputs):
        raise ValueError('EXPERIMENT_RESULT_OUTPUT_SELECTION')
    for name in outputs:
        if (not isinstance(name, str) or PurePosixPath(name).name != name
                or PurePosixPath(name).suffix not in {'.json', '.csv', '.md', '.txt'}
                or name.startswith('.') or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]*', name)):
            raise ValueError('EXPERIMENT_RESULT_AGGREGATE_PATH')
        scan(name.encode(), frozenset(), kind='aggregate')
    return row


def validate(folder, binding, plan):
    """Pure local file validation, shared by worker and controller.

    This never computes patient results. All selected bytes are scanned before
    publication/collection. Per-patient artifacts remain in the private Volume;
    reviewed methods must produce the separately declared aggregate returns.
    """
    row = selected(plan, binding); folder = Path(folder)
    pr.check_tree(folder)
    paths = {str(p.relative_to(folder)):p for p in folder.rglob('*') if p.is_file()}
    if set(paths) != set(row['outputs']): raise ValueError('EXPERIMENT_RESULT_MEMBER_SET')
    files = {}; scans = {}; raw = {}
    for name, path in paths.items():
        if path.stat().st_size > 1_500_000: raise ValueError('EXPERIMENT_RESULT_FILE_LIMIT')
        data = path.read_bytes()
        scans[name] = scan(data, frozenset(), kind='aggregate')
        if path.suffix == '.json': strict(data)
        raw[name] = data; files[name] = {'sha256':pin(data), 'bytes':len(data)}
    value = strict(raw['validation.json'])
    expected = {'schema':'experiment-validation/v1', 'run_id':binding['run_id'],
        'fit_id':binding['experiment']['fit_id'], 'spec_sha256':binding['spec_sha256'],
        'code_sha256':binding['code_sha256'], 'execution_plan_sha256':binding['execution_plan_sha256']}
    if (not isinstance(value, dict) or set(value) != set(expected)|{'checks','files'}
            or any(value.get(key) != content for key,content in expected.items())):
        raise ValueError('EXPERIMENT_RESULT_VALIDATION_BINDING')
    observed = {name:entry for name,entry in files.items() if name != 'validation.json'}
    if (value['files'] != observed or any(not isinstance(entry,dict)
            or type(entry.get('bytes')) is not int for entry in value['files'].values())):
        raise ValueError('EXPERIMENT_RESULT_FILE_BINDING')
    checks = value['checks']
    if not isinstance(checks, list) or len(checks) != len(row['validation_checks']):
        raise ValueError('EXPERIMENT_RESULT_CHECKS')
    evidence = set()
    for name, check in zip(row['validation_checks'], checks):
        if (not isinstance(check, dict) or set(check) != {'id','status','evidence'}
                or check['id'] != name or check['status'] != 'PASS'
                or not isinstance(check['evidence'], list) or not check['evidence']
                or any(not isinstance(p, str) or p not in observed for p in check['evidence'])
                or len(set(check['evidence'])) != len(check['evidence'])):
            raise ValueError('EXPERIMENT_RESULT_CHECK_FAILED_OR_MISSING')
        evidence.update(check['evidence'])
    if evidence != set(observed): raise ValueError('EXPERIMENT_RESULT_UNCHECKED_FILE')
    return {'schema':'experiment-result-receipt/v1', 'status':'VALIDATED',
        **{k:v for k,v in expected.items() if k != 'schema'}, 'files':files,
        'checks':checks, 'scans':scans, 'scientifically_accepted':False}
