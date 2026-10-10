"""Real local admission with synthetic rows; no provider or live ledger."""
from datetime import datetime, timezone
from pathlib import Path
import json
import pytest
from orchestrator import autonomy_limits as limits
from orchestrator import autonomy_accounting as accounting
from orchestrator import autonomy_review_runner as reviewer


class Clock:
    day = '2026-10-10'
    @classmethod
    def now(cls, zone):
        assert zone is timezone.utc
        return datetime.fromisoformat(cls.day + 'T12:00:00+00:00')


def queue(tmp_path, monkeypatch, day, kind, count):
    Clock.day = day
    monkeypatch.setattr(accounting, 'datetime', Clock)
    monkeypatch.setattr(reviewer, 'datetime', Clock)
    monkeypatch.setattr('orchestrator.connectivity.require', lambda *a, **k: {'synthetic': True})
    q = accounting.BatchAccounts(tmp_path/'ledger')
    q.register_run('new-run', {})
    for n in range(count):
        q.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
            ('original-'+str(n), 'scientific' if n % 3 == 0 else 'implementation_review',
             'old-run', n+1, day, 'FAILED' if n % 2 else 'COMPLETE',
             '{"daily_limit":30}', '{"original":true}'))
    q.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
        ('prior-day', 'implementation_review', 'past-run', 1, '2026-10-08', 'COMPLETE', '{}', '{}'))
    return q


def reserve(q, kind, suffix=''):
    if kind == 'scientific':
        return q.reserve_scientific('new-call'+suffix, 'new-run', 'run_spec_author', 'a'*40, {})
    return q.reserve({'change_id':'new-review'+suffix, 'round':1}, {})[0]


@pytest.mark.parametrize('kind', ['scientific', 'administrative'])
@pytest.mark.parametrize('day,count,admit', [
    ('2026-10-09',49,True), ('2026-10-09',50,False),
    ('2026-10-10',50,True), ('2026-10-10',99,True), ('2026-10-10',100,False),
    ('2026-10-11',49,True), ('2026-10-11',50,False),
    ('2027-10-10',50,False)])
def test_boundaries_preserve_every_original(tmp_path, monkeypatch, kind, day, count, admit):
    q = queue(tmp_path, monkeypatch, day, kind, count)
    before = [tuple(r) for r in q.db.execute('SELECT * FROM autonomy_calls ORDER BY id')]
    if admit:
        result = reserve(q, kind)
        raw = q.db.execute('SELECT binding FROM autonomy_calls WHERE id=?', (result['id'],)).fetchone()[0]
        binding = json.loads(raw)
        cap = binding['caps'] if kind == 'scientific' else binding
        effective = limits.daily_allowance(day)
        assert cap['daily_all_roles' if kind == 'scientific' else 'daily_limit'] == effective['limit']
        assert cap['daily_limit_authority_sha256'] == effective['authority_sha256']
    else:
        with pytest.raises(ValueError, match='^AUTONOMY_DAILY_CALL_LIMIT$'):
            reserve(q, kind)
    after = [tuple(r) for r in q.db.execute("SELECT * FROM autonomy_calls WHERE id LIKE 'original-%' OR id='prior-day' ORDER BY id")]
    assert after == before
    assert q.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0] == count+1+int(admit)


@pytest.mark.parametrize('kind', ['scientific', 'administrative'])
def test_long_lived_process_uses_new_utc_day(tmp_path, monkeypatch, kind):
    q = queue(tmp_path, monkeypatch, '2026-10-10', kind, 99)
    reserve(q, kind)
    # Closed first call and 50 immutable next-day rows; same imports/process.
    q.db.execute("UPDATE autonomy_calls SET status='COMPLETE' WHERE status='RUNNING'")
    for n in range(50):
        q.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
            ('next-day-'+str(n), 'implementation_review', 'other-run', n+1,
             '2026-10-11', 'COMPLETE', '{}', '{}'))
    Clock.day = '2026-10-11'
    with pytest.raises(ValueError, match='^AUTONOMY_DAILY_CALL_LIMIT$'):
        reserve(q, kind, '-next')


@pytest.mark.parametrize('mode', ['missing', 'changed', 'symlink'])
def test_increase_needs_exact_operator_authority(tmp_path, mode):
    root = Path(limits.__file__).resolve().parents[1]
    (tmp_path/'docs').mkdir()
    for name in (limits.DOCUMENT, limits.DAILY_DOCUMENT):
        (tmp_path/name).write_bytes((root/name).read_bytes())
    p = tmp_path/limits.TEMPORARY_DOCUMENT
    if mode == 'changed': p.write_text('unapproved')
    if mode == 'symlink': p.symlink_to(root/limits.TEMPORARY_DOCUMENT)
    with pytest.raises((ValueError, FileNotFoundError)):
        limits.daily_allowance('2026-10-10', tmp_path)
    assert limits.daily_allowance('2026-10-11', tmp_path)['limit'] == 50


@pytest.mark.parametrize('day', ['20261010', '2026-10-10T00:00:00Z', None, 20261010])
def test_no_ambiguous_dates(day):
    with pytest.raises((ValueError, TypeError)):
        limits.daily_allowance(day)


@pytest.mark.parametrize('which', ['batch', 'run'])
def test_other_admission_caps_still_refuse(tmp_path, monkeypatch, which):
    q = queue(tmp_path, monkeypatch, '2026-10-10', 'scientific', 0)
    count = 60 if which == 'batch' else 8
    for n in range(count):
        q.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
            ('cap-row-'+str(n), 'scientific', 'new-run' if which == 'run' else 'old-run',
             n+1, '2026-10-09', 'COMPLETE', '{}', '{}'))
    with pytest.raises(ValueError, match='^AUTONOMY_'+which.upper()+'_CALL_LIMIT$'):
        reserve(q, 'scientific')
    assert limits.DAILY == 50 and limits.SCIENTIFIC_BATCH == 60 and limits.REVISE_ROUNDS == 3
