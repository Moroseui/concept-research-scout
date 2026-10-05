"""M3's bounded Sprint9 lane, reusing the reviewed manual scientific stages.

One transition per invocation. No scheduler or automatic retry; the later M5
service drives these same transitions. Model inputs only use manual_context.
"""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import subprocess
import time

from orchestrator import private_records,manual_context,manual_stage,modal_package
from orchestrator.manual_driver import Driver,PROFILE,STAGES,CATEGORIES,git,stamp,write_once
from orchestrator.manual_executor import ManualExecutor,read,digest,atomic
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_executor import ModalExecutor,canonical
from orchestrator.modal_provider import ModalProvider
from orchestrator.modal_budget import estimate,SMOKE_CAP
from orchestrator.sprint9_modal_validation import validate
from orchestrator.git_publication import scan


@private_records.private_umask
def initialize(root,state,engine_review,plan_path):
    root,state,engine_review,plan_path=map(Path,(root,state,engine_review,plan_path))
    if git(root,'status','--porcelain'):raise ValueError('CLEAN_REVIEWED_SOURCE_REQUIRED')
    source=git(root,'rev-parse','HEAD');branch=git(root,'branch','--show-current');report=engine_review.read_text()
    if source not in report or re.findall(r'^## Verdict: (.+?)\s*$',report,re.M)!=['APPROVE']:raise ValueError('EXACT_ENGINE_REVIEW_REQUIRED')
    if not branch.startswith('astra/'):raise ValueError('REVIEWED_WORK_BRANCH_REQUIRED')
    if state.exists():raise ValueError('EXISTING_MODAL_LANE_RECONCILE')
    git(root,'var','GIT_AUTHOR_IDENT');git(root,'var','GIT_COMMITTER_IDENT')
    plan=read(plan_path);runtime=plan['runtime'];smoke=read(plan['smoke_path'])
    from experiments.sprint9_modal.worker import validate_config,CONTRACT
    if runtime['input_contract']!=CONTRACT:raise ValueError('M3_KNOWN_COHORT_REQUIRED')
    validate_config(smoke,runtime['input_contract'])
    # The concrete asset preparation receipt must be complete before any model
    # call. Preparation cost and provenance are not inferred from this initializer.
    receipt=read(plan['preparation_receipt'])
    if (digest(Path(plan['preparation_receipt']).read_bytes())!=plan['preparation_sha256'] or receipt.get('status')!='READY' or
        receipt.get('runtime_sha256')!=digest(canonical(runtime)) or receipt.get('source')!=source):raise ValueError('MODAL_PREPARATION_NOT_READY')
    cost=estimate(plan['resources'],plan['overhead_micro_usd'])
    if cost['reserved_micro_usd']>SMOKE_CAP:raise ValueError('M3_SMOKE_COST_CAP')
    accounts=BatchAccounts(runtime['batch_ledger'])
    from orchestrator.modal_budget import ComputeAccounts
    ComputeAccounts(accounts)
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(receipt['reservation_id'],)).fetchone()
    if row is None or row['status']!='READY' or json.loads(row['receipt'])!=receipt:raise ValueError('MODAL_PREPARATION_ACCOUNTING_REQUIRED')
    if cost['reserved_micro_usd']+row['reserved_micro_usd']>SMOKE_CAP:raise ValueError('M3_PREPARATION_AND_RUN_COST_CAP')
    clients=manual_stage.preflight()
    authority=root/'docs/AUTONOMY_BATCH_2026-09-27.md';raw=authority.read_bytes();text=raw.decode()
    run_id='sprint9-modal-'+digest((source+digest(engine_review.read_bytes())).encode())[:16]
    if receipt.get('run_id')!=run_id:raise ValueError('MODAL_PREPARATION_RUN_BINDING')
    common=Path(git(root,'rev-parse','--git-common-dir'));common=common if common.is_absolute() else root/common
    owner=common.resolve()/'autonomy-modal-smoke-owner.json'
    if owner.exists():raise ValueError('EXISTING_CANONICAL_ACCEPTANCE_USE_SAVED_STATE')
    private_records.mkdir(state,parents=True);context=state/'context';private_records.mkdir(context)
    manifest=read(root/PROFILE/'manifest.json')
    files={row['path'] for row in manifest['sources']}|{str(p.relative_to(root)) for p in (root/PROFILE).rglob('*') if p.is_file()}
    for name in files:
        dest=context/name;private_records.mkdir(dest.parent,parents=True,exist_ok=True);private_records.copyfile(root/name,dest)
    current=context/'current';private_records.mkdir(current)
    name='current/autonomy-batch-authority.md';write_once(context/name,raw)
    registry=read(context/PROFILE/'obligations.json');profile=read(context/PROFILE/'manifest.json')
    for label,start_text,end_text in [('stops','## Standing rules','**Reviews are automated.**'),('caps','**Caps, until I raise them:**','**Freeze:**'),
                                      ('m3','**M3: GPU executor','**M4: Closing the loop'),('old-routes','## Operator amendment: M4 successor contract','## Observed-outage amendment')]:
        start=text.index(start_text);end=text.index(end_text,start);quote=text[start:end];begin=len(text[:start].encode())
        registry['obligations'].append({'id':'AUTONOMY20260927-M3-'+label,'type':'protocol amendment','status':'open','severity':'major',
          'scope':{'project':['isles24-prediction'],'idea_ids':['Sprint9'],'stages':['*']},'text':quote,
          'source':{'path':name,'sha256':digest(raw),'start':begin,'end':begin+len(quote.encode()),'original_path':str(authority.relative_to(root))},'disposition':None})
    atomic(context/PROFILE/'obligations.json',registry);profile['obligations']['sha256']=digest((context/PROFILE/'obligations.json').read_bytes())
    profile['sources'].append({'path':name,'sha256':digest(raw)});atomic(context/PROFILE/'manifest.json',profile)
    rows=[]
    def artifact(kind,name,body):
        if not isinstance(body,bytes):body=(json.dumps(body,sort_keys=True,indent=2)+'\n').encode()
        scan('context/current.txt',body);write_once(current/name,body)
        rows.append({'id':kind,'type':kind,'version':1,'path':'current/'+name,'sha256':digest(body)})
    artifact('question','question.md',b'Can the existing two-epoch Sprint9 U_base development fold be reproduced through the server-owned GPU execution lane within the predeclared tolerance? This verifies execution; it is not new efficacy evidence.\n')
    code=b'\n\n'.join(name.encode()+b'\n'+data for name,data in modal_package.source_files(root).items())
    artifact('notebook_source','reviewed-source.txt',code)
    artifact('configuration','configuration.json',{'cnn':smoke['cnn'],'feature_cfg':smoke['feature_cfg'],'versions':smoke['versions'],'resources':plan['resources'],'cost':cost,'asset_cost_envelope':runtime['asset_cost_envelope'],'total_reserved_micro_usd':cost['reserved_micro_usd']+row['reserved_micro_usd'],'arm':'U_base','shuffle_seed':101,'fold':0,'training_seed':1})
    artifact('data_contract','input-contract.json',runtime['input_contract'])
    artifact('metric_contract','metric-contract.json',modal_package.tolerance())
    artifact('prior_results','baseline.json',{'source':'preserved external Sprint9 run-4a3a5ceee7-SMOKE','tolerance':modal_package.tolerance(),'status':'previously executed external known-case evidence, not a new system result'})
    artifact('validator','validator.py',(root/'orchestrator/sprint9_modal_validation.py').read_bytes())
    binding={'state':str(state.resolve()),'source':source,'review_sha256':digest(engine_review.read_bytes())}
    with private_records.open_file(owner,'x') as stream:json.dump(binding,stream,sort_keys=True)
    # Existing eight-call accounting semantics are retained; current authority
    # and task identity are explicitly M3, not a new authorization inferred from M2.
    policy={'status':'RATIFIED','operator_approval':digest(raw),'state_write_permission':'OPERATOR_AUTHORIZED',
            'n':4,'window':'UTC_CALENDAR_DAY','state_ref':'refs/heads/automation/dispatch-state','manual_semantics':'OPERATOR_STEP_D_MAX_EIGHT'}
    batch=BatchAccounts(runtime['batch_ledger']);batch.register_run(run_id,binding)
    config={'backend':'modal','idea_ids':['Sprint9'],'run_id':run_id,'source':source,'branch':branch,'root':str(root),'context':str(context),
      'authority_path':str(authority.relative_to(root)),'authority_sha256':digest(raw),'owner_path':str(owner),'owner_binding':binding,
      'engine_review':{'path':str(engine_review),'sha256':digest(engine_review.read_bytes())},'clients':clients,'policy':policy,'artifacts':rows,
      'workspace_root':str(state.parent/(state.name+'-scientific-workspaces')),'started_utc':stamp(),'notebook_code_sha256':modal_package.code_identity(root),
      'modal':runtime,'resources':plan['resources'],'overhead_micro_usd':plan['overhead_micro_usd'],'smoke_path':str(Path(plan['smoke_path']).resolve()),'smoke_sha256':digest(canonical(smoke)),
      'plan_path':str(plan_path.resolve()),'plan_sha256':digest(plan_path.read_bytes()),
      'profile_files':{str(p.relative_to(root)):digest(p.read_bytes()) for p in (root/PROFILE).rglob('*') if p.is_file()},
      'engine_files':{str(p.relative_to(root)):digest(p.read_bytes()) for p in (root/'orchestrator').glob('*.py')},
      'scientific_files':{str(p.relative_to(root)):digest(p.read_bytes()) for p in (root/modal_package.SCIENCE).iterdir() if p.is_file()}}
    config['engine_files']['scout.py']=digest((root/'scout.py').read_bytes())
    atomic(state/'lane.json',config)
    store=ManualExecutor(state/'jobs.sqlite',batch=batch);store.initialize_allowance(policy)
    store.db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps({'phase':STAGES[0],'rounds':{},'artifacts':rows,'interventions':[]}),));store.db.close()
    return {'status':'READY','run_id':run_id,'next':STAGES[0],'calls_used':0}


