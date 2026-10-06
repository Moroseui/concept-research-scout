"""Deterministic phone-button wiring; shared pipeline, no Git writes or patient jobs."""
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
UPLOAD='actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02'
CHECKOUT='actions/checkout@11d5960a326750d5838078e36cf38b85af677262'
PYTHON='actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065'
NODE='actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020'
MODEL_ENVIRONMENT='research-models'
MODEL_CONTEXT="${{ github.repository == 'Moroseui/concept-research-scout' && github.ref == 'refs/heads/main' && github.event_name == 'workflow_dispatch' }}"
MAIN_CONTEXT_GUARD=('python -c "import os; expected={\'GITHUB_REPOSITORY\':\'Moroseui/concept-research-scout\', '
                    '\'GITHUB_REF\':\'refs/heads/main\', \'GITHUB_EVENT_NAME\':\'workflow_dispatch\'}; '
                    'ok=all(os.environ.get(k)==v for k,v in expected.items()); '
                    'print(\'Main control context verified.\' if ok else \'Use the reviewed main branch controls; this job has no model credentials.\'); '
                    'raise SystemExit(0 if ok else 1)"')


def model_secret_relocation():
    """One fixed administrative workflow; no arbitrary secret-export control."""
    from orchestrator.model_secret_relocation import NAMES, REQUEST
    return {'name':'Stage existing model secrets for the reviewed environment',
        'on':{'workflow_dispatch':{'inputs':{'source_sha':{
            'description':'Exact independently reviewed and approved merged main source','required':True,'type':'string'}}}},
        'permissions':{'contents':'read','actions':'read'},
        'concurrency':{'group':REQUEST,'cancel-in-progress':False},
        'jobs':{'encrypt_for_existing_environment':{
            'if':"${{ github.repository == 'Moroseui/concept-research-scout' && github.ref == 'refs/heads/main' && github.event_name == 'workflow_dispatch' && inputs.source_sha == github.sha }}",
            'runs-on':'ubuntu-24.04','timeout-minutes':10,'env':{'SOURCE_SHA':'${{ inputs.source_sha }}'},
            'steps':[
                {'uses':CHECKOUT,'with':{'ref':'${{ github.sha }}','fetch-depth':1,'persist-credentials':False}},
                {'uses':PYTHON,'with':{'python-version':'3.11'}},
                {'name':'Install only the locked encryption dependency',
                 'run':'python -m pip install --only-binary=:all: --require-hashes -r configs/model-secret-relocation-requirements.txt'},
                {'name':'Check current source review and fixed recipient before reading source secrets',
                 'env':{'GH_TOKEN':'${{ github.token }}'},
                 'run':'python -m orchestrator.model_secret_relocation preflight --source "$SOURCE_SHA" --output "$RUNNER_TEMP/relocation-preflight.json"'},
                {'name':'Encrypt the three original repository values to GitHub',
                 'env':{'SOURCE_'+name:'${{ secrets.'+name+' }}' for name in NAMES},
                 'run':'python -m orchestrator.model_secret_relocation seal --source "$SOURCE_SHA" --preflight "$RUNNER_TEMP/relocation-preflight.json" --output "$RUNNER_TEMP/model-secret-ciphertext/manifest.json"'},
                {'name':'Validate the closed ciphertext artifact before upload',
                 'run':'python -m orchestrator.model_secret_relocation validate --source "$SOURCE_SHA" --run-id "$GITHUB_RUN_ID" --manifest "$RUNNER_TEMP/model-secret-ciphertext/manifest.json"'},
                {'name':'Preserve only the validated ciphertext manifest','uses':UPLOAD,
                 'with':{'name':REQUEST,'path':'${{ runner.temp }}/model-secret-ciphertext/manifest.json',
                         'if-no-files-found':'error','retention-days':1}}]}}}


