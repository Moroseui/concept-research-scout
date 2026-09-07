"""Trusted read-only evidence broker. Requests cannot select paths or commands.

Run collection as the setup operator, never by giving reviewer sessions shell tools.
Historical checked receipts are evidence, not proof of present deployment behavior.
"""
import hashlib
import json
import subprocess
import os
from datetime import datetime, timezone
from pathlib import Path
from orchestrator.research_context import checked
from orchestrator.git_publication import scan

SOURCES = {
    'handover_implementation': ('orchestrator/handover_runtime.py','orchestrator/handover_coordinator.py',
        'orchestrator/completion_bridge.py','orchestrator/report_delivery.py',
        'orchestrator/handover_notifications.py','orchestrator/phone_notifications.py',
        'orchestrator/protected_handover.py','scripts/verify_handover_service.py','deploy/research-system/research-system-handover.service',
        'deploy/research-system/research-system-handover-controller.service',
        'deploy/research-system/research-system-handover.socket'),
    'installed_sources': ('docs/operations/READINESS_HOSTED_ACCEPTANCE_20260906.json',),
    'service_runtime': ('docs/operations/READINESS_HOSTED_ACCEPTANCE_20260906.json',),
    'identity_boundaries': ('docs/operations/PROTECTED_WRITER_ADMISSION_DECISION.md',),
    'resource_limits': ('docs/operations/READINESS_HOSTED_ACCEPTANCE_20260906.json',),
    'completion_continuation': ('docs/operations/hosted-orientation-20260906/context-verification.json',),
    'restart_recovery': ('docs/operations/hosted-service-acceptance-20260907/receipt.json',),
    'backup_recovery': ('docs/operations/hosted-service-acceptance-20260907/backup-recovery.json',),
    'human_controls': ('docs/operations/hosted-service-acceptance-20260907/human-controls.json',),
    'deployment_acceptance': ('docs/operations/hosted-service-acceptance-20260907/receipt.json',
        'docs/operations/hosted-service-acceptance-20260907/backup-recovery.json',
        'docs/operations/hosted-service-acceptance-20260907/human-controls.json',
        'docs/operations/NOTIFICATION_APP_IDENTITY_20260906.json'),
    'reporting': ('docs/operations/REPORTING.md',),
    'phone_notifications': ('docs/operations/NOTIFICATION_APP_IDENTITY_20260906.json',),
    'laptop_independence': ('docs/operations/DEPLOYMENT_CLOSEOUT_CHECKLIST.md',),
}
UNITS = ('research-system-controller.service', 'research-system-controller.timer',
         'research-system-orientation-20260906.service',
         'research-system-handover.service','research-system-handover.socket',
         'research-system-handover-controller.service')
PROPERTIES = ('LoadState', 'ActiveState', 'SubState', 'User', 'Result', 'ExecMainStatus',
              'MemoryMax', 'CPUQuotaPerSecUSec', 'NoNewPrivileges', 'ProtectSystem',
              'Group', 'PrivateNetwork', 'ProtectHome', 'TasksMax')


def current_process():
    """Observe this collector's identity/resources; no logs or other processes."""
    result={'uid':os.getuid(),'observed_utc':datetime.now(timezone.utc).isoformat(),
            'no_new_privileges':None,'cgroup':{}}
    try:
        fields=dict(line.split(':',1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
        result['no_new_privileges']=fields.get('NoNewPrivs','').strip() or None
        groups=Path('/proc/self/cgroup').read_text().splitlines()
        unified=next(line.split(':',2)[2] for line in groups if line.startswith('0::'))
        group=(Path('/sys/fs/cgroup')/unified.lstrip('/')).resolve()
        if not group.is_relative_to('/sys/fs/cgroup'):
            result['observation_incomplete']=True
            return result
        for name in ('cpu.max','memory.max','pids.max'):
            path=group/name
            result['cgroup'][name]=path.read_text().strip() if path.is_file() else None
    except (OSError,StopIteration):result['observation_incomplete']=True
    scan('current-process.json',json.dumps(result).encode())
    return result


def validate(request):
    if not isinstance(request, dict) or set(request) != {'kind', 'purpose', 'affected_task'}:
        raise ValueError('EVIDENCE_REQUEST_SCHEMA')
    if request['kind'] not in SOURCES:
        raise ValueError('EVIDENCE_KIND_NOT_ALLOWED')
    for key in ('purpose', 'affected_task'):
        value = request[key]
        if not isinstance(value, str) or not value.strip() or len(value) > 500:
            raise ValueError('EVIDENCE_REQUEST_TEXT')
    scan('request.json', json.dumps(request, sort_keys=True).encode())
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
                        'status': ('SOURCE_CODE_NOT_EXECUTION_PROOF' if request['kind']=='handover_implementation' else 'HISTORICAL_DOCUMENT_NOT_CURRENT_EXECUTION_PROOF'), 'content': raw})
    result = {'version': 1, 'request_id': identity, 'request': request,
              'collected_utc': datetime.now(timezone.utc).isoformat(), 'records': records,
              'current_observations': [],
              'collector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'limitations': ['No patient files, private logs, credentials or arbitrary commands are read.',
                             'No new execution, restart, restore or phone delivery is performed.',
                             'Missing or historical evidence does not establish current success.']}
    if hosted and request['kind'] in ('service_runtime', 'resource_limits'):
        for unit in UNITS:
            command = ['systemctl', 'show', unit, '--property='+','.join(PROPERTIES)]
            try:
                proc = subprocess.run(command, capture_output=True, text=True, timeout=15)
            except (subprocess.TimeoutExpired, OSError):
                result['current_observations'].append({'unit': unit, 'status': 'COLLECTION_FAILED', 'execution_proven': False})
                continue
            # Never return raw stderr or unexpected properties from a service definition.
            fields = {}
            for line in proc.stdout.splitlines():
                key, sep, value = line.partition('=')
                if sep and key in PROPERTIES: fields[key] = value
            status='CURRENT_CONFIGURATION_ONLY'
            if fields.get('LoadState')=='not-found':
                status='UNIT_NOT_FOUND';fields={'LoadState':'not-found'}
            elif proc.returncode or not fields.get('LoadState'):status='COLLECTION_FAILED'
            scan('service-properties.json', json.dumps(fields).encode())
            result['current_observations'].append({'unit': unit, 'returncode': proc.returncode,
                'properties': fields, 'status': status,
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