class ModalDriver(Driver):
    def __init__(self,state,runner=None,provider=None):
        self.state=Path(state);self.config=read(self.state/'lane.json')
        if self.config.get('backend')!='modal':raise ValueError('MODAL_LANE_REQUIRED')
        self.root=Path(self.config['root']);self.context=Path(self.config['context'])
        self.store=ModalExecutor(self.state/'jobs.sqlite',self.config['modal'],provider or ModalProvider(self.config['modal']),BatchAccounts(self.config['modal']['batch_ledger']))
        self.runner=runner or manual_stage.invoke

    def guard(self):
        super().guard()
        from orchestrator.modal_cleanup import expired
        if self.current()['phase'] in {*STAGES[:2],'COMMIT_SPEC','EMIT_PACKAGE','PREPARE_REMOTE_PACKAGE','EXECUTE_MODAL'} and expired(self.config['modal']):raise ValueError('MODAL_ASSET_RETENTION_EXPIRED')
        if digest(Path(self.config['plan_path']).read_bytes())!=self.config['plan_sha256']:raise ValueError('MODAL_PLAN_CHANGED')
        if digest(canonical(read(self.config['smoke_path'])))!=self.config['smoke_sha256']:raise ValueError('MODAL_SMOKE_INPUT_CHANGED')

    def task(self,stage,value):
        text=('Sprint9 known-case GPU smoke: reproduce U_base, shuffle101, fold0, training seed1, at most two epochs, on99development patients only. '
              'No full folds or clinical arms. Assess the exact code, input contract, predeclared tolerance and result evidence. '
              'Distinguish reproduction from efficacy. Comparison: '+json.dumps(modal_package.tolerance(),sort_keys=True)+'. '
              'For REVISE identify a concrete BLOCKER[category]; categories: '+', '.join(CATEGORIES)+'. Record other concerns as advisories. ')
        if stage.startswith('run_spec'):
            text+='Write a spec at most12000characters. It must contain exactly these binding lines:\nrun_id: '+self.config['run_id']+'\nnotebook_code_sha256: '+self.config['notebook_code_sha256']+'\n'
        return text

    def status(self):
        result=super().status();value=self.current()
        result['next_action']='Server-owned Modal observation/collection; no Colab' if value['phase']=='WAIT_OUTPUTS' else value['phase']
        result['asset_preparation']=[dict(x) for x in self.store.costs.db.execute('SELECT id,status,reserved_micro_usd FROM autonomy_assets WHERE run=?',(self.config['run_id'],))]
        result['asset_cleanup']=read(self.state/'asset-cleanup/COMPLETE.json') if (self.state/'asset-cleanup/COMPLETE.json').exists() else {'status':'PENDING','expires_utc':self.config['modal'].get('asset_expires_utc')}
        result['compute']=[dict(x) for x in self.store.costs.db.execute('SELECT id,status,reserved_micro_usd,actual_micro_usd,provider_id FROM autonomy_compute WHERE run=?',(self.config['run_id'],))]
        return result

    def acceptance_path(self,kind):return self.root/'projects/isles24/modal-sprint9'/kind/self.config['run_id']

    def _advance(self,collect_folder=None,identity_refusal=None):
        if collect_folder is not None or identity_refusal is not None:raise ValueError('MODAL_COLLECTION_IS_BOUND')
        self.guard();value=self.current();phase=value['phase']
        if phase in STAGES or phase in {'MODEL_RUNNING','BLOCKED'}:return super()._advance()
        if phase=='COMMIT_SPEC':
            if git(self.root,'status','--porcelain'):raise ValueError('UNRELATED_EDITS_BEFORE_SPEC_COMMIT')
            target=self.acceptance_path('spec');private_records.mkdir(target,parents=True,exist_ok=True)
            for name,key in [('SPEC.md','spec'),('review.json','spec_review')]:write_once(target/name,Path(value[key]).read_bytes())
            subprocess.run(['git','add','--',str(target)],cwd=self.root,check=True);subprocess.run(['git','commit','-m','Record reviewed Sprint9 Modal smoke specification'],cwd=self.root,check=True)
            value.update(phase='EMIT_PACKAGE',spec_commit=git(self.root,'rev-parse','HEAD'));self.save(value);return self.status()
        if phase=='EMIT_PACKAGE':
            manual_context.prepare(self.context,stage='run_spec_review',idea_ids=['Sprint9'],task=self.task('run_spec_review',value),artifacts=value['artifacts'],workspace=self.state/'emit-preflight')
            manifest=modal_package.emit(self.root,self.state/'prepared-package',self.config,value['spec'],value['spec_review'])
            value.update(phase='PREPARE_REMOTE_PACKAGE',manifest=manifest);self.save(value);return self.status()
        if phase=='PREPARE_REMOTE_PACKAGE':
            # Upload the independently reviewed package once; uncertainty never
            # becomes an implicit retry or permission to launch.
            receipt=self.state/'remote-package-ready.json'
            if not receipt.exists():
                from orchestrator.modal_assets import prepare_package
                ready=prepare_package(self.store.provider,value['manifest']['binding'],self.state/'prepared-package',self.state/'package-upload')
                write_once(receipt,canonical(ready))
            ready=read(receipt)
            if ready.get('status')!='READY' or ready.get('manifest_sha256')!=digest(canonical(value['manifest'])) or ready.get('volume_id')!=self.config['modal']['package_volume_id']:
                raise ValueError('MODAL_REMOTE_PACKAGE_BINDING')
            value.update(phase='EXECUTE_MODAL');self.save(value);return self.status()
        if phase=='EXECUTE_MODAL':
            manifest=value['manifest'];result=self.store.submit(self.config['run_id'],manifest['binding'],self.state/'prepared-package',self.state/'package')
            if result['status'] not in {'SUBMITTED','RUNNING','COMPLETE'}:raise ValueError('MODAL_SUBMISSION_NOT_CONFIRMED')
            value.update(phase='WAIT_OUTPUTS');self.save(value);return self.status()
        if phase=='WAIT_OUTPUTS':
            manifest=value['manifest'];smoke=read(self.config['smoke_path'])
            validation=self.store.collect_remote(self.config['run_id'],self.state/'package',self.state/'collected',lambda p:validate(p,manifest['binding'],smoke))
            if validation['status'] in {'RUNNING','OBSERVATION_UNAVAILABLE'}:return {**self.status(),'observation':validation}
            if validation['status']!='VALID':raise ValueError('MODAL_EXECUTION_NOT_VALID: '+validation['status'])
            atomic(self.state/'validation.json',validation)
            from orchestrator.modal_cleanup import clear_copies
            clear_copies(self.store.provider,self.config['modal'],self.state/'asset-cleanup',collected=True)
            # Patient-level membership/results remain private originals. These
            # labelled controller views carry aggregate science + original hashes.
            safe={k:v for k,v in validation.items() if k!='files'}
            safe['private_files']={'count':len(validation['files']),'inventory_sha256':digest(canonical(validation['files']))}
            self.artifact(value,'validation_result','validation-view.json',canonical(safe),1)
            self.artifact(value,'result_tables','summary.json',(self.state/'collected/summary.json').read_bytes(),1)
            execution=(self.state/'collected/execution.json').read_bytes()
            self.artifact(value,'execution_receipt','execution.json',execution,1)
            from orchestrator.modal_evidence import collected_view
            self.artifact(value,'execution_manifest','execution-connection.json',collected_view(self.state,self.config,manifest),1)
            self.artifact(value,'package_manifest','package-manifest-view.json',canonical(modal_package.safe_manifest(manifest)),1)
            value.update(phase='result_interpretation_author');self.save(value);return self.status()
        if phase=='UPDATE_STATE':
            if git(self.root,'status','--porcelain'):raise ValueError('UNRELATED_EDITS_BEFORE_STATE_COMMIT')
            target=self.acceptance_path('acceptance');private_records.mkdir(target,parents=True,exist_ok=True)
            record={'run_id':self.config['run_id'],'source':self.config['source'],'validation_sha256':digest((self.state/'validation.json').read_bytes()),
                    'meaning':'Known-case Sprint9 GPU smoke reproduced within predeclared tolerance and independently interpreted; no new efficacy claim or successor execution authority'}
            for name,key in [('interpretation.md','interpretation'),('investigator_next_decision.json','next_decision'),('review.json','review')]:
                raw=Path(value[key]).read_bytes();write_once(target/name,raw);record[name]=digest(raw)
            for row in value['artifacts']:
                if row['type'] in {'interpretation_original','interpretation_format_repair'}:
                    raw=(self.context/row['path']).read_bytes()
                    if digest(raw)!=row['sha256']:raise ValueError('FORMAT_REPAIR_ARTIFACT_CHANGED')
                    write_once(target/Path(row['path']).name,raw)
            write_once(target/'acceptance.json',canonical(record))
            state=self.root/PROFILE/'STATE.md';body=state.read_text();addition='\n\n## Sprint9 system smoke acceptance\n'+record['meaning']+'\nSource: '+str((target/'acceptance.json').relative_to(self.root))+' SHA256 '+digest((target/'acceptance.json').read_bytes())+'\n'
            if addition not in body:
                if len(body+addition)>20000:raise ValueError('STATE_LIMIT')
                scan('context/STATE.md',(body+addition).encode());private_records.write_text(state,body+addition)
            profile=read(self.root/PROFILE/'manifest.json');profile['state']['sha256']=digest(state.read_bytes());atomic(self.root/PROFILE/'manifest.json',profile)
            subprocess.run(['git','add','--',str(target),str(state),str(self.root/PROFILE/'manifest.json')],cwd=self.root,check=True)
            subprocess.run(['git','commit','-m','Record reviewed Sprint9 Modal known-case smoke acceptance'],cwd=self.root,check=True)
            value.update(phase='REPORT');self.save(value);return self.status()
        if phase=='REPORT':
            calls=[json.loads(r['receipt']) for r in self.store.db.execute('SELECT receipt FROM manual_calls')]
            text='# Sprint9 Modal smoke acceptance\n\nOne development U_base fold reproduced within its predeclared tolerance; interpretation independently reviewed. No full folds, clinical arms or locked-patient access.\n\n'
            elapsed=(datetime.now(timezone.utc)-datetime.fromisoformat(self.config['started_utc'].replace('Z','+00:00'))).total_seconds()
            text+=f'Model calls: {len(calls)}/8; rounds: {json.dumps(value["rounds"])}; elapsed: {elapsed:.1f} seconds. No Colab intervention.\n\n'
            text+='Recorded interventions: '+json.dumps(value.get('interventions',[]),sort_keys=True)+'.\n\n'
            text+='| Stage | Input characters | Outcome |\n| --- | ---: | --- |\n'
            for call in calls:text+=f'| {call["stage"]} | {call["input_characters"]} | {call["outcome"]} |\n'
            text+='\nCompute accounting: '+json.dumps({k:self.status()[k] for k in ['compute','asset_preparation','asset_cleanup']},sort_keys=True)+'. Reservations are not actual provider charges.\n\n'
            text+='See validation.json, private originals and committed interpretation. Backlog succession, scheduling and disconnected observation remain separate M4?M6 requirements.\n'
            private_records.write_text(self.state/'REPORT.md',text);value.update(phase='COMPLETE');self.save(value)
        if self.current()['phase']=='COMPLETE':self.store.batch.complete_run(self.config['run_id'],{'report_sha256':digest((self.state/'REPORT.md').read_bytes())})
        return self.status()



