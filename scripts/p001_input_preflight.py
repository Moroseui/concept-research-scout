#!/usr/bin/env python3
"""P001 admission-only preflight: no prediction, labels, launch or new backend.

Use on the authorized CPU Colab runtime, with the existing archive and frozen
scientific checkout. Preserve all originals in a fresh private attempt directory.
NIfTI scaling/header observations alone cannot establish derivative units.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

APPROVAL_SHA = '56fa21d431ad60f5c6241d059e144bf7de0c2956eda85cf871c6955498c5c643'
RUNNER_SHA = 'd54e3ea5c45c0d47fe8bace014058e1660d92b72abc36cc2fdc077acae3d47b0'
ARCHIVE_SIZE = 99014629647
ARCHIVE_MD5 = '36ae28b9a17f7340b8bbef62b595cb57'
MAX_SECONDS = 5400


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest()


def admission_members(selected):
    """Select only the approved runner's admission side, never open its labels."""
    if len(selected)!=99:raise ValueError('PREFLIGHT_ELIGIBLE_COUNT')
    entries=[]
    for case,pair in sorted(selected.items()):
        entry=pair['tmax'];p=Path(entry['path'])
        if p.is_absolute() or '..' in p.parts or 'ses-01' not in p.parts or not p.name.endswith('_tmax.nii.gz'):
            raise ValueError('PREFLIGHT_ADMISSION_MEMBER')
        entries.append((case,entry))
    if len({e['path'] for _,e in entries})!=99:raise ValueError('PREFLIGHT_DUPLICATE_MEMBER')
    return entries


def header_record(path):
    import nibabel as nib
    image=nib.load(str(path))  # proxy/header only: do not materialize voxels
    slope=float(image.dataobj.slope);inter=float(image.dataobj.inter)
    if len(image.shape)!=3 or not math.isfinite(slope) or not math.isfinite(inter):
        raise ValueError('PREFLIGHT_HEADER_INVALID')
    return {'shape':list(image.shape),'dtype':str(image.get_data_dtype()),
            'proxy_slope':slope,'proxy_intercept':inter,'xyzt_units':list(image.header.get_xyzt_units())}


def reconcile_runtime(execution_root, proc_root=Path('/proc')):
    """Metadata only. Incomplete visibility never proves that no job started."""
    active = 0
    complete = True
    for path in proc_root.glob('[0-9]*/cmdline'):
        try:
            args = path.read_bytes().split(b'\0')
            if any(b'/experiments/P001/run.py' in arg or (execution_root.name+'.worker/launch.py').encode() in arg for arg in args):
                active += 1
        except FileNotFoundError:
            continue
        except OSError:
            complete = False
    private = execution_root.with_name(execution_root.name+'.private')
    worker = execution_root.with_name(execution_root.name+'.worker')
    present = any(p.exists() for p in [execution_root, private, worker])
    return {'process_scan_complete': complete, 'matching_processes': active,
            'existing_execution_paths': present,
            'disposition': 'HOLD_RECONCILE_EXISTING_OR_UNCERTAIN_EXECUTION'
                if active or present or not complete else 'NO_MATCH_IN_CHECKED_RUNTIME_AND_PATHS'}


