"""Deterministic manual-lane acceptance/recovery contracts. All model outputs fake."""
import ast
from datetime import datetime,timezone,timedelta
import json
import re
from pathlib import Path
import shutil
import subprocess
import pytest
from orchestrator import manual_driver as driver, manual_executor as executor, manual_package, manual_validation as validation, dispatch_limiter
from test_context_budget import root, ROOT, add_obligation, save_manifest


def policy():return {'status':'RATIFIED','operator_approval':'synthetic explicit step-d operator grant','state_write_permission':'OPERATOR_AUTHORIZED','n':4,'window':'UTC_CALENDAR_DAY','state_ref':dispatch_limiter.REF,'manual_semantics':'OPERATOR_STEP_D_MAX_EIGHT'}


def test_driver_uses_only_guarded_builder_and_transport_never_assembles():
    tree=ast.parse((ROOT/'orchestrator/manual_driver.py').read_text())
    calls=[node for node in ast.walk(tree) if isinstance(node,ast.Call)]
    assert any(isinstance(c.func,ast.Attribute) and isinstance(c.func.value,ast.Name) and c.func.value.id=='manual_context' and c.func.attr in {'build','prepare'} for c in calls)
    for module in ['manual_driver.py','manual_stage.py']:
        text=(ROOT/'orchestrator'/module).read_text();code=ast.parse(text)
        assert not any(isinstance(c,ast.Call) and isinstance(c.func,ast.Attribute) and c.func.attr=='assemble' for c in ast.walk(code))
        assert not any(isinstance(n,ast.ImportFrom) and 'context_budget' in (n.module or '') for n in ast.walk(code))
        assert not any(isinstance(n,ast.Name) and n.id=='eval' for n in ast.walk(code))


def test_job_store_duplicate_emission_and_collection_do_not_run_again(tmp_path):
    store=executor.ManualExecutor(tmp_path/'jobs.sqlite')
    prepared=tmp_path/'prepared';prepared.mkdir();(prepared/'notebook').write_text('synthetic')
    target=tmp_path/'package';binding={'source':'a'*40,'spec_sha256':'b'*64}
    assert store.submit('run',binding,prepared,target)['status']=='WAITING_FOR_OPERATOR_COLAB'
    assert store.submit('run',binding,prepared,target)['status']=='ALREADY_EMITTED_NO_RESUBMISSION'
    assert store.db.execute('SELECT count(*) FROM events').fetchone()[0]==2
    with pytest.raises(ValueError,match='different inputs'):store.submit('run',{'source':'c'*40},prepared,target)
    incoming=tmp_path/'incoming';incoming.mkdir();(incoming/'output').write_text('observed')
    validate=lambda p:{'status':'VALID','sha256':executor.inventory(p)}
    assert store.collect('run',incoming,tmp_path/'collected',validate)['status']=='VALID'
    assert store.collect('run',incoming,tmp_path/'collected',validate)['duplicate_collection']
    (incoming/'output').write_text('changed')
    with pytest.raises(ValueError,match='RETURN_CONFLICT'):store.collect('run',incoming,tmp_path/'collected',validate)


def test_uncertain_submission_and_partial_collection_are_not_retried(tmp_path):
    s=executor.ManualExecutor(tmp_path/'jobs.sqlite');s.register('run',{'v':1})
    lease=s.claim('run');s.complete_event('run','acquire','VALIDATED',lease=lease['lease']);s.claim('run')
    source=tmp_path/'source';source.mkdir()
    with pytest.raises(ValueError,match='UNCERTAIN_MANUAL'):s.submit('run',{'v':1},source,tmp_path/'package')
    assert not (tmp_path/'package').exists()
    assert s.get('run')['status']=='BLOCKED'


def test_accounting_replays_cap_and_halt_survive_midnight(tmp_path):
    s=executor.ManualExecutor(tmp_path/'jobs.sqlite');p=policy();s.initialize_allowance(p)
    stages=list(driver.STAGES)*2
    for i,stage in enumerate(stages):
        ident,n,receipt=s.reserve_call('run',stage,'a'*40,'astra/manual-test',p,{'synthetic':True})
        s.finish_call(ident,receipt,'COMPLETE')
        replay=dispatch_limiter.admit_manual(executor.Accounts(s),p,{'run_id':ident,'attempt':'1','source':'a'*40,'branch':'astra/manual-test'})
        assert replay['duplicate_admission'] and replay['count']==i+1
    before=executor.Accounts(s).read();assert before[1]['count']==8 and before[1]['halted']
    with pytest.raises(ValueError,match='CALL_LIMIT'):s.reserve_call('run',stages[0],'a'*40,'astra/manual-test',p,{})
    event={'run_id':'d'*64,'attempt':'1','source':'a'*40,'branch':'astra/manual-test'}
    future=datetime.now(timezone.utc)+timedelta(days=1)
    assert dispatch_limiter.admit_manual(executor.Accounts(s),p,event,future)['status']=='HALTED_OPERATOR_RESET_REQUIRED'
    s.initialize_allowance(p);assert executor.Accounts(s).read()==before


