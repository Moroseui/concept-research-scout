"""One linked recovery of the proven pre-Python, empty-volume download failure.

Original asset row/charge/status and provider records are never rewritten. A
new reservation counts both attempts in the unchanged item4 caps. This module
cannot authorize scientific calls. The separate mount correction selects only
one exact, proven terminal child; generic retries remain refused.
"""
from pathlib import Path
import json
from datetime import datetime, timezone
from orchestrator import private_records as pr
from orchestrator.manual_executor import digest, read
from orchestrator.modal_executor import canonical
from orchestrator import modal_direct_budget as budget

PARENT = "db2121f021ad93a1a49abc96a052a630f87bc4861076169268a50edd8d711033"
ERROR = "[dumb-init] /opt/conda/bin/python: No such file or directory\n"


def bound(ref, *, root=Path('/')):
    from orchestrator.modal_direct_continuation import mapped
    if not isinstance(ref,dict) or set(ref)!={'path','sha256'}:
        raise ValueError('DIRECT_RECOVERY_REFERENCE')
    p=mapped(root,ref['path'])
    if Path(root)==Path('/'):
        from orchestrator.manual_host_guard import trusted
        trusted(p)
    pr.check(p);raw=p.read_bytes()
    if digest(raw)!=ref['sha256']:raise ValueError('DIRECT_RECOVERY_RECORD_CHANGED')
    return json.loads(raw)


def selection(config, *, root=Path('/'), require_held=True):
    from orchestrator import modal_mount_recovery as mount
    if mount.selected(config):return mount.selection(config,root=root,require_held=require_held)
    from orchestrator.modal_direct_continuation import mapped, predecessor, held
    ref=config.get('recovery_from')
    if not isinstance(ref,dict) or set(ref)!={'config','terminal_proof','binding_sha256'} or ref['binding_sha256']!=PARENT:
        raise ValueError('DIRECT_RECOVERY_SELECTION')
    old=bound(ref['config'],root=root)
    expected={'schema','source','release','installation_record','installation_sha256','package',
              'package_manifest_sha256','batch_ledger','state','provider','units','prepared_from'}
    if set(old)!=expected or old['schema']!='direct-development-storage/v1':
        raise ValueError('DIRECT_RECOVERY_PREDECESSOR_SCHEMA')
    # This original reservation was made by the already-reviewed clock successor.
    # Verify both releases and unchanged first-preparation binding, not merely
    # a user-supplied path to an arbitrary failed record.
    first=predecessor(old,root=root)
    from tools.manual_promotion import manifest_check
    install=mapped(root,old['installation_record'])/'installed.json'
    if digest(pr.check(install).read_bytes())!=old['installation_sha256']:
        raise ValueError('DIRECT_RECOVERY_INSTALL_CHANGED')
    installed=manifest_check(root,old['installation_record'])
    if installed['source']!=old['source'] or installed['layout']['release']!=old['release']:
        raise ValueError('DIRECT_RECOVERY_RELEASE_CHANGED')
    if ref['config']['path']!='/etc/research-system-manual-sprint10/direct-inputs/'+old['source']+'/config.json':
        raise ValueError('DIRECT_RECOVERY_PREDECESSOR_PATH')
    expected_units={'research-manual-sprint10-direct-inputs-'+old['source'][:12]+suffix for suffix in ('.service','.timer')}
    if set(old['units'])!=expected_units:raise ValueError('DIRECT_RECOVERY_UNIT_SET')
    for name,row in old['units'].items():
        p=mapped(root,'/etc/systemd/system/'+name)
        if Path(root)==Path('/'):
            from orchestrator.manual_host_guard import trusted
            trusted(p)
        if set(row)!={'sha256'} or digest(pr.check(p).read_bytes())!=row['sha256']:raise ValueError('DIRECT_RECOVERY_UNIT_CHANGED')
    if Path(root)==Path('/') and require_held:held(old['units'])
    state=mapped(root,old['state']);pr.check_tree(state)
    binding=read(state/'binding.json')
    from orchestrator.modal_direct_continuation import check_binding
    check_binding(old,first,binding,(state/'binding.json').read_bytes())
    if digest(canonical(binding))!=PARENT or 'recovery' in binding:
        raise ValueError('DIRECT_RECOVERY_ORIGINAL_BINDING')
    handle=read(state/'provider/sandbox.json')
    failure=read(state/'FAILED.json')
    if (handle.get('binding_sha256')!=PARENT or failure!={'status':'FAILED','exit_code':2,
            'provider_id':handle['provider_id'],'no_automatic_retry':True}):
        raise ValueError('DIRECT_RECOVERY_ORIGINAL_FAILURE')
    proof=bound(ref['terminal_proof'],root=root)
    if (proof.get('provider_id')!=handle['provider_id'] or proof.get('exit_code')!=2
            or proof.get('stdout')!='' or proof.get('stderr')!=ERROR
            or proof.get('data_volume_file_count')!=0 or proof.get('data_volume_bytes')!=0
            or proof.get('provider_mutations')!=0):
        raise ValueError('DIRECT_RECOVERY_PREPYTHON_PROOF_REQUIRED')
    if 'state' in config:
        for key in ('package','package_manifest_sha256','batch_ledger','provider'):
            if config[key]!=old[key]:raise ValueError('DIRECT_RECOVERY_SCOPE_CHANGED:'+key)
        if config['source']==old['source'] or config['state']!='/var/lib/research-system-manual-sprint10/direct-inputs/'+config['source'] or 'prepared_from' in config:
            raise ValueError('DIRECT_RECOVERY_FRESH_STATE_REQUIRED')
    return {'old':old,'binding':binding,'handle':handle,'failure':failure,'reference':ref}


