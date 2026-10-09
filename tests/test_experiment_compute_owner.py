"""Actual initializer -> actual SQLite compute admission; no provider/model calls.

Reuse the labelled synthetic engine-approval/native-preflight fixtures. Neither
the owner verifier nor either accounting path is patched.
"""
import json
import pytest
from orchestrator import experiment_driver as ed, experiment_context as ec
from orchestrator.manual_executor import read, atomic, digest
from orchestrator.modal_executor import canonical
from orchestrator.modal_budget import ComputeAccounts
from orchestrator import private_records as pr
from test_experiment_driver import prepared, init, prepare_item4
from test_analysis_driver import initialization, analysis_lane
from test_manual_lane import lane, root, ROOT
from test_modal_item4_budget import bound, snapshot, NOW


@pytest.fixture
def actual(prepared, monkeypatch):
    prepare_item4(prepared, monkeypatch)
    init(prepared)
    d = ed.ExperimentDriver(prepared[0].state/'new-experiment')
    d.guard()
    b = bound()
    b.update(run_id=d.config['run_id'], source=d.config['source'],
        execution_plan_sha256=d.config['execution_scope']['plan_sha256'])
    yield d, b
    d.store.db.close(); d.store.batch.db.close()


def reserve(d, b):
    return ComputeAccounts(d.store.batch).reserve_item4(digest(canonical(b)), b['run_id'], b,
        billing_snapshot=snapshot(), now=NOW)


def test_initialized_owner_admits_compute_once_without_new_scientific_allowance(actual):
    d, b = actual
    before = [tuple(r) for r in d.store.batch.db.execute('SELECT * FROM autonomy_runs')]
    calls = [tuple(r) for r in d.store.batch.db.execute('SELECT * FROM autonomy_calls')]
    assert reserve(d, b) is True
    assert reserve(d, b) is False
    assert before == [tuple(r) for r in d.store.batch.db.execute('SELECT * FROM autonomy_runs')]
    assert calls == [tuple(r) for r in d.store.batch.db.execute('SELECT * FROM autonomy_calls')]
    rows = d.store.batch.db.execute('SELECT * FROM autonomy_compute').fetchall()
    assert len(rows) == 1 and rows[0]['run'] == ec.ITEM4_RUN
    assert rows[0]['reserved_micro_usd'] == b['cost']['reserved_micro_usd']


@pytest.mark.parametrize('change', ['lane-owner', 'plan-bytes', 'config-source', 'review-pin',
    'execution-source', 'execution-plan', 'legacy-canonical-owner', 'wrong-run', 'item6-scope'])
def test_owner_or_execution_drift_refuses_before_cost_reservation(actual, change):
    d, b = actual
    code = 'ITEM4_EXPERIMENT_OWNER_CHANGED'
    if change in {'lane-owner', 'config-source', 'review-pin'}:
        cfg = read(d.state/'lane.json')
        if change == 'lane-owner': cfg['owner_binding'] = {}
        elif change == 'config-source': cfg['source'] = '0'*40
        else: cfg['engine_review']['sha256'] = '0'*64
        atomic(d.state/'lane.json', cfg)
    elif change == 'plan-bytes':
        pr.write_bytes(d.state/'preparation-plan.json', (d.state/'preparation-plan.json').read_bytes()+b' ')
    elif change.startswith('execution-'):
        b['source' if change == 'execution-source' else 'execution_plan_sha256'] = '0'*(40 if change == 'execution-source' else 64)
        code = 'ITEM4_EXECUTION_OWNER_BINDING'
    elif change == 'legacy-canonical-owner':
        from orchestrator.modal_item4_policy import AUTHORITY
        d.store.batch.db.execute('UPDATE autonomy_runs SET binding=? WHERE id=?',
            (json.dumps({'backlog_item':4, 'experiment_authority_sha256':AUTHORITY}), b['run_id']))
        code = 'ITEM4_EXPERIMENT_OWNER_REQUIRED'
    elif change == 'wrong-run':
        old = b['run_id']; b['run_id'] = 'other'
        d.store.batch.db.execute('UPDATE autonomy_runs SET id=? WHERE id=?', (b['run_id'], old))
        code = 'ITEM4_EXPERIMENT_OWNER_REQUIRED'
    else:
        cfg = read(d.state/'lane.json'); cfg['execution_scope']['item_number'] = 6
        atomic(d.state/'lane.json', cfg)
    with pytest.raises(ValueError, match='^'+code+'$'): reserve(d, b)
    assert not d.store.batch.db.execute('SELECT 1 FROM autonomy_compute').fetchone()


def test_real_owner_still_refuses_scientific_uncertainty(actual):
    d, b = actual
    d.store.batch.db.execute("INSERT INTO autonomy_calls VALUES('uncertain','scientific','other',1,'2026-10-06','UNCERTAIN','{}',NULL)")
    with pytest.raises(ValueError, match='^BATCH_UNCERTAIN_OR_RUNNING_CALL$'): reserve(d, b)
    assert not d.store.batch.db.execute('SELECT 1 FROM autonomy_compute').fetchone()
