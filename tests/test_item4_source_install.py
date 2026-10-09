"""Review originals are service-owned; authentication precedes protected copying."""
from pathlib import Path
import json
import pytest
from tools import install_item4_source_preparation as install,item4_source_preparation as h
from orchestrator import autonomy_review as ar,manual_host_guard as guard,manual_executor as me

class ReachedNativeVerification(Exception):pass

@pytest.fixture
def authenticated_review(tmp_path,monkeypatch):
    packet=tmp_path/'packet';review=tmp_path/'service-review';review.mkdir();packet.mkdir()
    files={name:Path(h.__file__).parents[1].joinpath(name).read_bytes() for name in h.FILES}
    for name,raw in files.items():
        p=packet/'source'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    source='a'*40
    manifest={'change_id':h.REVIEW_CHANGE,'source_sha':source,'source_files':{n:me.digest(v) for n,v in files.items()}}
    (review/'packet-manifest.json').write_text(json.dumps(manifest))
    runtime=tmp_path/'runtime.json';runtime.write_bytes(b'{}')
    approval={'verdict':'APPROVE','source_sha':source,'change_id':h.REVIEW_CHANGE,'runtime_sha256':me.digest(runtime.read_bytes())}
    calls=[]
    monkeypatch.setattr(install.os,'getuid',lambda:0)
    monkeypatch.setattr(ar,'verify_packet',lambda p:manifest)
    def verify_result(p):
        assert p==review;calls.append(p);return approval
    monkeypatch.setattr(ar,'verify_result',verify_result)
    def trusted(p):
        p=Path(p)
        if p==review or review in p.parents:raise ValueError('HOST_PROOF_NOT_ROOT_OWNED')
        if str(p).startswith('/etc/research-system-manual-sprint10/releases/'):return runtime
        return p
    monkeypatch.setattr(guard,'trusted',trusted)
    def native():raise ReachedNativeVerification()
    monkeypatch.setattr(h,'native_helper',native)
    return packet,review,source,approval,calls

def test_authenticated_service_owned_review_passes_to_native_check(authenticated_review):
    packet,review,source,approval,calls=authenticated_review
    with pytest.raises(ReachedNativeVerification):install.install(packet,review,source,packet)
    assert calls==[review]

@pytest.mark.parametrize('change',['verdict','source','packet'])
def test_unauthorized_or_mismatched_review_still_refuses(authenticated_review,change):
    packet,review,source,approval,calls=authenticated_review
    if change=='verdict':approval['verdict']='REVISE'
    if change=='source':approval['source_sha']='b'*40
    if change=='packet':(review/'packet-manifest.json').write_text('{}')
    with pytest.raises(ValueError,match='INSTALL_(APPROVAL|PACKET)'):install.install(packet,review,source,packet)
    assert calls==[review]
