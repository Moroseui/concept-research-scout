"""One pre-dispatch CPU dependency update; never renews source/calls/allowances.

The caller must qualify the genuine independent report through the existing
review queue first. This tool checks the supplied exact report/source/binding;
it does not create or qualify an independent approval.
"""
import argparse
import fcntl
import json
import re
import sqlite3
import subprocess
from pathlib import Path
from orchestrator import cpu_package, private_records
from orchestrator.manual_executor import atomic, digest

RUN = 'sprint10-cpu-3b82380564e25cf2'
SOURCE = '7f781a56479ae3ae3cb272616b09ef66b2e39552'
OLD_ENV = '8b67dd3e70e31b3ce5d46018e97b8d499c64ca1750b642c33d8631542ca10df1'
NEW_ENV = '0f71b0d0a8131090bca668b7da55e3aecf70392687b23dd7f7a264f0532fb34a'


def table_snapshot(state):
    with sqlite3.connect('file:'+str(state/'jobs.sqlite')+'?mode=ro', uri=True) as db:
        db.row_factory=sqlite3.Row
        tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {name:[dict(r) for r in db.execute('SELECT * FROM "'+name.replace('"','""')+'" ORDER BY rowid')] for name in tables}


def checked_update(config,new_cpu,rows):
    if config.get('run_id')!=RUN or config.get('source')!=SOURCE or config.get('backend')!='cpu':
        raise ValueError('EXACT_EXISTING_CPU_RUN_REQUIRED')
    states=rows.get('manual_state',[])
    if len(states)!=1 or json.loads(states[0]['payload']).get('phase')!='EMIT_PACKAGE':
        raise ValueError('CPU_PRE_DISPATCH_PHASE_REQUIRED')
    if any(rows.get(name) for name in ['jobs','events','manual_packages','manual_collections','manual_recoveries']):
        raise ValueError('CPU_ALREADY_PREPARED_OR_DISPATCHED')
    calls=rows.get('manual_calls',[])
    if len(calls)!=2 or {r['stage'] for r in calls}!={'run_spec_author','run_spec_review'} or any(r['status']!='COMPLETE' or r['attempt']!=1 for r in calls):
        raise ValueError('EXACT_COMPLETED_SPEC_PAIR_REQUIRED')
    old=config['cpu'];allowed={'environment_root','environment_sha256','packages'}
    if set(new_cpu)!=set(old) or any(new_cpu[k]!=old[k] for k in old if k not in allowed):
        raise ValueError('CPU_NON_DEPENDENCY_CHANGE_REFUSED')
    if old['environment_sha256']!=OLD_ENV or new_cpu['environment_sha256']!=NEW_ENV:
        raise ValueError('CPU_ENVIRONMENT_PINS_CHANGED')
    if old['environment_root']!='/opt/research-system-cpu-tools/m2-python312-v1' or new_cpu['environment_root']!='/opt/research-system-cpu-tools/m2-python312-xgb341-v2':
        raise ValueError('CPU_ENVIRONMENT_PATH_CHANGED')
    if new_cpu['packages']!=old['packages']+['xgboost-cpu==3.4.1']:
        raise ValueError('CPU_EXISTING_PACKAGE_VERSIONS_CHANGED')
    return {**config,'cpu':new_cpu}


def preserved_pins(config):
    root=Path(config['root'])
    files={**config['engine_files'],**config['scientific_files']}
    files.update({config['authority_path']:config['authority_sha256']})
    for name,want in files.items():
        if digest((root/name).read_bytes())!=want:raise ValueError('CPU_SOURCE_OR_AUTHORITY_CHANGED')
    if json.loads(Path(config['owner_path']).read_text())!=config['owner_binding']:raise ValueError('CPU_OWNER_CHANGED')
    if digest(Path(config['engine_review']['path']).read_bytes())!=config['engine_review']['sha256']:raise ValueError('CPU_SOURCE_APPROVAL_CHANGED')
    if subprocess.check_output(['git','status','--porcelain'],cwd=root):raise ValueError('CPU_REPOSITORY_DIRTY')
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()


