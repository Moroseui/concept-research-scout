#!/usr/bin/env python3
"""Read execution receipts and write advisory proposals. Never apply proposals."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def review(root):
    receipts=[]; evidence=[]; malformed=0
    for path in sorted(Path(root).glob('ideas/*/stage_provenance.jsonl')):
        raw=path.read_bytes(); evidence.append({'path':path.relative_to(root).as_posix(),'sha256':hashlib.sha256(raw).hexdigest()})
        for line in raw.decode().splitlines():
            try: receipts.append(json.loads(line))
            except (ValueError,TypeError): malformed+=1
    failure=Counter(r['exit_class'] for r in receipts if r.get('exit_class') not in (None,'ok'))
    unknown_exit=sum(r.get('exit_class') is None for r in receipts)
    repeats=Counter((r.get('prompt_sha256'),r.get('stage')) for r in receipts if r.get('prompt_sha256'))
    duplicate_attempts=sum(n-1 for n in repeats.values() if n>1)
    durations=[r['duration_s'] for r in receipts if isinstance(r.get('duration_s'),(int,float))]
    missing_human=sum(r.get('human_intervention_minutes') is None for r in receipts)
    proposals=[]
    def add(friction,support,benefit,verification):
        proposals.append({'status':'PROPOSAL_ONLY','observed_friction':friction,'supporting_evidence':support,'expected_benefit':benefit,'verification_method':verification})
    if failure:
        add('Receipted non-successful agent invocations',dict(failure),'Avoid rerunning completed legs when a later leg fails','Compare completion-resume behavior and failed-leg count on a synthetic interrupted two-family stage; preserve review gates')
    if unknown_exit:
        add('Legacy receipt exit status unavailable',{'unknown_exit_status':unknown_exit},'Avoid classifying missing measurements as failures','Keep unknown separate from failed/successful receipts; backfill only from original logs when demonstrable')
    if duplicate_attempts:
        add('Repeated identical prompt/stage invocation',{'extra_attempts':duplicate_attempts},'Determine which repeats are recoverable work; do not assume all repeats are waste','Inspect matching receipt pairs and required-output hashes; propose resume only when prior valid output is bound to unchanged inputs')
    if missing_human:
        add('Human intervention time unavailable',{'receipts_without_measurement':missing_human},'Measure actual operator friction before prioritizing further automation','Offer an optional elapsed-intervention field; verify unknown stays null and known measurements have provenance')
    if malformed: add('Malformed receipt lines',{'count':malformed},'Preserve machine-readable operational evidence','Round-trip future receipt schemas; retain malformed originals as evidence')
    return {'mode':'proposal_only','receipt_count':len(receipts),'observed_agent_duration_s':sum(durations),'duration_available_count':len(durations),'cost_usd':None,'token_usage':None,'evidence':evidence,'proposals':proposals}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--root',type=Path,default=Path('.')); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
    result=review(args.root); args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(f"{result['receipt_count']} receipts; {len(result['proposals'])} proposals; no changes applied")
