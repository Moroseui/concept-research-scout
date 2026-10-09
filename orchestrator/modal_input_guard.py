"""Stdlib-only worker guard: hash mounted inputs before scientific code starts.

The provider sends this exact reviewed source as the one exec entry point.
No network, SDK, credentials, patient selection or scientific calculation.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys


def canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False).encode()


def validate_inventory(files):
    if not isinstance(files,dict) or not files or len(files)>10000:
        raise ValueError("INPUT_GUARD_INVENTORY")
    for name, row in files.items():
        path=PurePosixPath(name) if isinstance(name,str) else None
        if (path is None or path.is_absolute() or str(path)!=name or not path.parts
                or any(x in {".",".."} for x in path.parts) or "\\" in name or "\x00" in name
                or not isinstance(row,dict) or set(row)!={"bytes","sha256"}
                or type(row["bytes"]) is not int or not 0<row["bytes"]<=8*1024**3
                or not isinstance(row["sha256"],str) or not re.fullmatch("[a-f0-9]{64}",row["sha256"])):
            raise ValueError("INPUT_GUARD_INVENTORY")
    if sum(row["bytes"] for row in files.values())>128*1024**3:
        raise ValueError("INPUT_GUARD_TOTAL")
    return files


def verify(root, files):
    files=validate_inventory(files);root=Path(root)
    if root.is_symlink() or not root.is_dir():raise ValueError("INPUT_GUARD_ROOT")
    found={}
    for directory, dirs, names in os.walk(root,followlinks=False):
        for name in dirs+names:
            path=Path(directory)/name;mode=path.lstat().st_mode
            if stat.S_ISDIR(mode):continue
            if not stat.S_ISREG(mode):raise ValueError("INPUT_GUARD_ALIAS_OR_TYPE")
            found[path.relative_to(root).as_posix()]=path.stat().st_size
    if found!={name:row["bytes"] for name,row in files.items()}:
        raise ValueError("INPUT_GUARD_MEMBER_OR_SIZE")
    for name,row in sorted(files.items()):
        hashed=hashlib.sha256();count=0
        fd=os.open(root/name,os.O_RDONLY|os.O_NOFOLLOW)
        with os.fdopen(fd,"rb") as stream:
            before=os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):raise ValueError("INPUT_GUARD_ALIAS_OR_TYPE")
            for chunk in iter(lambda:stream.read(1024*1024),b""):
                count+=len(chunk)
                if count>row["bytes"]:raise ValueError("INPUT_GUARD_HASH")
                hashed.update(chunk)
            after=os.fstat(stream.fileno())
        if (count!=row["bytes"] or hashed.hexdigest()!=row["sha256"] or
                (before.st_ino,before.st_dev,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=
                (after.st_ino,after.st_dev,after.st_size,after.st_mtime_ns,after.st_ctime_ns)):
            raise ValueError("INPUT_GUARD_HASH")
    return {"file_count":len(files),"total_bytes":sum(x["bytes"] for x in files.values()),
            "inventory_sha256":hashlib.sha256(canonical(files)).hexdigest()}


def proof_path(progress, binding_sha256):
    if not isinstance(binding_sha256,str) or not re.fullmatch("[a-f0-9]{64}",binding_sha256):
        raise ValueError("INPUT_GUARD_BINDING")
    return Path(progress)/"input-verification"/(binding_sha256+".json")


def execute(root, progress, script, payload, *, worker_args=(), runtime_setup=None):
    os.umask(0o077)
    if (not isinstance(payload,dict) or set(payload) not in ({"binding_sha256","guard_sha256","preprocessing_sha256","files"},
            {"binding_sha256","guard_sha256","preprocessing_sha256","files","volume_ids"},
            {"binding_sha256","guard_sha256","preprocessing_sha256","files","volume_ids","execution_manifest"}) or any(not isinstance(payload[k],str) or
            not re.fullmatch("[a-f0-9]{64}",payload[k]) for k in
            ("binding_sha256","guard_sha256","preprocessing_sha256"))):
        raise ValueError("INPUT_GUARD_PAYLOAD")
    if 'volume_ids' in payload:
        ids=payload['volume_ids']
        if (not isinstance(ids,dict) or set(ids) not in ({'inputs','progress','package'},{'inputs','progress','package','wheels'})
                or any(not isinstance(v,str) or not re.fullmatch('vo-[A-Za-z0-9]{1,80}',v) for v in ids.values())
                or len(set(ids.values()))!=len(ids)):
            raise ValueError('FIT_VOLUME_ROLE_BINDING')
    validate_inventory(payload["files"])
    path=proof_path(progress,payload["binding_sha256"])
    parent=path.parent
    mode=Path(progress).lstat().st_mode
    if not stat.S_ISDIR(mode) or mode&0o077:raise ValueError("INPUT_GUARD_RECORD_PERMISSIONS")
    parent.mkdir(mode=0o700,exist_ok=True)
    mode=parent.lstat().st_mode
    if not stat.S_ISDIR(mode) or mode&0o077:raise ValueError("INPUT_GUARD_RECORD_PERMISSIONS")
    # Reserve before verification. A second launch refuses, including after a
    # failed/incomplete attempt. There is no automatic recomputation here.
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    error=None;worker_environment=None
    proof={"schema":"modal-input-verification/v1", **{k:payload[k] for k in
        ("binding_sha256","guard_sha256","preprocessing_sha256")},
        "inventory_sha256":hashlib.sha256(canonical(payload["files"])).hexdigest(),
        "file_count":len(payload["files"]),"total_bytes":sum(x["bytes"] for x in payload["files"].values()),
        "status":"FAILED","reason":None}
    if 'volume_ids' in payload:proof['volume_ids']=payload['volume_ids']
    if runtime_setup is not None:
        proof['scientific_environment_sha256']=hashlib.sha256(canonical(payload['execution_manifest']['binding']['scientific_environment'])).hexdigest()
    try:
        verify(root,payload["files"])
        if runtime_setup is not None:
            preparation=Path(progress)/'environment-verification'/payload['binding_sha256']
            preparation.parent.mkdir(mode=0o700,exist_ok=True)
            if preparation.parent.is_symlink() or preparation.parent.stat().st_mode&0o077:
                raise ValueError('INPUT_GUARD_RECORD_PERMISSIONS')
            preparation.mkdir(mode=0o700)
            try:worker_environment=runtime_setup(preparation)
            except (ValueError,OSError) as caught:
                with (preparation/'failure.json').open('xb') as failure:
                    failure.write(canonical({'status':'FAILED','reason':str(caught),'scientific_code_started':False}))
                raise ValueError('SCIENTIFIC_ENVIRONMENT_FAILED') from caught
        proof["status"]="VERIFIED"
    except (ValueError,OSError) as caught:
        error=caught;proof["reason"]=str(caught) if isinstance(caught,ValueError) else "INPUT_GUARD_IO"
    with os.fdopen(fd,"wb") as out:
        out.write(canonical(proof));out.flush();os.fsync(out.fileno())
    if path.lstat().st_mode&0o077:raise ValueError("INPUT_GUARD_RECORD_PERMISSIONS")
    # Same mountpoint fsync as `sync MOUNT`, using only the pinned interpreter.
    # Do not add a host executable to the confined test/worker environment.
    commit = ("import os,sys\n"
              "fd=os.open(sys.argv[1], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)\n"
              "try: os.fsync(fd)\n"
              "finally: os.close(fd)\n")
    subprocess.run([sys.executable,'-I','-B','-c',commit,str(progress)],check=True,timeout=120)
    if error is not None:raise ValueError(proof["reason"]) from None
    # Only now does any reviewed scientific code enter the process.
    command=[sys.executable,"-B","-s",str(script),"--binding",payload["binding_sha256"],*worker_args]
    if worker_environment is not None:os.execve(sys.executable,command,worker_environment)
    else:os.execv(sys.executable,command)


def packaged_inventory(payload, roots):
    """Read one exact hash-bound metadata file, never an arbitrary workspace path."""
    if 'inventory_ref' not in payload:return payload
    expected={'binding_sha256','guard_sha256','preprocessing_sha256','inventory_ref','volume_ids','execution_manifest'}
    manifest=payload.get('execution_manifest');ref=payload['inventory_ref']
    if (set(payload)!=expected or not isinstance(manifest,dict) or set(manifest)!={'schema','binding','files'}
            or manifest['schema']!='modal-run/v1'
            or hashlib.sha256(canonical(manifest['binding'])).hexdigest()!=payload['binding_sha256']
            or manifest['binding'].get('purpose')!='M4_ITEM4'
            or 'preprocessing' not in manifest['binding']
            or ref!={'path':'input-inventory.json','sha256':manifest['binding']['preprocessing']['input_contract_sha256']}
            or manifest['files'].get('input-inventory.json')!=ref['sha256']):
        raise ValueError('INPUT_GUARD_INVENTORY_BINDING')
    path=roots['package']/'input-inventory.json'
    if any(p.is_symlink() for p in [path,*path.parents]):raise ValueError('INPUT_GUARD_INVENTORY_BINDING')
    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOFOLLOW),'rb') as stream:
        info=os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or not 0<info.st_size<=4*1024*1024:
            raise ValueError('INPUT_GUARD_INVENTORY_BINDING')
        raw=stream.read(4*1024*1024+1)
    if len(raw)!=info.st_size or hashlib.sha256(raw).hexdigest()!=ref['sha256']:
        raise ValueError('INPUT_GUARD_INVENTORY_BINDING')
    files=json.loads(raw);validate_inventory(files)
    expanded=dict(payload);expanded.pop('inventory_ref');expanded['files']=files
    return expanded


def execute_provider(payload, resolver):
    """Resolver is the exact release source prefixed by guard_program()."""
    if not isinstance(payload,dict) or 'volume_ids' not in payload:
        raise ValueError('FIT_VOLUME_ROLE_BINDING')
    roots=resolver(payload['volume_ids'])
    payload=packaged_inventory(payload,roots)
    extra=();runtime_setup=None
    if 'execution_manifest' in payload:
        manifest=payload['execution_manifest']
        if (not isinstance(manifest,dict) or set(manifest)!={'schema','binding','files'}
                or manifest['schema']!='modal-run/v1'
                or hashlib.sha256(canonical(manifest['binding'])).hexdigest()!=payload['binding_sha256']):
            raise ValueError('INPUT_GUARD_EXECUTION_BINDING')
        extra=('--manifest-json',canonical(manifest).decode())
        if 'scientific_environment' in manifest['binding']:
            spec=manifest['binding']['scientific_environment'];environment_validate(spec)
            expected_environment=(manifest['binding']['preprocessing']['environment_sha256']
                if 'preprocessing' in manifest['binding'] else manifest['binding']['progress']['fit_binding']['environment_sha256'])
            image_mode=spec['schema']=='modal-pinned-image/v1'
            if (set(roots)!=({'inputs','progress','package'} if image_mode else {'inputs','progress','package','wheels'})
                    or hashlib.sha256(environment_bytes(spec['expected'])).hexdigest()!=expected_environment):
                raise ValueError('INPUT_GUARD_ENVIRONMENT_BINDING')
            runtime_setup=lambda folder:environment_prepare(spec,None if image_mode else roots['wheels'],folder,payload['binding_sha256'],verify)
    if 'wheels' in roots and runtime_setup is None:raise ValueError('INPUT_GUARD_ENVIRONMENT_BINDING')
    execute(roots['inputs'],roots['progress'],roots['package']/'run.py',payload,
            worker_args=('--input-root',str(roots['inputs']),'--progress-root',str(roots['progress']),*extra),runtime_setup=runtime_setup)


if __name__=="__main__":
    # Production runs the composed, hash-bound program, not a naked guard file.
    execute_provider(json.loads(sys.argv[1]),bound_fit_roots)
