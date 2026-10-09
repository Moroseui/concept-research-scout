"""Remove only this run's verified remote input copies, never local originals.

Normal cleanup follows durable collection. Expiry cleanup is a separate bounded
server housekeeping action; it never submits work or changes a scientific result.
The named empty volumes and every receipt remain available for reconciliation.
"""
from datetime import datetime,timezone
from pathlib import Path
import json
from orchestrator import private_records,connectivity
from orchestrator.manual_executor import read,digest,inventory
from orchestrator.manual_driver import write_once
from orchestrator.modal_executor import canonical
from orchestrator.modal_assets import local_files
from orchestrator.modal_provider import ModalProvider,member_map
from orchestrator.remote_supervisor import lock

VOLUME_KEYS={'data':'data_volume_id','wheels':'wheel_volume_id','package':'package_volume_id'}


def expired(runtime,now=None):
    return (now or datetime.now(timezone.utc))>=datetime.fromisoformat(runtime['asset_expires_utc'])


def remove_members(provider,volume_id,files,record,kind):
    """Exact members only; callers retain their admission/dependency guards."""
    record=Path(record)
    volume=provider._volume(volume_id)
    entries=volume.listdir('/',recursive=True)
    if any(x.type.name not in {'FILE','DIRECTORY'} for x in entries):raise ValueError('MODAL_CLEANUP_MEMBER_TYPE')
    remaining={x.path.lstrip('/'):{'bytes':x.size,'sha256':files[x.path.lstrip('/')]['sha256']} for x in entries if x.type.name=='FILE' and x.path.lstrip('/') in files}
    if len(remaining)!=sum(x.type.name=='FILE' for x in entries):raise ValueError('MODAL_CLEANUP_UNEXPECTED_MEMBER')
    provider._verify_volume(volume_id,remaining)
    for name,item in files.items():
        ident=digest(canonical({'kind':kind,'name':name,'identity':item}))
        path=record/(ident+'.intent.json')
        payload={'volume_id':volume_id,'name':name,**item}
        if name not in remaining:
            if not path.exists() or read(path)!=payload:raise ValueError('MODAL_CLEANUP_UNEXPLAINED_ABSENCE')
            continue
        write_once(path,canonical(payload))
        # Bound object ID, exact authorized file; no recursive deletion.
        volume.remove_file('/'+name,recursive=False)
    provider._verify_volume(volume_id,{})


@private_records.private_umask
def clear_copies(provider,runtime,record,*,collected=False,now=None):
    record=Path(record)
    if not collected and not expired(runtime,now):return {'status':'NOT_DUE'}
    private_records.mkdir(record,parents=True,exist_ok=True)
    lock_path=record/'cleanup.lock'
    if lock_path.exists():private_records.check(lock_path)
    with lock(lock_path):
        private_records.check(lock_path)
        pin=digest(canonical(runtime))
        if (record/'COMPLETE.json').exists():
            done=read(record/'COMPLETE.json')
            if done.get('runtime_sha256')!=pin:raise ValueError('MODAL_CLEANUP_BINDING')
            return done
        # Originals must still exist with their exact hashes before any deletion.
        expected={'data':runtime['data_files'],'wheels':runtime['wheel_files']}
        package=Path(runtime['local_assets']['package'])
        if package.exists():
            expected['package']={n:{'sha256':h,'bytes':(package/n).stat().st_size} for n,h in inventory(package).items()}
            if 'manifest.json' not in expected['package']:raise ValueError('MODAL_CLEANUP_PACKAGE_ORIGINAL')
        else:expected['package']={}
        for kind,files in expected.items():
            if files:
                member_map(files,maximum=2*1024**3 if kind=='data' else 256*1024**2)
                local_files(runtime['local_assets'][kind],files)
        connectivity.require(['modal'],record/'connectivity.json')
        intent={'runtime_sha256':pin,'reason':'DURABLE_COLLECTION' if collected else 'ASSET_RETENTION_EXPIRED',
                'files':expected,'volumes':{kind:runtime[VOLUME_KEYS[kind]] for kind in expected}}
        intent_path=record/'intent.json'
        if intent_path.exists():
            prior=read(intent_path)
            if any(prior[k]!=intent[k] for k in ['runtime_sha256','files','volumes']):raise ValueError('MODAL_CLEANUP_INTENT_CHANGED')
        else:
            # All remote inputs must match before the first removal.
            for kind,files in expected.items():provider._verify_volume(runtime[VOLUME_KEYS[kind]],files)
            write_once(intent_path,canonical(intent))
        for kind,files in expected.items():
            remove_members(provider,runtime[VOLUME_KEYS[kind]],files,record,kind)
        done={'status':'CLEARED','runtime_sha256':pin,'originals_preserved':True,'named_volumes_retained_empty':True}
        write_once(record/'COMPLETE.json',canonical(done));return done


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--runtime',required=True);parser.add_argument('--record',required=True)
    args=parser.parse_args();runtime=read(args.runtime)
    if not expired(runtime):result={'status':'NOT_DUE'}
    else:result=clear_copies(ModalProvider(runtime),runtime,args.record)
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
