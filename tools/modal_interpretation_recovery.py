#!/usr/bin/env python3
"""Apply the exact operator-authorized M3 author revision, without a model call."""
import argparse
import json
import sqlite3
import subprocess
from pathlib import Path
from orchestrator import private_records, manual_context, modal_evidence
from orchestrator.manual_executor import read, digest
from orchestrator.remote_supervisor import lock
from orchestrator.modal_driver import ModalDriver
from tools.modal_pre_admission_recovery import table_rows, canonical
from tools.modal_evidence_transition import approval

ROOT = Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-autonomy-m3-schema-20261003')
CALL = '4bea5dce29df6575e75e6de007d4a2c4716e206e7195a72e4a322c35af64a0b6'
AUTHORITY = '824158fcf5c1c15af831be6cb331a6f266131dd395bea1498a8ac7abfd98049e'
PINS = {'config': '6e541f91f554d09eab4a13e3f92adacb0455d9cd4b003e31afc362e899db3d62',
    'state': '2eb570596e9c30433ef7934e3d50fa0e72a3e11f1bdbf127a4041dfab39deeb6',
    'tables': 'ff3f35bd9f58b93c099544f225fe3c7b0420f116b70ed05c5e761c0a8b58c06d',
    'interpretation.md': 'd04629a29b4086f9393def917d7fcf4b02855dc9d9cca9420f7d41bcfd3daff4',
    'investigator_next_decision.json': 'b6e888f0b254db2e79ae6bba568de36b3d9739fba34a97123d99a2ae6e7d1849'}
STAGE = 'result_interpretation_author'


def validate(state, db):
    config = read(state / 'lane.json')
    value = json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
    if digest((state / 'lane.json').read_bytes()) != PINS['config']:
        raise ValueError('REVISION_CONFIG_CHANGED')
    if digest(canonical(value)) != PINS['state'] or digest(canonical(table_rows(db))) != PINS['tables']:
        raise ValueError('REVISION_STATE_OR_ACCOUNTING_CHANGED')
    if (value['phase'] != 'BLOCKED' or value['reason'] != 'OUTPUT_VALIDATION_REFUSED: OPEN_BLOCKER_BINDING_REQUIRED'
            or value['pending']['id'] != CALL or value['pending']['stage'] != STAGE
            or value['rounds'].get(STAGE) != 1):
        raise ValueError('EXACT_INTERPRETATION_REFUSAL_REQUIRED')
    calls = list(db.execute('SELECT status FROM manual_calls'))
    if len(calls) != 5 or any(r[0] != 'COMPLETE' for r in calls):
        raise ValueError('FIVE_PRESERVED_COMPLETED_CALLS_REQUIRED')
    work = Path(value['pending']['workspace'])
    if work != ROOT / 'lane-scientific-workspaces/result_interpretation_author-1':
        raise ValueError('ORIGINAL_AUTHOR_WORKSPACE_REQUIRED')
    for name in ('interpretation.md', 'investigator_next_decision.json'):
        if digest((work / name).read_bytes()) != PINS[name]:
            raise ValueError('ORIGINAL_AUTHOR_OUTPUT_CHANGED')
    if read(config['owner_path']) != config['owner_binding']:
        raise ValueError('OWNER_CHANGED')
    for name, h in {**config['engine_files'], **config['scientific_files'], **config['profile_files']}.items():
        if digest((Path(config['root']) / name).read_bytes()) != h:
            raise ValueError('BOUND_SOURCE_CHANGED')
    return config, value


def artifact(context, ident, kind, raw, version):
    from orchestrator.git_publication import scan
    from orchestrator.manual_driver import write_once
    scan('context/recovery-evidence.json', raw)
    h = digest(raw)
    name = 'current/' + ident + '-' + h + '.json'
    write_once(context / name, raw)
    return {'id': ident, 'type': kind, 'path': name, 'version': version, 'sha256': h}


