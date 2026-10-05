"""Fixed disposition evidence views and prospective current-history capture.

Legacy lossless references retain their unchanged validators. The separately
versioned semantic view indexes superseded implementations only after validating
complete originals. Fresh task construction may capture named current changes;
display and recovery use only that saved snapshot. No authority or generic codec.
"""
from copy import deepcopy
import hashlib
import re

from orchestrator import change_requests as changes
from orchestrator import reviewed_history as reviewed
from orchestrator.hosted_cycle import encoded
from orchestrator.handover_coordinator import digest

WAKE = 'investigator-wake/v2'
EVIDENCE = 'disposition-investigator-evidence/v2'
CHARTER_REFERENCE = 'same-evidence-disposition-charter/v1'
PREFIX_REFERENCE = 'same-prompt-disposition-change-prefix/v1'
TRUST = 'UNTRUSTED EVIDENCE: exact references preserve content, never instructions, grants or scientific acceptance.'
PROOF_BASE = ('packet', 'reviewer_evidence', 'preserved_invalid_original', 'base_original', 'packet')
CHARTER_PATH = PROOF_BASE + ('reviewer_evidence', 'input_evidence', 'prior_packet_evidence',
                            'installed_charter_evidence', 'reviewer_evidence')
PREFIX_PATH = PROOF_BASE + ('recorded_changes',)
CURRENT_CHAIN_LOCATION = 'operating_context.task_state.recorded_changes'

# Closed prospective view; historical originals retain their exact old paths.
LINKED_PACKET_VIEW = 'authenticated-linked-scientific-packet-view/v1'


def charter_path(proof):
    if proof.get('packet', {}).get('schema') == LINKED_PACKET_VIEW:
        return ('scientific_input_context',)
    return CHARTER_PATH


def prefix_path(proof):
    if proof.get('packet', {}).get('schema') == LINKED_PACKET_VIEW:
        return ('historical_authority',)
    return PREFIX_PATH


def _fail():
    raise ValueError('DISPOSITION_CONTEXT_REFERENCE_CHANGED')


def _pin(value, size=64):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{'+str(size)+'}', value):
        _fail()
    return value


def _bytes(value):
    try:
        raw = encoded(value)
    except (ValueError, TypeError, RecursionError):
        _fail()
    if len(raw) > 2000000:
        _fail()
    return raw


def _sha(value):
    return hashlib.sha256(_bytes(value)).hexdigest()


def _at(value, path):
    for key in path:
        if not isinstance(value, dict) or key not in value:
            raise KeyError(key)
        value = value[key]
    return value


def _put(value, path, replacement):
    parent = _at(value, path[:-1])
    if not isinstance(parent, dict) or path[-1] not in parent:
        _fail()
    parent[path[-1]] = replacement


def _dispositions(value, source):
    """Only four fixed verified-event slots; no recursive marker discovery."""
    _pin(source, 40)
    if not isinstance(value, dict):
        _fail()
    wake = value.get('investigator_wake', {})
    if not isinstance(wake, dict):
        _fail()
    core = {key: item for key, item in wake.items() if key != 'identity'}
    if (set(core) != {'schema', 'source', 'template_sha256', 'events', 'day'}
            or core['schema'] != WAKE or core['source'] != source
            or wake.get('identity') != digest(core)):
        _fail()
    rows = value.get('verified_events')
    if (not isinstance(rows, list) or not 1 <= len(rows) <= 4
            or not isinstance(core['events'], list) or len(rows) != len(core['events'])):
        _fail()
    found = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or row.get('event') != core['events'][index]:
            _fail()
        if not isinstance(row['event'], dict):
            _fail()
        from orchestrator.investigator_eligibility_replacement import disposition_event
        bound_event = disposition_event(row, source)
        if bound_event is not None:
            linked = row.get('linked_disposition', {})
            if not isinstance(linked, dict):
                _fail()
            proof = linked.get('originals', {})
            if (not isinstance(proof, dict) or proof.get('origin_task') != bound_event.get('identity')
                    or linked.get('result_sha256') != bound_event.get('original_sha256')):
                _fail()
            _pin(proof['origin_task'])
            _pin(linked['result_sha256'])
            found.append((index, proof))
    return found


def _charter_reference(source, index, proof, target):
    if (not isinstance(target, dict)
            or target.get('schema') in (CHARTER_REFERENCE, PREFIX_REFERENCE)):
        _fail()
    return {'schema': CHARTER_REFERENCE, 'source': source, 'event_index': index,
            'origin_task': proof['origin_task'], 'original_proof_sha256': _sha(proof),
            'literal_path_in_original_proof': list(charter_path(proof)), 'target_sha256': _sha(target),
            'trust': TRUST}


def encode_evidence(original, source):
    """Keep full proof literally; alias only identical OUTER charter evidence."""
    value = deepcopy(original)
    found = _dispositions(value, source)
    if not found:
        return value
    if 'disposition_presentation' in value:
        _fail()
    charter = value.get('installed_charter_evidence', {})
    outer = charter.get('reviewer_evidence') if isinstance(charter, dict) else None
    if isinstance(outer, dict) and outer.get('schema') == CHARTER_REFERENCE:
        _fail()
    for index, proof in found:
        try:
            target = _at(proof, charter_path(proof))
        except KeyError:
            continue  # Other valid original shapes stay fully literal.
        if isinstance(outer, dict) and _bytes(outer) == _bytes(target):
            charter['reviewer_evidence'] = _charter_reference(source, index, proof, target)
            break
    value['disposition_presentation'] = {'schema': EVIDENCE, 'source': source,
                                         'original_evidence_sha256': _sha(original)}
    if _bytes(reconstruct_evidence(value, source)) != _bytes(original):
        _fail()
    return value


def reconstruct_evidence(stored, source):
    """Reconstruct all fields, without external reads or reference chaining."""
    value = deepcopy(stored)
    found = dict(_dispositions(value, source))
    marker = value.pop('disposition_presentation', None)
    if not found:
        if marker is not None:
            _fail()
        return value
    if (not isinstance(marker, dict) or set(marker) != {'schema', 'source', 'original_evidence_sha256'}
            or marker['schema'] != EVIDENCE or marker['source'] != source):
        _fail()
    _pin(marker['original_evidence_sha256'])
    charter = value.get('installed_charter_evidence', {})
    outer = charter.get('reviewer_evidence') if isinstance(charter, dict) else None
    if isinstance(outer, dict) and outer.get('schema') == CHARTER_REFERENCE:
        index = outer.get('event_index')
        if type(index) is not int or index not in found:
            _fail()
        proof = found[index]
        try:
            target = _at(proof, charter_path(proof))
        except KeyError:
            _fail()
        if _bytes(outer) != _bytes(_charter_reference(source, index, proof, target)):
            _fail()
        charter['reviewer_evidence'] = deepcopy(target)
    if _sha(value) != marker['original_evidence_sha256']:
        _fail()
    return value


# Original evidence is not a model-facing packet. Keep _bytes/_sha and every
# compact/packet guard at 2MB. The original reader uses the existing 32MB material
# aggregate vocabulary, the capture record count, and the unchanged native record
# ceiling; it does not make any original eligible for scientific use by itself.
ORIGINAL_CHAIN_BYTES = 32_000_000


def _chain_bytes(state):
    """Bound complete original serialization; _chain still checks its integrity.

    Referenced representations keep their original compact 2MB bound. Per-record
    checks precede aggregate serialization, preventing an unbounded history value
    from becoming a new allocation or bypassing the native 100KB record ceiling.
    The returned encoding is unchanged, so historical original-value hashes match.
    """
    if reviewed.is_reference(state):
        return _bytes(state)
    from orchestrator.scientific_evidence_access import MAX_RECORDS, MAX_RECORD_BYTES
    if (not isinstance(state, dict) or set(state) != {'request','events','head_sha256'}
            or not isinstance(state['events'], list)
            or len(state['events']) + 1 > MAX_RECORDS):
        raise ValueError('DISPOSITION_ORIGINAL_CHAIN_COUNT_OR_SHAPE')
    try:
        total = 0
        for value in (state['request'], *state['events']):
            if not isinstance(value, dict) or len(changes.encoded(value) + b'\n') > MAX_RECORD_BYTES:
                raise ValueError('DISPOSITION_ORIGINAL_CHAIN_RECORD_BOUND')
            total += len(encoded(value))
            if total > ORIGINAL_CHAIN_BYTES:
                raise ValueError('DISPOSITION_ORIGINAL_CHAIN_AGGREGATE_BOUND')
        raw = encoded(state)
        if len(raw) > ORIGINAL_CHAIN_BYTES:
            raise ValueError('DISPOSITION_ORIGINAL_CHAIN_AGGREGATE_BOUND')
        return raw
    except (TypeError, RecursionError) as error:
        raise ValueError('DISPOSITION_ORIGINAL_CHAIN_ENCODING') from error


