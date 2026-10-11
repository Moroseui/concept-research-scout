"""Ordered reuse of the original author24 route and installed terminal proof."""
import argparse,hashlib,importlib.util,json,os,sys
from pathlib import Path
CHANGE='timing-author24-preparation-recovery-20261010'
REVIEW_CHANGE='rotation-timing-direction-20261010'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
SCIENCE=Path('/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
PREPARATION=Path('/opt/research-system/manual-repair-helpers/preparation-and-cap-repair-20261010')
REPAIRED=Path('/opt/research-system/manual-repair-helpers/preparation-branch-admission-repair-20261010')
CAP=Path('/opt/research-system/manual-repair-helpers/temporary-daily-cap-20261010')
def require(ok,why):
    if not ok:raise ValueError('TIMING_AUTHOR24_'+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        s=p.lstat();require(not p.is_symlink() and s.st_uid==0 and not s.st_mode&0o022,'TRUSTED_PATH')
    return path
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,trusted(path));m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def authority():
    from orchestrator.autonomy_review import verify_result
    require(Path(__file__).resolve()==ROOT/'tools/timing_author24_runtime.py','EXECUTED_SOURCE')
    result=verify_result(trusted(RECORD/'review'));manifest=json.loads(trusted(RECORD/'review/packet-manifest.json').read_bytes());installed=json.loads(trusted(RECORD/'installed.json').read_bytes())
    require(result['change_id']==REVIEW_CHANGE and result['verdict']=='APPROVE' and not result.get('findings'),'GENUINE_APPROVAL')
    require(installed['source']==result['source_sha'] and installed['review_sha256']==result['report_sha256'] and installed['status']=='INSTALLED_HELD' and installed['root']==str(ROOT),'HELD_INSTALL')
    require(set(installed['files'])>={'tools/timing_author24_runtime.py','tools/timing_author24_preparation_recovery.py','docs/TIMING_AUTHOR24_PREPARATION_PRIVATE.json'},'COMPONENT_MEMBERS')
    for name,pin in installed['files'].items():require(sha(trusted(ROOT/name).read_bytes())==pin==manifest['source_files'][name],'REVIEWED_SOURCE_CHANGED')
    for name,pin in installed['units'].items():require(sha(trusted(name).read_bytes())==pin,'UNIT_CHANGED')
    return result

def route():
    authority()
    import orchestrator
    require(Path(orchestrator.__file__).resolve()==SCIENCE/'orchestrator/__init__.py','ORIGINAL_SCIENCE_IMPORT')
    repaired=load('_timing_installed_proof_authority',REPAIRED/'tools/preparation_branch_repair_runtime.py');repaired.authority()
    cap=load('_timing_installed_cap',CAP/'tools/temporary_daily_cap.py');old=cap.author_route();factory=old.module
    def selected(name,path):
        if name=='orchestrator.item4_scoped_calls':
            require(Path(path)==old.ROOT/'orchestrator/item4_scoped_calls.py','EXACT_SCOPED_COMPONENT')
            return factory(name,PREPARATION/'orchestrator/item4_scoped_calls.py')
        return factory(name,path)
    old.module=selected;previous=old.connect;used=[]
    def ordered():
        require(not used,'ONE_TIMING_CONNECTION');used.append(True)
        # Old context must be loaded first. Preparation's import of
        # experiment_context before this point would trigger the old refusal.
        result=previous()
        load('orchestrator.aggregate_analysis_scope',PREPARATION/'orchestrator/aggregate_analysis_scope.py')
        proof_module=load('_timing_terminal_proof',REPAIRED/'tools/preparation_premodel_recovery.py')
        proof=proof_module.load_verified_proof(repaired.RECORD/'review')
        pi=load('orchestrator.preparation_interleaving',REPAIRED/'orchestrator/preparation_interleaving.py');orchestrator.preparation_interleaving=pi;pi.configure_premodel(proof)
        preparation=load('_timing_original_preparation',PREPARATION/'tools/preparation_scientific_runtime.py')
        scope=json.loads(trusted(preparation.RECORD/'preparation-interleaving.json').read_bytes())
        overlay=pi.Overlay(scope,preparation.RECORD/'review');preparation.reviewed_root(overlay);pi.connect(scope,preparation.RECORD/'review')
        return result
    old.connect=ordered
    return old

def connect():
    return route().connect()

def preservation():
    recovery=load('_timing_preparation_recovery',ROOT/'tools/timing_author24_preparation_recovery.py')
    completed=json.loads(recovery.pr.check(recovery.ARCHIVE/'COMPLETE.json').read_bytes())
    require(completed['status']=='PRESERVED_UNADMITTED_PREPARATION' and completed['binding_sha256']==recovery.DOCUMENT_SHA and completed['review_sha256']==authority()['report_sha256'],'PRESERVATION_REQUIRED')
    require(recovery.inventory(recovery.ARCHIVE/'workspace')==recovery.binding()['tree'] and recovery.metadata(recovery.ARCHIVE/'runtime-pins-24.json')==recovery.binding()['pins_metadata'],'ORIGINAL_PREPARATION_CHANGED')
    return completed

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('action',choices=['verify','run']);a=p.parse_args(argv)
    require(os.getuid()==os.getgid()==1003,'SERVICE_OWNER')
    old=route()
    if a.action=='run':preservation()
    return old.main([a.action])
if __name__=='__main__':
    os.umask(0o077);sys.path.insert(0,str(SCIENCE));main()
