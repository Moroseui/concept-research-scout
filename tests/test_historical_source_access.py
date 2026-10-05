"""Retirement narrows execution without destroying original evidence access."""
from copy import deepcopy
import hashlib
import json

import pytest

from orchestrator import install_reviewed_deployment as install
from orchestrator.hosted_cycle import encoded
from orchestrator.protected_handover import Broker
from test_protected_handover import broker
from test_server_admission import server
from test_terminal_review import evidence, accounting_fixture, validate_accounting


def saved_stage(b, event):
    from pathlib import Path
    folder = Path(b.config['turn_root'])/(event['turn_id']+'-'+event['attempt'])
    folder.mkdir(parents=True)
    packet = encoded({'version': 1, 'original': event['source']})
    (folder/'packet.json').write_bytes(packet)
    (folder/'binding.json').write_bytes(encoded({'event': event,
        'packet_sha256': hashlib.sha256(packet).hexdigest()}))
    receipt = {}
    for suffix, key in [('.stdout','stdout_sha256'),('.stderr','stderr_sha256'),
            ('.input.md','input_sha256'),('.md','answer_sha256'),
            ('.operating-context.json','operating_context_sha256')]:
        raw = ('original '+suffix).encode()
        (folder/('review'+suffix)).write_bytes(raw)
        receipt[key] = hashlib.sha256(raw).hexdigest()
    (folder/'review.receipt.json').write_bytes(encoded(receipt))
    return folder


def test_many_releases_keep_original_reads_without_growing_execution_list(tmp_path,monkeypatch):
    b = broker(tmp_path)
    b.config['policy']['n'] = 48
    events = []
    for i in range(1, 34):
        source = format(i, '040x')
        install.source_transition(b.config['sources'], [source], source)
        b.config['sources'] = [source]
        event = {**server(i), 'source': source}
        assert b.handle({'operation':'admit_server','body':event},10001)['status'] == 'ADMITTED'
        saved_stage(b,event)
        events.append(event)
    before = b.ledger.read()
    for event in events:
        assert b.stage_packet({'event':event})['packet']['original'] == event['source']
        assert b.stage_status({'event':event,'stage':'review'})['answer'] == 'original .md'
    assert b.ledger.read() == before
    assert len(b.config['sources']) == 1
    from types import SimpleNamespace
    from orchestrator import protected_handover as ph
    monkeypatch.setattr(ph,'os',SimpleNamespace(getuid=lambda:0))
    b.config['model_mode'] = 'SUPERVISED'
    # Repeated reads cannot become permission for an old new call or replay.
    for event in events[:-1]:
        with pytest.raises(ValueError,match='REVIEWED_SOURCE_REQUIRED'):
            b.handle({'operation':'admit_server','body':event},10001)
        with pytest.raises(ValueError,match='MODEL_STAGE_SOURCE'):
            b.model_stage({'event':event,'stage':'review','packet':{},'prompt':'No model.'})
        artifact = {'repository_id':1323461276,'run_id':'1','attempt':'1',
            'source':event['source'],'branch':event['branch'],'workflow_sha256':'a'*64}
        with pytest.raises(ValueError,match='ACTIONS_SOURCE_REFUSED'):
            b.actions_admission(artifact,artifact)
    assert b.ledger.read() == before


@pytest.mark.parametrize('mutation',['source','kind','turn_id','attempt','missing','changed-output','changed-binding'])
def test_retired_reads_authenticate_exact_admission_and_originals(tmp_path,mutation):
    b = broker(tmp_path);event = server(1)
    b.handle({'operation':'admit_server','body':event},10001)
    folder = saved_stage(b,event);b.config['sources'] = ['c'*40]
    if mutation == 'source': event = {**event,'source':'d'*40}
    elif mutation == 'kind': event = {**event,'kind':'nightly_review'}
    elif mutation == 'turn_id': event = {**event,'turn_id':'f'*64}
    elif mutation == 'attempt': event = {**event,'attempt':'2'}
    elif mutation == 'missing': (folder/'review.receipt.json').unlink()
    elif mutation == 'changed-output': (folder/'review.md').write_bytes(b'altered')
    elif mutation == 'changed-binding':
        value = json.loads((folder/'binding.json').read_bytes())
        value['event']['source'] = 'd'*40
        (folder/'binding.json').write_bytes(encoded(value))
    if mutation == 'missing':
        assert b.stage_status({'event':event,'stage':'review'})['status'] == 'NOT_STARTED_RECONCILIATION_REQUIRED'
    else:
        with pytest.raises(ValueError,match='HISTORICAL_ADMISSION_REQUIRED|RECEIPT_CHANGED|BINDING_CHANGED'):
            b.stage_status({'event':event,'stage':'review'})


def test_halt_does_not_erase_retired_evidence_or_reset_accounting(tmp_path):
    b = broker(tmp_path)
    for i in range(1,5):
        b.handle({'operation':'admit_server','body':server(i)},10001)
    event = server(1);saved_stage(b,event);b.config['sources'] = ['c'*40]
    before = b.ledger.read();assert before[1]['halted']
    assert b.stage_status({'event':event,'stage':'review'})['status'] == 'COMPLETE'
    assert b.ledger.read() == before


def test_execution_bound_and_new_source_requirement_remain(tmp_path):
    b = broker(tmp_path);pins = [format(i,'040x') for i in range(1,18)]
    with pytest.raises(ValueError,match='BOUNDED_EXECUTION_SOURCES'):
        install.source_transition(b.config['sources'],pins,pins[-1])
    with pytest.raises(ValueError,match='CURRENT_EXECUTION_SOURCE'):
        install.source_transition(b.config['sources'],pins[:16],pins[-1])
    with pytest.raises(ValueError,match='BOUNDED_REVIEWED_SOURCES'):
        Broker({**b.config,'sources':pins})


def test_job_controller_cannot_use_a_retired_source(tmp_path,monkeypatch):
    from orchestrator import protected_scientific_jobs as jobs
    b = broker(tmp_path)
    b.config['research_controller_config'] = '/synthetic/controller.json'
    monkeypatch.setattr('orchestrator.handover_runtime.configuration',lambda path:{
        'controller_uid':b.config['controller_uid'],'source':'c'*40})
    with pytest.raises(ValueError,match='SCIENTIFIC_JOB_CONTROLLER_BINDING_CHANGED'):
        jobs.controller_configuration(b)


def test_retired_accounting_keeps_exact_original_charge_and_rejects_forgery(evidence):
    f = accounting_fixture(evidence)
    f.allowed_sources = {'b'*40}  # Original charge used source a; it is retired.
    before = deepcopy(f.store.commits)
    assert validate_accounting(f) == validate_accounting(f)
    assert f.store.commits == before
    f.account['cases'][0]['event']['source'] = 'c'*40
    with pytest.raises(ValueError,match='ORIGINAL_TRANSITION_CHANGED'):
        validate_accounting(f)