def _chain_sha(state):
    return hashlib.sha256(_chain_bytes(state)).hexdigest()


def _chain(state):
    """Recompute the native canonical request/event hash chain, not its label."""
    if reviewed.is_reference(state):
        return reviewed.validate(state)
    if (not isinstance(state, dict) or set(state) != {'request', 'events', 'head_sha256'}
            or not isinstance(state['events'], list)):
        _fail()
    _chain_bytes(state)
    try:
        request = changes._request(state['request'])
        previous = hashlib.sha256(changes.encoded(request) + b'\n').hexdigest()
        prior = []
        identities = []
        for event in state['events']:
            core = {key: value for key, value in event.items() if key != 'identity'}
            if (event.get('schema') != changes.EVENT_SCHEMA
                    or event.get('request_identity') != request['identity']
                    or type(event.get('sequence')) is not int or event['sequence'] != len(prior)+1
                    or event.get('previous_sha256') != previous
                    or event.get('identity') != hashlib.sha256(changes.encoded(core)).hexdigest()):
                _fail()
            changes.actor(event['actor'])
            changes._transition(prior, event['event'], event['payload'])
            previous = hashlib.sha256(changes.encoded(event) + b'\n').hexdigest()
            prior.append(event)
            identities.append(event['identity'])
        if _pin(state['head_sha256']) != previous:
            _fail()
        return identities
    except (KeyError, TypeError, AttributeError):
        _fail()


def prefix_reference(historical, current, source):
    """Only an exact fully checked prefix of the same literal current chain."""
    _pin(source, 40)
    old_ids = _chain(historical)
    _chain(current)
    count = len(old_ids)
    exact = (reviewed.matches_prefix(historical, current) if reviewed.is_reference(current) else
             len(historical['events']) == len(current['events'][:count])
             and all(encoded(old) == encoded(new) for old, new in
                     zip(historical['events'], current['events'][:count])))
    if (not count or count > len(reviewed.index(current))
            or _bytes(historical['request']) != _bytes(current['request']) or not exact):
        _fail()
    return {'schema': PREFIX_REFERENCE, 'source': source,
            'literal_location': CURRENT_CHAIN_LOCATION,
            'request_identity': historical['request']['identity'],
            'request_sha256': hashlib.sha256(changes.encoded(historical['request']) + b'\n').hexdigest(),
            'event_count': count, 'event_identities': old_ids,
            'historical_head_sha256': historical['head_sha256'],
            'current_head_sha256': current['head_sha256'],
            'original_state_sha256': _chain_sha(historical), 'trust': TRUST}


def _restore_prefix(reference, current, source):
    count = reference.get('event_count')
    if (type(count) is not int or not isinstance(current, dict)
            or not isinstance(current.get('events'), list)
            or not 1 <= count <= len(current['events'])):
        _fail()
    historical = {'request': deepcopy(current['request']),
                  'events': deepcopy(current['events'][:count]),
                  'head_sha256': reference.get('historical_head_sha256')}
    if _bytes(reference) != _bytes(prefix_reference(historical, current, source)):
        _fail()
    return historical


def _authority_evidence(packet, source):
    """Return only new versioned DISPOSITION input evidence, never other tasks."""
    _pin(source, 40)
    _bytes(packet)
    if not isinstance(packet, dict) or packet.get('trigger') != 'installed-research-eligibility':
        return None
    reviewer = packet.get('reviewer_evidence', {})
    if not isinstance(reviewer, dict):
        _fail()
    catalog = reviewer.get('catalog_core', {})
    if not isinstance(catalog, dict) or not isinstance(catalog.get('request', {}), dict):
        _fail()
    task = catalog.get('request', {}).get('task', {})
    if not isinstance(task, dict):
        _fail()
    if task.get('schema') != 'investigator-task/v1':
        return None
    evidence = reviewer.get('input_evidence', {})
    if not isinstance(evidence, dict) or not isinstance(evidence.get('investigator_wake', {}), dict):
        _fail()
    if evidence.get('investigator_wake', {}).get('schema') != WAKE:
        return None
    if catalog.get('source') != source:
        _fail()
    return evidence


def authority_view(packet, source):
    """Fresh hosted text only. Keep every packet key and current chain literal."""
    view = deepcopy(packet)
    evidence = _authority_evidence(view, source)
    if evidence is None:
        return view
    reconstruct_evidence(evidence, source)
    current = view.get('recorded_changes')
    for _, proof in _dispositions(evidence, source):
        try:
            historical = _at(proof, prefix_path(proof))
        except KeyError:
            continue
        if (isinstance(historical, dict) and isinstance(current, dict)
                and historical.get('request', {}).get('identity') == current.get('request', {}).get('identity')):
            _put(proof, prefix_path(proof), prefix_reference(historical, current, source))
    return view


def reconstruct_authority(view, original_packet, source):
    """Restore from this SAME literal chain, then compare the complete packet."""
    restored = deepcopy(view)
    evidence = _authority_evidence(restored, source)
    if evidence is not None:
        for _, proof in _dispositions(evidence, source):
            try:
                reference = _at(proof, prefix_path(proof))
            except KeyError:
                continue
            if isinstance(reference, dict) and reference.get('schema') == PREFIX_REFERENCE:
                _put(proof, prefix_path(proof), _restore_prefix(reference, restored.get('recorded_changes'), source))
        reconstruct_evidence(evidence, source)
    if (_bytes(restored) != _bytes(original_packet)
            or _bytes(view) != _bytes(authority_view(original_packet, source))):
        _fail()
    return restored


# Prospective semantic presentation. These schemas never denote stored evidence
# or an inverse that can reconstruct omitted implementation payloads.
SELECTED_CHAIN = 'selected-scientific-change-history/v1'
SELECTED_PREFIX = 'same-prompt-selected-change-prefix/v1'
SELECTED_EVIDENCE = 'selected-disposition-evidence/v1'
SELECTED_CHARTER = 'same-selected-evidence-charter/v1'
SELECTED_NOTICE = (
    'Semantic selection, not a lossless original-chain encoding. Only superseded APPLIED '
    'payloads are indexed; active applications at every supplied historical/current head, '
    'all AUTHORIZED, REVIEW and DISPOSITION payloads remain complete, with declared fixed metadata views. Supersession does not '
    'resolve criticism. Indexed originals and external evidence descriptors are not '
    'inspected bodies or approval. Full records remain required where applicable; use the '
    'original protected packet and canonical change store for human inspection.')


def _active(state):
    _chain(state)
    if reviewed.is_reference(state):
        return reviewed.active(reviewed.index(state))
    applied = {e['identity'] for e in state['events'] if e['event'] == 'APPLIED'}
    superseded = {identity for e in state['events'] if e['event'] == 'APPLIED'
                  for identity in e['payload'].get('supersedes_applied_events', [])}
    return applied - superseded


def _selected_chain(state, source, packet_sha256, protected):
    active = _active(state)
    if reviewed.is_reference(state):
        if not (protected & set(reviewed.validate(state))) <= {e['identity'] for e in state['events']}:
            _fail()
        return reviewed.presentation(state)
    identities = {e['identity'] for e in state['events']}
    if not active <= protected:
        _fail()
    omitted = [e for e in state['events']
               if e['event'] == 'APPLIED' and e['identity'] not in protected]
    return {'schema': SELECTED_CHAIN, 'source': source,
        'request': deepcopy(state['request']), 'original_head_sha256': state['head_sha256'],
        'original_chain_value_sha256': _chain_sha(state), 'original_packet_sha256': packet_sha256,
        'digest_encoding': 'hosted_cycle.encoded of the complete chain value; not a raw-file SHA',
        'original_event_count': len(state['events']),
        'active_applied_events': sorted(active),
        'retained_historical_active_events': sorted((protected & identities) - active),
        'event_metadata': {'schema': changes.EVENT_SCHEMA, 'request_identity': state['request']['identity'],
            'notice': 'For non-APPLIED events only, schema/request_identity equal these checked defaults. '
                'previous_sha256 stays indexed in the bound original chain; identity, sequence, actor, '
                'timestamp and complete payload remain. This selected event is not a native hash-chain row.'},
        'evidence_descriptor_rule': 'Only named payload.evidence/review_evidence/response_evidence slots '
            'with exact {name,sha256,size} restore artifact as evidence/{sha256}-{name}. '
            'Unknown descriptors remain literal; descriptor presence is not body inspection.',
        'events': [_selected_event(e) for e in state['events']
                   if e['event'] != 'APPLIED' or e['identity'] in protected],
        'superseded_applied_index': [{'sequence': e['sequence'], 'identity': e['identity']}
                                     for e in omitted],
        'original_store_location': 'Configured private change store / request.identity / events',
        'original_event_name': '{sequence:04d}-{identity}.json',
        'notice': SELECTED_NOTICE}


