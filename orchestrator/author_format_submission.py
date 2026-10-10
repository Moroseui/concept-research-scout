"""Bound same-call feedback for the approved item4 author5 format correction.

No admission, attempt accounting, science execution or provider imports. The
normal host validators and independent scientific review remain mandatory.
"""
import hashlib
import json
import os
from pathlib import Path
import stat

RUNTIME = '.author-runtime'
CONFIG = RUNTIME + '/config.json'
SERVER = RUNTIME + '/submit.py'
RECORD = '.author-submission.json'
OUTPUTS = ('SPEC.proposed.md', 'execution.plan.json', 'notebook.patch.json')
LIMIT = 80000
REVISION_SCHEMA = 'item4-scientific-revision-submission/v1'
MODULE_VIEW = RUNTIME+'/module-view.txt'
MODULE_MANIFEST = RUNTIME+'/module-view-manifest.json'
FIXTURE_REFERENCE=RUNTIME+'/fixture-reference.py'
AUTHOR24_CALL='4a171e924b528328d4a4827815113449b39d19143a8824b92f17dce0ecf0b8ca'
FIXTURE_PIN='fa54d6e41db935c4a7671abe278d4a40423bda41cfce32692b58ed1364638d20'
LIBRARIES = ('author_output_schema', 'experiment_plan_validation', 'experiment_environment_requirements', 'modal_billing', 'notebook_execution', 'scientific_view_scan', 'privacy_patterns', 'fixture_contract')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise ValueError('AUTHOR_DUPLICATE_KEY')
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError('AUTHOR_NONFINITE_JSON')
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError('AUTHOR_INVALID_JSON') from error


def regular(path, limit=LIMIT):
    path = Path(path)
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError('AUTHOR_FILE_ALIAS')
    value = path.stat()
    if not stat.S_ISREG(value.st_mode) or value.st_nlink != 1 or value.st_mode & 0o027 or value.st_size > limit:
        raise ValueError('AUTHOR_FILE_IDENTITY')
    return path.read_bytes()


def load(root, pin):
    raw = regular(Path(root)/CONFIG)
    if sha(raw) != pin:
        raise ValueError('AUTHOR_CONFIG_CHANGED')
    value = strict(raw)
    if value.get('schema') == REVISION_SCHEMA:
        return load_revision(value)
    if (set(value) != {'schema', 'bindings', 'originals', 'output_schema'} or
            value['schema'] != 'item4-author5-format-submission/v1' or
            set(value['originals']) != set(OUTPUTS)):
        raise ValueError('AUTHOR_CONFIG_SCHEMA')
    expected = {'call_id', 'run_id', 'stage', 'round', 'source_sha', 'runtime_sha256', 'input_sha256'}
    if (set(value['bindings']) != expected or value['bindings']['round'] != 5 or
            value['bindings']['stage'] != 'run_spec_author' or
            value['bindings']['run_id'] != 'experiment-a74959ac4546a982af4ae137'):
        raise ValueError('AUTHOR_CONFIG_BINDING')
    for name, ref in value['originals'].items():
        if (set(ref) != {'path', 'sha256'} or ref['path'] != RUNTIME+'/originals/'+name or
                sha(regular(Path(root)/ref['path'])) != ref['sha256']):
            raise ValueError('AUTHOR_ORIGINAL_CHANGED')
    return value


