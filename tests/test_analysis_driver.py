"""Analysis driver integration with synthetic native outputs; never model calls."""
import ast
import json
from pathlib import Path
import re
import subprocess

import pytest

from orchestrator import analysis_driver, autonomy_backlog, connectivity, manual_runtime, private_records
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.manual_executor import atomic, read, digest
from test_manual_lane import lane, root, ROOT, private_copied_fixture
from test_scientific_intake import registered


def fake_model(work, stage, clients, expected):
    raw = (work/'prompt.md').read_bytes(); assert digest(raw) == expected
    if stage == 'run_spec_author':
        text = raw.decode()
        run = re.search(r'^run_id: (.+)$', text, re.M)[1]
        registry = re.search(r'^analysis_registry_sha256: (.+)$', text, re.M)[1]
        private_records.write_text(work/'SPEC.proposed.md', '# Synthetic analysis\nrun_id: '+run+'\nanalysis_registry_sha256: '+registry+'\nInspect saved aggregates and retain limitations; no computation.\n')
    elif stage.endswith('review'):
        private_records.write_text(work/'review.json', json.dumps({'verdict': 'APPROVE', 'rationale': 'Synthetic fixture only; no genuine reviewer.'}))
    else:
        private_records.write_text(work/'interpretation.md', '# Summary\nThe synthetic evidence answers the fixture question only; no scientific conclusion is established.\n# Details\nThe aggregate fixture was inspected. No patient-level file was used.\n')
        private_records.write_text(work/'investigator_next_decision.json', json.dumps({'status': 'PROPOSAL_ONLY', 'proposed_action_type': 'stop',
            'action': 'Stop for operator review of the stock-take.', 'rationale': 'The next backlog item remains held.', 'charter_basis': '', 'blocker_ids': []}))
    return {'family_effective': 'claude' if stage.endswith('review') else 'codex', 'exit_class': 'ok', 'synthetic': True}


@pytest.fixture
def analysis_lane(lane, monkeypatch):
    config = read(lane/'lane.json'); context = Path(config['context']); repo = Path(config['root'])
    monkeypatch.setattr(connectivity, 'require', lambda *a, **k: {'synthetic': True})
    monkeypatch.setattr(manual_runtime, 'settings', lambda: {'host_guard': {'receipt': str(lane/'missing-proof.json')}})
    ref, _ = registered(context, monkeypatch)
    backlog = b'# Backlog\n1. Stock-take. Stop for operator review.\n2. Proposal after operator review.\n3. CPU not authorized.\n'
    authority = b'Synthetic operator original only.'
    parts = autonomy_backlog.numbered_items(backlog)
    binding = {'schema': 'operator-backlog/v1', 'backlog_sha256': digest(backlog), 'operator_sha256': digest(authority),
        'items': [{'number': n, 'sha256': parts[n][1], 'mode': 'cpu' if n == 3 else 'analysis',
                   'state': ['AUTHORIZED', 'WAIT_OPERATOR', 'NOT_AUTHORIZED'][n-1], 'prerequisites': [] if n == 1 else [n-1]} for n in range(1, 4)]}
    refs = {}
    for key, name, raw in [('backlog', 'BACKLOG.md', backlog), ('operator', 'operator.txt', authority),
                            ('backlog_binding', 'backlog-binding.json', json.dumps(binding).encode())]:
        private_records.write_bytes(context/name, raw)
        refs[key] = {'path': name, 'sha256': digest(raw)}
    plan = {'schema': 'stocktake-analysis/v1', 'context': str(context), 'context_files': {}, **refs,
            'item_number': 1, 'item_sha256': parts[1][1], 'private_intake': ref,
            'idea_ids': ['sprints-stocktake'], 'artifacts': [], 'batch_ledger': str(repo/'analysis-batch')}
    private_copied_fixture(context)
    plan['context_files'] = {str(p.relative_to(context)): digest(p.read_bytes()) for p in context.rglob('*') if p.is_file()}
    atomic(lane/'preparation-plan.json', plan)
    batch = BatchAccounts(plan['batch_ledger']); batch.register_run(config['run_id'], {'synthetic': True})
    config.update(backend='analysis', batch_ledger=plan['batch_ledger'], private_intake=ref, idea_ids=plan['idea_ids'],
                  plan_sha256=digest((lane/'preparation-plan.json').read_bytes()), item_number=1, item_sha256=parts[1][1], **refs)
    atomic(lane/'lane.json', config)
    private_records.write_text(repo/'.gitignore', 'lane/\nlane-scientific-workspaces/\nanalysis-batch/\n')
    for k, v in [('user.name', 'Synthetic test'), ('user.email', 'fixture@invalid')]:
        subprocess.run(['git', 'config', k, v], cwd=repo, check=True)
    subprocess.run(['git', 'add', '.'], cwd=repo, check=True)
    subprocess.run(['git', 'commit', '-qm', 'Synthetic analysis fixture'], cwd=repo, check=True)
    return analysis_driver.AnalysisDriver(lane, runner=fake_model)


