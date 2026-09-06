import json
from pathlib import Path
import pytest
from orchestrator.hosted_context import DOCUMENTS,build,envelope


def fixture(root):
    for name in DOCUMENTS:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps({'entries':[]}) if name=='evidence/research_context.json' else 'Approved fixture direction or bound source')


def test_fresh_and_recovery_receive_canonical_versions_and_current_state(tmp_path):
    root=tmp_path/'source';fixture(root)
    folder=tmp_path/'attempt';folder.mkdir()
    (folder/'packet.json').write_text(json.dumps({'jobs':[{'id':'eligible'}],'decision_inbox':['launch-gate']}))
    first,c=envelope(root,folder,'Fresh driver task')
    assert 'eligible' in first and 'launch-gate' in first
    direction='docs/operations/REMOTE_OPERATING_DIRECTION.md'
    old=c['documents'][direction]['sha256']
    (root/direction).write_text('Approved updated fixture direction; launch remains gated')
    recovery=folder/'review-recovery';recovery.mkdir()
    (recovery/'packet.json').write_text(json.dumps({'jobs':[{'id':'new-eligible'}]}))
    second,r=envelope(root,recovery,'Original review preserved unchanged')
    assert r['documents'][direction]['sha256']!=old
    assert 'new-eligible' in second and 'Original review preserved unchanged' in second
    assert set(r['documents'])==set(c['documents'])
    assert r['documents'][direction]['disposition']=='APPROVED_OPERATING_DIRECTION'


def test_missing_canonical_context_or_task_fails_closed(tmp_path):
    with pytest.raises(FileNotFoundError):build(tmp_path,{})
    fixture(tmp_path)
    with pytest.raises(ValueError,match='CURRENT_TASK'):envelope(tmp_path,tmp_path,'no task')


def test_empty_task_packet_is_rejected(tmp_path):
    fixture(tmp_path)
    (tmp_path/'packet.json').write_text('{"jobs":[]}')
    with pytest.raises(ValueError,match='CURRENT_TASK'):envelope(tmp_path,tmp_path,'empty')
