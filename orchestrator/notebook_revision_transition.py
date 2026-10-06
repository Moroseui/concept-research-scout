"""Held continuation of the same four-call item2 run under notebook scope.

No new owner, allowance, retry, altered review or ledger-row update. The old
lane (including its HALT) stays intact. The selected new lane gets the exact
reviewed context additions and resumes the next ordinary revision round.
"""
import json
import os
from pathlib import Path
import sqlite3
from orchestrator import private_records, autonomy_limits
from orchestrator.manual_executor import read, digest, inventory, atomic, lock
from orchestrator.stocktake_recovery import connect
from orchestrator.analysis_revision_transition import rows, sha
from orchestrator.notebook_revision import AUTHORITY
from tools.deploy_manual_lane import bound

CHECKPOINT='b846782f0b0cf1be25c56682e6b91b530806b6cafa05b846a3608b33710cfc18'
KEY='stocktake-6b556dba36d299c05b8b7770:notebook-scope-continuation'


def checkpoint():
    path=Path(__file__).resolve().parents[1]/'docs/ITEM2_NOTEBOOK_CHECKPOINT.json'
    if digest(path.read_bytes())!=CHECKPOINT:raise ValueError('NOTEBOOK_CHECKPOINT_CHANGED')
    authority=path.with_name('ITEM2_NOTEBOOK_AUTHORITY.txt')
    if digest(authority.read_bytes())!=AUTHORITY:raise ValueError('NOTEBOOK_AUTHORITY_CHANGED')
    return read(path)


def prior(host, *, completed=False):
    p=checkpoint();old=bound(host,p['old_state'])
    if old.is_symlink() or digest((old/'HALT').read_bytes())!=p['halt_sha256']:
        raise ValueError('NOTEBOOK_OLD_HOLD_CHANGED')
    if digest((old/'lane.json').read_bytes())!=p['config_sha256']:
        raise ValueError('NOTEBOOK_OLD_CONFIG_CHANGED')
    config=read(old/'lane.json')
    if config['source']!=p['old_source'] or config['run_id']!=p['run_id'] or config['item_number']!=2:
        raise ValueError('NOTEBOOK_OLD_IDENTITY')
    if digest((old/'preparation-plan.json').read_bytes())!=p['plan_sha256']:
        raise ValueError('NOTEBOOK_OLD_PLAN_CHANGED')
    if digest(bound(host,config['owner_path']).read_bytes())!=p['owner_sha256']:
        raise ValueError('NOTEBOOK_OLD_OWNER_CHANGED')
    if sha(inventory(old/'context'))!=p['context_sha256']:
        raise ValueError('NOTEBOOK_OLD_CONTEXT_CHANGED')
    with connect(old/'jobs.sqlite') as db:
        for table,pin in p['tables'].items():
            if sha(rows(db,table))!=pin:raise ValueError('NOTEBOOK_OLD_ROWS_CHANGED:'+table)
        current=json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
        if (current['phase']!='run_spec_author' or current.get('reason')!='REVISION_REQUIRED'
                or current['rounds']!={'run_spec_author':2,'run_spec_review':2}):
            raise ValueError('NOTEBOOK_EXPECTED_FOUR_CALL_REVISION')
        if digest(bound(host,current['review']).read_bytes())!=p['review_sha256']:
            raise ValueError('NOTEBOOK_ORIGINAL_REVIEW_CHANGED')
    with connect(bound(host,config['batch_ledger'])/'jobs.sqlite') as db:
        for ident,pin in p['global_rows'].items():
            row=db.execute('SELECT * FROM autonomy_calls WHERE id=?',(ident,)).fetchone()
            if row is None or sha(dict(row))!=pin:raise ValueError('NOTEBOOK_GLOBAL_CALL_CHANGED')
        owner=db.execute('SELECT * FROM autonomy_runs WHERE id=?',(p['run_id'],)).fetchone()
        value=dict(owner) if owner else {}
        if completed and value.get('status')=='COMPLETE':value['status']='ACTIVE'
        if sha(value)!=p['global_owner_sha256']:raise ValueError('NOTEBOOK_GLOBAL_OWNER_CHANGED')
        if db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone():
            raise ValueError('NOTEBOOK_ACTIVE_CALL')
    return config,current


