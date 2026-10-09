"""One Modal execution, using existing jobs, batch accounting and private records.

The provider adapter creates an idle, bounded container, then launches the exact
reviewed package once. Restarted observation only attaches to its saved ID.
"""
import json
from pathlib import Path
import re
from orchestrator.manual_executor import ManualExecutor, read, digest, inventory
from orchestrator.manual_driver import write_once
from orchestrator import private_records, connectivity
from orchestrator.modal_budget import ComputeAccounts
from orchestrator.remote_supervisor import lock


def canonical(value):return json.dumps(value,sort_keys=True).encode()


def verify_package(package, binding):
    package=Path(package);private_records.check_tree(package)
    manifest=read(package/'manifest.json')
    if manifest.get('schema')!='modal-run/v1' or manifest.get('binding')!=binding:raise ValueError('MODAL_PACKAGE_BINDING')
    files=inventory(package);files.pop('manifest.json',None)
    if files!=manifest.get('files'):raise ValueError('MODAL_PACKAGE_MEMBER_OR_HASH_CHANGED')
    for name,key in [('SPEC.md','spec_sha256'),('review.json','review_sha256')]:
        if digest((package/name).read_bytes())!=binding.get(key):raise ValueError('MODAL_APPROVAL_BINDING')
    if binding.get('purpose') == 'M4_ITEM6_CPU':
        from orchestrator.diagnostics_execution import verify_prepared
        verify_prepared(package,binding)
        return manifest
    if binding.get('purpose') == 'M4_ITEM4':
        from orchestrator.review_contract import scientific
        from orchestrator.modal_item4_budget import AUTHORITY, TEAM_AUTHORITY
        scope = binding.get('experiment')
        if (not isinstance(scope,dict) or scope.get('backlog_item') != 4 or
                scope.get('authority_sha256') != AUTHORITY or scope.get('team_authority_sha256') != TEAM_AUTHORITY):
            raise ValueError('MODAL_ITEM4_SELECTED_SCOPE_REQUIRED')
        review = scientific((package/'review.json').read_bytes())
        if review['verdict'] != 'APPROVE' or review['findings']:
            from orchestrator.item4_validation_admission import package_review
            package_review(package, binding)
    else:
        if 'experiment' in binding:
            raise ValueError('MODAL_ITEM4_SELECTED_SCOPE_REQUIRED')
        # Preserve the earlier M3 package contract at its original scope.
        review=read(package/'review.json')
        if set(review)!={'verdict','rationale'} or review['verdict']!='APPROVE' or not isinstance(review['rationale'],str) or 'BLOCKER[' in review['rationale']:
            raise ValueError('MODAL_APPROVED_SCIENTIFIC_SPEC_REQUIRED')
    if 'execution' in binding:
        from orchestrator.experiment_modal_package import verify
        verify(package,binding,files)
        if not re.fullmatch(r'[0-9a-f]{40}',binding['source']):raise ValueError('MODAL_SOURCE_PIN')
        return manifest
    spec=(package/'SPEC.md').read_text().splitlines()
    for line in ['run_id: '+binding['run_id'],'notebook_code_sha256: '+binding['code_sha256']]:
        if spec.count(line)!=1:raise ValueError('MODAL_SPEC_CODE_BINDING')
    code={k:v for k,v in files.items() if k.endswith('.py')}
    if not code or digest(canonical(code))!=binding['code_sha256'] or 'run.py' not in code:raise ValueError('MODAL_CODE_IDENTITY')
    if not re.fullmatch(r'[0-9a-f]{40}',binding['source']):raise ValueError('MODAL_SOURCE_PIN')
    return manifest


