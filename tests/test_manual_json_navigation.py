"""Deterministic line-reader constraints; not a live Claude tool invocation."""
import json

import pytest

from orchestrator import manual_context as context, context_budget as budget
from test_context_budget import root
from test_scientific_intake import registered, save_registry, build


def check_pages(raw):
    lines = raw.splitlines(keepends=True)
    assert len(lines) > 1
    for start in range(len(lines)):
        assert len(b''.join(lines[start:start+100])) <= context.JSON_PAGE_BYTES
    return b''.join(b''.join(lines[n:n+100]) for n in range(0, len(lines), 100))


@pytest.mark.parametrize('stage', sorted(context.OUTPUTS))
def test_native_line_paging_can_discover_every_exact_original(root, monkeypatch, stage):
    ref, registry = registered(root, monkeypatch)
    original = registry['views'][0]
    for n in range(180):
        registry['views'].append({**original, 'id': 'distinct-registration-'+str(n)})
    ref = save_registry(root, registry)
    before = {p: p.read_bytes() for p in (root/'view.txt', root/'omissions.json')}
    body, measurement = build(root, ref, stage)
    work = root/'work'/stage
    index = measurement['private_scientific_index']
    raw = (work/index['path']).read_bytes()
    assert len(raw) > 100_000  # the actual failure class, not a tiny index
    assert budget.sha(raw) == index['sha256']
    navigation = json.loads(check_pages(raw))
    assert navigation['registry_sha256'] == ref['sha256']
    assert 'at most 100 lines per read' in body
    assert 'distinct-registration-179' not in body
    assert len(body) < 200_000
    for row in navigation['views']:
        original_raw = (work/row['path']).read_bytes()
        assert budget.sha(original_raw) == row['sha256']
        if row['path'].endswith('-omissions.json'):
            copy = row['readable_json']
            readable = (work/copy['path']).read_bytes()
            assert copy['original_path'] == row['path']
            assert copy['original_sha256'] == row['sha256']
            assert budget.sha(readable) == copy['sha256']
            assert json.loads(check_pages(readable)) == json.loads(original_raw)
    for path, old in before.items():
        assert path.read_bytes() == old
    for row in measurement['workspace_files']:
        assert (work/row['path']).stat().st_mode & 0o777 == 0o400


@pytest.mark.parametrize('stage', ['result_interpretation_author', 'result_interpretation_review'])
def test_validation_original_and_pageable_copy_are_both_authenticated(root, monkeypatch, stage):
    ref, _ = registered(root, monkeypatch)
    value = {'kind': 'SAVED_EVIDENCE_IDENTITY_ONLY', 'scientific_acceptance': False,
             'views': [{'id': 'synthetic-'+str(n), 'sha256': 'a'*64} for n in range(2000)]}
    raw = json.dumps(value).encode()
    (root/'validation.json').write_bytes(raw)
    row = {'id': 'validation', 'type': 'validation_result', 'version': 1,
           'path': 'validation.json', 'sha256': budget.sha(raw)}
    work = root/'validation-work'
    body, measured = context.build(root, stage=stage, idea_ids=['sprints-stocktake'],
        task='Inspect saved evidence.', artifacts=[row], workspace=work, private_intake=ref)
    original = next(x for x in measured['workspace_files'] if x.get('type') == 'validation_result')
    readable = original['readable_json']
    assert (work/original['path']).read_bytes() == raw
    assert readable['original_sha256'] == budget.sha(raw)
    assert json.loads(check_pages((work/readable['path']).read_bytes())) == value
    assert readable['sha256'] in body and original['sha256'] in body
    assert 'synthetic-1999' not in body and len(body) < 200_000
    path = work/readable['path']
    path.chmod(0o600); path.write_bytes(path.read_bytes()+b' ')
    with pytest.raises(ValueError, match='^MANUAL_WORKSPACE_FILE_CHANGED$'):
        context.build(root, stage=stage, idea_ids=['sprints-stocktake'], task='Inspect saved evidence.',
                      artifacts=[row], workspace=work, private_intake=ref)


@pytest.mark.parametrize('raw,reason', [
    (b'{"x":1,"x":2}', 'MANUAL_JSON_DUPLICATE_KEY'),
    (b'{"x":NaN}', 'MANUAL_JSON_NONFINITE'),
    (json.dumps({'x': 'x'*17000}).encode(), 'MANUAL_JSON_PAGE_TOO_LARGE'),
])
def test_ambiguous_nonfinite_or_unpageable_metadata_refuses(raw, reason):
    with pytest.raises(ValueError, match='^'+reason+'$'):
        context._pageable_json(raw)


def test_readable_copy_keeps_public_scanner(root):
    # Synthetic identifier assembled only in the test, never real case data.
    raw = json.dumps({'case': 'sub-' + 'stroke' + str(1).zfill(4)}).encode()
    with pytest.raises(ValueError, match='^CASE_LEVEL_RECORD_REJECTED$'):
        context._json_reading_copy({'id': 'metadata', 'path': 'evidence/original.json',
                                   'sha256': budget.sha(raw)}, raw)
