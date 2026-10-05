"""Fixed GitHub-to-GitHub model-secret relocation; never exports plaintext.

Runner commands only prepare ciphertext. The separate operator command uses
existing gh authentication to stage that ciphertext after verifying its origin.
It never removes repository originals or starts models, science, or activation.
"""
import argparse
import base64
import fcntl
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

from orchestrator.operations_report import immutable, private_root
from orchestrator.public_export import text as public_text

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'Moroseui/concept-research-scout'
REPOSITORY_ID = 1323461276
ENVIRONMENT = 'research-models'
ENVIRONMENT_ID = 21537367870
KEY_ID = '3380204578043523366'
KEY_SHA256 = 'a9e57336e84c42fecf7b07ce7a2c108d10f22eac8ede2a7fa3fbfce112c834d3'
NAMES = ('CLAUDE_CODE_OAUTH_TOKEN', 'CODEX_AUTH_JSON', 'OPENAI_API_KEY')
WORKFLOW = '.github/workflows/model-secret-relocation.yml'
REQUEST = 'model-secret-relocation-20260910-v1'
SCHEMA = 'github-model-secret-relocation/v1'
CONFIG = 'configs/model-secret-relocation-target.json'
GRANT = 'docs/operations/PROTECTED_HANDOVER_APPROVED_20260908.json'
GRANT_SHA256 = '0be99c7b0b4e5e9eb16d9ebf8b44e369f6ef07233b903173fcd5355536127d1a'
MAX_SECRET = 48 * 1024
MAX_MANIFEST = 220000


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def regular(path, limit=MAX_MANIFEST):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file() or path.stat().st_size > limit:
        raise ValueError('RELOCATION_REGULAR_BOUNDED_FILE_REQUIRED')
    return path.read_bytes()


def target(root=ROOT):
    value = json.loads(regular(Path(root) / CONFIG))
    if (set(value) != {'repository', 'repository_id', 'environment', 'environment_id',
                      'key_id', 'public_key', 'public_key_sha256', 'secret_names'} or
            value['repository'] != REPOSITORY or value['repository_id'] != REPOSITORY_ID or
            value['environment'] != ENVIRONMENT or value['environment_id'] != ENVIRONMENT_ID or
            value['key_id'] != KEY_ID or value['public_key_sha256'] != KEY_SHA256 or
            sha(value['public_key'].encode()) != KEY_SHA256 or value['secret_names'] != list(NAMES) or
            len(base64.b64decode(value['public_key'], validate=True)) != 32 or
            sha(regular(Path(root) / GRANT)) != GRANT_SHA256):
        raise ValueError('RELOCATION_FIXED_RECIPIENT_OR_GRANT_CHANGED')
    return value


