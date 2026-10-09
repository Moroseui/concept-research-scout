"""Install a reviewed fixed synthetic operation, disabled and unspent."""
from pathlib import Path
import importlib.util,json,os,stat,subprocess,sys
from tools import item4_native_runtime as h


def install(packet,review,source,bundle):
 from orchestrator.autonomy_review import verify_packet,verify_result,canonical
 from orchestrator.manual_host_guard import trusted
 from orchestrator.manual_executor import digest
 from orchestrator import modal_native_synthetic as n,modal_environment_inventory as inventory
 h.require(os.getuid()==0,'INSTALL_ROOT')
 packet,review,bundle=map(Path,(packet,review,bundle))
 manifest=verify_packet(packet);approval=verify_result(review)
 h.require(approval['verdict']=='APPROVE' and approval['change_id']==manifest['change_id']==h.REVIEW_CHANGE
  and approval['source_sha']==manifest['source_sha']==source,'INSTALL_APPROVAL')
 h.require(canonical(manifest)==canonical(json.loads((review/'packet-manifest.json').read_bytes())),'INSTALL_PACKET')
 raw={name:(packet/'source'/name).read_bytes() for name in h.FILES}
 h.require(all(digest(body)==manifest['source_files'][name] for name,body in raw.items()),'INSTALL_SOURCE')
 h.require(raw['tools/install_item4_native_runtime.py']==Path(__file__).read_bytes()
  and raw['tools/item4_native_runtime.py']==Path(h.__file__).read_bytes(),'INSTALL_EXECUTED_SOURCE')
 h.require(digest(raw[h.FILES[-1]])==h.AUTHORITY,'INSTALL_AUTHORITY')
 runtime=Path('/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json')
 h.require(approval['runtime_sha256']==digest(trusted(runtime).read_bytes()),'INSTALL_REVIEW_RUNTIME')
 old=h.image_helper().verify();config=h.config_from_image(old)
 h.require({k:v for k,v in old.items() if k!='units'}==json.loads(raw['docs/ITEM4_PINNED_IMAGE_SELECTION_20261008.json']),'INSTALL_BASE_SELECTION')
 code=bundle.read_bytes();sel=n.selected()
 h.require(digest(code)==sel['code_bundle_sha256'] and len(code)==sel['code_bundle_bytes'],'INSTALL_BUNDLE')
 # Validate all transferred source bytes, membership and no data payloads using
 # the same bounded extractor; nothing in the bundle is executed by installer.
 import tempfile,base64,gzip
 from tools import item4_native_worker as worker
 with tempfile.TemporaryDirectory(prefix='native-install-source-check-') as td:
  worker.unpack(base64.b64encode(gzip.compress(code,mtime=0)).decode(),sel,Path(td))
  worker.check_package(Path(td),sel)
 name=inventory.unit_name(config);unit=Path('/etc/systemd/system')/name
 if h.ROOT.exists():return upgrade(packet,review,source,raw,approval,config,code)
 targets=[h.ROOT,h.RECORD,h.CONFIG.parent,h.STATE,unit]
 h.require(all(not p.exists() and not p.is_symlink() for p in targets),'INSTALL_EXISTS_RECONCILE')
 # Reuse the already-reviewed exact service-owned state-parent check; no
 # ownership/permission changes to any existing state or credential.
 from tools.install_item4_image_runtime import destination_parent
 for p in targets:
  if p==h.STATE:destination_parent(h.IMAGE_STATE)
  else:
   ancestor=p.parent
   while not ancestor.exists():ancestor=ancestor.parent
   trusted(ancestor)
 system=unit.parent
 h.require(not any((d/name).exists() or (d/name).is_symlink() for pattern in ('*.wants','*.requires') for d in system.glob(pattern)),'INSTALL_PREENABLED')
 def put(p,body):
  p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
  with p.open('xb') as f:f.write(body)
  os.chown(p,0,1003);p.chmod(0o440)
 h.ROOT.mkdir(mode=0o700);h.RECORD.mkdir(mode=0o700)
 put(h.RECORD/'INSTALL_INTENT.json',canonical({'source':source,'review':approval,'operation':n.OPERATION,'status':'DISABLED_UNSPENT'}))
 for name,body in raw.items():put(h.ROOT/name,body)
 for p in review.iterdir():
  h.require(p.is_file() and not p.is_symlink(),'INSTALL_REVIEW_FILE');put(h.RECORD/'review'/p.name,p.read_bytes())
 put(h.RECORD/'code-bundle.json',code)
 put(h.CONFIG,canonical(config));put(unit,h.rendered(config))
 h.STATE.mkdir(mode=0o700);os.chown(h.STATE,1003,1003)
 record={'source':source,'review_sha256':approval['report_sha256'],'config_sha256':digest(canonical(config)),
  'base_source':config['source'],'base_receipt_sha256':config['installation_sha256'],'unit':unit.name,'model_calls':0,'provider_calls':0}
 put(h.RECORD/'installed.json',canonical(record))
 # Finalize new directories BEFORE the unprivileged postcheck.
 for root in (h.ROOT,h.RECORD,h.CONFIG.parent):
  for p in [root,*[v for v in root.rglob('*') if v.is_dir()]]:os.chown(p,0,1003);p.chmod(0o550)
 script=f"import importlib.util;from pathlib import Path;p=Path({str(h.ROOT/'tools/item4_native_runtime.py')!r});s=importlib.util.spec_from_file_location('native_installed',p);h=importlib.util.module_from_spec(s);s.loader.exec_module(h);h.bootstrap();h.verify(unit=False);print('STATIC_VERIFY_PASS')"
 envarg='RESEARCH_MANUAL_RUNTIME_CONFIG=/etc/research-system-manual-sprint10/releases/'+h.BASE.name+'/runtime.json'
 verified=subprocess.run(['runuser','-u','partho','--','env',envarg,'python3','-s','-B','-c',script],capture_output=True)
 put(h.RECORD/'verify.stdout',verified.stdout);put(h.RECORD/'verify.stderr',verified.stderr)
 h.require(verified.returncode==0 and verified.stdout.strip()==b'STATIC_VERIFY_PASS','INSTALL_POSTCHECK')
 put(h.RECORD/'COMPLETE.json',canonical({'status':'INSTALLED_DISABLED','provider_calls':0,'model_calls':0}))
 return {'status':'INSTALLED_DISABLED','unit':unit.name,'provider_calls':0,'model_calls':0}


