"""Actual author24 native receipt delivered to the already-reserved reviewer16."""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools import item4_diagnostic_native_runtime as native
ROOT=Path('/opt/research-system/manual-repair-helpers/terminal-ledger-readonly-20261011')
ACTIVATION_DOCUMENT='docs/NATIVE_REVIEW_ACTIVATION_PRIVATE.json'
ACTIVATION_SHA='ac8b4b87792a5a5bcc7f74371253bdd238f8286621f6c3508c8fda26864039a3'
PREFIX='diagnostic-native24-'
sha,require,trusted=native.sha,native.require,native.trusted

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module

def authority(*,held=True):
    current=load('_native_review_bundle_authority',ROOT/'tools/colab_intake_identity_runtime.py')
    return current,current.authority(held=held)


def connect(*,held=True):
    global native
    bundle,approval=authority(held=held)
    native,old_approval=bundle.preserved_native()
    require(old_approval['source_sha']=='1f2243448ca452abcad92ca355bead042cc731d2'
        and old_approval['report_sha256']=='c27eaa20e857449d1d054621848fd63084dc811a092f98128e63c9a99797ba93','PASSED_NATIVE_RELEASE')
    require(sha(trusted(native.PRIOR).read_bytes())==native.PRIOR_SHA,'PRIOR_RUNTIME_CHANGED')
    prior=load('_native_review_prior_author24',native.PRIOR)
    approved=prior.authority()
    require(approved['source_sha']=='72c48cb69af87b760c4da9f246c1d1cab10735e1'
        and approved['report_sha256']==native.PRIOR_REVIEW,'PRIOR_APPROVAL')
    # Supply the reviewed components before original connection installs all its
    # independent proof callbacks. No unconnected replacement of accounting.
    factory=prior.load
    def selected(name,path):
        if name=='orchestrator.preparation_interleaving':
            require(Path(path)==prior.REPAIRED/'orchestrator/preparation_interleaving.py','SEQUENCE_SOURCE')
            return factory(name,ROOT/'orchestrator/preparation_interleaving.py')
        return factory(name,path)
    prior.load=selected;route=prior.route();original=route.module;used=[]
    def component(name,path):
        if name=='orchestrator.item4_scoped_calls':
            require(Path(path)==route.ROOT/'orchestrator/item4_scoped_calls.py' and name not in used,'SCOPED_SOURCE')
            used.append(name)
            # Run predecessor loader/cap authentication before replacing its
            # still-unconnected author-only allocator. The replacement captures
            # exactly the same ordinary local/global reservation methods.
            predecessor=original(name,path)
            require(predecessor._validate is None,'SCOPED_ALREADY_CONNECTED')
            import orchestrator
            scoped=load(name,ROOT/'orchestrator/item4_scoped_calls.py')
            orchestrator.item4_scoped_calls=scoped
            return scoped
        if name=='orchestrator.item4_smoke_response':
            require(Path(path)==route.ROOT/'orchestrator/item4_smoke_response.py' and name not in used,'READY_SOURCE')
            used.append(name);return original(name,ROOT/'orchestrator/item4_smoke_response.py')
        return original(name,path)
    route.module=component;connection=route.connect()
    require(sorted(used)==['orchestrator.item4_scoped_calls','orchestrator.item4_smoke_response'] and connection[4].delivery_recovery(connection[5])
        and connection[4].profile(connection[5])['author']==24
        and connection[4].profile(connection[5])['reviewer']==16,'AUTHOR24_CONNECTION')
    native.overlay(native.ROOT)
    from orchestrator import manual_runtime,preparation_interleaving as pi
    repair=load('orchestrator.colab_reader_recovery',ROOT/'orchestrator/colab_reader_recovery.py')
    raw=trusted(ROOT/repair.TURN_DOCUMENT).read_bytes()
    require(sha(raw)==repair.TURN_DOCUMENT_SHA,'FAILED_REVIEW_BINDING');frozen=json.loads(raw)
    require(pi._REVIEW_TERMINAL is None and pi._EXTRA_ATTEMPT is None,'SEQUENCE_ALREADY_CONNECTED')
    pi._REVIEW_TERMINAL=lambda scope,row,item:repair.retained_review(scope,row,item,frozen)
    recovery_review=bundle.colab_recovery_review()
    pi._EXTRA_ATTEMPT=lambda scope,run,stage,ident:repair.extra_attempt(scope,run,stage,ident,frozen,recovery_review)
    terminal=load('orchestrator.colab_author_terminal',ROOT/'orchestrator/colab_author_terminal.py')
    terminal.connect_sequence(pi);terminal.connect_timing_admission()
    from tools import reviewer_connection_timing
    reviewer_connection_timing.bind(manual_runtime)
    return route,connection


