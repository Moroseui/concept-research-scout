"""One unspent call, new immutable context, old preparation and charges intact."""
import json
from pathlib import Path
from types import MethodType
import pytest
from orchestrator import item4_batch_recovery as r,author_format_submission as af
from orchestrator import item4_review4_continuation as x
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import Accounts
from tools import item4_scientific_revision_component as component
from test_item4_batch_continuation import extended,fifth,mechanical,fourth,third,setup,second,continuation,base_setup
from test_item4_review9_response import probe

@pytest.fixture
def prepared(extended):
    f,saved=extended;store,batch,config,d,response,*_=f
    checkpoint=saved['extension']
    store.db.execute('DELETE FROM events WHERE id=?',(r.EVENT,))
    work=r.original_workspace(d);work.mkdir(parents=True)
    body=b'Original prepared input before new operator staging decision'
    (work/'prompt.md').write_bytes(body)
    bindings={'call_id':r.CALL,'run_id':r.RUN,'stage':'run_spec_author','round':14,
        'source_sha':'a'*40,'runtime_sha256':'b'*64,'input_sha256':x.sha(body)}
    revision={key:'d'*64 for key in ('review_call_id','review_sha256','operator_scope_sha256','original_sha256','view_sha256')}
    pins=af.prepare_revision(work,bindings,revision);pins_path=d.state.parent/'original-runtime-pins.json'
    pins_path.write_bytes(x.canonical(pins))
    state=x.state(store);state.update(phase='BLOCKED',reason='ValueError: AUTONOMY_BATCH_CALL_LIMIT')
    raw=json.dumps(state,sort_keys=True);store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(raw,))
    checkpoint.update(configuration_sha256=x.sha((d.state/'lane.json').read_bytes()),
        state_sha256=x.sha(raw.encode()),runtime_pins_sha256=x.sha(pins_path.read_bytes()),
        local_calls={row['id']:x.sha(x.canonical(dict(row))) for row in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')},
        original_account_sha256=x.sha(x.canonical([dict(row) for row in store.db.execute('SELECT * FROM manual_account ORDER BY id')])),
        workspace_files={str(p.relative_to(work)):{'sha256':x.sha(p.read_bytes()),'bytes':p.stat().st_size} for p in work.rglob('*') if p.is_file()})
    dest=d.state.parent/'batch-recovery'
    return f,checkpoint,pins_path,dest


def apply(v):
    f,checkpoint,pins,dest=v;store,batch,config,d,response,*_=f
    return r.restore(d,checkpoint,'e'*64,response,'9'*64,dest,pins)


def test_actual_model_step_new_workspace_same_call_old_files_and_all60_preserved(prepared):
    f,checkpoint,pins,dest=prepared;store,batch,config,d,response,*_=f
    old=r.original_workspace(d);originals={str(p.relative_to(old)):p.read_bytes() for p in old.rglob('*') if p.is_file()}
    original_pins=pins.read_bytes();before=Accounts(store).read()
    assert apply(prepared)['model_calls']==0 and Accounts(store).read()==before
    p,calls=probe(f)
    ordinary=Driver.model_workspace.__get__(p,Driver)
    p.model_workspace=MethodType(lambda self,value,stage,n:r.workspace(self,value,stage,n,ordinary,checkpoint,'e'*64,pins),p)
    value=p._model_step(x.state(store))
    assert value['pending']['id']==r.CALL and value['pending']['round']==14
    assert Path(value['pending']['workspace'])==r.replacement_workspace(d)
    assert calls==[('run_spec_author-14','run_spec_author')]
    assert {str(q.relative_to(old)):q.read_bytes() for q in old.rglob('*') if q.is_file()}==originals
    assert pins.read_bytes()==original_pins
    assert store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==23
    assert batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]==61
    with pytest.raises(ValueError):apply(prepared)


