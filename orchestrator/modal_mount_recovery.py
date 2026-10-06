"""One exact empty-Volume mount failure; no general retry or ledger rewrite.

The predecessor chain is authenticated in full. Both reservations count in the
same item4 caps. Only executable package bytes change; cohort/plans stay exact.
"""
from pathlib import Path
from orchestrator import private_records as pr
from orchestrator.manual_executor import read,digest
from orchestrator.modal_executor import canonical
from orchestrator.modal_direct_continuation import mapped,held

PARENT='fab901a10c27a1e1325b766765d6dd84fb97e6f8471a40d15e6ddbc0eca58b1c'
SOURCE='2d0de4e1a6cfef8d3d657ef6df24796a7a052d7e'
STDERR_SHA256='cdf3afcf2d24719ef3eed89ad7e2c54ac9086d4faf62778748ab98dd88f45af3'


def selected(config):
    return isinstance(config.get('recovery_from'),dict) and config['recovery_from'].get('binding_sha256')==PARENT


def selection(config,*,root=Path('/'),require_held=True):
    from orchestrator import modal_direct_recovery as original
    from orchestrator import modal_download_package as package
    from tools.manual_promotion import manifest_check
    ref=config['recovery_from']
    if set(ref)!={'config','terminal_proof','binding_sha256','replacement_package'}:
        raise ValueError('MOUNT_RECOVERY_SELECTION')
    old=original.bound(ref['config'],root=root)
    expected={'schema','source','release','installation_record','installation_sha256','package',
              'package_manifest_sha256','batch_ledger','state','provider','units','recovery_from'}
    if (set(old)!=expected or old['source']!=SOURCE or old['schema']!='direct-development-storage/v1'
            or old['recovery_from'].get('binding_sha256')!=original.PARENT):
        raise ValueError('MOUNT_RECOVERY_PREDECESSOR')
    first=original.selection(old,root=root,require_held=require_held)
    install=mapped(root,old['installation_record'])/'installed.json'
    if digest(pr.check(install).read_bytes())!=old['installation_sha256']:
        raise ValueError('MOUNT_RECOVERY_INSTALL_CHANGED')
    installed=manifest_check(root,old['installation_record'])
    if installed['source']!=SOURCE or installed['layout']['release']!=old['release']:
        raise ValueError('MOUNT_RECOVERY_RELEASE_CHANGED')
    if (ref['config']['path']!='/etc/research-system-manual-sprint10/direct-inputs/'+SOURCE+'/config.json'
            or old['state']!='/var/lib/research-system-manual-sprint10/direct-inputs/'+SOURCE):
        raise ValueError('MOUNT_RECOVERY_PREDECESSOR_PATH')
    if set(old['units'])!={'research-manual-sprint10-direct-inputs-'+SOURCE[:12]+s for s in ('.service','.timer')}:
        raise ValueError('MOUNT_RECOVERY_UNIT_SET')
    for name,row in old['units'].items():
        path=mapped(root,'/etc/systemd/system/'+name)
        if Path(root)==Path('/'):
            from orchestrator.manual_host_guard import trusted
            trusted(path)
        if set(row)!={'sha256'} or digest(pr.check(path).read_bytes())!=row['sha256']:
            raise ValueError('MOUNT_RECOVERY_UNIT_CHANGED')
    if Path(root)==Path('/') and require_held:held(old['units'])
    state=mapped(root,old['state']);pr.check_tree(state)
    binding=read(state/'binding.json');handle=read(state/'provider/sandbox.json');failure=read(state/'FAILED.json')
    original.check_child(binding,first)
    if (digest(canonical(binding))!=PARENT or binding['source']!=SOURCE
            or binding['installed_config_sha256']!=ref['config']['sha256']
            or handle.get('binding_sha256')!=PARENT or failure!={'status':'FAILED','exit_code':1,
                'provider_id':handle['provider_id'],'no_automatic_retry':True}):
        raise ValueError('MOUNT_RECOVERY_BINDING')
    proof=original.bound(ref['terminal_proof'],root=root)
    if (proof!={'provider_id':handle['provider_id'],'exit_code':1,'stdout_sha256':digest(b''),
            'stderr_sha256':STDERR_SHA256,'data_volume_id':handle['data_volume_id'],
            'data_volume_file_count':0,'data_volume_bytes':0,'provider_mutations':0}):
        raise ValueError('MOUNT_RECOVERY_EMPTY_PROOF')
    replacement=ref['replacement_package']
    if not isinstance(replacement,dict) or set(replacement)!={'path','sha256'}:
        raise ValueError('MOUNT_RECOVERY_PACKAGE_REFERENCE')
    newpath=mapped(root,replacement['path']);oldpath=mapped(root,old['package'])
    if newpath==oldpath:raise ValueError('MOUNT_RECOVERY_FRESH_PACKAGE_REQUIRED')
    if Path(root)==Path('/'):
        from orchestrator.manual_host_guard import trusted
        for path in (newpath,oldpath):trusted(path)
    new=package.verify(newpath,replacement['sha256'])
    raw=pr.check(oldpath/'manifest.json').read_bytes()
    if digest(raw)!=old['package_manifest_sha256']:raise ValueError('MOUNT_RECOVERY_OLD_PACKAGE_CHANGED')
    previous=read(oldpath/'manifest.json');inventory=package.inventory(oldpath);inventory.pop('manifest.json')
    if inventory!=previous['files']:raise ValueError('MOUNT_RECOVERY_OLD_PACKAGE_CHANGED')
    for key in ('schema','attempt','plans','authority_sha256','patient_computation'):
        if new[key]!=previous[key]:raise ValueError('MOUNT_RECOVERY_PACKAGE_SCOPE:'+key)
    if (newpath/'cohort.json').read_bytes()!=(oldpath/'cohort.json').read_bytes():
        raise ValueError('MOUNT_RECOVERY_COHORT_CHANGED')
    # Every plan's hash is checked by verify; equality above fixes all members,
    # source URLs, byte counts, content hashes and the locked-patient exclusion.
    if 'state' in config:
        for key in ('batch_ledger','provider'):
            if config[key]!=old[key]:raise ValueError('MOUNT_RECOVERY_SCOPE:'+key)
        if (config['package']!=replacement['path'] or config['package_manifest_sha256']!=replacement['sha256']
                or config['source']==SOURCE or config['state']!='/var/lib/research-system-manual-sprint10/direct-inputs/'+config['source']
                or 'prepared_from' in config):raise ValueError('MOUNT_RECOVERY_FRESH_STATE_REQUIRED')
    return {'old':old,'binding':binding,'handle':handle,'failure':failure,'reference':ref,
            'ancestor':first,'ancestor_ids':{original.PARENT,PARENT},'parent_id':PARENT,
            'replacement_package_sha256':replacement['sha256'],'terminal_exit':1,
            'stdout_sha256':digest(b''),'stderr_sha256':STDERR_SHA256}