def documents():
    cfg=json.loads((ROOT/'configs/pilot/human-controls.json').read_text())
    fields={'mode':{'description':'System stage (proposals are never automatically adopted)','type':'choice','options':['discuss'],'default':'discuss'},
            'experiment':{'description':'Registered campaign experiment','type':'choice','options':['P001','P002','P003'],'default':'P001'},
            'question':{'description':'Question or bounded request; no patient details or credentials','default':'Summarize the evidence, limitations and next action.','type':'string'},
            'request_id':{'description':'Reuse to retrieve the same result; change only for a deliberate new attempt','default':'default','type':'string'},
            'source_sha':{'description':'Optional exact SHA; blank binds the selected branch revision','default':'','type':'string'},
            'destination':{'description':'Validated result destination','type':'choice','options':['actions-artifact'],'default':'actions-artifact'},
            'initiator':{'description':'Who is operating this control? (not an approval)','type':'choice','options':['human','codex'],'default':'human'}}
    docs={}
    for name,control in cfg['controls'].items():
        inputs=json.loads(json.dumps(fields));inputs['mode']['options']=control['modes'];inputs['mode']['default']=control['default']
        docs[name+'.yml']={'name':name+' — '+control['title'],'on':{'workflow_dispatch':{'inputs':inputs}},
            'permissions':{'contents':'read','actions':'read'},'jobs':{'control':{
                'uses':'./.github/workflows/research-control.yml',
                'with':{'control':name,**{k:'${{ inputs.'+k+' }}' for k in inputs}}}}}
    inputs={k:{'type':'string','required':False,'default':v.get('default','')} for k,v in fields.items()}
    inputs['control']={'type':'string','required':True}
    docs['research-control.yml']={'name':'Reviewed human and agent control runner',
      'on':{'workflow_call':{'inputs':inputs}},
      'permissions':{'contents':'read','actions':'read'},
      'concurrency':{'group':'human-control-${{ github.ref }}-${{ inputs.request_id }}','cancel-in-progress':False},
      # Environment secrets belong to the called job, never workflow_call or
      # caller forwarding. GitHub must separately restrict this environment to
      # the main branch and remove repository-level model-secret copies.
      'jobs':{'run':{'needs':'admission','if':MODEL_CONTEXT,'environment':MODEL_ENVIRONMENT,
        'runs-on':'ubuntu-latest','timeout-minutes':30,'env':{'SCOUT_CI':'1'},'steps':[
        {'uses':CHECKOUT,'with':{'ref':'${{ github.sha }}','fetch-depth':1,'persist-credentials':False}},
        {'uses':PYTHON,'with':{'python-version':'3.11'}}, {'uses':NODE,'with':{'node-version':'22'}},
        {'name':'Install fixed CLIs and system dependencies','run':'npm install -g @openai/codex@0.153.4 @anthropic-ai/claude-code@2.1.222\npip install -r requirements.txt'},
        {'name':'Verify recorded adapter review','run':'python -c "from orchestrator.actions_runner import reviewed; reviewed()"'},
        {'name':'Existing hosted authentication','continue-on-error':True,
         'env':{'OPENAI_API_KEY':'${{ secrets.OPENAI_API_KEY }}','CLAUDE_CODE_OAUTH_TOKEN':'${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}'},
         'run':'python scripts/actions_auth.py'},
        {'name':'Run the shared system control','id':'result','env':{
           'OPENAI_API_KEY':'${{ secrets.OPENAI_API_KEY }}','CLAUDE_CODE_OAUTH_TOKEN':'${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}','GH_TOKEN':'${{ github.token }}',
           'CONTROL':'${{ inputs.control }}','MODE':'${{ inputs.mode }}','EXPERIMENT':'${{ inputs.experiment }}','QUESTION':'${{ inputs.question }}',
           'REQUEST_ID':'${{ inputs.request_id }}','SOURCE_SHA':'${{ inputs.source_sha }}','DESTINATION':'${{ inputs.destination }}','INITIATOR':'${{ inputs.initiator }}'},
         'run':'python -m orchestrator.human_controls --control "$CONTROL" --mode "$MODE" --experiment "$EXPERIMENT" --request "$QUESTION" --request-id "$REQUEST_ID" --source "${SOURCE_SHA:-$GITHUB_SHA}" --destination "$DESTINATION" --initiator "$INITIATOR" --output "$RUNNER_TEMP/human-result"'},
        {'name':'Save validated phone result and review evidence','if':'${{ always() && steps.result.outputs.artifact_name != \'\' }}','uses':UPLOAD,
         'with':{'name':'${{ steps.result.outputs.artifact_name }}','path':'${{ runner.temp }}/human-result/','if-no-files-found':'error','retention-days':90}},
        {'name':'Explain infrastructure failure','if':"${{ failure() && steps.result.outputs.artifact_name == '' }}",'run':'python -m orchestrator.public_export'},
        {'name':'Remove ephemeral auth','if':'${{ always() }}','run':'python -c "import os,pathlib; p=pathlib.Path(os.environ.get(\'CODEX_HOME\',\'/nonexistent\'))/\'auth.json\'; p.unlink(missing_ok=True)"'}]}}}
    # Admission has no model credentials. Write permission remains ungranted;
    # the protected collector writes state; this job only requests and waits.
    docs['research-control.yml']['jobs']['admission']={
        'runs-on':'ubuntu-latest','timeout-minutes':15,
        'permissions':{'contents':'read','actions':'read'},
        'steps':[
            {'name':'Require reviewed main control context','run':MAIN_CONTEXT_GUARD},
            {'uses':CHECKOUT,'with':{'ref':'${{ github.sha }}','fetch-depth':1,'persist-credentials':False}},
            {'uses':PYTHON,'with':{'python-version':'3.11'}},
            {'name':'Verify recorded adapter review','run':'python -c "from orchestrator.actions_runner import reviewed; reviewed()"'},
            {'name':'Prepare checked shared admission request (inactive until ratified)','id':'admission_request',
             'run':'python -m orchestrator.actions_admission_wait workflow-prepare --repository-cache . --output "$RUNNER_TEMP/research-admission"'},
            {'name':'Save checked admission identity for protected collector','if':"${{ steps.admission_request.outputs.active == 'true' }}",'uses':UPLOAD,
             'with':{'name':'${{ steps.admission_request.outputs.artifact_name }}','path':'${{ runner.temp }}/research-admission/admission.json','if-no-files-found':'error','retention-days':1}},
            {'name':'Wait for exact shared admission (no state write credential)','if':"${{ steps.admission_request.outputs.active == 'true' }}",
             'env':{'GH_TOKEN':'${{ github.token }}','POLICY_SHA256':'${{ steps.admission_request.outputs.policy_sha256 }}'},
             'run':'python -m orchestrator.actions_admission_wait wait --repository-cache . --record "$RUNNER_TEMP/research-admission/admission.json" --policy-sha256 "$POLICY_SHA256"'},
            {'name':'Explain admission refusal','if':'${{ failure() }}','run':'python -m orchestrator.public_export'}]}
    docs['model-secret-relocation.yml']=model_secret_relocation()
    return docs


def render():
    for name,data in documents().items():(ROOT/'.github/workflows'/name).write_text(yaml.safe_dump(data,sort_keys=False,width=120))


def verify(root):
    expected=documents()
    names={p.name for p in (Path(root)/'.github/workflows').iterdir()}
    if names!=set(expected)|{'check.yml'}:raise ValueError('workflow inventory changed')
    for name,data in expected.items():
        if yaml.safe_load((Path(root)/'.github/workflows'/name).read_text())!=data:raise ValueError('reviewed workflow wiring differs: '+name)
    check=yaml.safe_load((Path(root)/'.github/workflows/check.yml').read_text())
    if check.get('on',check.get(True))!={'push': {'branches-ignore': ['remote-server']}, 'pull_request': None} or check.get('permissions')!={'contents':'read'}:
        raise ValueError('deterministic checks permissions or triggers changed')
    return {'human_controls':list(json.loads((ROOT/'configs/pilot/human-controls.json').read_text())['controls']),
            'on_main':'EXPLICIT_DISPATCH','destination':'actions-artifact','patient_execution':False,'git_publication':False}


if __name__=='__main__':render()
