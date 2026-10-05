"""Deterministic fake-provider checks; these never authenticate or run a GPU."""
import json
import os
from pathlib import Path
import pytest
from orchestrator import private_records, connectivity
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_budget import ComputeAccounts, estimate, WORKSPACE_CAP
from orchestrator.modal_executor import ModalExecutor, canonical, verify_package
from orchestrator.manual_executor import digest, inventory


@pytest.fixture(autouse=True)
def private_test_environment(monkeypatch):
    old=os.umask(0o077)
    monkeypatch.setattr(connectivity,'require',lambda *a,**kw:{'status':'SYNTHETIC_CONNECTED'})
    yield
    os.umask(old)


class Provider:
    def __init__(self):self.calls=[];self.failure=None;self.state='RUNNING';self.binding=None
    def preflight(self,config,binding,package):
        self.calls.append('preflight');self.binding=binding
        if self.failure=='preflight':raise ValueError('SYNTHETIC_NETWORK_REFUSAL')
        return {'status':'READY','workspace_spent_micro':0,'synthetic':True}
    def create(self,config,binding,package):
        self.calls.append('create')
        if self.failure=='create':raise TimeoutError('SYNTHETIC_UNCERTAIN_CREATE')
        return {'provider_id':'sb-synthetic'}
    def launch(self,provider_id,binding):
        self.calls.append('launch')
        if self.failure=='launch':raise TimeoutError('SYNTHETIC_UNCERTAIN_LAUNCH')
        return {'submitted':True}
    def status(self,provider_id,binding):
        self.calls.append('status')
        if self.failure=='status':raise TimeoutError('SYNTHETIC_READ_TIMEOUT')
        return {'status':self.state,'provider_id':provider_id,'binding_sha256':digest(canonical(binding))}
    def collect(self,provider_id,binding,folder):
        self.calls.append('collect');private_records.write_text(folder/'result.json','{"status":"VALID"}')
        return {'binding_sha256':digest(canonical(binding)),'file_sha256':inventory(folder)}
    def terminate(self,provider_id):
        self.calls.append('terminate')
        if self.failure=='terminate':raise TimeoutError('SYNTHETIC_TERMINATE_TIMEOUT')
        return {'provider_id':provider_id,'terminated':True}


@pytest.fixture
def setup(tmp_path):
    batch=BatchAccounts(tmp_path/'batch');run='m3-synthetic-run';batch.register_run(run,{'synthetic':True})
    state=tmp_path/'lane';state.mkdir(mode=0o700);config={'synthetic_runtime':True}
    provider=Provider();executor=ModalExecutor(state/'jobs.sqlite',config,provider,batch)
    prepared=tmp_path/'prepared';prepared.mkdir(mode=0o700)
    private_records.write_text(prepared/'run.py','# Synthetic, never executed.\n')
    code=digest(canonical({'run.py':digest((prepared/'run.py').read_bytes())}))
    private_records.write_text(prepared/'SPEC.md','Synthetic only.\nrun_id: '+run+'\nnotebook_code_sha256: '+code+'\n')
    private_records.write_text(prepared/'review.json',json.dumps({'verdict':'APPROVE','rationale':'Synthetic fixture only.'}))
    resources={'gpu':'A100-80GB','cpu':4,'memory_mib':32768,'timeout_seconds':1800}
    binding={'run_id':run,'source':'a'*40,'purpose':'M3_SMOKE','runtime_sha256':digest(canonical(config)),
        'spec_sha256':digest((prepared/'SPEC.md').read_bytes()),'review_sha256':digest((prepared/'review.json').read_bytes()),
        'code_sha256':code,'resources':resources,'overhead_micro_usd':500000,'cost':estimate(resources,500000)}
    private_records.write_bytes(prepared/'manifest.json',canonical({'schema':'modal-run/v1','binding':binding,'files':inventory(prepared)}))
    return executor,provider,batch,run,binding,prepared,state/'package'


def test_known_estimate_uses_sandbox_rates_and_integer_ceiling():
    e=estimate({'gpu':'A100-80GB','cpu':4,'memory_mib':32768,'timeout_seconds':1800},500000)
    assert e['compute_micro_usd']==1917800 and e['reserved_micro_usd']==2417800
    for value in [-1,1.0,True]:
        with pytest.raises(ValueError):estimate({'gpu':'T4','cpu':value,'memory_mib':1024,'timeout_seconds':60},0)


def test_submit_and_repeated_status_never_repeat_dispatch_or_budget(setup):
    e,p,b,run,binding,prepared,package=setup
    assert e.submit(run,binding,prepared,package)['status']=='SUBMITTED'
    rows=[dict(x) for x in b.db.execute('SELECT * FROM autonomy_compute')]
    for _ in range(3):assert e.submit(run,binding,prepared,package)['status']=='RUNNING'
    assert p.calls.count('create')==p.calls.count('launch')==1
    assert rows==[dict(x) for x in b.db.execute('SELECT * FROM autonomy_compute')]
    assert b.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0


