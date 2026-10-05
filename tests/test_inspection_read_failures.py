"""Synthetic hooks and protocol only; no native tool, provider, Git or admission."""
import copy
import json
import pytest
from orchestrator import inspection_access as access, inspection_review as review
from orchestrator import inspection_runner as runner, inspection_runtime as runtime
from orchestrator import deployment_review as gate, inspection_canary as canary
from test_inspection_review import fixture_manifest, fixture_attempt, events, replace_events

E, H = access.encoded, access.digest
ERROR = ('File content (293KB) exceeds maximum allowed size (256KB). Use offset and limit '
         'parameters to read specific portions of the file, or search for specific content '
         'instead of reading the whole file.')

TOKEN_ERROR = ('File content (25827 tokens) exceeds maximum allowed tokens (25000). '
               'Use offset and limit parameters to read specific portions of the file, '
               'or search for specific content instead of reading the whole file.')


def failure_fixture(tmp_path, *, direct=False, token=False, token_policy=True):
    """Use real hook writer + existing synthetic original parser fixture."""
    raw, policy = fixture_manifest()
    manifest = json.loads(raw); am = json.loads(manifest['access_manifest_original'])
    large = b'x\n'*150000
    am['files']['large.txt'] = {'sha256': H(large), 'bytes': len(large), 'line_count': 150000}
    if token and token_policy:
        am['read_failure_policy'] = access.READ_TOKEN_FAILURE_POLICY
    manifest['access_manifest_original'] = E(am).decode()
    manifest['access_manifest_sha256'] = H(E(am))
    probe = json.loads(fixture_attempt(raw, policy)['permission_probe'])
    probe['runtime_cli_sha256'] = access.READ_SIZE_ERROR_CLI_SHA256
    if token and token_policy:
        probe.update(read_boundary_version=canary.TOKEN_READ_BOUNDARY_VERSION,
                     token_limit_failure_verified=True)
    if direct:
        from orchestrator import inspection_model_policy as model
        manifest['model_policy_version']=model.DIRECT_VERSION
        probe['model_policy_version']=model.DIRECT_VERSION
    manifest['permission_probe_sha256'] = H(E(probe))
    raw = E(manifest)
    originals = fixture_attempt(raw, policy, status='IN_PROGRESS')
    originals['permission_probe'] = E(probe)
    view = tmp_path/'view'; view.mkdir()
    (view/'large.txt').write_bytes(large); (view/'code.py').write_bytes(b'a\nb\n')
    journal = tmp_path/'journal'; journal.mkdir(mode=0o700)
    config = {'schema': access.CONFIG_SCHEMA, 'source': manifest['source'],
              'access_manifest_sha256': H(E(am)), 'session_id': manifest['session_id'],
              'attempt_id': '1', 'journal_root': '/state/inspection-journal/1'}
    common = {'session_id': manifest['session_id'], 'cwd': '/review',
              'permission_mode': 'dontAsk', 'tool_name': 'Read', 'tool_use_id': 'size-read-1',
              'tool_input': {'file_path': '/review/large.txt'}}
    if token:
        common['tool_input'].update(offset=1, limit=993)
    error = TOKEN_ERROR if token else ERROR
    pre = {**common, 'hook_event_name': 'PreToolUse'}
    failure = {**common, 'hook_event_name': 'PostToolUseFailure',
               'error': error, 'is_interrupt': False, 'duration_ms': 1}
    for event in (pre, failure):
        output, observation = access.hook(config, E(am), E(event), view_root=view, journal_root=journal)
        assert output == {}
        failure_status = 'UNQUALIFIED' if token and not token_policy else 'OBSERVED_FAILURE'
        assert observation['status'] in ('ALLOWED', failure_status)
    original_rows = []
    for phase in ('pre', 'failure'):
        original_rows.append(E({'observation_original': (journal/('size-read-1.'+phase+'.observation.json')).read_bytes().decode(),
            'hook_input_original': (journal/('size-read-1.'+phase+'.input.json')).read_bytes().decode()}))
    originals['journal'] += original_rows
    stream = events(originals)
    stream.insert(-1, {'type': 'assistant', 'session_id': manifest['session_id'],
        'message': {'model': review.MODEL, 'content': [
            {'type': 'tool_use', 'id': 'size-read-1', 'name': 'Read', 'input': common['tool_input']}]}})
    stream.insert(-1, {'type': 'user', 'session_id': manifest['session_id'],
        'message': {'content': [{'type': 'tool_result', 'tool_use_id': 'size-read-1',
                                'is_error': True, 'content': error}]},
        'tool_use_result': 'Error: '+error})
    if direct:
        from test_inspection_direct_opus import direct_events
        stream=direct_events(stream)
    replace_events(originals, stream)
    return raw, policy, originals, config, am, view, journal, failure


