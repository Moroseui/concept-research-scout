"""Actual producer/provider connection; synthetic filesystem/SDK, no paid work."""
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import private_records
from orchestrator.modal_fit_progress import FitProgress, encoded
from orchestrator.modal_fit_result import publish, _key, _result_key
from orchestrator.modal_provider import ModalProvider
from orchestrator.modal_item4_provider import guard_payload
from orchestrator import modal_input_guard
from test_modal_item4_provider import candidate


class Volume:
    object_id='vo-progress'
    def __init__(self,mount):self.mount=mount
    def hydrate(self,**kwargs):pass
    def listdir(self,path,recursive=False):
        p=self.mount/path.lstrip('/')
        paths=[p] if p.is_file() else list(p.iterdir()) if p.is_dir() else []
        return [NS(path=str(x.relative_to(self.mount)),size=x.stat().st_size,
                   type=NS(name='FILE' if x.is_file() else 'DIRECTORY')) for x in paths]
    def read_file(self,path):
        with (self.mount/path.lstrip('/')).open('rb') as f:
            for chunk in iter(lambda:f.read(17),b''):yield chunk


def proof_fixture(provider,binding,mount):
    # Synthetic verification record for the provider consumer fixture. Native
    # hashing-before-exec is exercised separately by test_modal_input_guard.
    payload=guard_payload(provider,binding)
    proof={'schema':'modal-input-verification/v1', **{k:payload[k] for k in
        ('binding_sha256','guard_sha256','preprocessing_sha256')},
        'inventory_sha256':hashlib.sha256(modal_input_guard.canonical(payload['files'])).hexdigest(),
        'file_count':len(payload['files']),'total_bytes':sum(x['bytes'] for x in payload['files'].values()),
        'status':'VERIFIED','reason':None,'volume_ids':payload['volume_ids']}
    path=modal_input_guard.proof_path(mount,payload['binding_sha256'])
    private_records.write_bytes(path,modal_input_guard.canonical(proof))
    return path


@pytest.fixture
def connection(tmp_path,candidate):
    mount=tmp_path/'volume';private_records.mkdir(mount)
    outputs=tmp_path/'outputs';private_records.mkdir(outputs)
    for name,raw in {'result.csv':b'mean\n0.25\n','summary.json':b'{"synthetic":true}\n'}.items():
        private_records.write_bytes(outputs/name,raw)
    _,config,binding,*_=candidate
    binding['experiment']['segment']=1
    binding['outputs']=['result.csv','summary.json']
    fit=binding['progress']['fit_binding']
    commits=[];progress=FitProgress(mount,'fit',fit,commit=lambda path:commits.append(str(path)))
    with progress.writer(initial=True):
        progress.publish('final',lambda path:path.write_bytes(b'synthetic native final checkpoint'),
                         metadata={'next_epoch':5,'total_epochs':5,'native_version':'2.8.1'})
    volume=Volume(mount);sandbox=NS(object_id='sb-fit',poll=lambda:0)
    def lookup(name,**kwargs):
        assert name=='progress' and kwargs['version']==2 and kwargs['create_if_missing'] is False
        return volume
    provider=object.__new__(ModalProvider)
    provider.config=config;provider.client='synthetic';provider.modal=NS(Volume=NS(from_name=lookup));provider._sandbox=lambda ident:sandbox
    proof_fixture(provider,binding,mount)
    return progress,binding,outputs,provider,sandbox,commits


def test_actual_worker_producer_to_provider_collect_after_sandbox_ended(connection,tmp_path):
    progress,binding,outputs,provider,sandbox,commits=connection
    with progress.writer(initial=False):result=publish(progress,binding,outputs)
    assert provider.status('sb-fit',binding)['status']=='COMPLETE'
    # No sandbox filesystem capability exists: collection must use the Volume.
    receipt=provider.collect('sb-fit',binding,tmp_path/'collected')
    for name in binding['outputs']:
        assert (tmp_path/'collected'/name).read_bytes()==(outputs/name).read_bytes()
        assert receipt['file_sha256'][name]==hashlib.sha256((outputs/name).read_bytes()).hexdigest()
        assert (tmp_path/'collected'/name).stat().st_mode&0o077==0
    before=list(commits)
    assert provider.status('sb-fit',binding)['status']=='COMPLETE'
    assert commits==before
    with progress.writer(initial=False),pytest.raises(ValueError,match='^MODAL_FIT_RESULT_ALREADY_PUBLISHED$'):
        publish(progress,binding,outputs)


@pytest.mark.parametrize('running',[True,False])
def test_missing_result_is_never_claimed_as_success(connection,running):
    _,binding,_,provider,sandbox,_=connection;sandbox.poll=lambda:None if running else 137
    assert provider.status('sb-fit',binding)['status']==('RUNNING' if running else 'UNKNOWN')


def test_one_failed_segment_cannot_poison_or_approve_another(connection):
    progress,binding,outputs,provider,_,_=connection
    with progress.writer(initial=False):publish(progress,binding,None,status='FAILED')
    assert provider.status('sb-fit',binding)['status']=='FAILED'
    successor=copy.deepcopy(binding);successor['experiment']['segment']=2
    assert provider.status('sb-fit',successor)['status']=='UNKNOWN'
    proof_fixture(provider,successor,progress.mount)
    with progress.writer(initial=False):publish(progress,successor,outputs)
    assert provider.status('sb-fit',successor)['status']=='COMPLETE'
    assert provider.status('sb-fit',binding)['status']=='FAILED'


