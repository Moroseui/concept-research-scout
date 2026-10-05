#!/usr/bin/env python3
"""Run the unchanged M3 driver with one independently reviewed provider component.

No module is monkeypatched and no release file or scientific identity is changed.
The existing provider-injection hook supplies the immutable replacement; original
source/configuration guards, single transition, admission and caps remain native.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from orchestrator import modal_driver, private_records
from orchestrator.remote_supervisor import lock


@private_records.private_umask
def advance_once(state, *, factory):
    path=Path(state)/"one-run.lock"
    if path.exists():private_records.check(path)
    with lock(path):
        private_records.check(path)
        return factory(state).advance()


def load_provider(folder):
    folder=Path(folder)
    for p in [folder,*folder.parents]:
        if p.is_symlink() or p.stat().st_uid!=0 or p.stat().st_mode&0o022:
            raise ValueError('PROVIDER_COMPONENT_UNTRUSTED')
    binding=folder/'approval-binding.json';path=folder/'modal_provider.py'
    for p in [binding,path]:
        if p.is_symlink() or not p.is_file() or p.stat().st_uid!=0 or p.stat().st_mode&0o022:
            raise ValueError('PROVIDER_COMPONENT_UNTRUSTED')
    approved=json.loads(binding.read_text())
    if approved.get('scope')!='m3-image-preflight' or approved.get('verdict')!='APPROVE':
        raise ValueError('PROVIDER_COMPONENT_APPROVAL_SCOPE')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=approved['provider_sha256']:
        raise ValueError('PROVIDER_COMPONENT_CHANGED')
    spec=importlib.util.spec_from_file_location('reviewed_m3_modal_provider',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.ModalProvider


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--state',required=True);parser.add_argument('--preparation',required=True);args=parser.parse_args()
    provider=load_provider(Path(__file__).parent)
    def factory(state):
        config=json.loads((Path(state)/'lane.json').read_text())
        return modal_driver.ModalDriver(state,provider=provider(config['modal']))
    print(json.dumps(modal_driver.supervise(args.state,args.preparation,factory=factory,provider_factory=provider,run=advance_once),sort_keys=True))

if __name__=='__main__':main()
