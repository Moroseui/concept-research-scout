"""Connect the approved native checkpoint continuation without changing scientific identity."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
CHANGE='item4-benchmark-timer-format-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-closed-attempt-billing-20261009/tools/item4_closed_billing_runtime.py')
PRIOR_SHA='a3e0945e4511c2fe7367bd058cf08b1a5e87386f85c94e2cc08fa4aa795cc7f7'
PRIOR_REVIEW='08ba6c4fa437586c0cd8a44e9fb627a735c6827ecb45fe5333587053fff1cdc5'
FILES=('tools/item4_checkpoint_runtime.py', 'tools/install_item4_checkpoint.py', 'orchestrator/item4_checkpoint_connection.py', 'orchestrator/modal_item4_budget.py', 'orchestrator/modal_executor.py', 'docs/ITEM4_CHECKPOINT_CONNECTION.json', 'orchestrator/item4_closed_asset_billing.py', 'orchestrator/item4_benchmark_handoff.py', 'orchestrator/modal_terminal_cost.py', 'docs/ITEM4_CLOSED_EMPTY_ASSETS.json', 'docs/ITEM4_BENCHMARK_HANDOFF_PRIVATE.json')


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
    units=[unit,unit.with_name('research-'+CHANGE+'-retention.service'),unit.with_name('research-'+CHANGE+'-retention.timer')]
    require(installed['units']=={str(p):sha(trusted(p).read_bytes()) for p in units},'UNIT_CHANGED')
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
        for name in ('item4_closed_asset_billing','item4_benchmark_handoff'):
            loaded=module('orchestrator.'+name,ROOT/('orchestrator/'+name+'.py'))
            setattr(orchestrator,name,loaded);loaded.contract()
        from orchestrator import modal_terminal_cost
        candidate_cost=module('_benchmark_terminal_cost',ROOT/'orchestrator/modal_terminal_cost.py')
        require(not candidate_cost.observe_billing.__code__.co_freevars,'COST_CLOSURE')
        modal_terminal_cost.observe_billing.__code__=candidate_cost.observe_billing.__code__
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

def publish_runtimes():
    """Root invokes only a read-only owner export, then freezes its exact bytes."""
    import subprocess
    require(os.geteuid()==0,'ROOT_REQUIRED')
    sys.path.insert(0,'/opt/research-system/autonomy-review/d08b91bdc1d0')
    approved=authority()
    env='RESEARCH_MANUAL_RUNTIME_CONFIG=/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json'
    result=subprocess.run(['runuser','-u','partho','--','env',env,'PYTHONDONTWRITEBYTECODE=1',
        '/usr/bin/python3','-s','-B',str(ROOT/FILES[0]),'export-runtimes'],capture_output=True)
    require(result.returncode==0,'OWNER_EXPORT_FAILED')
    proposal=json.loads(result.stdout)
    contract=json.loads(trusted(ROOT/'docs/ITEM4_BENCHMARK_HANDOFF_PRIVATE.json').read_bytes())
    require(proposal['schema']=='item4-benchmark-runtime-proposal/v1' and proposal['provider_calls']==0 and
        proposal['contract_sha256']==sha(trusted(ROOT/'docs/ITEM4_BENCHMARK_HANDOFF_PRIVATE.json').read_bytes()) and
        [x['fit'] for x in proposal['rows']]==[x['fit_id'] for x in contract['fits']],'EXPORT_SCOPE')
    target=RECORD/'runtimes';require(not target.exists() and not target.is_symlink(),'RUNTIMES_EXIST_RECONCILE')
    installer=module('_benchmark_publisher',ROOT/'tools/install_item4_checkpoint.py')
    encoded=lambda value:json.dumps(value,sort_keys=True).encode()
    jobs=[]
    for row in proposal['rows']:
        path=target/(row['fit']+'.json');raw=encoded(row['runtime'])
        installer.put(path,raw)
        jobs.append({'runtime':{'path':str(path),'sha256':sha(raw)},'binding':row['binding']})
    installer.put(target/'proposal.json',result.stdout)
    installer.put(target/'jobs.json',encoded(jobs))
    os.chown(target,0,1003);target.chmod(0o550)
    return {'status':'RUNTIME_RECORDS_PUBLISHED','jobs':str(target/'jobs.json'),
            'provider_calls':0,'scientific_acceptance':False}


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if argv==['publish-runtimes']:
        print(json.dumps(publish_runtimes(),sort_keys=True));return
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/FILES[0],'SERVICE_IDENTITY')
    extra={'reconcile-empty-assets','prepare-benchmark-assets','export-runtimes','cleanup-benchmark-package'}
    require(argv and argv[0] in {'verify','advance','prepare-execution','measure-benchmark'}|extra,'ACTION_SCOPE')
    prior=connect()
    if argv[0] not in extra:return prior.main(argv)
    require(len(argv)==1,'ACTION_ARGUMENTS')
    c,policy,original,evidence,base,fresh=prior.connect()
    from orchestrator import item4_benchmark_handoff as handoff,item4_closed_asset_billing as assets
    from orchestrator import experiment_approval as approval
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    from orchestrator.modal_budget import ComputeAccounts
    driver=ExperimentDriver(c.LANE)
    try:
        with lock(driver.state/'driver.lock'):
            driver.guard();c.originals(driver,*original);base.connect_evidence(driver,c,evidence)
            accounts=ComputeAccounts(driver.store.batch);value=driver.current()
            if argv[0]=='cleanup-benchmark-package':
                p=handoff.contract();sys.path.insert(0,p['preprocessing_runtime']['sdk_package'])
                from orchestrator.modal_provider import ModalProvider
                result=handoff.cleanup_package(accounts,ModalProvider(p['preprocessing_runtime']))
            else:
                p=handoff.contract();handoff.checked_driver(driver,value,p)
                if argv[0]=='reconcile-empty-assets':result=assets.record(accounts)
                elif argv[0]=='export-runtimes':result=handoff.export_runtimes(driver,value,accounts)
                else:
                    sys.path.insert(0,p['preprocessing_runtime']['sdk_package'])
                    from orchestrator.modal_provider import ModalProvider
                    result=handoff.prepare_assets(driver,value,accounts,ModalProvider(p['preprocessing_runtime']))
        print(json.dumps(result,sort_keys=True))
    finally:driver.store.db.close();driver.store.batch.db.close()


if __name__=='__main__':
    os.umask(0o077);main()
