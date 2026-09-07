"""Read-only PR #5 historical audit, independent of today's main/publication base.

The operator's f62a4c4 ruling authorizes only the pinned existing policy. This
entry point cannot publish, ratify findings, or alter that policy. Each changed
historical blob is scanned, including versions deleted before the final tree.
Additional decision commits are explicit inputs and are scanned in full for
changes against every parent; metadata is scanned even for empty commits.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import types

BASE = 'd24ffb9003a2291f359afe3acf4bf491f2d7fd9f'
SOURCE = 'ac8e0150eb2daf8ca2252c27b5c7ab4bde38f36d'
TRUST = 'f62a4c418bc2eb25055a4b6ac5aa9a786fdcedfd'
POLICY_SHA256 = '5622c1b700437a022c63c539f28bb1b7b8adc64de6386485293bf495005532f5'


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.PIPE)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pinned_policy(root):
    """Execute only the reviewed, hash-verified local policy; never fetch code."""
    raw = git(root, 'show', SOURCE + ':orchestrator/git_publication.py')
    if sha(raw) != POLICY_SHA256:
        raise ValueError('TRUSTED_POLICY_IDENTITY_MISMATCH')
    # Bind the ruling to its exact reviewed commit, not a moving file on disk.
    if git(root, 'rev-parse', TRUST + '^').decode().strip() != SOURCE:
        raise ValueError('RULING_PARENT_MISMATCH')
    ruling = git(root, 'show', TRUST + ':evidence/decisions.md')
    module = types.ModuleType('pr5_pinned_publication_policy')
    exec(compile(raw, '<sha256-bound-publication-policy>', 'exec'), module.__dict__)
    return module, sha(ruling)


def scan_commits(root, commits, policy, trust):
    """Return all findings rather than letting the first refusal hide the rest.

    Receipts include byte identities and named refusal codes, never rejected
    contents, subprocess output, or unchecked path text.
    """
    blobs, metadata, findings = [], [], []
    for commit in commits:
        raw_commit = git(root, 'cat-file', 'commit', commit)
        metadata.append({'commit': commit, 'sha256': sha(raw_commit)})
        try:
            policy.scan_commit(raw_commit)
        except ValueError as error:
            findings.append({'commit': commit, 'kind': 'metadata', 'reason': str(error)})
        tree = {}
        for entry in git(root, 'ls-tree', '-r', '-z', commit).split(b'\0'):
            if entry:
                meta, name = entry.split(b'\t', 1)
                tree[name] = meta.split()
        names = set(git(root, 'diff-tree', '--root', '-m', '--no-commit-id',
                        '--name-only', '-r', '-z', commit).split(b'\0'))
        for name in sorted(names):
            if not name or name not in tree:
                continue
            mode, kind, oid = tree[name]
            record = {'commit': commit, 'path_sha256': sha(name),
                      'object': oid.decode(), 'mode': mode.decode()}
            if mode not in (b'100644', b'100755') or kind != b'blob':
                findings.append({**record, 'reason': 'NON_REGULAR_PUBLICATION'})
                continue
            data = git(root, 'cat-file', 'blob', oid.decode())
            record['sha256'] = sha(data)
            blobs.append(record)
            try:
                path = name.decode('utf-8')
                policy.scan_history_blob(root, trust, path, data)
            except (ValueError, UnicodeError) as error:
                reason = str(error) if isinstance(error, ValueError) and re.fullmatch('[A-Z_]+', str(error)) else 'NON_UTF8_PUBLICATION'
                findings.append({**record, 'reason': reason})
    return metadata, blobs, findings


def audit(root, additions):
    policy, ruling_hash = pinned_policy(root)
    original = git(root, 'rev-list', '--reverse', BASE + '..' + SOURCE).decode().splitlines()
    if len(original) != 82:
        raise ValueError('ORIGINAL_82_COMMIT_RANGE_REQUIRED')
    if not additions or TRUST not in additions or len(set(additions)) != len(additions):
        raise ValueError('EXPLICIT_UNIQUE_DECISION_COMMITS_INCLUDING_RULING_REQUIRED')
    for pin in additions:
        if not re.fullmatch('[0-9a-f]{40}', pin) or pin in original:
            raise ValueError('INVALID_ADDITIONAL_COMMIT')
        git(root, 'merge-base', '--is-ancestor', SOURCE, pin)
    commits = original + additions
    metadata, blobs, findings = scan_commits(root, commits, policy, TRUST)
    return {'schema': 1, 'status': 'BLOCKED_FINDINGS' if findings else 'PASS',
            'scope': 'RETROSPECTIVE_ONLY_NOT_PUBLICATION_OR_ACTIVATION',
            'range': {'base': BASE, 'source': SOURCE, 'original_commits': original},
            'additional_commits': additions,
            'policy': {'source': SOURCE, 'sha256': POLICY_SHA256},
            'ruling': {'commit': TRUST, 'decisions_sha256': ruling_hash},
            'commit_metadata': metadata, 'blob_versions': blobs, 'findings': findings,
            'counts': {'original_commits': len(original), 'additional_commits': len(additions),
                       'blob_versions': len(blobs), 'findings': len(findings)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--additional-commit', action='append', required=True)
    args = parser.parse_args()
    result = audit(Path.cwd(), args.additional_commit)
    print(json.dumps(result, indent=2))
    return 1 if result['findings'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