def _selected_event(event):
    """Checked event display, with only three named descriptor fields."""
    result = deepcopy(event)
    if event['event'] == 'APPLIED':
        return result
    # _selected_chain calls _active/_chain before any metadata changes.
    for key in ('schema', 'request_identity', 'previous_sha256'):
        del result[key]
    payload = result['payload']
    for key in ('evidence', 'review_evidence', 'response_evidence'):
        value = payload.get(key)
        if isinstance(value, list):
            payload[key] = [_selected_descriptor(row) for row in value]
        elif isinstance(value, dict):
            payload[key] = _selected_descriptor(value)
    return result


def _selected_descriptor(row):
    if not isinstance(row, dict) or set(row) != {'artifact', 'sha256', 'size'}:
        return deepcopy(row)
    sha, path, size = row['sha256'], row['artifact'], row['size']
    if (not isinstance(sha, str) or re.fullmatch('[0-9a-f]{64}', sha) is None
            or not isinstance(path, str) or not path.startswith('evidence/' + sha + '-')
            or type(size) is not int or size < 0):
        return deepcopy(row)
    name = path[len('evidence/' + sha + '-'):]
    if not name or name in ('.', '..') or '/' in name or '\\' in name:
        return deepcopy(row)
    return {'name': name, 'sha256': sha, 'size': size}


def _selected_evidence(packet, source):
    evidence = _authority_evidence(packet, source)
    if evidence is not None:
        return evidence
    if packet.get('trigger') != 'installed-research-request':
        return None
    task = packet.get('campaign_task', {})
    if not isinstance(task, dict) or task.get('schema') != 'investigator-task/v1':
        return None
    evidence = packet.get('reviewer_evidence', {})
    if not isinstance(evidence, dict):
        _fail()
    if not isinstance(evidence.get('investigator_wake', {}), dict):
        _fail()
    if evidence.get('investigator_wake', {}).get('schema') != WAKE:
        return None
    from orchestrator.hosted_campaign import _campaign_task
    _campaign_task(packet, source)
    return evidence


def selected_packet_view(original, source):
    """Select only named disposition chains after checking complete originals.

    No filesystem lookup, generic recursion, preview substitution or cap change.
    Historical prefix sharing refers to selected literals, never absent originals.
    """
    _pin(source, 40)
    from orchestrator import current_scientific_input
    if current_scientific_input.is_current(original):
        # Display only. Actual consuming paths reauthenticate the complete native
        # capture before model use; no digest is accepted as an original here.
        return current_scientific_input.presentation(original, source)
    packet_sha = _sha(original)
    view = deepcopy(original)
    evidence = _selected_evidence(view, source)
    if evidence is None:
        return None
    reconstructed = reconstruct_evidence(evidence, source)
    found = _dispositions(evidence, source)
    if not found and original.get('scientific_change_history', {}).get('schema') != CURRENT_INVESTIGATOR_HISTORY:
        return None

    states = validate_current_history(original, source)
    capture = view['scientific_change_history']
    primary = capture['primary']['request_id']
    # Fixed current capture slots and their fixed historical counterparts.
    current_slots = {}
    if view['trigger'] == 'installed-research-eligibility':
        current_slots[primary] = (view, ('recorded_changes',), CURRENT_CHAIN_LOCATION)
    for identity in capture['chains']:
        current_slots[identity] = (capture['chains'], (identity,),
            'operating_context.task_state.scientific_change_history.chains[' + identity + ']')
    slots = [(parent, path, states[identity], identity)
             for identity, (parent, path, _) in current_slots.items()]
    for index, proof in found:
        try:
            historical = _at(proof, prefix_path(proof))
        except KeyError:
            historical = None
        if historical is not None:
            _chain(historical)
            slots.append((proof, prefix_path(proof), historical, None))
        linked = evidence['verified_events'][index]['linked_disposition']
        repair = linked.get('reviewed_repair')
        if repair is not None:
            _chain(repair)
            slots.append((linked, ('reviewed_repair',), repair, None))
    protected = {}
    for _, _, state, _ in slots:
        protected.setdefault(state['request']['identity'], set()).update(_active(state))
    literal_originals = {sha: raw for sha, raw in capture['response_originals'].items()
                         if isinstance(raw, str)}
    references = {sha: raw for sha, raw in capture['response_originals'].items()
                  if not isinstance(raw, str)}
    capture['response_originals'] = {**_response_presentations(literal_originals, literal_text={
        row['descriptor']['sha256'] for row in capture['response_references']
        if row['descriptor']['artifact'].endswith('.md') and row['descriptor']['sha256'] in literal_originals}),
        **references}
    if reviewed.is_reference(states[primary]):
        capture['response_originals'] = reviewed.report_views(states[primary],
            original['scientific_change_history']['response_originals'],
            capture['response_originals'], capture['response_references'], states=states)
    _share_direction_findings(capture['response_originals'])
    field_selection = (reviewed.event_field_selection(states[primary], states)
                       if reviewed.is_reference(states[primary]) else {})
    def select(state, identity):
        shown = _selected_chain(state, source, packet_sha, protected[identity])
        shown = reviewed.selected_event_fields(shown, field_selection.get(identity, {}))
        _share_review_event_findings(shown, capture['response_originals'])
        return shown
    selected_current = {identity: select(state, identity)
                        for identity, state in states.items()}
    for parent, path, state, current_identity in slots:
        identity = state['request']['identity']
        selected = select(state, identity)
        if current_identity is None and identity in states:
            prefix_reference(state, states[identity], source)
            selected = {'schema': SELECTED_PREFIX, 'source': source,
                'literal_location': current_slots[identity][2],
                'through_sequence': len(reviewed.index(state)),
                'historical_active_applied_events': sorted(_active(state)),
                'original_head_sha256': state['head_sha256'],
                'original_chain_value_sha256': _chain_sha(state),
                'selected_chain_sha256': _sha(selected),
                'current_selected_chain_sha256': _sha(selected_current[identity]),
                'meaning': 'Read retained events and indexed identities through this sequence '
                    'from the literal selected current history. This is the historical SELECTED '
                    'view, not reconstruction of the original chain or omitted APPLIED payloads.'}
        _put(parent, path, selected)
    capture['schema'] = 'selected-current-scientific-changes/v1'
    capture['notice'] = SELECTED_NOTICE
    _request_presentation(evidence, source)
    _context_presentation(view, evidence, source)
    if not found:
        # No disposition proof was supplied: keep every scientific evidence field
        # literal, applying only the existing current-chain administrative view.
        if _bytes(evidence) != _bytes(_selected_evidence(original, source)):
            _fail()
        return view

    # Stored v2 aliases bind an original proof. Their exact validation happened
    # above; a changed selected proof requires a separate, honest display schema.
    old_marker = evidence.pop('disposition_presentation')
    charter = evidence.get('installed_charter_evidence', {})
    outer = charter.get('reviewer_evidence') if isinstance(charter, dict) else None
    if isinstance(outer, dict) and outer.get('schema') == CHARTER_REFERENCE:
        index = outer['event_index']
        proof = dict(_dispositions(evidence, source))[index]
        target = _at(proof, charter_path(proof))
        if _sha(target) != outer['target_sha256']:
            _fail()
        charter['reviewer_evidence'] = {'schema': SELECTED_CHARTER, 'source': source,
            'event_index': index, 'literal_path_in_selected_proof': list(charter_path(proof)),
            'target_sha256': _sha(target),
            'meaning': 'Only this unchanged charter literal is shared within the selected proof. '
                       'No original proof or evidence reconstruction is claimed.'}
    evidence['disposition_presentation'] = {'schema': SELECTED_EVIDENCE, 'source': source,
        'original_packet_sha256': packet_sha,
        'stored_evidence_sha256': _sha(_selected_evidence(original, source)),
        'original_evidence_sha256': old_marker['original_evidence_sha256'],
        'notice': SELECTED_NOTICE}
    if _sha(reconstructed) != old_marker['original_evidence_sha256']:
        _fail()
    return view


def validate_selected_packet_view(view, original, source):
    """Bind deterministic selected output to a separately retained full original."""
    expected = selected_packet_view(original, source)
    if expected is None or _bytes(view) != _bytes(expected):
        _fail()
    return {'schema': 'selected-scientific-packet-binding/v1', 'source': source,
            'original_packet_sha256': _sha(original), 'selected_packet_sha256': _sha(view),
            'notice': SELECTED_NOTICE}


CURRENT_HISTORY = 'current-scientific-change-capture/v1'
CURRENT_LINKED_HISTORY = 'current-linked-scientific-change-capture/v2'
CURRENT_INVESTIGATOR_HISTORY = 'current-investigator-change-capture/v1'


