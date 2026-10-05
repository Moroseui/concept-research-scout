"""Agent-attributed campaign decisions; no human approval marker mutation."""
import hashlib
import json
from pathlib import Path


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_decision(campaign, spec, decision, review=None, code=None):
    d=json.loads(Path(decision).read_text())
    if d.get('authority')!='campaign_delegated_investigator' or d.get('actor_type')!='agent':
        raise ValueError('decision must identify delegated agent authority')
    allowed={'schema_version','authority','actor_type','family','model','experiment','campaign_sha256','spec_sha256','decision','rationale','human_intervention_minutes','usage_tokens','cost_usd'}
    if set(d)-allowed:
        raise ValueError('agent decision cannot manufacture human approval')
    if d.get('campaign_sha256')!=sha(campaign) or d.get('spec_sha256')!=sha(spec):
        raise ValueError('campaign/specification binding stale')
    if d.get('experiment') not in ('P001','P002','P003'):
        raise ValueError('experiment exceeds campaign envelope')
    if d.get('family') not in ('codex','claude') or not d.get('model') or not d.get('rationale'):
        raise ValueError('decision lacks attributable investigator identity/rationale')
    if review is not None:
        verify_code_review(spec, review, code, d)
    return d


def verify_code_review(spec, review, code, decision):
    d = decision
    r=json.loads(Path(review).read_text())
    if r.get('actor_type')!='agent' or r.get('family') not in ('codex','claude') or r['family']==d['family']:
        raise ValueError('opposing-family review required')
    if r.get('verdict')!='APPROVE' or r.get('spec_sha256')!=sha(spec) or not code or r.get('code_sha256')!=sha(code):
        raise ValueError('review missing approval or current spec/code bindings')
    from orchestrator.campaign_review import verify_receipt
    exp=Path(spec).resolve().parent
    verify_receipt(exp.parents[3],exp,r)


CAMPAIGN = 'isles24-pilot'
EXPERIMENTS = ('P001', 'P002', 'P003')
DECISION_ACTIONS = ('approve_probe', 'adopt_followup', 'accept_interpretation')


def experiment_root(root, experiment):
    if experiment not in EXPERIMENTS:
        raise ValueError('CAMPAIGN_ENVELOPE_EXCEEDED')
    root = Path(root).absolute()
    path = root / 'campaigns' / CAMPAIGN / 'experiments' / experiment
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('CAMPAIGN_SYMLINK_PATH')
    return path


def require_no_human_stop(root, experiment):
    """Preserve explicit human campaign controls; model proposals are not controls.

    Campaign and experiment lifecycle records are chronological within their
    scope. Only a later human release in the same scope clears its human stop.
    This does not inspect server activation flags or pending-approval prose.
    """
    from orchestrator.scientific_authority import read
    exp = experiment_root(root, experiment)
    observations = []
    stops = {'STOP', 'STOPPED', 'PAUSE', 'PAUSED', 'HALT', 'HALTED'}
    releases = {'RESUME', 'RESUMED', 'RELEASE', 'RELEASED'}
    for path in (exp.parents[1] / 'lifecycle.jsonl', exp / 'lifecycle.jsonl'):
        if not path.exists() and not path.is_symlink():
            continue
        raw = read(path)
        stopped = False
        for line in raw.decode().splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError('CAMPAIGN_CONTROL_RECORD_INVALID')
            actor = event.get('actor_type', event.get('actor', {}).get('kind')
                              if isinstance(event.get('actor'), dict) else None)
            action = str(event.get('action', event.get('stage', ''))).upper()
            for prefix in ('HUMAN_', 'OPERATOR_'):
                if action.startswith(prefix):
                    action = action[len(prefix):]
            if event.get('experiment', experiment) != experiment:
                continue
            if action not in stops | releases:
                continue
            if actor not in ('human', 'operator', 'agent'):
                raise ValueError('CAMPAIGN_CONTROL_ACTOR_REQUIRED')
            if actor in ('human', 'operator'):
                stopped = action in stops
        observations.append({'path': str(path.relative_to(Path(root).absolute())),
                             'sha256': hashlib.sha256(raw).hexdigest(), 'stopped': stopped})
        if stopped:
            raise ValueError('CAMPAIGN_HUMAN_STOP_PRESERVED')
    return {'status': 'NO_RECORDED_CAMPAIGN_HUMAN_STOP', 'observations': observations}