def validate(root, config):
    root = Path(root)
    if config['schema'] == REVISION_SCHEMA:
        return validate_revision(root, config)
    original = {name: regular(root/ref['path']) for name, ref in config['originals'].items()}
    current = {name: regular(root/name) for name in OUTPUTS}
    plan = strict(current['execution.plan.json'])
    expected = strict(original['execution.plan.json'])
    rows = expected['full_training']['full_fits']
    if len(rows) != 40:
        raise ValueError('AUTHOR_ORIGINAL_ROW_COUNT')
    fields = {'fit_id', 'timing_fit_id', 'epochs', 'fixed_seconds', 'overhead_micro_usd', 'applicability_assumption'}
    for row in rows:
        if set(row) != fields:
            raise ValueError('AUTHOR_ORIGINAL_FORMAT_CHANGED')
        row['assumption'] = row.pop('applicability_assumption')
    # Constructing an in-memory comparison is not an authored output repair.
    # Only the scientific author may write or submit the output files.
    if canonical(plan) != canonical(expected):
        raise ValueError('AUTHOR_FIELD_NAME_CORRECTION_REQUIRED')
    old_line = b'execution_plan_sha256: ' + sha(original['execution.plan.json']).encode()
    new_line = b'execution_plan_sha256: ' + sha(current['execution.plan.json']).encode()
    if original['SPEC.proposed.md'].splitlines().count(old_line) != 1:
        raise ValueError('AUTHOR_ORIGINAL_SPEC_BINDING')
    expected_spec = b''.join(new_line + line[len(old_line):] if line.rstrip(b'\r\n') == old_line else line
                             for line in original['SPEC.proposed.md'].splitlines(keepends=True))
    if current['SPEC.proposed.md'] != expected_spec:
        raise ValueError('AUTHOR_SPEC_BINDING_CORRECTION_REQUIRED')
    if current['notebook.patch.json'] != original['notebook.patch.json']:
        raise ValueError('AUTHOR_NOTEBOOK_CHANGE_OUTSIDE_SCOPE')
    return {name: sha(raw) for name, raw in current.items()}


