"""Actual approved-package builder and resume consumer, synthetic evidence only.

The inherited fixture has clearly labelled synthetic model/native evidence.
No bridge, scientific seal, continuation or database operation is patched.
"""
import json
from copy import deepcopy
from types import SimpleNamespace as NS
import pytest
from orchestrator import experiment_modal_package as bridge, experiment_package as package
from orchestrator import experiment_projection as projection, experiment_continuation as continuation
from orchestrator import private_records as pr, modal_item4_budget as budget
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import digest,inventory
from orchestrator.modal_executor import canonical,item4_job
from orchestrator.modal_fit_progress import encoded
from orchestrator.modal_item4_policy import AUTHORITY,TEAM_AUTHORITY
from test_experiment_approval import reviewed
from test_experiment_context import experiment,root


@pytest.fixture
def native_resume(reviewed):
    d,v,_=reviewed
    assert d.config['item_number']==4
    Driver._accept_completed(d,v);package.emit(d,v)
    base={'purpose':'M4_ITEM4','run_id':d.config['run_id'],'source':d.config['source'],
        'experiment':{'backlog_item':4,'authority_sha256':AUTHORITY,'team_authority_sha256':TEAM_AUTHORITY,
            'fit_id':'fit-one','stage':'SMOKE','segment':1,'billing_object_id':'ap-synthetic'}}
    job={'job':item4_job(base),'binding':base,'runtime':{'synthetic':True}}
    folder=d.state/'fit-packages'/job['job']/'prepared';pr.mkdir(folder.parent,parents=True)
    manifest=bridge.emit(d,v,folder,base);binding=manifest['binding'];ident=digest(canonical(binding))
    from orchestrator.modal_budget import ComputeAccounts
    ComputeAccounts(d.store.batch)
    db=d.store.batch.db
    db.execute("INSERT INTO autonomy_compute(id,run,binding,status,reserved_micro_usd,provider_id,actual_micro_usd,month) VALUES(?,?,?,'RUNNING',1000,'sb-synthetic',NULL,'2026-10')",
        (ident,d.config['run_id'],canonical(binding).decode()))
    reason=d.state/'synthetic-cause.json'
    pr.write_bytes(reason,canonical({'schema':'modal-interruption-cause/v1','segment_id':ident,
        'provider_id':'sb-synthetic','reason':'DELIBERATE_SMOKE_INTERRUPTION',
        'evidence':{'synthetic_fixture_only':True}}))
    checkpoint={'synthetic_fixture_only':True,'metadata':{'next_epoch':1}}
    proof={'schema':'modal-fit-terminal-proof/v1','provider_id':'sb-synthetic',
        'binding_sha256':ident,'fit_id':'fit-one','terminal_exit_code':137,'may_launch':False,
        'checkpoint_record':checkpoint,'checkpoint_record_sha256':digest(encoded(checkpoint))}
    budget.record_interruption(NS(db=db),ident,NS(terminal_fit_checkpoint=lambda *a:proof),reason_record=reason)
    terminal=continuation.terminal(d,v,job)
    successor=continuation.successor(job,terminal)
    second=d.state/'fit-packages'/successor['job']/'prepared';pr.mkdir(second.parent,parents=True)
    bridge.emit(d,v,second,successor['binding'])
    return d,v,job,successor,manifest


@pytest.mark.parametrize('reviewed',[4],indirect=True)
def test_native_package_resume_replay_preserves_originals_and_charges(native_resume):
    d,v,old,new,manifest=native_resume
    before=inventory(d.state/'fit-packages')
    rows=[tuple(r) for r in d.store.batch.db.execute('SELECT * FROM autonomy_compute')]
    result=projection.resume_evidence(d,v,new)
    assert result[0]['epoch_resumed_from']==1
    assert projection.resume_evidence(d,v,new)==result
    assert inventory(d.state/'fit-packages')==before
    assert [tuple(r) for r in d.store.batch.db.execute('SELECT * FROM autonomy_compute')]==rows
    assert d.store.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==1 # synthetic spec fixture only
    # This was the producer/consumer defect: emit must still reject a full binding.
    with pytest.raises(ValueError,match='^EXPERIMENT_MODAL_DERIVED_BINDING_FIELDS$'):
        bridge.emit(d,v,d.state/'must-not-create',manifest['binding'])
    assert not (d.state/'must-not-create').exists()


@pytest.mark.parametrize('reviewed',[4],indirect=True)
@pytest.mark.parametrize('damage',['old-code','new-code','old-missing','new-missing','review','resume-link'])
def test_native_resume_rejects_changed_binding_or_missing_original(native_resume,damage):
    d,v,old,new,manifest=native_resume
    folder=d.state/'fit-packages'/(old if damage.startswith('old') else new)['job']/'prepared'
    if damage.endswith('missing'):
        folder.rename(folder.with_name('preserved-test-original'))
    elif damage=='review':pr.write_bytes(d.state/'experiment-package/review.json',b'{}')
    else:
        path=folder/'manifest.json';data=json.loads(path.read_bytes())
        if damage=='resume-link':data['binding']['resume']['checkpoint_record_sha256']='f'*64
        else:data['binding']['execution']['module_sha256']='f'*64
        pr.write_bytes(path,canonical(data))
    before=inventory(d.state/'fit-packages')
    with pytest.raises((ValueError,FileNotFoundError)):projection.resume_evidence(d,v,new)
    assert inventory(d.state/'fit-packages')==before


@pytest.mark.parametrize('reviewed',[4],indirect=True)
def test_readonly_replay_never_creates_missing_package(native_resume):
    d,v,_,_,manifest=native_resume
    path=d.state/'absent-package'
    with pytest.raises(ValueError,match='^EXPERIMENT_REPLAY_PACKAGE_REQUIRED$'):
        bridge.replay(d,v,path,manifest['binding'])
    assert not path.exists()
