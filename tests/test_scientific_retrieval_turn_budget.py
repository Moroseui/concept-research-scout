"""Proposed command bounds and authenticated lookup; no hosted admission."""
from copy import deepcopy
import os
import pytest
from orchestrator import hosted_cycle as cycle, scientific_evidence_access as access
from orchestrator import scientific_evidence_runtime as runtime
from test_scientific_evidence_access import capture, case


def test_actual_command_builder_scopes_budget_and_tools():
    rt={'command':'/usr/bin/python3','args':['-B','synthetic_reader.py']}
    plain=cycle.model_command('claude')
    enabled=cycle.model_command('claude',rt)
    assert plain[plain.index('--max-turns')+1]=='3'
    assert enabled[enabled.index('--max-turns')+1]=='32'
    assert '--dangerously-skip-permissions' not in enabled
    assert enabled[enabled.index('--permission-mode')+1]=='dontAsk'
    assert enabled[enabled.index('--tools')+1]==''
    assert enabled[enabled.index('--allowedTools')+1]==','.join('mcp__'+runtime.SERVER+'__'+t for t in runtime.TOOLS)
    assert '--max-turns' not in cycle.model_command('astra',rt)
    with pytest.raises(ValueError):cycle.model_command('unknown',rt)


@pytest.mark.parametrize('growth',[0,2000,9000])
def test_named_search_work_is_independent_of_unrelated_history(capture,monkeypatch,growth):
    reader=capture[-1]
    target=next(r for r in reader.records if r['kind']=='change_event' and r['provenance'].get('event_kind')=='REVIEW')
    original=reader._body(target); calls=[]
    # Extra settled-index entries are explicit synthetic size stress, not originals.
    reader.rows={**{f'synthetic/{i}':{'name':f'synthetic/{i}'} for i in range(growth)},**reader.rows}
    real=reader._body
    def body(row):calls.append(row['name']);return real(row)
    monkeypatch.setattr(reader,'_body',body)
    result=reader.call('search',{'capture':reader.identity,'cursor':0,'text':'REQUEST_CHANGES','name':target['name']})
    assert result['scanned_records']==1 and result['next_cursor'] is None
    assert calls==[target['name']]
    match=result['matches'][0]
    read=reader.call('read',{'capture':reader.identity,'name':target['name'],'sha256':target['sha256'],
        'offset':match['offset_characters'],'characters':64})
    assert read['content'].startswith('REQUEST_CHANGES')
    assert reader._body(target)==original


@pytest.mark.parametrize('bad',['missing','path','changed-bytes','changed-capture','cursor','unexpected-field'])
def test_named_search_still_authenticates_and_fails_closed(capture,bad):
    reader=capture[-1];row=reader.records[0]
    args={'capture':reader.identity,'cursor':0,'text':'request','name':row['name']}
    if bad=='missing':args['name']='not-in-capture'
    elif bad=='path':args['name']='/etc/passwd'
    elif bad=='changed-capture':args['capture']='f'*64
    elif bad=='cursor':args['cursor']=2
    elif bad=='unexpected-field':args['permission']='allow'
    else:
        p=capture[3]/'objects'/(row['sha256']+'.txt');p.chmod(0o600);p.write_text('changed')
    with pytest.raises(ValueError):reader.call('search',args)


def test_named_search_is_optional_in_actual_tool_schema():
    schema=next(x for x in access.definitions() if x['name']=='scientific_evidence_search')['inputSchema']
    assert 'name' in schema['properties'] and 'name' not in schema['required']
    assert set(schema['required'])=={'capture','cursor','text'}
    assert access.MAX_CALLS==64 and access.MAX_RETURN_BYTES==262144
    assert access.SEARCH_RECORDS==100 and access.READ_CHARACTERS==8192
