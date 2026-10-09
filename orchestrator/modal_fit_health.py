"""External, read-only native progress observation; never admission or restart.

Uses existing nnU-Net logs and committed checkpoint metadata, not a heartbeat.
A stalled result is only a stop candidate: terminal/checkpoint verification and
normal accounting are still mandatory before a same-fit continuation.
"""
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import PurePosixPath
from orchestrator.modal_executor import canonical
from orchestrator.modal_fit_progress import encoded
from orchestrator.modal_fit_provider import progress_scope, progress_volume, _file, MAX_RECORD

MAX_LOG = 8 * 1024 * 1024
STAMP = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?"
EPOCH = re.compile(r"^" + STAMP + r": Epoch (\d+)\s*$")
DURATION = re.compile(r"^" + STAMP + r": Epoch time: ([0-9]+(?:\.[0-9]+)?) s\s*$")


def native_progress(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_LOG:
        raise ValueError('FIT_HEALTH_LOG_BOUND')
    text = raw.decode('utf-8')
    epoch = None; completed = None; durations = []; done = False
    # A partial final line is not evidence of completed progress.
    for line in text.splitlines(keepends=True):
        if not line.endswith('\n'): continue
        line = line.rstrip('\r\n')
        start = EPOCH.fullmatch(line)
        finish = DURATION.fullmatch(line)
        if start:
            value = int(start[1])
            if epoch is not None and value <= epoch:
                raise ValueError('FIT_HEALTH_EPOCH_ORDER')
            epoch = value
        elif finish:
            seconds = float(finish[1])
            if epoch is None or completed == epoch or not math.isfinite(seconds) or seconds <= 0:
                raise ValueError('FIT_HEALTH_EPOCH_DURATION')
            completed = epoch; durations.append(seconds)
        elif re.fullmatch(STAMP + r": Training done\.\s*", line):
            done = True
    return {'epoch_started':epoch, 'epoch_completed':completed,
            'recent_epoch_seconds':durations[-10:], 'training_done':done}


def _checkpoint(volume, root, fit_hash):
    names = {e.path.lstrip('/') for e in volume.listdir(root, recursive=False) if e.type.name == 'FILE'}
    key = 'final' if (root+'/final.json').lstrip('/') in names else 'latest'
    pointer = _file(volume, root+'/'+key+'.json', MAX_RECORD, collect=True)
    record = json.loads(pointer['data'])
    fields = {'schema','key','binding_sha256','object','sha256','bytes','metadata','at_utc'}
    if (not isinstance(record,dict) or set(record)!=fields or record['schema']!='modal-fit-object/v1'
            or record['key']!=key or record['binding_sha256']!=fit_hash
            or not isinstance(record['object'],str) or not re.fullmatch('[0-9a-f]{32}',record['object'])
            or not isinstance(record['sha256'],str) or not re.fullmatch('[0-9a-f]{64}',record['sha256'])
            or type(record['bytes']) is not int or record['bytes']<=0):
        raise ValueError('FIT_HEALTH_CHECKPOINT_BINDING')
    original = _file(volume,root+'/objects/'+record['object']+'/record.json',MAX_RECORD,collect=True)
    if json.loads(original['data']) != record:
        raise ValueError('FIT_HEALTH_CHECKPOINT_CHANGED')
    meta=record['metadata']
    if (not isinstance(meta,dict) or set(meta)!={'next_epoch','total_epochs','native_version'}
            or any(type(meta[k]) is not int for k in ('next_epoch','total_epochs'))
            or not 0 <= meta['next_epoch'] <= meta['total_epochs'] or meta['total_epochs'] < 1
            or meta['native_version']!='2.8.1'
            or (key=='final' and meta['next_epoch']!=meta['total_epochs'])):
        raise ValueError('FIT_HEALTH_CHECKPOINT_METADATA')
    timestamp=datetime.fromisoformat(record['at_utc'])
    if timestamp.tzinfo is None:raise ValueError('FIT_HEALTH_CHECKPOINT_TIME')
    if _file(volume,root+'/'+key+'.json',MAX_RECORD,collect=True)['data']!=pointer['data']:
        raise ValueError('FIT_HEALTH_OBSERVATION_CHANGED')
    return {'key':key,'next_epoch':meta['next_epoch'],'total_epochs':meta['total_epochs'],
            'record_sha256':original['sha256'],'at_utc':record['at_utc'],
            'checkpoint_sha256':record['sha256'],'payload_verified':False}


def observe(provider, provider_id, binding, log_path=None, *, now=None):
    """log_path is the exact native log path learned from this fit's worker.

    Read only one bounded log and small records; do not repeatedly transfer model
    weights. The terminal checkpoint reader verifies payload bytes before resume.
    SDK/network/read errors propagate, never become a stall or successful result.
    """
    scope=progress_scope(binding); sandbox=provider._sandbox(provider_id)
    if sandbox.object_id!=provider_id:raise ValueError('MODAL_FIT_SANDBOX_ID_CHANGED')
    code=sandbox.poll()
    if code is not None and type(code) is not int:raise ValueError('FIT_HEALTH_PROVIDER_STATUS')
    observed = datetime.now(timezone.utc).timestamp() if now is None else now
    if type(observed) not in (int,float) or not math.isfinite(observed) or observed<0:
        raise ValueError('FIT_HEALTH_OBSERVATION_TIME')
    result={'schema':'modal-fit-health/v1','provider_id':provider_id,
            'binding_sha256':hashlib.sha256(canonical(binding)).hexdigest(),
            'observed_at':observed,'status':'RUNNING' if code is None else 'TERMINAL',
            'terminal_exit_code':code,'may_launch':False}
    if code is not None:return result
    root='/fits/'+scope['fit_id']
    volume=progress_volume(provider,scope)
    if log_path is None:
        # Check existing directory metadata first; missing startup records are
        # not a stalled fit. No broad file search or image reads are performed.
        for parent, child in [('/', 'fits'), ('/fits', scope['fit_id'])]:
            entries=volume.listdir(parent,recursive=False)
            matched=[e for e in entries if e.path.lstrip('/')==(parent.rstrip('/')+'/'+child).lstrip('/')]
            if not matched:
                return {**result,'status':'STARTING'}
            if len(matched)!=1 or matched[0].type.name!='DIRECTORY':
                raise ValueError('FIT_HEALTH_LOG_DIRECTORY')
        segment=binding['experiment']['segment']
        if type(segment) is not int or segment<1:raise ValueError('FIT_HEALTH_LOG_SEGMENT')
        record_path=root+'/training-log-'+str(segment)+'.json'
        entries=volume.listdir(root,recursive=False)
        if not any(e.path.lstrip('/')==record_path.lstrip('/') for e in entries):
            return {**result,'status':'STARTING'}
        registration=_file(volume,record_path,MAX_RECORD,collect=True)
        registered=json.loads(registration['data'])
        if (not isinstance(registered,dict) or set(registered)!={'schema','binding_sha256','segment','path'}
                or registered['schema']!='modal-fit-log/v1' or type(registered['segment']) is not int
                or registered['segment']!=segment
                or registered['binding_sha256']!=hashlib.sha256(encoded(scope['fit_binding'])).hexdigest()):
            raise ValueError('FIT_HEALTH_LOG_BINDING')
        log_path=registered['path']
        result['log_registration_sha256']=registration['sha256']
    path=PurePosixPath(log_path) if isinstance(log_path,str) else None
    if (path is None or str(path)!=log_path or '..' in path.parts
            or not path.is_relative_to(root+'/work')
            or not re.fullmatch(r'training_log_[0-9_]+\.txt',path.name)):
        raise ValueError('FIT_HEALTH_LOG_PATH')
    identity=_file(volume,root+'/identity.json',MAX_RECORD,collect=True)
    if json.loads(identity['data'])!={'schema':'modal-fit/v1','binding':scope['fit_binding']}:
        raise ValueError('MODAL_FIT_IDENTITY_CHANGED')
    log=_file(volume,log_path,MAX_LOG,collect=True)
    checkpoint=_checkpoint(volume,root,hashlib.sha256(encoded(scope['fit_binding'])).hexdigest())
    if sandbox.poll() is not None:raise ValueError('FIT_HEALTH_OBSERVATION_CHANGED')
    result.update(log={'path':log_path,'sha256':log['sha256'],'bytes':log['bytes'],
                       **native_progress(log['data'])}, checkpoint=checkpoint)
    return result


def assess(current, previous=None):
    """Persistent controller observation clock; no worker-clock stall inference.

    UNKNOWN reads never call this function. Preserve the prior successful state
    across network failures. A fresh observation baseline cannot trigger a stop.
    The scheduler must reobserve and recheck before executing any stop candidate.
    """
    if current['status']=='STARTING':
        return {'action':'OBSERVE_STARTUP','may_launch':False}
    if current['status']!='RUNNING':
        return {'action':'RECONCILE_TERMINAL','may_launch':False}
    log=current['log']; checkpoint=current['checkpoint']; now=current['observed_at']
    identity=(current['provider_id'],current['binding_sha256'],log['path'])
    marker=(log['epoch_started'],log['epoch_completed'],checkpoint['record_sha256'])
    state={'identity':list(identity),'marker':list(marker),'observed_at':now,
           'last_progress_at':now,'overdue_observations':0}
    if previous is not None:
        if previous['identity']!=list(identity) or now<=previous['observed_at']:
            raise ValueError('FIT_HEALTH_HISTORY_BINDING')
        if previous['marker']==list(marker):state['last_progress_at']=previous['last_progress_at']
    if log['training_done'] or checkpoint['key']=='final':
        return {'action':'OBSERVE_SCORING','state':state,'may_launch':False}
    durations=log['recent_epoch_seconds']
    if not durations:
        return {'action':'OBSERVE_STARTUP','state':state,'may_launch':False}
    threshold=max(900.0,5*max(durations))
    idle=now-state['last_progress_at']
    if previous is not None and idle>threshold:
        state['overdue_observations']=previous['overdue_observations']+1
    action='RECHECK_BEFORE_STOP' if state['overdue_observations']>=2 else 'OBSERVE'
    return {'action':action,'idle_seconds':idle,'threshold_seconds':threshold,
            'state':state,'may_launch':False}
