"""Explicit hosted campaign execution adapter. CI remains visible in every receipt."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REVIEW_FILES = ['orchestrator/actions_runner.py', 'scripts/actions_agent.py',
                'orchestrator/human_controls.py', 'orchestrator/campaign_pipeline.py',
                '.github/workflows/research-control.yml', 'configs/pilot/human-controls.json',
                'tests/test_human_controls.py', 'scripts/actions_auth.py', 'scripts/render_human_workflows.py']
REVIEW_FILES += ['.github/workflows/' + n + '.yml' for n in
                 ['actioner','confer','idea-pipeline','interpret','librarian','scout-cycle','results-validate']]


def reviewed(root=ROOT):
    prefix=Path(root)/'docs/isles-pilot/reviews/human-controls'
    e=json.loads(Path(str(prefix)+'.execution.json').read_text())
    p=Path(str(prefix)+'.response.json'); r=json.loads(p.read_text()); v=r.get('structured_output',{})
    if (e['returncode'] or r.get('subtype')!='success' or r.get('is_error')
            or v.get('verdict')!='APPROVE' or v.get('scope')!='human-controls'
            or v.get('reviewed_commit')!=e['reviewed_commit']
            or 'claude-fable-5' not in e['assistant_message_models']
            or hashlib.sha256(p.read_bytes()).hexdigest()!=e['response_sha256']):
        raise ValueError('REVIEW_REQUIRED')
    for name in REVIEW_FILES:
        p=Path(root)/name
        if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=e['input_file_sha256'].get(name):
            raise ValueError('REVIEW_BINDING_CHANGED')
    return e['reviewed_commit']


def identity():
    if os.environ.get('SCOUT_CI')!='1' or os.environ.get('GITHUB_ACTIONS')!='true':
        raise ValueError('HOSTED_RUNNER_REQUIRED')
    required=['GITHUB_REPOSITORY','GITHUB_RUN_ID','GITHUB_RUN_ATTEMPT','GITHUB_SHA','GITHUB_ACTOR','GITHUB_WORKFLOW_REF']
    if any(not os.environ.get(k) for k in required):raise ValueError('CI_IDENTITY_MISSING')
    return {'adapter':'github-actions-v1','ci':True,
            **{k.lower():os.environ[k] for k in required},
            'codex_auth':'existing_actions_api_key','claude_auth':'existing_subscription_oauth'}


def system_stage(sc,directory,family,stage,body,names):
    """Use scout.run_agent; only the process/output transport is hosted-specific."""
    execution=identity();review=reviewed()
    work=Path(tempfile.mkdtemp(prefix='hosted-campaign-'))
    # A tiny TOML profile calls a source-pinned transport, never an ambient CLI profile.
    cmd=[sys.executable,str(ROOT/'scripts/actions_agent.py'),family,json.dumps(names)]
    profile='[default]\nagent = '+json.dumps(family)+'\n[rotation]\nenabled = false\n[limits]\nstage_timeout = 720\n['+family+']\nenabled = true\nstdin = true\ncommand = '+json.dumps(cmd)+'\n'
    (work/'AGENTS.toml').write_text(profile)
    (work/'prompt.md').write_text(body)
    subprocess.run(['git','init','-q',str(work)],check=True)
    subprocess.run(['git','add','.'],cwd=work,check=True)
    subprocess.run(['git','-c','user.name=Hosted campaign','-c','user.email=hosted@local.invalid','commit','-qm','Bound stage input'],cwd=work,check=True)
    old_root=sc.ROOT; had_state=hasattr(sc,'STATE'); old_state=getattr(sc,'STATE',None)
    try:
        sc.ROOT=work;sc.STATE=work/'state.json'
        # The ordinary primitive's stdout is captured privately, not sent to Actions logs.
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            sc.run_agent(work/'prompt.md',family,stage=stage,log_path=work/'console.log')
    except BaseException as error:
        log=(work/'console.log').read_text() if (work/'console.log').exists() else ''
        code=next((c for c in ['CODEX_ACCOUNT_UNFUNDED','MODEL_CREDENTIAL_REJECTED','MODEL_EXECUTION_FAILED'] if c in log),'HOSTED_STAGE_FAILED')
        raise ValueError(code) from error
    finally:
        sc.ROOT=old_root
        if had_state:sc.STATE=old_state
        else:del sc.STATE
        for src,dst in [('prompt.md','prompt_'+stage+'.md'),('stage_provenance.jsonl','stage_provenance.jsonl')]:
            if (work/src).exists():
                with (directory/dst).open('ab') as f:f.write((work/src).read_bytes())
        (directory/('runner_'+stage+'.json')).write_text(json.dumps({**execution,'reviewed_adapter':review,'profile_sha256':hashlib.sha256(profile.encode()).hexdigest(),'private_evidence':str(work)},indent=2))
    receipt=json.loads((work/'stage_provenance.jsonl').read_text().splitlines()[-1])
    if receipt.get('ci') is not True or receipt.get('family_effective')!=family or receipt.get('exit_class')!='ok':raise ValueError('HOSTED_STAGE_RECEIPT_INVALID')
    for name in names:
        p=work/name
        if not p.is_file() or p.is_symlink():raise ValueError('HOSTED_ARTIFACT_MISSING')
        shutil.copyfile(p,directory/name)
    shutil.copyfile(work/'transport.json',directory/('transport_'+stage+'.json'))
    receipt['runner']=execution
    return receipt
