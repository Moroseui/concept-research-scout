"""Explicit campaign lane for existing scout commands; never writes human markers."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone

from orchestrator.campaign import sha, verify_experiment
from orchestrator.publication import copy_verified, inventory

COMMANDS={'probe-build','verify-probe','package-colab','validate-bundle','record-result','interpret-build'}


def context(root, args):
    if args.campaign != 'isles24-pilot' or args.experiment not in ('P001','P002','P003') or getattr(args,'idea',None) is not None:
        raise ValueError('explicit campaign/experiment required; numbered ideas use historical authority')
    base=Path(root)/'campaigns'/args.campaign
    exp=base/'experiments'/args.experiment
    if exp.is_symlink() or not exp.resolve().is_relative_to(base.resolve()):
        raise ValueError('campaign experiment escapes its root')
    d=verify_experiment(root,args.experiment)
    if d['experiment'] != args.experiment:
        raise ValueError('investigator decision names a different experiment')
    if args.experiment != 'P001':
        previous=base/'experiments'/f'P{int(args.experiment[1:])-1:03d}'/'interpretation_receipt.json'
        if not previous.exists() or json.loads(previous.read_text()).get('status')!='AGENT_REVIEWED_NOT_HUMAN_RATIFIED':
            raise ValueError('follow-up requires completed reviewed predecessor interpretation')
        prior=previous.parent; prior_receipt=json.loads(previous.read_text())
        prior_import=json.loads((prior/'import_receipt.json').read_text())
        if prior_receipt.get('import_receipt_sha256')!=sha(prior/'import_receipt.json') or prior_receipt.get('interpretation_sha256')!=sha(prior/'interpretation.md') or prior_receipt.get('review_sha256')!=sha(prior/'interpret_review.md') or prior_import.get('spec_sha256')!=sha(prior/'SPEC.md'):
            raise ValueError('predecessor interpretation evidence changed')
    return base,exp,d


def write(path,obj):
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')


def event(exp,stage,decision,**fields):
    rec={'stage':stage,'actor_type':'agent','family':decision['family'],'model':decision['model'],
         'authority':decision['authority'],'campaign_sha256':decision['campaign_sha256'],
         'spec_sha256':decision['spec_sha256'],'utc':datetime.now(timezone.utc).isoformat(),**fields}
    if 'session_id' in decision: rec['session_id']=decision['session_id']
    if 'decision_sha256' in decision: rec['decision_sha256']=decision['decision_sha256']
    with (exp/'lifecycle.jsonl').open('a') as f: f.write(json.dumps(rec,sort_keys=True)+'\n')



def commit(sc,exp,message,allowed):
    """Refuse cross-scope writes before staging; never sweep unrelated work."""
    tracked=subprocess.check_output(['git','diff','--name-only','-z','HEAD'],cwd=sc.ROOT).split(b'\0')
    new=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=sc.ROOT).split(b'\0')
    prefix=exp.relative_to(sc.ROOT).as_posix()+'/'
    paths=[]
    for raw in set(tracked+new):
        if not raw: continue
        name=raw.decode()
        if not name.startswith(prefix) or name[len(prefix):] not in allowed:
            raise ValueError('campaign stage changed a path outside its allowed artifacts: '+name)
        paths.append(name)
    if not paths: return
    if paths:
        subprocess.run(['git','add','--',*sorted(paths)],cwd=sc.ROOT,check=True)
    subprocess.run(['git','commit','-m',message],cwd=sc.ROOT,check=True,capture_output=True)


def run_isolated_stage(sc,exp,family,stage,body,outputs,*,authority_root=None):
    """Reuse scout's receipted agent primitive in an aggregate-only disposable repo."""
    import os, shutil, tempfile
    from orchestrator.scientific_authority import stage_context
    body=stage_context(authority_root or sc.ROOT,exp,family,stage)+body
    root=Path(tempfile.mkdtemp(prefix='scout-campaign-stage-'))
    source_root=sc.ROOT
    source_state=getattr(sc,"STATE",None)
    shutil.copy2(Path(source_root)/'AGENTS.toml',root/'AGENTS.toml')
    subprocess.run(['git','init','-q',str(root)],check=True)
    prompt=root/'prompt.md'
    prompt.write_text('Work only in this disposable directory. No patient data or original repository is available here. Do not seek it elsewhere. Write '+', '.join(outputs)+' in the current directory. No human ratification.\n'+body)
    # Keep ambient numbered-idea role rotation out of this explicitly attributed lane.
    (root/'state.json').write_text('{"active_cycle": 0}\n')
    subprocess.run(['git','add','AGENTS.toml','prompt.md','state.json'],cwd=root,check=True)
    subprocess.run(['git','-c','user.name=Campaign stage','-c','user.email=campaign@local.invalid','commit','-qm','Bound aggregate-only stage inputs'],cwd=root,check=True)
    removed={key:os.environ.pop(key,None) for key in ('ANTHROPIC_API_KEY','OPENAI_API_KEY','SCOUT_CI')}
    try:
        sc.ROOT=root
        sc.STATE=root/'state.json'
        sc.run_agent(prompt,family,stage=stage,log_path=root/'console.log')
    finally:
        sc.ROOT=source_root
        if source_state is None: del sc.STATE
        else: sc.STATE=source_state
        for key,value in removed.items():
            if value is not None: os.environ[key]=value
        for src,dest in [('prompt.md','prompt_'+stage+'.md'),('console.log','log_'+stage+'.txt')]:
            if (root/src).exists(): shutil.copy2(root/src,exp/dest)
        if (root/'stage_provenance.jsonl').exists():
            with (exp/'stage_provenance.jsonl').open('a') as f: f.write((root/'stage_provenance.jsonl').read_text())
    for name in outputs:
        f=root/name
        if f.is_symlink() or not f.is_file(): raise ValueError('agent stage missing required regular artifact: '+name)
        shutil.copy2(f,exp/name)
    return json.loads((root/'stage_provenance.jsonl').read_text().splitlines()[-1])

