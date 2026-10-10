"""Operator-bound item4 Colab notebook preparation; no patient/GPU execution.

A sibling drafting lane, never a new experiment allowance or a replacement for
item4's existing owner, scientific findings, pending author or paid-run guards.
"""
import json
from pathlib import Path
from orchestrator import context_budget,notebook_revision as nr,scientific_intake as intake
from orchestrator.manual_executor import digest

DOCUMENT='docs/PARALLEL_RESEARCH_OPERATOR_DECISION_20261010.txt'
AUTHORITY='644410e1659c8998040c3cc9035aaa0eb2c5c3708fba37cfbb1a91fadf9f00e6'
SCHEMA='item4-colab-preparation/v1'
TASK='sprint13b-execution'
IDEAS=[TASK,'colab-preparation-20261010']
MODE='item4-colab-preparation'


def authority(root=None):
    root=Path(root) if root is not None else Path(__file__).resolve().parents[1]
    if digest(context_budget.relative_file(root,DOCUMENT).read_bytes())!=AUTHORITY:
        raise ValueError('COLAB_PREPARATION_AUTHORITY_CHANGED')
    return AUTHORITY


def run_id(plan):
    return 'colab-'+digest((AUTHORITY+':'+plan['private_intake']['sha256']).encode())[:24]


def validate_notebook_config(root,cfg):
    authority()
    fields={'mode','authority','original','selection','safe_view','environment','carried_conditions'}
    if not isinstance(cfg,dict) or set(cfg)!=fields or cfg['mode']!=MODE:
        raise ValueError('COLAB_NOTEBOOK_CONFIG_FIELDS')
    if digest(nr.bound(root,cfg['authority']))!=AUTHORITY:
        raise ValueError('COLAB_NOTEBOOK_AUTHORITY_CHANGED')
    ref=cfg['original']
    if not isinstance(ref,dict) or set(ref)!={'path','sha256'} or ref['sha256']!=nr.ORIGINAL:
        raise ValueError('COLAB_NOTEBOOK_ORIGINAL_BINDING')
    path=Path(ref['path'])
    if not path.is_absolute() or any(x.is_symlink() for x in (path,*path.parents)):
        raise ValueError('COLAB_NOTEBOOK_ORIGINAL_PATH')
    from orchestrator import private_records
    original=private_records.check(path).read_bytes()
    if digest(original)!=nr.ORIGINAL:raise ValueError('COLAB_NOTEBOOK_ORIGINAL_CHANGED')
    if digest(nr.bound(root,cfg['safe_view']))!=nr.VIEW:
        raise ValueError('COLAB_NOTEBOOK_VIEW_CHANGED')
    selection=nr.strict_json(nr.bound(root,cfg['selection']))
    if set(cfg['environment'])!={'environment_root','environment_sha256'}:
        raise ValueError('COLAB_NOTEBOOK_SYNTHETIC_ENVIRONMENT_ONLY')
    conditions=nr.strict_json(nr.bound(root,cfg['carried_conditions']))
    if conditions.get('execution_authorized') is not False:
        raise ValueError('COLAB_PREPARATION_NO_EXECUTION_AUTHORITY')
    return original,selection


def validate(plan,backlog):
    authority()
    scope=plan.get('colab_preparation')
    if (not isinstance(scope,dict) or set(scope)!={'schema','operator','item_number'}
            or scope['schema']!=SCHEMA or type(scope['item_number']) is not int
            or scope['item_number']!=4 or type(plan.get('item_number')) is not int
            or plan['item_number']!=4 or plan.get('idea_ids')!=IDEAS
            or 'aggregate_analysis' in plan):
        raise ValueError('COLAB_PREPARATION_SCOPE')
    root=Path(plan['context'])
    if digest(nr.bound(root,scope['operator']))!=AUTHORITY:
        raise ValueError('COLAB_PREPARATION_OPERATOR_BINDING')
    item=next((x for x in backlog.items if x.number==4),None)
    if (item is None or item.sha256!=plan.get('item_sha256') or item.mode!='gpu'
            or item.state!='AUTHORIZED'):
        raise ValueError('COLAB_PREPARATION_BACKLOG_BINDING')
    original,selection=validate_notebook_config(root,plan['notebook_revision'])
    registry=nr.strict_json(nr.bound(root,plan['private_intake']))
    cases=intake.cohort(context_budget.relative_file(root,registry['cohort']).read_bytes())
    nr.partition(original,selection,cases,nr.VIEW)
    for stage in ('run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review'):
        views,_=intake.load_views(root,plan['private_intake'],stage=stage,idea_ids=IDEAS)
        if any(row.get('per_patient_material') for row in views):
            raise ValueError('COLAB_PREPARATION_NO_PATIENT_MATERIAL')
    for row in registry['views']:
        manifest=json.loads(context_budget.relative_file(root,row['manifest']).read_bytes())
        if manifest['per_patient_material']:
            raise ValueError('COLAB_PREPARATION_NO_PATIENT_MATERIAL')
    for row in plan['artifacts']:
        intake.scan(nr.bound(root,{k:row[k] for k in ('path','sha256')}),cases,
            kind='code',reason='Colab source and aggregate preparation only')
    return item


