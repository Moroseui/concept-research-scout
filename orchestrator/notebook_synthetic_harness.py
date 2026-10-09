"""Trusted synthetic checks of the actual revised notebook; no top-level cells run."""
import ast
import copy
import hashlib
import json
import math
import sys
import traceback
from pathlib import Path


def module(notebook, index):
    # Pure interface checks do not require the scientific test dependencies.
    global np, pd
    import numpy as np
    import pandas as pd
    source = ''.join(notebook['cells'][index]['source'])
    lines = source.splitlines(True)
    if lines and lines[0].startswith('%%writefile '):
        lines[0] = '\n'
    tree = ast.parse(''.join(lines))
    namespace = {'np': np, 'pd': pd, 'json': json, 'hashlib': hashlib, 'math': math}
    # Constants only: never evaluate notebook configuration, I/O or calls.
    config = ''.join(notebook['cells'][4]['source']).splitlines(True)
    if config[0].startswith('%%writefile '):
        config[0] = '\n'
    for node in [*ast.parse(''.join(config)).body, *tree.body]:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                namespace[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    available = {n.name:n for n in tree.body if isinstance(n, ast.FunctionDef)}
    required = {6:{'_fx','official_lesion_metrics'},
                8:{'coverage_support','zscore_in_brain','histeq_in_brain'},
                22:{'validate_full_folds','verdict_from_intervals'}}[index]
    if not required <= available.keys():
        raise ValueError('SYNTHETIC_REQUIRED_HELPERS_MISSING:'+','.join(sorted(required-available.keys())))
    needed=set(required)
    while True:
        additions={n.id for name in needed for n in ast.walk(available[name])
                   if isinstance(n,ast.Name) and n.id in available}-needed
        if not additions: break
        needed.update(additions)
    definitions = [available[name] for name in available if name in needed]
    for node in definitions:
        if node.decorator_list:
            raise ValueError('SYNTHETIC_NO_DECORATOR_EXECUTION')
        for default in [*node.args.defaults, *[x for x in node.args.kw_defaults if x is not None]]:
            ast.literal_eval(default)  # no executable defaults
    exec(compile(ast.Module(body=definitions, type_ignores=[]), f'actual-notebook-cell-{index}', 'exec'), namespace)
    return namespace


def refused(call):
    try:
        call()
    except (ValueError, AssertionError):
        return
    raise AssertionError('Invalid synthetic case was not refused')


def test_fold_completeness(nb):
    fn = module(nb, 22)['validate_full_folds']
    held = {i: [f'SYNTHETIC_{j:03d}' for j in range(i, 99, 5)] for i in range(5)}
    rows = [{'case': case, 'fold': fold, 'shuffle': 101} for fold, cases in held.items() for case in cases]
    fn(pd.DataFrame(rows), held)
    for changed in [rows[:-1], rows+[rows[0]], rows+[{'case':'SYNTHETIC_EXTRA','fold':0,'shuffle':101}],
                    [{**row, 'fold': 4} if i == 0 else row for i,row in enumerate(rows)],
                    [{**row, 'shuffle': 102} if i == 0 else row for i,row in enumerate(rows)]]:
        refused(lambda: fn(pd.DataFrame(changed), held))
    refused(lambda: fn(pd.DataFrame([r for r in rows if r['fold'] == 0]), {0: held[0]}))
    bad = copy.deepcopy(held); bad[1][0] = bad[0][0]
    refused(lambda: fn(pd.DataFrame(rows), bad))
    return {'valid_rows': 99, 'folds': 5, 'negative_cases': 7, 'identifiers': 'synthetic only'}


def test_verdict_rule(nb):
    fn = module(nb, 22)['verdict_from_intervals']
    assert fn((.03,.01,.05),(.02,.005,.04), complete=True) == 'better'
    assert fn((-.03,-.05,-.01),(-.02,-.04,-.005), complete=True) == 'worse'
    for a,b in [((.03,.01,.05),(.0,-.02,.02)), ((.03,.01,.05),(-.02,-.04,-.005)),
                ((.01,0.,.02),(.03,.01,.05)), ((0.,0.,0.),(0.,0.,0.))]:
        assert fn(a,b,complete=True) == 'no clear difference'
    assert fn((.03,.01,.05),(.02,.005,.04),complete=False) == 'provisional'
    refused(lambda: fn((float('nan'),0,1),(.02,.005,.04),complete=True))
    refused(lambda: fn((.03,.05,.01),(.02,.005,.04),complete=True))
    return {'conjunctive_intervals': True, 'no_ratio_argument': True,
            'cases': 9, 'training_variance_estimated': False}


def test_coverage_handling(nb):
    ns = module(nb, 8); support = ns['coverage_support']
    x = np.array([0.,1.,np.nan,np.inf,2.,0.],dtype=np.float32)
    brain = np.array([1,1,1,1,1,0],dtype=bool)
    covered = np.array([1,1,1,1,0,1],dtype=bool)
    mask, record = support(x,brain,covered)
    assert np.array_equal(mask,np.array([1,1,0,0,0,0],dtype=bool))
    assert record['coverage_known'] is True
    mask2, record2 = support(x,brain,None)
    assert np.array_equal(mask2,np.array([1,1,0,0,1,0],dtype=bool))
    assert record2['coverage_known'] is False  # finite != measured spatial coverage
    refused(lambda: support(x,brain,np.ones(2,dtype=bool)))
    for name in ('zscore_in_brain','histeq_in_brain'):
        fn = ns[name]
        actual, rec = fn(x,mask)
        assert np.isfinite(actual).all()
        assert np.all(actual[~mask] == 0)
        empty, rec = fn(x,np.zeros_like(brain))
        assert np.isfinite(empty).all() and np.all(empty==0) and rec.get('fallback')
        constant, rec = fn(np.ones_like(x),brain)
        assert np.isfinite(constant).all() and np.all(constant==0) and rec.get('fallback')
    tiny = np.array([.1,.10001,.10002],dtype=np.float32)
    scaled, rec = ns['zscore_in_brain'](tiny,np.ones(3,dtype=bool))
    assert rec['sd_used'] >= ns['ZSCORE_MIN_SD']
    assert np.isfinite(scaled).all()
    return {'valid_zero_retained': True, 'nonfinite_excluded_before_transform': True,
            'unknown_coverage_not_certified': True, 'empty_constant_floor_checked': True}


def test_existing_unit_checks(nb):
    ns=module(nb,6)
    observed=ns['_fx']()
    assert observed['both_empty']==(1.,0)
    assert observed['truth_only'][0]==0.
    assert observed['diagonal_contact_one_piece']==(1.,0)
    assert observed['truth_one_pred_two_split'][1]==1
    assert abs(observed['one_matched_one_fp'][0]-.6667)<1e-3
    assert observed['iou_0.2_boundary'][0]==1.
    return {'original_fixture_cases': 6, 'values': observed}


def test_execution_module(nb):
    """Run author-supplied CPU tests against the exact exported module.

    This process already runs in the private, no-network synthetic sandbox.
    No other notebook cell is executed and no real data path is mounted.
    """
    import importlib.util
    import unittest
    sys.path.insert(0, '/package')
    path = Path('/package/execution.py')
    spec = importlib.util.spec_from_file_location('execution', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['execution'] = module
    spec.loader.exec_module(module)
    suite = module.synthetic_tests()
    if not isinstance(suite, unittest.TestSuite) or suite.countTestCases() < 1:
        raise ValueError('NOTEBOOK_EXECUTION_SYNTHETIC_TESTS_REQUIRED')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if (not result.wasSuccessful() or result.testsRun < 1 or result.skipped
            or result.expectedFailures or result.unexpectedSuccesses):
        raise ValueError('NOTEBOOK_EXECUTION_SYNTHETIC_TESTS_FAILED')
    return {'module_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'tests_run':result.testsRun,'failures':0,'errors':0,'skipped':0,
            'expected_failures':0,'unexpected_successes':0,
            'patient_data':False,'network':False}


def main():
    raw=Path('/package/revised.ipynb').read_bytes()
    nb=json.loads(raw)
    records=[]
    names = ['test_fold_completeness','test_verdict_rule','test_coverage_handling','test_existing_unit_checks']
    if Path('/package/execution.py').exists(): names.append('test_execution_module')
    for name in names:
        try:
            details=globals()[name](nb)
            records.append({'test':name,'status':'PASS','details':details})
        except BaseException as error:
            records.append({'test':name,'status':'FAIL','type':type(error).__name__,
                            'message':str(error),'traceback':traceback.format_exc()})
    result={'schema':'notebook-synthetic-tests/v1','notebook_sha256':hashlib.sha256(raw).hexdigest(),
            'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'status':'PASS' if all(r['status']=='PASS' for r in records) else 'FAIL',
            'records':records,'patient_data':False,'network':False,'full_notebook_executed':False,
            'scope':'Actual pure functions extracted by AST; no top-level notebook data loading, training or driver.'}
    Path('/workspace/result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'tests':len(records)}))
    return 0 if result['status']=='PASS' else 1


if __name__=='__main__':
    sys.exit(main())
