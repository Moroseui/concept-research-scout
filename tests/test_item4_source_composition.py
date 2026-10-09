"""Synthetic transfer refusal tests; no patient files, network or provider."""
import io,json,tarfile,csv,os
from types import SimpleNamespace as NS
from pathlib import Path
import pytest
from orchestrator import modal_source_composition as m,private_records as pr
from tools import item4_source_preparation as h

def row(raw):return {'bytes':len(raw),'sha256':m.digest(raw)}

def archive(items):
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w') as out:
        for name,raw,kind in items:
            info=tarfile.TarInfo(name);info.type=kind;info.size=len(raw) if kind==tarfile.REGTYPE else 0
            if kind in (tarfile.LNKTYPE,tarfile.SYMTYPE):info.linkname='outside'
            out.addfile(info,io.BytesIO(raw) if kind==tarfile.REGTYPE else None)
    stream.seek(0);return stream

def test_exact_stream_and_duplicate_refusal(tmp_path):
    pr.mkdir(tmp_path/'data');r=tmp_path/'data';expected={'nested/a.bin':row(b'abc')}
    assert m.ingest_tar(archive([('nested/a.bin',b'abc',tarfile.REGTYPE)]),r,expected)=={'files':1,'bytes':3}
    assert (r/'nested/a.bin').read_bytes()==b'abc'
    with pytest.raises(ValueError,match='EXISTING_OUTPUT'):m.write_verified(r,'nested/a.bin',row(b'abc'),[b'abc'])
    assert (r/'nested/a.bin').read_bytes()==b'abc'

@pytest.mark.parametrize('kind',[tarfile.SYMTYPE,tarfile.LNKTYPE,tarfile.DIRTYPE,tarfile.FIFOTYPE])
def test_tar_nonregular_members_never_write(tmp_path,kind):
    with pytest.raises(ValueError,match='TAR_MEMBER'):m.ingest_tar(archive([('a',b'',kind)]),tmp_path,{'a':row(b'abc')})
    assert list(tmp_path.iterdir())==[]

@pytest.mark.parametrize('items,expected_code',[
    ([('../outside',b'abc',tarfile.REGTYPE)],'TAR_MEMBER'),
    ([('a',b'ab',tarfile.REGTYPE)],'TAR_MEMBER'),
    ([('a',b'bad',tarfile.REGTYPE)],'STREAM_HASH'),
    ([('a',b'abc',tarfile.REGTYPE),('a',b'abc',tarfile.REGTYPE)],'TAR_MEMBER'),
    ([],'TAR_EXACT_MEMBERS')])
def test_wrong_or_incomplete_tar_is_not_accepted(tmp_path,items,expected_code):
    with pytest.raises(ValueError,match=expected_code):m.ingest_tar(archive(items),tmp_path,{'a':row(b'abc')})

@pytest.mark.parametrize('chunks,code',[([b'ab'],'STREAM_HASH'),([b'abcd'],'STREAM_SIZE'),([b'bad'],'STREAM_HASH')])
def test_stream_mismatch_stays_unaccepted(tmp_path,chunks,code):
    with pytest.raises(ValueError,match=code):m.write_verified(tmp_path,'a',row(b'abc'),chunks)
    assert (tmp_path/'a').stat().st_size<=3

def test_link_and_escape_refuse_without_touching_original(tmp_path):
    outside=tmp_path/'outside';outside.write_bytes(b'original');root=tmp_path/'data';pr.mkdir(root)
    (root/'alias').symlink_to(outside)
    for name in ['alias','../outside','/absolute']:
        with pytest.raises(ValueError):m.write_verified(root,name,row(b'x'),[b'x'])
    assert outside.read_bytes()==b'original'

def test_copy_refuses_hardlink_original(tmp_path):
    original=tmp_path/'original';original.write_bytes(b'abc');os.link(original,tmp_path/'alias');root=tmp_path/'data';pr.mkdir(root)
    with pytest.raises(ValueError,match='PRIVATE_RECORD_HARDLINK'):m.copy_local(original,root,'a',row(b'abc'))
    assert not list(root.iterdir())

