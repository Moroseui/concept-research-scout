"""Scheduling and metadata observations must not add hidden launch authority."""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import handover_runtime as runtime
from orchestrator import protected_scientific_jobs as jobs
from orchestrator import continuing_operations as operations


def fixture(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, 'checked_source', lambda root, pin: Path(root))
    config = {'source_root': str(tmp_path), 'source': 'a'*40, 'controller_uid': runtime.os.getuid(),
              'state': str(tmp_path/'state'), 'broker_socket': str(tmp_path/'socket')}
    result = runtime.Runtime(config)
    monkeypatch.setattr(result, 'controls', lambda: [])
    return result


def test_tick_never_combines_campaign_model_work_with_formal_operation(tmp_path, monkeypatch):
    r = fixture(tmp_path, monkeypatch)
    calls = []
    monkeypatch.setattr(r.q, 'tick', lambda: {'status': 'COMPLETE', 'task': 'b'*64})
    monkeypatch.setattr(r, 'continuing_step', lambda: calls.append('operation'))
    assert r.tick()['status'] == 'COMPLETE'
    assert calls == []
    def step():
        # Coordinator does not hold branch.lock at the authority boundary.
        import fcntl
        with (r.state/'branch.lock').open('a') as gate:
            fcntl.flock(gate, fcntl.LOCK_EX|fcntl.LOCK_NB)
        calls.append('operation')
        return {'status': 'STEP_COMPLETE'}
    monkeypatch.setattr(r, 'continuing_step', step)
    monkeypatch.setattr(r.q, 'tick', lambda: runtime.Coordinator.tick(r.q))
    # This continuing-operation arbitration fixture has no disposition work.
    # The separately tested predecessor route runs before continuing_step.
    monkeypatch.setattr('orchestrator.disposition_successors.advance',
                        lambda runtime: {'status': 'NO_QUEUED_DISPOSITION_SUCCESSOR'})
    assert r.tick()['status'] == 'STEP_COMPLETE'
    assert calls == ['operation']


def test_controller_pause_blocks_formal_step_and_control_failure_blocks_every_step(tmp_path, monkeypatch):
    r = fixture(tmp_path, monkeypatch)
    r.q.db.execute('UPDATE controls SET paused=1')
    monkeypatch.setattr(r, 'continuing_step', lambda: pytest.fail('paused operation'))
    assert r.tick()['status'] == 'PAUSED'
    def bad_controls(): raise ValueError('CONTROL_TRANSPORT_UNAVAILABLE')
    monkeypatch.setattr(r, 'controls', bad_controls)
    monkeypatch.setattr(r.q, 'tick', lambda: pytest.fail('control failure'))
    assert r.tick()['status'] == 'CONTROL_TRANSPORT_BLOCKED'


def test_formal_step_requires_installed_deployment_before_effect(tmp_path, monkeypatch):
    r = fixture(tmp_path, monkeypatch)
    r.config['continuing_operations'] = {'enabled': True}
    monkeypatch.setattr(operations, 'advance', lambda r: pytest.fail('unreviewed operation'))
    def refused(): raise ValueError('CURRENT_DEPLOYMENT_REVIEW_PROOF_REQUIRED')
    monkeypatch.setattr(r, 'deployment_status', refused)
    with pytest.raises(ValueError, match='CURRENT_DEPLOYMENT_REVIEW'): r.continuing_step()


def test_new_state_is_separate_from_immutable_catalog_evidence(tmp_path, monkeypatch):
    r = fixture(tmp_path, monkeypatch)
    r.config['continuing_operations'] = {'enabled': True}
    observed = {'continuing_operations': {'completed': []}, 'scientific_completions': []}
    monkeypatch.setattr(r, 'continuing_context', lambda: observed)
    evidence = {'unchanged_approved_evidence': 'original'}
    first = r.enqueue_report('2026-09-11', [], {}, reviewer_evidence=evidence)
    original = (r.state/'tasks'/first['id']/'packet.json').read_bytes()
    packet = json.loads(original)
    assert packet['reviewer_evidence'] == evidence and packet['continuing_context'] == observed
    observed['scientific_completions'] = [{'event': 'c'*64}]
    second = r.enqueue_report('2026-09-11', [], {}, reviewer_evidence=evidence)
    assert second['id'] != first['id']
    assert (r.state/'tasks'/first['id']/'packet.json').read_bytes() == original


def test_observation_reader_never_waits_for_a_broker_and_marks_stale(tmp_path, monkeypatch):
    config = {'state': str(tmp_path), 'source': 'a'*40, 'controller_gid': 100,
              'scientific_jobs_config': '/fixed'}
    assert jobs.read_observation(config)['status'] == 'NOT_OBSERVED'
    folder = jobs.observation_directory(config); folder.mkdir(); (folder/'status.json').touch()
    value = {'schema':'scientific-observation/v1','source':'a'*40,'events':[], 'jobs':[],
             'observed_at':(datetime.now(timezone.utc)-timedelta(minutes=10)).isoformat(),
             'scientific_acceptance':False,'model_calls':0}
    monkeypatch.setattr(runtime, 'configuration', lambda *a, **k: value)
    monkeypatch.setattr(runtime, 'request_broker', lambda *a: pytest.fail('broker call'))
    assert jobs.read_observation(config)['status'] == 'STALE_OBSERVATION'
    value['source'] = 'b'*40
    with pytest.raises(ValueError, match='BINDING_CHANGED'): jobs.read_observation(config)


