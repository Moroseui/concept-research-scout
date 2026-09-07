from datetime import datetime,timezone
import pytest
from orchestrator.handover_coordinator import Coordinator,encoded,digest
from orchestrator.operations_report import immutable


def binding(i,stages=None,deps=None):
    return {'id':format(i,'064x'),'source':'a'*40,'kind':'astra_turn','thread':'primary',
            'dependencies':deps or [],'stages':stages or ['review','disposition']}


def test_review_survives_disposition_failure_and_late_receipt(tmp_path):
    calls=[]
    def review(*args):calls.append('review');return {'verdict':'APPROVE'}
    def fail(*args):calls.append('disposition');raise RuntimeError('uncertain transport')
    handlers={'review':review,'disposition':fail};admit=lambda b:{'status':'ADMITTED'}
    q=Coordinator(tmp_path,handlers,admit);b=binding(1);q.submit(b)
    assert q.tick()['status']=='BLOCKED'
    restarted=Coordinator(tmp_path,handlers,admit)
    assert restarted.reconcile(b['id'])['status']=='UNCERTAIN_STAGE_RECONCILE_NO_RETRY'
    assert restarted.tick()['status']=='WAITING_FOR_ELIGIBLE_WORK'
    # Trusted handler recovered its original completed disposition, not reconstructed.
    value={'binding':digest(b),'position':1,'output':{'status':'recorded'},'output_sha256':digest({'status':'recorded'})}
    immutable(tmp_path/(b['id']+'-1.json'),encoded(value))
    restarted.reconcile(b['id']);assert restarted.tick()['status']=='COMPLETE'
    assert calls==['review','disposition']
    assert restarted.submit(b)['duplicate']
    assert restarted.tick()['status']=='WAITING_FOR_ELIGIBLE_WORK'


def test_pause_status_stale_controls_and_independent_work(tmp_path):
    calls=[]
    q=Coordinator(tmp_path,{'review':lambda *a:calls.append(1) or {'ok':True}},lambda b:{'status':'ADMITTED'})
    q.submit(binding(1,['review'],[format(99,'064x')]))
    q.submit(binding(2,['review']))
    request={'id':'pause-1','expected_revision':0,'action':'pause'}
    with pytest.raises(ValueError):q.control(request,authenticated_operator=False)
    q.control(request,authenticated_operator=True)
    assert q.tick()['status']=='PAUSED';before=q.status();assert before==q.status()
    assert q.control(request,authenticated_operator=True)['duplicate']
    with pytest.raises(ValueError,match='STALE'):q.control({'id':'old','expected_revision':0,'action':'resume'},authenticated_operator=True)
    q.control({'id':'resume-1','expected_revision':1,'action':'resume'},authenticated_operator=True)
    assert q.tick()['status']=='COMPLETE';assert calls==[1]
    assert q.status()['tasks'][0]['reason']=='WAITING_DEPENDENCIES'


def test_nightly_dedup_and_no_review_recursion(tmp_path):
    q=Coordinator(tmp_path,{'review':lambda *a:{'ok':True}},lambda b:{'status':'ADMITTED'})
    b={**binding(1,['review']),'kind':'nightly_review'}
    now=datetime(2026,9,7,2,tzinfo=timezone.utc)
    assert q.schedule(now,'America/New_York',21,0,b)['status']=='SCHEDULED'
    q.tick()
    assert q.schedule(now,'America/New_York',21,0,b)['status']=='ALREADY_SCHEDULED'
