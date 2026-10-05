"""Native-original settlement projection; synthetic scientific context, no models."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
from orchestrator import reviewed_history as r, scientific_evidence_access as access
from orchestrator import change_requests as c, terminal_review as terminal
from test_selected_scientific_history import captured, append, write_state
from test_campaign_grounding_presentation import example
from test_disposition_context import SOURCE


def agent_append(state, kind, payload, family='codex'):
    event = append(state, kind, payload)
    event['actor'] = {'kind':'agent', 'family':family, 'model':'synthetic-model',
                      'session_id':'synthetic-session'}
    event['identity'] = r.sha({k:v for k,v in event.items() if k != 'identity'})
    state['head_sha256'] = hashlib.sha256(c.encoded(event)+b'\n').hexdigest()
    return event


def build(e, tmp_path, count=1, fault=None, extra_resolution=None, profile=terminal.PROFILE, resolution_metadata=None):
    state = deepcopy(e.current_chain)
    closed = [agent_append(state, 'DISPOSITION', {
        'rationale':f'Synthetic explicitly settled implementation issue {i}. '+('evidence '*300),
        'affected_results':['Synthetic source only.'],
        'conditions':['Human stop remains effective.'],
        'unknown':{'pending':'Unresolved extra condition.'}}) for i in range(count)]
    findings={name:{'disposition':'preserve','reason':'Synthetic remaining condition.'}
              for name in terminal.FINDINGS}
    findings['C006']['disposition']=findings['C007']['disposition']='resolved'
    statement={'schema':profile,'source':SOURCE,'proposal_sha256':'a'*64,
        'manifest_sha256':'b'*64,'session_id':'synthetic-review-session',
        'scope':'material-source-integration','verdict':'APPROVE',
        'inspected':['Synthetic source fixture.'],'unavailable':[],
        'unverified':['H2 is not accepted.'],'findings':findings,
        'resolution_of':terminal.BASE_SOURCE,
        'remaining_gates':['held-deployment','accounting-halt','retained-history-audit',
                           'conditional-activation','scientific-acceptance']}
    fence=chr(96)*3
    raw=('Final source/integration verdict: APPROVE\n'+fence+'terminal-review-verdict\n'+
         json.dumps(statement)+'\n'+fence+'\n').encode()
    if fault=='rejected_report':
        raw=raw.replace(b'APPROVE',b'REQUEST_CHANGES')
    sha=hashlib.sha256(raw).hexdigest()
    desc={'artifact':'evidence/'+sha+'-resolution.md','sha256':sha,'size':len(raw)}
    extra_artifacts = {}
    review_evidence = {'report':desc}
    original_binding = {}
    if extra_resolution is not None:
        extra_raw = raw.replace(b'Synthetic source fixture.', b'Synthetic retained substantive report.')
        extra_sha = hashlib.sha256(extra_raw).hexdigest()
        extra_desc = {'artifact':'evidence/'+extra_sha+'-substantive.md',
                      'sha256':extra_sha,'size':len(extra_raw)}
        review_evidence['substantive_prior'] = extra_desc
        extra_artifacts[extra_desc['artifact']] = extra_raw
        if extra_resolution != 'unpinned':
            original_binding = {'original_review':{'response_sha256':
                '0'*64 if extra_resolution=='wrong_pin' else sha}}
    resolution=agent_append(state,'REVIEW',{'applied_event':e.latest,'verdict':'APPROVE',
        'rationale':'Synthetic independent source approval, not activation.',
        'review_evidence':review_evidence,
        **({'source':SOURCE,'proposal_sha256':'a'*64} if resolution_metadata is None else resolution_metadata),
        **original_binding},'codex' if fault=='wrong_reviewer' else 'claude')
    plan={'schema':r.CURRENT_SETTLEMENT,'boundary':r.boundary(state),
          'settlements':{x['identity']:resolution['identity'] for x in closed},
          'scope':'settled-implementation-history-only',
          'qualification':'REQUIRES_INDEPENDENT_REVIEW_OF_THIS_EXACT_APPLICATION'}
    if fault=='unknown_event':plan['settlements']['0'*64]=resolution['identity']
    elif fault=='self_resolution':plan['settlements'][closed[0]['identity']]=closed[0]['identity']
    elif fault=='authority':plan['settlements'][state['events'][0]['identity']]=resolution['identity']
    elif fault=='human':plan['settlements'][state['events'][2]['identity']]=resolution['identity']
    elif fault=='wrong_boundary':plan['boundary']['head_sha256']='0'*64
    elif fault=='self_approval':plan['qualification']='APPROVED_BY_PROJECTION'
    elif fault=='scope':plan['scope']='all-science'
    elif fault=='empty_settlement':plan['settlements']={}
    app=agent_append(state,'APPLIED',{'modification':'Synthetic pending current-state representation.',
        'checks':['Synthetic exact binding'], 'review_status':'PENDING',
        'result_binding':{'source':SOURCE,'current_state_settlement':plan},
        'supersedes_applied_events':[e.latest]})
    if fault=='superseded':
        agent_append(state,'APPLIED',{'modification':'Later source.', 'checks':['Synthetic'],
          'review_status':'PENDING','result_binding':{'source':SOURCE},
          'supersedes_applied_events':[app['identity']]})
    agent_append(state,'DISPOSITION',{'rationale':'Unreviewed tail: do not execute.',
                                     'affected_results':['Synthetic']})
    store=tmp_path/('store-'+str(count)+'-'+str(fault))
    original_folder=Path(e.config['change_request_store'])/state['request']['identity']
    artifacts={str(x.relative_to(original_folder)):x.read_bytes()
               for x in (original_folder/'evidence').iterdir()}
    artifacts[desc['artifact']]=raw
    artifacts.update(extra_artifacts)
    write_state(store,state,artifacts)
    capture=access.capture_changes(store,[state['request']['identity']],
                                  source=SOURCE,task_binding='d'*64)
    return capture,state,app,closed,resolution


def test_projection_preserves_originals_open_criticism_authority_and_tail(captured,tmp_path):
    capture,state,app,closed,resolution=build(captured,tmp_path)
    before=deepcopy(capture);request=state['request']['identity']
    view=r.current_state_view(capture,request,app['identity'],source=SOURCE)
    assert capture==before
    assert r.captured_chain(capture,request)==state
    ids={x['identity'] for x in view['events']}
    assert closed[0]['identity'] not in ids
    assert app['identity'] in ids
    for event in state['events']:
        if event['event']=='AUTHORIZED' or event['identity']==state['events'][-1]['identity']:
            assert event in view['events']
    assert 'Unreviewed tail: do not execute.' in str(view)
    assert 'Latest criticism remains unresolved.' in str(view)
    assert 'H2 is not accepted.' in str(view)
    assert 'conditional-activation' in str(view)
    assert 'Human stop remains effective.' in str(view)
    assert 'Unresolved extra condition.' in str(view)
    assert app['payload']['review_status']=='PENDING'
    assert r.validate_current_state_view(view,capture,request,app['identity'],source=SOURCE)==view
    name='change/'+request+'/event/'+str(closed[0]['sequence'])+'.json'
    record=next(x for x in capture['manifest']['records'] if x['name']==name)
    assert json.loads(capture['payloads'][record['sha256']])==closed[0]


@pytest.mark.parametrize('fault',['unknown_event','self_resolution','authority','human',
                                 'wrong_boundary','self_approval','scope','superseded','rejected_report','wrong_reviewer'])
def test_invalid_or_superseded_settlement_refuses(captured,tmp_path,fault):
    capture,state,app,_,_=build(captured,tmp_path,fault=fault)
    with pytest.raises(ValueError):
        r.current_state_view(capture,state['request']['identity'],app['identity'],source=SOURCE)


@pytest.mark.parametrize('fault',['missing_original','changed_original','wrong_source','drop_open',
                                 'changed_view','changed_head'])
def test_original_and_view_corruption_refuses(captured,tmp_path,fault):
    capture,state,app,_,_=build(captured,tmp_path)
    request=state['request']['identity']
    view=r.current_state_view(capture,request,app['identity'],source=SOURCE)
    if fault=='missing_original':capture['payloads'].pop(next(iter(capture['payloads'])))
    elif fault=='changed_original':capture['payloads'][next(iter(capture['payloads']))]+=b'changed'
    elif fault=='wrong_source':capture['manifest']['source']='0'*40
    elif fault=='drop_open':view['events']=view['events'][:-1]
    elif fault=='changed_view':view['literal_resolution_reports']={}
    else:capture['manifest']['request_heads'][request]['head_sha256']='0'*64
    with pytest.raises(ValueError):
        r.validate_current_state_view(view,capture,request,app['identity'],source=SOURCE)


def test_settled_growth_moves_to_original_capture_not_initial_view(captured,tmp_path):
    sizes=[]
    for count in (1,10,100):
        capture,state,app,_,_=build(captured,tmp_path,count=count)
        view=r.current_state_view(capture,state['request']['identity'],app['identity'],source=SOURCE)
        sizes.append((len(c.encoded(view)),sum(len(x) for x in capture['payloads'].values())))
    assert sizes[2][0]-sizes[0][0]<200
    assert sizes[2][1]>sizes[0][1]+200000
    # Synthetic settled-history case, NOT real downstream task fit.


def test_later_approval_without_explicit_link_does_not_settle(captured,tmp_path):
    capture,state,app,closed,_=build(captured,tmp_path,fault='empty_settlement')
    view=r.current_state_view(capture,state['request']['identity'],app['identity'],source=SOURCE)
    assert closed[0] in view['events']


def test_cache_creation_scans_every_payload_before_any_write(captured,tmp_path,monkeypatch):
    capture,_,_,_,_=build(captured,tmp_path)
    calls=[]
    def scan(name,raw):
        calls.append((name,raw))
        if len(calls)==2:
            raise ValueError('SYNTHETIC_PUBLICATION_REFUSAL')
    monkeypatch.setattr(access,'scan',scan)
    destination=tmp_path/'not-created-on-refusal'
    with pytest.raises(ValueError,match='SYNTHETIC_PUBLICATION_REFUSAL'):
        access.write_capture(destination,capture)
    assert len(calls)==2
    assert not destination.exists()



def test_exact_crlf_originals_survive_cache_and_idempotent_recovery(captured,tmp_path):
    import os
    capture,_,_,_,_=build(captured,tmp_path)
    destination=tmp_path/'original-cache'
    descriptor=access.write_capture(destination,capture)
    assert access.write_capture(destination,capture)==descriptor
    reader=access.Reader(destination,descriptor['manifest_sha256'],source=SOURCE,
                         task_binding='d'*64,owner=os.getuid())
    row=next(x for x in capture['manifest']['records'] if x['sha256']==captured.response_sha)
    actual=reader._body(row).encode()
    assert bytes([13, 10]) in actual and actual==captured.raw_response
    original=destination/'objects'/(row['sha256']+'.txt')
    original.chmod(0o600);original.write_bytes(b'changed original')
    with pytest.raises(ValueError,match='IMMUTABLE_CONFLICT'):
        access.write_capture(destination,capture)



def test_secondary_history_uses_exact_external_source_application(captured,tmp_path):
    cap,state,prior,_,approval=build(captured,tmp_path)
    request=deepcopy(state['request']);request['key']='separate-repair-fixture'
    request['identity']=hashlib.sha256(c.encoded({k:v for k,v in request.items() if k not in c.META})).hexdigest()
    secondary={'request':request,'events':[],
               'head_sha256':hashlib.sha256(c.encoded(request)+bytes([10])).hexdigest()}
    append(secondary,'AUTHORIZED',deepcopy(state['events'][0]['payload']))
    base=agent_append(secondary,'APPLIED',{'modification':'Synthetic separate repair.',
        'checks':['Synthetic'], 'review_status':'PENDING','result_binding':{'source':SOURCE}})
    old=agent_append(secondary,'DISPOSITION',{'rationale':'Explicitly reviewed old secondary narrative.',
                                           'affected_results':['Synthetic source only.']})
    payload=deepcopy(approval['payload']);payload['applied_event']=base['identity']
    resolution=agent_append(secondary,'REVIEW',payload,'claude')
    template={'schema':r.CURRENT_SETTLEMENT,'scope':'settled-implementation-history-only',
              'qualification':'REQUIRES_INDEPENDENT_REVIEW_OF_THIS_EXACT_APPLICATION'}
    plans={state['request']['identity']:{**template,'boundary':r.boundary(state),'settlements':{}},
           request['identity']:{**template,'boundary':r.boundary(secondary),
                               'settlements':{old['identity']:resolution['identity']}}}
    app=agent_append(state,'APPLIED',{'modification':'Synthetic exact two-request map.',
        'checks':['Synthetic'], 'review_status':'PENDING','result_binding':{
            'source':SOURCE,'current_state_settlements':plans},
        'supersedes_applied_events':[prior['identity']]})
    store=tmp_path/'store-1-None'
    write_state(store,state)
    artifacts={}
    for row in cap['manifest']['records']:
        if row['kind']=='change_artifact':
            artifacts[row['provenance']['artifact']]=cap['payloads'][row['sha256']]
    write_state(store,secondary,artifacts)
    joined=access.capture_changes(store,sorted(plans),source=SOURCE,task_binding='d'*64)
    view=r.current_state_view(joined,request['identity'],app['identity'],
                              source=SOURCE,application_request=state['request']['identity'])
    assert old['identity'] not in {e['identity'] for e in view['events']}
    assert resolution['identity'] in view['literal_resolution_reports']
    with pytest.raises(ValueError):
        r.current_state_view(joined,request['identity'],app['identity'],source=SOURCE)


@pytest.mark.parametrize('binding',['bound','unpinned','wrong_pin'])
def test_same_bound_prior_report_requires_actual_original_and_keeps_both(captured,tmp_path,binding):
    cap,state,app,_,resolution=build(captured,tmp_path,extra_resolution=binding)
    if binding!='bound':
        with pytest.raises(ValueError):
            r.current_state_view(cap,state['request']['identity'],app['identity'],source=SOURCE)
        return
    view=r.current_state_view(cap,state['request']['identity'],app['identity'],source=SOURCE)
    reports=view['literal_resolution_reports'][resolution['identity']]
    assert reports['qualifying_original_sha256']==resolution['payload']['original_review']['response_sha256']
    assert len(reports['same_bound_original_reports'])==2
    assert all('conditional-activation' in body for body in reports['same_bound_original_reports'].values())
    assert any('retained substantive report' in body for body in reports['same_bound_original_reports'].values())
