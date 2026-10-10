"""Pure same-call format feedback. Host provenance/tests/review remain mandatory."""
import re
from orchestrator.experiment_plan_validation import validate_fits, contract, author_schema
from orchestrator import experiment_environment_requirements as requirements

PLAN_FIELDS = {"schema", "run_id", "operator_scope_sha256", "dispatch_mode", "fits",
               "preprocessing", "full_training", "environment_requirements"}
PRE_FIELDS = {"schema", "id", "input_contract_sha256", "environment_requirements_sha256",
              "split_sha256", "plans_name", "cohort_sha256", "source_capture_sha256", "partitions_sha256"}
PATCH_FIELDS = {"schema", "original_sha256", "view_sha256", "edits"}
EDIT_FIELDS = {"unit", "start", "end", "before_sha256", "replacement"}


def schema():
    return {"execution.plan.json": {"required_exact_fields": sorted(PLAN_FIELDS),
                "schema": requirements.PLAN_SCHEMA, "dispatch_mode": "incremental",
                "fits[]": "fit_id, stage (SMOKE/FULL), arm, fold (nonnegative integer), realization, outputs, validation_checks, preprocessing_id when preprocessing is declared",
                "preprocessing[]": sorted(PRE_FIELDS),
                "environment_requirements": {"fields": ["schema", "python", "cuda", "packages"],
                    "schema": requirements.SCHEMA, "versions": "exact; native CUDA build must later match"},
                "projection": author_schema()},
            "notebook.patch.json": {"required_exact_fields": sorted(PATCH_FIELDS),
                "schema": "safe-notebook-patch/v1", "edits[]": sorted(EDIT_FIELDS),
                "bounds": "1..80 nonoverlapping edits; integer byte spans within the supplied safe view"},
            "SPEC.proposed.md": "Exactly one each: run_id, operator_scope_sha256, execution_plan_sha256; match bindings and exact plan bytes",
            "execution_module": "Exactly one undecorated main(input_root, output_root, contract), synthetic_tests(), preprocess(input_root, output_root, contract), validate_preprocessing(output_root, contract); no defaults/varargs/keyword-only/positional-only arguments. The host tests require zero skips and failures.",
            "limits": "Each file at most80000 bytes. Strict JSON, no duplicate keys/nonfinite values. No execution or scientific approval from format acceptance."}


def plan(value, binding):
    if (not isinstance(value, dict) or set(value) != PLAN_FIELDS or
            value['schema'] != requirements.PLAN_SCHEMA or value['run_id'] != binding['run_id'] or
            value['operator_scope_sha256'] != binding['operator_scope_sha256'] or
            value['dispatch_mode'] != 'incremental' or not isinstance(value['preprocessing'], list) or
            not value['preprocessing']):
        raise ValueError('AUTHOR_PLAN_SCHEMA')
    requirements.validate(value['environment_requirements'])
    fits = validate_fits(value, incremental=True)
    contract(value)
    ids = set()
    for row in value['preprocessing']:
        if (not isinstance(row, dict) or set(row) != PRE_FIELDS or
                row['schema'] != requirements.PREPROCESSING_SCHEMA or
                any(not isinstance(row[k],str) or not re.fullmatch('[a-zA-Z0-9_-]{1,96}',row[k]) for k in ('id','plans_name')) or
                any(not isinstance(row[k],str) or not re.fullmatch('[a-f0-9]{64}',row[k]) for k in PRE_FIELDS if k.endswith('_sha256')) or
                row['environment_requirements_sha256'] != requirements.digest(value['environment_requirements']) or
                row['id'] in ids):
            raise ValueError('AUTHOR_PREPROCESSING_SCHEMA')
        ids.add(row['id'])
    if (ids != {f['preprocessing_id'] for f in fits} or len({f['fit_id'] for f in fits}) != len(fits) or
            any(not re.fullmatch('[a-zA-Z0-9_-]{1,96}',f['fit_id']) for f in fits)):
        raise ValueError('AUTHOR_PLAN_IDENTITIES')


def patch(value, binding):
    if (not isinstance(value,dict) or set(value)!=PATCH_FIELDS or value['schema']!='safe-notebook-patch/v1' or
            value['original_sha256']!=binding['original_sha256'] or value['view_sha256']!=binding['view_sha256'] or
            not isinstance(value['edits'],list) or not 1<=len(value['edits'])<=80):
        raise ValueError('AUTHOR_PATCH_SCHEMA')
    spans={}
    for row in value['edits']:
        if (not isinstance(row,dict) or set(row)!=EDIT_FIELDS or not isinstance(row['unit'],str) or
                not re.fullmatch(r'cells/[0-9]+/source',row['unit']) or
                type(row['start']) is not int or type(row['end']) is not int or not 0<=row['start']<row['end'] or
                not isinstance(row['before_sha256'],str) or not re.fullmatch('[a-f0-9]{64}',row['before_sha256']) or
                not isinstance(row['replacement'],str)):
            raise ValueError('AUTHOR_PATCH_EDIT_SCHEMA')
        if any(row['start']<end and row['end']>start for start,end in spans.get(row['unit'],[])):
            raise ValueError('AUTHOR_PATCH_OVERLAP')
        spans.setdefault(row['unit'],[]).append((row['start'],row['end']))


