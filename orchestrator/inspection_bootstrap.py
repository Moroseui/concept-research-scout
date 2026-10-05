"""Bootstrap inspection only through the unchanged, tool-free legacy verifier.

Inputs are root-selected original bytes, never a model-selected evidence path.
A successful result approves this enabler source only, not a later candidate.
"""
from pathlib import PurePosixPath

from orchestrator import deployment_review as legacy
from orchestrator import review_input_codec as codec

SCOPE = 'direct-review-enabler'
MANDATORY_SOURCE = frozenset({
    'orchestrator/inspection_source.py',
    'orchestrator/inspection_access.py',
    'orchestrator/inspection_review.py',
    'orchestrator/inspection_model_policy.py',
    'orchestrator/inspection_bootstrap.py',
    'orchestrator/inspection_runner.py',
    'orchestrator/inspection_runtime.py',
    'orchestrator/inspection_canary.py',
    'orchestrator/inspection_deployment.py',
    'orchestrator/review_input_codec.py',
    'orchestrator/deployment_review.py',
    'scripts/pilot_review.py',
    'orchestrator/dispatch_limiter.py',
    'orchestrator/handover_coordinator.py',
    'orchestrator/protected_handover.py',
    'orchestrator/public_export.py',
    'orchestrator/git_publication.py',
    'orchestrator/scientific_authority.py',
    'orchestrator/hosted_context.py',
    'configs/scientific-operating-context.json',
    'docs/operations/DIRECT_INSPECTION_REVIEW.md',
})


MANDATORY_SOURCE_V2 = MANDATORY_SOURCE | {'orchestrator/change_requests.py'}

def _require(value, reason):
    if not value:
        raise ValueError(reason)


def _policy_sources(files):
    """Derive the full literal authority/document closure from its bound manifest."""
    operating = codec.parsed(files['configs/scientific-operating-context.json'])
    _require(isinstance(operating, dict), 'INSPECTION_BOOTSTRAP_POLICY_REQUIRED')
    binding = operating.get('authority_policy')
    documents = operating.get('documents')
    _require(isinstance(binding, dict) and isinstance(documents, dict) and documents,
             'INSPECTION_BOOTSTRAP_POLICY_REQUIRED')
    policy_path = binding.get('path')
    _require(isinstance(policy_path, str) and policy_path in files
             and legacy.digest(files[policy_path]) == binding.get('sha256'),
             'INSPECTION_BOOTSTRAP_POLICY_CHANGED')
    policy = codec.parsed(files[policy_path])
    _require(isinstance(policy, dict), 'INSPECTION_BOOTSTRAP_POLICY_REQUIRED')
    direction = policy.get('direction_path')
    _require(isinstance(direction, str), 'INSPECTION_BOOTSTRAP_POLICY_REQUIRED')
    for name, pin in [*documents.items(), (direction, policy.get('direction_sha256'))]:
        _require(isinstance(name, str) and name in files
                 and legacy.digest(files[name]) == pin,
                 'INSPECTION_BOOTSTRAP_POLICY_CHANGED')


def require_v2_review(originals):
    """Require V2 for new use; callers must still validate the complete proof.

    Historical receipt and approved-baseline validation deliberately do not call
    this guard. A presentation marker alone grants no approval.
    """
    request = codec.parsed(originals['request.json'])
    _require(isinstance(request, dict) and request.get('input_presentation') == codec.FORMAT_V2,
             'REVIEW_PROSPECTIVE_V2_REQUIRED')


