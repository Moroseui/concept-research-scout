"""Server initiation evidence for the existing terminal-review importer.

No provider call or authority is created by this module. The protected service's
original launch/admission/session records replace typed-human initiation ONLY.
The old human route and downstream installation/accounting checks stay separate.
"""
import re
from dataclasses import dataclass
from datetime import datetime

from orchestrator import change_requests as changes, deployment_review as gate
from orchestrator.review_input_codec import parsed

PROFILE = 'server-terminal-review/v1'
PLAN = 'server-terminal-launch-plan/v1'
AUTH_REQUEST = '86868322a6b42a2271cfba27fbe63130c0b8a8c8e42bcc22540af8e21c690e00'
AUTH_EVENT = '49d63692c3eb30e1c9dd9786aca7a05a347880ede845198dcca3f435cf2a990d'
OPERATOR_SHA = '49c7b218c2a4dad6ac46b4344277408f8166d88506a961427753dc490d89a3f5'
AMENDMENT_SHA = '2033b405e0d4f0b731101f530f4ed4332b71778e7613d8723aeacde03473547b'
MODEL = 'claude-opus-4-8'
CLI_VERSION = '2.1.222'
MAX_ATTEMPTS = 16
MAX_ITERATIONS = 32
MAX_PROMPT_BYTES = 256000
ATTEMPT_NAMES = {'request.json', 'intent.json', 'admission_event.json',
    'admission_receipt.json', 'admission_policy.json', 'service-origin.json',
    'command.json', 'process.json', 'returned.json', 'protocol.jsonl', 'control-readback.json',
    'report.md', 'session.jsonl', 'outcome.json'}


def require(ok, reason):
    gate.require(ok, 'SERVER_TERMINAL_' + reason)


def authority(raw):
    prefix = 'server-authority/'
    state = changes.validate_originals(raw[prefix+'request.json'],
        {n[len(prefix+'events/'):]: v for n, v in raw.items()
         if n.startswith(prefix+'events/')}, lambda n: raw[prefix+n])
    require(state['request']['identity'] == AUTH_REQUEST, 'AUTHORITY_REQUEST_CHANGED')
    event = next((e for e in state['events'] if e['identity'] == AUTH_EVENT), None)
    require(event is not None and event['event'] == 'AUTHORIZED'
        and event['actor'] == {'kind': 'human', 'identity': 'project-operator'},
        'ACTUAL_OPERATOR_AUTHORIZATION_REQUIRED')
    payload = event['payload']
    require(gate.digest(raw[prefix+payload['authority_reference']['artifact']]) ==
        payload['operator_original_sha256'] == OPERATOR_SHA
        and gate.digest(raw[prefix+payload['review_policy']['approved_amendment']['artifact']]) == AMENDMENT_SHA
        and payload['review_policy']['implementation_independent_review_required_before_use'] is True
        and all(payload[k] is False for k in ('candidate_approved', 'installation_approved',
                    'activation_approved', 'implementation_driver_relocation_approved')),
        'EXACT_AMENDMENT_AND_BOUNDARIES_REQUIRED')
    return event


