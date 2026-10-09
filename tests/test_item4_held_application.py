import json
from pathlib import Path
import pytest
from tools import item4_scientific_revision_component as c


@pytest.fixture
def applied(tmp_path,monkeypatch):
    from orchestrator import autonomy_review as ar,manual_host_guard as hg
    from orchestrator import private_records as pr
    dest=tmp_path/'state';dest.mkdir();record=tmp_path/'record';record.mkdir()
    raw=json.dumps({'review_sha256':c.APPLICATION_REVIEW,'status':'READY_NO_MODEL_CALL','model_calls':0}).encode()
    pr.write_bytes(dest/'applied.json',raw)
    approval={'verdict':'APPROVE','change_id':c.CHANGE,'source_sha':c.APPLICATION_SOURCE,'report_sha256':c.APPLICATION_REVIEW}
    paths=[]
    def verify(path):paths.append(path);return approval
    monkeypatch.setattr(c,'DEST',dest);monkeypatch.setattr(c,'RECORD',record)
    monkeypatch.setattr(c,'APPLICATION_SHA',c.sha(raw));monkeypatch.setattr(hg,'trusted',lambda p:p)
    monkeypatch.setattr(ar,'verify_result',verify)
    return dest,record,raw,approval,paths


def test_original_application_approval_authenticated_without_rewriting(applied):
    dest,record,raw,approval,paths=applied
    assert c.held_application()==c.APPLICATION_REVIEW
    assert paths==[record/'history'/c.APPLICATION_SOURCE/'original-review-directory']
    assert (dest/'applied.json').read_bytes()==raw


@pytest.mark.parametrize('fault',['bytes','missing','verdict','source','change','review','application-review','application-status'])
def test_no_missing_or_changed_application_or_approval_is_accepted(applied,fault,monkeypatch):
    dest,record,raw,approval,paths=applied
    if fault=='bytes':(dest/'applied.json').write_bytes(raw+b' ')
    elif fault=='missing':(dest/'applied.json').unlink()
    elif fault in ('application-review','application-status'):
        v=json.loads(raw);v['review_sha256' if fault=='application-review' else 'status']='changed'
        new=json.dumps(v).encode();(dest/'applied.json').write_bytes(new);monkeypatch.setattr(c,'APPLICATION_SHA',c.sha(new))
    else:approval[{'verdict':'verdict','source':'source_sha','change':'change_id','review':'report_sha256'}[fault]]='other'
    with pytest.raises((ValueError,OSError)):c.held_application()
