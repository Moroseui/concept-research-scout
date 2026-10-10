"""Operator-backlog analysis using the existing four scientific roles.

There is no executor, Colab package, GPU provider or successor dispatch here.
The analysis specification is reviewed, preserved evidence is authenticated,
then interpretation is independently reviewed and returned to the operator.
Native transport/accounting/uncertainty/format handling come from Driver.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

from orchestrator import autonomy_backlog, context_budget, manual_context, manual_stage, private_records
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.manual_driver import Driver, STAGES, PROFILE, CATEGORIES, git, stamp, write_once
from orchestrator.manual_executor import ManualExecutor, read, digest, atomic
from orchestrator.git_publication import scan
from orchestrator.scientific_intake import load_views


def bound_file(root, ref):
    if not isinstance(ref, dict) or set(ref) != {'path', 'sha256'}:
        raise ValueError('ANALYSIS_FILE_BINDING_REQUIRED')
    raw = context_budget.relative_file(root, ref['path']).read_bytes()
    if digest(raw) != ref['sha256']:
        raise ValueError('ANALYSIS_BOUND_FILE_CHANGED')
    return raw


def preparation_scope(plan):
    keys = [key for key in ('aggregate_analysis', 'colab_preparation') if key in plan]
    if len(keys) > 1: raise ValueError('ONE_PREPARATION_SCOPE_REQUIRED')
    if not keys: return None
    if keys[0] == 'aggregate_analysis':
        from orchestrator import aggregate_analysis_scope
        return aggregate_analysis_scope
    from orchestrator import colab_preparation_scope
    return colab_preparation_scope


def verify_plan(plan):
    fields = {'schema', 'context', 'context_files', 'backlog', 'backlog_binding', 'operator',
              'item_number', 'item_sha256', 'private_intake', 'idea_ids', 'artifacts', 'batch_ledger'}
    scoped = preparation_scope(plan) if isinstance(plan, dict) else None
    if scoped:
        fields = fields | ({'aggregate_analysis'} if 'aggregate_analysis' in plan else {'colab_preparation', 'notebook_revision'})
    if isinstance(plan,dict) and plan.get('item_number') in (2,5):
        fields=fields|{'accepted_stocktake'}
        if plan['item_number']==5: fields=fields|{'directions'}
        elif 'notebook_revision' in plan: fields=fields|{'notebook_revision'}
    if not isinstance(plan, dict) or set(plan) != fields or plan['schema'] != 'stocktake-analysis/v1':
        raise ValueError('ANALYSIS_PLAN_FIELDS')
    scopes={1:'sprints-stocktake',2:'sprint13-proposal',5:'research-directions'}
    if scoped: scopes[4] = 'sprint13b-execution'
    if (type(plan['item_number']) is not int or plan['item_number'] not in scopes
            or not isinstance(plan['idea_ids'],list) or not plan['idea_ids']
            or plan['idea_ids'][0]!=scopes[plan['item_number']]):
        raise ValueError('STOCKTAKE_ONLY_NO_SUCCESSOR_AUTHORITY')
    root = Path(plan['context'])
    observed = {str(p.relative_to(root)): digest(p.read_bytes()) for p in root.rglob('*') if p.is_file()}
    if observed != plan['context_files'] or any(p.is_symlink() for p in [root, *root.rglob('*')]):
        raise ValueError('ANALYSIS_CONTEXT_INVENTORY_CHANGED')
    if 'notebook_revision' in plan:
        if 'colab_preparation' in plan:
            scoped.validate_notebook_config(root, plan['notebook_revision'])
        else:
            from orchestrator.notebook_revision import validate_config
            validate_config(root, plan['notebook_revision'])
    raw = bound_file(root, plan['backlog'])
    authority = bound_file(root, plan['operator'])
    if plan['item_number'] in (2,5):
        from orchestrator.completed_run import AUTHORITY,RUN
        accepted=plan['accepted_stocktake']
        if set(accepted)!={'run_id','report','operator_review'} or accepted['run_id']!=RUN or (plan['item_number']==2 and digest(authority)!=AUTHORITY):
            raise ValueError('ITEM2_OPERATOR_RELEASE_REQUIRED')
        report=bound_file(root,accepted['report'])
        review=json.loads(bound_file(root,accepted['operator_review']))
        if (review.get('status')!='REVIEWED_BY_OPERATOR' or review.get('stocktake_run')!=RUN
                or review.get('accepted_report_sha256')!=digest(report)):
            raise ValueError('ITEM2_ACCEPTED_STOCKTAKE_REQUIRED')

    if plan['item_number']==5:
        from orchestrator.directions_analysis import validate_plan
        validate_plan(plan)
    binding = json.loads(bound_file(root, plan['backlog_binding']))
    backlog = autonomy_backlog.load(raw, binding, authority)
    if scoped:
        item = scoped.validate(plan, backlog)
    else:
        item = autonomy_backlog.require_item(backlog, plan['item_number'], plan['item_sha256'], 'analysis', completed_items=(1,2,3) if plan['item_number']==5 else (1,) if plan['item_number'] == 2 else ())
    # Validate actual views and ordinary artifacts before any owner or allowance
    # record is created. Workspace materialization happens only after preflight.
    load_views(root, plan['private_intake'], stage='run_spec_author', idea_ids=plan['idea_ids'])
    if plan['item_number'] in (2,5):
        registry=json.loads(bound_file(root,plan['private_intake']))
        for row in registry['views']:
            manifest=json.loads(bound_file(root,{'path':row['manifest'],'sha256':row['manifest_sha256']}))
            if manifest['per_patient_material']: raise ValueError('ITEM2_NO_PATIENT_LEVEL_MATERIAL')

    for artifact in plan['artifacts']:
        bound_file(root, {k: artifact[k] for k in ('path', 'sha256')})
    manual_context.selected_artifacts('run_spec_author', plan['artifacts'])
    if plan['item_number'] in (2,5):
        require_stocktake_delivery(plan['artifacts'], plan['accepted_stocktake']['report'])
    context_budget.load(root)
    return backlog, item


def require_stocktake_delivery(artifacts, report):
    # A binding somewhere in the context is not evidence delivered to a role.
    # Reuse prior_results, already selected by all four scientific stages.
    for stage in manual_context.STAGE_ARTIFACT_TYPES:
        selected = manual_context.selected_artifacts(stage, artifacts)
        matches = [row for row in selected if row['id'] == 'operator-accepted-stocktake'
                   and row['type'] == 'prior_results'
                   and {key: row[key] for key in ('path', 'sha256')} == report]
        if len(matches) != 1:
            raise ValueError('ITEM2_ACCEPTED_STOCKTAKE_DELIVERY_REQUIRED:' + stage)


def release_identities(root):
    """Read all release bindings before creating analysis state or an owner."""
    root = Path(root)
    required = ['scout.py', 'docs/AUTONOMY_BATCH_2026-09-27.md',
                'orchestrator/analysis_driver.py', 'orchestrator/manual_driver.py',
                'orchestrator/manual_stage.py', 'orchestrator/manual_executor.py',
                'orchestrator/autonomy_accounting.py', 'orchestrator/scientific_intake.py',
                'evidence/decisions.md', str(PROFILE / 'manifest.json')]
    for name in required:
        path = context_budget.relative_file(root, name)
        if not path.is_file():
            raise ValueError('ANALYSIS_RELEASE_FILE_REQUIRED:' + name)
    context_budget.load(root)
    profile = {str(p.relative_to(root)): digest(context_budget.relative_file(root, str(p.relative_to(root))).read_bytes())
               for p in (root/PROFILE).rglob('*') if p.is_file()}
    engine = {str(p.relative_to(root)): digest(context_budget.relative_file(root, str(p.relative_to(root))).read_bytes())
              for p in (root/'orchestrator').glob('*.py')}
    engine['scout.py'] = digest((root/'scout.py').read_bytes())
    return profile, engine


@private_records.private_umask
def initialize(root, state, engine_review, plan_path):
    """Create one new analysis allowance only for a qualified exact source.

    The protected preparation plan is an installation input, not model output.
    Its entire inventory and immutable backlog interpretation are recorded.
    The canonical run ID excludes source/review changes so a fresh checkout
    cannot silently create another allowance for the same operator item.
    """
    root, state, engine_review, plan_path = map(Path, (root, state, engine_review, plan_path))
    if state.exists() or state.is_symlink():
        raise ValueError('EXISTING_ANALYSIS_LANE_RECONCILE')
    if git(root, 'status', '--porcelain'):
        raise ValueError('CLEAN_REVIEWED_SOURCE_REQUIRED')
    source = git(root, 'rev-parse', 'HEAD'); branch = git(root, 'branch', '--show-current')
    if not branch.startswith('astra/'):
        raise ValueError('REVIEWED_WORK_BRANCH_REQUIRED')
    from orchestrator.autonomy_review import verify_result
    approved = verify_result(engine_review.parent)
    # Review packets bind the literal configuration file. The separately
    # derived native-client identity remains enforced by preflight()/clients.
    runtime_file = os.environ.get('RESEARCH_MANUAL_RUNTIME_CONFIG')
    if not runtime_file or not Path(runtime_file).is_absolute():
        raise ValueError('EXPLICIT_REVIEWED_RUNTIME_CONFIG_REQUIRED')
    runtime_sha256 = digest(Path(runtime_file).read_bytes())
    if (approved['verdict'] != 'APPROVE' or approved['source_sha'] != source
            or digest(engine_review.read_bytes()) != approved['report_sha256']
            or approved['runtime_sha256'] != runtime_sha256):
        raise ValueError('QUALIFIED_EXACT_ENGINE_APPROVAL_REQUIRED')
    plan_raw = plan_path.read_bytes(); plan = json.loads(plan_raw)
    review_manifest = read(engine_review.parent/'packet-manifest.json')
    plan_evidence = ('evidence/aggregate-analysis-plan.json' if 'aggregate_analysis' in plan else
                     'evidence/colab-preparation-plan.json' if 'colab_preparation' in plan else
                     'evidence/analysis-plan.json')
    if review_manifest['files'].get(plan_evidence) != digest(plan_raw):
        raise ValueError('REVIEWED_ANALYSIS_PLAN_REQUIRED')
    backlog, item = verify_plan(plan)
    if plan.get("notebook_revision") and not plan.get("colab_preparation"):
        raise ValueError("NOTEBOOK_SCOPE_USES_SAME_RUN_CONTINUATION_ONLY")
    if item.number in (2,5):
        from orchestrator.completed_run import validate as completed
        if completed() is None: raise ValueError('ITEM2_COMPLETED_RUN_CLOSURE_REQUIRED')

    authority_path = 'docs/AUTONOMY_BATCH_2026-09-27.md'
    authority_sha256 = digest((root/authority_path).read_bytes())
    profile_files, engine_files = release_identities(root)
    git(root, 'var', 'GIT_AUTHOR_IDENT'); git(root, 'var', 'GIT_COMMITTER_IDENT')
    clients = manual_stage.preflight()
    run_id = 'stocktake-' + digest((backlog.sha256 + ':' + item.sha256).encode())[:24]
    scoped = preparation_scope(plan)
    if scoped: run_id = scoped.run_id(plan)
    batch = BatchAccounts(plan['batch_ledger'])
    if item.number==5:
        from orchestrator.directions_analysis import require_item2_complete
        require_item2_complete(batch, Path(plan['context']), plan['directions'])
    if batch.db.execute('SELECT 1 FROM autonomy_runs WHERE id=?', (run_id,)).fetchone():
        raise ValueError('EXISTING_ANALYSIS_OWNER_NO_NEW_ALLOWANCE')
    if (batch.folder/'HALT').exists():
        raise ValueError('AUTONOMY_BATCH_HALTED')
    if not scoped and batch.db.execute("SELECT 1 FROM autonomy_runs WHERE status!='COMPLETE'").fetchone():
        raise ValueError('ONE_ACTIVE_RESEARCH_RUN')
    common = Path(git(root, 'rev-parse', '--git-common-dir'))
    common = common if common.is_absolute() else root/common
    owner = common.resolve()/('analysis-owner-' + run_id + '.json')
    if owner.exists():
        raise ValueError('EXISTING_ANALYSIS_OWNER_NO_NEW_ALLOWANCE')
    private_records.mkdir(state, parents=True)
    context = state/'context'
    private_records.copytree(plan['context'], context)
    private_records.write_bytes(state/'preparation-plan.json', plan_raw)
    # Owner creation and global registration precede allowance creation. Any
    # partial failure remains visible and refuses a fresh init; no blind retry.
    owner_binding = {'state': str(state.resolve()), 'source': source, 'run_id': run_id,
                     'plan_sha256': digest(plan_raw), 'review_sha256': digest(engine_review.read_bytes())}
    if scoped:
        key = 'aggregate_analysis' if 'aggregate_analysis' in plan else 'colab_preparation'
        owner_binding[key] = plan[key]
    write_once(owner, json.dumps(owner_binding, sort_keys=True).encode())
    if scoped:
        from orchestrator.aggregate_analysis_scope import register
        register(batch, run_id, owner_binding)
    else:
        batch.register_run(run_id, owner_binding)
    policy = {'status': 'RATIFIED', 'operator_approval': backlog.operator_sha256,
              'state_write_permission': 'OPERATOR_AUTHORIZED', 'n': 4, 'window': 'UTC_CALENDAR_DAY',
              'state_ref': 'refs/heads/automation/dispatch-state', 'manual_semantics': 'OPERATOR_STEP_D_MAX_EIGHT'}
    store = ManualExecutor(state/'jobs.sqlite', batch=batch); store.initialize_allowance(policy)
    config = {'backend': 'analysis', 'run_id': run_id, 'source': source, 'branch': branch,
              'root': str(root), 'context': str(context), 'batch_ledger': plan['batch_ledger'],
              'owner_path': str(owner), 'owner_binding': owner_binding,
              'engine_review': {'path': str(engine_review), 'sha256': digest(engine_review.read_bytes())},
              'authority_path': authority_path, 'authority_sha256': authority_sha256,
              'profile_files': profile_files, 'engine_files': engine_files,
              'private_intake': plan['private_intake'], 'idea_ids': plan['idea_ids'], 'clients': clients,
              'policy': policy, 'started_utc': stamp(), 'plan_sha256': digest(plan_raw),
              'backlog': plan['backlog'], 'backlog_binding': plan['backlog_binding'], 'operator': plan['operator'],
              'item_number': item.number, 'item_sha256': item.sha256,
              'workspace_root': str(state.parent/(state.name+'-scientific-workspaces'))}
    if scoped: config[key] = plan[key]
    if plan.get('colab_preparation'): config['notebook_revision'] = plan['notebook_revision']
    if item.number in (2,5):
        from orchestrator.analysis_revisions import POLICY
        config.update(review_contract='bound-review/v1',accepted_stocktake=plan['accepted_stocktake'],revision_policy=POLICY)
    if item.number==5: config['directions']=plan['directions']
    atomic(state/'lane.json', config)
    store.db.execute('INSERT INTO manual_state VALUES(1,?)', (json.dumps({'phase': STAGES[0], 'rounds': {},
        'artifacts': plan['artifacts'], 'interventions': []}),))
    store.db.close()
    return {'status': 'READY', 'run_id': run_id, 'next': STAGES[0], 'calls_used': 0, 'call_limit': 16 if item.number in (2,5) else 8}


class AnalysisDriver(Driver):
    def __init__(self, state, runner=None):
        self.state = Path(state); self.config = read(self.state/'lane.json')
        if self.config.get('backend') != 'analysis':
            raise ValueError('ANALYSIS_LANE_REQUIRED')
        self.root = Path(self.config['root']); self.context = Path(self.config['context'])
        from orchestrator.stocktake_recovery import ledger_folder
        self.store = ManualExecutor(self.state/'jobs.sqlite', batch=BatchAccounts(ledger_folder(self.config),
            filesystem_root=Path(self.config.get('artifact_filesystem_root',self.config.get('notebook_filesystem_root','/')))))
        self.runner = runner or manual_stage.invoke

    def guard(self):
        super().guard()
        if digest((self.state/'preparation-plan.json').read_bytes()) != self.config['plan_sha256']:
            raise ValueError('ANALYSIS_PLAN_CHANGED')
        plan = read(self.state/'preparation-plan.json')
        for key in ('private_intake', 'idea_ids', 'backlog', 'backlog_binding', 'operator',
                    'item_number', 'item_sha256', 'batch_ledger'):
            if self.config[key] != plan[key]:
                raise ValueError('ANALYSIS_CONFIG_PLAN_MISMATCH')
        # The initial artifacts are immutable preparation inputs. Later stage
        # artifacts are separately hash-bound to their genuine call receipts.
        for artifact in plan['artifacts']:
            bound_file(self.context, {k: artifact[k] for k in ('path', 'sha256')})
        backlog = autonomy_backlog.load(bound_file(self.context, self.config['backlog']),
            json.loads(bound_file(self.context, self.config['backlog_binding'])), bound_file(self.context, self.config['operator']))
        scoped = preparation_scope(plan)
        if scoped or preparation_scope(self.config):
            key = 'aggregate_analysis' if 'aggregate_analysis' in plan else 'colab_preparation'
            if (scoped is None or self.config.get(key) != plan.get(key)
                    or preparation_scope(self.config) is not scoped or self.config['run_id'] != scoped.run_id(plan)):
                raise ValueError('AGGREGATE_ANALYSIS_CONFIG_CHANGED')
            scoped.validate({**plan, 'context': str(self.context)}, backlog)
        else:
            autonomy_backlog.require_item(backlog, self.config['item_number'], self.config['item_sha256'], 'analysis',
                completed_items=(1,2,3) if self.config['item_number']==5 else (1,) if self.config['item_number'] == 2 else ())
        if self.config.get('notebook_revision'):
            from orchestrator.notebook_revision import validate_config
            if self.config['notebook_revision'] != plan.get('notebook_revision'):
                raise ValueError('NOTEBOOK_REVISION_PLAN_CHANGED')
            if self.config.get('colab_preparation'):
                scoped.validate_notebook_config(self.context,self.config['notebook_revision'])
            else:
                validate_config(self.context,self.config['notebook_revision'])
        load_views(self.context, self.config['private_intake'], stage='run_spec_author', idea_ids=self.config['idea_ids'])
        if self.config['item_number']==5:
            from orchestrator.directions_analysis import validate_plan, require_item2_complete
            if self.config.get('directions')!=plan['directions']:
                raise ValueError('DIRECTIONS_CONFIGURATION_CHANGED')
            validate_plan({**plan, 'context': str(self.context)})
            require_item2_complete(self.store.batch, self.context, self.config['directions'])
        if self.config['item_number'] in (2,5):
            from orchestrator.completed_run import validate as completed
            if (self.config.get('review_contract')!='bound-review/v1' or
                    self.config.get('accepted_stocktake')!=plan['accepted_stocktake'] or completed() is None):
                raise ValueError('ITEM2_ACCEPTED_PREDECESSOR_OR_CONTRACT_CHANGED')
            # Recheck the immutable inventory and absence of per-patient views;
            # later stage artifacts are outside the immutable preparation context.
            for ref in (plan['accepted_stocktake']['report'],plan['accepted_stocktake']['operator_review']):
                bound_file(self.context,ref)


    def task(self, stage, value):
        scoped = preparation_scope(self.config)
        if scoped: return scoped.instructions(stage, read(self.state/'preparation-plan.json'))
        if self.config['item_number']==5:
            from orchestrator.directions_analysis import instructions
            from orchestrator.analysis_revisions import instructions as revisions
            text=instructions(stage)+revisions(self.store,self.config['run_id'])
            if stage.startswith('run_spec'):
                text+=('Write/review independent directions in SPEC.proposed.md, at most12000characters. Exact binding lines:\nrun_id: '
                    +self.config['run_id']+'\nanalysis_registry_sha256: '+self.config['private_intake']['sha256']+'\n')
            return text
        if self.config['item_number']==2:
            text=('Analysis-only next-steps proposal using the operator-reviewed stock-take and Sprint13 plan/code. '
                '13A is operator-run; do not schedule or rerun it. Use only its supplied, registered aggregate outputs. '
                'Focus on 13B: screen first versus all arms, second windows, verdict rule, repeat count and L configuration. '
                'Answer all eight plan questions, flag Sprint12b overlap and recommend advance/modify/reject with evidence. '
                'Challenge the proposed scope where warranted. Cost each option with explicit runtime assumptions, '
                'GPU/CPU/memory rates, overhead, uncertainty and scientific model-call estimates. Distinguish estimates '
                'from measured runtimes. No GPU/Modal/patient-level work, notebook execution or successor dispatch. '
                'Read the original safe views; cite numeric sources and identify missing evidence. '
                'The bound revision policy below supersedes earlier stop-on-REVISE instructions. '
                'The next decision must be stop for operator review, not execution authority. ')
            if stage.startswith('run_spec'):
                text+=('Write/review an analysis specification at most12000characters. Exact binding lines:\nrun_id: '
                    +self.config['run_id']+'\nanalysis_registry_sha256: '+self.config['private_intake']['sha256']+'\n')
            from orchestrator.analysis_revisions import instructions
            text += instructions(self.store,self.config['run_id'], notebook_revision=bool(self.config.get('notebook_revision')))
            if self.config.get('notebook_revision'):
                text=text.replace('No GPU/Modal/patient-level work, notebook execution or successor dispatch.', 'No GPU/Modal/patient-level work or successor dispatch. Only controller-run synthetic CPU tests are authorized.')
                from orchestrator.notebook_revision import instructions as notebook_instructions
                text += notebook_instructions()
                text += (' The latest explicit notebook-revision authority governs the revised copy. '
                    'No real-data notebook execution is permitted; only the controller runs the bound synthetic checks. '
                    'A passing synthetic receipt does not prove full pipeline execution. Review actual call-site wiring as well as tests. ')
            return text
        text = ('Stock-take of the preserved external Sprints1–12b research, analysis only. '
                'No training, notebook execution, new run or successor dispatch. Read the selected methods/results/plans/reviews; '
                'state each question, measured answer and uncertainty, tentative versus supported findings, limitations, '
                'inconsistencies and overlapping experiments. Preserve original judgments and inspect current closures. '
                'Do not equate unavailable or merely indexed evidence with inspection. Cite view IDs and exact components, '
                'not individual patient identifiers. Reports and proposals must be aggregate-only. '
                'For REVISE, name BLOCKER[category]; categories: ' + ', '.join(CATEGORIES) + '. Other concerns are advisories. ')
        if stage.startswith('run_spec'):
            text += ('Write or review a concise analysis specification, at most12000characters, covering the evidence and '
                     'questions rather than an executable experiment. Include exactly these binding lines:\nrun_id: ' +
                     self.config['run_id'] + '\nanalysis_registry_sha256: ' + self.config['private_intake']['sha256'] + '\n')
        else:
            text += ('The next decision must be an explicit stop for operator review of this stock-take; no item2/3/4 starts here. '
                     'List any per-patient evidence file used and its registered reason, all material omissions, '
                     'and missing artifacts. Do not claim imported originals are now scientifically accepted merely from registration. ')
        if self.config['run_id']=='stocktake-c9deb31c7f8668b41df09ea8' and stage.startswith('result_interpretation'):
            text += ('Use the corrected paged navigation to read the numeric source evidence. '
                     'Explicitly verify EVERY numeric claim in the approved specification, including table rows, '
                     'intervals, sample sizes and narrative claims. In interpretation.md include a numeric-claim '
                     'audit: claim, source view/component, observed value, and confirmed/corrected/unverifiable '
                     'status. Do not silently carry forward a number because the spec review approved scope. '
                     'An inaccessible or unsupported claim must be identified and excluded from supported '
                     'conclusions. The independent interpretation reviewer must inspect this audit and the '
                     'cited numeric evidence through the paged index, checking completeness against the spec. ')
        return text

    def output_names(self, stage):
        return super().output_names(stage) + (("notebook.patch.json",) if self.config.get("notebook_revision") and stage=="run_spec_author" else ())

    def prepare_input(self, value, stage, work):
        if self.config['item_number'] in (2,5):
            require_stocktake_delivery(value['artifacts'], self.config['accepted_stocktake']['report'])
        if self.config.get("notebook_revision"):
            from orchestrator.cpu_isolation import verify_environment
            verify_environment(self.config["notebook_revision"]["environment"])
        intake=self.config['private_intake']
        if self.config['item_number']==5:
            from orchestrator.directions_analysis import registry
            intake=registry(self,value,stage)
        result=manual_context.prepare(self.context, stage=stage, idea_ids=self.config['idea_ids'],
            task=self.task(stage, value), artifacts=value['artifacts'], workspace=work, private_intake=intake,
            structured_review=self.config.get('review_contract')=='bound-review/v1',
            reference_prior_results=self.config['item_number'] in (2,5) or preparation_scope(self.config) is not None,
            notebook_patch=bool(self.config.get('notebook_revision')) and stage=='run_spec_author')
        if self.config['item_number']==5:
            from orchestrator.directions_analysis import check_delivery
            check_delivery(self,stage,*result,work)
        return result

    def _accept_completed(self, value):
        pending = value['pending']
        if pending['stage'] == 'run_spec_review' and self.config.get('notebook_revision'):
            review=read(Path(pending['workspace'])/'review.json')
            if review.get('verdict')=='APPROVE' and value.get('notebook_revision_result',{}).get('synthetic_status')!='PASS':
                raise ValueError('NOTEBOOK_APPROVAL_REQUIRES_SYNTHETIC_PASS')
        if pending['stage'] != 'run_spec_author':
            if pending['stage'] == 'result_interpretation_author':
                decision = read(Path(pending['workspace'])/'investigator_next_decision.json')
                if decision.get('proposed_action_type') != 'stop':
                    raise ValueError('STOCKTAKE_OPERATOR_REVIEW_STOP_REQUIRED')
            return super()._accept_completed(value)
        row = self.store.db.execute('SELECT * FROM manual_calls WHERE id=?', (pending['id'],)).fetchone()
        if row is None or row['status'] != 'COMPLETE':
            raise ValueError('UNCERTAIN_MODEL_CALL_NO_RETRY')
        receipt = json.loads(row['receipt']); work = Path(pending['workspace'])
        for name, expected in receipt['output_sha256'].items():
            if digest((work/name).read_bytes()) != expected:
                raise ValueError('COMPLETED_OUTPUT_CHANGED')
        raw = (work/'SPEC.proposed.md').read_bytes(); spec = raw.decode()
        if len(spec) > 12000:
            raise ValueError('ANALYSIS_SPEC_LIMIT')
        for required in ['run_id: '+self.config['run_id'], 'analysis_registry_sha256: '+self.config['private_intake']['sha256']]:
            if spec.splitlines().count(required) != 1:
                raise ValueError('ANALYSIS_SPEC_BINDING_REQUIRED')
        if self.config.get('notebook_revision'):
            from orchestrator.notebook_revision import prepare_artifacts
            from orchestrator.scientific_intake import cohort
            registry=read(self.context/self.config['private_intake']['path'])
            cases = cohort((self.context/registry['cohort']).read_bytes())
            if self.config.get('colab_preparation'):
                preparation_scope(self.config).prepare_notebook_artifacts(self,value,pending,cases)
            else:
                prepare_artifacts(self,value,pending,cases)
        n = pending['round']; value['rounds']['run_spec_author'] = n
        for kind in ('run_spec', 'proposed_run_spec'):
            self.artifact(value, kind, 'ANALYSIS-SPEC-'+str(n)+'.md', raw, n)
        value.update(phase='run_spec_review', spec=str(work/'SPEC.proposed.md'))
        value.pop('pending'); self.save(value)
        return self.status()

    def status(self):
        value = super().status()
        value.update(next_action='Operator review required; no successor dispatch' if value['phase'] == 'COMPLETE' else value['phase'],
                     package=None, collection_inbox=None, execution_backend=('synthetic CPU only: no patient/experiment execution' if self.config.get('notebook_revision') else 'none: saved-evidence analysis only'))
        return value

    def acceptance_path(self, kind):
        return self.root/'projects/isles24/analysis'/self.config['run_id']/kind

    def _commit(self, target, message):
        subprocess.run(['git', 'add', '--', str(target)], cwd=self.root, check=True)
        if git(self.root, 'diff', '--cached', '--name-only'):
            subprocess.run(['git', 'commit', '-m', message], cwd=self.root, check=True)

    def _advance(self, collect_folder=None, identity_refusal=None):
        if collect_folder is not None or identity_refusal is not None:
            raise ValueError('ANALYSIS_HAS_NO_EXECUTION_OR_COLLECTION')
        self.guard(); value = self.current(); phase = value['phase']
        if phase in STAGES:
            return self.model_step(value)
        if phase == 'MODEL_RUNNING':
            return self.accept_completed(value)
        if phase == 'COMMIT_SPEC':
            if git(self.root, 'status', '--porcelain'):
                raise ValueError('UNRELATED_EDITS_BEFORE_ANALYSIS_COMMIT')
            target = self.acceptance_path('spec')
            write_once(target/'SPEC.md', Path(value['spec']).read_bytes())
            write_once(target/'review.json', Path(value['spec_review']).read_bytes())
            if self.config.get('notebook_revision'):
                names={'notebook_source':'revised13B.ipynb','notebook_diff':'notebook.diff',
                       'notebook_patch':'notebook.patch.json','synthetic_tests':'synthetic-tests.json',
                       'notebook_provenance':'patch-provenance.json','execution_conditions':'carried-conditions.json'}
                for typ,name in names.items():
                    matches=[row for row in value['artifacts'] if row['type']==typ]
                    if len(matches)!=1: raise ValueError('NOTEBOOK_ACCEPTED_ARTIFACT_REQUIRED:'+typ)
                    write_once(target/name,bound_file(self.context,{k:matches[0][k] for k in ('path','sha256')}))
            self._commit(target, 'Record reviewed stock-take analysis specification')
            intake=self.config['private_intake']
            if self.config['item_number']==5:
                from orchestrator.directions_analysis import phase1_receipt
                value['spec_commit']=git(self.root, 'rev-parse', 'HEAD')
                proof=phase1_receipt(self,value)
                write_once(self.state/'independent-directions.json', json.dumps(proof,sort_keys=True).encode())
                intake=self.config['directions']['phase2_intake']
            # This validates delivery identities, not scientific truth or a new
            # computation. It cannot be confused with a CPU/GPU execution receipt.
            views, _ = load_views(self.context, intake, stage='result_interpretation_author', idea_ids=self.config['idea_ids'])
            validation = {'status': 'VALID', 'kind': 'SAVED_EVIDENCE_IDENTITY_ONLY',
                          'registry_sha256': intake['sha256'], 'views': views,
                          'scientific_acceptance': False, 'execution_performed': False}
            atomic(self.state/'validation.json', validation)
            self.artifact(value, 'validation_result', 'intake-validation.json', json.dumps(validation, sort_keys=True).encode(), 1)
            value.update(phase='result_interpretation_author', spec_commit=git(self.root, 'rev-parse', 'HEAD'))
            self.save(value); return self.status()
        if phase == 'UPDATE_STATE':
            if git(self.root, 'status', '--porcelain'):
                raise ValueError('UNRELATED_EDITS_BEFORE_ANALYSIS_COMMIT')
            target = self.acceptance_path('interpretation')
            record = {'run_id': self.config['run_id'], 'source': self.config['source'],
                      'registry_sha256': self.config['private_intake']['sha256'], 'operator_review_pending': True,
                      'meaning': ('Independently reviewed two-phase research directions; operator comparison follows preserved independent directions. No experiment authorized.' if self.config['item_number']==5 else 'Independently reviewed Sprint13 next-steps proposal; 13A remains operator-run; no experiment or successor authorized.' if self.config['item_number']==2 else 'Independently reviewed stock-take analysis; original external execution attribution and limitations retained. No new experiment or successor authorized.')}
            if self.config['item_number']==5:
                from orchestrator.directions_analysis import registry, phase1_receipt
                record['registry_sha256']=registry(self,value,'result_interpretation_review')['sha256']
                record['independent_phase1']=phase1_receipt(self,value)
            for name, key in [('interpretation.md', 'interpretation'), ('review.json', 'review'), ('investigator_next_decision.json', 'next_decision')]:
                raw = Path(value[key]).read_bytes(); write_once(target/name, raw); record[name+'_sha256'] = digest(raw)
            for artifact in value['artifacts']:
                if artifact['type'] in {'interpretation_original', 'interpretation_format_repair'}:
                    write_once(target/Path(artifact['path']).name, bound_file(self.context, {k: artifact[k] for k in ('path', 'sha256')}))
            write_once(target/'record.json', json.dumps(record, sort_keys=True).encode())
            state = self.root/PROFILE/'STATE.md'
            addition = ('\n\n## Research directions awaiting operator review\n' if self.config['item_number']==5 else '\n\n## Sprint13 proposal awaiting operator review\n' if self.config['item_number']==2 else '\n\n## Stock-take awaiting operator review\n')+record['meaning']+'\nRecord: '+str((target/'record.json').relative_to(self.root))+' SHA256 '+digest((target/'record.json').read_bytes())+'\n'
            # Start with the prepared current state (including already completed
            # M3), not the implementation checkout's older seed snapshot.
            body = (self.context/PROFILE/'STATE.md').read_text()
            if addition not in body:
                if len(body+addition) > 20000:
                    raise ValueError('STATE_LIMIT')
                scan('context/STATE.md', (body+addition).encode()); private_records.write_text(state, body+addition)
            profile = read(self.root/PROFILE/'manifest.json'); profile['state']['sha256'] = digest(state.read_bytes())
            atomic(self.root/PROFILE/'manifest.json', profile)
            subprocess.run(['git', 'add', '--', str(state), str(self.root/PROFILE/'manifest.json')], cwd=self.root, check=True)
            self._commit(target, 'Record reviewed stock-take and operator review stop')
            value.update(phase='REPORT'); self.save(value); return self.status()
        if phase in {'REPORT', 'COMPLETE'}:
            if phase == 'REPORT':
                receipts = [json.loads(r['receipt']) for r in self.store.db.execute('SELECT receipt FROM manual_calls')]
                elapsed = (datetime.now(timezone.utc)-datetime.fromisoformat(self.config['started_utc'])).total_seconds()
                body = ('# Research directions ready for operator review\n\n' if self.config['item_number']==5 else '# Sprint13 proposal ready for operator review\n\n' if self.config['item_number']==2 else '# Stock-take ready for operator review\n\n')+Path(value['interpretation']).read_text()
                body += ('\n\n## Run record\nAnalysis plus a new notebook copy and isolated synthetic CPU tests only; no real-data notebook, GPU or Modal execution. ' if self.config.get('notebook_revision') else '\n\n## Run record\nAnalysis only; no notebook, CPU or GPU execution. ') + 'Operator review is required before any next backlog item.\n'
                body += f'Calls: {len(receipts)}/{self.status()['call_limit']}; elapsed seconds: {elapsed:.1f}; rounds: '+json.dumps(value['rounds'])+'.\n'
                body += '\n| Stage | Input characters | Outcome |\n| --- | ---: | --- |\n'
                for row in receipts:
                    body += f'| {row["stage"]} | {row["input_characters"]} | {row["outcome"]} |\n'
                private_records.write_text(self.state/'REPORT.md', body)
                value.update(phase='COMPLETE', operator_review_pending=True); self.save(value)
            self.store.batch.complete_run(self.config['run_id'], {'report_sha256': digest((self.state/'REPORT.md').read_bytes()), 'operator_review_pending': True})
            return self.status()
        if phase == 'BLOCKED':
            return self.status()
        raise ValueError('ANALYSIS_PHASE_HAS_NO_AUTHORIZED_TRANSITION')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['init', 'advance', 'status'])
    parser.add_argument('--state', required=True); parser.add_argument('--root')
    parser.add_argument('--engine-review'); parser.add_argument('--plan')
    args = parser.parse_args()
    if args.action == 'init':
        if not all((args.root, args.engine_review, args.plan)):
            parser.error('init requires root, engine-review and plan')
        result = initialize(args.root, args.state, args.engine_review, args.plan)
    else:
        driver = AnalysisDriver(args.state)
        result = driver.advance() if args.action == 'advance' else driver.status()
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