def preserved_predecessors(host):
    # Both frozen generations remain initialized: the two-call recorder stop
    # and its four-call continuation. Validate each checkpoint; never whitelist
    # a lane merely because it names the same run or has no active process.
    from orchestrator import analysis_revision_transition as earlier
    current,_=prior(host);p=checkpoint();ancestor=earlier.checkpoint()
    if (current.get('revision_continuation')!=earlier.KEY
            or ancestor['run_id']!=p['run_id']
            or ancestor['old_state']==p['old_state']):
        raise ValueError('NOTEBOOK_PREDECESSOR_CHAIN_CHANGED')
    earlier.prior(host)
    return [bound(host,p['old_state']),bound(host,ancestor['old_state'])]


def completed_predecessors(host):
    """Read-only closure of the exact two frozen generations after acceptance.

    This is a promotion-only connection. It grants no scientific admission,
    migration, new allowance or changed historical outcome.
    """
    from orchestrator import analysis_revision_transition as earlier
    from tools.deploy_manual_lane import system
    host=Path(host).resolve();p=checkpoint();ancestor=earlier.checkpoint()
    ledger=bound(host,'/var/lib/research-system-autonomy/reviews/jobs.sqlite')
    if not ledger.exists():return set()
    with connect(ledger) as db:
        row=db.execute('SELECT job,payload FROM events WHERE id=?',(KEY,)).fetchone()
        if row is None:return set()
        run=db.execute('SELECT status FROM autonomy_runs WHERE id=?',(p['run_id'],)).fetchone()
        if run is None or run['status']!='COMPLETE':return set()
        binding=json.loads(row['payload'])
        if row['job']!=p['run_id']:raise ValueError('NOTEBOOK_CLOSURE_EVENT_RUN')
        accepted=db.execute('SELECT job,payload FROM events WHERE id=?',(p['run_id']+':accepted',)).fetchone()
        if accepted is None or accepted['job']!=p['run_id']:
            raise ValueError('NOTEBOOK_CLOSURE_ACCEPTANCE_REQUIRED')
        acceptance=json.loads(accepted['payload'])
        global_calls=[dict(x) for x in db.execute('SELECT * FROM autonomy_calls WHERE change_id=?',(p['run_id'],))]
        prior_event=db.execute('SELECT job,payload FROM events WHERE id=?',(earlier.KEY,)).fetchone()
    # These existing verifiers bind every predecessor row, original review,
    # context, owner, hold and plan. Completion changes only the owner status.
    before,_=prior(host,completed=True);earlier.prior(host,completed=True)
    if (before.get('revision_continuation')!=earlier.KEY or ancestor['run_id']!=p['run_id']
            or ancestor['old_state']==p['old_state']):
        raise ValueError('NOTEBOOK_PREDECESSOR_CHAIN_CHANGED')
    state_name=binding.get('state','')
    if (not state_name.startswith('/var/lib/research-system-manual-sprint10/releases/')
            or not state_name.endswith('/lane') or '..' in Path(state_name).parts):
        raise ValueError('NOTEBOOK_CLOSURE_DESTINATION')
    state=bound(host,state_name)
    if state.is_symlink() or (state/'lane.json').is_symlink():raise ValueError('NOTEBOOK_CLOSURE_ALIAS')
    config=read(state/'lane.json')
    expected={'kind':KEY,'run_id':p['run_id'],'source':config['source'],'state':state_name,
        'filesystem_root':'/','config_sha256':sha(config),'checkpoint_sha256':CHECKPOINT,
        'operator_decision_sha256':AUTHORITY,'preserved_call_ids':p['call_rows'],'allowance_reset':False}
    if (binding!=expected or read(state/'notebook-continuation.json')!=binding
            or config.get('notebook_revision_continuation')!=KEY
            or config.get('run_id')!=p['run_id'] or config.get('item_number')!=2):
        raise ValueError('NOTEBOOK_CLOSURE_CONTINUATION_CHANGED')
    predecessor=bound(host,p['old_state'])
    if (prior_event is None or prior_event['job']!=p['run_id']
            or json.loads(prior_event['payload'])!=read(predecessor/'revision-continuation.json')):
        raise ValueError('NOTEBOOK_CLOSURE_PREDECESSOR_EVENT_CHANGED')
    if digest((state/'REPORT.md').read_bytes())!=acceptance.get('report_sha256'):
        raise ValueError('NOTEBOOK_CLOSURE_REPORT_CHANGED')
    with connect(state/'jobs.sqlite') as db:
        current=json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
        calls=rows(db,'manual_calls')
    if current.get('phase')!='COMPLETE' or not calls or any(c['status']!='COMPLETE' for c in calls):
        raise ValueError('NOTEBOOK_CLOSURE_NOT_TERMINAL')
    if (any(c['kind']!='scientific' or c['status']!='COMPLETE' for c in global_calls)
            or {c['id'] for c in calls}!={c['id'] for c in global_calls}
            or not set(p['call_rows']).issubset({c['id'] for c in calls})):
        raise ValueError('NOTEBOOK_CLOSURE_CALL_SET_CHANGED')
    # The continuation copied these original calls without editing them.
    with connect(predecessor/'jobs.sqlite') as db:preserved=rows(db,'manual_calls')
    if any(row not in calls for row in preserved):raise ValueError('NOTEBOOK_CLOSURE_COPIED_CALL_CHANGED')
    paths={bound(host,p['old_state']),bound(host,ancestor['old_state'])}
    if state in paths:raise ValueError('NOTEBOOK_CLOSURE_DESTINATION')
    for lane in [*paths,state]:
        for suffix in ('.service','.timer'):
            if system(host,'state',lane.parent.name+suffix)!={'enabled':False,'active':False}:
                raise ValueError('NOTEBOOK_CLOSURE_UNITS_NOT_HELD')
    return paths


