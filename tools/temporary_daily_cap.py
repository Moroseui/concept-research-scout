"""Date-bound daily admission; original loaders and all scoped wrappers remain."""
import ast
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import sys
import textwrap

CHANGE = 'temporary-daily-cap-20261010'
ROOT = Path('/opt/research-system/manual-repair-helpers') / CHANGE
RECORD = Path('/var/lib/research-system-manual-sprint10-deployment') / CHANGE
SCIENCE = '/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339'
AUTHOR = Path('/opt/research-system/manual-repair-helpers/item4-author24-delivery-20261010/tools/item4_smoke_response_runtime.py')
AUTHOR_PIN = '69ad839bc315a46b792490483f11dc302427b9df70e20fba89f4ce57ab713853'
PINS = {'scientific':'b9f743d3ade30c8f9fafec005a396331f57f00e36b46a98636b3fbe3931de302',
        'administrative':'4fd2c903037ada521308a4de1d86e3a54e9fe74b2290eb88fbdce0d73633b7ce'}
FILES = ('tools/temporary_daily_cap.py', 'tools/install_temporary_daily_cap.py',
         'tools/temporary_daily_cap_host.py',
         'orchestrator/autonomy_limits.py', 'orchestrator/autonomy_accounting.py',
         'orchestrator/autonomy_review_runner.py', 'docs/LIMIT_OPERATOR_DECISION.txt',
         'docs/DAILY_LIMIT_OPERATOR_DECISION_20261007.txt', 'docs/OPERATOR_DIRECTION_20261010.txt')


def require(ok, why):
    if not ok: raise ValueError('TEMPORARY_DAILY_CAP_' + why)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def trusted(path):
    path = Path(path)
    for p in (path, *path.parents):
        st = p.lstat()
        require(not p.is_symlink() and st.st_uid == 0 and not st.st_mode & 0o022, 'TRUSTED_PATH')
    return path


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def method_pin(method):
    tree = ast.parse(textwrap.dedent(inspect.getsource(method)))
    require(len(tree.body) == 1 and isinstance(tree.body[0], ast.FunctionDef), 'METHOD_SOURCE')
    # Canonical fields avoid ast.dump formatting changes between Python versions.
    def canonical(node):
        if isinstance(node, ast.AST):
            return [type(node).__name__, [[k,canonical(v)] for k,v in ast.iter_fields(node)
                                         if k != 'type_params' or v]]
        if isinstance(node, list): return [canonical(v) for v in node]
        return node
    return sha(json.dumps(canonical(tree.body[0]), separators=(',',':')).encode())


def verified(root=ROOT, record=RECORD):
    from orchestrator.autonomy_review import verify_result
    root, record = Path(root), Path(record)
    state = json.loads(trusted(record/'installed.json').read_bytes())
    completed = json.loads(trusted(record/'complete.json').read_bytes())
    approval = verify_result(trusted(record/'review'))
    manifest = json.loads(trusted(record/'review/packet-manifest.json').read_bytes())
    require(completed == {'status':'PASS','model_calls':0,'provider_calls':0,'held':True}, 'INCOMPLETE_INSTALL')
    require(approval['verdict'] == 'APPROVE' and not approval.get('findings')
            and approval['change_id'] == CHANGE and approval['source_sha'] == state['source']
            and approval['report_sha256'] == state['report_sha256'], 'GENUINE_APPROVAL')
    require(state['root'] == str(root) and set(state['files']) == set(FILES), 'INSTALL_SCOPE')
    for name, pin in state['files'].items():
        require(sha(trusted(root/name).read_bytes()) == pin == manifest['source_files'][name], 'REVIEWED_SOURCE')
    for path, pin in state['units'].items():
        require(sha(trusted(path).read_bytes()) == pin, 'REVIEWED_UNIT')
    require(Path(__file__).resolve() == root/'tools/temporary_daily_cap.py', 'EXECUTED_SOURCE')
    return approval


def bind(kind, root=ROOT):
    """Call only after a verified install, or exact one-use admin bootstrap.

    Keep original limits module identity and every non-daily selector/wrapper.
    Science binding must precede scoped_calls.connect, never replace its wrapper.
    """
    require(kind in PINS, 'BIND_KIND')
    from orchestrator import autonomy_limits as limits
    if kind == 'scientific':
        from orchestrator.autonomy_accounting import BatchAccounts
        cls, name, source = BatchAccounts, 'reserve_scientific', 'autonomy_accounting'
    else:
        from orchestrator.autonomy_review_runner import ReviewQueue
        cls, name, source = ReviewQueue, 'reserve', 'autonomy_review_runner'
    require(method_pin(getattr(cls, name)) == PINS[kind], 'ORIGINAL_ADMISSION_METHOD')
    require(limits.DAILY == 50 and limits.SCIENTIFIC_BATCH == 60 and limits.REVISE_ROUNDS == 3,
            'BASE_LIMITS_CHANGED')
    policy = module('_dated_daily_policy_' + kind, Path(root)/'orchestrator/autonomy_limits.py')
    # Confirm both static authorities and the dated authority before binding.
    require(policy.daily_allowance('2026-10-10') == {
        'limit':100, 'authority_sha256':'644410e1659c8998040c3cc9035aaa0eb2c5c3708fba37cfbb1a91fadf9f00e6'}, 'DATED_AUTHORITY')
    require(policy.daily_allowance('2026-10-11')['limit'] == 50, 'REVERSION')
    candidate = module('_dated_daily_' + source, Path(root)/'orchestrator'/(source+'.py'))
    require(candidate.limits is limits, 'MODULE_IDENTITY')
    limits.daily_allowance = policy.daily_allowance
    method = getattr(getattr(candidate, cls.__name__), name)
    setattr(cls, name, method)
    return method


def author_route(root=ROOT):
    """Insert base daily policy immediately before unchanged scopes capture it."""
    verified(root)
    require(sha(trusted(AUTHOR).read_bytes()) == AUTHOR_PIN, 'AUTHOR_ENTRY_CHANGED')
    route = module('_dated_daily_author', AUTHOR)
    original = route.module
    captured = []
    def factory(name, path):
        if name == 'orchestrator.item4_scoped_calls':
            require(not captured, 'DUPLICATE_SCIENCE_BIND')
            # The original revision loader has just loaded its base method.
            captured.append(bind('scientific', root))
        return original(name, path)
    route.module = factory
    original_connect = route.connect
    def connect():
        result = original_connect()
        from orchestrator.autonomy_accounting import BatchAccounts
        require(len(captured) == 1 and BatchAccounts.reserve_scientific is not captured[0]
                and inspect.getclosurevars(BatchAccounts.reserve_scientific).nonlocals.get('old_batch') is captured[0],
                'SCOPED_WRAPPER_REQUIRED')
        return result
    route.connect = connect
    return route


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    require(os.getuid() == os.getgid() == 1003, 'SERVICE_OWNER')
    require(argv in (['author','verify'], ['author','run']), 'ACTION_SCOPE')
    sys.path.insert(0, SCIENCE)
    return author_route().main(argv[1:])


if __name__ == '__main__':
    os.umask(0o077)
    main()