def test_uncertain_model_and_unknown_stage_cannot_spend_another_unit(tmp_path):
    s=executor.ManualExecutor(tmp_path/'jobs.sqlite');p=policy();s.initialize_allowance(p)
    with pytest.raises(ValueError,match='STAGE_REQUIRED'):s.reserve_call('r','other','a'*40,'astra/manual-test',p,{})
    ident,_,receipt=s.reserve_call('r',driver.STAGES[0],'a'*40,'astra/manual-test',p,{})
    s.finish_call(ident,receipt,'UNCERTAIN')
    with pytest.raises(ValueError,match='UNCERTAIN_MODEL_CALL'):s.reserve_call('r',driver.STAGES[1],'a'*40,'astra/manual-test',p,{})
    assert executor.Accounts(s).read()[1]['count']==1


def tables(folder,value='0.5'):
    folder.mkdir()
    for name in validation.TABLES:(folder/name).write_text('recipe,patients,dice\nsynthetic,99,'+value+'\n')


def test_predeclared_table_tolerance_and_differences(tmp_path):
    a,b=tmp_path/'a',tmp_path/'b';tables(a);tables(b,'0.50000000001')
    assert validation.compare_tables(a,b,'/old','/new')['status']=='VALID'
    (b/'paired_contrasts.csv').write_text('recipe,patients,dice\nsynthetic,99,0.6\n')
    r=validation.compare_tables(a,b,'/old','/new');assert r['status']=='INVALID' and r['differences'][0]['column_index']==2
    tables2=tmp_path/'c';tables(tables2);(tables2/'completion.csv').write_text('recipe,patients,dice\nsynthetic,99.00000000001,0.5\n')
    assert validation.compare_tables(a,tables2,'/old','/new')['status']=='INVALID'


def test_emitted_notebook_matches_preview_and_preserves_scientific_cells(tmp_path):
    original=json.loads((ROOT/'projects/isles24/manual/sprint10/isles24_sprint10_r2_exclusion_reference.ipynb').read_text())
    raw=manual_package.notebook_bytes(ROOT,'synthetic-run');new=json.loads(raw)
    assert len(new['cells'])==len(original['cells'])+3
    assert ''.join(new['cells'][0]['source'])=="from google.colab import drive\ndrive.mount('/content/drive')\n"
    for i in range(3,len(original['cells'])):assert new['cells'][i+2]['source']==original['cells'][i]['source']
    source=''.join(new['cells'][4]['source']);assert 'drive.mount' not in source and 'git fetch' not in source
    assert 'assert len(CASES) == 99' in source
    assert validation.TOLERANCE['bootstrap_seed']==0


def private_copied_fixture(folder):
    # shutil.copytree(copy2) carries repository 0644 modes despite UMask=0077.
    # Only synthetic fixture copies are normalized, never originals or the
    # explicitly planted unsafe files in test_private_records.
    for p in [Path(folder),*Path(folder).rglob('*')]:
        if not p.is_symlink():p.chmod(0o700 if p.is_dir() else 0o600)


@pytest.fixture
def lane(root,tmp_path,monkeypatch):
    # This is an entirely synthetic initialized lane, not an engine approval.
    private_copied_fixture(root)
    state=tmp_path/'lane';state.mkdir();context=state/'context';shutil.copytree(root,context,ignore=shutil.ignore_patterns('lane'));private_copied_fixture(context)
    store=executor.ManualExecutor(state/'jobs.sqlite');store.initialize_allowance(policy())
    review=state/'engine-review.md';review.write_text('Synthetic engine review fixture')
    auth=root/'docs/STEP_D_AUTHORIZATION.md';auth.parent.mkdir(exist_ok=True);auth.write_text('Synthetic scope')
    config={'run_id':'synthetic-stepd','source':'a'*40,'branch':'astra/manual-test','root':str(root),'context':str(context),
      'clients':{},'policy':policy(),'private':str(tmp_path/'private'),'notebook_code_sha256':'b'*64,
      'engine_review':{'path':str(review),'sha256':executor.digest(review.read_bytes())},'authority_sha256':executor.digest(auth.read_bytes()),
      'engine_files':{},'profile_files':{},'started_utc':driver.stamp()}
    executor.atomic(state/'lane.json',config)
    value={'phase':driver.STAGES[0],'rounds':{},'artifacts':[],'interventions':[]}
    store.db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps(value),));store.db.close()
    subprocess.run(['git','init','-q',str(root)],check=True)
    subprocess.run(['git','switch','-qc','astra/manual-test'],cwd=root,check=True)
    return state


