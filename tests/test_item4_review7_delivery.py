import pytest
from orchestrator import manual_context as mc, context_budget as cb, scientific_intake
from test_context_budget import root,add_obligation
from test_manual_context import artifact
from tools import item4_scientific_revision_component as component

def build(root,monkeypatch,row,task='Inspect exact originals.'):
    monkeypatch.setattr(scientific_intake,'load_views',lambda *a,**kw:([],[]))
    return mc.build(root,stage='run_spec_review',idea_ids=['P001'],task=task,
        artifacts=[row],workspace=root/'work',private_intake={'sha256':'a'*64})

def test_full_configuration_file_readonly_and_all_obligations_inline(root,monkeypatch):
    quote=add_obligation(root,'adverse finding')
    raw='Exact configuration and authority wording.\n'*1500
    row=artifact(root,'configuration','item4-operator-document-1',text=raw)
    body,m=build(root,monkeypatch,row)
    file=next(x for x in m['workspace_files'] if x['id']==row['id'])
    p=root/'work'/file['path']
    assert p.read_bytes()==raw.encode() and file['sha256']==row['sha256']
    assert p.stat().st_mode&0o777==0o400
    assert raw not in body and file['path'] in body and row['sha256'] in body
    assert quote in body and m['characters']==len(body)<200000
    assert not mc.workspace_artifact('configuration',artifact_id='item4-operator-document-1')

@pytest.mark.parametrize('damage',['changed','missing','symlink','private','oversize-task'])
def test_configuration_delivery_preserves_refusals(root,monkeypatch,damage):
    row=artifact(root,'configuration','item4-operator-document-1')
    p=root/row['path'];task='Inspect.'
    if damage=='changed':p.write_text('changed')
    elif damage=='missing':p.unlink()
    elif damage=='symlink':p.rename(root/'original');p.symlink_to(root/'original')
    elif damage=='private':p.write_text('sub-'+'stroke1234567890');row['sha256']=cb.sha(p.read_bytes())
    else:task='x'*200000
    with pytest.raises((ValueError,OSError)):build(root,monkeypatch,row,task)
    assert not (root/'work/evidence').exists()

@pytest.mark.parametrize('field',['verdict','change_id','source_sha','report_sha256',None])
def test_current_grant_uses_its_original_approval(tmp_path,monkeypatch,field):
    from orchestrator import autonomy_review as ar,manual_host_guard as hg
    approval={'verdict':'APPROVE','change_id':'item4-review6-continuation-20261008',
        'source_sha':component.THIRD_SOURCE,'report_sha256':component.THIRD_REVIEW}
    paths=[]
    monkeypatch.setattr(component,'RECORD',tmp_path);monkeypatch.setattr(hg,'trusted',lambda p:p)
    def verify(path):paths.append(path);return approval
    monkeypatch.setattr(ar,'verify_result',verify)
    if field:
        approval[field]='wrong'
        with pytest.raises(ValueError,match='HELD_THIRD_CONTINUATION_APPROVAL'):component.held_third_continuation_approval()
    else:assert component.held_third_continuation_approval()==component.THIRD_REVIEW
    assert paths==[tmp_path/'history'/component.THIRD_SOURCE/'original-review-directory']