def test_completion_poll_checks_original_deployment_before_registry_or_mutation(tmp_path, monkeypatch):
    from orchestrator import deployment_review
    config = {'source_root': str(Path(jobs.__file__).resolve().parents[1]), 'source':'a'*40}
    monkeypatch.setattr(jobs.os, 'getuid', lambda: 0)
    monkeypatch.setattr(runtime, 'configuration', lambda path: config)
    monkeypatch.setattr(jobs.jobs, 'Registry', lambda c: pytest.fail('registry touched'))
    def refused(*a, **k): raise ValueError('ORIGINAL_CLAUDE_REVIEW_REQUIRED')
    monkeypatch.setattr(deployment_review, 'verify_installed', refused)
    with pytest.raises(ValueError, match='FIXED_ROOT_SERVICE'):
        jobs.poll_completions('/caller-selected-config')
    with pytest.raises(ValueError, match='ORIGINAL_CLAUDE_REVIEW_REQUIRED'):
        jobs.poll_completions('/etc/research-system/live-research/controller.json')


@pytest.mark.parametrize('kind',['LAUNCH_JOB',None])
def test_human_status_exposes_pending_operations_and_stale_completion(tmp_path, monkeypatch, capsys, kind):
    import sys
    r = fixture(tmp_path, monkeypatch)
    result = r.status()
    result['continuing_research'] = {'continuing_operations': {'status':'SAVED_OPERATIONS',
        'operations':[{'operation':'b'*64,'kind':kind,'status':'RECONCILIATION_REQUIRED',
                       'reason':'Original start outcome is uncertain; no retry.'}]},
        'scientific_observation':{'status':'STALE_OBSERVATION','jobs':[{'id':'saved-job-v1','status':'FAILED'}]},
        'scientific_completions':[]}
    monkeypatch.setattr(runtime, 'configuration', lambda p: r.config)
    monkeypatch.setattr(runtime.os, 'getuid', lambda: 0)
    monkeypatch.setattr(runtime, 'controller_command', lambda *a, **k: result)
    monkeypatch.setattr(sys, 'argv', ['control','--config','fixed','status','--human'])
    runtime.main()
    shown = capsys.readouterr().out
    assert 'RECONCILIATION_REQUIRED' in shown and 'stale observation' in shown
    assert 'saved-job-v1: FAILED' in shown and 'no retry' in shown


def test_current_negative_review_refuses_job_registration_before_capture(tmp_path, monkeypatch):
    from contextlib import nullcontext
    core = {'proposal_id':'saved-version-v1','protocol':{'decision_path':str(tmp_path/'proposals/saved-version-v1/workspace/protocol/round-1/decision.json')},
            'scientific_version':{'decision_path':'version/round-1/decision.json'}}
    broker=SimpleNamespace(stage_status=lambda b: None, stage_packet=lambda b: None)
    config={'state':str(tmp_path)}
    registry=SimpleNamespace(config={'proposals':str(tmp_path/'proposals')},
                             register_scientific=lambda *a, **k: pytest.fail('unreviewed capture'))
    monkeypatch.setattr(jobs.jobs,'validate_core',lambda c:None)
    monkeypatch.setattr(jobs,'admission_guard',lambda *a:nullcontext())
    def negative(*a):raise ValueError('RESEARCH_CHANGE_REQUIRES_CORRECTION')
    monkeypatch.setattr(jobs,'current_changes',negative)
    with pytest.raises(ValueError,match='REQUIRES_CORRECTION'):
        jobs.handle_registry(broker,config,registry,'register_scientific_job',
            {'core':core,'decision_path':str(tmp_path/'formal-decisions/job/round-1/decision.json')})


@pytest.mark.parametrize('mode',['investigate','code_bundle','protocol_proposal'])
def test_new_scientific_controls_refuse_missing_formal_context_before_models(tmp_path, monkeypatch, mode):
    from orchestrator import campaign_pipeline
    monkeypatch.setattr(campaign_pipeline,'system_stage',lambda *a,**k:pytest.fail('missing typed context model call'))
    monkeypatch.setattr(campaign_pipeline,'grounding',lambda *a,**k:{})
    monkeypatch.setattr('orchestrator.research_context.evidence_context',lambda *a,**k:{})
    with pytest.raises(ValueError,match='REQUIRES_TYPED_FORMAL_CONTEXT|REQUIRES_REVIEWED_PROSPECTIVE_CONTEXT'):
        campaign_pipeline.execute(SimpleNamespace(ROOT=tmp_path),mode,'P001','Synthetic fixture',tmp_path/'campaigns/isles24-pilot/pipeline/output')
