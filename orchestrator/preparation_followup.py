"""Select exactly the two independently reviewed preparation scopes."""
from orchestrator import item6_idea2_followup as item6, colab_simple_full as colab, colab_arm_question as arm
STAGES=item6.STAGES
require=item6.require
sha=item6.sha
def module(run):
    from orchestrator import meeting_preparation as meeting
    return meeting if run==meeting.RUN else arm if run==arm.RUN else colab if run==colab.RUN else item6
def validate(store,run): return module(run).validate(store,run)
def offset(store,run,stage): return module(run).offset(store,run,stage)
def guard_admission(accounts,run,stage,source,receipt):
    return module(run).guard_admission(accounts,run,stage,source,receipt)
def terminal_ids(accounts,scope): return module(scope['run_id']).terminal_ids(accounts,scope)
def batch_allowance(accounts,scope): return module(scope['run_id']).batch_allowance(accounts,scope)
def refuse_legacy_completion(accounts,run): return module(run).refuse_legacy_completion(accounts,run)
def preparation_hold(driver,value,collect_folder,identity_refusal):
    return module(driver.config['run_id']).preparation_hold(driver,value,collect_folder,identity_refusal)
