"""Terminal-review profile of the existing protected inspection lifecycle.

Shared prepare/start/status/continue/reconcile operations, never a daemon that
resubmits rejected work. A systemd-owned invocation saves its original judgment;
only a qualified APPROVE may later enter the existing deployment importer.
"""
from contextlib import nullcontext
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import uuid

from orchestrator import inspection_runner as runner, inspection_access as access
from orchestrator import inspection_runtime as runtime, inspection_source as source_view
from orchestrator import server_terminal_review as evidence, terminal_review as terminal
from orchestrator import deployment_review as gate, change_requests as changes
from orchestrator import server_review_install as administrative

CONFIG = Path('/etc/research-system/server-reviews.json')
STATE_SCHEMA = 'server-terminal-state/v1'
# Source-reviewed terminal implementation reviews only. Scientific and legacy
# inspection limits remain unchanged. The supervisor allows cleanup/recovery.
TERMINAL_TIMEOUT_SECONDS = 1200
TERMINAL_SERVICE_SECONDS = TERMINAL_TIMEOUT_SECONDS + 100
read, save, sha = runner.read, runner.save, runner.sha
write_once = source_view.write_once
require = evidence.require


def now():
    return datetime.now(timezone.utc).isoformat()


def configured(*, check_control=True):
    """Root-held, independently approved installation, including its exact permit.

    The amendment is not the enabling source approval. Running an uninstalled
    checkout, replacing configuration, or inventing approval cannot satisfy the
    separately reviewed administrative receipt. Scientific release is unchanged.
    """
    require(os.getuid() == 0, 'PROTECTED_OPERATOR_REQUIRED')
    raw = gate.read(CONFIG); value = json.loads(raw)
    require(set(value) == {'schema', 'source', 'runtime', 'permit', 'max_attempts', 'max_iterations'}
        and value['schema'] == 'server-terminal-configuration/v1', 'CONFIGURATION_REQUIRED')
    root = Path(__file__).resolve().parents[1]
    proof = administrative.verify(root, value['source'], value)
    require({'orchestrator/server_review_runner.py', 'orchestrator/server_terminal_review.py',
        'orchestrator/terminal_review.py', 'orchestrator/inspection_runtime.py',
        'orchestrator/inspection_access.py', 'orchestrator/terminal_statement.py',
        'orchestrator/review_input_codec.py'} <= set(proof['source_files']), 'ENABLER_REVIEW_COVERAGE_REQUIRED')
    require(value['runtime'].get('terminal_profile') == evidence.PROFILE
        and value['permit']['operator_original_sha256'] == evidence.OPERATOR_SHA,
        'REVIEWED_ADMINISTRATIVE_PROFILE_REQUIRED')
    if 'host_read' in value['runtime']:
        from orchestrator import implementation_host_read as host
        host.profile(value['runtime']['host_read'])
        require('orchestrator/implementation_host_read.py' in proof['source_files'],
                'HOST_READ_REVIEWED_SOURCE_REQUIRED')
    if check_control:
        require(runner.current_control(json.loads(read(runner.CONTROLLER_CONFIG))) ==
                value['permit']['control_snapshot'], 'NEW_STOP_OR_STALE_PERMIT')
    return value, proof


def _directory(identity):
    path = runner.session_path(identity)
    access.no_symlinks(path)
    return path


def _state(directory):
    raw = read(directory/'manifest.json'); state = json.loads(raw)
    require(state.get('schema') == STATE_SCHEMA and state['session_id'] == directory.name,
            'SAVED_TERMINAL_STATE_REQUIRED')
    plan = evidence.validate_plan(json.loads(read(directory/'terminal-inputs/server/plan.json')))
    require(plan['session_id'] == state['session_id'] and plan['source'] == state['source'],
            'SAVED_PLAN_CHANGED')
    return state, plan


def _current_plan(directory, config, state, plan):
    require(directory == _directory(plan['session_id']), 'FIXED_STATE_ROOT_REQUIRED')
    require(plan['enabling_source'] == config['source']
        and sha(read(directory/'runtime.json')) == plan['runtime_sha256'] == sha(runner.encoded(config['runtime']))
        and sha(read(directory/'administrative-permit.json')) == plan['permit_sha256'] == sha(runner.encoded(config['permit']))
        and sha(read(directory/'context-original.json')) == plan['context_sha256']
        and state['admission_binding'] == plan['admission_binding']
        and state['max_attempts'] == plan['max_attempts'] == config['max_attempts']
        and state['max_iterations'] == plan['max_iterations'] == config['max_iterations'],
        'SAVED_REVIEWED_LAUNCH_CONFIGURATION_CHANGED')


