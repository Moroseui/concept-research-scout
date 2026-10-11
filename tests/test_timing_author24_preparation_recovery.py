import copy,json,os,sqlite3,stat
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import timing_author24_preparation_recovery as r

pytestmark=pytest.mark.skipif(os.getuid()!=0,reason='Exact service-owned fixture requires local root chown')

def fixture(root,monkeypatch):
    root=Path(root);lane=root/str(r.LANE).lstrip('/');work=root/str(r.WORK).lstrip('/');pins=root/str(r.PINS).lstrip('/');ledger=root/str(r.LEDGER).lstrip('/')
    for p in [lane,work,pins.parent,ledger.parent]:p.mkdir(parents=True,exist_ok=True,mode=0o700)
    (work/'.author-runtime').mkdir(mode=0o700);(work/'.author-runtime/config.json').write_bytes(b'synthetic preserved config')
    (work/'evidence').mkdir(mode=0o700);(work/'evidence/synthetic.txt').write_bytes(b'aggregate synthetic input')
    (work/'prompt.md').write_bytes(b'synthetic prompt');pins.write_bytes(b'{"synthetic":"pins"}')
    cfg=b'{"run_id":"experiment-a74959ac4546a982af4ae137"}'
    (lane/'lane.json').write_bytes(cfg)
    db=sqlite3.connect(lane/'jobs.sqlite');db.row_factory=sqlite3.Row
    db.executescript('CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT);CREATE TABLE manual_account(id INTEGER PRIMARY KEY,version INTEGER,payload TEXT);CREATE TABLE manual_calls(id TEXT PRIMARY KEY,stage TEXT,attempt INTEGER,status TEXT,receipt TEXT);')
    db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps({'phase':'run_spec_author','rounds':{'run_spec_author':23,'run_spec_review':15},'pending':None}),))
    db.execute('INSERT INTO manual_account VALUES(1,38,?)',('{"count":14,"sequence":38}',))
    for i in range(38):db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(str(i),'run_spec_author' if i<23 else 'run_spec_review',i+1,'COMPLETE','{}'))
    db.commit();rows=r.snapshot(db);db.close()
    g=sqlite3.connect(ledger);g.execute('CREATE TABLE autonomy_calls(id TEXT PRIMARY KEY,status TEXT)');g.commit();g.close()
    for p in [root,*root.rglob('*')]:os.chown(p,1003,1003);p.chmod(0o700 if p.is_dir() else 0o600)
    b=copy.deepcopy(r.binding());b.update(config_sha256=r.sha(cfg),tree=r.inventory(work),pins_metadata=r.metadata(pins))
    for k in ['state','account','calls']:b[k+'_sha256']=r.sha(r.canonical(rows[k]))
    monkeypatch.setattr(r,'binding',lambda:b);monkeypatch.setattr(r,'authority',lambda folder:{'report_sha256':'a'*64});monkeypatch.setattr(r.os,'getuid',lambda:1003);monkeypatch.setattr(r.os,'getgid',lambda:1003)
    return NS(root=root,lane=lane,work=work,pins=pins,ledger=ledger,rows=rows,binding=b,dest=root/str(r.ARCHIVE).lstrip('/'))

def test_exact_archive_preserves_bytes_rows_and_allows_fresh_preparation(tmp_path,monkeypatch):
    f=fixture(tmp_path,monkeypatch);before={p:p.read_bytes() for p in [f.lane/'lane.json',f.lane/'jobs.sqlite',f.ledger]}
    out=r.apply(tmp_path/'review',filesystem_root=tmp_path,check_unit=lambda:None)
    assert out['model_calls']==out['ledger_changes']==0
    assert not f.work.exists() and not f.pins.exists()
    assert r.inventory(f.dest/'workspace')==f.binding['tree'];assert r.metadata(f.dest/'runtime-pins-24.json')==f.binding['pins_metadata']
    assert all(p.read_bytes()==raw for p,raw in before.items())
    # The original exclusive directory creation is unmodified and usable again.
    f.work.mkdir(mode=0o700);(f.work/'.author-runtime').mkdir(mode=0o700)
    with pytest.raises(FileExistsError):(f.work/'.author-runtime').mkdir(mode=0o700)
    with pytest.raises(ValueError,match='ARCHIVE_PRESERVED'):r.apply(tmp_path/'review',filesystem_root=tmp_path,check_unit=lambda:None)

