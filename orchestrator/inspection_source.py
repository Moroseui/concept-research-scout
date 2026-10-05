"""Prepare an immutable, content-checked source view; never expose a checkout HOME.

The private originals remain in Git/evidence storage. Exclusions are explicit and
cannot satisfy a review obligation. There is no credential, Git configuration,
patient-output or arbitrary server-filesystem mount in the resulting view.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess

from orchestrator.git_publication import scan, scan_commit


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def safe_name(name):
    if not isinstance(name, str):
        raise ValueError('INSPECTION_RELATIVE_PATH_REQUIRED')
    path = PurePosixPath(name)
    if (path.is_absolute() or '..' in path.parts
            or path.as_posix() != name or not name or '\\' in name
            or any(ord(c) < 32 for c in name)):
        raise ValueError('INSPECTION_RELATIVE_PATH_REQUIRED')
    return name


def checked_text(name, raw):
    """Known text metadata aliases change scan names only, never content bytes."""
    safe_name(name)
    suffix = Path(name).suffix
    metadata = name in {'.gitignore', '.gitattributes', '.python-version'}
    template = name.startswith('deploy/research-system/') and name.endswith('.service.in')
    if metadata:
        scan('source-metadata.txt', raw)
    elif template:
        scan(name[:-3], raw)
    elif suffix in {'.csv', '.lock'} and name != 'deploy/research-system/drive-requirements.lock':
        # Unsupported artifacts remain excluded; this is not a new export rule.
        raise ValueError('INSPECTION_UNSUPPORTED_TEXT_ARTIFACT')
    else:
        scan(name, raw)
    return raw


def write_once(path, raw):
    path = Path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o400)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def prepare(root, source, destination, *, evidence=(), history=()):
    """Copy all eligible tracked files, with optional pinned history/evidence.

    Evidence entries are trusted preparation inputs with source path, SHA and
    public-safe label, not reviewer-selected filesystem paths. History is an
    explicit fixed commit inventory; every eligible original version is readable.
    Any rejected original is identified by its hash and reason, without quoting
    a potentially identifying pathname or content.
    """
    root = Path(root).resolve()
    destination = Path(destination).absolute()
    from orchestrator.inspection_access import no_symlinks, read_regular
    no_symlinks(destination)
    if destination.exists() or destination.is_symlink() or destination.is_relative_to(root):
        raise ValueError('FRESH_EXTERNAL_INSPECTION_VIEW_REQUIRED')
    if not re.fullmatch('[0-9a-f]{40}', source):
        raise ValueError('INSPECTION_EXACT_SOURCE_REQUIRED')

    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root)

    if git('rev-parse', 'HEAD').decode().strip() != source or git('status', '--porcelain'):
        raise ValueError('INSPECTION_CLEAN_FIXED_SOURCE_REQUIRED')
    commits = list(history)
    if len(commits) > 1024 or len(set(commits)) != len(commits):
        raise ValueError('INSPECTION_FIXED_HISTORY_REQUIRED')
    if any(not re.fullmatch('[0-9a-f]{40}', value) for value in commits):
        raise ValueError('INSPECTION_EXACT_HISTORY_REQUIRED')
    destination.mkdir(mode=0o700, parents=True)
    files, excluded, total = {}, [], 0

    def copy(name, raw, origin):
        nonlocal total
        safe_name(name)
        # The original source pathname was checked above. Prefixing it with a
        # view namespace must not alter the fixed metadata/template scan alias.
        scan('review-text.txt', raw)
        # The access manifest allows 4,000 entries including VIEW.json itself.
        if total + len(raw) > 150_000_000 or len(files) >= 3999:
            raise ValueError('INSPECTION_VIEW_CAPACITY_REQUIRES_SCOPING')
        write_once(destination / name, raw)
        files[name] = {'sha256': sha(raw), 'bytes': len(raw),
                       'lines': len(raw.decode('utf-8').splitlines()), 'origin': origin}
        total += len(raw)

    for commit in [source, *[v for v in commits if v != source]]:
        prefix = 'source/' if commit == source else 'history/' + commit + '/'
        entries = git('ls-tree', '-r', '-z', commit).split(b'\0')
        for entry in entries:
            if not entry:
                continue
            metadata, name_raw = entry.split(b'\t', 1)
            mode, kind, oid = metadata.decode().split()
            name = name_raw.decode()
            identity = {'commit': commit, 'path_sha256': sha(name_raw), 'object': oid}
            if mode not in {'100644', '100755'} or kind != 'blob':
                excluded.append({**identity, 'reason': 'NON_REGULAR_SOURCE'})
                continue
            size = int(git('cat-file', '-s', oid))
            if size > 1500000:
                excluded.append({**identity, 'bytes': size, 'reason': 'SOURCE_FILE_TOO_LARGE'})
                continue
            raw = git('cat-file', 'blob', oid)
            try:
                checked_text(name, raw)
            except (ValueError, UnicodeError) as error:
                excluded.append({**identity, 'sha256': sha(raw), 'reason': type(error).__name__ + ':' + str(error).split('\n')[0][:100]})
                continue
            copy(prefix + name, raw, {**identity, 'original_path': name, 'transformation': 'NONE'})
        metadata = git('cat-file', 'commit', commit)
        try:
            scan_commit(metadata)
        except ValueError:
            excluded.append({'commit': commit, 'sha256': sha(metadata), 'reason': 'COMMIT_METADATA_BOUNDARY'})
        else:
            copy('history/' + commit + '/commit.txt', metadata,
                 {'commit': commit, 'transformation': 'NONE', 'kind': 'git_commit_object'})

    for item in evidence:
        if set(item) != {'path', 'sha256', 'name'}:
            raise ValueError('INSPECTION_PINNED_EVIDENCE_REQUIRED')
        path = Path(item['path'])
        no_symlinks(path)
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 1500000:
            raise ValueError('INSPECTION_EVIDENCE_ORIGINAL_REQUIRED')
        raw = read_regular(path, 1500000)
        if sha(raw) != item['sha256']:
            raise ValueError('INSPECTION_EVIDENCE_CHANGED')
        name = 'evidence/' + safe_name(item['name'])
        checked_text(name, raw)
        copy(name, raw, {'original_sha256': sha(raw), 'transformation': 'NONE',
                         'kind': 'permitted_private_evidence'})
    manifest = {'schema': 'inspection-source-view/v1', 'source': source,
                'history_commits': commits, 'files': files, 'excluded': excluded,
                'bytes': total, 'availability_is_inspection': False}
    write_once(destination / 'VIEW.json', encoded(manifest))
    for path in sorted(destination.rglob('*'), reverse=True):
        if path.is_dir():
            path.chmod(0o500)
    destination.chmod(0o500)
    return manifest
