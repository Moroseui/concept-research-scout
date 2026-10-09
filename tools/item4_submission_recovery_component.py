"""Recover exact author5 bytes into normal scientific review, no author rerun."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import sys

CHANGE = 'item4-author5-submission-recovery-20261008'
ROOT = Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD = Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
LEGACY = Path('/opt/research-system/manual-repair-helpers/item4-author-submission-20261008/tools/item4_author_submission_component.py')
SCIENCE = Path('/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
STATE = Path('/var/lib/research-system-manual-sprint10/releases')/SCIENCE.name
LANE = STATE/'item4/lane'
WORK = STATE/'item4/lane-scientific-workspaces/run_spec_author-5'
DEST = STATE/'item4'/CHANGE
RUNTIME = Path('/etc/research-system-manual-sprint10/releases')/SCIENCE.name/'runtime.json'
FILES = ('tools/item4_submission_recovery_component.py','tools/install_item4_submission_recovery.py',
    'orchestrator/author_format_submission.py','orchestrator/author_submission_recovery.py',
    'docs/ITEM4_AUTHOR5_RECOVERY_APPROVAL_20261008.txt','docs/ITEM4_AUTHOR5_RECOVERY_BINDINGS.json')
AUTHORITY = 'a9ded8872a67385ab3a47f95a39914271ba8f4de9a8f8015c197bb7be35c4ef6'
REVIEW_STAGE = 'run_spec_review'
RUN = 'experiment-a74959ac4546a982af4ae137'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def require(ok, why):
    if not ok: raise ValueError('SUBMISSION_RECOVERY_'+why)
def trusted(path):
    path = Path(path)
    for p in [path,*path.parents]:
        st=p.lstat(); require(not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'UNTRUSTED')
    return path

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec)
    sys.modules[name]=value;spec.loader.exec_module(value);return value

def verified():
    from orchestrator.autonomy_review import verify_result
    v=json.loads(trusted(RECORD/'installed.json').read_bytes())
    require(v['schema']=='reviewed-author5-submission-recovery/v1' and v['root']==str(ROOT),'INSTALL_SCOPE')
    approved=verify_result(Path(v['review_folder']))
    require(approved['verdict']=='APPROVE' and approved['change_id']==CHANGE and
        approved['source_sha']==v['source'] and approved['report_sha256']==v['review_sha256'] and
        approved['runtime_sha256']==sha(trusted(RUNTIME).read_bytes()),'GENUINE_APPROVAL')
    manifest=json.loads(trusted(Path(v['review_folder'])/'packet-manifest.json').read_bytes())
    require(set(v['files'])==set(FILES),'FILE_SET')
    for n,pin in v['files'].items():
        require(sha(trusted(ROOT/n).read_bytes())==pin==manifest['source_files'][n],'REVIEWED_FILE_CHANGED')
    for n,pin in {**v['base_files'],**v['units']}.items():
        require(sha(trusted(n).read_bytes())==pin,'BASE_CHANGED')
    require(sha(trusted(ROOT/'docs/ITEM4_AUTHOR5_RECOVERY_APPROVAL_20261008.txt').read_bytes())==AUTHORITY,'AUTHORITY')
    return v

def load():
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/'tools/item4_submission_recovery_component.py','OWNER_PATH')
    v=verified()
    legacy=module('_submission_recovery_prior',trusted(LEGACY));legacy.load()
    import orchestrator
    for name in ('author_format_submission','author_submission_recovery'):
        setattr(orchestrator,name,module('orchestrator.'+name,ROOT/'orchestrator'/(name+'.py')))
    from orchestrator import author_submission_recovery as recovery
    require(recovery.binding()['authority_sha256']==AUTHORITY,'AUTHORITY_BINDING')
    return v,recovery

def check(driver,recovery):
    from orchestrator import private_records as pr
    b=recovery.binding()
    require(str(driver.state.resolve())==str(LANE) and driver.config['run_id']==RUN and
        sha(pr.check(LANE/'lane.json').read_bytes())==b['config_sha256'],'EXACT_LANE')
    recovery.local_rows([dict(r) for r in driver.store.db.execute('SELECT * FROM manual_calls')])
    for ident,pin in b['global_rows'].items():
        prior=driver.store.batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(ident,)).fetchone()
        require(prior is not None and sha(canonical(dict(prior)))==pin,'ORIGINAL_GLOBAL_CHARGE_CHANGED')
    row=driver.store.batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(recovery.CALL,)).fetchone()
    require(row is not None,'ORIGINAL_GLOBAL_MISSING')
    return recovery.outputs(WORK,dict(row))

def apply():
    v,recovery=load()
    from orchestrator import private_records as pr
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.experiment_context import accept_author
    from orchestrator.manual_executor import lock
    driver=ExperimentDriver(LANE)
    try:
        with lock(LANE/'driver.lock'):
            driver.guard(); evidence=check(driver,recovery); b=recovery.binding()
            require(not DEST.exists() and not DEST.is_symlink(),'EXISTS_RECONCILE')
            raw=driver.store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
            require(sha(raw.encode())==b['state_sha256'],'EXACT_BLOCK_CHANGED')
            value=json.loads(raw)
            require(value['phase']=='BLOCKED' and value['reason']=='MODEL_FAILED_OR_UNCERTAIN_NO_RETRY' and
                value['pending']=={'id':recovery.CALL,'stage':'run_spec_author','round':5,'workspace':str(WORK)} and
                value['rounds']=={'run_spec_author':4},'EXACT_AUTHOR5_BLOCK')
            require(not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'MODEL_RUNNING')
            calls=[dict(x) for x in driver.store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
            global_before=dict(driver.store.batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(recovery.CALL,)).fetchone())
            pr.mkdir(DEST)
            qualification={**evidence,'schema':'operator-approved-preserved-author5/v1','review_sha256':v['review_sha256'],
                'source':v['source'],'meaning':'Format qualification only; original native MCP refusal remains; scientific review required.'}
            with pr.open_file(DEST/'qualification.json','xb') as f:f.write(canonical(qualification))
            backup=pr.Connection(DEST/'before.sqlite');driver.store.db.backup(backup);backup.close()
            next_value=copy.deepcopy(value);next_value['rounds']['run_spec_author']=5
            # Original full host validation, notebook preparation and synthetic tests.
            # No replacement receipt or COMPLETE relabelling for the original call.
            accept_author(driver,next_value,next_value['pending'])
            require(next_value['phase']==REVIEW_STAGE,'NORMAL_SCIENTIFIC_REVIEW_REQUIRED')
            next_value['reason']=None;next_value.pop('pending');next_value.pop('blocked_stage',None)
            next_value['interventions'].append({'kind':'OPERATOR_APPROVED_PRESERVED_AUTHOR5',
                'authority_sha256':AUTHORITY,'qualification_sha256':sha(canonical(qualification)),'review_sha256':v['review_sha256']})
            check(driver,recovery)
            driver.store.db.execute('BEGIN IMMEDIATE')
            try:
                require(driver.store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'STATE_CHANGED')
                require([dict(x) for x in driver.store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]==calls,'CHARGE_CHANGED')
                driver.store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(next_value),))
                driver.store.db.execute('COMMIT')
            except BaseException:driver.store.db.execute('ROLLBACK');raise
            require(dict(driver.store.batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(recovery.CALL,)).fetchone())==global_before,'GLOBAL_CHARGE_CHANGED')
            with pr.open_file(DEST/'applied.json','xb') as f:f.write(canonical({'status':'READY_FOR_NORMAL_SCIENTIFIC_REVIEW',
                'qualification_sha256':sha(canonical(qualification)),'review_sha256':v['review_sha256'],'model_calls':0}))
            return {'status':'READY_FOR_NORMAL_SCIENTIFIC_REVIEW','model_calls':0,'originals_preserved':True}
    finally:driver.store.db.close();driver.store.batch.db.close()

def grant(driver,v,recovery):
    from orchestrator import private_records as pr
    evidence=check(driver,recovery)
    raw=pr.check(DEST/'qualification.json').read_bytes();q=json.loads(raw)
    applied=json.loads(pr.check(DEST/'applied.json').read_bytes())
    require(q=={**evidence,'schema':'operator-approved-preserved-author5/v1','review_sha256':v['review_sha256'],
        'source':v['source'],'meaning':'Format qualification only; original native MCP refusal remains; scientific review required.'} and
        applied['qualification_sha256']==sha(raw) and applied['review_sha256']==v['review_sha256'],'QUALIFICATION_CHANGED')
    return q

def run():
    v,recovery=load()
    require(json.loads(trusted(RECORD/'APPLIED.json').read_bytes())['status']=='INSTALLED_HELD','INSTALL_INCOMPLETE')
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator import manual_recovery as mr, stocktake_review_recovery as sr
    driver=ExperimentDriver(LANE)
    old_permit,old_admission=mr.permit,sr.admission
    review_id=sha((RUN+':run_spec_review:1').encode())
    def permit(store,run):
        prior=old_permit(store,run)
        if run!=RUN:return prior
        require(store is driver.store and prior is not None,'EXACT_LOCAL_ADMISSION')
        grant(driver,v,recovery)
        return {**prior,'preserved_failures':[prior['failed_id'],recovery.CALL]}
    def admission(batch,run,stage,ident,source,receipt):
        if run!=RUN:return old_admission(batch,run,stage,ident,source,receipt)
        require(batch is driver.store.batch and stage==REVIEW_STAGE and ident==review_id and
            source==recovery.binding()['source'],'ONE_NORMAL_REVIEW_ONLY')
        grant(driver,v,recovery)
        require(batch.db.execute('SELECT count(*) FROM autonomy_calls WHERE change_id=?',(RUN,)).fetchone()[0]==5,'REVIEW_ALREADY_ADMITTED')
        prior=old_permit(driver.store,RUN)
        require(prior is not None,'PRIOR_TIMEOUT_QUALIFICATION_REQUIRED')
        return [prior['failed_id'],recovery.CALL]
    try:
        driver.guard();grant(driver,v,recovery)
        value=driver.current()
        require(value['phase'] in {REVIEW_STAGE,'MODEL_RUNNING'} and
            (not value.get('pending') or value['pending']['id']==review_id),'ONE_NORMAL_REVIEW_ONLY')
        require(not driver.store.db.execute("SELECT 1 FROM manual_calls WHERE stage='run_spec_author' AND attempt>5").fetchone(),'NO_SIXTH_AUTHOR')
        mr.permit,sr.admission=permit,admission
        return driver.advance()
    finally:
        mr.permit,sr.admission=old_permit,old_admission
        driver.store.db.close();driver.store.batch.db.close()

if __name__=='__main__':
    os.umask(0o077)
    if sys.argv[1:]==['verify']:v,_=load();print(json.dumps({'status':'VERIFIED_HELD','source':v['source'],'model_calls':0}))
    elif sys.argv[1:]==['apply']:print(json.dumps(apply(),sort_keys=True))
    elif sys.argv[1:]==['run']:print(json.dumps(run(),sort_keys=True))
    else:raise SystemExit('FIXED_RECOVERY_ACTION_REQUIRED')
