"""Source lifecycle against real ledger and synthetic file/provider boundaries."""
from pathlib import Path
from types import SimpleNamespace as NS
import json
import pytest
from orchestrator import modal_source_composition as m,modal_source_budget as q,private_records as pr
from orchestrator.modal_assets import local_files
from orchestrator.modal_executor import canonical
from tools import item4_source_preparation as h
from test_item4_source_composition import synthetic_contract,row
from test_item4_source_budget import prepared,unreserved,unreserved_fixture,inventory_fixture,experiment,root,reserve

class Volume:
    def __init__(self,ident,files=None):self.object_id=ident;self.files=files or {};self.reads=[]
    def hydrate(self,**kw):return self
    def listdir(self,*a,**kw):return [NS(path=n,size=len(v),type=NS(name='FILE')) for n,v in self.files.items()]
    def read_file(self,name):self.reads.append(name);yield self.files[name.lstrip('/')]
    def remove_file(self,name,recursive=False):assert not recursive;del self.files[name.lstrip('/')]
    def batch_upload(self,force):
        assert force is False;v=self
        class Batch:
            def __enter__(self):return self
            def put_file(self,path,name,mode):
                assert mode==0o440 and name.lstrip('/') not in v.files
                if getattr(v,'fail_upload',False):raise OSError('synthetic transport interrupted')
                v.files[name.lstrip('/')]=Path(path).read_bytes()
            def __exit__(self,*args):return False
        return Batch()

class Provider:
    class NotFound(Exception):pass
    def __init__(self,images):
        self.source=Volume(q.DIRECT_VOLUME,{'images/'+n:b'x' for n in images});self.destination=None;self.creates=0;self.client=object();self.fail_upload=False
        self.modal=NS(exception=NS(NotFoundError=self.NotFound),Volume=NS(from_name=self.from_name))
    def from_name(self,name,*,create_if_missing,version,client):
        assert version==2 and client is self.client
        if not create_if_missing:
            if self.destination is None:raise self.NotFound()
            return self.destination
        assert self.destination is None;self.creates+=1;self.destination=Volume('vo-created');self.destination.fail_upload=self.fail_upload;return self.destination
    def _volume(self,ident):
        if ident==self.source.object_id:return self.source
        assert self.destination is not None and ident==self.destination.object_id;return self.destination
    def _verify_volume_members(self,ident,expected):
        volume=self._volume(ident);assert {n:len(v) for n,v in volume.files.items()}=={n:r['bytes'] for n,r in expected.items()};return volume
    def _verify_volume(self,ident,expected):
        volume=self._verify_volume_members(ident,expected)
        assert {n:row(v) for n,v in volume.files.items()}==expected;return volume

@pytest.fixture
def ready(prepared,synthetic_contract,tmp_path,monkeypatch):
    f=prepared;metadata,_=synthetic_contract;files,proof=m.contract(metadata)
    # The catalog fixture is synthetic and still exercises all893 exact members.
    f.source_binding['inventory_sha256']=m.INVENTORY
    f.source_binding['envelope']=q.envelope(f.view['rates'])
    config={'synthetic_fixture':True};f.source_binding['config_sha256']=m.digest(canonical(config))
    assert reserve(f)
    state=tmp_path/'state';pr.mkdir(state);incoming=state/'incoming';pr.mkdir(incoming);cache_root=tmp_path/'cache';pr.mkdir(cache_root)
    monkeypatch.setattr(h,'STATE',state);monkeypatch.setattr(h,'METADATA',metadata);monkeypatch.setattr(h,'CACHE',cache_root)
    images,brain,cache,baseline=m.partitions(files)
    for name,item in {**brain,**baseline}.items():m.write_verified(incoming,name,item,[b'x'])
    for name,item in cache.items():pr.write_bytes(cache_root/Path(name).name,b'x')
    ident=m.digest(canonical(f.source_binding));pr.write_bytes(state/'binding.json',canonical(f.source_binding));pr.write_bytes(state/'STAGED.json',canonical({'binding_sha256':ident}))
    monkeypatch.setattr(h,'direct_proof',lambda *a:{'status':'VERIFIED','source_volume_id':q.DIRECT_VOLUME})
    f.source_provider=Provider(images);f.source_state=state;f.source_config=config;f.source_files=files;f.source_id=ident;return f

