"""Bounded operator-terminal source review; original evidence, never self-approval.

The root-held bundle and local CLI journal are the trust boundary, not provider
signatures. This pure validator starts no model, records no approval and grants
no installation, activation, scientific authority or accounting exemption.
"""
import copy
import json
import re
from pathlib import Path

from orchestrator import change_requests as changes, deployment_review as gate
from orchestrator.review_input_codec import parsed

PROFILE = 'operator-terminal-review/v1'
BASE_SOURCE = '00d54b3ed529fd1e05afbbcccf9ba221a98db207'
AUTH_REQUEST = 'ab544f7cf68b8f77d52c5e110b3a80c27cf3f58ae338f8309a6a6a4d54b7a572'
AUTH_EVENT = 'a3f335084c3786a5f41d0927209133164ba116363ca5704f73949d551b326674'
AUTH_EVENT_SHA = '5c7e51be52e42d3cb0ee9b9a58a950d5f4189c3de1c2975be997794ed3a789bc'
OPERATOR_SHA = '60c8b5733a3c229548f736518fd321f0aed0b7f06d5611c6a33d5708ec7facc4'
AMENDMENT_SHA = '308f8ddbf55f64a741fca99ba706c75bd659f81a80c55b594d23a8fee90a608b'
SECTION_SHA = 'c5a62260bd54d38313161bc3895994a4107db198f1294aef4eb11c1feb626696'
PRIOR_REVIEWS = {
    '001-claude-review.md': '31dd52936f1bf1fcfdd992aeffd73110e0602b8272d4fa8fe304fe9f261d4c7c',
    '001-supplement-architecture.md': '310db28ba715aafb28e7568c16d581c41fb20c1ef1b6c9ca2b74f6d04685b8db',
    '003-claude-followup.md': 'b1d414f7ad6cd66679f236982229ffd4f7c40799f3bd093c095e507b3cf01a75',
}
FINDINGS = {f'C{i:03d}' for i in range(1, 12)}
DISPOSITIONS = {'resolved', 'preserve', 'held-deployment', 'held-accounting',
                'held-science', 'deferred-nonblocking'}


def require(ok, reason):
    gate.require(ok, 'TERMINAL_REVIEW_' + reason)


def _authority(raw):
    prefix = 'authority/'
    events = {name[len(prefix+'events/'):]: value for name, value in raw.items()
              if name.startswith(prefix+'events/')}
    state = changes.validate_originals(raw[prefix+'request.json'], events,
                                       lambda name: raw[prefix+name])
    require(state['request']['identity'] == AUTH_REQUEST, 'OPERATOR_REQUEST_CHANGED')
    event = next((e for e in state['events'] if e['identity'] == AUTH_EVENT), None)
    require(event is not None and event['event'] == 'AUTHORIZED'
            and event['actor'] == {'kind': 'human', 'identity': 'project-operator'},
            'OPERATOR_AUTHORIZATION_REQUIRED')
    original = events[f'{event["sequence"]:04d}-{AUTH_EVENT}.json']
    require(gate.digest(original) == AUTH_EVENT_SHA, 'OPERATOR_AUTHORIZATION_CHANGED')
    payload = event['payload']; policy = payload['review_policy']
    operator = raw[prefix+payload['authority_reference']['artifact']]
    amendment = raw[prefix+policy['approved_amendment']['artifact']]
    section = raw[prefix+policy['approved_section']['artifact']]
    require(gate.digest(operator) == payload['operator_original_sha256'] == OPERATOR_SHA
            and gate.digest(amendment) == AMENDMENT_SHA
            and gate.digest(section) == SECTION_SHA
            and amendment[1641:4125] == section and policy['source'] == BASE_SOURCE
            and all(payload.get(k) is False for k in
                    ('candidate_approved', 'installation_approved', 'activation_approved')),
            'EXACT_AMENDMENT_REQUIRED')
    return state


def _statement(report, *, profile=PROFILE, approval_required=True):
    from orchestrator.terminal_statement import statement
    return statement(report, profile=profile, approval_required=approval_required)


