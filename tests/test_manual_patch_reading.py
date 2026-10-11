import json
import pytest
from orchestrator import manual_context as m
from orchestrator.review_contract import strict_json

def fixture(text):
    patch={'schema':'safe-notebook-patch/v1','original_sha256':'a'*64,'view_sha256':'b'*64,
        'edits':[{'unit':'cells/3/source','start':0,'end':3,'before_sha256':'c'*64,'replacement':text}]}
    raw=json.dumps(patch,ensure_ascii=False,separators=(',',':')).encode()
    d={'id':'notebook_patch','path':'evidence/original.txt','sha256':m.budget.sha(raw),'delivery':'Read exact original.'}
    return raw,d,patch

def test_large_single_line_patch_gets_bounded_lossless_reading_copy():
    raw,d,original=fixture('value = "synthetic"  # exact source\n'*3500)
    assert len(raw)>100000 and len(raw.splitlines())==1
    before=bytes(raw);copy,body=m._notebook_patch_reading_copy(d,raw)
    view=strict_json(body);restored=view['patch']
    for edit in restored['edits']:edit['replacement']=''.join(edit['replacement'])
    assert restored==original and raw==before
    assert copy['original_sha256']==m.budget.sha(raw) and copy['original_path']==d['path']
    assert m.budget.sha(body)==copy['sha256'] and d['readable_patch']==copy
    lines=body.splitlines(keepends=True)
    assert max(sum(map(len,lines[n:n+100])) for n in range(len(lines)))<=16000
    assert copy['page_lines']==100

@pytest.mark.parametrize('text',['','no final newline','a\r\nb\nc\r','quoted " and Unicode \u03bb\n'])
def test_line_endings_empty_and_unicode_preserved(text):
    raw,d,patch=fixture(text);_,body=m._notebook_patch_reading_copy(d,raw)
    assert ''.join(strict_json(body)['patch']['edits'][0]['replacement'])==text

@pytest.mark.parametrize('fault',['hash','duplicate','nonfinite','wrong_schema','oversized_line','identifier'])
def test_reading_copy_does_not_weaken_hash_schema_or_privacy_checks(fault):
    raw,d,patch=fixture('ok\n')
    if fault=='hash':d['sha256']='0'*64
    else:
        if fault=='duplicate':raw=b'{"schema":"safe-notebook-patch/v1","schema":"other","edits":[]}'
        elif fault=='nonfinite':raw=b'{"schema":"safe-notebook-patch/v1","edits":[],"x":NaN}'
        else:
            if fault=='wrong_schema':patch['schema']='other'
            if fault=='oversized_line':patch['edits'][0]['replacement']='a'*17000
            if fault=='identifier':patch['edits'][0]['replacement']='sub'+'-stroke'+'1234'
            raw=json.dumps(patch).encode()
        d['sha256']=m.budget.sha(raw)
    with pytest.raises((ValueError,m.budget.ContextError)):
        m._notebook_patch_reading_copy(d,raw)
    assert 'readable_patch' not in d
