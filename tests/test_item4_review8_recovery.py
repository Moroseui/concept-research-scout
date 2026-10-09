"""Real reservation/CAS engines with synthetic evidence; no models or providers."""
import json
from pathlib import Path
import pytest
from orchestrator import item4_review8_recovery as repair,item4_scoped_calls as scoped
from orchestrator import item4_review4_continuation as x,manual_recovery,autonomy_limits as limits
from orchestrator import author_revision_accounting as a,review_submission as rs,dispatch_limiter
from orchestrator.manual_executor import ManualExecutor,Accounts
from orchestrator.autonomy_accounting import BatchAccounts
from test_item4_review7_continuation import fourth,accept_author
from test_item4_review6_continuation import third
from test_item4_review5_continuation import setup,second
from test_item4_review4_continuation import continuation,activate
from test_author_revision_accounting import review,reserve,setup as base_setup
from test_manual_lane import policy

@pytest.fixture
def mechanical(request,monkeypatch):
    saved=[(obj,key,getattr(obj,key)) for obj,key in [(limits,k) for k in ('local_limit','global_limit','allowance','cap_authority')]+[(ManualExecutor,'reserve_call'),(BatchAccounts,'reserve_scientific')]]
    fixture=request.getfixturevalue('fourth');store,batch,c,d,grant,*_=fixture
    accept_author(fixture)
    ident,n,receipt=store.reserve_call(c['run_id'],'run_spec_review',c['source'],'astra/manual-test',policy(),{})
    assert ident==repair.FAILED and n==8
    receipt.update(outcome='FAILED',reason='ACCEPTED_SUBMISSION_REQUIRED',error_type='TerminalSubmissionFailure')
    store.finish_call(ident,receipt,'FAILED')
    work=d.state.parent/'lane-scientific-workspaces/run_spec_review-8';work.mkdir(parents=True,mode=0o700)
    (work/rs.CONFIG).write_text('{}')
    (work/'prompt.md').write_text('preserved failed review8 prompt')
    (work/'console.log').write_text(json.dumps({'type':'result','subtype':'error_max_turns','num_turns':30,'session_id':'synthetic','is_error':False})+'\n')
    value=x.state(store);value.setdefault('artifacts',[]);value.update(phase='BLOCKED',reason=repair.REASON,pending={'id':ident,'stage':repair.STAGE,'round':8,'workspace':str(work)},notebook_revision_result={'synthetic':'unchanged'},spec='synthetic-author13')
    raw=json.dumps(value);store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(raw,))
    local=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')];glob=[dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid')]
    frozen={'schema':'item4-review8-mechanical-recovery/v1','run_id':x.RUN,'failed_call':ident,'failed_workspace':str(work),
        'local_calls':{r['id']:x.sha(x.canonical(r)) for r in local},'global_calls':{r['id']:x.sha(x.canonical(r)) for r in glob},
        'state_sha256':x.sha(raw.encode()),'configuration_sha256':x.sha((d.state/'lane.json').read_bytes()),
        'files':{p.name:{'sha256':x.sha(p.read_bytes()),'bytes':p.stat().st_size} for p in work.iterdir()},
        'native_subtype':'error_max_turns','native_turns':30,'next_review':9,'next_max_turns':60,'run_limit':24,
        'scientific_state_sha256':x.sha(x.canonical({k:value[k] for k in ('artifacts','notebook_revision_result','spec','review')}))}
    for obj,key,original in saved:monkeypatch.setattr(obj,key,original)
    monkeypatch.setattr(scoped,'_validate',None)
    scoped.connect(grant,'b'*64,mechanical=frozen,mechanical_approval='a'*64)
    old=manual_recovery.role_limit
    monkeypatch.setattr(manual_recovery,'role_limit',lambda st,run,stage:repair.next_review(st,frozen,'a'*64) if run==x.RUN and stage==repair.STAGE and x.state(st)['phase']==stage else old(st,run,stage))
    return store,batch,c,d,frozen,local,glob

def apply(v):
    store,batch,c,d,f,*_=v
    return repair.activate(d,f,'a'*64,d.state/'mechanical-recovery')

def replacement(v):
    store,batch,c,d,f,*_=v
    return store.reserve_call(c['run_id'],repair.STAGE,c['source'],'astra/manual-test',policy(),{'linked_recovery_of':repair.FAILED})

