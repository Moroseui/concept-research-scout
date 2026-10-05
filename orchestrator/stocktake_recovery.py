"""Exactly one operator-bound stock-take transport recovery, not a retry API.

Old state, owner and both charged UNCERTAIN rows remain unchanged. A new held
release gets a private copy of the same allowance and an append-only binding in
the existing ledger. No initialization, refund or additional run is performed.
"""
import json
import os
from pathlib import Path
import sqlite3
import time

from orchestrator import private_records
from orchestrator.manual_executor import digest, read, atomic, inventory, lock

RUN='stocktake-c9deb31c7f8668b41df09ea8'
STAGE='run_spec_author'
FAILED='2019f1b1b0c9439743811b6bfa7801fd1ed13c6ad9120e0ebfa5b52e0ed145b1'
BASE='6b63211a42ec362f4efa522eaa76c358fbfedd13'
DECISION='0c271019a9a31e70b0f68676d6a261ebec452be5fef65fd17567d46c9c5d4595'
APPROVAL='6b11eb6e2d139b51031a6b38b31899c2427abec0a8f7889cb239426183c68bf1'
LOCAL_ROW='15201af6f2df72872dc0ecd77583808d3f2624a97fe21cc97d37d2c60656fc6f'
GLOBAL_ROW='6601fe419d6855b93661067d2bf6f0b65671e51b8dcd534d767d23469f223bfb'
CONFIG='7f2c7c15a6daae8e06629a5cc22d66cc4463026d0f230154cd682eb91b1096ad'
ACCOUNT='a94659004e2451d66e8f72d924bd40ea98bae7f36f68610f3d3259678e12d179'
STATE='99a96d45d08b406ea771ce8e649d6b5ae95a0d003b19a3bd2ddc6850ff153317'
OWNER='108cf7151992821f7df93c52cc38c3c2c67e578609cbdee7d482595c2b0fc1d2'
RUNTIME='dbd849b9267ece5ff231ca7d45710d1bdb24e9294caa8f2e0d694e7394dd595d'
PLAN='33224bc10a98f01323838b334f6841b451c3b5bf87836ed4564b79b510b3514c'
PROMPT='1aa26a7ec29d79c7b1b25d667153206da6c2494642d61b009dc45c9c741c86eb'
OLD_STATE='/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-autonomy-stocktake-binding-20261004/lane'
EVENT=RUN+':one-transport-recovery'


