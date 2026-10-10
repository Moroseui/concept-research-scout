"""Separately approved continuation of the unchanged installed preparation engine."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

CHANGE='preparation-branch-admission-repair-20261010'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
ORIGINAL_ROOT=Path('/opt/research-system/manual-repair-helpers/preparation-and-cap-repair-20261010')
ORIGINAL_RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/preparation-and-cap-repair-20261010')
ORIGINAL_SOURCE='304cae4aa12d53eb99254499950eec4e71df8075'
LANES=('aggregate_analysis','colab_preparation')

def require(ok,why):
    if not ok:raise ValueError('PREPARATION_BRANCH_REPAIR_'+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def trusted(path):
    p=Path(path)
    for q in [p,*p.parents]:
        s=q.lstat();require(not q.is_symlink() and s.st_uid==0 and not s.st_mode&0o022,'TRUSTED_PATH')
    return p

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,trusted(path))
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def authority():
    from orchestrator.autonomy_review import verify_result
    require(Path(__file__).resolve()==ROOT/'tools/preparation_branch_repair_runtime.py','EXECUTED_PATH')
    approval=verify_result(trusted(RECORD/'review'))
    manifest=json.loads(trusted(RECORD/'review/packet-manifest.json').read_bytes())
    receipt=json.loads(trusted(RECORD/'installed.json').read_bytes())
    require(approval['verdict']=='APPROVE' and not approval.get('findings') and approval['change_id']==CHANGE,'GENUINE_APPROVAL')
    require(receipt['root']==str(ROOT) and receipt['source']==approval['source_sha'] and receipt['review_sha256']==approval['report_sha256'] and receipt['status']=='INSTALLED_HELD','INSTALL_BINDING')
    require(receipt['files']==manifest['source_files'],'EXACT_REVIEWED_COMPONENT')
    for name,pin in manifest['source_files'].items():
        require(sha(trusted(ROOT/name).read_bytes())==pin,'REVIEWED_SOURCE_CHANGED')
    old=verify_result(trusted(ORIGINAL_RECORD/'review'))
    require(old['source_sha']==ORIGINAL_SOURCE and old['verdict']=='APPROVE','ORIGINAL_APPROVAL')
    original=json.loads(trusted(ORIGINAL_RECORD/'review/packet-manifest.json').read_bytes())
    for name,pin in original['source_files'].items():
        require(sha(trusted(ORIGINAL_ROOT/name).read_bytes())==pin,'ORIGINAL_ENGINE_CHANGED')
    return approval,manifest,receipt

def connect():
    approval,manifest,receipt=authority()
    import orchestrator
    require(Path(orchestrator.__file__).resolve().parent==ORIGINAL_ROOT/'orchestrator','ORIGINAL_IMPORT_ROOT')
    proof_module=load('_reviewed_preparation_premodel_recovery',ROOT/'tools/preparation_premodel_recovery.py')
    proof=proof_module.load_verified_proof(RECORD/'review')
    pi=load('orchestrator.preparation_interleaving',ROOT/'orchestrator/preparation_interleaving.py')
    orchestrator.preparation_interleaving=pi
    pi.configure_premodel(proof)
    original=load('_original_preparation_scientific_runtime',ORIGINAL_ROOT/'tools/preparation_scientific_runtime.py')
    require(original.ROOT==ORIGINAL_ROOT and original.RECORD==ORIGINAL_RECORD,'ORIGINAL_RUNTIME_PATHS')
    from orchestrator import analysis_driver
    pi.install_driver_hook(analysis_driver,proof)
    return original

def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['verify','init','advance']);parser.add_argument('--lane',choices=LANES)
    args=parser.parse_args(argv)
    require(os.getuid()==os.getgid()==1003,'SERVICE_ACCOUNT')
    require((args.action=='verify')==(args.lane is None),'ACTION_LANE')
    original=connect()
    command=[args.action,'--scope',str(ORIGINAL_RECORD/'preparation-interleaving.json'),'--review-report',str(ORIGINAL_RECORD/'review/report.md')]
    if args.lane is not None:command+=['--lane',args.lane]
    return original.main(command)

if __name__=='__main__':
    os.umask(0o077);print(json.dumps(main(),sort_keys=True))
