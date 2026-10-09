"""Connect the exact pre-science stop to conservative cost reconciliation."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
CHANGE='item4-cost-runtime-bootstrap-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-preprocessing-root-repair-20261009/tools/item4_preprocessing_fresh_runtime.py')
PRIOR_SHA='9f8f192949af976f55a0eff8d2a0afe6e7300561024bfaadfa6e3913913155d4'
PRIOR_REVIEW='860f9f3193c005944116508220aa32584f3b79edd5b4c22cd1cd833258ef59ec'
FILES=('tools/item4_cost_runtime_bootstrap.py','tools/install_item4_cost_bootstrap.py','orchestrator/modal_terminal_cost.py')


def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('FRESH_RUNTIME_'+why)
def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        st=p.lstat();require(not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'TRUSTED_SOURCE')
    return path
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m


def authority():
    from orchestrator.autonomy_review import verify_result
    installed=json.loads(trusted(RECORD/'installed.json').read_bytes())
    result=verify_result(trusted(RECORD/'review'))
    manifest=json.loads(trusted(RECORD/'review/packet-manifest.json').read_bytes())
    require(result['verdict']=='APPROVE' and result['change_id']==CHANGE and
        result['source_sha']==installed['source']==manifest['source_sha'] and
        result['report_sha256']==installed['review_sha256'],'GENUINE_APPROVAL')
    require(set(installed['files'])==set(FILES),'INSTALL_MEMBERS')
    for name in FILES:
        require(sha(trusted(ROOT/name).read_bytes())==installed['files'][name]==manifest['source_files'][name],'SOURCE_CHANGED')
    require(Path(__file__).resolve()==ROOT/FILES[0],'EXECUTED_SOURCE')
    unit=Path('/etc/systemd/system')/('research-'+CHANGE+'.service')
    require(installed['units']=={str(unit):sha(trusted(unit).read_bytes())},'UNIT_CHANGED')
    return result



def connect():
    require(sha(trusted(PRIOR).read_bytes())==PRIOR_SHA,'PRIOR_SOURCE_CHANGED')
    prior=module('_pre_science_cost_prior',PRIOR)
    original=prior.connect
    def wired():
        result=original()  # Existing authenticated bootstrap establishes module paths.
        require(prior.authority()['report_sha256']==PRIOR_REVIEW,'PRIOR_APPROVAL')
        authority()  # Before connecting any candidate code or dispatching an action.
        from orchestrator import modal_terminal_cost
        candidate=module('_pre_science_cost_record',ROOT/'orchestrator/modal_terminal_cost.py')
        require(not candidate.record.__code__.co_freevars,'RECORD_CLOSURE')
        modal_terminal_cost.record.__code__=candidate.record.__code__
        return result
    prior.connect=wired
    return prior


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/FILES[0],'SERVICE_IDENTITY')
    require(argv and argv[0] in {'verify','advance','prepare-execution','measure-benchmark'},'ACTION_SCOPE')
    return connect().main(argv)

if __name__=='__main__':
    os.umask(0o077);main()
