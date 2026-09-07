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

MODES={'charter':['CHARTER.proposed.md','RUBRIC.proposed.md','P001_ADOPTION.proposed.md','PROMPTS.proposed.md'],
       'readiness':['readiness.md','launch_decision.proposed.json'],
       'adoption':['adoption.proposed.md'],
       'propose':['proposal.md'],'specify':['SPEC.proposed.md'],
       'code':['run.proposed.py'],'repair':['repair.md','run.proposed.py'],
       'discuss':['discussion.md'], 'brief':['actions.md'], 'curate':['curation.md'], 'interpret':['interpretation.md','investigator_next_decision.json']}


def system_stage(sc,directory,family,stage,body,names):
    """Single-writer process only: this primitive temporarily changes sc.ROOT.

    Model stages must not run in readiness_queue threads. CI retains its own
    separately reviewed profile/provenance adapter.
    """
    if os.environ.get('SCOUT_CI'):
        from orchestrator.actions_runner import system_stage as hosted_stage
        return hosted_stage(sc,directory,family,stage,body,names)
    original=sc.ROOT
    profile=Path(original)/'configs/pilot/agents-unattended.toml'
    config_root=Path(tempfile.mkdtemp(prefix='campaign-profile-'))
    shutil.copy2(profile,config_root/'AGENTS.toml')
    (directory/('profile_'+stage+'.json')).write_text(json.dumps({'profile_sha256':hashlib.sha256((config_root/'AGENTS.toml').read_bytes()).hexdigest(),'profile_source':'configs/pilot/agents-unattended.toml','stage':stage}))
    try:
        sc.ROOT=config_root
        return run_isolated_stage(sc,directory,family,stage,body,names)
    finally:
        sc.ROOT=original
        shutil.rmtree(config_root)


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
    for name in ['CURRENT_STATUS.md','047_LIFECYCLE.md']:
        f=Path(root)/'docs/isles-pilot'/name
        if f.is_file():files.add(f)
    if experiment!='P001':
        files.update(prior/name for name in ['interpretation_receipt.json','interpretation.md','interpret_review.md','investigator_next_decision.json'])
    for name in ['SPEC.md','run.py','publication.json','review.json','investigator_decision.json','build_receipt.json','verification_receipt.json']:
        if (exp/name).is_file():files.add(exp/name)
    if (exp/'import_receipt.json').exists():
        if (exp/'import_receipt.json').is_symlink():raise ValueError('symlink import receipt')
        r=json.loads((exp/'import_receipt.json').read_text());bundle=Path(root)/r['bundle']
        for key,name in [('spec_sha256','SPEC.md'),('review_sha256','review.json')]:
            if r.get(key)!=hashlib.sha256((exp/name).read_bytes()).hexdigest():raise ValueError('current import binding stale')
        if bundle.is_symlink() or not bundle.resolve().is_relative_to((exp/'results').resolve()):raise ValueError('unsafe bundle')
        if inventory(bundle)!=r['bundle_file_sha256']:raise ValueError('aggregate import changed')
        files.update(bundle/name for name in r['bundle_file_sha256'])
    for name in ['charters/isles24/CHARTER.md','docs/SCORING_RUBRIC.md','orchestrator/prompts/scout.md','docs/science/PREDICTION_READINESS_DIRECTION_20260906.md','docs/science/PREDICTION_PRIMARY_SOURCES_20260906.json']:
        f=Path(root)/name
        if f.is_file():files.add(f)
    for name in ['docs/operations/REMOTE_OPERATING_DIRECTION.md','docs/operations/CLAUDE_REVIEWER_DIRECTIVE.md']:
        f=Path(root)/name
        if not f.is_file():raise FileNotFoundError('REQUIRED_OPERATING_CONTEXT: '+name)
        files.add(f)
    result={}
    for f in sorted(files):
        if f.is_symlink():raise ValueError('symlink input')
        result[f.relative_to(root).as_posix()]=f.read_bytes().decode('utf-8')
    from orchestrator.research_context import selected_prediction_context
    selected = selected_prediction_context(root)
    if selected:
        for name in ['charters/isles24/CHARTER.md', 'docs/SCORING_RUBRIC.md', 'orchestrator/prompts/scout.md']:
            result.pop(name, None)
        result.update(selected)
    return result


