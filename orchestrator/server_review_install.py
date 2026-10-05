"""Reviewed administrative enabler only; preserve the active scientific release.

Uses the existing terminal importer/change-review predicates, protected archive
reader, native accounting and state inventory. No service, model or admission is
started here. The original approved bootstrap reader qualifies this implementation
before its administrative install; the new server importer cannot approve itself.
"""
import fcntl
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile

from orchestrator import deployment_review as gate, install_reviewed_deployment as native

BASE = Path('/etc/research-system/server-review-deployment')
CONFIG = Path('/etc/research-system/server-reviews.json')
SOURCES = Path('/var/lib/research-system/inspection-enabler-sources')
BOOTSTRAP_SOURCE = '7ccd7c700826b4729ff39b45252c767520739dae'
BOOTSTRAP_ROOT = Path('/opt/research-system/releases')/(BOOTSTRAP_SOURCE+'-research-handover')/'snapshot'
SERVER_BOOTSTRAP_SOURCE = '0ccce0c0dd890e9881b0124bc1b88cb3e3755c0c'
SERVER_BOOTSTRAP_ROOT = SOURCES/SERVER_BOOTSTRAP_SOURCE
SCHEMA = 'server-review-administrative-install/v1'
require = gate.require


def proposal(bundle):
    bundle = Path(bundle); gate.protected(bundle,directory=True)
    raw=gate.read(bundle/'proposal.json');value=json.loads(raw); source=gate.pin(value['source'],40)
    require(bundle == BASE/'bundles'/gate.digest(raw) and set(value)=={'schema','review_profile','source','source_root','source_files','archive_sha256',
            'targets','previous_files','recovery_sha256','changes'} and value['schema']==SCHEMA
        and value['review_profile'] in {'operator-terminal-review/v1','server-terminal-review/v1'}
        and value['source_root']==str(SOURCES/source)
        and set(value['targets'])=={str(CONFIG)}, 'ADMINISTRATIVE_FIXED_SCOPE_REQUIRED')
    target=value['targets'][str(CONFIG)]
    require(target['uid']==target['gid']==0 and target['mode']==0o600,
            'ADMINISTRATIVE_PROTECTED_CONFIGURATION_REQUIRED')
    config_raw=gate.read(bundle/'literals'/target['sha256']);config=json.loads(config_raw)
    require(gate.digest(config_raw)==target['sha256'] and config['source']==source,
            'ADMINISTRATIVE_CONFIGURATION_BINDING_CHANGED')
    # The one previous file is a read-only scientific-release witness. It is
    # preserved, never installed/restored by this administrative operation.
    witness='/etc/research-system/live-research/controller.json'
    require(set(value['previous_files'])=={witness}, 'ADMINISTRATIVE_EXISTING_RELEASE_WITNESS_REQUIRED')
    original=value['previous_files'][witness]
    require(gate.digest(gate.read(bundle/'literals'/original['sha256']))==original['sha256'],
            'ADMINISTRATIVE_RELEASE_WITNESS_ORIGINAL_CHANGED')
    archive=gate.read(bundle/'source.tar.gz',maximum=10000000)
    files=gate.archive_inventory(archive)
    require(gate.digest(archive)==value['archive_sha256'] and
        {n:gate.digest(v) for n,v in files.items()}==value['source_files'], 'ADMINISTRATIVE_ARCHIVE_CHANGED')
    return value,config,config_raw,archive,files


