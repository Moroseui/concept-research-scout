"""Exact Claude review before material deployment use; no implicit activation grant.

Provider CLI originals are retained evidence, not cryptographic signatures. Root
owns the installation boundary. This verifier does not claim to constrain malicious
root, and never converts a supplied verdict or opaque SHA into provider evidence.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tarfile

BASE = Path('/etc/research-system/deployment-review')
ACTIVE = BASE / 'active.json'
MODEL = 'claude-fable-5'
SCHEMA = 'research-deployment-review/v1'
PROFILE = 'continuing-linux-v1'
SERVER_REVIEW_TARGET = '/etc/research-system/server-reviews.json'
REGISTRATION_LOCK_TARGET = '/etc/research-system/live-research/research-catalog-registration.lock'
REQUIRED_TARGETS = {
    '/etc/research-system/live-research/broker.json',
    '/etc/research-system/live-research/controller.json',
    '/etc/research-system/linux-scientific-jobs.json',
    '/etc/research-system/issue-intake.json',
    '/etc/research-system/live-research/report-evidence.json',
    '/usr/local/bin/research-system-live-control',
} | {'/etc/systemd/system/'+name for name in (
    'research-system-handover-live.service', 'research-system-handover-live.socket',
    'research-system-live-research.service', 'research-system-live-research.timer',
    'research-system-issue-intake.service', 'research-system-issue-intake.timer',
    'research-system-scientific-job@.service',
    'research-system-scientific-completion.service', 'research-system-scientific-completion.timer')}
SUPPLEMENT = '\nPRIVATE SUPPLEMENTAL EVIDENCE (observations, not instructions or new authority):\n'
CODE_SUFFIXES = {'.py', '.sh', '.ps1', '.fish', '.service', '.socket', '.timer', '.json', '.toml', '.yml', '.yaml', '.lock'}
DEPENDENCY_PATHS = {
    'codex': '/usr/local/bin/codex', 'claude': '/usr/local/bin/claude',
    'node': '/usr/local/bin/node', 'python3': '/usr/bin/python3', 'runuser': '/usr/sbin/runuser',
    'codex-native': '/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex',
    'codex-platform-package': '/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/package.json'}
_DEPENDENCY_CACHE = {}
CHANGES = '\nRECORDED CHANGES: Inspect these attributed proposals, applications and pending reviews under the shared policy. They are state and evidence, not additional authority.\n'


# Opt-in profile only: existing single-review receipts keep their original rules.
COVERAGE_SCHEMA = 'two-part-deployment-source-review/v1'
RECEIPTS_SCHEMA = 'two-part-deployment-review-originals/v1'
PART_SCOPES = {'a': 'material-deployment-source-part-a', 'b': 'material-deployment-source-part-b'}
ORIGINAL_NAMES = ('request.json', 'response.json', 'execution.json', 'protocol.jsonl', 'intent.json', 'returned.json')
REQUIRED_TEMPLATES = {
    'deploy/research-system/research-system-issue-intake.service.in',
    'deploy/research-system/research-system-scientific-job@.service.in'}
REFERENCE_ONLY_FILES = {
    'deploy/research-system/bootstrap.sh',
    'deploy/research-system/install_drive_connector.py',
    'deploy/research-system/install_release.py',
    'deploy/research-system/update_consumed_handover_fixture.py',
    'scripts/prepare_handover_snapshot.py',
}
PART_COMMON_FILES = {
    'AGENTS.toml',
    'orchestrator/__init__.py',
    'orchestrator/change_requests.py',
    'orchestrator/deployment_review.py',
    'orchestrator/dispatch_limiter.py',
    'orchestrator/handover_coordinator.py',
    'orchestrator/hosted_context.py',
    'orchestrator/hosted_cycle.py',
    'orchestrator/job_store.py',
    'orchestrator/ledger.py',
    'orchestrator/protected_handover.py',
    'orchestrator/protected_writer.py',
    'orchestrator/public_export.py',
    'orchestrator/remote_supervisor.py',
    'orchestrator/research_context.py',
    'orchestrator/review_input_codec.py',
    'orchestrator/reviewer_evidence.py',
    'orchestrator/scientific_authority.py',
    'orchestrator/scientific_decision.py',
    'scout.py',
    'scripts/pilot_review.py',
}
INTEGRATION_FILES = {
    'AGENTS.toml',
    'deploy/research-system/install_live_handover.py',
    'deploy/research-system/install_live_research.py',
    'deploy/research-system/research-system-issue-intake.service.in',
    'deploy/research-system/research-system-issue-intake.timer',
    'deploy/research-system/research-system-scientific-job@.service.in',
    'deploy/research-system/update_consumed_handover_fixture.py',
    'orchestrator/__init__.py',
    'orchestrator/actions_runner.py',
    'orchestrator/campaign.py',
    'orchestrator/campaign_lifecycle.py',
    'orchestrator/campaign_pipeline.py',
    'orchestrator/campaign_review.py',
    'orchestrator/change_requests.py',
    'orchestrator/completion_bridge.py',
    'orchestrator/continuing_operations.py',
    'orchestrator/continuing_research.py',
    'orchestrator/deployment_review.py',
    'orchestrator/dispatch_limiter.py',
    'orchestrator/formal_decisions.py',
    'orchestrator/git_diagnostics.py',
    'orchestrator/git_publication.py',
    'orchestrator/handover_coordinator.py',
    'orchestrator/handover_notifications.py',
    'orchestrator/handover_runtime.py',
    'orchestrator/hosted_campaign.py',
    'orchestrator/hosted_campaign_task.py',
    'orchestrator/hosted_context.py',
    'orchestrator/hosted_cycle.py',
    'orchestrator/human_controls.py',
    'orchestrator/install_reviewed_deployment.py',
    'orchestrator/investigator_wakes.py',
    'orchestrator/issue_intake.py',
    'orchestrator/issue_intake_service.py',
    'orchestrator/job_store.py',
    'orchestrator/ledger.py',
    'orchestrator/linux_scientific_jobs.py',
    'orchestrator/operations_report.py',
    'orchestrator/phone_notifications.py',
    'orchestrator/prepare_deployment_bundle.py',
    'orchestrator/protected_handover.py',
    'orchestrator/protected_investigator.py',
    'orchestrator/protected_scientific_jobs.py',
    'orchestrator/protected_writer.py',
    'orchestrator/protocol_proposals.py',
    'orchestrator/public_export.py',
    'orchestrator/publication.py',
    'orchestrator/publication_candidate.py',
    'orchestrator/recorded_steering.py',
    'orchestrator/remote_supervisor.py',
    'orchestrator/report_delivery.py',
    'orchestrator/research_catalog.py',
    'orchestrator/research_context.py',
    'orchestrator/research_task_authority.py',
    'orchestrator/review_input_codec.py',
    'orchestrator/reviewer_evidence.py',
    'orchestrator/scientific_authority.py',
    'orchestrator/scientific_decision.py',
    'orchestrator/scientific_job_inputs.py',
    'orchestrator/scientific_job_results.py',
    'orchestrator/scientific_materialization.py',
    'orchestrator/scientific_versions.py',
    'scout.py',
    'scripts/pilot_review.py',
}


def require(value, reason):
    if not value:
        raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def pin(value, size=64):
    require(isinstance(value, str) and re.fullmatch('[0-9a-f]{'+str(size)+'}', value),
            'DEPLOYMENT_EXACT_IDENTITY_REQUIRED')
    return value


def protected(path, *, directory=False):
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts, 'DEPLOYMENT_PROTECTED_PATH_REQUIRED')
    for current in (path, *path.parents):
        try:
            info = current.lstat()
        except FileNotFoundError:
            raise ValueError('DEPLOYMENT_PROTECTED_INPUT_MISSING') from None
        is_directory = directory or current != path
        require((stat.S_ISDIR(info.st_mode) if is_directory else stat.S_ISREG(info.st_mode))
                and info.st_uid == 0 and not info.st_mode & 0o022,
                'DEPLOYMENT_ROOT_PROTECTED_INPUT_REQUIRED')
    return info if path == Path('/') else path.lstat()


def file_identity(info):
    # A read may legitimately update atime; identity and modification may not change.
    return (info.st_dev, info.st_ino, info.st_uid, info.st_gid, info.st_mode,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def read(path, *, maximum=4000000):
    before = protected(path)
    require(before.st_size <= maximum, 'DEPLOYMENT_INPUT_TOO_LARGE')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        require((opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns)
                == (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns),
                'DEPLOYMENT_INPUT_CHANGED')
        raw = stream.read(maximum+1)
        require(file_identity(os.fstat(stream.fileno())) == file_identity(opened) and len(raw) <= maximum,
                'DEPLOYMENT_INPUT_CHANGED')
        return raw


def access(path):
    info = Path(path).lstat()
    return info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode)



def dependency_metadata(name):
    """Hash the fixed launcher, caching only unchanged protected inode metadata."""
    path = Path(DEPENDENCY_PATHS[name])
    protected(path.parent, directory=True)
    alias = path.lstat()
    require(alias.st_uid == 0 and (stat.S_ISLNK(alias.st_mode) or not alias.st_mode & 0o022),
            'DEPLOYMENT_LAUNCHER_ALIAS_CHANGED')
    resolved = path.resolve(strict=True); info = protected(resolved)
    require(info.st_size <= 400000000, 'DEPLOYMENT_LAUNCHER_TOO_LARGE')
    key = (str(resolved), info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns,
           info.st_ctime_ns, info.st_uid, info.st_gid, info.st_mode)
    if key not in _DEPENDENCY_CACHE:
        value = hashlib.sha256()
        fd = os.open(resolved, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, 'rb') as stream:
            require(file_identity(os.fstat(stream.fileno())) == file_identity(info), 'DEPLOYMENT_LAUNCHER_CHANGED_DURING_READ')
            for chunk in iter(lambda: stream.read(1048576), b''):
                value.update(chunk)
            require(file_identity(os.fstat(stream.fileno())) == file_identity(info), 'DEPLOYMENT_LAUNCHER_CHANGED_DURING_READ')
        if len(_DEPENDENCY_CACHE) > 32:
            _DEPENDENCY_CACHE.clear()
        _DEPENDENCY_CACHE[key] = value.hexdigest()
    return {'path': str(path), 'resolved': str(resolved), 'sha256': _DEPENDENCY_CACHE[key],
            'bytes': info.st_size, 'uid': info.st_uid, 'gid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode)}


def running_broker(source_root):
    """Read the actual systemd MainPID, not the configured source label alone."""
    require(Path(__file__).resolve().parents[1] == Path(source_root).resolve(strict=True),
            'DEPLOYMENT_EXECUTING_VERIFIER_SOURCE_CHANGED')
    result = subprocess.run(['/usr/bin/systemctl', 'show', 'research-system-handover-live.service',
                             '--property=MainPID', '--value'], capture_output=True, text=True, timeout=10)
    require(result.returncode == 0 and re.fullmatch('[1-9][0-9]*', result.stdout.strip()),
            'DEPLOYMENT_RUNNING_BROKER_REQUIRED')
    pid = int(result.stdout)
    require((Path('/proc')/str(pid)/'cwd').resolve(strict=True) == Path(source_root),
            'DEPLOYMENT_RUNNING_BROKER_SOURCE_CHANGED')
    return {'main_pid': pid, 'cwd': str(source_root)}

def review_originals(raw, source, *, policy_baseline=None):
    # Component scopes must never become standalone deployment authority.
    return _review_originals(raw, source, {'human-controls', 'material-deployment'},
                             policy_baseline=policy_baseline)


def _review_originals(raw, source, scopes, *, policy_baseline=None):
    """Reuse the courier's actual protocol/schema checks, plus literal prompt proof."""
    request, response, execution, intent, returned = (
        json.loads(raw[name]) for name in ('request.json', 'response.json', 'execution.json',
                                         'intent.json', 'returned.json'))
    events = [json.loads(line) for line in raw['protocol.jsonl'].splitlines() if line]
    results = [event for event in events if event.get('type') == 'result']
    init = [event for event in events if event.get('type') == 'system' and event.get('subtype') == 'init']
    models = sorted({event.get('message', {}).get('model', 'unknown') for event in events
                     if event.get('type') == 'assistant'})
    sessions = {event.get('session_id') for event in events if event.get('session_id')}
    judgment = response.get('structured_output', {})
    require(len(results) == 1 and results[0] == response and len(init) == 1
            and init[0].get('tools') == ['StructuredOutput'] and init[0].get('mcp_servers') == []
            and init[0].get('permissionMode') == 'dontAsk' and models == [MODEL]
            and sessions == {response.get('session_id')} and response.get('session_id')
            and response.get('subtype') == 'success' and response.get('is_error') is False
            and response.get('type') == 'result', 'DEPLOYMENT_ORIGINAL_CLAUDE_PROTOCOL_REQUIRED')
    require(set(judgment) == {'scope', 'reviewed_commit', 'verdict', 'findings'}
            and judgment['verdict'] == 'APPROVE' and judgment['scope'] == request.get('scope')
            and judgment['scope'] in scopes
            and judgment['reviewed_commit'] == request.get('reviewed_commit') == source
            and isinstance(judgment['findings'], list)
            and all(isinstance(v, str) for v in judgment['findings']),
            'DEPLOYMENT_EXACT_APPROVING_REVIEW_REQUIRED')
    require(execution.get('returncode') == returned.get('returncode') == 0
            and execution.get('reviewed_commit') == intent.get('reviewed_commit') == source
            and intent.get('maximum_invocations') == 1 and intent.get('automatic_retry') is False
            and execution.get('requested_model') == MODEL
            and execution.get('assistant_message_models') == models
            and execution.get('request_sha256') == intent.get('request_sha256') == digest(raw['request.json'])
            and execution.get('response_sha256') == digest(raw['response.json'])
            and execution.get('protocol_sha256') == digest(raw['protocol.jsonl'])
            and execution.get('prompt_sha256') == digest(request['prompt'].encode())
            and execution.get('input_file_sha256') == request.get('input_file_sha256'),
            'DEPLOYMENT_ORIGINAL_REVIEW_BINDING_CHANGED')
    prompt = request['prompt']
    from orchestrator import review_input_codec as presentation
    if 'input_presentation' in request:
        presentation.parsed(raw['request.json'])  # New envelopes refuse duplicate format/metadata claims.
        baseline = None
        if request['input_presentation'] == presentation.FORMAT_V2:
            from orchestrator.inspection_bootstrap import validate_policy_baseline, validate_context
            anchor = validate_policy_baseline(policy_baseline)
            baseline = anchor['descriptor']
            require(request.get('policy_baseline') == baseline and execution.get('policy_baseline') == baseline,
                    'DEPLOYMENT_REVIEW_POLICY_BASELINE_CHANGED')
        else:
            require(policy_baseline is None and 'policy_baseline' not in request,
                    'DEPLOYMENT_LEGACY_POLICY_BASELINE_RELABEL')
        sources, supplements, changes = presentation.decode_presentation(
            prompt, request['scope'], source, request.get('shared_context_sha256'),
            input_presentation=request['input_presentation'], expected_baseline=baseline)
        if baseline is not None:
            reader = presentation.Reader(prompt.encode())
            reader.literal(presentation.PREFIX_V2.encode())
            reader.line()
            reader.frame('baseline', 'approved-policy-baseline')
            _, shown = reader.frame('context', 'shared-role-context')
            context_raw = presentation.restore_context_v2(presentation.parsed(shown), sources,
                                                        request['shared_context_sha256'])
            validate_context(context_raw, anchor['source_text'])
    else:
        require(policy_baseline is None and 'policy_baseline' not in request
                and not prompt.startswith((presentation.PREFIX, presentation.PREFIX_V2)),
                'DEPLOYMENT_REVIEW_FORMAT_REQUIRED')
        heading = ('Fresh author-operated Fable implementation review, not execution worker or independent merge desk. '
                   'Scope '+request['scope']+' at '+source+'.')
        require(prompt.count(heading) == 1 and SUPPLEMENT in prompt, 'DEPLOYMENT_COURIER_PROMPT_REQUIRED')
        start = prompt.index('Source:\n', prompt.index(heading)) + len('Source:\n')
        sources, consumed = json.JSONDecoder().raw_decode(prompt[start:])
        require(prompt[start+consumed:].startswith(SUPPLEMENT), 'DEPLOYMENT_COURIER_PROMPT_REQUIRED')
        supplements = json.loads(prompt[start+consumed+len(SUPPLEMENT):])
    require(isinstance(sources, dict) and isinstance(supplements, dict)
            and all(isinstance(name, str) and isinstance(value, str) for name, value in sources.items()),
            'DEPLOYMENT_LITERAL_SOURCE_REQUIRED')
    require({name: digest(value.encode()) for name, value in sources.items()} == request['input_file_sha256'],
            'DEPLOYMENT_REVIEWED_SOURCE_TEXT_CHANGED')
    require(all(isinstance(value, dict) and set(value) == {'sha256', 'content'}
                and isinstance(value['content'], str) and digest(value['content'].encode()) == value['sha256']
                for value in supplements.values())
            and {name: value['sha256'] for name, value in supplements.items()} == request.get('private_evidence_sha256'),
            'DEPLOYMENT_REVIEWED_PRIVATE_TEXT_CHANGED')
    require(request.get('runner_sha256') == request['input_file_sha256'].get('scripts/pilot_review.py'),
            'DEPLOYMENT_ACTUAL_COURIER_SOURCE_REQUIRED')
    if 'input_presentation' not in request:
        require(CHANGES in prompt, 'DEPLOYMENT_ORIGINAL_CHANGE_CONTEXT_REQUIRED')
        change_text = prompt.split(CHANGES, 1)[1]
        changes, _ = json.JSONDecoder().raw_decode(change_text)
    require(digest(json.dumps(changes, sort_keys=True).encode()) == request.get('change_context_sha256'),
            'DEPLOYMENT_ORIGINAL_CHANGE_CONTEXT_CHANGED')
    return {'request': request, 'response': response, 'execution': execution, 'changes': changes,
            'source_text': sources, 'private_text': {value['sha256']: value['content'].encode()
                                                   for value in supplements.values()}}


