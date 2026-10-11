"""Author24 binding and atomic, evidence-gated review transition; no provider."""
import json,sqlite3,copy
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import item4_diagnostic_native_runtime as native
from tools import item4_diagnostic_review_runtime as review
from orchestrator import modal_native_synthetic as selected,item4_diagnostic_native as policy


def test_exact_author24_selection_and_unchanged_resources():
    value=selected.selected()
    assert value['author_attempt']==24
    assert value['author_call_id']=='4a171e924b528328d4a4827815113449b39d19143a8824b92f17dce0ecf0b8ca'
    assert value['module_sha256']=='96c881d1c1779ace05f233b3a56f0b5f534b6f3e4a3fe97928da0bf1aa17e986'
    assert selected.RESOURCES==dict(gpu=None,cpu=2,memory_mib=8192,timeout_seconds=900)
    accepted=policy.document(policy.ACCEPTED,policy.ACCEPTED_SHA)
    state=json.loads(accepted['original_state'])
    assert state['phase']=='BLOCKED' and state['reason']=='REPORT_SNAPSHOT_AUTHOR_ACCEPTED_NATIVE_AND_REVIEW_REQUIRED'
    assert state['rounds']==dict(run_spec_author=24,run_spec_review=15)
    assert len(accepted['local_calls'])==39
    assert accepted['accepted_author']['id']==value['author_call_id']
    assert accepted['native_format']['record_sha256']==value['accepted_submission_sha256']


@pytest.fixture
def held(tmp_path,monkeypatch):
    db=sqlite3.connect(':memory:',isolation_level=None)
    other=sqlite3.connect(':memory:',isolation_level=None)
    db.execute('CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT)')
    db.execute('CREATE TABLE manual_calls(id TEXT PRIMARY KEY)')
    db.execute('CREATE TABLE events(id TEXT PRIMARY KEY,run TEXT,payload TEXT)')
    other.execute('CREATE TABLE autonomy_calls(id TEXT PRIMARY KEY,status TEXT)')
    before={'phase':'BLOCKED','reason':'REPORT_SNAPSHOT_AUTHOR_ACCEPTED_NATIVE_AND_REVIEW_REQUIRED',
        'pending':None,'rounds':{'run_spec_author':24,'run_spec_review':15},
        'review':{'preserved':True},'interventions':[{'original':'retained'}],
        'notebook_revision_result':{'accepted':'author24'},'artifacts':[{'unchanged':True}]}
    db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps(before),))
    store=NS(db=db,batch=NS(db=other));driver=NS(store=store,state=tmp_path)
    driver.current=lambda:json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
    mark={'exact_native_receipt':'a'*64,'scientific_acceptance':False}
    calls=[]
    monkeypatch.setattr(native,'accepted',lambda accounts: calls.append(('accepted',accounts)))
    monkeypatch.setattr(review,'marker',lambda accounts:(calls.append(('native-receipt',accounts)) or mark))
    def ready(owner,value,p,approval):
        assert owner is driver and value['diagnostic_native_evidence']==mark
        assert value['phase']=='run_spec_review' and p is scope and approval=='original-author24-approval'
        calls.append(('ready',value))
    scope={'original-scope':True}
    helper=NS(call=lambda p,role:'review16',ready=ready,RUN='original-item4')
    yield NS(driver=driver,helper=helper,scope=scope,approval='original-author24-approval',before=before,mark=mark,calls=calls)
    db.close();other.close()


def test_activation_keeps_all_scientific_authority_and_counters(held):
    h=held;result=review.activate_review(h.driver,h.helper,h.scope,h.approval)
    assert result==dict(status='READY_REVIEW16',model_calls=0,provider_calls=0)
    after=h.driver.current()
    assert {k:v for k,v in after.items() if k not in {'phase','reason','diagnostic_native_evidence'}}=={k:v for k,v in h.before.items() if k not in {'phase','reason'}}
    assert after['diagnostic_native_evidence']==h.mark
    assert h.driver.store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==0
    assert h.driver.store.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    event=h.driver.store.db.execute('SELECT id,payload FROM events').fetchone()
    assert event[0]=='author24-native-review-ready' and json.loads(event[1])==h.mark
    intent=json.loads((h.driver.state/'diagnostic-native24-activation.json').read_bytes())
    assert json.loads(intent['original_state'])==h.before and intent['native']==h.mark
    with pytest.raises(ValueError,match='REVIEW_ALREADY_STARTED'):
        review.activate_review(h.driver,h.helper,h.scope,h.approval)