def original_review(bundle,value):
    # Invoke the already installed, independently approved reader with an exact
    # clean environment/cwd. The reviewed candidate is evidence, not this reader.
    profile=value['review_profile']
    require(profile in {'operator-terminal-review/v1','server-terminal-review/v1'},
            'ADMINISTRATIVE_REVIEW_PROFILE_REQUIRED')
    # The independently installed032 reader already validates genuine server
    # launch provenance and prepaid accounting. Never run the candidate reader
    # to establish its own independent approval. Keep the manual bootstrap.
    root,source=(SERVER_BOOTSTRAP_ROOT,SERVER_BOOTSTRAP_SOURCE) if profile=='server-terminal-review/v1' else (BOOTSTRAP_ROOT,BOOTSTRAP_SOURCE)
    gate.protected(root,directory=True)
    from orchestrator.remote_supervisor import checked_source
    checked_source(root,source)
    script=("import json,sys;from pathlib import Path;"
        "from orchestrator import terminal_review as t,deployment_review as g;"
        "b=Path(sys.argv[1]);p=g.read(b/'proposal.json');"
        "r,_=t.load(b,p,g.archive_inventory(g.read(b/'source.tar.gz',maximum=10000000)));"
        "selected=g.selected_review_applications(r,p,json.loads(p)['source']);"
        "heads={x['request']:g.change_review(b,x,r,selected=selected) for x in json.loads(p)['changes']};"
        "print(json.dumps({'execution':r['execution'],'session':r['response']['session_id'],"
        "'model':r['terminal_session']['provider_model'],'change_heads':heads}))")
    proc=subprocess.run(['/usr/bin/python3','-B','-c',script,str(bundle)],cwd=root,
        env={'PATH':'/usr/bin:/bin','PYTHONPATH':str(root),'PYTHONDONTWRITEBYTECODE':'1'},
        capture_output=True,check=True,timeout=60)
    require(len(proc.stdout)<=100000,'ADMINISTRATIVE_ORIGINAL_REVIEW_BOUND')
    return json.loads(proc.stdout)



def host_read_authority(bundle,config):
    """Use the already authenticated original review inventory, not loose files."""
    if 'host_read' not in config.get('runtime', {}):
        return None
    from orchestrator import implementation_host_read as host
    host.profile(config['runtime']['host_read'])
    _, raw = gate._inspection_inventory(Path(bundle)/'terminal-review')
    return host.authority(raw)


def verify(root,source,config):
    require(os.getuid()==0 and Path(root)==SOURCES/gate.pin(source,40), 'ADMINISTRATIVE_FIXED_EXECUTING_SOURCE')
    pointer=json.loads(gate.read(BASE/'active.json'))
    require(set(pointer)=={'source','proposal_sha256','receipt_sha256'} and pointer['source']==source,
            'ADMINISTRATIVE_INSTALLED_SELECTION_REQUIRED')
    bundle=BASE/'bundles'/gate.pin(pointer['proposal_sha256']);value,actual,raw,_,files=proposal(bundle)
    require(actual==config and gate.read(CONFIG)==raw,'ADMINISTRATIVE_CALLER_CONFIGURATION_CHANGED')
    receipt_raw=gate.read(bundle/'install-receipt.json');receipt=json.loads(receipt_raw)
    intent_raw=gate.read(bundle/'install-intent.json');intent=json.loads(intent_raw)
    require(gate.digest(receipt_raw)==pointer['receipt_sha256']
        and receipt['status']=='INSTALLED_REVIEW_VERIFIED' and receipt['source']==source
        and receipt['proposal_sha256']==pointer['proposal_sha256']
        and receipt['configuration_sha256']==gate.digest(raw)
        and receipt['source_files']==value['source_files']
        and receipt['original_review']==original_review(bundle,value)
        and receipt['accounting_sha256']==gate.digest(gate.read(bundle/'terminal-accounting.json',maximum=4000000))
        and receipt['intent_sha256']==gate.digest(intent_raw)
        and intent['source']==source and intent['proposal_sha256']==pointer['proposal_sha256']
        and intent['original_review']==receipt['original_review']
        and intent['accounting']==receipt['accounting_validation']
        and receipt['state_before']==receipt['state_after']==intent['state_before']
        and receipt['research_activation']==receipt['models_started']==False,
        'ADMINISTRATIVE_COMPLETED_INDEPENDENT_INSTALL_REQUIRED')
    host_read_authority(bundle,config)
    native.source_inventory(root,value['source_files'],source)
    return {**receipt,'receipt_sha256':gate.digest(receipt_raw),'receipt_path':str(bundle/'install-receipt.json')}


