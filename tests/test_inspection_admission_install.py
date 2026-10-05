"""Offline integration guards; fixtures are never native review/admission proof."""
import copy
import json
from pathlib import Path

import pytest

from orchestrator import deployment_review as gate
from orchestrator import install_reviewed_deployment as install
from orchestrator import inspection_admission_recovery as ledger
from orchestrator import prepare_deployment_bundle as prep
from test_reviewed_deployment_install import host, SOURCE, SHA, write
from test_deployment_preparation import inputs, run as prepare


def legacy_recovery():
    return {'schema':'reviewed-deployment-recovery/v1','instructions':'Synthetic offline only.',
        'directories':{},'units_before':{},'previous_active':{'state':'ABSENT'},
        'preserved_state_sha256':'a'*64,'preserved_blocked_tasks':{}}


def fake_recovery(monkeypatch):
    # A stub is appropriate at the installer/helper interface. The helper's own
    # tests exercise actual immutable Git objects and the ordinary limiter.
    monkeypatch.setattr(ledger, 'validate_baseline', lambda value, policy=None: value)
    value = legacy_recovery()
    value.update(schema=install.DIRECT_RECOVERY, inspection_admissions={
        'schema':'reviewed-inspection-baseline/v1','ledger':{'synthetic':'unqualified',
            'policy_sha256':'b'*64,'snapshot':{'repository':'/synthetic/ledger','files':{}}},
        'policy_sha256':'b'*64,'canary_proof_sha256':'c'*64,
        'non_ledger_files':{'/synthetic/file':{'uid':0,'gid':0,'mode':384,'inode':1,'sha256':'d'*64}},
        'control_snapshot':{'paused':1,'revision':15,'steering':[]}})
    value['preserved_state_sha256']=install.inventory_fingerprint(value['inspection_admissions']['non_ledger_files'])['sha256']
    return value


def test_legacy_recovery_keeps_exact_key_and_schema_boundary(monkeypatch):
    value = legacy_recovery()
    install.validate_recovery(value, {})
    value['inspection_admissions'] = {}
    with pytest.raises(ValueError, match='REVIEWED_RECOVERY_PLAN_REQUIRED'):
        install.validate_recovery(value, {})


@pytest.mark.parametrize('proposal',[{}, {'review_profile':'unknown'},
    {'review_profile':'direct-inspection/v1','review_plan_sha256':'d'*64}])
def test_direct_recovery_never_changes_legacy_or_composed_profile(monkeypatch, proposal):
    with pytest.raises(ValueError, match='DIRECT_RECOVERY_PROFILE_REQUIRED'):
        install.validate_recovery(fake_recovery(monkeypatch), proposal)


def test_direct_native_preparation_binds_exact_immutable_profile_and_recovery(inputs, monkeypatch):
    f=inputs; recovery=fake_recovery(monkeypatch)
    Path(f['plan']['recovery_file']).write_bytes(gate.encoded(recovery))
    f['plan']['review_profile']='direct-inspection/v1'
    f['plan_file'].write_bytes(gate.encoded(f['plan']))
    result=prepare(f)
    proposal=json.loads((f['destination']/'proposal.json').read_bytes())
    assert proposal['review_profile']==result['review_profile']=='direct-inspection/v1'
    assert 'review_plan_sha256' not in proposal
    assert (f['destination']/'literals'/proposal['recovery_sha256']).read_bytes()==gate.encoded(recovery)
    assert result['review_originals_attached'] is False and result['models_started']==0


@pytest.mark.parametrize('profile, composed',[('unknown',False),('direct-inspection/v1',True)])
def test_preparer_rejects_unknown_or_composed_direct_profile_before_output(inputs, profile, composed):
    f=inputs;f['plan']['review_profile']=profile
    if composed:f['plan']['review_plan_file']='/never-read'
    f['plan_file'].write_bytes(gate.encoded(f['plan']))
    with pytest.raises(ValueError,match='EXPLICIT_REVIEW_PROFILE_REQUIRED'):prepare(f)
    assert not f['destination'].exists()


