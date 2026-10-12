"""One accepted-question follow-up; preserve the canonical owner and all usage.

This preparation grant permits scientific specification author/review only.
It provides no data executor, provider client, new allowance or completion path.
"""
from pathlib import Path
import hashlib
import json
import sqlite3

RUN = "diagnostics-b203ee1ce27e909d9d78d44a"
DOCUMENT = "docs/ITEM6_SMOOTHING_FOLLOWUP_PRIVATE.json"
DOCUMENT_SHA = "9547a419f92e11790f78fded950b96b2c8c4ab32993373d606158f618770ece1"
FIELD = "item6_idea2_followup"
EVENT = RUN + ":smoothing-specification-followup"
STAGES = frozenset(("run_spec_author", "run_spec_review"))
_TERMINAL_QUALIFIER = None  # Set only by the reviewed installed native entry point.


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def require(ok, why):
    if not ok:
        raise ValueError("IDEA2_FOLLOWUP_" + why)


def document():
    p = Path(__file__).resolve().parents[1] / DOCUMENT
    raw = p.read_bytes()
    require(not p.is_symlink() and sha(raw) == DOCUMENT_SHA, "SCOPE_CHANGED")
    scope = json.loads(raw)
    require(scope["run_id"] == RUN and scope["call_limit"] == 30 and
            scope["item_cap_micro_usd"] == 100_000_000 and scope["batch_limit"] == 128 and scope["allocation_limit"] == 4 and scope["prior_call_count"] == 13 and
            scope["admitted_stages"] == sorted(STAGES) and
            scope["execution_authorized"] is False, "SCOPE_LIMITS")
    for name,key in [('SCIENTIFIC_BATCH128_OPERATOR_APPROVAL.txt','batch_answer_sha256'),
                     ('SCIENTIFIC_BATCH128_OPERATOR_QUESTION.txt','batch_question_sha256')]:
        require(sha((p.parent/name).read_bytes()) == scope[key], 'OPERATOR_AUTHORITY_CHANGED')
    return scope


def _path(root, absolute):
    p = Path(absolute)
    require(p.is_absolute() and ".." not in p.parts, "ABSOLUTE_PATH")
    q = Path(root) / p.relative_to("/")
    require(not any(x.is_symlink() for x in (q, *q.parents)), "PATH_ALIAS")
    return q


def _approval(config, scope, root):
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_host_guard import trusted
    folder = _path(root, scope["review_directory"])
    if Path(root) == Path("/"):
        trusted(folder)
    result = verify_result(folder)
    manifest = json.loads((folder / "packet-manifest.json").read_bytes())
    require(result["verdict"] == "APPROVE" and result["source_sha"] == config["source"]
            and manifest["source_sha"] == config["source"]
            and result.get("change_id")=="item6-smoothing-terminal-route-20261012", "INDEPENDENT_APPROVAL_REQUIRED")
    report = json.loads((folder / "report.md").read_bytes())
    require(report.get("findings") == [], "UNRESOLVED_IMPLEMENTATION_FINDINGS")
    require({DOCUMENT,'orchestrator/item6_idea2_followup.py','tools/item6_idea2_runtime.py'}
            <= set(manifest['source_files']), 'WHOLE_COMPONENT_REQUIRED')
    for name in manifest["source_files"]:
        require(manifest["source_files"][name] == sha((Path(__file__).resolve().parents[1] / name).read_bytes()),
                "REVIEWED_SOURCE_CHANGED")
    return result["report_sha256"]


