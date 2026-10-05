"""Two fixed same-prompt document references; no packet/approval inference."""
from copy import deepcopy
import hashlib,json
import pytest
from orchestrator import hosted_context as h, hosted_cycle as cycle, scientific_decision as decision
from test_outer_document_view import root, context, packet, prompt, decode, SOURCE, REMOTE

AUTH=h.OUTER_AUTHORIZATION_NAME
DIRECTIVE=h.OUTER_DIRECTIVE_NAME

@pytest.fixture
def docs(root,monkeypatch):
    current=context();policy=current['shared_policy']
    texts={AUTH:'Synthetic authorization. Preserve reservations.\r\nSecond line.\n'*80,
           DIRECTIVE:'Synthetic reviewer directive. Keep every adverse finding.\n'*80}
    for name,text in texts.items():
        policy['operating_context']['documents'][name]={'sha256':hashlib.sha256(text.encode()).hexdigest(),'text':text}
    policy['direction']=texts[AUTH]
    policy['policy'].update(direction_path=AUTH,direction_sha256=hashlib.sha256(texts[AUTH].encode()).hexdigest())
    current['documents'][DIRECTIVE]={'sha256':hashlib.sha256(texts[DIRECTIVE].encode()).hexdigest(),
        'disposition':h.DOCUMENTS[DIRECTIVE],'content':texts[DIRECTIVE]}
    (root/'orchestrator/hosted_context.py').write_text('OUTER_DOCUMENT_VIEW_VERSION = 1\nOUTER_POLICY_DOCUMENT_VIEW_VERSION = 1\n')
    monkeypatch.setattr(h,'shared_policy',lambda path:deepcopy(policy))
    monkeypatch.setattr(h,'build',lambda path,state:{**deepcopy(current),'task_state':deepcopy(state)})
    monkeypatch.setattr(decision.authority,'context',lambda path:deepcopy(policy))
    return root,current,texts

@pytest.mark.parametrize('family',['claude','codex'])
@pytest.mark.parametrize('trigger',['installed-research-eligibility','installed-research-request','verified-completion'])
def test_composed_roundtrip_original_receipt_and_policy_slot(docs,family,trigger):
    root,_,texts=docs;value=packet(trigger);body=prompt(root,value)
    final,current=h.compose_input(root,cycle.encoded(value),body,verified_source=SOURCE,family=family)
    view=decode(final);before=h.authority_presentation(root,value,current,body,SOURCE)
    restored=h.reconstruct_outer_document(view,before,current,SOURCE)
    assert cycle.encoded(restored)==cycle.encoded(before)
    assert current['shared_policy']['direction']==texts[AUTH]
    assert current['documents'][DIRECTIVE]['content']==texts[DIRECTIVE]
    assert view['shared_policy']['operating_context']['documents']==current['shared_policy']['operating_context']['documents']
    for name,text in texts.items():assert final.count(json.dumps(text))==1
    tail=final.split('\n\nBOUND TASK / HISTORICAL EVIDENCE:\n',1)[1]
    assert h.outer_document_policy_prompt(tail,view,before,current,SOURCE,restore=True)==body
    if trigger=='installed-research-eligibility':
        ref=json.JSONDecoder().raw_decode(tail.split(h.TRUSTED_POLICY_MARKER,1)[1])[0]
        assert ref['schema']==h.RESTORED_POLICY_SCHEMA
        assert ref['policy_sha256']==hashlib.sha256(cycle.encoded(current['shared_policy'])).hexdigest()
        assert ref['presented_policy_sha256']==hashlib.sha256(cycle.encoded(view['shared_policy'])).hexdigest()
        assert ref['policy_sha256']!=ref['presented_policy_sha256']

@pytest.mark.parametrize('slot',[AUTH,DIRECTIVE])
@pytest.mark.parametrize('field,bad',[('schema','other'),('source','b'*40),('name','foreign'),
    ('literal_location','operating_context.task_state'),('sha256','c'*64),('bytes',True),
    ('bytes',1.5),('trust','New approval'),('extra','field')])
def test_ref_changes_refuse(docs,slot,field,bad):
    root,original,_=docs;view=h.outer_document_presentation(root,original,original,packet(),SOURCE)
    actual=view['shared_policy']['direction'] if slot==AUTH else view['documents'][DIRECTIVE]['content']
    actual[field]=bad
    with pytest.raises(ValueError):h.reconstruct_outer_document(view,original,original,SOURCE)

@pytest.mark.parametrize('slot',[AUTH,DIRECTIVE])
def test_integral_float_length_is_not_exact_integer(docs,slot):
    root,original,_=docs;view=h.outer_document_presentation(root,original,original,packet(),SOURCE)
    actual=view['shared_policy']['direction'] if slot==AUTH else view['documents'][DIRECTIVE]['content']
    actual['bytes']=float(actual['bytes'])
    with pytest.raises(ValueError):h.reconstruct_outer_document(view,original,original,SOURCE)

