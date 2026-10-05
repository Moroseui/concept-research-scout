"""One held same-run continuation after a completed REVISE recorder collision.

Copies preserved state as its owner. No call retry, new owner, allowance reset,
ledger-row edit or altered scientific output is permitted.
"""
import json
import os
from pathlib import Path
import sqlite3
from orchestrator import private_records, autonomy_limits, analysis_revisions
from orchestrator.manual_executor import read, digest, inventory, atomic, lock
from orchestrator.stocktake_recovery import connect
from tools.deploy_manual_lane import bound

CHECKPOINT = '248ccca5690f4fcb8bdbc8d0bb1082f219a652c310377ba78c82ceee2937e768'
KEY = 'stocktake-6b556dba36d299c05b8b7770:scoped-revision-continuation'


def sha(value):
    # The preserved checkpoint producer uses compact canonical JSON.
    return digest(json.dumps(value, sort_keys=True, separators=(',', ':')).encode())


def rows(db, table):
    if table not in {'manual_calls','manual_state','manual_account','manual_recoveries'}:
        raise ValueError('REVISION_TABLE_REQUIRED')
    # The frozen producer orders each table by its first (primary-key) column.
    return [dict(row) for row in db.execute('SELECT * FROM '+table+' ORDER BY 1')]


def checkpoint():
    p = Path(__file__).resolve().parents[1]/'docs/ITEM2_REVISION_CHECKPOINT.json'
    if digest(p.read_bytes()) != CHECKPOINT:
        raise ValueError('REVISION_CHECKPOINT_CHANGED')
    return read(p)


def prior(host, *, completed=False):
    p = checkpoint(); old = bound(host, p['old_state'])
    if old.is_symlink() or (old/'HALT').exists():
        raise ValueError('REVISION_OLD_HALTED_OR_ALIAS')
    if digest((old/'lane.json').read_bytes()) != p['config_sha256']:
        raise ValueError('REVISION_CONFIG_CHANGED')
    c = read(old/'lane.json')
    if c['source'] != p['old_source'] or c['run_id'] != p['run_id'] or c['item_number'] != 2:
        raise ValueError('REVISION_OLD_IDENTITY')
    if digest((old/'preparation-plan.json').read_bytes()) != p['plan_sha256']:
        raise ValueError('REVISION_PLAN_CHANGED')
    if digest(bound(host, c['owner_path']).read_bytes()) != p['owner_sha256']:
        raise ValueError('REVISION_OWNER_CHANGED')
    if sha(inventory(old/'context')) != p['context_sha256']:
        raise ValueError('REVISION_CONTEXT_CHANGED')
    with connect(old/'jobs.sqlite') as db:
        for table, expected in p['tables'].items():
            if sha(rows(db, table)) != expected:
                raise ValueError('REVISION_OLD_ROWS_CHANGED:' + table)
        v = json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
        if v['phase'] != 'BLOCKED' or v['reason'] != 'OUTPUT_VALIDATION_REFUSED: EXISTING_FINDING_CONFLICT':
            raise ValueError('REVISION_COMPLETED_REVIEW_REQUIRED')
        if digest((bound(host, v['pending']['workspace'])/'review.json').read_bytes()) != p['review_sha256']:
            raise ValueError('REVISION_SAVED_REVIEW_CHANGED')
    with connect(bound(host, c['batch_ledger'])/'jobs.sqlite') as db:
        for ident, expected in p['global_rows'].items():
            row = db.execute('SELECT * FROM autonomy_calls WHERE id=?', (ident,)).fetchone()
            if row is None or sha(dict(row)) != expected:
                raise ValueError('REVISION_GLOBAL_CALL_CHANGED')
        owner = db.execute('SELECT * FROM autonomy_runs WHERE id=?', (p['run_id'],)).fetchone()
        owner_value=dict(owner) if owner is not None else {}
        if completed and owner_value.get('status')=='COMPLETE':
            owner_value['status']='ACTIVE'
        if sha(owner_value) != p['global_owner_sha256']:
            raise ValueError('REVISION_GLOBAL_OWNER_CHANGED')
        if db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone():
            raise ValueError('REVISION_ACTIVE_CALL')
    return c, v


def promotion_check(host, previous, source, entrypoint, report):
    autonomy_limits.authority(source); p = checkpoint(); prior(host)
    if (entrypoint != 'analysis' or previous['source'] != p['old_source']
            or previous['state'] + '/lane' != p['old_state']
            or digest((Path(source)/'deploy/manual-lane/runtime.promotion.json').read_bytes()) != previous['runtime_sha256']):
        raise ValueError('REVISION_PROMOTION_SCOPE')
    return bound(host, p['old_state'])


def validate_driver(driver):
    value = read(driver.state/'revision-continuation.json')
    if value['run_id'] != checkpoint()['run_id'] or value['kind'] != KEY:
        raise ValueError('REVISION_CONTINUATION_SCOPE')
    if sha(driver.config) != value['config_sha256']:
        raise ValueError('REVISION_CONTINUATION_CONFIG_CHANGED')
    if value['state'] != str(driver.state.resolve()) or value['source'] != driver.config['source']:
        raise ValueError('REVISION_CONTINUATION_DESTINATION')
    row = driver.store.batch.db.execute('SELECT payload FROM events WHERE id=?', (KEY,)).fetchone()
    if row is None or row[0] != json.dumps(value, sort_keys=True):
        raise ValueError('REVISION_CONTINUATION_LEDGER_BINDING')
    autonomy_limits.authority(driver.root)
    prior(Path(value['filesystem_root']), completed=driver.current()['phase']=='COMPLETE')


