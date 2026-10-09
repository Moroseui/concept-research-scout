"""Connect the approved native checkpoint continuation without changing scientific identity."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
CHANGE='item4-stage1-cap-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-fit-stdin-recovery-20261009/tools/item4_checkpoint_runtime.py')
PRIOR_SHA='92cae462788c9d71caf973e4a36fb9aa6959fe48868b8df7da1a7e54d9d2b649'
PRIOR_REVIEW='8c37a6c932009dbb3d133ef7838c744b3a8714c58682dc3b11745c4458b12ac8'
FILES=('tools/item4_stage1_cap_runtime.py','tools/install_item4_stage1_cap.py','orchestrator/item4_stage1_cap.py','orchestrator/modal_item4_budget.py','docs/ITEM4_STAGE1_CAP_OPERATOR_DECISION_20261009.txt')


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
    units=[unit] # Existing reviewed retention timer remains the sole cleanup owner.
    require(installed['units']=={str(p):sha(trusted(p).read_bytes()) for p in units},'UNIT_CHANGED')
    return result



def connect():
    require(sha(trusted(PRIOR).read_bytes())==PRIOR_SHA,'PRIOR_SOURCE_CHANGED')
    route=module('_stage1_cap_prior',PRIOR)
    prior=route.connect();original=prior.connect
    def wired():
        result=original()
        require(route.authority()['report_sha256']==PRIOR_REVIEW,'PRIOR_APPROVAL')
        authority()
        import orchestrator
        from orchestrator import modal_item4_budget
        helper=module('orchestrator.item4_stage1_cap',ROOT/'orchestrator/item4_stage1_cap.py')
        orchestrator.item4_stage1_cap=helper
        require(sha(trusted(ROOT/helper.DOCUMENT).read_bytes())==helper.OPERATOR_SHA,'OPERATOR_APPROVAL')
        candidate=module('_stage1_cap_budget',ROOT/'orchestrator/modal_item4_budget.py')
        require(not candidate.reserve.__code__.co_freevars,'BUDGET_CLOSURE')
        modal_item4_budget.reserve.__code__=candidate.reserve.__code__
        modal_item4_budget.reserve.__kwdefaults__=candidate.reserve.__kwdefaults__
        require((modal_item4_budget.PROJECTION_LIMIT,modal_item4_budget.TOTAL_CAP)==(1_200_000_000,1_275_000_000),'OTHER_CAPS_CHANGED')
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
