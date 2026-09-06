"""Bind completed external review evidence to the campaign's executable sources."""
import json
from pathlib import Path
from orchestrator.campaign import sha


def required_files(root, experiment='P001'):
    base=f'campaigns/isles24-pilot/experiments/{experiment}/'
    return {'AGENTS.toml','scout.py','orchestrator/campaign.py','orchestrator/campaign_review.py',
            'orchestrator/campaign_lifecycle.py','orchestrator/publication.py','scripts/package_pilot.py',
            'campaigns/isles24-pilot/CAMPAIGN.md','tests/test_campaign.py',
            'tests/test_campaign_lifecycle.py','tests/test_campaign_review.py',
            'tests/test_pilot_notebook_acquisition.py',f'tests/test_prediction_{experiment.lower()}.py'} | {base+n for n in
            ('SPEC.md','run.py','validate_return.py','investigator_decision.json','publication.json','requirements.txt')}


def verdict(response):
    if response.get('is_error') or response.get('subtype')!='success':
        raise ValueError('incomplete or failed external review')
    body=response.get('result','')
    decoder=json.JSONDecoder(); found=[]
    for i,c in enumerate(body):
        if c=='{':
            try:
                obj,end=decoder.raw_decode(body[i:])
                if isinstance(obj,dict) and 'verdict' in obj and 'reviewed_commit' in obj: found.append(obj)
            except ValueError: pass
    if len(found)!=1: raise ValueError('ambiguous or missing external review verdict')
    found=found[0]
    if found.get('verdict')!='APPROVE' or found.get('blocking_findings')!=[]:
        raise ValueError('completed external approval with no blockers required')
    return found


def evidence(root,execution,response,experiment='P001'):
    root=Path(root)
    for path in (execution,response):
        if path.is_symlink() or not path.resolve().is_relative_to((root/'docs/isles-pilot/reviews').resolve()):
            raise ValueError('review evidence must be a regular versioned review artifact')
    e=json.loads(execution.read_text()); r=json.loads(response.read_text()); v=verdict(r)
    if e.get('returncode')!=0 or e.get('reviewed_commit')!=v['reviewed_commit'] or v.get('scope')!=experiment.lower():
        raise ValueError('external review scope/revision/exit mismatch')
    if 'claude-fable-5' not in r.get('modelUsage',{}) or e.get('response_sha256')!=sha(response):
        raise ValueError('actual reviewer identity or response integrity missing')
    files=e['input_file_sha256']
    needed=required_files(root,experiment)
    if not needed.issubset(files) or any(sha(root/f)!=files[f] for f in needed):
        raise ValueError('review does not bind every current executable dependency')
    return e,v,{f:files[f] for f in sorted(needed)}


def make_receipt(root,exp,execution,response):
    e,v,files=evidence(root,execution,response,exp.name)
    return {'actor_type':'agent','family':'claude','model':'claude-fable-5','verdict':'APPROVE',
            'reviewed_commit':v['reviewed_commit'],'spec_sha256':sha(exp/'SPEC.md'),'code_sha256':sha(exp/'run.py'),
            'decision_sha256':sha(exp/'investigator_decision.json'),'file_sha256':files,
            'execution':execution.relative_to(root).as_posix(),'execution_sha256':sha(execution),
            'response':response.relative_to(root).as_posix(),'response_sha256':sha(response)}


def verify_receipt(root,exp,receipt):
    execution=root/receipt['execution']; response=root/receipt['response']
    expected=make_receipt(root,exp,execution,response)
    if expected!=receipt: raise ValueError('review receipt differs from completed external evidence')
