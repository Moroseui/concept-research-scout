"""Fixed no-patient CPU harness adapter; scientific bytes remain author-owned.

Executed only in the independently reviewed, reserved, network-blocked Sandbox.
This file neither chooses scientific methods nor claims scientific approval.
"""
import base64
from contextlib import redirect_stdout,redirect_stderr
import gzip
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import traceback

MAX_BUNDLE=300000
MAX_COMPRESSED=90000
MAX_LOG=65536
MAX_RESULT=240000
DURABILITY_SCOPE="Real FitProgress/default fsync and reopened local synthetic filesystem; no provider Volume or production main claim."

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('NATIVE_REHEARSAL_'+why)

def unpack(encoded,selection,root):
    require(isinstance(encoded,str) and len(encoded)<=120000,'ENCODED_BOUND')
    zipped=base64.b64decode(encoded,validate=True)
    require(len(zipped)<=MAX_COMPRESSED,'COMPRESSED_BOUND')
    with gzip.GzipFile(fileobj=io.BytesIO(zipped)) as stream:
        raw=stream.read(MAX_BUNDLE+1)
    require(len(raw)<=MAX_BUNDLE and len(raw)==selection['code_bundle_bytes']
        and sha(raw)==selection['code_bundle_sha256'],'BUNDLE_BINDING')
    files=json.loads(raw)
    require(isinstance(files,dict) and set(files)==set(selection['files'])
        and 'execution.py' in files and len(files)==19,'EXACT_FILES')
    for name,body in files.items():
        relative=Path(name)
        require(isinstance(body,str) and not relative.is_absolute() and '..' not in relative.parts
            and (name=='execution.py' or re.fullmatch(r'orchestrator/[a-z_]+\.py',name)),'FILE_PATH')
        content=body.encode();require(sha(content)==selection['files'][name],'FILE_HASH')
        target=root/relative;target.parent.mkdir(exist_ok=True,mode=0o700)
        with target.open('xb') as out:out.write(content)
        target.chmod(0o400)
    return raw


def check_package(root,selection):
    require(not any(p.is_symlink() for p in root.rglob('*')),'PACKAGE_ALIAS')
    actual={p.relative_to(root).as_posix():sha(p.read_bytes()) for p in root.rglob('*') if p.is_file()}
    require(actual==selection['files'],'PACKAGE_CHANGED')


class BoundedLog(io.TextIOBase):
    def __init__(self):self.data=bytearray();self.exceeded=False
    def writable(self):return True
    def write(self,text):
        raw=text.encode('utf-8');room=MAX_LOG-len(self.data)
        self.data.extend(raw[:room])
        if len(raw)>room:
            self.exceeded=True;raise ValueError('NATIVE_REHEARSAL_LOG_BOUND')
        return len(text)
    def flush(self):pass


