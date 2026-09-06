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
    from scripts.render_human_workflows import verify as verify_controls
    return verify_controls(root)


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
