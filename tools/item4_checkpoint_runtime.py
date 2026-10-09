"""Connect the approved native checkpoint continuation without changing scientific identity."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
CHANGE='item4-checkpoint-sdk-bootstrap-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-closed-attempt-billing-20261009/tools/item4_closed_billing_runtime.py')
PRIOR_SHA='a3e0945e4511c2fe7367bd058cf08b1a5e87386f85c94e2cc08fa4aa795cc7f7'
PRIOR_REVIEW='08ba6c4fa437586c0cd8a44e9fb627a735c6827ecb45fe5333587053fff1cdc5'
FILES=('tools/item4_checkpoint_runtime.py','tools/install_item4_checkpoint.py','orchestrator/item4_checkpoint_connection.py','orchestrator/modal_item4_budget.py','orchestrator/modal_executor.py','docs/ITEM4_CHECKPOINT_CONNECTION.json')


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
    route=module('_checkpoint_prior',PRIOR)
    prior=route.connect();original=prior.connect
    def wired():
        result=original()
        require(route.authority()['report_sha256']==PRIOR_REVIEW,'PRIOR_APPROVAL')
        authority()
        import orchestrator
        from orchestrator import preprocessing_continuation,modal_item4_budget,modal_executor
        helper=module('orchestrator.item4_checkpoint_connection',ROOT/'orchestrator/item4_checkpoint_connection.py')
        orchestrator.item4_checkpoint_connection=helper;helper.authority=authority
        cfg,_,_=helper.contract()
        native_path=trusted(Path(preprocessing_continuation.__file__))
        require(sha(native_path.read_bytes())==cfg['native_resolve_sha256'],'NATIVE_CONTINUATION_SOURCE')
        native=module('_native_checkpoint_continuation',native_path)
        before=preprocessing_continuation.resolve
        def resolve(driver,value,selected):
            return helper.resolve(driver,value,selected,before,native.resolve)
        preprocessing_continuation.resolve=resolve
        require(sha(trusted(Path(modal_item4_budget.__file__)).read_bytes())==cfg['prior_budget_sha256'],
            'PRIOR_BUDGET_SOURCE')
        candidate=module('_checkpoint_budget',ROOT/'orchestrator/modal_item4_budget.py')
        require(not candidate.reserve.__code__.co_freevars,'BUDGET_CLOSURE')
        modal_item4_budget.reserve.__code__=candidate.reserve.__code__
        modal_item4_budget.reserve.__kwdefaults__=candidate.reserve.__kwdefaults__
        candidate_executor=module('_checkpoint_executor',ROOT/'orchestrator/modal_executor.py')
        require(not candidate_executor.item4_job.__code__.co_freevars,'IDENTITY_CLOSURE')
        modal_executor.item4_job.__code__=candidate_executor.item4_job.__code__
        return result
    prior.connect=wired
    return prior

def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/FILES[0],'SERVICE_IDENTITY')
    require(argv and argv[0] in {'verify','reconcile-checkpoint','advance','prepare-execution','measure-benchmark'},'ACTION_SCOPE')
    prior=connect()
    if argv[0]!='reconcile-checkpoint':return prior.main(argv)
    require(len(argv)==1,'RECONCILIATION_ARGUMENTS')
    c,policy,original,evidence,base,fresh=prior.connect()
    from orchestrator import item4_checkpoint_connection as helper,experiment_approval as approval
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    driver=ExperimentDriver(c.LANE)
    try:
        with lock(driver.state/'driver.lock'):
            driver.guard();c.originals(driver,*original);base.connect_evidence(driver,c,evidence)
            value=driver.current();require(value['phase']=='EXECUTE_EXPERIMENT','EXECUTION_PHASE')
            require('validation_admission' in approval.verify(driver,value),'VALIDATION_ONLY')
            # Same hash-bound SDK selection and unchanged import verifier used
            # by the existing provider; cold CLI must not depend on a caller's path.
            _,observed,_=helper.contract()
            sys.path.insert(0,observed['runtime']['sdk_package'])
            result=helper.reconcile(driver,value)
        print(json.dumps(result,sort_keys=True))
    finally:driver.store.db.close();driver.store.batch.db.close()

if __name__=='__main__':
    os.umask(0o077);main()
