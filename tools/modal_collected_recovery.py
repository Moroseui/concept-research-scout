#!/usr/bin/env python3
"""Reconcile only the already validated M3 collection; never submit or call a model."""
import argparse,json,sqlite3,subprocess
from pathlib import Path
from orchestrator import private_records,modal_cleanup
from orchestrator.manual_executor import read,digest,inventory
from orchestrator.modal_executor import canonical as binding_bytes
from orchestrator.autonomy_review import verify_result
from orchestrator.remote_supervisor import lock
from orchestrator.sprint9_modal_validation import validate as validate_result
from tools.modal_pre_admission_recovery import table_rows,canonical

ROOT=Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-autonomy-m3-schema-20261003')
CHANGE='m3-post-smoke-followup'
PINS={'run_id': 'sprint9-modal-65e6429dbad82d84', 'source': 'aca3dff09bba9d7c9efc4d621d52a2920ae54676', 'config_sha256': '6e541f91f554d09eab4a13e3f92adacb0455d9cd4b003e31afc362e899db3d62', 'state_sha256': '2f488d818490cf14328e02166841dc687d740d61a0303a6d3963f0333d7b6cbd', 'tables_sha256': 'acf738843853f0bcf1c14ba230bdd8d9dc5934c5ce51f3ba3c1adf4c38afedd1', 'validation_sha256': '45dd68dd91bc22a03d4385991e592dc41dc89a92ccd962cdf9fea1596e4c43c2', 'collection_sha256': '53b83218e3f1a12b151a2b47473b68273a2d4e7591263d0acf860a17ae1d2cd7', 'provider_id': 'sb-rFXWBFGcLwliqdRFdmuSuz', 'compute_id': 'c748e3536a568482411e3ff7e3ce3e1d5bdd3d23b24f1be12375adcb29d23bde'}


def approval(folder):
    result=verify_result(folder);manifest=read(Path(folder)/'packet-manifest.json')
    if result['verdict']!='APPROVE' or result['change_id']!=CHANGE:raise ValueError('FOCUSED_APPROVAL_REQUIRED')
    source=Path(__file__).resolve().parents[1]
    for name in ['tools/modal_collected_recovery.py','orchestrator/modal_cleanup.py']:
        if manifest['source_files'].get(name)!=digest((source/name).read_bytes()):raise ValueError('REVIEWED_RECOVERY_BYTES_REQUIRED')
    return result


def validate_saved(state,db,config):
    value=read_state(db)
    if digest((state/'lane.json').read_bytes())!=PINS['config_sha256']:raise ValueError('ORIGINAL_CONFIG_CHANGED')
    if config['run_id']!=PINS['run_id'] or config['source']!=PINS['source']:raise ValueError('EXACT_M3_RUN_REQUIRED')
    if value.get('phase')!='BLOCKED' or value.get('blocked_stage')!='WAIT_OUTPUTS' or value.get('reason')!="KeyError: 'wheels_volume_id'" or value.get('pending'):raise ValueError('EXACT_COLLECTED_BLOCK_REQUIRED')
    if digest(canonical(value))!=PINS['state_sha256'] or digest(canonical(table_rows(db)))!=PINS['tables_sha256']:raise ValueError('ORIGINAL_STATE_OR_CALLS_CHANGED')
    if value['rounds']!={'run_spec_author':2,'run_spec_review':2}:raise ValueError('EXACT_COMPLETED_CALLS_REQUIRED')
    calls=list(db.execute('SELECT status FROM manual_calls'))
    if len(calls)!=4 or any(r[0]!='COMPLETE' for r in calls):raise ValueError('EXACT_COMPLETED_CALLS_REQUIRED')
    work=state/'modal-executions'/PINS['run_id'];receipt=read(work/'collection-receipt.json')
    if digest((work/'collection-receipt.json').read_bytes())!=PINS['collection_sha256']:raise ValueError('COLLECTION_CHANGED')
    if receipt['provider_id']!=PINS['provider_id'] or receipt['binding_sha256']!=PINS['compute_id']:raise ValueError('COLLECTION_BINDING_CHANGED')
    if read(work/'terminated.json')!={'provider_id':PINS['provider_id'],'terminated':True}:raise ValueError('TERMINATION_REQUIRED')
    if inventory(work/'incoming')!=receipt['file_sha256']:raise ValueError('COLLECTED_BYTES_CHANGED')
    binding=value['manifest']['binding']
    if digest(binding_bytes(binding))!=PINS['compute_id']:raise ValueError('COMPUTE_BINDING_CHANGED')
    if digest((state/'validation.json').read_bytes())!=PINS['validation_sha256']:raise ValueError('VALIDATION_CHANGED')
    if digest(binding_bytes(read(config['smoke_path'])))!=config['smoke_sha256']:raise ValueError('SMOKE_CONFIG_CHANGED')
    validation=validate_result(work/'incoming',binding,read(config['smoke_path']))
    recorded=read(state/'validation.json')
    if validation['status']!='VALID' or any(recorded.get(k)!=v for k,v in validation.items()):raise ValueError('NATIVE_SAVED_VALIDATION_REFUSED')
    if read(config['owner_path'])!=config['owner_binding']:raise ValueError('OWNER_CHANGED')
    for name,h in {**config['engine_files'],**config['scientific_files'],**config['profile_files']}.items():
        if digest((Path(config['root'])/name).read_bytes())!=h:raise ValueError('BOUND_SOURCE_CHANGED')
    return value


