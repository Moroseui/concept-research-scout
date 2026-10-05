"""Direct-inspection admission suffix proof; no remote calls or Git mutations.

The installer must first validate one completed approved session and authenticate
broker status while holding its admission lock. This module does not confer
session approval, mutate quota state or authorize installation.
"""
import configparser
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from datetime import datetime, timezone
from orchestrator import dispatch_limiter as limiter
from orchestrator import inspection_review as review

SCHEMA = 'inspection-admission-ledger-baseline/v1'
TRANSITION = 'inspection-admission-ledger-transition/v1'
TRACKING = '.git/refs/remotes/origin/automation/dispatch-state'
REFLOG = '.git/logs/refs/remotes/origin/automation/dispatch-state'
BOOKKEEPING = frozenset({'.git/FETCH_HEAD', '.git/shallow', TRACKING, REFLOG})
MAX_FILES = 20000
MAX_OBJECTS = 12000
MAX_BYTES = 50_000_000
HEX = r'[0-9a-f]{40}'
IDENTITY = r'Astra \(OpenAI agent\) <astra@agents\.local\.invalid>'
MESSAGE = b'Dispatch admission metadata; no scientific authority\n'

def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def require(ok, reason):
    if not ok: raise ValueError('INSPECTION_LEDGER_'+reason)

def pin(value):
    require(isinstance(value, str) and re.fullmatch(HEX, value), 'OBJECT_PIN')
    return value

def parsed(raw):
    def unique(rows):
        out = {}
        for key,value in rows:
            require(key not in out, 'DUPLICATE_JSON_KEY')
            out[key] = value
        return out
    return json.loads(raw, object_pairs_hook=unique)

