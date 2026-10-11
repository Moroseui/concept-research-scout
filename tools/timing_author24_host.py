"""Fixed successor unit using the unchanged author host start/pulse checks."""
import importlib.util,json,os,sys
from pathlib import Path
ROOT=Path('/opt/research-system/manual-repair-helpers/timing-author24-preparation-recovery-20261010')

def runtime():
    path=ROOT/'tools/timing_author24_runtime.py'
    for p in [path,*path.parents]:
        st=p.lstat()
        if p.is_symlink() or st.st_uid!=0 or st.st_mode&0o022:raise ValueError('TIMING_HOST_TRUSTED_PATH')
    spec=importlib.util.spec_from_file_location('_timing_host_authority',path);rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt);return rt

def connect():
    rt=runtime();rt.require(os.getuid()==0 and sys.flags.no_user_site,'HOST_ROOT_ISOLATED')
    rt.require(Path(__file__).resolve()==rt.ROOT/'tools/timing_author24_host.py','HOST_EXECUTED_PATH')
    sys.path.insert(0,str(rt.SCIENCE))
    approval=rt.authority()
    installed=json.loads(rt.trusted(rt.RECORD/'installed.json').read_bytes())
    complete=json.loads(rt.trusted(rt.RECORD/'COMPLETE.json').read_bytes())
    rt.require(complete=={'status':'INSTALLED_HELD','source':approval['source_sha'],'scientific_calls':0,'provider_calls':0},'SERVICE_VERIFICATION_REQUIRED')
    caphost=rt.load('_timing_original_cap_host',rt.CAP/'tools/temporary_daily_cap_host.py')
    host=caphost.connect()
    frozen,_=host.authority(caphost.OLD_REVIEW)
    frozen['hashes']={**frozen['hashes'],**installed['units'],**{str(rt.ROOT/n):p for n,p in installed['files'].items()}}
    host.hashes(frozen)
    host.UNIT='research-'+rt.CHANGE+'.service'
    rt.require('/etc/systemd/system/'+host.UNIT in installed['units'],'EXACT_SUCCESSOR_UNIT')
    host.ENTRY=rt.ROOT/'tools/timing_author24_runtime.py'
    host.OPERATION_ROOT=rt.RECORD/'operation'
    original_starting=host.starting_state
    def starting(frozen,approval):
        value=original_starting(frozen,approval)
        child="import importlib.util,os,sys;from pathlib import Path;assert os.getuid()==os.getgid()==1003;sys.path.insert(0,sys.argv[1]);s=importlib.util.spec_from_file_location('_timing_preservation_check',sys.argv[2]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.authority();m.preservation();print('PRESERVED')"
        proof=host.command(['runuser','-u','partho','--','env','RESEARCH_MANUAL_RUNTIME_CONFIG='+str(host.RUNTIME),'python3','-s','-B','-c',child,str(rt.SCIENCE),str(host.ENTRY)])
        rt.require(proof.strip()=='PRESERVED','PRESERVATION_PRESTART_REQUIRED')
        return value
    host.starting_state=starting
    host.authority=lambda review:(frozen,approval)
    return host

def connect_colab(transition):
    rt=runtime();rt.require(os.getuid()==0 and sys.flags.no_user_site,'HOST_ROOT_ISOLATED')
    rt.require(Path(__file__).resolve()==rt.ROOT/'tools/timing_author24_host.py','HOST_EXECUTED_PATH')
    sys.path.insert(0,str(rt.PREPARATION));approval=rt.authority()
    installed=json.loads(rt.trusted(rt.RECORD/'installed.json').read_bytes())
    complete=json.loads(rt.trusted(rt.RECORD/'COMPLETE.json').read_bytes())
    rt.require(complete=={'status':'INSTALLED_HELD','source':approval['source_sha'],'scientific_calls':0,'provider_calls':0},'SERVICE_VERIFICATION_REQUIRED')
    old=rt.load('_original_colab_preparation_host',rt.REPAIRED/'tools/preparation_branch_repair_host.py')
    host=old.connect('colab_preparation',transition)
    frozen,_=host.authority(None)
    frozen['hashes']={**frozen['hashes'],**installed['units'],**{str(rt.ROOT/n):pin for n,pin in installed['files'].items()}}
    host.hashes(frozen)
    host.UNIT='research-'+rt.CHANGE+'-colab_preparation.service'
    rt.require('/etc/systemd/system/'+host.UNIT in installed['units'],'EXACT_COLAB_SUCCESSOR_UNIT')
    host.ENTRY=rt.ROOT/'tools/preparation_mechanical_continuation.py'
    host.OPERATION_ROOT=rt.RECORD/'operations/colab_preparation'/transition
    original_starting=host.starting_state
    def starting(frozen,approval):
        value=original_starting(frozen,approval)
        # The helper checks the exact retained completed row and normal next
        # author attempt. This is read-only and precedes the fresh START_INTENT.
        host.command(['runuser','-u','partho','--','env','PYTHONPATH='+str(rt.PREPARATION),'RESEARCH_MANUAL_RUNTIME_CONFIG='+str(host.RUNTIME),'python3','-s','-B',str(host.ENTRY),'ready-colab'])
        return value
    host.starting_state=starting;host.authority=lambda review:(frozen,approval)
    return host

def main(argv=None):
    argv=sys.argv[1:] if argv is None else argv
    colab=False
    if len(argv)==1 and argv[0] in {'start','pulse'}:host=connect()
    elif len(argv)==3 and argv==['status','--lane','colab_preparation']:
        rt=runtime();rt.require(os.getuid()==0 and sys.flags.no_user_site,'HOST_ROOT_ISOLATED');sys.path.insert(0,str(rt.PREPARATION));rt.authority()
        old=rt.load('_original_colab_status',rt.REPAIRED/'tools/preparation_branch_repair_host.py');value=old.status('colab_preparation');connect_colab(value['transition']);print(json.dumps(value,sort_keys=True));return
    elif len(argv)==5 and argv[0] in {'start','pulse'} and argv[1:4]==['--lane','colab_preparation','--transition']:
        import re
        if re.fullmatch('[0-9a-f]{64}',argv[4]) is None:raise ValueError('TIMING_HOST_TRANSITION_REQUIRED')
        colab=True;host=connect_colab(argv[4]);rt=runtime()
        for path in [rt.RECORD/'operations',rt.RECORD/'operations/colab_preparation',host.OPERATION_ROOT]:
            if not path.exists():rt.trusted(path.parent);path.mkdir(mode=0o700);path.chmod(0o700)
            rt.trusted(path)
    else:raise ValueError('TIMING_HOST_ACTION_SCOPE')
    prior=sys.argv
    try:
        sys.argv=[str(__file__),argv[0],'--stage','author','--review','/var/lib/research-system-manual-sprint10-deployment/timing-author24-preparation-recovery-20261010/review']
        return host.main()
    finally:sys.argv=prior

if __name__=='__main__':
    os.umask(0o077);main()
