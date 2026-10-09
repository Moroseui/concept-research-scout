"""One approved author5; original driver, admission, science and safeguards stay.

The component adds only measured format instructions, fixed same-call feedback,
and a read-only runtime subtree. It cannot dispatch compute or author round6.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

CHANGE = 'item4-author-submission-20261008'
ROOT = Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD = Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
SCIENCE = Path('/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
STATE = Path('/var/lib/research-system-manual-sprint10/releases')/SCIENCE.name
LANE = STATE/'item4/lane'
WORK = STATE/'item4/lane-scientific-workspaces/run_spec_author-5'
DEST = STATE/'item4'/CHANGE
GLOBAL = Path('/var/lib/research-system-autonomy/reviews')
RUNTIME = Path('/etc/research-system-manual-sprint10/releases')/SCIENCE.name/'runtime.json'
DAILY = Path('/opt/research-system/manual-repair-helpers/daily-limit-and-image-probe-20261007/tools/daily_limit_component.py')
AUTHORITY = '40b6529f29e9710bae217cfb84cf213caa601f99d84aa48b3259e3dba73f3fc7'
MODULES = ('experiment_plan_validation', 'experiment_plan_output', 'experiment_context', 'author_format_submission')
FILES = tuple('orchestrator/'+n+'.py' for n in MODULES) + (
    'tools/item4_author_submission_component.py', 'tools/install_item4_author_submission.py',
    'tools/ITEM4_AUTHOR5_BINDINGS.json', 'docs/ITEM4_AUTHOR5_OPERATOR_APPROVAL_20261008.txt')
GUIDANCE = (
    'OPERATOR-APPROVED AUTHOR5 SCOPE: correct ONLY the full_training.full_fits field name '
    'applicability_assumption to assumption in all40 rows, preserving every value and all '
    'other plan content. Update ONLY the SPEC execution_plan_sha256 line to the new plan '
    'hash; preserve every other SPEC byte. Copy the original notebook.patch.json bytes '
    'unchanged. Author4 originals are the selected author5-original artifacts and the '
    'read-only .author-runtime/originals files. Earlier drafts/guidance are historical. '
    'This specific scope supersedes generic invitations to redesign. You, the scientific '
    'author, write all three output files. The required projection schema is included '
    'below. When files are ready, call author_format.submit_author with {}. If validation '
    'returns a format error, correct it and call again IN THIS SESSION; there is no new '
    'model invocation or attempt for tool retries. Finish only after ACCEPTED, and do '
    'not change outputs afterwards. No scientific changes, execution or authorization '
    'expansion. All original attempts and charges remain counted.\n'
)


def require(ok, why):
    if not ok: raise ValueError(why)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
def trusted(path):
    path = Path(path)
    for p in [path, *path.parents]:
        st = p.lstat()
        require(not p.is_symlink() and st.st_uid == 0 and not st.st_mode & 0o022, 'AUTHOR_COMPONENT_UNTRUSTED')
    return path

def load_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verified(root=ROOT, record=RECORD):
    from orchestrator.autonomy_review import verify_result
    v = json.loads(trusted(Path(record)/'installed.json').read_bytes())
    require(v['schema'] == 'reviewed-author5-component/v1' and v['root'] == str(root), 'AUTHOR_COMPONENT_INSTALL_SCOPE')
    review = verify_result(Path(v['review_folder']))
    require(review['verdict'] == 'APPROVE' and review['change_id'] == CHANGE and
            review['source_sha'] == v['source'] and review['report_sha256'] == v['review_sha256'] and
            review['runtime_sha256'] == sha(trusted(RUNTIME).read_bytes()), 'AUTHOR_COMPONENT_APPROVAL')
    manifest = json.loads(trusted(Path(v['review_folder'])/'packet-manifest.json').read_bytes())
    require(set(v['files']) == set(FILES), 'AUTHOR_COMPONENT_FILES')
    for name, pin in v['files'].items():
        require(sha(trusted(Path(root)/name).read_bytes()) == pin == manifest['source_files'][name], 'AUTHOR_COMPONENT_FILE_CHANGED')
    for path, pin in v['base_files'].items():
        require(sha(trusted(path).read_bytes()) == pin, 'AUTHOR_COMPONENT_BASE_CHANGED')
    for path, pin in v['units'].items():
        require(sha(trusted(path).read_bytes()) == pin, 'AUTHOR_COMPONENT_UNIT_CHANGED')
    require(sha(trusted(Path(root)/'docs/ITEM4_AUTHOR5_OPERATOR_APPROVAL_20261008.txt').read_bytes()) == AUTHORITY, 'AUTHOR_COMPONENT_AUTHORITY')
    binding = json.loads(trusted(Path(root)/'tools/ITEM4_AUTHOR5_BINDINGS.json').read_bytes())
    require(binding['authority_sha256'] == AUTHORITY and binding['runtime_sha256'] == review['runtime_sha256'], 'AUTHOR_BINDING_AUTHORITY')
    return v, binding


def load():
    require(os.getuid() == os.getgid() == 1003 and Path(__file__).resolve() == ROOT/'tools/item4_author_submission_component.py', 'AUTHOR_SERVICE_OWNER_PATH')
    v, binding = verified()
    # The trusted installation records the existing daily component BEFORE import.
    daily = load_file('_author5_existing_daily', trusted(DAILY))
    daily.load()
    import orchestrator
    require(Path(orchestrator.__file__).resolve() == SCIENCE/'orchestrator/__init__.py', 'AUTHOR_ORIGINAL_ENGINE_REQUIRED')
    for name in MODULES:
        require('orchestrator.'+name not in sys.modules, 'AUTHOR_COMPONENT_LOAD_ORDER')
        module = load_file('orchestrator.'+name, ROOT/'orchestrator'/(name+'.py'))
        setattr(orchestrator, name, module)
    return v, binding


def call_rows(db):
    return [dict(r) for r in db.execute('SELECT * FROM manual_calls ORDER BY rowid')]


def preserved_calls(calls, binding, *, allow_fifth=False):
    require(len(calls) in ({4, 5} if allow_fifth else {4}), 'AUTHOR_FIFTH_ONLY')
    require(sha(canonical(calls[:4])) == binding['calls_sha256'], 'AUTHOR_ORIGINAL_CALLS_CHANGED')
    if len(calls) == 5:
        last = calls[4]
        require(last['id'] == binding['call5'] and last['stage'] == 'run_spec_author' and last['attempt'] == 5,
                'AUTHOR_FIFTH_IDENTITY')


def check_global(db, binding):
    for ident, pin in binding['global_calls'].items():
        row = db.execute('SELECT * FROM autonomy_calls WHERE id=?', (ident,)).fetchone()
        require(row is not None and sha(canonical(dict(row))) == pin, 'AUTHOR_ORIGINAL_CHARGE_CHANGED')


def fifth_limit(original, store, run, stage, binding):
    if run != binding['run_id'] or stage != 'run_spec_author':
        return original(store, run, stage)
    require(Path(store.path).resolve() == LANE/'jobs.sqlite', 'AUTHOR_EXACT_LANE_REQUIRED')
    require(sha((LANE/'lane.json').read_bytes()) == binding['config_sha256'], 'AUTHOR_CONFIG_CHANGED')
    preserved_calls(call_rows(store.db), binding, allow_fifth=True)
    # This changes only the one authorized ordinal. Original per-run, day,
    # batch and dollar admission remains in ManualExecutor.reserve_call.
    return 5


def output_originals(binding):
    from orchestrator import private_records as pr
    work = WORK.with_name('run_spec_author-4')
    bodies = {name: pr.check(work/name).read_bytes() for name in binding['outputs']}
    require({n:sha(raw) for n,raw in bodies.items()} == binding['outputs'], 'AUTHOR_ORIGINAL_OUTPUT_CHANGED')
    return bodies


def apply():
    v, binding = load()
    from orchestrator import private_records as pr
    from orchestrator.manual_executor import lock
    from orchestrator.manual_context import selected_artifacts
    from orchestrator.git_publication import scan
    with lock(LANE/'driver.lock'):
        require(not (LANE/'HALT').exists() and not (GLOBAL/'HALT').exists(), 'OPERATOR_HALT')
        require(not DEST.exists() and not DEST.is_symlink() and not WORK.exists(), 'AUTHOR_RECOVERY_EXISTS_INSPECT')
        with pr.Connection(pr.check(LANE/'jobs.sqlite')) as db, sqlite3.connect((GLOBAL/'jobs.sqlite').as_uri()+'?mode=ro', uri=True) as globaldb:
            db.row_factory = globaldb.row_factory = sqlite3.Row
            config_raw = pr.check(LANE/'lane.json').read_bytes()
            raw = db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
            require(sha(config_raw) == binding['config_sha256'] and sha(raw.encode()) == binding['state_sha256'], 'AUTHOR_EXACT_BLOCK_REQUIRED')
            config, value = json.loads(config_raw), json.loads(raw)
            require(config['source'] == binding['source'] and config['run_id'] == binding['run_id'] and
                    value['phase'] == 'BLOCKED' and value['reason'] == 'OUTPUT_VALIDATION_REFUSED: EXPERIMENT_PROJECTION_FULL_FIT' and
                    value['rounds'] == {'run_spec_author':4} and value['pending']['id'] == binding['call4'], 'AUTHOR_FORMAT_FAILURE_REQUIRED')
            preserved_calls(call_rows(db), binding)
            check_global(globaldb, binding)
            owner = globaldb.execute('SELECT binding,status FROM autonomy_runs WHERE id=?', (binding['run_id'],)).fetchone()
            require(owner and owner['status'] == 'ACTIVE' and json.loads(owner['binding']) == config['owner_binding'] and
                    json.loads(pr.check(config['owner_path']).read_bytes()) == config['owner_binding'], 'AUTHOR_OWNER_CHANGED')
            originals = output_originals(binding)
            before = {r[0]:sha(canonical([dict(x) for x in db.execute('SELECT * FROM "'+r[0]+'" ORDER BY rowid')]))
                      for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='manual_state'")}
            require(before == binding['accounting'], 'AUTHOR_ACCOUNTING_CHANGED')
            # No state/config/output mutation above this line; preserve first.
            pr.mkdir(DEST)
            pr.write_bytes(DEST/'intent.json', canonical({'binding':binding, 'review_sha256':v['review_sha256']}))
            backup = pr.Connection(DEST/'before.sqlite'); db.backup(backup); backup.close()
            pr.copyfile(LANE/'DECISION_REQUEST.md', DEST/'DECISION_REQUEST.original.md')
            descriptors = []
            kinds = {'SPEC.proposed.md':'run_spec', 'execution.plan.json':'execution_conditions', 'notebook.patch.json':'notebook_patch'}
            for name, body in originals.items():
                scan('context/'+name, body)
                relative = 'current/'+CHANGE+'/originals/'+name
                target = Path(config['context'])/relative
                pr.mkdir(target.parent, parents=True, exist_ok=True)
                require(not target.exists() and not target.is_symlink(), 'AUTHOR_CONTEXT_EXISTS')
                pr.write_bytes(target, body)
                descriptors.append({'id':'author5-original-'+name, 'type':kinds[name], 'path':relative, 'sha256':sha(body), 'version':1})
            old_ids = {'provenance-spec-original','provenance-plan-original','provenance-patch-original'}
            updated = {**value, 'phase':'run_spec_author', 'reason':None,
                'artifacts':[a for a in value['artifacts'] if a['id'] not in old_ids]+descriptors,
                'interventions':[*value['interventions'], {'kind':'AUTHORIZED_AUTHOR5_FORMAT_ONLY',
                    'authority_sha256':AUTHORITY,'review_sha256':v['review_sha256'], 'originals_preserved':True}]}
            updated.pop('pending', None); updated.pop('blocked_stage', None)
            selected_artifacts('run_spec_author', updated['artifacts'])
            db.execute('BEGIN IMMEDIATE')
            try:
                require(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0] == raw, 'AUTHOR_STATE_CHANGED')
                preserved_calls(call_rows(db), binding)
                db.execute('UPDATE manual_state SET payload=? WHERE id=1', (json.dumps(updated),))
                db.execute('COMMIT')
            except BaseException:
                db.execute('ROLLBACK'); raise
            preserved_calls(call_rows(db), binding); check_global(globaldb, binding)
            pr.write_bytes(DEST/'applied.json', canonical({'status':'APPLIED_HELD', 'state_sha256':sha(json.dumps(updated).encode()),
                'authority_sha256':AUTHORITY, 'review_sha256':v['review_sha256'], 'model_calls':0}))
    return {'status':'APPLIED_HELD', 'model_calls':0, 'item6_untouched':True}


def send(expected, family, command):
    _, binding = load()
    require(json.loads(trusted(RECORD/'APPLIED.json').read_bytes())['status'] == 'INSTALLED_HELD', 'AUTHOR_INSTALL_INCOMPLETE')
    from orchestrator import author_format_submission as af, manual_stage as ms
    require(Path.cwd().resolve() == WORK and family == 'codex', 'AUTHOR_SENDER_SCOPE')
    pins = json.loads((DEST/'runtime-pins.json').read_bytes())
    config = af.load(WORK, pins[af.CONFIG])
    require(config['bindings']['input_sha256'] == expected and config['bindings']['call_id'] == binding['call5'], 'AUTHOR_SENDER_INPUT')
    af.check_runtime(WORK, pins)
    base = ['/tools/node','/tools/codex/bin/codex.js','exec','--ignore-user-config','--ignore-rules','--model','gpt-6-astra',
        '-s','workspace-write','-c','approval_policy="never"','-c','sandbox_workspace_write.network_access=false','--json','-']
    require(command == af.client_command(base, WORK, pins), 'AUTHOR_SENDER_COMMAND')
    outer = ms.isolation.command
    def protected(workspace, *args, **kwargs):
        require(Path(workspace).resolve() == WORK, 'AUTHOR_SENDER_WORKSPACE')
        return af.protect_command(outer(workspace, *args, **kwargs), WORK, pins)
    ms.isolation.command = protected
    try: return ms.send_bound(expected, command, family=family)
    finally: ms.isolation.command = outer


def sender_profile(original, expected, commands, pins, *, sink=False, stage=None):
    from orchestrator import author_format_submission as af
    if sink: return original(expected, commands, sink=True, stage=stage)
    require(stage == 'run_spec_author', 'AUTHOR_ONLY_STAGE')
    changed = [(name, af.client_command(command, WORK, pins) if name=='codex' else command) for name, command in commands]
    text = original(expected, changed, stage=stage)
    prefix = json.dumps([sys.executable, '-m', 'orchestrator.manual_stage', '--send-bound'])[:-1]
    replacement = json.dumps([sys.executable, '-s', '-B', str(ROOT/'tools/item4_author_submission_component.py'), 'send'])[:-1]
    require(text.count(prefix) == 2, 'AUTHOR_PROFILE_SENDER_BINDING')
    return text.replace(prefix, replacement)


def run():
    v, binding = load()
    require(json.loads(trusted(RECORD/'APPLIED.json').read_bytes())['status'] == 'INSTALLED_HELD', 'AUTHOR_INSTALL_INCOMPLETE')
    from orchestrator import author_format_submission as af, manual_stage as ms, manual_recovery as recovery
    from orchestrator import private_records as pr
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.experiment_plan_validation import author_schema
    from orchestrator.manual_executor import lock
    require(json.loads(pr.check(DEST/'applied.json').read_bytes())['review_sha256'] == v['review_sha256'], 'AUTHOR_RECOVERY_REVIEW_CHANGED')
    old_limit, old_invoke, old_profile = recovery.role_limit, ms._invoke, ms.transport_profile
    def profile(expected, commands, *, sink=False, stage=None):
        pins = None if sink else json.loads(pr.check(DEST/'runtime-pins.json').read_bytes())
        return sender_profile(old_profile, expected, commands, pins, sink=sink, stage=stage)
    def invoke(workspace, stage, clients, expected):
        require(Path(workspace).resolve() == WORK and stage == 'run_spec_author', 'AUTHOR_INVOCATION_SCOPE')
        pins = json.loads(pr.check(DEST/'runtime-pins.json').read_bytes());af.check_runtime(workspace, pins)
        receipt = old_invoke(workspace, stage, clients, expected)
        af.check_runtime(workspace, pins)
        receipt['author_submission'] = af.verify_native(workspace, pins[af.CONFIG], (Path(workspace)/'console.log').read_text())
        receipt['author5_authority_sha256'] = AUTHORITY
        return receipt
    class Author5Driver(ExperimentDriver):
        def task(self, stage, value):
            return GUIDANCE + super().task(stage, value)
        def prepare_input(self, value, stage, work):
            require(Path(work).resolve() == WORK and stage == 'run_spec_author', 'AUTHOR_PREPARATION_SCOPE')
            body, measurement = super().prepare_input(value, stage, work)
            pins = af.prepare(work, {'call_id':binding['call5'], 'run_id':binding['run_id'], 'stage':stage, 'round':5,
                'source_sha':binding['source'], 'runtime_sha256':binding['runtime_sha256'], 'input_sha256':sha(body.encode())},
                output_originals(binding), author_schema())
            with pr.open_file(DEST/'runtime-pins.json','x') as f:json.dump(pins,f,sort_keys=True)
            return body, measurement
        def _advance(self, *args, **kwargs):
            self.guard()
            require(self.current()['phase'] == 'run_spec_author' and self.current()['rounds'] == {'run_spec_author':4}
                    and not self.current().get('pending'), 'AUTHOR_ONE_START_ONLY')
            preserved_calls(call_rows(self.store.db), binding)
            check_global(self.store.batch.db, binding)
            return super()._advance(*args, **kwargs)
    recovery.role_limit = lambda store, run, stage: fifth_limit(old_limit, store, run, stage, binding)
    ms._invoke, ms.transport_profile = invoke, profile
    driver = None
    try:
        driver = Author5Driver(LANE)
        require(sha(pr.check(LANE/'lane.json').read_bytes()) == binding['config_sha256'], 'AUTHOR_CONFIG_CHANGED')
        return driver.advance()
    finally:
        recovery.role_limit, ms._invoke, ms.transport_profile = old_limit, old_invoke, old_profile
        if driver is not None:
            driver.store.db.close();driver.store.batch.db.close()


if __name__ == '__main__':
    os.umask(0o077)
    if sys.argv[1:] == ['verify']:
        v, b = load();print(json.dumps({'status':'VERIFIED_HELD','source':v['source'],'model_calls':0}))
    elif sys.argv[1:] == ['apply']: print(json.dumps(apply(), sort_keys=True))
    elif sys.argv[1:] == ['run']: print(json.dumps(run(), sort_keys=True))
    elif len(sys.argv)>5 and sys.argv[1]=='send' and sys.argv[4]=='--':
        raise SystemExit(send(sys.argv[2], sys.argv[3], sys.argv[5:]))
    else: raise SystemExit('AUTHOR_COMPONENT_FIXED_ACTION_REQUIRED')
