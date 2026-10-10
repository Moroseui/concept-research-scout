"""Actual Driver._model_step and candidate ResponseDriver entry.
Input content/backend are test boundaries; no live ledger, process or science.
"""
import ast,copy,json,sqlite3,subprocess
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator.manual_driver import Driver
from orchestrator import manual_recovery
from tools import item4_smoke_response_runtime as route

ROOT=Path(__file__).parents[1]
class AtBackend(BaseException):pass

def candidate_class(raw,namespace):
    tree=ast.parse(raw)
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    cls=next(n for n in main.body if isinstance(n,ast.ClassDef) and n.name=='ResponseDriver')
    exec(compile(ast.Module(body=[cls],type_ignores=[]),'actual-response-driver-class','exec'),namespace)
    return namespace['ResponseDriver']

@pytest.fixture
def entry(tmp_path,monkeypatch):
    db=sqlite3.connect(':memory:')
    db.execute('CREATE TABLE manual_calls(id TEXT,stage TEXT,attempt INTEGER,status TEXT)')
    db.executemany('INSERT INTO manual_calls VALUES(?,?,?,?)',
        [(str(n),'run_spec_author',n,'UNCERTAIN' if n==22 else 'COMPLETE') for n in range(1,23)])
    old=list(db.execute('SELECT * FROM manual_calls'))
    calls=[];work=tmp_path/'run_spec_author-23';p={'test_only':True}
    class Base(Driver):
        def __init__(self):
            self.state=tmp_path;self.config={'run_id':'test-run','source':'a'*40,'branch':'test','policy':{}}
            self.context=tmp_path;self.store=NS(db=db,reserve_call=self.reserve,finish_call=self.finish)
            self.runner=self.backend
        def model_workspace(self,value,stage,number):
            return tmp_path/(stage+'-'+str(number))
        def prepare_input(self,value,stage,selected):
            calls.append(('content',stage,selected.name))
            assert stage=='run_spec_author' and selected==work
            return 'test input',{'workspace_files':[]}
        def reserve(self,run,stage,source,branch,policy,receipt):
            calls.append(('reserve',stage,receipt['workspace']))
            attempt=db.execute('SELECT count(*) FROM manual_calls WHERE stage=?',(stage,)).fetchone()[0]+1
            ident='test-'+str(attempt)
            db.execute('INSERT INTO manual_calls VALUES(?,?,?,?)',(ident,stage,attempt,'RUNNING'))
            return ident,attempt,receipt
        def finish(self,ident,receipt,status):
            db.execute('UPDATE manual_calls SET status=? WHERE id=?',(status,ident))
        def save(self,value):
            self.saved=copy.deepcopy(value)
        def guard(self):calls.append(('guard',))
        def backend(self,selected,stage,clients,digest):
            assert selected==work and self.saved['pending']['round']==23
            assert self.saved['pending']['id']=='test-23'
            assert db.execute("SELECT status FROM manual_calls WHERE id='test-23'").fetchone()[0]=='RUNNING'
            calls.append(('backend',stage,selected.name))
            raise AtBackend()
    helper=NS(deliver=lambda *a:None,verify_delivered=lambda *a:None,guidance=lambda *a:'')
    namespace=dict(vars(route),ExperimentDriver=Base,helper=helper,p=p,approval='b'*64,
        author_round=lambda:23,supplemental=lambda *a:None,deliver_failure=lambda *a:None,
        verify_failure_delivery=lambda *a:None,prepare_author_feedback=lambda *a:None)
    cls=candidate_class((ROOT/'tools/item4_smoke_response_runtime.py').read_bytes(),namespace)
    instance=cls();instance.config['clients']={}
    value={'phase':'run_spec_author','rounds':{'run_spec_author':21,'run_spec_review':15}}
    monkeypatch.setattr(manual_recovery,'role_limit',lambda *a:23)
    yield instance,value,db,old,calls,namespace
    db.close()