def run(a):
    if not os.environ.get('COLAB_RELEASE_TAG') or shutil.which('nvidia-smi'):
        raise ValueError('AUTHORIZED_CPU_COLAB_REQUIRED')
    observation=reconcile_runtime(a.execution_root)
    if observation['disposition']!='NO_MATCH_IN_CHECKED_RUNTIME_AND_PATHS':raise ValueError('PREFLIGHT_EXISTING_EXECUTION_RECONCILIATION_REQUIRED')
    if not shutil.which('7z'):raise ValueError('PREFLIGHT_7Z_REQUIRED')
    if digest(a.approval)!=APPROVAL_SHA:raise ValueError('PREFLIGHT_OPERATOR_BINDING')
    source=a.source_root/'campaigns/isles24-pilot/experiments/P001/run.py'
    if digest(source)!=RUNNER_SHA:raise ValueError('PREFLIGHT_FROZEN_SOURCE')
    import numpy,nibabel
    if numpy.__version__!='2.3.3' or nibabel.__version__!='5.3.2':raise ValueError('PREFLIGHT_ENVIRONMENT_PIN')
    if a.archive.is_symlink() or not a.archive.is_file():raise ValueError('PREFLIGHT_ARCHIVE_UNAVAILABLE')
    if not a.attempt.is_absolute() or a.attempt.exists():raise ValueError('PREFLIGHT_FRESH_ATTEMPT_REQUIRED')
    spec=importlib.util.spec_from_file_location('frozen_p001_preflight',source)
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    eligible=admission_members(runner.selection())
    # One lexical eligible admission sample resolves header/decoder readiness
    # without duplicating full scientific staging. No outcome-derived selection.
    selected=eligible[:1]
    need=sum(int(e['size']) for _,e in selected)+512*1024*1024
    if shutil.disk_usage(a.attempt.parent).free<need:raise ValueError('PREFLIGHT_DISK_CAPACITY')
    os.umask(0o077);a.attempt.mkdir(mode=0o700)
    started=time.monotonic()
    def save(name,value):
        with (a.attempt/name).open('x') as f:
            json.dump(value,f,indent=2,allow_nan=False);f.flush();os.fsync(f.fileno())
    save('binding.json',{'runner_sha256':RUNNER_SHA,'approval_sha256':APPROVAL_SHA,'archive':str(a.archive),'source_root':str(a.source_root),'pid':os.getpid(),'status':'STARTED','patient_launch':False,'execution_reconciliation':observation})
    result={'status':'FAILED','prediction_executed':False,'labels_opened':False,'reserved_access':False}
    try:
        if a.archive.stat().st_size!=ARCHIVE_SIZE:raise ValueError('PREFLIGHT_ARCHIVE_SIZE')
        h=hashlib.md5();count=0
        with a.archive.open('rb') as f:
            for block in iter(lambda:f.read(8<<20),b''):
                h.update(block);count+=len(block)
                if time.monotonic()-started>MAX_SECONDS:raise TimeoutError('PREFLIGHT_TIME_LIMIT')
        if count!=ARCHIVE_SIZE or h.hexdigest()!=ARCHIVE_MD5:raise ValueError('PREFLIGHT_ARCHIVE_CHECKSUM')
        staged=a.attempt/'admission-staging';staged.mkdir()
        with (a.attempt/'extraction.console.log').open('xb') as log:
            subprocess.run(['7z','x',str(a.archive),'-o'+str(staged),'-y','-bb0',*[e['path'] for _,e in selected]],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=max(1,MAX_SECONDS-(time.monotonic()-started)))
        headers={}
        for case,entry in selected:
            if time.monotonic()-started>MAX_SECONDS:raise TimeoutError('PREFLIGHT_TIME_LIMIT')
            path,sha=runner.verify_file(staged,entry)
            headers[case]={'sha256':sha,'header':header_record(path)}
        save('admission_headers.private.json',headers)
        result.update(status='INPUT_INTEGRITY_AND_HEADERS_VERIFIED',archive_size=count,archive_md5=h.hexdigest(),eligible_cohort_verified=99,admission_members_checked=1,selection_rule='first_lexical_eligible_id_no_outcome_selection',headers_sha256=digest(a.attempt/'admission_headers.private.json'),unit_semantics='HEADER_EVIDENCE_ONLY_REQUIRES_RELEASE_PROVENANCE_ASSESSMENT',launch_authorized=False)
    except Exception as error:
        result['failure_type']=type(error).__name__
        # Exception text and subprocess streams may contain private member names.
        with (a.attempt/'failure.private.txt').open('x') as f:f.write(str(error))
    finally:
        result['elapsed_seconds']=time.monotonic()-started
        save('receipt.json',result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root',type=Path,required=True);p.add_argument('--approval',type=Path,required=True)
    p.add_argument('--archive',type=Path,required=True);p.add_argument('--attempt',type=Path,required=True)
    p.add_argument('--execution-root',type=Path,required=True)
    a=p.parse_args()
    try:result=run(a)
    except Exception as e:result={'status':'ATTEMPT_EVIDENCE_WRITE_FAILED' if a.attempt.exists() else 'REFUSED_BEFORE_ATTEMPT','failure_type':type(e).__name__,'failure_code':str(e) if str(e).startswith(('PREFLIGHT_','AUTHORIZED_CPU_')) else 'PRIVATE_DIAGNOSTIC_REQUIRED','patient_launch':False}
    print(json.dumps(result))
    return 0 if result['status']=='INPUT_INTEGRITY_AND_HEADERS_VERIFIED' else 1

if __name__=='__main__':raise SystemExit(main())