def encoded(v):return json.dumps(v,sort_keys=True)
def sha(v):return digest(encoded(v).encode())
def rows(db,table):return [dict(x) for x in db.execute('SELECT * FROM '+table)]
def connect(path):
    db=sqlite3.connect('file:'+str(Path(path).resolve())+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    return db


def authority(root):
    for name,expected in [('STOCKTAKE_TRANSPORT_DECISION.md',DECISION),('STOCKTAKE_TRANSPORT_APPROVAL.txt',APPROVAL)]:
        if digest((Path(root)/'docs'/name).read_bytes())!=expected:raise ValueError('STOCKTAKE_RECOVERY_AUTHORITY_CHANGED')


def original_row(db,table,expected):
    row=db.execute('SELECT * FROM '+table+' WHERE id=?',(FAILED,)).fetchone()
    if row is None or row['status']!='UNCERTAIN' or sha(dict(row))!=expected:
        raise ValueError('STOCKTAKE_ORIGINAL_FAILURE_CHANGED')
    return dict(row)


def original_state(state, *, filesystem_root=Path('/')):
    state=Path(state);expected=Path(filesystem_root)/OLD_STATE.lstrip('/')
    if state.resolve()!=expected.resolve():raise ValueError('STOCKTAKE_NAMED_STATE_REQUIRED')
    if state.is_symlink() or (state/'HALT').exists():raise ValueError('STOCKTAKE_STATE_HALTED_OR_ALIAS')
    config=read(state/'lane.json')
    if sha(config)!=CONFIG or digest((state/'preparation-plan.json').read_bytes())!=PLAN:
        raise ValueError('STOCKTAKE_ORIGINAL_CONFIG_CHANGED')
    # Scratch roots are used only by deterministic tests; live paths are exact.
    def host(p):return Path(filesystem_root)/str(p).lstrip('/')
    if read(host(config['owner_path']))!=config['owner_binding']:raise ValueError('STOCKTAKE_OWNER_CHANGED')
    with connect(state/'jobs.sqlite') as db:
        original_row(db,'manual_calls',LOCAL_ROW)
        if len(rows(db,'manual_calls'))!=1 or sha(rows(db,'manual_account'))!=ACCOUNT or sha(rows(db,'manual_state'))!=STATE:
            raise ValueError('STOCKTAKE_ORIGINAL_STATE_CHANGED')
    with connect(host(config['batch_ledger'])/'jobs.sqlite') as db:
        original_row(db,'autonomy_calls',GLOBAL_ROW)
        owner=[dict(x) for x in db.execute('SELECT * FROM autonomy_runs WHERE id=?',(RUN,))]
        if sha(owner)!=OWNER:raise ValueError('STOCKTAKE_GLOBAL_OWNER_CHANGED')
        if db.execute('SELECT 1 FROM events WHERE id=?',(EVENT,)).fetchone():raise ValueError('STOCKTAKE_RECOVERY_ALREADY_RECORDED')
        pending=[x['id'] for x in db.execute("SELECT id FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')")]
        if pending!=[FAILED]:raise ValueError('STOCKTAKE_OTHER_PENDING_CALL')
    return config


def promotion_check(filesystem_root, previous, source, entrypoint):
    authority(source)
    if entrypoint!='analysis' or previous['source']!=BASE or previous['state']+'/lane'!=OLD_STATE:
        raise ValueError('STOCKTAKE_PROMOTION_SCOPE')
    if digest((Path(source)/'deploy/manual-lane/runtime.promotion.json').read_bytes())!=RUNTIME:
        raise ValueError('STOCKTAKE_RUNTIME_CHANGED')
    state=Path(filesystem_root)/OLD_STATE.lstrip('/')
    original_state(state,filesystem_root=filesystem_root)
    return state


def validate_binding(value):
    if 'review_checkpoint' in value:
        from orchestrator.stocktake_review_recovery import validate
        return validate(value)
    if 'navigation_parent_sha256' in value:
        from orchestrator.stocktake_navigation import validate
        return validate(value)
    filesystem_root=Path(value.get('filesystem_root','/'))
    if (value.get('run_id'),value.get('failed_id'),value.get('failed_sha256'),value.get('decision_sha256'),value.get('stage'))!=(RUN,FAILED,LOCAL_ROW,DECISION,STAGE):
        raise ValueError('STOCKTAKE_RECOVERY_BINDING')
    authority(value['root'])
    if digest(Path(value['review_path']).read_bytes())!=value['review_sha256']:
        raise ValueError('STOCKTAKE_RECOVERY_REVIEW_CHANGED')
    from orchestrator.autonomy_review import verify_result
    from orchestrator import stocktake_manual_review
    folder=Path(value['review_path']).parent
    from tools.deploy_manual_lane import bound
    result=stocktake_manual_review.verify(folder,filesystem_root=filesystem_root) if folder.parent==bound(filesystem_root,str(stocktake_manual_review.ROOT)) else verify_result(folder)
    if (result['verdict'],result['source_sha'],result['runtime_sha256'],result['report_sha256'])!=('APPROVE',value['runtime_source'],RUNTIME,value['review_sha256']):
        raise ValueError('STOCKTAKE_GENUINE_APPROVAL_REQUIRED')
    if digest(Path(value['dry_run_path']).read_bytes())!=value['dry_run_sha256']:
        raise ValueError('STOCKTAKE_DRY_RUN_CHANGED')
    validate_matrix(read(value['dry_run_path']),Path(value['root']),filesystem_root=filesystem_root)
    return value


def permit(store,run):
    if run!=RUN:return None
    from orchestrator.stocktake_review_recovery import permit as review_permit
    reviewed=review_permit(store,run)
    if reviewed is not None:return reviewed
    from orchestrator.stocktake_navigation import KEY, EVENT as NAV_EVENT
    row=store.db.execute('SELECT binding FROM manual_recoveries WHERE failed_id=?',(KEY,)).fetchone()
    event=NAV_EVENT if row is not None else EVENT
    if row is None:row=store.db.execute('SELECT binding FROM manual_recoveries WHERE failed_id=?',(FAILED,)).fetchone()
    if row is None:return None
    value=validate_binding(json.loads(row[0]));original_row(store.db,'manual_calls',LOCAL_ROW)
    if Path(store.path).resolve()!=Path(value['state'])/'jobs.sqlite':raise ValueError('STOCKTAKE_LOCAL_LEDGER_BINDING')
    global_row=store.batch.db.execute('SELECT payload FROM events WHERE id=?',(event,)).fetchone() if store.batch else None
    if global_row is None or global_row[0]!=encoded(value):raise ValueError('STOCKTAKE_BOTH_LEDGER_BINDING_REQUIRED')
    return value


def global_exception(batch,run, *, completing=False):
    # Only the named run may cross its preserved failure. Other runs still
    # encounter the original UNCERTAIN guard; this does not authorize item2.
    if run!=RUN:return None
    from orchestrator.stocktake_navigation import EVENT as NAV_EVENT
    row=batch.db.execute('SELECT payload FROM events WHERE id=?',(NAV_EVENT,)).fetchone()
    if row is None:row=batch.db.execute('SELECT payload FROM events WHERE id=?',(EVENT,)).fetchone()
    if row is None:return None
    value=validate_binding(json.loads(row[0]));original_row(batch.db,'autonomy_calls',GLOBAL_ROW)
    from tools.deploy_manual_lane import bound
    expected=bound(value.get('filesystem_root','/'),'/var/lib/research-system-autonomy/reviews')
    if batch.folder.resolve()!=expected:raise ValueError('STOCKTAKE_GLOBAL_LEDGER_BINDING')
    if completing:
        replacement=digest((RUN+':'+STAGE+':2').encode())
        result=batch.db.execute('SELECT status FROM autonomy_calls WHERE id=?',(replacement,)).fetchone()
        if result is None or result[0]!='COMPLETE':raise ValueError('STOCKTAKE_REPLACEMENT_NOT_COMPLETE')
    return FAILED


def validate_runtime(driver):
    value=permit(driver.store,driver.config['run_id'])
    if value is None or sha(driver.config)!=value['config_sha256'] or str(driver.root.resolve())!=value['root']:
        raise ValueError('STOCKTAKE_RUNTIME_BINDING')
    if driver.state.resolve()!=Path(value['state']).resolve():raise ValueError('STOCKTAKE_RECOVERY_DESTINATION')


def installed_selection(root,filesystem_root=Path('/')):
    from tools import deploy_manual_lane as deploy,manual_promotion
    filesystem_root=Path(filesystem_root).resolve();root=Path(root).resolve()
    pointer=deploy.bound(filesystem_root,manual_promotion.POINTER);selected=read(pointer)
    record=str(Path(selected['hash_list']).parent)
    installed=manual_promotion.manifest_check(filesystem_root,record)
    receipt=deploy.bound(filesystem_root,record+'/installed.json')
    if (installed['source']!=selected['source'] or installed.get('entrypoint')!='analysis'
        or selected['runtime_sha256']!=RUNTIME or digest(deploy.bound(filesystem_root,selected['runtime']).read_bytes())!=RUNTIME
        or digest(deploy.bound(filesystem_root,selected['hash_list']).read_bytes())!=selected['hash_list_sha256']
        or root not in {deploy.bound(filesystem_root,selected['release']),deploy.bound(filesystem_root,selected['state'])/'repository'}):
        raise ValueError('STOCKTAKE_SELECTED_RELEASE_REQUIRED')
    return {'source':selected['source'],'release':selected['release'],'state':selected['state'],
        'selected_sha256':digest(pointer.read_bytes()),'installed_sha256':digest(receipt.read_bytes()),
        'installed_path':record+'/installed.json','installed_mtime_ns':receipt.stat().st_mtime_ns,
        'filesystem_root':str(filesystem_root)}


def validate_matrix(matrix,root, *, filesystem_root=Path('/')):
    expected={(s,n) for s in ('run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review') for n in (1,2)}|{('run_spec_author',3)}
    if matrix.get('schema')!='stocktake-transport-matrix/v2' or matrix.get('runtime_sha256')!=RUNTIME:
        raise ValueError('STOCKTAKE_MATRIX_BINDING')
    selection=installed_selection(root,filesystem_root)
    if (matrix.get('installation')!=selection or type(matrix.get('recorded_at')) not in (int,float)
        or not selection['installed_mtime_ns']/1e9<=matrix['recorded_at']<=time.time()+5):
        raise ValueError('STOCKTAKE_MATRIX_AFTER_SELECTED_INSTALL_REQUIRED')
    proof=matrix.get('connections',[])
    if len(proof)!=len(expected) or {(x['stage'],x['round']) for x in proof}!=expected:
        raise ValueError('STOCKTAKE_ALL_CONNECTIONS_REQUIRED')
    for item in proof:
        record=read(Path(item['proof_path']))
        if digest(Path(item['proof_path']).read_bytes())!=item['proof_sha256'] or record!=item['proof']:
            raise ValueError('STOCKTAKE_TRANSPORT_PROOF_CHANGED')
        if (record['status']!='PASS' or record['input_sha256']!=PROMPT or record['model_client_launched'] is not False or record.get('isolated_stdin') is not True
            or record['stage']!=item['stage'] or record['family']!=('claude' if item['stage'].endswith('review') else 'codex')
            or record['producer_sha256']!=digest((root/'scout.py').read_bytes())
            or record['transport_sha256']!=digest((root/'orchestrator/manual_stage.py').read_bytes())):
            raise ValueError('STOCKTAKE_INSTALLED_TRANSPORT_REQUIRED')


def state_snapshot(state):
    from tools.deploy_manual_lane import database_rows
    files=inventory(state)
    for name in ('jobs.sqlite','jobs.sqlite-wal','jobs.sqlite-shm'):files.pop(name,None)
    return {'files':files,'database_rows_sha256':database_rows(Path(state)/'jobs.sqlite')}


def ledger_folder(config):
    from tools.deploy_manual_lane import bound
    recovery=config.get('execution_recovery',{})
    return bound(recovery.get('filesystem_root','/'),config['batch_ledger']) if recovery.get('kind')=='stocktake-transport' else Path(config['batch_ledger'])


@private_records.private_umask
def migrate(old_state,state,root,review,matrix_path, *, filesystem_root=Path('/')):
    from orchestrator.analysis_driver import release_identities
    from orchestrator.manual_driver import git,write_once
    from orchestrator.manual_executor import ManualExecutor
    from orchestrator.autonomy_accounting import BatchAccounts
    old_state,state,root,review,matrix_path=map(Path,(old_state,state,root,review,matrix_path))
    from tools import deploy_manual_lane as deploy
    filesystem_root=Path(filesystem_root).resolve()
    for path in (old_state,state,root,review,matrix_path):
        if not path.resolve().is_relative_to(filesystem_root):raise ValueError('STOCKTAKE_SCRATCH_PATH_ESCAPE')
    authority(root)
    if state.exists() or state.is_symlink():raise ValueError('STOCKTAKE_EXISTING_RECOVERY_RECONCILE')
    with lock(state.parent/'stocktake-migration.lock'):
        before=original_state(old_state,filesystem_root=filesystem_root)
        if git(root,'status','--porcelain'):raise ValueError('STOCKTAKE_CLEAN_RECOVERY_SOURCE_REQUIRED')
        head=git(root,'rev-parse','HEAD');branch=git(root,'branch','--show-current')
        if not branch.startswith('astra/manual-server-'):raise ValueError('STOCKTAKE_VERSIONED_SERVER_BRANCH_REQUIRED')
        runtime=Path(os.environ['RESEARCH_MANUAL_RUNTIME_CONFIG'])
        if digest(runtime.read_bytes())!=RUNTIME:raise ValueError('STOCKTAKE_RUNTIME_CHANGED')
        # The selected, installed version owns a fresh state directory. This
        # refuses a scratch checkout or an uninstalled/self-approved importer.
        selected=read(deploy.bound(filesystem_root,'/etc/research-system-manual-sprint10/selected-release.json'))
        if (selected['source']!=head or root.resolve()!=deploy.bound(filesystem_root,selected['state'])/'repository'
            or state.resolve()!=deploy.bound(filesystem_root,selected['state'])/'lane' or selected['runtime_sha256']!=RUNTIME):
            raise ValueError('STOCKTAKE_HELD_INSTALL_REQUIRED')
        from tools.manual_promotion import manifest_check
        installed=manifest_check(filesystem_root,str(Path(selected['hash_list']).parent))
        if installed['source']!=head or installed['entrypoint']!='analysis':raise ValueError('STOCKTAKE_INSTALLED_SOURCE_REQUIRED')
        for unit in selected['units']:
            if filesystem_root==Path('/'):
                import subprocess
                p=subprocess.run(['/usr/bin/systemctl','is-active',unit],capture_output=True,text=True)
                e=subprocess.run(['/usr/bin/systemctl','is-enabled',unit],capture_output=True,text=True)
                held=p.stdout.strip()=='inactive' and e.stdout.strip() in {'disabled','static'}
            else:held=deploy.system(filesystem_root,'state',unit)=={'enabled':False,'active':False}
            if not held:raise ValueError('STOCKTAKE_RECOVERY_MUST_BE_HELD')
        for name,expected in before['profile_files'].items():
            if digest((root/name).read_bytes())!=expected:raise ValueError('STOCKTAKE_CONTEXT_CHANGED')
        if digest((root/before['authority_path']).read_bytes())!=before['authority_sha256']:
            raise ValueError('STOCKTAKE_OLD_AUTHORITY_CHANGED')
        config={**before,'owner_path':str(deploy.bound(filesystem_root,before['owner_path'])),'root':str(root.resolve()),'context':str(state/'context'),'branch':branch,'source':head,
            'workspace_root':str(state.parent/'lane-scientific-workspaces'),
            'engine_review':{'path':str(review.resolve()),'sha256':digest(review.read_bytes())},
            'execution_recovery':{'kind':'stocktake-transport','runtime_source':head,'failed_id':FAILED,'decision_sha256':DECISION,'filesystem_root':str(filesystem_root)}}
        config['profile_files'],config['engine_files']=release_identities(root)
        binding={'run_id':RUN,'stage':STAGE,'failed_id':FAILED,'failed_sha256':LOCAL_ROW,'decision_sha256':DECISION,
            'runtime_source':head,'filesystem_root':str(filesystem_root),'root':str(root.resolve()),'state':str(state.resolve()),'review_path':str(review.resolve()),
            'review_sha256':digest(review.read_bytes()),'config_sha256':sha(config),
            'dry_run_path':str(matrix_path.resolve()),'dry_run_sha256':digest(matrix_path.read_bytes()),
            'original_config_sha256':CONFIG,'original_owner':before['owner_binding']}
        validate_binding(binding)
        from orchestrator.stocktake_manual_review import evidence_preconditions
        access=evidence_preconditions(review.parent,filesystem_root=filesystem_root)
        binding['evidence_preconditions']=access
        review_manifest=read(review.parent/'packet-manifest.json')
        if review_manifest['files'].get('evidence/analysis-plan.json')!=PLAN:raise ValueError('STOCKTAKE_REVIEWED_PLAN_REQUIRED')
        before_files=state_snapshot(old_state)
        # This intent makes a partial application non-repeatable. No old file is
        # rewritten. Local/global commits are deliberately fail-closed if split.
        intent=state.parent/'stocktake-recovery-intent.json'
        if intent.exists():raise ValueError('STOCKTAKE_PARTIAL_RECOVERY_RECONCILE')
        write_once(intent,(encoded(binding)+'\n').encode())
        private_records.mkdir(state)
        private_records.copytree(old_state/'context',state/'context')
        private_records.copyfile(old_state/'preparation-plan.json',state/'preparation-plan.json')
        with connect(old_state/'jobs.sqlite') as source,sqlite3.connect(state/'jobs.sqlite') as dest:source.backup(dest)
        atomic(state/'lane.json',config)
        batch=BatchAccounts(deploy.bound(filesystem_root,before['batch_ledger']));store=ManualExecutor(state/'jobs.sqlite',batch=batch)
        original_row(store.db,'manual_calls',LOCAL_ROW)
        if sha(rows(store.db,'manual_account'))!=ACCOUNT:raise ValueError('STOCKTAKE_ALLOWANCE_CHANGED')
        value=json.loads(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
        value.update(phase=STAGE,reason=None);value.pop('pending');value.pop('linked_recovery_of',None)
        write_once(state/'preserved-before.json',(encoded({'config':before,'files':before_files})+'\n').encode())
        if state_snapshot(old_state)!=before_files:raise ValueError('STOCKTAKE_OLD_STATE_CHANGED')
        batch.db.execute('BEGIN IMMEDIATE')
        try:
            original_row(batch.db,'autonomy_calls',GLOBAL_ROW)
            if (batch.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
            if batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN') AND id!=?",(FAILED,)).fetchone():raise ValueError('STOCKTAKE_OTHER_PENDING_CALL')
            batch.db.execute('INSERT INTO events VALUES(?,?,?)',(EVENT,RUN,encoded(binding)))
            batch.db.execute('COMMIT')
        except BaseException:batch.db.execute('ROLLBACK');raise
        store.db.execute('BEGIN IMMEDIATE')
        try:
            store.db.execute('INSERT INTO manual_recoveries VALUES(?,?)',(FAILED,encoded(binding)))
            store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(encoded(value),))
            store.db.execute('COMMIT')
        except BaseException:store.db.execute('ROLLBACK');raise
        private_records.check_tree(state)
        if state_snapshot(old_state)!=before_files:raise ValueError('STOCKTAKE_OLD_STATE_CHANGED')
        return {'status':'APPLIED_NO_MODEL_CALL' if filesystem_root==Path('/') else 'APPLIED_SCRATCH_NO_MODEL_CALL','filesystem_root':str(filesystem_root),'evidence_preconditions':access,'run_id':RUN,'source':head,'preserved_failure':FAILED,'calls_used':1,'call_limit':8}


def validate_next_call(store,stage,n):
    value=json.loads(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
    if value.get('phase')!=stage:raise ValueError('STOCKTAKE_CURRENT_STAGE_REQUIRED')
    if stage==STAGE and n==3:
        if value.get('reason')!='REVISION_REQUIRED':raise ValueError('STOCKTAKE_ONLY_REVIEW_REQUESTED_REVISION')
        row=store.db.execute("SELECT * FROM manual_calls WHERE stage='run_spec_review' AND attempt=1 AND status='COMPLETE'").fetchone()
        if row is None:raise ValueError('STOCKTAKE_REVIEW_REQUEST_REQUIRED')
        receipt=json.loads(row['receipt']);path=Path(receipt['workspace'])/'review.json'
        if digest(path.read_bytes())!=receipt['output_sha256']['review.json'] or read(path).get('verdict')!='REVISE':
            raise ValueError('STOCKTAKE_REVIEW_REQUEST_REQUIRED')
    if stage!=STAGE or n==3:
        replacement=digest((RUN+':'+STAGE+':2').encode())
        row=store.db.execute('SELECT status FROM manual_calls WHERE id=?',(replacement,)).fetchone()
        if row is None or row[0]!='COMPLETE':raise ValueError('STOCKTAKE_REPLACEMENT_NOT_COMPLETE')


@private_records.private_umask
def dry_run_matrix(workspace,destination, *, filesystem_root=Path('/'),source_root=None):
    from orchestrator.manual_stage import transport_check
    runtime=Path(os.environ['RESEARCH_MANUAL_RUNTIME_CONFIG'])
    if digest(runtime.read_bytes())!=RUNTIME:raise ValueError('STOCKTAKE_RUNTIME_CHANGED')
    destination=Path(destination)
    if destination.exists():raise ValueError('STOCKTAKE_MATRIX_ALREADY_EXISTS')
    root=Path(source_root) if source_root else Path(__file__).resolve().parents[1]
    installation=installed_selection(root,filesystem_root)
    connections=[]
    for stage in ('run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review'):
        for round_no in range(1,4 if stage==STAGE else 3):
            proof=transport_check(workspace,stage,PROMPT)
            path=Path(proof['probe'])/'proof.json'
            connections.append({'stage':stage,'round':round_no,'proof_path':str(path),'proof_sha256':digest(path.read_bytes()),'proof':proof})
    matrix={'schema':'stocktake-transport-matrix/v2','runtime_sha256':RUNTIME,'connections':connections,
        'installation':installation,'recorded_at':time.time(),
        'input_scope':'Preserved genuine first-author payload exercises every connection; future stage inputs do not exist yet. Each actual stage/revision also passes transport_check before reservation.'}
    validate_matrix(matrix,root,filesystem_root=filesystem_root)
    atomic(destination,matrix)
    return matrix


def main():
    import argparse
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='command',required=True)
    dry=sub.add_parser('dry-run');dry.add_argument('--workspace',type=Path,required=True);dry.add_argument('--output',type=Path,required=True);dry.add_argument('--filesystem-root',type=Path,default=Path('/'));dry.add_argument('--source-root',type=Path)
    apply=sub.add_parser('migrate')
    for key in ('old-state','state','root','review','matrix'):apply.add_argument('--'+key,type=Path,required=True)
    apply.add_argument('--filesystem-root',type=Path,default=Path('/'))
    args=parser.parse_args()
    if args.command=='dry-run':result=dry_run_matrix(args.workspace,args.output,filesystem_root=args.filesystem_root,source_root=args.source_root)
    else:result=migrate(args.old_state,args.state,args.root,args.review,args.matrix,filesystem_root=args.filesystem_root)
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':main()
