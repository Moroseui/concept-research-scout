"""Synthetic CPU tests; no GPU, provider, model, or patient data used."""
import json
from pathlib import Path
import pytest
from orchestrator import modal_nnunet as native
from orchestrator.modal_fit_progress import FitProgress


def binding(**updates):
    value = dict(run_id='run', arm='A1', fold=0, realization='one',
                 spec_sha256='a'*64, code_sha256='b'*64, input_contract_sha256='c'*64,
                 environment_sha256='d'*64, plans_sha256='e'*64)
    return {**value, **updates}


def store(tmp_path, **kw):
    tmp_path.chmod(0o700)
    return FitProgress(tmp_path, 'fit', binding(**kw), commit=lambda _: None)


class SyntheticTrainer:
    """Only the native checkpoint epoch convention is simulated here."""
    def __init__(self, fail_at=None):
        self.is_ddp=False; self.local_rank=0; self.disable_checkpointing=False
        self.num_epochs=5; self.current_epoch=0; self.fail_at=fail_at
        self.weights=0; self.optimizer=0; self.loaded=None; self.validated=False
        self.initialized=False
    def initialize(self): self.initialized=True
    def save_checkpoint(self, path):
        Path(path).write_text(json.dumps({'current_epoch':self.current_epoch+1,
                                         'weights':self.weights,'optimizer':self.optimizer}))
    def load_checkpoint(self, path):
        state=json.loads(Path(path).read_text());self.loaded=state
        self.current_epoch=state['current_epoch'];self.weights=state['weights'];self.optimizer=state['optimizer']
    def run_training(self):
        for epoch in range(self.current_epoch,self.num_epochs):
            self.current_epoch=epoch;self.weights+=1;self.optimizer+=2
            if (epoch+1)%self.save_every==0 and epoch!=self.num_epochs-1:
                self.save_checkpoint('checkpoint_latest.pth')
            if epoch+1==self.fail_at: raise RuntimeError('synthetic interruption')
        self.save_checkpoint('checkpoint_final.pth');self.current_epoch+=1
    def perform_actual_validation(self, npz): self.validated=True


def make_trainer(progress, **kwargs):
    from orchestrator import private_records
    result=SyntheticTrainer(**kwargs)
    folder=progress.root/'work'
    private_records.mkdir(folder,parents=True,exist_ok=True)
    index=len(list(folder.glob('training_log_*.txt')))+1
    log=folder/('training_log_2026_10_6_00_00_'+str(index)+'.txt')
    private_records.write_bytes(log,b'synthetic native trainer startup\n')
    result.log_file=str(log)
    return result


@pytest.fixture
def synthetic_native(monkeypatch):
    # Packaging/source verification is tested separately. This test does not
    # claim the real nnU-Net, CUDA, or Volume commit has been exercised.
    monkeypatch.setattr(native,'verify_native_source',lambda:None)


def test_interrupted_fit_resumes_optimizer_and_epoch_same_realization(tmp_path,synthetic_native):
    p=store(tmp_path)
    with p.writer(initial=True):
        first=make_trainer(p,fail_at=2)
        with pytest.raises(RuntimeError,match='synthetic interruption'):
            native.run_fit(first,p,initial=True,save_every=1,segment=1)
    identity=(p.root/'identity.json').read_bytes()
    second=make_trainer(p)
    with p.writer(initial=False):
        result=native.run_fit(second,p,initial=False,save_every=1,segment=2,interruption={'at_utc':'synthetic'})
    assert result['mode']=='resume' and result['epoch_resumed_from']==2
    assert second.loaded=={'current_epoch':2,'weights':2,'optimizer':4}
    assert second.weights==5 and second.optimizer==10 and second.validated
    assert (p.root/'identity.json').read_bytes()==identity
    third=make_trainer(p)
    with p.writer(initial=False):
        result=native.run_fit(third,p,initial=False,save_every=1,segment=3)
    assert result['mode']=='validation-only' and third.weights==5 and third.validated
    assert len(list((p.root/'receipts').glob('*.json')))==5


def test_interruption_before_first_epoch_retains_initial_state(tmp_path,synthetic_native):
    p=store(tmp_path)
    with p.writer(initial=True):
        trainer=make_trainer(p)
        def fail():raise RuntimeError('before epoch')
        trainer.run_training=fail
        with pytest.raises(RuntimeError,match='before epoch'):
            native.run_fit(trainer,p,initial=True,save_every=5,segment=1)
    with p.writer(initial=False):
        _,record=p.select('latest')
        assert record['metadata']['next_epoch']==0


def test_missing_resume_never_initializes_trainer(tmp_path,synthetic_native):
    p=store(tmp_path)
    with p.writer(initial=True):pass
    t=make_trainer(p)
    with p.writer(initial=False),pytest.raises(ValueError,match='FIT_PROGRESS_MISSING'):
        native.run_fit(t,p,initial=False,save_every=5,segment=2)
    assert not t.initialized and t.weights==0


def test_interrupted_write_keeps_previous_verified_progress(tmp_path):
    p=store(tmp_path)
    with p.writer(initial=True):
        old=p.publish('preprocessed',lambda q:q.write_bytes(b'complete synthetic unit'),metadata={'unit':1})
        def fail(q):q.write_bytes(b'partial');raise RuntimeError('interrupted')
        with pytest.raises(RuntimeError,match='interrupted'):p.publish('preprocessed',fail,metadata={'unit':2})
        q,record=p.select('preprocessed')
        assert record==old and q.read_bytes()==b'complete synthetic unit'
        assert len(list((p.root/'objects').iterdir()))==2 # Failed evidence retained.