def _originals(db, scope, root):
    old = scope["prior"]
    owner = db.execute("SELECT * FROM autonomy_runs WHERE id=?", (RUN,)).fetchone()
    require(owner is not None and owner["binding"] == old["owner"]["binding"], "ORIGINAL_OWNER_CHANGED")
    event = db.execute("SELECT * FROM events WHERE id=?", (old["acceptance"]["id"],)).fetchone()
    require(event is not None and dict(event) == old["acceptance"], "ORIGINAL_ACCEPTANCE_CHANGED")
    first = scope["original_acceptance"]
    event = db.execute("SELECT * FROM events WHERE id=?", (first["id"],)).fetchone()
    require(event is not None and dict(event) == first, "ORIGINAL_DIAGNOSTICS_ACCEPTANCE_CHANGED")
    for row in old["global_calls"]:
        actual = db.execute("SELECT * FROM autonomy_calls WHERE id=?", (row["id"],)).fetchone()
        require(actual is not None and dict(actual) == row, "ORIGINAL_GLOBAL_CALL_CHANGED")
    parent = _path(root, old["parent_lane"])
    for name, pin in (("lane.json", old["config_sha256"]),
                      ("REPORT.md", old["report_sha256"]),
                      ("preparation-plan.json", old["plan_sha256"])):
        require(sha(_path(root, str(Path(old["parent_lane"]) / name)).read_bytes()) == pin,
                "ACCEPTED_PARENT_FILE_CHANGED")
    with sqlite3.connect((parent / "jobs.sqlite").as_uri() + "?mode=ro", uri=True) as previous:
        previous.row_factory = sqlite3.Row
        require([dict(r) for r in previous.execute("SELECT * FROM manual_calls ORDER BY id")] == old["local_calls"],
                "ACCEPTED_PARENT_CALLS_CHANGED")
        row = previous.execute("SELECT * FROM manual_state WHERE id=1").fetchone()
        require(row is not None and dict(row) == old["parent_state_row"], "ACCEPTED_PARENT_STATE_CHANGED")
    return dict(owner)


def _configuration(store, run):
    from orchestrator import idea2_interpretation as interpretation
    if interpretation.selected(store):return interpretation._configuration(store,run)
    path = Path(store.path).parent / "lane.json"
    if not path.exists():
        return None
    config = json.loads(path.read_bytes())
    if FIELD not in config:
        return None
    scope = document()
    root = Path(store.batch.filesystem_root)
    require(run == RUN == config["run_id"] and config["item_number"] == 6 and
            config["backend"] == "cpu" and config[FIELD] == {
                "schema": "item6-idea2-followup/v1", "scope_sha256": DOCUMENT_SHA}, "CONFIG_SCOPE")
    require(Path(store.path).parent == _path(root, scope["new_lane"]), "EXACT_NEW_LANE")
    require(config["owner_binding"] == json.loads(scope["prior"]["owner"]["binding"]), "OWNER_BINDING_CHANGED")
    require(config["author_timeout_seconds"] == 1800, "AUTHOR_TIMEOUT_BINDING")
    before = scope['prior']['config']
    mutable = {'root','source','branch','context','workspace_root','engine_files','engine_review'}
    require(set(config) == set(before) | {FIELD,'author_timeout_seconds'} and
            all(config[k] == v for k,v in before.items() if k not in mutable),
            'ORIGINAL_CONFIG_SCOPE_CHANGED')
    expected_work = str(Path(scope["new_lane"]).with_name("lane-scientific-workspaces"))
    require(config["workspace_root"] == expected_work, "EXACT_WORKSPACE_ROOT")
    _path(root, expected_work)
    require(config.get('context') == str(_path(root,scope['new_lane'])/'context'), 'EXACT_CONTEXT_ROOT')
    if root == Path('/'):
        require(Path(config['root']) == Path(__file__).resolve().parents[1], 'EXACT_SOURCE_ROOT')
    approval = _approval(config, scope, root)
    for old in scope["prior"]["local_calls"]:
        actual = store.db.execute("SELECT * FROM manual_calls WHERE id=?", (old["id"],)).fetchone()
        require(actual is not None and dict(actual) == old, "PRESERVED_LOCAL_CALL_CHANGED")
    return config, scope, root, approval