@pytest.mark.parametrize('damage',['local-call','global-call','running','state','account','config','extra-directory','symlink','hardlink','changed-file','pins','partial','halt'])
def test_uncertain_or_changed_preparation_refuses_before_move(tmp_path,monkeypatch,damage):
    f=fixture(tmp_path,monkeypatch)
    if damage in ['local-call','state','account']:
        db=sqlite3.connect(f.lane/'jobs.sqlite')
        if damage=='local-call':db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(r.ID,'run_spec_author',24,'RUNNING',None))
        elif damage=='state':db.execute('UPDATE manual_state SET payload=?',('{"phase":"MODEL_RUNNING"}',))
        else:db.execute('UPDATE manual_account SET version=39')
        db.commit();db.close()
    elif damage in ['global-call','running']:
        db=sqlite3.connect(f.ledger);db.execute('INSERT INTO autonomy_calls VALUES(?,?)',(r.ID if damage=='global-call' else 'unknown','FAILED' if damage=='global-call' else 'RUNNING'));db.commit();db.close()
    elif damage=='config':(f.lane/'lane.json').write_bytes(b'changed')
    elif damage=='extra-directory':p=f.work/'extra';p.mkdir(mode=0o700);os.chown(p,1003,1003)
    elif damage=='symlink':(f.work/'link').symlink_to(f.work/'prompt.md')
    elif damage=='hardlink':os.link(f.work/'prompt.md',f.work/'link')
    elif damage=='changed-file':(f.work/'prompt.md').write_bytes(b'changed')
    elif damage=='pins':f.pins.write_bytes(b'changed')
    elif damage=='partial':f.dest.mkdir(mode=0o700)
    else:(f.lane/'HALT').write_bytes(b'held')
    with pytest.raises(ValueError):r.apply(tmp_path/'review',filesystem_root=tmp_path,check_unit=lambda:None)
    assert f.work.is_dir() and f.pins.is_file()

def test_original_failed_unit_identity_is_exact(monkeypatch):
    b=r.binding();unit=dict(b['failed_unit']);unit.pop('name')
    monkeypatch.setattr(r.subprocess,'check_output',lambda *a,**kw:'\n'.join(k+'='+v for k,v in {**unit,'InvocationID':'f'*32}.items()))
    with pytest.raises(ValueError,match='FAILED_INVOCATION'):r.held_unit()

def test_actual_captured_document_has_complete_closed_tree():
    b=r.binding();assert len(b['tree'])==624;assert sum(x['type']=='file' for x in b['tree'].values())==620
    assert b['tree']['.author-runtime']['type']=='directory' and b['tree']['evidence']['type']=='directory'

@pytest.mark.parametrize('damage',[None,'report','status','tree','pins'])
def test_runtime_requires_exact_preserved_archive(tmp_path,monkeypatch,damage):
    from tools import timing_author24_runtime as runtime
    f=fixture(tmp_path,monkeypatch)
    r.apply(tmp_path/'review',filesystem_root=tmp_path,check_unit=lambda:None)
    monkeypatch.setattr(r,'ARCHIVE',f.dest)
    monkeypatch.setattr(runtime,'load',lambda name,path:r)
    monkeypatch.setattr(runtime,'authority',lambda:{'report_sha256':'a'*64})
    if damage in ['report','status']:
        p=f.dest/'COMPLETE.json';v=json.loads(p.read_bytes());v['review_sha256' if damage=='report' else 'status']='wrong';p.write_bytes(r.canonical(v))
    elif damage=='tree':(f.dest/'workspace/prompt.md').write_bytes(b'changed')
    elif damage=='pins':(f.dest/'runtime-pins-24.json').write_bytes(b'changed')
    if damage:
        with pytest.raises(ValueError):runtime.preservation()
    else:assert runtime.preservation()['status']=='PRESERVED_UNADMITTED_PREPARATION'
