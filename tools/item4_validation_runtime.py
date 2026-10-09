"""Existing execution lane with one reviewed validation admission; no science calls."""
from pathlib import Path
import importlib.util
import json
import os
import sys

CHANGE='item4-partition-delivery-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
SCIENCE=Path('/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-author7-and-image-recovery-20261008/tools/item4_scientific_revision_component.py')
PRIOR_SOURCE='eb835b81d019cc8088a53a246f45b790dbfffa4c'
PRIOR_REVIEW='a2b2da904ba4974850e7b0455921692b473567bde43605207535bbb18551f479'


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value)
    return value


def load():
    if os.getuid()!=1003 or os.getgid()!=1003 or Path(__file__).resolve()!=ROOT/'tools/item4_validation_runtime.py':
        raise ValueError('VALIDATION_SERVICE_IDENTITY')
    sys.path.insert(0,str(SCIENCE))
    c=module('_validation_prior_revision',PRIOR)
    v,b,e,h,old,rec=c.load()
    if v['source']!=PRIOR_SOURCE or v['review_sha256']!=PRIOR_REVIEW:
        raise ValueError('VALIDATION_PRIOR_RELEASE_CHANGED')
    import orchestrator
    policy=module('orchestrator.item4_validation_admission',ROOT/'orchestrator/item4_validation_admission.py')
    orchestrator.item4_validation_admission=policy
    policy.authority()
    from orchestrator import experiment_approval as approval,experiment_modal_package as bridge,experiment_owner as owner
    fresh=module('_validation_approval',ROOT/'orchestrator/experiment_approval.py')
    approval.review_delivery=fresh.review_delivery;approval.inspect=fresh.inspect
    package=module('_validation_package',ROOT/'orchestrator/experiment_modal_package.py')
    package.WORKER=bridge.WORKER;package.SUPPORT_FILES=bridge.SUPPORT_FILES
    bridge.emit=package.emit
    fresh_owner=module('_validation_owner',ROOT/'orchestrator/experiment_owner.py')
    owner.verify_item4=fresh_owner.verify_item4
    from orchestrator import modal_executor
    executor=module('_validation_executor',ROOT/'orchestrator/modal_executor.py')
    # Preserve all existing direct-import aliases to this one verifier. The
    # reviewed body uses the same globals and adds only a local policy import.
    policy.require(not executor.verify_package.__code__.co_freevars and
        not modal_executor.verify_package.__code__.co_freevars,'VERIFIER_CLOSURE')
    modal_executor.verify_package.__code__=executor.verify_package.__code__
    from orchestrator import modal_item4_budget
    budget=module('_validation_budget',ROOT/'orchestrator/modal_item4_budget.py')
    modal_item4_budget.reserve.__code__=budget.reserve.__code__
    from orchestrator import experiment_partition_input as partitions
    fresh_partitions=module('_validation_partitions',ROOT/'orchestrator/experiment_partition_input.py')
    partitions.reviewed=fresh_partitions.reviewed
    return c,policy,(b,h,old,rec),e



def connect_evidence(driver,c,manifest):
    """Replay the exact existing scientific producer's supplementary view route.

    c.load independently authenticates this R42 manifest and every original.
    Reuse its scanner/descriptor producer, never accept a measured superset or
    skip a registered view. Only this same lane/context/config may use it.
    """
    from orchestrator import scientific_intake as intake,revision_evidence
    from orchestrator.item4_validation_admission import require
    original=intake.load_views
    def views(root,ref,*,stage,idea_ids):
        require(Path(root).resolve()==driver.context.resolve() and ref==driver.config['private_intake'] and
            stage in ('run_spec_author','run_spec_review') and idea_ids==driver.config['idea_ids'],'EVIDENCE_DELIVERY_SCOPE')
        descriptors,files=original(root,ref,stage=stage,idea_ids=idea_ids)
        registry=json.loads((driver.context/ref['path']).read_bytes())
        cases=intake.cohort((driver.context/registry['cohort']).read_bytes())
        return revision_evidence.append(descriptors,files,manifest,c.RECORD/'evidence',cases)
    intake.load_views=views
    return original