def parent(accounts,config,*,root=Path('/')):
    from orchestrator import modal_direct_recovery as original
    result=selection(config,root=root)
    original.parent(accounts,result['old'],root=root)
    binding=result['binding']
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(PARENT,)).fetchone()
    import json
    if (row is None or row['status']!='UNCERTAIN' or row['run']!=binding['run_id']
            or row['binding']!=canonical(binding).decode() or json.loads(row['receipt'])!=result['failure']
            or row['reserved_micro_usd']!=binding['envelope']['cost']['reserved_micro_usd']):
        raise ValueError('MOUNT_RECOVERY_LEDGER_CHANGED')
    return result


def check_child(binding,result):
    old=result['binding']
    if binding.get('recovery')!=result['reference']:raise ValueError('DIRECT_RECOVERY_CHILD_BINDING')
    for key in ('purpose','authority_sha256','download_authority_sha256','team_authority_sha256',
                'run_id','download_bytes','asset_expires_utc'):
        if binding.get(key)!=old[key]:raise ValueError('DIRECT_RECOVERY_CHILD_SCOPE:'+key)
    if binding.get('package_manifest_sha256')!=result['replacement_package_sha256']:
        raise ValueError('MOUNT_RECOVERY_CHILD_PACKAGE')
    if binding.get('source') in {old['source'],result['ancestor']['binding']['source']}:
        raise ValueError('DIRECT_RECOVERY_NEW_REVIEWED_SOURCE_REQUIRED')
