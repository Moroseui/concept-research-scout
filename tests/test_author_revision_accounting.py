"""Synthetic native-MCP traces with real local/global admission, no model calls."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import author_revision_accounting as a, review_submission as rs
from orchestrator import private_records as pr, experiment_approval as approval
from orchestrator.manual_executor import digest, Accounts
from test_scoped_revisions_limits import configured, seed
from test_manual_lane import policy


@pytest.fixture
def setup(tmp_path, monkeypatch):
    store,batch,c=configured(tmp_path)
    c.update(source='a'*40,clients={'runtime_config_sha256':'b'*64})
    pr.atomic(Path(store.path).parent/'lane.json',c)
    monkeypatch.setattr('orchestrator.connectivity.require',lambda *a,**k:{'synthetic':True})
    return store,batch,c


def failed_authors(store,c,count=4):
    for _ in range(count):
        ident,n,receipt=store.reserve_call(c['run_id'],'run_spec_author',c['source'],'astra/manual-test',policy(),{})
        store.finish_call(ident,receipt,'FAILED')


def review(store,c,n=1,verdict='REVISE',category='metric/statistic'):
    stage='run_spec_review';state=Path(store.path).parent
    work=state.parent/(state.name+'-scientific-workspaces')/(stage+'-'+str(n))
    pr.mkdir(work,parents=True)
    prompt=b'Synthetic accounting fixture; no scientific result.\n'
    pr.write_bytes(work/'prompt.md',prompt)
    ident=digest((c['run_id']+':'+stage+':'+str(n)).encode())
    bindings={'call_id':ident,'run_id':c['run_id'],'stage':stage,'source_sha':c['source'],
              'runtime_sha256':c['clients']['runtime_config_sha256'],'input_sha256':digest(prompt)}
    pins=rs.prepare(work,'scientific',bindings)
    findings=[] if verdict=='APPROVE' else [{'id':'F1','category':category,'text':'Synthetic finding',
        'evidence':'Synthetic fixture','resolution':'Address synthetic finding'}]
    decision={'verdict':verdict,'findings':findings,'rationale':'Synthetic fixture, not research judgment.', 'bindings':bindings}
    ack=rs.submit(work,pins['config_sha256'],decision)
    events=[{'type':'assistant','session_id':'synthetic','message':{'content':[
                {'type':'tool_use','id':'submit-1','name':rs.TOOL,'input':decision}]}},
            {'type':'user','session_id':'synthetic','message':{'content':[
                {'type':'tool_result','tool_use_id':'submit-1','content':json.dumps(ack)}]}},
            {'type':'result','subtype':'success','is_error':False,'session_id':'synthetic'}]
    console=b'\n'.join(rs.canonical(x) for x in events)
    pr.write_bytes(work/'console.log',console)
    receipt={'stage':stage,'workspace':str(work),'input_sha256':digest(prompt),'submission_preflight':pins,
        'native':{'review_submission':rs.collect_scientific(work,console),'console_sha256':digest(console)},
        'outcome':'COMPLETE','output_sha256':{'review.json':digest((work/'review.json').read_bytes())}}
    got,attempt,charged=store.reserve_call(c['run_id'],stage,c['source'],'astra/manual-test',policy(),receipt)
    assert got==ident and attempt==n
    store.finish_call(ident,charged,'COMPLETE')
    state_value={'phase':'run_spec_author','reason':'REVISION_REQUIRED','review':str(work/'review.json')}
    store.db.execute('INSERT OR REPLACE INTO manual_state VALUES(1,?)',(json.dumps(state_value),))
    return work,state_value


def reserve(store,c,receipt=None):
    return store.reserve_call(c['run_id'],'run_spec_author',c['source'],'astra/manual-test',policy(),receipt or {})


def test_four_failures_do_not_consume_genuine_revision_slots(setup):
    store,batch,c=setup;failed_authors(store,c)
    originals=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls')]
    with pytest.raises(ValueError,match='STEP_D_MODEL_CALL_LIMIT'):reserve(store,c)
    review(store,c)
    ident,n,receipt=reserve(store,c)
    assert n==5 and receipt[a.FIELD]['review_round']==1
    assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid LIMIT 4')]==originals
    assert Accounts(store).read()[1]['count']==6
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==6
    store.finish_call(ident,receipt,'COMPLETE')
    with pytest.raises(ValueError,match='AUTHOR_REVISION_NEW_REVIEW_REQUIRED'):reserve(store,c)


def test_three_revisions_not_three_total_authors(setup):
    store,batch,c=setup;failed_authors(store,c)
    for n in range(1,4):
        review(store,c,n)
        ident,ordinal,receipt=reserve(store,c)
        assert ordinal==4+n and receipt[a.FIELD]['review_round']==n
        store.finish_call(ident,receipt,'COMPLETE')
    review(store,c,4)
    with pytest.raises(ValueError,match='AUTHOR_REVISION_NEW_REVIEW_REQUIRED'):reserve(store,c)


@pytest.mark.parametrize('verdict,category',[('APPROVE','metric/statistic'),('REJECT','metric/statistic'),
    ('REVISE','privacy/secret'),('REVISE','test-set/leakage'),('REVISE','budget')])
def test_non_actionable_or_protected_review_cannot_unlock_author(setup,verdict,category):
    store,batch,c=setup;failed_authors(store,c);review(store,c,verdict=verdict,category=category)
    before=store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]
    with pytest.raises(ValueError,match='AUTHOR_GENUINE_ACTIONABLE_REVISE_REQUIRED'):reserve(store,c)
    assert store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==before


@pytest.mark.parametrize('target',['review.json','console.log',rs.RECORD,rs.CONFIG,'prompt.md'])
def test_changed_native_proof_cannot_unlock_author(setup,target):
    store,batch,c=setup;failed_authors(store,c);work,_=review(store,c)
    path=work/target;path.chmod(0o600);pr.write_bytes(path,path.read_bytes()+b' ')
    with pytest.raises(ValueError):reserve(store,c)
    assert store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==5


def test_revise_can_never_be_used_as_execution_approval(setup):
    store,batch,c=setup;work,_=review(store,c)
    driver=SimpleNamespace(store=store,state=Path(store.path).parent,config=c)
    pending={'stage':'run_spec_review','round':1,'workspace':str(work),
        'id':digest((c['run_id']+':run_spec_review:1').encode())}
    with pytest.raises(ValueError,match='EXPERIMENT_APPROVAL_REQUIRED'):
        approval.review_delivery(driver,pending,'run_spec_review')


def test_false_caller_classification_refused(setup):
    store,batch,c=setup
    with pytest.raises(ValueError,match='AUTHOR_REVISION_CALLER_CLASSIFICATION_REFUSED'):
        reserve(store,c,{a.FIELD:{'forged':True}})
    assert Accounts(store).read()[1]['count']==0


def test_successful_acceptance_does_not_use_failed_attempt_slot(setup):
    store,batch,c=setup;ident,n,receipt=reserve(store,c)
    receipt['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,receipt,'COMPLETE')
    driver=SimpleNamespace(store=store,config=c)
    a.accepted(driver,{'id':ident,'stage':'run_spec_author','round':n})
    failed_authors(store,c,4)
    assert a.inspect(store,c['run_id'],'run_spec_author')['failed_attempts']==4
    with pytest.raises(ValueError,match='STEP_D_MODEL_CALL_LIMIT'):reserve(store,c)
    assert Accounts(store).read()[1]['count']==5


def test_complete_without_host_acceptance_still_counts_as_failure(setup):
    store,batch,c=setup
    for _ in range(4):
        ident,n,receipt=reserve(store,c);store.finish_call(ident,receipt,'COMPLETE')
    with pytest.raises(ValueError,match='STEP_D_MODEL_CALL_LIMIT'):reserve(store,c)


@pytest.mark.parametrize('kind',['day','batch','run','uncertain'])
def test_other_admission_refusals_survive_revision(setup,kind):
    from datetime import datetime,timezone
    store,batch,c=setup;failed_authors(store,c);review(store,c)
    if kind=='day':
        seed(batch,45,kind='implementation_review',day=datetime.now(timezone.utc).date().isoformat())
        expected='AUTONOMY_DAILY_CALL_LIMIT'
    elif kind=='batch':
        seed(batch,55);expected='AUTONOMY_BATCH_CALL_LIMIT'
    elif kind=='run':
        for i in range(11):store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',
            ('extra-'+str(i),'result_interpretation_author',i+1,'FAILED','{}'))
        expected='STEP_D_MODEL_CALL_LIMIT'
    else:
        store.db.execute("UPDATE manual_calls SET status='UNCERTAIN' WHERE attempt=1 AND stage='run_spec_author'")
        expected='UNCERTAIN_MODEL_CALL_NO_RETRY'
    with pytest.raises(ValueError,match=expected):reserve(store,c)


def test_bare_item_number_cannot_enable_revision_policy(setup):
    store,batch,c=setup;c.update(item_number=4,backend='modal')
    pr.atomic(Path(store.path).parent/'lane.json',c)
    with pytest.raises(ValueError,match='ANALYSIS_REVISION_POLICY_SCOPE'):reserve(store,c)
    assert Accounts(store).read()[1]['count']==0
