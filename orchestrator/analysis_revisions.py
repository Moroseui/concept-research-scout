"""Operator-bound analysis revision policy. No new call allowance or failed-call retry."""
from pathlib import Path
import json
import hashlib

from orchestrator.autonomy_limits import AUTHORITY, DOCUMENT, REVISE_ROUNDS
POLICY={'authority_sha256':AUTHORITY,'max_revision_rounds':REVISE_ROUNDS}
# Categories reserved for changes to protected data, privacy, or spending controls.
RESERVED={'privacy/secret','test-set/leakage','budget'}


def enabled(store,run):
    path=Path(store.path).parent/'lane.json'
    if not path.exists():return False
    config=json.loads(path.read_bytes())
    if 'revision_policy' not in config:return False
    if (config['revision_policy']!=POLICY or config.get('run_id')!=run
            or config.get('review_contract')!='bound-review/v1'):
        raise ValueError('ANALYSIS_REVISION_POLICY_SCOPE')
    if 'execution_scope' in config:
        from types import SimpleNamespace
        from orchestrator.experiment_context import selection
        # Same immutable plan and actual selected caller as prepare_input; a
        # bare item number/backend is not enough to extend legacy role limits.
        selection(SimpleNamespace(config=config, state=path.parent,
                                  context=Path(config['context'])))
    elif config.get('backend')!='analysis' or config.get('item_number') not in (2,5):
        raise ValueError('ANALYSIS_REVISION_POLICY_SCOPE')
    authority=Path(config['root'])/DOCUMENT
    if authority.is_symlink() or hashlib.sha256(authority.read_bytes()).hexdigest()!=AUTHORITY:
        raise ValueError('ANALYSIS_REVISION_AUTHORITY_CHANGED')
    if config['item_number']==5:
        from orchestrator.directions_analysis import authority
        authority(config['root'])
    return True


def review_transition(review,stage,round_no):
    if stage not in ('run_spec_review','result_interpretation_review') or type(round_no)!=int or not 1<=round_no<=REVISE_ROUNDS+1:
        raise ValueError('ANALYSIS_REVISION_ROUND')
    if review['verdict']=='REJECT':return 'BLOCKED','REVIEW_REJECTED'
    if review['verdict']!='REVISE' or not review['findings']:
        return 'BLOCKED','REVISE_REQUIRES_ACTIONABLE_FINDINGS'
    if any(row['category'] in RESERVED for row in review['findings']):
        return 'BLOCKED','REVIEW_REQUIRES_OPERATOR_DECISION'
    if round_no>=REVISE_ROUNDS+1:return 'BLOCKED','UNRESOLVED_AFTER_THREE_REVISIONS'
    return stage.replace('_review','_author'),'REVISION_REQUIRED'


def instructions(store,run,*,notebook_revision=False):
    if not enabled(store,run):return 'Any listed finding, REVISE or REJECT stops for the operator. '
    config=json.loads((Path(store.path).parent/'lane.json').read_bytes())
    if 'execution_scope' in config:
        return execution_instructions(config)
    text = ('Latest operator limit decision SHA256 '+AUTHORITY+': item2 sixteen calls, '
        'experiment items3/4 twenty, UTC-day thirty across all roles, scientific batch sixty; '
        'GPU dollar caps unchanged. These figures supersede earlier limits in preserved history; '
        'past usage remains counted and this grants no experiment execution. '
        'The operator now authorizes at most three author revision/re-review cycles per stage, '
        'within the sixteen-call item2 allowance and UTC-day cap. Address every finding '
        'explicitly in the revised artifact; preserve the original finding, cite evidence and '
        'explain the correction or the retained limitation. Do not edit a reviewer report or '
        'claim closure yourself: only an independent APPROVE closes this run/stage findings. '
        'REVISE returns to the author; REJECT or an unresolved fourth review stops. '
        'Findings needing privacy, patient-data, cap or beyond-item2 scope decisions stop for '
        'the operator. Categories privacy/secret, test-set/leakage and budget are held conservatively; '
        'use metric/statistic for correctable aggregate analysis or cost arithmetic. '
        'This reviews an analysis-only proposal, not execution authority. Address future '
        'experiment defects with concrete proposed corrections and explicit execution holds; '
        'do not claim the executable was fixed, tested or approved. Preserve genuine criticism. '
        'If completing this analysis itself requires scope beyond item2, reject with that '
        'specific reason. No patient work, GPU/Modal job or experiment is authorized. ')

    config=json.loads((Path(store.path).parent/'lane.json').read_bytes())
    if config['item_number']==5:
        text=text.replace('item2','item5').replace('Item2','Item5')
        text += 'Item5 allowance16 is separately authorized by docs/DIRECTIONS_OPERATOR_DECISION.txt. Preserve Phase1 before operator-idea reveal. '
    if notebook_revision:
        text=text.replace('Address future experiment defects with concrete proposed corrections and explicit execution holds; do not claim the executable was fixed, tested or approved.', 'Revise the actual notebook copy and cite controller-produced synthetic evidence; retain unfulfilled real-execution conditions for item4.')
    return text


def execution_instructions(config):
    """Scope-specific wording for the already verified execution selection."""
    item=config['item_number']
    from orchestrator.autonomy_limits import selected_run_limit
    cap=selected_run_limit(config,config['run_id'])
    return (f'BACKLOG item {item}: at most three author revision/re-review cycles per stage, '
        f"within this run's {cap}-call allowance, the UTC-day 30-call cap and scientific batch 60-call cap. "
        'All preserved calls remain counted; this is not a retry of an uncertain or failed call. '
        'REVISE returns to the author to address each finding explicitly. Preserve original '
        'findings and cite the correction; only an independent approving review closes them. '
        'REJECT, unresolved findings after the third revision, or findings requiring changes to '
        'privacy, patient access, spending caps or approved backlog scope stop for the operator. '
        "Before execution, revise the actual code/notebook copy and inspect the controller's "
        'synthetic-test evidence. Synthetic tests do not establish real execution or efficacy. '
        'Interpretation revisions explain the existing results; they do not authorize another '
        'run or a post-hoc change to frozen definitions. Provider admission remains a separate '
        'bound transition after spec/code approval. No real-data computation in model workspaces. ')