def load_validator(exp):
    spec=importlib.util.spec_from_file_location('campaign_return_validator',exp/'validate_return.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def require_review(base,exp):
    verify_experiment(exp.parents[3],exp.name,review=True)


def _dispatch(sc,args):
    """Entered only via explicit --campaign; ordinary scout paths are unchanged."""
    base,exp,d=context(sc.ROOT,args)
    command=args.cmd
    if command=='probe-build':
        sc._require_clean_tree('campaign probe-build')
        if not (exp/'run.py').is_file():
            raise ValueError('campaign runner missing: author code under the frozen delegated specification first')
        # Existing reviewed investigator code follows the standard build's
        # existing-code route. No fake HUMAN_APPROVED_PROBE is synthesized.
        require_review(base,exp)
        subprocess.run([sys.executable,'-m','py_compile',str(exp/'run.py')],check=True)
        write(exp/'build_receipt.json',{'authority':d['authority'],'actor_type':'agent',
              **{k:d[k] for k in ('session_id','decision_sha256','policy') if k in d},
              'family':d['family'],'model':d['model'],'spec_sha256':sha(exp/'SPEC.md'),
              'code_sha256':sha(exp/'run.py'),'review_sha256':sha(exp/'review.json')})
        event(exp,'PROBE_BUILT',d,review_sha256=sha(exp/'review.json'))
        commit(sc,exp,f'campaign {args.experiment}: investigator build with opposing review',{'build_receipt.json','lifecycle.jsonl'})
        return
    require_review(base,exp)
    if command in ('verify-probe','package-colab'):
        build=json.loads((exp/'build_receipt.json').read_text())
        if any(build.get(key)!=sha(exp/file) for key,file in [('spec_sha256','SPEC.md'),('code_sha256','run.py'),('review_sha256','review.json')]):
            raise ValueError('campaign build receipt stale')
    if command=='verify-probe':
        sc._require_clean_tree('campaign verify-probe')
        requirements=(exp/'requirements.txt').read_text().splitlines()
        from importlib.metadata import version
        for line in requirements:
            if not line.strip() or line.lstrip().startswith('#'): continue
            name,expected=line.split('==')
            if version(name)!=expected: raise ValueError('install pinned experiment requirements before verification')
        subprocess.run([sys.executable,str(exp/'run.py'),'--preflight'],cwd=sc.ROOT,check=True)
        if not (Path(sc.ROOT)/'tests'/f'test_prediction_{args.experiment.lower()}.py').is_file():
            raise ValueError('experiment-specific synthetic tests required')
        subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p',f'test_prediction_{args.experiment.lower()}.py','-q'],cwd=sc.ROOT,check=True)
        write(exp/'verification.json',{'build_receipt_sha256':sha(exp/'build_receipt.json'),'status':'SYNTHETIC_VERIFIED_NO_PATIENT_EXECUTION'})
        event(exp,'PROBE_VERIFIED',d)
        commit(sc,exp,f'campaign {args.experiment}: synthetic verification',{'verification.json','lifecycle.jsonl'})
        return
    if command=='package-colab':
        sc._require_clean_tree('campaign package-colab')
        v=json.loads((exp/'verification.json').read_text())
        if v.get('build_receipt_sha256')!=sha(exp/'build_receipt.json'):
            raise ValueError('verification does not bind current build')
        if args.experiment!='P001': raise ValueError('follow-up notebook generator must be reviewed before packaging')
        from scripts import package_pilot
        original_root=package_pilot.ROOT
        try:
            package_pilot.ROOT=Path(sc.ROOT)
            package_pilot.main('HEAD')
        finally: package_pilot.ROOT=original_root
        changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=sc.ROOT,text=True).splitlines()
        changed+=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=sc.ROOT,text=True).splitlines()
        permitted={str((base/'colab/synthetic_execution.ipynb').relative_to(sc.ROOT)),str((exp/'colab_P001.ipynb').relative_to(sc.ROOT))}
        if set(changed)-permitted: raise ValueError('notebook generation exceeded scope')
        if not changed: return
        subprocess.run(['git','add','--',*sorted(permitted)],cwd=sc.ROOT,check=True)
        subprocess.run(['git','commit','-m',f'campaign {args.experiment}: notebook pinned to verified reviewed execution source'],cwd=sc.ROOT,check=True,capture_output=True)
        return
    if command in ('validate-bundle','record-result'):
        if not args.bundle or not args.private or not args.console:
            raise ValueError('campaign return requires --bundle, --private and --console')
        if command=='record-result': sc._require_clean_tree('campaign record-result')
        result=load_validator(exp).verify(Path(args.bundle),Path(args.private),Path(args.console))
        if command=='validate-bundle':
            print(json.dumps(result,indent=2)); return
        manifest=inventory(args.bundle)
        if result.get('file_sha256')!=manifest:
            raise ValueError('returned bytes changed after semantic validation')
        identity=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
        destination=exp/'results'/identity[:16]
        copied=copy_verified(args.bundle,destination,json.loads((exp/'publication.json').read_text()))
        if copied!=manifest or inventory(destination)!=manifest:
            raise ValueError('import bytes differ from validated return')
        receipt={'status':'VALIDATED_EXPLORATORY_IMPORT','bundle':destination.relative_to(sc.ROOT).as_posix(),
                 'bundle_file_sha256':manifest,'validation':result,'spec_sha256':sha(exp/'SPEC.md'),
                 'review_sha256':sha(exp/'review.json'),'authority':'campaign_delegated_investigator'}
        write(exp/'import_receipt.json',receipt)
        event(exp,'RESULT_IMPORTED',d,bundle_manifest_sha256=identity)
        # Private checkpoint/console bytes and paths are never copied into Git.
        subprocess.run(['git','add','-f','--',str(destination)],cwd=sc.ROOT,check=True)
        commit(sc,exp,f'campaign {args.experiment}: validated aggregate result import',{'import_receipt.json','lifecycle.jsonl'} | {'results/'+identity[:16]+'/'+name for name in manifest})
        return
    if command=='interpret-build':
        sc._require_clean_tree('campaign interpret-build')
        receipt=json.loads((exp/'import_receipt.json').read_text())
        bundle=Path(sc.ROOT)/receipt['bundle']
        if not bundle.resolve().is_relative_to((exp/'results').resolve()) or bundle.is_symlink():
            raise ValueError('import receipt escapes campaign results')
        if inventory(bundle)!=receipt['bundle_file_sha256'] or receipt['spec_sha256']!=sha(exp/'SPEC.md') or receipt['review_sha256']!=sha(exp/'review.json'):
            raise ValueError('interpretation requires the unchanged validated import')
        # The existing receipted execution primitive owns both agent legs.
        # Prompts carry only approved aggregate contents, never private logs.
        aggregate='\n'.join(f'FILE {name}\n'+(bundle/name).read_text() for name in sorted(receipt['bundle_file_sha256']))
        author=run_isolated_stage(sc,exp,'codex','interpret',
            'Interpret the exploratory campaign result. Cite aggregate files, state uncertainty and limitations. Write investigator_next_decision.json with exactly status PROPOSAL_ONLY and a nonempty rationale. This cannot authorize a follow-up or claim human authority.\n'+(exp/'SPEC.md').read_text()+'\n'+aggregate,
            ['interpretation.md','investigator_next_decision.json'])
        proposal=json.loads((exp/'investigator_next_decision.json').read_text())
        if set(proposal)!={'status','rationale'} or proposal['status']!='PROPOSAL_ONLY' or not isinstance(proposal['rationale'],str) or not proposal['rationale'].strip():
            raise ValueError('interpretation next decision must remain an attributed proposal')
        require_review(base,exp)
        reviewer=run_isolated_stage(sc,exp,'claude','interpret_review',
            'Review this interpretation against the aggregates. End interpret_review.md with fenced JSON verdict APPROVE or REVISE.\n'+(base/'CAMPAIGN.md').read_text()+'\n'+(exp/'SPEC.md').read_text()+'\n'+(exp/'interpretation.md').read_text()+'\n'+(exp/'investigator_next_decision.json').read_text()+'\n'+aggregate,
            ['interpret_review.md'])
        require_review(base,exp)
        verdict=sc._interpret_review_verdict(exp) or {}
        if author.get('family_effective')!='codex' or reviewer.get('family_effective')!='claude' or any(r.get('exit_class')!='ok' or r.get('ci') for r in (author,reviewer)) or verdict.get('verdict')!='APPROVE':

            raise ValueError('opposing-family interpretation approval required; partial evidence preserved')
        write(exp/'interpretation_receipt.json',{'status':'AGENT_REVIEWED_NOT_HUMAN_RATIFIED','import_receipt_sha256':sha(exp/'import_receipt.json'),
              'interpretation_sha256':sha(exp/'interpretation.md'),'proposal_sha256':sha(exp/'investigator_next_decision.json'),'review_sha256':sha(exp/'interpret_review.md'),
              'author_family':author['family_effective'],'reviewer_family':reviewer['family_effective']})
        event(exp,'INTERPRETATION_REVIEWED',d)
        commit(sc,exp,f'campaign {args.experiment}: opposing-family interpretation review',{'context_interpret.json','context_interpret_review.json','prompt_interpret.md','prompt_interpret_review.md','interpretation.md','investigator_next_decision.json','interpret_review.md','stage_provenance.jsonl','log_interpret.txt','log_interpret_review.txt','interpretation_receipt.json','lifecycle.jsonl'})
        return
    raise ValueError('unsupported campaign command')