def validate_plan(value):
    require(isinstance(value, dict) and set(value) == {'schema', 'session_id', 'source',
        'proposal_sha256', 'actor', 'max_attempts', 'max_iterations', 'model', 'cli_version',
        'context_sha256', 'permit_sha256', 'runtime_sha256', 'view_sha256',
        'enabling_source', 'installed_review_receipt_sha256', 'admission_binding',
        'operator_original_sha256'}, 'PLAN_SCHEMA')
    require(value['schema'] == PLAN and value['model'] == MODEL
        and value['cli_version'] == CLI_VERSION, 'FIXED_REVIEWER_REQUIRED')
    require(isinstance(value['session_id'], str) and re.fullmatch(
        r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', value['session_id']), 'SESSION_REQUIRED')
    for key in ('source', 'enabling_source'): gate.pin(value[key], 40)
    for key in ('proposal_sha256', 'context_sha256', 'permit_sha256', 'runtime_sha256',
                'view_sha256', 'installed_review_receipt_sha256'): gate.pin(value[key])
    changes.actor(value['actor'])
    require(value['actor']['kind'] == 'agent' and value['actor']['family'] == 'codex',
            'ATTRIBUTED_AGENT_INITIATION_REQUIRED')
    require(type(value['max_attempts']) is int and 1 <= value['max_attempts'] <= MAX_ATTEMPTS
        and type(value['max_iterations']) is int and 1 <= value['max_iterations'] <= MAX_ITERATIONS,
        'BOUNDED_CONTINUATION_REQUIRED')
    require(value['operator_original_sha256'] == OPERATOR_SHA, 'OPERATOR_BINDING_CHANGED')
    binding = value['admission_binding']
    require(isinstance(binding, dict) and set(binding) ==
        {'source', 'branch', 'kind', 'turn_id', 'policy_sha256'}
        and binding['kind'] == 'astra_turn'
        and binding['branch'] == 'astra/infrastructure-milestone-record', 'ADMISSION_BINDING')
    gate.pin(binding['source'], 40); gate.pin(binding['turn_id']); gate.pin(binding['policy_sha256'])
    return value


def original_names(raw):
    names = {n for n in raw if n.startswith('launch/')}
    require(names, 'SERVER_LAUNCH_ORIGINALS_REQUIRED')
    numbers = set()
    for name in names:
        match = re.fullmatch(r'launch/([0-9]{3})/(.+)', name)
        require(match and match[2] in ATTEMPT_NAMES, 'UNKNOWN_LAUNCH_ORIGINAL')
        numbers.add(int(match[1]))
    require(numbers == set(range(1, max(numbers)+1)) and max(numbers) <= MAX_ATTEMPTS,
            'COMPLETE_CONSECUTIVE_ATTEMPTS_REQUIRED')
    require(names == {f'launch/{n:03d}/{f}' for n in numbers for f in ATTEMPT_NAMES},
            'MISSING_LAUNCH_ORIGINAL')
    return names


def event_for(plan, number):
    require(type(number) is int and 1 <= number <= plan['max_attempts'], 'ATTEMPT_BOUND')
    return {**{k: plan['admission_binding'][k] for k in ('source', 'branch', 'kind', 'turn_id')},
            'attempt': str(number)}


def input_bounds(prompt, argv):
    require(isinstance(prompt, str) and prompt.strip(), 'PROMPT_REQUIRED')
    require(isinstance(argv, list) and all(isinstance(x, str) for x in argv), 'ARGV_REQUIRED')
    size = len(prompt.encode('utf-8')); argv_bytes = sum(len(x.encode('utf-8'))+1 for x in argv)
    require(size <= MAX_PROMPT_BYTES and argv_bytes <= 120000, 'COMPOSED_INPUT_BOUND')
    return {'prompt_characters': len(prompt), 'prompt_utf8_bytes': size,
            'argv_utf8_bytes': argv_bytes, 'tokens': None,
            'token_measurement': 'UNMEASURED; no character-to-token equivalence claimed',
            'prompt_byte_limit': MAX_PROMPT_BYTES, 'argv_byte_limit': 120000}


def _time(value):
    require(isinstance(value, str), 'TIMESTAMP_REQUIRED')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(dt.tzinfo is not None, 'TIMEZONE_REQUIRED')
    return dt


@dataclass(frozen=True)
class Launch:
    plan: dict
    attempts: list

    def units(self, events, session):
        """Match original SDK prompt events to saved, genuinely pre-admitted starts.

        SDK initiation is NOT represented as typed-human evidence. CLI internal
        meta records do not stand in for a launch or create a second charge.
        """
        users = []
        for event in events:
            if event.get('type') != 'user': continue
            content = event.get('message', {}).get('content')
            if isinstance(content, list) and content and all(isinstance(x, dict)
                    and x.get('type') == 'tool_result' for x in content): continue
            if event.get('isMeta') is True: continue
            require(event.get('sessionId') == session == self.plan['session_id']
                and event.get('isSidechain') is False and not event.get('isSynthetic')
                and not event.get('isCompactSummary') and not event.get('origin')
                and event.get('promptSource') == 'sdk' and event.get('entrypoint') == 'sdk-cli'
                and event.get('version') == CLI_VERSION and isinstance(content, str),
                'SDK_INITIATION_ORIGINAL_REQUIRED')
            users.append(event)
        require(len(users) == len(self.attempts), 'PROMPT_LAUNCH_COUNT_CHANGED')
        units = {}; seen = set()
        for user, attempt in zip(users, self.attempts):
            identity = user.get('uuid')
            require(isinstance(identity, str) and identity and identity not in seen,
                    'PROMPT_ID_REUSED')
            seen.add(identity)
            require(user['message']['content'] == attempt['request']['prompt']
                and _time(attempt['intent']['admitted_at_utc']) <= _time(user['timestamp'])
                <= _time(attempt['returned']['at_utc']), 'PROMPT_ADMISSION_BINDING_CHANGED')
            unit = {'session_id': session, 'request_uuid': identity,
                'request_sha256': gate.digest(gate.encoded(user)),
                'event': attempt['event'], 'receipt': attempt['receipt'],
                'intent_sha256': attempt['intent_sha256']}
            units[gate.digest(gate.encoded(unit))] = unit
        return units


def validate_launch(manifest_raw, raw, statement):
    from orchestrator import terminal_review as terminal
    authority(raw)
    manifest = parsed(manifest_raw)
    plan_raw = raw['server/plan.json']; plan = validate_plan(parsed(plan_raw))
    require(manifest['files'].get('server/plan.json') == gate.digest(plan_raw)
        and plan['source'] == manifest['source'] == statement['source']
        and plan['proposal_sha256'] == manifest['proposal_sha256']
        and plan['session_id'] == statement['session_id']
        and manifest['report_path'] == '/report/review.md', 'FIXED_SCOPE_CHANGED')
    for name, field in [('context', 'context_sha256'), ('permit', 'permit_sha256'),
                        ('runtime', 'runtime_sha256'), ('view', 'view_sha256'),
                        ('enabling-install', 'installed_review_receipt_sha256')]:
        require(gate.digest(raw['server/'+name+'.json']) == plan[field], 'SAVED_RUNTIME_BINDING_CHANGED')
    enabling = parsed(raw['server/enabling-install.json'])
    require(enabling['status'] == 'INSTALLED_REVIEW_VERIFIED' and enabling['source'] == plan['enabling_source'],
            'INDEPENDENTLY_INSTALLED_ENABLER_REQUIRED')
    original_names(raw)
    attempts = []; previous = None
    for number in range(1, len([n for n in raw if n.startswith('launch/') and n.endswith('/intent.json')])+1):
        prefix = f'launch/{number:03d}/'
        item = {name: parsed(raw[prefix+name]) for name in ATTEMPT_NAMES
                if name.endswith('.json')}
        request, intent, returned = item['request.json'], item['intent.json'], item['returned.json']
        require(request['attempt'] == number and request['session_id'] == plan['session_id']
            and request['manifest_sha256'] == gate.digest(manifest_raw)
            and request['previous_outcome_sha256'] == previous, 'REQUEST_CHAIN_CHANGED')
        if number > 1:
            require(attempts[-1]['outcome']['verdict'] == 'IN_PROGRESS', 'FINAL_VERDICT_NO_RESUBMISSION')
        require(request['prompt'].startswith('BEGIN_SHARED_OPERATING_CONTEXT\n'+
            raw['server/context.json'].decode()+'\nEND_SHARED_OPERATING_CONTEXT\n'),
            'ACTUAL_ROLE_CONTEXT_CHANGED')
        permit = parsed(raw['server/permit.json'])
        require(item['control-readback.json'] == permit['control_snapshot']
                and permit['operator_original_sha256'] == OPERATOR_SHA, 'NEW_STOP_OR_CHANGED_PERMIT')
        expected = {'schema': 'server-terminal-launch-intent/v1',
            'plan_sha256': gate.digest(plan_raw), 'request_sha256': gate.digest(raw[prefix+'request.json']),
            'manifest_sha256': gate.digest(manifest_raw), 'session_id': plan['session_id'],
            'attempt': number, 'actor': plan['actor'], 'maximum_invocations': 1,
            'automatic_retry': False,
            **{key+'_sha256': gate.digest(raw[prefix+key+'.json']) for key in
               ('admission_event', 'admission_receipt', 'admission_policy', 'service-origin', 'command', 'control-readback')},
            'admitted_at_utc': intent.get('admitted_at_utc')}
        require(intent == expected, 'AUTHENTICATED_LAUNCH_INTENT_CHANGED')
        event, receipt = item['admission_event.json'], item['admission_receipt.json']
        require(event == event_for(plan, number) and receipt.get('status') == 'ADMITTED'
            and receipt.get('duplicate_admission') is False and receipt.get('halted') is False
            and receipt.get('source') == event['source'], 'NORMAL_FRESH_ADMISSION_REQUIRED')
        require(gate.digest(raw[prefix+'admission_policy.json']) ==
            plan['admission_binding']['policy_sha256'], 'ADMISSION_POLICY_CHANGED')
        service = item['service-origin.json']
        require(service['Id'] == f"research-system-inspection-{plan['session_id']}-{number}.service"
            and service['ActiveState'] in ('active', 'activating')
            and service['InvocationID'] and str(service['MainPID']).isdigit()
            and int(service['MainPID']) > 1 and service['ControlGroup'], 'SYSTEMD_ORIGIN_REQUIRED')
        runtime_spec = parsed(raw['server/runtime.json'])
        if 'host_read' in runtime_spec:
            from orchestrator import implementation_host_read as host
            host.profile(runtime_spec['host_read'])
            host.validate_originals(returned.get('host_reads'), session=plan['session_id'], attempt=number)
        else:
            require('host_reads' not in returned, 'UNAUTHORIZED_HOST_READ_RECORDS')
        command = item['command.json']; process = item['process.json']
        require(command['invocation_id'] == service['InvocationID']
            and command['input_preflight'] == input_bounds(request['prompt'], command['argv'])
            and process['boot_id'] and process['proc_stat'] and type(process['pid']) is int
            and process['pid'] > 1 and returned['returncode'] == 0,
            'ACTUAL_EXECUTION_OR_RETURN_REQUIRED')
        require(command['argv'].count('--max-turns') == 1
            and command['argv'][command['argv'].index('--max-turns')+1] == str(plan['max_iterations'])
            and command['argv'].count('--model') == 1
            and command['argv'][command['argv'].index('--model')+1] == MODEL,
            'BOUNDED_ACTUAL_ARGUMENTS_REQUIRED')
        protocol = [parsed(x) for x in raw[prefix+'protocol.jsonl'].splitlines() if x.strip()]
        results = [x for x in protocol if x.get('type') == 'result']
        require(len(results) == 1 and results[0].get('session_id') == plan['session_id']
            and results[0].get('is_error') is False, 'GENUINE_FINAL_PROVIDER_RETURN_REQUIRED')
        for message in protocol:
            if message.get('type') == 'assistant':
                require(message.get('message', {}).get('model') == MODEL, 'UNEXPECTED_REVIEWING_MODEL')
        outcome = terminal._statement(raw[prefix+'report.md'], profile=PROFILE, approval_required=False)
        require(outcome['source'] == plan['source'] and outcome['proposal_sha256'] == plan['proposal_sha256']
            and outcome['manifest_sha256'] == gate.digest(manifest_raw)
            and outcome['session_id'] == plan['session_id'], 'OUTCOME_SCOPE_CHANGED')
        summary = {'verdict': outcome['verdict'], 'report_sha256': gate.digest(raw[prefix+'report.md']),
            'journal_sha256': gate.digest(raw[prefix+'session.jsonl']),
            'protocol_sha256': gate.digest(raw[prefix+'protocol.jsonl']), 'attempt': number}
        require(item['outcome.json'] == summary, 'OUTCOME_ORIGINAL_CHANGED')
        attempts.append({'request': request, 'intent': intent, 'returned': returned,
            'event': event, 'receipt': receipt, 'intent_sha256': gate.digest(raw[prefix+'intent.json']),
            'outcome': outcome})
        # Every continued report is genuinely written, not a fabricated progress sidecar.
        session = terminal._session(raw[prefix+'session.jsonl'], raw[prefix+'report.md'], outcome,
            manifest['report_path'], server_launch=Launch(plan, attempts))
        require(session['observed_models'] == [MODEL], 'JOURNAL_REVIEWING_MODEL_CHANGED')
        previous = gate.digest(raw[prefix+'outcome.json'])
    require(attempts and len(attempts) <= plan['max_attempts']
        and raw[prefix+'report.md'] == raw['report.md']
        and raw[prefix+'session.jsonl'] == raw['session.jsonl'], 'LATEST_ORIGINAL_OUTCOME_REQUIRED')
    return Launch(plan, attempts)