def recovery_document():
    raw=trusted(ROOT/ACTIVATION_DOCUMENT).read_bytes()
    require(sha(raw)==ACTIVATION_SHA,'ACTIVATION_DOCUMENT_CHANGED')
    return json.loads(raw)


REVIEW_GUIDANCE = (
    'Current task: independent scientific reviewer16, not authoring. Judge the unchanged accepted author24 output '
    'against genuine review15 and the complete actual native CPU evidence. The historical author instructions '
    'above do not authorize a new author call or any scientific edit. Read the diagnostic-native24 index and '
    'all ordered hash-bound pages, including console, selection and transport. An outer PASS alone is insufficient. '
    'Decide whether the evidence resolves DIAG-U2 for the two approved CPU-resource diagnostic fits. '
    'CPU-only invalid GPU telemetry is a limitation, not GPU or production evidence. No full-plan acceptance, '
    'coverage release or full-training admission is implied. Report all findings in one genuine submit_review verdict; '
    'no verdict is requested. Original findings, failed attempts and charges remain preserved.')


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
    require(helper._native_review_ready is None and helper._native_review_complete is None,'NATIVE_GUARD_ALREADY_CONNECTED')
    def qualified(current,value,scope,grant):
        require(current.store is driver.store and current.state==driver.state and current.config==driver.config
            and scope==p and grant==approval and helper.delivery_recovery(scope)
            and helper.profile(scope)['author']==24 and helper.profile(scope)['reviewer']==16
            and value.get('phase')=='run_spec_review','REVIEW_SCOPE')
        require(value.get('diagnostic_native_evidence')==marker(driver.store.batch),'ACTUAL_NATIVE_EVIDENCE_REQUIRED')
        return True
    def ready(current,value,scope,grant):
        if scope==p:qualified(current,value,scope,grant)
        return saved_ready(current,value,scope,grant)
    def completed(current,value,scope,grant):
        pending=value.get('pending') or {}
        require(value.get('phase')=='MODEL_RUNNING' and pending.get('id')==helper.call(p,'review')
            and pending.get('stage')=='run_spec_review' and pending.get('round')==16,'NATIVE_COMPLETION_SCOPE')
        return qualified(current,{**value,'phase':'run_spec_review'},scope,grant)
    helper._native_review_ready=qualified
    helper._native_review_complete=completed
    helper.ready=ready
    def restore():
        helper.ready=saved_ready;helper._native_review_ready=None;helper._native_review_complete=None
    return restore


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
        collection.artifact(driver,value,'result_tables',PREFIX+name,'diagnostic-native24/'+name,raw)
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
    # Reuse author24's exact preserved-failure proofs for its reserved reviewer;
    # this is neither a new author allowance nor a global uncertainty exception.
    from orchestrator import manual_stage as stage,manual_recovery as recovery
    from orchestrator import stocktake_review_recovery as prior_recovery
    saved=stage.reviewer_command
    saved_permit,saved_admission=recovery.permit,prior_recovery.admission
    def permit(store,run):
        result=saved_permit(store,run)
        if run!=helper.RUN:return result
        require(store is driver.store and result is not None,'REVIEW_LOCAL_OWNER')
        value=driver.current()
        require(value.get('phase')=='run_spec_review' and not value.get('pending'),'REVIEW_LOCAL_STAGE')
        c.originals(driver,*original);helper.ready(driver,value,p,approval)
        retained=result.get('preserved_failures',[result['failed_id']])
        return {**result,'preserved_failures':list(dict.fromkeys([*retained,result['failed_id'],original[3].CALL,helper.SENDER_FAILED_CALL]))}
    def admission(batch,run,stage_name,ident,source,receipt):
        if run!=helper.RUN:return saved_admission(batch,run,stage_name,ident,source,receipt)
        require(batch is driver.store.batch and source==driver.config['source']
            and (stage_name,ident)==('run_spec_review',helper.call(p,'review')),'REVIEW_GLOBAL_OWNER')
        return permit(driver.store,run)['preserved_failures']
    # Load first; a missing/invalid component must leave existing hooks intact.
    terminal=load('_native_review_admission_terminal',ROOT/'orchestrator/colab_author_terminal.py')
    recovery.permit,prior_recovery.admission=permit,admission
    try:
        # The already-reviewed exact Colab terminal qualifier remains mandatory.
        terminal.connect_timing_admission()
    except BaseException:
        recovery.permit,prior_recovery.admission=saved_permit,saved_admission
        raise
    def command(work,stage_name):
        argv=saved(work,stage_name);pending=driver.current().get('pending') or {}
        expected=Path(driver.config.get('workspace_root',driver.state.parent/(driver.state.name+'-scientific-workspaces')))/'run_spec_review-16'
        require(stage_name=='run_spec_review' and Path(work)==expected and pending.get('id')==helper.call(p,'review')
            and pending.get('round')==16 and pending.get('stage')==stage_name,'REVIEW_COMMAND_SCOPE')
        for db,table in [(driver.store.db,'manual_calls'),(driver.store.batch.db,'autonomy_calls')]:
            row=db.execute('SELECT status FROM '+table+' WHERE id=?',(helper.call(p,'review'),)).fetchone()
            require(row is not None and row[0]=='RUNNING','REVIEW_ADMISSION_REQUIRED')
        require(argv.count('--max-turns')==1 and argv[argv.index('--max-turns')+1]=='30','REVIEW_COMMAND_SHAPE')
        argv[argv.index('--max-turns')+1]='60';return argv
    stage.reviewer_command=command
    def restore():
        stage.reviewer_command=saved
        recovery.permit,prior_recovery.admission=saved_permit,saved_admission
    return restore


