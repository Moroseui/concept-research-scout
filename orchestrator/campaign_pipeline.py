"""Campaign authoring/discussion proposals through the existing receipted agents.

Never edits an executable experiment or claims human ratification. Adoption is a
separate specification/decision/review transaction, preserving live experiment pins.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
from datetime import datetime,timezone
import tempfile
import shutil
import os
from orchestrator.campaign_lifecycle import run_isolated_stage
from orchestrator.publication import inventory

MODES={'propose':['proposal.md'],'specify':['SPEC.proposed.md'],
       'code':['run.proposed.py'],'repair':['repair.md','run.proposed.py'],
       'discuss':['discussion.md']}


def system_stage(sc,directory,family,stage,body,names):
    """Reuse the existing primitive with a future-job profile, not live AGENTS.toml."""
    if os.environ.get('SCOUT_CI'):raise ValueError('campaign subscription stages refuse CI execution')
    original=sc.ROOT
    profile=Path(original)/'configs/pilot/agents-unattended.toml'
    config_root=Path(tempfile.mkdtemp(prefix='campaign-profile-'))
    shutil.copy2(profile,config_root/'AGENTS.toml')
    (directory/('profile_'+stage+'.json')).write_text(json.dumps({'profile_sha256':hashlib.sha256((config_root/'AGENTS.toml').read_bytes()).hexdigest(),'profile_source':'configs/pilot/agents-unattended.toml','stage':stage}))
    try:
        sc.ROOT=config_root
        return run_isolated_stage(sc,directory,family,stage,body,names)
    finally:sc.ROOT=original


def grounding(root,experiment):
    if experiment not in ['P001','P002','P003']:raise ValueError('campaign scope exceeded')
    base=Path(root)/'campaigns/isles24-pilot';exp=base/'experiments'/experiment
    # No future scientific proposal before the reviewed predecessor interpretation.
    if experiment!='P001':
        prior=base/'experiments'/f'P{int(experiment[1:])-1:03d}'
        for name in ['interpretation_receipt.json','import_receipt.json','interpretation.md','interpret_review.md','investigator_next_decision.json','SPEC.md']:
            if (prior/name).is_symlink():raise ValueError('symlink predecessor')
        r=json.loads((prior/'interpretation_receipt.json').read_text())
        if r.get('status')!='AGENT_REVIEWED_NOT_HUMAN_RATIFIED':raise ValueError('predecessor not reviewed')
        for key,name in [('import_receipt_sha256','import_receipt.json'),('interpretation_sha256','interpretation.md'),('review_sha256','interpret_review.md'),('proposal_sha256','investigator_next_decision.json')]:
            if r.get(key)!=hashlib.sha256((prior/name).read_bytes()).hexdigest():raise ValueError('predecessor binding stale')
        imported=json.loads((prior/'import_receipt.json').read_text())
        if imported.get('spec_sha256')!=hashlib.sha256((prior/'SPEC.md').read_bytes()).hexdigest():raise ValueError('predecessor specification changed')
    files={base/'CAMPAIGN.md'}
    if experiment!='P001':files.add(prior/'interpretation_receipt.json')
    for name in ['SPEC.md','run.py','publication.json']:
        if (exp/name).is_file():files.add(exp/name)
    if (exp/'import_receipt.json').exists():
        if (exp/'import_receipt.json').is_symlink():raise ValueError('symlink import receipt')
        r=json.loads((exp/'import_receipt.json').read_text());bundle=Path(root)/r['bundle']
        for key,name in [('spec_sha256','SPEC.md'),('review_sha256','review.json')]:
            if r.get(key)!=hashlib.sha256((exp/name).read_bytes()).hexdigest():raise ValueError('current import binding stale')
        if bundle.is_symlink() or not bundle.resolve().is_relative_to((exp/'results').resolve()):raise ValueError('unsafe bundle')
        if inventory(bundle)!=r['bundle_file_sha256']:raise ValueError('aggregate import changed')
        files.update(bundle/name for name in r['bundle_file_sha256'])
    result={}
    for f in sorted(files):
        if f.is_symlink():raise ValueError('symlink input')
        result[f.relative_to(root).as_posix()]=f.read_text()
    return result


def execute(sc,mode,experiment,request,output):
    if mode not in MODES:raise ValueError('unknown stage')
    output=Path(output)
    permitted=Path(sc.ROOT)/'campaigns/isles24-pilot/pipeline'
    for parent in [permitted,*permitted.parents]:
        if parent.is_symlink():raise ValueError('symlink pipeline ancestor')
        if parent==Path(sc.ROOT):break
    if not output.resolve().is_relative_to(permitted.resolve()) or output.is_symlink():raise ValueError('pipeline output outside campaign')
    output.mkdir(parents=True,exist_ok=False)
    try:context=grounding(sc.ROOT,experiment)
    except BaseException as e:
        (output/'blocked.json').write_text(json.dumps({'status':'BLOCKED','failure_type':type(e).__name__,'reason':'GROUNDING_FAILED'}))
        raise
    binding={k:hashlib.sha256(v.encode()).hexdigest() for k,v in context.items()}
    (output/'request.json').write_text(json.dumps({'mode':mode,'experiment':experiment,'request':request,'input_sha256':binding,'actor_type':'agent','family':'codex','authority':'campaign_delegated_investigator','status':'PROPOSAL_ONLY'},indent=2))
    body='You are the system campaign '+mode+' author. Produce a bounded proposal, not an approval or executable amendment. Preserve original experiment pins. No patient data, execution, remote writes, or human ratification. All scientific work is exploratory.\nREQUEST: '+request+'\nBOUND CONTEXT:\n'+json.dumps(context)
    try:
        for round in [1,2]:
            directory=output/f'round-{round}';directory.mkdir()
            author=system_stage(sc,directory,'codex','campaign_'+mode,body,MODES[mode])
            proposal='\n'.join(name+'\n'+(directory/name).read_text() for name in MODES[mode])
            if (directory/'review.json').exists():raise ValueError('author may not prepopulate reviewer output')
            reviewer=system_stage(sc,directory,'claude','campaign_'+mode+'_review',
                'Review this campaign proposal against its context. Write review.json with exactly verdict (APPROVE or REVISE) and rationale (nonempty string). Do not ratify or execute.\n'+body+'\nPROPOSAL:\n'+proposal,['review.json'])
            review=json.loads((directory/'review.json').read_text())
            if set(review)!={'verdict','rationale'} or review['verdict'] not in ['APPROVE','REVISE'] or not isinstance(review['rationale'],str) or not review['rationale'].strip():raise ValueError('malformed review')
            if author.get('family_effective')!='codex' or reviewer.get('family_effective')!='claude' or any(r.get('exit_class')!='ok' or r.get('ci') for r in [author,reviewer]):raise ValueError('opposing-family successful receipts required')
            if review['verdict']=='APPROVE':
                receipt={'status':'REVIEWED_PROPOSAL_NOT_ADOPTED','mode':mode,'experiment':experiment,'input_sha256':binding,'round':round,'artifact_sha256':{p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir() if p.is_file()},'author_family':'codex','reviewer_family':'claude'}
                (output/'receipt.json').write_text(json.dumps(receipt,indent=2));return receipt
            body+='\nPRIOR PROPOSAL:\n'+proposal+'\nREPAIR REQUIRED:\n'+review['rationale']
        raise ValueError('review revision limit reached')
    except BaseException as e:
        (output/'blocked.json').write_text(json.dumps({'status':'BLOCKED','failure_type':type(e).__name__,'human_decision':'Inspect preserved stage evidence; do not treat partial output as approved.'}))
        raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=MODES);p.add_argument('--experiment',choices=['P001','P002','P003'],required=True)
    p.add_argument('--request',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    import scout
    print(json.dumps(execute(scout,a.mode,a.experiment,a.request,a.output),indent=2))
