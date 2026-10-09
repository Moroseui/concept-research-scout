"""Held, independently reviewed connection for one exact pre-science fresh start."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

CHANGE='item4-preprocessing-root-repair-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-spending-module-20261009/tools/item4_execution_billing.py')
PRIOR_SHA='e4725d91be1de3c8f5eea191a73b19218321e54ea72fd448ccc44b1f7e550dcb'
PRIOR_REVIEW='3e3569d6f4284987e6dd96d71480f0764e2e82d825b27134386f4c66d6cbcda8'
FILES=('tools/item4_preprocessing_fresh_runtime.py','tools/install_item4_preprocessing_fresh.py',
    'orchestrator/item4_preprocessing_fresh_start.py','orchestrator/modal_volume_path.py',
    'orchestrator/modal_assets.py','orchestrator/modal_executor.py','orchestrator/modal_item4_budget.py',
    'orchestrator/modal_preprocessing_provider.py','docs/ITEM4_FRESH_START_CHECKPOINT.json',
    'docs/ITEM4_FRESH_RUNTIME.json')


def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('FRESH_RUNTIME_'+why)
def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        st=p.lstat();require(not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'TRUSTED_SOURCE')
    return path
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m


def authority():
    from orchestrator.autonomy_review import verify_result
    installed=json.loads(trusted(RECORD/'installed.json').read_bytes())
    result=verify_result(trusted(RECORD/'review'))
    manifest=json.loads(trusted(RECORD/'review/packet-manifest.json').read_bytes())
    require(result['verdict']=='APPROVE' and result['change_id']==CHANGE and
        result['source_sha']==installed['source']==manifest['source_sha'] and
        result['report_sha256']==installed['review_sha256'],'GENUINE_APPROVAL')
    require(set(installed['files'])==set(FILES),'INSTALL_MEMBERS')
    for name in FILES:
        require(sha(trusted(ROOT/name).read_bytes())==installed['files'][name]==manifest['source_files'][name],'SOURCE_CHANGED')
    require(Path(__file__).resolve()==ROOT/FILES[0],'EXECUTED_SOURCE')
    unit=Path('/etc/systemd/system')/('research-'+CHANGE+'.service')
    require(installed['units']=={str(unit):sha(trusted(unit).read_bytes())},'UNIT_CHANGED')
    return result


def connect():
    require(sha(trusted(PRIOR).read_bytes())==PRIOR_SHA,'PRIOR_SOURCE_CHANGED')
    prior=module('_fresh_prior_billing',PRIOR)
    base=module('_fresh_prior_validation',prior.PRIOR)
    c,policy,original,evidence=prior.connect(base.load)
    require(prior.authority()['report_sha256']==PRIOR_REVIEW,'PRIOR_APPROVAL')
    authority()
    import orchestrator
    fresh=module('orchestrator.item4_preprocessing_fresh_start',ROOT/'orchestrator/item4_preprocessing_fresh_start.py')
    orchestrator.item4_preprocessing_fresh_start=fresh;fresh.authority=authority;fresh.contract()
    volume=module('orchestrator.modal_volume_path',ROOT/'orchestrator/modal_volume_path.py')
    orchestrator.modal_volume_path=volume
    from orchestrator import modal_executor,modal_item4_budget,modal_assets,experiment_dispatch,modal_preprocessing_provider,preprocessing_continuation
    executor=module('_fresh_job_identity',ROOT/'orchestrator/modal_executor.py')
    require(not executor.item4_job.__code__.co_freevars,'JOB_CLOSURE')
    modal_executor.item4_job.__code__=executor.item4_job.__code__
    budget=module('_fresh_budget',ROOT/'orchestrator/modal_item4_budget.py')
    require(not budget.reserve.__code__.co_freevars,'BUDGET_CLOSURE')
    modal_item4_budget.reserve.__code__=budget.reserve.__code__
    assets=module('_fresh_package_upload',ROOT/'orchestrator/modal_assets.py')
    modal_assets.prepare_package=assets.prepare_package;experiment_dispatch.prepare_package=assets.prepare_package
    observed=module('_fresh_observation',ROOT/'orchestrator/modal_preprocessing_provider.py')
    modal_preprocessing_provider.exists=observed.exists
    previous=preprocessing_continuation.resolve
    def resolve(driver,value,selected):return fresh.resolve(driver,value,previous(driver,value,selected))
    preprocessing_continuation.resolve=resolve
    return c,policy,original,evidence,base,fresh


def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['verify','activate','advance','prepare-execution','measure-benchmark'])
    parser.add_argument('--jobs');parser.add_argument('--destination');args=parser.parse_args(argv)
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/FILES[0],'SERVICE_IDENTITY')
    c,policy,original,evidence,base,fresh=connect()
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    from orchestrator import experiment_approval as approval
    driver=ExperimentDriver(c.LANE)
    try:
        with lock(driver.state/'driver.lock'):
            driver.guard();c.originals(driver,*original);base.connect_evidence(driver,c,evidence)
            value=driver.current();require(value['phase']=='EXECUTE_EXPERIMENT','EXECUTION_PHASE')
            require('validation_admission' in approval.verify(driver,value),'VALIDATION_ONLY')
            if args.action=='verify':result={'status':'VERIFIED_HELD','model_calls':0,'provider_calls':0}
            elif args.action=='activate':
                p=fresh.contract();runtime=dict(p['new_runtime']);runtime['package_volume_id']=json.loads(p['old_row']['binding'])['package_volume_id']
                require(sha(fresh.encoded(runtime))==json.loads(p['old_row']['binding'])['runtime_sha256'],'OLD_RUNTIME')
                sys.path.insert(0,runtime['sdk_package'])
                from orchestrator.modal_provider import ModalProvider
                result=fresh.activate(driver,ModalProvider(runtime))
            elif args.action=='advance':
                require(value.get('preprocessing_fresh_start')==fresh.marker(fresh.contract()),'ACTIVATION_REQUIRED')
                result=driver._advance()
            elif args.action=='measure-benchmark':
                from orchestrator.experiment_projection import produce
                result=produce(driver,value,kind='hardware')
            else:
                from orchestrator import experiment_provisioning as provisioning,private_records as pr
                from orchestrator.review_contract import strict_json
                require(args.jobs is not None and args.destination is not None,'PREPARATION_ARGUMENTS')
                result=provisioning.prepare(driver,value,strict_json(pr.check(args.jobs).read_bytes()),args.destination,kind='fit')
        print(json.dumps(result,sort_keys=True))
    finally:driver.store.db.close();driver.store.batch.db.close()

if __name__=='__main__':
    os.umask(0o077);main()