def test_four_native_stage_connections_finish_without_execution_and_stop(analysis_lane):
    d = analysis_lane
    for phase in ['run_spec_review', 'COMMIT_SPEC', 'result_interpretation_author', 'result_interpretation_review', 'UPDATE_STATE', 'REPORT', 'COMPLETE']:
        outcome = d.advance(); assert outcome['phase'] == phase, outcome
    assert d.status()['calls_used'] == 4
    assert d.advance()['calls_used'] == 4
    assert d.store.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0] == 4
    assert d.store.batch.db.execute('SELECT status FROM autonomy_runs').fetchone()[0] == 'COMPLETE'
    assert d.current()['operator_review_pending'] is True
    assert not (d.state/'package').exists()
    assert read(d.state/'validation.json')['kind'] == 'SAVED_EVIDENCE_IDENTITY_ONLY'
    assert read(d.state/'validation.json')['execution_performed'] is False
    assert 'Stock-take awaiting operator review' in (d.root/analysis_driver.PROFILE/'STATE.md').read_text()
    assert 'Calls: 4/8' in (d.state/'REPORT.md').read_text()
    assert not d.store.db.execute('SELECT 1 FROM manual_packages').fetchone()


def test_both_roles_read_the_same_registered_view(analysis_lane):
    d = analysis_lane; seen = []
    def model(work, stage, clients, expected):
        measurement = read(work/'input-measurement.json')
        actual = [(row['sha256'], digest((work/row['path']).read_bytes())) for row in measurement['private_scientific_views']]
        assert all(a == b for a, b in actual)
        seen.append((stage, actual))
        return fake_model(work, stage, clients, expected)
    d.runner = model
    for _ in range(7):
        assert d.advance()['phase'] != 'BLOCKED'
    assert len(seen) == 4 and all(x[1] == seen[0][1] for x in seen)


@pytest.mark.parametrize('path', ['view.txt', 'BACKLOG.md', 'operator.txt', 'backlog-binding.json'])
def test_changed_evidence_or_authority_refuses_without_charge(analysis_lane, path):
    d = analysis_lane
    with private_records.open_file(d.context/path, 'ab') as stream:
        stream.write(b' changed')
    result = d.advance()
    assert result['phase'] == 'BLOCKED' and result['calls_used'] == 0
    assert not d.store.batch.db.execute('SELECT 1 FROM autonomy_calls').fetchone()


def test_uncertain_author_blocks_without_duplicate_call(analysis_lane):
    d = analysis_lane
    def failed(*args):
        raise OSError('Synthetic transport uncertainty')
    d.runner = failed
    assert d.advance()['phase'] == 'BLOCKED'
    assert d.advance()['calls_used'] == 1
    assert d.store.batch.db.execute('SELECT status FROM autonomy_calls').fetchone()[0] == 'UNCERTAIN'