def read_state(db):return json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])


def batch_guard(config):
    with sqlite3.connect('file:'+str(Path(config['modal']['batch_ledger'])/'jobs.sqlite')+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        if db.execute("SELECT 1 FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')").fetchone():raise ValueError('ACTIVE_OR_UNCERTAIN_CALL')
        rows=[dict(r) for r in db.execute('SELECT * FROM autonomy_compute WHERE run=?',(PINS['run_id'],))]
        if len(rows)!=1 or rows[0]['id']!=PINS['compute_id'] or rows[0]['provider_id']!=PINS['provider_id'] or rows[0]['status']!='COLLECTED':raise ValueError('EXACT_COLLECTED_COMPUTE_REQUIRED')
        return rows


@private_records.private_umask
def apply(state,review_folder):
    state=Path(state)
    if state!=ROOT/'lane' or state.is_symlink():raise ValueError('EXACT_M3_STATE_PATH_REQUIRED')
    approved=approval(review_folder)
    for suffix in ['.service','.timer']:
        if subprocess.check_output(['/usr/bin/systemctl','show',ROOT.name+suffix,'-p','ActiveState','--value'],text=True).strip()!='inactive':raise ValueError('LANE_MUST_BE_HELD')
    if (state/'HALT').exists():raise ValueError('HALT_REMAINS_EFFECTIVE')
    dest=state/'collected-cleanup-reconciliation-20261003'
    if dest.exists():raise ValueError('RECOVERY_EXISTS_RECONCILE_NO_BLIND_RETRY')
    config=read(state/'lane.json')
    with lock(state/'one-run.lock'),lock(state/'driver.lock'):
        db=private_records.Connection(state/'jobs.sqlite')
        value=validate_saved(state,db,config);before=table_rows(db);compute=batch_guard(config)
        private_records.mkdir(dest)
        backup=private_records.Connection(dest/'before.sqlite');db.backup(backup);backup.close()
        private_records.copyfile(state/'DECISION_REQUEST.md',dest/'DECISION_REQUEST.original.md')
        intent={'pins':PINS,'before':value,'review_source':approved['source_sha'],'review_report_sha256':approved['report_sha256'],'additional_calls':0,'additional_allowance':0,'additional_compute':0}
        private_records.write_bytes(dest/'INTENT.json',canonical(intent))
        # Existing authenticated provider: only exact verified copied assets may be
        # removed. Completed result, local originals and accounting are untouched.
        from orchestrator.modal_provider import ModalProvider
        cleanup=modal_cleanup.clear_copies(ModalProvider(config['modal']),config['modal'],state/'asset-cleanup',collected=True)
        if cleanup.get('status')!='CLEARED' or cleanup.get('runtime_sha256')!=digest(binding_bytes(config['modal'])):raise ValueError('CLEANUP_NOT_BOUND')
        if batch_guard(config)!=compute:raise ValueError('COMPUTE_CHANGED')
        validate_saved(state,db,config)
        restored={**value,'phase':'WAIT_OUTPUTS','reason':None,'interventions':value['interventions']+[{'kind':'COLLECTED_CLEANUP_RECOVERY',**{k:v for k,v in intent.items() if k!='before'}}]}
        db.execute('BEGIN IMMEDIATE')
        try:
            if read_state(db)!=value or table_rows(db)!=before:raise ValueError('STATE_CHANGED_DURING_RECONCILIATION')
            db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(restored),))
            if table_rows(db)!=before:raise ValueError('ACCOUNTING_CHANGED')
            db.execute('COMMIT')
        except BaseException:db.execute('ROLLBACK');raise
        db.close()
        done={'status':'RECONCILED','next':'WAIT_OUTPUTS: native saved validation, no execution retry','calls_used':4,'all_non_state_rows_unchanged':True,'cleanup':cleanup}
        private_records.write_bytes(dest/'COMPLETE.json',canonical(done));return done


def main():
    p=argparse.ArgumentParser();p.add_argument('--state',required=True);p.add_argument('--approval-folder',required=True);a=p.parse_args();print(json.dumps(apply(a.state,a.approval_folder),sort_keys=True))
if __name__=='__main__':main()
