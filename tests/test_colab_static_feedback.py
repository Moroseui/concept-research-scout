import copy,json,sqlite3,subprocess,sys
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import colab_static_feedback as f
from test_author_visible_module_feedback import visible,BODY

def feedback(tmp_path,body=BODY):
    patch,view,manifest=visible(body)
    folder=tmp_path/f.RUNTIME;(folder/'orchestrator').mkdir(parents=True)
    source=Path(f.__file__).parent
    for name,raw in f.runtime_libraries().items():(folder/'orchestrator'/(name+'.py')).write_bytes(raw)
    (folder/'orchestrator/__init__.py').write_bytes(b'')
    (folder/'check.py').write_text(f.CHECKER)
    binding={'run_id':f.RUN,'analysis_registry_sha256':'a'*64,'original_sha256':patch['original_sha256'],'view_sha256':patch['view_sha256']}
    for name,value in [('binding.json',binding),('manifest.json',manifest)]:(folder/name).write_bytes(f.canonical(value))
    (folder/'view.txt').write_bytes(view)
    (tmp_path/'SPEC.proposed.md').write_text('run_id: '+f.RUN+'\nanalysis_registry_sha256: '+'a'*64+'\n')
    (tmp_path/'notebook.patch.json').write_bytes(f.canonical(patch))
    return patch,folder

def call(tmp_path,folder):
    return subprocess.run([sys.executable,'-I','-B',str(folder/'check.py')],cwd=tmp_path,text=True,capture_output=True)

def test_same_call_cli_correction_with_actual_controller_validator(tmp_path):
    patch,folder=feedback(tmp_path,BODY.replace('main(input_root, output_root, contract)','main(arm, folds)'))
    first=call(tmp_path,folder)
    assert first.returncode==1,first.stderr
    assert 'NOTEBOOK_EXECUTION_ENTRYPOINT:main' in first.stdout
    patch['edits'][0]['replacement']='%%writefile /content/sprint13_pipeline.py\n'+BODY
    (tmp_path/'notebook.patch.json').write_bytes(f.canonical(patch))
    second=call(tmp_path,folder)
    assert second.returncode==0,second.stderr
    result=json.loads(second.stdout)
    assert result['status']=='FORMAT_PASS_NOT_SCIENTIFIC_APPROVAL'
    assert result['files']['notebook.patch.json']==f.sha((tmp_path/'notebook.patch.json').read_bytes())

@pytest.mark.parametrize('damage',['overlap','preimage','hidden','spec','long','json'])
def test_feedback_retains_refusals(tmp_path,damage):
    patch,folder=feedback(tmp_path)
    if damage=='overlap':patch['edits'].append(copy.deepcopy(patch['edits'][0]))
    elif damage=='preimage':patch['edits'][0]['before_sha256']='0'*64
    elif damage=='hidden':patch['edits'][0]['end']+=1
    elif damage=='spec':(tmp_path/'SPEC.proposed.md').write_text('run_id: other')
    elif damage=='long':(tmp_path/'SPEC.proposed.md').write_text('a'*12001)
    (tmp_path/'notebook.patch.json').write_bytes(b'{"x":1,"x":2}' if damage=='json' else f.canonical(patch))
    result=call(tmp_path,folder)
    assert result.returncode==1 and 'CORRECT_AND_RERUN' in result.stdout,result.stderr

def setup_lane(tmp_path):
    lane=tmp_path/'lane';lane.mkdir()
    folder=lane/'notebook-revisions/author-5';folder.mkdir(parents=True)
    (folder/'revised.ipynb').write_text(json.dumps({'cells':[{'cell_type':'code','source':['%%writefile /content/sprint13_pipeline.py\n'+BODY.replace('main(input_root, output_root, contract)','main(arm, folds)')]}]}))
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    db.executescript('CREATE TABLE manual_calls(id TEXT PRIMARY KEY,status TEXT); CREATE TABLE manual_account(id INTEGER PRIMARY KEY,payload TEXT); CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT); CREATE TABLE events(id TEXT PRIMARY KEY,job TEXT,payload TEXT);')
    glob=sqlite3.connect(':memory:');glob.row_factory=sqlite3.Row
    glob.execute('CREATE TABLE autonomy_calls(id TEXT PRIMARY KEY,status TEXT)')
    calls=[{'id':str(i),'status':'COMPLETE'}for i in range(9)]+[{'id':f.CALL,'status':'COMPLETE'}]
    db.executemany('INSERT INTO manual_calls VALUES(:id,:status)',calls)
    glob.execute('INSERT INTO autonomy_calls VALUES(?,?)',(f.CALL,'COMPLETE'))
    value={'phase':'BLOCKED','reason':f.REASON,'pending':{'id':f.CALL,'stage':'run_spec_author','round':5,'workspace':'preserved'},
           'rounds':{'run_spec_author':4,'run_spec_review':4},'interventions':[],'artifacts':[]}
    raw=json.dumps(value)
    db.execute('INSERT INTO manual_state VALUES(1,?)',(raw,));db.execute('INSERT INTO manual_account VALUES(1,?)',('unchanged charges and reservations',))
    db.commit();glob.commit()
    current=lambda:json.loads(db.execute('SELECT payload FROM manual_state').fetchone()[0])
    driver=SimpleNamespace(state=lane,config={'run_id':f.RUN,'batch_ledger':str(tmp_path/'global')},
        store=SimpleNamespace(db=db,batch=SimpleNamespace(db=glob)),current=current)
    b={'files':{},'calls':calls,'records':{'local':calls[-1],'global':calls[-1]},
       'state_row':dict(db.execute('SELECT * FROM manual_state').fetchone()),
       'account_row':dict(db.execute('SELECT * FROM manual_account').fetchone())}
    return driver,b

