#!/usr/bin/env python3
"""Reproduce aggregate results from returned private checkpoints; never publish them."""
import argparse
import importlib.util
import json
import math
import re
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('p001',HERE/'run.py'); p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
from orchestrator.publication import validate, inventory


def verify(bundle,private,console):
    policy=json.loads((HERE/'publication.json').read_text()); manifest=validate(bundle,policy)
    if console.is_symlink() or not console.is_file() or not console.stat().st_size:
        raise ValueError('original nonempty console required')
    selected=p.selection(); binding=json.loads((private/'binding.json').read_text())
    if binding['spec_sha256']!=p.sha(HERE/'SPEC.md') or binding['code_sha256']!=p.sha(HERE/'run.py'):
        raise ValueError('returned spec/code binding differs')
    p.verify_decision(HERE.parents[1]/'CAMPAIGN.md',HERE/'SPEC.md',HERE/'investigator_decision.json',HERE/'review.json',HERE/'run.py')
    if binding['review_sha256']!=p.sha(HERE/'review.json'): raise ValueError('review binding mismatch')
    if binding.get('cohort_sha256')!=p.COHORT_SHA or binding.get('member_manifest_blob')!=p.MEMBERS_BLOB or set(binding)!={'spec_sha256','code_sha256','cohort_sha256','member_manifest_blob','review_sha256'}:
        raise ValueError('cohort/manifest binding differs')
    index=json.loads((private/'checkpoint_index.json').read_text())
    checkpoints={f.stem:f for f in (private/'checkpoints').glob('*.json')}
    if set(checkpoints)!=set(selected) or set(index)!=set(selected): raise ValueError('returned cohort differs from frozen eligible cohort')
    rows=[]
    for case,f in checkpoints.items():
        if f.is_symlink() or p.sha(f)!=index[case]: raise ValueError('checkpoint integrity failure')
        row=json.loads(f.read_text()); prediction=private/'predictions'/f'{case}.npy'
        if row['binding']!=binding or prediction.is_symlink() or p.sha(prediction)!=row['prediction_sha256']:
            raise ValueError('prediction/checkpoint binding mismatch')
        m=row['metrics']
        if set(m)!={'dice','absolute_volume_error_ml','signed_volume_error_ml'} or any(type(v) not in (int,float) or not math.isfinite(v) for v in m.values()) or not 0<=m['dice']<=1 or m['absolute_volume_error_ml']!=abs(m['signed_volume_error_ml']):
            raise ValueError('invalid private metric values')
        rows.append(m)
    # Bootstrap order is frozen lexically, not directory enumeration order.
    rows=[json.loads(checkpoints[c].read_text())['metrics'] for c in sorted(checkpoints)]
    summary=json.loads((bundle/'summary.json').read_text())
    for key,value in p.summarize(rows).items():
        if summary.get(key)!=value: raise ValueError('aggregate result not reproduced: '+key)
    if set(summary)!={'status','experiment',*p.summarize(rows)} or summary['status']!='EXPLORATORY_BASELINE_COMPLETE' or summary['experiment']!='P001':
        raise ValueError('unexpected aggregate summary content')
    config=json.loads((bundle/'resolved_config.json').read_text())
    expected={**binding,'baseline':'finite admission Tmax > 6 seconds','seed':20260905,'bootstrap_samples':2000,'input_timing':'admission CT completion','reserved_cases_accessed':0}
    if config!=expected: raise ValueError('resolved configuration differs from reviewed experiment')
    env=json.loads((bundle/'environment.json').read_text())
    import numpy as np
    import nibabel as nib
    if set(env)!={'python','numpy','nibabel'} or env['numpy']!=np.__version__ or env['nibabel']!=nib.__version__ or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',env['python']):
        raise ValueError('environment mismatch: validate using pinned requirements')
    execution=json.loads((bundle/'execution_receipt.json').read_text())
    numeric={'wall_seconds','staging_seconds','analysis_seconds','resumed_cases'}
    unknown={'human_intervention_minutes','cost_usd','usage_tokens','gpu_minutes'}
    if set(execution)!=numeric|unknown|{'compute_method'} or any(execution[k] is not None for k in unknown) or execution['compute_method']!='CPU NumPy; GPU utilization not instrumented':
        raise ValueError('unexpected execution receipt content')
    if any(type(execution[k]) not in (int,float) or not math.isfinite(execution[k]) or execution[k]<0 for k in numeric) or execution['analysis_seconds']>3600 or type(execution['resumed_cases']) is not int or execution['resumed_cases']>99:
        raise ValueError('invalid execution accounting or analysis budget')
    if (bundle/'RESULT_CARD.md').read_text()!=p.result_card(summary): raise ValueError('result card differs from measured aggregate')
    if inventory(bundle)!=manifest: raise ValueError('return bytes changed during semantic validation')
    return {'status':'AGGREGATE_REPRODUCED_FROM_PRIVATE_CHECKPOINTS','file_sha256':manifest,'console_sha256':p.sha(console),
            'limitations':'Does not re-evaluate image geometry/labels or constitute interpretation/ratification'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['bundle','private','console']: ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args(); print(json.dumps(verify(a.bundle,a.private,a.console),indent=2))