class Volume:
    object_id='vo-synthetic'
    def __init__(self):self.files={'images/a':b'abc','ctp/untouched':b'not-read'};self.reads=[];self.changed=False
    def listdir(self,*a,**kw):
        return [NS(path=n,size=len(v),type=NS(name='FILE')) for n,v in self.files.items()]
    def read_file(self,name):
        self.reads.append(name);yield self.files[name.lstrip('/')]
        if self.changed:self.files['unexpected']=b'x'

def test_remote_copy_reads_only_selected_images(tmp_path):
    v=Volume();provider=NS(_volume=lambda ident:v)
    m.copy_images(provider,v.object_id,tmp_path,{'a':row(b'abc')})
    assert v.reads==['/images/a'] and (tmp_path/'a').read_bytes()==b'abc'
    assert v.files['ctp/untouched']==b'not-read'

def test_remote_membership_change_refuses(tmp_path):
    v=Volume();v.changed=True
    with pytest.raises(ValueError,match='SOURCE_MEMBERS_CHANGED'):m.copy_images(NS(_volume=lambda _:v),v.object_id,tmp_path,{'a':row(b'abc')})

def test_cleanup_only_new_known_tree(tmp_path,monkeypatch):
    monkeypatch.setattr(h,'STATE',tmp_path);data=tmp_path/'data';pr.mkdir(data);(data/'a').write_bytes(b'ab')
    unrelated=tmp_path/'original';unrelated.write_bytes(b'abc')
    h.clear_local(data,{'a':row(b'abc')});assert unrelated.read_bytes()==b'abc' and not data.exists()
    pr.mkdir(data);(data/'unknown').write_bytes(b'x')
    with pytest.raises(ValueError,match='CLEANUP_UNKNOWN_LOCAL'):h.clear_local(data,{'a':row(b'abc')})
    assert (data/'unknown').read_bytes()==b'x'

@pytest.fixture
def synthetic_contract(tmp_path,monkeypatch):
    case=lambda i:'sub-'+'stroke'+str(i).zfill(4)
    cases=[case(i) for i in range(1,100)]
    base={n:row(b'x') for n in m.frozen.expected_paths(cases)}
    aux={**{'feature-cache-2mm-v2/'+c+'.npz':row(b'x') for c in cases},'baseline/plans.json':row(b'x'),'baseline/handoff.json':row(b'x')}
    split='case_id,population\n'+''.join(case(i)+','+('census' if i<=100 else 'reserved')+'\n' for i in range(1,150))
    for n,raw in {'cohort.json':json.dumps({'cases':cases}).encode(),'source.json':b'{}','auxiliary.json':b'{}','authority.txt':b'synthetic','split.csv':split.encode()}.items():pr.write_bytes(tmp_path/n,raw)
    monkeypatch.setattr(m.frozen,'frozen_inventory',lambda *a:{'files':base})
    monkeypatch.setattr(m.frozen,'frozen_auxiliary',lambda *a:aux)
    monkeypatch.setattr(m,'SPLIT',m.digest(split.encode()));monkeypatch.setattr(m,'DATA_BYTES',893)
    monkeypatch.setattr(m,'INVENTORY',m.digest(m.canonical({**base,**aux})))
    return tmp_path,case

def test_all49_exclusions_checked_before_payload_access(synthetic_contract):
    root,case=synthetic_contract;files,proof=m.contract(root)
    assert len(files)==893 and proof['excluded_count']==49 and proof['excluded_overlap']==0
    cohort=json.loads((root/'cohort.json').read_bytes());cohort['cases'][0]=case(101)
    pr.write_bytes(root/'cohort.json',json.dumps(cohort).encode())
    with pytest.raises(ValueError,match='EXCLUDED_PATIENT'):m.contract(root)
