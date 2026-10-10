"""Exact October 10 aggregate synthesis lane; no execution or new admission allowance."""
import json
from pathlib import Path

from orchestrator import autonomy_backlog, context_budget, scientific_intake
from orchestrator.manual_executor import digest

DOCUMENT = 'docs/PARALLEL_RESEARCH_OPERATOR_DECISION_20261010.txt'
AUTHORITY = '644410e1659c8998040c3cc9035aaa0eb2c5c3708fba37cfbb1a91fadf9f00e6'
TASK = 'sprint13b-execution'
SCHEMA = 'parallel-aggregate-analysis/v1'


def authority(root=None):
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    if digest(context_budget.relative_file(root, DOCUMENT).read_bytes()) != AUTHORITY:
        raise ValueError('AGGREGATE_ANALYSIS_AUTHORITY_CHANGED')
    return AUTHORITY


def run_id(plan):
    return 'aggregate-' + digest((AUTHORITY + ':' + plan['private_intake']['sha256']).encode())[:24]


def validate(plan, backlog):
    authority()
    scope = plan.get('aggregate_analysis')
    if (not isinstance(scope, dict) or set(scope) != {'schema', 'operator', 'related_items'}
            or scope['schema'] != SCHEMA or plan.get('item_number') != 4
            or plan.get('idea_ids') != [TASK, 'post-result-synthesis-20261010']):
        raise ValueError('AGGREGATE_ANALYSIS_SCOPE')
    root = Path(plan['context'])
    ref = scope['operator']
    if (not isinstance(ref, dict) or set(ref) != {'path', 'sha256'} or ref['sha256'] != AUTHORITY
            or digest(context_budget.relative_file(root, ref['path']).read_bytes()) != AUTHORITY):
        raise ValueError('AGGREGATE_ANALYSIS_OPERATOR_BINDING')
    related = scope['related_items']
    if not isinstance(related, dict) or set(related) != {'4', '6'}:
        raise ValueError('AGGREGATE_ANALYSIS_RELATED_ITEMS')
    # Preserve the original BACKLOG modes and authority. This lane adds analysis,
    # never changes either item into an execution-authorized successor.
    for number, mode in ((4, 'gpu'), (6, 'cpu')):
        item = next((row for row in backlog.items if row.number == number), None)
        if (item is None or item.sha256 != related[str(number)] or item.mode != mode
                or item.state != 'AUTHORIZED'):
            raise ValueError('AGGREGATE_ANALYSIS_BACKLOG_BINDING')
    item = next(row for row in backlog.items if row.number == 4)
    if plan['item_sha256'] != item.sha256:
        raise ValueError('AGGREGATE_ANALYSIS_ITEM_CHANGED')
    registry_ref = plan['private_intake']
    raw = context_budget.relative_file(root, registry_ref['path']).read_bytes()
    if digest(raw) != registry_ref['sha256']:
        raise ValueError('AGGREGATE_ANALYSIS_INTAKE_CHANGED')
    registry = json.loads(raw)
    cases = scientific_intake.cohort(context_budget.relative_file(root, registry['cohort']).read_bytes())
    for stage in ('run_spec_author', 'run_spec_review', 'result_interpretation_author', 'result_interpretation_review'):
        views, _ = scientific_intake.load_views(root, registry_ref, stage=stage, idea_ids=plan['idea_ids'])
        if any(row.get('per_patient_material') for row in views):
            raise ValueError('AGGREGATE_ANALYSIS_NO_PATIENT_MATERIAL')
    for row in registry['views']:
        manifest = json.loads(context_budget.relative_file(root, row['manifest']).read_bytes())
        if manifest['per_patient_material']:
            raise ValueError('AGGREGATE_ANALYSIS_NO_PATIENT_MATERIAL')
        scientific_intake.scan(context_budget.relative_file(root, row['path']).read_bytes(), cases,
                               kind='aggregate', reason='Aggregate-only synthesis')
    for row in plan['artifacts']:
        scientific_intake.scan(context_budget.relative_file(root, row['path']).read_bytes(), cases,
                               kind='aggregate', reason='Aggregate-only synthesis artifact')
    return item


