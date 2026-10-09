"""Real interrupted-fit ledger -> driver link -> ordinary admission.

Provider/storage/clock and prior scientific package assembly are labelled
synthetic. The terminal reader, accounting transaction, continuation validator
and resumed reservation are unpatched. Separate native tests cover the packet.
"""
import copy
import json
from types import SimpleNamespace as NS
import pytest
from orchestrator import experiment_continuation as continuation, experiment_dispatch as dispatch
from orchestrator import experiment_modal_package as bridge, private_records as pr
from orchestrator.modal_executor import canonical,item4_job
from orchestrator.manual_executor import digest
from test_modal_fit_monitor import monitored,advance_to_stop
from test_modal_fit_health import health
from test_modal_fit_result import connection
from test_modal_item4_provider import candidate
from test_modal_item4_budget import snapshot,NOW


@pytest.fixture
def interrupted(monitored,monkeypatch):
    e,j,ident,b,path,stops,log,progress,sandbox=monitored
    assert advance_to_stop(monitored)['status']=='INTERRUPTED_CHECKPOINT_PRESERVED'
    folder=e.path.parent/'fit-packages'/j/'prepared';pr.mkdir(folder,parents=True)
    pr.write_bytes(folder/'manifest.json',canonical({'binding':b,'synthetic_scientific_package':True}))
    # The genuine package bridge has dedicated unmocked source/approval tests.
    monkeypatch.setattr(bridge,'emit',lambda driver,value,package,binding:{'binding':binding})
    v={'phase':'EXECUTE_EXPERIMENT','fit_dispatch':{j:{'phase':'INTERRUPTED'}}};saves=[]
    d=NS(state=e.path.parent,store=e,config={'run_id':b['run_id']},
         save=lambda value:saves.append(copy.deepcopy(value)),status=lambda:{'phase':v['phase']})
    job={'job':j,'binding':b,'runtime':e.config,'initial_job':j}
    selected={'sha256':'a'*64,'jobs':[job]}
    return d,v,selected,job,e,stops


def test_real_interruption_link_reservation_and_repeated_resolution(interrupted):
    d,v,selected,job,e,stops=interrupted
    original=[tuple(r) for r in e.costs.db.execute('SELECT * FROM autonomy_compute')]
    assert continuation.schedule(d,v,job)['provider_called'] is False
    resolved=continuation.resolve(d,v,selected);successor=resolved['jobs'][0]
    assert successor['job']!=job['job'] and successor['binding']['experiment']['segment']==2
    assert successor['binding']['progress']==job['binding']['progress']
    assert successor['runtime']==job['runtime']
    assert resolved['all_jobs']==[job['job'],successor['job']]
    assert resolved['continuations'][0]['epoch_resumed_from']==0
    assert continuation.resolve(d,v,selected)==resolved
    assert original==[tuple(r) for r in e.costs.db.execute('SELECT * FROM autonomy_compute')]
    b=successor['binding'];ident=digest(canonical(b))
    assert e.costs.reserve_item4(ident,b['run_id'],b,billing_snapshot=snapshot(),now=NOW)
    assert not e.costs.reserve_item4(ident,b['run_id'],b,billing_snapshot=snapshot(),now=NOW)
    assert e.costs.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==2
    assert tuple(e.costs.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(original[0][0],)).fetchone())==original[0]
    assert stops==['sb-fit'] and e.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0


@pytest.mark.parametrize('damage',['active','uncertain','no-event','wrong-binding','wrong-provider','wrong-checkpoint','unclassified'])
def test_unproven_resume_refuses_without_reservation(interrupted,damage):
    d,v,selected,job,e,stops=interrupted;ident=digest(canonical(job['binding']))
    if damage in {'active','uncertain'}:
        e.costs.db.execute('UPDATE autonomy_compute SET status=? WHERE id=?',('RUNNING' if damage=='active' else 'UNCERTAIN',ident))
    elif damage=='no-event':e.costs.db.execute('DELETE FROM events WHERE id=?',(ident+':fit-interruption',))
    else:
        row=e.costs.db.execute('SELECT payload FROM events WHERE id=?',(ident+':fit-interruption',)).fetchone()
        record=json.loads(row[0])
        if damage=='wrong-binding':record['proof']['binding_sha256']='f'*64
        elif damage=='wrong-provider':record['proof']['provider_id']='sb-other'
        elif damage=='wrong-checkpoint':record['proof']['checkpoint_record_sha256']='f'*64
        else:record['resume_reason']='UNKNOWN'
        e.costs.db.execute('UPDATE events SET payload=? WHERE id=?',(json.dumps(record,sort_keys=True),ident+':fit-interruption'))
    before=[tuple(r) for r in e.costs.db.execute('SELECT * FROM autonomy_compute')]
    with pytest.raises(ValueError,match='^EXPERIMENT_RESUME_'):continuation.schedule(d,v,job)
    assert 'fit_continuations' not in v
    assert before==[tuple(r) for r in e.costs.db.execute('SELECT * FROM autonomy_compute')]


@pytest.mark.parametrize('damage',['event','job','status','unknown-fit'])
def test_saved_link_tampering_is_not_new_authority(interrupted,damage):
    d,v,selected,job,e,_=interrupted;continuation.schedule(d,v,job)
    link=v['fit_continuations'][job['job']][0]
    if damage=='event':link['event_sha256']='f'*64
    elif damage=='job':link['previous_job']='other'
    elif damage=='status':v['fit_dispatch'][job['job']]['phase']='COMPLETE'
    else:v['fit_continuations']['unselected']=[]
    with pytest.raises(ValueError,match='^EXPERIMENT_RESUME_'):continuation.resolve(d,v,selected)


def test_driver_schedules_exactly_one_resume_link_without_provider(interrupted,monkeypatch):
    d,v,selected,job,e,stops=interrupted
    monkeypatch.setattr(dispatch,'load',lambda *args:continuation.resolve(d,v,selected))
    result=dispatch.advance(d,v)
    assert result['next_action']=='PREPARE_CHECKPOINT_CONTINUATION' and result['same_realization']
    assert len(v['fit_continuations'][job['job']])==1
    with pytest.raises(ValueError,match='^EXPERIMENT_RESUME_LINK_ALREADY_RECONCILE$'):
        continuation.schedule(d,v,job)
    assert e.costs.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==1


def test_only_completed_active_segments_count_for_collection(interrupted):
    d,v,selected,job,*_=interrupted;continuation.schedule(d,v,job)
    resolved=continuation.resolve(d,v,selected);ident=resolved['jobs'][0]['job']
    assert not continuation.complete_states(resolved,v['fit_dispatch'])
    v['fit_dispatch'][ident]={'phase':'COMPLETE'}
    assert continuation.complete_states(resolved,v['fit_dispatch'])
    v['fit_dispatch'][job['job']]['phase']='COMPLETE'
    assert not continuation.complete_states(resolved,v['fit_dispatch'])