def _grant(config, scope, approval):
    return {"schema": "item6-idea2-specification-grant/v1", "run_id": RUN,
            "source": config["source"], "new_lane": scope["new_lane"],
            "configuration_sha256":sha(encoded(config)),
            "scope_sha256": DOCUMENT_SHA, "implementation_review_sha256": approval,
            "prior_acceptance_sha256": sha(encoded(scope["prior"]["acceptance"])),
            "prior_calls": 13, "shared_call_limit": 30, "analysis_allocation_limit": 4, "item_cap_micro_usd": 100_000_000,
            "batch_limit": 128,
            "stages": sorted(STAGES), "execution_authorized": False}


def activate(store, run):
    """One transaction changes status only; original acceptance/rows stay intact."""
    selected = _configuration(store, run)
    require(selected is not None, "PREPARED_LANE_REQUIRED")
    config, scope, root, approval = selected
    db = store.batch.db
    db.execute("BEGIN IMMEDIATE")
    try:
        owner = _originals(db, scope, root)
        require(owner == scope["prior"]["owner"] and owner["status"] == "COMPLETE", "CANONICAL_OWNER_NOT_COMPLETE")
        require(not db.execute("SELECT 1 FROM events WHERE id=?", (EVENT,)).fetchone(), "ALREADY_ACTIVATED")
        calls = [dict(r) for r in db.execute("SELECT * FROM autonomy_calls WHERE change_id=? ORDER BY id", (RUN,))]
        require(calls == scope["prior"]["global_calls"] and len(calls) == 13, "PRIOR_CALL_SET_CHANGED")
        require(not db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(), "LIVE_MODEL_CALL")
        require([dict(r) for r in store.db.execute("SELECT * FROM manual_calls ORDER BY id")] == scope["prior"]["local_calls"],
                "NEW_LANE_ALREADY_USED")
        state = json.loads(store.db.execute("SELECT payload FROM manual_state WHERE id=1").fetchone()[0])
        require(state["phase"] == "run_spec_author" and state["rounds"] == scope["offsets"] and
                "reviewed_execution" not in state and "reviewed_results" not in state, "FRESH_PREPARATION_STATE")
        db.execute("INSERT INTO events VALUES(?,?,?)", (EVENT, RUN, encoded(_grant(config, scope, approval)).decode()))
        changed = db.execute("UPDATE autonomy_runs SET status='ACTIVE' WHERE id=? AND status='COMPLETE' AND binding=?",
                             (RUN, owner["binding"]))
        require(changed.rowcount == 1, "OWNER_RACE")
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise
    return {"status": "IDEA2_AUTHOR_READY", "calls_already_counted": 13,
            "shared_call_limit": 30, "execution_authorized": False}


def validate(store, run):
    from orchestrator import idea2_interpretation as interpretation
    if interpretation.selected(store):return interpretation.validate(store,run)
    selected = _configuration(store, run)
    if selected is None:
        return None
    config, scope, root, approval = selected
    owner = _originals(store.batch.db, scope, root)
    require(owner["status"] == "ACTIVE", "CANONICAL_OWNER_NOT_ACTIVE")
    row = store.batch.db.execute("SELECT job,payload FROM events WHERE id=?", (EVENT,)).fetchone()
    require(row is not None and row["job"] == RUN and json.loads(row["payload"]) == _grant(config, scope, approval),
            "QUALIFIED_ACTIVATION_REQUIRED")
    require(store.batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific' AND change_id=?",
                                   (RUN,)).fetchone()[0] <= 30, "SHARED_CALL_LIMIT")
    return scope


def offset(store, run, stage):
    scope = validate(store, run)
    return 0 if scope is None else scope["offsets"].get(stage, 0)


