"""One reviewed proposal response pair; no experiment dispatch action."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
CHANGE='item4-post-smoke-response-20261010'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-smoke-scientific-review-20261010/tools/item4_smoke_review_runtime.py')
PRIOR_SHA='98208d5e8366c05fa2f400cc76bca5e4efc85400c5fcb272b13fec7a53095ac2'
PRIOR_REVIEW='fb04e156b4b29bfbc99e86437d7266ce1df51186f72c0baef754d39a0dac1aef'
FILES=('tools/item4_smoke_response_runtime.py','tools/install_item4_smoke_response.py',
    'orchestrator/item4_smoke_response.py','orchestrator/item4_scoped_calls.py','orchestrator/dispatch_limiter.py',
    'docs/ITEM4_POST_SMOKE_RESPONSE_PRIVATE.json','docs/ITEM4_RESPONSE_TIMING_AUDIT.json',
    'docs/ITEM4_RESPONSE_NATIVE_TRAINER.py','docs/ITEM4_STAGE1_CAP_OPERATOR_DECISION_20261009.txt',
    'orchestrator/modal_nnunet.py','orchestrator/modal_fit_progress.py',
    'tools/item4_response_host_operation.py','docs/ITEM4_RESPONSE_HOST_PRIVATE.json')


def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('SMOKE_RESPONSE_RUNTIME_'+why)
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
    approved=authority()
    require(sha(trusted(PRIOR).read_bytes())==PRIOR_SHA,'PRIOR_SOURCE_CHANGED')
    route=module('_post_smoke_prior',PRIOR);original_factory=route.module;substituted=[]
    def factory(name,path):
        if name!='orchestrator.item4_scoped_calls':return original_factory(name,path)
        require(Path(path)==route.ROOT/'orchestrator/item4_scoped_calls.py' and not substituted,'SCOPED_FACTORY')
        import orchestrator
        helper=module('orchestrator.item4_smoke_response',ROOT/'orchestrator/item4_smoke_response.py')
        orchestrator.item4_smoke_response=helper
        p=json.loads(trusted(ROOT/helper.DOCUMENT).read_bytes());helper.scope(p,approved['report_sha256'])
        calls=module(name,ROOT/'orchestrator/item4_scoped_calls.py');orchestrator.item4_scoped_calls=calls
        original=calls.connect
        def scoped(*args,**kw):
            require('post_smoke' not in kw and 'post_smoke_approval' not in kw,'DUPLICATE_SCOPE')
            return original(*args,**kw,post_smoke=p,post_smoke_approval=approved['report_sha256'])
        calls.connect=scoped;substituted.append(name);return calls
    route.module=factory
    connected,smoke,smoke_p,smoke_approval=route.connect()
    require(substituted==['orchestrator.item4_scoped_calls'] and route.authority()['report_sha256']==PRIOR_REVIEW,'PRIOR_CONNECTION')
    from orchestrator import dispatch_limiter,item4_smoke_response as helper
    limiter=module('_post_smoke_limiter',ROOT/'orchestrator/dispatch_limiter.py')
    dispatch_limiter.admit_manual=limiter.admit_manual
    p=json.loads(trusted(ROOT/helper.DOCUMENT).read_bytes())
    return connected,smoke,smoke_p,smoke_approval,helper,p,approved['report_sha256']


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
        require(batch is driver.store.batch and source==driver.config['source'] and
            (stage_name,ident) in {('run_spec_author',helper.AUTHOR),('run_spec_review',helper.REVIEW)},'GLOBAL_OWNER')
        c.originals(driver,*original);helper.ready(driver,driver.current(),p,approval)
        result=saved[0](driver.store,run);require(result is not None,'TIMEOUT_QUALIFICATION')
        return [result['failed_id'],original[3].CALL]
    def command(work,stage_name):
        argv=saved[2](work,stage_name)
        pending=driver.current().get('pending') or {}
        expected=Path(driver.config.get('workspace_root',driver.state.parent/(driver.state.name+'-scientific-workspaces')))/'run_spec_review-12'
        require(stage_name=='run_spec_review' and Path(work)==expected and
            pending.get('id')==helper.REVIEW and pending.get('round')==12 and pending.get('stage')==stage_name,'REVIEWER_COMMAND_SCOPE')
        helper.granted(driver.store,p,approval)
        for db,table in [(driver.store.db,'manual_calls'),(driver.store.batch.db,'autonomy_calls')]:
            row=db.execute('SELECT status FROM '+table+' WHERE id=?',(helper.REVIEW,)).fetchone()
            require(row is not None and row[0]=='RUNNING','REVIEWER_COMMAND_ADMISSION')
        require(argv.count('--max-turns')==1 and argv[argv.index('--max-turns')+1]=='30','REVIEWER_COMMAND_SHAPE')
        argv[argv.index('--max-turns')+1]='60';return argv
    recovery.permit,old_recovery.admission,stage.reviewer_command=permit,admission,command
    def restore():recovery.permit,old_recovery.admission,stage.reviewer_command=saved
    return restore


def supplemental():
    names={'current-cap-decision.txt':'docs/ITEM4_STAGE1_CAP_OPERATOR_DECISION_20261009.txt',
        'timing-audit.json':'docs/ITEM4_RESPONSE_TIMING_AUDIT.json','native-trainer.py':'docs/ITEM4_RESPONSE_NATIVE_TRAINER.py',
        'checkpoint-adapter.py':'orchestrator/modal_nnunet.py','durable-progress.py':'orchestrator/modal_fit_progress.py'}
    return {name:trusted(ROOT/path).read_bytes() for name,path in names.items()}


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/FILES[0],'SERVICE_IDENTITY')
    require(len(argv)==1 and argv[0] in {'verify','activate','run'},'ACTION_SCOPE')
    connected,smoke,smoke_p,smoke_approval,helper,p,approval=connect()
    c,policy,original,evidence,base,fresh=connected
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    from orchestrator import private_records as pr
    restore=None;driver=None
    class ResponseDriver(ExperimentDriver):
        def task(self,stage_name,value):
            require(stage_name in {'run_spec_author','run_spec_review'},'ONLY_RESPONSE_STAGES')
            return super().task(stage_name,value)+'\n'+helper.GUIDANCE
        def prepare_input(self,value,stage_name,work):
            require((stage_name,self.model_round_number(value)) in {('run_spec_author',15),('run_spec_review',12)},'INPUT_SCOPE')
            helper.deliver(self,value,p,approval,supplemental())
            body,measurement=super().prepare_input(value,stage_name,work)
            helper.verify_delivered(self,value,stage_name,work,body,measurement,p)
            return body,measurement
        def _accept_completed(self,value):
            pending=value.get('pending') or {};stage=pending.get('stage')
            require((stage,pending.get('round'),pending.get('id')) in {
                ('run_spec_author',15,helper.AUTHOR),('run_spec_review',12,helper.REVIEW)},'COMPLETION_SCOPE')
            work=Path(pending['workspace'])
            helper.verify_delivered(self,value,stage,work,pr.check(work/'prompt.md').read_text(),
                json.loads(pr.check(work/'input-measurement.json').read_bytes()),p)
            if stage=='run_spec_review':return helper.finish_review(self,value,p,approval)
            # Ordinary author schema, synthetic tests and accepted-submission
            # validation remain unchanged. No execution approval is produced.
            return super()._accept_completed(value)
    try:
        driver=ResponseDriver(c.LANE)
        with lock(driver.state/'driver.lock'):
            driver.guard();c.originals(driver,*original);base.connect_evidence(driver,c,evidence)
            value=driver.current()
            if argv[0]=='verify':
                helper.originals(driver.store,p,approval);helper.review_binding(driver,p,approval)
                smoke.evidence(driver,value,smoke_p,smoke_approval)
                result={'status':'VERIFIED_HELD','model_calls':0,'provider_calls':0}
            elif argv[0]=='activate':
                result=helper.activate(driver,p,approval,driver.state/'post-smoke-response')
            else:
                helper.ready(driver,value,p,approval)
                restore=bind_admission(driver,c,original,helper,p,approval)
                result=driver._model_step(value) # One stage only; never dispatch or auto-loop.
        print(json.dumps(result,sort_keys=True))
    finally:
        if restore is not None:restore()
        if driver is not None:driver.store.db.close();driver.store.batch.db.close()

if __name__=='__main__':
    os.umask(0o077)
    sys.path.insert(0,'/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
    main()