def pin(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{40}', value):
        raise ValueError('RELOCATION_EXACT_SOURCE_REQUIRED')
    return value


def run_identity(value):
    required = {'source', 'run_id', 'attempt', 'actor', 'workflow_ref', 'request'}
    if (not isinstance(value, dict) or set(value) != required or value['attempt'] != '1' or
            not re.fullmatch('[1-9][0-9]{0,19}', str(value['run_id'])) or
            not re.fullmatch(r'[A-Za-z0-9_.\[\]-]{1,100}', str(value['actor'])) or
            value['workflow_ref'] != REPOSITORY + '/' + WORKFLOW + '@refs/heads/main' or
            value['request'] != REQUEST):
        raise ValueError('RELOCATION_ORIGINAL_MAIN_RUN_REQUIRED')
    pin(value['source'])
    return value


def hosted_identity(source):
    expected = {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': REPOSITORY,
                'GITHUB_REPOSITORY_ID': str(REPOSITORY_ID), 'GITHUB_REF': 'refs/heads/main',
                'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GITHUB_SHA': pin(source)}
    if any(os.environ.get(k) != v for k, v in expected.items()):
        raise ValueError('RELOCATION_REVIEWED_MAIN_CONTEXT_REQUIRED')
    return run_identity({'source': source, 'run_id': os.environ.get('GITHUB_RUN_ID'),
        'attempt': os.environ.get('GITHUB_RUN_ATTEMPT'), 'actor': os.environ.get('GITHUB_ACTOR'),
        'workflow_ref': os.environ.get('GITHUB_WORKFLOW_REF'), 'request': REQUEST})


def api(endpoint, *, method='GET', payload=None, binary=False):
    """Existing gh credential holder; values and stderr never enter public logs."""
    command = ['gh', 'api', '--hostname', 'github.com', '--method', method, endpoint]
    if payload is not None:
        command += ['--input', '-']
    env = {k: v for k, v in os.environ.items() if not k.startswith('SOURCE_') and k not in NAMES}
    result = subprocess.run(command, input=None if payload is None else encoded(payload),
                            capture_output=True, timeout=45, env=env)
    if result.returncode or len(result.stdout) > 1000000:
        raise ValueError('RELOCATION_GITHUB_OPERATION_FAILED')
    return result.stdout if binary else json.loads(result.stdout) if result.stdout.strip() else None


def endpoint(suffix):
    return 'repos/' + REPOSITORY + '/' + suffix


def remote_target(*, require_empty=False, read_key=True, root=ROOT):
    bound = target(root)
    repo = api(endpoint(''))
    env = api(endpoint('environments/' + ENVIRONMENT))
    rules = api(endpoint('environments/' + ENVIRONMENT + '/deployment-branch-policies'))
    # GITHUB_TOKEN actions:read can inspect environment/branch policy but lacks
    # the separate Environments permission for the key endpoint. Encryption uses
    # the exact reviewed public key; the owner verifies its freshness before PUT.
    key = (api(endpoint('environments/' + ENVIRONMENT + '/secrets/public-key'))
           if read_key else {'key_id': KEY_ID, 'key': bound['public_key']})
    if (repo.get('id') != REPOSITORY_ID or repo.get('default_branch') != 'main' or
            env.get('id') != ENVIRONMENT_ID or env.get('name') != ENVIRONMENT or
            env.get('deployment_branch_policy') != {'protected_branches': False, 'custom_branch_policies': True} or
            rules.get('total_count') != 1 or
            [(p.get('name'), p.get('type')) for p in rules.get('branch_policies', [])] != [('main', 'branch')] or
            key != {'key_id': KEY_ID, 'key': bound['public_key']}):
        raise ValueError('RELOCATION_REMOTE_RECIPIENT_OR_POLICY_CHANGED')
    if require_empty:
        if not read_key:
            raise ValueError('RELOCATION_OWNER_KEY_VALIDATION_REQUIRED')
        secrets = api(endpoint('environments/' + ENVIRONMENT + '/secrets'))
        originals = api(endpoint('actions/secrets'))
        if secrets.get('total_count') != 0 or secrets.get('secrets') != []:
            raise ValueError('RELOCATION_EXISTING_ENVIRONMENT_VALUES_RECONCILE')
        if originals.get('total_count') != 3 or sorted(s.get('name') for s in originals.get('secrets', [])) != list(NAMES):
            raise ValueError('RELOCATION_ORIGINAL_SECRET_NAMES_CHANGED')
    return bound


def source_review(source, root=ROOT):
    from orchestrator.actions_runner import reviewed
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if actual != pin(source) or subprocess.check_output(['git', 'status', '--porcelain'], cwd=root):
        raise ValueError('RELOCATION_CLEAN_BOUND_SOURCE_REQUIRED')
    return reviewed(root)


def preflight(source, output, root=ROOT):
    identity = hosted_identity(source)
    review = source_review(source, root)
    recipient = remote_target(root=root, read_key=False)
    runs = api(endpoint('actions/workflows/model-secret-relocation.yml/runs?event=workflow_dispatch&per_page=100'))
    if runs.get('total_count', 101) > 100 or any(str(r.get('id')) != identity['run_id'] and
            r.get('head_sha') == source for r in runs.get('workflow_runs', [])):
        raise ValueError('RELOCATION_EXISTING_RUN_RECONCILE_BEFORE_RETRY')
    value = {'schema': SCHEMA + '/preflight', 'run': identity, 'recipient': recipient,
             'reviewed_source': review, 'checked_at_utc': datetime.now(timezone.utc).isoformat()}
    output = Path(output)
    private_root(output.parent)
    immutable(output, encoded(value) + b'\n')
    return value


def validate(value, *, source, run_id, root=ROOT):
    """Closed ciphertext schema, plus existing public-text checks, before upload.

    Shape alone cannot prove encryption. Staging additionally requires the exact
    original artifact from the reviewed workflow, and seal() uses only SealedBox.
    """
    keys = {'schema', 'kind', 'recipient', 'run', 'reviewed_source', 'preflight_sha256', 'secrets'}
    if not isinstance(value, dict) or set(value) != keys or value['schema'] != SCHEMA or value['kind'] != 'GITHUB_ENVIRONMENT_SEALED_BOX':
        raise ValueError('RELOCATION_CIPHERTEXT_SCHEMA_REQUIRED')
    if value['recipient'] != target(root):
        raise ValueError('RELOCATION_RECIPIENT_MISMATCH')
    identity = run_identity(value['run'])
    if identity['source'] != pin(source) or identity['run_id'] != str(run_id):
        raise ValueError('RELOCATION_SOURCE_OR_RUN_MISMATCH')
    pin(value['reviewed_source'])
    if not re.fullmatch('[0-9a-f]{64}', str(value['preflight_sha256'])) or not isinstance(value['secrets'], dict) or set(value['secrets']) != set(NAMES):
        raise ValueError('RELOCATION_SECRET_NAMES_OR_BINDING_CHANGED')
    for item in value['secrets'].values():
        if not isinstance(item, dict) or set(item) != {'encrypted_value', 'ciphertext_sha256'}:
            raise ValueError('RELOCATION_CIPHERTEXT_FIELDS_REQUIRED')
        try:
            cipher = base64.b64decode(item['encrypted_value'], validate=True)
        except (ValueError, TypeError):
            raise ValueError('RELOCATION_CIPHERTEXT_ENCODING_REQUIRED') from None
        if not 68 <= len(cipher) <= MAX_SECRET + 48 or sha(cipher) != item['ciphertext_sha256']:
            raise ValueError('RELOCATION_CIPHERTEXT_SIZE_OR_HASH_CHANGED')
        # Reject ordinary text/base64-wrapped plaintext rather than treating an
        # arbitrary string as an encrypted administrative export.
        try:
            cipher.decode('utf-8')
        except UnicodeDecodeError:
            pass
        else:
            raise ValueError('RELOCATION_PLAINTEXT_NOT_PERMITTED')
    public_text(encoded(value).decode(), limit=MAX_MANIFEST)
    return value


def manifest(raw, *, source, run_id, root=ROOT):
    if not isinstance(raw, bytes) or len(raw) > MAX_MANIFEST:
        raise ValueError('RELOCATION_MANIFEST_SIZE_REQUIRED')
    value = json.loads(raw)
    if raw != encoded(value) + b'\n':
        raise ValueError('RELOCATION_CANONICAL_MANIFEST_REQUIRED')
    return validate(value, source=source, run_id=run_id, root=root)


def seal(preflight_path, output, *, source, root=ROOT):
    from nacl import encoding, public
    identity = hosted_identity(source)
    review = source_review(source, root)
    raw = regular(preflight_path)
    before = json.loads(raw)
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(before['checked_at_utc'])).total_seconds()
    if (set(before) != {'schema', 'run', 'recipient', 'reviewed_source', 'checked_at_utc'} or
            before['schema'] != SCHEMA + '/preflight' or before['run'] != identity or
            before['recipient'] != target(root) or before['reviewed_source'] != review or not 0 <= age <= 900):
        raise ValueError('RELOCATION_FRESH_PREFLIGHT_REQUIRED')
    values = {name: os.environ.get('SOURCE_' + name) for name in NAMES}
    if any(not isinstance(v, str) or not 20 <= len(v.encode()) <= MAX_SECRET for v in values.values()):
        raise ValueError('RELOCATION_REQUIRED_SOURCE_SECRET_MISSING_OR_SIZE')
    box = public.SealedBox(public.PublicKey(before['recipient']['public_key'].encode(), encoding.Base64Encoder()))
    sealed = {}
    for name, plaintext in values.items():
        cipher = box.encrypt(plaintext.encode())
        sealed[name] = {'encrypted_value': base64.b64encode(cipher).decode(), 'ciphertext_sha256': sha(cipher)}
    value = {'schema': SCHEMA, 'kind': 'GITHUB_ENVIRONMENT_SEALED_BOX', 'recipient': before['recipient'],
             'run': identity, 'reviewed_source': review, 'preflight_sha256': sha(raw), 'secrets': sealed}
    validate(value, source=source, run_id=identity['run_id'], root=root)
    payload = encoded(value) + b'\n'
    if any(v.encode() in payload or base64.b64encode(v.encode()) in payload for v in values.values()):
        raise ValueError('RELOCATION_PLAINTEXT_NOT_PERMITTED')
    output = Path(output)
    private_root(output.parent)
    immutable(output, payload)
    return {'status': 'CIPHERTEXT_PREPARED_NOT_STAGED', 'source': source, 'run_id': identity['run_id'],
            'manifest_sha256': sha(payload), 'secret_names': list(NAMES)}


