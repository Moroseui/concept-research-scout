import json
from pathlib import Path
import pytest
from orchestrator import idea2_cpu_contract as c

def test_corrupt_metadata_refuses_before_payload_access():
    with pytest.raises(ValueError,match="METADATA_HASH"):
        c.authenticate_metadata({name:b"untrusted" for name in c.PINS})

def test_unknown_metadata_member_refuses():
    with pytest.raises(ValueError,match="EXACT_METADATA"):
        c.authenticate_metadata({**{name:b"x"for name in c.PINS},"extra":b"x"})

def test_changed_scientific_program_refuses():
    with pytest.raises(ValueError,match="SCIENTIFIC_APPROVAL_HASH"):
        c.authenticate_program(b"changed",b"changed",b"changed",b"changed")

def test_tree_hashes_and_rejects_mutation_extra_member_and_link(tmp_path):
    root=tmp_path/"frozen";root.mkdir();(root/"sub").mkdir()
    path=root/"sub/input.bin";path.write_bytes(b"synthetic")
    expected={"sub/input.bin":{"sha256":c.sha(b"synthetic"),"bytes":9}}
    assert c.verify_tree(root,expected)["files"]==1
    path.write_bytes(b"corrupted")
    with pytest.raises(ValueError,match="INPUT_HASH"):c.verify_tree(root,expected)
    path.write_bytes(b"synthetic");(root/"extra").write_bytes(b"x")
    with pytest.raises(ValueError,match="INPUT_MEMBERSHIP"):c.verify_tree(root,expected)
    (root/"extra").unlink();(root/"alias").symlink_to(path)
    with pytest.raises(ValueError,match="INPUT_ALIAS"):c.verify_tree(root,expected)

def test_hardlink_refuses(tmp_path):
    import os
    root=tmp_path/"frozen";root.mkdir();path=root/"input";path.write_bytes(b"x")
    os.link(path,tmp_path/"another")
    with pytest.raises(ValueError,match="INPUT_SIZE"):
        c.verify_tree(root,{"input":{"sha256":c.sha(b"x"),"bytes":1}})

def test_worker_only_forwards_complete_contract_to_unchanged_main():
    import ast
    tree=ast.parse(c.WORKER)
    calls=[node for node in ast.walk(tree)if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and node.func.attr=="main"]
    assert len(calls)==1 and len(calls[0].args)==3
    assert isinstance(calls[0].args[2],ast.Name)and calls[0].args[2].id=="contract"
    assert "exec("not in c.WORKER and "subprocess"not in c.WORKER
