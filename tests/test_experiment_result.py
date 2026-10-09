"""Aggregate return and author validation contract, synthetic data only."""
import copy
import json
import pytest
from orchestrator import experiment_result as result, private_records as pr
from orchestrator.manual_executor import digest


@pytest.fixture
def returns(tmp_path):
    root=tmp_path/'returns';pr.mkdir(root)
    binding={'run_id':'synthetic-run','experiment':{'fit_id':'fit'},'spec_sha256':'a'*64,
        'code_sha256':'b'*64,'execution_plan_sha256':'c'*64,'outputs':['result.csv','validation.json']}
    plan={'fits':[{'fit_id':'fit','outputs':binding['outputs'],'validation_checks':['synthetic-check']}]}
    raw=b'group,metric\naggregate,0.5\n';pr.write_bytes(root/'result.csv',raw)
    validation={'schema':'experiment-validation/v1','run_id':'synthetic-run','fit_id':'fit',
        'spec_sha256':'a'*64,'code_sha256':'b'*64,'execution_plan_sha256':'c'*64,
        'files':{'result.csv':{'sha256':digest(raw),'bytes':len(raw)}},
        'checks':[{'id':'synthetic-check','status':'PASS','evidence':['result.csv']}]}
    pr.write_text(root/'validation.json',json.dumps(validation))
    return root,binding,plan,validation


def test_valid_aggregate_envelope_not_scientific_acceptance(returns):
    root,binding,plan,_=returns
    receipt=result.validate(root,binding,plan)
    assert receipt['status']=='VALIDATED' and receipt['scientifically_accepted'] is False
    assert receipt['files']['validation.json']['sha256']==digest((root/'validation.json').read_bytes())
    assert receipt==result.validate(root,binding,plan)


@pytest.mark.parametrize('damage',['failed','missing','extra-check','changed-id','duplicate-check',
    'missing-evidence','wrong-evidence','extra-file','changed-file','bad-binding','duplicate-json',
    'nonfinite','unsafe-file','binary','identifier','secret'])
def test_refusals(returns,damage):
    root,binding,plan,v=returns
    if damage=='failed':v['checks'][0]['status']='FAIL'
    elif damage=='missing':v['checks']=[]
    elif damage=='extra-check':v['checks'].append(copy.deepcopy(v['checks'][0]))
    elif damage=='changed-id':v['checks'][0]['id']='different'
    elif damage=='duplicate-check':plan['fits'][0]['validation_checks']*=2
    elif damage=='missing-evidence':v['checks'][0]['evidence']=[]
    elif damage=='wrong-evidence':v['checks'][0]['evidence']=['validation.json']
    elif damage=='extra-file':pr.write_text(root/'extra.txt','unselected')
    elif damage=='changed-file':pr.write_text(root/'result.csv','changed')
    elif damage=='bad-binding':v['code_sha256']='d'*64
    elif damage=='binary':pr.write_bytes(root/'result.csv',b'\x00synthetic')
    elif damage=='identifier':pr.write_text(root/'result.csv','sub-'+'stroke0000')
    elif damage=='secret':pr.write_text(root/'result.csv','access_'+'token=synthetic-forbidden-fixture')
    pr.write_text(root/'validation.json',json.dumps(v))
    if damage=='duplicate-json':pr.write_text(root/'validation.json','{"schema":"duplicate",'+json.dumps(v)[1:])
    elif damage=='nonfinite':pr.write_text(root/'validation.json',json.dumps(v)[:-1]+',"extra":NaN}')
    elif damage=='unsafe-file':(root/'result.csv').chmod(0o644)
    with pytest.raises(ValueError):result.validate(root,binding,plan)


@pytest.mark.parametrize('name',['../result.json','/result.json','weights.pth','.hidden.json','sub-'+'stroke0000.json'])
def test_nonaggregate_paths_refuse_before_execution(returns,name):
    _,binding,plan,_=returns
    binding['outputs']=[name,'validation.json'];plan['fits'][0]['outputs']=binding['outputs']
    with pytest.raises(ValueError):result.selected(plan,binding)


def test_extracted_scanner_is_identical_to_previous_implementation():
    # Exact function-source hash from 98b68acbfe2c40309e108ffcec15228fd69a0343.
    # ast.dump omits empty fields on newer Python; source bytes are version-independent.
    # No history fetch or privacy-rule change is needed in an installed suite.
    import ast, hashlib
    from pathlib import Path
    from orchestrator import scientific_view_scan
    tree=ast.parse(Path(scientific_view_scan.__file__).read_text())
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='scan')
    assert hashlib.sha256(ast.get_source_segment(Path(scientific_view_scan.__file__).read_text(),function).encode()).hexdigest()=='a670bb8ee23dce1ce56788c52c02bc790bf64173b94830ecb6b9fe54d2534935'


@pytest.mark.parametrize('raw',[b'{"metric":1e999}',b'{"metric":-1e999}',b'{"metric":NaN}',b'{"metric":Infinity}'])
def test_nonfinite_json_numbers_refuse(raw):
    with pytest.raises(ValueError,match='^EXPERIMENT_RESULT_NONFINITE$'):result.strict(raw)