def original_artifact(run_id, source, root=ROOT):
    if not re.fullmatch('[1-9][0-9]{0,19}', str(run_id)):
        raise ValueError('RELOCATION_RUN_ID_REQUIRED')
    pin(source)
    run = api(endpoint('actions/runs/' + str(run_id)))
    if (run.get('repository', {}).get('id') != REPOSITORY_ID or run.get('head_sha') != source or
            run.get('head_branch') != 'main' or run.get('event') != 'workflow_dispatch' or
            run.get('path') != WORKFLOW or run.get('run_attempt') != 1 or
            run.get('status') != 'completed' or run.get('conclusion') != 'success'):
        raise ValueError('RELOCATION_ORIGINAL_SUCCESSFUL_WORKFLOW_REQUIRED')
    listing = api(endpoint('actions/runs/' + str(run_id) + '/artifacts?per_page=100'))
    matches = [a for a in listing.get('artifacts', []) if a.get('name') == REQUEST]
    if listing.get('total_count', 101) > 100 or len(matches) != 1:
        raise ValueError('RELOCATION_ONE_ORIGINAL_ARTIFACT_REQUIRED')
    artifact = matches[0]
    bound = artifact.get('workflow_run', {})
    if (artifact.get('expired') is not False or bound.get('id') != int(run_id) or bound.get('head_sha') != source or
            not isinstance(artifact.get('id'), int) or not 0 < artifact.get('size_in_bytes', 0) <= MAX_MANIFEST + 10000):
        raise ValueError('RELOCATION_ARTIFACT_IDENTITY_OR_SIZE_CHANGED')
    archive = api(endpoint('actions/artifacts/' + str(artifact['id']) + '/zip'), binary=True)
    if len(archive) > MAX_MANIFEST + 10000:
        raise ValueError('RELOCATION_ARTIFACT_SIZE_CHANGED')
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        infos = bundle.infolist()
        if len(infos) != 1 or infos[0].filename != 'manifest.json' or infos[0].file_size > MAX_MANIFEST:
            raise ValueError('RELOCATION_ONE_MANIFEST_REQUIRED')
        raw = bundle.read('manifest.json')
    value = manifest(raw, source=source, run_id=run_id, root=root)
    if value['run']['actor'] != run.get('actor', {}).get('login'):
        raise ValueError('RELOCATION_ACTOR_CHANGED')
    return raw, {'run_id': str(run_id), 'source': source, 'artifact_id': artifact['id'],
                 'archive_sha256': sha(archive), 'manifest_sha256': sha(raw)}


