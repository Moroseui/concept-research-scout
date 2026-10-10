"""Native accepted-submission qualification and stage outcome, with labelled synthetic reviews."""
import json
from pathlib import Path
import pytest
from orchestrator import item4_smoke_review as smoke,item4_review4_continuation as x,private_records as pr
from orchestrator import review_submission as rs
from test_item4_smoke_review_calls import smoke_ready,extended,fifth,accepted,mechanical,fourth,third,setup,second,continuation,base_setup
from test_author_revision_accounting import review

@pytest.fixture
def completed(smoke_ready,monkeypatch,request):
    f,p,_=smoke_ready;store,batch,c,d,*_=f
    value=x.state(store);verdict=request.node.callspec.params.get('verdict','APPROVE')
    work,_=review(store,c,11,verdict=verdict)
    value.update(phase='MODEL_RUNNING',pending={'id':smoke.CALL,'stage':'run_spec_review','round':11,'workspace':str(work)})
    store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
    pr.atomic(work/'input-measurement.json',{'synthetic_fixture':True})
    checked=[]
    monkeypatch.setattr(smoke,'verify_delivered',lambda *args:checked.append(args[2]))
    d.save=lambda v:store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(v),))
    d.status=lambda:x.state(store)
    criticisms=[];d.criticism=lambda *args:criticisms.append(args)
    return d,value,work,p,checked,criticisms


@pytest.mark.parametrize('verdict',['APPROVE','REVISE','REJECT'])
def test_genuine_verdict_keeps_original_approval_and_never_releases_full(completed,verdict):
    d,value,work,p,checked,criticisms=completed
    old=json.loads(p['original_state']);raw=(work/'review.json').read_bytes()
    result=smoke.finish(d,value,p,'d'*64)
    assert checked==[work]
    assert result['review']==old['review']
    assert result.get('spec_review')==old.get('spec_review')
    assert result.get('reviewed_execution')==old.get('reviewed_execution')
    assert 'pending' not in result and result['rounds']['run_spec_review']==11
    assessment=result['smoke_review'];assert assessment['verdict']==verdict
    assert not assessment['full_training_admitted'] and not assessment['whole_plan_complete'] and not assessment['coverage_released']
    assert (d.state/'smoke-review11/review.json').read_bytes()==raw
    if verdict=='APPROVE':
        assert result['phase']=='EXECUTE_EXPERIMENT' and not criticisms
        assert result['reason']=='SMOKE_ASSESSED_FULL_AND_COVERAGE_HELD'
    else:
        assert result['phase']=='BLOCKED' and result['reason']=='SMOKE_REVIEW_'+verdict
        assert criticisms==[('run_spec_review',11,raw)]
    with pytest.raises(ValueError):smoke.finish(d,result,p,'d'*64)


@pytest.mark.parametrize('fault',['prompt.md','review.json','console.log',rs.RECORD,rs.CONFIG,'pending','status','delivery'])
def test_forged_or_undelivered_result_is_never_accepted(completed,monkeypatch,fault):
    d,value,work,p,checked,criticisms=completed
    if fault=='pending':value['pending']['id']='0'*64
    elif fault=='status':d.store.db.execute("UPDATE manual_calls SET status='UNCERTAIN' WHERE id=?",(smoke.CALL,))
    elif fault=='delivery':
        def refuse(*args):raise ValueError('MISSING_GENUINE_DELIVERY')
        monkeypatch.setattr(smoke,'verify_delivered',refuse)
    else:
        target=work/fault;target.chmod(0o600);pr.write_bytes(target,target.read_bytes()+b' ')
    with pytest.raises(ValueError):smoke.finish(d,value,p,'d'*64)
    assert 'smoke_review' not in value and not criticisms
    assert not (d.state/'smoke-review11/assessment.json').exists()
