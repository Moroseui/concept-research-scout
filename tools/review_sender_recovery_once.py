"""One administrative recurrence/repair review; no science, retry or ledger repair.
Standing mechanical-review bootstrap: exact terminal pre-SDK failure only.
The installed reviewer, its admission/accounting, native route and confinement
stay unchanged. This process replaces only its administrative classification.
"""
import hashlib,json,os,subprocess,sys
from pathlib import Path
CHANGE='item4-sender-recovery-20261010'
CP=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006')/CHANGE
ENGINE=Path('/opt/research-system/autonomy-review/d08b91bdc1d0')
AUTHORITY='5393434195dba6418242463f846dfcc0a2647a62766de1aaf2c276c34c9321b4'
DOC='docs/ITEM4_AUTHOR22_TERMINAL_PRIVATE.json'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('SENDER_ADMIN_BOOTSTRAP_'+why)
def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        s=p.lstat();require(not p.is_symlink() and s.st_uid==0 and not s.st_mode&0o022,'UNTRUSTED')
    return path

def stopped(binding):
    v=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',binding['unit'],'-p','LoadState','-p','ActiveState','-p','MainPID','-p','ControlGroup','-p','ExecMainStatus','-p','InvocationID'],text=True,timeout=15).splitlines())
    require(v=={'LoadState':'loaded','ActiveState':'failed','MainPID':'0','ControlGroup':'','ExecMainStatus':'1','InvocationID':binding['invocation']},'EXACT_TERMINAL_INVOCATION')

def qualify(row,binding,read_file):
    require(row['id']==binding['call_id'] and row['status']=='UNCERTAIN' and row['kind']=='scientific' and sha(json.dumps(row,sort_keys=True).encode())==binding['row_sha256'],'EXACT_ORIGINAL_ROW')
    stopped(binding)
    work=Path(binding['workspace'])
    require(all(sha(read_file(work/name))==pin for name,pin in binding['files'].items()),'ORIGINAL_BYTES_CHANGED')
    require(sha(read_file(work/'.author-runtime/config.json'))==binding['config_sha256'],'CONFIG_CHANGED')
    require(sha(trusted(binding['source_path']).read_bytes())==binding['source_sha256'],'INSTALLED_SOURCE_CHANGED')
    require(not any((work/n).exists() or (work/n).is_symlink() for n in ('sent-input.json','.author-submission.json','SPEC.proposed.md','execution.plan.json','notebook.patch.json')),'NEW_OUTPUT_OR_INVOCATION')
    return {'id':row['id'],'classification':'EXACT_TERMINAL_PRE_SDK_AUTHOR22_ADMIN_ONLY','proof_sha256':sha(json.dumps(binding,sort_keys=True).encode())}

def exceptions(db,proof_root,binding,original_verify,read_file):
    require(not db.execute('SELECT 1 FROM autonomy_calls WHERE change_id=?',(CHANGE,)).fetchone(),'ONE_ADMIN_CALL_ONLY')
    result=[]
    for row in db.execute("SELECT * FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')"):
        require(row['status']=='UNCERTAIN','RUNNING_REFUSED')
        result.append(qualify(dict(row),binding,read_file) if row['id']==binding['call_id'] else original_verify(dict(row),None if proof_root is None else Path(proof_root)/row['id']))
    require(any(r['id']==binding['call_id'] for r in result),'EXACT_FAILURE_REQUIRED')
    return result

def main():
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==CP/'packet/source/tools/review_sender_recovery_once.py','OWNER_PATH')
    meta=json.loads(trusted(CP/'BOOTSTRAP_BINDING.json').read_bytes())
    require(meta['change']==CHANGE and meta['wrapper_sha256']==sha(Path(__file__).read_bytes()),'WRAPPER_BINDING')
    sys.path.insert(0,str(ENGINE))
    from orchestrator import autonomy_review as ar,autonomy_review_runner as runner,administrative_terminal as terminal,private_records as pr
    packet=trusted(meta['packet_path']);m=ar.verify_packet(packet)
    require(ar.sha(ar.canonical(m))==meta['packet'] and m['change_id']==CHANGE and m['source_sha']==meta['source'] and m['round']==1,'ONE_BOUND_PACKET')
    source=CP/'packet/source'
    for name in ('tools/review_sender_recovery_once.py',DOC,'docs/MECHANICAL_REPAIR_REVIEW_STANDING_AUTHORITY_20261007.txt'):
        require(sha(trusted(source/name).read_bytes())==m['source_files'][name],'BOUND_SOURCE')
    require(sha(trusted(source/'docs/MECHANICAL_REPAIR_REVIEW_STANDING_AUTHORITY_20261007.txt').read_bytes())==AUTHORITY,'STANDING_AUTHORITY')
    binding=json.loads(trusted(source/DOC).read_bytes());original=terminal.administrative_exceptions
    terminal.administrative_exceptions=lambda db,proof_root=None:exceptions(db,proof_root,binding,terminal.verify,lambda p:pr.check(p).read_bytes())
    try:
        result=runner.run(packet,Path('/var/lib/research-system-autonomy/reviews'));print(json.dumps(result,sort_keys=True))
        return 0 if result['status']=='COMPLETE' else 2
    finally:terminal.administrative_exceptions=original

if __name__=='__main__':
    os.umask(0o077);require(len(sys.argv)==1,'NO_ARGUMENTS');raise SystemExit(main())