def test_commit_before_pointer_and_error_stops(tmp_path):
    p=store(tmp_path)
    with p.writer(initial=True):
        old=p.publish('score',lambda q:q.write_bytes(b'old'),metadata={})
        def fail(_):raise RuntimeError('commit unavailable')
        p.commit=fail
        with pytest.raises(RuntimeError,match='commit unavailable'):
            p.publish('score',lambda q:q.write_bytes(b'new'),metadata={})
        assert p.select('score')[1]==old


@pytest.mark.parametrize('field,value',[('environment_sha256','f'*64),('plans_sha256','f'*64),('fold',1),('realization','two')])
def test_binding_change_refuses_resume(tmp_path,field,value):
    p=store(tmp_path)
    with p.writer(initial=True):pass
    other=store(tmp_path,**{field:value})
    with pytest.raises(ValueError,match='FIT_IDENTITY_CHANGED'):
        with other.writer(initial=False):pass


def test_no_duplicate_writer_or_initialization(tmp_path):
    p=store(tmp_path);other=store(tmp_path)
    with p.writer(initial=True):
        with pytest.raises(ValueError,match='FIT_WRITER_ACTIVE'):
            with other.writer(initial=False):pass
        with pytest.raises(FileExistsError):
            with other.writer(initial=True):pass


def test_altered_checkpoint_and_world_readable_object_refused(tmp_path):
    p=store(tmp_path)
    with p.writer(initial=True):
        p.publish('latest',lambda q:q.write_bytes(b'original'),metadata={})
        q,_=p.select('latest');q.write_bytes(b'changed')
        with pytest.raises(ValueError,match='FIT_PROGRESS_HASH_CHANGED'):p.select('latest')
        def unsafe(q):q.write_bytes(b'synthetic');q.chmod(0o644)
        with pytest.raises(ValueError,match='PRIVATE_RECORD_PERMISSIONS'):
            p.publish('unsafe',unsafe,metadata={})


def test_checkpoint_interval_and_native_gate(tmp_path,monkeypatch):
    p=store(tmp_path)
    def refuse():raise ValueError('NNUNET_NATIVE_SOURCE_CHANGED')
    monkeypatch.setattr(native,'verify_native_source',refuse)
    with p.writer(initial=True),pytest.raises(ValueError,match='NNUNET_NATIVE_SOURCE_CHANGED'):
        native.run_fit(make_trainer(p),p,initial=True,save_every=1,segment=1)
    assert not list((p.root/'objects').iterdir())


def test_invalid_final_or_epoch_is_not_validation_approval(tmp_path,synthetic_native):
    p=store(tmp_path)
    with p.writer(initial=True):
        p.publish('final',lambda q:q.write_text('{}'),
                  metadata={'next_epoch':4,'total_epochs':5,'native_version':'2.8.1'})
    t=make_trainer(p)
    with p.writer(initial=False),pytest.raises(ValueError,match='NNUNET_RESUME_METADATA'):
        native.run_fit(t,p,initial=False,save_every=5,segment=2)
    assert not t.validated and t.loaded is None


def test_pointer_commit_failure_is_not_reported_as_success(tmp_path):
    p=store(tmp_path)
    with p.writer(initial=True):
        calls=[]
        def commit(_):
            calls.append(1)
            if len(calls)==2:raise RuntimeError('pointer commit failed')
        p.commit=commit
        with pytest.raises(RuntimeError,match='pointer commit failed'):
            p.publish('latest',lambda q:q.write_bytes(b'checkpoint'),metadata={})
        assert len(calls)==2
        assert not list((p.root/'receipts').iterdir())


def test_symlink_and_unlocked_writes_refused(tmp_path):
    p=store(tmp_path)
    with pytest.raises(ValueError,match='FIT_WRITER_LOCK_REQUIRED'):
        p.publish('latest',lambda q:q.write_bytes(b'no'),metadata={})
    with p.writer(initial=True):
        p.publish('latest',lambda q:q.write_bytes(b'original'),metadata={})
        data,_=p.select('latest');data.unlink();data.symlink_to(tmp_path/'elsewhere')
        with pytest.raises(ValueError,match='PRIVATE_RECORD_SYMLINK'):p.select('latest')


def test_native_mountpoint_commit_uses_available_python_and_refuses_missing_or_alias(tmp_path):
    import subprocess
    from orchestrator.modal_fit_progress import volume_commit
    volume_commit(tmp_path)  # Actual child and fsync, no mocked system call.
    with pytest.raises(subprocess.CalledProcessError):
        volume_commit(tmp_path/'missing')
    alias=tmp_path/'alias';alias.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(subprocess.CalledProcessError):
        volume_commit(alias)


def test_mountpoint_commit_keeps_timeout_and_failure(monkeypatch,tmp_path):
    import subprocess,sys
    from orchestrator import modal_fit_progress as progress
    observed=[]
    def stuck(args,**kwargs):
        observed.append((args,kwargs))
        raise subprocess.TimeoutExpired(args,kwargs['timeout'])
    monkeypatch.setattr(progress.subprocess,'run',stuck)
    with pytest.raises(subprocess.TimeoutExpired):progress.volume_commit(tmp_path)
    args,kwargs=observed[0]
    assert args[:4]==[sys.executable,'-I','-B','-c'] and args[-1]==str(tmp_path)
    assert 'os.fsync(fd)' in args[4]
    assert kwargs=={'check':True,'timeout':120}
