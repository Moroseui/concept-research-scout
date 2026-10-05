"""Native capture + real composed role inputs; synthetic data, no admissions."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json

import pytest
from orchestrator import linked_disposition_input as l, reviewed_history as r
from orchestrator import disposition_context as d, change_requests as cr, hosted_context as h
from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded
from test_selected_scientific_history import captured, append, write_state, prompt_for
from test_campaign_grounding_presentation import example
from test_disposition_context import SOURCE
from test_linked_disposition_reference import original


@pytest.fixture
def integrated(captured):
    e = captured
    evidence = d.reconstruct_evidence(e.authority['reviewer_evidence']['input_evidence'], SOURCE)
    proof = evidence['verified_events'][0]['linked_disposition']['originals']
    old = d._at(proof, d.PREFIX_PATH)
    # Separate, genuine synthetic request chain, matching the actual route shape.
    request = deepcopy(old['request'])
    request['key'] = 'linked-repair'
    request['identity'] = hashlib.sha256(cr.encoded({k:v for k,v in request.items() if k not in cr.META})).hexdigest()
    repair = {'request': request, 'events': [],
              'head_sha256': hashlib.sha256(cr.encoded(request)+b'\n').hexdigest()}
    for event in old['events']:
        payload = deepcopy(event['payload'])
        if event['event'] == 'REVIEW': payload['applied_event'] = repair['events'][1]['identity']
        append(repair, event['event'], payload)
    old_app = repair['events'][1]['identity']
    archived = append(repair, 'APPLIED', {'modification':'Large superseded repair '+ 'x'*20000,
        'checks':['synthetic'], 'result_binding':{'source':SOURCE}, 'review_status':'PENDING',
        'supersedes_applied_events':[old_app]})
    append(repair, 'APPLIED', {'modification':'Current repair remains literal.', 'checks':['synthetic'],
        'result_binding':{'source':SOURCE}, 'review_status':'PENDING',
        'supersedes_applied_events':[archived['identity']]})
    value = original(); value['originals'] = deepcopy(proof); value['reviewed_repair'] = repair
    value['result']['original_proof_sha256'] = hashlib.sha256(encoded(proof)).hexdigest()
    value['result_sha256'] = hashlib.sha256(encoded(value['result'])).hexdigest()
    reference = l.result_reference(value)
    plan = {'schema':l.SELECTION, 'origin_task':reference['origin_task'],
        'original_value_sha256':reference['original_value_sha256'],
        'boundaries':{'historical_authority':r.boundary(old), 'reviewed_repair':r.boundary(repair)}}
    current = deepcopy(e.current_chain)
    app = append(current, 'APPLIED', {'modification':'Pending exact linked input integration.',
        'checks':['synthetic'], 'review_status':'PENDING', 'result_binding':{'source':SOURCE,
        'reviewed_history_prefix':r.boundary(current),'linked_disposition_input':plan},
        'supersedes_applied_events':[e.latest]})
    write_state(Path(e.config['change_request_store']), current)
    write_state(Path(e.config['change_request_store']), repair)
    linked = l.project(value, plan, app['identity'], SOURCE)
    evidence['verified_events'][0]['linked_disposition'] = linked
    evidence['verified_events'][0]['event']['original_sha256'] = value['result_sha256']
    core = {k:v for k,v in evidence['investigator_wake'].items() if k!='identity'}
    core['events'] = [evidence['verified_events'][0]['event']]
    evidence['investigator_wake'] = {**core, 'identity':digest(core)}
    packet = deepcopy(e.authority); packet.pop('scientific_change_history')
    packet['reviewer_evidence']['input_evidence'] = d.encode_evidence(evidence, SOURCE)
    packet['reviewer_evidence']['catalog_core']['change_request']['applied_event'] = app['identity']
    packet['recorded_changes'] = current
    e.input = packet; e.linked_original = value; e.linked = linked; e.plan = plan
    e.app = app; e.repair = repair
    e.compact = d.capture_current_history(e.config, packet)
    return e


def test_native_capture_then_actual_author_reviewer_composition(integrated):
    e = integrated; packet = e.compact
    original = encoded(e.linked_original)
    assert e.linked['result'] == e.linked_original['result']
    for slot, state in [('reviewed_repair',e.repair),('historical_authority',d._at(e.linked_original['originals'],d.PREFIX_PATH))]:
        shown = e.linked[slot] if slot=='reviewed_repair' else d._at(e.linked['originals'],d.PREFIX_PATH)
        literals = {x['identity']:x for x in shown['events']}
        assert all(literals[x['identity']]==x for x in state['events'] if x['event']!='APPLIED')
        assert d._active(state) <= set(literals)
        assert r.index(shown)==r.index(state)
    for family in ('codex','claude'):
        final,context=h.compose_input(e.root,encoded(packet),prompt_for(e,packet),
            verified_source=SOURCE,family=family,prepared_prompt=True)
        h.measure_input(final,family,'review' if family=='claude' else 'continuation')
        assert 'Full original synthetic adverse finding.' in final
        assert 'Complete external criticism.' in final
        assert 'Current repair remains literal.' in final
        assert 'Large superseded repair' not in final
        assert 'not the original proof bytes' in final
    assert encoded(e.linked_original)==original


@pytest.mark.parametrize('fault',['boundary','external_app','drop_adverse','drop_active','changed_tail','wrong_source','original_pin'])
def test_saved_binding_failure_cases(integrated,fault):
    e=integrated; packet=deepcopy(e.compact)
    linked=packet['reviewer_evidence']['input_evidence']['verified_events'][0]['linked_disposition']
    state=linked['reviewed_repair']
    if fault=='boundary':state['boundary']['head_sha256']='0'*64
    elif fault=='external_app':state['binding_application']='0'*64
    elif fault=='drop_adverse':state['events']=[x for x in state['events'] if x['event']!='REVIEW']
    elif fault=='drop_active':state['events']=[x for x in state['events'] if x['identity'] not in d._active(state)]
    elif fault=='changed_tail':state['events'][-1]['payload']['modification']+='changed'
    elif fault=='wrong_source':linked['input_presentation']['source']='0'*40
    else:linked['input_presentation']['original_reference']['original_value_sha256']='0'*64
    with pytest.raises(ValueError):d.selected_packet_view(packet,SOURCE)


def test_new_tail_and_future_current_state_do_not_rewrite_saved_input(integrated):
    e=integrated; before=encoded(e.compact); previous=d.selected_packet_view(e.compact,SOURCE)
    state=deepcopy(e.repair)
    append(state,'DISPOSITION',{'rationale':'Later unresolved criticism must stay literal.',
        'affected_results':['Synthetic linked evidence']})
    write_state(Path(e.config['change_request_store']),state)
    newer=d.capture_current_history(e.config,e.input)
    shown=d.selected_packet_view(newer,SOURCE)
    assert 'Later unresolved criticism must stay literal.' in str(shown)
    assert d.selected_packet_view(e.compact,SOURCE)==previous
    assert encoded(e.compact)==before


def test_changed_native_original_or_unreviewed_selection_refuses_before_projection(integrated,monkeypatch):
    from orchestrator import investigator_wakes as w,disposition_successors as ds,research_catalog
    e=integrated
    config={**e.config,'investigator':{'template':{'change_request':{
        'request_id':e.input['recorded_changes']['request']['identity'],'applied_event':e.app['identity']}}}}
    monkeypatch.setattr(l,'enabled',lambda *args:True)
    monkeypatch.setattr(w,'setting',lambda c:c['investigator'])
    def blocked(*args):raise ValueError('RESEARCH_CHANGE_REVIEW_PENDING')
    monkeypatch.setattr(research_catalog,'linked_change',blocked)
    with pytest.raises(ValueError,match='REVIEW_PENDING'):l.for_template(config,e.linked_original)
    def missing(*args):raise ValueError('DISPOSITION_PROTECTED_ORIGINAL_CHANGED')
    monkeypatch.setattr(ds,'read_result',missing)
    with pytest.raises(ValueError,match='PROTECTED_ORIGINAL_CHANGED'):w._disposition(config,'c'*64,None)


def test_private_storage_roundtrip_and_changed_bytes_refuse(integrated,tmp_path):
    import os
    from orchestrator import continuing_research as c
    e=integrated;state=tmp_path/'state';state.mkdir(mode=0o700)
    config={'state':str(state),'controller_uid':os.getuid(),'controller_gid':os.getgid()}
    evidence=e.input['reviewer_evidence']['input_evidence']
    ref=c.preserve_evidence(config,evidence)
    assert c.read_evidence(config,ref)==evidence
    raw=Path(ref['evidence_file']).read_bytes()
    assert len(raw)<750000
    Path(ref['evidence_file']).write_bytes(raw+b' ')
    with pytest.raises(ValueError,match='EVIDENCE_CHANGED'):c.read_evidence(config,ref)


@pytest.mark.parametrize('marker',['LINKED_DISPOSITION_INPUT_VERSION=True',
    'LINKED_DISPOSITION_INPUT_VERSION=2',
    'LINKED_DISPOSITION_INPUT_VERSION=1\nLINKED_DISPOSITION_INPUT_VERSION=1',
    'LINKED_DISPOSITION_INPUT_VERSION: int = 1',
    'if True:\n LINKED_DISPOSITION_INPUT_VERSION=1',
    'LINKED_DISPOSITION_INPUT_VERSION=1\ndel LINKED_DISPOSITION_INPUT_VERSION'])
def test_ambiguous_source_profile_refuses(captured,marker):
    (captured.root/'orchestrator/hosted_context.py').write_text(marker+'\n')
    with pytest.raises(ValueError,match='SOURCE_PROFILE'):l.enabled(captured.root,SOURCE)


def test_native_authority_packet_uses_early_capture_without_weakening_bounds(integrated,monkeypatch):
    from orchestrator import research_task_authority as a
    e=integrated
    f=e.root/'orchestrator/hosted_context.py';f.write_text(f.read_text()+'\nLINKED_DISPOSITION_INPUT_VERSION=1\n')
    entry=e.input['reviewer_evidence']['catalog_core']
    monkeypatch.setattr(a,'_evidence',lambda *args:deepcopy(e.input['reviewer_evidence']['input_evidence']))
    monkeypatch.setattr(a,'_decision_contract',lambda *args:deepcopy(e.input['scientific_decision_artifacts']))
    packet=a._packet(e.config,entry,{'source':SOURCE})
    assert packet==e.compact
    assert len(a._transport_bytes({'source':SOURCE},packet))<1500000
    with pytest.raises(ValueError,match='ORIGINAL_TRANSPORT_BOUND'):
        a._transport_bytes({'source':SOURCE},{'oversized':'x'*1500000})


def test_primary_capture_race_refuses_instead_of_rebinding_new_head(integrated):
    e=integrated;packet=deepcopy(e.input)
    packet['recorded_changes']=l.prepare_primary_for_packet(packet['recorded_changes'],
        packet['reviewer_evidence']['input_evidence'],SOURCE,e.app['identity'])
    changed=deepcopy(e.input['recorded_changes'])
    append(changed,'DISPOSITION',{'rationale':'New unreviewed criticism after initial capture.',
        'affected_results':['Synthetic source']})
    write_state(Path(e.config['change_request_store']),changed)
    with pytest.raises(ValueError):d.capture_current_history(e.config,packet)


@pytest.fixture
def multi_reports(integrated):
    from orchestrator import terminal_review as terminal
    e=integrated;store=Path(e.config['change_request_store'])
    repair=deepcopy(e.repair)
    descriptor={'artifact':'evidence/'+e.response_sha+'-response.json','sha256':e.response_sha,'size':len(e.raw_response)}
    append(repair,'REVIEW',{'applied_event':next(iter(d._active(repair))), 'verdict':'REQUEST_CHANGES',
        'rationale':'The same original criticism is recorded against this repair too.', 'affected_results':['Synthetic repair'],
        'original_review':{'response_sha256':e.response_sha},'review_evidence':[descriptor]})
    write_state(store,repair,{descriptor['artifact']:e.raw_response})
    original=deepcopy(e.linked_original);original['reviewed_repair']=repair
    ref=l.result_reference(original);selection=deepcopy(e.plan)
    selection['original_value_sha256']=ref['original_value_sha256']
    selection['boundaries']['reviewed_repair']=r.boundary(repair)
    current=deepcopy(e.input['recorded_changes'])
    findings={name:{'disposition':'preserve','reason':'Synthetic remaining condition.'} for name in terminal.FINDINGS}
    findings['C006']['disposition']=findings['C007']['disposition']='resolved'
    statement={'schema':terminal.PROFILE,'source':SOURCE,'proposal_sha256':'a'*64,
        'manifest_sha256':'b'*64,'session_id':'synthetic-review-session','scope':'material-source-integration',
        'verdict':'APPROVE','inspected':['Synthetic source fixture.'],'unavailable':[],
        'unverified':['H2 remains pending.'],'findings':findings,'resolution_of':terminal.BASE_SOURCE,
        'remaining_gates':['held-deployment','accounting-halt','retained-history-audit','conditional-activation','scientific-acceptance']}
    raw=('Final source/integration verdict: APPROVE\n```terminal-review-verdict\n'+json.dumps(statement)+'\n```\n').encode()
    sha=hashlib.sha256(raw).hexdigest();resolution={'artifact':'evidence/'+sha+'-resolution.md','sha256':sha,'size':len(raw)}
    approval=append(current,'REVIEW',{'applied_event':e.app['identity'],'verdict':'APPROVE',
        'rationale':'Synthetic prior coverage; not approval of new selection.',
        'review_evidence':{'report':resolution},'source':SOURCE,'proposal_sha256':'a'*64})
    plan={'schema':'reviewed-multi-request-source-report-selection/v1','references':{e.response_sha:'Synthetic proposed source-only reconciliation; downstream conditions remain.'},
        'resolution_event':approval['identity'],'resolution_original':resolution,'resolution_text':raw.decode(),
        'scope':'historical-source-findings-only','qualification':'REQUIRES_INDEPENDENT_REVIEW_OF_THIS_EXACT_APPLICATION',
        'additional_prefixes':{repair['request']['identity']:selection['boundaries']['reviewed_repair']}}
    app=append(current,'APPLIED',{'modification':'Pending exact two-request report selection.',
        'checks':['Synthetic'], 'review_status':'PENDING', 'result_binding':{'source':SOURCE,
        'reviewed_history_prefix':r.boundary(current),'linked_disposition_input':selection,'historical_report_selection':plan},
        'supersedes_applied_events':[e.app['identity']]})
    write_state(store,current,{resolution['artifact']:raw})
    evidence=d.reconstruct_evidence(e.input['reviewer_evidence']['input_evidence'],SOURCE)
    evidence['verified_events'][0]['linked_disposition']=l.project(original,selection,app['identity'],SOURCE)
    packet=deepcopy(e.input);packet['recorded_changes']=current
    packet['reviewer_evidence']['catalog_core']['change_request']['applied_event']=app['identity']
    packet['reviewer_evidence']['input_evidence']=d.encode_evidence(evidence,SOURCE)
    e.multi_input=packet;e.multi=d.capture_current_history(e.config,packet);e.multi_app=app;e.multi_repair=repair
    return e


def test_two_request_selection_is_explicit_and_all_unselected_findings_stay_literal(multi_reports):
    e=multi_reports;capture=e.multi['scientific_change_history']
    assert capture['schema']==d.CURRENT_LINKED_HISTORY
    selected=capture['response_originals'][e.response_sha]
    assert isinstance(selected,dict) and 'Protected native change store' in selected['original_body']
    view=d.selected_packet_view(e.multi,SOURCE)
    assert 'H2 remains pending.' in str(view)
    assert 'Full original synthetic adverse finding.' in str(view)
    assert 'The same original criticism is recorded against this repair too.' in str(view)
    assert e.multi_app['payload']['review_status']=='PENDING'
    # Merely naming a report never grants an approval or makes it model-inspected.
    assert 'not newly' in selected['notice']


@pytest.mark.parametrize('fault',['missing_original','changed_original','changed_reference','cross_request','unreviewed_tail'])
def test_multi_request_reference_refusals(multi_reports,fault):
    e=multi_reports;store=Path(e.config['change_request_store'])
    if fault in ('missing_original','changed_original'):
        path=store/e.multi_repair['request']['identity']/('evidence/'+e.response_sha+'-response.json')
        if fault=='missing_original':path.unlink()
        else:path.write_bytes(b'changed')
        with pytest.raises((ValueError,FileNotFoundError)):d.capture_current_history(e.config,e.multi_input)
    elif fault=='changed_reference':
        value=deepcopy(e.multi);value['scientific_change_history']['response_originals'][e.response_sha]['original_recorded_verdict']='APPROVE'
        with pytest.raises(ValueError):d.validate_current_history(value,SOURCE)
    elif fault=='cross_request':
        value=deepcopy(e.multi);value['scientific_change_history']['response_references'][0]['request']='f'*64
        with pytest.raises(ValueError):d.validate_current_history(value,SOURCE)
    else:
        repair=deepcopy(e.multi_repair)
        descriptor={'artifact':'evidence/'+e.response_sha+'-response.json','sha256':e.response_sha,'size':len(e.raw_response)}
        append(repair,'REVIEW',{'applied_event':next(iter(d._active(repair))),'verdict':'REQUEST_CHANGES',
            'rationale':'New adverse occurrence beyond the reviewed boundary.', 'affected_results':['Synthetic repair'],
            'original_review':{'response_sha256':e.response_sha},'review_evidence':[descriptor]})
        write_state(store,repair)
        with pytest.raises(ValueError):d.capture_current_history(e.config,e.multi_input)


@pytest.mark.parametrize('fault',['suffix','historical_pin','representation_pin','drop_index'])
def test_same_packet_reviewed_extension_tampering_refuses(integrated,fault):
    value=deepcopy(integrated.compact);ext=value['recorded_changes']
    assert ext['schema']==d.REVIEWED_EXTENSION
    if fault=='suffix':ext['suffix_events'][-1]['payload']['modification']+='changed'
    elif fault=='historical_pin':ext['historical_representation_sha256']='0'*64
    elif fault=='representation_pin':ext['current_representation_sha256']='0'*64
    else:ext['prefix_index_suffix']=ext['prefix_index_suffix'][:-1]
    with pytest.raises(ValueError):d.validate_current_history(value,SOURCE)


def test_actual_runtime_stage_reads_originals_and_blocks_changed_reference(multi_reports,tmp_path,monkeypatch):
    from types import SimpleNamespace
    from orchestrator.handover_runtime import Runtime
    from orchestrator import hosted_campaign_task
    e=multi_reports;packet=deepcopy(e.multi);packet['campaign_task']={'synthetic':'dispatch-test'}
    report_text='Synthetic report, no scientific conclusion.'
    report={'id':hashlib.sha256(report_text.encode()).hexdigest()}
    identity=digest({'source':SOURCE,'packet':packet,'report':report})
    state=tmp_path/'runtime';folder=state/'tasks'/identity;folder.mkdir(parents=True,mode=0o700)
    (folder/'packet.json').write_bytes(encoded(packet));(folder/'report.json').write_bytes(encoded(report))
    (state/'reports').mkdir();(state/'reports'/(report['id']+'.md')).write_text(report_text)
    runtime=SimpleNamespace(state=state,config=e.config,validate_binding=lambda b:None)
    calls=[]
    monkeypatch.setattr(hosted_campaign_task,'stage_result',lambda *a,**k:calls.append('stage') or {'test':'stage-reached'})
    binding={'id':identity,'source':SOURCE,'stages':['continuation','review','disposition']}
    assert Runtime.model(runtime,binding,0)=={'test':'stage-reached'}
    receipt=json.loads((folder/'report-references-continuation.json').read_bytes())
    assert receipt['provider_calls']==0 and len(receipt['retrieved'])>=2
    path=Path(e.config['change_request_store'])/e.multi_repair['request']['identity']/('evidence/'+e.response_sha+'-response.json')
    path.write_bytes(b'altered after task capture')
    with pytest.raises(ValueError):Runtime.model(runtime,binding,0)
    assert calls==['stage']


def test_linked_context_storage_is_lossless_source_bound(monkeypatch):
    from orchestrator import hosted_context as h, linked_disposition_input as linked
    source = 'a' * 40
    context = {'verified_source_commit': source, 'task_state': {
        'scientific_change_history': {'schema': 'current-linked-scientific-change-capture/v2'},
        'evidence': {'unchanged': ['full original', {'unicode': '\u03b1'}]}}}
    monkeypatch.setattr(linked, 'enabled', lambda root, pin: pin == source)
    raw = h.context_bytes('.', context, source)
    assert json.loads(raw) == context
    assert b'\n  ' not in raw
    with pytest.raises(ValueError, match='LINKED_INPUT_SOURCE_PROFILE_REQUIRED'):
        h.context_bytes('.', context, 'b' * 40)
    context['verified_source_commit'] = 'b' * 40
    with pytest.raises(ValueError, match='HOSTED_CONTEXT_SOURCE_CHANGED'):
        h.context_bytes('.', context, source)
    context['verified_source_commit'] = source
    context['task_state']['evidence'] = 'x' * 1500000
    with pytest.raises(ValueError, match='HOSTED_FULL_CONTEXT_TOO_LARGE'):
        h.context_bytes('.', context, source)


@pytest.fixture
def scientific_packet(integrated):
    e = integrated
    native = deepcopy(e.linked_original)
    proof = native['originals']
    proof['packet']['campaign_task'] = {'mode': 'discuss', 'task_id': 'original-only'}
    proof['packet']['old_administrative_transport'] = 'Never science or authority. ' * 5000
    native['result']['original_proof_sha256'] = d._sha(proof)
    native['result_sha256'] = d._sha(native['result'])
    plan = deepcopy(e.plan)
    plan.update(schema=l.SCIENTIFIC_SELECTION,
        original_value_sha256=l.result_reference(native)['original_value_sha256'],
        packet_selection={'original_packet_sha256': d._sha(proof['packet']),
            'scientific_context_sha256': d._sha(d._at(proof, d.CHARTER_PATH)),
            'campaign_task_sha256': d._sha(proof['packet']['campaign_task']),
            'retained_proof_sha256': d._sha({k:v for k,v in proof.items()
                if k not in ('packet','schema')})})
    state = deepcopy(e.input['recorded_changes'])
    app = append(state, 'APPLIED', {'modification': 'Exact prospective scientific packet view.',
        'checks': ['synthetic original bytes'], 'review_status': 'PENDING',
        'result_binding': {'source': SOURCE, 'reviewed_history_prefix': r.boundary(state),
            'linked_disposition_input': plan},
        'supersedes_applied_events': [e.app['identity']]})
    write_state(Path(e.config['change_request_store']), state)
    shown = l.project(native, plan, app['identity'], SOURCE)
    evidence = d.reconstruct_evidence(e.input['reviewer_evidence']['input_evidence'], SOURCE)
    evidence['verified_events'][0]['linked_disposition'] = shown
    evidence['verified_events'][0]['event']['original_sha256'] = native['result_sha256']
    core = {k:v for k,v in evidence['investigator_wake'].items() if k!='identity'}
    core['events'] = [evidence['verified_events'][0]['event']]
    evidence['investigator_wake'] = {**core,'identity':digest(core)}
    packet = deepcopy(e.input)
    packet['reviewer_evidence']['input_evidence'] = d.encode_evidence(evidence, SOURCE)
    packet['reviewer_evidence']['catalog_core']['change_request']['applied_event'] = app['identity']
    packet['recorded_changes'] = state
    e.scientific_native=native; e.scientific_plan=plan; e.scientific_app=app
    e.scientific_shown=shown; e.scientific_packet=d.capture_current_history(e.config,packet)
    return e


def test_typed_packet_actual_roles_keep_science_and_criticism(scientific_packet):
    e=scientific_packet
    proof=e.scientific_shown['originals']; original=e.scientific_native['originals']
    assert proof['scientific_input_context']==d._at(original,d.CHARTER_PATH)
    assert e.scientific_shown['result']==e.scientific_native['result']
    assert {k:v for k,v in proof.items() if k not in (
        'packet','schema','scientific_input_context','historical_authority')} == {
        k:v for k,v in original.items() if k not in ('packet','schema')}
    assert len(encoded(e.scientific_shown)) < len(encoded(e.scientific_native))-100000
    for family in ('codex','claude'):
        prompt,context=h.compose_input(e.root,encoded(e.scientific_packet),
            prompt_for(e,e.scientific_packet),verified_source=SOURCE,
            family=family,prepared_prompt=True)
        assert 'Full original synthetic adverse finding.' in prompt
        assert 'Complete external criticism.' in prompt
        assert 'Never science or authority.' not in prompt
        assert 'not reproduced here or claimed model-inspected' in prompt


@pytest.mark.parametrize('fault', ['science','result','original_packet','task','new_field','old_plan','retained_proof','packet_notice','presentation_notice'])
def test_typed_packet_exact_binding_and_scientific_bodies(scientific_packet,fault):
    e=scientific_packet; shown=deepcopy(e.scientific_shown);plan=deepcopy(e.scientific_plan)
    proof=shown['originals']
    if fault=='science':proof['scientific_input_context']['hidden_change']='new interpretation'
    elif fault=='result':shown['result']['answer']='Invented acceptance.'
    elif fault=='original_packet':proof['packet']['original_packet_sha256']='0'*64
    elif fault=='task':proof['packet']['campaign_task']['mode']='execute'
    elif fault=='new_field':proof['packet']['extra_authority']=True
    elif fault=='packet_notice':proof['packet']['notice']='This is accepted science.'
    elif fault=='presentation_notice':shown['input_presentation']['notice']='No original evidence omitted.'
    elif fault=='old_plan':plan['schema']=l.SELECTION;del plan['packet_selection']
    else:proof['report']={'text':'Changed original report.'}
    with pytest.raises(ValueError):
        l.validate(shown,plan,e.scientific_app['identity'],SOURCE)


def test_typed_packet_unknown_original_change_cannot_reuse_selection(scientific_packet):
    e=scientific_packet; native=deepcopy(e.scientific_native)
    native['originals']['packet']['new_unresolved_criticism']='Must not silently disappear.'
    native['result']['original_proof_sha256']=d._sha(native['originals'])
    native['result_sha256']=d._sha(native['result'])
    with pytest.raises(ValueError):
        l.project(native,e.scientific_plan,e.scientific_app['identity'],SOURCE)
