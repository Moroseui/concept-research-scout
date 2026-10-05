"""Attempt-owned, read-only host access for the trusted implementation reviewer.

The root runner owns Broker; an unprivileged fixed stdio adapter talks over its
private Unix socket. No subprocess, credentials use, writes to requested paths,
or general RPC dispatch. Originals are kept by the existing attempt lifecycle.
This module deliberately does not apply a secret filter or a selected-path list.
"""
from contextlib import AbstractContextManager
from datetime import datetime, timezone
import base64
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import struct
import sys
import threading

PROFILE = 'implementation-review-host-read/v1'
AUTH_REQUEST = '31a5c5598e94320d796ccea27e3990d8aca50dc9e12d0c5ad039d717325231f6'
AUTH_EVENT = '6d496a1c89207ae6cac6ff0bad8c3b4240b46c39d6c8cb47f339b422f172b2e5'
OPERATOR_SHA = '1d0ed0b72fa05e08846b099964e86dfe693f9d13cca99e1e10e216a79bc7057a'
SOCKET = '/runtime/host-read.sock'
MAX_REQUEST = 8192
MAX_RESPONSE = 100000
MAX_TOTAL = 2000000
MAX_CALLS = 128
NAMES = ('read', 'list', 'search')
TOOL_PREFIX = 'mcp__hostfs__'


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                       allow_nan=False)+'\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def profile(value):
    require(isinstance(value, dict) and value == {
        'schema': PROFILE, 'operator_original_sha256': OPERATOR_SHA,
        'authority_request': AUTH_REQUEST, 'authorized_event': AUTH_EVENT},
        'HOST_READ_EXACT_AUTHORITY_REQUIRED')
    return value



def authority(raw):
    """Authenticate the fixed operator grant, not a self-declared profile.

    The existing protected review inventory supplies exact preserved originals.
    This validates record integrity and pins the actual operator decision; it
    does not turn a source review into installation or scientific authority.
    """
    from orchestrator import change_requests as changes
    prefix = 'host-read-authority/'
    state = changes.validate_originals(raw[prefix+'request.json'],
        {name[len(prefix+'events/'):]: value for name, value in raw.items()
         if name.startswith(prefix+'events/')}, lambda name: raw[prefix+name])
    require(state['request']['identity'] == AUTH_REQUEST,
            'HOST_READ_AUTHORITY_REQUEST_CHANGED')
    event = next((item for item in state['events'] if item['identity'] == AUTH_EVENT), None)
    require(event is not None and event['event'] == 'AUTHORIZED'
            and event['actor'] == {'kind': 'human', 'identity': 'project-operator'},
            'HOST_READ_ACTUAL_OPERATOR_AUTHORIZATION_REQUIRED')
    payload = event['payload']
    require(sha(raw[prefix+payload['authority_reference']['artifact']]) ==
            payload['operator_original_sha256'] == OPERATOR_SHA
            and payload['authority_scope'] == 'implementation-review root-equivalent read/discovery only'
            and all(payload[key] is False for key in ('source_approved', 'installation_approved',
                'scientific_activation_approved', 'implementation_driver_relocation_approved')),
            'HOST_READ_EXACT_OPERATOR_BOUNDARIES_REQUIRED')
    return event


def mcp_config():
    return {'mcpServers': {'hostfs': {'type': 'stdio', 'command': '/runtime/python',
        'args': ['-B', '/runtime/implementation_host_read.py', 'stdio']}}}


def metadata(st):
    return {k: getattr(st, 'st_'+k) for k in
            ('dev', 'ino', 'mode', 'uid', 'gid', 'size', 'mtime_ns', 'ctime_ns')}


def normalize(request):
    require(isinstance(request, dict) and set(request) == {'operation', 'arguments'}
            and request['operation'] in NAMES, 'HOST_READ_OPERATION_REFUSED')
    operation, args = request['operation'], request['arguments']
    keys = {'read': {'path', 'offset', 'length'},
            'list': {'path', 'offset', 'limit'},
            'search': {'path', 'text', 'offset', 'length'}}[operation]
    require(isinstance(args, dict) and set(args) <= keys and 'path' in args,
            'HOST_READ_ARGUMENTS')
    path = args['path']
    require(isinstance(path, str) and path.startswith('/') and len(path) <= 4096
            and '\x00' not in path, 'HOST_READ_ABSOLUTE_PATH_REQUIRED')
    args = dict(args)
    args.setdefault('offset', 0)
    require(type(args['offset']) is int and 0 <= args['offset'] <= 2**63-1,
            'HOST_READ_OFFSET')
    key, default, maximum = ('limit', 100, 200) if operation == 'list' else ('length', 16384, 32768)
    args.setdefault(key, default)
    require(type(args[key]) is int and 1 <= args[key] <= maximum, 'HOST_READ_RANGE')
    if operation == 'search':
        require(isinstance(args.get('text'), str) and 0 < len(args['text'].encode()) <= 1024,
                'HOST_READ_LITERAL_SEARCH_REQUIRED')
    return operation, args


