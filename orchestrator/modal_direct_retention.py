"""Expire only successful direct-download input copies, retaining all evidence.

No original data, result, model, partial failure, checkpoint or receipt is
removed. A per-file intent makes an interrupted cleanup resumable without
rewriting history. No paid container is created for cleanup.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
from orchestrator import private_records,modal_download_package as package
from orchestrator.modal_download_provider import observe
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import read,digest
from orchestrator.manual_driver import write_once


@private_records.private_umask
def expire(provider,accounts,binding,prepared,state,*,now=None):
    now=now or datetime.now(timezone.utc);state=Path(state)
    if now<datetime.fromisoformat(binding['asset_expires_utc']):return {'status':'NOT_DUE'}
    ident=digest(canonical(binding));row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
    if row is None:return {'status':'EXPIRED_BEFORE_RESERVATION','no_automatic_retry':True}
    if row['binding']!=canonical(binding).decode():raise ValueError('DIRECT_RETENTION_LEDGER_BINDING')
    if row['status']!='READY':return {'status':'EXPIRY_BLOCKED_INCOMPLETE_ATTEMPT','preserved':True,'no_automatic_retry':True}
    pending=accounts.db.execute("SELECT count(*) FROM autonomy_compute WHERE status NOT IN ('COLLECTED','ACCOUNTED')").fetchone()[0]
    if pending:return {'status':'EXPIRY_WAIT_ACTIVE_COMPUTE','preserved':True}
    manifest=package.verify(prepared,binding['package_manifest_sha256']);handle=read(state/'provider/sandbox.json')
    if handle['binding_sha256']!=ident:raise ValueError('DIRECT_RETENTION_HANDLE_BINDING')
    if provider._sandbox(handle['provider_id']).poll() is None:return {'status':'EXPIRY_WAIT_ACTIVE_DOWNLOAD','preserved':True}
    folder=state/'retention';private_records.mkdir(folder,exist_ok=True)
    done=folder/'COMPLETE.json'
    if done.exists():
        value=read(done)
        if value['binding_sha256']!=ident:raise ValueError('DIRECT_RETENTION_COMPLETION_BINDING')
        return value
    files={}
    for kind,ref in manifest['plans'].items():
        plan=read(Path(prepared)/ref['path'])
        for name,item in plan['files'].items():files[kind+'/'+name]={'bytes':item['bytes'],'sha256':item['sha256']}
    intent=folder/'intent.json'
    volume=provider._volume(handle['data_volume_id'])
    payload={'binding_sha256':ident,'data_volume_id':handle['data_volume_id'],'files':files,
             'scope':'Only successful verified source copies; all download evidence retained'}
    if not intent.exists():
        # Recheck the actual terminal worker proof and exact remote member set.
        # Verification of all image bytes occurred inside the confined worker;
        # the controller retrieves metadata only, never image payload.
        proof=observe(provider,binding,prepared,handle)
        saved=read(state/'VERIFIED.json')
        if proof['status']!='VERIFIED' or any(saved[k]!=v for k,v in proof.items()):
            raise ValueError('DIRECT_RETENTION_VERIFICATION_CHANGED')
        if json.loads(row['receipt'])!=saved:raise ValueError('DIRECT_RETENTION_ACCEPTANCE_CHANGED')
        metadata={}
        count=0
        for entry in volume.listdir('/',recursive=True):
            name=entry.path.lstrip('/')
            if entry.type.name!='FILE' or name in files:continue
            raw=bytearray()
            for block in volume.read_file('/'+name):
                raw.extend(block);count+=len(block)
                if count>4*1024**2:raise ValueError('DIRECT_RETENTION_METADATA_BOUND')
            metadata[name]={'bytes':len(raw),'sha256':digest(raw)}
        write_once(folder/'metadata.json',canonical(metadata))
        write_once(folder/'verified-before-removal.json',canonical(proof))
        write_once(intent,canonical(payload))
    elif read(intent)!=payload:raise ValueError('DIRECT_RETENTION_INTENT_CHANGED')
    volume=provider._volume(handle['data_volume_id'])
    entries=volume.listdir('/',recursive=True)
    metadata=read(folder/'metadata.json')
    current_meta={}
    count=0
    for entry in entries:
        name=entry.path.lstrip('/')
        if entry.type.name!='FILE' or name in files:continue
        if name not in metadata:raise ValueError('DIRECT_RETENTION_UNEXPECTED_METADATA')
        raw=bytearray()
        for block in volume.read_file('/'+name):
            raw.extend(block);count+=len(block)
            if count>4*1024**2:raise ValueError('DIRECT_RETENTION_METADATA_BOUND')
        current_meta[name]={'bytes':len(raw),'sha256':digest(raw)}
    if current_meta!=metadata:raise ValueError('DIRECT_RETENTION_METADATA_CHANGED')
    actual={x.path.lstrip('/'):x.size for x in entries if x.type.name=='FILE'}
    if any(x.type.name not in ('FILE','DIRECTORY') for x in entries):raise ValueError('DIRECT_RETENTION_MEMBER_TYPE')
    for name,item in files.items():
        pin=digest(canonical({'path':name,**item}));path=folder/(pin+'.json')
        per_file={'volume_id':handle['data_volume_id'],'path':name,**item}
        if name not in actual:
            if not path.exists() or read(path)!=per_file:raise ValueError('DIRECT_RETENTION_UNEXPLAINED_ABSENCE')
            continue
        if actual[name]!=item['bytes']:raise ValueError('DIRECT_RETENTION_CHANGED_SIZE')
        write_once(path,canonical(per_file))
        volume.remove_file('/'+name,recursive=False)
    remaining={x.path.lstrip('/') for x in volume.listdir('/',recursive=True) if x.type.name=='FILE'}
    if remaining & set(files):raise ValueError('DIRECT_RETENTION_NOT_REMOVED')
    if remaining!=set(actual)-set(files):raise ValueError('DIRECT_RETENTION_EVIDENCE_CHANGED')
    result={'status':'INPUT_COPIES_EXPIRED','binding_sha256':ident,'removed_files':len(files),
            'originals_and_evidence_preserved':True,'no_refund_or_allowance_reset':True}
    write_once(done,canonical(result));return result
