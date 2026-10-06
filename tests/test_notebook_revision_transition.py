"""No model calls: continuation paths and preserved checkpoint contracts."""
from pathlib import Path
import pytest
from orchestrator.stocktake_recovery import ledger_folder
from orchestrator.notebook_revision_transition import checkpoint, KEY


def test_notebook_scratch_ledger_never_resolves_to_live_path(tmp_path):
    config={'notebook_revision_continuation':KEY,'notebook_filesystem_root':str(tmp_path),
            'batch_ledger':'/var/lib/research-system-autonomy/reviews'}
    assert ledger_folder(config)==tmp_path/'var/lib/research-system-autonomy/reviews'
    config.pop('notebook_filesystem_root')
    with pytest.raises(KeyError):ledger_folder(config)


def test_notebook_live_ledger_keeps_existing_owner_path():
    config={'notebook_revision_continuation':KEY,'notebook_filesystem_root':'/',
            'batch_ledger':'/var/lib/research-system-autonomy/reviews'}
    assert ledger_folder(config)==Path(config['batch_ledger'])


def test_frozen_four_call_checkpoint_is_not_a_new_allowance():
    value=checkpoint()
    assert len(value['call_rows'])==4
    assert set(value['call_rows'])==set(value['global_rows'])
    assert value['run_id']=='stocktake-6b556dba36d299c05b8b7770'
    assert value['halt_sha256'] and value['tables']['manual_account']


def test_analysis_driver_maps_owner_lookup_to_same_scratch_root(tmp_path):
    from orchestrator.analysis_driver import AnalysisDriver
    from orchestrator.manual_executor import atomic
    from orchestrator import private_records
    state=tmp_path/'lane';private_records.mkdir(state)
    atomic(state/'lane.json',{'backend':'analysis','root':str(tmp_path/'repository'),
        'context':str(tmp_path/'context'),'notebook_revision_continuation':KEY,
        'notebook_filesystem_root':str(tmp_path),'batch_ledger':'/ledger'})
    driver=AnalysisDriver(state)
    assert driver.store.batch.folder==tmp_path/'ledger'
    assert driver.store.batch.filesystem_root==tmp_path
    driver.store.db.close();driver.store.batch.db.close()


def _stub_frozen_predecessors(monkeypatch, root):
    """Unit plumbing only; real frozen-checkpoint preflight is a server gate."""
    from orchestrator import notebook_revision_transition as current
    from orchestrator import analysis_revision_transition as earlier
    calls=[]
    monkeypatch.setattr(current,'checkpoint',lambda:{'run_id':'same-run','old_state':'/var/lib/research-system-manual-sprint10/releases/four/lane'})
    monkeypatch.setattr(earlier,'checkpoint',lambda:{'run_id':'same-run','old_state':'/var/lib/research-system-manual-sprint10/releases/two/lane'})
    monkeypatch.setattr(current,'prior',lambda host:(calls.append(('four',host)) or ({'revision_continuation':earlier.KEY},{})))
    monkeypatch.setattr(earlier,'prior',lambda host:calls.append(('two',host)))
    return current,earlier,calls


def test_promotion_preserves_both_verified_predecessor_generations(tmp_path,monkeypatch):
    current,earlier,calls=_stub_frozen_predecessors(monkeypatch,tmp_path)
    paths=current.preserved_predecessors(tmp_path)
    assert paths==[tmp_path/'var/lib/research-system-manual-sprint10/releases/four/lane',tmp_path/'var/lib/research-system-manual-sprint10/releases/two/lane']
    assert calls==[('four',tmp_path),('two',tmp_path)]


def test_promotion_refuses_changed_ancestor_checkpoint(tmp_path,monkeypatch):
    current,earlier,_=_stub_frozen_predecessors(monkeypatch,tmp_path)
    def changed(host):raise ValueError('REVISION_OLD_ROWS_CHANGED:manual_calls')
    monkeypatch.setattr(earlier,'prior',changed)
    with pytest.raises(ValueError,match='^REVISION_OLD_ROWS_CHANGED:manual_calls$'):
        current.preserved_predecessors(tmp_path)


@pytest.mark.parametrize('which',['link','run','alias'])
def test_promotion_refuses_unbound_predecessor_chain(tmp_path,monkeypatch,which):
    current,earlier,_=_stub_frozen_predecessors(monkeypatch,tmp_path)
    if which=='link':monkeypatch.setattr(current,'prior',lambda host:({'revision_continuation':'unrelated'},{}))
    elif which=='run':monkeypatch.setattr(earlier,'checkpoint',lambda:{'run_id':'other-run','old_state':'/different/lane'})
    else:monkeypatch.setattr(earlier,'checkpoint',lambda:current.checkpoint())
    with pytest.raises(ValueError,match='^NOTEBOOK_PREDECESSOR_CHAIN_CHANGED$'):
        current.preserved_predecessors(tmp_path)


def test_native_promotion_guard_accepts_only_verified_chain(tmp_path,monkeypatch):
    import sqlite3,json
    from orchestrator import private_records,completed_run
    from tools.manual_promotion import require_uninitialized_lane
    current,earlier,_=_stub_frozen_predecessors(monkeypatch,tmp_path)
    allowed=current.preserved_predecessors(tmp_path)
    monkeypatch.setattr(completed_run,'closed_lanes',lambda root:set())
    def lane(path):
        private_records.mkdir(path,parents=True)
        private_records.write_text(path/'lane.json','{}')
        with sqlite3.connect(path/'jobs.sqlite') as db:
            db.execute('CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT)')
            db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps({'phase':'BLOCKED'}),))
            db.execute('CREATE TABLE manual_calls(status TEXT)')
            db.execute('INSERT INTO manual_calls VALUES(?)',('COMPLETE',))
    for path in allowed:lane(path)
    # This reproduces the installed refusal when only the latest is selected.
    with pytest.raises(ValueError,match='^INITIALIZED_LANE_REQUIRES_SEPARATE_REVIEWED_MIGRATION_NO_BUDGET_RESET$'):
        require_uninitialized_lane(tmp_path,allowed[:1])
    require_uninitialized_lane(tmp_path,allowed)
    other=tmp_path/'var/lib/research-system-manual-sprint10/releases/unrelated/lane';lane(other)
    with pytest.raises(ValueError,match='^INITIALIZED_LANE_REQUIRES_SEPARATE_REVIEWED_MIGRATION_NO_BUDGET_RESET$'):
        require_uninitialized_lane(tmp_path,allowed)
