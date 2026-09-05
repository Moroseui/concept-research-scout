#!/usr/bin/env python3
"""Build thin pilot notebooks from versioned scripts, pinned to an existing commit."""
import argparse
import json
from pathlib import Path
import subprocess
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]


def notebook(cells,path):
    nb=nbf.v4.new_notebook(cells=cells)
    # Deterministic cell IDs make regeneration reviewable.
    for i,cell in enumerate(nb.cells): cell['id']=f'pilot-cell-{i:02d}'
    nbf.write(nb,path)


def main(pin):
    pin=subprocess.check_output(['git','rev-parse',pin],cwd=ROOT).decode().strip()
    md=nbf.v4.new_markdown_cell; code=nbf.v4.new_code_cell
    setup=code(f'''from pathlib import Path
import subprocess, sys
PIN = {pin!r}
REPO = Path('/content/scout-pilot-' + PIN[:12])
if not REPO.exists():
    subprocess.run(['git', 'clone', 'https://github.com/Moroseui/concept-research-scout.git', str(REPO)], check=True)
subprocess.run(['git', 'checkout', '--detach', PIN], cwd=REPO, check=True)
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip() == PIN
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=REPO,text=True).strip(), 'Modified code; use a fresh checkout'
sys.path.insert(0,str(REPO))''')
    base=ROOT/'campaigns/isles24-pilot'
    notebook([md('''# Synthetic Colab execution and retrieval test

CPU only. No patient data, Drive mount or credentials. Run All manually, or ask
Colab MCP to execute the cells and retrieve the result. A browser connection
alone is not success: preserve returned output from both operations.'''),setup,
        code("subprocess.run([sys.executable, str(REPO/'campaigns/isles24-pilot/colab/smoke.py'), 'execute'], check=True)"),
        code("subprocess.run([sys.executable, str(REPO/'campaigns/isles24-pilot/colab/smoke.py'), 'retrieve'], check=True)")],base/'colab/synthetic_execution.ipynb')
    notebook([md('''# P001 — admission perfusion baseline

This notebook runs one frozen exploratory baseline on 99 eligible cases.
Use a CPU runtime. Cross-family review must be committed before Run All can
pass the authority gate. Keep all private outputs in your own Drive; do not
upload patient files to Git. No follow-ups run here. See SPEC.md and RESULT_CARD.md.

Set ARCHIVE to your existing checksum-pinned local train.7z, or DATA_ROOT to
an existing selectively staged tree. Reading the 99 GB archive directly from
Drive can be slow; existing verified local staging is preferable. The script
extracts only the 198 selected files. It never downloads or extracts the full
cohort. Return aggregate outputs plus original console and private audit
checkpoints through the agreed private channel; no automatic push occurs.'''),setup,
        code("from google.colab import drive\ndrive.mount('/content/drive')\nOUTPUT = Path('/content/drive/MyDrive/isles-pilot/P001-v1')\nARCHIVE = Path('/content/train.7z')\nDATA_ROOT = None  # alternatively a verified selectively staged root\n"),
        code("EXPERIMENT = REPO/'campaigns/isles24-pilot/experiments/P001'\nsubprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', str(EXPERIMENT/'requirements.txt')], check=True)\nif not (EXPERIMENT/'review.json').is_file():\n    raise RuntimeError('Opposing-family spec/code review pending; do not run patient workflow')\n"),
        code("from orchestrator.publication import run_logged\ncommand = [sys.executable, str(EXPERIMENT/'run.py'), '--output-dir', str(OUTPUT)]\ncommand += ['--data-root', str(DATA_ROOT)] if DATA_ROOT else ['--archive', str(ARCHIVE)]\nexit_code = run_logged(command, OUTPUT)\nprint('Exit:', exit_code, '; console:', str(OUTPUT)+'.console.log')\nif exit_code: raise RuntimeError('Attempt failed; evidence and checkpoints preserved')"),
        code("from orchestrator.publication import validate\npolicy = __import__('json').loads((EXPERIMENT/'publication.json').read_text())\nvalidate(OUTPUT, policy)\nprint((OUTPUT/'RESULT_CARD.md').read_text())\nprint('Keep private audit files at:', str(OUTPUT)+'.private')")],base/'experiments/P001/colab_P001.ipynb')
    print('Notebooks pinned to',pin)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--pin',default='HEAD'); a=ap.parse_args(); main(a.pin)
