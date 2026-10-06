"""Continue one held, unreserved input preparation without rewriting its owner.

Root binds the predecessor config and unchanged binding. Only new executable,
config and unit files are installed. This is not retry authority after a provider
intent or reservation, and it creates no new scientific/spending allowance.
"""
from pathlib import Path
from contextlib import closing
import json
import os
import re
import sqlite3
import subprocess
import sys
from orchestrator import private_records
from orchestrator.manual_executor import digest, read
from orchestrator.modal_executor import canonical
from orchestrator import modal_direct_budget as budget


def mapped(root, value):
    from tools.direct_storage_service import safe
    safe(value)
    path=Path(root)/value.lstrip('/')
    if any(p.is_symlink() for p in [path,*path.parents]):raise ValueError('DIRECT_CONTINUATION_ALIAS')
    return path


def owner(binding):
    return {'purpose':budget.PURPOSE,'authority_sha256':budget.AUTHORITY,
            'source':binding['source'],'binding_sha256':digest(canonical(binding)),
            'no_scientific_allowance':True}


def held(units):
    for name in units:
        observed=subprocess.check_output(['/usr/bin/systemctl','show',name,
            '--property=LoadState,ActiveState,UnitFileState,MainPID'],text=True)
        v=dict(line.split('=',1) for line in observed.splitlines() if '=' in line)
        if (v.get('LoadState')!='loaded' or v.get('ActiveState') not in ('inactive','failed') or
                v.get('UnitFileState') not in ('disabled','masked') or v.get('MainPID','0')!='0'):
            raise ValueError('DIRECT_CONTINUATION_PREDECESSOR_NOT_HELD')


def predecessor(config, *, root=Path('/')):
    """Hash-checked original provenance, also checked on every live tick."""
    root=Path(root);ref=config['prepared_from']
    if not isinstance(ref,dict) or set(ref)!={'config','config_sha256','binding_sha256'}:
        raise ValueError('DIRECT_CONTINUATION_REFERENCE')
    if any(not isinstance(ref[k],str) or not re.fullmatch('[0-9a-f]{64}',ref[k])
           for k in ('config_sha256','binding_sha256')):raise ValueError('DIRECT_CONTINUATION_HASH')
    path=mapped(root,ref['config'])
    if root==Path('/'):
        from orchestrator.manual_host_guard import trusted
        trusted(path)
    private_records.check(path)
    if digest(path.read_bytes())!=ref['config_sha256']:raise ValueError('DIRECT_CONTINUATION_CONFIG_CHANGED')
    old=read(path)
    fields={'schema','source','release','installation_record','installation_sha256','package',
            'package_manifest_sha256','batch_ledger','state','provider','units'}
    if set(old)!=fields or old['schema']!='direct-development-storage/v1':raise ValueError('DIRECT_CONTINUATION_PREDECESSOR_SCHEMA')
    if (old['source']==config['source'] or
        ref['config']!='/etc/research-system-manual-sprint10/direct-inputs/'+old['source']+'/config.json' or
        old['state']!='/var/lib/research-system-manual-sprint10/direct-inputs/'+old['source']):
        raise ValueError('DIRECT_CONTINUATION_PREDECESSOR_PATH')
    for key in ('schema','package','package_manifest_sha256','batch_ledger','state','provider'):
        if old[key]!=config[key]:raise ValueError('DIRECT_CONTINUATION_SCOPE_CHANGED:'+key)
    from tools.manual_promotion import manifest_check
    installed=mapped(root,old['installation_record'])/'installed.json'
    if root==Path('/'):trusted(installed)
    if digest(installed.read_bytes())!=old['installation_sha256']:raise ValueError('DIRECT_CONTINUATION_INSTALL_CHANGED')
    receipt=manifest_check(root,old['installation_record'])
    if receipt['source']!=old['source'] or receipt['layout']['release']!=old['release']:
        raise ValueError('DIRECT_CONTINUATION_RELEASE_BINDING')
    expected={'research-manual-sprint10-direct-inputs-'+old['source'][:12]+suffix for suffix in ('.service','.timer')}
    if set(old['units'])!=expected:raise ValueError('DIRECT_CONTINUATION_UNIT_SET')
    for name,row in old['units'].items():
        unit=mapped(root,'/etc/systemd/system/'+name)
        if root==Path('/'):trusted(unit)
        private_records.check(unit)
        if set(row)!={'sha256'} or digest(unit.read_bytes())!=row['sha256']:raise ValueError('DIRECT_CONTINUATION_UNIT_CHANGED')
    if root==Path('/'):held(old['units'])
    return old