def validate_bootstrap(originals, bootstrap_source, required_source_bytes, *, policy_baseline=None):
    """Return the ordinary old validated review after exact complete source binding.

    The caller obtains this map from the fixed bootstrap Git source and dependency
    inventory. This function does not fetch, execute, grant authority or infer that
    unchanged enabling modules approve any later candidate source.
    """
    legacy.pin(bootstrap_source, 40)
    _require(isinstance(required_source_bytes, dict)
             and MANDATORY_SOURCE <= set(required_source_bytes),
             'INSPECTION_BOOTSTRAP_MANDATORY_SOURCE_REQUIRED')
    for name, raw in required_source_bytes.items():
        _require(isinstance(name, str) and name
                 and str(PurePosixPath(name)) == name
                 and not PurePosixPath(name).is_absolute()
                 and not {'.', '..', '.git'} & set(PurePosixPath(name).parts)
                 and '\\' not in name and isinstance(raw, bytes),
                 'INSPECTION_BOOTSTRAP_SOURCE_MAP_REQUIRED')
    _require(isinstance(originals, dict) and set(originals) == set(legacy.ORIGINAL_NAMES)
             and all(isinstance(raw, bytes) for raw in originals.values()),
             'INSPECTION_BOOTSTRAP_ORIGINALS_REQUIRED')
    _policy_sources(required_source_bytes)
    review = legacy._review_originals(originals, bootstrap_source, {SCOPE}, policy_baseline=policy_baseline)
    _require(review['request'].get('input_presentation') in {codec.FORMAT, codec.FORMAT_V2}
             and isinstance(review['request'].get('shared_context_sha256'), str),
             'INSPECTION_BOOTSTRAP_SHARED_CONTEXT_REQUIRED')
    if review['request'].get('input_presentation') == codec.FORMAT_V2:
        _require(MANDATORY_SOURCE_V2 <= set(required_source_bytes),
                 'INSPECTION_BOOTSTRAP_POLICY_VALIDATOR_SOURCE_REQUIRED')
    _require({name: value.encode() for name, value in review['source_text'].items()}
             == required_source_bytes, 'INSPECTION_BOOTSTRAP_SOURCE_BYTES_CHANGED')
    return review


POLICY_BASELINE = 'approved-review-policy-baseline/v1'


def validate_context(context_raw, approved_sources):
    """Check actual reviewer instructions against independently reviewed bytes.

    recorded_changes remains evidence; it cannot select the policy or role.
    The caller must already have authenticated approved_sources through originals.
    """
    context = codec.parsed(context_raw)
    sources = {name: value if isinstance(value, str) else value.decode()
               for name, value in approved_sources.items()}
    manifest_raw = sources['configs/scientific-operating-context.json'].encode()
    manifest = codec.parsed(manifest_raw)
    binding = manifest['authority_policy']
    policy = codec.parsed(sources[binding['path']])
    shared = context['shared_policy']
    _require(isinstance(shared, dict) and set(shared) == {
        'binding', 'direction', 'operating_context', 'policy'}
        and isinstance(shared['operating_context'], dict)
        and set(shared['operating_context']) == {'documents', 'manifest', 'manifest_sha256'},
        'REVIEW_POLICY_CONTEXT_NOT_APPROVED')
    _require(context['family'] == 'claude' and context['role'] == manifest['roles']['claude']
             and shared['binding'] == binding and shared['policy'] == policy
             and shared['operating_context']['manifest'] == manifest
             and shared['operating_context']['manifest_sha256'] == codec.digest(manifest_raw),
             'REVIEW_POLICY_CONTEXT_NOT_APPROVED')
    _require(shared['direction'] == sources[policy['direction_path']]
             and shared['operating_context']['documents'] == {
                 name: {'sha256': pin, 'text': sources[name]}
                 for name, pin in manifest['documents'].items()},
             'REVIEW_POLICY_CONTEXT_NOT_APPROVED')
    codec.restore_context(context, sources, codec.digest(context_raw))


