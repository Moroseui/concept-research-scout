"""Prepare supplemental selected preflight aliases; never replace the live registry.

Reuses the current credential and private output folder. No token replacement,
folder creation, download or service restart. Exact installation is a separate
setup transaction after inspection. Original selected records remain private.
"""
import argparse
import json
import os
from pathlib import Path
from orchestrator.drive_evidence import GoogleDrive,private_write,digest
from orchestrator.phone_notifications import protected_read

EXPECTED={'binding.json':('p001-preflight-binding',65536),
          'process.json':('p001-preflight-process',65536),
          'launch.console.log':('p001-preflight-launch-console',1048576),
          'setup.console.log':('p001-preflight-setup-console',1048576)}


def plan(config,selected,client):
    if (config.get('version')!=1 or config.get('mode')!='REGISTERED_EVIDENCE_ONLY'
            or not isinstance(selected,list) or not 1<=len(selected)<=4
            or any(not isinstance(i,str) for i in selected) or len(set(selected))!=len(selected)):
        raise ValueError('BOUNDED_EXISTING_REGISTRY_AND_SELECTION_REQUIRED')
    metadata=[];added={};ids={e['id'] for e in config['files'].values()}
    for file_id in selected:
        value=client.metadata(file_id);metadata.append(value)
        if value.get('id')!=file_id or value.get('name') not in EXPECTED or value.get('trashed'):
            raise ValueError('EXACT_SELECTED_PREFLIGHT_PROVENANCE_REQUIRED')
        alias,maximum=EXPECTED[value['name']]
        if alias in config['files'] or alias in added or file_id in ids:
            raise ValueError('EXISTING_OR_AMBIGUOUS_ALIAS_RECONCILE')
        if (not 0<int(value.get('size',0))<=maximum
                or value.get('mimeType','').startswith('application/vnd.google-apps.')):
            raise ValueError('SMALL_ORIGINAL_BINARY_REQUIRED')
        added[alias]={'id':file_id,'expected_name':value['name'],'access':'small-evidence-read','max_bytes':maximum}
    return {**config,'files':{**config['files'],**added}},metadata,sorted(added)


def prepare(config_path,credentials,picked,destination):
    if os.getuid()!=0:raise ValueError('SETUP_ADMIN_REQUIRED')
    os.umask(0o077);destination=Path(destination)
    if (destination.exists() or any(p.is_symlink() for p in [destination,*destination.parents])
            or destination.parent.stat().st_mode&0o077):raise ValueError('FRESH_PRIVATE_SETUP_REQUIRED')
    original=protected_read(config_path);selection=protected_read(picked)
    candidate,metadata,aliases=plan(json.loads(original),json.loads(selection)['file_ids'],GoogleDrive(credentials))
    if protected_read(config_path)!=original:raise ValueError('LIVE_REGISTRY_CHANGED')
    destination.mkdir(mode=0o700)
    private_write(destination/'original-config.json',json.loads(original))
    with (destination/'original-config.bytes').open('xb') as out:out.write(original)
    private_write(destination/'selected-metadata.json',metadata)
    private_write(destination/'config.proposed.json',candidate)
    receipt={'status':'PROVENANCE_ALIASES_PREPARED_NOT_INSTALLED','added_aliases':aliases,
             'original_config_sha256':digest(original),'picked_selection_sha256':digest(selection),
             'proposed_config_sha256':digest((destination/'config.proposed.json').read_bytes()),
             'existing_aliases_unchanged':True,'existing_output_folder_reused':True,
             'credentials_changed':False,'files_downloaded':0,'remote_objects_created':0}
    private_write(destination/'receipt.json',receipt);return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['config-path','credentials','picked','destination']:p.add_argument('--'+name,required=True)
    print(json.dumps(prepare(**vars(p.parse_args()))))
