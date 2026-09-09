"""Readable fixed P001 setup cells and native-result checks; never a dispatcher.

The caller owns actual MCP request/response evidence, immutable packet identity,
source readback and one-run ordering. This module makes no model or Colab call.
Frozen statements are instrumented only at subprocess calls, with explicit narrow
log handles. Their original and executed-presentation hashes remain separate.
"""
import ast
import hashlib
import inspect
import json
from pathlib import Path
import re

from orchestrator import p001_runtime_setup as setup
from orchestrator import p001_runtime_intake as intake
from orchestrator.colab_patient import CPU_CELL

REQUEST_ID = 'p001-runtime-setup-20260908-v1'
STAGES = ('cpu', 'guard-and-claim', 'source-and-dependencies', 'default-child-environment')
STATUSES = ('CPU_COLAB_VERIFIED', 'EXCLUSIVE_SETUP_INTENT_CREATED',
            'SOURCE_DEPENDENCY_SETUP_COMPLETE', 'DEFAULT_CHILD_ENVIRONMENT_OBSERVED')
OPERATIONS = ('acquisition', 'dependencies', 'seven-zip')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require_claim(request):
    """Recheck ownership of the original exclusive claim without recreating it."""
    import json
    from pathlib import Path
    import stat
    root = Path(request['setup_root'])
    for path in [*reversed(root.parents), root, root/'intent.json']:
        if stat.S_ISLNK(path.lstat().st_mode):
            raise ValueError('TRANSPARENT_SETUP_CLAIM_SYMLINK')
    expected = {'status': 'SETUP_INTENT_NO_AUTOMATIC_RETRY',
        'request_id': request['request_id'],
        'runtime_fingerprint_sha256': request['runtime_fingerprint_sha256'],
        'binding_sha256': request['binding_sha256'], 'prediction_launch_authorized': False}
    if json.loads((root/'intent.json').read_text()) != expected:
        raise ValueError('TRANSPARENT_SETUP_CLAIM_CHANGED')


