"""Synthetic current/history capture and semantic-view boundary checks; no models."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
from orchestrator import disposition_context as d, change_requests as cr
from orchestrator import hosted_context as h, research_task_authority as r
from orchestrator.hosted_cycle import encoded
from test_disposition_context import fixture as original_evidence, chain, SOURCE
from test_campaign_grounding_presentation import example


def append(state, kind, payload):
    core = {'schema': cr.EVENT_SCHEMA, 'request_identity': state['request']['identity'],
        'sequence': len(state['events']) + 1, 'previous_sha256': state['head_sha256'],
        'event': kind, 'payload': deepcopy(payload),
        'actor': {'kind': 'human', 'identity': 'synthetic'},
        'recorded_at_utc': '2026-09-13T00:00:00+00:00'}
    event = {**core, 'identity': hashlib.sha256(cr.encoded(core)).hexdigest()}
    state['events'].append(event)
    state['head_sha256'] = hashlib.sha256(cr.encoded(event) + b'\n').hexdigest()
    return event


def write_state(store, state, artifacts=None):
    folder = store / state['request']['identity']
    (folder / 'events').mkdir(parents=True, exist_ok=True)
    values = {'request.json': state['request'],
              **{f'events/{e["sequence"]:04d}-{e["identity"]}.json': e for e in state['events']}}
    for name, value in values.items():
        p = folder / name
        p.write_bytes(cr.encoded(value) + b'\n')
        p.chmod(0o600)
    for name, raw in (artifacts or {}).items():
        p = folder / name
        p.parent.mkdir(exist_ok=True)
        p.write_bytes(raw)
        p.chmod(0o600)


@pytest.fixture
def captured(example, tmp_path):
    e = example
    (e.root / 'orchestrator/hosted_context.py').write_text(
        'OUTER_DOCUMENT_VIEW_VERSION = 1\nSELECTED_HISTORY_VIEW_VERSION = 1\n')
    (e.root / 'orchestrator/research_task_authority.py').write_text(
        'EVIDENCE_VERSION = 2\nHOSTED_PRESENTATION_VERSION = 1\n')
    evidence, current = original_evidence()
    # Rehash the old fixture's adverse review with full inline findings.
    current = deepcopy(current)
    history_events = deepcopy(current['events'])
    current['events'] = []
    current['head_sha256'] = hashlib.sha256(cr.encoded(current['request']) + b'\n').hexdigest()
    for old in history_events:
        payload = deepcopy(old['payload'])
        if old['event'] == 'REVIEW':
            payload['applied_event'] = current['events'][1]['identity']
            payload['findings'] = ['Full original synthetic adverse finding.']
        append(current, old['event'], payload)
    historical = deepcopy(current)
    target = {'scientific_context': 'Original synthetic scientific context.\n',
              'pending': 'No acceptance or scientific result.'}
    proof = evidence['verified_events'][0]['linked_disposition']['originals']
    d._put(proof, d.PREFIX_PATH, historical)
    d._put(proof, d.CHARTER_PATH, target)
    evidence['installed_charter_evidence']['reviewer_evidence'] = deepcopy(target)

    # The same request can appear in both known proof slots. The capture is
    # unique by native identity, while each historical active application stays.
    evidence['verified_events'][0]['linked_disposition']['reviewed_repair'] = deepcopy(historical)
    old_active = current['events'][1]['identity']
    intermediate = append(current, 'APPLIED', {'modification': 'Archived implementation ' + 'x' * 20000,
        'checks': ['Synthetic'], 'result_binding': {'source': SOURCE}, 'review_status': 'PENDING',
        'supersedes_applied_events': [old_active]})
    response = {'scope': 'synthetic', 'verdict': 'REQUEST_CHANGES',
        'findings': ['Complete external criticism.'], 'questions': ['Unresolved question.'],
        'remaining_obligations': ['Preserve existing gates.'], 'resolved': []}
    original = {'type': 'result', 'session_id': 'synthetic-session', 'is_error': False,
        'subtype': 'success', 'modelUsage': {'synthetic-model': {}},
        'structured_output': response, 'result': json.dumps(response), 'duration_ms': 10}
    raw = (json.dumps(original, indent=2) + '\r\n').encode()
    sha = hashlib.sha256(raw).hexdigest()
    descriptor = {'artifact': 'evidence/' + sha + '-response.json', 'sha256': sha, 'size': len(raw)}
    append(current, 'REVIEW', {'applied_event': intermediate['identity'], 'verdict': 'REQUEST_CHANGES',
        'rationale': 'Latest criticism remains unresolved.', 'affected_results': ['Synthetic'],
        'original_review': {'response_sha256': sha}, 'review_evidence': [descriptor]})
    append(current, 'DISPOSITION', {'rationale': 'Complete response does not erase the adverse verdict.',
        'affected_results': ['Synthetic'], 'response_evidence': descriptor,
        'driver_responses': ['Complete literal response.'], 'admissions': 0, 'provider_calls': 0})
    latest = append(current, 'APPLIED', {'modification': 'Current implementation pending review.',
        'checks': ['Synthetic'], 'result_binding': {'source': SOURCE}, 'review_status': 'PENDING',
        'supersedes_applied_events': [intermediate['identity']]})
    store = tmp_path / 'changes'
    write_state(store, current, {descriptor['artifact']: raw})
    config = {'source': SOURCE, 'source_root': str(e.root), 'change_request_store': str(store)}
    primary = {'request_id': current['request']['identity'], 'applied_event': latest['identity']}
    stored = d.encode_evidence(evidence, SOURCE)
    packet = {'version': 1, 'trigger': 'installed-research-eligibility',
        'scientific_decision_artifacts': {'version': 2},
        'reviewer_evidence': {'catalog_core': {'source': SOURCE,
            'request': {'task': {'schema': 'investigator-task/v1'}},
            'change_request': primary}, 'input_evidence': stored},
        'recorded_changes': current}
    e.authority = d.capture_current_history(config, packet)
    campaign = {**e.packet, 'reviewer_evidence': stored,
        'research_catalog_entry': {'change_request': primary},
        'recorded_changes': {'projection': {'kind': 'BOUNDED_SUMMARY'},
                             'requests': [{'notice': 'Global overview only.'}]}}
    e.campaign = d.capture_current_history(config, campaign)
    e.config = config
    e.current_chain = current
    e.raw_response = raw
    e.response_sha = sha
    e.old_active = old_active
    e.intermediate = intermediate['identity']
    e.latest = latest['identity']
    return e


def prompt_for(e, packet):
    if packet['trigger'] == 'installed-research-eligibility':
        policy = h.shared_policy(e.root)
        return ('TRUSTED SCIENTIFIC DECISION INSTRUCTIONS:\n'
            + h.TRUSTED_POLICY_MARKER + json.dumps(h.trusted_policy_reference(policy, SOURCE))
            + h.TRUSTED_POLICY_END + 'Preserve synthetic decisions.'
            + h.EVIDENCE_MARKER + json.dumps(r.evidence_for_packet(e.root, packet, SOURCE)))
    return 'Synthetic third-stage disposition.' + h.CAMPAIGN_EVIDENCE_MARKER + json.dumps(
        h.campaign_prompt_reference(encoded(packet), SOURCE))


def shown_context(final):
    return json.JSONDecoder().raw_decode(final.split(':\n', 1)[1])[0]


@pytest.mark.parametrize('kind', ['authority', 'campaign'])
def test_full_native_capture_binds_current_and_historical_without_mutating_originals(captured, kind):
    e = captured
    packet = getattr(e, kind)
    before = encoded(packet)
    view = d.selected_packet_view(packet, SOURCE)
    binding = d.validate_selected_packet_view(view, packet, SOURCE)
    primary = packet['scientific_change_history']['primary']['request_id']
    selected = view['recorded_changes'] if kind == 'authority' else view['scientific_change_history']['chains'][primary]
    assert {row['identity'] for row in selected['events'] if row['event'] == 'APPLIED'} == {e.old_active, e.latest}
    assert selected['superseded_applied_index'] == [{'sequence': 5, 'identity': e.intermediate}]
    for shown_event in selected['events']:
        original_event = next(row for row in e.current_chain['events'] if row['identity'] == shown_event['identity'])
        assert shown_event['recorded_at_utc'] == original_event['recorded_at_utc']
        if shown_event['event'] == 'APPLIED':
            assert shown_event == original_event
        else:
            restored = deepcopy(shown_event)
            for field in ('schema', 'request_identity', 'previous_sha256'):
                restored[field] = original_event[field]
            for field in ('evidence', 'review_evidence', 'response_evidence'):
                value = restored['payload'].get(field)
                rows = value if isinstance(value, list) else [value]
                for row in rows:
                    if isinstance(row, dict) and set(row) == {'name','sha256','size'}:
                        row['artifact'] = 'evidence/' + row['sha256'] + '-' + row.pop('name')
            assert restored == original_event
    assert binding['original_packet_sha256'] == hashlib.sha256(before).hexdigest()
    assert binding['selected_packet_sha256'] == hashlib.sha256(encoded(view)).hexdigest()
    assert encoded(packet) == before
    assert d.validate_current_history(packet, SOURCE)[primary] == e.current_chain
    originals = packet['scientific_change_history']['response_originals']
    assert originals[e.response_sha].encode() == e.raw_response
    shown = view['scientific_change_history']['response_originals'][e.response_sha]
    assert shown['value']['structured_output'] == json.loads(e.raw_response)['structured_output']
    assert 'result' in shown['indexed_wrapper_fields']
    assert 'not a lossless' in selected['notice']


@pytest.mark.parametrize('kind', ['authority', 'campaign'])
@pytest.mark.parametrize('family', ['codex', 'claude'])
def test_both_real_composers_show_full_criticism_and_honest_active_refs(captured, kind, family):
    e = captured
    packet = getattr(e, kind)
    original = encoded(packet)
    final, current = h.compose_input(e.root, original, prompt_for(e, packet),
        verified_source=SOURCE, family=family, prepared_prompt=True)
    shown = shown_context(final)
    assert current['task_state']['reviewer_evidence'] == packet['reviewer_evidence']
    assert 'selected_scientific_presentation' not in current
    assert shown['selected_scientific_presentation']['original_packet_sha256'] == hashlib.sha256(original).hexdigest()
    assert 'Complete external criticism.' in final and 'Complete literal response.' in final
    assert 'Archived implementation' not in final
    assert 'No original proof or evidence reconstruction is claimed.' in final
    assert 'indexed APPLIED payloads cannot be reconstructed' in final
    assert 'THEN restore any separate authority prefix' not in final
    assert current['shared_policy'] == h.shared_policy(e.root)
    assert h.compose_input(e.root, original, prompt_for(e, packet), verified_source=SOURCE,
        family=family, prepared_prompt=True) == (final, current)


@pytest.mark.parametrize('mutation', ['missing_capture', 'source', 'primary', 'head', 'body',
                                      'missing_body', 'extra_chain', 'reference', 'event'])
def test_malformed_or_unbound_capture_refuses(captured, mutation):
    packet = deepcopy(captured.authority)
    capture = packet['scientific_change_history']
    if mutation == 'missing_capture':
        del packet['scientific_change_history']
    elif mutation == 'source':
        capture['source'] = '0' * 40
    elif mutation == 'primary':
        capture['primary']['applied_event'] = captured.intermediate
    elif mutation == 'head':
        packet['recorded_changes']['head_sha256'] = '0' * 64
    elif mutation == 'body':
        capture['response_originals'][captured.response_sha] += 'tampered'
    elif mutation == 'missing_body':
        capture['response_originals'].clear()
    elif mutation == 'extra_chain':
        capture['chains']['0' * 64] = captured.current_chain
    elif mutation == 'reference':
        capture['response_references'][0]['descriptor']['size'] += 1
    else:
        packet['recorded_changes']['suffix_events'][0]['payload']['modification'] = 'Tampered'
    with pytest.raises(ValueError):
        d.selected_packet_view(packet, SOURCE)


@pytest.mark.parametrize('mutation', ['dropped_review', 'dropped_disposition', 'dropped_active',
                                      'old_prefix', 'old_charter', 'wrong_view_hash'])
def test_view_tampering_cannot_be_accepted_as_presentation(captured, mutation):
    packet = captured.authority
    view = d.selected_packet_view(packet, SOURCE)
    evidence = view['reviewer_evidence']['input_evidence']
    if mutation.startswith('dropped'):
        kind = {'dropped_review': 'REVIEW', 'dropped_disposition': 'DISPOSITION', 'dropped_active': 'APPLIED'}[mutation]
        rows = view['recorded_changes']['events']
        rows.remove(next(e for e in rows if e['event'] == kind))
    elif mutation == 'old_prefix':
        proof = evidence['verified_events'][0]['linked_disposition']['originals']
        d._at(proof, d.PREFIX_PATH)['schema'] = d.PREFIX_REFERENCE
    elif mutation == 'old_charter':
        evidence['installed_charter_evidence']['reviewer_evidence']['schema'] = d.CHARTER_REFERENCE
    else:
        view['recorded_changes']['original_chain_value_sha256'] = '0' * 64
    with pytest.raises(ValueError):
        d.validate_selected_packet_view(view, packet, SOURCE)


def test_later_live_history_does_not_rewrite_saved_task_or_receipts(captured, monkeypatch):
    e = captured
    original = encoded(e.campaign)
    view = d.selected_packet_view(e.campaign, SOURCE)
    def forbidden(*args, **kwargs):
        pytest.fail('Saved-packet display/recovery cannot reread mutable current history.')
    monkeypatch.setattr(cr, 'load', forbidden)
    assert d.selected_packet_view(json.loads(original), SOURCE) == view
    assert d.validate_selected_packet_view(view, json.loads(original), SOURCE)


@pytest.mark.parametrize('marker', ['SELECTED_HISTORY_VIEW_VERSION=True',
    'SELECTED_HISTORY_VIEW_VERSION=2', 'SELECTED_HISTORY_VIEW_VERSION=1\nSELECTED_HISTORY_VIEW_VERSION=1',
    'SELECTED_HISTORY_VIEW_VERSION: int = 1', 'if True:\n SELECTED_HISTORY_VIEW_VERSION=1',
    'SELECTED_HISTORY_VIEW_VERSION=1\ndel SELECTED_HISTORY_VIEW_VERSION'])
def test_source_profile_is_literal_unique_and_not_deleted(captured, marker):
    (captured.root / 'orchestrator/hosted_context.py').write_text(marker + '\n')
    with pytest.raises(ValueError, match='SOURCE_BOUND_SELECTED_HISTORY'):
        h.selected_history_profile(captured.root, SOURCE)


def test_legacy_source_rejects_new_capture_and_keeps_old_lossless_route(captured):
    e = captured
    (e.root / 'orchestrator/hosted_context.py').write_text('# Legacy source without marker.\n')
    packet = deepcopy(e.authority)
    with pytest.raises(ValueError, match='SOURCE_PROFILE'):
        h.compose_input(e.root, encoded(packet), prompt_for(e, packet),
                        verified_source=SOURCE, family='claude')
    del packet['scientific_change_history']
    packet['recorded_changes'] = deepcopy(e.current_chain)
    final, current = h.compose_input(e.root, encoded(packet), prompt_for(e, packet),
                                    verified_source=SOURCE, family='claude', prepared_prompt=True)
    assert 'hosted-authority-presentation/v1' in final
    assert 'selected_scientific_presentation' not in final
    assert d.reconstruct_authority(d.authority_view(packet, SOURCE), packet, SOURCE) == packet
    assert current['task_state']['recorded_changes'] == packet['recorded_changes']


def test_changed_or_absent_original_prompt_reference_refuses(captured):
    e = captured
    for packet in [e.authority, e.campaign]:
        body = prompt_for(e, packet)
        marker = h.EVIDENCE_MARKER if packet['trigger'] == 'installed-research-eligibility' else h.CAMPAIGN_EVIDENCE_MARKER
        with pytest.raises(ValueError):
            h.compose_input(e.root, encoded(packet), body.replace(marker, '\nRemoved:\n'),
                            verified_source=SOURCE, family='codex')


def test_native_campaign_grounding_remains_exact_and_actual_roles_match_preflight(captured):
    from orchestrator import hosted_campaign as campaign
    e = captured
    for stage, family, proposal in [('continuation', 'codex', ''), ('review', 'claude', 'selection.json\n'+'x'*30000)]:
        prompt = campaign._typed_prompt(e.root, SOURCE, e.campaign, e.prepared, stage, proposal)
        final, current = h.compose_input(e.root, encoded(e.campaign), prompt,
            verified_source=SOURCE, family=family, output_format='json')
        assert 'Complete external criticism.' in final
        assert 'Original named grounding and target disposition are unchanged' in final
        assert 'original body SHA256' in final
    projected = campaign.campaign_preflight(e.root, SOURCE, e.campaign, supplement=e.supplement)
    assert projected['models'] == projected['admissions'] == 0
    assert [x['family'] for x in projected['stages']] == ['codex', 'claude']
    assert h.INPUT_LIMITS == {'codex': 1048576, 'claude': 900000}


def test_native_authority_constructor_captures_before_original_transport(captured, monkeypatch):
    e = captured
    expected = e.authority
    entry = expected['reviewer_evidence']['catalog_core']
    monkeypatch.setattr(r, '_evidence', lambda config, entry: deepcopy(expected['reviewer_evidence']['input_evidence']))
    monkeypatch.setattr(r, '_decision_contract', lambda bindings: deepcopy(expected['scientific_decision_artifacts']))
    actual = r._packet(e.config, entry, {'source': SOURCE})
    assert actual == expected
    raw = r._transport_bytes({'source': SOURCE}, actual)
    assert json.loads(raw)['packet']['scientific_change_history'] == expected['scientific_change_history']


def test_native_campaign_enqueue_saves_capture_before_preflight_or_admission(captured, monkeypatch, tmp_path):
    from types import SimpleNamespace
    from orchestrator.handover_runtime import Runtime
    e = captured
    entry = {**e.campaign['research_catalog_entry'], 'predecessors': []}
    evidence = e.campaign['reviewer_evidence']
    request = {'source': SOURCE, 'task_id': e.task['task_id'], 'identity': 'd' * 64, 'day': '2026-09-12'}
    monkeypatch.setattr('orchestrator.hosted_campaign_task.installed_research_request',
        lambda *args: (e.task, evidence, request))
    monkeypatch.setattr('orchestrator.research_catalog.selection', lambda *args: ({}, entry))
    monkeypatch.setattr('orchestrator.research_catalog.eligibility', lambda *args: {'synthetic': 'bound'})
    monkeypatch.setattr('orchestrator.continuing_research.supplemental_context',
        lambda *args, **kwargs: e.supplement)
    observed = []
    def preflight(root, source, packet, **kwargs):
        d.validate_current_history(packet, source)
        observed.append(deepcopy(packet))
        raise h.InputTooLarge({'stage': 'review', 'provider_calls': 0, 'reason': 'Synthetic boundary stop'})
    monkeypatch.setattr('orchestrator.hosted_campaign.campaign_preflight', preflight)
    state = tmp_path / 'runtime'
    state.mkdir(mode=0o700)
    runtime = SimpleNamespace(root=e.root, state=state, config=e.config)
    with pytest.raises(h.InputTooLarge):
        Runtime.enqueue_report(runtime, '2026-09-12', [], {'research_request_identity': request['identity']},
            reviewer_evidence=evidence, trigger='installed-research-request', research_task_id=e.task['task_id'])
    saved = list((state / 'tasks').glob('*/packet.json'))
    assert len(saved) == len(observed) == 1
    assert json.loads(saved[0].read_bytes()) == observed[0]
    assert saved[0].with_name('campaign-input-projection-refused.json').is_file()


def test_unknown_adverse_format_and_stale_current_application_refuse_capture(captured):
    e = captured
    packet = deepcopy(e.authority)
    del packet['scientific_change_history']
    packet['reviewer_evidence']['catalog_core']['change_request']['applied_event'] = e.intermediate
    with pytest.raises(ValueError, match='SUPERSEDED_OR_UNKNOWN'):
        d.capture_current_history(e.config, packet)
    state = deepcopy(e.current_chain)
    adverse = next(x for x in state['events'] if x['event'] == 'REVIEW')
    del adverse['payload']['findings']
    with pytest.raises(ValueError):
        d._literal_descriptors(state)


def test_divergent_result_string_is_not_discarded_as_duplicate(captured):
    original = json.loads(captured.raw_response)
    original['result'] = 'Different original observation; preserve it.'
    raw = json.dumps(original)
    shown = d._response_presentation(raw, hashlib.sha256(raw.encode()).hexdigest())
    assert shown['value'] == original
    assert shown['indexed_wrapper_fields'] == []


def test_current_capture_refuses_new_source_against_old_selected_application(captured):
    e = captured
    packet = deepcopy(e.authority)
    del packet['scientific_change_history']
    # The source mismatch is not repaired by mutating source labels or hashes.
    packet['reviewer_evidence']['catalog_core']['source'] = 'f' * 40
    with pytest.raises(ValueError):
        d.capture_current_history({**e.config, 'source': 'f' * 40}, packet)


@pytest.mark.parametrize('kind', ['authority', 'campaign'])
def test_lossless_current_extension_recovers_all_native_events_from_saved_literal(captured, kind, monkeypatch):
    packet = getattr(captured, kind)
    primary = packet['scientific_change_history']['primary']['request_id']
    extension = packet['recorded_changes'] if kind == 'authority' else packet['scientific_change_history']['chains'][primary]
    assert extension['schema'] == d.CURRENT_EXTENSION
    assert len(encoded(extension)) < len(encoded(captured.current_chain))
    before = encoded(packet)
    monkeypatch.setattr(cr, 'load', lambda *args: pytest.fail('No live store access during restoration'))
    restored = d._restore_current(extension, packet, SOURCE)
    assert encoded(restored) == encoded(captured.current_chain)
    assert d.validate_current_history(packet, SOURCE)[primary] == restored
    assert encoded(packet) == before


@pytest.mark.parametrize('change', ['unknown_slot', 'missing_literal', 'wrong_source', 'wrong_historical_head',
    'wrong_current_head', 'wrong_value_hash', 'bool_index', 'suffix_tamper', 'suffix_reorder', 'suffix_missing',
    'suffix_duplicate', 'different_prefix'])
def test_current_chain_extension_near_misses_refuse(captured, change):
    packet = deepcopy(captured.authority)
    ext = packet['recorded_changes']
    proof = packet['reviewer_evidence']['input_evidence']['verified_events'][0]['linked_disposition']['originals']
    if change == 'unknown_slot':
        ext['literal_slot'] = 'untrusted_arbitrary_path'
    elif change == 'missing_literal':
        if ext['literal_slot'] == 'historical_authority':
            del proof['packet']['reviewer_evidence']['preserved_invalid_original']['base_original']['packet']['recorded_changes']
        else:
            del packet['reviewer_evidence']['input_evidence']['verified_events'][0]['linked_disposition']['reviewed_repair']
    elif change == 'wrong_source':
        ext['source'] = '0' * 40
    elif change == 'wrong_historical_head':
        ext['historical_head_sha256'] = '0' * 64
    elif change == 'wrong_current_head':
        ext['current_head_sha256'] = '0' * 64
    elif change == 'wrong_value_hash':
        ext['current_chain_value_sha256'] = '0' * 64
    elif change == 'bool_index':
        ext['event_index'] = True
    elif change == 'suffix_tamper':
        ext['suffix_events'][0]['payload']['modification'] += 'Changed'
    elif change == 'suffix_reorder':
        ext['suffix_events'].reverse()
    elif change == 'suffix_missing':
        ext['suffix_events'].pop()
    elif change == 'suffix_duplicate':
        ext['suffix_events'].append(deepcopy(ext['suffix_events'][-1]))
    else:
        d._at(proof, d.PREFIX_PATH)['events'][0]['payload']['rationale'] = 'Different original'
    with pytest.raises(ValueError):
        d._restore_current(ext, packet, SOURCE)


def driver_versions():
    old = {key: 'Synthetic '+key for key in d.DRIVER_OLD_FIELDS}
    old.update(schema=d.DRIVER_SCHEMA, source=SOURCE, session_id='synthetic-session',
        response_original_sha256='a'*64, findings=[
            {'number':i+1,'original':'Original criticism '+str(i),'classification':'OLD',
             'driver_response':'Old response '+str(i)} for i in range(6)],
        original_questions=['Question'],original_remaining_obligations=['Obligation'],original_resolved_entries=[])
    raw = json.dumps(old)
    old_sha = hashlib.sha256(raw.encode()).hexdigest()
    new = deepcopy(old)
    new.update(utc='New time',previous_response_sha256=old_sha,focused_original_reconciliation={'synthetic':True})
    for index in [1,2,3]:
        new['findings'][index]['classification'] = 'CORRECTED'
        new['findings'][index]['driver_response'] = 'New response '+str(index)
    return old, new


def test_fixed_driver_containment_keeps_every_distinct_old_field():
    old, new = driver_versions()
    difference = d._driver_containment(old, new)
    assert [x['number'] for x in difference['findings']] == [2,3,4]
    assert difference['utc'] == old['utc']
    restored = {key:deepcopy(new[key]) for key in d.DRIVER_OLD_FIELDS}
    restored['utc'] = difference['utc']
    for row in difference['findings']:
        restored['findings'][row['number']-1].update({k:v for k,v in row.items() if k!='number'})
    assert restored == old
    old_raw = json.dumps(old)
    old_sha = hashlib.sha256(old_raw.encode()).hexdigest()
    new_raw = json.dumps(new)
    new_sha = hashlib.sha256(new_raw.encode()).hexdigest()
    shown = d._response_presentations({old_sha:old_raw,new_sha:new_raw})
    delta = shown[old_sha]['value']
    assert delta['current_driver_original_raw_sha256'] == new_sha
    assert delta['old_distinct_fields'] == difference
    assert shown[new_sha]['value'] == new


@pytest.mark.parametrize('change', ['unknown_field','missing_field','original_changed','number_changed',
                                    'shared_field_changed','unexpected_new_field'])
def test_driver_noncontainment_keeps_full_originals(captured, change):
    old, new = driver_versions()
    if change == 'unknown_field':
        old['new_original_limitation'] = 'Preserve me'
    elif change == 'missing_field':
        del new['state']
    elif change == 'original_changed':
        new['findings'][1]['original'] = 'Different criticism'
    elif change == 'number_changed':
        new['findings'][1]['number'] = 9
    elif change == 'shared_field_changed':
        new['original_questions'] = ['Changed question']
    else:
        new['new_obligation'] = 'Preserve this too'
    assert d._driver_containment(old, new) is None


def test_exact_named_request_copies_reference_one_literal_only(captured):
    packet = deepcopy(captured.authority)
    evidence = packet['reviewer_evidence']['input_evidence']
    proof = evidence['verified_events'][0]['linked_disposition']['originals']
    request = 'Exact scientific request.\n'
    # This exercise starts from a newly encoded original, not a forged old proof.
    original = d.reconstruct_evidence(evidence, SOURCE)
    proof = original['verified_events'][0]['linked_disposition']['originals']
    for path in [d.REQUEST_TARGET, *d.REQUEST_COPIES]:
        parent = proof
        for key in path[:-1]:
            parent = parent.setdefault(key,{})
        parent[path[-1]] = request
    proof_before = deepcopy(proof)
    stored = d.encode_evidence(original, SOURCE)
    d._request_presentation(stored, SOURCE)
    selected = stored['verified_events'][0]['linked_disposition']['originals']
    assert d._at(selected,d.REQUEST_TARGET) == request
    for path in d.REQUEST_COPIES:
        reference = d._at(selected,path)
        assert reference['schema'] == d.REQUEST_REFERENCE
        assert reference['request_sha256'] == hashlib.sha256(request.encode()).hexdigest()
        d._put(selected,path,d._at(selected,tuple(reference['literal_path_in_selected_proof'])))
    assert selected == proof_before


def test_nonmatching_named_request_is_not_replaced(captured):
    evidence = deepcopy(captured.authority['reviewer_evidence']['input_evidence'])
    proof = evidence['verified_events'][0]['linked_disposition']['originals']
    proof['packet']['campaign_task']['request'] = 'Unchanged target'
    proof['packet']['research_catalog_entry'] = {'request':{'task':{'request':'Different current request'}}}
    before = deepcopy(proof['packet']['research_catalog_entry'])
    d._request_presentation(evidence,SOURCE)
    assert proof['packet']['research_catalog_entry'] == before

@pytest.mark.parametrize('raw', [
    '{"findings":["first"],"findings":["different"]}',
    '{"outer":{"findings":["first"],"findings":["different"]}}',
    '{"findings":[NaN]}', 'Not a JSON evidence body.',
])
def test_response_projection_refuses_duplicate_or_non_json_bodies(raw):
    sha = hashlib.sha256(raw.encode()).hexdigest()
    with pytest.raises(ValueError):
        d._response_presentations({sha: raw})


def test_duplicate_result_keys_remain_literal_and_cannot_establish_output_equality():
    body = {'type':'result','session_id':'synthetic','is_error':False,'subtype':'success',
        'modelUsage':{},'structured_output':{'findings':['last']},
        'result':'{"findings":["first"],"findings":["last"]}'}
    raw = json.dumps(body)
    shown = d._response_presentation(raw, hashlib.sha256(raw.encode()).hexdigest())
    assert shown['value'] == body
    assert shown['indexed_wrapper_fields'] == []


def c9_body():
    part = {'scope':'material-deployment-source-part-a','session':'synthetic-a',
        'actual_structured_verdict':'REQUEST_CHANGES','requested_model':'synthetic',
        'assistant_message_models':['synthetic'],'usage_model_keys':['synthetic'],
        'native_qualifying_approval':False,
        'findings':[{'number':1,'original_finding':'Entire criticism',
            'driver_disposition_kind':'AGREE','driver_response':'Entire response'}],
        'fable_assistant_content':[[{'type':'thinking','thinking':'','signature':'synthetic-signature'},
            {'type':'text','text':'Meaningful actual refusal.'}]],
        'provider_fallback_original_rows':[], 'originals':{'path':'synthetic archive'}}
    second = deepcopy(part);second['scope']='material-deployment-source-part-b';second['session']='synthetic-b'
    return {'schema':'private-c9-v4-review-factual-disposition/v1','status':'ADVERSE_UNQUALIFIED',
        'source':SOURCE,'proposal_sha256':'b'*64,'disposition':'Preserve adverse result',
        'actual_remaining_conditions':['No acceptance'],'completed_authority_not_new_requests':[],
        'parts':{'part-a':part,'part-b':second},'source_evidence':{'path':'synthetic archive'}}


def test_declared_c9_body_preserves_all_criticism_identity_conditions_and_actual_text():
    body=c9_body();raw=json.dumps(body)
    selected=d._response_presentation(raw,hashlib.sha256(raw.encode()).hexdigest())
    assert selected['value']['actual_remaining_conditions'] == body['actual_remaining_conditions']
    for name, part in selected['value']['parts'].items():
        assert part['findings'] == body['parts'][name]['findings']
        assert part['native_qualifying_approval'] is False
        assert part['fable_assistant_content'][0][1]['text'] == 'Meaningful actual refusal.'
        assert part['fable_assistant_content'][0][0] == {'type':'thinking','thinking':''}
    assert 'signature' in json.dumps(selected['indexed_wrapper_fields'])
    assert 'source_evidence' in selected['indexed_wrapper_fields']
    assert body['parts']['part-a']['fable_assistant_content'][0][0]['signature'] == 'synthetic-signature'


@pytest.mark.parametrize('form',['driver','direction','c9'])
def test_declared_additional_bodies_require_exact_event_links(form):
    if form=='driver':
        body={'source':SOURCE,'review_session':'synthetic-session',
            'findings':[{'finding':'Entire criticism','disposition':'Entire response'}]}
        payload={'source':SOURCE,'response_to_review_session':'synthetic-session'}
        name='ASTRA_FINDING_DISPOSITION.json'
    elif form=='direction':
        output={'reviewed_commit':SOURCE,'scope':'synthetic-direction','verdict':'REQUEST_CHANGES',
                'findings':['Entire criticism']}
        body={'type':'result','session_id':'synthetic-session','structured_output':output}
        payload={'source':SOURCE,'review_session':'synthetic-session',
            'review_scope':'synthetic-direction','review_verdict':'REQUEST_CHANGES'}
        name='response.json'
    else:
        body=c9_body();payload={'source':SOURCE,'recorded_criticism':'REQUEST_CHANGES_NONQUALIFYING_MIXED_IDENTITY',
            'qualifying_review':False};name='DISPOSITION_DATA.json'
    raw=json.dumps(body);sha=hashlib.sha256(raw.encode()).hexdigest()
    descriptor={'artifact':'evidence/'+sha+'-'+name,'sha256':sha,'size':len(raw)}
    field='evidence' if form=='c9' else 'review_evidence'
    payload[field]=[descriptor,{'artifact':'evidence/'+'c'*64+'-execution.json','sha256':'c'*64,'size':1}]
    event={'event':'DISPOSITION','identity':'e'*64,'payload':payload}
    rows=d._literal_descriptors({'request':{'identity':'a'*64},'events':[event]})
    assert len(rows)==1 and rows[0]['descriptor']==descriptor
    d._response_event_binding(event,descriptor,raw)
    changed=deepcopy(event);changed['payload']['source']='f'*40
    with pytest.raises(ValueError):d._response_event_binding(changed,descriptor,raw)
    wrong=deepcopy(descriptor);wrong['artifact']='evidence/not-the-declared-sha-'+name
    with pytest.raises(ValueError):d._response_event_binding(event,wrong,raw)
    duplicate=deepcopy(event);duplicate['payload'][field].append(descriptor)
    with pytest.raises(ValueError):d._literal_descriptors({'request':{'identity':'a'*64},'events':[duplicate]})


@pytest.mark.parametrize('mutation',['unknown_field','nested_list','path_mismatch','missing_size'])
def test_unknown_descriptor_forms_remain_literal(mutation):
    row={'artifact':'evidence/'+'a'*64+'-original.json','sha256':'a'*64,'size':100}
    if mutation=='unknown_field':row['other']='Preserve this field'
    elif mutation=='nested_list':row=[row]
    elif mutation=='path_mismatch':row['artifact']='evidence/different-original.json'
    else:del row['size']
    assert d._selected_descriptor(row)==row


def test_complete_applied_and_non_named_descriptor_fields_are_never_compacted(captured):
    original=deepcopy(captured.current_chain['events'][-1])
    original['payload']['evidence']={'artifact':'evidence/'+'a'*64+'-original.json','sha256':'a'*64,'size':100}
    assert d._selected_event(original)==original
    event=deepcopy(captured.current_chain['events'][-2])
    event['payload']['unknown_evidence']=deepcopy(original['payload']['evidence'])
    shown=d._selected_event(event)
    assert shown['payload']['unknown_evidence']==event['payload']['unknown_evidence']
    assert shown['recorded_at_utc']==event['recorded_at_utc']


def test_two_context_copies_have_exact_terminal_literals_and_preserve_distinct_values(captured):
    e=captured
    evidence=deepcopy(d._selected_evidence(e.campaign,SOURCE))
    proof=evidence['verified_events'][0]['linked_disposition']['originals']
    proof['packet']['continuing_context']={'actual':'unchanged continuing context'}
    proof['packet']['research_eligibility']={'actual':'unchanged eligibility'}
    proof['eligibility']=deepcopy(proof['packet']['research_eligibility'])
    view={'continuing_context':deepcopy(proof['packet']['continuing_context'])}
    originals=deepcopy((view,proof))
    d._context_presentation(view,evidence,SOURCE)
    for parent,name in [(view,'continuing_context'),(proof,'eligibility')]:
        ref=parent[name]
        target=d._at(proof,tuple(ref['literal_path_in_selected_proof']))
        assert d._sha(target)==ref['value_sha256']
        assert target==originals[0 if name=='continuing_context' else 1][name]
    distinct={'continuing_context':{'actual':'later continuing state differs'}}
    d._context_presentation(distinct,evidence,SOURCE)
    assert distinct=={'continuing_context':{'actual':'later continuing state differs'}}


def test_unknown_response_fields_are_preserved_and_never_treated_as_archive_metadata():
    body=c9_body()
    body['additional_criticism']='Distinct unrecognized top-level criticism.'
    body['parts']['part-a']['additional_response']='Distinct unrecognized part response.'
    raw=json.dumps(body)
    shown=d._response_presentation(raw,hashlib.sha256(raw.encode()).hexdigest())
    assert shown['value']['additional_criticism']==body['additional_criticism']
    assert shown['value']['parts']['part-a']['additional_response']==body['parts']['part-a']['additional_response']
    wrapper={'type':'result','session_id':'synthetic','is_error':False,'subtype':'success',
        'modelUsage':{},'structured_output':{'findings':['Entire finding']},
        'result':'{"findings":["Entire finding"]}','additional_error':'Distinct unrecognized native error.'}
    raw=json.dumps(wrapper)
    shown=d._response_presentation(raw,hashlib.sha256(raw.encode()).hexdigest())
    assert shown['value']['additional_error']==wrapper['additional_error']


def test_single_backslash_descriptor_stays_literal():
    row = {'artifact': 'evidence/' + 'a' * 64 + '-odd' + chr(92) + 'name.json',
           'sha256': 'a' * 64, 'size': 100}
    original = deepcopy(row)
    assert d._selected_descriptor(row) == original
    assert row == original


@pytest.fixture
def bootstrap(captured):
    e = captured
    marker = e.root / 'orchestrator/hosted_context.py'
    marker.write_text(marker.read_text() + 'INVESTIGATOR_HISTORY_VERSION = 1\n')
    packet = deepcopy(e.authority)
    evidence = deepcopy(packet['reviewer_evidence']['input_evidence'])
    evidence.pop('disposition_presentation')
    evidence['installed_charter_evidence'] = {'reviewer_evidence': {'science': 'Original bootstrap evidence.'}}
    event = {'kind': 'BOOTSTRAP', 'identity': '1'*64, 'original_sha256': '2'*64}
    core = {k:v for k,v in evidence['investigator_wake'].items() if k != 'identity'}
    core['events'] = [event]
    from orchestrator.handover_coordinator import digest
    evidence['investigator_wake'] = {**core, 'identity': digest(core)}
    evidence['verified_events'] = [{'event': event, 'description': 'Synthetic protected template bootstrap.'}]
    packet['reviewer_evidence']['input_evidence'] = evidence
    packet['recorded_changes'] = deepcopy(e.current_chain)
    del packet['scientific_change_history']
    e.bootstrap_original = deepcopy(packet)
    e.bootstrap_packet = d.capture_current_history(e.config, packet)
    return e


@pytest.mark.parametrize('family', ['codex', 'claude'])
def test_bootstrap_captures_full_criticism_and_uses_existing_selection(bootstrap, family):
    e = bootstrap
    packet = e.bootstrap_packet
    assert packet['scientific_change_history']['schema'] == d.CURRENT_INVESTIGATOR_HISTORY
    assert d.validate_current_history(packet, SOURCE)
    view = d.selected_packet_view(packet, SOURCE)
    assert view['reviewer_evidence'] == packet['reviewer_evidence']
    assert {r['identity'] for r in view['recorded_changes']['events'] if r['event']=='APPLIED'} == {e.latest}
    final, context = h.compose_input(e.root, encoded(packet), prompt_for(e, packet),
        verified_source=SOURCE, family=family, prepared_prompt=True)
    assert 'Complete external criticism.' in final and 'Complete literal response.' in final
    assert 'Archived implementation' not in final
    raw = h.context_bytes(e.root, context, SOURCE)
    assert json.loads(raw) == context
    assert packet['reviewer_evidence'] == e.bootstrap_original['reviewer_evidence']
    assert h.INPUT_LIMITS == {'codex':1048576, 'claude':900000}


@pytest.mark.parametrize('mutation', ['missing_body','changed_body','superseded_application','wrong_source','changed_wake'])
def test_bootstrap_preserves_original_and_authority_guards(bootstrap, mutation):
    e = bootstrap; packet = deepcopy(e.bootstrap_packet)
    if mutation == 'missing_body': packet['scientific_change_history']['response_originals'].clear()
    elif mutation == 'changed_body': packet['scientific_change_history']['response_originals'][e.response_sha] += 'altered'
    elif mutation == 'superseded_application':
        packet['scientific_change_history']['primary']['applied_event'] = e.intermediate
        packet['reviewer_evidence']['catalog_core']['change_request']['applied_event'] = e.intermediate
    elif mutation == 'wrong_source': packet['scientific_change_history']['source'] = '0'*40
    else: packet['reviewer_evidence']['input_evidence']['investigator_wake']['identity'] = '0'*64
    with pytest.raises(ValueError): d.selected_packet_view(packet, SOURCE)


def test_bootstrap_legacy_inputs_unchanged_and_new_capture_rejected(bootstrap):
    e = bootstrap; marker = e.root / 'orchestrator/hosted_context.py'
    marker.write_text(marker.read_text().replace('INVESTIGATOR_HISTORY_VERSION = 1\n',''))
    assert d.capture_current_history(e.config,e.bootstrap_original) == e.bootstrap_original
    with pytest.raises(ValueError,match='INVESTIGATOR_HISTORY_SOURCE_PROFILE_REQUIRED'):
        h.compose_input(e.root, encoded(e.bootstrap_packet), prompt_for(e,e.bootstrap_packet),
            verified_source=SOURCE,family='codex')


@pytest.mark.parametrize('marker', ['INVESTIGATOR_HISTORY_VERSION=True','INVESTIGATOR_HISTORY_VERSION=2',
    'INVESTIGATOR_HISTORY_VERSION=1\nINVESTIGATOR_HISTORY_VERSION=1',
    'INVESTIGATOR_HISTORY_VERSION: int = 1','if True:\n INVESTIGATOR_HISTORY_VERSION=1',
    'INVESTIGATOR_HISTORY_VERSION=1\ndel INVESTIGATOR_HISTORY_VERSION'])
def test_investigator_profile_rejects_invalid_bindings(captured,marker):
    (captured.root/'orchestrator/hosted_context.py').write_text(marker+'\n')
    with pytest.raises(ValueError,match='SOURCE_BOUND_INVESTIGATOR_HISTORY'):
        h.investigator_history_profile(captured.root,SOURCE)


def test_terminal_markdown_original_is_hash_bound_and_literal(bootstrap):
    e=bootstrap; state=deepcopy(e.current_chain)
    raw=b'# Original terminal review\nREQUEST_CHANGES\nKeep this exact finding.\n'
    sha=hashlib.sha256(raw).hexdigest()
    descriptor={'artifact':'evidence/'+sha+'-006-review.md','sha256':sha,'size':len(raw)}
    append(state,'REVIEW',{'applied_event':e.latest,'verdict':'REQUEST_CHANGES',
        'rationale':'Preserve terminal original.','affected_results':['Synthetic'],
        'original_review':{'response_sha256':sha},
        'review_evidence':{'original_report':descriptor,'verified_session_and_scope':{'status':'separate'}}})
    write_state(Path(e.config['change_request_store']),state,{descriptor['artifact']:raw})
    packet=deepcopy(e.bootstrap_original);packet['recorded_changes']=state
    captured=d.capture_current_history(e.config,packet)
    shown=d.selected_packet_view(captured,SOURCE)
    assert shown['scientific_change_history']['response_originals'][sha]['text'].encode()==raw
    assert captured['scientific_change_history']['response_originals'][sha].encode()==raw
    changed=deepcopy(captured);changed['scientific_change_history']['response_originals'][sha]+='altered'
    with pytest.raises(ValueError):d.selected_packet_view(changed,SOURCE)


def test_bad_json_is_not_reclassified_as_terminal_markdown():
    with pytest.raises(ValueError):d._response_presentations({'a'*64:'{"a":1,"a":2}'})
    with pytest.raises(ValueError):d._response_presentations({'a'*64:'Not a JSON response.'})
