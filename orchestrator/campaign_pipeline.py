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
       'discuss':['discussion.md'], 'brief':['actions.md'], 'curate':['curation.md'], 'interpret':['interpretation.md','investigator_next_decision.json'], 'investigate':['selection.json'],
       'code_bundle':['run.proposed.py','validate_return.proposed.py','requirements.proposed.txt','publication.proposed.json','test.proposed.py'],
       'protocol_proposal':['protocol.proposed.json','methodology.proposed.md','literature-review.proposed.json',
           'input-manifest.proposed.json','partition-registry.proposed.json','exposure-history.proposed.json']}


def system_stage(sc,directory,family,stage,body,names):
    """Single-writer process only: this primitive temporarily changes sc.ROOT.

    Model stages must not run in readiness_queue threads. CI retains its own
    separately reviewed profile/provenance adapter.
    """
    if os.environ.get('SCOUT_CI'):
        from orchestrator.scientific_authority import stage_context
        body=stage_context(sc.ROOT,directory,family,stage)+body
        from orchestrator.actions_runner import system_stage as hosted_stage
        return hosted_stage(sc,directory,family,stage,body,names)
    original=sc.ROOT
    profile=Path(original)/'configs/pilot/agents-unattended.toml'
    config_root=Path(tempfile.mkdtemp(prefix='campaign-profile-'))
    shutil.copy2(profile,config_root/'AGENTS.toml')
    (directory/('profile_'+stage+'.json')).write_text(json.dumps({'profile_sha256':hashlib.sha256((config_root/'AGENTS.toml').read_bytes()).hexdigest(),'profile_source':'configs/pilot/agents-unattended.toml','stage':stage}))
    try:
        sc.ROOT=config_root
        return run_isolated_stage(sc,directory,family,stage,body,names,authority_root=original)
    finally:
        sc.ROOT=original
        shutil.rmtree(config_root)


def grounding(root,experiment,*,prospective_task=None,protocol_task=None,investigator_task=None):
    if experiment not in ['P001','P002','P003']:raise ValueError('campaign scope exceeded')
    if investigator_task is not None:
        from orchestrator.investigator_wakes import grounding as investigator_grounding
        if prospective_task is not None or protocol_task is not None or investigator_task.get('experiment') != experiment:
            raise ValueError('INVESTIGATOR_GROUNDING_SCOPE')
        return investigator_grounding(root, investigator_task)
    if protocol_task is not None:
        from orchestrator.protocol_proposals import grounding as proposal_grounding
        if prospective_task is not None or protocol_task.get('experiment') != experiment:
            raise ValueError('PROTOCOL_PROPOSAL_GROUNDING_SCOPE')
        return proposal_grounding(root, protocol_task)
    prospective=prospective_task is not None
    if prospective:
        from orchestrator.continuing_research import task_contract, PROSPECTIVE_SCHEMA
        task_contract(prospective_task)
        if prospective_task['schema']!=PROSPECTIVE_SCHEMA or prospective_task['experiment']!=experiment:
            raise ValueError('PROSPECTIVE_GROUNDING_CONTRACT_REQUIRED')
    base=Path(root)/'campaigns/isles24-pilot';exp=base/'experiments'/experiment
    # No future scientific proposal before the reviewed predecessor interpretation.
    # An explicit new protocol-backed version uses its separately bound registered
    # predecessors. The historical frozen campaign path retains its old sequence.
    if experiment!='P001' and not prospective:
        prior=base/'experiments'/f'P{int(experiment[1:])-1:03d}'
        for name in ['interpretation_receipt.json','import_receipt.json','interpretation.md','interpret_review.md','investigator_next_decision.json','SPEC.md']:
            if (prior/name).is_symlink():raise ValueError('symlink predecessor')
        r=json.loads((prior/'interpretation_receipt.json').read_text())
        if r.get('status')!='AGENT_REVIEWED_NOT_HUMAN_RATIFIED':raise ValueError('predecessor not reviewed')
        for key,name in [('import_receipt_sha256','import_receipt.json'),('interpretation_sha256','interpretation.md'),('review_sha256','interpret_review.md'),('proposal_sha256','investigator_next_decision.json')]:
            if r.get(key)!=hashlib.sha256((prior/name).read_bytes()).hexdigest():raise ValueError('predecessor binding stale')
        imported=json.loads((prior/'import_receipt.json').read_text())
        if imported.get('spec_sha256')!=hashlib.sha256((prior/'SPEC.md').read_bytes()).hexdigest():raise ValueError('predecessor specification changed')
    from orchestrator.campaign import require_no_human_stop
    from orchestrator.scientific_authority import context as current_authority
    require_no_human_stop(root,experiment)
    files={base/'CAMPAIGN.md'}
    for name in ['CURRENT_STATUS.md','047_LIFECYCLE.md']:
        f=Path(root)/'docs/isles-pilot'/name
        if f.is_file():files.add(f)
    if experiment!='P001' and not prospective:
        files.update(prior/name for name in ['interpretation_receipt.json','interpretation.md','interpret_review.md','investigator_next_decision.json'])
    prior_science=[] if prospective and 'import_result' in prospective_task else ['SPEC.md','run.py','publication.json','review.json','investigator_decision.json','build_receipt.json','verification_receipt.json']
    for name in prior_science:
        if (exp/name).is_file():files.add(exp/name)
    if (exp/'import_receipt.json').exists() and not (prospective and 'import_result' in prospective_task):
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
    delegation=current_authority(root)
    files.update((Path(root)/delegation['binding']['path'],
                  Path(root)/delegation['policy']['direction_path']))
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