def preflight(batch, run, binding):
    """Reuse owner identity checks; active item4 may coexist, no call concurrency."""
    from orchestrator.experiment_context import ITEM4_RUN
    from orchestrator.modal_item4_policy import AUTHORITY as ITEM4_AUTHORITY
    from orchestrator import private_records
    from tools.deploy_manual_lane import bound
    if (batch.folder/'HALT').exists():
        raise ValueError('AUTONOMY_BATCH_HALTED')
    if batch.db.execute('SELECT 1 FROM autonomy_runs WHERE id=?', (run,)).fetchone():
        raise ValueError('EXISTING_ANALYSIS_OWNER_NO_NEW_ALLOWANCE')
    from orchestrator.analysis_driver import preparation_scope
    selected = preparation_scope(binding)
    key = 'aggregate_analysis' if 'aggregate_analysis' in binding else 'colab_preparation'
    if (selected is None or set(binding) != {'state', 'source', 'run_id', 'plan_sha256', 'review_sha256', key}
            or binding['run_id'] != run or not Path(binding['state']).is_absolute()):
        raise ValueError('AGGREGATE_ANALYSIS_OWNER_BINDING')
    state = bound(batch.filesystem_root, binding['state'])
    raw = private_records.check(state/'preparation-plan.json').read_bytes()
    plan = json.loads(raw)
    if (digest(raw) != binding['plan_sha256'] or plan.get(key) != binding[key]
            or preparation_scope(plan) is not selected or selected.run_id(plan) != run):
        raise ValueError('AGGREGATE_ANALYSIS_OWNER_PLAN')
    # verify_plan authenticates all inputs, authority and aggregate-only scope.
    from orchestrator.analysis_driver import verify_plan
    verify_plan(plan)
    active = batch.db.execute("SELECT * FROM autonomy_runs WHERE status!='COMPLETE'").fetchall()
    if len(active) > 2: raise ValueError('ONE_ACTIVE_RESEARCH_RUN')
    for row in active:
        owner = json.loads(row['binding'])
        other = preparation_scope(owner)
        if row['status'] != 'ACTIVE' or (row['id'] != ITEM4_RUN and (other is None or other is selected)):
            raise ValueError('ONE_ACTIVE_RESEARCH_RUN')
        old_state = bound(batch.filesystem_root, owner['state'])
        config = json.loads(private_records.check(old_state/'lane.json').read_bytes())
        original = private_records.check(old_state/'preparation-plan.json').read_bytes()
        if other:
            old_plan = json.loads(original)
            other_key = 'aggregate_analysis' if 'aggregate_analysis' in owner else 'colab_preparation'
            if (other.run_id(old_plan) != row['id'] or config.get('owner_binding') != owner
                    or config.get('run_id') != row['id'] or config.get('plan_sha256') != digest(original)
                    or owner.get('plan_sha256') != digest(original)
                    or config.get(other_key) != old_plan.get(other_key) or owner.get(other_key) != old_plan.get(other_key)
                    or preparation_scope(old_plan) is not other):
                raise ValueError('AGGREGATE_ANALYSIS_PARALLEL_OWNER_CHANGED')
            verify_plan({**old_plan, 'context': config['context']})
            continue
        scope = owner.get('execution_scope')
        if (not isinstance(scope, dict) or scope.get('schema') != 'scientific-execution/v1'
                or set(scope) != {'schema','item_number','run_id','authority_sha256','plan_sha256'}
                or type(scope.get('item_number')) is not int or scope.get('item_number') != 4 or scope.get('run_id') != ITEM4_RUN
                or scope.get('authority_sha256') != ITEM4_AUTHORITY
                or json.loads(original).get('execution_scope') != scope
                or json.loads(original).get('execution_plan', {}).get('sha256') != scope.get('plan_sha256')
                or config.get('owner_binding') != owner or config.get('execution_scope') != scope
                or config.get('run_id') != row['id'] or config.get('plan_sha256') != digest(original)
                or owner.get('plan_sha256') != digest(original)):
            raise ValueError('AGGREGATE_ANALYSIS_PARALLEL_OWNER_CHANGED')


def register(batch, run, binding):
    batch.db.execute('BEGIN IMMEDIATE')
    try:
        preflight(batch, run, binding)
        batch.db.execute("INSERT INTO autonomy_runs VALUES(?,?,'ACTIVE')", (run, json.dumps(binding, sort_keys=True)))
        batch.db.execute('COMMIT')
    except BaseException:
        batch.db.execute('ROLLBACK')
        raise


def instructions(stage, plan):
    text = ('Analyze preserved aggregate results for item6, three hardware benchmarks, two smoke runs, '
        'operator Sprint13A and Sprint14; retain original attribution and acceptance status. '
        'The goal is understanding. Explain proposed ideas through biology, mathematics or computer science; '
        'state mechanism and discriminating test. Dissect gains by placement versus amount, infarct size, '
        'region and fragmentation where evidence permits; explicitly mark unavailable evidence. '
        'Do not drop a strong model merely because its mechanism is unclear. Compare supporting and opposing '
        'evidence and propose cheapest informative tests. Parked operator ideas are attributed proposals, '
        'not facts or privileged conclusions. All findings at once; cite exact evidence and preserve disagreement. '
        'Plan a private visual case review with a selection rule fixed before case inspection, development patients '
        'only; list required admission CT, follow-up MRI, reference/predicted masks and clinical information. '
        'Planning only: no patient reads, notebooks, experiments, provider jobs or successor dispatch. '
        'Conclusions and code belong to the scientific roles; no claim of acceptance before independent review. ')
    if stage.startswith('run_spec'):
        text += ('Write/review substantive concise synthesis, evidence-backed ranked hypotheses and a fixed case-selection proposal NOW in SPEC.proposed.md, not only a plan for later thought. Keep it at most12000characters with exact binding lines:\nrun_id: '
                 + run_id(plan) + '\nanalysis_registry_sha256: ' + plan['private_intake']['sha256'] + '\n')
    else:
        text += 'Return reviewed analysis and proposed ideas; next decision must be stop, not execution authority. '
    return text