@pytest.mark.parametrize('fault',['state','reason','round','pending','local-call','global-call','account','config','file','extra','symlink','pins','output','new-workspace','new-parent-alias','intent','old-grant','new-grant'])
def test_recovery_faults_refuse_without_reset_or_call(prepared,fault):
    f,checkpoint,pins,dest=prepared;store,batch,config,d,response,*_=f
    if fault in {'state','reason','round','pending'}:
        value=x.state(store)
        if fault=='state':value['phase']='run_spec_author'
        elif fault=='reason':value['reason']='different'
        elif fault=='round':value['rounds']['run_spec_author']=14
        else:value['pending']={'id':r.CALL}
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
    elif fault=='local-call':store.db.execute("UPDATE manual_calls SET receipt='{}' WHERE id=?",(next(iter(checkpoint['local_calls'])),))
    elif fault=='global-call':batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',(r.CALL,'scientific',r.RUN,23,'2000-01-01','UNCERTAIN','{}','{}'))
    elif fault=='account':store.db.execute('UPDATE manual_account SET version=version+1')
    elif fault=='config':(d.state/'lane.json').write_text('{}')
    elif fault=='file':(r.original_workspace(d)/'prompt.md').write_text('changed')
    elif fault=='extra':(r.original_workspace(d)/'extra.txt').write_text('extra')
    elif fault=='symlink':(r.original_workspace(d)/'alias').symlink_to(pins)
    elif fault=='pins':pins.write_text('{}')
    elif fault=='output':(r.original_workspace(d)/af.RECORD).write_text('{}')
    elif fault=='new-workspace':r.replacement_workspace(d).mkdir(parents=True)
    elif fault=='new-parent-alias':
        other=d.state.parent/'other';other.mkdir();r.replacement_workspace(d).parent.symlink_to(other,target_is_directory=True)
    elif fault=='intent':dest.mkdir()
    elif fault=='old-grant':store.db.execute('DELETE FROM events WHERE id=?',(x.reason(response),))
    elif fault=='new-grant':store.db.execute('INSERT INTO events VALUES(?,?,?)',(r.EVENT,r.RUN,'{}'))
    before=(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0],Accounts(store).read())
    with pytest.raises((ValueError,KeyError,FileNotFoundError)):apply(prepared)
    assert before==(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0],Accounts(store).read())
    assert store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==22


def test_restored_call_cannot_reprepare_existing_new_workspace(prepared):
    f,checkpoint,pins,dest=prepared;store,batch,config,d,*_=f
    apply(prepared);target=r.replacement_workspace(d);target.mkdir(parents=True)
    with pytest.raises(ValueError,match='NEW_WORKSPACE_EXISTS'):
        r.workspace(d,x.state(store),'run_spec_author',14,lambda *args:None,checkpoint,'e'*64,pins)
    assert store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==22


def test_sender_distinguishes_exact_recovered_pins_and_keeps_old_path(tmp_path,monkeypatch):
    monkeypatch.setattr(component,'STATE',tmp_path);monkeypatch.setattr(component,'DEST',tmp_path/'pins')
    old=tmp_path/'item4/lane-scientific-workspaces/run_spec_author-14'
    new=old.parent/r.DIRECTORY/old.name
    assert component.work_number(old)==component.work_number(new)==14
    assert component.runtime_pins_path(old)==tmp_path/'pins/runtime-pins-14.json'
    assert component.runtime_pins_path(new)==tmp_path/'pins/runtime-pins-14-batch-staging.json'
    for path in (new.with_name('run_spec_author-15'),new.parent/'extra'/new.name):
        with pytest.raises(ValueError):component.runtime_pins_path(path)


def test_held_response_approval_is_independent_of_new_install(tmp_path,monkeypatch):
    from orchestrator import autonomy_review,manual_host_guard
    monkeypatch.setattr(component,'RECORD',tmp_path)
    monkeypatch.setattr(manual_host_guard,'trusted',lambda p:p)
    record={'verdict':'APPROVE','change_id':'item4-review9-staged-continuation-20261009',
        'source_sha':component.RESPONSE_SOURCE,'report_sha256':component.RESPONSE_REVIEW}
    paths=[]
    monkeypatch.setattr(autonomy_review,'verify_result',lambda path:(paths.append(path) or record))
    assert component.held_response_approval()==component.RESPONSE_REVIEW
    assert paths==[tmp_path/'history'/component.RESPONSE_SOURCE/'original-review-directory']
    record['report_sha256']='e'*64
    with pytest.raises(ValueError,match='HELD_RESPONSE_APPROVAL'):component.held_response_approval()
