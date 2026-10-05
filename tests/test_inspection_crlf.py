"""Synthetic native display proofs; no provider, real permission or state changes."""
import copy
import json
import pytest
from orchestrator import inspection_access as a, inspection_review as r
from test_inspection_review import fixture_manifest, fixture_attempt


def response(raw, *, first=1, count=None, omit_lf=False):
    lines = raw.decode().splitlines(keepends=True)
    if count is None: count = len(lines)
    original = ''.join(lines[first-1:first-1+count])
    content = original.replace('\r\n', '\n')
    if omit_lf and content.endswith('\n'): content = content[:-1]
    manifest = {'schema': a.MANIFEST_SCHEMA, 'source': 'a'*40, 'files': {'code.py': {
        'sha256': a.digest(raw), 'bytes': len(raw), 'line_count': len(lines)}}}
    normalized = {'path': 'code.py', 'start_line': first, 'limit': max(1, count)}
    output = {'type': 'text', 'file': {'filePath': '/review/code.py', 'content': content,
        'numLines': count, 'startLine': first, 'totalLines': len(lines)}}
    return manifest, normalized, output


@pytest.mark.parametrize('raw', [b'a\r\nb\r\n', b'a\r\nb\n', b'a\nb\r\n',
                               b'a\r\nb', 'alpha\r\n\u03b2eta\n'.encode(), b'\r\n'])
@pytest.mark.parametrize('omit_lf', [False, True])
def test_original_and_native_display_are_distinct_exact_bindings(raw, omit_lf):
    manifest, normalized, output = response(raw, omit_lf=omit_lf)
    actual = a.verify_read_response(manifest, normalized, output, raw)
    assert actual['fragment_sha256'] == a.digest(raw)
    assert actual['displayed_fragment_sha256'] == a.digest(raw.replace(b'\r\n', b'\n'))
    assert a.verify_read_fragment(actual, output['file']['content']) == raw
    assert actual['returned_content_sha256'] == a.digest(output['file']['content'].encode())
    assert manifest['files']['code.py']['sha256'] == a.digest(raw)


def test_partial_read_crlf_positions_are_relative_to_returned_fragment():
    raw = b'a\r\nb\nc\r\nd\r\n'
    manifest, normalized, output = response(raw, first=2, count=2, omit_lf=True)
    actual = a.verify_read_response(manifest, normalized, output, raw)
    assert actual['crlf_line_numbers'] == [2]
    assert actual['fragment_sha256'] == a.digest(b'b\nc\r\n')
    assert (actual['start_line'], actual['end_line']) == (2, 3)


@pytest.mark.parametrize('raw', [b'a\nb\n', b'a\nb', b''])
def test_lf_only_observation_keeps_legacy_shape(raw):
    manifest, normalized, output = response(raw)
    actual = a.verify_read_response(manifest, normalized, output, raw)
    assert 'displayed_fragment_sha256' not in actual
    assert 'crlf_line_numbers' not in actual
    assert actual['comparison'] == 'literal source lines; optional final LF omission'
    assert a.verify_read_fragment(actual, output['file']['content']) == raw


@pytest.mark.parametrize('change', ['short', 'spaces', 'missing_middle_lf', 'bare_cr_removed',
                                  'bom_removed', 'nul_removed', 'wrong_type'])
def test_normalization_does_not_allow_other_edits(change):
    raw = b'a\r\nb\r\n'
    if change == 'bare_cr_removed': raw = b'a\rb\r\n'
    if change == 'bom_removed': raw = b'\xef\xbb\xbfa\r\nb\r\n'
    if change == 'nul_removed': raw = b'a\x00\r\nb\r\n'
    manifest, normalized, output = response(raw)
    content = output['file']['content']
    if change == 'short': content = content[:-2]
    if change == 'spaces': content = ' ' + content
    if change == 'missing_middle_lf': content = content.replace('\n', '', 1)
    if change == 'bare_cr_removed': content = content.replace('\r', '')
    if change == 'bom_removed': content = content.removeprefix('\ufeff')
    if change == 'nul_removed': content = content.replace('\x00', '')
    if change == 'wrong_type': content = []
    output['file']['content'] = content
    output['file']['truncatedByTokenCap'] = True
    with pytest.raises(ValueError): a.verify_read_response(manifest, normalized, output, raw)