def guard_admission(accounts, run, stage, source, receipt):
    """Called inside normal global admission; all normal caps still run afterward."""
    if run != RUN:
        return
    from orchestrator import idea2_interpretation as interpretation
    if accounts.db.execute("SELECT 1 FROM events WHERE id=?",(interpretation.EVENT,)).fetchone():
        return interpretation.guard_admission(accounts,run,stage,source,receipt)
    row = accounts.db.execute("SELECT payload FROM events WHERE id=?", (EVENT,)).fetchone()
    if row is None:
        return
    grant = json.loads(row[0]);scope = document();root = Path(accounts.filesystem_root)
    require(grant["source"] == source and grant["scope_sha256"] == DOCUMENT_SHA and stage in STAGES,
            "ADMISSION_SCOPE")
    _originals(accounts.db, scope, root)
    require(grant["new_lane"] == scope["new_lane"] and grant["execution_authorized"] is False, "GRANT_SCOPE")
    config = json.loads((_path(root, scope["new_lane"]) / "lane.json").read_bytes())
    require(config.get(FIELD)=={'schema':'item6-idea2-followup/v1','scope_sha256':DOCUMENT_SHA},'ADMISSION_CONFIG_SCOPE')
    require(grant == _grant(config, scope, _approval(config, scope, root)), "ADMISSION_APPROVAL_CHANGED")
    work = Path(receipt["workspace"])
    workspace_root = Path(scope["new_lane"]).with_name("lane-scientific-workspaces")
    require(config["workspace_root"] == str(workspace_root), "EXACT_WORKSPACE_ROOT")
    _path(root, str(work))
    require(work.parent == workspace_root and work.name.startswith(stage + "-"), "ADMISSION_WORKSPACE")
    number = work.name.removeprefix(stage + "-")
    require(number.isdecimal() and int(number) > scope["offsets"][stage], "ADMISSION_PRIOR_STAGE_REPLAY")
    require(accounts.db.execute("SELECT status FROM autonomy_runs WHERE id=?",(RUN,)).fetchone()[0]=='ACTIVE',
            'CANONICAL_OWNER_NOT_ACTIVE')
    count = accounts.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific' AND change_id=?", (RUN,)).fetchone()[0]
    require(count < scope['prior_call_count'] + scope['allocation_limit'], 'ANALYSIS_ALLOCATION_EXHAUSTED')
    return scope


def refuse_legacy_completion(accounts, run):
    if run == RUN and accounts.db.execute("SELECT 1 FROM events WHERE id=?", (EVENT,)).fetchone():
        raise ValueError("IDEA2_FOLLOWUP_DISTINCT_ACCEPTANCE_REQUIRED")


def preparation_hold(driver, value, collect_folder, identity_refusal):
    from orchestrator import idea2_interpretation as interpretation
    if interpretation.FIELD in driver.config:
        return interpretation.preparation_hold(driver,value,collect_folder,identity_refusal)
    if not hasattr(driver, "store"):
        require(FIELD not in driver.config, "PREPARATION_STORE_REQUIRED")
        return None  # Pure legacy context fixtures do not select a follow-up.
    scope = validate(driver.store, driver.config["run_id"])
    if scope is None:
        return None
    require(collect_folder is None and identity_refusal is None, "NO_EXECUTION_OR_COLLECTION")
    phase = value["phase"]
    require(phase in STAGES | {"MODEL_RUNNING", "BLOCKED", "COMMIT_SPEC"}, "PREPARATION_ONLY")
    if phase == "COMMIT_SPEC":
        return {**driver.status(), "next_action": "Smoothing specification reviewed; execution remains held",
                "execution_authorized": False}
    return None


