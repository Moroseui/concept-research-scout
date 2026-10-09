"""Close a reviewed experiment with its original results and independent verdict.

No scientific conclusion is generated here. Repeated finalization verifies the
same bytes and never creates a job, model invocation or new allowance.
"""
import json
from pathlib import Path
import subprocess
from datetime import datetime
from orchestrator import experiment_approval as approval,experiment_collection as collection
from orchestrator import manual_context as mc,context_budget as cb,private_records as pr
from orchestrator import review_submission as rs
from orchestrator.manual_driver import write_once,git,PROFILE,stamp
from orchestrator.manual_executor import digest,read,inventory
from orchestrator.git_publication import scan

TYPES={'run_spec','result_tables','validation_result','execution_receipt','execution_manifest',
       'package_manifest','interpretation','investigator_next_decision'}


def delivered(driver,value,work,receipt,stage,required):
    prompt=approval.checked(work/'prompt.md',receipt['input_sha256']).decode()
    measurement=json.loads(approval.checked(work/'input-measurement.json'))
    rows=[r for r in mc.selected_artifacts(stage,value['artifacts']) if r['type'] in required]
    if {r['type'] for r in rows}!=required:raise ValueError('EXPERIMENT_RESULTS_DELIVERY_REQUIRED')
    for ref in rows:
        if measurement['selected_artifacts'].count(ref)!=1:
            raise ValueError('EXPERIMENT_RESULTS_NOT_DELIVERED')
        raw=approval.checked(cb.relative_file(driver.context,ref['path']),ref['sha256'])
        if mc.workspace_artifact(ref['type'],artifact_id=ref['id'],private_intake=driver.config['private_intake']):
            matches=[r for r in measurement['workspace_files'] if r.get('id')==ref['id'] and r.get('type')==ref['type']]
            if len(matches)!=1:raise ValueError('EXPERIMENT_RESULTS_WORKSPACE_REQUIRED')
            shown=matches[0]
            if (any(shown.get(k)!=ref[k] for k in ('id','type','version','sha256'))
                    or shown.get('source_path')!=ref['path'] or cb.encoded(shown) not in prompt):
                raise ValueError('EXPERIMENT_RESULTS_DELIVERY_CHANGED')
            approval.checked(cb.relative_file(work,shown['path']),ref['sha256'])
        elif cb.encoded(ref)+'\n'+raw.decode() not in prompt:
            raise ValueError('EXPERIMENT_RESULTS_DELIVERY_CHANGED')
    return rows


