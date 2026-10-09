"""Bounded item6 mount identity, create-only refusal and full-byte revalidation.

No scientific operations, provider calls or credentials. Only controller-bound
mount aliases are resolved; all children remain regular, unaliased files/dirs.
"""
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import uuid
from orchestrator.modal_volume_path import _bound_root


def require(ok,reason):
    if not ok:raise ValueError(reason)


def encoded(value):return json.dumps(value,sort_keys=True,allow_nan=False).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()


def roots(mounts):
    require(isinstance(mounts,dict) and set(mounts)=={'data','package'},'DIAGNOSTICS_MOUNT_FIELDS')
    for role in mounts:
        require(set(mounts[role])=={'volume_id','sub_path'},'DIAGNOSTICS_MOUNT_FIELDS')
    require(mounts['data']['volume_id']!=mounts['package']['volume_id'],'DIAGNOSTICS_MOUNT_ROLE_ALIAS')
    require(mounts['package']['sub_path']=='/' and isinstance(mounts['data']['sub_path'],str)
        and re.fullmatch('/[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*',mounts['data']['sub_path']), 'DIAGNOSTICS_MOUNT_SUBPATH')
    aliases={'data':'/data','package':'/reviewed'}
    result={role:_bound_root(alias,mounts[role]['volume_id'],set(aliases.values())) for role,alias in aliases.items()}
    require(all(_bound_root(aliases[role],mounts[role]['volume_id'],set(aliases.values()))==path
        for role,path in result.items()),'DIAGNOSTICS_MOUNT_CHANGED')
    return result


def snapshot(root,expected):
    root=Path(root)
    require(isinstance(expected,dict) and expected,'DIAGNOSTICS_GUARD_INVENTORY')
    for path in [root,*root.parents]:
        require(stat.S_ISDIR(path.lstat().st_mode),'DIAGNOSTICS_GUARD_PARENT_ALIAS')
    actual={};directories={root}
    for directory,dirs,names in os.walk(root,followlinks=False):
        for name in dirs+names:
            path=Path(directory)/name;info=path.lstat()
            if stat.S_ISDIR(info.st_mode):directories.add(path)
            else:
                require(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'DIAGNOSTICS_GUARD_ALIAS')
                actual[path.relative_to(root).as_posix()]=path
    require(set(actual)==set(expected),'DIAGNOSTICS_GUARD_MEMBERS')
    verified={}
    for name,path in sorted(actual.items()):
        row=expected[name];h=hashlib.sha256();size=0
        require(isinstance(row,dict) and re.fullmatch('[a-f0-9]{64}',row.get('sha256','')),'DIAGNOSTICS_GUARD_EXPECTED_HASH')
        with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOFOLLOW),'rb') as stream:
            before=os.fstat(stream.fileno())
            require(stat.S_ISREG(before.st_mode) and before.st_nlink==1,'DIAGNOSTICS_GUARD_ALIAS')
            for chunk in iter(lambda:stream.read(1024*1024),b''):
                size+=len(chunk);h.update(chunk)
            after=os.fstat(stream.fileno())
        identity=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns,x.st_nlink)
        require(identity(before)==identity(after),'DIAGNOSTICS_GUARD_CHANGED_DURING_READ')
        require(h.hexdigest()==row['sha256'] and size==row.get('bytes',size),'DIAGNOSTICS_GUARD_HASH')
        verified[name]={'sha256':h.hexdigest(),'bytes':size}
    return {'files':len(verified),'inventory_sha256':sha(encoded(verified))},sorted(directories,key=str)


def refuse_create(directories):
    """Probe each mount root and every descendant directory, never existing data.

    A successful create is a failure; leave the new empty sentinel as evidence. EEXIST and unrelated I/O errors never count as read-only evidence.
    """
    for directory in directories:
        descriptor=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            name='.research-create-refusal-'+uuid.uuid4().hex
            try:
                created=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=descriptor)
            except OSError as error:
                require(error.errno in {errno.EROFS,errno.EACCES,errno.EPERM},'DIAGNOSTICS_WRITE_PROBE_INCONCLUSIVE')
            else:
                # No content write, unlink or modification of an existing file.
                os.close(created)
                raise ValueError('DIAGNOSTICS_WRITE_WAS_ALLOWED')
        finally:os.close(descriptor)
    return len(directories)


def verify(mounts,inputs,package):
    selected=roots(mounts);proof={}
    for role,expected in [('data',inputs),('package',package)]:
        observed,directories=snapshot(selected[role],expected)
        probes=refuse_create(directories)
        proof[role]={**observed,'write_refusal_probes':probes,'volume_id':mounts[role]['volume_id'],
                     'sub_path':mounts[role]['sub_path']}
    require(roots(mounts)==selected,'DIAGNOSTICS_MOUNT_CHANGED')
    return selected,proof