def author_body(mode, request, context, formal_task=None):
    """Exact original body; callers may supply a checked presentation map."""
    from orchestrator.continuing_research import PROSPECTIVE_SCHEMA
    prospective = formal_task is not None and formal_task['schema'] == PROSPECTIVE_SCHEMA
    protocol_proposal = formal_task is not None and formal_task['schema'] == 'protocol-proposal-task/v1'
    body='You are the system campaign '+mode+' author. Produce a bounded proposal, not an approval or executable amendment. Preserve original experiment pins. No patient data, execution, remote writes, or human ratification. All scientific work is exploratory. Lead markdown with a short readable result card: question, evidence, limitations and next decision. Do not invent literature searches or measurements.\nREQUEST: '+request+'\nBOUND CONTEXT:\n'+json.dumps(context)
    if mode in {'charter','adoption','readiness'}:
        body+='\nP001 is externally seeded and operator-delegated, not system-authored. Preserve its historical origin and exact frozen scientific artifacts; propose prospective linkage only. Assess baseline adequacy and scientific value candidly. A proposal may recommend adoption, amendment or rejection, never supply charter ratification or launch approval. Use the context-disposition and exact operator selection to distinguish already ratified guidance from proposals; do not re-request ratification of an unchanged selected charter or alter historical charters/scores. P001 does not depend on 047 acceptance.'
    if mode=='investigate':
        from orchestrator.continuing_research import investigator_instruction
        body+='\n'+investigator_instruction(formal_task)
    if mode=='protocol_proposal':
        from orchestrator.protocol_proposals import instructions
        if not protocol_proposal:raise ValueError('PROTOCOL_PROPOSAL_TYPED_TASK_REQUIRED')
        body+='\n'+instructions(formal_task,context)
    if mode=='code_bundle':
        if not prospective:raise ValueError('CODE_BUNDLE_REQUIRES_REVIEWED_PROSPECTIVE_CONTEXT')
        body+='\nGenerate the complete proposed scientific bundle from the exact reviewed idea, specification and protocol in the bound context. Do not invent a scientific choice or dataset beyond them. Files: run.proposed.py, validate_return.proposed.py, requirements.proposed.txt, publication.proposed.json and test.proposed.py. Runner CLI: --data-root, --output-dir, --settings. Inputs and settings are fixed by the registered job; never download data, install dependencies, use the network or access unrelated paths. Write aggregate outputs summary.json, resolved_config.json, environment.json, execution_receipt.json and RESULT_CARD.md, with scientific units/cohort/exposure/settings and process-completion meanings dictated by the reviewed specification. Additional private intermediates may use the sibling result.private directory within the job artifact root. The validator must expose verify(bundle:Path,private:Path,console:Path)->dict, return a file_sha256 inventory, and check semantic cohort/configuration/units/completion without asserting scientific acceptance. Match the existing publication bundle format. Tests use synthetic inputs only. Preserve this as a code proposal; full-input scientific-version approval and a separate launch decision follow.'
        from orchestrator.scientific_validation import author_instruction
        body+='\n'+author_instruction()
    if mode=='interpret':
        if prospective:
            if 'semantic_validation' in formal_task:
                body+='\nInterpret the original aggregates together with the separately bound semantic_validation original. Cite its actual VALID, INVALID or DEFER status, reason and diagnostics; none is automatic acceptance or adoption. INVALID or DEFER must remain visible limitations, never be relabeled a pass. Execution hashes are preservation evidence. Any acceptance still requires distinct formal scientific authority, and successor adoption remains separate.'
            else:
                body+='\nInterpret only the original aggregates in the bound import_result receipt. Its validation_status is PENDING_FORMAL_SCIENTIFIC_VALIDATION and scientific_acceptance is false. Mechanical hashes and exit zero establish preserved execution evidence only. Check the actual scientific version, protocol, cohort, units, settings and result limitations; identify semantic validation still needed, contradictions and measurements that cannot yet support a claim. Do not claim the generated return validator ran, that imported results are validated, or that an approving interpretation review accepts the experiment. Any result acceptance requires its applicable separately recorded semantic validation and authority. Cite the original aggregate filenames and execution/version/protocol bindings.'
        else:
            body+='\nInterpret only the bound validated aggregates.'
        body+=' State measured performance, uncertainty and limitations with artifact citations. Write investigator_next_decision.json with exactly status PROPOSAL_ONLY and a nonempty rationale. Do not authorize a follow-up or claim human ratification.'
    return body