def inspect(driver,value,pending):
    item=driver.config['item_number']
    if item not in {4,6}:raise ValueError('EXPERIMENT_RESULT_BACKEND_REQUIRED')
    if item==6:
        from orchestrator.diagnostics_execution import verified
        validation=verified(driver,value)
    else:validation=collection.verified(driver,value)
    stage='result_interpretation_review'
    work,prompt,raw_review,receipt,row,submission=approval.review_delivery(driver,pending,stage)
    artifacts=delivered(driver,value,work,receipt,stage,TYPES)
    byid={r['id']:r for r in artifacts}
    for job,fit in (value['fit_collections'].items() if item==4 else [('diagnostics',validation)]):
        for name,pin in fit['files'].items():
            ref=byid.get('experiment-result-'+job+'-'+name if item==4 else 'diagnostics-result-'+name)
            if ref is None or ref['sha256']!=pin['sha256']:
                raise ValueError('EXPERIMENT_ORIGINAL_RESULT_NOT_REVIEWED')
    for kind,key in [('interpretation','interpretation'),('investigator_next_decision','next_decision')]:
        matches=[r for r in artifacts if r['type']==kind]
        if len(matches)!=1:raise ValueError('EXPERIMENT_CURRENT_INTERPRETATION_REQUIRED')
        approval.checked(Path(value[key]),matches[0]['sha256'])
    author_round=value['rounds']['result_interpretation_author']
    ident=digest((driver.config['run_id']+':result_interpretation_author:'+str(author_round)).encode())
    author=driver.store.db.execute('SELECT * FROM manual_calls WHERE id=?',(ident,)).fetchone()
    if author is None or author['status']!='COMPLETE' or author['stage']!='result_interpretation_author':
        raise ValueError('EXPERIMENT_COMPLETED_AUTHOR_REQUIRED')
    author_receipt=json.loads(author['receipt']);folder=Path(author_receipt['workspace'])
    expected=Path(driver.config['workspace_root'])/('result_interpretation_author-'+str(author_round))
    if folder!=expected or author_receipt.get('outcome')!='COMPLETE':
        raise ValueError('EXPERIMENT_AUTHOR_BINDING')
    for name,pin in author_receipt['output_sha256'].items():approval.checked(folder/name,pin)
    if Path(value['next_decision'])!=folder/'investigator_next_decision.json':
        raise ValueError('EXPERIMENT_AUTHOR_BINDING')
    repair=author_receipt.get('deterministic_format_repair')
    if repair:
        approval.checked(folder/'interpretation.md',repair['original_sha256'])
        approval.checked(folder/'interpretation.formatted.md',repair['derived_sha256'])
        if Path(repair['path'])!=folder/'format-repair.json':raise ValueError('EXPERIMENT_AUTHOR_BINDING')
        approval.checked(folder/'format-repair.json',repair['sha256'])
    if Path(value['interpretation'])!=folder/('interpretation.formatted.md' if repair else 'interpretation.md'):
        raise ValueError('EXPERIMENT_AUTHOR_BINDING')
    delivered(driver,value,folder,author_receipt,'result_interpretation_author',TYPES-{'interpretation','investigator_next_decision'})
    from orchestrator.manual_contract import validate_next,validate_summary
    validate_summary(Path(value['interpretation']).read_text())
    # Use the author's authenticated original input. The approving review may
    # subsequently close its own findings; that must not rewrite what was open
    # when the author made this preserved proposal. No current finding is reopened.
    author_prompt=approval.checked(folder/'prompt.md',author_receipt['input_sha256']).decode()
    _,_,obligations=cb.load(driver.context)
    blockers=[r['id'] for r in obligations if (r['type']=='stop' or
        (r['type']=='adverse finding' and r['severity']=='blocker')) and cb.open_obligation_text(r) in author_prompt]
    validate_next(read(value['next_decision']),blockers)
    return {'schema':'reviewed-experiment-results/v1','run_id':driver.config['run_id'],
        'source':driver.config['source'],'item_number':item,'pending_review':pending,
        'review_sha256':digest(raw_review),'submission_sha256':digest(submission),
        'review_receipt_sha256':digest(row['receipt'].encode()),'author_receipt_sha256':digest(author['receipt'].encode()),
        'validation_sha256':digest((driver.state/'validation.json').read_bytes()),**({'fit_count':len(validation['fits'])} if item==4 else {'execution_count':1,'cpu_only':True}),
        'artifacts':artifacts,'interpretation_sha256':digest(Path(value['interpretation']).read_bytes()),
        'next_decision_sha256':digest(Path(value['next_decision']).read_bytes()),
        'scientifically_reviewed':True,'successor_execution_authorized':False}


@pr.private_umask
def record(driver,value,pending):
    manifest=inspect(driver,value,pending);raw=rs.canonical(manifest)
    path=driver.state/'reviewed-results'/(pending['id']+'.json');write_once(path,raw)
    value['reviewed_results']={'path':str(path),'sha256':digest(raw)}
    return manifest