def _regular(path):
    for p in (path, *path.parents):
        require(not p.is_symlink(), 'SYMLINK_REFUSED')
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_size <= MAX_BYTES, 'FILE_LAYOUT')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(fd)
        raw = b''
        while True:
            piece = os.read(fd, 1_000_000)
            if not piece: break
            raw += piece
            require(len(raw) <= MAX_BYTES, 'FILE_BOUND')
        after = os.fstat(fd)
    finally: os.close(fd)
    identity = lambda s: (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    require(identity(before) == identity(opened) == identity(after) == identity(path.lstat()), 'FILE_CHANGED_DURING_READ')
    return raw, {'uid':before.st_uid, 'gid':before.st_gid, 'mode':stat.S_IMODE(before.st_mode),
                 'inode':before.st_ino, 'device':before.st_dev, 'bytes':len(raw), 'sha256':digest(raw)}

def _inventory(repo):
    require(repo.is_absolute() and str(repo)==str(repo.resolve()) and repo.is_dir(), 'REPOSITORY_PATH')
    files, dirs, originals = {}, {}, {}
    for path in [repo, *sorted(repo.rglob('*'))]:
        info = path.lstat()
        require(not stat.S_ISLNK(info.st_mode), 'SYMLINK_REFUSED')
        name = path.relative_to(repo).as_posix()
        if stat.S_ISDIR(info.st_mode):
            dirs[name] = {'uid':info.st_uid,'gid':info.st_gid,'mode':stat.S_IMODE(info.st_mode),
                          'inode':info.st_ino,'device':info.st_dev}
        else:
            raw,row = _regular(path); files[name] = row
            if name in BOOKKEEPING or name in ('.git/config','.git/HEAD'):
                originals[name] = raw.decode('utf-8')
        require(len(files)+len(dirs) <= MAX_FILES, 'INVENTORY_BOUND')
    require('.git' in dirs and '.git/HEAD' in files and '.git/config' in files, 'ORDINARY_GIT_LAYOUT')
    for name in files:
        require(not name.endswith('.lock'), 'UNFINISHED_GIT_WRITE')
        require(not (name.startswith('.git/refs/') and name != TRACKING), 'UNKNOWN_REF')
        require(not (name.startswith('.git/logs/') and name != REFLOG), 'UNKNOWN_REFLOG')
        require(name not in ('.git/packed-refs','.git/commondir','.git/gitdir','.git/info/grafts',
                            '.git/objects/info/alternates','.git/objects/info/http-alternates'),
                'UNSUPPORTED_GIT_LAYOUT')
        if name.startswith('.git/objects/'):
            require(re.fullmatch(r'\.git/objects/[0-9a-f]{2}/[0-9a-f]{38}', name) or
                    re.fullmatch(r'\.git/objects/pack/pack-'+HEX+r'\.(pack|idx)', name),
                    'UNKNOWN_OBJECT_STORAGE')
        elif name.startswith('.git/'):
            require(name in BOOKKEEPING or name in ('.git/HEAD','.git/config','.git/description','.git/info/exclude')
                    or re.fullmatch(r'\.git/hooks/[A-Za-z0-9-]+\.sample',name), 'UNKNOWN_GIT_FILE')
    native_dirs={'.git','.git/branches','.git/hooks','.git/info','.git/objects',
                 '.git/objects/info','.git/objects/pack','.git/refs','.git/refs/heads',
                 '.git/refs/tags','.git/refs/remotes','.git/refs/remotes/origin',
                 '.git/refs/remotes/origin/automation','.git/logs','.git/logs/refs',
                 '.git/logs/refs/remotes','.git/logs/refs/remotes/origin',
                 '.git/logs/refs/remotes/origin/automation'}
    require(all(not name.startswith('.git/') or name in native_dirs or
                re.fullmatch(r'\.git/objects/[0-9a-f]{2}',name) for name in dirs),
            'UNKNOWN_GIT_DIRECTORY')
    require(originals['.git/HEAD']=='ref: refs/heads/master\n', 'UNKNOWN_HEAD_LAYOUT')
    return {'files':files,'directories':dirs,'control_originals':originals}

def _config(original, policy):
    require(isinstance(policy,dict) and isinstance(policy.get('repository'),str)
            and re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',policy['repository']), 'REPOSITORY_POLICY')
    url = 'https://github.com/'+policy['repository']+'.git'
    conf = configparser.RawConfigParser(strict=True, interpolation=None)
    conf.read_file(io.StringIO(original))
    require(set(conf.sections()) == {'core','remote "origin"'}, 'UNKNOWN_GIT_CONFIGURATION')
    require(dict(conf['core']) == {'repositoryformatversion':'0','filemode':'true','bare':'false',
                                   'logallrefupdates':'true','hookspath':'/dev/null'}, 'UNKNOWN_CORE_CONFIGURATION')
    require(dict(conf['remote "origin"']) == {'url':url,'fetch':'+refs/heads/*:refs/remotes/origin/*'},
            'ORIGIN_CONFIGURATION')
    return url

def _git(repo, args):
    # No shell, transport, hooks, lazy fetching, optional index locks or inherited
    # Git environment. Only callers below supply fixed read-only plumbing verbs.
    require(args and args[0] in ('cat-file','verify-pack'), 'NON_READ_ONLY_GIT_COMMAND')
    argv = ['/usr/bin/git','--no-replace-objects','-c','safe.directory='+str(repo),
            '-c','credential.helper=','-c','protocol.allow=never','-c','core.hooksPath=/dev/null',
            '-c','core.fsmonitor=false','-C',str(repo),*args]
    env = {'PATH':'/usr/bin:/bin','HOME':'/nonexistent','LC_ALL':'C','GIT_CONFIG_NOSYSTEM':'1',
           'GIT_CONFIG_GLOBAL':'/dev/null','GIT_OPTIONAL_LOCKS':'0','GIT_NO_LAZY_FETCH':'1',
           'GIT_TERMINAL_PROMPT':'0'}
    result = subprocess.run(argv, capture_output=True, timeout=30, env=env, check=False)
    require(result.returncode == 0 and not result.stderr and len(result.stdout) <= MAX_BYTES,
            'READ_ONLY_GIT_PLUMBING_REFUSED')
    return result.stdout

def _objects(repo, inventory):
    listing = _git(repo,['cat-file','--batch-all-objects','--batch-check=%(objectname) %(objecttype) %(objectsize)'])
    objects, raw_objects = {}, {}
    for line in listing.decode('ascii').splitlines():
        match = re.fullmatch('('+HEX+r') (blob|tree|commit) ([0-9]+)',line)
        require(match and match[1] not in objects, 'UNKNOWN_OBJECT_TYPE_OR_DUPLICATE')
        oid,kind,size = match[1],match[2],int(match[3])
        require(size <= 1_500_000 and len(objects) < MAX_OBJECTS, 'OBJECT_BOUND')
        raw = _git(repo,['cat-file',kind,oid])
        require(len(raw)==size and hashlib.sha1(kind.encode()+b' '+str(size).encode()+b'\0'+raw).hexdigest()==oid,
                'RAW_OBJECT_IDENTITY')
        objects[oid] = {'type':kind,'bytes':size,'sha256':digest(raw)}
        raw_objects[oid] = (kind,raw)
    loose,packed = set(), {}
    for name in inventory['files']:
        if re.fullmatch(r'\.git/objects/[0-9a-f]{2}/[0-9a-f]{38}',name):
            oid = ''.join(name.split('/')[-2:]);require(oid in objects,'UNENUMERATED_LOOSE_OBJECT');loose.add(oid)
    stems = {name.rsplit('.',1)[0] for name in inventory['files'] if name.startswith('.git/objects/pack/')}
    for stem in sorted(stems):
        require(stem+'.pack' in inventory['files'] and stem+'.idx' in inventory['files'],'INCOMPLETE_PACK_PAIR')
        raw,_ = _regular(repo/(stem+'.pack'))
        require(raw[:4]==b'PACK' and int.from_bytes(raw[4:8],'big')==2 and len(raw)>=32
                and hashlib.sha1(raw[:-20]).digest()==raw[-20:]
                and stem.endswith(raw[-20:].hex()),'PACK_IDENTITY')
        expected_count=int.from_bytes(raw[8:12],'big')
        lines=_git(repo,['verify-pack','-v',str(repo/(stem+'.idx'))]).decode().splitlines()
        rows=set()
        for line in lines:
            parts=line.split()
            if parts and re.fullmatch(HEX,parts[0]):
                require(len(parts) in (5,7) and parts[1] in ('blob','tree','commit')
                        and all(p.isdigit() for p in parts[2:5])
                        and (len(parts)==5 or (parts[5].isdigit() and re.fullmatch(HEX,parts[6]))),
                        'PACK_OBJECT_ROW')
                # verify-pack reports delta instruction bytes for a deltified
                # row. The reconstructed full object size/SHA1/SHA256 were checked
                # independently by cat-file above; do not confuse these sizes.
                oid=parts[0];require(oid in objects and objects[oid]['type']==parts[1]
                                    and oid not in rows and int(parts[2])<=MAX_BYTES,'PACK_OBJECT_IDENTITY')
                if len(parts)==5:
                    require(objects[oid]['bytes']==int(parts[2]),'PACK_FULL_OBJECT_SIZE')
                else:
                    require(parts[6] in objects and objects[parts[6]]['type']==parts[1],
                            'PACK_DELTA_BASE_IDENTITY')
                rows.add(oid)
            else:
                require(re.fullmatch(r'non delta: [0-9]+ objects?',line) or
                        re.fullmatch(r'chain length = [0-9]+: [0-9]+ objects?',line) or
                        line==str(repo/(stem+'.pack'))+': ok','PACK_DIAGNOSTIC')
        require(len(rows)==expected_count,'PACK_CONTENT_COUNT')
        packed[stem]=sorted(rows)
    require(set(objects)==loose|{oid for rows in packed.values() for oid in rows},'UNACCOUNTED_OBJECT_STORAGE')
    return objects,raw_objects,packed

def _snapshot(repo,policy):
    repo=Path(repo)
    before=_inventory(repo);url=_config(before['control_originals']['.git/config'],policy)
    objects,raw,packed=_objects(repo,before)
    require(_inventory(repo)==before,'REPOSITORY_CHANGED_DURING_READ')
    return {'repository':str(repo),'remote':url,**before,'objects':objects,'packs':packed},raw

def _state(objects,commit):
    pin(commit);require(commit in objects and objects[commit][0]=='commit','MISSING_COMMIT')
    raw=objects[commit][1]
    header,separator,message=raw.partition(b'\n\n')
    require(separator and message==MESSAGE,'COMMIT_MESSAGE')
    lines=header.decode('ascii').splitlines()
    require(len(lines) in (3,4) and re.fullmatch('tree '+HEX,lines[0]),'COMMIT_HEADERS')
    offset=2 if len(lines)==4 else 1
    parent=None
    if offset==2:
        require(re.fullmatch('parent '+HEX,lines[1]),'SINGLE_RAW_PARENT');parent=lines[1][7:]
    require(re.fullmatch('author '+IDENTITY+r' [0-9]+ [+-][0-9]{4}',lines[offset])
            and re.fullmatch('committer '+IDENTITY+r' [0-9]+ [+-][0-9]{4}',lines[offset+1]),'COMMIT_IDENTITY')
    tree=lines[0][5:];require(tree in objects and objects[tree][0]=='tree','MISSING_TREE')
    tree_raw=objects[tree][1];prefix=b'100644 '+limiter.FILE.encode()+b'\0'
    require(tree_raw.startswith(prefix) and len(tree_raw)==len(prefix)+20,'EXACT_SINGLE_FILE_TREE')
    blob=tree_raw[len(prefix):].hex();require(blob in objects and objects[blob][0]=='blob','MISSING_STATE_BLOB')
    state=limiter.validate(parsed(objects[blob][1]))
    return {'pin':commit,'parent':parent,'tree':tree,'blob':blob,'state':state,'blob_raw':objects[blob][1]}

def _status(status, row):
    require(isinstance(status,dict) and set(status)=={'mode','pin','sequence','count','halted','day'}
            and status['mode']=='LIVE_APPROVED' and status['pin']==row['pin'],'AUTHENTICATED_STATUS')
    require(all(status[k]==row['state'][k] and type(status[k]) is type(row['state'][k])
                for k in ('sequence','count','halted','day')),'AUTHENTICATED_STATE_CHANGED')

def _admissions(values, maximum, *, kind='nightly_review', preserved_nightly=()):
    require(kind in ('nightly_review', 'astra_turn'), 'ADMISSION_KIND_REQUIRED')
    require(isinstance(values,list) and 0<len(values)<=maximum,'BOUNDED_ADMISSIONS_REQUIRED')
    # Only exact originals from a separately reviewed recovery plan may carry
    # prior report work through terminal accounting. Never make it a review unit.
    if preserved_nightly:
        require(kind == 'astra_turn' and isinstance(preserved_nightly, list),
                'PINNED_PRIOR_REPORTS_REQUIRED')
        _admissions(preserved_nightly, maximum, kind='nightly_review')
        require(all(value in values for value in preserved_nightly),
                'PINNED_PRIOR_REPORT_NOT_IN_SUFFIX')
    result=[]
    for value in values:
        require(isinstance(value,dict) and set(value)=={'event_original','receipt_original'}
                and all(isinstance(v,str) for v in value.values()),'ADMISSION_ORIGINAL_SCHEMA')
        event=parsed(value['event_original']);receipt=parsed(value['receipt_original'])
        limiter.validate_server_event(event)
        require((event['kind']==kind or value in preserved_nightly)
                and receipt.get('status')=='ADMITTED'
                and receipt.get('duplicate_admission') is False,'ONLY_SUCCESSFUL_REVIEW_ADMISSION')
        pin(receipt.get('state_before'))
        require(re.fullmatch(r'\d{4}-\d{2}-\d{2}',receipt.get('day','')),'ADMISSION_DAY')
        result.append((event,receipt))
    require(len({(e['turn_id'],e['attempt']) for e,r in result})==len(result),'DUPLICATE_ADMISSION_KEY')
    return result

class _OneCAS:
    def __init__(self,pin,state):
        self.pin=pin;self.state=copy.deepcopy(state);self.result=None;self.calls=0
    def read(self):return self.pin,copy.deepcopy(self.state)
    def cas(self,old,state):
        require(old==self.pin and self.calls==0,'REPLAY_ONE_CAS')
        self.calls+=1;self.result=copy.deepcopy(state);return True

def _replay(objects, start, end, policy, admissions, *, kind='nightly_review',
            maximum=review.NATIVE_MAX_ATTEMPTS, preserved_nightly=()):
    values=_admissions(admissions,maximum,kind=kind, preserved_nightly=preserved_nightly)
    require(values[0][1]['state_before']==start,'FIRST_ADMISSION_BASELINE')
    backward=[];next_pin=end
    for _ in values:
        row=_state(objects,next_pin);require(row['parent'] is not None,'SUFFIX_PARENT_REQUIRED')
        backward.append(row);next_pin=row['parent']
    require(next_pin==start,'EXACT_SUFFIX_LENGTH')
    rows=list(reversed(backward));previous=_state(objects,start)
    for row,(event,receipt) in zip(rows,values):
        require(row['parent']==previous['pin'] and receipt['state_before']==previous['pin'],'ADMISSION_PARENT_CHANGED')
        store=_OneCAS(previous['pin'],previous['state'])
        day=datetime.strptime(receipt['day'],'%Y-%m-%d').replace(tzinfo=timezone.utc)
        replay=limiter.admit_server(store,policy,event,now=day,max_retries=1)
        require(replay==receipt and store.calls==1 and store.result==row['state'],'ORDINARY_ADMISSION_REPLAY')
        require(row['blob_raw']==(json.dumps(limiter.validate(store.result),sort_keys=True)+'\n').encode(),
                'ORDINARY_STATE_SERIALIZATION')
        previous=row
    return rows

def _bookkeeping(snapshot,head):
    originals=snapshot['control_originals'];pin(head)
    require(BOOKKEEPING<=set(originals),'MISSING_NATIVE_BOOKKEEPING')
    require(originals[TRACKING]==head+'\n','TRACKING_AUTHENTICATED_PIN')
    expected=head+"\t\t'"+head+"' of "+snapshot['remote'].removesuffix('.git')+'\n'
    require(originals['.git/FETCH_HEAD']==expected,'FETCH_HEAD_AUTHENTICATED_PIN')
    shallow=originals['.git/shallow'].splitlines()
    require(shallow==sorted(set(shallow)) and all(re.fullmatch(HEX,x) for x in shallow) and head in shallow,
            'SHALLOW_NATIVE_LAYOUT')
    require(all(x in snapshot['objects'] and snapshot['objects'][x]['type']=='commit' for x in shallow),
            'SHALLOW_MISSING_RAW_OBJECT')
    log=originals[REFLOG].splitlines(keepends=True)
    require(log and all(re.fullmatch(HEX+' '+HEX+' '+IDENTITY+r' [0-9]+ [+-][0-9]{4}\tupdate by push\n',x)
                       for x in log),'REFLOG_NATIVE_LAYOUT')
    require(log[-1].split()[1]==head,'REFLOG_CURRENT_PIN')
    return shallow,log

def _row_shape(row, file=False):
    keys={'uid','gid','mode','inode','device'}|({'bytes','sha256'} if file else set())
    require(isinstance(row,dict) and set(row)==keys,'INVENTORY_ROW')
    require(all(type(row[k]) is int and row[k]>=0 for k in keys-{'sha256'}),'INVENTORY_METADATA')
    if file:
        require(row['bytes']<=MAX_BYTES and re.fullmatch(r'[0-9a-f]{64}',row['sha256']),'INVENTORY_FILE_PIN')

def validate_baseline(baseline, policy=None):
    require(isinstance(baseline,dict) and set(baseline)=={'schema','policy_sha256','original_head',
            'authenticated_status','snapshot','canary_admissions','canary_commits'},
            'BASELINE_SCHEMA')
    require(baseline['schema']==SCHEMA and re.fullmatch(r'[0-9a-f]{64}',baseline['policy_sha256']),
            'BASELINE_VERSION')
    pin(baseline['original_head'])
    snap=baseline['snapshot']
    require(isinstance(snap,dict) and set(snap)=={'repository','remote','files','directories',
            'control_originals','objects','packs'},'BASELINE_SNAPSHOT')
    require(Path(snap['repository']).is_absolute() and '..' not in Path(snap['repository']).parts,
            'BASELINE_REPOSITORY')
    for key,file in (('files',True),('directories',False)):
        require(isinstance(snap[key],dict) and 0<len(snap[key])<=MAX_FILES,'BASELINE_INVENTORY')
        for name,row in snap[key].items():
            require(isinstance(name,str) and not Path(name).is_absolute()
                    and '..' not in Path(name).parts and str(Path(name))==name,'INVENTORY_PATH')
            _row_shape(row,file)
    require(isinstance(snap['objects'],dict) and 0<len(snap['objects'])<=MAX_OBJECTS,'BASELINE_OBJECTS')
    for oid,row in snap['objects'].items():
        pin(oid)
        require(isinstance(row,dict) and set(row)=={'type','bytes','sha256'}
                and row['type'] in ('blob','tree','commit') and type(row['bytes']) is int
                and 0<=row['bytes']<=1_500_000 and re.fullmatch(r'[0-9a-f]{64}',row['sha256']),
                'BASELINE_OBJECT_METADATA')
    require(isinstance(snap['control_originals'],dict)
            and set(snap['control_originals'])==BOOKKEEPING|{'.git/config','.git/HEAD'},'BASELINE_CONTROLS')
    for name,original in snap['control_originals'].items():
        require(isinstance(original,str) and name in snap['files'],'BASELINE_CONTROL_ORIGINAL')
        row=snap['files'][name]
        require(digest(original.encode())==row['sha256'] and len(original.encode())==row['bytes'],
                'BASELINE_CONTROL_HASH')
    require(isinstance(snap['packs'],dict),'BASELINE_PACKS')
    for stem,oids in snap['packs'].items():
        require(re.fullmatch(r'\.git/objects/pack/pack-'+HEX,stem)
                and isinstance(oids,list) and oids==sorted(set(oids))
                and set(oids)<=set(snap['objects'])
                and stem+'.pack' in snap['files'] and stem+'.idx' in snap['files'],'BASELINE_PACK_MEMBERSHIP')
    _bookkeeping(snap,baseline['original_head'])
    canaries=_admissions(baseline['canary_admissions'],2)
    require(len(canaries)==2 and isinstance(baseline['canary_commits'],list)
            and len(baseline['canary_commits'])==2
            and all(event['attempt']=='1' for event,receipt in canaries)
            and canaries[0][0]['turn_id']!=canaries[1][0]['turn_id']
            and canaries[0][0]['source']==canaries[1][0]['source'],
            'BOTH_CANARIES_BEFORE_BASELINE')
    previous=canaries[0][1]['state_before']
    for row,(event,receipt) in zip(baseline['canary_commits'],canaries):
        require(set(row)=={'pin','parent','tree','blob'} and row['parent']==previous
                and receipt['state_before']==previous,'CANARY_ORDER')
        for key,kind in (('pin','commit'),('tree','tree'),('blob','blob')):
            pin(row[key]);require(snap['objects'].get(row[key],{}).get('type')==kind,'CANARY_OBJECT_MISSING')
        previous=row['pin']
    require(previous==baseline['original_head'],'CANARIES_MUST_END_AT_BASELINE')
    if policy is not None:
        limiter.policy(policy)
        require(digest(encoded(policy))==baseline['policy_sha256'],'POLICY_CHANGED')
        require(_config(snap['control_originals']['.git/config'],policy)==snap['remote'],'REMOTE_CHANGED')
    return baseline

def _identities(rows):
    return [{k:row[k] for k in ('pin','parent','tree','blob')} for row in rows]

def capture_ledger(repo, policy, authenticated_status, canary_admissions):
    """Capture AFTER both validated canaries and authenticated status, under lock."""
    limiter.policy(policy)
    require(len(canary_admissions)==2,'BOTH_CANARIES_BEFORE_BASELINE')
    snap,objects=_snapshot(Path(repo),policy)
    head=pin(authenticated_status['pin']);row=_state(objects,head);_status(authenticated_status,row)
    _bookkeeping(snap,head)
    canaries=_admissions(canary_admissions,2)
    rows=_replay(objects,canaries[0][1]['state_before'],head,policy,canary_admissions)
    baseline={'schema':SCHEMA,'policy_sha256':digest(encoded(policy)),'original_head':head,
              'authenticated_status':copy.deepcopy(authenticated_status),'snapshot':snap,
              'canary_admissions':copy.deepcopy(canary_admissions),'canary_commits':_identities(rows)}
    validate_baseline(baseline,policy)
    return baseline

def _preservation(before,after,rows):
    old_files,new_files=before['files'],after['files']
    require(set(old_files)<=set(new_files),'PREEXISTING_FILE_REMOVED')
    for name,old in old_files.items():
        new=new_files[name]
        if name not in BOOKKEEPING:
            require(new==old,'PREEXISTING_FILE_CHANGED')
        else:
            metadata={'uid','gid','mode','device'}|({'inode'} if name in (REFLOG,'.git/FETCH_HEAD') else set())
            require(all(new[k]==old[k] for k in metadata),'BOOKKEEPING_METADATA_CHANGED')
    old_dirs,new_dirs=before['directories'],after['directories']
    require(set(old_dirs)<=set(new_dirs) and all(new_dirs[n]==v for n,v in old_dirs.items()),
            'PREEXISTING_DIRECTORY_CHANGED')
    require(set(before['objects'])<=set(after['objects']) and
            all(after['objects'][n]==v for n,v in before['objects'].items()),'PREEXISTING_OBJECT_CHANGED')
    closure={r[k] for r in rows for k in ('pin','tree','blob')}
    require(set(after['objects'])-set(before['objects'])<=closure,'UNRELATED_NEW_OBJECT')
    allowed_objects=set(before['objects'])|closure
    object_parent=old_dirs['.git/objects']
    added_files=sorted(set(new_files)-set(old_files))
    for name in added_files:
        row=new_files[name]
        require(row['uid']==object_parent['uid'] and row['gid']==object_parent['gid']
                and row['mode']==0o400,'NEW_OBJECT_METADATA')
        if re.fullmatch(r'\.git/objects/[0-9a-f]{2}/[0-9a-f]{38}',name):
            require(''.join(name.split('/')[-2:]) in allowed_objects,'UNRELATED_NEW_LOOSE_OBJECT')
        else:
            require(re.fullmatch(r'\.git/objects/pack/pack-'+HEX+r'\.(pack|idx)',name),'UNRELATED_NEW_FILE')
            stem=name.rsplit('.',1)[0]
            require(set(after['packs'][stem])<=allowed_objects,'UNRELATED_PACK_OBJECT')
    for name in set(new_dirs)-set(old_dirs):
        row=new_dirs[name]
        require(re.fullmatch(r'\.git/objects/[0-9a-f]{2}',name) or name=='.git/objects/pack',
                'UNRELATED_NEW_DIRECTORY')
        require(row['uid']==object_parent['uid'] and row['gid']==object_parent['gid']
                and row['mode'] in (0o700,0o2700)
                and any(n.startswith(name+'/') for n in added_files),'NEW_OBJECT_DIRECTORY_METADATA')
    old_shallow,old_log=_bookkeeping(before,rows[0]['parent'])
    new_shallow,new_log=_bookkeeping(after,rows[-1]['pin'])
    require(new_shallow==sorted(set(old_shallow)|{r['pin'] for r in rows}),'SHALLOW_UNEXPLAINED_CHANGE')
    require(new_log[:len(old_log)]==old_log and len(new_log)==len(old_log)+len(rows),'REFLOG_NOT_EXACT_SUFFIX')
    for text,row in zip(new_log[len(old_log):],rows):
        require(text.split()[:2]==[row['parent'],row['pin']],'REFLOG_UNRELATED_ADVANCE')
    return {'added_files':added_files,'added_objects':sorted(set(after['objects'])-set(before['objects'])),
            'changed_bookkeeping':sorted(n for n in BOOKKEEPING if old_files[n]!=new_files[n]),
            'added_directories':sorted(set(new_dirs)-set(old_dirs))}

def verify_transition(repo, baseline, policy, admissions, authenticated_status):
    """No fetch: caller authenticates once before this and fingerprints only after."""
    validate_baseline(baseline,policy)
    require(str(Path(repo))==baseline['snapshot']['repository'],'CONFIGURED_REPOSITORY_CHANGED')
    snap,objects=_snapshot(Path(repo),policy)
    head=pin(authenticated_status['pin']);_status(authenticated_status,_state(objects,head))
    _status(baseline['authenticated_status'],_state(objects,baseline['original_head']))
    # Revalidate original canary ordering against preserved immutable raw objects.
    start=_admissions(baseline['canary_admissions'],2)[0][1]['state_before']
    original_canaries=_replay(objects,start,baseline['original_head'],policy,baseline['canary_admissions'])
    require(_identities(original_canaries)==baseline['canary_commits'],'CANARY_PROOF_CHANGED')
    events=_admissions(admissions,review.NATIVE_MAX_ATTEMPTS)
    require(all(event['turn_id']==events[0][0]['turn_id']
                and event['source']==events[0][0]['source']
                and event['attempt']==str(index)
                for index,(event,receipt) in enumerate(events,1)),
            'ONLY_ONE_SEQUENTIAL_REVIEW_SESSION')
    rows=_replay(objects,baseline['original_head'],head,policy,admissions)
    changes=_preservation(baseline['snapshot'],snap,rows)
    # Pure replay cannot alter Git. The final local inventory closes read races;
    # no Git command or authenticated fetch occurs after this point.
    require(_inventory(Path(repo))=={k:snap[k] for k in ('files','directories','control_originals')},
            'FINAL_REPOSITORY_CAPTURE_MOVED')
    return {'schema':TRANSITION,'status':'VERIFIED_ONLY_APPROVED_SESSION_ADMISSIONS',
            'original_head':baseline['original_head'],'current_head':head,
            'baseline_sha256':digest(encoded(baseline)),'admissions_sha256':digest(encoded(admissions)),
            'authenticated_status_sha256':digest(encoded(authenticated_status)),
            'current_snapshot_sha256':digest(encoded(snap)),'suffix':_identities(rows),
            'repository_changes':changes,'git_mutations':0,'remote_calls':0,
            'caller_must_capture_full_state_after_return':True}


def verify_terminal_transition(repo, baseline, policy, admissions, authenticated_status, *,
                               preserved_admissions_count=0, server_profile=False,
                               preserved_nightly_admissions=()):
    """Preserve an existing capture across only already-validated manual charges.

    Explicit prior ordinary admissions may be pinned in the reviewed recovery
    plan; they remain distinct from manual units and must replay exactly.
    Prior nightly reports require their exact originals separately bound by that
    plan; a nonzero count alone never widens the terminal-unit kind.
    The caller first validates the terminal original journal/case mapping and
    authenticates current status. Historical canaries authenticate the original
    inventory only: this does not require or grant fresh native review coverage.
    """
    require(type(server_profile) is bool and type(preserved_admissions_count) is int and isinstance(admissions, list)
            and 0 <= preserved_admissions_count < len(admissions),
            'PRESERVED_ADMISSION_COUNT_REQUIRED')
    require(isinstance(preserved_nightly_admissions, (list, tuple))
            and len(preserved_nightly_admissions) <= preserved_admissions_count,
            'PINNED_PRIOR_REPORT_COUNT_REQUIRED')
    validate_baseline(baseline, policy)
    require(str(Path(repo)) == baseline['snapshot']['repository'], 'CONFIGURED_REPOSITORY_CHANGED')
    snap, objects = _snapshot(Path(repo), policy)
    head = pin(authenticated_status['pin']); current = _state(objects, head)
    _status(authenticated_status, current)
    require(current['state']['halted'] is False, 'TERMINAL_ACCOUNTING_HALT_REMAINS')
    _status(baseline['authenticated_status'], _state(objects, baseline['original_head']))
    start = _admissions(baseline['canary_admissions'], 2)[0][1]['state_before']
    canaries = _replay(objects, start, baseline['original_head'], policy, baseline['canary_admissions'])
    require(_identities(canaries) == baseline['canary_commits'], 'CANARY_PROOF_CHANGED')
    events = _admissions(admissions, MAX_OBJECTS, kind='astra_turn',
                         preserved_nightly=preserved_nightly_admissions)
    require(all(event['attempt'] == '1' or server_profile
            and event['attempt'].isdigit() and 1 <= int(event['attempt']) <= 16 for event, receipt in events),
            'ONLY_ORIGINAL_TERMINAL_ACCOUNTING_UNITS')
    rows = _replay(objects, baseline['original_head'], head, policy, admissions,
                   kind='astra_turn', maximum=MAX_OBJECTS,
                   preserved_nightly=preserved_nightly_admissions)
    changes = _preservation(baseline['snapshot'], snap, rows)
    require(_inventory(Path(repo)) == {k: snap[k] for k in ('files','directories','control_originals')},
            'FINAL_REPOSITORY_CAPTURE_MOVED')
    return {'schema': 'terminal-accounting-ledger-transition/v1',
            **({'server_profile': True} if server_profile else {}),
            'status': ('VERIFIED_TERMINAL_AND_PINNED_PRIOR_ADMISSIONS' if preserved_admissions_count
                       else 'VERIFIED_ONLY_TERMINAL_ACCOUNTING_ADMISSIONS'),
            **({'preserved_admissions_count': preserved_admissions_count} if preserved_admissions_count else {}),
            'original_head': baseline['original_head'], 'current_head': head,
            'baseline_sha256': digest(encoded(baseline)), 'admissions_sha256': digest(encoded(admissions)),
            **({'preserved_nightly_admissions_sha256': digest(encoded(preserved_nightly_admissions))}
               if preserved_nightly_admissions else {}),
            'authenticated_status_sha256': digest(encoded(authenticated_status)),
            'current_snapshot_sha256': digest(encoded(snap)), 'suffix': _identities(rows),
            'repository_changes': changes, 'git_mutations': 0, 'remote_calls': 0,
            'caller_must_capture_full_state_after_return': True}
