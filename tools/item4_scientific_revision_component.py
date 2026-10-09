"""Reviewed 13B revision connection; original engine/jail/admission remain in use."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

CHANGE='item4-author7-and-image-recovery-20261008'
REVIEW_CHANGE='item4-review7-context-delivery-20261009'
CONTINUATION_DOCUMENT='docs/ITEM4_REVIEW6_CONTINUATION.json'
SECOND_DOCUMENT='docs/ITEM4_REVIEW5_CONTINUATION.json'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-review-evidence-paths-20261008/tools/item4_review_context_component.py')
SCIENCE=Path('/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
STATE=Path('/var/lib/research-system-manual-sprint10/releases')/SCIENCE.name
LANE=STATE/'item4/lane'
DEST=STATE/'item4'/CHANGE
RUN='experiment-a74959ac4546a982af4ae137'
RUNTIME=Path('/etc/research-system-manual-sprint10/releases')/SCIENCE.name/'runtime.json'
MODULES=('author_revision_accounting','author_output_schema','revision_evidence','author_format_submission',
         'experiment_plan_validation','experiment_environment_requirements','modal_billing','author_format_retry',
         'experiment_approval','manual_executor','manual_driver','manual_recovery')
DOCS=('AUTHOR_REVISE_ACCOUNTING_OPERATOR_DECISION_20261008.txt','OVERNIGHT_AUTONOMY_OPERATOR_DECISION_20261008.txt',
      'ITEM4_REVISION_CHECKPOINT.json','ITEM4_REVISION_EVIDENCE.json')
FILES=tuple('orchestrator/'+n+'.py' for n in MODULES)+tuple('docs/'+n for n in DOCS)+(
      'tools/item4_scientific_revision_component.py','tools/install_item4_scientific_revision.py')
# Reuse the existing worker's explicit stdlib-only support closure. Every byte
# is independently reviewed, installed and hash-bound before author tests.
SUPPORT_FILES=('orchestrator/__init__.py', 'orchestrator/private_records.py', 'orchestrator/modal_files.py', 'orchestrator/modal_fit_progress.py', 'orchestrator/modal_fit_contract.py', 'orchestrator/modal_fit_publication.py', 'orchestrator/modal_nnunet.py', 'orchestrator/experiment_result.py', 'orchestrator/scientific_view_scan.py', 'orchestrator/privacy_patterns.py', 'orchestrator/experiment_preprocessing.py', 'orchestrator/preprocessing_checkpoints.py', 'orchestrator/modal_preprocessed_contract.py', 'orchestrator/modal_input_guard.py', 'orchestrator/modal_scientific_environment.py', 'orchestrator/experiment_environment_requirements.py', 'orchestrator/modal_development_inputs.py', 'orchestrator/review_contract.py')
RUNTIME_MODULES=('experiment_preprocessing','experiment_preprocessing_dispatch',
    'modal_development_inputs','modal_preprocessing_provider','experiment_worker')
FILES=tuple(dict.fromkeys(FILES+tuple('orchestrator/'+n+'.py' for n in RUNTIME_MODULES)
    +SUPPORT_FILES+('orchestrator/experiment_modal_package.py','orchestrator/manual_context.py',
        'orchestrator/item4_review4_continuation.py','docs/ITEM4_REVIEW4_CONTINUATION.json',SECOND_DOCUMENT,CONTINUATION_DOCUMENT,)))

GUIDANCE=(
 'Read the exact validator artifact and full current-six-item-backlog via their hashed workspace paths. '
 'Respond to the latest genuine scientific REVISE and every still-open finding, using the current accepted '
 'SPEC, notebook and execution plan. Preserved failed-author originals are historical evidence, not the current outputs. '
 'Read INPUT_PROVENANCE_RECONCILIATION.json and its exact native receipts, then NEXT_AUTHOR_EVIDENCE_POINTERS.md '
 'and PINNED_IMAGE_CONSUMER_PROOF.json; inspect the actual original files. '
 'The source inventories, baseline plans, handoff and runtime interfaces are supplied as exact files; '
 'availability alone is not scientific acceptance. Any newly authored semantic mapping is prospective, '
 'bound to genuine source bytes; never present it as an original historical manifest. '
 'The pinned image proof establishes package versions and CPU imports/interfaces only; it explicitly does '
 'not establish GPU operation or native preprocessing/training/scoring/checkpoint integration. '
 'Review6 confirms that both prior log filename defects are fixed, but actual author11 native CPU '
 'execution failed in validate_preprocessing: nnUNetDatasetBlosc2 rejects case_identifiers. '
 'Read the complete validator evidence; correct the pinned-library contract and audit adjacent native '
 'interfaces. Preserve the full integration harness; the controller reruns it before the next review. '
 'Address U1 explicitly using INPUT_PROVENANCE_RECONCILIATION.json and the original native download, '
 'cache rehash and baseline origin evidence. Decide whether a newly authored prospective source manifest '
 'can satisfy the actual installed contract and scientific provenance requirements. Never invent historical '
 'manifest bytes or describe a reconstructed manifest as historical. If originals are insufficient, state '
 'the exact missing binding and reason; scientific reviewer judges the proposal. '
 'You own the scientific changes and any synthetic native integration harness needed to address the findings. '
 'In this workspace use only synthetic checks; no provider calls, real patient computation or experiments. '
 'Independent scientific review and ordinary execution admission remain required; coverage arms remain held '
 'pending the review-required source evidence. Preserve all smoke, benchmark and full-training commitments. '
 'Read the provenance-validators and historical author5 SPEC originals via their hash-bound workspace paths. '
 'Keep SPEC at most12000 characters, preferably10000. Dailycap50; all other caps and past charges unchanged. '
 'Write SPEC.proposed.md, execution.plan.json and notebook.patch.json to the exact schema, call '
 'author_format.submit_author({}) and correct format errors within this call until ACCEPTED. '
 'Format acceptance is not scientific approval; only independent APPROVE closes findings.\n')

REVIEW_GUIDANCE=(
 'Read the exact validator artifact and full current-six-item-backlog via their hashed workspace paths. '
 'Review the actual scientific revision against every preserved finding. First read '
 'NEXT_AUTHOR_EVIDENCE_POINTERS.md and PINNED_IMAGE_CONSUMER_PROOF.json via the private evidence index, '
 'then the cited original baseline plans/handoff, recovered cache hashes, frozen auxiliary inventory, '
 'experiment_preprocessing.py, modal_preprocessed_contract.py, modal_nnunet.py and full runtime interfaces. '
 'Before reporting a required file absent, inspect its current indexed path. Historical CONTEXT and SPEC '
 'absence statements describe older attempts, not current delivery. Inspect the installed input schema '
 'and current _input_manifest implementation rather than assuming a historical schema is required. '
 'Delivery alone proves neither scientific adequacy nor native execution. Pending-review/open-finding '
 'labels preserve unresolved history; judge closure from evidence and retain every unsupported claim. '
 'For repeated U1, inspect actual source and authenticated underlying receipts: distinguish a missing '
 'historical manifest from a prospective author-owned manifest grounded in original hashes. Accept neither '
 'format alone nor an invented history; state the specific unsupported binding if provenance remains inadequate. '
 'Only genuine independent APPROVE closes findings. Preserve coverage holds and all other limitations. ')

def guidance(stage,base):
    from orchestrator.author_output_schema import schema
    return ((GUIDANCE+'Exact output schema: '+json.dumps(schema(),sort_keys=True)+'\n') if stage=='run_spec_author' else REVIEW_GUIDANCE) + base

def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def require(ok,why):
    if not ok:raise ValueError('SCIENTIFIC_REVISION_'+why)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m

def verified():
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_host_guard import trusted
    v=json.loads(trusted(RECORD/'installed.json').read_bytes())
    a=verify_result(Path(v['review_folder']))
    require(v['schema']=='reviewed-scientific-revision/v1' and v['root']==str(ROOT) and
        a['verdict']=='APPROVE' and a['change_id']==REVIEW_CHANGE and a['source_sha']==v['source'] and
        a['report_sha256']==v['review_sha256'] and a['runtime_sha256']==sha(trusted(RUNTIME).read_bytes()),'APPROVAL')
    manifest=json.loads(trusted(Path(v['review_folder'])/'packet-manifest.json').read_bytes())
    require(set(v['files'])==set(FILES),'FILE_SET')
    for name,pin in v['files'].items():require(sha(trusted(ROOT/name).read_bytes())==pin==manifest['source_files'][name],'SOURCE_CHANGED')
    for name,pin in {**v['base_files'],**v['units']}.items():require(sha(trusted(name).read_bytes())==pin,'BASE_CHANGED')
    b=json.loads(trusted(ROOT/'docs/ITEM4_REVISION_CHECKPOINT.json').read_bytes())
    for name,key in [(DOCS[0],'author_authority_sha256'),(DOCS[1],'autonomy_authority_sha256'),(DOCS[3],'evidence_manifest_sha256')]:
        require(sha(trusted(ROOT/'docs'/name).read_bytes())==b[key],'AUTHORITY_OR_EVIDENCE_CHANGED')
    evidence=json.loads(trusted(ROOT/'docs/ITEM4_REVISION_EVIDENCE.json').read_bytes())
    for row in evidence['files']:
        require(Path(row['name']).name==row['name'] and sha(trusted(RECORD/'evidence'/row['name']).read_bytes())==row['sha256'],'EVIDENCE_CHANGED')
    return v,b,evidence

def load():
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/'tools/item4_scientific_revision_component.py','OWNER_PATH')
    v,b,evidence=verified()
    prior=module('_revision_existing_context',PRIOR);_,_,h,old,rec=prior.load()
    import orchestrator
    # Keep existing class/module identities, so imported consumers cannot retain
    # stale admission/acceptance functions. Only these reviewed methods change.
    for name in ('author_revision_accounting','author_output_schema','revision_evidence','author_format_submission','author_format_retry'):
        setattr(orchestrator,name,module('orchestrator.'+name,ROOT/'orchestrator'/(name+'.py')))
    from orchestrator import manual_executor as me,manual_driver as md,manual_recovery as mr,experiment_approval as ea
    new=module('_revision_approval',ROOT/'orchestrator/experiment_approval.py')
    ea.verified_review_delivery=new.verified_review_delivery;ea.review_delivery=new.review_delivery
    newme=module('_revision_executor',ROOT/'orchestrator/manual_executor.py');me.ManualExecutor.reserve_call=newme.ManualExecutor.reserve_call
    newmd=module('_revision_driver',ROOT/'orchestrator/manual_driver.py');md.Driver._accept_completed=newmd.Driver._accept_completed
    newmr=module('_revision_recovery',ROOT/'orchestrator/manual_recovery.py');mr.role_limit=newmr.role_limit
    from orchestrator import author_revision_accounting as accounting,author_format_retry as retry
    prior_inspect=accounting.inspect
    accounting.inspect=lambda store,run,stage:retry.inspect(prior_inspect,store,run,stage,b)
    continuation=module('orchestrator.item4_review4_continuation',ROOT/'orchestrator/item4_review4_continuation.py')
    frozen=json.loads((ROOT/continuation.DOCUMENT).read_bytes())
    continuation.connect(accounting,mr,frozen,held_continuation_approval())
    second=json.loads((ROOT/SECOND_DOCUMENT).read_bytes())
    continuation.connect(accounting,mr,second,held_second_continuation_approval())
    current=json.loads((ROOT/CONTINUATION_DOCUMENT).read_bytes())
    continuation.connect(accounting,mr,current,held_third_continuation_approval())
    connect_runtime()
    return v,b,evidence,h,old,rec

def connect_runtime():
    """Keep consumer module identities; update explicit reviewed interfaces only."""
    from orchestrator import experiment_environment_requirements as req, manual_context as context
    from orchestrator import modal_development_inputs as source, experiment_preprocessing as prep
    from orchestrator import modal_preprocessing_provider as provider, experiment_worker as worker
    from orchestrator import experiment_modal_package as bridge, experiment_preprocessing_dispatch as dispatch
    delivery=module('_revision_workspace_delivery',ROOT/'orchestrator/manual_context.py')
    context.workspace_artifact=delivery.workspace_artifact
    context.build=delivery.build
    fresh={name:module('_revision_runtime_'+name,ROOT/'orchestrator'/(name+'.py'))
           for name in ('experiment_environment_requirements',*RUNTIME_MODULES)}
    req.runtime_preprocessing=fresh['experiment_environment_requirements'].runtime_preprocessing
    source.frozen_auxiliary=fresh['modal_development_inputs'].frozen_auxiliary
    source.AUXILIARY_CAPTURE=fresh['modal_development_inputs'].AUXILIARY_CAPTURE
    prep.scope=fresh['experiment_preprocessing'].scope
    prep.execute=fresh['experiment_preprocessing'].execute
    provider.input_files=fresh['modal_preprocessing_provider'].input_files
    worker.SUPPORT_FILES=fresh['experiment_worker'].SUPPORT_FILES
    worker.execute=fresh['experiment_worker'].execute
    bridge.SUPPORT_FILES=worker.SUPPORT_FILES
    bridge.WORKER=ROOT/'orchestrator/experiment_worker.py'
    dispatch.scientific_scope=prep.scope
    fresh['experiment_preprocessing_dispatch'].scientific_scope=prep.scope
    dispatch.validate_selection=fresh['experiment_preprocessing_dispatch'].validate_selection


def originals(driver,b,h,old,rec):
    require(str(driver.state.resolve())==str(LANE) and driver.config['run_id']==RUN and
        sha((LANE/'lane.json').read_bytes())==b['configuration_sha256'],'LANE_CHANGED')
    for table,pins,db in [('manual_calls',b['local_calls'],driver.store.db),('autonomy_calls',b['global_calls'],driver.store.batch.db)]:
        for ident,pin in pins.items():
            row=db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone()
            require(row is not None and sha(canonical(dict(row)))==pin,'ORIGINAL_CALL_OR_CHARGE_CHANGED')
    h.grant(driver,old,rec)

def apply():
    v,b,e,h,old,rec=load()
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator import private_records as pr,author_revision_accounting as accounting
    from orchestrator.manual_executor import lock
    d=ExperimentDriver(LANE)
    try:
        with lock(LANE/'driver.lock'):
            d.guard();originals(d,b,h,old,rec)
            require(not DEST.exists() and not DEST.is_symlink(),'EXISTS_RECONCILE')
            raw=d.store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
            require(sha(raw.encode())==b['state_sha256'] and not d.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'CHECKPOINT_CHANGED_OR_RUNNING')
            from orchestrator import author_format_retry as retry
            state=json.loads(raw)
            require(state['phase']=='BLOCKED' and state['reason']==b['format_recovery']['reason']
                and state['pending']['id']==b['format_recovery']['call_id'],'EXACT_SIZE_REFUSAL')
            classification=retry.qualify(d.store,RUN,b)
            pr.mkdir(DEST)
            pr.write_bytes(DEST/'original-state.json',raw.encode())
            state.pop('pending');state.update(phase='run_spec_author',reason=retry.REASON)
            state['interventions'].append({'kind':'REVIEWED_AUTHOR7_FORMAT_RECOVERY','review_sha256':v['review_sha256'],
                'authority_sha256':b['autonomy_authority_sha256'],'preserved_call':b['format_recovery']['call_id'],
                'next_author':8,'old_calls_and_charges_unchanged':True})
            d.save(state)
            pr.write_bytes(DEST/'applied.json',canonical({'status':'READY_NO_MODEL_CALL','review_sha256':v['review_sha256'],'classification':classification,'model_calls':0}))
            return {'status':'READY_NO_MODEL_CALL','model_calls':0}
    finally:d.store.db.close();d.store.batch.db.close()

def continue_review6():
    v,b,e,h,old,rec=load()
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    from orchestrator import item4_review4_continuation as continuation
    d=ExperimentDriver(LANE)
    try:
        with lock(LANE/'driver.lock'):
            d.guard();originals(d,b,h,old,rec);held_application()
            frozen=json.loads((ROOT/CONTINUATION_DOCUMENT).read_bytes())
            return continuation.activate(d,frozen,held_third_continuation_approval(),STATE/'item4'/'item4-review6-continuation-20261008')
    finally:d.store.db.close();d.store.batch.db.close()


def work_number(work):
    work=Path(work).resolve()
    match=re.fullmatch('run_spec_author-([0-9]+)',work.name)
    require(work.parent==STATE/'item4/lane-scientific-workspaces' and match is not None and 6<=int(match[1])<=20,'AUTHOR_WORKSPACE')
    return int(match[1])

def sender_profile(original,expected,commands,work,pins,*,sink=False,stage=None):
    from orchestrator import author_format_submission as af
    if sink or stage!='run_spec_author':return original(expected,commands,sink=sink,stage=stage)
    changed=[(name,af.client_command(command,work,pins) if name=='codex' else command) for name,command in commands]
    text=original(expected,changed,stage=stage)
    prefix=json.dumps([sys.executable,'-m','orchestrator.manual_stage','--send-bound'])[:-1]
    replacement=json.dumps([sys.executable,'-s','-B',str(ROOT/'tools/item4_scientific_revision_component.py'),'send'])[:-1]
    require(text.count(prefix)==2,'SENDER_PROFILE')
    return text.replace(prefix,replacement)

def send(expected,family,command):
    load();work=Path.cwd();n=work_number(work)
    from orchestrator import author_format_submission as af,manual_stage as ms
    require(family=='codex','SENDER_FAMILY')
    pins=json.loads((DEST/('runtime-pins-'+str(n)+'.json')).read_bytes());cfg=af.load(work,pins[af.CONFIG])
    require(cfg['bindings']['input_sha256']==expected and cfg['bindings']['round']==n,'SENDER_BINDING')
    base=['/tools/node','/tools/codex/bin/codex.js','exec','--ignore-user-config','--ignore-rules','--model','gpt-6-astra',
          '-s','workspace-write','-c','approval_policy="never"','-c','sandbox_workspace_write.network_access=false','--json','-']
    require(command==af.client_command(base,work,pins),'SENDER_COMMAND')
    original=ms.isolation.command
    def protected(workspace,*args,**kwargs):
        require(Path(workspace).resolve()==work.resolve(),'SENDER_WORKSPACE')
        return af.protect_command(original(workspace,*args,**kwargs),work,pins)
    ms.isolation.command=protected
    try:return ms.send_bound(expected,command,family=family)
    finally:ms.isolation.command=original

APPLICATION_SOURCE='d69a2914926b96d713ce235eb74db769725ad7d8'
APPLICATION_SHA='c42a0dc2241640db2601f2c5db7674bdbb99de60ae060b5c09e213f4a1239b6f'
APPLICATION_REVIEW='f052606f15793f8f4943768de8ac1ae2e8988e7c6fdd7429f8f3d090bd228e32'


def held_application():
    """Authenticate the original recovery independently of later code reviews."""
    from orchestrator import private_records as pr
    from orchestrator.manual_host_guard import trusted
    from orchestrator.autonomy_review import verify_result
    raw=pr.check(DEST/'applied.json').read_bytes()
    require(sha(raw)==APPLICATION_SHA,'HELD_APPLICATION_CHANGED')
    proof=json.loads(raw)
    original=verify_result(trusted(RECORD/'history'/APPLICATION_SOURCE/'original-review-directory'))
    require(original['verdict']=='APPROVE' and original['change_id']==CHANGE
        and original['source_sha']==APPLICATION_SOURCE and original['report_sha256']==APPLICATION_REVIEW
        and proof['review_sha256']==APPLICATION_REVIEW and proof['status']=='READY_NO_MODEL_CALL'
        and proof['model_calls']==0,'HELD_APPLICATION_APPROVAL')
    return APPLICATION_REVIEW


CONTINUATION_SOURCE='7ce4c1d90caa81937b3f3bad75cdc4f7657f1b45'
CONTINUATION_REVIEW='4b4b8c029305ae6c1a517f125abd0638592016dcf92a802be4c9a71ff4ee6350'


def held_continuation_approval():
    """Preserve author10's historical approval across this helper update."""
    from orchestrator.manual_host_guard import trusted
    from orchestrator.autonomy_review import verify_result
    proof=verify_result(trusted(RECORD/'history'/CONTINUATION_SOURCE/'original-review-directory'))
    require(proof['verdict']=='APPROVE' and proof['change_id']=='item4-review4-continuation-20261008'
        and proof['source_sha']==CONTINUATION_SOURCE and proof['report_sha256']==CONTINUATION_REVIEW,
        'HELD_CONTINUATION_APPROVAL')
    return CONTINUATION_REVIEW


