"""Real canonical ownership/accounting; provider/native output explicitly synthetic."""
import copy,json
import pytest
from orchestrator import modal_pinned_image as image,modal_environment_budget as budget
from orchestrator import modal_environment_inventory as controller,modal_environment_provider as native
from orchestrator import private_records as pr
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from test_modal_pinned_image import unreserved_fixture,inventory_fixture,experiment,root,view,NOW
from test_modal_environment_budget import asset,compute


def reserve(f):
    return budget.reserve(f.accounts,digest(canonical(f.binding)),image.RUN,f.binding,billing_snapshot=view(),now=NOW)


def rows(f,table):return [tuple(r) for r in f.accounts.db.execute('SELECT * FROM '+table)]


def config(f,state):
    return {**{k:f.binding[k] for k in ('source','operation_id','image_id','base_image','worker_sha256','image_build','owner_sha256')},
        'schema':image.SCHEMA,'release':'/synthetic-release','installation_record':'/synthetic-install',
        'installation_sha256':'c'*64,'state':str(state),'batch_ledger':str(f.accounts.batch.folder),
        'provider':f.provider.config,'units':{}}


def test_controller_reserves_builds_replays_without_owner_or_allowance_change(unreserved_fixture,tmp_path):
    f=unreserved_fixture;state=tmp_path/'image-state';pr.mkdir(state);c=config(f,state)
    proof={'status':'PASS','source':c['source'],'installation_sha256':c['installation_sha256'],
        'config_sha256':f.binding['installed_config_sha256']}
    owners=rows(f,'autonomy_runs');calls=rows(f,'autonomy_calls')
    result=controller.tick(c,f.provider,f.accounts,host_proof=proof,now=NOW)
    assert result['status']=='VERIFIED'
    assert rows(f,'autonomy_runs')==owners and rows(f,'autonomy_calls')==calls
    assert f.accounts.db.execute('SELECT status FROM autonomy_runs WHERE id=?',(image.RUN,)).fetchone()[0]=='ACTIVE'
    before=list(f.calls);saved=rows(f,'autonomy_assets')
    assert controller.tick(c,None,f.accounts,host_proof=proof,now=NOW)==result
    assert f.calls==before and rows(f,'autonomy_assets')==saved
    consumer=image.consumer_proof(f.accounts,f.binding,state)
    assert consumer['binding']['owner_sha256']==digest(canonical(f.original_owner))
    assert rows(f,'autonomy_runs')==owners and rows(f,'autonomy_calls')==calls
    with pytest.raises(ValueError,match='^ITEM4_IMAGE_REUSE_EXISTING_OWNER$'):budget.owner(f.binding)
    assert len([c for c in f.calls if c[0]=='build-function'])==1


@pytest.mark.parametrize('damage,code',[
    ('missing','BATCH_ACTIVE_RUN_REQUIRED'),('complete','BATCH_ACTIVE_RUN_REQUIRED'),
    ('scope','ITEM4_IMAGE_EXISTING_OWNER_CHANGED'),('source','ITEM4_IMAGE_EXISTING_OWNER_CHANGED'),
    ('authority','ENVIRONMENT_INVENTORY_BINDING'),('run','ENVIRONMENT_INVENTORY_BINDING'),
    ('owner-pin','ITEM4_IMAGE_EXISTING_OWNER_CHANGED'),('lane','ITEM4_IMAGE_EXISTING_OWNER_CHANGED'),
    ('preparation','ITEM4_IMAGE_EXISTING_OWNER_CHANGED')])
def test_owner_scope_drift_refuses_before_new_reservation(unreserved_fixture,damage,code):
    f=unreserved_fixture;d=f.owner_driver;db=f.accounts.db
    if damage=='missing':db.execute('DELETE FROM autonomy_runs WHERE id=?',(image.RUN,))
    elif damage=='complete':db.execute("UPDATE autonomy_runs SET status='COMPLETE' WHERE id=?",(image.RUN,))
    elif damage=='scope':
        owner=copy.deepcopy(f.original_owner);owner['execution_scope']['item_number']=6
        db.execute('UPDATE autonomy_runs SET binding=? WHERE id=?',(canonical(owner).decode(),image.RUN))
    elif damage=='source':f.binding['source']='f'*40
    elif damage=='authority':f.binding['authority_sha256']='f'*64
    elif damage=='run':f.binding['run_id']='sprint13b-second-owner'
    elif damage=='owner-pin':f.binding['owner_sha256']='0'*64
    elif damage=='lane':
        c=copy.deepcopy(d.config);c['source']='f'*40;pr.atomic(d.state/'lane.json',c)
    elif damage=='preparation':pr.write_text(d.state/'preparation-plan.json','{}')
    before=rows(f,'autonomy_runs');calls=rows(f,'autonomy_calls')
    with pytest.raises(ValueError,match='^'+code+'$'):reserve(f)
    assert rows(f,'autonomy_runs')==before and rows(f,'autonomy_calls')==calls
    assert rows(f,'autonomy_assets')==[] and f.calls==[]


