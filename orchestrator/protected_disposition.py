"""Protected originals for a single new-source campaign disposition successor.

The old event remains immutable. A refused input is not a model answer or retry
permission. Only the installed typed successor verifier can permit the new stage.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from orchestrator.dispatch_limiter import validate_server_event
from orchestrator.hosted_cycle import encoded


def _require_root():
    if os.getuid() != 0:
        raise ValueError('DISPOSITION_PROTECTED_ROOT_REQUIRED')


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _signature(info):
    return (info.st_dev, info.st_ino, info.st_uid, info.st_gid,
            info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _directory(path):
    info = path.lstat()
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != 0o700
            or any(p.is_symlink() for p in (path, *path.parents))):
        raise ValueError('DISPOSITION_PROTECTED_DIRECTORY_REQUIRED')


def _original(path, limit=1500000):
    info = path.lstat()
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != 0o600 or info.st_size > limit
            or any(p.is_symlink() for p in (path, *path.parents))):
        raise ValueError('DISPOSITION_PROTECTED_ORIGINAL_REQUIRED')
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as stream:
        before = os.fstat(stream.fileno())
        raw = stream.read(limit + 1)
        after = os.fstat(stream.fileno())
    if (len(raw) > limit or _signature(info) != _signature(before)
            or _signature(before) != _signature(after)
            or _signature(after) != _signature(path.lstat())):
        raise ValueError('DISPOSITION_ORIGINAL_MOVED')
    return raw


def _lock_original(root, stream):
    path = root / 'branch.lock'
    if _original(path, 1) != b'' or _signature(path.lstat()) != _signature(os.fstat(stream.fileno())):
        raise ValueError('DISPOSITION_FIXED_WRITER_LOCK_CHANGED')


def _event(broker, body):
    if not isinstance(body, dict) or set(body) != {'event'}:
        raise ValueError('DISPOSITION_REFUSAL_EVENT_ONLY')
    event = body['event']
    validate_server_event(event)
    if (not re.fullmatch('[0-9a-f]{64}', event.get('turn_id', ''))
            or not re.fullmatch('[1-9][0-9]*', event.get('attempt', ''))):
        raise ValueError('DISPOSITION_REFUSAL_EVENT_SOURCE')
    broker.historical_event(event)
    return event


def _locked_refusal(broker, body, stream):
    """Internal only: caller owns this exact broker branch lock; no wire flag."""
    _require_root()
    event = _event(broker, body)
    root = Path(broker.config['turn_root'])
    folder = root / (event['turn_id'] + '-' + event['attempt'])
    _directory(root); _directory(folder); _lock_original(root, stream)
    allowed = {'disposition.request.json', 'disposition.input-refused.json'}
    if {p.name for p in folder.iterdir() if p.name.startswith('disposition.')} != allowed:
        raise ValueError('DISPOSITION_STARTED_OUTPUT_OR_UNKNOWN_ORIGINAL')
    # No input, start, process, answer or receipt is compatible with this proof.
    names = ['binding.json', 'packet.json', *sorted(allowed)]
    suffixes = ('.request.json', '.started.json', '.ended.json', '.process.json',
                '.process-identity.json', '.receipt.json', '.md', '.stdout',
                '.stderr', '.input.md', '.operating-context.json')
    names += [stage + suffix for stage in ('continuation', 'review') for suffix in suffixes]
    raw = {name: _original(folder / name) for name in names}
    packet = broker.stage_packet(body)
    if (packet.get('status') != 'COMPLETE'
            or raw['packet.json'] != encoded(packet['packet'])
            or _sha(raw['packet.json']) != packet['packet_sha256']
            or raw['binding.json'] != encoded({'event': event, 'packet_sha256': packet['packet_sha256']})):
        raise ValueError('DISPOSITION_ORIGINAL_PACKET_CHANGED')
    request = json.loads(raw['disposition.request.json'])
    refusal = json.loads(raw['disposition.input-refused.json'])
    if (raw['disposition.request.json'] != encoded(request)
            or set(request) != {'prompt_sha256'}
            or not isinstance(request['prompt_sha256'], str)
            or re.fullmatch('[0-9a-f]{64}', request['prompt_sha256']) is None
            or raw['disposition.input-refused.json'] != encoded(refusal)
            or set(refusal) != {'status', 'measurement', 'provider_calls', 'automatic_retry'}
            or refusal['status'] != 'PREFLIGHT_INPUT_REFUSED'
            or type(refusal['provider_calls']) is not int or refusal['provider_calls'] != 0
            or refusal['automatic_retry'] is not False):
        raise ValueError('DISPOSITION_EXACT_PREFLIGHT_REFUSAL_REQUIRED')
    measurement = refusal['measurement']
    expected = {'schema', 'stage', 'family', 'characters', 'utf8_bytes', 'input_sha256',
                'limit_basis', 'limit_characters', 'provider_calls', 'provider_limit_verified'}
    if (not isinstance(measurement, dict) or set(measurement) != expected
            or measurement['schema'] != 'hosted-final-input-measurement/v1'
            or measurement['stage'] != 'disposition' or measurement['family'] != 'codex'
            or measurement['limit_basis'] != 'OBSERVED_CODEX_INPUT_CHARACTERS'
            or type(measurement['limit_characters']) is not int or measurement['limit_characters'] != 1048576
            or measurement['provider_limit_verified'] is not True
            or type(measurement['provider_calls']) is not int or measurement['provider_calls'] != 0
            or type(measurement['characters']) is not int or measurement['characters'] <= 1048576
            or type(measurement['utf8_bytes']) is not int
            or not measurement['characters'] <= measurement['utf8_bytes'] <= 4 * measurement['characters']
            or not isinstance(measurement['input_sha256'], str)
            or re.fullmatch('[0-9a-f]{64}', measurement['input_sha256']) is None):
        raise ValueError('DISPOSITION_EXACT_INPUT_MEASUREMENT_REQUIRED')
    stages = {}
    for stage in ('continuation', 'review'):
        result = broker.stage_status({'event': event, 'stage': stage})
        receipt = json.loads(raw[stage + '.receipt.json'])
        ended = json.loads(raw[stage + '.ended.json'])
        context = json.loads(raw[stage + '.operating-context.json'])
        if (result.get('status') != 'COMPLETE' or result.get('packet_sha256') != packet['packet_sha256']
                or result.get('receipt') != receipt or receipt.get('stage') != stage
                or type(receipt.get('returncode')) is not int or receipt['returncode'] != 0
                or type(ended.get('returncode')) is not int or ended['returncode'] != 0
                or context.get('verified_source_commit') != event['source']
                or context.get('task_packet') != {'name': 'packet.json', 'sha256': packet['packet_sha256']}):
            raise ValueError('DISPOSITION_COMPLETE_ORIGINAL_STAGES_REQUIRED')
        stages[stage] = result
    # Keep the proof stable through the last read, including absent start/output.
    if (any(_original(folder / name) != value for name, value in raw.items())
            or {p.name for p in folder.iterdir() if p.name.startswith('disposition.')} != allowed):
        raise ValueError('DISPOSITION_ORIGINAL_CHANGED_DURING_PROOF')
    _lock_original(root, stream)
    return {'schema': 'protected-disposition-refusal/v1', 'status': 'PREFLIGHT_REFUSED_NO_PROVIDER',
            'event': event, 'packet': packet['packet'], 'packet_sha256': packet['packet_sha256'],
            'originals': {name: raw[name].decode('utf-8') for name in sorted(allowed)},
            'file_sha256': {name: _sha(raw[name]) for name in sorted(allowed)},
            'stages': stages, 'active': False, 'started': False,
            'answer_present': False, 'receipt_present': False, 'admissions': 0}


def disposition_refusal(broker, body):
    """Read original-only proof under the broker's fixed existing writer lock."""
    _require_root()
    _event(broker, body)
    root = Path(broker.config['turn_root']); _directory(root)
    path = root / 'branch.lock'; _original(path, 1)
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError('DISPOSITION_MODEL_WRITER_ACTIVE') from error
        return _locked_refusal(broker, body, stream)