@pytest.mark.parametrize('failure',['create','launch'])
def test_uncertain_submission_is_preserved_never_resubmitted(setup,failure):
    e,p,b,run,binding,prepared,package=setup;p.failure=failure
    with pytest.raises(ValueError,match='UNCERTAIN_SUBMISSION'):e.submit(run,binding,prepared,package)
    before=list(p.calls);p.failure=None
    e.submit(run,binding,prepared,package)
    assert p.calls.count('create')==before.count('create') and p.calls.count('launch')==before.count('launch')
    row=b.db.execute('SELECT * FROM autonomy_compute').fetchone()
    assert row['status']=='UNCERTAIN' and row['reserved_micro_usd']>0
    assert (e._paths(run)/'submission-uncertain.json').is_file()


def test_network_refusal_spends_nothing(setup):
    e,p,b,run,binding,prepared,package=setup;p.failure='preflight'
    with pytest.raises(ValueError,match='NETWORK'):e.submit(run,binding,prepared,package)
    assert p.calls==['preflight'] and not package.exists()
    assert b.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==0


@pytest.mark.parametrize('damage',['changed_code','extra_file','review','runtime'])
def test_changed_package_or_binding_refused_before_provider_use(setup,damage):
    e,p,b,run,binding,prepared,package=setup
    if damage=='changed_code':private_records.write_text(prepared/'run.py','changed')
    if damage=='extra_file':private_records.write_text(prepared/'extra.txt','not selected')
    if damage=='review':private_records.write_text(prepared/'review.json','{"verdict":"REVISE"}')
    if damage=='runtime':binding={**binding,'runtime_sha256':'f'*64}
    with pytest.raises(ValueError):e.submit(run,binding,prepared,package)
    assert not p.calls


def test_observation_timeout_is_not_terminal_or_a_resubmission(setup):
    e,p,b,run,binding,prepared,package=setup;e.submit(run,binding,prepared,package);p.failure='status'
    assert e.remote_status(run)['status']=='OBSERVATION_UNAVAILABLE'
    assert b.db.execute('SELECT status FROM autonomy_compute').fetchone()[0]=='RUNNING'
    p.failure=None
    assert e.remote_status(run)['status']=='RUNNING' and p.calls.count('launch')==1


def test_collect_preserves_and_reconciles_cleanup_without_new_job(setup):
    e,p,b,run,binding,prepared,package=setup;e.submit(run,binding,prepared,package);p.state='COMPLETE'
    destination=e.path.parent/'collected';validate=lambda path:json.loads((path/'result.json').read_text())
    p.failure='terminate'
    with pytest.raises(TimeoutError):e.collect_remote(run,package,destination,validate)
    assert destination.is_dir() and b.db.execute('SELECT status FROM autonomy_compute').fetchone()[0]=='RUNNING'
    p.failure=None
    assert e.collect_remote(run,package,destination,validate)['duplicate_collection']
    before=list(p.calls)
    assert e.collect_remote(run,package,destination,validate)['duplicate_collection']
    assert p.calls==before and p.calls.count('collect')==1 and p.calls.count('launch')==1
    assert b.db.execute('SELECT status FROM autonomy_compute').fetchone()[0]=='COLLECTED'
    private_records.check_tree(destination)


def test_workspace_cap_and_halt_refuse_before_reservation(setup):
    e,p,b,run,binding,prepared,package=setup;accounts=ComputeAccounts(b)
    with pytest.raises(ValueError,match='WORKSPACE_COST_CAP'):
        accounts.reserve('cost-test',run,binding,workspace_spent_micro=WORKSPACE_CAP,smoke=True)
    (b.folder/'HALT').write_text('operator stop')
    with pytest.raises(ValueError,match='HALTED'):
        accounts.reserve('cost-test',run,binding,workspace_spent_micro=0,smoke=True)
    assert b.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==0


def test_model_uncertainty_prevents_gpu_reservation(setup):
    e,p,b,run,binding,prepared,package=setup
    b.db.execute("INSERT INTO autonomy_calls VALUES('prior','scientific',?,1,'2026-09-30','UNCERTAIN','{}',NULL)",(run,))
    with pytest.raises(ValueError,match='UNCERTAIN_OR_RUNNING_CALL'):
        ComputeAccounts(b).reserve('cost-test',run,binding,workspace_spent_micro=0,smoke=True)


def test_observed_content_violation_is_not_hidden_as_network_wait(setup,monkeypatch):
    e,p,b,run,binding,prepared,package=setup;e.submit(run,binding,prepared,package)
    def invalid(*args):raise ValueError('MODAL_RESULT_BINDING')
    monkeypatch.setattr(p,'status',invalid)
    with pytest.raises(ValueError,match='RESULT_BINDING'):e.remote_status(run)
    assert p.calls.count('launch')==1