def verify(driver,value):
    ref=value.get('reviewed_results')
    if not isinstance(ref,dict) or set(ref)!={'path','sha256'}:
        raise ValueError('EXPERIMENT_REVIEWED_RESULTS_REQUIRED')
    manifest=rs.contract.strict_json(approval.checked(Path(ref['path']),ref['sha256']))
    if (Path(ref['path'])!=driver.state/'reviewed-results'/(manifest['pending_review']['id']+'.json')
            or inspect(driver,value,manifest['pending_review'])!=manifest):
        raise ValueError('EXPERIMENT_RESULTS_SEAL_CHANGED')
    return manifest


@pr.private_umask
def prepare(driver,value):
    manifest=verify(driver,value)
    if git(driver.root,'status','--porcelain'):raise ValueError('UNRELATED_EDITS_BEFORE_EXPERIMENT_ACCEPTANCE')
    target=Path('projects/isles24/experiments')/driver.config['run_id']/'acceptance'
    files={str(target/'acceptance.json'):rs.canonical(manifest)}
    for name,key in [('interpretation.md','interpretation'),('review.json','review'),('investigator_next_decision.json','next_decision')]:
        files[str(target/name)]=approval.checked(Path(value[key]))
    files[str(target/'validation.json')]=approval.checked(driver.state/'validation.json',manifest['validation_sha256'])
    for ref in value['artifacts']:
        if ref['type'] in {'interpretation_original','interpretation_format_repair'}:
            files[str(target/Path(ref['path']).name)]=approval.checked(cb.relative_file(driver.context,ref['path']),ref['sha256'])
    state=Path(PROFILE)/'STATE.md';profile=Path(PROFILE)/'manifest.json'
    body=(driver.context/state).read_text()
    addition='\n\n## Reviewed experiment results\nBACKLOG item '+str(driver.config['item_number'])+' run completed with independently reviewed results. This does not close unexecuted stages of the backlog item.\nRecord: '+str(target/'acceptance.json')+' SHA256 '+digest(files[str(target/'acceptance.json')])+'\nOriginal judgments and limitations remain authoritative. This record grants no successor execution.\n'
    if len(body+addition)>20000:raise ValueError('STATE_LIMIT')
    scan('context/STATE.md',(body+addition).encode())
    files[str(state)]=(body+addition).encode()
    current=read(driver.root/profile);current['state']['sha256']=digest(files[str(state)])
    files[str(profile)]=(json.dumps(current,sort_keys=True,indent=2)+'\n').encode()
    folder=driver.state/'acceptance-commit'
    for name,raw in files.items():write_once(folder/'files'/name,raw)
    # Saved before mutating the repository: a repeat finalizes the exact same
    # planned bytes. Unexpected edits always refuse, never get swept into Git.
    path=folder/'intent.json'
    intent={'schema':'experiment-acceptance-commit/v1','run_id':driver.config['run_id'],
        'reviewed_results_sha256':value['reviewed_results']['sha256'],
        'files':{name:digest(raw) for name,raw in files.items()}}
    write_once(path,rs.canonical(intent))
    value.update(phase='REPORT',acceptance_intent_sha256=digest(path.read_bytes()))
    driver.save(value);return driver.status()


