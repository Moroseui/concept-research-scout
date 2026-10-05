"""Synthetic offline preparation fixtures; no installed or provider proof is claimed."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile

import pytest

from orchestrator import change_requests as changes
from orchestrator import deployment_review as gate
from orchestrator import prepare_deployment_bundle as prep

ACTOR = {'kind':'agent', 'family':'codex', 'model':'synthetic-test', 'session_id':'offline-fixture'}


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return path


def archived(files, path):
    with tarfile.open(path, 'w:gz') as archive:
        for name, raw in files.items():
            member = tarfile.TarInfo('snapshot/'+name); member.size=len(raw)
            archive.addfile(member, io.BytesIO(raw))


@pytest.fixture
def inputs(tmp_path):
    root=tmp_path/'repo';root.mkdir()
    direction=b'Synthetic direction for offline package checks.\n'
    policy=gate.encoded({'direction_path':'docs/direction.md','direction_sha256':gate.digest(direction)})
    operating=gate.encoded({'authority_policy':{'path':'configs/authority.json','sha256':gate.digest(policy)},
                            'documents':{'docs/direction.md':gate.digest(direction)}})
    files={'docs/direction.md':direction,'configs/authority.json':policy,
        'configs/scientific-operating-context.json':operating,
        'scripts/pilot_review.py':b'# synthetic courier fixture\n',
        'orchestrator/deployment_review.py':b'# synthetic verifier fixture\n',
        'orchestrator/prepare_deployment_bundle.py':b'# synthetic preparer fixture\n'}
    files.update({'orchestrator/a_nested/first.py': b'# Synthetic first nested source.\n',
                  'orchestrator/a_nested/second.py': b'# Synthetic repeated parent.\n',
                  'scripts/nested/probe.py': b'# Synthetic separate parent.\n'})
    for name,raw in files.items():write(root/name,raw)
    subprocess.run(['git','init','-q',str(root)],check=True)
    subprocess.run(['git','add','.'],cwd=root,check=True)
    subprocess.run(['git','-c','user.name=Offline Fixture','-c','user.email=fixture@example.invalid',
                    'commit','-qm','Synthetic source'],cwd=root,check=True)
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    archive=tmp_path/'snapshot.tar.gz';archived(files,archive)
    request=changes.submit(tmp_path/'changes',root,'system:deployment','Prepare exact source for offline test.',
        ACTOR,source=source,key='prepare',scope_limits=['No host operations or review claims.'])
    folder=tmp_path/'changes'/request['identity']
    changes.record(folder,'AUTHORIZED',ACTOR,{'authority_reference':'Synthetic offline fixture',
        'rationale':'Fixture only','review_policy':'Pending actual review'})
    applied=changes.record(folder,'APPLIED',ACTOR,{'modification':'Synthetic source prepared',
        'checks':'Synthetic fixture','result_binding':{'source':source},'review_status':'PENDING'})
    dependencies={name:{'path':path,'resolved':'/synthetic/'+name,'sha256':'a'*64,
                          'bytes':100,'uid':0,'gid':0,'mode':0o755}
                  for name,path in gate.DEPENDENCY_PATHS.items()}
    dep=write(tmp_path/'dependencies.json',gate.encoded(dependencies))
    recovery=write(tmp_path/'recovery.txt',b'Preserve originals; no automatic retry or invented success.\n')
    target_root='/opt/research-system/releases/'+source+'-research-handover/snapshot'
    target_json=write(tmp_path/'target.json',gate.encoded({'source':source,'source_root':target_root}))
    broker_json=write(tmp_path/'broker.json',gate.encoded({'sources':[source]}))
    unit=write(tmp_path/'unit.txt',b'# Synthetic unit bytes; never executed.\n')
    old=write(tmp_path/'previous.json',b'{"source":"synthetic-previous-observation"}\n')
    plan={'schema':prep.SCHEMA,'source':source,'source_root':target_root,
          'previous_source':'b'*40,'previous_source_root':'/opt/research-system/previous/snapshot',
          'targets':{name:{'file':str(broker_json if name.endswith('/broker.json') else target_json if name.endswith('.json') else unit),
                           'uid':0,'gid':0,'mode':0o600 if name.endswith('.json') else 0o644}
                     for name in gate.REQUIRED_TARGETS},
          'previous_files':{'/etc/research-system/live-research/broker.json':
                            {'file':str(old),'uid':0,'gid':0,'mode':0o600}},
          'dependencies_file':str(dep),'recovery_file':str(recovery),
          'changes':[{'folder':str(folder),'applied':applied['identity']}]}
    plan_file=write(tmp_path/'plan.json',gate.encoded(plan))
    return {'root':root,'source':source,'archive':archive,'files':files,'plan':plan,
            'plan_file':plan_file,'destination':tmp_path/'prepared','change_folder':folder,
            'applied':applied,'target_json':target_json}


def run(f):
    return prep.prepare(f['root'],f['source'],f['archive'],f['plan_file'],f['destination'])


def test_exact_private_preparation_preserves_unreviewed_originals(inputs):
    f=inputs;manifest=run(f);out=f['destination']
    assert manifest['status']=='PREPARED_NOT_REVIEWED_NOT_INSTALLED'
    assert manifest['models_started']==0 and manifest['host_observations_verified'] is False
    assert not any((out/name).exists() for name in ['request.json','response.json','execution.json',
                                                 'install-intent.json','install-receipt.json','active.json'])
    for name,sha in manifest['file_sha256'].items():
        assert gate.digest((out/name).read_bytes())==sha
    assert (out/'source.tar.gz').read_bytes()==f['archive'].read_bytes()
    proposal=json.loads((out/'proposal.json').read_bytes())
    assert set(proposal['targets'])==gate.REQUIRED_TARGETS
    assert json.loads((out/'change-bindings.json').read_bytes()) == changes.review_bindings(
        f['source'], gate.digest((out/'proposal.json').read_bytes()), proposal['changes'])
    assert 'change-bindings.json' in manifest['courier_private_files']
    assert manifest['courier_change_bindings'] == 'change-bindings.json'
    copied=changes.load(out/'change-inputs'/f['change_folder'].name)
    assert copied['events'][-1]==f['applied']
    assert copied['events'][-1]['payload']['review_status']=='PENDING'
    assert out.stat().st_mode & 0o777==0o700
    with pytest.raises(ValueError,match='FRESH_EXTERNAL_PREPARATION_REQUIRED'):run(f)


@pytest.mark.parametrize('defect',['archive','missing_target','extra_target','source_config','dependency','mode'])
def test_material_input_mismatch_refuses_before_output(inputs,defect):
    f=inputs
    if defect=='archive':archived({**f['files'],'scripts/pilot_review.py':b'# changed\n'},f['archive'])
    elif defect=='missing_target':f['plan']['targets'].pop(next(iter(gate.REQUIRED_TARGETS)))
    elif defect=='extra_target':f['plan']['targets']['/etc/unrelated.json']=next(iter(f['plan']['targets'].values()))
    elif defect=='source_config':f['target_json'].write_bytes(gate.encoded({'source':'c'*40}))
    elif defect=='dependency':Path(f['plan']['dependencies_file']).write_bytes(b'{}')
    else:next(iter(f['plan']['targets'].values()))['mode']=0o666
    f['plan_file'].write_bytes(gate.encoded(f['plan']))
    with pytest.raises(ValueError):run(f)
    assert not f['destination'].exists()


def test_changed_original_change_chain_refuses(inputs):
    f=inputs;event=next((f['change_folder']/'events').glob('*'+f['applied']['identity']+'.json'))
    value=json.loads(event.read_bytes());value['payload']['modification']='changed';event.write_bytes(gate.encoded(value))
    with pytest.raises(ValueError,match='CHANGE_EVENT_CHAIN_INVALID'):run(f)
    assert not f['destination'].exists()


def test_actual_negative_cannot_be_packaged_as_pending(inputs):
    f=inputs
    changes.record(f['change_folder'],'REVIEW',ACTOR,{'applied_event':f['applied']['identity'],
        'verdict':'REQUEST_CHANGES','rationale':'Synthetic negative remains blocking',
        'review_evidence':'Offline fixture','affected_results':'No result used'})
    with pytest.raises(ValueError,match='APPLICATION_REQUIRES_CORRECTION'):run(f)
    assert not f['destination'].exists()


def test_symlink_input_and_root_operation_refuse(inputs,monkeypatch):
    f=inputs;link=f['root'].parent/'linked-plan.json';link.symlink_to(f['plan_file'])
    f['plan_file']=link
    with pytest.raises(ValueError,match='REGULAR_INPUT_REQUIRED'):run(f)
    monkeypatch.setattr(prep.os,'getuid',lambda:0)
    with pytest.raises(ValueError,match='UNPRIVILEGED_PREPARATION_REQUIRED'):run(f)
    assert not f['destination'].exists()


def test_actual_broker_sources_list_must_include_proposed_source(inputs):
    f=inputs;path=Path(f['plan']['targets']['/etc/research-system/live-research/broker.json']['file'])
    path.write_bytes(gate.encoded({'sources':['c'*40]}))
    with pytest.raises(ValueError,match='CONFIGURATION_SOURCE_CHANGED'):run(f)
    assert not f['destination'].exists()


def test_nested_change_evidence_survives_preparation_with_original_chain(inputs):
    f = inputs
    patch = changes.preserve(f['change_folder'], write(f['root'].parent/'patch.txt', b'Original proposed and applied difference.\n'))
    check = changes.preserve(f['change_folder'], write(f['root'].parent/'check.txt', b'Original observed check.\n'))
    applied = changes.record(f['change_folder'], 'APPLIED', ACTOR, {
        'modification': {'patch': patch}, 'checks': [{'original': check}],
        'result_binding': {'source': f['source'], 'input': patch},
        'supersedes_applied_events': [f['applied']['identity']], 'review_status': 'PENDING'})
    f['plan']['changes'][0]['applied'] = applied['identity']
    f['plan_file'].write_bytes(gate.encoded(f['plan']))
    original = changes.load(f['change_folder'])
    manifest = run(f)
    copied_folder = f['destination']/'change-inputs'/f['change_folder'].name
    assert changes.load(copied_folder) == original
    for ref in (patch, check):
        assert (copied_folder/ref['artifact']).read_bytes() == (f['change_folder']/ref['artifact']).read_bytes()
        assert manifest['file_sha256']['change-inputs/'+f['change_folder'].name+'/'+ref['artifact']] == ref['sha256']
    assert not (f['destination']/'install-receipt.json').exists()


def test_large_chain_preparation_keeps_originals_and_selected_pending_event(inputs):
    f = inputs
    for n in range(12):
        changes.record(f['change_folder'], 'DISPOSITION', ACTOR, {
            'rationale': str(n)+' Preserved original preparation history. '*100,
            'affected_results': 'No actual result.'})
    original = changes.load(f['change_folder'])
    run(f)
    sidecar = json.loads((f['destination']/'change-bindings.json').read_bytes())
    projection = changes.review_context(f['destination']/'change-inputs', sidecar['changes'], source=f['source'])
    assert projection['projection']['kind'] == 'BOUNDED_SUMMARY'
    assert projection['selected_applications'][0]['event'] == f['applied']
    assert projection['requests'][0]['review_status'] == 'PENDING'
    assert changes.load(f['destination']/'change-inputs'/f['change_folder'].name) == original


def test_legacy_binding_shape_has_readable_refusal_before_preparation(inputs):
    f = inputs
    applied = changes.record(f['change_folder'], 'APPLIED', ACTOR, {
        'modification': 'Synthetic old string binding', 'checks': 'Offline only',
        'result_binding': f['source'], 'review_status': 'PENDING',
        'supersedes_applied_events': [f['applied']['identity']]})
    f['plan']['changes'][0]['applied'] = applied['identity']
    f['plan_file'].write_bytes(gate.encoded(f['plan']))
    with pytest.raises(ValueError, match='PREPARATION_EXACT_APPLIED_SOURCE_REQUIRED'): run(f)
    assert not f['destination'].exists()


def test_cli_default_umask_completes_nested_package_with_private_parents(inputs):
    f = inputs
    result = subprocess.run([sys.executable, '-B', '-m', 'orchestrator.prepare_deployment_bundle',
        '--root', str(f['root']), '--source', f['source'], '--archive', str(f['archive']),
        '--plan', str(f['plan_file']), '--destination', str(f['destination'])],
        cwd=Path(prep.__file__).resolve().parents[1], capture_output=True, text=True, umask=0o022)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['status'] == 'PREPARED_NOT_REVIEWED_NOT_INSTALLED'
    out = f['destination']
    manifest = json.loads((out/'preparation.json').read_bytes())
    for name, sha in manifest['file_sha256'].items():
        assert gate.digest((out/name).read_bytes()) == sha
    for name in ('orchestrator/a_nested/first.py', 'orchestrator/a_nested/second.py',
                 'orchestrator/deployment_review.py', 'scripts/nested/probe.py',
                 'scripts/pilot_review.py'):
        assert (out/'review-source'/name).read_bytes() == f['files'][name]
    assert changes.load(out/'change-inputs'/f['change_folder'].name) == changes.load(f['change_folder'])
    for path in (out, *out.rglob('*')):
        assert not path.is_symlink()
        assert path.stat().st_mode & 0o777 == (0o700 if path.is_dir() else 0o600)


def planned_inputs(f):
    """Extend an ordinary synthetic clean checkout to the exact new named profile."""
    for name in (gate.INTEGRATION_FILES | gate.PART_COMMON_FILES | gate.REQUIRED_TEMPLATES) - gate.REFERENCE_ONLY_FILES:
        f['files'].setdefault(name, ('# Synthetic '+name+'\n').encode())
    references = {name: ('# Synthetic reference only '+name+'\n').encode() for name in gate.REFERENCE_ONLY_FILES}
    for name, raw in {**f['files'], **references}.items(): write(f['root']/name, raw)
    subprocess.run(['git', 'add', '.'], cwd=f['root'], check=True)
    subprocess.run(['git', '-c', 'user.name=Offline Fixture', '-c', 'user.email=fixture@example.invalid',
                    'commit', '-qm', 'Synthetic full component profile'], cwd=f['root'], check=True)
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=f['root'], text=True).strip()
    f['source'] = source; f['plan']['source'] = source
    for path in {Path(value['file']) for name, value in f['plan']['targets'].items() if name.endswith('.json')}:
        value = json.loads(path.read_bytes())
        if 'source' in value: value['source'] = source
        if 'sources' in value: value['sources'] = [source]
        path.write_bytes(gate.encoded(value))
    applied = changes.record(f['change_folder'], 'APPLIED', ACTOR, {
        'modification': 'Synthetic planned source version', 'checks': 'Offline fixture',
        'result_binding': {'source': source}, 'supersedes_applied_events': [f['applied']['identity']],
        'review_status': 'PENDING'})
    f['plan']['changes'][0]['applied'] = applied['identity']
    archived(f['files'], f['archive'])
    required, policy = gate.coverage_requirements(f['files'])
    ref_map = {name: gate.digest(raw) for name, raw in references.items()}
    known = {**{name: gate.digest(raw) for name, raw in f['files'].items()}, **ref_map}
    review_plan = {'schema': gate.COVERAGE_SCHEMA, 'source': source,
        'archive_sha256': gate.digest(f['archive'].read_bytes()), 'shared_context_sha256': 'c'*64,
        'required_files': required, 'reference_files': ref_map,
        'parts': {'a': known, 'b': {name: known[name] for name in gate.PART_COMMON_FILES | policy}},
        'integration': {name: known[name] for name in gate.INTEGRATION_FILES | policy},
        'shared_evidence_sha256': [gate.digest(b'Synthetic preserved criticism')]}
    f['review_plan'] = review_plan
    f['review_plan_file'] = write(f['root'].parent/'review-plan.json', gate.encoded(review_plan))
    f['plan']['review_plan_file'] = str(f['review_plan_file'])
    f['plan_file'].write_bytes(gate.encoded(f['plan']))
    return f


def test_planned_package_freezes_names_and_keeps_reference_files_outside_archive(inputs):
    f = planned_inputs(inputs); result = run(f)
    proposal = json.loads((f['destination']/'proposal.json').read_bytes())
    assert proposal['review_plan_sha256'] == gate.digest(f['review_plan_file'].read_bytes())
    assert result['reference_only_file_sha256'] == f['review_plan']['reference_files']
    assert not set(result['reference_only_file_sha256']) & set(proposal['source_files'])
    assert gate.REQUIRED_TEMPLATES <= set(result['courier_source_file_sha256'])
    for part in [*gate.PART_SCOPES, 'integration']:
        actual = json.loads((f['destination']/result['courier_review_file_manifests'][part]).read_bytes())
        expected = f['review_plan']['integration'] if part == 'integration' else f['review_plan']['parts'][part]
        assert actual == expected
    assert changes.load(f['change_folder'])['head_sha256'] == result['change_heads_at_preparation'][f['change_folder'].name]


def test_reference_only_bytes_checked_at_same_clean_source(inputs):
    f = planned_inputs(inputs)
    name = sorted(gate.REFERENCE_ONLY_FILES)[0]
    f['review_plan']['reference_files'][name] = 'f'*64
    for mapping in [*f['review_plan']['parts'].values(), f['review_plan']['integration']]:
        if name in mapping: mapping[name] = 'f'*64
    f['review_plan_file'].write_bytes(gate.encoded(f['review_plan']))
    with pytest.raises(ValueError, match='REFERENCE_SOURCE_CHANGED'): run(f)
    assert not f['destination'].exists()


def test_component_assembly_preserves_originals_and_private_parents(tmp_path, monkeypatch):
    from test_deployment_review import composition_fixture
    f = composition_fixture(tmp_path, monkeypatch)
    # The synthetic provider directory has the same private ownership as courier output.
    for directory in [f['bundle']/'component-reviews'/part for part in gate.PART_SCOPES]:
        directory.chmod(0o700)
    before = {p.relative_to(f['bundle']).as_posix(): p.read_bytes() for p in f['bundle'].rglob('*') if p.is_file()}
    destination = tmp_path/'assembled'
    old = os.umask(0o022)
    try:
        assert prep.main(['--assemble-components', '--bundle', str(f['bundle']),
            '--part-a', str(f['bundle']/'component-reviews/a'),
            '--part-b', str(f['bundle']/'component-reviews/b'), '--destination', str(destination)]) == 0
        receipt = json.loads((destination/'component-preparation.json').read_bytes())
    finally: os.umask(old)
    assert receipt['models_started'] == 0 and not receipt['install_receipt_created']
    for part in gate.PART_SCOPES:
        for name in gate.ORIGINAL_NAMES:
            assert (destination/'component-reviews'/part/name).read_bytes() == f['components'][part][name]
    for path in [destination, *destination.rglob('*')]:
        assert path.stat().st_mode & 0o777 == (0o700 if path.is_dir() else 0o600)
    assert before == {p.relative_to(f['bundle']).as_posix(): p.read_bytes() for p in f['bundle'].rglob('*') if p.is_file()}
    with pytest.raises(ValueError, match='FRESH_EXTERNAL'):
        prep.assemble_components(f['bundle'], f['bundle']/'component-reviews/a',
                                 f['bundle']/'component-reviews/b', destination)


@pytest.mark.parametrize('defect', ['negative', 'oversized', 'symlink'])
def test_component_assembly_refuses_without_creating_output(tmp_path, monkeypatch, defect):
    from test_deployment_review import composition_fixture, bind_component_protocol
    f = composition_fixture(tmp_path, monkeypatch)
    for directory in [f['bundle']/'component-reviews'/part for part in gate.PART_SCOPES]:
        directory.chmod(0o700)
    folder = f['bundle']/'component-reviews/b'
    if defect == 'negative':
        raw = dict(f['components']['b']); response = json.loads(raw['response.json'])
        response['structured_output']['verdict'] = 'REQUEST_CHANGES'
        raw['response.json'] = gate.encoded(response)
        for name, value in bind_component_protocol(raw).items(): (folder/name).write_bytes(value)
    elif defect == 'oversized': (folder/'request.json').write_bytes(b'x'*4000001)
    else:
        original = folder/'request.json'; copy = folder/'original-request.json'
        original.rename(copy); original.symlink_to(copy)
    destination = tmp_path/'refused'
    with pytest.raises(ValueError):
        prep.assemble_components(f['bundle'], f['bundle']/'component-reviews/a', folder, destination)
    assert not destination.exists()

def add_existing_lock_profile(f, *, defect=None):
    name=gate.REGISTRATION_LOCK_TARGET
    raw=b'changed' if defect=='content' else b''
    path=write(f['root'].parent/'existing-registration.lock',raw)
    meta={'file':str(path),'uid':0,'gid':987,'mode':0o600}
    f['plan']['targets'][name]=dict(meta);f['plan']['previous_files'][name]=dict(meta)
    controller=gate.encoded({'source':f['source'],'source_root':f['plan']['source_root'],'controller_gid':987})
    current=write(f['root'].parent/'controller-with-lock.json',controller)
    f['plan']['targets']['/etc/research-system/live-research/controller.json']['file']=str(current)
    if defect=='missing_previous':del f['plan']['previous_files'][name]
    elif defect=='gid':f['plan']['targets'][name]['gid']=986
    elif defect=='mode':f['plan']['targets'][name]['mode']=0o640
    elif defect=='extra':f['plan']['targets']['/etc/research-system/unreviewed.lock']=dict(meta)
    write(f['plan_file'],gate.encoded(f['plan']))
    return path


def test_prepare_current_sixteen_target_profile_binds_existing_empty_lock(inputs):
    f=inputs;lock=add_existing_lock_profile(f);before=lock.stat().st_ino
    run(f)
    proposal=json.loads((f['destination']/'proposal.json').read_bytes())
    current=proposal['targets'][gate.REGISTRATION_LOCK_TARGET]
    assert len(proposal['targets'])==16
    assert current==proposal['previous_files'][gate.REGISTRATION_LOCK_TARGET]
    assert current=={'sha256':gate.digest(b''),'uid':0,'gid':987,'mode':0o600}
    assert (f['destination']/'literals'/current['sha256']).read_bytes()==b''
    assert lock.stat().st_ino==before and lock.read_bytes()==b''
    assert not (f['destination']/'install-intent.json').exists()


@pytest.mark.parametrize('defect',['content','missing_previous','gid','mode','extra'])
def test_prepare_does_not_grant_other_lock_content_access_or_targets(inputs,defect):
    f=inputs;add_existing_lock_profile(f,defect=defect)
    with pytest.raises(ValueError,match='PREPARATION_(UNCHANGED_REGISTRATION_LOCK|EXACT_COMPONENT_PROFILE)_REQUIRED'):
        run(f)
    assert not (f['destination']/'preparation-receipt.json').exists()



def recovery_literal_with_size(size):
    """Valid strict recovery JSON; synthetic bulk only, never a host baseline."""
    from orchestrator.install_reviewed_deployment import validate_recovery
    value = {'schema':'reviewed-deployment-recovery/v1', 'instructions':'',
        'directories':{}, 'units_before':{}, 'previous_active':{'state':'ABSENT'},
        'preserved_state_sha256':'d'*64, 'preserved_blocked_tasks':{}}
    value['instructions'] = 'x' * (size - len(gate.encoded(value)))
    raw = gate.encoded(value)
    assert len(raw) == size
    validate_recovery(json.loads(raw), {})
    return raw


@pytest.mark.parametrize('size', [2000001, 4000000])
def test_recovery_only_accepts_existing_verifier_bound_and_preserves_bytes(inputs, size):
    from orchestrator.install_reviewed_deployment import validate_recovery
    raw = recovery_literal_with_size(size)
    Path(inputs['plan']['recovery_file']).write_bytes(raw)
    manifest = run(inputs)
    proposal = json.loads((inputs['destination']/'proposal.json').read_bytes())
    assert proposal['recovery_sha256'] == gate.digest(raw)
    assert (inputs['destination']/'literals'/gate.digest(raw)).read_bytes() == raw
    validate_recovery(json.loads(raw), proposal)
    assert manifest['models_started'] == 0 and not manifest['install_receipt_created']


def test_recovery_above_four_million_refuses_before_any_output(inputs):
    Path(inputs['plan']['recovery_file']).write_bytes(recovery_literal_with_size(4000001))
    with pytest.raises(ValueError, match='PREPARATION_BOUNDED_INPUT_REQUIRED'):
        run(inputs)
    assert not inputs['destination'].exists()


@pytest.mark.parametrize('role', ['plan', 'dependencies', 'target'])
def test_other_preparation_inputs_keep_two_million_bound(inputs, role):
    path = (inputs['plan_file'] if role == 'plan' else
        Path(inputs['plan']['dependencies_file']) if role == 'dependencies' else inputs['target_json'])
    original = path.read_bytes()
    path.write_bytes(original + b' ' * (2000001-len(original)))
    with pytest.raises(ValueError, match='PREPARATION_BOUNDED_INPUT_REQUIRED'):
        run(inputs)
    assert not inputs['destination'].exists()


def test_local_read_default_boundary_stays_two_million(tmp_path):
    path = tmp_path/'ordinary.json'
    path.write_bytes(b' ' * 2000000)
    assert len(prep.local_read(path)) == 2000000
    path.write_bytes(b' ' * 2000001)
    with pytest.raises(ValueError, match='PREPARATION_BOUNDED_INPUT_REQUIRED'):
        prep.local_read(path)
