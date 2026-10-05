import asyncio
import copy
import json
from types import SimpleNamespace

import pytest
from orchestrator import p001_native_setup as native

PACKET = {'cells': ['# cpu\n', '# guarded claim\n', '# fixed setup\n', '# environment\n']}


class Spec:
    @staticmethod
    def validate_stage(packet, index, result):
        if any(x.get('output_type') == 'error' for x in result.get('outputs', [])):
            raise ValueError('REMOTE_STAGE_FAILED')
        value = json.loads(''.join(''.join(x['text']) for x in result['outputs']))
        if value != {'stage': index, 'ok': True}:
            raise ValueError('STAGE_RESULT_MISMATCH')
        return value

    @staticmethod
    def final_receipt(packet, outcomes, exchange_digest):
        assert len(outcomes) == 4
        return {'status': 'SYNTHETIC_FOUR_STAGES_VERIFIED', 'exchange_digest': exchange_digest,
                'patient_launch_authorized': False}


class Response:
    def __init__(self, value):
        self.value = value

    def model_dump(self, **kwargs):
        return self.value


class FakeSession:
    def __init__(self, *, fail_at=None, wrong_readback=False, stage_error=None):
        self.calls = []
        self.rows = []
        self.cells = [{'id': 'existing-unexecuted', 'cell_type': 'code', 'source': ['# prior cell\n']}]
        self.fail_at = fail_at
        self.wrong_readback = wrong_readback
        self.stage_error = stage_error
        self.ids = 0

    def record(self, direction, rpc):
        self.rows.append({'sequence': len(self.rows), 'direction': direction,
                          'recorded_at_utc': '2026-09-09T00:00:00+00:00', 'rpc': copy.deepcopy(rpc)})

    async def list_tools(self):
        return SimpleNamespace(tools=[SimpleNamespace(name=name) for name in native.TOOL_NAMES])

    async def call_tool(self, name, args, **kwargs):
        number = len(self.calls)
        self.calls.append((name, args))
        request_id = self.ids
        self.ids += 1
        self.record('sent', {'jsonrpc': '2.0', 'id': request_id, 'method': 'tools/call',
                             'params': {'name': name, 'arguments': args}})
        if number == self.fail_at:
            raise TimeoutError('SYNTHETIC_LOST_RESPONSE')
        if name == 'open_colab_browser_connection':
            value = {'result': True}
        elif name == 'get_cells':
            value = {'cells': copy.deepcopy(self.cells)}
            if self.wrong_readback and len(self.cells) == 5:
                value['cells'][-1]['source'] = ['# changed\n']
        elif name == 'add_code_cell':
            cell_id = 'new-' + str(number)
            self.cells.append({'id': cell_id, 'cell_type': 'code', 'source': [args['code']]})
            value = {'newCellId': cell_id}
        elif name == 'run_code_cell':
            index = [x['id'] for x in self.cells[1:]].index(args['cellId'])
            output = {'output_type': 'stream', 'text': [json.dumps({'stage': index, 'ok': True})]}
            if index == self.stage_error:
                output = {'output_type': 'error', 'ename': 'RuntimeError', 'evalue': 'synthetic'}
            value = {'outputs': [output]}
        else:
            raise AssertionError(name)
        result = {'content': [{'type': 'text', 'text': json.dumps(value)}], 'isError': False}
        self.record('received', {'jsonrpc': '2.0', 'id': request_id, 'result': result})
        return Response(result)

    def raw(self):
        return b''.join(native.encoded(row) + b'\n' for row in self.rows)


def executed(tmp_path, **kwargs):
    session = FakeSession(**kwargs)
    asyncio.run(native.dispatch(PACKET, session, tmp_path, Spec))
    return session


def test_native_order_and_original_ids(tmp_path):
    session = executed(tmp_path)
    result = native.verify_native(PACKET, session.raw(), Spec)
    assert result['status'] == 'SYNTHETIC_FOUR_STAGES_VERIFIED'
    assert result['actual_tool_calls'] == 14
    assert result['model_calls'] == 0
    assert result['patient_launch_authorized'] is False
    assert 'existing-unexecuted' not in [args.get('cellId') for name, args in session.calls if name == 'run_code_cell']
    assert len(list(tmp_path.glob('*.intent.json'))) == 14


@pytest.mark.parametrize('fail_at', [0, 2, 5, 7, 9, 11, 13])
def test_lost_response_never_retries(tmp_path, fail_at):
    session = FakeSession(fail_at=fail_at)
    with pytest.raises(TimeoutError):
        asyncio.run(native.dispatch(PACKET, session, tmp_path, Spec))
    assert len(session.calls) == fail_at + 1
    assert (tmp_path / (str(fail_at).zfill(2) + '.intent.json')).exists()
    assert not (tmp_path / (str(fail_at).zfill(2) + '.response.json')).exists()
    with pytest.raises(ValueError, match='UNCERTAIN'):
        native.verify_native(PACKET, session.raw(), Spec)


