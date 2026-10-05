"""Mechanical job proposal from saved reviewed operations; no launch or judgment."""
import hashlib
import json
import os
from pathlib import Path

from orchestrator import linux_scientific_jobs as jobs
from orchestrator.hosted_cycle import encoded
from orchestrator.operations_report import private_root
from orchestrator.remote_supervisor import lock
from orchestrator.scientific_materialization import immutable, workspace, _read


def prepare_job(config, *, version_ref, protocol_ref, settings_ref, job_id, original_client, by):
    from orchestrator import continuing_operations as operations, continuing_research
    from orchestrator import scientific_versions, formal_decisions
    from orchestrator.change_requests import actor
    actor(by); jobs.identifier(job_id)
    if os.getuid() != config['controller_uid'] or config['controller_uid'] <= 0:
        raise ValueError('SCIENTIFIC_JOB_PREPARATION_CONTROLLER_REQUIRED')
    if not callable(original_client): raise ValueError('ORIGINAL_PROTECTED_MODEL_REPLIES_REQUIRED')
    installed = jobs.configuration(config.get('scientific_jobs_config', jobs.CONFIG))
    if (installed['source'] != config['source'] or installed['source_root'] != config['source_root'] or
            Path(installed['proposals']) != Path(config['state'])/'scientific-versions'):
        raise ValueError('SCIENTIFIC_JOB_INSTALLED_CONFIGURATION_CHANGED')
    version_result = operations.read_operation_result(config, version_ref, kinds=('APPROVE_VERSION',))['result']
    protocol_result = operations.read_operation_result(config, protocol_ref, kinds=('AUTHORIZE_PROTOCOL',))['result']
    attachment = version_result['attachment']; descriptor = attachment['descriptor']
    root, version = workspace(config, descriptor['core_sha256'])
    scientific_versions.verify_authority(root, descriptor, original_client=original_client)
    protocol = protocol_result['protocol']; continuing_research.protocol_descriptor(protocol)
    if (protocol['decision_sha256'] != version['protocol_decision_sha256'] or
            protocol['bindings']['source'] != config['source'] or
            protocol['bindings']['experiment'] != version['experiment']):
        raise ValueError('SCIENTIFIC_JOB_VERSION_PROTOCOL_CHANGED')
    original_protocol = Path(protocol['decision_path']).absolute()
    if (original_protocol.name != 'decision.json' or original_protocol.parent.name != 'round-1' or
            original_protocol.parent.parent.parent != Path(config['state'])/'formal-decisions'):
        raise ValueError('SCIENTIFIC_JOB_SAVED_PROTOCOL_ORIGINAL_REQUIRED')
    decision = formal_decisions.verify_original_decision(root, original_protocol,
        action='authorize_protocol', subject=protocol['subject'], bindings=protocol['bindings'],
        source=config['source'], original_client=original_client,
        expected_transition={'from': 'REVIEWED_PROTOCOL_PROPOSAL', 'to': 'PROTOCOL_ELIGIBLE'})
    if decision['decision'] != 'APPLY' or decision['_decision_sha256'] != protocol['decision_sha256']:
        raise ValueError('SCIENTIFIC_JOB_REVIEWED_PROTOCOL_REQUIRED')
    prefix = 'campaigns/isles24-pilot/experiments/'+version['experiment']+'/'
    settings_raw = continuing_research.read_reference(config, settings_ref)
    settings = json.loads(settings_raw)
    if (set(settings) != {'schema', 'settings', 'limits'} or settings['schema'] != 'linux-scientific-settings/v1'
            or not isinstance(settings['settings'], dict) or set(settings['limits']) != set(jobs.MAXIMUM)
            or any(type(value) is not int or not 0 < value <= jobs.MAXIMUM[key]
                   for key, value in settings['limits'].items())):
        raise ValueError('SCIENTIFIC_JOB_REVIEWED_BOUNDED_SETTINGS_REQUIRED')
    settings_name = prefix+'job-inputs/'+job_id+'/settings.json'
    files = {settings_name: settings_raw}
    fields = ('protocol_sha256', 'input_manifest_sha256', 'partition_registry_sha256',
              'exposure_history_sha256', 'literature_review_sha256', 'methodology_review_sha256')
    if set(protocol_result['artifacts']) != set(fields):
        raise ValueError('SCIENTIFIC_JOB_COMPLETE_PROTOCOL_ORIGINALS_REQUIRED')
    artifacts = {}
    protocol_base = 'campaigns/isles24-pilot/protocols/'+protocol['subject']+'/'
    for key in fields:
        reference = protocol_result['artifacts'][key]
        if reference['sha256'] != protocol['bindings'][key]:
            raise ValueError('SCIENTIFIC_JOB_REVIEWED_PROTOCOL_ARTIFACT_CHANGED')
        name = protocol_base+key.removesuffix('_sha256')+'.original'
        files[name] = continuing_research.read_reference(config, reference); artifacts[key] = name
    for name, raw in jobs._decision_files(original_protocol, providers=True).items():
        files[protocol_base+'round-1/'+name] = raw
    files[protocol_base+'authority-transport.json'] = _read(original_protocol.parent.parent/'authority-transport.json')
    requirements = {}
    for line in _read(root/(prefix+'requirements.txt')).decode().splitlines():
        if not line.strip() or line.lstrip().startswith('#'): continue
        pair = line.strip().split('==')
        if len(pair) != 2 or pair[0] in requirements:
            raise ValueError('LINUX_JOB_EXACT_REQUIREMENTS_REQUIRED')
        requirements[pair[0]] = pair[1]
    environment = jobs.environment(installed, requirements)
    all_files = dict(version['files'])
    all_files['scientific-version.json'] = descriptor['core_sha256']
    review_base = 'scientific-authority/'+version['version_id']+'/'
    for name, sha in attachment['files'].items():
        if hashlib.sha256(_read(root/(review_base+name))).hexdigest() != sha:
            raise ValueError('SCIENTIFIC_JOB_ORIGINAL_VERSION_REVIEW_CHANGED')
        all_files[review_base+name] = sha
    all_files.update({name: hashlib.sha256(raw).hexdigest() for name, raw in files.items()})
    core = {'schema': 'linux-scientific-job/v1', 'job_id': job_id, 'source': config['source'],
        'experiment': version['experiment'], 'proposal_id': descriptor['core_sha256'],
        'code': prefix+'run.py', 'spec': prefix+'SPEC.md', 'requirements': prefix+'requirements.txt',
        'settings': settings_name, 'input_manifest': artifacts['input_manifest_sha256'],
        'files': all_files, 'arguments': jobs.ARGUMENTS.copy(), 'environment': environment,
        'limits': settings['limits'], 'scientific_version': descriptor,
        'protocol': {**protocol, 'decision_path': str(root/(protocol_base+'round-1/decision.json')),
                     'artifacts': artifacts}}
    jobs.validate_core(core)
    # The private protocol and settings originals may add files, never overwrite
    # any existing proposed/executed scientific bytes or alter the version core.
    for name, raw in files.items():
        if (root/name).exists() and _read(root/name) != raw:
            raise ValueError('SCIENTIFIC_JOB_ORIGINAL_INPUT_DESTINATION_CONFLICT')
    parent = private_root(Path(config['state'])/'scientific-job-proposals'); folder = parent/job_id
    identity = {'version': version_ref, 'protocol': protocol_ref, 'settings': settings_ref,
                'job_core_sha256': jobs.digest(jobs.encoded(core)), 'source': config['source']}
    with lock(parent/'.preparation.lock'):
        if folder.exists():
            if not (folder/'prepared.json').exists():
                raise ValueError('SCIENTIFIC_JOB_PARTIAL_PREPARATION_RECONCILIATION_REQUIRED')
            saved = json.loads(_read(folder/'prepared.json'))
            if saved['identity'] != identity or saved['core'] != core:
                raise ValueError('SCIENTIFIC_JOB_SAVED_PROPOSAL_CHANGED')
            jobs.checked_inputs(installed, core, payloads=False, artifact_root=root)
            return {**saved, 'duplicate': True}
        private_root(folder); immutable(folder/'intent.json', encoded(identity))
        for name, raw in files.items():
            target = root/name; private_root(target.parent); immutable(target, raw)
        jobs.checked_inputs(installed, core, payloads=False, artifact_root=root)
        evidence = {'linux-job-core.json': jobs.encoded(core).decode(),
            'reviewed-specification.md': _read(root/core['spec']).decode(),
            'original-settings.json': settings_raw.decode(),
            'scientific-version.json': _read(root/'scientific-version.json').decode(),
            'original-protocol-decision.json': _read(original_protocol).decode(),
            'scientific-version-review.json': _read(root/descriptor['decision_path']).decode()}
        receipt = {'schema': 'scientific-job-preparation/v1', 'status': 'PENDING_LAUNCH_JUDGMENT',
            'identity': identity, 'core': core, 'decision_request': {**jobs.decision_request(core), 'evidence': evidence},
            'workspace': str(root), 'applied_by': by, 'model_calls': 0, 'scientific_acceptance': False}
        immutable(folder/'prepared.json', encoded(receipt))
        return {**receipt, 'duplicate': False}