@pytest.mark.parametrize('cause',['bytes','metadata','pointer','identity','volume','binding'])
def test_changed_persistent_evidence_refuses(connection,tmp_path,cause):
    progress,binding,outputs,provider,_,_=connection
    with progress.writer(initial=False):publish(progress,binding,outputs)
    pointer=progress.root/(_key('result.csv')+'.json');rec=json.loads(pointer.read_bytes())
    folder=progress.root/'objects'/rec['object']
    if cause=='bytes':(folder/'data').write_bytes(b'changed')
    if cause=='metadata':
        rec['metadata']['path']='other.csv';pointer.write_bytes(encoded(rec));(folder/'record.json').write_bytes(encoded(rec))
    if cause=='pointer':
        rec['object']='b'*32;pointer.write_bytes(encoded(rec))
    if cause=='identity':(progress.root/'identity.json').write_bytes(b'{}')
    if cause=='volume':provider.modal.Volume.from_name('progress',version=2,create_if_missing=False).object_id='vo-other'
    if cause=='binding':binding['spec_sha256']='f'*64
    with pytest.raises(ValueError):provider.collect('sb-fit',binding,tmp_path/'no-success')


def test_partly_published_return_reuses_only_identical_completed_objects(connection):
    progress,binding,outputs,provider,_,_=connection
    name='result.csv';raw=(outputs/name).read_bytes()
    with progress.writer(initial=False):
        record=progress.publish(_key(name),lambda path:path.write_bytes(raw),metadata={'path':name})
    assert provider.status('sb-fit',binding)['status']=='UNKNOWN'
    with progress.writer(initial=False):publish(progress,binding,outputs)
    assert json.loads((progress.root/(_key(name)+'.json')).read_bytes())==record
    assert provider.status('sb-fit',binding)['status']=='COMPLETE'


def test_changed_file_after_partial_publication_is_not_overwritten(connection):
    progress,binding,outputs,_,_,_=connection
    with progress.writer(initial=False):
        record=progress.publish(_key('result.csv'),lambda path:path.write_bytes(b'original'),metadata={'path':'result.csv'})
        with pytest.raises(ValueError,match='^MODAL_FIT_OUTPUT_CHANGED$'):publish(progress,binding,outputs)
    assert json.loads((progress.root/(_key('result.csv')+'.json')).read_bytes())==record
    assert not (progress.root/(_result_key(binding)+'.json')).exists()


@pytest.mark.parametrize('cause',['extra','missing','no_final','alias'])
def test_invalid_producer_input_never_publishes_result(connection,cause):
    progress,binding,outputs,_,_,_=connection
    if cause=='extra':private_records.write_bytes(outputs/'extra.txt',b'not declared')
    if cause=='missing':(outputs/'result.csv').unlink()
    if cause=='no_final':(progress.root/'final.json').unlink()
    if cause=='alias':
        (outputs/'result.csv').unlink();(outputs/'result.csv').symlink_to(outputs/'summary.json')
    with progress.writer(initial=False),pytest.raises(ValueError):publish(progress,binding,outputs)
    assert not (progress.root/(_result_key(binding)+'.json')).exists()


def test_incomplete_final_checkpoint_cannot_publish_complete_tables(connection):
    progress,binding,outputs,_,_,_=connection
    with progress.writer(initial=False):
        progress.publish('final',lambda path:path.write_bytes(b'incomplete synthetic checkpoint'),
                         metadata={'next_epoch':2,'total_epochs':5,'native_version':'2.8.1'})
        with pytest.raises(ValueError,match='^MODAL_FIT_FINAL_NOT_COMPLETE$'):publish(progress,binding,outputs)
    assert not (progress.root/(_result_key(binding)+'.json')).exists()


@pytest.mark.parametrize('damage',['missing','inventory','guard','preprocessing','binding','status','extra'])
def test_input_verification_is_required_for_complete_result(connection,tmp_path,damage):
    progress,binding,outputs,provider,_,_=connection
    with progress.writer(initial=False):publish(progress,binding,outputs)
    payload=guard_payload(provider,binding)
    path=modal_input_guard.proof_path(progress.mount,payload['binding_sha256'])
    if damage=='missing':path.unlink()
    else:
        proof=json.loads(path.read_bytes())
        key={'inventory':'inventory_sha256','guard':'guard_sha256','preprocessing':'preprocessing_sha256',
             'binding':'binding_sha256','status':'status','extra':'extra'}[damage]
        proof[key]='changed';private_records.write_bytes(path,modal_input_guard.canonical(proof))
    with pytest.raises(ValueError,match='^ITEM4_INPUT_VERIFICATION_(REQUIRED|BINDING)$'):
        provider.collect('sb-fit',binding,tmp_path/'not-collected')
    assert not (tmp_path/'not-collected').exists()


def test_genuine_guard_failure_is_failed_not_an_uncertain_running_fit(connection):
    progress,binding,_,provider,_,_=connection
    payload=guard_payload(provider,binding)
    path=modal_input_guard.proof_path(progress.mount,payload['binding_sha256'])
    proof=json.loads(path.read_bytes());proof.update(status='FAILED',reason='INPUT_GUARD_HASH')
    private_records.write_bytes(path,modal_input_guard.canonical(proof))
    assert provider.status('sb-fit',binding)['status']=='FAILED'
