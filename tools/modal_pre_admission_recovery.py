#!/usr/bin/env python3
"""Exact M3 pre-admission reconciliation. Never retries a reserved model call.

Administrative application requires a genuine approving queue result bound to
these helper bytes. Scientific source, owner, policy, calls and accounts stay
unchanged. The original block and database are preserved before a state write.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
from orchestrator import private_records
from orchestrator.remote_supervisor import lock
from orchestrator.autonomy_review import verify_result

BINDINGS = {'run_id': 'sprint9-modal-65e6429dbad82d84', 'source': 'aca3dff09bba9d7c9efc4d621d52a2920ae54676', 'call_id': 'e65d5abb190f6d97c6e17f133385ca2a08df86d88f06dd7f8f5056b7198bf7fc', 'output_sha256': 'a2428c7a3f5dc35e06de9b86837981c71edd8b5f347acc7ba18898ebf5a8b567', 'state_sha256': '4cd3bcd19f887ffc7972027a38dbbdc2bf91b167b9a670819bebe2d806afa4fa', 'call_sha256': 'a53726bd361c8783a20a86c7654ca12f95ba5a5d919e416692208556eda852a7', 'checkpoint_archive_sha256': '9ed4692544a65e93388e599ed7e82377cfdc003eaf5c9e894d6946ef19bd7bb1', 'config_sha256': '6e541f91f554d09eab4a13e3f92adacb0455d9cd4b003e31afc362e899db3d62'}
ROOT = Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-autonomy-m3-schema-20261003')
CHANGE = 'autonomy-m3-host-proof-transition-20261003'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True).encode()


def validate(config, value, calls, spec):
    if config['run_id'] != BINDINGS['run_id'] or config['source'] != BINDINGS['source']:
        raise ValueError('EXACT_M3_RUN_REQUIRED')
    if value.get('phase') != 'BLOCKED' or value.get('blocked_stage') != 'run_spec_review' or value.get('reason') != 'ValueError: HOST_PROOF_EXPIRED' or value.get('pending'):
        raise ValueError('EXACT_PRE_ADMISSION_BLOCK_REQUIRED')
    if sha(canonical(value)) != BINDINGS['state_sha256']:
        raise ValueError('ORIGINAL_STATE_CHANGED')
    if len(calls) != 1 or calls[0]['id'] != BINDINGS['call_id'] or calls[0]['stage'] != 'run_spec_author' or calls[0]['status'] != 'COMPLETE':
        raise ValueError('ONLY_COMPLETED_AUTHOR_NO_REVIEW_CALL')
    if sha(canonical(calls[0])) != BINDINGS['call_sha256']:
        raise ValueError('ORIGINAL_CALL_CHANGED')
    if sha(spec) != BINDINGS['output_sha256']:
        raise ValueError('COMPLETED_SPEC_CHANGED')


def approval(folder):
    result = verify_result(folder)
    manifest = json.loads((Path(folder) / 'packet-manifest.json').read_text())
    if result['verdict'] != 'APPROVE' or result['change_id'] != CHANGE:
        raise ValueError('FOCUSED_APPROVAL_REQUIRED')
    for name in ['modal_transition_service.py', 'modal_pre_admission_recovery.py']:
        if manifest['source_files'].get('tools/' + name) != sha(Path(__file__).with_name(name).read_bytes()):
            raise ValueError('REVIEWED_HELPER_BYTES_REQUIRED')
    return result



def installed_entrypoint():
    from orchestrator.manual_host_guard import trusted
    entry = trusted(Path(__file__).with_name('modal_transition_service.py'))
    drop = trusted(Path('/etc/systemd/system')/(ROOT.name+'.service.d')/'20-one-transition.conf')
    expected = ('[Service]\nExecStart=\nExecStart=/usr/bin/python3 -B '+str(entry)+
                ' --state '+str(ROOT/'lane')+' --preparation '+str(ROOT/'modal-preparation')+'\n')
    if drop.read_text() != expected:
        raise ValueError('REVIEWED_TRANSITION_OVERRIDE_REQUIRED')
    import subprocess
    loaded = subprocess.check_output(['/usr/bin/systemctl','show',ROOT.name+'.service','-p','ExecStart','--value'], text=True)
    command = 'argv[]=/usr/bin/python3 -B '+str(entry)+' --state '+str(ROOT/'lane')+' --preparation '+str(ROOT/'modal-preparation')
    if command not in loaded:
        raise ValueError('TRANSITION_OVERRIDE_NOT_LOADED')


def table_rows(db):
    # Preserve every row outside manual_state, including admission/accounting.
    names = sorted(r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='manual_state'"))
    if any(not n.replace('_', '').isalnum() for n in names):
        raise ValueError('UNEXPECTED_DATABASE_TABLE')
    return {n: [tuple(r) for r in db.execute('SELECT * FROM "' + n + '" ORDER BY rowid')] for n in names}


@private_records.private_umask
def apply(state, review_folder):
    state = Path(state)
    if state != ROOT / 'lane' or state.is_symlink():
        raise ValueError('EXACT_M3_STATE_PATH_REQUIRED')
    approved = approval(review_folder)
    dest = state / 'host-proof-reconciliation-20261003'
    if dest.exists():
        raise ValueError('RECONCILIATION_ALREADY_PREPARED_INSPECT_NO_RETRY')
    if (state/'HALT').exists():
        raise ValueError('HALT_REMAINS_EFFECTIVE')
    # Service/timer must be held by the recorded installation operation first.
    import subprocess
    for suffix in ['.service', '.timer']:
        active = subprocess.check_output(['/usr/bin/systemctl', 'show', ROOT.name+suffix, '-p', 'ActiveState', '--value'], text=True).strip()
        if active != 'inactive':
            raise ValueError('NEW_LANE_MUST_BE_HELD')
    installed_entrypoint()
    config_raw = (state/'lane.json').read_bytes()
    if sha(config_raw) != BINDINGS['config_sha256']:
        raise ValueError('ORIGINAL_CONFIG_CHANGED')
    config = json.loads(config_raw)
    for path in [state/'jobs.sqlite', state/'DECISION_REQUEST.md', Path(config['owner_path'])]:
        private_records.check(path)
    with lock(state/'one-run.lock'), lock(state/'driver.lock'):
        db = private_records.Connection(state/'jobs.sqlite')
        db.row_factory = sqlite3.Row
        value = json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
        calls = [dict(r) for r in db.execute('SELECT * FROM manual_calls')]
        for row in calls:
            row['receipt'] = json.loads(row['receipt'])
        spec_path = Path(value['spec'])
        if spec_path != ROOT/'lane-scientific-workspaces/run_spec_author-1/SPEC.proposed.md':
            raise ValueError('EXACT_SPEC_PATH_REQUIRED')
        validate(config, value, calls, spec_path.read_bytes())
        if json.loads(Path(config['owner_path']).read_text()) != config['owner_binding']:
            raise ValueError('OWNER_CHANGED')
        for name, expected in {**config['engine_files'], **config['scientific_files'], **config['profile_files']}.items():
            if sha((Path(config['root'])/name).read_bytes()) != expected:
                raise ValueError('BOUND_SOURCE_CHANGED')
        private_records.mkdir(dest)
        backup = private_records.Connection(dest/'before.sqlite'); db.backup(backup); backup.close()
        private_records.copyfile(state/'DECISION_REQUEST.md', dest/'DECISION_REQUEST.original.md')
        before = table_rows(db)
        intent = {'kind': 'PRE_ADMISSION_HOST_PROOF_RECONCILIATION', 'bindings': BINDINGS, 'before': value,
                  'approval_report_sha256': approved['report_sha256'], 'review_source': approved['source_sha'],
                  'reason': 'Use one native transition per fresh systemd invocation; completed author is not repeated',
                  'additional_calls': 0, 'additional_allowance': 0, 'original_source': config['source']}
        private_records.write_bytes(dest/'INTENT.json', canonical(intent))
        restored = dict(value)
        restored.update(phase='run_spec_review', reason=None,
                        interventions=value['interventions'] + [{k:v for k,v in intent.items() if k!='before'}])
        db.execute('BEGIN IMMEDIATE')
        try:
            if json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]) != value or table_rows(db) != before:
                raise ValueError('STATE_CHANGED_DURING_RECONCILIATION')
            db.execute('UPDATE manual_state SET payload=? WHERE id=1', (json.dumps(restored),))
            if table_rows(db) != before:
                raise ValueError('NON_STATE_ROWS_CHANGED')
            db.execute('COMMIT')
        except BaseException:
            db.execute('ROLLBACK')
            raise
        if (state/'lane.json').read_bytes() != config_raw:
            raise ValueError('CONFIGURATION_CHANGED')
        private_records.write_bytes(dest/'COMPLETE.json', canonical({'status':'PASS', 'state_sha256':sha(canonical(restored)),
                                     'all_other_database_rows_unchanged':True, 'config_sha256':sha(config_raw),
                                     'next':'run_spec_review under a new native root preflight; normal admission', 'calls_used':1}))
        # Keep the original request; supersession is explicit, not an erased block.
        db.close()
        return {'status':'RECONCILED', 'receipt':str(dest/'COMPLETE.json'), 'calls_used':1}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', required=True)
    parser.add_argument('--approval-folder', required=True)
    args = parser.parse_args()
    print(json.dumps(apply(args.state, args.approval_folder), sort_keys=True))


if __name__ == '__main__':
    main()
