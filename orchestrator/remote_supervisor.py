"""Small supervised Linux synthetic adapter over Store; no patient/model dispatch.

Controller owns state/requests; separate credential-free worker owns outputs.
Installed code and policy are administrator-owned. No shell/job text from requests.
"""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import shutil
import sqlite3
import subprocess
import sys
import time
import uuid
from orchestrator.job_store import Store
from orchestrator.public_export import text as public_text

PAYLOAD=b'ISLES pilot synthetic execution: 6 * 7 = 42\n'
SMOKE='campaigns/isles24-pilot/colab/smoke.py'
KINDS={'synthetic_success','synthetic_failure'}

def digest(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def atomic(path,value,mode=0o640):
    p=Path(path);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    with tmp.open('x') as f:
        os.chmod(tmp,mode);json.dump(value,f,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p)

def identifier(value):
    if not isinstance(value,str) or not re.fullmatch('[A-Za-z0-9_-]{1,64}',value):raise ValueError('INVALID_ID')
    return value

@contextmanager
def lock(path):
    with Path(path).open('a') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        yield

def checked_source(root,pin):
    root=Path(root).resolve()
    if not re.fullmatch('[0-9a-f]{40}',pin):raise ValueError('SOURCE_PIN_REQUIRED')
    git_env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','GIT_OPTIONAL_LOCKS':'0'}
    actual=subprocess.check_output(['git','-c','safe.directory='+str(root),'rev-parse','HEAD'],cwd=root,text=True,env=git_env).strip()
    if actual!=pin or subprocess.check_output(['git','-c','safe.directory='+str(root),'status','--porcelain'],cwd=root,env=git_env).strip():raise ValueError('SOURCE_CHANGED')
    return root

class Controller(Store):
    def __init__(self,path):
        super().__init__(path)
        self.db.executescript('''CREATE TABLE IF NOT EXISTS linux_attempts(
        id TEXT PRIMARY KEY,job TEXT UNIQUE NOT NULL,request TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS wakes(id TEXT PRIMARY KEY,job TEXT NOT NULL,
        status TEXT NOT NULL,reason TEXT NOT NULL);
        ''')

    def submit(self,job,source,kind='synthetic_success',backend='linux',delay=0):
        identifier(job)
        if not re.fullmatch('[0-9a-f]{40}',source) or kind not in KINDS or backend not in ['linux','colab'] or type(delay) is not int or not 0<=delay<=90:raise ValueError('SYNTHETIC_BINDING_REJECTED')
        if self.db.execute('SELECT count(*) FROM jobs').fetchone()[0]>=16 and not self.db.execute('SELECT 1 FROM jobs WHERE id=?',(job,)).fetchone():raise ValueError('SUPERVISED_FIXTURE_BUDGET_EXHAUSTED')
        self.register(job,{'source':source,'kind':kind,'backend':backend,'delay':delay,'authority':'OPERATOR_SUPERVISED_SYNTHETIC_ONLY'})
        self.db.execute("UPDATE jobs SET phase='linux_synthetic' WHERE id=? AND phase='acquisition'",(job,))

    def event(self,attempt,receipt):
        row=self.db.execute('SELECT * FROM linux_attempts WHERE id=?',(attempt,)).fetchone()
        if not row:raise ValueError('UNKNOWN_ATTEMPT')
        request=json.loads(row['request'])
        validate_receipt(receipt,request)
        payload=json.dumps(receipt,sort_keys=True)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT payload FROM events WHERE id=?',(attempt,)).fetchone()
            if old:
                if old[0]!=payload:raise ValueError('CONFLICTING_EVENT')
            else:
                self.db.execute('INSERT INTO events VALUES(?,?,?)',(attempt,row['job'],payload))
                self.db.execute("UPDATE inbox SET status='RESOLVED' WHERE job=? AND reason='AMBIGUOUS_LINUX_ATTEMPT_RECONCILE_OUTPUTS_AND_PROCESS'",(row['job'],))
                self.db.execute('UPDATE jobs SET status=?,lease=0 WHERE id=?',(receipt['status'],row['job']))
                self.db.execute("INSERT INTO wakes VALUES(?,?,'PENDING_AUTH','CODEX_AUTH_AND_BOUNDED_TURN_REQUIRED')",(attempt,row['job']))
                if receipt['status']=='FAILED':
                    self.block(row['job'],'SYNTHETIC_'+receipt['failure']['kind'] if receipt.get('failure') else 'SYNTHETIC_WORKER_FAILED_OR_TIMED_OUT')
                    self.db.execute("UPDATE jobs SET status='FAILED' WHERE id=?",(row['job'],))
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise

    def tick(self,state,requests,outputs,source_root,pin,now=None):
        now=time.time() if now is None else now
        checked_source(source_root,pin)
        with lock(Path(state)/'branch.lock'):
            for r in self.db.execute('SELECT * FROM linux_attempts').fetchall():
                req=json.loads(r['request']);folder=Path(outputs)/r['id'];out=folder/'outcome.json'
                if any(x['job']==r['job'] and x['status']=='OPEN' and x['reason']=='OUTCOME_VALIDATION_FAILED' for x in self.inbox()):continue
                if out.exists():
                    try:
                        if folder.is_symlink() or out.is_symlink() or out.stat().st_size>65536:raise ValueError('OUTCOME_PATH')
                        value=read(out)
                        validate_receipt(value,req)
                        if value['status']=='COMPLETE':
                            artifact=folder/'synthetic-result.txt'
                            if artifact.is_symlink() or artifact.read_bytes()!=PAYLOAD:raise ValueError('ARTIFACT_TAMPERED')
                        for name,h in value['console_sha256'].items():
                            p=folder/name
                            if p.is_symlink() or digest(p.read_bytes())!=h:raise ValueError('CONSOLE_TAMPERED')
                        self.event(r['id'],value)
                    except (ValueError,KeyError,TypeError,OSError):
                        self.block(r['job'],'OUTCOME_VALIDATION_FAILED')
                elif self.get(r['job'])['status']=='RUNNING' and now>req['deadline']:
                    # Missing evidence never proves no execution. No automatic redispatch.
                    self.block(r['job'],'AMBIGUOUS_LINUX_ATTEMPT_RECONCILE_OUTPUTS_AND_PROCESS')
            for row in self.db.execute('SELECT * FROM linux_attempts').fetchall():
                p=Path(requests)/(row['id']+'.json')
                req=json.loads(row['request'])
                if not p.exists() and self.get(row['job'])['status']=='RUNNING' and now<=req['deadline']:
                    atomic(p,req)
            if self.db.execute("SELECT 1 FROM jobs WHERE status='RUNNING'").fetchone():return
            for job in self.db.execute("SELECT * FROM jobs WHERE status='READY' ORDER BY id").fetchall():
                binding=json.loads(job['binding'])
                if binding['backend']=='colab':self.block(job['id'],'COLAB_BROWSER_DEPENDENCY');continue
                if binding['source']!=pin:self.block(job['id'],'SOURCE_CHANGED');continue
                attempt=uuid.uuid4().hex
                req={'version':1,'attempt_id':attempt,'job_id':job['id'],'source':pin,'kind':binding['kind'],
                     'delay':binding['delay'],'deadline':now+240,'smoke_sha256':digest((Path(source_root)/SMOKE).read_bytes())}
                self.db.execute('BEGIN IMMEDIATE')
                try:
                    self.db.execute('INSERT INTO linux_attempts VALUES(?,?,?)',(attempt,job['id'],json.dumps(req,sort_keys=True)))
                    self.db.execute("UPDATE jobs SET status='RUNNING',lease=? WHERE id=?",(req['deadline'],job['id']))
                    self.db.execute('COMMIT')
                except BaseException:self.db.execute('ROLLBACK');raise
                # Crash before/after write is reconciled from the persisted immutable request.
                atomic(Path(requests)/(attempt+'.json'),req)
                break

    def status(self):
        outcomes={r['job']:json.loads(r['payload']) for r in self.db.execute('SELECT * FROM events')}
        rows=[]
        for j in self.db.execute('SELECT * FROM jobs ORDER BY id'):
            b=json.loads(j['binding']);o=outcomes.get(j['id'],{})
            reason=next((x['reason'] for x in self.inbox() if x['job']==j['id'] and x['status']=='OPEN'),None)
            rows.append({'job_id':j['id'],'status':j['status'],'source':b['source'],'kind':b['kind'],
                         'backend':b['backend'],'reason':reason,'attempt_id':o.get('attempt_id'),
                         'wall_seconds':o.get('wall_seconds'),'cpu_seconds':o.get('cpu_seconds'),
                         'peak_rss_kib':o.get('peak_rss_kib'),'artifact_sha256':o.get('artifact_sha256')})
        return {'jobs':rows,'wakes':[dict(r) for r in self.db.execute('SELECT * FROM wakes')],
                'inbox':self.inbox(),'patient_execution':False,'model_execution':False}


def limits():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU,(10,10))
    resource.setrlimit(resource.RLIMIT_FSIZE,(2*1024**2,2*1024**2))
    resource.setrlimit(resource.RLIMIT_NOFILE,(64,64))