def reviewer_body(body, proposal, verdicts):
    return ('Review this campaign proposal against its context. Write review.json with exactly verdict ('+' or '.join(verdicts)+') and rationale (nonempty string). Do not ratify or execute.\n'+body+'\nPROPOSAL:\n'+proposal)


def prepare_input(root, mode, experiment, request, *, formal_task=None, supplemental_context=None, proposal=None):
    """Pure original grounding and body used by dispatch, preflight and recovery."""
    if mode not in MODES: raise ValueError('unknown stage')
    if formal_task is not None:
        from orchestrator.continuing_research import task_contract, checked_supplement
        contract = task_contract(formal_task)
        if (contract['mode'], contract['experiment']) != (mode, experiment):
            raise ValueError('CHECKED_FORMAL_OPERATION_REQUIRED')
        supplemental_context = checked_supplement(formal_task, supplemental_context)
    elif supplemental_context is not None or mode in ('investigate','protocol_proposal'):
        raise ValueError('INVESTIGATOR_REQUIRES_TYPED_FORMAL_CONTEXT')
    from orchestrator.continuing_research import PROSPECTIVE_SCHEMA
    prospective=formal_task is not None and formal_task['schema']==PROSPECTIVE_SCHEMA
    protocol_proposal=formal_task is not None and formal_task['schema']=='protocol-proposal-task/v1'
    if mode=='interpret' and not prospective:
        exp=Path(root)/'campaigns/isles24-pilot/experiments'/experiment
        if not (exp/'import_receipt.json').is_file():raise ValueError('RESULT_IMPORT_REQUIRED')
        from orchestrator.campaign_lifecycle import require_review
        require_review(exp.parents[1],exp)
    options={'protocol_task':formal_task} if protocol_proposal else {'prospective_task':formal_task} if prospective else {}
    if formal_task is not None and formal_task['schema']=='investigator-task/v1':options={'investigator_task':formal_task}
    context=grounding(root,experiment,**options)
    from orchestrator.research_context import proposal_context,evidence_context,selected_prediction_context
    if proposal is not None and selected_prediction_context(root):
        raise ValueError('RATIFIED_CONTEXT_REFUSES_PROPOSAL_PREVIEW')
    context['related-evidence.json']=json.dumps(evidence_context(root,'isles24-prediction'))
    if formal_task is not None:context.update(supplemental_context)
    if proposal:
        if mode not in {'adoption','readiness','discuss','brief','curate'}: raise ValueError('PROPOSAL_PREVIEW_STAGE_ONLY')
        context.update(proposal_context(root,proposal))
        # The proposed scoped guidance is used, rather than contradictory legacy
        # generation requirements. Historical inputs remain in the charter review.
        for name in ['orchestrator/prompts/scout.md','docs/SCORING_RUBRIC.md']:
            context.pop(name,None)
    return {'context': context,
        'input_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k,v in context.items()},
        'body': author_body(mode, request, context, formal_task)}


