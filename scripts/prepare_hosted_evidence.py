"""Prepare a source comparison and effective-tool evidence amendment; no model call."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from orchestrator.git_publication import scan


def prepare(originals,root):
    originals=Path(originals);root=Path(root)
    complete=json.loads((originals/'complete.json').read_text())
    pins=[complete['execution_source'],complete['source']]
    names=['orchestrator/remote_supervisor.py','orchestrator/operations_report.py','campaigns/isles24-pilot/colab/smoke.py','orchestrator/job_store.py','orchestrator/public_export.py','orchestrator/git_publication.py']
    comparisons={}
    for name in names:
        hashes={p:hashlib.sha256(subprocess.check_output(['git','show',p+':'+name],cwd=root)).hexdigest() for p in pins}
        comparisons[name]={'sha256_by_source':hashes,'identical':len(set(hashes.values()))==1}
    receipt=json.loads((originals/'review.receipt.json').read_text());raw=(originals/'review.stdout').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=receipt['stdout_sha256']:raise ValueError('REVIEW_PROTOCOL_CHANGED')
    init=next(e for e in map(json.loads,raw.decode().splitlines()) if e.get('type')=='system' and e.get('subtype')=='init')
    evidence={'amends_report_evidence':complete['report'],'execution_source':pins[0],'reporting_source':pins[1],
      'implementation_comparison':comparisons,'claude_effective_configuration':{k:init.get(k) for k in ['tools','mcp_servers','model','permissionMode']},
      'astra_model_identity':'gpt-6-astra was explicitly requested with no fallback; resolved identity is not independently reported by the captured protocol',
      'original_review_preserved':True,'model_call':False,'new_review_or_approval':False}
    raw=json.dumps(evidence,indent=2)+'\n';scan('source-tool-evidence.json',raw.encode());return raw

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--originals',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    raw=prepare(a.originals,a.root)
    with a.output.open('x') as f:f.write(raw)
