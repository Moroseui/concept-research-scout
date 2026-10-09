"""One local Sprint10 acceptance transition per command; no automatic loop.

Only manual_context.prepare constructs model inputs. The executor owns durable
identity/accounting. Engine review is required before initialization or calls.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from orchestrator.review_submission import TerminalSubmissionFailure
from pathlib import Path
from orchestrator import private_records
import re
import shutil
import subprocess
import time
from orchestrator import manual_context, manual_package, manual_stage
from orchestrator.manual_executor import ManualExecutor, atomic, digest, inventory, lock, read
from orchestrator.manual_validation import validate_return,TOLERANCE
from orchestrator.git_publication import scan
from orchestrator.connectivity import NetworkUnavailable

STAGES=('run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review')
CATEGORIES=('test-set/leakage','code/spec mismatch','metric/statistic','privacy/secret','budget','execution authority/provenance')
PROFILE=Path('projects/isles24/context')


def review_blocker_categories(rationale):
    """Keep every marker unless its complete sentence is explicitly negative.

    This recognizes a small affirmative-absence grammar, not sentiment or general
    natural-language negation. Quoted, conditional, qualified, mixed and unknown
    forms remain markers and retain the existing refusal behavior.
    """
    marker = r'BLOCKER\[([^]]+)\]'
    negative = re.compile(
        r'(?:\A|(?<=[.!?])[ \t]+|\n)No ' + marker +
        r' is present(?: in (?:this|the) (?:review|candidate|stock-take))?'
        r'(?:, which performs no execution and makes no new acceptance claim)?'
        r'\.(?=\s|\Z)')
    ignored = set()
    for statement in negative.finditer(rationale):
        categories = statement.group(1).split(', ')
        if categories and len(categories) == len(set(categories)) and all(c in CATEGORIES for c in categories):
            ignored.add(statement.span(1))
    return [m.group(1) for m in re.finditer(marker, rationale) if m.span(1) not in ignored]


def validate_review(review):
    if set(review)!={'verdict','rationale'} or review['verdict'] not in {'APPROVE','REVISE'} or not isinstance(review['rationale'],str) or not review['rationale'].strip():raise ValueError('INVALID_REVIEW')
    blockers=review_blocker_categories(review['rationale'])
    if any(x not in CATEGORIES for x in blockers) or (review['verdict']=='REVISE' and not blockers) or (review['verdict']=='APPROVE' and blockers):raise ValueError('REVIEW_CATEGORY_OR_VERDICT_CONFLICT')
    return blockers


def git(root,*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
def stamp():return datetime.now(timezone.utc).isoformat()
def write_once(path,raw):
    path=Path(path);private_records.mkdir(path.parent,parents=True,exist_ok=True)
    if path.exists():
        private_records.check(path)
        if path.read_bytes()!=raw:raise ValueError('IMMUTABLE_ARTIFACT_CONFLICT')
    else:
        with private_records.open_file(path,'xb') as f:f.write(raw)


@private_records.private_umask
def initialize(root,state,engine_review,server_rerun=False,*,cpu=False):
    root,state,engine_review=map(Path,(root,state,engine_review))
    if git(root,'status','--porcelain'):raise ValueError('CLEAN_REVIEWED_SOURCE_REQUIRED')
    source=git(root,'rev-parse','HEAD');branch=git(root,'branch','--show-current')
    report=engine_review.read_text()
    if source not in report or re.findall(r'^## Verdict: (.+?)\s*$',report,re.M)!=['APPROVE']:raise ValueError('EXACT_ENGINE_REVIEW_REQUIRED')
    if not branch.startswith('astra/manual-'):raise ValueError('MANUAL_BRANCH_REQUIRED')
    if cpu and server_rerun:raise ValueError('DISTINCT_BATCH_ALLOWANCE_REQUIRED')
    backend=manual_package
    cpu_config=None
    if cpu:
        from orchestrator import cpu_package
        backend=cpu_package
        cpu_config=cpu_package.runtime_config(root)
    if (state/'lane.json').exists():raise ValueError('EXISTING_LANE_USE_STATUS_OR_ADVANCE')
    if cpu:
        try:
            git(root,'var','GIT_AUTHOR_IDENT');git(root,'var','GIT_COMMITTER_IDENT')
        except subprocess.CalledProcessError:
            raise ValueError('CPU_GIT_IDENTITY_REQUIRED: configure the new repository before initializing; no call reserved') from None
        cpu_readiness=cpu_package.runtime_preflight(root,cpu_config)
    private_records.mkdir(state,parents=True,exist_ok=True,mode=0o700)
    context=state/'context';private_records.mkdir(context)
    manifest=read(root/PROFILE/'manifest.json')
    files={row['path'] for row in manifest['sources']}
    files.update(str(p.relative_to(root)) for p in (root/PROFILE).rglob('*') if p.is_file())
    fixtures=Path('tests/fixtures/context_budget/round2')
    # Size-only proxies must never enter the actual scientific task.
    original=read(root/fixtures/'PROVENANCE.json')
    rows=[row['artifact'] for row in original['artifacts'] if not row['is_size_proxy']]
    files.update(row['path'] for row in rows)
    for name in files:
        dest=context/name;private_records.mkdir(dest.parent,parents=True,exist_ok=True);private_records.copyfile(root/name,dest)
    # Stage input records pin originals; notebook output contains private membership
    # only in the separately held operator file, never in model input.
    run_id=('sprint10-cpu-' if cpu else 'sprint10-stepd-')+digest((source+digest(engine_review.read_bytes())).encode())[:16]
    # Build the exact future notebook before authoring/review; manifest binding is
    # read at runtime, so the notebook's code does not depend on a future spec.
    nb=backend.notebook_bytes(root,run_id)
    notebook=json.loads(nb)
    exact_source="\n\n".join("".join(c["source"]) for c in notebook["cells"])
    current=context/'current';private_records.mkdir(current)
    private_records.write_text(current/'notebook-source.txt',exact_source)
    rows=[row for row in rows if row['type']!='notebook_source']+[{'id':'notebook-source','type':'notebook_source','version':2,'path':'current/notebook-source.txt','sha256':digest(exact_source.encode())}]
    validator=(root/'projects/isles24/manual/sprint10/validate_reference.py').read_bytes()+b"\n\n"+(root/'orchestrator/manual_validation.py').read_bytes()
    if cpu:validator+=b'\n\n'+(root/'orchestrator/cpu_package.py').read_bytes()
    private_records.write_bytes(current/'validator.py',validator)
    rows=[row for row in rows if row['type']!='validator']+[{'id':'validator','type':'validator','version':2,'path':'current/validator.py','sha256':digest(validator)}]
    manual_package.baseline_contract(root)
    baseline=(root/'projects/isles24/manual/sprint10/REFERENCE_BINDINGS.json').read_bytes()
    private_records.write_bytes(current/'baseline-bindings.json',baseline)
    rows.append({'id':'original-baseline-bindings','type':'data_contract','version':1,'path':'current/baseline-bindings.json','sha256':digest(baseline)})
    if cpu:
        data_contract=(root/'projects/isles24/manual/sprint10/CPU_INPUT_BINDING.json').read_bytes()
        private_records.write_bytes(current/'cpu-input-binding.json',data_contract)
        rows=[r for r in rows if r['type']!='data_contract' or r['id']=='original-baseline-bindings']
        rows.append({'id':'cpu-input-binding','type':'data_contract','version':1,'path':'current/cpu-input-binding.json','sha256':digest(data_contract)})
        for kind,name,raw in [('configuration','cpu-configuration.txt',manual_package.code_cells(nb)[0].encode()),
                              ('metric_contract','cpu-metric-contract.json',json.dumps(cpu_package.TOLERANCE,sort_keys=True).encode())]:
            private_records.write_bytes(current/name,raw)
            rows=[r for r in rows if r['type']!=kind]+[{'id':kind,'type':kind,'version':1,'path':'current/'+name,'sha256':digest(raw)}]
    clients=manual_stage.preflight()
    common=Path(git(root,'rev-parse','--git-common-dir'))
    if not common.is_absolute():common=root/common
    owner=common.resolve()/('autonomy-cpu-owner.json' if cpu else 'manual-sprint10-step-d-owner.json')
    binding={'state':str(state.resolve()),'source':source,'review_sha256':digest(engine_review.read_bytes())}
    if owner.exists():raise ValueError('EXISTING_CANONICAL_ACCEPTANCE_USE_SAVED_STATE')
    with private_records.open_file(owner,'x') as stream:json.dump(binding,stream,sort_keys=True)
    authority=root/('docs/AUTONOMY_BATCH_2026-09-27.md' if cpu else 'docs/SERVER_RERUN_AUTHORIZATION.md' if server_rerun else 'docs/STEP_D_AUTHORIZATION.md')
    policy={'status':'RATIFIED','operator_approval':digest(authority.read_bytes()),'state_write_permission':'OPERATOR_AUTHORIZED',
       'n':4,'window':'UTC_CALENDAR_DAY','state_ref':'refs/heads/automation/dispatch-state','manual_semantics':'OPERATOR_STEP_D_MAX_EIGHT'}
    if server_rerun:policy.update(n=3,manual_semantics='OPERATOR_SERVER_SPRINT10_MAX_SIX')
    if cpu:
        # Deliver the actual current operator scope through the existing exact-
        # quote register, rather than relying on this driver's conversation.
        raw=authority.read_bytes();text=raw.decode();name='current/autonomy-batch-authority.md'
        private_records.write_bytes(context/name,raw)
        folder=context/PROFILE;registry=read(folder/'obligations.json');context_manifest=read(folder/'manifest.json')
        spans=[('stops','## Standing rules','**Reviews are automated.**'),
               ('caps','**Caps, until I raise them:**','**Freeze:**'),
               ('m2','**M2: Server CPU executor','**M3: GPU executor'),
               ('old-routes','## Operator amendment: M4 successor contract','## Observed-outage amendment')]
        for label,start_text,end_text in spans:
            start=text.index(start_text);end=text.index(end_text,start)
            quote=text[start:end];begin=len(text[:start].encode());finish=begin+len(quote.encode())
            registry['obligations'].append({'id':'AUTONOMY20260927-'+label,'type':'protocol amendment','status':'open','severity':'major',
                'scope':{'project':['isles24-prediction'],'idea_ids':['Sprint10'],'stages':['*']},'text':quote,
                'source':{'path':name,'sha256':digest(raw),'start':begin,'end':finish,'original_path':str(authority.relative_to(root))},'disposition':None})
        atomic(folder/'obligations.json',registry)
        context_manifest['obligations']['sha256']=digest((folder/'obligations.json').read_bytes())
        context_manifest['sources'].append({'path':name,'sha256':digest(raw)})
        atomic(folder/'manifest.json',context_manifest)

    config={'server_rerun':server_rerun,'authority_path':str(authority.relative_to(root)),'run_id':run_id,'source':source,'branch':branch,'root':str(root),'context':str(context),
      'owner_path':str(owner),'owner_binding':binding,'engine_review':{'path':str(engine_review),'sha256':digest(engine_review.read_bytes())},'authority_sha256':digest(authority.read_bytes()),
      'notebook_code_sha256':manual_package.code_sha(nb),'workspace_root':str(state.parent/(state.name+'-scientific-workspaces')),'clients':clients,'policy':policy,'artifacts':rows,'started_utc':stamp(),
      'profile_files':{str(p.relative_to(root)):digest(p.read_bytes()) for p in (root/PROFILE).rglob('*') if p.is_file()},
      'engine_files':{str(p.relative_to(root)):digest(p.read_bytes()) for p in (root/'orchestrator').glob('*.py')}}
    config['engine_files']['scout.py']=digest((root/'scout.py').read_bytes())
    config['scientific_files']={str(p.relative_to(root)):digest(p.read_bytes()) for p in (root/'projects/isles24/manual/sprint10').iterdir() if p.is_file()}
    batch=None
    if cpu:
        from orchestrator.autonomy_accounting import BatchAccounts
        batch=BatchAccounts(cpu_config['batch_ledger'])
        batch.register_run(run_id,binding)
        config['backend']='cpu';config['cpu']=cpu_config;config['cpu_readiness']=cpu_readiness
        config['engine_files']['deploy/manual-lane/cpu-runtime.json']=digest((root/'deploy/manual-lane/cpu-runtime.json').read_bytes())
    atomic(state/'lane.json',config,mode=0o600)
    store=ManualExecutor(state/'jobs.sqlite');store.initialize_allowance(policy)
    store.db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps({'phase':STAGES[0],'rounds':{},'artifacts':rows,'interventions':[{'kind':'OPERATOR_SUPPLIED_ENGINE_APPROVAL','recorded_utc':stamp(),'review_sha256':digest(engine_review.read_bytes())}]}),))
    store.db.close()
    return {'status':'READY','run_id':run_id,'next':STAGES[0],'calls_used':0}


class Driver:
    def __init__(self,state,runner=None):
        self.state=Path(state);self.config=read(self.state/'lane.json')
        self.root=Path(self.config['root']);self.context=Path(self.config['context'])
        if self.config.get('backend')=='cpu':
            from orchestrator.autonomy_accounting import BatchAccounts
            from orchestrator.cpu_executor import CPUExecutor
            self.store=CPUExecutor(self.state/'jobs.sqlite',self.config['cpu'],batch=BatchAccounts(self.config['cpu']['batch_ledger']))
        else:self.store=ManualExecutor(self.state/'jobs.sqlite')
        self.runner=runner or manual_stage.invoke

    def current(self):return json.loads(self.store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
    def save(self,value):
        self.store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
        if value.get('phase')=='BLOCKED':
            pending=value.get('pending',{});stage=pending.get('stage',value.get('blocked_stage','unknown'))
            round_no=pending.get('round',value.get('rounds',{}).get(stage,0))
            # A pending failed call outranks the previous successful review.
            candidates=[]
            record_missing=False
            if pending.get('workspace'):
                work=Path(pending['workspace'])
                record_missing=not (work/'stage_provenance.jsonl').is_file()
                candidates.extend(work/name for name in ['stage_provenance.jsonl','transport.log','console.log','sent-input.json','prompt.md'])
            elif value.get('review'):candidates.append(Path(value['review']))
            candidates.extend([self.state/'jobs.sqlite',self.state/'lane.json'])
            review=next((str(p) for p in candidates if p.is_file()),None)
            evidence=('Existing evidence: '+review+'. ') if review else 'No evidence file is currently available. '
            if pending.get('id'):evidence+='Call id: '+pending['id']+'. '
            if record_missing:evidence+='The call provenance record was not written; the nearest existing evidence is linked above. '
            categories=value.get('blocker_categories',[])
            text=(f"Decision needed for {self.config['run_id']}: stage {stage}, round {round_no}, "
                  f"reason {value.get('reason','UNSPECIFIED_BLOCK')}; categories {', '.join(categories) or 'execution authority/provenance (operational refusal)'}. "
                  +evidence+"No automatic retry, extra call or execution is authorized. "
                  "Please inspect this saved outcome and decide whether to defer, reject, or authorize a specifically bounded recovery.\n")
            path=self.state/'DECISION_REQUEST.md'
            if path.exists() and path.read_text()!=text:
                write_once(self.state/('decision-request-'+digest(path.read_bytes())+'.md'),path.read_bytes())
            private_records.write_text(path,text)
    def guard(self):
        if (self.state/'HALT').exists():raise ValueError('OPERATOR_HALT: HALT file is present; no work started. Preserve state and request operator disposition before resuming.')
        c=self.config
        if self.store.batch is not None and (self.store.batch.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
        if c.get('timeout_continuation'):
            from orchestrator.experiment_timeout_continuation import validate_driver
            validate_driver(self)
        if c.get('artifact_continuation'):
            from orchestrator.artifact_recording_transition import validate_driver
            validate_driver(self)
        if c.get('notebook_revision_continuation'):
            from orchestrator.notebook_revision_transition import validate_driver
            validate_driver(self)
        if c.get('revision_continuation'):
            from orchestrator.analysis_revision_transition import validate_driver
            validate_driver(self)
        if c.get('execution_recovery'):
            from orchestrator.manual_recovery import validate_runtime
            validate_runtime(self)
        if c.get('owner_path') and read(c['owner_path'])!=c['owner_binding']:raise ValueError('CANONICAL_ACCEPTANCE_STATE_CHANGED')
        if digest(Path(c['engine_review']['path']).read_bytes())!=c['engine_review']['sha256']:raise ValueError('ENGINE_REVIEW_CHANGED')
        if digest((self.root/c.get('authority_path','docs/STEP_D_AUTHORIZATION.md')).read_bytes())!=c['authority_sha256']:raise ValueError('AUTHORITY_CHANGED')
        # A changed authority/register cannot be hidden by the initial snapshot.
        if self.current()['phase'] not in {'REPORT','COMPLETE'}:
            for name,expected in c['profile_files'].items():
                if digest((self.root/name).read_bytes())!=expected:raise ValueError('PROJECT_CONTEXT_CHANGED_RECONCILE')
        archive=self.root/'evidence/decisions.md'
        private_records.copyfile(archive,self.context/'evidence/decisions.md')
        if git(self.root,'branch','--show-current')!=c['branch']:raise ValueError('MANUAL_BRANCH_CHANGED')
        for name,expected in {**c['engine_files'],**c.get('scientific_files',{})}.items():
            if digest((self.root/name).read_bytes())!=expected:raise ValueError('REVIEWED_ENGINE_CHANGED')

    def status(self):
        from orchestrator.manual_host_guard import lane_status
        v=self.current();calls=[dict(r) for r in self.store.db.execute('SELECT * FROM manual_calls')]
        return {'run_id':self.config['run_id'],'phase':v['phase'],'calls_used':len(calls),'call_limit':__import__('orchestrator.autonomy_limits',fromlist=['selected_run_limit']).selected_run_limit(self.config,self.config['run_id']),'rounds':v['rounds'],
          'interventions':v['interventions'],'operator_halt':(self.state/'HALT').exists(),'host_controls':lane_status(self.state),'connectivity':__import__('orchestrator.connectivity',fromlist=['status']).status(self.state/'connectivity.json'),'reason':v.get('reason'),
          'decision_request':str(self.state/'DECISION_REQUEST.md') if v['phase']=='BLOCKED' else None,
          'next_action':('Server-owned CPU execution/collection; no Colab' if self.config.get('backend')=='cpu' and v['phase'] in {'WAIT_OUTPUTS','EXECUTE_CPU'} else 'Run the emitted notebook once in Colab; then advance --collect-folder PATH' if v['phase']=='WAIT_OUTPUTS' else v['phase']),
          'package':str(self.state/'package'),'collection_inbox':str(self.state/'inbox'/self.config['run_id']),'calls':[{k:r[k] for k in ['id','stage','attempt','status']} for r in calls]}

    def artifact(self,value,kind,name,raw,version):
        scan('context/current.txt',raw)
        # Seed context may retain predecessor outputs with the same stage/round
        # name. New writes belong to this run; immutable predecessor paths stay
        # readable and unchanged. Hash the run ID rather than interpreting it
        # as a filesystem path. Artifact IDs remain the current selection keys.
        relative='current/runs/'+digest(self.config['run_id'].encode())+'/'+name
        write_once(self.context/relative,raw)
        row={'id':kind,'type':kind,'version':version,'path':relative,'sha256':digest(raw)}
        value['artifacts']=[r for r in value['artifacts'] if r['id']!=kind]+[row]

    def task(self,stage,value):
        tolerance=TOLERANCE
        if self.config.get('backend')=='cpu':
            from orchestrator.cpu_package import TOLERANCE as tolerance
        text=('Sprint10 known-case reproduction of completed results: interpret the selected evidence '
          'or write the exact notebook run spec (at most12000 characters), as this stage requires. '
          'Report measured performance, uncertainty and limitations with artifact citations; distinguish '
          'reproduction from new efficacy. Predeclared comparison: '+json.dumps(tolerance,sort_keys=True)+'. '
          'For REVISE, identify a concrete BLOCKER[category] in rationale. Categories: '+', '.join(CATEGORIES)+'. '
          'Record other concerns as advisories. APPROVE must not conceal a blocker. ')
        if self.config.get('backend')=='cpu':text+=' Execution is server CPU, no Colab or training. All five CSVs must reproduce byte-for-byte; the99-only split and empty exclusion list are derived from the verified cohort, not the original mixed-membership split. '
        if stage.startswith('run_spec'):
            text+=' The spec must contain exactly these two binding lines: \nrun_id: '+self.config['run_id']+'\nnotebook_code_sha256: '+self.config['notebook_code_sha256']+'\n'
        return text

    def model_step(self,value):
        if self.runner is manual_stage.invoke:
            with manual_stage.login_guard(value['phase']):
                return self._model_step(value)
        return self._model_step(value)

    def model_round_number(self,value):
        """Attempt workspace number; accepted-round counters remain scientific state."""
        stage=value['phase']
        if self.config.get('execution_recovery'):
            return self.store.db.execute('SELECT count(*) FROM manual_calls WHERE stage=?',(stage,)).fetchone()[0]+1
        return value['rounds'].get(stage,0)+1

    def model_workspace(self,value,stage,round_no):
        return Path(self.config.get('workspace_root',self.state.parent/(self.state.name+'-scientific-workspaces')))/(stage+'-'+str(round_no))

    def _model_step(self,value):
        from orchestrator.manual_recovery import role_limit
        stage=value['phase']
        round_no=self.model_round_number(value)
        if round_no>role_limit(self.store,self.config['run_id'],stage):raise ValueError('REVIEW_ROUND_LIMIT')
        work=self.model_workspace(value,stage,round_no)
        body,measurement=self.prepare_input(value,stage,work)
        private_records.mkdir(work,parents=True,exist_ok=True)
        write_once(work/'prompt.md',body.encode());atomic(work/'input-measurement.json',measurement)
        self.guard()
        if stage.endswith('review') and self.config.get('review_contract')=='bound-review/v1':
            from orchestrator import review_submission as rs
            expected_call=digest((self.config['run_id']+':'+stage+':'+str(round_no)).encode())
            submission=rs.prepare(work,'scientific',{'call_id':expected_call,'run_id':self.config['run_id'],
                'stage':stage,'source_sha':self.config['source'],'runtime_sha256':self.config['clients']['runtime_config_sha256'],
                'input_sha256':digest(body.encode())})
            atomic(work/'submission-pre-reservation.json',submission)
        if self.runner is manual_stage.invoke:
            manual_stage.data_access_guard(work,stage)
            if manual_stage.preflight()!=self.config['clients']:raise ValueError('LOCAL_CLIENT_OR_AUTH_CHANGED')
            transport=manual_stage.transport_check(work,stage,digest(body.encode()))
            if stage.endswith('review'):
                from orchestrator.scientific_search import prepare as prepare_search
                search=prepare_search(work)
                atomic(work/'search-pre-reservation.json',search)
        base={'stage':stage,'input_characters':len(body),'input_utf8_bytes':len(body.encode()),'input_sha256':digest(body.encode()),'started_utc':stamp(),'workspace':str(work)}
        if stage.endswith('review') and self.config.get('review_contract')=='bound-review/v1':base['submission_preflight']=submission
        if self.runner is manual_stage.invoke:
            base['transport_preflight']=transport
            if stage.endswith('review'):base['search_preflight']=search
        from orchestrator.stocktake_recovery import RUN as STOCKTAKE_RUN
        if value.get('linked_recovery_of') and self.config['run_id']!=STOCKTAKE_RUN:
            base['linked_recovery_of'] = value['linked_recovery_of']
        ident,attempt,receipt=self.store.reserve_call(self.config['run_id'],stage,self.config['source'],self.config['branch'],self.config['policy'],base)
        value.update(phase='MODEL_RUNNING',pending={'id':ident,'stage':stage,'round':round_no,'workspace':str(work)})
        self.save(value)
        try:
            native=self.runner(work,stage,self.config['clients'],base['input_sha256'])
            if stage.endswith('review') and self.config.get('review_contract')=='bound-review/v1' and self.runner is manual_stage.invoke:
                from orchestrator import review_submission as rs
                if rs.runtime_pins(work)!=submission:raise ValueError('SUBMISSION_PREPARATION_CHANGED')
            if digest((work/'prompt.md').read_bytes())!=base['input_sha256']:raise ValueError('MODEL_ALTERED_BOUND_PROMPT')
            for ref in measurement['workspace_files']:
                if digest((work/ref['path']).read_bytes())!=ref['sha256']:raise ValueError('MODEL_ALTERED_BOUND_EVIDENCE')
            output={}
            for name in self.output_names(stage):
                path=work/name
                if path.is_symlink() or not path.is_file():raise ValueError('MISSING_REGULAR_MODEL_OUTPUT')
                raw=path.read_bytes();scan('context/'+name,raw)
                if len(raw)>80000:raise ValueError('MODEL_OUTPUT_TOO_LARGE')
                output[name]=digest(raw)
            receipt.update(native=native,output_sha256=output,completed_utc=stamp(),outcome='COMPLETE')
            self.store.finish_call(ident,receipt,'COMPLETE')
        except TerminalSubmissionFailure as error:
            receipt.update(completed_utc=stamp(),outcome='FAILED',reason=str(error),error_type=type(error).__name__)
            self.store.finish_call(ident,receipt,'FAILED')
            value.update(phase='BLOCKED',reason='REVIEW_SUBMISSION_FAILED_NO_RETRY: '+str(error));self.save(value);raise
        except BaseException as error:
            receipt.update(completed_utc=stamp(),outcome='FAILED_OR_UNCERTAIN',error_type=type(error).__name__)
            self.store.finish_call(ident,receipt,'UNCERTAIN')
            value.update(phase='BLOCKED',reason='MODEL_FAILED_OR_UNCERTAIN_NO_RETRY');self.save(value);raise
        return self.accept_completed(value)

    def output_names(self, stage):
        if "execution_scope" in self.config:
            from orchestrator.experiment_context import outputs
            return outputs(self, stage)
        return manual_context.OUTPUTS[stage]

    def prepare_input(self,value,stage,work):
        if "execution_scope" in self.config:
            from orchestrator.experiment_context import prepare
            return prepare(self, value, stage, work)
        return manual_context.prepare(self.context,stage=stage,idea_ids=self.config.get('idea_ids',['Sprint10']),task=self.task(stage,value),artifacts=value['artifacts'],workspace=work)

    def finding_prefix(self,stage):
        # Full run digest avoids path syntax and cross-run stage/round collisions.
        return 'STEPD-'+digest(self.config['run_id'].encode())+'-'+stage+'-'

    def criticism(self,stage,round_no,raw):
        folder=self.context/PROFILE;registry=read(folder/'obligations.json');manifest=read(folder/'manifest.json')
        ident=self.finding_prefix(stage)+str(round_no)
        name='current/finding-'+ident+'.json'
        expected={'id':ident,'type':'adverse finding','status':'open','severity':'blocker',
          'scope':{'project':['isles24-prediction'],'idea_ids':self.config.get('idea_ids',['Sprint10']),'stages':['*']},'text':raw.decode(),
          'source':{'path':name,'sha256':digest(raw),'start':0,'end':len(raw),'original_path':name},'disposition':None}
        matches=[row for row in registry['obligations'] if row['id']==ident]
        if matches:
            if len(matches)!=1 or matches[0]!=expected or (self.context/name).read_bytes()!=raw:
                raise ValueError('EXISTING_FINDING_CONFLICT')
            return
        write_once(self.context/name,raw)
        registry['obligations'].append(expected)
        atomic(folder/'obligations.json',registry);manifest['obligations']['sha256']=digest((folder/'obligations.json').read_bytes());atomic(folder/'manifest.json',manifest)

    def accept_completed(self,value):
        try:return self._accept_completed(value)
        except ValueError as error:
            value.update(phase='BLOCKED',reason='OUTPUT_VALIDATION_REFUSED: '+str(error));self.save(value);raise

    def _accept_completed(self,value):
        pending=value['pending'];row=self.store.db.execute('SELECT * FROM manual_calls WHERE id=?',(pending['id'],)).fetchone()
        if row['status']!='COMPLETE':raise ValueError('UNCERTAIN_MODEL_CALL_NO_RETRY')
        receipt=json.loads(row['receipt']);work=Path(pending['workspace']);stage=pending['stage'];n=pending['round']
        for name,expected in receipt['output_sha256'].items():
            if digest((work/name).read_bytes())!=expected:raise ValueError('COMPLETED_OUTPUT_CHANGED')
        value['rounds'][stage]=n
        value['blocked_stage']=stage
        if stage=='run_spec_author' and 'execution_scope' in self.config:
            from orchestrator.experiment_context import accept_author
            accept_author(self,value,pending)
        elif stage=='run_spec_author':
            spec=(work/'SPEC.proposed.md').read_text()
            for required in ['run_id: '+self.config['run_id'],'notebook_code_sha256: '+self.config['notebook_code_sha256']]:
                if spec.splitlines().count(required)!=1:raise ValueError('SPEC_NOTEBOOK_BINDING_REQUIRED')
            for kind in ['run_spec','proposed_run_spec']:self.artifact(value,kind,f'SPEC-{n}.md',(work/'SPEC.proposed.md').read_bytes(),n)
            value.update(phase='run_spec_review',spec=str(work/'SPEC.proposed.md'))
        elif stage=='result_interpretation_author':
            decision=read(work/'investigator_next_decision.json')
            from orchestrator.manual_contract import validate_next,validate_summary
            blockers=manual_context.open_blocker_ids(self.context,stage,self.config.get('idea_ids',['Sprint10']))
            validate_next(decision,blockers)
            from orchestrator.manual_contract import repair_summary_length
            original=(work/'interpretation.md').read_text()
            text,repair=repair_summary_length(original)
            interpretation=work/'interpretation.md'
            if repair:
                interpretation=work/'interpretation.formatted.md'
                write_once(interpretation,text.encode())
                repair.update(original_sha256=digest(original.encode()),derived_sha256=digest(text.encode()),
                    original_file='interpretation.md',derived_file=interpretation.name,call_id=pending['id'])
                raw=(json.dumps(repair,sort_keys=True,indent=2)+'\n').encode()
                write_once(work/'format-repair.json',raw)
                receipt['deterministic_format_repair']={'path':str(work/'format-repair.json'),'sha256':digest(raw),
                    'original_sha256':repair['original_sha256'],'derived_sha256':repair['derived_sha256']}
                self.store.finish_call(pending['id'],receipt,'COMPLETE')
                self.artifact(value,'interpretation_original',f'interpretation-original-{n}.md',original.encode(),n)
                self.artifact(value,'interpretation_format_repair',f'format-repair-{n}.json',raw,n)
            else:
                value['artifacts']=[r for r in value['artifacts'] if r['type'] not in {'interpretation_original','interpretation_format_repair'}]
            self.artifact(value,'interpretation',f'interpretation-{n}.md',text.encode(),n)
            self.artifact(value,'investigator_next_decision',f'investigator_next_decision-{n}.json',(work/'investigator_next_decision.json').read_bytes(),n)
            value.update(phase='result_interpretation_review',reason=None,interpretation=str(interpretation),next_decision=str(work/'investigator_next_decision.json'))
        else:
            raw=(work/'review.json').read_bytes()
            if self.config.get('review_contract')=='bound-review/v1':
                from orchestrator.review_contract import scientific
                review=scientific(raw);blockers=[x['category'] for x in review['findings']]
                if review['verdict']!='APPROVE' or blockers:
                    self.criticism(stage,n,raw)
                    from orchestrator.analysis_revisions import enabled,review_transition
                    next_phase,reason=review_transition(review,stage,n) if enabled(self.store,self.config['run_id']) else ('BLOCKED','STRUCTURED_REVIEW_FINDING_OR_REJECTION')
                    value.update(phase=next_phase,reason=reason,
                                 review=str(work/'review.json'),blocker_categories=blockers)
                    value.pop('pending',None);self.save(value);return self.status()
            else:
                review=json.loads(raw);blockers=validate_review(review)
            value.update(review=str(work/'review.json'),blocker_categories=blockers)
            if review['verdict']=='REVISE':
                self.criticism(stage,n,raw)
                value.update(phase='BLOCKED' if n==2 else stage.replace('_review','_author'),reason='UNRESOLVED_REVIEW_BLOCKER' if n==2 else 'REVISION_REQUIRED')
            else:
                if stage=='run_spec_review' and 'execution_scope' in self.config:
                    from orchestrator.experiment_approval import record as record_execution_approval
                    record_execution_approval(self,value,pending)
                if stage=='result_interpretation_review' and 'execution_scope' in self.config:
                    from orchestrator.experiment_acceptance import record as record_results
                    record_results(self,value,pending)
                # Only a later approving independent review closes its own round's
                # recorded blockers, with the original approval bytes as citation.
                folder=self.context/PROFILE;registry=read(folder/'obligations.json');manifest=read(folder/'manifest.json')
                name='current/approval-'+self.finding_prefix(stage)+str(n)+'.json';write_once(self.context/name,raw)
                for record in registry['obligations']:
                    if record['id'].startswith(self.finding_prefix(stage)) and record['status']=='open':
                        record.update(status='closed',disposition={'path':name,'sha256':digest(raw),'start':0,'end':len(raw),'text':raw.decode()})
                atomic(folder/'obligations.json',registry);manifest['obligations']['sha256']=digest((folder/'obligations.json').read_bytes());atomic(folder/'manifest.json',manifest)
                value.update(phase='COMMIT_SPEC' if stage=='run_spec_review' else 'UPDATE_STATE',review=str(work/'review.json'),reason=None)
                if stage=='run_spec_review':value['spec_review']=str(work/'review.json')
        if stage.endswith('_author'):
            from orchestrator.author_revision_accounting import accepted
            accepted(self,pending)
        value.pop('pending',None);self.save(value)
        return self.status()

    def acceptance_path(self,kind):
        path=self.root/'projects/isles24/manual/sprint10'/kind
        return path/'cpu-runs'/self.config['run_id'] if self.config.get('backend')=='cpu' else path/'server-reruns'/self.config['run_id'] if self.config.get('server_rerun') else path

    def advance(self,collect_folder=None,identity_refusal=None):
        with lock(self.state/'driver.lock'):
            try:
                from orchestrator.manual_isolation import cleanup_stale_claude_copies
                removed=cleanup_stale_claude_copies(Path(self.config.get('workspace_root',self.state.parent/(self.state.name+'-scientific-workspaces'))))
                if removed:atomic(self.state/('startup-token-cleanup-'+str(time.time_ns())+'.json'),{'removed_runtime_homes':removed,'original_login_unchanged':True})
                return self._advance(collect_folder,identity_refusal)
            except NetworkUnavailable as error:
                # No reservation or dispatch happened. Preserve the scientific
                # phase; a later scheduled health check may try admission again.
                return {**self.status(),'operational_refusal':str(error),'charged_calls':0}
            except (ValueError,OSError,KeyError,TypeError) as error:
                value=self.current()
                if value['phase']!='BLOCKED':
                    value.update(blocked_stage=value['phase'],phase='BLOCKED',reason=type(error).__name__+': '+str(error))
                    self.save(value)
                return self.status()

    def _advance(self,collect_folder=None,identity_refusal=None):
        self.guard();value=self.current();phase=value['phase']
        if 'execution_scope' in self.config and phase not in {*STAGES,'MODEL_RUNNING','BLOCKED'}:
            from orchestrator.experiment_package import advance
            return advance(self,value,collect_folder,identity_refusal)
        if identity_refusal is not None and phase!='WAIT_OUTPUTS':raise ValueError('IDENTITY_REFUSAL_REQUIRES_WAIT_OUTPUTS')
        if phase in STAGES:return self.model_step(value)
        if phase=='MODEL_RUNNING':return self.accept_completed(value)
        if phase=='COMMIT_SPEC':
            if git(self.root,'status','--porcelain'):raise ValueError('UNRELATED_EDITS_BEFORE_SPEC_COMMIT')
            target=self.acceptance_path('acceptance-spec');private_records.mkdir(target,parents=True,exist_ok=True)
            write_once(target/'SPEC.md',Path(value['spec']).read_bytes())
            write_once(target/'review.json',Path(value['spec_review']).read_bytes())
            subprocess.run(['git','add','--',str(target)],cwd=self.root,check=True)
            subprocess.run(['git','commit','-m','Record independently reviewed Sprint10 acceptance specification'],cwd=self.root,check=True)
            value.update(phase='EMIT_PACKAGE',spec_commit=git(self.root,'rev-parse','HEAD'));self.save(value);return self.status()
        if phase=='EXECUTE_CPU':
            result=self.store.execute(self.config['run_id'],self.state/'package',self.state/'cpu-execution')
            value.update(phase='WAIT_OUTPUTS',cpu_execution=result);self.save(value);return self.status()
        if phase=='EMIT_PACKAGE':
            # Reapply the same scoped preflight to current authority before emission.
            manual_context.prepare(self.context,stage='run_spec_review',idea_ids=self.config.get('idea_ids',['Sprint10']),task=self.task('run_spec_review',value),artifacts=value['artifacts'],workspace=self.state/'emit-preflight')
            prepared=self.state/'prepared-package'
            if prepared.exists():raise ValueError('PREPARATION_EXISTS_INSPECT_NO_RETRY')
            backend=manual_package
            if self.config.get('backend')=='cpu':
                from orchestrator import cpu_package
                backend=cpu_package
            manifest=backend.emit(self.root,prepared,self.config['run_id'],self.config['source'],value['spec'],value['spec_review'])
            if manifest['notebook_code_sha256']!=self.config['notebook_code_sha256']:raise ValueError('REVIEWED_NOTEBOOK_CHANGED')
            binding={'source':self.config['source'],'spec_sha256':manifest['spec_sha256'],'review_sha256':manifest['review_sha256'],'notebook_code_sha256':manifest['notebook_code_sha256']}
            if self.config.get('backend')=='cpu':binding['cpu_config_sha256']=digest(json.dumps(self.config['cpu'],sort_keys=True).encode())
            self.store.submit(self.config['run_id'],binding,prepared,self.state/'package')
            value.update(phase='EXECUTE_CPU' if self.config.get('backend')=='cpu' else 'WAIT_OUTPUTS',manifest=manifest);self.save(value)
            atomic(self.state/'RUN_PACKAGE_READY.json',self.status());return self.status()
        if phase=='WAIT_OUTPUTS':
            validator=validate_return
            if self.config.get('backend')=='cpu':
                if collect_folder is not None or identity_refusal is not None:raise ValueError('CPU_COLLECTION_PATH_IS_BOUND')
                from orchestrator.manual_validation import validate_cpu_return
                validator=validate_cpu_return
                observed=self.store.execute(self.config['run_id'],self.state/'package',self.state/'cpu-execution')
                collect_folder=observed['return_path']
            if identity_refusal is not None:
                if collect_folder is not None:raise ValueError('ONE_TRANSITION_REQUIRED')
                raw=Path(identity_refusal).read_bytes();token=digest(raw)
                saved=self.state/'precomputation-refusals'/(token+'.json');write_once(saved,raw)
                result=self.store.reemit_identity_refusal(self.config['run_id'],value['manifest'],saved,self.state/'package',self.state/'re-emitted'/token)
                value['last_reemission']=result;self.save(value)
                return {**self.status(),'re_emission':result}
            if collect_folder is None:return self.status()
            if not Path(collect_folder).is_dir():
                raise ValueError('COLLECT_FOLDER_NOT_FOUND: supply the existing extracted return directory, not a ZIP or Drive URL; no collection or model call started. Inspect the path and saved state before resuming.')
            try:
                validation=self.store.collect(self.config['run_id'],collect_folder,self.state/'collected',lambda p:validator(p,value['manifest']))
            except ValueError:
                value.update(phase='BLOCKED',reason='COLLECTION_REFUSED_OR_CHANGED_INSPECT_PRESERVED_RETURN');self.save(value);raise
            if validation.get('status')!='VALID':raise ValueError('COLLECTION_NOT_VALID')
            atomic(self.state/'validation.json',validation)
            # Full private return is preserved; only two aggregate CSVs and
            # count-only validation/current execution metadata enter science.
            aggregate='\n\n'.join(name+'\n'+(self.state/'collected/actual'/name).read_text() for name in ['summary_by_recipe.csv','paired_contrasts.csv'])
            self.artifact(value,'result_tables','collected-aggregates.txt',aggregate.encode(),2)
            self.artifact(value,'validation_result','validation.json',json.dumps(validation,sort_keys=True).encode(),1)
            execution={k:value['manifest'][k] for k in ['run_id','source','spec_sha256','notebook_code_sha256','tolerance','baseline_sha256']}
            self.artifact(value,'execution_manifest','execution.json',json.dumps(execution,sort_keys=True).encode(),1)
            self.artifact(value,'execution_receipt','execution-receipt.json',(self.state/'collected/execution_receipt.json').read_bytes(),1)
            self.artifact(value,'package_manifest','package-manifest.json',(self.state/'package/manifest.json').read_bytes(),1)
            value['interventions'].append({'kind':'SERVER_CPU_EXECUTION_AND_COLLECTION' if self.config.get('backend')=='cpu' else 'OPERATOR_COLAB_RUN_AND_COLLECTION','recorded_utc':stamp()})
            value.update(phase='result_interpretation_author');self.save(value);return self.status()
        if phase=='UPDATE_STATE':
            if git(self.root,'status','--porcelain'):raise ValueError('UNRELATED_EDITS_BEFORE_STATE_COMMIT')
            record={'run_id':self.config['run_id'],'source':self.config['source'],'validation_sha256':digest((self.state/'validation.json').read_bytes()),'interpretation_sha256':digest(Path(value['interpretation']).read_bytes()),'review_sha256':digest(Path(value['review']).read_bytes()),'next_decision_sha256':digest(Path(value['next_decision']).read_bytes()),'meaning':'Known-case Sprint10 reproduction, independently reviewed; no new efficacy claim or follow-up execution authority'}
            target=self.acceptance_path('acceptance');private_records.mkdir(target,parents=True,exist_ok=True)
            for name,key in [('interpretation.md','interpretation'),('investigator_next_decision.json','next_decision'),('review.json','review')]:write_once(target/name,Path(value[key]).read_bytes())
            for artifact in value['artifacts']:
                if artifact['type'] in {'interpretation_original','interpretation_format_repair'}:
                    raw=(self.context/artifact['path']).read_bytes()
                    if digest(raw)!=artifact['sha256']:raise ValueError('FORMAT_REPAIR_ARTIFACT_CHANGED')
                    write_once(target/Path(artifact['path']).name,raw)
            write_once(target/'acceptance.json',(json.dumps(record,sort_keys=True,indent=2)+'\n').encode())
            state_path=self.root/PROFILE/'STATE.md';body=state_path.read_text();addition='\n\n## Sprint10 system acceptance\n'+record['meaning']+'\nSource: '+str((target/'acceptance.json').relative_to(self.root))+' SHA256 '+digest((target/'acceptance.json').read_bytes())+'\n'
            if addition not in body:
                if len(body+addition)>20000:raise ValueError('STATE_LIMIT')
                scan('context/STATE.md',(body+addition).encode());private_records.write_text(state_path,body+addition)
            manifest=read(self.root/PROFILE/'manifest.json');manifest['state']['sha256']=digest(state_path.read_bytes());atomic(self.root/PROFILE/'manifest.json',manifest)
            subprocess.run(['git','add','--',str(target),str(state_path),str(self.root/PROFILE/'manifest.json')],cwd=self.root,check=True)
            subprocess.run(['git','commit','-m','Record reviewed Sprint10 known-case acceptance'],cwd=self.root,check=True)
            value.update(phase='REPORT');self.save(value);return self.status()
        if phase=='REPORT':
            status=self.status();calls=[json.loads(row['receipt']) for row in self.store.db.execute('SELECT receipt FROM manual_calls')]
            elapsed=(datetime.now(timezone.utc)-datetime.fromisoformat(self.config['started_utc'])).total_seconds()
            text='# Sprint10 system acceptance\n\nKnown-case comparison reproduced and interpretation independently reviewed. No training, locked-patient access, deployment or new paid resource.\n\n'
            text+=f'Calls: {len(calls)}/{status["call_limit"]}; rounds: {json.dumps(value["rounds"])}; elapsed seconds: {elapsed:.1f}; human interventions: {len([x for x in value["interventions"] if x.get("kind")!="SERVER_CPU_EXECUTION_AND_COLLECTION"])}.\n\n'
            from orchestrator.manual_host_guard import report_status
            text+=report_status(self.state)+'\n\n'
            text+='Connectivity: '+json.dumps(status['connectivity'],sort_keys=True)+'\n\n'
            text+='| Stage | Input characters | Outcome |\n| --- | ---: | --- |\n'
            for call in calls:text+=f'| {call["stage"]} | {call["input_characters"]} | {call["outcome"]} |\n'
            text+='\nSee validation.json, original stage receipts and the committed interpretation/next decision. Remaining scientific limitations and any advisory findings remain in those originals. This does not demonstrate laptop independence.\n'
            if self.config.get('backend')=='cpu':
                text=text.replace('This does not demonstrate laptop independence.','CPU execution and scientific stages are server-owned; M4 scheduling and M6 observation remain separate requirements.')
            private_records.write_text(self.state/'REPORT.md',text);value.update(phase='COMPLETE');self.save(value)
            if self.config.get('backend')=='cpu':self.store.batch.complete_run(self.config['run_id'],{'report_sha256':digest((self.state/'REPORT.md').read_bytes())})
            return self.status()
        if phase=='COMPLETE' and self.config.get('backend')=='cpu':self.store.batch.complete_run(self.config['run_id'],{'report_sha256':digest((self.state/'REPORT.md').read_bytes())})
        return self.status()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['init','status','advance']);parser.add_argument('--state',type=Path,required=True);parser.add_argument('--root',type=Path);parser.add_argument('--server-rerun',action='store_true');parser.add_argument('--cpu',action='store_true');parser.add_argument('--engine-review',type=Path);parser.add_argument('--collect-folder',type=Path);parser.add_argument('--identity-refusal',type=Path);args=parser.parse_args()
    if args.command=='init':result=initialize(args.root,args.state,args.engine_review,args.server_rerun,cpu=args.cpu)
    else:
        driver=Driver(args.state);result=driver.status() if args.command=='status' else driver.advance(args.collect_folder,args.identity_refusal)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