def archive_inventory(raw):
    require(len(raw) <= 10000000, 'DEPLOYMENT_ARCHIVE_TOO_LARGE')
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        members = archive.getmembers()
        require(len(members) <= 2000 and sum(item.size for item in members) <= 20000000,
                'DEPLOYMENT_ARCHIVE_EXPANSION_LIMIT')
        for item in members:
            path = Path(item.name)
            require(not path.is_absolute() and '..' not in path.parts and path.parts[0] == 'snapshot'
                    and (item.isdir() or item.isfile()), 'DEPLOYMENT_ARCHIVE_MEMBER_REFUSED')
            if item.isfile() and '.git' not in path.parts:
                name = Path(*path.parts[1:]).as_posix()
                require(name not in files, 'DEPLOYMENT_ARCHIVE_DUPLICATE')
                files[name] = archive.extractfile(item).read()
    require(files, 'DEPLOYMENT_SOURCE_INVENTORY_REQUIRED')
    return files


def selected_review_applications(review, proposal_raw, source):
    """Validate explicit applications delivered with the exact deployment proposal."""
    from orchestrator import change_requests as changes
    selected = [row for store in review['changes']
                for row in store.get('projection', {}).get('selected_applications', [])]
    selection_sha = review['request'].get('change_bindings_sha256')
    if not selected and selection_sha is None:
        return []  # Preserve original, complete small-context review receipts.
    raw = review['private_text'].get(pin(selection_sha))
    require(raw is not None, 'DEPLOYMENT_SELECTION_NOT_ACTUALLY_REVIEWED')
    proposal = json.loads(proposal_raw)
    require(json.loads(raw) == changes.review_bindings(source, digest(proposal_raw), proposal['changes']),
            'DEPLOYMENT_REVIEW_SELECTION_CHANGED')
    require(all(isinstance(row, dict) and isinstance(row.get('event'), dict) for row in selected),
            'DEPLOYMENT_SELECTED_APPLICATION_REQUIRED')
    identities = [{'request': row.get('request'), 'applied': row['event'].get('identity')} for row in selected]
    changes._review_selections(identities)
    require(sorted(identities, key=lambda row: row['request'])
            == sorted(proposal['changes'], key=lambda row: row['request']),
            'DEPLOYMENT_REVIEW_SELECTION_CHANGED')
    require(len(changes.encoded(selected)) <= changes.MAX_SELECTED_REVIEW_BYTES,
            'DEPLOYMENT_SELECTED_APPLICATION_BYTES_EXCEEDED')
    require(all(row['event'].get('event') == 'APPLIED'
                and isinstance(row['event'].get('payload'), dict)
                and isinstance(row['event']['payload'].get('result_binding'), dict)
                and row['event']['payload']['result_binding'].get('source') == source for row in selected),
            'DEPLOYMENT_SELECTED_APPLICATION_SOURCE_CHANGED')
    return selected


