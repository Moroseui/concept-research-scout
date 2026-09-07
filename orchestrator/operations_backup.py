"""Consistent private application sample backup/restore; not provider backup proof."""
import argparse
from contextlib import ExitStack
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3


def identity(root):
    result={}
    for p in sorted(Path(root).rglob('*')):
        if p.is_symlink():raise ValueError('BACKUP_SYMLINK_REJECTED')
        if p.is_file() and p!=Path(root)/'manifest.json':result[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def backup(state,outputs,destination):
    state,outputs,dest=map(Path,(state,outputs,destination));os.umask(0o077)
    dest.mkdir(mode=0o700,parents=True,exist_ok=False)
    with ExitStack() as stack:
        for p in [state/'branch.lock',outputs/'worker.lock']:
            f=stack.enter_context(p.open('rb'));fcntl.flock(f,fcntl.LOCK_EX)
        source=sqlite3.connect(state/'jobs.sqlite');target=sqlite3.connect(dest/'jobs.sqlite')
        source.backup(target);target.close();source.close()
        # Original synthetic consoles/results are copied, never reduced to hashes alone.
        for p in outputs.iterdir():
            if p.is_symlink():raise ValueError('BACKUP_SYMLINK_REJECTED')
            if p.is_dir():
                identity(p);shutil.copytree(p,dest/'outputs'/p.name)
            elif p.is_file():
                (dest/'outputs').mkdir(mode=0o700,exist_ok=True)
                shutil.copy2(p,dest/'outputs'/p.name)
            else:raise ValueError('BACKUP_SPECIAL_FILE_REJECTED')
    data=identity(dest);(dest/'manifest.json').write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    return {'files':len(data),'manifest_sha256':hashlib.sha256((dest/'manifest.json').read_bytes()).hexdigest(),'provider_recovery_proven':False}


def restore(source,destination):
    source,dest=Path(source),Path(destination)
    if source.is_symlink():raise ValueError('BACKUP_SYMLINK_REJECTED')
    expected=json.loads((source/'manifest.json').read_text())
    if identity(source)!=expected:raise ValueError('BACKUP_IDENTITY_MISMATCH')
    shutil.copytree(source,dest)
    if identity(dest)!=expected:raise ValueError('RESTORE_IDENTITY_MISMATCH')
    db=sqlite3.connect(dest/'jobs.sqlite')
    try:
        if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('RESTORE_DATABASE_INVALID')
        count=db.execute('SELECT count(*) FROM events').fetchone()[0]
    finally:db.close()
    return {'restored':True,'events':count,'files':len(expected),'provider_recovery_proven':False}


def backup_handover(state,turns,destination):
    """Snapshot the known coordinator/report databases and original model evidence.

    Use under the setup/operator identity. This never backs up keys or restores
    authority. Protected ledger/permission reconciliation is a separate operation.
    """
    state,turns,dest=map(Path,(state,turns,destination))
    for path in (state,turns):
        if any(p.is_symlink() for p in (path,*path.parents)):raise ValueError('BACKUP_SYMLINK_REJECTED')
    os.umask(0o077);dest.mkdir(mode=0o700,parents=True,exist_ok=False)
    with ExitStack() as stack:
        for path in (state/'branch.lock',state/'admission.lock',turns/'branch.lock'):
            stream=stack.enter_context(path.open('rb'));fcntl.flock(stream,fcntl.LOCK_EX)
        databases=('coordinator.sqlite','reports/reports.sqlite')
        for name in databases:
            source=state/name
            if source.is_symlink() or not source.is_file():raise ValueError('HANDOVER_DATABASE_REQUIRED')
            target=dest/'state'/name;target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
            with sqlite3.connect('file:'+str(source)+'?mode=ro',uri=True) as original:
                with sqlite3.connect(target) as copy:original.backup(copy)
        for path in state.rglob('*'):
            if path.is_symlink():raise ValueError('BACKUP_SYMLINK_REJECTED')
            name=path.relative_to(state).as_posix()
            if not path.is_file() or any(name==d or name in (d+'-wal',d+'-shm') for d in databases):continue
            target=dest/'state'/name;target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
            shutil.copy2(path,target)
        identity(turns);shutil.copytree(turns,dest/'turns')
    files=identity(dest)
    manifest={'kind':'HANDOVER_APPLICATION_SAMPLE','files':files,
              'databases':['state/'+name for name in databases],
              'authority_restored':False,'provider_recovery_proven':False}
    (dest/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    return {'files':len(files),'manifest_sha256':hashlib.sha256((dest/'manifest.json').read_bytes()).hexdigest(),
            'authority_restored':False,'provider_recovery_proven':False}


def restore_handover(source,destination):
    """Restore into a fresh private test directory; never start services or models."""
    source,dest=Path(source),Path(destination)
    if source.is_symlink():raise ValueError('BACKUP_SYMLINK_REJECTED')
    manifest=json.loads((source/'manifest.json').read_text())
    if (manifest.get('kind')!='HANDOVER_APPLICATION_SAMPLE' or
        manifest.get('databases')!=['state/coordinator.sqlite','state/reports/reports.sqlite'] or
        identity(source)!=manifest['files']):raise ValueError('BACKUP_IDENTITY_MISMATCH')
    shutil.copytree(source,dest)
    if identity(dest)!=manifest['files']:raise ValueError('RESTORE_IDENTITY_MISMATCH')
    for name in manifest['databases']:
        with sqlite3.connect('file:'+str(dest/name)+'?mode=ro',uri=True) as database:
            if database.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('RESTORE_DATABASE_INVALID')
    return {'restored':True,'files':len(manifest['files']),'authority_restored':False,
            'models_started':0,'provider_recovery_proven':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['backup','restore']);p.add_argument('--state',type=Path);p.add_argument('--outputs',type=Path);p.add_argument('--source',type=Path);p.add_argument('--destination',type=Path,required=True);a=p.parse_args()
    print(json.dumps(backup(a.state,a.outputs,a.destination) if a.action=='backup' else restore(a.source,a.destination)))