@private_records.private_umask
def apply(state,binding,report,report_sha256,reviewed_root,output):
    state,report,reviewed_root,output=map(Path,(state,report,reviewed_root,output))
    raw=report.read_bytes()
    pin=subprocess.check_output(['git','rev-parse','HEAD'],cwd=reviewed_root,text=True).strip()
    if digest(raw)!=report_sha256 or pin!=binding['reviewed_source'] or pin not in raw.decode() or re.findall(r'^## Verdict: (.+?)\s*$',raw.decode(),re.M)!=['APPROVE']:
        raise ValueError('EXACT_QUALIFIED_CORRECTION_APPROVAL_REQUIRED')
    if subprocess.check_output(['git','status','--porcelain'],cwd=reviewed_root):raise ValueError('REVIEWED_CORRECTION_DIRTY')
    if output.exists():raise ValueError('EXISTING_CPU_UPDATE_RECORD_RECONCILE_NO_RETRY')
    private_records.check_tree(state)
    with (state/'driver.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        original=(state/'lane.json').read_bytes()
        if digest(original)!=binding['lane_sha256']:raise ValueError('CPU_LANE_BINDING_CHANGED')
        config=json.loads(original);rows=table_snapshot(state)
        if digest(json.dumps(rows,sort_keys=True).encode())!=binding['database_rows_sha256']:raise ValueError('CPU_CALL_OR_STATE_BINDING_CHANGED')
        if any((state/p).exists() for p in ['prepared','prepared-package','package','cpu-execution','collected']):raise ValueError('CPU_EXECUTION_ALREADY_PREPARED')
        new_cpu=cpu_package.runtime_config(reviewed_root)
        if digest(json.dumps(new_cpu,sort_keys=True).encode())!=binding['new_cpu_sha256']:raise ValueError('CPU_NEW_CONFIG_BINDING_CHANGED')
        updated=checked_update(config,new_cpu,rows)
        head=preserved_pins(config)
        if head!=binding['repository_head']:raise ValueError('CPU_SPEC_COMMIT_CHANGED')
        proof=cpu_package.runtime_preflight(Path(config['root']),new_cpu)
        if proof['notebook_code_sha256']!=config['notebook_code_sha256']:raise ValueError('CPU_REVIEWED_NOTEBOOK_CHANGED')
        private_records.mkdir(output)
        private_records.write_bytes(output/'lane.before.json',original)
        atomic(output/'INTENT.json',{'binding':binding,'report_sha256':report_sha256,'readiness':proof,'scope':'CPU dependency configuration only; installed/source/run/owner/calls/allowances unchanged'})
        atomic(state/'lane.json',updated,mode=0o600)
        if json.loads((state/'lane.json').read_text())!=updated or table_snapshot(state)!=rows or preserved_pins(updated)!=head:
            raise ValueError('CPU_POST_APPLY_INVARIANT_FAILED_STOP_NO_RETRY')
        private_records.check_tree(output);private_records.check_tree(state)
        result={'status':'APPLIED','before_sha256':digest(original),'after_sha256':digest((state/'lane.json').read_bytes()),'reviewed_correction':pin,'installed_source':config['source'],'run_id':config['run_id'],'calls_unchanged':True,'allowance_unchanged':True,'model_calls':0,'readiness':proof}
        atomic(output/'COMPLETE.json',result)
        return result


def main():
    parser=argparse.ArgumentParser()
    for name in ['state','binding','report','reviewed-root','output']:parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--binding-sha256',required=True);parser.add_argument('--report-sha256',required=True)
    args=parser.parse_args();raw=args.binding.read_bytes()
    if digest(raw)!=args.binding_sha256:raise ValueError('CPU_OPERATION_BINDING_CHANGED')
    print(json.dumps(apply(args.state,json.loads(raw),args.report,args.report_sha256,args.reviewed_root,args.output),indent=2))

if __name__=='__main__':main()