def dispatch(sc,args):
    try:
        return _dispatch(sc,args)
    except Exception as error:
        # Never erase failed prompts, original consoles or completed stage receipts.
        # Leave them reviewable locally; do not publish unchecked agent output.
        if args.cmd=='interpret-build':
            try:
                base,exp,d=context(sc.ROOT,args)
                event(exp,'INTERPRETATION_FAILED',d,exception_type=type(error).__name__)
            except (OSError,ValueError,KeyError): pass
        raise



def require_interpretation(exp):
    """An acceptance never promotes unreviewed or changed result evidence."""
    exp = Path(exp)
    receipt = json.loads((exp / 'interpretation_receipt.json').read_text())
    if receipt.get('status') != 'AGENT_REVIEWED_NOT_HUMAN_RATIFIED':
        raise ValueError('CAMPAIGN_REVIEWED_INTERPRETATION_REQUIRED')
    for key, name in [('import_receipt_sha256', 'import_receipt.json'),
                      ('interpretation_sha256', 'interpretation.md'),
                      ('review_sha256', 'interpret_review.md'),
                      ('proposal_sha256', 'investigator_next_decision.json')]:
        if receipt.get(key) != sha(exp / name):
            raise ValueError('CAMPAIGN_INTERPRETATION_CHANGED')
    if receipt.get('author_family') == receipt.get('reviewer_family') or set(
            (receipt.get('author_family'), receipt.get('reviewer_family'))) != {'codex', 'claude'}:
        raise ValueError('CAMPAIGN_OPPOSING_INTERPRETATION_REVIEW_REQUIRED')
    proposal = json.loads((exp / 'investigator_next_decision.json').read_text())
    if set(proposal) != {'status', 'rationale'} or proposal['status'] != 'PROPOSAL_ONLY' or not proposal['rationale']:
        raise ValueError('CAMPAIGN_ORIGINAL_NEXT_PROPOSAL_REQUIRED')
    return receipt


