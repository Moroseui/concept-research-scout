"""Source-bound administrative prefix references; never scientific authority.

The selected application binds the complete prefix index reviewed with it. Every
non-APPLIED record (including all criticism and responses), every active/historically
needed application and the entire unreviewed tail stay literal. Originals are
validated through the native private store before capture. This representation
cannot qualify that application: ordinary independent-review/deployment gates
still use the complete original store, not this scientific input view.
"""
from copy import deepcopy
import hashlib
import re

from orchestrator import change_requests as changes

SCHEMA = 'reviewed-administrative-prefix/v1'
HISTORICAL_SCHEMA = 'reviewed-linked-history-prefix/v1'
BOUNDARY = 'reviewed-administrative-boundary/v1'
NOTICE = ('Only superseded APPLIED payloads inside this explicitly bound prefix are '
    'referenced. All review, authorization and disposition records and the entire '
    'tail are literal. Supersession does not resolve criticism. Full original '
    'event files remain in the protected change store; indexed material is not '
    'model-inspected material. The index grows with total history. This is not '
    'a native complete chain or an approval receipt.')


def _fail():
    raise ValueError('REVIEWED_HISTORY_BINDING_CHANGED')


def _source_review_statement(raw):
    """Parse either existing approval profile; this supplies no qualification.

    Both routes still use their strict APPROVE-only report contract. The caller
    must bind the original report to its authenticated REVIEW and exact source/
    proposal. Unknown schemas and non-final/adverse judgments remain refused.
    """
    from orchestrator.terminal_review import _statement, PROFILE
    from orchestrator.server_terminal_review import PROFILE as SERVER_PROFILE
    for profile in (PROFILE, SERVER_PROFILE):
        try:
            return _statement(raw, profile=profile)
        except ValueError:
            pass
    _fail()


