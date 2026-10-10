"""Immutable-engine receipt tests; synthetic authority only, no deployment."""
import json
from types import SimpleNamespace
import pytest
from orchestrator import private_records as pr,autonomy_review
from tools import preparation_scientific_runtime as runtime

@pytest.fixture
def installed(tmp_path,monkeypatch):
    root=tmp_path/'immutable';record=tmp_path/'record';review=tmp_path/'review'
    for path in (root,record,review):pr.mkdir(path)
    names=['orchestrator/preparation_interleaving.py','orchestrator/analysis_driver.py',
        'orchestrator/aggregate_analysis_scope.py','orchestrator/colab_preparation_scope.py',
        'tools/preparation_scientific_runtime.py']
    pins={}
    for name in names:
        pr.mkdir((root/name).parent,parents=True,exist_ok=True)
        raw=b'# synthetic reviewed fixture\n';pr.write_bytes(root/name,raw);pins[name]=runtime.pi.sha(raw)
    q={'verdict':'APPROVE','source_sha':'a'*40,'report_sha256':'b'*64,'test_only':True}
    value={'root':str(root),'source':q['source_sha'],'review_sha256':q['report_sha256'],
           'status':'INSTALLED_HELD','files':pins}
    pr.write_text(record/'installed.json',json.dumps(value))
    pr.write_text(review/'packet-manifest.json',json.dumps({'source_files':pins}))
    monkeypatch.setattr(runtime,'ROOT',root);monkeypatch.setattr(runtime,'RECORD',record)
    monkeypatch.setattr(runtime,'trusted',lambda p:pr.check(p))
    monkeypatch.setattr(autonomy_review,'verify_result',lambda p:q)
    overlay=SimpleNamespace(verify=lambda:q,review_folder=review)
    return overlay,root,record,value


def test_immutable_engine_needs_no_git_or_completed_record(installed):
    overlay,root,record,value=installed
    assert not (root/'.git').exists() and not (record/'COMPLETE.json').exists()
    runtime.reviewed_root(overlay)


@pytest.mark.parametrize('field,value',[('root','/other'),('source','c'*40),('review_sha256','c'*64),('status','COMPLETE')])
def test_wrong_install_receipt_refuses(installed,field,value):
    overlay,root,record,receipt=installed;receipt[field]=value
    pr.write_text(record/'installed.json',json.dumps(receipt))
    with pytest.raises(ValueError,match='INSTALLED_RECEIPT'):runtime.reviewed_root(overlay)


def test_modified_immutable_component_refuses(installed):
    overlay,root,record,value=installed
    pr.write_bytes(root/'orchestrator/analysis_driver.py',b'# changed\n')
    with pytest.raises(ValueError,match='RUNTIME_SOURCE_CHANGED'):runtime.reviewed_root(overlay)