def terminal_ids(accounts, scope):
    """Qualify terminality only; this release's grant supplies new-question authority.

    No historical call becomes accepted, refunded, restarted or completed here.
    Every pending row must be one of the exact frozen rows and pass its original
    native terminal verifier. A missing qualifier or any live/new row refuses.
    """
    if scope.get('schema')=='idea2-interpretation-scope/v1':
        from orchestrator.idea2_interpretation import terminal_ids as interpret_terminals
        return interpret_terminals(accounts,scope)
    require(callable(_TERMINAL_QUALIFIER), 'INSTALLED_TERMINAL_QUALIFIER_REQUIRED')
    rows = [dict(r) for r in accounts.db.execute(
        "SELECT * FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN') ORDER BY id")]
    require(rows == scope['uncertain_rows'] and all(r['status']=='UNCERTAIN' for r in rows),
            'UNCLASSIFIED_OR_RUNNING_CALL')
    result=[]
    for row in rows:
        proof=_TERMINAL_QUALIFIER(accounts,row)
        require(isinstance(proof,dict) and proof.get('id')==row['id'] and
                isinstance(proof.get('proof_sha256'),str) and len(proof['proof_sha256'])==64,
                'AUTHENTIC_TERMINAL_PROOF_REQUIRED')
        result.append(row['id'])
    return result


def batch_allowance(accounts, scope):
    """Only the four analysis slots; no Colab or meeting allocation is borrowed."""
    if scope.get('schema')=='idea2-interpretation-scope/v1':
        from orchestrator.idea2_interpretation import batch_allowance as interpretation_batch
        return interpretation_batch(accounts,scope)
    require(scope['batch_limit']==128 and scope['allocation_limit']==4, 'BATCH_CEILING_CHANGED')
    # The complete pre-grant history is frozen, including all 104 original calls
    # and five Colab calls. No prior row is deleted, relabelled or refunded.
    frozen=scope['allocation_initial_calls']
    require(len(frozen)==109 and len({row['id'] for row in frozen})==109, 'INITIAL_CALL_SET')
    for row in frozen:
        actual=accounts.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(row['id'],)).fetchone()
        require(actual is not None and sha(encoded(dict(actual)))==row['sha256'], 'ALLOCATION_HISTORY_CHANGED')
    old_ids={row['id'] for row in scope['prior']['global_calls']}
    rows=accounts.db.execute("SELECT id FROM autonomy_calls WHERE kind='scientific' AND change_id=?",(RUN,)).fetchall()
    used=sum(row['id'] not in old_ids for row in rows)
    require(used < 4, 'ANALYSIS_ALLOCATION_EXHAUSTED')
    grant=json.loads(accounts.db.execute('SELECT payload FROM events WHERE id=?',(EVENT,)).fetchone()[0])
    require(grant['batch_limit']==128 and grant['scope_sha256']==DOCUMENT_SHA,'BATCH_GRANT')
    return {'limit':128,'scoped_run_id':RUN,'scope_sha256':DOCUMENT_SHA,
            'review_sha256':grant['implementation_review_sha256'],
            'operator_answer_sha256':scope['batch_answer_sha256'],
            'operator_question_sha256':scope['batch_question_sha256'],
            'analysis_allocation_used':used,'analysis_allocation_limit':4}


