"""Controlled append-only Git publication; credential holders can bypass this API.

A request is a byte inventory, not an operator signature. Production authority is
separate and currently permits only the pilot implementation destination.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

CONTAMINATED = '940293b6d562f2d3dd6bfd9d8d8281ccf01e4783'
PILOT = 'astra/autonomous-isles-pilot'
SECRET = re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN (?:(?:RSA |OPENSSH |EC |DSA |ENCRYPTED )?PRIVATE KEY|PGP PRIVATE KEY BLOCK)-----)')
TEXT_SUFFIXES = {'.py','.md','.json','.jsonl','.yml','.yaml','.toml','.txt','.fish','.ipynb','.sh','.service','.timer'}


def git(root, *args, **kw):
    return subprocess.check_output(['git', *args], cwd=root, **kw)


def scan(name, data):
    if SECRET.search(name.encode()) or re.search(r'sub[-_]stroke[0-9]+',name,re.I) or any(ord(c)<32 for c in name):raise ValueError('PUBLICATION_PATH_CONTENT_REJECTED')
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or p.as_posix() != name or any(x.startswith('.') and x != '.github' for x in p.parts):
        raise ValueError('PUBLICATION_PATH_REJECTED')
    public_docs={'docs/isles-pilot/PRIVATE_COORDINATOR_PLAN.md','docs/isles-pilot/PRIVATE_COORDINATOR_SETUP.fish'}
    private_path=any(x.lower().startswith(('staged','private','raw_patient')) for x in p.parts)
    if p.suffix not in TEXT_SUFFIXES or (private_path and name not in public_docs):
        raise ValueError('PUBLICATION_TYPE_REJECTED')
    if len(data) > 1500000 or b'\0' in data or SECRET.search(data):
        raise ValueError('PUBLICATION_CONTENT_REJECTED')
    data.decode('utf-8')
    if re.search(rb'sub[-_]stroke[0-9]+',data,re.I):
        raise ValueError('CASE_LEVEL_RECORD_REJECTED')
    if p.suffix == '.ipynb':
        nb = json.loads(data)
        if any(c.get('outputs') or c.get('execution_count') is not None for c in nb['cells']):
            raise ValueError('NOTEBOOK_OUTPUT_REJECTED')


def scan_commit(data):
    if len(data)>500000 or SECRET.search(data) or re.search(rb'sub[-_]stroke[0-9]+',data,re.I):
        raise ValueError('COMMIT_METADATA_REJECTED')


# Existing public evidence is preserved byte-for-byte; only this pinned prefix is
# grandfathered, plus one exact public test line below. No general case-data
# exception or results route is introduced.
PUBLIC_DECISION_BASELINE = '2cb97cec43a07b3ab908329d38c509215237081f'
PUBLIC_DECISION_SHA256 = 'dbb96211221407b5e13218a5e8c043afcf178700ee992aebab6479f95001ee7c'

PUBLIC_FIXTURE_SHA256 = '2e63b621c00522b27ffa7228c754976834c076651e6248e7f90e8fc8d83149ff'

SYNTHETIC_REPORT_TEST_SHA256 = '46aa7a14b8390cc16562f21863fb1c80499c73441209f3b727b50b8e00424b3d'
SYNTHETIC_REPORT_TEST_VERSIONS = {SYNTHETIC_REPORT_TEST_SHA256,
    '159246c86201491334dc3e18cb9ba9198ae21edeedf1c7a67c9b7e4ad7adedaf'}

# Exact reviewed synthetic rejection test; no general Python or case-record exemption.
HUMAN_CONTROL_SYNTHETIC_FIXTURE_SHA256 = '9a50b783e8e19cc1107cb22bd10c1157e27577afaa269666416ff86430337dc1'

def scan_history_blob(root, before, name, data):
    try:
        scan(name,data)
    except ValueError as error:
        if str(error)=='CASE_LEVEL_RECORD_REJECTED' and name=='tests/test_human_controls.py' and hashlib.sha256(data).hexdigest()==HUMAN_CONTROL_SYNTHETIC_FIXTURE_SHA256:
            scan(name,re.sub(rb'sub[-_]stroke[0-9]+',b'SYNTHETIC_REJECTION_FIXTURE',data,flags=re.I));return
        if str(error)=='CASE_LEVEL_RECORD_REJECTED' and name=='tests/test_operations_report.py' and hashlib.sha256(data).hexdigest() in SYNTHETIC_REPORT_TEST_VERSIONS:
            # Exact synthetic rejection fixtures, reviewed at 1900522 and 460deab; no patient input.
            scan(name,re.sub(rb'sub[-_]stroke[0-9]+',b'SYNTHETIC_REJECTION_FIXTURE',data,flags=re.I));return
        if str(error)!='CASE_LEVEL_RECORD_REJECTED' or name not in {'evidence/decisions.md','tests/test_git_publication.py'}:raise
        if subprocess.run(['git','merge-base','--is-ancestor',PUBLIC_DECISION_BASELINE,before],cwd=root,capture_output=True).returncode:raise
        original=git(root,'show',PUBLIC_DECISION_BASELINE+':'+name)
        if name=='evidence/decisions.md':
            if hashlib.sha256(original).hexdigest()!=PUBLIC_DECISION_SHA256 or not original.endswith(b'\n') or not data.startswith(original):raise
            historical=re.sub(rb'sub[-_]stroke[0-9]+',b'PUBLIC_HISTORICAL_IDENTIFIER',original,flags=re.I)
            scan(name,historical+data[len(original):])
        else:
            # One already-public synthetic test line survives in preserved commits.
            # No general Python exemption; final source splits the fixture literal.
            if hashlib.sha256(original).hexdigest()!=PUBLIC_FIXTURE_SHA256:raise
            lines=[line for line in original.splitlines(keepends=True) if re.search(rb'sub[-_]stroke[0-9]+',line,re.I)]
            if len(lines)!=1 or not lines[0].endswith(b'\n') or data.count(lines[0])!=1:raise
            scan(name,data.replace(lines[0],b'PUBLIC_HISTORICAL_TEST_FIXTURE\n',1))



def audit(root, source, before, inventory):
    """Every newly reachable commit/blob, including files deleted before the tip.