@pytest.fixture
def transition(tmp_path, monkeypatch):
    controller=tmp_path/'controller';controller.mkdir()
    parent=tmp_path/'broker';parent.mkdir();repo=parent/'ledger';repo.mkdir()
    (parent/'turns').mkdir()
    write(controller/'evidence.txt', b'Original scientific evidence.\n')
    write(repo/'original-object', b'Immutable baseline object.\n')
    write(parent/'notifications.json', b'{"delivered":false}\n')
    broker={'turn_root':str(parent/'turns'),'ledger_repo':str(repo),'policy':{'synthetic':'only'}}
    monkeypatch.setattr(install,'CONTROLLER',controller)
    monkeypatch.setattr(install,'JOBS',tmp_path/'absent-jobs')
    baseline=install.state_inventory(broker)
    control={'revision':15,'paused':1,'steering':[]}
    proof={'inspection_index_sha256':'d'*64}
    canary=b'{"synthetic":"not actual canary proof"}\n'
    admissions=[{'event_original':'{}\n','receipt_original':'{}\n'}]
    recovery=fake_recovery(monkeypatch)
    recovery['preserved_state_sha256']=install.inventory_fingerprint(baseline)['sha256']
    recovery['inspection_admissions'].update(policy_sha256=gate.digest(gate.encoded(broker['policy'])),
        canary_proof_sha256=gate.digest(canary),non_ledger_files=install._non_ledger(baseline,broker),
        control_snapshot=copy.deepcopy(control))
    proposal={'source':SOURCE,'review_profile':'direct-inspection/v1','recovery_sha256':'e'*64}
    events=[]
    monkeypatch.setattr(install,'_inspection_admissions',lambda *args:(proof,admissions,canary))
    monkeypatch.setattr(install,'_inspection_control',lambda:copy.deepcopy(control))
    def status(_):events.append('authenticated-status');return {'pin':'f'*40}
    monkeypatch.setattr(install,'authenticated_ledger_status',status)
    def verify(*args, preserved_admissions_count=0):
        assert preserved_admissions_count == 0
        events.append('verified-ledger')
        return {'schema':ledger.TRANSITION,'status':'VERIFIED',
            'baseline_sha256':gate.digest(gate.encoded(recovery['inspection_admissions']['ledger'])),
            'admissions_sha256':gate.digest(gate.encoded(admissions))}
    monkeypatch.setattr(ledger,'verify_transition',verify)
    inventory=install.state_inventory
    def capture(b):events.append('full-inventory');return inventory(b)
    monkeypatch.setattr(install,'state_inventory',capture)
    return dict(broker=broker,recovery=recovery,proposal=proposal,events=events,repo=repo,
        controller=controller,parent=parent,control=control,admissions=admissions,proof=proof,canary=canary)


def verified(f):
    return install.inspection_preserved_state(Path('/synthetic/bundle'),f['proposal'],f['recovery'],f['broker'])


def test_validated_ledger_suffix_then_full_fingerprint_is_the_only_exception(transition):
    f=transition
    write(f['repo']/'verified-new-object',b'Already validated by the separate ledger helper.\n')
    preserved,proof=verified(f)
    assert preserved['sha256']!=f['recovery']['preserved_state_sha256']
    assert proof['post_review_state']==preserved
    assert proof['original_preserved_state_sha256']==f['recovery']['preserved_state_sha256']
    assert f['events']==['authenticated-status','verified-ledger','full-inventory','full-inventory']


@pytest.mark.parametrize('kind',['notification','science','mode','new-file'])
def test_unrelated_state_is_never_excluded_with_the_ledger(transition, kind):
    f=transition
    if kind=='notification':(f['parent']/'notifications.json').write_text('{"delivered":true}\n')
    elif kind=='science':(f['controller']/'evidence.txt').write_text('Changed evidence.\n')
    elif kind=='mode':(f['controller']/'evidence.txt').chmod(0o777)
    else:write(f['controller']/'new.txt',b'Unexpected state')
    with pytest.raises(ValueError,match='NON_LEDGER_STATE_CHANGED'):verified(f)


def test_helper_rejection_cannot_be_converted_into_fingerprint_allowance(transition, monkeypatch):
    def foreign(*args, preserved_admissions_count=0):
        assert preserved_admissions_count == 0
        raise ValueError('FOREIGN_ADMISSION')
    monkeypatch.setattr(ledger,'verify_transition',foreign)
    with pytest.raises(ValueError,match='FOREIGN_ADMISSION'):verified(transition)
    assert transition['events']==['authenticated-status']


def test_new_pause_or_steering_refuses_before_remote_status(transition):
    transition['control']['revision']+=1
    with pytest.raises(ValueError,match='INSPECTION_CONTROL_CHANGED'):verified(transition)
    assert transition['events']==[]


@pytest.mark.parametrize('field',['policy_sha256','canary_proof_sha256'])
def test_policy_and_actual_canary_binding_cannot_move(transition, field):
    transition['recovery']['inspection_admissions'][field]='0'*64
    with pytest.raises(ValueError,match='(POLICY_CHANGED|CANARIES_CHANGED)'):verified(transition)
    assert transition['events']==[]


