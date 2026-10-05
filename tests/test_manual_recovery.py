"""Named-recovery tests use only synthetic calls, never credentials/providers."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import pytest
from orchestrator import manual_driver as driver, manual_executor as exe, manual_recovery as rec

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(root,*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()

def make_git(root,branch):
    subprocess.run(['git','init','-q',str(root)],check=True)
    git(root,'config','user.name','Synthetic fixture');git(root,'config','user.email','fixture@local.invalid')
    git(root,'add','.');git(root,'commit','-qm','Synthetic fixture');git(root,'switch','-qc',branch)

@pytest.fixture
def saved(tmp_path,monkeypatch):
    old=tmp_path/'old';new=tmp_path/'new';state=tmp_path/'lane';context=state/'context'
    for root in [old,new]:
        for name,body in {'evidence/decisions.md':'synthetic archive','projects/isles24/context/STATE.md':'synthetic state','projects/isles24/manual/sprint10/data.json':'{}','docs/STEP_D_AUTHORIZATION.md':'synthetic prior grant','orchestrator/fake.py':'# fixture','scout.py':'# fixture'}.items():
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body)
        (root/rec.DECISION_PATH).write_bytes((ROOT/rec.DECISION_PATH).read_bytes())
    make_git(old,'astra/manual-old');make_git(new,'astra/manual-new')
    (context/'evidence').mkdir(parents=True);(context/driver.PROFILE).mkdir(parents=True)
    exe.atomic(context/driver.PROFILE/'obligations.json',{'obligations':[]});exe.atomic(context/driver.PROFILE/'manifest.json',{'obligations':{}})
    old_review=tmp_path/'old-review.md';old_review.write_text('Synthetic old engine approval')
    report=tmp_path/'review.md';report.write_text('Synthetic approval only '+git(new,'rev-parse','HEAD')+'\n## Verdict: APPROVE\n')
    policy={'status':'RATIFIED','operator_approval':'synthetic explicit grant','state_write_permission':'OPERATOR_AUTHORIZED','n':4,'window':'UTC_CALENDAR_DAY','state_ref':'refs/heads/automation/dispatch-state','manual_semantics':'OPERATOR_STEP_D_MAX_EIGHT'}
    store=exe.ManualExecutor(state/'jobs.sqlite');store.initialize_allowance(policy)
    for stage in ['run_spec_author','run_spec_review',rec.STAGE]:
        ident,n,receipt=store.reserve_call(rec.RUN,stage,rec.BASE,'astra/manual-old',policy,{'synthetic':True})
        store.finish_call(ident,receipt,'UNCERTAIN' if stage==rec.STAGE else 'COMPLETE')
    failed=dict(store.db.execute('SELECT * FROM manual_calls WHERE id=?',(rec.FAILED,)).fetchone())
    monkeypatch.setattr(rec,'FAILED_SHA',rec.digest(rec.encoded(failed).encode()))
    monkeypatch.setattr(rec,'__file__',str(new/'orchestrator/manual_recovery.py'))
    config={'run_id':rec.RUN,'source':rec.BASE,'root':str(old),'context':str(context),'branch':'astra/manual-old','policy':policy,'clients':{},'engine_review':{'path':str(old_review),'sha256':sha(old_review)},'authority_sha256':sha(old/'docs/STEP_D_AUTHORIZATION.md'),'profile_files':{'projects/isles24/context/STATE.md':sha(old/'projects/isles24/context/STATE.md')},'scientific_files':{'projects/isles24/manual/sprint10/data.json':sha(old/'projects/isles24/manual/sprint10/data.json')},'engine_files':{'orchestrator/fake.py':sha(old/'orchestrator/fake.py')},'started_utc':'2026-09-25T00:00:00+00:00'}
    exe.atomic(state/'lane.json',config)
    value={'phase':'BLOCKED','reason':'MODEL_FAILED_OR_UNCERTAIN_NO_RETRY','pending':{'id':rec.FAILED,'stage':rec.STAGE,'round':1},'rounds':{'run_spec_author':1,'run_spec_review':1},'artifacts':[],'interventions':[]}
    store.db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps(value),))
    # Existing decision request must remain evidence even after recovery applies.
    (state/'DECISION_REQUEST.md').write_text('Synthetic original request')
    return state,new,report,store,failed


def test_original_no_retry_and_two_role_cap_without_grant(saved):
    state,root,review,store,failed=saved
    with pytest.raises(ValueError,match='UNCERTAIN'):store.reserve_call(rec.RUN,rec.STAGE,rec.BASE,'astra/manual-old',exe.read(state/'lane.json')['policy'],{})
    assert rec.role_limit(store,rec.RUN,rec.STAGE)==2
    assert dict(store.db.execute('SELECT * FROM manual_calls WHERE id=?',(rec.FAILED,)).fetchone())==failed


def test_apply_is_idempotent_and_preserves_failure_charge_authority(saved):
    state,root,review,store,failed=saved;before=exe.Accounts(store).read();old=exe.read(state/'lane.json')
    assert rec.apply(state,root,review)['status']=='APPLIED_NO_MODEL_CALL'
    assert rec.apply(state,root,review)['status']=='ALREADY_APPLIED'
    assert exe.Accounts(store).read()==before
    assert dict(store.db.execute('SELECT * FROM manual_calls WHERE id=?',(rec.FAILED,)).fetchone())==failed
    c=exe.read(state/'lane.json');assert c['source']==old['source'] and c['engine_review']==old['engine_review'] and c['authority_sha256']==old['authority_sha256']
    assert c['execution_recovery']['runtime_source']==git(root,'rev-parse','HEAD')
    assert (state/'DECISION_REQUEST.md').read_text()=='Synthetic original request'
    driver.Driver(state).guard()

@pytest.mark.parametrize('damage',['rejection','missing_pin','different_run','changed_failure','halt'])
def test_unqualified_or_wrong_scope_never_applies(saved,damage):
    state,root,report,store,failed=saved
    if damage=='rejection':report.write_text(report.read_text().replace('APPROVE','REQUEST_CHANGES'))
    elif damage=='missing_pin':report.write_text('## Verdict: APPROVE\n')
    elif damage=='different_run':c=exe.read(state/'lane.json');c['run_id']='different';exe.atomic(state/'lane.json',c)
    elif damage=='changed_failure':store.db.execute("UPDATE manual_calls SET receipt='{}' WHERE id=?",(rec.FAILED,))
    else:(state/'HALT').touch()
    before=exe.Accounts(store).read()
    with pytest.raises(ValueError):rec.apply(state,root,report)
    assert not store.db.execute('SELECT * FROM manual_recoveries').fetchall()
    assert driver.Driver(state).current()['phase']=='BLOCKED' and exe.Accounts(store).read()==before


def test_one_recovery_plus_revision_other_roles_two_total_eight(saved):
    state,root,report,store,failed=saved;rec.apply(state,root,report);c=exe.read(state/'lane.json')
    assert rec.role_limit(store,'other-run',rec.STAGE)==2
    for n in [2,3]:
        ident,attempt,r=store.reserve_call(rec.RUN,rec.STAGE,rec.BASE,c['branch'],c['policy'],{})
        assert attempt==n and r['linked_recovery_of']==rec.FAILED and r['recovery_runtime_source']==git(root,'rev-parse','HEAD')
        store.finish_call(ident,r,'COMPLETE')
    with pytest.raises(ValueError,match='CALL_LIMIT'):store.reserve_call(rec.RUN,rec.STAGE,rec.BASE,c['branch'],c['policy'],{})
    for stage in ['result_interpretation_review','result_interpretation_review','run_spec_author']:
        ident,n,r=store.reserve_call(rec.RUN,stage,rec.BASE,c['branch'],c['policy'],{});store.finish_call(ident,r,'COMPLETE')
    assert store.db.execute('select count(*) from manual_calls').fetchone()[0]==8
    with pytest.raises(ValueError,match='CALL_LIMIT'):store.reserve_call(rec.RUN,'run_spec_review',rec.BASE,c['branch'],c['policy'],{})
    assert dict(store.db.execute('SELECT * FROM manual_calls WHERE id=?',(rec.FAILED,)).fetchone())==failed


def test_new_uncertain_attempt_never_gets_second_recovery(saved):
    state,root,report,store,failed=saved;rec.apply(state,root,report);c=exe.read(state/'lane.json')
    ident,n,r=store.reserve_call(rec.RUN,rec.STAGE,rec.BASE,c['branch'],c['policy'],{});store.finish_call(ident,r,'UNCERTAIN')
    rec.apply(state,root,report)
    with pytest.raises(ValueError,match='UNCERTAIN'):store.reserve_call(rec.RUN,rec.STAGE,rec.BASE,c['branch'],c['policy'],{})
    with pytest.raises(ValueError,match='UNCERTAIN'):store.reserve_call(rec.RUN,'result_interpretation_review',rec.BASE,c['branch'],c['policy'],{})


def test_partial_config_application_resumes_same_plan_without_call(saved,monkeypatch):
    state,root,report,store,failed=saved;original=exe.atomic
    def interrupted(path,value,**kw):
        original(path,value,**kw)
        if Path(path)==state/'lane.json':raise OSError('synthetic interruption after config')
    monkeypatch.setattr(exe,'atomic',interrupted)
    with pytest.raises(OSError):rec.apply(state,root,report)
    assert driver.Driver(state).current()['phase']=='BLOCKED' and rec.permit(store,rec.RUN) is None
    monkeypatch.setattr(exe,'atomic',original)
    assert rec.apply(state,root,report)['status']=='APPLIED_NO_MODEL_CALL'
    assert len(store.db.execute('select * from manual_calls').fetchall())==3


def test_author_workspace_two_then_review_revision_three(saved,monkeypatch):
    state,root,report,store,failed=saved;rec.apply(state,root,report)
    monkeypatch.setattr(driver.manual_context,'prepare',lambda *a,**kw:('synthetic input',{'workspace_files':[]}))
    monkeypatch.setattr('orchestrator.context_budget.obligations',lambda *args:[])
    paths=[]
    def fake(work,stage,*args):
        paths.append(work.name)
        if stage==rec.STAGE:
            (work/'interpretation.md').write_text('# Summary\nSynthetic result.\n# Details\nSynthetic evidence.')
            exe.atomic(work/'investigator_next_decision.json',{'status':'PROPOSAL_ONLY','proposed_action_type':'stop','action':'Stop.','rationale':'Synthetic fixture only','charter_basis':'','blocker_ids':[]})
        else:
            first=work.name.endswith('-1');exe.atomic(work/'review.json',{'verdict':'REVISE' if first else 'APPROVE','rationale':'BLOCKER[metric/statistic] Synthetic revision' if first else 'Synthetic resolved'})
        return {'synthetic':True}
    d=driver.Driver(state,runner=fake)
    assert d.advance()['phase']=='result_interpretation_review'
    assert d.advance()['phase']==rec.STAGE
    assert d.advance()['phase']=='result_interpretation_review'
    assert d.advance()['phase']=='UPDATE_STATE'
    assert paths==['result_interpretation_author-2','result_interpretation_review-1','result_interpretation_author-3','result_interpretation_review-2']
    assert d.status()['calls_used']==7
    assert dict(store.db.execute('SELECT * FROM manual_calls WHERE id=?',(rec.FAILED,)).fetchone())==failed


def test_modified_review_after_application_fails_before_admission(saved):
    state,root,report,store,failed=saved;rec.apply(state,root,report);report.write_text(report.read_text()+'changed')
    status=driver.Driver(state).advance()
    assert status['phase']=='BLOCKED' and 'RECOVERY_REVIEW_CHANGED' in status['reason'] and status['calls_used']==3