def execute(sc,mode,experiment,request,output,initiator=None,proposal=None,*,max_rounds=2,stage_runner=None):
    if mode not in MODES:raise ValueError('unknown stage')
    if type(max_rounds) is not int or max_rounds not in (1,2):raise ValueError('CAMPAIGN_ROUND_BOUND')
    # Trusted callers may supply the existing hosted model transport. This is not
    # a task-supplied command, credential change or bypass of receipt checks.
    run_stage=stage_runner or system_stage
    output=Path(output)
    permitted=Path(sc.ROOT)/'campaigns/isles24-pilot/pipeline'
    for parent in [permitted,*permitted.parents]:
        if parent.is_symlink():raise ValueError('symlink pipeline ancestor')
        if parent==Path(sc.ROOT):break
    if not output.resolve().is_relative_to(permitted.resolve()) or output.is_symlink():raise ValueError('pipeline output outside campaign')
    output.mkdir(parents=True,exist_ok=False,mode=0o700)
    try:
        if mode=='interpret':
            exp=Path(sc.ROOT)/'campaigns/isles24-pilot/experiments'/experiment
            if not (exp/'import_receipt.json').is_file():raise ValueError('RESULT_IMPORT_REQUIRED')
            from orchestrator.campaign_lifecycle import require_review
            require_review(exp.parents[1],exp)
        context=grounding(sc.ROOT,experiment)
        from orchestrator.research_context import proposal_context,evidence_context,selected_prediction_context
        if proposal is not None and selected_prediction_context(sc.ROOT):
            raise ValueError('RATIFIED_CONTEXT_REFUSES_PROPOSAL_PREVIEW')
        context['related-evidence.json']=json.dumps(evidence_context(sc.ROOT,'isles24-prediction'))
        if proposal:
            if mode not in {'adoption','readiness','discuss','brief','curate'}: raise ValueError('PROPOSAL_PREVIEW_STAGE_ONLY')
            context.update(proposal_context(sc.ROOT,proposal))
            # The proposed scoped guidance is used, rather than contradictory legacy
            # generation requirements. Historical inputs remain in the charter review.
            for name in ['orchestrator/prompts/scout.md','docs/SCORING_RUBRIC.md']:
                context.pop(name,None)
    except BaseException as e:
        (output/'blocked.json').write_text(json.dumps({'status':'BLOCKED','failure_type':type(e).__name__,'reason':'GROUNDING_FAILED'}))
        raise
    binding={k:hashlib.sha256(v.encode()).hexdigest() for k,v in context.items()}
    (output/'request.json').write_text(json.dumps({'mode':mode,'experiment':experiment,'request':request,'input_sha256':binding,'actor_type':'agent','family':'codex','authority':'campaign_delegated_investigator','status':'PROPOSAL_ONLY','max_rounds':max_rounds,'initiator':initiator or {'kind':'agent','family':'codex'}},indent=2))
    body='You are the system campaign '+mode+' author. Produce a bounded proposal, not an approval or executable amendment. Preserve original experiment pins. No patient data, execution, remote writes, or human ratification. All scientific work is exploratory. Lead markdown with a short readable result card: question, evidence, limitations and next decision. Do not invent literature searches or measurements.\nREQUEST: '+request+'\nBOUND CONTEXT:\n'+json.dumps(context)
    if mode in {'charter','adoption','readiness'}:
        body+='\nP001 is externally seeded and operator-delegated, not system-authored. Preserve its historical origin and exact frozen scientific artifacts; propose prospective linkage only. Assess baseline adequacy and scientific value candidly. A proposal may recommend adoption, amendment or rejection, never supply charter ratification or launch approval. Use the context-disposition and exact operator selection to distinguish already ratified guidance from proposals; do not re-request ratification of an unchanged selected charter or alter historical charters/scores. P001 does not depend on 047 acceptance.'
    if mode=='interpret':body+='\nInterpret only the bound validated aggregates. State measured performance, uncertainty and limitations with artifact citations. Write investigator_next_decision.json with exactly status PROPOSAL_ONLY and a nonempty rationale. Do not authorize a follow-up or claim human ratification.'
    try:
        for round in range(1,max_rounds+1):
            directory=output/f'round-{round}';directory.mkdir(mode=0o700)
            author=run_stage(sc,directory,'codex','campaign_'+mode,body,MODES[mode])
            if mode=='interpret':
                decision=json.loads((directory/'investigator_next_decision.json').read_text())
                if set(decision)!={'status','rationale'} or decision['status']!='PROPOSAL_ONLY' or not isinstance(decision['rationale'],str) or not decision['rationale'].strip():raise ValueError('INVALID_INTERPRETATION_NEXT_DECISION')
            proposal='\n'.join(name+'\n'+(directory/name).read_text() for name in MODES[mode])
            if (directory/'review.json').exists():raise ValueError('author may not prepopulate reviewer output')
            reviewer=run_stage(sc,directory,'claude','campaign_'+mode+'_review',
                'Review this campaign proposal against its context. Write review.json with exactly verdict (APPROVE or REVISE) and rationale (nonempty string). Do not ratify or execute.\n'+body+'\nPROPOSAL:\n'+proposal,['review.json'])
            review=json.loads((directory/'review.json').read_text())
            if set(review)!={'verdict','rationale'} or review['verdict'] not in ['APPROVE','REVISE'] or not isinstance(review['rationale'],str) or not review['rationale'].strip():raise ValueError('malformed review')
            if author.get('family_effective')!='codex' or reviewer.get('family_effective')!='claude' or any(r.get('exit_class')!='ok' for r in [author,reviewer]):raise ValueError('opposing-family successful receipts required')
            expected_ci=bool(os.environ.get('SCOUT_CI'))
            if any(bool(r.get('ci'))!=expected_ci or (expected_ci and r.get('runner',{}).get('adapter')!='github-actions-v1') for r in [author,reviewer]):raise ValueError('runner provenance mismatch')
            if review['verdict']=='APPROVE':
                receipt={'status':'REVIEWED_PROPOSAL_NOT_ADOPTED','mode':mode,'experiment':experiment,'input_sha256':binding,'round':round,'artifact_sha256':{p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir() if p.is_file()},'author_family':'codex','reviewer_family':'claude','ci':expected_ci,'initiator':initiator or {'kind':'agent','family':'codex'}}
                (output/'receipt.json').write_text(json.dumps(receipt,indent=2));return receipt
            body+='\nPRIOR PROPOSAL:\n'+proposal+'\nREPAIR REQUIRED:\n'+review['rationale']
        raise ValueError('review revision limit reached')
    except BaseException as e:
        (output/'blocked.json').write_text(json.dumps({'status':'BLOCKED','failure_type':type(e).__name__,'failure_code':str(e) if re.fullmatch('[A-Z][A-Z0-9_]{1,100}',str(e)) else 'PIPELINE_STAGE_FAILED','human_decision':'Inspect preserved stage evidence; do not treat partial output as approved.'}))
        raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=MODES);p.add_argument('--experiment',choices=['P001','P002','P003'],required=True)
    p.add_argument('--proposal-context');p.add_argument('--request',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    import scout
    print(json.dumps(execute(scout,a.mode,a.experiment,a.request,a.output,proposal=a.proposal_context),indent=2))