def item4_job(binding):
    """One local job per fit segment, inside the single approved global run."""
    scope=binding.get('experiment',{})
    run=binding.get('run_id');fit=scope.get('fit_id');segment=scope.get('segment')
    if (binding.get('purpose')!='M4_ITEM4' or not isinstance(run,str) or
            not re.fullmatch('[a-z0-9][a-z0-9-]{1,100}',run) or not isinstance(fit,str) or
            not re.fullmatch('[a-zA-Z0-9_-]{1,96}',fit) or type(segment) is not int or segment<1):
        raise ValueError('ITEM4_JOB_SCOPE')
    # Deliberately excludes mutable resources/quote: changing them cannot create
    # another job for an already submitted realization/segment.
    identity={'run':run,'fit':fit,'segment':segment}
    if 'fresh_start' in binding:
        link=binding['fresh_start']
        if 'preprocessing' not in binding:
            from orchestrator.item4_fit_transport_recovery import validate_identity, ORIGINAL_ID
            if not isinstance(link,dict) or link.get('previous_binding_sha256')!=ORIGINAL_ID:
                raise ValueError('ITEM4_FRESH_START_IDENTITY')
            validate_identity(binding)
        if ((segment==1 and 'resume' in binding)
                or (segment!=1 and 'resume' not in binding)
                or not isinstance(link,dict) or set(link)!={'previous_binding_sha256','terminal_event_sha256'}
                or any(not isinstance(v,str) or not re.fullmatch('[a-f0-9]{64}',v) for v in link.values())):
            raise ValueError('ITEM4_FRESH_START_IDENTITY')
        # Explicit terminal linkage distinguishes one reviewed fresh attempt;
        # resources/quotes still cannot create a new job. Admission checks the
        # full pinned binding and genuine terminal event, not just this shape.
        if segment!=1:
            from orchestrator.item4_checkpoint_connection import validate_identity
            validate_identity(binding)
        identity['fresh_start']=link
    return 'item4-'+digest(canonical(identity))[:40]


