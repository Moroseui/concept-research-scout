import json
from pathlib import Path
import pytest
from orchestrator import manual_context as mc,context_budget as cb
from test_context_budget import root,add_obligation
from test_manual_context import artifact,build


@pytest.mark.parametrize('kind,name', [('configuration','provenance-validators'),('run_spec','author5-original-SPEC.proposed.md')])
def test_large_original_is_scanned_exact_readonly_file_and_findings_stay_verbatim(root,kind,name):
    raw='Preserved validator or historical scientific specification.\n'*700
    row=artifact(root,kind,name,text=raw)
    quote=add_obligation(root,'adverse finding')
    body,m=build(root,'run_spec_author',[row])
    files=[v for v in m['workspace_files'] if v['id']==name]
    assert len(files)==1 and files[0]['sha256']==row['sha256']
    p=root/'workspaces/run_spec_author'/files[0]['path']
    assert p.read_text()==raw and p.stat().st_mode&0o777==0o400
    assert raw not in body and row['sha256'] in body and files[0]['path'] in body
    assert quote in body and m['characters']==len(body)
    assert mc.workspace_artifact(kind,artifact_id=name)


@pytest.mark.parametrize('damage',['changed','missing','symlink','private'])
def test_new_delivery_keeps_source_hash_membership_and_scanner_refusals(root,damage):
    row=artifact(root,'configuration','provenance-validators')
    p=root/row['path']
    if damage=='changed':p.write_text('tampered')
    elif damage=='missing':p.unlink()
    elif damage=='symlink':p.rename(root/'original');p.symlink_to(root/'original')
    else:
        p.write_text('sub-'+'stroke1234567890');row['sha256']=cb.sha(p.read_bytes())
    with pytest.raises((ValueError,OSError)):build(root,'run_spec_author',[row])
    assert not (root/'workspaces/run_spec_author/evidence').exists()


def test_unrelated_artifacts_remain_inline_and_cap_refuses(root):
    row=artifact(root,'configuration','other-validator',text='x'*200000)
    with pytest.raises(cb.ContextTooLarge):build(root,'run_spec_author',[row])
    assert not mc.workspace_artifact('configuration',artifact_id='other-validator')
    assert not mc.workspace_artifact('run_spec',artifact_id='other-history')


def test_evidence_manifest_is_append_only_with_exact_original_image_bytes():
    from tools import item4_scientific_revision_component as c
    repo=Path(__file__).resolve().parents[1]
    manifest=json.loads((repo/'docs/ITEM4_REVISION_EVIDENCE.json').read_bytes())
    checkpoint=json.loads((repo/'docs/ITEM4_REVISION_CHECKPOINT.json').read_bytes())
    assert c.sha((repo/'docs/ITEM4_REVISION_EVIDENCE.json').read_bytes())==checkpoint['evidence_manifest_sha256']
    names=[r['name'] for r in manifest['files']]
    assert len(names)==47 and len(set(names))==47
    assert names[38:42]==['NEXT_AUTHOR_EVIDENCE_POINTERS.md','PINNED_IMAGE_CONSUMER_PROOF.json','PINNED_IMAGE_NATIVE.original.json','PINNED_IMAGE_TERMINAL.original.json']
    assert 'latest genuine scientific REVISE' in c.guidance('run_spec_author','')
    assert 'Continue the preserved author7' not in c.GUIDANCE


@pytest.fixture
def upgrade_fixture(tmp_path,monkeypatch):
    from tools import install_item4_scientific_revision as i
    from types import SimpleNamespace
    root=tmp_path/'root';record=tmp_path/'record';review=tmp_path/'new-review'
    for p in (root/'tools',root/'docs',record/'evidence',record/'review',review):p.mkdir(parents=True,exist_ok=True)
    manifest={'schema':'example','files':[{'name':'original.txt','sha256':'kept'}]}
    checkpoint={'evidence_manifest_sha256':'old','original_calls':'unchanged'}
    files=['tools/item4_scientific_revision_component.py','docs/ITEM4_REVISION_CHECKPOINT.json','docs/ITEM4_REVISION_EVIDENCE.json']
    old={'source':i._contract.CONTINUATION_SOURCE,'review_sha256':i._contract.CONTINUATION_REVIEW,'files':{},'base_files':{'untouched':'pin'},'units':{'same.service':'same-pin'},'review_folder':str(record/'review')}
    original_state={'checkpoint':checkpoint,'manifest':manifest,'old':old};statefile=tmp_path/'prior.json';statefile.write_text(json.dumps(original_state))
    code='import json\nfrom pathlib import Path\nFILES='+repr(files)+'\ndef verified():\n v=json.loads(Path('+repr(str(statefile))+').read_text());return v["old"],v["checkpoint"],v["manifest"]\n'
    (root/files[0]).write_text(code);(root/files[1]).write_text(json.dumps(checkpoint));(root/files[2]).write_text(json.dumps(manifest))
    (record/'evidence/original.txt').write_bytes(b'exact original');(record/'review/original.json').write_text('original review')
    (record/'installed.json').write_text(json.dumps(old));(record/'APPLIED.json').write_text('{"status":"INSTALLED_HELD"}')
    (review/'new.json').write_text('genuine review fixture')
    updated_manifest={**manifest,'files':manifest['files']+[{'name':'additional.txt','sha256':'new'}]}
    bodies={files[0]:code.encode(),files[1]:json.dumps({**checkpoint,'evidence_manifest_sha256':'new'}).encode(),files[2]:json.dumps(updated_manifest).encode()}
    evidence={'original.txt':b'exact original','additional.txt':b'new evidence'}
    monkeypatch.setattr(i,'ROOT',root);monkeypatch.setattr(i,'RECORD',record);monkeypatch.setattr(i,'UNIT',tmp_path/'same.service')
    monkeypatch.setattr(i._contract,'held_application',lambda:'qualified-original');
    monkeypatch.setattr(i,'trusted',lambda p:Path(p));monkeypatch.setattr(i.os,'chown',lambda *a:None)
    calls=[]
    def check(cmd,**kw):
        calls.append(cmd)
        return 'ActiveState=inactive\nMainPID=0\nControlGroup=\n' if cmd[0]=='systemctl' else 'HELD_REVIEW5_NO_RUNNING_CALL\n'
    monkeypatch.setattr(i.subprocess,'check_output',check)
    monkeypatch.setattr(i.subprocess,'run',lambda *a,**kw:SimpleNamespace(returncode=0,stdout='verified',stderr=''))
    return i,root,record,review,statefile,bodies,evidence,calls