def test_second_review_blocker_stops_with_original_judgments(analysis_lane):
    d = analysis_lane
    def model(work, stage, clients, expected):
        if stage.endswith('review'):
            private_records.write_text(work/'review.json', json.dumps({'verdict': 'REVISE', 'rationale': 'BLOCKER[metric/statistic] Synthetic uncertainty remains.'}))
            return {'synthetic': True}
        return fake_model(work, stage, clients, expected)
    d.runner = model
    for phase in ['run_spec_review', 'run_spec_author', 'run_spec_review', 'BLOCKED']:
        result = d.advance(); assert result['phase'] == phase, result
    assert d.advance()['calls_used'] == 4
    assert 'UNRESOLVED_REVIEW_BLOCKER' in (d.state/'DECISION_REQUEST.md').read_text()
    findings = read(d.context/analysis_driver.PROFILE/'obligations.json')['obligations']
    assert len([x for x in findings if x['id'].startswith('STEPD-') and x['status'] == 'open']) == 2


@pytest.mark.parametrize('phase', ['EXECUTE_CPU', 'EXECUTE_MODAL', 'EMIT_PACKAGE', 'WAIT_OUTPUTS'])
def test_no_execution_transition_can_be_injected(analysis_lane, phase):
    d = analysis_lane; value = d.current(); value['phase'] = phase; d.save(value)
    result = d.advance()
    assert result['phase'] == 'BLOCKED' and result['calls_used'] == 0
    assert 'ANALYSIS_PHASE_HAS_NO_AUTHORIZED_TRANSITION' in result['reason']


def test_nonstop_next_decision_cannot_start_proposal_or_experiment(analysis_lane):
    d = analysis_lane
    for _ in range(3):
        d.advance()
    def model(work, stage, clients, expected):
        result = fake_model(work, stage, clients, expected)
        proposal = read(work/'investigator_next_decision.json')
        proposal.update(proposed_action_type='analysis', action='Start next proposal', charter_basis='Synthetic')
        private_records.write_text(work/'investigator_next_decision.json', json.dumps(proposal))
        return result
    d.runner = model
    result = d.advance()
    assert result['phase'] == 'BLOCKED' and result['calls_used'] == 3
    assert 'STOCKTAKE_OPERATOR_REVIEW_STOP_REQUIRED' in result['reason']
    assert d.advance()['calls_used'] == 3


def test_plan_validation_uses_actual_context_and_rejects_execution_fields(analysis_lane):
    d = analysis_lane; plan = read(d.state/'preparation-plan.json')
    assert analysis_driver.verify_plan(plan)[1].number == 1
    plan['executor'] = 'modal'
    with pytest.raises(ValueError, match='^ANALYSIS_PLAN_FIELDS$'):
        analysis_driver.verify_plan(plan)


