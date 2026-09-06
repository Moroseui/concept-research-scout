"""Fail-closed, byte-checked publication boundary. No implicit recursive publishing."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys


def inventory(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('publication root must be a real directory')
    files = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise ValueError('symlinks are not publishable')
        if p.is_dir():
            continue
        if not p.is_file():
            raise ValueError('special files are not publishable')
        files[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return files


def validate(root, policy):
    if policy.get('blocked'):
        raise ValueError(policy['blocked'])
    files = inventory(root)
    allowed = set(policy['allowed'])
    required = set(policy['required'])
    if not required <= allowed:
        raise ValueError('required publication files cannot be excluded')
    for name in allowed:
        p = Path(name)
        if p.is_absolute() or '..' in p.parts or name != p.as_posix():
            raise ValueError('unsafe policy path')
    if set(files) - allowed:
        raise ValueError('unpermitted publication contents: ' + ', '.join(sorted(set(files)-allowed)))
    if required - set(files):
        raise ValueError('missing required publication contents: ' + ', '.join(sorted(required-set(files))))
    # Policies permit artifact names, never raw payloads hidden under a permitted name.
    for name in files:
        data = (Path(root) / name).read_bytes()
        if b'-----BEGIN ' in data or b'ghp_' in data or b'github_pat_' in data:
            raise ValueError('possible credential in publication')
    return files


def copy_verified(source, destination, policy):
    """Immutable destinations: identical rerun is a no-op; conflicts never delete."""
    source, destination = Path(source), Path(destination)
    before = validate(source, policy)
    if destination.exists():
        if validate(destination, policy) != before:
            raise ValueError('destination differs; preserve it and use a new session destination')
        return before
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Validate ALL source contents before copying anything.
    shutil.copytree(source, destination)
    if validate(destination, policy) != before or validate(source, policy) != before:
        raise ValueError('publication bytes changed during copy; do not commit')
    return before


def run_logged(command, output):
    """Actual combined child output; preserve checkpoints and all failed attempts."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    console = Path(str(output).rstrip('/') + '.console.log')
    if console.is_symlink():
        raise ValueError('console must not be a symlink')
    with console.open('ab', buffering=0) as log:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(proc.stdout.readline, b''):
            log.write(line)
            sys.stdout.buffer.write(line)
            sys.stdout.buffer.flush()
        return proc.wait()


def check_git_paths(repo, base, permitted):
    """Check each outgoing commit, including files later deleted, and staged paths."""
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=repo)
    commits = git('rev-list', f'{base}..HEAD').decode().splitlines()
    for commit in commits:
        parents = git('rev-list', '--parents', '-n', '1', commit).split()
        if len(parents) != 2:
            raise ValueError('publication requires linear reviewed outgoing history')
        paths = git('diff-tree', '--no-commit-id', '--name-only', '-r', '-z', commit).split(b'\0')
        if any(p.decode() not in permitted for p in paths if p):
            raise ValueError('outgoing commit changes unpermitted paths')
    staged = git('diff', '--cached', '--name-only', '-z').split(b'\0')
    if any(p.decode() not in permitted for p in staged if p):
        raise ValueError('staged changes exceed publication scope')


def export_session(source, destination, policy):
    """Deposit original console alongside export; never substitute run_log.txt."""
    validate(source, policy)
    console = Path(str(source).rstrip('/') + '.console.log')
    target = Path(str(destination).rstrip('/') + '.console.log')
    if console.is_symlink() or not console.is_file():
        raise ValueError('original sibling console missing')
    data = console.read_bytes()
    if any(x in data for x in (b'ghp_', b'github_pat_', b'-----BEGIN ')):
        raise ValueError('possible credential in console; retain privately for review')
    if target.exists() and (target.is_symlink() or target.read_bytes() != data):
        raise ValueError('console destination differs; use a new session destination')
    result = copy_verified(source, destination, policy)
    if not target.exists():
        with target.open('xb') as f:
            f.write(data)
    if target.read_bytes() != data or console.read_bytes() != data:
        raise ValueError('console changed during export')
    return result
