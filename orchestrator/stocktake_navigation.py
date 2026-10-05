"""One held, same-run continuation after the operator's navigation review.

No new allowance, call, retry, scientific judgment or old-record mutation.
The frozen three-row checkpoint is copied and an explicit continuation appended.
"""
import json
import os
from pathlib import Path
import sqlite3
from orchestrator import private_records, stocktake_recovery as rec
from orchestrator.manual_executor import read, digest, atomic, lock
from tools import deploy_manual_lane as deploy

EVENT=rec.RUN+':readable-navigation'
KEY=rec.FAILED+':readable-navigation'
SOURCE='dcc161e26d7900070bf03a4fc05c864793ae1e36'
OLD='/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-stocktake-transport-dcc161e2/lane'


def checkpoint():
    return read(Path(__file__).resolve().parents[1]/'docs/STOCKTAKE_NAVIGATION_CHECKPOINT.json')


def authority(root):
    from orchestrator.stocktake_manual_review import authority, NAVIGATION
    authority(NAVIGATION)
    for name in ('STOCKTAKE_NAVIGATION_DECISION.md','STOCKTAKE_NAVIGATION_APPROVAL.txt',
                 'STOCKTAKE_NAVIGATION_RECONCILIATION.md','STOCKTAKE_NAVIGATION_CHECKPOINT.json'):
        if (Path(root)/'docs'/name).read_bytes()!=(Path(__file__).resolve().parents[1]/'docs'/name).read_bytes():
            raise ValueError('NAVIGATION_AUTHORITY_CHANGED')


def unchanged_rows(db,table,pins):
    for ident,pin in pins.items():
        row=db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone()
        if row is None or rec.sha(dict(row))!=pin:raise ValueError('NAVIGATION_PRIOR_CALL_CHANGED')


def prior(state,filesystem_root, *, exact=True):
    state=Path(state);host=Path(filesystem_root);pin=checkpoint()
    if state.resolve()!=deploy.bound(host,OLD).resolve() or state.is_symlink() or (state/'HALT').exists():
        raise ValueError('NAVIGATION_NAMED_PREDECESSOR_REQUIRED')
    c=read(state/'lane.json')
    if rec.sha(c)!=pin['config_sha256']:raise ValueError('NAVIGATION_CONFIG_CHANGED')
    if digest((state/'preparation-plan.json').read_bytes())!=rec.PLAN:raise ValueError('NAVIGATION_PLAN_CHANGED')
    if read(deploy.bound(host,c['owner_path']))!=c['owner_binding']:raise ValueError('NAVIGATION_OWNER_CHANGED')
    with rec.connect(state/'jobs.sqlite') as db:
        unchanged_rows(db,'manual_calls',pin['local_calls'])
        if len(rec.rows(db,'manual_calls'))!=3 or rec.sha(rec.rows(db,'manual_account'))!=pin['account_sha256']:
            raise ValueError('NAVIGATION_ALLOWANCE_CHANGED')
        if rec.sha(rec.rows(db,'manual_state'))!=pin['state_sha256']:raise ValueError('NAVIGATION_PHASE_CHANGED')
        parent=json.loads(db.execute('SELECT binding FROM manual_recoveries WHERE failed_id=?',(rec.FAILED,)).fetchone()[0])
        if rec.sha(parent)!=pin['parent_sha256']:raise ValueError('NAVIGATION_PARENT_CHANGED')
    ledger=deploy.bound(host,c['batch_ledger'])
    with rec.connect(ledger/'jobs.sqlite') as db:
        unchanged_rows(db,'autonomy_calls',pin['global_calls'])
        row=db.execute('SELECT payload FROM events WHERE id=?',(rec.EVENT,)).fetchone()
        if row is None or row[0]!=rec.encoded(parent):raise ValueError('NAVIGATION_PARENT_EVENT_CHANGED')
        if exact and db.execute("SELECT 1 FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN') AND id!=?",(rec.FAILED,)).fetchone():
            raise ValueError('NAVIGATION_OTHER_PENDING_CALL')
        if exact and db.execute('SELECT 1 FROM events WHERE id=?',(EVENT,)).fetchone():raise ValueError('NAVIGATION_ALREADY_APPLIED')
    # Original proofs remain byte-bound after selection changes; they cannot be
    # recomputed or presented as proof of the successor. New matrix is separate.
    matrix=deploy.bound(host,parent['dry_run_path'])
    if digest(matrix.read_bytes())!=parent['dry_run_sha256']:raise ValueError('NAVIGATION_PARENT_MATRIX_CHANGED')
    for item in read(matrix)['connections']:
        if digest(deploy.bound(host,item['proof_path']).read_bytes())!=item['proof_sha256']:
            raise ValueError('NAVIGATION_PARENT_PROOF_CHANGED')
    for path,sha in ((parent['review_path'],parent['review_sha256']),):
        if digest(deploy.bound(host,path).read_bytes())!=sha:raise ValueError('NAVIGATION_PARENT_REVIEW_CHANGED')
    if exact and rec.state_snapshot(state)!=pin['snapshot']:raise ValueError('NAVIGATION_OLD_SNAPSHOT_CHANGED')
    return c,parent