def validate_request(req,pin,root):
    if set(req)!={'version','attempt_id','job_id','source','kind','delay','deadline','smoke_sha256'} or req['version']!=1:raise ValueError('REQUEST_SCHEMA')
    identifier(req['attempt_id']);identifier(req['job_id'])
    if req['source']!=pin or req['kind'] not in KINDS or type(req['delay']) is not int or not 0<=req['delay']<=90 or not isinstance(req['deadline'],(int,float)) or not math.isfinite(req['deadline']):raise ValueError('REQUEST_BINDING')
    if req['smoke_sha256']!=digest((Path(root)/SMOKE).read_bytes()):raise ValueError('SYNTHETIC_SOURCE_CHANGED')

def worker(requests,outputs,source_root,pin):
    root=checked_source(source_root,pin);outputs=Path(outputs)
    with lock(outputs/'worker.lock'):
        for request_file in sorted(Path(requests).glob('*.json')):
            try:
                if request_file.is_symlink() or request_file.stat().st_size>65536:raise ValueError('REQUEST_SYMLINK_OR_SIZE')
                req=read(request_file);validate_request(req,pin,root)
                if request_file.stem!=req['attempt_id']:raise ValueError('REQUEST_PATH_BINDING')
            except (ValueError,KeyError,TypeError,OSError):
                rejected=outputs/'rejected-requests';rejected.mkdir(mode=0o750,exist_ok=True)
                name=digest(request_file.name.encode())+'.json'
                if not (rejected/name).exists():atomic(rejected/name,{'status':'REQUEST_REJECTED','request_name_sha256':digest(request_file.name.encode())})
                continue
            folder=outputs/req['attempt_id']
            if folder.exists() or time.time()>req['deadline']:continue
            folder.mkdir(mode=0o750)
            boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
            atomic(folder/'started.json',{'pid':os.getpid(),'boot_id':boot,'process_start':Path('/proc/self/stat').read_text().split()[21],'request_sha256':digest(request_file.read_bytes())})
            start=time.monotonic();cpu=resource.getrusage(resource.RUSAGE_CHILDREN)
            status='FAILED';console={};retrieved=None;failure={'kind':None,'exit_code':None}
            try:
                time.sleep(req['delay'])
                commands=[['-c',"raise RuntimeError('SYNTHETIC_FAILURE')"]] if req['kind']=='synthetic_failure' else [[str(root/SMOKE),op,'--root',str(folder)] for op in ['execute','retrieve']]
                for i,args in enumerate(commands):
                    out,err=folder/f'console-{i}.stdout',folder/f'console-{i}.stderr'
                    with out.open('xb') as stdout,err.open('xb') as stderr:
                        os.chmod(out,0o640);os.chmod(err,0o640)
                        result=subprocess.run([sys.executable,*args],cwd=root,env={'PATH':'/usr/bin:/bin','HOME':str(folder),'LANG':'C.UTF-8','PYTHONNOUSERSITE':'1'},stdout=stdout,stderr=stderr,timeout=20,preexec_fn=limits)
                    if result.returncode:
                        failure={'kind':'CHILD_NONZERO','exit_code':result.returncode};raise ValueError('CHILD_FAILED')
                retrieved=read(folder/'console-1.stdout')
                if retrieved!={'retrieved_text':PAYLOAD.decode(),'sha256':digest(PAYLOAD)} or (folder/'synthetic-result.txt').read_bytes()!=PAYLOAD:raise ValueError('RETRIEVAL_MISMATCH')
                os.chmod(folder/'synthetic-result.txt',0o640)
                status='COMPLETE'
            except subprocess.TimeoutExpired:failure={'kind':'TIMEOUT','exit_code':None}
            except OSError:failure={'kind':'IO_ERROR','exit_code':None}
            except ValueError:
                if failure['kind'] is None:failure={'kind':'OUTPUT_VALIDATION','exit_code':None}
            finally:
                usage=resource.getrusage(resource.RUSAGE_CHILDREN)
                for p in folder.glob('console-*.*'):console[p.name]=digest(p.read_bytes())
                outcome={'version':2,'failure':failure,'attempt_id':req['attempt_id'],'job_id':req['job_id'],'source':pin,'status':status,
                         'request_sha256':digest(json.dumps(req,sort_keys=True).encode()),'artifact_sha256':digest(PAYLOAD) if status=='COMPLETE' else None,
                         'console_sha256':console,'wall_seconds':time.monotonic()-start,
                         'cpu_seconds':usage.ru_utime+usage.ru_stime-cpu.ru_utime-cpu.ru_stime,
                         'peak_rss_kib':usage.ru_maxrss,'separate_retrieval':status=='COMPLETE'}
                atomic(folder/'outcome.json',outcome)
            return outcome
    return None


