"""Archived SDK interface is synthetic; original controller integration is separate."""
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace as NS
import pytest
from orchestrator import modal_direct_recovery as recovery


def fixture():
    stamp=datetime(2026,10,6,11,tzinfo=timezone.utc)
    rows=[NS(object_id='sb-original',source='stderr',message=recovery.ERROR,timestamp=stamp)]
    calls=[]
    class Sandbox:
        object_id='sb-original'
        def poll(self): return 2
        @property
        def stdout(self): raise AssertionError('Never use a terminated live stream')
        @property
        def stderr(self): raise AssertionError('Never use a terminated live stream')
    sb=Sandbox()
    def fetch(**kwargs):
        calls.append(kwargs);return iter(rows)
    sb.logs=NS(fetch=fetch)
    provider=NS(_sandbox=lambda ident:sb,_volume=lambda ident:NS(listdir=lambda *a,**k:[]))
    result={'handle':{'provider_id':'sb-original','data_volume_id':'vo-original'}}
    return sb,rows,provider,result,calls


def test_archived_entrypoint_logs_match_exact_original_without_live_streams():
    sb,rows,p,r,calls=fixture()
    # A transport may split one line; reconstruction must preserve exact bytes.
    rows[:]=[NS(**{**vars(rows[0]),'message':part}) for part in (recovery.ERROR[:20],recovery.ERROR[20:])]
    assert recovery.live_empty(p,r) is True
    assert len(calls)==1
    assert calls[0]['since']==datetime(2026,10,6,tzinfo=timezone.utc)
    assert calls[0]['until']>=calls[0]['since']


@pytest.mark.parametrize('fault,code',[
 ('missing','DIRECT_RECOVERY_PROVIDER_PROOF_CHANGED'),
 ('extra-stdout','DIRECT_RECOVERY_PROVIDER_PROOF_CHANGED'),
 ('different-stderr','DIRECT_RECOVERY_PROVIDER_PROOF_CHANGED'),
 ('duplicate','DIRECT_RECOVERY_PROVIDER_PROOF_CHANGED'),
 ('object','DIRECT_RECOVERY_LOG_BINDING'),('source','DIRECT_RECOVERY_LOG_BINDING'),
 ('before-window','DIRECT_RECOVERY_LOG_BINDING'),('naive-time','DIRECT_RECOVERY_LOG_BINDING'),
 ('future','DIRECT_RECOVERY_LOG_BINDING'),('non-text','DIRECT_RECOVERY_LOG_BINDING'),
 ('oversize','DIRECT_RECOVERY_LOG_SIZE'),
 ('active','DIRECT_RECOVERY_PROVIDER_NOT_TERMINAL'),
 ('changed-exit','DIRECT_RECOVERY_PROVIDER_NOT_TERMINAL'),
 ('volume','DIRECT_RECOVERY_ORIGINAL_VOLUME_NOT_EMPTY')])
def test_missing_mixed_changed_or_unproven_evidence_refuses(fault,code):
    sb,rows,p,r,calls=fixture()
    if fault=='missing': rows.clear()
    elif fault=='extra-stdout':rows.append(NS(**{**vars(rows[0]),'source':'stdout','message':'extra'}))
    elif fault=='different-stderr': rows[0].message='different'
    elif fault=='duplicate': rows.append(rows[0])
    elif fault=='object': rows[0].object_id='sb-other'
    elif fault=='source': rows[0].source='unknown'
    elif fault=='before-window': rows[0].timestamp-=timedelta(days=1)
    elif fault=='naive-time': rows[0].timestamp=rows[0].timestamp.replace(tzinfo=None)
    elif fault=='future': rows[0].timestamp=datetime.now(timezone.utc)+timedelta(days=1)
    elif fault=='non-text':rows[0].message=None
    elif fault=='oversize':rows[0].message='x'*(1024*1024+1)
    elif fault=='active':sb.poll=lambda:None
    elif fault=='changed-exit':
        codes=iter([2,None]);sb.poll=lambda:next(codes)
    elif fault=='volume':p._volume=lambda ident:NS(listdir=lambda *a,**k:['unexpected'])
    with pytest.raises(ValueError,match='^'+code+'$'):recovery.live_empty(p,r)


def test_observation_failure_is_not_success_and_does_not_launch():
    sb,rows,p,r,calls=fixture()
    def unavailable(**kw):raise TimeoutError('synthetic transport timeout')
    sb.logs.fetch=unavailable
    with pytest.raises(TimeoutError):recovery.live_empty(p,r)
