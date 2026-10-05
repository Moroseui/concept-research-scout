"""Scratch-only integration setup. Approval, installation and context are synthetic.
The captured UNCERTAIN rows/allowance are genuine, unmodified private fixtures.
No model is invoked. No business validator is substituted by this helper.
"""
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import time
from orchestrator import stocktake_recovery as rec, stocktake_manual_review as manual
from orchestrator import autonomy_review as review
from orchestrator.manual_executor import atomic, digest, read
from tools import deploy_manual_lane as deploy, manual_promotion as promotion

REPO=Path(__file__).resolve().parents[1]

def git(root,*args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()

def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(value if isinstance(value,bytes) else review.canonical(value))

def prepare(base,evidence,source=REPO):
    base,evidence,source=map(Path,(base,evidence,source))
    os.umask(0o077);base.mkdir(parents=True,exist_ok=True)
    checkout=base/'source'
    # Exact working candidate bytes, committed only in this disposable copy.
    shutil.copytree(source,checkout,ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache'))
    git(checkout,'init','-q');git(checkout,'add','.')
    git(checkout,'-c','user.name=Scratch','-c','user.email=scratch@invalid','commit','-qm','Synthetic integration fixture from current candidate')
    tag='research-manual-sprint10-20260926-rc3'
    git(checkout,'-c','user.name=Scratch','-c','user.email=scratch@invalid','tag','-am','Synthetic only',tag)
    host=base/'host';host.mkdir();(host/'etc/systemd/system').mkdir(parents=True)
    (host/'run').mkdir();old=host/'var/lib/research-system';old.mkdir(parents=True)
    write(old/'pause.json',{'paused':True,'fixture':'synthetic old host'})
    with sqlite3.connect(old/'jobs.sqlite') as db:db.execute('CREATE TABLE jobs(id PRIMARY KEY,status)')
    write(old/'receipts/original.json',{'fixture':'synthetic'})
    write(old/'log.txt',b'Synthetic original log\n');write(old/'snapshot.json',{'status':'PASS','kind':'synthetic fixture'})
    unit='research-synthetic-old.service';definition=host/'etc/systemd/system'/unit
    write(definition,b'Synthetic original unit\n')
    write(host/'run/manual-deploy-test-units.json',{'units':{unit:{'enabled':False,'active':False}},'calls':[]})
    old_file=base/'old-inventory.json'
    write(old_file,{'units':[{'name':unit,'enabled':False,'active':False,'definition_sha256':digest(definition.read_bytes())}],
        'pause_files':['/var/lib/research-system/pause.json'],'databases':['/var/lib/research-system/jobs.sqlite'],
        'receipt_directories':['/var/lib/research-system/receipts'],'logs':['/var/lib/research-system/log.txt'],
        'snapshot_verification':{'path':'/var/lib/research-system/snapshot.json','sha256':digest((old/'snapshot.json').read_bytes())}})
    oldstate=deploy.bound(host,rec.OLD_STATE);oldstate.mkdir(parents=True)
    for name in ('lane.json','preparation-plan.json'):shutil.copyfile(evidence/'lane'/name,oldstate/name)
    config=read(oldstate/'lane.json')
    context=evidence/'lane/context'
    if context.exists():shutil.copytree(context,oldstate/'context')
    else:write(oldstate/'context/SYNTHETIC.txt',b'Synthetic context for migration/admission only; no scientific consumption.\n')
    write(deploy.bound(host,config['owner_path']),config['owner_binding'])
    ledger=deploy.bound(host,config['batch_ledger']);ledger.mkdir(parents=True)
    for captured,dest in [('lane.sqlite',oldstate/'jobs.sqlite'),('accounting.sqlite',ledger/'jobs.sqlite')]:
        # Byte copies include retained WAL; do not open the originals with SQLite.
        for suffix in ('','-wal','-shm'):
            p=evidence/(captured+suffix)
            if p.exists():shutil.copyfile(p,Path(str(dest)+suffix))
    previous_layout=promotion.layout(Path(rec.OLD_STATE).parent.name)
    # Synthetic old installation carrier. Canonical old lane/ledger remain real.
    prior_file=deploy.bound(host,previous_layout['release']+'/SYNTHETIC.txt')
    write(prior_file,b'Synthetic installed carrier; not an assertion about deployed bytes.\n')
    runtime=deploy.bound(host,previous_layout['config']+'/runtime.json')
    write(runtime,(checkout/'deploy/manual-lane/runtime.promotion.json').read_bytes())
    files={'/'+str(prior_file.relative_to(host)):{'sha256':digest(prior_file.read_bytes()),'mode':0o600}}
    hashlist=deploy.bound(host,previous_layout['record']+'/FILES.json');write(hashlist,files)
    previous={'source':rec.BASE,'release':previous_layout['release'],'state':previous_layout['state'],'units':previous_layout['units'],
        'hash_list':previous_layout['record']+'/FILES.json','hash_list_sha256':digest(hashlist.read_bytes()),
        'runtime':previous_layout['config']+'/runtime.json','runtime_sha256':digest(runtime.read_bytes())}
    prev=base/'previous.json';write(prev,previous);write(deploy.bound(host,promotion.POINTER),previous)
    head=git(checkout,'rev-parse','HEAD');tag='research-manual-sprint10-round2-scratch'
    git(checkout,'-c','user.name=Scratch','-c','user.email=scratch@invalid','tag','-am','Synthetic only',tag)
    manifest={'change_id':manual.CHANGE,'source_sha':head,'runtime_sha256':rec.RUNTIME,'round':2,
        'predecessor':{'report_sha256':'9d1b76c5179c8c8bf073a82ca7547c1586332b2f61ac64f5f546fef5d122826f'},
        'files':{'evidence/analysis-plan.json':rec.PLAN}}
    packet=digest(review.canonical(manifest));folder=deploy.bound(host,str(manual.ROOT))/packet
    report=('SYNTHETIC APPROVAL FOR SCRATCH ONLY; never independent authority.\nsource_sha: '+head+'\nruntime_sha256: '+rec.RUNTIME+
        '\npacket_sha256: '+packet+'\nanalysis_entrypoint: orchestrator.analysis_driver\nreviewer_product: Claude Code\nreviewer_model: synthetic\nreviewer_session_id: unavailable\n## Verdict: APPROVE\n\n## Blockers\nNone.\n')
    write(folder/'packet-manifest.json',manifest);write(folder/'report.md',report.encode())
    original=b'Synthetic operator provenance fixture, not an actual decision.'
    write(folder/'operator-return-original.txt',original);write(folder/'evidence-files.json',{'operator-return-original.txt':digest(original)})
    return {'host':host,'checkout':checkout,'oldstate':oldstate,'ledger':ledger,'folder':folder,'head':head,
        'args':(host,checkout,tag,head,git(checkout,'rev-parse',tag),folder/'report.md',digest(report.encode()),prev,old_file),
        'runtime':checkout/'deploy/manual-lane/runtime.promotion.json'}

def qualify(f):
    value=manual.inputs(f['folder'],filesystem_root=f['host'])
    receipt={'review':value,'accounting_units':1,'synthetic_provenance':True}
    write(f['folder']/'qualification.json',receipt)
    with sqlite3.connect(f['ledger']/'jobs.sqlite') as db:
        db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('manual-stocktake-'+value['packet_sha256'],'implementation_review',manual.CHANGE,2,'2026-01-01','COMPLETE','{}',review.canonical(receipt).decode()))
    assert manual.verify(f['folder'],filesystem_root=f['host'])==value
    return value

def matrix(f,root):
    connections=[]
    for stage in ('run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review'):
        for n in range(1,4 if stage==rec.STAGE else 3):
            proof={'status':'PASS','stage':stage,'family':'claude' if stage.endswith('review') else 'codex',
                'input_sha256':rec.PROMPT,'model_client_launched':False,'isolated_stdin':True,
                'producer_sha256':digest((root/'scout.py').read_bytes()),'transport_sha256':digest((root/'orchestrator/manual_stage.py').read_bytes()),
                'fixture':'SYNTHETIC transport record; real producer/sink verified separately'}
            path=f['host']/'proofs'/(stage+str(n)+'.json');write(path,proof)
            connections.append({'stage':stage,'round':n,'proof_path':str(path),'proof_sha256':digest(path.read_bytes()),'proof':proof})
    value={'schema':'stocktake-transport-matrix/v2','runtime_sha256':rec.RUNTIME,'connections':connections,
        'installation':rec.installed_selection(root,f['host']),'recorded_at':time.time()}
    rec.validate_matrix(value,root,filesystem_root=f['host'])
    path=f['host']/'matrix.json';write(path,value);return path