def _primary_change(packet):
    if packet.get('trigger') == 'registered-formal-scientific-decision':
        entry = packet.get('formal_request', {})
    elif packet.get('trigger') == 'installed-research-eligibility':
        entry = packet['reviewer_evidence']['catalog_core']
    else:
        entry = packet.get('research_catalog_entry', {})
    binding = entry.get('change_request') if isinstance(entry, dict) else None
    if (not isinstance(binding, dict) or set(binding) != {'request_id', 'applied_event'}):
        _fail()
    _pin(binding['request_id'])
    _pin(binding['applied_event'])
    return binding


def _applicable_requests(packet, source, *, investigator=False):
    evidence = _selected_evidence(packet, source)
    if evidence is None:
        return None
    found = _dispositions(evidence, source)
    if not found and not investigator:
        return None
    reconstruct_evidence(evidence, source)
    primary = _primary_change(packet)
    requests = {primary['request_id']}
    for index, _ in _dispositions(evidence, source):
        repair = evidence['verified_events'][index]['linked_disposition'].get('reviewed_repair')
        if repair is not None:
            _chain(repair)
            requests.add(repair['request']['identity'])
    return primary, sorted(requests)


def _literal_descriptors(state):
    """Only named adverse-response and driver-response fields, never a walker."""
    descriptors = []
    for event in state['events']:
        payload = event['payload']
        rows = []
        if event['event'] == 'REVIEW' and payload['verdict'] == 'REQUEST_CHANGES':
            # Some native records already carry the complete findings literally.
            # Older original-review records explicitly bind their response file.
            original = payload.get('original_review')
            # A native terminal record may bind the same complete report directly
            # in its named evidence slot, without a redundant response digest.
            # Preserve the whole criticism; all descriptor/hash checks below apply.
            evidence = payload.get('review_evidence')
            report = evidence.get('original_report') if isinstance(evidence, dict) else None
            if original is None and isinstance(report, dict) and 'sha256' in report:
                original = {'response_sha256': report['sha256']}
            if isinstance(original, dict) and 'response_sha256' in original:
                expected = _pin(original['response_sha256'])
                evidence = payload['review_evidence']
                if isinstance(evidence, dict):
                    # Native terminal-review records bind the report in this one
                    # named slot; session qualification is separate provenance.
                    if 'original_report' in evidence:
                        report = evidence['original_report']
                        if (not isinstance(report, dict)
                                or not str(report.get('artifact', '')).endswith('.md')):
                            _fail()
                        evidence = [report]
                    else:
                        evidence = [evidence]
                if not isinstance(evidence, list):
                    _fail()
                rows = [r for r in evidence if isinstance(r, dict) and r.get('sha256') == expected]
                if len(rows) != 1:
                    _fail()
            elif not isinstance(payload.get('findings'), list) or not payload['findings']:
                # Unknown external criticism representation is not a preview grant.
                _fail()
        if event['event'] == 'DISPOSITION' and 'response_evidence' in payload:
            response = payload['response_evidence']
            rows += response if isinstance(response, list) else [response]
        if event['event'] == 'DISPOSITION':
            # Declared native response/adverse record forms, not filename crawling
            # or an inference that an unlinked record's criticism is resolved.
            suffix = None
            field = 'review_evidence'
            if payload.get('response_to_review_session'):
                suffix = '-ASTRA_FINDING_DISPOSITION.json'
            elif payload.get('review_verdict') == 'REQUEST_CHANGES':
                suffix = '-response.json'
            elif (payload.get('recorded_criticism') == 'REQUEST_CHANGES_NONQUALIFYING_MIXED_IDENTITY'
                    and payload.get('qualifying_review') is False):
                suffix = '-DISPOSITION_DATA.json'
                field = 'evidence'
            if suffix is not None:
                candidates = payload.get(field)
                if isinstance(candidates, dict):
                    candidates = [candidates]
                if not isinstance(candidates, list):
                    _fail()
                selected = [row for row in candidates if isinstance(row, dict)
                    and isinstance(row.get('artifact'), str) and row['artifact'].endswith(suffix)]
                if len(selected) != 1:
                    _fail()
                rows += selected
        for row in rows:
            if (not isinstance(row, dict) or not {'artifact', 'sha256'} <= set(row)
                    or set(row) - {'artifact', 'sha256', 'size'}):
                _fail()
            _pin(row['sha256'])
            if (not isinstance(row['artifact'], str) or not row['artifact'].startswith('evidence/')
                    or '\\' in row['artifact'] or '..' in row['artifact'].split('/')):
                _fail()
            descriptors.append({'request': state['request']['identity'],
                'event': event['identity'], 'descriptor': deepcopy(row)})
    return descriptors


def capture_current_history(config, packet):
    """Capture applicable complete originals once, before immutable task binding."""
    from pathlib import Path
    source = config['source']
    from orchestrator import current_scientific_input
    prepared = current_scientific_input.preparation_view(config, packet)
    if (current_scientific_input.has_references(prepared, source)
            or current_scientific_input.has_current_plan(config, prepared)):
        return current_scientific_input.capture_history(config, packet)
    from orchestrator.hosted_context import investigator_history_profile
    investigator = investigator_history_profile(config['source_root'], source) == 1
    applicable = _applicable_requests(packet, source, investigator=investigator)
    if applicable is None:
        return packet
    without_disposition = not _dispositions(_selected_evidence(packet, source), source)
    if 'scientific_change_history' in packet:
        _fail()
    primary, identities = applicable
    states = {identity: changes.load(Path(config['change_request_store']) / identity)
              for identity in identities}
    primary_state = states[primary['request_id']]
    active = _active(primary_state)
    if primary['applied_event'] not in active:
        raise ValueError('SELECTED_APPLICATION_SUPERSEDED_OR_UNKNOWN')
    applied = next(e for e in primary_state['events'] if e['identity'] == primary['applied_event'])
    if applied['payload']['result_binding'].get('source') != source:
        raise ValueError('SELECTED_APPLICATION_SOURCE_CHANGED')
    result = deepcopy(packet)
    if packet['trigger'] == 'installed-research-eligibility':
        expected = primary_state
        if reviewed.is_reference(packet['recorded_changes']):
            from orchestrator.linked_disposition_input import prepare_primary_for_packet
            expected = prepare_primary_for_packet(primary_state,
                _selected_evidence(packet, source), source, primary['applied_event'])
        if _bytes(packet['recorded_changes']) != _bytes(expected):
            _fail()
        del states[primary['request_id']]
    all_states = [primary_state] + [s for key, s in states.items() if key != primary['request_id']]
    originals = {}
    references = []
    for state in all_states:
        for row in _literal_descriptors(state):
            raw = changes._read(Path(config['change_request_store']) / row['request']
                                / row['descriptor']['artifact'])
            sha = hashlib.sha256(raw).hexdigest()
            if sha != row['descriptor']['sha256'] or len(raw) != row['descriptor'].get('size', len(raw)):
                _fail()
            try:
                literal = raw.decode('utf-8')
            except UnicodeError:
                _fail()
            originals.setdefault(sha, literal)
            if originals[sha].encode('utf-8') != raw:
                _fail()
            references.append(row)
    result['scientific_change_history'] = {'schema': CURRENT_INVESTIGATOR_HISTORY if without_disposition else CURRENT_HISTORY, 'source': source,
        'primary': deepcopy(primary), 'chains': states,
        'response_originals': originals, 'response_references': references,
        'notice': 'Captured complete applicable current chains and exact adverse/driver response '
                  'originals before task identity. Recovery uses this snapshot, not later live history.'}
    protected = set()
    for history in _literal_histories(packet, source).values():
        if history['request']['identity'] == primary['request_id']:
            protected.update(_active(history))
    primary_state = reviewed.capture(primary_state, primary['applied_event'], protected=protected)
    # The exact source application may also bind the linked result's historical
    # repair prefix. Preserve every historical active application in its current
    # chain, plus every adverse/authority/response record and unreviewed tail.
    from orchestrator.linked_disposition_input import validate as validate_linked
    plan = applied['payload']['result_binding'].get('linked_disposition_input')
    for index, proof in _dispositions(_selected_evidence(packet, source), source):
        linked = _selected_evidence(packet, source)['verified_events'][index]['linked_disposition']
        if 'input_presentation' not in linked:
            continue
        bounds = validate_linked(linked, plan, primary['applied_event'], source)
        repair = linked['reviewed_repair']
        identity = repair['request']['identity']
        if identity == primary['request_id']:
            _fail()  # this fixed route has distinct primary and repair requests
        states[identity] = reviewed.capture_linked_history(states[identity],
            bounds['reviewed_repair'], primary['applied_event'], protected=_active(repair))
    if primary['request_id'] in states:
        states[primary['request_id']] = primary_state
    if packet['trigger'] == 'installed-research-eligibility':
        result['recorded_changes'] = _current_extension(primary_state, packet, source)
    result['scientific_change_history']['chains'] = {
        identity: _current_extension(state, packet, source) for identity, state in states.items()}
    checked_states = validate_current_history(result, source)
    report_plan = applied['payload']['result_binding'].get('historical_report_selection', {})
    if report_plan.get('schema') == 'reviewed-multi-request-source-report-selection/v1':
        # Every original above was natively retrieved and authenticated. The
        # independently reviewed exact selection may reference source-settled
        # reports; unselected criticism and all conditions remain literal.
        capture = result['scientific_change_history']
        capture['response_originals'] = reviewed.report_views(checked_states[primary['request_id']],
            capture['response_originals'], capture['response_originals'],
            capture['response_references'], states=checked_states)
        capture['schema'] = CURRENT_LINKED_HISTORY
        capture['notice'] = ('Captured applicable native chains and eagerly authenticated every '
            'original response. Exactly reviewed source-report references retain native '
            'request/event/artifact hashes. Unselected bodies remain literal. No indexed '
            'body is claimed model-inspected; saved recovery retains this exact snapshot.')
        validate_current_history(result, source)
    return result


