"""Exact author5 terminal evidence; qualification is not scientific acceptance."""
import hashlib
import json
from pathlib import Path

CALL = '49cc364b033bf52198fbc44c5470bb72b9cfec03826294f71f2dd2286d244524'
AUTHORITY = 'a9ded8872a67385ab3a47f95a39914271ba8f4de9a8f8015c197bb7be35c4ef6'
BINDINGS = 'ffab135633077d63c275b81ac936368d207d0555ecda48a4e2b5ccb16e489372'
UNIT = 'research-item4-author-submission-20261008.service'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(v): return json.dumps(v, sort_keys=True, separators=(',', ':')).encode()
def require(ok, why):
    if not ok: raise ValueError('AUTHOR5_RECOVERY_' + why)

def binding():
    root = Path(__file__).resolve().parents[1]
    raw = (root/'docs/ITEM4_AUTHOR5_RECOVERY_BINDINGS.json').read_bytes()
    require(sha(raw) == BINDINGS, 'BINDING_CHANGED')
    require(sha((root/'docs/ITEM4_AUTHOR5_RECOVERY_APPROVAL_20261008.txt').read_bytes()) == AUTHORITY, 'AUTHORITY_CHANGED')
    b = json.loads(raw)
    require(b['authority_sha256'] == AUTHORITY and b['call'] == CALL, 'AUTHORITY_BINDING')
    return b

def terminal(row, bodies):
    b = binding()
    require(sha(canonical(dict(row))) == b['global_row_sha256'] and
            row['id'] == CALL and row['status'] == 'UNCERTAIN', 'ORIGINAL_CHARGE_CHANGED')
    require(set(bodies) == set(b['native_files']) and
            all(sha(bodies[n]) == pin for n, pin in b['native_files'].items()), 'NATIVE_EVIDENCE_CHANGED')
    native = [json.loads(x) for x in bodies['stage_provenance.jsonl'].splitlines() if x.strip()]
    require(len(native) == 1, 'ONE_INVOCATION')
    p = native[0]
    require(p['stage'] == 'run_spec_author' and p['exit_class'] == 'ok' and
            p['family_effective'] == 'codex' and p['fallback'] is False and
            p['attempts'] == [{'model':'gpt-6-astra','returncode':0}] and
            p['prompt_sha256'] == b['input'] == sha(bodies['prompt.md']) and
            json.loads(bodies['sent-input.json'])['input_sha256'] == b['input'], 'NATIVE_INPUT_BINDING')
    events = []
    for line in bodies['console.log'].splitlines():
        try: event = json.loads(line)
        except ValueError: continue
        if isinstance(event, dict): events.append(event)
    completed = [x['item'] for x in events if x.get('type') == 'item.completed']
    writes = [x for x in completed if x.get('id') == 'item_4' and x.get('type') == 'command_execution']
    require(len(writes) == 1 and writes[0]['exit_code'] == 0 and writes[0]['status'] == 'completed', 'AUTHOR_WRITE_EVENT')
    for name, pin in b['outputs'].items():
        lines = writes[0]['aggregated_output'].splitlines()
        matches = [x.split() for x in lines if x.startswith(name+' ')]
        require(len(matches) == 1 and len(matches[0]) == 3 and matches[0][2] == pin, 'AUTHOR_STREAM_OUTPUT_BINDING')
    calls = [x for x in completed if x.get('type') == 'mcp_tool_call']
    require(calls == [{'id':'item_5','type':'mcp_tool_call','server':'author_format',
        'tool':'submit_author','arguments':{},'result':None,
        'error':{'message':'MCP tool call requires approval, but approval policy is never'},
        'status':'failed'}], 'EXACT_SUBMISSION_REFUSAL')
    require(events[-1].get('type') == 'turn.completed', 'TERMINAL_STREAM')
    return {'call':CALL, 'authority_sha256':AUTHORITY, 'console_sha256':b['native_files']['console.log'],
            'output_sha256':b['outputs'], 'original_status':'UNCERTAIN', 'native_submission':'REFUSED_NO_RECEIPT'}

def local_rows(rows):
    b = binding()
    indexed = {x['id']:dict(x) for x in rows}
    require(all(i in indexed and sha(canonical(indexed[i])) == pin for i,pin in b['local_rows'].items()), 'ORIGINAL_LOCAL_CALL_CHANGED')
    return b


def outputs(work, row):
    from orchestrator import author_format_submission as af
    work = Path(work); b = binding()
    require(str(work.resolve()) == b['workspace'], 'WORKSPACE_SCOPE')
    require(not (work/af.RECORD).exists() and not (work/af.RECORD).is_symlink(), 'NO_FABRICATED_SUBMISSION')
    evidence = terminal(row, {n:af.regular(work/n, 200000) for n in b['native_files']})
    af.check_runtime(work, b['runtime_pins'])
    actual = af.validate(work, af.load(work, b['runtime_pins'][af.CONFIG]))
    require(actual == b['outputs'], 'PRESERVED_OUTPUT_CHANGED')
    return evidence
