import pytest

@pytest.fixture(autouse=True)
def deterministic_connectivity(monkeypatch):
    from orchestrator import connectivity
    monkeypatch.setattr(connectivity,'probe',lambda host:{
        'host':host,'dns':'SYNTHETIC_TEST_RESOLVED','https_status':200,'authenticated':False})


@pytest.fixture(autouse=True)
def active_lane_service_umask(request):
    """Model the active units' existing UMask=0077 for synthetic subprocess writers.

    Explicit chmod/umask adversarial tests still override this and must refuse.
    Archived route fixtures retain their original environment.
    """
    import os
    name=request.node.path.name
    applies=name.startswith(('test_manual_', 'test_autonomy_')) or name=='test_private_records.py'
    previous=os.umask(0o077) if applies else None
    try:yield
    finally:
        if previous is not None:os.umask(previous)
