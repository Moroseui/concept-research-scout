"""Bound adapter for the approved Idea2 program on existing server CPU.

Reuses ManualExecutor's durable jobs and cpu_isolation. No provisioning, model
calls, scientific edits or automatic retry. Native installed entry point must
verify implementation approval and the accepted lane before calling submit.
"""
from pathlib import Path
import json, subprocess, time
from orchestrator.manual_executor import ManualExecutor, inventory
from orchestrator import private_records as pr, cpu_isolation
from orchestrator import idea2_cpu_contract as contract
from orchestrator.diagnostics_contract import validate_outputs

JOB=contract.RUN+':fixed-smoothing-server-cpu-1'

def package_files(program,full_contract):
    return {'analysis.py':program['files']['analysis.py'].encode(),
            'test_analysis.py':program['files']['test_analysis.py'].encode(),
            'contract.json':contract.encoded(full_contract),'run.py':contract.WORKER.encode()}

def hashes(files):
    return {name:{'sha256':contract.sha(raw),'bytes':len(raw)}for name,raw in files.items()}

class Idea2CPUExecutor(ManualExecutor):
    def __init__(self,path,config,batch=None):
        super().__init__(path,batch=batch);self.cpu=config

    @pr.private_umask
    def submit(self,*,source,implementation_review,metadata,program,spec,review,approval,package):
        """Caller has independently reviewed installation/owner authority.

        Exact approved scientific bytes and frozen membership are checked before
        reading any payload. The admitted local server has no incremental bill.
        """
        require=contract.require
        require(self.batch is not None,'EXISTING_BATCH_OWNER')
        owner=self.batch.db.execute('SELECT * FROM autonomy_runs WHERE id=?',(contract.RUN,)).fetchone()
        require(owner is not None and owner['status']=='ACTIVE','EXISTING_OWNER_ACTIVE')
        require(len(implementation_review)==64 and all(x in '0123456789abcdef'for x in implementation_review),'IMPLEMENTATION_BINDING')
        selected=contract.authenticate_metadata(metadata)
        scientific,program_contract=contract.authenticate_program(program,spec,review,approval)
        full=contract.build_contract(selected,program_contract,source)
        files=package_files(scientific,full);expected=hashes(files)
        package=Path(package)
        require(not package.exists() and not package.is_symlink(),'PARTIAL_PACKAGE_OR_REPLAY')
        require(not self.db.execute('SELECT 1 FROM jobs WHERE id=?',(JOB,)).fetchone(),'EXISTING_JOB_RECONCILE')
        cpu_isolation.verify_environment(self.cpu)
        observed=contract.verify_tree(self.cpu['data_root'],selected['contract']['files'])
        binding={**full['runtime'],'program_contract':program_contract,
            'scientific_review_sha256':contract.REVIEW,'implementation_review_sha256':implementation_review,
            'program_sha256':contract.PROGRAM,'package_files':expected,
            'cpu_config_sha256':contract.sha(contract.encoded(self.cpu)),
            'venue':'existing-server-cpu','incremental_micro_usd':0,
            'input_verification':full['runtime']['input_verification']}
        # A partial package or registration never authorizes a replay.
        self.register(JOB,binding)
        pr.mkdir(package)
        for name,raw in files.items():pr.write_bytes(package/name,raw);(package/name).chmod(0o400)
        contract.verify_tree(package,expected)
        self.db.execute('INSERT INTO manual_packages VALUES(?,?)',(JOB,contract.encoded(expected).decode()))
        lease=self.claim(JOB)
        require(lease is not None,'ACQUISITION_CLAIM')
        self.complete_event(JOB,JOB+':acquired','VALIDATED',lease=lease['lease'])
        return {'status':'QUEUED_EXISTING_SERVER_CPU','job':JOB,'input_verification':observed,
                'incremental_micro_usd':0,'scientific_acceptance':False}

    @pr.private_umask
    def execute(self,package,work):
        require=contract.require
        package,work=Path(package),Path(work)
        record=self.get(JOB);binding=json.loads(record['binding'])
        require(binding['cpu_config_sha256']==contract.sha(contract.encoded(self.cpu))
                and binding['venue']=='existing-server-cpu' and binding['incremental_micro_usd']==0,
                'UNCHANGED_CPU_CONFIG')
        saved=self.db.execute('SELECT manifest FROM manual_packages WHERE job=?',(JOB,)).fetchone()
        require(saved is not None and json.loads(saved[0])==binding['package_files'],'SAVED_PACKAGE')
        # No automatic reconciliation or restart here, even after a successful
        # exit. A controller can inspect durable receipts without executing.
        require(record['status']=='READY' and record['phase']=='dispatch'
                and not work.exists() and not work.is_symlink(),'UNCERTAIN_OR_PREVIOUS_EXECUTION')
        expected=binding['input_verification']['files']
        before={'inputs':contract.verify_tree(self.cpu['data_root'],expected),
                'package':contract.verify_tree(package,binding['package_files'])}
        pr.mkdir(work)
        pr.write_bytes(work/'before.json',contract.encoded(before))
        probe=work/'probe';pr.mkdir(probe)
        probe_argv=cpu_isolation.command(self.cpu,package,self.cpu['data_root'],probe,probe=True,
            imports=('numpy','scipy','nibabel'),profile='diagnostics-fixed3x3')
        checked=subprocess.run(probe_argv,capture_output=True,timeout=120)
        pr.write_bytes(work/'probe.stdout',checked.stdout);pr.write_bytes(work/'probe.stderr',checked.stderr)
        require(checked.returncode==0,'ISOLATION_PROBE_REFUSED')
        argv=cpu_isolation.command(self.cpu,package,self.cpu['data_root'],work,profile='diagnostics-fixed3x3')
        lease=self.claim(JOB);require(lease is not None,'DISPATCH_CLAIM')
        intent={'job':JOB,'binding_sha256':contract.sha(record['binding'].encode()),
                'lease':lease['lease'],'started_at':time.time(),'incremental_micro_usd':0}
        pr.write_bytes(work/'dispatch-intent.json',contract.encoded(intent))
        status={'exit_code':None,'uncertain':True,'valid':False,'error':None,**intent}
        process=None
        try:
            with pr.open_file(work/'console.log','xb') as stream:
                process=subprocess.Popen(argv,stdout=stream,stderr=subprocess.STDOUT,close_fds=True)
                pr.write_bytes(work/'process.json',contract.encoded({'pid':process.pid,'started_at':time.time()}))
                try:status['exit_code']=process.wait(timeout=3600)
                except BaseException:
                    process.terminate()
                    try:process.wait(timeout=10)
                    except subprocess.TimeoutExpired:process.kill();process.wait()
                    raise
            status['uncertain']=False
            require(status['exit_code']==0,'SCIENTIFIC_PROCESS_FAILED')
        except BaseException as error:
            status['error']=type(error).__name__+': '+str(error)
        finally:
            # Also rehash after a nonzero exit/timeout. A failed verification
            # leaves the run invalid; it never produces accepted results.
            try:
                after={'inputs':contract.verify_tree(self.cpu['data_root'],expected),
                       'package':contract.verify_tree(package,binding['package_files'])}
                require(after==before,'POST_EXECUTION_HASH_CHANGED')
                pr.write_bytes(work/'after.json',contract.encoded(after))
                if status['exit_code']==0 and not status['uncertain'] and status['error'] is None:
                    validated=validate_outputs(work/'return',binding)
                    pr.write_bytes(work/'validation.json',contract.encoded(validated))
                    status['valid']=True
            except BaseException as error:
                status['error']=(status['error']+'; ' if status['error'] else '')+type(error).__name__+': '+str(error)
            status.update(completed_at=time.time(),
                console_sha256=contract.sha((work/'console.log').read_bytes())if(work/'console.log').exists()else None)
            pr.write_bytes(work/'process-exit.json',contract.encoded(status))
        if not status['valid']:
            self.block(JOB,'IDEA2_CPU_INVALID_OR_UNCERTAIN_NO_RETRY')
            raise ValueError('IDEA2_CPU_INVALID_OR_UNCERTAIN_NO_RETRY')
        self.complete_event(JOB,JOB+':executed','DISPATCHED',lease=lease['lease'])
        return {'status':'EXECUTED_VALIDATED_NOT_SCIENTIFICALLY_ACCEPTED','job':JOB,
                'return_path':str(work/'return'),'incremental_micro_usd':0}