def parent(accounts, config, *, root=Path('/')):
    from orchestrator import modal_mount_recovery as mount
    if mount.selected(config):return mount.parent(accounts,config,root=root)
    result=selection(config,root=root)
    binding=result['binding']
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(PARENT,)).fetchone()
    from orchestrator.modal_direct_continuation import owner
    run=accounts.db.execute('SELECT * FROM autonomy_runs WHERE id=?',(binding['run_id'],)).fetchone()
    if (row is None or row['status']!='UNCERTAIN' or row['binding']!=canonical(binding).decode()
            or row['run']!=binding['run_id'] or json.loads(row['receipt'])!=result['failure']
            or row['reserved_micro_usd']!=binding['envelope']['cost']['reserved_micro_usd']
            or run is None or run['status'] not in ('ACTIVE','COMPLETE')
            or json.loads(run['binding'])!=owner(binding)):
        raise ValueError('DIRECT_RECOVERY_ORIGINAL_LEDGER_CHANGED')
    return result


def preflight(config, *, root=Path('/')):
    # Root reads trusted files; ledger reads/writes remain with the service owner.
    result=selection(config,root=root)
    return {'status':'PASS','parent_binding_sha256':result.get('parent_id',PARENT),'run_id':result['binding']['run_id'],
            'fresh_state':config['state'],'no_reservation_or_launch':True}


def live_empty(provider, result):
    if 'ancestor' in result:live_empty(provider,result['ancestor'])
    expected_exit=result.get('terminal_exit',2)
    h=result['handle'];sb=provider._sandbox(h['provider_id'])
    if sb.poll()!=expected_exit:raise ValueError('DIRECT_RECOVERY_PROVIDER_NOT_TERMINAL')
    # Live stdio is served by the container's command router and can disappear
    # after termination. Query archived entrypoint logs with the same pinned SDK.
    # This recovery is scoped to PARENT's exact 2026-10-06 incident, not a generic
    # retry path. Keep the preserved proof and require the full fresh streams to
    # match it exactly; unavailable, incomplete or changed evidence still refuses.
    since = datetime(2026, 10, 6, tzinfo=timezone.utc)
    until = datetime.now(timezone.utc)
    streams = {'stdout': [], 'stderr': []}
    total = 0
    for entry in sb.logs.fetch(since=since, until=until):
        if (entry.object_id != h['provider_id'] or entry.source not in {'stdout', 'stderr', 'system'}
                or not isinstance(entry.timestamp, datetime) or entry.timestamp.tzinfo is None
                or not since <= entry.timestamp <= until or not isinstance(entry.message, str)):
            raise ValueError('DIRECT_RECOVERY_LOG_BINDING')
        total += len(entry.message.encode('utf-8'))
        if total > 1024 * 1024: raise ValueError('DIRECT_RECOVERY_LOG_SIZE')
        if entry.source in streams: streams[entry.source].append(entry.message)
    if (digest(''.join(streams['stdout']).encode())!=result.get('stdout_sha256',digest(b''))
            or digest(''.join(streams['stderr']).encode())!=result.get('stderr_sha256',digest(ERROR.encode()))):
        raise ValueError('DIRECT_RECOVERY_PROVIDER_PROOF_CHANGED')
    if list(provider._volume(h['data_volume_id']).listdir('/',recursive=True)):
        raise ValueError('DIRECT_RECOVERY_ORIGINAL_VOLUME_NOT_EMPTY')
    if sb.poll()!=expected_exit:raise ValueError('DIRECT_RECOVERY_PROVIDER_NOT_TERMINAL')
    return True


def check_child(binding, result):
    if 'ancestor' in result:
        from orchestrator.modal_mount_recovery import check_child as check_mount
        return check_mount(binding,result)
    old=result['binding']
    if binding.get('recovery')!=result['reference']:
        raise ValueError('DIRECT_RECOVERY_CHILD_BINDING')
    for key in ('purpose','authority_sha256','download_authority_sha256','team_authority_sha256',
                'run_id','download_bytes','package_manifest_sha256','asset_expires_utc'):
        if binding.get(key)!=old[key]:raise ValueError('DIRECT_RECOVERY_CHILD_SCOPE:'+key)
    if binding.get('source')==old['source']:raise ValueError('DIRECT_RECOVERY_NEW_REVIEWED_SOURCE_REQUIRED')


def resolved_failure_ids(accounts, *, root=Path('/')):
    """Only a successfully verified linked child closes its parent's admission.

    The parent's original UNCERTAIN row and full reservation still count. All
    other uncertain assets remain blocking, including a failed recovery.
    """
    closed=set()
    for child in accounts.db.execute("SELECT * FROM autonomy_assets WHERE status='READY'").fetchall():
        binding=json.loads(child['binding'])
        if 'recovery' not in binding:continue
        result=parent(accounts,{'recovery_from':binding['recovery']},root=root)
        check_child(binding,result)
        receipt=json.loads(child['receipt'])
        if (receipt.get('status')!='VERIFIED' or receipt.get('binding_sha256')!=child['id']
                or digest(canonical(binding))!=child['id'] or receipt.get('recovery_of')!=result.get('parent_id',PARENT)):
            raise ValueError('DIRECT_RECOVERY_COMPLETION_BINDING')
        ancestors=result.get('ancestor_ids',{PARENT})
        if ancestors & closed:raise ValueError('DIRECT_RECOVERY_DUPLICATE_CHILD')
        closed.update(ancestors)
    return closed