def inspect(request):
    """One bounded observation, never a claim that a live tree is a snapshot.

    Byte ranges support arbitrary-size regular files. Binary ranges are base64.
    Search is literal within one requested range; list discovers directories.
    Special files are excluded to prevent device/socket/FIFO operations.
    """
    operation, args = normalize(request)
    requested = args['path']
    path = Path(requested).resolve(strict=True)
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
    if operation == 'list':
        flags |= os.O_DIRECTORY
    fd = os.open(path, flags)
    try:
        before = os.fstat(fd)
        result = {'requested_path': requested, 'resolved_path': str(path),
                  'observed_utc': datetime.now(timezone.utc).isoformat(),
                  'file_identity': metadata(before), 'operation': operation,
                  'offset': args['offset'], 'status': 'OBSERVED',
                  'scope': 'live host observation; not frozen-candidate coverage'}
        if operation == 'list':
            require(stat.S_ISDIR(before.st_mode), 'HOST_READ_DIRECTORY_REQUIRED')
            # Bound traversal before sorting; no recursive server crawl.
            with os.scandir(fd) as entries:
                names = []
                for entry in entries:
                    require(len(names) < 10000, 'HOST_READ_DIRECTORY_BOUND')
                    names.append(entry.name)
            names.sort()
            selected = names[args['offset']:args['offset']+args['limit']]
            result.update(entries=selected, total_entries=len(names),
                          next_offset=args['offset']+len(selected))
        else:
            require(stat.S_ISREG(before.st_mode), 'HOST_READ_REGULAR_FILE_REQUIRED')
            raw = os.pread(fd, args['length'], args['offset'])
            result.update(range_bytes=len(raw), range_sha256=sha(raw),
                          next_offset=args['offset']+len(raw),
                          whole_file_sha256=sha(raw) if args['offset'] == 0
                          and len(raw) == before.st_size else None)
            if operation == 'read':
                try:
                    result.update(encoding='utf-8', content=raw.decode('utf-8'))
                except UnicodeDecodeError:
                    result.update(encoding='base64', content=base64.b64encode(raw).decode())
            else:
                needle = args['text'].encode()
                matches, pos = [], 0
                while len(matches) < 100:
                    pos = raw.find(needle, pos)
                    if pos < 0:
                        break
                    matches.append(args['offset']+pos)
                    pos += max(1, len(needle))
                result.update(matches=matches, match_limit=100,
                              search_scope='literal byte-range only; page to inspect more')
        if operation != 'list':
            require(os.pread(fd, args['length'], args['offset']) == raw,
                    'HOST_READ_CHANGED_DURING_OBSERVATION')
        require(metadata(before) == metadata(os.fstat(fd)) == metadata(path.stat()),
                'HOST_READ_CHANGED_DURING_OBSERVATION')
        require(len(encoded(result)) <= MAX_RESPONSE, 'HOST_READ_RESPONSE_BOUND')
        return result
    finally:
        os.close(fd)


def _line(stream, maximum):
    raw = b''
    while not raw.endswith(b'\n'):
        part = stream.recv(min(65536, maximum+1-len(raw)))
        require(part, 'HOST_READ_INCOMPLETE_REQUEST')
        raw += part
        require(len(raw) <= maximum, 'HOST_READ_MESSAGE_BOUND')
    require(raw.count(b'\n') == 1, 'HOST_READ_SINGLE_MESSAGE_REQUIRED')
    return raw


