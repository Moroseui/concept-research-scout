"""Real native submission/seal/dispatch/accounting, on labelled synthetic fixtures.

External administrative authority and its exact allowlist are synthetic here;
no scientific decision, patient bytes, paid SDK operation or genuine receipt is
fabricated. Native MCP qualification and evidence/hash checks are not mocked.
"""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import item4_validation_admission as gate,experiment_approval as approval
from orchestrator import experiment_package,review_submission as rs,private_records as pr
from orchestrator.manual_executor import digest
from orchestrator.manual_driver import Driver
from test_experiment_context import experiment,root
from test_experiment_approval import reviewed as base_reviewed


@pytest.fixture
def reviewed(experiment,monkeypatch,request):
    original=rs.submit
    def submit(work,pin,decision):
        decision.update(verdict='REVISE',findings=[{'id':name,'category':'code/spec mismatch',
            'text':'Synthetic unresolved validation fixture, no research judgment.',
            'evidence':'Synthetic fixture only.','resolution':'Retain this finding until actual evidence.'}
            for name in ['U1-input-provenance','U2-runtime-interface-native-integration','U3-coverage-arm-source-validation']])
        return original(work,pin,decision)
    monkeypatch.setattr(rs,'submit',submit)
    return base_reviewed.__wrapped__(experiment,monkeypatch,request)


@pytest.fixture
def validation(reviewed,monkeypatch):
    d,value,work=reviewed
    from orchestrator import experiment_plan_output as authored,manual_context as mc
    selected=json.loads((Path(__file__).parents[1]/gate.DOCUMENT).read_bytes())
    plan_ref=authored.ref(d,value)
    rows={a['id']:a for a in mc.selected_artifacts('run_spec_review',value['artifacts'])}
    module=Path(value['notebook_revision_result']['folder'])/'synthetic/package/execution.py'
    selected.update(run_id=d.config['run_id'],source=d.config['source'],state=str(d.state),
        review_round=value['pending']['round'],author_round=plan_ref['version'],
        review_call=value['pending']['id'],review_sha256=digest((work/'review.json').read_bytes()),
        submission_sha256=digest((work/rs.RECORD).read_bytes()),plan_sha256=plan_ref['sha256'],
        module_sha256=digest(module.read_bytes()),artifact_pins={name:{k:rows[name][k] for k in ['sha256','version']}
            for name in selected['artifact_pins']})
    monkeypatch.setattr(gate,'REVIEW_SHA',selected['review_sha256'])
    monkeypatch.setattr(gate,'contract',lambda:copy.deepcopy(selected))
    monkeypatch.setattr(gate,'authority',lambda:'c'*64) # Labelled external implementation approval fixture only.
    return d,value,work,selected


pytestmark=pytest.mark.parametrize('reviewed',['authored4'],indirect=True)


def test_real_revise_submission_seals_without_closing_findings_or_calls(validation):
    d,value,work,selected=validation
    originals={name:(work/name).read_bytes() for name in ['review.json','console.log',rs.RECORD]}
    calls=[tuple(x) for x in d.store.db.execute('SELECT * FROM manual_calls')]
    manifest=approval.record(d,value,value['pending'])
    assert approval.verify(d,value)==manifest
    assert manifest['validation_admission']['scientific_verdict']=='REVISE'
    assert manifest['validation_admission']['findings_closed'] is False
    assert manifest['validation_admission']['full_training_allowed'] is False
    experiment_package.emit(d,value)
    assert json.loads((d.state/'experiment-package/review.json').read_bytes())['verdict']=='REVISE'
    assert originals=={name:(work/name).read_bytes() for name in originals}
    assert calls==[tuple(x) for x in d.store.db.execute('SELECT * FROM manual_calls')]
    assert not d.store.batch.db.execute("SELECT 1 FROM sqlite_master WHERE name='autonomy_compute'").fetchone()