def validate_current_history(packet, source):
    """Check the saved finite snapshot and original-byte bodies without live I/O."""
    capture = packet.get('scientific_change_history')
    schema = capture.get('schema') if isinstance(capture, dict) else None
    investigator = schema == CURRENT_INVESTIGATOR_HISTORY
    applicable = _applicable_requests(packet, source, investigator=investigator)
    if applicable is None:
        _fail()
    if investigator and _dispositions(_selected_evidence(packet, source), source):
        _fail()
    primary, identities = applicable
    if (not isinstance(capture, dict) or set(capture) != {
            'schema', 'source', 'primary', 'chains', 'response_originals', 'response_references', 'notice'}
            or schema not in (CURRENT_HISTORY, CURRENT_INVESTIGATOR_HISTORY, CURRENT_LINKED_HISTORY) or capture['source'] != source
            or capture['primary'] != primary or not isinstance(capture['chains'], dict)
            or not isinstance(capture['response_originals'], dict)
            or not isinstance(capture['response_references'], list)):
        _fail()
    states = dict(capture['chains'])
    if packet['trigger'] == 'installed-research-eligibility':
        if primary['request_id'] in states:
            _fail()
        states[primary['request_id']] = packet['recorded_changes']
    if sorted(states) != identities:
        _fail()
    states = {identity: _restore_current(state, packet, source) for identity, state in states.items()}
    for identity, state in states.items():
        if state['request']['identity'] != identity:
            _fail()
    state = states[primary['request_id']]
    if primary['applied_event'] not in _active(state):
        raise ValueError('SELECTED_APPLICATION_SUPERSEDED_OR_UNKNOWN')
    applied = next(e for e in state['events'] if e['identity'] == primary['applied_event'])
    if applied['payload']['result_binding'].get('source') != source:
        raise ValueError('SELECTED_APPLICATION_SOURCE_CHANGED')
    from orchestrator.linked_disposition_input import validate as validate_linked
    plan = applied['payload']['result_binding'].get('linked_disposition_input')
    referenced = set()
    for index, proof in _dispositions(_selected_evidence(packet, source), source):
        linked = _selected_evidence(packet, source)['verified_events'][index]['linked_disposition']
        if 'input_presentation' not in linked:
            continue
        bounds = validate_linked(linked, plan, primary['applied_event'], source)
        identity = linked['reviewed_repair']['request']['identity']
        current = states[identity]
        if (current.get('schema') != reviewed.HISTORICAL_SCHEMA
                or current['binding_application'] != primary['applied_event']
                or current['boundary'] != bounds['reviewed_repair']):
            _fail()
        referenced.add(identity)
    if any(s.get('schema') == reviewed.HISTORICAL_SCHEMA and identity not in referenced
           for identity, s in states.items()):
        _fail()
    expected = [row for state in [states[primary['request_id']]] + [
        states[k] for k in sorted(states) if k != primary['request_id']]
        for row in _literal_descriptors(state)]
    if capture['response_references'] != expected:
        _fail()
    if set(capture['response_originals']) != {r['descriptor']['sha256'] for r in expected}:
        _fail()
    selected_originals = {}
    if schema == CURRENT_LINKED_HISTORY:
        plan = applied['payload']['result_binding'].get('historical_report_selection', {})
        if plan.get('schema') != 'reviewed-multi-request-source-report-selection/v1':
            _fail()
        selected_originals = reviewed.report_views(state, capture['response_originals'],
            capture['response_originals'], expected, states=states)
    for row in expected:
        sha = row['descriptor']['sha256']
        literal = capture['response_originals'][sha]
        if isinstance(literal, dict):
            if (schema != CURRENT_LINKED_HISTORY or sha not in plan['references']
                    or literal != selected_originals.get(sha)):
                _fail()
            continue  # Explicit authenticated reference, never a claimed literal body.
        if not isinstance(literal, str):
            _fail()
        raw = literal.encode('utf-8')
        if hashlib.sha256(raw).hexdigest() != sha or len(raw) != row['descriptor'].get('size', len(raw)):
            _fail()
        event = next(e for e in states[row['request']]['events'] if e['identity'] == row['event'])
        _response_event_binding(event, row['descriptor'], literal)
    # Current states must extend every supplied historical state of that request.
    evidence = _selected_evidence(packet, source)
    for index, proof in _dispositions(evidence, source):
        histories = []
        try:
            histories.append(_at(proof, prefix_path(proof)))
        except KeyError:
            pass
        repair = evidence['verified_events'][index]['linked_disposition'].get('reviewed_repair')
        if repair is not None:
            histories.append(repair)
        for history in histories:
            identity = history['request']['identity']
            if identity in states:
                prefix_reference(history, states[identity], source)
    return states


def _response_event_binding(event, descriptor, literal):
    """Bind the three declared archival body forms to their actual event."""
    if event['event'] != 'DISPOSITION':
        return
    payload = event['payload']
    basename = descriptor['artifact'].rsplit('/', 1)[-1]
    names = ('ASTRA_FINDING_DISPOSITION.json', 'response.json', 'DISPOSITION_DATA.json')
    name = next((name for name in names if basename.endswith('-' + name)), None)
    if name is not None and descriptor['artifact'] != 'evidence/' + descriptor['sha256'] + '-' + name:
        _fail()
    if payload.get('response_to_review_session') and name == 'ASTRA_FINDING_DISPOSITION.json':
        body = _response_object(literal)
        if (not isinstance(body, dict) or body.get('source') != payload.get('source')
                or body.get('review_session') != payload['response_to_review_session']
                or not isinstance(body.get('findings'), list) or not body['findings']
                or any(not isinstance(row, dict) or not {'finding','disposition'} <= set(row)
                       for row in body['findings'])):
            _fail()
    elif payload.get('review_verdict') == 'REQUEST_CHANGES' and name == 'response.json':
        body = _response_object(literal)
        if not isinstance(body, dict):
            _fail()
        output = body.get('structured_output')
        if (body.get('type') != 'result' or body.get('session_id') != payload.get('review_session')
                or not isinstance(output, dict) or output.get('scope') != payload.get('review_scope')
                or output.get('reviewed_commit') != payload.get('source')
                or output.get('verdict') != payload['review_verdict']
                or not isinstance(output.get('findings'), list) or not output['findings']):
            _fail()
    elif (payload.get('recorded_criticism') == 'REQUEST_CHANGES_NONQUALIFYING_MIXED_IDENTITY'
            and name == 'DISPOSITION_DATA.json'):
        body = _response_object(literal)
        if (not isinstance(body, dict) or body.get('schema') != 'private-c9-v4-review-factual-disposition/v1'
                or body.get('source') != payload.get('source') or not isinstance(body.get('parts'), dict)
                or set(body['parts']) != {'part-a','part-b'}):
            _fail()
        for name, part in body['parts'].items():
            if (not isinstance(part, dict) or part.get('scope') != 'material-deployment-source-' + name
                    or part.get('actual_structured_verdict') != 'REQUEST_CHANGES'
                    or part.get('native_qualifying_approval') is not False
                    or not isinstance(part.get('findings'), list) or not part['findings']):
                _fail()
            for index, row in enumerate(part['findings'], 1):
                if (not isinstance(row, dict) or type(row.get('number')) is not int or row['number'] != index
                        or any(not isinstance(row.get(key), str)
                            for key in ('original_finding','driver_disposition_kind','driver_response'))):
                    _fail()