@pytest.mark.parametrize('change', ['missing_display', 'missing_positions', 'empty', 'duplicate', 'unordered',
                                  'wrong_line', 'zero', 'past_end', 'bool', 'string', 'display_hash', 'source_hash'])
def test_claimed_conversion_requires_exact_source_reconstruction(change):
    raw = b'a\r\nb\r\n'
    manifest, normalized, output = response(raw)
    actual = a.verify_read_response(manifest, normalized, output, raw)
    if change == 'missing_display': actual.pop('displayed_fragment_sha256')
    elif change == 'missing_positions': actual.pop('crlf_line_numbers')
    elif change == 'display_hash': actual['displayed_fragment_sha256'] = '0'*64
    elif change == 'source_hash': actual['fragment_sha256'] = actual['displayed_fragment_sha256']
    else: actual['crlf_line_numbers'] = {'empty': [], 'duplicate': [1, 1], 'unordered': [2, 1],
        'wrong_line': [1], 'zero': [0], 'past_end': [3], 'bool': [True], 'string': ['1']}[change]
    with pytest.raises(ValueError): a.verify_read_fragment(actual, output['file']['content'])


def crlf_session(raw=b'a\r\nb\n', *, number=1, previous=None, status='APPROVE', start=1, count=2):
    manifest_raw, policy = fixture_manifest()
    manifest = json.loads(manifest_raw)
    access = json.loads(manifest['access_manifest_original'])
    access['files']['code.py'].update(sha256=r.digest(raw), bytes=len(raw))
    manifest['access_manifest_original'] = r.encoded(access).decode()
    manifest['access_manifest_sha256'] = r.digest(r.encoded(access))
    manifest_raw = r.encoded(manifest)
    original = fixture_attempt(manifest_raw, policy, number=number, previous=previous,
                               status=status, start=start, count=count)
    wrapper = json.loads(original['journal'][1])
    row = json.loads(wrapper['observation_original'])
    hook = json.loads(wrapper['hook_input_original'])
    _, normalized, output = response(raw, first=start, count=count, omit_lf=True)
    hook['tool_response'] = output
    row['raw_input_sha256'] = r.digest(r.encoded(hook))
    row['tool_response_sha256'] = r.digest(r.encoded(output))
    row['actual_read'] = a.verify_read_response(access, normalized, output, raw)
    wrapper.update(observation_original=r.encoded(row).decode(), hook_input_original=r.encoded(hook).decode())
    original['journal'][1] = r.encoded(wrapper)
    return manifest_raw, original


def test_full_journal_keeps_original_hash_and_accepts_displayed_crlf_relation():
    manifest, original = crlf_session()
    result = r.validate_session(manifest, [original])
    assert result['status'] == 'APPROVE'
    assert result['reads'] == {'code.py': [[1, 2]]}
    assert json.loads(manifest)['current_request_sha256'] == 'c'*64


def test_continued_read_ranges_preserve_mixed_original_bytes():
    manifest, first = crlf_session(status='IN_PROGRESS', count=1)
    previous = r.validate_session(manifest, [first])['attempts'][0]
    same_manifest, second = crlf_session(number=2, previous=previous, start=2, count=1)
    assert same_manifest == manifest
    result = r.validate_session(manifest, [first, second])
    assert result['status'] == 'APPROVE' and result['required_ranges_missing'] == {}


def test_display_hash_cannot_replace_full_original_source_hash():
    manifest, original = crlf_session()
    wrapper = json.loads(original['journal'][1]); row = json.loads(wrapper['observation_original'])
    actual = row['actual_read']
    actual['fragment_sha256'] = actual.pop('displayed_fragment_sha256')
    actual.pop('crlf_line_numbers')
    wrapper['observation_original'] = r.encoded(row).decode(); original['journal'][1] = r.encoded(wrapper)
    result = r.validate_session(manifest, [original])
    assert result['status'] == 'RECONCILIATION_REQUIRED'
    assert result['attempts'][0]['reason'] == 'FULL_READ_SOURCE_DIGEST'


def test_adverse_terminal_is_not_resumed_after_repair():
    manifest, original = crlf_session(status='REQUEST_CHANGES')
    prior = r.validate_session(manifest, [original])
    assert prior['status'] == 'REQUEST_CHANGES'
    _, next_attempt = crlf_session(number=2, previous=prior['attempts'][0])
    with pytest.raises(ValueError, match='TERMINAL_REVIEW_CANNOT_RESUME'):
        r.validate_session(manifest, [original, next_attempt])
