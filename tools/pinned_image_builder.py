"""Fixed no-patient Modal image build. Standalone file: never mount its package."""
import hashlib
import importlib
import importlib.metadata as metadata
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import sys

TARGET='/opt/research-scientific-python'
PROOF=TARGET+'/native-proof.json'
IMPORTS=('numpy','pandas','scipy','sklearn','torch','matplotlib','psutil','nibabel','xgboost','nnunetv2','SimpleITK','dynamic_network_architectures','batchgeneratorsv2')
TRAINERS=('nnUNetTrainer_5epochs','nnUNetTrainer_250epochs')
PARAMETERS=['self','plans','configuration','fold','dataset_json','device']
BUILD_TOOLS=('setuptools','wheel','packaging')
CONSOLES=('nnUNetv2_plan_and_preprocess','nnUNetv2_extract_fingerprint','nnUNetv2_preprocess','nnUNetv2_train')

def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def name(value):return re.sub(r'[-_.]+','-',value).lower()

CPU_SCHEMA='pinned-diagnostics-image-selection/v1'
def cpu(value):return isinstance(value,dict) and value.get('schema')==CPU_SCHEMA

def selection(value):
    is_cpu=cpu(value)
    fields={'schema','python_executable','python_version','cuda','packages','hashes'}
    if (not isinstance(value,dict) or set(value)!=fields or value['schema'] not in {'pinned-modal-image-selection/v1',CPU_SCHEMA}
            or not isinstance(value['python_executable'],str)
            or not re.fullmatch(r'/(?:usr/bin|opt/[A-Za-z0-9_./-]+/bin)/python(?:3(?:\.[0-9]+)?)?',value['python_executable'])
            or '..' in Path(value['python_executable']).parts
            or not re.fullmatch(r'3\.[0-9]+\.[0-9]+',str(value['python_version']))
            or (value['cuda'] is not None if is_cpu else not re.fullmatch(r'[0-9]+\.[0-9]+',str(value['cuda'])))):raise ValueError('PINNED_IMAGE_SELECTION')
    packages=value['packages'];hashes=value['hashes']
    if not isinstance(packages,dict) or not (3 if is_cpu else 13)<=len(packages)<=300 or not isinstance(hashes,dict) or set(hashes)!=set(packages):
        raise ValueError('PINNED_IMAGE_COMPLETE_LOCK_REQUIRED')
    for key,version in packages.items():
        if (not isinstance(key,str) or name(key)!=key or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,99}',key)
                or not isinstance(version,str) or not re.fullmatch(r'[0-9][A-Za-z0-9.+!_-]{0,79}',version)
                or not isinstance(hashes[key],list) or not 1<=len(hashes[key])<=5
                or len(set(hashes[key]))!=len(hashes[key])
                or any(not isinstance(h,str) or not re.fullmatch('[0-9a-f]{64}',h) for h in hashes[key])):
            raise ValueError('PINNED_IMAGE_LOCK')
    required={'numpy','pandas','scipy','scikit-learn','torch','matplotlib','psutil','nibabel','xgboost','nnunetv2','simpleitk','dynamic-network-architectures','batchgeneratorsv2'}
    if is_cpu:
        if not set(BUILD_TOOLS)<=set(packages) or any(n.startswith(('nvidia-','cuda-','cupy','tensorrt','triton')) for n in packages):
            raise ValueError('PINNED_IMAGE_CPU_PACKAGES')
        if 'torch' in packages and not packages['torch'].endswith('+cpu'):raise ValueError('PINNED_IMAGE_CPU_TORCH')
    elif (not (required|set(BUILD_TOOLS)|{'acvl-utils'})<=set(packages) or packages['nnunetv2']!='2.8.1'
            or packages['torch']!='2.11.0+cu128' or value['cuda']!='12.8'):
        raise ValueError('PINNED_IMAGE_REQUIRED_PACKAGES')
    return ''.join(n+'=='+packages[n]+''.join(' --hash=sha256:'+h for h in sorted(hashes[n]))+'\n' for n in sorted(packages))

def safe_environment():
    # No host/operator/Modal credentials are passed into pip or native imports.
    return {'PATH':TARGET+'/bin:/usr/bin:/bin','HOME':TARGET,'LANG':'C.UTF-8',
        'PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1','CUDA_VISIBLE_DEVICES':'',
        'nnUNet_raw':TARGET+'/empty/raw','nnUNet_preprocessed':TARGET+'/empty/preprocessed',
        'nnUNet_results':TARGET+'/empty/results','MPLCONFIGDIR':TARGET+'/empty/matplotlib'}