def changed_row(originals, index, mutate):
    wrapper = json.loads(originals['journal'][index])
    row, hook = json.loads(wrapper['observation_original']), json.loads(wrapper['hook_input_original'])
    mutate(row, hook)
    wrapper['hook_input_original'] = E(hook).decode()
    row['raw_input_sha256'] = H(E(hook))
    wrapper['observation_original'] = E(row).decode()
    originals['journal'][index] = E(wrapper)


@pytest.mark.parametrize('token', [False, True])
def test_real_hook_writer_and_parser_keep_failure_originals_without_read_credit(tmp_path, token):
    raw, _, originals, _, _, _, journal, failure = failure_fixture(tmp_path, token=token)
    result = review.validate_session(raw, [originals])
    receipt = result['attempts'][0]
    assert result['status'] == 'IN_PROGRESS'
    assert receipt['reads'] == {'code.py': [[1, 2]]}
    assert receipt['denials'] == []
    assert len(receipt['tool_failures']) == 1
    error = receipt['tool_failures'][0]
    assert error['kind'] == ('READ_TOKEN_EXECUTION_ERROR' if token else 'READ_SIZE_EXECUTION_ERROR')
    assert error['coverage'] == []
    if token:
        assert (error['reported_tokens'], error['maximum_tokens']) == (25827, 25000)
        assert error['requested_range'] == {'path': 'large.txt', 'start_line': 1, 'limit': 993}
    assert error['path'] == 'large.txt' and error['file_bytes'] == 300000
    assert error['runtime_cli_sha256'] == access.READ_SIZE_ERROR_CLI_SHA256
    assert (journal/'size-read-1.failure.input.json').read_bytes() == E(failure)


def test_known_error_without_failure_original_keeps_old_refusal(tmp_path):
    raw, _, originals, *_ = failure_fixture(tmp_path)
    originals['journal'].pop()
    result = review.parse_attempt(raw, originals)
    assert result['status'] == 'RECONCILIATION_REQUIRED'
    assert result['reason'] == 'MISSING_ALLOWED_TOOL_HOOK_OR_RESULT'


@pytest.mark.parametrize('mutation', [
    'wrong_cli', 'no_pre', 'denied_pre', 'pre_hash', 'orphan', 'duplicate', 'unknown_error',
    'interrupted', 'duration_bool', 'duration_negative', 'tool_response', 'file_sha',
    'result_success', 'result_text', 'separate_output', 'native_denial', 'read_credit',
    'source', 'session', 'input', 'attempt', 'normalized', 'error_hash'])