@private_records.private_umask
def run_until_stop(state,*,factory=ModalDriver,sleep=time.sleep,clock=time.monotonic):
    """One initialized run only. No backlog selection, retry or new allowance."""
    from orchestrator.remote_supervisor import lock
    state=Path(state);path=state/'one-run.lock'
    if path.exists():private_records.check(path)
    with lock(path):
        private_records.check(path)
        driver=factory(state);started=clock()
        while True:
            result=driver.advance()
            if result['phase'] in {'COMPLETE','BLOCKED'}:return result
            if clock()-started>=4*3600:
                # No in-flight call is killed here: advance() has returned.
                return {**result,'operational_refusal':'ONE_RUN_SUPERVISOR_DEADLINE; saved state retained; no automatic restart'}
            if result['phase']=='WAIT_OUTPUTS' or result.get('operational_refusal'):sleep(30)



def supervise(state,preparation,*,factory=ModalDriver,provider_factory=ModalProvider,run=run_until_stop):
    """The existing two-unit lane owns both progression and expiry housekeeping."""
    state,preparation=Path(state),Path(preparation)
    runtime_file=preparation/'runtime.json'
    if not runtime_file.exists():return {'status':'NOT_PREPARED','calls_started':0}
    runtime=read(runtime_file)
    from orchestrator.modal_cleanup import expired,clear_copies
    if expired(runtime):
        # Existing scientific uncertainty remains a block. Housekeeping never
        # turns a partial or expired run into permission to call a model again.
        if (state/'lane.json').exists():
            driver=factory(state)
            if any(row['status'] in {'RUNNING','UNCERTAIN'} for row in driver.status()['calls']):
                return {'status':'ASSET_CLEANUP_BLOCKED_BY_UNCERTAIN_CALL','calls_started':0}
        return clear_copies(provider_factory(runtime),runtime,state/'asset-cleanup')
    if not (state/'lane.json').exists():return {'status':'AWAITING_INITIALIZATION','calls_started':0}
    return run(state,factory=factory)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['init','status','advance','run','supervise']);parser.add_argument('--state',required=True)
    parser.add_argument('--preparation');parser.add_argument('--root');parser.add_argument('--engine-review');parser.add_argument('--plan');args=parser.parse_args()
    if args.command=='init':result=initialize(args.root,args.state,args.engine_review,args.plan)
    elif args.command=='supervise':result=supervise(args.state,args.preparation)
    elif args.command=='run':result=run_until_stop(args.state)
    else:
        driver=ModalDriver(args.state);result=driver.status() if args.command=='status' else driver.advance()
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
