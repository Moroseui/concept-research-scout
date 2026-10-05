"""Synthetic current-input presentation fixtures; no native approval/model claims."""
from copy import deepcopy
import hashlib
import json

import pytest

from orchestrator import change_requests as changes, current_scientific_input as current
from orchestrator import disposition_context as dc, reviewed_history as history
from test_current_input_integration import current_packet
from test_linked_input_integration import integrated
from test_campaign_grounding_presentation import example
from test_selected_scientific_history import captured
from test_disposition_context import SOURCE

FINDINGS=['Unresolved authority concern. '*30, 'Pending runtime condition. '*30]
SESSION='synthetic-independent-session'
SCOPE='synthetic-direction'
ACTOR={'kind':'agent','family':'codex','model':'synthetic-driver','session_id':'driver-session'}


def raw(value):
    return json.dumps(value,sort_keys=True)


def build(e, mutation=None):
    packet=deepcopy(e.current_packet)
    output={'scope':SCOPE,'reviewed_commit':SOURCE,'verdict':'REQUEST_CHANGES',
            'findings':deepcopy(FINDINGS)}
    response={'type':'result','session_id':SESSION,'is_error':False,'subtype':'success',
        'modelUsage':{'synthetic-model':{}},'structured_output':output,'result':raw(output)}
    response_raw=raw(response);response_sha=hashlib.sha256(response_raw.encode()).hexdigest()
    driver={'schema':'independent-direction-and-driver-response/v1',
        'session_id':SESSION,'scope':SCOPE,'source':SOURCE,'response_sha256':response_sha,
        'actual_verdict':'REQUEST_CHANGES','applied_material_approval':False,
        'science_or_activation_approval':False,'driver_actor':deepcopy(ACTOR),
        'distinct_condition':'No installation; no retry.',
        'findings_and_responses':[{'number':i+1,'finding_verbatim':finding,
            'driver_disposition':'UNRESOLVED','driver_response':'Distinct response '+str(i)+' remains. '*25}
            for i,finding in enumerate(FINDINGS)]}
    if mutation=='wrong_quote':driver['findings_and_responses'][0]['finding_verbatim']+=' Changed.'
    elif mutation=='driver_session':driver['session_id']='different-session'
    elif mutation=='driver_source':driver['source']='e'*40
    elif mutation=='driver_scope':driver['scope']='different-scope'
    elif mutation=='driver_verdict':driver['actual_verdict']='APPROVE'
    elif mutation=='approval_claim':driver['applied_material_approval']=True
    elif mutation=='unknown_schema':driver['schema']='unknown-direction/v1'
    elif mutation=='wrong_number':driver['findings_and_responses'][0]['number']=True
    elif mutation=='wrong_actor':driver['driver_actor']['session_id']='another-driver'
    driver_raw=raw(driver);driver_sha=hashlib.sha256(driver_raw.encode()).hexdigest()
    rid=packet['scientific_change_history']['primary']['request_id']
    def event(kind,number,payload):
        return {'schema':changes.EVENT_SCHEMA,'event':kind,'identity':str(number)*64,
            'sequence':number,'request_identity':rid,'previous_sha256':'d'*64,
            'actor':deepcopy(ACTOR),'recorded_at_utc':'synthetic','payload':payload}
    review=event('REVIEW',1,{'verdict':'REQUEST_CHANGES','rationale':'Preserved criticism.',
        'findings':deepcopy(FINDINGS),'affected_results':['No scientific acceptance.'],
        'original_review':{'response_sha256':response_sha,'session_id':SESSION,
            'source':SOURCE,'scope':SCOPE}})
    disposition=event('DISPOSITION',2,{'rationale':'Distinct explanation must remain.',
        'affected_results':['No scientific acceptance.'],'authority_reference':'Preserve authority.',
        'responds_to_review_event':review['identity'],'responds_to_session':SESSION,
        'response_evidence':[{'artifact':'evidence/'+driver_sha+'-driver.json',
            'sha256':driver_sha,'size':len(driver_raw.encode())}],
        'driver_responses':[{'finding_number':i+1,'disposition':'UNRESOLVED',
            'response':'Distinct response '+str(i)+' remains. '*25} for i in range(2)]})
    if mutation=='disposition_session':disposition['payload']['responds_to_session']='another-session'
    elif mutation=='changed_response':disposition['payload']['driver_responses'][0]['response']+=' Changed.'
    elif mutation=='unknown_response_field':disposition['payload']['driver_responses'][0]['extra']='Must remain.'
    elif mutation=='missing_review_link':disposition['payload']['responds_to_review_event']='e'*64
    elif mutation=='wrong_descriptor':disposition['payload']['response_evidence'][0]['size']+=1
    tail=event('DISPOSITION',3,deepcopy(disposition['payload']))
    packet['scientific_change_history']['current_requests']={rid:{
        'schema':history.CURRENT_VIEW,'reviewed_boundary':{'event_count':2},
        'native_event_count':3,'events':[review,disposition,tail],
        'literal_resolution_reports':{}}}
    literals=packet['scientific_change_history']['literal_response_originals']
    literals.update({response_sha:response_raw,driver_sha:driver_raw})
    if mutation=='missing_response':del literals[response_sha]
    elif mutation=='missing_driver':del literals[driver_sha]
    return packet,rid,response_sha,driver_sha


