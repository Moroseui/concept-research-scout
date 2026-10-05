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
from scripts.actions_agent import MODELS

ROOT = Path(__file__).resolve().parents[1]
REVIEW_FILES = ['orchestrator/actions_runner.py', 'scripts/actions_agent.py',
                'orchestrator/human_controls.py', 'orchestrator/campaign_pipeline.py',
                '.github/workflows/research-control.yml', 'configs/pilot/human-controls.json',
                'tests/test_human_controls.py', 'scripts/actions_auth.py', 'scripts/render_human_workflows.py',
                'orchestrator/public_export.py', 'orchestrator/dispatch_limiter.py', 'orchestrator/git_publication.py', 'configs/pilot/dispatch-limiter.json',
                'scout.py','orchestrator/campaign_lifecycle.py','orchestrator/publication.py',
                'orchestrator/campaign_review.py','orchestrator/campaign.py',
                'orchestrator/actions_admission_wait.py','orchestrator/operations_report.py',
                'orchestrator/remote_supervisor.py','orchestrator/job_store.py']
REVIEW_FILES += ['.github/workflows/' + n + '.yml' for n in
                 ['actioner','confer','idea-pipeline','interpret','librarian','scout-cycle','results-validate']]
REVIEW_FILES += ['orchestrator/scientific_authority.py', 'orchestrator/scientific_decision.py',
                 'orchestrator/research_catalog.py', 'orchestrator/research_task_authority.py',
                 'orchestrator/change_requests.py', 'orchestrator/hosted_context.py',
                 'configs/scientific-operating-context.json',
                 'configs/scientific-delegation-20260909.json',
                 'docs/operations/SCIENTIFIC_DELEGATION_20260909.md']
REVIEW_FILES += ['orchestrator/model_secret_relocation.py', 'tests/test_model_secret_relocation.py',
                 '.github/workflows/model-secret-relocation.yml',
                 'configs/model-secret-relocation-target.json',
                 'configs/model-secret-relocation-requirements.txt',
                 'docs/operations/MODEL_SECRET_RELOCATION_20260910.md',
                 'docs/operations/PROTECTED_HANDOVER_APPROVED_20260908.json']
# The final handoff review also covers the actual server route and its protected
# transport. These are mandatory inputs, not an optional glob. Generated private
# units/configuration and observed installation evidence require separate exact
# reviewer inputs; reviewing a generator alone does not review deployed settings.
REVIEW_FILES += ['orchestrator/handover_runtime.py', 'orchestrator/handover_coordinator.py',
                 'orchestrator/protected_handover.py', 'orchestrator/hosted_cycle.py',
                 'orchestrator/hosted_campaign.py', 'orchestrator/hosted_campaign_task.py',
                 'orchestrator/completion_bridge.py', 'orchestrator/research_context.py',
                 'orchestrator/reviewer_evidence.py', 'orchestrator/git_diagnostics.py',
                 'orchestrator/report_delivery.py', 'orchestrator/publication_candidate.py',
                 'orchestrator/protected_writer.py', 'orchestrator/handover_notifications.py',
                 'orchestrator/phone_notifications.py', 'scripts/pilot_review.py',
                 'scripts/prepare_handover_snapshot.py',
                 'deploy/research-system/prepare_live_research.py',
                 'deploy/research-system/install_live_research.py',
                 'deploy/research-system/install_handover_fixture.py',
                 'deploy/research-system/install_live_handover.py',
                 'deploy/research-system/research-system-handover-live.socket',
                 'deploy/research-system/research-system-control.sh']

REVIEW_FILES += ['orchestrator/continuing_research.py', 'orchestrator/formal_decisions.py',
                 'orchestrator/scientific_versions.py', 'orchestrator/scientific_materialization.py',
                 'orchestrator/linux_scientific_jobs.py', 'orchestrator/issue_intake.py',
                 'orchestrator/issue_intake_service.py', 'tests/test_continuing_broker.py']
REVIEW_FILES += ['orchestrator/continuing_operations.py', 'orchestrator/protected_scientific_jobs.py',
                 'orchestrator/scientific_job_inputs.py', 'orchestrator/scientific_job_results.py',
                 'orchestrator/protocol_proposals.py', 'orchestrator/deployment_review.py',
                 'tests/test_continuing_operations.py', 'tests/test_continuing_runtime.py',
                 'tests/test_protected_scientific_jobs.py', 'tests/test_linux_scientific_jobs.py',
                 'tests/test_scientific_materialization.py', 'tests/test_formal_scientific_versions.py',
                 'tests/test_protocol_proposals.py', 'tests/test_protocol_proposal_pipeline.py',
                 'tests/test_prospective_interpretation.py', 'tests/test_deployment_review.py',
                 'tests/test_issue_intake.py', 'tests/test_prepare_handover_snapshot.py',
                 'tests/test_continuing_review_inputs.py']


def reviewed_files(root=ROOT):
    """Bind the shared policy and the finite hosted/server handoff implementation."""
    from orchestrator.hosted_context import policy_files
    from scripts.prepare_handover_snapshot import REQUIRED_CONTINUING_SOURCE, scientific_support_files
    root = Path(root)
    # The sparse archive installs these modules. A new installed runtime or
    # installer must not escape the actual review because a manual list is stale.
    installed_modules = {path.relative_to(root).as_posix()
                         for path in (root/'orchestrator').rglob('*.py')}
    return sorted(set(REVIEW_FILES) | policy_files(root) | installed_modules
                  | set(REQUIRED_CONTINUING_SOURCE) | scientific_support_files(root))


def reviewed(root=ROOT):
    # Prior approved inputs remain preserved under human-controls-closeout.
    # This workflow revision needs its own genuine full-input review receipt.
    prefix=Path(root)/'docs/isles-pilot/reviews/human-controls-handover'
    if not Path(str(prefix)+'.execution.json').is_file():raise ValueError('REVIEW_REQUIRED')
    e=json.loads(Path(str(prefix)+'.execution.json').read_text())
    p=Path(str(prefix)+'.response.json'); r=json.loads(p.read_text()); v=r.get('structured_output',{})
    if (e['returncode'] or r.get('subtype')!='success' or r.get('is_error')
            or v.get('verdict')!='APPROVE' or v.get('scope')!='human-controls'
            or v.get('reviewed_commit')!=e['reviewed_commit']
            or 'claude-fable-5' not in e['assistant_message_models']
            or hashlib.sha256(p.read_bytes()).hexdigest()!=e['response_sha256']):
        raise ValueError('REVIEW_REQUIRED')
    for name in reviewed_files(root):
        p=Path(root)/name
        if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=e['input_file_sha256'].get(name):
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
    model=MODELS[family]
    cmd=[sys.executable,str(ROOT/'scripts/actions_agent.py'),family,json.dumps(names),'--model',model]
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
    if (receipt.get('ci') is not True or receipt.get('family_effective')!=family or receipt.get('exit_class')!='ok'
            or receipt.get('model_requested')!=model or receipt.get('model_used')!=model):
        raise ValueError('HOSTED_STAGE_RECEIPT_INVALID')
    transport=json.loads((work/'transport.json').read_text())
    if transport.get('requested_model')!=model or transport.get('model_selection')!='explicit_cli_argument':
        raise ValueError('HOSTED_MODEL_BINDING_INVALID')
    for name in names:
        p=work/name
        if not p.is_file() or p.is_symlink():raise ValueError('HOSTED_ARTIFACT_MISSING')
        shutil.copyfile(p,directory/name)
    shutil.copyfile(work/'transport.json',directory/('transport_'+stage+'.json'))
    receipt['runner']=execution
    return receipt