class Operation:
    """One fixed setup operation; original command streams stay in its private log."""
    def __init__(self, request, name, source_sha256, presentation_sha256):
        import json
        import os
        from pathlib import Path
        import time
        require_claim(request)
        if name not in ('acquisition', 'dependencies', 'seven-zip'):
            raise ValueError('TRANSPARENT_SETUP_OPERATION_SCOPE')
        self.request = request; self.name = name
        self.source_sha256 = source_sha256; self.presentation_sha256 = presentation_sha256
        self.root = Path(request['setup_root']); self.started = time.monotonic(); self.calls = 0; self.failed = False
        self.log = self.root/(name+'.console.log')
        if self.log.is_symlink() or not self.log.is_file() or self.log.stat().st_size:
            raise ValueError('TRANSPARENT_SETUP_LOG_RECONCILE')
        with (self.root/(name+'.operation-intent.json')).open('x') as handle:
            os.chmod(handle.name, 0o600)
            json.dump({'binding_sha256': request['binding_sha256'], 'operation': name,
                'source_sha256': source_sha256, 'presentation_sha256': presentation_sha256,
                'status': 'OPERATION_INTENT_NO_RETRY'}, handle)
            handle.flush(); os.fsync(handle.fileno())

    def _command(self, command, *, cwd=None, check=True, timeout=180, text=False, output=False):
        import os
        from pathlib import Path
        import re
        import subprocess
        import sys
        if self.failed:
            raise ValueError('TRANSPARENT_SETUP_FAILED_OPERATION_RECONCILE')
        if check is not True or timeout != 180 or not isinstance(command, list):
            raise ValueError('TRANSPARENT_SETUP_COMMAND_OPTIONS')
        source = self.request['source_root']
        if self.name == 'acquisition':
            expected = [
                (['git','init','-q',source], None, False),
                (['git','remote','add','origin','https://github.com/Moroseui/concept-research-scout.git'], source, False),
                (['git','config','remote.origin.fetch','+refs/heads/astra/autonomous-isles-pilot:refs/remotes/origin/astra/autonomous-isles-pilot'], source, False),
                (['git','fetch','--no-tags','--depth=1','origin','d6a1184b4378e849213fd887a6f7b103fb1a64d5'], source, False),
                (['git','checkout','--detach','d6a1184b4378e849213fd887a6f7b103fb1a64d5'], source, False),
                (['git','rev-parse','HEAD'], source, True),
                (['git','status','--porcelain','--untracked-files=all'], source, True)]
        elif self.name == 'dependencies':
            if not re.fullmatch(r'/usr/(?:local/)?bin/python[0-9.]*', str(Path(sys.executable).resolve())):
                raise ValueError('TRANSPARENT_SETUP_PYTHON_DOMAIN')
            expected = [([sys.executable,'-m','pip','install','-q','-r',source+'/campaigns/isles24-pilot/experiments/P001/requirements.txt'], None, False)]
        else:
            expected = [(['apt-get','-qq','update'], None, False),
                        (['apt-get','-qq','install','-y','p7zip-full'], None, False)]
        actual = (command, None if cwd is None else str(cwd), output)
        if self.calls >= len(expected) or actual != expected[self.calls] or text is not output:
            raise ValueError('TRANSPARENT_SETUP_COMMAND_NOT_FIXED')
        self.calls += 1
        self.failed = True  # Any exceptional exit poisons this operation; no retry.
        if self.log.is_symlink():
            raise ValueError('TRANSPARENT_SETUP_LOG_SYMLINK')
        # Only these particular subprocess handles are redirected. Python and
        # notebook stdout/stderr remain available for checked outcomes/errors.
        with self.log.open('ab', buffering=0) as log:
            os.chmod(log.name, 0o600)
            try:
                result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE if output else log,
                    stderr=log, timeout=timeout, check=False)
            except subprocess.TimeoutExpired as error:
                if output and isinstance(error.output, bytes):
                    log.write(error.output)
                raise ValueError('TRANSPARENT_SETUP_COMMAND_TIMEOUT_PRIVATE_LOG_PRESERVED') from None
            if output:
                raw = result.stdout
                if not isinstance(raw, bytes):
                    raise ValueError('TRANSPARENT_SETUP_COMMAND_OUTPUT_TYPE')
                log.write(raw)  # Preserve even an oversized original before refusing.
                if len(raw) > 16384:
                    raise ValueError('TRANSPARENT_SETUP_COMMAND_OUTPUT_BOUND')
            if result.returncode:
                raise ValueError('TRANSPARENT_SETUP_COMMAND_FAILED_PRIVATE_LOG_PRESERVED')
        returned = result.stdout.decode() if output else result
        self.failed = False
        return returned

    def run(self, command, **kwargs):
        return self._command(command, **kwargs)

    def check_output(self, command, **kwargs):
        return self._command(command, output=True, **kwargs)

    def finish(self):
        import json
        import os
        import time
        if self.failed:
            raise ValueError('TRANSPARENT_SETUP_FAILED_OPERATION_RECONCILE')
        if self.calls not in {'acquisition': (7,), 'dependencies': (1,), 'seven-zip': (0, 2)}[self.name]:
            raise ValueError('TRANSPARENT_SETUP_COMMAND_SEQUENCE_INCOMPLETE')
        record = {'operation': self.name, 'status': 'COMPLETE', 'returncode': 0,
            'command_count': self.calls, 'source_sha256': self.source_sha256,
            'presentation_sha256': self.presentation_sha256,
            'elapsed_seconds': round(time.monotonic()-self.started, 6), 'original_log_private': True}
        with (self.root/(self.name+'.operation-result.json')).open('x') as handle:
            os.chmod(handle.name, 0o600); json.dump(record, handle, sort_keys=True)
            handle.flush(); os.fsync(handle.fileno())
        return record


def readable(source):
    """Change only the subprocess call target; all frozen AST statements survive."""
    tree = ast.parse(source)
    class Instrument(ast.NodeTransformer):
        def visit_Call(self, node):
            self.generic_visit(node)
            if (isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == 'subprocess'):
                if node.func.attr not in ('run', 'check_output'):
                    raise ValueError('TRANSPARENT_SETUP_UNREVIEWED_SUBPROCESS_CALL')
                node.func.value.id = '_p001_operation'
            return node
    transformed = ast.fix_missing_locations(Instrument().visit(tree))
    rendered = ast.unparse(transformed)+'\n'
    # Mechanical equivalence check is part of preparation, not model judgment.
    restored = ast.parse(rendered)
    for node in ast.walk(restored):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name) and node.func.value.id == '_p001_operation'):
            node.func.value.id = 'subprocess'
    if ast.dump(restored, include_attributes=False) != ast.dump(ast.parse(source), include_attributes=False):
        raise ValueError('TRANSPARENT_SETUP_FROZEN_STATEMENTS_CHANGED')
    return rendered


