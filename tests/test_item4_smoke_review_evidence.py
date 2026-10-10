"""Replay actual synthetic collection/ledger receipts with no provider calls."""
import copy,json
from pathlib import Path
import pytest
from orchestrator import item4_smoke_review as smoke,experiment_collection as collection,private_records as pr
from test_experiment_collection import collected_lane,item4_dispatch,make_item4_package,setup,private_test_environment,root

@pytest.fixture
def replay(collected_lane,monkeypatch):
    d,v,e,provider,batch,job=collected_lane
    d.root=d.context
    selected=collection.dispatch.load(d,v);selected['complete_selection']=False
    v['phase']='EXECUTE_EXPERIMENT';v['rounds']={'run_spec_author':14,'run_spec_review':10}
    v['fit_continuations']={'synthetic-previous':[{'epoch_resumed_from':1}]}
    assert collection.collect_ready(d,v,selected)
    def pin(path):
        raw=path.read_bytes();return {'sha256':smoke.sha(raw),'bytes':len(raw)}
    native=json.loads((e._paths(job)/'collection-receipt.json').read_bytes())
    local=dict(e.db.execute('SELECT * FROM jobs WHERE id=?',(job,)).fetchone())
    globalrow=dict(batch.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(native['binding_sha256'],)).fetchone())
    frozen={'job':job,'fit_id':'one','binding_sha256':native['binding_sha256'],
        'collection_receipt_sha256':v['fit_collection_receipts'][job],
        'validation':copy.deepcopy(v['fit_collections'][job]),
        'manifest':pin(d.state/'fit-packages'/job/'prepared/manifest.json'),
        'termination':pin(e._paths(job)/'terminated.json'),
        'local_row_sha256':smoke.sha(smoke.canonical(local)),
        'global_row_sha256':smoke.sha(smoke.canonical(globalrow))}
    package=d.state/'experiment-package'
    p={'fits':[frozen],'package_files':{str(f.relative_to(package)):pin(f) for f in package.rglob('*') if f.is_file()}}
    old=copy.deepcopy(v)
    # Only selection/administrative authority are synthetic in this fixture.
    # The actual file validator, native collection and SQLite records run intact.
    monkeypatch.setattr(smoke,'FITS',['one'])
    monkeypatch.setattr(smoke,'scope',lambda *args:old)
    monkeypatch.setattr(smoke,'originals',lambda *args:None)
    return d,v,e,provider,batch,p


@pytest.mark.parametrize('fault',['none','data','native','global','local','missing','terminal','extra-package','package','receipt-pin','manifest-pin'])
def test_original_collections_replayed_and_tampering_refused(replay,fault):
    d,v,e,provider,batch,p=replay;fit=p['fits'][0];job=fit['job']
    before=list(provider.calls)
    if fault=='data':pr.write_bytes(d.state/'fit-results'/job/'aggregate.csv',b'changed')
    elif fault=='native':pr.write_bytes(e._paths(job)/'collection-receipt.json',b'{}')
    elif fault=='global':batch.db.execute("UPDATE autonomy_compute SET provider_id='changed'")
    elif fault=='local':e.db.execute("UPDATE jobs SET status='RUNNING'")
    elif fault=='missing':(d.state/'fit-results'/job/'aggregate.csv').unlink()
    elif fault=='terminal':pr.write_bytes(e._paths(job)/'terminated.json',b'{"terminated":false}')
    elif fault=='extra-package':pr.write_bytes(d.state/'experiment-package/extra.json',b'{}')
    elif fault=='package':pr.write_bytes(d.state/'experiment-package/execution-plan.json',b'{}')
    elif fault=='receipt-pin':fit['collection_receipt_sha256']='f'*64
    elif fault=='manifest-pin':fit['manifest']['sha256']='f'*64
    if fault=='none':
        records=smoke.evidence(d,v,p,'d'*64);assert len(records)==1 and not records[0]['scientifically_accepted']
    else:
        with pytest.raises((ValueError,FileNotFoundError)):smoke.evidence(d,v,p,'d'*64)
    assert provider.calls==before
    assert v['phase']=='EXECUTE_EXPERIMENT' and not (d.state/'validation.json').exists()


@pytest.mark.parametrize('fault',['fit','local','global','batch','state','direction','authority','approval'])
def test_frozen_five_fit_scope_is_not_generic(fault):
    p=json.loads((Path(__file__).resolve().parents[1]/smoke.DOCUMENT).read_bytes());approval='d'*64
    smoke.scope(p,approval)
    if fault=='fit':p['fits'].pop()
    elif fault=='local':p['local_calls'].pop(next(iter(p['local_calls'])))
    elif fault=='global':p['global_calls'][next(iter(p['global_calls']))]='0'*64
    elif fault=='batch':p['batch_calls'].pop(next(iter(p['batch_calls'])))
    elif fault=='state':p['original_state']+=' '
    elif fault=='direction':p['direction_sha256']='0'*64
    elif fault=='authority':p['authority_sha256']='0'*64
    else:approval='not-an-approval'
    with pytest.raises(ValueError):smoke.scope(p,approval)