@private_records.private_umask
def prepare(state, root, report, *, filesystem_root=Path('/')):
    from tools import manual_promotion, deploy_manual_lane as deploy
    from orchestrator.manual_driver import git, write_once
    from orchestrator.analysis_driver import release_identities
    from orchestrator.autonomy_review import verify_result
    host = Path(filesystem_root).resolve(); state, root, report = map(Path, (state, root, report))
    if host == Path('/') and os.getuid() != 1003:
        raise ValueError('REVISION_OWNER_REQUIRED')
    if any(not p.resolve().is_relative_to(host) for p in (state, root, report)):
        raise ValueError('REVISION_PATH_ESCAPE')
    if state.exists() or state.is_symlink():
        raise ValueError('REVISION_EXISTING_DESTINATION')
    with lock(state.parent/'revision-continuation.lock'):
        before, current = prior(host); p = checkpoint(); old = bound(host, p['old_state'])
        autonomy_limits.authority(root)
        head = git(root, 'rev-parse', 'HEAD'); branch = git(root, 'branch', '--show-current')
        approved = verify_result(report.parent)
        if (approved['verdict'] != 'APPROVE' or approved['source_sha'] != head
                or approved['report_sha256'] != digest(report.read_bytes())):
            raise ValueError('REVISION_EXACT_APPROVAL_REQUIRED')
        selected = read(bound(host, manual_promotion.POINTER))
        runtime_hash = digest(Path(os.environ['RESEARCH_MANUAL_RUNTIME_CONFIG']).read_bytes())
        if (git(root, 'status', '--porcelain') or not branch.startswith('astra/manual-server-')
                or root.resolve() != bound(host, selected['state'])/'repository'
                or state.resolve() != bound(host, selected['state'])/'lane'
                or selected['source'] != head or selected['runtime_sha256'] != runtime_hash
                or approved['runtime_sha256'] != runtime_hash):
            raise ValueError('REVISION_HELD_INSTALL_REQUIRED')
        for unit in selected['units'] + [Path(p['old_state']).parent.name + x for x in ('.service', '.timer')]:
            if deploy.system(host, 'state', unit) != {'enabled': False, 'active': False}:
                raise ValueError('REVISION_UNITS_NOT_HELD')
        ledger = bound(host, before['batch_ledger'])/'jobs.sqlite'
        with connect(ledger) as db:
            if db.execute('SELECT 1 FROM events WHERE id=?', (KEY,)).fetchone():
                raise ValueError('REVISION_ALREADY_CONTINUED')
        if (ledger.parent/'HALT').exists():
            raise ValueError('AUTONOMY_BATCH_HALTED')
        config = {**before, 'source': head, 'root': str(root.resolve()), 'branch': branch,
            'context': str(state/'context'), 'owner_path': str(bound(host, before['owner_path'])),
            'revision_filesystem_root': str(host), 'workspace_root': str(state.parent/'lane-scientific-workspaces'),
            'engine_review': {'path': str(report.resolve()), 'sha256': digest(report.read_bytes())},
            'revision_policy': analysis_revisions.POLICY, 'revision_continuation': KEY}
        config['profile_files'], config['engine_files'] = release_identities(root)
        if config['profile_files'] != before['profile_files']:
            raise ValueError('REVISION_PROFILE_CHANGED')
        value = {'kind': KEY, 'run_id': p['run_id'], 'source': head, 'state': str(state.resolve()),
            'filesystem_root': str(host), 'config_sha256': sha(config), 'checkpoint_sha256': CHECKPOINT,
            'operator_decision_sha256': autonomy_limits.AUTHORITY, 'original_source': p['old_source'],
            'preserved_call_ids': list(p['call_rows']), 'allowance_reset': False}
        write_once(state.parent/'revision-continuation-intent.json', json.dumps(value, sort_keys=True).encode())
        private_records.mkdir(state)
        for path in old.iterdir():
            if path.name in {'jobs.sqlite', 'jobs.sqlite-wal', 'jobs.sqlite-shm', 'lane.json'}: continue
            if path.is_dir(): private_records.copytree(path, state/path.name)
            else: private_records.copyfile(path, state/path.name)
        with connect(old/'jobs.sqlite') as src, sqlite3.connect(state/'jobs.sqlite') as dst:
            src.backup(dst)
        atomic(state/'lane.json', config)
        atomic(state/'revision-continuation.json', value)
        with sqlite3.connect('file:'+str(ledger)+'?mode=rw', uri=True) as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('INSERT INTO events VALUES(?,?,?)', (KEY, p['run_id'], json.dumps(value, sort_keys=True)))
        prior(host); private_records.check_tree(state)
        return {'status': 'CONTINUED_NO_CALL_OR_RESET', 'calls_used': 2, 'call_limit': 16, 'source': head}


@private_records.private_umask
def accept_saved_review(state):
    from orchestrator.analysis_driver import AnalysisDriver
    d = AnalysisDriver(state)
    with lock(Path(state)/'driver.lock'):
        validate_driver(d); v = d.current()
        if v['phase'] != 'BLOCKED' or v['reason'] != 'OUTPUT_VALIDATION_REFUSED: EXISTING_FINDING_CONFLICT':
            raise ValueError('REVISION_EXACT_PENDING_REQUIRED')
        d.guard()
        result = d.accept_completed(v)
        if result['phase'] != 'run_spec_author':
            raise ValueError('REVISION_SAVED_OUTCOME_NOT_ROUTED')
        return result