def test_no_direct_assembly_or_executor_in_analysis_driver():
    tree = ast.parse((ROOT/'orchestrator/analysis_driver.py').read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in {'assemble', 'submit', 'create_sandbox', 'launch'}
            if node.func.attr == 'execute':
                # SQLite accounting queries are required; executor dispatch is
                # not. Require the actual database receiver, not a name match.
                assert isinstance(node.func.value, ast.Attribute) and node.func.value.attr == 'db'
    assert 'manual_context.prepare' in (ROOT/'orchestrator/analysis_driver.py').read_text()


@pytest.mark.parametrize('key,value', [('item_number', 2), ('idea_ids', ['sprint13-proposal']),
                                     ('private_intake', {'path': 'other.json', 'sha256': '0'*64})])
def test_config_cannot_substitute_unreviewed_scope(analysis_lane, key, value):
    d = analysis_lane; d.config[key] = value
    result = d.advance()
    assert result['phase'] == 'BLOCKED' and result['calls_used'] == 0
    assert 'ANALYSIS_CONFIG_PLAN_MISMATCH' in result['reason']


def test_finding_reconciliation_is_idempotent_and_conflict_refuses(analysis_lane):
    d = analysis_lane
    raw = b'{"verdict":"REVISE","rationale":"BLOCKER[metric/statistic] synthetic"}'
    d.criticism('run_spec_review', 1, raw)
    before = (d.context/analysis_driver.PROFILE/'obligations.json').read_bytes()
    d.criticism('run_spec_review', 1, raw)
    assert (d.context/analysis_driver.PROFILE/'obligations.json').read_bytes() == before
    with pytest.raises(ValueError, match='^EXISTING_FINDING_CONFLICT$'):
        d.criticism('run_spec_review', 1, raw.replace(b'synthetic', b'altered'))


@pytest.mark.parametrize('ideas', [[], None, 'sprints-stocktake'])
def test_malformed_target_refuses_as_plan_error(analysis_lane, ideas):
    plan = read(analysis_lane.state/'preparation-plan.json'); plan['idea_ids'] = ideas
    with pytest.raises(ValueError, match='^STOCKTAKE_ONLY_NO_SUCCESSOR_AUTHORITY$'):
        analysis_driver.verify_plan(plan)


@pytest.fixture
def initialization(analysis_lane, monkeypatch):
    from orchestrator import autonomy_review, manual_stage
    d = analysis_lane
    # Exact candidate release files and profile, not a partial initialized-lane
    # imitation. Only context, native outputs, and review/client verification
    # are synthetic. No installed release or preserved record is modified.
    names = sorted(set(analysis_driver.git(ROOT, 'ls-files', 'orchestrator/*.py',
        'scout.py', 'docs/AUTONOMY_BATCH_2026-09-27.md', analysis_driver.PROFILE).splitlines()))
    expected = {name: digest((ROOT/name).read_bytes()) for name in names}
    for name in names:
        private_records.mkdir((d.root/name).parent, parents=True, exist_ok=True)
        private_records.write_bytes(d.root/name, (ROOT/name).read_bytes())
    assert {name: digest((d.root/name).read_bytes()) for name in names} == expected
    profile, engine = analysis_driver.release_identities(d.root)
    assert profile and engine['scout.py'] == expected['scout.py']
    assert all(expected[name] == pin for name, pin in {**profile, **engine}.items())
    analysis_driver.verify_plan(read(d.state/'preparation-plan.json'))
    # Normalize only the inherited synthetic checkout, including its Git files.
    private_copied_fixture(d.root)
    with private_records.umask():
        subprocess.run(['git', 'add', '.'], cwd=d.root, check=True)
        subprocess.run(['git', 'commit', '-qm', 'Exact candidate release; synthetic context and verifier fixture'], cwd=d.root, check=True)
    for path in [d.root, *d.root.rglob('*')]:
        if not path.is_symlink():
            private_records.check(path)
    review = d.state/'qualified-fixture'/'review.md'
    private_records.write_text(review, 'Synthetic review evidence; never a genuine approval.')
    runtime = d.state/'runtime.json'
    private_records.write_text(runtime, '{"denied_paths": []}\n')
    monkeypatch.setenv('RESEARCH_MANUAL_RUNTIME_CONFIG', str(runtime))
    receipt = {'verdict': 'APPROVE', 'source_sha': analysis_driver.git(d.root, 'rev-parse', 'HEAD'),
               'report_sha256': digest(review.read_bytes()),
               'runtime_sha256': autonomy_review.sha(runtime.read_bytes())}
    # Exercise the actual two hash conventions rather than forcing equality.
    assert receipt['runtime_sha256'] != manual_runtime.identity()
    atomic(review.parent/'packet-manifest.json', {'files': {
        'evidence/analysis-plan.json': digest((d.state/'preparation-plan.json').read_bytes())}})
    monkeypatch.setattr(autonomy_review, 'verify_result', lambda folder: receipt)
    monkeypatch.setattr(manual_stage, 'preflight', lambda: {'synthetic': True})
    return d, review, receipt


def test_initialization_binds_review_plan_and_single_global_owner(initialization):
    d, review, _ = initialization
    d.store.batch.complete_run(d.config['run_id'], {'synthetic': True})
    target = d.state/'new-analysis'
    result = analysis_driver.initialize(d.root, target, review, d.state/'preparation-plan.json')
    assert result['call_limit'] == 8 and result['calls_used'] == 0
    config = read(target/'lane.json')
    assert config['private_intake'] == d.config['private_intake']
    assert read(config['owner_path']) == config['owner_binding']
    with pytest.raises(ValueError, match='^EXISTING_ANALYSIS_OWNER_NO_NEW_ALLOWANCE$'):
        analysis_driver.initialize(d.root, d.state/'duplicate', review, d.state/'preparation-plan.json')
    assert not (d.state/'duplicate').exists()


def test_existing_active_run_refuses_before_new_state_or_owner(initialization):
    d, review, _ = initialization
    with pytest.raises(ValueError, match='^ONE_ACTIVE_RESEARCH_RUN$'):
        analysis_driver.initialize(d.root, d.state/'new-analysis', review, d.state/'preparation-plan.json')
    assert not (d.state/'new-analysis').exists()
    assert not list((d.root/'.git').glob('analysis-owner-*'))


@pytest.mark.parametrize('field,bad', [('verdict', 'REQUEST_CHANGES'), ('source_sha', '0'*40),
                                    ('report_sha256', '0'*64), ('runtime_sha256', 'different')])
def test_initialization_cannot_self_qualify_review(initialization, field, bad):
    d, review, receipt = initialization; receipt[field] = bad
    with pytest.raises(ValueError, match='^QUALIFIED_EXACT_ENGINE_APPROVAL_REQUIRED$'):
        analysis_driver.initialize(d.root, d.state/'new-analysis', review, d.state/'preparation-plan.json')
    assert not (d.state/'new-analysis').exists()


def test_unreviewed_plan_refuses_before_allowance(initialization):
    d, review, _ = initialization
    atomic(review.parent/'packet-manifest.json', {'files': {'evidence/analysis-plan.json': '0'*64}})
    with pytest.raises(ValueError, match='^REVIEWED_ANALYSIS_PLAN_REQUIRED$'):
        analysis_driver.initialize(d.root, d.state/'new-analysis', review, d.state/'preparation-plan.json')
    assert not (d.state/'new-analysis').exists()


@pytest.mark.parametrize('runtime_path', [None, 'relative-runtime.json'])
def test_initializer_requires_explicit_runtime_before_owner(initialization, monkeypatch, runtime_path):
    d, review, _ = initialization
    if runtime_path is None:
        monkeypatch.delenv('RESEARCH_MANUAL_RUNTIME_CONFIG')
    else:
        monkeypatch.setenv('RESEARCH_MANUAL_RUNTIME_CONFIG', runtime_path)
    target = d.state/'new-analysis'
    with pytest.raises(ValueError, match='^EXPLICIT_REVIEWED_RUNTIME_CONFIG_REQUIRED$'):
        analysis_driver.initialize(d.root, target, review, d.state/'preparation-plan.json')
    assert not target.exists()
    assert not list((d.root/'.git').glob('analysis-owner-*'))


@pytest.mark.parametrize('change', ['bytes', 'missing'])
def test_initializer_refuses_runtime_file_drift_before_owner(initialization, change):
    d, review, _ = initialization
    runtime = d.state/'runtime.json'
    if change == 'bytes':
        # Even equivalent JSON with different bytes is outside exact review.
        private_records.write_text(runtime, '{ "denied_paths": [] }\n')
        error = ValueError
        match = '^QUALIFIED_EXACT_ENGINE_APPROVAL_REQUIRED$'
    else:
        runtime.unlink()
        error = FileNotFoundError
        match = 'runtime.json'
    target = d.state/'new-analysis'
    with pytest.raises(error, match=match):
        analysis_driver.initialize(d.root, target, review, d.state/'preparation-plan.json')
    assert not target.exists()
    assert not list((d.root/'.git').glob('analysis-owner-*'))


@pytest.fixture
def item2_lane(analysis_lane, monkeypatch):
    """Synthetic scope/transport fixture; completed-host proof is separately tested
    with real SQLite in test_completed_run and the private installed-state rehearsal."""
    from orchestrator import completed_run
    d = analysis_lane
    plan = read(d.state/'preparation-plan.json')
    authority = (ROOT/'docs/CONNECTIONS_OPERATOR_APPROVAL.txt').read_bytes()
    private_records.write_bytes(d.context/'operator.txt', authority)
    plan['operator']['sha256'] = digest(authority)
    binding = read(d.context/'backlog-binding.json')
    binding['operator_sha256'] = digest(authority)
    binding['items'][0]['state'] = 'AUTHORIZED'
    binding['items'][1]['state'] = 'AUTHORIZED'
    private_records.write_text(d.context/'backlog-binding.json', json.dumps(binding))
    plan['backlog_binding']['sha256'] = digest((d.context/'backlog-binding.json').read_bytes())
    registry = read(d.context/'registry.json')
    registry.update(task='sprint13-proposal', idea_ids=['sprint13-proposal'])
    private_records.write_text(d.context/'registry.json', json.dumps(registry))
    plan['private_intake']['sha256'] = digest((d.context/'registry.json').read_bytes())
    report = b'Synthetic accepted stocktake: aggregate finding retained exactly.'
    private_records.write_bytes(d.context/'accepted.md', report)
    review = {'status': 'REVIEWED_BY_OPERATOR', 'stocktake_run': completed_run.RUN,
              'accepted_report_sha256': digest(report)}
    private_records.write_text(d.context/'operator-review.json', json.dumps(review))
    plan.update(item_number=2, item_sha256=binding['items'][1]['sha256'], idea_ids=['sprint13-proposal'],
        accepted_stocktake={'run_id': completed_run.RUN, 'report': {'path': 'accepted.md', 'sha256': digest(report)},
            'operator_review': {'path': 'operator-review.json', 'sha256': digest((d.context/'operator-review.json').read_bytes())}},
        artifacts=[{'id': 'operator-accepted-stocktake', 'type': 'prior_results', 'version': 1,
                    'path': 'accepted.md', 'sha256': digest(report)}])
    private_copied_fixture(d.context)
    plan['context_files'] = {str(p.relative_to(d.context)): digest(p.read_bytes()) for p in d.context.rglob('*') if p.is_file()}
    atomic(d.state/'preparation-plan.json', plan)
    for key in ('operator','backlog_binding','private_intake','item_number','item_sha256','idea_ids','accepted_stocktake'):
        d.config[key] = plan[key]
    d.config['clients']['runtime_config_sha256']='e'*64  # explicit synthetic binding, no native runtime
    d.config.update(review_contract='bound-review/v1', plan_sha256=digest((d.state/'preparation-plan.json').read_bytes()))
    atomic(d.state/'lane.json', d.config)
    value=d.current(); value['artifacts']=plan['artifacts'];d.save(value)
    monkeypatch.setattr(completed_run, 'validate', lambda: {'synthetic_host_closure': True})
    def model(work, stage, clients, expected):
        measurement=read(work/'input-measurement.json')
        delivered=[x for x in measurement['workspace_files'] if x.get('id')=='operator-accepted-stocktake']
        assert len(delivered)==1 and (work/delivered[0]['path']).read_bytes()==report
        assert delivered[0]['sha256']==digest(report)
        assert report.decode() not in (work/'prompt.md').read_text()
        if stage.endswith('review'):
            private_records.write_text(work/'review.json', json.dumps({'verdict':'APPROVE','findings':[],
                'rationale':'Synthetic approval. Prose example BLOCKER[metric/statistic] has no authority.'}))
            return {'synthetic':True}
        return fake_model(work,stage,clients,expected)
    d.runner=model
    return d


def test_item2_four_connections_deliver_accepted_report_and_stop(item2_lane):
    d=item2_lane
    assert analysis_driver.verify_plan(read(d.state/'preparation-plan.json'))[1].number == 2
    for phase in ['run_spec_review','COMMIT_SPEC','result_interpretation_author','result_interpretation_review','UPDATE_STATE','REPORT','COMPLETE']:
        result=d.advance();assert result['phase']==phase,result
    assert d.status()['calls_used']==4
    assert d.current()['operator_review_pending'] is True
    assert not (d.state/'package').exists()
    assert not d.store.db.execute('SELECT 1 FROM manual_packages').fetchone()


@pytest.mark.parametrize('change',['absent','wrong-type','superseded'])
def test_item2_bound_but_undelivered_report_refuses(item2_lane,change):
    d=item2_lane;plan=read(d.state/'preparation-plan.json')
    if change=='absent':plan['artifacts']=[]
    elif change=='wrong-type':plan['artifacts'][0]['type']='interpretation'
    else:plan['artifacts'].append({**plan['artifacts'][0],'version':2,'path':'operator.txt','sha256':plan['operator']['sha256']})
    with pytest.raises(ValueError,match='ITEM2_ACCEPTED_STOCKTAKE_DELIVERY_REQUIRED'):
        analysis_driver.verify_plan(plan)
    assert d.status()['calls_used']==0


@pytest.mark.parametrize('verdict,findings', [('REJECT', []), ('REVISE', []), ('APPROVE', [
    {'id':'f1','category':'metric/statistic','text':'Synthetic finding','evidence':'fixture','resolution':'repair'}])])
def test_item2_any_structured_finding_or_negative_verdict_stops(item2_lane,verdict,findings):
    d=item2_lane;assert d.advance()['phase']=='run_spec_review'
    def model(work,*args):
        private_records.write_text(work/'review.json',json.dumps({'verdict':verdict,'findings':findings,'rationale':'Synthetic'}))
        return {'synthetic':True}
    d.runner=model
    assert d.advance()['phase']=='BLOCKED'
    assert d.advance()['calls_used']==2


def test_generated_artifacts_do_not_collide_with_preserved_predecessor(analysis_lane):
    """Real driver, context assembly and ledger; only native model output is synthetic."""
    d = analysis_lane
    originals = {}
    for name in ['ANALYSIS-SPEC-1.md', 'intake-validation.json',
                 'interpretation-1.md', 'next-decision-1.json']:
        path = d.context/'current'/name
        private_records.write_text(path, 'Preserved predecessor: '+name)
        originals[path] = path.read_bytes()
    for phase in ['run_spec_review', 'COMMIT_SPEC', 'result_interpretation_author',
                  'result_interpretation_review', 'UPDATE_STATE', 'REPORT', 'COMPLETE']:
        result = d.advance()
        assert result['phase'] == phase, result
    assert {path: path.read_bytes() for path in originals} == originals
    prefix = 'current/runs/'+digest(d.config['run_id'].encode())+'/'
    assert all(row['path'].startswith(prefix) for row in d.current()['artifacts'])
    assert d.status()['calls_used'] == 4
    assert d.advance()['calls_used'] == 4


def test_run_namespace_preserves_same_run_immutable_refusal(analysis_lane):
    d = analysis_lane; value = d.current()
    raw = b'Synthetic immutable output.'
    d.artifact(value, 'run_spec', 'SPEC-1.md', raw, 1)
    first = dict(value['artifacts'][-1])
    d.artifact(value, 'proposed_run_spec', 'SPEC-1.md', raw, 1)
    assert value['artifacts'][-1]['path'] == first['path']
    with pytest.raises(ValueError, match='^IMMUTABLE_ARTIFACT_CONFLICT$'):
        d.artifact(value, 'run_spec', 'SPEC-1.md', b'Changed output.', 1)
    assert (d.context/first['path']).read_bytes() == raw
    d.config['run_id'] += '-distinct'
    d.artifact(value, 'run_spec', 'SPEC-1.md', b'Distinct run output.', 1)
    assert value['artifacts'][-1]['path'] != first['path']
    assert (d.context/first['path']).read_bytes() == raw
    assert d.status()['calls_used'] == 0


def test_saved_completed_author_requalifies_without_another_call(analysis_lane, monkeypatch):
    """Reproduce the old path defect with synthetic native output, then use real acceptance."""
    from orchestrator.manual_driver import write_once
    d = analysis_lane
    old_path = d.context/'current/ANALYSIS-SPEC-1.md'
    private_records.write_bytes(old_path, b'Immutable predecessor specification.')
    def old_recorder(value, kind, name, raw, version):
        write_once(d.context/'current'/name, raw)
    with monkeypatch.context() as patch:
        patch.setattr(d, 'artifact', old_recorder)
        result = d.advance()
    assert result['phase'] == 'BLOCKED'
    assert result['reason'] == 'OUTPUT_VALIDATION_REFUSED: IMMUTABLE_ARTIFACT_CONFLICT'
    pending = d.current()['pending']
    before = [tuple(row) for row in d.store.db.execute('SELECT * FROM manual_calls')]
    charges = [tuple(row) for row in d.store.batch.db.execute('SELECT * FROM autonomy_calls')]
    assert len(before) == len(charges) == 1
    assert d.store.db.execute('SELECT status FROM manual_calls').fetchone()[0] == 'COMPLETE'
    raw = (Path(pending['workspace'])/'SPEC.proposed.md').read_bytes()
    def forbidden(*args, **kwargs):
        pytest.fail('Requalification must not launch a model')
    d.runner = forbidden
    assert d.accept_completed(d.current())['phase'] == 'run_spec_review'
    assert [tuple(row) for row in d.store.db.execute('SELECT * FROM manual_calls')] == before
    assert [tuple(row) for row in d.store.batch.db.execute('SELECT * FROM autonomy_calls')] == charges
    assert (Path(pending['workspace'])/'SPEC.proposed.md').read_bytes() == raw
    assert old_path.read_bytes() == b'Immutable predecessor specification.'
    assert 'pending' not in d.current()
    with pytest.raises(KeyError):
        d.accept_completed(d.current())
    assert d.status()['calls_used'] == 1


@pytest.mark.parametrize('branch',['astra/workstream-b-aggregate-20261010','astra/manual-BAD','main'])
def test_init_rejects_local_accounting_branch_before_owner_or_allowance(initialization,branch):
    d,review,_=initialization
    subprocess.run(['git','checkout','-qb',branch],cwd=d.root,check=True)
    before=[tuple(r) for r in d.store.batch.db.execute('SELECT * FROM autonomy_runs')]
    target=d.state/'new-analysis'
    with pytest.raises(ValueError,match='^MANUAL_ACCOUNTING_BRANCH_REQUIRED$'):
        analysis_driver.initialize(d.root,target,review,d.state/'preparation-plan.json')
    assert not target.exists() and not list((d.root/'.git').glob('analysis-owner-*'))
    assert [tuple(r) for r in d.store.batch.db.execute('SELECT * FROM autonomy_runs')]==before
    assert not d.store.batch.db.execute('SELECT 1 FROM autonomy_calls').fetchone()


def test_real_initialize_then_both_ledgers_reserve_uses_same_branch_contract(initialization):
    from orchestrator.manual_executor import ManualExecutor
    d,review,_=initialization
    d.store.batch.complete_run(d.config['run_id'],{'synthetic':True})
    target=d.state/'new-analysis'
    result=analysis_driver.initialize(d.root,target,review,d.state/'preparation-plan.json')
    config=read(target/'lane.json')
    assert result['calls_used']==0
    assert re.fullmatch(r'astra/manual-[a-z0-9-]+',config['branch'])
    batch=BatchAccounts(config['batch_ledger']);store=ManualExecutor(target/'jobs.sqlite',batch=batch)
    try:
        ident,n,receipt=store.reserve_call(config['run_id'],'run_spec_author',config['source'],config['branch'],config['policy'],{'synthetic':True})
        assert n==1 and receipt['accounting']['status']=='ADMITTED'
        assert store.db.execute('SELECT status FROM manual_calls WHERE id=?',(ident,)).fetchone()[0]=='RUNNING'
        assert batch.db.execute('SELECT status FROM autonomy_calls WHERE id=?',(ident,)).fetchone()[0]=='RUNNING'
        account=json.loads(store.db.execute('SELECT payload FROM manual_account WHERE id=1').fetchone()[0])
        assert account['count']==1 and len(account['events'])==1
        assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==1
    finally:store.db.close();batch.db.close()
