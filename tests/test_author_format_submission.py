"""Synthetic-only tests of format feedback; no model, ledger or provider calls."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest
from orchestrator import author_format_submission as sub
from orchestrator.experiment_plan_validation import author_schema


def fixture(root):
    (root/sub.RUNTIME).mkdir(mode=0o700)
    original = root/sub.RUNTIME/'originals'
    original.mkdir(mode=0o700)
    plan = {'full_training': {'full_fits': [
        {'fit_id': 'synthetic-'+str(i), 'timing_fit_id': 'synthetic-smoke',
         'epochs': 1, 'fixed_seconds': '0', 'overhead_micro_usd': 0,
         'applicability_assumption': 'Synthetic fixture only.'} for i in range(40)]}}
    raw = sub.canonical(plan)
    files = {'execution.plan.json': raw,
             'SPEC.proposed.md': b'Synthetic spec\nexecution_plan_sha256: '+sub.sha(raw).encode()+b'\n',
             'notebook.patch.json': b'{"synthetic":true}'}
    refs = {}
    for name, body in files.items():
        for path in [original/name, root/name]:
            path.write_bytes(body)
            path.chmod(0o600)
        refs[name] = {'path': sub.RUNTIME+'/originals/'+name, 'sha256': sub.sha(body)}
    config = {'schema': 'item4-author5-format-submission/v1', 'bindings': {
        'run_id': 'experiment-a74959ac4546a982af4ae137', 'stage': 'run_spec_author', 'round': 5,
        'call_id': '1'*64, 'source_sha': '2'*40, 'runtime_sha256': '3'*64, 'input_sha256': '4'*64},
        'originals': refs, 'output_schema': author_schema()}
    raw = sub.canonical(config)
    (root/sub.CONFIG).write_bytes(raw)
    (root/sub.CONFIG).chmod(0o600)
    return sub.sha(raw), files


def author_correction(root, originals):
    # Synthetic author action in tests, never a production output repair.
    plan = json.loads(originals['execution.plan.json'])
    for row in plan['full_training']['full_fits']:
        row['assumption'] = row.pop('applicability_assumption')
    raw = sub.canonical(plan)
    (root/'execution.plan.json').write_bytes(raw)
    (root/'SPEC.proposed.md').write_bytes(originals['SPEC.proposed.md'].replace(
        sub.sha(originals['execution.plan.json']).encode(), sub.sha(raw).encode()))


def test_invalid_then_corrected_submission_uses_one_config_and_preserves_originals(tmp_path):
    pin, originals = fixture(tmp_path)
    with pytest.raises(ValueError, match='^AUTHOR_FIELD_NAME_CORRECTION_REQUIRED$'):
        sub.submit(tmp_path, pin, {})
    assert not (tmp_path/sub.RECORD).exists()
    author_correction(tmp_path, originals)
    answer = sub.submit(tmp_path, pin, {})
    assert answer['status'] == 'ACCEPTED'
    assert sub.verify(tmp_path, pin)['files'] == answer['files']
    for name, raw in originals.items():
        assert (tmp_path/sub.RUNTIME/'originals'/name).read_bytes() == raw
    with pytest.raises(ValueError, match='^AUTHOR_SECOND_SUBMISSION_REFUSED$'):
        sub.submit(tmp_path, pin, {})


@pytest.mark.parametrize('damage', ['scientific-value', 'bool-for-int', 'notebook', 'spec', 'original', 'duplicate-key'])
def test_out_of_scope_changes_and_bad_format_refuse_without_accepting(tmp_path, damage):
    pin, originals = fixture(tmp_path)
    author_correction(tmp_path, originals)
    if damage in {'scientific-value', 'bool-for-int'}:
        p = tmp_path/'execution.plan.json'
        value = json.loads(p.read_bytes())
        value['full_training']['full_fits'][0]['epochs'] = 2 if damage == 'scientific-value' else True
        p.write_bytes(sub.canonical(value))
    elif damage == 'notebook': (tmp_path/'notebook.patch.json').write_bytes(b'{"changed":true}')
    elif damage == 'spec': (tmp_path/'SPEC.proposed.md').write_bytes(b'Changed conclusion')
    elif damage == 'original': (tmp_path/sub.RUNTIME/'originals/notebook.patch.json').write_bytes(b'Changed original')
    else: (tmp_path/'execution.plan.json').write_bytes(b'{"a":1,"a":2}')
    with pytest.raises(ValueError):
        sub.submit(tmp_path, pin, {})
    assert not (tmp_path/sub.RECORD).exists()


def test_accepted_output_cannot_change(tmp_path):
    pin, originals = fixture(tmp_path)
    author_correction(tmp_path, originals)
    sub.submit(tmp_path, pin, {})
    (tmp_path/'notebook.patch.json').write_bytes(b'Changed after acceptance')
    with pytest.raises(ValueError): sub.verify(tmp_path, pin)


def test_stdio_returns_errors_then_accepts_in_same_process(tmp_path):
    pin, originals = fixture(tmp_path)
    process = subprocess.Popen([sys.executable, '-I', '-B', str(Path(sub.__file__)), pin],
        cwd=tmp_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    def call(ident):
        request = {'jsonrpc': '2.0', 'id': ident, 'method': 'tools/call',
                   'params': {'name': 'submit_author', 'arguments': {}}}
        process.stdin.write(json.dumps(request)+'\n'); process.stdin.flush()
        return json.loads(process.stdout.readline())
    try:
        first = call(1)['result']
        assert first['isError'] is True
        assert json.loads(first['content'][0]['text'])['validation_error'] == 'AUTHOR_FIELD_NAME_CORRECTION_REQUIRED'
        assert not (tmp_path/sub.RECORD).exists()
        author_correction(tmp_path, originals)
        second = call(2)['result']
        assert second['isError'] is False
        assert json.loads(second['content'][0]['text'])['status'] == 'ACCEPTED'
        assert sub.verify(tmp_path, pin)['bindings']['round'] == 5
    finally:
        process.stdin.close()
        assert process.wait(timeout=10) == 0, process.stderr.read()


def prepared(root):
    source = root/'synthetic-source'
    source.mkdir(mode=0o700)
    pin, originals = fixture(source)
    config = sub.load(source, pin)
    work = root/'workspace'
    work.mkdir(mode=0o700)
    pins = sub.prepare(work, config['bindings'], originals, config['output_schema'])
    return work, pins


def test_native_readonly_runtime_and_writable_outputs(tmp_path):
    work, pins = prepared(tmp_path)
    script = """from pathlib import Path
