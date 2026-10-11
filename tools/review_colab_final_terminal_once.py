"""One administrative bootstrap for an exact terminal timeout; no science.

Use the standing mechanical-review exception. Preserve existing admission,
reviewer route, credentials, confinement, cap and every original ledger row.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,runpy,sys
CHANGE='colab-finalization-terminal-native-20261011'
CP=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006')/(CHANGE+'-setup2')
EXISTING=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006/colab-finalization-native-intent-20261011/invoke_advisory_existing.py')
EXISTING_SHA='573ae3fcd8e0fe42fd0fabe943738f4c0543aeb09f05ce58477b98036f43d803'
AUTHORITY='5393434195dba6418242463f846dfcc0a2647a62766de1aaf2c276c34c9321b4'
ENGINE=Path('/opt/research-system/autonomy-review/d08b91bdc1d0')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('COLAB_FINAL_ADMIN_BOOTSTRAP_'+why)

def trusted(path):
    path=Path(path)
    for p in (path,*path.parents):
        s=p.lstat();require(not p.is_symlink() and s.st_uid==0 and not s.st_mode&0o022,'TRUSTED_PATH')
    return path

def exact_adapter(previous,proof,binding):
    def verify(row,folder=None):
        if row['id']==proof.CALL:return proof.qualify(row,binding)
        return previous(row,folder)
    return verify

def one_administrative_check(original):
    used=[]
    def check(db,proof_root=None):
        require(db.in_transaction and not used,'ONE_ADMISSION_TRANSACTION')
        require(not db.execute('SELECT 1 FROM autonomy_calls WHERE change_id=?',(CHANGE,)).fetchone(),'ALREADY_RESERVED')
        used.append(True)
        return original(db,proof_root)
    return check

def main():
    require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site
        and Path(__file__).resolve()==CP/'packet/source/tools/review_colab_final_terminal_once.py','OWNER_PATH')
    meta=json.loads(trusted(CP/'BOOTSTRAP_BINDING.json').read_bytes())
    require(meta['change']==CHANGE and meta['wrapper_sha256']==sha(Path(__file__).read_bytes()),'WRAPPER_BINDING')
    sys.path.insert(0,str(ENGINE))
    from orchestrator import autonomy_review as ar,autonomy_review_runner as runner,administrative_terminal as terminal
    packet=trusted(meta['packet_path']);manifest=ar.verify_packet(packet)
    require(ar.sha(ar.canonical(manifest))==meta['packet'] and manifest['source_sha']==meta['source']
        and manifest['change_id']==CHANGE and manifest['round']==1,'PACKET_BINDING')
    source=CP/'packet/source';names=['tools/review_colab_final_terminal_once.py','orchestrator/colab_author_terminal.py',
        'docs/COLAB_FINAL_AUTHOR_TERMINAL_PRIVATE.json','docs/MECHANICAL_REPAIR_REVIEW_STANDING_AUTHORITY_20261007.txt']
    for name in names:require(sha(trusted(source/name).read_bytes())==manifest['source_files'][name],'SOURCE_BINDING')
    require(sha(trusted(source/names[-1]).read_bytes())==AUTHORITY,'STANDING_AUTHORITY')
    require(sha(trusted(EXISTING).read_bytes())==EXISTING_SHA,'EXISTING_ROUTE_CHANGED')
    spec=importlib.util.spec_from_file_location('_exact_colab_final_terminal',source/names[1]);proof=importlib.util.module_from_spec(spec);spec.loader.exec_module(proof)
    binding=proof.frozen();previous=terminal.verify;saved=terminal.administrative_exceptions
    terminal.verify=exact_adapter(previous,proof,binding)
    terminal.administrative_exceptions=one_administrative_check(saved)
    old_argv=sys.argv;sys.argv=[str(EXISTING),'--request',meta['packet']]
    try:runpy.run_path(str(EXISTING),run_name='__main__')
    finally:terminal.verify=previous;terminal.administrative_exceptions=saved;sys.argv=old_argv

if __name__=='__main__':
    os.umask(0o077);require(len(sys.argv)==1,'NO_ARGUMENTS');main()