def candidate_preflight(spec):
    """A deployment carrier may omit Git blobs; reject it before saving a session.

    Check the complete tracked tree needed by inspection_source, independently
    of the smaller production archive. This makes no admission or state write.
    """
    root = Path(spec['candidate_root']); access.no_symlinks(root)
    proposal = json.loads(read(spec['proposal']))
    source = gate.pin(proposal['source'], 40)
    if proposal.get('schema') == gate.SCHEMA:
        gate.proposal_shape(proposal, proposal.get('source_root'), source)
    def git(*args, payload=None):
        return subprocess.run(['git', *args], cwd=root, input=payload,
            capture_output=True, check=True, timeout=60).stdout
    require(git('rev-parse', 'HEAD').decode().strip() == source
        and not git('status', '--porcelain'), 'CLEAN_COMPLETE_CANDIDATE_REQUIRED')
    rows = git('ls-tree', '-rz', '--full-tree', source).split(b'\0')
    objects = []
    for row in rows:
        if not row: continue
        metadata, name = row.split(b'\t', 1)
        mode, kind, identity = metadata.split()
        if kind == b'blob': objects.append(identity)
    require(objects, 'COMPLETE_SOURCE_OBJECTS_REQUIRED')
    answer = git('cat-file', '--batch-check', payload=b'\n'.join(objects)+b'\n').splitlines()
    require(len(answer) == len(objects) and all(
        len(row.split()) == 3 and row.split()[0] == identity
        and row.split()[1] == b'blob' and row.split()[2].isdigit()
        for row, identity in zip(answer, objects)), 'COMPLETE_SOURCE_OBJECTS_REQUIRED')
    return {'source': source, 'tracked_blobs': len(objects), 'models': 0}


