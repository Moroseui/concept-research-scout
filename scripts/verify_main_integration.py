"""Read-only merge verification. Run python -m scripts.verify_main_integration.

Run from the candidate checkout root; never merges or pushes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import yaml


CHECK_WORKFLOW_SHA256 = "363ae27a48575aa4105860aa76f4239cb2baec8a9e5e28bd1dce58e0efb3b648"

def workflow_policy(root):
    from scripts.render_human_workflows import verify as verify_controls
    result = verify_controls(root)
    # Retain the pre-amendment deterministic-CI boundaries as well as the controls.
    path = Path(root) / '.github/workflows/check.yml'
    if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != CHECK_WORKFLOW_SHA256:
        raise ValueError('deterministic CI differs from reviewed bytes')
    text = path.read_text()
    checks = yaml.safe_load(text)
    if set(checks['jobs']) != {'basic'}:
        raise ValueError('deterministic CI job contract changed')
    basic = checks['jobs']['basic']
    if 'permissions' in basic or any('permissions' in step for step in basic['steps']):
        raise ValueError('CI cannot override read-only permissions')
    if any(step.get('with', {}).get('persist-credentials') is not False
           for step in basic['steps'] if step.get('uses', '').startswith('actions/checkout@')):
        raise ValueError('CI cannot persist checkout credentials')
    if 'secrets.' in text:
        raise ValueError('CI cannot consume repository secrets')
    return result


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
    from orchestrator.actions_runner import reviewed as controls_review
    exp = root / 'campaigns/isles24-pilot/experiments/P001'
    verify_receipt(root, exp, json.loads((exp / 'review.json').read_text()))
    return {'main_before': main, 'pilot': pilot, 'candidate': git('rev-parse', 'HEAD'),
            'tree': git('rev-parse', 'HEAD^{tree}'), 'workflow_policy': workflow_policy(root),
            'scientific_approval': 'VERIFIED', 'patient_adapter_review': require_patient_review(),
            'archive_review': reviewed(), 'human_controls_review': controls_review(), 'patient_execution': False, 'remote_mutations': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--main', required=True); p.add_argument('--pilot', required=True)
    args = p.parse_args()
    print(json.dumps(verify(Path.cwd(), args.main, args.pilot), indent=2))
