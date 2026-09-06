"""Deterministic phone-button wiring; shared pipeline, no Git writes or patient jobs."""
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
UPLOAD='actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02'
CHECKOUT='actions/checkout@11d5960a326750d5838078e36cf38b85af677262'
PYTHON='actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065'
NODE='actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020'


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
                'with':{'control':name,**{k:'${{ inputs.'+k+' }}' for k in inputs}},
                'secrets':{'OPENAI_API_KEY':'${{ secrets.OPENAI_API_KEY }}','CLAUDE_CODE_OAUTH_TOKEN':'${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}'}}}}
    inputs={k:{'type':'string','required':False,'default':v.get('default','')} for k,v in fields.items()}
    inputs['control']={'type':'string','required':True}
    docs['research-control.yml']={'name':'Reviewed human and agent control runner',
      'on':{'workflow_call':{'inputs':inputs,'secrets':{'OPENAI_API_KEY':{'required':False},'CLAUDE_CODE_OAUTH_TOKEN':{'required':False}}}},
      'permissions':{'contents':'read','actions':'read'},
      'concurrency':{'group':'human-control-${{ github.ref }}-${{ inputs.request_id }}','cancel-in-progress':False},
      'jobs':{'run':{'runs-on':'ubuntu-latest','timeout-minutes':30,'env':{'SCOUT_CI':'1'},'steps':[
        {'uses':CHECKOUT,'with':{'ref':'${{ github.sha }}','fetch-depth':1,'persist-credentials':False}},
        {'uses':PYTHON,'with':{'python-version':'3.11'}}, {'uses':NODE,'with':{'node-version':'22'}},
        {'name':'Install fixed CLIs and system dependencies','run':'npm install -g @openai/codex@0.153.4 @anthropic-ai/claude-code@2.1.222\npip install -r requirements.txt'},
        {'name':'Verify independent adapter review','run':'python -c "from orchestrator.actions_runner import reviewed; reviewed()"'},
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
        {'name':'Explain infrastructure failure','if':"${{ failure() && steps.result.outputs.artifact_name == '' }}",'run':'echo "## BLOCKED\nA preflight or runner step failed. Open the failed step for the named gate; repair the review, dependency or existing authentication binding before a new request. No reviewed result is claimed." >> "$GITHUB_STEP_SUMMARY"'},
        {'name':'Remove ephemeral auth','if':'${{ always() }}','run':'python -c "import os,pathlib; p=pathlib.Path(os.environ.get(\'CODEX_HOME\',\'/nonexistent\'))/\'auth.json\'; p.unlink(missing_ok=True)"'}]}}}
    return docs


def render():
    for name,data in documents().items():(ROOT/'.github/workflows'/name).write_text(yaml.safe_dump(data,sort_keys=False,width=120))


def verify(root):
    expected=documents()
    names={p.name for p in (Path(root)/'.github/workflows').iterdir()}
    if names!=set(expected)|{'check.yml'}:raise ValueError('workflow inventory changed')
    for name,data in expected.items():
        if yaml.safe_load((Path(root)/'.github/workflows'/name).read_text())!=data:raise ValueError('reviewed workflow wiring differs: '+name)
    return {'human_controls':list(json.loads((ROOT/'configs/pilot/human-controls.json').read_text())['controls']),
            'on_main':'EXPLICIT_DISPATCH','destination':'actions-artifact','patient_execution':False,'git_publication':False}


if __name__=='__main__':render()