def resolve(packet,reference):
    value=packet
    for key in reference['literal_path_in_task_state']:
        value=value[key]
    if reference['schema']=='same-prompt-current-driver-responses/v1':
        value=[{key:row[target] for key,target in reference['fields'].items()} for row in value]
    assert hashlib.sha256(changes.encoded(value)).hexdigest()==reference['value_sha256']
    return value


def test_current_caller_has_exact_reachable_driver_review_and_disposition_literals(current_packet):
    packet,rid,response,driver=build(current_packet);before=deepcopy(packet)
    shown=current.presentation(packet,SOURCE)
    literals=shown['scientific_change_history']['literal_response_originals']
    rows=literals[driver]['value']['findings_and_responses']
    assert [resolve(shown,row['finding_verbatim']) for row in rows]==FINDINGS
    events=shown['scientific_change_history']['current_requests'][rid]['events']
    assert resolve(shown,events[0]['payload']['findings'])==FINDINGS
    assert resolve(shown,events[1]['payload']['driver_responses'])==before['scientific_change_history']['current_requests'][rid]['events'][1]['payload']['driver_responses']
    assert events[1]['payload']['rationale']=='Distinct explanation must remain.'
    assert events[1]['payload']['authority_reference']=='Preserve authority.'
    assert events[2]==before['scientific_change_history']['current_requests'][rid]['events'][2]
    assert packet==before
    assert literals[response]['value']['structured_output']['verdict']=='REQUEST_CHANGES'


@pytest.mark.parametrize('mutation',['missing_response','missing_driver','driver_session','driver_source',
    'driver_scope','driver_verdict','approval_claim','unknown_schema','wrong_quote','wrong_number',
    'wrong_actor','disposition_session','changed_response','unknown_response_field','missing_review_link',
    'wrong_descriptor'])
def test_unsupported_or_unbound_driver_response_remains_literal(current_packet,mutation):
    packet,rid,response,driver=build(current_packet,mutation)
    before=deepcopy(packet)
    shown=current.presentation(packet,SOURCE)
    assert shown['scientific_change_history']['current_requests'][rid]['events'][1]['payload']['driver_responses']==before['scientific_change_history']['current_requests'][rid]['events'][1]['payload']['driver_responses']
    assert packet==before
    if mutation=='unknown_schema':
        assert shown['scientific_change_history']['literal_response_originals'][driver]==before['scientific_change_history']['literal_response_originals'][driver]


@pytest.mark.parametrize('body',['# Original160\nREQUEST_CHANGES: full unsupported Markdown remains.','null','[]','23',
    '{"schema":"unknown","condition":"Do not execute."}',
    '{"schema":"independent-direction-and-driver-response/v1","schema":"unknown"}'])
def test_unknown_and_unsupported_originals_remain_exact_strings(current_packet,body):
    packet,_,_,_=build(current_packet)
    identity=hashlib.sha256(body.encode()).hexdigest()
    packet['scientific_change_history']['literal_response_originals'][identity]=body
    assert current.presentation(packet,SOURCE)['scientific_change_history']['literal_response_originals'][identity]==body


@pytest.mark.parametrize('fault',['missing','changed','reference'])
def test_changed_same_prompt_target_cannot_validate_as_original_view(current_packet,fault):
    packet,_,response,driver=build(current_packet)
    view=dc.selected_packet_view(packet,SOURCE)
    literals=view['scientific_change_history']['literal_response_originals']
    if fault=='missing':del literals[response]
    elif fault=='changed':literals[response]['value']['structured_output']['findings'][0]+=' Changed.'
    else:literals[driver]['value']['findings_and_responses'][0]['finding_verbatim']['value_sha256']='0'*64
    with pytest.raises(ValueError):dc.validate_selected_packet_view(view,packet,SOURCE)
