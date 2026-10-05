"""Server-owned CPU transition using job_store and manual-lane accounting.

Execution is synchronous inside the persistent server service, never an SSH-owned
background process. The durable intent precedes Popen; interrupted intent blocks.
"""
import json
from pathlib import Path
import subprocess
import time
from orchestrator.manual_executor import ManualExecutor, atomic, digest, inventory, read
from orchestrator import cpu_package, cpu_isolation, manual_package, connectivity, private_records
from orchestrator.manual_driver import write_once


class CPUExecutor(ManualExecutor):
    def __init__(self,path,config,batch=None):
        super().__init__(path,batch=batch);self.cpu=config

    @private_records.private_umask
    def submit(self,job,binding,prepared,package):
        prior=self.db.execute('SELECT manifest FROM manual_packages WHERE job=?',(job,)).fetchone()
        if prior:
            if inventory(package)!=json.loads(prior[0]):raise ValueError('CPU_PACKAGE_CHANGED')
            if json.loads(self.get(job)['binding'])!=binding:raise ValueError('CPU_JOB_BINDING_CHANGED')
            return {'status':'ALREADY_QUEUED','job':job}
        connectivity.require(['codex','claude'],self.path.parent/'connectivity.json')
        cpu_package.verify_data(self.cpu['data_root'],read(Path(prepared)/'manifest.json')['data_binding'])
        cpu_isolation.verify_environment(self.cpu)
        if Path(package).exists():raise ValueError('CPU_PARTIAL_SUBMISSION_NO_RETRY')
        self.register(job,binding)
        if self.get(job)['status']!='READY':raise ValueError('CPU_UNCERTAIN_SUBMISSION')
        # Nothing executes here. A partial copy or ledger write refuses next time.
        private_records.copytree(prepared,package)
        files=inventory(package)
        if files!=inventory(prepared):raise ValueError('CPU_PACKAGE_COPY_CHANGED')
        self.db.execute('INSERT INTO manual_packages VALUES(?,?)',(job,json.dumps(files,sort_keys=True)))
        first=self.claim(job);self.complete_event(job,job+':cpu-acquired','VALIDATED',lease=first['lease'])
        return {'status':'QUEUED_CPU','job':job}

    @private_records.private_umask
    def execute(self,job,package,work):
        package,work=Path(package),Path(work)
        record=self.get(job)
        saved=self.db.execute('SELECT manifest FROM manual_packages WHERE job=?',(job,)).fetchone()
        if not saved or inventory(package)!=json.loads(saved[0]):raise ValueError('CPU_PACKAGE_CHANGED')
        manifest=read(package/'manifest.json')
        manual_package.check_notebook((package/'Sprint10.ipynb').read_bytes(),manifest)
        binding=json.loads(record['binding'])
        for key in ['source','spec_sha256','review_sha256','notebook_code_sha256']:
            if manifest[key]!=binding[key]:raise ValueError('CPU_EXECUTION_BINDING')
        if binding.get('cpu_config_sha256')!=digest(json.dumps(self.cpu,sort_keys=True).encode()):raise ValueError('CPU_CONFIGURATION_CHANGED')
        exit_file=work/'process-exit.json'
        if exit_file.exists():
            private_records.check_tree(work)
            result=read(exit_file)
            if result['binding_sha256']!=digest(record['binding'].encode()) or result['console_sha256']!=digest((work/'console.log').read_bytes()):raise ValueError('CPU_RESULT_BINDING_CHANGED')
            if result['exit_code']!=0 or result['uncertain']:raise ValueError('CPU_FAILED_NO_REEXECUTION')
            if record['status']=='RUNNING' and record['phase']=='dispatch':
                intent=read(work/'dispatch-intent.json')
                if intent['binding_sha256']!=result['binding_sha256']:raise ValueError('CPU_INTENT_BINDING_CHANGED')
                self.complete_event(job,job+':cpu-executed','DISPATCHED',lease=intent['lease'])
            elif record['status'] not in {'READY','COMPLETE'} or record['phase']!='patient':raise ValueError('CPU_RESULT_STATE_CONFLICT')
            return {'status':'EXECUTED','return_path':str(work/'return'),'reconciled':True}
        if record['status']!='READY' or record['phase']!='dispatch' or work.exists():
            self.block(job,'CPU_UNCERTAIN_DISPATCH_NO_RETRY');raise ValueError('CPU_UNCERTAIN_DISPATCH_NO_RETRY')
        connectivity.require(['codex','claude'],self.path.parent/'connectivity.json')
        cpu_package.verify_data(self.cpu['data_root'],manifest['data_binding'])
        private_records.mkdir(work)
        private=work/'inputs';private_records.mkdir(private)
        cases=read(Path(self.cpu['data_root'])/'development99.manifest.json')['cases']
        private_records.write_bytes(private/'split_manifest.csv',cpu_package.split_bytes(cases));private_records.write_bytes(private/'excluded_cases.json',b'[]\n')
        if inventory(private)!=manifest['private_files']:raise ValueError('CPU_DERIVED_MEMBERSHIP_HASH')
        from orchestrator.manual_host_guard import before_call
        private_records.mkdir(work/'host-preflight')
        before_call(work/'host-preflight')
        probe=work/'probe';private_records.mkdir(probe)
        argv=cpu_isolation.command(self.cpu,package,Path(self.cpu['data_root']),probe,probe=True)
        result=subprocess.run(argv,capture_output=True,text=True,timeout=60)
        write_once(work/'sandbox-probe.stdout',result.stdout.encode());write_once(work/'sandbox-probe.stderr',result.stderr.encode())
        if result.returncode:raise ValueError('CPU_SANDBOX_PROBE_REFUSED')
        argv=cpu_isolation.command(self.cpu,package,Path(self.cpu['data_root']),work)
        claimed=self.claim(job)
        if not claimed:raise ValueError('CPU_DISPATCH_NOT_CLAIMED')
        intent={'job':job,'binding_sha256':digest(record['binding'].encode()),'lease':claimed['lease'],'started_at':time.time(),'source':manifest['source'],'package_sha256':digest(json.dumps(inventory(package),sort_keys=True).encode())}
        write_once(work/'dispatch-intent.json',(json.dumps(intent,sort_keys=True)+'\n').encode())
        uncertain=False;rc=None
        try:
            with private_records.open_file(work/'console.log','xb') as log:
                process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,close_fds=True)
                atomic(work/'process.json',{'pid':process.pid,'started_at':time.time(),'binding_sha256':intent['binding_sha256']})
                try:rc=process.wait(timeout=3600)
                except BaseException:
                    process.terminate()
                    try:process.wait(timeout=10)
                    except subprocess.TimeoutExpired:process.kill();process.wait()
                    raise
        except BaseException:uncertain=True
        result={'binding_sha256':intent['binding_sha256'],'exit_code':rc,'uncertain':uncertain,'completed_at':time.time(),'console_sha256':digest((work/'console.log').read_bytes()) if (work/'console.log').exists() else None}
        write_once(exit_file,(json.dumps(result,sort_keys=True)+'\n').encode())
        private_records.check_tree(work)
        if rc!=0 or uncertain:
            self.block(job,'CPU_FAILED_OR_UNCERTAIN_NO_RETRY');raise ValueError('CPU_FAILED_OR_UNCERTAIN_NO_RETRY')
        self.complete_event(job,job+':cpu-executed','DISPATCHED',lease=claimed['lease'])
        return {'status':'EXECUTED','return_path':str(work/'return'),'reconciled':False}
