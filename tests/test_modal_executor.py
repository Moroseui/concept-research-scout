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


def item4_review_fixture(setup,raw):
    # Synthetic package and binding only; this does not submit a provider job.
    from orchestrator.modal_item4_budget import AUTHORITY, TEAM_AUTHORITY
    e,p,b,run,binding,prepared,package=setup
    binding={**binding,'purpose':'M4_ITEM4','experiment':{'backlog_item':4,
        'authority_sha256':AUTHORITY,'team_authority_sha256':TEAM_AUTHORITY}}
    private_records.write_bytes(prepared/'review.json',raw)
    binding['review_sha256']=digest(raw)
    members=inventory(prepared);members.pop('manifest.json')
    private_records.write_bytes(prepared/'manifest.json',canonical({'schema':'modal-run/v1','binding':binding,'files':members}))
    return prepared,binding


def test_item4_package_uses_structured_findings_and_opaque_prose(setup):
    raw=canonical({'verdict':'APPROVE','findings':[],
        'rationale':'Synthetic explanation discussing BLOCKER[budget] examples, not a finding.'})
    prepared,binding=item4_review_fixture(setup,raw)
    assert verify_package(prepared,binding)['binding']==binding
    assert not setup[1].calls
    assert setup[2].db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==0


@pytest.mark.parametrize('bad',['finding','revise','reject','missing-findings','duplicate-verdict','legacy','ambiguous','binding'])
def test_item4_package_refuses_nonapproval_or_malformed_structure(setup,bad):
    value={'verdict':'APPROVE','findings':[],'rationale':'Synthetic inspection.'}
    if bad=='finding':value['findings']=[{'id':'F1','category':'budget','text':'Missing bound.', 'evidence':'SPEC.md','resolution':'Supply bound.'}]
    elif bad in {'revise','reject'}:value['verdict']=bad.upper()
    elif bad in {'missing-findings','legacy'}:value.pop('findings')
    elif bad=='ambiguous':value['verdict']='APPROVE or REVISE'
    raw=canonical(value)
    if bad=='duplicate-verdict':raw=b'{"verdict":"REJECT","verdict":"APPROVE","findings":[],"rationale":"Synthetic"}'
    prepared,binding=item4_review_fixture(setup,raw)
    if bad=='binding':binding['review_sha256']='f'*64
    with pytest.raises(ValueError):verify_package(prepared,binding)
    assert not setup[1].calls
    assert setup[2].db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==0


class Item4Provider(Provider):
    """Synthetic provider only; real budget transaction and job lifecycle below."""
    def __init__(self):super().__init__();self.spent='0';self.missing_billing=False
    def preflight(self,config,binding,package):
        value=super().preflight(config,binding,package)
        from datetime import datetime,timezone
        body={'schema':'modal-billing-snapshot/v1','workspace':'moroseui',
              'observed_at':datetime.now(timezone.utc).isoformat(),'rates':ITEM4_RATES,
              'rows':[],'summary':{'metered_cost':self.spent,'billed_cost':self.spent,'adjustments':{}}}
        from orchestrator.modal_billing import canonical as billing_canonical
        if not self.missing_billing:value['billing_snapshot']={**body,'sha256':digest(billing_canonical(body))}
        return value
    def create(self,config,binding,package):
        result=super().create(config,binding,package)
        return {**result,'provider_id':'sb-'+digest(canonical(binding))[:24]}


ITEM4_RATES={'cpu_hour_cost_sandbox':'.1419','mem_gib_hour_cost_sandbox':'.024',
             'gpu_hour_cost_a100_80gb':'2.5','gpu_hour_cost_h100':'3.95','gpu_hour_cost_b200':'6.25'}


@pytest.fixture
def item4_dispatch(setup):
    from orchestrator.modal_item4_budget import AUTHORITY
    e,_,b,run,_,_,_=setup
    b.db.execute('UPDATE autonomy_runs SET binding=? WHERE id=?',
                 (json.dumps({'backlog_item':4,'experiment_authority_sha256':AUTHORITY}),run))
    p=Item4Provider();e.provider=p
    return e,p,b,run


def make_item4_package(fixture,fit='one',segment=1,gpu='H100'):
    from orchestrator.modal_item4_budget import AUTHORITY,TEAM_AUTHORITY,quote
    from orchestrator.modal_executor import item4_job
    e,p,b,run=fixture
    prepared=e.path.parent/('prepared-'+fit+'-'+str(segment));prepared.mkdir(mode=0o700)
    private_records.write_text(prepared/'run.py','# Synthetic fit, never executed.\n')
    code=digest(canonical({'run.py':digest((prepared/'run.py').read_bytes())}))
    private_records.write_text(prepared/'SPEC.md','Synthetic only.\nrun_id: '+run+'\nnotebook_code_sha256: '+code+'\n')
    private_records.write_bytes(prepared/'review.json',canonical({'verdict':'APPROVE','findings':[], 'rationale':'Synthetic package approval.'}))
    resources={'gpu':gpu,'cpu':16,'memory_mib':65536,'timeout_seconds':60}
    binding={'run_id':run,'source':'a'*40,'purpose':'M4_ITEM4','runtime_sha256':digest(canonical(e.config)),
             'spec_sha256':digest((prepared/'SPEC.md').read_bytes()),'review_sha256':digest((prepared/'review.json').read_bytes()),
             'code_sha256':code,'resources':resources,'overhead_micro_usd':0,'cost':quote(resources,ITEM4_RATES,0),
             'experiment':{'backlog_item':4,'authority_sha256':AUTHORITY,'team_authority_sha256':TEAM_AUTHORITY,
                           'fit_id':fit,'stage':'SMOKE','segment':segment,'billing_object_id':'ap-'+fit}}
    private_records.write_bytes(prepared/'manifest.json',canonical({'schema':'modal-run/v1','binding':binding,'files':inventory(prepared)}))
    job=item4_job(binding);return job,binding,prepared,e.path.parent/('emitted-'+job)


