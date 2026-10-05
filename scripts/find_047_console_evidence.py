#!/usr/bin/env python3
"""Read bounded existing console/notebook evidence; never reconstruct or execute.

Paths and candidate identities are written privately. Stdout has counts only.
A marker hit is a candidate, not proof of an original successful console.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

CONTRACT = 'dc586665d0bece940d1a1f4b3b0572f8c951c2ba'
LIMIT = 32 * 1024 * 1024


def inspect(path):
    raw = path.read_bytes()
    if path.suffix == '.ipynb':
        nb = json.loads(raw)
        # Examine output payloads only, never treat notebook source as execution.
        parts = []
        for cell in nb.get('cells', []):
            for output in cell.get('outputs', []):
                value = output.get('text', output.get('data', {}).get('text/plain', ''))
                parts.append(''.join(value) if isinstance(value, list) else str(value))
        text = '\n'.join(parts)
    else:
        text = raw.decode('utf-8', errors='replace')
    markers = {'contract': CONTRACT in text,
               'phase_b_authority': '[authority] Idea 047 Phase B' in text,
               'completion': 'STUDY_COMPLETE' in text,
               'failure': 'PROBE FAILURE' in text or 'exit=7' in text}
    return {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(),
            'bytes': len(raw), 'markers': markers,
            'disposition': 'CANDIDATE_REQUIRES_ORIGINAL_PROVENANCE' if all(markers[k] for k in ['contract','phase_b_authority','completion']) else 'NO_COMPLETE_MARKER_COMBINATION'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,action='append',required=True)
    ap.add_argument('--private-output',type=Path,required=True)
    a=ap.parse_args()
    repo=Path(__file__).resolve().parents[1]
    output=a.private_output.absolute()
    if output.exists() or output.resolve().is_relative_to(repo):
        raise ValueError('FRESH_PRIVATE_OUTPUT_REQUIRED')
    os.umask(0o077);output.mkdir(mode=0o700)
    findings=[]; skipped=[];seen=set();started=time.monotonic()
    for root in a.root:
        if root.is_symlink():raise ValueError('ROOT_SYMLINK')
        for folder,dirs,files in os.walk(root,followlinks=False):
            dirs[:]=[n for n in dirs if n not in ['.git','objects','node_modules','staged','__pycache__'] and not n.endswith('.git')]
            for name in files:
                p=Path(folder)/name
                if p.is_symlink():continue
                if not (p.suffix=='.txt' and any(k in name.lower() for k in ['console','run_log','session'])) and p.suffix not in ['.log','.stdout','.stderr','.ipynb'] and not (p.suffix=='.jsonl' and any(k in name for k in ['protocol','session','transcript'])):continue
                if p.resolve() in seen:continue
                seen.add(p.resolve())
                if time.monotonic()-started>90 or p.stat().st_size>LIMIT:
                    skipped.append({'path':str(p),'reason':'TIME_OR_SIZE_BOUND'});continue
                try:findings.append(inspect(p))
                except (OSError,ValueError,TypeError) as error:skipped.append({'path':str(p),'reason':type(error).__name__})
    (output/'inventory.json').write_text(json.dumps({'findings':findings,'skipped':skipped},indent=2)+'\n')
    summary={'status':'BOUNDED_SEARCH_COMPLETE','files_checked':len(findings),'files_skipped':len(skipped),
             'candidate_files':sum(r['disposition']=='CANDIDATE_REQUIRES_ORIGINAL_PROVENANCE' for r in findings),
             'original_successful_console_established':False,'experiment_executed':False,
             'inventory_sha256':hashlib.sha256((output/'inventory.json').read_bytes()).hexdigest(),
             'limits':'Only existing log/stream/notebook-output and named protocol files, 32 MiB each, 90-second read bound; candidate markers do not establish original provenance.'}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))

if __name__=='__main__':main()
