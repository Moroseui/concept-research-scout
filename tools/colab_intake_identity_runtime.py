"""Fixed Colab-only intake repair; reuse existing installation and host controls."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

CHANGE = 'review-continuation-20261011'
# One bounded administrative recovery review; original failed request is retained.
REVIEW_CHANGE = 'native-authority-reader-recovery-20261011'
REVIEW_SCOPE = 'docs/NATIVE_REVIEW_COLAB_TURN_SCOPE.md'
READER_PREVIOUS = Path('/opt/research-system/manual-repair-helpers/colab-network-continuation-20261011')
NETWORK_PREVIOUS = Path('/opt/research-system/manual-repair-helpers/colab-intake-source-alignment-20261011')
NETWORK_DOC = 'docs/COLAB_NETWORK_PREMODEL_PRIVATE.json'
NETWORK_SHA = 'f074b5f21453c90c3dc3707f3ac5a6a4d4b0ca72b1d40b8f477bbc60c35075fd'
PREVIOUS_ROOT = Path('/opt/research-system/manual-repair-helpers/colab-intake-identity-20261011')
PREVIOUS_SOURCE = '9f28966e8228be06d76a99959d60a9aecf06f30b'
PREVIOUS_REVIEW = 'ffce32d7f49dbe333d87dcf41daba11d08d20f208aee8207c12d804400238987'
ROOT = Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD = Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
ORIGINAL = Path('/opt/research-system/manual-repair-helpers/preparation-and-cap-repair-20261010')
BRANCH = Path('/opt/research-system/manual-repair-helpers/preparation-branch-admission-repair-20261010')
BRANCH_RECORD = Path('/var/lib/research-system-manual-sprint10-deployment/preparation-branch-admission-repair-20261010')
RUNTIME = Path('/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json')
ENTRY = 'tools/colab_intake_identity_runtime.py'
RECOVERY = 'tools/colab_intake_identity_recovery.py'
UNIT = 'research-'+CHANGE+'.service'
NATIVE_UNIT = 'research-'+CHANGE+'-native-review.service'
NATIVE_PREVIOUS = Path('/opt/research-system/manual-repair-helpers/timing-author24-history-repair-20261011')
OLD_UNIT = 'research-preparation-branch-admission-repair-20261010-colab_preparation.service'
REQUIRED = [ENTRY, RECOVERY, REVIEW_SCOPE, NETWORK_DOC, 'tools/item4_diagnostic_review_runtime.py',
            'tools/item4_response_host_operation.py','docs/ITEM4_RESPONSE_HOST_PRIVATE.json',
            'docs/COLAB_TURN_RECOVERY_PRIVATE.json','docs/NATIVE_REVIEW_ACTIVATION_PRIVATE.json',
            'orchestrator/item4_smoke_response.py', 'orchestrator/colab_reader_recovery.py',
            'orchestrator/manual_context.py', 'orchestrator/preparation_interleaving.py', 'docs/COLAB_READER_RECOVERY_PRIVATE.json', 'docs/COLAB_TIMING_TRANSPORT_REPAIR_SCOPE.md', 'tools/reviewer_connection_timing.py', 'docs/COLAB_INTAKE_PREMODEL_PRIVATE.json',
            'orchestrator/scientific_intake.py', 'orchestrator/scientific_search.py']


def require(ok, why):
    if not ok: raise ValueError('COLAB_INTAKE_RUNTIME_'+why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def trusted(path):
    p=Path(path)
    for q in [p,*p.parents]:
        st=q.lstat();require(not q.is_symlink() and st.st_uid==0 and not st.st_mode&0o022, 'TRUSTED_PATH')
    return p


def load(name, path):
    spec=importlib.util.spec_from_file_location(name,trusted(path));m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m


def reviewed(review):
    from orchestrator.autonomy_review import verify_result
    approval=verify_result(trusted(review))
    require(approval['verdict']=='APPROVE' and not approval.get('findings')
            and approval['change_id']==REVIEW_CHANGE
            and approval['runtime_sha256']==sha(trusted(RUNTIME).read_bytes()), 'GENUINE_APPROVAL')
    manifest=json.loads(trusted(Path(review)/'packet-manifest.json').read_bytes())
    require(all(n in manifest['source_files'] for n in REQUIRED), 'WHOLE_REPAIR_COMPONENT')
    return approval,manifest


def authority(held=True):
    require(Path(__file__).resolve()==ROOT/ENTRY, 'EXECUTED_PATH')
    approval,manifest=reviewed(RECORD/'review')
    installed=json.loads(trusted(RECORD/'installed.json').read_bytes())
    require(installed['root']==str(ROOT) and installed['source']==approval['source_sha']
            and installed['review_sha256']==approval['report_sha256']
            and installed['files']==manifest['source_files'] and installed['status']=='INSTALLED_HELD', 'INSTALL_BINDING')
    for name,pin in installed['files'].items():
        require(sha(trusted(ROOT/name).read_bytes())==pin, 'REVIEWED_SOURCE_CHANGED')
    require(set(installed['units'])=={'/etc/systemd/system/'+UNIT,'/etc/systemd/system/'+NATIVE_UNIT}, 'UNIT_SET')
    for name,pin in installed['units'].items():require(sha(trusted(name).read_bytes())==pin,'UNIT_CHANGED')
    if held:
        require(json.loads(trusted(RECORD/'COMPLETE.json').read_bytes())==
                {'status':'INSTALLED_HELD','source':approval['source_sha'],'scientific_calls':0,'provider_calls':0}, 'INSTALL_VERIFICATION')
    return approval


def original():
    import orchestrator
    require(Path(orchestrator.__file__).resolve().parent==ORIGINAL/'orchestrator','ORIGINAL_IMPORT_ROOT')
    m=load('_colab_intake_original_branch',BRANCH/'tools/preparation_branch_repair_runtime.py')
    m.authority();return m


def recovery():
    # The prior recovery is complete. Authenticate and reuse its exact verifier;
    # never replay it or rewrite its original review binding.
    previous=load('_colab_intake_preserved_release',PREVIOUS_ROOT/ENTRY)
    approved=previous.authority()
    require(approved['source_sha']==PREVIOUS_SOURCE and approved['report_sha256']==PREVIOUS_REVIEW
            and approved['change_id']=='colab-intake-identity-20261011', 'PREVIOUS_RECOVERY_APPROVAL')
    state=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',
        'research-colab-intake-identity-20261011.service','-p','MainPID','-p','ActiveState'],text=True).splitlines())
    require(state.get('MainPID')=='0' and state.get('ActiveState') in {'inactive','failed'},'PREVIOUS_WRITER')
    return previous.recovery()


def network_predecessor(raw=None):
    """One exact zero-call predecessor; never mutate its host intent or state."""
    raw=trusted(ROOT/NETWORK_DOC).read_bytes() if raw is None else raw
    require(sha(raw)==NETWORK_SHA,'NETWORK_BINDING_CHANGED')
    b=json.loads(raw)
    previous=load('_colab_network_preserved_release',NETWORK_PREVIOUS/ENTRY)
    approved=previous.authority()
    require(approved['source_sha']==b['source'] and approved['report_sha256']==b['review']
            and approved['change_id']=='colab-timing-transport-repair-20261011','NETWORK_PREVIOUS_APPROVAL')
    props=['MainPID','ActiveState','SubState','ExecMainStatus','Result','InvocationID']
    state=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',b['unit'],
        *sum([['-p',name] for name in props],[])],text=True).splitlines())
    require(state==b['terminal'] and state['MainPID']=='0' and state['ActiveState']=='inactive'
            and state['Result']=='success' and state['ExecMainStatus']=='0','NETWORK_PREVIOUS_TERMINAL')
    if os.getuid()==0:
        for name,row in b['host_records'].items():
            require(sha(trusted(name).read_bytes())==row['sha256'],'NETWORK_HOST_RECORD_CHANGED')
        journal=subprocess.check_output(['journalctl','--no-pager','-o','cat',
            '_SYSTEMD_INVOCATION_ID='+b['invocation']],text=True)
        require(sha(journal.encode())==b['journal_sha256'],'NETWORK_TERMINAL_PROOF_CHANGED')
        value=json.loads(journal)
        require(value['charged_calls']==0 and value['operational_refusal']=='NETWORK_PREFLIGHT_FAILED_NO_CHARGE:claude'
                and value['phase']=='run_spec_review' and value['calls_used']==2,'NETWORK_ZERO_CALL_REFUSAL')
    return b


def connect(action='advance'):
    authority(held=action!='verify')
    previous=load('_colab_reader_previous_runtime',READER_PREVIOUS/ENTRY)
    approved=previous.authority()
    require(approved['source_sha']=='c4280f2723e0adcf3c7cee51a435fc775528b393' and
        approved['report_sha256']=='f5118bf6ae3c80cee8bf719adb4059b1f12637208c5a601a6a3fa6b6fab1d0b5','PREVIOUS_INSTALLED_APPROVAL')
    # Keep all predecessor authentication. Only its sequence component changes,
    # as separately source-bound by this release's implementation approval.
    original_branch=previous.original
    def branch_with_reviewed_sequence():
        branch=original_branch();factory=branch.load
        def selected(name,path):
            if name=='orchestrator.preparation_interleaving':
                require(Path(path)==BRANCH/'orchestrator/preparation_interleaving.py','EXACT_SEQUENCE_COMPONENT')
                return factory(name,ROOT/'orchestrator/preparation_interleaving.py')
            return factory(name,path)
        branch.load=selected
        return branch
    previous.original=branch_with_reviewed_sequence
    prior=previous.connect()  # Original intake, runtime, transport, host and cap checks.
    import orchestrator
    from orchestrator import analysis_driver,manual_driver
    context=load('orchestrator.manual_context',ROOT/'orchestrator/manual_context.py')
    orchestrator.manual_context=context;analysis_driver.manual_context=context;manual_driver.manual_context=context
    repair=load('orchestrator.colab_reader_recovery',ROOT/'orchestrator/colab_reader_recovery.py')
    raw=trusted(ROOT/repair.TURN_DOCUMENT).read_bytes();require(sha(raw)==repair.TURN_DOCUMENT_SHA,'RECOVERY_DOCUMENT_CHANGED')
    approval=authority(held=action!='verify')
    repair.install_hook(analysis_driver,json.loads(raw),approval['report_sha256'],action)
    return prior


def unit_bytes(raw):
    before='ExecStart=/usr/bin/python3 -s -B '+str(BRANCH/'tools/preparation_branch_repair_runtime.py')+' advance --lane colab_preparation\n'
    after='ExecStart=/usr/bin/python3 -s -B '+str(ROOT/ENTRY)+' advance\n'
    require(raw.decode().splitlines(keepends=True).count(before)==1
            and sum(s.startswith('ExecStart=') for s in raw.decode().splitlines())==1, 'EXACT_OLD_ENTRY')
    result=raw.replace(before.encode(),after.encode())
    require(result.replace(after.encode(),before.encode())==raw,'ENTRY_ONLY_CHANGE');return result


def host(action, transition):
    require(os.getuid()==0 and sys.flags.no_user_site,'ROOT_ISOLATED');approval=authority();network=network_predecessor();original()
    old=load('_colab_intake_original_host',BRANCH/'tools/preparation_branch_repair_host.py')
    if action=='status':
        require(transition is None,'STATUS_NO_TRANSITION');return old.status('colab_preparation')
    require(isinstance(transition,str) and re.fullmatch('[0-9a-f]{64}',transition),'TRANSITION')
    if action=='start':
        checked=subprocess.check_output(['runuser','-u','partho','--','env','RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),
            'python3','-s','-B',str(ROOT/ENTRY),'ready'],text=True)
        require(json.loads(checked)['status']=='READY_REVIEW_RECOVERY','RECOVERY_READY_REQUIRED')
    h=old.connect('colab_preparation',transition);frozen,_=h.authority(None)
    installed=json.loads(trusted(RECORD/'installed.json').read_bytes())
    frozen['hashes']={**frozen['hashes'],**installed['units'],**{str(ROOT/n):pin for n,pin in installed['files'].items()}}
    h.hashes(frozen);h.UNIT=UNIT;h.ENTRY=ROOT/ENTRY;h.OPERATION_ROOT=RECORD/'operations'/transition
    h.authority=lambda review:(frozen,approval)
    for p in [RECORD/'operations',h.OPERATION_ROOT]:
        if not p.exists():trusted(p.parent);p.mkdir(mode=0o700)
        trusted(p)
    previous=sys.argv
    try:
        sys.argv=[str(__file__),action,'--stage','author','--review',str(RECORD/'review')]
        return h.main()
    finally:sys.argv=previous


def preserved_native():
    """Authenticate preserved native config in its own established import context."""
    retained=load('_review_retained_native_install',NATIVE_PREVIOUS/'tools/item4_diagnostic_native_runtime.py')
    # Source authority is import-independent; configuration authority needs the
    # original runtime's bootstrap, isolated from this installer's modules.
    source,record=retained.reviewed_source()
    require(source['source_sha']=='1f2243448ca452abcad92ca355bead042cc731d2'
        and source['report_sha256']=='c27eaa20e857449d1d054621848fd63084dc811a092f98128e63c9a99797ba93','NATIVE_PREVIOUS_SOURCE')
    child="""import os,sys,json,hashlib,importlib.util
