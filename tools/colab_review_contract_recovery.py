"""Exact zero-call Colab contract correction; no model or allowance change."""
import base64,hashlib,json,os,sqlite3,subprocess
from pathlib import Path
from orchestrator import private_records as pr
CHANGE='colab-contract-and-direction-20261010'
DOCUMENT='docs/COLAB_REVIEW_CONTRACT_PRIVATE.json'
DOCUMENT_SHA='e73c76f785d059163dcc858a5a5ee87a9c1dc079ecbf94ea285250cf737d0b21'
LANE=Path('/var/lib/research-system-manual-sprint10-deployment/colab-preparation-20261010/lane')
LEDGER=Path('/var/lib/research-system-autonomy/reviews/jobs.sqlite')
RUN='colab-1ad5fafc220b3d65f576ce08'
SOURCE='304cae4aa12d53eb99254499950eec4e71df8075'
RECORD=LANE/'review-contract-reconciliation-20261010'
def require(ok,why):
    if not ok:raise ValueError('COLAB_CONTRACT_'+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True).encode()
def binding():
    raw=(Path(__file__).resolve().parents[1]/DOCUMENT).read_bytes();require(sha(raw)==DOCUMENT_SHA,'DOCUMENT_CHANGED');return json.loads(raw)
def snapshot(db):
    return {name:[dict(r) for r in db.execute('SELECT * FROM '+name+' ORDER BY rowid')] for name in ['manual_state','manual_account','manual_calls']}
def validate(config_raw,rows,global_calls,workspace_exists):
    b=binding();cfg=json.loads(config_raw);state=json.loads(rows['manual_state'][0]['payload'])
    require(sha(config_raw)==b['config_sha256'] and config_raw==base64.b64decode(b['config_base64']),'ORIGINAL_CONFIG_CHANGED')
    require(rows=={'manual_state':[b['state']],'manual_account':[b['account']],'manual_calls':[]},'ZERO_CALL_ORIGINAL_ROWS_REQUIRED')
    require(not global_calls and not workspace_exists,'NO_ADMISSION_OR_WORKSPACE')
    require(cfg['run_id']==RUN and cfg['source']==SOURCE and cfg.get('review_contract') is None and cfg.get('colab_preparation') and cfg.get('notebook_revision') and cfg.get('private_intake'),'EXACT_MISSING_CONTRACT')
    require(state['phase']=='BLOCKED' and state['reason']=='ContextError: NOTEBOOK_PATCH_OUTPUT_SCOPE' and not state.get('pending') and state['rounds']=={},'EXACT_BLOCK')
    require(json.loads(rows['manual_account'][0]['payload'])['count']==0,'ORIGINAL_ZERO_ACCOUNT')
    return cfg,state
def approval(folder):
    from orchestrator.autonomy_review import verify_result
    result=verify_result(folder);manifest=json.loads(pr.check(Path(folder)/'packet-manifest.json').read_bytes())
    require(result['verdict']=='APPROVE' and not result.get('findings') and result['change_id']==CHANGE,'GENUINE_APPROVAL')
    root=Path(__file__).resolve().parents[1]
    for name in [DOCUMENT,'tools/colab_review_contract_recovery.py','orchestrator/analysis_driver.py']:
        require(manifest['source_files'].get(name)==sha((root/name).read_bytes()),'REVIEWED_BYTES')
    return result
def held_unit():
    name='research-preparation-branch-admission-repair-20261010-colab_preparation.service'
    text=subprocess.check_output(['systemctl','show',name,'-p','MainPID','-p','ActiveState','-p','ExecMainStatus'],text=True)
    require(dict(line.split('=',1) for line in text.splitlines())=={'MainPID':'0','ActiveState':'inactive','ExecMainStatus':'0'},'HELD_ORIGINAL_UNIT')
