"""Deterministic permitted reports and durable fresh-review requests; no model calls."""
import argparse
from datetime import date
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import uuid

from orchestrator.public_export import text

FIELDS = {'job_id', 'status', 'source', 'attempt_id', 'wall_seconds', 'peak_rss_kib',
          'cpu_seconds', 'artifact_sha256', 'kind', 'backend', 'reason'}
MEASUREMENTS = {'wall_seconds', 'peak_rss_kib', 'cpu_seconds'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,128}', value):
        raise ValueError('INVALID_IDENTIFIER')
    return text(value)


def pin(value, size):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{'+str(size)+'}', value):
        raise ValueError('INVALID_PIN')
    return value


def sanitized(receipt):
    if not isinstance(receipt, dict) or set(receipt)-FIELDS:
        raise ValueError('RECEIPT_SCHEMA_REJECTED')
    result = dict.fromkeys(sorted(FIELDS))
    for key, value in receipt.items():
        if value is None:
            continue
        if key in MEASUREMENTS:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError('INVALID_MEASUREMENT')
        elif key == 'source':
            pin(value, 40)
        elif key == 'artifact_sha256':
            pin(value, 64)
        else:
            identifier(value)
        result[key] = value
    if not result['job_id'] or not result['status']:
        raise ValueError('JOB_ID_AND_STATUS_REQUIRED')
    text(json.dumps(result, sort_keys=True))
    return result


def private_root(root):
    root = Path(root).absolute()
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError('SYMLINK_ROOT_REJECTED')
    root.mkdir(parents=True, mode=0o700, exist_ok=True)
    if root.stat().st_uid != os.getuid() or root.stat().st_mode & 0o077:
        raise ValueError('PRIVATE_OWNER_ONLY_ROOT_REQUIRED')
    return root


def immutable(path, data):
    text(data.decode())
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        if path.is_symlink() or path.read_bytes() != data:
            raise ValueError('IMMUTABLE_OUTPUT_CONFLICT')
        return
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


