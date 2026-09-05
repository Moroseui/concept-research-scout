#!/usr/bin/env python3
"""P001: fixed admission Tmax prediction, private patient checkpoints, aggregate export."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import zlib

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from orchestrator.campaign import verify_decision, sha

HERE=Path(__file__).resolve().parent
COHORT=ROOT/'probes/046/results/results_v3/per_case_contributions.csv'
MEMBERS=ROOT/'probes/023/results/results_v2/archive_manifest.csv'
COHORT_SHA='aba525122f796618761e6c4d29b664647760e8dff4987932c3ff6ab5456faae9'
MEMBERS_BLOB='edb9a8c2ceb90df214cdd7ec167f0b1e8c858bb2'


def save(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.partial')
    tmp.write_text(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+'\n')
    os.replace(tmp,path)


def selection():
    if sha(COHORT)!=COHORT_SHA: raise ValueError('cohort identity mismatch')
    data=MEMBERS.read_bytes()
    if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=MEMBERS_BLOB:
        raise ValueError('member manifest identity mismatch')
    with COHORT.open() as f: ids=sorted(row['case_id'] for row in csv.DictReader(f))
    if len(ids)!=99 or len(set(ids))!=99: raise ValueError('eligible cohort must be exactly 99 unique IDs')
    with MEMBERS.open() as f: members=list(csv.DictReader(f))
    selected={}
    for case in ids:
        tmax=re.compile(rf'^train/derivatives/{case}/ses-01/perfusion-maps/{case}_ses-01_space-ncct_tmax\.nii\.gz$')
        label=re.compile(rf'^train/derivatives/{case}/ses-02/{case}_ses-02_space-ncct_lesion-msk\.nii\.gz$')
        selected[case]={}
        for kind,pattern in [('tmax',tmax),('label',label)]:
            rows=[row for row in members if pattern.fullmatch(row['path'])]
            if len(rows)!=1: raise ValueError('ambiguous or missing eligible member: '+kind)
            selected[case][kind]=rows[0]
    return selected


def verify_file(root,entry):
    path=root/entry['path']
    if not path.resolve().is_relative_to(root.resolve()) or path.is_symlink():
        raise ValueError('staged input escapes private data root')
    crc=0; size=0; h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):
            size+=len(block); crc=zlib.crc32(block,crc); h.update(block)
    if size!=int(entry['size']) or f'{crc&0xffffffff:08x}'!=entry['crc'].lower():
        raise ValueError('selected input fails size/CRC verification')
    return path,h.hexdigest()


def predict(tmax):
    import numpy as np
    if tmax.ndim!=3 or not np.isfinite(tmax).all(): raise ValueError('Tmax must be finite 3D')
    return tmax>6.0


def metrics(pred,label,voxel_ml):
    import numpy as np
    if label.shape!=pred.shape or label.ndim!=3 or not np.isfinite(label).all() or not np.isin(label,[0,1]).all():
        raise ValueError('label must be finite binary and match prediction geometry')
    if not np.isfinite(voxel_ml) or voxel_ml<=0: raise ValueError('invalid voxel volume')
    label=label.astype(bool); a=int(pred.sum()); b=int(label.sum()); intersection=int((pred&label).sum())
    return {'dice':2*intersection/(a+b) if a+b else 1.0,
            'absolute_volume_error_ml':abs(a-b)*voxel_ml,'signed_volume_error_ml':(a-b)*voxel_ml}


def summarize(rows):
    import numpy as np
    dices=np.array([r['dice'] for r in rows]); rng=np.random.default_rng(20260905)
    boot=dices[rng.integers(0,len(rows),size=(2000,len(rows)))].mean(axis=1)
    return {'n':len(rows),'mean_dice':float(dices.mean()),'median_dice':float(np.median(dices)),
            'mean_dice_bootstrap_percentile_95':np.percentile(boot,[2.5,97.5]).tolist(),
            'mean_absolute_volume_error_ml':float(np.mean([r['absolute_volume_error_ml'] for r in rows])),
            'mean_signed_volume_error_ml':float(np.mean([r['signed_volume_error_ml'] for r in rows]))}


def run(args):
    start=time.monotonic(); selected=selection()
    if args.preflight:
        print(json.dumps({'eligible_cases':len(selected),'selected_members':sum(map(len,selected.values())),
                          'patient_payloads_opened':0,'reserved_cases_selected':0}))
        return
    # No real payload may be touched before exact campaign/spec/code review checks.
    verify_decision(HERE.parents[1]/'CAMPAIGN.md',HERE/'SPEC.md',HERE/'investigator_decision.json',HERE/'review.json',HERE/'run.py')
    import numpy as np
    import nibabel as nib
    if bool(args.archive)==bool(args.data_root): raise ValueError('supply exactly one archive or pre-staged data root')
    out=args.output_dir.resolve(); private=out.with_name(out.name+'.private')
    if args.output_dir.is_symlink() or private.is_symlink(): raise ValueError('output roots must not be symlinks')
    if out.exists() and any(out.iterdir()) and not (private/'binding.json').exists():
        raise ValueError('nonempty destination lacks campaign checkpoint binding')
    out.mkdir(parents=True,exist_ok=True); private.mkdir(parents=True,exist_ok=True)
    binding={'spec_sha256':sha(HERE/'SPEC.md'),'code_sha256':sha(HERE/'run.py'),'cohort_sha256':COHORT_SHA,
             'member_manifest_blob':MEMBERS_BLOB,'review_sha256':sha(HERE/'review.json')}
    state=private/'binding.json'
    if state.exists() and json.loads(state.read_text())!=binding: raise ValueError('checkpoint binding stale; use a new output path')
    save(state,binding)
    staging_start=time.monotonic()
    data=args.data_root.resolve() if args.data_root else private/'staged'
    if args.archive:
        if data.exists():
            # Previous extraction is retained and must verify member-by-member below.
            print('Reusing private staging; validating every selected member')
        else:
            h=hashlib.md5(); size=0
            with args.archive.open('rb') as f:
                for b in iter(lambda:f.read(8<<20),b''): h.update(b); size+=len(b)
            if size!=99014629647 or h.hexdigest()!='36ae28b9a17f7340b8bbef62b595cb57': raise ValueError('archive identity mismatch')
            data.mkdir()
            members=[e['path'] for pair in selected.values() for e in pair.values()]
            subprocess.run(['7z','x',str(args.archive),'-o'+str(data),'-y',*members],check=True)
    paths={}
    for case,pair in selected.items(): paths[case]={kind:verify_file(data,e) for kind,e in pair.items()}
    staging_seconds=time.monotonic()-staging_start
    save(private/'selected_inputs.json',{case:{kind:{'path':str(v[0]),'sha256':v[1]} for kind,v in pair.items()} for case,pair in paths.items()})
    index_path=private/'checkpoint_index.json'
    checkpoint_index=json.loads(index_path.read_text()) if index_path.exists() else {}
    analysis_start=time.monotonic(); all_rows=[]; resumed=0
    for index,(case,pair) in enumerate(paths.items()):
        if time.monotonic()-analysis_start>3600: raise TimeoutError('60-minute analysis cap reached; retain checkpoints')
        checkpoint=private/'checkpoints'/f'{case}.json'; prediction=private/'predictions'/f'{case}.npy'
        inputs={k:v[1] for k,v in pair.items()}
        if checkpoint.exists():
            if checkpoint_index.get(case)!=sha(checkpoint): raise ValueError('checkpoint metric bytes changed')
            row=json.loads(checkpoint.read_text())
            if row['binding']!=binding or row['inputs']!=inputs or not prediction.is_file() or sha(prediction)!=row['prediction_sha256']:
                raise ValueError('checkpoint input/prediction identity changed')
            all_rows.append(row['metrics']); resumed+=1; continue
        image=nib.load(str(pair['tmax'][0])); arr=np.asarray(image.dataobj,dtype=np.float32)
        pred=predict(arr)
        prediction.parent.mkdir(parents=True,exist_ok=True)
        np.save(prediction,pred,allow_pickle=False)  # persist before opening label
        label_image=nib.load(str(pair['label'][0]))
        if image.shape!=label_image.shape or not np.allclose(image.affine,label_image.affine,atol=1e-5,rtol=0):
            raise ValueError('geometry mismatch; amendment required, no implicit resampling')
        voxel_ml=abs(float(np.linalg.det(image.affine[:3,:3])))/1000.0
        row=metrics(pred,np.asarray(label_image.dataobj),voxel_ml)
        save(checkpoint,{'binding':binding,'inputs':inputs,'prediction_sha256':sha(prediction),'metrics':row})
        checkpoint_index[case]=sha(checkpoint); save(index_path,checkpoint_index)
        all_rows.append(row); print(f'Evaluated {index+1}/99')
    if len(all_rows)!=99: raise ValueError('incomplete cohort; no additional exclusions permitted')
    summary={'status':'EXPLORATORY_BASELINE_COMPLETE','experiment':'P001',**summarize(all_rows)}
    save(out/'summary.json',summary)
    save(out/'resolved_config.json',{**binding,'baseline':'finite admission Tmax > 6 seconds','seed':20260905,'bootstrap_samples':2000,'input_timing':'admission CT completion','reserved_cases_accessed':0})
    save(out/'environment.json',{'python':platform.python_version(),'numpy':np.__version__,'nibabel':nib.__version__})
    save(out/'execution_receipt.json',{'wall_seconds':time.monotonic()-start,'staging_seconds':staging_seconds,'analysis_seconds':time.monotonic()-analysis_start,'resumed_cases':resumed,'human_intervention_minutes':None,'cost_usd':None,'usage_tokens':None,'gpu_minutes':0})
    lo,hi=summary['mean_dice_bootstrap_percentile_95']
    (out/'RESULT_CARD.md').write_text(f'''# P001 — exploratory baseline result

Question: Does admission Tmax > 6 s predict released follow-up infarct?
Baseline: fixed hypoperfusion threshold; no fitting. Change: none (first baseline).
Data: frozen eligible 99 development patients. Input timing: admission CT only.
Result: mean patient Dice {summary['mean_dice']:.4f}; patient-bootstrap 95% range
[{lo:.4f}, {hi:.4f}]. Mean absolute volume error {summary['mean_absolute_volume_error_ml']:.2f} mL.
Limitations: reused development outcomes, selected cohort, unmodeled treatment,
registration and units; this interval is not external or clinical validation.
Artifacts: summary.json, resolved_config.json, execution_receipt.json; per-case
checkpoints and predictions retained privately alongside this aggregate bundle.
Next decision: inspect baseline failures and volume bias, then register at most
one follow-up at a time under the two-comparison campaign cap.
''')
    print('P001 complete; retain private checkpoints and original console for audit')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--preflight',action='store_true'); ap.add_argument('--archive',type=Path)
    ap.add_argument('--data-root',type=Path); ap.add_argument('--output-dir',type=Path,default=Path('/tmp/P001'))
    args=ap.parse_args()
    try: run(args)
    except Exception as e:
        private=args.output_dir.with_name(args.output_dir.name+'.private')
        failure_dir=private/'failed_attempts'
        try:
            save(failure_dir/(str(time.time_ns())+'.json'),{'status':'INVALID_OR_BLOCKED','exception_type':type(e).__name__,'scientific_result':None,'human_intervention_minutes':None,'cost_usd':None})
            card=args.output_dir/'RESULT_CARD.md'
            if not card.exists():
                card.parent.mkdir(parents=True,exist_ok=True)
                card.write_text('# P001 — failed or blocked attempt\n\nQuestion: admission Tmax baseline for follow-up infarct. Baseline: fixed >6 s.\nNo valid scientific result or uncertainty is available. Preserve the original\nsibling console and private failed-attempt receipt; inspect the failure before\na retry. No negative finding is inferred.\n')
        except OSError:
            pass
        print('P001 FAILED:',type(e).__name__,str(e),file=sys.stderr)
        raise
