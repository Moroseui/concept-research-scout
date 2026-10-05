"""Bound single-start supervisor. No credentials, uploads or automatic retries."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(obj):return json.dumps(obj,sort_keys=True).encode()


def offline_environment(package,wheels=Path('/wheels'),target=Path('/tmp/scientific-python')):
    expected=json.loads((package/'wheels.json').read_text())['files']
    if {p.name for p in wheels.iterdir()}!=set(expected):raise ValueError('WORKLOAD_WHEEL_MEMBERS')
    for name,item in expected.items():
        path=wheels/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size!=item['bytes'] or sha(path.read_bytes())!=item['sha256']:
            raise ValueError('WORKLOAD_WHEEL_HASH')
    if target.exists():raise ValueError('WORKLOAD_ENVIRONMENT_ALREADY_EXISTS')
    # All wheels, including transitive dependencies, are reviewed hash pins.
    # No index/network, dependency resolution, source build or host installation.
    subprocess.run([sys.executable,'-B','-s','-m','pip','install','--no-index','--no-deps','--require-hashes',
                    '--only-binary=:all:','--find-links',str(wheels),'--target',str(target),
                    '-r',str(package/'requirements.lock')],check=True,timeout=180,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    env=dict(os.environ,PYTHONPATH=str(target),PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1')
    return env


def supervise(package,work,bound,*,execute=subprocess.run,prepare_environment=offline_environment):
    os.umask(0o077);package=Path(package);work=Path(work)
    manifest=json.loads((package/'manifest.json').read_bytes());binding=manifest['binding']
    if manifest.get('schema')!='modal-run/v1' or sha(canonical(binding))!=bound:raise ValueError('WORKLOAD_BINDING')
    files={}
    for path in package.rglob('*'):
        if path.is_symlink():raise ValueError('WORKLOAD_ALIAS')
        if path.is_file() and path.name!='manifest.json':files[str(path.relative_to(package))]=sha(path.read_bytes())
    if files!=manifest['files']:raise ValueError('WORKLOAD_PACKAGE_HASH')
    code={k:v for k,v in files.items() if k.endswith('.py')}
    if sha(canonical(code))!=binding['code_sha256']:raise ValueError('WORKLOAD_CODE_HASH')
    if sha((package/'SPEC.md').read_bytes())!=binding['spec_sha256'] or sha((package/'review.json').read_bytes())!=binding['review_sha256']:
        raise ValueError('WORKLOAD_APPROVAL_HASH')
    reviewed=json.loads((package/'review.json').read_bytes())
    if reviewed.get('verdict')!='APPROVE':raise ValueError('WORKLOAD_NOT_APPROVED')
    # An uncertain SDK response cannot lead to a second run inside this task.
    # Parent executor also prevents another exec/container request after intent.
    with (work/'started.json').open('x') as out:
        json.dump({'binding_sha256':bound,'started_at':time.time()},out);out.flush();os.fsync(out.fileno())
    final={'schema':'modal-result/v1','binding_sha256':bound,'status':'FAILED','files':{}}
    try:
        environment=prepare_environment(package)
        with (work/'worker-console.log').open('xb') as log:
            result=execute([sys.executable,'-B','-s',str(package/'worker.py')],cwd=work,
                           stdout=log,stderr=subprocess.STDOUT,env=environment,timeout=binding['resources']['timeout_seconds']-30,check=False)
        if result.returncode!=0:raise ValueError('WORKLOAD_FAILED')
        output=work/'outputs'
        (output/'console.log').write_bytes((work/'worker-console.log').read_bytes())
        (output/'started.json').write_bytes((work/'started.json').read_bytes())
        actual={str(p.relative_to(output)) for p in output.rglob('*') if p.is_file()}
        if actual!=set(binding['outputs']):raise ValueError('WORKLOAD_OUTPUT_MEMBER_SET')
        # Every produced result must have been declared before execution.
        # Do not discard predictions, masks, curves or console evidence.
        for name in binding['outputs']:
            path=output/name
            if (Path(name).is_absolute() or '..' in Path(name).parts or path.is_symlink() or not path.is_file() or
                any(parent.is_symlink() for parent in path.parents)):raise ValueError('WORKLOAD_OUTPUT_PATH')
            data=path.read_bytes();final['files'][name]={'sha256':sha(data),'bytes':len(data)}
        final['status']='COMPLETE'
    except Exception:
        final['files']={}
        raise
    finally:
        tmp=work/'research-result.json.tmp'
        with tmp.open('x') as out:
            json.dump(final,out,sort_keys=True);out.flush();os.fsync(out.fileno())
        os.replace(tmp,work/'research-result.json')
    return final


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--binding',required=True);args=parser.parse_args()
    supervise('/reviewed','/tmp',args.binding)
