"""Synthetic guarded server-profile integration; never a provider call or approval."""
from copy import deepcopy
import json
import pytest
from test_terminal_review import evidence, encoded, event_record, session_events, journal, SOURCE, SESSION, AGENT
from orchestrator import terminal_review as terminal, server_terminal_review as server
from orchestrator import inspection_access as access, change_requests as changes, deployment_review as gate


@pytest.fixture
def launched(evidence, monkeypatch):
    f = evidence
    # Preserve the unchanged manual authority and add a separately bound amendment.
    old = json.loads(f.raw[f.auth_key]); auth = deepcopy(old)
    auth['payload']['implementation_driver_relocation_approved'] = False
    auth['payload']['review_policy']['implementation_independent_review_required_before_use'] = True
    auth = event_record({k: v for k, v in auth.items() if k != 'identity'})
    for n, value in list(f.raw.items()):
        if n.startswith('authority/') and not n.startswith('authority/events/'):
            f.raw['server-'+n] = value
    f.raw['server-authority/events/0001-'+auth['identity']+'.json'] = encoded(auth)
    for name, value in [('AUTH_REQUEST', terminal.AUTH_REQUEST), ('AUTH_EVENT', auth['identity']),
                       ('OPERATOR_SHA', terminal.OPERATOR_SHA), ('AMENDMENT_SHA', terminal.AMENDMENT_SHA)]:
        monkeypatch.setattr(server, name, value)
    proposal = json.loads(f.proposal_raw); proposal['review_profile'] = server.PROFILE
    f.proposal_raw = encoded(proposal); f.raw['proposal.json'] = f.proposal_raw
    f.raw['change-bindings.json'] = encoded(changes.review_bindings(SOURCE, gate.digest(f.proposal_raw), proposal['changes']))
    f.manifest.update(schema=server.PROFILE, proposal_sha256=gate.digest(f.proposal_raw),
        report_path=access.REPORT_PATH, change_bindings_sha256=gate.digest(f.raw['change-bindings.json']))
    f.plan = {'schema': server.PLAN, 'session_id': SESSION, 'source': SOURCE,
        'proposal_sha256': gate.digest(f.proposal_raw), 'actor': AGENT, 'max_attempts': 2,
        'max_iterations': 32, 'model': server.MODEL, 'cli_version': server.CLI_VERSION,
        'context_sha256': '1'*64, 'permit_sha256': '2'*64, 'runtime_sha256': '3'*64,
        'view_sha256': '4'*64, 'enabling_source': 'b'*40, 'installed_review_receipt_sha256': '5'*64,
        'operator_original_sha256': server.OPERATOR_SHA,
        'admission_binding': {'source': 'b'*40, 'branch': 'astra/infrastructure-milestone-record', 'kind': 'astra_turn',
                              'turn_id': '6'*64, 'policy_sha256': gate.digest(encoded({'synthetic': True}))}}
    extras = {'context': b'{"synthetic":true}\n', 'runtime': b'{}\n',
        'permit': encoded({'control_snapshot': {'revision':19,'paused':1,'steering':[]}, 'operator_original_sha256':server.OPERATOR_SHA}),
        'view': b'{}\n', 'enabling-install': encoded({'status':'INSTALLED_REVIEW_VERIFIED','source':'b'*40})}
    for name, field in [('context','context_sha256'),('runtime','runtime_sha256'),('permit','permit_sha256'),
                        ('view','view_sha256'),('enabling-install','installed_review_receipt_sha256')]:
        f.raw['server/'+name+'.json'] = extras[name]; f.plan[field] = gate.digest(extras[name])
    f.raw['server/plan.json'] = encoded(f.plan)
    f.manifest['files'] = {n: gate.digest(v) for n, v in f.raw.items() if n not in ('report.md', 'session.jsonl')}
    f.manifest_raw = encoded(f.manifest)
    f.statement.update(schema=server.PROFILE, proposal_sha256=gate.digest(f.proposal_raw),
                       manifest_sha256=gate.digest(f.manifest_raw))
    seal_outcome(f)
    return f


