"""Connect a private invocation copy and one exact second pre-science retry."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
CHANGE='item4-closed-attempt-billing-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-private-package-staging-20261009/tools/item4_private_staging_runtime.py')
PRIOR_SHA='54773c6656d2ee63b703aeefd9a55c1f2083494cc12b5dd256d9e6a26bda9b72'
PRIOR_REVIEW='69369d365a4ff9dae5e85cc464e8bbd3758dace82f1e1c601124536cf3256a92'
FILES=('tools/item4_closed_billing_runtime.py', 'tools/install_item4_closed_billing.py', 'orchestrator/item4_closed_attempt_billing.py', 'orchestrator/modal_terminal_cost.py', 'docs/ITEM4_CLOSED_BILLING.json')


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
    route=module('_closed_billing_prior',PRIOR)
    prior=route.connect();original=prior.connect
    def wired():
        result=original()
        require(route.authority()['report_sha256']==PRIOR_REVIEW,'PRIOR_APPROVAL')
        authority()
        import orchestrator
        from orchestrator import modal_terminal_cost
        billing=module('orchestrator.item4_closed_attempt_billing',ROOT/'orchestrator/item4_closed_attempt_billing.py')
        orchestrator.item4_closed_attempt_billing=billing
        billing.contract()
        candidate=module('_confirmed_closed_cost',ROOT/'orchestrator/modal_terminal_cost.py')
        # Keep the existing record(), every old stop check and every cap unchanged.
        for name in ('effective','exposure'):
            replacement=getattr(candidate,name)
            require(not replacement.__code__.co_freevars,'COST_CLOSURE')
            existing=getattr(modal_terminal_cost,name)
            existing.__code__=replacement.__code__
            existing.__kwdefaults__=replacement.__kwdefaults__
        return result
    prior.connect=wired
    return prior


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/FILES[0],'SERVICE_IDENTITY')
    require(argv and argv[0] in {'verify','reconcile-billing','advance','prepare-execution','measure-benchmark'},'ACTION_SCOPE')
    prior=connect()
    if argv[0]!='reconcile-billing':return prior.main(argv)
    require(len(argv)==1,'RECONCILIATION_ARGUMENTS')
    c,policy,original,evidence,base,fresh=prior.connect()
    from orchestrator import item4_closed_attempt_billing as billing,experiment_approval as approval
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    driver=ExperimentDriver(c.LANE)
    try:
        with lock(driver.state/'driver.lock'):
            driver.guard();c.originals(driver,*original);base.connect_evidence(driver,c,evidence)
            value=driver.current();require(value['phase']=='EXECUTE_EXPERIMENT','EXECUTION_PHASE')
            require('validation_admission' in approval.verify(driver,value),'VALIDATION_ONLY')
            require(driver.config['run_id']==next(iter(billing.contract()['selected'].values()))['row']['run'],'RUN_SCOPE')
            result=billing.record(driver.store.batch)
        print(json.dumps(result,sort_keys=True))
    finally:driver.store.db.close();driver.store.batch.db.close()


if __name__=='__main__':
    os.umask(0o077);main()
