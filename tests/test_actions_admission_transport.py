"""Trusted API identity precedes small artifact retrieval; never accept run prose."""
import base64
import pytest
from test_actions_admission import fixture
from orchestrator.actions_admission_transport import collect


def test_attempt_endpoint_and_fixed_repository_binding():
    run,artifact,raw,workflow,expected=fixture();artifact['id']=77
    calls=[]
    def get(method,path,token):
        assert token=='fixture-private'
        calls.append(path)
        if '/attempts/' in path:return run
        if '/contents/' in path:return {'encoding':'base64','path':expected['workflow_path'],
                                        'content':base64.b64encode(workflow).decode()}
        return {'artifacts':[artifact]}
    def download(identity,token):
        assert identity==77 and token=='fixture-private';return raw
    assert collect(expected,'fixture-private',get=get,download=download)['attempt']=='2'
    assert all(path.startswith('/repos/Moroseui/concept-research-scout/') for path in calls)
    assert calls[0].endswith('/runs/123/attempts/2')


def test_wrong_run_refuses_before_source_or_archive_fetch():
    run,artifact,raw,workflow,expected=fixture();calls=[]
    def get(*args):calls.append(args);return {**run,'run_attempt':3}
    with pytest.raises(ValueError,match='RUN_BINDING'):
        collect(expected,'fixture',get=get,download=lambda *args:pytest.fail('no download'))
    assert len(calls)==1


def test_unreviewed_workflow_refuses_before_archive_listing():
    run,artifact,raw,workflow,expected=fixture();calls=[]
    def get(method,path,token):
        calls.append(path)
        if '/attempts/' in path:return run
        return {'encoding':'base64','path':expected['workflow_path'],
                'content':base64.b64encode(b'changed').decode()}
    with pytest.raises(ValueError,match='WORKFLOW_CHANGED'):
        collect(expected,'fixture',get=get,download=lambda *args:pytest.fail('no download'))
    assert len(calls)==2


def test_signed_download_never_forwards_authorization(monkeypatch):
    import urllib.error
    import orchestrator.actions_admission_transport as module
    calls=[]
    class Response:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self,limit):return b'synthetic zip bytes'
    class Opener:
        def open(self,request,timeout):
            calls.append(request)
            if request.full_url.startswith('https://api.github.com/'):
                raise urllib.error.HTTPError(request.full_url,302,'redirect',
                    {'Location':'https://fixture.blob.core.windows.net/blob?sig=private-fixture'},None)
            return Response()
    monkeypatch.setattr(module.urllib.request,'build_opener',lambda *args:Opener())
    assert module.artifact_bytes(7,'fixture-token')==b'synthetic zip bytes'
    assert calls[0].get_header('Authorization')=='Bearer fixture-token'
    assert calls[1].get_header('Authorization') is None
