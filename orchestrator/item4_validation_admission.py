"""One exact evidence-generating stage; the scientific REVISE stays a REVISE.

This host-only patch creates no scientific judgment or money allowance. Default
approval remains clean APPROVE. The exact reviewed exception carries its open
findings into the package and is checked again before dispatch and reservation.
"""
from pathlib import Path
import hashlib
import json
import re
from orchestrator import private_records as pr
from orchestrator.manual_host_guard import trusted
from orchestrator.review_submission import canonical

CHANGE='item4-partition-delivery-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
DOCUMENT='docs/ITEM4_VALIDATION_ADMISSION_PRIVATE.json'
CONTRACT_SHA='620442350aac43d3b07af9e26b4265b122f8075169456ddc734e0e7117baf34f'
OPERATOR='12457759a381afd91b722ba050a040ed1d1bf58a148ee89ba0082aab8c419e4d'
DIRECTION='7653ab6622decd4105f495789ce2428cd4df31ec8a88495a262b44aaf806ad8c'
REVIEW_SHA='bd6252dee2df5f0323fdc285731e3309e36d3bc95068c09502a39232f415bd77'
DIRECTION_SOURCE='0def0557211dc0fef6f48348f77fb1852e1ff6fc'
FILES=(DOCUMENT,'docs/ITEM4_GPU_SMOKE_STAGING_OPERATOR_DECISION_20261009.txt',
 'orchestrator/item4_validation_admission.py','orchestrator/experiment_approval.py',
 'orchestrator/experiment_modal_package.py','orchestrator/experiment_owner.py','orchestrator/modal_executor.py',
 'tools/item4_validation_runtime.py','tools/install_item4_validation.py',
 'orchestrator/modal_item4_budget.py','tools/item4_validation_retained.py',
 'orchestrator/experiment_partition_input.py')


def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('ITEM4_VALIDATION_'+why)


def contract():
    raw=trusted(ROOT/DOCUMENT).read_bytes()
    require(sha(raw)==CONTRACT_SHA,'CONTRACT_CHANGED')
    return json.loads(raw)


def authority():
    """Only an installed, independently approved patch may supply the exception."""
    from orchestrator.autonomy_review import verify_result
    installed=json.loads(trusted(RECORD/'installed.json').read_bytes())
    result=verify_result(trusted(RECORD/'review'))
    manifest=json.loads(trusted(RECORD/'review/packet-manifest.json').read_bytes())
    require(result['verdict']=='APPROVE' and result['change_id']==CHANGE
        and result['source_sha']==installed['source']==manifest['source_sha']
        and result['report_sha256']==installed['review_sha256'],'IMPLEMENTATION_APPROVAL')
    require(set(installed['files'])==set(FILES),'INSTALL_MEMBERS')
    for name,pin in installed['files'].items():
        require(sha(trusted(ROOT/name).read_bytes())==pin==manifest['source_files'][name],'INSTALLED_SOURCE')
    require(Path(__file__).resolve()==ROOT/'orchestrator/item4_validation_admission.py','IMPORTED_SOURCE')
    unit=Path('/etc/systemd/system')/('research-'+CHANGE+'.service')
    require(set(installed['units'])=={str(unit)} and sha(trusted(unit).read_bytes())==installed['units'][str(unit)],'UNIT_CHANGED')
    direction=verify_result(trusted(RECORD/'direction'))
    require(direction['verdict']=='APPROVE' and direction['report_sha256']==DIRECTION
        and direction['source_sha']==DIRECTION_SOURCE,'DIRECTION_APPROVAL')
    require(sha(trusted(ROOT/FILES[1]).read_bytes())==OPERATOR,'OPERATOR_BINDING')
    return result['report_sha256']


