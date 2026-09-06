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
TEXT_SUFFIXES = {'.py','.md','.json','.jsonl','.yml','.yaml','.toml','.txt','.fish','.ipynb'}


def git(root, *args, **kw):
    return subprocess.check_output(['git', *args], cwd=root, **kw)


def scan(name, data):
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
    if p.suffix in {'.json','.jsonl','.txt'} and re.search(rb'sub[-_]stroke[0-9]+',data,re.I):
        raise ValueError('CASE_LEVEL_RECORD_REJECTED')
    if p.suffix == '.ipynb':
        nb = json.loads(data)
        if any(c.get('outputs') or c.get('execution_count') is not None for c in nb['cells']):
            raise ValueError('NOTEBOOK_OUTPUT_REJECTED')


def scan_commit(data):
    if len(data)>500000 or SECRET.search(data) or re.search(rb'sub[-_]stroke[0-9]+',data,re.I):
        raise ValueError('COMMIT_METADATA_REJECTED')


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
        if not subprocess.run(['git','merge-base','--is-ancestor',CONTAMINATED,source],cwd=root,capture_output=True).returncode:
            raise ValueError('CONTAMINATED_HISTORY_REJECTED')
    observed = {}
    for commit in git(root,'rev-list',before+'..'+source).decode().splitlines():
        scan_commit(git(root,'cat-file','commit',commit))
        # -m includes changes relative to each parent: side history is never hidden.
        names = set(git(root,'diff-tree','--root','-m','--no-commit-id','--name-only','-r','-z',commit).split(b'\0'))
        for raw in sorted(names):
            if not raw: continue
            name = raw.decode()
            entry = git(root,'ls-tree',commit,'--',name)
            if not entry: continue
            if entry.split()[0] not in (b'100644',b'100755'):
                raise ValueError('NON_REGULAR_PUBLICATION')
            data = git(root,'show',commit+':'+name)
            scan(name,data)
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
    remote = git(root,'ls-remote','origin',ref).decode().split()
    if remote != [before,ref]: raise ValueError('REMOTE_MOVED')
    subprocess.run(['git','push','--force-with-lease='+ref+':'+before,'origin',source+':'+ref],cwd=root,check=True)
    return {**receipt,'destination':destination,'operation':'append_only_compare_and_swap'}


def checkpoint(root, request_path):
    """Existing CI checkpoint route: only explicitly bound, audited pilot writes.

Broader grants remain a governance decision, not an environment-variable bypass.
"""
    if not request_path: raise ValueError('CHECKPOINT_PUBLICATION_BINDING_REQUIRED')
    req = json.loads(Path(request_path).read_text())
    if req['destination'] != PILOT: raise ValueError('DESTINATION_NOT_AUTHORIZED')
    from scripts.workflow_boundary import publish as pilot_publish
    return pilot_publish(root,req['source'],req['destination'],req['before'])