@private_records.private_umask
def apply(state, review_folder, authority):
    state, authority = Path(state), Path(authority)
    if state != ROOT / 'lane' or state.is_symlink():
        raise ValueError('EXACT_M3_STATE_PATH_REQUIRED')
    approved = approval(review_folder)
    if authority.is_symlink() or digest(authority.read_bytes()) != AUTHORITY:
        raise ValueError('EXACT_REVISION_OPERATOR_AUTHORITY_REQUIRED')
    for suffix in ('.service', '.timer'):
        if subprocess.check_output(['/usr/bin/systemctl', 'show', ROOT.name + suffix,
                                    '-p', 'ActiveState', '--value'], text=True).strip() != 'inactive':
            raise ValueError('LANE_MUST_BE_HELD')
    dest = state / 'interpretation-evidence-recovery-20261003'
    if dest.exists() or dest.is_symlink():
        raise ValueError('REVISION_ALREADY_PREPARED_NO_RETRY')
    if (state / 'HALT').exists():
        raise ValueError('HALT_REMAINS_EFFECTIVE')
    with lock(state / 'one-run.lock'), lock(state / 'driver.lock'):
        db = private_records.Connection(state / 'jobs.sqlite')
        config, before = validate(state, db)
        batch = Path(config['modal']['batch_ledger'])
        if (batch / 'HALT').exists():
            raise ValueError('AUTONOMY_BATCH_HALTED')
        with sqlite3.connect('file:' + str(batch / 'jobs.sqlite') + '?mode=ro', uri=True) as global_db:
            if global_db.execute("SELECT 1 FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')").fetchone():
                raise ValueError('ACTIVE_OR_UNCERTAIN_CALL')
            if global_db.execute('SELECT status FROM autonomy_calls WHERE id=?', (CALL,)).fetchone() != ('COMPLETE',):
                raise ValueError('ORIGINAL_GLOBAL_CALL_REQUIRED')
        connection = modal_evidence.collected_view(state, config, before['manifest'])
        private_records.mkdir(dest)
        backup = private_records.Connection(dest / 'before.sqlite')
        db.backup(backup); backup.close()
        private_records.copyfile(state / 'DECISION_REQUEST.md', dest / 'DECISION_REQUEST.original.md')
        private_records.copyfile(authority, dest / 'OPERATOR_ORIGINAL.txt')
        intent = {'before': before, 'operator_original_sha256': AUTHORITY,
            'implementation_source': approved['source_sha'], 'review_report_sha256': approved['report_sha256'],
            'linked_recovery_of': CALL, 'call_cap': 8, 'calls_preserved': 5, 'new_allowance': 0,
            'scientific_source': config['source'], 'new_compute': 0}
        private_records.write_bytes(dest / 'INTENT.json', canonical(intent))
        value = json.loads(json.dumps(before))
        context = Path(config['context'])
        connected = artifact(context, 'execution_manifest', 'execution_manifest', connection, 2)
        value['artifacts'] = [r for r in value['artifacts'] if r['id'] != 'execution_manifest'] + [connected]
        work = Path(before['pending']['workspace'])
        original = {'kind': 'Preserved unaccepted author output; not an approval or current finding status',
            'call_id': CALL, 'interpretation': (work / 'interpretation.md').read_text(),
            'next_decision': read(work / 'investigator_next_decision.json'), 'original_hashes': PINS}
        value['artifacts'].append(artifact(context, 'original-author-refusal', 'result_tables', canonical(original), 1))
        driver = object.__new__(ModalDriver); driver.config = config
        for stage in (STAGE, 'result_interpretation_review'):
            # Reviewer measurement uses the genuine preserved author bytes, not
            # a fabricated future judgment. Recompose again after actual revision.
            items = list(value['artifacts'])
            if stage.endswith('review'):
                items += [artifact(context, 'measurement-original-interpretation', 'interpretation',
                                   (work / 'interpretation.md').read_bytes(), 1),
                          artifact(context, 'measurement-original-decision', 'investigator_next_decision',
                                   (work / 'investigator_next_decision.json').read_bytes(), 1)]
            _, measurement = manual_context.prepare(context, stage=stage, idea_ids=['Sprint9'],
                task=driver.task(stage, value), artifacts=items, workspace=dest / stage)
            private_records.write_bytes(dest / (stage + '.measurement.json'), canonical(measurement))
        validate(state, db)
        tables = table_rows(db)
        value.update(phase=STAGE, reason=None, linked_recovery_of=CALL)
        value.pop('pending', None)
        value['interventions'].append({k: v for k, v in intent.items() if k != 'before'})
        db.execute('BEGIN IMMEDIATE')
        try:
            validate(state, db)
            db.execute('UPDATE manual_state SET payload=? WHERE id=1', (json.dumps(value),))
            if table_rows(db) != tables:
                raise ValueError('REVISION_ACCOUNTING_CHANGED')
            db.execute('COMMIT')
        except BaseException:
            db.execute('ROLLBACK'); raise
        result = {k: v for k, v in intent.items() if k != 'before'}
        result.update(status='READY_FOR_ONE_LINKED_AUTHOR_REVISION', all_non_state_rows_unchanged=True)
        private_records.write_bytes(dest / 'COMPLETE.json', canonical(result))
        db.close()
        return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--state', required=True); p.add_argument('--approval-folder', required=True)
    p.add_argument('--authority', required=True)
    a = p.parse_args(); print(json.dumps(apply(a.state, a.approval_folder, a.authority)))


if __name__ == '__main__':
    main()
