"""Use the existing image lifecycle with the installed SDK's deny-all syntax."""
from pathlib import Path
import json
import os
import sys

CHANGE='item4-image-runtime-20261008'
REVIEW_CHANGE='item4-image-terminal-compute-20261008'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
BASE=Path('/opt/research-system/manual-sprint10/research-manual-sprint10-spending-a51ac44279e4')
BASE_RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/spending-continuation-scope-20261007')
CONFIG=Path('/etc/research-system-manual-sprint10/environment-inventory/a51ac44279e47a0df52dc2cfa012ecfa12defee5/image/config.json')
FILES=('orchestrator/modal_environment_budget.py','tools/item4_image_runtime.py','tools/install_item4_image_runtime.py','tools/environment_inventory_service.py',
       'docs/ITEM4_PINNED_IMAGE_SELECTION_20261008.json','docs/OVERNIGHT_AUTONOMY_OPERATOR_DECISION_20261008.txt')
AUTHORITY='a7fbba4b5c49426c099f1eb8d91e45489b454fc51a527f5df1566a60c1cabcb1'


def require(ok,why):
    if not ok:raise ValueError(why)


def sandbox_arguments(kwargs):
    """Only drop mutually exclusive empty filters from an exact deny-all probe."""
    expected={'app','name','image','gpu','cpu','memory','timeout','block_network','outbound_cidr_allowlist',
              'outbound_domain_allowlist','inbound_cidr_allowlist','include_oidc_identity_token','secrets','env',
              'encrypted_ports','h2_ports','unencrypted_ports','volumes','client'}
    require(set(kwargs)==expected,'IMAGE_SDK_ARGUMENT_SET')
    require(kwargs['block_network'] is True and kwargs['include_oidc_identity_token'] is False
        and kwargs['gpu'] is None and kwargs['cpu']==(1,1) and kwargs['memory']==(4096,4096)
        and type(kwargs['timeout']) is int and kwargs['timeout']==300,'IMAGE_SDK_PROBE_SCOPE')
    for key in ('outbound_cidr_allowlist','outbound_domain_allowlist','inbound_cidr_allowlist','secrets',
                'encrypted_ports','h2_ports','unencrypted_ports'):
        require(type(kwargs[key]) is list and not kwargs[key],'IMAGE_SDK_DENY_ALL_REQUIRED')
    require(kwargs['env']=={} and kwargs['volumes']=={},'IMAGE_SDK_NO_MOUNTS_OR_ENV')
    return {k:v for k,v in kwargs.items() if k not in
            {'outbound_cidr_allowlist','outbound_domain_allowlist','inbound_cidr_allowlist'}}


class SandboxView:
    def __init__(self,original):self.original=original
    def __getattr__(self,name):return getattr(self.original,name)
    def create(self,*args,**kwargs):return self.original.create(*args,**sandbox_arguments(kwargs))


class ModalView:
    def __init__(self,original):
        self.original=original
        self.Sandbox=SandboxView(original.Sandbox)
    def __getattr__(self,name):return getattr(self.original,name)