class Queue:
    def __init__(self, root):
        self.root = private_root(root)
        path = self.root/'reports.sqlite'
        if path.is_symlink():
            raise ValueError('SYMLINK_DATABASE_REJECTED')
        self.db = sqlite3.connect(path, timeout=30, isolation_level=None)
        os.chmod(path, 0o600)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''PRAGMA journal_mode=WAL;
          CREATE TABLE IF NOT EXISTS reviews(
            id TEXT PRIMARY KEY, source TEXT NOT NULL, report_sha256 TEXT NOT NULL,
            status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
            attempt_id TEXT, reason TEXT, review_sha256 TEXT);
        ''')

    def status(self, report_id):
        pin(report_id, 64)
        row = self.db.execute('SELECT * FROM reviews WHERE id=?', (report_id,)).fetchone()
        if row is None:
            raise ValueError('UNKNOWN_REPORT')
        return dict(row)

    def claim(self, report_id):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row = self.status(report_id)
            if row['status'] not in ('QUEUED', 'NOT_REVIEWED') or row['attempts'] >= 3:
                self.db.execute('COMMIT')
                return None
            attempt = uuid.uuid4().hex
            self.db.execute("UPDATE reviews SET status='REVIEWING', attempts=attempts+1, attempt_id=?, reason=NULL WHERE id=?", (attempt, report_id))
            self.db.execute('COMMIT')
            return self.status(report_id)
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def unavailable(self, report_id, attempt_id, reason):
        identifier(reason)
        # Interrupted REVIEWING claims are never silently retried. The adapter must
        # explicitly reconcile and record unavailability using the existing attempt.
        result = self.db.execute("UPDATE reviews SET status='NOT_REVIEWED', reason=? WHERE id=? AND status='REVIEWING' AND attempt_id=?", (reason, report_id, attempt_id))
        if result.rowcount != 1:
            raise ValueError('STALE_REVIEW_ATTEMPT')
        return self.status(report_id)

    def attach(self, report_id, attempt_id, review_text, receipt):
        text(review_text)
        required = {'family', 'model', 'source', 'report_sha256', 'review_sha256',
                    'execution_receipt_sha256', 'session_id', 'status'}
        if not isinstance(receipt, dict) or set(receipt) != required:
            raise ValueError('REVIEW_RECEIPT_SCHEMA_REJECTED')
        if receipt['family'] != 'claude' or receipt['status'] != 'COMPLETE':
            raise ValueError('ACTUAL_CLAUDE_COMPLETION_REQUIRED')
        identifier(receipt['model']); identifier(receipt['session_id'])
        pin(receipt['execution_receipt_sha256'], 64)
        review_hash = digest(review_text.encode())
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row = self.status(report_id)
            if row['status'] != 'REVIEWING' or row['attempt_id'] != attempt_id:
                raise ValueError('STALE_REVIEW_ATTEMPT')
            if any(receipt[k] != row[k] for k in ('source', 'report_sha256')) or receipt['review_sha256'] != review_hash:
                raise ValueError('REVIEW_BINDING_MISMATCH')
            report_path = self.root/(report_id+'.md')
            if report_path.is_symlink() or digest(report_path.read_bytes()) != row['report_sha256']:
                raise ValueError('REPORT_CHANGED')
            payload = (json.dumps(receipt, sort_keys=True, indent=2)+'\n').encode()
            text(payload.decode())
            immutable(self.root/(report_id+'.claude-review.md'), review_text.encode())
            immutable(self.root/(report_id+'.claude-review.json'), payload)
            self.db.execute("UPDATE reviews SET status='REVIEWED', review_sha256=? WHERE id=?", (review_hash, report_id))
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise
        return self.status(report_id)

    def disposition(self, report_id, value):
        text(value)
        row = self.status(report_id)
        if row['status'] != 'REVIEWED':
            raise ValueError('REVIEW_REQUIRED')
        immutable(self.root/(report_id+'.astra-disposition.md'), value.encode())
        # Neither reviewer output nor disposition schedules another review.


def finalize(root, source, day, receipts, amendment_of=None):
    pin(source, 40)
    if date.fromisoformat(day).isoformat() != day:
        raise ValueError('INVALID_REPORT_DATE')
    if amendment_of is not None:
        pin(amendment_of, 64)
    if not isinstance(receipts, list) or len(receipts) > 1000:
        raise ValueError('RECEIPT_LIST_REQUIRED')
    rows = sorted((sanitized(r) for r in receipts), key=lambda r: json.dumps(r, sort_keys=True))
    receipt_bytes = (json.dumps(rows, sort_keys=True, indent=2)+'\n').encode()
    text(receipt_bytes.decode())
    receipt_hash = digest(receipt_bytes)
    counts = {'completed': 0, 'failed': 0, 'blocked': 0, 'other': 0}
    for row in rows:
        status = row['status'].upper()
        bucket = ('completed' if status in ('COMPLETE', 'COMPLETED', 'SUCCEEDED', 'VALIDATED')
                  else 'failed' if status in ('FAILED', 'FAILURE')
                  else 'blocked' if status in ('BLOCKED', 'NOT_REVIEWED', 'AUTH', 'PERMISSION') else 'other')
        counts[bucket] += 1
    def measured(value, unit):
        return 'unavailable' if value is None else f'{value:g} {unit}'
    table = '| Job | Status | Backend | Elapsed | CPU | Peak RSS |\n|---|---|---|---|---|---|\n'
    for row in rows:
        table += ('| '+row['job_id']+' | '+row['status']+' | '+(row['backend'] or 'unavailable')
                  +' | '+measured(row['wall_seconds'], 's')+' | '+measured(row['cpu_seconds'], 's')
                  +' | '+measured(row['peak_rss_kib'], 'KiB')+' |\n')
    dependencies = sorted({row['reason'] for row in rows if row['reason']})
    synthetic_only = bool(rows) and all(row['kind'] == 'synthetic' for row in rows)
    science = ('Only synthetic work is recorded; no patient experiment or measured scientific result is established.'
               if synthetic_only else 'Scientific progress is not established by these operational receipts; consult validated experiment results and interpretation artifacts.')
    body = (f'# Research system daily report — {day}\n\nSource: `{source}`.\n\n'
            +f"{counts['completed']} completed; {counts['failed']} failed; {counts['blocked']} blocked; {counts['other']} in other states.\n\n"
            + (f'Amendment of report `{amendment_of}`; original bytes remain preserved.\n\n' if amendment_of else '')
            + table+'\n'+science+'\n\n'
            + 'Human intervention, model usage and cost measurements: unavailable. '
            'The table preserves per-job measurements; overlapping jobs are not summed as elapsed time.\n\n'
            + ('Named dependencies: '+', '.join(dependencies)+'.\n\n' if dependencies else 'No named dependency was supplied; this does not prove all work is unblocked.\n\n')
            +f'Primary evidence: [{receipt_hash}.receipts.json]({receipt_hash}.receipts.json); SHA-256 `{receipt_hash}`.\n\n'
            + 'Next action: review the bound primary receipts and resolve their named dependencies. '
            'Phone delivery, unattended execution and fresh model review require separate evidence.\n')
    text(body)
    report_id = digest(body.encode())
    queue = Queue(root)
    if amendment_of is not None:
        queue.status(amendment_of)
    immutable(queue.root/(receipt_hash+'.receipts.json'), receipt_bytes)
    immutable(queue.root/(report_id+'.md'), body.encode())
    queue.db.execute("INSERT OR IGNORE INTO reviews(id,source,report_sha256,status) VALUES(?,?,?,'QUEUED')", (report_id, source, report_id))
    return queue.status(report_id)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['finalize', 'queue', 'status'])
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--source'); p.add_argument('--day'); p.add_argument('--receipts', type=Path)
    p.add_argument('--report-id'); p.add_argument('--amendment-of')
    a = p.parse_args()
    if a.action == 'finalize':
        if not a.receipts or not a.source or not a.day:
            p.error('finalize requires receipts, source and day')
        result = finalize(a.root, a.source, a.day, json.loads(a.receipts.read_text()), a.amendment_of)
    elif a.action == 'status':
        result = Queue(a.root).status(a.report_id)
    else:
        result = [dict(r) for r in Queue(a.root).db.execute('SELECT * FROM reviews ORDER BY id')]
    print(text(json.dumps(result, sort_keys=True)))


if __name__ == '__main__':
    main()
