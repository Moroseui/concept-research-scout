"""Actual private SQLite admission; synthetic billing, no provider/model calls."""
import copy
from datetime import timedelta
import json
import pytest
from orchestrator import modal_environment_budget as budget, modal_direct_budget as direct
from orchestrator import modal_item4_policy as policy, modal_terminal_cost as terminal
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_assets import BASE_IMAGE
from orchestrator.modal_budget import ComputeAccounts
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from orchestrator.modal_billing import canonical as compact
from test_modal_direct_budget import billing, NOW


def binding(view):
    return {"purpose":budget.PURPOSE,"operation_id":budget.OPERATION,
        "authority_sha256":policy.AUTHORITY,"team_authority_sha256":policy.TEAM_AUTHORITY,
        "run_id":budget.RUN,"source":"a"*40,"installed_config_sha256":"b"*64,
        "worker_sha256":"c"*64,"image_id":"im-synthetic", "base_image":BASE_IMAGE,
        "envelope":budget.envelope(view["rates"])}


@pytest.fixture
def prepared(tmp_path):
    batch=BatchAccounts(tmp_path/"ledger");accounts=ComputeAccounts(batch)
    view=billing();value=binding(view);batch.register_run(budget.RUN,budget.owner(value))
    yield batch,accounts,value,view
    batch.db.close()


def reserve(f, **kw):
    _,accounts,value,view=f
    return budget.reserve(accounts,digest(canonical(value)),value["run_id"],value,
                          billing_snapshot=view,now=kw.get("now",NOW))


def seal(view):
    body=dict(view);body.pop("sha256",None);view["sha256"]=digest(compact(body));return view


def asset(batch, amount, ident="download", status="READY"):
    value={"purpose":direct.PURPOSE,"authority_sha256":policy.AUTHORITY,
           "download_authority_sha256":direct.DOWNLOAD_AUTHORITY}
    batch.db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,?,?,NULL)",
                     (ident,"old-inputs",canonical(value).decode(),status,amount))


def compute(batch, amount, ident="fit", stage="SMOKE", status="COLLECTED", run="old-item4"):
    value={"purpose":"M4_ITEM4","run_id":run,"experiment":{"backlog_item":4,
        "authority_sha256":policy.AUTHORITY,"team_authority_sha256":policy.TEAM_AUTHORITY,
        "fit_id":ident,"stage":stage,"segment":1,"billing_object_id":"ap-"+ident}}
    batch.db.execute("INSERT INTO autonomy_compute VALUES(?,?,?,?,?,?,NULL,?)",
        (ident,run,canonical(value).decode(),status,amount,"sb-"+ident,"2026-10"))
    return value


def test_one_operation_keeps_full_charge_and_has_no_scientific_allowance(prepared):
    batch,accounts,b,view=prepared
    assert reserve(prepared) is True
    amount=b["envelope"]["cost"]["reserved_micro_usd"]
    assert amount>budget.OVERHEAD_MICRO and b["envelope"]["resources"]["gpu"] is None
    old=[tuple(x) for x in batch.db.execute("SELECT * FROM autonomy_assets")]
    assert reserve(prepared) is False
    assert [tuple(x) for x in batch.db.execute("SELECT * FROM autonomy_assets")]==old
    ident=digest(canonical(b));accounts.finish_assets(ident,"READY",{"status":"VERIFIED","synthetic_fixture":True})
    batch.complete_run(budget.RUN,{"administrative_only":True})
    assert reserve(prepared) is False
    row=batch.db.execute("SELECT * FROM autonomy_assets WHERE id=?",(ident,)).fetchone()
    assert budget.selected_asset(row) and row["reserved_micro_usd"]==amount
    owner=json.loads(batch.db.execute("SELECT binding FROM autonomy_runs WHERE id=?",(budget.RUN,)).fetchone()[0])
    assert owner["no_scientific_allowance"] is True
    assert batch.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==0
    assert batch.db.execute("SELECT count(*) FROM autonomy_compute").fetchone()[0]==0


@pytest.mark.parametrize("field,new",[
    ("operation_id","second"),("run_id","old-M3"),("source","wrong"),
    ("authority_sha256","f"*64),("team_authority_sha256","f"*64),
    ("worker_sha256","x"*64),("installed_config_sha256","b"*63),
    ("image_id","bad"),("base_image","unbound:latest"),("purpose",direct.PURPOSE)])
