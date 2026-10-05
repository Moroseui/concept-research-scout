import json
import pytest
from orchestrator import context_budget as budget, manual_context, modal_evidence, private_records
from orchestrator.manual_executor import read, atomic
from orchestrator.manual_contract import validate_next
from test_context_budget import root, add_obligation, save_manifest
from test_manual_context import build, artifact, STAGES
from test_modal_driver import modal_lane, lane, policy, private_copied_fixture


def closed_finding(root):
    quote = add_obligation(root, 'adverse finding')
    path = root / budget.PROJECT / 'obligations.json'
    register = json.loads(path.read_text())
    row = register['obligations'][-1]
    resolution = root / 'current-resolution.md'
    resolution.write_text('Independent approval closes this exact synthetic finding; no efficacy claim.')
    row.update(status='closed', disposition={'path': resolution.name,
        'sha256': budget.sha(resolution.read_bytes()), 'start': 0,
        'end': len(resolution.read_bytes()), 'text': resolution.read_text()})
    path.write_text(json.dumps(register)); save_manifest(root)
    return quote, row, resolution


def test_historical_open_text_always_has_current_closure_for_both_roles(root):
    quote, row, resolution = closed_finding(root)
    spec = artifact(root, 'run_spec', text='Historical: TEST-STOP remains open. ' + quote)
    for stage in STAGES:
        body, measurement = build(root, stage, [spec])
        record = next(x for x in measurement['finding_status'] if x['id'] == row['id'])
        assert record['status'] == 'closed' and record['resolution']['sha256'] == row['disposition']['sha256']
        delivered = json.loads((root / 'workspaces' / stage / record['path']).read_text())
        assert delivered == row and delivered['text'] == quote
        assert delivered['disposition']['text'] == resolution.read_text()
        assert row['id'] not in measurement['open_obligations']
        assert record['path'] in body and 'Historical: TEST-STOP remains open' in body
    with pytest.raises(ValueError, match='OPEN_BLOCKER_BINDING_REQUIRED'):
        validate_next({'status':'PROPOSAL_ONLY','proposed_action_type':'blocker_resolution',
            'action':'Resolve historical finding','rationale':'Synthetic','charter_basis':'',
            'blocker_ids':[row['id']]}, manual_context.open_blocker_ids(root,'result_interpretation_author',['P001']))


def test_open_findings_remain_verbatim_and_wrong_scope_does_not_leak(root):
    quote = add_obligation(root,'adverse finding')
    body, measurement = build(root,'result_interpretation_author')
    assert quote in body and 'TEST-STOP' in measurement['open_obligations']
    record = next(r for r in measurement['finding_status'] if r['id']=='TEST-STOP')
    assert record['status']=='open' and record['resolution'] is None
    assert 'TEST-STOP' not in build(root,'result_interpretation_author',target='P002')[0]


@pytest.mark.parametrize('damage',['changed','missing'])
def test_closed_finding_resolution_must_remain_retrievable(root,damage):
    _,_,path=closed_finding(root)
    if damage=='changed':path.write_text('altered resolution')
    else:path.unlink()
    with pytest.raises(budget.ContextError,match='RESOLUTION_CHANGED|SOURCE_MISSING'):
        build(root,'result_interpretation_review')


@pytest.fixture
def collected(modal_lane):
    d,p=modal_lane
    for _ in range(6):d.advance()
    p.state='COMPLETE'
    result=d.advance()
    assert result['phase']=='result_interpretation_author',result
    return d,p


def test_actual_driver_delivers_saved_attempt_connection_to_both_roles(collected):
    d,p=collected;calls=list(p.calls)
    raw=modal_evidence.collected_view(d.state,d.config,d.current()['manifest'])
    view=json.loads(raw)
    assert view['validation_status']=='VALID'
    assert view['epoch_counts'][0]['inner_epochs']==2
    assert view['epoch_counts'][0]['final_epochs']==2
    assert view['records']['terminated.json']['terminated'] is True
    assert 'file_sha256' not in view['records']['collection-receipt.json']
    assert p.calls==calls  # No retrieval/submission attributed to this read.
    for stage in ['result_interpretation_author','result_interpretation_review']:
        body,m=manual_context.prepare(d.context,stage=stage,idea_ids=['Sprint9'],
            task=d.task(stage,d.current()),artifacts=d.current()['artifacts'],workspace=d.state/('measurement-'+stage))
        assert view['binding_sha256'] in body and len(body)<200000


@pytest.mark.parametrize('damage,code',[
    ('binding','EVIDENCE_ATTEMPT_BINDING'),('provider','EVIDENCE_PROVIDER_BINDING'),
    ('termination','EVIDENCE_TERMINATION_REQUIRED'),('result','EVIDENCE_COLLECTION_CHANGED'),
    ('validation','EVIDENCE_VALIDATION_BINDING'),('missing','EVIDENCE_ORIGINAL_REQUIRED')])
def test_changed_or_missing_saved_connection_refuses(collected,damage,code):
    d,p=collected;calls=list(p.calls);work=d.state/'modal-executions'/d.config['run_id']
    if damage in {'binding','provider'}:
        path=work/'execute-intent.json';r=read(path)
        r['binding_sha256' if damage=='binding' else 'provider_id']='changed';atomic(path,r)
    elif damage=='termination':atomic(work/'terminated.json',{'provider_id':read(work/'created.json')['provider_id'],'terminated':False})
    elif damage=='result':private_records.write_text(d.state/'collected/summary.json','{}')
    elif damage=='validation':
        r=read(d.state/'validation.json');r['files']={};atomic(d.state/'validation.json',r)
    else:(work/'execute-intent.json').unlink()
    with pytest.raises(ValueError) as error:modal_evidence.collected_view(d.state,d.config,d.current()['manifest'])
    assert str(error.value)==code and p.calls==calls