def submit(root, pin, arguments):
    root = Path(root)
    if arguments != {}:
        raise ValueError('AUTHOR_SUBMISSION_NO_ARGUMENTS')
    config = load(root, pin)
    if (root/RECORD).exists() or (root/RECORD).is_symlink():
        raise ValueError('AUTHOR_SECOND_SUBMISSION_REFUSED')
    files = validate(root, config)
    raw = canonical({'schema': 'accepted-author-submission/v1', 'config_sha256': pin,
                     'bindings': config['bindings'], 'files': files})
    fd = os.open(root/RECORD, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as target:
        target.write(raw)
        target.flush()
        os.fsync(target.fileno())
    return {'status': 'ACCEPTED', 'record_sha256': sha(raw), 'files': files}


def verify(root, pin):
    config = load(root, pin)
    raw = regular(Path(root)/RECORD)
    expected = {'schema': 'accepted-author-submission/v1', 'config_sha256': pin,
                'bindings': config['bindings'], 'files': validate(root, config)}
    if raw != canonical(expected):
        raise ValueError('AUTHOR_SUBMISSION_CHANGED')
    return expected



def verify_native(root, pin, console):
    """Require a native exec MCP completion as well as exact accepted bytes.

    Wire shape verified against openai/codex rust-v0.153.4 exec_events.rs;
    final assistant text and shell output are never submission evidence.
    """
    accepted = verify(root, pin)
    expected = {'status': 'ACCEPTED',
                'record_sha256': sha(regular(Path(root)/RECORD)), 'files': accepted['files']}
    matches = []
    for line in console.splitlines():
        try:
            event = strict(line)
        except ValueError:
            continue
        if not isinstance(event, dict) or event.get('type') != 'item.completed':
            continue
        item = event.get('item', {})
        if not isinstance(item, dict) or item.get('type') != 'mcp_tool_call':
            continue
        if item.get('server') != 'author_format' or item.get('tool') != 'submit_author':
            continue
        result = item.get('result')
        if item.get('status') != 'completed' or item.get('error') is not None or item.get('arguments') != {} or not isinstance(result, dict):
            continue
        for block in result.get('content', []):
            if not isinstance(block, dict) or block.get('type') != 'text':
                continue
            try:
                answer = strict(block['text'])
            except (KeyError, ValueError, TypeError):
                continue
            if canonical(answer) == canonical(expected):
                matches.append(item.get('id'))
    if len(matches) != 1 or not isinstance(matches[0], str) or not matches[0]:
        raise ValueError('AUTHOR_NATIVE_ACCEPTED_SUBMISSION_REQUIRED')
    return {**expected, 'native_item_id': matches[0], 'config_sha256': pin}


def prepare(root, bindings, originals, output_schema):
    """Host-only preparation before admission; no edits to authored outputs."""
    root = Path(root)
    if set(originals) != set(OUTPUTS) or (root/RECORD).exists():
        raise ValueError('AUTHOR_PREPARATION_SCOPE')
    runtime = root/RUNTIME
    runtime.mkdir(mode=0o700)  # existing means inspect, never replay preparation
    (runtime/'originals').mkdir(mode=0o700)
    refs = {}
    bodies = {SERVER: Path(__file__).read_bytes()}
    for name, raw in originals.items():
        if not isinstance(raw, bytes) or len(raw) > LIMIT:
            raise ValueError('AUTHOR_ORIGINAL_SIZE')
        relative = RUNTIME+'/originals/'+name
        refs[name] = {'path': relative, 'sha256': sha(raw)}
        bodies[relative] = raw
    bodies[CONFIG] = canonical({'schema': 'item4-author5-format-submission/v1',
        'bindings': bindings, 'originals': refs, 'output_schema': output_schema})
    for name, raw in bodies.items():
        fd = os.open(root/name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as output:
            output.write(raw)
    pins = {name: sha(raw) for name, raw in bodies.items()}
    load(root, pins[CONFIG])
    return pins



def load_revision(value):
    if set(value) not in ({'schema','bindings','revision','output_schema'}, {'schema','bindings','revision','output_schema','notebook'}, {'schema','bindings','revision','output_schema','notebook','delivery'}):
        raise ValueError('AUTHOR_CONFIG_SCHEMA')
    b = value['bindings'];r = value['revision']
    fields = {'call_id','run_id','stage','round','source_sha','runtime_sha256','input_sha256'}
    if (set(b)!=fields or b['stage']!='run_spec_author' or b['run_id']!='experiment-a74959ac4546a982af4ae137' or
            type(b['round']) is not int or b['round']<6 or
            b['call_id']!=sha((b['run_id']+':'+b['stage']+':'+str(b['round'])).encode()) or
            set(r)!={'review_call_id','review_sha256','operator_scope_sha256','original_sha256','view_sha256'} or
            any(not isinstance(pin,str) or len(pin)!=64 or any(c not in '0123456789abcdef' for c in pin) for pin in r.values())):
        raise ValueError('AUTHOR_CONFIG_BINDING')
    if 'delivery' in value:
        d=value['delivery']
        if (b['round']!=24 or b['call_id']!=AUTHOR24_CALL or
                d!={'notebook_patch_bytes':96000,'fixture_reference':{'path':FIXTURE_REFERENCE,'sha256':FIXTURE_PIN}}):
            raise ValueError('AUTHOR24_DELIVERY_SCOPE')
    return value


def validate_revision(root, config):
    from orchestrator import author_output_schema as output
    limit=config.get('delivery',{}).get('notebook_patch_bytes',LIMIT)
    current = {name:regular(root/name,limit=limit if name=='notebook.patch.json' else LIMIT) for name in OUTPUTS}
    binding = {**config['bindings'], **config['revision']}
    output.plan(strict(current['execution.plan.json']), binding)
    patch_value=strict(current['notebook.patch.json'])
    output.patch(patch_value, binding)
    from orchestrator.scientific_view_scan import reject_opaque
    for edit in patch_value['edits']:reject_opaque(edit['replacement'].encode())
    if 'notebook' in config:
        refs=config['notebook']
        if set(refs)!={MODULE_VIEW,MODULE_MANIFEST}:raise ValueError('AUTHOR_MODULE_REFERENCES')
        raw={name:regular(root/name,limit=1400000) for name in refs}
        if {name:sha(body) for name,body in raw.items()}!=refs:raise ValueError('AUTHOR_MODULE_FILES_CHANGED')
        reference=None
        if 'delivery' in config:
            reference=regular(root/FIXTURE_REFERENCE,limit=200000)
            if sha(reference)!=FIXTURE_PIN:raise ValueError('AUTHOR_FIXTURE_REFERENCE_CHANGED')
        output.visible_module(strict(current['notebook.patch.json']),raw[MODULE_VIEW],strict(raw[MODULE_MANIFEST]),fixture_reference=reference)
    text=current['SPEC.proposed.md'].decode()
    if len(text)>12000:
        raise ValueError('EXPERIMENT_SPEC_LIMIT: SPEC.proposed.md must be at most 12000 characters; shorten it before submitting')
    for raw in (current['SPEC.proposed.md'],current['execution.plan.json']):reject_opaque(raw)
    lines=text.splitlines()
    for key,expected in {'run_id':binding['run_id'], 'operator_scope_sha256':binding['operator_scope_sha256'],
                         'execution_plan_sha256':sha(current['execution.plan.json'])}.items():
        if [line for line in lines if line.startswith(key+':')] != [key+': '+expected]:
            raise ValueError('AUTHOR_SPEC_BINDING')
    return {name:sha(raw) for name,raw in current.items()}


def prepare_revision(root, bindings, revision, *, notebook=None, fixture_reference=None):
    from orchestrator.author_output_schema import schema
    root=Path(root)
    if (root/RECORD).exists() or (root/RECORD).is_symlink():
        raise ValueError('AUTHOR_PREPARATION_SCOPE')
    runtime=root/RUNTIME;runtime.mkdir(mode=0o700)
    (runtime/'orchestrator').mkdir(mode=0o700)
    bodies={SERVER:Path(__file__).read_bytes(), RUNTIME+'/orchestrator/__init__.py':b''}
    for name in LIBRARIES:
        bodies[RUNTIME+'/orchestrator/'+name+'.py']=Path(__file__).with_name(name+'.py').read_bytes()
    config={'schema':REVISION_SCHEMA,'bindings':bindings,'revision':revision,'output_schema':schema()}
    if notebook is not None:
        if not isinstance(notebook,dict) or set(notebook)!={MODULE_VIEW,MODULE_MANIFEST} or any(not isinstance(raw,bytes) or len(raw)>1400000 for raw in notebook.values()):
            raise ValueError('AUTHOR_MODULE_INPUTS')
        if sha(notebook[MODULE_VIEW])!=revision['view_sha256'] or strict(notebook[MODULE_MANIFEST]).get('view_sha256')!=revision['view_sha256']:
            raise ValueError('AUTHOR_MODULE_VIEW_BINDING')
        bodies.update(notebook);config['notebook']={name:sha(raw) for name,raw in notebook.items()}
    if fixture_reference is not None:
        if notebook is None or sha(fixture_reference)!=FIXTURE_PIN:raise ValueError('AUTHOR_FIXTURE_REFERENCE_SCOPE')
        config['delivery']={'notebook_patch_bytes':96000,'fixture_reference':{'path':FIXTURE_REFERENCE,'sha256':FIXTURE_PIN}}
        config['output_schema']=schema(notebook_patch_bytes=96000)
        load_revision(config)
        bodies[FIXTURE_REFERENCE]=fixture_reference
    bodies[CONFIG]=canonical(config)
    for name,raw in bodies.items():
        fd=os.open(root/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as target:target.write(raw)
    pins={name:sha(raw) for name,raw in bodies.items()}
    check_runtime(root,pins)
    return pins


def check_runtime(root, pins):
    config = load(root, pins[CONFIG])
    expected = ({CONFIG, SERVER, RUNTIME+'/orchestrator/__init__.py',
                 *(RUNTIME+'/orchestrator/'+name+'.py' for name in LIBRARIES)}
                if config['schema'] == REVISION_SCHEMA else
                {CONFIG, SERVER, *(RUNTIME+'/originals/'+name for name in OUTPUTS)})
    if config.get('notebook') is not None:
        if set(config['notebook'])!={MODULE_VIEW,MODULE_MANIFEST}:raise ValueError('AUTHOR_MODULE_REFERENCES')
        expected|=set(config['notebook'])
    if 'delivery' in config:expected.add(FIXTURE_REFERENCE)
    if set(pins) != expected:
        raise ValueError('AUTHOR_RUNTIME_FILE_SET')
    for name, pin in pins.items():
        if sha(regular(Path(root)/name,limit=1400000 if name in {MODULE_VIEW,MODULE_MANIFEST} else 200000 if name==FIXTURE_REFERENCE else LIMIT)) != pin:
            raise ValueError('AUTHOR_RUNTIME_CHANGED')
    load(root, pins[CONFIG])


def protect_command(command, root, pins):
    """Add one read-only bind to the existing qualified outer namespace."""
    root = Path(root).resolve()
    check_runtime(root, pins)
    positions = [i for i, value in enumerate(command) if value == '--bind' and
                 command[i+1:i+3] == [str(root), '/workspace']]
    if len(positions) != 1 or command.count('--chdir') != 1:
        raise ValueError('AUTHOR_OUTER_COMMAND_BINDING')
    index = command.index('--chdir')
    if index <= positions[0] or command[index+1] != '/workspace':
        raise ValueError('AUTHOR_OUTER_COMMAND_BINDING')
    return command[:index] + ['--ro-bind', str(root/RUNTIME), '/workspace/'+RUNTIME] + command[index:]


def client_command(command, root, pins):
    check_runtime(root, pins)
    if (command[:3] != ['/tools/node', '/tools/codex/bin/codex.js', 'exec'] or
            command[-1] != '-' or '--ignore-user-config' not in command or
            'sandbox_workspace_write.network_access=false' not in command):
        raise ValueError('AUTHOR_CLIENT_COMMAND_BINDING')
    # Command-line configuration only; existing credentials/config files unchanged.
    extra = ['-c', 'mcp_servers.author_format.command="/usr/bin/python3"', '-c',
        'mcp_servers.author_format.args='+json.dumps(['-I', '-B', '/workspace/'+SERVER, pins[CONFIG]])]
    return command[:-1] + extra + command[-1:]


def serve(root, pin):
    import sys
    config = load(root, pin)
    tool = {'name': 'submit_author',
            'description': 'Validate the three authored files against the bound output schema. '
                'Write files first, then call with no arguments. Correct returned validation errors '
                'in this same session and submit again. Accepted files cannot be replaced. '
                'This does not approve science or start computation.',
            'annotations': {'readOnlyHint': False, 'destructiveHint': False,
                            'openWorldHint': False, 'idempotentHint': False},
            'inputSchema': {'type': 'object', 'properties': {}, 'additionalProperties': False}}
    recoverable = {'AUTHOR_INVALID_JSON', 'AUTHOR_DUPLICATE_KEY', 'AUTHOR_NONFINITE_JSON',
                   'AUTHOR_FIELD_NAME_CORRECTION_REQUIRED', 'AUTHOR_SPEC_BINDING_CORRECTION_REQUIRED',
                   'AUTHOR_NOTEBOOK_CHANGE_OUTSIDE_SCOPE', 'AUTHOR_SUBMISSION_NO_ARGUMENTS'}
    for raw in iter(lambda: sys.stdin.buffer.readline(8193), b''):
        if len(raw) > 8192:
            raise ValueError('AUTHOR_REQUEST_BOUND')
        request = strict(raw)
        ident = request.get('id')
        if ident is None:
            continue
        try:
            method = request.get('method')
            if method == 'initialize':
                result = {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}},
                          'serverInfo': {'name': 'author-format-submission', 'version': '1'}}
            elif method == 'tools/list':
                result = {'tools': [tool]}
            elif method == 'ping':
                result = {}
            elif method == 'tools/call':
                params = request['params']
                if params['name'] != 'submit_author':
                    raise ValueError('AUTHOR_TOOL_REFUSED')
                try:
                    answer = submit(root, pin, params.get('arguments', {}))
                    failed = False
                except ValueError as error:
                    if str(error) not in recoverable and not (config['schema'] == REVISION_SCHEMA and (str(error) == 'PRIVATE_INTAKE_OPAQUE_PAYLOAD_REJECTED' or str(error).startswith(('AUTHOR_PLAN_', 'AUTHOR_PREPROCESSING_', 'AUTHOR_PATCH_', 'AUTHOR_SPEC_', 'AUTHOR_MODULE_', 'EXPERIMENT_')))):
                        raise
                    answer = {'validation_error': str(error), 'required_output_schema': config['output_schema']}
                    failed = True
                result = {'content': [{'type': 'text', 'text': json.dumps(answer, ensure_ascii=True)}],
                          'isError': failed}
            else:
                raise ValueError('AUTHOR_METHOD_REFUSED')
            reply = {'jsonrpc': '2.0', 'id': ident, 'result': result}
        except (ValueError, KeyError, TypeError, OSError) as error:
            # Do not expose exception messages from file/runtime errors.
            reply = {'jsonrpc': '2.0', 'id': ident,
                     'error': {'code': -32602, 'message': 'AUTHOR_SUBMISSION_RUNTIME_REFUSED'}}
        print(json.dumps(reply, ensure_ascii=True), flush=True)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        raise SystemExit('AUTHOR_CONFIG_PIN_REQUIRED')
    # Only the host-prepared read-only runtime package is made importable.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    serve(Path.cwd(), sys.argv[1])
