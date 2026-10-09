"""Fixed author12 rehearsal; verifies both reviewed patch and existing image."""
from pathlib import Path
import importlib.util,json,os,subprocess,sys,time
CHANGE='item4-native-cpu-rehearsal-20261008'
REVIEW_CHANGE='item4-native-import-binding-20261009'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
CONFIG=Path('/etc/research-system-manual-sprint10')/CHANGE/'config.json'
STATE=Path('/var/lib/research-system-manual-sprint10/environment-inventory/item4-author12-native-synthetic-v1')
BASE=Path('/opt/research-system/manual-sprint10/research-manual-sprint10-spending-a51ac44279e4')
IMAGE_ROOT=Path('/opt/research-system/manual-repair-helpers/item4-image-runtime-20261008')
IMAGE_HELPER_SHA='26e0172ad5986463ec618ffb9c7d5c48d333c04645461df3b14c3e6a571e7c51'
IMAGE_STATE=STATE.parent/'item4-pinned-scientific-image-v1'
AUTHORITY='8f645432a26ba2030392d2d390950252c4c8be075c87c3fca9d3dd9646ff1ec1'
FILES=('orchestrator/modal_environment_budget.py','orchestrator/modal_environment_inventory.py',
 'orchestrator/modal_environment_provider.py','orchestrator/modal_pinned_image.py','orchestrator/modal_native_synthetic.py',
 'tools/item4_native_worker.py','tools/item4_native_runtime.py','tools/install_item4_native_runtime.py',
 'docs/ITEM4_NATIVE_PRECREATE_REFUSAL_20261008.json','docs/ITEM4_NATIVE_SYNTHETIC_SELECTION_20261008.json','docs/ITEM4_PINNED_IMAGE_SELECTION_20261008.json',
 'orchestrator/modal_billing.py','orchestrator/modal_native_successor.py','docs/ITEM4_NATIVE_AUTHOR12_PREDECESSOR_20261009.json',
 'docs/OVERNIGHT_AUTONOMY_OPERATOR_DECISION_20261008.txt','docs/ITEM4_SMOKE_RETRY_OPERATOR_DECISION_20261009.txt')
PROPS={'User':'partho','Group':'partho','UMask':'0077','NoNewPrivileges':'yes','ProtectSystem':'strict',
 'PrivateTmp':'yes','ProtectHome':'read-only','RestrictSUIDSGID':'yes','LockPersonality':'yes'}
LANE=Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/item4/lane')


def require(ok,why):
 if not ok:raise ValueError('NATIVE_RUNTIME_'+why)


def bootstrap():
 # Base remains independently manifest-checked. Only listed reviewed modules
 # resolve from the patch; no filesystem identity or promotion receipt is faked.
 sys.path.insert(0,str(BASE))
 import orchestrator,tools
 orchestrator.__path__=[str(ROOT/'orchestrator'),*orchestrator.__path__]
 tools.__path__=[str(ROOT/'tools'),*tools.__path__]


def image_helper():
 from orchestrator.manual_host_guard import trusted
 from orchestrator.manual_executor import digest
 p=trusted(IMAGE_ROOT/'tools/item4_image_runtime.py')
 require(digest(p.read_bytes())==IMAGE_HELPER_SHA,'IMAGE_HELPER_CHANGED')
 spec=importlib.util.spec_from_file_location('_native_existing_image_helper',p)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def config_from_image(old):
 from orchestrator import modal_native_synthetic as n,modal_environment_inventory as inventory
 from orchestrator.modal_executor import canonical
 from orchestrator.manual_executor import digest
 selected=n.selected()
 result={k:v for k,v in old.items() if k not in {'units','image_build'}}
 result.update(schema=n.SCHEMA,operation_id=n.OPERATION,image_id=selected['image_id'],
 state=str(STATE),worker_sha256=n.worker_sha256(),native_synthetic=selected)
 result['units']={inventory.unit_name(result):{'sha256':digest(rendered(result))}}
 inventory.selection(result);return result


def rendered(config):
 return f"""[Unit]
Description=Fixed author12 synthetic CPU rehearsal
After=network-online.target
Wants=network-online.target
[Service]
Type=oneshot
User=partho
Group=partho
UMask=0077
WorkingDirectory={BASE}
Environment=PYTHONPATH={BASE}:{config['provider']['sdk_package']}
Environment=RESEARCH_MANUAL_RUNTIME_CONFIG=/etc/research-system-manual-sprint10/releases/{BASE.name}/runtime.json
ExecStart=/usr/bin/python3 -s -B {ROOT}/tools/item4_native_runtime.py --config {CONFIG}
TimeoutStartSec=1200
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=true
ReadWritePaths={STATE} {config['batch_ledger']}
RestrictSUIDSGID=true
LockPersonality=true
[Install]
WantedBy=multi-user.target
""".encode()


