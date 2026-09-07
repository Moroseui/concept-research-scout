
import hashlib,json,os,sqlite3,subprocess,tarfile
from pathlib import Path
source='9af868d47fecaf26c82c88a4d957183ea50962f5'
root=Path('/opt/research-system/handover').resolve()
import sys
sys.path.insert(0,str(root))
from orchestrator.remote_supervisor import checked_source
from orchestrator.reviewer_evidence import collect
checked_source(root,source)
c=json.loads(Path('/etc/research-system/handover-broker.json').read_text())
r=json.loads(Path('/etc/research-system/handover-controller.json').read_text())
assert c['mode']=='SYNTHETIC_FIXTURE' and c['model_mode']=='SUPERVISED' and c['max_model_turns']==3 and c['writer_config'] is None
assert r['source']==source and r.get('report_schedule') is None and r.get('publication') is None
state=Path(r['state'])
def rows(query):
 db=sqlite3.connect('file:'+str(state/'coordinator.sqlite')+'?mode=ro',uri=True)
 try:return db.execute(query).fetchall()
 finally:db.close()
assert rows("SELECT count(*) FROM tasks WHERE status!='COMPLETE'")[0][0]==0
turns=Path(c['turn_root']);before=sorted(str(p) for p in turns.glob('*/binding.json'));assert len(before)==3
work=Path('/var/lib/research-system/final-service-evidence-9af868d');work.mkdir(mode=0o700)
for unit in ['research-system-handover-controller.service','research-system-handover-controller.timer','research-system-completion-fixture.timer']:
 assert subprocess.check_output(['systemctl','show',unit,'--property=ActiveState','--value'],text=True).strip() in ('inactive','failed')
with (work/'start.stdout').open('xb') as out,(work/'start.stderr').open('xb') as err:
 result=subprocess.run(['systemctl','start','research-system-handover-controller.service'],stdout=out,stderr=err,timeout=90)
assert result.returncode==0
assert sorted(str(p) for p in turns.glob('*/binding.json'))==before
assert rows("SELECT count(*) FROM tasks WHERE status!='COMPLETE'")[0][0]==0
observed=collect(root,{'kind':'service_runtime','purpose':'Current final supervised service configuration after one idle tick; historical cycle evidence remains separate.','affected_task':'first-handover'},hosted=True)
(work/'service-evidence.json').write_text(json.dumps(observed,indent=2))
units={}
for unit in ['research-system-handover.service','research-system-handover-controller.service','research-system-handover-controller.timer','research-system-completion-fixture.timer']:
 raw=subprocess.check_output(['systemctl','show',unit,'--property=ActiveState,SubState,Result,ExecMainStatus,User,MemoryMax,CPUQuotaPerSecUSec,TasksMax,NoNewPrivileges,PrivateNetwork'],text=True)
 units[unit]=dict(line.split('=',1) for line in raw.splitlines() if '=' in line)
assert units['research-system-handover-controller.service']['Result']=='success'
assert units['research-system-handover-controller.service']['ExecMainStatus']=='0'
permissions={}
for user in ['research-controller','research-driver','research-reviewer','research-worker']:
 exists=subprocess.run(['id',user],capture_output=True).returncode==0
 if not exists:permissions[user]={'identity_exists':False};continue
 permissions[user]={'identity_exists':True,'installed_source_writable':subprocess.run(['runuser','-u',user,'--','test','-w',str(root)],capture_output=True).returncode==0,
 'broker_config_writable':subprocess.run(['runuser','-u',user,'--','test','-w','/etc/research-system/handover-broker.json'],capture_output=True).returncode==0}
 assert not permissions[user]['installed_source_writable'] and not permissions[user]['broker_config_writable']
with (work/'original-journal.log').open('xb') as out:
 subprocess.run(['journalctl','--no-pager','-u','research-system-handover-controller.service','-n','120'],stdout=out,check=True)
receipt={'status':'PASSED_SUPERVISED_IDLE_TICK','source':source,'model_turns_before':3,'model_turns_after':3,'new_model_calls':0,'new_scientific_jobs':0,'units':units,'role_write_boundaries':permissions,'configured':{'writer':False,'notifications':r.get('notifications') is True,'schedule':False,'purpose':r['purpose'],'max_model_turns':3},'control_state':rows('SELECT revision,paused FROM controls')[0],'coordinator_tasks':rows('SELECT id,status FROM tasks'),'review_bookkeeping':rows('SELECT status,count(*) FROM bookkeeping GROUP BY status'),'service_evidence_sha256':hashlib.sha256((work/'service-evidence.json').read_bytes()).hexdigest(),'unattended_observation':False}
(work/'receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