Inventory keys are commit:path and values exact SHA256. This explicit inventory
must be reviewed by the caller; matching hashes alone are not a privacy review.
"""
    if not all(re.fullmatch('[0-9a-f]{40}', x) for x in [source,before]):
        raise ValueError('EXACT_PINS_REQUIRED')
    if subprocess.run(['git','merge-base','--is-ancestor',before,source],cwd=root,capture_output=True).returncode:
        raise ValueError('NON_FAST_FORWARD_REJECTED')
    # cat-file first: an absent known bad object does not itself invalidate a clean repo.
    if not subprocess.run(['git','cat-file','-e',CONTAMINATED+'^{commit}'],cwd=root,capture_output=True).returncode:
        ancestry=subprocess.run(['git','merge-base','--is-ancestor',CONTAMINATED,source],cwd=root,capture_output=True).returncode
        if ancestry==0:raise ValueError('CONTAMINATED_HISTORY_REJECTED')
        if ancestry!=1:raise ValueError('CONTAMINATED_ANCESTRY_UNAVAILABLE')
    observed = {}
    for commit in git(root,'rev-list',before+'..'+source).decode().splitlines():
        scan_commit(git(root,'cat-file','commit',commit))
        # -m includes changes relative to each parent: side history is never hidden.
        tree={}
        for entry in git(root,'ls-tree','-r','-z',commit).split(b'\0'):
            if entry:
                metadata,name=entry.split(b'\t',1);tree[name]=metadata.split()
        names = set(git(root,'diff-tree','--root','-m','--no-commit-id','--name-only','-r','-z',commit).split(b'\0'))
        for raw in sorted(names):
            if not raw: continue
            name = raw.decode()
            entry = tree.get(raw)
            # Byte-exact membership: absence means a real deletion, not a path glob.
            if entry is None: continue
            if entry[0] not in (b'100644',b'100755'):
                raise ValueError('NON_REGULAR_PUBLICATION')
            data = git(root,'cat-file','blob',entry[2].decode())
            scan_history_blob(root,before,name,data)
            observed[commit+':'+name] = hashlib.sha256(data).hexdigest()
    if observed != inventory:
        raise ValueError('OUTGOING_INVENTORY_MISMATCH')
    return {'source':source,'before':before,'blob_versions':len(observed),
            'inventory_sha256':hashlib.sha256(json.dumps(observed,sort_keys=True).encode()).hexdigest()}


def publish(root, request, authority=None):
    """No implicit branch inference, rebasing, force rewrite, or credential change.

