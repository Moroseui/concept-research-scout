"""Durable fit returns using the same private Volume objects as checkpoints.

No scientific calculation, admission, asset creation or retry is performed.
Only declared small return files are collected; model weights and predictions
remain on their existing private volume unless explicitly in the bound outputs.
"""
import hashlib
import json
from pathlib import Path
from orchestrator import private_records
from orchestrator.modal_executor import canonical
from orchestrator.modal_fit_progress import encoded, file_hash
from orchestrator.modal_fit_provider import progress_scope, progress_volume, _file, MAX_RECORD
from orchestrator.modal_provider import member_map, MAX_FILE


from orchestrator.modal_fit_publication import _key, _result_key, _result, publish


def _object(volume, root, key, fit_sha256, maximum):
    pointer = _file(volume,root+'/'+key+'.json',MAX_RECORD,collect=True)
    record = json.loads(pointer['data'])
    import re
    if (not isinstance(record,dict) or set(record) != {'schema','key','binding_sha256','object','sha256','bytes','metadata','at_utc'} or
            record['schema']!='modal-fit-object/v1' or record['key']!=key or record['binding_sha256']!=fit_sha256 or
            not isinstance(record['object'],str) or not re.fullmatch('[0-9a-f]{32}',record['object'])):
        raise ValueError('MODAL_FIT_RESULT_OBJECT_BINDING')
    base=root+'/objects/'+record['object']
    original=_file(volume,base+'/record.json',MAX_RECORD,collect=True)
    if json.loads(original['data']) != record:
        raise ValueError('MODAL_FIT_RECORD_CHANGED')
    data=_file(volume,base+'/data',maximum,collect=True)
    if any(record[k]!=data[k] for k in ('sha256','bytes')):
        raise ValueError('MODAL_FIT_OUTPUT_CHANGED')
    if _file(volume,root+'/'+key+'.json',MAX_RECORD,collect=True)['data']!=pointer['data']:
        raise ValueError('MODAL_FIT_OBSERVATION_CHANGED')
    return data['data'], record


def observe(provider, provider_id, binding):
    scope=progress_scope(binding)
    sandbox=provider._sandbox(provider_id)
    if sandbox.object_id!=provider_id:raise ValueError('MODAL_FIT_SANDBOX_ID_CHANGED')
    volume=progress_volume(provider,scope);root='/fits/'+scope['fit_id']
    from orchestrator.modal_item4_provider import input_proof
    proof=input_proof(provider,binding,volume)
    if proof and proof['status']=='FAILED':
        return {'schema':'modal-result/v1','binding_sha256':proof['binding_sha256'],
                'status':'FAILED','files':{}},sandbox,volume,root
    names={entry.path.lstrip('/') for entry in volume.listdir(root,recursive=False)}
    if (root+'/'+_result_key(binding)+'.json').lstrip('/') not in names:
        return None, sandbox, volume, root
    if proof is None or proof['status']!='VERIFIED':raise ValueError('ITEM4_INPUT_VERIFICATION_REQUIRED')
    identity=_file(volume,root+'/identity.json',MAX_RECORD,collect=True)
    if json.loads(identity['data'])!={'schema':'modal-fit/v1','binding':scope['fit_binding']}:
        raise ValueError('MODAL_FIT_IDENTITY_CHANGED')
    fit_sha=hashlib.sha256(encoded(scope['fit_binding'])).hexdigest()
    raw,record=_object(volume,root,_result_key(binding),fit_sha,MAX_RECORD)
    result=_result(json.loads(raw),binding)
    if record['metadata']!={'binding_sha256':result['binding_sha256']}:
        raise ValueError('MODAL_RESULT_BINDING')
    return result,sandbox,volume,root


def status(provider, provider_id, binding):
    result,sandbox,_,_=observe(provider,provider_id,binding)
    state=result['status'] if result else ('RUNNING' if sandbox.poll() is None else 'UNKNOWN')
    return {'provider_id':provider_id,'binding_sha256':hashlib.sha256(canonical(binding)).hexdigest(),'status':state}


@private_records.private_umask
def collect(provider, provider_id, binding, destination):
    result,_,volume,root=observe(provider,provider_id,binding)
    if result is None or result['status']!='COMPLETE':raise ValueError('MODAL_RESULT_NOT_COMPLETE')
    fit_sha=hashlib.sha256(encoded(progress_scope(binding)['fit_binding'])).hexdigest()
    for name,item in result['files'].items():
        raw,record=_object(volume,root,_key(name),fit_sha,MAX_FILE)
        if record['metadata']!={'path':name} or any(record[k]!=item[k] for k in ('sha256','bytes')):
            raise ValueError('MODAL_FIT_OUTPUT_CHANGED')
        target=Path(destination)/name
        private_records.mkdir(target.parent,parents=True,exist_ok=True)
        private_records.write_bytes(target,raw)
    if observe(provider,provider_id,binding)[0]!=result:
        raise ValueError('MODAL_RESULT_CHANGED_DURING_COLLECTION')
    from orchestrator.modal_item4_provider import input_proof
    proof=input_proof(provider,binding,volume)
    if proof is None or proof['status']!='VERIFIED':raise ValueError('ITEM4_INPUT_VERIFICATION_REQUIRED')
    return {'provider_id':provider_id,'binding_sha256':result['binding_sha256'],
            'input_verification':proof,
            'file_sha256':{name:item['sha256'] for name,item in result['files'].items()}}
