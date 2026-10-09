"""Local manual executor: durable package emission, never Colab dispatch.

Uses the existing job_store for identity/ambiguous-dispatch protection and the
existing dispatch_limiter CAS accounting engine for the operator's local allowance.
No inference from an absent receipt can authorize a retry.
"""
import hashlib
import json
from pathlib import Path
from orchestrator import private_records
import shutil
import time
from orchestrator.job_store import Store
from orchestrator import dispatch_limiter as accounting
from orchestrator.remote_supervisor import lock
from orchestrator.private_records import atomic


def digest(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def inventory(folder,allow_symlinks=False):
    folder=Path(folder)
    result={}
    for p in sorted(folder.rglob('*')):
        if p.is_symlink():
            if not allow_symlinks:raise ValueError('SYMLINK_REFUSED')
            result[str(p.relative_to(folder))]='symlink:'+digest(str(p.readlink()).encode());continue
        if p.is_file():result[str(p.relative_to(folder))]=digest(p.read_bytes())
    return result


class Accounts:
    """CAS adapter backed by the same local job database, without a new reset API."""
    def __init__(self,store):self.db=store.db
    def read(self):
        row=self.db.execute('SELECT version,payload FROM manual_account WHERE id=1').fetchone()
        if not row:raise ValueError('LOCAL_ALLOWANCE_NOT_INITIALIZED')
        return str(row[0]),accounting.validate(json.loads(row[1]))
    def cas(self,old,state):
        raw=json.dumps(accounting.validate(state),sort_keys=True)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.db.execute('SELECT version FROM manual_account WHERE id=1').fetchone()
            if row is None or str(row[0])!=old:self.db.execute('ROLLBACK');return False
            self.db.execute('UPDATE manual_account SET version=version+1,payload=? WHERE id=1',(raw,))
            self.db.execute('COMMIT');return True
        except BaseException:self.db.execute('ROLLBACK');raise


class ManualExecutor(Store):
    def __init__(self,path,batch=None):
        self.batch=batch
        self.path=Path(path)
        super().__init__(path,connection_factory=private_records.Connection)
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS manual_packages(job TEXT PRIMARY KEY, manifest TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS manual_collections(job TEXT PRIMARY KEY, manifest TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS manual_account(id INTEGER PRIMARY KEY,version INTEGER,payload TEXT);
        CREATE TABLE IF NOT EXISTS manual_calls(id TEXT PRIMARY KEY, stage TEXT, attempt INTEGER, status TEXT, receipt TEXT);
        CREATE TABLE IF NOT EXISTS manual_state(id INTEGER PRIMARY KEY,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS manual_recoveries(failed_id TEXT PRIMARY KEY,binding TEXT NOT NULL);
        """)

    def initialize_allowance(self,policy):
        accounting.policy(policy)
        old=self.db.execute('SELECT payload FROM manual_account WHERE id=1').fetchone()
        binding=digest(json.dumps(policy,sort_keys=True).encode())
        if old:
            if json.loads(old[0])['policy_sha256']!=binding:raise ValueError('ALLOWANCE_CHANGE_REFUSED')
            return
        value=accounting.initial();value['policy_sha256']=binding
        self.db.execute('INSERT INTO manual_account VALUES(1,0,?)',(json.dumps(value),))

    def reserve_call(self,run_id,stage,source,branch,policy,receipt):
        if stage not in {'run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review'}:raise ValueError('MANUAL_STAGE_REQUIRED')
        rows=self.db.execute('SELECT * FROM manual_calls').fetchall()
        from orchestrator import manual_recovery
        recovery=manual_recovery.permit(self,run_id)
        excepted=recovery['failed_id'] if recovery else None
        preserved=recovery.get('preserved_failures',[excepted]) if recovery else [None]
        if any(row['status'] in {'RUNNING','UNCERTAIN'} and row['id'] not in preserved for row in rows):raise ValueError('UNCERTAIN_MODEL_CALL_NO_RETRY')
        n=sum(row['stage']==stage for row in rows)+1
        from orchestrator.autonomy_limits import local_limit
        cap=local_limit(self,run_id,policy)
        if len(rows)>=cap or n>manual_recovery.role_limit(self,run_id,stage):raise ValueError('STEP_D_MODEL_CALL_LIMIT')
        from orchestrator.author_revision_accounting import inspect, FIELD
        classification=inspect(self,run_id,stage)
        if FIELD in receipt:raise ValueError('AUTHOR_REVISION_CALLER_CLASSIFICATION_REFUSED')
        if classification is not None and classification['binding'] is not None:
            receipt={**receipt,FIELD:classification['binding']}
        if recovery and stage==recovery.get('stage',manual_recovery.STAGE):
            if recovery.get('stage')!='run_spec_author' or n==2:
                receipt={**receipt,'linked_recovery_of':excepted,'recovery_invocation':n,'recovery_decision_sha256':recovery['decision_sha256'],'recovery_runtime_source':recovery['runtime_source']}
            elif n==3:
                receipt={**receipt,'revision_kind':'reviewer_requested_revision',
                    'revision_of':digest((run_id+':'+stage+':2').encode()),
                    'requested_by_review':digest((run_id+':run_spec_review:1').encode())}
        if recovery and recovery.get('stage')=='run_spec_author':
            from orchestrator.stocktake_recovery import validate_next_call
            validate_next_call(self,stage,n)
        if recovery and 'review_checkpoint' in recovery:
            from orchestrator.stocktake_review_recovery import validate_next_call
            validate_next_call(self,stage,n)
        from orchestrator import connectivity
        receipt={**receipt,'connectivity':connectivity.require(['claude' if stage.endswith('review') else 'codex'], self.path.parent/'connectivity.json')}
        ident=digest((run_id+':'+stage+':'+str(n)).encode())
        if self.batch is not None:
            receipt={**receipt,'batch_accounting':self.batch.reserve_scientific(ident,run_id,stage,source,receipt)}
        self.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(ident,stage,n,'RUNNING',json.dumps(receipt)))
        try:
            from orchestrator.autonomy_limits import allowance
            amendment=allowance(self,run_id,policy)
            charged=accounting.admit_manual(Accounts(self),policy,{'run_id':ident,'attempt':'1','source':source,'branch':branch},allowance=amendment)
            if charged['status']!='ADMITTED':raise ValueError('LOCAL_ALLOWANCE_HALTED')
            receipt={**receipt,'accounting':charged}
            self.db.execute('UPDATE manual_calls SET receipt=? WHERE id=?',(json.dumps(receipt),ident))
        except BaseException:
            self.db.execute('UPDATE manual_calls SET status=? WHERE id=?',('BLOCKED_BEFORE_MODEL',ident));raise
        return ident,n,receipt

    def finish_call(self,ident,receipt,status):
        if status not in {'COMPLETE','FAILED','UNCERTAIN'}:raise ValueError('CALL_OUTCOME')
        if self.batch is not None:self.batch.finish_scientific(ident,receipt,status)
        self.db.execute('UPDATE manual_calls SET status=?,receipt=? WHERE id=?',(status,json.dumps(receipt),ident))

    def submit(self,job,binding,prepared,package):
        if not self.db.execute('SELECT 1 FROM manual_packages WHERE job=?',(job,)).fetchone():
            from orchestrator import connectivity
            connectivity.require(['drive'],self.path.parent/'connectivity.json')
        self.register(job,binding)
        prior=self.db.execute('SELECT manifest FROM manual_packages WHERE job=?',(job,)).fetchone()
        if prior:
            if self.get(job)['phase'] != 'patient':
                self.block(job,'UNCERTAIN_MANUAL_SUBMISSION_NO_RETRY');raise ValueError('UNCERTAIN_MANUAL_SUBMISSION_NO_RETRY')
            if inventory(package)!=json.loads(prior[0]):raise ValueError('EMITTED_PACKAGE_CHANGED')
            return {'status':'ALREADY_EMITTED_NO_RESUBMISSION','job':job}
        state=self.get(job)
        if state['status']!='READY' or Path(package).exists():
            self.block(job,'UNCERTAIN_MANUAL_SUBMISSION_NO_RETRY');raise ValueError('UNCERTAIN_MANUAL_SUBMISSION_NO_RETRY')
        first=self.claim(job)
        self.complete_event(job,job+':acquired','VALIDATED',lease=first['lease'])
        dispatch=self.claim(job)
        if not dispatch:raise ValueError('MANUAL_DISPATCH_NOT_CLAIMED')
        # Any interruption after claiming dispatch is ambiguous, never re-emitted.
        private_records.copytree(prepared,package)
        manifest=inventory(package)
        self.db.execute('INSERT INTO manual_packages VALUES(?,?)',(job,json.dumps(manifest,sort_keys=True)))
        self.complete_event(job,job+':emitted','DISPATCHED',lease=dispatch['lease'])
        return {'status':'WAITING_FOR_OPERATOR_COLAB','job':job,'package_files':manifest}

    def reemit_identity_refusal(self,job,manifest,refusal_file,package,destination):
        raw=Path(refusal_file).read_bytes();refusal=json.loads(raw)
        expected={'schema':'manual-precomputation-refusal/v1','run_id':job,
            'manifest_sha256':digest(json.dumps(manifest,sort_keys=True).encode()),
            'status':'IDENTITY_REFUSED_BEFORE_COMPUTATION','computation_started':False,
            'return_exists':False,'reason':'PACKAGE_IDENTITY_CHECK_FAILED'}
        if refusal!=expected:raise ValueError('BOUND_PRECOMPUTATION_REFUSAL_REQUIRED')
        state=self.get(job)
        if state['phase']!='patient' or state['status']!='READY':raise ValueError('NO_REEMISSION_AFTER_EXECUTION_OR_BLOCK')
        original=self.db.execute('SELECT manifest FROM manual_packages WHERE job=?',(job,)).fetchone()
        if original is None or inventory(package)!=json.loads(original[0]):raise ValueError('ORIGINAL_PACKAGE_CHANGED')
        if self.db.execute('SELECT 1 FROM manual_collections WHERE job=?',(job,)).fetchone():raise ValueError('NO_REEMISSION_AFTER_COLLECTION')
        token=digest(raw);event=job+':identity-refusal:'+token
        payload=json.dumps({'kind':'PRECOMPUTATION_IDENTITY_REFUSED','refusal_sha256':token,'manifest_sha256':expected['manifest_sha256'],'package':json.loads(original[0])},sort_keys=True)
        old=self.db.execute('SELECT payload FROM events WHERE id=?',(event,)).fetchone()
        destination=Path(destination)
        if old:
            if old[0]!=payload or not destination.exists() or inventory(destination)!=json.loads(original[0]):raise ValueError('UNCERTAIN_REEMISSION_PRESERVE_NO_RETRY')
            return {'status':'ALREADY_REEMITTED','path':str(destination),'refusal_sha256':token}
        if destination.exists():raise ValueError('UNCERTAIN_REEMISSION_PRESERVE_NO_RETRY')
        self.db.execute('INSERT INTO events VALUES(?,?,?)',(event,job,payload))
        private_records.copytree(package,destination)
        if inventory(destination)!=json.loads(original[0]):raise ValueError('REEMISSION_COPY_CHANGED')
        return {'status':'REEMITTED_BEFORE_COMPUTATION','path':str(destination),'refusal_sha256':token}

    def reemit_infrastructure_failure(self,job,failure,authorization,decision,package,destination):
        """One explicitly authorized CPU/Colab re-emission, same reviewed code.

        The operator supplies terminal failure evidence and its exact decision;
        missing/uncertain output is never classified as infrastructure by itself.
        Original package, failure, job identity and all model charges survive.
        """
        failure,package,destination=map(Path,(failure,package,destination))
        approval=read(authorization);decision_raw=Path(decision).read_bytes()
        failed_files=inventory(failure);failed_sha=digest(json.dumps(failed_files,sort_keys=True).encode())
        original=self.db.execute('SELECT manifest FROM manual_packages WHERE job=?',(job,)).fetchone()
        if original is None or inventory(package)!=json.loads(original[0]):raise ValueError('ORIGINAL_PACKAGE_CHANGED')
        manifest=read(package/'manifest.json');manifest_sha=digest(json.dumps(manifest,sort_keys=True).encode())
        required={'schema':'manual-infrastructure-reexecution/v1','run_id':job,
            'operator_decision_sha256':digest(decision_raw),'failed_inventory_sha256':failed_sha,
            'manifest_sha256':manifest_sha,'max_additional_attempts':1,
            'terminal_confirmed':True,'classification':'infrastructure','computation_completed':False}
        if approval!=required or not decision_raw.strip():raise ValueError('EXACT_INFRASTRUCTURE_RECOVERY_AUTHORITY_REQUIRED')
        start=read(failure/'return/started.json')
        if start.get('run_id')!=job or start.get('manifest_sha256')!=manifest_sha:
            raise ValueError('FAILED_EXECUTION_PACKAGE_BINDING')
        if (failure/'return/actual').exists() or (failure/'return/receipt.json').exists():
            raise ValueError('COMPLETED_OR_PARTIAL_RESULTS_REQUIRE_SEPARATE_RECONCILIATION')
        if self.db.execute('SELECT 1 FROM manual_collections WHERE job=?',(job,)).fetchone():
            raise ValueError('NO_REEXECUTION_AFTER_COLLECTION')
        event=job+':infrastructure-reexecution'
        record={'kind':'ONE_INFRASTRUCTURE_REEXECUTION','failed_inventory':failed_files,
                'authorization':approval,'destination':str(destination.absolute()),
                'original_package':json.loads(original[0]),'additional_model_calls':0}
        payload=json.dumps(record,sort_keys=True)
        old=self.db.execute('SELECT payload FROM events WHERE id=?',(event,)).fetchone()
        if old:
            if old[0]!=payload or not destination.is_dir() or inventory(destination)!=json.loads(original[0]):
                raise ValueError('UNCERTAIN_REEXECUTION_PRESERVED_NO_RETRY')
            return {'status':'ALREADY_REEMITTED_NO_NEW_ATTEMPT','job':job}
        state=self.get(job)
        if state['phase']!='patient' or state['status']!='READY' or destination.exists():
            raise ValueError('NO_INFRASTRUCTURE_REEXECUTION_FROM_THIS_STATE')
        from orchestrator import connectivity
        connectivity.require(['drive'],self.path.parent/'connectivity.json')
        preserved=self.path.parent/'failed-executions'/job/'attempt-1'
        if preserved.exists():raise ValueError('PARTIAL_FAILURE_PRESERVATION_INSPECT_NO_RETRY')
        private_records.copytree(failure,preserved)
        if inventory(preserved)!=failed_files or inventory(failure)!=failed_files:
            raise ValueError('FAILED_EXECUTION_EVIDENCE_CHANGED')
        atomic(preserved.parent/'authority.json',approval)
        private_records.write_bytes(preserved.parent/'operator-decision.txt',decision_raw)
        # Intent precedes copy. A crash requires reconciliation, never another try.
        self.db.execute('INSERT INTO events VALUES(?,?,?)',(event,job,payload))
        private_records.copytree(package,destination)
        if inventory(destination)!=json.loads(original[0]):raise ValueError('REEMITTED_PACKAGE_CHANGED')
        return {'status':'REEMITTED_ONE_INFRASTRUCTURE_ATTEMPT','job':job,
                'path':str(destination),'failed_evidence':str(preserved),'additional_model_calls':0}

    def collect(self,job,folder,destination,validate):
        if not self.db.execute('SELECT 1 FROM manual_packages WHERE job=?',(job,)).fetchone():raise ValueError('PACKAGE_REQUIRED')
        rows=inventory(folder,allow_symlinks=True)
        prior=self.db.execute('SELECT manifest FROM manual_collections WHERE job=?',(job,)).fetchone()
        if prior:
            if json.loads(prior[0])!=rows or inventory(destination)!=rows:raise ValueError('RETURN_CONFLICT')
            return {**validate(Path(destination)),'duplicate_collection':True}
        if Path(destination).exists():raise ValueError('UNCERTAIN_COLLECTION_PRESERVE_AND_INSPECT')
        try:
            validation=validate(Path(folder))
            if validation.get('status')!='VALID':raise ValueError('RETURN_VALIDATION_FAILED')
        except (ValueError,KeyError,TypeError,AttributeError,IndexError,OSError) as error:
            rejected=Path(destination).parent/('rejected-return-'+digest(json.dumps(rows,sort_keys=True).encode())[:16])
            if not rejected.exists():private_records.copytree(folder,rejected,symlinks=True)
            if inventory(rejected,allow_symlinks=True)!=rows:raise ValueError('REJECTED_RETURN_PRESERVATION_CONFLICT')
            atomic(rejected.with_suffix('.validation.json'),{'status':'INVALID','reason':str(error),'validation':locals().get('validation'),'file_sha256':rows})
            self.block(job,'INVALID_RETURN_NO_AUTOMATIC_RERUN')
            raise ValueError('RETURN_REJECTED_'+type(error).__name__) from None
        private_records.copytree(folder,destination)
        if inventory(destination)!=rows or inventory(folder)!=rows:raise ValueError('RETURN_CHANGED_DURING_COLLECTION')
        self.db.execute('INSERT INTO manual_collections VALUES(?,?)',(job,json.dumps(rows,sort_keys=True)))
        self.db.execute("UPDATE jobs SET status='COMPLETE' WHERE id=?",(job,))
        return validation

    def status(self,job):
        return {'job':self.get(job),'inbox':self.inbox(),'calls':[dict(row) for row in self.db.execute('SELECT * FROM manual_calls')],'accounting':Accounts(self).read()[1]}
