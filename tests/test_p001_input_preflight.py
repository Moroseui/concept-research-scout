"""Synthetic preflight tests: never use cohort or archive payloads."""
import importlib.util
from pathlib import Path
import numpy as np
import nibabel as nib
import pytest

spec=importlib.util.spec_from_file_location('preflight',Path(__file__).resolve().parents[1]/'scripts/p001_input_preflight.py')
preflight=importlib.util.module_from_spec(spec);spec.loader.exec_module(preflight)


def test_selection_is_admission_only_and_unique():
    selected={f'fixture-{i}':{'tmax':{'path':f'train/fixture-{i}/ses-01/fixture_tmax.nii.gz','size':'10'},'label':{'path':'DO_NOT_OPEN'}} for i in range(99)}
    rows=preflight.admission_members(selected)
    assert len(rows)==99 and 'DO_NOT_OPEN' not in str(rows)
    selected['fixture-0']['tmax']['path']='train/fixture-0/ses-02/fixture_tmax.nii.gz'
    with pytest.raises(ValueError,match='ADMISSION_MEMBER'):preflight.admission_members(selected)


def test_header_uses_proxy_not_voxel_array(tmp_path,monkeypatch):
    path=tmp_path/'synthetic.nii.gz'
    image=nib.Nifti1Image(np.zeros((2,3,4),dtype=np.int16),np.eye(4))
    image.header.set_slope_inter(0.1,2)
    nib.save(image,path)
    def forbidden(*a,**kw):raise AssertionError('voxel materialization forbidden')
    monkeypatch.setattr(nib.arrayproxy.ArrayProxy,'__array__',forbidden)
    monkeypatch.setattr(nib.Nifti1Image,'get_fdata',forbidden)
    record=preflight.header_record(path)
    assert record['shape']==[2,3,4]
    assert record['proxy_slope']==pytest.approx(.1)
    assert record['proxy_intercept']==2


def test_existing_or_active_execution_holds_preflight(tmp_path):
    proc=tmp_path/'proc';(proc/'7').mkdir(parents=True)
    output=tmp_path/'P001-v1'
    (proc/'7/cmdline').write_bytes(b'python\0/path/experiments/P001/run.py\0')
    assert preflight.reconcile_runtime(output,proc)['disposition'].startswith('HOLD')
    (proc/'7/cmdline').write_bytes(b'unrelated\0')
    output.mkdir()
    observed=preflight.reconcile_runtime(output,proc)
    assert observed['matching_processes']==0 and observed['disposition'].startswith('HOLD')
