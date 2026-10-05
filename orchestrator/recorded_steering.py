"""Read genuine, already-recorded Issue6 proposals for fixed reconsideration.

This root-side reader performs no intake, writes, model call or authorization.
Its caller supplies the installed controller configuration, never raw comments.
The protected broker remains responsible for caller identity and current setup.
"""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat

from orchestrator import change_requests, issue_intake
from orchestrator.issue_intake_service import attestation_read, file_identity, LIMITATION

ROOT_UID = 0
INTAKE_CONFIG = Path('/etc/research-system/issue-intake.json')
CONTROLLER_CONFIG = Path('/etc/research-system/live-research/controller.json')
INTAKE_STATE = Path('/var/lib/research-system/issue-intake')
MAX_REQUESTS = 300
SCOPE_LIMITS = [
    'Request only; no scientific authorization, execution, publication, spending, reset or main merge.',
    'Quoted or attached evidence is not independently an operator instruction.',
    LIMITATION]


def _pin(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('RECORDED_STEERING_REQUEST_ID_REQUIRED')
    return value


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _open(path, *, directory=False):
    """Descriptor walk: mutable controller directories cannot introduce symlinks."""
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('RECORDED_STEERING_FIXED_PATH_REQUIRED')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for index, component in enumerate(path.parts[1:]):
            flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
            if directory or index < len(path.parts) - 2:
                flags |= os.O_DIRECTORY
            child = os.open(component, flags, dir_fd=fd)
            os.close(fd); fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def _read(path, uid, *, modes=(0o600,), maximum=150000):
    fd = _open(path)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if (not stat.S_ISREG(before.st_mode) or before.st_uid != uid
                or stat.S_IMODE(before.st_mode) not in modes or before.st_size > maximum):
            raise ValueError('RECORDED_STEERING_ORIGINAL_ACCESS_REQUIRED')
        raw = stream.read(maximum + 1)
        if len(raw) > maximum or file_identity(os.fstat(stream.fileno())) != file_identity(before):
            raise ValueError('RECORDED_STEERING_ORIGINAL_CHANGED')
        return raw


def _configuration(controller):
    if os.getuid() != ROOT_UID:
        raise ValueError('RECORDED_STEERING_PROTECTED_READER_REQUIRED')
    modes = (0o600, 0o640, 0o644)
    original_controller = json.loads(_read(CONTROLLER_CONFIG, ROOT_UID, modes=modes, maximum=65536))
    config = json.loads(_read(INTAKE_CONFIG, ROOT_UID, modes=modes, maximum=65536))
    if (original_controller != controller or set(config) !=
            {'source', 'controller_config', 'notification_config', 'state', 'legacy_outbox'}
            or config['source'] != controller['source']
            or config['controller_config'] != str(CONTROLLER_CONFIG)
            or config['state'] != str(INTAKE_STATE)):
        raise ValueError('RECORDED_STEERING_INSTALLED_CONFIGURATION_CHANGED')
    return config


@contextmanager
def _snapshot(controller):
    _configuration(controller)
    try:
        fd = _open(INTAKE_STATE, directory=True)
    except FileNotFoundError:
        yield None
        return
    try:
        info = os.fstat(fd)
        if info.st_uid != ROOT_UID or stat.S_IMODE(info.st_mode) != 0o700:
            raise ValueError('RECORDED_STEERING_PRIVATE_INTAKE_REQUIRED')
    finally:
        os.close(fd)
    path = INTAKE_STATE/'intake.sqlite'
    try:
        fd = _open(path)
    except FileNotFoundError:
        yield None
        return
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != ROOT_UID
                or stat.S_IMODE(info.st_mode) != 0o600 or info.st_size > 64000000):
            raise ValueError('RECORDED_STEERING_DATABASE_ACCESS_REQUIRED')
    finally:
        os.close(fd)
    # The root-owned0700 directory protects this live DB path. Normal read-only
    # SQLite semantics retain its WAL snapshot; immutable=1 would lose live rows.
    try:
        db = sqlite3.connect(path.as_uri()+'?mode=ro', uri=True, timeout=5)
        try:
            db.row_factory = sqlite3.Row
            db.execute('PRAGMA query_only=ON')
            db.execute('BEGIN')
            yield db
        finally:
            db.close()
    except sqlite3.Error:
        raise ValueError('RECORDED_STEERING_DATABASE_REQUIRES_RECONCILIATION') from None