@pytest.mark.parametrize('damage',['review','native','submission','config','incomplete','wrong-round','module','plan','spec','test','authority'])
def test_changes_cannot_use_the_exact_revise_exception(validation,monkeypatch,damage):
    d,value,work,selected=validation
    if damage in {'review','native','submission','config'}:
        name={'review':'review.json','native':'console.log','submission':rs.RECORD,'config':rs.CONFIG}[damage]
        pr.write_bytes(work/name,(work/name).read_bytes()+b' ')
    elif damage=='incomplete':d.store.db.execute("UPDATE manual_calls SET status='UNCERTAIN'")
    elif damage=='wrong-round':value['pending']['round']+=1
    elif damage=='module':pr.write_bytes(Path(value['notebook_revision_result']['folder'])/'synthetic/package/execution.py',b'changed')
    elif damage in {'plan','spec'}:
        key='authored-execution-plan' if damage=='plan' else 'run_spec'
        ref=next(a for a in reversed(value['artifacts']) if a['id']==key)
        pr.write_bytes(d.context/ref['path'],b'changed')
    elif damage=='test':pr.write_bytes(Path(value['notebook_revision_result']['folder'])/'synthetic/receipt.json',b'{}')
    else:monkeypatch.setattr(gate,'authority',lambda:(_ for _ in ()).throw(ValueError('not approved')))
    with pytest.raises((ValueError,KeyError)):approval.record(d,value,value['pending'])
    assert 'reviewed_execution' not in value


def test_default_genuine_revise_still_refuses_without_exact_authority(validation,monkeypatch):
    d,value,work,selected=validation
    monkeypatch.setattr(gate,'REVIEW_SHA','f'*64)
    with pytest.raises(ValueError,match='^EXPERIMENT_APPROVAL_REQUIRED$'):
        approval.record(d,value,value['pending'])


def runtime(selected,fit='smoke-A1_repeat',*,preprocessing=False):
    value={'purpose':'M4_ITEM4','run_id':selected['run_id'],'source':selected['source'],'image_id':selected['image_id'],
        'resources':{'gpu':None if preprocessing else 'A100-80GB','cpu':16,'memory_mib':131072,'timeout_seconds':60},
        'experiment':{'backlog_item':4,'stage':'SMOKE','fit_id':fit,'segment':1},
        'review_sha256':selected['review_sha256'],'spec_sha256':selected['artifact_pins']['run_spec']['sha256'],
        'execution_plan_sha256':selected['plan_sha256'],'execution':{'module_sha256':selected['module_sha256']}}
    if preprocessing:
        value['experiment']['fit_id']='preprocess-'+selected['preprocessing_id']
        value['preprocessing']={'id':selected['preprocessing_id'],'input_contract_sha256':selected['input_contract_sha256']}
    else:value['progress']={'fit_binding':dict(zip(['arm','fold','realization'],selected['fits'][fit]))}
    return value


def test_exact_preparation_and_five_smokes_permitted_by_scope(validation):
    d,value,work,selected=validation;manifest=approval.record(d,value,value['pending'])
    gate.scope(manifest,runtime(selected,preprocessing=True),bound=True)
    for fit in selected['fits']:gate.scope(manifest,runtime(selected,fit),bound=True)
    resumed=runtime(selected);resumed['experiment']['segment']=2
    gate.scope(manifest,resumed,bound=True) # Terminal/checkpoint evidence still checked by ordinary reserve.


