"""Item6-only image preparation; genuine approved requirements, existing owner.

This is infrastructure, not a scientific allowance or an execution selection.
It never creates/completes an owner, changes requirements, or reads patient data.
"""
from pathlib import Path
from types import SimpleNamespace as NS
import sqlite3
import tempfile
from contextlib import contextmanager
import re
from orchestrator import diagnostics_policy as policy, private_records as pr
from orchestrator.manual_executor import digest
from orchestrator.modal_executor import canonical
from orchestrator.review_contract import strict_json
from orchestrator import modal_pinned_image as image

PURPOSE=image.CPU_PURPOSE
OPERATION='item6-reviewed-cpu-image-v1'
RUN=policy.RUN_ID
SCHEMA='item6-pinned-image-build/v1'
REFERENCE_FIELDS={'state','lane_sha256','source','owner_sha256','reviewed_execution_sha256','program_sha256','requirements'}


def requirements(value):
    if (not isinstance(value,dict) or set(value)!={'python','distributions'}
            or not re.fullmatch(r'3\.[0-9]+',str(value['python']))
            or not isinstance(value['distributions'],dict) or len(value['distributions'])>32):
        raise ValueError('DIAGNOSTICS_IMAGE_REQUIREMENTS')
    for name,version in value['distributions'].items():
        if (not isinstance(name,str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]{0,99}',name)
                or not isinstance(version,str) or not re.fullmatch(r'[0-9][A-Za-z0-9.+!_-]{0,79}',version)):
            raise ValueError('DIAGNOSTICS_IMAGE_REQUIREMENTS')
    normalized=[image.worker.name(n) for n in value['distributions']]
    if len(set(normalized))!=len(normalized):raise ValueError('DIAGNOSTICS_IMAGE_REQUIREMENTS_ALIAS')
    return value


def reference(value):
    if (not isinstance(value,dict) or set(value)!=REFERENCE_FIELDS
            or not isinstance(value['state'],str) or not Path(value['state']).is_absolute()
            or '..' in Path(value['state']).parts
            or not re.fullmatch('[0-9a-f]{40}',str(value['source']))
            or any(not re.fullmatch('[0-9a-f]{64}',str(value[k])) for k in REFERENCE_FIELDS-{'state','source','requirements'})):
        raise ValueError('DIAGNOSTICS_IMAGE_REVIEW_REFERENCE')
    requirements(value['requirements']);return value


def ledger_bytes(path):
    """The exact database plus existing WAL/SHM; absence is bound too."""
    path=Path(path);result={}
    for suffix in ('','-wal','-shm'):
        p=path.with_name(path.name+suffix)
        if not p.exists() and not p.is_symlink():
            if not suffix:raise ValueError('DIAGNOSTICS_IMAGE_LEDGER_MISSING')
            result[suffix]=None;continue
        checked=pr.check(p)
        if not checked.is_file() or checked.stat().st_nlink!=1 or checked.stat().st_size>268435456:
            raise ValueError('DIAGNOSTICS_IMAGE_LEDGER_FILE')
        info=checked.stat();raw=checked.read_bytes()
        after=checked.stat()
        metadata=(info.st_dev,info.st_ino,info.st_uid,info.st_gid,info.st_mode,info.st_size)
        if metadata!=(after.st_dev,after.st_ino,after.st_uid,after.st_gid,after.st_mode,after.st_size) or len(raw)!=info.st_size:
            raise ValueError('DIAGNOSTICS_IMAGE_LEDGER_CHANGED')
        result[suffix]={'bytes':raw,'sha256':digest(raw),'metadata':metadata}
    return result


