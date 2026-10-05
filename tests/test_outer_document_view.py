"""Exact outer-view tests; campaign constructor seam is independently tested."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import pytest
from orchestrator import hosted_context as h, hosted_cycle as hc, hosted_campaign as campaign
from orchestrator import scientific_decision as decision, research_task_authority as rta

SOURCE = 'a'*40
REMOTE = h.OUTER_DOCUMENT_NAME
TEXT = 'Synthetic approved operating direction. Preserve original criticism.\n'*280
SHA = hashlib.sha256(TEXT.encode()).hexdigest()
POLICY = {'binding': {'path': 'synthetic-policy.json', 'sha256': 'b'*64},
    'policy': {'version': 'synthetic-policy'}, 'direction': 'Synthetic policy; no new grant.',
    'operating_context': {'manifest': {'roles': {'codex': 'Synthetic author', 'claude': 'Synthetic reviewer'}},
        'documents': {REMOTE: {'sha256': SHA, 'text': TEXT}}}}

def context():
    return {'documents': {REMOTE: {'sha256': SHA, 'disposition': h.DOCUMENTS[REMOTE], 'content': TEXT},
        'literal-unmatched': {'content': 'Keep every distinct original qualification.'}},
        'shared_policy': deepcopy(POLICY), 'verified_source_commit': SOURCE,
        'task_state': {'trigger': 'installed-research-request', 'jobs': {'synthetic': 'read-only'}}}

@pytest.fixture
def root(tmp_path, monkeypatch):
    tmp_path.chmod(0o700); folder=tmp_path/'orchestrator'; folder.mkdir()
    (folder/'hosted_context.py').write_text('OUTER_DOCUMENT_VIEW_VERSION = 1\n')
    (folder/'research_task_authority.py').write_text('EVIDENCE_VERSION = 2\nHOSTED_PRESENTATION_VERSION = 1\n')
    def checked(path, source):
        if source != SOURCE or Path(path) != tmp_path: raise ValueError('SYNTHETIC_EXACT_SOURCE_REQUIRED')
        return tmp_path
    monkeypatch.setattr('orchestrator.remote_supervisor.checked_source', checked)
    monkeypatch.setattr(h, 'shared_policy', lambda root: deepcopy(POLICY))
    monkeypatch.setattr(h, 'build', lambda root, state: {**context(), 'task_state': deepcopy(state)})
    monkeypatch.setattr(decision.authority, 'context', lambda root: deepcopy(POLICY))
    monkeypatch.setattr(decision.authority, 'decision_context', lambda root, **v: {'action':v['action'], 'subject':v['subject'], 'bindings':v['bindings']})
    # This suite owns the fixed outer view. Actual typed grounding is tested by its owner.
    monkeypatch.setattr(campaign, 'grounding_presentation', lambda root, packet, current, prompt, source, **k: prompt, raising=False)
    return tmp_path

def packet(trigger='installed-research-request'):
    if trigger=='installed-research-eligibility':
        return {'version':1, 'trigger':trigger,
            'scientific_decision_artifacts': {'version':1, 'action':rta.ACTION, 'experiment':'P001', 'mode':'discuss'},
            'reviewer_evidence': {'catalog_core': {'source':SOURCE}, 'input_evidence': {'original':'Keep distinct evidence.'}},
            'recorded_changes': {'criticism':'Unresolved original criticism, no approval assertion.'}}
    return {'trigger':trigger, 'jobs':{'synthetic':'No model or execution.'}}

def prompt(root, value):
    if value['trigger']!='installed-research-eligibility': return 'Synthetic exact campaign body.'
    return decision.prepare(root, action=rta.ACTION, subject='synthetic-discussion', bindings={'source':SOURCE},
        evidence=rta.evidence_for_packet(root,value,SOURCE), request='Synthetic bounded discussion.', max_rounds=1,
        hosted_policy_source=SOURCE)['body']

def decode(final):
    marker='CURRENT APPROVED OPERATING POLICY AND BOUND CONTEXT ('+h.TRUST+'):\n'
    return json.JSONDecoder().raw_decode(final.split(marker,1)[1])[0]

@pytest.mark.parametrize('trigger',['installed-research-eligibility','installed-research-request','verified-completion'])
@pytest.mark.parametrize('family',['codex','claude'])
def test_both_roles_routes_keep_original_context_and_one_terminal_literal(root,trigger,family):
    value=packet(trigger);body=prompt(root,value);before=hc.encoded(value)
    final,current=h.compose_input(root,before,body,verified_source=SOURCE,family=family)
    shown=decode(final);prior=h.authority_presentation(root,value,current,body,SOURCE)
    restored=h.reconstruct_outer_document(shown,prior,current,SOURCE)
    assert hc.encoded(restored)==hc.encoded(prior)
    assert shown['shared_policy']==current['shared_policy']==POLICY
    assert shown['documents'][REMOTE]['disposition']==h.DOCUMENTS[REMOTE]
    assert shown['documents'][REMOTE]['sha256']==SHA
    ref=shown['documents'][REMOTE]['content']
    assert ref['literal_location']==h.OUTER_DOCUMENT_LOCATION and ref['bytes']==len(TEXT.encode())
    assert final.count(json.dumps(TEXT))==1
    assert current['documents'][REMOTE]['content']==TEXT and h.OUTER_DOCUMENT_META not in current
    assert shown[h.OUTER_DOCUMENT_META]['original_context_sha256']==hashlib.sha256(hc.encoded(current)).hexdigest()
    assert value==json.loads(before) and 'distinct' in final.lower()

@pytest.mark.parametrize('field,value',[('schema','other'),('source','b'*40),('name','other.md'),
    ('literal_location','operating_context.task_state.reviewer_evidence'),('sha256','c'*64),('bytes',True),
    ('bytes',len(TEXT.encode())+1),('trust','Authority grant'),('unexpected','extra')])
def test_reference_near_misses_refuse_without_general_resolution(root,field,value):
    original=context();shown=h.outer_document_presentation(root,original,original,packet(),SOURCE)
    shown['documents'][REMOTE]['content'][field]=value
    with pytest.raises(ValueError,match='OUTER_DOCUMENT_REFERENCE_CHANGED'):
        h.reconstruct_outer_document(shown,original,original,SOURCE)
    assert original['documents'][REMOTE]['content']==TEXT

@pytest.mark.parametrize('change',['missing-target','different-target','target-reference','outer-reference','outer-disposition','outer-hash','target-hash','extra-target-field'])
def test_nonliteral_or_changed_targets_are_not_repaired_or_aliased(root,change):
    value=context();target=value['shared_policy']['operating_context']['documents'][REMOTE]
    if change=='missing-target':del value['shared_policy']['operating_context']['documents'][REMOTE]
    if change=='different-target':target['text']+='changed'
    if change=='target-reference':target['text']={'schema':h.OUTER_DOCUMENT_SCHEMA}
    if change=='outer-reference':value['documents'][REMOTE]['content']={'schema':h.OUTER_DOCUMENT_SCHEMA}
    if change=='outer-disposition':value['documents'][REMOTE]['disposition']='NEW_GRANT'
    if change=='outer-hash':value['documents'][REMOTE]['sha256']='c'*64
    if change=='target-hash':target['sha256']='c'*64
    if change=='extra-target-field':target['ref']='other'
    with pytest.raises(ValueError,match='OUTER_DOCUMENT'):
        h.outer_document_presentation(root,value,value,packet(),SOURCE)

@pytest.mark.parametrize('definition',['OUTER_DOCUMENT_VIEW_VERSION = 2','OUTER_DOCUMENT_VIEW_VERSION = True',
    'OUTER_DOCUMENT_VIEW_VERSION = int(1)','OUTER_DOCUMENT_VIEW_VERSION: int = 1',
    'OUTER_DOCUMENT_VIEW_VERSION = 1\nOUTER_DOCUMENT_VIEW_VERSION = 1',
    'OUTER_DOCUMENT_VIEW_VERSION = 1\ndel OUTER_DOCUMENT_VIEW_VERSION',
    'OUTER_DOCUMENT_VIEW_VERSION, other = 1, 0','(OUTER_DOCUMENT_VIEW_VERSION := 1)',
    'if True:\n    OUTER_DOCUMENT_VIEW_VERSION = 1','def nested():\n    OUTER_DOCUMENT_VIEW_VERSION = 1'])
def test_profile_is_one_literal_in_checked_source_not_loaded_module(root,definition):
    (root/'orchestrator/hosted_context.py').write_text(definition+'\n')
    with pytest.raises(ValueError,match='SOURCE_BOUND_OUTER_DOCUMENT_VERSION'):
        h.outer_document_profile(root,SOURCE)


def test_historical_source_without_marker_is_exact_noop_and_missing_file_refuses(root):
    file=root/'orchestrator/hosted_context.py';file.write_text('"""Historical exact source."""\n')
    original=context();before=hc.encoded(original)
    assert h.outer_document_profile(root,SOURCE)==0
    assert h.outer_document_presentation(root,original,original,packet(),SOURCE) is original
    assert hc.encoded(original)==before
    file.unlink()
    with pytest.raises((ValueError,FileNotFoundError)):h.outer_document_profile(root,SOURCE)


def test_wrong_source_context_and_double_layer_refuse(root):
    original=context()
    with pytest.raises(ValueError,match='EXACT_SOURCE'):h.outer_document_presentation(root,original,original,packet(),'b'*40)
    view=h.outer_document_presentation(root,original,original,packet(),SOURCE)
    with pytest.raises(ValueError,match='ORIGINAL_CONTEXT_CHANGED'):h.outer_document_presentation(root,view,original,packet(),SOURCE)
    view=deepcopy(view)
    view['documents']['literal-unmatched']['content']='Dropped criticism'
    with pytest.raises(ValueError,match='RECONSTRUCTION_CHANGED'):h.reconstruct_outer_document(view,original,original,SOURCE)


def test_linked_disposition_and_other_triggers_keep_original_view(root):
    for trigger in ['linked-campaign-disposition','unrelated']:
        original=context();assert h.outer_document_presentation(root,original,original,packet(trigger),SOURCE) is original


def test_dispatch_envelope_and_recovery_recomposition_preserve_full_receipt_hash(root):
    value=packet();body=prompt(root,value);folder=root/'turn';folder.mkdir(mode=0o700);(folder/'packet.json').write_bytes(hc.encoded(value))
    expected,original=h.compose_input(root,hc.encoded(value),body,verified_source=SOURCE,family='claude')
    dispatched,recovered=h.envelope(root,folder,body,verified_source=SOURCE,family='claude')
    assert h.format_prefix(dispatched,prepared_prompt=False,output_format='markdown')==expected
    assert hc.encoded(recovered)==hc.encoded(original)
    again,again_original=h.compose_input(root,hc.encoded(value),body,verified_source=SOURCE,family='claude')
    assert hashlib.sha256(again.encode()).hexdigest()==hashlib.sha256(expected.encode()).hexdigest()
    assert hashlib.sha256(hc.encoded(again_original)).hexdigest()==hashlib.sha256(hc.encoded(original)).hexdigest()


def test_outer_inverse_precedes_prefix_and_unchanged_v2_reconstruction(root):
    from test_disposition_context import packet as prefix_packet
    from orchestrator import disposition_context as dc
    value=prefix_packet();body=prompt(root,value);raw=hc.encoded(value)
    final,current=h.compose_input(root,raw,body,verified_source=SOURCE,family='claude')
    prior=h.authority_presentation(root,value,current,body,SOURCE)
    restored_outer=h.reconstruct_outer_document(decode(final),prior,current,SOURCE)
    ref=h.same_prompt_reference(raw,SOURCE)
    prefix_view={**restored_outer['task_state'],**ref['packet_header']}
    restored_packet=dc.reconstruct_authority(prefix_view,value,SOURCE)
    assert hc.encoded(restored_packet)==raw
    assert ref['packet_sha256']==hashlib.sha256(raw).hexdigest()
    assert current['documents'][REMOTE]['content']==TEXT


def test_campaign_reference_is_validated_after_typed_hook(root,monkeypatch):
    monkeypatch.setattr(h,'campaign_prompt_reference',lambda *a:{'exact':'packet'})
    calls=[]
    def changed(root,value,current,prompt,source,**kw):
        calls.append((source,kw['family'],current['documents'][REMOTE]['content']))
        return prompt+h.CAMPAIGN_EVIDENCE_MARKER+json.dumps({'exact':'changed'})
    monkeypatch.setattr(campaign,'grounding_presentation',changed)
    with pytest.raises(ValueError,match='CAMPAIGN_SOURCE_BOUND_REFERENCE_CHANGED'):
        h.compose_input(root,hc.encoded(packet()),'Canonical campaign seam fixture',verified_source=SOURCE,family='claude')
    assert calls==[(SOURCE,'claude',TEXT)]


def test_inverse_cannot_rebind_reference_to_a_different_context_source(root):
    original=context();view=h.outer_document_presentation(root,original,original,packet(),SOURCE)
    other='b'*40
    view['documents'][REMOTE]['content']['source']=other
    view[h.OUTER_DOCUMENT_META]['source']=other
    with pytest.raises(ValueError,match='SOURCE_CONTEXT_CHANGED'):
        h.reconstruct_outer_document(view,original,original,other)
