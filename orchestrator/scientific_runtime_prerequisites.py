"""Require reviewed runtime prerequisites inside the scientific evidence capture.

The existing source-bound primary application selects a bounded set of completed
proofs. This checks delivery, not scientific acceptance or permission to execute.
No model paths, extra namespace, provider call, or reconstructed proof is allowed.
"""
import json
from pathlib import Path

from orchestrator import change_requests as changes
from orchestrator import scientific_evidence_access as access
from orchestrator.disposition_context import _primary_change
from orchestrator.hosted_cycle import encoded as packet_bytes

FIELD = 'runtime_prerequisites'
MAX_PREREQUISITES = 8


def require(ok, reason):
    if not ok:
        raise ValueError('SCIENTIFIC_PREREQUISITE_' + reason)


def validate(specs):
    require(isinstance(specs, list) and 1 <= len(specs) <= MAX_PREREQUISITES,
            'BOUNDED_NONEMPTY_SELECTION_REQUIRED')
    require(len(changes.encoded(specs)) <= 12000, 'SELECTION_BYTES_EXCEEDED')
    names = set()
    for item in specs:
        require(isinstance(item, dict) and set(item) == {
            'request', 'event', 'source', 'authorization', 'technical_event',
            'status', 'completed_original'}, 'EXACT_SELECTION_REQUIRED')
        for key in ('request', 'event', 'authorization'):
            access.pin(item[key])
        access.pin(item['source'], 40)
        event = item['technical_event']
        require(isinstance(event, dict) and set(event) == {
            'turn_id', 'attempt', 'source', 'branch', 'kind'} and
            event['source'] == item['source'] and event['attempt'] == '1' and
            event['kind'] == 'astra_turn' and
            event['branch'] == 'astra/infrastructure-milestone-record',
            'TECHNICAL_EVENT_REQUIRED')
        access.pin(event['turn_id'])
        require(isinstance(item['status'], str) and 0 < len(item['status']) <= 160,
                'COMPLETION_STATUS_REQUIRED')
        ref = item['completed_original']
        require(isinstance(ref, dict) and set(ref) == {'artifact', 'sha256', 'size'},
                'ORIGINAL_REFERENCE_REQUIRED')
        access.pin(ref['sha256'])
        name = ref['artifact']
        require(isinstance(name, str) and name.startswith('evidence/') and
                len(Path(name).parts) == 2 and '..' not in Path(name).parts and
                type(ref['size']) is int and 1 <= ref['size'] <= 100000,
                'BOUNDED_ORIGINAL_REQUIRED')
        identity = (item['request'], item['event'])
        require(identity not in names, 'DUPLICATE_SELECTION')
        names.add(identity)
    return specs


def selected(config, packet, source, *, owner=None):
    """Read the exact native application; existing admission still checks approval."""
    primary = _primary_change(packet)
    state = changes.load(Path(config['change_request_store']) / primary['request_id'], owner=owner)
    app = next((e for e in state['events'] if e['identity'] == primary['applied_event']), None)
    require(app is not None and app['event'] == 'APPLIED', 'APPLICATION_REQUIRED')
    binding = app['payload']['result_binding']
    require(binding.get('source') == source, 'APPLICATION_SOURCE_CHANGED')
    if FIELD not in binding:
        return app, []  # Historical applications did not declare this contract.
    return app, validate(binding[FIELD])


def _body(capture, name, kind):
    rows = [row for row in capture['manifest']['records'] if row['name'] == name]
    require(len(rows) == 1 and rows[0]['kind'] == kind, 'NOT_IN_CAPTURE')
    row = rows[0]
    raw = capture['payloads'].get(row['sha256'])
    require(isinstance(raw, bytes) and access.sha(raw) == row['sha256'] and
            len(raw) == row['utf8_bytes'], 'CAPTURE_BYTES_CHANGED')
    return raw


def verify_capture(capture, specs, *, source, task_binding):
    """Validate the same immutable content delivered to both roles, not a later read."""
    validate(specs)
    require(capture['manifest']['source'] == source and
            capture['manifest']['task_binding'] == task_binding, 'TASK_CAPTURE_CHANGED')
    verified = []
    for item in specs:
        rows = [row for row in capture['manifest']['records']
                if row['kind'] == 'change_event' and
                row['provenance'].get('request') == item['request'] and
                row['provenance'].get('event') == item['event']]
        require(len(rows) == 1, 'COMPLETION_NOT_IN_CAPTURE')
        event = json.loads(_body(capture, rows[0]['name'], 'change_event'))
        require(event['identity'] == item['event'] and event['request_identity'] == item['request']
                and event['event'] == 'DISPOSITION', 'COMPLETION_EVENT_CHANGED')
        expected = {key: value for key, value in item.items() if key not in ('request', 'event')}
        require(event['payload'].get('runtime_verification') == expected,
                'COMPLETION_BINDING_CHANGED')
        ref = item['completed_original']
        name = 'change/' + item['request'] + '/' + ref['artifact']
        raw = _body(capture, name, 'change_artifact')
        require(access.sha(raw) == ref['sha256'] and len(raw) == ref['size'], 'ORIGINAL_CHANGED')
        proof = json.loads(raw)
        require(isinstance(proof, dict) and proof.get('status') == item['status'] and
                proof.get('source') == item['source'] and
                proof.get('event') == item['technical_event'] and
                proof.get('scientific_authority') is False and
                type(proof.get('models_launched_by_check')) is int and
                proof['models_launched_by_check'] == 0, 'COMPLETED_PROOF_CHANGED')
        verified.append({'name': name, 'sha256': ref['sha256'], 'event': item['event']})
    return verified


def verify(config, packet, source, capture, *, owner=None):
    app, specs = selected(config, packet, source, owner=owner)
    from orchestrator.investigator_eligibility263_reconsideration import verify_captured_originals
    verify_captured_originals(packet, source, capture, specs)
    if not specs:
        return []
    # The application selecting these prerequisites must itself belong to the
    # authenticated immutable prefix; an external current read is insufficient.
    name = 'change/' + app['request_identity'] + '/event/' + str(app['sequence']) + '.json'
    require(json.loads(_body(capture, name, 'change_event')) == app,
            'APPLICATION_NOT_IN_CAPTURE')
    result = verify_capture(capture, specs, source=source, task_binding=access.sha(packet_bytes(packet)))
    return result