@pytest.mark.parametrize('damage',['phase','pending','existing-review','running-call','native-failure','existing-intent'])
def test_activation_refuses_without_changing_state_or_counting_call(held,monkeypatch,damage):
    h=held
    if damage in {'phase','pending'}:
        value=h.driver.current();value[damage]='wrong';h.driver.store.db.execute('UPDATE manual_state SET payload=?',(json.dumps(value),))
    elif damage=='existing-review':h.driver.store.db.execute("INSERT INTO manual_calls VALUES('review16')")
    elif damage=='running-call':h.driver.store.batch.db.execute("INSERT INTO autonomy_calls VALUES('unrelated','RUNNING')")
    elif damage=='existing-intent':(h.driver.state/'diagnostic-native24-activation.json').write_text('preserved')
    else:
        def failure(accounts):raise ValueError('actual native receipt failed')
        monkeypatch.setattr(review,'marker',failure)
    raw=h.driver.store.db.execute('SELECT payload FROM manual_state').fetchone()[0]
    counts=(h.driver.store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0],h.driver.store.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0])
    with pytest.raises((ValueError,FileExistsError)):
        review.activate_review(h.driver,h.helper,h.scope,h.approval)
    assert h.driver.store.db.execute('SELECT payload FROM manual_state').fetchone()[0]==raw
    assert h.driver.store.db.execute('SELECT count(*) FROM events').fetchone()[0]==0
    assert counts==(h.driver.store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0],h.driver.store.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0])


def test_ready_refusal_preserves_exclusive_intent_and_original_state(held):
    h=held
    def reject(*args):raise ValueError('existing scientific guard refused')
    h.helper.ready=reject
    with pytest.raises(ValueError,match='existing scientific guard'):
        review.activate_review(h.driver,h.helper,h.scope,h.approval)
    assert h.driver.current()==h.before
    assert (h.driver.state/'diagnostic-native24-activation.json').is_file()
    with pytest.raises(FileExistsError):review.activate_review(h.driver,h.helper,h.scope,h.approval)


def test_reader_binding_preserves_existing_admission_functions(held,monkeypatch):
    from orchestrator import manual_recovery,stocktake_review_recovery,manual_stage
    h=held;before=(manual_recovery.permit,stocktake_review_recovery.admission,manual_stage.reviewer_command)
    restore=review.bind_admission(h.driver,None,None,h.helper,h.scope,h.approval)
    assert (manual_recovery.permit,stocktake_review_recovery.admission)==before[:2]
    restore()
    assert (manual_recovery.permit,stocktake_review_recovery.admission,manual_stage.reviewer_command)==before


@pytest.mark.parametrize('damage',[None,'bytes','source','report','scope','author','reviewer'])
def test_connection_reuses_exact_installed_author24_route(tmp_path,monkeypatch,damage):
    source='wrong' if damage=='source' else '72c48cb69af87b760c4da9f246c1d1cab10735e1'
    report='wrong' if damage=='report' else native.PRIOR_REVIEW
    author=23 if damage=='author' else 24;reviewer=17 if damage=='reviewer' else 16
    code=("from types import SimpleNamespace as NS\n"
          "def authority():return "+repr({'source_sha':source,'report_sha256':report})+"\n"
          "helper=NS(delivery_recovery=lambda p:"+repr(damage!='scope')+",profile=lambda p:"+repr({'author':author,'reviewer':reviewer})+")\n"
          "connection=(object(),object(),object(),object(),helper,{'existing_scope':True},'preserved_approval')\n"
          "owner=NS(connect=lambda:connection)\n"
          "def route():return owner\n")
    path=tmp_path/'prior.py';path.write_text(code)
    monkeypatch.setattr(native,'PRIOR',path);monkeypatch.setattr(native,'PRIOR_SHA',native.sha(path.read_bytes()))
    monkeypatch.setattr(native,'trusted',Path)
    if damage=='bytes':path.write_text(code+'# changed after pin\n')
    if damage is not None:
        with pytest.raises(ValueError):native.verified_prior()
    else:
        owner,connection=native.verified_prior(scientific=True)
        assert owner.connect() is connection and connection[5]=={'existing_scope':True}
        assert connection[6]=='preserved_approval'


@pytest.mark.parametrize('damage',[None,'receipt-bytes','artifact-bytes','reference','frozen-pin','different-content'])
def test_controller_receipt_authenticates_both_exact_representations(damage):
    value={'status':'PASS','tests':[{'passed':True}],'exit_code':0}
    receipt=json.dumps(value,indent=2).encode()
    artifact=json.dumps(value,sort_keys=True,separators=(',',':')).encode()
    assert receipt!=artifact
    selection={'controller_receipt_sha256':native.sha(receipt)}
    frozen={'id':'synthetic_tests','version':24,'sha256':native.sha(artifact)}
    reference=dict(frozen)
    if damage=='receipt-bytes':receipt+=b' '
    elif damage=='artifact-bytes':artifact+=b' '
    elif damage=='reference':reference['version']=25
    elif damage=='frozen-pin':frozen['sha256']='0'*64;reference=dict(frozen)
    elif damage=='different-content':
        artifact=json.dumps({**value,'status':'FAIL'}).encode()
        frozen['sha256']=native.sha(artifact);reference=dict(frozen)
    if damage is None:
        native.controller_binding(receipt,artifact,selection,reference,frozen)
    else:
        with pytest.raises(ValueError,match='CONTROLLER_BINDING'):
            native.controller_binding(receipt,artifact,selection,reference,frozen)