def test_wrong_scope_pins_and_owner_cannot_reserve(prepared,field,new):
    batch,a,b,v=prepared;b[field]=new
    with pytest.raises(ValueError,match="^ENVIRONMENT_INVENTORY_BINDING$"):reserve(prepared)
    assert batch.db.execute("SELECT count(*) FROM autonomy_assets").fetchone()[0]==0


@pytest.mark.parametrize("change",["extra","gpu","cpu","cost","extra-rate","missing-rate"])
def test_envelope_cannot_be_changed(prepared,change):
    batch,a,b,v=prepared
    if change=="extra":b["extra"]="ignored"
    elif change in {"gpu","cpu"}:b["envelope"]["resources"][change]="H100" if change=="gpu" else 2
    elif change=="cost":b["envelope"]["cost"]["reserved_micro_usd"]=1
    elif change=="extra-rate":b["envelope"]["cost"]["rates"]["ignored"]="0"
    else:b["envelope"]["cost"]["rates"].pop("cpu_hour_cost_sandbox")
    with pytest.raises(ValueError):reserve(prepared)
    assert batch.db.execute("SELECT count(*) FROM autonomy_assets").fetchone()[0]==0


@pytest.mark.parametrize("change",["source","image_id","worker_sha256","installed_config_sha256","price"])
def test_changed_binding_cannot_manufacture_second_operation(prepared,change):
    batch,a,b,v=prepared;reserve(prepared)
    old=[tuple(x) for x in batch.db.execute("SELECT * FROM autonomy_assets")]
    if change=="price":
        v["rates"]["cpu_hour_cost_sandbox"]=".2";seal(v);b["envelope"]=budget.envelope(v["rates"])
    else:b[change]="im-changed" if change=="image_id" else ("e"*(40 if change=="source" else 64))
    # Even a hypothetical new owner binding cannot evade the immutable operation
    # guard. Real register_run itself refuses this changed owner first.
    with pytest.raises(ValueError,match="^BATCH_RUN_BINDING_CHANGED$"):
        batch.register_run(budget.RUN,budget.owner(b))
    batch.db.execute("UPDATE autonomy_runs SET binding=? WHERE id=?",(canonical(budget.owner(b)).decode(),budget.RUN))
    with pytest.raises(ValueError,match="^ENVIRONMENT_INVENTORY_ALREADY_RESERVED_NO_RETRY$"):reserve(prepared)
    assert [tuple(x) for x in batch.db.execute("SELECT * FROM autonomy_assets")]==old


@pytest.mark.parametrize("change,code",[
    ("owner","ENVIRONMENT_INVENTORY_OWNER_REQUIRED"),("complete","BATCH_ACTIVE_RUN_REQUIRED"),
    ("halt","AUTONOMY_BATCH_HALTED"),("running","BATCH_UNCERTAIN_OR_RUNNING_CALL"),
    ("uncertain","BATCH_UNCERTAIN_OR_RUNNING_CALL"),("asset","MODAL_UNCERTAIN_ASSET_PREPARATION"),
    ("compute","MODAL_ACTIVE_OR_UNCERTAIN_COMPUTE"),("active-compute","MODAL_ACTIVE_OR_UNCERTAIN_COMPUTE"),
    ("headroom","ITEM4_PROVIDER_HEADROOM_WAIT"),("stale","MODAL_BILLING_SNAPSHOT_STALE"),
    ("wrong-workspace","ENVIRONMENT_INVENTORY_COST_BINDING"),("snapshot-hash","MODAL_BILLING_SNAPSHOT_HASH")])
