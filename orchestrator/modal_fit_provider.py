"""Read-only, authenticated per-fit checkpoint observation from Modal.

A positive terminal Sandbox observation plus a committed hash-checked checkpoint
can support continuation. A missing object, a timeout or missing checkpoint does
not. This module does not infer the cause of termination or launch any process.
"""
from datetime import datetime, timezone
import hashlib
import json
import re
from orchestrator.modal_fit_progress import encoded, identifier, validate_binding
from orchestrator.modal_executor import canonical

MAX_RECORD = 1024 * 1024
MAX_CHECKPOINT = 8 * 1024**3


from orchestrator.modal_fit_contract import progress_scope


def progress_volume(provider, scope):
    # The pinned SDK compares version against provider metadata when from_name
    # supplies it. This lookup cannot create or mutate a volume.
    volume = provider.modal.Volume.from_name(scope['volume_name'],version=2,create_if_missing=False,client=provider.client)
    volume.hydrate(client=provider.client)
    if volume.object_id != scope['volume_id']:
        raise ValueError('MODAL_FIT_VOLUME_ID_CHANGED')
    return volume


def _file(volume, path, maximum, *, collect):
    rows = volume.listdir(path,recursive=False)
    if len(rows)!=1 or rows[0].path.lstrip('/') != path.lstrip('/') or rows[0].type.name!='FILE':
        raise ValueError('MODAL_FIT_FILE_TYPE')
    size=rows[0].size
    if type(size) is not int or not 0<size<=maximum:raise ValueError('MODAL_FIT_FILE_SIZE')
    hashed=hashlib.sha256();parts=[];count=0
    for chunk in volume.read_file(path):
        count+=len(chunk)
        if count>size:raise ValueError('MODAL_FIT_FILE_CHANGED')
        hashed.update(chunk)
        if collect:parts.append(chunk)
    if count!=size:raise ValueError('MODAL_FIT_FILE_CHANGED')
    return {'sha256':hashed.hexdigest(),'bytes':count,'data':b''.join(parts) if collect else None}


def terminal_checkpoint(provider, provider_id, binding):
    scope=progress_scope(binding)
    sandbox=provider._sandbox(provider_id)
    if sandbox.object_id!=provider_id:raise ValueError('MODAL_FIT_SANDBOX_ID_CHANGED')
    code=sandbox.poll()
    if type(code) is not int:raise ValueError('MODAL_FIT_NOT_PROVEN_TERMINAL')
    volume=progress_volume(provider,scope);root='/fits/'+scope['fit_id']
    identity=_file(volume,root+'/identity.json',MAX_RECORD,collect=True)
    if json.loads(identity['data'])!={'schema':'modal-fit/v1','binding':scope['fit_binding']}:
        raise ValueError('MODAL_FIT_IDENTITY_CHANGED')
    entries=volume.listdir(root,recursive=False)
    names={e.path.lstrip('/') for e in entries if e.type.name=='FILE'}
    key='final' if (root+'/final.json').lstrip('/') in names else 'latest'
    pointer=_file(volume,root+'/'+key+'.json',MAX_RECORD,collect=True)
    record=json.loads(pointer['data'])
    if not isinstance(record,dict) or set(record)!={'schema','key','binding_sha256','object','sha256','bytes','metadata','at_utc'}:
        raise ValueError('MODAL_FIT_RECORD_SCHEMA')
    if (record['schema']!='modal-fit-object/v1' or record['key']!=key or
            record['binding_sha256']!=hashlib.sha256(encoded(scope['fit_binding'])).hexdigest() or
            not isinstance(record['object'],str) or not re.fullmatch('[0-9a-f]{32}',record['object'])):
        raise ValueError('MODAL_FIT_RECORD_BINDING')
    object_root=root+'/objects/'+record['object']
    original=_file(volume,object_root+'/record.json',MAX_RECORD,collect=True)
    if json.loads(original['data'])!=record:raise ValueError('MODAL_FIT_RECORD_CHANGED')
    data=_file(volume,object_root+'/data',MAX_CHECKPOINT,collect=False)
    if data['sha256']!=record['sha256'] or data['bytes']!=record['bytes']:
        raise ValueError('MODAL_FIT_CHECKPOINT_CHANGED')
    meta=record['metadata']
    if (not isinstance(meta,dict) or set(meta)!={'next_epoch','total_epochs','native_version'} or
            any(type(meta[k]) is not int for k in ('next_epoch','total_epochs')) or
            not 0<=meta['next_epoch']<=meta['total_epochs'] or meta['total_epochs']<1 or
            meta['native_version']!='2.8.1' or (key=='final' and meta['next_epoch']!=meta['total_epochs'])):
        raise ValueError('MODAL_FIT_CHECKPOINT_METADATA')
    # Detect observation drift; never conceal a changed pointer or process state.
    if (_file(volume,root+'/'+key+'.json',MAX_RECORD,collect=True)['data']!=pointer['data'] or sandbox.poll()!=code):
        raise ValueError('MODAL_FIT_OBSERVATION_CHANGED')
    return {'schema':'modal-fit-terminal-proof/v1','provider_id':provider_id,
            'binding_sha256':hashlib.sha256(canonical(binding)).hexdigest(),'terminal_exit_code':code,
            'volume_id':volume.object_id,'volume_version':2,'fit_id':scope['fit_id'],
            'fit_binding_sha256':record['binding_sha256'],'identity_sha256':identity['sha256'],
            'checkpoint_record':record,'checkpoint_record_sha256':original['sha256'],
            'mode':'validation-only' if key=='final' else 'resume',
            'observed_at':datetime.now(timezone.utc).isoformat(),
            'termination_cause':'not inferred from exit code','may_launch':False}
