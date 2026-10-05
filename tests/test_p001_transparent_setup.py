"""Synthetic renderer/native-result tests; no Colab, install or model calls."""
import ast
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator import p001_transparent_setup as transparent
from orchestrator import p001_runtime_setup as setup
from test_p001_runtime_setup import inputs, environment  # Existing verified synthetic fixtures.


@pytest.fixture
def packet(inputs):
    prior, receipt, _ = inputs
    return transparent.prepare(Path('/synthetic/frozen'), prior, receipt)


def native(value):
    return {'outputs': [{'output_type': 'stream', 'name': 'stdout', 'text': [json.dumps(value)]}]}


def outcomes(packet):
    binding = packet['request']['binding_sha256']
    return [{'cpu_only': True, 'colab_runtime': True},
        {'status':'EXCLUSIVE_SETUP_INTENT_CREATED','binding_sha256':binding,
            'exclusive_intent_created':True,'patient_launch_authorized':False},
        {'status':'SOURCE_DEPENDENCY_SETUP_COMPLETE','binding_sha256':binding,
            'source_postcondition_verified':True,'patient_launch_authorized':False,
            'operations':[{'operation':name,'status':'COMPLETE','returncode':0,'command_count':[7,1,0][i],
                'source_sha256':packet['request']['source_sha256'][i],
                'presentation_sha256':packet['presentation_sha256'][i],
                'elapsed_seconds':0.5,'original_log_private':True}
                for i,name in enumerate(transparent.OPERATIONS)]},
        {'status':'DEFAULT_CHILD_ENVIRONMENT_OBSERVED','binding_sha256':binding,'environment':environment()}]