@pytest.mark.parametrize('token', [False, True])
def test_conflicting_failure_originals_refuse(tmp_path, mutation, token):
    raw, _, original, *_ = failure_fixture(tmp_path, token=token)
    a = copy.deepcopy(original); stream = events(a)
    if mutation == 'wrong_cli':
        m=json.loads(raw); probe=json.loads(a['permission_probe'])
        probe['runtime_cli_sha256']='0'*64; a['permission_probe']=E(probe)
        m['permission_probe_sha256']=H(a['permission_probe']); raw=E(m)
        # Exercise the exact journal predicate without changing unrelated manifest/intent bindings.
        failures=[]
        with pytest.raises(ValueError, match='RUNTIME_OR_COLLECTOR'):
            review._journal(m,1,stream,a['journal'],runtime_cli_sha256='0'*64,observed_failures=failures)
        return
    if mutation == 'no_pre': del a['journal'][-2]
    elif mutation == 'denied_pre':
        changed_row(a,-2,lambda r,h:r.update(status='DENIED'))
        changed_row(a,-1,lambda r,h:r.update(pre_observation_sha256=H(json.loads(a['journal'][-2])['observation_original'].encode())))
    elif mutation == 'pre_hash': changed_row(a,-1,lambda r,h:r.update(pre_observation_sha256='0'*64))
    elif mutation == 'orphan': changed_row(a,-1,lambda r,h:r.update(tool_use_id='other'))
    elif mutation == 'duplicate': a['journal'].append(a['journal'][-1])
    elif mutation == 'unknown_error': changed_row(a,-1,lambda r,h:h.update(error='ENOENT'))
    elif mutation == 'interrupted': changed_row(a,-1,lambda r,h:h.update(is_interrupt=True))
    elif mutation == 'duration_bool': changed_row(a,-1,lambda r,h:h.update(duration_ms=True))
    elif mutation == 'duration_negative': changed_row(a,-1,lambda r,h:h.update(duration_ms=-1))
    elif mutation == 'tool_response': changed_row(a,-1,lambda r,h:h.update(tool_response={}))
    elif mutation == 'file_sha': changed_row(a,-1,lambda r,h:r['native_failure'].update(file_sha256='0'*64))
    elif mutation == 'result_success': stream[-2]['message']['content'][0]['is_error']=False
    elif mutation == 'result_text': stream[-2]['message']['content'][0]['content']='other'
    elif mutation == 'separate_output': stream[-2]['tool_use_result']='Error: other'
    elif mutation == 'native_denial': stream[-1]['permission_denials']=[{'tool_use_id':'size-read-1','tool_name':'Read','tool_input':{'file_path':'/review/large.txt'}}]
    elif mutation == 'read_credit': changed_row(a,-1,lambda r,h:r.update(actual_read={'path':'large.txt'}))
    elif mutation == 'source': changed_row(a,-1,lambda r,h:r.update(source='b'*40))
    elif mutation == 'session': changed_row(a,-1,lambda r,h:h.update(session_id='22222222-2222-2222-2222-222222222222'))
    elif mutation == 'input': changed_row(a,-1,lambda r,h:h['tool_input'].update(offset=2))
    elif mutation == 'attempt': changed_row(a,-1,lambda r,h:r.update(attempt_id='2'))
    elif mutation == 'normalized': changed_row(a,-1,lambda r,h:r['normalized_request'].update(start_line=2))
    elif mutation == 'error_hash': changed_row(a,-1,lambda r,h:r['native_failure'].update(error_sha256='0'*64))
    replace_events(a,stream)
    assert review.parse_attempt(raw,a)['status']=='RECONCILIATION_REQUIRED'


@pytest.mark.parametrize('error', ['ENOENT', 'InputValidationError: missing pattern',
    ERROR.replace('256KB','512KB'), ERROR.replace('293KB','294KB')])
def test_hook_unknown_failure_is_preserved_unqualified(tmp_path,error):
    _,_,_,config,am,view,journal,failure=failure_fixture(tmp_path)
    failure['tool_use_id']='second-error'; failure['error']=error
    pre={k:v for k,v in failure.items() if k not in ('error','is_interrupt','duration_ms')}
    pre['hook_event_name']='PreToolUse'
    access.hook(config,E(am),E(pre),view_root=view,journal_root=journal)
    output,row=access.hook(config,E(am),E(failure),view_root=view,journal_root=journal)
    assert output=={} and row['status']=='UNQUALIFIED' and row['actual_read'] is None
    assert (journal/'second-error.failure.input.json').read_bytes()==E(failure)


@pytest.mark.parametrize('change', ['no_pre','changed_view','post_exists','denied_pre'])
def test_failure_hook_requires_unchanged_allowed_pre_and_view(tmp_path,change):
    _,_,_,config,am,view,journal,failure=failure_fixture(tmp_path)
    failure['tool_use_id']='new-error'
    pre={k:v for k,v in failure.items() if k not in ('error','is_interrupt','duration_ms')}
    pre['hook_event_name']='PreToolUse'
    if change!='no_pre':
        access.hook(config,E(am),E(pre),view_root=view,journal_root=journal)
    if change=='changed_view': (view/'large.txt').write_bytes(b'changed\n')
    if change=='post_exists': (journal/'new-error.post.input.json').write_bytes(b'{}')
    if change=='denied_pre':
        p=journal/'new-error.pre.observation.json'; r=json.loads(p.read_bytes());r['status']='DENIED';p.write_bytes(E(r))
    _,row=access.hook(config,E(am),E(failure),view_root=view,journal_root=journal)
    assert row['status']=='UNQUALIFIED'