def test_changed_readback_stops_before_any_run(tmp_path):
    session = FakeSession(wrong_readback=True)
    with pytest.raises(ValueError, match='READBACK'):
        asyncio.run(native.dispatch(PACKET, session, tmp_path, Spec))
    assert not any(name == 'run_code_cell' for name, args in session.calls)


@pytest.mark.parametrize('stage', [0, 1, 2, 3])
def test_remote_error_stops_before_next_stage(tmp_path, stage):
    session = FakeSession(stage_error=stage)
    with pytest.raises(ValueError, match='REMOTE_STAGE_FAILED'):
        asyncio.run(native.dispatch(PACKET, session, tmp_path, Spec))
    assert sum(name == 'run_code_cell' for name, args in session.calls) == stage + 1


def mutated(raw, mutate):
    rows = [json.loads(line) for line in raw.splitlines()]
    mutate(rows)
    for index, row in enumerate(rows):
        row['sequence'] = index
    return b''.join(native.encoded(row) + b'\n' for row in rows)


@pytest.mark.parametrize('change', ['duplicate_run', 'unbound_run', 'arbitrary_source', 'old_output_read', 'response_id', 'missing_response', 'reordered_response', 'duplicate_request'])
def test_native_proof_rejects_tampering(tmp_path, change):
    session = executed(tmp_path)
    def alter(rows):
        calls = [row for row in rows if row['direction'] == 'sent']
        if change == 'duplicate_run':
            pair = copy.deepcopy(rows[-2:])
            for row in pair:
                row['rpc']['id'] = 99
            rows.extend(pair)
        elif change == 'unbound_run':
            calls[-1]['rpc']['params']['arguments']['cellId'] = 'existing-unexecuted'
        elif change == 'arbitrary_source':
            calls[2]['rpc']['params']['arguments']['code'] = 'print(99)'
        elif change == 'old_output_read':
            calls[1]['rpc']['params']['arguments']['includeOutputs'] = True
        elif change == 'response_id':
            rows[-1]['rpc']['id'] = 888
        elif change == 'missing_response':
            rows.pop()
        elif change == 'reordered_response':
            rows[-3], rows[-1] = rows[-1], rows[-3]
        elif change == 'duplicate_request':
            calls[-1]['rpc']['id'] = calls[0]['rpc']['id']
    with pytest.raises(ValueError):
        native.verify_native(PACKET, mutated(session.raw(), alter), Spec)


def test_existing_intent_is_not_replaced(tmp_path):
    first = {'preserved': True}
    native.write_new(tmp_path / '00.intent.json', first)
    session = FakeSession()
    with pytest.raises(FileExistsError):
        asyncio.run(native.dispatch(PACKET, session, tmp_path, Spec))
    assert session.calls == []
    assert json.loads((tmp_path / '00.intent.json').read_text()) == first


def test_private_file_refuses_symlink_and_fifo(tmp_path):
    target = tmp_path / 'target'
    target.write_text('{}')
    target.chmod(0o600)
    link = tmp_path / 'link'
    link.symlink_to(target)
    with pytest.raises(ValueError):
        native.private_file(link)
    import os
    pipe = tmp_path / 'pipe'
    os.mkfifo(pipe, 0o600)
    with pytest.raises(ValueError):
        native.private_file(pipe)


def test_tool_error_and_ambiguous_representations_refused():
    with pytest.raises(ValueError, match='TOOL_ERROR'):
        native.decode_result('get_cells', {'isError': True})
    with pytest.raises(ValueError, match='DIFFER'):
        native.decode_result('get_cells', {'content': [{'type': 'text', 'text': '{}'}], 'structuredContent': {'cells': []}})
    assert native.decode_result('open_colab_browser_connection', {'content': [{'type': 'text', 'text': 'true'}], 'structuredContent': {'result': True}}) == {'result': True}


def test_provider_ping_is_recorded_without_new_tool_operation(tmp_path):
    session = executed(tmp_path)
    def add_ping(rows):
        rows.extend([{'direction': 'received', 'rpc': {'jsonrpc': '2.0', 'id': 4321, 'method': 'ping'}},
                     {'direction': 'sent', 'rpc': {'jsonrpc': '2.0', 'id': 4321, 'result': {}}}])
    assert native.verify_native(PACKET, mutated(session.raw(), add_ping), Spec)['actual_tool_calls'] == 14