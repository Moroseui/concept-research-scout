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


@pytest.mark.parametrize('changed',[False,True])
def test_047_uses_exact_historical_summary_and_original_stream(tmp_path,monkeypatch,changed):
    from orchestrator.notebook_evidence import inspect
    summary=b'{"synthetic":true}'
    contract='dc586665d0bece940d1a1f4b3b0572f8c951c2ba'
    stream=contract+' STUDY_COMPLETE '+summary.decode()
    notebook=json.dumps({'cells':[{'execution_count':7,'outputs':[{'output_type':'stream','text':stream}]}]}).encode()
    matches,_=inspect(notebook,summary,contract)
    prior={'source_commit':'940293b6d562f2d3dd6bfd9d8d8281ccf01e4783','replacement_commit':'c812421207b6ddcba6516444897c777d8440275a','contract':contract,'notebook_sha256':m.sha(notebook),'summary_sha256':m.sha(summary),'matches':matches}
    d=tmp_path/'notebook';d.mkdir()
    for name,raw in [('original.ipynb',notebook),('receipt.json',json.dumps(prior).encode())]:
        (d/name).write_bytes(raw);(d/name).chmod(0o600)
    original(tmp_path,'047-console',(stream+(' altered' if changed else '')).encode())
    def git(args,**kwargs):
        assert args[-1].endswith(':probes/047/results_v2/summary.json')
        return summary
    monkeypatch.setattr(m.subprocess,'check_output',git)
    if changed:
        with pytest.raises(ValueError,match='STREAM_DIFFERS'):m.sibling(tmp_path,d,tmp_path/'git')
    else:
        result=m.sibling(tmp_path,d,tmp_path/'git')
        assert result['saved_stream_byte_identical'] and result['exit_status'] is None
        assert not result['scientific_acceptance'] and not result['experiment_executed']
