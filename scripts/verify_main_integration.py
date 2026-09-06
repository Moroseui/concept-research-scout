"""Read-only verification of a disposable main merge candidate. Never merges/pushes."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import yaml

MODEL_WORKFLOWS = ('actioner', 'confer', 'idea-pipeline', 'interpret', 'librarian', 'scout-cycle')
CONDITION = "github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/astra/autonomous-isles-pilot' && inputs.destination_branch == 'astra/autonomous-isles-pilot' && vars.PILOT_REMOTE_RESEARCH_ENABLED == 'true'"


def workflow_policy(root):
    root = Path(root)
    directory = root / '.github/workflows'
    expected = {name + '.yml' for name in (*MODEL_WORKFLOWS, 'check', 'results-validate')}
    if {p.name for p in directory.iterdir()} != expected:
        raise ValueError('workflow inventory changed; explicit review required')
    for name in MODEL_WORKFLOWS:
        text = (directory / (name + '.yml')).read_text()
        data = yaml.safe_load(text)
        triggers = data.get('on', data.get(True))
        if set(triggers) != {'workflow_dispatch'} or data['permissions'] != {'contents': 'read'}:
            raise ValueError('model workflow trigger or permission changed')
        if len(data['jobs']) != 1:
            raise ValueError('unexpected model job')
        job = next(iter(data['jobs'].values()))
        if job['if'] != CONDITION:
            raise ValueError('model workflow source/destination quarantine changed')
        steps = job['steps']
        guard = steps[-1]
        # Execute ONLY the known diagnostic guard, after checking its closed syntax.
        if guard.get('name') != 'Campaign route required' or not re.fullmatch(
                r"echo 'BLOCKED: [^'\n]+'\nexit 1\n?", guard.get('run', '')):
            raise ValueError('unconditional quarantine guard changed')
        runs = [s for s in steps[:-1] if 'run' in s]
        if len(runs) != 1 or runs[0]['run'] != 'python scripts/workflow_boundary.py verify --source "$SOURCE_SHA" --destination "$DESTINATION_BRANCH"':
            raise ValueError('unexpected executable workflow step')
        allowed_actions = {
            'actions/checkout@11d5960a326750d5838078e36cf38b85af677262',
            'actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065',
            'actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020',
        }
        if any(s['uses'] not in allowed_actions for s in steps if 'uses' in s):
            raise ValueError('unreviewed workflow action')
        if 'secrets.' in text or 'git push' in text or 'git pull' in text:
            raise ValueError('quarantined workflow acquired credentials or publication')
        checkouts = [s for s in steps if s.get('uses', '').startswith('actions/checkout@')]
        if len(checkouts) != 1 or checkouts[0]['with'] != {'ref': '${{ github.sha }}', 'fetch-depth': 1, 'persist-credentials': False}:
            raise ValueError('checkout binding changed')
        result = subprocess.run(['bash', '-c', guard['run']], cwd=root, capture_output=True, timeout=5)
        if result.returncode != 1 or not result.stdout.startswith(b'BLOCKED: '):
            raise ValueError('quarantine does not refuse')
    raw = yaml.safe_load((directory / 'results-validate.yml').read_text())
    if raw['permissions'] != {'contents': 'read'} or set(raw['jobs']) != {'quarantined'} or raw['jobs']['quarantined']['if'] != '${{ false }}':
        raise ValueError('raw results workflow quarantine changed')
    checks = yaml.safe_load((directory / 'check.yml').read_text())
    if checks.get('on', checks.get(True)) != ['push', 'pull_request'] or checks['permissions'] != {'contents': 'read'} or set(checks['jobs']) != {'basic'}:
        raise ValueError('deterministic CI trigger/permission/job contract changed')
    basic = checks['jobs']['basic']
    if 'permissions' in basic or any('permissions' in s for s in basic['steps']):
        raise ValueError('CI cannot override read-only permissions')
    if any(s.get('with', {}).get('persist-credentials') is not False for s in basic['steps'] if s.get('uses', '').startswith('actions/checkout@')):
        raise ValueError('CI cannot persist checkout credentials')
    if 'secrets.' in (directory / 'check.yml').read_text():
        raise ValueError('CI cannot consume repository secrets')
    return {'model_workflows': list(MODEL_WORKFLOWS), 'on_main': 'SKIPPED',
            'pilot_opt_in_guard': 'REFUSED_EXIT_1', 'raw_results': 'DISABLED', 'checks': 'PUSH_PR_READ_ONLY'}


def verify(root, main, pilot):
    root = Path(root).resolve()
    if root != Path(__file__).resolve().parents[1]:
        raise ValueError('run the candidate-owned verifier inside its own checkout')
    if not all(re.fullmatch('[0-9a-f]{40}', pin) for pin in (main, pilot)):
        raise ValueError('full main and pilot pins required')
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root, text=True).strip()
    if git('status', '--porcelain') or git('branch', '--show-current') != 'main':
        raise ValueError('clean isolated main checkout required')
    if git('rev-list', '--parents', '-n', '1', 'HEAD').split()[1:] != [main, pilot]:
        raise ValueError('candidate must retain exact main and pilot parents')
    subprocess.run(['git', 'merge-base', '--is-ancestor', main, pilot], cwd=root, check=True)
    if git('rev-parse', 'HEAD^{tree}') != git('rev-parse', pilot + '^{tree}'):
        raise ValueError('merge tree differs from reviewed pilot tree')
    from orchestrator.campaign_review import verify_receipt
    from orchestrator.colab_patient import require_patient_review
    from orchestrator.archive_preserve import reviewed
    exp = root / 'campaigns/isles24-pilot/experiments/P001'
    verify_receipt(root, exp, json.loads((exp / 'review.json').read_text()))
    return {'main_before': main, 'pilot': pilot, 'candidate': git('rev-parse', 'HEAD'),
            'tree': git('rev-parse', 'HEAD^{tree}'), 'workflow_policy': workflow_policy(root),
            'scientific_approval': 'VERIFIED', 'patient_adapter_review': require_patient_review(),
            'archive_review': reviewed(), 'patient_execution': False, 'remote_mutations': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--main', required=True); p.add_argument('--pilot', required=True)
    args = p.parse_args()
    print(json.dumps(verify(Path.cwd(), args.main, args.pilot), indent=2))