def successor_packet(packet, stage):
    """A narrow format selector, not authority to skip the original checks."""
    if not isinstance(packet, dict):
        raise ValueError('MODEL_PACKET_SCHEMA')
    if packet.get('trigger') != 'linked-campaign-disposition' and 'linked_disposition' not in packet:
        return False
    if (set(packet) != {'version', 'trigger', 'linked_disposition', 'reviewer_evidence', 'recorded_changes'}
            or type(packet['version']) is not int or packet['version'] != 1
            or packet['trigger'] != 'linked-campaign-disposition' or stage != 'disposition'
            or not isinstance(packet['linked_disposition'], dict)
            or packet['linked_disposition'].get('schema') != 'linked-campaign-disposition/v1'):
        raise ValueError('SINGLE_LINKED_DISPOSITION_STAGE_REQUIRED')
    return True


def verify_successor_launch(broker, body, stream):
    """Validate as the controller UID, then bind fresh root originals under EX lock."""
    if not successor_packet(body['packet'], body['stage']):
        raise ValueError('LINKED_DISPOSITION_PACKET_REQUIRED')
    from orchestrator.protected_scientific_jobs import controller_configuration
    from orchestrator.protected_investigator import verify_subprocess
    config = controller_configuration(broker)
    if config['source'] != body['event']['source']:
        raise ValueError('LINKED_DISPOSITION_CURRENT_SOURCE_REQUIRED')
    result = verify_subprocess(broker, config, 'disposition_launch', body, disposition_lock=stream)
    keys = {'status', 'event', 'packet_sha256', 'original_event', 'original_proof_sha256', 'request', 'source', 'stage'}
    link = body['packet']['linked_disposition']
    if (not isinstance(result, dict) or set(result) != keys
            or result['status'] != 'VERIFIED_LINKED_DISPOSITION_LAUNCH'
            or result['event'] != body['event'] or result['source'] != config['source']
            or result['stage'] != 'disposition' or result['packet_sha256'] != _sha(encoded(body['packet']))
            or result['request'] != link.get('request')):
        raise ValueError('LINKED_DISPOSITION_VERIFIER_BINDING_CHANGED')
    proof = _locked_refusal(broker, {'event': result['original_event']}, stream)
    original = body['packet']['reviewer_evidence']['original']
    if (not isinstance(original, dict)
            or original.get('schema') != 'disposition-successor-original-proof/v1'
            or original.get('origin_event') != result['original_event']
            or original.get('packet') != proof['packet']
            or original.get('protected_original') != {k: v for k, v in proof.items() if k != 'packet'}
            or result['original_proof_sha256'] != _sha(encoded(original))
            or result['original_proof_sha256'] != link.get('original_proof_sha256')
            or result['original_event']['source'] == body['event']['source']
            or result['original_event']['turn_id'] == body['event']['turn_id']
            or link.get('source') != body['event']['source']
            or link.get('origin_task') != result['original_event']['turn_id']
            or link.get('origin_source') != result['original_event']['source']
            or body['event']['attempt'] != '1'):
        raise ValueError('LINKED_DISPOSITION_OLD_NEW_SOURCE_OR_PROOF_CHANGED')
    return result


