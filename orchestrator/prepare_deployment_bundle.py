"""Prepare one private continuing deployment proposal; no host or model operation.

This unprivileged phase preserves exact input bytes and existing change history.
Actual Claude originals and the resulting REVIEW event are attached later to a
separate root-held installation bundle; preparation never asserts approval.
"""
import argparse
import json
import os
from pathlib import Path
import stat
import subprocess

from orchestrator import change_requests as changes
from orchestrator import deployment_review as gate
from orchestrator.operations_report import private_root
from orchestrator.remote_supervisor import checked_source

SCHEMA = 'research-deployment-preparation/v1'


def local_read(path, maximum=2000000):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('PREPARATION_REGULAR_INPUT_REQUIRED')
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > maximum:
        raise ValueError('PREPARATION_BOUNDED_INPUT_REQUIRED')
    with path.open('rb') as stream:
        before = os.fstat(stream.fileno()); raw = stream.read(maximum+1)
        if gate.file_identity(before) != gate.file_identity(os.fstat(stream.fileno())) or len(raw) > maximum:
            raise ValueError('PREPARATION_INPUT_CHANGED')
    return raw


def text_literal(raw):
    # Same existing content boundary as recorded requests; no redaction or rewrite.
    text = raw.decode('utf-8')
    changes.permitted_text(text, limit=max(20000, len(raw)))
    return raw