def test_failure_original_cannot_be_overwritten(tmp_path):
    *_,config,am,view,journal,failure=failure_fixture(tmp_path)
    before={p.name:p.read_bytes() for p in journal.iterdir()}
    with pytest.raises(FileExistsError):
        access.hook(config,E(am),E(failure),view_root=view,journal_root=journal)
    assert before=={p.name:p.read_bytes() for p in journal.iterdir()}


@pytest.mark.parametrize('size,label',[(262144,'256KB'),(300000,'293KB'),
    (1048575,'1024KB'),(1048576,'1MB'),(1310720,'1.3MB'),
    (1572864,'1.5MB'),(1330489,'1.3MB')])
def test_pinned_native_size_rounding_boundaries(size,label):
    assert access._read_size_label(size)==label


@pytest.mark.parametrize('tool_input',[
    {'file_path':'/review/large.txt','limit':100},
    {'file_path':'/review/large.txt','offset':1},
    {'file_path':'/review/large.txt','offset':2},
    {'file_path':'/review/large.txt','pages':'1'},
    {'file_path':'/state/private'}, {'file_path':'/review/large.txt','offset':True}])
def test_predicate_never_accepts_other_read_paths_or_range_errors(tmp_path,tool_input):
    _,_,_,_,am,*_=failure_fixture(tmp_path)
    with pytest.raises(ValueError): access.read_size_failure(am,tool_input,ERROR)


def test_failure_does_not_satisfy_required_large_file_or_allow_terminal_resume(tmp_path):
    raw,p,a,*_=failure_fixture(tmp_path)
    m=json.loads(raw);m['required_ranges']['large.txt']=[[1,150000]]
    # Direct journal proves no large-file range regardless of its presence/size.
    failures=[];reads,_=review._journal(m,1,events(a),a['journal'],
        runtime_cli_sha256=access.READ_SIZE_ERROR_CLI_SHA256,observed_failures=failures)
    assert review._coverage(m['required_ranges'],reads)=={'large.txt':[[1,150000]]}
    stream=events(a);stream[-1]['structured_output']['status']='REQUEST_CHANGES';replace_events(a,stream)
    receipt=review.parse_attempt(raw,a)
    b=fixture_attempt(raw,p,number=2,previous=receipt)
    b['permission_probe']=a['permission_probe']
    with pytest.raises(ValueError,match='TERMINAL_REVIEW'):
        review.validate_session(raw,[a,b])


def test_first_attempt_historical_resolutions_still_refused(tmp_path):
    raw,_,a,*_=failure_fixture(tmp_path)
    stream=events(a)
    stream[-1]['structured_output']['resolved']=[{'field':'findings','original':'Historical criticism','response':'Preserved response'}]
    replace_events(a,stream)
    with pytest.raises(ValueError,match='RESOLUTION_WITHOUT_PREVIOUS_ATTEMPT'):
        review.validate_session(raw,[a])


def test_success_only_receipt_shape_unchanged():
    raw,p=fixture_manifest();a=fixture_attempt(raw,p)
    assert 'tool_failures' not in review.parse_attempt(raw,a)


@pytest.mark.parametrize('token', [False, True])
def test_failure_reader_and_deployment_loader_preserve_identical_originals(tmp_path, token):
    raw,_,a,*_=failure_fixture(tmp_path, token=token)
    directory=tmp_path/'session';target=directory/'attempts/001';target.mkdir(parents=True)
    (directory/'permission-probe.json').write_bytes(a['permission_probe'])
    exported={}
    for name,value in a.items():
        if name in ('journal','timeout','reconciliation','permission_probe'):continue
        leaf=name+('.jsonl' if name=='protocol' else '.json')
        (target/leaf).write_bytes(value);exported['attempts/001/'+leaf]=value
    (target/'journal').mkdir()
    for raw_row in a['journal']:
        wrap=json.loads(raw_row);row=json.loads(wrap['observation_original'])
        suffix={'PreToolUse':'pre','PostToolUse':'post','PostToolUseFailure':'failure'}[row['phase']]
        stem=row['tool_use_id']+'.'+suffix
        # Fixture successful rows omit raw_input_file; native loader requires it.
        row['raw_input_file']=stem+'.input.json'
        for end,value in (('.input.json',wrap['hook_input_original'].encode()),('.observation.json',E(row))):
            (target/'journal'/(stem+end)).write_bytes(value)
            exported['attempts/001/journal/'+stem+end]=value
    exported['attempts/001/response.json']=b'{}'
    exported['attempts/001/execution.json']=b'{}'
    loaded=runner.original_attempt(target)
    deployed=gate._inspection_attempt(exported,1,a['permission_probe'])['originals']
    assert loaded==deployed
    assert any('PostToolUseFailure' in x.decode() for x in loaded['journal'])
    exported['attempts/001/journal/orphan.failure.input.json']=b'{}'
    with pytest.raises(ValueError,match='ORPHAN_JOURNAL'):
        gate._inspection_attempt(exported,1,a['permission_probe'])