def stage(run_id, source, store, root=ROOT):
    """Operator-only existing-gh route. No credential value is available here."""
    store = private_root(store)
    lock = store / '.stage.lock'
    if lock.is_symlink():
        raise ValueError('RELOCATION_REGULAR_BOUNDED_FILE_REQUIRED')
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'r+') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        return _stage_locked(run_id, source, store, root)


def _stage_locked(run_id, source, store, root=ROOT):
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        raise ValueError('RELOCATION_OWNER_ROUTE_OUTSIDE_ACTIONS_REQUIRED')
    if not re.fullmatch('[1-9][0-9]{0,19}', str(run_id)):
        raise ValueError('RELOCATION_RUN_ID_REQUIRED')
    source_review(source, root)
    if api(endpoint('git/ref/heads/main')).get('object', {}).get('sha') != source:
        raise ValueError('RELOCATION_CURRENT_REVIEWED_MAIN_REQUIRED')
    folder = private_root(private_root(store) / str(run_id))
    if (folder / 'staged.json').exists():
        saved = json.loads(regular(folder / 'staged.json'))
        raw = regular(folder / 'manifest.json')
        manifest(raw, source=source, run_id=run_id, root=root)
        if saved['source'] != source or saved['run_id'] != str(run_id) or saved['manifest_sha256'] != sha(raw):
            raise ValueError('RELOCATION_SAVED_IDENTITY_CHANGED')
        return {**saved, 'status': 'ALREADY_STAGED_RECHECK_CANARIES', 'puts_this_call': 0}
    if list(folder.glob('intent-*.json')):
        raise ValueError('RELOCATION_PARTIAL_STAGING_RECONCILE_ORIGINAL_INTENTS')
    raw, original = original_artifact(run_id, source, root)
    remote_target(require_empty=True, root=root)
    immutable(folder / 'manifest.json', raw)
    immutable(folder / 'original-artifact.json', encoded(original) + b'\n')
    value = json.loads(raw)
    for name in NAMES:
        payload = {'encrypted_value': value['secrets'][name]['encrypted_value'], 'key_id': KEY_ID}
        intent = {'source': source, 'run_id': str(run_id), 'name': name,
                  'manifest_sha256': original['manifest_sha256'], 'payload_sha256': sha(encoded(payload))}
        immutable(folder / ('intent-' + name + '.json'), encoded(intent) + b'\n')
        api(endpoint('environments/' + ENVIRONMENT + '/secrets/' + name), method='PUT', payload=payload)
        observed = api(endpoint('environments/' + ENVIRONMENT + '/secrets/' + name))
        if observed.get('name') != name:
            raise ValueError('RELOCATION_STAGED_NAME_READBACK_FAILED')
        immutable(folder / ('receipt-' + name + '.json'), encoded({**intent, 'metadata': observed}) + b'\n')
    result = {'status': 'STAGED_CANARIES_AND_ORIGINALS_RETAINED', **original, 'secret_names': list(NAMES),
              'repository_secrets_removed': False, 'puts_this_call': 3}
    immutable(folder / 'staged.json', encoded(result) + b'\n')
    return result