class ModalExecutor(ManualExecutor):
    def __init__(self,path,config,provider,batch):
        super().__init__(path,batch=batch)
        self.config=config;self.provider=provider;self.costs=ComputeAccounts(batch)

    def _paths(self,job):
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,100}',job):raise ValueError('MODAL_JOB_ID')
        return self.path.parent/'modal-executions'/job

    def _guard(self):
        if (self.path.parent/'HALT').exists() or (self.batch.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
        connectivity.require(['modal'],self.path.parent/'connectivity.json')

    @private_records.private_umask
    def submit(self,job,binding,prepared,package):
        work=self._paths(job)
        with lock(self.path.parent/'modal-executor.lock'):
            self._guard()
            if binding.get('purpose') in {'M4_ITEM4','M4_ITEM6_CPU'}:
                return self._submit_item4(job,binding,prepared,package,work)
            if binding.get('run_id')!=job or binding.get('runtime_sha256')!=digest(canonical(self.config)):
                raise ValueError('MODAL_RUNTIME_BINDING')
            manifest=verify_package(prepared,binding)
            self.register(job,binding)
            prior=self.db.execute('SELECT manifest FROM manual_packages WHERE job=?',(job,)).fetchone()
            if prior:
                if inventory(package)!=json.loads(prior[0]):raise ValueError('MODAL_EMITTED_PACKAGE_CHANGED')
                # Critically, never create or launch through an existing submission.
                return self._status(job,work)
            if work.exists() or Path(package).exists() or self.get(job)['phase']!='acquisition' or self.get(job)['status']!='READY':
                self.block(job,'MODAL_PARTIAL_SUBMISSION_RECONCILE');raise ValueError('MODAL_PARTIAL_SUBMISSION_RECONCILE')
            # Read-only provider/data/image checks, before any spending reservation.
            observation=self.provider.preflight(self.config,binding,prepared)
            if observation.get('status')!='READY':raise ValueError('MODAL_PROVIDER_PREFLIGHT')
            private_records.copytree(prepared,package)
            if inventory(package)!=inventory(prepared):raise ValueError('MODAL_PACKAGE_COPY_CHANGED')
            private_records.mkdir(work,parents=True)
            self.db.execute('INSERT INTO manual_packages VALUES(?,?)',(job,json.dumps(inventory(package),sort_keys=True)))
            first=self.claim(job);self.complete_event(job,job+':gpu-acquired','VALIDATED',lease=first['lease'])
            claimed=self.claim(job)
            if not claimed:raise ValueError('MODAL_DISPATCH_NOT_CLAIMED')
            ident=digest(canonical(binding))
            if not self.costs.reserve(ident,job,binding,workspace_spent_micro=observation['workspace_spent_micro'],smoke=binding['purpose']=='M3_SMOKE'):
                self.block(job,'MODAL_EXISTING_RESERVATION_NO_RESUBMISSION');raise ValueError('MODAL_EXISTING_RESERVATION_NO_RESUBMISSION')
            intent={'job':job,'binding_sha256':ident,'lease':claimed['lease'],'package_sha256':digest(canonical(inventory(package))),'preflight':observation}
            write_once(work/'create-intent.json',canonical(intent))
            provider_id=None
            try:
                created=self.provider.create(self.config,binding,package)
                provider_id=created['provider_id']
                if not isinstance(provider_id,str) or not provider_id:raise ValueError('MODAL_PROVIDER_ID_REQUIRED')
                write_once(work/'created.json',canonical({'provider_id':provider_id,'binding_sha256':ident,'receipt':created}))
                self.costs.observe(ident,'CREATED',provider_id)
                write_once(work/'execute-intent.json',canonical({'provider_id':provider_id,'binding_sha256':ident}))
                launched=self.provider.launch(provider_id,binding)
                write_once(work/'launched.json',canonical({'provider_id':provider_id,'binding_sha256':ident,'receipt':launched}))
                self.costs.observe(ident,'RUNNING',provider_id)
                self.complete_event(job,job+':gpu-submitted','DISPATCHED',lease=claimed['lease'])
            except BaseException as error:
                write_once(work/'submission-uncertain.json',canonical({'binding_sha256':ident,'provider_id':provider_id,'error_type':type(error).__name__,'resubmitted':False}))
                self.costs.observe(ident,'UNCERTAIN',provider_id)
                self.block(job,'MODAL_UNCERTAIN_SUBMISSION_NO_RESUBMISSION')
                raise ValueError('MODAL_UNCERTAIN_SUBMISSION_NO_RESUBMISSION') from None
            return {'status':'SUBMITTED','job':job,'provider_id':provider_id,'cost_reserved_micro_usd':binding['cost']['reserved_micro_usd']}

    def _submit_item4(self,job,binding,prepared,package,work):
        # Called only under submit's private umask and the existing executor lock.
        item6=binding.get('purpose')=='M4_ITEM6_CPU'
        expected_job=binding['run_id'] if item6 else item4_job(binding)
        if expected_job!=job or binding.get('runtime_sha256')!=digest(canonical(self.config)):
            raise ValueError('MODAL_RUNTIME_BINDING')
        verify_package(prepared,binding)
        self.register(job,binding)
        prior=self.db.execute('SELECT manifest FROM manual_packages WHERE job=?',(job,)).fetchone()
        if prior:
            if inventory(package)!=json.loads(prior[0]):raise ValueError('MODAL_EMITTED_PACKAGE_CHANGED')
            return self._status(job,work)
        if work.exists() or Path(package).exists() or self.get(job)['phase']!='acquisition' or self.get(job)['status']!='READY':
            self.block(job,'MODAL_PARTIAL_SUBMISSION_RECONCILE')
            raise ValueError('MODAL_PARTIAL_SUBMISSION_RECONCILE')
        # Reconcile known terminal segments before ordinary next-wave admission.
        # Missing legacy clocks retain their reservations; no provider is called.
        from orchestrator import modal_terminal_cost
        for prior_row in self.costs.db.execute("SELECT * FROM autonomy_compute WHERE run=? AND status IN ('COLLECTED','ACCOUNTED')",(binding['run_id'],)).fetchall():
            previous=json.loads(prior_row['binding'])
            if previous.get('purpose')=='M4_ITEM4':
                modal_terminal_cost.record(self.costs,prior_row['id'],self._paths(item4_job(previous)))
        observation=self.provider.preflight(self.config,binding,prepared)
        if observation.get('status')!='READY' or 'billing_snapshot' not in observation:
            raise ValueError('ITEM4_PROVIDER_BILLING_PREFLIGHT')
        ident=digest(canonical(binding))
        try:
            if item6:
                from orchestrator.diagnostics_budget import reserve
                reserved=reserve(self.costs,ident,binding['run_id'],binding,billing_snapshot=observation['billing_snapshot'])
            else:
                reserved=self.costs.reserve_item4(ident,binding['run_id'],binding,
                    billing_snapshot=observation['billing_snapshot'])
        except ValueError as error:
            if str(error) not in {'ITEM4_PROVIDER_HEADROOM_WAIT','DIAGNOSTICS_PROVIDER_HEADROOM_WAIT'}:raise
            # No package, event claim, spending row or provider creation exists.
            # The same job can be checked later after a new billing observation.
            return {'status':'WAIT_PROVIDER_HEADROOM','job':job,'run_id':binding['run_id'],
                    'reason':str(error),'reserved':False,'provider_created':False}
        if not reserved:
            self.block(job,'MODAL_EXISTING_RESERVATION_NO_RESUBMISSION')
            raise ValueError('MODAL_EXISTING_RESERVATION_NO_RESUBMISSION')
        provider_id=None
        try:
            private_records.copytree(prepared,package)
            if inventory(package)!=inventory(prepared):raise ValueError('MODAL_PACKAGE_COPY_CHANGED')
            private_records.mkdir(work,parents=True)
            self.db.execute('INSERT INTO manual_packages VALUES(?,?)',(job,json.dumps(inventory(package),sort_keys=True)))
            first=self.claim(job);self.complete_event(job,job+':gpu-acquired','VALIDATED',lease=first['lease'])
            claimed=self.claim(job)
            if not claimed:raise ValueError('MODAL_DISPATCH_NOT_CLAIMED')
            intent={'job':job,'run_id':binding['run_id'],'binding_sha256':ident,
                    'lease':claimed['lease'],'package_sha256':digest(canonical(inventory(package))),
                    'preflight':observation,'cost_clock':modal_terminal_cost.clock()}
            write_once(work/'create-intent.json',canonical(intent))
            created=self.provider.create(self.config,binding,package)
            provider_id=created['provider_id']
            if not isinstance(provider_id,str) or not provider_id:raise ValueError('MODAL_PROVIDER_ID_REQUIRED')
            write_once(work/'created.json',canonical({'provider_id':provider_id,'binding_sha256':ident,'receipt':created}))
            self.costs.observe(ident,'CREATED',provider_id)
            write_once(work/'execute-intent.json',canonical({'provider_id':provider_id,'binding_sha256':ident}))
            launched=self.provider.launch(provider_id,binding)
            write_once(work/'launched.json',canonical({'provider_id':provider_id,'binding_sha256':ident,'receipt':launched}))
            self.costs.observe(ident,'RUNNING',provider_id)
            self.complete_event(job,job+':gpu-submitted','DISPATCHED',lease=claimed['lease'])
        except BaseException as error:
            private_records.mkdir(work,parents=True,exist_ok=True)
            write_once(work/'submission-uncertain.json',canonical({'binding_sha256':ident,
                'provider_id':provider_id,'error_type':type(error).__name__,'resubmitted':False}))
            self.costs.observe(ident,'UNCERTAIN',provider_id)
            self.block(job,'MODAL_UNCERTAIN_SUBMISSION_NO_RESUBMISSION')
            raise ValueError('MODAL_UNCERTAIN_SUBMISSION_NO_RESUBMISSION') from None
        return {'status':'SUBMITTED','job':job,'run_id':binding['run_id'],'provider_id':provider_id,
                'cost_reserved_micro_usd':binding['cost']['reserved_micro_usd']}

    def _status(self,job,work):
        if not (work/'created.json').is_file():
            return {'status':'UNRESOLVED_SUBMISSION','job':job,'may_resubmit':False}
        saved=read(work/'created.json');record=self.get(job)
        if saved['binding_sha256']!=digest(record['binding'].encode()):raise ValueError('MODAL_CREATED_RECEIPT_CHANGED')
        binding=json.loads(record['binding'])
        if binding.get('purpose')=='M4_ITEM4' and (work/'failed-outcome.json').exists():
            return self._failed_item4(job,work,binding,saved,None)
        try:result=self.provider.status(saved['provider_id'],binding)
        except ValueError:
            # Content/binding violations are real invariants, not a network wait.
            raise
        except Exception as error:
            # Observation failure is not proof that execution stopped.
            return {'status':'OBSERVATION_UNAVAILABLE','job':job,'provider_id':saved['provider_id'],'error_type':type(error).__name__,'may_resubmit':False}
        if result.get('provider_id')!=saved['provider_id'] or result.get('binding_sha256')!=saved['binding_sha256']:
            raise ValueError('MODAL_OBSERVATION_BINDING')
        if result.get('status') not in {'RUNNING','COMPLETE','FAILED','UNKNOWN'}:raise ValueError('MODAL_OBSERVATION_STATE')
        if result['status']=='FAILED' and binding.get('purpose')=='M4_ITEM4':
            return self._failed_item4(job,work,binding,saved,result)
        return {**result,'job':job,'may_resubmit':False}

    @private_records.private_umask
    def _failed_item4(self,job,work,binding,created,observation):
        from orchestrator.modal_failure import reconcile
        return reconcile(self,job,work,binding,created,observation)

    def monitor_fit(self,job,log_path=None):
        from orchestrator.modal_fit_monitor import tick
        return tick(self,job,log_path)

    @private_records.private_umask
    def remote_status(self,job):
        with lock(self.path.parent/'modal-executor.lock'):
            return self._status(job,self._paths(job))

    @private_records.private_umask
    def collect_remote(self,job,package,destination,validate):
        work=self._paths(job)
        with lock(self.path.parent/'modal-executor.lock'):
            record=self.get(job);binding=json.loads(record['binding']);verify_package(package,binding)
            old=self.db.execute('SELECT manifest FROM manual_collections WHERE job=?',(job,)).fetchone()
            if old:
                # Validate the saved local copy; no provider call and no charge.
                if inventory(destination)!=json.loads(old[0]):raise ValueError('MODAL_COLLECTED_RESULT_CHANGED')
                verified=validate(Path(destination))
                if verified.get('status')!='VALID':raise ValueError('MODAL_SAVED_VALIDATION_REFUSED')
                provider_id=read(work/'created.json')['provider_id']
                self._finalize(binding,work,provider_id)
                return {**verified,'duplicate_collection':True}
            observed=self._status(job,work)
            if observed['status']!='COMPLETE':return observed
            incoming=work/'incoming'
            if incoming.exists():raise ValueError('MODAL_PARTIAL_COLLECTION_RECONCILE')
            private_records.mkdir(incoming)
            result=self.provider.collect(observed['provider_id'],binding,incoming)
            private_records.check_tree(incoming)
            if result.get('binding_sha256')!=digest(canonical(binding)) or result.get('file_sha256')!=inventory(incoming):raise ValueError('MODAL_RETURN_BINDING')
            write_once(work/'collection-receipt.json',canonical(result))
            verified=super().collect(job,incoming,destination,validate)
            self._finalize(binding,work,observed['provider_id'])
            return {**verified,'provider_id':observed['provider_id'],'cost':'conservative reservation retained pending provider reconciliation'}

    def _finalize(self,binding,work,provider_id):
        # Idempotent cleanup may be reconciled after a local interruption. It is
        # never a submission and cannot repeat scientific computation.
        if not (work/'terminated.json').exists():
            stopped=self.provider.terminate(provider_id)
            if stopped.get('provider_id')!=provider_id or stopped.get('terminated') is not True:
                raise ValueError('MODAL_TERMINATION_UNVERIFIED')
            write_once(work/'terminated.json',canonical(stopped))
        else:
            stopped=read(work/'terminated.json')
            if stopped.get('provider_id')!=provider_id or stopped.get('terminated') is not True:
                raise ValueError('MODAL_TERMINATION_RECEIPT_CHANGED')
        self.costs.observe(digest(canonical(binding)),'COLLECTED',provider_id)
        if binding.get('purpose')=='M4_ITEM4':
            from orchestrator.modal_terminal_cost import record
            record(self.costs,digest(canonical(binding)),work)
