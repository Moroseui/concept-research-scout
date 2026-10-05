"""Deterministic requalification of one completed review; never call admission.

Keep the six original call rows, allowance and old lane intact. A versioned
copy binds the reviewed parser to the same saved report and normal finalization.
"""
import json
import os
from pathlib import Path
import sqlite3
from orchestrator import private_records, stocktake_recovery as rec, stocktake_review_recovery as rr
from orchestrator.manual_executor import read, digest, atomic, lock
from tools.deploy_manual_lane import bound

KEY=rec.RUN+':saved-call6-requalification'
DECISION='992522508b1735ea9a81102d387a14420f1de55eadca282fb6a8a4556c0376e2'
CHECKPOINT='941de8146d0907df7443cfb9ef83fbd8e164cf242878e8d23270d3360e2b5728'
REPORT='4a8f8391a34fac210ecc1c8e612b78bdbd6d885469012fd3425b337e2c42b289'


def checkpoint():
    p=Path(__file__).resolve().parents[1]/'docs/STOCKTAKE_CALL6_CHECKPOINT.json'
    if digest(p.read_bytes())!=CHECKPOINT:raise ValueError('REQUALIFICATION_CHECKPOINT_CHANGED')
    return read(p)


def authority(root):
    if digest((Path(root)/'docs/STOCKTAKE_CALL6_REQUALIFICATION_APPROVAL.txt').read_bytes())!=DECISION:
        raise ValueError('REQUALIFICATION_AUTHORITY_CHANGED')
    rr.authority(root)


def call_rows(db,table):
    pins=checkpoint()['local_calls' if table=='manual_calls' else 'global_calls']
    rr.unchanged(db,table,pins)
    query='SELECT count(*) FROM '+table
    count=db.execute(query).fetchone()[0] if table=='manual_calls' else db.execute(query+' WHERE change_id=?',(rec.RUN,)).fetchone()[0]
    if count!=6:raise ValueError('REQUALIFICATION_EXACT_SIX_CALLS_REQUIRED')


def saved_report(host):
    p=bound(host,checkpoint()['pending']['workspace'])/'review.json'
    if digest(p.read_bytes())!=REPORT:raise ValueError('REQUALIFICATION_SAVED_REPORT_CHANGED')
    return p


def prior(host):
    p=checkpoint();old=bound(host,p['selected']['state'])/'lane';rr.prior(host)
    c=read(old/'lane.json')
    if (old/'HALT').exists() or old.is_symlink():raise ValueError('REQUALIFICATION_OLD_HALTED_OR_ALIAS')
    if rec.sha(c)!=p['config_sha256'] or digest(bound(host,c['owner_path']).read_bytes())!=p['owner_file_sha256']:
        raise ValueError('REQUALIFICATION_OLD_CONFIG_OR_OWNER_CHANGED')
    with rec.connect(old/'jobs.sqlite') as db:
        call_rows(db,'manual_calls')
        v=json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
        if (rec.sha(v)!=p['state_sha256'] or rec.sha(rec.rows(db,'manual_account'))!=p['account_sha256']
            or rec.sha(rec.rows(db,'manual_recoveries'))!=p['recoveries_sha256']):
            raise ValueError('REQUALIFICATION_OLD_STATE_CHANGED')
    with rec.connect(bound(host,c['batch_ledger'])/'jobs.sqlite') as db:call_rows(db,'autonomy_calls')
    if rec.sha(rec.state_snapshot(old))!=p['snapshot_sha256']:raise ValueError('REQUALIFICATION_OLD_SNAPSHOT_CHANGED')
    saved_report(host)
    return c


def promotion_check(host,previous,source,entrypoint,report):
    from orchestrator.manual_driver import git
    from orchestrator import stocktake_navigation as nav
    authority(source);p=checkpoint()
    if entrypoint!='analysis' or previous!=p['selected']:raise ValueError('REQUALIFICATION_PROMOTION_SCOPE')
    if digest((Path(source)/'deploy/manual-lane/runtime.promotion.json').read_bytes())!=rec.RUNTIME:
        raise ValueError('REQUALIFICATION_RUNTIME_CHANGED')
    rr.qualified(report,git(source,'rev-parse','HEAD'),host);prior(host)
    return [bound(host,x) for x in [rec.OLD_STATE,nav.OLD,rr.OLD,p['selected']['state']+'/lane']]