def test_four_readable_cells_keep_original_request_and_frozen_statements(packet, inputs):
    original = setup.packet(Path('/synthetic/frozen'), inputs[0], inputs[1], transparent.REQUEST_ID)
    assert packet['request'] == original['request']
    assert packet['original_setup_packet_sha256'] == transparent.sha(transparent.canonical(original))
    assert [s['name'] for s in packet['stages']] == list(transparent.STAGES)
    assert len(packet['cells']) == 4 and packet['maximum_run_calls'] == 4
    for cell in packet['cells']:
        compile(cell,'synthetic-readable-cell','exec')
        calls=[n for n in ast.walk(ast.parse(cell)) if isinstance(n,ast.Call)]
        assert not any(isinstance(n.func,ast.Name) and n.func.id in ('exec','eval','compile') for n in calls)
        assert not any(isinstance(n.func,ast.Attribute) and n.func.attr=='dup2' for n in calls)
    assert '_p001_operation.run' in packet['cells'][2]
    assert 'pip' in packet['cells'][2] and 'CHILD_ENVIRONMENT_SOURCE = r"""' in packet['cells'][3]
    import inspect
    child = next(n.value.value for n in ast.parse(packet['cells'][3]).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CHILD_ENVIRONMENT_SOURCE' for t in n.targets))
    assert ast.dump(ast.parse(child),include_attributes=False) == ast.dump(ast.parse(inspect.getsource(setup.child_environment)),include_attributes=False)
    assert packet['patient_launch_authorized'] is False
    with pytest.raises(ValueError,match='ORIGINAL_REQUEST'):
        transparent.prepare(Path('/synthetic/frozen'),inputs[0],inputs[1],'another-request')


def run_claim_with_synthetic_observation(packet, observation, tmp_path):
    """Replace only the read-only collector and bound fixture paths; retain real guard/claim code."""
    request=copy.deepcopy(packet['request'])
    request['source_root']=str(tmp_path/'source');request['setup_root']=str(tmp_path/'setup')
    tree=ast.parse(packet['cells'][1]); kept=[]
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name=='runtime_observation':continue
        if isinstance(node,ast.Assign) and any(isinstance(n,ast.Name) and n.id=='request' for n in node.targets):continue
        kept.append(node)
    namespace={'request':request,'runtime_observation':lambda value:observation}
    exec(compile(ast.Module(body=kept,type_ignores=[]),'synthetic-claim-guard','exec'),namespace)
    return request


@pytest.mark.parametrize('change',[
    lambda x:x['runtime'].update(fingerprint_sha256='e'*64),
    lambda x:x['drive'].update(visible=False),
    lambda x:x['processes'].update(scan_complete=False),
    lambda x:x['processes'].update(matches=[{'pid':3}]),
    lambda x:x['execution_paths'].update(checkpoint_index={'state':'PRESENT'}),
])
def test_actual_claim_cell_guards_stop_before_any_write(packet, inputs, tmp_path, change):
    observed=copy.deepcopy(inputs[1]['observation']);change(observed)
    with pytest.raises(ValueError,match='SETUP_'):
        run_claim_with_synthetic_observation(packet,observed,tmp_path)
    assert not (tmp_path/'setup').exists()


def test_claim_cell_preserves_existing_source_and_setup_intent(packet, inputs, tmp_path):
    observed=copy.deepcopy(inputs[1]['observation'])
    (tmp_path/'source').mkdir()
    with pytest.raises(ValueError,match='ALREADY_EXISTS'):
        run_claim_with_synthetic_observation(packet,observed,tmp_path)
    assert not (tmp_path/'setup').exists()
    (tmp_path/'source').rmdir()
    run_claim_with_synthetic_observation(packet,observed,tmp_path)
    before=(tmp_path/'setup/intent.json').read_bytes()
    with pytest.raises(ValueError,match='ALREADY_EXISTS'):
        run_claim_with_synthetic_observation(packet,observed,tmp_path)
    assert (tmp_path/'setup/intent.json').read_bytes()==before


def operation(tmp_path, name='seven-zip'):
    request={'source_root':str(tmp_path/'source'),'setup_root':str(tmp_path/'setup'),
        'request_id':transparent.REQUEST_ID,'runtime_fingerprint_sha256':'a'*64,'binding_sha256':'b'*64}
    setup.claim_setup(request)
    return transparent.Operation(request,name,'c'*64,'d'*64), request


def test_command_failure_preserves_original_log_without_printing_it(tmp_path,monkeypatch,capsys):
    op,request=operation(tmp_path)
    def fail(command,**kwargs):
        assert kwargs['stdout'] is kwargs['stderr']
        kwargs['stdout'].write(b'PRIVATE SYNTHETIC FAILURE\n')
        return SimpleNamespace(returncode=17)
    monkeypatch.setattr('subprocess.run',fail)
    with pytest.raises(ValueError,match='COMMAND_FAILED_PRIVATE_LOG_PRESERVED'):
        op.run(['apt-get','-qq','update'],check=True,timeout=180)
    assert capsys.readouterr().out==''
    assert (Path(request['setup_root'])/'seven-zip.console.log').read_bytes()==b'PRIVATE SYNTHETIC FAILURE\n'
    assert not (Path(request['setup_root'])/'seven-zip.operation-result.json').exists()
    with pytest.raises(ValueError,match='LOG_RECONCILE'):
        transparent.Operation(request,'seven-zip','c'*64,'d'*64)


def test_operation_rejects_arbitrary_or_repeated_commands_before_subprocess(tmp_path,monkeypatch):
    op,_=operation(tmp_path);calls=[]
    monkeypatch.setattr('subprocess.run',lambda *a,**kw:calls.append(a) or SimpleNamespace(returncode=0))
    with pytest.raises(ValueError,match='COMMAND_NOT_FIXED'):
        op.run(['sh','-c','anything'])
    assert calls==[]
    op.run(['apt-get','-qq','update'],check=True,timeout=180)
    with pytest.raises(ValueError,match='COMMAND_NOT_FIXED'):
        op.run(['apt-get','-qq','update'],check=True,timeout=180)
    assert len(calls)==1
    with pytest.raises(ValueError,match='SEQUENCE_INCOMPLETE'):op.finish()


@pytest.mark.parametrize('interpreter',[
    '/opt/hostedtoolcache/Python/3.11.16/x64/bin/python',
    '/tmp/python3',
])
def test_dependencies_reject_other_python_domains_before_subprocess(tmp_path,monkeypatch,interpreter):
    monkeypatch.setattr('sys.executable',interpreter)
    op,request=operation(tmp_path,'dependencies');calls=[]
    monkeypatch.setattr('subprocess.run',lambda *a,**kw:calls.append(a))
    command=[interpreter,'-m','pip','install','-q','-r',
        request['source_root']+'/campaigns/isles24-pilot/experiments/P001/requirements.txt']
    with pytest.raises(ValueError,match='TRANSPARENT_SETUP_PYTHON_DOMAIN'):
        op.run(command,check=True,timeout=180)
    assert calls==[] and op.calls==0
    assert (Path(request['setup_root'])/'dependencies.operation-intent.json').exists()
    assert not (Path(request['setup_root'])/'dependencies.operation-result.json').exists()


def test_operation_timeout_has_named_failure_and_preserved_intent(tmp_path,monkeypatch):
    import subprocess
    op,request=operation(tmp_path)
    def timeout(*a,**kw):raise subprocess.TimeoutExpired(a[0],180)
    monkeypatch.setattr(subprocess,'run',timeout)
    with pytest.raises(ValueError,match='COMMAND_TIMEOUT_PRIVATE_LOG_PRESERVED'):
        op.run(['apt-get','-qq','update'])
    assert (Path(request['setup_root'])/'seven-zip.operation-intent.json').exists()
    with pytest.raises(FileExistsError):transparent.Operation(request,'seven-zip','c'*64,'d'*64)


def test_complete_native_results_produce_receipt_bound_to_real_exchange_digest(packet):
    checked=[transparent.validate_stage(packet,i,native(v)) for i,v in enumerate(outcomes(packet))]
    receipt=transparent.final_receipt(packet,checked,'a'*64)
    assert receipt['status']=='SOURCE_DEPENDENCIES_AND_DEFAULT_CHILD_ENVIRONMENT_VERIFIED'
    assert receipt['native_exchange_sha256']=='a'*64 and receipt['patient_launch_authorized'] is False
    assert receipt['request_id']==transparent.REQUEST_ID
    with pytest.raises(ValueError,match='COMPLETE_SEQUENCE'):
        transparent.final_receipt(packet,checked[:-1],'a'*64)
    with pytest.raises(ValueError,match='CHECKED_STAGE_BINDING'):
        transparent.final_receipt(packet,[checked[1],checked[0],*checked[2:]],'a'*64)


@pytest.mark.parametrize('result',[
    {'outputs':[]},
    {'outputs':[{'output_type':'stream','text':['{"incomplete":']}]},
    {'outputs':[{'output_type':'error','ename':'SyntheticError'}]},
    {'outputs':[{'output_type':'stream','text':['X'*8193]}]},
    {'status':'COMPLETE'},
])
def test_missing_truncated_oversized_or_error_results_cannot_advance(packet,result):
    with pytest.raises(ValueError,match='TRANSPARENT_SETUP_'):
        transparent.validate_stage(packet,1,result)


@pytest.mark.parametrize('stage,change',[
    (0,lambda x:x.update(cpu_only=False)),
    (1,lambda x:x.update(binding_sha256='f'*64)),
    (1,lambda x:x.update(exclusive_intent_created=False)),
    (2,lambda x:x.update(source_postcondition_verified=False)),
    (2,lambda x:x['operations'][0].update(returncode=1)),
    (2,lambda x:x['operations'][0].update(command_count=6)),
    (2,lambda x:x['operations'][0].update(source_sha256='f'*64)),
    (3,lambda x:x['environment']['packages'][0].update(import_version='wrong')),
])
def test_per_stage_postconditions_and_child_environment_are_checked(packet,stage,change):
    value=outcomes(packet)[stage];change(value)
    with pytest.raises(ValueError):transparent.validate_stage(packet,stage,native(value))

@pytest.mark.parametrize('seven_zip_exists',[True,False])
def test_generated_operations_execute_frozen_sequence_with_private_logs(packet,inputs,tmp_path,monkeypatch,capsys,seven_zip_exists):
    import subprocess,sys,shutil
    monkeypatch.setattr(sys,'path',list(sys.path))
    # This cell simulates Colab; the CI runner's interpreter is outside its domain.
    monkeypatch.setattr(sys,'executable','/usr/bin/python3')
    request=copy.deepcopy(packet['request'])
    prefix=str(tmp_path/'scout-pilot-')
    request['source_root']=prefix+setup.intake.SOURCE_PIN[:12]
    request['setup_root']=str(tmp_path/'setup')
    setup.claim_setup(request)
    observations=[]
    for present in (False,True):
        observed=copy.deepcopy(inputs[1]['observation'])
        for row in observed['source_files']:
            row['path']=row['path'].replace(setup.SOURCE_ROOT,request['source_root'])
            if present:row.update(state='PRESENT',matches_expected=True)
        observations.append(observed)
    tree=ast.parse(packet['cells'][2]);kept=[]
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name=='runtime_observation':continue
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='request' for t in node.targets):continue
        kept.append(node)
    tree=ast.Module(body=kept,type_ignores=[])
    for node in ast.walk(tree):
        if isinstance(node,ast.Constant) and node.value=='/content/scout-pilot-':node.value=prefix
    calls=[]
    def run(command,**kwargs):
        calls.append(command)
        if command[:3]==['git','init','-q']:Path(command[3]).mkdir()
        if kwargs['stdout']==subprocess.PIPE:
            raw=(setup.intake.SOURCE_PIN+'\n').encode() if command[1]=='rev-parse' else b''
        else:
            kwargs['stdout'].write(b'SYNTHETIC STDOUT\n');kwargs['stderr'].write(b'SYNTHETIC STDERR\n');raw=None
        return SimpleNamespace(returncode=0,stdout=raw)
    monkeypatch.setattr(subprocess,'run',run)
    monkeypatch.setattr(shutil,'which',lambda name:'/usr/bin/7z' if seven_zip_exists else None)
    original_is_file=Path.is_file
    monkeypatch.setattr(Path,'is_file',lambda path:True if str(path)==request['source_root']+'/campaigns/isles24-pilot/experiments/P001/review.json' else original_is_file(path))
    namespace={'request':request,'runtime_observation':lambda value:observations.pop(0)}
    exec(compile(tree,'synthetic-full-operation-cell','exec'),namespace)
    value=json.loads(capsys.readouterr().out)
    assert value['source_postcondition_verified'] is True
    assert [row['command_count'] for row in value['operations']]==[7,1,0 if seven_zip_exists else 2]
    assert len(calls)==8+(0 if seven_zip_exists else 2)
    assert not observations
    assert b'SYNTHETIC STDOUT' in (tmp_path/'setup/acquisition.console.log').read_bytes()
    assert 'SYNTHETIC STDOUT' not in json.dumps(value)


def test_failed_operation_cannot_finish_or_continue(tmp_path,monkeypatch):
    op,_=operation(tmp_path)
    results=iter([0,5])
    monkeypatch.setattr('subprocess.run',lambda *a,**kw:SimpleNamespace(returncode=next(results)))
    op.run(['apt-get','-qq','update'])
    with pytest.raises(ValueError,match='COMMAND_FAILED'):
        op.run(['apt-get','-qq','install','-y','p7zip-full'])
    with pytest.raises(ValueError,match='FAILED_OPERATION_RECONCILE'):op.finish()
    with pytest.raises(ValueError,match='FAILED_OPERATION_RECONCILE'):
        op.run(['apt-get','-qq','install','-y','p7zip-full'])


def test_claim_numeric_boolean_and_changed_request_are_rejected(packet):
    value=outcomes(packet)[1];value['exclusive_intent_created']=1
    with pytest.raises(ValueError,match='CLAIM_RESULT'):transparent.validate_stage(packet,1,native(value))
    changed=copy.deepcopy(packet);changed['request']['source_root']='/different/source'
    with pytest.raises(ValueError,match='REQUEST_BINDING'):
        transparent.validate_stage(changed,0,native(outcomes(packet)[0]))
