"""One linked final implementation review using the approved terminal classifier.

Original bootstrap remains consumed. Its source and genuine APPROVE are checked
before reusing only the exact terminal classification for this new request.
Normal reviewer, daily admission, accounting, isolation and other refusals stay.
"""
import hashlib,importlib.util,json,os,sys
from pathlib import Path
CHANGE='item4-author24-delivery-20261010'
CP=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006')/CHANGE
ENGINE=Path('/opt/research-system/autonomy-review/d08b91bdc1d0')
PRIOR=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006/item4-sender-recovery-20261010/packet/source')
PACKET='a27b9e0bdf19ec037711ff079725ee83afe02e4d2b95fd751ac1ab9a7e81e04d'
APPROVAL='a54ef800461b974db328d18fba65e4d6d819044a3a003d9699a59603b0710139'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('FINAL_SENDER_REVIEW_'+why)
def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        s=p.lstat();require(not p.is_symlink() and s.st_uid==0 and not s.st_mode&0o022,'TRUSTED_SOURCE')
    return path

def classifier(ar):
    folder=Path('/var/lib/research-system-autonomy/reviews')/PACKET
    approved=ar.verify_result(folder)
    require(approved['verdict']=='APPROVE' and approved['change_id']=='item4-sender-recovery-20261010' and approved['source_sha']=='41b93574a0ad0fb546745095ff0078debd6f133d' and approved['report_sha256']==APPROVAL,'PRIOR_GENUINE_APPROVE')
    manifest=json.loads(ar.regular(folder/'packet-manifest.json').read_bytes())
    for name in ('tools/review_sender_recovery_once.py','docs/ITEM4_AUTHOR22_TERMINAL_PRIVATE.json'):
        require(sha(trusted(PRIOR/name).read_bytes())==manifest['source_files'][name],'EXACT_APPROVED_CLASSIFIER')
    spec=importlib.util.spec_from_file_location('_approved_terminal_classifier',PRIOR/'tools/review_sender_recovery_once.py')
    boot=importlib.util.module_from_spec(spec);spec.loader.exec_module(boot)
    # New linked candidate, separately counted. Do not reuse the original request,
    # its one-use dispatch or any prior scientific grant.
    boot.CHANGE=CHANGE
    binding=json.loads(trusted(PRIOR/boot.DOC).read_bytes())
    return boot,binding

def main():
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==CP/'packet/source/tools/review_sender_continuation_once.py','OWNER_PATH')
    meta=json.loads(trusted(CP/'BOOTSTRAP_BINDING.json').read_bytes())
    require(meta['change']==CHANGE and meta['wrapper_sha256']==sha(Path(__file__).read_bytes()),'WRAPPER')
    sys.path.insert(0,str(ENGINE))
    from orchestrator import autonomy_review as ar,autonomy_review_runner as runner,administrative_terminal as terminal,private_records as pr
    packet=trusted(meta['packet_path']);m=ar.verify_packet(packet)
    require(ar.sha(ar.canonical(m))==meta['packet'] and m['change_id']==CHANGE and m['source_sha']==meta['source'] and m['round']==1,'EXACT_NEW_REQUEST')
    boot,binding=classifier(ar)
    original=terminal.administrative_exceptions
    terminal.administrative_exceptions=lambda db,proof_root=None:boot.exceptions(db,proof_root,binding,terminal.verify,lambda path:pr.check(path).read_bytes())
    try:
        result=runner.run(packet,Path('/var/lib/research-system-autonomy/reviews'));print(json.dumps(result,sort_keys=True))
        return 0 if result['status']=='COMPLETE' else 2
    finally:terminal.administrative_exceptions=original

if __name__=='__main__':
    os.umask(0o077);require(len(sys.argv)==1,'NO_ARGUMENTS');raise SystemExit(main())
