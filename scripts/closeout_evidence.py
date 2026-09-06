"""Reproduce the historical 047 notebook without executing any notebook cell.

Generator revision, acquisition pin, CLI arguments, and nbformat are distinct
inputs. Random cell IDs are compared explicitly; normalization is not byte proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
GENERATOR='469d29df002ea78f64146731244769d7c82330d6'
SOURCE='9216e6acce01c5113fc505ad96404fa4e36ffab6'
NOTEBOOK='probes/047/colab_probe_047.ipynb'
ARGS=['package-colab','47','--phase','B','--staging-zenodo','16813698','--staging-record','16813698','--staging-mode','origin_direct','--omit-phase-flag','--runner-args','--archive-file {ARCHIVE_LOCAL} --member-manifest probes/023/results/results_v2/archive_manifest.csv','--runner-setup','apt-get -qq install -y p7zip-full > /dev/null']


def digest(b):return hashlib.sha256(b).hexdigest()
def generate(destination):
    destination=Path(destination).resolve()
    if destination.is_relative_to(ROOT):raise ValueError('use private disposable directory outside Git')
    destination.mkdir(mode=0o700)
    repo=destination/'repo';repo.mkdir()
    def git(*args):return subprocess.check_output(['git',*args],cwd=repo,stderr=subprocess.PIPE)
    git('init','-q');git('fetch','--no-tags',str(ROOT),SOURCE,GENERATOR);git('checkout','--detach',SOURCE)
    git('remote','add','origin','https://github.com/Moroseui/concept-research-scout.git')
    # Explicit historical generator overlay: HEAD is the source-acquisition pin,
    # while scout.py bytes are the generator committed with the target notebook.
    generator=git('show',GENERATOR+':scout.py');(repo/'scout.py').write_bytes(generator)
    original=git('show',GENERATOR+':'+NOTEBOOK);(destination/'original.ipynb').write_bytes(original)
    command=[sys.executable,'scout.py',*ARGS]
    result=subprocess.run(command,cwd=repo,capture_output=True)
    (destination/'generator.stdout').write_bytes(result.stdout);(destination/'generator.stderr').write_bytes(result.stderr)
    if result.returncode:raise RuntimeError('generation failed; original console retained privately')
    generated=(repo/NOTEBOOK).read_bytes();(destination/'generated.ipynb').write_bytes(generated)
    a,b=json.loads(original),json.loads(generated)
    sources_a=[(c['cell_type'],''.join(c['source'])) for c in a['cells']]
    sources_b=[(c['cell_type'],''.join(c['source'])) for c in b['cells']]
    differing=[]
    for i,(x,y) in enumerate(zip(a['cells'],b['cells'])):
        for k in set(x)|set(y):
            if x.get(k)!=y.get(k):differing.append({'cell':i,'field':k})
    no_ids=lambda n:{**n,'cells':[{k:v for k,v in c.items() if k!='id'} for c in n['cells']]}
    import nbformat
    receipt={'generator_commit':GENERATOR,'source_acquisition_pin':SOURCE,'target_notebook_commit':GENERATOR,'generator_file_sha256':digest(generator),'cli_argv':command[1:],'nbformat_version':nbformat.__version__,
        'overlay':'source HEAD 9216e6 with scout.py bytes from 469d29d; no implicit claim that those commits are identical',
        'original_sha256':digest(original),'generated_sha256':digest(generated),'exact_bytes_equal':original==generated,'cell_count_original':len(a['cells']),'cell_count_generated':len(b['cells']),
        'cell_sources_equal':sources_a==sources_b,'notebook_equal_after_removing_cell_ids':no_ids(a)==no_ids(b),'different_cell_fields':differing,
        'top_level_metadata_equal':a.get('metadata')==b.get('metadata'),'run_py_before':git('rev-parse',SOURCE+':probes/047/run.py').decode().strip(),'run_py_after_sha256':digest((repo/'probes/047/run.py').read_bytes()),
        'run_py_unchanged':git('show',SOURCE+':probes/047/run.py')==(repo/'probes/047/run.py').read_bytes(),'notebook_cells_executed':0,'patient_payloads_opened':0,
        'limitation':'This is a current reproduction from explicit historical inputs, not a reconstructed original generation session.'}
    (destination/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--private-dir',required=True);a=p.parse_args();print(json.dumps(generate(a.private_dir),indent=2))
