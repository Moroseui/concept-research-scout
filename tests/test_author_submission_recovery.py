import copy
import json
import subprocess
import sys
from pathlib import Path
import pytest
from orchestrator import author_format_submission as af, author_submission_recovery as recovery
from test_author_format_submission import fixture


def test_truthful_metadata_uses_actual_pinned_native_classifier(tmp_path):
    pin, _ = fixture(tmp_path)
    result = subprocess.run([sys.executable, '-I', '-B', af.__file__, pin], cwd=tmp_path,
        input=json.dumps({'jsonrpc':'2.0','id':1,'method':'tools/list'})+'\n',
        capture_output=True, text=True, check=True)
    tools = json.loads(result.stdout)['result']['tools']
    assert len(tools) == 1 and tools[0]['name'] == 'submit_author'
    hints = tools[0]['annotations']
    assert hints == {'readOnlyHint':False, 'destructiveHint':False, 'openWorldHint':False, 'idempotentHint':False}
    # Exact native function from openai/codex rust-v0.153.4, mcp_tool_call.rs.
    # The production caller's Never branch refuses when this function is true.
    native = Path(__file__).parent/'fixtures/codex-0.153.4-mcp-approval.rs'
    assert af.sha(native.read_bytes()) == '4e8c4cb6989418c0a0eef760df3d87770959b44a8fffcf3bdb3cc01200b42a34'
    struct = '#[derive(Default)] struct ToolAnnotations { destructive_hint: Option<bool>, read_only_hint: Option<bool>, open_world_hint: Option<bool> }\n'
    harness = """
fn main() {
    let truth = ToolAnnotations { destructive_hint: Some(false), read_only_hint: Some(false), open_world_hint: Some(false) };
    assert!(!requires_mcp_tool_approval(Some(&truth)));
    assert!(requires_mcp_tool_approval(None));
    assert!(requires_mcp_tool_approval(Some(&ToolAnnotations::default())));
    assert!(requires_mcp_tool_approval(Some(&ToolAnnotations { destructive_hint: Some(true), ..truth })));
    assert!(requires_mcp_tool_approval(Some(&ToolAnnotations { destructive_hint: Some(false), read_only_hint: Some(false), open_world_hint: None })));
    println!("bounded tool classified safe; missing/unknown/destructive metadata still requires approval and Never refuses");
}
"""
    source = tmp_path/'native.rs'; source.write_text(struct+native.read_text()+harness)
    binary = tmp_path/'native'
    subprocess.run(['rustc', str(source), '-o', str(binary)], check=True, capture_output=True)
    subprocess.run([str(binary)], check=True, capture_output=True)
    assert 'approval_policy="never"' in (Path(__file__).parents[1]/'tools/item4_author_submission_component.py').read_text()


def evidence(monkeypatch):
    b = copy.deepcopy(recovery.binding())
    row = {'id':recovery.CALL,'status':'UNCERTAIN','charge':1}
    p = {'stage':'run_spec_author','exit_class':'ok','family_effective':'codex','fallback':False,
         'attempts':[{'model':'gpt-6-astra','returncode':0}],'prompt_sha256':af.sha(b'prompt')}
    b['input'] = p['prompt_sha256']
    events = [
      {'type':'item.completed','item':{'id':'item_4','type':'command_execution','exit_code':0,'status':'completed',
        'aggregated_output':'\n'.join(n+' 1 '+pin for n,pin in b['outputs'].items())}},
      {'type':'item.completed','item':{'id':'item_5','type':'mcp_tool_call','server':'author_format','tool':'submit_author',
        'arguments':{},'result':None,'error':{'message':'MCP tool call requires approval, but approval policy is never'},'status':'failed'}},
      {'type':'turn.completed'}]
    bodies = {'prompt.md':b'prompt','console.log':b'\n'.join(af.canonical(x) for x in events),
       'stage_provenance.jsonl':af.canonical(p),'sent-input.json':af.canonical({'input_sha256':b['input']}),'isolation-live.json':b'{}'}
    b['global_row_sha256'] = af.sha(af.canonical(row)); b['native_files'] = {n:af.sha(raw) for n,raw in bodies.items()}
    monkeypatch.setattr(recovery, 'binding', lambda:b)
    return b,row,bodies,events


def test_exact_terminal_qualification_preserves_refusal(monkeypatch):
    b,row,bodies,_ = evidence(monkeypatch)
    before = copy.deepcopy((row,bodies))
    out = recovery.terminal(row,bodies)
    assert out['native_submission'] == 'REFUSED_NO_RECEIPT'
    assert (row,bodies) == before


@pytest.mark.parametrize('damage',['row','stream','input','failure','multiple','hash-output','exit','nonterminal','missing'])
def test_unknown_or_changed_evidence_refused(monkeypatch, damage):
    b,row,bodies,events = evidence(monkeypatch)
    if damage == 'row': row['charge'] = 0
    elif damage == 'stream': bodies['console.log'] += b'changed'
    elif damage == 'missing': bodies.pop('isolation-live.json')
    else:
        if damage == 'input':
            value = json.loads(bodies['sent-input.json']);value['input_sha256']='0'*64;bodies['sent-input.json']=af.canonical(value)
        elif damage == 'exit':
            value=json.loads(bodies['stage_provenance.jsonl']);value['attempts'][0]['returncode']=1;bodies['stage_provenance.jsonl']=af.canonical(value)
        else:
            if damage == 'failure': events[1]['item']['error']['message']='different failure'
            if damage == 'multiple': events.insert(1,copy.deepcopy(events[1]))
            if damage == 'hash-output': events[0]['item']['aggregated_output']='wrong'
            if damage == 'nonterminal': events.pop()
            bodies['console.log']=b'\n'.join(af.canonical(x) for x in events)
        # Even with an altered test pin, semantic checks reject these failures.
        b['native_files']={n:af.sha(raw) for n,raw in bodies.items()}
    with pytest.raises((ValueError,KeyError)): recovery.terminal(row,bodies)


def test_local_originals_never_relabelled(monkeypatch):
    b,_,_,_=evidence(monkeypatch)
    rows=[{'id':x,'status':'UNCERTAIN','attempt':i} for i,x in enumerate(b['local_rows'])]
    b['local_rows']={r['id']:af.sha(af.canonical(r)) for r in rows}
    recovery.local_rows(rows)
    rows[-1]['status']='COMPLETE'
    with pytest.raises(ValueError,match='ORIGINAL_LOCAL_CALL_CHANGED'):recovery.local_rows(rows)
