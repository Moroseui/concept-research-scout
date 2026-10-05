#!/usr/bin/env python3
"""Reviewed evidence assembler over the existing M3 lane and scientific identity.

This immutable administrative release is bound independently from the original
scientific package. Native admission, accounting, isolation and stops remain in
the driver. The previously reviewed provider component remains separately bound.
"""
import argparse
from pathlib import Path
import json
from orchestrator import modal_driver, private_records
from orchestrator.manual_executor import read, digest
from orchestrator.autonomy_review import verify_result
from orchestrator.manual_host_guard import trusted
from tools.modal_provider_transition import advance_once, load_provider

CHANGE = 'm3-interpretation-evidence-delivery'
REQUIRED = ('orchestrator/context_budget.py', 'orchestrator/manual_context.py',
    'orchestrator/manual_driver.py', 'orchestrator/manual_stage.py',
    'orchestrator/manual_contract.py', 'orchestrator/modal_driver.py',
    'orchestrator/modal_evidence.py', 'tools/modal_evidence_transition.py',
    'tools/modal_interpretation_recovery.py', 'tools/install_m3_evidence.py')


def approval(folder):
    result = verify_result(folder)
    if result['verdict'] != 'APPROVE' or result['change_id'] != CHANGE:
        raise ValueError('EVIDENCE_DELIVERY_APPROVAL_REQUIRED')
    manifest = read(Path(folder) / 'packet-manifest.json')
    source = Path(__file__).resolve().parents[1]
    for name in REQUIRED:
        if manifest['source_files'].get(name) != digest((source / name).read_bytes()):
            raise ValueError('EVIDENCE_IMPLEMENTATION_CHANGED')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', required=True)
    parser.add_argument('--preparation', required=True)
    parser.add_argument('--approval-folder', required=True)
    parser.add_argument('--provider-folder', required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    trusted(source)
    approved = approval(args.approval_folder)
    provider = load_provider(args.provider_folder)

    def factory(state):
        config = read(Path(state) / 'lane.json')
        driver = modal_driver.ModalDriver(state, provider=provider(config['modal']))
        receipt = read(Path(state) / 'interpretation-evidence-recovery-20261003/COMPLETE.json')
        if receipt['implementation_source'] != approved['source_sha']:
            raise ValueError('EVIDENCE_RECOVERY_IMPLEMENTATION_BINDING')
        return driver

    print(json.dumps(modal_driver.supervise(args.state, args.preparation,
        factory=factory, provider_factory=provider, run=advance_once), sort_keys=True))


if __name__ == '__main__':
    main()