def validate_policy_baseline(raw):
    """Authenticate one portable prior approval, without model calls or recursion.

    A fresh V2 review may use a root-selected, recorded V1 enabling approval as
    its policy anchor. Historical V1 proof is retained at its original scope;
    it is not relabeled or made into approval of the new candidate.
    """
    from orchestrator import change_requests as changes
    from orchestrator.inspection_access import relative_name
    from orchestrator.inspection_review import MAX_EXPORT_FILES
    _require(isinstance(raw, dict) and 'baseline.json' in raw
             and 0 < len(raw) <= MAX_EXPORT_FILES, 'REVIEW_POLICY_BASELINE_REQUIRED')
    _require(all(isinstance(value, bytes) and len(value) <= 16000000 for value in raw.values())
             and sum(map(len, raw.values())) <= 150000000, 'REVIEW_POLICY_BASELINE_SIZE')
    for name in raw:
        relative_name(name)
    manifest = codec.parsed(raw['baseline.json'])
    _require(isinstance(manifest, dict) and set(manifest) == {
        'schema', 'source', 'request_id', 'applied_event', 'review_event',
        'canonical_head_sha256', 'standing_authority', 'files'}
        and manifest['schema'] == POLICY_BASELINE, 'REVIEW_POLICY_BASELINE_SCHEMA')
    source = legacy.pin(manifest['source'], 40)
    _require(manifest['files'] == {
        name: {'sha256': codec.digest(value), 'bytes': len(value)}
        for name, value in raw.items() if name != 'baseline.json'},
        'REVIEW_POLICY_BASELINE_ORIGINALS_CHANGED')
    originals = {name: raw['review/' + name] for name in legacy.ORIGINAL_NAMES}
    _require(codec.parsed(originals['request.json']).get('input_presentation') == codec.FORMAT,
             'REVIEW_POLICY_BASELINE_REQUIRES_RECORDED_LEGACY_ANCHOR')
    prior = legacy._review_originals(originals, source, {SCOPE})
    files = {name: value.encode() for name, value in prior['source_text'].items()}
    approved = validate_bootstrap(originals, source, files)
    events = {name[len('changes/events/'):]: value for name, value in raw.items()
              if name.startswith('changes/events/')}
    chain = changes.validate_originals(raw['changes/request.json'], events,
                                      lambda name: raw['changes/' + name])
    _require(chain['request']['identity'] == manifest['request_id']
             and chain['head_sha256'] == manifest['canonical_head_sha256'],
             'REVIEW_POLICY_BASELINE_CHANGE_CHAIN')
    applied = [event for event in chain['events'] if event['event'] == 'APPLIED']
    reviews = [event for event in chain['events'] if event['event'] == 'REVIEW']
    selected = [event for event in reviews if event['identity'] == manifest['review_event']]
    _require(applied and applied[-1]['identity'] == manifest['applied_event']
             and applied[-1]['payload']['result_binding']['source'] == source
             and len(selected) == 1, 'REVIEW_POLICY_BASELINE_APPLIED_BINDING')
    review = selected[0]
    payload, actor = review['payload'], review['actor']
    session = prior['response']['session_id']
    _require(payload.get('verdict') == 'APPROVE'
             and payload.get('applied_event') == manifest['applied_event']
             and payload.get('reviewed_source') == source
             and payload.get('review_session_id') == session
             and actor.get('kind') == 'agent' and actor.get('family') == 'claude'
             and actor.get('model') == legacy.MODEL and actor.get('session_id') == session
             and not any(event['payload'].get('applied_event') == manifest['applied_event']
                         and event['payload'].get('verdict') == 'REQUEST_CHANGES'
                         for event in reviews), 'REVIEW_POLICY_BASELINE_REVIEW_BINDING')
    evidence = payload['review_evidence']
    _require(isinstance(evidence, list), 'REVIEW_POLICY_BASELINE_REVIEW_EVIDENCE')
    for name in ('response.json', 'execution.json', 'protocol.jsonl', 'intent.json', 'returned.json'):
        _require(any(item.get('sha256') == codec.digest(originals[name])
                     and raw.get('changes/' + item.get('artifact', '')) == originals[name]
                     for item in evidence), 'REVIEW_POLICY_BASELINE_REVIEW_EVIDENCE')
    application_raw = raw['changes/events/' +
        f"{applied[-1]['sequence']:04d}-{applied[-1]['identity']}.json"]
    _require(approved['private_text'].get(codec.digest(application_raw)) == application_raw,
             'REVIEW_POLICY_BASELINE_APPLICATION_NOT_IN_ORIGINAL_REVIEW')
    authority = manifest['standing_authority']
    operating = codec.parsed(files['configs/scientific-operating-context.json'])
    _require(isinstance(authority, dict) and set(authority) == {'path', 'sha256'}
             and operating['documents'].get(authority['path']) == authority['sha256']
             and authority['path'] in files
             and codec.digest(files[authority['path']]) == authority['sha256'],
             'REVIEW_POLICY_BASELINE_STANDING_AUTHORITY')
    allowed = {'baseline.json', 'changes/request.json'} | {
        'review/' + name for name in legacy.ORIGINAL_NAMES} | {
        'changes/events/' + name for name in events}
    def collect(value):
        if isinstance(value, dict):
            if 'artifact' in value and 'sha256' in value:
                allowed.add('changes/' + value['artifact'])
            for item in value.values(): collect(item)
        elif isinstance(value, list):
            for item in value: collect(item)
    for event in chain['events']: collect(event['payload'])
    _require(set(raw) == allowed, 'REVIEW_POLICY_BASELINE_UNEXPECTED_FILE')
    policy = codec.parsed(files[operating['authority_policy']['path']])
    closure = set(operating['documents']) | {'configs/scientific-operating-context.json',
        operating['authority_policy']['path'], policy['direction_path']}
    descriptor = {'schema': POLICY_BASELINE, 'source': source,
        'proof_sha256': codec.digest(raw['baseline.json']),
        'approval': {key: manifest[key] for key in
                     ('request_id', 'applied_event', 'review_event', 'canonical_head_sha256')},
        'review_session_id': session, 'standing_authority': authority,
        'original_review_sha256': {name: codec.digest(value) for name, value in originals.items()},
        'policy_files': {name: codec.digest(files[name]) for name in sorted(closure)}}
    request = prior['request']
    reader = codec.Reader(request['prompt'].encode())
    reader.literal(codec.PREFIX.encode())
    reader.line()
    _, shown = reader.frame('context', 'shared-role-context')
    context_raw = codec.restore_context(codec.parsed(shown), approved['source_text'],
                                        request['shared_context_sha256'])
    validate_context(context_raw, approved['source_text'])
    return {'descriptor': descriptor, 'source_text': approved['source_text'],
            'source': source, 'chain': chain, 'context_raw': context_raw}