def qualified(review,source,host):
    from orchestrator import stocktake_manual_review as manual
    value=manual.verify(Path(review).parent,filesystem_root=host)
    if (value['verdict']!='APPROVE' or value['source_sha']!=source or value['runtime_sha256']!=rec.RUNTIME
        or value['operator_approval_sha256']!=manual.NAV_APPROVAL or value['round']!=1
        or value['analysis_entrypoint']!='orchestrator.analysis_driver'):
        raise ValueError('NAVIGATION_INDEPENDENT_APPROVAL_REQUIRED')
    return value


def promotion_check(host,previous,source,entrypoint,review):
    from orchestrator.manual_driver import git
    authority(source)
    if entrypoint!='analysis' or previous['source']!=SOURCE or previous['state']+'/lane'!=OLD:
        raise ValueError('NAVIGATION_PROMOTION_SCOPE')
    if digest((Path(source)/'deploy/manual-lane/runtime.promotion.json').read_bytes())!=rec.RUNTIME:
        raise ValueError('NAVIGATION_RUNTIME_CHANGED')
    qualified(review,git(source,'rev-parse','HEAD'),host)
    prior(deploy.bound(host,OLD),host)
    # Exactly the two retained nonterminal predecessors, never arbitrary lanes.
    return [deploy.bound(host,rec.OLD_STATE),deploy.bound(host,OLD)]


def validate(value):
    host=Path(value.get('filesystem_root','/'));root=Path(value['root']);authority(root)
    if value.get('navigation_parent_sha256')!=checkpoint()['parent_sha256']:
        raise ValueError('NAVIGATION_PARENT_CHANGED')
    if (value.get('run_id'),value.get('stage'),value.get('failed_id'),value.get('failed_sha256'),value.get('decision_sha256'))!=(rec.RUN,rec.STAGE,rec.FAILED,rec.LOCAL_ROW,rec.DECISION):
        raise ValueError('NAVIGATION_RUN_BINDING')
    prior(deploy.bound(host,OLD),host,exact=False)
    result=qualified(value['review_path'],value['runtime_source'],host)
    if result['report_sha256']!=value['review_sha256']:raise ValueError('NAVIGATION_REVIEW_CHANGED')
    if digest(Path(value['dry_run_path']).read_bytes())!=value['dry_run_sha256']:raise ValueError('NAVIGATION_MATRIX_CHANGED')
    rec.validate_matrix(read(value['dry_run_path']),root,filesystem_root=host)
    selected=rec.installed_selection(root,host)
    if (selected['source']!=value['runtime_source'] or Path(value['state']).resolve()!=deploy.bound(host,selected['state'])/'lane'):
        raise ValueError('NAVIGATION_SELECTED_STATE_REQUIRED')
    return value