def prepare(spec):
    config, installed = configured()
    require(isinstance(spec, dict) and set(spec) == {'candidate_root', 'manifest', 'proposal', 'inputs', 'actor',
        'question', 'request_key'}, 'PREPARATION_SPEC_REQUIRED')
    changes.actor(spec['actor'])
    require(spec['actor']['kind'] == 'agent' and spec['actor']['family'] == 'codex', 'AGENT_REQUIRED')
    require(isinstance(spec['request_key'], str) and re_key(spec['request_key']), 'REQUEST_KEY_REQUIRED')
    # One request key has one durable session, even across client disconnects.
    index = runner.ROOT/'server-terminal-requests'
    index.mkdir(mode=0o700, exist_ok=True)
    with (index/'.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        key = index/('request-'+spec['request_key']+'.json')
        fingerprint = sha(runner.encoded(spec))
        if key.exists():
            old = json.loads(read(key)); require(old['spec_sha256'] == fingerprint, 'REQUEST_KEY_SCOPE_CHANGED')
            return status(_directory(old['session_id']))
        # Exact same source/proposal cannot obtain a fresh paid session by changing a key/question.
        scope = sha(read(spec['proposal']))
        scope_key = index/('scope-'+scope+'.json')
        if scope_key.exists():
            return status(_directory(json.loads(read(scope_key))['session_id']))
        candidate_preflight(spec)
        runtime.preflight_inputs(config['runtime'])
        identity = str(uuid.uuid4()); directory = _directory(identity)
        directory.mkdir(mode=0o700); (directory/'attempts').mkdir(mode=0o700)
        save(key, {'session_id': identity, 'spec_sha256': fingerprint})
        save(scope_key, {'session_id': identity, 'proposal_sha256': scope})
        save(directory/'preparation-spec.json', spec)
        # A partial preparation is retained under the key and never remints a session.
        proposal_raw = read(spec['proposal']); proposal = json.loads(proposal_raw)
        manifest = json.loads(read(spec['manifest']))
        require(proposal['review_profile'] == manifest['schema'] == evidence.PROFILE
            and manifest['source'] == proposal['source']
            and manifest['proposal_sha256'] == sha(proposal_raw)
            and manifest['report_path'] == access.REPORT_PATH, 'TERMINAL_SCOPE_REQUIRED')
        raw = {name: read(Path(spec['inputs'])/access.relative_name(name)) for name in manifest['files']}
        require({n: sha(v) for n, v in raw.items()} == manifest['files'], 'INPUTS_CHANGED')
        terminal._authority(raw); evidence.authority(raw)
        require(sha(proposal_raw) in {sha(v) for v in raw.values()}, 'PROPOSAL_ORIGINAL_REQUIRED')
        for name in ('source', 'proposal_sha256'):
            require(manifest[name] == proposal[name] if name == 'source' else
                    manifest[name] == sha(proposal_raw), 'PROPOSAL_SCOPE_CHANGED')
        task = changes.submit(directory/'changes', Path(spec['candidate_root']),
            'implementation-review:'+proposal['source'], 'Independent fixed-scope source/integration review; original question preserved in preparation-spec.json.', spec['actor'],
            source=proposal['source'], key='server-review', risk='MATERIAL_SOURCE_REVIEW',
            scope_limits=['Independent source judgment only; no installation or scientific authority.',
                          'Same fixed source/configuration/proposal/applications; no equivalent rejection resubmission.'])
        save(directory/'saved-request.json', task)
        for name, digest in proposal['source_files'].items():
            actual = read(Path(spec['candidate_root'])/access.relative_name(name))
            require(sha(actual) == digest, 'CANDIDATE_SOURCE_CHANGED')
            write_once(directory/'source-files'/name, actual)
        inputs = directory/'terminal-inputs'
        for name, value in raw.items(): write_once(inputs/name, value)
        write_once(directory/'proposal.json', proposal_raw)
        from orchestrator.scientific_authority import stage_context
        stage_context(Path(__file__).resolve().parents[1], directory, 'claude', 'implementation_review')
        context = read(directory/'context_implementation_review.json')
        write_once(directory/'context-original.json', context)
        enabling_receipt = gate.read(installed['receipt_path'])
        for name, body in {'server/context.json': context,
                'server/runtime.json': runner.encoded(config['runtime']),
                'server/permit.json': runner.encoded(config['permit']),
                'server/enabling-install.json': enabling_receipt}.items():
            require(name not in raw, 'GENERATED_SERVER_INPUT_ALREADY_EXISTS')
            raw[name] = body; write_once(inputs/name, body)
            manifest['files'][name] = sha(body)
        # Existing scan/copy/catalog mechanism; excluded material earns no inspection credit.
        view = source_view.prepare(Path(spec['candidate_root']), proposal['source'], directory/'view',
            evidence=[{'path': str(inputs/n), 'sha256': sha(v), 'name': n} for n, v in raw.items()])
        view_files = {n: {'sha256': v['sha256'], 'bytes': v['bytes'], 'line_count': v['lines']}
                      for n, v in view['files'].items()}
        catalog = read(directory/'view/VIEW.json')
        view_files['VIEW.json'] = {'sha256': sha(catalog), 'bytes': len(catalog),
                                   'line_count': len(catalog.decode().splitlines())}
        access_raw = access.encoded({'schema': access.MANIFEST_SCHEMA, 'source': proposal['source'],
                                    'files': view_files})
        access_manifest = access.validate_access_manifest(access_raw)
        write_once(inputs/'server/view.json', access_raw)
        manifest['files']['server/view.json'] = sha(access_raw)
        rt = config['runtime']
        require(rt['execution']['settings_sha256'] == sha(access.encoded(access.terminal_settings(host_read='host_read' in rt))),
                'REVIEWED_TERMINAL_SETTINGS_REQUIRED')
        prepared = runtime.prepare_runtime(directory, rt, access_raw,
                        access.encoded(access.terminal_settings(host_read='host_read' in rt)), proposal['source'])
        broker = json.loads(read(runner.BROKER_CONFIG)); controller = json.loads(read(runner.CONTROLLER_CONFIG))
        plan = evidence.validate_plan({'schema': evidence.PLAN, 'source': proposal['source'],
            'proposal_sha256': sha(proposal_raw), 'session_id': identity, 'actor': spec['actor'],
            'max_attempts': config['max_attempts'], 'max_iterations': config['max_iterations'],
            'model': evidence.MODEL, 'cli_version': evidence.CLI_VERSION,
            'context_sha256': sha(context), 'permit_sha256': sha(runner.encoded(config['permit'])),
            'runtime_sha256': sha(runner.encoded(rt)), 'view_sha256': sha(access_raw),
            'enabling_source': config['source'], 'installed_review_receipt_sha256': installed['receipt_sha256'],
            'operator_original_sha256': evidence.OPERATOR_SHA,
            'admission_binding': {'source': controller['source'], 'branch': 'astra/infrastructure-milestone-record',
                'kind': 'astra_turn', 'turn_id': sha(runner.encoded({'session': identity, 'profile': evidence.PROFILE})),
                'policy_sha256': sha(runner.encoded(broker['policy']))}})
        plan_raw = runner.encoded(plan); write_once(inputs/'server/plan.json', plan_raw)
        manifest['files']['server/plan.json'] = sha(plan_raw)
        write_once(directory/'terminal-manifest.json', runner.encoded(manifest))
        save(directory/'runtime.json', rt); save(directory/'administrative-permit.json', config['permit'])
        state = {'schema': STATE_SCHEMA, 'source': proposal['source'], 'session_id': identity,
            'scope': 'material-deployment', 'model_policy_version': 'direct-inspection-opus-4-8/v1',
            'max_attempts': plan['max_attempts'], 'max_iterations': plan['max_iterations'],
            'current_request_sha256': evidence.OPERATOR_SHA, 'admission_binding': plan['admission_binding'],
            'access_manifest_original': access_raw.decode(), 'access_manifest_sha256': sha(access_raw),
            'pins': {'settings_sha256': prepared['settings_sha256'], 'hooks_sha256': prepared['hooks_sha256'],
                'runner_sha256': prepared['runner_sha256'], 'runtime_sha256': sha(runner.encoded(rt['execution']))}}
        save(directory/'manifest.json', state)
        prepare_attempt(directory, spec['question'])
        return status(directory)


def re_key(value):
    import re
    return re.fullmatch(r'[A-Za-z0-9_-]{1,80}', value)


def export_headroom(directory, completed):
    """Apply the unchanged export budget to export originals, not runtime copies.

    originals() is the exact exporter selection, including duplicated report/session
    aliases. Runtime executables remain preserved, but export() never emits them.
    The future-invocation reserve and final export checks remain unchanged.
    """
    if completed:
        manifest_raw, raw = originals(directory, completed)
    else:
        manifest_raw = read(directory/'terminal-manifest.json')
        manifest = json.loads(manifest_raw)
        raw = {name: read(directory/'terminal-inputs'/name) for name in manifest['files']}
    raw['manifest.json'] = manifest_raw
    sizes = [len(value) for value in raw.values()]
    require(len(raw) <= 7000 and all(size <= 16000000 for size in sizes), 'EXPORT_BOUND')
    retained = sum(sizes)
    require(retained+65000000 <= 150000000, 'EXPORT_HEADROOM_EXHAUSTED')
    return {'export_original_bytes': retained, 'reserved_bytes': 65000000,
            'limit_bytes': 150000000, 'export_files': len(raw)}


def prepare_attempt(directory, question):
    config, _ = configured(); state, plan = _state(directory)
    _current_plan(directory, config, state, plan)
    require(isinstance(question, str) and question.strip(), 'QUESTION_REQUIRED')
    with (directory/'execution.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        rows = sorted((directory/'attempts').iterdir()); number = len(rows)+1
        require(number <= plan['max_attempts'], 'ATTEMPTS_EXHAUSTED')
        previous = None; prior = ''
        if rows:
            recovered = recover(directory, number-1)
            require(recovered['verdict'] == 'IN_PROGRESS', 'FINAL_OR_UNCERTAIN_NO_CONTINUATION')
            previous = sha(read(rows[-1]/'outcome.json')); prior = read(rows[-1]/'report.md').decode()
        contract = {'schema': evidence.PROFILE, 'source': plan['source'],
            'proposal_sha256': plan['proposal_sha256'],
            'manifest_sha256': sha(read(directory/'terminal-manifest.json')),
            'session_id': plan['session_id'], 'scope': 'material-source-integration',
            'resolution_of': terminal.BASE_SOURCE,
            'verdict': 'CHOOSE INDEPENDENTLY: APPROVE, REQUEST_CHANGES, or IN_PROGRESS',
            'inspected': ['Name actual inspected files/connections and reused prior coverage explicitly.'],
            'unavailable': [], 'unverified': [],
            'findings': {name: {'disposition': 'Choose an applicable disposition; do not infer resolution.',
                               'reason': 'Your evidence-backed judgment.'} for name in sorted(terminal.FINDINGS)},
            'remaining_gates': ['held-deployment', 'accounting-halt', 'retained-history-audit',
                                'conditional-activation', 'scientific-acceptance']}
        prompt = ('BEGIN_SHARED_OPERATING_CONTEXT\n'+read(directory/'context-original.json').decode()+
            '\nEND_SHARED_OPERATING_CONTEXT\nIndependent fixed-scope implementation review. '
            'Read /review/source and permitted evidence under /review/evidence. '
            'Write your own report only to /report/review.md. Preserve original adverse findings. '
            'Use the terminal-review-verdict contract supplied in the evidence; schema server-terminal-review/v1. '
            'APPROVE or REQUEST_CHANGES is final; IN_PROGRESS preserves genuine unfinished inspection. '
            'Use exactly one verdict line: Final source/integration verdict: followed by your verdict. '
            'Prefer the bare line without Markdown prefix; only the exact ## prefix is also supported. '
            'Use exactly one terminal-review-verdict JSON fence with the same verdict. '
            'Distinguish source approval from later deployment and scientific gates. '
            'Do not claim indexed or supplied evidence was inspected. '
            'Findings may add IDs; preserve original judgments. Dispositions: '+', '.join(sorted(terminal.DISPOSITIONS))+
            ('\nHOST READ ACCESS: The operator authorizes independent read/discovery of the remote host '
             'through hostfs read/list/search with root-equivalent filesystem permissions. Use absolute host paths. '
             'Each response is a bounded live observation with identity, not frozen-candidate evidence. '
             'Use /review/source for the fixed candidate. Inspect relevant files; do not bulk-load the host '
             'or gratuitously reproduce secrets. No source edits, arbitrary execution, service control, '
             'installation, or use of discovered credentials is authorized. Bound report Write is unchanged. '
             'Scientific models do not acquire these tools.\n' if 'host_read' in config['runtime'] else '')+
            '\nCONTRACT TEMPLATE (NOT A REVIEW; replace instructions with your independent judgment):\n'+
            json.dumps(contract, sort_keys=True)+'\n'+question+
            '\nACTUAL SESSION: '+plan['session_id']+'\nEXACT MANIFEST SHA256: '+
            sha(read(directory/'terminal-manifest.json'))+'\nEXACT MANIFEST:\n'+read(directory/'terminal-manifest.json').decode()+
            ('\nPREVIOUS ORIGINAL REPORT (carry unresolved findings):\n'+prior if prior else ''))
        bounds = evidence.input_bounds(prompt, [])
        # Reserve the existing maximum original-file bounds, not a token estimate.
        export_headroom(directory, number-1)
        target = directory/'attempts'/f'{number:03d}'; target.mkdir(mode=0o700)
        save(target/'request.json', {'session_id': plan['session_id'], 'source': plan['source'],
            'attempt': number, 'manifest_sha256': sha(read(directory/'terminal-manifest.json')),
            'runtime_manifest_sha256': sha(read(directory/'manifest.json')),
            'previous_outcome_sha256': previous, 'prompt': prompt})
        save(target/'input-preflight.json', bounds)
        return {'status': 'PREPARED_NOT_ADMITTED', 'attempt': number, 'input': bounds}


def start(directory, number):
    config, _ = configured(); state, plan = _state(directory)
    _current_plan(directory, config, state, plan)
    require(type(number) is int and 1 <= number <= plan['max_attempts'], 'ATTEMPT_BOUND')
    target = directory/'attempts'/f'{number:03d}'
    with (directory/'execution.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if (target/'service-start-intent.json').exists(): return status(directory)
        require((target/'request.json').is_file(), 'PREPARED_REQUEST_REQUIRED')
        unit = f"research-system-inspection-{directory.name}-{number}"
        root = Path(__file__).resolve().parents[1]
        command = ['systemd-run', '--unit='+unit, '--no-block', '--service-type=exec',
            '--property=Restart=no', '--property=KillMode=control-group', '--property=TimeoutStopSec=20s',
            '--property=RuntimeMaxSec='+str(TERMINAL_SERVICE_SECONDS)+'s', '--property=MemoryMax=4294967296', '--property=CPUQuota=200%',
            '--property=TasksMax=128', '--property=UMask=0077', '--working-directory='+str(root),
            '/usr/bin/python3', '-B', '-m', 'orchestrator.inspection_runner', 'run-terminal',
            '--session', directory.name, '--attempt', str(number)]
        save(target/'service-start-intent.json', {'unit': unit+'.service', 'argv': command,
            'maximum_start_attempts': 1, 'automatic_retry': False})
        proc = subprocess.run(command, capture_output=True, timeout=30)
        write_once(target/'service-start.stdout.txt', proc.stdout)
        write_once(target/'service-start.stderr.txt', proc.stderr)
        save(target/'service-start-returned.json', {'returncode': proc.returncode})
        require(proc.returncode == 0, 'START_RECONCILE_NO_RETRY')
        return {'status': 'SERVER_SERVICE_START_SUBMITTED', 'unit': unit+'.service', 'scientific_execution': False}


def run(directory, number):
    config, _ = configured(); state, plan = _state(directory)
    _current_plan(directory, config, state, plan)
    service = runner.service_readback(f'research-system-inspection-{directory.name}-{number}.service')
    runner.require_service(service)
    target = directory/'attempts'/f'{number:03d}'
    with (directory/'execution.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # Parent records service submission before releasing this lock.
        require(not (target/'intent.json').exists() and not (target/'admission_event.json').exists(),
                'PRIOR_OPERATION_RECONCILE_NO_REPLAY')
        request = json.loads(read(target/'request.json'))
        require(request['manifest_sha256'] == sha(read(directory/'terminal-manifest.json'))
            and request['runtime_manifest_sha256'] == sha(read(directory/'manifest.json'))
            and request['attempt'] == number, 'REQUEST_CHANGED')
        rt = json.loads(read(directory/'runtime.json'))
        # Native runtime expects its own saved manifest, distinct from source-review manifest.
        command = runtime.command(directory, state, number, rt, json_schema={})
        bounds = evidence.input_bounds(request['prompt'], command)
        access.verify_view(json.loads(state['access_manifest_original']), directory/'view')
        save(target/'command.json', {'argv': command, 'invocation_id': os.environ['INVOCATION_ID'],
                                     'input_preflight': bounds,
                                     'wall_timeout_seconds': TERMINAL_TIMEOUT_SECONDS})
        save(target/'service-origin.json', service)
        runner.admit(target, state, request, config['permit'])
        intent = {'schema': 'server-terminal-launch-intent/v1',
            'plan_sha256': sha(read(directory/'terminal-inputs/server/plan.json')),
            'request_sha256': sha(read(target/'request.json')),
            'manifest_sha256': sha(read(directory/'terminal-manifest.json')),
            'session_id': directory.name, 'attempt': number, 'actor': plan['actor'],
            'maximum_invocations': 1, 'automatic_retry': False, 'admitted_at_utc': now(),
            **{key+'_sha256': sha(read(target/(key+'.json'))) for key in
               ('admission_event', 'admission_receipt', 'admission_policy', 'service-origin', 'command', 'control-readback')}}
        save(target/'intent.json', intent)
        start_time = time.monotonic()
        host_broker = None
        if 'host_read' in rt:
            from orchestrator import implementation_host_read as host
            host_broker = host.Broker(target/'read.sock', target/'host-reads',
                uid=rt['execution']['reviewer']['uid'], gid=rt['execution']['reviewer']['gid'],
                session=directory.name, attempt=number, cgroup=Path('/proc/self/cgroup').read_text())
        with host_broker if host_broker is not None else nullcontext():
            with (target/'protocol.jsonl').open('xb') as out, (target/'stderr.log').open('xb') as err:
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=out, stderr=err,
                    start_new_session=True, env={'PATH': '/usr/sbin:/usr/bin:/bin'}, cwd='/')
                save(target/'process.json', {'pid': process.pid,
                    'proc_stat': Path(f'/proc/{process.pid}/stat').read_text(),
                    'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip()})
                try:
                    process.communicate(request['prompt'].encode(), timeout=TERMINAL_TIMEOUT_SECONDS)
                except subprocess.TimeoutExpired:
                    save(target/'timeout.json', {'status': 'RECONCILIATION_REQUIRED', 'automatic_retry': False})
                    os.killpg(process.pid, signal.SIGTERM)
                    try: process.wait(timeout=10)
                    except subprocess.TimeoutExpired: os.killpg(process.pid, signal.SIGKILL); process.wait()
                finally:
                    try: os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                    process.wait()
        save(target/'returned.json', {'returncode': process.returncode, 'at_utc': now(),
                                      'wall_seconds': time.monotonic()-start_time,
                                      **({'host_reads': host_broker.originals()} if host_broker is not None else {})})
        return recover(directory, number)


def originals(directory, number):
    manifest_raw = read(directory/'terminal-manifest.json'); manifest = json.loads(manifest_raw)
    raw = {name: read(directory/'terminal-inputs'/name) for name in manifest['files']}
    for n in range(1, number+1):
        for name in evidence.ATTEMPT_NAMES:
            raw[f'launch/{n:03d}/{name}'] = read(directory/'attempts'/f'{n:03d}'/name)
    raw['report.md'] = raw[f'launch/{number:03d}/report.md']
    raw['session.jsonl'] = raw[f'launch/{number:03d}/session.jsonl']
    return manifest_raw, raw


def recover(directory, number):
    state, plan = _state(directory); target = directory/'attempts'/f'{number:03d}'
    require((target/'returned.json').exists(), 'ORIGINAL_RETURN_REQUIRED_NO_RETRY')
    for name, origin in [('report.md', target/'report/review.md'),
            ('session.jsonl', directory/'state/projects/-review'/(directory.name+'.jsonl'))]:
        if not (target/name).exists(): write_once(target/name, access.read_regular(origin, 16000000))
    statement = terminal._statement(read(target/'report.md'), profile=evidence.PROFILE, approval_required=False)
    outcome = {'verdict': statement['verdict'], 'report_sha256': sha(read(target/'report.md')),
        'journal_sha256': sha(read(target/'session.jsonl')), 'protocol_sha256': sha(read(target/'protocol.jsonl')),
        'attempt': number}
    if not (target/'outcome.json').exists(): save(target/'outcome.json', outcome)
    require(json.loads(read(target/'outcome.json')) == outcome, 'SAVED_OUTCOME_CHANGED')
    manifest_raw, raw = originals(directory, number)
    launch = evidence.validate_launch(manifest_raw, raw, statement)
    actual = terminal._session(raw['session.jsonl'], raw['report.md'], statement,
                              access.REPORT_PATH, server_launch=launch)
    provider = next(e for e in (json.loads(line) for line in raw[f'launch/{number:03d}/protocol.jsonl'].splitlines()
                    if line.strip()) if e.get('type') == 'result')
    result = {**outcome, 'status': 'INDEPENDENT_JUDGMENT_RECOVERED', 'session_id': directory.name,
        'actual_model': actual['provider_model'], 'usage': actual['usage_fragments_by_message'],
        'prepaid_units': actual['prepaid_units'], 'findings': statement['findings'],
        'remaining_gates': statement['remaining_gates'], 'unavailable': statement['unavailable'],
        'unverified': statement['unverified'], 'automatic_retry': False,
        'budget': {'attempts_used': number, 'remaining_attempts': plan['max_attempts']-number,
            'max_native_model_iterations_per_invocation': plan['max_iterations'],
            'returned_counters': {k: provider[k] for k in ('num_turns','duration_ms','total_cost_usd','usage') if k in provider},
            'returned_num_turns_is_native_iteration_counter': False},
        'source_approval_qualification': 'SEPARATE_IMPORT_REQUIRED', 'provider_calls': 0,
        'progress_checkpoint': ('Assess useful progress now; report recurring obstacles and recommend the smallest action. '
            'This is not an approval deadline or automatic halt.' if number >= 2 else 'First substantive invocation; retain findings.')}
    task = json.loads(read(directory/'saved-request.json'))
    folder = directory/'changes'/task['identity']
    recorded = changes.record(folder, 'DISPOSITION', {'kind': 'agent', 'family': 'claude',
        'model': actual['provider_model'], 'session_id': directory.name},
        {'rationale': 'Record original independent '+statement['verdict']+'; original report and actual session preserved. '
                      'This disposition grants no deployment/scientific authority.',
         'affected_results': ['This fixed implementation review only. All downstream gates remain.'],
         'original_review': {'request_sha256': sha(manifest_raw), 'response_sha256': sha(raw['report.md']),
                             'protocol_sha256': sha(raw['session.jsonl'])},
         'review_evidence': changes.preserve(folder, target/'report.md'),
         'recording_attribution': 'Server finalizer transcribes genuine Claude judgment without modifying it.'})
    result['recorded_outcome_event'] = recorded['identity']
    if not (target/'recovered.json').exists(): save(target/'recovered.json', result)
    require(json.loads(read(target/'recovered.json')) == result, 'RECOVERED_RESULT_CHANGED')
    return result


def status(directory):
    if not (directory/'manifest.json').exists():
        return {'status': 'PARTIAL_PREPARATION_RECONCILE', 'session_id': directory.name, 'automatic_retry': False}
    state, _ = _state(directory); rows = sorted((directory/'attempts').iterdir())
    if not rows: return {'status': 'PREPARATION_INCOMPLETE', 'session_id': directory.name}
    last = rows[-1]
    if (last/'recovered.json').exists(): return json.loads(read(last/'recovered.json'))
    if (last/'service-start-intent.json').exists() and not (last/'returned.json').exists():
        service = runner.service_readback(f'research-system-inspection-{directory.name}-{int(last.name)}.service')
        if service['ActiveState'] in ('active', 'activating') and service['MainPID'] != '0':
            return {'status': 'RUNNING_SERVER_OWNED', 'session_id': directory.name,
                    'attempt': int(last.name), 'service': service, 'automatic_retry': False}
    return {'status': 'OUTCOME_RECONCILIATION_REQUIRED' if (last/'intent.json').exists() else
            'SERVICE_START_RECORDED' if (last/'service-start-intent.json').exists() else 'PREPARED_NOT_ADMITTED',
            'session_id': directory.name, 'attempt': int(last.name), 'automatic_retry': False}


def reconcile(directory, number):
    """No retry. Recover only after the original service/process has ended."""
    configured(check_control=False); state, plan = _state(directory)
    with (directory/'execution.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        target = directory/'attempts'/f'{number:03d}'
        service = runner.service_readback(f'research-system-inspection-{directory.name}-{number}.service')
        require(service['MainPID'] == '0' and service['ActiveState'] in ('inactive', 'failed'),
                'SERVICE_STILL_ACTIVE')
        process = json.loads(read(target/'process.json'))
        boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        current = Path(f"/proc/{process['pid']}/stat")
        same = current.read_text() if current.exists() else None
        ticks = lambda value: value.rsplit(')', 1)[1].split()[19]
        require(boot != process['boot_id'] or same is None or ticks(same) != ticks(process['proc_stat']),
                'ORIGINAL_PROCESS_STILL_ACTIVE')
        # Without its original returned.json, a killed/uncertain call stays blocked.
        return recover(directory, number)


def export(directory, bundle):
    """Model-free export for the unchanged protected installer/accounting route."""
    configured(); state, plan = _state(directory)
    with (directory/'execution.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        number = len(list((directory/'attempts').iterdir()))
        result = recover(directory, number)
        require(result['verdict'] == 'APPROVE', 'SOURCE_APPROVAL_REQUIRED_FOR_INSTALL_EXPORT')
        manifest_raw, raw = originals(directory, number)
        proposal_raw = read(directory/'proposal.json'); proposal = json.loads(proposal_raw)
        files = {n: read(directory/'source-files'/n) for n in proposal['source_files']}
        approved = terminal.validate(manifest_raw, raw, proposal_raw, files)
        # Authenticate every PRE-admission against the ordinary current ledger.
        from orchestrator import install_reviewed_deployment as installer
        broker = json.loads(read(runner.BROKER_CONFIG)); status = installer.authenticated_ledger_status(broker)
        repo = installer._ledger_path(broker); cache = {}
        def commit(pin):
            if pin not in cache: cache[pin] = installer._terminal_accounting_commit(repo, pin)
            return cache[pin]
        # Locate each genuine transition on the complete current ledger parent chain.
        units = approved['terminal_session']['prepaid_units']; transitions = {}; cursor = status['pin']
        for _ in range(12000):
            current = commit(cursor); parents = current['parents']
            if len(parents) != 1: break
            before = commit(parents[0])['state']
            for unit, row in units.items():
                event = row['event']; key = 'server:'+event['turn_id']+':'+event['attempt']
                if key in current['state']['events'] and key not in before['events']:
                    transitions[unit] = {'unit_sha256': unit, 'event': event, 'receipt': row['receipt'], 'state_after': cursor}
            if len(transitions) == len(units): break
            cursor = parents[0]
        require(len(transitions) == len(units), 'PREPAID_LEDGER_ANCESTRY_REQUIRED')
        account = {'schema': 'server-terminal-accounting/v1',
            'manifest_sha256': sha(manifest_raw), 'report_sha256': sha(raw['report.md']),
            'journal_sha256': sha(raw['session.jsonl']), 'policy_sha256': commit(status['pin'])['state']['policy_sha256'],
            'ledger_pin': status['pin'], 'cases': list(transitions.values())}
        account_raw = runner.encoded(account)
        terminal.validate_accounting(account_raw, approved, status, status['pin'],
            commit(status['pin'])['state'], broker['policy'], broker['sources'], commit)
        require(installer.authenticated_ledger_status(broker) == status, 'ACCOUNTING_CHANGED_DURING_EXPORT')
        target = Path(bundle)/'terminal-review'
        require(not target.exists(), 'FRESH_EXPORT_OR_RECONCILE_REQUIRED')
        raw['manifest.json'] = manifest_raw
        require(len(raw) <= 7000 and sum(len(v) for v in raw.values()) <= 150000000
            and all(len(v) <= 16000000 for v in raw.values()), 'EXPORT_BOUND')
        target.mkdir(mode=0o700, parents=True)
        for name, value in raw.items(): write_once(target/name, value)
        save(target/'index.json', {'schema': 'inspection-deployment-file-index/v1',
            'files': {n: {'sha256': sha(v), 'bytes': len(v)} for n, v in raw.items()}})
        write_once(Path(bundle)/'terminal-accounting.json', account_raw)
        return {'status': 'SOURCE_AND_PREPAID_ACCOUNTING_VALIDATED_EXPORTED',
                'source': plan['source'], 'session_id': directory.name,
                'accounting_sha256': sha(account_raw), 'new_admissions': 0, 'deployment_authority': False}