def verify(*,unit=True):
 from orchestrator.manual_host_guard import trusted
 from orchestrator.manual_executor import digest
 from orchestrator.autonomy_review import verify_result
 from orchestrator import modal_native_synthetic as n,modal_environment_inventory as inventory
 record=json.loads(trusted(RECORD/'installed.json').read_bytes())
 approval=verify_result(trusted(RECORD/'review'))
 manifest=json.loads(trusted(RECORD/'review/packet-manifest.json').read_bytes())
 require(approval['verdict']=='APPROVE' and approval['change_id']==REVIEW_CHANGE
  and approval['source_sha']==manifest['source_sha']==record['source']
  and approval['report_sha256']==record['review_sha256'],'GENUINE_APPROVAL')
 for name in FILES:require(digest(trusted(ROOT/name).read_bytes())==manifest['source_files'][name],'SOURCE_CHANGED')
 require(Path(__file__).resolve()==ROOT/'tools/item4_native_runtime.py','RUNTIME_SOURCE')
 require(digest(trusted(ROOT/FILES[-1]).read_bytes())==AUTHORITY,'AUTHORITY')
 for name in (*FILES[:5],'orchestrator/modal_billing.py','orchestrator/modal_native_successor.py'):
  m=__import__(name[:-3].replace('/','.'),fromlist=['__file__'])
  require(Path(m.__file__).resolve()==ROOT/name,'IMPORTED_SOURCE')
 old=image_helper().verify();expected=config_from_image(old)
 raw=trusted(CONFIG).read_bytes();config=json.loads(raw)
 require(config==expected and digest(raw)==record['config_sha256'],'CONFIG_CHANGED')
 require(digest(trusted(RECORD/'code-bundle.json').read_bytes())==n.selected()['code_bundle_sha256'],'BUNDLE_CHANGED')
 n.bundle();n.arguments({'native_synthetic':n.selected()})  # Actual bounded payload before admission.
 name=inventory.unit_name(config);up=trusted(Path('/etc/systemd/system')/name)
 require(up.read_bytes()==rendered(config),'UNIT_CHANGED')
 if unit:
  require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,'SERVICE_IDENTITY')
  observed=subprocess.check_output(['systemctl','show',name,'--property='+','.join(PROPS)],text=True)
  require(dict(x.split('=',1) for x in observed.splitlines() if '=' in x)==PROPS,'SERVICE_RESTRICTIONS')
 return config,{'status':'PASS','source':config['source'],'installation_sha256':config['installation_sha256'],
  'config_sha256':digest(raw),'helper_source':record['source'],'helper_review_sha256':record['review_sha256']}


def author_and_image(accounts):
 import sqlite3
 from orchestrator import modal_native_synthetic as n,modal_pinned_image as image
 from orchestrator import private_records as pr
 s=n.selected()
 with sqlite3.connect((LANE/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as db:
  db.row_factory=sqlite3.Row
  row=db.execute('SELECT * FROM manual_calls WHERE id=?',(s['author_call_id'],)).fetchone()
  require(row is not None and row['status']=='COMPLETE' and row['stage']=='run_spec_author' and row['attempt']==12,'ACCEPTED_AUTHOR')
  receipt=json.loads(row['receipt']);accepted=receipt['native']['author_submission']
  require(accepted['status']=='ACCEPTED' and accepted['record_sha256']==s['accepted_submission_sha256'],'SUBMISSION_BINDING')
  state=json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
  require(state['phase']=='run_spec_review' and state['rounds']['run_spec_author']==12 and state['rounds']['run_spec_review']==6,'HELD_REVIEW7')
  require(any(a['id']=='synthetic_tests' and a['sha256']==s['controller_receipt_sha256'] for a in state['artifacts']),'CONTROLLER_RECEIPT')
 globalrow=accounts.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(s['author_call_id'],)).fetchone()
 require(globalrow is not None and globalrow['status']=='COMPLETE','GLOBAL_AUTHOR_TERMINAL')
 binding=json.loads(pr.check(IMAGE_STATE/'binding.json').read_bytes())
 proof=image.consumer_proof(accounts,binding,IMAGE_STATE)
 require(proof['scientific_environment']==s['environment'] and proof['scientific_acceptance'] is False,'READY_IMAGE_PROVENANCE')
 return proof


def main():
 require(sys.argv[1:]==['--config',str(CONFIG)],'FIXED_ARGUMENTS')
 require(os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,'SERVICE_IDENTITY')
 bootstrap();config,proof=verify()
 from orchestrator import spending_continuation,modal_environment_budget as budget,modal_environment_inventory as inventory
 from orchestrator import private_records as pr,connectivity
 from orchestrator.autonomy_accounting import BatchAccounts
 from orchestrator.modal_budget import ComputeAccounts
 from orchestrator.modal_provider import ModalProvider
 from orchestrator.manual_executor import digest
 from orchestrator.modal_executor import canonical
 helper=image_helper();prior=spending_continuation.closed_ids
 spending_continuation.closed_ids=lambda batch,run:helper.qualified_closed(prior,batch,run)
 budget.terminal_failed_compute=helper.stopped_item6
 batch=BatchAccounts(config['batch_ledger'])
 try:
  accounts=ComputeAccounts(batch);author_and_image(accounts)
  saved=STATE/'binding.json';existing=json.loads(pr.check(saved).read_bytes()) if saved.exists() else None
  row=accounts.db.execute('SELECT status FROM autonomy_assets WHERE id=?',(digest(canonical(existing)),)).fetchone() if existing else None
  local=row is not None and (row['status'] in {'READY','UNCERTAIN'} or (STATE/'provider').exists() and not (STATE/'provider/sandbox.json').exists())
  # The original pre-create continuation was consumed. New attempt has no
  # recovery path: any interrupted create/send remains held for reconciliation.
  provider=None
  if not local:
   connectivity.require(['modal'],STATE/'connectivity.json');provider=ModalProvider(config['provider'])
  deadline=time.monotonic()+1020
  while True:
   result=inventory.tick(config,provider,accounts,host_proof=proof)
   pr.atomic(STATE/'STATUS.json',result)
   if result['status']!='RUNNING' or time.monotonic()>=deadline:break
   time.sleep(10)
  print(json.dumps({k:v for k,v in result.items() if k in {'status','no_automatic_retry','scientific_calls'}}))
  if result['status']!='VERIFIED':raise SystemExit(1)
 finally:batch.db.close()


if __name__=='__main__':main()
