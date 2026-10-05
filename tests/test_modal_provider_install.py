import json,sqlite3,hashlib
from pathlib import Path
import pytest
from tools import install_modal_provider as install


@pytest.fixture
def prepared(tmp_path,monkeypatch):
    lane=tmp_path/'lane';batch=tmp_path/'batch';root=tmp_path/'source'
    for p in [lane,batch,root]:p.mkdir(mode=0o700)
    code=root/'engine.py';code.write_text('# exact reviewed original')
    review=tmp_path/'review.json';review.write_text('{"verdict":"APPROVE"}')
    monkeypatch.setattr(install,'SPEC_REVIEW_SHA',install.sha(review.read_bytes()))
    config={'run_id':'test-run','root':str(root),'engine_files':{'engine.py':install.sha(code.read_bytes())},'scientific_files':{}}
    (lane/'lane.json').write_text(json.dumps(config));monkeypatch.setattr(install,'CONFIG_SHA',install.sha((lane/'lane.json').read_bytes()))
    state={'phase':'EXECUTE_MODAL','rounds':{'run_spec_author':2,'run_spec_review':2},'spec_review':str(review)}
    db=sqlite3.connect(lane/'jobs.sqlite');db.execute('create table manual_state(payload text)');db.execute('insert into manual_state values(?)',(json.dumps(state),));db.execute('create table manual_calls(id text,stage text,attempt integer,status text)')
    for n in range(4):db.execute('insert into manual_calls values(?,?,?,?)',(str(n),'stage',n,'COMPLETE'))
    db.commit();db.close()
    db=sqlite3.connect(batch/'jobs.sqlite');db.execute('create table autonomy_calls(status text)');db.execute('create table autonomy_compute(run text)');db.commit();db.close()
    return lane,batch,root,review,state


def test_install_guard_reads_without_changing_originals(prepared):
    lane,batch,root,review,state=prepared
    paths=[*lane.iterdir(),*batch.iterdir(),*root.iterdir(),review];before={p:install.sha(p.read_bytes()) for p in paths}
    assert len(install.state_guard(lane,batch)['calls'])==4
    assert {p:install.sha(p.read_bytes()) for p in paths}==before


@pytest.mark.parametrize('damage,code',[('config','PROVIDER_LANE_CHANGED'),('source','ORIGINAL_SOURCE_CHANGED'),('review','SCIENTIFIC_APPROVAL_CHANGED'),('phase','EXACT_PRECOMPUTE_STATE_REQUIRED'),('pending','EXACT_PRECOMPUTE_STATE_REQUIRED'),('call','EXACT_PRECOMPUTE_STATE_REQUIRED'),('global','CALL_IN_FLIGHT'),('compute','COMPUTE_ALREADY_RESERVED_RECONCILE')])
def test_install_refuses_any_used_or_changed_bound_state(prepared,damage,code):
    lane,batch,root,review,state=prepared
    if damage=='config':(lane/'lane.json').write_text('{}')
    if damage=='source':(root/'engine.py').write_text('changed')
    if damage=='review':review.write_text('{"verdict":"REVISE"}')
    if damage in {'phase','pending'}:
        state['phase']='WAIT_OUTPUTS' if damage=='phase' else state['phase']
        if damage=='pending':state['pending']={'id':'another'}
        db=sqlite3.connect(lane/'jobs.sqlite');db.execute('update manual_state set payload=?',(json.dumps(state),));db.commit();db.close()
    if damage=='call':
        db=sqlite3.connect(lane/'jobs.sqlite');db.execute("update manual_calls set status='UNCERTAIN' where id='1'");db.commit();db.close()
    if damage in {'global','compute'}:
        db=sqlite3.connect(batch/'jobs.sqlite');db.execute("insert into autonomy_calls values('RUNNING')" if damage=='global' else "insert into autonomy_compute values('test-run')");db.commit();db.close()
    with pytest.raises(ValueError,match='^'+code+'$'):install.state_guard(lane,batch)


def test_installer_scope_can_be_prepared_by_native_review(tmp_path):
    import subprocess
    from orchestrator import autonomy_review as review
    from tests.test_autonomy_review import native
    from tests.test_consolidated_review_contract import report
    from orchestrator import review_submission as submission
    repo=tmp_path/'repo';repo.mkdir(mode=0o700)
    (repo/'worker.py').write_text('# synthetic component only\n')
    subprocess.run(['git','init','-q',str(repo)],check=True)
    subprocess.run(['git','-C',str(repo),'add','.'],check=True)
    subprocess.run(['git','-C',str(repo),'-c','user.name=Synthetic','-c','user.email=test@invalid','commit','-qm','fixture'],check=True)
    source=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    runtime=tmp_path/'runtime.json';runtime.write_text('{"synthetic":true}\n')
    evidence=tmp_path/'evidence';evidence.mkdir(mode=0o700)
    destination=tmp_path/'packet'
    review.prepare(repo,source,runtime,evidence,['worker.py'],destination,'Inspect the synthetic component.',change_id=install.CHANGE)
    manifest=review.verify_packet(destination)
    assert manifest['change_id']==install.CHANGE
    # Current protocol: a synthetic native tool call must match the real server record.
    work=tmp_path/'submission';work.mkdir(mode=0o700)
    pins=submission.prepare(work,'administrative',submission.administrative_bindings(manifest))
    payload=report(manifest);ack=submission.submit(work,pins['config_sha256'],payload)
    events=native(manifest)
    events[-2:-2]=[
        {'type':'assistant','session_id':'synthetic-session','message':{'model':'synthetic-model','content':[{'type':'tool_use','name':submission.TOOL,'id':'submit','input':payload}]}},
        {'type':'user','session_id':'synthetic-session','message':{'content':[{'type':'tool_result','tool_use_id':'submit','content':[{'type':'text','text':json.dumps(ack)}]}]}}]
    stream='\n'.join(json.dumps(event) for event in events)
    with pytest.raises(ValueError,match='^ACCEPTED_SUBMISSION_REQUIRED$'):
        review.extract_result(stream,manifest,0)
    assert review.extract_result(stream,manifest,0,(work/submission.RECORD).read_bytes())['verdict']=='APPROVE'