def validate(value):
    host=Path(value['filesystem_root']);root=Path(value['root']);authority(root);prior(host)
    if (value.get('run_id'),value.get('kind'),value.get('decision_sha256'),value.get('checkpoint'),value.get('saved_report_sha256'))!=(rec.RUN,'saved-call6-requalification',DECISION,CHECKPOINT,REPORT):
        raise ValueError('REQUALIFICATION_SCOPE')
    if value.get('preserved_failures')!=[rec.FAILED,rr.FAILED]:raise ValueError('REQUALIFICATION_FAILURE_SET')
    rr.qualified(value['review_path'],value['runtime_source'],host)
    if digest(Path(value['review_path']).read_bytes())!=value['review_sha256']:raise ValueError('REQUALIFICATION_REVIEW_CHANGED')
    if digest(Path(value['dry_run_path']).read_bytes())!=value['dry_run_sha256']:raise ValueError('REQUALIFICATION_MATRIX_CHANGED')
    rec.validate_matrix(read(value['dry_run_path']),root,filesystem_root=host)
    selected=rec.installed_selection(root,host)
    if selected['source']!=value['runtime_source'] or Path(value['state']).resolve()!=bound(host,selected['state'])/'lane':
        raise ValueError('REQUALIFICATION_SELECTED_STATE_REQUIRED')
    return value


def permit(store,run):
    if run!=rec.RUN:return None
    row=store.db.execute('SELECT binding FROM manual_recoveries WHERE failed_id=?',(KEY,)).fetchone()
    if row is None:return None
    value=validate(json.loads(row[0]));call_rows(store.db,'manual_calls')
    if Path(store.path).resolve()!=Path(value['state'])/'jobs.sqlite':raise ValueError('REQUALIFICATION_LOCAL_LEDGER')
    event=store.batch.db.execute('SELECT payload FROM events WHERE id=?',(KEY,)).fetchone() if store.batch else None
    if event is None or event[0]!=rec.encoded(value):raise ValueError('REQUALIFICATION_BOTH_LEDGER_BINDING')
    return value


def global_permit(batch,run):
    if run!=rec.RUN:return None
    row=batch.db.execute('SELECT payload FROM events WHERE id=?',(KEY,)).fetchone()
    if row is None:return None
    value=validate(json.loads(row[0]));call_rows(batch.db,'autonomy_calls')
    if batch.folder.resolve()!=bound(value['filesystem_root'],'/var/lib/research-system-autonomy/reviews'):
        raise ValueError('REQUALIFICATION_GLOBAL_LEDGER')
    return value


