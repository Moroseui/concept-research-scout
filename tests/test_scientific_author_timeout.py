"""No client launch: producer and watchdog must share the approved stage bound."""
import ast
import inspect
import tomllib
import pytest
from orchestrator import manual_stage

@pytest.mark.parametrize('stage,seconds', [
    ('run_spec_author',1800),('result_interpretation_author',1800),
    ('run_spec_review',900),('result_interpretation_review',1200),
    (None,900),('implementation_review',900),('unknown_author',900)])
def test_exact_stages_and_sink_share_timeout(stage,seconds):
    for sink in (False,True):
        profile=tomllib.loads(manual_stage.transport_profile('a'*64,[('codex',[])],stage=stage,sink=sink))
        assert profile['limits']['stage_timeout']==seconds
    assert manual_stage.scientific_stage_timeout(stage)+60==seconds+60

def test_outer_watchdog_uses_same_stage_bound_plus_cleanup_margin():
    # Inspect only the native parent wait; no real process or wall-clock sleep.
    tree=ast.parse(inspect.getsource(manual_stage))
    waits=[n for n in ast.walk(tree) if isinstance(n,ast.Call)
           and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name)
           and n.func.value.id=='p' and n.func.attr=='wait']
    first=next(n for n in waits if any(k.arg=='timeout' and isinstance(k.value,ast.BinOp) for k in n.keywords))
    bound=next(k.value for k in first.keywords if k.arg=='timeout')
    assert ast.unparse(bound)=='scientific_stage_timeout(stage) + 60'