def test_new_settings_add_no_permissions_and_only_read_failure_hook():
    settings=access.access_settings()
    failure=settings['hooks']['PostToolUseFailure']
    assert failure[0]['matcher']=='Read'
    assert failure[0]['hooks'][0]['command'].endswith('failure --config /runtime/inspection-access.json')
    assert settings['permissions']['defaultMode']=='dontAsk'
    assert not settings['permissions'].get('allow')
    assert 'Read(//state/**)' in settings['permissions']['deny']


def test_actual_command_schema_binds_first_attempt_and_does_not_coerce_results(tmp_path,monkeypatch):
    raw,_=fixture_manifest();m=json.loads(raw);(tmp_path/'manifest.json').write_bytes(raw)
    captured=[]
    monkeypatch.setattr(runtime,'command',lambda *args,**kw:captured.append(kw['json_schema']) or ['synthetic-no-execution'])
    runner.runtime_command(tmp_path,m,1,{})
    previous = review.validate_session(raw, [fixture_attempt(raw, _, status='IN_PROGRESS')])['attempts'][-1]
    runner.runtime_command(tmp_path,m,2,{},previous=previous)
    assert captured[0]['properties']['resolved']['maxItems']==0
    assert 'maxItems' not in captured[1]['properties']['resolved']
    assert 'historical' in captured[0]['properties']['resolved']['description']


@pytest.mark.parametrize('token', [False, True])
def test_direct_opus_profile_keeps_identity_and_requires_failure_original(tmp_path, token):
    raw,_,a,*_=failure_fixture(tmp_path,direct=True,token=token)
    result=review.validate_session(raw,[a])
    assert result['status']=='IN_PROGRESS' and result['provider_model']=='claude-opus-4-8'
    assert result['attempts'][0]['assistant_models']==['claude-opus-4-8']
    a['journal'].pop()
    assert review.parse_attempt(raw,a)['reason']=='MISSING_ALLOWED_TOOL_HOOK_OR_RESULT'


@pytest.mark.parametrize('token', [False, True])
def test_following_bounded_read_gets_only_its_actual_lines(tmp_path, token):
    raw,_,a,config,am,view,journal,_=failure_fixture(tmp_path,token=token)
    common={'session_id':config['session_id'],'cwd':'/review','permission_mode':'dontAsk',
        'tool_name':'Read','tool_use_id':'bounded-read',
        'tool_input':{'file_path':'/review/large.txt','offset':1,'limit':2}}
    pre={**common,'hook_event_name':'PreToolUse'}
    post={**common,'hook_event_name':'PostToolUse','tool_response':{
        'type':'text','file':{'filePath':'/review/large.txt','content':'x\nx',
        'numLines':2,'startLine':1,'totalLines':150001}}}
    for event in (pre,post):
        _,row=access.hook(config,E(am),E(event),view_root=view,journal_root=journal)
        assert row['status'] in ('ALLOWED','OBSERVED')
    for phase in ('pre','post'):
        a['journal'].append(E({'observation_original':(journal/('bounded-read.'+phase+'.observation.json')).read_bytes().decode(),
                              'hook_input_original':(journal/('bounded-read.'+phase+'.input.json')).read_bytes().decode()}))
    stream=events(a)
    stream.insert(-1,{'type':'assistant','session_id':config['session_id'],
        'message':{'model':review.MODEL,'content':[{'type':'tool_use','id':'bounded-read',
        'name':'Read','input':common['tool_input']}]}})
    stream.insert(-1,{'type':'user','session_id':config['session_id'],
        'message':{'content':[{'type':'tool_result','tool_use_id':'bounded-read','content':'Synthetic formatted result'}]}})
    replace_events(a,stream)
    receipt=review.parse_attempt(raw,a)
    assert receipt['status']=='IN_PROGRESS'
    assert receipt['reads']['large.txt']==[[1,2]]
    assert len(receipt['tool_failures'])==1


