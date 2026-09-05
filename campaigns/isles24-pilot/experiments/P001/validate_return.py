#!/usr/bin/env python3
"""Reproduce aggregate results from returned private checkpoints; never publish them."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('p001',HERE/'run.py'); p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
from orchestrator.publication import validate


def verify(bundle,private,console):
    policy=json.loads((HERE/'publication.json').read_text()); manifest=validate(bundle,policy)
    if console.is_symlink() or not console.is_file() or not console.stat().st_size:
        raise ValueError('original nonempty console required')
    selected=p.selection(); binding=json.loads((private/'binding.json').read_text())
    if binding['spec_sha256']!=p.sha(HERE/'SPEC.md') or binding['code_sha256']!=p.sha(HERE/'run.py'):
        raise ValueError('returned spec/code binding differs')
    p.verify_decision(HERE.parents[1]/'CAMPAIGN.md',HERE/'SPEC.md',HERE/'investigator_decision.json',HERE/'review.json',HERE/'run.py')
    if binding['review_sha256']!=p.sha(HERE/'review.json'): raise ValueError('review binding mismatch')
    index=json.loads((private/'checkpoint_index.json').read_text())
    checkpoints={f.stem:f for f in (private/'checkpoints').glob('*.json')}
    if set(checkpoints)!=set(selected) or set(index)!=set(selected): raise ValueError('returned cohort differs from frozen eligible cohort')
    rows=[]
    for case,f in checkpoints.items():
        if f.is_symlink() or p.sha(f)!=index[case]: raise ValueError('checkpoint integrity failure')
        row=json.loads(f.read_text()); prediction=private/'predictions'/f'{case}.npy'
        if row['binding']!=binding or prediction.is_symlink() or p.sha(prediction)!=row['prediction_sha256']:
            raise ValueError('prediction/checkpoint binding mismatch')
        rows.append(row['metrics'])
    # Bootstrap order is frozen lexically, not directory enumeration order.
    rows=[json.loads(checkpoints[c].read_text())['metrics'] for c in sorted(checkpoints)]
    summary=json.loads((bundle/'summary.json').read_text())
    for key,value in p.summarize(rows).items():
        if summary.get(key)!=value: raise ValueError('aggregate result not reproduced: '+key)
    return {'status':'AGGREGATE_REPRODUCED_FROM_PRIVATE_CHECKPOINTS','file_sha256':manifest,'console_sha256':p.sha(console),
            'limitations':'Does not re-evaluate image geometry/labels or constitute interpretation/ratification'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['bundle','private','console']: ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args(); print(json.dumps(verify(a.bundle,a.private,a.console),indent=2))
