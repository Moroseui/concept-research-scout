"""Fixed broker connection to reviewed Linux jobs and current operator controls.

No request chooses an executable, unit, configuration path or authority verifier.
Original provider proof stays in the root broker; change records are inspected as
its existing controller identity. Long jobs and completion polling use systemd.
"""
import argparse
from datetime import datetime, timezone
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
import tempfile
import subprocess
import sys

from orchestrator import linux_scientific_jobs as jobs
from orchestrator.hosted_cycle import encoded


OPERATIONS = frozenset(('register_scientific_job', 'dispatch_scientific_job',
    'scientific_job_status', 'observe_scientific_jobs', 'scientific_job_result',
    'register_scientific_validation', 'scientific_validation_result', 'scientific_validation_specification'))


def original_client(broker):
    def read(_socket, operation, body):
        if operation == 'stage_status':
            return broker.stage_status(body)
        if operation == 'stage_packet':
            return broker.stage_packet(body)
        raise ValueError('SCIENTIFIC_JOB_ORIGINAL_READ_ONLY')
    return read


def controller_configuration(broker):
    from orchestrator.handover_runtime import configuration
    path = broker.config.get('research_controller_config')
    if not path:
        raise ValueError('PROTECTED_RESEARCH_CONFIG_REQUIRED')
    value = configuration(path)
    if (value['controller_uid'] != broker.config['controller_uid']
            or value['source'] not in broker.config['sources']):
        raise ValueError('SCIENTIFIC_JOB_CONTROLLER_BINDING_CHANGED')
    return value


def verify_current_changes(config, references):
    """Runs under the existing controller UID, never as a fabricated human."""
    from orchestrator.research_catalog import linked_change
    if os.getuid() != config['controller_uid'] or not isinstance(references, list) or not 1 <= len(references) <= 3:
        raise ValueError('SCIENTIFIC_JOB_CHANGE_VERIFIER_IDENTITY')
    for ref in references:
        if not isinstance(ref, dict) or set(ref) != {'request_id', 'applied_event'}:
            raise ValueError('SCIENTIFIC_JOB_CHANGE_REFERENCE_REQUIRED')
        jobs.pin(ref['request_id']); jobs.pin(ref['applied_event'])
        linked_change(config, {'change_request': ref})
    return {'status': 'CURRENT_CHANGES_REVIEWED', 'references_sha256': hashlib.sha256(encoded(references)).hexdigest()}


def current_changes(broker, config, decision_paths):
    from orchestrator.formal_decisions import original_transport
    references = [original_transport(Path(path).parent.parent)['packet']['formal_request']['change_request']
                  for path in decision_paths]
    def controller_identity():
        os.setgroups([])
        os.setgid(config['controller_gid'])
        os.setuid(config['controller_uid'])
    root = config['source_root']
    result = subprocess.run([sys.executable, '-B', '-m', 'orchestrator.protected_scientific_jobs',
            '--verify-current-changes', '--controller-config', broker.config['research_controller_config']],
        input=encoded(references), cwd=root,
        env={'PATH': '/usr/bin:/bin', 'PYTHONPATH': root, 'PYTHONDONTWRITEBYTECODE': '1', 'GIT_NO_LAZY_FETCH': '1'},
        preexec_fn=controller_identity, capture_output=True, timeout=30)
    if result.returncode or len(result.stdout) > 10000:
        raise ValueError('SCIENTIFIC_JOB_CURRENT_CHANGE_REVIEW_REQUIRED')
    proof = json.loads(result.stdout)
    if (proof.get('status') != 'CURRENT_CHANGES_REVIEWED'
            or proof.get('references_sha256') != hashlib.sha256(encoded(references)).hexdigest()):
        raise ValueError('SCIENTIFIC_JOB_CHANGE_PROOF_CHANGED')
    return proof


