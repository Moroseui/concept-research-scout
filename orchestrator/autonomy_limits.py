"""Operator-selected admission limits; count preserved rows, never reset usage."""
from pathlib import Path
import hashlib
import json

AUTHORITY = '38b3f7298f64f53396318b2e460c0b2a80013dcef2bcbd30168444c5f24609ff'
DOCUMENT = 'docs/LIMIT_OPERATOR_DECISION.txt'
DAILY_AUTHORITY = 'fcfaa8f3e3c17ffc0ea76c08e76177ddc3ed510a3456d019ad6ed2148283b48d'
DAILY_DOCUMENT = 'docs/DAILY_LIMIT_OPERATOR_DECISION_20261007.txt'
DAILY = 50
SCIENTIFIC_BATCH = 60
REVISE_ROUNDS = 3


def authority(root=None):
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    p = root / DOCUMENT
    if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest() != AUTHORITY:
        raise ValueError('LIMIT_OPERATOR_AUTHORITY_CHANGED')
    p = root / DAILY_DOCUMENT
    if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest() != DAILY_AUTHORITY:
        raise ValueError('DAILY_LIMIT_OPERATOR_AUTHORITY_CHANGED')
    return AUTHORITY


def selected_run_limit(config, run):
    """No larger allowance for legacy acceptance or an unclassified run."""
    authority()
    if config.get('run_id') != run:
        raise ValueError('LIMIT_RUN_BINDING')
    item = config.get('item_number')
    if type(item) is int and item == 6:
        from orchestrator.diagnostics_policy import validate_config
        return validate_config(config, run)
    if type(item) is int and item == 5 and config.get('backend') == 'analysis':
        from orchestrator.directions_analysis import authority as directions_authority
        directions_authority()
        return 16
    if type(item) is int and item == 2 and config.get('backend') == 'analysis':
        return 16
    if type(item) is int and item in (3, 4) and config.get('backend') in ('cpu', 'modal'):
        return 20
    return 6 if config.get('policy', {}).get('manual_semantics') == 'OPERATOR_SERVER_SPRINT10_MAX_SIX' else 8


def local_limit(store, run, policy):
    path = Path(store.path).parent / 'lane.json'
    if path.exists():
        return selected_run_limit(json.loads(path.read_bytes()), run)
    authority()
    return 6 if policy.get('manual_semantics') == 'OPERATOR_SERVER_SPRINT10_MAX_SIX' else 8


def global_limit(batch, run):
    authority()
    row = batch.db.execute('SELECT binding FROM autonomy_runs WHERE id=?', (run,)).fetchone()
    if row is None:
        raise ValueError('BATCH_ACTIVE_RUN_REQUIRED')
    owner = json.loads(row[0])
    state = owner.get('state')
    if not state:
        return 8
    from tools.deploy_manual_lane import bound
    path = bound(batch.filesystem_root, state) / 'lane.json'
    if not path.exists():
        return 8
    return selected_run_limit(json.loads(path.read_bytes()), run)


def allowance(store, run, policy):
    cap = local_limit(store, run, policy)
    if cap == 30:
        from orchestrator import diagnostics_policy as diagnostics
        return {'authority_sha256': diagnostics.authority(), 'run_limit': cap,
                'scoped_run_id': diagnostics.RUN_ID}
    return {'authority_sha256': AUTHORITY, 'run_limit': cap} if cap in (16, 20) else None


def cap_authority(cap):
    if cap == 30:
        from orchestrator.diagnostics_policy import authority as diagnostics_authority
        return diagnostics_authority()
    return authority()


def scientific_batch_allowance(batch, run, stage, ident, source, receipt):
    """Ordinary batch refusal; a reviewed installed scope may bind exact slots."""
    return {'limit': SCIENTIFIC_BATCH}
