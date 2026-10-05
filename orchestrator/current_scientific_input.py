"""Compact saved current state over the existing native evidence capture.

This module selects no science and authorizes no execution. Controller preparation
and protected delivery recompute identical projections from native originals.
Only fixed investigator/eligibility evidence slots are supported.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from orchestrator import change_requests as changes, reviewed_history as history
from orchestrator import scientific_evidence_access as access, linked_disposition_input as linked

SCHEMA = 'authenticated-current-scientific-input/v1'
FORMAL = 'registered-formal-scientific-decision'


def is_formal(packet):
    return isinstance(packet,dict) and packet.get('trigger') == FORMAL


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def is_current(packet):
    return isinstance(packet, dict) and packet.get('scientific_change_history', {}).get('schema') == SCHEMA


def evidence(packet, source):
    from orchestrator.disposition_context import _selected_evidence
    return _selected_evidence(packet, source)


def has_references(packet, source):
    selected = evidence(packet, source)
    return isinstance(selected, dict) and any(
        row.get('linked_disposition', {}).get('input_presentation', {}).get('schema') == linked.CURRENT_PRESENTATION
        for row in selected.get('verified_events', []))


def references(packet, source):
    from orchestrator.disposition_context import _dispositions, _primary_change
    primary = _primary_change(packet)
    if is_formal(packet):
        from orchestrator.formal_decisions import checked_request, contract
        request=checked_request(packet['formal_request'])
        from orchestrator.handover_coordinator import digest
        require(request['source']==source and contract(packet['scientific_decision_artifacts'])=={
            'version':3,'action':request['action'],'subject':request['subject'],
            'bindings_sha256':digest(request['bindings'])}, 'CURRENT_INPUT_FORMAL_CONTRACT_CHANGED')
        return primary, []
    selected = evidence(packet, source)
    if selected is None:
        # Typed continuing tasks inherit the same source-bound primary plan.
        # This does not infer a wake, scientific authority or an absent finding.
        from orchestrator.scientific_context_references import has_references
        require(has_references(packet), 'CURRENT_INPUT_WAKE_REQUIRED')
        from orchestrator.hosted_campaign_task import task_contract
        if packet.get('trigger') == 'installed-research-eligibility':
            entry = packet['reviewer_evidence']['catalog_core']
            task = entry['request']['task']
        else:
            require(packet.get('trigger') == 'installed-research-request',
                    'CURRENT_INPUT_TYPED_TASK_REQUIRED')
            entry = packet['research_catalog_entry']; task = packet['campaign_task']
            require(entry['request']['task'] == task, 'CURRENT_INPUT_CATALOG_TASK_CHANGED')
        require(entry['source'] == source, 'CURRENT_INPUT_CATALOG_SOURCE_CHANGED')
        task_contract(task)
        return primary, []
    require(isinstance(selected, dict), 'CURRENT_INPUT_WAKE_REQUIRED')
    result = []
    for index, _proof in _dispositions(selected, source):
        value = selected['verified_events'][index]['linked_disposition']
        ref = linked.check_reference_view(value, source=source, application=primary['applied_event'])
        result.append((index, ref))
    return primary, result



def _bound_scope(primary, primary_state, refs, source):
    app=next((e for e in primary_state['events'] if e['identity']==primary['applied_event']),None)
    require(app is not None and app['event']=='APPLIED'
            and app['payload']['result_binding'].get('source')==source,
            'CURRENT_INPUT_SOURCE_APPLICATION_REQUIRED')
    plans=app['payload']['result_binding'].get('current_state_settlements')
    require(isinstance(plans,dict) and primary['request_id'] in plans
            and 1 <= len(plans) <= 4, 'CURRENT_INPUT_EXPLICIT_HISTORY_SCOPE_REQUIRED')
    for identity in plans:
        history._pin(identity)
    require({ref['repair_request'] for _,ref in refs} <= set(plans),
            'CURRENT_INPUT_LINKED_HISTORY_SCOPE_REQUIRED')
    return sorted(plans)


def has_current_plan(config, packet):
    """The actual native application opts later wakes into the same representation.

    This detects a pending plan for engineering preparation, not approval.
    Existing linked_change/protected admission still qualifies the application.
    """
    selected=evidence(packet,config['source'])
    if selected is None and not is_formal(packet):
        from orchestrator.scientific_context_references import has_references
        if not has_references(packet):
            return False
    from orchestrator.disposition_context import _primary_change
    primary=_primary_change(packet)
    state=changes.load(Path(config['change_request_store'])/primary['request_id'])
    app=next((e for e in state['events'] if e['identity']==primary['applied_event']),None)
    require(app is not None and app['event']=='APPLIED','CURRENT_INPUT_APPLICATION_REQUIRED')
    binding=app['payload']['result_binding']
    if 'current_state_settlements' not in binding:
        return False
    _,refs=references(packet,config['source'])
    _bound_scope(primary,state,refs,config['source'])
    return True


def _change_capture(capture, primary, prefixes):
    """Select authenticated change originals from the same immutable capture.

    No new retrieval is claimed. Exclude task/role records from the history
    descriptor so it cannot be circularly dependent on the packet that uses it.
    The actual role tools use their outer task-bound descriptor for every read.
    """
    result = deepcopy(capture)
    rows = [r for r in result['manifest']['records'] if r['name'].startswith('change/')]
    result['manifest']['records'] = rows
    result['payloads'] = {r['sha256']:capture['payloads'][r['sha256']] for r in rows}
    result['manifest']['task_binding'] = access.sha(changes.encoded({
        'source':capture['manifest']['source'], 'primary':primary, 'prefixes':prefixes}))
    return result


def _prefix(state):
    bound = history.boundary(state)
    return {key:bound[key] for key in ('event_count','head_sha256','index_sha256')}


def _views(capture, primary, prefixes, source):
    capture = _change_capture(capture, primary, prefixes)
    views = {}
    literal = {}
    for request_id in sorted(prefixes):
        state = history.captured_chain(capture, request_id)
        require(_prefix(state) == prefixes[request_id], 'CURRENT_INPUT_NATIVE_PREFIX_CHANGED')
        selected = history.current_state_view(capture, request_id, primary['applied_event'],
            source=source, application_request=primary['request_id'])
        # An unclassified request remains wholly literal. No fallback to an
        # overview, a latest verdict, or a driver-produced narrative summary.
        views[request_id] = deepcopy(state) if selected is None else selected
        from orchestrator.disposition_context import _literal_descriptors, _response_event_binding
        rows = {r['name']:r for r in capture['manifest']['records']}
        for ref in _literal_descriptors(views[request_id]):
            descriptor = ref['descriptor']
            record = rows['change/'+request_id+'/'+descriptor['artifact']]
            raw = capture['payloads'][record['sha256']]
            require(access.sha(raw) == descriptor['sha256'], 'CURRENT_INPUT_RESPONSE_CHANGED')
            event = next(e for e in state['events'] if e['identity'] == ref['event'])
            _response_event_binding(event, descriptor, raw.decode('utf-8'))
            literal.setdefault(descriptor['sha256'], raw.decode('utf-8'))
    return views, literal


def _history(capture, packet, source, prefixes):
    primary, refs = references(packet, source)
    change_capture = _change_capture(capture, primary, prefixes)
    states = {key:history.captured_chain(change_capture,key) for key in prefixes}
    # Historical linked-only fixtures without a multi-request plan preserve
    # their original fixed scope. Fresh current plans explicitly bind all scope.
    binding=next(e for e in states[primary['request_id']]['events']
        if e['identity']==primary['applied_event'])['payload']['result_binding']
    expected=(_bound_scope(primary,states[primary['request_id']],refs,source)
        if 'current_state_settlements' in binding else
        sorted({primary['request_id']} | {ref['repair_request'] for _,ref in refs}))
    require(sorted(prefixes)==expected,'CURRENT_INPUT_EXACT_HISTORY_SCOPE_REQUIRED')
    from orchestrator.scientific_context_references import required_history
    for identity, prior in required_history(packet).items():
        require(identity in states and prior['event_count'] <= len(states[identity]['events']),
                'CURRENT_INPUT_INHERITED_HISTORY_SCOPE_REQUIRED')
        previous = states[identity]
        count = prior['event_count']
        old = {'request': previous['request'], 'events': previous['events'][:count],
               'head_sha256': history.row(previous['events'][count-1])['original_sha256']}
        bound = history.boundary(old)
        require(all(bound[key] == prior[key] for key in prior),
                'CURRENT_INPUT_INHERITED_HISTORY_CHANGED')
    for index, ref in refs:
        value = evidence(packet, source)['verified_events'][index]['linked_disposition']
        for bound in (value['reviewed_repair'], value['originals']['historical_authority']):
            state = states.get(bound['request_id'])
            require(state is not None and bound['event_count'] <= len(state['events']),
                    'CURRENT_INPUT_HISTORICAL_NAMESPACE_REQUIRED')
            count = bound['event_count']
            old = {'request':state['request'], 'events':state['events'][:count],
                   'head_sha256':history.row(state['events'][count-1])['original_sha256']}
            expected = history.boundary(old)
            require(all(expected[k] == bound[k] for k in
                        ('request_id','event_count','head_sha256','index_sha256')),
                    'CURRENT_INPUT_HISTORICAL_PREFIX_CHANGED')
    views, literals = _views(capture, primary, prefixes, source)
    return {'schema':SCHEMA, 'source':source, 'primary':primary,
        'native_prefixes':deepcopy(prefixes), 'current_requests':views,
        'literal_response_originals':literals,
        'notice':'Current state is recomputed from native originals at preparation, delivery and recovery. '
            'Only explicitly reviewed source-history settlements are referenced. Current authority, '
            'active applications, unbound criticism, unknown conditions and unreviewed tail stay literal. '
            'Use the outer task-bound scientific evidence descriptor to retrieve originals; '
            'nested history descriptors are provenance, not additional tool captures.'}


def preparation_view(config, packet):
    """Authenticate a native primary before constructing the bounded saved packet.

    Full retained history belongs in the native store/capture, not the transient
    provider packet. Only fresh eligibility/formal construction can use this;
    existing saved packets and legacy references retain their original readers.
    """
    if (not isinstance(packet, dict) or 'scientific_change_history' in packet
            or packet.get('trigger') not in ('installed-research-eligibility', FORMAL)):
        return packet
    supplied = packet.get('recorded_changes')
    if not isinstance(supplied, dict) or set(supplied) != {'request', 'events', 'head_sha256'}:
        return packet
    from orchestrator.disposition_context import _primary_change
    primary = _primary_change(packet)
    native = changes.load(Path(config['change_request_store']) / primary['request_id'])
    require(supplied == native, 'CURRENT_INPUT_PRIMARY_ORIGINAL_CHANGED')
    result = {key:deepcopy(value) for key,value in packet.items() if key != 'recorded_changes'}
    result['recorded_changes'] = {'schema':'current-change-state-location/v1',
        'request_id':primary['request_id'], 'location':'scientific_change_history.current_requests'}
    return result


def capture_history(config, packet):
    """Controller's exact native snapshot before immutable task identity."""
    require('scientific_change_history' not in packet, 'CURRENT_INPUT_ALREADY_CAPTURED')
    source = config['source']
    prepared = preparation_view(config, packet)
    primary, refs = references(prepared,source)
    primary_state=changes.load(Path(config['change_request_store'])/primary['request_id'])
    binding=next(e for e in primary_state['events'] if e['identity']==primary['applied_event'])['payload']['result_binding']
    identities=(_bound_scope(primary,primary_state,refs,source)
        if 'current_state_settlements' in binding else
        sorted({primary['request_id']} | {r['repair_request'] for _,r in refs}))
    require(bool(refs) or 'current_state_settlements' in binding,
            'CURRENT_INPUT_EXPLICIT_HISTORY_SCOPE_REQUIRED')
    states = {identity:(primary_state if identity==primary['request_id'] else
        changes.load(Path(config['change_request_store'])/identity)) for identity in identities}
    prefixes = {identity:_prefix(state) for identity,state in states.items()}
    binding = access.sha(changes.encoded({'source':source,'primary':primary,'prefixes':prefixes}))
    captured = access.capture_changes(config['change_request_store'],identities,
        source=source,task_binding=binding,expected_prefixes=prefixes)
    result = deepcopy(prepared)
    result['scientific_change_history'] = _history(captured,prepared,source,prefixes)
    if packet['trigger'] in ('installed-research-eligibility', FORMAL):
        require(packet['recorded_changes'] == states[primary['request_id']],
                'CURRENT_INPUT_PRIMARY_ORIGINAL_CHANGED')
        result['recorded_changes'] = {'schema':'current-change-state-location/v1',
            'request_id':primary['request_id'],
            'location':'scientific_change_history.current_requests'}
    from orchestrator.disposition_context import _bytes
    _bytes(result)  # The final packet retains the unchanged bound.
    return result


