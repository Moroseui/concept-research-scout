"""One reviewed continuation after author7's exact specification-size refusal."""
from pathlib import Path
import importlib.util
import json

REASON='REVIEWED_AUTHOR7_FORMAT_RECOVERY'


def qualify(store,run,b):
    from orchestrator.manual_executor import digest
    frozen=b['format_recovery'];ident=frozen['call_id']
    def require(ok):
        if not ok:raise ValueError('AUTHOR7_RECOVERY_CHANGED')
    require(run==b['run_id'] and frozen['next_author']==8)
    for table,key,db in [('manual_calls','local_calls',store.db),('autonomy_calls','global_calls',store.batch.db)]:
        for call,pin in b[key].items():
            row=db.execute('SELECT * FROM '+table+' WHERE id=?',(call,)).fetchone()
            require(row is not None and digest(json.dumps(dict(row),sort_keys=True,separators=(',',':')).encode())==pin)
    rows=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    require(len(rows)==9 and rows[-1]['id']==ident and rows[-1]['status']=='COMPLETE')
    receipt=json.loads(rows[-1]['receipt']);require(receipt['output_sha256']==frozen['output_sha256'])
    require(receipt['scientific_revision_response']==frozen['classification'])
    require(not store.db.execute('SELECT 1 FROM events WHERE id=?',('author-accepted:'+ident,)).fetchone())
    work=Path(receipt['workspace']);pins=json.loads(Path(frozen['original_runtime_pins']).read_bytes())
    require(pins==frozen['runtime_pins'])
    path=Path(frozen['original_runtime_root'])/'orchestrator/author_format_submission.py'
    from orchestrator.manual_host_guard import trusted
    require(digest(trusted(path).read_bytes())==frozen['original_submission_source_sha256'])
    spec=importlib.util.spec_from_file_location('_preserved_author7_format',path)
    original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
    original.check_runtime(work,pins)
    console=(work/'console.log').read_bytes();require(digest(console)==receipt['native']['console_sha256'])
    require(original.verify_native(work,pins[original.CONFIG],console.decode())==receipt['native']['author_submission'])
    for name,pin in frozen['output_sha256'].items():require(digest((work/name).read_bytes())==pin)
    require(len((work/'SPEC.proposed.md').read_text())>12000)
    return frozen['classification']


def inspect(original,store,run,stage,b):
    result=original(store,run,stage)
    if run!=b['run_id'] or stage!='run_spec_author':return result
    state=json.loads(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
    if state.get('phase')!='run_spec_author' or state.get('reason')!=REASON:return result
    count=store.db.execute('SELECT count(*) FROM manual_calls WHERE stage=?',(stage,)).fetchone()[0]
    if count!=7:return result
    qualify(store,run,b)
    # No new scientific revision slot, altered old receipt, or general limit.
    return {**result,'limit':8,'binding':None}


def context_binding(store,run,b):
    from orchestrator.manual_executor import digest
    binding=dict(qualify(store,run,b))
    binding.update(author_attempt=8,author_call_id=digest((run+':run_spec_author:8').encode()))
    return binding