@contextmanager
def admission_guard(broker, config):
    """Current pause/halt check shares the operator's existing admission lock."""
    state = Path(config['state'])
    lock = state/'admission.lock'
    database = state/'coordinator.sqlite'
    for path in (state, lock, database):
        if path.is_symlink() or path.stat().st_uid != config['controller_uid']:
            raise ValueError('SCIENTIFIC_JOB_EXISTING_CONTROL_STATE_REQUIRED')
    fd = os.open(lock, os.O_RDWR | os.O_NOFOLLOW)
    with os.fdopen(fd, 'r+') as stream:
        # A caller holding the lock must release it before this protected request.
        # Refuse promptly rather than deadlocking behind its own socket request.
        try: fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error: raise ValueError('SCIENTIFIC_JOB_ADMISSION_BUSY') from error
        db = sqlite3.connect(database.absolute().as_uri()+'?mode=ro', uri=True)
        try:
            control = db.execute('SELECT revision,paused FROM controls WHERE singleton=1').fetchone()
            if not control or control[1] != 0:
                raise ValueError('SCIENTIFIC_JOB_OPERATOR_PAUSED')
            blocked = db.execute("SELECT 1 FROM runtime_blocks WHERE phase='controls'").fetchone()
            if blocked:
                raise ValueError('SCIENTIFIC_JOB_CONTROL_TRANSPORT_BLOCKED')
            with broker.authentication():
                pin, ledger = broker.ledger.read()
            if ledger['halted']:
                raise ValueError('SCIENTIFIC_JOB_ADMISSION_HALTED')
            yield {'control_revision': control[0], 'ledger_pin': pin,
                   'ledger_sequence': ledger['sequence'], 'new_model_admissions': 0}
        finally:
            db.close()


def start_once(registry, proposal, proof):
    """Preserve an exclusive service-start intent; uncertainty never retries it."""
    if proposal['status'] != 'REGISTERED':
        return proposal
    attempt = jobs.pin(proposal['attempt'])
    unit = jobs.UNIT.format(attempt)
    if proposal['unit'] != unit:
        raise ValueError('SCIENTIFIC_JOB_FIXED_UNIT_REQUIRED')
    base = Path(registry.config['requests'])
    intent = base/(attempt+'.service-start-intent.json')
    outcome = base/(attempt+'.service-start-result.json')
    with jobs.lock(base/'.service-start.lock'):
        if outcome.exists():
            return json.loads(jobs.regular(outcome))
        if intent.exists() or intent.is_symlink():
            return {**proposal, 'status': 'SERVICE_START_UNCERTAIN_NO_RETRY', 'automatic_restart': False}
        value = {'schema': 'scientific-service-start/v1', 'attempt': attempt, 'unit': unit,
                 'checks': proof, 'status': 'INTENT', 'automatic_restart': False}
        jobs.original(intent, encoded(value), 0o600)
        result = subprocess.run(['systemctl', 'start', '--no-block', unit], capture_output=True, timeout=20)
        receipt = {**value, 'status': 'SERVICE_START_REQUEST_ACCEPTED' if result.returncode == 0 else 'SERVICE_START_FAILED_RECONCILE',
            'returncode': result.returncode,
            'stdout_sha256': hashlib.sha256(result.stdout).hexdigest(),
            'stderr_sha256': hashlib.sha256(result.stderr).hexdigest(),
            'scientific_acceptance': False}
        jobs.original(base/(attempt+'.service-start.stdout.txt'), result.stdout, 0o600)
        jobs.original(base/(attempt+'.service-start.stderr.txt'), result.stderr, 0o600)
        jobs.original(outcome, encoded(receipt), 0o600)
        return receipt


def handle(broker, operation, body):
    if os.getuid() != 0 or operation not in OPERATIONS:
        raise ValueError('SCIENTIFIC_JOB_PROTECTED_ROUTE_REQUIRED')
    config = controller_configuration(broker)
    job_path = broker.config.get('scientific_jobs_config')
    if not job_path or config.get('scientific_jobs_config') != job_path:
        raise ValueError('SCIENTIFIC_JOB_INSTALLED_CONFIG_REQUIRED')
    jc = jobs.configuration(job_path)
    if jc['source'] != config['source'] or jc['source_root'] != config['source_root']:
        raise ValueError('SCIENTIFIC_JOB_INSTALLED_SOURCE_CHANGED')
    registry = jobs.Registry(jc)
    try:
        return handle_registry(broker, config, registry, operation, body)
    finally:
        registry.db.close()


