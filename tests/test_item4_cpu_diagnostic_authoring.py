"""Bounded diagnostic authoring; synthetic accounting and delta refusals only."""
import json
import copy
import pytest
from orchestrator import item4_smoke_response as post,item4_scoped_calls as scoped
from orchestrator import item4_review4_continuation as x,author_revision_accounting as a
from orchestrator import autonomy_limits as limits,manual_recovery,experiment_collection
from orchestrator.manual_executor import ManualExecutor,Accounts
from orchestrator.autonomy_accounting import BatchAccounts
from test_item4_smoke_response import (response_ready,accepted_author,smoke_ready,extended,fifth,
    accepted,mechanical,fourth,third,setup,second,continuation,base_setup)
from test_author_revision_accounting import review
from test_manual_lane import policy


def baseline():
    return {'fits':[{'fit_id':'old','stage':'SMOKE','arm':'base','fold':0,'preprocessing_id':'prep'},
        {'fit_id':'full','stage':'FULL','arm':'base','fold':0,'preprocessing_id':'prep'}],
        'full_training':{'resume_fit_id':'old'},'other':'unchanged'}


def diagnostic_plan():
    p=baseline()
    p['fits'] += [dict(p['fits'][0],fit_id='cpu-A'),dict(p['fits'][0],fit_id='cpu-B')]
    return p


@pytest.fixture
def diagnostic_ready(request,monkeypatch):
    connect=scoped.connect
    originals=[(o,k,getattr(o,k)) for o,k in [(limits,k) for k in
        ('local_limit','global_limit','allowance','cap_authority','scientific_batch_allowance')]+
        [(ManualExecutor,'reserve_call'),(BatchAccounts,'reserve_scientific')]]
    old=request.getfixturevalue('response_ready');f,smoke,post_p,_=old;store,batch,c,d,*_=f
    accepted_author(old)
    value=x.state(store)
    work,_=review(store,c,12,category='budget')
    value.update(phase='MODEL_RUNNING',pending={
        'id':post.REVIEW,'stage':'run_spec_review','round':12,'workspace':str(work)})
    post.finish_review(d,value,post_p,'c'*64)
    raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    pins=lambda db,sql:{r['id']:x.sha(x.canonical(dict(r))) for r in db.execute(sql)}
    plan=x.canonical(baseline())
    p={'schema':post.DIAGNOSTIC_SCHEMA,'run_id':x.RUN,'authority_sha256':x.AUTHORITY,
        'author_attempt':16,'review_attempt':13,'run_limit':31,'batch_limit':69,'execution_authorized':False,
        'configuration_sha256':x.sha((d.state/'lane.json').read_bytes()),'original_state':raw,'state_sha256':x.sha(raw.encode()),
        'local_calls':pins(store.db,'SELECT * FROM manual_calls ORDER BY rowid'),
        'global_calls':pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' AND change_id='"+x.RUN+"' ORDER BY rowid"),
        'batch_calls':pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid"),
        'assessment':value['post_smoke_response'],'assessment_sha256':x.sha(x.canonical(value['post_smoke_response'])),
        'operator_decision_sha256':post.DIAGNOSTIC_DECISION,'diagnostic_micro_usd':25_000_000,
        'stage1_micro_usd':150_000_000,'projection_micro_usd':1_200_000_000,'total_micro_usd':1_275_000_000,
        'automatic_retry':False,'baseline_plan':plan.decode(),'baseline_plan_sha256':x.sha(plan),
        'baseline_module_sha256':x.sha(b'baseline')}
    for o,k,fn in originals:monkeypatch.setattr(o,k,fn)
    monkeypatch.setattr(scoped,'_validate',None)
    old_grant=request.getfixturevalue('fourth')[4];mechanic=request.getfixturevalue('mechanical')[4]
    _,saved=request.getfixturevalue('extended')
    connect(old_grant,'b'*64,mechanical=mechanic,mechanical_approval='a'*64,
        response=f[4],response_approval='9'*64,batch_extension=saved['extension'],batch_approval='e'*64,
        smoke=smoke,smoke_approval='d'*64,post_smoke=post_p,post_smoke_approval='c'*64,
        diagnostic=p,diagnostic_approval='8'*64)
    assert limits.local_limit(store,x.RUN,policy())==29
    post.activate(d,p,'8'*64,d.state/'cpu-diagnostic-authoring')
    return f,p