@pytest.mark.parametrize('damage',['full','coverage-fit','coverage-prep','other-fit','other-prep','arm','fold','realization','image','input','gpu-prep','marker','removed-marker','bound-module','bound-plan','bound-spec','segment'])
def test_held_scope_is_refused_at_the_actual_package_dispatch_boundary(validation,tmp_path,damage):
    d,value,work,selected=validation;manifest=approval.record(d,value,value['pending']);experiment_package.emit(d,value)
    pre=damage in {'coverage-prep','other-prep','input','gpu-prep'}
    binding=runtime(selected,preprocessing=pre)
    if damage=='full':binding['experiment']['stage']='FULL'
    elif damage in {'coverage-fit','other-fit'}:binding['experiment']['fit_id']='smoke-A1_zscore' if damage=='coverage-fit' else 'foreign'
    elif damage in {'coverage-prep','other-prep'}:
        binding['preprocessing']['id']='prep-A1_zscore' if damage=='coverage-prep' else 'foreign'
        binding['experiment']['fit_id']='preprocess-'+binding['preprocessing']['id']
    elif damage in {'arm','fold','realization'}:binding['progress']['fit_binding'][damage]='changed'
    elif damage=='image':binding['image_id']='im-other'
    elif damage=='input':binding['preprocessing']['input_contract_sha256']='f'*64
    elif damage=='gpu-prep':binding['resources']['gpu']='H100'
    elif damage=='marker':manifest['validation_admission']['full_training_allowed']=True
    elif damage=='removed-marker':manifest.pop('validation_admission')
    elif damage=='segment':binding['experiment']['segment']=0
    else:
        if damage=='bound-module':binding['execution']['module_sha256']='f'*64
        if damage=='bound-plan':binding['execution_plan_sha256']='f'*64
        if damage=='bound-spec':binding['spec_sha256']='f'*64
    with pytest.raises(ValueError,match='ITEM4_VALIDATION_'):gate.scope(manifest,binding,bound=True)
    if damage in {'marker','removed-marker','bound-module','bound-plan','bound-spec'}:return
    # Real package producer is the dispatch boundary; no provider object exists.
    from orchestrator import experiment_modal_package as bridge
    base=bridge.base_binding(binding);target=tmp_path/'not-created'
    with pytest.raises(ValueError,match='ITEM4_VALIDATION_'):bridge.emit(d,value,target,base)
    assert not target.exists()