The production wrapper supplies the existing pilot authority. Other destinations
are supported only with an externally supplied, exact operation grant; this
function does not authenticate a human signer or create such a grant.
"""
    if request.get('operation') == 'create':
        return create(root, request, authority)
    if 'operation' in request:
        raise ValueError('UNSUPPORTED_PUBLICATION_OPERATION')
    source,before,destination = (request[k] for k in ['source','before','destination'])
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./-]*',destination) or '..' in destination:
        raise ValueError('INVALID_DESTINATION')
    expected = {'source':source,'before':before,'destination':destination,'remote':request['remote']}
    if authority != expected:
        raise ValueError('EXACT_OPERATION_AUTHORITY_REQUIRED')
    if git(root,'rev-parse','HEAD').decode().strip()!=source or git(root,'status','--porcelain').strip():
        raise ValueError('CLEAN_BOUND_SOURCE_REQUIRED')
    if git(root,'remote','get-url','origin').decode().strip()!=request['remote']:
        raise ValueError('REMOTE_IDENTITY_CHANGED')
    receipt = audit(root,source,before,request['inventory'])
    ref = 'refs/heads/'+destination
    remote = git(root,'ls-remote',request['remote'],ref).decode().split()
    if remote != [before,ref]: raise ValueError('REMOTE_MOVED')
    subprocess.run(['git','push','--force-with-lease='+ref+':'+before,request['remote'],source+':'+ref],cwd=root,check=True)
    return {**receipt,'destination':destination,'operation':'append_only_compare_and_swap'}


def create(root, request, authority=None):
    """Create exactly one absent ref, auditing from a separately public baseline.

    An empty expected-old lease is checked atomically by receive-pack. A porcelain
    creation result is also required: an already-identical ref can otherwise be
    reported up-to-date without testing a lease. No update fallback is permitted.
    """
    bindings = {'operation', 'source', 'audit_baseline', 'baseline_ref',
                'destination', 'remote', 'expected_destination'}
    if set(request) != bindings | {'inventory'}:
        raise ValueError('EXACT_CREATION_FIELDS_REQUIRED')
    if authority != {k: request[k] for k in bindings}:
        raise ValueError('EXACT_OPERATION_AUTHORITY_REQUIRED')
    if request['operation'] != 'create' or request['expected_destination'] != 'absent':
        raise ValueError('EXPECTED_ABSENCE_REQUIRED')
    source, baseline = request['source'], request['audit_baseline']
    if not all(isinstance(x, str) and re.fullmatch('[0-9a-f]{40}', x)
               for x in (source, baseline)):
        raise ValueError('EXACT_PINS_REQUIRED')
    destination, baseline_ref, remote = (request[k] for k in
                                       ('destination', 'baseline_ref', 'remote'))
    if not isinstance(destination, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./-]*', destination):
        raise ValueError('INVALID_DESTINATION')
    ref = 'refs/heads/' + destination
    if not isinstance(baseline_ref, str) or not baseline_ref.startswith('refs/heads/'):
        raise ValueError('INVALID_BASELINE_REF')
    for name in (ref, baseline_ref):
        if subprocess.run(['git', 'check-ref-format', name], cwd=root,
                          capture_output=True).returncode:
            raise ValueError('INVALID_PUBLICATION_REF')
    if git(root, 'rev-parse', 'HEAD').decode().strip() != source or git(root, 'status', '--porcelain').strip():
        raise ValueError('CLEAN_BOUND_SOURCE_REQUIRED')
    if git(root, 'remote', 'get-url', 'origin').decode().strip() != remote:
        raise ValueError('REMOTE_IDENTITY_CHANGED')
    # Use the bound repository directly, not an independently configurable pushurl.
    if git(root, 'ls-remote', remote, baseline_ref).decode().split() != [baseline, baseline_ref]:
        raise ValueError('PUBLIC_AUDIT_BASELINE_CHANGED')
    receipt = audit(root, source, baseline, request['inventory'])
    if git(root, 'ls-remote', remote, ref).strip():
        raise ValueError('DESTINATION_ALREADY_EXISTS')
    output = git(root, 'push', '--porcelain', '--force-with-lease=' + ref + ':',
                 remote, source + ':' + ref).decode()
    statuses = [line.split('\t') for line in output.splitlines() if '\t' in line]
    if len(statuses) != 1 or statuses[0][0] != '*' or statuses[0][1] != source + ':' + ref:
        raise ValueError('DESTINATION_NOT_CREATED')
    if git(root, 'ls-remote', remote, ref).decode().split() != [source, ref]:
        raise ValueError('CREATED_DESTINATION_VERIFICATION_FAILED')
    return {'source': source, 'audit_baseline': baseline, 'baseline_ref': baseline_ref,
            'remote': remote, 'destination': destination, 'expected_destination': 'absent',
            'operation': 'create_if_absent', 'blob_versions': receipt['blob_versions'],
            'inventory_sha256': receipt['inventory_sha256'], 'remote_verified': True}


def checkpoint(root, request_path):
    """Existing CI checkpoint route: only explicitly bound, audited pilot writes.

Broader grants remain a governance decision, not an environment-variable bypass.
"""
    if not request_path: raise ValueError('CHECKPOINT_PUBLICATION_BINDING_REQUIRED')
    req = json.loads(Path(request_path).read_text())
    if req['destination'] != PILOT: raise ValueError('DESTINATION_NOT_AUTHORIZED')
    from scripts.workflow_boundary import publish as pilot_publish
    return pilot_publish(root,req['source'],req['destination'],req['before'])
