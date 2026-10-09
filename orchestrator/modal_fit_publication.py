"""Durable worker publication, shared with the existing controller result path.

The original validation and publication code is factored here so the confined
worker does not import controller, client, billing or credential modules.
"""
import hashlib
import json
from pathlib import Path
from orchestrator import private_records
from orchestrator.modal_fit_progress import encoded, file_hash
from orchestrator.modal_fit_contract import progress_scope
from orchestrator.modal_files import member_map


def canonical(value):return json.dumps(value,sort_keys=True).encode()


def _key(name):
    return 'output-' + hashlib.sha256(name.encode()).hexdigest()


def _result_key(binding):
    return 'result-' + hashlib.sha256(canonical(binding)).hexdigest()


def _result(value, binding):
    if (not isinstance(value, dict) or set(value) != {'schema','binding_sha256','status','files'} or
            value['schema'] != 'modal-result/v1' or
            value['binding_sha256'] != hashlib.sha256(canonical(binding)).hexdigest()):
        raise ValueError('MODAL_RESULT_BINDING')
    if value['status'] not in {'COMPLETE','FAILED'}:
        raise ValueError('MODAL_RESULT_STATE')
    if value['status'] == 'COMPLETE':
        member_map(value['files'])
        if set(value['files']) != set(binding['outputs']):
            raise ValueError('MODAL_RESULT_EXPECTED_MEMBERS')
    elif value['files']:
        raise ValueError('MODAL_FAILED_RESULT_FILES')
    return value


def publish(progress, binding, outputs, *, status='COMPLETE'):
    """Called once by the reviewed worker after its bound execution finishes.

    Each output is committed independently. Interrupted publication can reuse
    identical objects; it cannot relabel altered bytes as the previous result.
    The final result pointer is published last, with the full segment binding.
    """
    progress._guard()
    scope = progress_scope(binding)
    if scope['fit_id'] != progress.root.name or scope['fit_binding'] != progress.binding:
        raise ValueError('MODAL_FIT_RESULT_SCOPE')
    if (progress.root/(_result_key(binding)+'.json')).exists():
        raise ValueError('MODAL_FIT_RESULT_ALREADY_PUBLISHED')
    files = {}
    if status == 'COMPLETE':
        outputs = Path(outputs)
        private_records.check_tree(outputs)
        found = {str(p.relative_to(outputs)) for p in outputs.rglob('*') if p.is_file()}
        if found != set(binding['outputs']):
            raise ValueError('MODAL_RESULT_EXPECTED_MEMBERS')
        files = {name:{'sha256':file_hash(outputs/name),'bytes':(outputs/name).stat().st_size}
                 for name in sorted(found)}
        member_map(files)
        # Do not turn an interrupted fit into a completed fit based on tables.
        _,final = progress.select('final')
        meta = final['metadata']
        if (not isinstance(meta,dict) or set(meta)!={'next_epoch','total_epochs','native_version'} or
                type(meta['total_epochs']) is not int or type(meta['next_epoch']) is not int or
                meta['total_epochs']<1 or meta['next_epoch']!=meta['total_epochs'] or meta['native_version']!='2.8.1'):
            raise ValueError('MODAL_FIT_FINAL_NOT_COMPLETE')
    result = _result({'schema':'modal-result/v1','binding_sha256':hashlib.sha256(canonical(binding)).hexdigest(),
                      'status':status,'files':files},binding)
    for name,item in files.items():
        key = _key(name)
        if (progress.root/(key+'.json')).exists():
            _,record = progress.select(key)
            if record['metadata'] != {'path':name} or any(record[k] != item[k] for k in ('sha256','bytes')):
                raise ValueError('MODAL_FIT_OUTPUT_CHANGED')
        else:
            def copy(target):
                with (outputs/name).open('rb') as src, target.open('wb') as dst:
                    for chunk in iter(lambda:src.read(1024*1024),b''):dst.write(chunk)
            record = progress.publish(key,copy,metadata={'path':name})
            if any(record[k] != item[k] for k in ('sha256','bytes')):
                raise ValueError('MODAL_FIT_OUTPUT_CHANGED')
    progress.publish(_result_key(binding),lambda path:path.write_bytes(encoded(result)),
                     metadata={'binding_sha256':result['binding_sha256']})
    return result