def check_binding(config, old, binding, raw):
    ref=config['prepared_from']
    if (digest(raw)!=ref['binding_sha256'] or digest(canonical(binding))!=ref['binding_sha256'] or
        binding.get('source')!=old['source'] or binding.get('installed_config_sha256')!=ref['config_sha256'] or
        binding.get('package_manifest_sha256')!=old['package_manifest_sha256']):
        raise ValueError('DIRECT_CONTINUATION_BINDING_CHANGED')


def unreserved(config, old, *, root=Path('/')):
    """Read-only URI and original account: never root-open a live service DB."""
    root=Path(root)
    if root==Path('/') and os.getuid()!=1003:raise ValueError('DIRECT_CONTINUATION_LEDGER_OWNER_REQUIRED')
    state=mapped(root,config['state']);private_records.check_tree(state)
    if root==Path('/') and any(p.stat().st_uid!=1003 for p in [state,*state.iterdir()]):
        raise ValueError('DIRECT_CONTINUATION_STATE_OWNER')
    if set(p.name for p in state.iterdir())!={'binding.json','initial-billing.json','connectivity.json','tick.lock'}:
        raise ValueError('DIRECT_CONTINUATION_NOT_PRE_RESERVATION')
    path=state/'binding.json';raw=path.read_bytes();binding=json.loads(raw)
    check_binding(config,old,binding,raw)
    ledger=mapped(root,config['batch_ledger']);dbpath=ledger/'jobs.sqlite'
    for suffix in ('','-wal','-shm'):
        p=Path(str(dbpath)+suffix)
        if p.exists():
            private_records.check(p)
            if root==Path('/') and p.stat().st_uid!=1003:raise ValueError('DIRECT_CONTINUATION_LEDGER_OWNER')
    with closing(sqlite3.connect(dbpath.as_uri()+'?mode=ro',uri=True)) as db:
        db.execute('PRAGMA query_only=ON')
        row=db.execute('SELECT binding,status FROM autonomy_runs WHERE id=?',(binding['run_id'],)).fetchone()
        if row is None or json.loads(row[0])!=owner(binding) or row[1]!='ACTIVE':
            raise ValueError('DIRECT_CONTINUATION_OWNER_CHANGED')
        if db.execute('SELECT 1 FROM autonomy_assets WHERE run=?',(binding['run_id'],)).fetchone() or db.execute(
                'SELECT 1 FROM autonomy_compute WHERE run=?',(binding['run_id'],)).fetchone():
            raise ValueError('DIRECT_CONTINUATION_ALREADY_RESERVED')
    return {'status':'PASS','run_id':binding['run_id'],'binding_sha256':digest(raw),
            'asset_expires_utc':binding['asset_expires_utc'],'ledger_mode':'ro','writes':0}


def preflight(config, *, root=Path('/')):
    old=predecessor(config,root=root)
    if Path(root)!=Path('/'):return unreserved(config,old,root=root)
    # Root never opens the database or its sidecars. No credential access, no
    # provider operation, and no writable/prep checkout on this import path.
    script=('import sys,json; sys.path.insert(0,sys.argv[1]); '
            'from orchestrator.modal_direct_continuation import predecessor,unreserved; '
            'c=json.load(sys.stdin); print(json.dumps(unreserved(c,predecessor(c))))')
    result=subprocess.run([sys.executable,'-I','-B','-c',script,config['release']],
        input=json.dumps(config),text=True,capture_output=True,check=True,
        user=1003,group=1003,extra_groups=[],cwd='/',timeout=60)
    return json.loads(result.stdout)
