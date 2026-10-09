"""Connect the approved native checkpoint continuation without changing scientific identity."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
CHANGE='item4-smoke-connection-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-stage1-cap-20261009/tools/item4_stage1_cap_runtime.py')
PRIOR_SHA='66194725f74d87fa37791689a295dc25a0c1575d45b5264c5b6785ba0b99f37a'
PRIOR_REVIEW='e840553db3ca94518f41f71fb986843902dae7b7d3dd6dc33c580e1d6f88b49c'
FILES=('tools/item4_smoke_runtime.py','tools/install_item4_smoke.py','orchestrator/experiment_projection.py','orchestrator/item4_smoke_handoff.py')
RETENTION=Path('/etc/systemd/system/research-item4-benchmark-timer-format-20261009-retention.service')


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
    units=[unit,RETENTION] # Same timer; cleanup now guards all package consumers.
    require(installed['units']=={str(p):sha(trusted(p).read_bytes()) for p in units},'UNIT_CHANGED')
    return result



def connect():
    require(sha(trusted(PRIOR).read_bytes())==PRIOR_SHA,'PRIOR_SOURCE_CHANGED')
    route=module('_stage1_cap_prior',PRIOR)
    prior=route.connect();original=prior.connect
    def wired():
        result=original()
        require(route.authority()['report_sha256']==PRIOR_REVIEW,'PRIOR_APPROVAL')
        authority()
        import orchestrator
        from orchestrator import experiment_projection as projection
        candidate=module('_smoke_projection',ROOT/'orchestrator/experiment_projection.py')
        projection.timing_view=candidate.timing_view
        require(not candidate.timings.__code__.co_freevars,'TIMING_CLOSURE')
        projection.timings.__code__=candidate.timings.__code__
        helper=module('orchestrator.item4_smoke_handoff',ROOT/'orchestrator/item4_smoke_handoff.py')
        orchestrator.item4_smoke_handoff=helper
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
    expected=['smoke-A1_repeat','smoke-A1_repeat2']
    require(proposal['schema']=='item4-base-smoke-runtime-proposal/v1' and proposal['provider_calls']==0 and
        len(proposal['contract_sha256'])==64 and
        [x['fit'] for x in proposal['rows']]==expected,'EXPORT_SCOPE')
    target=RECORD/'runtimes';require(not target.exists() and not target.is_symlink(),'RUNTIMES_EXIST_RECONCILE')
    installer=module('_benchmark_publisher',ROOT/'tools/install_item4_smoke.py')
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
    extra={'prepare-smoke-assets','export-runtimes','cleanup-shared-package'}
    require(argv and argv[0] in {'verify','advance','prepare-execution','measure-benchmark'}|extra,'ACTION_SCOPE')
    prior=connect()
    if argv[0] not in extra:return prior.main(argv)
    require(len(argv)==1,'ACTION_ARGUMENTS')
    c,policy,original,evidence,base,fresh=prior.connect()
    from orchestrator import item4_smoke_handoff as handoff
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    from orchestrator.modal_budget import ComputeAccounts
    driver=ExperimentDriver(c.LANE)
    try:
        with lock(driver.state/'driver.lock'):
            driver.guard();c.originals(driver,*original);base.connect_evidence(driver,c,evidence)
            accounts=ComputeAccounts(driver.store.batch);value=driver.current()
            if argv[0]=='cleanup-shared-package':
                p=handoff.base.contract();sys.path.insert(0,p['preprocessing_runtime']['sdk_package'])
                from orchestrator.modal_provider import ModalProvider
                result=handoff.cleanup_shared(accounts,ModalProvider(p['preprocessing_runtime']))
            elif argv[0]=='export-runtimes':result=handoff.export_runtimes(driver,value,accounts)
            else:
                p=handoff.context(driver,value)
                sys.path.insert(0,p['preprocessing_runtime']['sdk_package'])
                from orchestrator.modal_provider import ModalProvider
                result=handoff.prepare_assets(driver,value,accounts,ModalProvider(p['preprocessing_runtime']))
        print(json.dumps(result,sort_keys=True))
    finally:driver.store.db.close();driver.store.batch.db.close()

if __name__=='__main__':
    os.umask(0o077);main()