SECOND_SOURCE='1d1e033c604f3664302ec4492dd92016a207b6c9'
SECOND_REVIEW='71f43725bf08fde663e337790a8863ed669446dcd9c97c755936204d8a22db23'

def held_second_continuation_approval():
    """Authenticate author11's own review, not the replacement implementation."""
    from orchestrator.manual_host_guard import trusted
    from orchestrator.autonomy_review import verify_result
    proof=verify_result(trusted(RECORD/'history'/SECOND_SOURCE/'original-review-directory'))
    require(proof['verdict']=='APPROVE' and proof['change_id']=='item4-review5-continuation-20261008'
        and proof['source_sha']==SECOND_SOURCE and proof['report_sha256']==SECOND_REVIEW,
        'HELD_SECOND_CONTINUATION_APPROVAL')
    return SECOND_REVIEW


THIRD_SOURCE='c1a712bc65a9baedf0788aaacd14fe9334801b55'
THIRD_REVIEW='d1b610fd3480254cbc5aa9700b42fa546d3c5e938e824faa223624b885824c5f'

def held_third_continuation_approval():
    """Preserve author12/review7 grant identity across delivery-only repair."""
    from orchestrator.manual_host_guard import trusted
    from orchestrator.autonomy_review import verify_result
    proof=verify_result(trusted(RECORD/'history'/THIRD_SOURCE/'original-review-directory'))
    require(proof['verdict']=='APPROVE' and proof['change_id']=='item4-review6-continuation-20261008'
        and proof['source_sha']==THIRD_SOURCE and proof['report_sha256']==THIRD_REVIEW,
        'HELD_THIRD_CONTINUATION_APPROVAL')
    return THIRD_REVIEW


