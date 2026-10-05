
from copy import deepcopy
import hashlib
import os
import pytest
from orchestrator import scientific_evidence_access as access
from orchestrator import current_scientific_input as current, disposition_context as dc
from orchestrator.hosted_cycle import encoded
from orchestrator.handover_coordinator import digest
from test_current_input_integration import current_packet
from test_current_successor_history import next_packet
from test_linked_input_integration import integrated
from test_selected_scientific_history import captured
from test_campaign_grounding_presentation import example
from test_disposition_context import SOURCE


def task_capture(e):
    packet,_,_=next_packet(e,'TASK')
    selected=packet['reviewer_evidence']['input_evidence']
    event=selected['investigator_wake']['events'][0]
    native={'event':deepcopy(event),
        'packet':{'campaign_task':{'mode':'discuss','request':'Synthetic original science.'}},
        'review':{'verdict':'REQUEST_CHANGES'},
        'disposition':{'scope':'Synthetic original disposition; not accepted.'},
        'references':[],
        'predecessor':{'task':event['identity'],'source':'b'*40},
        'original_answers':{'continuation':'Synthetic original author.',
                            'review':'Synthetic original adverse review.',
                            'disposition':'Synthetic original DEFER; preserve criticism.'},
        'original_receipts':{stage:{'stage':stage,'session_id':'synthetic-'+stage,
                                   'actual_model':'synthetic-model'} for stage in ('continuation','review','disposition')}}
    row={k:v for k,v in native.items() if k not in ('packet','original_answers','original_receipts')}
    row.update(original_task=native['packet']['campaign_task'],
               original_packet_sha256=hashlib.sha256(encoded(native['packet'])).hexdigest())
    selected['verified_events']=[deepcopy(row)]
    packet=dc.capture_current_history(e.config,packet)
    cap=access.capture_task_changes(e.config['change_request_store'],packet,source=SOURCE)
    return packet,cap,native


def test_native_task_outputs_are_independently_readable(current_packet,monkeypatch,tmp_path):
    e=current_packet;packet,cap,native=task_capture(e);calls=[]
    def reader(config,identity,client,**kwargs):
        assert kwargs=={'include_originals':True};calls.append(identity)
        return deepcopy(native)
    monkeypatch.setattr('orchestrator.investigator_wakes._task',reader)
    # Native task cryptographic validation has its own tests. This seam supplies
    # that reader's result; export, bindings, cache and independent read are real.
    result=access.capture_tasks(cap,e.config,packet,original_client=lambda *a:None)
    desc=access.write_capture(tmp_path/'cache',result)
    r=access.Reader(tmp_path/'cache',desc['manifest_sha256'],source=SOURCE,
                    task_binding=desc['task_binding'],owner=os.getuid())
    for role,stage in [('author','continuation'),('reviewer','review'),('disposition','disposition')]:
        name='result/'+native['event']['identity']+'/'+role+'.original.txt'
        row=next(v for v in r.records if v['name']==name)
        assert r._body(row)==native['original_answers'][stage]
        assert row['provenance']['original_receipt']==native['original_receipts'][stage]
    assert calls==[native['event']['identity']]
    assert cap!=result and len(result['manifest']['records'])==len(cap['manifest']['records'])+5


@pytest.mark.parametrize('fault',['capture_source','task_binding','wake','event','review','task','packet_hash','duplicate','missing_original'])
def test_changed_task_or_original_binding_refuses(current_packet,monkeypatch,fault):
    e=current_packet;packet,cap,native=task_capture(e);native=deepcopy(native)
    if fault=='capture_source':cap['manifest']['source']='0'*40
    elif fault=='task_binding':cap['manifest']['task_binding']='0'*64
    elif fault=='wake':packet['reviewer_evidence']['input_evidence']['investigator_wake']['events']=[]
    elif fault=='event':native['event']['original_sha256']='0'*64
    elif fault=='review':native['review']['verdict']='APPROVE'
    elif fault=='task':native['packet']['campaign_task']['request']='Changed science.'
    elif fault=='packet_hash':native['packet']['extra']='Changed packet.'
    elif fault=='duplicate':
        evidence=packet['reviewer_evidence']['input_evidence']
        evidence['verified_events']*=2;evidence['investigator_wake']['events']*=2
    else:del native['original_answers']['review']
    if fault in ('wake','duplicate'):
        cap['manifest']['task_binding']=hashlib.sha256(encoded(packet)).hexdigest()
    monkeypatch.setattr('orchestrator.investigator_wakes._task',lambda *a,**kw:native)
    with pytest.raises((ValueError,KeyError)):
        access.capture_tasks(cap,e.config,packet,original_client=lambda *a:None)
