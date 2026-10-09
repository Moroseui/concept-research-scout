import json
from pathlib import Path
import pytest
from orchestrator import context_budget as cb,manual_context as mc,experiment_approval as approval
from orchestrator import private_records as pr
from test_manual_context import root,artifact,build,add_obligation
from test_experiment_approval import reviewed
from test_experiment_context import experiment


def test_complete_plan_delivered_as_hash_bound_original_and_readable_copy(root):
    quote=add_obligation(root,'adverse finding')
    plan=json.dumps({'full_fits':[{'id':str(i),'text':'synthetic '+str(i)} for i in range(2000)]})
    original=artifact(root,'configuration','authored-execution-plan',text=plan)
    operator=artifact(root,'configuration','operator-scope',text='SYNTHETIC OPERATOR CAP:75')
    body,m=build(root,'run_spec_review',[original,operator])
    assert plan not in body and 'SYNTHETIC OPERATOR CAP:75' in body and quote in body
    assert m['selected_artifacts']==mc.selected_artifacts('run_spec_review',[original,operator])
    delivered=next(x for x in m['workspace_files'] if x['id']==original['id'])
    copy=delivered['readable_json'];work=root/'workspaces/run_spec_review'
    assert (work/delivered['path']).read_bytes()==plan.encode()
    assert json.loads((work/copy['path']).read_bytes())==json.loads(plan)
    assert cb.sha((work/delivered['path']).read_bytes())==original['sha256']==copy['original_sha256']
    assert copy['original_path']==delivered['path'] and cb.encoded(delivered) in body
    assert len(body)==m['characters']<cb.LIMIT==200000
    assert all((work/x['path']).stat().st_mode&0o777==0o400 for x in m['workspace_files'])


def test_large_unrelated_configuration_still_hits_unchanged_limit(root):
    original=artifact(root,'configuration','operator-scope',text='x'*200000)
    with pytest.raises(cb.ContextTooLarge):build(root,'run_spec_review',[original])
    assert not (root/'workspaces').exists()


@pytest.mark.parametrize('damage',['changed-original','unsafe','duplicate-json','changed-delivery'])
def test_plan_transport_refuses_changed_unsafe_or_ambiguous_material(root,damage):
    original=artifact(root,'configuration','authored-execution-plan',text='{"synthetic":1}')
    if damage=='changed-delivery':
        _,m=build(root,'run_spec_review',[original]);x=next(x for x in m['workspace_files'] if x['id']==original['id'])
        p=root/'workspaces/run_spec_review'/x['path'];p.chmod(0o600);p.write_text('changed')
    else:
        p=root/original['path']
        if damage=='changed-original':p.write_text('changed')
        elif damage=='unsafe':
            p.write_text('{"patient":"sub-'+'stroke1234567890"}');original['sha256']=cb.sha(p.read_bytes())
        else:p.write_text('{"a":1,"a":2}');original['sha256']=cb.sha(p.read_bytes())
    with pytest.raises(ValueError):build(root,'run_spec_review',[original])


@pytest.mark.parametrize("reviewed",["authored4","partitions4","requirements4"],indirect=True)
def test_real_approval_consumer_requires_preserved_authored_plan_copy(reviewed):
    d,value,work=reviewed
    assert any(x['id']=='authored-execution-plan' for x in value['artifacts'])
    m=json.loads((work/'input-measurement.json').read_bytes())
    shown=next(x for x in m['workspace_files'] if x.get('id')=='authored-execution-plan')
    approval.inspect(d,value,value['pending'])
    copy=shown['readable_json'];p=work/copy['path'];p.chmod(0o600);p.write_text('{"tampered":true}')
    with pytest.raises(ValueError):approval.inspect(d,value,value['pending'])


@pytest.mark.parametrize("reviewed",["authored4","partitions4","requirements4"],indirect=True)
def test_real_approval_consumer_refuses_missing_original_even_if_copy_exists(reviewed):
    d,value,work=reviewed
    assert any(x['id']=='authored-execution-plan' for x in value['artifacts'])
    m=json.loads((work/'input-measurement.json').read_bytes());shown=next(x for x in m['workspace_files'] if x.get('id')=='authored-execution-plan')
    (work/shown['path']).unlink()
    with pytest.raises((ValueError,OSError)):approval.inspect(d,value,value['pending'])


def test_same_bytes_distinct_artifact_ids_remain_searchable_without_relaxing_duplicate_guard(root):
    from orchestrator import scientific_search as search
    first=artifact(root,'notebook_patch','original-patch',text='{"synthetic":1}')
    second=artifact(root,'notebook_patch','current-patch',text='{"synthetic":1}')
    body,measurement=build(root,'run_spec_review',[first,second]);work=root/'workspaces/run_spec_review'
    rows=measurement['workspace_files'];assert len(rows)==2 and len({r['path'] for r in rows})==2
    pr.write_text(work/'input-measurement.json',json.dumps(measurement))
    prepared=search.prepare(work)
    result=search.query(work,prepared['manifest_sha256'],'evidence_glob',{})
    assert {r['id'] for r in result['hits']}=={'original-patch','current-patch'}
    assert all((work/r['path']).read_bytes()==b'{"synthetic":1}' for r in result['hits'])
    # A conflicting path/ID is still refused by the unchanged search implementation.
    measurement['workspace_files'].append({**rows[0],'id':'conflicting-ID'})
    pr.write_text(work/'input-measurement.json',json.dumps(measurement))
    with pytest.raises(ValueError,match='SEARCH_DUPLICATE_BINDING'):search.prepare(work)


def test_same_json_reading_bytes_keep_distinct_original_identities():
    a={'id':'first','path':'evidence/first','sha256':cb.sha(b'{"a":1}')}
    b={'id':'second','path':'evidence/second','sha256':a['sha256']}
    x,raw=mc._json_reading_copy(a,b'{"a":1}');y,other=mc._json_reading_copy(b,b'{"a":1}')
    assert raw==other and x['path']!=y['path'] and x['original_path']!=y['original_path']