def handle_registry(broker, config, registry, operation, body):
    reader = original_client(broker)
    if operation in ('scientific_job_status', 'observe_scientific_jobs'):
        if body != {}:
            raise ValueError('SCIENTIFIC_JOB_STATUS_BODY')
        return registry.status() if operation == 'scientific_job_status' else {
            'events': registry.observe(), 'model_calls': 0, 'scientific_acceptance': False}
    if operation == 'scientific_job_result':
        if set(body) != {'completion'}:
            raise ValueError('SCIENTIFIC_JOB_RESULT_BODY')
        jobs.pin(body['completion'])
        from orchestrator.scientific_job_results import export_result
        return export_result(registry, body['completion'], original_client=reader)
    if operation in ('register_scientific_validation', 'scientific_validation_result', 'scientific_validation_specification'):
        keys = {'completion', 'decision_path'} if operation == 'register_scientific_validation' else {'completion'}
        if set(body) != keys:
            raise ValueError('SCIENTIFIC_VALIDATION_COMPLETION_BODY')
        jobs.pin(body['completion'])
        from orchestrator import scientific_validation as semantic
        if operation == 'scientific_validation_specification':
            return semantic.launch_specification(registry, body['completion'], original_client=reader)
        if operation == 'scientific_validation_result':
            return semantic.export_result(registry, body['completion'], original_client=reader)
        decision = Path(body['decision_path']).absolute()
        if ('..' in decision.parts or decision.name != 'decision.json' or decision.parent.name != 'round-1'
                or decision.parent.parent.parent != Path(config['state'])/'formal-decisions'):
            raise ValueError('SCIENTIFIC_VALIDATION_REGISTERED_DECISION_PATH_REQUIRED')
        with admission_guard(broker, config):
            binding = semantic.execution_binding(registry, body['completion'], original_client=reader)
            from orchestrator.campaign import require_no_human_stop
            core = binding['core']
            require_no_human_stop(config['source_root'], core['experiment'])
            require_no_human_stop(binding['artifact_root'], core['experiment'])
            version = Path(binding['artifact_root'])/core['scientific_version']['decision_path']
            current_changes(broker, config, [binding['decision_path'], binding['protocol_path'], version])
            current_changes(broker, config, [decision])
            return semantic.register(registry, body['completion'], decision, original_client=reader)
    if operation == 'register_scientific_job':
        if set(body) != {'core', 'decision_path'}:
            raise ValueError('SCIENTIFIC_JOB_REGISTRATION_BODY')
        core = body['core']
        jobs.validate_core(core)
        workspace = Path(registry.config['proposals'])/core['proposal_id']/'workspace'
        launch = Path(body['decision_path']).absolute()
        protocol = Path(core['protocol']['decision_path']).absolute()
        version = workspace/core['scientific_version']['decision_path']
        if ('..' in launch.parts or not (launch.is_relative_to(workspace)
                or launch.parent.parent.parent == Path(config['state'])/'formal-decisions')
                or not protocol.is_relative_to(workspace)):
            raise ValueError('SCIENTIFIC_JOB_REGISTERED_DECISION_PATH_REQUIRED')
        with admission_guard(broker, config):
            current_changes(broker, config, [launch, protocol, version])
            return registry.register_scientific(core, body['decision_path'], original_client=reader)
    if set(body) != {'job'}:
        raise ValueError('SCIENTIFIC_JOB_DISPATCH_BODY')
    jobs.identifier(body['job'])
    row = registry.get(body['job'])
    binding = json.loads(row['binding'])
    core = binding['core']
    with admission_guard(broker, config) as proof:
        from orchestrator.campaign import require_no_human_stop
        require_no_human_stop(config['source_root'], core['experiment'])
        require_no_human_stop(binding['artifact_root'], core['experiment'])
        version = Path(binding['artifact_root'])/core['scientific_version']['decision_path']
        proof['current_changes'] = current_changes(broker, config,
            [binding['decision_path'], binding['protocol_path'], version])
        if row['phase'] == 'scientific_validation':
            proof['validation_change'] = current_changes(broker, config,
                [Path(binding['validation_authority']['path'])])
        proposal = registry.dispatch(body['job'], original_client=reader)
        return start_once(registry, proposal, proof)



def observation_directory(config):
    return Path(config['state'])/'scientific-observation'


def read_observation(config):
    """Read protected metadata without waiting for the broker or any model."""
    if not config.get('scientific_jobs_config'):
        return {'status': 'DISABLED', 'events': [], 'jobs': [], 'model_calls': 0}
    folder = observation_directory(config)
    path = folder/'status.json'
    if not path.exists() and not path.is_symlink():
        return {'status': 'NOT_OBSERVED', 'events': [], 'jobs': [], 'model_calls': 0,
                'reason': 'Independent completion service has not published an observation.'}
    from orchestrator.handover_runtime import configuration
    value = configuration(path, maximum=750000, private_gid=config['controller_gid'])
    if (value.get('schema') != 'scientific-observation/v1' or value.get('source') != config['source']
            or value.get('scientific_acceptance') is not False or value.get('model_calls') != 0):
        raise ValueError('SCIENTIFIC_OBSERVATION_BINDING_CHANGED')
    observed = datetime.fromisoformat(value['observed_at'])
    if observed.tzinfo is None:
        raise ValueError('SCIENTIFIC_OBSERVATION_TIME_REQUIRED')
    age = (datetime.now(timezone.utc)-observed).total_seconds()
    return {**value, 'status': 'OBSERVED' if -30 <= age <= 300 else 'STALE_OBSERVATION',
            'age_seconds': max(0, int(age))}