def fake_author(work,stage,clients,expected_sha256):
    assert executor.digest((work/'prompt.md').read_bytes())==expected_sha256
    pin=re.search(r'^notebook_code_sha256: ([a-f0-9]{64})$',(work/'prompt.md').read_text(),re.M).group(1)
    (work/'SPEC.proposed.md').write_text('# Synthetic specification\nrun_id: synthetic-stepd\nnotebook_code_sha256: '+pin+'\n')
    return {'family_effective':'codex','exit_class':'ok','synthetic':True}


def test_one_transition_call_records_and_recovery_do_not_duplicate(lane):
    d=driver.Driver(lane,runner=fake_author);status=d.advance()
    assert status['phase']=='run_spec_review' and status['calls_used']==1
    assert d.status()['calls_used']==1
    # Restore the saved in-flight state after a hypothetical lost final save.
    row=d.store.db.execute('SELECT * FROM manual_calls').fetchone();receipt=json.loads(row['receipt'])
    v=d.current();v.update(phase='MODEL_RUNNING',pending={'id':row['id'],'stage':'run_spec_author','round':1,'workspace':receipt['workspace']});d.save(v)
    assert d.advance()['calls_used']==1 and d.current()['phase']=='run_spec_review'


def test_scoped_stop_prevents_call_and_accounting(lane):
    d=driver.Driver(lane,runner=lambda *args:pytest.fail('model must not run'))
    # add_obligation fixture defaults P001; set exact Sprint10 stage scope.
    add_obligation(d.context);p=d.context/driver.PROFILE/'obligations.json';v=json.loads(p.read_text());v['obligations'][-1]['scope'].update(idea_ids=['Sprint10'],stages=['run_spec_author']);p.write_text(json.dumps(v));save_manifest(d.context)
    assert d.advance()['phase']=='BLOCKED'
    assert 'SCOPED_STOP' in d.status()['reason']
    assert (lane/'DECISION_REQUEST.md').is_file()
    assert d.status()['calls_used']==0


def test_two_review_rounds_block_and_keep_findings(lane):
    d=driver.Driver(lane,runner=fake_author);d.advance()
    def reject(work,*args):
        (work/'review.json').write_text(json.dumps({'verdict':'REVISE','rationale':'BLOCKER[code/spec mismatch] Synthetic unresolved mismatch.'}))
        return {'family_effective':'claude','exit_class':'ok','synthetic':True}
    d.runner=reject;assert d.advance()['phase']=='run_spec_author'
    d.runner=fake_author;d.advance();d.runner=reject
    assert d.advance()['phase']=='BLOCKED' and d.status()['calls_used']==4
    assert d.advance()['calls_used']==4
    rows=json.loads((d.context/driver.PROFILE/'obligations.json').read_text())['obligations']
    assert len([x for x in rows if x['id'].startswith('STEPD-') and x['status']=='open'])==2


def test_engine_changed_and_operator_halt_prevent_call(lane):
    d=driver.Driver(lane,runner=lambda *x:pytest.fail('no call'))
    (lane/'HALT').write_text('operator stop')
    assert 'OPERATOR_HALT' in d.advance()['reason']
    value=d.current();value['phase']='run_spec_author';d.save(value)
    (lane/'HALT').unlink();Path(d.config['engine_review']['path']).write_text('altered')
    assert 'ENGINE_REVIEW_CHANGED' in d.advance()['reason']
    assert d.status()['calls_used']==0