def progress_factory(selection):
    from orchestrator.modal_fit_progress import FitProgress
    from orchestrator import private_records as pr
    authenticated_root=None
    authenticated_inputs=None
    def factory(mount,fit,plans,environment):
        nonlocal authenticated_root,authenticated_inputs
        mount=Path(mount)
        require(mount.is_absolute() and '..' not in mount.parts
            and mount.name in {'durable','diagnostic'}
            and mount.parent.name.startswith('item4-native-synthetic-')
            and fit=='synthetic-fit','PROGRESS_SCOPE')
        # Both authored outputs are exact siblings of the same generated inputs.
        # Keep the two fits separate without accepting arbitrary subdirectories.
        pr.check(mount.parent)
        require(authenticated_root is None or mount.parent==authenticated_root,'PROGRESS_ROOT_CHANGED')
        pr.mkdir(mount,parents=False,exist_ok=True)
        # Bind actual generated fixture bytes, never production inputs.
        inputs=mount.parent/'inputs'
        require(inputs.is_dir() and not inputs.is_symlink(),'SYNTHETIC_INPUTS')
        inventory={}
        for path in sorted(inputs.rglob('*')):
            require(not path.is_symlink(),'SYNTHETIC_ALIAS')
            if path.is_file():
                name=path.relative_to(inputs).as_posix()
                require('sub-stroke' not in name,'PATIENT_PATH')
                inventory[name]={'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())}
        require(len(inventory)==893,'SYNTHETIC_INPUT_MEMBERSHIP')
        inputs_pin=sha(json.dumps(inventory,sort_keys=True,allow_nan=False).encode())
        require(authenticated_inputs is None or inputs_pin==authenticated_inputs,'SYNTHETIC_INPUTS_CHANGED')
        authenticated_root=mount.parent
        authenticated_inputs=inputs_pin
        binding={'run_id':'item4-native-synthetic','arm':'A1_repeat','fold':0,'realization':'synthetic',
            'spec_sha256':sha(b'synthetic rehearsal, no approval'),
            'code_sha256':selection['module_sha256'],
            'input_contract_sha256':inputs_pin,
            'environment_sha256':environment,'plans_sha256':plans}
        return FitProgress(mount,fit,binding)
    return factory


def validate_authored_result(result,selection):
    require(result['schema']=='item4-native-synthetic-integration/v1'
                    and result['module_sha256']==selection['module_sha256']
                    and result['preprocessed_files']==300 and result['preprocessing_reuse_verified'] is True
                    and result['gpu_verified'] is False and result['production_main_verified'] is False
                    and result['scientific_approval'] is False,'AUTHORED_RESULT')


def main(args):
    require(len(args)==3,'ARGUMENTS')
    encoded,selection_text,operation=args
    require(re.fullmatch('[0-9a-f]{64}',operation) is not None,'OPERATION_BINDING')
    selection=json.loads(selection_text)
    require(selection['entrypoint']=='native_synthetic_integration' and selection['patient_payload'] is False
        and selection['scientific_approval'] is False,'SELECTION_SCOPE')
    os.umask(0o077);sys.dont_write_bytecode=True
    log=BoundedLog();result=None;failure=None;package_unchanged=False;observed=None
    with tempfile.TemporaryDirectory(prefix='item4-reviewed-code-') as folder:
        root=Path(folder);unpack(encoded,selection,root);check_package(root,selection)
        sys.path.insert(0,str(root))
        try:
            with redirect_stdout(log),redirect_stderr(log):
                from importlib.metadata import version
                import torch
                expected=selection['environment']['expected']
                observed={'python':sys.version,'cuda':torch.version.cuda,
                    'packages':{name:version(name) for name in expected['packages']}}
                require(observed==expected and not torch.cuda.is_available(),'PINNED_CPU_ENVIRONMENT')
                spec=importlib.util.spec_from_file_location('accepted_item4_execution',root/'execution.py')
                module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                result=module.native_synthetic_integration(progress_factory(selection))
                validate_authored_result(result,selection)
        except BaseException:
            failure=traceback.format_exc(limit=20)
        finally:
            try:check_package(root,selection);package_unchanged=True
            except BaseException:failure=(failure or '')+traceback.format_exc(limit=5)
        output={'schema':'item4-native-rehearsal-result/v1','status':'PASS' if failure is None and not log.exceeded else 'FAIL',
            'operation_sha256':operation,'selection_sha256':sha(selection_text.encode()),
            'module_sha256':selection['module_sha256'],'code_bundle_sha256':selection['code_bundle_sha256'],
            'image_id':selection['image_id'],'author_call_id':selection['author_call_id'],
            'package_unchanged':package_unchanged,'observed_environment':observed,'native':result,'console':log.data.decode('utf-8',errors='replace'),
            'console_sha256':sha(bytes(log.data)),'console_truncated':log.exceeded,'failure':failure,
            'patient_data':False,'network_permission':False,'gpu':False,'scientific_approval':False,
            'durability_scope':DURABILITY_SCOPE}
        raw=json.dumps(output,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
        require(len(raw)<=MAX_RESULT,'RESULT_BOUND')
        sys.stdout.buffer.write(raw+b'\n');sys.stdout.buffer.flush()
        return 0 if output['status']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main(sys.argv[1:]))
