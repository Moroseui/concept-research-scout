"""Preserve one proven unadmitted Colab review preparation before recomposition.

No model, provider, allowance, credential or scientific-output operation lives
here. The fixed runtime supplies the independently approved source binding.
"""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat

DOC = 'docs/COLAB_INTAKE_PREMODEL_PRIVATE.json'
DOC_SHA = '7f0a3b0f8fbbcc58762f044492ff62a51ec64485522a839fd5a7aae0610eaf4d'
LANE = Path('/var/lib/research-system-manual-sprint10-deployment/colab-preparation-20261010/lane')
LEDGER = Path('/var/lib/research-system-autonomy/reviews/jobs.sqlite')
DEST = LANE/'intake-identity-recovery-20261011'
REASON = 'ValueError: SEARCH_DUPLICATE_BINDING'


def require(ok, why):
    if not ok:
        raise ValueError('COLAB_INTAKE_RECOVERY_' + why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True).encode()


def binding():
    raw = (Path(__file__).resolve().parents[1]/DOC).read_bytes()
    require(sha(raw) == DOC_SHA, 'BINDING_CHANGED')
    return json.loads(raw)


def mapped(root, path):
    from tools.deploy_manual_lane import bound
    return bound(Path(root), str(path))


def raw(path):
    from orchestrator.private_records import check
    return check(path).read_bytes()


def authority():
    # Absent/uninstalled runtime fails closed; this draft cannot self-approve.
    from tools.colab_intake_identity_runtime import authority as verified
    return verified()


def service_owner():
    require(os.getuid() == os.getgid() == 1003, 'SERVICE_OWNER')


def inventory(work):
    from orchestrator import private_records as pr
    pr.check(work); require(work.is_dir(), 'WORKSPACE_ROOT')
    result = {}; directories = set()
    for path in sorted(work.rglob('*')):
        require(not path.is_symlink(), 'WORKSPACE_SYMLINK')
        st = path.lstat(); name = str(path.relative_to(work))
        if stat.S_ISDIR(st.st_mode):
            pr.check(path); directories.add(name)
        else:
            require(stat.S_ISREG(st.st_mode), 'WORKSPACE_FILE_TYPE')
            body = raw(path)
            result[name] = {'sha256': sha(body), 'bytes': len(body), 'mode': stat.S_IMODE(st.st_mode)}
    expected_dirs = {str(parent) for name in result for parent in Path(name).parents if str(parent) != '.'}
    require(directories == expected_dirs, 'WORKSPACE_DIRECTORY_MEMBERSHIP')
    return result


def rows(root):
    b = binding(); lane = mapped(root, LANE)
    require(sha(raw(lane/'lane.json')) == b['config_sha256'], 'CONFIG_CHANGED')
    require(json.loads(raw(lane/'lane.json'))['run_id'] == b['run_id'], 'RUN_CHANGED')
    with sqlite3.connect((lane/'jobs.sqlite').as_uri()+'?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        value = {name: [dict(r) for r in db.execute('SELECT * FROM '+name+' ORDER BY rowid')]
                 for name in ['manual_calls', 'manual_state', 'manual_account']}
    with sqlite3.connect(mapped(root, LEDGER).as_uri()+'?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        value['global_calls'] = [dict(r) for r in db.execute(
            'SELECT * FROM autonomy_calls WHERE change_id=? ORDER BY rowid', (b['run_id'],))]
        require(not db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(), 'RUNNING_CALL')
    require([r['id'] for r in value['manual_calls']] == b['row_ids']
            and [r['id'] for r in value['global_calls']] == b['row_ids'], 'ORIGINAL_CALL_SET')
    require(all(r['status'] == 'COMPLETE' for r in value['manual_calls']+value['global_calls']), 'ORIGINAL_CALL_STATUS')
    return value


def restored(original, approval):
    value = json.loads(original['manual_state'][0]['payload'])
    require(value['phase'] == 'BLOCKED' and value.get('reason') == REASON
            and value.get('blocked_stage') == 'run_spec_review' and not value.get('pending'), 'EXACT_PREMODEL_FAILURE')
    event = {'kind': 'UNADMITTED_REVIEW_PREPARATION_RECOVERY', 'binding_sha256': DOC_SHA,
             'review_sha256': approval['report_sha256'], 'new_allowance': 0, 'model_calls': 0}
    return {**value, 'phase': 'run_spec_review', 'reason': 'REVIEWED_INTAKE_IDENTITY_REPAIR',
            'interventions': [*value.get('interventions', []), event]}