def authenticate_capture(store, packet, source, *, owner=None):
    """Reconstruct the saved exact prefix, never replace it with latest history."""
    require(is_current(packet), 'CURRENT_INPUT_CAPTURE_REQUIRED')
    saved=packet['scientific_change_history']
    primary, refs = references(packet,source)
    require(saved.get('source') == source and saved.get('primary') == primary,
            'CURRENT_INPUT_SOURCE_OR_APPLICATION_CHANGED')
    prefixes=saved['native_prefixes']
    # Establish namespace authority from the original primary application before
    # opening any packet-named secondary request, including during recovery.
    primary_state=changes.load(Path(store)/primary['request_id'], owner=owner)
    app=next(e for e in primary_state['events'] if e['identity']==primary['applied_event'])
    binding=app['payload']['result_binding']
    require(bool(refs) or 'current_state_settlements' in binding,
            'CURRENT_INPUT_EXPLICIT_HISTORY_SCOPE_REQUIRED')
    expected=(_bound_scope(primary,primary_state,refs,source)
        if 'current_state_settlements' in binding else
        sorted({primary['request_id']} | {ref['repair_request'] for _,ref in refs}))
    require(sorted(prefixes)==expected,'CURRENT_INPUT_EXACT_HISTORY_SCOPE_REQUIRED')
    captured=access.capture_changes(store,sorted(prefixes),source=source,
        task_binding=access.sha(access.encoded(packet)),expected_prefixes=prefixes,owner=owner)
    require(_history(captured,packet,source,prefixes) == saved, 'CURRENT_INPUT_SAVED_VIEW_CHANGED')
    if packet['trigger'] in ('installed-research-eligibility', FORMAL):
        require(packet['recorded_changes']=={'schema':'current-change-state-location/v1',
            'request_id':primary['request_id'],'location':'scientific_change_history.current_requests'},
            'CURRENT_INPUT_PRIMARY_LOCATION_CHANGED')
    return captured


