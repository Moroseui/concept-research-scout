import json
import pytest
from orchestrator.colab_notebook_delivery import variants, COVERAGE_INDEPENDENT_ARMS

def notebook(arm):
    cells=[dict(cell_type='markdown',metadata={},source=[]) for _ in range(4)]
    cells.append(dict(cell_type='code',metadata={},outputs=[],execution_count=None,
        source=[f'DELIVERY_ARM = {arm!r}\n','DELIVERY_FOLDS = (0, 1, 2, 3, 4)\n',
                'def preserved_helper():\n','    return 42\n']))
    return (json.dumps(dict(nbformat=4,nbformat_minor=5,metadata={},cells=cells))+'\n').encode()

@pytest.mark.parametrize('arm',sorted(COVERAGE_INDEPENDENT_ARMS))
def test_exact_arm_and_only_fold_literal_change(arm):
    raw=notebook(arm);out=variants(raw,expected_arm=arm);original=json.loads(raw)
    assert set(out)=={f'13B_{arm}.ipynb',*[f'13B_{arm}_fold{k}.ipynb' for k in range(5)]}
    assert out[f'13B_{arm}.ipynb']==raw
    for fold in range(5):
        actual=json.loads(out[f'13B_{arm}_fold{fold}.ipynb'])
        src=''.join(actual['cells'][4]['source'])
        assert src==''.join(original['cells'][4]['source']).replace('(0, 1, 2, 3, 4)',repr((fold,)))
        actual['cells'][4]=original['cells'][4]
        assert actual==original

@pytest.mark.parametrize('arm',['A1_multiwin','A1_pnormct','A1_pnorm_v2','A1_L','A1_repeat2'])
def test_legacy_default_does_not_admit_another_arm(arm):
    with pytest.raises(ValueError,match='EXACT_ARM_FOLDS'):
        variants(notebook(arm))

@pytest.mark.parametrize('arm',['A1_zscore','A1_histeq','unknown','../other',None,[],True])
def test_held_unknown_or_malformed_controller_arm_refuses(arm):
    with pytest.raises(ValueError,match='RELEASED_ARM_REQUIRED'):
        variants(notebook('A1_repeat'),expected_arm=arm)

def test_authored_arm_cannot_override_controller_selection():
    with pytest.raises(ValueError,match='EXACT_ARM_FOLDS'):
        variants(notebook('A1_repeat2'),expected_arm='A1_multiwin')

@pytest.mark.parametrize('arm',['A1_multiwin','A1_pnormct','A1_pnorm_v2','A1_L'])
def test_arm_level_delivery_keeps_exact_author_bytes_without_fold_files(arm):
    raw=notebook(arm)
    assert variants(raw,expected_arm=arm,arm_level_only=True)=={f'13B_{arm}.ipynb':raw}

@pytest.mark.parametrize('change',['single-fold','executed','wrong-arm','held-arm'])
def test_arm_level_format_retains_content_and_scope_refusals(change):
    nb=json.loads(notebook('A1_multiwin'));arm='A1_multiwin'
    if change=='single-fold':nb['cells'][4]['source'][1]='DELIVERY_FOLDS = (0,)\n'
    elif change=='executed':nb['cells'][4]['execution_count']=1
    elif change=='wrong-arm':arm='A1_pnormct'
    else:arm='A1_zscore'
    with pytest.raises(ValueError):
        variants(json.dumps(nb).encode(),expected_arm=arm,arm_level_only=True)

@pytest.mark.parametrize('flag',[1,'yes',None,[]])
def test_arm_level_format_requires_explicit_boolean(flag):
    with pytest.raises(ValueError,match='FORMAT_BOOLEAN'):
        variants(notebook('A1_multiwin'),expected_arm='A1_multiwin',arm_level_only=flag)