def validate_receipt(r,req):
    keys={'version','attempt_id','job_id','source','status','request_sha256','artifact_sha256','console_sha256','wall_seconds','cpu_seconds','peak_rss_kib','separate_retrieval'}
    if r.get('version')==2:
        keys=keys|{'failure'}
        f=r.get('failure')
        if not isinstance(f,dict) or set(f)!={'kind','exit_code'} or f['kind'] not in [None,'CHILD_NONZERO','TIMEOUT','IO_ERROR','OUTPUT_VALIDATION'] or (f['exit_code'] is not None and type(f['exit_code'])!=int):raise ValueError('FAILURE_SCHEMA')
        if (r.get('status')=='COMPLETE') != (f['kind'] is None):raise ValueError('FAILURE_STATUS')
    if set(r)!=keys or r['version'] not in (1,2) or r['status'] not in ['COMPLETE','FAILED']:raise ValueError('OUTCOME_SCHEMA')
    for k in ['attempt_id','job_id','source']:
        if r[k]!=req[k]:raise ValueError('OUTCOME_BINDING')
    if r['request_sha256']!=digest(json.dumps(req,sort_keys=True).encode()):raise ValueError('REQUEST_IDENTITY')
    if r['status']=='COMPLETE' and (r['artifact_sha256']!=digest(PAYLOAD) or r['separate_retrieval'] is not True):raise ValueError('RESULT_IDENTITY')
    if r['status']=='FAILED' and (r['artifact_sha256'] is not None or r['separate_retrieval'] is not False):raise ValueError('FAILED_RESULT_FIELDS')
    for k in ['wall_seconds','cpu_seconds','peak_rss_kib']:
        if type(r[k]) not in [int,float] or not math.isfinite(r[k]) or r[k]<0:raise ValueError('RESOURCE_RECEIPT')
    expected={'console-0.stdout','console-0.stderr'}|({'console-1.stdout','console-1.stderr'} if r['status']=='COMPLETE' else set())
    if not isinstance(r['console_sha256'],dict) or not expected.issubset(r['console_sha256']):raise ValueError('CONSOLE_EVIDENCE_REQUIRED')
    for k,v in r['console_sha256'].items():
        if k not in {'console-0.stdout','console-0.stderr','console-1.stdout','console-1.stderr'} or not re.fullmatch('[0-9a-f]{64}',v):raise ValueError('CONSOLE_PATH')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['submit','tick','worker','status'])
    p.add_argument('--state',type=Path);p.add_argument('--requests',type=Path);p.add_argument('--outputs',type=Path)
    p.add_argument('--source-root',type=Path);p.add_argument('--source');p.add_argument('--job')
    p.add_argument('--kind',default='synthetic_success');p.add_argument('--backend',default='linux');p.add_argument('--delay',type=int,default=0)
    a=p.parse_args();os.umask(0o027)
    if a.action=='worker':
        result=worker(a.requests,a.outputs,a.source_root,a.source)
        print(json.dumps({'processed':result is not None}));return
    if a.state is None:p.error('private state required')
    a.state.mkdir(mode=0o700,parents=True,exist_ok=True)
    s=Controller(a.state/'jobs.sqlite')
    if a.action=='submit':s.submit(a.job,a.source,a.kind,a.backend,a.delay)
    elif a.action=='tick':s.tick(a.state,a.requests,a.outputs,a.source_root,a.source)
    value=json.dumps(s.status());public_text(value);print(value)

if __name__=='__main__':main()