def verify():
    from orchestrator.manual_host_guard import trusted
    from orchestrator.manual_executor import digest
    from orchestrator.autonomy_review import verify_result
    from tools.manual_promotion import manifest_check
    record=json.loads(trusted(RECORD/'installed.json').read_bytes())
    approved=verify_result(trusted(RECORD/'review'))
    require(approved['verdict']=='APPROVE' and approved['change_id']==REVIEW_CHANGE
        and approved['source_sha']==record['source'] and approved['report_sha256']==record['review_sha256'],
        'IMAGE_RUNTIME_GENUINE_APPROVAL')
    manifest=json.loads(trusted(RECORD/'review/packet-manifest.json').read_bytes())
    require(manifest['source_sha']==record['source'],'IMAGE_RUNTIME_REVIEW_SOURCE')
    for name in FILES:
        require(digest(trusted(ROOT/name).read_bytes())==manifest['source_files'][name], 'IMAGE_RUNTIME_SOURCE_CHANGED')
    require(digest(trusted(ROOT/FILES[-1]).read_bytes())==AUTHORITY,'IMAGE_RUNTIME_AUTHORITY')
    require(Path(__file__).resolve()==ROOT/'tools/item4_image_runtime.py','IMAGE_RUNTIME_IMPORTED_SOURCE')
    require(digest(trusted(BASE_RECORD/'installed.json').read_bytes())==record['base_receipt_sha256'],
        'IMAGE_RUNTIME_BASE_RECEIPT_CHANGED')
    base=manifest_check(Path('/'),str(BASE_RECORD))
    require(base['layout']['release']==str(BASE),'IMAGE_RUNTIME_BASE_RELEASE')
    require(digest(trusted(CONFIG).read_bytes())==record['config_sha256'],'IMAGE_RUNTIME_CONFIG_CHANGED')
    config=json.loads(trusted(CONFIG).read_bytes());selected=json.loads(trusted(ROOT/FILES[-2]).read_bytes())
    require({k:v for k,v in config.items() if k!='units'}==selected,'IMAGE_RUNTIME_EXACT_SELECTION')
    from orchestrator import modal_environment_inventory as inventory,modal_pinned_image as image
    inventory.selection(config)
    require(config['schema']==image.SCHEMA,'IMAGE_RUNTIME_ITEM4_IMAGE_ONLY')
    return config


RUN='experiment-a74959ac4546a982af4ae137'
AUTHOR5='49cc364b033bf52198fbc44c5470bb72b9cfec03826294f71f2dd2286d244524'
RECOVERY=Path('/opt/research-system/manual-repair-helpers/item4-author5-submission-recovery-20261008')
RECOVERY_SHA='e43d1dac544a3fc4d8d9d7015a8558d1ed96b581e1dc6c172f97041051f6edc9'