def test_provider_checks_owner_again_before_any_rpc(unreserved_fixture):
    f=unreserved_fixture;assert reserve(f)
    f.accounts.db.execute("UPDATE autonomy_runs SET status='COMPLETE' WHERE id=?",(image.RUN,))
    with pytest.raises(ValueError,match='^ITEM4_IMAGE_ACTIVE_OWNER_REQUIRED$'):
        native.launch(f.provider,f.accounts,f.binding,f.root)
    assert f.calls==[] and not f.root.exists()


def test_original_item4_assets_compute_and_charged_calls_preserved(unreserved_fixture):
    f=unreserved_fixture
    # Explicit preserved-cost fixture: original assets are charged, not forgiven.
    asset(f.accounts.batch,24170118,ident='original-inputs')
    compute(f.accounts.batch,3000000,ident='prior-fit')
    f.accounts.db.execute("INSERT INTO autonomy_calls VALUES('charged','scientific',?,1,'2026-10-07','COMPLETE','{}','{}')",(image.RUN,))
    old_assets=rows(f,'autonomy_assets');old_compute=rows(f,'autonomy_compute');old_calls=rows(f,'autonomy_calls');old_owner=rows(f,'autonomy_runs')
    assert old_assets[0][1]=='old-inputs' and old_assets[0][1]!=image.RUN
    assert old_compute[0][1]=='old-item4' and old_compute[0][1]!=image.RUN
    assert reserve(f)
    event=json.loads(f.accounts.db.execute('SELECT payload FROM events WHERE id=?',(digest(canonical(f.binding))+':assets-reserved',)).fetchone()[0])
    assert event['prior_item4_smoke_micro_usd']==event['prior_item4_total_micro_usd']==27170118
    assert event['caps']=={'smoke':75000000,'total':1275000000}
    assert rows(f,'autonomy_assets')[:len(old_assets)]==old_assets
    assert rows(f,'autonomy_compute')==old_compute and rows(f,'autonomy_calls')==old_calls and rows(f,'autonomy_runs')==old_owner
    assert reserve(f) is False


@pytest.mark.parametrize('kind',['smoke','total'])
def test_prior_asset_and_compute_exposure_cannot_escape_original_caps(unreserved_fixture,kind):
    f=unreserved_fixture;amount=f.binding['envelope']['cost']['reserved_micro_usd']
    if kind=='smoke':asset(f.accounts.batch,budget.SMOKE_CAP-amount+1)
    else:compute(f.accounts.batch,budget.TOTAL_CAP-amount+1,stage='FULL')
    before=rows(f,'autonomy_assets');owners=rows(f,'autonomy_runs')
    with pytest.raises(ValueError,match='^ITEM4_HARD_COST_CAP$'):reserve(f)
    assert rows(f,'autonomy_assets')==before and rows(f,'autonomy_runs')==owners and f.calls==[]


def test_changed_image_source_cannot_create_second_owner_or_operation(unreserved_fixture):
    f=unreserved_fixture;assert reserve(f)
    before=rows(f,'autonomy_runs');assets=rows(f,'autonomy_assets')
    f.binding['source']='f'*40
    with pytest.raises(ValueError,match='^ITEM4_IMAGE_EXISTING_OWNER_CHANGED$'):reserve(f)
    assert rows(f,'autonomy_runs')==before and rows(f,'autonomy_assets')==assets
    f.binding['source']=f.original_owner['source'];f.binding['image_id']='im-Another'
    with pytest.raises(ValueError,match='^ENVIRONMENT_INVENTORY_ALREADY_RESERVED_NO_RETRY$'):reserve(f)
    assert rows(f,'autonomy_runs')==before and rows(f,'autonomy_assets')==assets and f.calls==[]