import errno,os
root=Path('/workspace')
for directory in ['.author-runtime','.author-runtime/originals']:
 try:
  fd=os.open(root/directory/'new-synthetic-probe',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 except OSError as error:
  assert error.errno==errno.EROFS
 else:
  os.close(fd);raise AssertionError('runtime was writable')
(root/'synthetic-output.txt').write_text('allowed output')
print('READONLY_RUNTIME_WRITABLE_OUTPUTS')
"""
    command = ['/usr/bin/bwrap', '--unshare-user', '--unshare-pid', '--unshare-net',
        '--tmpfs', '/', '--ro-bind', '/usr', '/usr', '--symlink', 'usr/lib', '/lib',
        '--symlink', 'usr/lib', '/lib64', '--bind', str(work), '/workspace', '--chdir', '/workspace',
        '--', '/usr/bin/python3', '-I', '-B', '-c', script]
    protected = sub.protect_command(command, work, pins)
    result = subprocess.run(protected, capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == 'READONLY_RUNTIME_WRITABLE_OUTPUTS'
    assert (work/'synthetic-output.txt').read_text() == 'allowed output'
    sub.check_runtime(work, pins)


def test_command_adapter_preserves_every_existing_sandbox_option(tmp_path):
    work, pins = prepared(tmp_path)
    original = ['/tools/node', '/tools/codex/bin/codex.js', 'exec', '--ignore-user-config',
        '--ignore-rules', '--model', 'gpt-6-astra', '-s', 'workspace-write', '-c',
        'approval_policy="never"', '-c', 'sandbox_workspace_write.network_access=false', '--json', '-']
    updated = sub.client_command(original, work, pins)
    assert updated[:len(original)-1] == original[:-1]
    assert updated[-1] == original[-1]
    assert updated[len(original)-1] == '-c'
    assert pins[sub.CONFIG] in updated[-2]
    (work/sub.SERVER).write_text('changed')
    with pytest.raises(ValueError, match='^AUTHOR_RUNTIME_CHANGED$'):
        sub.client_command(original, work, pins)


def test_unknown_outer_layout_and_duplicate_preparation_refuse(tmp_path):
    work, pins = prepared(tmp_path)
    with pytest.raises(ValueError, match='^AUTHOR_OUTER_COMMAND_BINDING$'):
        sub.protect_command(['/usr/bin/python3'], work, pins)
    config = sub.load(work, pins[sub.CONFIG])
    originals = {name: sub.regular(work/ref['path']) for name,ref in config['originals'].items()}
    with pytest.raises(FileExistsError):
        sub.prepare(work, config['bindings'], originals, config['output_schema'])