def prepare_activation(d,value,work,selected):
    from tools import item4_validation_runtime as service
    from orchestrator.manual_executor import atomic
    value.pop('pending');value.update(phase='BLOCKED',reason='UNRESOLVED_AFTER_THREE_REVISIONS',review=str(work/'review.json'),
        rounds={'run_spec_author':selected['author_round'],'run_spec_review':selected['review_round']})
    raw=json.dumps(value,sort_keys=True);d.store.db.execute('INSERT OR REPLACE INTO manual_state VALUES(1,?)',(raw,))
    atomic(d.state/'lane.json',d.config)
    selected.update(state_sha256=digest(raw.encode()),config_sha256=digest((d.state/'lane.json').read_bytes()),context_files={},
        local_calls_sha256=digest(rs.canonical([dict(x) for x in d.store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')])),
        scientific_calls_sha256=digest(rs.canonical([dict(x) for x in d.store.batch.db.execute("SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid")])))
    return service,raw


def test_activation_is_one_cas_and_preserves_every_original_call(validation):
    d,value,work,selected=validation;service,raw=prepare_activation(d,value,work,selected)
    local=[tuple(x) for x in d.store.db.execute('SELECT * FROM manual_calls')]
    global_rows=[tuple(x) for x in d.store.batch.db.execute('SELECT * FROM autonomy_calls')]
    review=(work/'review.json').read_bytes()
    assert service.activate(d,gate)['status']=='VALIDATION_ONLY_READY'
    current=json.loads(d.store.db.execute('SELECT payload FROM manual_state').fetchone()[0])
    assert current['phase']=='COMMIT_SPEC' and current['review']==str(work/'review.json')
    assert current['artifacts']==value['artifacts'] and current['rounds']==value['rounds']
    assert (d.state.parent/service.CHANGE/'ORIGINAL_STATE.json').read_text()==raw
    assert local==[tuple(x) for x in d.store.db.execute('SELECT * FROM manual_calls')]
    assert global_rows==[tuple(x) for x in d.store.batch.db.execute('SELECT * FROM autonomy_calls')]
    assert (work/'review.json').read_bytes()==review
    with pytest.raises(ValueError,match='ACTIVATION_STATE'):service.activate(d,gate)


@pytest.mark.parametrize('damage',['state','local-call','global-call','findings','config','intent'])
def test_activation_refuses_changed_or_partial_originals(validation,damage):
    d,value,work,selected=validation;service,raw=prepare_activation(d,value,work,selected)
    if damage=='state':d.store.db.execute("UPDATE manual_state SET payload='{}'")
    elif damage=='local-call':d.store.db.execute("UPDATE manual_calls SET status='UNCERTAIN'")
    elif damage=='global-call':d.store.batch.db.execute("UPDATE autonomy_calls SET status='UNCERTAIN'")
    elif damage=='config':pr.write_text(d.state/'lane.json','{}')
    elif damage=='findings':
        pr.write_text(d.context/'obligations.json','changed');selected['context_files']={'obligations.json':'f'*64}
    else:
        folder=d.state.parent/service.CHANGE;pr.mkdir(folder);pr.write_text(folder/'ACTIVATION_INTENT.json','preserved')
    before=d.store.db.execute('SELECT payload FROM manual_state').fetchone()[0]
    with pytest.raises((ValueError,FileExistsError)):service.activate(d,gate)
    assert d.store.db.execute('SELECT payload FROM manual_state').fetchone()[0]==before


@pytest.fixture
def owned(validation):
    from orchestrator import experiment_context as ec
    from orchestrator.modal_budget import ComputeAccounts
    from orchestrator.modal_item4_policy import AUTHORITY,TEAM_AUTHORITY,quote
    from test_modal_item4_budget import RATES
    d,value,work,selected=validation
    approval.record(d,value,value['pending']);experiment_package.emit(d,value)
    owner={'state':str(d.state),'source':d.config['source'],'run_id':d.config['run_id'],
        'plan_sha256':d.config['plan_sha256'],'review_sha256':'d'*64,'execution_scope':copy.deepcopy(ec.selection(d))}
    d.config.update(owner_binding=owner,engine_review={'sha256':'d'*64})
    pr.atomic(d.state/'lane.json',d.config)
    d.store.db.execute('INSERT OR REPLACE INTO manual_state VALUES(1,?)',(json.dumps(value),))
    d.store.batch.db.execute('UPDATE autonomy_runs SET binding=? WHERE id=?',(json.dumps(owner),d.config['run_id']))
    d.store.batch.filesystem_root=Path('/')
    binding=runtime(selected);binding.update(overhead_micro_usd=0)
    binding['execution']['approval_sha256']=value['reviewed_execution']['sha256']
    binding['experiment'].update(authority_sha256=AUTHORITY,team_authority_sha256=TEAM_AUTHORITY,billing_object_id='ap-validation')
    binding['cost']=quote(binding['resources'],RATES,0)
    return d,value,selected,binding,ComputeAccounts(d.store.batch)


def reserve(owned,binding):
    from test_modal_item4_budget import snapshot,NOW
    from orchestrator.modal_executor import canonical
    d,value,selected,base,accounts=owned
    return accounts.reserve_item4(digest(canonical(binding)),binding['run_id'],binding,billing_snapshot=snapshot(),now=NOW)


def test_actual_budget_owner_requalifies_revise_and_reserves_once(owned):
    d,value,selected,binding,accounts=owned
    calls=[tuple(x) for x in d.store.batch.db.execute('SELECT * FROM autonomy_calls')]
    assert reserve(owned,binding) is True
    assert reserve(owned,binding) is False
    assert d.store.batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==1
    assert calls==[tuple(x) for x in d.store.batch.db.execute('SELECT * FROM autonomy_calls')]
    # The untouched admission policy still requires genuine interrupted-segment proof.
    later=copy.deepcopy(binding);later['experiment']['segment']=2
    with pytest.raises(ValueError,match='ITEM4_RESUME_TERMINAL_PROOF_REQUIRED'):reserve(owned,later)


@pytest.mark.parametrize('damage',['FULL','coverage','foreign','changed-code','changed-review','changed-seal','missing-marker'])
def test_actual_spending_consumer_refuses_outside_validation_scope(owned,damage):
    d,value,selected,binding,accounts=owned
    if damage=='FULL':binding['experiment']['stage']='FULL'
    elif damage=='coverage':binding['experiment']['fit_id']='smoke-A1_histeq'
    elif damage=='foreign':binding['experiment']['fit_id']='another'
    elif damage=='changed-code':binding['execution']['module_sha256']='f'*64
    elif damage=='changed-review':binding['review_sha256']='f'*64
    elif damage=='changed-seal':binding['execution']['approval_sha256']='f'*64
    else:
        path=Path(value['reviewed_execution']['path']);manifest=json.loads(path.read_bytes());manifest.pop('validation_admission');pr.write_bytes(path,rs.canonical(manifest))
        value['reviewed_execution']['sha256']=digest(path.read_bytes())
        d.store.db.execute('UPDATE manual_state SET payload=?',(json.dumps(value),))
    with pytest.raises(ValueError):reserve(owned,binding)
    assert d.store.batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==0


def test_cap_exceeding_validation_launch_still_refused_and_past_amount_retained(owned):
    d,value,selected,binding,accounts=owned
    d.store.batch.db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,'READY',?,?)",
        ('preserved',binding['run_id'],'{}',75_000_000,'{}'))
    originals=[tuple(x) for x in d.store.batch.db.execute('SELECT * FROM autonomy_assets')]
    with pytest.raises(ValueError,match='^ITEM4_HARD_COST_CAP$'):reserve(owned,binding)
    assert d.store.batch.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==0
    assert originals==[tuple(x) for x in d.store.batch.db.execute('SELECT * FROM autonomy_assets')]


@pytest.mark.parametrize('kind',['call','compute','asset'])
def test_normal_uncertainty_refusals_survive_validation_admission(owned,kind):
    d,value,selected,binding,accounts=owned
    if kind=='call':d.store.batch.db.execute("INSERT INTO autonomy_calls VALUES('uncertain','scientific','other',1,'2026-10-06','UNCERTAIN','{}',NULL)")
    if kind=='compute':d.store.batch.db.execute("INSERT INTO autonomy_compute VALUES('uncertain','other','{}','UNCERTAIN',100,NULL,NULL,'2026-10')")
    if kind=='asset':d.store.batch.db.execute("INSERT INTO autonomy_assets VALUES('uncertain','other','{}','UNCERTAIN',100,'{}')")
    with pytest.raises(ValueError,match='UNCERTAIN'):reserve(owned,binding)
    assert not d.store.batch.db.execute('SELECT 1 FROM autonomy_compute WHERE run=?',(binding['run_id'],)).fetchone()


def test_positive_real_package_dispatch_preserves_revise_and_code(validation):
    from orchestrator import experiment_modal_package as bridge
    from orchestrator.modal_executor import verify_package
    from orchestrator.modal_item4_policy import AUTHORITY,TEAM_AUTHORITY
    d,value,work,selected=validation;approval.record(d,value,value['pending']);experiment_package.emit(d,value)
    base=bridge.base_binding(runtime(selected))
    base['experiment'].update(authority_sha256=AUTHORITY,team_authority_sha256=TEAM_AUTHORITY)
    folder=d.state/'selected-modal-package';manifest=bridge.emit(d,value,folder,base)
    assert verify_package(folder,manifest['binding'])==manifest
    assert json.loads((folder/'review.json').read_bytes())['verdict']=='REVISE'
    assert (folder/'execution.py').read_bytes()==(d.state/'experiment-package/code/execution.py').read_bytes()
    assert bridge.emit(d,value,folder,base)==manifest


@pytest.fixture
def terminal_fixture(owned,monkeypatch):
    """External original-proof verifier is a labelled synthetic boundary here.

    The live read-only qualification is recorded separately; these tests exercise
    its real parent consumer, original rows, actual owner, and ordinary budgets.
    """
    import subprocess
    d,value,selected,binding,accounts=owned;db=accounts.db
    for ident in gate.TERMINAL_ASSETS:
        db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,'UNCERTAIN',?,?)",
            (ident,binding['run_id'],'{}',1_000_000,'{}'))
    for ident in gate.TERMINAL_COMPUTE:
        db.execute("INSERT INTO autonomy_compute VALUES(?,?,?,'RUNNING',?,?,NULL,'2026-10')",
            (ident,'diagnostics-other','{}',2_000_000,'sb-terminal'))
    proof={'schema':'item4-retained-terminal-qualification/v1',
        'source_sha':'28726e3d5cdf32f1d80c63187f5abd9146cbfcd0',
        'source_asset':'9878e7923ea81dceefce162166a113aa7d0a53dd65c4199a42b4276fe952d365'}
    for key,table,ids in [('assets','autonomy_assets',gate.TERMINAL_ASSETS),('compute','autonomy_compute',gate.TERMINAL_COMPUTE)]:
        proof[key]={r['id']:digest(rs.canonical(dict(r))) for r in db.execute('SELECT * FROM '+table) if r['id'] in ids}
    original=subprocess.check_output
    def output(args,*a,**kw):
        if args==['/usr/bin/python3','-s','-B',str(gate.ROOT/'tools/item4_validation_retained.py')]:
            return json.dumps(proof).encode()
        return original(args,*a,**kw)
    monkeypatch.setattr(subprocess,'check_output',output)
    before={table:[tuple(r) for r in db.execute('SELECT * FROM '+table)] for table in ('autonomy_assets','autonomy_compute')}
    return owned,proof,before


