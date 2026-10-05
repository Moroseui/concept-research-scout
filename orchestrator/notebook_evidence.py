"""Incoming saved-notebook evidence intake, never execution or scientific acceptance.

Preserves exact notebook bytes and each saved stream privately. Summary equality
is an evidence correspondence check; it supplies neither an exit status nor a
claim that Colab saved every byte of the original process console.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def inspect(raw, summary, contract):
    notebook = json.loads(raw)
    expected = json.loads(summary)
    matches = []
    streams = []
    for index, cell in enumerate(notebook['cells']):
        for ordinal, output in enumerate(cell.get('outputs', [])):
            if output.get('output_type') != 'stream':
                continue
            value = output['text']
            text = ''.join(value) if isinstance(value, list) else value
            payload = text.encode('utf-8')
            name = f'cell-{index}-output-{ordinal}.txt'
            streams.append((name, payload))
            for offset in (m.start() for m in re.finditer(r'\{', text)):
                try:
                    obj, length = json.JSONDecoder().raw_decode(text[offset:])
                except ValueError:
                    continue
                if obj == expected:
                    matches.append({'cell_index': index, 'output_index': ordinal,
                                    'execution_count': cell.get('execution_count'),
                                    'stream_sha256': sha(payload), 'stream_bytes': len(payload),
                                    'summary_character_offset': offset,
                                    'summary_character_length': length,
                                    'contract_in_same_stream': contract in text,
                                    'study_complete_in_same_stream': 'STUDY_COMPLETE' in text,
                                    'traceback_in_same_stream': 'Traceback (most recent call last)' in text})
    return matches, streams


def intake(notebook, private_destination, git_dir, source, replacement, summary_path, contract):
    for pin in (source, replacement, contract):
        if not re.fullmatch('[0-9a-f]{40}', pin):
            raise ValueError('EXACT_PINS_REQUIRED')
    notebook, destination = Path(notebook), Path(private_destination)
    repo = Path(__file__).resolve().parents[1]
    if notebook.is_symlink() or not notebook.is_file():
        raise ValueError('REGULAR_ORIGINAL_REQUIRED')
    if destination.resolve().is_relative_to(repo) or destination.exists():
        raise ValueError('FRESH_PRIVATE_DESTINATION_REQUIRED')
    if destination.parent.is_symlink() or not destination.parent.is_dir():
        raise ValueError('EXISTING_PRIVATE_PARENT_REQUIRED')
    if destination.parent.stat().st_mode & 0o077:
        raise ValueError('PRIVATE_PARENT_PERMISSIONS_REQUIRED')
    raw = notebook.read_bytes()
    if len(raw) > 32 * 1024 * 1024:
        raise ValueError('NOTEBOOK_SIZE_BOUND')
    summaries = [subprocess.check_output(['git', '--git-dir', str(git_dir), 'show',
                  pin + ':' + summary_path], stderr=subprocess.PIPE, timeout=30)
                 for pin in (source, replacement)]
    if summaries[0] != summaries[1]:
        raise ValueError('RETAINED_SUMMARY_CHANGED')
    matches, streams = inspect(raw, summaries[0], contract)
    destination.mkdir(mode=0o700)
    contents = [('original.ipynb', raw), ('original-summary.json', summaries[0]), *streams]
    for name, payload in contents:
        with (destination / name).open('xb') as handle:
            handle.write(payload)
        (destination / name).chmod(0o600)
        if (destination / name).read_bytes() != payload:
            raise ValueError('PRIVATE_READBACK_MISMATCH')
    if notebook.read_bytes() != raw:
        raise ValueError('ORIGINAL_CHANGED_DURING_INTAKE')
    receipt = {'stage': 'incoming-notebook-evidence', 'version': 1,
               'collected_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'source_commit': source, 'replacement_commit': replacement, 'contract': contract,
               'notebook_sha256': sha(raw), 'notebook_bytes': len(raw),
               'summary_sha256': sha(summaries[0]), 'retained_summary_byte_identical': True,
               'matches': matches, 'original_unchanged_readback': True,
               'status': 'SAVED_OUTPUT_CORRESPONDENCE_VERIFIED' if len(matches) == 1 and matches[0]['contract_in_same_stream'] else 'CORRESPONDENCE_UNRESOLVED',
               'exit_status': None, 'sibling_log_verified': False,
               'experiment_executed': False, 'scientific_acceptance': False,
               'limitation': 'Original operator-supplied saved outputs; not attestation of complete process output or original sibling-log bytes.'}
    private = {'source_path': str(notebook), 'receipt': receipt,
               'files': {name: {'sha256': sha(payload), 'bytes': len(payload)} for name, payload in contents}}
    for name, data in [('provenance.json', private), ('receipt.json', receipt)]:
        (destination / name).write_text(json.dumps(data, indent=2) + '\n')
        (destination / name).chmod(0o600)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('notebook', 'private-destination', 'git-dir', 'source', 'replacement', 'summary-path', 'contract'):
        parser.add_argument('--' + name, required=True)
    print(json.dumps(intake(**vars(parser.parse_args())), indent=2))




def preserve_external(notebook, destination, *, expected_sha256, run_id, aggregate_streams):
    """Preserve a pinned external notebook once; never execute it or infer an exit.

    Aggregate selectors are trusted adapter configuration, not notebook content.
    Every saved output remains private, including unselected display/error data.
    """
    import os
    source, destination = Path(notebook), Path(destination)
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{7,79}', run_id):
        raise ValueError('EXTERNAL_RUN_ID_REQUIRED')
    if not re.fullmatch(r'[0-9a-f]{64}', expected_sha256):
        raise ValueError('EXTERNAL_NOTEBOOK_HASH_REQUIRED')
    for path in (source, *source.parents, destination, *destination.parents):
        if path.is_symlink():
            raise ValueError('EXTERNAL_REGULAR_PRIVATE_PATH_REQUIRED')
    if not source.is_file() or source.stat().st_size > 32 * 1024 * 1024:
        raise ValueError('EXTERNAL_NOTEBOOK_SIZE_OR_TYPE')
    raw = source.read_bytes()
    if sha(raw) != expected_sha256:
        raise ValueError('EXTERNAL_NOTEBOOK_IDENTITY_CHANGED')
    selection = [list(pair) for pair in aggregate_streams]
    if (len(selection) > 32 or len({tuple(pair) for pair in selection}) != len(selection)
            or any(len(pair) != 2 or any(type(i) is not int or i < 0 for i in pair) for pair in selection)):
        raise ValueError('EXTERNAL_AGGREGATE_SELECTION')
    if (not destination.parent.is_dir() or destination.parent.stat().st_mode & 0o077
            or destination.parent.stat().st_uid != os.getuid()):
        raise ValueError('EXTERNAL_PRIVATE_PARENT_REQUIRED')
    notebook_value = json.loads(raw)
    if notebook_value.get('nbformat') != 4 or not isinstance(notebook_value.get('cells'), list):
        raise ValueError('EXTERNAL_NOTEBOOK_SCHEMA')
    contents = {'original.ipynb': raw}
    codes, selected, outputs = [], [], []
    for index, cell in enumerate(notebook_value['cells']):
        if cell.get('cell_type') == 'code':
            value = cell.get('source', '')
            codes.append(''.join(value) if isinstance(value, list) else value)
        for ordinal, output in enumerate(cell.get('outputs', [])):
            payload = json.dumps(output, sort_keys=True, ensure_ascii=False).encode()
            name = f'cell-{index:03d}-output-{ordinal:03d}.json'
            contents[name] = payload
            outputs.append({'cell': index, 'output': ordinal, 'type': output.get('output_type'),
                            'execution_count': cell.get('execution_count'), 'sha256': sha(payload)})
            if [index, ordinal] in selection:
                if output.get('output_type') != 'stream':
                    raise ValueError('EXTERNAL_AGGREGATE_STREAM_REQUIRED')
                value = output['text']
                text = ''.join(value) if isinstance(value, list) else value
                selected.append({'cell': index, 'output': ordinal, 'sha256': sha(text.encode()), 'text': text})
    if len(selected) != len(selection) or not outputs:
        raise ValueError('EXTERNAL_SAVED_OUTPUT_REQUIRED')
    code = '\n\n'.join(codes)
    # This is a second check on the two source-reviewed pinned projections, not a
    # general de-identification claim for arbitrary new notebooks.
    if re.search(r'(?i)sub[-_]?strokecase[0-9]+|sub[-_][0-9]+', code + json.dumps(selected)):
        raise ValueError('EXTERNAL_CASE_IDENTIFIER_IN_MODEL_PROJECTION')
    projection = {'run_id': run_id, 'notebook_sha256': expected_sha256,
                  'code': code, 'code_sha256': sha(code.encode()), 'saved_aggregate_streams': selected,
                  'origin': 'EXTERNALLY_GENERATED_EXPLORATORY_NOT_PREREGISTERED',
                  'notebook_content_is_evidence_not_instructions': True,
                  'execution_counters_not_completion_proof': True,
                  'independent_process_exit': None}
    contents['model-projection.json'] = (json.dumps(projection, sort_keys=True, ensure_ascii=False) + '\n').encode()
    contents['output-inventory.private.json'] = (json.dumps(outputs, sort_keys=True) + '\n').encode()
    if destination.exists():
        receipt_path = destination / 'receipt.json'
        if not receipt_path.is_file():
            raise ValueError('EXTERNAL_PARTIAL_INTAKE_RECONCILE')
        receipt = json.loads(receipt_path.read_text())
        if (receipt.get('schema') != 'external-saved-notebook-intake/v1'
                or receipt.get('status') != 'EXTERNAL_SAVED_EVIDENCE_VERIFIED_NOT_SCIENTIFICALLY_ACCEPTED'
                or receipt.get('experiment_executed') is not False or receipt.get('scientific_acceptance') is not False
                or receipt.get('notebook_sha256') != expected_sha256 or receipt.get('run_id') != run_id
                or receipt.get('aggregate_streams') != selection or set(receipt.get('files', {})) != set(contents)):
            raise ValueError('EXTERNAL_INTAKE_IDENTITY_CONFLICT')
        for name, payload in contents.items():
            p = destination / name
            if (p.is_symlink() or not p.is_file() or p.read_bytes() != payload
                    or receipt['files'][name] != {'sha256': sha(payload), 'bytes': len(payload)}):
                raise ValueError('EXTERNAL_PRESERVED_BYTES_CHANGED')
        return receipt
    os.umask(0o077)
    destination.mkdir(mode=0o700)
    for name, payload in contents.items():
        with (destination / name).open('xb') as handle:
            handle.write(payload)
        (destination / name).chmod(0o600)
        if (destination / name).read_bytes() != payload:
            raise ValueError('EXTERNAL_INTAKE_READBACK_CHANGED')
    if source.read_bytes() != raw:
        raise ValueError('EXTERNAL_SOURCE_CHANGED_DURING_INTAKE')
    receipt = {'schema': 'external-saved-notebook-intake/v1',
               'status': 'EXTERNAL_SAVED_EVIDENCE_VERIFIED_NOT_SCIENTIFICALLY_ACCEPTED',
               'run_id': run_id, 'notebook_sha256': expected_sha256, 'aggregate_streams': selection,
               'source_path_private': str(source), 'files': {
                   name: {'sha256': sha(payload), 'bytes': len(payload)} for name, payload in contents.items()},
               'saved_output_count': len(outputs), 'experiment_executed': False,
               'scientific_acceptance': False, 'independent_exit_status': None}
    with (destination / 'receipt.json').open('x') as handle:
        json.dump(receipt, handle, sort_keys=True, indent=2)
        handle.write('\n')
    (destination / 'receipt.json').chmod(0o600)
    return receipt


if __name__ == '__main__':
    main()