def _response_presentation(raw, original_sha256):
    """One fixed native result wrapper; complete driver objects stay complete."""
    import json
    try:
        value = _response_object(raw)
    except (ValueError, TypeError):
        _fail()
    if not isinstance(value, dict):
        _fail()
    selected = value
    omitted = []
    if value.get('type') == 'result' and isinstance(value.get('structured_output'), dict):
        try:
            same = _response_object(value.get('result', '')) == value['structured_output']
        except (ValueError, TypeError):
            same = False
        if same:
            keys = {'session_id', 'is_error', 'subtype', 'modelUsage', 'structured_output'}
            if not keys <= set(value):
                _fail()
            archival = {'type','result','api_error_status','duration_api_ms','duration_ms',
                'fast_mode_disabled_reason','fast_mode_state','num_turns','permission_denials',
                'stop_reason','terminal_reason','time_to_request_ms','total_cost_usd','ttft_ms',
                'ttft_stream_ms','usage','uuid'}
            omitted = sorted(set(value) & archival)
            selected = {key: value[key] for key in value if key not in omitted}
    if value.get('schema') == 'private-c9-v4-review-factual-disposition/v1':
        keys = {'schema', 'status', 'source', 'proposal_sha256', 'disposition',
                'actual_remaining_conditions', 'completed_authority_not_new_requests'}
        part_keys = {'scope', 'session', 'actual_structured_verdict', 'requested_model',
                     'assistant_message_models', 'usage_model_keys', 'native_qualifying_approval', 'findings'}
        if not keys <= set(value) or not isinstance(value.get('parts'), dict) or set(value['parts']) != {'part-a','part-b'}:
            _fail()
        archive_top = {'actions_by_this_task','created_utc','existing_route','prepared_by',
                       'selected_applications','source_evidence'}
        archive_part = {'originals','provider_fallback_original_rows'}
        parts = {}
        for name, part in value['parts'].items():
            if (not isinstance(part, dict) or not part_keys <= set(part)
                    or not isinstance(part['findings'], list)):
                _fail()
            for row in part['findings']:
                if not isinstance(row, dict) or not {'number','original_finding','driver_disposition_kind','driver_response'} <= set(row):
                    _fail()
            parts[name] = {key: deepcopy(part[key]) for key in part if key not in archive_part}
            content = part.get('fable_assistant_content')
            if not isinstance(content, list) or any(not isinstance(message, list) for message in content):
                _fail()
            visible = []
            for message in content:
                blocks = []
                for block in message:
                    if not isinstance(block, dict):
                        _fail()
                    # Preserve every actual text/refusal and even thinking text.
                    # Only the typed cryptographic signature is archival metadata.
                    shown = deepcopy(block)
                    if shown.get('type') == 'thinking' and isinstance(shown.get('signature'), str):
                        del shown['signature']
                    blocks.append(shown)
                visible.append(blocks)
            parts[name]['fable_assistant_content'] = visible
        selected = {key: deepcopy(value[key]) for key in value if key not in archive_top}
        selected['parts'] = parts
        omitted = sorted(set(value) & archive_top)
        omitted += ['parts.' + name + '.' + key for name,part in value['parts'].items()
                    for key in sorted(set(part) & archive_part)]
        omitted += ['parts.' + name + '.fable_assistant_content[*][*].signature (thinking blocks only)'
                    for name in parts]
    return {'schema': 'selected-original-response/v1',
        'original_raw_sha256': original_sha256, 'original_bytes': len(raw.encode('utf-8')),
        'value': selected, 'indexed_wrapper_fields': omitted,
        'notice': 'Complete structured review output or complete driver response object. '
            'Only a proven duplicate result string, declared archival originals or transport/accounting fields '
            'may be indexed. Raw original remains separately preserved, not claimed inspected '
            'or requalified. No findings, questions, obligations or responses are truncated.'}


CURRENT_EXTENSION = 'same-packet-current-change-extension/v1'
REVIEWED_EXTENSION = 'same-packet-reviewed-change-extension/v1'
REQUEST_REFERENCE = 'same-selected-disposition-request/v1'
RESPONSE_FIELD_REFERENCE = 'same-selected-original-response-field/v1'
DRIVER_SCHEMA = 'material-review-findings-and-driver-response/v1'
DRIVER_OLD_FIELDS = {
    'schema', 'source', 'session_id', 'state', 'utc', 'findings',
    'model_attribution_only', 'native_reason', 'native_receipt_status', 'new_mechanical_defect',
    'original_questions', 'original_remaining_obligations', 'original_resolved_entries',
    'protocol_original_sha256', 'provider_verdict', 'response_original_sha256'}
REQUEST_TARGET = ('packet', 'campaign_task', 'request')
REQUEST_COPIES = (
    ('packet', 'research_catalog_entry', 'request', 'task', 'request'),
    ('packet', 'reviewer_evidence', 'preserved_invalid_original', 'base_original',
     'entry', 'request', 'task', 'request'),
    PROOF_BASE + ('reviewer_evidence', 'catalog_core', 'request', 'task', 'request'),
    PROOF_BASE + ('reviewer_evidence', 'input_evidence', 'original_selection', 'successor', 'request'),
    ('packet', 'reviewer_evidence', 'preserved_invalid_original', 'entry', 'request', 'task', 'request'),
)


def _literal_histories(packet, source):
    """Only the existing proof's historical authority and reviewed-repair slots."""
    evidence = _selected_evidence(packet, source)
    if evidence is None:
        _fail()
    result = {}
    for index, proof in _dispositions(evidence, source):
        try:
            history = _at(proof, prefix_path(proof))
        except KeyError:
            history = None
        if history is not None:
            _chain(history)
            result[(index, 'historical_authority')] = history
        repair = evidence['verified_events'][index]['linked_disposition'].get('reviewed_repair')
        if repair is not None:
            _chain(repair)
            result[(index, 'reviewed_repair')] = repair
    return result


def _current_extension(state, packet, source):
    """Losslessly store native suffix events against one unchanged literal prefix."""
    _chain(state)
    if reviewed.is_reference(state):
        return _reviewed_extension(state, packet, source)
    candidates = []
    for (index, slot), history in _literal_histories(packet, source).items():
        if history['request']['identity'] == state['request']['identity']:
            prefix_reference(history, state, source)
            candidates.append((len(history['events']), index, slot, history))
    if not candidates:
        return deepcopy(state)
    count, index, slot, history = max(candidates, key=lambda row: (row[0], -row[1], row[2]))
    return {'schema': CURRENT_EXTENSION, 'source': source,
        'event_index': index, 'literal_slot': slot,
        'request_identity': state['request']['identity'],
        'historical_head_sha256': history['head_sha256'],
        'historical_chain_value_sha256': _chain_sha(history),
        'current_head_sha256': state['head_sha256'],
        'current_chain_value_sha256': _chain_sha(state),
        'suffix_events': deepcopy(state['events'][count:]),
        'meaning': 'Exact complete current chain equals this same packet historical literal plus '
            'these ordered native suffix events. Value hashes use hosted_cycle.encoded, '
            'not claims about raw native event files. Both native chains are verified before selection.'}


def _restore_current(value, packet, source):
    if isinstance(value, dict) and value.get('schema') == REVIEWED_EXTENSION:
        return _restore_reviewed_extension(value, packet, source)
    if not isinstance(value, dict) or value.get('schema') != CURRENT_EXTENSION:
        _chain(value)
        return deepcopy(value)
    if (set(value) != {'schema', 'source', 'event_index', 'literal_slot', 'request_identity',
            'historical_head_sha256', 'historical_chain_value_sha256', 'current_head_sha256',
            'current_chain_value_sha256', 'suffix_events', 'meaning'}
            or value['source'] != source or type(value['event_index']) is not int
            or not isinstance(value['suffix_events'], list)):
        _fail()
    history = _literal_histories(packet, source).get((value['event_index'], value['literal_slot']))
    if history is None:
        _fail()
    state = {'request': deepcopy(history['request']),
        'events': deepcopy(history['events']) + deepcopy(value['suffix_events']),
        'head_sha256': value['current_head_sha256']}
    _chain(state)
    if _bytes(value) != _bytes(_current_extension(state, packet, source)):
        _fail()
    return state


def _request_presentation(evidence, source):
    """Five named request copies refer only to one unchanged terminal string."""
    for index, proof in _dispositions(evidence, source):
        try:
            target = _at(proof, REQUEST_TARGET)
        except KeyError:
            continue
        if not isinstance(target, str):
            continue
        reference = {'schema': REQUEST_REFERENCE, 'source': source,
            'event_index': index, 'literal_path_in_selected_proof': list(REQUEST_TARGET),
            'request_sha256': hashlib.sha256(target.encode('utf-8')).hexdigest(),
            'meaning': 'Exact unchanged request literal in this same selected proof; no new request or authority.'}
        for path in REQUEST_COPIES:
            try:
                original = _at(proof, path)
            except KeyError:
                continue
            if isinstance(original, str) and original == target:
                _put(proof, path, deepcopy(reference))



