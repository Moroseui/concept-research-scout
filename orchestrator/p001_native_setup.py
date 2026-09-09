"""Fixed transparent P001 setup over native MCP, with private original JSON-RPC.

No model-generated commands, patient execution, reconnection or automatic retry.
The renderer supplies all code. Native protocol is never relabeled as model output.
Run only after the exact renderer/client source review; uncertain calls stay stopped.
"""
import argparse
import asyncio
import datetime
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[1]
CONFIG = Path('/home/partho/.local/share/isles-colab-mcp/claude-worker.json')
CONFIG_SHA256 = 'e236feebb9f1a23856a84fba252fc4eef6df445e516e5a06a36afc602fd87de4'
COMMAND = '/home/partho/.local/share/isles-colab-mcp/bin/colab-mcp'
MAX_FRAME = 2 * 1024 * 1024
MAX_PROTOCOL = 32 * 1024 * 1024
TOOL_NAMES = {'open_colab_browser_connection', 'get_cells', 'add_code_cell', 'run_code_cell'}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('NATIVE_DUPLICATE_JSON_KEY')
        value[key] = item
    return value


def read_json(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def private_file(path, maximum=MAX_PROTOCOL):
    path = Path(path).absolute()
    for parent in path.parents:
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise ValueError('NATIVE_PRIVATE_PATH_ANCESTOR')
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_mode & 0o077 or before.st_uid != os.getuid() or before.st_size > maximum:
        raise ValueError('NATIVE_PRIVATE_FILE_REQUIRED')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns):
            raise ValueError('NATIVE_PRIVATE_FILE_CHANGED')
        raw = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
        if len(raw) > maximum or (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError('NATIVE_PRIVATE_FILE_CHANGED')
    return raw


def write_new(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(encoded(value) + b'\n')
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(Path(path).parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def require_review(directory):
    directory = Path(directory)
    execution = read_json(private_file(directory / 'execution.json'))
    response_raw = private_file(directory / 'response.json')
    response = read_json(response_raw)
    review = response.get('structured_output', {})
    required = {'orchestrator/p001_native_setup.py', 'orchestrator/p001_transparent_setup.py',
                'orchestrator/p001_runtime_setup.py', 'orchestrator/p001_runtime_intake.py'}
    if (execution.get('returncode') != 0 or response.get('is_error') or response.get('subtype') != 'success'
            or review.get('verdict') != 'APPROVE' or review.get('reviewed_commit') != execution.get('reviewed_commit')
            or not review.get('scope', '').startswith('p001-transparent-setup-native-v1')
            or execution.get('requested_model') != 'claude-fable-5'
            or execution.get('assistant_message_models') != ['claude-fable-5']
            or digest(response_raw) != execution.get('response_sha256')
            or digest(private_file(directory / 'protocol.jsonl')) != execution.get('protocol_sha256')
            or not required <= set(execution.get('input_file_sha256', {}))):
        raise ValueError('NATIVE_EXACT_SOURCE_REVIEW_REQUIRED')
    for name, expected in execution['input_file_sha256'].items():
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or (ROOT / path).is_symlink():
            raise ValueError('NATIVE_REVIEW_INPUT_PATH')
        if digest((ROOT / path).read_bytes()) != expected:
            raise ValueError('NATIVE_REVIEW_INPUT_CHANGED')
    return {'reviewed_commit': execution['reviewed_commit'], 'execution_sha256': digest(private_file(directory / 'execution.json'))}


class Journal:
    def __init__(self, path):
        self.stream = Path(path).open('xb')
        os.chmod(path, 0o600)
        self.count = 0
        self.bytes = 0

    def record(self, direction, message):
        rpc = message.message.model_dump(mode='json', by_alias=True, exclude_none=True)
        if direction == 'received' and 'method' in rpc and 'id' in rpc and rpc['method'] != 'ping':
            raise ValueError('NATIVE_UNEXPECTED_SERVER_REQUEST')
        row = {'sequence': self.count, 'direction': direction,
               'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'rpc': rpc}
        raw = encoded(row) + b'\n'
        if len(raw) > MAX_FRAME or self.bytes + len(raw) > MAX_PROTOCOL or self.count >= 256:
            raise ValueError('NATIVE_PROTOCOL_BOUND')
        self.stream.write(raw)
        self.stream.flush()
        os.fsync(self.stream.fileno())  # Outbound original intent is durable before send.
        self.count += 1
        self.bytes += len(raw)

    def close(self):
        self.stream.close()


class RecordedSend:
    def __init__(self, stream, journal):
        self.stream, self.journal = stream, journal

    async def send(self, message):
        self.journal.record('sent', message)
        await self.stream.send(message)

    async def aclose(self):
        await self.stream.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()


class RecordedReceive:
    def __init__(self, stream, journal):
        self.stream, self.journal = stream, journal

    async def receive(self):
        message = await self.stream.receive()
        if isinstance(message, Exception):
            raise message
        self.journal.record('received', message)
        return message

    def __aiter__(self):
        return self

    async def __anext__(self):
        from anyio import EndOfStream
        try:
            return await self.receive()
        except EndOfStream:
            raise StopAsyncIteration from None

    async def aclose(self):
        await self.stream.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()


def decode_result(name, result):
    if not isinstance(result, dict) or result.get('isError'):
        raise ValueError('NATIVE_TOOL_ERROR')
    content = result.get('content', [])
    if not isinstance(content, list) or any(not isinstance(c, dict) or c.get('type') != 'text' or not isinstance(c.get('text'), str) for c in content):
        raise ValueError('NATIVE_TEXT_RESULT_REQUIRED')
    text = ''.join(c['text'] for c in content)
    if len(text.encode()) > MAX_FRAME:
        raise ValueError('NATIVE_RESULT_BOUND')
    parsed = read_json(text) if text else None
    structured = result.get('structuredContent')
    if structured is not None:
        if parsed is not None and parsed != structured and structured != {'result': parsed}:
            raise ValueError('NATIVE_RESULT_REPRESENTATIONS_DIFFER')
        value = structured
    else:
        value = {'result': parsed} if name == 'open_colab_browser_connection' and type(parsed) is bool else parsed
    if not isinstance(value, dict):
        raise ValueError('NATIVE_OBJECT_RESULT_REQUIRED')
    return value


def cells_result(value):
    cells = value.get('cells')
    if not isinstance(cells, list) or len(cells) > 64:
        raise ValueError('NATIVE_NOTEBOOK_CELL_BOUND')
    observed = {}
    for cell in cells:
        if not isinstance(cell, dict) or not isinstance(cell.get('id'), str) or cell['id'] in observed:
            raise ValueError('NATIVE_CELL_IDENTITY')
        source = cell.get('source')
        if not isinstance(source, list) or any(not isinstance(line, str) for line in source):
            raise ValueError('NATIVE_CELL_SOURCE_SCHEMA')
        if 'outputs' in cell:
            raise ValueError('NATIVE_EXISTING_OUTPUT_READ_REFUSED')
        observed[cell['id']] = ''.join(source)
    return observed


async def dispatch(packet, session, directory, spec):
    """One fixed attempt; no exception path resubmits a tool call."""
    cells = packet['cells']
    if len(cells) != 4 or any(not isinstance(cell, str) or len(cell.encode()) > 131072 for cell in cells):
        raise ValueError('NATIVE_FIXED_SETUP_PACKET_REQUIRED')
    ordinal = 0

    async def call(name, args):
        nonlocal ordinal
        if name not in TOOL_NAMES or ordinal >= 16:
            raise ValueError('NATIVE_UNEXPECTED_OPERATION')
        operation = ordinal
        ordinal += 1
        write_new(directory / (str(operation).zfill(2) + '.intent.json'),
                  {'tool': name, 'arguments': args, 'packet_sha256': digest(encoded(packet))})
        response = await session.call_tool(name, args, read_timeout_seconds=datetime.timedelta(seconds=900 if name == 'run_code_cell' else 90))
        value = response.model_dump(mode='json', by_alias=True, exclude_none=True)
        write_new(directory / (str(operation).zfill(2) + '.response.json'), value)
        return decode_result(name, value)

    opened = await call('open_colab_browser_connection', {})
    if opened != {'result': True}:
        raise ValueError('NATIVE_EXISTING_BROWSER_CONNECTION_REQUIRED')
    tools = await session.list_tools()
    if not TOOL_NAMES <= {tool.name for tool in tools.tools}:
        raise ValueError('NATIVE_CONNECTED_TOOL_SET_REQUIRED')
    initial = cells_result(await call('get_cells', {'includeOutputs': False}))
    if len(initial) > 60:
        raise ValueError('NATIVE_NOTEBOOK_CELL_BOUND')
    created = []
    for index, source in enumerate(cells):
        result = await call('add_code_cell', {'cellIndex': len(initial) + index, 'language': 'python', 'code': source})
        cell_id = result.get('newCellId')
        if not isinstance(cell_id, str) or not cell_id or cell_id in initial or cell_id in created:
            raise ValueError('NATIVE_NEW_CELL_IDENTITY_REQUIRED')
        created.append(cell_id)
    outcomes = []
    expected = {**initial, **dict(zip(created, cells))}
    for index, cell_id in enumerate(created):
        readback = cells_result(await call('get_cells', {'includeOutputs': False}))
        if readback != expected or list(readback) != list(expected):
            raise ValueError('NATIVE_CELL_READBACK_CHANGED')
        result = await call('run_code_cell', {'cellId': cell_id})
        outcomes.append(spec.validate_stage(packet, index, result))
    return outcomes


def verify_native(packet, raw, spec):
    """Verify actual JSON-RPC IDs, source readbacks and every ordered result."""
    if not raw or len(raw) > MAX_PROTOCOL:
        raise ValueError('NATIVE_PROTOCOL_BOUND')
    rows = [read_json(line) for line in raw.splitlines()]
    requests, responses, calls = {}, {}, []
    server_pings, ping_responses = set(), set()
    for index, row in enumerate(rows):
        if row.get('sequence') != index or row.get('direction') not in ('sent', 'received'):
            raise ValueError('NATIVE_PROTOCOL_SEQUENCE')
        rpc = row['rpc']
        if row['direction'] == 'received' and rpc.get('method') == 'ping' and 'id' in rpc:
            if rpc['id'] in server_pings or rpc.get('params', {}) != {}:
                raise ValueError('NATIVE_UNEXPECTED_SERVER_REQUEST')
            server_pings.add(rpc['id'])
        elif row['direction'] == 'sent' and 'id' in rpc and 'method' not in rpc:
            if rpc['id'] not in server_pings or rpc['id'] in ping_responses or rpc.get('result') != {}:
                raise ValueError('NATIVE_UNEXPECTED_CLIENT_RESPONSE')
            ping_responses.add(rpc['id'])
        elif row['direction'] == 'sent' and 'method' in rpc and 'id' in rpc:
            if rpc['id'] in requests:
                raise ValueError('NATIVE_DUPLICATE_REQUEST_ID')
            requests[rpc['id']] = rpc
            if rpc['method'] not in ('initialize', 'tools/list', 'tools/call'):
                raise ValueError('NATIVE_UNEXPECTED_METHOD')
            if rpc['method'] == 'tools/call':
                if set(rpc['params']) != {'name', 'arguments'}:
                    raise ValueError('NATIVE_TOOL_ARGUMENT_SCHEMA')
                calls.append((index, rpc))
        elif row['direction'] == 'received' and 'id' in rpc:
            if rpc['id'] not in requests or rpc['id'] in responses or 'error' in rpc or 'result' not in rpc:
                raise ValueError('NATIVE_RESPONSE_ID_OR_ERROR')
            responses[rpc['id']] = (index, rpc['result'])
    if server_pings != ping_responses or any(request_id not in responses for request_id in requests):
        raise ValueError('NATIVE_UNCERTAIN_REQUEST_RECONCILE')
    expected_names = ['open_colab_browser_connection', 'get_cells'] + ['add_code_cell'] * 4 + ['get_cells', 'run_code_cell'] * 4
    if [rpc['params']['name'] for _, rpc in calls] != expected_names:
        raise ValueError('NATIVE_FIXED_SEQUENCE_REQUIRED')
    initial, expected, created, outcomes = None, None, [], []
    for position, (sent_index, rpc) in enumerate(calls):
        response_index, raw_result = responses[rpc['id']]
        if response_index <= sent_index or (position + 1 < len(calls) and response_index >= calls[position + 1][0]):
            raise ValueError('NATIVE_SERIAL_RESPONSE_ORDER')
        name, args = rpc['params']['name'], rpc['params']['arguments']
        result = decode_result(name, raw_result)
        if name == 'open_colab_browser_connection':
            if args != {} or result != {'result': True}:
                raise ValueError('NATIVE_EXISTING_BROWSER_CONNECTION_REQUIRED')
        elif name == 'get_cells':
            if args != {'includeOutputs': False}:
                raise ValueError('NATIVE_SOURCE_ONLY_READ_REQUIRED')
            observed = cells_result(result)
            if initial is None:
                initial = observed
            elif observed != expected or list(observed) != list(expected):
                raise ValueError('NATIVE_CELL_READBACK_CHANGED')
        elif name == 'add_code_cell':
            index = len(created)
            if args != {'cellIndex': len(initial) + index, 'language': 'python', 'code': packet['cells'][index]}:
                raise ValueError('NATIVE_EXACT_SOURCE_REQUIRED')
            cell_id = result.get('newCellId')
            if not isinstance(cell_id, str) or not cell_id or cell_id in initial or cell_id in created:
                raise ValueError('NATIVE_NEW_CELL_IDENTITY_REQUIRED')
            created.append(cell_id)
            expected = {**initial, **dict(zip(created, packet['cells']))}
        elif name == 'run_code_cell':
            index = len(outcomes)
            if args != {'cellId': created[index]}:
                raise ValueError('NATIVE_BOUND_RUN_REQUIRED')
            outcomes.append(spec.validate_stage(packet, index, result))
    if len(outcomes) != 4:
        raise ValueError('NATIVE_STAGE_SEQUENCE_INCOMPLETE')
    result = spec.final_receipt(packet, outcomes, digest(raw))
    return {**result, 'transport': 'NATIVE_MCP_JSONRPC_NOT_MODEL_OUTPUT',
            'native_protocol_sha256': digest(raw), 'actual_tool_calls': len(calls), 'model_calls': 0}


async def run(snapshot, runtime_packet, runtime_receipt, destination, review):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from orchestrator import p001_transparent_setup as spec
    reviewed = require_review(review)
    config_raw = private_file(CONFIG)
    if digest(config_raw) != CONFIG_SHA256:
        raise ValueError('NATIVE_EXISTING_MCP_CONFIGURATION_CHANGED')
    config = read_json(config_raw)
    if set(config.get('mcpServers', {})) != {'colab-worker'}:
        raise ValueError('NATIVE_EXISTING_MCP_CONFIGURATION_CHANGED')
    server = config['mcpServers']['colab-worker']
    if server['command'] != COMMAND or server.get('args', []) != []:
        raise ValueError('NATIVE_EXISTING_MCP_CONFIGURATION_CHANGED')
    packet = spec.prepare(snapshot, read_json(private_file(runtime_packet)), read_json(private_file(runtime_receipt)))
    destination = Path(destination).absolute()
    if destination.is_relative_to(ROOT.resolve()):
        raise ValueError('NATIVE_PRIVATE_DESTINATION_REQUIRED')
    for parent in destination.parents:
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise ValueError('NATIVE_PRIVATE_PATH_ANCESTOR')
    info = destination.parent.stat()
    if info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError('NATIVE_PRIVATE_PARENT_REQUIRED')
    os.umask(0o077)
    destination.mkdir(mode=0o700, exist_ok=False)
    write_new(destination / 'packet.json', packet)
    write_new(destination / 'execution-intent.json', {'packet_sha256': digest(encoded(packet)),
              'client_sha256': digest(Path(__file__).read_bytes()), 'review': reviewed,
              'configuration_sha256': CONFIG_SHA256, 'max_wall_seconds': 1800,
              'patient_launch_authorized': False, 'automatic_retry': False})
    journal = Journal(destination / 'native-protocol.jsonl')
    try:
        with (destination / 'server.stderr.log').open('x') as errors:
            async with asyncio.timeout(1800):
                async with stdio_client(StdioServerParameters(command=COMMAND, args=[], env=server.get('env')), errlog=errors) as (read, write):
                    async with ClientSession(RecordedReceive(read, journal), RecordedSend(write, journal),
                                             read_timeout_seconds=datetime.timedelta(seconds=90)) as session:
                        await session.initialize()
                        await dispatch(packet, session, destination, spec)
        journal.close()
        result = verify_native(packet, private_file(destination / 'native-protocol.jsonl'), spec)
        write_new(destination / 'verified.json', result)
        return result
    except BaseException as error:
        journal.close()
        write_new(destination / 'stopped.json', {'status': 'NATIVE_SETUP_STOPPED_RECONCILE_ORIGINAL_REQUESTS',
                  'error_type': type(error).__name__, 'packet_sha256': digest(encoded(packet)),
                  'patient_launch_authorized': False, 'automatic_retry': False})
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['snapshot', 'runtime-packet', 'runtime-receipt', 'destination', 'review']:
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    try:
        result = asyncio.run(run(**vars(args)))
    except BaseException as error:
        print(json.dumps({'status': 'NATIVE_SETUP_STOPPED_RECONCILE_ORIGINAL_REQUESTS',
                          'error_type': type(error).__name__, 'patient_launch_authorized': False}))
        raise SystemExit(1) from None
    print(json.dumps({'status': result['status'], 'native_protocol_sha256': result['native_protocol_sha256'],
                      'actual_tool_calls': result['actual_tool_calls'], 'model_calls': 0, 'patient_launch_authorized': False}))


if __name__ == '__main__':
    main()