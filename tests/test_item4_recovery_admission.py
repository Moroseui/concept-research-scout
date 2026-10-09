"""Real scratch release provenance and real item4 cost transaction, no provider.

The inherited fixture simulates root provenance and the fixed incident ID only.
Neither recovery validation nor admission is patched. The legacy synthetic
item4 owner is deliberate; canonical initialized owners have separate tests.
"""
import json
import pytest
from orchestrator import modal_direct_recovery as recovery
from orchestrator.modal_budget import ComputeAccounts
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from test_modal_direct_recovery import preserved
from test_direct_storage_continuation import prepared
from test_direct_storage_service import installed
from test_modal_ctp_download import planned
from test_modal_item4_budget import bound, reserve, item4


@pytest.fixture
def ready(preserved):
    root, cfg, batch, state, _ = preserved
    batch.filesystem_root = root
    accounts = ComputeAccounts(batch)
    original = recovery.parent(accounts, cfg, root=root)
    parent = original['binding']
    child = dict(parent, source=cfg['source'], recovery=cfg['recovery_from'])
    ident = digest(canonical(child))
    receipt = {'status':'VERIFIED','binding_sha256':ident,'recovery_of':recovery.PARENT}
    batch.db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,'READY',?,?)",
        (ident, child['run_id'], canonical(child).decode(),
         child['envelope']['cost']['reserved_micro_usd'], canonical(receipt).decode()))
    batch.db.execute("INSERT INTO autonomy_runs VALUES('item4',?,'ACTIVE')",
        (canonical({'backlog_item':4,'experiment_authority_sha256':item4.AUTHORITY}).decode(),))
    assert recovery.resolved_failure_ids(accounts, root=root) == {recovery.PARENT}
    yield batch, accounts, ident


def test_actual_item4_admission_accepts_verified_child_preserving_both_original_costs(ready):
    batch, accounts, child = ready
    before = [tuple(x) for x in batch.db.execute('SELECT * FROM autonomy_assets ORDER BY id')]
    assert reserve(accounts, bound())
    assert not reserve(accounts, bound())
    assert before == [tuple(x) for x in batch.db.execute('SELECT * FROM autonomy_assets ORDER BY id')]
    event = json.loads(batch.db.execute("SELECT payload FROM events WHERE id LIKE '%:gpu-reserved'").fetchone()[0])
    # Both original and recovery remain in the provider-headroom commitment.
    costs = sum(x[0] for x in batch.db.execute('SELECT reserved_micro_usd FROM autonomy_assets'))
    assert len(before) == 2 and costs > 0
    assert batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0] == 1
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0] == 0
    assert event['caps']['smoke'] == 75_000_000


@pytest.mark.parametrize('fault,code', [
    ('pending','MODAL_UNCERTAIN_ASSET_PREPARATION'),
    ('other','MODAL_UNCERTAIN_ASSET_PREPARATION'),
    ('receipt','DIRECT_RECOVERY_COMPLETION_BINDING'),
    ('cap','ITEM4_HARD_COST_CAP')])
def test_actual_item4_admission_keeps_recovery_evidence_and_all_cost_gates(ready,fault,code):
    batch,accounts,child=ready
    if fault=='pending':batch.db.execute("UPDATE autonomy_assets SET status='RUNNING' WHERE id=?",(child,))
    elif fault=='other':batch.db.execute("INSERT INTO autonomy_assets VALUES('other','other','{}','UNCERTAIN',1,'{}')")
    elif fault=='receipt':batch.db.execute("UPDATE autonomy_assets SET receipt='{}' WHERE id=?",(child,))
    else:
        # Additional same-run cost leaves enough room for this fit if either
        # original retrieval reservation were incorrectly omitted, not both.
        amounts=[x[0] for x in batch.db.execute('SELECT reserved_micro_usd FROM autonomy_assets')]
        amount=item4.SMOKE_CAP-bound()['cost']['reserved_micro_usd']-max(amounts)
        batch.db.execute("INSERT INTO autonomy_assets VALUES('cost','item4','{}','READY',?,'{}')",(amount,))
    before=list(batch.db.iterdump())
    with pytest.raises(ValueError,match='^'+code+'$'):reserve(accounts,bound())
    assert before==list(batch.db.iterdump())