@contextmanager
def readonly_ledger(path):
    # SQLite may need to create SHM even for mode=ro when a closed WAL ledger
    # lacks sidecars. Only a private temporary copy is writable. Originals and
    # their exact sidecar presence/hashes are checked before and after all reads.
    with tempfile.TemporaryDirectory(prefix='research-cpu-image-ledger-') as tmp:
        folder=pr.check(Path(tmp));before=ledger_bytes(path)
        for suffix,row in before.items():
            if row is not None:pr.write_bytes(folder/('jobs.sqlite'+suffix),row['bytes'])
        if ledger_bytes(path)!=before:raise ValueError('DIAGNOSTICS_IMAGE_LEDGER_CHANGED')
        db=sqlite3.connect((folder/'jobs.sqlite').as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
        try:
            yield db
        finally:
            db.close()
            if ledger_bytes(path)!=before:raise ValueError('DIAGNOSTICS_IMAGE_LEDGER_CHANGED')


def inspect_reviewed(state):
    """Read-only genuine package/approval verification; never initialize a lane."""
    from orchestrator import experiment_package, experiment_approval
    from orchestrator.diagnostics_contract import encoded,program_contract
    state=pr.check(Path(state));raw=pr.check(state/'lane.json').read_bytes();config=strict_json(raw)
    if config.get('item_number')!=6 or config.get('run_id')!=RUN:raise ValueError('DIAGNOSTICS_IMAGE_LANE')
    dbpath=pr.check(state/'jobs.sqlite')
    with readonly_ledger(dbpath) as db:
        row=db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()
        if row is None:raise ValueError('DIAGNOSTICS_IMAGE_REVIEWED_STATE_REQUIRED')
        value=strict_json(row['payload'])
        if value.get('phase') not in {'EXECUTE_EXPERIMENT','COLLECT_EXPERIMENT','result_interpretation_author','result_interpretation_review','UPDATE_STATE','REPORT','COMPLETE'}:
            raise ValueError('DIAGNOSTICS_IMAGE_REVIEW_NOT_COMPLETE')
        driver=NS(state=state,config=config,root=Path(config['root']),context=Path(config['context']),store=NS(db=db))
        package=state/'experiment-package'
        experiment_package.verify(driver,value,package)
        approved=experiment_approval.verify(driver,value)
        program_raw=pr.check(package/'code/analysis.program.json').read_bytes();program=strict_json(program_raw)
        if program.get('schema')!='scientific-program/v2':raise ValueError('DIAGNOSTICS_IMAGE_REVIEWED_PROGRAM')
        contract=program_contract(program['contract'])
        from orchestrator.context_budget import relative_file
        rows=[r for r in approved['artifacts'] if r['type']=='analysis_provenance']
        if len(rows)!=1:raise ValueError('DIAGNOSTICS_IMAGE_REVIEWED_PROVENANCE')
        row=rows[0];shown=pr.check(relative_file(driver.context,row['path'])).read_bytes()
        if digest(shown)!=row['sha256'] or strict_json(shown).get('program_contract')!=contract:
            raise ValueError('DIAGNOSTICS_IMAGE_REVIEWED_REQUIREMENTS')
        ref={'state':str(state),'lane_sha256':digest(raw),'source':config['source'],
            'owner_sha256':digest(encoded(config['owner_binding'])),
            'reviewed_execution_sha256':value['reviewed_execution']['sha256'],
            'program_sha256':digest(program_raw),'requirements':contract['requirements']}
        return reference(ref)


def reviewed(ref):
    reference(ref)
    if inspect_reviewed(ref['state'])!=ref:raise ValueError('DIAGNOSTICS_IMAGE_REVIEW_CHANGED')
    return ref


def validate_selection(selected,ref):
    reference(ref);image.validate(selected)
    if not image.worker.cpu(selected):raise ValueError('DIAGNOSTICS_IMAGE_CPU_SELECTION')
    req=ref['requirements']
    if '.'.join(selected['python_version'].split('.')[:2])!=req['python']:
        raise ValueError('DIAGNOSTICS_IMAGE_REVIEWED_PYTHON')
    if any(selected['packages'].get(image.worker.name(n))!=v for n,v in req['distributions'].items()):
        raise ValueError('DIAGNOSTICS_IMAGE_REVIEWED_PACKAGES')
    return selected


def owner(accounts,binding):
    from orchestrator.diagnostics_contract import encoded
    row=accounts.db.execute('SELECT binding,status FROM autonomy_runs WHERE id=?',(RUN,)).fetchone()
    if row is None or row['status']!='ACTIVE':raise ValueError('DIAGNOSTICS_IMAGE_ACTIVE_OWNER_REQUIRED')
    value=strict_json(row['binding']);scope=value.get('execution_scope',{})
    ref=binding['reviewed_requirements']
    from orchestrator.spending_continuation import lane
    continued=lane(accounts.batch,RUN,value,ref['source'])
    selected_source=continued[1]['source'] if continued else value.get('source')
    selected_state=str(continued[0]) if continued else value.get('state')
    if (digest(encoded(value))!=ref['owner_sha256'] or selected_source!=ref['source']
            or selected_state!=ref['state'] or value.get('run_id')!=RUN
            or scope.get('item_number')!=6 or scope.get('authority_sha256')!=policy.authority()):
        raise ValueError('DIAGNOSTICS_IMAGE_EXISTING_OWNER_CHANGED')
    return value


def selected_asset(row):
    value=strict_json(row['binding'])
    if value.get('purpose')!=PURPOSE:return False
    from orchestrator.modal_environment_budget import validate_binding
    validate_binding(value)
    if (row['run']!=RUN or row['id']!=digest(canonical(value))
            or row['reserved_micro_usd']!=value['envelope']['cost']['reserved_micro_usd']):
        raise ValueError('DIAGNOSTICS_IMAGE_ASSET_BINDING')
    return True


def environment(base,proof):
    """Exact image receipt selects one fixed interpreter, never an arbitrary path."""
    if not isinstance(proof,dict) or proof.get('schema')!='pinned-image-consumer-provenance/v1':
        raise ValueError('DIAGNOSTICS_IMAGE_PROVENANCE_REQUIRED')
    from orchestrator.modal_environment_budget import validate_binding
    binding=validate_binding(proof['binding'])
    fields={'schema','binding','asset_receipt_sha256','native_receipt_sha256','result','scientific_environment','scientific_acceptance','gpu_verified'}
    if (set(proof)!=fields or binding['purpose']!=PURPOSE or proof['scientific_acceptance'] is not False or proof['gpu_verified'] is not False
            or any(not re.fullmatch('[0-9a-f]{64}',str(proof[k])) for k in ('asset_receipt_sha256','native_receipt_sha256'))):
        raise ValueError('DIAGNOSTICS_IMAGE_PROVENANCE_REQUIRED')
    spec=image.consumer_spec(proof['result'],binding)
    if (proof['scientific_environment']!=spec or base!={'schema':'diagnostics-environment/v1','image_id':spec['image_id'],
            'requirements':binding['reviewed_requirements']['requirements']}):
        raise ValueError('DIAGNOSTICS_IMAGE_CONSUMER_BINDING')
    return {**base,'interpreter':image.worker.TARGET+'/bin/python','image_proof_sha256':digest(canonical(proof))}


def runtime_environment(base,assets):
    """Root's exact proof is mandatory only for the new optional interpreter mode."""
    if set(assets.get('environment',{}))==set(base):
        if 'pinned_image_provenance' in assets:raise ValueError('DIAGNOSTICS_IMAGE_UNUSED_PROOF')
        return base
    from orchestrator.manual_host_guard import trusted
    ref=assets.get('pinned_image_provenance')
    if not isinstance(ref,dict) or set(ref)!={'path','sha256'} or not re.fullmatch('[0-9a-f]{64}',str(ref['sha256'])):
        raise ValueError('DIAGNOSTICS_IMAGE_PROVENANCE_REQUIRED')
    path=trusted(Path(ref['path']));raw=pr.check(path).read_bytes()
    if len(raw)>262144 or digest(raw)!=ref['sha256']:raise ValueError('DIAGNOSTICS_IMAGE_PROVENANCE_CHANGED')
    return environment(base,strict_json(raw))