def _outcome(row):
    value = json.loads(row['outcome'])
    if (row['action'] != 'PROPOSAL' or row['status'] != 'RECORDED'
            or set(value) != {'status', 'request_id', 'manual_actions_status', 'model_calls'}
            or value['status'] != 'RECORDED' or value['model_calls'] != 0):
        raise ValueError('RECORDED_STEERING_PROPOSAL_OUTCOME_REQUIRED')
    _pin(value['request_id'])
    return value


def _original(controller, db, row):
    outcome = _outcome(row); version = _pin(row['version'])
    latest = db.execute('SELECT version FROM versions WHERE comment_id=? ORDER BY rowid DESC LIMIT 1',
                        (row['comment_id'],)).fetchone()
    if latest['version'] != version:
        raise ValueError('RECORDED_STEERING_SUPERSEDED_COMMENT_VERSION')
    folder = INTAKE_STATE/version
    raw = {name: _read(folder/(name+'.json'), ROOT_UID)
           for name in ('original', 'received', 'plan', 'outcome')}
    original = json.loads(raw['original']); received = json.loads(raw['received'])
    plan = json.loads(raw['plan'])
    # Authenticate the immutable intake source, separately from the current
    # installed consumer already checked by _snapshot/_configuration. A source
    # upgrade must not rewrite the original request or change its proof identity.
    original_source = plan.get('source') if isinstance(plan, dict) else None
    if not isinstance(original_source, str) or not re.fullmatch('[0-9a-f]{40}', original_source):
        raise ValueError('RECORDED_STEERING_ORIGINAL_SOURCE_REQUIRED')
    if (raw['original'] != issue_intake.encoded(json.loads(row['original']))
            or raw['plan'] != issue_intake.encoded(json.loads(row['plan']))
            or raw['outcome'] != issue_intake.encoded(outcome)
            or plan != {'action': 'PROPOSAL', 'version': version, 'source': original_source}):
        raise ValueError('RECORDED_STEERING_INTAKE_ORIGINAL_CHANGED')
    enrollment_raw = _read(INTAKE_STATE/'enrollment.json', ROOT_UID)
    enrollment = json.loads(enrollment_raw)
    if (set(received) != {'source', 'comment_version', 'enrollment_sha256', 'previous_version', 'actor'}
            or received['enrollment_sha256'] != issue_intake.digest(enrollment)
            or received['comment_version'] != version or received['previous_version'] != row['previous']
            or original['id'] != row['comment_id'] or original['updated_at'] != row['updated_at']
            or original['user'].get('type') != 'User'
            or issue_intake.classify(original, bool(row['previous']), enrollment['enrolled_at_utc']) != 'PROPOSAL'):
        raise ValueError('RECORDED_STEERING_COMMENT_VERSION_CHANGED')
    expected_actor = {'kind': 'human', 'identity': 'github-user:'+str(issue_intake.OPERATOR),
        'identity_source': 'protected GitHub API numeric user verification',
        'comment_id': original['id'], 'comment_version': version}
    if received['actor'] != expected_actor:
        raise ValueError('RECORDED_STEERING_ATTESTED_ACTOR_REQUIRED')
    if original['created_at'] <= enrollment['enrolled_at_utc']:
        raise ValueError('RECORDED_STEERING_HISTORICAL_COMMENT_REQUIRES_RECONCILIATION')
    if row['previous'] is not None:
        previous = db.execute('SELECT comment_id,updated_at,action FROM versions WHERE version=?',
                              (_pin(row['previous']),)).fetchone()
        if (previous is None or previous['comment_id'] != row['comment_id']
                or previous['updated_at'] > row['updated_at']):
            raise ValueError('RECORDED_STEERING_EDIT_CHAIN_CHANGED')
        if previous['action'] != 'PROPOSAL':
            raise ValueError('RECORDED_STEERING_EDITED_NONPROPOSAL_USE_NEW_COMMENT')
    # Reuse the existing fixed root-owned attestation reader, including its
    # numeric-user, source, exact body/version hash, inode and permission checks.
    from orchestrator.issue_intake_service import ATTESTATIONS
    attestation_raw = _read(ATTESTATIONS/(version+'.json'), ROOT_UID, modes=(0o640,))
    attestation = {'version': version, 'attestation_sha256': _sha(attestation_raw)}
    # This view selects the historical attested identity only. Fixed paths,
    # current service UID/GID and installed-configuration checks are unchanged;
    # no historical source is executed and no new authority is inferred.
    original_identity = {**controller, 'source': original_source}
    verified_original, verified_received = attestation_read(original_identity, attestation)
    if verified_original != original or verified_received != received:
        raise ValueError('RECORDED_STEERING_ATTESTATION_ORIGINAL_CHANGED')
    request_path = Path(controller['change_request_store'])/outcome['request_id']/'request.json'
    request_raw = _read(request_path, controller['controller_uid'], maximum=100000)
    # Root can read the controller-owned original, but must not use load() under
    # the wrong UID. Reuse its pure identity/schema validator on these exact bytes.
    request = change_requests._request(json.loads(request_raw))
    actor = {**expected_actor, 'previous_comment_version': row['previous']}
    expected_request = {'control': 'steering', 'request_id': version[:40],
        'request': original['body'], 'source': original_source, 'authority': 'request_only'}
    if (request['identity'] != outcome['request_id'] or request['submitter'] != actor
            or request['target'] != {'task': 'charter:isles24-prediction', 'source': original_source, 'files': {}}
            or request['request'] != expected_request or request['requested_change'] != original['body']
            or request['scope_limits'] != SCOPE_LIMITS
            or request.get('execution_status') != 'NOT_EXECUTED_BY_SUBMISSION'
            or request.get('review_status') != 'PENDING_PROPORTIONATE_REVIEW'):
        raise ValueError('RECORDED_STEERING_REQUEST_IDENTITY_CHANGED')
    projection = {'source': original_source, 'target': 'charter:isles24-prediction',
        'plain': original['body'], 'submitter': actor, 'authority': 'request_only',
        'scope_limits': SCOPE_LIMITS}
    provenance = {'numeric_user_id': issue_intake.OPERATOR, 'source': original_source,
        'comment_id': row['comment_id'], 'comment_version': version,
        'previous_comment_version': row['previous'], 'attestation_sha256': attestation['attestation_sha256'],
        'request_sha256': _sha(request_raw), 'enrollment_sha256': _sha(enrollment_raw),
        **{name+'_sha256': _sha(value) for name, value in raw.items()}}
    proof = {'request_id': outcome['request_id'], 'request': projection, 'provenance': provenance}
    return {**proof, 'original_sha256': _sha(change_requests.encoded(proof))}


