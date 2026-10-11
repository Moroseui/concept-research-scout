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

CHANGE = 'colab-intake-source-alignment-20261011'
# One bounded administrative recovery review; original failed request is retained.
REVIEW_CHANGE = 'colab-timing-transport-repair-20261011'
REVIEW_SCOPE = 'docs/COLAB_INTAKE_TRANSPORT_RECOVERY_SCOPE.md'
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
OLD_UNIT = 'research-preparation-branch-admission-repair-20261010-colab_preparation.service'
REQUIRED = [ENTRY, RECOVERY, REVIEW_SCOPE, 'docs/COLAB_TIMING_TRANSPORT_REPAIR_SCOPE.md', 'tools/reviewer_connection_timing.py', 'docs/COLAB_INTAKE_PREMODEL_PRIVATE.json',
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
    require(set(installed['units'])=={'/etc/systemd/system/'+UNIT}, 'UNIT_SET')
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


def connect(held=True):
    authority(held=held);branch=original();prior=branch.connect();m=recovery();b=m.binding()
    require(sha(trusted(ORIGINAL/'orchestrator/scientific_intake.py').read_bytes())==b['original_intake_sha256'], 'ORIGINAL_INTAKE_CHANGED')
    from orchestrator import scientific_search as search
    require(sys.modules.get('orchestrator.scientific_search') is search
            and Path(search.__file__).resolve()==ORIGINAL/'orchestrator/scientific_search.py'
            and sha(trusted(search.__file__).read_bytes())==b['original_search_sha256'], 'SEARCH_GUARD_UNCHANGED')
    patched=load('orchestrator.scientific_intake',ROOT/'orchestrator/scientific_intake.py')
    import orchestrator
    orchestrator.scientific_intake=patched
    from orchestrator import manual_runtime
    load('_colab_review_connection_timing',ROOT/'tools/reviewer_connection_timing.py').bind(manual_runtime)
    return prior


def unit_bytes(raw):
    before='ExecStart=/usr/bin/python3 -s -B '+str(BRANCH/'tools/preparation_branch_repair_runtime.py')+' advance --lane colab_preparation\n'
    after='ExecStart=/usr/bin/python3 -s -B '+str(ROOT/ENTRY)+' advance\n'
    require(raw.decode().splitlines(keepends=True).count(before)==1
            and sum(s.startswith('ExecStart=') for s in raw.decode().splitlines())==1, 'EXACT_OLD_ENTRY')
    result=raw.replace(before.encode(),after.encode())
    require(result.replace(after.encode(),before.encode())==raw,'ENTRY_ONLY_CHANGE');return result


def host(action, transition):
    require(os.getuid()==0 and sys.flags.no_user_site,'ROOT_ISOLATED');approval=authority();original()
    old=load('_colab_intake_original_host',BRANCH/'tools/preparation_branch_repair_host.py')
    if action=='status':
        require(transition is None,'STATUS_NO_TRANSITION');return old.status('colab_preparation')
    require(isinstance(transition,str) and re.fullmatch('[0-9a-f]{64}',transition),'TRANSITION')
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
    oldpath=Path('/etc/systemd/system')/OLD_UNIT;oldraw=trusted(oldpath).read_bytes()
    oldreceipt=json.loads(trusted(BRANCH_RECORD/'installed.json').read_bytes())
    require(sha(oldraw)==oldreceipt['units'][str(oldpath)],'PRIOR_UNIT_PIN')
    state=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',OLD_UNIT,'-p','MainPID','-p','ActiveState','-p','ExecMainStatus'],text=True).splitlines())
    require(state=={'MainPID':'0','ActiveState':'inactive','ExecMainStatus':'0'},'PRIOR_UNIT_HELD')
    target=oldpath.with_name(UNIT);body=unit_bytes(oldraw)
    for p in [ROOT,RECORD,target]:
        trusted(p.parent);require(not p.exists() and not p.is_symlink(),'EXISTING_INSTALL_PRESERVED')
    review_files={p.name:trusted(p).read_bytes() for p in review.iterdir() if p.is_file()}
    require(len(review_files)==len(list(review.iterdir())),'FLAT_REVIEW')
    check=json.loads(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',helper.OWNER_CHECK],text=True))
    require(check['status']=='NO_RUNNING_CALL','LIVE_CALL');prior.verify_units({target:body})
    helper.mkdir(RECORD);helper.put(RECORD/'INSTALL_INTENT.json',json.dumps({'source':approval['source_sha'],'review_sha256':approval['report_sha256']},sort_keys=True).encode())
    helper.mkdir(ROOT)
    for n,content in bodies.items():helper.put(ROOT/helper.relative(n),content)
    for n,content in review_files.items():helper.put(RECORD/'review'/n,content)
    helper.put(target,body)
    installed={'root':str(ROOT),'source':approval['source_sha'],'review_sha256':approval['report_sha256'],
               'files':manifest['source_files'],'units':{str(target):sha(body)},'status':'INSTALLED_HELD'}
    helper.put(RECORD/'installed.json',json.dumps(installed,sort_keys=True).encode())
    subprocess.run(['systemctl','daemon-reload'],check=True)
    result=subprocess.run(['runuser','-u','partho','--','env','PYTHONPATH='+str(ORIGINAL),'PYTHONDONTWRITEBYTECODE=1',
        'RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),'python3','-s','-B',str(ROOT/ENTRY),'verify'],capture_output=True)
    helper.put(RECORD/'VERIFY.stdout',result.stdout);helper.put(RECORD/'VERIFY.stderr',result.stderr)
    require(result.returncode==0,'SERVICE_VERIFY_FAILED')
    complete={'status':'INSTALLED_HELD','source':approval['source_sha'],'scientific_calls':0,'provider_calls':0}
    helper.put(RECORD/'COMPLETE.json',json.dumps(complete,sort_keys=True).encode());return complete


def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('action',choices=['install','verify','ready','advance','status','start','pulse'])
    p.add_argument('--source',type=Path);p.add_argument('--review',type=Path);p.add_argument('--transition');a=p.parse_args(argv)
    sys.path.insert(0,str(ORIGINAL))
    if a.action=='install':
        require(a.source is not None and a.review is not None and a.transition is None,'INSTALL_ARGUMENTS');return install(a.source,a.review)
    require(a.source is None and a.review is None,'NO_SOURCE_OVERRIDE')
    if a.action in {'status','start','pulse'}:return host(a.action,a.transition)
    require(a.transition is None and os.getuid()==os.getgid()==1003,'SERVICE_ACTION')
    authority(held=a.action!='verify');original()
    if a.action=='verify':
        connect(held=False)  # Exercise the real installed connection before completion.
        recovery().ready()
        return {'status':'VERIFIED_HELD','scientific_calls':0,'provider_calls':0}
    m=recovery()
    if a.action=='ready':return m.ready()
    m.ready();prior=connect()
    return prior.main(['advance','--scope',str(prior.RECORD/'preparation-interleaving.json'),
        '--review-report',str(prior.RECORD/'review/report.md'),'--lane','colab_preparation'])


if __name__=='__main__':
    os.umask(0o077);print(json.dumps(main(),sort_keys=True))