def run():
    v,b,e,h,old,rec=load()
    from orchestrator import manual_recovery as mr,stocktake_review_recovery as sr,manual_stage as ms
    from orchestrator import scientific_intake as intake,revision_evidence,author_format_submission as af,private_records as pr
    from orchestrator.author_output_schema import schema
    from orchestrator.experiment_driver import ExperimentDriver
    require(json.loads((RECORD/'APPLIED.json').read_bytes())['status']=='INSTALLED_HELD','INSTALL_INCOMPLETE')
    saved=(mr.permit,sr.admission,ms._invoke,ms.transport_profile,intake.load_views)
    d=None;active={}
    from orchestrator import analysis_revisions, item4_review4_continuation as continuation
    prior_transition=analysis_revisions.review_transition
    frozen=json.loads((ROOT/CONTINUATION_DOCUMENT).read_bytes())
    def permit(store,run):
        prior=saved[0](store,run)
        if run!=RUN:return prior
        require(store is d.store and prior is not None,'LOCAL_OWNER')
        originals(d,b,h,old,rec)
        return {**prior,'preserved_failures':[prior['failed_id'],rec.CALL]}
    def admission(batch,run,stage,ident,source,receipt):
        if run!=RUN:return saved[1](batch,run,stage,ident,source,receipt)
        require(batch is d.store.batch and source==b['source'] and stage in ('run_spec_author','run_spec_review'),'GLOBAL_OWNER')
        originals(d,b,h,old,rec)
        n=d.store.db.execute('SELECT count(*) FROM manual_calls WHERE stage=?',(stage,)).fetchone()[0]+1
        require(ident==sha((RUN+':'+stage+':'+str(n)).encode()) and d.current()['phase']==stage,'NORMAL_NEXT_CALL')
        prior=saved[0](d.store,RUN);require(prior is not None,'TIMEOUT_QUALIFICATION')
        return [prior['failed_id'],rec.CALL]
    def views(root,ref,*,stage,idea_ids):
        descriptors,files=saved[4](root,ref,stage=stage,idea_ids=idea_ids)
        require(Path(root).resolve()==d.context.resolve() and ref==d.config['private_intake'] and
            stage in ('run_spec_author','run_spec_review') and idea_ids==d.config['idea_ids'],'EVIDENCE_DELIVERY_SCOPE')
        registry=json.loads((d.context/ref['path']).read_bytes())
        cases=intake.cohort((d.context/registry['cohort']).read_bytes())
        return revision_evidence.append(descriptors,files,e,RECORD/'evidence',cases)
    def profile(expected,commands,*,sink=False,stage=None):
        return sender_profile(saved[3],expected,commands,active.get('work'),active.get('pins'),sink=sink,stage=stage)
    def invoke(work,stage,clients,expected):
        if stage!='run_spec_author':return saved[2](work,stage,clients,expected)
        require(Path(work)==active['work'],'INVOCATION_WORKSPACE');pins=active['pins'];af.check_runtime(work,pins)
        result=saved[2](work,stage,clients,expected);af.check_runtime(work,pins)
        result['author_submission']=af.verify_native(work,pins[af.CONFIG],(Path(work)/'console.log').read_text())
        return result
    class RevisionDriver(ExperimentDriver):
        def task(self,stage,value):
            return guidance(stage,super().task(stage,value))
        def prepare_input(self,value,stage,work):
            body,measurement=super().prepare_input(value,stage,work)
            if stage=='run_spec_author':
                from orchestrator.author_revision_accounting import inspect
                n=work_number(work);binding=inspect(self.store,RUN,stage)['binding']
                if binding is None and n==8:
                    from orchestrator import author_format_retry as retry
                    binding=retry.context_binding(self.store,RUN,b)
                require(binding is not None and binding['author_attempt']==n,'REVISION_CLASSIFICATION')
                pins=af.prepare_revision(work,{'call_id':binding['author_call_id'],'run_id':RUN,'stage':stage,'round':n,
                    'source_sha':b['source'],'runtime_sha256':b['runtime_sha256'],'input_sha256':sha(body.encode())},
                    {k:binding[k] if k in binding else b[k] for k in ('review_call_id','review_sha256','operator_scope_sha256','original_sha256','view_sha256')})
                with pr.open_file(DEST/('runtime-pins-'+str(n)+'.json'),'xb') as f:f.write(canonical(pins))
                active.update(work=Path(work),pins=pins)
            return body,measurement
        def _advance(self,*args,**kwargs):
            self.guard();originals(self,b,h,old,rec)
            require(self.current()['phase'] in ('run_spec_author','run_spec_review') and not self.current().get('pending'),'ONE_NEXT_SCIENTIFIC_STAGE')
            return super()._advance(*args,**kwargs)
    try:
        d=RevisionDriver(LANE)
        held_application()
        mr.permit,sr.admission,ms._invoke,ms.transport_profile,intake.load_views=permit,admission,invoke,profile,views
        analysis_revisions.review_transition=lambda review,stage,n:continuation.terminal_transition(
            prior_transition,d,review,stage,n,frozen,held_third_continuation_approval())
        return d.advance()
    finally:
        analysis_revisions.review_transition=prior_transition
        mr.permit,sr.admission,ms._invoke,ms.transport_profile,intake.load_views=saved
        if d is not None:d.store.db.close();d.store.batch.db.close()

if __name__=='__main__':
    os.umask(0o077)
    if sys.argv[1:]==['verify']:v,*_=load();print(json.dumps({'status':'VERIFIED_HELD','source':v['source'],'model_calls':0}))
    elif sys.argv[1:]==['apply']:print(json.dumps(apply(),sort_keys=True))
    elif sys.argv[1:]==['continue-review6']:print(json.dumps(continue_review6(),sort_keys=True))
    elif sys.argv[1:]==['run']:print(json.dumps(run(),sort_keys=True))
    elif len(sys.argv)>5 and sys.argv[1]=='send' and sys.argv[4]=='--':raise SystemExit(send(sys.argv[2],sys.argv[3],sys.argv[5:]))
    else:raise SystemExit('FIXED_REVISION_ACTION_REQUIRED')
