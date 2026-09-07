"""Human controls and report recovery use the same persistent runtime interface."""
import json
from pathlib import Path
from orchestrator.handover_runtime import Runtime
from orchestrator.handover_coordinator import Coordinator,encoded,digest


def runtime(tmp_path,monkeypatch):
    import orchestrator.handover_runtime as module
    monkeypatch.setattr(module,'checked_source',lambda root,pin:Path(root))
    config={'source_root':str(tmp_path),'source':'a'*40,'controller_uid':module.os.getuid(),
            'state':str(tmp_path/'state'),'broker_socket':str(tmp_path/'socket')}
    return Runtime(config)


def test_report_identity_stable_after_review_queue_mutates(tmp_path,monkeypatch):
    from orchestrator.operations_report import Queue
    r=runtime(tmp_path,monkeypatch)
    first=r.enqueue_report('2026-09-06',[],{'waiting':'operator'})
    report=json.loads((r.state/'tasks'/first['id']/'report.json').read_text())
    Queue(r.state/'reports').claim(report['id'])
    second=r.enqueue_report('2026-09-06',[],{'waiting':'operator'})
    assert first==second


def test_recovery_uses_status_operation_only(tmp_path,monkeypatch):
    import orchestrator.handover_runtime as module
    r=runtime(tmp_path,monkeypatch);binding=r.enqueue_report('2026-09-06',[],{})
    r.q.submit(binding)
    r.q.db.execute("INSERT INTO stages VALUES(?,0,'STARTED',NULL)",(binding['id'],))
    r.q.db.execute("UPDATE tasks SET status='BLOCKED'")
    calls=[]
    def retrieve(path,operation,body):
        calls.append(operation)
        return {'status':'UNCERTAIN_MODEL_RECONCILE_NO_RETRY'}
    monkeypatch.setattr(module,'request_broker',retrieve)
    r.recover()
    assert calls==['stage_status']
    assert r.q.status()['tasks'][0]['status']=='BLOCKED'
