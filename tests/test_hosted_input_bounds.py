"""Pure composition and admission ordering; no provider or scientific assertion."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator import hosted_context as context, hosted_cycle as cycle
from orchestrator import research_task_authority as task, scientific_decision as decision

SOURCE = 'a' * 40


@pytest.fixture
def root(tmp_path, monkeypatch):
    tmp_path.chmod(0o700)
    module = tmp_path / 'orchestrator/research_task_authority.py'
    module.parent.mkdir(); module.write_text('EVIDENCE_VERSION = 2\n')
    module.with_name('hosted_context.py').write_text('"""Synthetic original-only hosted source; no outer document view."""\n')
    monkeypatch.setattr('orchestrator.remote_supervisor.checked_source', lambda root, source: Path(root))
    monkeypatch.setattr(context, 'build', lambda root, state: {'task_state': state, 'policy': 'synthetic fixed policy'})
    monkeypatch.setattr(decision.authority, 'decision_context', lambda *a, **kw: {'action': kw['action'], 'bindings': kw['bindings']})
    monkeypatch.setattr(decision.authority, 'context', lambda root: {'direction': 'synthetic delegation'})
    return tmp_path


def packet():
    return {'version': 1, 'trigger': 'installed-research-eligibility',
        'scientific_decision_artifacts': {'version': 1, 'action': 'authorize_research_task', 'experiment': 'P001', 'mode': 'discuss'},
        'reviewer_evidence': {'catalog_core': {'source': SOURCE}, 'input_evidence': {'qualification': 'Keep this unique criticism in both roles.'}},
        'recorded_changes': {'criticism': 'Unresolved original criticism is not approval.'}}


def body(root, value):
    return decision.prepare(root, action='authorize_research_task', subject='test-discussion',
        bindings={'source': SOURCE}, evidence=task.evidence_for_packet(root, value, SOURCE),
        request='Synthetic bounded discussion only.', max_rounds=1)['body']


def test_exact_v2_reconstruction_and_untrusted_literal_in_both_roles(root):
    value=packet();raw=cycle.encoded(value);reference=json.loads(task.evidence_for_packet(root,value,SOURCE)['installed-request-and-evidence.json'])
    prepared=body(root,value)
    stages=task.DecisionStages('unused',{'source':SOURCE},value)
    for row in decision.projected_bodies(prepared,1):
        final,current=context.compose_input(root,raw,stages.prompt(row['body'],row['names']),verified_source=SOURCE,
            family=row['family'],prepared_prompt=False,output_format='json')
        restored={**current['task_state'],**reference['packet_header']}
        assert cycle.encoded(restored)==raw
        assert reference['packet_sha256']==hashlib.sha256(raw).hexdigest()
        assert reference['schema']==context.REFERENCE_SCHEMA and reference['source']==SOURCE
        assert current['task_state_trust']==reference['trust']==context.TRUST
        assert 'UNTRUSTED CONTENT' in final
        assert value['recorded_changes']['criticism'] in final
        assert value['reviewer_evidence']['input_evidence']['qualification'] in final
        assert final.startswith('Return one JSON object only.')


@pytest.mark.parametrize('marker',['EVIDENCE_VERSION = 1\n','EVIDENCE_VERSION = 3\n',
    'EVIDENCE_VERSION = True\n','EVIDENCE_VERSION = int(2)\n','EVIDENCE_VERSION = 2\nEVIDENCE_VERSION = 2\n',
    'EVIDENCE_VERSION: int = 2\n',
    'EVIDENCE_VERSION, other = 2, 0\n',
    '[EVIDENCE_VERSION] = [2]\n',
    'EVIDENCE_VERSION += 2\n',
    '(EVIDENCE_VERSION := 2)\n',
    'EVIDENCE_VERSION = 2\nEVIDENCE_VERSION += 0\n',
    'EVIDENCE_VERSION = 2\n(EVIDENCE_VERSION := 2)\n',
    'EVIDENCE_VERSION = 2\nEVIDENCE_VERSION, other = 2, 0\n',
    'if True:\n    EVIDENCE_VERSION = 2\n',
    'def nested():\n    EVIDENCE_VERSION = 2\n'])
def test_source_marker_unknown_or_ambiguous_refuses(root,marker):
    (root/'orchestrator/research_task_authority.py').write_text(marker)
    with pytest.raises(ValueError,match='SOURCE_BOUND_AUTHORITY_EVIDENCE_VERSION'):
        task.evidence_for_packet(root,packet(),SOURCE)


def test_historical_exact_v1_is_selected_by_source_not_payload(root):
    value=packet();new=body(root,value)
    (root/'orchestrator/research_task_authority.py').write_text('"""Original pre-marker source."""\n')
    assert task.evidence_for_packet(root,value,SOURCE)=={'installed-request-and-evidence.json':json.dumps(value,sort_keys=True)}
    with pytest.raises(ValueError,match='SOURCE_BOUND_EVIDENCE_FORMAT_CHANGED'):
        context.compose_input(root,cycle.encoded(value),new,verified_source=SOURCE,family='codex')
    (root/'orchestrator/research_task_authority.py').write_text('EVIDENCE_VERSION = 2\n')
    old=decision.prepare(root,action='authorize_research_task',subject='test-discussion',bindings={},
        evidence={'installed-request-and-evidence.json':json.dumps(value,sort_keys=True)},request='test',max_rounds=1)['body']
    with pytest.raises(ValueError,match='SOURCE_BOUND_EVIDENCE_FORMAT_CHANGED'):
        context.compose_input(root,cycle.encoded(value),old,verified_source=SOURCE,family='codex')


def test_packet_or_reference_near_miss_refuses(root):
    value=packet();prepared=body(root,value);changed=deepcopy(value)
    changed['recorded_changes']['criticism']='Changed qualification'
    with pytest.raises(ValueError,match='SOURCE_BOUND_EVIDENCE_FORMAT_CHANGED'):
        context.compose_input(root,cycle.encoded(changed),prepared,verified_source=SOURCE,family='claude')
    with pytest.raises(ValueError,match='REFERENCE_RECONSTRUCTION'):
        context.same_prompt_reference(json.dumps(value).encode(),SOURCE)
    value['reviewer_evidence']['catalog_core']['source']='b'*40
    with pytest.raises(ValueError,match='REFERENCE_PACKET'):
        context.same_prompt_reference(cycle.encoded(value),SOURCE)


def test_final_character_measurement_and_claude_caveat():
    text='é'*1048576
    measured=context.measure_input(text,'codex','continuation')
    assert measured['characters']==1048576 and measured['utf8_bytes']==2097152
    with pytest.raises(context.InputTooLarge):context.measure_input(text+'x','codex','continuation')
    value=context.measure_input('x','claude','review')
    assert value['limit_characters']==900000 and not value['provider_limit_verified']
    assert value['limit_basis']=='UNVERIFIED_CLAUDE_CONSERVATIVE_LOCAL_BOUND'


def test_generic_round_two_growth_and_finite_hosted_refusal(root):
    rows=decision.projected_bodies('B',2)
    assert [(r['round'],r['family']) for r in rows]==[(1,'codex'),(1,'claude'),(2,'codex'),(2,'claude')]
    assert len(rows[2]['body'])>=len(rows[0]['body'])+60000
    assert len(rows[3]['body'])>=len(rows[2]['body'])+30000
    with pytest.raises(ValueError,match='FINITE_HOSTED_SCIENTIFIC_DECISION_ROUND'):
        task.DecisionStages('unused',{'source':SOURCE},packet()).preflight_bodies(root,'body',2)


def test_author_fits_but_review_refuses_before_admission_or_attempt(root,monkeypatch):
    monkeypatch.setattr(context,'build',lambda root,state:{'task_state':state,'fixed_policy':'x'*898000})
    value=packet();bindings={'source':SOURCE};output=root/'authority'
    monkeypatch.setattr(task,'_identity',lambda *args:(root,'test-discussion',bindings))
    monkeypatch.setattr(task,'_packet',lambda *args:value)
    monkeypatch.setattr(task,'_turn_guard',lambda *args,**kwargs:pytest.fail('admission guard entered before both-role preflight'))
    config={'controller_uid':os.getuid(),'broker_socket':'unused','source':SOURCE,'source_root':str(root)}
    with pytest.raises(context.InputTooLarge) as found:
        task.execute(config,{'source':SOURCE,'request':{'task':{}}},output,client=lambda *a:pytest.fail('broker called'))
    assert found.value.measurement['family']=='claude'
    failure=json.loads((root/'authority.input-preflight-failure.json').read_text())
    assert failure['admissions']==failure['provider_calls']==0 and not failure['automatic_retry']
    assert not output.exists()
    with pytest.raises(ValueError,match='PREFLIGHT_REFUSAL_REQUIRES_RECONCILIATION'):
        task.execute(config,{'source':SOURCE},output,client=lambda *a:pytest.fail('broker called'))


@pytest.mark.parametrize('characters',[1048577,1500001])
def test_final_dispatch_refuses_before_worker_or_provider(root,monkeypatch,characters):
    folder=root/'turn';folder.mkdir(mode=0o700)
    monkeypatch.setattr(cycle.subprocess,'check_output',lambda *a,**kw:SOURCE)
    monkeypatch.setattr(cycle,'checked_source',lambda *a:root)
    monkeypatch.setattr(context,'envelope',lambda *a,**kw:('x'*characters,{}))
    monkeypatch.setattr(cycle.pwd,'getpwnam',lambda *a:pytest.fail('worker preparation happened'))
    monkeypatch.setattr(cycle.subprocess,'Popen',lambda *a,**kw:pytest.fail('provider launched'))
    with pytest.raises(context.InputTooLarge):cycle.model_call(folder,'continuation','astra','original')
    assert (folder/'continuation.input.md').exists() == (characters<1500000)
    assert (folder/'continuation.input-preflight-failure.json').exists()
    assert not (folder/'continuation.started.json').exists()


def test_formal_finite_preflight_precedes_admission(root,monkeypatch):
    from orchestrator import formal_decisions as formal
    config={'controller_uid':os.getuid(),'state':str(root),'source_root':str(root),'broker_socket':'unused'}
    output=root/'formal-decisions'/'fixed-test'
    request={'source':SOURCE,'action':'authorize_protocol','subject':'test','bindings':{},'evidence':{'test':'synthetic'},'request':'test','transition':{'from':'PROPOSED','to':'ELIGIBLE'}}
    monkeypatch.setattr(formal,'checked_request',lambda value:value)
    monkeypatch.setattr(formal,'scientific_root',lambda *args:root)
    monkeypatch.setattr(formal,'_application_request',lambda *args:None)
    monkeypatch.setattr(formal,'_packet',lambda *args:{'trigger':'registered-formal-scientific-decision',
        'formal_request':request,'reviewer_evidence':{'test':'synthetic'},
        'scientific_decision_artifacts':{'version':3,'action':request['action'],
            'subject':request['subject'],'bindings_sha256':formal.digest(request['bindings'])}})
    monkeypatch.setattr(formal,'event',lambda value:{'source':SOURCE})
    monkeypatch.setattr(context,'build',lambda root,state:{'task_state':state,'policy':'x'*1100000})
    monkeypatch.setattr(formal,'_turn_guard',lambda *args,**kwargs:pytest.fail('formal admission entered'))
    with pytest.raises(context.InputTooLarge):formal.execute_formal_decision(config,request,output,client=lambda *a:pytest.fail('provider called'))
    assert output.with_name(output.name+'.input-preflight-failure.json').exists()
    assert not output.exists()
