"""Connect one independently reviewed scientific smoke assessment; never execute a fit."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
CHANGE='item4-smoke-scientific-review-20261010'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-deliberate-smoke-stop-20261009/tools/item4_deliberate_smoke_runtime.py')
PRIOR_SHA='998a9710c397440ff1f2c0b4dbb123a5eabb28412918a78bc18a33c69f53d45f'
PRIOR_REVIEW='30b4cdea7bab3dbd5c666f61b42202978014221e80f98b61739256c5fb19f3c1'
FILES=('tools/item4_smoke_review_runtime.py','tools/install_item4_smoke_review.py',
    'orchestrator/item4_smoke_review.py','orchestrator/item4_scoped_calls.py','orchestrator/dispatch_limiter.py',
    'docs/ITEM4_SMOKE_REVIEW_CHECKPOINT_PRIVATE.json','docs/ITEM4_SMOKE_TIMING_COMPARISON.json',
    'docs/ITEM4_SMOKE_SPRINT12_TIMING.json')
DIRECTIONS={
    'direction1':('item4-smoke-review-path-20261010','d76b60553bcecfeca7e2b0d5ad89b51d1c7436bb9e84cc5efaa9be09935a133b'),
    'direction2':('item4-smoke-review-path-followup-20261010','bdb5e9516d00a87ff706840da709a8c09f608a273e1ff1c1e1719f72b5763b22')}


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
    for name,(change,pin) in DIRECTIONS.items():
        opinion=verify_result(trusted(RECORD/name))
        require(opinion['verdict']=='APPROVE' and opinion['change_id']==change and
            opinion['source_sha']=='2e6bfd6a66610e775ad8c4b64fcd75ec3cbd437f' and
            opinion['report_sha256']==pin,'DIRECTION_AUTHORITY')
    return result




def connect():
    """Replace one explicit module-factory result before admission closures exist."""
    approved=authority()
    require(sha(trusted(PRIOR).read_bytes())==PRIOR_SHA,'PRIOR_SOURCE_CHANGED')
    route=module('_smoke_review_prior',PRIOR);prior=route.connect()
    require(prior.__file__=='/opt/research-system/manual-repair-helpers/item4-preprocessing-root-repair-20261009/tools/item4_preprocessing_fresh_runtime.py','PRIOR_ENTRY')
    require(sha(trusted(prior.__file__).read_bytes())=='9f8f192949af976f55a0eff8d2a0afe6e7300561024bfaadfa6e3913913155d4','PRIOR_ENTRY_HASH')
    original_factory=prior.module;substituted=[]
    def fresh_factory(name,path):
        result=original_factory(name,path)
        if name!='_fresh_prior_validation':return result
        require(str(path)=='/opt/research-system/manual-repair-helpers/item4-partition-delivery-20261009/tools/item4_validation_runtime.py'
            and sha(trusted(path).read_bytes())=='8f3b690fc85ce10fa6a806cad5859366291299129d885444708c58c68e42ad99','VALIDATION_FACTORY')
        validation_factory=result.module
        def validation_module(name,path):
            component=validation_factory(name,path)
            if name!='_validation_prior_revision':return component
            require(Path(path)==result.PRIOR,'REVISION_FACTORY')
            original=component.module
            def revision_module(name,path):
                if name!='orchestrator.item4_scoped_calls':return original(name,path)
                require(Path(path)==component.ROOT/'orchestrator/item4_scoped_calls.py' and not substituted,'SCOPED_FACTORY')
                import orchestrator
                helper=module('orchestrator.item4_smoke_review',ROOT/'orchestrator/item4_smoke_review.py')
                orchestrator.item4_smoke_review=helper
                checkpoint=json.loads(trusted(ROOT/helper.DOCUMENT).read_bytes())
                helper.scope(checkpoint,approved['report_sha256'])
                calls=module(name,ROOT/'orchestrator/item4_scoped_calls.py')
                orchestrator.item4_scoped_calls=calls;ordinary=calls.connect
                def scoped(*args,**kwargs):
                    require('smoke' not in kwargs and 'smoke_approval' not in kwargs,'DUPLICATE_SCOPE')
                    return ordinary(*args,**kwargs,smoke=checkpoint,smoke_approval=approved['report_sha256'])
                calls.connect=scoped;substituted.append(name)
                return calls
            component.module=revision_module
            return component
        result.module=validation_module
        return result
    prior.module=fresh_factory
    connected=prior.connect()
    require(substituted==['orchestrator.item4_scoped_calls'],'SCOPED_CONNECTION_REQUIRED')
    require(route.authority()['report_sha256']==PRIOR_REVIEW,'PRIOR_APPROVAL')
    from orchestrator import dispatch_limiter
    candidate=module('_smoke_review_limiter',ROOT/'orchestrator/dispatch_limiter.py')
    dispatch_limiter.admit_manual=candidate.admit_manual
    from orchestrator import item4_smoke_review as helper
    p=json.loads(trusted(ROOT/helper.DOCUMENT).read_bytes())
    return connected,helper,p,approved['report_sha256']


def bind_admission(driver,c,original,helper,p,approval):
    from orchestrator import manual_recovery as recovery,stocktake_review_recovery as old_recovery,manual_stage as stage
    saved=(recovery.permit,old_recovery.admission,stage.reviewer_command)
    def permit(store,run):
        result=saved[0](store,run)
        if run!=helper.RUN:return result
        require(store is driver.store and result is not None,'LOCAL_OWNER')
        c.originals(driver,*original);helper.granted(store,p,approval)
        return {**result,'preserved_failures':[result['failed_id'],original[3].CALL]}
    def admission(batch,run,stage_name,ident,source,receipt):
        if run!=helper.RUN:return saved[1](batch,run,stage_name,ident,source,receipt)
        require(batch is driver.store.batch and source==p['source'] and
            (stage_name,ident)==('run_spec_review',helper.CALL),'GLOBAL_OWNER')
        c.originals(driver,*original);helper.ready(driver,driver.current(),p,approval)
        result=saved[0](driver.store,run);require(result is not None,'TIMEOUT_QUALIFICATION')
        return [result['failed_id'],original[3].CALL]
    def command(work,stage_name):
        argv=saved[2](work,stage_name)
        value=driver.current();pending=value.get('pending') or {}
        expected=Path(driver.config.get('workspace_root',driver.state.parent/(driver.state.name+'-scientific-workspaces')))/'run_spec_review-11'
        require(stage_name=='run_spec_review' and Path(work)==expected and
            value['phase']=='MODEL_RUNNING' and pending.get('id')==helper.CALL and
            pending.get('round')==11 and pending.get('stage')==stage_name,'REVIEWER_COMMAND_SCOPE')
        helper.granted(driver.store,p,approval)
        for db,table in [(driver.store.db,'manual_calls'),(driver.store.batch.db,'autonomy_calls')]:
            row=db.execute('SELECT status FROM '+table+' WHERE id=?',(helper.CALL,)).fetchone()
            require(row is not None and row[0]=='RUNNING','REVIEWER_COMMAND_ADMISSION')
        require(argv.count('--max-turns')==1 and argv[argv.index('--max-turns')+1]=='30','REVIEWER_COMMAND_SHAPE')
        argv[argv.index('--max-turns')+1]='60'
        return argv
    recovery.permit,old_recovery.admission,stage.reviewer_command=permit,admission,command
    def restore():
        recovery.permit,old_recovery.admission,stage.reviewer_command=saved
    return restore


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/FILES[0],'SERVICE_IDENTITY')
    require(len(argv)==1 and argv[0] in {'verify','activate','run'},'ACTION_SCOPE')
    (c,policy,original,evidence,base,fresh),helper,p,approval=connect()
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator import manual_recovery as recovery,stocktake_review_recovery as old_recovery,manual_stage as stage
    from orchestrator.manual_executor import lock
    restore=None;driver=None
    class SmokeDriver(ExperimentDriver):
        def task(self,stage_name,value):
            require(stage_name=='run_spec_review','ONLY_SCIENTIFIC_REVIEW')
            return super().task(stage_name,value)+'\n'+helper.GUIDANCE
        def prepare_input(self,value,stage_name,work):
            require(stage_name=='run_spec_review' and self.model_round_number(value)==11,'INPUT_SCOPE')
            extra={'timing-comparison.json':trusted(ROOT/'docs/ITEM4_SMOKE_TIMING_COMPARISON.json').read_bytes(),
                'sprint12-timing.json':trusted(ROOT/'docs/ITEM4_SMOKE_SPRINT12_TIMING.json').read_bytes()}
            helper.deliver(self,value,p,approval,extra)
            body,measurement=super().prepare_input(value,stage_name,work)
            helper.verify_delivered(self,value,work,body,measurement,p)
            return body,measurement
        def _accept_completed(self,value):
            return helper.finish(self,value,p,approval)
    try:
        driver=SmokeDriver(c.LANE)
        with lock(driver.state/'driver.lock'):
            driver.guard();c.originals(driver,*original);base.connect_evidence(driver,c,evidence)
            value=driver.current()
            if argv[0]=='verify':
                helper.evidence(driver,value,p,approval)
                result={'status':'VERIFIED_HELD','model_calls':0,'provider_calls':0,'scientifically_accepted':False}
            elif argv[0]=='activate':
                result=helper.activate(driver,p,approval,driver.state/'smoke-review11')
            else:
                helper.ready(driver,value,p,approval)
                restore=bind_admission(driver,c,original,helper,p,approval)
                result=driver._model_step(value)
        print(json.dumps(result,sort_keys=True))
    finally:
        if restore is not None:restore()
        if driver is not None:driver.store.db.close();driver.store.batch.db.close()

if __name__=='__main__':
    os.umask(0o077)
    sys.path.insert(0,'/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
    main()
