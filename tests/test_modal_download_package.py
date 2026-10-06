"""Real stdlib package assembly; synthetic cohort/plans only, no network."""
from pathlib import Path
import json,subprocess,sys
import pytest
from test_modal_ctp_download import planned,image_plan
from orchestrator import modal_download_package as p, private_records


def test_real_package_contains_only_allowlisted_modules_and_bound_metadata(planned,tmp_path):
    f=planned;root=Path(__file__).resolve().parents[1];destination=tmp_path/'package'
    result=p.emit(root,destination,f.cohort,{'ctp':f.plan},'attempt1')
    checked=p.verify(destination,result['manifest_sha256'])
    assert checked['patient_computation'] is False
    assert set(checked['files'])=={'run.py','cohort.json','ctp-plan.json'}|{'orchestrator/'+n for n in p.MODULES}
    assert result['provider_operations']==0 and result['network_payload_bytes']==0
    with pytest.raises(ValueError,match='^DOWNLOAD_PACKAGE_EXISTS$'):p.emit(root,destination,f.cohort,{'ctp':f.plan},'attempt1')
    # The exact isolated launcher refuses a wrong pin before any import/download.
    out=subprocess.run([sys.executable,'-I','-S','-B',str(destination/'run.py'),'0'*64,'ctp'],capture_output=True,text=True)
    assert out.returncode!=0 and 'DOWNLOAD_PACKAGE_MANIFEST_PIN' in out.stderr


def test_package_pin_or_members_cannot_be_changed(planned,tmp_path):
    f=planned;root=Path(__file__).resolve().parents[1];destination=tmp_path/'package'
    result=p.emit(root,destination,f.cohort,{'ctp':f.plan},'attempt1')
    private_records.write_bytes(destination/'extra.py',b'print("not selected")')
    with pytest.raises(ValueError,match='^DOWNLOAD_PACKAGE_CHANGED$'):p.verify(destination,result['manifest_sha256'])


def test_both_metadata_plans_use_same_frozen_cohort(planned,tmp_path):
    f=planned;ctp=f.plan;image_plan(f)
    result=p.emit(Path(__file__).resolve().parents[1],tmp_path/'package',f.cohort,{'ctp':ctp,'images':f.plan},'attempt1')
    value=p.verify(tmp_path/'package',result['manifest_sha256'])
    assert set(value['plans'])=={'ctp','images'}
    assert result['planned_download_bytes']==(99+693)*len(f.body)


def test_mislabeled_plan_refuses_before_creating_package(planned,tmp_path):
    f=planned
    with pytest.raises(ValueError,match='^DOWNLOAD_PACKAGE_PLAN_KIND$'):
        p.emit(Path(__file__).resolve().parents[1],tmp_path/'package',f.cohort,{'images':f.plan},'attempt1')
    assert not (tmp_path/'package').exists()
