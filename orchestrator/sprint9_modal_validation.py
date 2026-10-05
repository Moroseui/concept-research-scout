"""Predeclared M3 smoke comparison; no training, bootstrap or tolerance tuning."""
import csv
import json
import math
from pathlib import Path
from orchestrator import private_records
from orchestrator.manual_executor import digest,inventory
from orchestrator.modal_executor import canonical

BASELINE={'U_base_raw':0.14332621679029806,'U_base_smoothed':0.1574551448013633}
ABSOLUTE_TOLERANCE=0.005
BASELINE_TABLE_SHA256='700e947d93df402c89a79e5158bce2f14ddb8006a9c9a288596a602df13cbf75'


def validate(folder,binding,smoke):
    folder=Path(folder);private_records.check_tree(folder)
    files=inventory(folder)
    if set(files)!=set(binding['outputs']):raise ValueError('SMOKE_RETURN_MEMBER_SET')
    receipt=json.loads((folder/'execution.json').read_text())
    if (receipt['run_id']!=binding['run_id'] or receipt['input_contract']!=binding['input_contract'] or
        receipt['versions']!=smoke['versions'] or receipt['arm']!='U_base' or receipt['shuffle']!=101 or
        receipt['fold']!=0 or receipt['training_seed']!=1 or receipt['maximum_epochs']!=2 or receipt['held_count']!=20):
        raise ValueError('SMOKE_EXECUTION_BINDING')
    rows=list(csv.DictReader((folder/'folds/unet_U_base_s101_f0_t1.csv').open()))
    expected={(recipe,case) for recipe in BASELINE for case in smoke['partitions']['held']}
    actual=[(row['recipe'],row['case']) for row in rows]
    if len(actual)!=len(expected) or set(actual)!=expected:raise ValueError('SMOKE_RESULT_COHORT')
    values={name:[] for name in BASELINE}
    for row in rows:
        if row['fingerprint']!=binding['run_id'] or (row['shuffle'],row['fold'],row['train_seed'])!=('101','0','1'):
            raise ValueError('SMOKE_RESULT_RUN_BINDING')
        counts=[int(row[k]) for k in ('tp','fp','fn')]
        if min(counts)<0:raise ValueError('SMOKE_NEGATIVE_COUNTS')
        tp,fp,fn=counts;denominator=2*tp+fp+fn;expected_dice=2*tp/denominator if denominator else 1.0
        dsc=float(row['dice']);f1=float(row['f1_voxel'])
        if not all(math.isfinite(x) and 0<=x<=1 for x in (dsc,f1)) or abs(dsc-expected_dice)>1e-12 or abs(f1-dsc)>1e-12:
            raise ValueError('SMOKE_DICE_CONTRACT')
        values[row['recipe']].append(dsc)
    means={name:sum(v)/len(v) for name,v in values.items()}
    summary=json.loads((folder/'summary.json').read_text())
    for recorded in (receipt['mean_dice'],summary['mean_dice']):
        if set(recorded)!=set(means) or any(not math.isfinite(recorded[k]) or abs(recorded[k]-means[k])>1e-12 for k in means):raise ValueError('SMOKE_SUMMARY_NOT_FROM_TABLE')
    differences={name:means[name]-BASELINE[name] for name in means}
    fits=all(abs(v)<=ABSOLUTE_TOLERANCE for v in differences.values())
    # Results outside tolerance are preserved as a valid observed failure, never
    # labelled reproduced. The driver must block acceptance, not retry training.
    return {'status':'VALID' if fits else 'REPRODUCTION_FAILED','run_id':binding['run_id'],
            'scope':'one development U_base fold, two epochs; not a new efficacy result',
            'baseline_table_sha256':BASELINE_TABLE_SHA256,'absolute_mean_dice_tolerance':ABSOLUTE_TOLERANCE,
            'expected_mean_dice':BASELINE,'observed_mean_dice':means,'difference':differences,
            'patients':20,'rows':40,'input_contract_sha256':digest(canonical(binding['input_contract'])),
            'files':{name:{'sha256':identity,'bytes':(folder/name).stat().st_size} for name,identity in files.items()}}