def author5_terminal(batch):
    """Reuse the installed, independently approved qualification read-only."""
    import importlib.util
    import sqlite3
    from types import SimpleNamespace
    import orchestrator
    from orchestrator.manual_host_guard import trusted
    from orchestrator.manual_executor import digest
    path=trusted(RECOVERY/'tools/item4_submission_recovery_component.py')
    require(digest(path.read_bytes())==RECOVERY_SHA,'IMAGE_RECOVERY_SOURCE_CHANGED')
    spec=importlib.util.spec_from_file_location('_image_author5_recovery',path)
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    installed=h.verified()
    rec=h.module('_image_author5_original',RECOVERY/'orchestrator/author_submission_recovery.py')
    af=h.module('_image_author5_format',RECOVERY/'orchestrator/author_format_submission.py')
    previous=getattr(orchestrator,'author_format_submission',None)
    require(rec.CALL==AUTHOR5 and h.RUN==RUN,'IMAGE_RECOVERY_CALL_SCOPE')
    try:
        orchestrator.author_format_submission=af
        with sqlite3.connect((h.LANE/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as local:
            local.row_factory=sqlite3.Row
            driver=SimpleNamespace(state=h.LANE,config=json.loads((h.LANE/'lane.json').read_bytes()),
                store=SimpleNamespace(db=local,batch=batch))
            q=h.grant(driver,installed,rec)
            require(q['call']==AUTHOR5 and q['original_status']=='UNCERTAIN'
                and q['native_submission']=='REFUSED_NO_RECEIPT','IMAGE_RECOVERY_TERMINAL')
    finally:
        if previous is None:delattr(orchestrator,'author_format_submission')
        else:orchestrator.author_format_submission=previous
    return AUTHOR5


def qualified_closed(original,batch,run):
    closed=set(original(batch,run))
    if run!=RUN:return closed
    require(author5_terminal(batch)==AUTHOR5,'IMAGE_RECOVERY_EXACT_CALL')
    return closed|{AUTHOR5}


CPU_ROOT=Path('/opt/research-system/manual-repair-helpers/item6-contract-service-identity-20261008')
CPU_HELPER_SHA='7cb2a8744460d29fe719eddb7cd76ed75318d4b9ead12e4709b98328feeb90d0'
FIRST_STOP_SHA='0c0b687ce4d584f4e6360b55a7064ba307041eac8b7539445bcc8c0098ee8e97'
CPU_SUCCESS='6c6e617ac31cfc6cefb7426c7a4b4a45159c19dd4dc7acd56e90a12aecb3a173'
CPU_PARENTS={'d9bd52cf0b27045e1e23ba018ac44d9ed25cb2ab8ccf81f8c22cf33b4fb264e3',
    '2b0ab32a1f4d4890bb0f17a9986440e0675debcd9cbfc56746183e3dbab31795'}


def load_source(name,path):
    import importlib.util
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def stopped_item6(accounts):
    """Authenticate existing terminal proofs; keep all compute rows unchanged."""
    import orchestrator
    from orchestrator.manual_host_guard import trusted
    from orchestrator.manual_executor import digest
    helper=trusted(CPU_ROOT/'tools/item6_native_mount_service.py')
    require(digest(helper.read_bytes())==CPU_HELPER_SHA,'IMAGE_CPU_HELPER_CHANGED')
    h=load_source('_image_cpu_original',helper);h.checked()
    row=accounts.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(CPU_SUCCESS,)).fetchone()
    require(row is not None and row['status']=='COLLECTED' and row['run']=='diagnostics-b203ee1ce27e909d9d78d44a'
        and row['provider_id']=='sb-01M4CTVGT1CC1CSPY149KG94BK' and digest(row['binding'].encode())==CPU_SUCCESS,
        'IMAGE_CPU_SUCCESS_BINDING')
    previous=getattr(orchestrator,'diagnostics_native_guard',None)
    try:
        orchestrator.diagnostics_native_guard=load_source('_image_cpu_guard',CPU_ROOT/'orchestrator/diagnostics_native_guard.py')
        retry=load_source('_image_cpu_retry',CPU_ROOT/'orchestrator/diagnostics_mount_retry.py')
        stopped=retry.retained_parent(accounts,json.loads(row['binding']))
        require(stopped==CPU_PARENTS,'IMAGE_CPU_TERMINAL_SCOPE')
        first=trusted(Path('/var/lib/research-system-manual-sprint10-deployment/item6-native-mount-repair-20261008/parent-failed-stop.json')).read_bytes()
        require(digest(first)==FIRST_STOP_SHA,'IMAGE_CPU_FIRST_STOP_CHANGED')
        proof=json.loads(first)
        require(proof['result']=={'binding_sha256':'d9bd52cf0b27045e1e23ba018ac44d9ed25cb2ab8ccf81f8c22cf33b4fb264e3','files':{},'schema':'modal-result/v1','status':'FAILED'}
            and proof['stop']=={'provider_id':'sb-01M4CJFPRC3SJ1ZXPXG6APJA5H','terminated':True}
            and proof['reservation_retained'] is True,'IMAGE_CPU_FIRST_TERMINAL')
        return stopped
    finally:
        if previous is None:delattr(orchestrator,'diagnostics_native_guard')
        else:orchestrator.diagnostics_native_guard=previous


def main():
    require(os.getuid()==os.getgid()==1003,'IMAGE_RUNTIME_SERVICE_OWNER')
    require(sys.argv[1:]==['--config',str(CONFIG)],'IMAGE_RUNTIME_FIXED_CONFIG')
    verify()
    from orchestrator import modal_provider,modal_environment_inventory,spending_continuation,modal_environment_budget
    original=modal_provider.ModalProvider
    prior_closed=spending_continuation.closed_ids
    original_reserve=modal_environment_budget.reserve
    reviewed_budget=load_source('_image_accounting',ROOT/'orchestrator/modal_environment_budget.py')
    reviewed_budget.terminal_failed_compute=stopped_item6
    class Provider(original):
        def __init__(self,config):
            super().__init__(config)
            self.modal=ModalView(self.modal)
    # The ordinary lifecycle retains host checks, reservations, intents, limits,
    # billing, observation and refusal of uncertain or duplicate operations.
    modal_provider.ModalProvider=Provider
    spending_continuation.closed_ids=lambda batch,run:qualified_closed(prior_closed,batch,run)
    modal_environment_budget.reserve=reviewed_budget.reserve
    try:modal_environment_inventory.main()
    finally:
        modal_provider.ModalProvider=original
        spending_continuation.closed_ids=prior_closed
        modal_environment_budget.reserve=original_reserve


if __name__=='__main__':main()