def save_original(path, raw):
    """Preserve either validated text or the already inspected binary archive."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    directory = os.open(Path(path).parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try: os.fsync(directory)
    finally: os.close(directory)


def metadata(value):
    gate.require(isinstance(value, dict) and set(value) == {'file', 'uid', 'gid', 'mode'},
                 'PREPARATION_LITERAL_ACCESS_REQUIRED')
    gate.require(value['uid'] == 0 and all(type(value[k]) is int and value[k] >= 0
                 for k in ('uid', 'gid', 'mode')) and value['mode'] <= 0o777
                 and not value['mode'] & 0o022, 'PREPARATION_LITERAL_ACCESS_REQUIRED')
    raw = text_literal(local_read(value['file']))
    return {'sha256': gate.digest(raw), **{k: value[k] for k in ('uid', 'gid', 'mode')}}, raw


def investigator_target_binding(targets, literals):
    """Check the assembled files, not independently valid source labels.

    The native template validator checks its enclosing digest. The evidence pin
    must bind the exact target bytes the same proposal installs; historical
    previous_files cannot satisfy this relation. No review/authority is inferred.
    """
    from orchestrator.investigator_wakes import setting
    controller_path = '/etc/research-system/live-research/controller.json'
    evidence_path = '/etc/research-system/live-research/report-evidence.json'
    controller = json.loads(literals[targets[controller_path]['sha256']])
    investigator = setting(controller)
    if investigator is None:
        return None
    template = investigator['template']
    gate.require(template['evidence_file'] == evidence_path
        and evidence_path in targets, 'PREPARATION_INVESTIGATOR_EVIDENCE_TARGET_REQUIRED')
    actual = gate.digest(literals[targets[evidence_path]['sha256']])
    gate.require(actual == targets[evidence_path]['sha256'] == template['evidence_sha256'],
        'PREPARATION_INVESTIGATOR_EVIDENCE_BINDING_CHANGED')
    return {'evidence_file': evidence_path, 'evidence_sha256': actual,
        'template_sha256': investigator['template_sha256']}


def dependency_inputs(path):
    raw = text_literal(local_read(path)); value = json.loads(raw)
    gate.require(isinstance(value, dict) and set(value) == set(gate.DEPENDENCY_PATHS),
                 'PREPARATION_FIXED_DEPENDENCIES_REQUIRED')
    for name, item in value.items():
        gate.require(isinstance(item, dict) and set(item) ==
            {'path', 'resolved', 'sha256', 'bytes', 'uid', 'gid', 'mode'}
            and item['path'] == gate.DEPENDENCY_PATHS[name]
            and Path(item['resolved']).is_absolute() and '..' not in Path(item['resolved']).parts,
            'PREPARATION_DEPENDENCY_METADATA_REQUIRED')
        gate.pin(item['sha256'])
        gate.require(item['uid'] == 0 and all(type(item[k]) is int and item[k] >= 0
            for k in ('uid', 'gid', 'mode', 'bytes')) and item['bytes'] <= 400000000
            and item['mode'] <= 0o777 and not item['mode'] & 0o022,
            'PREPARATION_DEPENDENCY_ACCESS_REQUIRED')
    return value, raw


def referenced_evidence(value):
    """Find the same nested evidence records validated by change_requests.load."""
    if isinstance(value, dict):
        if 'artifact' in value and 'sha256' in value:
            yield value
        for item in value.values():
            yield from referenced_evidence(item)
    elif isinstance(value, list):
        for item in value:
            yield from referenced_evidence(item)


def original_change(folder, applied, source):
    folder = Path(folder); state = changes.load(folder); gate.pin(applied)
    selected = [e for e in state['events'] if e['event'] == 'APPLIED' and e['identity'] == applied]
    gate.require(len(selected) == 1 and isinstance(selected[0]['payload'].get('result_binding'), dict)
                 and selected[0]['payload']['result_binding'].get('source') == source,
                 'PREPARATION_EXACT_APPLIED_SOURCE_REQUIRED')
    gate.require(not any(applied in e['payload'].get('supersedes_applied_events', [])
                        for e in state['events'] if e['event'] == 'APPLIED'),
                 'PREPARATION_SUPERSEDED_APPLICATION')
    gate.require(not any(e['payload'].get('applied_event') == applied and
                        e['payload'].get('verdict') == 'REQUEST_CHANGES'
                        for e in state['events'] if e['event'] == 'REVIEW'),
                 'PREPARATION_APPLICATION_REQUIRES_CORRECTION')
    files = {'request.json': local_read(folder/'request.json')}
    for event in state['events']:
        name = 'events/' + str(event['sequence']).zfill(4) + '-' + event['identity'] + '.json'
        files[name] = local_read(folder/name)
        for evidence in referenced_evidence(event['payload']):
            files[evidence['artifact']] = local_read(folder/evidence['artifact'])
    return {'request': state['request']['identity'], 'applied': applied}, files, state['head_sha256']


def prepare(root, source, archive, plan_file, destination):
    gate.require(os.getuid() != 0, 'UNPRIVILEGED_PREPARATION_REQUIRED')
    root = checked_source(root, source)
    destination = Path(destination).absolute()
    gate.require(not destination.exists() and not destination.is_symlink()
                 and not destination.is_relative_to(root), 'FRESH_EXTERNAL_PREPARATION_REQUIRED')
    plan_raw = local_read(plan_file); plan = json.loads(plan_raw)
    gate.require(isinstance(plan, dict) and set(plan) == {'schema', 'source', 'source_root',
        'previous_source', 'previous_source_root', 'targets', 'previous_files',
        'dependencies_file', 'recovery_file', 'changes'}
        | ({'review_plan_file'} if 'review_plan_file' in plan else set())
        | ({'review_profile'} if 'review_profile' in plan else set()) and plan['schema'] == SCHEMA
        and plan['source'] == source, 'PREPARATION_PLAN_REQUIRED')
    gate.require('review_profile' not in plan or (plan['review_profile'] in
                 ('direct-inspection/v1', 'operator-terminal-review/v1', 'server-terminal-review/v1')
                 and 'review_plan_file' not in plan), 'PREPARATION_EXPLICIT_REVIEW_PROFILE_REQUIRED')
    for key in ('source_root', 'previous_source_root'):
        gate.require(isinstance(plan[key], str) and Path(plan[key]).is_absolute()
                     and '..' not in Path(plan[key]).parts, 'PREPARATION_RELEASE_PATH_REQUIRED')
    gate.pin(plan['previous_source'], 40)
    gate.require(isinstance(plan['targets'], dict) and set(plan['targets']) in (gate.REQUIRED_TARGETS,gate.REQUIRED_TARGETS|{gate.REGISTRATION_LOCK_TARGET})
                 and isinstance(plan['previous_files'], dict) and plan['previous_files']
                 and set(plan['previous_files']) <= set(plan['targets']),
                 'PREPARATION_EXACT_COMPONENT_PROFILE_REQUIRED')
    source_raw = local_read(archive, maximum=10000000); files = gate.archive_inventory(source_raw)
    env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'GIT_OPTIONAL_LOCKS': '0',
           'GIT_NO_LAZY_FETCH': '1', 'GIT_ALLOW_PROTOCOL': '', 'GIT_TERMINAL_PROMPT': '0'}
    for name, raw in files.items():
        observed = subprocess.check_output(['git', '-c', 'credential.helper=', '-c', 'protocol.allow=never',
                                           'show', source+':'+name], cwd=root, env=env)
        gate.require(observed == raw, 'PREPARATION_ARCHIVE_SOURCE_CHANGED')
        text_literal(raw)
    operating_name = 'configs/scientific-operating-context.json'
    gate.require(operating_name in files, 'PREPARATION_OPERATING_MANIFEST_REQUIRED')
    operating = json.loads(files[operating_name]); authority = operating['authority_policy']
    gate.require(authority['path'] in files and gate.digest(files[authority['path']]) == authority['sha256'],
                 'PREPARATION_AUTHORITY_MANIFEST_CHANGED')
    policy = json.loads(files[authority['path']])
    policy_names = {**operating['documents'], policy['direction_path']: policy['direction_sha256']}
    gate.require(all(name in files and gate.digest(files[name]) == sha for name, sha in policy_names.items()),
                 'PREPARATION_ROLE_DOCUMENT_CHANGED')
    required = {name for name in files if Path(name).suffix in gate.CODE_SUFFIXES}
    required.update(policy_names); required.update({operating_name, authority['path'], 'scripts/pilot_review.py',
                                                   'orchestrator/deployment_review.py',
                                                   'orchestrator/prepare_deployment_bundle.py'})
    required.update(gate.replacement_review_files(files))
    if plan.get('review_profile') in ('operator-terminal-review/v1', 'server-terminal-review/v1'):
        required.update({'orchestrator/terminal_review.py', 'orchestrator/deployment_review.py',
                         'orchestrator/prepare_deployment_bundle.py',
                         'orchestrator/install_reviewed_deployment.py',
                         'orchestrator/inspection_admission_recovery.py'})
    gate.require(required <= set(files), 'PREPARATION_REQUIRED_SOURCE_MISSING')
    review_plan = None; review_plan_raw = None; references = {}
    if 'review_plan_file' in plan:
        review_plan_raw = text_literal(local_read(plan['review_plan_file']))
        review_plan = gate.coverage_plan(review_plan_raw, source, gate.digest(source_raw), files)
        for name, sha in review_plan['reference_files'].items():
            observed = subprocess.check_output(['git', '-c', 'credential.helper=', '-c', 'protocol.allow=never',
                                               'show', source+':'+name], cwd=root, env=env)
            gate.require(gate.digest(observed) == sha, 'PREPARATION_REFERENCE_SOURCE_CHANGED')
            references[name] = text_literal(observed)
        required = set(review_plan['required_files'])
    proposal = {'schema': gate.SCHEMA, 'profile': gate.PROFILE, 'source': source,
        'source_root': plan['source_root'], 'previous_source': plan['previous_source'],
        'previous_source_root': plan['previous_source_root'], 'archive_sha256': gate.digest(source_raw),
        'source_files': {name: gate.digest(raw) for name, raw in files.items()},
        'targets': {}, 'previous_files': {}, 'changes': []}
    if 'review_profile' in plan: proposal['review_profile'] = plan['review_profile']
    literals = {}
    for field in ('targets', 'previous_files'):
        for name, value in sorted(plan[field].items()):
            item, raw = metadata(value); proposal[field][name] = item; literals[item['sha256']] = raw
            if field == 'targets' and name.endswith('.json'):
                config = json.loads(raw)
                if name == '/etc/research-system/live-research/broker.json':
                    gate.require(isinstance(config, dict) and isinstance(config.get('sources'), list)
                        and 1 <= len(config['sources']) <= 16 and source in config['sources'],
                        'PREPARATION_CONFIGURATION_SOURCE_CHANGED')
                    for allowed in config['sources']: gate.pin(allowed, 40)
                else:
                    gate.require(isinstance(config, dict) and config.get('source') == source
                        and ('source_root' not in config or config['source_root'] == plan['source_root']),
                        'PREPARATION_CONFIGURATION_SOURCE_CHANGED')
    investigator_binding = investigator_target_binding(proposal['targets'], literals)
    lock=gate.REGISTRATION_LOCK_TARGET
    if lock in proposal['targets']:
        controller=json.loads(literals[proposal['targets']['/etc/research-system/live-research/controller.json']['sha256']])
        expected={'sha256':gate.digest(b''),'uid':0,'gid':controller.get('controller_gid'),'mode':0o600}
        gate.require(type(expected['gid']) is int and expected['gid']>0
            and proposal['targets'][lock]==expected and proposal['previous_files'].get(lock)==expected
            and literals[expected['sha256']]==b'', 'PREPARATION_UNCHANGED_REGISTRATION_LOCK_REQUIRED')
    dependencies, dependency_raw = dependency_inputs(plan['dependencies_file'])
    proposal['dependencies'] = dependencies
    recovery = text_literal(local_read(plan['recovery_file'], maximum=4000000))
    if 'review_profile' in plan:
        from orchestrator.install_reviewed_deployment import validate_recovery
        from orchestrator import recovery_inventory
        # Pages are siblings in the existing literal layout, never arbitrary paths
        # from the descriptor. Keep every page in the exact private review manifest.
        page_root = Path(plan['recovery_file']).parent/'literals'
        resolved, pages = recovery_inventory.resolve(json.loads(recovery),
            lambda sha: text_literal(local_read(page_root/sha, maximum=recovery_inventory.MAX_PAGE_BYTES)))
        validate_recovery(resolved, proposal)
        literals.update(pages)
    proposal['recovery_sha256'] = gate.digest(recovery); literals[gate.digest(recovery)] = recovery
    gate.require(isinstance(plan['changes'], list) and plan['changes'], 'PREPARATION_RECORDED_CHANGE_REQUIRED')
    change_files = {}; heads = {}
    for item in plan['changes']:
        gate.require(isinstance(item, dict) and set(item) == {'folder', 'applied'}, 'PREPARATION_CHANGE_BINDING_REQUIRED')
        binding, originals, head = original_change(item['folder'], item['applied'], source)
        gate.require(binding['request'] not in heads, 'PREPARATION_DUPLICATE_CHANGE_REQUEST')
        proposal['changes'].append(binding); heads[binding['request']] = head
        change_files.update({'change-inputs/'+binding['request']+'/'+name: raw for name, raw in originals.items()})
    if review_plan is not None:
        proposal['review_plan_sha256'] = gate.digest(review_plan_raw)
    proposal_raw = gate.encoded(proposal)
    selection_raw = gate.encoded(changes.review_bindings(source, gate.digest(proposal_raw), proposal['changes']))
    output = {'proposal.json': proposal_raw, 'source.tar.gz': source_raw,
              'change-bindings.json': selection_raw,
              'preparation-inputs/plan.json': plan_raw, 'preparation-inputs/dependencies.json': dependency_raw,
              **{'literals/'+sha: raw for sha, raw in literals.items()}, **change_files}
    # Source texts are included separately for a bounded exact courier invocation.
    output.update({'review-source/'+name: files[name] for name in sorted(required)})
    if review_plan is not None:
        output['review-plan.json'] = review_plan_raw
        output.update({'reference-source/'+name: raw for name, raw in references.items()})
        for part, assignment in {**review_plan['parts'], 'integration': review_plan['integration']}.items():
            output['review-files-'+part+'.json'] = gate.encoded(assignment)
    gate.require(sum(map(len, output.values())) <= 30000000, 'PREPARATION_PACKAGE_LIMIT')
    manifest = {'schema': SCHEMA, 'status': 'PREPARED_NOT_REVIEWED_NOT_INSTALLED',
        'source': source, 'proposal_sha256': gate.digest(proposal_raw),
        'archive_sha256': gate.digest(source_raw), 'source_file_sha256': proposal['source_files'],
        'courier_source_file_sha256': {name: gate.digest(files[name]) for name in sorted(required)},
        'courier_private_files': ['proposal.json', 'change-bindings.json', *sorted('literals/'+sha for sha in literals)],
        'courier_change_store': 'change-inputs', 'courier_change_bindings': 'change-bindings.json',
        'change_heads_at_preparation': heads,
        'file_sha256': {name: gate.digest(raw) for name, raw in output.items()},
        'investigator_evidence_binding': investigator_binding,
        'review_originals_attached': False, 'install_receipt_created': False,
        'host_observations_verified': False, 'models_started': 0, 'unattended_activated': False}
    if 'review_profile' in plan: manifest['review_profile'] = plan['review_profile']
    if review_plan is not None:
        manifest.update(review_plan_sha256=gate.digest(review_plan_raw),
            reference_only_file_sha256=review_plan['reference_files'],
            courier_review_file_manifests={part: 'review-files-'+part+'.json'
                for part in [*gate.PART_SCOPES, 'integration']})
        manifest['courier_private_files'].append('review-plan.json')
    destination = private_root(destination)
    for name, raw in output.items():
        parent = destination
        for component in Path(name).parent.parts:
            parent = private_root(parent/component)
        save_original(parent/Path(name).name, raw)
    # Check copied history using the ordinary reader; do not fabricate a REVIEW.
    for binding in proposal['changes']:
        copied = changes.load(destination/'change-inputs'/binding['request'])
        gate.require(copied['head_sha256'] == heads[binding['request']], 'PREPARATION_CHANGE_COPY_CHANGED')
    save_original(destination/'preparation.json', gate.encoded(manifest))
    return manifest


def assemble_components(bundle, part_a, part_b, destination):
    """Copy checked originals to a fresh private output; no provider or host operation.

    Keep the prepared change-input store untouched. Component outcomes are not
    REVIEW events and do not authorize installation or scientific execution.
    """
    gate.require(os.getuid() != 0, 'UNPRIVILEGED_PREPARATION_REQUIRED')
    bundle = Path(bundle).absolute(); destination = Path(destination).absolute()
    inputs = {'a': Path(part_a).absolute(), 'b': Path(part_b).absolute()}
    gate.require(not destination.exists() and not destination.is_symlink()
                 and not any(destination.is_relative_to(path) for path in [bundle, *inputs.values()]),
                 'FRESH_EXTERNAL_PREPARATION_REQUIRED')
    for path in [bundle, *inputs.values()]:
        info = path.lstat()
        gate.require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid()
                     and not info.st_mode & 0o077, 'PREPARATION_PRIVATE_ORIGINALS_REQUIRED')
    proposal_raw = local_read(bundle/'proposal.json'); proposal = json.loads(proposal_raw)
    archive = local_read(bundle/'source.tar.gz', maximum=10000000)
    files = gate.archive_inventory(archive)
    gate.require(gate.digest(archive) == proposal['archive_sha256']
                 and {name: gate.digest(raw) for name, raw in files.items()} == proposal['source_files'],
                 'PREPARATION_ARCHIVE_SOURCE_CHANGED')
    plan_raw = local_read(bundle/'review-plan.json')
    gate.require(gate.digest(plan_raw) == proposal.get('review_plan_sha256'), 'DEPLOYMENT_REVIEW_PLAN_CHANGED')
    plan = gate.coverage_plan(plan_raw, proposal['source'], proposal['archive_sha256'], files)
    originals = {}
    for part, folder in inputs.items():
        originals[part] = {}
        for name in gate.ORIGINAL_NAMES:
            info = (folder/name).lstat()
            gate.require(info.st_uid == os.getuid() and not info.st_mode & 0o077,
                         'PREPARATION_PRIVATE_ORIGINALS_REQUIRED')
            originals[part][name] = local_read(folder/name, maximum=4000000)
    manifest, _, _ = gate.checked_components(plan, plan_raw, proposal_raw, originals)
    output = {'component-receipts.json': gate.encoded(manifest)}
    for part, raw in originals.items():
        output.update({'component-reviews/'+part+'/'+name: value for name, value in raw.items()})
    gate.require(sum(map(len, output.values())) <= 30000000, 'PREPARATION_PACKAGE_LIMIT')
    destination = private_root(destination)
    for name, raw in output.items():
        parent = destination
        for component in Path(name).parent.parts:
            parent = private_root(parent/component)
        save_original(destination/name, raw)
    receipt = {'status': 'COMPONENT_ORIGINALS_PREPARED_NOT_DEPLOYMENT_APPROVAL',
        'source': proposal['source'], 'proposal_sha256': gate.digest(proposal_raw),
        'review_plan_sha256': gate.digest(plan_raw),
        'file_sha256': {name: gate.digest(raw) for name, raw in output.items()},
        'final_review_private_files': ['component-receipts.json',
            *['component-reviews/'+part+'/response.json' for part in gate.PART_SCOPES]],
        'models_started': 0, 'install_receipt_created': False, 'unattended_activated': False}
    save_original(destination/'component-preparation.json', gate.encoded(receipt))
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path); parser.add_argument('--source')
    parser.add_argument('--archive', type=Path); parser.add_argument('--plan', type=Path)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--assemble-components', action='store_true',
                        help='Copy two checked source reviews; no provider or host operation.')
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--part-a', type=Path); parser.add_argument('--part-b', type=Path)
    args = parser.parse_args(argv)
    if args.assemble_components:
        if not all((args.bundle, args.part_a, args.part_b)) or any((args.root, args.source, args.archive, args.plan)):
            parser.error('Component assembly requires --bundle --part-a --part-b only, with --destination.')
        result = assemble_components(args.bundle, args.part_a, args.part_b, args.destination)
    else:
        if not all((args.root, args.source, args.archive, args.plan)) or any((args.bundle, args.part_a, args.part_b)):
            parser.error('Preparation requires --root --source --archive --plan, with --destination.')
        result = prepare(args.root, args.source, args.archive, args.plan, args.destination)
    print(json.dumps({'status': result['status'], 'source': result['source'],
                      'proposal_sha256': result['proposal_sha256']}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
