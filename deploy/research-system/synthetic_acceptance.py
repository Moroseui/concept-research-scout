#!/usr/bin/env python3
"""Fixed supervised host acceptance; no patient, model dispatch or live admission."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

ROOT = Path('/opt/research-system/current')
BASE = Path('/var/lib/research-system')
STATE = BASE/'research-controller'
JOBS = {'00-colab-blocked', '10-linux-delay', '20-linux-failure', '30-linux-next'}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


class Harness:
    def __init__(self):
        require(os.getuid() == 0, 'BOUNDED_SETUP_ADMIN_REQUIRED')
        os.umask(0o077)
        evidence = BASE/'setup-evidence'
        require(not evidence.is_symlink(), 'EVIDENCE_SYMLINK')
        evidence.mkdir(mode=0o700, exist_ok=True)
        require(evidence.stat().st_uid == 0 and not evidence.stat().st_mode & 0o077,
                'PRIVATE_ROOT_EVIDENCE_REQUIRED')
        self.evidence = evidence/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex)
        self.evidence.mkdir(mode=0o700)
        self.n = 0
        env = Path('/etc/research-system/source.env').read_text().strip()
        require(re.fullmatch(r'SOURCE=[0-9a-f]{40}', env) is not None, 'SOURCE_ENV_INVALID')
        self.source = env.split('=', 1)[1]

    def command(self, args, allowed=(0,), stdin=None):
        self.n += 1
        result = subprocess.run(args, cwd=ROOT, input=stdin, capture_output=True, timeout=30)
        (self.evidence/f'{self.n:03}.stdout').write_bytes(result.stdout)
        (self.evidence/f'{self.n:03}.stderr').write_bytes(result.stderr)
        (self.evidence/f'{self.n:03}.exit.json').write_text(json.dumps({'returncode': result.returncode})+'\n')
        require(result.returncode in allowed, 'ACCEPTANCE_COMMAND_FAILED_'+str(self.n))
        return result

    def controller(self, action, extra=()):
        args = ['runuser', '-u', 'research-controller', '--', '/usr/bin/python3', '-B', '-m',
                'orchestrator.remote_supervisor', action, '--state', str(STATE),
                '--requests', str(BASE/'requests'), '--outputs', str(BASE/'outputs'),
                '--source-root', str(ROOT), '--source', self.source, *extra]
        return json.loads(self.command(args).stdout)

    def start(self):
        status = self.controller('status')
        require(not status['jobs'], 'EXISTING_JOBS_RECONCILE_NO_REDISPATCH')
        fixtures = [('00-colab-blocked', 'synthetic_success', 'colab', '0'),
                    ('10-linux-delay', 'synthetic_success', 'linux', '45'),
                    ('20-linux-failure', 'synthetic_failure', 'linux', '0'),
                    ('30-linux-next', 'synthetic_success', 'linux', '0')]
        for job, kind, backend, delay in fixtures:
            self.controller('submit', ['--job', job, '--kind', kind, '--backend', backend, '--delay', delay])
        self.command(['systemctl', 'start', '--no-block', 'research-system-controller.service'])
        self.command(['systemctl', 'start', '--no-block', 'research-system-worker.service'])
        until = time.monotonic()+3
        started = []
        while time.monotonic() < until:
            started = list((BASE/'outputs').glob('*/started.json'))
            if started:
                break
            time.sleep(.1)
        require(bool(started), 'START_MARKER_NOT_YET_VISIBLE_RECONCILE')
        return {'status': 'REMOTE_SYNTHETIC_STARTED', 'source': self.source,
                'started_markers': len(started), 'requested_delay_seconds': 45,
                'completed': False, 'model_execution': False, 'patient_execution': False}

    def collect(self):
        status = self.controller('status')
        rows = {row['job_id']: row for row in status['jobs']}
        require(set(rows) == JOBS, 'FIXTURE_SET_CHANGED')
        require(all(row['source'] == self.source for row in rows.values()), 'FIXTURE_SOURCE_CHANGED')
        require(rows['10-linux-delay']['status'] == rows['30-linux-next']['status'] == 'COMPLETE', 'LINUX_NOT_COMPLETE')
        require(rows['20-linux-failure']['status'] == 'FAILED' and
                rows['20-linux-failure']['reason'] == 'SYNTHETIC_WORKER_FAILED_OR_TIMED_OUT', 'FAILURE_NOT_RECONCILED')
        require(rows['00-colab-blocked']['status'] == 'BLOCKED', 'COLAB_NOT_BLOCKED')
        require(not status['model_execution'] and not status['patient_execution'], 'FORBIDDEN_EXECUTION')
        # All fixtures are terminal before restarting; never kill active work for a test.
        self.command(['systemctl', 'restart', 'research-system-controller.service'])
        self.command(['systemctl', 'restart', 'research-system-worker.service'])
        status = self.controller('status')
        event_code = "import json,sqlite3; c=sqlite3.connect('/var/lib/research-system/research-controller/jobs.sqlite'); print(json.dumps([json.loads(r[0]) for r in c.execute('SELECT payload FROM events')]))"
        events = json.loads(self.command(['runuser', '-u', 'research-controller', '--', '/usr/bin/python3', '-B', '-c', event_code]).stdout)
        require(len(events) == 3 and len(status['wakes']) == 3 and len({w['id'] for w in status['wakes']}) == 3, 'EVENT_WAKE_DEDUP_FAILED')
        require(sorted(e['status'] for e in events) == ['COMPLETE', 'COMPLETE', 'FAILED'], 'OUTCOME_COUNTS_CHANGED')
        boundaries = {}
        for role, flag, path in [('research-driver', '-w', '/opt/research-system/current/orchestrator/remote_supervisor.py'),
                                 ('research-worker', '-r', '/var/lib/research-system/research-controller'),
                                 ('research-worker', '-r', '/home/research-driver'),
                                 ('research-driver', '-w', '/etc/research-system/source.env')]:
            result = self.command(['runuser', '-u', role, '--', 'test', flag, path], allowed=(0, 1))
            require(result.returncode == 1, 'ROLE_BOUNDARY_FAILED')
            boundaries[role+':'+flag+':'+path] = 'DENIED'
        properties = {}
        for unit, user in [('research-system-controller.service', 'research-controller'), ('research-system-worker.service', 'research-worker')]:
            raw = self.command(['systemctl', 'show', unit, '--property=User,NoNewPrivileges,ProtectSystem,ProtectHome,PrivateNetwork,MemoryMax,CPUQuotaPerSecUSec,TimeoutStartUSec']).stdout.decode()
            values = dict(line.split('=', 1) for line in raw.splitlines() if '=' in line)
            require(values.get('User') == user and values.get('NoNewPrivileges') == 'yes' and
                    values.get('PrivateNetwork') == 'yes' and values.get('ProtectSystem') == 'strict', 'SERVICE_BOUNDARY_FAILED')
            properties[unit] = values
        stamp = uuid.uuid4().hex
        backup_path = STATE/('backup-'+stamp)
        restore_path = STATE/('restore-'+stamp)
        common = ['runuser', '-u', 'research-controller', '--', '/usr/bin/python3', '-B', '-m', 'orchestrator.operations_backup']
        backup = json.loads(self.command(common+['backup', '--state', str(STATE), '--outputs', str(BASE/'outputs'), '--destination', str(backup_path)]).stdout)
        restore = json.loads(self.command(common+['restore', '--source', str(backup_path), '--destination', str(restore_path)]).stdout)
        require(restore.get('restored') is True and restore.get('events') == 3, 'APPLICATION_RESTORE_FAILED')
        # Only a parsed boolean is exposed; original authentication output stays private.
        auth_result = self.command(['runuser', '-u', 'research-reviewer', '--', 'claude', 'auth', 'status', '--json'], allowed=(0, 1))
        auth = json.loads(auth_result.stdout)
        logged_in = auth.get('loggedIn')
        require(isinstance(logged_in, bool), 'CLAUDE_AUTH_STATUS_SCHEMA_UNKNOWN')
        report_code = '''import json,sys
from orchestrator.operations_report import finalize,Queue
d=json.load(sys.stdin)
root='/var/lib/research-system/research-controller/reports'
r=finalize(root,d['source'],d['day'],d['jobs'])
q=Queue(root)
if not d['logged_in'] and r['status']=='QUEUED':
 c=q.claim(r['id'])
 if c:q.unavailable(r['id'],c['attempt_id'],'REMOTE_CLAUDE_AUTH_REQUIRED')
print(json.dumps(q.status(r['id'])))
'''
        report = json.loads(self.command(['runuser', '-u', 'research-controller', '--', '/usr/bin/python3', '-B', '-c', report_code], stdin=json.dumps({'source': self.source, 'day': datetime.now(timezone.utc).date().isoformat(), 'jobs': status['jobs'], 'logged_in': logged_in}).encode()).stdout)
        return {'status': 'SUPERVISED_SYNTHETIC_ACCEPTANCE_COMPLETE', 'source': self.source,
                'jobs': status['jobs'], 'event_count': 3, 'wake_count': 3,
                'completion_events': 2, 'failure_events': 1, 'service_restart_tested': True, 'role_boundaries': boundaries,
                'service_properties': properties, 'application_backup': backup,
                'application_restore': restore, 'report': report,
                'claude_logged_in': logged_in, 'model_execution': False, 'patient_execution': False,
                'astra_continuation_demonstrated': False, 'phone_delivery_demonstrated': False,
                'unattended_24h_demonstrated': False, 'limiter_active': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['start', 'collect'])
    args = p.parse_args()
    harness = Harness()
    sys.path.insert(0, str(ROOT))
    from orchestrator.public_export import text
    result = getattr(harness, args.action)()
    payload = text(json.dumps(result, sort_keys=True))
    (harness.evidence/'receipt.json').write_text(payload+'\n')
    print(payload)


if __name__ == '__main__':
    main()