def promotion_check(host,previous,source,entrypoint,report):
    p=checkpoint();preserved=preserved_predecessors(host);autonomy_limits.authority(source)
    if (entrypoint!='analysis' or previous['source']!=p['old_source']
            or previous['state']+'/lane'!=p['old_state']
            or digest((Path(source)/'deploy/manual-lane/runtime.promotion.json').read_bytes())!=previous['runtime_sha256']):
        raise ValueError('NOTEBOOK_PROMOTION_SCOPE')
    return preserved


def validate_driver(driver):
    binding=read(driver.state/'notebook-continuation.json')
    if (binding['kind']!=KEY or binding['run_id']!=checkpoint()['run_id']
            or binding['source']!=driver.config['source']
            or binding['state']!=str(driver.state.resolve())
            or binding['config_sha256']!=sha(driver.config)):
        raise ValueError('NOTEBOOK_CONTINUATION_BINDING')
    event=driver.store.batch.db.execute('SELECT payload FROM events WHERE id=?',(KEY,)).fetchone()
    if event is None or event[0]!=json.dumps(binding,sort_keys=True):
        raise ValueError('NOTEBOOK_CONTINUATION_EVENT_CHANGED')
    prior(Path(binding['filesystem_root']),completed=driver.current()['phase']=='COMPLETE')
    autonomy_limits.authority(driver.root)


