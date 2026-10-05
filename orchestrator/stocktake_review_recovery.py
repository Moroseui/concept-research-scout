"""One operator-linked replacement review of the unchanged stock-take draft.

A copied same-run lane retains its owner, allowance, every call and old recovery.
Administrative terminal proofs are deliberately not scientific authority here.
"""
import json
import os
from pathlib import Path
import sqlite3
from orchestrator import private_records, stocktake_recovery as rec
from orchestrator.manual_executor import read, digest, atomic, lock

RUN=rec.RUN
STAGE='result_interpretation_review'
FAILED='a573c5023b98abda38e2233f991b765729e324032901ae8523f818387a3f3b72'
KEY=RUN+':one-review-replacement'
EVENT=KEY
BASE='efb1b016315b87b62a31dc547be65468e689ed87'
OLD='/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-stocktake-navigation-efb1b016/lane'
CHECKPOINT='085940be5384e6aa6d17f623824a1d489d38ce22dd1fe0ab8cb9241e549ea30f'
DECISION='bdffccfeddb2338fc5f64b76e489e6daef60abb6897b428b3b9c7aeb8f4ba340'
BOOTSTRAP='8819a15073af3e6f337c095a76bb469cd7aca07012a0205026541d065c9c0d71'
REPLACEMENT=digest((RUN+':'+STAGE+':2').encode())


def checkpoint():
    p=Path(__file__).resolve().parents[1]/'docs/STOCKTAKE_REVIEW_CHECKPOINT.json'
    if digest(p.read_bytes())!=CHECKPOINT:raise ValueError('REVIEW_RECOVERY_CHECKPOINT_CHANGED')
    return read(p)


def authority(root):
    for name,pin in [('STOCKTAKE_REVIEW_CONTINUATION.txt',DECISION),('ADMIN_REVIEW_SEARCH_APPROVAL.txt',BOOTSTRAP)]:
        if digest((Path(root)/'docs'/name).read_bytes())!=pin:raise ValueError('REVIEW_RECOVERY_AUTHORITY_CHANGED')


def unchanged(db,table,pins):
    for ident,pin in pins.items():
        row=db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone()
        if row is None or rec.sha(dict(row))!=pin:raise ValueError('REVIEW_RECOVERY_ORIGINAL_ROW_CHANGED')


def prior(host):
    from tools.deploy_manual_lane import bound
    from orchestrator import stocktake_navigation as nav
    p=checkpoint();old=bound(host,OLD);c=read(old/'lane.json')
    if old.is_symlink() or (old/'HALT').exists():raise ValueError('REVIEW_RECOVERY_OLD_HALTED_OR_ALIAS')
    if rec.sha(c)!=p['config_sha256'] or digest((old/'preparation-plan.json').read_bytes())!=rec.PLAN:
        raise ValueError('REVIEW_RECOVERY_OLD_CONFIG_CHANGED')
    if digest(bound(host,c['owner_path']).read_bytes())!=p['owner_file_sha256']:
        raise ValueError('REVIEW_RECOVERY_OWNER_CHANGED')
    with rec.connect(old/'jobs.sqlite') as db:
        unchanged(db,'manual_calls',p['local_calls'])
        if (len(rec.rows(db,'manual_calls'))!=5 or rec.sha(rec.rows(db,'manual_account'))!=p['account_sha256']
            or rec.sha(rec.rows(db,'manual_state'))!=p['state_sha256']
            or rec.sha(rec.rows(db,'manual_recoveries'))!=p['recoveries_sha256']):
            raise ValueError('REVIEW_RECOVERY_OLD_STATE_CHANGED')
        parent=json.loads(db.execute('SELECT binding FROM manual_recoveries WHERE failed_id=?',(nav.KEY,)).fetchone()[0])
    with rec.connect(bound(host,c['batch_ledger'])/'jobs.sqlite') as db:
        unchanged(db,'autonomy_calls',p['global_calls'])
        if rec.sha([dict(x) for x in db.execute('SELECT * FROM autonomy_runs WHERE id=?',(RUN,))])!=p['owner_sha256']:
            # A successful accepted completion is separately checked in the new lane.
            owner=db.execute('SELECT binding,status FROM autonomy_runs WHERE id=?',(RUN,)).fetchone()
            original=c['owner_binding']
            if owner is None or owner['status']!='COMPLETE' or json.loads(owner['binding'])!=original:
                raise ValueError('REVIEW_RECOVERY_GLOBAL_OWNER_CHANGED')
        event=db.execute('SELECT payload FROM events WHERE id=?',(nav.EVENT,)).fetchone()
        if event is None or event[0]!=rec.encoded(parent):raise ValueError('REVIEW_RECOVERY_PARENT_EVENT_CHANGED')
    # Preserve the original recovery ancestry and its original proof scope.
    nav.prior(bound(host,nav.OLD),host,exact=False)
    for path,pin in [(parent['review_path'],parent['review_sha256']),(parent['dry_run_path'],parent['dry_run_sha256'])]:
        if digest(bound(host,path).read_bytes())!=pin:raise ValueError('REVIEW_RECOVERY_PARENT_EVIDENCE_CHANGED')
    for item in read(bound(host,parent['dry_run_path']))['connections']:
        if digest(bound(host,item['proof_path']).read_bytes())!=item['proof_sha256']:
            raise ValueError('REVIEW_RECOVERY_PARENT_PROOF_CHANGED')
    if rec.sha(rec.state_snapshot(old))!=p['snapshot_sha256']:raise ValueError('REVIEW_RECOVERY_OLD_SNAPSHOT_CHANGED')
    return c