def prepare(snapshot, prior_runtime_packet, prior_runtime_receipt, request_id=REQUEST_ID):
    if request_id != REQUEST_ID:
        raise ValueError('TRANSPARENT_SETUP_ORIGINAL_REQUEST_REQUIRED')
    original = setup.packet(snapshot, prior_runtime_packet, prior_runtime_receipt, request_id)
    notebook_raw = intake.git_bytes(intake.NOTEBOOK_PIN, 'campaigns/isles24-pilot/experiments/P001/colab_P001.ipynb')
    if sha(notebook_raw) != original['frozen_review']['notebook_sha256']:
        raise ValueError('TRANSPARENT_SETUP_FROZEN_NOTEBOOK_CHANGED')
    notebook = json.loads(notebook_raw)
    frozen_sources = [''.join(notebook['cells'][i]['source']) for i in (1, 3)]
    seven_zip = "import shutil, subprocess\nif shutil.which('7z') is None:\n    subprocess.run(['apt-get','-qq','update'],check=True,timeout=180)\n    subprocess.run(['apt-get','-qq','install','-y','p7zip-full'],check=True,timeout=180)\n"
    sources = [*frozen_sources, seven_zip]
    request = original['request']
    if [sha(s.encode()) for s in sources] != request['source_sha256']:
        raise ValueError('TRANSPARENT_SETUP_FROZEN_SOURCE_BINDING')
    presented = [readable(source) for source in sources]
    hashes = [sha(s.encode()) for s in presented]
    shared = '\n'.join([inspect.getsource(intake.runtime_observation), inspect.getsource(setup.check_observation),
        inspect.getsource(require_claim), 'request = '+repr(request)])
    claim = shared+'\n'+inspect.getsource(setup.claim_setup)+'\n'+"\n".join([
        "check_observation(runtime_observation(request['runtime_request']),request,source_absent=True)",
        'claim_setup(request)', 'require_claim(request)',
        "import json\nprint(json.dumps({'status':'EXCLUSIVE_SETUP_INTENT_CREATED','binding_sha256':request['binding_sha256'],'exclusive_intent_created':True,'patient_launch_authorized':False}))"])
    operations = [shared, inspect.getsource(Operation),
        "check_observation(runtime_observation(request['runtime_request']),request,source_absent=True)",
        'require_claim(request)', '_p001_outcomes = []']
    for name, source, original_sha, presentation_sha in zip(OPERATIONS, presented, request['source_sha256'], hashes):
        operations += ['# Readable frozen '+name+' statements; subprocess log instrumentation is separately bound.',
            '_p001_operation = Operation(request, '+repr(name)+', '+repr(original_sha)+', '+repr(presentation_sha)+')',
            source, '_p001_outcomes.append(_p001_operation.finish())']
    operations += ["check_observation(runtime_observation(request['runtime_request']),request,source_absent=False)",
        "import json\nprint(json.dumps({'status':'SOURCE_DEPENDENCY_SETUP_COMPLETE','binding_sha256':request['binding_sha256'],'operations':_p001_outcomes,'source_postcondition_verified':True,'patient_launch_authorized':False},sort_keys=True,allow_nan=False))"]
    # A readable triple-quoted child program avoids nested escaped exec payloads.
    child = inspect.getsource(setup.child_environment)
    if '"""' in child:
        child = child.replace('"""', "'''")
    environment = shared+'\n'+'\n'.join([inspect.getsource(setup.observe_environment),
        'import hashlib, json, re', 'SOURCE_ROOT = '+repr(setup.SOURCE_ROOT), 'SCOPE = '+repr(setup.SCOPE),
        inspect.getsource(setup.canonical), inspect.getsource(setup.sha), inspect.getsource(setup.validate_environment),
        "check_observation(runtime_observation(request['runtime_request']),request,source_absent=False)",
        'require_claim(request)', 'CHILD_ENVIRONMENT_SOURCE = r"""\n'+child+'"""',
        'environment = observe_environment(request, CHILD_ENVIRONMENT_SOURCE)', 'validate_environment(environment)',
        "print(json.dumps({'status':'DEFAULT_CHILD_ENVIRONMENT_OBSERVED','binding_sha256':request['binding_sha256'],'environment':environment},sort_keys=True,allow_nan=False))"])
    cells = [CPU_CELL, claim, '\n'.join(operations)+'\n', environment+'\n']
    for source in cells:
        compile(source, 'readable-p001-setup', 'exec')
    return {'version': 1, 'route': 'p001-transparent-setup/v1', 'request': request,
        'original_setup_packet_sha256': sha(canonical(original)), 'pins': original['pins'],
        'frozen_review': original['frozen_review'], 'renderer_source_sha256': sha(Path(__file__).read_bytes()),
        'presentation_sha256': hashes, 'cells': cells,
        'stages': [{'index': i, 'name': name, 'cell_sha256': sha(cells[i].encode())} for i, name in enumerate(STAGES)],
        'patient_launch_authorized': False, 'scientific_acceptance': False,
        'request_identity_preserved': True, 'maximum_run_calls': 4,
        'transport_requirement': 'Actual native MCP request/response evidence, exact source readback, ordered single execution and result validation before advancement; no automatic retry.'}