def _context_presentation(view, evidence, source):
    """Two demonstrated context copies refer to fixed unchanged proof literals."""
    for index, proof in _dispositions(evidence, source):
        for parent, name, terminal in (
                (view, 'continuing_context', ('packet', 'continuing_context')),
                (proof, 'eligibility', ('packet', 'research_eligibility'))):
            try:
                target = _at(proof, terminal)
            except KeyError:
                continue
            value = parent.get(name)
            if (not isinstance(value, dict) or not isinstance(target, dict)
                    or _bytes(value) != _bytes(target)):
                continue
            parent[name] = {'schema': 'same-selected-disposition-context/v1', 'source': source,
                'event_index': index, 'literal_path_in_selected_proof': list(terminal),
                'value_sha256': _sha(target),
                'meaning': 'This exact unchanged context value is literal in the named same-prompt proof slot. '
                           'No new eligibility, scientific result or authority; original packet remains bound.'}

def _driver_containment(older, newer):
    """Complete newer driver plus finite old overrides, only on proved equality."""
    if (not isinstance(older, dict) or not isinstance(newer, dict)
            or older.get('schema') != DRIVER_SCHEMA or newer.get('schema') != DRIVER_SCHEMA
            or set(older) != DRIVER_OLD_FIELDS
            or set(newer) != DRIVER_OLD_FIELDS | {'previous_response_sha256', 'focused_original_reconciliation'}
            or not isinstance(older['findings'], list) or not isinstance(newer['findings'], list)
            or len(older['findings']) != len(newer['findings'])):
        return None
    for key in DRIVER_OLD_FIELDS - {'utc', 'findings'}:
        if older[key] != newer[key]:
            return None
    overrides = []
    for index, (old, new) in enumerate(zip(older['findings'], newer['findings']), 1):
        fields = {'number', 'original', 'classification', 'driver_response'}
        if (not isinstance(old, dict) or not isinstance(new, dict)
                or set(old) != fields or set(new) != fields
                or type(old['number']) is not int or old['number'] != index
                or type(new['number']) is not int or new['number'] != index
                or old['original'] != new['original']):
            return None
        changed = {key: deepcopy(old[key]) for key in ('classification', 'driver_response')
                   if old[key] != new[key]}
        if changed:
            overrides.append({'number': index, **changed})
    restored = {key: deepcopy(newer[key]) for key in DRIVER_OLD_FIELDS}
    restored['utc'] = deepcopy(older['utc'])
    for row in overrides:
        restored['findings'][row['number']-1].update({k: deepcopy(v) for k,v in row.items() if k != 'number'})
    if _bytes(restored) != _bytes(older):
        _fail()
    return {'utc': deepcopy(older['utc']), 'findings': overrides}


def _response_field_reference(sha, path, value):
    return {'schema': RESPONSE_FIELD_REFERENCE, 'response_original_raw_sha256': sha,
        'literal_path_in_selected_response': ['value', 'structured_output', *path],
        'value_sha256': _sha(value),
        'meaning': 'Exact full value is literal in this same selected original response; no truncation or resolution.'}


def _response_presentations(originals, *, literal_text=()):
    """Finite driver versions and their exact named original-review fields."""
    import json
    literal_text = set(literal_text)
    if not literal_text <= set(originals):
        _fail()
    decoded = {sha: _response_object(raw) for sha, raw in originals.items() if sha not in literal_text}
    shown = {sha: _response_presentation(raw, sha) for sha, raw in originals.items() if sha not in literal_text}
    shown.update({sha: {'schema': 'literal-original-review-text/v1',
        'original_raw_sha256': sha, 'text': originals[sha],
        'meaning': 'Complete unchanged UTF-8 original report text; no inferred resolution or approval.'}
        for sha in sorted(literal_text)})
    # A declared predecessor must be present, unique and exact. Unknown shapes
    # stay entirely literal; they cannot acquire a containment claim.
    predecessors = {}
    for sha, value in decoded.items():
        previous = value.get('previous_response_sha256') if isinstance(value, dict) else None
        if isinstance(previous, str) and previous in decoded:
            predecessors.setdefault(previous, []).append(sha)
    for old_sha, successors in predecessors.items():
        if len(successors) != 1:
            continue
        new_sha = successors[0]
        difference = _driver_containment(decoded[old_sha], decoded[new_sha])
        if difference is not None:
            shown[old_sha]['value'] = {'schema': 'selected-previous-driver-response/v1',
                'current_driver_original_raw_sha256': new_sha,
                'original_driver_original_raw_sha256': old_sha,
                'old_distinct_fields': difference,
                'meaning': 'Shared values are in the selected current driver version; retain these '
                    'exact earlier overrides. First read its fixed original-response field references, '
                    'then apply these old fields to compare the complete older decoded response. '
                    'Every distinct older statement remains; no raw-byte reconstruction, review '
                    'inspection, criticism resolution or approval is claimed.'}
    for sha, original in decoded.items():
        if not isinstance(original, dict):
            continue
        value = shown[sha]['value']
        if value.get('schema') == 'selected-previous-driver-response/v1':
            continue
        if original.get('schema') == DRIVER_SCHEMA:
            response_sha = original.get('response_original_sha256')
            response = decoded.get(response_sha)
            if not isinstance(response, dict) or not isinstance(response.get('structured_output'), dict):
                continue
            output = response['structured_output']
            # The terminal target must actually remain a full structured literal.
            if shown[response_sha]['value'].get('structured_output') != output:
                _fail()
            pairs = [('original_questions', 'questions'),
                     ('original_remaining_obligations', 'remaining_obligations'),
                     ('original_resolved_entries', 'resolved')]
            for local, terminal in pairs:
                if local in original and terminal in output and original[local] == output[terminal]:
                    value[local] = _response_field_reference(response_sha, [terminal], output[terminal])
            findings = output.get('findings')
            if isinstance(findings, list) and isinstance(original.get('findings'), list):
                for index, row in enumerate(original['findings']):
                    if (index < len(findings) and isinstance(row, dict)
                            and row.get('number') == index+1 and row.get('original') == findings[index]):
                        value['findings'][index]['original'] = _response_field_reference(
                            response_sha, ['findings', index], findings[index])
        elif original.get('schema') == 'private-material-finding-reconciliation/v1':
            descriptor = original.get('actual_originals', {}).get('response.json', {})
            response_sha = descriptor.get('sha256') if isinstance(descriptor, dict) else None
            response = decoded.get(response_sha)
            if not isinstance(response, dict) or not isinstance(response.get('structured_output'), dict):
                continue
            findings = response['structured_output'].get('findings')
            if not isinstance(findings, list) or not isinstance(original.get('findings'), list):
                continue
            for index, row in enumerate(original['findings']):
                if not isinstance(row, dict) or not isinstance(row.get('reviewer_original'), str):
                    continue
                matches = [i for i, finding in enumerate(findings) if finding == row['reviewer_original']]
                if len(matches) == 1:
                    value['findings'][index]['reviewer_original'] = _response_field_reference(
                        response_sha, ['findings', matches[0]], findings[matches[0]])
    return shown

def _literal_findings_target(views, sha, *, session, source, scope, verdict):
    """A hash-bound complete literal in this input, never an archival reference.

    Native capture authenticates original bytes before this presentation step.
    Equality here adds no verdict, historical settlement or new inspection claim.
    """
    if (not isinstance(sha, str) or not isinstance(session, str) or not session
            or not isinstance(source, str) or len(source) != 40
            or not isinstance(scope, str) or not scope):
        return None
    selected = views.get(sha)
    if (not isinstance(selected, dict)
            or selected.get('schema') != 'selected-original-response/v1'
            or selected.get('original_raw_sha256') != sha):
        return None
    response = selected.get('value')
    if (not isinstance(response, dict) or response.get('is_error') is not False
            or response.get('session_id') != session):
        return None
    output = response.get('structured_output')
    if (not isinstance(output, dict) or output.get('reviewed_commit') != source
            or output.get('scope') != scope or output.get('verdict') != verdict
            or verdict != 'REQUEST_CHANGES'
            or not isinstance(output.get('findings'), list)
            or not output['findings']
            or any(not isinstance(item, str) or not item for item in output['findings'])):
        return None
    return output['findings']


