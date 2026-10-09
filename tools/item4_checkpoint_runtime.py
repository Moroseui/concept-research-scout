"""Connect the approved native checkpoint continuation without changing scientific identity."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
CHANGE='item4-fit-stdin-recovery-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-closed-attempt-billing-20261009/tools/item4_closed_billing_runtime.py')
PRIOR_SHA='a3e0945e4511c2fe7367bd058cf08b1a5e87386f85c94e2cc08fa4aa795cc7f7'
PRIOR_REVIEW='08ba6c4fa437586c0cd8a44e9fb627a735c6827ecb45fe5333587053fff1cdc5'
FILES=('tools/item4_checkpoint_runtime.py', 'tools/install_item4_checkpoint.py', 'orchestrator/item4_checkpoint_connection.py', 'orchestrator/modal_item4_budget.py', 'orchestrator/modal_executor.py', 'docs/ITEM4_CHECKPOINT_CONNECTION.json', 'orchestrator/item4_closed_asset_billing.py', 'orchestrator/item4_benchmark_handoff.py', 'orchestrator/modal_terminal_cost.py', 'docs/ITEM4_CLOSED_EMPTY_ASSETS.json', 'docs/ITEM4_BENCHMARK_HANDOFF_PRIVATE.json', 'orchestrator/modal_fit_stdin.py', 'orchestrator/modal_item4_provider.py', 'orchestrator/item4_fit_transport_recovery.py', 'orchestrator/experiment_dispatch.py', 'docs/ITEM4_FIT_TRANSPORT_RECOVERY_PRIVATE.json')


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
    units=[unit] # Existing reviewed retention timer remains the sole cleanup owner.
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
        for name in ('effective','record','exposure'):
            function=getattr(candidate_cost,name);require(not function.__code__.co_freevars,'COST_CLOSURE')
            getattr(modal_terminal_cost,name).__code__=function.__code__
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
        for name in ('modal_fit_stdin','item4_fit_transport_recovery'):
            loaded=module('orchestrator.'+name,ROOT/('orchestrator/'+name+'.py'))
            setattr(orchestrator,name,loaded)
        recovery=orchestrator.item4_fit_transport_recovery;recovery.authority=authority;recovery.contract()
        from orchestrator import modal_item4_provider,experiment_dispatch
        expected_sources={'orchestrator.modal_item4_provider':'307bf7cdda63948531ceb4241a387a6d9ce9c7873bed61eaf1b01ec826ffc854',
            'orchestrator.experiment_dispatch':'9acf06307fb561593c4b20eee18c6b971597751b346189533fc8d9374f8c7be7'}
        for target,names in ((modal_item4_provider,('preflight','launch')),(experiment_dispatch,('load',))):
            require(sha(trusted(Path(target.__file__)).read_bytes())==expected_sources[target.__name__],'PRIOR_TRANSPORT_SOURCE')
            candidate=module('_fit_transport_'+target.__name__.split('.')[-1],ROOT/('orchestrator/'+target.__name__.split('.')[-1]+'.py'))
            for name in names:
                function=getattr(candidate,name);require(not function.__code__.co_freevars,'TRANSPORT_CLOSURE')
                getattr(target,name).__code__=function.__code__
        return result
    prior.connect=wired
    return prior


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/FILES[0],'SERVICE_IDENTITY')
    extra={'reconcile-fit-transport'}
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
            from orchestrator import item4_fit_transport_recovery as recovery
            p=recovery.contract();sys.path.insert(0,p['runtime']['sdk_package'])
            from orchestrator.modal_provider import ModalProvider
            result=recovery.activate(driver,ModalProvider(p['runtime']))
        print(json.dumps(result,sort_keys=True))
    finally:driver.store.db.close();driver.store.batch.db.close()


if __name__=='__main__':
    os.umask(0o077);main()
