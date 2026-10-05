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
from orchestrator.hosted_context import DOCUMENTS, policy_files
from orchestrator.reviewer_evidence import SOURCES

REQUIRED_ADMIN_SOURCE = tuple('deploy/research-system/'+name for name in (
    'install_live_research.py', 'prepare_live_research.py',
    'install_handover_fixture.py', 'install_live_handover.py'))
SERVICE_TEMPLATES = (
    'deploy/research-system/research-system-scientific-job@.service.in',
    'deploy/research-system/research-system-issue-intake.service.in',
)
REQUIRED_CONTINUING_SOURCE = ('scripts/pilot_review.py', *SERVICE_TEMPLATES)

DEFAULT_SOURCE_BRANCH = 'astra/infrastructure-milestone-record'


def scientific_support_files(root):
    """Installed originals needed to materialize either prospective version.

    Reviewed proposal bytes create the experiment files later. Only their shared
    source inputs belong in this archive; absent P002/P003 science is not invented.
    """
    from orchestrator.scientific_versions import required_files, artifact_targets
    names = set()
    for experiment in ('P002', 'P003'):
        generated = {name for outputs in artifact_targets(experiment).values() for name in outputs.values()}
        generated.add('campaigns/isles24-pilot/experiments/'+experiment+'/scientific-origin.json')
        names.update(required_files(root, experiment) - generated)
    return names


def prepare(root, source, destination, *, source_branch=DEFAULT_SOURCE_BRANCH):
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    if destination.exists() or destination.is_relative_to(root):
        raise ValueError('FRESH_EXTERNAL_DESTINATION_REQUIRED')
    def git(*args, cwd=root):
        return subprocess.check_output(['git', *args], cwd=cwd)
    if git('rev-parse', 'HEAD').decode().strip() != source:
        raise ValueError('SOURCE_HEAD_CHANGED')
    if git('diff', '--name-only', source):
        raise ValueError('SOURCE_WORKTREE_CHANGED')
    if not isinstance(source_branch, str) or not source_branch:
        raise ValueError('EXPLICIT_SOURCE_BRANCH_REQUIRED')
    if git('branch', '--show-current').decode().strip() != source_branch:
        raise ValueError('SOURCE_BRANCH_MISMATCH')
    names = set(DOCUMENTS)
    names.update(REQUIRED_ADMIN_SOURCE)
    names.update(policy_files(root))
    for paths in SOURCES.values():
        names.update(paths)
    tree = git('ls-tree', '-r', '--name-only', source).decode().splitlines()
    if not set(REQUIRED_ADMIN_SOURCE) <= set(tree):
        raise ValueError('MANDATORY_INSTALL_SOURCE_MISSING')
    continuing = set(REQUIRED_CONTINUING_SOURCE) | scientific_support_files(root)
    if not continuing <= set(tree):
        raise ValueError('MANDATORY_SCIENTIFIC_SUPPORT_MISSING')
    names.update(continuing)
    names.update(n for n in tree if n.startswith('orchestrator/') and n.endswith('.py'))
    # Reuse the scientific pipeline's actual context inventory; optional files
    # present in the reviewed source must not silently disappear on the host.
    from orchestrator.campaign_pipeline import grounding
    names.update(name for name in grounding(root, 'P001') if name in tree)
    names.update(n for n in tree if n.startswith('deploy/research-system/') and n.endswith(('.service','.socket','.timer')))
    names.update(n for n in ('scripts/drive_consent.py','scripts/drive_register.py',
                              'deploy/research-system/drive-requirements.lock') if n in tree)
    names.add('scripts/verify_handover_service.py')
    names.add('scripts/verify_protected_intake.py')
    names.add('deploy/research-system/research-system-control.sh')
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
    selection='campaigns/isles24-pilot/prediction_selection.json'
    if selection in tree:
        selected=json.loads(git('show',source+':'+selection))
        names.add(selection)
        names.update(selected['artifact_sha256'])
    # Imported by the thin preflight transport; code only, no patient payloads.
    if 'scripts/p001_input_preflight.py' in tree:
        names.add('scripts/p001_input_preflight.py')
    metadata = {'.gitignore', '.gitattributes'} & set(tree)
    expected = {}
    for name in sorted(names | metadata):
        raw = git('show', source+':'+name)
        # Dotfiles are exact pinned bootstrap metadata, not a publication exception.
        # These two fixed templates render reviewed .service files. The scan's
        # content rules still apply; this is no general .in/publication exception.
        scanned_name = name[:-3] if name in SERVICE_TEMPLATES else name
        scan('bootstrap-metadata.txt' if name in metadata else scanned_name, raw)
        expected[git('rev-parse', source+':'+name).decode().strip()] = name
    destination.mkdir(mode=0o700)
    snapshot = destination/'snapshot'
    git('clone', '--upload-pack=git -c uploadpack.allowFilter=true upload-pack',
        '--no-local', '--filter=blob:none', '--depth=1', '--no-checkout',
        '--single-branch', '--branch', source_branch,
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
    manifest = {'source':source, 'source_branch':source_branch, 'kind':'INSPECTED_SPARSE_SOURCE_SNAPSHOT',
                'files':sorted(names | metadata), 'physical_blob_count':len(blobs),
                'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
                'archive_bytes':archive.stat().st_size, 'patient_payloads':False}
    (destination/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--source-branch', default=DEFAULT_SOURCE_BRANCH,
                        help='Exact checked-out source branch; selection grants no deployment authority.')
    parser.add_argument('--destination', type=Path, required=True)
    args=parser.parse_args()
    print(json.dumps(prepare(Path(__file__).resolve().parents[1], args.source, args.destination,
                             source_branch=args.source_branch)))