@pr.private_umask
def apply(review,*,root=Path('/'),check_unit=held_unit):
    require(os.getuid()==os.getgid()==1003,'SERVICE_OWNER')
    from tools.deploy_manual_lane import bound
    from orchestrator.remote_supervisor import lock
    path=lambda p:bound(Path(root),str(p))
    reviewed=approval(review);dest=path(RECORD)
    require(not path(LANE/'HALT').exists() and not path(LEDGER.parent/'HALT').exists(),'HALT_PRESERVED')
    check_unit()
    require(not dest.exists() and not dest.is_symlink(),'EXISTING_OUTCOME_PRESERVED')
    with lock(path(LANE/'one-run.lock')),lock(path(LANE/'driver.lock')):
        db=pr.Connection(path(LANE/'jobs.sqlite'));db.row_factory=sqlite3.Row
        try:
            original=pr.check(path(LANE/'lane.json')).read_bytes();cfg=json.loads(original)
            workspace=path(Path(cfg['workspace_root']))
            with sqlite3.connect(path(LEDGER).resolve().as_uri()+'?mode=ro',uri=True) as globaldb:
                globaldb.row_factory=sqlite3.Row
                require(not globaldb.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'OTHER_RUNNING_CALL')
                calls=[dict(r) for r in globaldb.execute('SELECT * FROM autonomy_calls WHERE change_id=?',(RUN,))]
                cfg,state=validate(original,snapshot(db),calls,workspace.exists() or workspace.is_symlink())
            owner=pr.check(path(Path(cfg['owner_path']))).read_bytes();require(json.loads(owner)==cfg['owner_binding'],'OWNER_UNCHANGED')
            plan=pr.check(path(LANE/'preparation-plan.json')).read_bytes();require(sha(plan)==cfg['plan_sha256'],'PLAN_UNCHANGED')
            target={**cfg,'review_contract':'bound-review/v1'}
            intervention={'kind':'EXACT_ZERO_CALL_COLAB_CONTRACT_CORRECTION','review_sha256':reviewed['report_sha256'],'original_config_sha256':sha(original),'binding_sha256':DOCUMENT_SHA,'new_calls':0,'new_allowance':0}
            resumed={**state,'phase':'run_spec_author','reason':None,'interventions':[*state.get('interventions',[]),intervention]}
            pr.mkdir(dest);pr.write_bytes(dest/'lane.original.json',original);pr.write_bytes(dest/'original-rows.json',canonical(snapshot(db)));pr.write_bytes(dest/'owner.original.json',owner)
            backup=sqlite3.connect(dest/'before.sqlite');db.backup(backup);backup.close()
            pr.write_bytes(dest/'INTENT.json',canonical({'intervention':intervention,'config_after':target,'state_after':resumed}))
            # A crash after the config write remains BLOCKED; the exclusive
            # record forbids a blind second application.
            pr.atomic(path(LANE/'lane.json'),target)
            db.execute('BEGIN IMMEDIATE')
            try:
                require(snapshot(db)=={'manual_state':[binding()['state']],'manual_account':[binding()['account']],'manual_calls':[]},'STATE_RACE')
                db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(resumed,sort_keys=True),));db.execute('COMMIT')
            except BaseException:db.execute('ROLLBACK');raise
            require(pr.check(path(Path(cfg['owner_path']))).read_bytes()==owner and pr.check(path(LANE/'preparation-plan.json')).read_bytes()==plan,'OWNER_PLAN_CHANGED')
            result={'status':'CORRECTED_READY_NO_CALL','run_id':RUN,'source':SOURCE,'review_sha256':reviewed['report_sha256'],'calls':0,'allowance_change':0,'contract':'bound-review/v1'}
            pr.write_bytes(dest/'COMPLETE.json',canonical(result));return result
        finally:db.close()

if __name__=='__main__':
    import argparse
    os.umask(0o077);parser=argparse.ArgumentParser();parser.add_argument('--review',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(apply(args.review),sort_keys=True))
