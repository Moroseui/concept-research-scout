"""Explicit source-complete subset provenance; no rewriting retained artifacts."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from orchestrator.publication import inventory


def verify(repo, bundle, declaration, source_commit, contract_blob, required, expected_source_dir=None):
    raw=Path(declaration).read_bytes(); doc=json.loads(raw)
    if doc.get('schema_version') != 1 or doc.get('source_commit') != source_commit or doc.get('contract_blob') != contract_blob:
        raise ValueError('subset source/contract identity mismatch')
    if not re.fullmatch('[0-9a-f]{40}', source_commit or ''):
        raise ValueError('subset requires full source commit pin')
    source_dir=doc['source_dir']; p=PurePosixPath(source_dir)
    if expected_source_dir is not None and source_dir != expected_source_dir:
        raise ValueError('subset source directory mismatch')
    if p.is_absolute() or '..' in p.parts or str(p)!=source_dir:
        raise ValueError('unsafe source directory')
    def git(*a):
        return subprocess.check_output(['git',*a],cwd=repo)
    source={}
    for row in git('ls-tree','-rz',source_commit,'--',source_dir).split(b'\0'):
        if not row: continue
        meta,name=row.split(b'\t'); mode,kind,blob=meta.decode().split()
        if mode not in ('100644','100755') or kind!='blob':
            raise ValueError('nonregular source artifact')
        name=name.decode(); prefix=source_dir+'/'
        if not name.startswith(prefix): raise ValueError('source containment mismatch')
        source[name[len(prefix):]]=hashlib.sha256(git('cat-file','blob',blob)).hexdigest()
    retained=doc['retained']; excluded=doc['excluded']
    if not source or set(retained)&set(excluded) or set(source)!=set(retained)|set(excluded):
        raise ValueError('every source file must have exactly one disposition')
    if not set(required)<=set(retained):
        raise ValueError('required scientific/audit outputs cannot be excluded')
    if inventory(bundle)!=retained:
        raise ValueError('retained bytes or file set differs from declaration')
    for name,sha in retained.items():
        if source[name]!=sha: raise ValueError('retained bytes differ from pinned source')
    for name,entry in excluded.items():
        if not name.startswith('staged/'):
            raise ValueError('only staged inputs may be excluded; audit dispositions need separate adjudication')
        if entry.get('sha256')!=source[name] or not entry.get('reason') or not entry.get('decision_ref'):
            raise ValueError('exclusion lacks byte-bound reason/decision reference')
        if entry.get('disposition')!='private-original-preserved':
            raise ValueError('unsupported exclusion disposition')
        evidence=Path(entry['private_evidence_path'])
        if evidence.is_symlink() or not evidence.is_file() or hashlib.sha256(evidence.read_bytes()).hexdigest()!=source[name]:
            raise ValueError('original excluded evidence unavailable or changed')
    # Only digest/counts enter public import receipt; private paths remain private.
    return {'declaration_sha256':hashlib.sha256(raw).hexdigest(),
            'source_commit':source_commit,'source_dir':source_dir,
            'source_file_count':len(source),'retained_file_count':len(retained),
            'excluded_file_count':len(excluded),'dispositions_verified':True}
