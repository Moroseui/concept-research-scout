"""Actual author20 native receipt delivered to the already-reserved reviewer16."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools import item4_diagnostic_native_runtime as native
ROOT=native.ROOT
PREFIX='diagnostic-native20-'
sha,require,trusted=native.sha,native.require,native.trusted

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module

def connect():
    prior,connected=native.verified_prior(scientific=True)
    native.overlay(ROOT)
    approval=native.authority()['report_sha256']
    p=json.loads(trusted(ROOT/'docs/ITEM4_CORRECTED_NATIVE_REVIEW_PRIVATE.json').read_bytes())
    return prior,(*connected[:5],p,approval)


def evidence(accounts):
    from orchestrator.modal_executor import canonical
    from orchestrator import private_records as pr,modal_native_synthetic as n
    native.accepted(accounts,review=True)
    binding,result=native.native_result(accounts)
    # Exact full provider receipt (including unabridged console), selection and
    # transport proof. Each byte is delivered through small hash-checked pages.
    value={'schema':'item4-diagnostic-native-review-evidence/v1','binding':binding,'receipt':result,
        'selection':n.selected(),
        'transport':{name:json.loads(pr.check(native.STATE/'provider'/name).read_bytes())
            for name in ('terminal.json','stdin-intent.json','stdin-sent.json')},
        'scientific_acceptance':False,'gpu_verified':False,'production_main_verified':False}
    return canonical(value)

def marker(accounts):
    from orchestrator import modal_native_synthetic as n
    raw=evidence(accounts)
    return {'schema':'item4-diagnostic-native-evidence-binding/v1','implementation_sha256':native.authority()['report_sha256'],
        'receipt_sha256':sha(raw),'selection_sha256':n.SELECTION_SHA,'author_call_id':n.selected()['author_call_id'],
        'review_attempt':16,'execution_authorized':False,'full_training_admitted':False,'coverage_released':False}

def attach(driver,helper,p,approval):
    saved_ready=helper.ready
    def ready(current,value,scope,grant):
        result=saved_ready(current,value,scope,grant)
        if not helper.corrected_review(scope):return result
        require(current.store is driver.store and current.state==driver.state and current.config==driver.config
            and scope==p and grant==approval==native.authority()['report_sha256'],'REVIEW_SCOPE')
        require(value.get('diagnostic_native_evidence')==marker(driver.store.batch),'ACTUAL_NATIVE_EVIDENCE_REQUIRED')
        return result
    helper.ready=ready
    return lambda:setattr(helper,'ready',saved_ready)


def pages(raw):
    from orchestrator.modal_executor import canonical
    text=raw.decode();pieces=[text[i:i+6000] for i in range(0,len(text),6000)]
    result={f'page-{i+1:03}.txt':part.encode() for i,part in enumerate(pieces)}
    result['index.json']=canonical({'schema':'item4-complete-native-pages/v1','sha256':sha(raw),'bytes':len(raw),
        'pages':[{'name':name,'bytes':len(body),'sha256':sha(body)} for name,body in result.items()],
        'omissions':[],'scientific_acceptance':False,'gpu_verified':False,'production_main_verified':False})
    return result

def deliver(driver,value):
    from orchestrator import experiment_collection as collection
    expected=pages(evidence(driver.store.batch))
    for name,raw in expected.items():
        collection.artifact(driver,value,'result_tables',PREFIX+name,'diagnostic-native20/'+name,raw)
    actual=[r for r in value['artifacts'] if r['id'].startswith(PREFIX)]
    require(len(actual)==len(expected) and {r['id']:r['sha256'] for r in actual}==
        {PREFIX+n:sha(raw) for n,raw in expected.items()},'NATIVE_DELIVERY_MEMBERS')
    driver.save(value)

def verify_delivery(driver,value):
    require(value.get('diagnostic_native_evidence')==marker(driver.store.batch),'NATIVE_MARKER_CHANGED')
    from orchestrator import context_budget as cb,private_records as pr
    expected=pages(evidence(driver.store.batch))
    actual=[r for r in value['artifacts'] if r['id'].startswith(PREFIX)]
    require(len(actual)==len(expected),'NATIVE_DELIVERY_MEMBERS')
    for ref in actual:
        require(pr.check(cb.relative_file(driver.context,ref['path'])).read_bytes()==expected[ref['id'][len(PREFIX):]],
            'NATIVE_DELIVERY_BYTES')

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
            (stage_name,ident)==('run_spec_review',helper.call(p,'review')),'GLOBAL_OWNER')
        c.originals(driver,*original);helper.ready(driver,driver.current(),p,approval)
        result=saved[0](driver.store,run);require(result is not None,'TIMEOUT_QUALIFICATION')
        return [result['failed_id'],original[3].CALL]
    def command(work,stage_name):
        argv=saved[2](work,stage_name);pending=driver.current().get('pending') or {}
        expected=Path(driver.config.get('workspace_root',driver.state.parent/(driver.state.name+'-scientific-workspaces')))/'run_spec_review-16'
        require(stage_name=='run_spec_review' and Path(work)==expected and pending.get('id')==helper.call(p,'review')
            and pending.get('round')==16 and pending.get('stage')==stage_name,'REVIEW_COMMAND_SCOPE')
        for db,table in [(driver.store.db,'manual_calls'),(driver.store.batch.db,'autonomy_calls')]:
            row=db.execute('SELECT status FROM '+table+' WHERE id=?',(helper.call(p,'review'),)).fetchone()
            require(row is not None and row[0]=='RUNNING','REVIEW_ADMISSION_REQUIRED')
        require(argv.count('--max-turns')==1 and argv[argv.index('--max-turns')+1]=='30','REVIEW_COMMAND_SHAPE')
        argv[argv.index('--max-turns')+1]='60';return argv
    recovery.permit,old_recovery.admission,stage.reviewer_command=permit,admission,command
    def restore():recovery.permit,old_recovery.admission,stage.reviewer_command=saved
    return restore

def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    require(argv in (['verify'],['activate'],['run']) and os.getuid()==os.getgid()==1003
        and sys.flags.no_user_site and Path(__file__).resolve()==ROOT/'tools/item4_diagnostic_review_runtime.py','SERVICE_IDENTITY')
    prior,connection=connect();connected,smoke,smoke_p,smoke_approval,helper,p,approval=connection
    c,policy,original,old_evidence,base,fresh=connected
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    from orchestrator.modal_executor import canonical
    from orchestrator import private_records as pr
    restore=None;restore_helper=None;driver=None
    class Reviewer(ExperimentDriver):
        def task(self,stage,value):
            require(stage=='run_spec_review','REVIEW_ONLY');return super().task(stage,value)+'\n'+helper.guidance(p)
        def prepare_input(self,value,stage,work):
            require((stage,self.model_round_number(value))==('run_spec_review',16),'INPUT_SCOPE')
            helper.deliver(self,value,p,approval,prior.supplemental(self,p));deliver(self,value)
            body,measurement=super().prepare_input(value,stage,work)
            helper.verify_delivered(self,value,stage,work,body,measurement,p);verify_delivery(self,value)
            return body,measurement
        def _accept_completed(self,value):
            pending=value.get('pending') or {};work=Path(pending.get('workspace',''))
            require((pending.get('stage'),pending.get('round'),pending.get('id'))==
                ('run_spec_review',16,helper.call(p,'review')),'COMPLETION_SCOPE')
            helper.verify_delivered(self,value,'run_spec_review',work,pr.check(work/'prompt.md').read_text(),
                json.loads(pr.check(work/'input-measurement.json').read_bytes()),p);verify_delivery(self,value)
            result=helper.finish_review(self,value,p,approval)
            assessment=value[helper.profile(p)['result']]
            value['diagnostic_native_scientific_assessment']={**assessment,
                'scientific_scope':'two-cpu-diagnostic-fits-only','global_findings_closed':False,
                'carried_review_sha256':helper.REVIEW15_REPORT,
                'native_evidence':value['diagnostic_native_evidence']}
            self.save(value);return self.status()
    try:
        driver=Reviewer(c.LANE);restore_helper=attach(driver,helper,p,approval)
        with lock(driver.state/'driver.lock'):
            driver.guard();c.originals(driver,*original);base.connect_evidence(driver,c,old_evidence)
            value=driver.current()
            helper.originals(driver.store,p,approval);helper.review_binding(driver,p,approval)
            prior.retained_smoke_evidence(driver,value,smoke,smoke_p,smoke_approval,helper)
            if argv==['verify']:
                native.accepted(driver.store.batch,review=True)
                result={'status':'VERIFIED_HELD','model_calls':0,'provider_calls':0}
            elif argv==['activate']:
                native.accepted(driver.store.batch)
                require(value['phase']=='BLOCKED' and not value.get('pending') and
                    not driver.store.db.execute('SELECT 1 FROM manual_calls WHERE id=?',(helper.call(p,'review'),)).fetchone(),
                    'REVIEW_ALREADY_STARTED')
                mark=marker(driver.store.batch)
                with pr.open_file(driver.state/'diagnostic-native20-activation.json','xb') as stream:stream.write(canonical(mark))
                helper.activate(driver,p,approval,driver.state/helper.profile(p)['folder'])
                value=driver.current();value['diagnostic_native_evidence']=mark
                helper.ready(driver,value,p,approval);driver.save(value)
                result={'status':'READY_REVIEW16','model_calls':0,'provider_calls':0}
            else:
                helper.ready(driver,value,p,approval)
                restore=bind_admission(driver,c,original,helper,p,approval)
                result=driver._model_step(value)
        print(json.dumps(result,sort_keys=True))
    finally:
        if restore is not None:restore()
        if restore_helper is not None:restore_helper()
        if driver is not None:driver.store.db.close();driver.store.batch.db.close()

if __name__=='__main__':
    os.umask(0o077)
    sys.path.insert(0,'/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
    main()
