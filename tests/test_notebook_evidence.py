import json
import pytest
from orchestrator.notebook_evidence import inspect
from orchestrator.publication import collect_console_handoff


def test_saved_summary_is_not_source_or_exit_status():
    summary = {'status':'STUDY_COMPLETE','aggregate':1}
    stream = 'contract-token\n'+json.dumps(summary)+'\n'
    nb={'cells':[{'source':[stream],'outputs':[]}, {'execution_count':7,'outputs':[{'output_type':'stream','text':[stream[:4],stream[4:]]}]}]}
    matches, streams=inspect(json.dumps(nb).encode(),json.dumps(summary).encode(),'contract-token')
    assert len(matches)==1 and matches[0]['cell_index']==1
    assert matches[0]['contract_in_same_stream']
    assert streams[0][1]==stream.encode()
    assert 'exit_status' not in matches[0]
    nb['cells'][1]['outputs']=[]
    assert inspect(json.dumps(nb).encode(),json.dumps(summary).encode(),'contract-token')[0]==[]


def test_console_collection_rerun_conflict_missing_and_private(tmp_path):
    source=tmp_path/'original.log'; source.write_bytes(b'original console\n')
    destination=tmp_path/'private'
    receipt=collect_console_handoff(source,destination,{'source':'pin'})
    assert receipt==collect_console_handoff(source,destination,{'source':'pin'})
    assert (destination/'console.log').read_bytes()==source.read_bytes()
    with pytest.raises(ValueError,match='DIFFERS'):
        collect_console_handoff(source,destination,{'source':'changed'})
    source.write_bytes(b'changed')
    with pytest.raises(ValueError,match='DIFFERS'):
        collect_console_handoff(source,destination,{'source':'pin'})
    assert (destination/'console.log').read_bytes()==b'original console\n'
    source.unlink()
    with pytest.raises(ValueError,match='NONEMPTY'):
        collect_console_handoff(source,tmp_path/'new',{})
    assert not (tmp_path/'new').exists()


def test_console_collection_refuses_partial_and_symlink(tmp_path):
    source=tmp_path/'original';source.write_bytes(b'console')
    partial=tmp_path/'partial';partial.mkdir(mode=0o700)
    with pytest.raises(ValueError,match='INCOMPLETE'):
        collect_console_handoff(source,partial,{})
    link=tmp_path/'link';link.symlink_to(source)
    with pytest.raises(ValueError,match='NONEMPTY'):
        collect_console_handoff(link,tmp_path/'new',{})