def test_changed_full_capture_refuses_even_after_validated_suffix(transition, monkeypatch):
    monkeypatch.setattr(install,'state_fingerprint',lambda broker:{'sha256':'0'*64,'files':0})
    with pytest.raises(ValueError,match='STATE_CHANGED_DURING_TRANSITION'):verified(transition)


def test_restore_intent_binds_original_review_and_exact_post_review_state(transition):
    f=transition;preserved,proof=verified(f)
    intent={'preserved_state':preserved,'inspection_admission_transition':proof}
    install.validate_inspection_intent(Path('/synthetic/bundle'),f['proposal'],f['recovery'],intent)
    for field in ('original_preserved_state_sha256','recovery_sha256','admissions_sha256','canary_proof_sha256'):
        changed=copy.deepcopy(intent);changed['inspection_admission_transition'][field]='0'*64
        with pytest.raises(ValueError,match='ORIGINAL_ADMISSION_TRANSITION_CHANGED'):
            install.validate_inspection_intent(Path('/synthetic/bundle'),f['proposal'],f['recovery'],changed)


def direct_host(f, monkeypatch):
    f['proposal']['review_profile']='direct-inspection/v1'
    f['recovery']['schema']=install.DIRECT_RECOVERY
    f['state']['sha256']='e'*64
    post=copy.deepcopy(f['state'])
    transition={'synthetic':'already validated adapter','post_review_state':post,
        'original_preserved_state_sha256':f['recovery']['preserved_state_sha256']}
    monkeypatch.setattr(install,'inspection_preserved_state',lambda *args:(post,transition))
    monkeypatch.setattr(install,'validate_inspection_intent',lambda *args:None)
    return transition


def test_install_and_restore_keep_actual_post_review_fingerprint(host, monkeypatch):
    f=host;transition=direct_host(f,monkeypatch)
    receipt=install.apply(SHA,SOURCE)
    intent=json.loads((f['bundle']/'upgrade-intent.json').read_bytes())
    assert intent['preserved_state']==receipt['preserved_state']==f['state']
    assert intent['preserved_state']['sha256']!=f['recovery']['preserved_state_sha256']
    assert intent['inspection_admission_transition']==receipt['inspection_admission_transition']==transition
    restored=install.restore(SHA,SOURCE)
    assert restored['preserved_state']==f['state']


def test_new_admission_after_install_blocks_restore_without_fetch_or_replay(host, monkeypatch):
    f=host;direct_host(f,monkeypatch);install.apply(SHA,SOURCE)
    def forbidden(*args):raise AssertionError('Restore must never rebase or fetch the ledger')
    monkeypatch.setattr(install,'inspection_preserved_state',forbidden)
    f['state']['sha256']='f'*64
    with pytest.raises(ValueError,match='RESULTS_CHANGED_RESTORE_REFUSED'):install.restore(SHA,SOURCE)
    assert not (f['bundle']/'restore-intent.json').exists()


def test_direct_state_change_before_mutation_still_preserves_failure(host, monkeypatch):
    f=host;direct_host(f,monkeypatch)
    def stop():f['events'].append('stop-broker');f['state']['sha256']='f'*64
    monkeypatch.setattr(install,'stop_broker',stop)
    with pytest.raises(ValueError,match='STATE_CHANGED_BEFORE_MUTATION'):install.apply(SHA,SOURCE)
    assert f['target'].read_bytes()==b'old'
    assert (f['bundle']/'upgrade-failure.json').exists()
    assert not (f['bundle']/'upgrade-receipt.json').exists()


def test_reviewed_full_baseline_must_equal_exact_ledger_and_nonledger_union(monkeypatch):
    recovery=fake_recovery(monkeypatch)
    install.validate_recovery(recovery, {'review_profile':'direct-inspection/v1'})
    recovery['preserved_state_sha256']='0'*64
    with pytest.raises(ValueError,match='ORIGINAL_FULL_BASELINE_CHANGED'):
        install.validate_recovery(recovery, {'review_profile':'direct-inspection/v1'})


def test_nonledger_map_cannot_hide_a_second_copy_inside_ledger(monkeypatch):
    recovery=fake_recovery(monkeypatch)
    files=recovery['inspection_admissions']['non_ledger_files']
    files['/synthetic/ledger/hidden']=next(iter(files.values()))
    with pytest.raises(ValueError,match='INSPECTION_LEDGER_OVERLAP'):
        install.validate_recovery(recovery, {'review_profile':'direct-inspection/v1'})