def _compacted_session_view(events, session):
    """Recognize only original Read replays immediately preceding auto-compaction.

    The full original journal remains the protocol hash and private evidence.
    This logical view never joins sessions or treats a summary as a human request.
    Unknown replay/summary shapes fail; successful report Writes are never replayed.
    """
    seen = {}; view = []; pending = []; receipts = []
    for index, event in enumerate(events):
        identity = event.get('uuid')
        is_message = event.get('type') in {'assistant', 'user'}
        if is_message and identity and identity in seen:
            original = seen[identity]
            content = event.get('message', {}).get('content')
            require(not (event['type'] == 'user' and isinstance(content, str)),
                    'MANUAL_REQUEST_ID_REQUIRED')
            require(event.get('sessionId') == session == original.get('sessionId')
                    and event.get('isSidechain') is False
                    and isinstance(content, list) and content,
                    'COMPACTION_REPLAY_IDENTITY_REQUIRED')
            changed = {k for k in set(original) | set(event)
                       if original.get(k) != event.get(k)}
            require(changed <= {'parentUuid', 'slug', 'toolUseResult'},
                    'COMPACTION_REPLAY_CONTENT_CHANGED')
            if event['type'] == 'assistant':
                require(all(x.get('type') == 'tool_use' and x.get('name') == 'Read'
                            for x in content), 'ONLY_READ_REPLAY_SUPPORTED')
            else:
                require(all(x.get('type') == 'tool_result' for x in content)
                        and event.get('sourceToolAssistantUUID') in seen,
                        'ONLY_READ_RESULT_REPLAY_SUPPORTED')
                caller = seen[event['sourceToolAssistantUUID']]
                calls = caller.get('message', {}).get('content', [])
                require(caller.get('type') == 'assistant'
                        and caller.get('sessionId') == session
                        and all(any(c.get('type') == 'tool_use' and c.get('name') == 'Read'
                                    and c.get('id') == x.get('tool_use_id') for c in calls)
                                for x in content), 'READ_REPLAY_CALLER_REQUIRED')
            require(identity not in pending, 'REPEATED_COMPACTION_REPLAY')
            pending.append(identity)
            continue
        boundary = event.get('type') == 'system' and event.get('subtype') == 'compact_boundary'
        require(not pending or boundary, 'READ_REPLAY_COMPACTION_BOUNDARY_REQUIRED')
        if boundary:
            meta = event.get('compactMetadata', {})
            segment = meta.get('preservedSegment', {})
            messages = meta.get('preservedMessages', {})
            summary = events[index+1] if index+1 < len(events) else {}
            require(event.get('sessionId') == session and event.get('isSidechain') is False
                    and isinstance(identity, str) and identity and identity not in seen
                    and meta.get('trigger') == 'auto'
                    and event.get('logicalParentUuid') in seen
                    and segment.get('tailUuid') == event.get('logicalParentUuid')
                    and segment.get('headUuid') in seen,
                    'COMPACTION_BOUNDARY_BINDING_REQUIRED')
            require(summary.get('type') == 'user' and summary.get('isCompactSummary') is True
                    and summary.get('isVisibleInTranscriptOnly') is True
                    and summary.get('isSidechain') is False
                    and summary.get('sessionId') == session
                    and summary.get('parentUuid') == identity
                    and isinstance(summary.get('uuid'), str) and summary['uuid'] not in seen
                    and summary['uuid'] == segment.get('anchorUuid') == messages.get('anchorUuid')
                    and not summary.get('origin') and not summary.get('promptSource')
                    and isinstance(summary.get('message', {}).get('content'), str)
                    and summary['message']['content'].strip(),
                    'COMPACTION_SUMMARY_BINDING_REQUIRED')
            receipts.append({'boundary_uuid': identity, 'summary_uuid': summary['uuid'],
                             'boundary_sha256': gate.digest(gate.encoded(event)),
                             'summary_sha256': gate.digest(gate.encoded(summary)),
                             'replayed_read_uuids': list(pending)})
            pending = []
        if event.get('isCompactSummary') is True:
            require(receipts and receipts[-1]['summary_uuid'] == identity
                    and index and events[index-1].get('uuid') == event.get('parentUuid')
                    and receipts[-1]['summary_sha256'] == gate.digest(gate.encoded(event)),
                    'UNBOUND_COMPACTION_SUMMARY')
        else:
            view.append(event)
        if identity:
            require(identity not in seen, 'JOURNAL_EVENT_ID_REUSED')
            seen[identity] = event
    require(not pending, 'READ_REPLAY_COMPACTION_BOUNDARY_REQUIRED')
    return view, receipts


