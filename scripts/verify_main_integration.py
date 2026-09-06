"""Read-only merge verification. Run python -m scripts.verify_main_integration.

Run from the candidate checkout root; never merges or pushes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
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



FROZEN_REVIEW_SOURCE = '1ecc3f9d5815fb1401bee48454dce197985d947f'


def scientific_status(root):
    """Verify original approved bytes without authorizing the changed checkout."""
    from orchestrator.campaign_review import verify_receipt
    from orchestrator import colab_patient as patient
    def raw(name):
        return subprocess.check_output(['git','show',FROZEN_REVIEW_SOURCE+':'+name],cwd=root)
    base = 'campaigns/isles24-pilot/experiments/P001/'
    receipt = json.loads(raw(base+'review.json'))
    patient_prefix = 'docs/isles-pilot/reviews/'+patient.REVIEW_PREFIX
    execution = json.loads(raw(patient_prefix+'.execution.json'))
    names = set(receipt['file_sha256']) | set(execution['input_file_sha256']) | {
        base+'review.json',receipt['execution'],receipt['response'],
        patient_prefix+'.execution.json',patient_prefix+'.response.json'}
    with tempfile.TemporaryDirectory(prefix='frozen-review-check-') as temporary:
        frozen = Path(temporary)
        for name in names:
            if Path(name).is_absolute() or '..' in Path(name).parts:
                raise ValueError('unsafe frozen review path')
            target = frozen/name; target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw(name))
        verify_receipt(frozen,frozen/base,receipt)
        old_root,old_review = patient.ROOT,patient.REVIEW_DIR
        try:
            patient.ROOT=frozen;patient.REVIEW_DIR=frozen/'docs/isles-pilot/reviews'
            patient_pin=patient.require_patient_review()
        finally:
            patient.ROOT,patient.REVIEW_DIR=old_root,old_review
    # Preserve the original current-tree gate. Only known dependency drift may be
    # reported as blocked infrastructure; every other error still fails verification.
    try:
        verify_receipt(root,root/base,json.loads((root/base/'review.json').read_text()))
        current='VERIFIED'
    except ValueError as error:
        if str(error)!='review does not bind every current executable dependency':raise
        changed=[name for name,h in receipt['file_sha256'].items()
                 if hashlib.sha256((root/name).read_bytes()).hexdigest()!=h]
        if changed!=['scout.py'] and set(changed)!={'scout.py'}:raise
        current='BLOCKED_SCOUT_DEPENDENCY_REVIEW_REQUIRED'
    return {'frozen_source':FROZEN_REVIEW_SOURCE,'frozen_scientific_approval':'VERIFIED',
            'frozen_patient_adapter_review':patient_pin,'current_scientific_gate':current,
            'patient_execution_authorized_by_this_verification':False}


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
    science = scientific_status(root)
    return {'main_before': main, 'pilot': pilot, 'candidate': git('rev-parse', 'HEAD'),
            'tree': git('rev-parse', 'HEAD^{tree}'), 'workflow_policy': workflow_policy(root),
            'scientific_approval': science,
            'archive_review': reviewed(), 'human_controls_review': controls_review(), 'patient_execution': False, 'remote_mutations': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--main', required=True); p.add_argument('--pilot', required=True)
    args = p.parse_args()
    print(json.dumps(verify(Path.cwd(), args.main, args.pilot), indent=2))
