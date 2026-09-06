"""Trusted read-only evidence broker. Requests cannot select paths or commands.

Run collection as the setup operator, never by giving reviewer sessions shell tools.
Historical checked receipts are evidence, not proof of present deployment behavior.
"""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from orchestrator.research_context import checked
from orchestrator.git_publication import scan

SOURCES = {
    'installed_sources': ('docs/operations/READINESS_HOSTED_ACCEPTANCE_20260906.json',),
    'service_runtime': ('docs/operations/READINESS_HOSTED_ACCEPTANCE_20260906.json',),
    'identity_boundaries': ('docs/operations/PROTECTED_WRITER_ADMISSION_DECISION.md',),
    'resource_limits': ('docs/operations/READINESS_HOSTED_ACCEPTANCE_20260906.json',),
    'completion_continuation': ('docs/operations/hosted-orientation-20260906/context-verification.json',),
    'restart_recovery': ('docs/operations/DEPLOYMENT_CLOSEOUT_CHECKLIST.md',),
    'backup_recovery': ('docs/operations/DEPLOYMENT_CLOSEOUT_CHECKLIST.md',),
    'reporting': ('docs/operations/REPORTING.md',),
    'phone_notifications': ('docs/operations/NOTIFICATION_APP_IDENTITY_20260906.json',),
    'laptop_independence': ('docs/operations/DEPLOYMENT_CLOSEOUT_CHECKLIST.md',),
}
UNITS = ('research-system-controller.service', 'research-system-controller.timer',
         'research-system-orientation-20260906.service')
PROPERTIES = ('LoadState', 'ActiveState', 'SubState', 'User', 'Result', 'ExecMainStatus',
              'MemoryMax', 'CPUQuotaPerSecUSec', 'NoNewPrivileges', 'ProtectSystem')


def validate(request):
    if not isinstance(request, dict) or set(request) != {'kind', 'purpose', 'affected_task'}:
        raise ValueError('EVIDENCE_REQUEST_SCHEMA')
    if request['kind'] not in SOURCES:
        raise ValueError('EVIDENCE_KIND_NOT_ALLOWED')
    for key in ('purpose', 'affected_task'):
        value = request[key]
        if not isinstance(value, str) or not value.strip() or len(value) > 500:
            raise ValueError('EVIDENCE_REQUEST_TEXT')
    scan('request.json', json.dumps(request).encode())
    return hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()


def collect(root, request, *, hosted=False):
    identity = validate(request)
    records = []
    for name in SOURCES[request['kind']]:
        try:
            raw = checked(root, name)
        except FileNotFoundError:
            records.append({'source': name, 'status': 'UNAVAILABLE'}); continue
        scan(name, raw.encode())
        records.append({'source': name, 'sha256': hashlib.sha256(raw.encode()).hexdigest(),
                        'status': 'HISTORICAL_DOCUMENT_NOT_CURRENT_EXECUTION_PROOF', 'content': raw})
    result = {'version': 1, 'request_id': identity, 'request': request,
              'collected_utc': datetime.now(timezone.utc).isoformat(), 'records': records,
              'current_observations': [],
              'limitations': ['No patient files, private logs, credentials or arbitrary commands are read.',
                             'No new execution, restart, restore or phone delivery is performed.',
                             'Missing or historical evidence does not establish current success.']}
    if hosted and request['kind'] in ('service_runtime', 'resource_limits'):
        for unit in UNITS:
            command = ['systemctl', 'show', unit, '--property='+','.join(PROPERTIES)]
            proc = subprocess.run(command, capture_output=True, text=True, timeout=15)
            # Never return raw stderr or unexpected properties from a service definition.
            fields = {}
            for line in proc.stdout.splitlines():
                key, sep, value = line.partition('=')
                if sep and key in PROPERTIES: fields[key] = value
            scan('service-properties.json', json.dumps(fields).encode())
            result['current_observations'].append({'unit': unit, 'returncode': proc.returncode,
                'properties': fields, 'status': 'CURRENT_CONFIGURATION_ONLY',
                'execution_proven': False})
    scan('evidence-response.json', json.dumps(result).encode())
    return result


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--request', type=Path, required=True)
    p.add_argument('--hosted', action='store_true')
    args = p.parse_args()
    if args.request.is_symlink() or args.request.stat().st_size > 4096:
        raise ValueError('EVIDENCE_REQUEST_FILE')
    result = collect(Path(__file__).resolve().parents[1], json.loads(args.request.read_text()), hosted=args.hosted)
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
