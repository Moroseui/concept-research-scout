"""Bounded discovery of immutable scientific evidence, never an authority grant.

This reader uses records exported by the existing authenticated change reader.
The scientific runner must bind the capture and actual service identity. No tool
accepts a filesystem path, command, verifier, permission or new authority.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from orchestrator import change_requests as changes
from orchestrator.hosted_cycle import encoded, immutable
from orchestrator.git_publication import scan

SCHEMA = 'scientific-evidence-capture/v1'
RECORD_KINDS = frozenset(('change_request', 'change_event', 'change_artifact',
    'linked_disposition_original', 'scientific_stage_output', 'task_packet_original', 'formal_request_evidence',
    'scientific_task_original', 'continuing_context_original', 'completed_operation_result',
    'scientific_completion_observation', 'source_policy_document'))
MAX_RECORDS = 10000
MAX_RECORD_BYTES = 100000  # Existing native change-record bound, not raised.
NATIVE_RESULT_BYTES = 1500000  # Existing immutable text storage ceiling; never truncates.
PAGE_RECORDS = 20
SEARCH_RECORDS = 100
READ_CHARACTERS = 8192
REPLY_BYTES = 65536


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(value, length=64):
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{'+str(length)+'}', value) is None:
        raise ValueError('SCIENTIFIC_EVIDENCE_EXACT_IDENTITY_REQUIRED')
    return value


def _artifacts(value):
    if isinstance(value, dict):
        if 'artifact' in value and 'sha256' in value:
            yield value
        for child in value.values():
            yield from _artifacts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _artifacts(child)


def _maximum(kind):
    if kind == 'continuing_context_original':
        return 750000  # Existing continuing-evidence native storage bound.
    if kind == 'completed_operation_result':
        return NATIVE_RESULT_BYTES  # Existing scientific original capture ceiling; native reader is stricter where applicable.
    return NATIVE_RESULT_BYTES if kind in ('linked_disposition_original', 'task_packet_original', 'formal_request_evidence', 'scientific_task_original') else MAX_RECORD_BYTES


def _add(records, payloads, name, kind, raw, provenance):
    if kind not in RECORD_KINDS or len(raw) > _maximum(kind):
        raise ValueError('SCIENTIFIC_EVIDENCE_NATIVE_RECORD_BOUND')
    body = raw.decode('utf-8')
    # Preserve every original byte. Text cache names confer no scan exception
    # or public export permission on the source evidence.
    identity = sha(raw)
    scan('scientific-evidence/'+identity+'.txt', raw)
    row = {'name':name,'kind':kind,'sha256':identity,'utf8_bytes':len(raw),
           'characters':len(body),'provenance':provenance}
    if name in records and records[name] != row:
        raise ValueError('SCIENTIFIC_EVIDENCE_RECORD_IDENTITY_CONFLICT')
    if identity in payloads and payloads[identity] != raw:
        raise ValueError('SCIENTIFIC_EVIDENCE_CONTENT_IDENTITY_CONFLICT')
    records[name] = row; payloads[identity] = raw
    if len(records) > MAX_RECORDS:
        raise ValueError('SCIENTIFIC_EVIDENCE_SCOPE_CAPACITY')


def capture_changes(store, request_ids, *, source, task_binding, expected_prefixes=None, owner=None):
    """Native originals first; no selected-body list or inferred settlement.

    The caller supplies the already authorized task's request namespace. It is
    not a model-selected path. Every record/artifact in those request chains is
    discoverable. The namespace-selection caller still requires separate review.
    """
    pin(source, 40); pin(task_binding)
    if (not isinstance(request_ids, list) or not 1 <= len(request_ids) <= 32
            or len(set(request_ids)) != len(request_ids)):
        raise ValueError('SCIENTIFIC_EVIDENCE_REQUEST_SCOPE_REQUIRED')
    if expected_prefixes is not None and (
            not isinstance(expected_prefixes, dict) or set(expected_prefixes) != set(request_ids)):
        raise ValueError('SCIENTIFIC_EVIDENCE_EXACT_PREFIX_SCOPE_REQUIRED')
    records = {}; payloads = {}; heads = {}
    def add(name, kind, raw, provenance):
        _add(records, payloads, name, kind, raw, provenance)
    for identity in sorted(request_ids):
        pin(identity); folder = Path(store)/identity
        state = changes.load(folder, owner=owner)
        if expected_prefixes is not None:
            from orchestrator import reviewed_history as history
            expected = expected_prefixes[identity]
            if (not isinstance(expected, dict) or set(expected) !=
                    {'event_count', 'head_sha256', 'index_sha256'} or
                    type(expected['event_count']) is not int or
                    not 1 <= expected['event_count'] <= len(state['events'])):
                raise ValueError('SCIENTIFIC_EVIDENCE_NATIVE_PREFIX_REQUIRED')
            count = expected['event_count']
            prefix = {'request': state['request'], 'events': state['events'][:count],
                      'head_sha256': history.row(state['events'][count-1])['original_sha256']}
            if (prefix['head_sha256'] != expected['head_sha256'] or
                    history.sha(history.index(prefix)) != expected['index_sha256']):
                raise ValueError('SCIENTIFIC_EVIDENCE_NATIVE_PREFIX_CHANGED')
            state = prefix
        heads[identity] = {'head_sha256': state['head_sha256'], 'event_count': len(state['events'])}
        request_raw = changes._read(folder/'request.json', owner=owner)
        add('change/'+identity+'/request.json', 'change_request', request_raw,
            {'request': identity, 'source': state['request']['target']['source']})
        captured_events = {}; captured_artifacts = {}
        for event in state['events']:
            basename = f"{event['sequence']:04d}-{event['identity']}.json"
            raw = changes._read(folder/'events'/basename, owner=owner)
            if json.loads(raw) != event:
                raise ValueError('SCIENTIFIC_EVIDENCE_NATIVE_RECORD_CHANGED_DURING_CAPTURE')
            captured_events[basename] = raw
            add('change/'+identity+'/event/'+str(event['sequence'])+'.json', 'change_event', raw,
                {'request': identity, 'event': event['identity'], 'sequence': event['sequence'],
                 'event_kind': event['event'], 'actor': event['actor'],
                 'recorded_at_utc': event['recorded_at_utc']})
        for value in [state['request'], *state['events']]:
            for descriptor in _artifacts(value):
                name = descriptor['artifact']
                raw = changes._read(folder/name, owner=owner)
                if sha(raw) != descriptor['sha256'] or len(raw) != descriptor.get('size', len(raw)):
                    raise ValueError('SCIENTIFIC_EVIDENCE_NATIVE_ARTIFACT_CHANGED')
                captured_artifacts[name] = raw
                add('change/'+identity+'/'+name, 'change_artifact', raw,
                    {'request': identity, 'artifact': name})
        # Validate the bytes actually captured, not just an earlier load. Append
        # after this snapshot does not silently extend its authenticated prefix.
        verified = changes.validate_originals(request_raw, captured_events, captured_artifacts.__getitem__)
        if verified != state:
            raise ValueError('SCIENTIFIC_EVIDENCE_CAPTURE_PREFIX_CHANGED')
    manifest = {'schema': SCHEMA, 'source': source, 'task_binding': task_binding,
        'request_heads': heads, 'records': [records[k] for k in sorted(records)],
        'semantics': 'Evidence originals; no approval, settlement, inspection or scientific acceptance inferred.'}
    return {'manifest': manifest, 'payloads': payloads}



def capture_task_changes(store, packet, *, source, owner=None):
    """Derive scope from the existing validated task, never a prepared name list.

    The full native store is checked before exporting the exact saved prefix.
    Later append-only history cannot alter that snapshot. This is historical
    evidence availability, not current approval, eligibility or execution authority.
    The caller must still perform its current native admission/authority checks.
    """
    from orchestrator import disposition_context, reviewed_history
    pin(source, 40)
    from orchestrator import current_scientific_input
    if current_scientific_input.is_current(packet):
        result = current_scientific_input.authenticate_capture(store, packet, source, owner=owner)
        rows = {row['name']:row for row in result['manifest']['records']}
        _add(rows,result['payloads'],'task/packet.original.json','task_packet_original',
            encoded(packet),{'source':source,'task_binding':result['manifest']['task_binding'],
            'meaning':'Exact compact saved task; native originals authenticated separately.'})
        result['manifest']['records']=[rows[name] for name in sorted(rows)]
        return result
    states = disposition_context.validate_current_history(packet, source)
    prefixes = {identity: {'event_count': len(reviewed_history.index(state)),
                          'head_sha256': state['head_sha256'],
                          'index_sha256': reviewed_history.sha(reviewed_history.index(state))}
                for identity, state in states.items()}
    result = capture_changes(store, sorted(states), source=source,
                             task_binding=sha(encoded(packet)), expected_prefixes=prefixes, owner=owner)
    rows = {row['name']: row for row in result['manifest']['records']}
    _add(rows, result['payloads'], 'task/packet.original.json', 'task_packet_original',
         encoded(packet), {'source': source, 'task_binding': result['manifest']['task_binding'],
         'meaning': 'Exact saved task evidence; not acceptance, current authority or a new retrieval.'})
    result['manifest']['records'] = [rows[name] for name in sorted(rows)]
    return result


def capture_formal_changes(store, packet, *, source, owner=None):
    """Exact saved formal request and native prefix, not an authority decision.

    Evidence strings are originals of this request, not a claim that every
    underlying scientific artifact has been independently validated. Existing
    acceptance/adoption constructors and protected admission retain that duty.
    """
    from orchestrator import formal_decisions, reviewed_history
    from orchestrator.handover_coordinator import digest
    pin(source, 40)
    from orchestrator import current_scientific_input as current
    base={'version','trigger','scientific_decision_artifacts','formal_request','recorded_changes'}
    if (not isinstance(packet,dict) or set(packet) not in (base,base|{'scientific_change_history'})
            or type(packet['version']) is not int or packet['version'] != 1
            or packet['trigger'] != 'registered-formal-scientific-decision'
            or ('scientific_change_history' in packet and not current.is_current(packet))):
        raise ValueError('SCIENTIFIC_EVIDENCE_EXACT_FORMAL_PACKET_REQUIRED')
    request = formal_decisions.checked_request(packet['formal_request'])
    contract = formal_decisions.contract(packet['scientific_decision_artifacts'])
    if request['source'] != source or contract != {
            'version': 3, 'action': request['action'], 'subject': request['subject'],
            'bindings_sha256': digest(request['bindings'])}:
        raise ValueError('SCIENTIFIC_EVIDENCE_FORMAL_SOURCE_OR_CONTRACT_CHANGED')
    if current.is_current(packet):
        result=current.authenticate_capture(store,packet,source,owner=owner)
    else:
        state = packet['recorded_changes']
        boundary = reviewed_history.boundary(state)
        change = request['change_request']
        if boundary['request_id'] != change['request_id'] or not any(
                row['event'] == 'APPLIED' and row['identity'] == change['applied_event']
                for row in state['events']):
            raise ValueError('SCIENTIFIC_EVIDENCE_FORMAL_APPLICATION_CHANGED')
        # Pure chain validation above plus capture_changes' native request, event,
        # artifact and exact-prefix verification. No packet-only hash can pass.
        result = capture_changes(store, [boundary['request_id']], source=source,
            task_binding=sha(encoded(packet)), expected_prefixes={boundary['request_id']: {
                name: boundary[name] for name in ('event_count', 'head_sha256', 'index_sha256')}}, owner=owner)
        native_request = next(row for row in result['manifest']['records']
                              if row['kind'] == 'change_request')
        if json.loads(result['payloads'][native_request['sha256']]) != state['request']:
            raise ValueError('SCIENTIFIC_EVIDENCE_FORMAL_NATIVE_REQUEST_CHANGED')
    rows = {row['name']: row for row in result['manifest']['records']}
    _add(rows, result['payloads'], 'task/packet.original.json', 'task_packet_original',
        encoded(packet), {'source': source, 'task_binding': result['manifest']['task_binding'],
        'meaning': 'Exact saved formal request; no acceptance or adoption inferred.'})
    for name, body in sorted(request['evidence'].items()):
        _add(rows, result['payloads'], 'formal/evidence/'+name, 'formal_request_evidence',
            body.encode('utf-8'), {'source': source, 'path_in_task_packet': ['formal_request','evidence',name],
            'task_binding': result['manifest']['task_binding'],
            'meaning': 'Original evidence string in bound request, not independent validation of its claims.'})
    result['manifest']['records'] = [rows[name] for name in sorted(rows)]
    return result


def task_disposition_references(packet, *, source):
    """Only native-validated fixed wake slots, never recursive model-selected paths."""
    from orchestrator import disposition_context
    from orchestrator.disposition_successors import result_reference
    selected = disposition_context._selected_evidence(packet, source)
    if selected is None:
        return []
    from orchestrator import current_scientific_input
    if current_scientific_input.is_current(packet):
        return [deepcopy(ref) for _,ref in current_scientific_input.references(packet,source)[1]]
    disposition_context.validate_current_history(packet, source)
    references = []
    for index, proof in disposition_context._dispositions(selected, source):
        linked = selected['verified_events'][index]['linked_disposition']
        marker = linked.get('input_presentation')
        if marker is None:
            reference = result_reference(linked)
        else:
            # validate_current_history checked the exact source/application plan.
            # The following native reader will check this complete reference
            # against the original result/proof/repair chain again.
            reference = marker['original_reference']
        references.append(deepcopy(reference))
    return references


def capture_dispositions(capture, config, references, *, original_client):
    """Add full native originals and navigable exact outputs, never summaries.

    The authorized task-scope caller, still separately reviewed, supplies up to
    four immutable dependencies. The model cannot choose configuration or paths.
    Native read_result_reference checks the saved proof and all protected stage
    replies before any record is exported. Same captured originals feed all roles.
    """
    from orchestrator.disposition_successors import read_result_reference
    if (not isinstance(references,list) or not 1 <= len(references) <= 4
            or capture['manifest']['source'] != config['source']):
        raise ValueError('SCIENTIFIC_EVIDENCE_RESULT_SCOPE_REQUIRED')
    result = deepcopy(capture)
    records = {row['name']:row for row in result['manifest']['records']}
    payloads = result['payloads']; seen = set()
    for reference in references:
        value = read_result_reference(config,reference,original_client)
        identity = reference['origin_task']
        if identity in seen:
            raise ValueError('SCIENTIFIC_EVIDENCE_DUPLICATE_RESULT')
        seen.add(identity)
        raw = encoded(value)
        if sha(raw) != reference['original_value_sha256']:
            raise ValueError('SCIENTIFIC_EVIDENCE_NATIVE_RESULT_CHANGED')
        prefix = 'result/'+identity+'/'
        _add(records,payloads,prefix+'linked-disposition.original.json',
             'linked_disposition_original',raw,{'native_reference':deepcopy(reference)})
        from orchestrator.disposition_context import charter_path, _at
        from orchestrator.linked_disposition_input import context_document_originals
        try:
            science_path = charter_path(value['originals'])
            science = _at(value['originals'], science_path)
        except (KeyError, TypeError, ValueError):
            science = None  # Legacy/unknown layout stays full original, never a reference.
        for document in context_document_originals(science, identity):
            _add(records, payloads, document['name'], 'continuing_context_original',
                 document['text'].encode('utf-8'), {
                     'native_reference': deepcopy(reference),
                     'path_in_native_original': ['originals', *science_path, *document['path']],
                     'meaning': 'Exact native predecessor document from the same original capture; '
                                'no new retrieval, inspection, acceptance or authority.'})
        original = value['originals']['protected_original']['stages']
        fields = [
            ('author', ('originals','protected_original','stages','continuation','answer'),
             original['continuation']['answer']),
            ('reviewer', ('originals','protected_original','stages','review','answer'),
             original['review']['answer']),
            ('disposition', ('result','answer'),value['result']['answer'])]
        for role,path,body in fields:
            if not isinstance(body,str):
                raise ValueError('SCIENTIFIC_EVIDENCE_ORIGINAL_STAGE_TEXT_REQUIRED')
            _add(records,payloads,prefix+role+'.original.txt','scientific_stage_output',
                 body.encode('utf-8'),{'native_reference':deepcopy(reference),
                    'path_in_native_original':list(path),'role':role,
                    'meaning':'Exact original string, not summary, new retrieval or acceptance.'})
    result['manifest']['records'] = [records[name] for name in sorted(records)]
    return result



def capture_tasks(capture, config, packet, *, original_client):
    """Authenticate fixed TASK wake slots through the existing native reader.

    No model-selected path or task ID is accepted. Every exported proposal,
    review and disposition is an exact protected original from that same read;
    the bound starting evidence must equal the native wake projection.
    """
    from orchestrator import disposition_context, investigator_wakes
    if (capture['manifest']['source']!=config['source']
            or capture['manifest']['task_binding']!=sha(encoded(packet))):
        raise ValueError('SCIENTIFIC_EVIDENCE_EXACT_TASK_CAPTURE_REQUIRED')
    selected=disposition_context._selected_evidence(packet,config['source'])
    if selected is None:
        return capture
    candidates=[row for row in selected.get('verified_events',[])
                if row.get('event',{}).get('kind')=='TASK']
    expected=[event for event in selected['investigator_wake']['events'] if event['kind']=='TASK']
    if [row['event'] for row in candidates]!=expected:
        raise ValueError('SCIENTIFIC_EVIDENCE_TASK_WAKE_CHANGED')
    if not candidates:
        return capture
    if len(candidates)>investigator_wakes.MAX_EVENTS or not callable(original_client):
        raise ValueError('SCIENTIFIC_EVIDENCE_TASK_SCOPE_REQUIRED')
    result=deepcopy(capture)
    records={row['name']:row for row in result['manifest']['records']}
    payloads=result['payloads'];seen=set()
    for proposed in candidates:
        identity=pin(proposed['event']['identity'])
        if identity in seen:
            raise ValueError('SCIENTIFIC_EVIDENCE_DUPLICATE_TASK')
        seen.add(identity)
        native=investigator_wakes._task(config,identity,original_client,include_originals=True)
        projected={key:value for key,value in native.items()
                   if key not in ('packet','original_answers','original_receipts')}
        projected.update(original_task=native['packet']['campaign_task'],
                         original_packet_sha256=sha(encoded(native['packet'])))
        if projected!=proposed:
            raise ValueError('SCIENTIFIC_EVIDENCE_NATIVE_TASK_CHANGED')
        prefix='result/'+identity+'/'
        provenance={'native_task_event':deepcopy(native['event']),
            'original_packet_sha256':projected['original_packet_sha256'],
            'origin_source':native['predecessor']['source'],
            'meaning':'Native original read, not a new task, scientific acceptance or model inspection.'}
        _add(records,payloads,prefix+'task.original.json','scientific_task_original',
             encoded(native),provenance)
        _add(records,payloads,prefix+'packet.original.json','task_packet_original',
             encoded(native['packet']),provenance)
        for stage,role in [('continuation','author'),('review','reviewer'),('disposition','disposition')]:
            body=native['original_answers'][stage]
            if not isinstance(body,str):
                raise ValueError('SCIENTIFIC_EVIDENCE_ORIGINAL_STAGE_TEXT_REQUIRED')
            _add(records,payloads,prefix+role+'.original.txt','scientific_stage_output',
                 body.encode('utf-8'),{**provenance,'role':role,
                     'original_receipt':deepcopy(native['original_receipts'][stage])})
    result['manifest']['records']=[records[name] for name in sorted(records)]
    return result


def _capture_layout(capture):
    """One deterministic encoder shared by controller expectation and cache write."""
    manifest = capture['manifest']
    expected = {row['sha256'] for row in manifest['records']}
    if set(capture['payloads']) != expected:
        raise ValueError('SCIENTIFIC_EVIDENCE_COMPLETE_PAYLOAD_SET_REQUIRED')
    for identity, body in capture['payloads'].items():
        if sha(body) != identity:
            raise ValueError('SCIENTIFIC_EVIDENCE_PAYLOAD_CHANGED')
    for row in manifest['records']:
        body = capture['payloads'][row['sha256']]
        if (row['kind'] not in RECORD_KINDS or len(body) > _maximum(row['kind'])
                or len(body) != row['utf8_bytes']
                or len(body.decode('utf-8')) != row['characters']):
            raise ValueError('SCIENTIFIC_EVIDENCE_NATIVE_RECORD_BOUND')
    rows = manifest['records']; pages = []
    for offset in range(0, len(rows), 100):
        page = rows[offset:offset+100]; raw = encoded(page)
        pages.append(({'sha256': sha(raw), 'records': len(page)}, raw))
    header = {k: v for k, v in manifest.items() if k != 'records'}
    header.update(pages=[row for row, raw in pages], record_count=len(rows))
    raw = encoded(header)
    descriptor = {'schema': SCHEMA, 'source': manifest['source'],
        'task_binding': manifest['task_binding'], 'manifest_sha256': sha(raw),
        'record_count': len(rows)}
    return descriptor, raw, pages


def describe_capture(capture):
    """Same immutable capture identity, without claiming a model read or writing files."""
    return _capture_layout(capture)[0]


def write_capture(destination, capture):
    """Cache original bytes once; page the index independently of task input."""
    from orchestrator.operations_report import private_root
    descriptor, raw, pages = _capture_layout(capture)
    # Recheck the actual bytes at the persistence boundary as well as at _add
    # and read. A constructed capture cannot bypass the original-data scanner.
    # Check all payloads before creating any cache objects.
    from orchestrator.public_export import text
    for identity, body in sorted(capture['payloads'].items()):
        scan('scientific-evidence/'+identity+'.txt', body)
        # CRLF belongs to original evidence, not a generated public summary.
        # Validate all other controls without rewriting the original bytes.
        # _capture_layout checked the full byte count before this text check.
        text(body.decode('utf-8').replace(chr(13), ''), limit=NATIVE_RESULT_BYTES)
    path = private_root(destination)
    for identity, body in sorted(capture['payloads'].items()):
        _write_original(path/'objects'/(identity+'.txt'), body)
    for page, body in pages:
        immutable(path/'indexes'/(page['sha256']+'.json'), body)
    immutable(path/'manifests'/(descriptor['manifest_sha256']+'.json'), raw)
    return descriptor


def _write_original(path, body):
    """Preserve exact validated evidence bytes using the existing raw writer."""
    from orchestrator.inspection_source import write_once
    from orchestrator.hosted_cycle import sync_dir
    from orchestrator.operations_report import private_root
    path = Path(path)
    private_root(path.parent)
    try:
        write_once(path, body)
    except FileExistsError:
        if _regular(path, os.getuid(), NATIVE_RESULT_BYTES) != body:
            raise ValueError('SCIENTIFIC_EVIDENCE_IMMUTABLE_CONFLICT')
    sync_dir(path.parent)


def _regular(path, owner, maximum):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('SCIENTIFIC_EVIDENCE_SYMLINK_REFUSED')
    with os.fdopen(os.open(path, os.O_RDONLY|os.O_NOFOLLOW), 'rb') as stream:
        before = os.fstat(stream.fileno())
        if (not stat.S_ISREG(before.st_mode) or before.st_uid != owner
                or before.st_mode & 0o022 or before.st_size > maximum):
            raise ValueError('SCIENTIFIC_EVIDENCE_PROTECTED_ORIGINAL_REQUIRED')
        raw = stream.read(maximum+1); after = os.fstat(stream.fileno())
    if (len(raw) > maximum or (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
            != (after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)):
        raise ValueError('SCIENTIFIC_EVIDENCE_ORIGINAL_MOVED')
    return raw


class Reader:
    """Pure bounded operations; runtime wrapper must journal before delivery."""
    def __init__(self, directory, manifest_sha256, *, source, task_binding, owner):
        self.directory = Path(directory).absolute()
        pin(manifest_sha256); pin(source,40); pin(task_binding)
        if type(owner) is not int or owner < 0:
            raise ValueError('SCIENTIFIC_EVIDENCE_OWNER_REQUIRED')
        self.owner = owner; self.identity = manifest_sha256
        raw = _regular(self.directory/'manifests'/(manifest_sha256+'.json'), owner, 1500000)
        if sha(raw) != manifest_sha256:
            raise ValueError('SCIENTIFIC_EVIDENCE_MANIFEST_CHANGED')
        manifest = json.loads(raw)
        if (set(manifest) != {'schema','source','task_binding','request_heads','pages','record_count','semantics'}
                or manifest['schema'] != SCHEMA or manifest['source'] != source
                or manifest['task_binding'] != task_binding
                or type(manifest['record_count']) is not int or not 1 <= manifest['record_count'] <= MAX_RECORDS
                or not isinstance(manifest['pages'],list)
                or not 1 <= len(manifest['pages']) <= (MAX_RECORDS+99)//100):
            raise ValueError('SCIENTIFIC_EVIDENCE_BOUND_CAPTURE_REQUIRED')
        records = []
        for page in manifest['pages']:
            if (not isinstance(page,dict) or set(page) != {'sha256','records'}
                    or type(page['records']) is not int or not 1 <= page['records'] <= 100):
                raise ValueError('SCIENTIFIC_EVIDENCE_INDEX_PAGE_REQUIRED')
            pin(page['sha256'])
            raw = _regular(self.directory/'indexes'/(page['sha256']+'.json'),owner,1500000)
            if sha(raw) != page['sha256']:
                raise ValueError('SCIENTIFIC_EVIDENCE_INDEX_PAGE_CHANGED')
            rows = json.loads(raw)
            if not isinstance(rows,list) or len(rows) != page['records']:
                raise ValueError('SCIENTIFIC_EVIDENCE_INDEX_PAGE_CHANGED')
            records.extend(rows)
        if len(records) != manifest['record_count']:
            raise ValueError('SCIENTIFIC_EVIDENCE_INDEX_INCOMPLETE')
        names = []
        for row in records:
            if (set(row) != {'name','kind','sha256','utf8_bytes','characters','provenance'}
                    or not isinstance(row['name'],str) or row['kind'] not in RECORD_KINDS
                    or type(row['utf8_bytes']) is not int or not 0 <= row['utf8_bytes'] <= _maximum(row['kind'])
                    or type(row['characters']) is not int or not 0 <= row['characters'] <= row['utf8_bytes']):
                raise ValueError('SCIENTIFIC_EVIDENCE_RECORD_CONTRACT')
            pin(row['sha256']); names.append(row['name'])
        if names != sorted(set(names)):
            raise ValueError('SCIENTIFIC_EVIDENCE_UNIQUE_RECORDS_REQUIRED')
        self.manifest = manifest; self.records = records; self.rows = {row['name']: row for row in records}

    def _body(self, row):
        raw = _regular(self.directory/'objects'/(row['sha256']+'.txt'), self.owner, _maximum(row['kind']))
        if len(raw) != row['utf8_bytes'] or sha(raw) != row['sha256']:
            raise ValueError('SCIENTIFIC_EVIDENCE_ORIGINAL_CHANGED')
        body = raw.decode('utf-8')
        if len(body) != row['characters']:
            raise ValueError('SCIENTIFIC_EVIDENCE_CHARACTER_BINDING_CHANGED')
        scan('scientific-evidence/'+row['sha256']+'.txt', raw)
        return body

    def call(self, operation, arguments):
        if not isinstance(arguments,dict) or arguments.get('capture') != self.identity:
            raise ValueError('SCIENTIFIC_EVIDENCE_CAPTURE_REQUIRED')
        if operation == 'list':
            if set(arguments) != {'capture','cursor','kind'}:
                raise ValueError('SCIENTIFIC_EVIDENCE_LIST_FIELDS')
            kind = arguments['kind']
            if kind not in RECORD_KINDS | {'all'}:
                raise ValueError('SCIENTIFIC_EVIDENCE_KIND')
            rows = [r for r in self.rows.values() if kind == 'all' or r['kind'] == kind]
            cursor = self._cursor(arguments['cursor'],len(rows))
            end = min(cursor+PAGE_RECORDS,len(rows))
            result = {'records':deepcopy(rows[cursor:end]),'next_cursor':end if end<len(rows) else None}
        elif operation == 'read':
            if set(arguments) != {'capture','name','sha256','offset','characters'}:
                raise ValueError('SCIENTIFIC_EVIDENCE_READ_FIELDS')
            row = self.rows.get(arguments['name'])
            if row is None or row['sha256'] != arguments['sha256']:
                raise ValueError('SCIENTIFIC_EVIDENCE_BOUND_RECORD_REQUIRED')
            body = self._body(row)
            offset = self._cursor(arguments['offset'],len(body)); count = arguments['characters']
            if type(count) is not int or not 1 <= count <= READ_CHARACTERS:
                raise ValueError('SCIENTIFIC_EVIDENCE_READ_BOUND')
            end = min(offset+count,len(body)); part = body[offset:end]
            result = {'record':deepcopy(row), 'offset_characters':offset,'end_characters':end,
                'next_offset_characters':end if end<len(body) else None, 'content':part,
                'content_utf8_bytes':len(part.encode('utf-8')), 'content_sha256':sha(part.encode('utf-8'))}
        elif operation == 'search':
            if set(arguments) not in ({'capture','cursor','text'}, {'capture','cursor','text','name'}):
                raise ValueError('SCIENTIFIC_EVIDENCE_SEARCH_FIELDS')
            needle = arguments['text']
            if not isinstance(needle,str) or not 1 <= len(needle) <= 128:
                raise ValueError('SCIENTIFIC_EVIDENCE_LITERAL_QUERY_BOUND')
            # A name is only a selector in the already authenticated capture index.
            # It is never interpreted as a filesystem path or additional scope.
            if 'name' in arguments:
                name = arguments['name']
                if not isinstance(name, str) or name not in self.rows:
                    raise ValueError('SCIENTIFIC_EVIDENCE_BOUND_RECORD_REQUIRED')
                rows = [self.rows[name]]
            else:
                rows = list(self.rows.values())
            cursor = self._cursor(arguments['cursor'],len(rows))
            end = min(cursor+SEARCH_RECORDS,len(rows)); matches = []
            for row in rows[cursor:end]:
                body = self._body(row); offset = body.find(needle)
                if offset >= 0:
                    matches.append({'record':deepcopy(row),'offset_characters':offset})
                if len(matches) == PAGE_RECORDS:
                    end = cursor + rows[cursor:end].index(row) + 1
                    break
            result = {'matches':matches,'next_cursor':end if end<len(rows) else None,
                      'scanned_records':end-cursor, 'query':needle}
        else:
            raise ValueError('SCIENTIFIC_EVIDENCE_READ_ONLY_OPERATION')
        result = {'capture':self.identity, **result}
        if len(encoded(result)) > REPLY_BYTES:
            raise ValueError('SCIENTIFIC_EVIDENCE_REPLY_BOUND')
        return result

    @staticmethod
    def _cursor(value, maximum):
        if type(value) is not int or not 0 <= value <= maximum:
            raise ValueError('SCIENTIFIC_EVIDENCE_CURSOR_BOUND')
        return value


MAX_CALLS = 64
MAX_RETURN_BYTES = 262144


class Session:
    """Persistent per-role read budget and genuine tool-return originals.

    This is retrieval accounting only; it neither grants a model admission nor
    changes the existing usage ledger. The runner must bind this journal to the
    genuine CLI session and compare actual returned tool contents.
    """
    def __init__(self, reader, journal, *, role, task_binding):
        from orchestrator.operations_report import private_root
        if role not in ('author','reviewer','disposition'):
            raise ValueError('SCIENTIFIC_EVIDENCE_ROLE_REQUIRED')
        pin(task_binding)
        if reader.manifest['task_binding'] != task_binding:
            raise ValueError('SCIENTIFIC_EVIDENCE_SESSION_TASK_CHANGED')
        self.reader = reader; self.root = private_root(journal)
        self.binding = {'schema':'scientific-evidence-session/v1','role':role,
            'capture':reader.identity,'task_binding':task_binding,
            'max_calls':MAX_CALLS,'max_return_utf8_bytes':MAX_RETURN_BYTES}
        immutable(self.root/'binding.json', encoded(self.binding))

    def _history(self):
        files = sorted(self.root.glob('call-*.json'))
        previous = sha(encoded(self.binding)); used = 0
        for number, path in enumerate(files,1):
            if path.name != f'call-{number:04d}.json':
                raise ValueError('SCIENTIFIC_EVIDENCE_JOURNAL_SEQUENCE_CHANGED')
            raw = _regular(path,os.getuid(),200000); value = json.loads(raw)
            if (set(value) != {'number','previous_sha256','request','response','returned_utf8_bytes'}
                    or value['number'] != number or value['previous_sha256'] != previous
                    or value['returned_utf8_bytes'] != len(tool_text(value['response']).encode('utf-8'))):
                raise ValueError('SCIENTIFIC_EVIDENCE_JOURNAL_CHANGED')
            used += value['returned_utf8_bytes']; previous = sha(raw)
        return len(files),used,previous

    def call(self, operation, arguments):
        from orchestrator.remote_supervisor import lock
        with lock(self.root/'.retrieval.lock'):
            count,used,previous = self._history()
            if count >= MAX_CALLS or used >= MAX_RETURN_BYTES:
                raise ValueError('SCIENTIFIC_EVIDENCE_SESSION_BUDGET_EXHAUSTED')
            request = {'operation':operation,'arguments':arguments}
            # Preserve the attempted request before reading. An interrupted
            # delivery cannot be mistaken for a fresh uncounted tool operation.
            pending = self.root/'pending.json'
            if pending.exists():
                raise ValueError('SCIENTIFIC_EVIDENCE_INTERRUPTED_READ_RECONCILE')
            immutable(pending,encoded({'number':count+1,'request':request,'previous_sha256':previous}))
            try:
                result = self.reader.call(operation,arguments)
                response = {'ok':True,'result':result}
            except (ValueError,OSError,KeyError,TypeError,UnicodeError):
                # Original request and refusal survive, without leaking a
                # filesystem path or unrelated exception contents to the model.
                response = {'ok':False,'error':'SCIENTIFIC_EVIDENCE_READ_REFUSED','capture':self.reader.identity}
            if used + len(tool_text(response).encode('utf-8')) > MAX_RETURN_BYTES:
                response = {'ok':False,'error':'SCIENTIFIC_EVIDENCE_RETURN_BUDGET_EXHAUSTED',
                            'capture':self.reader.identity}
            size = len(tool_text(response).encode('utf-8'))
            if used + size > MAX_RETURN_BYTES:
                raise ValueError('SCIENTIFIC_EVIDENCE_SESSION_BUDGET_EXHAUSTED')
            record = {'number':count+1,'previous_sha256':previous,'request':request,
                'response':response,'returned_utf8_bytes':size}
            immutable(self.root/f'call-{count+1:04d}.json',encoded(record))
            # This is our own consumed transient marker; all original request
            # and response bytes remain in the immutable numbered record.
            pending.unlink()
            return response


def tool_text(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)


def definitions():
    shared = {'capture':{'type':'string','pattern':'^[0-9a-f]{64}$'}}
    properties = {
        'list': {**shared,'cursor':{'type':'integer','minimum':0},
                 'kind':{'type':'string','enum':['all',*sorted(RECORD_KINDS)]}},
        'search': {**shared,'cursor':{'type':'integer','minimum':0},
                   'text':{'type':'string','minLength':1,'maxLength':128},
                   'name':{'type':'string','description':'Optional exact record name returned by list; restrict search to that authenticated original.'}},
        'read': {**shared,'name':{'type':'string'},'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},
                 'offset':{'type':'integer','minimum':0},
                 'characters':{'type':'integer','minimum':1,'maximum':READ_CHARACTERS}}}
    descriptions = {
        'list':'Discover original evidence in a pinned capture. Start cursor0, follow next_cursor. No content inspection is implied.',
        'search':'Literal search over authenticated originals. After list, supply the exact record name to search that original without paging unrelated history. Without name, follow next_cursor. No regex or filesystem paths.',
        'read':'Read a character range from one discovered original with its exact SHA256. Follow next_offset_characters to read more.'}
    return [{'name':'scientific_evidence_'+name,'description':descriptions[name],
        'inputSchema':{'type':'object','properties':fields,'required':[k for k in fields if not (name == 'search' and k == 'name')],'additionalProperties':False},
        'annotations':{'readOnlyHint':True,'destructiveHint':False,'openWorldHint':False}}
        for name,fields in properties.items()]


def rpc(session, message):
    if not isinstance(message,dict) or message.get('jsonrpc') != '2.0':
        raise ValueError('SCIENTIFIC_EVIDENCE_JSONRPC_REQUIRED')
    if 'id' not in message:
        if message.get('method') == 'notifications/initialized':
            return None
        raise ValueError('SCIENTIFIC_EVIDENCE_NOTIFICATION_REFUSED')
    identity = message['id']; method = message.get('method')
    if method == 'initialize':
        result = {'protocolVersion':'2024-11-05','capabilities':{'tools':{}},
                  'serverInfo':{'name':'scientific-evidence','version':'1'}}
    elif method == 'tools/list':
        result = {'tools':definitions()}
    elif method == 'tools/call':
        params = message.get('params',{})
        # MCP clients attach transport metadata (for example progressToken and
        # claudecode/toolUseId). It is not evidence input or authority. Keep the
        # actual operation/arguments strict and journal their original response.
        if (not isinstance(params,dict) or
                not {'name','arguments'} <= set(params) <= {'name','arguments','_meta'} or
                ('_meta' in params and not isinstance(params['_meta'],dict)) or
                params['name'] not in {item['name'] for item in definitions()}):
            raise ValueError('SCIENTIFIC_EVIDENCE_TOOL_REFUSED')
        response = session.call(params['name'].removeprefix('scientific_evidence_'),params['arguments'])
        result = {'content':[{'type':'text','text':tool_text(response)}],
                  'isError':not response['ok']}
    elif method == 'ping':
        result = {}
    else:
        raise ValueError('SCIENTIFIC_EVIDENCE_METHOD_REFUSED')
    return {'jsonrpc':'2.0','id':identity,'result':result}


def main():
    import argparse
    import sys
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('directory','manifest','source','task-binding','journal','role'):
        parser.add_argument('--'+name,required=True)
    parser.add_argument('--owner',type=int,required=True)
    parser.add_argument('--reader-uid',type=int,required=True)
    args=parser.parse_args()
    if args.reader_uid <= 0 or os.getuid() != args.reader_uid:
        raise ValueError('SCIENTIFIC_EVIDENCE_READER_IDENTITY_REQUIRED')
    reader=Reader(args.directory,args.manifest,source=args.source,task_binding=args.task_binding,owner=args.owner)
    session=Session(reader,args.journal,role=args.role,task_binding=args.task_binding)
    while True:
        line=sys.stdin.buffer.readline(16385)
        if not line:
            break
        if len(line)>16384 or not line.endswith(b'\n'):
            raise ValueError('SCIENTIFIC_EVIDENCE_RPC_INPUT_BOUND')
        message=None
        try:
            message=json.loads(line)
            reply=rpc(session,message)
        except (ValueError,KeyError,TypeError):
            reply={'jsonrpc':'2.0','id':message.get('id') if isinstance(message,dict) else None,
                   'error':{'code':-32602,'message':'SCIENTIFIC_EVIDENCE_REQUEST_REFUSED'}}
        if reply is not None:
            sys.stdout.write(tool_text(reply)+'\n');sys.stdout.flush()


if __name__=='__main__':
    main()