from pathlib import Path
assert os.getuid()==os.getgid()==1003 and sys.flags.no_user_site
path,pin=sys.argv[1:];path=Path(path)
assert hashlib.sha256(path.read_bytes()).hexdigest()==pin
spec=importlib.util.spec_from_file_location('_preserved_native_authority',path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.bootstrap();print(json.dumps(m.authority()))
"""
    require(os.getuid() in {0,1003} and sys.flags.no_user_site,'NATIVE_PROOF_IDENTITY')
    command=['env','RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),'/usr/bin/python3','-s','-B','-c',child,
        str(NATIVE_PREVIOUS/'tools/item4_diagnostic_native_runtime.py'),record['files']['tools/item4_diagnostic_native_runtime.py']]
    if os.getuid()==0:command=['runuser','-u','partho','--',*command]
    else:require(os.getgid()==1003,'NATIVE_PROOF_GROUP')
    approved=json.loads(subprocess.check_output(command,text=True,timeout=120))
    require(approved==source,'NATIVE_PREVIOUS_APPROVAL_CHANGED')
    return retained,approved


def install(source, review):
    require(os.getuid()==0 and sys.flags.no_user_site,'ROOT_ISOLATED')
    source,review=map(trusted,(source,review));approval,manifest=reviewed(review);branch=original()
    helper=load('_colab_intake_existing_installer',BRANCH/'tools/install_preparation_branch_repair.py')
    prior=load('_colab_intake_original_installer',ORIGINAL/'tools/install_preparation_runtime.py')
    prior.standalone_git(source)
    git=lambda *args:subprocess.check_output(['git',*args],cwd=source,text=True).strip()
    require(git('rev-parse','HEAD')==approval['source_sha'] and re.fullmatch(r'astra/manual-[a-z0-9-]+',git('branch','--show-current'))
            and not git('status','--porcelain'),'CLEAN_REVIEWED_SOURCE')
    bodies={n:trusted(source/helper.relative(n)).read_bytes() for n in manifest['source_files']}
    require(all(sha(body)==manifest['source_files'][n] for n,body in bodies.items()),'SOURCE_HASHES')
    require(bodies[ENTRY]==Path(__file__).read_bytes(),'EXECUTED_INSTALLER')
    network_predecessor(bodies[NETWORK_DOC])
    oldpath=Path('/etc/systemd/system')/OLD_UNIT;oldraw=trusted(oldpath).read_bytes()
    oldreceipt=json.loads(trusted(BRANCH_RECORD/'installed.json').read_bytes())
    require(sha(oldraw)==oldreceipt['units'][str(oldpath)],'PRIOR_UNIT_PIN')
    state=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',OLD_UNIT,'-p','MainPID','-p','ActiveState','-p','ExecMainStatus'],text=True).splitlines())
    require(state=={'MainPID':'0','ActiveState':'inactive','ExecMainStatus':'0'},'PRIOR_UNIT_HELD')
    previous=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show','research-colab-network-continuation-20261011.service','-p','MainPID','-p','ActiveState'],text=True).splitlines())
    require(previous['MainPID']=='0' and previous['ActiveState'] in {'inactive','failed'},'PREVIOUS_REVIEW_TERMINAL')
    retained,native_approval=preserved_native()
    require(native_approval['source_sha']=='1f2243448ca452abcad92ca355bead042cc731d2'
        and native_approval['report_sha256']=='c27eaa20e857449d1d054621848fd63084dc811a092f98128e63c9a99797ba93','NATIVE_PREVIOUS_APPROVAL')
    for unit in ('research-colab-reader-recovery-20261011.service',retained.REVIEW_UNIT,retained.CPU_UNIT):
        observed=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',unit,'-p','MainPID','-p','ActiveState'],text=True).splitlines())
        require(observed['MainPID']=='0' and observed['ActiveState'] in {'inactive','failed'},'PREVIOUS_WRITER')
    target=oldpath.with_name(UNIT);body=unit_bytes(oldraw)
    native_target=oldpath.with_name(NATIVE_UNIT)
    native_raw=trusted(oldpath.with_name(retained.REVIEW_UNIT)).read_bytes()
    before=('ExecStart=/usr/bin/python3 -s -B '+str(NATIVE_PREVIOUS/'tools/item4_diagnostic_review_runtime.py')+' run\n').encode()
    after=('ExecStart=/usr/bin/python3 -s -B '+str(ROOT/'tools/item4_diagnostic_review_runtime.py')+' run\n').encode()
    require(native_raw.splitlines(keepends=True).count(before)==1,'EXACT_NATIVE_UNIT_ENTRY')
    native_body=native_raw.replace(before,after)
    require(native_body.replace(after,before)==native_raw,'NATIVE_ENTRY_ONLY_CHANGE')
    units={target:body,native_target:native_body}
    for p in [ROOT,RECORD,*units]:
        trusted(p.parent);require(not p.exists() and not p.is_symlink(),'EXISTING_INSTALL_PRESERVED')
    review_files={p.name:trusted(p).read_bytes() for p in review.iterdir() if p.is_file()}
    require(len(review_files)==len(list(review.iterdir())),'FLAT_REVIEW')
    check=json.loads(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',helper.OWNER_CHECK],text=True))
    require(check['status']=='NO_RUNNING_CALL','LIVE_CALL');prior.verify_units(units)
    helper.mkdir(RECORD);helper.put(RECORD/'INSTALL_INTENT.json',json.dumps({'source':approval['source_sha'],'review_sha256':approval['report_sha256']},sort_keys=True).encode())
    helper.mkdir(ROOT)
    for n,content in bodies.items():helper.put(ROOT/helper.relative(n),content)
    for n,content in review_files.items():helper.put(RECORD/'review'/n,content)
    for path,raw in units.items():helper.put(path,raw)
    installed={'root':str(ROOT),'source':approval['source_sha'],'review_sha256':approval['report_sha256'],
               'files':manifest['source_files'],'units':{str(path):sha(raw) for path,raw in units.items()},'status':'INSTALLED_HELD'}
    helper.put(RECORD/'installed.json',json.dumps(installed,sort_keys=True).encode())
    subprocess.run(['systemctl','daemon-reload'],check=True)
    result=subprocess.run(['runuser','-u','partho','--','env','PYTHONPATH='+str(ORIGINAL),'PYTHONDONTWRITEBYTECODE=1',
        'RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),'python3','-s','-B',str(ROOT/ENTRY),'verify'],capture_output=True)
    helper.put(RECORD/'VERIFY.stdout',result.stdout);helper.put(RECORD/'VERIFY.stderr',result.stderr)
    require(result.returncode==0,'SERVICE_VERIFY_FAILED')
    result=subprocess.run(['runuser','-u','partho','--','env','PYTHONPATH='+str(ORIGINAL),'PYTHONDONTWRITEBYTECODE=1',
        'RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),'python3','-s','-B',str(ROOT/'tools/item4_diagnostic_review_runtime.py'),'verify'],capture_output=True)
    helper.put(RECORD/'NATIVE_VERIFY.stdout',result.stdout);helper.put(RECORD/'NATIVE_VERIFY.stderr',result.stderr)
    require(result.returncode==0,'NATIVE_SERVICE_VERIFY_FAILED')
    complete={'status':'INSTALLED_HELD','source':approval['source_sha'],'scientific_calls':0,'provider_calls':0}
    helper.put(RECORD/'COMPLETE.json',json.dumps(complete,sort_keys=True).encode());return complete


def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('action',choices=['install','verify','recover','ready','advance','status','start','pulse'])
    p.add_argument('--source',type=Path);p.add_argument('--review',type=Path);p.add_argument('--transition');a=p.parse_args(argv)
    sys.path.insert(0,str(ORIGINAL))
    if a.action=='install':
        require(a.source is not None and a.review is not None and a.transition is None,'INSTALL_ARGUMENTS');return install(a.source,a.review)
    require(a.source is None and a.review is None,'NO_SOURCE_OVERRIDE')
    if a.action in {'status','start','pulse'}:return host(a.action,a.transition)
    require(a.transition is None and os.getuid()==os.getgid()==1003,'SERVICE_ACTION')
    prior=connect(a.action)
    result=prior.main(['advance','--scope',str(prior.RECORD/'preparation-interleaving.json'),
        '--review-report',str(prior.RECORD/'review/report.md'),'--lane','colab_preparation'])
    if a.action=='verify':
        require(result=={'status':'VERIFIED_HELD','model_calls':0,'provider_calls':0},'ACTUAL_VERIFY_REQUIRED')
        return {'status':'VERIFIED_HELD','scientific_calls':0,'provider_calls':0}
    return result


if __name__=='__main__':
    os.umask(0o077);print(json.dumps(main(),sort_keys=True))