class Broker(AbstractContextManager):
    """No standalone service: lifetime is exactly one admitted server attempt."""
    def __init__(self, socket_path, journal, *, uid, gid, session, attempt, cgroup):
        require(os.geteuid() == 0, 'HOST_READ_ROOT_RUNNER_REQUIRED')
        require(isinstance(cgroup, str) and cgroup.strip(), 'HOST_READ_CGROUP_REQUIRED')
        self.path, self.journal = Path(socket_path), Path(journal)
        self.uid, self.gid = uid, gid
        self.binding = {'schema': PROFILE, 'session_id': session, 'attempt': attempt,
                        'operator_original_sha256': OPERATOR_SHA, 'cgroup': cgroup}
        self.records, self.total = [], 0
        self.stop = threading.Event()

    def __enter__(self):
        require(not self.path.exists() and not self.journal.exists(),
                'HOST_READ_EXISTING_ATTEMPT_RECONCILE')
        self.journal.mkdir(mode=0o700)
        self.listener = socket.socket(socket.AF_UNIX)
        self.listener.bind(str(self.path))
        os.chown(self.path, 0, self.gid)
        os.chmod(self.path, 0o660)
        self.listener.listen(2)
        self.listener.settimeout(.2)
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()
        return self

    def _serve(self):
        while not self.stop.is_set() and len(self.records) < MAX_CALLS and self.total+MAX_RESPONSE <= MAX_TOTAL:
            try:
                connection, _ = self.listener.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            with connection:
                connection.settimeout(5)
                request = None
                try:
                    pid, uid, _ = struct.unpack('3i', connection.getsockopt(
                        socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
                    require(uid == self.uid and Path(f'/proc/{pid}/cgroup').read_text() ==
                            self.binding['cgroup'], 'HOST_READ_ATTEMPT_PEER_REQUIRED')
                    require(len(self.records) < MAX_CALLS and self.total+MAX_RESPONSE <= MAX_TOTAL,
                            'HOST_READ_ATTEMPT_BUDGET')
                    request = json.loads(_line(connection, MAX_REQUEST))
                    result = inspect(request)
                except (ValueError, OSError, KeyError, TypeError) as error:
                    reason = str(error) if isinstance(error, ValueError) else type(error).__name__
                    if not reason.startswith('HOST_READ_'):
                        reason = 'HOST_READ_REQUEST_REFUSED'
                    result = {'status': 'REFUSED', 'reason': reason}
                response = encoded(result)
                record = {**self.binding, 'sequence': len(self.records)+1,
                          'request': request, 'response': result}
                raw = encoded(record)
                target = self.journal/f'{record["sequence"]:04d}.json'
                # Persist the original response before it can reach the model.
                try:
                    with target.open('xb') as file:
                        os.chmod(target, 0o600)
                        file.write(raw); file.flush(); os.fsync(file.fileno())
                    self.records.append({'name': target.name, 'sha256': sha(raw), 'bytes': len(raw)})
                    self.total += len(response)
                    connection.sendall(response)
                except OSError:
                    self.stop.set()

    def __exit__(self, *_):
        self.stop.set()
        self.listener.close()
        self.thread.join(timeout=6)
        require(not self.thread.is_alive(), 'HOST_READ_BROKER_NOT_STOPPED')
        # Preserve socket and all originals. A subsequent attempt gets a new path.

    def originals(self):
        rows = []
        for item in self.records:
            raw = (self.journal/item['name']).read_bytes()
            require(sha(raw) == item['sha256'] and len(raw) == item['bytes'],
                    'HOST_READ_ORIGINAL_CHANGED')
            rows.append(json.loads(raw))
        return {**self.receipt(), 'originals': rows}

    def receipt(self):
        return {**self.binding, 'records': list(self.records),
                'response_utf8_bytes': self.total, 'calls': len(self.records),
                'automatic_retry': False}



def validate_originals(value, *, session, attempt):
    """Validate the preserved root observation set; no automatic Read credit."""
    require(isinstance(value, dict) and set(value) == {
        'schema', 'session_id', 'attempt', 'operator_original_sha256', 'cgroup',
        'records', 'response_utf8_bytes', 'calls', 'automatic_retry', 'originals'},
        'HOST_READ_ORIGINAL_SCHEMA')
    require(value['schema'] == PROFILE and value['session_id'] == session
            and type(value['attempt']) is int and value['attempt'] == attempt
            and value['operator_original_sha256'] == OPERATOR_SHA
            and value['automatic_retry'] is False and isinstance(value['cgroup'], str)
            and value['cgroup'].strip(), 'HOST_READ_ORIGINAL_BINDING')
    rows, originals = value['records'], value['originals']
    require(isinstance(rows, list) and isinstance(originals, list)
            and len(rows) == len(originals) == value['calls'] <= MAX_CALLS,
            'HOST_READ_ORIGINAL_COUNT')
    total = 0
    binding = {key: value[key] for key in
               ('schema', 'session_id', 'attempt', 'operator_original_sha256', 'cgroup')}
    for number, (row, original) in enumerate(zip(rows, originals), 1):
        raw = encoded(original)
        require(row == {'name': f'{number:04d}.json', 'sha256': sha(raw), 'bytes': len(raw)}
                and all(original.get(k) == v for k, v in binding.items())
                and original.get('sequence') == number, 'HOST_READ_ORIGINAL_CHANGED')
        response = encoded(original['response'])
        require(len(response) <= MAX_RESPONSE, 'HOST_READ_RESPONSE_BOUND')
        total += len(response)
    require(type(value['response_utf8_bytes']) is int and total == value['response_utf8_bytes']
            and total <= MAX_TOTAL, 'HOST_READ_ORIGINAL_TOTAL')
    return {'calls': len(rows), 'originals_sha256': sha(encoded(value)),
            'inspection_credit': 'No automatic coverage; distinguish actual model tool results from available root records.'}


def forward(request):
    with socket.socket(socket.AF_UNIX) as client:
        client.settimeout(10)
        client.connect(SOCKET)
        client.sendall(encoded(request))
        return json.loads(_line(client, MAX_RESPONSE))


def definitions():
    out = []
    for name in NAMES:
        properties = {'path': {'type': 'string', 'description': 'Absolute path on the remote host.'},
                      'offset': {'type': 'integer', 'minimum': 0}}
        required = ['path']
        if name == 'list':
            properties['limit'] = {'type': 'integer', 'minimum': 1, 'maximum': 200}
        else:
            properties['length'] = {'type': 'integer', 'minimum': 1, 'maximum': 32768}
        if name == 'search':
            properties['text'] = {'type': 'string'}; required.append('text')
        out.append({'name': name, 'description': {
            'read': 'Read a byte range with live file identity and range digest; no path allowlist. No commands.',
            'list': 'List a directory page for independent host discovery; no recursive crawl.',
            'search': 'Find literal text in one file byte range. No regex or command execution.'
            }[name], 'inputSchema': {'type': 'object', 'properties': properties,
              'required': required, 'additionalProperties': False},
            'annotations': {'readOnlyHint': True, 'destructiveHint': False}})
    return out


def rpc(message):
    require(isinstance(message, dict) and message.get('jsonrpc') == '2.0',
            'HOST_READ_RPC_SCHEMA')
    if 'id' not in message:
        require(message.get('method') == 'notifications/initialized',
                'HOST_READ_NOTIFICATION_REFUSED')
        return None
    method = message.get('method')
    if method == 'initialize':
        result = {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}},
                  'serverInfo': {'name': 'implementation-host-read', 'version': '1'}}
    elif method == 'tools/list':
        result = {'tools': definitions()}
    elif method == 'ping':
        result = {}
    elif method == 'tools/call':
        args = message.get('params', {})
        request = {'operation': args.get('name'), 'arguments': args.get('arguments', {})}
        normalize(request)
        value = forward(request)
        result = {'content': [{'type': 'text', 'text': encoded(value).decode()}],
                  'isError': value.get('status') != 'OBSERVED'}
    else:
        raise ValueError('HOST_READ_METHOD_REFUSED')
    return {'jsonrpc': '2.0', 'id': message['id'], 'result': result}


def stdio():
    while True:
        raw = sys.stdin.buffer.readline(MAX_REQUEST+1)
        if not raw:
            return
        message = None
        try:
            require(len(raw) <= MAX_REQUEST and raw.endswith(b'\n'), 'HOST_READ_MESSAGE_BOUND')
            message = json.loads(raw)
            response = rpc(message)
        except (ValueError, OSError, KeyError, TypeError):
            response = {'jsonrpc': '2.0', 'id': message.get('id') if isinstance(message, dict) else None,
                        'error': {'code': -32602, 'message': 'HOST_READ_REQUEST_REFUSED'}}
        if response is not None:
            sys.stdout.buffer.write(encoded(response)); sys.stdout.buffer.flush()


if __name__ == '__main__':
    require(sys.argv[1:] == ['stdio'], 'HOST_READ_FIXED_ADAPTER_ONLY')
    stdio()