def native(selected):
    selection(selected)
    actual={'python':sys.version,'cuda':(importlib.import_module('torch').version.cuda if 'torch' in selected['packages'] else None),
            'packages':{n:metadata.version(n) for n in selected['packages']}}
    if ('.'.join(map(str,sys.version_info[:3]))!=selected['python_version']
            or actual['cuda']!=selected['cuda'] or actual['packages']!=selected['packages']):
        raise ValueError('PINNED_IMAGE_ACTUAL_VERSION')
    found={}
    for d in metadata.distributions():
        key=name(d.metadata['Name'])
        if key in found:raise ValueError('PINNED_IMAGE_DUPLICATE_DISTRIBUTION')
        found[key]=d.version
    if found!=selected['packages']:raise ValueError('PINNED_IMAGE_UNPINNED_DISTRIBUTION')
    if cpu(selected):return {'actual':actual,'imports':{},'trainers':{},'reader':None,'console_help':{}}
    imports={n:importlib.import_module(n).__name__ for n in IMPORTS}
    trainers=importlib.import_module('nnunetv2.training.nnUNetTrainer.variants.training_length.nnUNetTrainer_Xepochs')
    observed={n:list(inspect.signature(getattr(trainers,n).__init__).parameters) for n in TRAINERS}
    if observed!={n:PARAMETERS for n in TRAINERS}:raise ValueError('PINNED_IMAGE_TRAINER_API')
    reader=importlib.import_module('nnunetv2.imageio.simpleitk_reader_writer').SimpleITKIO
    if not inspect.isclass(reader) or not all(callable(getattr(reader,n,None)) for n in ('read_images','read_seg')):
        raise ValueError('PINNED_IMAGE_READER_API')
    consoles={}
    for n in CONSOLES:
        run=subprocess.run([TARGET+'/bin/'+n,'--help'],env=safe_environment(),capture_output=True,timeout=60,check=True)
        if max(len(run.stdout),len(run.stderr))>131072 or b'usage:' not in (run.stdout+run.stderr).lower():
            raise ValueError('PINNED_IMAGE_CONSOLE_HELP')
        consoles[n]={'exit_code':run.returncode,'stdout_sha256':sha(run.stdout),'stderr_sha256':sha(run.stderr),'usage_seen':True}
    return {'actual':actual,'imports':imports,'trainers':observed,'reader':'SimpleITKIO','console_help':consoles}

def build(selected,selection_sha256,builder_sha256):
    """One exact hashed pip installation at image build time, never in a job."""
    os.umask(0o077);lock=selection(selected)
    if sha(encoded(selected))!=selection_sha256 or sha(Path(__file__).read_bytes())!=builder_sha256:
        raise ValueError('PINNED_IMAGE_BUILD_SOURCE')
    if Path(TARGET).exists() or Path(TARGET).is_symlink():raise ValueError('PINNED_IMAGE_BUILD_EXISTS')
    env={'PATH':'/usr/bin:/bin','HOME':'/tmp','LANG':'C.UTF-8','PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1'}
    executable=selected['python_executable']
    subprocess.run([executable,'-I','-B','-c',"import sys;assert '.'.join(map(str,sys.version_info[:3]))==sys.argv[1]",selected['python_version']],env=env,check=True,timeout=30)
    subprocess.run([executable,'-I','-B','-m','venv','--copies','--without-pip',TARGET],env=env,check=True,timeout=60)
    for folder in ('raw','preprocessed','results','matplotlib'):(Path(TARGET)/'empty'/folder).mkdir(mode=0o700,parents=True)
    lockpath=Path(TARGET)/'requirements.lock';lockpath.write_text(lock)
    # Exact build tools are installed first; the only source package is the
    # hash-pinned acvl-utils archive. No isolated build can fetch extra tooling.
    buildlock=Path(TARGET)/'build-tools.lock'
    buildlock.write_text(''.join(line+'\n' for line in lock.splitlines() if line.split('==',1)[0] in BUILD_TOOLS))
    pip=[executable,'-I','-B','-m','pip','--isolated','--python',TARGET+'/bin/python',
         'install','--index-url','https://pypi.org/simple','--extra-index-url',('https://download.pytorch.org/whl/cpu' if cpu(selected) else 'https://download.pytorch.org/whl/cu128'),
         '--require-hashes','--no-deps','--no-cache-dir','--no-compile','--disable-pip-version-check']
    with (Path(TARGET)/'pip-build-tools.log').open('xb') as out:
        subprocess.run(pip+['--only-binary=:all:','-r',str(buildlock)],env=env,check=True,timeout=120,stdout=out,stderr=subprocess.STDOUT)
    with (Path(TARGET)/'pip-install.log').open('xb') as out:
        subprocess.run(pip+['--no-build-isolation','--only-binary=:all:']+([] if cpu(selected) else ['--no-binary=acvl-utils'])+['-r',str(lockpath)],
            env=env,check=True,timeout=1080,stdout=out,stderr=subprocess.STDOUT)
    # pip check uses the same fresh target; missing dependencies fail the build.
    subprocess.run([executable,'-I','-B','-m','pip','--isolated','--python',TARGET+'/bin/python','check'],
                   env=env,check=True,timeout=60)
    copied=Path(TARGET)/'pinned_image_builder.py';copied.write_bytes(Path(__file__).read_bytes())
    data=subprocess.run([TARGET+'/bin/python','-I','-B',str(copied),'native',json.dumps(selected)],
                        env=safe_environment(),check=True,capture_output=True,timeout=300)
    if len(data.stdout)>131072:raise ValueError('PINNED_IMAGE_PROOF_SIZE')
    actual=json.loads(data.stdout)
    proof={'schema':'pinned-modal-image-native/v1','selection_sha256':selection_sha256,
           'builder_sha256':builder_sha256,'lock_sha256':sha(lock.encode()),**actual,
           'patient_computation':False,'gpu_verified':False}
    with Path(PROOF).open('xb') as out:out.write(encoded(proof));out.flush();os.fsync(out.fileno())

if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1]!='native':raise SystemExit('PINNED_IMAGE_FIXED_COMMAND')
    from contextlib import redirect_stdout
    with redirect_stdout(sys.stderr):value=native(json.loads(sys.argv[2]))
    print(json.dumps(value,sort_keys=True))
