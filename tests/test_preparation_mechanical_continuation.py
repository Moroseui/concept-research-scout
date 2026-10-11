import copy,json,os,sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import preparation_mechanical_continuation as m

def create_table(db,name,row):
    order={'manual_state':['id','payload'],'manual_account':['id','version','payload'],'manual_calls':['id','stage','attempt','status','receipt'],'autonomy_calls':['id','kind','change_id','round','day','status','binding','receipt']}[name]
    keys=[k for k in order if k in row];assert set(keys)==set(row)
    db.execute('CREATE TABLE '+name+'('+','.join('"'+k+'"'+(' PRIMARY KEY' if k=='id' else '') for k in keys)+')')
    db.execute('INSERT INTO '+name+' VALUES('+','.join('?' for _ in keys)+')',[row[k] for k in keys])
def fixture(root,monkeypatch,capture=None):
    root=Path(root);p=lambda path:m.map_path(root,path);lane=p(m.LANE);work=p(m.binding()['workspace']);folder=lane/'notebook-revisions/author-1'
    for d in [lane,work,folder,p(m.LEDGER).parent]:d.mkdir(parents=True,exist_ok=True,mode=0o700)
    if capture is not None:
        v=json.loads((capture/'CAPTURE_READONLY.stdout').read_bytes());cfg=v['config_raw'].encode();b=m.binding()
        for n in [*b['output_sha256'],'console.log']:(work/n).write_bytes((capture/'originals/files'/n).read_bytes())
        for n in b['derived_sha256']:(folder/n).write_bytes((capture/'originals/derived_files'/n).read_bytes())
    else:
        v={'state_row':{'id':1,'payload':json.dumps({'phase':'BLOCKED','reason':m.binding()['reason'],'rounds':{},'pending':{'id':m.ID,'stage':'run_spec_author','round':1,'workspace':m.binding()['workspace']},'interventions':[]})},'account_row':{'id':1,'version':1,'payload':'{"count":1}'}}
        cfg=json.dumps({'run_id':m.RUN}).encode()
        for n in ['SPEC.proposed.md','notebook.patch.json','console.log']:(work/n).write_bytes(b'synthetic '+n.encode())
        code='def main(input_root, output_root, contract): pass\ndef synthetic_tests(): pass\ndef preprocess(input_root, output_root, contract): pass\ndef preprocess(input_root, output_root, contract): pass\ndef validate_preprocessing(output_root, contract): pass\n'
        (folder/'revised.ipynb').write_text(json.dumps({'cells':[{'cell_type':'code','source':['%%writefile /content/sprint13_pipeline.py\n'+code]}]}))
        for n in ['notebook.diff','patch-receipt.json']:(folder/n).write_bytes(b'synthetic')
        v['local_row']={'id':m.ID,'stage':'run_spec_author','attempt':1,'status':'COMPLETE','receipt':json.dumps({'output_sha256':{n:m.sha((work/n).read_bytes()) for n in ['SPEC.proposed.md','notebook.patch.json']}})}
        v['global_row']={'id':m.ID,'status':'COMPLETE','receipt':v['local_row']['receipt']}
        b=copy.deepcopy(m.binding());b.update(config_sha256=m.sha(cfg),output_sha256=json.loads(v['local_row']['receipt'])['output_sha256'],console_sha256=m.sha((work/'console.log').read_bytes()),derived_sha256={p.name:m.sha(p.read_bytes()) for p in folder.iterdir()})
        for name in ['state_row','account_row','local_row','global_row']:
            key={'state_row':'state_sha256','account_row':'account_sha256'}.get(name,name+'_sha256');b[key]=m.sha(m.canonical(v[name]))
        monkeypatch.setattr(m,'binding',lambda:b)
    (lane/'lane.json').write_bytes(cfg);db=sqlite3.connect(lane/'jobs.sqlite')
    for name,key in [('manual_state','state_row'),('manual_account','account_row'),('manual_calls','local_row')]:create_table(db,name,v[key])
    db.commit();db.close();db=sqlite3.connect(p(m.LEDGER));create_table(db,'autonomy_calls',v['global_row']);db.commit();db.close()
    for f in root.rglob('*'):f.chmod(0o700 if f.is_dir() else 0o600)
    monkeypatch.setattr(m,'authority',lambda:{'report_sha256':'a'*64});monkeypatch.setattr(m.os,'getuid',lambda:1003);monkeypatch.setattr(m.os,'getgid',lambda:1003)
    return NS(root=root,lane=lane,work=work,folder=folder,original=v,binding=b,ledger=p(m.LEDGER),dest=p(m.CONTINUATION))