def _review_model(review):
    """Use actual model identity only after the selected original proof validates."""
    if review.get('inspection_profile') == 'direct-inspection/v1':
        from orchestrator import inspection_deployment
        return inspection_deployment.review_model(review)
    if review.get('terminal_profile') in ('operator-terminal-review/v1', 'server-terminal-review/v1'):
        return review['terminal_session']['provider_model']
    return MODEL


def change_review(bundle, binding, review, *, selected=()):
    """Validate the existing original event chain; never trust an exported verdict."""
    from orchestrator import change_requests as changes
    folder = bundle/'changes'/pin(binding['request'])
    request_raw = read(folder/'request.json', maximum=100000)
    request = changes._request(json.loads(request_raw))
    require(request['identity'] == binding['request'], 'DEPLOYMENT_CHANGE_REQUEST_CHANGED')
    prior = digest(request_raw); events = []; original_heads = {prior: 0}
    for path in sorted((folder/'events').iterdir()):
        if path.name == '.lock':
            continue
        raw = read(path, maximum=100000); event = json.loads(raw)
        core = {key: value for key, value in event.items() if key != 'identity'}
        require(event.get('schema') == changes.EVENT_SCHEMA and event.get('request_identity') == request['identity']
                and event.get('sequence') == len(events)+1 and event.get('previous_sha256') == prior
                and event.get('identity') == digest(changes.encoded(core))
                and path.name == f'{len(events)+1:04d}-{event["identity"]}.json',
                'DEPLOYMENT_CHANGE_CHAIN_CHANGED')
        changes.actor(event['actor']); changes._transition(events, event['event'], event['payload'])
        events.append(event); prior = digest(raw); original_heads[prior] = len(events)
    applications = {event['identity'] for event in events if event['event'] == 'APPLIED'}
    superseded = {identity for event in events if event['event'] == 'APPLIED'
                  for identity in event['payload'].get('supersedes_applied_events', [])}
    active = applications - superseded
    require(active == {binding['applied']}, 'DEPLOYMENT_SINGLE_ACTIVE_APPLICATION_REQUIRED')
    for identity in active:
        verdicts = [event['payload']['verdict'] for event in events if event['event'] == 'REVIEW'
                    and event['payload'].get('applied_event') == identity]
        require(verdicts and all(verdict == 'APPROVE' for verdict in verdicts),
                'DEPLOYMENT_ACTIVE_CHANGE_PENDING_OR_NEGATIVE')
    applied = [event for event in events if event['identity'] == binding['applied'] and event['event'] == 'APPLIED']
    outcomes = [event for event in events if event['event'] == 'REVIEW'
                and event['payload'].get('applied_event') == binding['applied']]
    require(len(applied) == 1 and outcomes and all(event['payload']['verdict'] == 'APPROVE' for event in outcomes),
            'DEPLOYMENT_CHANGE_REVIEW_PENDING_OR_NEGATIVE')
    require(not any(binding['applied'] in event['payload'].get('supersedes_applied_events', [])
                    for event in events if event['event'] == 'APPLIED'), 'DEPLOYMENT_SUPERSEDED_APPLICATION')
    supplied = [row for store in review['changes'] for row in store.get('projection', {}).get('requests', [])
                if row.get('identity') == binding['request']]
    original_in_context = any(any(event.get('identity') == binding['applied'] and event.get('event') == 'APPLIED'
                                  and event.get('payload') == applied[0]['payload']
                                  and event.get('actor') == applied[0]['actor'] for event in row.get('events', []))
                              for row in supplied)
    selected_original = any(row.get('request') == binding['request'] and row.get('event') == applied[0]
                            and row.get('request_sha256') == digest(request_raw)
                            and original_heads.get(row.get('record_head_sha256'), -1) >= applied[0]['sequence']
                            and all(row.get(key) == request[key] for key in
                                    ('target', 'requested_change', 'submitter', 'scope_limits')) for row in selected)
    require(selected_original if selected else original_in_context, 'DEPLOYMENT_APPLICATION_NOT_IN_ACTUAL_REVIEW')
    expected = {'request_sha256': review['execution']['request_sha256'],
                'response_sha256': review['execution']['response_sha256'],
                'protocol_sha256': review['execution']['protocol_sha256']}
    require(any(event['actor'].get('kind') == 'agent' and event['actor'].get('family') == 'claude'
                and event['actor'].get('model') == _review_model(review)
                and event['actor'].get('session_id') == review['response']['session_id']
                and event['payload'].get('original_review') == expected for event in outcomes),
            'DEPLOYMENT_CHANGE_ORIGINAL_CLAUDE_REVIEW_REQUIRED')
    return prior