def make_return(folder,manifest,private):
    folder.mkdir()
    cases=[f'synthetic-{i}' for i in range(99)]
    for sub in ['baseline','actual']:
        target=folder/sub;tables(target)
        (target/'all_percase.csv').write_text('case,recipe,dice\n'+''.join(c+',synthetic,0.5\n' for c in cases))
        document={'sprint8':{'fingerprint':'875c56c278'},'sprint9':{'fingerprint':'0a60362503'},'hard_checks':{'same':True},'clinical_checks':{},'provisional':False,'states':{'complete':1},'matched_amount':{'paired':1},'rows':{'sprint8':99,'sprint9':99},'code_version':'synthetic-original','utc':'synthetic-before'}
        if sub=='actual':
            identity=validation.expected_identity(manifest['private_files'])
            document.update(run_identity=identity,fingerprint=executor.digest(json.dumps(identity,sort_keys=True).encode())[:12],code_version='synthetic-new',utc='synthetic-now')
        for name in ['comparison_reference.json','compatibility_report.json']:
            record={key:document.get(key,{} if key in ['cache_identity','clinical_fields'] else []) for key in validation.BASELINE_JSON_KEYS[name]}
            if sub=='actual':record.update({k:document[k] for k in ['fingerprint','run_identity']})
            (target/name).write_text(json.dumps(record))
    manifest.setdefault('baseline_sha256',executor.inventory(folder/'baseline'))
    manifest.setdefault('baseline_json_keys',{name:sorted(executor.read(folder/'baseline'/name)) for name in ['comparison_reference.json','compatibility_report.json']})
    receipt={k:manifest[k] for k in ['run_id','source','spec_sha256','notebook_code_sha256','private_files']}
    receipt.update(manifest_sha256=executor.digest(json.dumps(manifest,sort_keys=True).encode()),development_count=99,training_performed=False,tolerance=validation.TOLERANCE,baseline_output_path=validation.BASELINE_PATH,actual_output_path=validation.expected_output_path(manifest))
    for sub in ['baseline','actual']:receipt[sub+'_sha256']=executor.inventory(folder/sub)
    executor.atomic(folder/'execution_receipt.json',receipt)
    executor.atomic(folder/'started.json',{'run_id':manifest['run_id'],'manifest_sha256':receipt['manifest_sha256'],'baseline_sha256':manifest['baseline_sha256']})


def private_fixture(folder):
    folder.mkdir()
    (folder/'split_manifest.csv').write_text('case_id,population\n'+''.join(f'synthetic-{i},census\n' for i in range(100)))
    (folder/'excluded_cases.json').write_text(json.dumps(['synthetic-99']))
    return executor.inventory(folder)


def test_return_identity_membership_and_missing_originals_fail_closed(tmp_path):
    private=tmp_path/'private';hashes=private_fixture(private)
    manifest={'run_id':'synthetic','source':'a'*40,'spec_sha256':'b'*64,'notebook_code_sha256':'c'*64,'private_files':hashes}
    folder=tmp_path/'return';make_return(folder,manifest,private)
    assert validation.validate_return(folder,manifest,private)['status']=='VALID'
    p=folder/'actual/all_percase.csv';p.write_text(p.read_text().replace('synthetic-0,','synthetic-99,'))
    receipt=executor.read(folder/'execution_receipt.json');receipt['actual_sha256']['all_percase.csv']=executor.digest(p.read_bytes());executor.atomic(folder/'execution_receipt.json',receipt)
    with pytest.raises(ValueError,match='CASE_MEMBERSHIP'):validation.validate_return(folder,manifest,private)
    receipt['source']='f'*40;executor.atomic(folder/'execution_receipt.json',receipt)
    with pytest.raises(ValueError,match='VERSION_BINDING'):validation.validate_return(folder,manifest,private)


