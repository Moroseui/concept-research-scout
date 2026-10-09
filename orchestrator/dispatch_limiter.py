"""Repository-wide job-count admission with durable CAS state, not a dollar cap.

Production activation and state-ref write permission are proposed, not granted.
The same Git compare-and-swap is exercised against local disposable repositories.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import stat
from orchestrator.git_diagnostics import run as git_run

REF = 'refs/heads/automation/dispatch-state'
FILE = 'dispatch_state.json'
IDENTITY = ['-c','user.name=Astra (OpenAI agent)','-c','user.email=astra@agents.local.invalid']


def initial():
    return {'version':1,'sequence':0,'day':None,'count':0,'halted':False,
            'events':{},'notifications':{},'resets':[], 'policy_sha256':None}


def validate(state):
    if set(state)!=set(initial()) or state['version']!=1:
        raise ValueError('LIMITER_STATE_SCHEMA')
    if type(state['sequence']) is not int or state['sequence']<0 or type(state['count']) is not int or state['count']<0 or type(state['halted']) is not bool:
        raise ValueError('LIMITER_STATE_VALUES')
    if state['policy_sha256'] is not None and not re.fullmatch('[0-9a-f]{64}',state['policy_sha256']):raise ValueError('LIMITER_POLICY_BINDING')
    if state['day'] is not None and not re.fullmatch(r'\d{4}-\d{2}-\d{2}',state['day']):raise ValueError('LIMITER_DAY')
    if len(state['events'])>10000 or len(json.dumps(state))>1400000:raise ValueError('LIMITER_CAPACITY_REQUIRES_MAINTENANCE')
    for key,v in state['events'].items():
        server=bool(re.fullmatch(r'server:[0-9a-f]{64}:[1-9]\d*',key))
        manual=bool(re.fullmatch(r'manual:[0-9a-f]{64}:[1-8]',key))
        expected={'source','branch','day','count','notification','halted'} | ({'kind'} if server else set())
        if (not server and not manual and not re.fullmatch(r'\d+:\d+',key)) or set(v)!=expected:
            raise ValueError('LIMITER_EVENT_SCHEMA')
        if not re.fullmatch('[0-9a-f]{40}',v['source']) or (not re.fullmatch(r'astra/manual-[a-z0-9-]+',v['branch']) if manual else v['branch'] not in (['astra/infrastructure-milestone-record'] if server else ['main','astra/autonomous-isles-pilot'])) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',v['day']) or type(v['count']) is not int or v['notification'] not in [None,'N','2N','CAP'] or type(v['halted']) is not bool:
            raise ValueError('LIMITER_EVENT_VALUES')
        if server and v['kind'] not in ['astra_turn','nightly_review']:raise ValueError('LIMITER_SERVER_KIND')
    for key,v in state['notifications'].items():
        if not re.fullmatch(r'\d+:N|\d+:2N|\d+:CAP',key) or set(v)!={'threshold','count','day'} or v['threshold'] not in ['N','2N','CAP'] or type(v['count']) is not int or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',v['day']):raise ValueError('LIMITER_NOTICE_SCHEMA')
    for v in state['resets']:
        if set(v)!={'approval_sha256','expected_sequence','at'} or not re.fullmatch('[0-9a-f]{64}',v['approval_sha256']) or type(v['expected_sequence']) is not int or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',v['at']):raise ValueError('LIMITER_RESET_SCHEMA')
    return state


class GitLedger:
    def __init__(self, repo, remote=False, expected_remote=None, allow_initialization=False,
                 *, protected_owner_group=False):
        self.repo=Path(repo);self.remote=remote;self.expected_remote=expected_remote;self.allow_initialization=allow_initialization
        if type(protected_owner_group) is not bool:
            raise ValueError('LIMITER_PROTECTED_GROUP_SELECTION_REQUIRED')
        self.protected_owner_group=protected_owner_group

    def _git_credentials(self):
        # The root broker's primary group serves its socket, not its private ledger.
        # Set only the Git child's group, before it creates/fetches any objects.
        # Existing objects are never repaired here; all other callers keep defaults.
        if not self.protected_owner_group:
            return {}
        if os.geteuid() != 0:
            raise ValueError('LIMITER_PROTECTED_GROUP_ROOT_REQUIRED')
        for path in (self.repo, self.repo/'.git', self.repo/'.git/objects'):
            info=path.lstat()
            if (not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_gid != 0
                    or stat.S_IMODE(info.st_mode) & 0o022):
                raise ValueError('LIMITER_PROTECTED_OBJECT_PARENT_REQUIRED')
        return {'group': 0}

    def _bookkeeping_before(self):
        # Git atomically replaces shallow/tracking refs under its child's group.
        # Their historical owner need not match the object directory's owner.
        # Capture only preexisting native bookkeeping, never an object or user path.
        names=('.git/FETCH_HEAD', '.git/shallow',
               '.git/refs/remotes/origin/automation/dispatch-state',
               '.git/logs/refs/remotes/origin/automation/dispatch-state')
        rows={}
        for name in names:
            path=self.repo/name
            for parent in path.parents:
                if parent==self.repo: break
                if parent.is_symlink():
                    raise ValueError('LIMITER_BOOKKEEPING_SYMLINK')
            try: before=path.lstat()
            except FileNotFoundError: continue
            if (not stat.S_ISREG(before.st_mode) or before.st_uid!=0
                    or before.st_nlink!=1 or stat.S_IMODE(before.st_mode)&0o022):
                raise ValueError('LIMITER_BOOKKEEPING_LAYOUT')
            rows[path]=before
        return rows

    def _bookkeeping_after(self, rows):
        # This is ownership preservation for Git's atomic replacements, not a
        # census/repair of existing objects. A failed/interrupted command remains
        # subject to ordinary admission reconciliation and native preservation.
        replaceable={'.git/shallow', '.git/refs/remotes/origin/automation/dispatch-state'}
        for path,before in rows.items():
            for parent in path.parents:
                if parent==self.repo: break
                if parent.is_symlink():
                    raise ValueError('LIMITER_BOOKKEEPING_SYMLINK')
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
            try:
                after=os.fstat(fd)
                if (not stat.S_ISREG(after.st_mode) or after.st_nlink!=1
                        or (after.st_uid,after.st_dev,stat.S_IMODE(after.st_mode))
                        !=(before.st_uid,before.st_dev,stat.S_IMODE(before.st_mode))):
                    raise ValueError('LIMITER_BOOKKEEPING_METADATA')
                replaced=after.st_ino!=before.st_ino
                if replaced and str(path.relative_to(self.repo)) not in replaceable:
                    raise ValueError('LIMITER_BOOKKEEPING_UNEXPECTED_REPLACEMENT')
                if after.st_gid!=before.st_gid:
                    if not replaced or after.st_gid!=0:
                        raise ValueError('LIMITER_BOOKKEEPING_UNEXPECTED_GROUP')
                    os.fchown(fd,-1,before.st_gid)
                    os.fsync(fd)
                final=os.fstat(fd)
                current=path.lstat()
                if ((current.st_dev,current.st_ino)!=(final.st_dev,final.st_ino)
                        or final.st_gid!=before.st_gid):
                    raise ValueError('LIMITER_BOOKKEEPING_PATH_CHANGED')
            finally:
                os.close(fd)

    def git(self,*args,input=None,check=True):
        auth=['-c','credential.helper=','-c','credential.helper=!gh auth git-credential'] if self.remote else []
        credentials=self._git_credentials()
        before=self._bookkeeping_before() if self.protected_owner_group else {}
        try:
            return git_run(['git',*IDENTITY,*auth,*args],cwd=self.repo,input=input,text=True,
                           capture_output=True,check=check,**credentials)
        finally:
            self._bookkeeping_after(before)
    def read(self):
        if self.remote:
            if self.expected_remote and self.git('remote','get-url','origin').stdout.strip()!=self.expected_remote:raise ValueError('LIMITER_REPOSITORY_MISMATCH')
            advertised=self.git('ls-remote','origin',REF).stdout.split()
            if len(advertised)!=2 or advertised[1]!=REF:raise ValueError('LIMITER_STATE_NOT_PROVISIONED')
            pin=advertised[0]
            self.git('fetch','--no-tags','--depth=1','origin',pin)
        else:
            r=self.git('rev-parse','--verify',REF,check=False)
            if r.returncode:raise ValueError('LIMITER_STATE_NOT_PROVISIONED')
            pin=r.stdout.strip()
        entries=self.git('ls-tree',pin).stdout.splitlines()
        if len(entries)!=1 or entries[0].split()[0]!='100644' or entries[0].split()[-1]!=FILE:
            raise ValueError('LIMITER_TREE_REJECTED')
        state=validate(json.loads(self.git('show',pin+':'+FILE).stdout))
        return pin,state
    def cas(self,old,state):
        # Validate all outgoing bytes before creating the commit or touching the ref.
        raw=json.dumps(validate(state),sort_keys=True)+'\n'
        blob=self.git('hash-object','-w','--stdin',input=raw).stdout.strip()
        tree=self.git('mktree',input='100644 blob '+blob+'\t'+FILE+'\n').stdout.strip()
        args=['commit-tree',tree]
        if old:args+=['-p',old]
        new=self.git(*args,input='Dispatch admission metadata; no scientific authority\n').stdout.strip()
        from orchestrator.git_publication import scan_commit
        scan_commit(self.git('cat-file','commit',new).stdout.encode())
        if self.remote:
            if not old and not self.allow_initialization:raise ValueError('OPERATOR_MUST_INITIALIZE_STATE_REF')
            if self.expected_remote and self.git('remote','get-url','origin').stdout.strip()!=self.expected_remote:raise ValueError('LIMITER_REPOSITORY_MISMATCH')
            r=self.git('push','--porcelain','--force-with-lease='+REF+':'+(old or ''),'origin',new+':'+REF,check=False)
            if r.returncode:
                # Distinguish a real CAS race from unavailable permission/connectivity.
                current=self.git('ls-remote','origin',REF).stdout.split()
                if current and current[0]!=old:return False
                raise ValueError('LIMITER_STATE_WRITE_UNAVAILABLE')
            statuses=[line.split('\t') for line in r.stdout.splitlines() if '\t' in line]
            if len(statuses)!=1 or statuses[0][1]!=new+':'+REF:raise ValueError('LIMITER_CAS_RESULT_UNVERIFIED')
            # Git can report an already-identical ref as up-to-date without
            # exercising the expected-old lease. Re-read it as a duplicate/race.
            if statuses[0][0]=='=':return False
            if statuses[0][0]!=('*' if old is None else ' '):raise ValueError('LIMITER_CAS_RESULT_UNVERIFIED')
        else:
            r=self.git('update-ref',REF,new,old or '0'*40,check=False)
            if r.returncode:return False
        return True


def policy(config):
    if config.get('status')!='RATIFIED' or not config.get('operator_approval') or config.get('state_write_permission')!='OPERATOR_AUTHORIZED':
        raise ValueError('LIMITER_RATIFICATION_AND_PERMISSION_REQUIRED')
    if type(config.get('n')) is not int or not 1<=config['n']<=10000:raise ValueError('LIMITER_N_REQUIRED')
    if config.get('window')!='UTC_CALENDAR_DAY' or config.get('state_ref')!=REF:raise ValueError('LIMITER_POLICY_UNSUPPORTED')
    return config['n']


def admit(store,config,event,now=None,max_retries=12):
    n=policy(config)
    if set(event)!={'run_id','attempt','source','branch'} or not re.fullmatch(r'\d+',event['run_id']) or not re.fullmatch(r'[1-9]\d*',event['attempt']) or not re.fullmatch('[0-9a-f]{40}',event['source']) or event['branch'] not in ['main','astra/autonomous-isles-pilot']:
        raise ValueError('LIMITER_EVENT_IDENTITY_REQUIRED')
    return _admit(store,config,event,event['run_id']+':'+event['attempt'],now,max_retries)


def admit_server(store,config,event,now=None,max_retries=12):
    # This library is not the permission boundary: the protected broker owns config
    # and authenticates the requester. Live policy remains inactive until approved.
    policy(config)
    if config.get('server_semantics')!='OPERATOR_AUTHORIZED_V1':raise ValueError('SERVER_ADMISSION_NOT_AUTHORIZED')
    validate_server_event(event)
    return _admit(store,config,event,'server:'+event['turn_id']+':'+event['attempt'],now,max_retries)


def validate_server_event(event):
    if set(event)!={'turn_id','attempt','source','branch','kind'} or not re.fullmatch('[0-9a-f]{64}',event['turn_id']) or not re.fullmatch('[1-9][0-9]*',event['attempt']) or not re.fullmatch('[0-9a-f]{40}',event['source']) or event['branch']!='astra/infrastructure-milestone-record' or event['kind'] not in ['astra_turn','nightly_review']:
        raise ValueError('LIMITER_SERVER_IDENTITY')

def admit_manual(store, config, event, now=None, *, allowance=None):
    """Explicit local acceptance allowance; never resets or uses server authority.

    Reuses the same CAS, validation, duplicate charging and latched halt engine.
    The caller separately enforces the bound lifetime (eight or six) and per-role limits.
    """
    policy(config)
    if (config.get('manual_semantics'),config['n']) not in {('OPERATOR_STEP_D_MAX_EIGHT',4),('OPERATOR_SERVER_SPRINT10_MAX_SIX',3)}:
        raise ValueError('MANUAL_ALLOWANCE_REQUIRED')
    if (set(event) != {'run_id','attempt','source','branch'}
            or not re.fullmatch('[0-9a-f]{64}',event['run_id'])
            or not re.fullmatch('[1-8]',event['attempt'])
            or not re.fullmatch('[0-9a-f]{40}',event['source'])
            or not re.fullmatch('astra/manual-[a-z0-9-]+',event['branch'])):
        raise ValueError('MANUAL_ACCOUNTING_BINDING')
    effective_n = None
    exact_limit = None
    if allowance is not None:
        from orchestrator import autonomy_limits
        autonomy_limits.authority()
        if allowance.get('run_limit') in (23,24):
            if type(allowance['run_limit']) is not int:raise ValueError('MANUAL_LIMIT_AMENDMENT_BINDING')
            from orchestrator.item4_scoped_calls import validate_allowance
            validate_allowance(store,event,allowance)
            exact_limit = allowance['run_limit']
        elif allowance.get('run_limit') == 30:
            from orchestrator import diagnostics_policy
            if (set(allowance) != {'authority_sha256','run_limit','scoped_run_id'} or
                    type(allowance['run_limit']) is not int or
                    allowance['authority_sha256'] != diagnostics_policy.authority() or
                    allowance['scoped_run_id'] != diagnostics_policy.RUN_ID):
                raise ValueError('MANUAL_LIMIT_AMENDMENT_BINDING')
        elif (set(allowance) != {'authority_sha256','run_limit'} or
                allowance['authority_sha256'] != autonomy_limits.AUTHORITY or
                type(allowance['run_limit']) is not int or allowance['run_limit'] not in (16,20)):
            raise ValueError('MANUAL_LIMIT_AMENDMENT_BINDING')
        effective_n = allowance['run_limit']//2
    result = _admit(store,config,event,'manual:'+event['run_id']+':'+event['attempt'],now,12,effective_n=effective_n,exact_limit=exact_limit)
    return {**result,'limit_amendment':allowance} if allowance is not None else result


def pending_notifications(state):
    # Git JSON uses sorted keys: lexicographic order is not admission order.
    return sorted(state['notifications'], key=lambda key:int(key.split(':',1)[0]))[-4:]


def _admit(store,config,event,key,now,max_retries,*,effective_n=None,exact_limit=None):
    n=policy(config) if effective_n is None else effective_n
    ceiling=2*n if exact_limit is None else exact_limit
    if type(ceiling) is not int or ceiling < n:raise ValueError('LIMITER_EXACT_LIMIT_REQUIRED')
    day=(now or datetime.now(timezone.utc)).astimezone(timezone.utc).date().isoformat()
    for _ in range(max_retries):
        old,state=store.read()
        binding=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
        if state['policy_sha256'] not in [None,binding]:raise ValueError('LIMITER_POLICY_CHANGE_REQUIRES_RESET')
        state['policy_sha256']=binding
        if key in state['events']:
            e=state['events'][key]
            if any(e[k]!=event[k] for k in ['source','branch']) or e.get('kind')!=event.get('kind'):raise ValueError('LIMITER_EVENT_BINDING_CHANGED')
            return {'status':'ADMITTED','duplicate_admission':True,**e,'state_before':old,'pending_notifications':pending_notifications(state)}
        # Halt is latched across midnight. No automatic recovery/reset.
        if state['count']>ceiling or (state['count']==ceiling and not state['halted']):raise ValueError('LIMITER_STATE_INCONSISTENT')
        if state['halted']:return {'status':'HALTED_OPERATOR_RESET_REQUIRED','count':state['count'],'day':state['day']}
        if state['day'] and day<state['day']:raise ValueError('LIMITER_CLOCK_ROLLBACK')
        if state['day']!=day:state.update(day=day,count=0)
        state['count']+=1;state['sequence']+=1
        notice=('CAP' if exact_limit is not None else '2N') if state['count']>=ceiling else 'N' if state['count']==n else None
        state['halted']=state['count']>=ceiling
        e={'source':event['source'],'branch':event['branch'],'day':day,'count':state['count'],'notification':notice,'halted':state['halted']}
        if 'kind' in event:e['kind']=event['kind']
        state['events'][key]=e
        if notice:state['notifications'][str(state['sequence'])+':'+notice]={'threshold':notice,'count':state['count'],'day':day}
        if store.cas(old,state):return {'status':'ADMITTED','duplicate_admission':False,**e,'state_before':old,'pending_notifications':pending_notifications(state)}
    raise ValueError('LIMITER_CAS_RETRY_EXHAUSTED')


def reset(store,config,approval,now=None):
    """Explicit operator reset input, never called by admission or model stages.

