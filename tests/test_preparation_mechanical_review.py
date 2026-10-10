"""Synthetic exact predecessor and linked approval bindings; no model calls."""
import copy,hashlib,json,sqlite3
from pathlib import Path
import pytest
from tools import review_preparation_cap_repair_once as boot
from tools import install_preparation_runtime as install,preparation_host_operation as host,repair_temporary_daily_cap_permissions as repair

canonical=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode()

@pytest.fixture
def predecessor(tmp_path,monkeypatch):
    original={'change_id':boot.RELEASE_CHANGE,'round':1,'source_sha':'a'*40}
    files={'packet-manifest.json':canonical(original),'process-exit.json':canonical({'exit_code':0,'uncertain':False}),
           'submission.json':canonical({'submission':{'verdict':'APPROVE','findings':[]}}),'native-stream.jsonl':b'synthetic native stream'}
    receipt={'accounting_units':1,'exit_code':0,'uncertain':False,'reason':'SUCCESSFUL_NATIVE_SCOPE_AND_SOURCE_READS_REQUIRED',
        'native_stream_sha256':boot.sha(files['native-stream.jsonl']),'submission_sha256':boot.sha(files['submission.json'])}
    row={'id':'f'*64,'kind':'implementation_review','change_id':boot.RELEASE_CHANGE,'round':1,'day':'2026-10-10',
         'status':'FAILED','binding':json.dumps({'manifest':original}),'receipt':json.dumps(receipt)}
    link={'original_packet':row['id'],'original_row_sha256':boot.sha(canonical(row)),'original_source':'a'*40,
          'original_files':{name:boot.sha(raw) for name,raw in files.items()}}
    path=tmp_path/boot.LINK_DOCUMENT;path.parent.mkdir();path.write_bytes(canonical(link))
    monkeypatch.setattr(boot,'SOURCE',tmp_path);monkeypatch.setattr(boot,'LINK_SHA',boot.sha(path.read_bytes()))
    db=sqlite3.connect(':memory:',isolation_level=None);db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE autonomy_calls(id TEXT,kind TEXT,change_id TEXT,round INTEGER,day TEXT,status TEXT,binding TEXT,receipt TEXT)')
    for n in range(51):db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',(str(n),'implementation_review','old',1,'2026-10-10','COMPLETE','{}','{}'))
    db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',tuple(row.values()))
    reader=lambda p:files[Path(p).name]
    yield db,row,files,reader,path
    db.close()


def test_exact_mechanical_original_remains_counted_and_unchanged(predecessor):
    db,row,files,reader,path=predecessor;before=[tuple(r) for r in db.execute('SELECT * FROM autonomy_calls')]
    proof=boot.admission_preflight(db,'new-packet','2026-10-10',reader)
    assert proof['original_packet']==row['id'] and db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==52
    assert [tuple(r) for r in db.execute('SELECT * FROM autonomy_calls')]==before


@pytest.mark.parametrize('field,value',[('status','COMPLETE'),('status','UNCERTAIN'),('receipt','{}'),('binding','{}'),('round',2),('change_id','unrelated')])
def test_changed_or_uncertain_original_refuses(predecessor,field,value):
    db,row,files,reader,path=predecessor;db.execute('UPDATE autonomy_calls SET '+field+'=? WHERE id=?',(value,row['id']))
    with pytest.raises(ValueError,match='MECHANICAL_PREDECESSOR_CHANGED'):boot.admission_preflight(db,'new','2026-10-10',reader)


