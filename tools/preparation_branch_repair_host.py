"""Preserve the original host start/pulse checks for fixed repaired lane units."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys

def runtime():
    root=Path('/opt/research-system/manual-repair-helpers/preparation-branch-admission-repair-20261010')
    if Path(__file__).resolve()!=root/'tools/preparation_branch_repair_host.py':raise ValueError('PREPARATION_BRANCH_HOST_EXECUTED_PATH')
    path=root/'tools/preparation_branch_repair_runtime.py'
    for parent in [path,*path.parents]:
        stat=parent.lstat()
        if parent.is_symlink() or stat.st_uid!=0 or stat.st_mode&0o022:raise ValueError('PREPARATION_BRANCH_HOST_TRUSTED_PATH')
    spec=importlib.util.spec_from_file_location('_preparation_repair_authority',path)
    route=importlib.util.module_from_spec(spec);spec.loader.exec_module(route)
    return route

def connect(key,transition):
    rt=runtime();rt.require(os.getuid()==0 and sys.flags.no_user_site,'ROOT_ISOLATED_REQUIRED')
    approval,manifest,receipt=rt.authority()
    rt.require(key in rt.LANES,'NAMED_LANE')
    rt.require(Path(__file__).resolve()==rt.ROOT/'tools/preparation_branch_repair_host.py','HOST_EXECUTED_PATH')
    complete=json.loads(rt.trusted(rt.RECORD/'COMPLETE.json').read_bytes())
    rt.require(complete=={'status':'INSTALLED_HELD','source':approval['source_sha'],'scientific_calls':0,'provider_calls':0},'SERVICE_VERIFICATION_REQUIRED')
    old=rt.load('_original_preparation_host_operation',rt.ORIGINAL_ROOT/'tools/preparation_host_operation.py')
    host=old.connect(key,transition)
    frozen,_=host.authority(None)
    frozen['hashes']={**frozen['hashes'],**receipt['units'],**{str(rt.ROOT/name):pin for name,pin in receipt['files'].items()}}
    host.hashes(frozen)
    host.UNIT='research-'+rt.CHANGE+'-'+key+'.service'
    rt.require('/etc/systemd/system/'+host.UNIT in receipt['units'],'EXACT_NEW_UNIT')
    host.OPERATION_ROOT=rt.RECORD/'operations'/key/transition
    # The old starting_state closure still binds the original run, source,
    # approval and transition. Its pulse/stop/limits/hooks stay unchanged.
    host.authority=lambda review:(frozen,approval)
    return host

def status(key):
    rt=runtime();rt.require(os.getuid()==0 and sys.flags.no_user_site and key in rt.LANES,'ROOT_LANE')
    rt.authority()
    old=rt.load('_original_preparation_host_status',rt.ORIGINAL_ROOT/'tools/preparation_host_operation.py')
    value=old.status(key)
    connect(key,value['transition'])
    return value

def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['status','start','pulse']);parser.add_argument('--lane',choices=['aggregate_analysis','colab_preparation'],required=True);parser.add_argument('--transition')
    args=parser.parse_args(argv)
    if args.action=='status':
        if args.transition is not None:raise ValueError('STATUS_NO_TRANSITION')
        print(json.dumps(status(args.lane),sort_keys=True));return
    host=connect(args.lane,args.transition);rt=runtime()
    for path in [rt.RECORD/'operations',rt.RECORD/'operations'/args.lane,host.OPERATION_ROOT]:
        if not path.exists():rt.trusted(path.parent);path.mkdir(mode=0o700);path.chmod(0o700)
        rt.trusted(path)
    prior=sys.argv
    try:
        sys.argv=[str(__file__),args.action,'--stage','author','--review',str(rt.RECORD/'review')]
        return host.main()
    finally:sys.argv=prior

if __name__=='__main__':
    os.umask(0o077);main()