PRIOR_SOURCE='e16bb77f5c7363d7b306e354db960827291095d5'


def upgrade(packet,review,source,raw,approval,config,code):
 """Replace only the known stopped author11 helper; retain all originals/costs."""
 from orchestrator.manual_host_guard import trusted
 from orchestrator.manual_executor import digest
 from orchestrator.autonomy_review import canonical
 from orchestrator import modal_native_synthetic as n
 old=json.loads(trusted(h.RECORD/'installed.json').read_bytes())
 h.require(old['source']==PRIOR_SOURCE,'UPGRADE_EXACT_PRIOR_SOURCE')
 unit=old['unit'];props=dict(x.split('=',1) for x in subprocess.check_output(
  ['systemctl','show',unit,'-p','ActiveState','-p','MainPID'],text=True).splitlines())
 h.require(props['MainPID']=='0' and props['ActiveState'] in {'inactive','failed'},'UPGRADE_RUNNING')
 h.require(not h.STATE.exists() and not h.STATE.is_symlink(),'UPGRADE_NEW_STATE_EXISTS')
 from tools.install_item4_image_runtime import destination_parent
 destination_parent(h.IMAGE_STATE)
 program="""from pathlib import Path
import os,importlib.util,json,sqlite3
assert os.getuid()==os.getgid()==1003
p=Path('/opt/research-system/manual-repair-helpers/item4-native-cpu-rehearsal-20261008/tools/item4_native_runtime.py')
s=importlib.util.spec_from_file_location('native_old',p);h=importlib.util.module_from_spec(s);s.loader.exec_module(h);h.bootstrap();c,proof=h.verify()
print(json.dumps({'proof':proof,'config':c,'files':h.FILES}))
"""
 envarg='RESEARCH_MANUAL_RUNTIME_CONFIG=/etc/research-system-manual-sprint10/releases/'+h.BASE.name+'/runtime.json'
 cmd=['runuser','-u','partho','--','env',envarg,'python3','-s','-B','-c']
 checked=json.loads(subprocess.check_output(cmd+[program],text=True))
 h.require(checked['proof']['helper_source']==PRIOR_SOURCE,'UPGRADE_OLD_PROOF')
 # Fresh process: actual candidate modules, real UID1003 readonly ledger,
 # unchanged old terminal files and accepted author12/image before mutations.
 candidate=f"""import os,sys,json,sqlite3
from pathlib import Path
from types import SimpleNamespace
assert os.getuid()==os.getgid()==1003
sys.path.insert(0,{str(h.BASE)!r})
import orchestrator,tools
# This module requires its actual installed path. Import it and its guarded
# dependencies from the verified base before exposing review-only source copies.
from orchestrator import spending_continuation
orchestrator.__path__.insert(0,{str(packet/'source/orchestrator')!r})
tools.__path__=[{str(packet/'source/tools')!r},*tools.__path__]
from orchestrator import modal_native_successor as successor,modal_native_synthetic as n
from tools import item4_native_runtime as runtime
with sqlite3.connect('file:/var/lib/research-system-autonomy/reviews/jobs.sqlite?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 accounts=SimpleNamespace(db=db,batch=SimpleNamespace(db=db,folder=Path('/var/lib/research-system-autonomy/reviews'),filesystem_root=Path('/')))
 original=successor.proof()['asset'];binding=json.loads(original['binding'])
 binding.update(operation_id=n.OPERATION,native_synthetic=n.selected())
 successor.qualify(accounts,binding);runtime.author_and_image(accounts)
 print('PREDECESSOR_AUTHOR_IMAGE_PASS')
"""
 h.require(subprocess.check_output(cmd+[candidate],text=True).strip()=='PREDECESSOR_AUTHOR_IMAGE_PASS','UPGRADE_PREDECESSOR')
 history=h.RECORD/'history'/PRIOR_SOURCE;staged=h.RECORD/('upgrade-staged-'+source)
 h.require(not history.exists() and not staged.exists(),'UPGRADE_EXISTS_RECONCILE')
 def put(p,body):
  p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
  with p.open('xb') as out:out.write(body)
  os.chown(p,0,1003);p.chmod(0o440)
 put(history/'UPGRADE_INTENT.json',canonical({'source':source,'review':approval,'prior':old,
  'scope':'exact author12 successor; no model/provider/reservation mutation; original state and full costs retained'}))
 for name in checked['files']:put(history/'source'/name,trusted(h.ROOT/name).read_bytes())
 for name in ('installed.json','COMPLETE.json','START_INTENT.json','START_RECOVERY_INTENT.json','code-bundle.json'):
  put(history/name,trusted(h.RECORD/name).read_bytes())
 put(history/'original-config.json',trusted(h.CONFIG).read_bytes())
 unit_path=Path('/etc/systemd/system')/unit;put(history/'original-unit.service',trusted(unit_path).read_bytes())
 for name,body in raw.items():put(staged/'source'/name,body)
 for p in review.iterdir():
  h.require(p.is_file() and not p.is_symlink(),'UPGRADE_REVIEW_FILE');put(staged/'review'/p.name,p.read_bytes())
 record={**old,'source':source,'review_sha256':approval['report_sha256'],'previous_source':PRIOR_SOURCE,
  'config_sha256':digest(canonical(config)),'money_authority_sha256':h.AUTHORITY}
 put(staged/'installed.json',canonical(record));put(staged/'config.json',canonical(config))
 put(staged/'unit.service',h.rendered(config));put(staged/'code-bundle.json',code)
 h.STATE.mkdir(mode=0o700);os.chown(h.STATE,1003,1003)
 for name in raw:os.replace(staged/'source'/name,h.ROOT/name)
 (h.RECORD/'review').rename(history/'original-review-directory')
 (staged/'review').rename(h.RECORD/'review')
 for name,dest in [('installed.json',h.RECORD/'installed.json'),('config.json',h.CONFIG),('unit.service',unit_path),('code-bundle.json',h.RECORD/'code-bundle.json')]:os.replace(staged/name,dest)
 for root in (h.ROOT,h.RECORD,h.CONFIG.parent):
  for p in [root,*[v for v in root.rglob('*') if v.is_dir()]]:os.chown(p,0,1003);p.chmod(0o550)
 subprocess.run(['systemctl','daemon-reload'],check=True)
 check=program[:program.index('print(json.dumps')]+"print('UPGRADE_VERIFY_PASS')"
 result=subprocess.run(cmd+[check],capture_output=True)
 put(history/'verify.stdout',result.stdout);put(history/'verify.stderr',result.stderr)
 h.require(result.returncode==0 and result.stdout.strip()==b'UPGRADE_VERIFY_PASS','UPGRADE_POSTCHECK')
 put(history/'UPGRADE_COMPLETE.json',canonical({'status':'UPDATED_HELD','provider_calls':0,'model_calls':0,'original_reservation_unchanged':True,'new_reservation':False}))
 return {'status':'UPDATED_HELD','unit':unit,'provider_calls':0,'model_calls':0,'original_reservation_unchanged':True,'new_reservation':False}


if __name__=='__main__':
 import argparse
 os.umask(0o077);p=argparse.ArgumentParser()
 for name in ('packet','review','source','bundle'):p.add_argument('--'+name,required=True)
 a=p.parse_args();print(json.dumps(install(a.packet,a.review,a.source,a.bundle)))
