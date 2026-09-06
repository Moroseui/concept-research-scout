import json,tempfile
from pathlib import Path
import pytest
from orchestrator.hosted_cycle import select_next,encoded
from orchestrator.hosted_review_recovery import recover
from orchestrator.operations_report import Queue,finalize


def test_selection_is_closed_to_one_eligible_task():
    assert select_next('{"task_id":"eligible","reason":"synthetic"}','eligible')['task_id']=='eligible'
    for bad in ['{"task_id":"patient","reason":"no"}','{"task_id":"eligible","reason":"x","command":"sh"}','not json']:
        with pytest.raises(ValueError):select_next(bad,'eligible')


def test_interrupted_review_reconciles_without_dispatch_then_one_explicit_retry():
    with tempfile.TemporaryDirectory() as temp:
        folder=Path(temp)/'cycle';folder.mkdir();source='a'*40
        (folder/'binding.json').write_bytes(encoded({'source':source}))
        report=finalize(folder/'reports',source,'2026-09-06',[{'job_id':'synthetic','status':'COMPLETE','source':source,'kind':'synthetic'}])
        q=Queue(folder/'reports');claim=q.claim(report['id'])
        (folder/'review-claim.json').write_bytes(encoded(claim))
        (folder/'review.started.json').write_text('{}')
        (folder/'review.process-identity.json').write_text('{"process_group":123,"boot_id":"fixture"}')
        (folder/'review.input.md').write_text('Synthetic review fixture')
        with pytest.raises(ValueError,match='STILL_LIVE'):recover(folder,is_live=lambda _:True)
        assert recover(folder,is_live=lambda _:False)['model_calls']==0
        assert q.status(report['id'])['status']=='NOT_REVIEWED'
        calls=[]
        def model(*args):
            calls.append(args[1]);return 'Synthetic model fixture, not a real call.',{'actual_model':'claude-fable-5','session_id':'fixture'}
        r=recover(folder,True,model,lambda _:False)
        assert r['additional_model_calls']==2 and r['scientific_dispatches']==0
        assert calls==['review','disposition']
        assert q.status(report['id'])['status']=='REVIEWED'
        with pytest.raises(ValueError):recover(folder,True,model,lambda _:False)
        assert len(calls)==2


def test_context_carries_both_source_versions_and_all_verified_events(monkeypatch):
    from orchestrator import hosted_cycle as h
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)/'report';old=Path(temp)/'execution'
        for name in h.SOURCE_FILES:
            for base in [root,old]:
                p=base/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('synthetic fixture source\n')
        (old/'orchestrator/remote_supervisor.py').write_text('older synthetic fixture source\n')
        calls=[]
        monkeypatch.setattr(h,'checked_source',lambda r,p:calls.append((r,p)))
        packet=h.checked_packet(root,[{'source':'a'*40}],{'source':'a'*40},{},old,{'event1':{},'event2':{}})
        assert calls==[(old,'a'*40)]
        assert set(packet['verified_events'])=={'event1','event2'}
        assert packet['execution_implementation']['orchestrator/remote_supervisor.py']['identical_to_reporting'] is False
        assert 'older synthetic' in packet['execution_implementation']['orchestrator/remote_supervisor.py']['content']
        assert 'orchestrator/git_publication.py' in packet['implementation']
        assert 'orchestrator/public_export.py' in packet['implementation']