def test_recovery_preserves_calls_rounds_account_and_is_one_use(tmp_path):
    d,b=setup_lane(tmp_path)
    out=f.resume(d,b,'a'*64)
    assert out['new_calls']==out['new_allowance']==0
    assert [dict(r)for r in d.store.db.execute('SELECT * FROM manual_calls')]==b['calls']
    assert dict(d.store.db.execute('SELECT * FROM manual_account').fetchone())==b['account_row']
    after=d.current()
    assert after['phase']=='run_spec_author' and 'pending' not in after
    assert after['rounds']==json.loads(b['state_row']['payload'])['rounds']
    assert after['interventions'][-1]['reviewer_revise'] is False
    with pytest.raises(ValueError):f.resume(d,b,'a'*64)

@pytest.mark.parametrize('damage',['local','global','live','new','state','account','different_failure','halt'])
def test_recovery_refuses_changed_or_uncertain_state_without_mutating(tmp_path,damage):
    d,b=setup_lane(tmp_path);db=d.store.db;g=d.store.batch.db
    if damage=='local':db.execute("UPDATE manual_calls SET status='UNCERTAIN' WHERE id=?",(f.CALL,))
    elif damage=='global':g.execute("UPDATE autonomy_calls SET status='UNCERTAIN'")
    elif damage=='live':g.execute("INSERT INTO autonomy_calls VALUES('other','RUNNING')")
    elif damage=='new':db.execute("INSERT INTO manual_calls VALUES('other','COMPLETE')")
    elif damage=='state':db.execute("UPDATE manual_state SET payload='{}'")
    elif damage=='account':db.execute("UPDATE manual_account SET payload='changed'")
    elif damage=='different_failure':(d.state/'notebook-revisions/author-5/revised.ipynb').write_text(json.dumps({'cells':[{'cell_type':'code','source':['%%writefile /content/sprint13_pipeline.py\n'+BODY.replace('synthetic_tests()','synthetic_tests(arg)')]}]}))
    elif damage=='halt':(d.state/'HALT').touch()
    db.commit();g.commit()
    before=db.execute('SELECT payload FROM manual_state').fetchone()[0]
    with pytest.raises(ValueError):f.resume(d,b,'a'*64)
    assert db.execute('SELECT payload FROM manual_state').fetchone()[0]==before
    assert not db.execute('SELECT * FROM events').fetchall()

@pytest.mark.parametrize('field,value',[('reason','REVIEW_REJECTED'),('phase','run_spec_review'),('pending',{'id':'other','stage':'run_spec_author','round':5})])
def test_never_reclassifies_genuine_review(field,value):
    original={'phase':'BLOCKED','reason':f.REASON,'pending':{'id':f.CALL,'stage':'run_spec_author','round':5},'interventions':[]}
    original[field]=value
    with pytest.raises(ValueError):f.restored(original,'a'*64)

def test_native_unit_preserves_every_other_directive():
    from tools import colab_static_feedback_runtime as rt
    raw=('User=partho\nGroup=partho\nExecStart=/usr/bin/python3 -s -B '+str(rt.BASE)+'/tools/colab_simple_runtime.py run\nRestart=no\nReadWritePaths=/fixed/work\n')
    parent=SimpleNamespace(metadata=lambda:({},{}),unit_bytes=lambda scope:raw.encode())
    changed=rt.unit_bytes(parent).decode()
    assert changed.replace(str(rt.ROOT/rt.ENTRY),str(rt.BASE/'tools/colab_simple_runtime.py'))==raw

def test_entire_feedback_runtime_passes_unchanged_host_privacy_scan():
    from orchestrator import notebook_revision as nr
    bodies={**f.runtime_libraries(),'check':f.CHECKER.encode()}
    for raw in bodies.values():nr.scan(raw,frozenset())

def test_opaque_predicate_is_exact_existing_source_and_still_refuses(tmp_path):
    import ast,importlib.util,inspect
    from orchestrator import scientific_view_scan as original
    raw=f.runtime_libraries()['scientific_view_scan']
    target=tmp_path/'opaque.py';target.write_bytes(raw)
    spec=importlib.util.spec_from_file_location('exact_opaque',target)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    for name in ('text_variants','reject_opaque'):
        assert ast.dump(ast.parse(inspect.getsource(getattr(module,name))))==ast.dump(ast.parse(inspect.getsource(getattr(original,name))))
    for data in [b'normal visible code',b'A'*256,b'&#65;'*256]:
        def verdict(fn):
            try:fn(data);return 'pass'
            except ValueError as error:return str(error)
        assert verdict(module.reject_opaque)==verdict(original.reject_opaque)
    assert b'SECRET' not in raw
