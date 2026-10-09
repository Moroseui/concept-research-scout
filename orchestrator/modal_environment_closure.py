"""Fixed no-patient offline nnUNet closure proof; no provider or admission path.

Exact selected wheels install once. Native observations produce the expected
identity; the ordinary scientific guard retains its strict expected checks.
This proof neither trains nor chooses methods and is not GPU validation.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from orchestrator import modal_scientific_environment as environment

SCHEMA = "offline-scientific-closure-selection/v1"
RESULT = "offline-scientific-closure-proof/v1"
IMPORTS = {"numpy":"numpy", "pandas":"pandas", "scipy":"scipy",
    "scikit-learn":"sklearn", "torch":"torch", "matplotlib":"matplotlib",
    "psutil":"psutil", "nibabel":"nibabel", "xgboost":"xgboost",
    "nnunetv2":"nnunetv2", "simpleitk":"SimpleITK",
    "dynamic-network-architectures":"dynamic_network_architectures",
    "batchgeneratorsv2":"batchgeneratorsv2"}
TRAINERS = ("nnUNetTrainer_5epochs", "nnUNetTrainer_250epochs")
PARAMETERS = ["self", "plans", "configuration", "fold", "dataset_json", "device"]
CONSOLES = ("nnUNetv2_plan_and_preprocess", "nnUNetv2_extract_fingerprint",
            "nnUNetv2_preprocess", "nnUNetv2_train")
MAX_CAPTURE = 128 * 1024
PROBE = r"""import importlib,inspect,json
names=('numpy','pandas','scipy','sklearn','torch','matplotlib','psutil','nibabel','xgboost','nnunetv2','SimpleITK','dynamic_network_architectures','batchgeneratorsv2')
imports={name:importlib.import_module(name).__name__ for name in names}
mod=importlib.import_module('nnunetv2.training.nnUNetTrainer.variants.training_length.nnUNetTrainer_Xepochs')
trainers={name:list(inspect.signature(getattr(mod,name).__init__).parameters) for name in ('nnUNetTrainer_5epochs','nnUNetTrainer_250epochs')}
reader=importlib.import_module('nnunetv2.imageio.simpleitk_reader_writer').SimpleITKIO
if not inspect.isclass(reader) or not all(callable(getattr(reader,x,None)) for x in ('read_images','read_seg')):
    raise RuntimeError('CLOSURE_READER_INTERFACE')