def read_policy_baseline(directory):
    """Read the exact private saved proof with existing export size bounds."""
    import os
    import stat
    from pathlib import Path
    from orchestrator.inspection_access import relative_name
    from orchestrator.inspection_review import MAX_EXPORT_FILES
    directory = Path(directory).absolute()
    _require(not any(path.is_symlink() for path in (directory, *directory.parents))
             and directory.is_dir() and directory.stat().st_uid == os.getuid()
             and not directory.stat().st_mode & 0o077, 'REVIEW_POLICY_BASELINE_PRIVATE_DIRECTORY')
    raw = {}
    for parent, directories, names in os.walk(directory, followlinks=False):
        for name in directories:
            path = Path(parent) / name
            _require(not path.is_symlink() and path.stat().st_uid == os.getuid()
                     and not path.stat().st_mode & 0o077, 'REVIEW_POLICY_BASELINE_PRIVATE_DIRECTORY')
        for name in names:
            path = Path(parent) / name
            relative = path.relative_to(directory).as_posix()
            relative_name(relative)
            info = path.lstat()
            _require(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid()
                     and not info.st_mode & 0o077 and info.st_size <= 16000000,
                     'REVIEW_POLICY_BASELINE_PRIVATE_FILE')
            raw[relative] = path.read_bytes()
            _require(len(raw) <= MAX_EXPORT_FILES and sum(map(len, raw.values())) <= 150000000,
                     'REVIEW_POLICY_BASELINE_SIZE')
    validate_policy_baseline(raw)
    return raw



