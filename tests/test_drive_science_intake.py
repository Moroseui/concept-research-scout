import json
import pytest
from orchestrator import drive_science_intake as m


def original(root, alias, raw):
    p=root/(alias+'-original-0001');p.mkdir(exist_ok=True)
    (p/'original').write_bytes(raw);(p/'original').chmod(0o600)
    r={'status':'PRIVATE_ORIGINAL_COLLECTED','sha256':m.sha(raw),'bytes':len(raw),'implementation_sha256':m.IMPLEMENTATION,'alias':alias}
    (p/'receipt.json').write_text(json.dumps(r));(p/'receipt.json').chmod(0o600)


def fixture(root):
    h=json.dumps({'private-case-token':{'sha256':'a'*64,'header':{'shape':[2,3,4],'dtype':'float32','proxy_slope':1.0,'proxy_intercept':0.0,'xyzt_units':['mm','unknown']}}}).encode()
    r={'status':'INPUT_INTEGRITY_AND_HEADERS_VERIFIED','prediction_executed':False,'labels_opened':False,'reserved_access':False,'archive_size':99014629647,'archive_md5':'36ae28b9a17f7340b8bbef62b595cb57','eligible_cohort_verified':99,'admission_members_checked':1,'selection_rule':'first_lexical_eligible_id_no_outcome_selection','headers_sha256':m.sha(h),'unit_semantics':'HEADER_EVIDENCE_ONLY_REQUIRES_RELEASE_PROVENANCE_ASSESSMENT','launch_authorized':False,'elapsed_seconds':23.0}
    original(root,'p001-preflight-headers',h)
    for alias in ['p001-preflight-receipt','p001-preflight-console']:original(root,alias,json.dumps(r).encode())
    return r,h


def test_case_identity_stays_private_and_correspondence_is_not_acceptance(tmp_path):
    fixture(tmp_path);out=m.p001(tmp_path);text=json.dumps(out)
    assert 'private-case-token' not in text and 'a'*64 not in text
    assert not out['scientific_acceptance'] and not out['launch_authorized']
    assert not out['original_attempt_binding_supplied']


@pytest.mark.parametrize('kind',['console','header','collection','permission','symlink','extra','nonfinite'])
def test_refuses_mismatch_or_unsafe_originals(tmp_path,kind):
    r,h=fixture(tmp_path)
    if kind=='console':original(tmp_path,'p001-preflight-console',b'{}')
    if kind=='header':original(tmp_path,'p001-preflight-headers',h+b' ')
    if kind=='collection':(tmp_path/'p001-preflight-console-original-0001/original').write_bytes(b'{}')
    if kind=='permission':(tmp_path/'p001-preflight-console-original-0001/original').chmod(0o644)
    if kind=='symlink':
        p=tmp_path/'p001-preflight-console-original-0001/original';p.rename(p.with_name('saved'));p.symlink_to(p.with_name('saved'))
    if kind in ('extra','nonfinite'):
        if kind=='extra':r['private_case']='private-case-token'
        else:r['elapsed_seconds']=float('nan')
        for a in ['p001-preflight-receipt','p001-preflight-console']:original(tmp_path,a,json.dumps(r).encode())
    with pytest.raises(ValueError):m.p001(tmp_path)
