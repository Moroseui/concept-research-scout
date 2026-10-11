"""Registered administrative invocation using normal admission and exact historical proofs.

Installed entry, not exceptional admission or a cap override. Executes only in
the registered request service identity and confinement.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

STATE=Path('/var/lib/research-system-autonomy/reviews')
CAP=Path('/opt/research-system/manual-repair-helpers/temporary-daily-cap-20261010')
SENDER=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006/item4-sender-recovery-20261010/packet/source')
SENDER_PACKET='a27b9e0bdf19ec037711ff079725ee83afe02e4d2b95fd751ac1ab9a7e81e04d'
SENDER_SOURCE='41b93574a0ad0fb546745095ff0078debd6f133d'
SENDER_REPORT='a54ef800461b974db328d18fba65e4d6d819044a3a003d9699a59603b0710139'
SENDER_ID='af4547778fe7e1f35698089607ab524d08346618131512c232670b7ccbf02ab8'


def require(ok,why):
    if not ok:raise ValueError('DIRECT_ADMIN_INVOCATION_'+why)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def trusted(path):
    path=Path(path)
    for p in (path,*path.parents):
        st=p.lstat()
        require(not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'TRUSTED_PATH')
    require(path.is_file(),'REGULAR_FILE')
    return path


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,trusted(path))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def exact_verify_adapter(original,qualify,binding,read_file):
    require(binding['call_id']==SENDER_ID,'EXACT_SENDER_ID')
    def verify(row,folder=None):
        if row['id']==SENDER_ID:return qualify(dict(row),binding,read_file)
        return original(row,folder)
    return verify


def authenticate(request):
    require(re.fullmatch('[0-9a-f]{64}',request) is not None,'REQUEST_ID')
    target=Path('/etc/research-system-autonomy/requests')/request
    binding=json.loads(trusted(target/'binding.json').read_bytes())
    registration=json.loads(trusted(target/'registration.json').read_bytes())
    ENGINE=Path(binding['release'])
    require(re.fullmatch('/opt/research-system/autonomy-review/[0-9a-f]{12}',str(ENGINE)) is not None,'INSTALLED_ENGINE_PATH')
    INSTALL=Path('/etc/research-system-autonomy/review')/ENGINE.name/'install-receipt.json'
    INSTALL_SHA=registration['installed_receipt_sha256']
    require(sha(trusted(INSTALL).read_bytes())==INSTALL_SHA,'INSTALLED_ENGINE_RECEIPT')
    installed=json.loads(INSTALL.read_bytes())
    require(installed['release']==str(ENGINE),'ENGINE_PATH')
    for name,pin in installed['files'].items():
        require(sha(trusted(name).read_bytes())==pin,'ENGINE_FILE')
    sys.path.insert(0,str(ENGINE))
    from orchestrator import autonomy_review as ar
    import orchestrator
    require(Path(orchestrator.__file__).resolve().parent==ENGINE/'orchestrator','ENGINE_IMPORT')
    require(Path(__file__).resolve()==ENGINE/'tools/invoke_registered_administrative.py','INSTALLED_OPERATOR_ENTRY')
    require(binding['schema']=='autonomy-review-host/v1' and binding['release']==str(ENGINE)
        and binding['state']==str(STATE) and binding['packets']==str(target/'packets')
        and set(binding['requests'])=={request},'REGISTERED_BINDING')
    require(registration['packet_sha256']==request and registration['installed_receipt_sha256']==INSTALL_SHA
        and registration['binding']==str(target/'binding.json')
        and registration['accounting_state']==str(STATE),'REGISTERED_RECEIPT')
    require(ar.inventory(ENGINE)==binding['release_files'],'FULL_ENGINE_INVENTORY')
    for name,pin in binding['release_files'].items():
        require(sha(trusted(ENGINE/name).read_bytes())==pin,'FULL_ENGINE_SOURCE')
    packet=target/'packets'/request
    manifest=ar.verify_packet(packet)
    require(ar.sha(ar.canonical(manifest))==request and manifest==binding['requests'][request],'REGISTERED_MANIFEST')
    for name in ar.inventory(packet):trusted(packet/name)
    require(os.environ.get('RESEARCH_MANUAL_RUNTIME_CONFIG')==binding['runtime']
        and sha(trusted(binding['runtime']).read_bytes())==binding['runtime_sha256'],'RUNTIME_BINDING')
    approved=ar.verify_result(STATE/SENDER_PACKET)
    require(approved['verdict']=='APPROVE' and not approved.get('findings')
        and approved['source_sha']==SENDER_SOURCE and approved['report_sha256']==SENDER_REPORT
        and approved['change_id']=='item4-sender-recovery-20261010','SENDER_GENUINE_APPROVAL')
    from orchestrator import private_records
    source_manifest=json.loads(private_records.check(STATE/SENDER_PACKET/'packet-manifest.json').read_bytes())
    for name,pin in source_manifest['source_files'].items():
        require(sha(trusted(SENDER/name).read_bytes())==pin,'FULL_APPROVED_SENDER_SOURCE')
    sender=load('_approved_sender_qualifier',SENDER/'tools/review_sender_recovery_once.py')
    exact=json.loads(trusted(SENDER/sender.DOC).read_bytes())
    require(exact['call_id']==SENDER_ID,'EXACT_SENDER_BINDING')
    from orchestrator import administrative_family as af
    af.require_current(manifest)
    return packet,sender,exact


def verify_current_host(request):
    # Called after static authentication, immediately before the normal runner.
    # A currently scientific, stale or unrelated proof is not an admin proof.
    target=Path('/etc/research-system-autonomy/requests')/request
    proof=json.loads(trusted('/run/research-manual-sprint10/host-check.json').read_bytes())
    import time
    require(proof.get('status')=='PASS' and proof.get('review_request')==request
        and proof.get('review_binding_sha256')==sha(trusted(target/'binding.json').read_bytes())
        and proof.get('invocation')==os.environ.get('INVOCATION_ID')
        and bool(proof.get('invocation')) and isinstance(proof.get('time'),(int,float))
        and 0<=time.time()-proof['time']<180,'CURRENT_REGISTERED_HOST_PROOF')


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--request',required=True)
    args=parser.parse_args(argv)
    require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,'SERVICE_OWNER')
    trusted(__file__)
    packet,sender,binding=authenticate(args.request)
    from orchestrator import autonomy_review_runner as runner,administrative_terminal as terminal,private_records as pr
    cap=load('_installed_reviewed_daily_cap',CAP/'tools/temporary_daily_cap.py')
    cap.verified()
    # New installed reserve is family-aware and already uses the same reviewed
    # dated policy. Never overwrite it with the legacy cap's method.
    from orchestrator import autonomy_limits as limits
    policy=cap.module('_verified_existing_daily_policy',CAP/'orchestrator/autonomy_limits.py')
    from datetime import datetime,timezone
    for day in (datetime.now(timezone.utc).date().isoformat(),'2026-10-10','2026-10-11'):
        require(limits.daily_allowance(day)==policy.daily_allowance(day),'UNCHANGED_DAILY_POLICY')
    verify_current_host(args.request)
    original=terminal.verify
    terminal.verify=exact_verify_adapter(original,sender.qualify,binding,lambda p:pr.check(p).read_bytes())
    try:
        result=runner.run(packet,STATE)
        print(json.dumps(result,sort_keys=True))
        return 0 if result['status']=='COMPLETE' else 2
    finally:terminal.verify=original


if __name__=='__main__':
    os.umask(0o077);raise SystemExit(main())