@pytest.mark.parametrize("format_repair",[False,True])
def test_synthetic_full_driver_through_package_collection_interpretation_and_report(lane,monkeypatch,format_repair):
    from orchestrator import manual_runtime
    monkeypatch.setattr(manual_runtime,'settings',lambda:{'host_guard':{'receipt':str(lane/'missing-root-proof.json')}})
    d=driver.Driver(lane,runner=fake_author)
    # Seed the temporary fixture's known notebook and private metadata only.
    source=ROOT/'projects/isles24/manual/sprint10';target=d.root/'projects/isles24/manual/sprint10'
    # Completed real-lane outputs are not inputs to this synthetic fresh lane.
    shutil.copytree(source,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('acceptance-spec','acceptance'));private_copied_fixture(target)
    private=Path(d.config['private']);hashes=private_fixture(private)
    contract=executor.read(target/'DATA_CONTRACT.json');contract['split_manifest']['sha256']=hashes['split_manifest.csv'];contract['exclusions']['sha256']=hashes['excluded_cases.json'];executor.atomic(target/'DATA_CONTRACT.json',contract)
    pin_fixture_baseline(target,hashes)
    subprocess.run(['git','init','-q',str(d.root)],check=True)
    subprocess.run(['git','config','user.name','Synthetic test'],cwd=d.root,check=True);subprocess.run(['git','config','user.email','test@local.invalid'],cwd=d.root,check=True)
    # State/context lives under this fixture root, so ignore it for clean-source checks.
    (d.root/'.gitignore').write_text('lane/\nlane-scientific-workspaces/\nprivate/\n')
    subprocess.run(['git','add','.'],cwd=d.root,check=True);subprocess.run(['git','commit','-qm','Synthetic fixture'],cwd=d.root,check=True)
    d.config['notebook_code_sha256']=manual_package.code_sha(manual_package.notebook_bytes(d.root,d.config['run_id']));executor.atomic(lane/'lane.json',d.config)
    d.advance()
    def approve(work,*args):
        (work/'review.json').write_text(json.dumps({'verdict':'APPROVE','rationale':'Synthetic approval fixture only.'}));return {'family_effective':'claude','exit_class':'ok','synthetic':True}
    d.runner=approve;assert d.advance()['phase']=='COMMIT_SPEC'
    assert d.advance()['phase']=='EMIT_PACKAGE'
    assert d.advance()['phase']=='WAIT_OUTPUTS'
    assert d.advance()['phase']=='WAIT_OUTPUTS' and d.status()['calls_used']==2
    assert (lane/'package/RUN_INSTRUCTIONS.md').is_file()
    assert not (lane/'package/private-inputs').exists()
    assert not any(p.name in {'split_manifest.csv','excluded_cases.json'} for p in (lane/'package').rglob('*'))
    incoming=lane/'incoming';make_return(incoming,d.current()['manifest'],private)
    assert d.advance(incoming)['phase']=='result_interpretation_author'
    evidence={r['type']:r for r in d.current()['artifacts']}
    for kind,name in [('execution_receipt','execution-receipt.json'),('package_manifest','package-manifest.json')]:
        assert evidence[kind]['sha256']==executor.digest((d.context/'current'/name).read_bytes())
        assert kind in driver.manual_context.STAGE_ARTIFACT_TYPES['result_interpretation_author']
        assert kind in driver.manual_context.STAGE_ARTIFACT_TYPES['result_interpretation_review']
    def interpret(work,*args):
        summary='Known results match, not new efficacy.'
        if format_repair:summary+=' '+('Additional descriptive evidence '+('word '*90)+'ends. More details '+('word '*75)+'end.')
        (work/'interpretation.md').write_text('# Summary\n'+summary+'\n# Details\nSynthetic evidence.\n')
        (work/'investigator_next_decision.json').write_text(json.dumps({'status':'PROPOSAL_ONLY','proposed_action_type':'stop','action':'Stop here.','rationale':'Synthetic evidence is insufficient.','charter_basis':'','blocker_ids':[]}))
        return {'family_effective':'codex','exit_class':'ok','synthetic':True}
    d.runner=interpret;assert d.advance()['phase']=='result_interpretation_review'
    d.runner=approve;assert d.advance()['phase']=='UPDATE_STATE'
    assert d.advance()['phase']=='REPORT'
    assert d.advance()['phase']=='COMPLETE' and d.status()['calls_used']==4
    assert d.advance()['phase']=='COMPLETE' and d.status()['calls_used']==4
    assert 'Known-case Sprint10 reproduction' in (d.root/driver.PROFILE/'STATE.md').read_text()
    assert (lane/'REPORT.md').is_file()
    if format_repair:
        target=d.acceptance_path('acceptance')
        for name in ['interpretation-original-1.md','format-repair-1.json']:
            assert (target/name).is_file()
            committed=subprocess.check_output(['git','show','HEAD:'+str((target/name).relative_to(d.root))],cwd=d.root)
            assert committed==(target/name).read_bytes()


def test_invalid_review_cannot_become_approval_or_another_call(lane):
    d=driver.Driver(lane,runner=fake_author);d.advance()
    def contradict(work,*args):
        (work/'review.json').write_text(json.dumps({'verdict':'APPROVE','rationale':'BLOCKER[privacy/secret] Still unresolved.'}));return {'synthetic':True}
    d.runner=contradict
    assert 'VERDICT_CONFLICT' in d.advance()['reason']
    assert d.status()['phase']=='BLOCKED' and d.advance()['calls_used']==2



