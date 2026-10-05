"""Deterministic correspondence intake of private Drive originals; no analysis."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

IMPLEMENTATION = '4a69a4226ebdc5cdff1a6128f96e3f94fde172863690ec73b2f848250955a926'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path, maximum=50000):
    path = Path(path)
    if any(p.is_symlink() for p in [path, *path.parents]) or not path.is_file():
        raise ValueError('REGULAR_PRIVATE_ORIGINAL_REQUIRED')
    if path.stat().st_mode & 0o077 or path.stat().st_size > maximum:
        raise ValueError('PRIVATE_ORIGINAL_MODE_OR_SIZE')
    return path.read_bytes()


def collected(root, alias):
    folder = Path(root) / (alias + '-original-0001')
    raw = read(folder / 'original')
    receipt_raw = read(folder / 'receipt.json')
    receipt = json.loads(receipt_raw)
    if (receipt.get('status') != 'PRIVATE_ORIGINAL_COLLECTED'
            or receipt.get('sha256') != sha(raw) or receipt.get('bytes') != len(raw)
            or receipt.get('implementation_sha256') != IMPLEMENTATION
            or receipt.get('alias') != alias):
        raise ValueError('ORIGINAL_COLLECTION_BINDING_REQUIRED')
    return raw, {'sha256': sha(raw), 'bytes': len(raw), 'collection_receipt_sha256': sha(receipt_raw)}


def p001(root):
    raw, binding = collected(root, 'p001-preflight-receipt')
    console, console_binding = collected(root, 'p001-preflight-console')
    headers, headers_binding = collected(root, 'p001-preflight-headers')
    receipt = json.loads(raw)
    if json.loads(console) != receipt:
        raise ValueError('PREFLIGHT_CONSOLE_RECEIPT_MISMATCH')
    expected = {'status': 'INPUT_INTEGRITY_AND_HEADERS_VERIFIED',
        'prediction_executed': False, 'labels_opened': False, 'reserved_access': False,
        'archive_size': 99014629647, 'archive_md5': '36ae28b9a17f7340b8bbef62b595cb57',
        'eligible_cohort_verified': 99, 'admission_members_checked': 1,
        'selection_rule': 'first_lexical_eligible_id_no_outcome_selection',
        'headers_sha256': sha(headers),
        'unit_semantics': 'HEADER_EVIDENCE_ONLY_REQUIRES_RELEASE_PROVENANCE_ASSESSMENT',
        'launch_authorized': False}
    if (set(receipt) != set(expected) | {'elapsed_seconds'}
            or any(type(receipt[k]) is not type(v) or receipt[k] != v for k, v in expected.items())
            or type(receipt['elapsed_seconds']) not in (int, float)
            or not math.isfinite(receipt['elapsed_seconds']) or receipt['elapsed_seconds'] < 0):
        raise ValueError('EXPECTED_TERMINAL_PREFLIGHT_REPORT_REQUIRED')
    values = json.loads(headers)
    if not isinstance(values, dict) or len(values) != 1:
        raise ValueError('ONE_PRIVATE_HEADER_REQUIRED')
    sample = next(iter(values.values()))
    if set(sample) != {'sha256', 'header'} or not re.fullmatch('[0-9a-f]{64}', sample['sha256']):
        raise ValueError('HEADER_FILE_BINDING_REQUIRED')
    h = sample['header']
    if (set(h) != {'shape','dtype','proxy_slope','proxy_intercept','xyzt_units'}
            or not isinstance(h['shape'],list) or len(h['shape']) != 3
            or any(type(n) is not int or not 0 < n < 100000 for n in h['shape'])
            or h['dtype'] not in ('float32','float64','int16','int32','uint16','uint8','int8','uint32')
            or any(type(h[k]) not in (int,float) or not math.isfinite(h[k]) for k in ('proxy_slope','proxy_intercept'))
            or not isinstance(h['xyzt_units'],list) or len(h['xyzt_units']) != 2
            or h['xyzt_units'][0] not in ('unknown','meter','mm','micron')
            or h['xyzt_units'][1] not in ('unknown','sec','msec','usec','hz','ppm','rads')):
        raise ValueError('HEADER_SCHEMA_REQUIRED')
    return {'version':1, 'stage':'drive-p001-preflight-intake',
        'status':'TERMINAL_REPORT_AND_HEADER_CORRESPONDENCE_VERIFIED',
        'originals': {'receipt':binding, 'console':console_binding, 'headers':headers_binding},
        'reported_preflight':receipt, 'single_sample_header_without_case_identity':h,
        'private_member_sha256_retained_not_exported':True,
        'original_attempt_binding_supplied':False,
        'scientific_acceptance':False, 'launch_authorized':False,
        'limitations':['Reported archive checksum and preflight observations, not a new archive examination.',
                      'Header schema and byte correspondence do not establish scalar Tmax units.',
                      'No original attempt binding or process-exit attestation supplied in these three files.']}


def sibling(root, notebook_directory, git_dir):
    from orchestrator.notebook_evidence import inspect
    raw, binding = collected(root, '047-console')
    prior_raw = read(Path(notebook_directory) / 'receipt.json')
    prior = json.loads(prior_raw)
    notebook = read(Path(notebook_directory) / 'original.ipynb', 32*1024*1024)
    source = '940293b6d562f2d3dd6bfd9d8d8281ccf01e4783'
    replacement = 'c812421207b6ddcba6516444897c777d8440275a'
    contract = 'dc586665d0bece940d1a1f4b3b0572f8c951c2ba'
    summary_path = 'probes/047/results_v2/summary.json'
    summaries = [subprocess.check_output(['git','--git-dir',str(git_dir),'show',s+':'+summary_path],stderr=subprocess.PIPE,timeout=30) for s in (source,replacement)]
    if (summaries[0] != summaries[1] or prior.get('summary_sha256') != sha(summaries[0])
            or prior.get('notebook_sha256') != sha(notebook)
            or prior.get('source_commit') != source or prior.get('replacement_commit') != replacement
            or prior.get('contract') != contract):
        raise ValueError('RETAINED_NOTEBOOK_SOURCE_BINDING_CHANGED')
    matches, streams = inspect(notebook, summaries[0], contract)
    if matches != prior.get('matches') or len(matches) != 1:
        raise ValueError('NOTEBOOK_CORRESPONDENCE_CHANGED')
    match = matches[0]
    same = [payload for _, payload in streams if sha(payload) == match['stream_sha256']]
    if len(same) != 1 or same[0] != raw:
        raise ValueError('ORIGINAL_SIBLING_NOTEBOOK_STREAM_DIFFERS')
    return {'version':1,'stage':'drive-047-sibling-intake',
        'status':'ORIGINAL_SIBLING_MATCHES_REVIEWED_NOTEBOOK_STREAM',
        'original':binding,'prior_notebook_receipt_sha256':sha(prior_raw),
        'source':source,'replacement':replacement,'contract':contract,
        'summary_sha256':sha(summaries[0]),'saved_stream_byte_identical':True,
        'contract_in_stream':match['contract_in_same_stream'],
        'study_complete_in_stream':match['study_complete_in_same_stream'],
        'traceback_in_stream':match['traceback_in_same_stream'],
        'exit_status':None,'scientific_acceptance':False,'experiment_executed':False,
        'limitation':'Collected original sibling bytes correspond to the reviewed saved stream; no independent process exit attestation or scientific acceptance.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['p001','047']);p.add_argument('--originals',required=True)
    p.add_argument('--notebook-directory');p.add_argument('--git-dir');p.add_argument('--output',required=True)
    a=p.parse_args(); result=p001(a.originals) if a.mode=='p001' else sibling(a.originals,a.notebook_directory,a.git_dir)
    output=Path(a.output)
    if any(p.is_symlink() for p in [output,*output.parents]):raise ValueError('OUTPUT_SYMLINK')
    with output.open('x') as out:out.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    output.chmod(0o600)
    print(json.dumps({'status':result['status'],'receipt_sha256':sha(output.read_bytes()),'scientific_acceptance':False}))




def external_collected(root, alias, request_id, *, implementation_sha256, expected_sha256, maximum):
    """Read a newly registered external artifact using its actual collector binding.

    Historical P001/047 intake retains its original fixed implementation check.
    This path does not register an alias, widen a grant, download or execute.
    """
    if (not re.fullmatch(r'[a-z0-9][a-z0-9-]{7,79}', request_id)
            or not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,79}', alias)
            or any(not re.fullmatch(r'[0-9a-f]{64}', x) for x in (implementation_sha256, expected_sha256))
            or type(maximum) is not int or not 0 < maximum <= 32 * 1024 * 1024):
        raise ValueError('EXTERNAL_COLLECTION_EXACT_BINDING_REQUIRED')
    directory = Path(root) / request_id
    raw = read(directory / 'original', maximum)
    receipt_raw = read(directory / 'receipt.json')
    receipt = json.loads(receipt_raw)
    if (receipt.get('status') != 'PRIVATE_ORIGINAL_COLLECTED'
            or receipt.get('sha256') != expected_sha256 or sha(raw) != expected_sha256
            or receipt.get('bytes') != len(raw) or receipt.get('alias') != alias
            or receipt.get('implementation_sha256') != implementation_sha256):
        raise ValueError('EXTERNAL_ORIGINAL_COLLECTION_CHANGED')
    return raw, {'sha256': sha(raw), 'bytes': len(raw), 'alias': alias,
                 'request_id': request_id, 'origin': 'INSTALLED_DRIVE_ORIGINAL_COLLECTION',
                 'collection_receipt_sha256': sha(receipt_raw),
                 'implementation_sha256': implementation_sha256}


def external_artifact(path, expected_sha256, *, maximum=32 * 1024 * 1024):
    """Inspect bounded supplied originals, preserving case data outside model text."""
    import csv
    import io
    import stat
    import zipfile
    from pathlib import PurePosixPath
    if not re.fullmatch(r'[0-9a-f]{64}', expected_sha256):
        raise ValueError('EXTERNAL_ARTIFACT_HASH_REQUIRED')
    if type(maximum) is not int or not 0 < maximum <= 32 * 1024 * 1024:
        raise ValueError('EXTERNAL_ARTIFACT_BOUND_REQUIRED')
    raw = read(path, maximum)
    if sha(raw) != expected_sha256:
        raise ValueError('EXTERNAL_ARTIFACT_IDENTITY_CHANGED')
    result = {'sha256': expected_sha256, 'bytes': len(raw),
              'case_contents_retained_private': True, 'scientific_acceptance': False}
    suffix = Path(path).suffix.lower()
    if suffix == '.csv':
        rows = list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
        if not rows or any(len(row) != len(rows[0]) for row in rows):
            raise ValueError('EXTERNAL_CSV_SHAPE')
        result.update(format='CSV', rows=len(rows) - 1, columns=rows[0])
    elif suffix in ('.zip', '.pptx'):
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            members = archive.infolist()
            if len(members) > 512 or sum(row.file_size for row in members) > 256 * 1024 * 1024:
                raise ValueError('EXTERNAL_ARCHIVE_EXPANSION_BOUND')
            names = set()
            for member in members:
                name = PurePosixPath(member.filename)
                if (member.filename in names or name.is_absolute() or '..' in name.parts
                        or '\\' in member.filename or stat.S_ISLNK(member.external_attr >> 16)
                        or member.flag_bits & 1):
                    raise ValueError('EXTERNAL_ARCHIVE_UNSAFE_MEMBER')
                names.add(member.filename)
            if archive.testzip() is not None:
                raise ValueError('EXTERNAL_ARCHIVE_CRC')
            result.update(format='PRESENTATION_DERIVED_SUMMARY' if suffix == '.pptx' else 'ZIP',
                          archive_members=len(members), extracted=False, archive_crc_verified=True)
    else:
        result['format'] = 'ORIGINAL_BYTES'
    return raw, result


if __name__=='__main__':main()