def authenticate_linked_capture(capture, packet, source):
    """Authenticate literal science from the already native-read original.

    capture_dispositions performed the native read; this compares its immutable
    captured body. No second retrieval or invented later-read provenance.
    """
    primary, refs=references(packet,source)
    state=history.captured_chain(_change_capture(capture,primary,
        packet['scientific_change_history']['native_prefixes']),primary['request_id'])
    app=next(e for e in state['events'] if e['identity']==primary['applied_event'])
    plan=app['payload']['result_binding']['linked_disposition_input']
    linked.reference_plan(plan)
    records={r['name']:r for r in capture['manifest']['records']}
    for index,ref in refs:
        name='result/'+ref['origin_task']+'/linked-disposition.original.json'
        row=records[name];raw=capture['payloads'][row['sha256']]
        require(access.sha(raw)==ref['original_value_sha256'], 'CURRENT_INPUT_LINKED_ORIGINAL_CHANGED')
        original=json.loads(raw)
        expected=linked.reference_view(original,plan,primary['applied_event'],source)
        value=evidence(packet,source)['verified_events'][index]['linked_disposition']
        require(expected==value, 'CURRENT_INPUT_LINKED_LITERAL_CHANGED')
    return capture


def _literal_reference(path, value):
    raw = changes.encoded(value)
    return {'schema':'same-prompt-current-literal/v1',
        'literal_path_in_task_state':path, 'value_sha256':access.sha(raw),
        'value_utf8_bytes':len(raw),
        'meaning':'Exact complete value is literal at this path in the same task_state. '
                  'No summary, settlement, new retrieval or inspection is claimed.'}


