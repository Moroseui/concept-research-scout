import base64
import json
import os
import stat

import pytest

from orchestrator import implementation_host_read as h
from orchestrator import inspection_access as access


def test_root_read_authority_is_exact():
    value = {'schema': h.PROFILE, 'operator_original_sha256': h.OPERATOR_SHA,
             'authority_request': h.AUTH_REQUEST, 'authorized_event': h.AUTH_EVENT}
    assert h.profile(value) == value
    for key in value:
        with pytest.raises(ValueError):
            h.profile({**value, key: 'changed'})
    with pytest.raises(ValueError):
        h.profile({**value, 'execute': True})


@pytest.mark.parametrize('operation,args', [
    ('write', {'path': '/tmp/f', 'content': 'changed'}),
    ('read', {'path': 'relative'}),
    ('read', {'path': '/tmp/f', 'command': 'id'}),
    ('read', {'path': '/tmp/f', 'offset': -1}),
    ('read', {'path': '/tmp/f', 'length': 32769}),
    ('read', {'path': '/tmp/f', 'length': True}),
    ('read', {'path': '/tmp/f\0'}),
    ('list', {'path': '/', 'recursive': True}),
    ('list', {'path': '/', 'limit': 201}),
    ('search', {'path': '/tmp/f', 'text': ''}),
    ('search', {'path': '/tmp/f', 'text': 'x', 'regex': True}),
])
def test_no_execution_or_unbounded_operation(operation, args):
    with pytest.raises(ValueError):
        h.normalize({'operation': operation, 'arguments': args})


def test_range_read_preserves_literal_original(tmp_path):
    p = tmp_path/'ordinary'; p.write_bytes(b'one\ntwo\nthree\n'); before = p.stat()
    result = h.inspect({'operation': 'read', 'arguments': {'path': str(p), 'offset': 4, 'length': 4}})
    assert result['content'] == 'two\n'
    assert result['range_sha256'] == h.sha(b'two\n')
    assert result['whole_file_sha256'] is None
    assert result['file_identity']['ino'] == before.st_ino
    assert p.read_bytes() == b'one\ntwo\nthree\n'
    assert p.stat().st_mtime_ns == before.st_mtime_ns


def test_binary_read_and_complete_hash(tmp_path):
    p = tmp_path/'binary'; p.write_bytes(b'\xff\0')
    result = h.inspect({'operation': 'read', 'arguments': {'path': str(p)}})
    assert base64.b64decode(result['content']) == p.read_bytes()
    assert result['whole_file_sha256'] == h.sha(p.read_bytes())


def test_symlink_discovery_is_not_selected_packet(tmp_path):
    target = tmp_path/'outside'; target.write_text('independent evidence')
    alias = tmp_path/'alias'; alias.symlink_to(target)
    result = h.inspect({'operation': 'read', 'arguments': {'path': str(alias)}})
    assert result['resolved_path'] == str(target)
    assert result['content'] == 'independent evidence'


def test_directory_discovery_and_literal_search(tmp_path):
    for name in ['a', 'b', 'c']:
        (tmp_path/name).write_text('one needle two needle three')
    result = h.inspect({'operation': 'list', 'arguments': {'path': str(tmp_path), 'offset': 1, 'limit': 1}})
    assert result['entries'] == ['b'] and result['total_entries'] == 3
    result = h.inspect({'operation': 'search', 'arguments': {'path': str(tmp_path/'a'), 'text': 'needle'}})
    assert result['matches'] == [4, 15]


@pytest.mark.parametrize('kind', ['fifo', 'directory'])
def test_special_files_never_read_as_streams(tmp_path, kind):
    p = tmp_path/'special'
    os.mkfifo(p) if kind == 'fifo' else p.mkdir()
    with pytest.raises(ValueError, match='REGULAR_FILE'):
        h.inspect({'operation': 'read', 'arguments': {'path': str(p)}})


def test_changed_file_never_claimed_stable(tmp_path, monkeypatch):
    p = tmp_path/'f'; p.write_bytes(b'one')
    pread = os.pread
    def changed(fd, length, offset):
        raw = pread(fd, length, offset)
        p.write_bytes(b'two')
        return raw
    monkeypatch.setattr(os, 'pread', changed)
    with pytest.raises(ValueError, match='CHANGED_DURING'):
        h.inspect({'operation': 'read', 'arguments': {'path': str(p)}})


def test_rpc_fixed_tool_transport(monkeypatch):
    monkeypatch.setattr(h, 'forward', lambda request: {'status': 'OBSERVED', 'request': request})
    response = h.rpc({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'})
    assert [x['name'] for x in response['result']['tools']] == list(h.NAMES)
    result = h.rpc({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
                    'params': {'name': 'read', 'arguments': {'path': '/any/file'}}})
    assert json.loads(result['result']['content'][0]['text'])['request']['arguments']['path'] == '/any/file'
    with pytest.raises(ValueError):
        h.rpc({'jsonrpc': '2.0', 'id': 3, 'method': 'execute', 'command': 'id'})
    assert h.mcp_config()['mcpServers']['hostfs']['command'] == '/runtime/python'


def test_native_write_and_execution_restrictions_unchanged():
    original = access.terminal_settings()
    proposed = access.terminal_settings(host_read=True)
    added = proposed['permissions']['allow'][len(original['permissions']['allow']):]
    assert added == ['mcp__hostfs__read', 'mcp__hostfs__list', 'mcp__hostfs__search']
    proposed['permissions']['allow'] = proposed['permissions']['allow'][:-3]
    assert proposed == original
    assert access.terminal_request('Write', {'file_path': '/report/review.md', 'content': 'report'})
    for tool, args in [('Write', {'file_path': '/any/source', 'content': 'change'}),
                       ('Bash', {'command': 'id'}), ('Edit', {'file_path': '/report/review.md'})]:
        with pytest.raises(ValueError):
            access.terminal_request(tool, args)


def test_original_read_receipt_is_bound_and_never_claims_coverage(tmp_path):
    p = tmp_path/'f'; p.write_text('original')
    result = h.inspect({'operation': 'read', 'arguments': {'path': str(p)}})
    binding = {'schema': h.PROFILE, 'session_id': 'session', 'attempt': 1,
               'operator_original_sha256': h.OPERATOR_SHA, 'cgroup': '0::/fixture.service\n'}
    original = {**binding, 'sequence': 1, 'request': {'operation': 'read', 'arguments': {'path': str(p)}},
                'response': result}
    raw = h.encoded(original)
    value = {**binding, 'records': [{'name': '0001.json', 'sha256': h.sha(raw), 'bytes': len(raw)}],
             'originals': [original], 'calls': 1, 'response_utf8_bytes': len(h.encoded(result)),
             'automatic_retry': False}
    assert h.validate_originals(value, session='session', attempt=1)['calls'] == 1
    for kwargs in [{'session': 'other', 'attempt': 1}, {'session': 'session', 'attempt': 2}]:
        with pytest.raises(ValueError):
            h.validate_originals(value, **kwargs)
    value['originals'][0]['response']['content'] = 'changed'
    with pytest.raises(ValueError, match='CHANGED'):
        h.validate_originals(value, session='session', attempt=1)
