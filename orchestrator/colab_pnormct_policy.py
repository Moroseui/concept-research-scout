"""Scoped interface repair for the already admitted pnormct question."""
from pathlib import Path
import json
from orchestrator import colab_arm_question as question
EVENT='pnormct-policy-premodel-recovery'
DOCUMENT='docs/COLAB_PNORMCT_POLICY_FAILURE_PRIVATE.json'
DOCUMENT_SHA='904453069c1695650a854a1386e58764a055bc21aafb548da40e00c24d2d2439'

def document(root):
    from orchestrator import private_records as pr
    raw=pr.check(Path(root)/DOCUMENT).read_bytes()
    question.require(question.sha(raw)==DOCUMENT_SHA,'POLICY_CHECKPOINT_CHANGED')
    f=json.loads(raw)
    question.require(f['run_id']==question.RUN and f['calls']==[] and
        f['source']=='45c6b7deea7768df99b4c754d960444afc117cb5','POLICY_CHECKPOINT_SCOPE')
    return f

def check(driver,f,initial=False):
    question.require(driver.config['run_id']==question.RUN and str(driver.state)==f['lane']
        and question.sha((driver.state/'lane.json').read_bytes())==f['config_sha256'],
        'POLICY_EXACT_LANE')
    question.validate(driver.store,question.RUN)
    if initial:
        question.require(dict(driver.store.db.execute('SELECT * FROM manual_state WHERE id=1').fetchone())==f['state_row']
            and not driver.store.db.execute('SELECT 1 FROM manual_calls').fetchone()
            and not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),
            'POLICY_PREMODEL_STATE_CHANGED')
    return True

def restored(value,f):
    question.require(value==json.loads(f['state_row']['payload']) and value['phase']=='BLOCKED'
        and value['reason']=='ValueError: ANALYSIS_REVISION_POLICY_SCOPE'
        and not value.get('pending') and value['rounds']=={},'POLICY_PREMODEL_FAILURE_ONLY')
    return {**value,'phase':'run_spec_author','reason':None}

def connect():
    """Retain generic refusals; validate exact normal question before adaptation."""
    from orchestrator import analysis_revisions as revisions
    original_enabled=revisions.enabled
    original_instructions=revisions.instructions
    original_validate=question.validate
    def validate(store,run):
        scope=original_validate(store,run)
        if scope is None:return None
        # The legacy caller expects explicit initial offsets. No history reset:
        # this distinct question was admitted with zero initial calls.
        return {**scope,'offsets':{stage:0 for stage in question.STAGES}}
    def enabled(store,run):
        if run!=question.RUN:return original_enabled(store,run)
        config=json.loads((Path(store.path).parent/'lane.json').read_bytes())
        question.require(config.get('revision_policy')==revisions.POLICY and
            config.get('run_id')==run and config.get('review_contract')=='bound-review/v1'
            and config.get('backend')=='analysis' and config.get('item_number')==4,
            'POLICY_CONFIGURATION')
        question.require(validate(store,run) is not None,'POLICY_BOUND_QUESTION_REQUIRED')
        authority=Path(config['root'])/revisions.DOCUMENT
        question.require(not authority.is_symlink() and
            question.sha(authority.read_bytes())==revisions.AUTHORITY,'POLICY_AUTHORITY')
        revisions.correction_authority()
        return True
    def instructions(store,run,*,notebook_revision=False):
        if run!=question.RUN:
            return original_instructions(store,run,notebook_revision=notebook_revision)
        enabled(store,run)
        return ("This is the independently admitted A1_L notebook question for item4. "
            "Approved UTC-day policy, run20, scientific batch128, shared additional Colab allocation16 from baseline104; "
            "all original calls count. At most three genuine REVISE response cycles per stage. "
            "Four failed/unsubmitted/format-rejected author attempts remain the failed-attempt guard. "
            "Genuine REVISE goes to the scientific author in every finding category; only independent "
            "APPROVE closes findings. REJECT or unresolved after three revisions stops. "
            "No data execution, patient access, credential change or new spending is granted. "
            "Real trainer construction/iteration and scientific acceptance are required before delivery. ")
    question.validate=validate
    revisions.enabled=enabled
    revisions.instructions=instructions

def recover(driver,f,approval):
    from orchestrator import private_records as pr
    check(driver,f,initial=True)
    question.require(not (driver.state/'HALT').exists() and not (driver.store.batch.folder/'HALT').exists(),'POLICY_HALT')
    before=driver.current();after=restored(before,f)
    dest=driver.state/EVENT
    question.require(not dest.exists() and not dest.is_symlink(),'POLICY_ALREADY_ATTEMPTED')
    grant={'kind':EVENT,'review_sha256':approval,'checkpoint_sha256':DOCUMENT_SHA,
           'model_calls':0,'new_allowance':0,'preserved_calls':0}
    pr.mkdir(dest);pr.write_bytes(dest/'original-state.json',f['state_row']['payload'].encode())
    pr.write_bytes(dest/'intent.json',question.encoded(grant))
    after['interventions']=[*after['interventions'],grant]
    db=driver.store.db;db.execute('BEGIN IMMEDIATE')
    try:
        check(driver,f,initial=True)
        db.execute('INSERT INTO events VALUES(?,?,?)',(EVENT,question.RUN,question.encoded(grant).decode()))
        db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(after,sort_keys=True),))
        db.execute('COMMIT')
    except BaseException:db.execute('ROLLBACK');raise
    pr.write_bytes(dest/'COMPLETE.json',question.encoded(grant))
    return {'status':'RESTORED_AUTHOR1_NO_CALL','model_calls':0,'new_allowance':0}