def status(run_id, store):
    if not re.fullmatch('[1-9][0-9]{0,19}', str(run_id)):
        raise ValueError('RELOCATION_RUN_ID_REQUIRED')
    folder = Path(store).absolute() / str(run_id)
    if any(p.is_symlink() for p in (folder, *folder.parents)):
        raise ValueError('RELOCATION_REGULAR_BOUNDED_FILE_REQUIRED')
    if (folder / 'staged.json').exists():
        return json.loads(regular(folder / 'staged.json'))
    intents = [name for name in NAMES if (folder / ('intent-' + name + '.json')).exists()]
    receipts = [name for name in NAMES if (folder / ('receipt-' + name + '.json')).exists()]
    return {'status': 'PARTIAL_OR_UNCERTAIN_STAGING' if intents else 'NOT_STAGED',
            'run_id': str(run_id), 'intended_names': intents, 'acknowledged_names': receipts,
            'next_action': 'Preserve originals and reconcile GitHub metadata before a retry.' if intents else
                           'Use the separately reviewed and authorized stage command after the original workflow completes.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    for name in ('preflight', 'seal', 'validate', 'stage'):
        p = sub.add_parser(name)
        p.add_argument('--source', required=True)
        if name in ('preflight', 'seal'):
            p.add_argument('--output', type=Path, required=True)
        if name == 'seal':
            p.add_argument('--preflight', type=Path, required=True)
        if name == 'validate':
            p.add_argument('--manifest', type=Path, required=True)
        if name in ('stage', 'validate'):
            p.add_argument('--run-id', required=True)
        if name == 'stage':
            p.add_argument('--store', type=Path, required=True)
    view = sub.add_parser('status')
    view.add_argument('--run-id', required=True)
    view.add_argument('--store', type=Path, required=True)
    args = parser.parse_args()
    if args.operation == 'status':
        result = status(args.run_id, args.store)
    elif args.operation == 'preflight':
        preflight(args.source, args.output)
        result = {'status': 'PREFLIGHT_READY_NO_SOURCE_SECRETS_READ'}
    elif args.operation == 'seal':
        result = seal(args.preflight, args.output, source=args.source)
    elif args.operation == 'validate':
        raw = regular(args.manifest)
        manifest(raw, source=args.source, run_id=args.run_id)
        result = {'status': 'CIPHERTEXT_MANIFEST_VALIDATED', 'manifest_sha256': sha(raw)}
    else:
        result = stage(args.run_id, args.source, args.store)
    print(public_text(json.dumps(result, sort_keys=True)))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Never stringify provider/library exceptions while source secrets may
        # be in memory. Only this module's fixed recoverable error identifiers.
        code = str(error) if isinstance(error, ValueError) and re.fullmatch('RELOCATION_[A-Z_]+', str(error)) else 'RELOCATION_FAILED_PRESERVE_AND_RECONCILE'
        print(code, file=sys.stderr)
        raise SystemExit(1)