def test_no_new_charge_on_refusal(prepared,change,code):
    batch,a,b,v=prepared
    if change=="owner":batch.db.execute("UPDATE autonomy_runs SET binding='{}'")
    elif change=="complete":batch.db.execute("UPDATE autonomy_runs SET status='COMPLETE'")
    elif change=="halt":(batch.folder/"HALT").write_text("Synthetic hold")
    elif change in {"running","uncertain"}:
        batch.db.execute("INSERT INTO autonomy_calls VALUES('old','scientific','old',1,'2026-10-06',?,'{}',NULL)",(change.upper(),))
    elif change=="asset":asset(batch,100,status="UNCERTAIN")
    elif change in {"compute","active-compute"}:compute(batch,100,status="UNCERTAIN" if change=="compute" else "RUNNING")
    elif change=="headroom":v["summary"]["metered_cost"]="1000";seal(v)
    elif change=="stale":v["observed_at"]=(NOW-timedelta(minutes=6)).isoformat();seal(v)
    elif change=="wrong-workspace":v["workspace"]="other";seal(v)
    else:v["sha256"]="f"*64
    before=[tuple(x) for x in batch.db.execute("SELECT * FROM autonomy_assets")]
    with pytest.raises(ValueError,match="^"+code+"$"):reserve(prepared)
    assert [tuple(x) for x in batch.db.execute("SELECT * FROM autonomy_assets")]==before


@pytest.mark.parametrize("kind",["download","smoke","full","owned-assets"])
def test_all_prior_item4_costs_count_across_owners(prepared,kind):
    batch,a,b,v=prepared;amount=b["envelope"]["cost"]["reserved_micro_usd"]
    if kind=="download":asset(batch,policy.SMOKE_CAP-amount+1)
    elif kind=="owned-assets":
        batch.db.execute("INSERT INTO autonomy_runs VALUES('old-item4',?,'COMPLETE')",(canonical({"backlog_item":4,"experiment_authority_sha256":policy.AUTHORITY}).decode(),))
        batch.db.execute("INSERT INTO autonomy_assets VALUES('old','old-item4','{}','READY',?,NULL)",(policy.SMOKE_CAP-amount+1,))
    else:compute(batch,(policy.TOTAL_CAP if kind=="full" else policy.SMOKE_CAP)-amount+1,stage=kind.upper())
    before=[tuple(x) for x in batch.db.execute("SELECT * FROM autonomy_assets")]
    with pytest.raises(ValueError,match="^ITEM4_HARD_COST_CAP$"):reserve(prepared)
    assert [tuple(x) for x in batch.db.execute("SELECT * FROM autonomy_assets")]==before


def test_exact_cap_and_prior_failed_charges_are_not_refunded(prepared):
    batch,a,b,v=prepared;amount=b["envelope"]["cost"]["reserved_micro_usd"]
    # Two completed original infrastructure reservations both count; no netting.
    asset(batch,1000000,"one");asset(batch,policy.SMOKE_CAP-amount-1000000,"two")
    before=[tuple(x) for x in batch.db.execute("SELECT * FROM autonomy_assets")]
    assert reserve(prepared)
    assert [tuple(x) for x in batch.db.execute("SELECT * FROM autonomy_assets WHERE id IN ('one','two')")]==before
    event=json.loads(batch.db.execute("SELECT payload FROM events WHERE id=?",(digest(canonical(b))+":assets-reserved",)).fetchone()[0])
    assert event["prior_item4_smoke_micro_usd"]+amount==policy.SMOKE_CAP
    assert event["caps"]=={"smoke":policy.SMOKE_CAP,"total":policy.TOTAL_CAP}


def test_billed_excess_is_preserved_before_failed_admission(prepared):
    batch,a,b,v=prepared;compute(batch,100,ident="paid")
    v["rows"]=[{"object_id":"ap-paid","interval_start":"2026-10-06T02:00:00+00:00","cost":"2","cost_by_resource":{"CPU":"2"}}]
    v["summary"].update(metered_cost="2",billed_cost="2");seal(v)
    with pytest.raises(ValueError,match="^ITEM4_COST_BOUND_BELOW_BILLING$"):reserve(prepared)
    assert terminal.highwater(batch.db)=={("ap-paid","2026-10"):2000000}
    assert batch.db.execute("SELECT reserved_micro_usd FROM autonomy_compute").fetchone()[0]==100
    assert batch.db.execute("SELECT count(*) FROM autonomy_assets").fetchone()[0]==0


def test_unrelated_legacy_reservations_still_reduce_workspace_headroom(prepared):
    batch,a,b,v=prepared
    batch.db.execute("INSERT INTO autonomy_compute VALUES('old','M3','{}','ACCOUNTED',899500000,'sb-old',NULL,'2026-09')")
    with pytest.raises(ValueError,match="^ITEM4_PROVIDER_HEADROOM_WAIT$"):reserve(prepared)
    assert batch.db.execute("SELECT count(*) FROM autonomy_assets").fetchone()[0]==0