def test_preserved_failure_one_replacement_and_exact_twenty_four(mechanical,monkeypatch):
    from orchestrator import experiment_collection
    store,batch,c,d,f,local,glob=mechanical
    assert apply(mechanical)['preserved_calls']==21
    assert Accounts(store).read()[1]['count']==21
    ident,n,receipt=replacement(mechanical);assert ident==repair.REPLACEMENT and n==9
    assert receipt['batch_accounting']['run_limit']==24 and Accounts(store).read()[1]['count']==22
    value=x.state(store);value.update(phase='MODEL_RUNNING',pending={'id':ident,'round':9,'stage':repair.STAGE})
    store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
    original=lambda work,stage:['client','--max-turns','30','--permission-mode','default']
    argv=repair.command(original,Path(f['failed_workspace']).with_name('run_spec_review-9'),repair.STAGE,store,f,'a'*64)
    assert argv==['client','--max-turns','60','--permission-mode','default']
    assert repair.command(original,'unrelated','result_interpretation_review',store,f,'a'*64)==original(None,None)
    receipt['output_sha256']={'review.json':'f'*64};store.finish_call(ident,receipt,'COMPLETE')
    checks=[];monkeypatch.setattr(experiment_collection,'verified',lambda driver,value:checks.append(value['phase']))
    rounds={'run_spec_author':13,'run_spec_review':9}
    for stage in ('result_interpretation_author','result_interpretation_review'):
        value=x.state(store);value.pop('pending',None);value.update(phase=stage,reason=None,rounds=dict(rounds))
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
        ident,n,receipt=store.reserve_call(c['run_id'],stage,c['source'],'astra/manual-test',policy(),{})
        assert n==1;receipt['output_sha256']={'interpretation.md':'f'*64};store.finish_call(ident,receipt,'COMPLETE');rounds[stage]=1
        if stage.endswith('author'):a.accepted(d,{'id':ident,'stage':stage,'round':1})
    assert len(checks)==4
    account=Accounts(store).read()[1];assert account['count']==24 and account['halted'] and account['resets']==[]
    for stage in ('run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review'):
        with pytest.raises(ValueError):store.reserve_call(c['run_id'],stage,c['source'],'astra/manual-test',policy(),{})
    assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid LIMIT 21')]==local
    assert [dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid LIMIT 21')]==glob

@pytest.mark.parametrize('fault',['local','global','file','submission','verdict','state','running','repeat','scientific','grant','command-unreserved','command-wrong-work'])
def test_recovery_refuses_changed_or_unqualified_state(mechanical,fault):
    store,batch,c,d,f,*_=mechanical
    if fault=='local':store.db.execute("UPDATE manual_calls SET receipt='{}' WHERE id=?",(repair.FAILED,))
    elif fault=='global':batch.db.execute("UPDATE autonomy_calls SET receipt='{}' WHERE id=?",(repair.FAILED,))
    elif fault=='file':(Path(f['failed_workspace'])/'console.log').write_text('changed')
    elif fault in ('submission','verdict'):(Path(f['failed_workspace'])/(rs.RECORD if fault=='submission' else 'review.json')).write_text('{}')
    elif fault=='state':store.db.execute("UPDATE manual_state SET payload='{}' WHERE id=1")
    elif fault=='running':batch.db.execute("UPDATE autonomy_calls SET status='RUNNING' WHERE id=?",(repair.FAILED,))
    else:
        apply(mechanical)
        if fault=='repeat':
            with pytest.raises(ValueError):apply(mechanical)
            return
        if fault=='scientific':
            value=x.state(store);value['spec']='changed';store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
        elif fault=='grant':store.db.execute('DELETE FROM events WHERE id=?',(repair.EVENT,))
        elif fault.startswith('command'):
            if fault=='command-wrong-work':replacement(mechanical)
            with pytest.raises(ValueError):repair.command(lambda w,s:['client','--max-turns','30'],'wrong-work',repair.STAGE,store,f,'a'*64)
            return
        with pytest.raises(ValueError):replacement(mechanical)
        assert Accounts(store).read()[1]['count']==21
        return
    with pytest.raises((ValueError,KeyError)):apply(mechanical)
    assert Accounts(store).read()[1]['count']==21

@pytest.mark.parametrize('kind',['day','batch','account-halt','batch-halt','direct-global','forged','early-interpretation'])
def test_other_refusals_survive(mechanical,kind):
    from datetime import datetime,timezone
    from test_scoped_revisions_limits import seed
    store,batch,c,d,f,*_=mechanical;apply(mechanical)
    if kind=='day':seed(batch,29,kind='implementation_review',day=datetime.now(timezone.utc).date().isoformat())
    elif kind=='batch':seed(batch,39)
    elif kind=='batch-halt':(batch.folder/'HALT').write_text('synthetic stop')
    elif kind=='account-halt':
        version,value=Accounts(store).read();value['halted']=True;assert Accounts(store).cas(version,value)
    elif kind=='direct-global':
        with pytest.raises(ValueError):batch.reserve_scientific(repair.REPLACEMENT,c['run_id'],repair.STAGE,c['source'],{})
        return
    elif kind=='forged':
        with pytest.raises(ValueError):dispatch_limiter.admit_manual(Accounts(store),policy(),{'run_id':'f'*64,'attempt':'1','source':c['source'],'branch':'astra/manual-test'},allowance={'run_limit':24})
        return
    elif kind=='early-interpretation':
        with pytest.raises(ValueError):store.reserve_call(c['run_id'],'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
        return
    with pytest.raises(ValueError):replacement(mechanical)
    assert Accounts(store).read()[1]['count']==21
