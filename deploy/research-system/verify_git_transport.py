#!/usr/bin/env python3
"""Bounded file-transport contention/recovery probe; no live refs or credentials.

Run from an immutable source snapshot under a non-root test identity. Destination
must be absent. Preserve it after success or failure; never automatically replay
an uncertain invocation. Raw Git diagnostics stay in its private sibling folder.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from orchestrator.dispatch_limiter import GitLedger, REF, admit, initial
from orchestrator.git_diagnostics import run as git_run


def verify(root, source):
    if not root.is_absolute() or root.exists():
        raise ValueError('FRESH_ABSOLUTE_ATTEMPT_REQUIRED')
    if shutil.disk_usage(root.parent).free < 512 * 1024 * 1024:
        raise ValueError('DIAGNOSTIC_CAPACITY_REQUIRED')
    os.umask(0o077)
    root.mkdir(mode=0o700)
    # Bound every Git subprocess, including library calls, to private local-only
    # transport. No caller credential helper or model environment is needed.
    os.environ['RESEARCH_GIT_DIAGNOSTICS'] = str(root / 'diagnostics')
    os.environ['GIT_CONFIG_NOSYSTEM'] = '1'
    os.environ['GIT_CONFIG_GLOBAL'] = '/dev/null'
    os.environ['GIT_ALLOW_PROTOCOL'] = 'file'
    os.environ['GIT_TERMINAL_PROMPT'] = '0'
    start = time.monotonic()
    (root / 'started.json').write_text(json.dumps({'source': source, 'pid': os.getpid(), 'uid': os.getuid()}))
    remote = root / 'remote.git'
    git_run(['git', 'init', '-q', '--bare', str(remote)], check=True)
    if not GitLedger(remote).cas(None, initial()):
        raise ValueError('FRESH_INITIALIZATION_FAILED')
    config = {'status': 'RATIFIED', 'operator_approval': 'SYNTHETIC_ONLY',
              'state_write_permission': 'OPERATOR_AUTHORIZED', 'n': 4,
              'window': 'UTC_CALENDAR_DAY', 'state_ref': REF}
    now = datetime(2026, 9, 7, 12, tzinfo=timezone.utc)

    def client(number):
        path = root / ('client-' + str(number))
        git_run(['git', 'init', '-q', str(path)], check=True)
        git_run(['git', '-C', str(path), 'remote', 'add', 'origin', str(remote)], check=True)
        return GitLedger(path, remote=True, expected_remote=str(remote))

    def event(number):
        return {'run_id': str(number), 'attempt': '1', 'source': source, 'branch': 'main'}

    def invoke(number):
        try:
            return {'number': number, 'result': admit(client(number), config, event(number), now, max_retries=30)}
        except Exception as error:
            # Status is ambiguous until the durable ledger is reconciled. Preserve
            # original Git stderr through the shared adapter, never print it.
            return {'number': number, 'error_type': type(error).__name__,
                    'returncode': getattr(error, 'returncode', None)}

    with ThreadPoolExecutor(max_workers=8) as pool:
        outcomes = list(pool.map(invoke, range(1, 25)))
    (root / 'outcomes.json').write_text(json.dumps(outcomes, indent=2))
    before, state = GitLedger(remote).read()
    recover = client('recovery')
    recovered = []
    for key in sorted(state['events']):
        number = int(key.split(':')[0])
        recovered.append(admit(recover, config, event(number), now)['duplicate_admission'])
    after, state_after = GitLedger(remote).read()
    midnight = admit(recover, config, event(25), now + timedelta(days=1))
    diagnostics = list((root / 'diagnostics').glob('*/receipt.json'))
    captures = [json.loads(p.read_text()) for p in diagnostics]
    summary = {
        'schema': 1, 'scope': 'HOST_LOCAL_FILE_TRANSPORT_SYNTHETIC_ONLY',
        'source': source, 'uid': os.getuid(), 'requests': 24, 'workers': 8,
        'admitted': sum(o.get('result', {}).get('status') == 'ADMITTED' for o in outcomes),
        'errors': sum('error_type' in o for o in outcomes),
        'durable_count': state['count'], 'durable_events': len(state['events']),
        'halted': state['halted'], 'notifications': len(state['notifications']),
        'duplicate_recovery_all': len(recovered) == 8 and all(recovered),
        'recovery_unchanged_pin': before == after,
        'midnight_halt': midnight['status'] == 'HALTED_OPERATOR_RESET_REQUIRED',
        'diagnostic_receipts': len(captures),
        'nonzero_git_exits': sum(c.get('returncode') not in (0, None) for c in captures),
        'diagnostic_hashes_verified': all(hashlib.sha256((p.parent / 'stderr').read_bytes()).hexdigest() == c['stderr_sha256'] for p, c in zip(diagnostics, captures)),
        'diagnostic_modes_private': all((p.stat().st_mode & 0o777) == 0o600 and (p.parent.stat().st_mode & 0o777) == 0o700 for p in diagnostics),
        'elapsed_seconds': time.monotonic() - start,
        'original_exit_128_cause': 'UNRESOLVED', 'live_activation': False,
        'network_protocols': ['file'], 'outcomes_sha256': hashlib.sha256((root / 'outcomes.json').read_bytes()).hexdigest(),
    }
    summary['passed'] = (summary['errors'] == 0 and summary['admitted'] == 8
                         and state_after['count'] == 8 and summary['durable_events'] == 8
                         and summary['notifications'] == 2 and summary['halted']
                         and summary['duplicate_recovery_all'] and summary['recovery_unchanged_pin']
                         and summary['midnight_halt'] and summary['diagnostic_hashes_verified']
                         and summary['diagnostic_modes_private'])
    (root / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--attempt', type=Path, required=True)
    p.add_argument('--source', required=True)
    a = p.parse_args()
    if len(a.source) != 40 or any(c not in '0123456789abcdef' for c in a.source):
        raise ValueError('EXACT_SOURCE_REQUIRED')
    summary = verify(a.attempt, a.source)
    print(json.dumps(summary))
    return 0 if summary['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
