"""Bounded routing observations; no model execution or review qualification."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import stat
from urllib.parse import urlsplit

SCHEMA = 'review-routing-context/v1'
MODES = ('CURRENT_DIAGNOSTIC', 'PRE_LAUNCH')
MODEL_ENV = ('ANTHROPIC_MODEL', 'ANTHROPIC_DEFAULT_MODEL',
             'ANTHROPIC_DEFAULT_OPUS_MODEL', 'ANTHROPIC_DEFAULT_FABLE_MODEL',
             'ANTHROPIC_DEFAULT_SONNET_MODEL', 'ANTHROPIC_DEFAULT_HAIKU_MODEL')
BOOL_ENV = ('CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK', 'CLAUDE_CODE_NO_MODEL_FALLBACK',
            'CLAUDE_CODE_USE_BEDROCK', 'CLAUDE_CODE_USE_FOUNDRY',
            'CLAUDE_CODE_USE_ANTHROPIC_AWS', 'CLAUDE_CODE_USE_ANTHROPIC_GOOGLE_CLOUD',
            'CLAUDE_CODE_USE_MANTLE', 'CLAUDE_CODE_USE_VERTEX',
            'CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST', '_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL')
SETTING_KEYS = ('model', 'fallbackModel', 'modelOverrides', 'availableModels',
                'enforceAvailableModels', 'switchModelsOnFlag', 'wslInheritsWindowsSettings')
MODEL = re.compile(r'(?:claude-(?:fable|opus|sonnet|haiku|mythos|[23])-[0-9][0-9a-z.-]*|fable|opus|sonnet|haiku|default|opusplan)(?:\[1m\])?')

def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def _require(value, reason):
    if not value:
        raise ValueError(reason)

def _read(path, maximum, *, executable=False):
    path = Path(path).absolute()
    resolved = path.resolve(strict=True)
    if not executable:
        _require(not any(p.is_symlink() for p in (path, *path.parents)), 'ROUTING_SYMLINK_REFUSED')
    fd = os.open(resolved, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        before = os.fstat(fd)
        _require(stat.S_ISREG(before.st_mode) and before.st_size <= maximum, 'ROUTING_FILE_BOUND')
        chunks = []
        total = 0
        while True:
            chunk = os.read(fd, 1048576)
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            _require(total <= maximum, 'ROUTING_FILE_BOUND')
        raw = b''.join(chunks)
        after = os.fstat(fd)
        keys = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
        current = resolved.stat()
        _require(all(getattr(before, k) == getattr(after, k) == getattr(current, k) for k in keys),
                 'ROUTING_FILE_CHANGED')
        return raw, {'path': str(path), 'resolved_path': str(resolved),
                     'sha256': digest(raw), 'bytes': len(raw), 'device': before.st_dev,
                     'inode': before.st_ino, 'uid': before.st_uid, 'gid': before.st_gid,
                     'mode': oct(stat.S_IMODE(before.st_mode)), 'mtime_ns': before.st_mtime_ns}
    finally:
        os.close(fd)

def _parsed(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, 'ROUTING_DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    def invalid(_):
        raise ValueError('ROUTING_NONFINITE_JSON')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)

def _model(value):
    if isinstance(value, str) and len(value) <= 160 and MODEL.fullmatch(value):
        return {'status': 'OBSERVED', 'value': value}
    return {'status': 'NONSTANDARD_VALUE_NOT_DISCLOSED'}

def named_environment(environment):
    result = {}
    for name in MODEL_ENV + BOOL_ENV + ('HOME', 'CLAUDE_CONFIG_DIR'):
        if name not in environment:
            result[name] = {'status': 'ABSENT'}
            continue
        value = environment[name]
        if name in MODEL_ENV:
            result[name] = _model(value)
        elif name in BOOL_ENV:
            result[name] = ({'status': 'OBSERVED', 'value': value}
                            if isinstance(value, str) and value.lower() in
                            ('', '0', '1', 'true', 'false', 'yes', 'no', 'on', 'off')
                            else {'status': 'NONSTANDARD_VALUE_NOT_DISCLOSED'})
        else:
            result[name] = ({'status': 'OBSERVED', 'value': value}
                            if isinstance(value, str) and value.startswith('/')
                            and len(value) <= 1024 and not any(ord(c) < 32 for c in value)
                            else {'status': 'NONSTANDARD_PATH_NOT_DISCLOSED'})
    value = environment.get('ANTHROPIC_BASE_URL')
    base = {'status': 'ABSENT'}
    if value is not None:
        base = {'status': 'UNPARSED_VALUE_NOT_DISCLOSED'}
        try:
            url = urlsplit(value)
            if url.scheme in ('http', 'https') and url.hostname:
                base = {'status': 'OBSERVED_ORIGIN_ONLY', 'scheme': url.scheme,
                        'hostname': url.hostname, 'port': url.port,
                        'has_userinfo': url.username is not None or url.password is not None,
                        'has_nonroot_path': url.path not in ('', '/'),
                        'has_query_or_fragment': bool(url.query or url.fragment)}
        except (TypeError, ValueError):
            pass
    result['ANTHROPIC_BASE_URL'] = base
    return result

def _setting_projection(value):
    _require(isinstance(value, dict), 'ROUTING_SETTINGS_OBJECT')
    result = {}
    for key in SETTING_KEYS:
        if key not in value:
            continue
        item = value[key]
        if key in ('enforceAvailableModels', 'switchModelsOnFlag', 'wslInheritsWindowsSettings'):
            result[key] = ({'status': 'OBSERVED', 'value': item} if type(item) is bool
                           else {'status': 'UNEXPECTED_TYPE_NOT_DISCLOSED'})
        elif key == 'modelOverrides':
            result[key] = ({'status': 'OBSERVED_ENTRIES', 'entries': [
                {'model': _model(k), 'target': _model(v)} for k, v in item.items()]}
                if isinstance(item, dict) and len(item) <= 128
                else {'status': 'UNSUPPORTED_MAP_NOT_DISCLOSED'})
        elif isinstance(item, list) and key in ('fallbackModel', 'availableModels'):
            result[key] = ([_model(v) for v in item] if len(item) <= 128
                           else {'status': 'OVERSIZE_LIST_NOT_DISCLOSED'})
        else:
            result[key] = _model(item)
    if isinstance(value.get('env'), dict):
        result['named_routing_env'] = named_environment(value['env'])
    return result

def _cache_projection(value):
    _require(isinstance(value, dict), 'ROUTING_CACHE_OBJECT')
    def booleans(obj, names):
        return {name: obj[name] for name in names if isinstance(obj, dict)
                and type(obj.get(name)) is bool}
    result = {'features': booleans(value.get('cachedGrowthBookFeatures'),
                                  ('tengu_dash_flame', 'tengu_loggia_denkbild')),
              'legacy_client': booleans(value.get('clientDataCache'), ('convolute_arcades',))}
    slots = value.get('clientDataCacheSlots', {})
    _require(isinstance(slots, dict) and len(slots) <= 128, 'ROUTING_CACHE_SLOT_BOUND')
    result['client_slots'] = [{'slot_key_sha256': digest(key.encode()),
                              'fields': booleans(row.get('data'), ('convolute_arcades',))}
                             for key, row in slots.items() if isinstance(row, dict)]
    access = value.get('modelAccessCache', [])
    _require(isinstance(access, list) and len(access) <= 128, 'ROUTING_MODEL_ACCESS_BOUND')
    result['model_access'] = [{'model': _model(row.get('apiName')), 'entitled': row['entitled']}
                             for row in access if isinstance(row, dict)
                             and type(row.get('entitled')) is bool]
    org = value.get('orgModelDefaultCache')
    if isinstance(org, dict):
        result['org_default'] = {'model': _model(org.get('name')),
                                **booleans(org, ('override_user_selection',))}
    result['active_slot_or_live_payload_observed'] = False
    return result


def capture(*, request_path, executable, executable_sha256, environment, cwd,
            mode, managed_settings=(), config_cache=None, launcher_sha256=None):
    """Observe supplied launch inputs; caller owns launch and current/past attribution."""
    _require(mode in MODES, 'ROUTING_CAPTURE_MODE')
    _require(re.fullmatch('[0-9a-f]{64}', executable_sha256 or ''), 'ROUTING_EXECUTABLE_PIN')
    _require(launcher_sha256 is None or re.fullmatch('[0-9a-f]{64}', launcher_sha256), 'ROUTING_LAUNCHER_PIN')
    request_raw, request_pin = _read(request_path, 4000000)
    request = _parsed(request_raw)
    command = request.get('command')
    _require(isinstance(command, list) and command and all(isinstance(x, str) for x in command), 'ROUTING_REQUEST_COMMAND')
    _, binary = _read(executable, 350000000, executable=True)
    _require(binary['sha256'] == executable_sha256, 'ROUTING_EXECUTABLE_CHANGED')
    cwd = Path(cwd).resolve(strict=True)
    _require(cwd.is_dir(), 'ROUTING_CHILD_CWD')
    target = Path(command[0])
    if '/' in command[0]:
        target = target if target.is_absolute() else cwd / target
    else:
        candidates = [(Path(part) if Path(part).is_absolute() else cwd / part) / command[0]
                      for part in environment.get('PATH', os.defpath).split(os.pathsep)]
        target = next((p for p in candidates if p.is_file() and os.access(p, os.X_OK)), None)
    _require(target is not None and target.resolve(strict=True) == Path(binary['resolved_path']),
             'ROUTING_COMMAND_EXECUTABLE_MISMATCH')
    _require(len(managed_settings) <= 16, 'ROUTING_SETTINGS_COUNT')
    files = []
    for path in managed_settings:
        path = Path(path).absolute()
        _require(path.suffix == '.json' and 'credential' not in path.name.lower()
                 and path.name not in ('auth.json', 'token.json', '.claude.json', '.config.json'),
                 'ROUTING_MANAGED_SETTINGS_ONLY')
        row = {'path': str(path)}
        try:
            raw, identity = _read(path, 2000000)
            row.update(original_identity=identity, projection=_setting_projection(_parsed(raw)), status='OBSERVED')
        except FileNotFoundError:
            row['status'] = 'ABSENT'
        except (OSError, ValueError, TypeError, UnicodeError):
            row['status'] = 'UNOBSERVED_READ_OR_PARSE_REFUSED'
        files.append(row)
    cache = None
    if config_cache is not None:
        path = Path(config_cache).absolute()
        _require(path.name in ('.config.json', '.claude.json', '.claude-custom-oauth.json',
                              '.claude-local-oauth.json', '.claude-staging-oauth.json'),
                 'ROUTING_NAMED_GLOBAL_CACHE_REQUIRED')
        cache = {'path': str(path)}
        try:
            raw, identity = _read(path, 4000000)
            cache.update(status='OBSERVED_CACHED_FIELDS', original_identity=identity,
                         projection=_cache_projection(_parsed(raw)))
        except FileNotFoundError:
            cache['status'] = 'ABSENT'
        except (OSError, ValueError, TypeError, UnicodeError):
            cache['status'] = 'UNOBSERVED_READ_OR_PARSE_REFUSED'
    account = pwd.getpwuid(os.geteuid())
    result = {'schema': SCHEMA, 'mode': mode,
              'observed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'source': request.get('reviewed_commit'), 'scope': request.get('scope'),
              'request': request_pin, 'command_sha256': digest(encoded(command)),
              'requested_executable': command[0], 'executable': binary,
              'launcher_sha256': launcher_sha256, 'child_cwd': str(cwd),
              'os_account': {'uid': os.getuid(), 'euid': os.geteuid(), 'gid': os.getgid(),
                             'egid': os.getegid(), 'groups': os.getgroups(),
                             'username': account.pw_name, 'passwd_home': account.pw_dir},
              'named_environment': named_environment(environment), 'managed_settings': files,
              'config_cache': cache,
              'environment_provenance': 'EXACT_CALLER_SUPPLIED_MAPPING; no subprocess observed by this helper',
              'historical_environment_reconstructed': False,
              'effective_cli_policy_exported': False, 'live_feature_payload_observed': False,
              'authenticated_claude_account': 'NOT_OBSERVED',
              'qualification_authority': False}
    _require(len(encoded(result)) <= 100000, 'ROUTING_SIDECAR_BOUND')
    return result

def capture_plan(plan_raw, *, environment):
    """Caller supplies the exact planned courier environment; never launches it."""
    plan = _parsed(plan_raw)
    required = {'schema', 'request_path', 'executable', 'executable_sha256', 'cwd', 'mode',
                'managed_settings', 'config_cache', 'launcher_sha256'}
    _require(isinstance(plan, dict) and set(plan) == required
             and plan['schema'] == 'review-routing-capture-plan/v1', 'ROUTING_PLAN_REQUIRED')
    result = capture(**{k: v for k, v in plan.items() if k != 'schema'}, environment=environment)
    result['plan_sha256'] = digest(plan_raw)
    return result


def write_sidecar(path, value):
    """Exclusive private output; existing or partial captures are never overwritten."""
    raw = encoded(value)
    _require(value.get('schema') == SCHEMA and len(raw) <= 100000, 'ROUTING_SIDECAR_BOUND')
    path = Path(path).absolute()
    _require(not any(p.is_symlink() for p in (path, *path.parents)), 'ROUTING_SYMLINK_REFUSED')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as output:
        output.write(raw)
        output.flush()
        os.fsync(output.fileno())
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return {'path': str(path), 'bytes': len(raw), 'sha256': digest(raw)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    raw, _ = _read(args.plan, 100000)
    value = capture_plan(raw, environment=os.environ)
    print(json.dumps(write_sidecar(args.output, value), sort_keys=True))


if __name__ == '__main__':
    main()