@private_records.private_umask
def prepare(state,root,report,matrix,*,filesystem_root=Path('/')):
    from tools import manual_promotion, deploy_manual_lane as deploy
    from orchestrator.manual_driver import git,write_once,validate_review
    from orchestrator.analysis_driver import release_identities
    host=Path(filesystem_root).resolve();state,root,report,matrix=map(Path,(state,root,report,matrix))
    if host==Path('/') and os.getuid()!=1003:raise ValueError('REQUALIFICATION_OWNER_REQUIRED')
    if any(not p.resolve().is_relative_to(host) for p in [state,root,report,matrix]):raise ValueError('REQUALIFICATION_PATH_ESCAPE')
    if state.exists() or state.is_symlink():raise ValueError('REQUALIFICATION_EXISTING_DESTINATION')
    with lock(state.parent/'requalification.lock'):
        before=prior(host);authority(root);p=checkpoint();old=bound(host,p['selected']['state'])/'lane'
        validate_review(read(saved_report(host)))
        head=git(root,'rev-parse','HEAD');branch=git(root,'branch','--show-current')
        if git(root,'status','--porcelain') or not branch.startswith('astra/manual-server-'):raise ValueError('REQUALIFICATION_CLEAN_SERVER_SOURCE')
        selected=read(bound(host,manual_promotion.POINTER))
        if (root.resolve()!=bound(host,selected['state'])/'repository' or state.resolve()!=bound(host,selected['state'])/'lane'
            or selected['source']!=head or digest(Path(os.environ['RESEARCH_MANUAL_RUNTIME_CONFIG']).read_bytes())!=rec.RUNTIME):
            raise ValueError('REQUALIFICATION_HELD_INSTALL_REQUIRED')
        for unit in selected['units']+p['selected']['units']:
            if deploy.system(host,'state',unit)!={'enabled':False,'active':False}:raise ValueError('REQUALIFICATION_UNITS_NOT_HELD')
        config={**before,'root':str(root.resolve()),'context':str(state/'context'),'branch':branch,
            'owner_path':str(bound(host,before['owner_path'])),'workspace_root':str(state.parent/'lane-scientific-workspaces'),
            'engine_review':{'path':str(report.resolve()),'sha256':digest(report.read_bytes())},
            'execution_recovery':{**before['execution_recovery'],'runtime_source':head,'filesystem_root':str(host)}}
        # Original source and call provenance remain unchanged; runtime_source
        # identifies only the new parser/finalizer. There is no new allowance.
        config['profile_files'],config['engine_files']=release_identities(root)
        if config['profile_files']!=before['profile_files']:raise ValueError('REQUALIFICATION_PROFILE_CHANGED')
        binding={'run_id':rec.RUN,'kind':'saved-call6-requalification','decision_sha256':DECISION,'checkpoint':CHECKPOINT,
            'saved_report_sha256':REPORT,'preserved_failures':[rec.FAILED,rr.FAILED],
            'root':str(root.resolve()),'state':str(state.resolve()),'filesystem_root':str(host),'runtime_source':head,
            'review_path':str(report.resolve()),'review_sha256':digest(report.read_bytes()),'config_sha256':rec.sha(config),
            'dry_run_path':str(matrix.resolve()),'dry_run_sha256':digest(matrix.read_bytes())}
        validate(binding)
        def check_global(db):
            call_rows(db,'autonomy_calls')
            if db.execute('SELECT 1 FROM events WHERE id=?',(KEY,)).fetchone():raise ValueError('REQUALIFICATION_ALREADY_RECORDED')
            if any(x['id'] not in binding['preserved_failures'] or x['status']!='UNCERTAIN' for x in db.execute("SELECT id,status FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')")):
                raise ValueError('REQUALIFICATION_OTHER_PENDING')
            if (bound(host,before['batch_ledger'])/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
        ledger=bound(host,before['batch_ledger'])/'jobs.sqlite'
        with rec.connect(ledger) as db:check_global(db)
        write_once(state.parent/'requalification-intent.json',(rec.encoded(binding)+'\n').encode())
        private_records.mkdir(state)
        for path in old.iterdir():
            if path.name in {'jobs.sqlite','jobs.sqlite-wal','jobs.sqlite-shm','lane.json'}:continue
            if path.is_dir():private_records.copytree(path,state/path.name)
            else:private_records.copyfile(path,state/path.name)
        with rec.connect(old/'jobs.sqlite') as src,sqlite3.connect(state/'jobs.sqlite') as dst:src.backup(dst)
        atomic(state/'lane.json',config)
        with sqlite3.connect('file:'+str(state/'jobs.sqlite')+'?mode=rw',uri=True) as db:
            db.execute('INSERT INTO manual_recoveries VALUES(?,?)',(KEY,rec.encoded(binding)))
        with sqlite3.connect('file:'+str(ledger)+'?mode=rw',uri=True) as db:
            db.row_factory=sqlite3.Row;db.execute('BEGIN IMMEDIATE');check_global(db)
            db.execute('INSERT INTO events VALUES(?,?,?)',(KEY,rec.RUN,rec.encoded(binding)))
        prior(host);private_records.check_tree(state)
        return {'status':'PREPARED_SAVED_OUTPUT_ONLY','source':head,'calls_used':6,'call_limit':8,'report_sha256':REPORT}


@private_records.private_umask
def accept(state):
    from orchestrator.analysis_driver import AnalysisDriver
    driver=AnalysisDriver(state)
    with lock(Path(state)/'driver.lock'):
        value=permit(driver.store,driver.config['run_id'])
        if value is None:raise ValueError('REQUALIFICATION_BINDING_REQUIRED')
        current=driver.current();p=checkpoint()
        if current.get('phase')!='BLOCKED' or current.get('reason')!=p['reason'] or current.get('pending')!=p['pending']:
            raise ValueError('REQUALIFICATION_EXACT_PENDING_REQUIRED')
        if Path(current['pending']['workspace'])/'review.json'!=saved_report(Path(value['filesystem_root'])):
            raise ValueError('REQUALIFICATION_OUTPUT_PATH')
        driver.guard()
        result=driver.accept_completed(current)
        if result['phase']!='UPDATE_STATE':raise ValueError('REQUALIFICATION_FINALIZATION_ONLY')
        call_rows(driver.store.db,'manual_calls');call_rows(driver.store.batch.db,'autonomy_calls')
        return result
