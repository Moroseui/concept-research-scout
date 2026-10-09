"""Pinned, offline dependency setup inside an already admitted fit sandbox.

No SDK, network, credential, source build, dependency resolution or scientific
method lives here. This is composed into the existing input guard. Root-selected
runtime pins select the interpreter, wheels and expected import environment.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import stat
import sys


def environment_bytes(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def environment_name(value):return re.sub(r'[-_.]+','-',value).lower()


def environment_validate(spec):
    if isinstance(spec,dict) and spec.get('schema')=='modal-pinned-image/v1':
        fields={'schema','python_executable','image_id','base_image','builder_sha256','selection_sha256','native_sha256','expected'}
        if (set(spec)!=fields or spec['python_executable']!='/opt/research-scientific-python/bin/python'
                or not re.fullmatch(r'im-[A-Za-z0-9]+',str(spec['image_id']))
                or not re.fullmatch(r'pytorch/pytorch@sha256:[0-9a-f]{64}',str(spec['base_image']))
                or any(not re.fullmatch('[0-9a-f]{64}',str(spec[k])) for k in ('builder_sha256','selection_sha256','native_sha256'))):
            raise ValueError('SCIENTIFIC_IMAGE_FIELDS')
        e=spec['expected']
        if (not isinstance(e,dict) or set(e)!={'python','cuda','packages'} or not isinstance(e['python'],str)
                or not 1<=len(e['python'])<=500 or not re.fullmatch(r'[0-9]+\.[0-9]+',str(e['cuda']))
                or not isinstance(e['packages'],dict) or not 13<=len(e['packages'])<=300
                or e['packages'].get('nnunetv2')!='2.8.1' or 'torch' not in e['packages']):raise ValueError('SCIENTIFIC_IMAGE_EXPECTED')
        for n,v in e['packages'].items():
            if (not isinstance(n,str) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,99}',n)
                    or not isinstance(v,str) or not re.fullmatch('[0-9][A-Za-z0-9.+!_-]{0,79}',v)):raise ValueError('SCIENTIFIC_IMAGE_PACKAGES')
        return None
    if (not isinstance(spec,dict) or set(spec)!={'schema','python_executable','expected','wheels'}
            or spec['schema']!='offline-scientific-python/v1'
            or not isinstance(spec['python_executable'],str)
            or not re.fullmatch(r'/(?:usr/bin|opt/[A-Za-z0-9_./-]+/bin)/python(?:3(?:\.[0-9]+)?)?',spec['python_executable'])
            or '..' in Path(spec['python_executable']).parts):
        raise ValueError('SCIENTIFIC_ENVIRONMENT_FIELDS')
    expected=spec['expected'];wheels=spec['wheels']
    if (not isinstance(expected,dict) or set(expected)!={'python','cuda','packages'}
            or not isinstance(expected['python'],str) or not 1<=len(expected['python'])<=500
            or expected['cuda'] is not None and (not isinstance(expected['cuda'],str) or not re.fullmatch(r'[0-9]+\.[0-9]+',expected['cuda']))):
        raise ValueError('SCIENTIFIC_ENVIRONMENT_EXPECTED')
    packages=expected['packages']
    if (not isinstance(packages,dict) or not packages or len(packages)>300
            or not isinstance(wheels,dict) or not wheels or len(wheels)>300):
        raise ValueError('SCIENTIFIC_ENVIRONMENT_PACKAGES')
    names=set();requirements=[]
    for name,version in packages.items():
        if (not isinstance(name,str) or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]{0,99}',name)
                or not isinstance(version,str) or not re.fullmatch('[0-9][A-Za-z0-9.+!_-]{0,79}',version)
                or environment_name(name) in names):
            raise ValueError('SCIENTIFIC_ENVIRONMENT_PACKAGES')
        names.add(environment_name(name))
    versions={environment_name(k):v for k,v in packages.items()};seen=set()
    for filename,row in sorted(wheels.items()):
        if (not isinstance(filename,str) or not re.fullmatch(r'[A-Za-z0-9_.+!-]+\.whl',filename)
                or not isinstance(row,dict) or set(row)!={'sha256','bytes'}
                or not isinstance(row['sha256'],str) or not re.fullmatch('[a-f0-9]{64}',row['sha256'])
                or type(row['bytes']) is not int or not 0<row['bytes']<=8*1024**3):
            raise ValueError('SCIENTIFIC_ENVIRONMENT_WHEELS')
        parts=filename[:-4].split('-')
        if len(parts) not in {5,6}:raise ValueError('SCIENTIFIC_ENVIRONMENT_WHEEL_NAME')
        name=environment_name(parts[0]);version=parts[1]
        if name in seen or versions.get(name)!=version:raise ValueError('SCIENTIFIC_ENVIRONMENT_WHEEL_VERSION')
        seen.add(name);requirements.append(name+'=='+version+' --hash=sha256:'+row['sha256'])
    if sum(x['bytes'] for x in wheels.values())>32*1024**3:raise ValueError('SCIENTIFIC_ENVIRONMENT_SIZE')
    return '\n'.join(requirements)+'\n'


def environment_path(target,current):
    """Expose only pip's private, freshly installed console-script directory."""
    target=Path(target);scripts=target/'bin'
    for directory in (target,scripts):
        if directory==scripts and not directory.exists() and not directory.is_symlink():
            return current
        info=directory.lstat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.geteuid() or info.st_mode&0o077):
            raise ValueError('SCIENTIFIC_ENVIRONMENT_SCRIPT_PATH')
    for script in scripts.iterdir():
        info=script.lstat()
        # pip gives console scripts 0755 even under umask 077. Their two
        # enclosing directories remain owner-only; no other writer is allowed.
        if (not stat.S_ISREG(info.st_mode) or info.st_uid!=os.geteuid() or info.st_mode&0o022):
            raise ValueError('SCIENTIFIC_ENVIRONMENT_SCRIPT_PATH')
    return str(scripts)+os.pathsep+(current or os.defpath)