def replacement_review_files(files):
    """Keep legacy receipts while requiring the new authority route when used."""
    module='orchestrator/authority_replacements.py'
    entrypoints=('orchestrator/handover_runtime.py','orchestrator/continuing_operations.py')
    used=module in files or any(b'authority_replacements' in files.get(name,b'') for name in entrypoints)
    if not used:return set()
    require(module in files, 'DEPLOYMENT_REPLACEMENT_AUTHORITY_SOURCE_MISSING')
    return {module}


def coverage_requirements(files):
    """Derive the new profile from installed bytes, never a caller's coverage list."""
    operating_name = 'configs/scientific-operating-context.json'
    require(operating_name in files, 'DEPLOYMENT_OPERATING_MANIFEST_REQUIRED')
    operating = json.loads(files[operating_name]); authority = operating['authority_policy']
    require(authority['path'] in files and digest(files[authority['path']]) == authority['sha256'],
            'DEPLOYMENT_AUTHORITY_MANIFEST_CHANGED')
    policy = json.loads(files[authority['path']])
    policy_names = {**operating['documents'], policy['direction_path']: policy['direction_sha256']}
    require(all(name in files and digest(files[name]) == sha for name, sha in policy_names.items()),
            'DEPLOYMENT_ROLE_DOCUMENT_CHANGED')
    policy_names = set(policy_names) | {operating_name, authority['path']}
    required = ({name for name in files if Path(name).suffix in CODE_SUFFIXES} | policy_names
                | REQUIRED_TEMPLATES | PART_COMMON_FILES
                | (INTEGRATION_FILES - REFERENCE_ONLY_FILES) | replacement_review_files(files))
    require(required <= set(files), 'DEPLOYMENT_REQUIRED_SOURCE_MISSING')
    return {name: digest(files[name]) for name in sorted(required)}, policy_names


def coverage_plan(plan_raw, source, archive_sha, files):
    """Validate an acyclic, pre-call plan; no review receipt may be put in it."""
    from orchestrator.review_input_codec import parsed
    plan = parsed(plan_raw)
    require(isinstance(plan, dict) and set(plan) == {
        'schema', 'source', 'archive_sha256', 'shared_context_sha256', 'required_files',
        'reference_files', 'parts', 'integration', 'shared_evidence_sha256'}
        and plan['schema'] == COVERAGE_SCHEMA and plan['source'] == source
        and plan['archive_sha256'] == archive_sha, 'DEPLOYMENT_COVERAGE_PLAN_REQUIRED')
    pin(plan['shared_context_sha256'])
    required, policy = coverage_requirements(files)
    require(plan['required_files'] == required, 'DEPLOYMENT_NAMED_REQUIRED_COVERAGE_CHANGED')
    refs = plan['reference_files']
    require(isinstance(refs, dict) and set(refs) == REFERENCE_ONLY_FILES
            and not set(refs) & set(files), 'DEPLOYMENT_REFERENCE_ONLY_PROFILE_REQUIRED')
    for sha in refs.values(): pin(sha)
    known = {**{name: digest(raw) for name, raw in files.items()}, **refs}
    require(isinstance(plan['parts'], dict) and set(plan['parts']) == set(PART_SCOPES),
            'DEPLOYMENT_TWO_SOURCE_PARTS_REQUIRED')
    for assignment in [*plan['parts'].values(), plan['integration']]:
        require(isinstance(assignment, dict) and assignment
                and all(name in known and known[name] == sha for name, sha in assignment.items()),
                'DEPLOYMENT_NAMED_SOURCE_ASSIGNMENT_CHANGED')
    for assignment in plan['parts'].values():
        require(PART_COMMON_FILES | policy <= set(assignment), 'DEPLOYMENT_PART_COMMON_SOURCE_REQUIRED')
    require(set(required) | set(refs) <= set(plan['parts']['a']) | set(plan['parts']['b']),
            'DEPLOYMENT_COMPLETE_NAMED_COVERAGE_REQUIRED')
    require(INTEGRATION_FILES | policy | replacement_review_files(files) <= set(plan['integration']),
            'DEPLOYMENT_INTEGRATION_SOURCE_REQUIRED')
    evidence = plan['shared_evidence_sha256']
    require(isinstance(evidence, list) and 1 <= len(evidence) <= 256
            and len(evidence) == len(set(evidence)), 'DEPLOYMENT_SHARED_CRITICISM_REQUIRED')
    for sha in evidence: pin(sha)
    return plan


def planned_review(review, plan, plan_raw, proposal_raw, assignment):
    """Require named complete source and the identical frozen policy/change inputs."""
    from orchestrator import review_input_codec as presentation
    request = review['request']
    require(request.get('input_presentation') in {presentation.FORMAT, presentation.FORMAT_V2}
            and request.get('shared_context_sha256') == plan['shared_context_sha256']
            and request.get('reviewed_commit') == plan['source'],
            'DEPLOYMENT_SAME_ORIGINAL_CONTEXT_REQUIRED')
    # The codec reconstructed this hash from actual full policy/source text.
    require(request['input_file_sha256'] == assignment,
            'DEPLOYMENT_EXACT_REVIEW_ASSIGNMENT_REQUIRED')
    private = review['private_text']
    require(private.get(digest(plan_raw)) == plan_raw and private.get(digest(proposal_raw)) == proposal_raw,
            'DEPLOYMENT_PLAN_AND_PROPOSAL_NOT_REVIEWED')
    require(all(sha in private for sha in plan['shared_evidence_sha256']),
            'DEPLOYMENT_SHARED_CRITICISM_NOT_REVIEWED')
    require(selected_review_applications(review, proposal_raw, plan['source']),
            'DEPLOYMENT_PLANNED_SELECTION_REQUIRED')
    return (request['shared_context_sha256'], request['change_context_sha256'],
            request['change_bindings_sha256'])


def checked_components(plan, plan_raw, proposal_raw, originals):
    """Internal source-component verification; it confers no deployment approval."""
    require(isinstance(originals, dict) and set(originals) == set(PART_SCOPES),
            'DEPLOYMENT_TWO_SOURCE_PARTS_REQUIRED')
    reviews = {}; context = None; sessions = set()
    for part, scope in PART_SCOPES.items():
        raw = originals[part]
        require(isinstance(raw, dict) and set(raw) == set(ORIGINAL_NAMES)
                and all(isinstance(value, bytes) and len(value) <= 4000000 for value in raw.values()),
                'DEPLOYMENT_COMPONENT_ORIGINALS_REQUIRED')
        review = _review_originals(raw, plan['source'], {scope})
        binding = planned_review(review, plan, plan_raw, proposal_raw, plan['parts'][part])
        require(context is None or context == binding, 'DEPLOYMENT_FROZEN_REVIEW_CONTEXT_CHANGED')
        context = binding
        session = review['response']['session_id']
        require(session not in sessions, 'DEPLOYMENT_DISTINCT_COMPONENT_ORIGINALS_REQUIRED')
        sessions.add(session); reviews[part] = review
    manifest = {'schema': RECEIPTS_SCHEMA, 'source': plan['source'],
        'review_plan_sha256': digest(plan_raw), 'proposal_sha256': digest(proposal_raw),
        'parts': {part: {'scope': PART_SCOPES[part], 'session': reviews[part]['response']['session_id'],
            'original_sha256': {name: digest(raw[name]) for name in ORIGINAL_NAMES}}
            for part, raw in originals.items()}}
    return manifest, reviews, context


def composed_review(bundle, proposal, proposal_raw, files, final_review):
    """Require original complete parts plus one exact final integration judgment."""
    return composed_review_bytes(proposal, proposal_raw, files, final_review,
        read(bundle/'review-plan.json'),
        {part: {name: read(bundle/'component-reviews'/part/name) for name in ORIGINAL_NAMES}
         for part in PART_SCOPES}, read(bundle/'component-receipts.json'))


def composed_review_bytes(proposal, proposal_raw, files, final_review, plan_raw, originals, manifest_raw):
    """Pure proof for protected loader and unprivileged freeze preflight alike."""
    from orchestrator.review_input_codec import parsed
    require(parsed(proposal_raw) == proposal
            and {name: digest(raw) for name, raw in files.items()} == proposal['source_files'],
            'DEPLOYMENT_SOURCE_INVENTORY_CHANGED')
    require(digest(plan_raw) == pin(proposal['review_plan_sha256']), 'DEPLOYMENT_REVIEW_PLAN_CHANGED')
    plan = coverage_plan(plan_raw, proposal['source'], proposal['archive_sha256'], files)
    manifest, reviews, context = checked_components(plan, plan_raw, proposal_raw, originals)
    require(parsed(manifest_raw) == manifest, 'DEPLOYMENT_COMPONENT_RECEIPTS_CHANGED')
    require(final_review['request']['scope'] == 'material-deployment',
            'DEPLOYMENT_FINAL_INTEGRATION_SCOPE_REQUIRED')
    require(planned_review(final_review, plan, plan_raw, proposal_raw, plan['integration']) == context,
            'DEPLOYMENT_FROZEN_REVIEW_CONTEXT_CHANGED')
    require(final_review['response']['session_id'] not in
            {review['response']['session_id'] for review in reviews.values()},
            'DEPLOYMENT_DISTINCT_FINAL_REVIEW_REQUIRED')
    private = final_review['private_text']
    require(private.get(digest(manifest_raw)) == manifest_raw
            and all(private.get(digest(raw['response.json'])) == raw['response.json']
                    for raw in originals.values()),
            'DEPLOYMENT_COMPLETE_COMPONENT_FINDINGS_NOT_REVIEWED')
    # Stable proof travels unchanged through pre-install intent and final receipt.
    return {'review_plan_sha256': digest(plan_raw), 'component_receipts_sha256': digest(manifest_raw),
            'component_original_sha256': {part: row['original_sha256'] for part, row in manifest['parts'].items()}}


