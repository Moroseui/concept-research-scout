import ast
import json
import pytest
from orchestrator.p001_preflight_transport import notebook,cells,public_receipt


def test_thin_notebook_preserves_separate_retrieval_and_private_capture():
    sources=cells('a'*40,'/content/drive/MyDrive/isles-pilot/archive/train.7z','/content/drive/MyDrive/isles-pilot/p001-preflight-'+'b'*32)
    n=notebook('a'*40,'/content/drive/MyDrive/isles-pilot/archive/train.7z','/content/drive/MyDrive/isles-pilot/p001-preflight-'+'b'*32)
    assert len(sources)==6
    assert all(not c['outputs'] for c in n['cells'] if c['cell_type']=='code')
    for source in sources:ast.parse(source)
    assert 'receipt.json' in sources[-1] and 'subprocess' not in sources[-1]
    assert 'dup2' in sources[3] and 'dup2' in sources[4]
    assert '--filter=blob:none' in sources[3] and 'clone' not in sources[3]
    assert 'DISPATCH_INTENT_NO_AUTOMATIC_RETRY' in sources[4]
    assert 'P001/run.py' not in sources[4]


def test_private_text_in_allowed_field_refuses_before_transport():
    r={'status':'FAILED','prediction_executed':False,'labels_opened':False,'reserved_access':False,'elapsed_seconds':1,'failure_type':'ValueError'}
    assert public_receipt(r)==r
    r['failure_type']='private clinical detail'
    with pytest.raises(ValueError,match='RECEIPT_REJECTED'):public_receipt(r)
    r['failure_type']='ValueError';r['extra']='private detail'
    with pytest.raises(ValueError,match='RECEIPT_REJECTED'):public_receipt(r)