def test_initialization_requires_exact_approval_and_single_canonical_state(root,tmp_path,monkeypatch):
    target=root/'projects/isles24/manual/sprint10';shutil.copytree(ROOT/'projects/isles24/manual/sprint10',target,dirs_exist_ok=True);private_copied_fixture(target)
    fixtures=Path('tests/fixtures/context_budget/round2');shutil.copytree(ROOT/fixtures,root/fixtures)
    (root/'orchestrator').mkdir(exist_ok=True);shutil.copyfile(ROOT/'orchestrator/manual_validation.py',root/'orchestrator/manual_validation.py')
    auth=root/'docs/STEP_D_AUTHORIZATION.md';auth.write_text('Synthetic explicit eight-call authorization')
    (root/'scout.py').write_text('# Synthetic pinned transport fixture\n')
    private=tmp_path/'private';hashes=private_fixture(private)
    contract=executor.read(target/'DATA_CONTRACT.json');contract['split_manifest']['sha256']=hashes['split_manifest.csv'];contract['exclusions']['sha256']=hashes['excluded_cases.json'];executor.atomic(target/'DATA_CONTRACT.json',contract)
    pin_fixture_baseline(target,hashes)
    subprocess.run(['git','init','-q',str(root)],check=True)
    subprocess.run(['git','config','user.name','Fixture'],cwd=root,check=True);subprocess.run(['git','config','user.email','fixture@local.invalid'],cwd=root,check=True)
    (root/'.gitignore').write_text('lane*/\nprivate/\nreview.md\n')
    subprocess.run(['git','add','.'],cwd=root,check=True);subprocess.run(['git','commit','-qm','Synthetic source'],cwd=root,check=True)
    subprocess.run(['git','switch','-qc','astra/manual-synthetic'],cwd=root,check=True)
    pin=driver.git(root,'rev-parse','HEAD');review=tmp_path/'review.md'
    review.write_text('Candidate '+pin+'\n## Verdict: REQUEST_CHANGES\n')
    with pytest.raises(ValueError,match='EXACT_ENGINE_REVIEW'):driver.initialize(root,tmp_path/'lane-first',review)
    monkeypatch.setattr(driver.manual_stage,'preflight',lambda:{'synthetic':True})
    review.write_text('Synthetic reviewed candidate '+pin+'\n## Verdict: APPROVE\n')
    first=driver.initialize(root,tmp_path/'lane-first',review)
    assert first['calls_used']==0
    with pytest.raises(ValueError,match='EXISTING_CANONICAL'):driver.initialize(root,tmp_path/'lane-second',review)
    d=driver.Driver(tmp_path/'lane-first',runner=lambda *x:pytest.fail('no model'))
    assert d.status()['calls_used']==0
    assert all('P001' not in row['path'] and '-047' not in row['path'] for row in d.current()['artifacts'])
    assert d.config['notebook_code_sha256']==manual_package.code_sha(manual_package.notebook_bytes(root,first['run_id']))



def test_per_role_limit_stops_before_eight_total(tmp_path):
    store=executor.ManualExecutor(tmp_path/'jobs.sqlite');store.initialize_allowance(policy())
    for _ in range(2):
        ident,n,receipt=store.reserve_call('run','run_spec_author','a'*40,'astra/manual-test',policy(),{})
        store.finish_call(ident,receipt,'COMPLETE')
    with pytest.raises(ValueError,match='CALL_LIMIT'):store.reserve_call('run','run_spec_author','a'*40,'astra/manual-test',policy(),{})
    assert executor.Accounts(store).read()[1]['count']==2



def test_native_identity_and_usage_are_observed_not_invented():
    from orchestrator.manual_stage import native_metadata
    codex=native_metadata('prefix\n'+json.dumps({'type':'thread.started','thread_id':'synthetic-thread'})+'\n'+json.dumps({'type':'turn.completed','usage':{'input_tokens':12,'output_tokens':3}}))
    assert codex['native_session_ids']==['synthetic-thread'] and codex['observed_model_ids']==[]
    assert codex['native_usage_records'][0]['input_tokens']==12
    claude=native_metadata(json.dumps({'type':'system','session_id':'synthetic-session','model':'synthetic-model'}))
    assert claude['observed_model_ids']==['synthetic-model']
    with pytest.raises(ValueError,match='SESSION_EVIDENCE'):native_metadata('not a genuine JSON session stream')


def pin_fixture_baseline(target,hashes):
    folder=target/'synthetic-originals'
    manifest={'run_id':'synthetic','source':'a'*40,'spec_sha256':'b'*64,'notebook_code_sha256':'c'*64,'private_files':hashes}
    make_return(folder,manifest,None)
    executor.atomic(target/'REFERENCE_BINDINGS.json',{'status':'PINNED_ORIGINALS','baseline_path':validation.BASELINE_PATH,
        'sha256':manifest['baseline_sha256'],'json_keys':manifest['baseline_json_keys']})
    shutil.rmtree(folder)


