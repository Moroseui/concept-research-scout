"""Actual provider/progress connection on synthetic data; no Modal calls."""
import copy
import json
from pathlib import Path
import pytest
from test_modal_fit_result import connection
from test_modal_item4_provider import candidate
from orchestrator import private_records
from orchestrator.modal_fit_health import native_progress, assess

LOG = (b'2026-10-06 06:00:00.000001: Epoch 0 \n'
       b'2026-10-06 06:02:00: Epoch time: 120.0 s \n')


@pytest.fixture
def health(connection):
    progress,binding,outputs,provider,sandbox,commits=connection
    # This is synthetic fixture state, not an installed or preserved record.
    (progress.root/'final.json').unlink()
    with progress.writer(initial=False):
        progress.publish('latest',lambda p:p.write_bytes(b'synthetic epoch zero checkpoint'),
                         metadata={'next_epoch':0,'total_epochs':5,'native_version':'2.8.1'})
    log=progress.root/'work/dataset/trainer/fold_0/training_log_2026_10_6_06_00_00.txt'
    private_records.mkdir(log.parent,parents=True)
    private_records.write_bytes(log,LOG)
    sandbox.poll=lambda:None
    path='/'+str(log.relative_to(progress.mount))
    return progress,binding,provider,sandbox,commits,log,path


def observe(health,t=1000):
    _,binding,provider,_,_,_,path=health
    return provider.fit_health('sb-fit',binding,path,now=t)


def test_actual_provider_reader_uses_native_log_and_small_committed_records_without_writes(health):
    progress,_,_,_,commits,_,_=health;before=list(commits)
    value=observe(health)
    assert value['status']=='RUNNING' and value['log']['epoch_completed']==0
    assert value['log']['recent_epoch_seconds']==[120]
    assert value['checkpoint']['next_epoch']==0 and not value['checkpoint']['payload_verified']
    assert value['may_launch'] is False and commits==before
    # Monitoring reads metadata only. Full checkpoint bytes are verified at resume.
    record=json.loads((progress.root/'latest.json').read_bytes())
    (progress.root/'objects'/record['object']/'data').write_bytes(b'payload not read on every poll')
    assert observe(health)['checkpoint']['record_sha256']==value['checkpoint']['record_sha256']


def test_stall_requires_two_late_successful_observations_and_never_launches(health):
    first=assess(observe(health,1000))
    assert first['action']=='OBSERVE'
    boundary=assess(observe(health,1900),first['state']);assert boundary['action']=='OBSERVE'
    late=assess(observe(health,1901),boundary['state']);assert late['action']=='OBSERVE'
    again=assess(observe(health,1961),late['state'])
    assert again['action']=='RECHECK_BEFORE_STOP' and again['may_launch'] is False
    assert again['idle_seconds']==961 and again['threshold_seconds']==900


@pytest.mark.parametrize('signal',['epoch','checkpoint'])
def test_either_real_progress_signal_cancels_candidate_stop(health,signal):
    progress,_,_,_,_,log,_=health
    prior=assess(observe(health,1000))['state']
    prior=assess(observe(health,1901),prior)['state']
    if signal=='epoch':
        with log.open('ab') as f:f.write(b'2026-10-06 06:02:01: Epoch 1 \n')
    else:
        with progress.writer(initial=False):
            progress.publish('latest',lambda p:p.write_bytes(b'next synthetic checkpoint'),
                             metadata={'next_epoch':1,'total_epochs':5,'native_version':'2.8.1'})
    result=assess(observe(health,1961),prior)
    assert result['action']=='OBSERVE' and result['idle_seconds']==0
    assert result['state']['overdue_observations']==0


def test_unrelated_log_chatter_does_not_hide_stall(health):
    *_,log,path=health
    prior=assess(observe(health,1000))['state']
    prior=assess(observe(health,1901),prior)['state']
    with log.open('ab') as f:f.write(b'2026-10-06 06:19:00: repeated ordinary notice \n')
    assert assess(observe(health,1961),prior)['action']=='RECHECK_BEFORE_STOP'


def test_slow_observed_epoch_has_generous_threshold(health):
    *_,log,path=health;log.write_bytes(LOG.replace(b'120.0',b'500.0'))
    prior=assess(observe(health,1000))['state']
    result=assess(observe(health,3400),prior)
    assert result['action']=='OBSERVE' and result['threshold_seconds']==2500


@pytest.mark.parametrize('phase',['startup','scoring'])
def test_epoch_stall_rule_does_not_kill_nontraining_phase(health,phase):
    *_,log,path=health
    log.write_bytes(b'initializing\n' if phase=='startup' else LOG+b'2026-10-06 06:03:00: Training done. \n')
    first=assess(observe(health,1000))
    last=assess(observe(health,50000),first['state'])
    assert last['action']==('OBSERVE_STARTUP' if phase=='startup' else 'OBSERVE_SCORING')
    assert last['may_launch'] is False


@pytest.mark.parametrize('cause',['network','log-missing','checkpoint-missing','wrong-volume','wrong-job','wrong-identity'])
def test_missing_or_untrusted_observation_never_becomes_stall(health,cause):
    progress,binding,provider,sandbox,_,log,_=health
    if cause=='network':
        def fail():raise TimeoutError('synthetic unavailable observation')
        sandbox.poll=fail
    elif cause=='log-missing':log.unlink()
    elif cause=='checkpoint-missing':(progress.root/'latest.json').unlink()
    elif cause=='wrong-volume':provider.modal.Volume.from_name(binding['progress']['volume_name'],version=2,create_if_missing=False).object_id='vo-other'
    elif cause=='wrong-job':sandbox.object_id='sb-other'
    else:(progress.root/'identity.json').write_bytes(b'{}')
    with pytest.raises((ValueError,TimeoutError)):observe(health)


