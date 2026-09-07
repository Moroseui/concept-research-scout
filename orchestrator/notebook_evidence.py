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


if __name__ == '__main__':
    main()
