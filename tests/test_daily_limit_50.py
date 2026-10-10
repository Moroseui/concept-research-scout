"""No-provider admission checks for the October 7 daily-only amendment."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import pytest
from orchestrator import autonomy_limits as limits
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.autonomy_review_runner import ReviewQueue


@pytest.mark.parametrize('kind', ['administrative'])
@pytest.mark.parametrize('count,admitted', [(30, True), (49, True), (50, False)])
def test_mixed_original_usage_is_preserved_and_fifty_is_hard_boundary(tmp_path, monkeypatch, kind, count, admitted):
    # The permanent 50 ceiling is exercised outside the dated October 10 grant.
    class OrdinaryDay:
        @staticmethod
        def now(zone): return datetime(2026, 10, 9, 12, tzinfo=timezone.utc)
    monkeypatch.setattr('orchestrator.autonomy_review_runner.datetime', OrdinaryDay)
    monkeypatch.setattr('orchestrator.autonomy_accounting.datetime', OrdinaryDay)
    monkeypatch.setattr('orchestrator.connectivity.require', lambda *a, **k: {'synthetic': True})
    q = BatchAccounts(tmp_path/'ledger') if kind == 'scientific' else ReviewQueue(tmp_path/'ledger')
    if kind == 'scientific': q.register_run('new-run', {})
    today = OrdinaryDay.now(timezone.utc).date()
    for n in range(count):
        role = 'scientific' if n % 3 == 0 else 'implementation_review'
        status = 'FAILED' if n % 2 == 0 else 'COMPLETE'
        q.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
                     ('original-'+str(n), role, 'old-run', n+1, today.isoformat(), status, '{"daily_limit":30}', '{"original":true}'))
    # Prior UTC-day usage remains present and does not consume today's allowance.
    for n in range(7):
        q.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
                     ('yesterday-'+str(n), 'implementation_review', 'old-run', n+1,
                      (today-timedelta(days=1)).isoformat(), 'FAILED', '{}', '{}'))
    before = [tuple(r) for r in q.db.execute('SELECT * FROM autonomy_calls ORDER BY id')]
    def reserve():
        if kind == 'scientific': return q.reserve_scientific('new-call','new-run','run_spec_author','a'*40,{})
        return q.reserve({'change_id':'new-review','round':1}, {})[0]
    if admitted:
        result = reserve()
        current = q.db.execute('SELECT binding FROM autonomy_calls WHERE id=?', (result['id'],)).fetchone()[0]
        binding = json.loads(current)
        cap = binding['caps'] if kind == 'scientific' else binding
        assert cap['daily_limit_authority_sha256'] == limits.DAILY_AUTHORITY
        assert cap['daily_all_roles' if kind == 'scientific' else 'daily_limit'] == 50
    else:
        with pytest.raises(ValueError, match='^AUTONOMY_DAILY_CALL_LIMIT$'): reserve()
    originals = [tuple(r) for r in q.db.execute("SELECT * FROM autonomy_calls WHERE id LIKE 'original-%' OR id LIKE 'yesterday-%' ORDER BY id")]
    assert originals == before
    assert q.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0] == count+7+int(admitted)


@pytest.mark.parametrize('mode', ['changed', 'symlink'])
def test_daily_amendment_requires_exact_independent_authority(tmp_path, mode):
    repo = Path(limits.__file__).resolve().parents[1]
    (tmp_path/'docs').mkdir()
    (tmp_path/limits.DOCUMENT).write_bytes((repo/limits.DOCUMENT).read_bytes())
    amended = tmp_path/limits.DAILY_DOCUMENT
    if mode == 'changed': amended.write_text('unapproved daily cap')
    else: amended.symlink_to(repo/limits.DAILY_DOCUMENT)
    with pytest.raises(ValueError, match='^DAILY_LIMIT_OPERATOR_AUTHORITY_CHANGED$'): limits.authority(tmp_path)