def _inspection_inventory(directory):
    """Read one bounded protected export, excluding only its own exact index."""
    from orchestrator.inspection_access import relative_name
    from orchestrator.review_input_codec import parsed
    from orchestrator.inspection_review import MAX_EXPORT_FILES
    directory = Path(directory)
    protected(directory, directory=True)
    index_raw = read(directory/'index.json', maximum=16000000)
    index = parsed(index_raw)
    require(isinstance(index, dict) and set(index) == {'schema', 'files'}
            and index['schema'] == 'inspection-deployment-file-index/v1'
            and isinstance(index['files'], dict) and 0 < len(index['files']) <= MAX_EXPORT_FILES,
            'DEPLOYMENT_INSPECTION_INDEX_REQUIRED')
    for name, row in index['files'].items():
        relative_name(name)
        require(name != 'index.json' and isinstance(row, dict) and set(row) == {'sha256', 'bytes'}
                and type(row['bytes']) is int and 0 <= row['bytes'] <= 16000000,
                'DEPLOYMENT_INSPECTION_INDEX_ENTRY')
        pin(row['sha256'])
    require(sum(row['bytes'] for row in index['files'].values()) <= 150000000,
            'DEPLOYMENT_INSPECTION_EXPORT_TOO_LARGE')
    observed = set()
    for root, directories, names in os.walk(directory, followlinks=False):
        for name in directories:
            protected(Path(root)/name, directory=True)
        for name in names:
            path = Path(root)/name
            relative = path.relative_to(directory).as_posix()
            protected(path)
            if relative != 'index.json':
                observed.add(relative)
            require(len(observed) <= MAX_EXPORT_FILES, 'DEPLOYMENT_INSPECTION_EXPORT_TOO_LARGE')
    require(observed == set(index['files']), 'DEPLOYMENT_INSPECTION_EXACT_TREE_REQUIRED')
    raw = {}
    for name, row in index['files'].items():
        value = read(directory/name, maximum=16000000)
        require(len(value) == row['bytes'] and digest(value) == row['sha256'],
                'DEPLOYMENT_INSPECTION_FILE_CHANGED')
        value.decode('utf-8')
        require(b'\0' not in value, 'DEPLOYMENT_INSPECTION_TEXT_ORIGINAL_REQUIRED')
        raw[name] = value
    return index_raw, raw


def _inspection_bootstrap(raw, files, *, prospective=False):
    """Qualify the enabling mechanism through original legacy review first."""
    from orchestrator import inspection_bootstrap as bootstrap
    from orchestrator.inspection_access import access_settings
    from orchestrator.review_input_codec import parsed
    runtime = parsed(raw['runtime.json'])
    source = pin(runtime['bootstrap_source'], 40)
    originals = {name: raw['bootstrap/'+name] for name in ORIGINAL_NAMES}
    if prospective:
        bootstrap.require_v2_review(originals)
    baseline = {name[len('bootstrap/policy-baseline/'):]: value for name, value in raw.items()
                if name.startswith('bootstrap/policy-baseline/')}
    old = _review_originals(originals, source, {bootstrap.SCOPE}, policy_baseline=baseline or None)
    complete = {name: text.encode() for name, text in old['source_text'].items()}
    names = runtime.get('enabling_files')
    if isinstance(names, dict):
        require(names == {name: digest(value) for name, value in complete.items()},
                'DEPLOYMENT_INSPECTION_COMPLETE_BOOTSTRAP_MAP_REQUIRED')
    else:
        require(isinstance(names, list) and len(names) == len(set(names)) and set(names) == set(complete),
                'DEPLOYMENT_INSPECTION_COMPLETE_BOOTSTRAP_MAP_REQUIRED')
    approved = bootstrap.validate_bootstrap(originals, source, complete, policy_baseline=baseline or None)
    if old['request'].get('input_presentation') == bootstrap.codec.FORMAT_V2:
        bootstrap.validate_context(raw['context-original.json'], approved['source_text'])
    operating = parsed(files['configs/scientific-operating-context.json'])
    authority = operating['authority_policy']['path']
    policy = parsed(files[authority])
    mandatory = set(bootstrap.MANDATORY_SOURCE) | set(operating['documents']) | {authority, policy['direction_path']}
    if old['request'].get('input_presentation') == bootstrap.codec.FORMAT_V2:
        mandatory.update(bootstrap.MANDATORY_SOURCE_V2)
    require(all(name in files and complete.get(name) == files[name] for name in mandatory),
            'DEPLOYMENT_INSPECTION_UNREVIEWED_ENABLER_OR_POLICY')
    bootstrap._policy_sources(files)
    execution = runtime['execution']
    require(execution['settings_sha256'] == digest(encoded(access_settings()))
            and execution['files']['hooks']['sha256'] == digest(complete['orchestrator/inspection_access.py'])
            and execution['files']['runner']['sha256'] == digest(complete['orchestrator/inspection_runner.py']),
            'DEPLOYMENT_INSPECTION_RUNTIME_SOURCE_CHANGED')
    launch_raw, plan_raw, permit_raw = (raw[name] for name in
        ('canary/canary-plan.json', 'canary/plan.json', 'administrative-permit.json'))
    launch, plan = parsed(launch_raw), parsed(plan_raw)
    require(launch['schema'] == 'inspection-canary-launch-plan/v1'
            and launch['bootstrap_source'] == launch['source'] == plan['source'] == source
            and launch['enabling_files'] == {name: digest(value) for name, value in complete.items()}
            and launch['expected_plan_sha256'] == digest(plan_raw)
            and launch['permit_sha256'] == digest(permit_raw)
            and plan['execution'] == execution
            and raw['canary/administrative-permit.json'] == permit_raw
            and all(approved['private_text'].get(digest(value)) == value
                    for value in (launch_raw, plan_raw, permit_raw)),
            'DEPLOYMENT_INSPECTION_CANARY_NOT_BOOTSTRAPPED')
    return runtime


def _inspection_attempt(raw, number, permission_raw):
    """Rebuild an adapter from exact exported files, never from saved verdicts."""
    from orchestrator.review_input_codec import parsed
    prefix = 'attempts/'+f'{number:03d}'+'/'
    values = {name: raw[prefix+name+('.jsonl' if name == 'protocol' else '.json')]
              for name in ('request', 'intent', 'process', 'returned', 'protocol',
                           'admission_event', 'admission_receipt', 'admission_policy')}
    values.update(permission_probe=permission_raw,
                  timeout=raw.get(prefix+'timeout.json'), reconciliation=raw.get(prefix+'reconciliation.json'))
    journal, used = [], set()
    for name in sorted(raw):
        if not name.startswith(prefix+'journal/') or not name.endswith('.observation.json'):
            continue
        row = parsed(raw[name]); key, phase = row['tool_use_id'], row['phase']
        require(isinstance(key, str) and re.fullmatch('[A-Za-z0-9_-]{1,128}', key)
                and phase in ('PreToolUse', 'PostToolUse', 'PostToolUseFailure'), 'DEPLOYMENT_INSPECTION_JOURNAL_IDENTITY')
        stem = key+{'PreToolUse': '.pre', 'PostToolUse': '.post', 'PostToolUseFailure': '.failure'}[phase]
        inp = prefix+'journal/'+stem+'.input.json'
        require(name == prefix+'journal/'+stem+'.observation.json'
                and row['raw_input_file'] == stem+'.input.json', 'DEPLOYMENT_INSPECTION_JOURNAL_PATH')
        journal.append((key, phase, encoded({'observation_original': raw[name].decode(),
                                           'hook_input_original': raw[inp].decode()})))
        used.update({name, inp})
    require(used == {name for name in raw if name.startswith(prefix+'journal/')},
            'DEPLOYMENT_INSPECTION_ORPHAN_JOURNAL')
    values['journal'] = [value for _, _, value in sorted(journal, key=lambda row:
                         (row[0], 0 if row[1] == 'PreToolUse' else 1))]
    return {'originals': values, 'response_raw': raw[prefix+'response.json'],
            'execution_raw': raw[prefix+'execution.json']}