def environment_install(requirements,wheels,wheel_files,progress,binding_sha256,verify_files):
    """Shared offline install; caller validates the exact selected wheel lock."""
    os.umask(0o077)
    verify_files(wheels,wheel_files)
    work=Path('/tmp')/('scientific-python-'+binding_sha256)
    if work.exists() or work.is_symlink():raise ValueError('SCIENTIFIC_ENVIRONMENT_ALREADY_EXISTS')
    work.mkdir(mode=0o700);lock=work/'requirements.lock';target=work/'site-packages'
    with lock.open('x') as f:f.write(requirements)
    # Hash-only wheel requirements; all transitive wheels must be selected.
    # The existing sandbox blocks network even if a dependency is absent.
    args=[sys.executable,'-I','-B','-m','pip','--isolated','install','--no-index','--no-deps',
          '--require-hashes','--only-binary=:all:','--no-cache-dir','--no-compile',
          '--find-links',str(wheels),'--target',str(target),'-r',str(lock)]
    log=Path(progress)/'environment-install.log'
    # One log per segment, because progress is the segment-specific directory.
    try:
        with log.open('xb') as out:
            subprocess.run(args,check=True,timeout=180,stdout=out,stderr=subprocess.STDOUT)
            out.flush();os.fsync(out.fileno())
    except (subprocess.SubprocessError,OSError) as error:
        raise ValueError('SCIENTIFIC_ENVIRONMENT_INSTALL_FAILED') from error
    env=dict(os.environ,PYTHONPATH=str(target),PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1')
    env['PATH']=environment_path(target,env.get('PATH',os.defpath))
    return env


def environment_observe(packages,cuda,env):
    """Observe the same native identity used by the normal scientific guard."""
    probe=("import importlib.metadata,json,sys\n"
           "names=json.loads(sys.argv[1]);cuda=None\n"
           "if sys.argv[2]=='cuda':\n import torch;cuda=torch.version.cuda\n"
           "print(json.dumps({'python':sys.version,'cuda':cuda,'packages':{n:importlib.metadata.version(n) for n in names}},sort_keys=True))\n")
    try:
        observed=subprocess.run([sys.executable,'-B','-s','-c',probe,json.dumps(list(packages)),
                                 'cuda' if cuda else 'cpu'],
                                env=env,check=True,capture_output=True,text=True,timeout=60)
        actual=json.loads(observed.stdout)
    except (subprocess.SubprocessError,ValueError,OSError) as error:
        raise ValueError('SCIENTIFIC_ENVIRONMENT_PROBE_FAILED') from error
    return actual


def environment_prepare(spec,wheels,progress,binding_sha256,verify_files):
    """Runs before the reviewed module, in the same network-blocked container."""
    os.umask(0o077)
    requirements=environment_validate(spec)
    if (sys.version!=spec['expected']['python']
            or Path(sys.executable).resolve()!=Path(spec['python_executable']).resolve()):
        raise ValueError('SCIENTIFIC_ENVIRONMENT_INTERPRETER')
    image_mode=spec['schema']=='modal-pinned-image/v1'
    if image_mode:
        if wheels is not None:raise ValueError('SCIENTIFIC_IMAGE_UNEXPECTED_WHEELS')
        native=Path('/opt/research-scientific-python/native-proof.json')
        if native.is_symlink() or not native.is_file() or hashlib.sha256(native.read_bytes()).hexdigest()!=spec['native_sha256']:
            raise ValueError('SCIENTIFIC_IMAGE_NATIVE_CHANGED')
        env=dict(os.environ,PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1')
        env.pop('PYTHONPATH',None);env['PATH']='/opt/research-scientific-python/bin:'+os.defpath
    else:env=environment_install(requirements,wheels,spec['wheels'],progress,binding_sha256,verify_files)
    expected=spec['expected']
    actual=environment_observe(expected['packages'],expected['cuda'] is not None,env)
    if actual!=expected:raise ValueError('SCIENTIFIC_ENVIRONMENT_CHANGED')
    with (Path(progress)/'environment.json').open('xb') as out:
        out.write(environment_bytes({'schema':'scientific-environment-proof/v1',
            'binding_sha256':binding_sha256,'expected_sha256':hashlib.sha256(environment_bytes(expected)).hexdigest(),
            'actual':actual,'offline':True,**({'image_id':spec['image_id'],'native_sha256':spec['native_sha256']} if image_mode else {})}))
        out.flush();os.fsync(out.fileno())
    for path in ([Path(progress)/'environment.json'] if image_mode else [Path(progress)/'environment-install.log',Path(progress)/'environment.json']):
        if path.is_symlink() or path.stat().st_mode&0o077:
            raise ValueError('SCIENTIFIC_ENVIRONMENT_RECORD_PERMISSIONS')
    return env


def environment_proof(raw,binding):
    """Verify the original observed receipt, not just its presence."""
    spec=binding['scientific_environment'];environment_validate(spec)
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('SCIENTIFIC_ENVIRONMENT_PROOF')
            result[key]=value
        return result
    try:proof=json.loads(raw,object_pairs_hook=unique)
    except (ValueError,TypeError) as error:raise ValueError('SCIENTIFIC_ENVIRONMENT_PROOF') from error
    expected={'schema':'scientific-environment-proof/v1',
        'binding_sha256':hashlib.sha256(json.dumps(binding,sort_keys=True).encode()).hexdigest(),
        'expected_sha256':hashlib.sha256(environment_bytes(spec['expected'])).hexdigest(),
        'actual':spec['expected'],'offline':True}
    if spec['schema']=='modal-pinned-image/v1':expected.update(image_id=spec['image_id'],native_sha256=spec['native_sha256'])
    if not isinstance(proof,dict) or type(proof.get('offline')) is not bool or proof!=expected:
        raise ValueError('SCIENTIFIC_ENVIRONMENT_PROOF')
    return {'receipt_sha256':hashlib.sha256(raw).hexdigest(),**proof}
