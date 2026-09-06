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
        if not re.fullmatch(r'\d+:\d+',key) or set(v)!={'source','branch','day','count','notification','halted'}:
            raise ValueError('LIMITER_EVENT_SCHEMA')
        if not re.fullmatch('[0-9a-f]{40}',v['source']) or v['branch'] not in ['main','astra/autonomous-isles-pilot'] or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',v['day']) or type(v['count']) is not int or v['notification'] not in [None,'N','2N'] or type(v['halted']) is not bool:
            raise ValueError('LIMITER_EVENT_VALUES')
    for key,v in state['notifications'].items():
        if not re.fullmatch(r'\d+:N|\d+:2N',key) or set(v)!={'threshold','count','day'} or v['threshold'] not in ['N','2N'] or type(v['count']) is not int or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',v['day']):raise ValueError('LIMITER_NOTICE_SCHEMA')
    for v in state['resets']:
        if set(v)!={'approval_sha256','expected_sequence','at'} or not re.fullmatch('[0-9a-f]{64}',v['approval_sha256']) or type(v['expected_sequence']) is not int or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',v['at']):raise ValueError('LIMITER_RESET_SCHEMA')
    return state


class GitLedger:
    def __init__(self, repo, remote=False, expected_remote=None, allow_initialization=False):
        self.repo=Path(repo);self.remote=remote;self.expected_remote=expected_remote;self.allow_initialization=allow_initialization
    def git(self,*args,input=None,check=True):
        auth=['-c','credential.helper=','-c','credential.helper=!gh auth git-credential'] if self.remote else []
        return subprocess.run(['git',*IDENTITY,*auth,*args],cwd=self.repo,input=input,text=True,capture_output=True,check=check)
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
            r=self.git('push','--force-with-lease='+REF+':'+(old or ''),'origin',new+':'+REF,check=False)
            if r.returncode:
                # Distinguish a real CAS race from unavailable permission/connectivity.
                current=self.git('ls-remote','origin',REF).stdout.split()
                if current and current[0]!=old:return False
                raise ValueError('LIMITER_STATE_WRITE_UNAVAILABLE')
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
    day=(now or datetime.now(timezone.utc)).astimezone(timezone.utc).date().isoformat()
    key=event['run_id']+':'+event['attempt']
    for _ in range(max_retries):
        old,state=store.read()
        binding=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
        if state['policy_sha256'] not in [None,binding]:raise ValueError('LIMITER_POLICY_CHANGE_REQUIRES_RESET')
        state['policy_sha256']=binding
        if key in state['events']:
            e=state['events'][key]
            if any(e[k]!=event[k] for k in ['source','branch']):raise ValueError('LIMITER_EVENT_BINDING_CHANGED')
            return {'status':'ADMITTED','duplicate_admission':True,**e,'state_before':old,'pending_notifications':list(state['notifications'])[-4:]}
        # Halt is latched across midnight. No automatic recovery/reset.
        if state['count']>2*n or (state['count']==2*n and not state['halted']):raise ValueError('LIMITER_STATE_INCONSISTENT')
        if state['halted']:return {'status':'HALTED_OPERATOR_RESET_REQUIRED','count':state['count'],'day':state['day']}
        if state['day'] and day<state['day']:raise ValueError('LIMITER_CLOCK_ROLLBACK')
        if state['day']!=day:state.update(day=day,count=0)
        state['count']+=1;state['sequence']+=1
        notice='2N' if state['count']>=2*n else 'N' if state['count']==n else None
        state['halted']=state['count']>=2*n
        e={'source':event['source'],'branch':event['branch'],'day':day,'count':state['count'],'notification':notice,'halted':state['halted']}
        state['events'][key]=e
        if notice:state['notifications'][str(state['sequence'])+':'+notice]={'threshold':notice,'count':state['count'],'day':day}
        if store.cas(old,state):return {'status':'ADMITTED','duplicate_admission':False,**e,'state_before':old,'pending_notifications':list(state['notifications'])[-4:]}
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
