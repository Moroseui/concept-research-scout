"""The linked reviewer may reuse only the byte-exact approved classifier."""
import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import review_sender_continuation_once as final
from tools import review_sender_recovery_once as boot
from test_review_sender_recovery_once import case

@pytest.fixture
def prior(tmp_path,monkeypatch):
    root=tmp_path/'prior';(root/'tools').mkdir(parents=True);(root/'docs').mkdir()
    names=['tools/review_sender_recovery_once.py','docs/ITEM4_AUTHOR22_TERMINAL_PRIVATE.json']
    raw=Path(boot.__file__).read_bytes();(root/names[0]).write_bytes(raw);(root/names[1]).write_text('{}')
    manifest=tmp_path/'packet-manifest.json';manifest.write_text(json.dumps({'source_files':{n:final.sha((root/n).read_bytes()) for n in names}}))
    result={'verdict':'APPROVE','change_id':'item4-sender-recovery-20261010','source_sha':'41b93574a0ad0fb546745095ff0078debd6f133d','report_sha256':final.APPROVAL}
    monkeypatch.setattr(final,'PRIOR',root)
    monkeypatch.setattr(final,'trusted',lambda p:manifest if Path(p).name=='packet-manifest.json' else Path(p))
    return NS(verify_result=lambda p:dict(result),regular=lambda p:manifest),result,root

def test_verified_classifier_retains_narrow_proof_checks(prior):
    ar,_,_=prior;qualified,binding=final.classifier(ar)
    assert qualified.CHANGE==final.CHANGE
    assert qualified.sha(Path(qualified.__file__).read_bytes())==qualified.sha(Path(boot.__file__).read_bytes())
    assert binding=={}

@pytest.mark.parametrize('fault',['verdict','source_sha','change_id','report_sha256','source','binding'])
def test_changed_authority_or_classifier_refused(prior,fault):
    ar,result,root=prior
    if fault=='source':(root/'tools/review_sender_recovery_once.py').write_text('pass')
    elif fault=='binding':(root/'docs/ITEM4_AUTHOR22_TERMINAL_PRIVATE.json').write_text('{"changed":true}')
    else:result[fault]='changed'
    with pytest.raises(ValueError):final.classifier(ar)

def test_original_review_retained_new_request_counted_separately(case,monkeypatch):
    db,binding,original,*_=case
    db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?)',('old-review','implementation_review',boot.CHANGE,'COMPLETE'))
    monkeypatch.setattr(boot,'CHANGE',final.CHANGE)
    before=list(db.iterdump())
    assert boot.exceptions(db,None,binding,original,lambda p:p.read_bytes())[0]['id']=='exact'
    assert list(db.iterdump())==before
    db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?)',('new-review','implementation_review',final.CHANGE,'FAILED'))
    before=list(db.iterdump())
    with pytest.raises(ValueError):boot.exceptions(db,None,binding,original,lambda p:p.read_bytes())
    assert list(db.iterdump())==before