def install(bundle):
    require(os.getuid()==0,'ADMINISTRATIVE_ROOT_INSTALL_REQUIRED')
    bundle=Path(bundle);value,config,config_raw,archive,files=proposal(bundle)
    source=value['source'];root=SOURCES/source
    gate.protected(BASE,directory=True);gate.protected(SOURCES,directory=True)
    with (BASE/'install.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if (bundle/'install-receipt.json').exists():return verify(root,source,config)
        require(not (bundle/'install-intent.json').exists(),'ADMINISTRATIVE_PARTIAL_INSTALL_RECONCILE')
        require(not root.exists() and not CONFIG.exists() and not (BASE/'active.json').exists(),
                'ADMINISTRATIVE_INITIAL_INSTALL_ONLY_PRESERVE_PREVIOUS')
        review=original_review(bundle,value)
        # Existing canonical accounting validates the actual manual review once;
        # installation itself makes no admission or Git mutation.
        from orchestrator import terminal_review
        checked,metadata=terminal_review.load(bundle,gate.read(bundle/'proposal.json'),files)
        require(checked['execution']==review['execution'],'ADMINISTRATIVE_BOOTSTRAP_READER_DISAGREEMENT')
        broker=json.loads(gate.read(native.CONFIG/'broker.json'))
        accounting=native.require_terminal_accounting(bundle,{**metadata,
            'terminal_profile':checked['terminal_profile'],'proposal_sha256':gate.digest(gate.read(bundle/'proposal.json')),
            'archive_sha256':value['archive_sha256']})
        host_read_authority(bundle,config)
        native.source_inventory(Path(__file__).resolve().parents[1],value['source_files'],source)
        witness='/etc/research-system/live-research/controller.json'
        item=value['previous_files'][witness]
        require(gate.digest(gate.read(witness))==item['sha256']
            and gate.access(Path(witness))==(item['uid'],item['gid'],item['mode']),
                'ADMINISTRATIVE_SCIENTIFIC_RELEASE_CHANGED')
        from orchestrator import inspection_runner
        control=inspection_runner.current_control(json.loads(gate.read(witness)))
        require(control==config['permit']['control_snapshot'],'ADMINISTRATIVE_NEW_STOP_OR_STALE_PERMIT')
        state=native.state_fingerprint(broker)
        active_original=gate.read(gate.ACTIVE)
        before={'scientific_state':state,'scientific_active_sha256':gate.digest(active_original),
                'control':control}
        intent={'source':source,'proposal_sha256':gate.digest(gate.read(bundle/'proposal.json')),
                'original_review':review,'accounting':accounting,'state_before':before,
                'automatic_retry':False,'operations':['install immutable administrative source','create one private config']}
        gate._save_once(bundle,'install-intent.json',intent)
        root.mkdir(mode=0o755)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            # Native archive_inventory above has already refused unsafe members.
            # Extract into a new private staging directory; move only its snapshot.
            staging=bundle/'source-extraction';staging.mkdir(mode=0o700)
            tar.extractall(staging,filter='data')
        for child in (staging/'snapshot').iterdir():child.rename(root/child.name)
        for path in [root,*root.rglob('*')]:
            require(not path.is_symlink(),'ADMINISTRATIVE_SOURCE_SYMLINK_REFUSED')
            os.chown(path,0,0);os.chmod(path,0o755 if path.is_dir() else 0o644)
        native.source_inventory(root,value['source_files'],source)
        native.atomic(CONFIG,config_raw,value['targets'][str(CONFIG)])
        after={'scientific_state':native.state_fingerprint(broker),
               'scientific_active_sha256':gate.digest(gate.read(gate.ACTIVE)),
               'control':inspection_runner.current_control(json.loads(gate.read(witness)))}
        require(after==before,'ADMINISTRATIVE_SCIENTIFIC_STATE_CHANGED_RECONCILE')
        receipt={'status':'INSTALLED_REVIEW_VERIFIED','source':source,
            'intent_sha256':gate.digest(gate.read(bundle/'install-intent.json')),
            'proposal_sha256':intent['proposal_sha256'],'configuration_sha256':gate.digest(config_raw),
            'source_files':value['source_files'],'original_review':review,
            'accounting_sha256':gate.digest(gate.read(bundle/'terminal-accounting.json',maximum=4000000)),
            'accounting_validation':accounting,'state_before':before,'state_after':after,
            'research_activation':False,'models_started':False,
            'recovery':'No research release changed. Preserve all originals; disabling/removing only this administrative config prevents future administrative starts. Reconcile partial installs before any further install.'}
        saved=gate._save_once(bundle,'install-receipt.json',receipt)
        native.atomic(BASE/'active.json',gate.encoded({'source':source,'proposal_sha256':intent['proposal_sha256'],
            'receipt_sha256':gate.digest(gate.read(bundle/'install-receipt.json'))}),{'uid':0,'gid':0,'mode':0o600})
        return verify(root,source,config)
