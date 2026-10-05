"""Bounded Issue6 intake and deterministic replies; no model or dispatch entry point.

The protected service authenticates API responses. Originals and every edit remain
private. Receipt replies never claim investigator assessment or scientific approval.
"""
from datetime import datetime, timezone
import hashlib
import os
import json
import re
import sqlite3
from pathlib import Path

from orchestrator.operations_report import private_root, immutable
from orchestrator.phone_notifications import REPO, positive
from orchestrator.public_export import text

ISSUE = 6
OPERATOR = 157774170
BOT = 325760728
BASE = '/repos/' + REPO
ISSUE_URL = 'https://api.github.com' + BASE + '/issues/6'
MAX_PAGES = 3
MAX_ATTEMPTS = 3


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True) + '\n').encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def private_original(path, value):
    raw = encoded(value)
    if len(raw) > 150000:
        raise ValueError('COMMENT_ORIGINAL_SIZE_LIMIT')
    if path.exists():
        if path.is_symlink() or path.read_bytes() != raw:
            raise ValueError('COMMENT_ORIGINAL_CHANGED')
        return
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


def checked_comment(value):
    positive(value.get('id'))
    if value.get('issue_url') != ISSUE_URL:
        raise ValueError('COMMENT_ISSUE_MISMATCH')
    user = value.get('user', {})
    positive(user.get('id'))
    body = value.get('body')
    if not isinstance(body, str) or len(body.encode()) > 65536:
        raise ValueError('COMMENT_BODY_LIMIT')
    for key in ('created_at', 'updated_at'):
        if not isinstance(value.get(key), str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value[key]):
            raise ValueError('COMMENT_TIMESTAMP_REQUIRED')
    if value['updated_at'] < value['created_at']:
        raise ValueError('COMMENT_TIMESTAMP_ORDER')
    return value


CONTROL = re.compile(r'/research (status|pause|resume)(?: revision (0|[1-9][0-9]{0,17}))?')


def classify(comment, prior=False, cutoff=None):
    body = comment['body'].strip()
    match = CONTROL.fullmatch(body)
    if match:
        if cutoff is not None and comment['created_at'] <= cutoff:
            return 'HISTORICAL_CONTROL'
        if prior or comment['created_at'] != comment['updated_at']:
            return 'EDITED_CONTROL'
        action, revision = match.groups()
        if action == 'status':
            return 'status' if revision is None else 'UNSUPPORTED_CONTROL_OR_QUOTE'
        return action if revision is not None else 'CONTROL_REVISION_REQUIRED'
    if body.startswith('/research') or body.startswith(('>', '```')):
        return 'UNSUPPORTED_CONTROL_OR_QUOTE'
    if re.fullmatch(r'ACK system-[0-9a-f]{32} [0-9a-f]{32} [0-9a-f]{64}', body):
        return 'HISTORICAL_ACK'
    return 'PROPOSAL'


def comments(call):
    """Fetch all bounded pages before processing; do not lose a later page silently."""
    found = []
    for page in range(1, MAX_PAGES + 1):
        result = call('GET', BASE + '/issues/6/comments?per_page=100&page=' + str(page))
        if not isinstance(result, list):
            raise ValueError('COMMENT_LIST_REQUIRED')
        # Other authors cannot create steering or reply-reconciliation inputs.
        found.extend(checked_comment(item) for item in result
                     if item.get('user', {}).get('id') in (OPERATOR, BOT))
        if len(result) < 100:
            return sorted(found, key=lambda item: item['id'])
    raise ValueError('COMMENT_PAGE_LIMIT_RECONCILE_WITHOUT_EXECUTION')


