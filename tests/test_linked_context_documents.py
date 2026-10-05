"""Candidate document views preserve criticism and bind actual reader originals."""
from copy import deepcopy
import hashlib
import json
import os
import pytest
from orchestrator import linked_disposition_input as linked, scientific_evidence_access as access
from orchestrator import disposition_successors as native, disposition_context as dc
from orchestrator.hosted_cycle import encoded
from test_scientific_evidence_access import capture
from test_change_requests import case


def science():
    return {'limitations': ['No final evaluation; do not infer performance.'],
        'reviewed_scientific_context': {'context': {'entries': [{
            'id': 'original-entry', 'dependencies': ['pending original split'],
            'consideration': {'status': 'DEFER', 'criticism': 'Unresolved concern.'},
            'evidence': {
                'interpretation': {'source': 'historical.md', 'sha256': 'a'*64,
                    'text': 'Original claim and limitation. '*100},
                'next_decision': {'text': 'Original result card. '*100},
                'review': {'verdict': 'REQUEST_CHANGES', 'text': 'Original criticism. '*100},
                'unknown_document': {'text': 'Unknown material must remain. '*100}}}]}}}


def test_view_references_only_fixed_document_bodies_and_keeps_all_other_fields():
    original=science();before=deepcopy(original)
    view=linked.context_document_presentation(original,'b'*64)
    entry=view['reviewed_scientific_context']['context']['entries'][0]
    old=original['reviewed_scientific_context']['context']['entries'][0]
    assert original==before and view['limitations']==original['limitations']
    for key in ['id','dependencies','consideration']:assert entry[key]==old[key]
    for key in ['review','unknown_document']:assert entry['evidence'][key]==old['evidence'][key]
    for key in ['interpretation','next_decision']:
        ref=entry['evidence'][key]['text'];raw=old['evidence'][key]['text'].encode()
        assert ref['sha256']==hashlib.sha256(raw).hexdigest()
        assert ref['utf8_bytes']==len(raw) and ref['reader_name'].endswith(key+'.original.txt')
    assert entry['evidence']['interpretation']['source']==old['evidence']['interpretation']['source']


@pytest.mark.parametrize('value',[None,[],{}, {'reviewed_scientific_context': []},
    {'reviewed_scientific_context':{'context':{'entries':{}}}}])
def test_unknown_layout_is_not_hidden_or_assumed_settled(value):
    assert linked.context_document_presentation(value,'b'*64)==value


def test_same_native_capture_supplies_documents_to_independent_role_readers(capture,monkeypatch,tmp_path):
    from test_linked_disposition_reference import original
    store,folder,request,cache,descriptor,_=capture
    value=original();proof=value['originals'];proof['packet']={'reviewer_evidence':science()}
    monkeypatch.setattr(dc,'charter_path',lambda proof:('packet','reviewer_evidence'))
    # Native-reference fixture binds the amended proof; it is not scientific evidence.
    value['result']['original_proof_sha256']=hashlib.sha256(encoded(proof)).hexdigest()
    value['result_sha256']=hashlib.sha256(encoded(value['result'])).hexdigest()
    ref=native.result_reference(value);calls=[]
    def read(config,reference,client):
        assert reference==ref;calls.append(reference);return deepcopy(value)
    monkeypatch.setattr(native,'read_result_reference',read)
    base=access.capture_changes(store,[request['identity']],source=descriptor['source'],task_binding='b'*64)
    captured=access.capture_dispositions(base,{'source':descriptor['source']},[ref],original_client=object())
    assert len(calls)==1  # One immutable native capture; not a later invented read.
    saved=access.write_capture(cache,captured)
    reader=access.Reader(cache,saved['manifest_sha256'],source=saved['source'],task_binding='b'*64,owner=os.getuid())
    rows=[r for r in reader.records if '/context/' in r['name']]
    assert len(rows)==2
    for role in ['author','reviewer','disposition']:
        session=access.Session(reader,tmp_path/role,role=role,task_binding='b'*64)
        for row in rows:
            result=session.call('read',{'capture':reader.identity,'name':row['name'],
                'sha256':row['sha256'],'offset':0,'characters':access.READ_CHARACTERS})
            text=value
            for part in row['provenance']['path_in_native_original']:text=text[part]
            assert result['ok'] and result['result']['content']==text
        assert len(list((tmp_path/role).glob('call-*.json')))==2
    row=rows[0]
    with pytest.raises(ValueError):reader.call('read',{'capture':reader.identity,
        'name':row['name'],'sha256':'0'*64,'offset':0,'characters':1000})


@pytest.mark.parametrize('fault',['missing_body','changed_body','changed_view'])
def test_document_failure_does_not_silently_substitute_evidence(capture,monkeypatch,tmp_path,fault):
    from test_linked_disposition_reference import original
    store,folder,request,cache,descriptor,_=capture
    value=original();value['originals']['packet']={'reviewer_evidence':science()}
    monkeypatch.setattr(dc,'charter_path',lambda proof:('packet','reviewer_evidence'))
    value['result']['original_proof_sha256']=hashlib.sha256(encoded(value['originals'])).hexdigest()
    value['result_sha256']=hashlib.sha256(encoded(value['result'])).hexdigest()
    ref=native.result_reference(value)
    monkeypatch.setattr(native,'read_result_reference',lambda *args:deepcopy(value))
    base=access.capture_changes(store,[request['identity']],source=descriptor['source'],task_binding='b'*64)
    captured=access.capture_dispositions(base,{'source':descriptor['source']},[ref],original_client=object())
    saved=access.write_capture(cache,captured)
    reader=access.Reader(cache,saved['manifest_sha256'],source=saved['source'],task_binding='b'*64,owner=os.getuid())
    row=next(r for r in reader.records if '/context/' in r['name'])
    if fault=='changed_view':
        with pytest.raises(ValueError):
            reader.call('read',{'capture':reader.identity,'name':row['name']+'-changed',
                               'sha256':row['sha256'],'offset':0,'characters':1000})
    else:
        target=cache/'objects'/(row['sha256']+'.txt')
        if fault=='missing_body':target.unlink()
        else:
            target.chmod(0o600)
            target.write_bytes(b'Changed original')
            target.chmod(0o400)
        with pytest.raises((ValueError,FileNotFoundError)):
            reader.call('read',{'capture':reader.identity,'name':row['name'],
                               'sha256':row['sha256'],'offset':0,'characters':1000})
