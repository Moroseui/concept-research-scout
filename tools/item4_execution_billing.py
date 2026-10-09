"""Connect an already reviewed billing reader to the unchanged validation lane."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

CHANGE='item4-execution-billing-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-partition-delivery-20261009/tools/item4_validation_runtime.py')
PRIOR_SHA='8f3b690fc85ce10fa6a806cad5859366291299129d885444708c58c68e42ad99'
PRIOR_REVIEW='5dab94cbfd162c837f42f4e87debe9ead36a2833e8cb2eddb5fd78371e69636d'
BILLING_SHA='ca613aa0bcabdfd4b59147f5fb52537feb6d2d0a1b9b73d2f798ef7f5de9e7c4'
FILES=('tools/item4_execution_billing.py','tools/install_item4_execution_billing.py','orchestrator/modal_billing.py')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('EXECUTION_BILLING_'+why)

def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        st=p.lstat();require(not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'TRUSTED_SOURCE')
    return path

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

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
    require(Path(__file__).resolve()==ROOT/FILES[0] and installed['files'][FILES[2]]==BILLING_SHA,'EXECUTED_SOURCE')
    unit=Path('/etc/systemd/system')/('research-'+CHANGE+'.service')
    require(installed['units']=={str(unit):sha(trusted(unit).read_bytes())},'UNIT_CHANGED')
    return result

def connect(prior_load):
    # Preserve the existing activated authority/seal; never substitute this
    # accounting review for the R45 validation admission or scientific decision.
    result=prior_load()
    require(result[1].authority()==PRIOR_REVIEW,'PRIOR_AUTHORITY')
    authority()
    fresh=module('_execution_reviewed_billing',ROOT/'orchestrator/modal_billing.py')
    from orchestrator import modal_billing
    # Keep all existing module references/headroom accounting. capture retains
    # its own reviewed globals, including contiguous report_rows, not old ones.
    modal_billing.capture=fresh.capture
    return result

def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    require(argv and argv[0] in {'verify','advance','prepare-preprocessing','prepare-execution','measure-benchmark'},'ACTION')
    require(os.getuid()==1003 and os.getgid()==1003 and Path(__file__).resolve()==ROOT/FILES[0],'SERVICE_IDENTITY')
    require(sha(trusted(PRIOR).read_bytes())==PRIOR_SHA,'PRIOR_RUNTIME')
    prior=module('_execution_prior_validation',PRIOR)
    original=prior.load
    prior.load=lambda:connect(original)
    return prior.main(argv)

if __name__=='__main__':
    os.umask(0o077);main()