class Intake:
    def __init__(self, root, source, *, enrolled_at=None):
        if not re.fullmatch('[0-9a-f]{40}', source):
            raise ValueError('INTAKE_SOURCE_REQUIRED')
        self.root = private_root(root)
        self.source = source
        path = self.root / 'enrollment.json'
        if path.exists():
            if path.is_symlink(): raise ValueError('INTAKE_ENROLLMENT_CHANGED')
            enrollment = json.loads(path.read_text())
        else:
            enrollment = {'schema': 'issue6-intake-enrollment/v1', 'source': source,
                          'enrolled_at_utc': enrolled_at or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
        if (set(enrollment) != {'schema', 'source', 'enrolled_at_utc'} or
                enrollment['schema'] != 'issue6-intake-enrollment/v1' or
                not re.fullmatch('[0-9a-f]{40}', enrollment['source']) or
                not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', enrollment['enrolled_at_utc'])):
            raise ValueError('INTAKE_ENROLLMENT_CHANGED')
        immutable(path, encoded(enrollment))
        self.enrollment = enrollment
        self.db = sqlite3.connect(self.root / 'intake.sqlite', isolation_level=None, timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
          CREATE TABLE IF NOT EXISTS versions(
            version TEXT PRIMARY KEY, comment_id INTEGER, updated_at TEXT, original TEXT,
            previous TEXT, action TEXT, status TEXT, plan TEXT, outcome TEXT, attempts INTEGER);
          CREATE TABLE IF NOT EXISTS replies(
            version TEXT PRIMARY KEY, body TEXT, state TEXT, attempts INTEGER, comment_id INTEGER);
          CREATE TABLE IF NOT EXISTS api_attempts(
            sequence INTEGER PRIMARY KEY, method TEXT, path TEXT, outcome TEXT);
        """)

    def api(self, call, method, path, body=None):
        # A distinct API attempt record does not alter the research ledger.
        row = self.db.execute('INSERT INTO api_attempts(method,path,outcome) VALUES(?,?,?)',
                              (method, path, 'STARTED'))
        try:
            result = call(method, path, body)
        except Exception:
            self.db.execute('UPDATE api_attempts SET outcome=? WHERE sequence=?',
                            ('FAILED_OR_UNCERTAIN', row.lastrowid))
            raise
        self.db.execute('UPDATE api_attempts SET outcome=? WHERE sequence=?', ('RETURNED', row.lastrowid))
        return result

    def receive(self, comment):
        comment = checked_comment(comment)
        # Do not trust owner association or display names; never ingest own replies.
        if comment['user']['id'] != OPERATOR or comment['user'].get('type') != 'User':
            return None
        version = digest({'repository': REPO, 'issue': ISSUE, 'id': comment['id'],
                          'updated_at': comment['updated_at'], 'body': comment['body']})
        if self.db.execute('SELECT 1 FROM versions WHERE version=?', (version,)).fetchone():
            return version
        prior = self.db.execute('SELECT version,updated_at FROM versions WHERE comment_id=? ORDER BY rowid DESC LIMIT 1',
                                (comment['id'],)).fetchone()
        if prior and prior['updated_at'] > comment['updated_at']:
            raise ValueError('COMMENT_VERSION_ROLLBACK')
        folder = private_root(self.root / version)
        # Preserve raw user input privately. Unsafe request projection is refused
        # by the existing change-request guard without echoing it publicly.
        private_original(folder / 'original.json', comment)
        record = {'source': self.source, 'comment_version': version,
                  'enrollment_sha256': digest(self.enrollment),
                  'previous_version': prior['version'] if prior else None,
                  'actor': {'kind': 'human', 'identity': 'github-user:' + str(OPERATOR),
                            'identity_source': 'protected GitHub API numeric user verification',
                            'comment_id': comment['id'], 'comment_version': version}}
        immutable(folder / 'received.json', encoded(record))
        self.db.execute('INSERT INTO versions VALUES(?,?,?,?,?,?,?,?,?,0)',
                        (version, comment['id'], comment['updated_at'], encoded(comment).decode(),
                         record['previous_version'], classify(comment, bool(prior), self.enrollment['enrolled_at_utc']), 'RECEIVED', None, None))
        return version

    def process(self, version, operations):
        row = self.db.execute('SELECT * FROM versions WHERE version=?', (version,)).fetchone()
        if not row:
            raise ValueError('SAVED_COMMENT_REQUIRED')
        folder = self.root / version
        original = json.loads(row['original'])
        if (folder / 'original.json').read_bytes() != encoded(original):
            raise ValueError('COMMENT_ORIGINAL_CHANGED')
        received = json.loads((folder / 'received.json').read_text())
        if (received['comment_version'] != version or received['previous_version'] != row['previous'] or
                received['actor']['identity'] != 'github-user:' + str(OPERATOR) or
                received['actor']['comment_id'] != original['id'] or
                received['actor']['comment_version'] != version or
                received.get('enrollment_sha256') != digest(self.enrollment)):
            raise ValueError('COMMENT_RECEIPT_CHANGED')
        if row['outcome'] is not None:
            outcome = json.loads(row['outcome'])
            if (folder / 'outcome.json').read_bytes() != encoded(outcome):
                raise ValueError('COMMENT_OUTCOME_CHANGED')
            self.queue_reply(version, outcome)
            return outcome
        if row['attempts'] >= MAX_ATTEMPTS:
            return {'status': 'BLOCKED', 'reason': 'INTAKE_ATTEMPT_LIMIT_RECONCILE_ORIGINAL'}
        # Preserve each planned operation before applying it. Recovery uses the same
        # revision/idempotency key even after a later human control changed state.
        self.db.execute('UPDATE versions SET attempts=attempts+1 WHERE version=?', (version,))
        if row['plan'] is None:
            plan_path = folder / 'plan.json'
            plan = (json.loads(plan_path.read_text()) if plan_path.exists()
                    else operations.prepare(row['action'], original, received))
            immutable(plan_path, encoded(plan))
            self.db.execute('UPDATE versions SET plan=? WHERE version=?', (encoded(plan).decode(), version))
        else:
            plan = json.loads(row['plan'])
            if (folder / 'plan.json').read_bytes() != encoded(plan):
                raise ValueError('COMMENT_PLAN_CHANGED')
        result_path = folder / 'outcome.json'
        outcome = (json.loads(result_path.read_text()) if result_path.exists()
                   else operations.apply(plan, original, received))
        immutable(result_path, encoded(outcome))
        self.db.execute('UPDATE versions SET status=?,outcome=? WHERE version=?',
                        (outcome['status'], encoded(outcome).decode(), version))
        self.queue_reply(version, outcome)
        return outcome

    def queue_reply(self, version, outcome):
        row = self.db.execute('SELECT comment_id FROM versions WHERE version=?', (version,)).fetchone()
        if not row:
            raise ValueError('SAVED_COMMENT_REQUIRED')
        status = outcome['status']
        if status == 'RECORDED':
            message = ('Received and recorded as request `' + outcome['request_id'] +
                       '`; awaiting investigator assessment. No scientific approval or execution is implied.')
        elif status == 'HISTORICAL_ACKNOWLEDGED':
            message = 'Received and recorded as a historical report acknowledgment. It does not request new research or control execution.'
        elif status == 'CONTROL_COMPLETE':
            message = ('Recorded control: ' + outcome['action'] + '; ' +
                       ('paused' if outcome['paused'] else 'not paused') +
                       '; revision ' + str(outcome['revision']) +
                       '. Pause prevents new admissions; it does not terminate active jobs.')
            if 'current_revision' in outcome:
                message += (' Latest readback: ' + ('paused' if outcome['current_paused'] else 'not paused') +
                            '; revision ' + str(outcome['current_revision']) + '.')
        elif status == 'STATUS':
            message = ('Saved status: ' + ('paused' if outcome['paused'] else 'not paused') +
                       '; revision ' + str(outcome['revision']) +
                       '; ' + str(outcome['task_count']) + ' recorded coordinator tasks. No model was called.')
        else:
            message = ('Received; action is blocked: ' + outcome.get('reason', 'RECONCILIATION_REQUIRED') +
                       '. Post /research status, then a new unquoted /research pause revision N or /research resume revision N using the observed revision; other plain text is recorded for investigator assessment.')
        body = ('Research system (deterministic service, not an investigator assessment).\n\n' +
                'Regarding https://github.com/' + REPO + '/issues/6#issuecomment-' + str(row['comment_id']) +
                ': ' + message + '\n\nSaved intake: `' + version + '`.\n<!-- research-intake:' + version + ' -->')
        text(body)
        old = self.db.execute('SELECT body FROM replies WHERE version=?', (version,)).fetchone()
        if old and old['body'] != body:
            raise ValueError('REPLY_BINDING_CHANGED')
        self.db.execute('INSERT OR IGNORE INTO replies VALUES(?,?,?,0,NULL)', (version, body, 'READY'))

    def deliver(self, version, call, observed):
        row = self.db.execute('SELECT * FROM replies WHERE version=?', (version,)).fetchone()
        if not row or row['state'] == 'SENT':
            return {'status': 'SENT' if row else 'NO_REPLY', 'duplicate': bool(row)}
        # Reconcile an uncertain POST, including after process death. Never issue a
        # second POST just because the initiating connection failed.
        matches = [item for item in observed if item['user']['id'] == BOT and item['body'] == row['body']]
        if len(matches) > 1:
            raise ValueError('DUPLICATE_REPLY_REQUIRES_RECONCILIATION')
        if matches:
            result = matches[0]
        elif row['state'] != 'READY':
            if row['attempts'] >= MAX_ATTEMPTS:
                return {'status': 'BLOCKED_NO_REPOST'}
            self.db.execute('UPDATE replies SET attempts=attempts+1,state=? WHERE version=?',
                            ('BLOCKED' if row['attempts'] + 1 >= MAX_ATTEMPTS else 'UNCERTAIN', version))
            return {'status': 'UNCERTAIN_NO_REPOST'}
        else:
            self.db.execute('UPDATE replies SET state=?,attempts=attempts+1 WHERE version=?', ('UNCERTAIN', version))
            result = self.api(call, 'POST', BASE + '/issues/6/comments', {'body': row['body']})
        checked_comment(result)
        if (result['user']['id'] != BOT or result['body'] != row['body'] or
                result['created_at'] != result['updated_at']):
            raise ValueError('POSTED_REPLY_BINDING_CHANGED')
        immutable(self.root / version / 'reply.json', encoded(result))
        self.db.execute('UPDATE replies SET state=?,comment_id=? WHERE version=?', ('SENT', result['id'], version))
        return {'status': 'SENT', 'comment_id': result['id']}

    def status(self):
        return {'source': self.source, 'model_calls': 0, 'research_admissions': 0,
                'requests': [dict(row) for row in self.db.execute(
                    'SELECT version,comment_id,previous,action,status,attempts FROM versions ORDER BY rowid')],
                'replies': [dict(row) for row in self.db.execute(
                    'SELECT version,state,attempts,comment_id FROM replies ORDER BY rowid')],
                'api_attempts': self.db.execute('SELECT count(*) FROM api_attempts').fetchone()[0]}
