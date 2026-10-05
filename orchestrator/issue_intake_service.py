"""Protected independent Issue6 bookkeeping service, never a research worker.

Root holds the existing notification App key and validates comments. Proposal
recording uses a fixed controller-UID subprocess; controls use the existing
revisioned coordinator transport. No model or Actions dispatch route exists here.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import sqlite3
import stat
import subprocess

from orchestrator import issue_intake as intake
from orchestrator.handover_runtime import configuration, controller_command, operator_request
from orchestrator.operations_report import immutable
from orchestrator.phone_notifications import config_checked, protected_read, session, jwt, digest
from orchestrator.remote_supervisor import checked_source


ATTESTATIONS = Path('/etc/research-system/live-research/controls/issue-intake-attestations')


LIMITATION = ('Manual Actions dispatch is waiting: the public workflows do not currently use shared '
              'admission accounting. Do not dispatch until a separately verified coordination path '
              'can count this run. Linux-only research may continue within its recorded authority.')


def checked_configuration(path):
    c = configuration(path)
    if set(c) != {'source', 'controller_config', 'notification_config', 'state', 'legacy_outbox'}:
        raise ValueError('ISSUE_INTAKE_CONFIGURATION_REQUIRED')
    for key in ('controller_config', 'notification_config', 'state', 'legacy_outbox'):
        if not isinstance(c[key], str) or not Path(c[key]).is_absolute():
            raise ValueError('ISSUE_INTAKE_ABSOLUTE_PATH_REQUIRED')
    controller = configuration(c['controller_config'])
    if c['source'] != controller['source']:
        raise ValueError('ISSUE_INTAKE_SOURCE_CHANGED')
    checked_source(controller['source_root'], c['source'])
    if pwd.getpwuid(controller['controller_uid']).pw_name != 'research-controller':
        raise ValueError('ISSUE_INTAKE_CONTROLLER_IDENTITY')
    notification = config_checked(json.loads(protected_read(c['notification_config'])))
    if (notification['operator_id'] != intake.OPERATOR or notification['bot_id'] != intake.BOT or
            notification['mode'] != 'NOTIFICATION_ONLY'):
        raise ValueError('ISSUE_INTAKE_AUTHENTICATED_ACTORS_REQUIRED')
    return c, controller, notification


class Operations:
    def __init__(self, config, controller):
        self.config, self.controller = config, controller

    def state(self):
        return controller_command(self.controller, 'control-status', self.config['controller_config'])

    def prepare(self, action, original, received):
        if received['source'] != self.controller['source']:
            raise ValueError('HISTORICAL_INTAKE_REQUIRES_SOURCE_RECONCILIATION')
        plan = {'action': action, 'version': received['comment_version'], 'source': received['source']}
        if action in ('pause', 'resume'):
            command = intake.CONTROL.fullmatch(original['body'].strip())
            if command is None or command.group(1) != action or command.group(2) is None:
                raise ValueError('EXPLICIT_OBSERVED_CONTROL_REVISION_REQUIRED')
            observed = self.state()
            plan['expected_revision'] = int(command.group(2))
            plan['observed_revision'] = observed['revision']
            plan['already_effective'] = bool(observed['paused']) == (action == 'pause')
            plan['observed_paused'] = bool(observed['paused'])
        return plan

    def apply(self, plan, original, received):
        if (plan['version'] != received['comment_version'] or plan['source'] != received['source'] or
                plan['source'] != self.controller['source']):
            raise ValueError('INTAKE_OPERATION_BINDING_CHANGED')
        action = plan['action']
        if action == 'status':
            state = self.state()
            return {'status': 'STATUS', 'revision': state['revision'], 'paused': bool(state['paused']),
                    'task_count': len(state['tasks']), 'source': self.controller['source']}
        if action in ('pause', 'resume'):
            if plan['expected_revision'] != plan['observed_revision']:
                return {'status': 'BLOCKED', 'reason': 'CONTROL_REVISION_MISMATCH_USE_STATUS'}
            if plan['already_effective']:
                current = self.state()
                if current['revision'] != plan['expected_revision'] or bool(current['paused']) != plan['observed_paused']:
                    return {'status': 'BLOCKED', 'reason': 'CONTROL_STATE_CHANGED_USE_NEW_COMMENT'}
                return {'status': 'CONTROL_COMPLETE', 'action': action,
                        'revision': plan['expected_revision'], 'paused': plan['observed_paused'],
                        'effect': 'ALREADY_EFFECTIVE_AT_RECORDED_OBSERVATION'}
            request = operator_request(self.controller, action, plan['expected_revision'],
                                       plan['version'], self.config['controller_config'])
            controller_command(self.controller, 'controls', self.config['controller_config'])
            state = self.state()
            receipt = next((item for item in state['controls'] if item['request'] == request['request']), None)
            if not receipt or receipt['status'] != 'APPLIED':
                return {'status': 'BLOCKED', 'reason': 'CONTROL_STALE_OR_PENDING_INSPECT_STATUS'}
            return {'status': 'CONTROL_COMPLETE', 'action': action, 'revision': receipt['revision'],
                    'paused': action == 'pause', 'control_receipt': receipt,
                    'current_revision': state['revision'], 'current_paused': bool(state['paused'])}
        if action == 'HISTORICAL_ACK':
            path = Path(self.config['legacy_outbox'])
            if path.is_symlink() or not path.is_file():
                raise ValueError('ORIGINAL_NOTIFICATION_REQUIRED')
            with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
                rows = db.execute('SELECT packet FROM notifications WHERE issue=6').fetchall()
            matches = []
            for (raw,) in rows:
                packet = json.loads(raw)
                expected = 'ACK ' + packet['id'] + ' ' + packet['nonce'] + ' ' + digest(packet)
                if original['body'].strip() == expected:
                    matches.append(digest(packet))
            if len(matches) != 1 or original['created_at'] != original['updated_at']:
                return {'status': 'BLOCKED', 'reason': 'HISTORICAL_ACK_BINDING_UNVERIFIED'}
            return {'status': 'HISTORICAL_ACKNOWLEDGED', 'notification_sha256': matches[0],
                    'old_notification_or_ack_state_modified': False}
        if action in ('EDITED_CONTROL', 'UNSUPPORTED_CONTROL_OR_QUOTE',
                      'HISTORICAL_CONTROL', 'CONTROL_REVISION_REQUIRED'):
            return {'status': 'BLOCKED', 'reason': action + '_USE_NEW_UNQUOTED_COMMENT'}
        if action != 'PROPOSAL':
            raise ValueError('INTAKE_ACTION_NOT_INSTALLED')
        # The operator's prose is a proposal, never arbitrary shell or authority.
        reference = attest_proposal(self.controller, original, received)
        command = ['/usr/sbin/runuser', '-u', 'research-controller', '--', 'env', '-i',
                   'PATH=/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE=1',
                   'PYTHONPATH=' + self.controller['source_root'], '/usr/bin/python3', '-B',
                   '-m', 'orchestrator.issue_intake_service', '--config',
                   self.config['controller_config'], 'record-proposal']
        result = subprocess.run(command, input=intake.encoded(reference), capture_output=True, timeout=20)
        if result.returncode or len(result.stdout) > 10000:
            # Preserve the failure and do not echo a possibly sensitive payload.
            raise ValueError('INTAKE_PROPOSAL_TRANSPORT_PENDING_RECONCILE')
        return json.loads(result.stdout)


def attestation_directory(controller):
    """One installed root-held inbox; group traversal grants no write authority."""
    for path in (ATTESTATIONS, *ATTESTATIONS.parents):
        try:
            info = path.lstat()
        except FileNotFoundError:
            raise ValueError('ROOT_INTAKE_ATTESTATION_DIRECTORY_REQUIRED') from None
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('ROOT_INTAKE_ATTESTATION_DIRECTORY_REQUIRED')
        if path == ATTESTATIONS and (info.st_gid != controller['controller_gid']
                                     or stat.S_IMODE(info.st_mode) != 0o750):
            raise ValueError('ROOT_INTAKE_ATTESTATION_ACCESS_REQUIRED')
    return ATTESTATIONS


def validated_payload(controller, payload):
    if not isinstance(payload, dict) or set(payload) != {'original', 'received'}:
        raise ValueError('ATTESTED_COMMENT_PAYLOAD_REQUIRED')
    original = intake.checked_comment(payload['original']); received = payload['received']
    if (original['user']['id'] != intake.OPERATOR or received['source'] != controller['source'] or
            received['actor']['identity'] != 'github-user:' + str(intake.OPERATOR) or
            received['comment_version'] != intake.digest({'repository': intake.REPO, 'issue': 6,
                'id': original['id'], 'updated_at': original['updated_at'], 'body': original['body']})):
        raise ValueError('ATTESTED_COMMENT_BINDING_CHANGED')
    return original, received


def file_identity(info):
    # A read may legitimately update atime; identity and modification may not change.
    return (info.st_dev, info.st_ino, info.st_uid, info.st_gid, info.st_mode,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def attestation_read(controller, reference):
    if (not isinstance(reference, dict) or set(reference) != {'version', 'attestation_sha256'} or
            any(not isinstance(reference[k], str) or not re.fullmatch('[0-9a-f]{64}', reference[k])
                for k in reference)):
        raise ValueError('ROOT_ATTESTED_INTAKE_REFERENCE_REQUIRED')
    path = attestation_directory(controller)/(reference['version']+'.json')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_gid != controller['controller_gid']
                or stat.S_IMODE(info.st_mode) != 0o640 or info.st_size > 150000):
            raise ValueError('ROOT_ATTESTED_INTAKE_FILE_REQUIRED')
        raw = stream.read(150001)
        if len(raw) > 150000 or file_identity(os.fstat(stream.fileno())) != file_identity(info):
            raise ValueError('ROOT_ATTESTED_INTAKE_CHANGED')
    if hashlib.sha256(raw).hexdigest() != reference['attestation_sha256']:
        raise ValueError('ROOT_ATTESTED_INTAKE_CHANGED')
    value = json.loads(raw)
    if (set(value) != {'schema', 'source', 'comment_version', 'payload_sha256', 'payload'} or
            value['schema'] != 'issue6-root-attestation/v1' or value['source'] != controller['source'] or
            value['comment_version'] != reference['version'] or
            value['payload_sha256'] != hashlib.sha256(intake.encoded(value['payload'])).hexdigest()):
        raise ValueError('ROOT_ATTESTED_COMMENT_BINDING_CHANGED')
    original, received = validated_payload(controller, value['payload'])
    if received['comment_version'] != reference['version']:
        raise ValueError('ROOT_ATTESTED_COMMENT_BINDING_CHANGED')
    return original, received


def attest_proposal(controller, original, received):
    """The root poller records the fetched version before its fixed UID997 child."""
    if os.getuid() != 0:
        raise ValueError('ROOT_INTAKE_ATTESTOR_REQUIRED')
    payload = {'original': original, 'received': received}
    validated_payload(controller, payload)
    folder = attestation_directory(controller); version = received['comment_version']
    value = {'schema': 'issue6-root-attestation/v1', 'source': controller['source'],
             'comment_version': version, 'payload_sha256': hashlib.sha256(intake.encoded(payload)).hexdigest(),
             'payload': payload}
    raw = intake.encoded(value)
    if len(raw) > 150000:
        raise ValueError('INTAKE_ATTESTATION_LIMIT')
    reference = {'version': version, 'attestation_sha256': hashlib.sha256(raw).hexdigest()}
    path = folder/(version+'.json')
    if not path.exists():
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o640)
        with os.fdopen(fd, 'wb') as stream:
            os.fchmod(stream.fileno(), 0o640); os.fchown(stream.fileno(), 0, controller['controller_gid'])
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        fd = os.open(folder, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try: os.fsync(fd)
        finally: os.close(fd)
    # An identical retry reuses its original proof; a changed source/body refuses.
    attestation_read(controller, reference)
    return reference


def record_proposal(controller, reference):
    # The readable root-held record is the proof; parent PID/UID is not authority.
    if os.getuid() != controller['controller_uid']:
        raise ValueError('ROOT_ATTESTED_INTAKE_TRANSPORT_REQUIRED')
    original, received = attestation_read(controller, reference)
    checked_source(controller['source_root'], controller['source'])
    from orchestrator.change_requests import submit
    actor = {**received['actor'], 'previous_comment_version': received['previous_version']}
    try:
        request = submit(controller['change_request_store'], controller['source_root'],
                         'charter:isles24-prediction', original['body'], actor,
                         source=controller['source'], key=received['comment_version'][:40],
                         scope_limits=['Request only; no scientific authorization, execution, publication, spending, reset or main merge.',
                                       'Quoted or attached evidence is not independently an operator instruction.',
                                       LIMITATION])
    except ValueError:
        return {'status': 'BLOCKED', 'reason': 'REQUEST_CONTENT_OR_BINDING_NOT_PERMITTED'}
    return {'status': 'RECORDED', 'request_id': request['identity'],
            'manual_actions_status': 'WAITING_FOR_VERIFIED_ACCOUNTING', 'model_calls': 0}


def poll(store, operations, call):
    observed = intake.comments(lambda method, path: store.api(call, method, path))
    for comment in observed:
        version = store.receive(comment)
        if version:
            try:
                store.process(version, operations)
            except (ValueError, KeyError, TypeError, OSError, sqlite3.Error, subprocess.TimeoutExpired):
                row = store.db.execute('SELECT attempts FROM versions WHERE version=?', (version,)).fetchone()
                status = 'BLOCKED' if row['attempts'] >= intake.MAX_ATTEMPTS else 'RETRY'
                store.db.execute('UPDATE versions SET status=? WHERE version=?', (status, version))
                failure = {'status': status, 'reason': 'INTAKE_OPERATION_RECONCILIATION_REQUIRED'}
                immutable(store.root / version / ('failure-' + str(row['attempts']) + '.json'), intake.encoded(failure))
                if status == 'BLOCKED': store.queue_reply(version, failure)
    # No network operation is performed under the coordinator admission/branch lock.
    for row in store.db.execute("SELECT version FROM replies WHERE state != 'SENT' ORDER BY rowid").fetchall():
        try:
            store.deliver(row['version'], call, observed)
        except (ValueError, KeyError, TypeError, OSError):
            # Original UNCERTAIN intent is durable. Later polling can reconcile it;
            # no second POST follows a transport exception.
            continue
    return store.status()


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('operation', choices=['poll', 'status', 'record-proposal'])
    args = parser.parse_args()
    if args.operation == 'record-proposal':
        import sys
        raw = sys.stdin.buffer.read(150001)
        if len(raw) > 150000: raise ValueError('INTAKE_ATTESTATION_LIMIT')
        result = record_proposal(configuration(args.config), json.loads(raw))
    else:
        if os.getuid() != 0: raise ValueError('PROTECTED_INTAKE_SERVICE_REQUIRED')
        config, controller, notification = checked_configuration(args.config)
        if args.operation == 'poll':
            from orchestrator.deployment_review import verify_installed
            verify_installed(controller['source_root'], controller['source'],
                             config_path=args.config, config=config)
        store = intake.Intake(config['state'], config['source'])
        # Separate from model/branch/admission locks; timer overlap exits without
        # another delivery. Ordinary API latency cannot block direct phone controls.
        with (store.root / 'poll.lock').open('a') as stream:
            try: fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                print(json.dumps({'status': 'INTAKE_ALREADY_RUNNING'})); return
            if args.operation == 'status': result = store.status()
            else:
                from orchestrator.phone_notifications import api
                token, identity = session(notification, jwt(notification),
                    call=lambda method, path, token, body=None: store.api(
                        lambda m, p, b: api(m, p, token, b), method, path, body))
                immutable(store.root / 'verified-identities.json', intake.encoded(identity))
                result = poll(store, Operations(config, controller),
                              lambda method, path, body=None: api(method, path, token, body))
        store.db.close()
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
