import tempfile
from pathlib import Path
import pytest
from orchestrator.hosted_cycle_reconcile import reconcile,read_checked


def test_missing_completion_cannot_consume_wake():
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp);(root/'event').mkdir()
        with pytest.raises(ValueError):reconcile(root,root,'event')
        assert not (root/'jobs.sqlite').exists()


def test_evidence_symlink_and_path_traversal_refuse():
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp);(root/'file').write_text('synthetic')
        (root/'link').symlink_to(root/'file')
        with pytest.raises(ValueError):read_checked(root/'link')
        with pytest.raises(ValueError):reconcile(root,root,'../escape')


def test_completed_fixture_reconciles_once_and_tamper_refuses():
    import json,hashlib
    from orchestrator.hosted_cycle import encoded
    from orchestrator.remote_supervisor import Controller
    from orchestrator.operations_report import Queue,finalize
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp);state=root/'state';state.mkdir();dest=root/'cycles';dest.mkdir();folder=dest/'event';folder.mkdir()
        source='a'*40;event={'synthetic_fixture':True}
        controller=Controller(state/'jobs.sqlite')
        controller.db.execute('INSERT INTO events VALUES(?,?,?)',('event','job',json.dumps(event)))
        controller.db.execute('INSERT INTO wakes VALUES(?,?,?,?)',('event','job','PENDING_AUTH','AUTH'))
        binding={'source':source,'event':'event','event_sha256':hashlib.sha256(encoded(event)).hexdigest()}
        (folder/'binding.json').write_bytes(encoded(binding))
        for stage,model in [('continuation','gpt-6-astra'),('review','claude-fable-5'),('disposition','gpt-6-astra')]:
            receipt={'stage':stage,'returncode':0,'requested_model':model,'actual_model':model}
            for suffix,key in [('stdout','stdout_sha256'),('stderr','stderr_sha256'),('input.md','input_sha256'),('md','answer_sha256')]:
                raw=b'Synthetic fixture, not a real model execution.'
                (folder/(stage+'.'+suffix)).write_bytes(raw);receipt[key]=hashlib.sha256(raw).hexdigest()
            (folder/(stage+'.receipt.json')).write_bytes(encoded(receipt))
        report=finalize(folder/'reports',source,'2026-09-06',[{'job_id':'fixture','status':'COMPLETE','source':source,'kind':'synthetic'}])
        q=Queue(folder/'reports');claim=q.claim(report['id']);review=(folder/'review.md').read_text()
        q.attach(report['id'],claim['attempt_id'],review,{'family':'claude','model':'claude-fable-5','source':source,'report_sha256':report['id'],'review_sha256':hashlib.sha256(review.encode()).hexdigest(),'execution_receipt_sha256':'b'*64,'session_id':'fixture','status':'COMPLETE'})
        q.disposition(report['id'],(folder/'disposition.md').read_text())
        (folder/'complete.json').write_bytes(encoded({**binding,'status':'COMPLETE','real_model_calls':3,'report':report['id']}))
        assert reconcile(state,dest,'event')['duplicate'] is False
        assert reconcile(state,dest,'event')['duplicate'] is True
        (folder/'review.md').write_text('tampered')
        with pytest.raises(ValueError,match='EVIDENCE_CHANGED'):reconcile(state,dest,'event')
