"""Finite selection over real saved workflows; model/authority fixtures only."""
import copy
import fcntl
import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from test_installed_research_request import prepared
from test_research_catalog import installed,synthetic_eligibility,ACTOR,MultiBroker,run_original
import orchestrator.handover_runtime as runtime
from orchestrator import research_catalog as catalog


@pytest.fixture(autouse=True)
def installed_controls(installed):
    # The existing fixture already provides this protected root-owned parent.
    # Its evidence filename is not a control request; exercise real empty intake.
    installed.config['control_inbox']=str(installed.parent)


def configured(installed,*identifiers):
    installed.config['research_schedule']={'task_ids':list(identifiers or ['next-discussion-v1'])}
    return runtime.Runtime(installed.config)


def test_default_disabled_does_not_submit_legacy_or_catalog(installed,monkeypatch):
    r=runtime.Runtime(installed.config)
    monkeypatch.setattr(runtime,'request_broker',lambda *args:pytest.fail('No broker call expected'))
    assert r.tick()['status']=='WAITING_FOR_ELIGIBLE_WORK'
    assert r.q.status()['tasks']==[]
    assert r.status()['research_schedule']=={'status':'DISABLED','task_ids':[]}


@pytest.mark.parametrize('setting',[{}, {'task_ids':[]}, {'task_ids':['same','same']},
    {'task_ids':['../file']},{'task_ids':['a']*33},{'task_ids':['a'],'authorize':True}])
def test_only_bounded_unique_explicit_ids_are_configuration(installed,setting):
    installed.config['research_schedule']=setting
    with pytest.raises(ValueError):runtime.Runtime(installed.config)


def test_one_shared_submission_per_tick_survives_restart_then_exhausts(installed,monkeypatch):
    monkeypatch.setattr(catalog,'verify_eligibility',synthetic_eligibility)
    other=copy.deepcopy(installed.entry);other['request']['task']['task_id']='second-discussion-v1';installed.save(other)
    r=configured(installed,'next-discussion-v1','second-discussion-v1')
    with patch.object(r.q,'tick',return_value={'status':'SYNTHETIC_QUEUE_ONLY'}):
        r.tick()
        assert len(r.q.status()['tasks'])==1
        first=r.status()['research_schedule']
        assert first['status']=='SUBMITTED' and first['requests'][1]['reason']=='ONE_SUBMISSION_PER_TICK'
        r.tick();assert len(r.q.status()['tasks'])==2
    resumed=runtime.Runtime(installed.config)
    before=[dict(row) for row in resumed.q.db.execute('SELECT * FROM research_submissions')]
    assert resumed.scheduled_research()['status']=='QUEUED'
    assert before==[dict(row) for row in resumed.q.db.execute('SELECT * FROM research_submissions')]
    item=resumed.research_inspect('next-discussion-v1')
    assert item['saved']['submitted_by']==resumed.research_service_submitter()
    assert item['request']['initiator']==installed.entry['request']['initiator']
    assert 'model' not in item['saved']['submitted_by']
    broker=MultiBroker();monkeypatch.setattr(runtime,'request_broker',broker)
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        assert resumed.tick()['status']=='COMPLETE'
        assert resumed.tick()['status']=='COMPLETE'
        assert resumed.tick()['status']=='WAITING_FOR_ELIGIBLE_WORK'
    assert resumed.status()['research_schedule']['status']=='EXHAUSTED'
    assert len([x for x in broker.calls if x[1]=='model_stage'])==6
    assert before==[dict(row) for row in resumed.q.db.execute('SELECT * FROM research_submissions')]


def test_current_pause_and_failed_control_delivery_prevent_submission(installed,monkeypatch):
    monkeypatch.setattr(catalog,'verify_eligibility',synthetic_eligibility)
    r=configured(installed)
    monkeypatch.setattr(runtime,'request_broker',lambda *args:pytest.fail('No broker call expected'))
    r.q.control({'id':'pause','action':'pause','expected_revision':0},authenticated_operator=True)
    assert r.tick()['status']=='PAUSED'
    assert r.status()['research_schedule']['status']=='PAUSED' and r.q.status()['tasks']==[]
    r.q.control({'id':'resume','action':'resume','expected_revision':1},authenticated_operator=True)
    def unavailable():raise ValueError('CONTROL_FIXTURE_UNAVAILABLE')
    monkeypatch.setattr(r,'controls',unavailable)
    assert r.tick()['status']=='CONTROL_TRANSPORT_BLOCKED'
    assert r.status()['research_schedule']['status']=='CONTROL_TRANSPORT_BLOCKED'
    assert r.q.status()['tasks']==[]


def test_blocked_predecessor_and_missing_entry_do_not_hide_independent_work(installed,monkeypatch):
    monkeypatch.setattr(catalog,'verify_eligibility',synthetic_eligibility)
    other=copy.deepcopy(installed.entry);other['request']['task']['task_id']='independent-v1';installed.save(other)
    installed.entry['predecessors']=[{'task':'0'*64,'source':'a'*40,'disposition_sha256':'1'*64,
        'requires':'APPROVED_PROPOSAL_ONLY'}];installed.save()
    r=configured(installed,'next-discussion-v1','not-installed-v1','independent-v1')
    result=r.scheduled_research()
    assert result['status']=='SUBMITTED' and len(r.q.status()['tasks'])==1
    assert result['requests'][0]['reason']=='RESEARCH_PREDECESSOR_INCOMPLETE'
    assert result['requests'][1]=={'task_id':'not-installed-v1','status':'PENDING','reason':'CATALOG_ENTRY_NOT_INSTALLED'}
    assert result['requests'][2]['status']=='QUEUED'
    assert r.research_inspect('next-discussion-v1')['saved'] is None


