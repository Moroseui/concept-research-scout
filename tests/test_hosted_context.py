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
    first,c=envelope(root,folder,'Fresh driver task',verified_source='a'*40)
    assert 'eligible' in first and 'launch-gate' in first
    direction='docs/operations/REMOTE_OPERATING_DIRECTION.md'
    old=c['documents'][direction]['sha256']
    (root/direction).write_text('Approved updated fixture direction; launch remains gated')
    recovery=folder/'review-recovery';recovery.mkdir()
    (recovery/'packet.json').write_text(json.dumps({'jobs':[{'id':'new-eligible'}]}))
    second,r=envelope(root,recovery,'Original review preserved unchanged',verified_source='a'*40)
    assert r['documents'][direction]['sha256']!=old
    assert 'new-eligible' in second and 'Original review preserved unchanged' in second
    assert set(r['documents'])==set(c['documents'])
    assert r['documents'][direction]['disposition']=='APPROVED_OPERATING_DIRECTION'


def test_missing_canonical_context_or_task_fails_closed(tmp_path):
    with pytest.raises(FileNotFoundError):build(tmp_path,{})
    fixture(tmp_path)
    with pytest.raises(ValueError,match='CURRENT_TASK'):envelope(tmp_path,tmp_path,'no task',verified_source='a'*40)


def test_empty_task_packet_is_rejected(tmp_path):
    fixture(tmp_path)
    (tmp_path/'packet.json').write_text('{"jobs":[]}')
    with pytest.raises(ValueError,match='CURRENT_TASK'):envelope(tmp_path,tmp_path,'empty',verified_source='a'*40)


def test_source_and_own_task_packet_required(tmp_path):
    fixture(tmp_path)
    (tmp_path/'packet.json').write_text('{"jobs":["old"]}')
    recovery=tmp_path/'recovery';recovery.mkdir()
    with pytest.raises(ValueError,match='VERIFIED_SOURCE'):
        envelope(tmp_path,tmp_path,'missing source')
    with pytest.raises(ValueError,match='CURRENT_TASK'):
        envelope(tmp_path,recovery,'no parent fallback',verified_source='a'*40)
    _, packet=envelope(tmp_path,tmp_path,'bound',verified_source='a'*40)
    import hashlib
    assert packet['task_packet']['sha256']==hashlib.sha256((tmp_path/'packet.json').read_bytes()).hexdigest()


def current_policy_fixture(root):
    import shutil
    from orchestrator.hosted_context import policy_files
    source=Path(__file__).resolve().parents[1]
    fixture(root)
    for name in policy_files(source):
        destination=root/name;destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source/name,destination)


def test_portable_current_policy_reaches_both_distinct_roles(tmp_path):
    from orchestrator.hosted_context import policy_files
    root=tmp_path/'snapshot';current_policy_fixture(root)
    task=tmp_path/'task';task.mkdir()
    changes={'schema':'research-change-request/v1','requests':[{'review_status':'PENDING'}]}
    (task/'packet.json').write_text(json.dumps({'jobs':['desk'], 'recorded_changes':changes}))
    author,a=envelope(root,task,'Analyze the bounded evidence',verified_source='a'*40,family='codex')
    reviewer,b=envelope(root,task,'Independently challenge the analysis',verified_source='a'*40,family='claude')
    assert a['shared_policy']==b['shared_policy']
    assert a['role']['instruction']!=b['role']['instruction']
    assert a['task_state']['recorded_changes']==b['task_state']['recorded_changes']==changes
    assert 'Pending is not approval' in reviewer
    assert 'MATERIAL_DEPLOYMENT_CLARIFICATION_20260911.md' in author
    assert all((root/name).is_file() for name in policy_files(root))
    assert 'configs/scientific-delegation-20260909.json' in policy_files(root)
    with pytest.raises(ValueError,match='CURRENT_HOSTED_ROLE_REQUIRED'):
        envelope(root,task,'Unattributed call',verified_source='a'*40)


def test_current_snapshot_rejects_missing_or_changed_shared_policy(tmp_path):
    current_policy_fixture(tmp_path)
    name='docs/operations/MATERIAL_DEPLOYMENT_CLARIFICATION_20260911.md'
    original=(tmp_path/name).read_bytes()
    (tmp_path/name).write_text('Changed authority without a version binding')
    with pytest.raises(ValueError,match='SCIENTIFIC_OPERATING_CONTEXT_CHANGED'):
        build(tmp_path,{'jobs':['desk']})
    (tmp_path/name).write_bytes(original)
    (tmp_path/name).unlink()
    with pytest.raises(ValueError,match='SCIENTIFIC_AUTHORITY_REGULAR_FILE_REQUIRED'):
        build(tmp_path,{'jobs':['desk']})