def test_notebook_identity_tolerates_autosave_but_rejects_every_code_edit():
    raw=manual_package.notebook_bytes(ROOT,'synthetic-run')
    manifest={'notebook_code_cells':manual_package.code_cells(raw),'notebook_code_sha256':manual_package.code_sha(raw)}
    n=json.loads(raw);n['metadata']={'colab':{'autosave':'synthetic'}}
    for cell in n['cells']:
        cell['metadata']={'id':'autosaved'}
        if cell['cell_type']=='code':cell.update(execution_count=4,outputs=[{'output_type':'stream','name':'stdout','text':['synthetic output']}])
    manual_package.check_notebook(json.dumps(n,separators=(',',':')).encode(),manifest)
    for i,cell in enumerate(n['cells']):
        if cell['cell_type']!='code':continue
        changed=json.loads(json.dumps(n));changed['cells'][i]['source'].append('\n# any code edit\n')
        with pytest.raises(ValueError,match='CODE_CHANGED'):manual_package.check_notebook(json.dumps(changed).encode(),manifest)



def test_prepare_output_hash_is_reserved_and_runner_receives_same_text(lane,monkeypatch):
    original=driver.manual_context.prepare;captured={}
    def prepare(*a,**kw):
        body,m=original(*a,**kw);captured['body']=body;return body,m
    monkeypatch.setattr(driver.manual_context,'prepare',prepare)
    def run(work,stage,clients,expected):
        assert (work/'prompt.md').read_text()==captured['body']
        db=executor.ManualExecutor(lane/'jobs.sqlite')
        receipt=json.loads(db.db.execute('SELECT receipt FROM manual_calls').fetchone()[0]);db.db.close()
        assert receipt['input_sha256']==expected==executor.digest(captured['body'].encode())
        allowed={'prompt.md','input-measurement.json','evidence'}
        assert {p.name for p in work.iterdir()}<=allowed
        return fake_author(work,stage,clients,expected)
    assert driver.Driver(lane,runner=run).advance()['phase']=='run_spec_review'


def test_precomputation_refusal_reemits_without_reset_or_duplicate_dispatch(tmp_path):
    store=executor.ManualExecutor(tmp_path/'jobs.sqlite');prepared=tmp_path/'prepared';prepared.mkdir();(prepared/'notebook').write_text('reviewed')
    manifest={'run_id':'r','source':'a'*40};package=tmp_path/'package';store.submit('r',manifest,prepared,package)
    refusal={'schema':'manual-precomputation-refusal/v1','run_id':'r','manifest_sha256':executor.digest(json.dumps(manifest,sort_keys=True).encode()),'status':'IDENTITY_REFUSED_BEFORE_COMPUTATION','computation_started':False,'return_exists':False,'reason':'PACKAGE_IDENTITY_CHECK_FAILED'}
    f=tmp_path/'refusal.json';executor.atomic(f,refusal);destination=tmp_path/'re-emitted'
    before=store.get('r')
    assert store.reemit_identity_refusal('r',manifest,f,package,destination)['status']=='REEMITTED_BEFORE_COMPUTATION'
    assert store.reemit_identity_refusal('r',manifest,f,package,destination)['status']=='ALREADY_REEMITTED'
    assert store.get('r')==before and store.db.execute('SELECT count(*) FROM events').fetchone()[0]==3
    refusal['computation_started']=True;executor.atomic(f,refusal)
    with pytest.raises(ValueError,match='PRECOMPUTATION_REFUSAL'):store.reemit_identity_refusal('r',manifest,f,package,tmp_path/'unsafe')


@pytest.mark.parametrize('damage',['missing_key','wrong_type','bad_json','extra_file','missing_started'])
def test_malformed_return_is_preserved_and_blocks_driver(lane,damage):
    d=driver.Driver(lane);private=Path(d.config['private']);hashes=private_fixture(private)
    manifest={'run_id':d.config['run_id'],'source':'a'*40,'spec_sha256':'b'*64,'notebook_code_sha256':'c'*64,'private_files':hashes}
    incoming=lane/'bad-return';make_return(incoming,manifest,private)
    prepared=lane/'prepared';prepared.mkdir();(prepared/'n').write_text('synthetic')
    d.store.submit(d.config['run_id'],{},prepared,lane/'package')
    v=d.current();v.update(phase='WAIT_OUTPUTS',manifest=manifest);d.save(v)
    receipt=incoming/'execution_receipt.json'
    if damage=='missing_key':data=executor.read(receipt);del data['actual_sha256'];executor.atomic(receipt,data)
    elif damage=='wrong_type':executor.atomic(receipt,[])
    elif damage=='bad_json':receipt.write_text('{broken')
    elif damage=='extra_file':(incoming/'unbound.txt').write_text('synthetic')
    else:(incoming/'started.json').unlink()
    status=d.advance(incoming)
    assert status['phase']=='BLOCKED' and status['reason'] and Path(status['decision_request']).is_file()
    rejected=list(lane.glob('rejected-return-*'));assert any(p.is_dir() for p in rejected)
    assert d.store.get(d.config['run_id'])['status']=='BLOCKED'
    assert d.advance()['calls_used']==0


