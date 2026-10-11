"""Preserve two real-shaped failures while admitting one bounded review3."""
import copy,json
from pathlib import Path
import pytest
from orchestrator import colab_reader_recovery as m,private_records as pr,preparation_interleaving as pi
from test_colab_reader_recovery import fixture,APPROVAL

@pytest.fixture
def twice(fixture,monkeypatch):
    x=fixture;first=copy.deepcopy(x.f)
    m.activate(x.driver,first,APPROVAL)
    work=x.work.with_name('run_spec_review-2');pr.copytree(x.work,work)
    receipt=json.dumps({'error_type':'TerminalSubmissionFailure','reason':'ACCEPTED_SUBMISSION_REQUIRED','cost':5.72188325})
    x.store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(m.SECOND,m.STAGE,2,'FAILED',receipt))
    x.store.batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?)',(m.SECOND,'FAILED',receipt,'scientific',m.RUN,json.dumps({'source':'b'*40,'run_id':m.RUN,'stage':m.STAGE}),4))
    value=x.driver.current();value.update(phase='BLOCKED',reason=m.REASON,pending={'id':m.SECOND,'stage':m.STAGE,'round':2})
    raw=json.dumps(value,sort_keys=True);x.store.db.execute('UPDATE manual_state SET payload=?',(raw,))
    f=copy.deepcopy(first);f.update(schema='colab-review-turn-recovery/v1',failed_call=m.SECOND,next_review=3,max_turns=60,
        failed_workspace=str(work),state_sha256=m.sha(raw.encode()),original_state=value,
        local_rows=[dict(r) for r in x.store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')],
        global_rows=[dict(r) for r in x.store.batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid')])
    monkeypatch.setattr(m,'prior_document',lambda:copy.deepcopy(first))
    x.first=first;x.f=f;x.work=work
    return x


def scope(x):return {'source_sha':'b'*40,'lanes':{'colab_preparation':{'run_id':m.RUN,'state':str(x.lane)}},'ledger':str(x.batch)}

def test_one_review3_keeps_both_charges_and_original_attempts(twice):
    x=twice;before=x.driver.current()
    assert m.originals(x.store,x.f)
    assert m.activate(x.driver,x.f,APPROVAL)=={'status':'RESTORED_REVIEW3_NO_CALL','preserved_calls':4,'model_calls':0,'new_allowance':0}
    assert m.next_round(x.driver,x.driver.current(),x.f,APPROVAL,lambda v:99)==3
    assert x.driver.current()['rounds']==before['rounds']
    for db,table,rows in [(x.store.db,'manual_calls',x.f['local_rows']),(x.store.batch.db,'autonomy_calls',x.f['global_rows'])]:
        assert [dict(r) for r in db.execute('SELECT * FROM '+table+' ORDER BY rowid')]==rows
    assert (x.lane/m.EVENT/'COMPLETE.json').is_file() and (x.lane/m.TURN_EVENT/'COMPLETE.json').is_file()
    with pytest.raises(ValueError):m.activate(x.driver,x.f,APPROVAL)

@pytest.mark.parametrize('damage',['prior-charge','second-charge','prior-grant','prior-console','second-console','verdict','new-attempt','limit','turns','state'])
def test_drift_never_recovers_or_discounts(twice,damage):
    x=twice
    if damage in {'prior-charge','second-charge'}:
        x.store.batch.db.execute("UPDATE autonomy_calls SET receipt='{}' WHERE id=?",(m.FAILED if damage=='prior-charge' else m.SECOND,))
    elif damage=='prior-grant':x.store.db.execute('DELETE FROM events WHERE id=?',(m.EVENT,))
    elif damage=='prior-console':pr.write_text(Path(x.first['failed_workspace'])/'console.log','changed')
    elif damage=='second-console':pr.write_text(x.work/'console.log','changed')
    elif damage=='verdict':pr.write_text(x.work/'review.json','{"verdict":"REJECT"}')
    elif damage=='new-attempt':x.store.db.execute("INSERT INTO manual_calls VALUES('other','run_spec_review',3,'RUNNING','{}')")
    elif damage=='limit':x.f['run_limit']=9
    elif damage=='turns':x.f['max_turns']=61
    else:x.store.db.execute("UPDATE manual_state SET payload='{}'")
    before=x.store.db.execute('SELECT payload FROM manual_state').fetchone()[0]
    with pytest.raises((ValueError,KeyError)):m.activate(x.driver,x.f,APPROVAL)
    assert x.store.db.execute('SELECT payload FROM manual_state').fetchone()[0]==before
    assert not (x.lane/m.TURN_EVENT/'COMPLETE.json').exists()


def test_shared_history_keeps_both_failed_rows_and_default_refusal(twice,monkeypatch):
    x=twice
    for i in [2,3]:assert m.retained_review(scope(x),x.f['global_rows'][i],x.f['local_rows'][i],x.f)
    ident=pi.identity(m.RUN,m.STAGE,3)
    assert not m.extra_attempt(scope(x),m.RUN,m.STAGE,ident,x.f,APPROVAL)
    m.activate(x.driver,x.f,APPROVAL)
    assert pi.permitted_attempts(scope(x),m.RUN,m.STAGE)==(1,2)
    monkeypatch.setattr(pi,'_EXTRA_ATTEMPT',lambda s,r,st,i:m.extra_attempt(s,r,st,i,x.f,APPROVAL))
    assert pi.permitted_attempts(scope(x),m.RUN,m.STAGE)==(1,2,3)
    for run,stage in [('other',m.STAGE),(m.RUN,'run_spec_author'),(m.RUN,'result_interpretation_review')]:
        assert pi.permitted_attempts(scope(x),run,stage)==(1,2)
    assert not m.extra_attempt(scope(x),m.RUN,m.STAGE,pi.identity(m.RUN,m.STAGE,4),x.f,APPROVAL)

@pytest.mark.parametrize('damage',[None,'local','global','pending','work','stage','command','grant'])
def test_sixty_turns_only_after_exact_dual_admission(twice,damage):
    x=twice;m.activate(x.driver,x.f,APPROVAL);ident=pi.identity(m.RUN,m.STAGE,3)
    x.store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(ident,m.STAGE,3,'COMPLETE' if damage=='local' else 'RUNNING','{}'))
    x.store.batch.db.execute('INSERT INTO autonomy_calls(id,status) VALUES(?,?)',(ident,'COMPLETE' if damage=='global' else 'RUNNING'))
    value=x.driver.current();value['pending']={'id':ident,'stage':m.STAGE,'round':4 if damage=='pending' else 3}
    x.store.db.execute('UPDATE manual_state SET payload=?',(json.dumps(value),))
    if damage=='grant':x.store.db.execute('DELETE FROM events WHERE id=?',(m.TURN_EVENT,))
    argv=['claude','--max-turns','60' if damage=='command' else '30'];work=x.work.with_name('other' if damage=='work' else 'run_spec_review-3')
    action=lambda:m.review_command(x.driver,work,'run_spec_author' if damage=='stage' else m.STAGE,argv,x.f,APPROVAL)
    if damage:
        with pytest.raises(ValueError):action()
    else:
        assert action()==['claude','--max-turns','60']
        assert argv==['claude','--max-turns','30']


from test_preparation_interleaving import admitted_history,complete_fixture_call
from types import SimpleNamespace as NS

def test_real_admission_of_review3_keeps_four_original_calls(admitted_history,fixture,monkeypatch):
    scope,history,batch,locals,overlay=admitted_history
    local=locals['colab_preparation'];run=scope['lanes']['colab_preparation']['run_id'];lane=Path(local.path).parent
    monkeypatch.setattr(local,'batch',batch)
    monkeypatch.setattr(m,'RUN',run)
    monkeypatch.setattr(m,'FAILED',pi.identity(run,m.STAGE,1));monkeypatch.setattr(m,'SECOND',pi.identity(run,m.STAGE,2))
    for stage,attempt in [('run_spec_author',1),('run_spec_author',2),(m.STAGE,1),(m.STAGE,2)]:
        complete_fixture_call(scope,batch,local,'colab_preparation',stage,attempt)
    for ident,cost in [(m.FAILED,4.476676),(m.SECOND,5.72188325)]:
        receipt=json.dumps({'error_type':'TerminalSubmissionFailure','reason':'ACCEPTED_SUBMISSION_REQUIRED','cost':cost})
        for db,table in [(local.db,'manual_calls'),(batch.db,'autonomy_calls')]:
            db.execute('UPDATE '+table+" SET status='FAILED',receipt=? WHERE id=?",(receipt,ident))
    work=lane.parent/'lane-scientific-workspaces/run_spec_review-1';pr.copytree(fixture.work,work)
    pr.copytree(work,work.with_name('run_spec_review-2'))
    rows=[dict(r) for r in local.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    globals=[dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls WHERE change_id=? ORDER BY rowid',(run,))]
    first=copy.deepcopy(fixture.f);first.update(run_id=run,failed_call=m.FAILED,lane=str(lane),failed_workspace=str(work),
        configuration_sha256=m.sha((lane/'lane.json').read_bytes()),local_rows=rows[:3],global_rows=globals[:3])
    # Reconstruct the already-approved first recovery event without changing call records.
    grant=m.binding(first,APPROVAL);local.db.execute('INSERT INTO events VALUES(?,?,?)',(m.EVENT,run,m.canonical(grant).decode()))
    monkeypatch.setattr(m,'prior_document',lambda:copy.deepcopy(first))
    value={'phase':'BLOCKED','reason':m.REASON,'rounds':{'run_spec_author':2},
        'pending':{'id':m.SECOND,'round':2,'stage':m.STAGE},'artifacts':[],'spec':'unchanged',
        'notebook_revision_result':{'unchanged':True},'interventions':[grant]}
    raw=json.dumps(value,sort_keys=True);local.db.execute('INSERT OR REPLACE INTO manual_state VALUES(1,?)',(raw,))
    frozen=copy.deepcopy(first);frozen.update(schema='colab-review-turn-recovery/v1',failed_call=m.SECOND,next_review=3,max_turns=60,
        failed_workspace=str(work.with_name('run_spec_review-2')),local_rows=rows,global_rows=globals,state_sha256=m.sha(raw.encode()),original_state=value)
    driver=NS(store=local,state=lane,config={'run_id':run},current=lambda:json.loads(local.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]))
    m.activate(driver,frozen,APPROVAL)
    monkeypatch.setattr(pi,'_REVIEW_TERMINAL',lambda sc,row,item:m.retained_review(sc,row,item,frozen))
    monkeypatch.setattr(pi,'_EXTRA_ATTEMPT',lambda sc,r,s,i:m.extra_attempt(sc,r,s,i,frozen,APPROVAL))
    before=[dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid')]
    ident=pi.identity(run,m.STAGE,3)
    admission=batch.reserve_scientific(ident,run,m.STAGE,scope['source_sha'],{})
    assert (admission['run_limit'],admission['batch_limit'])==(8,95)
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls WHERE change_id=?',(run,)).fetchone()[0]==5
    assert [dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid')][:-1]==before
    assert [dict(r) for r in local.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]==rows


def test_installed_hook_limits_local_review_to_three_and_retains_prior_failure(twice,monkeypatch):
    from orchestrator import manual_recovery,stocktake_review_recovery
    x=twice;m.activate(x.driver,x.f,APPROVAL)
    monkeypatch.setattr(pi,'_REVIEW_TERMINAL',None);monkeypatch.setattr(pi,'_EXTRA_ATTEMPT',None)
    monkeypatch.setattr(manual_recovery,'role_limit',lambda *a:2)
    monkeypatch.setattr(stocktake_review_recovery,'completion',lambda *a:None)
    class Driver:pass
    m.install_hook(NS(AnalysisDriver=Driver),x.f,APPROVAL,'ready')
    assert manual_recovery.role_limit(x.store,m.RUN,m.STAGE)==3
    assert manual_recovery.role_limit(x.store,m.RUN,'run_spec_author')==2
    assert manual_recovery.role_limit(x.store,'other',m.STAGE)==2
    assert stocktake_review_recovery.completion(x.store.batch,m.RUN)==[m.FAILED,m.SECOND]
    x.store.db.execute('DELETE FROM events WHERE id=?',(m.TURN_EVENT,))
    with pytest.raises(ValueError,match='GRANT_REQUIRED'):manual_recovery.role_limit(x.store,m.RUN,m.STAGE)
