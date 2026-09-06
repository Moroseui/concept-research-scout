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

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['backup','restore']);p.add_argument('--state',type=Path);p.add_argument('--outputs',type=Path);p.add_argument('--source',type=Path);p.add_argument('--destination',type=Path,required=True);a=p.parse_args()
    print(json.dumps(backup(a.state,a.outputs,a.destination) if a.action=='backup' else restore(a.source,a.destination)))
