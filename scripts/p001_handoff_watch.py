"""Serial, bounded monitoring and dispatch using independently reviewed adapters."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from orchestrator import colab_acquire as acquisition
from orchestrator import colab_patient as patient
from orchestrator.colab_worker import private_dir, write_private

ROOT=patient.ROOT
FILES=['scripts/p001_handoff_watch.py','tests/test_p001_handoff_watch.py']


def approval():
    prefix=ROOT/'docs/isles-pilot/reviews/p001-handoff-watch'
    e=json.loads(Path(str(prefix)+'.execution.json').read_text())
    p=Path(str(prefix)+'.response.json');r=json.loads(p.read_text());v=r.get('structured_output',{})
    if (e['returncode'] or r.get('is_error') or r.get('subtype')!='success' or
        v.get('verdict')!='APPROVE' or v.get('scope')!='p001-handoff-watch' or
        v.get('reviewed_commit')!=e['reviewed_commit'] or
        e['response_sha256']!=hashlib.sha256(p.read_bytes()).hexdigest() or
        'claude-fable-5' not in e.get('assistant_message_models',[])):
        raise ValueError('completed handoff review required')
    for name in FILES:
        if e['input_file_sha256'].get(name)!=hashlib.sha256((ROOT/name).read_bytes()).hexdigest():
            raise ValueError('handoff source binding mismatch')
    acquisition.reviewed();patient.require_patient_review()


def follow(poll_input, dispatch, poll_result, record, pause):
    # No retries of mutations; polls are read-only. Poll counts bound observation.
    for _ in range(60):
        result=poll_input();record('acquisition',result)
        if result.get('status')!='COMPLETE':return 'ACQUISITION_WORKER_BLOCKED'
        status=result.get('remote',{}).get('status')
        if status=='VALIDATED':break
        if status not in ['STARTING','RUNNING']:return 'ACQUISITION_STOPPED'
        pause()
    else:return 'ACQUISITION_OBSERVATION_LIMIT'
    result=dispatch();record('dispatch',result)
    if result.get('status')!='COMPLETE' or result.get('job_status')!='DISPATCHED_NOT_YET_VALIDATED':
        return 'DISPATCH_BLOCKED'
    for _ in range(60):
        result=poll_result();record('patient',result)
        if result.get('status')!='COMPLETE':return 'PATIENT_WORKER_BLOCKED'
        status=result.get('job_status')
        if status=='VALIDATED':return 'NEEDS_PRIVATE_RETURN_TRANSFER'
        if status not in ['STARTING','RUNNING']:return 'PATIENT_STOPPED'
        pause()
    return 'PATIENT_OBSERVATION_LIMIT'


def main(destination):
    approval()
    directory=private_dir(destination)  # exclusive destination prevents accidental controller reruns
    counter=0
    def attempt():
        nonlocal counter
        counter+=1
        return directory/('attempt-'+str(counter))
    def record(stage,result):
        write_private(directory/('event-'+str(counter)+'.json'),json.dumps({'stage':stage,'result':result}))
    def pause():
        for _ in range(5):time.sleep(60)
    def dispatch():
        approval()  # Recheck every approval immediately before the only patient mutation.
        return patient.worker(patient.execution_packet('/content/isles-p001-input-16813698/train.7z'),attempt())
    outcome=follow(lambda:acquisition.run('poll',attempt()),dispatch,
        lambda:patient.worker({'task':'poll_p001','cells':[patient.CPU_CELL,patient.poll_cell()]},attempt()),record,pause)
    write_private(directory/'outcome.json',json.dumps({'status':outcome}))
    print(json.dumps({'status':outcome}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--private-dir',type=Path,required=True)
    main(parser.parse_args().private_dir)