def test_qualified_terminal_rows_remain_unchanged_and_charged(terminal_fixture):
    owned,proof,before=terminal_fixture;d,value,selected,binding,accounts=owned
    assert reserve(owned,binding)
    assert before['autonomy_assets']==[tuple(r) for r in accounts.db.execute('SELECT * FROM autonomy_assets')]
    assert before['autonomy_compute']==[tuple(r) for r in accounts.db.execute('SELECT * FROM autonomy_compute WHERE run!=?',(binding['run_id'],))]
    # Kept asset reservations consume cap; terminal proof does not release them.
    second=copy.deepcopy(binding);second['experiment']['fit_id']='smoke-A1_repeat2'
    second['experiment']['billing_object_id']='ap-second'
    second['progress']['fit_binding']=dict(zip(['arm','fold','realization'],selected['fits']['smoke-A1_repeat2']))
    accounts.db.execute("INSERT INTO autonomy_assets VALUES('cap',?,?,'READY',?,?)",(binding['run_id'],'{}',72_000_000,'{}'))
    with pytest.raises(ValueError,match='ITEM4_HARD_COST_CAP'):reserve(owned,second)


@pytest.mark.parametrize('damage',['asset-row','compute-row','missing-asset','missing-compute','foreign-proof','release','source','unknown-live','unknown-asset'])
def test_terminal_bridge_refuses_stale_forged_or_unrelated_proofs(terminal_fixture,damage):
    owned,proof,before=terminal_fixture;d,value,selected,binding,accounts=owned
    if damage=='asset-row':accounts.db.execute("UPDATE autonomy_assets SET reserved_micro_usd=1")
    elif damage=='compute-row':accounts.db.execute("UPDATE autonomy_compute SET provider_id='sb-changed'")
    elif damage=='missing-asset':proof['assets'].pop(next(iter(proof['assets'])))
    elif damage=='missing-compute':proof['compute'].pop(next(iter(proof['compute'])))
    elif damage=='foreign-proof':proof['compute']['foreign']='f'*64
    elif damage=='release':proof['source_sha']='f'*40
    elif damage=='source':proof['source_asset']='f'*64
    elif damage=='unknown-live':accounts.db.execute("INSERT INTO autonomy_compute VALUES('live','other','{}','RUNNING',1,NULL,'sb-live','2026-10')")
    else:accounts.db.execute("INSERT INTO autonomy_assets VALUES('unknown','other','{}','UNCERTAIN',1,'{}')")
    with pytest.raises(ValueError):reserve(owned,binding)
    assert not accounts.db.execute('SELECT 1 FROM autonomy_compute WHERE run=?',(binding['run_id'],)).fetchone()


def test_terminal_bridge_never_qualifies_an_ordinary_other_run(terminal_fixture):
    owned,proof,before=terminal_fixture;d,value,selected,binding,accounts=owned
    binding['review_sha256']='f'*64
    assert gate.retained_terminal(accounts,binding)==(set(),set())
