"""Exact reviewed install inputs and recovery gates; no host/service mutations."""
import copy
import importlib.util
import json
from pathlib import Path
import runpy
import sqlite3

import pytest


def module():
    path=Path(__file__).parents[1]/'deploy/research-system/install_live_research.py'
    spec=importlib.util.spec_from_file_location('live_research_installer_test',path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


def review_inputs(m):
    source='c'*40; inputs={name:b'reviewed source fixture\n' for name in m.REQUIRED_SOURCE}
    hashes={name:m.digest(raw) for name,raw in inputs.items()}
    request=m.encoded({'scope':'human-controls','reviewed_commit':source,'input_file_sha256':hashes})
    response=m.encoded({'subtype':'success','is_error':False,'structured_output':{
        'scope':'human-controls','reviewed_commit':source,'verdict':'APPROVE','findings':[]}})
    execution=m.encoded({'reviewed_commit':source,'returncode':0,'response_sha256':m.digest(response),
        'request_sha256':m.digest(request),'requested_model':'claude-fable-5',
        'assistant_message_models':['claude-fable-5'],'input_file_sha256':hashes})
    proposal=b'{}\n'; evidence=b'{"fixture":true}\n'
    manifest={'source':source,'archive_sha256':'a'*64,'proposal_sha256':m.digest(proposal),
        'evidence_sha256':m.digest(evidence),'source_review_request_sha256':m.digest(request),
        'source_review_sha256':m.digest(response),'source_review_execution_sha256':m.digest(execution),
        'source_input_sha256':hashes,'before_sha256':{name:'d'*64 for name in m.BASELINE},
        'ledger_pin':'e'*40,'ledger_state_sha256':'f'*64,'fixture_link':'/opt/research-system/original/snapshot'}
    manifest['before_sha256'].update(m.CONFIG_HASHES)
    return manifest,source,proposal,evidence,request,response,execution,inputs


def test_completed_exact_review_is_required_and_original_bytes_bound():
    m=module();args=review_inputs(m);m.checked_manifest(*args)
    for index,replacement in [(1,'a'*40),(2,b'changed proposal'),(3,b'changed evidence'),
                              (4,b'changed request'),(5,b'changed review')]:
        changed=list(copy.deepcopy(args));changed[index]=replacement
        with pytest.raises(ValueError):m.checked_manifest(*changed)
    changed=list(copy.deepcopy(args));changed[-1][next(iter(m.REQUIRED_SOURCE))]=b'new source'
    with pytest.raises(ValueError,match='SOURCE_BYTES_CHANGED'):m.checked_manifest(*changed)


@pytest.mark.parametrize('field,value', [('verdict','REQUEST_CHANGES'),('scope','remote-handoff-direction'),
                                       ('reviewed_commit','a'*40)])
def test_relabeling_or_critical_review_never_becomes_install_approval(field,value):
    m=module();args=list(review_inputs(m));response=json.loads(args[5]);response['structured_output'][field]=value
    args[5]=m.encoded(response);args[0]['source_review_sha256']=m.digest(args[5])
    execution=json.loads(args[6]);execution['response_sha256']=m.digest(args[5]);args[6]=m.encoded(execution)
    args[0]['source_review_execution_sha256']=m.digest(args[6])
    with pytest.raises(ValueError,match='COMPLETED_EXACT_SOURCE_REVIEW_REQUIRED'):m.checked_manifest(*args)


def test_generated_plan_cannot_change_bound_limits_inputs_or_credential_paths(tmp_path):
    m=module()
    fixtures=runpy.run_path(str(Path(__file__).with_name('test_live_research_preparation.py')))
    live,controller,request=fixtures['inputs']();prepare=fixtures['module']()
    evidence=b'{"fixture":true}\n';request['evidence_sha256']=m.digest(evidence)
    proposal=prepare.prepare('c'*40,live,controller,request,tmp_path/'proposal')
    files={name:(tmp_path/'proposal'/name).read_bytes() for name in proposal['file_sha256']}
    originals={'live_config':m.encoded(live),'fixture_controller_config':m.encoded(controller)}
    m.checked_proposal('c'*40,proposal,files,originals,evidence,prepare)
    for key,value in [('max_model_turns',2),('writer_config','/tmp/new-credential')]:
        changed=copy.deepcopy(files);broker=json.loads(changed['broker.json']);broker[key]=value
        changed['broker.json']=m.encoded(broker)
        with pytest.raises(ValueError,match='GENERATED_CONFIGURATION_CHANGED'):
            m.checked_proposal('c'*40,proposal,changed,originals,evidence,prepare)
    with pytest.raises(ValueError,match='PROPOSAL_INPUT_BINDING_CHANGED'):
        m.checked_proposal('c'*40,proposal,files,originals,b'other evidence',prepare)


def test_partial_and_duplicate_install_use_original_receipts():
    m=module();manifest=review_inputs(m)[0]
    assert m.recovery_state(None,None,manifest)=='FRESH'
    intent={'source':manifest['source'],'review_manifest_sha256':'9'*64}
    with pytest.raises(ValueError,match='PARTIAL_INSTALL_PRESERVED_RECONCILE'):
        m.recovery_state(intent,None,manifest)
    receipt={**intent,'original_sha256':manifest['before_sha256'],
        'status':'LIVE_RESEARCH_INSTALLED_BROKER_READY_TASK_NOT_SUBMITTED','models_started':0,
        'controller_started':False,'timer_enabled':False,'credentials_modified':False,'unattended_activated':False}
    assert m.recovery_state(intent,receipt,manifest)=='COMPLETE'
    with pytest.raises(ValueError,match='PARTIAL_INSTALL_PRESERVED_RECONCILE'):
        m.recovery_state(None,receipt,manifest)
    with pytest.raises(ValueError,match='ORIGINAL_INSTALL_RECEIPT_CHANGED'):
        m.recovery_state(intent,{**receipt,'review_manifest_sha256':'8'*64},manifest)


def test_pending_running_or_failed_saved_tasks_block_install_without_rewriting_database(tmp_path):
    m=module();db=tmp_path/'coordinator.sqlite'
    with sqlite3.connect(db) as connection:
        connection.execute('CREATE TABLE tasks(id TEXT PRIMARY KEY,status TEXT)')
        connection.execute("INSERT INTO tasks VALUES('old','COMPLETE')")
    original=db.read_bytes();m.completed_tasks(db);assert db.read_bytes()==original
    for status in ('QUEUED','RUNNING','BLOCKED','FAILED'):
        with sqlite3.connect(db) as connection:
            connection.execute('UPDATE tasks SET status=?',(status,))
        original=db.read_bytes()
        with pytest.raises(ValueError,match='EXISTING_COORDINATOR_WORK_RECONCILE'):m.completed_tasks(db)
        assert db.read_bytes()==original


def test_actual_review_request_includes_every_literal_proposal_config_unit_and_evidence():
    m=module();proposal=b'proposal';evidence=b'evidence'
    files={name:name.encode() for name in ('broker.json','controller.json',m.LIVE,m.CONTROLLER,
                                         'research-system-live-control.sh')}
    all_inputs={'proposal':proposal,'evidence':evidence,**files}
    observed={'private/'+name:m.digest(raw) for name,raw in all_inputs.items()}
    request=m.encoded({'private_evidence_sha256':observed})
    m.reviewed_private_inputs(request,proposal,evidence,files)
    for name in all_inputs:
        missing=dict(observed);missing.pop('private/'+name)
        with pytest.raises(ValueError,match='ACTUAL_REVIEW_PRIVATE_INPUT_MISSING'):
            m.reviewed_private_inputs(m.encoded({'private_evidence_sha256':missing}),proposal,evidence,files)
    # Updating proposed bytes and a root manifest cannot make them reviewed.
    changed={**files,'broker.json':b'changed unit/configuration'}
    with pytest.raises(ValueError,match='ACTUAL_REVIEW_PRIVATE_INPUT_MISSING'):
        m.reviewed_private_inputs(request,proposal,evidence,changed)
    with pytest.raises(ValueError,match='ACTUAL_PRIVATE_REVIEW_INPUTS_REQUIRED'):
        m.reviewed_private_inputs(b'{}',proposal,evidence,files)