def decision_bindings(root, experiment, action, proposal=None):
    """Bind a prospective decision without changing a reviewed proposal or runner."""
    from orchestrator.scientific_authority import read
    from orchestrator.campaign_pipeline import reviewed_proposal, grounding
    root = Path(root).absolute()
    exp = experiment_root(root, experiment)
    require_no_human_stop(root, experiment)
    if action not in DECISION_ACTIONS:
        raise ValueError('CAMPAIGN_DECISION_ACTION')
    if action == 'adopt_followup' and experiment == 'P001':
        raise ValueError('FOLLOWUP_REQUIRES_P002_OR_P003')
    if action == 'approve_probe' and experiment != 'P001':
        raise ValueError('FOLLOWUP_REQUIRES_DISTINCT_ADOPTION')
    # Reuse the existing reviewed-predecessor and aggregate-integrity gates.
    grounding(Path(root), experiment)
    files = [exp.parents[1] / 'CAMPAIGN.md', exp / 'SPEC.md', exp / 'run.py',
             exp / 'requirements.txt', exp / 'publication.json']
    if experiment == 'P001':
        # An ordinary decision cannot rewrite the externally seeded baseline.
        verify_decision(files[0], exp / 'SPEC.md', exp / 'investigator_decision.json')
        original_review = json.loads(read(exp / 'review.json'))
        if (original_review.get('code_sha256') != sha(exp / 'run.py') or
                original_review.get('spec_sha256') != sha(exp / 'SPEC.md')):
            raise ValueError('P001_FROZEN_REVIEW_BINDING')
        files.extend((exp / 'investigator_decision.json', exp / 'review.json'))
    if experiment != 'P001':
        prior = exp.parent / f'P{int(experiment[1:])-1:03d}'
        files += [prior / n for n in ('SPEC.md', 'import_receipt.json',
                  'interpretation_receipt.json', 'interpretation.md',
                  'interpret_review.md', 'investigator_next_decision.json')]
    if action == 'accept_interpretation':
        from orchestrator.campaign_lifecycle import require_interpretation
        require_interpretation(exp)
        files += [exp / n for n in ('import_receipt.json', 'interpretation_receipt.json',
                  'interpretation.md', 'interpret_review.md', 'investigator_next_decision.json')]
        if proposal is not None:
            raise ValueError('INTERPRETATION_USES_ORIGINAL_NEXT_DECISION')
        proposal_binding = None
    else:
        if proposal is None:
            raise ValueError('REVIEWED_CAMPAIGN_PROPOSAL_REQUIRED')
        proposal_binding = reviewed_proposal(root, proposal, experiment)
        if proposal_binding['mode'] not in ('adoption', 'specify', 'propose'):
            raise ValueError('CAMPAIGN_ADOPTION_PROPOSAL_MODE')
    root = Path(root).absolute()
    return {'campaign': CAMPAIGN, 'experiment': experiment,
            'envelope': {'experiments': list(EXPERIMENTS), 'development_cases': 99,
                         'reserved_cases': 49, 'reserved_access': False},
            'files': {str(p.relative_to(root)): hashlib.sha256(read(p)).hexdigest()
                      for p in sorted(set(files))}, 'proposal': proposal_binding}


def decision_request(root, experiment, action, proposal=None):
    from orchestrator.scientific_authority import decision_context
    bindings = decision_bindings(root, experiment, action, proposal)
    transition = ({'from': 'AGENT_REVIEWED_NOT_HUMAN_RATIFIED', 'to': 'AGENT_ACCEPTED'}
                  if action == 'accept_interpretation' else
                  {'from': 'REVIEWED_PROPOSAL_NOT_ADOPTED', 'to': 'AGENT_ADOPTED'})
    kw = {'action': action, 'subject': f'campaign:{CAMPAIGN}:{experiment}',
          'bindings': bindings}
    return {**kw, 'transition': transition, 'decision_context': decision_context(root, **kw)}


def verify_experiment(root, experiment, *, review=False):
    """Read either existing investigator authority or a new reviewed adoption."""
    exp = experiment_root(root, experiment)
    require_no_human_stop(root, experiment)
    record = exp / 'agent_adoption.json'
    if not record.exists() and not record.is_symlink():
        return verify_decision(exp.parents[1] / 'CAMPAIGN.md', exp / 'SPEC.md',
                               exp / 'investigator_decision.json',
                               exp / 'review.json' if review else None,
                               exp / 'run.py' if review else None)
    from orchestrator.campaign_lifecycle import verify_application
    applied, d = verify_application(root, experiment, record)
    if applied['action'] not in ('approve_probe', 'adopt_followup'):
        raise ValueError('CAMPAIGN_ADOPTION_ACTION_REQUIRED')
    actor = d['actor']
    normalized = {'authority': d['authority'], 'actor_type': 'agent',
                  'family': actor['family'], 'model': actor['model'],
                  'session_id': actor['session_id'], 'experiment': experiment,
                  'campaign_sha256': sha(exp.parents[1] / 'CAMPAIGN.md'),
                  'spec_sha256': sha(exp / 'SPEC.md'), 'rationale': d['rationale'],
                  'decision_sha256': d['_decision_sha256'], 'policy': d['policy']}
    if review:
        verify_code_review(exp / 'SPEC.md', exp / 'review.json', exp / 'run.py', normalized)
    return normalized


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Apply separately reviewed agent campaign decisions; preserve proposals and frozen code.')
    parser.add_argument('operation', choices=['decision-context', 'apply-decision'])
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--experiment', choices=EXPERIMENTS, required=True)
    parser.add_argument('--action', choices=DECISION_ACTIONS, required=True)
    parser.add_argument('--proposal', type=Path)
    parser.add_argument('--decision', type=Path)
    args = parser.parse_args()
    if args.operation == 'decision-context':
        result = decision_request(args.root, args.experiment, args.action, args.proposal)
    else:
        if args.decision is None:
            parser.error('apply-decision requires --decision')
        from orchestrator.campaign_lifecycle import apply_decision
        result = apply_decision(args.root, args.experiment, args.action, args.decision, args.proposal)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