@private_records.private_umask
def prepare(state,root,report,plan_path,*,filesystem_root=Path('/')):
    from tools import manual_promotion, deploy_manual_lane as deploy
    from orchestrator.manual_driver import git,write_once
    from orchestrator.analysis_driver import release_identities,verify_plan
    from orchestrator.autonomy_review import verify_result
    host=Path(filesystem_root).resolve()
    state,root,report,plan_path=map(Path,(state,root,report,plan_path))
    if host==Path('/') and os.getuid()!=1003:raise ValueError('NOTEBOOK_OWNER_REQUIRED')
    if any(not p.resolve().is_relative_to(host) for p in (state,root,report,plan_path)):
        raise ValueError('NOTEBOOK_PATH_ESCAPE')
    if state.exists() or state.is_symlink():raise ValueError('NOTEBOOK_EXISTING_DESTINATION')
    with lock(state.parent/'notebook-continuation.lock'):
        before,current=prior(host);p=checkpoint();old=bound(host,p['old_state'])
        head=git(root,'rev-parse','HEAD');branch=git(root,'branch','--show-current')
        approved=verify_result(report.parent);selected=read(bound(host,manual_promotion.POINTER))
        runtime=digest(Path(os.environ['RESEARCH_MANUAL_RUNTIME_CONFIG']).read_bytes())
        if (approved['verdict']!='APPROVE' or approved['source_sha']!=head
                or approved['report_sha256']!=digest(report.read_bytes())
                or approved['runtime_sha256']!=runtime):
            raise ValueError('NOTEBOOK_EXACT_APPROVAL_REQUIRED')
        if (git(root,'status','--porcelain') or not branch.startswith('astra/manual-server-')
                or root.resolve()!=bound(host,selected['state'])/'repository'
                or state.resolve()!=bound(host,selected['state'])/'lane'
                or selected['source']!=head or selected['runtime_sha256']!=runtime):
            raise ValueError('NOTEBOOK_HELD_INSTALL_REQUIRED')
        for unit in selected['units']+[Path(p['old_state']).parent.name+x for x in ('.service','.timer')]:
            if deploy.system(host,'state',unit)!={'enabled':False,'active':False}:
                raise ValueError('NOTEBOOK_UNITS_NOT_HELD')
        plan_raw=plan_path.read_bytes();plan=json.loads(plan_raw)
        manifest=read(report.parent/'packet-manifest.json')
        if manifest['files'].get('evidence/analysis-plan.json')!=digest(plan_raw):
            raise ValueError('NOTEBOOK_REVIEWED_PLAN_REQUIRED')
        verify_plan(plan)
        # The former preparation selection remains a preserved baseline. Only
        # the new reviewed notebook capability/context field may be added.
        original=read(old/'preparation-plan.json')
        if {k:v for k,v in plan.items() if k not in {'context','context_files','artifacts','notebook_revision'}} != {
                k:v for k,v in original.items() if k not in {'context','context_files','artifacts'}}:
            raise ValueError('NOTEBOOK_UNRELATED_PLAN_CHANGE')
        if plan['artifacts'][:len(current['artifacts'])]!=current['artifacts']:
            raise ValueError('NOTEBOOK_EXISTING_ARTIFACTS_CHANGED')
        fresh=Path(plan['context']);old_files=inventory(old/'context')
        for name,pin in old_files.items():
            if digest((fresh/name).read_bytes())!=pin:raise ValueError('NOTEBOOK_PRESERVED_CONTEXT_CHANGED')
        ledger=bound(host,before['batch_ledger'])/'jobs.sqlite'
        if (ledger.parent/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
        with connect(ledger) as db:
            if db.execute('SELECT 1 FROM events WHERE id=?',(KEY,)).fetchone():
                raise ValueError('NOTEBOOK_ALREADY_CONTINUED')
        config={**before,'source':head,'root':str(root.resolve()),'branch':branch,
            'context':str(state/'context'),'workspace_root':str(state.parent/'lane-scientific-workspaces'),
            'owner_path':str(bound(host,before['owner_path'])),
            'engine_review':{'path':str(report.resolve()),'sha256':digest(report.read_bytes())},
            'plan_sha256':digest(plan_raw),'notebook_revision':plan['notebook_revision'],
            'notebook_revision_continuation':KEY,'notebook_filesystem_root':str(host)}
        config.pop('revision_continuation',None);config.pop('revision_filesystem_root',None)
        config['profile_files'],config['engine_files']=release_identities(root)
        if config['profile_files']!=before['profile_files']:raise ValueError('NOTEBOOK_PROFILE_CHANGED')
        binding={'kind':KEY,'run_id':p['run_id'],'source':head,'state':str(state.resolve()),
            'filesystem_root':str(host),'config_sha256':sha(config),'checkpoint_sha256':CHECKPOINT,
            'operator_decision_sha256':AUTHORITY,'preserved_call_ids':p['call_rows'],'allowance_reset':False}
        write_once(state.parent/'notebook-continuation-intent.json',json.dumps(binding,sort_keys=True).encode())
        private_records.mkdir(state)
        for path in old.iterdir():
            if path.name in {'jobs.sqlite','jobs.sqlite-wal','jobs.sqlite-shm','lane.json','context','preparation-plan.json','HALT'}:continue
            if path.is_dir():private_records.copytree(path,state/path.name)
            else:private_records.copyfile(path,state/path.name)
        private_records.copyfile(old/'HALT',state/'predecessor-HALT.txt')
        private_records.copytree(fresh,state/'context')
        private_records.write_bytes(state/'preparation-plan.json',plan_raw)
        with connect(old/'jobs.sqlite') as src,sqlite3.connect(state/'jobs.sqlite') as dst:src.backup(dst)
        current['artifacts']=plan['artifacts']
        current.setdefault('interventions',[]).append({'kind':'OPERATOR_NOTEBOOK_SCOPE','authority_sha256':AUTHORITY})
        with sqlite3.connect('file:'+str(state/'jobs.sqlite')+'?mode=rw',uri=True) as db:
            db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(current),))
        atomic(state/'lane.json',config);atomic(state/'notebook-continuation.json',binding)
        with sqlite3.connect('file:'+str(ledger)+'?mode=rw',uri=True) as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('INSERT INTO events VALUES(?,?,?)',(KEY,p['run_id'],json.dumps(binding,sort_keys=True)))
        prior(host);private_records.check_tree(state)
        return {'status':'CONTINUED_SAME_RUN','calls_used':4,'call_limit':16,'next':'run_spec_author',
                'next_author_attempt':3,'original_hold_preserved':True,'source':head}