def seal_outcome(f):
    report = ('Synthetic original server report only.\nFinal source/integration verdict: '+f.statement['verdict']+
              '\n```terminal-review-verdict\n'+json.dumps(f.statement)+'\n```\n').encode()
    events = session_events(report, access.REPORT_PATH)
    events[0].pop('origin'); events[0].update(promptSource='sdk', entrypoint='sdk-cli',
        version=server.CLI_VERSION, timestamp='2026-09-18T01:00:01Z')
    events[0]['message']['content'] = ('BEGIN_SHARED_OPERATING_CONTEXT\n'+f.raw['server/context.json'].decode()+
        '\nEND_SHARED_OPERATING_CONTEXT\nReview synthetic source only.')
    f.events = events
    f.raw['report.md'] = report; f.raw['session.jsonl'] = journal(events)
    req = {'attempt': 1, 'session_id': SESSION, 'source': SOURCE,
        'manifest_sha256': gate.digest(f.manifest_raw), 'previous_outcome_sha256': None,
        'prompt': events[0]['message']['content']}
    command = {'argv': ['claude', '--model', server.MODEL, '--max-turns', '32'], 'invocation_id': 'real-synthetic-unit'}
    command['input_preflight'] = server.input_bounds(req['prompt'], command['argv'])
    originals = {'request.json': encoded(req), 'admission_event.json': encoded(server.event_for(f.plan, 1)),
        'admission_receipt.json': encoded({'status': 'ADMITTED', 'duplicate_admission': False,
                                         'halted': False, 'source': 'b'*40}),
        'admission_policy.json': encoded({'synthetic': True}),
        'service-origin.json': encoded({'Id': f'research-system-inspection-{SESSION}-1.service',
            'ActiveState': 'active', 'InvocationID': 'real-synthetic-unit', 'MainPID': '99', 'ControlGroup': '/synthetic'}),
        'control-readback.json': encoded({'revision':19,'paused':1,'steering':[]}),
        'command.json': encoded(command), 'process.json': encoded({'pid': 100, 'boot_id': 'synthetic', 'proc_stat': 'synthetic'}),
        'returned.json': encoded({'returncode': 0, 'at_utc': '2026-09-18T01:01:00Z'}),
        'protocol.jsonl': encoded({'type': 'result', 'session_id': SESSION, 'is_error': False}),
        'report.md': report, 'session.jsonl': journal(events)}
    intent = {'schema': 'server-terminal-launch-intent/v1', 'plan_sha256': gate.digest(f.raw['server/plan.json']),
        'request_sha256': gate.digest(originals['request.json']), 'manifest_sha256': gate.digest(f.manifest_raw),
        'session_id': SESSION, 'attempt': 1, 'actor': f.plan['actor'], 'maximum_invocations': 1,
        'automatic_retry': False, 'admitted_at_utc': '2026-09-18T01:00:00Z',
        **{k+'_sha256': gate.digest(originals[k+'.json']) for k in
           ('admission_event','admission_receipt','admission_policy','service-origin','command','control-readback')}}
    originals['intent.json'] = encoded(intent)
    originals['outcome.json'] = encoded({'verdict': f.statement['verdict'], 'report_sha256': gate.digest(report),
        'journal_sha256': gate.digest(originals['session.jsonl']), 'protocol_sha256': gate.digest(originals['protocol.jsonl']), 'attempt': 1})
    f.raw.update({'launch/001/'+n: v for n, v in originals.items()})


def validate(f):
    return terminal.validate(f.manifest_raw, f.raw, f.proposal_raw, f.source_files)


def test_actual_sdk_not_a_forged_human_request(launched):
    result = validate(launched)
    assert result['terminal_profile'] == server.PROFILE
    assert result['terminal_session']['manual_units'] == {}
    assert len(result['terminal_session']['prepaid_units']) == 1
    assert result['approval_confers_deployment_authority'] is False


@pytest.mark.parametrize('verdict', ['REQUEST_CHANGES', 'IN_PROGRESS'])
def test_nonapproval_preserved_but_never_qualifies(launched, verdict):
    launched.statement['verdict'] = verdict; seal_outcome(launched)
    launch = server.validate_launch(launched.manifest_raw, launched.raw, launched.statement)
    assert launch.attempts[-1]['outcome']['verdict'] == verdict
    with pytest.raises(ValueError): validate(launched)


@pytest.mark.parametrize('name', sorted(server.ATTEMPT_NAMES))
def test_missing_launch_original_refuses(launched, name):
    del launched.raw['launch/001/'+name]
    with pytest.raises(ValueError): validate(launched)


@pytest.mark.parametrize('name,field,value', [
    ('intent.json','maximum_invocations',2), ('intent.json','automatic_retry',True),
    ('intent.json','actor',{'kind':'human','identity':'pretend'}),
    ('admission_receipt.json','duplicate_admission',True),
    ('admission_receipt.json','status','REFUSED'), ('admission_receipt.json','halted',True),
    ('service-origin.json','MainPID','0'), ('service-origin.json','InvocationID','changed'),
    ('request.json','prompt','Changed prompt'), ('request.json','previous_outcome_sha256','0'*64),
    ('returned.json','returncode',1), ('returned.json','at_utc','2026-09-17T00:00:00Z'),
    ('outcome.json','verdict','APPROVE_MANUFACTURED'),
])
def test_changed_originals_refuse_even_with_outer_inventory(launched, name, field, value):
    key = 'launch/001/'+name; row = json.loads(launched.raw[key]); row[field] = value; launched.raw[key] = encoded(row)
    with pytest.raises(ValueError): validate(launched)