def test_item4_executor_dispatches_independent_fits_against_one_owner_once(item4_dispatch):
    e,p,b,run=item4_dispatch
    one=make_item4_package(item4_dispatch);two=make_item4_package(item4_dispatch,'two',gpu='B200')
    assert one[0]!=two[0] and e.submit(*one)['status']==e.submit(*two)['status']=='SUBMITTED'
    before=[tuple(r) for r in b.db.execute('SELECT * FROM autonomy_compute ORDER BY id')]
    assert len(before)==2 and {r[1] for r in before}=={run}
    for _ in range(3):assert e.submit(*one)['status']=='RUNNING'
    assert p.calls.count('create')==p.calls.count('launch')==2
    assert before==[tuple(r) for r in b.db.execute('SELECT * FROM autonomy_compute ORDER BY id')]
    assert b.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0


def test_item4_headroom_wait_is_recheckable_without_partial_dispatch(item4_dispatch):
    e,p,b,run=item4_dispatch;args=make_item4_package(item4_dispatch);p.spent='1000'
    for _ in range(2):assert e.submit(*args)['status']=='WAIT_PROVIDER_HEADROOM'
    assert not args[3].exists() and not e._paths(args[0]).exists()
    assert e.db.execute('SELECT count(*) FROM manual_packages').fetchone()[0]==0
    assert b.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==0
    assert p.calls==['preflight','preflight']
    p.spent='0';assert e.submit(*args)['status']=='SUBMITTED'
    assert p.calls.count('create')==p.calls.count('launch')==1


@pytest.mark.parametrize('failure',['create','launch'])
def test_item4_uncertain_provider_operation_never_restarts_fit(item4_dispatch,failure):
    e,p,b,run=item4_dispatch;args=make_item4_package(item4_dispatch);p.failure=failure
    with pytest.raises(ValueError,match='^MODAL_UNCERTAIN_SUBMISSION_NO_RESUBMISSION$'):e.submit(*args)
    before=list(p.calls);rows=[tuple(r) for r in b.db.execute('SELECT * FROM autonomy_compute')]
    p.failure=None;e.submit(*args)
    assert p.calls.count('create')==before.count('create') and p.calls.count('launch')==before.count('launch')
    assert rows==[tuple(r) for r in b.db.execute('SELECT * FROM autonomy_compute')]
    assert rows[0][3]=='UNCERTAIN'


def test_item4_requires_live_billing_and_refuses_unbound_job_before_creation(item4_dispatch):
    e,p,b,run=item4_dispatch;args=make_item4_package(item4_dispatch)
    with pytest.raises(ValueError,match='^MODAL_RUNTIME_BINDING$'):e.submit(run,*args[1:])
    assert not p.calls
    p.missing_billing=True
    with pytest.raises(ValueError,match='^ITEM4_PROVIDER_BILLING_PREFLIGHT$'):e.submit(*args)
    assert b.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==0
    assert p.calls==['preflight']


def test_item4_segment_two_requires_prior_terminal_checkpoint(item4_dispatch):
    e,p,b,run=item4_dispatch;first=make_item4_package(item4_dispatch)
    e.submit(*first);second=make_item4_package(item4_dispatch,segment=2)
    with pytest.raises(ValueError,match='^ITEM4_RESUME_TERMINAL_PROOF_REQUIRED$'):e.submit(*second)
    assert p.calls.count('create')==p.calls.count('launch')==1
    assert b.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==1
    assert not second[3].exists()


def test_item4_collection_reuses_normal_validation_and_no_duplicate_charge(item4_dispatch):
    e,p,b,run=item4_dispatch;args=make_item4_package(item4_dispatch);e.submit(*args);p.state='COMPLETE'
    dest=e.path.parent/'collected-item4';validate=lambda path:json.loads((path/'result.json').read_text())
    assert e.collect_remote(args[0],args[3],dest,validate)['status']=='VALID'
    before=list(p.calls);rows=[tuple(r) for r in b.db.execute('SELECT * FROM autonomy_compute')]
    assert e.collect_remote(args[0],args[3],dest,validate)['duplicate_collection']
    assert p.calls==before and rows==[tuple(r) for r in b.db.execute('SELECT * FROM autonomy_compute')]
    assert rows[0][3]=='COLLECTED'
