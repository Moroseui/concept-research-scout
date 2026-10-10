"""Reuse the approved bounded host operation for one preparation transition."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

CHANGE='preparation-and-cap-repair-20261010'
LINKED_REVIEW_CHANGE=CHANGE+'-format2'
LINK_DOCUMENT='docs/PREPARATION_CAP_CALL52_MECHANICAL_PRIVATE.json'
LINK_SHA='e0a382926188ef464ff50fffcc3edaa58575fbfcb0dfc0d83029a7683ca7b4b4'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
OLD=Path('/opt/research-system/manual-repair-helpers/item4-author24-delivery-20261010/tools/item4_response_host_operation.py')
OLD_REVIEW=Path('/var/lib/research-system-manual-sprint10-deployment/item4-author24-delivery-20261010/review')
HOST_PIN='a180f1ca903ca0a82566016d58425a4411dcfbfc512568afe57138b2c3329ade'
LANES=('aggregate_analysis','colab_preparation')

def review_change(approval,manifest,source):
    if approval.get('change_id')==CHANGE:return True
    return (approval.get('change_id')==LINKED_REVIEW_CHANGE
        and manifest.get('source_files',{}).get(LINK_DOCUMENT)==LINK_SHA
        and sha(trusted(Path(source)/LINK_DOCUMENT).read_bytes())==LINK_SHA)


def require(ok,why):
    if not ok:raise ValueError('PREPARATION_HOST_'+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def trusted(path):
    p=Path(path)
    for q in [p,*p.parents]:
        s=q.lstat();require(not q.is_symlink() and s.st_uid==0 and not s.st_mode&0o022,'TRUSTED_PATH')
    return p

def transition_identity(run,payload,calls):
    require(isinstance(run,str) and isinstance(payload,str) and isinstance(calls,list),'STATE_SHAPE')
    return sha(json.dumps({'run':run,'payload':payload,'calls':calls},sort_keys=True,separators=(',',':')).encode())

STATE_READER=r"""from pathlib import Path
import json,os,sqlite3,hashlib,sys
assert os.getuid()==os.getgid()==1003
lane=Path(sys.argv[1]);config=json.loads((lane/'lane.json').read_bytes())
with sqlite3.connect((lane/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as db:
 payload=db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
 calls=[list(r) for r in db.execute('SELECT id,stage,attempt,status FROM manual_calls ORDER BY rowid')]
 state=json.loads(payload)
 assert len(calls)<=8 and not any(r[3]=='RUNNING' for r in calls)
 assert state['phase'] in ('run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review','MODEL_RUNNING','COMMIT_SPEC','UPDATE_STATE','REPORT')
with sqlite3.connect('file:/var/lib/research-system-autonomy/reviews/jobs.sqlite?mode=ro',uri=True) as db:
 assert not db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone()
value={'run':config['run_id'],'payload':payload,'calls':calls}
identity=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
print(json.dumps({'transition':identity,'run_id':config['run_id'],'phase':state['phase'],'local_calls':len(calls),'source':config['source'],'review_sha256':config['engine_review']['sha256']}))
"""

def connect(key,transition):
    require(os.getuid()==0 and sys.flags.no_user_site,'ROOT_ISOLATED_REQUIRED')
    require(key in LANES and re.fullmatch('[0-9a-f]{64}',transition or '') is not None,'ACTION_BINDING')
    require(sha(trusted(OLD).read_bytes())==HOST_PIN,'ORIGINAL_HOST_SOURCE')
    spec=importlib.util.spec_from_file_location('_unchanged_preparation_host',OLD)
    host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
    original_frozen,old_approval=host.authority(OLD_REVIEW)
    from orchestrator.autonomy_review import verify_result
    approved=verify_result(trusted(RECORD/'review'))
    manifest=json.loads(trusted(RECORD/'review/packet-manifest.json').read_bytes())
    require(approved['verdict']=='APPROVE' and review_change(approved,manifest,ROOT),'GENUINE_APPROVAL')
    installed=json.loads(trusted(RECORD/'installed.json').read_bytes())
    require(installed['root']==str(ROOT) and installed['source']==approved['source_sha']
        and installed['review_sha256']==approved['report_sha256'],'INSTALL_BINDING')
    complete=json.loads(trusted(RECORD/'COMPLETE.json').read_bytes())
    require(complete=={'status':'INSTALLED_HELD','source':approved['source_sha'],'scientific_calls':0,'provider_calls':0},'SERVICE_VERIFICATION_REQUIRED')
    require(Path(__file__).resolve()==ROOT/'tools/preparation_host_operation.py','EXECUTED_PATH')
    for name,pin in manifest['source_files'].items():
        require(installed['files'].get(name)==pin==sha(trusted(ROOT/name).read_bytes()),'REVIEWED_SOURCE')
    scope_raw=trusted(RECORD/'preparation-interleaving.json').read_bytes();scope=json.loads(scope_raw)
    require(sha(scope_raw)==manifest['files']['evidence/preparation-interleaving.json'] and scope['source_sha']==approved['source_sha'],'REVIEWED_SCOPE')
    lane=scope['lanes'][key]
    original_frozen['hashes']={**original_frozen['hashes'],**installed['units'],
        **{str(ROOT/name):pin for name,pin in manifest['source_files'].items()},
        str(RECORD/'preparation-interleaving.json'):sha(scope_raw)}
    host.hashes(original_frozen)
    host.UNIT='research-'+CHANGE+'-'+key+'.service'
    host.OPERATION_ROOT=RECORD/'operations'/key/transition
    # Keep original selected-lane hook, policy checks, pulse ceilings, invocation
    # identity, stale-proof refusal and safe_stop. New lane is separately bound.
    def starting_state(frozen,approval):
        value=json.loads(host.command(['runuser','-u','partho','--','python3','-s','-B','-c',STATE_READER,lane['state']]))
        require(value['transition']==transition and value['run_id']==lane['run_id']
            and value['source']==approved['source_sha'] and value['review_sha256']==approved['report_sha256'],'CURRENT_LANE_STATE')
        return value
    host.starting_state=starting_state
    host.authority=lambda review:(original_frozen,approved)
    return host

def status(key):
    require(os.getuid()==0 and sys.flags.no_user_site and key in LANES,'STATUS_OWNER_LANE')
    scope=json.loads(trusted(RECORD/'preparation-interleaving.json').read_bytes())
    import subprocess
    raw=subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',STATE_READER,scope['lanes'][key]['state']],text=True)
    value=json.loads(raw)
    connect(key,value['transition'])
    return value

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('action',choices=['status','start','pulse']);p.add_argument('--lane',choices=LANES,required=True);p.add_argument('--transition')
    a=p.parse_args(argv)
    if a.action=='status':
        require(a.transition is None,'STATUS_NO_TRANSITION');print(json.dumps(status(a.lane),sort_keys=True));return
    host=connect(a.lane,a.transition)
    # Fixed reviewed record roots only. Never remove/reuse a failed operation.
    for path in [RECORD/'operations',RECORD/'operations'/a.lane,host.OPERATION_ROOT]:
        if not path.exists():trusted(path.parent);path.mkdir(mode=0o700);path.chmod(0o700)
        trusted(path)
    prior=sys.argv
    try:
        sys.argv=[str(__file__),a.action,'--stage','author','--review',str(RECORD/'review')]
        return host.main()
    finally:sys.argv=prior

if __name__=='__main__':
    os.umask(0o077);main()
