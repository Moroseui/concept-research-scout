"""Connect the approved native checkpoint continuation without changing scientific identity."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
CHANGE='item4-deliberate-smoke-stop-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-smoke-connection-20261009/tools/item4_smoke_runtime.py')
PRIOR_SHA='e9318492ba7fab85238f310b135312ba9f6fa549e4eb1563e2257aa90f59ef91'
PRIOR_REVIEW='8d1b54f44b373ed169f172ee7eb697ed7f8162eaccafa707af61c76e5276fef8'
FILES=('tools/item4_deliberate_smoke_runtime.py','tools/install_item4_deliberate_smoke.py','orchestrator/item4_deliberate_smoke.py','orchestrator/experiment_dispatch.py','orchestrator/modal_item4_budget.py','tools/publish_item4_smoke_handoff.py')


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
    route=module('_deliberate_smoke_prior',PRIOR)
    prior=route.connect();original=prior.connect
    def wired():
        result=original()
        require(route.authority()['report_sha256']==PRIOR_REVIEW,'PRIOR_APPROVAL')
        authority()
        import orchestrator
        from orchestrator import modal_item4_budget,experiment_dispatch
        helper=module('orchestrator.item4_deliberate_smoke',ROOT/'orchestrator/item4_deliberate_smoke.py')
        orchestrator.item4_deliberate_smoke=helper
        candidate=module('_deliberate_smoke_budget',ROOT/'orchestrator/modal_item4_budget.py')
        dispatch=module('_deliberate_smoke_dispatch',ROOT/'orchestrator/experiment_dispatch.py')
        # Keep installed admission and every earlier connection intact. Only
        # add the optional checkpoint pin and the immediate stop-control call.
        require(not candidate.record_interruption.__code__.co_freevars,'BUDGET_CLOSURE')
        modal_item4_budget.record_interruption.__code__=candidate.record_interruption.__code__
        modal_item4_budget.record_interruption.__kwdefaults__=candidate.record_interruption.__kwdefaults__
        # private_umask wraps advance; its original function carries the code.
        before=experiment_dispatch.advance.__wrapped__
        after=dispatch.advance.__wrapped__
        require(not after.__code__.co_freevars and not before.__code__.co_freevars,'DISPATCH_CLOSURE')
        before.__code__=after.__code__
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