def commit(driver,value):
    manifest=verify(driver,value);folder=driver.state/'acceptance-commit'
    intent=rs.contract.strict_json(approval.checked(folder/'intent.json',value['acceptance_intent_sha256']))
    if (intent['run_id']!=driver.config['run_id'] or intent['reviewed_results_sha256']!=value['reviewed_results']['sha256']
            or inventory(folder/'files')!=intent['files']):raise ValueError('EXPERIMENT_COMMIT_INTENT_CHANGED')
    # Check every modified or staged path and planned destination before writing.
    changed=set(git(driver.root,'diff','--name-only').splitlines())|set(git(driver.root,'diff','--cached','--name-only').splitlines())|set(git(driver.root,'ls-files','--others','--exclude-standard').splitlines())
    if changed-set(intent['files']):raise ValueError('UNRELATED_EDITS_BEFORE_EXPERIMENT_ACCEPTANCE')
    for name,pin in intent['files'].items():
        raw=approval.checked(cb.relative_file(folder/'files',name),pin);dest=driver.root/name
        if dest.exists():
            current=digest(approval.checked(dest))
            allowed={pin}
            if name in driver.config['profile_files']:allowed.add(driver.config['profile_files'][name])
            if current not in allowed:raise ValueError('EXPERIMENT_ACCEPTANCE_DESTINATION_CHANGED')
        elif name in driver.config['profile_files']:raise ValueError('EXPERIMENT_ACCEPTANCE_DESTINATION_MISSING')
    for name,pin in intent['files'].items():
        dest=driver.root/name;raw=(folder/'files'/name).read_bytes()
        if not dest.exists() or digest(dest.read_bytes())!=pin:
            pr.mkdir(dest.parent,parents=True,exist_ok=True);pr.write_bytes(dest,raw)
    subprocess.run(['git','add','--',*intent['files']],cwd=driver.root,check=True,capture_output=True)
    if git(driver.root,'diff','--cached','--name-only'):
        subprocess.run(['git','commit','-m','Record independently reviewed experiment results'],cwd=driver.root,check=True,capture_output=True)
    if git(driver.root,'status','--porcelain'):raise ValueError('EXPERIMENT_ACCEPTANCE_COMMIT_NOT_CLEAN')
    for name,pin in intent['files'].items():
        if digest(subprocess.check_output(['git','show','HEAD:'+name],cwd=driver.root))!=pin:
            raise ValueError('EXPERIMENT_ACCEPTANCE_COMMIT_CHANGED')
    pr.check_tree(driver.root/'projects/isles24/experiments'/driver.config['run_id'])
    return manifest


@pr.private_umask
def finish(driver,value):
    manifest=commit(driver,value)
    path=driver.state/'completion.json'
    if not path.exists():write_once(path,rs.canonical({'completed_utc':stamp(),'acceptance_commit':git(driver.root,'rev-parse','HEAD'),
        'reviewed_results_sha256':value['reviewed_results']['sha256']}))
    completed=read(path)
    if completed['reviewed_results_sha256']!=value['reviewed_results']['sha256']:
        raise ValueError('EXPERIMENT_COMPLETION_CHANGED')
    calls=[dict(r) for r in driver.store.db.execute('SELECT * FROM manual_calls ORDER BY stage,attempt')]
    elapsed=(datetime.fromisoformat(completed['completed_utc'])-datetime.fromisoformat(driver.config['started_utc'])).total_seconds()
    report='# Reviewed experiment results\n\n'+Path(value['interpretation']).read_text()+'\n\n## Run record\n'
    report+=('Validated fits: '+str(manifest['fit_count']) if manifest['item_number']==4 else 'Validated CPU diagnostics executions: '+str(manifest['execution_count']))+'. Calls: '+str(len(calls))+'/'+str(driver.status()['call_limit'])+'. Elapsed seconds: '+str(round(elapsed,1))+'.\n'
    report+='Review rounds: '+json.dumps(value['rounds'],sort_keys=True)+'. Operator interventions: '+str(len(value.get('interventions',[])))+'.\n\n'
    report+='| Stage | Input characters | Outcome |\n| --- | ---: | --- |\n'
    for row in calls:
        receipt=json.loads(row['receipt']);report+='| '+row['stage']+' | '+str(receipt.get('input_characters','not recorded'))+' | '+row['status']+' |\n'
    report+='\nOriginal results, validation, interpretation and independent review are preserved. No successor is launched by this report. Scheduling and unattended observation remain separate requirements.\n'
    write_once(driver.state/'REPORT.md',report.encode())
    driver.store.batch.complete_run(driver.config['run_id'],{'report_sha256':digest(report.encode()),
        'reviewed_results_sha256':value['reviewed_results']['sha256'],'successor_execution_authorized':False})
    value.update(phase='COMPLETE',operator_review_pending=True);driver.save(value)
    return driver.status()