def _session(journal, report, statement, report_path, *, server_launch=None):
    events = [parsed(line) for line in journal.splitlines() if line.strip()]
    require(events and len(events) <= 20000, 'BOUNDED_SESSION_ORIGINAL_REQUIRED')
    session = statement['session_id']
    require(isinstance(session, str) and re.fullmatch(
        r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', session), 'ACTUAL_SESSION_REQUIRED')
    events, compactions = _compacted_session_view(events, session)
    calls = {}; results = {}; models = set(); usage = {}
    for index, event in enumerate(events):
        if event.get('type') not in {'assistant', 'user'}:
            continue
        require(event.get('sessionId') == session, 'SESSION_ID_CHANGED')
        message = event.get('message', {}); content = message.get('content', [])
        if event['type'] == 'assistant':
            model = message.get('model')
            require(isinstance(model, str) and model.startswith('claude-'), 'ACTUAL_CLAUDE_MODEL_REQUIRED')
            models.add(model)
            if 'usage' in message:
                identity = message.get('id')
                require(isinstance(identity, str) and identity, 'USAGE_MESSAGE_ID_REQUIRED')
                # Streaming fragments can revise usage; preserve every distinct
                # observed fragment. Do not pretend these are a billing total.
                fragments = usage.setdefault(identity, [])
                if message['usage'] not in fragments: fragments.append(message['usage'])
        if not isinstance(content, list): continue
        for item in content:
            if not isinstance(item, dict): continue
            if event['type'] == 'assistant' and item.get('type') == 'tool_use':
                args = item.get('input', {})
                if item.get('name') == 'Write' and args.get('file_path') == report_path:
                    key = item.get('id'); require(key and key not in calls, 'DUPLICATE_REPORT_WRITE')
                    calls[key] = (index, args.get('content'), model)
            elif event['type'] == 'user' and item.get('type') == 'tool_result':
                key = item.get('tool_use_id')
                require(key not in results, 'DUPLICATE_TOOL_RESULT')
                results[key] = (index, item.get('is_error', False))
    matching = [(key, row) for key, row in calls.items()
                if row[1] == report.decode('utf-8') and key in results
                and results[key][0] > row[0] and results[key][1] is False]
    require(len(matching) == 1, 'ORIGINAL_SUCCESSFUL_CLAUDE_WRITE_REQUIRED')
    key, final = matching[0]
    require(final[0] == max(row[0] for row in calls.values()), 'REPORT_WAS_SUPERSEDED')
    units = manual_units(events, session) if server_launch is None else server_launch.units(events, session)
    return {'session_id': session, 'provider_model': final[2], 'observed_models': sorted(models),
            'report_write_tool_use_id': key, 'usage_fragments_by_message': usage,
            'manual_units': units if server_launch is None else {},
            **({'prepaid_units': units} if server_launch is not None else {}),
            'compactions': compactions,
            'accounting_reconciled': False, 'provider_attestation_claimed': False}


def validate(manifest_raw, raw, proposal_raw, source_files):
    """Pure source/integration validation. Never writes a qualifying REVIEW event."""
    manifest = parsed(manifest_raw); proposal = parsed(proposal_raw)
    require(isinstance(manifest, dict) and set(manifest) == {
        'schema', 'base_source', 'source', 'proposal_sha256', 'files', 'report_path',
        'changes_sha256', 'change_bindings_sha256'}, 'MANIFEST_SCHEMA')
    from orchestrator import server_terminal_review as server
    profile = manifest['schema']
    is_server = profile == server.PROFILE
    require(profile in (PROFILE, server.PROFILE) and manifest['base_source'] == BASE_SOURCE
            and manifest['source'] == proposal['source']
            and proposal.get('review_profile') == profile
            and 'review_plan_sha256' not in proposal
            and manifest['proposal_sha256'] == gate.digest(proposal_raw), 'EXACT_SOURCE_PROPOSAL_REQUIRED')
    gate.pin(manifest['source'], 40)
    require({name: gate.digest(value) for name, value in source_files.items()}
            == proposal['source_files'], 'SOURCE_INVENTORY_CHANGED')
    required = manifest['files']
    launch_names = server.original_names(raw) if is_server else set()
    require(isinstance(required, dict) and required
            and set(raw) == set(required) | {'report.md', 'session.jsonl'} | launch_names, 'EXACT_EVIDENCE_SET_REQUIRED')
    require(not {'report.md', 'session.jsonl'} & set(required), 'CYCLIC_MANIFEST_REFUSED')
    require(all(gate.digest(raw[name]) == gate.pin(sha) for name, sha in required.items()),
            'ORIGINAL_EVIDENCE_CHANGED')
    _authority(raw)
    require(all(raw.get('history/'+name) is not None
                and gate.digest(raw['history/'+name]) == sha for name, sha in PRIOR_REVIEWS.items()),
            'ORIGINAL_ADVERSE_REVIEWS_REQUIRED')
    statement = _statement(raw['report.md'], profile=profile)
    require(statement['source'] == manifest['source']
            and statement['resolution_of'] == BASE_SOURCE
            and statement['proposal_sha256'] == gate.digest(proposal_raw)
            and statement['manifest_sha256'] == gate.digest(manifest_raw), 'REVIEWED_BINDING_CHANGED')
    require(isinstance(manifest['report_path'], str) and Path(manifest['report_path']).is_absolute(),
            'ORIGINAL_REPORT_PATH_REQUIRED')
    launch = server.validate_launch(manifest_raw, raw, statement) if is_server else None
    session = _session(raw['session.jsonl'], raw['report.md'], statement, manifest['report_path'],
                       server_launch=launch)
    private = {gate.digest(value): value for value in raw.values()}
    require(private.get(gate.digest(proposal_raw)) == proposal_raw, 'EXACT_PROPOSAL_ORIGINAL_REQUIRED')
    for field in ('targets', 'previous_files'):
        require(isinstance(proposal[field], dict) and proposal[field], 'CONFIGURATION_INVENTORY_REQUIRED')
        for item in proposal[field].values():
            require(item['sha256'] in private, 'CONFIGURATION_ORIGINAL_MISSING')
    require(proposal['recovery_sha256'] in private, 'RECOVERY_ORIGINAL_MISSING')
    context_raw = private.get(manifest['changes_sha256'])
    require(context_raw is not None, 'CHANGE_CONTEXT_REQUIRED')
    context = parsed(context_raw); require(isinstance(context, list), 'CHANGE_CONTEXT_REQUIRED')
    sidecar = private.get(manifest['change_bindings_sha256'])
    require(sidecar is not None and parsed(sidecar) == changes.review_bindings(
        manifest['source'], gate.digest(proposal_raw), proposal['changes']), 'SELECTED_CHANGES_CHANGED')
    execution = {'metadata_projection': 'DERIVED_FROM_TERMINAL_ORIGINALS_NOT_NATIVE_RECEIPTS',
        'reviewed_commit': manifest['source'], 'request_sha256': gate.digest(manifest_raw),
        'response_sha256': gate.digest(raw['report.md']), 'protocol_sha256': gate.digest(raw['session.jsonl'])}
    result = {'terminal_profile': profile, 'terminal_session': session,
        'request': {'reviewed_commit': manifest['source'], 'change_bindings_sha256': manifest['change_bindings_sha256']},
        'response': {'session_id': session['session_id'], 'structured_output': statement},
        'execution': execution, 'changes': context, 'source_text': {}, 'private_text': private,
        'approval_confers_deployment_authority': False}
    gate.selected_review_applications(result, proposal_raw, manifest['source'])
    return result


def load(bundle, proposal_raw, source_files):
    # Reuse the existing exact protected tree, symlink, byte and export bounds.
    index_raw, raw = gate._inspection_inventory(Path(bundle)/'terminal-review')
    manifest_raw = raw.pop('manifest.json')
    review = validate(manifest_raw, raw, proposal_raw, source_files)
    evidence = {'terminal_review_index_sha256': gate.digest(index_raw),
        'terminal_review_manifest_sha256': gate.digest(manifest_raw),
        'terminal_review_report_sha256': gate.digest(raw['report.md']),
        'terminal_review_session_sha256': gate.digest(raw['session.jsonl']),
        'terminal_scope': 'SOURCE_INTEGRATION_ONLY',
        'terminal_accounting_validation': 'SEPARATE_INSTALL_REQUIREMENT',
        'terminal_native_receipts_claimed': False}
    return review, evidence


def manual_units(events, session):
    """Original interactive human requests, not streamed assistant/tool iterations.

    A recorded session fallback remains within the same request unit. All original
    usage/iteration fragments stay bound by the journal hash. Unknown user shapes
    require reconciliation; they are not silently omitted or charged twice.
    """
    result = {}; seen = set()
    for event in events:
        if event.get('type') != 'user': continue
        content = event.get('message', {}).get('content')
        if isinstance(content, list) and content and all(
                isinstance(x, dict) and x.get('type') == 'tool_result' for x in content): continue
        if event.get('isMeta') is True: continue
        require(not event.get('isSidechain') and not event.get('isCompactSummary')
                and not event.get('isSynthetic') and event.get('sessionId') == session
                and event.get('origin', {}).get('kind') == 'human'
                and event.get('promptSource') == 'typed'
                and isinstance(content, str) and content.strip(), 'MANUAL_REQUEST_SHAPE_RECONCILE')
        identity = event.get('uuid')
        require(isinstance(identity, str) and identity and identity not in seen,
                'MANUAL_REQUEST_ID_REQUIRED')
        seen.add(identity)
        unit = {'session_id': session, 'request_uuid': identity,
                'request_sha256': gate.digest(gate.encoded(event))}
        result[gate.digest(gate.encoded(unit))] = unit
    require(result, 'MANUAL_REQUEST_ORIGINAL_REQUIRED')
    return result


def accounting_event(unit_sha256, source):
    """Stable input to existing admit_server; performs no admission or retry."""
    gate.pin(unit_sha256); gate.pin(source, 40)
    return {'turn_id': gate.digest(gate.encoded({'schema': 'operator-terminal-late-charge/v1',
                    'unit_sha256': unit_sha256})), 'attempt': '1', 'source': source,
            'branch': 'astra/infrastructure-milestone-record', 'kind': 'astra_turn'}


def validate_accounting(accounting_raw, review, status, ledger_pin, state, policy,
                        allowed_sources, read_commit):
    """Validate real late-charge receipts/commits; never charge, reset or refund.

    read_commit is the installer's hash-checked protected ledger reader. Local
    derivation below proves the ordinary transition; it is not a minted receipt.
    Complete billing is not asserted: original usage, including fallback fragments,
    remains in the exact journal. Three interactive requests are three units, not
    29 assistant message fragments. Unknown request shapes fail at source import.
    """
    from orchestrator import dispatch_limiter as limiter
    account = parsed(accounting_raw)
    prepaid = review.get('terminal_profile') == 'server-terminal-review/v1'
    require(isinstance(account, dict) and set(account) == {'schema', 'manifest_sha256',
        'report_sha256', 'journal_sha256', 'policy_sha256', 'ledger_pin', 'cases'}
        and account['schema'] == ('server-terminal-accounting/v1' if prepaid else 'operator-terminal-accounting/v1'), 'ACCOUNTING_ORIGINAL_REQUIRED')
    execution = review['execution']
    require(all(account[k] == execution[v] for k, v in {
        'manifest_sha256': 'request_sha256', 'report_sha256': 'response_sha256',
        'journal_sha256': 'protocol_sha256'}.items()), 'ACCOUNTING_REVIEW_BINDING_CHANGED')
    limiter.validate(state); n = limiter.policy(policy)
    policy_sha = gate.digest(json.dumps(policy, sort_keys=True).encode())
    require(n == 48 and policy.get('server_semantics') == 'OPERATOR_AUTHORIZED_V1'
            and account['policy_sha256'] == state['policy_sha256'] == policy_sha,
            'ACCOUNTING_POLICY_CHANGED')
    gate.pin(ledger_pin, 40)
    require(account['ledger_pin'] == ledger_pin == status.get('pin')
            and all(status.get(k) == state[k] for k in ('count', 'day', 'sequence', 'halted')),
            'ACCOUNTING_AUTHENTICATED_STATE_CHANGED')
    require(state['halted'] is False and state['count'] < 2*n, 'ACCOUNTING_HALT_REMAINS')
    units = review['terminal_session']['prepaid_units' if prepaid else 'manual_units']; cases = account['cases']
    require(isinstance(cases, list) and len(cases) == len(units)
            and all(isinstance(c, dict) and set(c) == {'unit_sha256', 'event', 'receipt', 'state_after'}
                    for c in cases)
            and {c['unit_sha256'] for c in cases} == set(units), 'ACCOUNTING_CASE_COVERAGE_REQUIRED')
    # A retained object with matching JSON is not enough: every charge must
    # belong to the authenticated current ledger's actual parent chain.
    ancestry = set(); cursor = ledger_pin
    needed = {gate.pin(c['state_after'], 40) for c in cases}
    for _ in range(12000):
        ancestry.add(cursor)
        if needed <= ancestry: break
        parents = read_commit(cursor)['parents']
        require(len(parents) == 1 and parents[0] not in ancestry, 'ACCOUNTING_ANCESTRY_REQUIRED')
        cursor = gate.pin(parents[0], 40)
    require(needed <= ancestry, 'ACCOUNTING_ANCESTRY_BOUND')
    for case in cases:
        event, receipt = case['event'], case['receipt']
        limiter.validate_server_event(event)
        # Accounting proves an already charged event against original receipts,
        # authenticated ledger ancestry and the complete transition below. The
        # current execution allowlist cannot revoke that historical charge.
        # Keep allowed_sources in this API for existing callers; it grants no
        # authority here and remains enforced by all fresh admission paths.
        require(event == (units[case['unit_sha256']]['event'] if prepaid else
                              accounting_event(case['unit_sha256'], event['source'])),
                'ACCOUNTING_EXACT_CASE_EVENT_REQUIRED')
        require(isinstance(receipt, dict) and receipt.get('status') == 'ADMITTED'
                and receipt.get('duplicate_admission') is False, 'ACCOUNTING_ORIGINAL_CHARGE_REQUIRED')
        if prepaid:
            require(receipt == units[case['unit_sha256']]['receipt'],
                    'ACCOUNTING_LAUNCH_ADMISSION_CHANGED')
        parent = gate.pin(receipt['state_before'], 40); after_pin = gate.pin(case['state_after'], 40)
        before = read_commit(parent)['state']; after = read_commit(after_pin)
        limiter.validate(before); limiter.validate(after['state'])
        require(after['parents'] == [parent] and before['policy_sha256'] == policy_sha
                and before['halted'] is False, 'ACCOUNTING_ORIGINAL_PARENT_REQUIRED')
        key = 'server:'+event['turn_id']+':'+event['attempt']
        require(key not in before['events'] and key in state['events'], 'ACCOUNTING_CHARGE_NOT_NEW')
        expected = copy.deepcopy(before); day = receipt['day']
        require(re.fullmatch(r'\d{4}-\d{2}-\d{2}', day)
                and (before['day'] is None or day >= before['day'])
                and before['count'] < 2*n, 'ACCOUNTING_CHARGE_WINDOW')
        if expected['day'] != day: expected.update(day=day, count=0)
        expected['count'] += 1; expected['sequence'] += 1
        notice = '2N' if expected['count'] >= 2*n else 'N' if expected['count'] == n else None
        expected['halted'] = expected['count'] >= 2*n
        entry = {'source': event['source'], 'branch': event['branch'], 'kind': event['kind'],
            'day': day, 'count': expected['count'], 'notification': notice, 'halted': expected['halted']}
        expected['events'][key] = entry
        if notice: expected['notifications'][str(expected['sequence'])+':'+notice] = {
            'threshold': notice, 'count': expected['count'], 'day': day}
        original_response = {'status': 'ADMITTED', 'duplicate_admission': False, **entry,
            'state_before': parent, 'pending_notifications': limiter.pending_notifications(expected)}
        require(after['state'] == expected and receipt == original_response
                and state['resets'] == expected['resets']
                and all(state['notifications'].get(k) == value for k, value in expected['notifications'].items())
                and all(state['events'].get(k) == value for k, value in expected['events'].items()),
                'ACCOUNTING_ORIGINAL_TRANSITION_CHANGED')
    return {'schema': ('server-terminal-accounting-verification/v1' if prepaid else
                       'operator-terminal-accounting-verification/v1'),
            'accounting_sha256': gate.digest(accounting_raw), 'ledger_pin': ledger_pin,
            'policy_sha256': policy_sha,
            ('prepaid_units' if prepaid else 'manual_units'): sorted(units),
            'late_charge': not prepaid, 'retroactive_pre_admission_claimed': False,
            'usage_original_sha256': execution['protocol_sha256']}