@pytest.mark.parametrize("damage",["id","run","cost","binding"])
def test_recognized_asset_requires_exact_preserved_binding(prepared,damage):
    batch,a,b,v=prepared;reserve(prepared)
    row=dict(batch.db.execute("SELECT * FROM autonomy_assets").fetchone())
    if damage=="id":row["id"]="f"*64
    elif damage=="run":row["run"]="another"
    elif damage=="cost":row["reserved_micro_usd"]-=1
    else:
        value=json.loads(row["binding"]);value["operation_id"]="another";row["binding"]=canonical(value).decode()
    with pytest.raises(ValueError):budget.selected_asset(row)
    assert budget.selected_asset({"binding":"{}"}) is False


def finish_inventory(prepared):
    batch,accounts,value,view=prepared
    assert reserve(prepared) is True
    ident=digest(canonical(value))
    accounts.finish_assets(ident,"READY",{"status":"VERIFIED","synthetic_inventory_fixture":True})
    batch.complete_run(budget.RUN,{"administrative_environment_inventory_only":True})
    row=dict(batch.db.execute("SELECT * FROM autonomy_assets WHERE id=?",(ident,)).fetchone())
    assert row["status"]=="READY" and budget.selected_asset(row)
    return row


def test_genuine_inventory_reservation_carries_into_scientific_smoke_cap(prepared):
    from test_modal_item4_budget import bound
    batch,accounts,value,view=prepared;original=finish_inventory(prepared)
    batch.register_run("item4",{"backlog_item":4,"experiment_authority_sha256":policy.AUTHORITY})
    scientific=bound("nextfit")
    scientific["cost"]=policy.quote(scientific["resources"],view["rates"],0)
    cost=scientific["cost"]["reserved_micro_usd"]
    # Fits alone exactly fit; the real prior inventory reservation must make
    # admission refuse. No monkeypatch of either producer or budget consumer.
    compute(batch,policy.SMOKE_CAP-cost,ident="oldfit",run="item4")
    before=[tuple(x) for x in batch.db.execute("SELECT * FROM autonomy_compute")]
    with pytest.raises(ValueError,match="^ITEM4_HARD_COST_CAP$"):
        accounts.reserve_item4(digest(canonical(scientific)),"item4",scientific,billing_snapshot=view,now=NOW)
    assert [tuple(x) for x in batch.db.execute("SELECT * FROM autonomy_compute")]==before
    assert dict(batch.db.execute("SELECT * FROM autonomy_assets WHERE id=?",(original["id"],)).fetchone())==original
    assert batch.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==0


def test_genuine_inventory_reservation_carries_into_direct_input_smoke_cap(prepared):
    batch,accounts,value,view=prepared;original=finish_inventory(prepared)
    run="item4-inputs-after-inventory"
    batch.register_run(run,{"purpose":direct.PURPOSE,"authority_sha256":policy.AUTHORITY})
    selected={"purpose":direct.PURPOSE,"authority_sha256":policy.AUTHORITY,
        "download_authority_sha256":direct.DOWNLOAD_AUTHORITY,"team_authority_sha256":policy.TEAM_AUTHORITY,
        "run_id":run,"download_bytes":54323796401,"envelope":direct.envelope(54323796401,view["rates"]),
        "package_manifest_sha256":"d"*64}
    # This is not a prior download, and so must not trip one-download refusal.
    # It must instead count against the same original item4 smoke ceiling.
    cost=selected["envelope"]["cost"]["reserved_micro_usd"]
    compute(batch,policy.SMOKE_CAP-cost,ident="old-science")
    with pytest.raises(ValueError,match="^ITEM4_HARD_COST_CAP$"):
        direct.reserve(accounts,digest(canonical(selected)),run,selected,billing_snapshot=view,now=NOW)
    assert batch.db.execute("SELECT count(*) FROM autonomy_assets").fetchone()[0]==1
    assert dict(batch.db.execute("SELECT * FROM autonomy_assets WHERE id=?",(original["id"],)).fetchone())==original
    assert batch.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==0
