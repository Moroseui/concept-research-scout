# One reviewed operator procedure. No installed service, timer, privilege grant,
# scientific code, changed guard, or synthetic host attestation.
from pathlib import Path
import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import time

CHANGE='item4-host-proof-refresh-20261010'
FILE='tools/item4_host_proof_operation.py'
DOCUMENT='docs/ITEM4_HOST_PROOF_PREFLIGHT_PRIVATE.json'
UNIT='research-item4-smoke-scientific-review-20261010.service'
FAILED='afa7992f3ebb491eb86ea08f8b051794'
SOURCE='7a8f4d662a2a3f8bb2b7032f0e7bfd3d620c7671'
IMPLEMENTATION='fb04e156b4b29bfbc99e86437d7266ce1df51186f72c0baef754d39a0dac1aef'
BASE=Path('/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
RUNTIME=Path('/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json')
LANE=Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/item4/lane')
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006')/CHANGE/'operation'
HOOK=BASE/'tools/manual_host_control.py'
RECEIPT=Path('/run/research-manual-sprint10/host-check.json')
ENGINE=Path('/opt/research-system/autonomy-review/d08b91bdc1d0')
ENGINE_RECEIPT=Path('/etc/research-system-autonomy/review/d08b91bdc1d0/install-receipt.json')
ENGINE_PIN='ae77aa415933b8a7586052e2260fbb4cbceec745f9d3cc54a8597e0c67d3476d'
MAX_SECONDS=3700
MAX_REFRESHES=62


def require(ok,reason):
    if not ok:raise ValueError('HOST_OPERATION_'+reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def trusted(path):
    p=Path(path)
    for q in [p,*p.parents]:
        st=q.lstat();require(not q.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'UNTRUSTED_PATH')
    return p
def command(args,**kwargs):
    return subprocess.run(args,check=True,capture_output=True,text=True,timeout=60,**kwargs).stdout
def put(path,value):
    raw=value if isinstance(value,bytes) else (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
    with Path(path).open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    Path(path).chmod(0o600)
def boot():return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def authority(review):
    require(os.getuid()==0 and sys.flags.no_user_site,'ROOT_ISOLATED_PYTHON_REQUIRED')
    engine=json.loads(trusted(ENGINE_RECEIPT).read_bytes())
    require(sha(ENGINE_RECEIPT.read_bytes())==ENGINE_PIN,'ENGINE_BINDING')
    for name,pin in engine['files'].items():require(sha(trusted(name).read_bytes())==pin,'ENGINE_CHANGED')
    sys.path.insert(0,str(ENGINE))
    from orchestrator.autonomy_review import verify_result
    approval=verify_result(review);manifest=json.loads((Path(review)/'packet-manifest.json').read_bytes())
    require(approval['verdict']=='APPROVE' and approval['change_id']==CHANGE and
        manifest['source_sha']==approval['source_sha'],'APPROVAL_REQUIRED')
    root=Path(__file__).resolve().parents[1]
    require(sha(trusted(__file__).read_bytes())==manifest['source_files'][FILE],'EXECUTED_SOURCE')
    raw=trusted(root/DOCUMENT).read_bytes();require(sha(raw)==manifest['source_files'][DOCUMENT],'FROZEN_SCOPE')
    return json.loads(raw),approval


def hashes(frozen):
    for name,pin in frozen['hashes'].items():require(sha(trusted(name).read_bytes())==pin,'HOST_SOURCE_CHANGED')


def unit():
    names=['ActiveState','MainPID','InvocationID','ControlGroup','ExecMainStatus','ExecMainStartTimestampMonotonic']
    args=['systemctl','show',UNIT]
    for n in names:args+=['-p',n]
    rows=command(args).splitlines();value=dict(row.split('=',1) for row in rows)
    require(set(value)==set(names),'UNIT_SHAPE')
    return value


def live(value,run):
    require(re.fullmatch('[0-9a-f]{32}',run['invocation']) is not None and run['invocation']!=FAILED,'INVOCATION_FORMAT')
    require(value['ActiveState']=='activating' and value['InvocationID']==run['invocation'] and
        value['ControlGroup']=='/system.slice/'+UNIT and int(value['MainPID'])>0 and
        int(value['ExecMainStartTimestampMonotonic'])==run['started_monotonic_us'],'INVOCATION_CHANGED')
    os.kill(int(value['MainPID']),0)  # Liveness only; no signal is delivered.
    require(run['boot_id']==boot() and 0<=time.monotonic()-run['started_monotonic_us']/1e6<MAX_SECONDS,'INVOCATION_EXPIRED')


def terminal(value,run):
    return (value['ActiveState'] in {'inactive','failed'} and value['MainPID']=='0' and
        value['ControlGroup']=='' and value['InvocationID'] in {'',run['invocation']} and
        int(value['ExecMainStartTimestampMonotonic'])==run['started_monotonic_us'])


def safe_stop(run):
    value=unit()
    if value['InvocationID']==run['invocation'] and value['ActiveState'] in {'activating','active'}:
        command(['systemctl','stop',UNIT])


def starting_state(frozen):
    # All live database reads and archive/workspace reads happen as service UID.
    child="""import os,json,sqlite3,hashlib,sys
from pathlib import Path
assert os.getuid()==os.getgid()==1003
f=json.loads(sys.argv[1]);lane=Path(sys.argv[2]);record=Path(f['archive'])
assert not record.is_symlink() and hashlib.sha256(record.read_bytes()).hexdigest()==f['archive_sha']
a=json.loads(record.read_bytes());work=Path(a['workspace'])
files={str(p.relative_to(work)):hashlib.sha256(p.read_bytes()).hexdigest() for p in work.rglob('*') if p.is_file()}
assert not any(p.is_symlink() for p in work.rglob('*')) and files==a['files']
with sqlite3.connect((lane/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 rows=[dict(r) for r in db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
 assert {r['id']:hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest() for r in rows}==f['local_calls']
 raw=db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
 assert hashlib.sha256(raw.encode()).hexdigest()==f['state']
 v=json.loads(raw);assert v['phase']=='run_spec_review' and not v.get('pending')
 assert db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==24
 assert not db.execute("SELECT 1 FROM manual_calls WHERE stage='run_spec_review' AND attempt=11").fetchone()
with sqlite3.connect('file:/var/lib/research-system-autonomy/reviews/jobs.sqlite?mode=ro',uri=True) as db:
 assert not db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone()
 assert not db.execute('SELECT 1 FROM autonomy_calls WHERE id=?',(f['call_id'],)).fetchone()
print(json.dumps({'state_sha256':f['state'],'local_calls':24,'workspace_preserved':True}))
"""
    return json.loads(command(['runuser','-u','partho','--','python3','-s','-B','-c',child,json.dumps(frozen),str(LANE)]))


def verify_installed():
    child="""from pathlib import Path
import os,sys,json,importlib.util
assert os.getuid()==os.getgid()==1003
sys.path.insert(0,sys.argv[1]);p=Path('/opt/research-system/manual-repair-helpers/item4-smoke-scientific-review-20261010/tools/item4_smoke_review_runtime.py')
s=importlib.util.spec_from_file_location('_installed_smoke_authority',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
a=m.authority();assert a['source_sha']==sys.argv[2] and a['report_sha256']==sys.argv[3]
print(json.dumps({'status':'GENUINE_INSTALLED_APPROVAL','source':a['source_sha']}))
"""
    return json.loads(command(['runuser','-u','partho','--','env','RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),
        'python3','-s','-B','-c',child,str(BASE),SOURCE,IMPLEMENTATION]))


def start(frozen,approval):
    hashes(frozen);installed=verify_installed();before=unit()
    require(before['ActiveState']=='failed' and before['MainPID']=='0' and before['ControlGroup']=='' and
        before['ExecMainStatus']=='1' and before['InvocationID']==FAILED,'ORIGINAL_NOT_TERMINAL')
    state=starting_state(frozen)
    put(RECORD/'START_INTENT.json',{'before':before,'state':state,'installed':installed,'review_sha256':approval['report_sha256']})
    command(['systemctl','start','--no-block',UNIT])
    deadline=time.monotonic()+30
    while time.monotonic()<deadline:
        value=unit()
        if value['ActiveState']=='activating' and int(value['MainPID'])>0:
            run={'invocation':value['InvocationID'],'started_monotonic_us':int(value['ExecMainStartTimestampMonotonic']),
                'boot_id':boot(),'review_sha256':approval['report_sha256'],'source_sha':approval['source_sha']}
            live(value,run);put(RECORD/'RUN.json',run)
            return {'status':'STARTED_ONCE','run':run}
        require(value['ActiveState'] not in {'failed','inactive'},'START_TERMINAL_RECONCILE')
        time.sleep(0.1)
    raise ValueError('HOST_OPERATION_START_UNCERTAIN_RECONCILE')


def pulse(frozen,approval):
    run=json.loads(trusted(RECORD/'RUN.json').read_bytes())
    try:
        require(run['review_sha256']==approval['report_sha256'] and run['source_sha']==approval['source_sha'],'RUN_AUTHORITY')
        value=unit()
        if terminal(value,run):return {'status':'TERMINAL_NO_REFRESH','unit':value}
        live(value,run);hashes(frozen)
        rounds=sorted(RECORD.glob('refresh-*'))
        require(len(rounds)<MAX_REFRESHES and all((p/'COMPLETE.json').is_file() for p in rounds),'REFRESH_BOUND_OR_UNCERTAIN')
        folder=RECORD/('refresh-%03d'%(len(rounds)+1));folder.mkdir(mode=0o700)
        put(folder/'INTENT.json',{'unit':value,'at_monotonic':time.monotonic()})
        put(folder/'previous-proof.json',trusted(RECEIPT).read_bytes())
        env={'PATH':'/usr/bin:/bin','PYTHONPATH':str(BASE),'INVOCATION_ID':run['invocation']}
        try:
            output=command(['/usr/bin/python3','-s','-B',str(HOOK),'before','--runtime',str(RUNTIME),'--lane',str(LANE)],env=env)
        except subprocess.CalledProcessError as error:
            put(folder/'REFUSAL.json',{'exit':error.returncode,'stdout':error.stdout,'stderr':error.stderr});raise
        put(folder/'stdout.txt',output.encode());raw=trusted(RECEIPT).read_bytes();proof=json.loads(raw)
        put(folder/'fresh-proof.json',raw)
        require(proof['status']=='PASS' and proof['invocation']==run['invocation'] and
            proof['runtime_sha256']==frozen['hashes'][str(RUNTIME)] and proof['lane']==str(LANE) and
            proof['boot_id']==run['boot_id'] and 0<=time.time()-proof['time']<180,'FRESH_PROOF_BINDING')
        after=unit()
        if not terminal(after,run):live(after,run)
        put(folder/'COMPLETE.json',{'status':'GENUINE_POLICY_RECHECK','unit':after,'proof_sha256':sha(raw)})
        return {'status':'REFRESHED' if not terminal(after,run) else 'TERMINAL_AFTER_REFRESH','number':len(rounds)+1}
    except BaseException:
        safe_stop(run);raise


def main():
    os.umask(0o077)
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['start','pulse']);parser.add_argument('--review',required=True);args=parser.parse_args()
    frozen,approval=authority(args.review)
    if not RECORD.exists():trusted(RECORD.parent);RECORD.mkdir(mode=0o700)
    trusted(RECORD)
    with (RECORD/'operation.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        result=start(frozen,approval) if args.action=='start' else pulse(frozen,approval)
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