def _current_response_reference(value, views, expected):
    """Bind an existing quote alias to its literal location in current task state."""
    from orchestrator import disposition_context as disposition
    try:
        require(value['schema'] == disposition.RESPONSE_FIELD_REFERENCE,
                'CURRENT_INPUT_RESPONSE_REFERENCE_REQUIRED')
        identity = value['response_original_raw_sha256']
        target = views[identity]
        require(target['schema'] == 'selected-original-response/v1'
                and target['original_raw_sha256'] == identity,
                'CURRENT_INPUT_RESPONSE_LITERAL_REQUIRED')
        path = value['literal_path_in_selected_response']
        for key in path:
            target = target[key]
        require(target == expected and disposition._sha(target) == value['value_sha256'],
                'CURRENT_INPUT_RESPONSE_LITERAL_CHANGED')
    except (KeyError, TypeError, IndexError):
        raise ValueError('CURRENT_INPUT_RESPONSE_LITERAL_REQUIRED') from None
    return _literal_reference(
        ['scientific_change_history', 'literal_response_originals', identity, *path], target)


def _share_current_driver_responses(prefix, views):
    """Share one exact supported driver array; never infer resolution or authority."""
    from orchestrator.disposition_context import _literal_findings_target
    events={event['identity']:event for event in prefix['events']}
    for event in prefix['events']:
        if event['event']!='DISPOSITION':
            continue
        payload=event['payload']
        responses=payload.get('driver_responses')
        review=events.get(payload.get('responds_to_review_event'))
        if (not isinstance(responses,list) or not responses
                or not isinstance(review,dict) or review['event']!='REVIEW'):
            continue
        original_review=review['payload'].get('original_review',{})
        if not isinstance(original_review,dict):
            continue
        matches=[]
        for descriptor in access._artifacts(payload.get('response_evidence')):
            identity=descriptor['sha256']
            selected=views.get(identity,{})
            value=selected.get('value',{})
            if (selected.get('schema')!='selected-original-response/v1'
                    or selected.get('original_raw_sha256')!=identity
                    or selected.get('original_bytes')!=descriptor.get('size')
                    or not isinstance(value,dict)
                    or value.get('schema')!='independent-direction-and-driver-response/v1'
                    or value.get('actual_verdict')!='REQUEST_CHANGES'
                    or value.get('applied_material_approval') is not False
                    or value.get('science_or_activation_approval') is not False
                    or value.get('session_id')!=payload.get('responds_to_session')
                    or any(original_review.get(key)!=value.get(field) for key,field in (
                        ('response_sha256','response_sha256'),('session_id','session_id'),
                        ('source','source'),('scope','scope')))):
                continue
            actor=value.get('driver_actor')
            if (not isinstance(actor,dict) or not actor
                    or any(event['actor'].get(key)!=item for key,item in actor.items())):
                continue
            findings=_literal_findings_target(views,value.get('response_sha256'),
                session=value.get('session_id'),source=value.get('source'),
                scope=value.get('scope'),verdict=value.get('actual_verdict'))
            rows=value.get('findings_and_responses')
            if findings is None or not isinstance(rows,list) or len(rows)!=len(findings):
                continue
            projected=[]
            for index,row in enumerate(rows):
                if (not isinstance(row,dict) or type(row.get('number')) is not int
                        or row['number']!=index+1
                        or not isinstance(row.get('driver_disposition'),str)
                        or not isinstance(row.get('driver_response'),str)
                        or row.get('finding_verbatim')!=_literal_reference(
                            ['scientific_change_history','literal_response_originals',
                             value['response_sha256'],'value','structured_output','findings',index],
                            findings[index])):
                    break
                projected.append({'finding_number':row['number'],
                    'disposition':row['driver_disposition'],'response':row['driver_response']})
            if len(projected)==len(rows) and projected==responses:
                matches.append(identity)
        if len(matches)!=1:
            continue
        payload['driver_responses']={
            'schema':'same-prompt-current-driver-responses/v1',
            'literal_path_in_task_state':['scientific_change_history',
                'literal_response_originals',matches[0],'value','findings_and_responses'],
            'fields':{'finding_number':'number','disposition':'driver_disposition',
                'response':'driver_response'},
            'value_sha256':access.sha(changes.encoded(responses)),
            'meaning':'Read every row at this literal path using exactly this field mapping. '
                'The complete ordered responses are byte-equivalent values; no finding is resolved.'}