def test_upgrade_preserves_source_evidence_approval_and_no_apply_or_start(upgrade_fixture):
    i,root,record,review,statefile,bodies,evidence,calls=upgrade_fixture
    originals={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
    applied=(record/'APPLIED.json').read_bytes()
    result=i.upgrade(bodies,evidence,review,{'report_sha256':'new-review'},'new-source')
    assert result['status']=='UPDATED_HELD' and result['model_calls']==result['provider_calls']==0
    history=record/'history'/i._contract.CONTINUATION_SOURCE
    assert all((history/'source'/name).read_bytes()==raw for name,raw in originals.items())
    assert (history/'original-review-directory/original.json').read_text()=='original review'
    assert (history/'original-evidence-directory/original.txt').read_bytes()==b'exact original'
    assert (record/'evidence/original.txt').read_bytes()==b'exact original'
    assert (record/'APPLIED.json').read_bytes()==applied
    updated=json.loads((record/'installed.json').read_bytes())
    assert updated['base_files']=={'untouched':'pin'} and updated['units']=={'same.service':'same-pin'}
    assert all('start' not in cmd and 'apply' not in cmd for cmd in calls)


@pytest.mark.parametrize('fault',['prior-source','checkpoint','evidence-row','evidence-bytes','active','running-call'])
def test_upgrade_refuses_before_mutation(upgrade_fixture,fault,monkeypatch):
    i,root,record,review,statefile,bodies,evidence,calls=upgrade_fixture
    if fault=='prior-source':
        v=json.loads(statefile.read_text());v['old']['source']='other';statefile.write_text(json.dumps(v))
    elif fault=='checkpoint':
        key='docs/ITEM4_REVISION_CHECKPOINT.json';v=json.loads(bodies[key]);v['original_calls']='changed';bodies[key]=json.dumps(v).encode()
    elif fault=='evidence-row':
        key='docs/ITEM4_REVISION_EVIDENCE.json';v=json.loads(bodies[key]);v['files'][0]['sha256']='changed';bodies[key]=json.dumps(v).encode()
    elif fault=='evidence-bytes':evidence['original.txt']=b'changed'
    elif fault=='active':monkeypatch.setattr(i.subprocess,'check_output',lambda *a,**kw:'ActiveState=active\nMainPID=123\nControlGroup=/active\n')
    else:
        def pending(cmd,**kw):
            if cmd[0]=='systemctl':return 'ActiveState=inactive\nMainPID=0\nControlGroup=\n'
            raise i.subprocess.CalledProcessError(1,cmd)
        monkeypatch.setattr(i.subprocess,'check_output',pending)
    before={str(p):p.read_bytes() for top in (root,record) for p in top.rglob('*') if p.is_file()}
    with pytest.raises((ValueError,i.subprocess.CalledProcessError)):
        i.upgrade(bodies,evidence,review,{'report_sha256':'new-review'},'new-source')
    assert before=={str(p):p.read_bytes() for top in (root,record) for p in top.rglob('*') if p.is_file()}
    assert not (record/'history').exists()


def test_stopped_failed_unit_can_update_but_nonempty_cgroup_still_refuses(upgrade_fixture,monkeypatch):
    i,root,record,review,statefile,bodies,evidence,calls=upgrade_fixture
    def failed(cmd,**kw):
        return 'ActiveState=failed\nMainPID=0\nControlGroup=/still-present\n' if cmd[0]=='systemctl' else 'HELD_REVIEW5_NO_RUNNING_CALL\n'
    monkeypatch.setattr(i.subprocess,'check_output',failed)
    with pytest.raises(ValueError,match='AUTHOR_UPGRADE_ACTIVE'):
        i.upgrade(bodies,evidence,review,{'report_sha256':'new-review'},'new-source')
    assert not (record/'history').exists()
    monkeypatch.setattr(i.subprocess,'check_output',lambda cmd,**kw:failed(cmd,**kw).replace('/still-present',''))
    assert i.upgrade(bodies,evidence,review,{'report_sha256':'new-review'},'new-source')['status']=='UPDATED_HELD'