def activate_review(driver,helper,p,approval,*,recovery=None,recovery_approval=None):
    from orchestrator import private_records as pr
    from orchestrator.modal_executor import canonical
    native.accepted(driver.store.batch)
    value=driver.current();ident=helper.call(p,'review')
    require(value['phase']=='BLOCKED' and not value.get('pending') and
        not driver.store.db.execute('SELECT 1 FROM manual_calls WHERE id=?',(ident,)).fetchone(),
        'REVIEW_ALREADY_STARTED')
    require(not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),
        'OTHER_RUNNING_CALL')
    mark=marker(driver.store.batch)
    raw=driver.store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    require(json.loads(raw)==value,'STATE_DRIFT')
    intent=driver.state/'diagnostic-native24-activation.json'
    expected_intent=canonical({'original_state':raw,'native':mark})
    if recovery is None:
        require(recovery_approval is None,'UNEXPECTED_RECOVERY_APPROVAL')
        with pr.open_file(intent,'xb') as stream:stream.write(expected_intent)
    else:
        require(recovery.get('schema')=='native-review-activation-recovery/v1'
            and recovery.get('state_sha256')==sha(raw.encode())
            and recovery.get('intent_sha256')==sha(expected_intent)
            and recovery.get('native')==mark and pr.check(intent).read_bytes()==expected_intent,
            'EXACT_FAILED_ACTIVATION_REQUIRED')
        require(isinstance(recovery_approval,str) and len(recovery_approval)==64
            and all(c in '0123456789abcdef' for c in recovery_approval),'RECOVERY_APPROVAL')
        require(not driver.store.db.execute('SELECT 1 FROM events WHERE id=?',('author24-native-review-ready',)).fetchone(),
            'ACTIVATION_ALREADY_APPLIED')
        with pr.open_file(driver.state/'diagnostic-native24-recovery-intent.json','xb') as stream:
            stream.write(canonical({'original_intent_sha256':sha(expected_intent),
                'implementation_review_sha256':recovery_approval,'recovery_sha256':sha(canonical(recovery))}))
    changed={**value,'phase':'run_spec_review','reason':'AUTHOR24_NATIVE_EVIDENCE_READY',
             'diagnostic_native_evidence':mark}
    helper.ready(driver,changed,p,approval)
    db=driver.store.db;db.execute('BEGIN IMMEDIATE')
    try:
        require(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'STATE_DRIFT')
        require(pr.check(intent).read_bytes()==expected_intent,'ACTIVATION_INTENT_CHANGED')
        db.execute('INSERT INTO events VALUES(?,?,?)',('author24-native-review-ready',helper.RUN,canonical(mark).decode()))
        db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(changed),))
        db.execute('COMMIT')
    except BaseException:db.execute('ROLLBACK');raise
    return {'status':'READY_REVIEW16','model_calls':0,'provider_calls':0}

