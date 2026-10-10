"""One-call size policy and unchanged fixture guard in same-call feedback."""
import ast,copy,json
from pathlib import Path
import pytest
from orchestrator import author_format_submission as af,author_output_schema as out,fixture_contract
from test_author_revision_submission import prepared,write_plan
from test_author_visible_module_feedback import visible,BODY

BASE=BODY.replace('def synthetic_tests(): return {}\n','def synthetic_tests():\n class Checks:\n  def test_original(self): pass\n return Checks\n')+'def _native_diagnostic_fixture(): return 1\n'
FIXED=BASE.replace('return 1','return 2')
CONFORMING=FIXED.replace(' return Checks\n','  def test_report_lifecycle(self): pass\n return Checks\n')

@pytest.fixture
def delivery(tmp_path,monkeypatch):
    first=tmp_path/'prior';first.mkdir();oldpins,plan=prepared(first);old=af.load(first,oldpins[af.CONFIG])
    work=tmp_path/'work';work.mkdir();patch,view,manifest=visible(FIXED)
    b=copy.deepcopy(old['bindings']);b['round']=24;b['call_id']=af.AUTHOR24_CALL
    revision=copy.deepcopy(old['revision']);revision['view_sha256']=af.sha(view)
    # Synthetic test baseline only; production policy pins the actual accepted21 hash.
    monkeypatch.setattr(af,'FIXTURE_PIN',af.sha(BASE.encode()))
    pins=af.prepare_revision(work,b,revision,notebook={af.MODULE_VIEW:view,af.MODULE_MANIFEST:af.canonical(manifest)},fixture_reference=BASE.encode())
    write_plan(work,plan);(work/'notebook.patch.json').write_bytes(af.canonical(patch))
    return work,pins,patch,view,manifest

def conform(work,patch,size=None):
    patch=copy.deepcopy(patch);patch['edits'][0]['replacement']='%%writefile /content/sprint13_pipeline.py\n'+CONFORMING
    raw=af.canonical(patch)
    if size is not None:
        assert len(raw)<size;raw+=b' '*(size-len(raw))
    (work/'notebook.patch.json').write_bytes(raw)

def test_missing_test_is_returned_before_submission_then_author_corrects(delivery):
    work,pins,patch,view,manifest=delivery
    with pytest.raises(ValueError,match='ITEM4_FIXTURE_ORIGINAL_TESTS_CHANGED'):af.submit(work,pins[af.CONFIG],{})
    assert not (work/af.RECORD).exists()
    conform(work,patch)
    accepted=af.submit(work,pins[af.CONFIG],{})
    assert accepted['status']=='ACCEPTED' and af.verify(work,pins[af.CONFIG])['bindings']['round']==24
    af.check_runtime(work,pins)

@pytest.mark.parametrize('size',[80001,96000])
def test_only_exact_author24_patch_can_use_bounded_space(delivery,size):
    work,pins,patch,*_=delivery;conform(work,patch,size)
    assert af.submit(work,pins[af.CONFIG],{})['status']=='ACCEPTED'

@pytest.mark.parametrize('name,size',[('notebook.patch.json',96001),('execution.plan.json',80001),('SPEC.proposed.md',80001)])
def test_file_limits_still_refuse(delivery,name,size):
    work,pins,patch,*_=delivery;conform(work,patch)
    (work/name).write_bytes(b' '*size)
    with pytest.raises(ValueError,match='AUTHOR_FILE_IDENTITY'):af.submit(work,pins[af.CONFIG],{})
    assert not (work/af.RECORD).exists()

@pytest.mark.parametrize('fault',['attempt23','attempt25','call','run','size','baseline','extra','no-notebook'])
def test_cannot_apply_exception_to_other_calls_or_inputs(delivery,fault):
    work,pins,*_=delivery;config=copy.deepcopy(af.load(work,pins[af.CONFIG]))
    if fault.startswith('attempt'):
        n=int(fault[-2:]);config['bindings']['round']=n;config['bindings']['call_id']=af.sha((config['bindings']['run_id']+':run_spec_author:'+str(n)).encode())
    elif fault=='call':config['bindings']['call_id']='a'*64
    elif fault=='run':config['bindings']['run_id']='another-run'
    elif fault=='size':config['delivery']['notebook_patch_bytes']=96001
    elif fault=='baseline':config['delivery']['fixture_reference']['sha256']='f'*64
    elif fault=='extra':config['delivery']['additional']=True
    else:config.pop('notebook')
    with pytest.raises(ValueError):af.load_revision(config)

def test_default_still_refuses_over80000(delivery):
    work,pins,patch,*_=delivery;conform(work,patch,80001)
    config=af.load(work,pins[af.CONFIG]);config.pop('delivery')
    with pytest.raises(ValueError,match='AUTHOR_FILE_IDENTITY'):af.validate_revision(work,config)