def presentation(packet, source):
    """Fixed display sharing after native capture; never rewrite saved evidence.

    Reuse the existing typed-only metadata renderer at the explicit prefix.
    The tail is untouched. Share only equal complete science values and exact
    resolution report bytes, with a direct same-prompt target and original hash.
    """
    from orchestrator.disposition_context import _selected_event
    require(is_current(packet), 'CURRENT_INPUT_CAPTURE_REQUIRED')
    references(packet, source)
    shown=deepcopy(packet)
    captured=shown['scientific_change_history']
    literal=captured['literal_response_originals']
    # Reuse the existing result and direction/driver quote-sharing contracts.
    # Unknown bodies stay full literals; a parser failure never removes criticism.
    from orchestrator.disposition_context import (_response_object,
        _response_presentations, _share_direction_findings, _share_review_event_findings,
        RESPONSE_FIELD_REFERENCE)
    structured={}
    direction_originals={}
    for identity, body in literal.items():
        try:
            value=_response_object(body)
        except (ValueError,TypeError):
            continue
        if not isinstance(value,dict):
            continue
        if (value.get('type')=='result'
                and isinstance(value.get('structured_output'),dict)):
            structured[identity]=body
        elif value.get('schema')=='independent-direction-and-driver-response/v1':
            structured[identity]=body
            direction_originals[identity]=value
    response_views=_response_presentations(structured)
    _share_direction_findings(response_views)
    for identity, original in direction_originals.items():
        rows=response_views[identity]['value'].get('findings_and_responses')
        original_rows=original.get('findings_and_responses')
        if not isinstance(rows,list) or not isinstance(original_rows,list):
            continue
        for row,before in zip(rows,original_rows):
            if not isinstance(row,dict) or not isinstance(before,dict):
                continue
            quote=row.get('finding_verbatim')
            if (isinstance(before.get('finding_verbatim'),str) and isinstance(quote,dict)
                    and quote.get('schema')==RESPONSE_FIELD_REFERENCE):
                row['finding_verbatim']=_current_response_reference(
                    quote,response_views,before['finding_verbatim'])
    literal.update(response_views)
    for state in captured['current_requests'].values():
        if state.get('schema') != history.CURRENT_VIEW:
            continue  # No reviewed selection: retain complete native state.
        count=state['reviewed_boundary']['event_count']
        require(type(count) is int and 1 <= count <= state['native_event_count'],
                'CURRENT_INPUT_PRESENTATION_BOUNDARY_CHANGED')
        prefix={'events':[event for event in state['events'] if event['sequence'] <= count]}
        previous_findings={event['identity']:deepcopy(event['payload'].get('findings'))
            for event in prefix['events'] if event['event']=='REVIEW'}
        _share_review_event_findings(prefix,response_views)
        for event in prefix['events']:
            before=previous_findings.get(event['identity'])
            quote=event['payload'].get('findings')
            if (isinstance(before,list) and isinstance(quote,dict)
                    and quote.get('schema')==RESPONSE_FIELD_REFERENCE):
                event['payload']['findings']=_current_response_reference(quote,response_views,before)
        _share_current_driver_responses(prefix,response_views)
        state['events']=[history._administrative_event(event,count,_selected_event)
            if event['sequence'] <= count else deepcopy(event) for event in state['events']]
        state['display_rule']=(
            'Prefix events reuse selected-event metadata and typed administrative field references. '
            'historical_administrative_fields names exact fields in change/request/event originals. '
            'Unknown values, narratives, findings, authority, refusals and conditions remain literal. '
            'Every event after reviewed_boundary remains complete. Reference presence is not inspection.')
        for resolution in state['literal_resolution_reports'].values():
            bodies=resolution['same_bound_original_reports']
            for identity, body in list(bodies.items()):
                rendered = body
                selected_condition = state.get('resolution_condition_views', {}).get(identity)
                if selected_condition is not None:
                    rendered = selected_condition['presentation']
                    require(isinstance(body,dict)
                            and body == history.resolution_condition_reference(rendered)
                            and body['original_report_sha256'] == identity,
                            'CURRENT_INPUT_RESOLUTION_CONDITIONS_CHANGED')
                else:
                    require(isinstance(body,str) and access.sha(body.encode('utf-8'))==identity,
                            'CURRENT_INPUT_RESOLUTION_ORIGINAL_CHANGED')
                require(identity not in literal or literal[identity] in (body, rendered),
                        'CURRENT_INPUT_RESOLUTION_LITERAL_CONFLICT')
                literal[identity]=rendered
                bodies[identity]=_literal_reference(
                    ['scientific_change_history','literal_response_originals',identity],rendered)
        # The native saved view retains exact selectors, original bodies and a
        # recomputable presentation. Display one copy at the literal location.
        if 'resolution_condition_views' in state:
            state['resolution_condition_views'] = {
                identity: _literal_reference(
                    ['scientific_change_history','literal_response_originals',identity],
                    row['presentation'])
                for identity, row in state['resolution_condition_views'].items()}
    selected=evidence(shown,source)
    if selected is None:
        return shown  # Formal request and its scientific evidence stay literal.
    base=selected.get('installed_charter_evidence',{}).get('reviewer_evidence')
    if isinstance(base,dict):
        path=['reviewer_evidence']
        if packet['trigger'] in ('installed-research-eligibility', FORMAL):
            path.append('input_evidence')
        path += ['installed_charter_evidence','reviewer_evidence']
        for row in selected.get('verified_events',[]):
            proof=row.get('linked_disposition',{}).get('originals',{})
            if 'scientific_input_context' in proof and changes.encoded(proof['scientific_input_context'])==changes.encoded(base):
                proof['scientific_input_context']=_literal_reference(path,base)
    # The exact scientific outputs/reviews and all surrounding conditions stay
    # literal. Historical supporting documents use the SAME authenticated
    # predecessor capture already supplied independently to each scientific role.
    for row in selected.get('verified_events', []):
        value = row.get('linked_disposition')
        if not isinstance(value, dict) or 'input_presentation' not in value:
            continue
        reference = linked.check_reference_view(value, source=source,
            application=captured['primary']['applied_event'])
        proof = value['originals']
        science = proof.get('scientific_input_context')
        if isinstance(science, dict) and science.get('schema') != 'same-prompt-current-literal/v1':
            proof['scientific_input_context'] = linked.context_document_presentation(
                science, reference['origin_task'])
            if proof['scientific_input_context'] != science:
                notice = ('Display references historical interpretation/result-card document bodies '
                    'through the authenticated task-bound scientific reader. Full scientific context '
                    'remains in the immutable saved packet and native predecessor original. '
                    'Original author/reviewer outputs, disposition, original reviews, consideration '
                    'decisions and surrounding conditions remain literal. Read referenced originals '
                    'before relying on their claims or limitations; no finding is settled by this view.')
                proof['packet']['notice'] = notice
                value['input_presentation']['notice'] = notice
    return shown
