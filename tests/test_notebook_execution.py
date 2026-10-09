"""Exact notebook export and real unittest execution, entirely synthetic."""
import json
from pathlib import Path
import pytest
from orchestrator import notebook_execution as execution, notebook_synthetic_harness as harness

SOURCE = """import unittest
def preprocess(input_root, output_root, contract):
    return None  # Synthetic interface fixture only.
def validate_preprocessing(output_root, contract):
    return {'fixture': 'synthetic only'}
def main(input_root, output_root, contract):
    return contract['synthetic_value'] + 1
class Checks(unittest.TestCase):
    def test_actual_entry(self):
        self.assertEqual(main(None, None, {'synthetic_value': 1}), 2)
def synthetic_tests():
    return unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
"""


def notebook(source=SOURCE):
    return json.dumps({'cells':[{'cell_type':'code','source':
        '%%writefile /content/sprint13_pipeline.py\n'+source}]}).encode()


def test_export_is_exact_writefile_concatenation_and_runs_no_notebook_cell(tmp_path):
    marker=tmp_path/'must-not-exist'
    nb=json.loads(notebook())
    nb['cells'].insert(0,{'cell_type':'code','source':f'open({str(marker)!r}, "w").write("not executed")'})
    nb['cells'].append({'cell_type':'code','source':'%%writefile -a /content/sprint13_pipeline.py\n# append preserved\n'})
    assert execution.extract(json.dumps(nb).encode())==(SOURCE+'# append preserved\n').encode()
    assert not marker.exists()


@pytest.mark.parametrize('change,code',[
    ('empty','NOTEBOOK_EXECUTION_MODULE_REQUIRED'),
    ('append-first','NOTEBOOK_EXECUTION_WRITEFILE_ORDER'),
    ('overwrite-twice','NOTEBOOK_EXECUTION_WRITEFILE_ORDER'),
    ('wrong-path','NOTEBOOK_UNREVIEWED_CELL_MAGIC'),
    ('missing-main','NOTEBOOK_EXECUTION_ENTRYPOINT:main'),
    ('different-args','NOTEBOOK_EXECUTION_ENTRYPOINT:main'),
    ('duplicate-main','NOTEBOOK_EXECUTION_ENTRYPOINT:main'),
    ('missing-tests','NOTEBOOK_EXECUTION_ENTRYPOINT:synthetic_tests')])
def test_incomplete_or_ambiguous_execution_contract_refuses(change,code):
    nb=json.loads(notebook())
    if change=='empty':nb['cells']=[]
    elif change=='append-first':nb['cells'][0]['source']=nb['cells'][0]['source'].replace('%%writefile ','%%writefile -a ',1)
    elif change=='overwrite-twice':nb['cells'].append(dict(nb['cells'][0]))
    elif change=='wrong-path':nb['cells'][0]['source']=nb['cells'][0]['source'].replace('/content/sprint13_pipeline.py','/somewhere/else.py')
    elif change=='missing-main':nb['cells'][0]['source']=nb['cells'][0]['source'].replace('def main(','def alternate(')
    elif change=='different-args':nb['cells'][0]['source']=nb['cells'][0]['source'].replace('output_root, contract','output_root, contract, extra=None')
    elif change=='duplicate-main':nb['cells'][0]['source']+='\ndef main(input_root, output_root, contract): pass\n'
    elif change=='missing-tests':nb['cells'][0]['source']=nb['cells'][0]['source'].replace('def synthetic_tests(','def unrelated(')
    with pytest.raises(ValueError,match='^'+code+'$'):execution.extract(json.dumps(nb).encode())


def test_author_test_runs_actual_export_not_a_controller_scientific_substitute(tmp_path,monkeypatch):
    # Only /package is mapped to a disposable fixture here. Native confinement
    # belongs to notebook_synthetic's existing server checks, not this unit test.
    path=tmp_path/'execution.py';path.write_bytes(execution.extract(notebook()))
    monkeypatch.setattr(harness,'Path',lambda value:path if value=='/package/execution.py' else Path(value))
    result=harness.test_execution_module({})
    assert result['tests_run']==1 and result['errors']==result['failures']==result['skipped']==0
    assert result['module_sha256']==harness.hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize('change',['empty','wrong-type','failure','skip','expected-failure'])
def test_empty_or_nonpassing_author_tests_never_pass(tmp_path,monkeypatch,change):
    source=SOURCE
    if change=='empty':source=source.replace('unittest.defaultTestLoader.loadTestsFromTestCase(Checks)','unittest.TestSuite()')
    elif change=='wrong-type':source=source.replace('unittest.defaultTestLoader.loadTestsFromTestCase(Checks)','True')
    elif change=='failure':source=source.replace("{'synthetic_value': 1}), 2)","{'synthetic_value': 1}), 3)")
    elif change=='skip':source=source.replace('    def test_actual_entry',"    @unittest.skip('synthetic negative fixture')\n    def test_actual_entry")
    else:
        source=source.replace('    def test_actual_entry','    @unittest.expectedFailure\n    def test_actual_entry').replace("{'synthetic_value': 1}), 2)","{'synthetic_value': 1}), 3)")
    path=tmp_path/'execution.py';path.write_bytes(execution.extract(notebook(source)))
    monkeypatch.setattr(harness,'Path',lambda value:path if value=='/package/execution.py' else Path(value))
    code='NOTEBOOK_EXECUTION_SYNTHETIC_TESTS_REQUIRED' if change in {'empty','wrong-type'} else 'NOTEBOOK_EXECUTION_SYNTHETIC_TESTS_FAILED'
    with pytest.raises(ValueError,match='^'+code+'$'):harness.test_execution_module({})


@pytest.mark.parametrize('change',['missing','duplicate','wrong-hash','zero','bool-count','skipped','failed'])
def test_passing_other_groups_cannot_substitute_for_execution_tests(change):
    d={'module_sha256':'a'*64,'tests_run':1,'failures':0,'errors':0,'skipped':0,
       'expected_failures':0,'unexpected_successes':0,'patient_data':False,'network':False}
    row={'test':'test_execution_module','status':'PASS','details':d};test={'records':[row]}
    assert execution.tests_passed(test,'a'*64)
    if change=='missing':test['records']=[]
    elif change=='duplicate':test['records'].append(dict(row))
    elif change=='wrong-hash':d['module_sha256']='b'*64
    elif change=='zero':d['tests_run']=0
    elif change=='bool-count':d['tests_run']=True
    elif change=='skipped':d['skipped']=1
    else:row['status']='FAIL'
    assert not execution.tests_passed(test,'a'*64)


@pytest.mark.parametrize('name',['preprocess','validate_preprocessing'])
@pytest.mark.parametrize('damage',['missing','wrong-signature','duplicate'])
def test_preprocessing_author_contract_refuses_before_any_execution(name,damage):
    source=SOURCE
    signature=('input_root, output_root, contract' if name=='preprocess' else 'output_root, contract')
    if damage=='missing':source=source.replace('def '+name+'(', 'def unused_'+name+'(')
    elif damage=='wrong-signature':source=source.replace('def '+name+'('+signature+')', 'def '+name+'()')
    else:source+='\ndef '+name+'('+signature+'): pass\n'
    # Legacy extraction's scope remains unchanged. The new actual execution
    # author and approval routes explicitly require the preprocessing interface.
    execution.extract(notebook(source))
    with pytest.raises(ValueError,match='^NOTEBOOK_EXECUTION_ENTRYPOINT:'+name+'$'):
        execution.extract(notebook(source),preprocessing=True)