def test_manual_route_does_not_accept_sdk_initiation(launched):
    with pytest.raises(ValueError, match='MANUAL_REQUEST_SHAPE'):
        terminal.manual_units(launched.events, SESSION)


@pytest.mark.parametrize('tool,args', [
    ('Write', {'file_path':'/review/source.py','content':'alter source'}),
    ('Write', {'file_path':'/report/../state/.credentials.json','content':'x'}),
    ('Write', {'file_path':'/report/review.md','content':'x','extra':'y'}),
    ('WebFetch', {'url':'https://example.test/docs','prompt':'docs'}),
    ('WebFetch', {'url':'https://code.claude.com@evil.test/docs','prompt':'docs'}),
    ('WebFetch', {'url':'https://code.claude.com/docs?data=private','prompt':'docs'}),
    ('WebFetch', {'url':'http://code.claude.com/docs','prompt':'docs'}),
])
def test_report_and_documentation_boundaries(tool, args):
    with pytest.raises(ValueError): access.terminal_request(tool, args)


def test_fixed_report_and_official_docs_allowed():
    assert access.terminal_request('Write', {'file_path':access.REPORT_PATH, 'content':'independent rejection'})
    assert access.terminal_request('WebFetch', {'url':'https://code.claude.com/docs/en/cli-reference', 'prompt':'Explain flag'})


def test_input_units_are_distinct_and_no_limit_increase():
    result = server.input_bounds(chr(233)*100, ['claude'])
    assert result['prompt_characters'] == 100 and result['prompt_utf8_bytes'] == 200
    assert result['tokens'] is None
    with pytest.raises(ValueError): server.input_bounds(chr(233)*128001, ['claude'])
    with pytest.raises(ValueError): server.input_bounds('small', ['x'*120001])


@pytest.mark.parametrize('kind', ['prepaid', 'late-charge-schema', 'missing-case', 'different-receipt', 'duplicate-charge'])
def test_prepaid_accounting_uses_real_limiter_once_and_rejects_mixed_routes(launched, kind):
    from datetime import datetime, timezone
    from test_terminal_review import SyntheticLedger
    from orchestrator import dispatch_limiter as limiter
    review = validate(launched)
    policy = {'status':'RATIFIED', 'operator_approval':'Synthetic only.',
        'state_write_permission':'OPERATOR_AUTHORIZED','n':48,'window':'UTC_CALENDAR_DAY',
        'state_ref':limiter.REF,'server_semantics':'OPERATOR_AUTHORIZED_V1',
        'reset_operators':['synthetic-operator']}
    store = SyntheticLedger()
    limiter.initialize(store, policy, {'actor':'synthetic-operator','role':'operator','decision_ref':'Synthetic only.'})
    unit, row = next(iter(review['terminal_session']['prepaid_units'].items()))
    receipt = limiter.admit_server(store, policy, row['event'], now=datetime(2026,9,18,tzinfo=timezone.utc))
    row['receipt'] = receipt
    case = {'unit_sha256':unit, 'event':row['event'], 'receipt':receipt, 'state_after':store.pin}
    execution = review['execution']
    account = {'schema':'server-terminal-accounting/v1', 'manifest_sha256':execution['request_sha256'],
        'report_sha256':execution['response_sha256'], 'journal_sha256':execution['protocol_sha256'],
        'policy_sha256':gate.digest(json.dumps(policy,sort_keys=True).encode()), 'ledger_pin':store.pin, 'cases':[case]}
    pin, state = store.read(); status = {'pin':pin, **{k:state[k] for k in ('count','day','sequence','halted')}}
    before = deepcopy(store.commits)
    if kind == 'late-charge-schema': account['schema']='operator-terminal-accounting/v1'
    if kind == 'missing-case': account['cases']=[]
    if kind == 'different-receipt': account['cases']=deepcopy(account['cases']); account['cases'][0]['receipt']['day']='2026-09-17'
    if kind == 'duplicate-charge': account['cases']=account['cases']*2
    def check():return terminal.validate_accounting(encoded(account), review, status, pin, state, policy, {'b'*40}, store.read_commit)
    if kind == 'prepaid':
        result=check(); assert result['late_charge'] is False and state['count']==1
    else:
        with pytest.raises(ValueError):check()
    assert store.commits == before


@pytest.mark.parametrize('field,value', [('max_attempts',17),('max_iterations',33),('max_attempts',True),
    ('model','claude-other'),('operator_original_sha256','0'*64)])
def test_plan_does_not_reset_or_expand_existing_bounds(launched, field, value):
    plan=deepcopy(launched.plan);plan[field]=value
    with pytest.raises(ValueError):server.validate_plan(plan)