def _locked_unstarted(broker, body, stream):
    """Narrow authenticated absence proof, not a general ledger lookup."""
    _require_root()
    from orchestrator import disposition_successors as d
    from orchestrator.protected_scientific_jobs import controller_configuration
    from orchestrator.dispatch_limiter import policy, validate
    from orchestrator.remote_supervisor import checked_source
    if (not isinstance(body,dict) or set(body) != {'origin_task','request','source','candidate_request'}):
        raise ValueError('DISPOSITION_UNSTARTED_REQUEST_SCHEMA')
    config = controller_configuration(broker)
    checked_source(config['source_root'],config['source'])
    if body['source'] != config['source']:
        raise ValueError('DISPOSITION_UNSTARTED_CURRENT_SOURCE_REQUIRED')
    root = Path(broker.config['turn_root']); _directory(root); _lock_original(root,stream)
    identity = d.pin(body['origin_task'])
    _, saved, _, _, predecessor = d._predecessor(config,identity)
    # This exact hash-bound saved predecessor is deliberately NOT admitted. Its
    # absence proof must survive retirement from fresh execution permission;
    # _predecessor validates its original request/proof/history, not an allowlist.
    if (saved['identity'] != d.pin(body['request']) or saved['source'] == config['source']):
        raise ValueError('DISPOSITION_UNSTARTED_PREDECESSOR_BINDING')
    events = [d.event(saved)]
    candidate = body['candidate_request']
    if candidate is not None:
        value = d._validate_revision(config,identity,
            d._load_folder(d._revision_root(config,identity)/d.pin(candidate),identity))
        if value[1]['identity'] != candidate or value[1]['source'] != config['source']:
            raise ValueError('DISPOSITION_UNSTARTED_CANDIDATE_BINDING')
        d._unstarted(value[0],config)
        events.append(d.event(value[1]))
    paths = [root/(event['turn_id']+'-'+event['attempt']) for event in events]
    if any(path.exists() or path.is_symlink() for path in paths):
        raise ValueError('DISPOSITION_PROTECTED_TURN_ALREADY_PRESENT')
    n = policy(broker.config['policy'])
    expected_policy = hashlib.sha256(json.dumps(broker.config['policy'],sort_keys=True).encode()).hexdigest()
    with broker.authentication():
        pin, state = broker.ledger.read()
        validate(state)
        if state['policy_sha256'] != expected_policy:
            raise ValueError('DISPOSITION_UNSTARTED_LEDGER_HALTED_OR_CHANGED')
        if any('server:'+event['turn_id']+':'+event['attempt'] in state['events'] for event in events):
            raise ValueError('DISPOSITION_PREDECESSOR_OR_CANDIDATE_ALREADY_ADMITTED')
        # Only an immutable, already selected revision can finish its ordinary
        # admitted turn at the latched threshold. No caller-supplied bypass bit.
        admitted = None
        selection = d._revision_root(config,identity)/'selection.json'
        if candidate is None and (selection.exists() or selection.is_symlink()):
            _, selected, _, _ = d._load(config,identity)
            current = d.event(selected)
            entry = state['events'].get('server:'+current['turn_id']+':'+current['attempt'])
            if (selected['source'] == config['source'] and isinstance(entry,dict)
                    and all(entry.get(k) == current[k] for k in ('source','branch','kind'))):
                admitted = current
        if (state['halted'] or state['count'] >= 2*n) and admitted is None:
            raise ValueError('DISPOSITION_UNSTARTED_LEDGER_HALTED_OR_CHANGED')
        after_pin, after = broker.ledger.read()
    if (pin != after_pin or state != after
            or any(path.exists() or path.is_symlink() for path in paths)
            or d._predecessor(config,identity)[4] != predecessor):
        raise ValueError('DISPOSITION_UNSTARTED_PROOF_MOVED')
    _lock_original(root,stream)
    return {'status':'VERIFIED_UNSTARTED_DISPOSITION','origin_task':identity,
        'request':saved['identity'],'source':config['source'],'event':events[0],
        'candidate_request':candidate,'predecessor':predecessor,'control':d._control(config),
        'current_admitted_event':admitted,
        'ledger':{'pin':pin,'sequence':state['sequence'],'count':state['count'],
                  'day':state['day'],'halted':state['halted'],'policy_sha256':state['policy_sha256']},
        'models':0,'admissions':0}


def disposition_unstarted(broker, body):
    _require_root()
    root = Path(broker.config['turn_root']); _directory(root)
    path = root/'branch.lock'; _original(path,1)
    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOFOLLOW),'rb') as stream:
        try: fcntl.flock(stream,fcntl.LOCK_SH|fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError('DISPOSITION_MODEL_WRITER_ACTIVE') from error
        return _locked_unstarted(broker,body,stream)