@pytest.mark.parametrize('fault',['count51','count53','running','successor','day','files','link'])
def test_exact_one_use_daily_and_original_bindings(predecessor,fault):
    db,row,files,reader,path=predecessor;day='2026-10-10'
    if fault=='count51':db.execute("DELETE FROM autonomy_calls WHERE id='0'")
    elif fault=='count53':db.execute("INSERT INTO autonomy_calls VALUES('extra','implementation_review','old',1,'2026-10-10','COMPLETE','{}','{}')")
    elif fault=='running':db.execute("UPDATE autonomy_calls SET status='RUNNING' WHERE id='0'")
    elif fault=='successor':db.execute('UPDATE autonomy_calls SET change_id=? WHERE id=?',(boot.CHANGE,'0'))
    elif fault=='day':day='2026-10-11'
    elif fault=='files':files['native-stream.jsonl']+=b'changed'
    else:path.write_bytes(path.read_bytes()+b' ')
    before=[tuple(r) for r in db.execute('SELECT * FROM autonomy_calls')]
    with pytest.raises(ValueError):boot.admission_preflight(db,'new',day,reader)
    assert [tuple(r) for r in db.execute('SELECT * FROM autonomy_calls')]==before


def test_transaction_rechecks_original_and_call53(predecessor,monkeypatch):
    db,row,files,reader,path=predecessor;original=boot.admission_preflight
    monkeypatch.setattr(boot,'admission_preflight',lambda connection,packet,day:original(connection,packet,day,reader))
    selected=boot.dated_bootstrap(lambda day:{'limit':100}, {'db':db}, 'new')
    with pytest.raises(ValueError,match='ADMISSION_TRANSACTION_REQUIRED'):selected('2026-10-10')
    db.execute('BEGIN IMMEDIATE');assert selected('2026-10-10')['limit']==100;db.execute('ROLLBACK')
    db.execute("INSERT INTO autonomy_calls VALUES('extra','implementation_review','old',1,'2026-10-10','COMPLETE','{}','{}')")
    db.execute('BEGIN IMMEDIATE')
    with pytest.raises(ValueError,match='EXACT_CALL53'):selected('2026-10-10')
    db.execute('ROLLBACK')


@pytest.mark.parametrize('module',[install,host,repair])
def test_only_exact_review_link_can_authorize_same_release(tmp_path,monkeypatch,module):
    monkeypatch.setattr(module,'trusted',lambda p:Path(p))
    path=tmp_path/module.LINK_DOCUMENT;path.parent.mkdir();path.write_bytes(b'synthetic pinned link')
    monkeypatch.setattr(module,'LINK_SHA',boot.sha(path.read_bytes()))
    manifest={'source_files':{module.LINK_DOCUMENT:module.LINK_SHA}}
    assert module.review_change({'change_id':module.CHANGE},manifest,tmp_path)
    assert module.review_change({'change_id':module.LINKED_REVIEW_CHANGE},manifest,tmp_path)
    assert not module.review_change({'change_id':module.LINKED_REVIEW_CHANGE+'-other'},manifest,tmp_path)
    assert not module.review_change({'change_id':module.LINKED_REVIEW_CHANGE},{'source_files':{}},tmp_path)
    path.write_bytes(b'changed')
    assert not module.review_change({'change_id':module.LINKED_REVIEW_CHANGE},manifest,tmp_path)


@pytest.mark.parametrize('verdict,findings',[('REJECT',[]),('REVISE',[]),('APPROVE',[{'synthetic':'unresolved finding'}])])
def test_genuine_disagreement_is_never_mechanical_retry(predecessor,monkeypatch,verdict,findings):
    db,row,files,reader,path=predecessor
    files['submission.json']=canonical({'submission':{'verdict':verdict,'findings':findings}})
    receipt=json.loads(row['receipt']);receipt['submission_sha256']=boot.sha(files['submission.json']);row['receipt']=json.dumps(receipt)
    db.execute('UPDATE autonomy_calls SET receipt=? WHERE id=?',(row['receipt'],row['id']))
    link=json.loads(path.read_bytes());link['original_row_sha256']=boot.sha(canonical(row));link['original_files']['submission.json']=boot.sha(files['submission.json'])
    path.write_bytes(canonical(link));monkeypatch.setattr(boot,'LINK_SHA',boot.sha(path.read_bytes()))
    with pytest.raises(ValueError,match='MECHANICAL_NOT_REJECT_OR_REVISE'):
        boot.admission_preflight(db,'new','2026-10-10',reader)