print(json.dumps({'imports':imports,'trainers':trainers,'reader':'SimpleITKIO'},sort_keys=True))
"""


def digest(raw): return hashlib.sha256(raw).hexdigest()
def encoded(value): return environment.environment_bytes(value)


def strict(raw):
    def pairs(items):
        value={}
        for key,item in items:
            if key in value: raise ValueError('CLOSURE_DUPLICATE_FIELD')
            value[key]=item
        return value
    try: return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('CLOSURE_JSON_NUMBER')))
    except (TypeError,UnicodeError) as error: raise ValueError('CLOSURE_JSON') from error


def selection(value):
    if not isinstance(value,dict) or set(value)!={'schema','python_executable','packages','wheels'} or value['schema']!=SCHEMA:
        raise ValueError('CLOSURE_SELECTION_FIELDS')
    # Reuse the existing package/wheel contract. These two temporary fields are
    # observations of this process used only for validation, never claimed pins.
    candidate={'schema':'offline-scientific-python/v1','python_executable':value['python_executable'],
               'expected':{'python':sys.version,'cuda':None,'packages':value['packages']},'wheels':value['wheels']}
    requirements=environment.environment_validate(candidate)
    packages={environment.environment_name(k):v for k,v in value['packages'].items()}
    if (not set(IMPORTS)<=set(packages) or packages['nnunetv2']!='2.8.1'
            or not {'nnunetv2','torch'}<=set(value['packages'])
            or not any(environment.environment_name(name.split('-')[0])=='nnunetv2' for name in value['wheels'])):
        raise ValueError('CLOSURE_REQUIRED_PACKAGES')
    return requirements


def private(path,directory=False):
    path=Path(path)
    if any(p.is_symlink() for p in (path,*path.parents)): raise ValueError('CLOSURE_PATH_ALIAS')
    info=path.stat()
    if ((directory and not stat.S_ISDIR(info.st_mode)) or (not directory and not stat.S_ISREG(info.st_mode))
            or info.st_mode&0o007 or info.st_mode&0o070 and info.st_gid!=1003
            or not directory and info.st_nlink!=1): raise ValueError('CLOSURE_PRIVATE_PATH')
    return path


def filehash(path):
    value=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):value.update(chunk)
    return value.hexdigest()


def verify_wheels(root,files):
    root=private(root,True);seen={}
    for path in root.iterdir():
        private(path)
        seen[path.name]={'bytes':path.stat().st_size,'sha256':filehash(path)}
    if seen!=files: raise ValueError('CLOSURE_WHEEL_INVENTORY')


def capture(argv,env,folder,name):
    paths={key:Path(folder)/(name+'.'+key) for key in ('stdout','stderr')}
    try:
        with paths['stdout'].open('xb') as out,paths['stderr'].open('xb') as err:
            result=subprocess.run(argv,env=env,stdout=out,stderr=err,timeout=60,check=False)
    except (OSError,subprocess.SubprocessError) as error: raise ValueError('CLOSURE_CHECK_FAILED:'+name) from error
    raw={};metadata={}
    for key,path in paths.items():
        private(path)
        if path.stat().st_size>MAX_CAPTURE: raise ValueError('CLOSURE_CAPTURE_LIMIT')
        raw[key]=path.read_bytes();metadata[key]={'sha256':digest(raw[key]),'bytes':len(raw[key])}
    if result.returncode!=0:raise ValueError('CLOSURE_CHECK_FAILED:'+name)
    return raw,{'exit_code':result.returncode,**metadata}


def pins():
    return {'worker_sha256':filehash(__file__),'consumer_sha256':filehash(environment.__file__)}


def validate_result(raw,selected,binding_sha256):
    selection(selected)
    if not isinstance(raw,bytes) or len(raw)>MAX_CAPTURE:raise ValueError('CLOSURE_RESULT_BOUND')
    value=strict(raw)
    fields={'schema','binding_sha256','selection_sha256','worker_sha256','consumer_sha256',
            'scientific_environment','environment_sha256','checks','patient_computation','gpu_verified'}
    if (not isinstance(value,dict) or set(value)!=fields or value['schema']!=RESULT
            or not re.fullmatch('[0-9a-f]{64}',binding_sha256)
            or value['binding_sha256']!=binding_sha256 or value['selection_sha256']!=digest(encoded(selected))
            or any(value[k]!=v for k,v in pins().items())
            or value['patient_computation'] is not False or value['gpu_verified'] is not False):
        raise ValueError('CLOSURE_RESULT_BINDING')
    spec=value['scientific_environment'];environment.environment_validate(spec)
    if (spec['python_executable']!=selected['python_executable'] or spec['wheels']!=selected['wheels']
            or spec['expected']['packages']!=selected['packages'] or spec['expected']['cuda'] is None
            or value['environment_sha256']!=digest(encoded(spec['expected']))):raise ValueError('CLOSURE_RESULT_ENVIRONMENT')
    checks=value['checks']
    if (not isinstance(checks,dict) or set(checks)!={'imports','trainers','reader','console_help'}
            or checks['imports']!={name:name for name in IMPORTS.values()}
            or checks['trainers']!={name:PARAMETERS for name in TRAINERS}
            or checks['reader']!='SimpleITKIO' or not isinstance(checks['console_help'],dict)
            or set(checks['console_help'])!=set(CONSOLES)):raise ValueError('CLOSURE_RESULT_CHECKS')
    for record in checks['console_help'].values():
        if (not isinstance(record,dict) or set(record)!={'exit_code','stdout','stderr','usage_seen'}
                or type(record['exit_code']) is not int or record['exit_code']!=0 or record['usage_seen'] is not True):
            raise ValueError('CLOSURE_RESULT_HELP')
        for stream in ('stdout','stderr'):
            item=record[stream]
            if (not isinstance(item,dict) or set(item)!={'sha256','bytes'}
                    or not isinstance(item['sha256'],str) or not re.fullmatch('[0-9a-f]{64}',item['sha256'])
                    or type(item['bytes']) is not int or not 0<=item['bytes']<=MAX_CAPTURE):
                raise ValueError('CLOSURE_RESULT_HELP')
        if sum(record[k]['bytes'] for k in ('stdout','stderr'))==0:raise ValueError('CLOSURE_RESULT_HELP')
    return value


def run(selected,wheels,output,binding_sha256):
    """No SDK, dataset paths, dependency resolution or caller-supplied commands."""
    os.umask(0o077);requirements=selection(selected)
    if (not isinstance(binding_sha256,str) or not re.fullmatch('[0-9a-f]{64}',binding_sha256)
            or Path(sys.executable).resolve()!=Path(selected['python_executable']).resolve()):
        raise ValueError('CLOSURE_INTERPRETER_OR_BINDING')
    wheels=private(wheels,True);verify_wheels(wheels,selected['wheels'])
    output=Path(output)
    if output.exists() or output.is_symlink():raise ValueError('CLOSURE_EXISTING_ATTEMPT_NO_RETRY')
    private(output.parent,True);output.mkdir(mode=0o700)
    (output/'selection.json').write_bytes(encoded(selected))
    env=environment.environment_install(requirements,wheels,selected['wheels'],output,binding_sha256,verify_wheels)
    # Fixed empty roots prevent help/import checks discovering ambient datasets.
    for key in ('nnUNet_raw','nnUNet_preprocessed','nnUNet_results','MPLCONFIGDIR','XDG_CACHE_HOME'):
        empty=output/key;empty.mkdir(mode=0o700);env[key]=str(empty)
    env['CUDA_VISIBLE_DEVICES']=''
    actual=environment.environment_observe(selected['packages'],True,env)
    if (set(actual)!={'python','cuda','packages'} or actual['python']!=sys.version
            or actual['packages']!=selected['packages'] or actual['cuda'] is None):
        raise ValueError('CLOSURE_OBSERVED_IDENTITY')
    spec={'schema':'offline-scientific-python/v1','python_executable':selected['python_executable'],
          'expected':actual,'wheels':selected['wheels']};environment.environment_validate(spec)
    raw,_=capture([sys.executable,'-B','-s','-c',PROBE],env,output,'imports')
    checks=strict(raw['stdout'])
    if not isinstance(checks,dict) or set(checks)!={'imports','trainers','reader'}:
        raise ValueError('CLOSURE_IMPORT_RESULT')
    checks['console_help']={}
    target=Path(env['PYTHONPATH']);scripts=target/'bin'
    for name in CONSOLES:
        executable=scripts/name
        if executable.is_symlink() or not executable.is_file() or not os.access(executable,os.X_OK):
            raise ValueError('CLOSURE_CONSOLE_MISSING:'+name)
        raw,metadata=capture([str(executable),'--help'],env,output,name)
        usage=b'usage:' in (raw['stdout']+raw['stderr']).lower()
        if not usage:raise ValueError('CLOSURE_HELP_USAGE_MISSING:'+name)
        checks['console_help'][name]={**metadata,'usage_seen':usage}
    result={'schema':RESULT,'binding_sha256':binding_sha256,'selection_sha256':digest(encoded(selected)),
        **pins(),'scientific_environment':spec,'environment_sha256':digest(encoded(actual)),
        'checks':checks,'patient_computation':False,'gpu_verified':False}
    validate_result(encoded(result),selected,binding_sha256)
    with (output/'result.json').open('xb') as out:out.write(encoded(result))
    for path in output.rglob('*'):private(path,path.is_dir())
    return result


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--selection',required=True)
    parser.add_argument('--wheels',required=True);parser.add_argument('--output',required=True)
    parser.add_argument('--binding',required=True);args=parser.parse_args()
    path=private(args.selection)
    if path.stat().st_size>MAX_CAPTURE:raise ValueError('CLOSURE_SELECTION_BOUND')
    selected=strict(path.read_bytes())
    result=run(selected,args.wheels,args.output,args.binding)
    sys.stdout.buffer.write(encoded(result))

if __name__=='__main__':main()
