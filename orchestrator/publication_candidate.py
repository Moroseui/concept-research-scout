"""Stage a bounded candidate in a protected cache before credentialed publication.

The sender supplies a Git bundle and full outgoing inventory. Neither is trusted:
the receiver audits every newly reachable commit/blob using the existing policy.
No source-controlled hooks execute and no credential is used by this module.
The cache and baseline must be prepared by the protected service, not selected by
the request. Publication and current remote-ref verification remain separate.
"""
import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile

from orchestrator.git_publication import audit

LIMIT=1000000


def git(root,*args):
    env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','GIT_CONFIG_NOSYSTEM':'1',
         'GIT_CONFIG_GLOBAL':'/dev/null','GIT_TERMINAL_PROMPT':'0','GIT_NO_LAZY_FETCH':'1'}
    try:
        return subprocess.check_output(['git','-c','core.hooksPath=/dev/null',
            '-c','credential.helper=',*args],cwd=root,env=env,stderr=subprocess.PIPE,timeout=60)
    except subprocess.TimeoutExpired:raise ValueError('CANDIDATE_GIT_TIMEOUT') from None
    except subprocess.CalledProcessError:
        code={'cat-file':'CANDIDATE_GIT_OBJECT_UNAVAILABLE','bundle':'CANDIDATE_BUNDLE_INVALID'}.get(args[0],'CANDIDATE_GIT_OPERATION_FAILED')
        raise ValueError(code) from None


def pins(source,before):
    if not all(isinstance(p,str) and re.fullmatch('[0-9a-f]{40}',p) for p in (source,before)):
        raise ValueError('EXACT_CANDIDATE_PINS_REQUIRED')


def sparse_paths(entries):
    paths=sorted({name.split(':',1)[1] for name in entries})
    if not paths:raise ValueError('EMPTY_CANDIDATE')
    if any(path!=path.strip() or any(c in path for c in '*?[]\\\n\r') for path in paths):
        raise ValueError('LITERAL_SPARSE_PATH_REQUIRED')
    return paths


def inventory(root,source,before):
    pins(source,before);result={}
    for commit in git(root,'rev-list',before+'..'+source).decode().splitlines():
        names=set(git(root,'diff-tree','--root','-m','--no-commit-id','--name-only','-r','-z',commit).split(b'\0'))
        tree={entry.split(b'\t',1)[1]:entry.split(b'\t',1)[0].split()
              for entry in git(root,'ls-tree','-r','-z',commit).split(b'\0') if entry}
        for name in names:
            if name in tree:
                raw=git(root,'cat-file','blob',tree[name][2].decode())
                result[commit+':'+name.decode()]=hashlib.sha256(raw).hexdigest()
    audit(root,source,before,result)
    return result


def prepare(root,source,before,destination):
    pins(source,before);root=Path(root).resolve();destination=Path(destination).absolute()
    if destination.exists() or destination.is_symlink() or destination.resolve().is_relative_to(root.resolve()):
        raise ValueError('FRESH_EXTERNAL_BUNDLE_REQUIRED')
    if git(root,'rev-parse','HEAD').decode().strip()!=source or git(root,'status','--porcelain'):
        raise ValueError('CLEAN_BOUND_SOURCE_REQUIRED')
    entries=inventory(root,source,before)
    sparse_paths(entries)
    staging=Path(tempfile.mkdtemp(prefix='bundle-preparation-',dir=destination.parent))
    bundle=staging/'source.bundle'
    git(root,'bundle','create',str(bundle),'HEAD','^'+before)
    raw=bundle.read_bytes();bundle.chmod(0o600)
    if len(raw)>LIMIT:raise ValueError('CANDIDATE_BUNDLE_LIMIT')
    try:os.link(bundle,destination)
    except FileExistsError:raise ValueError('FRESH_EXTERNAL_BUNDLE_REQUIRED') from None
    except OSError:raise ValueError('CANDIDATE_BUNDLE_LINK_FAILED_OR_UNSUPPORTED') from None
    return {'source':source,'before':before,'inventory':entries,
            'bundle_sha256':hashlib.sha256(raw).hexdigest()}


def receive(cache,source,before,entries,raw,expected_sha256):
    """Inspect in the fixed private cache; no Git push or remote fetch occurs."""
    pins(source,before);cache=Path(cache).absolute()
    if any(p.is_symlink() for p in (cache,*cache.parents)) or (cache/'.git').is_symlink() or not (cache/'.git').is_dir():
        raise ValueError('DEDICATED_PROTECTED_CACHE_REQUIRED')
    if (cache/'.git/objects/info/alternates').exists() or any(
            p.is_symlink() or (p.is_file() and p.stat().st_nlink!=1) for p in (cache/'.git/objects').rglob('*')):
        raise ValueError('INDEPENDENT_CACHE_OBJECTS_REQUIRED')
    if not isinstance(raw,bytes) or len(raw)>LIMIT or hashlib.sha256(raw).hexdigest()!=expected_sha256:
        raise ValueError('CANDIDATE_BUNDLE_CHANGED_OR_OVERSIZE')
    git(cache,'cat-file','-e',before+'^{commit}')
    # Keep each incoming bundle on failure for private reconciliation.
    incoming=Path(tempfile.mkdtemp(prefix='candidate-',dir=cache.parent))
    bundle=incoming/'candidate.bundle';bundle.write_bytes(raw);bundle.chmod(0o600)
    heads=git(cache,'bundle','list-heads',str(bundle)).decode().splitlines()
    if heads!=[source+' HEAD']:raise ValueError('CANDIDATE_BUNDLE_HEADS')
    git(cache,'bundle','verify',str(bundle))
    git(cache,'fetch','--no-tags',str(bundle),'HEAD')
    receipt=audit(cache,source,before,entries)
    # Audit precedes checkout: forbidden symlinks or source blobs cannot be staged
    # by an unchecked sender. Sparse checkout avoids materializing legacy data.
    paths=sparse_paths(entries)
    git(cache,'sparse-checkout','set','--no-cone',*('/'+p for p in paths))
    git(cache,'checkout','--detach',source)
    if git(cache,'status','--porcelain'):raise ValueError('CANDIDATE_CACHE_DIRTY')
    return {**receipt,'bundle_sha256':expected_sha256,'status':'STAGED_NOT_PUBLISHED'}
