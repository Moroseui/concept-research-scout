"""Exact no-call context continuation; original recovery owns scientific admission."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

CHANGE='item4-review-evidence-paths-20261008'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-author5-submission-recovery-20261008/tools/item4_submission_recovery_component.py')
AUTHORITY='4fa50311ebe607e872cc546baf18d476d17e29b89a922310737e9cb00ba4dfef'
CHECKPOINT='7270392db86c73fa1f8347ae14bb1f4ddee4ae2b3b8005e802d19e4cc5e6f0a0'
MODULES=('manual_context','experiment_approval','experiment_acceptance')
FILES=tuple('orchestrator/'+n+'.py' for n in MODULES)+('tools/item4_review_context_component.py',
    'tools/install_item4_review_context.py','docs/REPAIR_JUDGMENT_OPERATOR_DECISION_20261008.txt','docs/ITEM4_REVIEW_CONTEXT_CHECKPOINT.json')

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def load():
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_host_guard import trusted
    if hashlib.sha256(trusted(PRIOR).read_bytes()).hexdigest()!='e43d1dac544a3fc4d8d9d7015a8558d1ed96b581e1dc6c172f97041051f6edc9':raise ValueError('CONTEXT_PRIOR_COMPONENT_CHANGED')
    h=module('_prior_author5_recovery',PRIOR)
    h.require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/'tools/item4_review_context_component.py','CONTEXT_OWNER_PATH')
    v=json.loads(h.trusted(RECORD/'installed.json').read_bytes())
    a=verify_result(Path(v['review_folder']))
    h.require(v['schema']=='reviewed-context-delivery/v1' and v['root']==str(ROOT) and
        a['verdict']=='APPROVE' and a['change_id']==CHANGE and a['source_sha']==v['source'] and
        a['report_sha256']==v['review_sha256'] and a['runtime_sha256']==h.sha(h.trusted(h.RUNTIME).read_bytes()),'CONTEXT_APPROVAL')
    m=json.loads(h.trusted(Path(v['review_folder'])/'packet-manifest.json').read_bytes())
    h.require(set(v['files'])==set(FILES),'CONTEXT_FILES')
    for n,pin in v['files'].items():h.require(h.sha(h.trusted(ROOT/n).read_bytes())==pin==m['source_files'][n],'CONTEXT_FILE_CHANGED')
    for n,pin in {**v['base_files'],**v['units']}.items():h.require(h.sha(h.trusted(n).read_bytes())==pin,'CONTEXT_BASE_CHANGED')
    h.require(h.sha(h.trusted(ROOT/'docs/REPAIR_JUDGMENT_OPERATOR_DECISION_20261008.txt').read_bytes())==AUTHORITY,'CONTEXT_AUTHORITY')
    raw=h.trusted(ROOT/'docs/ITEM4_REVIEW_CONTEXT_CHECKPOINT.json').read_bytes();h.require(h.sha(raw)==CHECKPOINT,'CONTEXT_CHECKPOINT')
    b=json.loads(raw);h.require(b['authority_sha256']==AUTHORITY,'CONTEXT_AUTHORITY_BINDING')
    import orchestrator
    # Load the shared delivery rule before all consumers, never leave stale aliases.
    h.require('orchestrator.manual_context' not in sys.modules,'CONTEXT_LOAD_ORDER')
    mc=module('orchestrator.manual_context',ROOT/'orchestrator/manual_context.py');orchestrator.manual_context=mc
    prior,rec=h.load()
    h.require(prior['review_sha256']==b['prior_review_sha256'],'CONTEXT_PRIOR_REVIEW')
    for name in MODULES[1:]:
        h.require('orchestrator.'+name not in sys.modules,'CONTEXT_CONSUMER_LOAD_ORDER')
        setattr(orchestrator,name,module('orchestrator.'+name,ROOT/'orchestrator'/(name+'.py')))
    from orchestrator import manual_driver,experiment_context,experiment_plan_output
    h.require(manual_driver.manual_context is mc and experiment_context.manual_context is mc and experiment_plan_output.mc is mc,'CONTEXT_SHARED_DELIVERY')
    return v,b,h,prior,rec

def apply():
    v,b,h,prior,rec=load()
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator import private_records as pr
    from orchestrator.manual_executor import lock
    d=ExperimentDriver(h.LANE);dest=h.STATE/'item4'/CHANGE
    try:
        with lock(h.LANE/'driver.lock'):
            d.guard();h.grant(d,prior,rec)
            raw=d.store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
            value=json.loads(raw)
            h.require(h.sha(raw.encode())==b['state_sha256'] and value['phase']=='BLOCKED' and value['reason']==b['original_failure'] and
                value['reason']=='ValueError: SEARCH_DUPLICATE_BINDING' and not value.get('pending') and
                value['rounds']=={'run_spec_author':5},'EXACT_CONTEXT_REFUSAL')
            h.require(h.sha(pr.check(h.LANE/'lane.json').read_bytes())==b['configuration_sha256'],'CONTEXT_CONFIG')
            calls=[dict(x) for x in d.store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
            globals=[dict(x) for x in d.store.batch.db.execute('SELECT * FROM autonomy_calls WHERE change_id=? ORDER BY rowid',(h.RUN,))]
            h.require(h.sha(h.canonical(calls))==b['calls_sha256'] and h.sha(h.canonical(globals))==b['globals_sha256'],'CONTEXT_ORIGINAL_CALLS')
            h.require(not d.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'CONTEXT_MODEL_RUNNING')
            h.require(not dest.exists() and not dest.is_symlink(),'CONTEXT_EXISTS_RECONCILE')
            work=h.STATE/'item4/lane-scientific-workspaces/run_spec_review-1'
            h.require(work.is_dir() and not work.is_symlink(),'EXACT_UNADMITTED_WORKSPACE')
            def inventory():
                pr.check_tree(work)
                return {str(p.relative_to(work)):h.sha(p.read_bytes()) for p in work.rglob('*') if p.is_file()}
            h.require(inventory()==b['workspace_files'],'CONTEXT_FAILED_WORKSPACE_CHANGED')
            h.require(not d.store.db.execute("SELECT 1 FROM manual_calls WHERE stage='run_spec_review'").fetchone(),'CONTEXT_REVIEW_ALREADY_ADMITTED')
            pr.mkdir(dest)
            with pr.open_file(dest/'intent.json','xb') as f:f.write(h.canonical({'checkpoint_sha256':CHECKPOINT,'review_sha256':v['review_sha256'],'original_state':value}))
            backup=pr.Connection(dest/'before.sqlite');d.store.db.backup(backup);backup.close()
            # No call owns this failed pre-admission workspace. Preserve all bytes
            # under this one-use continuation record before rebuilding review1.
            h.require(inventory()==b['workspace_files'],'CONTEXT_FAILED_WORKSPACE_CHANGED')
            work.rename(dest/'failed-pre-admission-workspace')
            h.require({str(p.relative_to(dest/'failed-pre-admission-workspace')):h.sha(p.read_bytes()) for p in (dest/'failed-pre-admission-workspace').rglob('*') if p.is_file()}==b['workspace_files'],'CONTEXT_ARCHIVE_CHANGED')
            value.update(phase='run_spec_review',reason=None);value.pop('blocked_stage',None)
            value['interventions'].append({'kind':'EXACT_EVIDENCE_IDENTITY_PATHS','authority_sha256':AUTHORITY,'review_sha256':v['review_sha256'],'original_failure_preserved':True})
            d.store.db.execute('BEGIN IMMEDIATE')
            try:
                h.require(d.store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'CONTEXT_STATE_CHANGED')
                d.store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),));d.store.db.execute('COMMIT')
            except BaseException:d.store.db.execute('ROLLBACK');raise
            h.require([dict(x) for x in d.store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]==calls,'CONTEXT_CHARGE_CHANGED')
            h.require([dict(x) for x in d.store.batch.db.execute('SELECT * FROM autonomy_calls WHERE change_id=? ORDER BY rowid',(h.RUN,))]==globals,'CONTEXT_GLOBAL_CHANGED')
            with pr.open_file(dest/'applied.json','xb') as f:f.write(h.canonical({'status':'READY_NO_MODEL_CALL','review_sha256':v['review_sha256'],'model_calls':0}))
            return {'status':'READY_NO_MODEL_CALL','model_calls':0,'limit_unchanged':200000}
    finally:d.store.db.close();d.store.batch.db.close()

def run():
    v,b,h,prior,rec=load()
    h.require(json.loads(h.trusted(RECORD/'APPLIED.json').read_bytes())['status']=='INSTALLED_HELD','CONTEXT_INSTALL_INCOMPLETE')
    # Exact existing scientific-admission wrapper, with all its cap/refusal checks.
    original=h.load;h.load=lambda:(prior,rec)
    try:return h.run()
    finally:h.load=original

if __name__=='__main__':
    os.umask(0o077)
    if sys.argv[1:]==['verify']:v,*_=load();print(json.dumps({'status':'VERIFIED_HELD','source':v['source'],'model_calls':0}))
    elif sys.argv[1:]==['apply']:print(json.dumps(apply(),sort_keys=True))
    elif sys.argv[1:]==['run']:print(json.dumps(run(),sort_keys=True))
    else:raise SystemExit('FIXED_CONTEXT_ACTION_REQUIRED')