Caller must separately authenticate/authorize the operator; a JSON field is not
an operator signature. Production reset permission is part of the pending plan.
"""
    policy(config)
    if set(approval)!={'actor','role','decision_ref','expected_sequence'} or approval['role']!='operator' or not approval['decision_ref'] or approval['actor'] not in config.get('reset_operators',[]):
        raise ValueError('OPERATOR_RESET_APPROVAL_REQUIRED')
    old,state=store.read()
    if state['sequence']!=approval['expected_sequence']:raise ValueError('RESET_STATE_MOVED')
    stamp=(now or datetime.now(timezone.utc)).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    state['resets'].append({'approval_sha256':hashlib.sha256(json.dumps(approval,sort_keys=True).encode()).hexdigest(),'expected_sequence':state['sequence'],'at':stamp})
    state.update(day=stamp[:10],count=0,halted=False,sequence=state['sequence']+1,policy_sha256=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest())
    if not store.cas(old,state):raise ValueError('RESET_STATE_MOVED')
    return {'status':'OPERATOR_RESET_RECORDED','sequence':state['sequence']}



def initialize(store,config,approval):
    """Operator-only creation of the metadata ref. Caller authenticates operator."""
    policy(config)
    if set(approval)!={'actor','role','decision_ref'} or approval['role']!='operator' or approval['actor'] not in config.get('reset_operators',[]) or not approval['decision_ref']:
        raise ValueError('OPERATOR_INITIALIZATION_APPROVAL_REQUIRED')
    state=initial();state['policy_sha256']=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
    # Absent-ref CAS, never overwrite an existing state or reset a halt.
    if not store.cas(None,state):raise ValueError('LIMITER_STATE_ALREADY_EXISTS')
    return {'status':'INITIALIZED','approval_sha256':hashlib.sha256(json.dumps(approval,sort_keys=True).encode()).hexdigest()}


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',default='configs/pilot/dispatch-limiter.json');p.add_argument('--repo',required=True);a=p.parse_args()
    config=json.loads(Path(a.config).read_text())
    if config['status']=='PROPOSED':
        print(json.dumps({'status':'PROPOSED_NOT_ACTIVE','standing_dispatch_grant':False}));return 0
    if os.environ.get('GITHUB_ACTIONS')!='true':raise ValueError('HOSTED_ADMISSION_REQUIRED')
    if os.environ.get('GITHUB_REPOSITORY')!=config.get('repository'):raise ValueError('LIMITER_REPOSITORY_MISMATCH')
    event={'run_id':os.environ['GITHUB_RUN_ID'],'attempt':os.environ['GITHUB_RUN_ATTEMPT'],'source':os.environ['GITHUB_SHA'],'branch':os.environ['GITHUB_REF_NAME']}
    r=admit(GitLedger(a.repo,remote=True,expected_remote='https://github.com/'+config['repository']+'.git'),config,event)
    print(json.dumps(r))
    # Fixed metadata only; no model/user content or credentials in notifications.
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        from orchestrator.public_export import summary
        text='Dispatch limiter: '+r['status']+'.'
        if r.get('notification') or r.get('pending_notifications'):text+=' Threshold notification recorded in the shared ledger. Operator: inspect admission state; at 2N further admission requires explicit reset.'
        summary(text,os.environ['GITHUB_STEP_SUMMARY'])
        if r.get('notification') or r.get('pending_notifications'):
            print('::warning title=Dispatch admission threshold::Operator notification: inspect this run Summary and shared admission ledger. No dollar-limit claim.')
    return 0 if r['status']=='ADMITTED' else 2

if __name__=='__main__':raise SystemExit(main())
