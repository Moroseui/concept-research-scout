"""Synthetic harness fixtures only; none are a proposed scientific notebook."""
import copy
import json
import unittest

FOLDS = """
def validate_full_folds(table, held):
    expected={(101,k,c) for k,values in held.items() for c in values}
    flat=[c for values in held.values() for c in values]
    if set(held)!=set(range(5)) or len(flat)!=99 or len(set(flat))!=99: raise ValueError('membership')
    actual=list(zip(table.shuffle,table.fold,table.case))
    if len(actual)!=99 or len(set(actual))!=99 or set(actual)!=expected: raise ValueError('rows')
    return True

def verdict_from_intervals(a,b,complete=True):
    for ci in (a,b):
        if len(ci)!=3 or not all(math.isfinite(x) for x in ci) or not ci[1]<=ci[0]<=ci[2]: raise ValueError('interval')
    if not complete: return 'provisional'
    if a[1]>0 and b[1]>0: return 'better'
    if a[2]<0 and b[2]<0: return 'worse'
    return 'no clear difference'
"""
COVERAGE = """
def coverage_support(x,brain,coverage=None):
    if coverage is not None and coverage.shape!=x.shape: raise ValueError('shape')
    return brain & np.isfinite(x) & (coverage if coverage is not None else True), {'coverage_known':coverage is not None}
def zscore_in_brain(x,mask):
    y=np.zeros_like(x)
    v=x[mask]
    if not len(v) or v.std()<1e-6:return y, {'fallback':'empty or constant'}
    sd=max(float(v.std()),ZSCORE_MIN_SD)
    y[mask]=(v-v.mean())/sd
    return y,{'fallback':None,'sd_used':sd}
def histeq_in_brain(x,mask):
    y=np.zeros_like(x);v=x[mask]
    if not len(v) or v.std()<1e-6:return y,{'fallback':'empty or constant'}
    y[mask]=np.searchsorted(np.sort(v),v,side='right')/len(v)
    return y,{'fallback':None}
"""
# Deliberate synthetic stand-in exercises harness result validation; the live
# negative-control receipt separately executes the genuine six original checks.
METRICS = """
def official_lesion_metrics(a,b): return None
def _fx():
    return {'both_empty':(1.,0),'truth_only':(0.,1),'diagonal_contact_one_piece':(1.,0),
            'truth_one_pred_two_split':(.5,1),'one_matched_one_fp':(2/3,1),'iou_0.2_boundary':(1.,0)}
"""


def fixture():
    nb={'cells':[{'cell_type':'markdown','source':[]} for _ in range(23)]}
    for index,source in [(4,'ZSCORE_MIN_SD = 0.01\n'),(6,METRICS),(8,COVERAGE),(22,FOLDS)]:
        nb['cells'][index]={'cell_type':'code','source':[source]}
    return nb



import tempfile
from pathlib import Path
from orchestrator import notebook_synthetic as sandbox

ENVIRONMENT={'environment_root':'/opt/research-system-cpu-tools/m2-python312-xgb341-v2',
             'environment_sha256':'0f71b0d0a8131090bca668b7da55e3aecf70392687b23dd7f7a264f0532fb34a'}


@unittest.skipUnless(Path(ENVIRONMENT['environment_root']).is_dir(),
                     'Native pinned CPU runtime required; exercised on the server')
class SyntheticHarnessTests(unittest.TestCase):
    def check(self,nb):
        with tempfile.TemporaryDirectory(prefix='nb-harness-') as temporary:
            folder=Path(temporary)/'run'
            receipt=sandbox.run(folder,json.dumps(nb).encode(),ENVIRONMENT)
            self.assertEqual(receipt['isolation']['status'],'ISOLATED')
            self.assertEqual(receipt['isolation']['network'],'UNSHARED')
            self.assertFalse(receipt['isolation']['patient_mounts'])
            self.assertFalse(receipt['isolation']['credentials'])
            # A repeated observation reuses exact evidence, never executes again.
            self.assertEqual(sandbox.run(folder,json.dumps(nb).encode(),ENVIRONMENT),receipt)
            return receipt

    def test_actual_exported_module_and_author_tests_in_native_sandbox(self):
        from test_notebook_execution import SOURCE
        from orchestrator.notebook_execution import extract, tests_passed
        import hashlib
        nb=fixture()
        nb['cells'].append({'cell_type':'code','source':[
            '%%writefile /content/sprint13_pipeline.py\n'+
            'from orchestrator.modal_fit_progress import FitProgress\n'+
            'from orchestrator.modal_nnunet import run_fit\n'+
            'assert callable(run_fit) and callable(FitProgress)\n'+SOURCE]})
        raw=json.dumps(nb).encode()
        with tempfile.TemporaryDirectory(prefix='nb-execution-') as temporary:
            folder=Path(temporary)/'run'
            receipt=sandbox.run(folder,raw,ENVIRONMENT,execution=True)
            self.assertEqual(receipt['status'],'PASS',receipt['tests'])
            self.assertEqual(receipt['isolation']['status'],'ISOLATED')
            module=extract(raw)
            self.assertEqual((folder/'package/execution.py').read_bytes(),module)
            from orchestrator.experiment_modal_package import support_files
            for name,data in support_files().items():
                self.assertEqual((folder/'package'/name).read_bytes(),data)
                self.assertEqual(receipt['binding']['files'][name],hashlib.sha256(data).hexdigest())
            self.assertTrue(tests_passed(receipt['tests'],hashlib.sha256(module).hexdigest()))
            self.assertEqual(sandbox.run(folder,raw,ENVIRONMENT,execution=True),receipt)

    def test_positive_control_all_groups(self):
        result=self.check(fixture())
        self.assertEqual(result['status'],'PASS',result['tests'])

    def test_bad_membership_verdict_and_coverage_caught(self):
        for cell,name,source in [
            (22,'test_fold_completeness',FOLDS+"\ndef validate_full_folds(table,held): return True\n"),
            (22,'test_verdict_rule',FOLDS+"\ndef verdict_from_intervals(a,b,complete=True): return 'better'\n"),
            (8,'test_coverage_handling',COVERAGE+"\ndef coverage_support(x,brain,coverage=None): return brain, {'coverage_known':True}\n")]:
            nb=fixture();nb['cells'][cell]['source']=[source]
            with self.subTest(group=name):
                result=self.check(nb)
                self.assertEqual(result['status'],'FAIL')
                self.assertEqual(next(x for x in result['tests']['records'] if x['test']==name)['status'],'FAIL')

    def test_top_level_notebook_operations_never_execute(self):
        nb=fixture();nb['cells'][22]['source']=[FOLDS+"\nraise RuntimeError('top-level must not execute')\n"]
        self.assertEqual(self.check(nb)['status'],'PASS')

    def test_decorator_or_executable_default_refuses(self):
        for source in ['@print\ndef validate_full_folds(table,held): return True\n',
                       'def validate_full_folds(table,held=print(\"bad\")): return True\n']:
            nb=fixture();nb['cells'][22]['source']=[FOLDS+source]
            with self.subTest(source=source):
                result=self.check(nb)
                self.assertEqual(result['status'],'FAIL')
                failed=next(x for x in result['tests']['records'] if x['test']=='test_fold_completeness')
                self.assertEqual(failed['type'],'ValueError')


if __name__=='__main__':
    unittest.main()
