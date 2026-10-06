"""Operator-selected admission limits; count preserved rows, never reset usage."""
from pathlib import Path
import hashlib
import json

AUTHORITY = '38b3f7298f64f53396318b2e460c0b2a80013dcef2bcbd30168444c5f24609ff'
DOCUMENT = 'docs/LIMIT_OPERATOR_DECISION.txt'
DAILY = 30
SCIENTIFIC_BATCH = 60
REVISE_ROUNDS = 3


def authority(root=None):
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    p = root / DOCUMENT
    if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest() != AUTHORITY:
        raise ValueError('LIMIT_OPERATOR_AUTHORITY_CHANGED')
    return AUTHORITY


def selected_run_limit(config, run):
    """No larger allowance for legacy acceptance or an unclassified run."""
    authority()
    if config.get('run_id') != run:
        raise ValueError('LIMIT_RUN_BINDING')
    item = config.get('item_number')
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
