"""Operator-selected admission limits; count preserved rows, never reset usage."""
from pathlib import Path
import hashlib
import json

AUTHORITY = '38b3f7298f64f53396318b2e460c0b2a80013dcef2bcbd30168444c5f24609ff'
DOCUMENT = 'docs/LIMIT_OPERATOR_DECISION.txt'
DAILY_AUTHORITY = 'fcfaa8f3e3c17ffc0ea76c08e76177ddc3ed510a3456d019ad6ed2148283b48d'
DAILY_DOCUMENT = 'docs/DAILY_LIMIT_OPERATOR_DECISION_20261007.txt'
DAILY = 50
TEMPORARY_DAY = '2026-10-10'
TEMPORARY_DAILY = 100
TEMPORARY_AUTHORITY = '644410e1659c8998040c3cc9035aaa0eb2c5c3708fba37cfbb1a91fadf9f00e6'
TEMPORARY_DOCUMENT = 'docs/OPERATOR_DIRECTION_20261010.txt'
TONIGHT_DAY = '2026-10-12'
TONIGHT_DAILY = 100
TONIGHT_DOCUMENT = 'docs/COLAB_TONIGHT_OPERATOR_20261012.txt'
TONIGHT_AUTHORITY = '23a45f2fdf214ba69f808393973fb5b6bff38a72a50dd6601106647a919e4cbd'
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


def daily_allowance(day, root=None):
    """Select from the admission transaction's UTC day, never process start time.

    A past or future day has the original limit. No caller-selected cap and no
    ledger mutation occurs here. The temporary operator direction is mandatory
    only when its increased allowance would be used.
    """
    from datetime import date
    authority(root)
    if type(day) is not str or date.fromisoformat(day).isoformat() != day:
        raise ValueError('DAILY_ADMISSION_DATE_REQUIRED')
    if day == TONIGHT_DAY:
        root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
        p = root / TONIGHT_DOCUMENT
        if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest() != TONIGHT_AUTHORITY:
            raise ValueError('TONIGHT_DAILY_AUTHORITY_CHANGED')
        return {'limit': TONIGHT_DAILY, 'authority_sha256': TONIGHT_AUTHORITY}
    if day != TEMPORARY_DAY:
        return {'limit': DAILY, 'authority_sha256': DAILY_AUTHORITY}
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    p = root / TEMPORARY_DOCUMENT
    if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest() != TEMPORARY_AUTHORITY:
        raise ValueError('TEMPORARY_DAILY_AUTHORITY_CHANGED')
    return {'limit': TEMPORARY_DAILY, 'authority_sha256': TEMPORARY_AUTHORITY}


def selected_run_limit(config, run):
    """No larger allowance for legacy acceptance or an unclassified run."""
    authority()
    if config.get('run_id') != run:
        raise ValueError('LIMIT_RUN_BINDING')
    if 'colab_simple_full' in config:
        from orchestrator import colab_simple_full as full
        scope=full.document()
        if run!=full.RUN or config['colab_simple_full']!={'schema':'colab-simple-full-preparation/v1','scope_sha256':full.DOCUMENT_SHA}:
            raise ValueError('COLAB_FULL_LIMIT_SCOPE')
        return scope['call_limit']
    from orchestrator import colab_arm_question as question
    if question.selected(config):
        if run != question.RUN:
            raise ValueError('COLAB_ARM_LIMIT_RUN_CHANGED')
        return question.validate_scope(config)['call_limit']
    from orchestrator import meeting_preparation as meeting
    if meeting.selected(config):
        return meeting.validate_config(config, run)['call_limit']
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
    from orchestrator import colab_simple_full as full
    event=batch.db.execute('SELECT payload FROM events WHERE id=?',(full.EVENT,)).fetchone() if run==full.RUN else None
    if event is not None:
        scope=full.document()
        config=json.loads((full._path(batch.filesystem_root,scope['new_lane'])/'lane.json').read_bytes())
        if json.loads(event[0])!=full._grant(config,scope,full._approval(config,scope,batch.filesystem_root)):
            raise ValueError('COLAB_FULL_GLOBAL_APPROVAL_CHANGED')
        return scope['call_limit']
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