@pytest.mark.parametrize('change',['missing','changed','alias','hash','extra','direction-path','direction-sha','outer-directive','outer-disposition'])
def test_no_changed_target_is_repaired(docs,monkeypatch,change):
    root,value,_=docs;value=deepcopy(value);policy=value['shared_policy'];target=policy['operating_context']['documents'][AUTH]
    if change=='missing':del policy['operating_context']['documents'][AUTH]
    elif change=='changed':target['text']+='different'
    elif change=='alias':target['text']={'schema':h.OUTER_DOCUMENT_SCHEMA}
    elif change=='hash':target['sha256']='c'*64
    elif change=='extra':target['extra']='not the fixed shape'
    elif change=='direction-path':policy['policy']['direction_path']='foreign'
    elif change=='direction-sha':policy['policy']['direction_sha256']='c'*64
    elif change=='outer-directive':value['documents'][DIRECTIVE]['content']+='different'
    else:value['documents'][DIRECTIVE]['disposition']='New grant'
    monkeypatch.setattr(h,'shared_policy',lambda path:deepcopy(policy))
    with pytest.raises(ValueError):h.outer_document_presentation(root,value,value,packet(),SOURCE)

@pytest.mark.parametrize('slot',[AUTH,DIRECTIVE])
def test_same_prompt_target_change_or_unrelated_content_change_refuses(docs,slot):
    root,original,_=docs;view=deepcopy(h.outer_document_presentation(root,original,original,packet(),SOURCE))
    view['shared_policy']['operating_context']['documents'][slot]['text']+='changed'
    with pytest.raises(ValueError):h.reconstruct_outer_document(view,original,original,SOURCE)
    view=deepcopy(h.outer_document_presentation(root,original,original,packet(),SOURCE))
    view['task_state']['new_grant']='No'
    with pytest.raises(ValueError):h.reconstruct_outer_document(view,original,original,SOURCE)

@pytest.mark.parametrize('field,bad',[('schema',h.TRUSTED_POLICY_SCHEMA),('source','b'*40),
    ('policy_sha256','c'*64),('presented_policy_sha256','c'*64),('literal_location','operating_context.task_state')])
def test_restored_policy_reference_mutations_refuse(docs,field,bad):
    root,_,_=docs;value=packet('installed-research-eligibility');body=prompt(root,value)
    final,current=h.compose_input(root,cycle.encoded(value),body,verified_source=SOURCE,family='claude')
    view=decode(final);before=h.authority_presentation(root,value,current,body,SOURCE)
    tail=final.split('\n\nBOUND TASK / HISTORICAL EVIDENCE:\n',1)[1]
    prefix,rest=tail.split(h.TRUSTED_POLICY_MARKER);ref,end=json.JSONDecoder().raw_decode(rest);ref[field]=bad
    changed=prefix+h.TRUSTED_POLICY_MARKER+json.dumps(ref)+rest[end:]
    with pytest.raises(ValueError):h.outer_document_policy_prompt(changed,view,before,current,SOURCE,restore=True)
    with pytest.raises(ValueError):h.outer_document_policy_prompt(tail.replace(h.TRUSTED_POLICY_MARKER,'missing'),view,before,current,SOURCE,restore=True)

@pytest.mark.parametrize('definition',['OUTER_POLICY_DOCUMENT_VIEW_VERSION = True','OUTER_POLICY_DOCUMENT_VIEW_VERSION = 2',
    'OUTER_POLICY_DOCUMENT_VIEW_VERSION: int = 1','OUTER_POLICY_DOCUMENT_VIEW_VERSION = 1\nOUTER_POLICY_DOCUMENT_VIEW_VERSION = 1',
    'if True:\n OUTER_POLICY_DOCUMENT_VIEW_VERSION = 1','def f():\n OUTER_POLICY_DOCUMENT_VIEW_VERSION = 1'])
def test_new_source_marker_is_exact(docs,definition):
    root,_,_=docs;(root/'orchestrator/hosted_context.py').write_text(definition+'\n')
    with pytest.raises(ValueError):h.outer_policy_document_profile(root,SOURCE)

def test_old_source_profile_keeps_old_policy_and_metadata(docs):
    root,original,_=docs;(root/'orchestrator/hosted_context.py').write_text('OUTER_DOCUMENT_VIEW_VERSION = 1\n')
    before=cycle.encoded(original);view=h.outer_document_presentation(root,original,original,packet(),SOURCE)
    assert view[h.OUTER_DOCUMENT_META]['schema']=='outer-operating-document-presentation/v1'
    assert view['shared_policy']==original['shared_policy']
    assert view['documents'][DIRECTIVE]==original['documents'][DIRECTIVE]
    assert cycle.encoded(original)==before

def test_semantic_packet_remains_explicitly_nonreconstructible(docs):
    root,original,_=docs;shown=deepcopy(original);shown['selected_scientific_presentation']={'meaning':'Semantic selected packet'}
    view=h.outer_document_presentation(root,shown,original,packet(),SOURCE)
    assert 'does not reconstruct original packets' in view[h.OUTER_DOCUMENT_META]['restoration']
    assert cycle.encoded(h.reconstruct_outer_document(view,shown,original,SOURCE))==cycle.encoded(shown)
