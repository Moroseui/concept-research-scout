import copy,json,sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import colab_author_terminal as m

@pytest.fixture
def fixture():
    work='/synthetic/work';lane='/synthetic/lane';pin='a'*64
    row={'id':m.CALL,'change_id':m.RUN,'kind':'scientific','status':'UNCERTAIN',
        'binding':json.dumps({'stage':'result_interpretation_author','source':'source','input':{'workspace':work,'input_sha256':pin}}),
        'receipt':json.dumps({'outcome':'FAILED_OR_UNCERTAIN','error_type':'ValueError'})}
    local={'id':m.CALL,'status':'UNCERTAIN'}
    state=json.dumps({'phase':'BLOCKED','reason':'MODEL_FAILED_OR_UNCERTAIN_NO_RETRY',
        'pending':{'id':m.CALL,'stage':'result_interpretation_author','round':1,'workspace':work}})
    provenance={'family_effective':'codex','stage':'result_interpretation_author','exit_class':'timeout',
        'exit_detail':'Agent timed out after 900s.','prompt_sha256':pin}
    bodies={'stage_provenance.jsonl':(json.dumps(provenance)+'\n').encode(),'sent-input.json':json.dumps({'input_sha256':pin}).encode(),
        'transport.log':b'Agent timed out after 900s.\n','interpretation.md':b'unaccepted scientific draft'}
    unit={'LoadState':'loaded','ActiveState':'inactive','SubState':'dead','MainPID':'0','ControlGroup':'','ExecMainStatus':'0','InvocationID':''}
    f={'schema':'colab-final-author-terminal/v1','call_id':m.CALL,'run_id':m.RUN,'scientific_successor':False,'scientific_acceptance':False,
        'unit':'research-review-continuation-20261011.service','unit_state':unit,'workspace':work,'lane':lane,
        'global_row':row,'local_row':local,'state_sha256':m.sha(state.encode()),
        'files':{n:{'sha256':m.sha(v),'bytes':len(v)}for n,v in bodies.items()}}
    return f,row,local,state,bodies,unit

@pytest.mark.parametrize('damage',[None,'global','local','active','cgroup','state','draft','provenance','prompt','successor','acceptance','transport'])
def test_exact_terminal_only_and_originals_preserved(fixture,damage):
    f,row,local,state,bodies,unit=copy.deepcopy(fixture);before=copy.deepcopy(f)
    if damage=='global':row={**row,'status':'RUNNING'}
    if damage=='local':local={**local,'status':'COMPLETE'}
    if damage=='active':unit={**unit,'ActiveState':'activating','MainPID':'123'}
    if damage=='cgroup':unit={**unit,'ControlGroup':'/active'}
    if damage=='state':state+=' '
    if damage in ('draft','provenance','prompt','transport'):
        name={'draft':'interpretation.md','provenance':'stage_provenance.jsonl','prompt':'sent-input.json','transport':'transport.log'}[damage]
        bodies[name]+=b'x'
    if damage=='successor':f['scientific_successor']=True
    if damage=='acceptance':f['scientific_acceptance']=True
    kwargs={'read_file':lambda p:bodies[p.name],'observe':lambda _:unit,'read_local':lambda _: (local,state)}
    if damage:
        with pytest.raises(ValueError):m.qualify(row,f,**kwargs)
    else:
        assert m.qualify(row,f,**kwargs)['scientific_successor'] is False
        assert f==before


def test_timeout_semantics_not_just_matching_hashes(fixture):
    f,row,local,state,bodies,unit=copy.deepcopy(fixture)
    p=json.loads(bodies['stage_provenance.jsonl']);p['exit_class']='ok'
    bodies['stage_provenance.jsonl']=json.dumps(p).encode()
    f['files']['stage_provenance.jsonl']={'bytes':len(bodies['stage_provenance.jsonl']),'sha256':m.sha(bodies['stage_provenance.jsonl'])}
    with pytest.raises(ValueError,match='NATIVE_TIMEOUT_BINDING'):
        m.qualify(row,f,read_file=lambda p:bodies[p.name],observe=lambda _:unit,read_local=lambda _: (local,state))


def test_sequence_preserves_unrelated_classifier_and_refusals(monkeypatch):
    seen=[];pi=NS(_REVIEW_TERMINAL=lambda *a:seen.append(a) or 'original')
    monkeypatch.setattr(m,'retained',lambda s,r,i:r.get('id')==m.CALL)
    m.connect_sequence(pi)
    assert pi._REVIEW_TERMINAL({}, {'id':m.CALL},None) is True and not seen
    assert pi._REVIEW_TERMINAL({}, {'id':'other'},None)=='original' and len(seen)==1
    with pytest.raises(ValueError):m.connect_sequence(NS(_REVIEW_TERMINAL=None))


@pytest.mark.parametrize('scope',['review16','review17','author','colab'])
def test_only_timing_review16_gets_terminal_recognition(monkeypatch,scope):
    from orchestrator import stocktake_review_recovery as sr
    from orchestrator.experiment_context import ITEM4_RUN
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    db.execute('create table autonomy_calls(id text,status text)');db.execute('insert into autonomy_calls values(?,?)',(m.CALL,'UNCERTAIN'))
    original=lambda *a:['old'];monkeypatch.setattr(sr,'admission',original)
    calls=[];monkeypatch.setattr(m,'qualify',lambda row:calls.append(row) or {'id':m.CALL})
    m.connect_timing_admission()
    run=m.RUN if scope=='colab' else ITEM4_RUN;stage='run_spec_author' if scope=='author' else 'run_spec_review';round=17 if scope=='review17' else 16
    ident=m.sha((run+':'+stage+':'+str(round)).encode())
    assert sr.admission(NS(db=db),run,stage,ident,'source',{})==(['old',m.CALL] if scope=='review16' else ['old'])
    assert len(calls)==(scope=='review16')
    if scope=='review16':
        db.execute('delete from autonomy_calls')
        with pytest.raises(ValueError,match='ORIGINAL_ROW_REQUIRED'):sr.admission(NS(db=db),run,stage,ident,'source',{})
    db.close()


def test_prior_admission_refusal_propagates(monkeypatch):
    from orchestrator import stocktake_review_recovery as sr
    def refused(*a):raise ValueError('over cap or other original refusal')
    monkeypatch.setattr(sr,'admission',refused);m.connect_timing_admission()
    with pytest.raises(ValueError,match='original refusal'):sr.admission(None,'r','s','i','source',{})