def host(action):
    """Reuse genuine host-proof start/pulse with exact review-stage readiness."""
    import subprocess,fcntl
    require(action in {'start','pulse'} and os.getuid()==0 and sys.flags.no_user_site
        and Path(__file__).resolve()==ROOT/'tools/item4_diagnostic_review_runtime.py','HOST_ACTION')
    bundle,approval=authority()
    h=load('_native_review_existing_host',ROOT/'tools/item4_response_host_operation.py')
    frozen=json.loads(trusted(ROOT/h.DOCUMENT).read_bytes())
    installed=json.loads(trusted(bundle.RECORD/'installed.json').read_bytes())
    frozen['hashes']={**frozen['hashes'],**installed['units'],**{str(ROOT/n):pin for n,pin in installed['files'].items()}}
    h.hashes(frozen)
    h.UNIT=bundle.NATIVE_UNIT;h.ENTRY=ROOT/'tools/item4_diagnostic_review_runtime.py'
    h.STAGE='review';h.OPERATION_ROOT=bundle.RECORD/'native-review-operation';h.RECORD=h.OPERATION_ROOT/'review'
    def starting_state(proof,approved):
        require(proof==frozen and approved==approval,'HOST_AUTHORITY_CHANGED')
        result=json.loads(subprocess.check_output(['runuser','-u','partho','--','env',
            'RESEARCH_MANUAL_RUNTIME_CONFIG='+str(h.RUNTIME),'python3','-s','-B',str(h.ENTRY),'ready'],text=True))
        require(result=={'status':'READY_REVIEW16','model_calls':0,'provider_calls':0},'GENUINE_REVIEW_READINESS')
        return {**result,'stage':'review','source':approval['source_sha'],'review_sha256':approval['report_sha256']}
    h.starting_state=starting_state
    for path in (h.OPERATION_ROOT,h.RECORD):
        if not path.exists():trusted(path.parent);path.mkdir(mode=0o700)
        trusted(path)
    with (h.RECORD/'operation.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        return h.start(frozen,approval) if action=='start' else h.pulse(frozen,approval)


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if argv in (['start'],['pulse']):
        print(json.dumps(host(argv[0]),sort_keys=True));return
    require(argv in (['verify'],['ready'],['activate'],['run']) and os.getuid()==os.getgid()==1003
        and sys.flags.no_user_site and Path(__file__).resolve()==ROOT/'tools/item4_diagnostic_review_runtime.py','SERVICE_IDENTITY')
    prior,connection=connect(held=argv!=['verify']);connected,smoke,smoke_p,smoke_approval,helper,p,approval=connection
    c,policy,original,old_evidence,base,fresh=connected
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    from orchestrator.modal_executor import canonical
    from orchestrator import private_records as pr
    restore=None;restore_helper=None;driver=None
    class Reviewer(ExperimentDriver):
        def task(self,stage,value):
            require(stage=='run_spec_review','REVIEW_ONLY');return super().task(stage,value)+'\nHistorical author24 instruction, retained verbatim as context:\n'+helper.guidance(p)+'\n'+REVIEW_GUIDANCE
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
            if argv in (['verify'],['ready']):
                native.accepted(driver.store.batch,review=True)
                prospective={**value,'phase':'run_spec_review','reason':'AUTHOR24_NATIVE_EVIDENCE_READY',
                    'diagnostic_native_evidence':marker(driver.store.batch)}
                helper.ready(driver,prospective,p,approval)
                if argv==['ready']:
                    require(value==prospective,'ACTIVATION_REQUIRED')
                    require(not driver.store.db.execute('SELECT 1 FROM manual_calls WHERE id=?',(helper.call(p,'review'),)).fetchone()
                        and not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),
                        'MODEL_ALREADY_RUNNING')
                result={'status':'VERIFIED_HELD' if argv==['verify'] else 'READY_REVIEW16','model_calls':0,'provider_calls':0}
            elif argv==['activate']:
                result=activate_review(driver,helper,p,approval,recovery=recovery_document(),recovery_approval=authority()[1]['report_sha256'])
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
