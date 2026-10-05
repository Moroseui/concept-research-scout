"""Read-only, authenticated post-execution evidence for scientific interpretation.

Uses saved local originals only. No provider call, submission, scientific
computation, state mutation or inference of scientific acceptance.
"""
from pathlib import Path
from orchestrator.manual_executor import read, digest, inventory
from orchestrator.modal_executor import canonical, verify_package
from orchestrator.git_publication import scan


def collected_view(state, config, manifest):
    state = Path(state)
    binding = manifest['binding']
    job = config['run_id']
    if binding['run_id'] != job or binding['source'] != config['source']:
        raise ValueError('EVIDENCE_RUN_SOURCE_BINDING')
    package = state / 'package'
    verify_package(package, binding)
    if read(package / 'manifest.json') != manifest:
        raise ValueError('EVIDENCE_MANIFEST_BINDING')
    work = state / 'modal-executions' / job
    ident = digest(canonical(binding))
    records = {}
    originals = {}
    for name in ('create-intent.json', 'created.json', 'execute-intent.json',
                 'launched.json', 'collection-receipt.json', 'terminated.json'):
        path = work / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('EVIDENCE_ORIGINAL_REQUIRED')
        originals[name] = {'path': str(path), 'sha256': digest(path.read_bytes())}
        records[name] = read(path)
    provider = records['created.json']['provider_id']
    for name, record in records.items():
        if name != 'terminated.json' and record.get('binding_sha256') != ident:
            raise ValueError('EVIDENCE_ATTEMPT_BINDING')
        if name != 'create-intent.json' and record.get('provider_id') != provider:
            raise ValueError('EVIDENCE_PROVIDER_BINDING')
    intent = records['create-intent.json']
    if intent.get('job') != job or intent.get('package_sha256') != digest(canonical(inventory(package))):
        raise ValueError('EVIDENCE_PACKAGE_INTENT_BINDING')
    for name in ('created.json', 'launched.json'):
        receipt = records[name].get('receipt', {})
        if receipt.get('binding_sha256') != ident or receipt.get('provider_id') != provider:
            raise ValueError('EVIDENCE_NATIVE_RECEIPT_BINDING')
    if records['launched.json']['receipt'].get('submitted') is not True:
        raise ValueError('EVIDENCE_LAUNCH_REQUIRED')
    if records['terminated.json'] != {'provider_id': provider, 'terminated': True}:
        raise ValueError('EVIDENCE_TERMINATION_REQUIRED')
    files = records['collection-receipt.json']['file_sha256']
    if inventory(work / 'incoming') != files or inventory(state / 'collected') != files:
        raise ValueError('EVIDENCE_COLLECTION_CHANGED')
    validation = read(state / 'validation.json')
    expected_validation_files = {name: {'sha256': h,
        'bytes': (state / 'collected' / name).stat().st_size} for name, h in files.items()}
    if validation.get('status') != 'VALID' or validation.get('files') != expected_validation_files:
        raise ValueError('EVIDENCE_VALIDATION_BINDING')
    curves = []
    for name in sorted(files):
        if not name.startswith('ckpt/curves_') or not name.endswith('.json'):
            continue
        raw = read(state / 'collected' / name)
        inner, final, best = raw.get('inner_curve'), raw.get('final_curve'), raw.get('best_epoch')
        if (not isinstance(inner, list) or not isinstance(final, list)
                or type(best) is not int or not 1 <= best <= len(inner) <= 2
                or len(final) != best):
            raise ValueError('EVIDENCE_SMOKE_EPOCH_CONTRACT')
        curves.append({'path': name, 'sha256': files[name], 'arm': raw.get('arm'),
                       'inner_epochs': len(inner), 'final_epochs': len(final), 'best_epoch': best})
    if len(curves) != 1 or curves[0]['arm'] != 'U_base':
        raise ValueError('EVIDENCE_EXACT_SMOKE_CURVE_REQUIRED')
    # Patient filenames remain in the private originals. The model gets the
    # exact inventory digest, count, binding and substantive verified outcome.
    records['collection-receipt.json'] = {'binding_sha256': ident, 'provider_id': provider,
        'private_file_count': len(files), 'private_file_inventory_sha256': digest(canonical(files))}
    result = {'kind': 'controller-verified saved execution connection',
        'run_id': job, 'scientific_source': config['source'], 'binding_sha256': ident,
        'manifest_sha256': digest((package / 'manifest.json').read_bytes()),
        'spec_sha256': digest((package / 'SPEC.md').read_bytes()),
        'spec_review_sha256': digest((package / 'review.json').read_bytes()),
        'validation_sha256': digest((state / 'validation.json').read_bytes()),
        'validation_status': validation['status'], 'originals': originals,
        'records': records, 'epoch_counts': curves,
        'limits': 'Controller rechecked local original bytes. Private membership and curve values '
                  'are not exposed. No fresh provider retrieval or scientific acceptance is claimed.'}
    raw = canonical(result)
    scan('context/saved-execution-connection.json', raw)
    return raw