def test_resume_preserves_complete_attempt_and_pending_then_counts_next(tmp_path,monkeypatch):
    f=fixture(tmp_path,monkeypatch);old={p:m.sha(p.read_bytes()) for p in [*f.work.iterdir(),*f.folder.iterdir(),f.ledger]}
    assert m.resume(tmp_path,check_unit=lambda:None)['next_author']==2
    review,original,live=m.verify_record(tmp_path)
    assert live['local_row']==original['local_row'] and live['global_row']==original['global_row'] and live['account_row']==original['account_row']
    state=json.loads(live['state_row']['payload']);assert state['rounds']=={} and 'pending' not in state
    assert original['state_row']==f.original['state_row'] and all(m.sha(p.read_bytes())==pin for p,pin in old.items())
    class Base:
        def model_round_number(self,value):return value['rounds'].get(value['phase'],0)+1
        def task(self,stage,value):return 'Original scientific instructions'
    module=NS(AnalysisDriver=Base);m.install_hook(module);driver=module.AnalysisDriver();driver.config={'run_id':m.RUN};driver.store=NS(db=sqlite3.connect(f.lane/'jobs.sqlite'))
    real=m.verify_record;monkeypatch.setattr(m,'verify_record',lambda:real(tmp_path))
    assert driver.model_round_number(state)==2
    assert 'EXACTLY ONCE' in driver.task('run_spec_author',state)
    assert 'def entrypoints(source, *, preprocessing=False):' in driver.task('run_spec_author',state)
    with pytest.raises(ValueError,match='RECORD_PRESERVED'):m.resume(tmp_path,check_unit=lambda:None)
    driver.store.db.close()

@pytest.mark.parametrize('damage',['REVISE','REJECT','unknown','local-uncertain','global-running','other-running','accepted','config','partial-file','partial-extra-dir','output','stream','account','existing-record','halt'])
def test_unknown_or_scientific_review_states_never_unblocked(tmp_path,monkeypatch,damage):
    f=fixture(tmp_path,monkeypatch)
    if damage in ['REVISE','REJECT','unknown','accepted','account','local-uncertain']:
        db=sqlite3.connect(f.lane/'jobs.sqlite')
        if damage=='local-uncertain':db.execute("UPDATE manual_calls SET status='UNCERTAIN'")
        elif damage=='account':db.execute('UPDATE manual_account SET version=2')
        else:
            state=json.loads(f.original['state_row']['payload']);state['reason']=damage
            if damage=='accepted':state['rounds']={'run_spec_author':1}
            db.execute('UPDATE manual_state SET payload=?',(json.dumps(state),))
        db.commit();db.close()
    elif damage in ['global-running','other-running']:
        db=sqlite3.connect(f.ledger)
        if damage=='global-running':db.execute("UPDATE autonomy_calls SET status='RUNNING'")
        else:db.execute('INSERT INTO autonomy_calls VALUES(?,?,?)',('foreign','RUNNING',None))
        db.commit();db.close()
    elif damage=='config':(f.lane/'lane.json').write_bytes(b'changed')
    elif damage=='partial-file':(f.folder/'revised.ipynb').write_bytes(b'changed')
    elif damage=='partial-extra-dir':(f.folder/'extra').mkdir()
    elif damage=='output':(f.work/'notebook.patch.json').write_bytes(b'changed')
    elif damage=='stream':(f.work/'console.log').write_bytes(b'changed')
    elif damage=='existing-record':f.dest.mkdir()
    else:(f.lane/'HALT').write_bytes(b'held')
    with pytest.raises(ValueError):m.resume(tmp_path,check_unit=lambda:None)
    assert not (f.dest/'COMPLETE.json').exists()

def test_delivered_validator_is_exact_and_rejects_original_duplicate(tmp_path):
    from orchestrator import notebook_execution as ne
    import inspect
    text=m.feedback();assert inspect.getsource(ne.entrypoints) in text
    script=text.split('```python\n',1)[1].split('```',1)[0];namespace={'__name__':'not_main'};exec(script,namespace)
    with pytest.raises(ValueError,match='ENTRYPOINT:preprocess'):namespace['entrypoints']('def main(input_root,output_root,contract): pass\ndef synthetic_tests(): pass\ndef preprocess(input_root,output_root,contract): pass\ndef preprocess(input_root,output_root,contract): pass\ndef validate_preprocessing(output_root,contract): pass',preprocessing=True)
