"""Fixed native reference projection before bounded evidence storage."""
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import pytest
from orchestrator import linked_disposition_input as l, disposition_context as d
from orchestrator import continuing_research as continuing, disposition_successors as successors
from orchestrator.hosted_cycle import encoded
from test_linked_input_integration import integrated
from test_selected_scientific_history import captured
from test_campaign_grounding_presentation import example
from test_disposition_context import SOURCE

PLAN={'schema':l.CURRENT_REFERENCE_SELECTION,
      'scope':'native-originals-with-literal-scientific-context',
      'qualification':'REQUIRES_INDEPENDENT_REVIEW_OF_THIS_EXACT_APPLICATION',
      'require_current_history':True}


def test_native_rule_keeps_science_and_original_binding(integrated):
    e=integrated;original=deepcopy(e.linked_original)
    view=l.project(original,PLAN,e.app['identity'],SOURCE)
    assert original==e.linked_original
    assert view['result']==original['result']
    assert view['originals']['packet']['campaign_task']==original['originals']['packet']['campaign_task']
    assert view['originals']['scientific_input_context']==d._at(original['originals'],d.CHARTER_PATH)
    for key,value in original['originals'].items():
        if key not in ('schema','packet'):
            assert view['originals'][key]==value
    assert view['input_presentation']['original_reference']==successors.result_reference(original)
    assert len(encoded(view))<len(encoded(original))


def test_actual_intake_store_roundtrip_keeps_exact_reference(integrated,tmp_path):
    e=integrated
    evidence=d.reconstruct_evidence(e.input['reviewer_evidence']['input_evidence'],SOURCE)
    view=l.project(e.linked_original,PLAN,e.app['identity'],SOURCE)
    evidence['verified_events'][0]['linked_disposition']=view
    stored=d.encode_evidence(evidence,SOURCE)
    state=tmp_path/'state';state.mkdir(mode=0o700)
    config={'state':str(state),'controller_uid':os.getuid(),'controller_gid':os.getgid()}
    descriptor=continuing.preserve_evidence(config,stored)
    assert continuing.read_evidence(config,descriptor)==stored
    assert d.reconstruct_evidence(stored,SOURCE)==evidence
    assert Path(descriptor['evidence_file']).stat().st_size<=750000


@pytest.mark.parametrize('field',['require_current_history','qualification','scope','extra'])
def test_plan_cannot_disable_history_or_approve_itself(integrated,field):
    plan=deepcopy(PLAN)
    plan[field]=False if field=='require_current_history' else 'changed'
    with pytest.raises(ValueError,match='REVIEWED_PLAN'):
        l.project(integrated.linked_original,plan,integrated.app['identity'],SOURCE)


@pytest.mark.parametrize('fault',['science','author','result','repair','source','application','missing-original'])
def test_native_authentication_rejects_changed_consumed_material(integrated,monkeypatch,fault):
    e=integrated;view=l.project(e.linked_original,PLAN,e.app['identity'],SOURCE)
    calls=[]
    def read(config,ref,client):
        calls.append(deepcopy(ref))
        if fault=='missing-original':raise ValueError('ORIGINAL_MISSING')
        assert ref==successors.result_reference(e.linked_original)
        return deepcopy(e.linked_original)
    monkeypatch.setattr(successors,'read_result_reference',read)
    if fault=='science':view['originals']['scientific_input_context']['pending']='changed'
    elif fault=='author':view['originals']['protected_original']={'altered':'output'}
    elif fault=='result':view['result']['answer']='changed'
    elif fault=='repair':view['reviewed_repair']['head_sha256']='0'*64
    elif fault=='source':view['input_presentation']['source']='0'*40
    elif fault=='application':view['input_presentation']['binding_application']='0'*64
    with pytest.raises(ValueError):
        l.authenticate_reference_view({},view,source=SOURCE,application=e.app['identity'],plan=PLAN,client=None)


def test_same_original_is_authenticated_without_new_authority(integrated,monkeypatch):
    e=integrated;view=l.project(e.linked_original,PLAN,e.app['identity'],SOURCE)
    calls=[]
    def read(config,ref,client):
        calls.append(ref)
        return deepcopy(e.linked_original)
    monkeypatch.setattr(successors,'read_result_reference',read)
    assert l.authenticate_reference_view({},view,source=SOURCE,application=e.app['identity'],plan=PLAN,client=None)==e.linked_original
    assert calls==[successors.result_reference(e.linked_original)]
