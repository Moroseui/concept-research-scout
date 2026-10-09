"""Explicit reviewed item6 component; unchanged original engine/owners/units."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

CHANGE='item6-contract-service-identity-20261008'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
SCIENCE='/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339'
SPENDING='/opt/research-system/manual-sprint10/research-manual-sprint10-spending-a51ac44279e4'
STATE=Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/lane')
INPUT_ROOT=Path('/opt/research-system/manual-repair-helpers/item6-input-provisioning-20261007')
DAILY=Path('/opt/research-system/manual-repair-helpers/daily-limit-and-image-probe-20261007')
MODULES=('diagnostics_native_guard','diagnostics_mount_retry','modal_executor','diagnostics_budget','diagnostics_execution')
FILES=tuple('orchestrator/'+n+'.py' for n in MODULES)+('tools/item6_native_mount_service.py','tools/install_item6_native_mount.py','docs/ITEM6_NATIVE_MOUNT_AUTHORITY_20261008.txt','docs/ITEM6_CONTRACT_RETRY_OPERATOR_APPROVAL_20261008.txt')


def require(ok,reason):
    if not ok:raise ValueError(reason)


def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        st=p.lstat();require(not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'MOUNT_COMPONENT_UNTRUSTED')
    return path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked():
    value=json.loads(trusted(RECORD/'installed.json').read_bytes())
    require(value['change']==CHANGE and value['layout']['release']==str(ROOT),'MOUNT_COMPONENT_SCOPE')
    require(json.loads(trusted(RECORD/'complete.json').read_bytes()).get('status')=='PASS','MOUNT_COMPONENT_INSTALL_INCOMPLETE')
    manifest=json.loads(trusted(RECORD/'review/packet-manifest.json').read_bytes())
    receipt=json.loads(trusted(RECORD/'review/receipt.json').read_bytes())
    require(receipt['verdict']=='APPROVE' and receipt['source_sha']==manifest['source_sha']==value['source']
        and sha(trusted(RECORD/'review/report.md'))==receipt['report_sha256']==value['review_sha256'], 'MOUNT_COMPONENT_APPROVAL')
    require(set(value['component_files'])==set(FILES),'MOUNT_COMPONENT_FILE_SET')
    for name in FILES:require(sha(trusted(ROOT/name))==manifest['source_files'][name],'MOUNT_COMPONENT_SOURCE_CHANGED')
    for path,pin in value['base_files'].items():require(sha(trusted(path))==pin,'MOUNT_COMPONENT_BASE_CHANGED')
    for path,pin in value['units'].items():require(sha(trusted(path))==pin,'MOUNT_COMPONENT_UNIT_CHANGED')
    require(Path(__file__).resolve()==ROOT/'tools/item6_native_mount_service.py','MOUNT_COMPONENT_IMPORT_PATH')
    return value


def file_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module


def load(mode):
    checked();science=mode in {'science','verify-science','state'}
    if science:
        caps=file_module('reviewed_daily_limit_component',DAILY/'tools/daily_limit_component.py')
        caps.load()
    import orchestrator
    expected=SCIENCE if science else SPENDING
    require(Path(orchestrator.__file__).resolve()==Path(expected)/'orchestrator/__init__.py','MOUNT_COMPONENT_BASE_IMPORT')
    for name in MODULES:
        fullname='orchestrator.'+name
        require(fullname not in sys.modules,'MOUNT_COMPONENT_MUST_LOAD_FIRST')
        module=file_module(fullname,ROOT/'orchestrator'/(name+'.py'));setattr(orchestrator,name,module)
    from orchestrator import diagnostics_mount_retry as retry
    return retry.permit()


def advance():
    # Existing helper and spending qualification stay active; no credential changes.
    sys.path.insert(0,str(INPUT_ROOT/'tools'))
    original=file_module('reviewed_original_item6_input_service',INPUT_ROOT/'tools/item6_input_service.py')
    original.verify_installed()
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    from orchestrator import spending_continuation as sc,diagnostics_mount_retry as retry
    from orchestrator.experiment_package import advance as execute
    driver=ExperimentDriver(STATE)
    try:
        with lock(STATE/'driver.lock'):
            driver.guard();value=driver.current()
            require(value['phase'] in {'EXECUTE_EXPERIMENT','COLLECT_EXPERIMENT'},'MOUNT_COMPONENT_EXECUTION_PHASE')
            sc.lane(driver.store.batch,driver.config['run_id'],driver.config['owner_binding'],driver.config['source'])
            driver.provider_factory=retry.provider_factory(original.sdk_provider())
            return execute(driver,value,None,None)
    finally:driver.store.db.close();driver.store.batch.db.close()


def science(state_only=False):
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_driver import STAGES
    class Driver(ExperimentDriver):
        def _advance(self,*args,**kwargs):
            self.guard()
            allowed={'UPDATE_STATE','REPORT'} if state_only else {*STAGES,'MODEL_RUNNING'}
            if self.current()['phase'] not in allowed:return {**self.status(),'operational_hold':'MOUNT_COMPONENT_PHASE_ONLY'}
            return super()._advance(*args,**kwargs)
    driver=Driver(STATE)
    try:return driver.advance()
    finally:driver.store.db.close();driver.store.batch.db.close()


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['execute','science','state','verify-execute','verify-science']);a=p.parse_args()
    require(os.getuid()==os.getgid()==1003,'MOUNT_COMPONENT_SERVICE_OWNER');load(a.mode)
    if a.mode.startswith('verify-'):value={'status':'PASS','mode':a.mode,'model_calls':0,'provider_calls':0}
    elif a.mode=='execute':value=advance()
    else:value=science(a.mode=='state')
    print(json.dumps(value,sort_keys=True))


if __name__=='__main__':main()