def verify_application(root, experiment, path):
    from orchestrator import campaign, scientific_authority as authority
    exp = campaign.experiment_root(root, experiment)
    record = json.loads(authority.read(path))
    keys = {'schema', 'status', 'action', 'experiment', 'decision_sha256', 'decision_path',
            'proposal', 'actor', 'policy', 'transition'}
    if (set(record) != keys or record['schema'] != 'campaign-scientific-application/v1' or
            record['experiment'] != experiment or record['status'] != 'AGENT_DECISION_APPLIED'):
        raise ValueError('CAMPAIGN_APPLICATION_SCHEMA')
    relative = Path(record['decision_path'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('CAMPAIGN_APPLICATION_PATH')
    decision = exp / relative
    if decision.parent.parent != exp / 'delegated_decisions' or decision.name != 'decision.json':
        raise ValueError('CAMPAIGN_APPLICATION_PATH')
    request = campaign.decision_request(root, experiment, record['action'], record['proposal'])
    checked = authority.verify(root, decision, action=request['action'], subject=request['subject'],
                               bindings=request['bindings'], expected_transition=request['transition'])
    if (record['decision_sha256'] != checked['_decision_sha256'] or
            record['actor'] != checked['actor'] or record['policy'] != checked['policy'] or
            record['transition'] != checked['transition']):
        raise ValueError('CAMPAIGN_APPLICATION_BINDING')
    return record, checked


def apply_decision(root, experiment, action, decision_path, proposal=None):
    """Apply an explicit reviewed judgment with exclusive receipts, never execution.

    The original proposal and model packet remain intact. A completed duplicate
    returns its checked receipt; an interrupted copy is retained for reconciliation.
    No old investigator decision, scientific artifact or human marker is replaced.
    """
    import os
    from orchestrator import campaign, scientific_authority as authority
    exp = campaign.experiment_root(root, experiment)
    request = campaign.decision_request(root, experiment, action, proposal)
    checked = authority.verify(root, decision_path, action=action, subject=request['subject'],
                               bindings=request['bindings'], expected_transition=request['transition'])
    target = exp / ('agent_interpretation_acceptance.json' if action == 'accept_interpretation'
                    else 'agent_adoption.json')
    if target.exists() or target.is_symlink():
        record, previous = verify_application(root, experiment, target)
        if previous['_decision_sha256'] != checked['_decision_sha256']:
            raise ValueError('CAMPAIGN_EXISTING_DECISION_PRESERVED')
        return {**record, 'duplicate': True}
    directory = exp / 'delegated_decisions' / checked['_decision_sha256']
    if directory.parent.is_symlink():
        raise ValueError('CAMPAIGN_SYMLINK_PATH')
    directory.parent.mkdir(exist_ok=True, mode=0o700)
    directory.mkdir(mode=0o700)  # Existing partial applications require explicit reconciliation.
    original = Path(decision_path).absolute().parent
    files = {'decision.json': authority.read(decision_path)}
    for key in ('author_provenance', 'reviewer_provenance', 'judgment', 'review'):
        descriptor = checked[key]
        files[descriptor['path']] = authority.read(original / descriptor['path'])
    for name, raw in files.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with path.open('xb') as handle:
            os.chmod(path, 0o600)
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
    campaign.require_no_human_stop(root, experiment)
    # Recheck source/evidence after copying, before creating the application receipt.
    fresh = campaign.decision_request(root, experiment, action, proposal)
    if fresh != request:
        raise ValueError('CAMPAIGN_DECISION_INPUT_CHANGED')
    record = {'schema': 'campaign-scientific-application/v1', 'status': 'AGENT_DECISION_APPLIED',
              'action': action, 'experiment': experiment,
              'decision_sha256': checked['_decision_sha256'],
              'decision_path': str((directory / 'decision.json').relative_to(exp)),
              'proposal': request['bindings']['proposal']['path'] if proposal is not None else None,
              'actor': checked['actor'], 'policy': checked['policy'], 'transition': checked['transition']}
    # Verify the copied original packet before the final exclusive application marker.
    authority.verify(root, directory / 'decision.json', action=action, subject=request['subject'],
                     bindings=request['bindings'], expected_transition=request['transition'])
    with target.open('xb') as handle:
        os.chmod(target, 0o600)
        handle.write(authority.encoded(record) + b'\n'); handle.flush(); os.fsync(handle.fileno())
    return {**record, 'duplicate': False}