def visible_module(patch_value, view, manifest):
    """Reconstruct only complete visible writefile cells; never omitted bytes.

    This is supplementary same-call feedback. The host still applies the patch
    to its authentic original, validates privacy, extracts and tests exact code.
    """
    import hashlib
    from orchestrator.notebook_execution import entrypoints
    sha=lambda raw:hashlib.sha256(raw).hexdigest()
    if (not isinstance(view,bytes) or not isinstance(manifest,dict)
            or sha(view)!=patch_value['view_sha256'] or manifest.get('view_sha256')!=sha(view)
            or manifest.get('original_sha256')!=patch_value['original_sha256']
            or manifest.get('schema')!='private-scientific-view/v1'):
        raise ValueError('AUTHOR_MODULE_VIEW_BINDING')
    groups={}
    for span in manifest['spans']:
        unit=span['unit']
        if not re.fullmatch(r'cells/[0-9]+/source',unit):continue
        groups.setdefault(unit,[]).append(span)
    edits={}
    for edit in patch_value['edits']:edits.setdefault(edit['unit'],[]).append(edit)
    parts=[]
    for unit,spans in sorted(groups.items(),key=lambda pair:int(pair[0].split('/')[1])):
        cursor=0;chunks=[];complete=True;applied=set();is_code=False
        for span in spans:
            start,end=span['start'],span['end']
            if type(start) is not int or type(end) is not int or start!=cursor or end<=start:
                raise ValueError('AUTHOR_MODULE_SPAN_PARTITION')
            cursor=end
            if not span['keep']:
                complete=False
                continue
            marker=('\n## '+unit+' bytes '+str(start)+':'+str(end)+'\n').encode()
            if view.count(marker)!=1:raise ValueError('AUTHOR_MODULE_SPAN_MARKER')
            position=view.index(marker)+len(marker);raw=view[position:position+end-start]
            if len(raw)!=end-start or sha(raw)!=span['sha256']:
                raise ValueError('AUTHOR_MODULE_SPAN_CHANGED')
            is_code|=span['kind']=='code'
            chosen=[]
            for index,edit in enumerate(edits.get(unit,[])):
                if start<=edit['start']<edit['end']<=end:
                    before=raw[edit['start']-start:edit['end']-start]
                    if sha(before)!=edit['before_sha256']:raise ValueError('AUTHOR_MODULE_PATCH_PREIMAGE')
                    chosen.append(edit);applied.add(index)
            for edit in sorted(chosen,key=lambda e:e['start'],reverse=True):
                raw=raw[:edit['start']-start]+edit['replacement'].encode()+raw[edit['end']-start:]
            chunks.append(raw)
        if applied!=set(range(len(edits.get(unit,[])))):
            raise ValueError('AUTHOR_MODULE_PATCH_OUTSIDE_VISIBLE_SPAN')
        source=b''.join(chunks).decode()
        if not complete:
            # A partial cell is not an executable reconstruction. No placeholder
            # can impersonate omitted membership, even when its hash is known.
            if '%%writefile ' in source:raise ValueError('AUTHOR_MODULE_OMITTED_CODE')
            continue
        lines=source.splitlines(keepends=True)
        if not lines or not lines[0].startswith('%%writefile '):continue
        if not is_code:raise ValueError('AUTHOR_MODULE_CODE_CLASSIFICATION')
        directive=lines[0].strip()
        required='%%writefile '+('-a ' if parts else '')+'/content/sprint13_pipeline.py'
        if directive!=required or any(line.lstrip().startswith(('!','%')) for line in lines[1:]):
            raise ValueError('AUTHOR_MODULE_WRITEFILE_ORDER')
        parts.append(''.join(lines[1:]))
    if set(edits)-set(groups) or not parts:raise ValueError('AUTHOR_MODULE_VISIBLE_CODE_REQUIRED')
    source=''.join(parts)
    try:entrypoints(source,preprocessing=True)
    except (SyntaxError,ValueError) as error:
        raise ValueError('AUTHOR_MODULE_ENTRYPOINT: '+str(error)) from error
    return sha(source.encode())
