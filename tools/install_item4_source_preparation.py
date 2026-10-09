"""Install only the independently reviewed frozen-source helper and retention."""
from pathlib import Path
import json,os,subprocess,sys
from tools import item4_source_preparation as h

def install(packet,review,source,metadata):
    from orchestrator.autonomy_review import verify_packet,verify_result,canonical
    from orchestrator.manual_host_guard import trusted
    from orchestrator.manual_executor import digest
    h.require(os.getuid()==0,'INSTALL_ROOT')
    packet,review,metadata=map(Path,(packet,review,metadata));m=verify_packet(packet);a=verify_result(review)
    h.require(a['verdict']=='APPROVE' and a['change_id']==m['change_id']==h.REVIEW_CHANGE
              and a['source_sha']==m['source_sha']==source,'INSTALL_APPROVAL')
    h.require(json.loads((review/'packet-manifest.json').read_bytes())==m,'INSTALL_PACKET')
    raw={name:trusted(packet/'source'/name).read_bytes() for name in h.FILES}
    h.require(all(digest(body)==m['source_files'][name] for name,body in raw.items()),'INSTALL_SOURCE')
    h.require(raw['tools/install_item4_source_preparation.py']==Path(__file__).read_bytes()
              and raw['tools/item4_source_preparation.py']==Path(h.__file__).read_bytes(),'INSTALL_EXECUTED_SOURCE')
    runtime=Path('/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json')
    h.require(a['runtime_sha256']==digest(trusted(runtime).read_bytes()),'INSTALL_RUNTIME')
    native=h.native_helper();cfg,proof=native.verify(unit=False)
    h.require(proof['helper_source']==h.NATIVE_SOURCE and proof['helper_review_sha256']==h.NATIVE_REVIEW,'INSTALL_NATIVE_RELEASE')
    import orchestrator
    orchestrator.__path__.insert(0,str(packet/'source/orchestrator'))
    from orchestrator import modal_source_composition as composition
    composition.contract(metadata)
    inputs={name:trusted(metadata/name).read_bytes() for name in ('cohort.json','source.json','auxiliary.json','authority.txt','split.csv')}
    config={'schema':'item4-source-service/v1','state':str(h.STATE),'metadata':str(h.METADATA),
            'provider':cfg['provider'],'batch_ledger':cfg['batch_ledger'],'base_source':cfg['source'],'owner_sha256':cfg['owner_sha256']}
    units=h.units(native.BASE,config)
    targets=[h.ROOT,h.RECORD,h.CONFIG.parent,*[Path('/etc/systemd/system')/n for n in units]]
    h.require(all(not p.exists() and not p.is_symlink() for p in targets),'INSTALL_EXISTS_RECONCILE')
    for p in targets:
        parent=p.parent
        while not parent.exists():parent=parent.parent
        trusted(parent)
    def put(path,body):
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        with path.open('xb') as f:f.write(body)
        os.chown(path,0,1003);path.chmod(0o440)
    h.ROOT.mkdir(mode=0o700);h.RECORD.mkdir(mode=0o700)
    put(h.RECORD/'INSTALL_INTENT.json',canonical({'source':source,'review':a,'provider_calls':0,'scope':'frozen source preparation, no scientific admission'}))
    for name,body in raw.items():put(h.ROOT/name,body)
    for name,body in inputs.items():put(h.METADATA/name,body)
    for p in review.iterdir():
        h.require(p.is_file() and not p.is_symlink(),'INSTALL_REVIEW_FILE');put(h.RECORD/'review'/p.name,p.read_bytes())
    put(h.CONFIG,canonical(config))
    for name,body in units.items():put(Path('/etc/systemd/system')/name,body)
    h.STATE.mkdir(mode=0o700);os.chown(h.STATE,1003,1003)
    put(h.RECORD/'installed.json',canonical({'source':source,'review_sha256':a['report_sha256'],
          'config_sha256':digest(canonical(config)),'base_source':cfg['source'],'native_source':h.NATIVE_SOURCE}))
    for root in (h.ROOT,h.RECORD,h.CONFIG.parent):
        for p in [root,*[p for p in root.rglob('*') if p.is_dir()]]:
            if p==h.STATE or h.STATE in p.parents:continue
            os.chown(p,0,1003);p.chmod(0o550)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    subprocess.run(['systemctl','enable','--now',h.TIMER],check=True)
    program=f"import importlib.util;from pathlib import Path;p=Path({str(h.ROOT/'tools/item4_source_preparation.py')!r});s=importlib.util.spec_from_file_location('source_installed',p);h=importlib.util.module_from_spec(s);s.loader.exec_module(h);h.verify();print('SOURCE_STATIC_VERIFY_PASS')"
    envarg='RESEARCH_MANUAL_RUNTIME_CONFIG=/etc/research-system-manual-sprint10/releases/'+native.BASE.name+'/runtime.json'
    checked=subprocess.run(['runuser','-u','partho','--','env',envarg,'python3','-s','-B','-c',program],capture_output=True)
    put(h.RECORD/'verify.stdout',checked.stdout);put(h.RECORD/'verify.stderr',checked.stderr)
    h.require(checked.returncode==0 and checked.stdout.strip()==b'SOURCE_STATIC_VERIFY_PASS','INSTALL_POSTCHECK')
    result={'status':'INSTALLED_UNSPENT','provider_calls':0,'model_calls':0,'retention_timer_active':True}
    put(h.RECORD/'COMPLETE.json',canonical(result));return result

if __name__=='__main__':
    import argparse
    os.umask(0o077);p=argparse.ArgumentParser()
    for name in ('packet','review','source','metadata'):p.add_argument('--'+name,required=True)
    a=p.parse_args();print(json.dumps(install(a.packet,a.review,a.source,a.metadata)))
