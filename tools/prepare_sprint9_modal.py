"""Extract unchanged scientific definitions from the pinned, executed notebook.

No cell execution, training, upload or model call. Paths, run selection and
identity validation live in the separately reviewed headless entry point.
"""
import ast
import hashlib
import json
from pathlib import Path
from orchestrator import private_records

NOTEBOOK_SHA256='a519f3e0ed92850a9a39edf364b4415573f7a751cf06b89f2ff7de0dc6eb5c06'
FUNCTIONS={'load_cache','apply_normative','compute_normative','dice','vol_from_flat','expected_volume_ml','rank_order','rule_topk_lexsort',
           'feature_volume','feature_scale','pad_to','sample_patch_origin','sliding_windows','assemble_windows','official_lesion_metrics','smooth_scores'}
CONSTANTS={'CACHE_SCHEMA','FEATURE_NAMES','Z_COLUMNS'}
HEADER="""# Scientific definitions copied verbatim from the pinned Sprint9 notebook.
# See science-provenance.json. No top-level training or data loading.
import os, json, time, glob, uuid, hashlib, datetime
import numpy as np, pandas as pd, psutil
from scipy.ndimage import gaussian_filter, distance_transform_edt, binary_erosion, label as cc_label
from sklearn.metrics import roc_auc_score, average_precision_score
"""


def prepare(notebook,destination):
    raw=Path(notebook).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=NOTEBOOK_SHA256:raise ValueError('SPRINT9_NOTEBOOK_CHANGED')
    nb=json.loads(raw);parts=[HEADER];records=[]
    for cell in (3,10,12):
        source=''.join(nb['cells'][cell]['source']);tree=ast.parse(source)
        for node in tree.body:
            keep=isinstance(node,(ast.FunctionDef,ast.ClassDef)) and (cell!=3 or node.name in FUNCTIONS)
            if isinstance(node,ast.Assign):
                names={x.id for x in node.targets if isinstance(x,ast.Name)}
                keep=(cell==3 and bool(names&CONSTANTS)) or (cell==10)
            if not keep:continue
            segment=ast.get_source_segment(source,node)
            parts.append(segment+'\n')
            records.append({'cell':cell,'start':node.lineno,'end':node.end_lineno,'sha256':hashlib.sha256(segment.encode()).hexdigest()})
        if cell==3:
            # Literal string definitions only. Do not execute the notebook's exec.
            torch_source=''
            for node in tree.body:
                if isinstance(node,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='TORCH_CODE' for x in node.targets):torch_source=ast.literal_eval(node.value)
                if isinstance(node,ast.AugAssign) and isinstance(node.target,ast.Name) and node.target.id=='TORCH_CODE':
                    if not isinstance(node.op,ast.Add):raise ValueError('SPRINT9_TORCH_LITERAL')
                    torch_source+=ast.literal_eval(node.value)
            ast.parse(torch_source);parts.append(torch_source)
            records.append({'cell':3,'literal':'TORCH_CODE combined literal definitions','sha256':hashlib.sha256(torch_source.encode()).hexdigest()})
    combined='\n'.join(parts);ast.parse(combined)
    dest=Path(destination);private_records.mkdir(dest,parents=True)
    private_records.write_text(dest/'science.py',combined)
    provenance={'source_notebook_sha256':NOTEBOOK_SHA256,'extraction':'verbatim selected definitions and literal torch definitions; no notebook execution',
                'science_sha256':hashlib.sha256(combined.encode()).hexdigest(),'segments':records}
    private_records.write_text(dest/'science-provenance.json',json.dumps(provenance,indent=2)+'\n')
    return provenance