def _pin(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        _fail()
    return value


def sha(value):
    return hashlib.sha256(changes.encoded(value)).hexdigest()


def row(event):
    return {'sequence': event['sequence'], 'identity': event['identity'],
        'event': event['event'], 'payload_sha256': sha(event['payload']),
        'original_sha256': hashlib.sha256(changes.encoded(event) + b'\n').hexdigest(),
        'supersedes': event['payload'].get('supersedes_applied_events', [])
            if event['event'] == 'APPLIED' else []}


def is_reference(state):
    return isinstance(state, dict) and state.get('schema') in (SCHEMA, HISTORICAL_SCHEMA)


def index(state):
    return state['prefix_index'] + [row(e) for e in state['events']
        if e['sequence'] > state['boundary']['event_count']] if is_reference(state) else [row(e) for e in state['events']]


def active(rows):
    return {r['identity'] for r in rows if r['event'] == 'APPLIED'} - {
        identity for r in rows for identity in r['supersedes']}


def boundary(state):
    """Produce exact review material from a previously native-validated prefix."""
    from orchestrator.disposition_context import _chain
    if is_reference(state):
        _fail()
    _chain(state)
    rows = index(state)
    return {'schema': BOUNDARY, 'request_id': state['request']['identity'],
        'event_count': len(rows), 'head_sha256': state['head_sha256'],
        'index_sha256': sha(rows)}


def validate(state):
    """Validate a saved reference without pretending omitted payloads are present.

    Exact index commitment is inside the literal native selected application.
    Its approval is checked elsewhere against the protected original chain.
    """
    try:
        if set(state) != {'schema', 'request', 'events', 'head_sha256', 'boundary',
                         'binding_application', 'prefix_index', 'notice'} or state['schema'] not in (SCHEMA, HISTORICAL_SCHEMA):
            _fail()
        request = changes._request(state['request'])
        bound = state['boundary']; prefix = state['prefix_index']; events = state['events']
        if (not isinstance(prefix, list) or not prefix or not isinstance(events, list)
                or set(bound) != {'schema', 'request_id', 'event_count', 'head_sha256', 'index_sha256'}
                or bound['schema'] != BOUNDARY or bound['request_id'] != request['identity']
                or type(bound['event_count']) is not int or bound['event_count'] != len(prefix)
                or sha(prefix) != bound['index_sha256'] or state['notice'] != NOTICE):
            _fail()
        count = len(prefix)
        literal = {e['sequence']: e for e in events}
        if len(literal) != len(events) or [e['sequence'] for e in events] != sorted(literal):
            _fail()
        rows = index(state)
        previous = hashlib.sha256(changes.encoded(request) + b'\n').hexdigest()
        prior = []
        for number, item in enumerate(rows, 1):
            if (set(item) != {'sequence', 'identity', 'event', 'payload_sha256', 'original_sha256', 'supersedes'}
                    or type(item['sequence']) is not int or item['sequence'] != number
                    or item['event'] not in changes.EVENTS or not isinstance(item['supersedes'], list)):
                _fail()
            for name in ('identity', 'payload_sha256', 'original_sha256'):
                _pin(item[name])
            event = literal.get(number)
            if event is None:
                if number > count or item['event'] != 'APPLIED':
                    _fail()
                # Only the committed administrative index is available here.
                # Preserve transition identities without fabricating a payload.
                if not set(item['supersedes']) <= {r['identity'] for r in prior if r['event'] == 'APPLIED'}:
                    _fail()
                event = {'identity': item['identity'], 'event': 'APPLIED'}
            else:
                core = {k: v for k, v in event.items() if k != 'identity'}
                if (row(event) != item or event['schema'] != changes.EVENT_SCHEMA
                        or event['request_identity'] != request['identity']
                        or event['previous_sha256'] != previous or sha(core) != event['identity']):
                    _fail()
                changes.actor(event['actor'])
                changes._transition(prior, event['event'], event['payload'])
            prior.append(event)
            previous = item['original_sha256']
            if number == count and previous != bound['head_sha256']:
                _fail()
        if previous != state['head_sha256'] or not active(rows) <= {e['identity'] for e in events}:
            _fail()
        if state['schema'] == HISTORICAL_SCHEMA:
            # The external source application is checked by linked_disposition_input
            # against the literal primary application in the same saved packet.
            # This validates representation integrity, not approval or provenance.
            _pin(state['binding_application'])
        else:
            application = next(e for e in events if e['identity'] == state['binding_application'])
            if (application['event'] != 'APPLIED' or application['sequence'] <= count
                    or application['identity'] not in active(rows)
                    or application['payload']['result_binding'].get('reviewed_history_prefix') != bound):
                _fail()
        return [r['identity'] for r in rows]
    except (KeyError, TypeError, AttributeError, StopIteration):
        _fail()


def capture(state, application_id, *, protected=()):
    """Use only a prefix explicitly bound by this independently reviewed application.

    Called after native changes.load has checked every original and its evidence.
    Keeping every adverse/response body avoids requiring unavailable model tools.
    """
    from orchestrator.disposition_context import _chain
    _chain(state)
    application = next(e for e in state['events'] if e['identity'] == application_id)
    bound = application['payload']['result_binding'].get('reviewed_history_prefix')
    if bound is None:
        return deepcopy(state)  # unchanged legacy inputs; no inferred boundary
    count = bound.get('event_count')
    if type(count) is not int or not 1 <= count < application['sequence']:
        _fail()
    prefix = {'request': state['request'], 'events': state['events'][:count],
              'head_sha256': row(state['events'][count-1])['original_sha256']}
    if boundary(prefix) != bound:
        _fail()
    rows = index(state); retained = active(rows) | set(protected) | {application_id}
    if application_id not in active(rows) or not retained <= {e['identity'] for e in state['events'] if e['event'] == 'APPLIED'}:
        _fail()
    result = {'schema': SCHEMA, 'request': deepcopy(state['request']),
        'events': [deepcopy(e) for e in state['events'] if e['sequence'] > count
                   or e['event'] != 'APPLIED' or e['identity'] in retained],
        'head_sha256': state['head_sha256'], 'boundary': deepcopy(bound),
        'binding_application': application_id, 'prefix_index': rows[:count], 'notice': NOTICE}
    validate(result)
    return result


def matches_prefix(historical, current):
    """An exact original prefix is checked using every native event commitment."""
    validate(current)
    rows = index(historical)
    return (historical['request'] == current['request'] and rows == index(current)[:len(rows)]
            and (rows[-1]['original_sha256'] if rows else
                 hashlib.sha256(changes.encoded(historical['request']) + b'\n').hexdigest()) == historical['head_sha256'])


def presentation(state):
    """Display already validated original bindings without repeating their index.

    Full index stays in the saved packet. Literal event identities already index
    retained rows; only omitted application identities need the extra prompt index.
    No native-chain reconstruction is claimed for this selected display.
    """
    from orchestrator.disposition_context import _selected_event
    validate(state)
    literal = {e['identity'] for e in state['events']}
    return {'schema': 'selected-reviewed-administrative-prefix/v1',
        'request': deepcopy(state['request']), 'head_sha256': state['head_sha256'],
        'boundary': deepcopy(state['boundary']), 'binding_application': state['binding_application'],
        'original_capture_sha256': sha(state), 'original_event_count': len(index(state)),
        'events': [_administrative_event(e, state['boundary']['event_count'], _selected_event) for e in state['events']],
        'referenced_applications': [{'sequence': r['sequence'], 'identity': r['identity'],
            } for r in state['prefix_index'] if r['identity'] not in literal],
        'administrative_field_reference_rule': 'For a prefix DISPOSITION or REVIEW only, historical_administrative_fields names '
            'digest/typed-artifact metadata in its exact original payload. Resolve through this request identity '
            'and the retained event identity in the complete stored packet/native event file. Unknown values, '
            'narratives, findings, refusals and conditions remain literal. No resolution or approval is inferred.',
        'notice': NOTICE + ' Full prefix index is in the original stored packet; retained events '
            'use the existing selected-event metadata/descriptor rules.'}



# Fixed metadata fields only. Unknown fields stay literal. A referenced field is
# not declared resolved: every rationale, affected result, finding, response,
# limitation, refusal and later gate remains literal. This source-bound rule is
# part of the exact candidate application reviewed before scientific use.
ADMINISTRATIVE_REFERENCES = frozenset({
    'evidence', 'review_evidence', 'original_review', 'proposal',
    'source', 'reviewed_source', 'corrective_source', 'source_before',
    'original_session', 'review_session', 'review_session_id', 'review_event',
    'responds_to_review_event', 'responds_to_session', 'response_to_review_session',
    'checks', 'observations', 'verification', 'test_output', 'test_receipt',
    'original_qualification_and_evidence', 'reviewer_originals_and_driver_evidence',
    'final_review_originals', 'reviewer_observation', 'private_session_original_binding',
    'control_binding', 'controller_config_sha256', 'broker_config_sha256',
    'completed_audit_original_sha256', 'completed_audit_receipt_sha256',
    'installed_proposal_sha256', 'installed_receipt_sha256', 'upgrade_receipt_sha256',
    'coverage_sha256', 'observed_completion_sha256', 'repair_receipt_sha256',
    'canonical_append_receipt_sha256', 'refresh_receipt_sha256', 'proposal_sha256',
    'input_preflight_collector_sha256', 'preflight_collector_sha256', 'packet_sha256',
    'original_request_sha256', 'original_response', 'original_review_attempt',
    'actual_carrier_source', 'original_session', 'source_evidence', 'evidence_map',
})


def _administrative_event(event, count, render):
    shown = render(event)
    if event['sequence'] > count or event['event'] not in ('DISPOSITION', 'REVIEW'):
        return shown
    payload = shown['payload']
    names = sorted(k for k in ADMINISTRATIVE_REFERENCES & set(payload)
                   if _referenceable_metadata(payload[k]))
    if not names:
        return shown
    shown['payload'] = {k: v for k, v in payload.items() if k not in names}
    shown['historical_administrative_fields'] = names

    return shown


def _referenceable_metadata(value):
    """Never infer absence of criticism from a key such as checks/observations.

    Only exact digest strings and typed artifact descriptors may leave this
    selected display. Every narrative, status, scope or unknown field stays.
    """
    if isinstance(value, str):
        return bool(re.fullmatch('[0-9a-f]{40}|[0-9a-f]{64}', value))
    if isinstance(value, list):
        return bool(value) and all(_referenceable_metadata(v) for v in value)
    if isinstance(value, dict):
        fields = set(value)
        descriptor = (fields in ({'artifact','sha256','size'}, {'artifact','sha256'},
                           {'name','sha256','size'})
            and isinstance(value.get('sha256'), str)
            and bool(re.fullmatch('[0-9a-f]{64}', value['sha256']))
            and (type(value.get('size')) is int and value['size'] >= 0 if 'size' in value else True))
        if descriptor:
            return True
        # The original event remains available under its exact request/event
        # binding. Accept maps of typed descriptors or explicitly named digests,
        # never a narrative/status hidden under a metadata-looking parent key.
        return bool(value) and all(
            isinstance(k, str) and re.fullmatch('[a-zA-Z0-9_.-]{1,100}', k)
            and ((isinstance(v, dict) and _referenceable_metadata(v))
                 or (k.endswith(('_sha256', '_sha1')) and isinstance(v, str)
                     and bool(re.fullmatch('[0-9a-f]{40}|[0-9a-f]{64}', v))))
            for k, v in value.items())
    return False


def report_views(state, originals, views, references, *, states=None):
    """Apply only an exact reviewed selection; never infer settlement from age.

    Originals were eagerly retrieved and authenticated in capture_current_history
    and remain fully stored. The source/configuration application containing this
    selection must pass the existing independent review gate before research use.
    An old review supplies provenance, not approval of this new selection.
    """
    validate(state)
    app = next(e for e in state['events'] if e['identity'] == state['binding_application'])
    plan = app['payload']['result_binding'].get('historical_report_selection')
    if plan is None:
        return views
    try:
        multi = plan.get('schema') == 'reviewed-multi-request-source-report-selection/v1'
        keys = {'schema', 'references', 'resolution_event', 'resolution_original',
                'resolution_text', 'scope', 'qualification'}
        if multi:
            keys.add('additional_prefixes')
        if (set(plan) != keys
                or plan['schema'] not in ('reviewed-prefix-report-selection/v1',
                    'reviewed-multi-request-source-report-selection/v1')
                or plan['scope'] != 'historical-source-findings-only'
                or plan['qualification'] != 'REQUIRES_INDEPENDENT_REVIEW_OF_THIS_EXACT_APPLICATION'
                or not isinstance(plan['references'], dict)):
            _fail()
        resolution = next(e for e in state['events'] if e['identity'] == plan['resolution_event'])
        if (resolution['event'] != 'REVIEW' or resolution['payload']['verdict'] != 'APPROVE'
                or resolution['sequence'] > state['boundary']['event_count']
                or list(resolution['payload']['review_evidence'].values()).count(plan['resolution_original']) != 1):
            _fail()
        raw = plan['resolution_text'].encode('utf-8')
        if (hashlib.sha256(raw).hexdigest() != plan['resolution_original']['sha256']
                or len(raw) != plan['resolution_original']['size']):
            _fail()
        statement = _source_review_statement(raw)
        if (statement['verdict'] != 'APPROVE' or statement['scope'] != 'material-source-integration'
                or statement['source'] != resolution['payload']['source']
                or statement['proposal_sha256'] != resolution['payload']['proposal_sha256']):
            _fail()
        by_request = {state['request']['identity']: state}
        if multi:
            linked = app['payload']['result_binding'].get('linked_disposition_input', {})
            repair = linked.get('boundaries', {}).get('reviewed_repair')
            if (not isinstance(repair, dict) or plan['additional_prefixes'] != {repair.get('request_id'): repair}
                    or not isinstance(states, dict)):
                _fail()
            additional = states.get(repair['request_id'])
            if (not is_reference(additional) or additional['schema'] != HISTORICAL_SCHEMA
                    or additional['boundary'] != repair
                    or additional['binding_application'] != state['binding_application']):
                _fail()
            validate(additional)
            by_request[repair['request_id']] = additional
        def exact_prefix_event(reference):
            chain = by_request.get(reference['request'])
            if chain is None:
                _fail()
            event = next(e for e in chain['events'] if e['identity'] == reference['event'])
            if event['sequence'] > chain['boundary']['event_count']:
                _fail()
            return event
        descriptors = {r['descriptor']['sha256']: r for r in references}
        result = deepcopy(views)
        for identity, reason in plan['references'].items():
            if (identity not in originals or identity not in descriptors or identity not in views
                    or not isinstance(reason, str) or not 20 <= len(reason) <= 2000):
                _fail()
            matches = [r for r in references if r['descriptor']['sha256'] == identity]
            for matched in matches:
                exact_prefix_event(matched)
            reference = descriptors[identity]
            event = exact_prefix_event(reference)
            result[identity] = {'schema': 'reviewed-historical-source-report-reference/v1',
                **deepcopy(reference), 'selection_reason': reason,
                'original_recorded_verdict': event['payload'].get('verdict',
                    event['payload'].get('review_verdict', 'DRIVER_RESPONSE_NOT_A_VERDICT')),
                'resolution_event': plan['resolution_event'],
                'literal_conditions': 'Selected current APPLIED.result_binding.historical_report_selection.resolution_text',
                'original_body': ('Protected native change store / request / descriptor.artifact; eagerly authenticated '
                    'before this capture. Exact original is preserved, not supplied or model-inspected.' if multi else
                    'Preserved packet.scientific_change_history.response_originals[' + identity + ']'),
                'notice': 'Original historical judgment remains unchanged. Referenced content is not newly '
                    'model-inspected. The exact independent review of this application must confirm this '
                    'source-only scope; every condition in the complete literal resolution report still '
                    'applies at its own stage. No deployment, accounting, authority or scientific '
                    'acceptance is inferred. No model tools are enabled; controller retrieval supplies '
                    'all unresolved/unselected bodies directly. If further historical detail is needed, '
                    'defer and name this exact reference rather than inventing a conclusion.'}
        return result
    except (KeyError, TypeError, AttributeError, StopIteration):
        _fail()


def capture_linked_history(state, bound, application_id, *, protected=()):
    """Reference only a separately reviewed, exact historical prefix.

    The caller authenticates the complete native original and the selected source
    application's explicit boundary. All adverse/response/authority payloads and
    active applications remain literal; every suffix event also remains literal.
    A reference is never used to qualify its own source application.
    """
    from orchestrator.disposition_context import _chain
    _chain(state)
    if is_reference(state):
        _fail()
    _pin(application_id)
    count = bound.get('event_count') if isinstance(bound, dict) else None
    if type(count) is not int or not 1 <= count <= len(state['events']):
        _fail()
    prefix = {'request': state['request'], 'events': state['events'][:count],
              'head_sha256': row(state['events'][count-1])['original_sha256']}
    if boundary(prefix) != bound:
        _fail()
    rows = index(state)
    retained = active(rows) | set(protected)
    if not retained <= {e['identity'] for e in state['events'] if e['event'] == 'APPLIED'}:
        _fail()
    result = {'schema': HISTORICAL_SCHEMA, 'request': deepcopy(state['request']),
        'events': [deepcopy(e) for e in state['events'] if e['sequence'] > count
                   or e['event'] != 'APPLIED' or e['identity'] in retained],
        'head_sha256': state['head_sha256'], 'boundary': deepcopy(bound),
        'binding_application': application_id, 'prefix_index': rows[:count], 'notice': NOTICE}
    validate(result)
    return result


EVENT_FIELD_SELECTION = 'reviewed-prefix-event-field-selection/v1'
EVENT_FIELD_REFERENCE = 'selected-historical-event-fields/v1'
# Only these source-review/progress body slots are eligible for an explicit,
# independently reviewed selection. No authority, result, verdict, scope,
# condition, no-retry or unknown field can be selected by this operation.
SOURCE_BODY_FIELDS = frozenset({
    'rationale', 'findings', 'findings_and_responses',
    'findings_and_driver_responses', 'driver_responses',
})


def event_field_selection(primary, states):
    """Validate a proposed field selection against immutable native commitments.

    This does NOT approve its own classification. Like report selection, actual
    scientific use requires the independent approval of this exact application
    at the existing linked_change/admission boundary. The material reviewer gets
    complete originals; a PENDING application permits engineering preflight only.
    """
    validate(primary)
    app = next(e for e in primary['events']
               if e['identity'] == primary['binding_application'])
    plan = app['payload']['result_binding'].get('historical_event_selection')
    if plan is None:
        return {}
    try:
        if (not isinstance(plan, dict) or set(plan) != {
                'schema', 'qualification', 'purpose', 'requests'}
                or plan['schema'] != EVENT_FIELD_SELECTION
                or plan['qualification'] != 'REQUIRES_INDEPENDENT_REVIEW_OF_THIS_EXACT_APPLICATION'
                or plan['purpose'] != 'settled-implementation-history-only'
                or not isinstance(plan['requests'], dict) or not plan['requests']):
            _fail()
        selected = {}
        for identity, rows in plan['requests'].items():
            state = states[identity]
            validate(state)
            if (state['request']['identity'] != identity
                    or state['binding_application'] != primary['binding_application']
                    or not isinstance(rows, list) or not rows):
                _fail()
            native = {e['identity']: e for e in state['events']}
            selected[identity] = {}
            for row in rows:
                if (not isinstance(row, dict) or set(row) != {'event', 'fields', 'reason'}
                        or row['event'] in selected[identity]
                        or not isinstance(row['fields'], list) or not row['fields']
                        or any(not isinstance(k, str) for k in row['fields'])
                        or len(set(row['fields'])) != len(row['fields'])
                        or not set(row['fields']) <= SOURCE_BODY_FIELDS
                        or not isinstance(row['reason'], str)
                        or not 30 <= len(row['reason']) <= 1500):
                    _fail()
                event = native[row['event']]
                if (event['event'] not in ('REVIEW', 'DISPOSITION')
                        or event['sequence'] > state['boundary']['event_count']
                        or not set(row['fields']) <= set(event['payload'])):
                    _fail()
                selected[identity][row['event']] = deepcopy(row)
        return selected
    except (KeyError, TypeError, AttributeError, StopIteration):
        _fail()


def selected_event_fields(shown, selection):
    """Select a view only; keep every nonselected value and original identity.

    The fixed current or historical-prefix view may contain fewer events than
    the current capture. All rows were validated against that full current
    capture first. No generic recursive aliasing or replacement of saved chains.
    """
    if not selection:
        return shown
    result = deepcopy(shown)
    result['event_field_reference_rule'] = (
        'Each historical_source_fields entry names exact payload fields in this request/event native original. '
        'They are not model-inspected. The exact source application selection requires independent review. '
        'Original judgments, nonselected values and all later gates remain unchanged.')
    for event in result['events']:
        row = selection.get(event['identity'])
        if row is None:
            continue
        payload = event['payload']
        if not set(row['fields']) <= set(payload):
            _fail()
        event['payload'] = {k: v for k, v in payload.items() if k not in row['fields']}
        event['historical_source_fields'] = {
            'schema': EVENT_FIELD_REFERENCE,
            'fields': deepcopy(row['fields']),
            'reason': row['reason']}
    return result


CURRENT_SETTLEMENT = 'reviewed-current-state-settlement/v1'
CURRENT_VIEW = 'authenticated-current-change-state/v1'

RESOLUTION_CONDITIONS = 'reviewed-resolution-conditions/v1'


def resolution_conditions(body, selection, reader_names):
    """An exact reviewed display, not a summary or a new review judgment.

    Keep the COMPLETE original terminal statement, including every finding,
    limitation and additional finding accepted by the strict schema. Additional scope/condition prose is
    selected as hash-bound UTF-8 byte ranges, never generated text. The material
    reviewer must assess completeness of this exact selection before use;
    mechanical validation cannot decide whether prose contains another condition.
    """
    try:
        if (not isinstance(body, str) or not isinstance(selection, dict)
                or set(selection) != {'schema', 'scope', 'qualification', 'sections'}
                or selection['schema'] != RESOLUTION_CONDITIONS
                or selection['scope'] != 'source-review-narrative-only'
                or selection['qualification'] != 'REQUIRES_INDEPENDENT_REVIEW_OF_THIS_EXACT_APPLICATION'
                or not isinstance(selection['sections'], list)
                or not 1 <= len(selection['sections']) <= 32
                or not isinstance(reader_names, list) or not reader_names
                or any(not isinstance(name, str) or not re.fullmatch(
                    r'change/[0-9a-f]{64}/evidence/[A-Za-z0-9_.-]+', name)
                    for name in reader_names)
                or reader_names != sorted(set(reader_names))):
            _fail()
        raw = body.encode('utf-8')
        statement = _source_review_statement(raw)  # APPROVE only, original strict parser.
        sections = []
        previous = 0
        for section in selection['sections']:
            if (not isinstance(section, dict)
                    or set(section) != {'start_utf8', 'end_utf8', 'sha256'}
                    or type(section['start_utf8']) is not int
                    or type(section['end_utf8']) is not int
                    or not previous <= section['start_utf8'] < section['end_utf8'] <= len(raw)):
                _fail()
            part = raw[section['start_utf8']:section['end_utf8']]
            if hashlib.sha256(part).hexdigest() != _pin(section['sha256']):
                _fail()
            sections.append({**deepcopy(section), 'text': part.decode('utf-8')})
            previous = section['end_utf8']
        return {'schema': RESOLUTION_CONDITIONS,
            'original_report_sha256': hashlib.sha256(raw).hexdigest(),
            'original_report_utf8_bytes': len(raw),
            'original_statement': statement,
            'verbatim_scope_conditions': sections,
            'authenticated_reader_names': deepcopy(reader_names),
            'notice': 'Complete original structured judgment and reviewed verbatim condition prose. '
                'The exact selection requires independent review; this display supplies no approval. '
                'Historical findings keep their original scope and all later gates. The complete '
                'report remains in this task-bound authenticated capture, retrievable at the named '
                'records; referenced narrative is not claimed inspected. No scientific acceptance '
                'or settlement of an unlinked finding follows from this representation.'}
    except (KeyError, TypeError, AttributeError, UnicodeError):
        _fail()


def resolution_condition_reference(presentation):
    """Bind compact saved state to its conditions and captured original.

    Native current_state_view reconstructs this from the original on preparation,
    protected delivery and recovery. No full report is copied into that state.
    """
    return {'schema': 'authenticated-resolution-condition-reference/v1',
        'original_report_sha256': presentation['original_report_sha256'],
        'original_report_utf8_bytes': presentation['original_report_utf8_bytes'],
        'condition_view_sha256': sha(presentation),
        'authenticated_reader_names': deepcopy(presentation['authenticated_reader_names'])}


def captured_chain(capture, request_id):
    """Restore one exact native chain from the existing authenticated capture.

    No live filesystem lookup, model call, or acceptance of a digest as a body.
    This runs outside model input. Full original indexes and bodies remain in
    the existing paged capture and are discoverable through its ordinary reader.
    """
    from orchestrator.scientific_evidence_access import _capture_layout
    import json
    try:
        _capture_layout(capture)
        manifest = capture['manifest']
        expected = manifest['request_heads'][_pin(request_id)]
        rows = {r['name']: r for r in manifest['records']}
        if len(rows) != len(manifest['records']):
            _fail()
        prefix = 'change/' + request_id + '/'
        def body(name):
            row_value = rows[prefix + name]
            raw = capture['payloads'][row_value['sha256']]
            if (hashlib.sha256(raw).hexdigest() != row_value['sha256']
                    or len(raw) != row_value['utf8_bytes']):
                _fail()
            return raw
        events = {}
        for sequence in range(1, expected['event_count'] + 1):
            raw = body('event/' + str(sequence) + '.json')
            event = json.loads(raw)
            if event['sequence'] != sequence:
                _fail()
            events[f"{sequence:04d}-{event['identity']}.json"] = raw
        result = changes.validate_originals(body('request.json'), events, body)
        if (result['head_sha256'] != expected['head_sha256']
                or len(result['events']) != expected['event_count']):
            _fail()
        return result
    except (KeyError, TypeError, AttributeError, UnicodeError):
        _fail()


def current_state_view(capture, request_id, application_id, *, source, application_request=None):
    """Project explicit reviewed settlements; never infer them from chronology.

    An exact independently reviewed application must bind this plan before use.
    This pure function intentionally permits a pending application for engineering
    preflight, exactly like event_field_selection; it does not qualify approval.
    The ordinary protected admission reader must still validate that application.
    No current authority, active application, unbound criticism or tail is hidden.
    """
    from orchestrator.scientific_evidence_access import _capture_layout
    try:
        state = captured_chain(capture, request_id)
        if capture['manifest']['source'] != source:
            _fail()
        rows = index(state)
        by_id = {e['identity']: e for e in state['events']}
        primary = state if application_request in (None, request_id) else captured_chain(capture, application_request)
        app = next(e for e in primary['events'] if e['identity'] == _pin(application_id))
        if (app['event'] != 'APPLIED' or application_id not in active(index(primary))
                or app['payload']['result_binding'].get('source') != source):
            _fail()
        binding = app['payload']['result_binding']
        plans = binding.get('current_state_settlements')
        if plans is not None:
            if not isinstance(plans, dict) or any(k not in capture['manifest']['request_heads'] for k in plans):
                _fail()
            plan = plans.get(request_id)
        else:
            plan = binding.get('current_state_settlement') if primary is state else None
        if plan is None:
            return None  # unchanged legacy representation; no inferred reduction
        plan_keys = {'schema', 'boundary', 'settlements', 'scope', 'qualification'}
        if (not isinstance(plan, dict) or set(plan) not in
                (plan_keys, plan_keys | {'resolution_presentations'})
                or plan['schema'] != CURRENT_SETTLEMENT
                or plan['scope'] != 'settled-implementation-history-only'
                or plan['qualification'] != 'REQUIRES_INDEPENDENT_REVIEW_OF_THIS_EXACT_APPLICATION'
                or not isinstance(plan['settlements'], dict)):
            _fail()
        bound = plan['boundary']
        count = bound['event_count']
        if (type(count) is not int or not 1 <= count <= len(state['events'])
                or (primary is state and count >= app['sequence'])):
            _fail()
        prefix = {'request': state['request'], 'events': state['events'][:count],
                  'head_sha256': row(state['events'][count-1])['original_sha256']}
        if boundary(prefix) != bound:
            _fail()
        resolutions = {}
        for old_id, resolution_id in plan['settlements'].items():
            old, resolution = by_id[_pin(old_id)], by_id[_pin(resolution_id)]
            # Human records, scientific outcomes and authority cannot be settled
            # merely by putting their IDs in an administrative application.
            if (old['event'] not in ('REVIEW', 'DISPOSITION')
                    or old['actor']['kind'] != 'agent'
                    or not old['sequence'] < resolution['sequence'] <= count
                    or resolution['event'] != 'REVIEW'
                    or resolution['actor']['kind'] != 'agent'
                    or resolution['actor']['family'] != 'claude'
                    or resolution['payload']['verdict'] != 'APPROVE'):
                _fail()
            # Source resolutions use the same exact report primitive as
            # report_views; the body is fetched from the actual capture.
            from orchestrator.scientific_evidence_access import _artifacts
            descriptors = list(_artifacts(resolution['payload']['review_evidence']))
            reports = []
            for descriptor in descriptors:
                raw = capture['payloads'][descriptor['sha256']]
                if len(raw) != descriptor['size']:
                    _fail()
                try:
                    statement = _source_review_statement(raw)
                except ValueError:
                    continue
                if (statement['source'] == resolution['payload']['source']
                        and statement['proposal_sha256'] == resolution['payload']['proposal_sha256']):
                    reports.append(raw)
            # A native binding confirmation may retain its substantive prior
            # report under the same source/proposal (genuine 014 + 015). Bind
            # the qualifying original explicitly, and retain both full bodies;
            # do not guess which report was written or discard prior conditions.
            report_bodies = {hashlib.sha256(raw).hexdigest(): raw.decode('utf-8')
                             for raw in reports}
            response = resolution['payload'].get('original_review', {}).get('response_sha256')
            if (not report_bodies or (response is not None and response not in report_bodies)
                    or (response is None and len(report_bodies) != 1)):
                _fail()
            resolutions[resolution_id] = {
                'qualifying_original_sha256': response or next(iter(report_bodies)),
                'same_bound_original_reports': report_bodies}
        # A resolution may itself have a later explicit resolution. Keep every
        # terminal resolution report literal, including its remaining gates,
        # limitations and preserved adverse findings. No last-review-wins rule.
        terminal = {key: value for key, value in resolutions.items()
                    if key not in plan['settlements']}
        presentations = {}
        if 'resolution_presentations' in plan:
            selections = plan['resolution_presentations']
            bodies = {identity: body for resolution in terminal.values()
                      for identity, body in resolution['same_bound_original_reports'].items()}
            if (not isinstance(selections, dict) or not selections
                    or not set(selections) <= set(bodies)):
                _fail()  # No unresolved/nonterminal report may enter this route.
            for identity, selection in selections.items():
                _pin(identity)
                raw = bodies[identity].encode('utf-8')
                if hashlib.sha256(raw).hexdigest() != identity:
                    _fail()
                names = sorted(row['name'] for row in capture['manifest']['records']
                    if row['name'].startswith('change/') and '/evidence/' in row['name']
                    and row['sha256'] == identity and row['utf8_bytes'] == len(raw))
                if (not any(name.startswith('change/' + request_id + '/evidence/') for name in names)
                        or capture['payloads'].get(identity) != raw):
                    _fail()
                presentations[identity] = {
                    'selection': deepcopy(selection), 'reader_names': names,
                    'presentation': resolution_conditions(bodies[identity], selection, names)}
            for resolution in terminal.values():
                for identity in resolution['same_bound_original_reports']:
                    if identity in presentations:
                        resolution['same_bound_original_reports'][identity] = resolution_condition_reference(
                            presentations[identity]['presentation'])
        kept = []
        preserved_fields = {}
        for event in state['events']:
            if event['sequence'] <= count:
                if event['identity'] in plan['settlements']:
                    # The explicit settlement covers source narrative fields,
                    # not unknown conditions, consequences or authority labels.
                    # Deduplicate only byte-identical remaining values; originals
                    # retain each event's exact attribution and provenance.
                    remainder = {key: deepcopy(value) for key, value in event['payload'].items()
                        if key not in SOURCE_BODY_FIELDS and not (
                            key in ADMINISTRATIVE_REFERENCES | {'applied_event'}
                            and _referenceable_metadata(value))}
                    if remainder:
                        preserved_fields[sha(remainder)] = remainder
                    continue
                if event['event'] == 'APPLIED' and event['identity'] not in active(rows):
                    continue
            shown = deepcopy(event)
            if event['identity'] == application_id:
                field = 'current_state_settlements' if plans is not None else 'current_state_settlement'
                shown['payload']['result_binding'][field] = {
                    'schema': 'authenticated-settlement-plan-reference/v1',
                    'original_sha256': sha(binding[field]),
                    'original_event': application_id,
                    'reader_name': 'change/' + request_id + '/event/' + str(event['sequence']) + '.json',
                    'meaning': 'Exact plan is in the authenticated original active application; not self-approval.'}
            kept.append(shown)
        descriptor, _, _ = _capture_layout(capture)
        result = {'schema': CURRENT_VIEW, 'source': source, 'request': deepcopy(state['request']),
            'binding_application': application_id, 'native_head_sha256': state['head_sha256'],
            'native_event_count': len(rows), 'reviewed_boundary': deepcopy(bound),
            'authenticated_capture': descriptor,
            'events': kept, 'literal_resolution_reports': terminal,
            'literal_preserved_fields': preserved_fields,
            'notice': 'Only explicitly linked source-history settlements and superseded prefix applications '
                'are referenced. Current authority, active applications, unbound criticism and the entire '
                'unreviewed tail remain literal. Full originals and their index remain in the existing '
                'authenticated capture; no referenced body is claimed model-inspected or scientifically accepted.'}
        if presentations:
            result['resolution_condition_views'] = presentations
        return result
    except (KeyError, TypeError, AttributeError, StopIteration):
        _fail()


def validate_current_state_view(value, capture, request_id, application_id, *, source):
    """Recompute against original native bodies before accepting a saved view."""
    expected = current_state_view(capture, request_id, application_id, source=source)
    if expected is None or changes.encoded(value) != changes.encoded(expected):
        _fail()
    return expected