def instructions(stage,plan):
    text=('Prepare the exact 13B notebook for Partho on Colab under the October10 direction. '
        'This is a NEW private notebook copy under approved item4, not a restart of completed item2 '
        'or a modification of pending timing author24. Scientific author owns all scientific code. '
        'Original13B notebook is the patch base; inspect the entire provided current pipeline, '
        'plan, notebook and actual test/review evidence as context, including limitations. '
        'Retain all eight arms x five folds in the full research plan; stage coverage-independent '
        'arms first and hold zscore/histeq coverage-dependent work. First human handoff should '
        'be explicit baseline repeat smoke on Colab A100, independently of Modal CPU-starvation '
        'A/B. Decide scientific comparability of cohort,fold,iterations,epochs,plans,seed,environment '
        'and checkpoint timing; original12-patient smoke must not silently impersonate current99 '
        'development/fold0 workload. Minor platform differences are allowed if recorded. '
        'Supply exact settings and private result-return instructions in SPEC.proposed.md. '
        'Only frozen99 development inputs may be read at eventual human execution, verified '
        'against existing manifests/hashes and excluded-membership checks. No locked25/reserve24 '
        'patient access, new credentials, public patient-derived output, BACKLOG edits or main merge. '
        'Here there is NO real-data notebook/GPU/provider execution. The controller may only '
        'compile and run isolated synthetic CPU tests. Scientific review judges all findings '
        'at once with the whole component, not selected snippets. No full training until genuine '
        'scientific smoke acceptance and unchanged spending/projection gates. Keep150stage1, '
        '1200projection,1275total and1001operatorColabunits explicit; obtain actualCU/hour from '
        'the runtime, do not invent a rate or certify capacity. Record checkpoint/resume,timing '
        'and private artifacts needed to return results to the system. Preserve all existing '
        'findings and genuine review outcomes; an APPROVE here accepts the prepared notebook, '
        'not unseen patient results or full training. ')
    if stage.startswith('run_spec'):
        text+=('Write/review SPEC.proposed.md (at most12000characters) with exact binding lines:\nrun_id: '
            +run_id(plan)+'\nanalysis_registry_sha256: '+plan['private_intake']['sha256']+'\n')
        text+=('Author also writes notebook.patch.json: safe-notebook-patch/v1; original_sha256='
            +nr.ORIGINAL+', view_sha256='+nr.VIEW+'. Exact fields schema,original_sha256,'
            'view_sha256,edits; each edit has unit=cells/N/source,start,end,before_sha256,replacement. '
            'At most80000bytes; nonoverlapping UTF8 byte spans wholly inside visible kept source. '
            'All rounds patch this SAME original. Never reconstruct omitted membership. '
            'Expose pure helpers required by notebook-synthetic-contract.md and use them at actual '
            'call sites. Emit one importable writefile pipeline with main(input_root,output_root,contract), '
            'preprocess(input_root,output_root,contract),validate_preprocessing(output_root,contract), '
            'synthetic_tests() returning a nonempty unittest.TestSuite. The controller runs that '
            'exact module suite as well as notebook helper checks with zero skips/failures. ')
    else:text+='Return the reviewed handoff and limitations; next action is stop, never an executor dispatch. '
    return text


def prepare_notebook_artifacts(driver,value,pending,cases):
    from orchestrator import notebook_synthetic
    from orchestrator.manual_driver import write_once
    cfg=driver.config['notebook_revision']
    original,selection=validate_notebook_config(driver.context,cfg)
    patch=(Path(pending['workspace'])/'notebook.patch.json').read_bytes()
    notebook,diff,receipt=nr.apply(original,selection,patch,cases,
        original_sha256=nr.ORIGINAL,view_sha256=nr.VIEW)
    folder=driver.state/'notebook-revisions'/('author-'+str(pending['round']))
    write_once(folder/'revised.ipynb',notebook)
    write_once(folder/'notebook.diff',diff)
    write_once(folder/'patch-receipt.json',intake.canonical(receipt))
    tests=(notebook_synthetic.run(folder/'synthetic',notebook,cfg['environment'],execution=True)
        if all(x['compile']=='PASS' for x in receipt['compile']) else
        {'status':'FAIL','reason':'COMPILE_FAILED_NO_EXECUTION','compile':receipt['compile'],
         'patient_data':False,'no_model_call':True})
    nr.scan(intake.canonical(tests),cases)
    conditions=nr.bound(driver.context,cfg['carried_conditions'])
    for typ,name,raw in [
        ('notebook_source','colab13B-'+str(pending['round'])+'.ipynb',notebook),
        ('notebook_diff','colab13B-diff-'+str(pending['round'])+'.patch',diff),
        ('notebook_patch','colab13B-patch-'+str(pending['round'])+'.json',patch),
        ('synthetic_tests','colab13B-tests-'+str(pending['round'])+'.json',intake.canonical(tests)),
        ('notebook_provenance','colab13B-provenance-'+str(pending['round'])+'.json',intake.canonical(receipt)),
        ('execution_conditions','colab13B-conditions-'+str(pending['round'])+'.json',conditions)]:
        driver.artifact(value,typ,name,raw,pending['round'])
    value['notebook_revision_result']={'folder':str(folder),'notebook_sha256':digest(notebook),
        'diff_sha256':digest(diff),'tests_sha256':digest(intake.canonical(tests)),
        'synthetic_status':tests['status']}
    if digest(Path(cfg['original']['path']).read_bytes())!=nr.ORIGINAL:
        raise ValueError('COLAB_NOTEBOOK_ORIGINAL_CHANGED_AFTER_PATCH')