def prepare_policy_baseline(directory, *, source_root, expected_source, review_directory,
                            change_folder, standing_authority_path):
    """Save a named prior approval using the same operation for humans and agents.

    Inputs select existing reviewed work. This supplies the exact file manifest
    and bookkeeping; it neither reviews code nor grants new authority.
    """
    import os
    import stat
    import subprocess
    from pathlib import Path
    from orchestrator import change_requests as changes
    from orchestrator.operations_report import private_root
    from orchestrator.inspection_source import write_once
    source_root, review_directory, change_folder = map(Path,
        (source_root, review_directory, change_folder))
    legacy.pin(expected_source, 40)
    _require(subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source_root,
                                    text=True).strip() == expected_source
             and not subprocess.check_output(['git', 'status', '--porcelain'], cwd=source_root),
             'REVIEW_POLICY_BASELINE_SOURCE_MOVED_OR_DIRTY')
    originals = {}
    for name in legacy.ORIGINAL_NAMES:
        path = (review_directory / name).absolute()
        _require(not any(item.is_symlink() for item in (path, *path.parents)),
                 'REVIEW_POLICY_BASELINE_PRIVATE_FILE')
        info = path.stat()
        _require(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid()
                 and not info.st_mode & 0o077 and info.st_size <= 4000000,
                 'REVIEW_POLICY_BASELINE_PRIVATE_FILE')
        originals[name] = path.read_bytes()
    prior = legacy._review_originals(originals, expected_source, {SCOPE})
    _require(prior['request'].get('input_presentation') == codec.FORMAT,
             'REVIEW_POLICY_BASELINE_REQUIRES_RECORDED_LEGACY_ANCHOR')
    for name, text in prior['source_text'].items():
        path = source_root / name
        _require(not path.is_symlink() and path.read_bytes() == text.encode()
                 and subprocess.check_output(['git', 'show', expected_source + ':' + name],
                                             cwd=source_root) == text.encode(),
                 'REVIEW_POLICY_BASELINE_SOURCE_BYTES_CHANGED')
    chain = changes.load(change_folder)
    reviews = [event for event in chain['events'] if event['event'] == 'REVIEW'
               and event['payload'].get('reviewed_source') == expected_source
               and event['payload'].get('review_session_id') == prior['response']['session_id']
               and event['payload'].get('verdict') == 'APPROVE']
    _require(len(reviews) == 1, 'REVIEW_POLICY_BASELINE_EXACT_RECORDED_REVIEW_REQUIRED')
    selected = reviews[0]
    raw = {'review/' + name: value for name, value in originals.items()}
    raw['changes/request.json'] = changes._read(change_folder / 'request.json')
    for event in chain['events']:
        name = f"{event['sequence']:04d}-{event['identity']}.json"
        raw['changes/events/' + name] = changes._read(change_folder / 'events' / name)
    def collect(value):
        if isinstance(value, dict):
            if 'artifact' in value and 'sha256' in value:
                name = value['artifact']
                raw['changes/' + name] = changes._read(change_folder / name)
            for item in value.values(): collect(item)
        elif isinstance(value, list):
            for item in value: collect(item)
    for event in chain['events']: collect(event['payload'])
    manifest = {'schema': POLICY_BASELINE, 'source': expected_source,
        'request_id': chain['request']['identity'],
        'applied_event': selected['payload']['applied_event'], 'review_event': selected['identity'],
        'canonical_head_sha256': chain['head_sha256'],
        'standing_authority': {'path': standing_authority_path,
            'sha256': codec.digest(prior['source_text'][standing_authority_path].encode())},
        'files': {name: {'sha256': codec.digest(value), 'bytes': len(value)}
                  for name, value in raw.items()}}
    raw['baseline.json'] = codec.encoded(manifest) + b'\n'
    checked = validate_policy_baseline(raw)
    _require(changes.load(change_folder)['head_sha256'] == chain['head_sha256'],
             'REVIEW_POLICY_BASELINE_CHANGE_CHAIN_MOVED')
    directory = Path(directory)
    _require(not directory.exists() and not directory.is_symlink(),
             'REVIEW_POLICY_BASELINE_OUTPUT_EXISTS_RECONCILE')
    private_root(directory)
    for name, value in raw.items():
        path = directory / name
        private_root(path.parent)
        write_once(path, value)
    _require(read_policy_baseline(directory) == raw, 'REVIEW_POLICY_BASELINE_COPY_CHANGED')
    return checked['descriptor']


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description='Preserve an existing independent policy approval; no model call.')
    parser.add_argument('--prepare-policy-baseline', required=True)
    parser.add_argument('--source-root', required=True)
    parser.add_argument('--expected-source', required=True)
    parser.add_argument('--review-directory', required=True)
    parser.add_argument('--change-folder', required=True)
    parser.add_argument('--standing-authority-path', required=True)
    args = parser.parse_args()
    print(json.dumps(prepare_policy_baseline(args.prepare_policy_baseline,
        source_root=args.source_root, expected_source=args.expected_source,
        review_directory=args.review_directory, change_folder=args.change_folder,
        standing_authority_path=args.standing_authority_path), sort_keys=True))
