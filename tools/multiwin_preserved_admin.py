"""One administrative implementation review, round1; all originals preserved.
Existing historical classifiers remain; one exact terminal proof uses standing repair-review authority.
"""
from pathlib import Path
import os,sys,json,hashlib,importlib.util,runpy,sqlite3
CHANGE='multiwin-output-boundary-20261013'
CP=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006/multiwin-output-boundary-20261013')
INSTALLED=Path('/opt/research-system/manual-repair-helpers/native-review-admission-20261011')
PRIOR=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006/native-review-admission-20261011/accepted-current-source-review')
ENGINE=Path('/opt/research-system/autonomy-review/d08b91bdc1d0')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def trusted(path):
 p=Path(path)
 for q in (p,*p.parents):
  st=q.lstat();assert not q.is_symlink() and st.st_uid==0 and not st.st_mode&0o022
 return p
def load(name,path):
 s=importlib.util.spec_from_file_location(name,trusted(path));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
assert os.getuid()==os.getgid()==1003 and sys.flags.no_user_site and Path(__file__).resolve()==CP/'invoke_review_with_installed_cap.py'
meta=json.loads(trusted(CP/'BOOTSTRAP_BINDING.json').read_bytes())
assert meta['change']==CHANGE and len(meta['source'])==40
SOURCE=meta['source']
sys.path.insert(0,str(ENGINE))
from orchestrator import autonomy_review as ar,administrative_terminal as terminal
manifest=ar.verify_packet(trusted(meta['packet_path']))
assert ar.sha(ar.canonical(manifest))==meta['packet'] and manifest['change_id']==CHANGE and manifest['source_sha']==SOURCE and manifest['round']==1
prior=ar.verify_result(trusted(PRIOR))
assert prior['verdict']=='APPROVE' and prior['source_sha']=='9e2816b322518f5d5843bd3656b078902818a589' and prior['report_sha256']=='001ea72281ccb25b0eaf0d5d0881966d2b46ae68c036f661fb7f621d53a6b48c'
assert json.loads(trusted(PRIOR/'report.md').read_bytes())['findings']==[]
pins=json.loads(trusted(PRIOR/'packet-manifest.json').read_bytes())['source_files']
for name in ('tools/review_colab_final_terminal_once.py','orchestrator/colab_author_terminal.py','docs/COLAB_FINAL_AUTHOR_TERMINAL_PRIVATE.json','docs/MECHANICAL_REPAIR_REVIEW_STANDING_AUTHORITY_20261007.txt'):
 assert sha(trusted(INSTALLED/name).read_bytes())==pins[name]
b=load('_approved_admin_wrapper',INSTALLED/'tools/review_colab_final_terminal_once.py')
assert meta['wrapper_sha256']==sha(trusted(INSTALLED/'tools/review_colab_final_terminal_once.py').read_bytes())
assert sha(trusted(INSTALLED/'docs/MECHANICAL_REPAIR_REVIEW_STANDING_AUTHORITY_20261007.txt').read_bytes())==b.AUTHORITY
assert sha(trusted(b.EXISTING).read_bytes())==b.EXISTING_SHA
# Use the installed, independently approved continuation proof. The candidate
# terminal classifier is always the previously approved one.
drive=Path('/opt/research-system/manual-repair-helpers/colab-drive-in-place-20261011')
rt=load('_installed_drive_authority',drive/'tools/colab_intake_identity_runtime.py')
authority=rt.authority()
assert authority['source_sha']=='e0394b8b8fd94a2d9feca3ffb88c917aed55936b' and authority['report_sha256']=='6d5689352510f3dda16edf084da1901c8121deec88af11a0b204685fe5e0d34d'
proof=load('_installed_drive_terminal',drive/'orchestrator/colab_author_terminal.py')
continuation=load('_installed_drive_history',drive/'orchestrator/colab_drive_in_place.py')
freeze=continuation.frozen();binding=proof.frozen()
proof._CONTINUATION=lambda value:premodel.historical_read(continuation.BORROWED[str(Path(freeze['config']['batch_ledger'])/'jobs.sqlite')],value,freeze,historical_value)

# Route the unchanged one-admission check to this sole corrective request.
b.CHANGE=CHANGE
# Reuse independently approved installed history proof, with no candidate code.
approved_root=Path('/opt/research-system/manual-repair-helpers/colab-simple-admission-20261012')
approved_folder=Path('/var/lib/research-system-manual-sprint10-deployment/colab-simple-admission-20261012/review')
approved=ar.verify_result(trusted(approved_folder))
assert approved['source_sha']=='0770e23ac2bf257edc819b2e3f6e2a2693e12095' and approved['report_sha256']=='93871cd5a9ccae13b9d68f5cd01457cff20b80aad3c55d457cbaa30777c7210d' and approved['verdict']=='APPROVE'
approved_pins=json.loads(trusted(approved_folder/'packet-manifest.json').read_bytes())['source_files']
for name in ('orchestrator/colab_premodel_terminal.py','docs/COLAB_ADMISSION_FAILURE_PRIVATE.json','docs/COLAB_HISTORICAL_EIGHT_PRIVATE.json'):
 assert sha(trusted(approved_root/name).read_bytes())==approved_pins[name]