def held_unit():
    import subprocess
    name = 'research-preparation-branch-admission-repair-20261010-colab_preparation.service'
    value = dict(line.split('=', 1) for line in subprocess.check_output(
        ['systemctl', 'show', name, '-p', 'MainPID', '-p', 'ActiveState', '-p', 'ExecMainStatus'], text=True).splitlines())
    require(value == {'MainPID': '0', 'ActiveState': 'inactive', 'ExecMainStatus': '0'}, 'PRIOR_UNIT_HELD')


def ready(root=Path('/')):
    approval = authority(); dest = mapped(root, DEST); b = binding()
    original = json.loads(raw(dest/'original-rows.json'))
    require(sha(canonical(original)) == b['rows_sha256'], 'ORIGINAL_SNAPSHOT_CHANGED')
    complete = {'status': 'READY_SAME_REVIEW_NO_CALL', 'binding_sha256': DOC_SHA,
                'review_sha256': approval['report_sha256'], 'original_rows_sha256': b['rows_sha256'],
                'workspace_inventory_sha256': b['workspace_inventory_sha256'], 'model_calls': 0, 'new_allowance': 0}
    require(json.loads(raw(dest/'COMPLETE.json')) == complete, 'COMPLETION_BINDING')
    require(inventory(dest/'workspace') == b['workspace_files'], 'ARCHIVE_CHANGED')
    require(not mapped(root, b['workspace']).exists(), 'FRESH_PREPARATION_REQUIRED')
    live = rows(root); expected = {**original, 'manual_state': [
        {**original['manual_state'][0], 'payload': json.dumps(restored(original, approval), sort_keys=True)}]}
    require(live == expected, 'RESTORED_ROWS_CHANGED')
    return complete


def apply(root=Path('/')):
    from orchestrator import private_records as pr
    from orchestrator.remote_supervisor import lock
    service_owner(); approval = authority(); b = binding()
    lane, dest, work = mapped(root, LANE), mapped(root, DEST), mapped(root, b['workspace'])
    require(not dest.exists() and not dest.is_symlink(), 'EXISTING_ATTEMPT_PRESERVED')
    require(not (lane/'HALT').exists() and not mapped(root, LEDGER.parent/'HALT').exists(), 'HALT_PRESERVED')
    held_unit()
    with lock(lane/'one-run.lock'), lock(lane/'driver.lock'):
        original = rows(root)
        require(sha(canonical(original)) == b['rows_sha256'], 'EXACT_ORIGINAL_ROWS')
        before = inventory(work)
        require(before == b['workspace_files'] and sha(canonical(before)) == b['workspace_inventory_sha256'], 'EXACT_WORKSPACE')
        after = restored(original, approval)
        pr.mkdir(dest)
        pr.write_bytes(dest/'original-rows.json', canonical(original))
        pr.write_bytes(dest/'INTENT.json', canonical({'after': after, 'review_sha256': approval['report_sha256']}))
        # Rename, not reconstruction or deletion: every original byte stays.
        work.rename(dest/'workspace')
        require(inventory(dest/'workspace') == before, 'ARCHIVE_READBACK')
        db = pr.Connection(lane/'jobs.sqlite'); db.row_factory = sqlite3.Row
        try:
            db.execute('BEGIN IMMEDIATE')
            for name in ['manual_calls', 'manual_state', 'manual_account']:
                require([dict(r) for r in db.execute('SELECT * FROM '+name+' ORDER BY rowid')] == original[name], 'STATE_RACE')
            db.execute('UPDATE manual_state SET payload=? WHERE id=1', (json.dumps(after, sort_keys=True),))
            db.execute('COMMIT')
        except BaseException:
            db.execute('ROLLBACK'); raise
        finally:
            db.close()
        complete = {'status': 'READY_SAME_REVIEW_NO_CALL', 'binding_sha256': DOC_SHA,
                    'review_sha256': approval['report_sha256'], 'original_rows_sha256': b['rows_sha256'],
                    'workspace_inventory_sha256': b['workspace_inventory_sha256'], 'model_calls': 0, 'new_allowance': 0}
        pr.write_bytes(dest/'COMPLETE.json', canonical(complete))
        return ready(root)
