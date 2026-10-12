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