premodel=load('_approved_terminal_history',approved_root/'orchestrator/colab_premodel_terminal.py')
premodel_value=premodel.document(approved_root/'docs/COLAB_ADMISSION_FAILURE_PRIVATE.json')
historical_value=premodel.historical_document(approved_root/'docs/COLAB_HISTORICAL_EIGHT_PRIVATE.json')
previous=terminal.verify;saved=terminal.administrative_exceptions;old_argv=sys.argv
terminal.verify=b.exact_adapter(previous,proof,binding)
used=[]
def current_owner_read(db,proof_root=None):
    assert db.in_transaction and not used
    rows=db.execute('SELECT id,status,receipt FROM autonomy_calls WHERE change_id=? ORDER BY round',(CHANGE,)).fetchall()
    assert not rows and manifest['predecessor'] is None
    assert not db.execute('SELECT 1 FROM autonomy_calls WHERE id=?',(meta['packet'],)).fetchone()
    used.append(True)
    # Read the same live admission transaction, not a journal-ignoring snapshot.
    key=str(Path(freeze['config']['batch_ledger'])/'jobs.sqlite')
    assert key not in continuation.BORROWED
    local_key=str(Path(freeze['lane'])/'jobs.sqlite')
    assert local_key not in continuation.BORROWED
    local=sqlite3.connect(Path(local_key).as_uri()+'?mode=ro',uri=True)
    local.row_factory=sqlite3.Row
    local.execute('BEGIN')
    continuation.BORROWED[key]=db
    continuation.BORROWED[local_key]=local
    try:
        # Standing one bounded administrative review while a mechanical failure
        # blocks its own repair. Candidate code is only a read-only terminal proof,
        # never a scientific grant or installation authority.
        from orchestrator import private_records as pr
        import subprocess
        root=CP/'packet/source'
        for name in ('orchestrator/multiwin_preserved_output.py','docs/MULTIWIN_OUTPUT_BOUNDARY_PRIVATE.json','tools/multiwin_preserved_admin.py'):
            assert sha(trusted(root/name).read_bytes())==manifest['source_files'][name]
        assert sha(Path(__file__).read_bytes())==manifest['source_files']['tools/multiwin_preserved_admin.py']
        candidate=load('_one_admin_preserved_terminal',root/'orchestrator/multiwin_preserved_output.py')
        frozen=candidate.document(root)
        def stopped(unit):
            assert unit=='research-multiwin-returned-provenance-20261013.service'
            v=dict(l.split('=',1)for l in subprocess.check_output(['systemctl','show',unit,'-p','MainPID','-p','ActiveState','-p','ControlGroup','-p','ExecMainStatus'],text=True).splitlines())
            return v=={'MainPID':'0','ActiveState':'inactive','ControlGroup':'','ExecMainStatus':'0'}
        return candidate.administrative(db,frozen,lambda p:pr.check(p).read_bytes(),
            lambda row:terminal.verify(row,None if proof_root is None else Path(proof_root)/row['id']),stopped,CHANGE)
    finally:
        continuation.BORROWED.pop(key);continuation.BORROWED.pop(local_key)
        local.rollback();local.close()
terminal.administrative_exceptions=current_owner_read  # Exact first request, one in-transaction qualification.

# Use unchanged reviewed native entry and timing transport, selecting only the
# independently approved installed 12October daily policy at its old bind point.
def run_with_installed_cap():
    ORIGINAL=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006/direction-transport-overhead-20261011/invoke_registered_administrative.py')
    assert sha(trusted(ORIGINAL).read_bytes())=='7e8a1f8c3e16397443f2db0eef8057f2f1be5538503faa3b15e6cedf07448502'
    entry=load('_existing_admin_operator',ORIGINAL)
    entry.authenticate(meta['packet'])
    root=Path('/opt/research-system/manual-repair-helpers/colab-intake-source-alignment-20261011')
    previous=entry.load('_existing_transport_authority',root/'tools/colab_intake_identity_runtime.py');approved=previous.authority()
    assert approved['change_id']=='colab-timing-transport-repair-20261011' and approved['source_sha']=='4a05c64af90af15078e43e31abc9bd13d063160e' and approved['report_sha256']=='c64df8e27dc86e96a15a4630b0aec5812ec44ddb32124a09dfda0909d7c584ca'
    helper=entry.trusted(root/'tools/reviewer_connection_timing.py')
    assert entry.sha(helper.read_bytes())=='853798d1e9dc61b79fbc7cdca5d48dfa0f03a9d41b28f217b90124fe033b555e'
    transport=entry.load('_existing_transport',helper)
    from orchestrator import manual_runtime
    restore=transport.bind(manual_runtime)
    previous_load=entry.load
    selected=[]
    def installed_load(name,path):
        if name!='_installed_reviewed_daily_cap':return previous_load(name,path)
        assert Path(path)==entry.CAP/'tools/temporary_daily_cap.py' and not selected
        current=previous_load('_installed_reviewed_tonight_cap',
            Path('/opt/research-system/manual-repair-helpers/colab-tonight-cap-20261012/tools/colab_tonight_cap.py'))
        verdict=current.verified()
        assert verdict['source_sha']=='fe3b52ce4cf047f3c024df6b68f2456b241d6ab3' and verdict['report_sha256']=='8547040a9626ebac15a5dc6fdd3b17c2967eb46f2017eff48e9bcda0126abb1d'
        selected.append(True)
        class InstalledPolicy:
            @staticmethod
            def verified():return current.verified()
            @staticmethod
            def bind(kind):
                assert kind=='administrative'
                return current.bind_administrative()
        return InstalledPolicy
    entry.load=installed_load
    try:
        result=entry.main(['--request',meta['packet']])
        assert selected==[True]
        return result
    finally:entry.load=previous_load;restore()
try:result=run_with_installed_cap()
finally:terminal.verify=previous;terminal.administrative_exceptions=saved;sys.argv=old_argv
raise SystemExit(result)
