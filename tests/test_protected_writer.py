import os
import pytest
from orchestrator.protected_writer import credentials,PERMISSIONS,REPOSITORY_ID


def cfg():return {'app_id':123,'installation_id':456,'repository_id':REPOSITORY_ID,'private_key':'synthetic-not-read','permission_decision':'fixture-only'}


def test_token_restricted_and_removed_on_failure(monkeypatch):
    monkeypatch.setattr('orchestrator.protected_writer.jwt',lambda c:'synthetic-jwt')
    def api(method,path,token,body=None):
        if method=='GET':return {'app_id':123,'repository_selection':'selected','permissions':PERMISSIONS}
        assert body=={'repository_ids':[REPOSITORY_ID],'permissions':PERMISSIONS}
        return {'permissions':PERMISSIONS,'repositories':[{'id':REPOSITORY_ID}],'token':'synthetic-token'}
    monkeypatch.setattr('orchestrator.protected_writer.api',api)
    before=os.environ.get('GH_TOKEN')
    with pytest.raises(RuntimeError):
        with credentials(cfg()) as receipt:
            assert 'token' not in receipt and os.environ['GH_TOKEN']=='synthetic-token'
            raise RuntimeError('fixture interrupt')
    assert os.environ.get('GH_TOKEN')==before


def test_unexpected_grant_rejected(monkeypatch):
    monkeypatch.setattr('orchestrator.protected_writer.jwt',lambda c:'synthetic-jwt')
    monkeypatch.setattr('orchestrator.protected_writer.api',lambda *a:{'app_id':123,'repository_selection':'all','permissions':PERMISSIONS})
    with pytest.raises(ValueError,match='INSTALLATION_BOUNDARY'):
        with credentials(cfg()):raise AssertionError('must not obtain credentials')
