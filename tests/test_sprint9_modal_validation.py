"""Deterministic validator checks; synthetic outputs, no patient computation."""
import csv
import io
import json
import pytest
from orchestrator import private_records
from orchestrator.sprint9_modal_validation import validate,BASELINE

@pytest.fixture
def result(tmp_path):
    folder=tmp_path/'return';private_records.mkdir(folder);private_records.mkdir(folder/'folds')
    cases=[f'dev-{i:03}' for i in range(20)];run='m3-synthetic';rows=[]
    fields=['case','recipe','fingerprint','shuffle','fold','train_seed','tp','fp','fn','dice','f1_voxel']
    means={}
    for recipe,fp in [('U_base_raw',200),('U_base_smoothed',170)]:
        dice=200/(200+fp+1000 if recipe.endswith('raw') else 200+fp+900);means[recipe]=dice
        for case in cases:rows.append(dict(zip(fields,[case,recipe,run,101,0,1,100,fp,1000 if recipe.endswith('raw') else 900,dice,dice])))
    stream=io.StringIO();writer=csv.DictWriter(stream,fields);writer.writeheader();writer.writerows(rows)
    private_records.write_text(folder/'folds/unet_U_base_s101_f0_t1.csv',stream.getvalue())
    binding={'run_id':run,'input_contract':{'synthetic':True},'outputs':['folds/unet_U_base_s101_f0_t1.csv','execution.json','summary.json']}
    smoke={'versions':{'synthetic':'no execution'},'partitions':{'held':cases}}
    receipt={'run_id':run,'input_contract':binding['input_contract'],'versions':smoke['versions'],'arm':'U_base','shuffle':101,'fold':0,'training_seed':1,'maximum_epochs':2,'held_count':20,'mean_dice':means}
    private_records.write_text(folder/'execution.json',json.dumps(receipt))
    private_records.write_text(folder/'summary.json',json.dumps({'mean_dice':means}))
    return folder,binding,smoke


def test_fixed_tolerance_accepts_valid_known_shape(result):
    report=validate(*result)
    assert report['status']=='VALID' and report['rows']==40 and report['patients']==20
    assert report['absolute_mean_dice_tolerance']==.005
    assert report['expected_mean_dice']==BASELINE

@pytest.mark.parametrize('damage',['extra','cohort','metric','summary','run'])
def test_validator_refuses_invalid_results(result,damage):
    folder,binding,smoke=result
    if damage=='extra':private_records.write_text(folder/'extra.txt','unexpected')
    if damage in {'cohort','metric','run'}:
        file=folder/'folds/unet_U_base_s101_f0_t1.csv';rows=list(csv.DictReader(file.open()))
        if damage=='cohort':rows[0]['case']='outside'
        if damage=='metric':rows[0]['dice']='nan'
        if damage=='run':rows[0]['fingerprint']='other'
        stream=io.StringIO();writer=csv.DictWriter(stream,list(rows[0]));writer.writeheader();writer.writerows(rows);private_records.write_text(file,stream.getvalue())
    if damage=='summary':private_records.write_text(folder/'summary.json',json.dumps({'mean_dice':{k:.9 for k in BASELINE}}))
    with pytest.raises(ValueError):validate(*result)


def test_valid_but_outside_tolerance_is_preserved_as_failure(result):
    folder,binding,smoke=result;file=folder/'folds/unet_U_base_s101_f0_t1.csv';rows=list(csv.DictReader(file.open()))
    for row in rows:row.update(tp='0',dice='0',f1_voxel='0')
    stream=io.StringIO();writer=csv.DictWriter(stream,list(rows[0]));writer.writeheader();writer.writerows(rows);private_records.write_text(file,stream.getvalue())
    means={k:0.0 for k in BASELINE}
    for name in ['execution.json','summary.json']:
        doc=json.loads((folder/name).read_text());doc['mean_dice']=means;private_records.write_text(folder/name,json.dumps(doc))
    assert validate(*result)['status']=='REPRODUCTION_FAILED'
    assert file.exists()