@pytest.mark.parametrize('path',['/other/training_log_1.txt','/fits/fit/work/../secret',
                                '/fits/fit/work/saved-predictions.npz','/fits/other/work/training_log_1.txt'])
def test_reader_refuses_anything_outside_selected_fit_native_log(health,path):
    _,binding,provider,*_=health
    with pytest.raises(ValueError,match='^FIT_HEALTH_LOG_PATH$'):
        provider.fit_health('sb-fit',binding,path)


def test_terminal_status_is_not_completion_or_resume_authority(health):
    _,_,_,sandbox,*_=health;sandbox.poll=lambda:137
    value=observe(health)
    assert value['status']=='TERMINAL' and value['terminal_exit_code']==137
    assert assess(value)=={'action':'RECONCILE_TERMINAL','may_launch':False}


def test_partial_lines_are_not_completed_epoch_evidence():
    assert native_progress(LOG.rstrip(b'\n'))['epoch_completed'] is None
    with pytest.raises(ValueError,match='^FIT_HEALTH_EPOCH_ORDER$'):native_progress(LOG+LOG)
    with pytest.raises(ValueError,match='^FIT_HEALTH_EPOCH_DURATION$'):
        native_progress(b'2026-10-06 06:02:00: Epoch time: 120.0 s \n')


@pytest.mark.parametrize('change',['job','binding','clock','path'])
def test_prior_health_state_cannot_be_reused_for_another_segment_or_clock(health,change):
    prior=assess(observe(health,1000))['state'];value=observe(health,1060)
    if change=='job':value['provider_id']='sb-other'
    elif change=='binding':value['binding_sha256']='0'*64
    elif change=='clock':value['observed_at']=999
    else:value['log']['path']+='.new'
    with pytest.raises(ValueError,match='^FIT_HEALTH_HISTORY_BINDING$'):assess(value,prior)


def test_native_registered_log_is_consumed_without_a_controller_path(health):
    progress,binding,provider,_,commits,log,path=health
    before=list(commits)
    with progress.writer(initial=False):
        registration=progress.training_log(log,segment=1)
    assert len(commits)==len(before)+1
    result=provider.fit_health('sb-fit',binding,now=1000)
    assert result['log']['path']==path and result['log']['epoch_completed']==0
    assert result['log_registration_sha256']
    assert registration['binding_sha256']==progress.binding_sha256
    assert assess(result)['action']=='OBSERVE'


@pytest.mark.parametrize('change',['segment','binding','path','ambiguous-segment'])
def test_registered_log_cannot_select_another_fit_or_segment(health,change):
    progress,binding,provider,_,_,log,_=health
    with progress.writer(initial=False):progress.training_log(log,segment=1)
    path=progress.root/'training-log-1.json';value=json.loads(path.read_bytes())
    if change=='segment':value['segment']=2
    elif change=='binding':value['binding_sha256']='0'*64
    elif change=='ambiguous-segment':value['segment']=True
    else:value['path']='/fits/another/work/training_log_1.txt'
    private_records.write_bytes(path,json.dumps(value).encode())
    with pytest.raises(ValueError,match='^FIT_HEALTH_LOG_(BINDING|PATH)$'):
        provider.fit_health('sb-fit',binding,now=1000)


def test_missing_log_registration_is_startup_not_stall(health):
    _,binding,provider,*_=health
    result=provider.fit_health('sb-fit',binding,now=999999)
    assert result['status']=='STARTING'
    assert assess(result)=={'action':'OBSERVE_STARTUP','may_launch':False}


def test_each_resume_has_its_own_immutable_native_log_registration(health):
    progress,binding,provider,_,_,log,path=health
    with progress.writer(initial=False):progress.training_log(log,segment=1)
    second=copy.deepcopy(binding);second['experiment']['segment']=2
    assert provider.fit_health('sb-fit',second,now=1000)['status']=='STARTING'
    next_log=log.with_name('training_log_2026_10_6_07_00_00.txt')
    private_records.write_bytes(next_log,LOG)
    with progress.writer(initial=False):
        progress.training_log(next_log,segment=2)
        with pytest.raises(FileExistsError):progress.training_log(next_log,segment=2)
    assert provider.fit_health('sb-fit',binding,now=1000)['log']['path']==path
    assert provider.fit_health('sb-fit',second,now=1000)['log']['path'].endswith(next_log.name)


@pytest.mark.parametrize('change',['outside','alias','permissions','unlocked','bad-segment'])
def test_log_producer_refuses_untrusted_paths_and_unlocked_registration(health,change,tmp_path):
    progress,_,_,_,commits,log,_=health
    before=list(commits)
    if change=='outside':
        log=tmp_path/'training_log_1.txt';private_records.write_bytes(log,b'synthetic')
    elif change=='alias':
        alias=log.parent/'training_log_2.txt';alias.symlink_to(log);log=alias
    elif change=='permissions':log.chmod(0o644)
    if change=='unlocked':
        with pytest.raises(ValueError,match='^FIT_WRITER_LOCK_REQUIRED$'):progress.training_log(log,segment=1)
    else:
        with progress.writer(initial=False):
            with pytest.raises(ValueError):progress.training_log(log,segment=True if change=='bad-segment' else 1)
    assert not (progress.root/'training-log-1.json').exists()
    assert commits==before