def qualified(report,source,host):
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_host_guard import trusted
    private_records.check_tree(Path(report).parent)
    for path in [Path(report).parent,*Path(report).parent.rglob('*')]:trusted(path)
    result=verify_result(Path(report).parent)
    manifest=read(Path(report).parent/'packet-manifest.json')
    if (result['verdict']!='APPROVE' or result['source_sha']!=source or result['runtime_sha256']!=rec.RUNTIME
        or digest(Path(report).read_bytes())!=result['report_sha256']
        or manifest['files'].get('evidence/analysis-plan.json')!=rec.PLAN
        or Path(report).read_text().splitlines().count('analysis_entrypoint: orchestrator.analysis_driver')!=1):
        raise ValueError('REVIEW_RECOVERY_AUTOMATED_APPROVAL_REQUIRED')
    return result


def promotion_check(host,previous,source,entrypoint,report):
    from orchestrator.manual_driver import git
    from orchestrator import stocktake_navigation as nav
    from tools.deploy_manual_lane import bound
    authority(source)
    if entrypoint!='analysis' or previous['source']!=BASE or previous['state']+'/lane'!=OLD:
        raise ValueError('REVIEW_RECOVERY_PROMOTION_SCOPE')
    if digest((Path(source)/'deploy/manual-lane/runtime.promotion.json').read_bytes())!=rec.RUNTIME:
        raise ValueError('REVIEW_RECOVERY_RUNTIME_CHANGED')
    qualified(report,git(source,'rev-parse','HEAD'),host);prior(host)
    return [bound(host,p) for p in [rec.OLD_STATE,nav.OLD,OLD]]


def validate(value):
    from tools.deploy_manual_lane import bound
    host=Path(value.get('filesystem_root','/'));root=Path(value['root']);authority(root);p=checkpoint()
    if (value.get('run_id'),value.get('stage'),value.get('failed_id'),value.get('decision_sha256'),value.get('review_checkpoint'))!=(RUN,STAGE,FAILED,DECISION,CHECKPOINT):
        raise ValueError('REVIEW_RECOVERY_SCOPE')
    if value.get('preserved_failures')!=[rec.FAILED,FAILED]:raise ValueError('REVIEW_RECOVERY_FAILURE_SET')
    prior(host);qualified(value['review_path'],value['runtime_source'],host)
    if digest(Path(value['review_path']).read_bytes())!=value['review_sha256']:
        raise ValueError('REVIEW_RECOVERY_REVIEW_CHANGED')
    if digest(Path(value['dry_run_path']).read_bytes())!=value['dry_run_sha256']:raise ValueError('REVIEW_RECOVERY_MATRIX_CHANGED')
    rec.validate_matrix(read(value['dry_run_path']),root,filesystem_root=host)
    selected=rec.installed_selection(root,host)
    if selected['source']!=value['runtime_source'] or Path(value['state']).resolve()!=bound(host,selected['state'])/'lane':
        raise ValueError('REVIEW_RECOVERY_SELECTED_STATE_REQUIRED')
    return value


def permit(store,run):
    from orchestrator.stocktake_review_requalification import permit as saved_permit
    saved=saved_permit(store,run)
    if saved is not None:return saved
    if run!=RUN:return None
    row=store.db.execute('SELECT binding FROM manual_recoveries WHERE failed_id=?',(KEY,)).fetchone()
    if row is None:return None
    value=validate(json.loads(row[0]));p=checkpoint();unchanged(store.db,'manual_calls',p['local_calls'])
    if Path(store.path).resolve()!=Path(value['state'])/'jobs.sqlite':raise ValueError('REVIEW_RECOVERY_LOCAL_LEDGER')
    other=store.batch.db.execute('SELECT payload FROM events WHERE id=?',(EVENT,)).fetchone() if store.batch else None
    if other is None or other[0]!=rec.encoded(value):raise ValueError('REVIEW_RECOVERY_BOTH_LEDGER_BINDING')
    return value