def test_real_driver_path_selects23_before_input_admits_and_reaches_backend(entry):
    driver,value,db,old,calls,_=entry
    with pytest.raises(AtBackend):driver._model_step(value)
    assert [x[0] for x in calls]==['content','guard','reserve','backend']
    assert list(db.execute('SELECT * FROM manual_calls WHERE attempt<=22'))==old
    assert value['rounds']=={'run_spec_author':21,'run_spec_review':15}
    assert value['pending']['round']==23
    assert (driver.state/'run_spec_author-23/prompt.md').read_text()=='test input'
    assert not (driver.state/'run_spec_author-22').exists()

def test_original_real_driver_reproduces_pre_admission_failure(entry):
    driver,value,db,old,calls,ns=entry
    raw=subprocess.check_output(['git','show','478a47243454b1f9ba6e6ecb82ba5d0132cef001:tools/item4_smoke_response_runtime.py'],cwd=ROOT)
    cls=candidate_class(raw,ns);prior=cls();prior.config['clients']={}
    with pytest.raises(ValueError,match='INPUT_SCOPE'):prior._model_step(value)
    assert calls==[] and list(db.execute('SELECT * FROM manual_calls'))==old
    assert not list(driver.state.iterdir())

@pytest.mark.parametrize('fault',['missing-failed22','extra-attempt23','review-stage','pending'])
def test_wrong_attempt_history_or_stage_refused_before_writes(entry,fault):
    driver,value,db,old,calls,_=entry
    if fault=='missing-failed22':db.execute('DELETE FROM manual_calls WHERE attempt=22')
    elif fault=='extra-attempt23':db.execute("INSERT INTO manual_calls VALUES('extra','run_spec_author',23,'RUNNING')")
    elif fault=='review-stage':value['phase']='run_spec_review'
    else:value['pending']={'id':'existing'}
    before=list(db.execute('SELECT * FROM manual_calls'))
    with pytest.raises(ValueError,match='ATTEMPT_'):driver._model_step(value)
    assert calls==[] and list(db.execute('SELECT * FROM manual_calls'))==before
    assert not list(driver.state.iterdir())

def test_repair_has_no_activation_or_cost_entrypoint():
    t=ast.parse((ROOT/'tools/item4_smoke_response_runtime.py').read_bytes())
    main=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    allowed=next(n for n in ast.walk(main) if isinstance(n,ast.Set) and {x.value for x in n.elts if isinstance(x,ast.Constant)}=={'verify','run'})
    assert len(allowed.elts)==2

@pytest.mark.parametrize('fault',['none','verdict','source','report','change','scope'])
def test_only_genuine_unchanged_original_grant_is_carried(tmp_path,monkeypatch,fault):
    from orchestrator import autonomy_review
    result={'verdict':'APPROVE','change_id':'item4-sender-continuation-20261010',
        'source_sha':'478a47243454b1f9ba6e6ecb82ba5d0132cef001',
        'report_sha256':'aff49bc6cc3ec2b402c7a89549cd643be8c2ed038260c4bff49f0522a829af5f'}
    name='docs/ITEM4_REPORT_SNAPSHOT_AUTHOR_PRIVATE.json'
    pin=route.sha((ROOT/name).read_bytes())
    manifest=tmp_path/'packet-manifest.json'
    manifest.write_text(json.dumps({'source_files':{name:'0'*64 if fault=='scope' else pin}}))
    if fault!='none' and fault!='scope':
        key={'verdict':'verdict','source':'source_sha','report':'report_sha256','change':'change_id'}[fault]
        result[key]='wrong'
    monkeypatch.setattr(autonomy_review,'verify_result',lambda path:result)
    monkeypatch.setattr(route,'ROOT',ROOT)
    monkeypatch.setattr(route,'trusted',lambda path:manifest if Path(path).name=='packet-manifest.json' else Path(path))
    if fault=='none':assert route.continuation_grant()==result
    else:
        with pytest.raises(ValueError,match='ORIGINAL_CONTINUATION'):route.continuation_grant()