def test_changed_baseline_or_return_prefix_cannot_normalize_differences(tmp_path):
    private=tmp_path/'private';hashes=private_fixture(private)
    manifest={'run_id':'synthetic','source':'a'*40,'spec_sha256':'b'*64,'notebook_code_sha256':'c'*64,'private_files':hashes}
    folder=tmp_path/'return';make_return(folder,manifest,private)
    receipt=executor.read(folder/'execution_receipt.json');receipt['baseline_output_path']='';executor.atomic(folder/'execution_receipt.json',receipt)
    with pytest.raises(ValueError,match='PATH_BINDING'):validation.validate_return(folder,manifest)
    receipt['baseline_output_path']=validation.BASELINE_PATH
    p=folder/'baseline/summary_by_recipe.csv';p.write_text(p.read_text().replace('0.5','0.6'))
    receipt['baseline_sha256'][p.name]=executor.digest(p.read_bytes());executor.atomic(folder/'execution_receipt.json',receipt)
    with pytest.raises(ValueError,match='UNREVIEWED_BASELINE'):validation.validate_return(folder,manifest)



def test_isolation_refusal_happens_before_call_reservation(lane,monkeypatch):
    d=driver.Driver(lane)
    def refuse(*args):raise ValueError('ISOLATION_PROBE_FAILED_TEST')
    from contextlib import nullcontext
    monkeypatch.setattr(driver.manual_stage,'login_guard',lambda stage:nullcontext())
    monkeypatch.setattr(driver.manual_stage,'data_access_guard',refuse)
    result=d.advance();assert result['phase']=='BLOCKED' and 'ISOLATION_PROBE_FAILED_TEST' in result['reason']
    assert result['calls_used']==0 and executor.Accounts(d.store).read()[1]['count']==0


def test_emitted_identity_guard_writes_refusal_before_any_capture(tmp_path):
    pkg=tmp_path/'package';pkg.mkdir()
    manifest={'run_id':'synthetic','notebook_code_cells':['reviewed code']}
    executor.atomic(pkg/'manifest.json',manifest)
    executor.atomic(pkg/'Sprint10.ipynb',{'cells':[{'cell_type':'code','source':['changed code']}]})
    start=manual_package.START.replace('Path("/content/drive/MyDrive/isles-pilot/manual-step-d/RUN_ID")','Path('+repr(str(pkg))+')')
    with pytest.raises(RuntimeError,match='Identity refused before computation'):exec(compile(start,'emitted-preflight','exec'),{})
    refusal=executor.read(next(pkg.glob('identity-refusal-*.json')))
    assert refusal['computation_started'] is False and refusal['return_exists'] is False
    assert not (pkg/'return').exists()
    assert refusal['manifest_sha256']==executor.digest(json.dumps(manifest,sort_keys=True).encode())


def test_reviewed_baseline_json_keys_match_actual_notebook_writers():
    nb=json.loads(manual_package.notebook_bytes(ROOT,'synthetic'))
    found={}
    for c in nb['cells']:
        if c['cell_type']!='code':continue
        for call in ast.walk(ast.parse(''.join(c['source']))):
            if not (isinstance(call,ast.Call) and isinstance(call.func,ast.Attribute) and call.func.attr=='dump' and call.args and isinstance(call.args[0],ast.Dict)):continue
            code=ast.unparse(call)
            for name in validation.BASELINE_JSON_KEYS:
                if name in code:found[name]={k.value for k in call.args[0].keys}
    assert found=={name:set(keys)|{'fingerprint','run_identity'} for name,keys in validation.BASELINE_JSON_KEYS.items()}
    binding=validation.baseline_contract(ROOT)
    assert set(binding['sha256'])==set(validation.RETURN_FILES)


def test_limit_refusal_saves_reason_and_decision_request(lane):
    d=driver.Driver(lane,runner=lambda *a:pytest.fail('over-budget model call'))
    v=d.current();v['rounds']['run_spec_author']=2;d.save(v)
    status=d.advance()
    assert status['phase']=='BLOCKED' and 'REVIEW_ROUND_LIMIT' in status['reason']
    text=Path(status['decision_request']).read_text()
    assert 'stage run_spec_author, round 2' in text and 'execution authority/provenance' in text
    assert status['calls_used']==0