def review(driver,pending,delivery):
    # Refuse ordinary REVISE/REJECT without even consulting the fixed exception.
    work,prompt,raw,receipt,row,submission=delivery
    if sha(raw)!=REVIEW_SHA:
        raise ValueError('EXPERIMENT_APPROVAL_REQUIRED')
    selected=contract()
    require(driver.config['run_id']==selected['run_id'] and driver.config['source']==selected['source']
        and str(driver.state)==selected['state'] and pending['id']==selected['review_call']
        and pending['stage']=='run_spec_review' and pending['round']==selected['review_round']
        and sha(submission)==selected['submission_sha256'],'EXACT_REVIEW_REQUIRED')
    decision=json.loads(raw)
    require(decision['verdict']=='REVISE' and {f['id'] for f in decision['findings']}=={
        'U1-input-provenance','U2-runtime-interface-native-integration','U3-coverage-arm-source-validation'},'PRESERVED_FINDINGS')
    authority()


def record_for(selected,implementation):
    return {'schema':selected['schema'],'scientific_verdict':'REVISE','findings_closed':False,
        'validation_only':True,'operator_sha256':OPERATOR,'direction_sha256':DIRECTION,
        'implementation_sha256':implementation,'contract_sha256':CONTRACT_SHA,
        'allowed_preprocessing':[selected['preprocessing_id']], 'allowed_fits':list(selected['fits']),
        'full_training_allowed':False,'coverage_allowed':False}


def artifacts(driver,pending,raw_review,by_type,outputs,authored_ref):
    if json.loads(raw_review)['verdict']=='APPROVE':return {}
    selected=contract()
    require(sha(raw_review)==selected['review_sha256'] and pending['id']==selected['review_call'],'EXACT_REVIEW_REQUIRED')
    require(authored_ref is not None and authored_ref['sha256']==selected['plan_sha256']
        and authored_ref['version']==selected['author_round']
        and outputs['execution.py']['sha256']==selected['module_sha256'],'TESTED_CODE_PLAN_CHANGED')
    for name,pin in selected['artifact_pins'].items():
        ref=by_type[name]
        require(ref['id']==name and ref['version']==pin['version'] and ref['sha256']==pin['sha256'],'AUTHOR_ARTIFACT_CHANGED')
    return {'validation_admission':record_for(selected,authority())}


def scope(approved,binding,*,bound=False):
    """Called after the actual seal replay: before package writes and spending.

    This does not replace plan/runtime/input/cost/resume checks. It only narrows
    the jobs for which the preserved REVISE can serve as validation permission.
    """
    marker=approved.get('validation_admission')
    if marker is None:
        if approved.get('review_sha256')==REVIEW_SHA:
            raise ValueError('ITEM4_VALIDATION_MARKER_REQUIRED')
        return
    selected=contract()
    require(isinstance(marker,dict) and re.fullmatch('[a-f0-9]{64}',str(marker.get('implementation_sha256','')))
        and marker==record_for(selected,marker['implementation_sha256'])
        and approved['review_sha256']==selected['review_sha256'],'SCOPE_MARKER_CHANGED')
    e=binding.get('experiment',{})
    require(binding.get('run_id')==selected['run_id'] and binding.get('source')==selected['source']
        and binding.get('image_id')==selected['image_id'] and e.get('backlog_item')==4
        and e.get('stage')=='SMOKE','SMOKE_ONLY')
    if bound:
        require(binding.get('review_sha256')==selected['review_sha256']
            and binding.get('spec_sha256')==selected['artifact_pins']['run_spec']['sha256']
            and binding.get('execution_plan_sha256')==selected['plan_sha256']
            and binding.get('execution',{}).get('module_sha256')==selected['module_sha256'],'BOUND_CODE_PLAN')
    if 'preprocessing' in binding:
        p=binding['preprocessing']
        require(p.get('id')==selected['preprocessing_id'] and e.get('fit_id')=='preprocess-'+p['id']
            and p.get('input_contract_sha256')==selected['input_contract_sha256']
            and binding.get('resources',{}).get('gpu') is None,'BASE_PREPROCESSING_ONLY')
    else:
        fit=binding.get('progress',{}).get('fit_binding',{})
        require(type(fit.get('fold')) is int and e.get('fit_id') in selected['fits'] and
            [fit.get(k) for k in ('arm','fold','realization')]==selected['fits'][e['fit_id']],'DECLARED_SMOKE_ONLY')
    # Segments are admitted only by the unchanged genuine terminal/resume route.
    require(type(e.get('segment')) is int and e['segment']>=1,'SEGMENT')


