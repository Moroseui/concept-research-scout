"""Offline ledger fixtures: Python writes disposable bytes; Git only reads them."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import zlib
from datetime import datetime, timezone

import pytest
from orchestrator import dispatch_limiter as limiter
from orchestrator import inspection_admission_recovery as r

POLICY={'status':'RATIFIED','operator_approval':'synthetic permission fixture only',
 'state_write_permission':'OPERATOR_AUTHORIZED','n':100,'window':'UTC_CALENDAR_DAY',
 'state_ref':limiter.REF,'server_semantics':'OPERATOR_AUTHORIZED_V1',
 'repository':'Moroseui/concept-research-scout','reset_operators':['synthetic']}
SOURCE='a'*40

def write(path,raw,mode=0o600):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw);path.chmod(mode)

def event(turn,attempt=1):
    return {'turn_id':str(turn).zfill(64),'attempt':str(attempt),'source':SOURCE,
            'branch':'astra/infrastructure-milestone-record','kind':'nightly_review'}

def original(e,receipt):
    return {'event_original':r.encoded(e).decode(),'receipt_original':r.encoded(receipt).decode()}

class Fixture:
    def __init__(self,path,n=100):
        self.repo=path/'ledger';self.repo.mkdir()
        self.git=self.repo/'.git';self.git.mkdir(mode=0o700)
        for name in ('objects','objects/info','objects/pack','refs','refs/heads','refs/remotes/origin/automation',
                     'logs/refs/remotes/origin/automation'):
            (self.git/name).mkdir(parents=True,exist_ok=True,mode=0o700)
        for p in self.repo.rglob('*'):
            if p.is_dir():p.chmod(0o700)
        self.policy={**copy.deepcopy(POLICY),'n':n}
        config='[core]\nrepositoryformatversion = 0\nfilemode = true\nbare = false\nlogallrefupdates = true\nhooksPath = /dev/null\n[remote "origin"]\nurl = https://github.com/Moroseui/concept-research-scout.git\nfetch = +refs/heads/*:refs/remotes/origin/*\n'
        write(self.git/'config',config.encode())
        write(self.git/'HEAD',b'ref: refs/heads/master\n')
        self.objects={};self.commits=[];self.head=None;self.state=limiter.initial();self.counter=0
        self.commit(self.state)
        self.canaries=[self.admit(event(1)),self.admit(event(2))]
        self.baseline=r.capture_ledger(self.repo,self.policy,self.status(),self.canaries)

    def obj(self,kind,raw):
        framed=kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw
        oid=hashlib.sha1(framed).hexdigest();path=self.git/'objects'/oid[:2]/oid[2:]
        if not path.exists():
            path.parent.mkdir(exist_ok=True,mode=0o700)
            write(path,zlib.compress(framed),0o400)
        self.objects[oid]=(kind,raw);return oid

    def commit(self,state,parent=None):
        before=self.head if parent is None else parent
        blob=self.obj('blob',(json.dumps(state,sort_keys=True)+'\n').encode())
        tree=self.obj('tree',b'100644 dispatch_state.json\0'+bytes.fromhex(blob))
        self.counter+=1;identity=b'Astra (OpenAI agent) <astra@agents.local.invalid> '+str(1789257600+self.counter).encode()+b' +0000'
        raw=b'tree '+tree.encode()+b'\n'+(b'parent '+before.encode()+b'\n' if before else b'')
        raw+=b'author '+identity+b'\ncommitter '+identity+b'\n\n'+r.MESSAGE
        oid=self.obj('commit',raw);self.commits.append(oid)
        old=self.head or '0'*40
        self.head=oid;self.state=copy.deepcopy(state)
        write(self.repo/r.TRACKING,(oid+'\n').encode())
        write(self.git/'FETCH_HEAD',(oid+"\t\t'"+oid+"' of https://github.com/Moroseui/concept-research-scout\n").encode())
        write(self.git/'shallow',('\n'.join(sorted(set(self.commits)))+'\n').encode())
        line=(old+' '+oid+' Astra (OpenAI agent) <astra@agents.local.invalid> '+str(1789257600+self.counter)+' +0000\tupdate by push\n').encode()
        with (self.repo/r.REFLOG).open('ab') as stream:stream.write(line)
        (self.repo/r.REFLOG).chmod(0o600)
        return oid

    def admit(self,e,day='2026-09-12'):
        class Store:
            def read(inner):return self.head,copy.deepcopy(self.state)
            def cas(inner,old,state):
                assert old==self.head
                self.commit(state);return True
        result=limiter.admit_server(Store(),self.policy,e,now=datetime.strptime(day,'%Y-%m-%d').replace(tzinfo=timezone.utc),max_retries=1)
        return original(e,result)

    def status(self):
        return {'mode':'LIVE_APPROVED','pin':self.head,**{k:self.state[k] for k in ('sequence','count','halted','day')}}

    def pack(self,oids,delta=None):
        body=b'PACK'+struct.pack('>II',2,len(oids));rows=[]
        kinds={'commit':1,'tree':2,'blob':3}
        for oid in oids:
            kind,raw=self.objects[oid]
            base=b''
            if delta and oid==delta[0]:
                def varint(number):
                    result=bytearray()
                    while True:
                        byte=number&127;number>>=7
                        result.append(byte|(128 if number else 0))
                        if not number:return bytes(result)
                prior=self.objects[delta[1]][1]
                raw=varint(len(prior))+varint(len(raw))+b''.join(bytes([len(raw[i:i+127])])+raw[i:i+127]
                    for i in range(0,len(raw),127))
                base=bytes.fromhex(delta[1]);kind_id=7
            else:kind_id=kinds[kind]
            size=len(raw)
            byte=(kind_id<<4)|(size&15);size>>=4;header=bytearray()
            if size:byte|=128
            header.append(byte)
            while size:
                byte=size&127;size>>=7
                if size:byte|=128
                header.append(byte)
            entry=bytes(header)+base+zlib.compress(raw);offset=len(body)
            rows.append((oid,zlib.crc32(entry),offset));body+=entry
        checksum=hashlib.sha1(body).digest();body+=checksum
        rows.sort()
        fanout=[sum(bytes.fromhex(oid)[0]<=i for oid,crc,off in rows) for i in range(256)]
        idx=b'\xfftOc'+struct.pack('>I',2)+b''.join(struct.pack('>I',n) for n in fanout)
        idx+=b''.join(bytes.fromhex(oid) for oid,crc,off in rows)
        idx+=b''.join(struct.pack('>I',crc) for oid,crc,off in rows)
        idx+=b''.join(struct.pack('>I',off) for oid,crc,off in rows)+checksum
        idx+=hashlib.sha1(idx).digest()
        stem=self.git/'objects/pack'/('pack-'+checksum.hex())
        write(Path(str(stem)+'.pack'),body,0o400);write(Path(str(stem)+'.idx'),idx,0o400)
        return stem

def verify(f,admissions):
    return r.verify_transition(f.repo,f.baseline,f.policy,admissions,f.status())

def test_exact_two_canaries_then_single_session_suffix_preserves_baseline(tmp_path):
    f=Fixture(tmp_path);old=copy.deepcopy(f.baseline)
    admissions=[f.admit(event(3,1)),f.admit(event(3,2))]
    result=verify(f,admissions)
    assert result['status']=='VERIFIED_ONLY_APPROVED_SESSION_ADMISSIONS'
    assert result['original_head']==old['original_head'] and result['current_head']==f.head
    assert result['baseline_sha256']==r.digest(r.encoded(old))
    assert result['admissions_sha256']==r.digest(r.encoded(admissions))
    assert f.baseline==old and len(result['suffix'])==2
    assert result['git_mutations']==result['remote_calls']==0

def test_midnight_rollover_is_exact_ordinary_replay(tmp_path):
    f=Fixture(tmp_path)
    admission=f.admit(event(3),day='2026-09-13')
    assert f.state['count']==1 and f.state['sequence']==3
    assert verify(f,[admission])['current_head']==f.head

@pytest.mark.parametrize('n,expected',[ (3,'N'),(2,None)])
def test_notification_and_latched_halt_semantics(tmp_path,n,expected):
    f=Fixture(tmp_path,n=n);admissions=[f.admit(event(3))]
    if n==2:admissions.append(f.admit(event(3,2)))
    result=verify(f,admissions)
    assert result['current_head']==f.head
    if n==3:assert f.state['notifications']['3:N']['count']==3 and not f.state['halted']
    else:
        assert f.state['halted'] and f.state['notifications']['4:2N']['count']==4
        blocked=f.admit(event(4),day='2026-09-13')
        assert json.loads(blocked['receipt_original'])['status']=='HALTED_OPERATOR_RESET_REQUIRED'
        with pytest.raises(ValueError,match='ONLY_SUCCESSFUL_REVIEW_ADMISSION'):verify(f,admissions+[blocked])

def test_clock_rollback_cannot_be_replayed_as_an_allowance(tmp_path):
    f=Fixture(tmp_path);admission=f.admit(event(3))
    receipt=json.loads(admission['receipt_original']);receipt['day']='2026-09-11'
    admission['receipt_original']=r.encoded(receipt).decode()
    with pytest.raises(ValueError,match='LIMITER_CLOCK_ROLLBACK'):verify(f,[admission])

@pytest.mark.parametrize('kind',['missing','extra','reordered','wrong-before','wrong-receipt','duplicate','foreign-kind','wrong-endpoint'])
def test_no_skipped_foreign_or_changed_admissions(tmp_path,kind):
    f=Fixture(tmp_path);a=f.admit(event(3));b=f.admit(event(3,2));values=[a,b]
    if kind=='missing':values=[b]
    if kind=='extra':f.admit(event(4))
    if kind=='reordered':values=[b,a]
    if kind in ('wrong-before','wrong-receipt','duplicate'):
        c=json.loads(a['receipt_original'])
        if kind=='wrong-before':c['state_before']='f'*40
        elif kind=='wrong-receipt':c['count']=999
        else:c['duplicate_admission']=True
        a['receipt_original']=r.encoded(c).decode()
    if kind=='foreign-kind':
        e=json.loads(a['event_original']);e['kind']='astra_turn';a['event_original']=r.encoded(e).decode()
    if kind=='wrong-endpoint':
        status=f.status();status['pin']=f.baseline['original_head']
        with pytest.raises(ValueError):r.verify_transition(f.repo,f.baseline,f.policy,values,status)
    else:
        with pytest.raises(ValueError):verify(f,values)

def test_reset_inside_window_is_never_a_valid_review_admission(tmp_path):
    f=Fixture(tmp_path);a=f.admit(event(3))
    changed=copy.deepcopy(f.state)
    changed['resets'].append({'approval_sha256':'d'*64,'expected_sequence':3,'at':'2026-09-12T00:00:00Z'})
    changed.update(sequence=4,count=0,halted=False)
    f.commit(changed)
    with pytest.raises(ValueError,match='SUFFIX_LENGTH'):verify(f,[a])

@pytest.mark.parametrize('kind',['tracked-ref','fetch','shallow','reflog','config','unknown-file','unrelated-blob','object-content','object-mode','object-removed','directory','symlink'])
def test_raw_repository_preservation_is_independent_of_valid_state(tmp_path,kind):
    f=Fixture(tmp_path);a=f.admit(event(3))
    if kind=='tracked-ref':write(f.repo/r.TRACKING,(f.baseline['original_head']+'\n').encode())
    if kind=='fetch':write(f.git/'FETCH_HEAD',b'unrelated\n')
    if kind=='shallow':write(f.git/'shallow',(f.head+'\n').encode())
    if kind=='reflog':
        p=f.repo/r.REFLOG;raw=p.read_bytes();write(p,raw.replace(b'update by push',b'changed reason',1))
    if kind=='config':
        p=f.git/'config';write(p,p.read_bytes()+b'\n[include]\npath = /outside\n')
    if kind=='unknown-file':write(f.git/'unknown',b'not native transport\n')
    if kind=='unrelated-blob':f.obj('blob',b'unrelated metadata\n')
    if kind in ('object-content','object-mode','object-removed'):
        oid=next(iter(f.baseline['snapshot']['objects']));p=f.git/'objects'/oid[:2]/oid[2:]
        if kind=='object-content':p.chmod(0o600);p.write_bytes(b'broken');p.chmod(0o400)
        elif kind=='object-mode':p.chmod(0o600)
        else:p.unlink()
    if kind=='directory':(f.git/'objects').chmod(0o750)
    if kind=='symlink':(f.repo/'outside').symlink_to('/tmp')
    with pytest.raises(ValueError):verify(f,[a])

def test_valid_new_pack_closes_exact_objects_and_preserved_dependencies(tmp_path):
    f=Fixture(tmp_path);a=f.admit(event(3))
    new=list(set(f.objects)-set(f.baseline['snapshot']['objects']))
    f.pack(new+[next(iter(f.baseline['snapshot']['objects']))])
    result=verify(f,[a])
    assert any(x.endswith('.pack') for x in result['repository_changes']['added_files'])

def test_new_pack_cannot_smuggle_an_unrelated_valid_object(tmp_path):
    f=Fixture(tmp_path);a=f.admit(event(3))
    oid=f.obj('blob',b'unrelated packed original')
    f.pack([oid]);(f.git/'objects'/oid[:2]/oid[2:]).unlink()
    with pytest.raises(ValueError,match='UNRELATED_NEW_OBJECT'):verify(f,[a])

def test_repacking_does_not_waive_old_file_preservation(tmp_path):
    f=Fixture(tmp_path);a=f.admit(event(3))
    oid=next(iter(f.baseline['snapshot']['objects']));f.pack([oid])
    (f.git/'objects'/oid[:2]/oid[2:]).unlink()
    with pytest.raises(ValueError,match='PREEXISTING_FILE_REMOVED'):verify(f,[a])

def test_baseline_proves_both_canaries_end_at_the_captured_head(tmp_path):
    f=Fixture(tmp_path);f.admit(event(3))
    with pytest.raises(ValueError):r.capture_ledger(f.repo,f.policy,f.status(),f.canaries)

def test_baseline_policy_and_original_hashes_refuse_mutation(tmp_path):
    f=Fixture(tmp_path);r.validate_baseline(f.baseline,f.policy)
    altered=copy.deepcopy(f.baseline);altered['snapshot']['control_originals']['.git/config']+=' '
    with pytest.raises(ValueError,match='BASELINE_CONTROL_HASH'):r.validate_baseline(altered,f.policy)
    with pytest.raises(ValueError,match='POLICY_CHANGED'):r.validate_baseline(f.baseline,{**f.policy,'n':200})


@pytest.mark.parametrize('kind',['foreign-session','skipped-attempt'])
def test_valid_limiter_events_do_not_make_another_session_eligible(tmp_path,kind):
    f=Fixture(tmp_path)
    first=f.admit(event(3))
    second=f.admit(event(4) if kind=='foreign-session' else event(3,3))
    with pytest.raises(ValueError,match='ONLY_ONE_SEQUENTIAL_REVIEW_SESSION'):
        verify(f,[first,second])

def test_unknown_empty_git_directory_is_a_layout_refusal(tmp_path):
    f=Fixture(tmp_path);a=f.admit(event(3))
    (f.git/'refs/replace').mkdir()
    with pytest.raises(ValueError,match='UNKNOWN_GIT_DIRECTORY'):verify(f,[a])


def test_valid_fetch_pack_with_delta_and_no_new_loose_objects(tmp_path):
    f=Fixture(tmp_path);a=f.admit(event(3))
    new=sorted(set(f.objects)-set(f.baseline['snapshot']['objects']))
    blob=next(oid for oid in new if f.objects[oid][0]=='blob')
    base=next(oid for oid in f.baseline['snapshot']['objects'] if f.objects[oid][0]=='blob')
    f.pack([base,*new],delta=(blob,base))
    for oid in new:
        path=f.git/'objects'/oid[:2]/oid[2:];path.unlink()
        if not list(path.parent.iterdir()) and path.parent.relative_to(f.repo).as_posix() not in f.baseline['snapshot']['directories']:
            path.parent.rmdir()
    result=verify(f,[a])
    assert result['current_head']==f.head
    assert all('/pack/' in name for name in result['repository_changes']['added_files'])

@pytest.mark.parametrize('count',[16,17])
def test_native_material_sixteen_admission_suffix_boundary(tmp_path,count):
    f=Fixture(tmp_path)
    admissions=[f.admit(event(3,number)) for number in range(1,count+1)]
    if count==17:
        with pytest.raises(ValueError,match='BOUNDED_ADMISSIONS_REQUIRED'):
            verify(f,admissions)
    else:
        result=verify(f,admissions)
        assert len(result['suffix'])==16 and result['current_head']==f.head
        assert result['git_mutations']==result['remote_calls']==0


def test_pinned_research_admission_and_manual_units_replay_without_recharging(tmp_path):
    from orchestrator import install_reviewed_deployment as installer
    f = Fixture(tmp_path)
    cases = []
    for number, day in [(3, '2026-09-12'), (4, '2026-09-12'), (5, '2026-09-13')]:
        ev = {**event(number), 'kind': 'astra_turn'}
        raw = f.admit(ev, day=day)
        cases.append({'event': ev, 'receipt': json.loads(raw['receipt_original']), 'state_after': f.head})
    # The middle unit is a prior research admission, never a manual billing unit.
    baseline = {'ledger': f.baseline, 'preserved_admissions': [{**cases[1], 'receipt_origin':'DERIVED_FROM_AUTHENTICATED_LEDGER'}]}
    account = {'cases': [cases[0], cases[2]], 'ledger_pin': f.head}
    ordered = installer.terminal_admission_cases(account, baseline)
    assert [{k:v for k,v in row.items() if k!='receipt_origin'} for row in ordered] == cases and len(account['cases']) == 2
    originals = [original(x['event'], x['receipt']) for x in ordered]
    with pytest.raises(ValueError, match='EXACT_SUFFIX_LENGTH'):
        r.verify_terminal_transition(f.repo, f.baseline, f.policy,
            [original(x['event'], x['receipt']) for x in account['cases']], f.status())
    proof = r.verify_terminal_transition(f.repo, f.baseline, f.policy, originals, f.status(),
                                         preserved_admissions_count=1)
    assert proof['status'] == 'VERIFIED_TERMINAL_AND_PINNED_PRIOR_ADMISSIONS'
    assert proof['preserved_admissions_count'] == 1
    assert len(proof['suffix']) == 3 and proof['git_mutations'] == proof['remote_calls'] == 0
    assert f.state['count'] == 1 and f.state['resets'] == []


@pytest.mark.parametrize('damage', ['missing', 'duplicate', 'parent', 'head', 'receipt', 'event', 'extra', 'reset'])
def test_pinned_recovery_still_refuses_unknown_or_altered_transitions(tmp_path, damage):
    from orchestrator import install_reviewed_deployment as installer
    f = Fixture(tmp_path); cases = []
    for number in (3, 4, 5):
        ev = {**event(number), 'kind': 'astra_turn'}; raw = f.admit(ev)
        cases.append({'event': ev, 'receipt': json.loads(raw['receipt_original']), 'state_after': f.head})
    baseline = {'ledger': f.baseline, 'preserved_admissions': [{**copy.deepcopy(cases[1]),'receipt_origin':'DERIVED_FROM_AUTHENTICATED_LEDGER'}]}
    account = {'cases': [cases[0], cases[2]], 'ledger_pin': f.head}
    if damage == 'missing': baseline['preserved_admissions'] = []
    if damage == 'duplicate': baseline['preserved_admissions'].append({**cases[0],'receipt_origin':'DERIVED_FROM_AUTHENTICATED_LEDGER'})
    if damage == 'parent': baseline['preserved_admissions'][0]['receipt']['state_before'] = 'e'*40
    if damage == 'head': baseline['preserved_admissions'][0]['state_after'] = 'e'*40
    if damage == 'receipt': baseline['preserved_admissions'][0]['receipt']['count'] += 1
    if damage == 'event': baseline['preserved_admissions'][0]['event']['turn_id'] = 'e'*64
    if damage == 'extra': f.admit({**event(6), 'kind':'astra_turn'}); account['ledger_pin'] = f.head
    if damage == 'reset':
        state = copy.deepcopy(f.state); state.update(sequence=state['sequence']+1, count=0)
        state['resets'].append({'approval_sha256':'d'*64,'expected_sequence':state['sequence']-1,'at':'2026-09-12T00:00:00Z'})
        f.commit(state); account['ledger_pin'] = f.head
    with pytest.raises(ValueError):
        ordered = installer.terminal_admission_cases(account, baseline)
        r.verify_terminal_transition(f.repo, f.baseline, f.policy,
            [original(x['event'], x['receipt']) for x in ordered], f.status(),
            preserved_admissions_count=len(baseline['preserved_admissions']))