def execute(sc,mode,experiment,request,output,initiator=None,proposal=None,*,max_rounds=2,stage_runner=None,complete_negative_review=False,formal_task=None,supplemental_context=None):
    if mode not in MODES:raise ValueError('unknown stage')
    if formal_task is not None:
        from orchestrator.continuing_research import task_contract, checked_supplement
        contract=task_contract(formal_task)
        if (contract['mode'],contract['experiment'])!=(mode,experiment) or stage_runner is None:
            raise ValueError('CHECKED_FORMAL_OPERATION_REQUIRED')
        supplemental_context=checked_supplement(formal_task,supplemental_context)
    elif supplemental_context is not None or mode in ('investigate','protocol_proposal'):
        raise ValueError('INVESTIGATOR_REQUIRES_TYPED_FORMAL_CONTEXT')
    if type(max_rounds) is not int or max_rounds not in (1,2):raise ValueError('CAMPAIGN_ROUND_BOUND')
    if (type(complete_negative_review) is not bool or (complete_negative_review and
            (max_rounds!=1 or stage_runner is None or (formal_task is None and (experiment!='P001' or mode not in ('readiness','discuss')))))):
        raise ValueError('CAMPAIGN_NEGATIVE_COMPLETION_SCOPE')
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
        prepared=prepare_input(sc.ROOT,mode,experiment,request,formal_task=formal_task,
            supplemental_context=supplemental_context,proposal=proposal)
        context=prepared['context']
    except BaseException as e:
        (output/'blocked.json').write_text(json.dumps({'status':'BLOCKED','failure_type':type(e).__name__,'reason':'GROUNDING_FAILED'}))
        raise
    binding={k:hashlib.sha256(v.encode()).hexdigest() for k,v in context.items()}
    (output/'request.json').write_text(json.dumps({'mode':mode,'experiment':experiment,'request':request,'input_sha256':binding,'actor_type':'agent','family':'codex','authority':'campaign_delegated_investigator','status':'PROPOSAL_ONLY','max_rounds':max_rounds,'initiator':initiator or {'kind':'agent','family':'codex'}},indent=2))
    body=prepared['body']
    from orchestrator.continuing_research import PROSPECTIVE_SCHEMA
    prospective=formal_task is not None and formal_task['schema']==PROSPECTIVE_SCHEMA
    protocol_proposal=formal_task is not None and formal_task['schema']=='protocol-proposal-task/v1'
    try:
        for round in range(1,max_rounds+1):
            directory=output/f'round-{round}';directory.mkdir(mode=0o700)
            from orchestrator.campaign import require_no_human_stop
            require_no_human_stop(sc.ROOT,experiment)
            author=run_stage(sc,directory,'codex','campaign_'+mode,body,MODES[mode])
            if protocol_proposal:
                from orchestrator.protocol_proposals import validate_bundle
                protocol_validation=validate_bundle(formal_task,
                    {name:(directory/name).read_text() for name in MODES[mode]},context)
            if mode=='investigate':
                from orchestrator.continuing_research import selection
                protocols=json.loads(supplemental_context['continuing-research-inputs.json']).get('eligible_protocols',[])
                selection(formal_task,json.loads((directory/'selection.json').read_text()),protocols=protocols)
            if mode=='interpret':
                decision=json.loads((directory/'investigator_next_decision.json').read_text())
                if set(decision)!={'status','rationale'} or decision['status']!='PROPOSAL_ONLY' or not isinstance(decision['rationale'],str) or not decision['rationale'].strip():raise ValueError('INVALID_INTERPRETATION_NEXT_DECISION')
            proposal='\n'.join(name+'\n'+(directory/name).read_text() for name in MODES[mode])
            if (directory/'review.json').exists():raise ValueError('author may not prepopulate reviewer output')
            require_no_human_stop(sc.ROOT,experiment)
            verdicts=('APPROVE','REVISE','REQUEST_CHANGES') if complete_negative_review else ('APPROVE','REVISE')
            reviewer=run_stage(sc,directory,'claude','campaign_'+mode+'_review',
                reviewer_body(body,proposal,verdicts),['review.json'])
            review=json.loads((directory/'review.json').read_text())
            if set(review)!={'verdict','rationale'} or review['verdict'] not in verdicts or not isinstance(review['rationale'],str) or not review['rationale'].strip():raise ValueError('malformed review')
            if author.get('family_effective')!='codex' or reviewer.get('family_effective')!='claude' or any(r.get('exit_class')!='ok' for r in [author,reviewer]):raise ValueError('opposing-family successful receipts required')
            expected_ci=bool(os.environ.get('SCOUT_CI'))
            if any(bool(r.get('ci'))!=expected_ci or (expected_ci and r.get('runner',{}).get('adapter')!='github-actions-v1') for r in [author,reviewer]):raise ValueError('runner provenance mismatch')
            if review['verdict']=='APPROVE' or complete_negative_review:
                receipt={'status':'REVIEWED_PROPOSAL_NOT_ADOPTED' if review['verdict']=='APPROVE' else 'REVISION_REQUIRED','mode':mode,'experiment':experiment,'input_sha256':binding,'round':round,'artifact_sha256':{p.relative_to(output).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir() if p.is_file()},'author_family':'codex','reviewer_family':'claude','ci':expected_ci,'initiator':initiator or {'kind':'agent','family':'codex'}}
                if complete_negative_review:
                    receipt.update(review_completion_policy='HOSTED_BOUNDED_REVIEW_WITH_DISPOSITION',
                        review_verdict=review['verdict'],acceptance_status='APPROVED_PROPOSAL_ONLY' if review['verdict']=='APPROVE' else 'NOT_ACCEPTED')
                if prospective and 'import_result' in formal_task:
                    imported=json.loads(supplemental_context['continuing-research-inputs.json'])['import_result']['receipt']
                    receipt['result_import_binding']={'reference':formal_task['import_result'],
                        'completion':imported['completion'],'original_response_sha256':imported['original_response_sha256'],
                        'validation_status':'PENDING_FORMAL_SCIENTIFIC_VALIDATION','scientific_acceptance':False}
                if protocol_proposal:receipt['protocol_proposal_validation']=protocol_validation
                (output/'receipt.json').write_text(json.dumps(receipt,indent=2));return receipt
            body+='\nPRIOR PROPOSAL:\n'+proposal+'\nREPAIR REQUIRED:\n'+review['rationale']
        raise ValueError('review revision limit reached')
    except BaseException as e:
        (output/'blocked.json').write_text(json.dumps({'status':'BLOCKED','failure_type':type(e).__name__,'failure_code':str(e) if re.fullmatch('[A-Z][A-Z0-9_]{1,100}',str(e)) else 'PIPELINE_STAGE_FAILED','human_decision':'Inspect preserved stage evidence; do not treat partial output as approved.'}))
        raise