def preserved(driver,selected):
    from orchestrator.review_submission import canonical
    from orchestrator.item4_validation_admission import require,sha
    raw=driver.store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    require(sha(raw.encode())==selected['state_sha256'],'ACTIVATION_STATE')
    require(sha((driver.state/'lane.json').read_bytes())==selected['config_sha256'],'ACTIVATION_CONFIG')
    for name,pin in selected['context_files'].items():
        from orchestrator.context_budget import relative_file
        require(sha(relative_file(driver.context,name).read_bytes())==pin,'OPEN_FINDINGS_CHANGED')
    local=[dict(x) for x in driver.store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    scientific=[dict(x) for x in driver.store.batch.db.execute("SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid")]
    require(sha(canonical(local))==selected['local_calls_sha256'] and
        sha(canonical(scientific))==selected['scientific_calls_sha256'],'ORIGINAL_ACCOUNTING_CHANGED')
    require(not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'ACTIVE_CALL')
    return raw


def activate(driver,policy):
    """One compare-and-swap, with the original review/findings/calls untouched."""
    from orchestrator import experiment_approval as approval,private_records as pr
    from orchestrator.manual_driver import write_once
    from orchestrator.review_submission import canonical
    selected=policy.contract();implementation=policy.authority()
    raw=preserved(driver,selected);value=json.loads(raw)
    policy.require(value['phase']=='BLOCKED' and value['reason']=='UNRESOLVED_AFTER_THREE_REVISIONS'
        and value['rounds']=={'run_spec_author':selected['author_round'],'run_spec_review':selected['review_round']} and not value.get('pending'),'ACTIVATION_SCOPE')
    pending={'id':selected['review_call'],'stage':'run_spec_review','round':selected['review_round'],
        'workspace':str(Path(value['review']).parent)}
    # All actual delivered artifacts/tests/native review are requalified first.
    preview=approval.inspect(driver,value,pending)
    policy.require(preview['validation_admission']==policy.record_for(selected,implementation),'ACTIVATION_REVIEW')
    folder=driver.state.parent/CHANGE
    pr.mkdir(folder,parents=True,exist_ok=True)
    with pr.open_file(folder/'ACTIVATION_INTENT.json','xb') as f:
        f.write(canonical({'state_sha256':policy.sha(raw.encode()),'implementation_sha256':implementation,
            'review_sha256':selected['review_sha256'],'scientific_verdict':'REVISE','scope':'validation only'}))
    write_once(folder/'ORIGINAL_STATE.json',raw.encode())
    approval.record(driver,value,pending)
    value.update(phase='COMMIT_SPEC',spec_review=value['review'],reason='VALIDATION_ONLY_OPEN_FINDINGS_RETAINED')
    value.setdefault('interventions',[]).append({'kind':'REVIEWED_VALIDATION_ONLY_ADMISSION',
        'original_state_sha256':selected['state_sha256'],'implementation_sha256':implementation,
        'scientific_review_sha256':selected['review_sha256'],'findings_closed':False})
    payload=canonical(value).decode();db=driver.store.db
    db.execute('BEGIN IMMEDIATE')
    try:
        policy.require(preserved(driver,selected)==raw,'ACTIVATION_CHANGED')
        policy.require(db.execute('UPDATE manual_state SET payload=? WHERE id=1 AND payload=?',(payload,raw)).rowcount==1,'ACTIVATION_CAS')
        db.execute('INSERT INTO events VALUES(?,?,?)',('validation-only-admission:'+selected['run_id'],selected['run_id'],
            json.dumps({'original_state_sha256':selected['state_sha256'],'new_state_sha256':policy.sha(payload.encode()),
                'implementation_sha256':implementation,'review_sha256':selected['review_sha256'],'findings_closed':False},sort_keys=True)))
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK');raise
    return {'status':'VALIDATION_ONLY_READY','phase':'COMMIT_SPEC','model_calls':0,'provider_calls':0,'findings_closed':False}


def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['verify','activate','advance','prepare-preprocessing','prepare-execution','measure-benchmark'])
    parser.add_argument('--jobs');parser.add_argument('--destination');args=parser.parse_args(argv)
    c,policy,original,evidence=load()
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    driver=ExperimentDriver(c.LANE)
    try:
        with lock(driver.state/'driver.lock'):
            driver.guard();c.originals(driver,*original)
            connect_evidence(driver,c,evidence)
            selected=policy.contract()
            if args.action=='verify':result={'status':'VERIFIED_HELD','model_calls':0,'provider_calls':0}
            elif args.action=='activate':
                c.response_native_equivalence(driver,json.loads((c.ROOT/c.RESPONSE_DOCUMENT).read_bytes()))
                result=activate(driver,policy)
            else:
                value=driver.current()
                policy.require(value['phase'] in {'COMMIT_SPEC','EMIT_EXPERIMENT_PACKAGE','EXECUTE_EXPERIMENT'},'EXECUTION_PHASE')
                from orchestrator import experiment_approval as approval
                approved=approval.verify(driver,value)
                policy.require('validation_admission' in approved,'EXACT_VALIDATION_REQUIRED')
                if args.action=='advance':
                    # One existing transition; never enter a model stage or FULL admission.
                    result=driver._advance()
                elif args.action=='measure-benchmark':
                    from orchestrator.experiment_projection import produce
                    result=produce(driver,value,kind='hardware')
                else:
                    from orchestrator import experiment_provisioning as provisioning,private_records as pr
                    from orchestrator.review_contract import strict_json
                    policy.require(args.jobs is not None and args.destination is not None,'PREPARATION_ARGUMENTS')
                    rows=strict_json(pr.check(args.jobs).read_bytes())
                    result=provisioning.prepare(driver,value,rows,args.destination,
                        kind='preprocessing' if args.action=='prepare-preprocessing' else 'fit')
        print(json.dumps(result,sort_keys=True))
    finally:driver.store.db.close();driver.store.batch.db.close()

if __name__=='__main__':
    os.umask(0o077);main()