def test_complete893_copy_verified_once_and_original_untouched(ready):
    f=ready;before=dict(f.source_provider.source.files)
    v=h.prepare(f.accounts,f.source_provider,f.source_config)
    assert v['status']=='VERIFIED' and v['membership']['files']==893 and f.source_provider.creates==1
    assert len(f.source_provider.destination.files)==893 and before==f.source_provider.source.files
    local_files(f.source_state/'data',f.source_files)
    saved=f.accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(f.source_id,)).fetchone()
    assert saved['status']=='READY' and json.loads(saved['receipt'])==v
    with pytest.raises(ValueError,match='EXISTING_ATTEMPT_NO_RETRY'):h.prepare(f.accounts,f.source_provider,f.source_config)
    assert f.source_provider.creates==1 and f.accounts.db.execute('SELECT reserved_micro_usd FROM autonomy_assets WHERE id=?',(f.source_id,)).fetchone()[0]==f.source_binding['envelope']['reserved_micro_usd']

@pytest.mark.parametrize('failure',['source-hash','upload'])
def test_failure_keeps_charge_and_never_repeats_create(ready,failure):
    f=ready
    if failure=='source-hash':f.source_provider.source.files[next(iter(f.source_provider.source.files))]=b'y'
    else:f.source_provider.fail_upload=True
    with pytest.raises(ValueError,match='PREPARATION_FAILED_RECONCILE'):h.prepare(f.accounts,f.source_provider,f.source_config)
    record=f.accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(f.source_id,)).fetchone()
    assert record['status']=='UNCERTAIN' and record['reserved_micro_usd']==f.source_binding['envelope']['reserved_micro_usd']
    assert f.source_provider.creates==(0 if failure=='source-hash' else 1)
    with pytest.raises(ValueError,match='EXISTING_ATTEMPT_NO_RETRY'):h.prepare(f.accounts,f.source_provider,f.source_config)
    assert f.source_provider.creates==(0 if failure=='source-hash' else 1)

def test_unknown_create_cannot_delete_any_remote_source(ready,monkeypatch):
    f=ready
    from datetime import datetime,timezone,timedelta
    class Clock:
        @staticmethod
        def now(zone):return datetime.fromisoformat(f.source_binding['expires_at'])+timedelta(seconds=1)
    monkeypatch.setattr(h,'datetime',Clock)
    # No replacement binding/charge: advance only the observation clock.
    Clock.fromisoformat=staticmethod(datetime.fromisoformat)
    h.intent('volume-create-intent',{'binding_sha256':f.source_id,'name':'unreturned','version':2})
    before=dict(f.source_provider.source.files)
    with pytest.raises(ValueError,match='UNKNOWN_CREATE_RECONCILE'):h.cleanup(f.accounts,f.source_provider,f.source_config)
    assert before==f.source_provider.source.files and f.source_provider.creates==0

def test_retention_removes_only_new_copies_and_retains_charge(ready,monkeypatch):
    f=ready;h.prepare(f.accounts,f.source_provider,f.source_config)
    from datetime import datetime,timedelta
    class Clock:
        fromisoformat=staticmethod(datetime.fromisoformat)
        @staticmethod
        def now(zone):return datetime.fromisoformat(f.source_binding['expires_at'])+timedelta(seconds=1)
    monkeypatch.setattr(h,'datetime',Clock)
    before=dict(f.source_provider.source.files);v=h.cleanup(f.accounts,f.source_provider,f.source_config)
    assert v['status']=='CLEARED' and v['reservation_retained'] is True
    assert before==f.source_provider.source.files and not f.source_provider.destination.files
    assert not (f.source_state/'incoming').exists() and not (f.source_state/'data').exists()
    assert h.cleanup(f.accounts,f.source_provider,f.source_config)==v
    assert f.accounts.db.execute('SELECT reserved_micro_usd FROM autonomy_assets WHERE id=?',(f.source_id,)).fetchone()[0]==f.source_binding['envelope']['reserved_micro_usd']