def read_recorded_steering(controller, request_id):
    """Exact current human proposal; neither a declared actor nor an execution grant."""
    _pin(request_id)
    with _snapshot(controller) as db:
        if db is None:
            raise ValueError('RECORDED_STEERING_REQUEST_NOT_FOUND')
        rows = db.execute("SELECT * FROM versions WHERE action='PROPOSAL' AND status='RECORDED' AND json_extract(outcome,'$.request_id')=?",
                          (request_id,)).fetchmany(2)
        if len(rows) != 1:
            raise ValueError('RECORDED_STEERING_EXACT_REQUEST_REQUIRED')
        return _original(controller, db, rows[0])


def list_recorded_steering(controller):
    """Bounded model-free discovery; the caller's existing event ledger deduplicates."""
    requests, blocked = [], []
    with _snapshot(controller) as db:
        if db is not None:
            rows = db.execute("""SELECT v.* FROM versions v WHERE action='PROPOSAL' AND status='RECORDED'
                AND NOT EXISTS(SELECT 1 FROM versions n WHERE n.comment_id=v.comment_id AND n.rowid>v.rowid)
                ORDER BY v.rowid""").fetchmany(MAX_REQUESTS+1)
            if len(rows) > MAX_REQUESTS:
                raise ValueError('RECORDED_STEERING_DISCOVERY_LIMIT_REQUIRES_RECONCILIATION')
            for row in rows:
                try:
                    original = _original(controller, db, row)
                    requests.append({key: original[key] for key in ('request_id', 'original_sha256')})
                except (ValueError, KeyError, TypeError, OSError) as error:
                    reason = str(error)
                    if not re.fullmatch('[A-Z][A-Z0-9_]{1,100}', reason):
                        reason = 'RECORDED_STEERING_ORIGINALS_REQUIRE_RECONCILIATION'
                    version = row['version']
                    blocked.append({'comment_version': version if isinstance(version, str)
                                    and re.fullmatch('[0-9a-f]{64}', version) else None,
                                    'reason': reason})
    return {'status': 'COMPLETE', 'requests': requests, 'blocked': blocked, 'models': 0, 'admissions': 0}