def global_permit(batch,run):
    from orchestrator.stocktake_review_requalification import global_permit as saved_permit
    saved=saved_permit(batch,run)
    if saved is not None:return saved
    if run!=RUN:return None
    row=batch.db.execute('SELECT payload FROM events WHERE id=?',(EVENT,)).fetchone()
    if row is None:return None
    value=validate(json.loads(row[0]));unchanged(batch.db,'autonomy_calls',checkpoint()['global_calls'])
    from tools.deploy_manual_lane import bound
    if batch.folder.resolve()!=bound(value.get('filesystem_root','/'),'/var/lib/research-system-autonomy/reviews'):
        raise ValueError('REVIEW_RECOVERY_GLOBAL_LEDGER')
    return value


def admission(batch,run,stage,ident,source,receipt):
    value=global_permit(batch,run)
    if value is None:return None
    if value.get('kind')=='saved-call6-requalification':raise ValueError('REQUALIFICATION_NO_SCIENTIFIC_CALL')
    if (stage,ident,source,receipt.get('linked_recovery_of'))!=(STAGE,REPLACEMENT,value['runtime_source'],FAILED):
        raise ValueError('ONE_LINKED_REVIEW_REPLACEMENT_ONLY')
    if batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE change_id=?",(RUN,)).fetchone()[0]!=5:
        raise ValueError('REVIEW_REPLACEMENT_ALREADY_USED')
    return value['preserved_failures']


def completion(batch,run):
    value=global_permit(batch,run)
    if value is None:return None
    row=batch.db.execute('SELECT status,receipt FROM autonomy_calls WHERE id=?',(REPLACEMENT,)).fetchone()
    if row is None or row['status']!='COMPLETE':raise ValueError('REVIEW_REPLACEMENT_NOT_COMPLETE')
    receipt=json.loads(row['receipt']);path=Path(receipt['workspace'])/'review.json'
    if digest(path.read_bytes())!=receipt['output_sha256']['review.json'] or read(path).get('verdict')!='APPROVE':
        raise ValueError('REVIEW_REPLACEMENT_NOT_APPROVED')
    return value['preserved_failures']


