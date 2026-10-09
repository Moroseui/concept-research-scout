"""Selected review packet applications; synthetic plans never admit calls."""
import pytest
from orchestrator import experiment_selection as selection
from orchestrator.autonomy_review import canonical, sha


def plan(item):
    return canonical({"schema":"experiment-lane/v1","item_number":item,"fixture":"synthetic"})


@pytest.mark.parametrize("item",[4,6])
def test_primary_or_named_exact_selection(item):
    raw=plan(item)
    for key in ("evidence/experiment-plan.json",f"evidence/experiment-plan-item{item}.json"):
        assert selection.reviewed_plan(raw,{"files":{key:sha(raw)}})["item_number"]==item


def test_one_review_binds_both_exact_applications():
    a,b=plan(4),plan(6)
    m={"files":{"evidence/experiment-plan-item4.json":sha(a),"evidence/experiment-plan-item6.json":sha(b)}}
    assert selection.reviewed_plan(a,m)["item_number"]==4
    assert selection.reviewed_plan(b,m)["item_number"]==6
    with pytest.raises(ValueError,match="^REVIEWED_EXPERIMENT_PLAN_REQUIRED$"):
        selection.reviewed_plan(a.replace(b"synthetic",b"altered"),m)


def test_other_application_or_conflicting_named_binding_refuses():
    a,b=plan(4),plan(6)
    for files in ({"evidence/experiment-plan.json":sha(a)},
                  {"evidence/experiment-plan-item4.json":sha(b)},
                  {"evidence/experiment-plan.json":sha(b),"evidence/experiment-plan-item6.json":sha(a)}):
        with pytest.raises(ValueError,match="^REVIEWED_EXPERIMENT_PLAN_REQUIRED$"):
            selection.reviewed_plan(b,{"files":files})


@pytest.mark.parametrize("item",[True,5,"6",None])
def test_unsupported_selection_refuses(item):
    raw=plan(item)
    with pytest.raises(ValueError,match="^EXPERIMENT_AUTHORING_ITEM_REQUIRED$"):
        selection.reviewed_plan(raw,{"files":{"evidence/experiment-plan.json":sha(raw)}})