def poll_completions(controller_path):
    """Independent root service: review gate, original result observation, no launch."""
    if os.getuid() != 0 or str(controller_path) != '/etc/research-system/live-research/controller.json':
        raise ValueError('SCIENTIFIC_COMPLETION_FIXED_ROOT_SERVICE_REQUIRED')
    from orchestrator.handover_runtime import configuration
    from orchestrator.deployment_review import verify_installed
    config = configuration(controller_path)
    root = Path(__file__).resolve().parents[1]
    if root != Path(config['source_root']):
        raise ValueError('SCIENTIFIC_COMPLETION_RUNNING_SOURCE_CHANGED')
    # This proof precedes Registry construction, observation or state mutation.
    verify_installed(root, config['source'], config_path=controller_path, config=config)
    jc = jobs.configuration(config['scientific_jobs_config'])
    if jc['source'] != config['source'] or jc['source_root'] != config['source_root']:
        raise ValueError('SCIENTIFIC_COMPLETION_JOB_SOURCE_CHANGED')
    folder = observation_directory(config)
    if folder.is_symlink():
        raise ValueError('SCIENTIFIC_OBSERVATION_DIRECTORY_REQUIRED')
    info = folder.stat()
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_gid != config['controller_gid']
            or info.st_mode & 0o027):
        raise ValueError('SCIENTIFIC_OBSERVATION_DIRECTORY_REQUIRED')
    with jobs.lock(folder/'.poll.lock'):
        registry = jobs.Registry(jc)
        try:
            events = registry.observe()
            status = registry.status()
        finally:
            registry.db.close()
        safe_events = [{key: row[key] for key in ('event', 'job', 'attempt', 'source',
                            'core_sha256', 'result_manifest_sha256')}
                       | {'outcome_status': row['outcome']['status'], 'scientific_acceptance': False}
                       for row in events]
        value = {'schema': 'scientific-observation/v1', 'source': config['source'],
            'observed_at': datetime.now(timezone.utc).isoformat(), 'events': safe_events,
            'jobs': status['jobs'], 'attempts': status['attempts'], 'analysis': status['analysis'],
            'model_calls': 0, 'scientific_acceptance': False, 'automatic_retry': False}
        raw = encoded(value)
        if len(raw) > 750000:
            raise ValueError('SCIENTIFIC_OBSERVATION_BOUND_REQUIRES_INSPECTION')
        descriptor, temporary = tempfile.mkstemp(prefix='.status-', dir=folder)
        try:
            with os.fdopen(descriptor, 'wb') as stream:
                os.fchown(stream.fileno(), 0, config['controller_gid'])
                os.fchmod(stream.fileno(), 0o640)
                stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            os.replace(temporary, folder/'status.json')
            directory = os.open(folder, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try: os.fsync(directory)
            finally: os.close(directory)
        finally:
            if os.path.exists(temporary): os.unlink(temporary)
        return {'status': 'OBSERVATION_RECORDED', 'source': config['source'],
                'jobs': len(status['jobs']), 'completion_events': len(safe_events),
                'observation_sha256': hashlib.sha256(raw).hexdigest(), 'model_calls': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument('--verify-current-changes', action='store_true')
    operation.add_argument('--poll-completions', action='store_true')
    parser.add_argument('--controller-config', required=True)
    args = parser.parse_args()
    if args.poll_completions:
        print(json.dumps(poll_completions(args.controller_config), sort_keys=True))
        return
    from orchestrator.handover_runtime import configuration
    config = configuration(args.controller_config)
    raw = sys.stdin.buffer.read(10001)
    if len(raw) > 10000:
        raise ValueError('SCIENTIFIC_JOB_CHANGE_INPUT_BOUND')
    print(json.dumps(verify_current_changes(config, json.loads(raw)), sort_keys=True))


if __name__ == '__main__':
    main()
