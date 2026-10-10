"""Held runtime for exactly two independently reviewed preparation lanes.

Reuse the existing scientific driver, host guard, clients and isolation. No
provider dispatch, background scheduler, credential handling or ledger reset.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

from orchestrator import preparation_interleaving as pi,private_records
from orchestrator.manual_host_guard import trusted

ROOT=Path(__file__).resolve().parents[1]
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/preparation-and-cap-repair-20261010')
OLD_RUNTIME=Path('/opt/research-system/manual-repair-helpers/item4-author24-delivery-20261010/tools/item4_smoke_response_runtime.py')


def reviewed_root(overlay):
    overlay.verify()
    from orchestrator.autonomy_review import verify_result
    q=verify_result(overlay.review_folder)
    manifest=json.loads(private_records.check(overlay.review_folder/'packet-manifest.json').read_bytes())
    installed=json.loads(trusted(RECORD/'installed.json').read_bytes())
    pi.require(installed.get('root')==str(ROOT) and installed.get('source')==q['source_sha']
        and installed.get('review_sha256')==q['report_sha256']
        and installed.get('status')=='INSTALLED_HELD','INSTALLED_RECEIPT')
    names=[name for name in manifest['source_files'] if name.startswith(('orchestrator/','tools/','docs/'))]
    pi.require(all(name in names for name in ('orchestrator/preparation_interleaving.py',
        'orchestrator/analysis_driver.py','orchestrator/aggregate_analysis_scope.py',
        'orchestrator/colab_preparation_scope.py','tools/preparation_scientific_runtime.py')),'FULL_RUNTIME_REVIEW')
    for name in names:
        pi.require(pi.sha(trusted(ROOT/name).read_bytes())==manifest['source_files'][name],'RUNTIME_SOURCE_CHANGED')


def connect_item4(overlay):
    """Load the original approved helper and substitute one reviewed sequence hook.

    Original helper source, frozen scope, genuine approval and grant are checked
    in full by its own connection. Only the new scoped-calls file is substituted;
    its original acceptance predicate follows the default-inert hook unchanged.
    """
    old=overlay.scope['item4_scope']
    manifest=json.loads(private_records.check(overlay.path(old['review_folder'])/'packet-manifest.json').read_bytes())
    raw=trusted(OLD_RUNTIME).read_bytes()
    pi.require(pi.sha(raw)==manifest['source_files']['tools/item4_smoke_response_runtime.py'],'OLD_RUNTIME_PIN')
    # Reuse the installed dated-cap route before original scopes capture the
    # base admission method. Its own genuine approval/source/unit checks remain.
    dated=Path('/opt/research-system/manual-repair-helpers/temporary-daily-cap-20261010/tools/temporary_daily_cap.py')
    spec=importlib.util.spec_from_file_location('_approved_installed_dated_cap',trusted(dated))
    cap=importlib.util.module_from_spec(spec);spec.loader.exec_module(cap)
    module=cap.author_route()
    factory=module.module
    def selected(name,path):
        if name=='orchestrator.item4_scoped_calls':
            pi.require(Path(path)==module.ROOT/'orchestrator/item4_scoped_calls.py','EXACT_ITEM4_COMPONENT')
            return factory(name,ROOT/'orchestrator/item4_scoped_calls.py')
        return factory(name,path)
    module.module=selected
    return module


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('action',choices=['verify','init','advance','item4-author'])
    p.add_argument('--scope',type=Path,required=True)
    p.add_argument('--review-report',type=Path,required=True)
    p.add_argument('--lane',choices=['aggregate_analysis','colab_preparation'])
    args=p.parse_args(argv)
    pi.require(os.getuid()==os.getgid()==1003,'SERVICE_ACCOUNT')
    raw=trusted(args.scope).read_bytes();value=json.loads(raw)
    pi.require(raw==pi.scope_bytes(value),'CANONICAL_REVIEWED_SCOPE_BYTES')
    overlay=pi.Overlay(value,args.review_report.parent)
    pi.require(pi.sha(trusted(args.review_report).read_bytes())==overlay.approval,'REPORT_BINDING')
    reviewed_root(overlay)
    if args.action=='verify':
        return {'status':'VERIFIED_HELD','scientific_calls':0,'provider_calls':0}
    if args.action=='item4-author':
        pi.require(args.lane is None,'ITEM4_NO_PREPARATION_LANE')
        old=connect_item4(overlay)
        # Old connect installs its exact scoped allowance; the outer reviewed
        # overlay must follow it, so wrap just this setup call, once.
        previous=old.connect;used=[]
        def connect():
            pi.require(not used,'ONE_ITEM4_CONNECTION');used.append(True)
            result=previous()
            pi.connect(value,args.review_report.parent)
            return result
        old.connect=connect
        return old.main(['run'])
    pi.require(args.lane is not None,'NAMED_LANE_REQUIRED')
    lane=value['lanes'][args.lane]
    repository=Path(lane['state']).parent/'repository'
    # Scientific profile commits belong to this service-owned lane repository;
    # imported engine/runtime code remains in the separately immutable release.
    pi.require(not repository.is_symlink() and repository.is_dir(),'LANE_REPOSITORY')
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=repository,text=True).strip()
    pi.require(branch.startswith('astra/'),'LANE_WORK_BRANCH')
    subprocess.run(['git','merge-base','--is-ancestor',value['source_sha'],'HEAD'],cwd=repository,check=True)
    manifest=json.loads(private_records.check(overlay.review_folder/'packet-manifest.json').read_bytes())
    for name,pin in manifest['source_files'].items():
        if name.startswith(('orchestrator/','tools/','docs/')):
            pi.require(pi.sha(private_records.check(repository/name).read_bytes())==pin,'LANE_SOURCE_CHANGED')
    from orchestrator.analysis_driver import AnalysisDriver,initialize
    if args.action=='init':
        pi.require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=repository,text=True).strip()==value['source_sha'],'INITIAL_SOURCE')
        # Initialization creates no model call and consumes no call slot.
        return initialize(repository,lane['state'],args.review_report,lane['plan'])
    pi.connect(value,args.review_report.parent)
    driver=AnalysisDriver(lane['state'])
    pi.require(driver.root.resolve()==repository.resolve(),'LANE_REPOSITORY_BINDING')
    return driver.advance()


if __name__=='__main__':
    os.umask(0o077)
    print(json.dumps(main(),sort_keys=True))
