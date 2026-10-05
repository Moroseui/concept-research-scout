"""Exact copied-asset cleanup; no actual network, data or provider operation."""
from datetime import datetime,timezone
from pathlib import Path
import pytest
from orchestrator import private_records,modal_cleanup,connectivity
from orchestrator.modal_assets import asset_estimate
from orchestrator.manual_executor import digest,read,inventory
from test_modal_provider import Volume,ModalProvider

class Removable(Volume):
    def __init__(self,files):super().__init__(files);self.removed=[];self.fail=False
    def remove_file(self,path,recursive=False):
        assert not recursive;self.removed.append(path);del self.files[path.lstrip('/')]
        if self.fail:self.fail=False;raise TimeoutError('Synthetic lost deletion acknowledgement')

@pytest.fixture
def copies(tmp_path,monkeypatch):
    monkeypatch.setattr(connectivity,'require',lambda *a,**k:{'synthetic':True})
    config={'asset_expires_utc':'2099-01-01T00:00:00+00:00','local_assets':{}};volumes={}
    for kind in ['data','wheels','package']:
        folder=tmp_path/kind;private_records.mkdir(folder);name='manifest.json' if kind=='package' else 'original'
        private_records.write_bytes(folder/name,b'original')
        config['local_assets'][kind]=str(folder);config[{'data':'data_volume_id','wheels':'wheel_volume_id','package':'package_volume_id'}[kind]]='vo-'+kind
        files={name:{'sha256':digest(b'original'),'bytes':8}}
        if kind!='package':config['data_files' if kind=='data' else 'wheel_files']=files
        volumes['vo-'+kind]=Removable({name:b'original'})
    p=object.__new__(ModalProvider);p._volume=lambda ident:volumes[ident]
    return p,config,tmp_path/'cleanup',volumes


def test_clears_only_verified_remote_copies_and_preserves_originals(copies):
    p,c,record,volumes=copies;before={kind:inventory(path) for kind,path in c['local_assets'].items()}
    assert modal_cleanup.clear_copies(p,c,record)['status']=='NOT_DUE' and not record.exists()
    assert modal_cleanup.clear_copies(p,c,record,collected=True)['status']=='CLEARED'
    assert all(not v.files and len(v.removed)==1 for v in volumes.values())
    assert before=={kind:inventory(path) for kind,path in c['local_assets'].items()}
    assert modal_cleanup.clear_copies(p,c,record,collected=True)['status']=='CLEARED'
    assert all(len(v.removed)==1 for v in volumes.values())
    private_records.check_tree(record)


def test_cleanup_reconciles_lost_ack_without_deleting_again(copies):
    p,c,record,volumes=copies;volumes['vo-data'].fail=True
    with pytest.raises(TimeoutError):modal_cleanup.clear_copies(p,c,record,collected=True)
    assert (record/'intent.json').exists() and not (record/'COMPLETE.json').exists()
    assert modal_cleanup.clear_copies(p,c,record,collected=True)['status']=='CLEARED'
    assert volumes['vo-data'].removed==['/original']


@pytest.mark.parametrize('damage',['local','remote','extra','missing'])
def test_any_unexplained_binding_change_prevents_first_removal(copies,damage):
    p,c,record,volumes=copies
    if damage=='local':private_records.write_bytes(Path(c['local_assets']['data'])/'original',b'changed!')
    elif damage=='remote':volumes['vo-data'].files['original']=b'changed!'
    elif damage=='extra':volumes['vo-data'].files['extra']=b'wrong'
    else:del volumes['vo-data'].files['original']
    with pytest.raises(ValueError):modal_cleanup.clear_copies(p,c,record,collected=True)
    assert all(not v.removed for v in volumes.values())


def test_retention_deadline_runs_same_bound_cleanup(copies):
    p,c,record,volumes=copies
    assert modal_cleanup.clear_copies(p,c,record,now=datetime(2100,1,1,tzinfo=timezone.utc))['status']=='CLEARED'
    assert read(record/'intent.json')['reason']=='ASSET_RETENTION_EXPIRED'


def test_asset_envelope_covers_maximum_allowed_input_and_output_sizes():
    data={str(i):{'bytes':64*1024**2,'sha256':'a'*64} for i in range(32)}
    wheels={str(i):{'bytes':64*1024**2,'sha256':'b'*64} for i in range(4)}
    result=asset_estimate(data,wheels)
    assert result['maximum_stored_bytes']==int(2.5*1024**3)
    assert result['storage_micro_usd']==249108 and result['output_transfer_micro_usd']==10000
    assert result['registry_and_other_headroom_micro_usd']==740892
