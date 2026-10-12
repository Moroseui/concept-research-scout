"""Mechanical notebook variants; scientific code is always authored upstream."""
import ast
import json
from pathlib import Path
from orchestrator.manual_executor import digest
from orchestrator.manual_driver import write_once
from orchestrator import scientific_intake as intake

COVERAGE_INDEPENDENT_ARMS = frozenset((
    "A1_repeat", "A1_multiwin", "A1_pnormct", "A1_pnorm_v2", "A1_L", "A1_repeat2",
))

def variants(raw, *, expected_arm="A1_repeat", arm_level_only=False):
    if type(arm_level_only) is not bool:
        raise ValueError("DELIVERY_FORMAT_BOOLEAN_REQUIRED")
    # Selection is supplied by the reviewed controller, never inferred from model output.
    if type(expected_arm) is not str or expected_arm not in COVERAGE_INDEPENDENT_ARMS:
        raise ValueError("DELIVERY_RELEASED_ARM_REQUIRED")
    nb=json.loads(raw)
    if nb.get('nbformat')!=4 or any(c.get('outputs') or c.get('execution_count') is not None for c in nb['cells'] if c['cell_type']=='code'):
        raise ValueError('DELIVERY_UNEXECUTED_NOTEBOOK_REQUIRED')
    cell=nb['cells'][4]
    if cell['cell_type']!='code':raise ValueError('DELIVERY_CONFIG_CELL_REQUIRED')
    source=''.join(cell['source']);lines=source.splitlines(keepends=True)
    parse=list(lines)
    if parse and parse[0].startswith('%%writefile '):parse[0]='\n'
    tree=ast.parse(''.join(parse))
    selected={}
    for node in tree.body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in {'DELIVERY_ARM','DELIVERY_FOLDS'}:
                    if len(node.targets)!=1 or target.id in selected:raise ValueError('DELIVERY_ONE_ASSIGNMENT')
                    selected[target.id]=node
        elif isinstance(node,(ast.AnnAssign,ast.AugAssign)) and isinstance(node.target,ast.Name) and node.target.id in {'DELIVERY_ARM','DELIVERY_FOLDS'}:
            raise ValueError('DELIVERY_PLAIN_LITERAL_REQUIRED')
    if set(selected)!={'DELIVERY_ARM','DELIVERY_FOLDS'}:raise ValueError('DELIVERY_CONSTANTS_REQUIRED')
    arm=ast.literal_eval(selected['DELIVERY_ARM'].value);folds=ast.literal_eval(selected['DELIVERY_FOLDS'].value)
    if arm!=expected_arm or type(folds)is not tuple or folds!=(0,1,2,3,4) or any(type(x)is not int for x in folds):
        raise ValueError('DELIVERY_EXACT_ARM_FOLDS')
    node=selected['DELIVERY_FOLDS'].value;encoded=source.encode()
    start=sum(len(x.encode()) for x in lines[:node.lineno-1])+node.col_offset
    end=sum(len(x.encode()) for x in lines[:node.end_lineno-1])+node.end_col_offset
    result={f'13B_{arm}.ipynb':raw}
    if arm_level_only:
        return result  # Exact author bytes; no fold variants or scientific edits.
    for fold in range(5):
        copy=json.loads(raw)
        changed=encoded[:start]+repr((fold,)).encode()+encoded[end:]
        copy['cells'][4]['source']=changed.decode().splitlines(keepends=True)
        result[f'13B_{arm}_fold{fold}.ipynb']=(json.dumps(copy,ensure_ascii=False,indent=1)+'\n').encode()
        # Only the literal in this one source cell may differ.
        compare=json.loads(result[f'13B_{arm}_fold{fold}.ipynb'])
        compare['cells'][4]=nb['cells'][4]
        if compare!=nb:raise ValueError('DELIVERY_UNRELATED_CHANGE')
    return result

def prepare_variants(driver,value,pending,cases,*,expected_arm="A1_repeat",arm_level_only=False):
    from orchestrator.colab_simple_full import validate,require
    require(validate(driver.store,driver.config['run_id']) is not None,'REVIEWED_DELIVERY_SCOPE')
    folder=Path(value['notebook_revision_result']['folder'])
    raw=(folder/'revised.ipynb').read_bytes()
    files=variants(raw,expected_arm=expected_arm,arm_level_only=arm_level_only);manifest={}
    for name,body in files.items():
        # Existing full notebook has already passed the preserved-member scan.
        # Variants can only change a literal fold tuple; never execute them here.
        write_once(folder/'delivery'/name,body)
        manifest[name]={'sha256':digest(body),'bytes':len(body)}
        driver.artifact(value,'notebook_source','delivery-'+str(pending['round'])+'-'+name,body,pending['round'])
    receipt={'schema':'colab-notebook-delivery/v1','source_notebook_sha256':digest(raw),
        'only_change':'none; exact authored arm notebook' if arm_level_only else 'cell4 DELIVERY_FOLDS literal tuple','files':manifest,
        'patient_data':False,'notebook_executed':False,'code_review_required':True}
    body=intake.canonical(receipt)
    write_once(folder/'delivery'/'manifest.json',body)
    driver.artifact(value,'notebook_provenance','delivery-'+str(pending['round'])+'-manifest.json',body,pending['round'])
    value['colab_delivery']={'folder':str(folder/'delivery'),'manifest_sha256':digest(body)}