def reviewed_proposal(root, proposal, experiment):
    """Read one completed proposal; adoption never changes its PROPOSAL_ONLY status."""
    from orchestrator.scientific_authority import read, digest
    root = Path(root).absolute()
    proposal = Path(proposal)
    if not proposal.is_absolute():
        proposal = root / proposal
    allowed = root / 'campaigns/isles24-pilot/pipeline'
    if '..' in proposal.parts or not proposal.is_relative_to(allowed) or any(p.is_symlink() for p in (proposal, *proposal.parents)):
        raise ValueError('CAMPAIGN_PROPOSAL_PATH')
    raw = read(proposal / 'receipt.json')
    receipt = json.loads(raw)
    if (receipt.get('status') != 'REVIEWED_PROPOSAL_NOT_ADOPTED' or
            receipt.get('experiment') != experiment or receipt.get('mode') not in MODES or
            type(receipt.get('round')) is not int or receipt['round'] not in (1, 2) or
            receipt.get('author_family') != 'codex' or receipt.get('reviewer_family') != 'claude'):
        raise ValueError('REVIEWED_CAMPAIGN_PROPOSAL_REQUIRED')
    request_raw = read(proposal / 'request.json')
    request = json.loads(request_raw)
    if (request.get('status') != 'PROPOSAL_ONLY' or request.get('mode') != receipt['mode'] or
            request.get('experiment') != experiment):
        raise ValueError('CAMPAIGN_ORIGINAL_PROPOSAL_REQUEST_REQUIRED')
    hashes = receipt.get('artifact_sha256')
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError('CAMPAIGN_PROPOSAL_ARTIFACTS_REQUIRED')
    prefix = 'round-' + str(receipt['round']) + '/'
    for name, expected in hashes.items():
        relative = Path(name)
        if (relative.is_absolute() or '..' in relative.parts or not name.startswith(prefix) or
                digest(read(proposal / relative)) != expected):
            raise ValueError('CAMPAIGN_PROPOSAL_ARTIFACT_CHANGED')
    for name in [*MODES[receipt['mode']], 'review.json']:
        if prefix + name not in hashes:
            raise ValueError('CAMPAIGN_PROPOSAL_ARTIFACTS_REQUIRED')
    review = json.loads(read(proposal / prefix / 'review.json'))
    if review.get('verdict') != 'APPROVE' or not review.get('rationale'):
        raise ValueError('CAMPAIGN_PROPOSAL_REVIEW_REQUIRED')
    return {'path': str(proposal.relative_to(root)), 'receipt_sha256': digest(raw),
            'request_sha256': digest(request_raw), 'mode': receipt['mode'], 'artifact_sha256': hashes}



if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=MODES);p.add_argument('--experiment',choices=['P001','P002','P003'],required=True)
    p.add_argument('--proposal-context');p.add_argument('--request',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    import scout
    print(json.dumps(execute(scout,a.mode,a.experiment,a.request,a.output,proposal=a.proposal_context),indent=2))