def validate_next_call(store,stage,n):
    value=json.loads(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
    if stage!=STAGE or n!=2 or len(rec.rows(store.db,'manual_calls'))!=5 or value.get('phase')!=STAGE:
        raise ValueError('ONE_LINKED_REVIEW_REPLACEMENT_ONLY')
    artifacts={x['id']:x for x in value['artifacts']}
    for expected in checkpoint()['interpretation_artifacts']:
        if artifacts.get(expected['id'])!=expected:raise ValueError('REVIEW_REPLACEMENT_AUTHOR_CHANGED')


@private_records.private_umask
def continue_run(state,root,report,matrix,*,filesystem_root=Path('/')):
    from tools import deploy_manual_lane as deploy,manual_promotion
    from orchestrator.manual_driver import git,write_once
    from orchestrator.analysis_driver import release_identities
    host=Path(filesystem_root).resolve();state,root,report,matrix=map(Path,(state,root,report,matrix))
    if host==Path('/') and os.getuid()!=1003:raise ValueError('REVIEW_CONTINUATION_OWNER_REQUIRED')
    if any(not p.resolve().is_relative_to(host) for p in [state,root,report,matrix]):raise ValueError('REVIEW_CONTINUATION_PATH_ESCAPE')
    if state.exists() or state.is_symlink():raise ValueError('REVIEW_CONTINUATION_EXISTING_DESTINATION')
    with lock(state.parent/'review-continuation.lock'):
        before=prior(host);authority(root);old=deploy.bound(host,OLD)
        head=git(root,'rev-parse','HEAD');branch=git(root,'branch','--show-current')
        if git(root,'status','--porcelain') or not branch.startswith('astra/manual-server-'):
            raise ValueError('REVIEW_CONTINUATION_CLEAN_SERVER_SOURCE')
        selected=read(deploy.bound(host,manual_promotion.POINTER))
        if (root.resolve()!=deploy.bound(host,selected['state'])/'repository' or state.resolve()!=deploy.bound(host,selected['state'])/'lane'
            or selected['source']!=head or digest(Path(os.environ['RESEARCH_MANUAL_RUNTIME_CONFIG']).read_bytes())!=rec.RUNTIME):
            raise ValueError('REVIEW_CONTINUATION_HELD_INSTALL_REQUIRED')
        for unit in selected['units']+[Path(OLD).parent.name+'.service',Path(OLD).parent.name+'.timer']:
            if deploy.system(host,'state',unit)!={'enabled':False,'active':False}:raise ValueError('REVIEW_CONTINUATION_UNITS_NOT_HELD')
        with rec.connect(old/'jobs.sqlite') as db:value=json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
        if value.get('pending',{}).get('id')!=FAILED or value.get('phase')!='BLOCKED':raise ValueError('REVIEW_CONTINUATION_EXACT_FAILURE')
        config={**before,'root':str(root.resolve()),'context':str(state/'context'),'branch':branch,'source':head,
            'owner_path':str(deploy.bound(host,before['owner_path'])),'workspace_root':str(state.parent/'lane-scientific-workspaces'),
            'engine_review':{'path':str(report.resolve()),'sha256':digest(report.read_bytes())},
            'execution_recovery':{**before['execution_recovery'],'runtime_source':head,'failed_id':FAILED,'decision_sha256':DECISION,'filesystem_root':str(host)}}
        config['profile_files'],config['engine_files']=release_identities(root)
        if config['profile_files']!=before['profile_files']:raise ValueError('REVIEW_CONTINUATION_PROFILE_CHANGED')
        binding={'run_id':RUN,'stage':STAGE,'failed_id':FAILED,'failed_sha256':checkpoint()['local_calls'][FAILED],
            'decision_sha256':DECISION,'review_checkpoint':CHECKPOINT,'preserved_failures':[rec.FAILED,FAILED],
            'root':str(root.resolve()),'state':str(state.resolve()),'filesystem_root':str(host),'runtime_source':head,
            'review_path':str(report.resolve()),'review_sha256':digest(report.read_bytes()),'config_sha256':rec.sha(config),
            'dry_run_path':str(matrix.resolve()),'dry_run_sha256':digest(matrix.read_bytes())}
        validate(binding)
        with rec.connect(deploy.bound(host,before['batch_ledger'])/'jobs.sqlite') as db:
            if db.execute('SELECT 1 FROM events WHERE id=?',(EVENT,)).fetchone():raise ValueError('REVIEW_CONTINUATION_ALREADY_RECORDED')
            if any(x['id'] not in binding['preserved_failures'] or x['status']!='UNCERTAIN' for x in db.execute("SELECT id,status FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')")):
                raise ValueError('REVIEW_CONTINUATION_OTHER_PENDING')
        intent=state.parent/'review-continuation-intent.json'
        write_once(intent,(rec.encoded(binding)+'\n').encode())
        private_records.mkdir(state)
        for p in old.iterdir():
            if p.name in {'jobs.sqlite','jobs.sqlite-wal','jobs.sqlite-shm','lane.json'}:continue
            if p.is_dir():private_records.copytree(p,state/p.name)
            else:private_records.copyfile(p,state/p.name)
        with rec.connect(old/'jobs.sqlite') as src,sqlite3.connect(state/'jobs.sqlite') as dst:src.backup(dst)
        atomic(state/'lane.json',config)
        value.update(phase=STAGE,reason=None,linked_recovery_of=FAILED);value.pop('pending',None)
        with sqlite3.connect('file:'+str(state/'jobs.sqlite')+'?mode=rw',uri=True) as db:
            db.execute('INSERT INTO manual_recoveries VALUES(?,?)',(KEY,rec.encoded(binding)))
            db.execute('UPDATE manual_state SET payload=? WHERE id=1',(rec.encoded(value),))
        with sqlite3.connect('file:'+str(deploy.bound(host,before['batch_ledger'])/'jobs.sqlite')+'?mode=rw',uri=True) as db:
            db.row_factory=sqlite3.Row;db.execute('BEGIN IMMEDIATE')
            if (deploy.bound(host,before['batch_ledger'])/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
            unchanged(db,'autonomy_calls',checkpoint()['global_calls'])
            if any(x['id'] not in binding['preserved_failures'] or x['status']!='UNCERTAIN' for x in db.execute("SELECT id,status FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')")):
                raise ValueError('REVIEW_CONTINUATION_OTHER_PENDING')
            db.execute('INSERT INTO events VALUES(?,?,?)',(EVENT,RUN,rec.encoded(binding)))
        if rec.sha(rec.state_snapshot(old))!=checkpoint()['snapshot_sha256']:raise ValueError('REVIEW_CONTINUATION_OLD_STATE_CHANGED')
        private_records.check_tree(state)
        return {'status':'CONTINUED_NO_MODEL_CALL','source':head,'calls_used':5,'call_limit':8,'next':STAGE,'replacement_of':FAILED}


def main():
    import argparse
    p=argparse.ArgumentParser()
    for n in ['state','root','report','matrix']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--filesystem-root',type=Path,default=Path('/'));a=p.parse_args()
    print(json.dumps(continue_run(a.state,a.root,a.report,a.matrix,filesystem_root=a.filesystem_root),indent=2))

if __name__=='__main__':main()