@private_records.private_umask
def continue_run(state,root,review,matrix_path, *, filesystem_root=Path('/')):
    from orchestrator.manual_driver import git,write_once
    from orchestrator.analysis_driver import release_identities
    from orchestrator.stocktake_manual_review import evidence_preconditions
    from tools import manual_promotion
    host=Path(filesystem_root).resolve();state,root,review,matrix_path=map(Path,(state,root,review,matrix_path))
    if host==Path('/') and os.getuid()!=1003:raise ValueError('NAVIGATION_SERVICE_OWNER_REQUIRED')
    for p in (state,root,review,matrix_path):
        if not p.resolve().is_relative_to(host):raise ValueError('NAVIGATION_PATH_ESCAPE')
    if state.exists() or state.is_symlink():raise ValueError('NAVIGATION_EXISTING_DESTINATION_RECONCILE')
    with lock(state.parent/'navigation-continuation.lock'):
        old=deploy.bound(host,OLD);before,parent=prior(old,host);authority(root)
        if git(root,'status','--porcelain'):raise ValueError('NAVIGATION_CLEAN_SOURCE_REQUIRED')
        head=git(root,'rev-parse','HEAD');branch=git(root,'branch','--show-current')
        if not branch.startswith('astra/manual-server-'):raise ValueError('NAVIGATION_SERVER_BRANCH_REQUIRED')
        selected=read(deploy.bound(host,manual_promotion.POINTER))
        if (selected['source']!=head or root.resolve()!=deploy.bound(host,selected['state'])/'repository'
            or state.resolve()!=deploy.bound(host,selected['state'])/'lane'
            or digest(Path(os.environ['RESEARCH_MANUAL_RUNTIME_CONFIG']).read_bytes())!=rec.RUNTIME):
            raise ValueError('NAVIGATION_HELD_INSTALL_REQUIRED')
        for unit in selected['units']+manual_promotion.layout(Path(OLD).parent.name)['units']:
            if deploy.system(host,'state',unit)!={'enabled':False,'active':False}:raise ValueError('NAVIGATION_UNITS_MUST_BE_HELD')
        access=evidence_preconditions(review.parent,filesystem_root=host)
        config={**before,'owner_path':str(deploy.bound(host,before['owner_path'])),'root':str(root.resolve()),
            'context':str(state/'context'),'branch':branch,'source':head,
            'workspace_root':str(state.parent/'lane-scientific-workspaces'),
            'engine_review':{'path':str(review.resolve()),'sha256':digest(review.read_bytes())},
            'execution_recovery':{**before['execution_recovery'],'runtime_source':head,'filesystem_root':str(host)}}
        config['profile_files'],config['engine_files']=release_identities(root)
        if config['profile_files']!=before['profile_files']:raise ValueError('NAVIGATION_PROFILE_CHANGED')
        binding={**parent,'filesystem_root':str(host),'root':str(root.resolve()),'state':str(state.resolve()),
            'runtime_source':head,'review_path':str(review.resolve()),'review_sha256':digest(review.read_bytes()),
            'config_sha256':rec.sha(config),'dry_run_path':str(matrix_path.resolve()),'dry_run_sha256':digest(matrix_path.read_bytes()),
            'navigation_parent_sha256':checkpoint()['parent_sha256'],'evidence_preconditions':access}
        validate(binding)
        intent=state.parent/'navigation-continuation-intent.json'
        if intent.exists():raise ValueError('NAVIGATION_PARTIAL_RECONCILE_NO_RETRY')
        write_once(intent,(rec.encoded(binding)+'\n').encode())
        private_records.mkdir(state)
        for p in old.iterdir():
            if p.name in {'jobs.sqlite','jobs.sqlite-wal','jobs.sqlite-shm','lane.json'}:continue
            if p.is_dir():private_records.copytree(p,state/p.name)
            else:private_records.copyfile(p,state/p.name)
        with rec.connect(old/'jobs.sqlite') as src,sqlite3.connect(state/'jobs.sqlite') as dst:src.backup(dst)
        atomic(state/'lane.json',config)
        # Carry forward the phase, all rows, receipts and original recovery.
        # No changes to manual_account, manual_calls, owner, or manual_state.
        with sqlite3.connect('file:'+str(state/'jobs.sqlite')+'?mode=rw',uri=True) as db:
            db.execute('INSERT INTO manual_recoveries VALUES(?,?)',(KEY,rec.encoded(binding)))
        ledger=deploy.bound(host,before['batch_ledger'])
        with sqlite3.connect('file:'+str(ledger/'jobs.sqlite')+'?mode=rw',uri=True) as db:
            db.row_factory=sqlite3.Row;db.execute('BEGIN IMMEDIATE')
            if (ledger/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
            unchanged_rows(db,'autonomy_calls',checkpoint()['global_calls'])
            if db.execute("SELECT 1 FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN') AND id!=?",(rec.FAILED,)).fetchone():raise ValueError('NAVIGATION_OTHER_PENDING_CALL')
            db.execute('INSERT INTO events VALUES(?,?,?)',(EVENT,rec.RUN,rec.encoded(binding)))
        private_records.check_tree(state)
        if rec.state_snapshot(old)!=checkpoint()['snapshot']:raise ValueError('NAVIGATION_OLD_STATE_CHANGED')
        return {'status':'CONTINUED_NO_MODEL_CALL','calls_used':3,'call_limit':8,'phase':'COMMIT_SPEC','source':head,
            'path':'Carry scope approval; next interpretation must audit every numeric claim via corrected navigation.'}


def main():
    import argparse
    p=argparse.ArgumentParser()
    for n in ('state','root','review','matrix'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--filesystem-root',type=Path,default=Path('/'))
    a=p.parse_args();print(json.dumps(continue_run(a.state,a.root,a.review,a.matrix,filesystem_root=a.filesystem_root),indent=2))

if __name__=='__main__':main()