@pytest.mark.parametrize('damage',['old-test','production','no-new-test','interface','duplicate-test','decorator'])
def test_old_guard_refusals_preserved(damage):
    raw=CONFORMING
    if damage=='old-test':raw=raw.replace('test_original','test_replaced')
    elif damage=='production':raw=raw.replace('def main(input_root, output_root, contract): pass','def main(input_root, output_root, contract): return 5')
    elif damage=='no-new-test':raw=FIXED
    elif damage=='interface':raw=raw.replace('_native_diagnostic_fixture()', '_native_diagnostic_fixture(x)')
    elif damage=='duplicate-test':raw=raw.replace('test_report_lifecycle','test_original')
    else:raw=raw.replace('  def test_report_lifecycle','  @decorator\n  def test_report_lifecycle')
    with pytest.raises(ValueError):fixture_contract.check(BASE.encode(),raw.encode())

def test_shared_guard_accepts_only_additive_delta():
    r=fixture_contract.check(BASE.encode(),CONFORMING.encode())
    assert r['added_contract_tests']==['test_report_lifecycle'] and r['existing_tests_unchanged']
    assert r['corrected_fixture_executed'] is False and r['scientific_acceptance'] is False

@pytest.mark.parametrize('name',[af.FIXTURE_REFERENCE,af.RUNTIME+'/orchestrator/fixture_contract.py',af.CONFIG])
def test_readonly_runtime_pins_include_guard_and_reference(delivery,name):
    work,pins,*_=delivery
    assert name in pins
    (work/name).write_bytes((work/name).read_bytes()+b' ')
    with pytest.raises(ValueError):af.check_runtime(work,pins)


def test_real_controller_limit_is_exact_call_and_patch_only():
    from test_item4_driver_round_entry import candidate_class
    from orchestrator import item4_smoke_response as helper
    from orchestrator.manual_driver import Driver
    from tools import item4_smoke_response_runtime as route
    root=Path(__file__).parents[1];scope=json.loads((root/helper.SNAPSHOT_DOCUMENT).read_bytes())
    ns=dict(vars(route),ExperimentDriver=Driver,helper=helper,p=scope)
    cls=candidate_class((root/'tools/item4_smoke_response_runtime.py').read_bytes(),ns)
    driver=cls.__new__(cls);driver.config={'run_id':helper.RUN}
    pending={'stage':'run_spec_author','round':24,'id':helper.call(scope,'author')}
    assert driver.model_output_limit({'pending':pending},'notebook.patch.json')==96000
    for key,value in [('stage','run_spec_review'),('round',23),('round',25),('id','a'*64)]:
        assert driver.model_output_limit({'pending':{**pending,key:value}},'notebook.patch.json')==80000
    for name in ['SPEC.proposed.md','execution.plan.json','review.json']:
        assert driver.model_output_limit({'pending':pending},name)==80000
    driver.config={'run_id':'another-run'}
    assert driver.model_output_limit({'pending':pending},'notebook.patch.json')==80000
    assert Driver.model_output_limit(driver,{'pending':pending},'notebook.patch.json')==80000

@pytest.mark.parametrize('limit,size,passes',[(80000,80001,False),(96000,96000,True),(96000,96001,False),(96001,96000,False)])
def test_notebook_application_remains_bounded(limit,size,passes):
    from test_notebook_revision import fixture
    from orchestrator import notebook_revision as nr,scientific_intake as si
    original,selection,patch=fixture();raw=si.canonical(patch);raw+=b' '*(size-len(raw))
    def apply():return nr.apply(original,selection,raw,set(),original_sha256=patch['original_sha256'],view_sha256=patch['view_sha256'],patch_limit=limit)
    if passes:assert apply()[2]['compile']
    else:
        with pytest.raises(ValueError):apply()


def test_author24_scope_preserves_failed23_and_all_caps():
    from orchestrator import item4_smoke_response as h
    root=Path(__file__).parents[1];p=json.loads((root/h.SNAPSHOT_DOCUMENT).read_bytes())
    old=h.scope(p,'f'*64);q=h.profile(p);prior=p['delivery_recovery']['previous_scope']
    assert (q['author'],q['count'],q['batch'],q['limit'],q['batch_limit'])==(24,38,76,41,79)
    assert old['rounds']=={'run_spec_author':23,'run_spec_review':15}
    assert old['pending']['id']==h.DELIVERY_FAILED_CALL
    assert set(p['local_calls'])==set(prior['local_calls'])|{h.DELIVERY_FAILED_CALL}
    assert set(p['batch_calls'])==set(prior['batch_calls'])|{h.DELIVERY_FAILED_CALL}
    for fault in ['approval','call','old-call','limit']:
        bad=copy.deepcopy(p)
        if fault=='approval':bad['delivery_recovery']['previous_approval']='a'*64
        elif fault=='call':bad['delivery_recovery']['failed_call_id']='b'*64
        elif fault=='old-call':bad['local_calls'].pop(h.DELIVERY_FAILED_CALL)
        else:bad['delivery_recovery']['patch_limit_bytes']=96001
        with pytest.raises(ValueError):h.scope(bad,'f'*64)