def _share_direction_findings(views):
    """Quote aliases only; every distinct driver statement stays in place."""
    for selected in views.values():
        if not isinstance(selected, dict) or selected.get('schema') != 'selected-original-response/v1':
            continue
        value = selected.get('value')
        if (not isinstance(value, dict)
                or value.get('schema') != 'independent-direction-and-driver-response/v1'
                or value.get('applied_material_approval') is not False
                or value.get('science_or_activation_approval') is not False):
            continue
        sha = value.get('response_sha256')
        if not isinstance(sha, str):
            continue
        findings = _literal_findings_target(views, sha, session=value.get('session_id'),
            source=value.get('source'), scope=value.get('scope'), verdict=value.get('actual_verdict'))
        rows = value.get('findings_and_responses')
        if findings is None or not isinstance(rows, list) or len(rows) != len(findings):
            continue
        # Require the complete ordered set to match before changing any quote.
        if any(not isinstance(row, dict) or type(row.get('number')) is not int
                or row['number'] != index + 1 or row.get('finding_verbatim') != findings[index]
                for index, row in enumerate(rows)):
            continue
        for index, row in enumerate(rows):
            row['finding_verbatim'] = _response_field_reference(sha, ['findings', index], findings[index])


def _share_review_event_findings(shown, views):
    """Selected event view only; original chain validation remains unchanged."""
    for event in shown['events']:
        if event.get('event') != 'REVIEW':
            continue
        payload = event['payload']
        original = payload.get('original_review')
        if not isinstance(original, dict) or not isinstance(original.get('response_sha256'), str):
            continue
        sha = original['response_sha256']
        findings = _literal_findings_target(views, sha, session=original.get('session_id'),
            source=original.get('source'), scope=original.get('scope'), verdict=payload.get('verdict'))
        if findings is not None and payload.get('findings') == findings:
            payload['findings'] = _response_field_reference(sha, ['findings'], findings)


def _response_object(raw):
    """Strict JSON for evidence projections; duplicate values cannot disappear."""
    import json
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('SELECTED_RESPONSE_DUPLICATE_KEYS')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('SELECTED_RESPONSE_NONFINITE_JSON')
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def selected_linked_disposition_view(original, source):
    """Select only the current administrative chain; original science stays literal."""
    from orchestrator.protected_disposition import successor_packet
    _pin(source, 40)
    if not successor_packet(original, 'disposition'):
        _fail()
    link = original['linked_disposition']
    proof = original['reviewer_evidence'].get('original')
    history = original['recorded_changes']
    if (set(link) != {'schema', 'request', 'source', 'origin_task', 'origin_source',
                     'original_proof_sha256', 'change_request'}
            or link['source'] != source or not isinstance(proof, dict)
            or proof.get('schema') != 'disposition-successor-original-proof/v1'
            or proof.get('origin_task') != link['origin_task']
            or proof.get('origin_source') != link['origin_source']
            or proof.get('origin_source') == source
            or _sha(proof) != link['original_proof_sha256']):
        _fail()
    _pin(link['request']); _pin(link['origin_task']); _pin(link['origin_source'], 40)
    _chain(history)
    reference = link['change_request']
    if (not isinstance(reference, dict) or set(reference) != {'request_id', 'applied_event'}
            or history['request']['identity'] != reference['request_id']
            or reference['applied_event'] not in _active(history)):
        _fail()
    applied = next(e for e in history['events'] if e['identity'] == reference['applied_event'])
    if applied['payload'].get('result_binding', {}).get('source') != source:
        _fail()
    # No scientific proof slot is selected or rewritten. Thus historical active
    # applications at every original scientific head remain complete literals.
    view = deepcopy(original)
    protected = _active(history)
    predecessor = original['reviewer_evidence'].get('unstarted_predecessor')
    if predecessor is not None:
        if (not isinstance(predecessor,dict) or predecessor.get('schema') != 'unstarted-disposition-predecessor/v1'
                or type(predecessor.get('history_event_count')) is not int
                or not 0 < predecessor['history_event_count'] < len(history['events'])):
            _fail()
        prefix = {**history, 'events':history['events'][:predecessor['history_event_count']],
                  'head_sha256':predecessor['history_head_sha256']}
        if sorted(_active(prefix)) != predecessor['active_applied_events']:
            _fail()
        protected |= _active(prefix)
    view['recorded_changes'] = _selected_chain(history, source, _sha(original), protected)
    if view['reviewer_evidence'] != original['reviewer_evidence']:
        _fail()
    return view


def _reviewed_extension(state, packet, source):
    """Lossless sharing of one already validated referenced-history prefix.

    Unlike the native-chain extension, the reconstructed object is explicitly a
    reviewed history representation. No absent original payload is reconstructed.
    """
    candidates=[]
    for (index,slot),old in _literal_histories(packet,source).items():
        if not reviewed.is_reference(old) or old['request'] != state['request']:
            continue
        prefix_reference(old,state,source)
        count=len(reviewed.index(old))
        if count > state['boundary']['event_count']:
            continue
        prior={e['sequence']:e for e in old['events']}
        current={e['sequence']:e for e in state['events'] if e['sequence']<=count}
        if prior != current:
            continue  # Different retained applications must remain separate literals.
        candidates.append((count,index,slot,old))
    if not candidates:
        return deepcopy(state)
    count,index,slot,old=max(candidates,key=lambda x:(x[0],-x[1],x[2]))
    return {'schema':REVIEWED_EXTENSION,'source':source,'event_index':index,'literal_slot':slot,
        'historical_representation_sha256':_sha(old),'current_representation_sha256':_sha(state),
        'representation_schema':state['schema'],'head_sha256':state['head_sha256'],
        'boundary':deepcopy(state['boundary']),'binding_application':state['binding_application'],
        'prefix_index_suffix':deepcopy(state['prefix_index'][count:]),
        'suffix_events':deepcopy([e for e in state['events'] if e['sequence']>count]),
        'notice':'Exact same-packet sharing of a validated reviewed history representation; '
                 'not reconstruction of omitted native application payloads or new approval.'}


def _restore_reviewed_extension(value,packet,source):
    try:
        if (set(value)!={'schema','source','event_index','literal_slot','historical_representation_sha256',
                'current_representation_sha256','representation_schema','head_sha256','boundary',
                'binding_application','prefix_index_suffix','suffix_events','notice'}
                or value['source']!=source or type(value['event_index']) is not int):
            _fail()
        old=_literal_histories(packet,source)[(value['event_index'],value['literal_slot'])]
        if not reviewed.is_reference(old) or _sha(old)!=value['historical_representation_sha256']:
            _fail()
        state={'schema':value['representation_schema'],'request':deepcopy(old['request']),
            'events':deepcopy(old['events'])+deepcopy(value['suffix_events']),
            'head_sha256':value['head_sha256'],'boundary':deepcopy(value['boundary']),
            'binding_application':value['binding_application'],
            'prefix_index':reviewed.index(old)+deepcopy(value['prefix_index_suffix']),'notice':reviewed.NOTICE}
        reviewed.validate(state)
        if _sha(state)!=value['current_representation_sha256'] or _bytes(value)!=_bytes(_reviewed_extension(state,packet,source)):
            _fail()
        return state
    except (KeyError,TypeError,AttributeError):
        _fail()


def authenticate_report_references(config, packet, source, *, original_client=None):
    """Native read-only retrieval immediately before use or saved recovery.

    Fixed descriptors come from validated retained event payloads. No arbitrary
    caller path, model tool, latest-history replacement, or approval inference.
    """
    from pathlib import Path
    from orchestrator import current_scientific_input
    if current_scientific_input.is_current(packet):
        from orchestrator.scientific_evidence_runtime import _capture
        from orchestrator.handover_runtime import request_broker
        if original_client is None:
            original_client = lambda _socket, operation, body: request_broker(config['broker_socket'], operation, body)
        result = _capture(config, packet, source, original_client=original_client)
        from orchestrator.scientific_evidence_access import describe_capture
        return {'schema':'authenticated-current-scientific-retrieval/v1',
            'source':source,'packet_sha256':_sha(packet),
            'capture':describe_capture(result),'provider_calls':0}
    capture=packet.get('scientific_change_history',{})
    if capture.get('schema')!=CURRENT_LINKED_HISTORY:
        return None
    states=validate_current_history(packet,source)
    receipts=[]
    for row in capture['response_references']:
        descriptor=row['descriptor']
        raw=changes._read(Path(config['change_request_store'])/row['request']/descriptor['artifact'])
        if (hashlib.sha256(raw).hexdigest()!=descriptor['sha256']
                or len(raw)!=descriptor.get('size',len(raw))):
            _fail()
        event=next(e for e in states[row['request']]['events'] if e['identity']==row['event'])
        _response_event_binding(event,descriptor,raw.decode('utf-8'))
        receipts.append({'request':row['request'],'event':row['event'],
            'artifact':descriptor['artifact'],'sha256':descriptor['sha256'],'bytes':len(raw)})
    return {'schema':'authenticated-scientific-report-retrieval/v1','source':source,
        'packet_sha256':_sha(packet),'retrieved':receipts,'provider_calls':0,
        'meaning':'Native reader authenticated these exact originals; no claim of model inspection or scientific acceptance.'}