def test_historical_ranged_token_failure_stays_unqualified(tmp_path):
    raw, _, originals, _, am, _, journal, failure = failure_fixture(
        tmp_path, token=True, token_policy=False)
    before = {p.name: p.read_bytes() for p in journal.iterdir()}
    assert 'read_failure_policy' not in am
    with pytest.raises(ValueError, match='INSPECTION_READ_SIZE_EXACT_REQUEST_REQUIRED'):
        access.verify_read_failure(am, failure['tool_input'], failure)
    receipt = review.parse_attempt(raw, originals)
    assert receipt['status'] == 'RECONCILIATION_REQUIRED'
    assert receipt['reason'] == 'UNQUALIFIED_TOOL'
    assert before == {p.name: p.read_bytes() for p in journal.iterdir()}


@pytest.mark.parametrize('marker', [None, '', 'native-read-token-limit/v2', True])
def test_unknown_token_policy_marker_is_not_legacy_default(tmp_path, marker):
    _, _, _, _, am, *_ = failure_fixture(tmp_path)
    am['read_failure_policy'] = marker
    with pytest.raises(ValueError):
        access.validate_access_manifest(E(am))


@pytest.mark.parametrize('count', ['25001', '25827', '4000000'])
def test_token_error_uses_fixed_maximum_and_bounded_decimal_count(tmp_path, count):
    _, _, _, _, am, _, _, failure = failure_fixture(tmp_path, token=True)
    error = TOKEN_ERROR.replace('25827', count)
    result = access.read_token_failure(am, failure['tool_input'], error)
    assert result['reported_tokens'] == int(count)
    assert result['maximum_tokens'] == 25000 and result['coverage'] == []


@pytest.mark.parametrize('error', [
    TOKEN_ERROR.replace('25827', count)
    for count in ['25000', '0', '-25827', '025827', '25827.0', '2.5827e4', '4000001', '9'*50]
] + [TOKEN_ERROR.replace('(25000)', '(25001)'), TOKEN_ERROR+' ', 'Permission denied'])
def test_token_error_refuses_malformed_count_maximum_or_other_error(tmp_path, error):
    _, _, _, _, am, _, _, failure = failure_fixture(tmp_path, token=True)
    with pytest.raises(ValueError):
        access.read_token_failure(am, failure['tool_input'], error)


@pytest.mark.parametrize('tool_input', [
    {'file_path': '/review/large.txt'},
    {'file_path': '/review/large.txt', 'offset': 1},
    {'file_path': '/review/large.txt', 'limit': 993},
    {'file_path': '/review/large.txt', 'offset': 0, 'limit': 993},
    {'file_path': '/review/large.txt', 'offset': True, 'limit': 993},
    {'file_path': '/review/large.txt', 'offset': 1, 'limit': False},
    {'file_path': '/review/large.txt', 'offset': 150001, 'limit': 1},
    {'file_path': '/review/large.txt', 'offset': 1, 'limit': 10001},
    {'file_path': '/review/large.txt', 'offset': 1, 'limit': 993, 'pages': '1'},
    {'file_path': '/state/private', 'offset': 1, 'limit': 993},
])
def test_token_error_requires_exact_bounded_in_view_range(tmp_path, tool_input):
    _, _, _, _, am, *_ = failure_fixture(tmp_path, token=True)
    with pytest.raises(ValueError):
        access.read_token_failure(am, tool_input, TOKEN_ERROR)


def test_token_failure_has_no_required_range_credit(tmp_path):
    raw, _, originals, *_ = failure_fixture(tmp_path, token=True)
    m = json.loads(raw); m['required_ranges']['large.txt'] = [[1, 150000]]
    failures = []
    reads, _ = review._journal(m, 1, events(originals), originals['journal'],
        runtime_cli_sha256=access.READ_SIZE_ERROR_CLI_SHA256, observed_failures=failures)
    assert failures[0]['coverage'] == []
    assert review._coverage(m['required_ranges'], reads) == {'large.txt': [[1, 150000]]}
