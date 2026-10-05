#!/usr/bin/env python3
"""One existing M3 transition per systemd host-proof invocation.

An administrative entry point: imports the unchanged reviewed scientific release.
The native supervisor still owns expiry/uncertainty checks and asset cleanup.
No retry, allowance, proof refresh or proof-age exception is introduced.
"""
import argparse
import json
from pathlib import Path
from orchestrator import modal_driver, private_records
from orchestrator.remote_supervisor import lock


@private_records.private_umask
def advance_once(state, *, factory=modal_driver.ModalDriver):
    state = Path(state)
    path = state / 'one-run.lock'
    if path.exists():
        private_records.check(path)
    with lock(path):
        private_records.check(path)
        return factory(state).advance()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', required=True)
    parser.add_argument('--preparation', required=True)
    args = parser.parse_args()
    print(json.dumps(modal_driver.supervise(
        args.state, args.preparation, run=advance_once), sort_keys=True))


if __name__ == '__main__':
    main()
