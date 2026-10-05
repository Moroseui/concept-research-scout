"""Native-store retrieval checks; these fixtures are not hosted model inspection."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from orchestrator import scientific_evidence_access as access, change_requests as changes
from orchestrator.hosted_cycle import encoded
from test_change_requests import case, authority, application, review, AGENT

TASK='b'*64


@pytest.fixture
def capture(case,tmp_path):
    repo,store,folder,request=case
    authority(folder);applied=application(folder,tmp_path)
    review(folder,applied,tmp_path,verdict='REQUEST_CHANGES')
    source=request['target']['source']
    captured=access.capture_changes(store,[request['identity']],source=source,task_binding=TASK)
    cache=tmp_path/'cache';descriptor=access.write_capture(cache,captured)
    reader=access.Reader(cache,descriptor['manifest_sha256'],source=source,task_binding=TASK,owner=os.getuid())
    return store,folder,request,cache,descriptor,reader


def test_native_originals_and_adverse_judgment_are_all_discoverable(capture):
    store,folder,request,cache,descriptor,reader=capture
    records=reader.call('list',{'capture':reader.identity,'cursor':0,'kind':'all'})['records']
    originals={(folder/'request.json').read_bytes()}
    originals.update(p.read_bytes() for p in (folder/'events').glob('*.json'))
    originals.update(p.read_bytes() for p in (folder/'evidence').iterdir() if p.is_file())
    actual=set()
    for row in records:
        reply=reader.call('read',{'capture':reader.identity,'name':row['name'],'sha256':row['sha256'],
            'offset':0,'characters':access.READ_CHARACTERS})
        assert reply['next_offset_characters'] is None
        actual.add(reply['content'].encode())
    assert originals==actual
    found=reader.call('search',{'capture':reader.identity,'cursor':0,'text':'REQUEST_CHANGES'})
    assert len(found['matches'])==1
    assert found['matches'][0]['record']['provenance']['event_kind']=='REVIEW'


def test_append_does_not_change_old_capture_or_duplicate_old_objects(capture):
    store,folder,request,cache,descriptor,old=capture
    before={p.name:p.read_bytes() for p in (cache/'objects').iterdir()}
    changes.record(folder,'DISPOSITION',AGENT,{'rationale':'Later state is not silently imported.',
        'affected_results':['fixture']})
    assert old.call('search',{'capture':old.identity,'cursor':0,'text':'Later state'})['matches']==[]
    current=access.capture_changes(store,[request['identity']],source=descriptor['source'],task_binding=TASK)
    newer=access.write_capture(cache,current)
    assert newer['manifest_sha256']!=descriptor['manifest_sha256']
    assert len(list((cache/'objects').iterdir()))==len(before)+1
    assert all((cache/'objects'/k).read_bytes()==v for k,v in before.items())
    again=access.write_capture(cache,current)
    assert again==newer
    assert old.call('search',{'capture':old.identity,'cursor':0,'text':'REQUEST_CHANGES'})['matches']


@pytest.mark.parametrize('kind',['original_event','original_evidence','head_gap','wrong_scope'])
def test_native_capture_rejects_changed_originals(capture,kind):
    store,folder,request,cache,descriptor,reader=capture
    ids=[request['identity']]
    if kind=='original_event':
        p=next((folder/'events').glob('0001-*'));value=json.loads(p.read_bytes());value['payload']['rationale']='tampered';p.write_bytes(encoded(value))
    elif kind=='original_evidence':
        p=next((folder/'evidence').iterdir());p.write_text('tampered')
    elif kind=='head_gap':
        p=next((folder/'events').glob('0001-*'));p.rename(folder/'preserved-moved-event.json')
    else:ids=['f'*64]
    with pytest.raises((ValueError,FileNotFoundError)):
        access.capture_changes(store,ids,source=descriptor['source'],task_binding=TASK)


@pytest.mark.parametrize('kind',['hash','contents','missing','symlink','writable','owner','task','source'])
def test_delivery_requires_exact_capture_and_originals(capture,tmp_path,kind):
    store,folder,request,cache,descriptor,reader=capture
    row=reader.records[0];p=cache/'objects'/(row['sha256']+'.txt')
    if kind in ('task','source','owner'):
        kwargs={'source':descriptor['source'],'task_binding':TASK,'owner':os.getuid()}
        kwargs[{'task':'task_binding','source':'source','owner':'owner'}[kind]]={
            'task':'e'*64,'source':'e'*40,'owner':os.getuid()+1}[kind]
        with pytest.raises(ValueError):
            access.Reader(cache,reader.identity,**kwargs)
        return
    if kind=='hash':
        args={'capture':reader.identity,'name':row['name'],'sha256':'f'*64,'offset':0,'characters':10}
    else:
        args={'capture':reader.identity,'name':row['name'],'sha256':row['sha256'],'offset':0,'characters':10}
        if kind=='contents':
            p.chmod(0o600)  # Simulate owner tampering with the read-only original.
            p.write_text('changed')
        elif kind=='missing':p.unlink()
        elif kind=='symlink':
            original=p.read_bytes();p.unlink();other=tmp_path/'original';other.write_bytes(original);p.symlink_to(other)
        elif kind=='writable':p.chmod(0o666)
    with pytest.raises((ValueError,FileNotFoundError)):reader.call('read',args)


@pytest.mark.parametrize('operation,args',[
    ('write',{}),('execute',{}),('read',{'path':'/etc/passwd'}),
    ('list',{'cursor':True,'kind':'all'}),('list',{'cursor':-1,'kind':'all'}),
    ('search',{'cursor':0,'text':''}),('search',{'cursor':0,'text':'x'*129})])
def test_no_paths_execution_or_unbounded_requests(capture,operation,args):
    reader=capture[-1]
    with pytest.raises(ValueError):reader.call(operation,{'capture':reader.identity,**args})


def test_unicode_units_and_read_ranges(case,tmp_path):
    repo,store,folder,request=case
    text='Original Unicode: '+chr(0x03b1)*10000
    p=tmp_path/'unicode.txt';p.write_text(text)
    ref=changes.preserve(folder,p)
    changes.record(folder,'DISPOSITION',AGENT,{'rationale':'Literal Unicode evidence retained.','affected_results':[ref]})
    captured=access.capture_changes(store,[request['identity']],source=request['target']['source'],task_binding=TASK)
    d=access.write_capture(tmp_path/'cache',captured)
    r=access.Reader(tmp_path/'cache',d['manifest_sha256'],source=d['source'],task_binding=TASK,owner=os.getuid())
    row=next(x for x in r.records if x['kind']=='change_artifact')
    offset=0;parts=[]
    while True:
        reply=r.call('read',{'capture':r.identity,'name':row['name'],'sha256':row['sha256'],'offset':offset,'characters':5000})
        parts.append(reply['content'])
        assert reply['content_utf8_bytes']==len(reply['content'].encode())
        assert reply['content_sha256']==hashlib.sha256(reply['content'].encode()).hexdigest()
        offset=reply['next_offset_characters']
        if offset is None:break
    assert ''.join(parts)==text
    assert row['utf8_bytes']>row['characters']


def test_role_journals_are_independent_and_restart_does_not_reset_budget(capture,tmp_path,monkeypatch):
    r=capture[-1];monkeypatch.setattr(access,'MAX_CALLS',2)
    author=access.Session(r,tmp_path/'author',role='author',task_binding=TASK)
    reviewer=access.Session(r,tmp_path/'reviewer',role='reviewer',task_binding=TASK)
    query={'capture':r.identity,'cursor':0,'text':'REQUEST_CHANGES'}
    for session in [author,reviewer]:
        result=session.call('search',query)
        assert result['ok'] is True and result['result']['matches']
        raw=json.loads((session.root/'call-0001.json').read_bytes())
        assert raw['response']==result
        assert raw['returned_utf8_bytes']==len(access.tool_text(result).encode())
    author.call('search',query)
    again=access.Session(r,tmp_path/'author',role='author',task_binding=TASK)
    with pytest.raises(ValueError,match='BUDGET_EXHAUSTED'):again.call('search',query)
    assert reviewer.call('search',query)['ok'] is True


def test_budget_refusal_and_interrupted_request_preserve_evidence(capture,tmp_path,monkeypatch):
    r=capture[-1];monkeypatch.setattr(access,'MAX_RETURN_BYTES',500)
    session=access.Session(r,tmp_path/'journal',role='disposition',task_binding=TASK)
    result=session.call('list',{'capture':r.identity,'cursor':0,'kind':'all'})
    assert result['ok'] is False and result['error']=='SCIENTIFIC_EVIDENCE_RETURN_BUDGET_EXHAUSTED'
    assert (session.root/'call-0001.json').exists()
    (session.root/'pending.json').write_text('preserved uncertain fixture');(session.root/'pending.json').chmod(0o600)
    with pytest.raises(ValueError,match='INTERRUPTED_READ_RECONCILE'):
        session.call('list',{'capture':r.identity,'cursor':0,'kind':'all'})
    assert (session.root/'pending.json').read_text()=='preserved uncertain fixture'


def test_stdio_exposes_only_fixed_tools_and_records_actual_response(capture,tmp_path):
    r=capture[-1]
    requests=[
        {'jsonrpc':'2.0','id':1,'method':'initialize','params':{}},
        {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},
        {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'scientific_evidence_search',
            'arguments':{'capture':r.identity,'cursor':0,'text':'REQUEST_CHANGES'},
            '_meta':{'progressToken':3,'claudecode/toolUseId':'fixture-tool-call'}}},
        {'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'Bash','arguments':{'command':'id'}}}]
    args=[sys.executable,'-B','-m','orchestrator.scientific_evidence_access',
        '--directory',str(r.directory),'--manifest',r.identity,'--source',r.manifest['source'],
        '--task-binding',TASK,'--journal',str(tmp_path/'stdio'),'--role','reviewer','--owner',str(os.getuid()),'--reader-uid',str(os.getuid())]
    process=subprocess.run(args,input=''.join(access.tool_text(x)+'\n' for x in requests),
        text=True,capture_output=True,cwd=Path(__file__).parents[1])
    assert process.returncode==0,process.stderr
    replies=[json.loads(line) for line in process.stdout.splitlines()]
    assert {t['name'] for t in replies[1]['result']['tools']}=={
        'scientific_evidence_list','scientific_evidence_search','scientific_evidence_read'}
    delivered=replies[2]['result']['content'][0]['text']
    original=json.loads((tmp_path/'stdio/call-0001.json').read_bytes())
    assert delivered==access.tool_text(original['response'])
    assert replies[3]['id']==4 and 'error' in replies[3] and len(list((tmp_path/'stdio').glob('call-*.json')))==1


def test_hundred_cycle_growth_uses_pages_not_full_inline_index(case,tmp_path):
    repo,store,folder,request=case;descriptors=[];counts=[]
    for cycle in range(101):
        if cycle:
            changes.record(folder,'DISPOSITION',AGENT,{'rationale':('Fixture history cycle '+str(cycle)).ljust(1024,'x'),
                'affected_results':['NONAUTHORIZING_GROWTH_TEST']})
        if cycle not in (0,10,100):continue
        captured=access.capture_changes(store,[request['identity']],source=request['target']['source'],task_binding=TASK)
        d=access.write_capture(tmp_path/'cache',captured);descriptors.append(len(encoded(d)))
        r=access.Reader(tmp_path/'cache',d['manifest_sha256'],source=d['source'],task_binding=TASK,owner=os.getuid())
        cursor=0;found=[]
        while True:
            page=r.call('list',{'capture':r.identity,'cursor':cursor,'kind':'all'})
            assert len(page['records'])<=access.PAGE_RECORDS and len(encoded(page))<=access.REPLY_BYTES
            found+=page['records'];cursor=page['next_cursor']
            if cursor is None:break
        counts.append(len(found));assert len(found)==cycle+1
    assert max(descriptors)-min(descriptors)<=2
    assert counts==[1,11,101]
    # This is descriptor/backend growth, not yet actual composed-role fit.


def test_original_patch_bytes_remain_text_not_executable(case,tmp_path):
    _,store,folder,request=case
    path=tmp_path/'source.patch';raw=b'diff --git a/code.py b/code.py\\n- old\\n+ new\\n';path.write_bytes(raw)
    ref=changes.preserve(folder,path)
    changes.record(folder,'DISPOSITION',AGENT,{'rationale':'Original text patch, not execution.','affected_results':[ref]})
    value=access.capture_changes(store,[request['identity']],source=request['target']['source'],task_binding=TASK)
    row=next(x for x in value['manifest']['records'] if x['kind']=='change_artifact')
    assert row['provenance']['artifact'].endswith('.patch')
    assert value['payloads'][row['sha256']]==raw


def test_original_content_scanner_is_not_bypassed_by_text_cache(case,tmp_path):
    _,store,folder,request=case
    # Native preserve already refuses protected content; inject a scanner
    # sentinel into a canonical source fixture only to test delivery refusal.
    captured=access.capture_changes(store,[request['identity']],source=request['target']['source'],task_binding=TASK)
    row=captured['manifest']['records'][0]
    raw=('fixture '+ 'sub-' + 'stroke' + '123').encode()
    old_identity=row['sha256'];identity=hashlib.sha256(raw).hexdigest()
    row.update(sha256=identity,utf8_bytes=len(raw),characters=len(raw))
    captured['payloads'][identity]=raw
    if not any(x['sha256']==old_identity for x in captured['manifest']['records']):
        captured['payloads'].pop(old_identity)
    assert set(captured['payloads'])=={x['sha256'] for x in captured['manifest']['records']}
    with pytest.raises(ValueError,match='CASE_LEVEL_RECORD_REJECTED'):
        access.write_capture(tmp_path/'refused-cache',captured)
    assert not list((tmp_path/'refused-cache').rglob('*.txt'))


@pytest.mark.parametrize('mutation',['missing','changed'])
def test_paged_index_is_bound_not_an_unchecked_navigation_summary(capture,mutation):
    _,_,_,cache,d,r=capture
    page=r.manifest['pages'][0];path=cache/'indexes'/(page['sha256']+'.json')
    if mutation=='missing':path.unlink()
    else:path.write_text('[]')
    with pytest.raises((ValueError,FileNotFoundError)):
        access.Reader(cache,r.identity,source=d['source'],task_binding=TASK,owner=os.getuid())


def test_changed_journal_and_cross_role_reuse_are_not_fresh_budget(capture,tmp_path):
    r=capture[-1]
    session=access.Session(r,tmp_path/'journal',role='author',task_binding=TASK)
    session.call('list',{'capture':r.identity,'cursor':0,'kind':'all'})
    with pytest.raises(ValueError):
        access.Session(r,tmp_path/'journal',role='reviewer',task_binding=TASK)
    path=session.root/'call-0001.json';v=json.loads(path.read_bytes());v['returned_utf8_bytes']=0
    path.write_bytes(encoded(v))
    with pytest.raises(ValueError,match='JOURNAL_CHANGED'):
        session.call('list',{'capture':r.identity,'cursor':0,'kind':'all'})


def test_native_disposition_and_all_three_original_outputs_are_independently_discoverable(capture,monkeypatch):
    from orchestrator import disposition_successors as native
    from test_linked_disposition_reference import original
    store,folder,request,cache,descriptor,reader=capture
    value=original();reference=native.result_reference(value);calls=[]
    client=object();config={'source':descriptor['source']}
    def read(actual,identity,transport):
        assert actual is config and transport is client and identity==reference['origin_task']
        calls.append(identity)
        return deepcopy(value)
    monkeypatch.setattr(native,'read_result',read)
    base=access.capture_changes(store,[request['identity']],source=descriptor['source'],task_binding=TASK)
    before=encoded(base['manifest'])
    combined=access.capture_dispositions(base,config,[reference],original_client=client)
    result=access.write_capture(cache,combined)
    r=access.Reader(cache,result['manifest_sha256'],source=result['source'],task_binding=TASK,owner=os.getuid())
    rows=r.call('list',{'capture':r.identity,'cursor':0,'kind':'scientific_stage_output'})['records']
    assert {x['provenance']['role'] for x in rows}=={'author','reviewer','disposition'}
    for row in rows:
        body=value
        for key in row['provenance']['path_in_native_original']:body=body[key]
        response=r.call('read',{'capture':r.identity,'name':row['name'],'sha256':row['sha256'],
            'offset':0,'characters':8192})
        assert response['content']==body
    full=r.call('list',{'capture':r.identity,'cursor':0,'kind':'linked_disposition_original'})['records'][0]
    assert r._body(full).encode()==encoded(value)
    matches=r.call('search',{'capture':r.identity,'cursor':0,'text':'REQUEST_CHANGES'})['matches']
    assert any(m['record']['provenance'].get('role')=='reviewer' for m in matches)
    assert calls==[reference['origin_task']] and encoded(base['manifest'])==before


@pytest.mark.parametrize('damage',['missing','review-body','repair-chain','reference','source','duplicate'])
def test_native_result_failure_never_replaces_or_partly_extends_capture(capture,monkeypatch,damage):
    from orchestrator import disposition_successors as native
    from test_linked_disposition_reference import original
    store,folder,request,cache,descriptor,reader=capture
    value=original();reference=native.result_reference(value)
    base=access.capture_changes(store,[request['identity']],source=descriptor['source'],task_binding=TASK)
    before=deepcopy(base)
    config={'source':descriptor['source']}
    if damage=='review-body':value['originals']['protected_original']['stages']['review']['answer']='APPROVE'
    elif damage=='repair-chain':value['reviewed_repair']['events'][1]['previous_sha256']='f'*64
    elif damage=='reference':reference['result_sha256']='f'*64
    elif damage=='source':config['source']='f'*40
    def read(*args):
        if damage=='missing':raise ValueError('DISPOSITION_PROTECTED_ORIGINAL_CHANGED')
        return deepcopy(value)
    monkeypatch.setattr(native,'read_result',read)
    with pytest.raises(ValueError):
        access.capture_dispositions(base,config,[reference]* (2 if damage=='duplicate' else 1),original_client=None)
    assert base==before


def test_complete_result_storage_ceiling_is_preserved_without_truncating(capture,monkeypatch):
    from orchestrator import disposition_successors as native
    from test_linked_disposition_reference import original
    store,folder,request,cache,descriptor,reader=capture
    value=original()
    value['originals']['packet']['large_original']='x'*1500000
    value['result']['original_proof_sha256']=hashlib.sha256(encoded(value['originals'])).hexdigest()
    value['result_sha256']=hashlib.sha256(encoded(value['result'])).hexdigest()
    # The unchanged native scanner already imposes this same byte ceiling
    # before the backend export. It must refuse, never shorten an original.
    with pytest.raises(ValueError,match='PUBLICATION_CONTENT_REJECTED'):
        native.result_reference(value)
    assert len(value['originals']['packet']['large_original'])==1500000
    assert access.NATIVE_RESULT_BYTES==1500000


def test_task_scope_uses_exact_native_prefix_and_ignores_later_append(capture, monkeypatch):
    from orchestrator import disposition_context, reviewed_history
    store,folder,request,cache,descriptor,reader=capture
    original=changes.load(folder)
    packet={"fixture": "Validated saved task; native validator has separate full tests."}
    monkeypatch.setattr(disposition_context,"validate_current_history",
                        lambda value,source: {request["identity"]: original})
    first=access.capture_task_changes(store,packet,source=descriptor["source"])
    changes.record(folder,"DISPOSITION",AGENT,{"rationale":"Later append remains separate.",
                                             "affected_results":["fixture"]})
    second=access.capture_task_changes(store,packet,source=descriptor["source"])
    assert first==second
    assert first["manifest"]["request_heads"][request["identity"]]["head_sha256"]==original["head_sha256"]
    assert first["manifest"]["task_binding"]==access.sha(encoded(packet))


@pytest.mark.parametrize("field", ["head_sha256","index_sha256","event_count","scope"])
def test_saved_task_prefix_cannot_be_rebound_to_other_native_history(capture,field):
    from orchestrator import reviewed_history
    store,folder,request,cache,descriptor,reader=capture
    state=changes.load(folder)
    expected={request["identity"]:{"event_count":len(state["events"]),
              "head_sha256":state["head_sha256"],
              "index_sha256":reviewed_history.sha(reviewed_history.index(state))}}
    if field=="scope":expected={}
    elif field=="event_count":expected[request["identity"]][field]=len(state["events"])+1
    else:expected[request["identity"]][field]="f"*64
    with pytest.raises(ValueError,match="SCIENTIFIC_EVIDENCE_"):
        access.capture_changes(store,[request["identity"]],source=descriptor["source"],
                               task_binding=TASK,expected_prefixes=expected)


@pytest.mark.parametrize('fault', [None, 'wrong-owner', 'public-mode', 'symlink',
                                  'changed-event', 'changed-artifact', 'missing-event'])
def test_privileged_capture_keeps_original_integrity_and_writer_boundary(capture, monkeypatch, fault):
    # UID simulation here; the release check also exercises actual root/controller
    # accounts against the preserved broker packet without any model admission.
    store, folder, request, cache, descriptor, reader = capture
    owner = os.getuid()
    before = access.capture_changes(store, [request['identity']],
                                   source=descriptor['source'], task_binding=TASK)
    if fault == 'public-mode': (folder/'request.json').chmod(0o644)
    elif fault == 'symlink':
        original = folder/'preserved-request.json'
        (folder/'request.json').rename(original); (folder/'request.json').symlink_to(original)
    elif fault == 'changed-event':
        path = next((folder/'events').glob('0001-*'))
        value = json.loads(path.read_bytes()); value['payload']['rationale'] += ' changed'
        path.write_bytes(encoded(value))
    elif fault == 'changed-artifact': next((folder/'evidence').iterdir()).write_text('changed')
    elif fault == 'missing-event': next((folder/'events').glob('0001-*')).rename(folder/'preserved-event')
    monkeypatch.setattr(os, 'getuid', lambda: 0)
    expected_owner = owner + 1 if fault == 'wrong-owner' else owner
    if fault is not None:
        with pytest.raises((ValueError, FileNotFoundError)):
            access.capture_changes(store, [request['identity']], source=descriptor['source'],
                                   task_binding=TASK, owner=expected_owner)
        return
    with pytest.raises(ValueError, match='CHANGE_PRIVATE_FILE_REQUIRED'):
        changes.load(folder)  # Default reader/writer contract is unchanged.
    assert access.capture_changes(store, [request['identity']], source=descriptor['source'],
                                  task_binding=TASK, owner=owner) == before
    with pytest.raises(ValueError):
        changes.record(folder, 'DISPOSITION', AGENT, {'rationale':'Forbidden cross-owner write',
                                                     'affected_results':['fixture']})


@pytest.mark.parametrize('owner', [-1, True, '1000', 1.0, 999999])
def test_unprivileged_reader_cannot_choose_another_owner(case, owner):
    _, _, folder, _ = case
    with pytest.raises(ValueError, match='CHANGE_READ_OWNER_NOT_PERMITTED'):
        changes.load(folder, owner=owner)


@pytest.mark.parametrize('extra',[
    {'_meta':None}, {'_meta':[]}, {'_meta':'progress'},
    {'path':'/etc/passwd'}, {'task':{'ttl':1000}},
    {'_meta':{},'execute':'id'}])
def test_mcp_metadata_does_not_expand_request_schema(capture,tmp_path,extra):
    r=capture[-1];session=access.Session(r,tmp_path/'journal',role='reviewer',task_binding=TASK)
    params={'name':'scientific_evidence_list',
        'arguments':{'capture':r.identity,'cursor':0,'kind':'all'},**extra}
    with pytest.raises(ValueError,match='TOOL_REFUSED'):
        access.rpc(session,{'jsonrpc':'2.0','id':1,'method':'tools/call','params':params})
    assert not list(session.root.glob('call-*.json'))


def test_metadata_cannot_replace_capture_or_arguments(capture,tmp_path):
    r=capture[-1];session=access.Session(r,tmp_path/'journal',role='reviewer',task_binding=TASK)
    args={'capture':'f'*64,'cursor':0,'kind':'all'}
    reply=access.rpc(session,{'jsonrpc':'2.0','id':1,'method':'tools/call','params':{
        'name':'scientific_evidence_list','arguments':args,
        '_meta':{'capture':r.identity,'arguments':{'capture':r.identity},'authority':'APPROVE'}}})
    response=json.loads(reply['result']['content'][0]['text'])
    assert reply['result']['isError'] and response['ok'] is False
    original=json.loads((session.root/'call-0001.json').read_bytes())
    assert original['request']=={'operation':'list','arguments':args}
    assert original['response']==response


def test_client_envelope_metadata_retains_delivery_binding(capture,tmp_path):
    from orchestrator import scientific_evidence_runtime as runtime
    r=capture[-1];session=access.Session(r,tmp_path/'journal',role='reviewer',task_binding=TASK)
    args={'capture':r.identity,'cursor':0,'text':'REQUEST_CHANGES'}
    name='scientific_evidence_search';tool_id='fixture-client-tool'
    reply=access.rpc(session,{'jsonrpc':'2.0','id':7,'method':'tools/call','params':{
        'name':name,'arguments':args,'_meta':{'progressToken':7,'claudecode/toolUseId':tool_id}}})
    content=reply['result']['content']
    events=[{'type':'assistant','message':{'content':[{'type':'tool_use','id':tool_id,
        'name':'mcp__scientific_evidence__'+name,'input':args}]}},
        {'type':'user','message':{'content':[{'type':'tool_result','tool_use_id':tool_id,
            'content':content,'is_error':reply['result']['isError']}]}}]
    profile={'descriptor':capture[-2],'role':'reviewer','uid':os.getuid(),'journal':str(session.root)}
    receipt=runtime.verify(profile,events,'claude')
    assert receipt['successful_calls']==1 and receipt['refused_calls']==0
    assert receipt['actual_tool_matches']==[{'tool_id':tool_id,'journal_number':1}]
    events[-1]['message']['content'][0]['content'][0]['text']='changed original'
    with pytest.raises(ValueError):runtime.verify(profile,events,'claude')