def test_later_negative_review_blocks_original_saved_submission_without_models(installed,monkeypatch):
    from orchestrator import change_requests as changes
    monkeypatch.setattr(catalog,'verify_eligibility',synthetic_eligibility)
    r=configured(installed);r.scheduled_research()
    first=[dict(row) for row in r.q.db.execute('SELECT * FROM research_submissions')]
    reference=installed.entry['change_request']
    folder=Path(installed.config['change_request_store'])/reference['request_id']
    changes.record(folder,'REVIEW',{**ACTOR,'family':'claude','model':'claude-fable-5'},
        {'applied_event':reference['applied_event'],'verdict':'REQUEST_CHANGES',
         'rationale':'Synthetic later criticism','review_evidence':'Synthetic fixture only',
         'affected_results':['Preserve the queued original; revalidate before affected execution.']})
    monkeypatch.setattr(runtime,'request_broker',lambda *args:pytest.fail('Criticism stops before broker admission'))
    assert r.tick()['status']=='WAITING_FOR_ELIGIBLE_WORK'
    assert r.status()['research_schedule']['status']=='BLOCKED'
    assert r.status()['research_schedule']['requests'][0]['reason']=='RESEARCH_CHANGE_REQUIRES_CORRECTION'
    assert first==[dict(row) for row in r.q.db.execute('SELECT * FROM research_submissions')]
    assert r.research_inspect('next-discussion-v1')['saved']['revalidation_required'] is True


def test_service_transport_cannot_claim_another_identity(installed,monkeypatch):
    monkeypatch.setattr(catalog,'verify_eligibility',synthetic_eligibility)
    r=configured(installed)
    forged={**r.research_service_submitter(),'model':'gpt-6-astra'}
    with pytest.raises(ValueError,match='EXACT_RESEARCH_SERVICE_TRANSPORT_REQUIRED'):
        r.submit_research('next-discussion-v1',submitted_by=forged)
    assert r.q.status()['tasks']==[]
    # Existing human/agent submissions still use exactly the same operation.
    assert r.submit_research('next-discussion-v1',submitted_by=ACTOR)['status']=='QUEUED'


def test_existing_writer_prevents_concurrent_selection(installed,monkeypatch):
    monkeypatch.setattr(catalog,'verify_eligibility',synthetic_eligibility)
    r=configured(installed)
    with (r.state/'branch.lock').open('a') as held:
        fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
        assert r.scheduled_research()['status']=='WRITER_OR_ADMISSION_BUSY'
    assert r.q.status()['tasks']==[]
    assert r.scheduled_research()['status']=='SUBMITTED'


def test_phone_status_shows_saved_pending_schedule(installed,monkeypatch,capsys):
    r=configured(installed,'not-installed-v1');r.scheduled_research()
    state=r.status()
    monkeypatch.setattr(runtime,'configuration',lambda path:installed.config)
    monkeypatch.setattr(runtime,'controller_command',lambda *args:state)
    monkeypatch.setattr(runtime.os,'getuid',lambda:0)
    monkeypatch.setattr(sys,'argv',['runtime','--config','/fixture/config','--human','status'])
    runtime.main()
    printed=capsys.readouterr().out
    assert 'Finite research schedule: pending (saved observation).' in printed
    assert 'not-installed-v1: pending' in printed and 'CATALOG_ENTRY_NOT_INSTALLED' in printed


def test_inspected_disposition_value_and_hash_use_one_original_read(installed,monkeypatch):
    r=runtime.Runtime(installed.config)
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        original,broker=run_original(r,monkeypatch)
    path=r.state/'tasks'/original['task']/'scientific-disposition.json'
    raw=path.read_bytes();observed=Path.read_bytes;reads=[]
    def read(p):
        if p==path:
            reads.append(p)
            return raw if len(reads)==1 else b'{"unexpected":"second read"}'
        return observed(p)
    monkeypatch.setattr(Path,'read_bytes',read)
    saved=r.research_inspect()['saved']
    assert len(reads)==1
    assert saved['disposition']==json.loads(raw) and saved['disposition_sha256']==hashlib.sha256(raw).hexdigest()


def test_busy_poll_preserves_last_substantive_schedule_observation(installed,monkeypatch):
    monkeypatch.setattr(catalog,'verify_eligibility',synthetic_eligibility)
    r=configured(installed)
    previous=r.scheduled_research()
    assert previous['status']=='SUBMITTED'
    with (r.state/'branch.lock').open('a') as gate:
        fcntl.flock(gate,fcntl.LOCK_EX|fcntl.LOCK_NB)
        blocked=r.scheduled_research()
        assert blocked['status']=='WRITER_OR_ADMISSION_BUSY'
        assert blocked['previous_observation_preserved'] is True
        assert r.research_schedule_status()==previous
