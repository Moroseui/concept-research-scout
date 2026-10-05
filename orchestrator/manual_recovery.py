"""One named operator recovery; original failure, charge and science remain bound.

Preparation/application is local and deterministic, never a model launch. Engine
review must approve this exact successor before application to the saved lane.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

RUN = "sprint10-stepd-a9123b81e3ef32ee"
STAGE = "result_interpretation_author"
FAILED = "fc3802218969bdb52ba5f40d6a59b122fc14e1c9edce19adb45e70bf42976ecc"
FAILED_SHA = "55423230b04034ddf196487aea5cf21452d5470eb4ec9ad153de4135b12df73d"
DECISION_SHA = "d7e1b0aac6a9749f949af9e7fe31f42dde17a10827748a97adf14f4cabb3cf72"
BASE = "3a2d5c33fe2a8bd4613b34ae4643324f5320bda4"
DECISION_PATH = "docs/STEP_D_LINKED_RECOVERY_DECISION.txt"


def digest(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return json.dumps(value,sort_keys=True)
def git(root,*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()


def failed_binding(store):
    row=store.db.execute('SELECT * FROM manual_calls WHERE id=?',(FAILED,)).fetchone()
    if row is None or row['status']!='UNCERTAIN' or digest(encoded(dict(row)).encode())!=FAILED_SHA:
        raise ValueError('RECOVERY_ORIGINAL_FAILURE_CHANGED')
    return dict(row)


def permit(store,run):
    from orchestrator import stocktake_recovery
    if run==stocktake_recovery.RUN:return stocktake_recovery.permit(store,run)
    row=store.db.execute('SELECT binding FROM manual_recoveries WHERE failed_id=?',(FAILED,)).fetchone()
    if row is None:return None
    value=json.loads(row[0])
    if value['run_id']!=RUN or value['failed_id']!=FAILED or value['failed_sha256']!=FAILED_SHA or value['decision_sha256']!=DECISION_SHA:
        raise ValueError('RECOVERY_GRANT_BINDING')
    failed_binding(store)
    return value if run==RUN else None


def role_limit(store,run,stage):
    from orchestrator.analysis_revisions import enabled
    if enabled(store,run):return 4
    value=permit(store,run)
    if value is not None and 'review_checkpoint' in value:return 2
    return 3 if value is not None and stage==value.get('stage',STAGE) else 2


def validate_runtime(driver):
    if driver.config.get('execution_recovery',{}).get('kind')=='stocktake-transport':
        from orchestrator.stocktake_recovery import validate_runtime as validate_stocktake
        return validate_stocktake(driver)
    value=permit(driver.store,driver.config['run_id'])
    if value is None or digest(encoded(driver.config).encode())!=value['config_sha256']:
        raise ValueError('RECOVERY_RUNTIME_CONFIG_BINDING')
    if driver.root.resolve()!=Path(__file__).resolve().parents[1]:
        raise ValueError('REVIEWED_RECOVERY_RUNTIME_REQUIRED')
    if digest((driver.root/DECISION_PATH).read_bytes())!=DECISION_SHA:
        raise ValueError('RECOVERY_AUTHORITY_CHANGED')
    if digest(Path(value['review_path']).read_bytes())!=value['review_sha256']:
        raise ValueError('RECOVERY_REVIEW_CHANGED')


def apply(state,root,review):
    from orchestrator.manual_driver import Driver,write_once
    from orchestrator.manual_executor import atomic,lock,read
    state,root,review=map(Path,(state,root,review))
    with lock(state/'driver.lock'):
        if (state/'HALT').exists():raise ValueError('OPERATOR_HALT')
        if root.resolve()!=Path(__file__).resolve().parents[1]:raise ValueError('REVIEWED_RECOVERY_RUNTIME_REQUIRED')
        if git(root,'status','--porcelain'):raise ValueError('CLEAN_REVIEWED_SOURCE_REQUIRED')
        head=git(root,'rev-parse','HEAD');branch=git(root,'branch','--show-current')
        report=review.read_text()
        if head not in report or re.findall(r'^## Verdict: (.+?)\s*$',report,re.M)!=['APPROVE']:
            raise ValueError('EXACT_ENGINE_REVIEW_REQUIRED')
        if not branch.startswith('astra/manual-'):raise ValueError('MANUAL_BRANCH_REQUIRED')
        if digest((root/DECISION_PATH).read_bytes())!=DECISION_SHA:raise ValueError('EXACT_RECOVERY_DECISION_REQUIRED')
        driver=Driver(state);failed_binding(driver.store)
        if driver.config['run_id']!=RUN or driver.config['source']!=BASE:raise ValueError('RECOVERY_RUN_SOURCE_SCOPE')
        plan_path=state/'linked-recovery-plan.json'
        if plan_path.exists():
            plan=read(plan_path)
            if plan['permit']['runtime_source']!=head or plan['permit']['review_sha256']!=digest(review.read_bytes()):
                raise ValueError('RECOVERY_PLAN_CHANGED')
        else:
            driver.guard();value=driver.current()
            if value['phase']!='BLOCKED' or value.get('reason')!='MODEL_FAILED_OR_UNCERTAIN_NO_RETRY' or value.get('pending',{}).get('id')!=FAILED:
                raise ValueError('RECOVERY_EXACT_BLOCK_REQUIRED')
            calls=driver.store.db.execute('SELECT * FROM manual_calls').fetchall()
            if len(calls)!=3 or any(r['status']!='COMPLETE' for r in calls if r['id']!=FAILED):raise ValueError('RECOVERY_INITIAL_CALL_SET')
            # The successor may change the engine only; accepted science/context
            # and old authority stay identical. Both source identities survive.
            for name,expected in {**driver.config['profile_files'],**driver.config['scientific_files']}.items():
                if digest((root/name).read_bytes())!=expected:raise ValueError('RECOVERY_SCIENCE_OR_CONTEXT_CHANGED')
            if digest((root/'docs/STEP_D_AUTHORIZATION.md').read_bytes())!=driver.config['authority_sha256']:
                raise ValueError('RECOVERY_PRIOR_AUTHORITY_CHANGED')
            config={**driver.config,'root':str(root.resolve()),'branch':branch,'execution_recovery':{'runtime_source':head,'failed_id':FAILED,'decision_sha256':DECISION_SHA}}
            config['engine_files']={str(p.relative_to(root)):digest(p.read_bytes()) for p in (root/'orchestrator').glob('*.py')}
            config['engine_files']['scout.py']=digest((root/'scout.py').read_bytes())
            binding={'run_id':RUN,'failed_id':FAILED,'failed_sha256':FAILED_SHA,'decision_sha256':DECISION_SHA,'runtime_source':head,'review_path':str(review.resolve()),'review_sha256':digest(review.read_bytes()),'config_sha256':digest(encoded(config).encode())}
            plan={'before_config':driver.config,'after_config':config,'before_state':value,'permit':binding}
            write_once(plan_path,(encoded(plan)+'\n').encode())
        before,after=plan['before_config'],plan['after_config']
        if digest(encoded(after).encode())!=plan['permit']['config_sha256'] or after['root']!=str(root.resolve()) or after['source']!=BASE:
            raise ValueError('RECOVERY_PLAN_CONFIG_BINDING')
        if driver.config not in [before,after]:raise ValueError('RECOVERY_CONFIG_DRIFT')
        binding=plan['permit']
        old=permit(driver.store,RUN)
        if old is not None:
            if old!=binding or driver.config!=after:raise ValueError('RECOVERY_APPLICATION_DRIFT')
            return {'status':'ALREADY_APPLIED','run_id':RUN,'failed_id':FAILED,'phase':driver.current()['phase']}
        if driver.current()!=plan['before_state']:raise ValueError('RECOVERY_STATE_DRIFT')
        # An interruption between config and transaction is still BLOCKED with
        # no permit. Reapplying this same immutable plan is the only recovery.
        atomic(state/'lane.json',after,mode=0o600)
        resumed={**plan['before_state'],'phase':STAGE,'reason':None,'linked_recovery_of':FAILED}
        resumed.pop('pending',None)
        driver.store.db.execute('BEGIN IMMEDIATE')
        try:
            failed_binding(driver.store)
            if driver.current()!=plan['before_state']:raise ValueError('RECOVERY_STATE_DRIFT')
            driver.store.db.execute('INSERT INTO manual_recoveries VALUES(?,?)',(FAILED,encoded(binding)))
            driver.store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(resumed),))
            driver.store.db.execute('COMMIT')
        except BaseException:
            driver.store.db.execute('ROLLBACK');raise
        return {'status':'APPLIED_NO_MODEL_CALL','run_id':RUN,'failed_id':FAILED,'next':STAGE,'runtime_source':head,'scientific_source':BASE}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--state',type=Path,required=True);parser.add_argument('--root',type=Path,required=True);parser.add_argument('--engine-review',type=Path,required=True);args=parser.parse_args()
    print(json.dumps(apply(args.state,args.root,args.engine_review),indent=2))

if __name__=='__main__':main()