def validate_stage(packet, index, native_result):
    """Parse one actual native run result; the dispatcher proves its call/source binding."""
    if (type(index) is not int or index not in range(4) or type(packet.get('version')) is not int or packet.get('version') != 1
            or packet.get('route') != 'p001-transparent-setup/v1'
            or packet.get('maximum_run_calls') != 4 or len(packet.get('cells', [])) != 4
            or packet['request'].get('request_id') != REQUEST_ID
            or packet.get('patient_launch_authorized') is not False or packet.get('scientific_acceptance') is not False
            or packet.get('stages') != [{'index': i, 'name': n, 'cell_sha256': sha(packet['cells'][i].encode())}
                for i, n in enumerate(STAGES)]):
        raise ValueError('TRANSPARENT_SETUP_PACKET_SCHEMA')
    request = packet['request']
    binding = request.get('binding_sha256')
    fingerprint = request.get('runtime_fingerprint_sha256')
    if (not isinstance(binding, str) or not re.fullmatch('[0-9a-f]{64}', binding)
            or not isinstance(fingerprint, str) or not re.fullmatch('[0-9a-f]{64}', fingerprint)
            or request.get('source_root') != setup.SOURCE_ROOT
            or request.get('setup_root') != setup.SETUP_PARENT+'/p001-runtime-setup-0770c7dcabe7-'+fingerprint[:12]
            or binding != sha(canonical({k:v for k,v in request.items() if k != 'binding_sha256'}))
            or packet.get('renderer_source_sha256') != sha(Path(__file__).read_bytes())
            or not re.fullmatch('[0-9a-f]{64}', packet.get('original_setup_packet_sha256', ''))):
        raise ValueError('TRANSPARENT_SETUP_REQUEST_BINDING')
    if not isinstance(native_result, dict) or not isinstance(native_result.get('outputs'), list):
        raise ValueError('TRANSPARENT_SETUP_NATIVE_RESULT_REQUIRED')
    parts = []
    for output in native_result['outputs']:
        if not isinstance(output, dict) or output.get('output_type') != 'stream':
            raise ValueError('TRANSPARENT_SETUP_UNEXPECTED_OR_FAILED_OUTPUT')
        content = output.get('text')
        if isinstance(content, str): content = [content]
        if not isinstance(content, list) or any(not isinstance(t, str) for t in content):
            raise ValueError('TRANSPARENT_SETUP_STREAM_SCHEMA')
        parts.extend(content)
    raw = ''.join(parts)
    if len(raw.encode()) > (132096 if index == 3 else 8192):
        raise ValueError('TRANSPARENT_SETUP_RESULT_BOUND')
    try:
        value = json.loads(raw)
    except (ValueError, TypeError) as error:
        raise ValueError('TRANSPARENT_SETUP_RESULT_JSON') from error
    binding = packet['request']['binding_sha256']
    if index == 0:
        if value != {'cpu_only': True, 'colab_runtime': True} or any(type(v) is not bool for v in value.values()):
            raise ValueError('TRANSPARENT_SETUP_CPU_REQUIRED')
    elif index == 1:
        if value != {'status': STATUSES[index], 'binding_sha256': binding,
                'exclusive_intent_created': True, 'patient_launch_authorized': False} or value['exclusive_intent_created'] is not True or value['patient_launch_authorized'] is not False:
            raise ValueError('TRANSPARENT_SETUP_CLAIM_RESULT')
    elif index == 2:
        if (not isinstance(value, dict) or set(value) != {'status','binding_sha256','operations','source_postcondition_verified','patient_launch_authorized'}
                or value['status'] != STATUSES[index] or value['binding_sha256'] != binding
                or value['source_postcondition_verified'] is not True or value['patient_launch_authorized'] is not False
                or not isinstance(value['operations'], list) or len(value['operations']) != 3):
            raise ValueError('TRANSPARENT_SETUP_SOURCE_RESULT')
        for i, row in enumerate(value['operations']):
            if (not isinstance(row, dict) or set(row) != {'operation','status','returncode','command_count','source_sha256','presentation_sha256','elapsed_seconds','original_log_private'}
                    or row['operation'] != OPERATIONS[i] or row['status'] != 'COMPLETE'
                    or type(row['returncode']) is not int or row['returncode'] != 0
                    or type(row['command_count']) is not int or row['command_count'] not in [(7,), (1,), (0,2)][i]
                    or row['source_sha256'] != packet['request']['source_sha256'][i]
                    or row['presentation_sha256'] != packet['presentation_sha256'][i]
                    or type(row['elapsed_seconds']) not in (float,int) or not 0 <= row['elapsed_seconds'] <= 1800
                    or row['original_log_private'] is not True):
                raise ValueError('TRANSPARENT_SETUP_OPERATION_RESULT')
    else:
        if (not isinstance(value, dict) or set(value) != {'status','binding_sha256','environment'}
                or value['status'] != STATUSES[index] or value['binding_sha256'] != binding):
            raise ValueError('TRANSPARENT_SETUP_ENVIRONMENT_RESULT')
        setup.validate_environment(value['environment'])
    return {'stage': STAGES[index], 'index': index, 'status': STATUSES[index],
        'packet_sha256': sha(canonical(packet)), 'native_result_sha256': sha(canonical(native_result)),
        'cell_sha256': packet['stages'][index]['cell_sha256'], 'checked_outcome': value}


