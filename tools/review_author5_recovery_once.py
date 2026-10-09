"""One administrative bootstrap, under the standing mechanical-review exception.

Uses the installed reviewer/accounting/isolation unchanged, replacing only this
exact known terminal call's administrative classification for this invocation.
No scientific component is loaded or installed, no usage row is edited.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

CHANGE='item4-author5-submission-recovery-20261008'
STANDING_AUTHORITY='5393434195dba6418242463f846dfcc0a2647a62766de1aaf2c276c34c9321b4'
CP=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006')/CHANGE
REVIEW_ENGINE=Path('/opt/research-system/autonomy-review/b71912e6cfbf')

def require(ok, why):
    if not ok:raise ValueError('AUTHOR5_ADMIN_BOOTSTRAP_'+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        s=p.lstat();require(not p.is_symlink() and s.st_uid==0 and not s.st_mode&0o022,'UNTRUSTED')
    return path

def stopped(unit):
    require(unit=='research-item4-author-submission-20261008.service','EXACT_UNIT')
    values=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',unit,
        '-p','LoadState','-p','ActiveState','-p','MainPID','-p','ControlGroup'],text=True).splitlines())
    require(values=={'LoadState':'loaded','ActiveState':'inactive','MainPID':'0','ControlGroup':''},'NOT_TERMINAL')

def exceptions(db,proof_root,recovery,original_verify,read_native,*,change=CHANGE):
    require(not db.execute('SELECT 1 FROM autonomy_calls WHERE change_id=?',(change,)).fetchone(),'ONE_ADMIN_REVIEW_ONLY')
    result=[]
    for row in db.execute("SELECT * FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')"):
        require(row['status']=='UNCERTAIN','RUNNING_OR_UNKNOWN')
        if row['id']==recovery.CALL:
            stopped(recovery.UNIT)
            evidence=recovery.terminal(dict(row),read_native(recovery.binding()))
            result.append({'id':row['id'],'classification':'OPERATOR_STANDING_ONE_ADMIN_AUTHOR5_REPAIR',
                'proof_sha256':sha(json.dumps(evidence,sort_keys=True).encode())})
        else:result.append(original_verify(dict(row),None if proof_root is None else Path(proof_root)/row['id']))
    require(any(x['id']==recovery.CALL for x in result),'EXACT_FAILURE_REQUIRED')
    return result

def main():
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==CP/'packet/source/tools/review_author5_recovery_once.py','OWNER_PATH')
    metadata=json.loads(trusted(CP/'BOOTSTRAP_BINDING.json').read_bytes())
    require(metadata['change']==CHANGE and sha(Path(__file__).read_bytes())==metadata['wrapper_sha256'],'WRAPPER_BINDING')
    sys.path.insert(0,str(REVIEW_ENGINE))
    from orchestrator import autonomy_review as ar,autonomy_review_runner as runner,administrative_terminal as terminal
    from orchestrator import private_records as pr
    packet=trusted(metadata['packet_path']);m=ar.verify_packet(packet)
    ident=ar.sha(ar.canonical(m))
    require(ident==metadata['packet'] and m['change_id']==CHANGE and m['source_sha']==metadata['source'] and m['round']==1,'ONE_REQUEST_ONLY')
    source=CP/'packet/source'
    for name in ('tools/review_author5_recovery_once.py','orchestrator/author_submission_recovery.py',
        'docs/ITEM4_AUTHOR5_RECOVERY_APPROVAL_20261008.txt','docs/ITEM4_AUTHOR5_RECOVERY_BINDINGS.json',
        'docs/MECHANICAL_REPAIR_REVIEW_STANDING_AUTHORITY_20261007.txt'):
        require(sha(trusted(source/name).read_bytes())==m['source_files'][name],'REVIEWED_INPUT_CHANGED')
    require(sha(trusted(source/'docs/MECHANICAL_REPAIR_REVIEW_STANDING_AUTHORITY_20261007.txt').read_bytes())==STANDING_AUTHORITY,'STANDING_AUTHORITY_CHANGED')
    spec=importlib.util.spec_from_file_location('_exact_author5_admin',source/'orchestrator/author_submission_recovery.py')
    recovery=importlib.util.module_from_spec(spec);spec.loader.exec_module(recovery)
    def read_native(b):return {n:pr.check(Path(b['workspace'])/n).read_bytes() for n in b['native_files']}
    original=terminal.administrative_exceptions
    terminal.administrative_exceptions=lambda db,proof_root=None:exceptions(db,proof_root,recovery,terminal.verify,read_native)
    try:
        result=runner.run(packet,Path('/var/lib/research-system-autonomy/reviews'))
        print(json.dumps(result,sort_keys=True))
        return 0 if result['status']=='COMPLETE' else 2
    finally:terminal.administrative_exceptions=original

if __name__=='__main__':
    os.umask(0o077)
    require(len(sys.argv)==1,'NO_ARGUMENTS')
    raise SystemExit(main())