def prepare(root, *, filesystem_root=Path('/')):
    """Copy the accepted lane once without altering its owner or admitting a call.

    Partial copies remain for reconciliation. This never initializes an allowance,
    creates a new owner, deletes a destination, or invokes a model/provider.
    """
    import os
    from orchestrator import private_records as pr
    from orchestrator.manual_driver import git
    from orchestrator.analysis_driver import release_identities
    from orchestrator.manual_executor import ManualExecutor, atomic, lock
    from orchestrator.autonomy_accounting import BatchAccounts
    scope=document();host=Path(filesystem_root);root=Path(root)
    require(host!=Path('/') or os.getuid()==os.getgid()==1003,'SERVICE_OWNER_REQUIRED')
    require(root.is_absolute() and not root.is_symlink(),'REPOSITORY_PATH')
    if host==Path('/'):
        from orchestrator.manual_host_guard import trusted
        trusted(root)
    require(not git(root,'status','--porcelain'),'CLEAN_REVIEWED_SOURCE')
    source=git(root,'rev-parse','HEAD');branch=git(root,'branch','--show-current')
    require(branch=='astra/manual-item6-smoothing-terminal-20261012','EXACT_BRANCH')
    parent=_path(host,scope['prior']['parent_lane']);state=_path(host,scope['new_lane'])
    require(not state.exists() and not state.is_symlink(),'EXISTING_LANE_RECONCILE')
    old=scope['prior']['config'];batch=BatchAccounts(_path(host,old['batch_ledger']),filesystem_root=host)
    try:
        with lock(parent/'driver.lock'):
            require(not(parent/'HALT').exists() and not(batch.folder/'HALT').exists(),'HALT')
            require(_originals(batch.db,scope,host)==scope['prior']['owner'],'ORIGINAL_OWNER_CHANGED')
            require(not batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'LIVE_MODEL_CALL')
            profile,engine=release_identities(root)
            require(profile==old['profile_files'],'PROFILE_CHANGED')
            for name,pin in old['engine_files'].items():
                if name not in engine:
                    require(sha((root/name).read_bytes())==pin,'RETAINED_AUTHORITY_CHANGED');engine[name]=pin
            config={**old,'root':str(root),'source':source,'branch':branch,
                'context':str(state/'context'),'workspace_root':str(Path(scope['new_lane']).with_name('lane-scientific-workspaces')),
                'engine_files':engine,'author_timeout_seconds':1800,
                FIELD:{'schema':'item6-idea2-followup/v1','scope_sha256':DOCUMENT_SHA}}
            # Qualify before creating any lane state or copying the database.
            approved=_approval(config,scope,host)
            config['engine_review']={'path':str(_path(host,scope['review_directory'])/'report.md'),'sha256':approved}
            pr.mkdir(state)
            pr.write_bytes(state/'PREPARE_INTENT.json',encoded({'source':source,'scope_sha256':DOCUMENT_SHA,
                'prior_acceptance_sha256':sha(encoded(scope['prior']['acceptance'])),'model_calls':0,'new_allowance':0}))
            pr.copytree(parent/'context',state/'context')
            pr.copyfile(parent/'preparation-plan.json',state/'preparation-plan.json')
            with sqlite3.connect((parent/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as original:
                with pr.Connection(state/'jobs.sqlite') as target:original.backup(target)
            atomic(state/'lane.json',config)
            store=ManualExecutor(state/'jobs.sqlite',batch=batch)
            try:
                value=json.loads(scope['prior']['parent_state_row']['payload'])
                fresh={'phase':'run_spec_author','rounds':scope['offsets'],
                    'artifacts':value['artifacts'],'interventions':[*value['interventions'],
                        {'kind':'NEW_ACCEPTED_QUESTION','scope_sha256':DOCUMENT_SHA,'original_acceptance_preserved':True}]}
                store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(encoded(fresh).decode(),))
                _configuration(store,RUN)
                require(_originals(batch.db,scope,host)==scope['prior']['owner'],'ORIGINAL_OWNER_CHANGED_AFTER_COPY')
                for table,key in [('manual_account','manual_account'),('manual_recoveries','manual_recoveries')]:
                    actual=[dict(r) for r in store.db.execute('SELECT * FROM '+table)]
                    require(actual==scope['prior'][key],'ORIGINAL_ACCOUNTING_COPY_CHANGED')
                require(not batch.db.execute('SELECT 1 FROM events WHERE id=?',(EVENT,)).fetchone(),'PREPARATION_MUST_NOT_ACTIVATE')
            finally:store.db.close()
            pr.write_bytes(state/'PREPARED.json',encoded({'status':'PREPARED_NOT_ACTIVATED','source':source,
                'scope_sha256':DOCUMENT_SHA,'calls_preserved':13,'model_calls':0,'new_allowance':0}))
            return {'status':'PREPARED_NOT_ACTIVATED','calls_preserved':13,'model_calls':0,'new_allowance':0}
    finally:batch.db.close()