def inspection_review(bundle, proposal_raw, files, originals, *, prospective=False):
    """Explicit direct profile: independent bootstrap, canary, then full Read proof."""
    from orchestrator import inspection_review as inspection, inspection_deployment as adapter
    from orchestrator import inspection_runner as runner, inspection_canary as canary, inspection_runtime as runtime_guard
    from orchestrator.review_input_codec import parsed
    directory = Path(bundle)/'inspection'
    index_raw, raw = _inspection_inventory(directory)
    fixed = {'manifest.json', 'context-original.json', 'change-context.json', 'change-bindings.json',
             'runtime.json', 'administrative-permit.json', 'permission-probe.json'}
    fixed.update('bootstrap/'+name for name in ORIGINAL_NAMES)
    attempt_names = set(ORIGINAL_NAMES) | {'process.json', 'admission_event.json', 'admission_receipt.json',
                      'admission_policy.json', 'timeout.json', 'reconciliation.json', 'command.json',
                      'control-readback.json', 'receipt.json', 'stderr.log', 'service-origin.json',
                      'reconciliation-observation.json', 'service-start-intent.json',
                      'service-start.stdout.txt', 'service-start.stderr.txt', 'service-start-returned.json',
                      'confinement-readback.json'}
    canary_names = {'plan.json', 'canary-plan.json', 'administrative-permit.json', 'permission-probe.json'}
    phase_names = {'request.json', 'command.json', 'settings.json', 'execution.json', 'intent.json',
                   'process.json', 'protocol.jsonl', 'admission_event.json', 'admission_receipt.json',
                   'admission_policy.json', 'returned.json', 'CANARY.after.txt', 'probe.before.txt',
                   'control-readback.json', 'runtime-readback.json', 'invocation.json', 'confinement-readback.json'}
    for name in raw:
        parts = name.split('/')
        journal = bool(re.fullmatch('[A-Za-z0-9_-]{1,128}\\.(pre|post|failure)\\.(input|observation)\\.json', parts[-1]))
        allowed = name in fixed or name.startswith('view/') or (name.startswith('canary/') and name[7:] in canary_names)
        # The complete baseline subtree is separately checked against its exact
        # manifest, native change chain and independent original review below.
        allowed |= name.startswith('bootstrap/policy-baseline/')
        allowed |= (len(parts) in (3, 4) and parts[0] == 'attempts' and bool(re.fullmatch('[0-9]{3}', parts[1]))
                    and ((len(parts) == 3 and parts[2] in attempt_names) or (len(parts) == 4 and parts[2] == 'journal' and journal)))
        allowed |= (len(parts) in (3, 4) and parts[0] == 'canary' and parts[1] in ('baseline', 'hooks')
                    and ((len(parts) == 3 and parts[2] in phase_names) or (len(parts) == 4 and parts[2] == 'journal' and journal)))
        require(allowed, 'DEPLOYMENT_INSPECTION_UNEXPECTED_EXPORT_FILE')
    require(fixed <= set(raw), 'DEPLOYMENT_INSPECTION_FIXED_ORIGINAL_MISSING')
    runtime = _inspection_bootstrap(raw, files, prospective=prospective)
    manifest = inspection.validate_manifest(raw['manifest.json'])
    execution = runtime['execution']
    require(manifest['pins'] == {'runtime_sha256': digest(encoded(execution)),
            'settings_sha256': execution['settings_sha256'], 'hooks_sha256': execution['files']['hooks']['sha256'],
            'runner_sha256': execution['files']['runner']['sha256']}
            and manifest['current_request_sha256'] == parsed(raw['administrative-permit.json'])['operator_original_sha256'],
            'DEPLOYMENT_INSPECTION_RUNTIME_OR_OPERATOR_CHANGED')
    expected, canary_originals = runner.read_canary_proof(directory/'canary')
    probe = canary.verify_canary(canary_originals, expected)
    require(encoded(probe) == raw['permission-probe.json'] == raw['canary/permission-probe.json'],
            'DEPLOYMENT_INSPECTION_NATIVE_CANARY_CHANGED')
    numbers = sorted({int(name.split('/')[1]) for name in raw if name.startswith('attempts/')})
    require(numbers == list(range(1, len(numbers)+1)) and 0 < len(numbers) <= manifest['max_attempts'],
            'DEPLOYMENT_INSPECTION_ATTEMPT_SEQUENCE')
    attempts = [_inspection_attempt(raw, number, raw['permission-probe.json']) for number in numbers]
    for number in numbers:
        runtime_guard.verify_confinement_readback(raw['attempts/' + f'{number:03d}' + '/confinement-readback.json'],
            execution, source=manifest['source'], session_id=manifest['session_id'], attempt=number)
    last = 'attempts/'+f'{numbers[-1]:03d}'+'/'
    require(all(originals[name] == raw[last+name] for name in ORIGINAL_NAMES),
            'DEPLOYMENT_INSPECTION_BUNDLE_LAST_ORIGINALS_CHANGED')
    view = {name[5:]: value for name, value in raw.items() if name.startswith('view/')}
    required = {name: view[name] for name in manifest['required_ranges']}
    require(digest(raw['change-bindings.json']) == manifest['change_bindings_sha256'],
            'DEPLOYMENT_INSPECTION_CHANGE_BINDINGS_CHANGED')
    result = adapter.validate_deployment_session(raw['manifest.json'], attempts, view, required,
        parsed(proposal_raw)['source'], 'material-deployment', proposal_raw,
        raw['change-context.json'], raw['context-original.json'],
        # _inspection_bootstrap has already proved this candidate policy closure
        # byte-identical to the independently approved bootstrap originals.
        approved_policy_sources=files if parsed(raw['bootstrap/request.json']).get(
            'input_presentation') == 'raw-text-review-envelope/v2' else None)
    # Re-read after the runner's fixed canary loader; bind every exported wrapper
    # original as well as the recursive core attempt receipts.
    final_index, final_raw = _inspection_inventory(directory)
    require(final_index == index_raw and final_raw == raw, 'DEPLOYMENT_INSPECTION_EXPORT_CHANGED_DURING_VERIFY')
    return result, {'review_profile': adapter.PROFILE, 'inspection_index_sha256': digest(index_raw),
                    'inspection_manifest_sha256': digest(raw['manifest.json']),
                    'inspection_original_wrapper_index_sha256': result['full_original_wrapper_index_sha256']}