def test_preserves_calls_and_final_pair(diagnostic_ready,monkeypatch):
    f,p=diagnostic_ready;store,batch,c,d,*_=f
    before=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    ident,n,receipt=store.reserve_call(x.RUN,'run_spec_author',c['source'],'astra/manual-test',policy(),{})
    assert n==16 and ident==post.call(p,'author')
    assert receipt['batch_accounting']['run_limit']==31 and receipt['batch_accounting']['batch_limit']==69
    receipt['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,receipt,'COMPLETE')
    a.accepted(d,{'id':ident,'stage':'run_spec_author','round':16})
    value=x.state(store);value.update(phase='run_spec_review',rounds={'run_spec_author':16,'run_spec_review':12});d.save(value)
    checked=[]
    def candidate(*args):
        checked.append(True)
        return post.validate_diagnostic_delta(x.canonical(diagnostic_plan()),b'new executable',p)
    monkeypatch.setattr(post,'executable_candidate',candidate)
    assert manual_recovery.role_limit(store,x.RUN,'run_spec_review')==13
    value=x.state(store)
    work,_=review(store,c,13,verdict='APPROVE')
    value.update(phase='MODEL_RUNNING',pending={
        'id':post.call(p,'review'),'stage':'run_spec_review','round':13,'workspace':str(work)})
    result=post.finish_review(d,value,p,'8'*64)
    assert checked and result['reason']=='CPU_DIAGNOSTIC_AUTHORING_APPROVE_EXECUTION_HELD'
    assert result['cpu_diagnostic_authoring']['execution_authorized'] is False
    assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')][:27]==before
    assert Accounts(store).read()[1]['count']==29
    value=x.state(store);value.update(phase='result_interpretation_author');d.save(value)
    counted=Accounts(store).read()
    with pytest.raises((ValueError,KeyError,FileNotFoundError)):
        store.reserve_call(x.RUN,'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
    assert Accounts(store).read()==counted
    monkeypatch.setattr(experiment_collection,'verified',lambda *args:None)
    rounds={'run_spec_author':16,'run_spec_review':13}
    for stage in ('result_interpretation_author','result_interpretation_review'):
        value=x.state(store);value.update(phase=stage,rounds=dict(rounds));d.save(value)
        ident,n,r=store.reserve_call(x.RUN,stage,c['source'],'astra/manual-test',policy(),{})
        r['output_sha256']={'interpretation.md':'f'*64};store.finish_call(ident,r,'COMPLETE');rounds[stage]=1
        if stage.endswith('author'):a.accepted(d,{'id':ident,'stage':stage,'round':1})
    assert Accounts(store).read()[1]['count']==31
    assert batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]==69
    post.originals(store,p,'8'*64)


@pytest.mark.parametrize('fault',['daily','uncertain','old-local','old-global','grant','execution','duplicate'])
def test_diagnostic_admission_refusals_preserve_accounting(diagnostic_ready,fault):
    f,p=diagnostic_ready;store,batch,c,d,*_=f
    if fault=='daily':
        from datetime import datetime,timezone
        from test_scoped_revisions_limits import seed
        day=datetime.now(timezone.utc).date().isoformat();n=batch.db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(day,)).fetchone()[0]
        seed(batch,50-n,kind='implementation_review',day=day)
    elif fault=='uncertain':batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('new-uncertain','review','other',1,'2000-01-01','UNCERTAIN','{}','{}'))
    elif fault in ('old-local','old-global'):
        db,table,pins=(store.db,'manual_calls',p['local_calls']) if fault=='old-local' else (batch.db,'autonomy_calls',p['batch_calls'])
        db.execute('UPDATE '+table+" SET receipt='altered' WHERE id=?",(next(iter(pins)),))
    elif fault=='grant':store.db.execute('DELETE FROM events WHERE id=?',(post.profile(p)['event'],))
    elif fault=='execution':
        value=x.state(store);value['execution_package']={'changed':True};d.save(value)
    before=Accounts(store).read()
    with pytest.raises(ValueError):
        if fault=='duplicate':post.activate(d,p,'8'*64,d.state/'second-diagnostic')
        else:store.reserve_call(x.RUN,'run_spec_author',c['source'],'astra/manual-test',policy(),{})
    assert Accounts(store).read()==before


@pytest.mark.parametrize('fault',['unchanged-code','unchanged-plan','removed-fit','changed-full','changed-baseline','extra-fit','other-arm','other-fold','full-stage','duplicate-id'])
def test_delta_refuses_prose_only_and_scientific_scope_changes(fault):
    p={'schema':post.DIAGNOSTIC_SCHEMA,'baseline_plan':x.canonical(baseline()).decode(),'baseline_module_sha256':x.sha(b'baseline')}
    plan=diagnostic_plan();module=b'changed module'
    if fault=='unchanged-code':module=b'baseline'
    elif fault=='unchanged-plan':plan=baseline()
    elif fault=='removed-fit':plan['fits'].pop(0)
    elif fault=='changed-full':plan['full_training']['resume_fit_id']='changed'
    elif fault=='changed-baseline':plan['fits'][0]['fold']=1
    elif fault=='extra-fit':plan['fits'].append(dict(plan['fits'][-1],fit_id='third'))
    elif fault=='other-arm':plan['fits'][-1]['arm']='coverage'
    elif fault=='other-fold':plan['fits'][-1]['fold']=1
    elif fault=='full-stage':plan['fits'][-1]['stage']='FULL'
    else:plan['fits'][-1]['fit_id']='old'
    with pytest.raises(ValueError):post.validate_diagnostic_delta(x.canonical(plan),module,p)


def test_delta_accepts_only_structural_candidate_not_execution():
    p={'schema':post.DIAGNOSTIC_SCHEMA,'baseline_plan':x.canonical(baseline()).decode(),'baseline_module_sha256':x.sha(b'baseline')}
    result=post.validate_diagnostic_delta(x.canonical(diagnostic_plan()),b'changed module',p)
    assert result['fit_ids']==['cpu-A','cpu-B'] and result['execution_authorized'] is False


def test_scope_never_raises_financial_caps_or_enables_retry(diagnostic_ready):
    _,p=diagnostic_ready
    for key,replacement in [('run_limit',32),('batch_limit',70),('author_attempt',17),('review_attempt',14),
            ('diagnostic_micro_usd',25_000_001),('stage1_micro_usd',150_000_001),
            ('projection_micro_usd',1_200_000_001),('total_micro_usd',1_275_000_001),
            ('automatic_retry',True),('execution_authorized',True),('operator_decision_sha256','f'*64)]:
        with pytest.raises(ValueError):post.scope({**p,key:replacement},'8'*64)
    assert limits.DAILY==50 and limits.SCIENTIFIC_BATCH==60
