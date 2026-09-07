#!/usr/bin/env python3
"""Prepare a minimal, inspected Git snapshot for supervised hosted acceptance.

Local preparation only. No server operation or publication. Refuse an existing
destination, retain failures, and include the exact approved-context dependencies.
The resulting sparse tree preserves Git source checks without acquiring results
branches or patient payloads.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

from orchestrator.git_publication import scan
from orchestrator.hosted_context import DOCUMENTS
from orchestrator.reviewer_evidence import SOURCES


def prepare(root, source, destination):
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    if destination.exists() or destination.is_relative_to(root):
        raise ValueError('FRESH_EXTERNAL_DESTINATION_REQUIRED')
    def git(*args, cwd=root):
        return subprocess.check_output(['git', *args], cwd=cwd)
    if git('rev-parse', 'HEAD').decode().strip() != source:
        raise ValueError('SOURCE_HEAD_CHANGED')
    if git('branch', '--show-current').decode().strip() != 'astra/infrastructure-milestone-record':
        raise ValueError('INFRASTRUCTURE_BRANCH_REQUIRED')
    names = set(DOCUMENTS)
    for paths in SOURCES.values():
        names.update(paths)
    tree = git('ls-tree', '-r', '--name-only', source).decode().splitlines()
    names.update(n for n in tree if n.startswith('orchestrator/') and n.endswith('.py'))
    names.update(n for n in tree if n.startswith('deploy/research-system/') and n.endswith(('.service','.socket','.timer')))
    names.add('scripts/verify_handover_service.py')
    proposal = 'campaigns/isles24-pilot/pipeline/prediction-charter-20260906-v1'
    receipt = json.loads(git('show', source+':'+proposal+'/receipt.json'))
    names.add(proposal+'/receipt.json')
    names.update(proposal+'/round-'+str(receipt['round'])+'/'+n for n in
                 ('CHARTER.proposed.md','RUBRIC.proposed.md','PROMPTS.proposed.md',
                  'P001_ADOPTION.proposed.md','review.json'))
    names.update(n for n in receipt['input_sha256'] if n == 'campaigns/isles24-pilot/CAMPAIGN.md'
                 or n.startswith('campaigns/isles24-pilot/experiments/P001/'))
    names.update(n for n in tree if n in {
        'docs/science/P001_SOURCE_CHECK_AMENDMENT_20260906.md',
        'docs/science/P001_METADATA_PREFLIGHT_20260906.json'})
    metadata = {'.gitignore', '.gitattributes'} & set(tree)
    expected = {}
    for name in sorted(names | metadata):
        raw = git('show', source+':'+name)
        # Dotfiles are exact pinned bootstrap metadata, not a publication exception.
        scan('bootstrap-metadata.txt' if name in metadata else name, raw)
        expected[git('rev-parse', source+':'+name).decode().strip()] = name
    destination.mkdir(mode=0o700)
    snapshot = destination/'snapshot'
    git('clone', '--upload-pack=git -c uploadpack.allowFilter=true upload-pack',
        '--no-local', '--filter=blob:none', '--depth=1', '--no-checkout',
        '--single-branch', '--branch', 'astra/infrastructure-milestone-record',
        str(root), str(snapshot))
    git('sparse-checkout', 'set', '--no-cone', *('/'+n for n in sorted(names | metadata)), cwd=snapshot)
    git('checkout', '--detach', source, cwd=snapshot)
    if git('status', '--porcelain', cwd=snapshot):
        raise ValueError('SNAPSHOT_DIRTY')
    objects = git('cat-file', '--batch-all-objects', '--batch-check=%(objectname) %(objecttype)', cwd=snapshot)
    blobs = [line.split()[0] for line in objects.decode().splitlines() if line.endswith(' blob')]
    if set(blobs) != set(expected):
        raise ValueError('UNEXPECTED_OR_MISSING_PHYSICAL_BLOBS')
    git('remote', 'set-url', 'origin', 'https://github.com/Moroseui/concept-research-scout.git', cwd=snapshot)
    archive = destination/'snapshot.tar.gz'
    def include(info):
        parts = Path(info.name).parts
        if '.git' in parts and any(n in parts for n in ('logs','hooks')):
            return None
        return info
    with tarfile.open(archive, 'w:gz') as output:
        output.add(snapshot, arcname='snapshot', filter=include)
    manifest = {'source':source, 'kind':'INSPECTED_SPARSE_SOURCE_SNAPSHOT',
                'files':sorted(names | metadata), 'physical_blob_count':len(blobs),
                'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
                'archive_bytes':archive.stat().st_size, 'patient_payloads':False}
    (destination/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args=parser.parse_args()
    print(json.dumps(prepare(Path(__file__).resolve().parents[1], args.source, args.destination)))