def proposal_shape(proposal, source_root, source):
    """Shared preparation/deployment shape; provenance grants no execution authority."""
    require(isinstance(proposal, dict) and set(proposal) == {
        'schema', 'profile', 'source', 'source_root', 'previous_source', 'previous_source_root',
        'archive_sha256', 'source_files', 'targets', 'previous_files', 'recovery_sha256',
        'changes', 'dependencies'}
        | ({'review_plan_sha256'} if 'review_plan_sha256' in proposal else set())
        | ({'review_profile'} if 'review_profile' in proposal else set())
        | ({'linked_recovery'} if 'linked_recovery' in proposal else set())
        and proposal['schema'] == SCHEMA and proposal['profile'] == PROFILE
        and proposal['source'] == source and proposal['source_root'] == str(Path(source_root)),
        'DEPLOYMENT_PROPOSAL_SCHEMA')
    require('review_profile' not in proposal or (proposal['review_profile'] in
            ('direct-inspection/v1', 'operator-terminal-review/v1', 'server-terminal-review/v1')
            and 'review_plan_sha256' not in proposal), 'DEPLOYMENT_EXPLICIT_REVIEW_PROFILE_REQUIRED')
    if 'linked_recovery' in proposal:
        link = proposal['linked_recovery']
        require(proposal.get('review_profile') == 'server-terminal-review/v1'
            and isinstance(link, dict) and set(link) == {
                'schema', 'authorized_event', 'decision_sha256', 'operator_original_sha256',
                'maximum_successors', 'automatic_retry', 'predecessor_proposal_sha256',
                'predecessor_session', 'predecessor_report_sha256',
                'predecessor_manifest_sha256', 'runtime_source'}
            and link['schema'] == 'operator-authorized-single-successor-review/v1'
            and type(link['maximum_successors']) is int and link['maximum_successors'] == 1
            and link['automatic_retry'] is False,
            'DEPLOYMENT_LINKED_REVIEW_SCOPE_REQUIRED')
        for key in ('authorized_event', 'decision_sha256', 'operator_original_sha256',
                    'predecessor_proposal_sha256', 'predecessor_report_sha256',
                    'predecessor_manifest_sha256'):
            pin(link[key])
        pin(link['runtime_source'], 40)
        require(isinstance(link['predecessor_session'], str) and re.fullmatch(
            r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', link['predecessor_session']),
            'DEPLOYMENT_LINKED_REVIEW_SESSION_REQUIRED')


def linked_review_provenance(proposal, private):
    """Check review-bound originals, not a retry grant or predecessor approval substitute.

    Current genuine review, selected applications, accounting, deployment and
    activation predicates are still mandatory. The root-supplied human decision
    keeps the same trust boundary as the existing recorded operator pathway.
    """
    if 'linked_recovery' not in proposal:
        return
    from orchestrator import change_requests as changes, terminal_review
    link = proposal['linked_recovery']
    def original(identity):
        raw = private.get(pin(identity))
        require(isinstance(raw, bytes) and digest(raw) == identity,
                'DEPLOYMENT_LINKED_REVIEW_ORIGINAL_REQUIRED')
        return raw
    previous_raw = original(link['predecessor_proposal_sha256'])
    require(json.loads(previous_raw) == {k: v for k, v in proposal.items() if k != 'linked_recovery'},
            'DEPLOYMENT_LINKED_REVIEW_UNCHANGED_SCOPE_REQUIRED')
    statement = terminal_review._statement(original(link['predecessor_report_sha256']),
        profile='server-terminal-review/v1', approval_required=False)
    require(all(statement[key] == expected for key, expected in {
        'source': proposal['source'], 'proposal_sha256': link['predecessor_proposal_sha256'],
        'manifest_sha256': link['predecessor_manifest_sha256'],
        'session_id': link['predecessor_session']}.items()),
        'DEPLOYMENT_LINKED_REVIEW_PREDECESSOR_CHANGED')
    original(link['operator_original_sha256']); original(link['decision_sha256'])
    events = []
    for raw in private.values():
        try: event = json.loads(raw)
        except (ValueError, UnicodeError): continue
        if isinstance(event, dict) and event.get('identity') == link['authorized_event']:
            events.append(event)
    require(len(events) == 1, 'DEPLOYMENT_LINKED_REVIEW_AUTHORIZATION_REQUIRED')
    event = events[0]
    require(event.get('schema') == changes.EVENT_SCHEMA and event.get('event') == 'AUTHORIZED'
        and event.get('actor', {}).get('kind') == 'human'
        and digest(changes.encoded({k: v for k, v in event.items() if k != 'identity'})) == event['identity'],
        'DEPLOYMENT_LINKED_REVIEW_AUTHORIZATION_CHANGED')
    changes.actor(event['actor'])
    authority = event.get('payload', {}).get('authority_reference', {})
    require(isinstance(authority, dict) and set(authority) == {'operator_original', 'exact_decision'}
        and authority['operator_original'].get('sha256') == link['operator_original_sha256']
        and authority['exact_decision'].get('sha256') == link['decision_sha256'],
        'DEPLOYMENT_LINKED_REVIEW_ACTUAL_DECISION_REQUIRED')
    for ref in authority.values():
        require(ref.get('size') == len(original(ref['sha256'])),
                'DEPLOYMENT_LINKED_REVIEW_DECISION_CHANGED')
    # The one-use authorization is an original first event in its own saved
    # request, not an arbitrary later event detached from an omitted history.
    request_raw = original(event['previous_sha256'])
    require(event.get('sequence') == 1, 'DEPLOYMENT_LINKED_REVIEW_AUTHORIZATION_CHAIN_REQUIRED')
    evidence = {ref['artifact']: original(ref['sha256']) for ref in authority.values()}
    changes.validate_originals(request_raw,
        {'0001-'+event['identity']+'.json': changes.encoded(event)+b'\n'}, evidence.__getitem__)


def verify_bundle(bundle, source_root, source, *, installed=False, check_current=True, prospective=False):
    """Read-only: verify review before installation, then exact installed bytes when requested."""
    from orchestrator.remote_supervisor import checked_source
    require(type(prospective) is bool and not (prospective and installed),
            'DEPLOYMENT_PROSPECTIVE_MODE_REQUIRED')
    bundle = Path(bundle); bundle_access = protected(bundle, directory=True); pin(source, 40)
    require(not bundle_access.st_mode & 0o007, 'DEPLOYMENT_PRIVATE_BUNDLE_REQUIRED')
    proposal_raw = read(bundle/'proposal.json'); proposal = json.loads(proposal_raw)
    proposal_shape(proposal, source_root, source)
    require(REQUIRED_TARGETS <= set(proposal['targets']), 'DEPLOYMENT_CONTINUING_COMPONENT_MISSING')
    require(type(check_current) is bool, 'DEPLOYMENT_CURRENT_CHECK_MODE_REQUIRED')
    if check_current and not installed:
        require(all(name in proposal['previous_files'] or (not Path(name).exists() and not Path(name).is_symlink())
                    for name in proposal['targets']), 'DEPLOYMENT_EXISTING_TARGET_NOT_RECONCILED')
    pin(proposal['previous_source'], 40)
    checked_source(proposal['previous_source_root'], proposal['previous_source'])
    archive = read(bundle/'source.tar.gz', maximum=10000000)
    require(digest(archive) == pin(proposal['archive_sha256']), 'DEPLOYMENT_ARCHIVE_CHANGED')
    files = archive_inventory(archive)
    require({name: digest(raw) for name, raw in files.items()} == proposal['source_files'],
            'DEPLOYMENT_SOURCE_INVENTORY_CHANGED')
    inspection_proof = {}
    terminal = proposal.get('review_profile') in ('operator-terminal-review/v1', 'server-terminal-review/v1')
    if terminal:
        from orchestrator import terminal_review
        review, inspection_proof = terminal_review.load(bundle, proposal_raw, files)
        inspection_proof['terminal_profile'] = review['terminal_profile']
    elif proposal.get('review_profile') == 'direct-inspection/v1':
        originals = {name: read(bundle/name, maximum=16000000) for name in ORIGINAL_NAMES}
        review, inspection_proof = inspection_review(bundle, proposal_raw, files, originals, prospective=prospective)
    else:
        originals = {name: read(bundle/name) for name in ('request.json', 'response.json', 'execution.json',
                                                        'protocol.jsonl', 'intent.json', 'returned.json')}
        from orchestrator.inspection_bootstrap import read_policy_baseline, require_v2_review
        if prospective:
            require_v2_review(originals)
        baseline = (read_policy_baseline(bundle/'policy-baseline') if json.loads(originals['request.json']).get(
            'input_presentation') == 'raw-text-review-envelope/v2' else None)
        review = review_originals(originals, source, policy_baseline=baseline)
    private = review['private_text']
    linked_review_provenance(proposal, private)
    require(private.get(digest(proposal_raw)) == proposal_raw, 'DEPLOYMENT_PROPOSAL_NOT_ACTUALLY_REVIEWED')
    selected = selected_review_applications(review, proposal_raw, source)
    required = {name for name in files if Path(name).suffix in CODE_SUFFIXES}
    operating_name = 'configs/scientific-operating-context.json'
    require(operating_name in files, 'DEPLOYMENT_OPERATING_MANIFEST_REQUIRED')
    operating = json.loads(files[operating_name]); authority = operating['authority_policy']
    require(authority['path'] in files and digest(files[authority['path']]) == authority['sha256'],
            'DEPLOYMENT_AUTHORITY_MANIFEST_CHANGED')
    policy = json.loads(files[authority['path']])
    policy_names = {**operating['documents'], policy['direction_path']: policy['direction_sha256']}
    require(all(name in files and digest(files[name]) == value for name, value in policy_names.items()),
            'DEPLOYMENT_ROLE_DOCUMENT_CHANGED')
    required.update(policy_names); required.update({operating_name, authority['path'], 'scripts/pilot_review.py'})
    required.update(replacement_review_files(files))
    if terminal:
        required.update({'orchestrator/terminal_review.py', 'orchestrator/deployment_review.py',
                         'orchestrator/prepare_deployment_bundle.py',
                         'orchestrator/install_reviewed_deployment.py',
                         'orchestrator/inspection_admission_recovery.py'})
    require(required <= set(files), 'DEPLOYMENT_REQUIRED_SOURCE_MISSING')
    if proposal.get('review_profile') == 'server-terminal-review/v1':
        require({'orchestrator/server_terminal_review.py', 'orchestrator/server_review_runner.py'} <= set(files),
                'DEPLOYMENT_SERVER_REVIEW_SOURCE_MISSING')
    composition = inspection_proof
    if 'review_plan_sha256' in proposal:
        composition = composed_review(bundle, proposal, proposal_raw, files, review)
    elif not terminal:
        for name in required:
            require((name in review['source_text'] and review['source_text'][name].encode() == files[name])
                    or private.get(digest(files[name])) == files[name], 'DEPLOYMENT_SOURCE_NOT_ACTUALLY_REVIEWED')
    for field in ('targets', 'previous_files'):
        require(isinstance(proposal[field], dict) and proposal[field], 'DEPLOYMENT_CONFIGURATION_INVENTORY_REQUIRED')
        for name, metadata in proposal[field].items():
            path = Path(name)
            require(path.is_absolute() and '..' not in path.parts and not path.is_relative_to(BASE),
                    'DEPLOYMENT_TARGET_PATH_REFUSED')
            require(set(metadata) == {'sha256', 'uid', 'gid', 'mode'} and metadata['uid'] == 0
                    and all(type(metadata[key]) is int and metadata[key] >= 0 for key in ('uid', 'gid', 'mode'))
                    and metadata['mode'] <= 0o777 and not metadata['mode'] & 0o022,
                    'DEPLOYMENT_TARGET_ACCESS_REQUIRED')
            raw = read(bundle/'literals'/pin(metadata['sha256']))
            require(digest(raw) == metadata['sha256'] and private.get(metadata['sha256']) == raw,
                    'DEPLOYMENT_CONFIGURATION_NOT_ACTUALLY_REVIEWED')
            if check_current and ((installed and field == 'targets') or (not installed and field == 'previous_files')):
                require(read(path) == raw, 'DEPLOYMENT_INSTALLED_CONFIGURATION_CHANGED')
                require(access(path) == (metadata['uid'], metadata['gid'], metadata['mode']), 'DEPLOYMENT_INSTALLED_ACCESS_CHANGED')
    require(isinstance(proposal['dependencies'], dict) and set(proposal['dependencies']) == set(DEPENDENCY_PATHS),
            'DEPLOYMENT_FIXED_LAUNCHERS_REQUIRED')
    for name, expected in proposal['dependencies'].items():
        require(dependency_metadata(name) == expected, 'DEPLOYMENT_LAUNCHER_IDENTITY_CHANGED')
    recovery = read(bundle/'literals'/pin(proposal['recovery_sha256']))
    if terminal:
        from orchestrator.install_reviewed_deployment import validate_recovery
        from orchestrator import recovery_inventory
        resolved, pages = recovery_inventory.resolve(json.loads(recovery),
            lambda sha: read(bundle/'literals'/sha, maximum=recovery_inventory.MAX_PAGE_BYTES))
        require(all(private.get(sha) == raw for sha, raw in pages.items()),
                'DEPLOYMENT_RECOVERY_PAGE_NOT_REVIEWED')
        validate_recovery(resolved, proposal)
    require(private.get(proposal['recovery_sha256']) == recovery, 'DEPLOYMENT_RECOVERY_PLAN_NOT_REVIEWED')
    require(isinstance(proposal['changes'], list) and proposal['changes'], 'DEPLOYMENT_RECORDED_CHANGES_REQUIRED')
    heads = {}
    for change in proposal['changes']:
        require(set(change) == {'request', 'applied'} and change['request'] not in heads,
                'DEPLOYMENT_EXACT_CHANGE_BINDING_REQUIRED')
        pin(change['applied']); heads[change['request']] = change_review(bundle, change, review, selected=selected)
    if check_current and installed:
        checked_source(source_root, source)
        root = Path(source_root)
        observed = {}
        for path in root.rglob('*'):
            name = path.relative_to(root)
            if '.git' in name.parts:
                continue
            if path.is_dir():
                protected(path, directory=True)
            else:
                observed[name.as_posix()] = digest(read(path))
        require(observed == proposal['source_files'], 'DEPLOYMENT_INSTALLED_SOURCE_INVENTORY_CHANGED')
    return {'schema': SCHEMA, 'profile': PROFILE, 'source': source, 'proposal_sha256': digest(proposal_raw),
            'archive_sha256': proposal['archive_sha256'],
            'review_execution_sha256': (inspection_proof['terminal_review_manifest_sha256']
                                        if terminal else digest(originals['execution.json'])),
            'review_response_sha256': (inspection_proof['terminal_review_report_sha256']
                                       if terminal else digest(originals['response.json'])), 'review_session': review['response']['session_id'],
            'review_model': _review_model(review), 'change_heads': heads, 'previous_source': proposal['previous_source'],
            'target_sha256': {name: value['sha256'] for name, value in proposal['targets'].items()},
            'source_files': proposal['source_files'], 'dependencies': proposal['dependencies'],
            'unattended_activation_authority': False, 'current_state_checked': check_current, **composition}


def _save_once(bundle, name, value):
    raw = encoded(value); path = Path(bundle)/name
    if path.exists():
        require(read(path) == raw, 'DEPLOYMENT_ORIGINAL_RECEIPT_CHANGED')
    else:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o640)
        with os.fdopen(fd, 'wb') as stream:
            os.fchmod(stream.fileno(), 0o640); os.fchown(stream.fileno(), 0, Path(bundle).stat().st_gid)
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        fd = os.open(bundle, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try: os.fsync(fd)
        finally: os.close(fd)
    return value


def _preinstall_review(bundle, source_root, source):
    """Authenticate source and accounting before the installer's state inventory."""
    require(os.getuid() == 0, 'DEPLOYMENT_ADMIN_REQUIRED')
    result = verify_bundle(bundle, source_root, source, installed=False, prospective=True)
    from orchestrator.install_reviewed_deployment import require_terminal_accounting
    accounting = require_terminal_accounting(bundle, result)
    return result, accounting


def begin_install(bundle, source_root, source):
    """Save actual pre-mutation source/config/review verification; start no service."""
    result, _ = _preinstall_review(bundle, source_root, source)
    return _save_once(bundle, 'install-intent.json', {'status': 'PREPARED_REVIEW_VERIFIED', **result})


def record_install(bundle, source_root, source):
    """Root installer records actual readback; incomplete original attempts stay intact."""
    require(os.getuid() == 0, 'DEPLOYMENT_ADMIN_REQUIRED')
    result = verify_bundle(bundle, source_root, source, installed=True)
    intent_raw = read(Path(bundle)/'install-intent.json')
    require(json.loads(intent_raw) == {'status': 'PREPARED_REVIEW_VERIFIED', **result},
            'DEPLOYMENT_ORIGINAL_PREINSTALL_CHECK_REQUIRED')
    return _save_once(bundle, 'install-receipt.json',
                      {'status': 'INSTALLED_REVIEW_VERIFIED', 'intent_sha256': digest(intent_raw), **result})


def verify_installed(source_root, source, *, config_path=None, config=None):
    """Fixed protected selection; callers cannot supply a review path or verdict."""
    require(os.getuid() == 0, 'DEPLOYMENT_PROTECTED_BROKER_VERIFIER_REQUIRED')
    active = json.loads(read(ACTIVE, maximum=10000))
    require(set(active) == {'schema', 'source', 'proposal_sha256', 'install_receipt_sha256'}
            and active['schema'] == SCHEMA and active['source'] == source,
            'DEPLOYMENT_ACTIVE_SELECTION_REQUIRED')
    bundle = BASE/'bundles'/pin(active['proposal_sha256'])
    result = verify_bundle(bundle, source_root, source, installed=True)
    receipt_raw = read(bundle/'install-receipt.json'); receipt = json.loads(receipt_raw)
    intent_raw = read(bundle/'install-intent.json')
    require(json.loads(intent_raw) == {'status': 'PREPARED_REVIEW_VERIFIED', **result},
            'DEPLOYMENT_ORIGINAL_PREINSTALL_CHECK_REQUIRED')
    require(result['proposal_sha256'] == active['proposal_sha256']
            and digest(receipt_raw) == pin(active['install_receipt_sha256'])
            and receipt == {'status': 'INSTALLED_REVIEW_VERIFIED', 'intent_sha256': digest(intent_raw), **result},
            'DEPLOYMENT_COMPLETED_INSTALL_RECEIPT_REQUIRED')
    if config_path is not None:
        name = str(Path(config_path))
        require(name in result['target_sha256'] and digest(read(name)) == result['target_sha256'][name],
                'DEPLOYMENT_CALLER_CONFIGURATION_NOT_REVIEWED')
        if config is not None:
            require(json.loads(read(name)) == config, 'DEPLOYMENT_IN_MEMORY_CONFIGURATION_CHANGED')
    elif config is not None:
        raise ValueError('DEPLOYMENT_CALLER_CONFIGURATION_PATH_REQUIRED')
    return {**result, 'running_broker': running_broker(source_root)}
