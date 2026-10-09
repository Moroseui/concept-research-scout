"""Reviewed 13B revision connection; original engine/jail/admission remain in use."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

CHANGE='item4-author7-and-image-recovery-20261008'
REVIEW_CHANGE='item4-review9-staged-continuation-20261009'
RESPONSE_DOCUMENT='docs/ITEM4_REVIEW9_CONTINUATION.json'
PRE_ADMISSION_DOCUMENT='docs/ITEM4_REVIEW9_PRE_ADMISSION.json'
MECHANICAL_SOURCE='ed9ad9aead00c9df8d0ecae1a25ecd782aef169c'
MECHANICAL_REVIEW='6f7742d5f7f7ceaead77a75e66e2ef068f5ff6ef50915945fbc9dcebbeacf4cf'
RECOVERY_DOCUMENT='docs/ITEM4_REVIEW8_MECHANICAL_RECOVERY.json'
PROOF_DOCUMENT='docs/ITEM4_REVIEW8_PREREQUISITES.json'
CONTINUATION_DOCUMENT='docs/ITEM4_REVIEW7_CONTINUATION.json'
THIRD_DOCUMENT='docs/ITEM4_REVIEW6_CONTINUATION.json'
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
    +SUPPORT_FILES+('orchestrator/experiment_modal_package.py','orchestrator/manual_context.py','orchestrator/context_budget.py',
        'orchestrator/item4_review4_continuation.py','docs/ITEM4_REVIEW4_CONTINUATION.json',SECOND_DOCUMENT,THIRD_DOCUMENT,CONTINUATION_DOCUMENT,
        'orchestrator/item4_scoped_calls.py','orchestrator/dispatch_limiter.py',
        'tools/item4_review8_proof.py',PROOF_DOCUMENT,
        'orchestrator/item4_review8_recovery.py',RECOVERY_DOCUMENT,PRE_ADMISSION_DOCUMENT,RESPONSE_DOCUMENT,)))

GUIDANCE=(
 'Respond to genuine scientific REVISE9 and every still-open finding. Read the exact full report, '
 'current accepted SPEC, notebook, plan, validator and full current-six-item-backlog. '
 'Read SOURCE_BINDING.json, SOURCE_VERIFIED.json, SOURCE_LOCAL_VERIFIED.json and SOURCE_VOLUME.json '
 'through the evidence index: base-source composition now passed original/frozen hashes and full '
 '893-file byte readback,99 development patients,49 excluded and zero overlap. These records do not '
 'prove the missing coverage inventory or a future production execution root. Read NATIVE_BINDING.json, '
 'NATIVE_OUTPUT.json, NATIVE_VERIFIED.json and NATIVE_TERMINAL.json: exact author13 module passed '
 'pinned-image synthetic CPU preparation, reuse, genuine interruption/resume and scoring. '
 'Review9 closes the concrete nnUNetDatasetBlosc2 API defect, but synthetic CPU evidence does not '
 'establish real production/GPU integration, patient efficacy or provider-volume durability. '
 'Update stale SPEC claims honestly. Decide the smallest scientifically defensible next validation '
 'stage and distinguish pre-execution permission from acceptance of resulting evidence. State precisely '
 'which findings require proof before launch and which can only be resolved by an admitted validation '
 'run; do not close findings by promise. The independent scientific reviewer judges this proposal. '
 'Preserve all51 fits,seven preparations,40 FULL fits,three GPU benchmarks and subsequent smoke/full '
 'commitments; coverage-dependent zscore/histeq/derived_ctp_support remain held until required evidence '
 'and method are accepted. Do not invent originals or replace the full goal with a limited smoke. '
 'Read original provenance receipts, NEXT_AUTHOR_EVIDENCE_POINTERS.md and PINNED_IMAGE_CONSUMER_PROOF.json. '
 'Current native proof binds the author13 executable module exactly; changed scientific code requires '
 'fresh applicable integration evidence, never a false claim that old receipts prove new code. '
 'You own scientific choices and code. Make necessary corrections, preserving unchanged code when '
 'only documentation is deficient. This author workspace permits synthetic checks only, no provider '
 'calls or patient computation. The controller reruns the full synthetic harness on your submission. '
 'Ordinary execution, confinement, input, image and spending checks remain mandatory. '
 'SPEC maximum12000 characters, preferably10000. Dailycap50; this reviewed continuation has exactly '
 'author14/review10 plus final post-execution interpretation pair, scopedcap26,22 prior calls retained. '
 'Write SPEC.proposed.md, execution.plan.json and notebook.patch.json to the exact output schema; '
 'call author_format.submit_author({}) and correct format errors within this call until ACCEPTED. '
 'Format acceptance and administrative process approval are not scientific approval.\n')

REVIEW_GUIDANCE=(
 'Read the exact validator artifact and full current-six-item-backlog via their hashed workspace paths. '
 'Review the author14 response to genuine REVISE9 against every preserved finding. Judge the proposed '
 'staging of pre-execution permission separately from acceptance of validation results; do not waive '
 'missing preconditions or treat administrative opinion as scientific approval. First read '
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
 'Read SOURCE_BINDING.json, SOURCE_VERIFIED.json, SOURCE_LOCAL_VERIFIED.json and SOURCE_VOLUME.json; '
 'the reviewed service bound these originals to the frozen inventory and full composed-volume byte readback. '
 'Read NATIVE_OUTPUT.json, NATIVE_VERIFIED.json, NATIVE_BINDING.json and NATIVE_TERMINAL.json for actual '
 'author13 synthetic native CPU execution in the pinned image, applicable only to the exact tested module. These are original receipts, not patient '
 'efficacy, GPU validation, production-main execution or scientific approval. Judge U1/U2 against these '
 'new proofs; preserve U3 coverage holds and distinct later execution/confinement/budget gates. '
 'Only genuine independent APPROVE closes findings. Preserve coverage holds and all other limitations. ')

DIRECT_REVIEW_EVIDENCE=('evidence/40860aa053572ffc0571e45c89b950eaf813725b107f981ad18d5b9921cdb59c-revision-NATIVE_BINDING.json', 'evidence/1eda41750da41c1953fb4721fdaf2a0d26ecb488cc92409ab0fc0bb3e3352631-revision-NATIVE_OUTPUT.json', 'evidence/679fafe1eb3ea06dd449dae12e71d3e2358fb73523eba7457f30b78b21b56b17-revision-NATIVE_TERMINAL.json', 'evidence/0204237b70ac72daccfb5121a5d6f07b5d649602b540ceca7c7380e6be3ab941-revision-NATIVE_VERIFIED.json', 'evidence/ae2effda304d00c028bc1c5c1e554ddeb62d9594b80c2bfe32505b908b9b7927-revision-NEXT_AUTHOR_EVIDENCE_POINTERS.md', 'evidence/cf52d2e04f0a1052ca533af0e7b91af71a8b6eb18bc5762aedb72179fdf615ef-revision-PINNED_IMAGE_CONSUMER_PROOF.json', 'evidence/9878e7923ea81dceefce162166a113aa7d0a53dd65c4199a42b4276fe952d365-revision-SOURCE_BINDING.json', 'evidence/b715ce005f597e0730ca51285fedd98e81bc97f4e66c9b4003068dfd9fcc95db-revision-SOURCE_LOCAL_VERIFIED.json', 'evidence/48e9635cd74cb45d2428ac60153e49af0052a8201dec481adb836984e236785e-revision-SOURCE_VERIFIED.json', 'evidence/e7d3c2478ba4f92c6989f8b5113432e12aea1f762789f76717fa066cb0eed998-revision-SOURCE_VOLUME.json')

def evidence_navigation():
    return ('This is scientific review10 of author14, answering genuine REVISE9; it is not a mechanical replacement. '
        'Use these exact original paths; readable copies and full indexes remain available. '
        'The call has at most60 turns. Submit your independent judgment using submit_review before that limit; '
        'retain unresolved findings if evidence is insufficient. No prior partial commentary is a verdict.\n'+
        '\n'.join(DIRECT_REVIEW_EVIDENCE)+'\n')

def guidance(stage,base):
    from orchestrator.author_output_schema import schema
    return ((GUIDANCE+'Exact output schema: '+json.dumps(schema(),sort_keys=True)+'\n') if stage=='run_spec_author' else evidence_navigation()+REVIEW_GUIDANCE) + base

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
    require(set(DIRECT_REVIEW_EVIDENCE)<=set('evidence/'+row['sha256']+'-revision-'+row['name'] for row in evidence['files']),'DIRECT_EVIDENCE_PATHS')
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
    md.Driver.model_round_number=newmd.Driver.model_round_number;md.Driver._model_step=newmd.Driver._model_step
    newmr=module('_revision_recovery',ROOT/'orchestrator/manual_recovery.py');mr.role_limit=newmr.role_limit
    from orchestrator import author_revision_accounting as accounting,author_format_retry as retry
    prior_inspect=accounting.inspect
    accounting.inspect=lambda store,run,stage:retry.inspect(prior_inspect,store,run,stage,b)
    continuation=module('orchestrator.item4_review4_continuation',ROOT/'orchestrator/item4_review4_continuation.py')
    frozen=json.loads((ROOT/continuation.DOCUMENT).read_bytes())
    continuation.connect(accounting,mr,frozen,held_continuation_approval())
    second=json.loads((ROOT/SECOND_DOCUMENT).read_bytes())
    continuation.connect(accounting,mr,second,held_second_continuation_approval())
    third=json.loads((ROOT/THIRD_DOCUMENT).read_bytes())
    continuation.connect(accounting,mr,third,held_third_continuation_approval())
    current=json.loads((ROOT/CONTINUATION_DOCUMENT).read_bytes())
    continuation.connect(accounting,mr,current,held_fourth_continuation_approval())
    from orchestrator import dispatch_limiter
    limiter=module('_revision_dispatch_limiter',ROOT/'orchestrator/dispatch_limiter.py')
    dispatch_limiter.admit_manual=limiter.admit_manual
    dispatch_limiter.validate=limiter.validate
    calls=module('orchestrator.item4_scoped_calls',ROOT/'orchestrator/item4_scoped_calls.py')
    repair=module('orchestrator.item4_review8_recovery',ROOT/'orchestrator/item4_review8_recovery.py')
    mechanical=json.loads((ROOT/RECOVERY_DOCUMENT).read_bytes())
    response=json.loads((ROOT/RESPONSE_DOCUMENT).read_bytes())
    continuation.connect(accounting,mr,response,v['review_sha256'])
    calls.connect(current,held_fourth_continuation_approval(),mechanical=mechanical,
        mechanical_approval=held_mechanical_approval(),response=response,response_approval=v['review_sha256'])
    connect_runtime()
    return v,b,evidence,h,old,rec

def connect_runtime():
    """Keep consumer module identities; update explicit reviewed interfaces only."""
    from orchestrator import experiment_environment_requirements as req, manual_context as context
    from orchestrator import modal_development_inputs as source, experiment_preprocessing as prep
    from orchestrator import modal_preprocessing_provider as provider, experiment_worker as worker
    from orchestrator import experiment_modal_package as bridge, experiment_preprocessing_dispatch as dispatch
    delivery=module('_revision_workspace_delivery',ROOT/'orchestrator/manual_context.py')
    from orchestrator import context_budget
    budget_module=module('_revision_context_budget',ROOT/'orchestrator/context_budget.py')
    context_budget.assemble=budget_module.assemble
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

def held_mechanical_approval():
    from orchestrator.manual_host_guard import trusted
    from orchestrator.autonomy_review import verify_result
    proof=verify_result(trusted(RECORD/'history'/MECHANICAL_SOURCE/'original-review-directory'))
    require(proof['verdict']=='APPROVE' and proof['change_id']=='item4-review8-turn-recovery-20261009'
        and proof['source_sha']==MECHANICAL_SOURCE and proof['report_sha256']==MECHANICAL_REVIEW,
        'HELD_MECHANICAL_APPROVAL')
    return MECHANICAL_REVIEW

def restore_review9():
    v,b,e,h,old,rec=load()
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    from orchestrator import item4_review8_recovery as repair
    d=ExperimentDriver(LANE)
    try:
        with lock(LANE/'driver.lock'):
            d.guard();originals(d,b,h,old,rec);held_application()
            return repair.restore_pre_admission(d,json.loads((ROOT/RECOVERY_DOCUMENT).read_bytes()),
                held_mechanical_approval(),v['review_sha256'],json.loads((ROOT/PRE_ADMISSION_DOCUMENT).read_bytes()),
                STATE/'item4'/'item4-review9-workspace-repair-20261009')
    finally:d.store.db.close();d.store.batch.db.close()

def recover_review8():
    v,b,e,h,old,rec=load()
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    from orchestrator import item4_review8_recovery as repair
    d=ExperimentDriver(LANE)
    try:
        with lock(LANE/'driver.lock'):
            d.guard();originals(d,b,h,old,rec);held_application()
            return repair.activate(d,json.loads((ROOT/RECOVERY_DOCUMENT).read_bytes()),held_mechanical_approval(),
                STATE/'item4'/'item4-review8-turn-recovery-20261009')
    finally:d.store.db.close();d.store.batch.db.close()

def continue_review9():
    v,b,e,h,old,rec=load()
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    from orchestrator import item4_review4_continuation as continuation
    d=ExperimentDriver(LANE)
    try:
        with lock(LANE/'driver.lock'):
            d.guard();originals(d,b,h,old,rec);held_application()
            return continuation.activate(d,json.loads((ROOT/RESPONSE_DOCUMENT).read_bytes()),
                v['review_sha256'],STATE/'item4'/REVIEW_CHANGE)
    finally:d.store.db.close();d.store.batch.db.close()


def continue_review7():
    v,b,e,h,old,rec=load()
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    from orchestrator import item4_review4_continuation as continuation
    d=ExperimentDriver(LANE)
    try:
        with lock(LANE/'driver.lock'):
            d.guard();originals(d,b,h,old,rec);held_application()
            frozen=json.loads((ROOT/CONTINUATION_DOCUMENT).read_bytes())
            return continuation.activate(d,frozen,held_fourth_continuation_approval(),STATE/'item4'/'item4-review7-continuation-20261009')
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



FOURTH_SOURCE='46583c209b65a75c98c29aa3ea0b47802ace251f'
FOURTH_REVIEW='27aedad79b9021e61458d884c2acab2d7e9c9cb131322c7d8edbf9a8042e6096'

def held_fourth_continuation_approval():
    """Delivery approval cannot replace or expand the existing author13/review8 grant."""
    from orchestrator.manual_host_guard import trusted
    from orchestrator.autonomy_review import verify_result
    proof=verify_result(trusted(RECORD/'history'/FOURTH_SOURCE/'original-review-directory'))
    require(proof['verdict']=='APPROVE' and proof['change_id']=='item4-review7-continuation-20261009'
        and proof['source_sha']==FOURTH_SOURCE and proof['report_sha256']==FOURTH_REVIEW,
        'HELD_FOURTH_CONTINUATION_APPROVAL')
    return FOURTH_REVIEW

def review8_prerequisites(driver,evidence):
    """Equivalent concrete replacement for the temporary no-proof review hold."""
    import subprocess
    from orchestrator.manual_host_guard import trusted
    current=driver.current()
    require(current['phase']=='run_spec_review' and not current.get('pending')
        and current['rounds']=={'run_spec_author':13,'run_spec_review':7}
        and driver.store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==21,
        'REVIEW8_EXACT_STAGE')
    from orchestrator import item4_review8_recovery as repair
    installed,*_=verified()
    repair.next_review(driver.store,json.loads(trusted(ROOT/RECOVERY_DOCUMENT).read_bytes()),held_mechanical_approval())
    expected=json.loads(trusted(ROOT/PROOF_DOCUMENT).read_bytes())
    result=subprocess.run([sys.executable,'-s','-B',str(ROOT/'tools/item4_review8_proof.py')],
        capture_output=True,text=True,timeout=180)
    require(result.returncode==0,'REVIEW8_PREREQUISITES_FAILED')
    require(json.loads(result.stdout)==expected,'REVIEW8_PREREQUISITES_CHANGED')
    rows={row['name']:row for row in evidence['files']}
    for name,pin in expected['files'].items():
        require(name in rows and {k:rows[name][k] for k in ('sha256','bytes')}==pin,
            'REVIEW8_PROOF_NOT_DELIVERED')
    return expected

def response_stage(driver,frozen,approval):
    """Qualify the exact next stage before workspace creation or model admission."""
    from orchestrator import item4_review4_continuation as continuation,author_revision_accounting as accounting
    rows=continuation.originals(driver.store,RUN,frozen);continuation.granted(driver.store,frozen,approval)
    value=driver.current();stage=value['phase']
    expected={'run_spec_author':(22,13,9,14),'run_spec_review':(23,14,9,10)}
    require(driver.config['run_id']==RUN and stage in expected and not value.get('pending'),'RESPONSE_STAGE')
    count,author,review,attempt=expected[stage]
    require(len(rows)==count and value['rounds']=={'run_spec_author':author,'run_spec_review':review},'RESPONSE_ROUNDS')
    if stage=='run_spec_author':
        require(value.get('reason')==continuation.reason(frozen),'RESPONSE_REASON')
    else:
        row=rows[-1]
        require(row['stage']=='run_spec_author' and row['attempt']==14 and accounting._accepted(driver.store,row),'RESPONSE_AUTHOR')
        expected_binding=continuation.review_binding(driver,frozen,approval)
        require(json.loads(row['receipt']).get(accounting.FIELD)==expected_binding,'RESPONSE_AUTHOR_BINDING')
    return attempt


def response_model_attempt(driver,value,frozen,approval):
    from orchestrator import item4_review4_continuation as continuation
    require(value==continuation.state(driver.store),'RESPONSE_MODEL_STATE')
    return response_stage(driver,frozen,approval)


def response_reviewer_command(original,workspace,stage,driver,frozen,approval):
    """Only normally admitted scientific review10 receives the existing60-turn reader budget."""
    argv=original(workspace,stage)
    if stage!='run_spec_review':return argv
    from orchestrator import item4_review4_continuation as continuation
    rows=continuation.originals(driver.store,RUN,frozen);continuation.granted(driver.store,frozen,approval)
    value=driver.current();pending=value.get('pending') or {}
    expected=driver.state.parent/(driver.state.name+'-scientific-workspaces')/'run_spec_review-10'
    ident=sha((RUN+':run_spec_review:10').encode())
    require(driver.config['run_id']==RUN and Path(workspace).resolve()==expected.resolve()
        and value['phase']=='MODEL_RUNNING' and pending.get('id')==ident and pending.get('round')==10
        and pending.get('stage')==stage and Path(pending.get('workspace','')).resolve()==expected.resolve() and value['rounds']=={'run_spec_author':14,'run_spec_review':9}
        and len(rows)==24,'RESPONSE_COMMAND_SCOPE')
    for db,table in [(driver.store.db,'manual_calls'),(driver.store.batch.db,'autonomy_calls')]:
        row=db.execute('SELECT status FROM '+table+' WHERE id=?',(ident,)).fetchone()
        require(row is not None and row[0]=='RUNNING','RESPONSE_COMMAND_ADMISSION')
    require(argv.count('--max-turns')==1 and argv[argv.index('--max-turns')+1]=='30','RESPONSE_COMMAND_SHAPE')
    argv[argv.index('--max-turns')+1]='60'
    return argv


def response_prerequisites(driver,evidence,frozen,approval):
    import subprocess
    from orchestrator.manual_host_guard import trusted
    response_stage(driver,frozen,approval)
    expected=json.loads(trusted(ROOT/PROOF_DOCUMENT).read_bytes())
    result=subprocess.run([sys.executable,'-s','-B',str(ROOT/'tools/item4_review8_proof.py')],
        capture_output=True,text=True,timeout=180)
    require(result.returncode==0,'RESPONSE_PREREQUISITES_FAILED')
    require(json.loads(result.stdout)==expected,'RESPONSE_PREREQUISITES_CHANGED')
    rows={row['name']:row for row in evidence['files']}
    for name,pin in expected['files'].items():
        require(name in rows and {k:rows[name][k] for k in ('sha256','bytes')}==pin,'RESPONSE_PROOF_NOT_DELIVERED')
    # Historical proof is explicitly author13. A changed executable needs fresh proof.
    if driver.current()['phase']=='run_spec_review':
        response_native_equivalence(driver,frozen)
    return expected


def response_native_equivalence(driver,frozen):
    from orchestrator import private_records as pr,notebook_execution
    value=driver.current();result=value['notebook_revision_result']
    folder=driver.state/'notebook-revisions/author-14'
    require(result['folder']==str(folder) and result['synthetic_status']=='PASS','RESPONSE_CONTROLLER')
    raw=pr.check(folder/'revised.ipynb').read_bytes()
    require(sha(raw)==result['notebook_sha256'],'RESPONSE_NOTEBOOK')
    tests=pr.check(folder/'synthetic/receipt.json').read_bytes();receipt=json.loads(tests)
    require(sha(canonical(receipt))==result['tests_sha256'] and receipt['status']=='PASS'
        and receipt['exit_code']==0 and receipt['binding']['files']['revised.ipynb']==sha(raw)
        and pr.check(folder/'synthetic/package/revised.ipynb').read_bytes()==raw,'RESPONSE_TEST_RECEIPT')
    module=notebook_execution.extract(raw,preprocessing=True)
    require(module==pr.check(folder/'synthetic/package/execution.py').read_bytes()
        and sha(module)==frozen['historical_science']['execution_sha256']
        and receipt['binding']['files']['execution.py']==sha(module),'RESPONSE_CHANGED_MODULE_NEEDS_NATIVE_PROOF')
    require(receipt['binding']['environment']==frozen['historical_science']['controller_environment'],'RESPONSE_TEST_ENVIRONMENT')
    for name,pin in frozen['historical_science']['native_files'].items():
        require(receipt['binding']['files'].get(name)==pin and
            sha(pr.check(folder/'synthetic/package'/name).read_bytes())==pin,'RESPONSE_NATIVE_SUPPORT_CHANGED')
    for name,pin in receipt['preserved_files'].items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts,'RESPONSE_TEST_PATH')
        require(sha(pr.check(folder/'synthetic'/name).read_bytes())==pin,'RESPONSE_TEST_CHANGED')
    for ident,pin in [('notebook_source',result['notebook_sha256']),('synthetic_tests',result['tests_sha256'])]:
        require(any(a['id']==ident and a['version']==14 and a['sha256']==pin for a in value['artifacts']),
            'RESPONSE_ARTIFACT_BINDING')


def run():
    v,b,e,h,old,rec=load()
    from orchestrator import manual_recovery as mr,stocktake_review_recovery as sr,manual_stage as ms
    from orchestrator import scientific_intake as intake,revision_evidence,author_format_submission as af,private_records as pr
    from orchestrator.author_output_schema import schema
    from orchestrator.experiment_driver import ExperimentDriver
    require(json.loads((RECORD/'APPLIED.json').read_bytes())['status']=='INSTALLED_HELD','INSTALL_INCOMPLETE')
    saved=(mr.permit,sr.admission,ms._invoke,ms.transport_profile,intake.load_views,ms.reviewer_command)
    d=None;active={}
    from orchestrator import item4_review8_recovery as repair
    mechanical=json.loads((ROOT/RECOVERY_DOCUMENT).read_bytes())
    from orchestrator import analysis_revisions, item4_review4_continuation as continuation
    prior_transition=analysis_revisions.review_transition
    frozen=json.loads((ROOT/RESPONSE_DOCUMENT).read_bytes())
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
    def reviewer_command(work,stage):
        return response_reviewer_command(saved[5],work,stage,d,frozen,v['review_sha256'])
    def transition(review,stage,n):
        return continuation.terminal_transition(prior_transition,d,review,stage,n,frozen,v['review_sha256'])
    class RevisionDriver(ExperimentDriver):
        def model_round_number(self,value):
            return response_model_attempt(self,value,frozen,v['review_sha256'])
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
            response_prerequisites(self,e,frozen,v['review_sha256'])
            return super()._advance(*args,**kwargs)
    try:
        d=RevisionDriver(LANE)
        held_application()
        mr.permit,sr.admission,ms._invoke,ms.transport_profile,intake.load_views,ms.reviewer_command=permit,admission,invoke,profile,views,reviewer_command
        analysis_revisions.review_transition=transition
        return d.advance()
    finally:
        analysis_revisions.review_transition=prior_transition
        mr.permit,sr.admission,ms._invoke,ms.transport_profile,intake.load_views,ms.reviewer_command=saved
        if d is not None:d.store.db.close();d.store.batch.db.close()

if __name__=='__main__':
    os.umask(0o077)
    if sys.argv[1:]==['verify']:v,*_=load();print(json.dumps({'status':'VERIFIED_HELD','source':v['source'],'model_calls':0}))
    elif sys.argv[1:]==['apply']:print(json.dumps(apply(),sort_keys=True))
    elif sys.argv[1:]==['restore-review9']:print(json.dumps(restore_review9(),sort_keys=True))
    elif sys.argv[1:]==['recover-review8']:print(json.dumps(recover_review8(),sort_keys=True))
    elif sys.argv[1:]==['continue-review9']:print(json.dumps(continue_review9(),sort_keys=True))
    elif sys.argv[1:]==['continue-review7']:print(json.dumps(continue_review7(),sort_keys=True))
    elif sys.argv[1:]==['run']:print(json.dumps(run(),sort_keys=True))
    elif len(sys.argv)>5 and sys.argv[1]=='send' and sys.argv[4]=='--':raise SystemExit(send(sys.argv[2],sys.argv[3],sys.argv[5:]))
    else:raise SystemExit('FIXED_REVISION_ACTION_REQUIRED')
