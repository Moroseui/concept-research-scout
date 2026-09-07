from types import SimpleNamespace
from pathlib import Path
import json
from unittest.mock import patch
from orchestrator.job_store import Store
from orchestrator.readiness_discussion import discuss


def test_one_system_discussion_per_completion_set(tmp_path):
    from orchestrator.hosted_context import DOCUMENTS
    for name in DOCUMENTS:
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text('{"entries":[]}' if name=='evidence/research_context.json' else 'Canonical fixture direction')
    q=Store(tmp_path/'readiness.sqlite')
    v={'scope':'METADATA_ONLY_NOT_SCIENTIFIC_VALIDATION','binding':{'source':'a'*40,'handler':'context_inventory'},'facts':[],'finished':1}
    q.db.execute('INSERT INTO events VALUES(?,?,?)',('event','task',json.dumps(v)))
    with patch('orchestrator.readiness_discussion.execute',return_value={'status':'REVIEWED_PROPOSAL_NOT_ADOPTED'}) as call:
        first=discuss(SimpleNamespace(ROOT=tmp_path),tmp_path,tmp_path/'output','proposal')
        second=discuss(SimpleNamespace(ROOT=tmp_path),tmp_path,tmp_path/'output','proposal')
        assert call.call_count==1 and second['duplicate'] and first['identity']==second['identity']
        assert call.call_args.args[1]=='discuss'
        assert 'CURRENT CANONICAL OPERATING CONTEXT' in call.call_args.args[3]
        assert len(list((tmp_path/'discussion-contexts').glob('*.json')))==1


def test_ratified_context_refuses_preview_and_binds_discussion_revision(tmp_path):
    import pytest
    q=Store(tmp_path/'readiness.sqlite')
    value={'scope':'METADATA_ONLY_NOT_SCIENTIFIC_VALIDATION','binding':{'source':'a'*40,'handler':'context_inventory'},'facts':[],'finished':1}
    q.db.execute('INSERT INTO events VALUES(?,?,?)',('event','task',json.dumps(value)))
    context={'selected_scientific_context':{'selection':{'sha256':'a'*64}},'documents':{}}
    with patch('orchestrator.readiness_discussion.build',return_value=context), patch('orchestrator.readiness_discussion.execute',return_value={'status':'REVIEWED_PROPOSAL_NOT_ADOPTED'}) as call:
        with pytest.raises(ValueError,match='RATIFIED_CONTEXT_REFUSES_PROPOSAL_PREVIEW'):
            discuss(SimpleNamespace(ROOT=tmp_path),tmp_path,tmp_path/'bad','stale-preview')
        assert not call.called
        first=discuss(SimpleNamespace(ROOT=tmp_path),tmp_path,tmp_path/'first')
        again=discuss(SimpleNamespace(ROOT=tmp_path),tmp_path,tmp_path/'first')
        assert again['duplicate'] and call.call_count==1
        context['task_state']={'decision_inbox':[{'status':'unrelated update'}]}
        assert discuss(SimpleNamespace(ROOT=tmp_path),tmp_path,tmp_path/'first')['duplicate']
        assert call.call_count==1
        context['selected_scientific_context']['selection']['sha256']='b'*64
        amended=discuss(SimpleNamespace(ROOT=tmp_path),tmp_path,tmp_path/'amended')
        assert amended['identity']!=first['identity'] and call.call_count==2
        assert call.call_args.kwargs['proposal'] is None
        assert 'do not re-request' in call.call_args.args[3]
        assert len(list((tmp_path/'discussion-contexts').glob('*.json')))==2