def final_receipt(packet, checked_outcomes, exchange_digest):
    """Assemble checked results; native exchange identity is supplied by the dispatcher."""
    if not isinstance(exchange_digest, str) or not re.fullmatch('[0-9a-f]{64}', exchange_digest):
        raise ValueError('TRANSPARENT_SETUP_NATIVE_EXCHANGE_DIGEST_REQUIRED')
    if not isinstance(checked_outcomes, list) or len(checked_outcomes) != 4:
        raise ValueError('TRANSPARENT_SETUP_COMPLETE_SEQUENCE_REQUIRED')
    for index, checked in enumerate(checked_outcomes):
        if (not isinstance(checked, dict) or set(checked) != {'stage','index','status','packet_sha256','native_result_sha256','cell_sha256','checked_outcome'}
                or checked['stage'] != STAGES[index] or checked['index'] != index
                or checked['status'] != STATUSES[index] or checked['packet_sha256'] != sha(canonical(packet))
                or checked['cell_sha256'] != packet['stages'][index]['cell_sha256']
                or not re.fullmatch('[0-9a-f]{64}', checked['native_result_sha256'])):
            raise ValueError('TRANSPARENT_SETUP_CHECKED_STAGE_BINDING')
        # Recheck the semantic value without claiming this reconstructed stream
        # is the original MCP result. The native digest above retains that identity.
        validate_stage(packet, index, {'outputs': [{'output_type':'stream','text':[canonical(checked['checked_outcome']).decode()]}]})
    environment = checked_outcomes[3]['checked_outcome']['environment']
    return {'status': 'SOURCE_DEPENDENCIES_AND_DEFAULT_CHILD_ENVIRONMENT_VERIFIED',
        'route': packet['route'], 'binding_sha256': packet['request']['binding_sha256'],
        'request_id': REQUEST_ID, 'packet_sha256': sha(canonical(packet)),
        'original_setup_packet_sha256': packet['original_setup_packet_sha256'],
        'native_exchange_sha256': exchange_digest, 'stages': checked_outcomes,
        'runtime_fingerprint_sha256': packet['request']['runtime_fingerprint_sha256'],
        'environment': environment, 'environment_sha256': sha(canonical(environment)),
        'patient_launch_authorized': False, 'scientific_acceptance': False}