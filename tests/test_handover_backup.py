"""A restored handover sample preserves task state and original evidence bytes."""
import sqlite3
import pytest
from orchestrator.operations_backup import backup_handover,restore_handover


def test_consistent_database_and_original_evidence_restore(tmp_path):
    state=tmp_path/'state';turns=tmp_path/'turns';state.mkdir();turns.mkdir()
    for path in (state/'branch.lock',state/'admission.lock',turns/'branch.lock'):path.touch()
    (state/'reports').mkdir()
    for name in ('coordinator.sqlite','reports/reports.sqlite'):
        with sqlite3.connect(state/name) as db:
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('CREATE TABLE specimen(value TEXT)')
            db.execute('INSERT INTO specimen VALUES(?)',('completed original',))
    (turns/'original.stdout').write_bytes(b'Original synthetic console\n')
    backup=tmp_path/'backup';restored=tmp_path/'restored'
    assert backup_handover(state,turns,backup)['authority_restored'] is False
    assert restore_handover(backup,restored)['models_started']==0
    assert (restored/'turns/original.stdout').read_bytes()==b'Original synthetic console\n'
    with sqlite3.connect(restored/'state/coordinator.sqlite') as db:
        assert db.execute('SELECT value FROM specimen').fetchone()[0]=='completed original'
    (backup/'turns/original.stdout').write_bytes(b'changed')
    with pytest.raises(ValueError,match='IDENTITY_MISMATCH'):
        restore_handover(backup,tmp_path/'must-not-exist')
    assert not (tmp_path/'must-not-exist').exists()