def package_review(package,binding):
    """Equivalent check at the existing low-level provider package boundary.

    Native delivery was independently qualified before sealing. Here its exact
    original report/submission pins and installed authority are required again;
    the spending owner also compares the actual sealed approval-record hash.
    """
    raw=pr.check(Path(package)/'review.json').read_bytes()
    if sha(raw)!=REVIEW_SHA:raise ValueError('MODAL_APPROVED_SCIENTIFIC_SPEC_REQUIRED')
    selected=contract();implementation=authority()
    raw_approval=pr.check(Path(package)/'approval.json').read_bytes();approved=json.loads(raw_approval)
    require(approved.get('validation_admission')==record_for(selected,implementation)
        and approved.get('submission_sha256')==selected['submission_sha256']
        and approved.get('pending_review',{}).get('id')==selected['review_call']
        and binding.get('execution',{}).get('approval_sha256')==sha(raw_approval),'PACKAGE_AUTHORITY')
    scope(approved,binding,bound=True)


TERMINAL_ASSETS={
 '5679c16fedb876f53ac9fcc39fac4c885c1cb245292e3fde7cc0664403b3a46f',
 '1b516eb5c8472d29d95c9795b8cd37fd722ab45f52bc244531c9786b6c1e7ccf',
 '450b6795685fe5b1d80986e64836f8f155d7953986cb32a05fd0d0a3266cb7e9'}
TERMINAL_COMPUTE={
 'd9bd52cf0b27045e1e23ba018ac44d9ed25cb2ab8ccf81f8c22cf33b4fb264e3',
 '2b0ab32a1f4d4890bb0f17a9986440e0675debcd9cbfc56746183e3dbab31795'}


def retained_terminal(accounts,binding):
    """Only exact validation jobs reuse exact prior proofs; all charges remain.

    Called after owner/seal replay inside the existing reservation transaction.
    The child has a read-only SQLite connection and imports the original reviewed
    releases in isolation. Matching every returned row to our locked snapshot
    rejects a stale proof; unknown/live/changed records retain normal refusals.
    """
    if binding.get('review_sha256')!=REVIEW_SHA:return set(),set()
    observed={r['id'] for table in ('autonomy_assets','autonomy_compute')
        for r in accounts.db.execute('SELECT id FROM '+table)}
    if not observed & (TERMINAL_ASSETS|TERMINAL_COMPUTE):return set(),set()
    import subprocess
    selected=contract();scope({'review_sha256':REVIEW_SHA,
        'validation_admission':record_for(selected,authority())},binding,bound=True)
    raw=subprocess.check_output(['/usr/bin/python3','-s','-B',
        str(ROOT/'tools/item4_validation_retained.py')])
    from orchestrator.review_contract import strict_json
    proof=strict_json(raw)
    require(set(proof)=={'schema','source_sha','source_asset','assets','compute'} and
        proof['schema']=='item4-retained-terminal-qualification/v1' and
        proof['source_sha']=='28726e3d5cdf32f1d80c63187f5abd9146cbfcd0' and
        proof['source_asset']=='9878e7923ea81dceefce162166a113aa7d0a53dd65c4199a42b4276fe952d365' and
        set(proof['assets'])==TERMINAL_ASSETS and set(proof['compute'])==TERMINAL_COMPUTE,'TERMINAL_SCOPE')
    for kind,table in [('assets','autonomy_assets'),('compute','autonomy_compute')]:
        for ident,pin in proof[kind].items():
            row=accounts.db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone()
            require(row is not None and sha(canonical(dict(row)))==pin,'TERMINAL_ROW_CHANGED')
    return set(proof['assets']),set(proof['compute'])
